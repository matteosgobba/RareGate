"""Separate Task0041 payload authorization; Task0039 remains metadata-only."""

import hashlib
import importlib.metadata
import os
import struct
from pathlib import Path

from latenttrigger.benchmarks import development_raw_protocol as old
from latenttrigger.benchmarks.development_raw_protocol import (
    CACHE as CACHE,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    GOLDEN as GOLDEN,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    MEMBERSHIP as MEMBERSHIP,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    RAW as RAW,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    ROOT as ROOT,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    dependencies as dependencies,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    digest as digest,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    durable_json as durable_json,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    file_hash as file_hash,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    fixed as fixed,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    header as header,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    native_build as raw_native_build,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    read as read,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    require as require,
)

CONFIG = "configs/benchmarks/development_raw_decision_v1.json"
PROMPT = "docs/prompts/0041-development-raw-decision-measurement.md"
OUTPUT = "results/benchmarks/task0041-development-raw-decisions"
VALIDATION = "data/task0041-validation"
CONFIG_HASH = "8fe900058437bd4152f0321fd09aa5ecc5f57ce3bbde769e78b6b40ec93f0ec1"


def load(root=ROOT):
    spec = read(root / CONFIG)
    require(
        digest(spec) == CONFIG_HASH and spec["task"] == "0041", "Fixed payload protocol"
    )
    from latenttrigger.benchmarks.development_decision_planning import counts

    require(spec["expected"] == counts(), "Derived unchanged joint matrix/accounting")
    return spec


def source_map(root=ROOT):
    names = {v for d in ("src", "scripts", "tests") for v in (root / d).rglob("*.py")}
    names.update(
        root / n
        for n in (
            CONFIG,
            PROMPT,
            "pyproject.toml",
            old.CONFIG,
            old.PROMPT,
            "results/tables/final/task0039-development-raw-feature-summary.json",
            "configs/benchmarks/development_raw_measurement_v1.json",
            "configs/benchmarks/prepared_batch_service_v1.json",
            "results/tables/final/task0040-development-raw-feature-summary.json",
        )
    )
    require(all(not v.is_symlink() for v in names), "No source symlink")
    return {str(v.relative_to(root)): file_hash(v) for v in sorted(names)}


def custody(root=ROOT):
    from latenttrigger.benchmarks import development_payload_protocol as prior
    from latenttrigger.benchmarks import prepared_service_protocol as service

    spec = load(root)
    prior.custody(
        root
    )  # byte/header/scientific metadata, never old grants/acceptance validation
    service.custody(root)  # original model/scientific/calibration metadata only
    require(
        spec["models"] == service.load(root)["models"]
        and spec["channels"] == service.load(root)["input"]["channels"]
        and spec["numerical"] == service.load(root)["numerical"],
        "Unchanged frozen model/arithmetic registry",
    )
    for name, sha in spec["byte_pins"].items():
        require(
            file_hash(fixed(root, name)) == sha,
            "Changed historical/model/input pin: " + name,
        )
    for task, item in spec["historical_acceptances"].items():
        path = fixed(root, item["path"])
        require(
            file_hash(path) == item["sha256"], "Original acceptance identity " + task
        )
        accepted = read(path)
        # Newly added files are not retroactively members of an old source map.
        for name, sha in accepted["source_map"].items():
            require(
                file_hash(fixed(root, name)) == sha,
                "Original historical source changed: " + name,
            )
    summary = read(
        root / "results/tables/final/task0040-development-raw-feature-summary.json"
    )
    base = root / summary["provenance"]["operational_directory"]
    workflow = read(base / "workflow.json")
    accepted = read(base / "parent-acceptance.json")
    require(
        workflow["status"]
        == accepted["status"]
        == "parent_accepted_development_raw_feature_measurement"
        and accepted["workflow_sha256"] == file_hash(base / "workflow.json"),
        "Task0040 accepted/consumed lineage",
    )
    return dict(
        status="all_historical_original_maps_and_scientific_lineage_verified",
        numerical_loads=0,
        model_instantiations=0,
    )


def stream_hash(path):
    sha = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(2**20):
            sha.update(chunk)
    return sha.hexdigest()


def native_build():
    files = raw_native_build()
    dist = importlib.metadata.distribution("torch")
    for item in dist.files or ():
        name = str(item)
        if name.endswith((".so", ".dylib")) or name in (
            "torch/__config__.py",
            "torch/version.py",
        ):
            path = Path(dist.locate_file(item))
            files["torch:" + name] = stream_hash(path)
    require(
        any("libtorch_cpu" in name for name in files)
        and any(name.startswith("torch:") and "/_C." in name for name in files),
        "Torch CPU extension/library coverage",
    )
    return dict(
        files=files,
        torch_config_canonical_JSON_string_sha256=load()["numerical"][
            "runtime_torch_build_sha256"
        ],
        torch_version=importlib.metadata.version("torch"),
        build_hash_convention="canonical_JSON_string_not_raw_UTF8",
    )


def acceptance(path):
    path = Path(path).absolute()
    require(
        path.parent.parent == ROOT / VALIDATION
        and path.name == "software-acceptance.json",
        "Fresh acceptance namespace",
    )
    a = read(fixed(path.parent, path.name))
    require(
        a["status"] == "software_accepted_synthetic_development_decision"
        and a["source_map"] == source_map()
        and a["dependencies"] == dependencies()
        and a["native_build"] == native_build()
        and a["config_sha256"] == file_hash(ROOT / CONFIG)
        and a["prompt_sha256"] == file_hash(ROOT / PROMPT),
        "Current source/config/build/prompt acceptance",
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
        "All checks required",
    )
    for v in a["checks"].values():
        require(
            file_hash(fixed(ROOT, v["log"])) == v["log_sha256"],
            "Validation log identity",
        )
    require(
        file_hash(fixed(ROOT, a["native_receipt_path"])) == a["native_receipt_sha256"],
        "Native evidence identity",
    )
    return a


