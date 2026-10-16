"""Dataset-independent engineering admission, custody, lineage and budget gates."""

import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from raregate.data.processed import content_hash
from raregate.models import particle_memory_study as study
from raregate.models import particle_recovery as previous
from raregate.training import particle_resources as resources
from raregate.training.particle_set import ResourceLimitError, parse_vm_stat


@pytest.fixture
def config():
    return json.loads((study.ROOT / previous.CONFIG).read_text())


@pytest.fixture
def profile(config):
    value = json.loads((study.ROOT / study.PROFILE).read_text())
    resources.validate_policy(value, config)
    return value


def sample(available=9 * 2**29, pressure=None):
    return {
        **parse_vm_stat(
            f"page size of 16384 bytes\nPages free: {available // 16384}.\nPages inactive: 0.\n"
        ),
        "peak_rss_bytes": 400 * 2**20,
        "native_heap_reserved_bytes": 184 * 2**20,
        "native_heap_in_use_bytes": 138 * 2**20,
        "available_method": "Darwin_free_plus_inactive_pages",
        "workspace_method": "all_malloc_zone_reserved_bytes_conservative_upper_bound",
        "pressure_dispatch_flags": pressure,
        "current_rss_bytes": 390 * 2**20,
    }


def test_exact_separate_policy_and_no_original_mutation(config, profile):
    original = copy.deepcopy(config)
    detached = resources.policy_definition(config)
    detached["dev_contract"]["events"] = 1
    assert config == original
    resources.validate_policy(profile, config, content_hash(profile))
    assert profile["limits"]["minimum_system_available_bytes_at_launch"] == 4831838208
    assert (
        profile["headroom_bytes"]
        == profile["limits"]["minimum_system_available_bytes_at_launch"] - 4 * 2**30
    )
    for key, value in profile["limits"].items():
        if key != "minimum_system_available_bytes_at_launch":
            assert value == config["resource_gate"][key]
    assert profile["remaining_timing_limits"]["max_two_run_total_wall_seconds"] == 79200
    assert profile["dev_contract"]["max_optimizer_steps"] == 96
    resources.validate_sample(sample(), config, profile, launch=True)
    with pytest.raises(ResourceLimitError, match="8 GiB"):
        previous.check_reading(sample(), config["resource_gate"])
    assert config == original and profile["policy_v1_compliance_claim"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("engineering_policy_version", 1),
        ("engineering_policy_version", True),
        ("schema_version", 2),
        ("policy_type", "generic_override"),
        ("canonical_training_authorized", True),
        ("metric", "active_plus_compressed"),
        ("scope", "full_fit"),
        ("headroom_bytes", 1),
        ("status", "finalized"),
    ],
)
def test_unsupported_type_version_scope_or_override(config, profile, field, value):
    profile[field] = value
    with pytest.raises(ValueError):
        resources.validate_policy(profile, config)


@pytest.mark.parametrize(
    "field,value",
    [
        ("minimum_system_available_bytes_at_launch", 4 * 2**30),
        ("minimum_system_available_bytes_at_launch", 5 * 2**30),
        ("stop_if_system_available_below_bytes", 3 * 2**30),
        ("process_peak_rss_ceiling_bytes", 7 * 2**30),
        ("working_tensor_and_workspace_ceiling_bytes", 1024 * 2**20),
    ],
)
def test_only_exact_authorized_launch_diff_allowed(config, profile, field, value):
    profile["limits"][field] = value
    with pytest.raises(ValueError):
        resources.validate_policy(profile, config)


def test_policy_hash_and_model_hash_are_distinct_required(config, profile):
    with pytest.raises(ValueError, match="identity"):
        resources.validate_policy(profile, config, "bad")
    config["training"]["batch_size"] = 16
    with pytest.raises(ValueError):
        resources.validate_policy(profile, config)


@pytest.mark.parametrize("pressure", [None, 1])
def test_equality_unknown_optional_and_normal(config, profile, pressure):
    s = sample(pressure=pressure)
    s["peak_rss_bytes"] = 6 * 2**30
    s["native_heap_reserved_bytes"] = 512 * 2**20
    resources.validate_sample(s, config, profile, launch=True)
    resources.validate_sample(
        sample(4 * 2**30, pressure), config, profile, launch=False
    )


