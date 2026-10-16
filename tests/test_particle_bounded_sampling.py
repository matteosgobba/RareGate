"""Synthetic age/publication/guard/routing proofs; no operational data required."""

import copy
import dataclasses
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest
import torch

from raregate.models.particle_memory_study import StudyAudit
from raregate.models.particle_set import ParticleSetAutoencoder, event_loss
from raregate.supervision import particle_launcher as io
from raregate.supervision import particle_sampling as sampling
from raregate.supervision import particle_sampling_benchmark as bench
from raregate.supervision.particle_monitor_benchmark import (
    fixture,
    physical_batches,
)
from raregate.training.autoencoder import deterministic_cpu
from raregate.training.particle_monitor_v3 import MonitorV3
from raregate.training.particle_monitor_v4 import (
    MonitorV4,
    definition,
    optimizer_observer,
    validate_manifest,
)
from raregate.training.particle_set import ResourceLimitError, adam


@pytest.fixture
def config():
    return io.read(io.ROOT / io.CONFIG)


@pytest.fixture
def profile():
    return io.read(io.ROOT / io.PROFILE)


def row(start=1.0, end=1.001, synthetic=True):
    f = fixture()
    return {
        k: f[k]
        for k in ("page_size_bytes", "free_pages", "inactive_pages", "available_bytes")
    } | {
        "backend": sampling.BACKEND,
        "query_start": start,
        "query_end": end,
        "raw": f["vm_stat_raw"],
        "synthetic": synthetic,
    }


@pytest.mark.parametrize("now", [0.001, 0.05, 0.1])
def test_age_from_query_start_and_boundary(now):
    o = sampling.observation(row(), "issuer", 1, 1.001)
    # Binary float boundary chosen from same difference; exact100ms allowed.
    o = dataclasses.replace(o, query_start=0.0, query_end=0.001, published_at=0.001)
    assert o.age(now, "issuer") <= 0.1


@pytest.mark.parametrize(
    "field,value",
    [
        ("query_start", float("nan")),
        ("query_end", None),
        ("published_at", float("inf")),
        ("query_end", 0.9),
        ("generation", True),
        ("generation", 0),
        ("backend", "direct_mach"),
        ("validated", False),
        ("issuer", "foreign"),
    ],
)
def test_invalid_provenance_timestamp_generation(field, value):
    o = sampling.observation(row(), "issuer", 1, 1.001)
    o = dataclasses.replace(o, **{field: value})
    with pytest.raises(sampling.ResourceLimitError):
        o.age(1.05, "issuer")


def test_publication_does_not_renew_age_and_expiration():
    o = sampling.observation(row(), "issuer", 1, 1.099)
    with pytest.raises(sampling.ResourceLimitError):
        o.age(1.101, "issuer")


@pytest.mark.parametrize(
    "key,value",
    [
        ("free_pages", False),
        ("available_bytes", 1),
        ("backend", "cached_unknown"),
        ("raw", "partial"),
        ("synthetic", 1),
        ("page_size_bytes", 0),
    ],
)
def test_partial_malformed_primary_rejected(key, value):
    r = row()
    r[key] = value
    with pytest.raises(sampling.ResourceLimitError):
        sampling.observation(r, "issuer", 1, 1.002)


class ManualSampler:
    def __init__(self, issuer, **kw):
        self.issuer, self.clock = issuer, kw["clock"]
        self.error = None
        self.refreshed = 0
        self.closed = False
        self.latest = None

    def start(self):
        self.refresh()

    def refresh(self):
        if self.error:
            raise sampling.ResourceLimitError(self.error)
        t = self.clock()
        self.refreshed += 1
        self.latest = sampling.observation(row(t, t), "issuer", self.refreshed, t)
        self.latest = dataclasses.replace(self.latest, issuer=self.issuer)
        return self.latest

    def get(self):
        if self.error:
            raise sampling.ResourceLimitError(self.error)
        if self.latest is None:
            raise sampling.ResourceLimitError("missing")
        return self.latest

    def fail(self, exc):
        self.error = self.error or str(exc)

    def close(self):
        self.closed = True

    def report(self):
        return {
            "host_queries_started": self.refreshed,
            "host_generations_published": self.refreshed,
            "latched_failure": self.error,
            "owned_thread_alive": False,
        }