def hash_raw(path, spec, audit, persist, poll):
    """Bounded stdlib custody: parent never imports numerical/HDF libraries."""
    require(
        path.absolute() == path.resolve() and path.stat().st_size == spec["size_bytes"],
        "Raw byte source",
    )
    require(audit.get("attempts", 0) == 0, "One pass in each fixed custody stage")
    audit.update(attempts=1, passes=0, bytes=0, inflight=True)
    persist()
    sha = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(2**20):
            poll()
            sha.update(block)
            audit["bytes"] += len(block)
            require(audit["bytes"] <= spec["size_bytes"], "Raw growth during custody")
            if audit["bytes"] % (64 * 2**20) == 0:
                persist()
    audit.update(passes=1, inflight=False, sha256=sha.hexdigest())
    persist()
    require(
        audit["bytes"] == spec["size_bytes"] and sha.hexdigest() == spec["file_sha256"],
        "Raw whole-file identity",
    )


def validate_grant(directory, token, clock):
    grant = read(fixed(directory, "grant.json"))
    base = directory.parent
    require(
        directory == directory.resolve()
        and grant["parent_pid"] == os.getppid()
        and grant["token"] == token
        and len(token) == 32,
        "Owned parent grant/token",
    )
    require(
        grant["phase"] in ("repetition1", "repetition2", "repetition3", "reporting")
        and directory.name == grant["phase"]
        and clock() < grant["operation_deadline"],
        "Phase/deadline grant",
    )
    require(
        (grant["synthetic_only"] and base.is_relative_to(ROOT / VALIDATION))
        or (not grant["synthetic_only"] and base.parent == ROOT / OUTPUT),
        "Grant namespace",
    )
    expected_path = directory / "fixture.h5" if grant["synthetic_only"] else ROOT / RAW
    require(
        grant["payload_path"] == str(expected_path)
        and grant["prefix_sha256"]
        == (
            hashlib.sha256(
                b"".join(struct.pack("<q", 3 * i) for i in range(1024))
            ).hexdigest()
            if grant["synthetic_only"]
            else load()["membership"]["selected_sha256"]
        ),
        "Exact phase payload path/prefix",
    )
    plan = read(base / "plan.json")
    require(
        file_hash(base / "plan.json") == grant["plan_sha256"]
        and grant["source_map"] == plan["source_map"] == source_map()
        and grant["dependencies"] == plan["dependencies"] == dependencies()
        and plan["prompt_sha256"] == file_hash(ROOT / PROMPT)
        and plan["native_build"] == native_build(),
        "Frozen grant/source/dependency/build",
    )
    if not grant["synthetic_only"]:
        anchor = read(ROOT / OUTPUT / "attempt.json")
        require(
            anchor["directory"] == str(base.relative_to(ROOT))
            and anchor["plan_sha256"] == grant["plan_sha256"],
            "Durable one-session anchor",
        )
        require(
            grant["inputs"] == {k: load()[k] for k in ("membership", "raw", "golden")},
            "Exact payload input grant",
        )
    require(
        grant["models"] == plan["models"] == load()["models"],
        "Exact candidate/threshold grant",
    )
    require(
        grant["expected"] == plan["expected"] == load()["expected"],
        "Exact per-phase operation budgets",
    )
    durable_json(
        directory / "claim.json",
        dict(token_sha256=hashlib.sha256(token.encode()).hexdigest(), pid=os.getpid()),
        exclusive=True,
    )
    return grant, PayloadPermit(grant, _PERMIT_SEAL)


_PERMIT_SEAL = object()


class PayloadPermit:
    def __init__(self, grant, seal):
        require(seal is _PERMIT_SEAL, "No unauthenticated payload permit")
        self.phase = grant["phase"]
        self.pid = os.getpid()
        self.deadline = grant["operation_deadline"]
        self.path = str(Path(grant["payload_path"]).absolute())
        self.prefix = grant["prefix_sha256"]
        self.models = grant["models"]
        self.expected = grant["expected"]


def expected_parameter_hash(artifact):
    """Exact static parameter-byte binding, not a model constructor/forward."""
    science = artifact["scientific"]
    require(
        digest(science) == artifact["scientific_sha256"],
        "Source scientific identity before tensor binding",
    )

    def packed(values, code):
        if isinstance(values, list):
            return b"".join(packed(v, code) for v in values)
        return struct.pack("<" + code, values)

    if science["model_type"] == "compact_autoencoder":
        return digest(
            {
                v["name"]: hashlib.sha256(packed(v["values"], "f")).hexdigest()
                for v in science["parameters"]
            }
        )
    require(science["model_type"] == "pca_reconstruction", "Only fixed tensor families")
    return digest(
        dict(
            arrays={
                k: hashlib.sha256(packed(science[k], "d")).hexdigest()
                for k in (
                    "mean",
                    "components",
                    "explained_variance",
                    "explained_variance_ratio",
                )
            },
            k=science["selected_k"],
            target=science["variance_target"],
            training_count=science["training_count"],
        )
    )
