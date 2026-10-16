"""Fixed Task0039 metadata permission; future payload measurement is unauthorized."""

import ast
import importlib.metadata
import struct
from pathlib import Path

from raregate.benchmarks import protocol as old
from raregate.simulation.protocol import dependencies as dependencies
from raregate.simulation.protocol import durable_json as durable_json
from raregate.simulation.protocol import require

ROOT = old.ROOT
CONFIG = "configs/benchmarks/development_raw_features_v1.json"
PROMPT = "docs/prompts/0039-development-raw-feature-foundation.md"
OUTPUT = "results/benchmarks/task0039-development-raw-features"
MEMBERSHIP = "data/analysis/lhco-rd-v1/dev_train_background.npy"
RAW = "data/raw/lhco/6466204/events_anomalydetection_v2.h5"
GOLDEN = "results/benchmarks/task0020-frozen-cpu/prepare/input.npy"
CONFIG_HASH = "18293da771b510f70005d7b841784d587ff9f68f0ebce440a2d45fc3de4db236"
read, digest, file_hash = old.read, old.digest, old.file_hash
CACHE = dict(rdcc_nbytes=1048576, rdcc_nslots=521, rdcc_w0=0.75)
RESOLVER_LIMITS = dict(
    prerequisites_seconds=30,
    worker_seconds=60,
    reporting_seconds=30,
    whole_seconds=150,
    cleanup_seconds=2,
    worker_RSS_bytes=2**30,
    native_reserved_bytes=512 * 2**20,
    controller_RSS_bytes=128 * 2**20,
    guard_journal_bytes=16 * 2**20,
    log_bytes=2**20,
    storage_bytes=32 * 2**20,
)


def load(root=ROOT):
    value = read(root / CONFIG)
    require(
        digest(value) == CONFIG_HASH
        and value["future_measurement_execution_authorized"] is False,
        "Fixed prospective protocol, no payload grant",
    )
    return value


def fixed(root, relative):
    path = root / relative
    require(
        path.absolute() == path.resolve() and path.is_file(), "Missing/symlinked source"
    )
    return path


def header(path, shape, dtype, size):
    with path.open("rb") as f:
        magic = f.read(10)
        require(magic[:8] == b"\x93NUMPY\x01\x00" and len(magic) == 10, "NPY1 only")
        count = struct.unpack("<H", magic[8:])[0]
        require(count <= 1024, "Bounded NPY header")
        value = ast.literal_eval(f.read(count).decode("latin1").strip())
    require(
        value == dict(descr=dtype, fortran_order=False, shape=tuple(shape))
        and type(value["fortran_order"]) is bool
        and type(value["shape"]) is tuple
        and all(type(v) is int for v in value["shape"])
        and path.stat().st_size == size,
        "NPY dtype/shape/order/size",
    )
    return dict(
        version=[1, 0],
        dtype=dtype,
        shape=shape,
        header_bytes=count + 10,
        size_bytes=size,
        numerical_load=False,
    )


def source_map(root=ROOT):
    names = {
        v
        for folder in ("src", "scripts", "tests")
        for v in (root / folder).rglob("*.py")
    }
    names.update(root / v for v in (CONFIG, PROMPT, "pyproject.toml"))
    require(all(not v.is_symlink() for v in names), "Source symlink")
    return {str(v.relative_to(root)): file_hash(v) for v in sorted(names)}


def native_build():
    """Installed selected NumPy/HDF/Blosc binary custody; no numerical imports."""
    result = {}
    for package in ("numpy", "h5py", "hdf5plugin"):
        distribution = importlib.metadata.distribution(package)
        for relative in distribution.files or ():
            name = str(relative)
            wanted = (
                (
                    package == "numpy"
                    and "_multiarray_umath" in name
                    and name.endswith(".so")
                )
                or (package == "h5py" and name.endswith((".so", ".dylib")))
                or (
                    package == "hdf5plugin"
                    and (
                        name.endswith("plugins/libh5blosc.dylib")
                        or name.endswith("/_config.py")
                    )
                )
            )
            if wanted:
                path = Path(distribution.locate_file(relative))
                result[package + ":" + name] = file_hash(path)
    require(
        any(k.startswith("numpy:") for k in result)
        and any(k.startswith("h5py:") for k in result)
        and any(k.endswith("libh5blosc.dylib") for k in result),
        "Installed native build coverage",
    )
    return result


def custody(root=ROOT):
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


def acceptance(path):
    path = Path(path).absolute()
    require(
        path.parent.parent == ROOT / "data/task0039-validation"
        and path.name == "software-acceptance.json",
        "Fresh acceptance namespace",
    )
    a = read(path)
    require(
        a["status"] == "software_accepted_synthetic_raw_feature_foundation"
        and a["source_map"] == source_map()
        and a["dependencies"] == dependencies()
        and a["config_sha256"] == file_hash(ROOT / CONFIG)
        and a["prompt_sha256"] == file_hash(ROOT / PROMPT),
        "Current final resolver source/config/dependencies",
    )
    require(a["native_build"] == native_build(), "Current installed native build")
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
        "Complete synthetic acceptance",
    )
    for r in a["checks"].values():
        require(
            file_hash(ROOT / r["log"]) == r["log_sha256"],
            "Validation evidence identity",
        )
    require(
        file_hash(ROOT / a["native_receipt_path"]) == a["native_receipt_sha256"],
        "Native synthetic evidence",
    )
    return a
