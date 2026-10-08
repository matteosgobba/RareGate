"""Self-contained process-policy, history, concurrency and scientific parity tests."""

import copy
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest
import torch

from latenttrigger.models.particle_memory_study import StudyAudit
from latenttrigger.models.particle_set import ParticleSetAutoencoder, event_loss
from latenttrigger.supervision import particle_dev_policy as policy
from latenttrigger.supervision import particle_launcher as io
from latenttrigger.supervision import particle_shared_host as ctl
from latenttrigger.supervision import particle_shared_host_worker as worker
from latenttrigger.training.autoencoder import deterministic_cpu
from latenttrigger.training.particle_monitor_v4 import optimizer_observer
from latenttrigger.training.particle_process_budget import ProcessBudgetGuard
from latenttrigger.training.particle_set import ResourceLimitError, adam


def process(**changes):
    return {
        "peak_rss_bytes": 385089536,
        "native_heap_reserved_bytes": 188399616,
        "native_heap_in_use_bytes": 140000000,
        "workspace_method": "all_malloc_zone_reserved_bytes_conservative_upper_bound",
        "pressure_dispatch_flags": 2,
        "pressure_errno": None,
        "pressure_method": "XNU_read_only_sysctl_dispatch_flags_1normal_2warning_4critical",
        **changes,
    }


class MissingContext:
    def __init__(self, **_):
        pass

    def begin(self):
        raise ResourceLimitError("Malformed/unavailable optional system context.")

    def close(self):
        pass


class SlowContext:
    def __init__(self, clock):
        self.clock = clock

    def begin(self):
        self.query_start = self.clock()
        self.r, self.w = os.pipe()
        return self.r

    def finish(self):
        if self.clock() - self.query_start < 0.16:
            return None
        return {
            "available_bytes": 0,
            "available_gib": 0.0,
            "backend": "system_vm_stat_oneshot_host_v4",
            "query_start": self.query_start,
            "query_end": self.clock(),
            "synthetic": True,
        }

    def close(self):
        os.close(self.r)
        os.close(self.w)


@pytest.fixture
def config():
    return io.read(io.ROOT / io.CONFIG)


def guard(config, probe=lambda: process(), query=MissingContext, **kwargs):
    return ProcessBudgetGuard(
        config,
        policy.definition(),
        process_probe=probe,
        query_factory=query,
        synthetic_fixture=True,
        notify_failure=False,
        **kwargs,
    )


@pytest.mark.parametrize("pressure", [None, 1, 2])
@pytest.mark.parametrize("available", [0, 1, 3 * 2**30, 4831838207])
def test_low_global_and_warning_are_advisory(config, pressure, available):
    m = guard(
        config,
        lambda: process(pressure_dispatch_flags=pressure, available_bytes=available),
    )
    m.check(launch=True)
    assert m.last["pressure_dispatch_flags"] == pressure and m.error is None
    assert m.report()["minimum_available_bytes"] is None


@pytest.mark.parametrize(
    "changes",
    [
        {"pressure_dispatch_flags": 4},
        {"peak_rss_bytes": 536870913},
        {"native_heap_reserved_bytes": 268435457},
        {"peak_rss_bytes": None},
        {"peak_rss_bytes": True},
        {"native_heap_in_use_bytes": None},
        {"native_heap_reserved_bytes": 0},
        {"workspace_method": "unsupported"},
        {"native_heap_in_use_bytes": 300000000},
        {"pressure_dispatch_flags": 3},
        {"pressure_method": "foreign"},
    ],
)
def test_primary_caps_critical_and_malformed_fail_latched(config, changes):
    value = process(**changes)
    m = guard(config, lambda: value)
    with pytest.raises(ResourceLimitError):
        m.check()
    first = m.error
    value.clear()
    value.update(process())
    with pytest.raises(ResourceLimitError, match=first):
        m.check()
    assert m.last_failure["error"] == first


