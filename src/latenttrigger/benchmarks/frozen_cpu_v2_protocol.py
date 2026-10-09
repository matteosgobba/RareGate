"""Strict stdlib v2 protocol, frozen lineage, NPY header and acceptance checks."""

import ast
import struct

from latenttrigger.benchmarks import ae_parity_protocol as old_review
from latenttrigger.benchmarks import protocol as p

ROOT = p.ROOT
CONFIG = "configs/benchmarks/frozen_cpu_v2.json"
HASH = "3727d8d81e8f62db920c4d418713117acd02466da31f71e55c7a8ba3424f98fa"
OUTPUT = "results/benchmarks/task0022-frozen-cpu-v2"
SYNTHETIC = "data/task0022-synthetic-study"
ACCEPTANCE = "data/task0022-synthetic-acceptance.json"
PHASES = p.PHASES


def load(root=ROOT):
    spec = p.read(root / CONFIG)
    if p.digest(spec) != HASH:
        raise ValueError("Unsupported v2 protocol/keys/policy/selector/override.")
    return spec


def fixed(root, relative):
    return old_review.fixed_path(root, relative)


def header(path):
    """Bounded stdlib-only NPY v1 header read; payload is not a numerical array."""
    with path.open("rb") as file:
        prefix = file.read(10)
        if prefix[:8] != b"\x93NUMPY\x01\x00" or len(prefix) != 10:
            raise ValueError("Expected frozen NPY1 header.")
        length = struct.unpack("<H", prefix[8:])[0]
        if length > 1024:
            raise ValueError("Bounded NPY header length exceeded.")
        value = ast.literal_eval(file.read(length).decode("latin1").strip())
    if (
        value != {"descr": "<f4", "fortran_order": False, "shape": (1024, 8)}
        or type(value["fortran_order"]) is not bool
        or type(value["shape"]) is not tuple
        or any(type(v) is not int for v in value["shape"])
    ):
        raise ValueError("Only little-endian contiguous nonpickle FP32[1024,8].")
    if 10 + length + 32768 != path.stat().st_size:
        raise ValueError("NPY size/header/payload relation mismatch.")
    return {
        "version": [1, 0],
        "header_bytes": 10 + length,
        "dtype": "<f4",
        "shape": [1024, 8],
        "fortran_order": False,
    }


def input_file(root, spec, *, local=False):
    relative = OUTPUT + "/prepare/input.npy" if local else spec["input"]["path"]
    expected = "results/benchmarks/task0020-frozen-cpu/prepare/input.npy"
    if spec["input"]["path"] != expected:
        raise ValueError(
            "Only frozen prepared input source; no population/store selector."
        )
    path = fixed(root, relative)
    if (
        path.stat().st_size != 32896
        or p.file_hash(path) != spec["input"]["file_sha256"]
    ):
        raise ValueError(
            "Prepared file-byte identity/size mismatch before numeric opening."
        )
    return path, header(path)


def metadata(root, spec):
    if (
        p.file_hash(root / spec["numerical"]["derivation_path"])
        != spec["numerical"]["derivation_file_sha256"]
    ):
        raise ValueError("Frozen derivation bytes changed.")
    old_review.verify_metadata(root, old_review.load(root))
    for name, expected in spec["historical_review_file_sha256"].items():
        if p.file_hash(fixed(root, name)) != expected:
            raise ValueError("Historical Task0020/0021 bytes changed: " + name)
    for name, expected in spec["historical_source_sha256"].items():
        if p.file_hash(root / name) != expected:
            raise ValueError("Historical source changed: " + name)
    for entry in (spec["prompt"], spec["brief"]):
        if p.file_hash(root / entry["path"]) != entry["file_sha256"]:
            raise ValueError("Prompt/brief binding changed.")
    brief = spec["brief"]
    if p.file_hash(root / brief["summary_path"]) != brief["summary_file_sha256"]:
        raise ValueError("Frozen review summary changed.")
    for model in spec["models"]:
        documents = {}
        for kind in ("config", "model", "results"):
            path = root / model[kind + "_path"]
            if p.file_hash(path) != model[kind + "_file_sha256"]:
                raise ValueError("Frozen model/config/results bytes changed.")
            documents[kind] = p.read(path)
        if p.digest(documents["config"]) != model["config_canonical_sha256"]:
            raise ValueError("Canonical config changed.")
        for kind in ("model", "results"):
            doc = documents[kind]
            if (
                p.digest(doc["scientific"]) != doc["scientific_sha256"]
                or doc["scientific_sha256"] != model[kind + "_scientific_sha256"]
            ):
                raise ValueError("Scientific model/results identity changed.")
        science = documents["model"]["scientific"]
        if (
            science["provenance"]["processed_scientific_sha256"]
            != spec["input"]["full_training_provenance_sha256"]
            or science["features"] != spec["input"]["channels"]
            or documents["results"]["scientific"]["model_scientific_sha256"]
            != model["model_scientific_sha256"]
            or [
                {"target_fpr": t["target_fpr"], "threshold": t["threshold"]}
                for t in documents["results"]["scientific"]["thresholds"]
            ]
            != model["thresholds"]
        ):
            raise ValueError(
                "Frozen scientific/calibration/input relationship changed."
            )
    _, h = input_file(root, spec)
    return {
        "prepared_header": h,
        "payload_file_byte_hash_verified": True,
        "numerical_array_opened": False,
        "historical_files_verified": len(spec["historical_review_file_sha256"]),
    }


def acceptance(root=ROOT, *, campaign=False):
    path = root / OUTPUT / "acceptance.json" if campaign else root / ACCEPTANCE
    a = p.read(path)
    study = a.get("synthetic_study", {})
    if (
        a.get("task") != "0022"
        or a.get("protocol_canonical_sha256") != HASH
        or a.get("source_sha256") != p.source_map(root)
        or type(a.get("pytest_passed")) is not int
        or a["pytest_passed"] <= 827
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
        or study.get("violations") != 0
        or study.get("effective_threads_verified") is not True
        or not 0 < study.get("worker_seconds", 0) <= 60
        or not 0 < study.get("peak_rss_bytes", 0) <= 1073741824
        or not 0 < study.get("native_heap_reserved_bytes", 0) <= 536870912
    ):
        raise ValueError(
            "Current complete v2 acceptance/footprint/source/policy validation required."
        )
    for evidence in a["validation_evidence"]:
        if p.file_hash(root / evidence["path"]) != evidence["file_sha256"]:
            raise ValueError("Acceptance evidence bytes changed.")
    return a
