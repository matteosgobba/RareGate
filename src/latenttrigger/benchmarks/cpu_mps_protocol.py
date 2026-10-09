"""Isolated strict Task0023 metadata/authorization; no numerical imports."""

import os
import sys

from latenttrigger.benchmarks import frozen_cpu_v2_protocol as cpu
from latenttrigger.benchmarks import protocol as p

ROOT = p.ROOT
CONFIG = "configs/benchmarks/frozen_cpu_mps_v1.json"
HASH = "8e9b4b72d2954799f8ba4de1cb469f36aab5cdb4f37b497188bdd7f29f608855"
OUTPUT = "results/benchmarks/task0023-cpu-mps"
PROOF = "data/task0023-device-proof"
ACCEPTANCE = "data/task0023-software-acceptance.json"
PHASES = ("prepare", "CPU1", "MPS1", "CPU2", "MPS2", "CPU3", "MPS3")


def load(root=ROOT):
    spec = p.read(root / CONFIG)
    if p.digest(spec) != HASH:
        raise ValueError("Unsupported device protocol/keys/tolerance/path/override.")
    return spec


def fixed(root, relative):
    return cpu.fixed(root, relative)


def input_file(root, spec, *, local=False):
    relative = OUTPUT + "/prepare/input.npy" if local else spec["input"]["path"]
    if (
        spec["input"]["path"]
        != "results/benchmarks/task0020-frozen-cpu/prepare/input.npy"
    ):
        raise ValueError(
            "Only original frozen prepared array; stores/populations refused."
        )
    path = fixed(root, relative)
    if (
        path.stat().st_size != 32896
        or p.file_hash(path) != spec["input"]["file_sha256"]
    ):
        raise ValueError("Frozen bounded file identity before numerical opening.")
    return path, cpu.header(path)


def metadata(root, spec, *, input_metadata=True):
    # Verify the accepted historical source subset, not a new acceptance for old routes.
    for key in ("files", "source_sha256"):
        for name, expected in spec["cpu_reference"][key].items():
            if p.file_hash(fixed(root, name)) != expected:
                raise ValueError("Accepted CPU reference changed: " + name)
    for name, expected in spec["historical_receipt_sha256"].items():
        if p.file_hash(fixed(root, name)) != expected:
            raise ValueError("Historical receipt/input bytes changed: " + name)
    for entry in (spec["prompt"], spec["policy"]):
        if p.file_hash(fixed(root, entry["path"])) != entry["file_sha256"]:
            raise ValueError("Frozen prompt/device policy changed.")
    cpu.metadata(root, cpu.load(root))
    previous_acceptance = p.read(root / "data/task0022-synthetic-acceptance.json")
    if previous_acceptance["runtime_versions"] != p.runtime_versions():
        raise ValueError("Accepted CPU reference runtime versions changed.")
    report = p.read(
        root / "results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json"
    )
    if (
        report.get("comparison_success") is not True
        or report.get("execution_status") != "complete_accepted_consumed_no_retry"
    ):
        raise ValueError("Accepted complete CPU reference required.")
    if spec["model"] != cpu.load(root)["models"][1]:
        raise ValueError(
            "Scientific model/scaler/feature/calibration identities changed."
        )
    result = {
        "old_cpu_source_entries": len(spec["cpu_reference"]["source_sha256"]),
        "old_receipt_files": len(spec["historical_receipt_sha256"]),
        "numerical_array_opened": False,
    }
    if input_metadata:
        _, result["prepared_header"] = input_file(root, spec)
    return result


def software_acceptance(root=ROOT, *, final_software_only=False):
    # The final repair acceptance cannot admit execution using the failed old proof.
    path = (
        "data/task0023-software-final-acceptance.json"
        if final_software_only
        else ACCEPTANCE
    )
    accepted = p.read(root / path)
    if (
        accepted.get("task") != "0023"
        or accepted.get("protocol_canonical_sha256") != HASH
        or accepted.get("source_sha256") != p.source_map(root)
        or accepted.get("runtime_versions") != p.runtime_versions()
        or type(accepted.get("pytest_passed")) is not int
        or accepted["pytest_passed"] <= 942
        or accepted.get("pytest_cases") != accepted["pytest_passed"]
        or accepted.get("portable_passed") != accepted["pytest_passed"]
        or accepted.get("quality_checks")
        != dict(
            ruff_lint="passed",
            ruff_format="passed",
            pip_check="passed",
            cpu_smoke="passed",
        )
        or accepted.get("physical_device_validated") is not False
    ):
        raise ValueError(
            "Current software validation/source freeze required; simulated tests are not device proof."
        )
    for row in accepted["validation_evidence"]:
        if p.file_hash(fixed(root, row["path"])) != row["file_sha256"]:
            raise ValueError("Software validation evidence changed.")
    return accepted


def environment(spec, current=None):
    env = dict(os.environ if current is None else current)
    if any(name in env for name in spec["forbidden_environment_overrides"]):
        raise ValueError("Allocator/operator/profiler overrides refused; no tuning.")
    env.update(spec["runtime"]["thread_environment_before_imports"])
    env.update(spec["device_environment_before_imports"])
    return env


def verify_environment(spec):
    expected = dict(
        spec["runtime"]["thread_environment_before_imports"],
        **spec["device_environment_before_imports"],
    )
    if any(os.environ.get(k) != v for k, v in expected.items()) or any(
        k in os.environ for k in spec["forbidden_environment_overrides"]
    ):
        raise ValueError(
            "Device/thread settings must precede imports; unsupported overrides."
        )
    if any(k in sys.modules for k in ("numpy", "torch", "sklearn", "h5py")):
        raise ValueError("Numerical imports before guarded fresh worker refused.")


def exclusive(root, relative):
    path = fixed(root, relative)
    path.mkdir(exist_ok=False)
    return path
