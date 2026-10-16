"""Self-contained history/concurrency/authorization tests; no operational receipts."""

import copy
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest

from raregate.supervision import particle_launcher as io
from raregate.supervision import particle_readiness as ctl
from raregate.supervision import particle_readiness_worker as worker

REAL_IDENTITY = ctl.identity


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    bind = {
        "workflow_sha256": "synthetic-test-only",
        "source_sha256": {"fake": "hash"},
        "historical_torch_version": "same",
        "current_torch_version": "same",
    }
    monkeypatch.setattr(ctl, "identity", lambda: copy.deepcopy(bind))
    monkeypatch.setattr(io, "assert_lightweight", lambda: None)
    offset = [0.0]
    lock = threading.Lock()

    def advance(value):
        with lock:
            offset[0] += value

    monkeypatch.setattr(
        ctl,
        "time",
        SimpleNamespace(
            monotonic=lambda: time.monotonic() + offset[0], advance=advance
        ),
    )
    return tmp_path, bind


def receipt_for(res, status="not_ready"):
    start = res["started_monotonic"]
    g = {
        "synthetic_not_readiness": False,
        "host_backend": "system_vm_stat_oneshot_host_v4",
        "host_validation_status": "valid_primary_fields",
        "host_age_upper_seconds": 0.1,
        "available_bytes": 4831838208,
        "native_heap_reserved_bytes": 536870912,
        "peak_rss_bytes": 6442450944,
        "pressure_dispatch_flags": None,
    }
    # Parser fixture only. No actual worker or live readiness is authorized by it.
    return {
        "status": status,
        "invocation_id": res["invocation_id"],
        "action": res["action"],
        "binding": res["binding"],
        "reservation_sha256": io.file_hash(
            ctl.invocation_path(res["invocation_id"]) / "reservation.json"
        ),
        "check_only_zero_data_steps": True,
        "real_slot_reserved_by_check": False,
        "elapsed_seconds_including_imports_cleanup": 6.0,
        "finished_monotonic": start + 6,
        "readings": [
            {"sample_monotonic": start + x, "guard": copy.deepcopy(g)}
            for x in (0.5, 3.0, 5.5)
        ]
        if status == "ready"
        else [],
        "resources": {
            "sampler": {"latched_failure": None, "owned_thread_alive": False}
        },
        "error": None
        if status == "ready"
        else "Verified pressure warning/critical veto.",
    }


def fake_dispatch(statuses):
    lock = threading.Lock()
    iterator = iter(statuses)

    def dispatch(command, *args, **kwargs):
        assert "--check" in command and "--phase" not in command
        uid = command[command.index("--check") + 1]
        directory = ctl.invocation_path(uid)
        res = io.read(directory / "reservation.json")
        # Advance the test clock; immutable reservation bytes are never rewritten.
        ctl.time.advance(6)
        with lock:
            status = next(iterator)
        io.exclusive(directory / "receipt.json", receipt_for(res, status))
        return {"returncode": 0 if status == "ready" else 2}

    return dispatch


def test_two_failed_checks_preserve_both_and_no_real_slot(sandbox, monkeypatch):
    root, _ = sandbox
    monkeypatch.setattr(io, "dispatch", fake_dispatch(["not_ready", "not_ready"]))
    a = ctl.invoke("check_readiness")
    before = (ctl.invocation_path(a["invocation_id"]) / "receipt.json").read_bytes()
    b = ctl.invoke("check_readiness")
    assert (
        a["invocation_id"] != b["invocation_id"]
        and a["status"] == b["status"] == "not_ready"
    )
    assert (
        ctl.invocation_path(a["invocation_id"]) / "receipt.json"
    ).read_bytes() == before
    assert (
        not (root / ctl.SLOT).exists()
        and not (root / ctl.PLAN).exists()
        and not (root / ctl.OUTPUT).exists()
    )


def test_failed_then_ready_check_never_starts_data_or_reserves(sandbox, monkeypatch):
    root, _ = sandbox
    monkeypatch.setattr(io, "dispatch", fake_dispatch(["not_ready", "ready"]))
    monkeypatch.setattr(
        ctl, "reserve_real", lambda *_: pytest.fail("check-only must never reserve")
    )
    monkeypatch.setattr(
        ctl,
        "dispatch_real",
        lambda *_: pytest.fail("check-only must never dispatch data"),
    )
    assert ctl.invoke("check_readiness")["status"] == "not_ready"
    assert ctl.invoke("check_readiness")["status"] == "ready"
    assert not (root / ctl.SLOT).exists()


