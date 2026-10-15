"""Task0056 thin explicit scope adapter over the qualified streaming lifecycle."""

import gc
import hashlib
import json
from dataclasses import asdict

from . import pilot54, quota, startup55
from .pilot_context import CANDIDATES, CONFIG56, ROOT56, PilotContext56, digest
from .protocol import require
from .resources import POLICY

CONFIG, ROOT = CONFIG56, ROOT56
SCRIPT = "scripts/development_hdf_consumer_pilot_v2.py"
SUBJECT_CAP = 116_000_000_000
CLEANUP_BY = 118_000_000_000
GROUP_CAP = 120_000_000_000
TOTAL_CAP = 240_000_000_000
EXPECTED_CHECKS = 16


def file_plan():
    files = startup55.file_plan()
    # Unused preflight reservations outside its one injected case are unnecessary.
    files = {
        k: v
        for k, v in files.items()
        if not (
            k.endswith("counter-preflight.json")
            and "failed_publication_cleanup" not in k
        )
    }
    files.update(
        {k: v for k, v in pilot54.file_plan().items() if k.startswith("pilot/")}
    )
    files.update(
        {"historical.json": 32768, "bootstrap.json": 786432, "pilot/tracker.bin": 65536}
    )
    for group in (1, 2):
        for index in (15, 16):
            files[f"suite-{group}/attempt-{index}.json"] = 1024
        for index, name in ((15, "serialized-pca"), (16, "serialized-ae")):
            d = f"suite-{group}/{index:02d}-{name}"
            for key, cap in pilot54.file_plan().items():
                prefix = "pilot/pca-v1/"
                if key.startswith(prefix):
                    files[d + "/" + key[len(prefix) :]] = cap
            files[d + "/tracker.bin"] = 65536
            files[d + "/fixture-spec.json"] = 32768
            files[d + "/emergency.txt"] = 2048
            caps = dict(
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
            for name, cap in caps.items():
                files[f"{d}/serialized/{name}.bin"] = cap
    require(
        len(files) <= 512 and sum(files.values()) <= 32 * 1024**2, "Complete0056 ledger"
    )
    return files


def initialize(root, repo):
    require(
        root == repo / ROOT
        and not root.exists()
        and root.parent.resolve() == root.parent,
        "New0056 canonical root",
    )
    files = file_plan()
    root.mkdir(mode=0o700, parents=True)
    ledger = quota.Ledger(root, files, task="0056")
    ledger.write_json(
        root / "ledger.json", dict(task="0056", cap_bytes=32 * 1024**2, files=files)
    )
    ledger.write_json(
        root / "owner.json",
        dict(task="0056", single_new_session=True, old0054_consumed=True),
    )
    return quota.activate(root)


def source_paths(repo):
    old = json.loads((repo / pilot54.CONFIG).read_text())
    paths = list(startup55.source_paths(repo))
    paths += [repo / x["path"] for x in old["reused_source_manifest"]]
    paths += [
        repo / SCRIPT,
        repo / CONFIG,
        repo / "docs/prompts/0056-fresh-bounded-hdf-pilot.md",
        repo / "tests/test_development_hdf_pilot_v2.py",
    ]
    return sorted(set(paths))


def source_manifest(repo):
    return [
        dict(
            path=str(p.relative_to(repo)),
            bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
        )
        for p in source_paths(repo)
        for b in [p.read_bytes()]
    ]


def validate_spec(spec, repo):
    old = json.loads((repo / pilot54.CONFIG).read_text())
    require(
        spec["task"] == "0056"
        and spec["pilot_scope_authorized"] is True
        and spec["full_study_execution_authorized"] is False
        and spec["session_replacement_authorized"] is False,
        "Fresh narrow0056 scope",
    )
    for key in (
        "allowed_files",
        "models",
        "membership",
        "golden",
        "raw",
        "lineage_roles",
        "dev_scientific_sha256",
        "cache",
        "runtime",
        "thread_environment",
        "case_order",
        "maxima",
        "numerical",
    ):
        require(spec[key] == old[key], "Unchanged closed original " + key)
    require(
        spec["resource_policy"] == asdict(POLICY)
        and spec["file_ledger"] == file_plan(),
        "0056 policy and ledger",
    )
    require(
        spec["limits"]["storage_bytes"] == 32 * 1024**2
        and spec["limits"]["reserved_bytes"] == sum(file_plan().values()),
        "Complete budget",
    )
    require(
        spec["source_bytes_bound"] == 393216
        and sum(spec["buffer_derivation"].values()) <= 8 * 1024**2,
        "Visible buffer bound",
    )
    actual = source_manifest(repo)
    for pin in spec["code_manifest"]:
        require(pin in actual, "Current source pin")
    require(len(spec["allowed_files"]) == 17, "Exactly17 originals")
    return spec


def prepare_group(root, group, repo):
    require(root == repo / ROOT and group in (1, 2), "Two0056 groups")
    ledger = quota.activate(root)
    require(ledger.task == "0056" and ledger.entries == file_plan(), "Whole0056 ledger")
    spec = validate_spec(json.loads((repo / CONFIG).read_text()), repo)
    identity = source_manifest(repo)
    if group == 2:
        previous = json.loads((root / "suite-1/observer.json").read_text())
        require(
            identity != previous["source_manifest"]
            and spec.get("correctness_repair_after_group1"),
            "Only documented correctness repair",
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
            task="0056",
            source_manifest=identity,
            bundle_sha256=digest(identity),
            generated_only=True,
            case_order=spec["generated"]["matrix"],
            reserved_bytes=sum(ledger.entries.values()),
        ),
    )
    return ledger, directory, identity


