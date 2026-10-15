"""Fixed Task0053 generated qualification, immutable reservations and no operational provider."""

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
from pathlib import Path

from . import quota
from .protocol import require
from .supervision import Clocks, Monitor, own_rss

CONFIG = "configs/streaming/development_streaming_validation_v2.json"
PROTOCOL = "configs/protocols/development_streaming_v2.json"
CASES = (
    ("normal500", 128, 500),
    ("normal2500", 128, 2500),
    ("normal5000", 128, 5000),
    ("capacity", 96, 500),
    ("contention", 32, 1000),
    ("die_before_return", 8, 500),
    ("die_after_return", 8, 500),
    ("die_after_output", 8, 500),
    ("failed_start", 8, 500),
    ("torn_publication", 8, 500),
    ("failed_publication_cleanup", 8, 500),
    ("observer_report_quota", 0, 0),
)
OUTER_RSS = 48 * 1024**2
INNER_RSS = 80 * 1024**2
HEART = struct.Struct(
    "<8sQQQQQQQ"
)  # 64B, generation/time/inner/prod/consumer/RSScharge/CRC


def file_plan():
    files = {
        "ledger.json": 65536,
        "owner.json": 1024,
        "historical.json": 8192,
        "aggregate.json": 524288,
        "cases.csv": 32768,
        # Unmaterialized reservations charge simultaneous curated copies too.
        "curated-summary-copy.reserved": 524288,
        "curated-csv-copy.reserved": 32768,
        "curated-text-copy.reserved": 131072,
    }
    for suite in (1, 2):
        prefix = f"suite-{suite}"
        files.update(
            {
                f"sources-{suite}.json": 524288,
                f"{prefix}/prospective.json": 65536,
                f"{prefix}/observer.json": 8192,
                f"{prefix}/heartbeat.bin": 4096,
                f"{prefix}/cases.csv": 16384,
                f"{prefix}/subject.json": 8192,
                f"{prefix}/observer-emergency.txt": 1024,
            }
        )
        for i, (name, n, _) in enumerate(CASES, 1):
            d = f"{prefix}/{i:02d}-{name}"
            files.update({f"{d}/result.json": 131072, f"{d}/emergency.txt": 1024})
            if n:
                files.update(
                    {
                        f"{d}/fixture-ring.shm": 12288,
                        f"{d}/events.bin": n * 512,
                        f"{d}/batches.bin": n * 512,
                        f"{d}/outputs.bin": n * 12,
                        f"{d}/producer-samples.bin": 768 * 64,
                        f"{d}/consumer-samples.bin": 4096 * 64,
                        f"{d}/counter-preflight.json": 1024,
                    }
                )
                for role in ("producer", "consumer", "supervisor"):
                    files[f"{d}/{role}-phases.bin"] = 32 * 512
            else:
                files.update(
                    {f"{d}/cleanup-guard.bin": 4096, f"{d}/quota-target.bin": 16}
                )
    require(
        len(files) <= 512 and sum(files.values()) <= quota.CAP,
        "Complete prospective storage plan",
    )
    return files


def source_paths(root):
    return sorted((root / "src/latenttrigger/streaming").glob("*.py")) + [
        root / "scripts/validate_development_streaming_v2.py",
        root / "tests/test_development_streaming_foundation.py",
        root / "tests/test_development_streaming_instrumentation.py",
        root / "tests/test_development_streaming_contract_v2.py",
        root / CONFIG,
        root / PROTOCOL,
        root / "docs/prompts/0053-streaming-contract-v2-validation.md",
    ]


def source_manifest(root):
    return [
        dict(
            path=str(p.relative_to(root)),
            size_bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
        )
        for p in source_paths(root)
        for b in [p.read_bytes()]
    ]


