"""Task0047 own current byte custody with unchanged scientific/header relationships."""

from raregate.benchmarks import frozen_cpu_v2_protocol as old
from raregate.benchmarks import prepared_service_protocol as prepared_protocol
from raregate.benchmarks import targeted_raw_protocol as p
from raregate.benchmarks.development_raw_protocol import header

read, require, digest, file_hash, fixed, load, RAW = (
    p.read,
    p.require,
    p.digest,
    p.file_hash,
    p.fixed,
    p.load,
    p.RAW,
)


def raw_custody(root):
    """Small text/header/byte custody only; deliberately no raw-file hash here."""
    spec = load(root)
    for name, sha in spec["byte_pins"].items():
        require(file_hash(fixed(root, name)) == sha, "Changed pinned source: " + name)
    for key in ("membership", "golden"):
        entry = spec[key]
        path = fixed(root, entry["path"])
        require(file_hash(path) == entry["file_sha256"], "Input byte custody")
        header(path, entry["shape"], entry["dtype"], entry["size_bytes"])
    raw = fixed(root, RAW)
    require(raw.stat().st_size == spec["raw"]["size_bytes"], "Raw stat size")
    split = read(root / spec["lineage"]["split_manifest"])
    config = read(root / spec["transform_config"])
    manifest = read(root / spec["lineage"]["dev_manifest"])
    science = manifest["scientific"]
    prepared = read(root / spec["lineage"]["prepared"])
    receipt = read(root / spec["lineage"]["prepare_receipt"])
    acquire = read(root / spec["lineage"]["acquisition"])
    audit = read(root / spec["lineage"]["raw_audit"])
    require(
        manifest["scientific_sha256"]
        == digest(science)
        == spec["lineage"]["dev_scientific_sha256"]
        and science["scope"] == "dev"
        and science["counts"]["train_background"] == 6999
        and science["counts"]["test_background"]
        == science["counts"]["test_signal"]
        == 0,
        "Dev scientific identity/roles",
    )
    require(
        science["config_sha256"] == file_hash(root / spec["transform_config"])
        and science["config_sha256"] == science["files"]["configuration.json"]["sha256"]
        and config == read(root / spec["lineage"]["dev_configuration"]),
        "Frozen transformation identity",
    )
    require(
        science["split_identity_sha256"] == digest(science["split_identity"])
        and science["split_identity"]["array_sha256"]["dev_train_background.npy"]
        == split["artifacts"]["dev_train_background.npy"]["sha256"]
        == spec["membership"]["file_sha256"]
        and split["counts"]["dev_train_background"] == 6999
        and split["counts"] == config["split"]["counts"]
        and science["split_identity"]["development_subset"]
        == split["development_subset"]
        == config["split"]["development_subset"]
        and all(
            science["split_identity"]["array_sha256"][name]
            == split["artifacts"][name]["sha256"]
            == sha
            for name, sha in config["analysis_provenance"]["split_array_sha256"].items()
        )
        and split["protocol"] == config["split"]["protocol"]
        and split["seed"] == config["split"]["seed"],
        "Membership role/config/split binding",
    )
    population = receipt["access_audit"]["population"]
    require(
        receipt["status"] == "completed"
        and population["split"] == "train_background"
        and population["dev_only"] is True
        and population["allow_test"] is False
        and population["include_labels"] is False
        and population["status"] == "completed"
        and population["rows"] == population["unique_rows"] == 1024
        and population["ids_sha256"]
        == prepared["source_ids_bytes_sha256"]
        == spec["membership"]["selected_sha256"]
        and prepared["strict_source_order"] is True
        and prepared["manifest_scientific_sha256"] == manifest["scientific_sha256"]
        and prepared["input_file_sha256"] == spec["golden"]["file_sha256"]
        and prepared["input_bytes_sha256"] == spec["golden"]["payload_sha256"],
        "Accepted preparation role/order/golden relation",
    )
    for document in (
        config["source_integrity"],
        split["source_integrity"],
        science["source_integrity"],
    ):
        require(
            document["sha256"] == spec["raw"]["file_sha256"]
            and document["file_size"] == spec["raw"]["size_bytes"],
            "Raw scientific identity",
        )
    require(
        acquire["sha256"] == spec["raw"]["file_sha256"]
        and acquire["source"]["record_id"] == 6466204
        and acquire["source"]["version"] == "v5"
        and acquire["verified_checksum"] == spec["raw"]["publisher_md5"]
        and audit["datasets"]["df/block0_values"] == spec["raw"]["audit_schema"],
        "Acquisition/audit identity",
    )
    return dict(
        status="metadata_byte_header_custody_passed",
        numerical_ID_loads=0,
        raw_hash_passes=0,
        raw_HDF_opens=0,
        model_artifacts_read=0,
    )


def model_custody(root):
    """Only byte/header/small metadata access; no numerical array/model construction."""
    spec = prepared_protocol.load(root)
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
