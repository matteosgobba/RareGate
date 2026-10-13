"""Task0038 fixed, stdlib-only custody and prospective plan bindings."""

from pathlib import Path

from latenttrigger.benchmarks import frozen_cpu_v2_protocol as old
from latenttrigger.benchmarks import protocol as historical
from latenttrigger.simulation.protocol import dependencies, require
from latenttrigger.simulation.protocol import durable_json as durable_json

ROOT = historical.ROOT
CONFIG = "configs/benchmarks/prepared_batch_service_v1.json"
PROMPT = "docs/prompts/0038-prepared-batch-service-measurement.md"
OUTPUT = "results/benchmarks/task0038-prepared-batch-service"
CONFIG_HASH = "fc8928bb330e3a7b0e8f5049d78824e0b106f75e713422315102d7547cca7c12"
CASES = tuple(
    (b, m)
    for b in (1, 8, 32, 128, 1024)
    for m in ((1,) if b == 1 else (1, 2, b - 1, b))
)
LIMITS = dict(
    prerequisite_seconds=60,
    worker_seconds=120,
    reporting_seconds=60,
    finalization_seconds=15,
    reserved_seconds=480,
    whole_seconds=540,
    cleanup_seconds=2,
    worker_RSS_bytes=2**30,
    native_reserved_bytes=512 * 2**20,
    controller_RSS_bytes=128 * 2**20,
    guard_journal_bytes=16 * 2**20,
    worker_log_bytes=2**20,
    owned_storage_bytes=128 * 2**20,
)
read, digest, file_hash = historical.read, historical.digest, historical.file_hash


def load(root=ROOT):
    spec = read(root / CONFIG)
    require(digest(spec) == CONFIG_HASH, "Fixed Task0038 protocol, no overrides")
    return spec


def fixed(root, relative):
    path = root / relative
    require(
        path.absolute() == path.resolve() and path.is_file(), "Missing/symlinked source"
    )
    return path


def source_map(root=ROOT):
    names = {
        v
        for folder in ("src", "scripts", "tests")
        for v in (root / folder).rglob("*.py")
    }
    names.update(root / v for v in (CONFIG, PROMPT, "pyproject.toml"))
    require(all(not v.is_symlink() for v in names), "Source symlink")
    return {str(v.relative_to(root)): file_hash(v) for v in sorted(names)}


def custody(root=ROOT):
    """Only byte/header/small metadata access; no numerical array/model construction."""
    spec = load(root)
    for name, sha in spec["byte_pins"].items():
        require(file_hash(fixed(root, name)) == sha, "Pinned source changed: " + name)
    base = read(root / "configs/benchmarks/frozen_cpu_v2.json")
    require(digest(base) == old.HASH, "Accepted registry identity")
    path, header = old.input_file(root, base)
    prepared = read(root / spec["preparation"]["prepared_path"])
    receipt = read(root / spec["preparation"]["receipt_path"])
    population = receipt["access_audit"]["population"]
    require(
        receipt["status"] == "completed"
        and population == spec["preparation"]["population"],
        "Prepared role/order lineage",
    )
    require(
        prepared["strict_source_order"] is True
        and prepared["unique_rows"] == 1024
        and prepared["source_ids_bytes_sha256"] == population["ids_sha256"]
        and prepared["input_file_sha256"] == base["input"]["file_sha256"]
        and prepared["input_bytes_sha256"] == base["input"]["array_bytes_sha256"],
        "Prepared byte/source-order relationship",
    )
    summary = read(
        root / "results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json"
    )
    require(
        summary["execution_status"] == "complete_accepted_consumed_no_retry"
        and summary["comparison_success"] is True
        and summary["active_v2_numerical_policy"] == "arithmetic-cpu-v2",
        "Accepted Task0022 status",
    )
    for entry in base["models"]:
        docs = {
            k: read(root / entry[k + "_path"]) for k in ("config", "model", "results")
        }
        require(
            digest(docs["config"]) == entry["config_canonical_sha256"],
            "Config identity",
        )
        for k in ("model", "results"):
            require(
                digest(docs[k]["scientific"])
                == docs[k]["scientific_sha256"]
                == entry[k + "_scientific_sha256"],
                "Scientific identity",
            )
        science = docs["model"]["scientific"]
        require(
            science["provenance"]["processed_scientific_sha256"]
            == base["input"]["full_training_provenance_sha256"]
            and science["features"] == base["input"]["channels"]
            and docs["results"]["scientific"]["model_scientific_sha256"]
            == entry["model_scientific_sha256"]
            and [
                {"target_fpr": v["target_fpr"], "threshold": v["threshold"]}
                for v in docs["results"]["scientific"]["thresholds"]
            ]
            == entry["thresholds"],
            "Training/features/calibration relationship",
        )
    return dict(
        header=header,
        input_path=str(path),
        numerical_loads=0,
        byte_sources=len(spec["byte_pins"]),
    ), base


def verify_acceptance(path):
    path = Path(path).absolute()
    require(
        path.parent.parent == ROOT / "data/task0038-validation"
        and path.name == "software-acceptance.json",
        "New acceptance namespace",
    )
    a = read(path)
    require(
        a["status"] == "software_accepted_synthetic_prepared_service_only"
        and a["source_map"] == source_map()
        and a["dependencies"] == dependencies()
        and a["config_sha256"] == file_hash(ROOT / CONFIG)
        and a["prompt_sha256"] == file_hash(ROOT / PROMPT),
        "Fresh complete source/dependency acceptance",
    )
    require(
        set(a["checks"])
        == {
            "focused",
            "full",
            "portable",
            "lint",
            "format",
            "dependencies",
            "native_synthetic",
        }
        and all(v["exit_code"] == 0 for v in a["checks"].values()),
        "Complete final validation",
    )
    for item in a["checks"].values():
        require(
            file_hash(ROOT / item["log"]) == item["log_sha256"],
            "Validation log identity",
        )
    require(
        file_hash(ROOT / a["native_receipt_path"]) == a["native_receipt_sha256"],
        "Synthetic native receipt",
    )
    return a