def fingerprint(manifest):
    return hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def prepare(root, suite, repo):
    require(suite in (1, 2), "At most two frozen suites")
    require(
        root.is_absolute()
        and root.parent == repo / "data/task0053-validation"
        and root.parent.resolve() == root.parent,
        "New canonical Task0053 root",
    )
    files = file_plan()
    if suite == 1:
        require(not root.exists(), "No reuse/overwrite of earlier evidence")
        root.parent.mkdir(parents=True, exist_ok=True)
        root.mkdir(mode=0o700)
        ledger = quota.Ledger(root, files)
        # The full immutable plan, including this file, is reserved before creation.
        ledger.write_json(
            root / "ledger.json", dict(task="0053", cap_bytes=quota.CAP, files=files)
        )
        ledger.write_json(
            root / "owner.json",
            dict(task="0053", generated_only=True, operational=False),
        )
    else:
        require((root / "suite-1/observer.json").is_file(), "Prior receipt required")
        prior = json.loads((root / "suite-1/observer.json").read_text())
        require(
            not prior["qualified"] and not (root / "suite-2").exists(),
            "Second suite only after correctness failure",
        )
        ledger = quota.activate(root)
    ledger = quota.activate(root)
    require(ledger.entries == files, "Original whole-task plan unchanged")
    directory = root / f"suite-{suite}"
    directory.mkdir(mode=0o700)
    manifest = source_manifest(repo)
    for x in json.loads((repo / CONFIG).read_text())["source_manifest"]:
        require(x in manifest, "Frozen configured code identity")
    if suite == 2:
        old = json.loads((root / "suite-1/prospective.json").read_text())
        require(
            fingerprint(manifest) != old["bundle_sha256"], "No favorable-sample rerun"
        )
    ledger.write_json(
        root / f"sources-{suite}.json",
        {str(p.relative_to(repo)): p.read_text() for p in source_paths(repo)},
    )
    ledger.write_json(
        directory / "prospective.json",
        dict(
            source_manifest=manifest,
            bundle_sha256=fingerprint(manifest),
            case_order=[dict(id=n, offers=c, rate_hz=r) for n, c, r in CASES],
            whole_task_reserved_bytes=sum(files.values()),
            cap_bytes=quota.CAP,
            no_native_case_started=True,
            fixture_only=True,
        ),
    )
    return ledger, directory, manifest


def write_heartbeat(fd, clocks, peaks, generation):
    from .resources import POLICY, heartbeat_joint

    inner = heartbeat_joint(peaks, POLICY)
    require(inner <= INNER_RSS, "Inner RSS guard")
    prod, consumer = peaks.get("producer", 0), peaks.get("consumer", 0)
    # Conservative resident-native charge, not attribution of native workspace.
    charge = inner + prod + consumer
    require(charge + OUTER_RSS <= 512 * 1024**2, "Conservative512MiB resident charge")
    b = HEART.pack(
        b"LTH0053\0", generation, clocks.continuous(), inner, prod, consumer, charge, 0
    )
    b = b[:56] + struct.pack("<Q", zlib.crc32(b[:56]))
    require(quota.pwrite(fd, b, 0) == 64, "Short heartbeat")


def read_heartbeat(path):
    if not path.exists():
        return None
    with open(path, "rb", buffering=0) as f:
        b = f.read(64)
    if len(b) != 64 or b == bytes(64):
        return None
    r = HEART.unpack(b)
    if r[0] != b"LTH0053\0" or r[-1] != zlib.crc32(b[:56]):
        return None  # concurrent publication, not success
    return r


def semaphore_absence(names):
    """Open-only query of our own already-finalized names; creates no SemLock."""
    import ctypes
    import errno

    lib = ctypes.CDLL(None, use_errno=True)
    lib.sem_open.restype = ctypes.c_void_p
    lib.sem_open.argtypes = [ctypes.c_char_p, ctypes.c_int]
    lib.sem_close.argtypes = [ctypes.c_void_p]
    absent = 0
    for name in names:
        ctypes.set_errno(0)
        handle = lib.sem_open(name.encode(), 0)
        error = ctypes.get_errno()
        if handle in (None, ctypes.c_void_p(-1).value):
            require(error == errno.ENOENT, "Own semaphore absence query unknown")
            absent += 1
        else:
            lib.sem_close(handle)
    return dict(
        names_checked=len(names),
        absent=absent,
        all_absent=absent == len(names),
        kernel_backing_bytes=None,
    )


