"""Real producer/consumer and checked coordinator over bounded generated roots."""

import copy
import json
from dataclasses import replace

import pytest

from raregate.benchmarks import partial_raw_admission as a
from raregate.benchmarks import partial_raw_admission as c
from raregate.benchmarks import partial_raw_native as n
from raregate.benchmarks import partial_raw_protocol as p


@pytest.fixture
def emitted(tmp_path, monkeypatch):
    original = p.ROOT
    names = list(p.source_map())
    for name in names:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((original / name).read_bytes())
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "src/fixture.py").write_text("# owned generated source\n")
    library = tmp_path / "library.txt"
    library.write_text("generated native-build identity, no native execution")
    dependencies = {"python": "fixture", "packages": {"fixture": "1"}}
    monkeypatch.setattr(p, "dependencies", lambda: copy.deepcopy(dependencies))
    monkeypatch.setattr(p, "native_build", lambda: {"fixture": p.file_hash(library)})
    context = c.Context(tmp_path)
    directory = context.namespace / "record"
    directory.mkdir(parents=True)
    checks = {}
    for name in c.CHECKS:
        log = directory / (name + ".txt")
        log.write_text("owned synthetic check passed")
        checks[name] = dict(
            exit_code=0, log=str(log.relative_to(tmp_path)), log_sha256=p.file_hash(log)
        )
    native = directory / "native-synthetic"
    native.mkdir()
    names = (
        {
            f"repetition{i}/{name}"
            for i in (1, 2, 3)
            for name in (
                "receipt.json",
                "grant.json",
                "access.json",
                "access-journal.jsonl",
                "aggregate.json",
                "timings.jsonl",
                "timer.json",
                "guards.jsonl",
                "worker.log",
            )
        }
        | {
            "reporting/" + name
            for name in (
                "receipt.json",
                "grant.json",
                "guards.jsonl",
                "worker.log",
                "cells.csv",
                "pairs.csv",
                "summary.json",
                "joint-cost.png",
                "paired-cost.png",
                "chronology.png",
            )
        }
        | {"plan.json", "guards.jsonl"}
    )
    for name in names:
        target = native / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "generated metadata for admission path checks; no native execution"
        )
    p.durable_json(
        native / "workflow.json",
        dict(
            source_map=p.source_map(context.root),
            dependencies=p.dependencies(),
            status="parent_accepted_synthetic_natural_partial_raw_decision",
            synthetic_only=True,
            reserved=False,
            identity=p.identity(context.root),
            native_build=p.native_build(),
            owned_evidence_sha256={
                name: p.file_hash(native / name) for name in sorted(names)
            },
            sleep_assertion=dict(released=True, owned_assertion_absent=True),
        ),
    )
    path = a.emit(
        context, directory, p.source_map(tmp_path), checks, native / "workflow.json"
    )
    return (context, path, directory / "launch", dependencies, library)


def read_record(path):
    return json.loads(path.read_text())


def rewrite(path, mutate):
    record = read_record(path)
    mutate(record)
    p.durable_json(path, record)


def test_actual_serialized_producer_outer_consumer_roundtrip(emitted):
    context, path, directory, _, _ = emitted
    raw = read_record(path)
    assert raw["status"] == "software_accepted_synthetic_natural_partial_raw_decision"
    assert raw["identity"]["task"] == "0045"
    assert raw["identity"]["validation_owner"] == "0045"
    assert raw["identity"]["scope"] == "selected_partial_raw_to_decisions"
    assert a.verify(path, context) == raw
    before = path.read_bytes()
    dispatches = []
    result = a.launch(
        path,
        directory,
        context,
        a.Mode.SYNTHETIC,
        lambda f: dispatches.append(f) or "synthetic_only",
    )
    assert result == "synthetic_only" and len(dispatches) == 1
    assert path.read_bytes() == before
    with pytest.raises(FileExistsError):
        a.dispatch(dispatches[0], lambda f: pytest.fail("duplicate leaf"))
    with pytest.raises(ValueError):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("duplicate path"),
        )
    with pytest.raises(ValueError, match="namespace"):
        a.verify(path, a.Context(p.ROOT))


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "software_accepted_synthetic_development_decision"),
        ("status", "accepted"),
        ("status", None),
        ("schema_version", True),
        ("record_role", "execution_permission"),
        ("synthetic_only", False),
        ("execution_authorized", True),
        ("operational_reservation", True),
        ("source_map", {}),
        ("dependencies", {}),
        ("native_build", {}),
        ("checks", {}),
        ("extra", "permissive field"),
    ],
)
def test_real_predicates_block_all_downstream(emitted, field, value):
    context, path, directory, _, _ = emitted
    rewrite(path, lambda r: r.update({field: value}))
    effects = []

    def leaf(frozen):
        effects.extend(
            [
                "controller",
                "reservation",
                "raw_custody",
                "assertion",
                "worker",
                "numerical",
            ]
        )

    with pytest.raises((ValueError, KeyError, TypeError)):
        a.launch(path, directory, context, a.Mode.SYNTHETIC, leaf)
    assert effects == [] and (not directory.exists())


