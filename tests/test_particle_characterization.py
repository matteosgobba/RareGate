"""Task0016 self-contained authorization/routing; never operational data fixtures."""

import copy
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

from raregate.supervision import particle_characterization as c
from raregate.supervision import particle_characterization_worker as worker
from raregate.supervision import particle_launcher as io
from raregate.training.particle_set import ResourceLimitError


@pytest.mark.parametrize(
    "field,value",
    [
        ("maximum_cumulative_steps_started", 288),
        ("maximum_additional_steps_started", 192),
        ("original_real_cycle_target_seconds", 200),
        ("original_steps_started_completed", 0),
        ("Task0015_historical_material_pass", True),
        ("canonical_fit_selection_calibration_freeze_authorized", True),
        ("authorization_version", True),
        ("adopted_observation_manifest_sha256", "foreign"),
        ("prospective_synthetic_admission", "median_gain_ge2"),
    ],
)
def test_exact_revised_authorization_no_scope_type_or_limit_override(field, value):
    d = c.definition()
    d[field] = value
    with pytest.raises(ValueError):
        c.validate_authorization(d)


def test_adopts_unchanged_v4_keeps_failed_material_and_real_target():
    assert c.validate_authorization(io.read(io.ROOT / c.AUTHORIZATION)) == io.digest(
        c.definition()
    )
    d = c.definition()
    assert d["Task0015_historical_material_pass"] is False
    assert d["Task0015_paired_median_gain"] == 2.1402944935480797
    assert d["original_real_cycle_target_seconds"] == 180
    assert d["observation_seconds"] == {
        "cadence": 0.05,
        "age_upper": 0.1,
        "probe_timeout": 2,
    }
    assert (
        d["maximum_additional_steps_started"] == 96
        and d["maximum_cumulative_steps_started"] == 192
    )
    assert (
        c.project(
            [0.5065042919995904, 0.4505980419999105, 0.45002770899918687],
            0.3897375420001481,
        )
        == 749.3431957854029
    )
    assert not d["full_custody_replay_authorized"]


@pytest.mark.parametrize(
    "train,score",
    [
        ([], 1),
        ([1, 2], 1),
        ([True, 1, 1], 1),
        ([float("nan"), 1, 1], 1),
        ([1, 1, 1], -1),
    ],
)
def test_projection_refuses_partial_nonfinite_or_reweighted_input(train, score):
    with pytest.raises(ValueError):
        c.project(train, score)


def gate_audit():
    gate = {
        "passes": 3,
        "optimizer_steps": 96,
        "unique_events": 1024,
        "train_pass_seconds": [0.5, 0.4, 0.3],
        "score_pass_seconds": 0.2,
        "last_online_objective": 0.1,
        "same_sample_score_mean": 0.2,
        "same_sample_score_sha256": "a" * 64,
    }
    p = c.project(gate["train_pass_seconds"], gate["score_pass_seconds"])
    gate.update(extrapolated_full_cycle_seconds=p, feasibility_pass=p <= 180)
    audit = {
        "optimizer_steps_started": 96,
        "optimizer_steps_completed": 96,
        "possible_inflight_optimizer_step": False,
        "unique_dev_sample_events": 1024,
        "population_access": [
            {
                "status": "completed",
                "events_read": 1024,
                "split": "train_background",
                "allow_test": False,
                "include_labels": False,
                "dev_only": True,
            }
            for _ in range(4)
        ],
    }
    return gate, audit


@pytest.mark.parametrize(
    "change", ["inflight", "partial", "foreign", "favorable_projection", "float_steps"]
)
def test_complete_gate_never_hides_partial_or_foreign_work(change):
    g, a = gate_audit()
    if change == "inflight":
        a["optimizer_steps_completed"] = 95
    if change == "partial":
        a["population_access"].pop()
    if change == "foreign":
        a["population_access"][0]["split"] = "test_background"
    if change == "favorable_projection":
        g["extrapolated_full_cycle_seconds"] = 179
    if change == "float_steps":
        a["optimizer_steps_started"] = 96.0
    with pytest.raises(ValueError):
        c.complete_gate(g, a)