def report_quota_case(directory, ledger):
    directory.mkdir()
    guard = directory / "cleanup-guard.bin"
    fd = ledger.open(guard, os.O_CREAT | os.O_EXCL | os.O_RDWR)
    quota.truncate(fd, 4096)
    rejected = False
    try:
        try:
            ledger.write_bytes(directory / "quota-target.bin", bytes(17))
        except quota.QuotaError:
            rejected = True
            ledger.write_bytes(
                directory / "emergency.txt",
                b"EXPECTED_FINAL_REPORT_PRE_GROWTH_REJECTION\n",
            )
    finally:
        quota.close(fd)
        guard.unlink()  # resource cleanup; reservation is never released
    passed = (
        rejected
        and not guard.exists()
        and not (directory / "quota-target.bin").exists()
    )
    return dict(
        scenario="observer_report_quota",
        configured_offers=0,
        normal=False,
        expected_validity="invalid_reporting_quota",
        observed_validity="invalid_reporting_quota",
        software_checks_passed=passed,
        software_checks=dict(
            pre_growth_rejected=rejected,
            no_overquota_file=not (directory / "quota-target.bin").exists(),
            cleanup_absent=not guard.exists(),
        ),
        accounting=None,
        synthetic_stage_counts=None,
        append_diagnostics={},
        native_numerical_work=False,
        cleanup_resource_retired=True,
        external_receipt_required=True,
    )


def compact_report(report):
    # Preserve every homogeneous aggregate using one shared column schema.
    fields = [
        "operation",
        "stage",
        "m",
        "updates",
        "n",
        "sum_ns",
        "mean_ns",
        "median_ns",
        "p95_ns",
        "p99_ns",
        "maximum_ns",
        "threshold_ns",
        "exceeds",
    ]
    aggregates = report.pop("sample_aggregates", {})
    report["sample_aggregate_columns"] = fields
    report["sample_aggregates"] = {
        role: [[g[k] for k in fields] for g in groups] if groups is not None else None
        for role, groups in aggregates.items()
    }
    report["append_diagnostics"] = {}
    for op in ("event_append", "batch_append"):
        gs = [
            g
            for groups in aggregates.values()
            if groups
            for g in groups
            if g["operation"] == op
        ]
        report["append_diagnostics"][op] = dict(
            n=sum(g["n"] for g in gs),
            exceeds=sum(g["exceeds"] for g in gs),
            maximum_ns=max((g["maximum_ns"] for g in gs), default=None),
        )
    report["child_summary_available"] = (
        "v2 intentionally has no redundant child JSON;fixed phases/samples+exit codes authoritative"
    )
    report["expected_validity"] = (
        "valid_drained"
        if report["scenario"]
        in ("normal500", "normal2500", "normal5000", "capacity", "contention")
        else "expected_invalid_injected"
    )
    report["observed_validity"] = (
        "valid_drained" if report["normal"] else "invalid_injected_or_failed"
    )
    return report


def row_from_report(case_id, bundle, report, case_elapsed):
    a = (report.get("accounting") or {}).get("after_stop")
    counts = report.get("synthetic_stage_counts")
    diag = report.get("append_diagnostics", {})
    return dict(
        case_id=case_id,
        bundle_sha256=bundle,
        expected_validity=report.get("expected_validity"),
        observed_validity=report.get("observed_validity"),
        software_checks_passed=report["software_checks_passed"],
        configured_offers=report["configured_offers"],
        issued_offers=a["submitted"] if a else None,
        completed=a["completed"] if a else None,
        pending=sum(a[k] for k in ("ring", "staged", "active")) if a else None,
        unresolved=a["unresolved"] if a else None,
        undecided=a["undecided"] if a else None,
        read_rows=counts["read_rows"] if counts else None,
        score_rows=counts["score_rows"] if counts else None,
        reference_rows=counts["reference_rows"] if counts else None,
        boolean_outputs=a["boolean_outputs"] if a else None,
        event_append_n=diag.get("event_append", {}).get("n", 0),
        event_exceeds=diag.get("event_append", {}).get("exceeds", 0),
        batch_append_n=diag.get("batch_append", {}).get("n", 0),
        batch_exceeds=diag.get("batch_append", {}).get("exceeds", 0),
        core_SemLocks=report.get("synchronization_inventory", {}).get(
            "actual_SemLocks", 0
        ),
        semaphore_cleanup=report.get("semaphore_cleanup", {}).get("all_absent", True),
        cleanup_ns=report.get("cleanup_ns"),
        case_inclusive_ns=case_elapsed,
        monitor_gap_ns=report.get("maximum_monitor_gap_ns"),
        coverage="same_frozen_bundle",
    )


