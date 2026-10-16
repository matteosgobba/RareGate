"""Synthetic accounting/boundary/lifecycle vetoes; no real assertion/worker here."""

import copy
import json
import os
from pathlib import Path

import pytest

from raregate.evaluation.guard import NATIVE_METHOD, PRESSURE_METHOD, GuardError
from raregate.simulation import native
from raregate.simulation import protocol as p
from raregate.simulation import runtime as rt
from raregate.simulation.sweep import validate_aggregates


def sample(**changes):
    return dict(
        peak_rss_bytes=10000,
        native_heap_reserved_bytes=10000,
        native_heap_in_use_bytes=5000,
        workspace_method=NATIVE_METHOD,
        pressure_dispatch_flags=1,
        pressure_errno=None,
        pressure_method=PRESSURE_METHOD,
        **changes,
    )


def test_explicit_rss_cap_and_warn_unknown_pressure():
    for pressure, errno in [(2, None), (None, 0)]:
        v = sample()
        v.update(pressure_dispatch_flags=pressure, pressure_errno=errno)
        guard = rt.SimulationGuard(10, probe=lambda v=v: v, clock=lambda: 0)
        guard.check()
        assert guard.error is None
    v = sample()
    v["peak_rss_bytes"] = 2**30 + 1
    guard = rt.SimulationGuard(10, probe=lambda: v, clock=lambda: 0)
    with pytest.raises(GuardError, match="1GiB"):
        guard.check()
    assert guard.error and guard.peak_rss == 2**30 + 1


@pytest.mark.parametrize(
    "change",
    [
        {"pressure_dispatch_flags": 4},
        {"peak_rss_bytes": None},
        {"native_heap_reserved_bytes": 512 * 2**20 + 1},
        {"workspace_method": "unknown"},
    ],
)
def test_primary_pressure_accounting_veto(change):
    v = sample()
    v.update(change)
    guard = rt.SimulationGuard(10, probe=lambda: v, clock=lambda: 0)
    with pytest.raises(GuardError):
        guard.check()


def test_continuous_advances_through_simulated_suspend():
    class Clock:
        tick = 0

        def __call__(self):
            return self.tick

    clock = Clock()

    def probe():
        clock.tick = 15
        return sample()

    with pytest.raises(GuardError):
        rt.SimulationGuard(10, probe=probe, clock=clock).check()


@pytest.mark.parametrize("phase", ["simulation", "reporting"])
@pytest.mark.parametrize(
    "event", ["socket.connect", "subprocess.Popen", "os.system", "urllib.Request"]
)
def test_worker_no_network_or_children(tmp_path, phase, event):
    with pytest.raises(PermissionError):
        rt.check_access(tmp_path, tmp_path / "owned", phase, event, ())


@pytest.mark.parametrize(
    "name",
    [
        "torch",
        "sklearn",
        "h5py",
        "raregate.models.pca",
        "raregate.training.autoencoder",
    ],
)
def test_no_model_import(tmp_path, name):
    with pytest.raises(PermissionError):
        rt.check_access(tmp_path, tmp_path / "owned", "simulation", "import", (name,))


def test_report_only_owned_aggregates_and_no_array_aliases(tmp_path):
    owned = tmp_path / "results/simulation/owned"
    owned.mkdir(parents=True)
    timing = tmp_path / next(iter(p.PINS))
    timing.parent.mkdir(parents=True, exist_ok=True)
    timing.write_text("fixture")
    rt.check_access(tmp_path, owned, "simulation", "open", (str(timing), "r", 0))
    with pytest.raises(PermissionError):
        rt.check_access(tmp_path, owned, "reporting", "open", (str(timing), "r", 0))
    rt.check_access(
        tmp_path, owned, "reporting", "open", (str(owned / "aggregates.json"), "r", 0)
    )
    for name in ("data/features.npy", "artifacts/model.json", "sources/source.txt"):
        with pytest.raises(PermissionError):
            rt.check_access(
                tmp_path, owned, "simulation", "open", (str(tmp_path / name), "r", 0)
            )
    with pytest.raises(PermissionError):
        rt.check_access(
            tmp_path,
            owned,
            "simulation",
            "open",
            (str(owned / "arrays.npy"), "w", os.O_CREAT),
        )
    alias = owned / "alias.json"
    alias.symlink_to(timing)
    with pytest.raises(PermissionError):
        rt.check_access(tmp_path, owned, "reporting", "open", (str(alias), "r", 0))


