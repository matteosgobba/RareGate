"""Closed Task0044 identity, byte allowlist and software admission contract."""

import json
from pathlib import Path

from raregate.simulation.protocol import (
    dependencies as package_dependencies,
)
from raregate.simulation.protocol import (
    digest,
    durable_json,
    file_hash,
    read,
    require,
)

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "configs/simulation/joint_service_replay_v1.json"
PROMPT = "docs/prompts/0044-deterministic-joint-service-replay.md"
STATUS = "software_accepted_synthetic_joint_service_replay"
PARENT_STATUS = "parent_accepted_synthetic_joint_service_replay"
VALIDATION = "data/task0044-validation"
NAMESPACE = "results/benchmarks/task0044-joint-service-replay"
CANDIDATES = ("pca-v1", "compact-autoencoder-v2")
POLICIES = ((1, 0), *((b, t) for b in (8, 32, 128) for t in (1000000, 10000000)))
EXPECTED_DIGEST = "44428eff20b324af3fb5ceae21b680a0e96d1e70f0871bba778f07e79fd447ea"
PINS = {
    "results/tables/final/task0043-development-raw-decision-summary.json": "3baa1cc3c04d4b830912a7d7d06d535f23fe85952ed61ee4b63070e973d9a01b",
    "results/tables/final/task0043-development-raw-decision-cells.csv": "467583e24cb3f07303208c5e08a7f609da9a0494607bf4b67019e7547756436e",
    "configs/benchmarks/development_raw_decision_v2.json": "cb10a1de73b14f570f6e3490243baa1e08b165c99dede094ff0fd38cb67d82ab",
    "docs/prompts/0043-development-raw-decision-campaign-v2.md": "1a39bc50e8d7bea3ebfbe9f8c0dae9cfab272a86e48cf19760487127a355364f",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/workflow.json": "2259f76f4f7bd27dab3a2bf803bc4b0bf354e05d42ef69129dab6832b25694f9",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/parent-acceptance.json": "96b5becdfb04c92fb4fb79b59a9e6cd671aa5fedb2b04e81e8a787665c746c97",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/plan.json": "283f66813f7c6375a032c643f4436e8db30b61ceebe60ee795f0ab692eeb6810",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition1/receipt.json": "71cd30038701ba0a92aa7ee12fff4434809821d5aa78c2e44560f9c42d4f39b7",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition1/aggregate.json": "279c086dab4f48de5a011edba62adfe5f14c3b501d2ed9ca46a17b305757fe94",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition1/timings.jsonl": "59591523c9938015539ee90177ed438b041628bfa4c55e93e4141fd81f670cdc",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition1/timer.json": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition2/receipt.json": "91c642ed45af2c1774df4713949b79f6840988ecf7616e27755ebd98641a7878",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition2/aggregate.json": "647015ca0d5bcc06b1d24800d687491e6abb379e2b3c9dcd9e7f81d98bab97f2",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition2/timings.jsonl": "280134c291899aebbcb50eec91c712984e9498ca964ff8a96a1224d9f6be3957",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition2/timer.json": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition3/receipt.json": "91e402a9b4bc8b86ebfe3195ee7353e412d491b7a9ab4303b590d4d6cd67e2ad",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition3/aggregate.json": "025b8c523b2da24f58736203f8caa418d26d3f9564767f4d3ab7b14fc8e7ffce",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition3/timings.jsonl": "025204e86852d61083fefbbf97177d536cbea36beaf496680194ec4a4e4863c4",
    "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/repetition3/timer.json": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
}
LIMITS = {
    "prerequisite_seconds": 30,
    "simulation_seconds": 120,
    "reporting_seconds": 60,
    "finalization_seconds": 15,
    "whole_seconds": 240,
    "cleanup_seconds": 2,
    "worker_RSS_bytes": 1073741824,
    "native_reserved_bytes": 536870912,
    "controller_RSS_bytes": 134217728,
    "guard_journal_bytes": 67108864,
    "worker_log_bytes": 1048576,
    "owned_storage_bytes": 134217728,
    "retained_trace_bytes": 16777216,
    "max_latency_entries_per_scenario": 5000,
    "source_bundle_bytes": 8388608,
    "retained_service_vectors_bytes": 1048576,
}
SOURCE_DIRECTORY = "results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e"


def safe(root, relative, *, maximum=8 * 2**20):
    require(
        type(relative) is str
        and relative
        and not Path(relative).is_absolute()
        and all(v not in ("", ".", "..") for v in relative.split("/"))
        and str(Path(relative)) == relative,
        "Unsafe relative path",
    )
    path = Path(root).absolute()
    require(path.resolve() == path and not path.is_symlink(), "Symlink root ancestry")
    for part in Path(relative).parts:
        path /= part
        require(not path.is_symlink(), "Symlink path")
    require(path.is_file() and path.stat().st_size <= maximum, "Missing/oversized file")
    return path


def load_config(root=ROOT):
    value = json.loads(safe(root, CONFIG).read_text())
    require(
        digest(value) == EXPECTED_DIGEST, "Fixed Task0044 config/matrix/pins/limits"
    )
    return value


