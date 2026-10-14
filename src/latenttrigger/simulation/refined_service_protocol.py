"""Closed Task0048 identity, byte allowlist and software admission contract."""

import json
import math
from pathlib import Path

from latenttrigger.simulation.protocol import (
    dependencies as package_dependencies,
)
from latenttrigger.simulation.protocol import (
    digest,
    durable_json,
    file_hash,
    require,
)

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "configs/simulation/refined_service_replay_v1.json"
PROMPT = "docs/prompts/0048-refined-support-service-replay.md"
STATUS = "software_accepted_synthetic_refined_support_service_replay"
PARENT_STATUS = "parent_accepted_synthetic_refined_support_service_replay"
VALIDATION = "data/task0048-validation"
NAMESPACE = "results/simulations/task0048-refined-service-replay"
CANDIDATES = ("pca-v1", "compact-autoencoder-v2")
POLICIES = ((1, 0), *((b, t) for b in (8, 32, 128) for t in (1000000, 10000000)))
EXPECTED_DIGEST = "a467e46d143801b6b404df12366737f014e642c63c35e33148df07032e02f58e"
SOURCE_MANIFEST = {
    "results/tables/final/task0047-targeted-partial-raw-decision-summary.json": {
        "sha256": "64a43df2274afbd236bfc2459ccb52999e1a89a17a9db00cc5033c94c1c9f916",
        "bytes": 398200,
    },
    "results/tables/final/task0047-targeted-partial-raw-decision-cells.csv": {
        "sha256": "53b4a171011ad19b08489fa7dc10f84a6acc93c12225ba691f7aa2fbb8adae2a",
        "bytes": 120801,
    },
    "results/tables/final/task0047-targeted-partial-raw-decision-pairs.csv": {
        "sha256": "5f15973c0e10c6e7e67bcdf65ff678d14f9555abb78738af701306ebbfbc7ec3",
        "bytes": 847822,
    },
    "results/tables/final/task0047-targeted-partial-selection.csv": {
        "sha256": "e369e25f5e647bc970d9defbd5c8aa04a046d42dfda05e0e6a498f2f52895a3d",
        "bytes": 19686,
    },
    "configs/benchmarks/development_targeted_raw_decision_v1.json": {
        "sha256": "16f14d89297efc84dc51179bd93fbcc5d34dfa8e91b98d55e88d62d1b5ef4d92",
        "bytes": 24991,
    },
    "docs/prompts/0047-targeted-partial-raw-decision-measurement.md": {
        "sha256": "ea33de3e6ef252cbbbdf5cbe1c34466ed46eabfca755a12d5301958cff547434",
        "bytes": 25014,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/attempt.json": {
        "sha256": "d2a7440c3dd0d1731404845c71fe98d4df6cfe59f06f9809b30681d92adec75b",
        "bytes": 303,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/plan.json": {
        "sha256": "c6c9ae60aaeaa37bf5b1f1a12a2fc4e7a6dcd53623503fdcbafdc9fde0678f68",
        "bytes": 54931,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/workflow.json": {
        "sha256": "f04fc8f08e9d2e04628b1ef6ea1f5064ee3260773b51f309e4894a0cae4c6af3",
        "bytes": 94877,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/parent-acceptance.json": {
        "sha256": "7a6d50e78fc5cd9140e138d70eb90b612223366ef63052af702f7e95f726ea56",
        "bytes": 952,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/reporting/receipt.json": {
        "sha256": "e9b57b05be54d7a55dd39bcc2023e2b20729af9f2e1407531df421e6f9e0e4ed",
        "bytes": 44356,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/reporting/summary.json": {
        "sha256": "3daadab646b5d0a8cc7ed259775e693f2deece35a12cd6a0f5e639f2b30318a5",
        "bytes": 304159,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition1/receipt.json": {
        "sha256": "9aca76ebc01cdc7103871d1ec54c2db977224508ee8665cbcb8f0e0a382925f0",
        "bytes": 56141,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition1/aggregate.json": {
        "sha256": "2b1ad758e1bc5734864bebfe8f3d032805b09c8a6498d20124dcdd7cbeb79372",
        "bytes": 3336347,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition1/timings.jsonl": {
        "sha256": "8e2dcc91276a8ce87442b124375281a089602e12e02d784c7afe195968a36044",
        "bytes": 1707921,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition1/timer.json": {
        "sha256": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
        "bytes": 199,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition2/receipt.json": {
        "sha256": "4831b1f35305e845833c8501f54debfcef55b8c5ff7516212a34d409c6a8ae3b",
        "bytes": 56143,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition2/aggregate.json": {
        "sha256": "bd0b9107531ba51c186ee003f4f6a96f77fbdf369aa90172e3fe43bad3235a8f",
        "bytes": 3336274,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition2/timings.jsonl": {
        "sha256": "fdb3fa4061f769d6ede9160a102c502af50e5e1bbedb30d78db18c1631b925bf",
        "bytes": 1707906,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition2/timer.json": {
        "sha256": "8ef1c7e830557cd888b64e746e1e1dbfc58073f98dece8cef020281bc86e097b",
        "bytes": 199,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition3/receipt.json": {
        "sha256": "c11e1a9304d0dd3daa8d7204bc4a27f62f338aa0514f77e2928522ad4434197e",
        "bytes": 56143,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition3/aggregate.json": {
        "sha256": "3d51767152aa46e46f15d37e2960e972c19153603f99e33415ba75c24bb688d9",
        "bytes": 3336496,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition3/timings.jsonl": {
        "sha256": "05de80e404f272c0be1d24fccf62eb5aecc338a759094becc948e66372ca6d30",
        "bytes": 1708036,
    },
    "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d/repetition3/timer.json": {
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
    "source_bundle_bytes": 25165824,
    "parsed_source_python_bytes": 134217728,
    "retained_service_vectors_bytes": 2097152,
}
SOURCE_DIRECTORY = "results/benchmarks/task0047-targeted-partial-raw-decisions/4b1ae2522d114b47a56a89abccd9918d"


def safe(root, relative, *, maximum=24 * 2**20):
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
    path = Path(path).absolute()
    require(
        path.resolve() == path
        and not path.is_symlink()
        and path.is_file()
        and path.stat().st_size <= 4 * 2**20,
        "Bounded nonsymlink JSON custody",
    )

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
        digest(value) == EXPECTED_DIGEST, "Fixed Task0048 config/matrix/pins/limits"
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
        task="0048",
        kind="deterministic_refined_support_service_replay",
        validation_owner="0048",
        scope="closed_Task0047_timing_metadata_synthetic_FIFO",
        assignment_contract_sha256=digest(
            dict(
                supports=SUPPORTS,
                mappings=MAPPINGS,
                billings=BILLINGS,
                cursor="independent_anchor_zero_mod20_dispatch_only",
            )
        ),
        config_sha256=file_hash(safe(root, CONFIG)),
        prompt_sha256=file_hash(safe(root, PROMPT)),
    )


