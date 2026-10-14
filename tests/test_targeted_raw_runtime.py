"""New campaign authority/consumption/access/lifecycle, entirely generated roots."""

import os
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tests.runtime_fixtures import SyntheticClock
from tests.test_targeted_raw_admission import add_roundtrip
from tests.test_targeted_raw_admission import emitted as emitted

from latenttrigger.benchmarks import targeted_raw_admission as a
from latenttrigger.benchmarks import targeted_raw_native as n
from latenttrigger.benchmarks import targeted_raw_protocol as p
from latenttrigger.benchmarks import targeted_raw_runtime as rt
from latenttrigger.benchmarks.development_decision_native import synthetic_prefix


def granted(emitted):
    context, _, directory, _, _ = emitted
    base = directory / "bootstrap"
    folder = base / "repetition1"
    folder.mkdir(parents=True)
    spec = p.load(context.root)
    plan = dict(
        task="0047",
        identity=p.identity(context.root),
        kind="synthetic_fixed_matrix",
        synthetic_only=True,
        validation_bootstrap=True,
        whole_deadline_continuous=780,
        reserved_deadline_continuous=720,
        authorization_prompt_sha256=spec["authorization_prompt_sha256"],
        admission_freeze_sha256=None,
        source_map=p.source_map(context.root),
        dependencies=p.dependencies(),
        native_build=p.native_build(),
        inputs={k: spec[k] for k in ("raw", "membership", "golden")},
        models=spec["models"],
        expected=spec["expected"],
        limits=spec["limits"],
    )
    p.durable_json(
        base / "selection.json", dict(task="0047", status="closed_selection_verified")
    )
    plan["selection_sha256"] = p.file_hash(base / "selection.json")
    p.durable_json(base / "plan.json", plan)
    grant = dict(
        task="0047",
        identity=plan["identity"],
        parent_pid=os.getppid(),
        token="a" * 32,
        phase="repetition1",
        synthetic_only=True,
        operation_deadline=179,
        stage_deadline=181,
        started_continuous=1,
        source_map=plan["source_map"],
        dependencies=plan["dependencies"],
        native_build=plan["native_build"],
        inputs=plan["inputs"],
        models=plan["models"],
        expected=plan["expected"],
        plan_sha256=p.file_hash(base / "plan.json"),
        selection_sha256=plan["selection_sha256"],
        payload_path=str(folder / "fixture.h5"),
        prefix_sha256=synthetic_prefix(),
    )
    p.durable_json(folder / "grant.json", grant)
    return context, folder, grant, plan


def test_new_grant_claim_and_seal_only(emitted):
    context, folder, g, _ = granted(emitted)
    _, permit = p.validate_grant(folder, g["token"], lambda: 1, root=context.root)
    assert permit.root == context.root and permit.identity["task"] == "0047"
    p.verify_payload(permit)
    with pytest.raises(FileExistsError):
        p.validate_grant(folder, g["token"], lambda: 1, root=context.root)
    with pytest.raises(ValueError):
        p.verify_payload(True)


@pytest.mark.parametrize(
    "field,value",
    [
        ("task", "0040"),
        ("task", "0041"),
        ("task", "0042"),
        ("identity", {}),
        ("source_map", {}),
        ("dependencies", {}),
        ("native_build", {}),
        ("models", []),
        ("inputs", {}),
        ("expected", {}),
        ("prefix_sha256", "0" * 64),
        ("payload_path", "/foreign/raw.h5"),
        ("parent_pid", -1),
        ("operation_deadline", 0),
        ("synthetic_only", False),
        ("phase", "calibration"),
    ],
)
def test_grant_rejection_before_claim_backend(emitted, field, value):
    context, folder, g, _ = granted(emitted)
    g[field] = value
    p.durable_json(folder / "grant.json", g)
    with pytest.raises((ValueError, KeyError)):
        p.validate_grant(folder, g["token"], lambda: 1, root=context.root)
    assert not (folder / "claim.json").exists()


