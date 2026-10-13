"""Separate Task0040 payload authorization; Task0039 remains metadata-only."""

import hashlib
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
    native_build as native_build,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    read as read,
)
from latenttrigger.benchmarks.development_raw_protocol import (
    require as require,
)

CONFIG = "configs/benchmarks/development_raw_measurement_v1.json"
PROMPT = "docs/prompts/0040-development-raw-feature-measurement.md"
OUTPUT = "results/benchmarks/task0040-development-raw-features"
VALIDATION = "data/task0040-validation"
CONFIG_HASH = "089b30f3168497e87cadf698880920966ae3a4641f5ca9415684c7730881a396"


def load(root=ROOT):
    spec = read(root / CONFIG)
    require(
        digest(spec) == CONFIG_HASH and spec["task"] == "0040", "Fixed payload protocol"
    )
    require(
        spec["design"]["counts"] == old.load(root)["future"]["counts"],
        "Unchanged design counts",
    )
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
        )
    )
    require(all(not v.is_symlink() for v in names), "No source symlink")
    return {str(v.relative_to(root)): file_hash(v) for v in sorted(names)}


def custody(root=ROOT):
    spec = load(root)
    old.custody(
        root
    )  # text/header/bytes only, not old acceptance or consumed execution
    for name, sha in spec["byte_pins"].items():
        require(
            file_hash(fixed(root, name)) == sha,
            "Pinned historical source changed: " + name,
        )
    summary = read(
        root / "results/tables/final/task0039-development-raw-feature-summary.json"
    )
    base = root / summary["provenance"]["operational_directory"]
    workflow = read(base / "workflow.json")
    accepted = read(base / "parent-acceptance.json")
    require(
        workflow["status"]
        == accepted["status"]
        == "parent_accepted_membership_metadata_resolution"
        and accepted["workflow_sha256"] == file_hash(base / "workflow.json")
        and workflow["access"]["selected_IDs"] == 1024
        and workflow["access"]["membership_loads"] == 1,
        "Accepted consumed resolver lineage",
    )
    return dict(status="byte_header_scientific_lineage_verified", numerical_loads=0)


def acceptance(path):
    path = Path(path).absolute()
    require(
        path.parent.parent == ROOT / VALIDATION
        and path.name == "software-acceptance.json",
        "Fresh acceptance namespace",
    )
    a = read(fixed(path.parent, path.name))
    require(
        a["status"] == "software_accepted_synthetic_development_payload"
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