@pytest.mark.parametrize(
    "field,value",
    [
        ("task", "0040"),
        ("kind", "operational"),
        ("scope", "test_signal"),
        ("protocol_kind", "other"),
        ("validation_owner", "0041"),
        ("config_sha256", "0" * 64),
        ("prompt_sha256", "0" * 64),
        ("payload_scope", "other"),
    ],
)
def test_task_kind_scope_and_all_prompt_bindings(emitted, field, value):
    context, path, directory, _, _ = emitted
    rewrite(path, lambda r: r["identity"].update({field: value}))
    with pytest.raises(ValueError):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("identity failure must block leaf"),
        )
    assert not directory.exists()


@pytest.mark.parametrize(
    "change",
    [
        "failed_check",
        "missing_check",
        "log",
        "receipt",
        "receipt_task",
        "source",
        "dependency",
        "build",
        "config",
        "prompt",
        "repair_prompt",
        "foreign_log",
        "symlink_log",
        "traversal_log",
        "absolute_log",
    ],
)
def test_changed_evidence_and_current_bindings(emitted, change):
    context, path, directory, dependencies, library = emitted
    record = read_record(path)
    if change == "failed_check":
        rewrite(path, lambda r: r["checks"]["focused"].update(exit_code=1))
    elif change == "missing_check":
        rewrite(path, lambda r: r["checks"].pop("focused"))
    elif change in ("log", "symlink_log"):
        log = context.root / record["checks"]["focused"]["log"]
        if change == "log":
            log.write_text("modified")
        else:
            target = log.with_suffix(".other")
            log.rename(target)
            log.symlink_to(target)
    elif change in ("receipt", "receipt_task"):
        receipt = context.root / record["native_receipt_path"]
        workflow = p.read(receipt)
        if change == "receipt_task":
            workflow["identity"]["task"] = "0040"
            p.durable_json(receipt, workflow)
            rewrite(
                path, lambda r: r.update(native_receipt_sha256=p.file_hash(receipt))
            )
        else:
            receipt.write_text("modified")
    elif change == "dependency":
        dependencies["packages"]["fixture"] = "2"
    elif change == "build":
        library.write_text("changed library bytes")
    elif change in ("source", "config", "prompt", "repair_prompt"):
        name = {
            "source": "src/fixture.py",
            "config": p.CONFIG,
            "prompt": p.PROMPT,
            "repair_prompt": p.PROMPT,
        }[change]
        f = context.root / name
        f.write_text(f.read_text() + "\n ")
    else:
        foreign = context.root / "foreign.txt"
        foreign.write_text("owned synthetic check passed")
        value = {
            "foreign_log": "foreign.txt",
            "traversal_log": "../foreign.txt",
            "absolute_log": str(foreign),
        }[change]
        rewrite(path, lambda r: r["checks"]["focused"].update(log=value))
    with pytest.raises((ValueError, json.JSONDecodeError)):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("changed evidence leaf"),
        )
    assert not directory.exists()


@pytest.mark.parametrize("content", ["[]", "null", "{", "{}"])
def test_malformed_serialized_record(emitted, content):
    context, path, directory, _, _ = emitted
    path.write_text(content)
    with pytest.raises((ValueError, TypeError)):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("malformed leaf"),
        )
    assert not directory.exists()


