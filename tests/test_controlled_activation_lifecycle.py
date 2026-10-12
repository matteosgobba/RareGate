"""Simulated continuous/ownership/custody failures; no actual native invocations."""

import os
from contextlib import nullcontext

import pytest

from latenttrigger.data import three_prong_v3_runtime as clock_rt
from latenttrigger.evaluation.guard import NATIVE_METHOD, PRESSURE_METHOD, GuardError
from latenttrigger.research.controlled_activation import native
from latenttrigger.research.controlled_activation import protocol as p
from latenttrigger.research.controlled_activation import runtime as rt


class Clock:
    now = 0.0

    def __call__(self):
        return self.now

    def snapshot(self):
        return dict(continuous_seconds=self.now, ordinary_monotonic_seconds=0.0)


def sample(rss=350 * 2**20, pressure=2):
    return dict(
        peak_rss_bytes=rss,
        native_heap_reserved_bytes=180 * 2**20,
        native_heap_in_use_bytes=100 * 2**20,
        workspace_method=NATIVE_METHOD,
        pressure_dispatch_flags=pressure,
        pressure_errno=1 if pressure is None else None,
        pressure_method=PRESSURE_METHOD,
    )


@pytest.mark.parametrize(
    "rss,pressure,accepted",
    [
        (2**30, 2, True),
        (2**30 + 1, 2, False),
        (350 * 2**20, 1, True),
        (350 * 2**20, 4, False),
        (350 * 2**20, None, True),
        (0, 2, False),
    ],
)
def test_explicit_narrow_RSS_pressure_accounting(rss, pressure, accepted):
    guard = rt.SyntheticGuard(
        10, clock=Clock(), probe=lambda: sample(rss, pressure), notify=False
    )
    if accepted:
        guard.check()
    else:
        with pytest.raises(GuardError):
            guard.check()
    assert guard.report()["worker_RSS_ceiling_bytes"] == 2**30
    if pressure is None:
        assert guard.report()["pressure_counts"]["unknown"] == 1


@pytest.mark.parametrize(
    "key,value",
    [
        ("native_heap_reserved_bytes", 0),
        ("native_heap_reserved_bytes", 512 * 2**20 + 1),
        ("native_heap_in_use_bytes", None),
        ("native_heap_in_use_bytes", 181 * 2**20),
        ("workspace_method", "wrong"),
    ],
)
def test_primary_and_native_veto(key, value):
    value_sample = sample()
    value_sample[key] = value
    guard = rt.SyntheticGuard(
        10, clock=Clock(), probe=lambda: value_sample, notify=False
    )
    with pytest.raises(GuardError):
        guard.check()


def test_query_gap_and_suspension_deadline():
    clock = Clock()
    guard = rt.SyntheticGuard(10, clock=clock, probe=sample, notify=False)
    guard.check()
    clock.now = 3
    guard.check()
    assert guard.report()["max_query_start_gap_continuous_seconds"] == 3
    clock.now = 12
    with pytest.raises(GuardError):
        guard.check()
    with pytest.raises(GuardError):
        rt.check_deadline(clock, 10)


def test_guard_journal_overflow(tmp_path):
    guard = rt.SyntheticGuard(
        10,
        clock=Clock(),
        probe=sample,
        notify=False,
        directory=tmp_path,
        journal_limit=1,
    )
    with pytest.raises(GuardError):
        guard.__enter__()
    assert not guard.report()["owned_thread_alive"]


@pytest.mark.parametrize(
    "name,size",
    [
        ("worker.log", 2**20 + 1),
        ("guards.jsonl", 64 * 2**20 + 1),
        ("report.json", 2**20 + 1),
        ("owned.bin", 128 * 2**20 + 1),
    ],
)
def test_storage_and_log_bounds(tmp_path, name, size):
    with (tmp_path / name).open("wb") as stream:
        stream.truncate(size)
    with pytest.raises(ValueError):
        rt.storage_check(tmp_path)