def process_fixture():
    f = fixture()
    return {
        k: f[k]
        for k in (
            "peak_rss_bytes",
            "native_heap_reserved_bytes",
            "native_heap_in_use_bytes",
            "workspace_method",
            "pressure_dispatch_flags",
        )
    }


def mon(config, profile, **kwargs):
    return MonitorV4(
        config,
        profile,
        definition(),
        process_probe=kwargs.pop("process_probe", process_fixture),
        sampler_factory=ManualSampler,
        synthetic_fixture=True,
        notify_failure=False,
        **kwargs,
    )


def test_missing_host_sample_refused(config, profile):
    m = mon(config, profile)
    with pytest.raises(sampling.ResourceLimitError):
        m.check()
    assert m.error is not None
    m.close()


@pytest.mark.parametrize(
    "key,value",
    [
        ("pressure_dispatch_flags", 2),
        ("pressure_dispatch_flags", 4),
        ("native_heap_reserved_bytes", 512 * 2**20 + 1),
        ("peak_rss_bytes", 6 * 2**30 + 1),
        ("native_heap_reserved_bytes", None),
        ("native_heap_in_use_bytes", 300 * 2**20),
    ],
)
def test_process_veto_and_latching(config, profile, key, value):
    p = process_fixture()
    p[key] = value
    m = mon(config, profile, process_probe=lambda: p)
    with pytest.raises(ResourceLimitError):
        with m:
            pass
    p.update(process_fixture())
    with pytest.raises(ResourceLimitError):
        m.check()


def test_live_readiness_cannot_use_synthetic_host(config, profile):
    m = MonitorV4(
        config,
        profile,
        definition(),
        process_probe=process_fixture,
        sampler_factory=ManualSampler,
        notify_failure=False,
    )
    with pytest.raises(ResourceLimitError, match="Synthetic"):
        with m:
            pass


def test_phase_refresh_each_process_boundary_and_generation_counts(
    config, profile, tmp_path
):
    count = [0]

    def p():
        count[0] += 1
        return process_fixture()

    m = mon(config, profile, process_probe=p, directory=tmp_path)
    with m:
        init = m.sampler.refreshed
        m.check()
        m.check()
        assert m.sampler.refreshed == init
        m.phase = "constructor"
        assert m.sampler.refreshed == init + 1
        m.check()
        m.check()
    r = m.report()
    assert r["actual_fresh_process_checks"] == count[0] == 6
    assert r["sampler"]["host_queries_started"] == 3
    assert r["reused_host_guard_records"] >= 2
    lines = [
        json.loads(x)
        for x in (tmp_path / "guard-samples.jsonl").read_text().splitlines()
    ]
    assert all("process_query_start" in x and "host_query_start" in x for x in lines)


def test_concurrent_guards_and_stale_failure(config, profile):
    now = [1.0]
    m = mon(config, profile, clock=lambda: now[0])
    with m:
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: m.check(), range(32)))
        assert m.guards == 33
        now[0] = 1.101
        with pytest.raises(sampling.ResourceLimitError):
            m.check()
        now[0] = 1.01
        with pytest.raises(ResourceLimitError):
            m.check()


def test_blocked_work_signal_deadline(config, profile):
    m = mon(config, profile)
    with m, pytest.raises(ResourceLimitError), m.deadline("blocked", 0.02):
        time.sleep(0.1)


