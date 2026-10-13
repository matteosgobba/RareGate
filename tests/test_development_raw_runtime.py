"""Synthetic lifecycle/resource/access tests; no native or operational source work."""

from contextlib import nullcontext

import pytest

from latenttrigger.benchmarks import development_raw_native as native
from latenttrigger.benchmarks import development_raw_protocol as p
from latenttrigger.benchmarks import development_raw_runtime as rt
from latenttrigger.evaluation.guard import GuardError


@pytest.mark.parametrize(
    "event,args",
    [
        ("import", ("torch",)),
        ("import", ("latenttrigger.models.pca",)),
        ("import", ("latenttrigger.data.processed",)),
        ("import", ("latenttrigger.data.preprocessing",)),
        ("socket.connect", ()),
        ("subprocess.Popen", ()),
    ],
)
def test_no_broad_readers_models_network_children(tmp_path, event, args):
    with pytest.raises(PermissionError):
        rt.check_access(tmp_path, tmp_path / "owned", set(), event, args)


@pytest.mark.parametrize(
    "name",
    (
        "particles.npy",
        "event_features.npy",
        "split_codes.npy",
        "event_ids.npy",
        "scores.npy",
        "labels.npy",
        "fingerprints.npy",
        "validation.npy",
        "model.json",
    ),
)
def test_only_approved_member_raw_metadata_golden_bytes(tmp_path, name):
    owned = tmp_path / "owned"
    allowed = {tmp_path / p.MEMBERSHIP, tmp_path / p.GOLDEN, tmp_path / p.RAW}
    for folder in ("data", "results", "artifacts", "sources"):
        with pytest.raises(PermissionError):
            rt.check_access(
                tmp_path,
                owned,
                allowed,
                "open",
                (str(tmp_path / folder / name), "r", 0),
            )
    for path in allowed:
        rt.check_access(tmp_path, owned, allowed, "open", (str(path), "r", 0))
    with pytest.raises(PermissionError):
        rt.check_access(
            tmp_path, owned, allowed, "open", (str(tmp_path / p.MEMBERSHIP), "w", 0)
        )


def test_atomic_reservation_one_winner(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "ROOT", tmp_path)
    base = tmp_path / p.OUTPUT / "a"
    base.mkdir(parents=True)
    plan = dict(prompt_sha256="synthetic")
    p.durable_json(base / "plan.json", plan)
    native.reserve(base, plan)
    before = (tmp_path / p.OUTPUT / "attempt.json").read_bytes()
    with pytest.raises(FileExistsError):
        native.reserve(base, plan)
    assert (tmp_path / p.OUTPUT / "attempt.json").read_bytes() == before


@pytest.mark.parametrize("failure", ("setup", "loss", "release"))
def test_assertion_failure_release_preserved_no_operational_load(
    tmp_path, monkeypatch, failure
):
    spec = p.load()

    class Clock:
        def __call__(self):
            return 1.0

        def snapshot(self):
            return dict(continuous=1.0)

    class Assertion:
        identity = "fixture"

        def __init__(self, clock):
            self.evidence = dict(released=False)

        def start(self, deadline):
            if failure in ("setup", "release"):
                raise RuntimeError("assertion setup")

        def check(self, deadline, force=False):
            raise RuntimeError("assertion lost")

        def release(self, deadline):
            if failure == "release":
                raise RuntimeError("release failed")
            self.evidence["released"] = True
            return self.evidence

    def supervisor(*args, **kwargs):
        kwargs["monitor"]()
        pytest.fail("Loss must stop")

    monkeypatch.setattr(p, "ROOT", tmp_path)
    monkeypatch.setattr(p, "load", lambda: spec)
    monkeypatch.setattr(p, "source_map", lambda: {})
    monkeypatch.setattr(p, "dependencies", lambda: {})
    monkeypatch.setattr(rt, "ContinuousClock", Clock)
    monkeypatch.setattr(rt, "alarm", lambda *args: nullcontext())
    monkeypatch.setattr(rt, "IdleAssertion", Assertion)
    monkeypatch.setattr(rt, "parent_check", lambda **kw: 1)
    monkeypatch.setattr(rt, "supervise", supervisor)
    monkeypatch.setattr(p, "file_hash", lambda *args: "fixture")
    base, result = native.run(synthetic_directory=tmp_path / "native-fixture")
    assert (
        result["status"] == "failed_before_operational_reservation"
        and not result["reserved"]
        and not (base / "parent-acceptance.json").exists()
    )
    if failure == "release":
        assert "release_error" in result["sleep_assertion"]
    else:
        assert result["sleep_assertion"]["released"]


@pytest.mark.parametrize(
    "failure", ("exit", "reap", "deadline", "resource", "cleanup", "outputs", "body")
)
def test_parent_acceptance_requires_reaping_caps_complete_output(
    tmp_path, monkeypatch, failure
):
    monkeypatch.setattr(p, "source_map", lambda: {})
    monkeypatch.setattr(p, "dependencies", lambda: {})
    grant = dict(source_map={}, dependencies={}, synthetic_only=True)
    p.durable_json(tmp_path / "grant.json", grant)
    names = ("synthetic.json", "geometry.json", "selected-ids.npy")
    for name in names:
        (tmp_path / name).write_bytes(b"owned fixture bytes")
    body = dict(
        status="body_complete_awaiting_exit",
        source_map={},
        dependencies={},
        grant_sha256=p.file_hash(tmp_path / "grant.json"),
        outputs={n: p.file_hash(tmp_path / n) for n in names},
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
    assert (
        rt.accept(body, dispatch, grant, tmp_path, lambda: 2, 10)["status"]
        == "parent_accepted_metadata_worker"
    )
    if failure == "exit":
        dispatch["returncode"] = 1
    if failure == "reap":
        dispatch["child_reaped"] = False
    if failure == "deadline":
        dispatch["within_deadline"] = False
    if failure == "resource":
        body["resources"]["native_heap_reserved_bytes"] = 2**30
    if failure == "cleanup":
        body["cleanup_seconds"] = 3
    if failure == "outputs":
        body["outputs"].pop("geometry.json")
    if failure == "body":
        body["status"] = "complete"
    with pytest.raises(ValueError):
        rt.accept(body, dispatch, grant, tmp_path, lambda: 2, 10)


def test_storage_log_and_total_bounds(tmp_path):
    log = tmp_path / "worker.log"
    log.write_bytes(b"x" * (2**20 + 1))
    with pytest.raises(ValueError):
        rt.storage(tmp_path)
    log.unlink()
    (tmp_path / "link").symlink_to(tmp_path)
    with pytest.raises(ValueError):
        rt.storage(tmp_path)


def test_continuous_suspension_and_narrow_guard_ceiling():
    from latenttrigger.benchmarks.guard import NATIVE_METHOD, PRESSURE_METHOD

    now = [1.0]
    row = dict(
        peak_rss_bytes=1,
        native_heap_reserved_bytes=1,
        native_heap_in_use_bytes=0,
        workspace_method=NATIVE_METHOD,
        pressure_dispatch_flags=2,
        pressure_errno=None,
        pressure_method=PRESSURE_METHOD,
    )
    guard = rt.ServiceGuard(10, clock=lambda: now[0], probe=lambda: row, notify=False)
    guard.check()
    row["peak_rss_bytes"] = 2**30 + 1
    with pytest.raises(GuardError):
        guard.check()
    row["peak_rss_bytes"] = 1
    guard = rt.ServiceGuard(10, clock=lambda: now[0], probe=lambda: row, notify=False)
    now[0] = 11
    with pytest.raises(GuardError):
        guard.check()