def test_record_outer_symlink_and_wrong_path(emitted):
    context, path, directory, _, _ = emitted
    other = path.with_name("other.json")
    path.rename(other)
    path.symlink_to(other)
    with pytest.raises(ValueError):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("symlink leaf"),
        )
    with pytest.raises(ValueError):
        a.verify(other, context)


@pytest.mark.parametrize("phase", ["admission-plan.json", "admission-freeze.json"])
def test_actual_publication_failure_no_dispatch(emitted, monkeypatch, phase):
    context, path, directory, _, _ = emitted
    durable = p.durable_json

    def interrupted(target, value, **kw):
        if target.name == phase:
            target.write_text('{"interrupted":')
            raise OSError("synthetic publication interruption")
        return durable(target, value, **kw)

    monkeypatch.setattr(p, "durable_json", interrupted)
    with pytest.raises(OSError):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("failed freeze controller"),
        )
    assert not (directory / "admission-freeze.json").exists()
    assert not (directory / "admission-plan.json").exists()
    assert not (directory / "launch-claim.json").exists()
    assert list(directory.glob("rejected-*"))


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "partial",
        "plan",
        "task0040",
        "freeze",
        "source",
        "prompt",
        "build",
        "consumed",
    ],
)
def test_frozen_state_changes_block_real_coordinator_branch(emitted, change):
    context, path, directory, _, library = emitted
    frozen = a.prepare(path, directory, context, a.Mode.SYNTHETIC)
    if change == "missing":
        (directory / "admission-freeze.json").unlink()
    elif change == "partial":
        (directory / "admission-freeze.json").write_text('{"partial":')
    elif change in ("plan", "task0040"):
        plan = p.read(directory / "admission-plan.json")
        if change == "task0040":
            plan["identity"]["task"] = "0040"
        else:
            plan["execution_authorized"] = True
        p.durable_json(directory / "admission-plan.json", plan)
    elif change == "freeze":
        (directory / "admission-freeze.json").write_text("{}")
    elif change in ("source", "prompt"):
        (
            context.root / (p.PROMPT if change == "prompt" else "src/fixture.py")
        ).write_text("changed after freeze")
    elif change == "build":
        library.write_text("changed after freeze")
    else:
        p.durable_json(
            directory / "copied-consumed-marker.json",
            dict(
                status="prerequisites_consumed_no_retry",
                directory="historical_failed_fixture",
            ),
        )
    with pytest.raises((ValueError, FileNotFoundError)):
        a.dispatch(frozen, lambda f: pytest.fail("stale freeze downstream"))
    assert not (directory / "launch-claim.json").exists()


@pytest.mark.parametrize("permit", [True, "/arbitrary/path", None])
def test_native_controller_independent_pre_effect_gate(emitted, monkeypatch, permit):
    context, _, directory, _, _ = emitted
    monkeypatch.setattr(p, "custody", lambda *x: pytest.fail("raw custody"))
    monkeypatch.setattr(p, "consume", lambda *x, **kw: pytest.fail("reservation"))
    monkeypatch.setattr(n.rt, "IdleAssertion", lambda *x: pytest.fail("assertion"))
    monkeypatch.setattr(
        n.rt, "supervise", lambda *x, **kw: pytest.fail("worker dispatch")
    )
    with pytest.raises(ValueError):
        n.run(permit)
    assert not directory.exists()


def test_forged_sealed_binding_refused(emitted):
    context, path, directory, _, _ = emitted
    frozen = a.prepare(path, directory, context, a.Mode.SYNTHETIC)
    with pytest.raises(ValueError):
        a.dispatch(
            replace(frozen, plan_sha256="0" * 64), lambda f: pytest.fail("forged leaf")
        )


def add_roundtrip(context, path):
    record = a.verify(path, context)
    native = context.root / record["native_receipt_path"]
    p.durable_json(
        path.parent / "admission-roundtrip.json",
        dict(
            task="0045",
            status="software_accepted_synthetic_natural_partial_raw_decision_roundtrip",
            record_sha256=p.file_hash(path),
            workflow_path=str(native.relative_to(context.root)),
            workflow_sha256=p.file_hash(native),
            execution_authorized=False,
            identity=record["identity"],
            source_map=record["source_map"],
            dependencies=record["dependencies"],
            native_build=record["native_build"],
        ),
    )