@pytest.mark.parametrize(
    "name",
    [
        "data/events.json",
        "data/events.npy",
        "results/scores.npy",
        "artifacts/model.json",
        "sources/card.txt",
        "outside.npy",
        "outside.h5",
        "outside.pt",
    ],
)
def test_operational_array_or_source_open_refused(tmp_path, name):
    owned = tmp_path / "owned"
    owned.mkdir()
    with pytest.raises(PermissionError):
        rt.check_open(tmp_path, owned, set(), "open", (str(tmp_path / name), "r", 0))


@pytest.mark.parametrize(
    "event",
    [
        "socket.connect",
        "socket.bind",
        "urllib.Request",
        "subprocess.Popen",
        "os.system",
        "os.exec",
        "os.posix_spawn",
    ],
)
def test_worker_network_child_boundary(tmp_path, event):
    with pytest.raises(PermissionError):
        rt.check_open(tmp_path, tmp_path / "owned", set(), event, ())


def test_owned_json_allowed_but_symlink_escape_refused(tmp_path):
    owned = tmp_path / "owned"
    owned.mkdir()
    outside = tmp_path / "data"
    outside.mkdir()
    target = outside / "synthetic-placeholder.json"
    target.write_text("{}")
    rt.check_open(
        tmp_path,
        owned,
        set(),
        "open",
        (str(owned / "checkpoint.json"), "w", os.O_CREAT),
    )
    (owned / "alias.json").symlink_to(target)
    with pytest.raises(PermissionError):
        rt.check_open(
            tmp_path, owned, set(), "open", (str(owned / "alias.json"), "r", 0)
        )
    with pytest.raises(ValueError):
        rt.storage_check(owned)


class Child:
    pid = 987654
    returncode = None

    def poll(self):
        return self.returncode


def fake_reap(child, deadline, *, clock, **kwargs):
    child.returncode = -15 if child.returncode is None else child.returncode
    return dict(reaped=True, cleanup_deadline_met=clock() <= deadline)


@pytest.mark.parametrize("failure", ["none", "creation", "loss", "identity", "release"])
def test_assertion_creation_loss_identity_and_release(monkeypatch, failure):
    clock = Clock()
    child = Child()

    def read(command, *_):
        if command[0].endswith("ps"):
            return f"{child.pid} {os.getpid()} 3000 Ss"
        if failure == "creation" or (
            child.returncode is not None and failure != "release"
        ):
            return "PreventUserIdleSystemSleep 0"
        identity = "0xb" if failure == "identity" and clock.now else "0xa"
        return f"PreventUserIdleSystemSleep 1\npid {child.pid}(caffeinate): [{identity}] PreventUserIdleSystemSleep"

    monkeypatch.setattr(clock_rt, "reap", fake_reap)
    assertion = rt.IdleAssertion(clock, launch=lambda *a, **k: child, read=read)
    if failure == "creation":
        child.returncode = 1
        with pytest.raises(GuardError):
            assertion.start(10)
    else:
        assertion.start(10)
        if failure == "loss":
            child.returncode = 1
            with pytest.raises(GuardError):
                assertion.check(10, force=True)
        if failure == "identity":
            clock.now = 1
            with pytest.raises(GuardError):
                assertion.check(10, force=True)
        if failure == "release":
            with pytest.raises(GuardError):
                assertion.release(10)
            assert not assertion.evidence["released"]
        else:
            assert assertion.release(10)["released"]
    assert (
        assertion.evidence["display_sleep_permitted"]
        and not assertion.evidence["persistent_settings_changed"]
    )


@pytest.mark.parametrize("jump,accepted", [(0, True), (9, False), (12, False)])
def test_exit_zero_still_requires_continuous_deadline(
    monkeypatch, tmp_path, jump, accepted
):
    clock = Clock()
    child = Child()
    child.returncode = 0
    monkeypatch.setattr(clock_rt, "parent_check", lambda **_: 0)
    monkeypatch.setattr(clock_rt, "reap", fake_reap)

    def monitor():
        clock.now = jump

    result = rt.supervise(
        [],
        tmp_path / "worker.log",
        root=tmp_path,
        environment={},
        clock=clock,
        operation_deadline=8,
        stage_deadline=10,
        whole_deadline=20,
        launch=lambda *a, **k: child,
        monitor=monitor,
    )
    assert result["child_reaped"] and result["parent_confirms_normal_exit"] == accepted
    assert result["overshoot_seconds"] == max(0, jump - 10)


