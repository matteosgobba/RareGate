"""Task0054 closed manifest and one-session orchestration. No numeric imports."""

import hashlib
import json
import os
from pathlib import Path

from . import quota
from . import validation_v2 as v2
from .protocol import require

CONFIG = "configs/streaming/development_hdf_consumer_pilot_v1.json"
ROOT_NAME = "session-v1"
CAP = 32 * 1024**2


def file_plan():
    files = v2.file_plan()
    files.update(
        {
            "bootstrap.json": 32768,
            "software-checks.txt": 1048576,
            "software-checks-2.txt": 1048576,
            "pilot/prospective.json": 131072,
            "pilot/activation.json": 4096,
            "pilot/heartbeat.bin": 4096,
            "pilot/custody.bin": 4096,
            "pilot/observer.json": 16384,
            "pilot/observer-emergency.txt": 1024,
            "pilot/subject.json": 131072,
            "pilot/emergency.txt": 4096,
            "delivery-summary.json": 1048576,
            "delivery-cases.csv": 65536,
            "delivery-text.md": 131072,
            "curated-pilot-summary-copy.reserved": 1048576,
            "curated-pilot-cases-copy.reserved": 65536,
        }
    )
    for candidate in ("pca-v1", "compact-autoencoder-v2"):
        d = f"pilot/{candidate}"
        files.update(
            {
                f"{d}/fixture-ring.shm": 12288,
                f"{d}/events.bin": 64 * 512,
                f"{d}/batches.bin": 64 * 512,
                f"{d}/outputs.bin": 64 * 12,
                f"{d}/producer-samples.bin": 768 * 64,
                f"{d}/consumer-samples.bin": 4096 * 64,
                f"{d}/result.json": 131072,
                f"{d}/consumer-audit.bin": 65536,
                f"{d}/consumer-final.json": 65536,
            }
        )
        for role in ("producer", "consumer", "supervisor"):
            files[f"{d}/{role}-phases.bin"] = 32 * 512
    require(len(files) <= 512 and sum(files.values()) <= CAP, "Task0054 full ledger")
    return files


def initialize(root, repo):
    require(
        root == repo / "data/task0054-validation" / ROOT_NAME,
        "Single new Task0054 root",
    )
    require(
        not root.exists() and root.parent.resolve() == root.parent,
        "No prior session overwrite or redirects",
    )
    files = file_plan()
    root.mkdir(mode=0o700, parents=True)
    ledger = quota.Ledger(root, files, task="0054")
    ledger.write_json(
        root / "ledger.json", dict(task="0054", cap_bytes=CAP, files=files)
    )
    ledger.write_json(
        root / "owner.json", dict(task="0054", generated_and_conditional_pilot=True)
    )
    return quota.activate(root)


def source_paths(repo):
    return (
        sorted((repo / "src/latenttrigger/streaming").glob("*.py"))
        + [
            repo / "scripts/development_hdf_consumer_pilot.py",
            repo / "tests/test_development_hdf_consumer_pilot.py",
            repo / CONFIG,
            repo / "docs/prompts/0054-development-hdf-consumer-pilot.md",
        ]
        + [
            repo / x["path"]
            for x in json.loads((repo / CONFIG).read_text())["reused_source_manifest"]
        ]
    )


def source_manifest(repo):
    return [
        dict(
            path=str(p.relative_to(repo)),
            size_bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
        )
        for p in source_paths(repo)
        for b in [p.read_bytes()]
    ]