def source_map(root=ROOT):
    root = Path(root)
    names = {
        v
        for folder in ("src", "scripts", "tests")
        for v in (root / folder).rglob("*.py")
    }
    names.update(root / v for v in (CONFIG, PROMPT, "pyproject.toml"))
    return {
        str(v.relative_to(root)): file_hash(safe(root, str(v.relative_to(root))))
        for v in sorted(names)
    }


def identity(root=ROOT):
    return dict(
        task="0044",
        kind="deterministic_joint_service_replay",
        validation_owner="0044",
        config_sha256=file_hash(safe(root, CONFIG)),
        prompt_sha256=file_hash(safe(root, PROMPT)),
    )


def matrix():
    rows = []
    for mode in ("periodic", "poisson"):
        for rate in (500, 2500, 5000):
            for seed in (41, 42, 43):
                for candidate in CANDIDATES:
                    for b, t in POLICIES:
                        for repetition in (1, 2, 3):
                            for assignment in ("cyclic", "constant"):
                                rows.append(
                                    (
                                        mode,
                                        rate,
                                        seed,
                                        candidate,
                                        b,
                                        t,
                                        repetition,
                                        assignment,
                                    )
                                )
    rows.extend(
        (*r[:-1], a)
        for r in tuple(rows)
        if r[0] == "poisson" and r[1] == 2500 and r[-1] == "cyclic"
        for a in ("reverse", "rotation10")
    )
    require(len(rows) == len(set(rows)) == 1764, "Fixed unique scenario keys")
    return tuple(rows)


def emit(directory, checks, native):
    directory = Path(directory)
    value = dict(
        schema_version=1,
        status=STATUS,
        identity=identity(),
        source_map=source_map(),
        dependencies=dependencies(),
        checks=checks,
        bootstrap_workflow_sha256=file_hash(native),
        bootstrap_workflow=str(Path(native).relative_to(ROOT)),
        execution_authorized=False,
    )
    path = directory / "software-acceptance.json"
    durable_json(path, value, exclusive=True)
    return path


def verify_acceptance(path):
    path = Path(path).absolute()
    require(
        path.parent.parent == ROOT / VALIDATION
        and path.name == "software-acceptance.json",
        "Task0044 validation namespace",
    )
    safe(ROOT, str(path.relative_to(ROOT)))
    v = read(path)
    require(
        set(v)
        == set(
            (
                "schema_version status identity source_map dependencies checks bootstrap_workflow_sha256 bootstrap_workflow execution_authorized"
            ).split()
        ),
        "Authoritative software record schema",
    )
    require(
        v["schema_version"] == 1
        and type(v["schema_version"]) is int
        and v["status"] == STATUS
        and v["execution_authorized"] is False
        and v["identity"] == identity()
        and v["source_map"] == source_map()
        and v["dependencies"] == dependencies(),
        "Current Task0044 software acceptance",
    )
    require(
        set(v["checks"])
        == {
            "focused",
            "full",
            "portable",
            "lint",
            "format",
            "dependencies",
            "native_synthetic",
        },
        "Complete checks",
    )
    for c in v["checks"].values():
        require(type(c["exit_code"]) is int and c["exit_code"] == 0, "Passed check")
        log = safe(ROOT, c["log"])
        require(
            log.parent == path.parent and file_hash(log) == c["log_sha256"],
            "Owned check log/hash",
        )
    native = safe(ROOT, v["bootstrap_workflow"])
    require(
        native.is_relative_to(path.parent)
        and file_hash(native) == v["bootstrap_workflow_sha256"],
        "Owned native bootstrap",
    )
    w = read(native)
    require(
        w["status"] == PARENT_STATUS
        and w["fixture_only"] is True
        and w["sleep_assertion"]["released"] is True
        and w["source_map"] == v["source_map"]
        and w["dependencies"] == v["dependencies"],
        "Generated native lifecycle identity",
    )
    verify_lifecycle(native)
    return v


def dependencies():
    import importlib.metadata

    v = package_dependencies()
    bound = {}
    for name in ("numpy", "matplotlib", "pytest", "ruff"):
        distribution = importlib.metadata.distribution(name)
        for entry in distribution.files:
            if str(entry).endswith((".so", ".dylib", "METADATA", "RECORD")):
                path = Path(distribution.locate_file(entry))
                if path.is_file():
                    bound[str(path)] = file_hash(path)
    v["installed_metadata_native_sha256"] = bound
    return v


