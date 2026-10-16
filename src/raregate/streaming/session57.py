"""Task0057 generated-only sequential lifecycle qualification; no P4 entrypoint."""

import json

from . import quota, startup55
from . import validation_v2 as v2
from .pilot_context import CANDIDATES, digest
from .protocol import require

CONFIG = "configs/streaming/development_streaming_session_lifecycle_v1.json"
SCRIPT = "scripts/validate_development_streaming_session.py"
ROOT = "data/task0057-validation/session-lifecycle"
SUBJECT_CAP = 136_000_000_000
CLEANUP_BY = 138_000_000_000
GROUP_CAP = 140_000_000_000
TOTAL_CAP = 280_000_000_000
EXPECTED_CHECKS = 15
BOOTSTRAPS = ()  # RuntimeSession and its policy are unchanged.
SESSIONS = ("normal", "first-failure", "second-failure")
SERIAL_CAPS = dict(
    raw=256,
    membership=56120,
    golden=32896,
    transform=4096,
    dev_configuration=4096,
    dev_manifest=4096,
    split_manifest=2048,
    prepared=1024,
    prepare_receipt=2048,
    acquisition=1024,
    raw_audit=2048,
    model=16384,
    config=1024,
    calibration=2048,
)


def file_plan():
    files = {
        k: v
        for k, v in v2.file_plan().items()
        if not (
            k.endswith("counter-preflight.json")
            and "failed_publication_cleanup" not in k
        )
    }
    files.update(
        {
            "historical.json": 32768,
            "bootstrap.json": 786432,
            "checks.txt": 262144,
            "checks-2.txt": 262144,
            "delivery-summary.json": 1048576,
            "delivery-cases.csv": 65536,
            "curated-summary-copy.reserved": 1048576,
            "curated-csv-copy.reserved": 65536,
            "curated-text-copy.reserved": 262144,
            "regression-before.json": 8192,
            "regression/journal.bin": 65536,
            "regression/other.bin": 64,
            "unit-evidence.json": 32768,
        }
    )
    # Fixed slots for pure ownership/failure tests; evidence is never overwritten.
    for i in range(10):
        files[f"unit-{i}/journal.bin"] = 65536
        files[f"unit-{i}/case.bin"] = 64
    for group in (1, 2):
        prefix = f"suite-{group}"
        files[f"sources-{group}.json"] = 1048576
        files[f"{prefix}/subject.json"] = 65536
        files[f"{prefix}/subject-emergency.json"] = 32768
        files[f"{prefix}/observer.json"] = 16384
        files[f"{prefix}/tracker.bin"] = 65536
        files[f"{prefix}/attempts.bin"] = 16384
        for i, (name, n, _) in enumerate(v2.CASES, 1):
            if n:
                files[f"{prefix}/{i:02d}-{name}/tracker.bin"] = 65536
        for candidate in CANDIDATES:
            d = f"{prefix}/generated/{candidate}"
            files[f"{d}/fixture-spec.json"] = 32768
            for name, cap in SERIAL_CAPS.items():
                files[f"{d}/serialized/{name}.bin"] = cap
        for name in SESSIONS:
            d = f"{prefix}/session-{name}"
            files[f"{d}/tracker.bin"] = 65536
            files[f"{d}/session.json"] = 393216
            files[f"{d}/emergency.json"] = 16384
            candidates = CANDIDATES[:1] if name == "first-failure" else CANDIDATES
            for candidate in candidates:
                c = f"{d}/{candidate}"
                files.update(
                    {
                        f"{c}/fixture-ring.shm": 12288,
                        f"{c}/events.bin": 64 * 512,
                        f"{c}/batches.bin": 64 * 512,
                        f"{c}/outputs.bin": 64 * 12,
                        f"{c}/producer-samples.bin": 768 * 64,
                        f"{c}/consumer-samples.bin": 4096 * 64,
                        f"{c}/consumer-audit.bin": 65536,
                        f"{c}/consumer-final.json": 65536,
                    }
                )
                for role in ("producer", "consumer", "supervisor"):
                    files[f"{c}/{role}-phases.bin"] = 32 * 512
                if name == "second-failure" and candidate == CANDIDATES[1]:
                    for suffix in (
                        "producer-samples.bin",
                        "consumer-samples.bin",
                        "consumer-audit.bin",
                        "consumer-final.json",
                    ):
                        del files[f"{c}/{suffix}"]
    require(
        len(files) <= 512 and sum(files.values()) <= 32 * 1024**2, "Complete0057 ledger"
    )
    return files


def initialize(root, repo):
    require(
        root == repo / ROOT
        and not root.exists()
        and root.parent.resolve() == root.parent,
        "New canonical0057 owned root",
    )
    files = file_plan()
    root.mkdir(mode=0o700, parents=True)
    ledger = quota.Ledger(root, files, task="0057")
    ledger.write_json(
        root / "ledger.json", dict(task="0057", cap_bytes=32 * 1024**2, files=files)
    )
    ledger.write_json(
        root / "owner.json", dict(task="0057", generated_only=True, P4=False)
    )
    return quota.activate(root)


def source_paths(repo):
    paths = startup55.source_paths(repo) + [
        repo / SCRIPT,
        repo / CONFIG,
        repo / "tests/test_development_streaming_session.py",
        repo / "docs/prompts/0057-streaming-session-lifecycle-repair.md",
        repo / "src/raregate/benchmarks/development_raw_adapter.py",
    ]
    return sorted(set(paths))


def source_manifest(repo):
    import hashlib

    return [
        dict(
            path=str(p.relative_to(repo)),
            bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
        )
        for p in source_paths(repo)
        for b in [p.read_bytes()]
    ]


