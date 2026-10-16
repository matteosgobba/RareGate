"""Strict synthetic scope and raw-byte prerequisites; standard library only."""

import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CONFIG = "configs/research/controlled_activation_synthetic_v1.json"
DESIGN = "configs/research/controlled_follow_up_v1.json"
DESIGN_FILES = (
    "docs/prompts/0034-controlled-follow-up-protocol.md",
    "docs/handoffs/0034-controlled-follow-up-protocol.md",
    "docs/controlled-follow-up-protocol.md",
    DESIGN,
    "results/tables/final/task0034-confirmation-source-registry.csv",
    "results/tables/final/task0034-controlled-follow-up-summary.json",
)
ARMS = ("nonlinear", "linear")
SEEDS = (1729, 1730, 1731)
ORDER = tuple((arm, seed) for seed in SEEDS for arm in ARMS)
FEATURES = (
    "multiplicity",
    "scalar_pt",
    "max_pt",
    "pt_balance",
    "weighted_eta_mean",
    "weighted_eta_std",
    "pt_concentration",
    "massless_event_mass",
)
ROLES = (
    "train_background",
    "validation_selection_background",
    "validation_calibration_background",
)
ALPHAS = (0.1, 0.05, 0.01, 0.001)
ADAM = dict(
    betas=[0.9, 0.999],
    eps=1e-8,
    weight_decay=0,
    amsgrad=False,
    foreach=None,
    maximize=False,
    capturable=False,
    differentiable=False,
    fused=None,
    decoupled_weight_decay=False,
)
TRAINING = dict(
    optimizer="adam",
    learning_rate=0.001,
    batch_size=4096,
    max_epochs=1000,
    early_stopping_patience=15,
    min_delta=0.0,
    device="cpu",
    num_workers=0,
    num_threads=1,
    deterministic_algorithms=True,
    loss="mean_squared_reconstruction_error",
    initialization="pytorch_linear_default",
    adam_defaults=ADAM,
)
PROFILE = dict(
    name="tiny_two_epoch_v1",
    train_rows=17,
    selection_rows=13,
    calibration_rows=21,
    background_rows=127,
    signal_rows=131,
    epochs=2,
    batch_size=4096,
    steps_per_arm_seed_max=2,
)
LIMITS = dict(
    prerequisite_seconds=30,
    worker_seconds=60,
    finalization_seconds=15,
    whole_seconds=120,
    cleanup_seconds=2,
    worker_RSS_bytes=2**30,
    native_reserved_bytes=512 * 2**20,
    controller_RSS_bytes=128 * 2**20,
    guard_journal_bytes=64 * 2**20,
    worker_log_bytes=2**20,
    storage_bytes=128 * 2**20,
    optimizer_steps_max=12,
)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def file_hash(path):
    require(
        path.is_file() and not path.is_symlink(), "Regular nonsymlink file required"
    )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    require(
        path.stat().st_size <= 2**20 and not path.is_symlink(), "Bounded regular JSON"
    )

    def pairs(items):
        d = {}
        for k, v in items:
            require(k not in d, "Duplicate JSON key")
            d[k] = v
        return d

    return json.loads(
        path.read_text(),
        object_pairs_hook=pairs,
        parse_constant=lambda _: require(False, "Nonfinite JSON"),
    )


def durable_json(path, value, *, exclusive=False):
    import os
    import uuid

    data = json.dumps(value, indent=2, allow_nan=False) + "\n"
    require(len(data.encode()) <= 2**20, "Bounded JSON output")
    temporary = path.parent / ("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    with temporary.open("x") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        if exclusive:
            os.link(temporary, path)
            temporary.unlink()
        else:
            os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def validate_config(spec, root=ROOT):
    expected_keys = {
        "schema_version",
        "scope",
        "operational_execution",
        "PCA_three",
        "design_files",
        "design_digest",
        "arms",
        "seeds",
        "features",
        "layers",
        "parameters",
        "forward_dtype",
        "score_dtype",
        "training_contract",
        "synthetic_profile",
        "limits",
        "dependencies",
    }
    require(type(spec) is dict and set(spec) == expected_keys, "Strict research schema")
    require(
        type(spec["schema_version"]) is int
        and spec["schema_version"] == 1
        and spec["scope"] == "synthetic_only"
        and spec["operational_execution"] is False
        and spec["PCA_three"] is False,
        "Synthetic-only scope; PCA control disabled",
    )
    for key, expected in dict(
        arms=list(ARMS),
        seeds=list(SEEDS),
        features=list(FEATURES),
        layers=[8, 6, 3, 6, 8],
        parameters=155,
        forward_dtype="float32",
        score_dtype="float64",
        training_contract=TRAINING,
        synthetic_profile=PROFILE,
        limits=LIMITS,
    ).items():
        require(digest(spec[key]) == digest(expected), "Frozen research field: " + key)
    require(
        set(spec["design_files"]) == set(DESIGN_FILES), "Design prerequisite allowlist"
    )
    for name, sha in spec["design_files"].items():
        require(file_hash(root / name) == sha, "Altered Task0034 design: " + name)
    design = read(root / DESIGN)
    require(
        digest(design) == spec["design_digest"]
        and design["status"] == "design_only"
        and design["execution_authorized"] is False
        and design["confirmation"]["source_accepted"] is False,
        "Unchanged unaccepted design",
    )
    require(
        set(spec["dependencies"])
        == {"Python", "Torch", "NumPy", "torch_build_sha256", "adam_source_sha256"},
        "Exact dependency fields",
    )
    require(
        spec["dependencies"]["Python"] == sys.version
        and spec["dependencies"]["Torch"] == importlib.metadata.version("torch")
        and spec["dependencies"]["NumPy"] == importlib.metadata.version("numpy"),
        "Incompatible installed dependencies",
    )
    return spec


def load_config(root=ROOT):
    return validate_config(read(root / CONFIG), root)


def runtime_versions():
    return dict(
        Python=sys.version,
        platform=platform.platform(),
        packages=dict(
            sorted(
                (d.metadata["Name"], d.version)
                for d in importlib.metadata.distributions()
                if d.metadata.get("Name")
            )
        ),
    )


def source_map(root=ROOT):
    paths = {
        p
        for folder in ("src", "scripts", "tests", "configs")
        for p in (root / folder).rglob("*")
        if p.is_file() and p.suffix in (".py", ".json") and "__pycache__" not in p.parts
    }
    paths.update(
        root / n
        for n in (
            *DESIGN_FILES,
            "pyproject.toml",
            "docs/prompts/0035-controlled-activation-synthetic-foundation.md",
        )
    )
    return {str(p.relative_to(root)): file_hash(p) for p in sorted(paths)}