def test_parallel_independent_checks_preserve_disjoint_receipts(sandbox, monkeypatch):
    root, _ = sandbox
    monkeypatch.setattr(io, "dispatch", fake_dispatch(["not_ready"] * 8))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: ctl.invoke("check_readiness"), range(8)))
    assert len({r["invocation_id"] for r in results}) == 8
    assert len(list((root / ctl.HISTORY_ROOT).glob("*/receipt.json"))) == 8
    assert not (root / ctl.SLOT).exists()


def test_two_run_actions_compete_for_one_canonical_anchor_no_data_for_loser(
    sandbox, monkeypatch
):
    root, _ = sandbox
    barrier = threading.Barrier(2)
    calls = []
    dispatch = fake_dispatch(["ready", "ready"])

    def paired(*args, **kwargs):
        result = dispatch(*args, **kwargs)
        barrier.wait(timeout=5)
        return result

    monkeypatch.setattr(io, "dispatch", paired)

    def real(plan):
        calls.append(plan["readiness_id"])
        return {
            "status": "bounded_characterization_passed_canonical_pending",
            "new_steps_started": 96,
            "new_steps_completed": 96,
            "cumulative_started_steps": 192,
        }

    monkeypatch.setattr(ctl, "dispatch_real", real)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: ctl.invoke("run_characterization"), range(2)))
    assert len(calls) == 1 and sum("real_result" in r for r in results) == 1
    assert sum(r["status"] == "error" for r in results) == 1
    slot = io.read(root / ctl.SLOT)
    assert (
        slot["task"] == "0016"
        and slot["maximum_additional_started_steps"] == 96
        and slot["maximum_cumulative_started_steps"] == 192
    )
    assert ctl.SLOT == ctl.previous.SLOT and ctl.OUTPUT == ctl.previous.OUTPUT


@pytest.mark.parametrize(
    "contents",
    [
        {},
        {"status": "partial", "new_inflight_steps": 1},
        {"task": "foreign"},
        {"status": "consumed"},
    ],
)
def test_existing_slot_readiness_is_separate_and_run_never_clears_it(
    sandbox, monkeypatch, contents
):
    root, _ = sandbox
    io.exclusive(root / ctl.SLOT, contents)
    before = (root / ctl.SLOT).read_bytes()
    monkeypatch.setattr(io, "dispatch", fake_dispatch(["ready", "ready"]))
    monkeypatch.setattr(
        ctl, "dispatch_real", lambda *_: pytest.fail("consumed slot must block data")
    )
    r = ctl.invoke("check_readiness")
    assert r["status"] == "ready" and not r["execution_permission"]["available"]
    assert ctl.invoke("run_characterization")["status"] == "error"
    assert (root / ctl.SLOT).read_bytes() == before


@pytest.mark.parametrize(
    "bad",
    [
        "../escape",
        "/tmp/a",
        "A" * 32,
        "a" * 31,
        "a" * 33,
        None,
        True,
        "ab/../" + "c" * 32,
    ],
)
def test_safe_unique_history_ids(bad, sandbox):
    with pytest.raises(ValueError):
        ctl.invocation_path(bad)