def test_operational_freeze_requires_independent_roundtrip(emitted):
    context, path, directory, _, _ = emitted
    with pytest.raises((ValueError, FileNotFoundError)):
        a.prepare(path, directory, context, a.Mode.OPERATIONAL)
    assert not directory.exists()
    add_roundtrip(context, path)
    frozen = a.prepare(path, directory, context, a.Mode.OPERATIONAL)
    assert frozen.mode is a.Mode.OPERATIONAL
    effects = []
    a.dispatch(frozen, lambda f: effects.append("fixture_operational_branch"))
    assert effects == ["fixture_operational_branch"]
    assert not (context.root / p.OUTPUT).exists()


@pytest.mark.parametrize("old", ["0040", "0041", "0042"])
def test_copied_old_identity_and_context_refused(emitted, old):
    context, path, directory, _, _ = emitted
    with pytest.raises(ValueError):
        a.Context(context.root, old)
    rewrite(path, lambda r: r["identity"].update(task=old, validation_owner=old))
    with pytest.raises(ValueError):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("old identity launch"),
        )
    from raregate.benchmarks.development_decision_contract import Context

    with pytest.raises(ValueError):
        Context(context.root, "0045")


def test_old_sealed_object_is_not_operational_authority(emitted):
    from raregate.benchmarks.development_decision_admission import Frozen
    from raregate.benchmarks.development_decision_contract import Context

    context, path, directory, _, _ = emitted
    old = Frozen(
        Context(context.root, "0042"),
        path,
        directory,
        "a" * 64,
        "b" * 64,
        "c" * 64,
        object(),
    )
    with pytest.raises(ValueError):
        n.run(old)
    assert not directory.exists()


@pytest.mark.parametrize("mode", [True, False, "operational"])
def test_mode_flag_is_not_an_execution_permit(emitted, mode):
    context, path, directory, _, _ = emitted
    with pytest.raises(ValueError):
        a.prepare(path, directory, context, mode)
    assert not directory.exists()


def test_consumed_operational_fixture_marker_no_dispatch(emitted):
    context, path, directory, _, _ = emitted
    add_roundtrip(context, path)
    frozen = a.prepare(path, directory, context, a.Mode.OPERATIONAL)
    marker = context.root / p.OUTPUT / "prerequisite-attempt.json"
    marker.parent.mkdir(parents=True)
    marker.write_text('{"task":"0045","status":"prerequisites_consumed_no_retry"}')
    with pytest.raises(ValueError):
        a.dispatch(frozen, lambda f: pytest.fail("consumed launch"))
    assert not (directory / "launch-claim.json").exists()


@pytest.mark.parametrize(
    "name",
    [
        "repetition1/receipt.json",
        "repetition2/access-journal.jsonl",
        "repetition3/timings.jsonl",
        "reporting/pairs.csv",
    ],
)
def test_altered_owned_native_evidence_rejected_before_freeze(emitted, name):
    context, path, directory, _, _ = emitted
    record = read_record(path)
    native = context.root / record["native_receipt_path"]
    (native.parent / name).write_text("altered after accepted native receipt")
    with pytest.raises(ValueError):
        a.launch(
            path,
            directory,
            context,
            a.Mode.SYNTHETIC,
            lambda f: pytest.fail("changed native evidence reached controller"),
        )
    assert not directory.exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("packing", "padded_nominal_B"),
        ("paired_contract_sha256", "0" * 64),
        ("validation_owner", "0044"),
        ("scope", "selected_raw_to_decisions"),
    ],
)
def test_closed_paired_contract_identity_in_outer_record(emitted, field, value):
    context, path, directory, _, _ = emitted
    rewrite(path, lambda r: r["identity"].update({field: value}))
    with pytest.raises(ValueError):
        a.prepare(path, directory, context, a.Mode.SYNTHETIC)
    assert not directory.exists()