def subject(root, suite):
    # Imported only in a new, externally observed interpreter.
    from .fixture import run_fixture

    repo = Path(__file__).resolve().parents[3]
    ledger = quota.activate(root)
    directory = root / f"suite-{suite}"
    prospective = json.loads((directory / "prospective.json").read_text())
    manifest_fn = source_manifest
    if ledger.task == "0054":
        from .pilot54 import source_manifest as manifest_fn
    require(
        manifest_fn(repo) == prospective["source_manifest"],
        "Subject frozen identity before work",
    )
    clocks = Clocks()
    started = clocks.continuous()
    hb = ledger.open(directory / "heartbeat.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    quota.truncate(hb, 4096)
    rows = []
    generation = 0

    def heartbeat(peaks):
        nonlocal generation
        generation += 1
        write_heartbeat(hb, clocks, peaks, generation)

    def interrupted(signum, frame):
        raise TimeoutError("External observer termination")

    signal.signal(signal.SIGTERM, interrupted)
    try:
        heartbeat({})
        for index, (name, n, _rate) in enumerate(CASES, 1):
            require(
                clocks.continuous() - started < 68_000_000_000,
                "Subject finalization reserve",
            )
            path = directory / f"{index:02d}-{name}"
            before = clocks.continuous()
            heartbeat({})
            try:
                if n:
                    prior_fds = set(quota.FDS)
                    try:
                        r = compact_report(
                            run_fixture(
                                path,
                                name,
                                task52=True,
                                quota_root=str(root),
                                heartbeat=heartbeat,
                            )
                        )
                    finally:
                        release_errors = quota.emergency_release(prior_fds, path)
                    require(
                        not release_errors, "Emergency setup/resource cleanup failure"
                    )
                    names = r["synchronization_inventory"]["owned_names"]
                    require(
                        r["synchronization_inventory"]["actual_SemLocks"] <= 21,
                        "Core primitive bound",
                    )
                    gc.collect()
                    r["semaphore_cleanup"] = semaphore_absence(names)
                    r["software_checks_passed"] &= r["semaphore_cleanup"]["all_absent"]
                    # Missing/corrupt records never become a valid normal workload.
                    if r["normal"]:
                        require(
                            r["accounting_status"] == "reconciled",
                            "Normal accounting validity",
                        )
                else:
                    r = report_quota_case(path, ledger)
                r["case_id"] = f"s{suite}-{index:02d}-{name}"
                r["bundle_sha256"] = prospective["bundle_sha256"]
                ledger.write_json(path / "result.json", r)
                # Includes serialization/file close, GC and semaphore retirement.
                heartbeat(r.get("own_process_peak_RSS_bytes", {}))
                require(
                    ledger.inventory()["logical_bytes"] <= ledger.cap,
                    "Whole-task actual audit",
                )
                elapsed = clocks.continuous() - before
                require(elapsed <= 5_000_000_000, "Case inclusive5s")
                rows.append(
                    row_from_report(
                        r["case_id"], prospective["bundle_sha256"], r, elapsed
                    )
                )
                heartbeat(r.get("own_process_peak_RSS_bytes", {}))
                require(
                    ledger.inventory()["logical_bytes"] <= ledger.cap,
                    "Whole-task actual audit",
                )
                if not r["software_checks_passed"]:
                    break
            except Exception as exc:
                # Fixed emergency path was reserved up front, even when ordinary reporting fails.
                text = (type(exc).__name__ + ": " + str(exc))[:900].encode()
                if path.exists() and not (path / "emergency.txt").exists():
                    ledger.write_bytes(path / "emergency.txt", text)
                rows.append(
                    dict(
                        case_id=f"s{suite}-{index:02d}-{name}",
                        bundle_sha256=prospective["bundle_sha256"],
                        configured_offers=n,
                        software_checks_passed=False,
                        observed_validity="unknown_or_failed",
                        error=text.decode(),
                    )
                )
                break
        stream = io.StringIO()
        fields = list(dict.fromkeys(k for r in rows for k in r))
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        ledger.write_bytes(directory / "cases.csv", stream.getvalue().encode())
        require(
            manifest_fn(repo) == prospective["source_manifest"],
            "Final frozen identity",
        )
        heartbeat({})
        result = dict(
            qualified=len(rows) == 12
            and all(r["software_checks_passed"] for r in rows),
            attempted_cases=len(rows),
            configured_offers=sum(r["configured_offers"] for r in rows),
            bundle_sha256=prospective["bundle_sha256"],
            full_final_source_coverage=len(rows) == 12,
            observer_receipt_required=True,
            all_owned_children_reaped=all(
                not p.is_alive()
                for p in __import__("multiprocessing").active_children()
            ),
        )
        ledger.write_json(directory / "subject.json", result)
    finally:
        quota.close(hb)
    return int(not result["qualified"])


def owned_group_exists(pid):
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False


def tree_cleanup(process, clocks, deadline):
    """Signal the owned session; inner handler first gets a chance to reap roles."""
    actions = []
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        actions.append("SIGTERM_owned_group")
        try:
            process.wait(
                timeout=max(0, min(1.5, (deadline - clocks.continuous()) / 1e9))
            )
        except subprocess.TimeoutExpired:
            pass
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGKILL)
        actions.append("SIGKILL_owned_group")
        try:
            process.wait(timeout=max(0, (deadline - clocks.continuous()) / 1e9))
        except subprocess.TimeoutExpired:
            pass
    # Reap the direct subject and wait for its own tracker/descendant session to
    # retire. Forced group kill is uncertainty, never proof of grandchild reaping.
    while owned_group_exists(process.pid) and clocks.continuous() < deadline:
        time.sleep(0.005)
    absent = not owned_group_exists(process.pid)
    if not absent:
        os.killpg(process.pid, signal.SIGKILL)
        actions.append("SIGKILL_remaining_owned_group")
        absent = not owned_group_exists(process.pid)
    return dict(
        owned_group_absent=absent,
        actions=actions,
        exitcode=process.poll(),
        subject_reaped=process.poll() is not None,
        forced=bool(actions),
        descendant_cleanup="normal subject receipts required;forced group termination does not invent descendant reaping evidence",
    )