def test_storage_symlink_file_log_total_and_json_bounds(tmp_path, monkeypatch):
    alias = tmp_path / "link"
    alias.symlink_to("/dev/null")
    with pytest.raises(ValueError):
        rt.storage_check(tmp_path)
    alias.unlink()
    f = tmp_path / "worker.log"
    with f.open("wb") as stream:
        stream.truncate(2**20 + 1)
    with pytest.raises(ValueError):
        rt.storage_check(tmp_path)
    f.unlink()
    with pytest.raises(ValueError):
        p.durable_json(tmp_path / "large.json", {"x": "a" * (4 * 2**20)})
    p.durable_json(tmp_path / "once.json", {"ok": True}, exclusive=True)
    with pytest.raises(FileExistsError):
        p.durable_json(tmp_path / "once.json", {"ok": False}, exclusive=True)
    assert p.read(tmp_path / "once.json") == {"ok": True}


def test_body_completion_does_not_accept_exit_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "source_map", lambda: {"code": "hash"})
    monkeypatch.setattr(p, "dependencies", lambda: {"toy": "1"})
    grant = dict(
        phase="reporting", source_map=p.source_map(), dependencies=p.dependencies()
    )
    p.durable_json(tmp_path / "grant.json", grant)
    names = ["latency.png", "loss.png", "sensitivity.png", "reporting.json"]
    for name in names:
        (tmp_path / name).write_text("fixture")
    body = dict(
        status="body_complete_awaiting_exit",
        phase="reporting",
        source_map=p.source_map(),
        dependencies=p.dependencies(),
        grant_sha256=p.file_hash(tmp_path / "grant.json"),
        outputs={n: p.file_hash(tmp_path / n) for n in names},
        resources=dict(
            latched_error=None,
            owned_thread_alive=False,
            peak_rss_bytes=10000,
            native_heap_reserved_bytes=10000,
        ),
        cleanup_seconds=0.01,
        worker_seconds=1,
        monitor_closed_continuous=1,
    )
    dispatch = dict(
        returncode=0,
        parent_confirms_normal_exit=True,
        child_reaped=True,
        within_deadline=True,
        parent_error=None,
        exit_observed_continuous=1.2,
    )
    assert rt.accept_body(body, dispatch, grant, tmp_path, lambda: 2, 10)[
        "terminal_unaccounted_continuous_seconds"
    ] == pytest.approx(0.2)
    for k, v in [
        ("returncode", 1),
        ("child_reaped", False),
        ("within_deadline", False),
        ("parent_error", "timeout"),
        ("parent_confirms_normal_exit", False),
    ]:
        changed = dict(dispatch)
        changed[k] = v
        with pytest.raises(ValueError):
            rt.accept_body(body, changed, grant, tmp_path, lambda: 2, 10)
    for k, v in [
        ("cleanup_seconds", 2.1),
        ("worker_seconds", 61),
        ("status", "partial"),
    ]:
        changed = copy.deepcopy(body)
        changed[k] = v
        with pytest.raises(ValueError):
            rt.accept_body(changed, dispatch, grant, tmp_path, lambda: 2, 10)
    (tmp_path / "loss.png").write_text("altered")
    with pytest.raises(ValueError):
        rt.accept_body(body, dispatch, grant, tmp_path, lambda: 2, 10)


def test_aggregate_rejects_missing_event_export_and_csv_mismatch(tmp_path):
    for report in ({}, dict(kind="synthetic_queue_aggregates", events=[1])):
        with pytest.raises(ValueError):
            validate_aggregates(report)
    (tmp_path / "scenarios.csv").write_text("scenario_id\nS001\n")
    with pytest.raises(ValueError):
        native.verify_csv(tmp_path, {"rows": [{"scenario_id": "S002"}]})


def test_unaccepted_missing_source_identity(tmp_path):
    with pytest.raises(ValueError):
        p.verify_acceptance(tmp_path / "software-acceptance.json")
    with pytest.raises(ValueError):
        p.nonsymlink(tmp_path, "data/events.npy")