def prepare_generated(root, suite, repo):
    ledger = quota.activate(root)
    require(ledger.task == "0054" and ledger.entries == file_plan(), "Task0054 ledger")
    require(suite in (1, 2), "Two suites maximum")
    if suite == 2:
        prior = json.loads((root / "suite-1/observer.json").read_text())
        pilot_failure = root / "pilot/observer.json"
        repaired_after_failed_pilot = (
            pilot_failure.exists()
            and not json.loads(pilot_failure.read_text())["qualified"]
        )
        require(
            not prior["qualified"] or repaired_after_failed_pilot,
            "Only correctness repair, no favorable rerun",
        )
    directory = root / f"suite-{suite}"
    directory.mkdir(mode=0o700)
    manifest = source_manifest(repo)
    config = json.loads((repo / CONFIG).read_text())
    validate_spec(config, repo)
    for pin in config["code_manifest"]:
        require(pin in manifest, "Configured source pin")
    if suite == 2:
        prior = json.loads((root / "suite-1/prospective.json").read_text())
        require(
            v2.fingerprint(manifest) != prior["bundle_sha256"],
            "Repair requires new source",
        )
    ledger.write_json(
        root / f"sources-{suite}.json",
        {str(p.relative_to(repo)): p.read_text() for p in source_paths(repo)},
    )
    ledger.write_json(
        directory / "prospective.json",
        dict(
            source_manifest=manifest,
            bundle_sha256=v2.fingerprint(manifest),
            task="0054",
            generated_only=True,
            case_order=[dict(id=n, offers=c, rate_hz=r) for n, c, r in v2.CASES],
            reserved_bytes=sum(ledger.entries.values()),
        ),
    )
    return ledger, directory, manifest


def fixed_path(repo, entry):
    """Check every ancestor before opening; no alternative paths, links or hardlinks."""
    import stat

    p = repo / entry["path"]
    require(
        not Path(entry["path"]).is_absolute() and ".." not in Path(entry["path"]).parts,
        "Closed repository relative source",
    )
    current = repo
    for part in Path(entry["path"]).parts:
        current /= part
        require(not current.is_symlink(), "No source symlink redirects")
    info = p.stat()
    require(
        stat.S_ISREG(info.st_mode)
        and info.st_nlink == 1
        and info.st_size == entry["bytes"],
        "Exact regular source size and ownership",
    )
    return p


def source_bytes(repo, entry):
    p = fixed_path(repo, entry)
    require(entry["bytes"] <= 1048576, "Small closed source")
    with p.open("rb") as f:
        b = f.read(entry["bytes"] + 1)
    require(
        len(b) == entry["bytes"] and hashlib.sha256(b).hexdigest() == entry["sha256"],
        "Closed source bytes",
    )
    return b