@pytest.mark.parametrize(
    "bad",
    [
        "foreign",
        "stale",
        "partial",
        "synthetic",
        "age",
        "pressure_bool",
        "pressure_warn",
        "timestamp",
    ],
)
def test_malformed_stale_foreign_receipt_refusal(sandbox, bad):
    root, bind = sandbox
    uid = "a" * 32
    directory = ctl.invocation_path(uid)
    directory.mkdir(parents=True)
    res = {
        "invocation_id": uid,
        "action": "run_characterization",
        "binding": bind,
        "started_monotonic": time.monotonic() - 6,
        "parent_pid": os.getpid(),
    }
    io.exclusive(directory / "reservation.json", res)
    r = receipt_for(res, "ready")
    if bad == "foreign":
        r["binding"] = {}
    if bad == "stale":
        r["elapsed_seconds_including_imports_cleanup"] = 31
    if bad == "partial":
        r["readings"].pop()
    if bad == "synthetic":
        r["readings"][0]["guard"]["synthetic_not_readiness"] = True
    if bad == "age":
        r["readings"][0]["guard"]["host_age_upper_seconds"] = 0.101
    if bad == "pressure_bool":
        r["readings"][0]["guard"]["pressure_dispatch_flags"] = True
    if bad == "pressure_warn":
        r["readings"][0]["guard"]["pressure_dispatch_flags"] = 2
    if bad == "timestamp":
        r["readings"][0]["sample_monotonic"] = float("nan")
    with pytest.raises(ValueError):
        ctl.validate_check(r, res)


def test_old_or_check_only_pass_not_an_execution_bearer(sandbox):
    _, bind = sandbox
    uid = "b" * 32
    d = ctl.invocation_path(uid)
    d.mkdir(parents=True)
    res = {
        "invocation_id": uid,
        "action": "check_readiness",
        "binding": bind,
        "started_monotonic": time.monotonic() - 6,
        "parent_pid": os.getpid(),
    }
    io.exclusive(d / "reservation.json", res)
    r = receipt_for(res, "ready")
    io.exclusive(d / "receipt.json", r)
    forged = copy.deepcopy(r)
    forged["action"] = "run_characterization"
    with pytest.raises(ValueError):
        ctl.reserve_real(forged)
    res["action"] = "run_characterization"
    res["started_monotonic"] = time.monotonic() - 60
    io.atomic(d / "reservation.json", res)
    r = receipt_for(res, "ready")
    io.atomic(d / "receipt.json", r)
    with pytest.raises(ValueError):
        ctl.reserve_real(r)


def test_worker_rechecks_token_parent_source_and_role(sandbox, monkeypatch):
    _, bind = sandbox
    uid = "c" * 32
    d = ctl.invocation_path(uid)
    d.mkdir(parents=True)
    res = {
        "invocation_id": uid,
        "action": "check_readiness",
        "binding": bind,
        "parent_pid": os.getppid(),
        "token": "synthetic",
    }
    io.exclusive(d / "reservation.json", res)
    assert worker.verify_check(uid, "synthetic") == res
    with pytest.raises(ValueError):
        worker.verify_check(uid, "wrong")
    res["parent_pid"] = -1
    io.atomic(d / "reservation.json", res)
    with pytest.raises(ValueError):
        worker.verify_check(uid, "synthetic")
    res["parent_pid"] = os.getppid()
    res["binding"] = {}
    io.atomic(d / "reservation.json", res)
    with pytest.raises(ValueError):
        worker.verify_check(uid, "synthetic")


def test_timeout_bootstrap_history_is_preserved_no_real_reservation(
    sandbox, monkeypatch
):
    root, _ = sandbox

    def fail(command, *args, **kwargs):
        uid = command[command.index("--check") + 1]
        io.exclusive(ctl.invocation_path(uid) / "bootstrap-audit.json", {"events": 0})
        raise TimeoutError("owned worker timeout")

    monkeypatch.setattr(io, "dispatch", fail)
    first = ctl.invoke("check_readiness")
    second = ctl.invoke("check_readiness")
    assert (
        first["status"] == second["status"] == "error"
        and first["invocation_id"] != second["invocation_id"]
    )
    assert all(
        (ctl.invocation_path(r["invocation_id"]) / "bootstrap-audit.json").exists()
        for r in (first, second)
    )
    assert not (root / ctl.SLOT).exists()


def test_pressure_unknown_vs_veto_and_brief_output():
    assert (
        ctl.classify_failure("Verified pressure warning/critical veto.") == "not_ready"
    )
    assert (
        ctl.classify_failure("Policy v2 launch available memory below4.5GiB.")
        == "not_ready"
    )
    assert ctl.classify_failure("Malformed native accounting") == "error"
    r = {
        "status": "not_ready",
        "resources": {
            "last_sample": None,
            "last_process_observation": {"pressure_dispatch_flags": 2},
        },
        "later_diagnostic": {
            "available_gib": 4.8,
            "counts_as_admitted_generation": False,
        },
        "receipt_path": "synthetic-test",
    }
    text = ctl.brief(r)
    assert (
        "WARN" in text
        and "later diagnostic 4.800000" in text
        and "not admission" in text
    )
    assert "zero data/events/steps" in text and "vm_stat_raw" not in text
    r["resources"]["last_process_observation"]["pressure_dispatch_flags"] = None
    assert "pressure unknown" in ctl.brief(r)