def verify_lifecycle(path):
    """Outer verification of bound native evidence, without another simulation."""
    path = Path(path)
    w = read(path)
    require(
        w["status"] == PARENT_STATUS
        and w["fixture_only"] is True
        and w["identity"] == identity()
        and w["source_map"] == source_map()
        and w["dependencies"] == dependencies()
        and w["sleep_assertion"]["released"] is True
        and w["sleep_assertion"]["owned_assertion_absent"] is True
        and w["sleep_assertion"]["lifecycle"]["reaped"] is True
        and w["overshoot_seconds"] == 0,
        "Native generated current-source lifecycle",
    )
    require(
        [r["phase"] for r in w["phases"]] == ["simulation", "reporting"],
        "Two native fixture workers",
    )
    require(
        w["counters"]["scenarios_started"]
        == w["counters"]["scenarios_completed"]
        == 1764
        and w["counters"]["event_presentations_started"]
        == w["counters"]["event_presentations_completed"]
        == 8820000,
        "Native generated complete coverage",
    )
    for r in w["phases"]:
        dispatch = r["dispatch"]
        require(
            type(dispatch["returncode"]) is int
            and dispatch["returncode"] == 0
            and dispatch["child_reaped"] is True
            and dispatch["parent_confirms_normal_exit"] is True
            and dispatch["within_deadline"] is True
            and dispatch["parent_error"] is None
            and dispatch["overshoot_seconds"] == 0,
            "Outer native normal exits/reaping",
        )
        directory = path.parent / r["phase"]
        receipt = safe(ROOT, str((directory / "receipt.json").relative_to(ROOT)))
        require(file_hash(receipt) == r["body_sha256"], "Outer native receipt pin")
        body = read(receipt)
        require(
            body["identity"] == identity()
            and body["source_map"] == w["source_map"]
            and body["dependencies"] == w["dependencies"]
            and body["status"] == "body_complete_awaiting_exit"
            and body["phase"] == r["phase"]
            and body["grant_sha256"]
            == file_hash(safe(ROOT, str((directory / "grant.json").relative_to(ROOT))))
            and body["resources"]["latched_error"] is None
            and body["resources"]["owned_thread_alive"] is False,
            "Outer native body/source/resources",
        )
        for n, sha in body["outputs"].items():
            output = safe(ROOT, str((directory / n).relative_to(ROOT)))
            require(
                output.parent == directory and file_hash(output) == sha,
                "Outer native output pin",
            )
    return w


def verify_roundtrip(record):
    record = Path(record).absolute()
    receipt = safe(
        ROOT, str((record.parent / "admission-roundtrip.json").relative_to(ROOT))
    )
    v = read(receipt)
    require(
        v["task"] == "0044"
        and v["status"] == "software_accepted_synthetic_joint_service_replay_roundtrip"
        and v["record_sha256"] == file_hash(record)
        and v["source_map"] == source_map()
        and v["dependencies"] == dependencies()
        and v["execution_authorized"] is False,
        "Final noncircular emitted-record roundtrip",
    )
    workflow = safe(ROOT, v["workflow_path"])
    require(
        workflow.is_relative_to(record.parent)
        and file_hash(workflow) == v["workflow_sha256"],
        "Owned roundtrip workflow pin",
    )
    verify_lifecycle(workflow)
    plan = read(workflow.parent / "plan.json")
    require(
        plan["software_record_sha256"] == file_hash(record)
        and plan["validation_bootstrap"] is False
        and plan["fixture_only"] is True,
        "Actually admitted serialized-record fixture roundtrip",
    )
    return v


HISTORICAL_METADATA_PINS = {
    "configs/benchmarks/development_raw_decision_v1.json": "33660e9977c69bc96706ccfac036b2b8a7d8d2e289bda61854e752bb8f15287b",
    "configs/benchmarks/development_raw_decision_v2.json": "cb10a1de73b14f570f6e3490243baa1e08b165c99dede094ff0fd38cb67d82ab",
    "configs/benchmarks/development_raw_features_v1.json": "64a51e571ebce27bd155856b2ac8104c9e108661861862115b9300049eeabb24",
    "configs/benchmarks/development_raw_measurement_v1.json": "b3373142181d34d0d692073400aed987f5b7574a8903de45568500ee378a8187",
    "configs/benchmarks/prepared_batch_service_v1.json": "87286af8781f7793f6794497b9fb6be32972ffe4409b4cd69ad9fb0facf67d3d",
    "docs/prompts/0039-development-raw-feature-foundation.md": "f4cea291e70b7ae215c0822ee3e451b9eca6135eae448945bdbea669f971e165",
    "docs/prompts/0041-development-raw-decision-measurement.md": "62f251a903629f64fe34cc925e12a416445cfbb5194805956773ac9ebec3555b",
    "docs/prompts/0042-development-decision-admission-repair.md": "1c0fcd5673feae263aeb6494c050aaeac424350ce86159d566e632b9f62836e3",
    "docs/prompts/0043-development-raw-decision-campaign-v2.md": "1a39bc50e8d7bea3ebfbe9f8c0dae9cfab272a86e48cf19760487127a355364f",
    "pyproject.toml": "1c304182e8445c02346509e46005e6bb6be5201aa0d32bfff9866a96d514ec21",
    "results/tables/final/task0039-development-raw-feature-summary.json": "9fee8aac1ff087be14fe8a2990f038d8518be13c8ce086fb698c1e4624d9e352",
    "results/tables/final/task0040-development-raw-feature-summary.json": "119ca5a7bb8fb08ea712263fb6b23e3694f623c04e6b59ecd786d2468189ee6e",
    "results/tables/final/task0042-development-decision-admission-summary.json": "0df1e62149c915b824840d5bc7f48badb57eb30c05688e77d14c0caa965b082f",
}