def test_assertion_failure_preserved_no_worker_launch(tmp_path, monkeypatch):
    from contextlib import nullcontext

    class Clock:
        def __call__(self):
            return 1

        def snapshot(self):
            return {"continuous": 1}

    class Assertion:
        evidence = {"released": False}

        def __init__(self, clock):
            self.evidence = {"released": False}

        def start(self, deadline):
            raise GuardError("assertion failure")

        def release(self, deadline):
            self.evidence["released"] = True
            return self.evidence

    monkeypatch.setattr(native, "NAMESPACE", tmp_path / "runs")
    monkeypatch.setattr(rt, "ContinuousClock", Clock)
    monkeypatch.setattr(rt, "alarm", lambda *a: nullcontext())
    monkeypatch.setattr(rt, "parent_check", lambda **k: 10000)
    monkeypatch.setattr(rt, "IdleAssertion", Assertion)
    monkeypatch.setattr(p, "source_map", lambda: {"code": "sha"})
    monkeypatch.setattr(p, "dependencies", lambda: {"fixture": True})
    monkeypatch.setattr(p, "load_config", lambda: p.EXPECTED)
    monkeypatch.setattr(
        p,
        "verify_acceptance",
        lambda path: {"status": "software_accepted_synthetic_simulator_only"},
    )
    monkeypatch.setattr(p, "nonsymlink", lambda *a: Path("/dev/null"))
    monkeypatch.setattr(p, "file_hash", lambda path: "fixture")
    monkeypatch.setattr(p, "PINS", {"allowed": "fixture"})
    base, result = native.run_native(tmp_path / "acceptance")
    assert (
        result["status"] == "failed_synthetic_preserved"
        and result["sleep_assertion"]["released"]
    )
    assert (
        not result["phases"]
        and json.loads((base / "workflow.json").read_text())["status"]
        == "failed_synthetic_preserved"
    )


@pytest.mark.parametrize("failure", ["loss", "release"])
def test_assertion_loss_or_release_failure_cannot_accept(
    tmp_path, monkeypatch, failure
):
    from contextlib import nullcontext

    class Clock:
        def __call__(self):
            return 1

        def snapshot(self):
            return {"continuous": 1}

    class Assertion:
        identity = "fixture"

        def __init__(self, clock):
            self.evidence = {"released": False}

        def start(self, deadline):
            if failure == "release":
                raise GuardError("setup failure before cleanup")

        def check(self, deadline, force=False):
            raise GuardError("owned assertion lost")

        def release(self, deadline):
            if failure == "release":
                raise GuardError("release not confirmed")
            self.evidence["released"] = True
            return self.evidence

    def dispatch(*args, **kwargs):
        try:
            kwargs["monitor"]()
        except GuardError as e:
            return dict(
                returncode=1,
                parent_error=str(e),
                child_reaped=True,
                within_deadline=True,
                parent_confirms_normal_exit=False,
            )
        raise AssertionError("loss must stop dispatch")

    monkeypatch.setattr(native, "NAMESPACE", tmp_path / "runs")
    monkeypatch.setattr(rt, "ContinuousClock", Clock)
    monkeypatch.setattr(rt, "alarm", lambda *a: nullcontext())
    monkeypatch.setattr(rt, "parent_check", lambda **k: 10000)
    monkeypatch.setattr(rt, "IdleAssertion", Assertion)
    monkeypatch.setattr(rt, "supervise", dispatch)
    monkeypatch.setattr(p, "source_map", lambda: {"code": "sha"})
    monkeypatch.setattr(p, "dependencies", lambda: {"fixture": True})
    monkeypatch.setattr(p, "load_config", lambda: p.EXPECTED)
    monkeypatch.setattr(
        p,
        "verify_acceptance",
        lambda path: {"status": "software_accepted_synthetic_simulator_only"},
    )
    monkeypatch.setattr(p, "nonsymlink", lambda *a: Path("/dev/null"))
    monkeypatch.setattr(p, "file_hash", lambda path: "fixture")
    monkeypatch.setattr(p, "PINS", {"allowed": "fixture"})
    base, result = native.run_native(tmp_path / "acceptance")
    assert (
        result["status"] == "failed_synthetic_preserved"
        and not (base / "parent-acceptance.json").exists()
    )
    if failure == "release":
        assert "release_error" in result["sleep_assertion"]
    else:
        assert result["sleep_assertion"]["released"]
        assert "assertion lost" in result["phases"][0]["dispatch"]["parent_error"]