@pytest.mark.parametrize(
    "field,value",
    [
        ("host_age_upper_ceiling_seconds", 0.2),
        ("host_cadence_seconds", 0.1),
        ("maximum_additional_real_steps_started", 192),
        ("host_backend", "mach"),
        ("model_config_sha256", "foreign"),
        ("canonical_selection_calibration_freeze_authorized", True),
    ],
)
def test_manifest_no_override(config, profile, field, value):
    d = definition()
    d[field] = value
    with pytest.raises(ValueError):
        validate_manifest(d, config, profile)


def test_original_policy_and_all_limits_unchanged(config, profile):
    original = copy.deepcopy(config)
    assert definition()["limits"] == profile["limits"]
    assert definition()["phase_limits_seconds"] == {
        "readiness": 30,
        "dev_reader": 60,
        "dev_readiness": 30,
        "dev": 300,
    }
    assert definition()["remaining_full_run_limits"] == {
        "cycle_seconds": 180,
        "fit_per_run_seconds": 36000,
        "postfit_per_run_seconds": 3600,
        "two_run_total_seconds": 79200,
    }
    validate_manifest(definition(), config, profile)
    assert config == original


class PipeQuery:
    """Real owned pipe, synthetic query bytes, no system or dataset access."""

    def __init__(self, delay=0.0, fail=False):
        self.child = None
        self.delay = delay
        self.error = fail
        self.closed = False
        self.calls = 0

    def begin(self):
        assert self.child is None
        self.r, self.w = os.pipe()
        os.set_blocking(self.r, False)
        self.child = True
        self.started = time.monotonic()
        self.calls += 1
        if not self.delay:
            os.write(self.w, b"x")
            os.close(self.w)
        return self.r

    def drain(self):
        os.read(self.r, 32)
        return True

    def finish(self):
        if self.child is None:
            return None
        if time.monotonic() - self.started < self.delay:
            return None
        if self.error:
            raise RuntimeError("collector failed")
        os.close(self.r)
        self.child = None
        return row(self.started, time.monotonic())

    def close(self):
        self.closed = True
        if self.child:
            os.close(self.r)
            if self.delay:
                os.close(self.w)
            self.child = None


def test_sampling_schedule_publication_and_owned_cleanup():
    q = PipeQuery()
    ticks = []
    sampler = sampling.Sampler(
        "issuer", collector=q, on_tick=lambda v: ticks.append(time.monotonic())
    )
    sampler.start()
    try:
        first = sampler.refresh()
        time.sleep(0.06)
        second = sampler.get()
        assert second.generation > first.generation
        assert second.query_start >= first.query_start
    finally:
        sampler.close()
    assert q.closed and not sampler.thread.is_alive()
    assert len(ticks) >= 2 and q.calls <= 5


def test_slow_pending_query_tick_refresh_failure_and_no_restart():
    q = PipeQuery(delay=0.5)
    ticks = []
    sampler = sampling.Sampler(
        "issuer", collector=q, on_tick=lambda v: ticks.append(time.monotonic())
    )
    sampler.start()
    try:
        with pytest.raises(sampling.ResourceLimitError):
            sampler.refresh()
        assert sampler.error is not None and len(ticks) >= 2 and q.calls == 1
        with pytest.raises(sampling.ResourceLimitError):
            sampler.start()
    finally:
        sampler.close()
    assert q.closed


def test_error_latched_even_after_good_looking_publication():
    q = PipeQuery(fail=True)
    sampler = sampling.Sampler("issuer", collector=q)
    sampler.start()
    try:
        with pytest.raises(sampling.ResourceLimitError):
            sampler.refresh()
        sampler.latest = sampling.observation(
            row(time.monotonic(), time.monotonic()), "issuer", 10, time.monotonic()
        )
        with pytest.raises(sampling.ResourceLimitError):
            sampler.get()
    finally:
        sampler.close()


