"""Strict fixed Task0037 schema, byte custody and current-source acceptance."""

import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "configs/simulation/synthetic_trigger_v1.json"
PROMPT = "docs/prompts/0037-synthetic-trigger-simulator.md"
CANDIDATES = ("pca-v1", "compact-autoencoder-v2")
BATCHES = (1, 8, 32, 128, 1024)
POLICIES = ((1, 0), *((b, t) for b in BATCHES[1:] for t in (100000, 1000000)))
PINS = {
    "results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv": "ddd4d1ed21d11f28999687c757638238bb548e156061525a0c4ded368ed9d75b",
    "results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json": "33c09221548ef56ef1b96f10c951161b65bea8d9565f2f3c100fd5f7a7c5744e",
    "results/tables/final/task0032-quality-cost.csv": "64883a3668c82edbe34b38fd125326196f579a9f3b58db89e12ce791ed10720d",
}
LIMITS = dict(
    prerequisite_seconds=30,
    simulation_seconds=120,
    reporting_seconds=60,
    finalization_seconds=15,
    whole_seconds=240,
    cleanup_seconds=2,
    worker_RSS_bytes=2**30,
    native_reserved_bytes=512 * 2**20,
    controller_RSS_bytes=128 * 2**20,
    guard_journal_bytes=64 * 2**20,
    worker_log_bytes=2**20,
    owned_storage_bytes=128 * 2**20,
    retained_trace_bytes=16 * 2**20,
    max_latency_entries_per_scenario=5000,
)
EXPECTED = dict(
    schema_version=1,
    task="0037",
    kind="synthetic_trigger_only",
    server="one_fifo_nonpreemptive",
    admission="drop_tail_waiting_plus_in_service",
    tie_order=["completion", "arrivals_source_order", "dispatch_flush"],
    partial_service="constant_cost_for_B_modeled_padded_slots",
    flush_origin="oldest_waiting_original_arrival",
    source_events_per_trace=5000,
    seeds=[41, 42, 43],
    rates_per_second=[10000, 100000, 1000000],
    arrival_modes=["periodic", "poisson"],
    rng="PCG64_SeedSequence_[3700,seed,mode_id,rate,stream_id]",
    toy_thresholds=[0.9, 0.95, 0.99, 0.999],
    toy_decision="strict_score_gt_threshold_after_completion",
    candidates=list(CANDIDATES),
    policies=[list(p) for p in POLICIES],
    capacity_actual_events=1024,
    deadline_ns=1000000,
    main_service="ceil_count_weighted_pooled_600_invocation_adapter_mean_ns",
    sensitivity=dict(
        rate_per_second=100000,
        arrival_mode="poisson",
        batch=128,
        timeout_ns=100000,
        workers_per_candidate=3,
        constant_statistics=["mean_ns", "p99_ns", "max_ns"],
    ),
    expected=dict(
        traces=18,
        unique_events=90000,
        main_scenarios=324,
        stress_scenarios=54,
        scenarios=378,
        event_presentations=1890000,
    ),
    limits=LIMITS,
    operational_model_or_population_work_authorized=False,
    independent_signal_confirmation=False,
)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def nonsymlink(root, relative):
    require(relative in PINS or relative in (CONFIG, PROMPT), "Fixed file allowlist")
    root = Path(root).absolute()
    require(not root.is_symlink(), "Symlink root")
    path = root
    for part in Path(relative).parts:
        path /= part
        require(not path.is_symlink(), "Symlink source path")
    require(
        path.is_file() and path.stat().st_size <= 2 * 2**20,
        "Missing/oversized curated source",
    )
    return path


def validate_config(value):
    # Canonical JSON also distinguishes True from1 and rejects NaN/unknown fields.
    require(digest(value) == digest(EXPECTED), "Fixed synthetic schema/matrix/limits")
    return value


def load_config(root=ROOT):
    return validate_config(json.loads(nonsymlink(root, CONFIG).read_text()))


def read(path):
    path = Path(path)
    require(
        not path.is_symlink() and path.stat().st_size <= 4 * 2**20, "Bounded owned JSON"
    )
    return json.loads(path.read_text())


def durable_json(path, value, *, exclusive=False):
    path = Path(path)
    require(not path.is_symlink(), "Owned JSON symlink")
    data = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    require(len(data) <= 4 * 2**20, "4MiB JSON ceiling")
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("xb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if exclusive:
            os.link(temp, path)
            temp.unlink()
        else:
            os.replace(temp, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temp.exists():
            temp.unlink()


def source_map(root=ROOT):
    root = Path(root)
    names = {
        p
        for folder in ("src", "scripts", "tests")
        for p in (root / folder).rglob("*.py")
    }
    names.update(root / p for p in (CONFIG, PROMPT, "pyproject.toml"))
    require(all(not p.is_symlink() for p in names), "Source-map symlink")
    return {str(p.relative_to(root)): file_hash(p) for p in sorted(names)}


def dependencies():
    return dict(
        python=sys.version,
        platform=platform.platform(),
        packages={
            d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
        },
    )


def verify_acceptance(path):
    path = Path(path).absolute()
    require(
        path.parent.parent == ROOT / "data/task0037-validation"
        and path.name == "software-acceptance.json",
        "Fresh Task0037 acceptance path",
    )
    value = read(path)
    require(
        value["status"] == "software_accepted_synthetic_simulator_only"
        and value["source_map"] == source_map()
        and value["dependencies"] == dependencies()
        and value["config_sha256"] == file_hash(ROOT / CONFIG)
        and value["prompt_sha256"] == file_hash(ROOT / PROMPT),
        "Current-source/dependency/config/prompt acceptance",
    )
    require(
        set(value["checks"])
        == {"focused", "full", "portable", "lint", "format", "dependencies"}
        and all(x["exit_code"] == 0 for x in value["checks"].values()),
        "Complete fresh validation",
    )
    return value