def custody(root, ledger, spec, phase, clocks, heartbeat):
    """One of exactly two monitored raw-byte passes; never an HDF open."""
    import struct

    entry = next(x for x in spec["allowed_files"] if x["role"] == "raw")
    path = fixed_path(Path(__file__).resolve().parents[3], entry)
    fd = (
        ledger.open(root / "pilot/custody.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
        if phase == 1
        else ledger.open(root / "pilot/custody.bin", os.O_RDWR)
    )
    if phase == 1:
        quota.truncate(fd, 4096)
    begin = clocks.continuous()
    sha, count = hashlib.sha256(), 0
    try:
        # One fixed1MiB buffer; no allocating two adjacent read chunks.
        buffer = bytearray(1048576)
        with path.open("rb", buffering=0) as stream:
            while n := stream.readinto(buffer):
                require(clocks.continuous() - begin <= 45_000_000_000, "Custody45s")
                sha.update(memoryview(buffer)[:n])
                count += n
                require(count <= entry["bytes"], "Custody growth")
                heartbeat({})
                b = struct.pack(
                    "<QQQQ32s", phase, count, begin, clocks.continuous(), sha.digest()
                )
                require(
                    quota.pwrite(fd, b, (phase - 1) * 128) == len(b), "Custody progress"
                )
        require(
            count == entry["bytes"] and sha.hexdigest() == entry["sha256"],
            "Raw custody identity",
        )
        return dict(
            phase=phase,
            bytes=count,
            sha256=sha.hexdigest(),
            elapsed_ns=clocks.continuous() - begin,
            passed=True,
        )
    finally:
        quota.close(fd)


def pilot_subject(root):
    """No payload reads occur before immutable activation and source verification."""
    import signal

    from .fixture import run_pilot_core
    from .supervision import Clocks

    repo = Path(__file__).resolve().parents[3]
    ledger = quota.activate(root)
    spec = json.loads((repo / CONFIG).read_text())
    prospective = json.loads((root / "pilot/prospective.json").read_text())
    require(
        source_manifest(repo) == prospective["source_manifest"], "Final pilot bundle"
    )
    clocks = Clocks()
    hb = ledger.open(root / "pilot/heartbeat.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    quota.truncate(hb, 4096)
    phase, generation = 1, 0
    results, hashes, problem = [], [], None

    def heartbeat(peaks):
        nonlocal generation
        generation += 1
        v2.write_heartbeat(hb, clocks, peaks, (phase << 32) + generation)

    def terminate(signum, frame):
        raise TimeoutError("Pilot external termination")

    signal.signal(signal.SIGTERM, terminate)
    # Exclusive activation consumes the one-session grant, even if custody fails.
    ledger.write_json(
        root / "pilot/activation.json",
        dict(
            task="0054",
            single_session=True,
            bundle_sha256=prospective["bundle_sha256"],
            continuous_ns=clocks.continuous(),
        ),
    )
    try:
        heartbeat({})
        hashes.append(custody(root, ledger, spec, 1, clocks, heartbeat))
        for candidate in ("pca-v1", "compact-autoencoder-v2"):
            phase = 2 if candidate == "pca-v1" else 3
            heartbeat({})
            prior = set(quota.FDS)
            try:
                report = v2.compact_report(
                    run_pilot_core(
                        root / "pilot" / candidate,
                        candidate,
                        quota_root=str(root),
                        heartbeat=heartbeat,
                    )
                )
            finally:
                errors = quota.emergency_release(prior, root / "pilot" / candidate)
            require(not errors, "Pilot emergency resource release")
            import gc

            gc.collect()
            report["semaphore_cleanup"] = v2.semaphore_absence(
                report["synchronization_inventory"]["owned_names"]
            )
            final_path = root / "pilot" / candidate / "consumer-final.json"
            final = json.loads(final_path.read_text()) if final_path.exists() else None
            report["real_consumer"] = final
            report["candidate"] = candidate
            report["expected_validity"] = "valid_drained_with_all_parity"
            report["observed_validity"] = (
                "valid"
                if report["normal"] and final and final["valid"]
                else "invalid_or_incomplete"
            )
            report["software_checks_passed"] &= bool(
                final and final["valid"] and report["semaphore_cleanup"]["all_absent"]
            )
            ledger.write_json(root / "pilot" / candidate / "result.json", report)
            results.append(
                dict(candidate=candidate, valid=report["software_checks_passed"])
            )
            require(
                report["software_checks_passed"],
                "Unexpected pilot validity failure; no replacement",
            )
            heartbeat({})
    except Exception as exc:
        problem = (type(exc).__name__ + ": " + str(exc))[:900]
        ledger.write_bytes(root / "pilot/emergency.txt", problem.encode())
    finally:
        phase = 4
        try:
            heartbeat({})
            hashes.append(custody(root, ledger, spec, 2, clocks, heartbeat))
        except Exception as exc:
            problem = problem or (type(exc).__name__ + ": " + str(exc))[:900]
        phase = 5
        heartbeat({})
        frozen = source_manifest(repo) == prospective["source_manifest"]
        qualified = (
            problem is None and len(results) == 2 and len(hashes) == 2 and frozen
        )
        ledger.write_json(
            root / "pilot/subject.json",
            dict(
                qualified=qualified,
                problem=problem,
                cases=results,
                custody=hashes,
                source_unchanged=frozen,
                unattempted_candidates=[
                    c
                    for c in ("pca-v1", "compact-autoencoder-v2")
                    if c not in [x["candidate"] for x in results]
                ],
                operational_access_activated=True,
            ),
        )
        quota.close(hb)
    return int(not qualified)


def observe_pilot(root):
    """Narrow external180s watchdog, before subject imports through reap/retirement."""
    import subprocess
    import sys
    import time

    from .supervision import Clocks, Monitor, own_rss

    repo = Path(__file__).resolve().parents[3]
    ledger = quota.activate(root)
    require(
        ledger.task == "0054" and ledger.entries == file_plan(), "Global32MiB ledger"
    )
    require(
        not (root / "pilot/activation.json").exists(), "One operational session only"
    )
    manifest = source_manifest(repo)
    receipts = [json.loads(p.read_text()) for p in root.glob("suite-*/observer.json")]
    require(
        any(r["qualified"] and r["source_manifest"] == manifest for r in receipts),
        "Full final-source generated qualification",
    )
    spec = json.loads((repo / CONFIG).read_text())
    validate_spec(spec, repo)
    require(
        spec["software_prerequisites_passed"]
        and spec["pilot_scope_authorized"]
        and not spec["full_study_execution_authorized"],
        "Bound conditional grant",
    )
    directory = root / "pilot"
    directory.mkdir(mode=0o700)
    ledger.write_json(
        directory / "prospective.json",
        dict(
            source_manifest=manifest,
            bundle_sha256=v2.fingerprint(manifest),
            case_order=["pca-v1", "compact-autoencoder-v2"],
            payload_access_not_yet_started=True,
        ),
    )
    clocks = Clocks()
    before = clocks.observation()
    monitor = Monitor(*before[:2])
    start = before[1]
    phase_start = start
    last_phase = 0
    process = None
    problem = None
    cleanup = None
    peak = own_rss()
    latest = None
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                str(repo / "scripts/development_hdf_consumer_pilot.py"),
                "--pilot-subject",
                "--root",
                str(root),
            ],
            cwd=repo,
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={
                **os.environ,
                **spec["thread_environment"],
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )
        while process.poll() is None:
            service, now, _ = clocks.observation()
            monitor.observe(service, now)
            require(now - start <= 178_000_000_000, "Pilot180s cleanup reserve")
            peak = max(peak, own_rss())
            require(peak <= v2.OUTER_RSS, "Pilot outer48MiB")
            h = v2.read_heartbeat(directory / "heartbeat.bin")
            if h:
                latest = h
                phase = h[1] >> 32
                if phase != last_phase:
                    phase_start, last_phase = now, phase
                cap = {1: 45, 2: 30, 3: 30, 4: 45, 5: 30}[phase]
                require(now - phase_start <= cap * 1_000_000_000, "Pilot phase ceiling")
                require(
                    now - h[2] <= 2_000_000_000, "Pilot reporting/custody heartbeat2s"
                )
                require(
                    h[3] <= v2.INNER_RSS and h[4] <= 64 * 1024**2 and h[5] <= 1024**3,
                    "Pilot role RSS",
                )
                require(
                    peak + h[6] <= 512 * 1024**2 and peak + h[6] <= 1216 * 1024**2,
                    "Pilot summed resident charge",
                )
            else:
                require(now - start <= 10_000_000_000, "Pilot subject startup10s")
            time.sleep(0.005)
        process.wait()
    except Exception as exc:
        problem = (type(exc).__name__ + ": " + str(exc))[:900]
    finally:
        if process is not None:
            cleanup = v2.tree_cleanup(
                process,
                clocks,
                min(start + 180_000_000_000, clocks.continuous() + 2_000_000_000),
            )
        after = clocks.observation()
    path = directory / "subject.json"
    try:
        subject = json.loads(path.read_text()) if path.exists() else None
    except (OSError, ValueError):
        subject = None
    receipt = dict(
        qualified=bool(
            not problem
            and subject
            and subject["qualified"]
            and cleanup
            and cleanup["subject_reaped"]
            and cleanup["owned_group_absent"]
            and not cleanup["forced"]
            and cleanup["exitcode"] == 0
        ),
        problem=problem,
        subject=subject,
        cleanup=cleanup,
        source_manifest=manifest,
        bundle_sha256=v2.fingerprint(manifest),
        subject_service_bracket_ns=[before[0], after[0]],
        subject_continuous_bracket_ns=[before[1], after[1]],
        subject_lifetime_ns=after[1] - before[1],
        observer_receipt_outside_subject=True,
        observer_overhead_reserve_ns=2_000_000_000,
        outer_peak_RSS_bytes=peak,
        maximum_monitor_gap_ns=monitor.maximum_gap,
        last_heartbeat=list(latest[1:]) if latest else None,
        storage=ledger.inventory(),
    )
    try:
        ledger.write_json(directory / "observer.json", receipt)
    except (OSError, quota.QuotaError) as exc:
        receipt["qualified"] = False
        receipt["receipt_error"] = str(exc)[:800]
        try:
            ledger.write_bytes(
                directory / "observer-emergency.txt", b"RECEIPT_FAILURE_AFTER_CLEANUP\n"
            )
        except (OSError, quota.QuotaError):
            pass
    require(
        clocks.continuous() - start <= 180_000_000_000,
        "Whole pilot including observer receipt",
    )
    return receipt


def own_tracker_rss():
    """Only this subject's multiprocessing tracker PID; no process inventory."""
    import ctypes
    import sys
    from multiprocessing import resource_tracker

    pid = resource_tracker._resource_tracker._pid
    if pid is None:
        return 0
    if sys.platform == "darwin":
        # Darwin proc_taskinfo: six uint64 followed by twelve int32,96B.
        library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        query = library.proc_pidinfo
        query.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        query.restype = ctypes.c_int
        buffer = (ctypes.c_uint64 * 12)()
        require(
            query(pid, 4, 0, ctypes.byref(buffer), 96) == 96,
            "Own tracker RSS observation",
        )
        rss = int(buffer[1])
    else:
        import resource

        fields = (Path("/proc") / str(pid) / "statm").read_text().split()
        rss = int(fields[1]) * os.sysconf("SC_PAGE_SIZE")
        del resource
    require(0 < rss <= 16 * 1024**2, "Own tracker16MiB allowance within inner80MiB")
    return rss


def validate_spec(spec, repo):
    """Closed curated expectations, never recursive byte_pins/payload traversal."""
    method = json.loads(
        (
            repo / "configs/benchmarks/development_targeted_raw_decision_v1.json"
        ).read_text()
    )
    require(
        spec["task"] == "0054"
        and spec["pilot_scope_authorized"]
        and not spec["full_study_execution_authorized"],
        "Task0054 scope",
    )
    for key in (
        "models",
        "membership",
        "golden",
        "raw",
        "cache",
        "runtime",
        "thread_environment",
    ):
        require(spec[key] == method[key], "Original method identity:" + key)
    expected = {
        role: (method[role]["path"], method[role]["file_sha256"])
        for role in ("raw", "membership", "golden")
    }
    for role, path in method["lineage"].items():
        if role != "dev_scientific_sha256":
            expected[role] = (path, method["byte_pins"][path])
    path = method["transform_config"]
    expected["transform"] = (path, method["byte_pins"][path])
    for entry in method["models"]:
        for role, key in (
            ("model", "model"),
            ("config", "config"),
            ("calibration", "results"),
        ):
            expected[entry["name"] + ":" + role] = (
                entry[key + "_path"],
                entry[key + "_file_sha256"],
            )
    actual = {e["role"]: (e["path"], e["sha256"]) for e in spec["allowed_files"]}
    require(
        len(actual) == len(spec["allowed_files"]) == 17 and actual == expected,
        "Exact expanded17-source allowlist",
    )
    require(
        all(type(e["bytes"]) is int and e["bytes"] > 0 for e in spec["allowed_files"]),
        "Finite source sizes",
    )
    for x in spec["reused_source_manifest"]:
        blob = (repo / x["path"]).read_bytes()
        require(
            len(blob) == x["size_bytes"]
            and hashlib.sha256(blob).hexdigest() == x["sha256"],
            "Frozen reused code",
        )
    require(
        spec["file_ledger"] == file_plan()
        and spec["limits"]["storage_bytes"] == CAP
        and spec["limits"]["reserved_bytes"] == sum(file_plan().values()),
        "Closed diagnostic ledger",
    )
    require(
        [c["id"] for c in spec["case_order"]] == ["pca-v1", "compact-autoencoder-v2"]
        and all(
            c["offers"] == 64 and c["rate_hz"] == 500 and c["horizon_ns"] == 128000000
            for c in spec["case_order"]
        ),
        "Only two64/500 cases",
    )
