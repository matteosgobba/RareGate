"""Strict emitted-record contract. Software admission never grants real execution."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from latenttrigger.benchmarks import development_decision_protocol as p


class Status(StrEnum):
    ACCEPTED = "software_accepted_synthetic_development_raw_decision"


REPAIR_PROMPT = "docs/prompts/0042-development-decision-admission-repair.md"
CHECKS = frozenset(
    (
        "focused",
        "full",
        "portable",
        "lint",
        "format",
        "dependencies",
        "native_synthetic",
    )
)
ROLE = "software_validation_not_execution_authorization"


@dataclass(frozen=True)
class Context:
    root: Path
    owner: str = "0041"

    def __post_init__(self):
        p.require(self.owner in ("0041", "0042"), "Explicit validation owner")
        p.require(self.root == self.root.resolve(), "Safe context root")

    @property
    def namespace(self):
        return self.root / ("data/task" + self.owner + "-validation")

    @property
    def prompt(self):
        return REPAIR_PROMPT if self.owner == "0042" else p.PROMPT


def identity(context, *, synthetic):
    p.require(
        context.owner != "0042" or synthetic is True,
        "Repair admits only synthetic fixtures",
    )
    spec = p.load(context.root)
    return dict(
        task=spec["task"],
        protocol_kind=spec["kind"],
        scope=spec["scope"],
        kind="synthetic_fixed_matrix"
        if synthetic
        else "one_development_raw_decision_measurement",
        validation_owner=context.owner,
        config_sha256=p.file_hash(p.fixed(context.root, p.CONFIG)),
        prompt_sha256=p.file_hash(p.fixed(context.root, p.PROMPT)),
        validation_prompt_sha256=p.file_hash(p.fixed(context.root, context.prompt)),
    )


def produce(context, *, source, dependencies, build, checks, native):
    """Actual producer used by both drivers; serialization follows in emit()."""
    return dict(
        schema_version=1,
        status=Status.ACCEPTED.value,
        record_role=ROLE,
        identity=identity(context, synthetic=True),
        source_map=source,
        dependencies=dependencies,
        native_build=build,
        checks=checks,
        native_receipt_path=str(native.relative_to(context.root)),
        native_receipt_sha256=p.file_hash(native),
        operational_reservation=False,
        execution_authorized=False,
        synthetic_only=True,
    )


def emit(path, context, **bindings):
    p.require(path.parent.parent == context.namespace, "Producer owned namespace")
    p.require(path.name == "software-acceptance.json", "Producer record name")
    record = produce(context, **bindings)
    p.durable_json(path, record, exclusive=True)
    return path


def verify(path, context):
    path = Path(path).absolute()
    p.require(
        path.parent.parent == context.namespace
        and path.name == "software-acceptance.json",
        "Fresh acceptance namespace",
    )
    a = p.read(p.fixed(context.root, str(path.relative_to(context.root))))
    p.require(isinstance(a, dict), "Record object")
    p.require(
        set(a)
        == {
            "schema_version",
            "status",
            "record_role",
            "identity",
            "source_map",
            "dependencies",
            "native_build",
            "checks",
            "native_receipt_path",
            "native_receipt_sha256",
            "operational_reservation",
            "execution_authorized",
            "synthetic_only",
        },
        "Exact software record schema",
    )
    p.require(
        type(a["schema_version"]) is int
        and a["schema_version"] == 1
        and a["status"] == Status.ACCEPTED.value
        and a["record_role"] == ROLE
        and a["operational_reservation"] is False
        and a["execution_authorized"] is False
        and a["synthetic_only"] is True,
        "Typed status/role/synthetic-only contract",
    )
    p.require(
        a["identity"] == identity(context, synthetic=True)
        and a["source_map"] == p.source_map(context.root)
        and a["dependencies"] == p.dependencies()
        and a["native_build"] == p.native_build(),
        "Current source/config/build/prompt acceptance",
    )
    p.require(
        isinstance(a["checks"], dict) and set(a["checks"]) == CHECKS,
        "All checks required",
    )
    for v in a["checks"].values():
        p.require(
            isinstance(v, dict)
            and type(v.get("exit_code")) is int
            and v["exit_code"] == 0,
            "Successful check",
        )
        log = owned_evidence(context, path.parent, v["log"])
        p.require(p.file_hash(log) == v["log_sha256"], "Validation log identity")
    native = owned_evidence(context, path.parent, a["native_receipt_path"])
    p.require(
        p.file_hash(native) == a["native_receipt_sha256"], "Native evidence identity"
    )
    workflow = p.read(native)
    p.require(
        workflow["status"] == "parent_accepted_synthetic_raw_decision"
        and workflow["synthetic_only"] is True
        and workflow["reserved"] is False
        and workflow["identity"] == a["identity"]
        and workflow["sleep_assertion"]["released"] is True,
        "Native role/identity/lifecycle evidence",
    )
    return a


def owned_evidence(context, directory, name):
    p.require(
        isinstance(name, str)
        and not Path(name).is_absolute()
        and ".." not in Path(name).parts,
        "Safe relative evidence",
    )
    path = p.fixed(context.root, name)
    p.require(path.is_relative_to(directory), "Evidence belongs to emitted record")
    return path
