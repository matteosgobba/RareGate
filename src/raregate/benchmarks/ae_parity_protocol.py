"""Strict review-only metadata and source bindings; no numerical imports."""

from raregate.benchmarks import protocol as p

ROOT = p.ROOT
CONFIG = "configs/benchmarks/ae_batch_parity_review_v1.json"
PROTOCOL_HASH = "4eba729d5072dbce00f7626622815a74098f7db704e456abbd08ad0c59567ee9"
OUTPUT = "results/benchmarks/task0021-ae-batch-parity-review"
SYNTHETIC = "data/task0021-synthetic-study"
ACCEPTANCE = "data/task0021-review-acceptance.json"


def load(root=ROOT):
    spec = p.read(root / CONFIG)
    if p.digest(spec) != PROTOCOL_HASH:
        raise ValueError("Unsupported review protocol/keys/selector/thresholds.")
    return spec


def fixed_path(root, relative):
    path = root / relative
    if path.resolve() != path.absolute():
        raise ValueError("Symlink/foreign review path refused.")
    return path


def verify_metadata(root, spec):
    """Only small JSON/source and prepared FILE bytes, never numerical arrays/stores."""
    paths = {spec["prompt"]["path"]: spec["prompt"]["file_sha256"]}
    paths.update(spec["lineage_file_sha256"])
    paths.update(spec["historical_source_sha256"])
    model = spec["model"]
    paths.update(
        {
            model[f"{k}_path"]: model[f"{k}_file_sha256"]
            for k in ("config", "model", "results")
        }
    )
    inputs = spec["frozen_input_provenance"]
    paths[inputs["scaler_source"]] = inputs["preprocessing_file_sha256"]
    for name, expected in paths.items():
        path = fixed_path(root, name)
        if path.stat().st_size > 16 * 2**20 or p.file_hash(path) != expected:
            raise ValueError("Frozen historical/file binding changed: " + name)
    old = root / p.OUTPUT
    workflow, reservation, prepared, audit = (
        p.read(old / name)
        for name in (
            "workflow.json",
            "reservation.json",
            "prepare/prepared.json",
            "prepare/access-audit.json",
        )
    )
    if (
        workflow["status"] != "failed_consumed_no_retry"
        or reservation["status"] != "reserved_no_retry"
        or prepared["shape"] != [1024, 8]
        or prepared["dtype"] != "float32"
        or prepared["unique_rows"] != 1024
        or prepared["strict_source_order"] is not True
        or prepared["manifest_scientific_sha256"] != inputs["scientific_sha256"]
        or audit["custody"]["status"] != "completed"
        or audit["population"]
        != {
            "split": "train_background",
            "dev_only": True,
            "allow_test": False,
            "include_labels": False,
            "representation": "event_features",
            "status": "completed",
            "rows": 1024,
            "requests": 1,
            "unique_rows": 1024,
            "ids_sha256": prepared["source_ids_bytes_sha256"],
        }
        or audit["optimizer_updates"] != 0
        or audit["test_background_model_access"] is not False
        or audit["test_signal_model_access"] is not False
    ):
        raise ValueError("Original preparation/workflow lineage incompatible.")
    config, artifact, results = (
        p.read(root / model[f"{k}_path"]) for k in ("config", "model", "results")
    )
    if p.digest(config) != model["config_canonical_sha256"]:
        raise ValueError("Configuration canonical identity changed.")
    for document, key in ((artifact, "model"), (results, "results")):
        if (
            p.digest(document["scientific"]) != document["scientific_sha256"]
            or document["scientific_sha256"] != model[f"{key}_scientific_sha256"]
        ):
            raise ValueError("Scientific JSON identity changed.")
    provenance = artifact["scientific"]["provenance"]
    if (
        provenance["processed_scientific_sha256"]
        != inputs["full_training_provenance_sha256"]
        or provenance["split_identity_sha256"] != inputs["split_scientific_sha256"]
        or provenance["preprocessing_config_sha256"]
        != inputs["preprocessing_file_sha256"]
        or provenance["model_config_sha256"] != model["config_canonical_sha256"]
        or artifact["scientific"]["features"] != inputs["channels"]
        or results["scientific"]["model_scientific_sha256"]
        != artifact["scientific_sha256"]
        or [
            {"target_fpr": t["target_fpr"], "threshold": t["threshold"]}
            for t in results["scientific"]["thresholds"]
        ]
        != model["thresholds"]
        or config["thresholds"]["decision"] != "score > threshold"
    ):
        raise ValueError("Frozen full-training/input/calibration provenance mismatch.")
    path = fixed_path(root, spec["input"]["path"])
    if (
        path.stat().st_size != spec["input"]["file_size_bytes"]
        or p.file_hash(path) != spec["input"]["file_sha256"]
        or prepared["input_file_sha256"] != spec["input"]["file_sha256"]
        or prepared["input_bytes_sha256"] != spec["input"]["array_bytes_sha256"]
    ):
        raise ValueError("Prepared file identity/size changed before numerical open.")
    return {
        "metadata_file_bindings_verified": len(paths),
        "prepared_file_byte_hash_verified": True,
        "numerical_array_opened": False,
    }


def verify_acceptance(root=ROOT, *, campaign=False):
    path = root / OUTPUT / "acceptance.json" if campaign else root / ACCEPTANCE
    a = p.read(path)
    study = a.get("synthetic_study", {})
    if (
        a.get("task") != "0021"
        or a.get("schema_version") != 1
        or a.get("protocol_canonical_sha256") != PROTOCOL_HASH
        or a.get("source_sha256") != p.source_map(root)
        or type(a.get("pytest_passed")) is not int
        or a["pytest_passed"] <= 763
        or a.get("pytest_cases") != a["pytest_passed"]
        or a.get("portable_passed") != a["pytest_passed"]
        or a.get("runtime_versions") != p.runtime_versions()
        or a.get("quality_checks")
        != {
            "ruff_lint": "passed",
            "ruff_format": "passed",
            "pip_check": "passed",
            "cpu_smoke": "passed",
        }
        or study.get("status") != "completed"
        or study.get("source_sha256") != a["source_sha256"]
        or study.get("families_completed") != 4
        or study.get("effective_threads_verified") is not True
        or not 0 < study.get("peak_rss_bytes", 0) <= 1073741824
        or not 0 < study.get("native_heap_reserved_bytes", 0) <= 536870912
        or not 0 < study.get("worker_seconds", 0) <= 60
    ):
        raise ValueError("Current complete review acceptance/study/source required.")
    for e in a["validation_evidence"]:
        if p.file_hash(root / e["path"]) != e["file_sha256"]:
            raise ValueError("Review validation evidence changed.")
    return a
