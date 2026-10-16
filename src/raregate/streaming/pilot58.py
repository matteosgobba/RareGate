"""Task0058 thin AE-only plan over the existing session and external observers."""

import hashlib
import json
from dataclasses import asdict

from . import pilot54, quota, session57, startup55
from . import validation_v2 as v2
from .ae_context import AE_PLAN, GeneratedSession58, PilotContext58
from .pilot_context import CANDIDATES, digest
from .protocol import require
from .resources import POLICY

TASK = "0058"
CONFIG = "configs/streaming/development_ae_hdf_pilot_v1.json"
SCRIPT = "scripts/development_ae_hdf_pilot.py"
ROOT = "data/task0058-validation/ae-pilot-v1"
SUBJECT_CAP = 156_000_000_000
CLEANUP_BY = 158_000_000_000
GROUP_CAP = TOTAL_CAP = 160_000_000_000  # Prospectively ONE group, no later extension.
EXPECTED_CHECKS = 16
BOOTSTRAPS = ()
write_attempt = session57.write_attempt
SESSIONS = session57.SESSIONS + ("ae-only",)


def case_files(prefix):
    files = {
        f"{prefix}/fixture-ring.shm": 12288,
        f"{prefix}/events.bin": 64 * 512,
        f"{prefix}/batches.bin": 64 * 512,
        f"{prefix}/outputs.bin": 64 * 12,
        f"{prefix}/producer-samples.bin": 768 * 64,
        f"{prefix}/consumer-samples.bin": 4096 * 64,
        f"{prefix}/consumer-audit.bin": 65536,
        f"{prefix}/consumer-final.json": 65536,
    }
    files.update(
        {
            f"{prefix}/{role}-phases.bin": 32 * 512
            for role in ("producer", "consumer", "supervisor")
        }
    )
    return files


def file_plan():
    # Only the one new group and actual Task0058 paths, no old task allowance.
    files = {
        k: v
        for k, v in v2.file_plan().items()
        if k.startswith("suite-1/")
        and not (
            k.endswith("counter-preflight.json")
            and "failed_publication_cleanup" not in k
        )
    }
    files.update(
        {
            "ledger.json": 65536,
            "owner.json": 2048,
            "historical.json": 32768,
            "bootstrap.json": 786432,
            "sources-1.json": 1048576,
            "checks-1.txt": 262144,
            "checks-2.txt": 262144,
            "unit-evidence.json": 65536,
            "delivery-summary.json": 1048576,
            "delivery-cases.csv": 65536,
            "static-receipt.json": 32768,
            "curated-summary-copy.reserved": 1048576,
            "curated-csv-copy.reserved": 65536,
            "curated-text-copy.reserved": 524288,
            "suite-1/subject.json": 65536,
            "suite-1/subject-emergency.json": 32768,
            "suite-1/observer.json": 16384,
            "suite-1/tracker.bin": 65536,
            "suite-1/attempts.bin": 16384,
        }
    )
    # Pure file regressions have distinct slots for two test executions; no native starts.
    for execution in (1, 2):
        for index in range(20):
            d = f"unit-{execution}-{index}"
            files[f"{d}/journal.bin"] = 65536
            files[f"{d}/case.bin"] = 1024
    for index, (name, n, _) in enumerate(v2.CASES, 1):
        if n:
            files[f"suite-1/{index:02d}-{name}/tracker.bin"] = 65536
    for c in CANDIDATES:
        d = f"suite-1/generated/{c}"
        files[f"{d}/fixture-spec.json"] = 32768
        for name, cap in session57.SERIAL_CAPS.items():
            files[f"{d}/serialized/{name}.bin"] = cap
    for name in SESSIONS:
        d = f"suite-1/session-{name}"
        files[f"{d}/tracker.bin"] = 65536
        files[f"{d}/session.json"] = 393216
        files[f"{d}/emergency.json"] = 16384
        plan = (
            AE_PLAN
            if name == "ae-only"
            else (CANDIDATES[:1] if name == "first-failure" else CANDIDATES)
        )
        for c in plan:
            files.update(case_files(d + "/" + c))
            if name == "second-failure" and c == CANDIDATES[1]:
                for suffix in (
                    "producer-samples.bin",
                    "consumer-samples.bin",
                    "consumer-audit.bin",
                    "consumer-final.json",
                ):
                    del files[f"{d}/{c}/{suffix}"]
    files.update(case_files("pilot/" + AE_PLAN[0]))
    files["pilot/" + AE_PLAN[0] + "/result.json"] = 131072
    files.update(
        {
            "pilot/prospective.json": 131072,
            "pilot/activation.json": 4096,
            "pilot/heartbeat.bin": 4096,
            "pilot/custody.bin": 4096,
            "pilot/tracker.bin": 65536,
            "pilot/observer.json": 32768,
            "pilot/observer-emergency.txt": 2048,
            "pilot/subject.json": 131072,
            "pilot/subject-emergency.json": 32768,
            "pilot/emergency.txt": 4096,
        }
    )
    require(
        len(files) <= 512 and sum(files.values()) <= 32 * 1024**2,
        "Whole0058 ledger before native",
    )
    return files