def body_fixture(directory):
    counters = dict(
        model_instances=9,
        forward_calls=66,
        forward_rows=2346,
        reconstruction_computations=66,
        optimizer_steps_started=12,
        optimizer_steps_completed=12,
        optimizer_steps_inflight=0,
        synthetic_calibrations=6,
    )
    report = dict(
        kind="synthetic_only",
        arms=[
            dict(
                arm=a,
                seed=s,
                restoration=dict(
                    selected_bytes_verified=True,
                    selected_score_identity=True,
                    complete_epochs=2,
                    selected_epoch=1,
                ),
            )
            for a, s in p.ORDER
        ],
        pairs=[
            dict(
                seed=s,
                common_epochs=2,
                identical_consumed_orders=True,
                missing_later_epochs=0,
            )
            for s in p.SEEDS
        ],
        decision=dict(label="inconclusive", claim_permitted=False),
    )
    names = {
        "report.json",
        "counters.json",
        *[f"initialization-{s}.json" for s in p.SEEDS],
        *[f"checkpoint-{a}-{s}.json" for a, s in p.ORDER],
    }
    for name in names:
        p.durable_json(
            directory / name,
            report
            if name == "report.json"
            else counters
            if name == "counters.json"
            else {},
        )
    grant = p.read(directory / "grant.json")
    body = dict(
        status="body_complete_awaiting_exit",
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        grant_sha256=p.file_hash(directory / "grant.json"),
        config_sha256=grant["config_sha256"],
        resources=dict(
            latched_error=None,
            owned_thread_alive=False,
            peak_rss_bytes=350 * 2**20,
            native_heap_reserved_bytes=180 * 2**20,
        ),
        cleanup_seconds=0.001,
        counters=counters,
        all_pairing_restoration_checks=True,
        monitor_closed_continuous=0.0,
        outputs={n: p.file_hash(directory / n) for n in names},
    )
    return body


@pytest.fixture
def lifecycle(monkeypatch, tmp_path):
    monkeypatch.setattr(p, "ROOT", tmp_path)
    monkeypatch.setattr(p, "source_map", lambda *a: {"synthetic.py": "a" * 64})
    monkeypatch.setattr(p, "runtime_versions", lambda: {"fixture": True})
    config = tmp_path / p.CONFIG
    config.parent.mkdir(parents=True)
    config.write_text("{}")
    directory = tmp_path / "owned"
    directory.mkdir()
    grant = dict(
        source_map=p.source_map(),
        dependencies=p.runtime_versions(),
        config_sha256=p.file_hash(config),
    )
    p.durable_json(directory / "grant.json", grant)
    body = body_fixture(directory)
    dispatch = dict(
        parent_confirms_normal_exit=True,
        child_reaped=True,
        within_deadline=True,
        returncode=0,
        parent_error=None,
        exit_observed_continuous=0.1,
    )
    return directory, grant, body, dispatch


@pytest.mark.parametrize(
    "field,value",
    [
        ("parent_confirms_normal_exit", False),
        ("child_reaped", False),
        ("within_deadline", False),
        ("returncode", -15),
        ("parent_error", "stalled after body"),
    ],
)
def test_body_complete_stalled_or_failed_exit_rejected(lifecycle, field, value):
    directory, grant, body, dispatch = lifecycle
    dispatch[field] = value
    with pytest.raises(ValueError):
        rt.accept_body(body, dispatch, grant, directory, Clock(), 10)


