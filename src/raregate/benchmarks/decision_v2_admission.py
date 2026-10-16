"""Task0043 serialized software admission and distinct prompt-bound capabilities."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from raregate.benchmarks import decision_v2_protocol as p
from raregate.benchmarks.development_decision_contract import CHECKS, ROLE, Status


@dataclass(frozen=True)
class Context:
    root: Path
    owner: str = "0043"

    def __post_init__(self):
        p.require(
            self.owner == "0043" and self.root == self.root.resolve(),
            "Closed Task0043 context",
        )

    @property
    def namespace(self):
        return self.root / p.VALIDATION


class Mode(StrEnum):
    SYNTHETIC = "synthetic"
    OPERATIONAL = "operational"


def emit(context, directory, source, checks, native):
    p.require(directory.parent == context.namespace, "Producer namespace")
    record = dict(
        schema_version=1,
        status=Status.ACCEPTED.value,
        record_role=ROLE,
        identity=p.identity(context.root),
        source_map=source,
        dependencies=p.dependencies(),
        native_build=p.native_build(),
        checks=checks,
        native_receipt_path=str(native.relative_to(context.root)),
        native_receipt_sha256=p.file_hash(native),
        operational_reservation=False,
        execution_authorized=False,
        synthetic_only=True,
    )
    p.durable_json(directory / "software-acceptance.json", record, exclusive=True)
    return directory / "software-acceptance.json"


def evidence(path, context, directory):
    p.require(
        type(path) is str
        and not Path(path).is_absolute()
        and ".." not in Path(path).parts,
        "Safe evidence name",
    )
    f = p.fixed(context.root, path)
    p.require(f.is_relative_to(directory), "Owned record evidence")
    return f


def verify(record, context):
    record = Path(record).absolute()
    p.require(
        record.parent.parent == context.namespace
        and record.name == "software-acceptance.json",
        "Task0043 outer record namespace",
    )
    a = p.read(p.fixed(context.root, str(record.relative_to(context.root))))
    p.require(
        type(a) is dict
        and set(a)
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
        "Exact serialized software schema",
    )
    p.require(
        type(a["schema_version"]) is int
        and a["schema_version"] == 1
        and a["status"] == Status.ACCEPTED.value
        and a["record_role"] == ROLE
        and a["operational_reservation"] is False
        and a["execution_authorized"] is False
        and a["synthetic_only"] is True,
        "Software validation is not execution authority",
    )
    p.require(
        a["identity"] == p.identity(context.root)
        and a["source_map"] == p.source_map(context.root)
        and a["dependencies"] == p.dependencies()
        and a["native_build"] == p.native_build(),
        "Fresh Task0043 source/config/prompt/packages/build",
    )
    p.require(
        type(a["checks"]) is dict and set(a["checks"]) == CHECKS, "Complete checks"
    )
    for check in a["checks"].values():
        p.require(
            type(check) is dict
            and type(check.get("exit_code")) is int
            and check["exit_code"] == 0,
            "Successful check",
        )
        p.require(
            p.file_hash(evidence(check["log"], context, record.parent))
            == check["log_sha256"],
            "Check log identity",
        )
    native = evidence(a["native_receipt_path"], context, record.parent)
    p.require(
        p.file_hash(native) == a["native_receipt_sha256"], "Native evidence bytes"
    )
    w = p.read(native)
    p.require(
        w["identity"] == a["identity"]
        and w["source_map"] == a["source_map"]
        and w["dependencies"] == a["dependencies"]
        and w["status"] == "parent_accepted_synthetic_raw_decision"
        and w["synthetic_only"] is True
        and w["sleep_assertion"]["released"] is True
        and w["sleep_assertion"]["owned_assertion_absent"] is True,
        "Native synthetic identity/lifecycle",
    )
    return a


_SEAL = object()


@dataclass(frozen=True)
class Frozen:
    context: Context
    directory: Path
    record: Path
    mode: Mode
    record_sha256: str
    plan_sha256: str
    freeze_sha256: str
    seal: object


def roundtrip(record, context):
    f = p.fixed(record.parent, "admission-roundtrip.json")
    r = p.read(f)
    record_fields = verify(record, context)
    p.require(
        r["task"] == "0043"
        and r["status"]
        == "software_accepted_synthetic_development_raw_decision_roundtrip"
        and r["record_sha256"] == p.file_hash(record)
        and r["execution_authorized"] is False
        and r["identity"] == record_fields["identity"]
        and r["source_map"] == record_fields["source_map"]
        and r["dependencies"] == record_fields["dependencies"]
        and r["native_build"] == record_fields["native_build"],
        "Final emitted-record roundtrip required before operational freeze",
    )
    native = evidence(r["workflow_path"], context, record.parent)
    p.require(
        p.file_hash(native) == r["workflow_sha256"], "Roundtrip workflow identity"
    )
    w = p.read(native)
    p.require(
        w["identity"] == p.identity(context.root)
        and w["source_map"] == record_fields["source_map"]
        and w["dependencies"] == record_fields["dependencies"]
        and w["status"] == "parent_accepted_synthetic_raw_decision"
        and w["sleep_assertion"]["released"]
        and w["sleep_assertion"]["owned_assertion_absent"],
        "Final roundtrip parent acceptance",
    )
    return p.file_hash(f)


def fields(record, context, mode):
    admitted = verify(record, context)
    spec = p.load(context.root)
    p.require(isinstance(mode, Mode), "Typed scope, not a caller Boolean")
    return dict(
        identity=p.identity(context.root),
        mode=mode.value,
        record=str(record.relative_to(context.root)),
        record_sha256=p.file_hash(record),
        source_map=admitted["source_map"],
        dependencies=admitted["dependencies"],
        native_build=admitted["native_build"],
        inputs={k: spec[k] for k in ("membership", "raw", "golden")},
        models=spec["models"],
        expected=spec["expected"],
        limits=spec["limits"],
        authorization_prompt_sha256=spec["authorization_prompt_sha256"],
        roundtrip_sha256=roundtrip(record, context)
        if mode is Mode.OPERATIONAL
        else None,
        operational_allowances=1 if mode is Mode.OPERATIONAL else 0,
    )


def safe(directory, context):
    p.require(
        directory == directory.resolve()
        and directory.is_relative_to(context.namespace)
        and directory != context.namespace,
        "Closed admission freeze namespace",
    )


def prepare(record, directory, context, mode):
    record = Path(record).absolute()
    directory = Path(directory).absolute()
    safe(directory, context)
    plan = fields(record, context, mode)
    p.require(not directory.exists(), "Fresh one-winner freeze")
    directory.mkdir(parents=True)
    try:
        p.durable_json(directory / "admission-plan.json", plan, exclusive=True)
        p.durable_json(
            directory / "admission-freeze.json",
            dict(
                task="0043",
                identity=plan["identity"],
                mode=mode.value,
                plan_sha256=p.file_hash(directory / "admission-plan.json"),
                record_sha256=plan["record_sha256"],
            ),
            exclusive=True,
        )
        return reload(directory, context)
    except BaseException:
        for name in ("admission-plan.json", "admission-freeze.json"):
            f = directory / name
            if f.exists():
                f.rename(directory / ("rejected-" + name))
        raise


def reload(directory, context):
    directory = Path(directory).absolute()
    safe(directory, context)
    plan = p.read(p.fixed(directory, "admission-plan.json"))
    freeze = p.read(p.fixed(directory, "admission-freeze.json"))
    mode = Mode(plan["mode"])
    record = p.fixed(context.root, plan["record"])
    p.require(
        plan == fields(record, context, mode), "Immutable admitted plan/authorization"
    )
    p.require(
        freeze
        == dict(
            task="0043",
            identity=plan["identity"],
            mode=mode.value,
            plan_sha256=p.file_hash(directory / "admission-plan.json"),
            record_sha256=p.file_hash(record),
        ),
        "Immutable admission freeze",
    )
    return Frozen(
        context,
        directory,
        record,
        mode,
        p.file_hash(record),
        freeze["plan_sha256"],
        p.file_hash(directory / "admission-freeze.json"),
        _SEAL,
    )


def verify_frozen(frozen):
    p.require(
        isinstance(frozen, Frozen) and frozen.seal is _SEAL,
        "Only closed Task0043 capability",
    )
    p.require(
        reload(frozen.directory, frozen.context) == frozen,
        "Changed freeze/source/authorization before dispatch",
    )
    return frozen


def claim_fields(frozen):
    return dict(
        task="0043",
        mode=frozen.mode.value,
        record_sha256=frozen.record_sha256,
        freeze_sha256=frozen.freeze_sha256,
    )


def dispatch(frozen, executor):
    verify_frozen(frozen)
    p.require(
        not (frozen.context.root / p.OUTPUT / "prerequisite-attempt.json").exists()
        if frozen.mode is Mode.OPERATIONAL
        else not (frozen.directory / "copied-consumed-marker.json").exists(),
        "One unconsumed allowance",
    )
    p.durable_json(
        frozen.directory / "launch-claim.json", claim_fields(frozen), exclusive=True
    )
    verify_frozen(frozen)
    return executor(frozen)


def launch(record, directory, context, mode, executor=None):
    from raregate.benchmarks.decision_v2_native import run

    return dispatch(prepare(record, directory, context, mode), executor or run)
