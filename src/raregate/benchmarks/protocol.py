"""Strict Task0020 protocol/metadata/acceptance checks, standard library only."""

import hashlib
import json
import math
import os
import platform
import statistics
import subprocess
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "configs/benchmarks/frozen_cpu_v1.json"
PROTOCOL_HASH = "8f57d005c65443ab2143f48c64ecf7590cdc0389408bbef4a010571092305846"
OUTPUT = "results/benchmarks/task0020-frozen-cpu"
ACCEPTANCE = "data/task0020-synthetic-acceptance.json"
PHASES = ("prepare", "PCA1", "AE1", "PCA2", "AE2", "PCA3", "AE3")


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def read(path):
    path = Path(path)
    if path.stat().st_size > 4 * 2**20:
        raise ValueError("Expected bounded JSON metadata.")
    return json.loads(
        path.read_text(),
        object_pairs_hook=_pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )


def write(path, value, *, exclusive=False):
    path = Path(path)
    content = json.dumps(value, indent=2, allow_nan=False) + "\n"
    if exclusive:
        with path.open("x") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
    else:
        temp = path.with_suffix(".tmp")
        temp.write_text(content)
        temp.replace(path)


def now():
    return datetime.now(UTC).isoformat()


def load(root=ROOT):
    value = read(root / CONFIG)
    if digest(value) != PROTOCOL_HASH:
        raise ValueError("Unsupported protocol/keys/limits/selector; no overrides.")
    return value


def validate_scope(
    store_path, population, dev_only, allow_test, include_labels, root=ROOT
):
    expected = root / "data/processed/lhco-rd-v1/schema-v1/dev"
    if (
        Path(store_path) != expected
        or expected.resolve() != expected.absolute()
        or population != "train_background"
        or dev_only is not True
        or allow_test is not False
        or include_labels is not False
    ):
        raise ValueError("Only fixed dev training aggregates without truth/test.")


def validate_dev_manifest(manifest, expected):
    science = manifest.get("scientific", {})
    if (
        manifest.get("schema_version") != 1
        or manifest.get("complete") is not True
        or digest(science) != manifest.get("scientific_sha256")
        or manifest["scientific_sha256"] != expected["scientific_sha256"]
        or science.get("scope") != "dev"
        or science.get("aggregate_channels") != expected["channels"]
        or science.get("config_sha256") != expected["preprocessing_file_sha256"]
        or science.get("split_identity_sha256") != expected["split_scientific_sha256"]
        or digest(science.get("split_identity")) != expected["split_scientific_sha256"]
        or science.get("counts", {}).get("train_background", 0) < 1024
        or science.get("counts", {}).get("test_background") != 0
        or science.get("counts", {}).get("test_signal") != 0
    ):
        raise ValueError("Frozen dev inference schema/scaler/split identity mismatch.")


def verify_frozen(root, specification):
    """Small metadata only; no ProcessedStore, population or full-payload hashing."""
    for entry in [specification["prompt"], specification["brief"]]:
        if file_hash(root / entry["path"]) != entry["file_sha256"]:
            raise ValueError("Prompt/brief byte identity changed.")
    brief = specification["brief"]
    if file_hash(root / brief["summary_path"]) != brief["summary_file_sha256"]:
        raise ValueError("Task0019 curated brief changed.")
    inputs = specification["input"]
    validate_scope(
        root / inputs["store"], inputs["population"], True, False, False, root
    )
    if file_hash(root / inputs["scaler_source"]) != inputs["preprocessing_file_sha256"]:
        raise ValueError("Frozen preprocessing file changed.")
    manifest = read(root / inputs["store"] / "manifest.json")
    validate_dev_manifest(manifest, inputs)
    for model in specification["models"]:
        documents = {}
        for kind in ("config", "model", "results"):
            path = root / model[f"{kind}_path"]
            if file_hash(path) != model[f"{kind}_file_sha256"]:
                raise ValueError(
                    "Frozen model/config/calibration byte identity changed."
                )
            documents[kind] = read(path)
        config, artifact, result = (
            documents[k] for k in ("config", "model", "results")
        )
        if digest(config) != model["config_canonical_sha256"]:
            raise ValueError("Frozen config content mismatch.")
        for kind in ("model", "results"):
            document = documents[kind]
            if (
                digest(document["scientific"]) != document["scientific_sha256"]
                or document["scientific_sha256"] != model[f"{kind}_scientific_sha256"]
            ):
                raise ValueError("Frozen scientific content mismatch.")
        science, results = artifact["scientific"], result["scientific"]
        provenance = science["provenance"]
        if (
            provenance["processed_scientific_sha256"]
            != inputs["full_training_provenance_sha256"]
            or provenance["preprocessing_config_sha256"]
            != inputs["preprocessing_file_sha256"]
            or provenance["split_identity_sha256"] != inputs["split_scientific_sha256"]
            or provenance["model_config_sha256"] != model["config_canonical_sha256"]
            or science["features"] != inputs["channels"]
            or science["score_definition"] != "sum_squared_reconstruction_residual"
            or science["orientation"] != "higher_is_more_anomalous"
            or results["model_scientific_sha256"] != artifact["scientific_sha256"]
            or [
                {"target_fpr": t["target_fpr"], "threshold": t["threshold"]}
                for t in results["thresholds"]
            ]
            != model["thresholds"]
            or any(t["calibration"]["total"] != 74823 for t in results["thresholds"])
            or config["thresholds"]["decision"] != "score > threshold"
        ):
            raise ValueError("Input/model/calibration provenance or score mismatch.")
    return {"manifest_file_sha256": file_hash(root / inputs["store"] / "manifest.json")}