def test_one_later_pressure_diagnostic_never_admission(monkeypatch):
    class Query:
        count = 0

        def __init__(self):
            self.child = None
            self.closed = False

        def begin(self):
            self.r, self.w = os.pipe()
            self.query_start = time.monotonic()
            Query.count += 1
            return self.r

        def finish(self):
            return {
                "available_bytes": 4831838208,
                "query_start": self.query_start,
                "query_end": time.monotonic(),
            }

        def close(self):
            os.close(self.r)
            os.close(self.w)
            self.closed = True

    monkeypatch.setattr(worker, "SystemQuery", Query)
    resource = {
        "last_sample": None,
        "last_process_observation": {"pressure_dispatch_flags": 2},
    }
    d = worker.later_diagnostic(resource, time.monotonic() + 2)
    assert (
        Query.count == 1
        and d["status"] == "available"
        and not d["authorizes_work"]
        and not d["counts_as_admitted_generation"]
        and d["original_veto_unchanged"]
    )
    assert (
        worker.later_diagnostic(
            {
                "last_sample": None,
                "last_process_observation": {"pressure_dispatch_flags": None},
            },
            time.monotonic() + 2,
        )
        is None
    )


def test_workflow_definition_preserves_budget_and_old_manifest():
    d = ctl.definition()
    assert (
        d["new_optimizer_allowance"] == 0
        and d["original_steps"] == 96
        and d["additional_maximum_started"] == 96
        and d["cumulative_maximum_started"] == 192
    )
    assert d["check_only_never_reserves_or_dispatches_real_work"]
    assert d["phase_limits_seconds"] == {
        "dev_reader": 60,
        "dev_readiness": 30,
        "dev": 300,
    }
    assert d["unchanged_projection_target_seconds"] == 180
    assert io.digest(io.read(io.ROOT / ctl.MANIFEST)) == io.digest(d)
    assert io.file_hash(io.ROOT / ctl.PROMPT) == ctl.PROMPT_HASH


def test_stdlib_parent_worker_import_and_source_acceptance_coverage():
    code = "from raregate.supervision import particle_readiness,particle_readiness_worker;from raregate.supervision import particle_launcher as i;i.assert_lightweight()"
    subprocess.run(
        [sys.executable, "-c", code], check=True, capture_output=True, timeout=10
    )
    for p in (
        "src/raregate/supervision/particle_readiness.py",
        "src/raregate/supervision/particle_readiness_worker.py",
        "tests/test_particle_readiness_workflow.py",
    ):
        assert p in io.source_hashes()


def test_check_worker_ready_never_constructs_store_model_optimizer(
    sandbox, monkeypatch
):
    from raregate.supervision import particle_worker as runtime_module
    from raregate.training import particle_monitor_v4 as monitor_module

    _, bind = sandbox
    uid = "d" * 32
    d = ctl.invocation_path(uid)
    d.mkdir(parents=True)
    res = {
        "invocation_id": uid,
        "action": "check_readiness",
        "binding": bind,
        "parent_pid": os.getppid(),
        "token": "fixture",
        "started_monotonic": time.monotonic(),
        "started_utc": io.now(),
    }
    io.exclusive(d / "reservation.json", res)
    io.exclusive(io.ROOT / ctl.previous.prior.MONITOR, {})

    def forbidden(*args, **kwargs):
        pytest.fail("check-only cannot construct/read/train data")

    old = SimpleNamespace(
        bg=SimpleNamespace(verify_acceptance=lambda *args: None, run_dev=forbidden),
        reader_measurement=forbidden,
        ParticleSetAutoencoder=forbidden,
    )
    monkeypatch.setattr(runtime_module, "runtime", lambda: (old, {}, {}, 0.0))
    monkeypatch.setattr(ctl, "current_acceptance", lambda: {})
    monkeypatch.setattr(monitor_module, "validate_manifest", lambda *args: None)

    class Monitor:
        _active = False

        def __init__(self, *args, **kwargs):
            pass

        def report(self):
            return {
                "sampler": {"latched_failure": None, "owned_thread_alive": False},
                "last_process_observation": {"pressure_dispatch_flags": None},
            }

    monkeypatch.setattr(monitor_module, "MonitorV4", Monitor)
    monkeypatch.setattr(
        worker, "readiness", lambda m: {"status": "passed", "readings": []}
    )
    assert worker.check_worker(uid, "fixture") == 0
    result = io.read(d / "receipt.json")
    assert (
        result["events"]
        == result["population_requests"]
        == result["new_steps_started"]
        == 0
    )
    assert (
        not result["real_slot_reserved_by_check"] and not (io.ROOT / ctl.SLOT).exists()
    )


