"""Task0025 strict metadata-only protocol and current-source acceptance."""

import hashlib
import platform

from raregate.benchmarks import protocol as p
from raregate.exports import onnx_protocol as old

ROOT = p.ROOT
CONFIG = "configs/benchmarks/pytorch_onnx_cpu_v1.json"
HASH = "65da398177b676a9effc8659bf465017407aacd825e6e38bdb921bc4cb70dc5a"
OUTPUT = "results/benchmarks/task0025-pytorch-onnx-cpu"
ACCEPTANCE = "data/task0025-software-acceptance.json"
PHASES = ("prepare", "PyTorch1", "ORT1", "PyTorch2", "ORT2", "PyTorch3", "ORT3")
BATCHES = (1, 8, 32, 128, 1024)
SCOPES = ("reconstruction", "score_decision", "adapter_decision")
fixed = old.fixed
source_map = old.source_map


def load(root=ROOT):
    spec = p.read(root / CONFIG)
    if p.digest(spec) != HASH:
        raise ValueError(
            "Unsupported strict Task0025 protocol/keys/selector/tolerance."
        )
    return spec


def metadata(root, spec):
    prior = old.load(root)
    old.frozen_metadata(root, prior)
    old.check_dependencies(root, prior)
    if platform.python_version() != spec["python"]:
        raise ValueError("Pinned Python drift.")
    if any(
        spec[k] != prior[k] for k in ("input", "model", "numerical", "dependencies")
    ):
        raise ValueError(
            "Frozen scientific/input/arithmetic/dependency contract drift."
        )
    for key in ("prior_source_file_sha256", "prior_evidence_file_sha256"):
        for name, digest in spec[key].items():
            if p.file_hash(fixed(root, name)) != digest:
                raise ValueError("Preserved prerequisite bytes changed: " + name)
    if p.file_hash(root / spec["prompt"]["path"]) != spec["prompt"]["file_byte_sha256"]:
        raise ValueError("Actual prompt changed.")
    receipt = p.read(root / spec["prior_receipt"])
    if (
        receipt["status"] != "completed_accepted"
        or receipt["real"]["status"] != "passed"
    ):
        raise ValueError("Accepted Task0024 prerequisite missing.")
    for graph in spec["graphs"].values():
        path = fixed(root, graph["path"])
        if (
            path.stat().st_size != graph["file_size_bytes"]
            or p.file_hash(path) != graph["file_byte_sha256"]
        ):
            raise ValueError("Accepted graph bytes/size mismatch.")
    _, header = old.input_file(root, prior)
    return dict(
        header=header,
        numerical_array_opened=False,
        prior_source_files=len(spec["prior_source_file_sha256"]),
    )


def input_path(root, spec, *, local=False):
    path = fixed(
        root, OUTPUT + "/prepare/input.npy" if local else spec["input"]["path"]
    )
    if (
        path.stat().st_size != 32896
        or p.file_hash(path) != spec["input"]["file_sha256"]
    ):
        raise ValueError("Frozen original/local bytes before numerical opening.")
    old.old.header(path)
    return path


def acceptance(root=ROOT):
    accepted = p.read(root / ACCEPTANCE)
    if (
        accepted.get("task") != "0025"
        or accepted.get("protocol_canonical_JSON_sha256") != HASH
        or accepted.get("protocol_file_byte_sha256") != p.file_hash(root / CONFIG)
        or accepted.get("source_file_sha256") != source_map(root)
        or type(accepted.get("full_passed")) is not int
        or accepted["full_passed"] <= 1111
        or accepted.get("portable_passed") != accepted["full_passed"]
        or accepted.get("quality")
        != dict(
            lint="passed",
            format="passed",
            dependencies="passed",
            CPU_smoke="passed",
            optional_integration="passed_actual_toy_runtime",
        )
        or accepted.get("guarded_synthetic_smoke", {}).get("status") != "passed"
    ):
        raise ValueError(
            "Current complete software/source/footprint acceptance required."
        )
    for record in accepted["validation_evidence"]:
        if p.file_hash(root / record["path"]) != record["file_byte_sha256"]:
            raise ValueError("Validation evidence changed.")
    return accepted


def build_hashes(text):
    return dict(
        raw_UTF8_byte_sha256=hashlib.sha256(text.encode()).hexdigest(),
        canonical_JSON_string_sha256=p.digest(text),
    )


def check_build(text, expected):
    if build_hashes(text) != expected:
        raise ValueError("Typed build text identity mismatch.")
