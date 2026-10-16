"""Real producer/consumer and checked coordinator over bounded generated roots."""

import copy
import json
from dataclasses import replace

import pytest
from scripts.validate_development_raw_decisions import emit_record

from raregate.benchmarks import development_decision_admission as a
from raregate.benchmarks import development_decision_contract as c
from raregate.benchmarks import development_decision_native as n
from raregate.benchmarks import development_decision_protocol as p


@pytest.fixture
def emitted(tmp_path, monkeypatch):
    # Only small source/config/curated metadata; none of the referenced payloads.
    original = p.ROOT
    names = [
        p.CONFIG,
        p.PROMPT,
        c.REPAIR_PROMPT,
        p.old.CONFIG,
        p.old.PROMPT,
        "pyproject.toml",
        "results/tables/final/task0039-development-raw-feature-summary.json",
        "configs/benchmarks/development_raw_measurement_v1.json",
        "configs/benchmarks/prepared_batch_service_v1.json",
        "results/tables/final/task0040-development-raw-feature-summary.json",
    ]
    for name in names:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((original / name).read_bytes())
    (tmp_path / "src").mkdir()
    (tmp_path / "src/fixture.py").write_text("# owned generated source\n")
    library = tmp_path / "library.txt"
    library.write_text("generated native-build identity, no native execution")
    dependencies = {"python": "fixture", "packages": {"fixture": "1"}}
    monkeypatch.setattr(p, "dependencies", lambda: copy.deepcopy(dependencies))
    monkeypatch.setattr(p, "native_build", lambda: {"fixture": p.file_hash(library)})
    context = c.Context(tmp_path, "0042")
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
    p.durable_json(
        native / "workflow.json",
        dict(
            status="parent_accepted_synthetic_raw_decision",
            synthetic_only=True,
            reserved=False,
            identity=c.identity(context, synthetic=True),
            sleep_assertion=dict(released=True),
        ),
    )
    path = emit_record(context, directory, p.source_map(tmp_path), checks, native)
    return context, path, directory / "launch", dependencies, library


def read_record(path):
    return json.loads(path.read_text())


def rewrite(path, mutate):
    record = read_record(path)
    mutate(record)
    p.durable_json(path, record)


def test_actual_serialized_producer_outer_consumer_roundtrip(emitted):
    context, path, directory, _, _ = emitted
    raw = read_record(path)
    # Independently prescribed literals, rather than constant equality.
    assert raw["status"] == "software_accepted_synthetic_development_raw_decision"
    assert raw["identity"]["task"] == "0041"
    assert raw["identity"]["validation_owner"] == "0042"
    assert raw["identity"]["scope"] == "selected_raw_to_decisions"
    assert p.acceptance(path, context=context) == raw
    before = path.read_bytes()
    dispatches = []
    result = a.launch(
        path, directory, context, lambda f: dispatches.append(f) or "synthetic_only"
    )
    assert result == "synthetic_only" and len(dispatches) == 1
    assert path.read_bytes() == before
    with pytest.raises(FileExistsError):
        a.dispatch(dispatches[0], lambda f: pytest.fail("duplicate leaf"))
    with pytest.raises(ValueError):
        a.launch(path, directory, context, lambda f: pytest.fail("duplicate path"))
    # Default production scope cannot admit a repair-owned record.
    with pytest.raises(ValueError, match="namespace"):
        p.acceptance(path)


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
        a.launch(path, directory, context, leaf)
    assert effects == [] and not directory.exists()


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
        ("validation_prompt_sha256", "0" * 64),
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
            "repair_prompt": c.REPAIR_PROMPT,
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
            path, directory, context, lambda f: pytest.fail("changed evidence leaf")
        )
    assert not directory.exists()


@pytest.mark.parametrize("content", ["[]", "null", "{", "{}"])
def test_malformed_serialized_record(emitted, content):
    context, path, directory, _, _ = emitted
    path.write_text(content)
    with pytest.raises((ValueError, TypeError)):
        a.launch(path, directory, context, lambda f: pytest.fail("malformed leaf"))
    assert not directory.exists()