def test_source_binding_mismatch_refuses_before_worker_dispatch(sandbox, monkeypatch):
    _, _ = sandbox
    monkeypatch.setattr(
        ctl, "identity", lambda: (_ for _ in ()).throw(ValueError("source mismatch"))
    )
    monkeypatch.setattr(
        io,
        "dispatch",
        lambda *args, **kwargs: pytest.fail("identity failure must not dispatch"),
    )
    r = ctl.invoke("check_readiness")
    assert r["status"] == "error" and "source mismatch" in r["error"]
    assert ctl.invocation_path(r["invocation_id"]).joinpath("receipt.json").exists()


def test_reserved_anchor_plan_failure_consumes_attempt_no_data(sandbox, monkeypatch):
    root, _ = sandbox
    monkeypatch.setattr(io, "dispatch", fake_dispatch(["ready", "ready"]))
    original = io.exclusive

    def exclusive(path, value):
        if path == root / ctl.PLAN:
            raise OSError("plan persistence interrupted")
        return original(path, value)

    monkeypatch.setattr(io, "exclusive", exclusive)
    monkeypatch.setattr(
        ctl, "dispatch_real", lambda *_: pytest.fail("partial plan cannot dispatch")
    )
    r = ctl.invoke("run_characterization")
    assert r["status"] == "error" and (root / ctl.SLOT).exists()
    assert not (root / ctl.OUTPUT).exists()
    assert ctl.invoke("run_characterization")["status"] == "error"


def test_diagnostic_query_failure_retains_unknown_without_veto_reversal(monkeypatch):
    class Query:
        def begin(self):
            raise OSError("unavailable snapshot")

        def close(self):
            pass

    monkeypatch.setattr(worker, "SystemQuery", Query)
    r = worker.later_diagnostic(
        {
            "last_sample": None,
            "last_process_observation": {"pressure_dispatch_flags": 2},
        },
        time.monotonic() + 2,
    )
    assert (
        r["status"] == "unavailable"
        and "available_gib" not in r
        and r["original_veto_unchanged"]
    )


def test_exact_workflow_manifest_and_full_acceptance_required(sandbox, monkeypatch):
    root, _ = sandbox
    # Identity validation uses synthetic files; no ignored operational receipt fixture.
    monkeypatch.setattr(ctl, "verify_history", lambda: None)
    monkeypatch.setattr(ctl, "identity", REAL_IDENTITY)
    monkeypatch.setattr(ctl.previous, "validate_authorization", lambda value: None)
    io.exclusive(root / ctl.previous.AUTHORIZATION, {})
    io.exclusive(root / ctl.PROMPT, {})
    monkeypatch.setattr(ctl, "PROMPT_HASH", io.file_hash(root / ctl.PROMPT))
    io.exclusive(root / ctl.MANIFEST, ctl.definition())
    monkeypatch.setattr(
        ctl,
        "current_acceptance",
        lambda: (_ for _ in ()).throw(ValueError("current acceptance missing")),
    )
    with pytest.raises(ValueError, match="current acceptance missing"):
        ctl.identity()
    bad = ctl.definition()
    bad["cumulative_maximum_started"] = 288
    io.atomic(root / ctl.MANIFEST, bad)
    with pytest.raises(ValueError, match="workflow"):
        ctl.identity()