@pytest.mark.parametrize("pressure", [2, 4, 6])
def test_verified_pressure_warning_critical_veto(config, profile, pressure):
    with pytest.raises(ResourceLimitError, match="veto"):
        resources.validate_sample(
            sample(pressure=pressure), config, profile, launch=True
        )


@pytest.mark.parametrize(
    "key,value",
    [
        ("available_bytes", 1),
        ("available_gib", 0),
        ("page_size_bytes", 0),
        ("native_heap_reserved_bytes", 0),
        ("peak_rss_bytes", None),
        ("pressure_dispatch_flags", "normal"),
        ("pressure_dispatch_flags", True),
    ],
)
def test_unknown_primary_and_malformed_optional_fail_closed(
    config, profile, key, value
):
    s = sample()
    s[key] = value
    with pytest.raises(ResourceLimitError):
        resources.validate_sample(s, config, profile, launch=True)


def preflight(config, profile, values):
    clock = [0.0]
    iterator = iter(values)

    def probe():
        value = next(iterator)
        if isinstance(value, Exception):
            raise value
        return value

    def sleep(seconds):
        clock[0] += seconds

    return study.stable_preflight(
        config,
        profile,
        probe=probe,
        clock=lambda: clock[0],
        sleep=sleep,
        context=lambda: {},
    )


def test_stable_preflight_only_three_samples_no_reader_optimizer(
    config, profile, monkeypatch
):
    monkeypatch.setattr(
        study, "ProcessedStore", lambda *a: pytest.fail("reader forbidden")
    )
    result = preflight(config, profile, [sample()] * 3)
    assert result["status"] == "passed" and result["sample_span_seconds"] == 5
    assert result["population_requests"] == result["real_optimizer_steps"] == 0
    assert result["policy_v1_compliance"] is False


def test_fluctuation_retains_all_samples(config, profile):
    result = preflight(config, profile, [sample(), sample(4 * 2**30), sample()])
    assert result["status"] == "failed" and len(result["readings"]) == 3


def test_readiness_deadline_preserves_prior_readings(config, profile):
    result = preflight(config, profile, [sample(), study.PreflightDeadline("timeout")])
    assert result["status"] == "failed" and len(result["readings"]) == 2


def test_monitor_compact_journal_overhead_and_including_probe_deadline(
    config, profile, tmp_path
):
    tick = [0.0]

    def probe():
        tick[0] += 0.1
        return sample()

    journal = tmp_path / "samples.jsonl"
    monitor = resources.PolicyMonitor(
        config,
        profile,
        probe=probe,
        clock=lambda: tick[0],
        journal=journal,
        monitor_background=False,
    )
    monitor.check(launch=True)
    monitor.phase = "verification"
    monitor.check()
    result = monitor.report()
    assert result["probe_total_seconds"] == pytest.approx(0.2)
    assert result["probe_max_seconds"] == pytest.approx(0.1)
    assert result["samples"] == 2 and len(journal.read_text().splitlines()) == 2
    assert (
        "vm_stat_raw" not in journal.read_text()
        and "vm_stat_raw" not in result["last_sample"]
    )
    assert (
        result["phases"]["startup"]["samples"] == 1
        and result["policy_v1_compliance"] is False
    )
    with pytest.raises(ResourceLimitError, match="Time ceiling"):
        with monitor.deadline("probe_cost_counted", 0.05):
            monitor.check()


def test_signal_deadline_still_interrupts_blocked_work(config, profile):
    import time

    monitor = resources.PolicyMonitor(config, profile, probe=lambda: sample())
    with monitor, pytest.raises(ResourceLimitError):
        with monitor.deadline("bounded_synthetic", 0.02):
            time.sleep(0.3)


@pytest.mark.parametrize(
    "phase",
    ["fit", "first_fit", "repeat_fit", "freeze", "calibration", "postfreeze", "test"],
)
def test_full_training_calibration_and_foreign_phase_refused(phase):
    with pytest.raises(ValueError):
        study.authorize_phase(phase, {"stages": []})