def prepare_group(root, group, repo):
    require(root == repo / ROOT and group in (1, 2), "Two generated0057 groups")
    ledger = quota.activate(root)
    require(
        ledger.task == "0057" and ledger.entries == file_plan(),
        "Immutable whole-task ledger",
    )
    spec = json.loads((repo / CONFIG).read_text())
    identity = source_manifest(repo)
    require(
        spec["task"] == "0057"
        and spec["P4"] is False
        and spec["operational_execution_authorized"] is False
        and spec["file_ledger"] == file_plan(),
        "No operational scope",
    )
    require(all(p in identity for p in spec["source_pins"]), "Prospective source pins")
    if group == 2:
        previous = json.loads((root / "suite-1/observer.json").read_text())
        require(
            not previous["qualified"]
            and identity != previous["source_manifest"]
            and spec.get("correctness_repair_after_group1"),
            "One correctness repair only",
        )
    directory = root / f"suite-{group}"
    directory.mkdir(mode=0o700)
    ledger.write_json(
        root / f"sources-{group}.json",
        {
            str(p.relative_to(repo)): [
                p.read_text()[i : i + 32768]
                for i in range(0, len(p.read_text()), 32768)
            ]
            for p in source_paths(repo)
        },
    )
    ledger.write_json(
        directory / "prospective.json",
        dict(
            task="0057",
            source_manifest=identity,
            bundle_sha256=digest(identity),
            generated_only=True,
            case_order=spec["case_matrix"],
            reserved_bytes=sum(file_plan().values()),
        ),
    )
    return ledger, directory, identity


def write_attempt(path, value):
    import os

    blob = (json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n").encode()
    require(len(blob) <= 1024, "Attempt record bound")
    target = path.parent / "attempts.bin"
    fd = quota.open_file(target, os.O_CREAT | os.O_RDWR)
    try:
        offset = os.fstat(fd).st_size
        require(
            quota.pwrite(fd, blob, offset) == len(blob),
            "Complete prospective attempt write",
        )
    finally:
        quota.close(fd)


def session_expectations(name, result):
    candidates = result["candidates"]
    common = bool(
        not result["cleanup_failures"]
        and result["journal_before_close"]["registered"]
        and result["journal_after_close"]["closed"]
        and result["journal_after_close"]["opens"] == 1
        and result["journal_after_close"]["closes"] == 1
        and all(p["registered"] for p in result["journal_checkpoints"])
        and len({tuple(p["inode"]) for p in result["journal_checkpoints"]}) == 1
        and all(
            r["semaphore_cleanup"]["all_absent"]
            and all(not c.get("leaked") for c in r["children"])
            for r in candidates
        )
    )
    if name == "normal":
        expected = (
            result["accepted"]
            and len(candidates) == 2
            and all(r["software_checks_passed"] for r in candidates)
            and not result["unattempted_candidates"]
        )
    elif name == "first-failure":
        first = candidates[0] if candidates else {}
        final = first.get("real_consumer") or {}
        expected = (
            not result["accepted"]
            and len(candidates) == 1
            and result["unattempted_candidates"] == [CANDIDATES[1]]
            and not first.get("normal", True)
            and "Injected PCA first stream read before return" in json.dumps(final)
            and first["arrival_clock_issued"]
        )
    else:
        second = candidates[1] if len(candidates) == 2 else {}
        tracker = second.get("tracker_resource_observations") or {}
        expected = (
            not result["accepted"]
            and len(candidates) == 2
            and candidates[0]["software_checks_passed"]
            and not second.get("arrival_clock_issued", True)
            and not second.get("real_consumer")
            and all(not c["started"] for c in second.get("children", []))
            and "Injected AE pre-worker tracker publication failure"
            in json.dumps(tracker)
            and "observed" in json.dumps(tracker)
        )
    return dict(ownership_cleanup=common, expected_session_outcome=bool(expected))


def run_integrations(
    root, directory, group, prospective, heartbeat, rows, attempts, clocks
):
    from .pilot54 import candidate_session
    from .session_context import GeneratedSession57

    ledger = quota.CURRENT
    for index, name in enumerate(SESSIONS, 13):
        attempt = dict(
            index=index, kind="sequential_session", case=name, configured_offers=128
        )
        write_attempt(
            directory / f"attempt-{index}.json",
            dict(**attempt, bundle_sha256=prospective["bundle_sha256"]),
        )
        attempts.append(attempt)
        path = directory / ("session-" + name)
        path.mkdir(mode=0o700)
        context = GeneratedSession57(
            str(root), str(path), prospective["bundle_sha256"], name
        )
        before = clocks.continuous()
        baseline = set(quota.FDS)
        result = candidate_session(
            root, path, context, heartbeat, save_case_reports=False
        )
        result["session_expectations"] = session_expectations(name, result)
        result["software_checks_passed"] = all(result["session_expectations"].values())
        result["bundle_sha256"] = prospective["bundle_sha256"]
        result["operational"] = False
        result["kind"] = "generated_shared_sequential_session"
        result["registered_fds_restored"] = set(quota.FDS) == baseline
        result["software_checks_passed"] &= result["registered_fds_restored"]
        ledger.write_json(path / "session.json", result)
        elapsed = clocks.continuous() - before
        require(
            elapsed <= 20_000_000_000, "Whole sequential session20s including report"
        )
        rows.append(
            dict(
                case_id=f"g{group}-session-{name}",
                kind="sequential_session",
                configured_offers=128,
                bundle_sha256=prospective["bundle_sha256"],
                software_checks_passed=result["software_checks_passed"],
                observed_validity="valid" if result["accepted"] else "expected_invalid",
                case_inclusive_ns=elapsed,
            )
        )
        heartbeat({})
        require(
            result["software_checks_passed"],
            "Unexpected shared session expectation failure",
        )