COARSE = {1: (1,), 8: (1, 2, 7, 8), 32: (1, 2, 8, 31, 32), 128: (1, 2, 32, 127, 128)}
REFINED = {
    1: (1,),
    8: tuple(range(1, 9)),
    32: (*range(1, 9), 31, 32),
    128: (*range(1, 11), 32, 127, 128),
}
SUPPORTS = {"coarse_reference": COARSE, "refined_32": REFINED}
ANCHORS = REFINED
WRAPPER = "task0047_owned_C_FP32_actual_rows_public_score_strict4_copies_v1"


def point_class(b, k):
    return "remeasured_reference" if k in COARSE[b] else "new_selected_point"


MAPPINGS = ("next_anchor", "previous_anchor")
BILLINGS = ("natural_anchor", "full_control")
CASES = tuple((b, k) for b, ks in ANCHORS.items() for k in ks)


def matrix():
    rows = tuple(
        (mode, rate, seed, c, b, t, rep, support, mapping, billing)
        for mode in ("periodic", "poisson")
        for rate in (500, 2500, 5000)
        for seed in (41, 42, 43)
        for c in CANDIDATES
        for b, t in POLICIES
        for rep in (1, 2, 3)
        for support in SUPPORTS
        for mapping in MAPPINGS
        for billing in BILLINGS
    )
    require(len(rows) == len(set(rows)) == 6048, "Fixed unique scenario keys")
    return rows