def test_phase_order_and_activation_required():
    with pytest.raises(ValueError):
        study.authorize_phase("full_custody", {"stages": []})
    state = {"stages": [{"phase": p, "status": "passed"} for p in study.PHASES[:3]]}
    with pytest.raises(ValueError):
        study.authorize_phase("dev_preflight", state)
    state["activation"] = {"activated_for_bounded_dev": True}
    study.authorize_phase("dev_preflight", state)
    state["stages"][0]["status"] = "failed"
    with pytest.raises(ValueError):
        study.authorize_phase("dev_preflight", state)


@pytest.mark.parametrize(
    "role",
    [
        "test_background",
        "test_signal",
        "validation_selection_background",
        "validation_calibration_background",
    ],
)
def test_audit_role_rejection_before_population_reads(tmp_path, role):
    audit = study.StudyAudit(tmp_path / "audit.json")
    with pytest.raises(ValueError):
        audit.request(role, "bad", True, 64)
    assert audit.records == []


def test_foreign_membership_and_seen_bitset_accounting(tmp_path):
    audit = study.StudyAudit(tmp_path / "audit.json")
    ids = np.arange(1024, dtype=np.int64) * 2
    audit.bind_sample(ids)
    request = audit.request("train_background", "reader", True, 64)
    audit.advance(request, 32)
    audit.observe_ids(ids[:32])
    audit.advance(request, 32)
    audit.observe_ids(ids[:32])
    result = json.loads(audit.path.read_text())
    assert (
        result["population_access"][0]["events_read"] == 64
        and result["unique_dev_sample_events"] == 32
    )
    assert (
        np.unpackbits(
            np.frombuffer(
                bytes.fromhex(result["sample_relative_seen_bitset_hex"]), dtype=np.uint8
            )
        ).sum()
        == 32
    )
    with pytest.raises(ValueError):
        audit.observe_ids(np.array([1]))
    with pytest.raises(ValueError):
        audit.bind_sample(ids[::-1])


def test_cumulative_96_step_reservation_and_partial_state(tmp_path):
    audit = study.StudyAudit(tmp_path / "audit.json")

    class Optimizer:
        def register_step_pre_hook(self, hook):
            self.before = hook

        def register_step_post_hook(self, hook):
            self.after = hook

    optimizer = Optimizer()
    audit.observe_optimizer(optimizer)
    optimizer.before()
    r = json.loads(audit.path.read_text())
    assert (
        r["optimizer_steps_started"] == 1
        and r["optimizer_steps_completed"] == 0
        and r["possible_inflight_optimizer_step"]
    )
    with pytest.raises(ValueError):
        optimizer.before()
    optimizer.after()
    for _ in range(95):
        optimizer.before()
        optimizer.after()
    with pytest.raises(ValueError):
        optimizer.before()
    assert audit.steps_completed == audit.steps_started == 96


def test_optimizer_observation_preserves_numeric_update(tmp_path):
    a = torch.nn.Parameter(torch.tensor([1.0], dtype=torch.float32))
    b = torch.nn.Parameter(a.detach().clone())
    x = torch.optim.Adam([a], lr=0.001, foreach=False)
    y = torch.optim.Adam([b], lr=0.001, foreach=False)
    audit = study.StudyAudit(tmp_path / "audit.json")
    audit.observe_optimizer(x)
    for _ in range(3):
        a.grad = torch.ones_like(a)
        b.grad = torch.ones_like(b)
        x.step()
        y.step()
    assert torch.equal(a, b) and audit.steps_completed == 3


class FakeStore:
    def __init__(self, path):
        self.scope = path.name
        self.manifest = {}
        self._arrays = {"tiny": np.zeros(16, dtype=np.float32)}
        self.closed = False
        self.requests = []

    def event_ids(self, role, **kwargs):
        assert (
            self.scope == "dev"
            and role == "train_background"
            and kwargs == {"allow_test": False, "dev_only": True}
        )
        return np.arange(6999, dtype=np.int64)

    def read_ids(self, role, ids, **kwargs):
        assert (
            role == "train_background"
            and len(ids) == 32
            and kwargs
            == {"allow_test": False, "include_labels": False, "dev_only": True}
        )
        self.requests.append(ids.copy())
        return SimpleNamespace(
            event_ids=ids,
            labels=None,
            model_view=lambda nmax: SimpleNamespace(
                features=np.zeros((32, nmax, 4), dtype=np.float32)
            ),
        )

    def close(self):
        self.closed = True
        self._arrays.clear()