def check_qualification(root, repo):
    identity = source_manifest(repo)
    receipts = [json.loads(p.read_text()) for p in root.glob("suite-*/observer.json")]
    require(
        any(
            r["qualified"]
            and r["source_manifest"] == identity
            and r["subject"]["attempted_cases"] == 16
            for r in receipts
        ),
        "All16 final-source checks before P4",
    )
    return identity


def context(root, repo):
    require(root == repo / ROOT, "Fixed0056 root")
    return PilotContext56(str(root), digest(source_manifest(repo)))


def run_integrations(
    root, directory, group, prospective, heartbeat, rows, attempts, clocks
):
    from . import validation_v2 as v2
    from .fixture import run_scoped_core
    from .pilot_context import FixtureContext56

    ledger = quota.CURRENT
    for index, name, candidate in (
        (15, "serialized-pca", CANDIDATES[0]),
        (16, "serialized-ae", CANDIDATES[1]),
    ):
        before = clocks.continuous()
        attempt = dict(
            index=index, kind="serialized_fixture", case=name, configured_offers=64
        )
        ledger.write_json(
            directory / f"attempt-{index}.json",
            dict(**attempt, bundle_sha256=prospective["bundle_sha256"]),
        )
        attempts.append(attempt)
        path = directory / f"{index:02d}-{name}"
        ctx = FixtureContext56(
            str(root), str(path), prospective["bundle_sha256"], candidate
        )
        journal = startup55.Journal(path / "tracker.bin")
        prior = set(quota.FDS)
        try:
            report = v2.compact_report(
                run_scoped_core(
                    path,
                    candidate,
                    quota_root=str(root),
                    heartbeat=heartbeat,
                    context=ctx,
                    resource_publish=journal.write,
                )
            )
        finally:
            journal.close()
            errors = quota.emergency_release(prior, path)
        gc.collect()
        report["semaphore_cleanup"] = v2.semaphore_absence(
            report["synchronization_inventory"]["owned_names"]
        )
        finalpath = path / "consumer-final.json"
        final = json.loads(finalpath.read_text()) if finalpath.exists() else None
        passed = bool(
            report["software_checks_passed"]
            and final
            and final["valid"]
            and report["semaphore_cleanup"]["all_absent"]
            and not errors
        )
        report.update(
            kind="serialized_fixture",
            case_id=f"g{group}-{index:02d}-{name}",
            bundle_sha256=prospective["bundle_sha256"],
            real_consumer=final,
            software_checks_passed=passed,
            operational=False,
        )
        ledger.write_json(path / "result.json", report)
        elapsed = clocks.continuous() - before
        require(elapsed <= 15_000_000_000, "Serialized15s including cleanup/report")
        row = v2.row_from_report(
            report["case_id"], prospective["bundle_sha256"], report, elapsed
        )
        row["kind"] = "serialized_fixture"
        rows.append(row)
        heartbeat(report["own_process_peak_RSS_bytes"])
        require(passed, "Serialized actual-loader integration failed")