def test_record_outer_symlink_and_wrong_path(emitted):
    context, path, directory, _, _ = emitted
    other = path.with_name("other.json")
    path.rename(other)
    path.symlink_to(other)
    with pytest.raises(ValueError):
        a.launch(path, directory, context, lambda f: pytest.fail("symlink leaf"))
    with pytest.raises(ValueError):
        p.acceptance(other, context=context)


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
            path, directory, context, lambda f: pytest.fail("failed freeze controller")
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
    frozen = a.prepare(path, directory, context)
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
        # Copied historical marker schema, generated bytes; no actual namespace.
        p.durable_json(
            directory / "prerequisite-attempt.json",
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
    monkeypatch.setattr(p, "ROOT", context.root)
    monkeypatch.setattr(p, "custody", lambda: pytest.fail("raw custody"))
    monkeypatch.setattr(p, "hash_raw", lambda *x: pytest.fail("raw hash"))
    monkeypatch.setattr(n, "reserve", lambda *x: pytest.fail("reservation"))
    monkeypatch.setattr(n.rt, "IdleAssertion", lambda *x: pytest.fail("assertion"))
    monkeypatch.setattr(
        n.rt, "supervise", lambda *x, **kw: pytest.fail("worker dispatch")
    )
    with pytest.raises(ValueError):
        n.run(
            synthetic_directory=directory / "native",
            validation_owner="0042",
            admission_freeze=permit,
        )
    assert not directory.exists()


def test_forged_sealed_binding_refused(emitted):
    context, path, directory, _, _ = emitted
    frozen = a.prepare(path, directory, context)
    with pytest.raises(ValueError):
        a.dispatch(
            replace(frozen, plan_sha256="0" * 64), lambda f: pytest.fail("forged leaf")
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("task", "0040"),
        ("config_sha256", "0" * 64),
        ("prompt_sha256", "0" * 64),
        ("kind", "other"),
    ],
)
def test_wrong_task_plan_grant_and_receipt(tmp_path, monkeypatch, field, value):
    from tests.test_development_decision_grants import owned_grant

    directory, grant = owned_grant(tmp_path, monkeypatch)
    plan = p.read(directory.parent / "plan.json")
    plan[field] = value
    p.durable_json(directory.parent / "plan.json", plan)
    grant["plan_sha256"] = p.file_hash(directory.parent / "plan.json")
    p.durable_json(directory / "grant.json", grant)
    with pytest.raises(ValueError, match="identity"):
        p.validate_grant(directory, grant["token"], lambda: 1)
    assert not (directory / "claim.json").exists()


def test_default_production_wrapper_exact_generated_namespace(emitted, monkeypatch):
    context, path, _, _, _ = emitted
    generated = c.Context(context.root, "0041")
    directory = generated.namespace / "new-record"
    directory.mkdir(parents=True)
    checks = {}
    for name in c.CHECKS:
        log = directory / (name + ".txt")
        log.write_text("generated production namespace check")
        checks[name] = dict(
            exit_code=0,
            log=str(log.relative_to(context.root)),
            log_sha256=p.file_hash(log),
        )
    native = directory / "native-synthetic"
    native.mkdir()
    p.durable_json(
        native / "workflow.json",
        dict(
            status="parent_accepted_synthetic_raw_decision",
            synthetic_only=True,
            reserved=False,
            identity=c.identity(generated, synthetic=True),
            sleep_assertion=dict(released=True),
        ),
    )
    emitted_path = emit_record(
        generated, directory, p.source_map(context.root), checks, native
    )
    monkeypatch.setattr(p, "ROOT", context.root)
    assert (
        p.acceptance(emitted_path)["status"]
        == "software_accepted_synthetic_development_raw_decision"
    )
    with pytest.raises(ValueError):
        p.acceptance(path)


def test_receipt_identity_mismatch_rejected_before_exit_claim(tmp_path):
    from raregate.benchmarks import development_decision_runtime as rt

    grant = dict(identity=dict(task="0041"))
    body = dict(status="body_complete_awaiting_exit", identity=dict(task="0040"))
    with pytest.raises(ValueError, match="frozen body"):
        rt.accept(body, {}, grant, tmp_path, lambda: 1, 10)


def test_repair_context_never_operational(emitted):
    context, _, _, _, _ = emitted
    with pytest.raises(ValueError, match="only synthetic"):
        c.identity(context, synthetic=False)
