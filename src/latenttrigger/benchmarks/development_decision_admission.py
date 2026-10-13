"""Checked software-only coordinator: admission → atomic freeze → one dispatch."""

from dataclasses import dataclass
from pathlib import Path

from latenttrigger.benchmarks import development_decision_protocol as p
from latenttrigger.benchmarks.development_decision_contract import Context, identity

_SEAL = object()


@dataclass(frozen=True)
class Frozen:
    context: Context
    record: Path
    directory: Path
    record_sha256: str
    plan_sha256: str
    freeze_sha256: str
    seal: object


def safe_directory(directory, context):
    p.require(
        directory == directory.resolve()
        and directory.is_relative_to(context.namespace),
        "Synthetic freeze namespace",
    )
    p.require(
        directory != context.namespace and not directory.is_symlink(),
        "Owned synthetic directory",
    )


def prepare(record, directory, context):
    """No controller effects occur here; failed publication retains rejected evidence."""
    record, directory = Path(record).absolute(), Path(directory).absolute()
    safe_directory(directory, context)
    p.acceptance(record, context=context)
    p.require(not directory.exists(), "Fresh synthetic freeze, no duplicate launch")
    directory.mkdir(parents=True)
    try:
        plan = dict(
            identity=identity(context, synthetic=True),
            record=str(record.relative_to(context.root)),
            record_sha256=p.file_hash(record),
            source_map=p.source_map(context.root),
            dependencies=p.dependencies(),
            native_build=p.native_build(),
            synthetic_only=True,
            execution_authorized=False,
        )
        p.durable_json(directory / "admission-plan.json", plan, exclusive=True)
        freeze = dict(
            identity=plan["identity"],
            record_sha256=plan["record_sha256"],
            plan_sha256=p.file_hash(directory / "admission-plan.json"),
            synthetic_only=True,
            execution_authorized=False,
        )
        p.durable_json(directory / "admission-freeze.json", freeze, exclusive=True)
        return load(directory, context)
    except BaseException:
        for name in ("admission-plan.json", "admission-freeze.json"):
            path = directory / name
            if path.exists():
                path.rename(directory / ("rejected-" + name))
        raise


def load(directory, context):
    directory = Path(directory).absolute()
    safe_directory(directory, context)
    plan = p.read(p.fixed(directory, "admission-plan.json"))
    freeze = p.read(p.fixed(directory, "admission-freeze.json"))
    record = p.fixed(context.root, plan["record"])
    admitted = p.acceptance(record, context=context)
    p.require(
        plan
        == dict(
            identity=identity(context, synthetic=True),
            record=str(record.relative_to(context.root)),
            record_sha256=p.file_hash(record),
            source_map=admitted["source_map"],
            dependencies=admitted["dependencies"],
            native_build=admitted["native_build"],
            synthetic_only=True,
            execution_authorized=False,
        )
        and freeze
        == dict(
            identity=plan["identity"],
            record_sha256=plan["record_sha256"],
            plan_sha256=p.file_hash(directory / "admission-plan.json"),
            synthetic_only=True,
            execution_authorized=False,
        ),
        "Immutable admitted synthetic freeze",
    )
    p.require(
        not (directory / "prerequisite-attempt.json").exists()
        and not (directory / "attempt.json").exists(),
        "Consumed fixture allowance refuses launch",
    )
    return Frozen(
        context,
        record,
        directory,
        p.file_hash(record),
        freeze["plan_sha256"],
        p.file_hash(directory / "admission-freeze.json"),
        _SEAL,
    )


def verify(frozen):
    p.require(
        isinstance(frozen, Frozen) and frozen.seal is _SEAL,
        "No Boolean/path launch permit",
    )
    current = load(frozen.directory, frozen.context)
    p.require(current == frozen, "Changed bytes after freeze")
    return current


def dispatch(frozen, executor):
    verify(frozen)
    p.durable_json(
        frozen.directory / "launch-claim.json",
        dict(record_sha256=frozen.record_sha256, freeze_sha256=frozen.freeze_sha256),
        exclusive=True,
    )
    verify(frozen)  # independent last binding check before the leaf executor
    return executor(frozen)


def launch(record, directory, context, executor):
    return dispatch(prepare(record, directory, context), executor)


def native(frozen):
    """Only generated synthetic payloads; no operational CLI branch."""
    from latenttrigger.benchmarks.development_decision_native import run

    return run(
        synthetic_directory=frozen.directory / "native",
        validation_owner=frozen.context.owner,
        admission_freeze=frozen,
    )
