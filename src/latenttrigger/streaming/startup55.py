"""Task0055 fixed source-free qualification; no operational activation or sources."""

import csv
import gc
import hashlib
import io
import json
import os
import signal
import struct
import subprocess
import sys
import time
import zlib
from dataclasses import asdict
from pathlib import Path

from . import quota
from . import validation_v2 as v2
from .cpu_runtime import ENVIRONMENT, RUNTIME_POLICY, RuntimeSession, exception_record
from .protocol import require
from .resources import POLICY, TrackerBudget
from .supervision import Clocks, Monitor, own_rss

CONFIG = "configs/streaming/development_streaming_startup_v1.json"
SCRIPT = "scripts/validate_development_streaming_startup.py"
ROOT = "data/task0055-validation/task0055"
BOOTSTRAPS = ("runtime-pca-metadata", "runtime-ae-metadata")


def file_plan():
    files = v2.file_plan()
    files.update(
        {
            "checks.txt": 1048576,
            "checks-2.txt": 1048576,
            "delivery-summary.json": 1048576,
            "delivery-cases.csv": 65536,
            "curated-final-summary.reserved": 1048576,
            "curated-final-cases.reserved": 65536,
        }
    )
    for group in (1, 2):
        files[f"sources-{group}.json"] = 786432
        prefix = f"suite-{group}"
        files[f"{prefix}/observer.json"] = 16384
        files[f"{prefix}/subject.json"] = 32768
        files[f"{prefix}/subject-emergency.json"] = 16384
        files[f"{prefix}/tracker.bin"] = 65536
        for index in range(1, 15):
            files[f"{prefix}/attempt-{index}.json"] = 1024
        for index, (name, n, _) in enumerate(v2.CASES, 1):
            if n:
                files[f"{prefix}/{index:02d}-{name}/tracker.bin"] = 65536
        for index, name in enumerate(BOOTSTRAPS, 13):
            d = f"{prefix}/{index:02d}-{name}"
            files.update(
                {
                    f"{d}/runtime.bin": 65536,
                    f"{d}/worker-result.json": 32768,
                    f"{d}/result.json": 65536,
                    f"{d}/emergency.txt": 2048,
                }
            )
    require(
        len(files) <= 512 and sum(files.values()) <= 32 * 1024**2,
        "Whole Task0055 ledger",
    )
    return files


def source_paths(repo):
    extras = [
        SCRIPT,
        "tests/test_development_streaming_startup.py",
        CONFIG,
        "docs/prompts/0055-streaming-startup-resource-repair.md",
        "src/latenttrigger/benchmarks/core.py",
        "src/latenttrigger/benchmarks/protocol.py",
        "src/latenttrigger/benchmarks/accelerate_threads.py",
        "src/latenttrigger/data/processed.py",
        "src/latenttrigger/data/features.py",
        "src/latenttrigger/data/inspection.py",
        "src/latenttrigger/data/analysis.py",
        "src/latenttrigger/data/splitting.py",
        "src/latenttrigger/models/pca.py",
        "src/latenttrigger/models/autoencoder.py",
    ]
    return sorted((repo / "src/latenttrigger/streaming").glob("*.py")) + [
        repo / p for p in extras
    ]


def manifest(repo):
    return [
        dict(
            path=str(p.relative_to(repo)),
            bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
        )
        for p in source_paths(repo)
        for b in [p.read_bytes()]
    ]