def initialize(root, repo):
    require(
        root == repo / ROOT
        and not root.exists()
        and root.parent.resolve() == root.parent,
        "New canonical0058 root",
    )
    root.mkdir(mode=0o700, parents=True)
    ledger = quota.Ledger(root, file_plan(), task=TASK)
    ledger.write_json(
        root / "ledger.json", dict(task=TASK, cap_bytes=32 * 1024**2, files=file_plan())
    )
    ledger.write_json(
        root / "owner.json",
        dict(
            task=TASK,
            candidate_plan=list(AE_PLAN),
            generated_groups=1,
            conditional_P4_sessions=1,
            full_study=False,
        ),
    )
    return quota.activate(root)


def source_paths(repo):
    return sorted(
        set(
            startup55.source_paths(repo)
            + [
                repo / SCRIPT,
                repo / CONFIG,
                repo / "src/raregate/benchmarks/development_raw_adapter.py",
                repo / "src/raregate/benchmarks/development_decision_protocol.py",
                repo / "tests/test_development_ae_hdf_pilot.py",
                repo / "docs/prompts/0058-bounded-ae-hdf-pilot.md",
                repo / "docs/arithmetic-cpu-v2-policy.md",
            ]
        )
    )


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
    old = json.loads(
        (repo / "configs/streaming/development_hdf_consumer_pilot_v2.json").read_text()
    )
    expected = [e for e in old["allowed_files"] if not e["role"].startswith("pca-v1:")]
    require(
        spec["task"] == TASK
        and spec["root"] == ROOT
        and tuple(spec["candidate_plan"]) == AE_PLAN
        and spec["pilot_scope_authorized"] is True
        and spec["full_study_execution_authorized"] is False
        and spec["session_replacement_authorized"] is False,
        "Closed0058 scope",
    )
    require(
        spec["allowed_files"] == expected
        and len(expected) == 14
        and spec["models"] == [e for e in old["models"] if e["name"] in AE_PLAN],
        "Exactly14 unchanged originals, no PCA",
    )
    for k in (
        "membership",
        "golden",
        "raw",
        "lineage_roles",
        "dev_scientific_sha256",
        "cache",
        "runtime",
        "thread_environment",
        "numerical",
        "buffer_derivation",
    ):
        require(spec[k] == old[k], "Unchanged0056 " + k)
    require(
        spec["file_ledger"] == file_plan()
        and spec["resource_policy"] == asdict(POLICY)
        and spec["source_bytes_bound"] == 393216
        and sum(spec["buffer_derivation"].values()) <= 8388608,
        "Original resource guards",
    )
    require(
        spec["generated"]["groups"] == 1
        and spec["generated"]["required_checks"] == 16
        and spec["generated"]["configured_offers"] == 1008,
        "One complete frozen group",
    )
    actual = source_manifest(repo)
    require(
        all(p in actual for p in spec["source_pins"]), "Frozen prospective0058 pins"
    )
    require(
        [x["threshold"] for x in spec["models"][0]["thresholds"]]
        == [
            3.478338537407165,
            4.681070974717348,
            8.324174660133213,
            16.642218868621573,
        ],
        "Original strict AE thresholds",
    )
    return spec