@pytest.mark.parametrize("phase", ["dev_reader", "full_custody"])
def test_exact_reader_or_no_population_custody_paths(
    config, profile, tmp_path, monkeypatch, phase
):
    stores = []

    def factory(path):
        store = FakeStore(path)
        stores.append(store)
        return store

    monkeypatch.setattr(study, "ProcessedStore", factory)
    monkeypatch.setattr(study, "validate_store", lambda *a, **k: None)
    audit = study.StudyAudit(tmp_path / "audit.json")
    audit.save()
    mon = resources.PolicyMonitor(
        config, profile, probe=lambda: sample(), monitor_background=False
    )
    result = study.reader_measurement(phase, config, mon, audit)
    assert result["custody_completed"] and stores[0].closed and audit.steps_started == 0
    if phase == "dev_reader":
        assert audit.records[0]["events_read"] == 64 and audit.seen.sum() == 64
        assert np.array_equal(np.concatenate(stores[0].requests), np.arange(64))
    else:
        assert audit.records == [] and stores[0].requests == []


def test_constructor_floor_failure_preserves_zero_request_audit(
    config, profile, tmp_path, monkeypatch
):
    def fail(*a):
        raise ResourceLimitError("continuing floor")

    monkeypatch.setattr(study, "ProcessedStore", fail)
    audit = study.StudyAudit(tmp_path / "audit.json")
    audit.save()
    mon = resources.PolicyMonitor(
        config, profile, probe=lambda: sample(), monitor_background=False
    )
    with pytest.raises(ResourceLimitError):
        study.reader_measurement("dev_reader", config, mon, audit)
    record = json.loads(audit.path.read_text())
    assert (
        record["population_access"] == []
        and record["custody_access"][0]["status"] == "failed_or_interrupted"
    )


def reader_results(config, profile):
    record = {
        "status": "passed",
        "custody_completed": True,
        "optimizer_steps_started": 0,
        "optimizer_steps_completed": 0,
        "engineering_policy_sha256": content_hash(profile),
        "model_config_sha256": content_hash(config),
        "resources": {
            "minimum_available_bytes": 4 * 2**30,
            "native_heap_reserved_bytes": 250 * 2**20,
            "peak_rss_bytes": 400 * 2**20,
            "phases": {
                "startup": {"first": {"native_heap_reserved_bytes": 184 * 2**20}}
            },
        },
    }
    a = copy.deepcopy(record)
    a["view_events"] = 64
    b = copy.deepcopy(record)
    b["view_events"] = 0
    return {"dev_reader": a, "full_custody": b}


def test_activation_completed_reader_bound_margin_only_before_dev(config, profile):
    records = reader_results(config, profile)
    acceptance = {"workspace_measurement": {"peak_tensor_bytes": 5228448}}
    result = resources.activation_decision(records, acceptance, profile)
    assert result["activated_for_bounded_dev"] and not result["canonical_authorized"]
    assert result["bound_plus_margin_bytes"] == 66 * 2**20 + 4 * 5228448 + 128 * 2**20
    records["full_custody"]["resources"]["native_heap_reserved_bytes"] = 512 * 2**20
    records["full_custody"]["resources"]["phases"]["startup"]["first"][
        "native_heap_reserved_bytes"
    ] = 64 * 2**20
    result = resources.activation_decision(records, acceptance, profile)
    assert not result["activated_for_bounded_dev"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "failed"),
        ("view_events", 64),
        ("custody_completed", False),
        ("optimizer_steps_started", 1),
        ("engineering_policy_sha256", "bad"),
        ("model_config_sha256", "bad"),
    ],
)
def test_activation_failed_foreign_nonzero_or_partial_evidence(
    config, profile, field, value
):
    records = reader_results(config, profile)
    records["full_custody"][field] = value
    with pytest.raises(ValueError):
        resources.activation_decision(
            records, {"workspace_measurement": {"peak_tensor_bytes": 5228448}}, profile
        )