def test_synthetic_v3_v4_exact_Adam_parameter_reconstruction_score_parity(
    config, profile, tmp_path
):
    from raregate.data.features import Parameters, model_view

    params = Parameters.from_config(io.read(io.ROOT / "configs/data/lhco_rnd_v5.json"))
    batches = physical_batches()
    out = []
    for version in (3, 4):
        directory = tmp_path / str(version)
        directory.mkdir()
        m = (
            MonitorV3(
                config,
                profile,
                io.read(
                    io.ROOT / "configs/resources/particle_resource_monitor_v3.json"
                ),
                probe=fixture,
                monitor_background=False,
                synthetic_fixture=True,
            )
            if version == 3
            else mon(config, profile, directory=directory)
        )
        audit = StudyAudit(directory / "audit.json")
        with m, deterministic_cpu(1729, 1):
            model = ParticleSetAutoencoder()
            opt = adam(model, config)
            if version == 4:
                optimizer_observer(audit, m)(opt)
            else:
                audit.observe_optimizer(opt)
            for b in batches:
                m.check()
                v = model_view(*b, params)
                x, mask = torch.from_numpy(v.features), torch.from_numpy(v.mask)
                opt.zero_grad(set_to_none=True)
                loss = event_loss(x, model(x, mask), mask).mean()
                loss.backward()
                opt.step()
                m.check()
            out.append(
                (
                    model.state_dict(),
                    opt.state_dict(),
                    model(x, mask).detach(),
                    model.score(x, mask),
                    loss.item(),
                )
            )
        assert audit.steps_started == audit.steps_completed == 2
    assert all(torch.equal(out[0][0][k], out[1][0][k]) for k in out[0][0])
    assert all(
        torch.equal(out[0][1]["state"][k][n], out[1][1]["state"][k][n])
        for k in out[0][1]["state"]
        for n in out[0][1]["state"][k]
    )
    assert (
        torch.equal(out[0][2], out[1][2])
        and np.array_equal(out[0][3], out[1][3])
        and out[0][4] == out[1][4]
    )


def test_material_gate_complete_fixed_repetitions_and_no_best_selection():
    rows = []
    for rep, arm in bench.ORDER:
        rows.append(
            {
                "rep": rep,
                "arm": arm,
                "status": "completed",
                "numerical_identity": {"same": True},
                "workload_wall_seconds": 0.4
                if arm == "v3"
                else 0.12
                if arm == "v4"
                else 0.07,
                "resources": {
                    "host_age_statistics": {"max_seconds": 0.05},
                    "sampler": {"latched_failure": None, "owned_thread_alive": False},
                },
            }
        )
    assert bench.evaluate(rows)["material_improvement_pass"]
    rows[4]["workload_wall_seconds"] = 0.5
    assert bench.evaluate(rows)[
        "material_improvement_pass"
    ]  # predetermined median, no dropped repetition
    rows[7]["workload_wall_seconds"] = 0.5
    assert not bench.evaluate(rows)["material_improvement_pass"]
    assert not bench.evaluate(rows[:-1])["material_improvement_pass"]


def test_stdlib_sampler_and_supervisor_source_coverage():
    code = "from raregate.supervision import particle_sampling,particle_sampling_benchmark;from raregate.supervision import particle_launcher as c;c.assert_lightweight()"
    subprocess.run(
        [sys.executable, "-c", code], check=True, capture_output=True, timeout=10
    )
    for p in (
        "src/raregate/supervision/particle_sampling.py",
        "src/raregate/supervision/particle_sampling_benchmark.py",
        "src/raregate/training/particle_monitor_v4.py",
        "tests/test_particle_bounded_sampling.py",
    ):
        assert p in io.source_hashes()


def test_lightweight_controller_worker_imports_and_source_binding():
    code = "from raregate.supervision import particle_bounded_study,particle_bounded_worker;from raregate.supervision import particle_launcher as c;c.assert_lightweight()"
    subprocess.run(
        [sys.executable, "-c", code], check=True, capture_output=True, timeout=10
    )
    from raregate.supervision import particle_bounded_study as route

    assert io.digest(io.read(io.ROOT / route.MONITOR)) == route.MONITOR_HASH
    for p in (
        "src/raregate/supervision/particle_bounded_study.py",
        "src/raregate/supervision/particle_bounded_worker.py",
    ):
        assert p in io.source_hashes()