def source_map(root=ROOT):
    paths = sorted(
        {
            *root.glob("src/raregate/**/*.py"),
            *root.glob("tests/*.py"),
            *root.glob("scripts/*.py"),
        }
    )
    return {str(p.relative_to(root)): file_hash(p) for p in paths}


def runtime_versions():
    return {
        "python": platform.python_version(),
        **{
            name: version(name)
            for name in (
                "numpy",
                "torch",
                "scikit-learn",
                "scipy",
                "threadpoolctl",
                "h5py",
                "hdf5plugin",
            )
        },
    }


def verify_acceptance(root, specification, *, campaign=False):
    path = root / OUTPUT / "acceptance.json" if campaign else root / ACCEPTANCE
    accepted = read(path)
    if (
        accepted.get("schema_version") != 1
        or accepted.get("task") != "0020"
        or accepted.get("protocol_canonical_sha256") != PROTOCOL_HASH
        or accepted.get("source_sha256") != source_map(root)
        or type(accepted.get("pytest_passed")) is not int
        or accepted["pytest_passed"] <= 670
        or accepted.get("pytest_cases") != accepted["pytest_passed"]
        or accepted.get("pytest_exit_code") != 0
        or accepted.get("portable_passed") != accepted["pytest_passed"]
        or accepted.get("runtime_versions") != runtime_versions()
        or accepted.get("footprint", {}).get("status") != "passed"
        or accepted.get("quality_checks")
        != {
            "ruff_lint": "passed",
            "ruff_format": "passed",
            "pip_check": "passed",
            "cpu_smoke": "passed",
        }
    ):
        raise ValueError(
            "Current complete benchmark synthetic/source acceptance required."
        )
    footprint = accepted["footprint"]
    if (
        footprint.get("synthetic_only") is not True
        or footprint.get("effective_threads_verified") is not True
        or footprint.get("source_sha256") != accepted["source_sha256"]
        or not 0
        < footprint.get("peak_rss_bytes", 0)
        <= specification["limits"]["worker_rss_bytes"]
        or not 0
        < footprint.get("native_heap_reserved_bytes", 0)
        <= specification["limits"]["worker_native_bytes"]
    ):
        raise ValueError("Benchmark synthetic startup/operation footprint invalid.")
    for evidence in accepted["validation_evidence"]:
        if file_hash(root / evidence["path"]) != evidence["file_sha256"]:
            raise ValueError("Acceptance validation evidence changed.")
    return accepted


def quantile(values, q):
    values = sorted(values)
    position = (len(values) - 1) * q
    lo, hi = math.floor(position), math.ceil(position)
    return values[lo] + (values[hi] - values[lo]) * (position - lo)


def distribution(values, batch=None):
    if not values or any(type(v) is not int or v < 0 for v in values):
        raise ValueError("Expected retained nonnegative integer nanoseconds.")
    mean = statistics.fmean(values)
    result = {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean,
        "population_std": statistics.pstdev(values),
        **{f"p{int(q * 100)}": quantile(values, q) for q in (0.5, 0.95, 0.99)},
    }
    if batch is not None:
        if mean <= 0:
            raise ValueError("Zero mean invocation time cannot define throughput.")
        result.update(
            throughput_events_per_second=batch * 1e9 / mean,
            mean_amortized_nanoseconds_per_event=mean / batch,
        )
    return result


def code_context(root=ROOT):
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, timeout=2
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=root, text=True, timeout=2
            ).strip()
        )
    except (OSError, subprocess.SubprocessError):
        commit, dirty = None, None
    return {
        "commit": commit,
        "working_tree_dirty": dirty,
        "source_sha256": source_map(root),
    }