class Journal:
    """One bounded file lifetime; registration token and inode reject stale fd reuse."""

    def __init__(self, path):
        self.path, self.fd, self.generation = Path(path), None, 0
        self.registration = self.inode = None
        self.closed = False
        self.opens = self.close_count = self.write_attempts = 0

    def open(self):
        require(not self.closed, "Journal already finalized")
        if self.fd is None:
            self.fd = quota.open_file(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            self.registration = quota.FDS.get(self.fd)
            info = os.fstat(self.fd)
            self.inode = (info.st_dev, info.st_ino)
            self.opens += 1
            quota.truncate(self.fd, 65536)
        self.assert_owned()
        return self

    def assert_owned(self):
        require(self.fd is not None and not self.closed, "Journal is not open")
        require(
            quota.FDS.get(self.fd) is self.registration
            and (self.registration is not None or quota.CURRENT is None),
            "Stale journal registration",
        )
        info = os.fstat(self.fd)
        require((info.st_dev, info.st_ino) == self.inode, "Stale journal inode")

    def evidence(self):
        registered = False
        if self.fd is not None and not self.closed:
            try:
                self.assert_owned()
                registered = True
            except (ValueError, OSError):
                pass
        return dict(
            fd=self.fd,
            inode=list(self.inode) if self.inode else None,
            registered=registered,
            opens=self.opens,
            closes=self.close_count,
            generation=self.generation,
            write_attempts=self.write_attempts,
            closed=self.closed,
        )

    def write(self, value):
        quota.validate_tree(value)
        b = json.dumps(value, separators=(",", ":"), allow_nan=False).encode()
        require(len(b) <= 65504, "Bounded startup/resource snapshot")
        self.open()  # Legacy case-local callers may still open lazily.
        require(self.generation < 65536, "Bounded journal generations")
        self.write_attempts += 1
        generation = self.generation + 1
        header = struct.pack(
            "<QQII", generation, time.monotonic_ns(), len(b), zlib.crc32(b)
        )
        require(
            quota.pwrite(self.fd, header + b, 0) == len(header) + len(b),
            "Short startup journal",
        )
        self.generation = generation

    def close(self):
        if self.closed:
            return
        if self.fd is not None:
            self.assert_owned()  # Never close a numeric fd now owned by another file.
            fd = self.fd
            os.close(fd)
            quota.FDS.pop(fd, None)
            self.fd = None
            self.close_count += 1
        self.closed = True


def read_journal(path):
    if not path.exists():
        return None
    with path.open("rb", buffering=0) as f:
        head = f.read(24)
        if len(head) != 24:
            return None
        g, stamp, n, crc = struct.unpack("<QQII", head)
        if not g or not n or n > 65504:
            return None
        b = f.read(n)
    if len(b) != n or zlib.crc32(b) != crc:
        return None
    try:
        return json.loads(b)
    except (ValueError, UnicodeDecodeError):
        return None


def install_payload_denial(repo, owned):
    """Fresh worker audit: production payload roots have no read exception."""
    counts = dict(denied_open_attempts=0, production_open_successes=0)
    protected = [repo / x for x in ("data", "artifacts", "results")]

    def audit(event, args):
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.path.abspath(os.fsdecode(args[0])))
        forbidden_configs = {
            repo / p
            for p in (
                "configs/models/pca_baseline.json",
                "configs/models/compact_autoencoder_v2.json",
                "configs/data/lhco_rnd_v5.json",
            )
        }
        if path in forbidden_configs or (
            any(path.is_relative_to(p) for p in protected)
            and not path.is_relative_to(owned)
        ):
            counts["denied_open_attempts"] += 1
            raise PermissionError(
                "Task0055 denies production data/model/result payload paths"
            )

    sys.addaudithook(audit)
    return counts