def test_exact_caps_equality_and_failed_peaks_preserved(config):
    value = process(peak_rss_bytes=536870912, native_heap_reserved_bytes=268435456)
    m = guard(config, lambda: value.copy())
    m.check()
    value["peak_rss_bytes"] += 1
    with pytest.raises(ResourceLimitError):
        m.check()
    assert m.report()["peak_rss_bytes"] == 536870913
    assert m.report()["last_process_observation"]["peak_rss_bytes"] == 536870913


def test_no_host_age_veto_and_periodic_process_guards_during_slow_context(config):
    m = guard(config, query=SlowContext)
    with m:
        assert m.contexts[0]["age_upper_seconds"] > 0.1
        assert m.contexts[0]["available_bytes"] == 0
        assert m.periodic_checks >= 2
        before = m.process_checks
        m.check()
        m.check()
        assert m.process_checks >= before + 2
    assert not m.report()["owned_thread_alive"] and m.error is None


def test_optional_context_failure_never_hides_primary_failure(config):
    m = guard(config)
    with m:
        assert m.contexts[0]["status"] == "unavailable"
        m.process_probe = lambda: process(pressure_dispatch_flags=4)
        with pytest.raises(ResourceLimitError, match="CRITICAL"):
            m.context()


def test_periodic_critical_during_blocked_work_latched(config):
    value = process()
    m = guard(config, lambda: value.copy())
    with m:
        value["pressure_dispatch_flags"] = 4
        time.sleep(0.12)
        assert m.error == "Verified CRITICAL pressure veto."
        with pytest.raises(ResourceLimitError):
            m.check()
    assert not m.report()["owned_thread_alive"]


def test_deadline_interrupts_slow_optional_context_instead_of_suppressing(config):
    m = guard(config)
    with m:
        m.query_factory = SlowContext
        with pytest.raises(ResourceLimitError):
            with m.deadline("blocked_context", 0.04):
                m.context()
    assert m.error


def test_concurrent_fresh_process_checks_and_journal(config, tmp_path):
    m = guard(config, directory=tmp_path)
    with m:
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: m.check(), range(12)))
    assert m.process_checks >= 15
    assert (
        len((tmp_path / "guard-samples.jsonl").read_text().splitlines())
        == m.process_checks
    )


@pytest.mark.parametrize(
    "phase,store,pop,dev",
    [
        ("full_custody", policy.DEV, "train_background", True),
        ("fit", policy.DEV, "train_background", True),
        ("dev", "data/processed/lhco-rd-v1/schema-v1/full", "train_background", True),
        ("dev", policy.DEV, "validation_selection_background", True),
        ("dev", policy.DEV, "validation_calibration_background", True),
        ("dev", policy.DEV, "test_background", True),
        ("dev", policy.DEV, "test_signal", True),
        ("dev", policy.DEV, "train_background", False),
    ],
)
def test_scope_rejected_before_worker_plan_or_data(monkeypatch, phase, store, pop, dev):
    with pytest.raises(ValueError):
        policy.scope(phase, store, pop, dev)
    if phase not in ctl.PHASES:
        monkeypatch.setattr(
            ctl,
            "verify_plan",
            lambda: pytest.fail("No plan/data before scope rejection"),
        )
        with pytest.raises(ValueError):
            worker.verify_phase(phase, "token")


def test_manifest_exact_identity_and_no_arbitrary_override(config):
    definition = policy.definition()
    assert policy.validate(io.read(io.ROOT / policy.POLICY), config) == io.digest(
        definition
    )
    for key, value in [
        ("process_lifetime_peak_rss_ceiling_bytes", 2**30),
        ("global_minimum_at_launch_bytes", 0),
        ("name", "unsafe"),
    ]:
        changed = copy.deepcopy(definition)
        changed[key] = value
        with pytest.raises(ValueError):
            policy.validate(changed, config)
    assert definition["new_optimizer_allowance"] == 0
    assert (
        definition["original_started_steps"] + definition["additional_started_ceiling"]
        == 192
    )