def test_only_exact_throughput_failure_is_completed_characterization(
    tmp_path, monkeypatch
):
    g, a = gate_audit()
    io.atomic(tmp_path / "dev-gate.json", g)
    audit = SimpleNamespace(
        path=tmp_path / "audit.json", save=lambda: io.atomic(tmp_path / "audit.json", a)
    )
    old = SimpleNamespace(
        ResourceLimitError=ResourceLimitError,
        bg=SimpleNamespace(
            run_dev=lambda *args, **kw: (_ for _ in ()).throw(
                ResourceLimitError(c.THROUGHPUT_ERROR)
            )
        ),
    )
    checks = []
    monitor = SimpleNamespace(check=lambda: checks.append(True))
    monkeypatch.setattr(
        c,
        "numeric_comparison",
        lambda *args: {"status": "exact_match", "canonical_proposal_blocked": False},
    )
    result = worker.run_characterization(old, {}, tmp_path, monitor, audit, {}, None)
    assert result["status"] == "characterization_completed_original_throughput_failed"
    assert (
        result["original_throughput_error"] == c.THROUGHPUT_ERROR
        and not result["original_throughput_pass"]
    )
    assert checks == [True] and io.read(tmp_path / "dev-gate.json") == g
    old.bg.run_dev = lambda *args, **kw: (_ for _ in ()).throw(
        ResourceLimitError("Host observation age exceeds100ms.")
    )
    with pytest.raises(ResourceLimitError, match="age"):
        worker.run_characterization(old, {}, tmp_path, monitor, audit, {}, None)
    old.bg.run_dev = lambda *args, **kw: (_ for _ in ()).throw(
        ResourceLimitError(c.THROUGHPUT_ERROR)
    )
    monitor.check = lambda: (_ for _ in ()).throw(
        ResourceLimitError("latched native failure")
    )
    with pytest.raises(ResourceLimitError, match="latched"):
        worker.run_characterization(old, {}, tmp_path, monitor, audit, {}, None)


def test_numeric_binding_mismatch_blocks_no_rerun(tmp_path, monkeypatch):
    g, a = gate_audit()
    monkeypatch.setattr(io, "ROOT", tmp_path)
    p = tmp_path / "data/baselines/task0013-particle-host-study/dev/dev-gate.json"
    io.exclusive(p, g)
    versions = {"historical_torch_version": "same", "current_torch_version": "same"}
    assert c.numeric_comparison(g, versions)["status"] == "exact_match"
    bad = copy.deepcopy(g)
    bad["same_sample_score_sha256"] = "b" * 64
    assert c.numeric_comparison(bad, versions)["canonical_proposal_blocked"]
    versions["current_torch_version"] = "different"
    assert (
        c.numeric_comparison(g, versions)["status"]
        == "runtime_binding_different_comparison_unresolved"
    )


@pytest.mark.parametrize(
    "path",
    [
        c.prior.PLAN,
        c.prior.SLOT,
        c.prior.OUTPUT,
        c.prior.READINESS_AUTO,
        c.prior.READINESS_MANUAL,
    ],
)
def test_prior_task15_execution_blocks_additional_spending(path, tmp_path, monkeypatch):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    io.exclusive(tmp_path / path, {"unexpected": True})
    with pytest.raises(ValueError):
        c.refuse_Task0015_consumption()
    assert not (tmp_path / c.SLOT).exists()


def live_receipt_fixture(tmp_path):
    # Pure parser fixture; cannot dispatch a real worker or authorize operational data.
    io.exclusive(tmp_path / c.PLAN, {})
    io.exclusive(tmp_path / c.ACCEPTANCE, {})
    guard = {
        "synthetic_not_readiness": False,
        "host_backend": "system_vm_stat_oneshot_host_v4",
        "host_validation_status": "valid_primary_fields",
        "host_age_upper_seconds": 0.1,
        "pressure_dispatch_flags": None,
        "available_bytes": 4831838208,
        "native_heap_reserved_bytes": 536870912,
        "peak_rss_bytes": 6442450944,
    }
    return {
        "status": "passed",
        "new_steps_started": 0,
        "plan_sha256": io.file_hash(tmp_path / c.PLAN),
        "current_acceptance_sha256": io.file_hash(tmp_path / c.ACCEPTANCE),
        "readings": [
            {"sample_monotonic": t, "guard": copy.deepcopy(guard)}
            for t in (1.0, 3.5, 6.0)
        ],
        "elapsed_seconds_including_imports": 6.0,
        "resources": {
            "sampler": {"latched_failure": None, "owned_thread_alive": False}
        },
    }


