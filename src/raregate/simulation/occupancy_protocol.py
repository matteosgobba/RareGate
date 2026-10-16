"""Closed Task0046 identity, byte allowlist and software admission contract."""

import json
import math
from pathlib import Path

from raregate.simulation.protocol import (
    dependencies as package_dependencies,
)
from raregate.simulation.protocol import (
    digest,
    durable_json,
    file_hash,
    require,
)

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "configs/simulation/occupancy_service_replay_v1.json"
PROMPT = "docs/prompts/0046-occupancy-aware-service-replay.md"
STATUS = "software_accepted_synthetic_occupancy_service_replay"
PARENT_STATUS = "parent_accepted_synthetic_occupancy_service_replay"
VALIDATION = "data/task0046-validation"
NAMESPACE = "results/simulations/task0046-occupancy-service-replay"
CANDIDATES = ("pca-v1", "compact-autoencoder-v2")
POLICIES = ((1, 0), *((b, t) for b in (8, 32, 128) for t in (1000000, 10000000)))
EXPECTED_DIGEST = "df7207608ccb9663e835d2338ab651655875c653403e73207fb944a1eb2fb387"
SOURCE_MANIFEST = {
    "results/tables/final/task0045-natural-partial-raw-decision-summary.json": {
        "sha256": "76a4cf7bceaa89bb5a71e9c11c324a7b52199867838739b0427783c4c402ea2b",
        "bytes": 148228,
    },
    "results/tables/final/task0045-natural-partial-raw-decision-cells.csv": {
        "sha256": "5768aed492722f55c4c6bfc37aed20e21f32b500c2e03291e6719d73963ddd2c",
        "bytes": 39422,
    },
    "results/tables/final/task0045-natural-partial-raw-decision-pairs.csv": {
        "sha256": "9a62167b1ed730eca9b629c8cf007f172d5a4dba6b1d1eb5cc595352783f34b3",
        "bytes": 244801,
    },
    "configs/benchmarks/development_partial_raw_decision_v1.json": {
        "sha256": "24d74acc9139fc5251dbeb50c4737b32086f3554a21c1eba1aba96daf8de53a2",
        "bytes": 25472,
    },
    "docs/prompts/0045-natural-partial-raw-decision-measurement.md": {
        "sha256": "fc0bb1bdd7d6301bc3aa581fc06c508a3d4e88e7d494ebf2cc549a0f136d22fe",
        "bytes": 22530,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/attempt.json": {
        "sha256": "17e1452cfe5a8b389a8692d3b39a0867d2e8f7654abc5de6e8dbc32d0c3da035",
        "bytes": 302,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/plan.json": {
        "sha256": "f6b6caafd37001a2f039cdc02112477fe625c1e120eb30e78883be89e128611b",
        "bytes": 50474,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/workflow.json": {
        "sha256": "6b3795b532cf2ad07e1d3bad0c48684e4ef7d40c81af2adbea732f3deb65bd68",
        "bytes": 70008,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/parent-acceptance.json": {
        "sha256": "b71e4535e6a31891ca43757f6e53c32a232f16b4ad1640f9e4b8e09cd797dc96",
        "bytes": 911,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/reporting/receipt.json": {
        "sha256": "9b49c5e08eb54aed4781d8276e0e8dad81a868e4bf8110d26e6d503ea7aa9717",
        "bytes": 39985,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/reporting/summary.json": {
        "sha256": "3b2dea24614ae9b9af71334a2b3e8b8dfb9b354e00489d9ea1cef90da2aa1433",
        "bytes": 129101,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition1/receipt.json": {
        "sha256": "bed74af1e9a5fc14ce456ce6ed49f601d55958af808cc33c65dd24652ef992ef",
        "bytes": 49531,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition1/aggregate.json": {
        "sha256": "ab94180dfb8fe602809016f28ca3e1cab96034b155fa6a41116b7f23f7b7c780",
        "bytes": 1225238,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition1/timings.jsonl": {
        "sha256": "e5556039f50c9c0ba530b603b1b9b4d3a790d165aad825c4ebee890ef46cd7de",
        "bytes": 630901,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition1/timer.json": {
        "sha256": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
        "bytes": 199,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition2/receipt.json": {
        "sha256": "7fb9b6869ebfc1f2fafc31acc278eaa256e2eab5ec65adf7fd9c3ffef1fe92c5",
        "bytes": 49533,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition2/aggregate.json": {
        "sha256": "e05c916e510a68b6876edd876b3b9af19653dc9878337f51a6dcb329ac891220",
        "bytes": 1225521,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition2/timings.jsonl": {
        "sha256": "ec54a07f7bd8646e877296e7b78e5a6415bae54bd51f2c8fd3da2a89bb2e7e6c",
        "bytes": 631205,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition2/timer.json": {
        "sha256": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
        "bytes": 199,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition3/receipt.json": {
        "sha256": "ef5dc3bcefe2da3abec0288e070b9275001c3b2e4a72e8127528f9a0e7a9cbb9",
        "bytes": 49533,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition3/aggregate.json": {
        "sha256": "41c43e27c7ed3e3bc5667c8aff651ccaab02b11df99be1bffa6aedb338807a84",
        "bytes": 1225390,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition3/timings.jsonl": {
        "sha256": "f447a262fc13a62653654f90b0bdaf0b36b7a6c5b654073a557a618ad1508a26",
        "bytes": 631046,
    },
    "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08/repetition3/timer.json": {
        "sha256": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
        "bytes": 199,
    },
}
PINS = {n: v["sha256"] for n, v in SOURCE_MANIFEST.items()}
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
SOURCE_DIRECTORY = "results/benchmarks/task0045-natural-partial-raw-decisions/1872bdaa920f49598ec8eafcf4ea3c08"


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