def test_operational_reservation_same_branch_fixture_only(emitted):
    context, path, directory, _, _ = emitted
    add_roundtrip(context, path)
    frozen = a.prepare(path, directory, context, a.Mode.OPERATIONAL)
    plan = p.read(directory / "admission-plan.json")
    base = context.root / p.OUTPUT / "fixture-run"
    base.mkdir(parents=True)
    p.durable_json(
        base.parent / "prerequisite-attempt.json",
        dict(
            task="0047",
            directory=str(base.relative_to(context.root)),
            status="prerequisites_consumed_no_retry",
        ),
    )
    p.durable_json(base / "plan.json", plan)
    p.consume(base, plan, root=context.root)
    before = (base.parent / "attempt.json").read_bytes()
    with pytest.raises(FileExistsError):
        p.consume(base, plan, root=context.root)
    assert (base.parent / "attempt.json").read_bytes() == before
    assert a.verify_frozen(frozen) == frozen


def test_real_branch_fixture_custody_failure_consumes_without_raw_hash(
    emitted, monkeypatch
):
    context, path, directory, _, _ = emitted
    add_roundtrip(context, path)
    frozen = a.prepare(path, directory, context, a.Mode.OPERATIONAL)
    effects = []

    monkeypatch.setattr(rt, "ContinuousClock", SyntheticClock)

    class FixtureGuard:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def close(self):
            pass

        def report(self):
            return {"native_heap_reserved_bytes": 1}

    monkeypatch.setattr(rt, "ServiceGuard", FixtureGuard)
    monkeypatch.setattr(rt, "parent_check", lambda **kwargs: 1)

    def custody(root):
        assert root == context.root
        effects.append("fixture_custody")
        raise ValueError("fixture source missing")

    monkeypatch.setattr(p, "custody", custody)
    monkeypatch.setattr(
        p, "hash_raw", lambda *x: pytest.fail("hash after failed custody")
    )
    monkeypatch.setattr(
        rt, "IdleAssertion", lambda *x: pytest.fail("assertion after failed custody")
    )
    monkeypatch.setattr(
        rt, "supervise", lambda *x, **kw: pytest.fail("worker after failed custody")
    )
    base, w = a.dispatch(frozen, n.run)
    assert (
        w["status"] == "failed_prerequisites_no_retry"
        and w["workers"] == []
        and effects == ["fixture_custody"]
    )
    marker = context.root / p.OUTPUT / "prerequisite-attempt.json"
    before = marker.read_bytes()
    assert p.read(marker)["task"] == "0047"
    with pytest.raises(ValueError):
        a.dispatch(frozen, n.run)
    assert marker.read_bytes() == before and not (base / "plan.json").exists()


def test_failed_changed_freeze_never_reaches_controller_leaf(emitted, monkeypatch):
    context, path, directory, _, _ = emitted
    add_roundtrip(context, path)
    frozen = a.prepare(path, directory, context, a.Mode.OPERATIONAL)
    (directory / "admission-plan.json").write_text("{}")
    monkeypatch.setattr(rt, "ContinuousClock", lambda: pytest.fail("controller starts"))
    monkeypatch.setattr(p, "custody", lambda *x: pytest.fail("custody starts"))
    with pytest.raises((ValueError, KeyError)):
        n.run(frozen)
    assert not (context.root / p.OUTPUT).exists()