def test_task0011_existing_consumption_blocks_study(config, tmp_path, monkeypatch):
    monkeypatch.setattr(study, "ROOT", tmp_path)
    monkeypatch.setattr(study, "EXTRA_PREDECESSOR", {})
    monkeypatch.setattr(previous, "verify_predecessor", lambda *a: None)
    ledger = tmp_path / previous.LEDGER
    ledger.parent.mkdir(parents=True)
    ledger.write_text("consumed")
    with pytest.raises(ValueError, match="consumed"):
        study.verify_unused_predecessor(config)


def test_superseded_unused_task0011_route_refuses_before_any_reservation(
    config, tmp_path, monkeypatch
):
    monkeypatch.setattr(previous, "ROOT", tmp_path)
    marker = tmp_path / study.PLAN
    marker.parent.mkdir(parents=True)
    marker.write_text("study authorization")
    with pytest.raises(FileExistsError, match="superseded"):
        previous.recover(None, None, config)
    assert not (tmp_path / previous.LEDGER).exists()


def test_exclusive_study_failure_ends_later_stages_and_refuses_retry(
    config, profile, tmp_path, monkeypatch
):
    monkeypatch.setattr(study, "ROOT", tmp_path)
    monkeypatch.setattr(study, "verify_unused_predecessor", lambda *a: None)
    monkeypatch.setattr(study.bg, "verify_acceptance", lambda *a: {})
    accept = tmp_path / "acceptance.json"
    accept.write_text("{}")
    calls = []

    class Child:
        def __init__(self, command, **kwargs):
            phase = command[command.index("--worker") + 1]
            calls.append(phase)
            out = tmp_path / study.OUTPUT / phase
            out.mkdir()
            result = {
                "phase": phase,
                "status": "failed",
                "error": "controlled probe veto",
            }
            study.atomic_json(out / "stage-result.json", result)

        def wait(self, **kwargs):
            return 1

    monkeypatch.setattr(study.subprocess, "Popen", Child)
    result = study.run_study(accept, config, profile)
    assert result["status"] == "provisional_launch_still_blocked" and calls == [
        "pilot_preflight"
    ]
    original = (
        tmp_path / study.OUTPUT / "pilot_preflight-reservation.json"
    ).read_bytes()
    with pytest.raises(FileExistsError):
        study.run_study(accept, config, profile)
    assert (
        tmp_path / study.OUTPUT / "pilot_preflight-reservation.json"
    ).read_bytes() == original


def test_stale_source_acceptance_refuses_before_plan(
    config, profile, tmp_path, monkeypatch
):
    monkeypatch.setattr(study, "ROOT", tmp_path)
    accept = tmp_path / "acceptance.json"
    accept.write_text("{}")
    with pytest.raises(ValueError):
        study.run_study(accept, config, profile)
    assert not (tmp_path / study.PLAN).exists()


def worker_fixture(tmp_path, config, profile, phase="dev_reader"):
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text("{}")
    output = tmp_path / study.OUTPUT
    output.mkdir(parents=True)
    plan = {
        "acceptance_sha256": previous.file_hash(acceptance),
        "profile_sha256": content_hash(profile),
        "config_sha256": content_hash(config),
    }
    previous.exclusive_json(tmp_path / study.PLAN, plan)
    prior = study.PHASES[: study.PHASES.index(phase)]
    study.atomic_json(
        output / "workflow.json",
        {"stages": [{"phase": p, "status": "passed"} for p in prior]},
    )
    import time

    previous.exclusive_json(
        output / f"{phase}-reservation.json",
        {
            "phase": phase,
            "maximum_optimizer_steps": 96 if phase == "dev" else 0,
            "status": "reserved_no_automatic_retry",
            "token": "exclusive",
            "plan_sha256": previous.file_hash(tmp_path / study.PLAN),
            "started_monotonic": time.monotonic(),
        },
    )
    return acceptance