@pytest.mark.parametrize(
    "bad",
    [
        "synthetic",
        "stale",
        "pressure",
        "low",
        "partial",
        "foreign",
        "inflight",
        "cleanup",
    ],
)
def test_receipt_refuses_fixture_staleness_unknown_or_foreign_provenance(
    bad, tmp_path, monkeypatch
):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    r = live_receipt_fixture(tmp_path)
    if bad == "synthetic":
        r["readings"][0]["guard"]["synthetic_not_readiness"] = True
    if bad == "stale":
        r["readings"][0]["guard"]["host_age_upper_seconds"] = 0.101
    if bad == "pressure":
        r["readings"][0]["guard"]["pressure_dispatch_flags"] = 2
    if bad == "low":
        r["readings"][0]["guard"]["available_bytes"] = 4831838207
    if bad == "partial":
        r["readings"].pop()
    if bad == "foreign":
        r["plan_sha256"] = "foreign"
    if bad == "inflight":
        r["new_steps_started"] = 1
    if bad == "cleanup":
        r["resources"]["sampler"]["owned_thread_alive"] = True
    with pytest.raises(ValueError):
        c.verify_readiness_receipt(r)


def test_single_atomic_shared_automatic_manual_additional_slot(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(c, "verify_plan", lambda: {})
    r = live_receipt_fixture(tmp_path)
    io.exclusive(tmp_path / c.READINESS["automatic"], r)
    io.exclusive(tmp_path / c.READINESS["manual"], r)
    c.reserve_additional("automatic")
    with pytest.raises(FileExistsError):
        c.reserve_additional("manual")
    slot = io.read(tmp_path / c.SLOT)
    assert slot["maximum_cumulative_started_steps"] == 192 and slot["task"] == "0016"


def test_failed_readiness_reserves_no_real_slot_and_duplicate_refuses(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(io, "assert_lightweight", lambda: None)
    monkeypatch.setattr(c, "prepare", lambda: {})
    monkeypatch.setattr(
        c, "dispatch_readiness", lambda mode: (False, {"status": "failed"})
    )
    result = c.study("automatic")
    assert result["cumulative_started"] == 96 and not (tmp_path / c.SLOT).exists()
    io.exclusive(tmp_path / c.SLOT, {"reserved": True})
    with pytest.raises(FileExistsError):
        c.study("manual")


def test_readiness_timeout_preserves_failure_and_blocks_repeated_dispatch(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(c, "verify_plan", lambda: {})
    io.exclusive(tmp_path / c.PLAN, {})
    monkeypatch.setattr(
        io,
        "dispatch",
        lambda *args, **kw: (_ for _ in ()).throw(TimeoutError("owned timeout")),
    )
    ok, r = c.dispatch_readiness("automatic")
    assert not ok and r["new_steps_started"] == 0 and not (tmp_path / c.SLOT).exists()
    with pytest.raises(FileExistsError):
        c.dispatch_readiness("automatic")


def test_worker_token_parent_phase_and_source_recheck(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(c, "verify_plan", lambda: {"checked": True})
    io.exclusive(tmp_path / c.PLAN, {})
    path = (tmp_path / c.READINESS["automatic"]).with_suffix(".reservation.json")
    row = {
        "mode": "automatic",
        "status": "read_only_once_no_retry",
        "token": "test",
        "parent_pid": os.getppid(),
        "plan_sha256": io.file_hash(tmp_path / c.PLAN),
    }
    io.exclusive(path, row)
    assert worker.verify_worker("automatic", "test")[1]["checked"]
    with pytest.raises(ValueError):
        worker.verify_worker("automatic", "foreign")
    row["parent_pid"] = -1
    io.atomic(path, row)
    with pytest.raises(ValueError):
        worker.verify_worker("automatic", "test")
    for kind in ("fit", "calibration", "test_signal", "full_custody"):
        with pytest.raises(ValueError):
            worker.verify_worker(kind, "test")
    monkeypatch.setattr(
        c, "verify_plan", lambda: (_ for _ in ()).throw(ValueError("stale source"))
    )
    with pytest.raises(ValueError, match="stale"):
        worker.verify_worker("automatic", "test")


def test_current_full_source_acceptance_not_historical_subset(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(io, "source_hashes", lambda: {"new.py": "new"})
    p = tmp_path / c.ACCEPTANCE
    p.parent.mkdir(parents=True)
    p.with_suffix(".pytest.xml").write_text("synthetic XML fixture")
    p.with_suffix(".pytest.log").write_text("synthetic log fixture")
    a = {
        "pytest_exit_code": 0,
        "pytest_passed": 1,
        "pytest_cases": 1,
        "source_sha256": {"new.py": "new"},
        "config_sha256": io.CONFIG_HASH,
        "workspace_measurement": {
            "parameter_count": 478,
            "synthetic_optimizer_steps": 2,
            "peak_tensor_bytes": 5228448,
        },
        "pytest_xml_sha256": io.file_hash(p.with_suffix(".pytest.xml")),
        "pytest_log_sha256": io.file_hash(p.with_suffix(".pytest.log")),
    }
    io.atomic(p, a)
    assert c.current_acceptance() == a
    a["source_sha256"] = {}
    io.atomic(p, a)
    with pytest.raises(ValueError):
        c.current_acceptance()


def test_parent_stays_stdlib_and_old_task15_route_stays_blocked():
    code = "from raregate.supervision import particle_characterization,particle_characterization_worker;from raregate.supervision import particle_launcher as i;i.assert_lightweight()"
    subprocess.run(
        [sys.executable, "-c", code], check=True, capture_output=True, timeout=10
    )
    for p in (
        "src/raregate/supervision/particle_characterization.py",
        "src/raregate/supervision/particle_characterization_worker.py",
        "tests/test_particle_characterization.py",
    ):
        assert p in io.source_hashes()
    # No old route invocation: its historical map cannot authorize added current files.
    assert len(io.source_hashes()) > 63


def test_interrupted_dev_preserves_partial_steps_and_consumes_single_slot(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(io, "assert_lightweight", lambda: None)
    monkeypatch.setattr(c, "prepare", lambda: {})
    monkeypatch.setattr(c, "verify_plan", lambda: {})
    io.exclusive(tmp_path / c.PLAN, {})
    io.exclusive(tmp_path / c.ACCEPTANCE, {})
    monkeypatch.setattr(c, "dispatch_readiness", lambda mode: (True, {}))
    monkeypatch.setattr(
        c,
        "reserve_additional",
        lambda mode: io.exclusive(tmp_path / c.SLOT, {"reserved": True}),
    )

    def dispatch(command, *args, **kwargs):
        phase = command[command.index("--phase") + 1]
        directory = tmp_path / c.OUTPUT / phase
        directory.mkdir()
        if phase == "dev":
            io.atomic(
                directory / "access-audit.json",
                {"optimizer_steps_started": 7, "optimizer_steps_completed": 6},
            )
            raise TimeoutError("owned parent stopped inflight dev")
        io.atomic(
            directory / "stage-result.json",
            {
                "phase": phase,
                "status": "passed",
                "plan_sha256": io.file_hash(tmp_path / c.PLAN),
                "current_acceptance_sha256": io.file_hash(tmp_path / c.ACCEPTANCE),
            },
        )
        return {"returncode": 0}

    monkeypatch.setattr(io, "dispatch", dispatch)
    result = c.study("automatic")
    assert result["status"] == "bounded_v4_characterization_attempt_failed"
    assert result["new_steps_started"] == 7 and result["new_steps_completed"] == 6
    assert (
        result["new_inflight_steps"] == 1 and result["cumulative_started_steps"] == 103
    )
    assert io.read(tmp_path / c.OUTPUT / "workflow.json") == result
    with pytest.raises(FileExistsError):
        c.study("manual")


def test_added_source_blocks_superseded_task15_route_before_reservation(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(io, "assert_lightweight", lambda: None)
    monkeypatch.setattr(
        io, "source_hashes", lambda: {"old.py": "same", "Task0016.py": "new"}
    )
    io.exclusive(tmp_path / c.SLOT, {"task": "0016", "reserved": True})
    old = {
        "pytest_exit_code": 0,
        "pytest_passed": 532,
        "pytest_cases": 532,
        "config_sha256": io.CONFIG_HASH,
        "source_sha256": {"old.py": "same"},
        "workspace_measurement": {
            "parameter_count": 478,
            "synthetic_optimizer_steps": 2,
            "peak_tensor_bytes": 5228448,
        },
    }
    io.exclusive(tmp_path / c.prior.bench.ACCEPTANCE, old)
    with pytest.raises(ValueError, match="source-bound"):
        c.prior.study("automatic")
    assert not (tmp_path / c.prior.SLOT).exists()


def test_fresh_readiness_pressure_bool_is_not_a_numeric_pressure_flag(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(io, "ROOT", tmp_path)
    r = live_receipt_fixture(tmp_path)
    assert c.verify_readiness_receipt(r)
    r["readings"][0]["guard"]["pressure_dispatch_flags"] = True
    with pytest.raises(ValueError):
        c.verify_readiness_receipt(r)