def test_default_cli_and_controller_are_lightweight():
    code = "from latenttrigger.supervision import particle_readiness,particle_shared_host; from latenttrigger.supervision.particle_launcher import assert_lightweight; assert_lightweight()"
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, result.stderr
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "latenttrigger.supervision.particle_readiness",
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "Shared-Mac" in result.stdout


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(
        ctl,
        "identity",
        lambda: {
            "policy": policy.NAME,
            "source_sha256": {"fixture": "only"},
            "historical_torch_version": "same",
            "current_torch_version": "same",
        },
    )
    monkeypatch.setattr(io, "assert_lightweight", lambda: None)
    return tmp_path


def receipt(res, status="ready"):
    t = time.monotonic()
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
        "elapsed_seconds_including_imports_cleanup": t - res["started_monotonic"],
        "finished_monotonic": t,
        "resources": {
            "policy": policy.NAME,
            "synthetic_not_readiness": False,
            "latched_failure": None,
            "owned_thread_alive": False,
            "last_process_observation": {
                **process(),
                "backend": "cached_DarwinBindings_fresh_own_process",
                "synthetic_not_readiness": False,
                "process_query_start": t,
                "process_query_end": t,
            },
        },
    }


def dispatch_fixture(statuses):
    iterator = iter(statuses)
    lock = threading.Lock()

    def dispatch(cmd, *_args, **_kw):
        assert "--check" in cmd and "--phase" not in cmd
        uid = cmd[cmd.index("--check") + 1]
        directory = ctl.invocation_path(uid)
        with lock:
            status = next(iterator)
        io.exclusive(
            directory / "receipt.json",
            receipt(io.read(directory / "reservation.json"), status),
        )
        return {"returncode": 0 if status == "ready" else 2}

    return dispatch


def test_repeat_failed_then_ready_checks_no_slot_data_or_plan(sandbox, monkeypatch):
    monkeypatch.setattr(
        io, "dispatch", dispatch_fixture(["not_ready", "not_ready", "ready"])
    )
    monkeypatch.setattr(
        ctl, "reserve_real", lambda *_: pytest.fail("check never reserves")
    )
    records = [ctl.invoke("check_readiness") for _ in range(3)]
    assert [r["status"] for r in records] == ["not_ready", "not_ready", "ready"]
    assert len(list((sandbox / ctl.HISTORY_ROOT).glob("*/receipt.json"))) == 3
    assert not (sandbox / ctl.SLOT).exists()


def test_parallel_run_actions_one_shared_anchor_and_no_loser_data(sandbox, monkeypatch):
    barrier = threading.Barrier(2)
    calls = []
    real_check = ctl.check
    monkeypatch.setattr(io, "dispatch", dispatch_fixture(["ready", "ready"]))

    def check(action):
        r = real_check(action)
        barrier.wait(timeout=2)
        return r

    monkeypatch.setattr(ctl, "check", check)
    monkeypatch.setattr(
        ctl, "dispatch_real", lambda p: calls.append(p) or {"status": "synthetic_only"}
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: ctl.invoke("run_characterization"), range(2)))
    assert (
        len(calls) == 1
        and sum(r.get("real_slot_reserved", False) for r in results) == 1
    )
    slot = io.read(sandbox / ctl.SLOT)
    assert slot["task"] == "0016" and slot["maximum_additional_started_steps"] == 96
    assert slot["maximum_cumulative_started_steps"] == 192
    assert not ctl.permission()["available"]


@pytest.mark.parametrize("kind", ["partial", "foreign", "consumed"])
def test_existing_anchor_no_retry(sandbox, monkeypatch, kind):
    io.exclusive(sandbox / ctl.SLOT, {"status": kind})
    monkeypatch.setattr(io, "dispatch", dispatch_fixture(["ready"]))
    monkeypatch.setattr(
        ctl, "dispatch_real", lambda *_: pytest.fail("No data for existing anchor")
    )
    assert ctl.invoke("run_characterization")["status"] == "error"
    assert io.read(sandbox / ctl.SLOT) == {"status": kind}