@pytest.mark.parametrize(
    "phase", ["fit", "calibration", "test_background", "test_signal", "full_custody"]
)
def test_no_canonical_test_or_custody_phase(phase):
    from raregate.supervision import particle_bounded_study as route

    with pytest.raises(ValueError):
        route.authorize(phase, {"stages": []})


def test_fixed_phase_order_failure_blocks_downstream():
    from raregate.supervision import particle_bounded_study as route

    assert route.PHASES == ("dev_reader", "dev_readiness", "dev")
    assert route.SECONDS == {"dev_reader": 60, "dev_readiness": 30, "dev": 300}
    route.authorize("dev_reader", {"stages": []})
    with pytest.raises(ValueError):
        route.authorize(
            "dev", {"stages": [{"phase": "dev_reader", "status": "passed"}]}
        )
    with pytest.raises(ValueError):
        route.authorize(
            "dev_readiness", {"stages": [{"phase": "dev_reader", "status": "failed"}]}
        )


def test_additional_cumulative_step_reservation_before_mutation(tmp_path):
    from raregate.supervision.particle_bounded_worker import additional_audit

    audit = additional_audit(StudyAudit, tmp_path / "audit.json")
    p = torch.nn.Parameter(torch.tensor([1.0]))
    opt = torch.optim.Adam([p], lr=0.001)
    audit.observe_optimizer(opt)
    before = []

    def check(*_):
        record = io.read(audit.path)
        assert record["additional_inflight_steps"] == 1
        assert record["cumulative_optimizer_steps_started"] == 97
        before.append(p.detach().clone())

    opt.register_step_pre_hook(check)
    p.grad = torch.ones_like(p)
    opt.step()
    assert torch.equal(before[0], torch.tensor([1.0]))
    record = io.read(audit.path)
    assert record["additional_optimizer_steps_completed"] == 1
    assert record["additional_inflight_steps"] == 0
    audit.steps_started = audit.steps_completed = 96
    audit.save()
    assert io.read(audit.path)["cumulative_optimizer_steps_started"] == 192
    with pytest.raises(ValueError):
        opt.step()


def test_guard_failure_prevents_optimizer_reservation(config, profile, tmp_path):
    audit = StudyAudit(tmp_path / "audit.json")
    m = mon(config, profile)
    p = torch.nn.Parameter(torch.tensor([1.0]))
    opt = torch.optim.Adam([p])
    optimizer_observer(audit, m)(opt)
    p.grad = torch.ones_like(p)
    with m:
        m.error = "latched host failure"
        with pytest.raises(ResourceLimitError):
            opt.step()
    assert audit.steps_started == 0 and p.item() == 1.0


@pytest.mark.parametrize("available,passed", [(4.5, True), (4.5 - 1 / 65536, False)])
def test_launch_availability_equality_and_below(config, profile, available, passed):
    class LaunchSampler(ManualSampler):
        def refresh(self):
            super().refresh()
            bytes_ = int(available * 2**30)
            self.latest = dataclasses.replace(
                self.latest,
                free_pages=0,
                inactive_pages=bytes_ // 16384,
                available_bytes=bytes_,
            )
            return self.latest

    m = MonitorV4(
        config,
        profile,
        definition(),
        process_probe=process_fixture,
        sampler_factory=LaunchSampler,
        synthetic_fixture=True,
        notify_failure=False,
    )
    if passed:
        with m:
            pass
    else:
        with pytest.raises(ResourceLimitError):
            with m:
                pass


