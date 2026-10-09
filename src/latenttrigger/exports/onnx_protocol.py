"""Strict stdlib protocol, additive stack and frozen metadata; no numerical IO."""

import importlib.metadata as metadata
import sys

from latenttrigger.benchmarks import frozen_cpu_v2_protocol as old
from latenttrigger.benchmarks import protocol as p

ROOT = p.ROOT
CONFIG = "configs/exports/frozen_ae_onnx_cpu_v1.json"
HASH = "b4508bfd5ec1663da9b1649459bbbcef671ebd51c7c6584ccd0d80b7f52c9ab1"
OUTPUT = "results/benchmarks/task0024-ae-onnx-cpu"
ACCEPTANCE = "data/task0024-software-acceptance.json"


def load(root=ROOT):
    spec = p.read(root / CONFIG)
    if p.digest(spec) != HASH:
        raise ValueError(
            "Unsupported strict export protocol/keys/opset/tolerance/input/output override."
        )
    return spec


def fixed(root, relative):
    return old.fixed(root, relative)


def input_file(root, spec):
    if (
        spec["input"]["path"]
        != "results/benchmarks/task0020-frozen-cpu/prepare/input.npy"
    ):
        raise ValueError(
            "Only original frozen prepared input, no stores/populations/truth/test selectors."
        )
    path = fixed(root, spec["input"]["path"])
    if (
        path.stat().st_size != 32896
        or p.file_hash(path) != spec["input"]["file_sha256"]
    ):
        raise ValueError("Input byte identity/size before numerical opening.")
    return path, old.header(path)


def dependency_versions():
    return {
        d.metadata["Name"].lower().replace("_", "-"): d.version
        for d in metadata.distributions()
    }


def check_dependencies(root, spec):
    dep = spec["dependencies"]
    actual = dependency_versions()
    for name, version in {
        **dep["existing_distributions"],
        **dep["added_versions"],
    }.items():
        if actual.get(name) != version:
            raise ValueError("Pinned additive optional/core package drift: " + name)
    for path, digest in dep["core_package_file_sha256"].items():
        if p.file_hash(root / path) != digest:
            raise ValueError("Preserved core package bytes changed: " + path)
    if (
        p.file_hash(root / dep["path"]) != dep["file_byte_sha256"]
        or p.file_hash(root / "pyproject.toml") != dep["pyproject_file_byte_sha256"]
    ):
        raise ValueError("Optional dependency declaration/record changed.")
    return dict(
        primary={name: actual[name] for name in ("onnx", "onnxruntime", "onnxscript")},
        baseline_versions_preserved=True,
        core_files_preserved=True,
    )


def frozen_metadata(root, spec):
    for key in (
        "historical_source_file_sha256",
        "historical_file_sha256",
        "prerequisite_files",
    ):
        for name, digest in spec[key].items():
            if p.file_hash(fixed(root, name)) != digest:
                raise ValueError("Preserved historical identity changed: " + name)
    for entry in (spec["prompt"], spec["numerical"]):
        if p.file_hash(root / entry["path"]) != entry["file_byte_sha256"]:
            raise ValueError("Prompt/numerical derivation changed.")

    old.metadata(root, old.load(root))
    if spec["model"] != old.load(root)["models"][1]:
        raise ValueError("Frozen AE/calibration/scaler/feature contracts changed.")
    _, header = input_file(root, spec)
    return dict(
        header=header,
        numerical_array_opened=False,
        historical_source_files=len(spec["historical_source_file_sha256"]),
        historical_evidence_files=len(spec["historical_file_sha256"]),
    )


def source_map(root=ROOT):
    result = p.source_map(root)
    result["pyproject.toml"] = p.file_hash(root / "pyproject.toml")
    result["configs/dependencies/onnx_cpu_v1.json"] = p.file_hash(
        root / "configs/dependencies/onnx_cpu_v1.json"
    )
    return result


def acceptance(root=ROOT):
    accepted = p.read(root / ACCEPTANCE)
    if (
        accepted.get("task") != "0024"
        or accepted.get("protocol_canonical_JSON_sha256") != HASH
        or accepted.get("source_file_sha256") != source_map(root)
        or type(accepted.get("full_passed")) is not int
        or accepted["full_passed"] <= 1033
        or accepted.get("full_cases") != accepted["full_passed"]
        or accepted.get("portable_passed") != accepted["full_passed"]
        or accepted.get("optional_integration")
        != "passed_actual_synthetic_export_runtime"
        or accepted.get("quality")
        != dict(
            lint="passed", format="passed", dependencies="passed", CPU_smoke="passed"
        )
    ):
        raise ValueError(
            "Complete current software/source/optional integration acceptance required."
        )
    if (
        accepted["guarded_synthetic_smoke"]["status"] != "passed"
        or accepted["guarded_synthetic_smoke"]["resources"]["latched_error"] is not None
        or accepted["guarded_synthetic_smoke"]["resources"]["owned_thread_alive"]
    ):
        raise ValueError(
            "Benchmark-specific synthetic exporter/runtime footprint/cleanup invalid."
        )
    for record in accepted["validation_evidence"]:
        if p.file_hash(root / record["path"]) != record["file_byte_sha256"]:
            raise ValueError("Validation evidence changed.")
    return accepted


def refuse_early_imports():
    if any(
        name in sys.modules
        for name in ("numpy", "torch", "onnx", "onnxruntime", "onnxscript")
    ):
        raise ValueError("Numeric/optional imports before guarded fresh worker.")