def test_live_receipt_rejects_synthetic_fixture_and_stale_fields(sandbox, monkeypatch):
    monkeypatch.setattr(io, "dispatch", dispatch_fixture(["ready"]))
    r = ctl.check("run_characterization")
    d = ctl.invocation_path(r["invocation_id"])
    res = io.read(d / "reservation.json")
    for key, value in [
        ("synthetic_not_readiness", True),
        ("pressure_dispatch_flags", 4),
        ("peak_rss_bytes", 536870913),
    ]:
        bad = copy.deepcopy(r)
        bad["resources"]["last_process_observation"][key] = value
        with pytest.raises(ValueError):
            ctl.validate_check(bad, res)


def test_worker_rechecks_identity_parent_token_before_import(sandbox, monkeypatch):
    uid = "a" * 32
    directory = ctl.invocation_path(uid)
    directory.mkdir(parents=True)
    res = {
        "invocation_id": uid,
        "action": "check_readiness",
        "parent_pid": os.getppid(),
        "token": "owned",
        "binding": ctl.identity(),
    }
    io.exclusive(directory / "reservation.json", res)
    assert worker.verify_check(uid, "owned") == res
    with pytest.raises(ValueError):
        worker.verify_check(uid, "foreign")
    monkeypatch.setattr(ctl, "identity", lambda: {"changed": True})
    with pytest.raises(ValueError):
        worker.verify_check(uid, "owned")


def test_same_math_parameters_adam_outputs_scores_with_fresh_pre_step_guards(
    config, tmp_path
):
    out = []
    for monitored in (False, True):
        with deterministic_cpu(1729, 1):
            model = ParticleSetAutoencoder()
            opt = adam(model, config)
            audit = StudyAudit(tmp_path / f"{monitored}.json")
            m = guard(config)
            if monitored:
                optimizer_observer(audit, m)(opt)
            else:
                audit.observe_optimizer(opt)
            for n in (1, 384):
                x = torch.zeros(32, 384, 4)
                mask = torch.arange(384)[None, :].expand(32, -1) < n
                x[:, :, 0] = 0.25
                x[:, :, 1] = -0.5
                x[:, :, 3] = 1
                x[~mask] = 0
                opt.zero_grad(set_to_none=True)
                event_loss(x, model(x, mask), mask).mean().backward()
                opt.step()
            out.append(
                (
                    [p.detach().clone() for p in model.parameters()],
                    copy.deepcopy(opt.state_dict()),
                    model(x, mask).detach(),
                    model.score(x, mask),
                )
            )
            assert audit.steps_started == audit.steps_completed == 2
            if monitored:
                assert m.process_checks == 2
    for a, b in zip(out[0][0], out[1][0], strict=True):
        assert torch.equal(a, b)
    assert torch.equal(out[0][2], out[1][2]) and np.array_equal(out[0][3], out[1][3])
    for k, a in out[0][1]["state"].items():
        for name, v in a.items():
            assert torch.equal(v, out[1][1]["state"][k][name])


def test_pre_step_guard_failure_prevents_audit_reservation_and_mutation(
    config, tmp_path
):
    p = torch.nn.Parameter(torch.ones(1))
    opt = torch.optim.Adam([p], lr=0.001)
    audit = StudyAudit(tmp_path / "audit.json")
    m = guard(config, lambda: process(pressure_dispatch_flags=4))
    optimizer_observer(audit, m)(opt)
    p.grad = torch.ones(1)
    with pytest.raises(ResourceLimitError):
        opt.step()
    assert audit.steps_started == audit.steps_completed == 0
    assert torch.equal(p, torch.ones(1))