def observe(root, suite, *, task="0053"):
    repo = Path(__file__).resolve().parents[3]
    clocks = Clocks()
    outer_start = clocks.continuous()
    if task == "0054":
        from .pilot54 import prepare_generated

        ledger, directory, manifest = prepare_generated(root, suite, repo)
    else:
        require(task == "0053", "Explicit generated task")
        ledger, directory, manifest = prepare(root, suite, repo)
    require(own_rss() <= OUTER_RSS, "Outer RSS48MiB")
    before = clocks.observation()
    monitor = Monitor(*before[:2])
    # No observer Event/SemLock/Queue/Pipe. Stdio discarded prospectively; bounded
    # journals, exceptions and exit codes carry evidence, not an unbounded pipe.
    process = None
    problem = None
    cleanup = None
    peak = own_rss()
    latest = None
    deadline = outer_start + 70_000_000_000
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                str(
                    repo
                    / (
                        "scripts/development_hdf_consumer_pilot.py"
                        if task == "0054"
                        else "scripts/validate_development_streaming_v2.py"
                    )
                ),
                "--generated-subject" if task == "0054" else "--subject",
                "--root",
                str(root),
                "--suite",
                str(suite),
            ],
            cwd=repo,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        while process.poll() is None:
            svc, cont, _ = clocks.observation()
            monitor.observe(svc, cont)
            require(
                cont < deadline, "External whole subject deadline including reporting"
            )
            peak = max(peak, own_rss())
            require(peak <= OUTER_RSS, "Outer RSS ceiling")
            h = read_heartbeat(directory / "heartbeat.bin")
            if h is None and latest is None:
                require(
                    cont - before[1] <= 7_500_000_000, "Subject import/setup deadline"
                )
            if h:
                latest = h
                require(
                    cont - h[2] <= 2_000_000_000, "Subject heartbeat/reporting liveness"
                )
                require(
                    h[3] <= INNER_RSS and h[4] <= 64 * 1024**2 and h[5] <= 1024**3,
                    "Concurrent role RSS",
                )
                require(
                    peak + h[6] <= 512 * 1024**2 and peak + h[6] <= 1216 * 1024**2,
                    "Concurrent resource charges",
                )
            time.sleep(0.005)
        process.wait()  # reap after reports/handles/finalizers/interpreter shutdown
    except Exception as exc:
        problem = (type(exc).__name__ + ": " + str(exc))[:900]
    finally:
        if process is not None:
            cleanup = tree_cleanup(
                process,
                clocks,
                min(outer_start + 72_000_000_000, clocks.continuous() + 2_000_000_000),
            )
        after = clocks.observation()  # external end after subject exited AND reaped
    subject_path = directory / "subject.json"
    try:
        subject_result = (
            json.loads(subject_path.read_text()) if subject_path.exists() else None
        )
    except (ValueError, OSError):
        subject_result = None
    qualified = bool(
        problem is None
        and cleanup
        and cleanup["subject_reaped"]
        and cleanup["owned_group_absent"]
        and not cleanup["forced"]
        and cleanup["exitcode"] == 0
        and subject_result
        and subject_result["qualified"]
        and subject_result["all_owned_children_reaped"]
        and latest is not None
    )
    receipt = dict(
        qualified=qualified,
        problem=problem,
        subject=subject_result,
        cleanup=cleanup,
        source_manifest=manifest,
        bundle_sha256=fingerprint(manifest),
        subject_service_bracket_ns=[before[0], after[0]],
        subject_continuous_bracket_ns=[before[1], after[1]],
        subject_lifetime_ns=after[1] - before[1],
        clock_call_brackets_ns=[before[2], after[2]],
        maximum_monitor_gap_ns=monitor.maximum_gap,
        outer_peak_RSS_bytes=peak,
        observer_explicit_SemLocks=0,
        active_tree_explicit_SemLocks_cap=26,
        last_heartbeat=list(latest[1:]) if latest else None,
        storage=ledger.inventory(),
        observer_overhead_reserve_ns=5_000_000_000,
        per_launch_total_cap_ns=75_000_000_000,
        measured_boundary="before Popen/import to after exit/reap;observer receipt outside subject,charged separately",
        no_operational_work=True,
    )
    try:
        ledger.write_json(directory / "observer.json", receipt)
    except (quota.QuotaError, OSError) as exc:
        receipt["qualified"] = False
        receipt["receipt_write_error"] = str(exc)[:800]
        try:
            ledger.write_bytes(
                directory / "observer-emergency.txt",
                b"OBSERVER_RECEIPT_FAILURE_AFTER_REAP\n",
            )
        except (quota.QuotaError, OSError):
            pass  # no diagnostic can undo completed resource cleanup; validity unknown
    require(
        clocks.continuous() - outer_start <= 75_000_000_000,
        "Observer total including receipt75s",
    )
    require(ledger.inventory()["logical_bytes"] <= ledger.cap, "Final global files")
    return receipt