def test_process_pressure_unknown_allowed_and_cap_equality(config, profile):
    p = process_fixture()
    p.update(
        pressure_dispatch_flags=None,
        peak_rss_bytes=6 * 2**30,
        native_heap_reserved_bytes=512 * 2**20,
    )
    with mon(config, profile, process_probe=lambda: p) as m:
        m.check()
        assert m.last["pressure_dispatch_flags"] is None


def test_real_slot_not_created_when_material_gate_fails(monkeypatch, tmp_path):
    from raregate.supervision import particle_bounded_study as route

    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(io, "assert_lightweight", lambda: None)
    monkeypatch.setattr(
        route,
        "verify_material",
        lambda: (_ for _ in ()).throw(ValueError("material gate failed")),
    )
    with pytest.raises(ValueError, match="material"):
        route.study("automatic")
    assert not (tmp_path / route.PLAN).exists()
    assert not (tmp_path / route.SLOT).exists()


def test_readiness_timeout_preserved_without_attempt_or_retry(monkeypatch, tmp_path):
    from raregate.supervision import particle_bounded_study as route

    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(route, "verify_plan", lambda: {})
    plan = tmp_path / route.PLAN
    plan.parent.mkdir(parents=True)
    io.exclusive(plan, {})
    monkeypatch.setattr(
        io,
        "dispatch",
        lambda *a, **kw: (_ for _ in ()).throw(TimeoutError("owned worker stopped")),
    )
    ok, receipt = route.dispatch_readiness("automatic")
    assert not ok and receipt["new_real_steps"] == 0
    assert "owned worker stopped" in receipt["parent_dispatch"]["dispatch_error"]
    assert not (tmp_path / route.SLOT).exists()
    with pytest.raises(FileExistsError):
        route.dispatch_readiness("automatic")


def test_failed_readiness_does_not_reserve_and_consumed_slot_refuses(
    monkeypatch, tmp_path
):
    from raregate.supervision import particle_bounded_study as route

    monkeypatch.setattr(io, "ROOT", tmp_path)
    monkeypatch.setattr(io, "assert_lightweight", lambda: None)
    monkeypatch.setattr(route, "prepare", lambda: {})
    monkeypatch.setattr(
        route, "dispatch_readiness", lambda _: (False, {"status": "failed"})
    )
    result = route.study("automatic")
    assert not result["slot_reserved"] and result["cumulative_steps"] == 96
    io.exclusive(tmp_path / route.SLOT, {"consumed": True})
    with pytest.raises(FileExistsError):
        route.study("manual")


def test_task_owned_system_query_cleanup_and_timeout(monkeypatch):
    popen = subprocess.Popen
    monkeypatch.setattr(
        sampling.subprocess,
        "Popen",
        lambda args, **kw: popen(
            [sys.executable, "-c", "import time;time.sleep(10)"], **kw
        ),
    )
    now = [0.0]
    q = sampling.SystemQuery(clock=lambda: now[0])
    q.begin()
    child = q.child
    with pytest.raises(sampling.ResourceLimitError):
        q.begin()
    now[0] = 2.001
    with pytest.raises(sampling.ResourceLimitError, match="timeout"):
        q.finish()
    q.close()
    assert child.poll() is not None and q.child is None and child.stdout.closed


@pytest.mark.parametrize(
    "key,value",
    [
        ("native_heap_reserved_bytes", 512 * 2**20 + 1),
        ("peak_rss_bytes", 6 * 2**30 + 1),
    ],
)
def test_veto_preserves_actual_failed_process_peak(config, profile, key, value):
    p = process_fixture()
    m = mon(config, profile, process_probe=lambda: p)
    with m:
        p[key] = value
        with pytest.raises(ResourceLimitError):
            m.check()
    r = m.report()
    assert r[key] == value
    assert r["last_failure"]["process_observation"][key] == value
    phase_key = (
        "native_peak_reserved_bytes"
        if key.startswith("native")
        else "lifetime_peak_rss_at_samples_bytes"
    )
    assert r["phases"]["startup"][phase_key] == value
