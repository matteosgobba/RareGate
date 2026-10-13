"""Synthetic lifecycle/resource/access tests; no native or operational source work."""

from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from latenttrigger.benchmarks import development_decision_native as native
from latenttrigger.benchmarks import development_decision_protocol as p
from latenttrigger.benchmarks import development_decision_runtime as rt
from latenttrigger.evaluation.guard import GuardError


@pytest.mark.parametrize(
    "event,args",
    [
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
    monkeypatch.setattr(
        rt,
        "ServiceGuard",
        lambda *a, **kw: SimpleNamespace(
            __enter__=lambda: None,
            check=lambda: None,
            close=lambda: None,
            report=lambda: {},
        ),
    )
    monkeypatch.setattr(rt, "supervise", supervisor)
    from latenttrigger.benchmarks import development_decision_contract as contract

    monkeypatch.setattr(
        contract,
        "identity",
        lambda *a, **kw: dict(task="0041", kind="synthetic_fixed_matrix"),
    )
    monkeypatch.setattr(p, "file_hash", lambda *args: "fixture")
    base, result = native.run(synthetic_directory=tmp_path / "native-fixture")
    assert (
        result["status"] == "failed_prerequisites_no_retry"
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
    grant = dict(
        identity={"task": "0041"},
        source_map={},
        dependencies={},
        synthetic_only=True,
        phase="reporting",
    )
    p.durable_json(tmp_path / "grant.json", grant)
    names = (
        "cells.csv",
        "summary.json",
        "joint-cost.png",
        "chronology.png",
    )
    for name in names:
        (tmp_path / name).write_bytes(b"owned fixture bytes")
    body = dict(
        status="body_complete_awaiting_exit",
        identity=grant["identity"],
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
        == "parent_accepted_worker"
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
        body["outputs"].pop("joint-cost.png")
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


@pytest.mark.parametrize("fault", ["critical", "invalid_primary", "unavailable"])
def test_scoped_pressure_primary_policy(fault):
    from latenttrigger.benchmarks.guard import NATIVE_METHOD, PRESSURE_METHOD

    row = dict(
        peak_rss_bytes=1,
        native_heap_reserved_bytes=1,
        native_heap_in_use_bytes=0,
        workspace_method=NATIVE_METHOD,
        pressure_dispatch_flags=2,
        pressure_errno=None,
        pressure_method=PRESSURE_METHOD,
    )
    if fault == "critical":
        row["pressure_dispatch_flags"] = 4
    if fault == "invalid_primary":
        row["workspace_method"] = "invented"
    if fault == "unavailable":
        row["pressure_dispatch_flags"] = None
        row["pressure_errno"] = 1
    guard = rt.ServiceGuard(10, clock=lambda: 1, probe=lambda: row, notify=False)
    if fault == "unavailable":
        guard.check()
        assert guard.report()["pressure_counts"]["unknown"] > 0
    else:
        with pytest.raises(GuardError):
            guard.check()


def test_module_presence_does_not_allow_store_fitting_optimizer(tmp_path):
    import numpy as np

    from latenttrigger.benchmarks import core

    blocked = rt.ProhibitedOperations(core)
    try:
        for call in (
            lambda: core.ProcessedStore(tmp_path),
            lambda: core.prepare_input(None, None, None, None, None),
            lambda: core.PCAReconstruction.fit(np.ones((10, 8)), feature_names=[]),
            lambda: core.torch.optim.Adam([]),
        ):
            with pytest.raises(PermissionError):
                call()
        from sklearn.decomposition import PCA

        with pytest.raises(PermissionError):
            PCA().fit(np.ones((10, 8)))
    finally:
        blocked.restore()


def test_canonical_build_hash_is_not_raw_build_hash():
    from latenttrigger.benchmarks.pytorch_onnx_cpu_protocol import build_hashes

    text = "owned synthetic CPU build\n"
    values = build_hashes(text)
    assert values["canonical_JSON_string_sha256"] == p.digest(text)
    assert values["canonical_JSON_string_sha256"] != values["raw_UTF8_byte_sha256"]


def test_owned_array_ceiling_resource_meanings():
    limit = p.load()["limits"]
    assert (
        limit["worker_RSS_bytes"] == 2**30
        and limit["native_reserved_bytes"] == 512 * 2**20
    )
    assert limit["owned_array_buffer_bytes"] == 64 * 2**20


def test_streaming_build_hash_bounded_reads(tmp_path, monkeypatch):
    import hashlib

    payload = b"owned binary metadata" * 100000
    f = tmp_path / "library.dylib"
    f.write_bytes(payload)
    assert p.stream_hash(f) == hashlib.sha256(payload).hexdigest()


def test_only_granted_owned_fixture_arrays(tmp_path):
    owned = tmp_path / "owned"
    owned.mkdir()
    path = owned / "fixture.npy"
    path.write_bytes(b"synthetic header fixture")
    with pytest.raises(PermissionError):
        rt.check_access(tmp_path, owned, set(), "open", (str(path), "r", 0))
    rt.check_access(tmp_path, owned, set(), "open", (str(path), "r", 0), synthetic=True)
    with pytest.raises(PermissionError):
        rt.check_access(
            tmp_path,
            owned,
            set(),
            "open",
            (str(tmp_path / "data/other.npy"), "r", 0),
            synthetic=True,
        )