def runtime_worker(root, directory, selector):
    # Spawn target; source/config identity verified in subject before launch.
    ledger = quota.activate(root)
    repo = Path(__file__).resolve().parents[3]
    counts = install_payload_denial(repo, root)
    journal = Journal(directory / "runtime.bin")
    session = None
    primary = report_error = None
    cleanup = []

    def guarded_import(name):
        import importlib

        module = importlib.import_module(name)

        def denied(*a, **k):
            counts["denied_payload_API_attempts"] = (
                counts.get("denied_payload_API_attempts", 0) + 1
            )
            raise PermissionError("Payload-not-armed API sentinel")

        if name == "numpy":
            module.load = denied
        if name == "h5py":
            module.File = denied
        if name == "latenttrigger.benchmarks.core":
            module.ProcessedStore.__init__ = denied
            module.PCAReconstruction.__init__ = denied
            module.CompactAutoencoder.__init__ = denied
            module.PCAReconstruction.from_artifact = denied
            module.CompactAutoencoder.from_artifact = denied
            module.PCAReconstruction.score = denied
            module.CompactAutoencoder.score = denied
        return module

    try:
        require(selector in BOOTSTRAPS, "Metadata selector only; no model path")
        session = RuntimeSession(publish=journal.write, import_module=guarded_import)
        session.initialize()
        # Denial sentinels are installed after imports, before leaving runtime.
        import h5py
        import numpy as np

        def denied(*a, **k):
            raise PermissionError("Payload-not-armed sentinel")

        h5py.File = denied
        np.load = denied
        session.core.ProcessedStore = denied
        session.core.PCAReconstruction.from_artifact = denied
        session.core.CompactAutoencoder.from_artifact = denied
        require(
            session.evidence["boundary"] == "payload_not_armed",
            "Stop before source phase",
        )
    except BaseException as exc:
        primary = exception_record(exc)
    finally:
        if session is not None:
            try:
                if not session.close():
                    cleanup = session.evidence["cleanup_failures"]
            except BaseException as exc:
                cleanup.append(exception_record(exc))
        value = dict(
            selector=selector,
            payload_armed=False,
            offers=0,
            operational_access=False,
            runtime=session.evidence if session else None,
            primary_failure=primary,
            report_failure=None,
            cleanup_failures=cleanup,
            audit=counts,
            own_lifetime_peak_RSS_bytes=own_rss(),
        )
        value["passed"] = (
            primary is None
            and not cleanup
            and session is not None
            and counts["denied_open_attempts"] == 0
        )
        try:
            journal.write(value)
            ledger.write_json(directory / "worker-result.json", value)
        except BaseException as exc:
            report_error = exception_record(exc)
            value["report_failure"] = report_error
            value["passed"] = False
            try:
                journal.write(value)
            except BaseException:
                pass
        finally:
            journal.close()
    if primary is not None or report_error is not None or cleanup:
        raise SystemExit(1)


def run_bootstrap(root, path, selector, heartbeat):
    import multiprocessing as mp

    clocks = Clocks()
    before = clocks.observation()
    monitor = Monitor(*before[:2])
    path.mkdir(mode=0o700)
    process = mp.get_context("spawn").Process(
        target=runtime_worker,
        args=(root, path, selector),
        name="source-free-CPU-runtime",
    )
    problem = None
    forced = False
    consumer_peak = 0
    budget = TrackerBudget(POLICY)
    try:
        budget.await_ready(clocks, time.sleep, monitor)
        process.start()
        while process.is_alive():
            svc, now, _ = clocks.observation()
            monitor.observe(svc, now)
            require(now - before[1] < 8_000_000_000, "Runtime8s body/2s cleanup")
            data = read_journal(path / "runtime.bin")
            if data:
                consumer_peak = max(
                    consumer_peak, data.get("own_lifetime_peak_RSS_bytes", 0)
                )
                runtime_data = data.get("runtime", data)
                step = runtime_data.get("last_step") if runtime_data else None
                stamp = runtime_data.get("last_monotonic_ns") if runtime_data else None
                if step and not step.startswith("import_") and type(stamp) is int:
                    require(
                        0 <= now - stamp <= 2_000_000_000,
                        "Runtime active-control/report no-progress2s",
                    )
            budget.observe(peaks=dict(consumer=consumer_peak))
            require(consumer_peak <= 1024**3, "Runtime worker RSS")
            heartbeat(dict(consumer=consumer_peak))
            time.sleep(0.005)
        process.join()
    except BaseException as exc:
        problem = exception_record(exc)
    finally:
        end = clocks.continuous() + 2_000_000_000
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
                forced = True
                process.join(timeout=0.15)
            if process.is_alive():
                process.kill()
                process.join(timeout=max(0, (end - clocks.continuous()) / 1e9))
            require(not process.is_alive(), "Runtime worker reaped")
            code = process.exitcode
        else:
            code = None
        process.close()
        after = clocks.observation()
    result_path = path / "worker-result.json"
    worker = json.loads(result_path.read_text()) if result_path.exists() else None
    result = dict(
        kind="runtime_bootstrap",
        case_id=selector,
        configured_offers=0,
        worker=worker,
        passed=bool(
            worker and worker["passed"] and code == 0 and not forced and not problem
        ),
        problem=problem,
        exitcode=code,
        forced=forced,
        reaped=code is not None,
        lifetime_ns=after[1] - before[1],
        monitor_gap_ns=monitor.maximum_gap,
        tracker=budget.summary(),
        consumer_peak_RSS_bytes=consumer_peak,
        last_journal=read_journal(path / "runtime.bin") if worker is None else None,
    )
    require(result["lifetime_ns"] <= 10_000_000_000, "Runtime10s inclusive")
    return result