@pytest.mark.parametrize(
    "kind",
    ["exit", "reap", "deadline", "resource", "cleanup", "body", "outputs", "identity"],
)
def test_new_parent_acceptance_requires_complete_reaped_body(emitted, kind):
    context, _, directory, _, _ = emitted
    directory.mkdir()
    ident = p.identity(context.root)
    grant = dict(
        identity=ident,
        source_map=p.source_map(context.root),
        dependencies=p.dependencies(),
        phase="reporting",
    )
    p.durable_json(directory / "grant.json", grant)
    names = {
        "selection.csv",
        "cells.csv",
        "pairs.csv",
        "summary.json",
        "joint-cost.png",
        "paired-cost.png",
        "selection-coverage.png",
    }
    for name in names:
        (directory / name).write_bytes(b"owned fixture output")
    body = dict(
        task="0047",
        identity=ident,
        status="body_complete_awaiting_exit",
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        grant_sha256=p.file_hash(directory / "grant.json"),
        outputs={name: p.file_hash(directory / name) for name in names},
        resources=dict(
            latched_error=None,
            owned_thread_alive=False,
            peak_rss_bytes=1,
            native_heap_reserved_bytes=1,
        ),
        cleanup_seconds=0,
        worker_seconds=1,
        monitor_closed_continuous=1,
    )
    dispatch = dict(
        returncode=0,
        parent_confirms_normal_exit=True,
        child_reaped=True,
        within_deadline=True,
        parent_error=None,
        end_continuous=2,
    )
    assert rt.accept(
        body, dispatch, grant, directory, lambda: 2, 10, root=context.root
    )["normal_exit_reaped"]
    if kind == "exit":
        dispatch["returncode"] = 1
    if kind == "reap":
        dispatch["child_reaped"] = False
    if kind == "deadline":
        dispatch["within_deadline"] = False
    if kind == "resource":
        body["resources"]["native_heap_reserved_bytes"] = 2**30
    if kind == "cleanup":
        body["cleanup_seconds"] = 3
    if kind == "body":
        body["status"] = "body_complete"
    if kind == "outputs":
        body["outputs"] = {}
    if kind == "identity":
        body["identity"] = {"task": "0042"}
    with pytest.raises(ValueError):
        rt.accept(body, dispatch, grant, directory, lambda: 2, 10, root=context.root)


@pytest.mark.parametrize(
    "failure",
    [
        "assertion_start",
        "assertion_loss",
        "assertion_release",
        "critical_resource",
        "suspension",
    ],
)
def test_synthetic_controller_failure_cleanup_and_deadlines(
    emitted, monkeypatch, failure
):
    context, _, directory, _, _ = emitted
    tick = [1.0]

    class Clock:
        def __call__(self):
            return tick[0]

        def snapshot(self):
            return {"continuous_seconds": tick[0]}

    class Assertion:
        identity = "fixture-owned"

        def __init__(self, clock):
            self.evidence = {"released": False}

        def start(self, deadline):
            if failure in ("assertion_start", "assertion_release"):
                raise ValueError("fixture start failure")

        def check(self, deadline, force=False):
            if failure == "assertion_loss":
                raise ValueError("fixture assertion lost")

        def release(self, deadline):
            if failure == "assertion_release":
                raise ValueError("fixture release failed")
            self.evidence.update(released=True, owned_assertion_absent=True)
            return self.evidence

    class Guard:
        def __init__(self, *x, **kw):
            pass

        def __enter__(self):
            if failure == "critical_resource":
                raise ValueError("fixture CRITICAL")

        def check(self):
            pass

        def close(self):
            pass

        def report(self):
            return {"native_heap_reserved_bytes": 1}

    def supervise(*x, **kw):
        if failure == "suspension":
            tick[0] = 1000
            rt.check_deadline(kw["clock"], kw["operation_deadline"])
        kw["monitor"]()
        pytest.fail("must stop in fixture monitor")

    monkeypatch.setattr(rt, "ContinuousClock", Clock)
    monkeypatch.setattr(rt, "IdleAssertion", Assertion)
    monkeypatch.setattr(rt, "ServiceGuard", Guard)
    monkeypatch.setattr(rt, "parent_check", lambda **kw: 1)
    monkeypatch.setattr(rt, "alarm", lambda *x: nullcontext())
    monkeypatch.setattr(rt, "supervise", supervise)
    base, w = n.bootstrap(directory, context)
    assert w["status"] == "failed_synthetic_validation" and not w["reserved"]
    assert not (base / "parent-acceptance.json").exists()
    if failure == "assertion_release":
        assert "release_error" in w["sleep_assertion"]
    elif failure != "critical_resource":
        assert w["sleep_assertion"]["released"]


def test_new_provider_refuses_old_permit_before_backend(emitted):
    from latenttrigger.benchmarks.targeted_raw_provider import Chain

    class Dataset:
        @property
        def file(self):
            pytest.fail("backend queried before authority")

    with pytest.raises(ValueError):
        Chain(Dataset(), None, Path("/foreign"), lambda: 1, 1000, permit=True)