def prepare_group(root, group, repo):
    require(root == repo / ROOT and group == 1, "Only one reserved0058 group")
    ledger = quota.activate(root)
    require(
        ledger.task == TASK and ledger.entries == file_plan(), "Immutable0058 ledger"
    )
    spec = validate_spec(json.loads((repo / CONFIG).read_text()), repo)
    identity = source_manifest(repo)
    directory = root / "suite-1"
    directory.mkdir(mode=0o700)
    texts = {str(p.relative_to(repo)): p.read_text() for p in source_paths(repo)}
    ledger.write_json(
        root / "sources-1.json",
        {
            p: [t[i : i + 32768] for i in range(0, len(t), 32768)]
            for p, t in texts.items()
        },
    )
    ledger.write_json(
        directory / "prospective.json",
        dict(
            task=TASK,
            source_manifest=identity,
            bundle_sha256=digest(identity),
            generated_only=True,
            case_order=spec["generated"]["matrix"],
            reserved_bytes=sum(file_plan().values()),
        ),
    )
    return ledger, directory, identity


def check_qualification(root, repo):
    require(root == repo / ROOT, "0058 qualification root")
    identity = source_manifest(repo)
    receipt = json.loads((root / "suite-1/observer.json").read_text())
    require(
        receipt["qualified"]
        and receipt["source_manifest"] == identity
        and receipt["subject"]["attempted_cases"] == 16
        and receipt["subject"]["source_unchanged"],
        "All16 current0058 expectations",
    )
    return identity


def context(root, repo):
    require(root == repo / ROOT, "Explicit0058 operational root")
    return PilotContext58(str(root), digest(source_manifest(repo)))


def run_integrations(
    root, directory, group, prospective, heartbeat, rows, attempts, clocks
):
    ledger = quota.CURRENT
    for index, name in enumerate(SESSIONS, 13):
        plan = AE_PLAN if name == "ae-only" else CANDIDATES
        attempt = dict(
            index=index,
            kind="sequential_session",
            case=name,
            configured_offers=64 * len(plan),
        )
        write_attempt(
            directory / f"attempt-{index}.json",
            dict(**attempt, bundle_sha256=prospective["bundle_sha256"]),
        )
        attempts.append(attempt)
        path = directory / ("session-" + name)
        path.mkdir(mode=0o700)
        ctx = GeneratedSession58(
            str(root), str(path), prospective["bundle_sha256"], name
        )
        baseline = set(quota.FDS)
        before = clocks.continuous()
        result = pilot54.candidate_session(
            root, path, ctx, heartbeat, save_case_reports=False
        )
        if name == "ae-only":
            js = result["journal_after_close"]
            checks = dict(
                accepted=result["accepted"],
                plan=result["intended_candidates"] == list(AE_PLAN),
                attempted=result["attempted_candidates"] == list(AE_PLAN),
                no_PCA=len(result["candidates"]) == 1
                and result["candidates"][0]["candidate"] == AE_PLAN[0],
                journal=js["opens"] == js["closes"] == 1
                and js["closed"]
                and result["journal_before_close"]["registered"]
                and all(p["registered"] for p in result["journal_checkpoints"]),
            )
        else:
            checks = session57.session_expectations(name, result)
        result.update(
            session_expectations=checks,
            software_checks_passed=all(checks.values()),
            bundle_sha256=prospective["bundle_sha256"],
            operational=False,
            kind="generated_shared_session",
            registered_fds_restored=set(quota.FDS) == baseline,
        )
        result["software_checks_passed"] &= result["registered_fds_restored"]
        ledger.write_json(path / "session.json", result)
        elapsed = clocks.continuous() - before
        require(
            elapsed <= (15 if name == "ae-only" else 20) * 10**9,
            "Inclusive generated session bound",
        )
        rows.append(
            dict(
                case_id=f"g1-session-{name}",
                kind="sequential_session",
                configured_offers=64 * len(plan),
                bundle_sha256=prospective["bundle_sha256"],
                software_checks_passed=result["software_checks_passed"],
                observed_validity="valid" if result["accepted"] else "expected_invalid",
                case_inclusive_ns=elapsed,
            )
        )
        heartbeat({})
        require(result["software_checks_passed"], "0058 shared session expectation")