def read(path):
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, "Duplicate JSON key")
            result[k] = v
        return result

    value = json.loads(
        Path(path).read_text(),
        object_pairs_hook=pairs,
        parse_constant=lambda x: require(False, "Nonfinite JSON"),
    )

    def finite(x):
        if isinstance(x, dict):
            for y in x.values():
                finite(y)
        elif isinstance(x, list):
            for y in x:
                finite(y)
        elif type(x) is float:
            require(math.isfinite(x), "Finite serialized record")

    finite(value)
    return value


def load_config(root=ROOT):
    value = read(safe(root, CONFIG))
    require(
        digest(value) == EXPECTED_DIGEST, "Fixed Task0046 config/matrix/pins/limits"
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
        task="0046",
        kind="deterministic_occupancy_service_replay",
        validation_owner="0046",
        scope="closed_Task0045_timing_metadata_synthetic_FIFO",
        assignment_contract_sha256=digest(
            dict(
                anchors=ANCHORS,
                mappings=MAPPINGS,
                billings=BILLINGS,
                cursor="independent_anchor_zero_mod20_dispatch_only",
            )
        ),
        config_sha256=file_hash(safe(root, CONFIG)),
        prompt_sha256=file_hash(safe(root, PROMPT)),
    )


ANCHORS = {1: (1,), 8: (1, 2, 7, 8), 32: (1, 2, 8, 31, 32), 128: (1, 2, 32, 127, 128)}
MAPPINGS = ("next_anchor", "previous_anchor")
BILLINGS = ("natural_anchor", "full_control")
CASES = tuple((b, k) for b, ks in ANCHORS.items() for k in ks)


def matrix():
    rows = tuple(
        (mode, rate, seed, c, b, t, rep, mapping, billing)
        for mode in ("periodic", "poisson")
        for rate in (500, 2500, 5000)
        for seed in (41, 42, 43)
        for c in CANDIDATES
        for b, t in POLICIES
        for rep in (1, 2, 3)
        for mapping in MAPPINGS
        for billing in BILLINGS
    )
    require(len(rows) == len(set(rows)) == 3024, "Fixed unique scenario keys")
    return rows


def planner():
    return dict(
        traces=18,
        unique_synthetic_events=90000,
        scenarios=len(matrix()),
        event_presentations=len(matrix()) * 5000,
        common_contexts=756,
        contrasts=2268,
        paired_vectors=90,
        original_timed_observations=3600,
        occupancy_row_bound=sum(b for b, t in POLICIES) * 18 * 2 * 3 * 4,
        anchor_row_bound=sum(len(ANCHORS[b]) for b, t in POLICIES) * 18 * 2 * 3 * 4,
    )


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
        "Task0046 validation namespace",
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
        "Current Task0046 software acceptance",
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
        == 3024
        and w["counters"]["event_presentations_started"]
        == w["counters"]["event_presentations_completed"]
        == 15120000,
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
        v["task"] == "0046"
        and v["status"]
        == "software_accepted_synthetic_occupancy_service_replay_roundtrip"
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