def initialize(root, repo):
    require(
        root == repo / ROOT
        and not root.exists()
        and root.parent.resolve() == root.parent,
        "New fixed Task0055 root",
    )
    files = file_plan()
    root.mkdir(mode=0o700, parents=True)
    ledger = quota.Ledger(root, files, task="0055")
    ledger.write_json(
        root / "ledger.json", dict(task="0055", cap_bytes=32 * 1024**2, files=files)
    )
    ledger.write_json(
        root / "owner.json", dict(task="0055", source_free=True, operational=False)
    )
    return quota.activate(root)


def prepare(root, group, repo, *, context=None):
    if context is not None:
        return context.prepare_group(root, group, repo)
    require(
        root == repo / ROOT and group in (1, 2), "Fixed root/two qualification groups"
    )
    ledger = quota.activate(root)
    require(ledger.entries == file_plan(), "Immutable global ledger")
    cfg = json.loads((repo / CONFIG).read_text())
    require(
        not cfg["operational_execution_authorized"]
        and not cfg["P4_allowance"]
        and cfg["resource_policy"] == asdict(POLICY)
        and cfg["runtime_policy"] == asdict(RUNTIME_POLICY)
        and cfg["thread_environment"] == ENVIRONMENT,
        "Source-free exact policy",
    )
    identity = manifest(repo)
    for pin in cfg["code_manifest"]:
        require(pin in identity, "Frozen configured source")
    if group == 2:
        prior = json.loads((root / "suite-1/observer.json").read_text())
        require(
            identity != prior["source_manifest"]
            and (
                not prior["qualified"]
                or cfg.get("correctness_repair_after_group1")
                == "consumer_failure_context_propagation"
            ),
            "Only documented correctness repair/new bundle; no favorable-sample rerun",
        )
    directory = root / f"suite-{group}"
    directory.mkdir(mode=0o700)
    ledger.write_json(
        root / f"sources-{group}.json",
        {str(p.relative_to(repo)): p.read_text() for p in source_paths(repo)},
    )
    ledger.write_json(
        directory / "prospective.json",
        dict(
            source_manifest=identity,
            bundle_sha256=v2.fingerprint(identity),
            generated_cases=[dict(id=n, offers=c, rate_hz=r) for n, c, r in v2.CASES],
            runtime_bootstraps=list(BOOTSTRAPS),
            operational=False,
            remaining_time_admission="per-case envelope +3s finalization <=96s subject; group100s, two200s",
        ),
    )
    return ledger, directory, identity