def planner():
    return dict(
        traces=18,
        unique_synthetic_events=90000,
        scenarios=len(matrix()),
        event_presentations=len(matrix()) * 5000,
        common_contexts=756,
        contrasts=6048,
        paired_vectors=192,
        original_timed_observations=7680,
        occupancy_row_bound=sum(b for b, t in POLICIES) * 18 * 2 * 3 * 8,
        anchor_row_bound=sum(len(a[b]) for a in SUPPORTS.values() for b, t in POLICIES)
        * 18
        * 2
        * 3
        * 4,
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
        "Task0048 validation namespace",
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
        "Current Task0048 software acceptance",
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
    for name, c in v["checks"].items():
        require(type(c["exit_code"]) is int and c["exit_code"] == 0, "Passed check")
        log = safe(ROOT, c["log"])
        require(
            log.parent == path.parent and file_hash(log) == c["log_sha256"],
            "Owned check log/hash",
        )
        if name in ("full", "portable"):
            import xml.etree.ElementTree as ET

            parts = c["subchecks"]
            require(
                type(parts) is list and len(parts) == 3,
                "Three bounded full-suite partitions",
            )
            files = [f for part in parts for f in part["test_files"]]
            expected = sorted(
                str(f.relative_to(ROOT)) for f in (ROOT / "tests").rglob("test*.py")
            )
            require(
                sorted(files) == expected and len(files) == len(set(files)),
                "Complete disjoint fresh full-suite file coverage",
            )
            for part in parts:
                require(
                    type(part["exit_code"]) is int
                    and part["exit_code"] == 0
                    and part["elapsed_seconds"] <= 240,
                    "Passed bounded software partition",
                )
                xml = safe(ROOT, part["junit"])
                require(
                    xml.parent == path.parent
                    and file_hash(xml) == part["junit_sha256"],
                    "Owned partition result/hash",
                )
                suites = list(ET.parse(xml).getroot().iter("testsuite"))
                counts = {
                    key: sum(int(s.get(key, "0")) for s in suites)
                    for key in ("tests", "failures", "errors", "skipped")
                }
                require(
                    all(
                        type(part[k]) is int and part[k] == n for k, n in counts.items()
                    )
                    and counts["tests"] > 0
                    and counts["failures"]
                    == counts["errors"]
                    == counts["skipped"]
                    == 0,
                    "Complete successful partition results",
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
        == 6048
        and w["counters"]["event_presentations_started"]
        == w["counters"]["event_presentations_completed"]
        == 30240000,
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
        expected_outputs = (
            {
                "summary.json",
                "scenarios.csv",
                "contrasts.csv",
                "occupancies.csv",
                "anchor-audit.csv",
            }
            if r["phase"] == "simulation"
            else {"outcomes.png", "latency.png", "sensitivity.png", "reporting.json"}
        )
        require(
            set(body["outputs"]) == expected_outputs
            and type(body["resources"]["peak_rss_bytes"]) is int
            and 0 < body["resources"]["peak_rss_bytes"] <= LIMITS["worker_RSS_bytes"]
            and type(body["resources"]["native_heap_reserved_bytes"]) is int
            and 0
            < body["resources"]["native_heap_reserved_bytes"]
            <= LIMITS["native_reserved_bytes"]
            and 0 <= body["cleanup_seconds"] <= 2
            and body["worker_seconds"] <= LIMITS[r["phase"] + "_seconds"],
            "Outer native output/resource/cleanup contract",
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
        v["task"] == "0048"
        and v["status"]
        == "software_accepted_synthetic_refined_support_service_replay_roundtrip"
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