def test_current_complete_acceptance_rejects_stale_map(sandbox, monkeypatch):
    a = {
        "pytest_exit_code": 0,
        "pytest_passed": 7,
        "pytest_cases": 7,
        "source_sha256": {"new_guard": "actual"},
        "config_sha256": io.CONFIG_HASH,
        "workspace_measurement": {
            "parameter_count": 478,
            "synthetic_optimizer_steps": 2,
            "peak_tensor_bytes": 5228448,
        },
    }
    monkeypatch.setattr(io, "source_hashes", lambda: {"new_guard": "actual"})
    for suffix, key in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        p = (sandbox / ctl.ACCEPTANCE).with_suffix(suffix)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("synthetic evidence")
        a[key] = io.file_hash(p)
    io.exclusive(sandbox / ctl.ACCEPTANCE, a)
    assert ctl.current_acceptance() == a
    monkeypatch.setattr(io, "source_hashes", lambda: {"new_guard": "edited"})
    with pytest.raises(ValueError):
        ctl.current_acceptance()


def test_dispatch_timeout_keeps_partial_check_unreserved(sandbox, monkeypatch):
    def fail(cmd, *_a, **_kw):
        uid = cmd[cmd.index("--check") + 1]
        io.exclusive(
            ctl.invocation_path(uid) / "bootstrap-audit.json", {"no_data": True}
        )
        raise TimeoutError("owned worker deadline")

    monkeypatch.setattr(io, "dispatch", fail)
    r = ctl.invoke("run_characterization")
    assert r["status"] == "error" and r["partial_evidence_retained"]
    assert (ctl.invocation_path(r["invocation_id"]) / "receipt.json").exists()
    assert not (sandbox / ctl.SLOT).exists()


def test_all_old_routes_and_new_share_same_anchor_and_output():
    from latenttrigger.supervision import (
        particle_characterization,
        particle_readiness,
    )

    for route in (
        particle_characterization,
        particle_readiness,
    ):
        assert route.SLOT == ctl.SLOT and route.OUTPUT == ctl.OUTPUT


@pytest.mark.parametrize("uid", ["../escape", "A" * 32, "a" * 31, "a" * 33, ""])
def test_new_history_safe_ids(uid):
    with pytest.raises(ValueError):
        ctl.invocation_path(uid)


def test_unexpected_old_plan_without_anchor_blocks_run(sandbox):
    io.exclusive(sandbox / ctl.legacy.PLAN, {"unexpected": "preserve"})
    assert not ctl.permission()["available"]


def test_historical_source_exception_is_only_default_router(monkeypatch, tmp_path):
    # No operational receipts/Git needed: a synthetic original commit blob.
    original = b"original accepted router"
    import hashlib

    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(ctl.legacy, "verify_history", lambda: None)
    a = {
        "pytest_passed": 612,
        "source_sha256": {
            ctl.CHANGED_HISTORICAL_SOURCE: hashlib.sha256(original).hexdigest(),
            "immutable_science.py": hashlib.sha256(b"science").hexdigest(),
        },
    }
    accepted = tmp_path / ctl.legacy.ACCEPTANCE
    accepted.parent.mkdir(parents=True)
    for suffix, key in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        p = accepted.with_suffix(suffix)
        p.write_text("history")
        a[key] = io.file_hash(p)
    io.exclusive(accepted, a)
    monkeypatch.setattr(ctl, "OLD_ACCEPTANCE_HASH", io.file_hash(accepted))
    monkeypatch.setattr(ctl.subprocess, "check_output", lambda *a, **k: original)
    (tmp_path / "immutable_science.py").write_bytes(b"science")
    (tmp_path / ctl.legacy.HISTORY_ROOT).mkdir(parents=True)
    ctl.verify_history()
    (tmp_path / "immutable_science.py").write_bytes(b"changed")
    with pytest.raises(ValueError, match="source entry changed"):
        ctl.verify_history()