def test_granted_provider_selected_rows_no_neighbors(emitted):
    from latenttrigger.benchmarks.targeted_raw_provider import Approval, Chain

    context, folder, g, _ = granted(emitted)
    _, permit = p.validate_grant(folder, g["token"], lambda: 1, root=context.root)
    ids = np.arange(1024, dtype="<i8") * 3
    approval = Approval(ids, g["prefix_sha256"])
    seen = []

    class Dataset:
        name = "/df/block0_values"
        shape = (1100000, 2101)
        dtype = np.dtype("<f8")
        id = SimpleNamespace(valid=True)
        file = SimpleNamespace(filename=g["payload_path"])

        def __getitem__(self, key):
            selected, columns = key
            seen.append(selected)
            assert columns == slice(None)
            assert selected == ids[:8].tolist()
            out = np.zeros((8, 2101), dtype="<f8")
            out[:, 0] = 1
            return out

    chain = Chain(
        Dataset(),
        approval,
        Path(g["payload_path"]),
        lambda: 1,
        g["operation_deadline"],
        permit=permit,
    )
    models = {
        name: (object(), object()) for name in ("pca-v1", "compact-autoencoder-v2")
    }
    channels = p.load()["channels"]
    chain.register(models, channels)
    model, thresholds = models["pca-v1"]
    chain.bind(
        dict(
            B=8,
            m=8,
            side="natural_m",
            actual_rows=8,
            model_shape_rows=8,
            wrapper="task0047_owned_C_FP32_actual_rows_public_score_strict4_copies_v1",
            case_class="remeasured_reference",
            window_position=0,
            candidate="pca-v1",
            phase="pre",
        ),
        model,
        thresholds,
        channels,
    )
    with pytest.raises(ValueError):
        chain.read(np.array([1], dtype="<i8"))
    assert seen == []
    assert chain.read(ids[:8]).shape == (8, 2101) and seen == [ids[:8].tolist()]
    assert chain.peak_owned_array_bound_bytes <= 64 * 2**20


def test_new_fixed_protocol_schedule_and_scope():
    from latenttrigger.benchmarks.targeted_raw_planning import counts

    spec = p.load()
    assert spec["expected"] == counts()
    assert (
        spec["task"] == "0047"
        and spec["limits"]["native_reserved_bytes"] == 512 * 2**20
    )
    assert spec["expected"]["public_service"] == dict(calls=15744, rows=621642)


def test_combined_worker_journal_bound(tmp_path):
    folder = tmp_path / "repetition1"
    folder.mkdir()
    for name in ["guard.jsonl", "access-journal.jsonl"]:
        with (folder / name).open("wb") as f:
            f.truncate(9 * 2**20)
    with pytest.raises(ValueError, match="Combined"):
        rt.storage(tmp_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("stage_deadline", 9999),
        ("operation_deadline", 9999),
        ("started_continuous", -9999),
    ],
)
def test_stale_or_extended_grant_deadlines_rejected(emitted, field, value):
    context, folder, g, _ = granted(emitted)
    g[field] = value
    p.durable_json(folder / "grant.json", g)
    with pytest.raises(ValueError):
        p.validate_grant(folder, g["token"], lambda: 1, root=context.root)
    assert not (folder / "claim.json").exists()


def test_atomic_durable_temporary_disappearance_is_conservatively_reserved(
    tmp_path, monkeypatch
):
    temp = tmp_path / ("access.json." + "a" * 32 + ".tmp")
    temp.write_text("owned temporary")
    original = Path.lstat

    def renamed(path):
        if path == temp:
            temp.unlink()
            raise FileNotFoundError(str(path))
        return original(path)

    monkeypatch.setattr(Path, "lstat", renamed)
    assert rt.storage(tmp_path) == 4 * 2**20


def test_unrecognized_disappearing_file_is_a_veto(tmp_path, monkeypatch):
    lost = tmp_path / "access-journal.jsonl"
    lost.write_text("owned journal")
    original = Path.lstat

    def removed(path):
        if path == lost:
            raise FileNotFoundError(str(path))
        return original(path)

    monkeypatch.setattr(Path, "lstat", removed)
    with pytest.raises(ValueError, match="Only owned atomic"):
        rt.storage(tmp_path)