def subject(root, group, *, context=None):
    from .fixture import run_fixture

    repo = Path(__file__).resolve().parents[3]
    bound_manifest = manifest if context is None else context.source_manifest
    subject_cap = 96_000_000_000 if context is None else context.SUBJECT_CAP
    expected_checks = 14 if context is None else context.EXPECTED_CHECKS
    ledger = quota.activate(root)
    directory = root / f"suite-{group}"
    prospective = json.loads((directory / "prospective.json").read_text())
    identity = prospective["source_manifest"]
    require(bound_manifest(repo) == identity, "Subject source before work")
    clocks = Clocks()
    start = clocks.continuous()
    rows = []
    primary = report_error = None
    cleanup_errors = []
    hb = ledger.open(directory / "heartbeat.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    quota.truncate(hb, 4096)
    tracker_journal = Journal(directory / "tracker.bin")
    tracker = TrackerBudget(POLICY, persist=tracker_journal.write)
    generation = 0
    attempts = []

    def heartbeat(peaks):
        nonlocal generation
        generation += 1
        # Before any spawn, no owned tracker is yet started: conservative80MiB
        # supervisor reservation, explicitly not a measured zero tracker footprint.
        value = tracker.observe(required=tracker.ready_pid is not None, peaks=peaks)
        joint = (
            value["joint_conservative_bytes"]
            if value["state"] == "observed"
            else POLICY.inner_tracker_bytes
        )
        charge = joint + peaks.get("producer", 0) + peaks.get("consumer", 0)
        b = v2.HEART.pack(
            b"LTH0053\0",
            generation,
            clocks.continuous(),
            joint,
            peaks.get("producer", 0),
            peaks.get("consumer", 0),
            charge,
            0,
        )
        b = b[:56] + struct.pack("<Q", zlib.crc32(b[:56]))
        require(quota.pwrite(hb, b, 0) == 64, "Subject heartbeat")

    def interrupted(signum, frame):
        raise TimeoutError("External source-free observer termination")

    signal.signal(signal.SIGTERM, interrupted)
    qualified = False
    try:
        heartbeat({})
        for index, (name, n, _rate) in enumerate(v2.CASES, 1):
            require(
                clocks.continuous() - start + 8_000_000_000 <= subject_cap,
                "Remaining generated envelope plus finalization",
            )
            write_attempt = (
                ledger.write_json
                if context is None
                else getattr(context, "write_attempt", ledger.write_json)
            )
            write_attempt(
                directory / f"attempt-{index}.json",
                dict(
                    index=index,
                    kind="generated",
                    case=name,
                    configured_offers=n,
                    bundle_sha256=prospective["bundle_sha256"],
                ),
            )
            attempts.append(
                dict(index=index, kind="generated", case=name, configured_offers=n)
            )
            path = directory / f"{index:02d}-{name}"
            before = clocks.continuous()
            resource_journal = Journal(path / "tracker.bin")
            prior = set(quota.FDS)
            try:
                if n:
                    result = v2.compact_report(
                        run_fixture(
                            path,
                            name,
                            task52=True,
                            quota_root=str(root),
                            heartbeat=heartbeat,
                            resource_policy=POLICY,
                            resource_publish=resource_journal.write,
                        )
                    )
                    resource_journal.close()
                    gc.collect()
                    result["semaphore_cleanup"] = v2.semaphore_absence(
                        result["synchronization_inventory"]["owned_names"]
                    )
                    result["software_checks_passed"] &= result["semaphore_cleanup"][
                        "all_absent"
                    ]
                else:
                    result = v2.report_quota_case(path, ledger)
            finally:
                resource_journal.close()
                cleanup_errors.extend(quota.emergency_release(prior, path))
            result.update(
                case_id=f"g{group}-{index:02d}-{name}",
                bundle_sha256=prospective["bundle_sha256"],
                kind="generated",
            )
            ledger.write_json(path / "result.json", result)
            heartbeat(result.get("own_process_peak_RSS_bytes", {}))
            elapsed = clocks.continuous() - before
            require(elapsed <= 5_000_000_000, "Generated5s includes report/cleanup")
            row = v2.row_from_report(
                result["case_id"], prospective["bundle_sha256"], result, elapsed
            )
            row["kind"] = "generated"
            rows.append(row)
            require(
                result["software_checks_passed"] and not cleanup_errors,
                "Unexpected generated expectation/cleanup failure",
            )
        for index, selector in enumerate(
            BOOTSTRAPS
            if context is None
            else getattr(context, "BOOTSTRAPS", BOOTSTRAPS),
            13,
        ):
            require(
                clocks.continuous() - start + 13_000_000_000 <= subject_cap,
                "Remaining runtime10s plus finalization",
            )
            ledger.write_json(
                directory / f"attempt-{index}.json",
                dict(
                    index=index,
                    kind="runtime_bootstrap",
                    case=selector,
                    configured_offers=0,
                    bundle_sha256=prospective["bundle_sha256"],
                ),
            )
            attempts.append(
                dict(
                    index=index,
                    kind="runtime_bootstrap",
                    case=selector,
                    configured_offers=0,
                )
            )
            path = directory / f"{index:02d}-{selector}"
            case_start = clocks.continuous()
            result = run_bootstrap(root, path, selector, heartbeat)
            result["case_id"] = f"g{group}-{index:02d}-{selector}"
            result["bundle_sha256"] = prospective["bundle_sha256"]
            ledger.write_json(path / "result.json", result)
            runtime_case_inclusive = clocks.continuous() - case_start
            require(
                runtime_case_inclusive <= 10_000_000_000,
                "Runtime case including parent report10s",
            )
            rows.append(
                dict(
                    case_id=result["case_id"],
                    kind="runtime_bootstrap",
                    bundle_sha256=prospective["bundle_sha256"],
                    configured_offers=0,
                    software_checks_passed=result["passed"],
                    case_inclusive_ns=runtime_case_inclusive,
                    observed_validity="payload_not_armed"
                    if result["passed"]
                    else "runtime_failed",
                )
            )
            heartbeat({})
            require(result["passed"], "Source-free runtime bootstrap failed")
        if context is not None:
            context.run_integrations(
                root, directory, group, prospective, heartbeat, rows, attempts, clocks
            )
        require(bound_manifest(repo) == identity, "Final source unchanged")
        qualified = len(rows) == expected_checks and all(
            r["software_checks_passed"] for r in rows
        )
    except BaseException as exc:
        primary = exception_record(exc)
        if hasattr(exc, "evidence"):
            primary["observation_evidence"] = exc.evidence
    finally:
        # Failures during final report/heartbeat cannot remove the primary error or
        # prevent independent resource close and outer reaping.
        value = dict(
            qualified=qualified and primary is None and not cleanup_errors,
            attempted_cases=len(attempts),
            attempts=attempts,
            rows=rows,
            primary_failure=primary,
            report_failure=None,
            cleanup_failures=cleanup_errors,
            tracker=tracker.summary(),
            payload_armed=False,
            operational=False,
            bundle_sha256=prospective["bundle_sha256"],
            source_unchanged=bound_manifest(repo) == identity,
        )
        try:
            stream = io.StringIO()
            fields = list(dict.fromkeys(k for r in rows for k in r))
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            ledger.write_bytes(directory / "cases.csv", stream.getvalue().encode())
            ledger.write_json(directory / "subject.json", value)
        except BaseException as exc:
            report_error = exception_record(exc)
            value["report_failure"] = report_error
            value["qualified"] = False
            try:
                ledger.write_json(directory / "subject-emergency.json", value)
            except BaseException:
                pass
        finally:
            try:
                tracker_journal.close()
            except (ValueError, OSError) as exc:
                cleanup_errors.append(exception_record(exc))
            try:
                quota.close(hb)
            except (ValueError, OSError) as exc:
                cleanup_errors.append(exception_record(exc))
            if cleanup_errors:
                emergency = {
                    k: v for k, v in value.items() if k not in ("rows", "tracker")
                }
                emergency["qualified"] = False
                emergency["tracker_last"] = tracker.last
                emergency["cleanup_failures"] = cleanup_errors
                try:
                    ledger.write_json(directory / "subject-emergency.json", emergency)
                except (OSError, ValueError):
                    pass
    return int(not value["qualified"] or bool(report_error) or bool(cleanup_errors))


def observe(root, group, *, context=None):
    repo = Path(__file__).resolve().parents[3]
    subject_cap = 96_000_000_000 if context is None else context.SUBJECT_CAP
    cleanup_by = 98_000_000_000 if context is None else context.CLEANUP_BY
    group_cap = 100_000_000_000 if context is None else context.GROUP_CAP
    total_cap = 200_000_000_000 if context is None else context.TOTAL_CAP
    entrypoint = SCRIPT if context is None else context.SCRIPT
    clocks = Clocks()
    outer_start = clocks.continuous()
    ledger, directory, identity = (
        prepare(root, group, repo)
        if context is None
        else prepare(root, group, repo, context=context)
    )
    before = clocks.observation()
    monitor = Monitor(*before[:2])
    process = None
    problem = None
    cleanup = None
    last = None
    peak = own_rss()
    if group == 2:
        prior = json.loads((root / "suite-1/observer.json").read_text())
        require(
            prior["group_total_ns"] + group_cap <= total_cap,
            "Remaining whole qualification admission",
        )
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                str(repo / entrypoint),
                "--subject",
                "--root",
                str(root),
                "--group",
                str(group),
            ],
            cwd=repo,
            env={**os.environ, **ENVIRONMENT, "PYTHONDONTWRITEBYTECODE": "1"},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        while process.poll() is None:
            service, now, _ = clocks.observation()
            monitor.observe(service, now)
            require(
                now - outer_start <= subject_cap,
                "Subject deadline reserves cleanup/receipt",
            )
            peak = max(peak, own_rss())
            require(peak <= POLICY.outer_bytes, "Outer48MiB")
            h = v2.read_heartbeat(directory / "heartbeat.bin")
            if h:
                last = h
                require(now - h[2] <= 2_000_000_000, "Subject/report heartbeat2s")
                require(
                    h[3] <= POLICY.inner_tracker_bytes
                    and h[4] <= POLICY.producer_bytes
                    and h[5] <= POLICY.consumer_bytes,
                    "Role/joint RSS",
                )
                require(
                    h[6] + peak <= POLICY.resident_bytes
                    and h[6] + peak <= POLICY.aggregate_bytes,
                    "Summed resident resources",
                )
            else:
                require(now - before[1] <= 7_500_000_000, "Import/setup allowance7.5s")
            time.sleep(0.005)
        process.wait()
    except BaseException as exc:
        problem = exception_record(exc)
    finally:
        if process is not None:
            cleanup = v2.tree_cleanup(
                process,
                clocks,
                min(outer_start + cleanup_by, clocks.continuous() + 2_000_000_000),
            )
        after = clocks.observation()
    subject_path = directory / "subject.json"
    subject_result = None
    missing = None
    try:
        if subject_path.exists():
            subject_result = json.loads(subject_path.read_text())
        else:
            missing = "subject.json missing after exit/reap; no normal qualification"
    except (ValueError, OSError) as exc:
        missing = str(exc)[:500]
    passed = bool(
        not problem
        and not missing
        and subject_result
        and subject_result["qualified"]
        and cleanup
        and cleanup["exitcode"] == 0
        and cleanup["subject_reaped"]
        and cleanup["owned_group_absent"]
        and not cleanup["forced"]
    )
    receipt = dict(
        qualified=passed,
        problem=problem,
        missing_subject_report=missing,
        subject={
            k: v for k, v in subject_result.items() if k not in ("rows", "tracker")
        }
        if subject_result
        else None,
        cleanup=cleanup,
        source_manifest=identity,
        bundle_sha256=v2.fingerprint(identity),
        subject_service_bracket_ns=[before[0], after[0]],
        subject_continuous_bracket_ns=[before[1], after[1]],
        subject_lifetime_ns=after[1] - before[1],
        outer_peak_RSS_bytes=peak,
        maximum_monitor_gap_ns=monitor.maximum_gap,
        observer_SemLocks=0,
        observer_receipt_outside_subject=True,
        observer_overhead_reserve_ns=4_000_000_000,
        group_before_receipt_ns=clocks.continuous() - outer_start,
        group_total_ns=after[1] - before[1] + 4_000_000_000,
        group_cap_ns=group_cap,
        storage=ledger.inventory(),
        payload_armed=False,
        operational=False,
        last_heartbeat=list(last[1:]) if last else None,
    )
    try:
        ledger.write_json(directory / "observer.json", receipt)
    except (OSError, ValueError) as exc:
        receipt["qualified"] = False
        receipt["receipt_failure"] = exception_record(exc)
        try:
            ledger.write_bytes(
                directory / "observer-emergency.txt", b"RECEIPT_FAILURE_AFTER_REAP\n"
            )
        except (OSError, ValueError):
            pass
    require(
        clocks.continuous() - outer_start <= group_cap,
        "Group envelope including observer receipt",
    )
    return receipt