def test_worker_launch_recheck_blocks_reader_after_stable_pass(
    config, profile, tmp_path, monkeypatch
):
    assert preflight(config, profile, [sample()] * 3)["status"] == "passed"
    acceptance = worker_fixture(tmp_path, config, profile)
    monkeypatch.setattr(study, "ROOT", tmp_path)
    monkeypatch.setattr(study.torch, "set_num_interop_threads", lambda _: None)
    monkeypatch.setattr(
        study,
        "PolicyMonitor",
        lambda c, p, **kwargs: resources.PolicyMonitor(
            c, p, probe=lambda: sample(4 * 2**30), monitor_background=False
        ),
    )
    monkeypatch.setattr(
        study,
        "ProcessedStore",
        lambda *a: pytest.fail("reader opened after failed launch"),
    )
    assert study.worker("dev_reader", "exclusive", acceptance, config, profile) == 1
    result = json.loads(
        (tmp_path / study.OUTPUT / "dev_reader/stage-result.json").read_text()
    )
    assert "4.5GiB" in result["error"] and result["optimizer_steps_started"] == 0
    audit = json.loads(
        (tmp_path / study.OUTPUT / "dev_reader/access-audit.json").read_text()
    )
    assert audit["population_access"] == audit["custody_access"] == []


def test_foreign_worker_lineage_rejected_before_directory(
    config, profile, tmp_path, monkeypatch
):
    acceptance = worker_fixture(tmp_path, config, profile)
    monkeypatch.setattr(study, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="lineage"):
        study.worker("dev_reader", "foreign-token", acceptance, config, profile)
    assert not (tmp_path / study.OUTPUT / "dev_reader").exists()


@pytest.mark.parametrize(
    "field,value",
    [("phase", "dev"), ("maximum_optimizer_steps", 97), ("status", "retry_allowed")],
)
def test_worker_rejects_foreign_or_extra_phase_allowance(
    config, profile, tmp_path, monkeypatch, field, value
):
    acceptance = worker_fixture(tmp_path, config, profile)
    monkeypatch.setattr(study, "ROOT", tmp_path)
    path = tmp_path / study.OUTPUT / "dev_reader-reservation.json"
    reservation = json.loads(path.read_text())
    reservation[field] = value
    study.atomic_json(path, reservation)
    with pytest.raises(ValueError, match="lineage"):
        study.worker("dev_reader", "exclusive", acceptance, config, profile)
    assert not (tmp_path / study.OUTPUT / "dev_reader").exists()


def test_parent_timeout_preserves_reservation_and_never_retries(
    config, profile, tmp_path, monkeypatch
):
    monkeypatch.setattr(study, "ROOT", tmp_path)
    monkeypatch.setattr(study, "verify_unused_predecessor", lambda *a: None)
    monkeypatch.setattr(study.bg, "verify_acceptance", lambda *a: {})
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text("{}")
    import subprocess

    calls = []

    class Child:
        def __init__(self, *a, **k):
            self.stopped = False
            calls.append("spawn")

        def wait(self, timeout=None):
            if not self.stopped:
                raise subprocess.TimeoutExpired("controlled", timeout)

        def terminate(self):
            self.stopped = True

    monkeypatch.setattr(study.subprocess, "Popen", Child)
    result = study.run_study(acceptance, config, profile)
    assert result["status"] == "provisional_launch_still_blocked" and calls == ["spawn"]
    assert (tmp_path / study.OUTPUT / "pilot_preflight-reservation.json").exists()


def test_extra_predecessor_mismatch_refused_before_reservation(
    config, tmp_path, monkeypatch
):
    monkeypatch.setattr(study, "ROOT", tmp_path)
    monkeypatch.setattr(previous, "verify_predecessor", lambda *a: None)
    path = tmp_path / "prior.json"
    path.write_text("{}")
    monkeypatch.setattr(study, "EXTRA_PREDECESSOR", {"prior.json": "bad"})
    with pytest.raises(ValueError, match="predecessor"):
        study.verify_unused_predecessor(config)