@pytest.mark.parametrize(
    "mutation",
    [
        "source",
        "config",
        "resource",
        "cleanup",
        "partial",
        "inflight",
        "calibration",
        "output",
        "pairing",
    ],
)
def test_parent_acceptance_identity_resources_and_counters(lifecycle, mutation):
    directory, grant, body, dispatch = lifecycle
    rt.accept_body(body, dispatch, grant, directory, Clock(), 10)
    if mutation == "source":
        body["source_map"] = {}
    if mutation == "config":
        body["config_sha256"] = "b" * 64
    if mutation == "resource":
        body["resources"]["peak_rss_bytes"] = 2**30 + 1
    if mutation == "cleanup":
        body["cleanup_seconds"] = 2.1
    if mutation == "partial":
        body["counters"]["optimizer_steps_completed"] = 11
    if mutation == "inflight":
        body["counters"]["optimizer_steps_inflight"] = 1
    if mutation == "calibration":
        body["counters"]["synthetic_calibrations"] = 5
    if mutation == "output":
        (directory / "report.json").write_text("{}")
    if mutation == "pairing":
        body["all_pairing_restoration_checks"] = False
    with pytest.raises(ValueError):
        rt.accept_body(body, dispatch, grant, directory, Clock(), 10)


@pytest.mark.parametrize(
    "failure",
    [
        "assertion_start",
        "assertion_loss",
        "assertion_release",
        "dispatch",
        "publication",
        "counter_corruption",
    ],
)
def test_native_adapter_failures_preserve_attempt_release(
    monkeypatch, tmp_path, failure
):
    clock = Clock()
    monkeypatch.setattr(native, "__name__", "__main__")
    monkeypatch.setattr(p, "ROOT", tmp_path)
    config = tmp_path / p.CONFIG
    config.parent.mkdir(parents=True)
    config.write_text("{}")
    monkeypatch.setattr(p, "load_config", lambda: None)
    monkeypatch.setattr(p, "source_map", lambda *a: {"synthetic.py": "a" * 64})
    monkeypatch.setattr(p, "runtime_versions", lambda: {"fixture": True})
    monkeypatch.setattr(rt, "ContinuousClock", lambda: clock)
    monkeypatch.setattr(rt, "alarm", lambda *a: nullcontext())
    monkeypatch.setattr(rt, "parent_check", lambda **k: 20 * 2**20)

    class Assertion:
        identity = "0xa"
        evidence = dict(released=False)

        def __init__(self, *_):
            self.evidence = dict(released=False)

        def start(self, *_):
            if failure == "assertion_start":
                raise GuardError("synthetic creation failure")

        def check(self, *a, **k):
            if failure == "assertion_loss":
                raise GuardError("synthetic assertion loss")

        def release(self, *a):
            if failure == "assertion_release":
                raise GuardError("synthetic release failure")
            self.evidence["released"] = True
            return dict(self.evidence)

    monkeypatch.setattr(rt, "IdleAssertion", Assertion)

    def dispatch(command, log, **kwargs):
        assert command[2] == "latenttrigger.research.controlled_activation.native"
        directory = log.parent
        if failure == "dispatch":
            raise GuardError("synthetic dispatch failure")
        body = body_fixture(directory)
        p.durable_json(directory / "receipt.json", body, exclusive=True)
        if failure == "counter_corruption":
            (directory / "counters.json").write_text("{broken")
        return dict(
            parent_confirms_normal_exit=True,
            child_reaped=True,
            within_deadline=True,
            returncode=0,
            parent_error=None,
            exit_observed_continuous=0.1,
        )

    monkeypatch.setattr(rt, "supervise", dispatch)
    original = p.durable_json

    def publication(path, *args, **kwargs):
        if failure == "publication" and path.name == "parent-acceptance.json":
            raise OSError("synthetic publication failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(p, "durable_json", publication)
    directory, result = native.run_native()
    assert result["status"] == "failed_synthetic_preserved"
    assert (directory / "workflow.json").is_file() and not (
        directory / "parent-acceptance.json"
    ).exists()
    assert result["sleep_assertion"]["released"] == (failure != "assertion_release")
    # A second fixture invocation uses a new path, preserving the first failed record.
    other, _ = native.run_native()
    assert other != directory and (directory / "workflow.json").is_file()


def test_duplicate_json_and_symlink_bytes(tmp_path):
    path = tmp_path / "record.json"
    path.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError):
        p.read(path)
    alias = tmp_path / "alias.json"
    alias.symlink_to(path)
    with pytest.raises(ValueError):
        p.file_hash(alias)
