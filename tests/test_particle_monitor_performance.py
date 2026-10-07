"""Synthetic v3 accounting/guards/numerical parity; no real host or populations."""

import copy
import ctypes as C
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from latenttrigger.models import particle_memory_study as old_study
from latenttrigger.models.particle_set import ParticleSetAutoencoder, event_loss
from latenttrigger.supervision import particle_collector as collect
from latenttrigger.supervision import particle_launcher as io
from latenttrigger.supervision import particle_monitor_benchmark as bench
from latenttrigger.supervision import particle_reconciliation as recon
from latenttrigger.training.autoencoder import deterministic_cpu
from latenttrigger.training.particle_monitor_v3 import (
    MonitorV3,
    definition,
    validate_manifest,
)
from latenttrigger.training.particle_resources import PolicyMonitor
from latenttrigger.training.particle_set import ResourceLimitError, adam


@pytest.fixture
def config():
    return io.read(io.ROOT / io.CONFIG)


@pytest.fixture
def profile():
    return io.read(io.ROOT / io.PROFILE)


@pytest.mark.parametrize(
    "free,spec,inactive,page",
    [(10, 3, 5, 16384), (0, 0, 0, 4096), (2**32 - 1, 0, 1, 65536)],
)
def test_native_display_metric_exact_parity(free, spec, inactive, page):
    v = collect.normalize_native(
        {"free_count": free, "speculative_count": spec, "inactive_count": inactive},
        page,
    )
    raw = f"page size of {page} bytes\nPages free: {free - spec}.\nPages inactive: {inactive}.\n"
    for key, value in collect.parse_vm_stat(raw).items():
        if key in v:
            assert v[key] == value
    assert v["native_free_count"] == free and v["free_pages"] == free - spec


@pytest.mark.parametrize(
    "raw,page",
    [
        ({"free_count": 1, "speculative_count": 2, "inactive_count": 3}, 16384),
        ({"free_count": 1, "speculative_count": False, "inactive_count": 3}, 16384),
        ({"free_count": 1, "speculative_count": 0, "inactive_count": -1}, 16384),
        ({"free_count": 1, "speculative_count": 0, "inactive_count": 1}, 0),
        ({"free_count": 1, "speculative_count": 0, "inactive_count": 1}, True),
    ],
)
def test_invalid_native_counts_fail_closed(raw, page):
    with pytest.raises(collect.ResourceLimitError):
        collect.normalize_native(raw, page)


def test_abi_layout_and_unsupported(monkeypatch):
    collect.validate_abi()
    assert (
        C.sizeof(collect.VMRev1) == 152
        and collect.VMRev1.speculative_count.offset == 92
    )
    monkeypatch.setattr(collect.C, "sizeof", lambda t: 1)
    with pytest.raises(collect.ResourceLimitError):
        collect.validate_abi()


@pytest.mark.parametrize("rc,count", [(1, 38), (0, 37), (0, 40)])
def test_mach_return_count_rejected(rc, count):
    obj = collect.MachDiagnosticCollector.__new__(collect.MachDiagnosticCollector)
    obj.host = 1
    obj.page_size = 16384

    def query(host, flavor, data, n):
        n._obj.value = count
        return rc

    obj.vm = query
    with pytest.raises(collect.ResourceLimitError):
        obj()


def test_cached_collector_exact_raw_timeout_and_no_value_cache():
    calls = []

    def run(cmd, **kw):
        calls.append((cmd, kw))
        return (
            f"page size of 16384 bytes\nPages free: {len(calls)}.\nPages inactive: 0.\n"
        )

    bindings = SimpleNamespace(process_sample=lambda: {"native_heap_reserved_bytes": 1})
    c = collect.CachedSystemCollector(bindings=bindings, run=run)
    a, b = c(), c()
    assert len(calls) == 2 and a["available_bytes"] != b["available_bytes"]
    assert calls[0] == (["/usr/bin/vm_stat"], {"text": True, "timeout": 2})
    assert "vm_stat_raw" in a and a["primary_values_reused"] is False


@pytest.mark.parametrize(
    "failure", [OSError("unavailable"), subprocess.TimeoutExpired("vm_stat", 2)]
)
def test_primary_query_error_no_fallback(failure):
    c = collect.CachedSystemCollector(
        bindings=SimpleNamespace(), run=lambda *a, **k: (_ for _ in ()).throw(failure)
    )
    with pytest.raises(type(failure)):
        c()


def test_collector_elapsed_age_bound():
    times = iter([0, 3])
    c = collect.CachedSystemCollector(
        bindings=SimpleNamespace(process_sample=lambda: {}),
        run=lambda *a, **k: (
            "page size of 16384 bytes\nPages free: 1.\nPages inactive: 0.\n"
        ),
        clock=lambda: next(times),
    )
    with pytest.raises(collect.ResourceLimitError, match="age"):
        c()


@pytest.mark.parametrize(
    "field,value",
    [
        ("implementation_version", 2),
        ("backend", "native"),
        ("watch_interval_seconds", 1),
        ("real_execution_authorized", True),
        ("model_config_sha256", "bad"),
        ("status", "real_validated"),
        ("canonical_training_authorized", True),
    ],
)
def test_manifest_strict_no_science_or_limit_override(config, profile, field, value):
    m = definition()
    m[field] = value
    with pytest.raises(ValueError):
        validate_manifest(m, config, profile)


def test_manifest_config_policy_acceptance_binding(config, profile):
    original = copy.deepcopy(config)
    validate_manifest(definition(), config, profile)
    with pytest.raises(ValueError):
        validate_manifest(
            definition(), config, profile, acceptance={"pytest_exit_code": 0}
        )
    assert config == original and profile["scope"].startswith("Task0012")
    assert definition()["limits"] == profile["limits"]


def monitor(tmp_path, config, profile, probe=None, **kwargs):
    return MonitorV3(
        config,
        profile,
        definition(),
        probe=probe or bench.fixture,
        journal=tmp_path / "samples.jsonl",
        monitor_background=False,
        synthetic_fixture=True,
        **kwargs,
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("available_bytes", 0),
        ("native_heap_reserved_bytes", 536870913),
        ("peak_rss_bytes", 6442450945),
        ("pressure_dispatch_flags", 2),
        ("pressure_dispatch_flags", 4),
        ("page_size_bytes", None),
        ("available_method", "raw_free_plus_inactive"),
        ("collector_backend", "host_statistics64_rev1_diagnostic_only"),
        ("primary_values_reused", True),
    ],
)
def test_low_unknown_veto_backend_and_failed_receipt(
    tmp_path, config, profile, field, value
):
    sample = bench.fixture()
    sample[field] = value
    m = monitor(tmp_path, config, profile, lambda: sample)
    with pytest.raises(ResourceLimitError):
        m.check(launch=True)
    assert m.report()["last_failure"] is not None
    m.close()


def test_threshold_equality_and_unknown_optional(tmp_path, config, profile):
    sample = bench.fixture()
    sample.update(
        collect.parse_vm_stat(
            "page size of 16384 bytes\nPages free: 294912.\nPages inactive: 0.\n"
        )
    )
    sample.update(
        peak_rss_bytes=6 * 2**30,
        native_heap_reserved_bytes=512 * 2**20,
        current_rss_bytes=None,
        pressure_dispatch_flags=None,
    )
    m = monitor(tmp_path, config, profile, lambda: sample)
    m.check(launch=True)
    assert m.samples == 1
    m.close()


@pytest.mark.parametrize("delta", [-1, 3, float("nan"), float("inf")])
def test_stale_primary_rejected(tmp_path, config, profile, delta):
    sample = bench.fixture()
    sample["sample_started_monotonic"] -= delta
    m = monitor(tmp_path, config, profile, lambda: sample)
    with pytest.raises(ResourceLimitError):
        m.check()
    m.close()


def test_fixture_cannot_label_live_check(tmp_path, config, profile):
    m = MonitorV3(
        config, profile, definition(), probe=bench.fixture, monitor_background=False
    )
    with pytest.raises(ResourceLimitError, match="fixture"):
        m.check()


def test_concurrent_checks_flush_journal_and_phase_counts(tmp_path, config, profile):
    m = monitor(tmp_path, config, profile)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: m.check(), range(32)))
    m.close()
    lines = (tmp_path / "samples.jsonl").read_text().splitlines()
    assert len(lines) == m.samples == 32
    assert m.phases["startup"]["samples"] == 32
    assert sum(m.check_threads.values()) == 32
    assert all(json.loads(x)["diagnostic_guard_fixture"] for x in lines)


def test_deadline_before_and_after_probe(tmp_path, config, profile):
    now = [0.0]

    def probe():
        row = bench.fixture(clock=lambda: now[0])
        now[0] = 2
        return row

    m = monitor(tmp_path, config, profile, probe, clock=lambda: now[0])
    m.deadlines["phase"] = 1
    with pytest.raises(ResourceLimitError, match="ceiling"):
        m.check()
    m.close()


def test_collector_exception_preserved(tmp_path, config, profile):
    m = monitor(
        tmp_path,
        config,
        profile,
        lambda: (_ for _ in ()).throw(OSError("probe failed")),
    )
    with pytest.raises(OSError):
        m.check()
    assert m.report()["last_failure"]["error"] == "probe failed"


def test_unchanged_numeric_and_optimizer_with_instrumentation(
    tmp_path, config, profile
):
    from latenttrigger.data.features import Parameters, model_view

    p = Parameters.from_config(io.read(io.ROOT / "configs/data/lhco_rnd_v5.json"))
    batches = bench.physical_batches()
    out = []
    for kind in ("old", "v3"):
        journal = tmp_path / f"{kind}.jsonl"
        m = (
            PolicyMonitor(
                config,
                profile,
                probe=bench.fixture,
                journal=journal,
                monitor_background=False,
            )
            if kind == "old"
            else MonitorV3(
                config,
                profile,
                definition(),
                probe=bench.fixture,
                journal=journal,
                monitor_background=False,
                synthetic_fixture=True,
            )
        )
        audit = old_study.StudyAudit(tmp_path / f"{kind}-audit.json")
        with m, deterministic_cpu(1729, 1):
            model = ParticleSetAutoencoder()
            opt = adam(model, config)
            audit.observe_optimizer(opt)
            losses = []
            for b in batches:
                m.check()
                v = model_view(*b, p)
                x, mask = torch.from_numpy(v.features), torch.from_numpy(v.mask)
                opt.zero_grad(set_to_none=True)
                value = event_loss(x, model(x, mask), mask)
                value.mean().backward()
                opt.step()
                m.check()
                losses.append(value.detach().clone())
            out.append(
                (
                    model.state_dict(),
                    opt.state_dict(),
                    model(x, mask).detach(),
                    model.score(x, mask),
                    losses,
                )
            )
        assert audit.steps_started == audit.steps_completed == 2
    for k in out[0][0]:
        assert torch.equal(out[0][0][k], out[1][0][k])
    for k in out[0][1]["state"]:
        for n in out[0][1]["state"][k]:
            assert torch.equal(out[0][1]["state"][k][n], out[1][1]["state"][k][n])
    assert torch.equal(out[0][2], out[1][2]) and np.array_equal(out[0][3], out[1][3])
    assert all(torch.equal(a, b) for a, b in zip(out[0][4], out[1][4], strict=True))


def test_synthetic_source_coverage_and_parent_import():
    code = "from latenttrigger.supervision import particle_collector,particle_reconciliation,particle_monitor_benchmark;from latenttrigger.supervision import particle_launcher as c;c.assert_lightweight()"
    subprocess.run(
        [sys.executable, "-c", code], check=True, capture_output=True, timeout=10
    )
    mapping = io.source_hashes()
    for p in (
        "src/latenttrigger/supervision/particle_collector.py",
        "src/latenttrigger/supervision/particle_reconciliation.py",
        "src/latenttrigger/supervision/particle_monitor_benchmark.py",
        "src/latenttrigger/training/particle_monitor_v3.py",
    ):
        assert p in mapping


def test_no_real_route_and_fixed_budget():
    assert bench.SPEC["real_events_steps_authorized"] == 0
    assert bench.SPEC["resident_physical_batches"] == 2
    assert bench.ARMS == (
        "collectors",
        "checks_old",
        "checks_v3",
        "workload_compute",
        "workload_old",
        "workload_v3",
    )
    assert definition()["real_execution_authorized"] is False


def historical_fixture(tmp_path):
    # Explicit synthetic receipts, no operational ignored files or arrays.
    for rel in (io.CONFIG, io.PROFILE, io.PROMPT):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((io.ROOT / rel).read_bytes())
    acceptance_path = tmp_path / io.ACCEPTANCE
    acceptance_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in (".pytest.xml", ".pytest.log"):
        acceptance_path.with_suffix(suffix).write_text(
            "synthetic historic test evidence"
        )
    accepted = {
        "pytest_exit_code": 0,
        "pytest_passed": 422,
        "source_sha256": {},
        "pytest_xml_sha256": io.file_hash(acceptance_path.with_suffix(".pytest.xml")),
        "pytest_log_sha256": io.file_hash(acceptance_path.with_suffix(".pytest.log")),
        "workspace_measurement": {"peak_tensor_bytes": 5228448},
    }
    io.exclusive(acceptance_path, accepted)
    plan = {
        "source_sha256": {},
        "acceptance_sha256": io.file_hash(acceptance_path),
        "profile_sha256": io.PROFILE_HASH,
        "config_sha256": io.CONFIG_HASH,
        "prompt_sha256": io.file_hash(tmp_path / io.PROMPT),
    }
    io.exclusive(tmp_path / io.PLAN, plan)
    io.exclusive(
        tmp_path / io.SLOT,
        {
            "plan_sha256": io.file_hash(tmp_path / io.PLAN),
            "status": "reserved_no_retry",
            "reserved_utc": "synthetic_fixture",
        },
    )
    base = tmp_path / recon.BASE
    stages = []
    for phase in io.PHASES:
        rows = []
        if phase == "dev_reader":
            counts = [64]
        elif phase == "dev":
            counts = [1024] * 4
        else:
            counts = []
        rows = [
            {
                "split": "train_background",
                "allow_test": False,
                "include_labels": False,
                "dev_only": True,
                "status": "completed",
                "events_read": n,
            }
            for n in counts
        ]
        steps = 96 if phase == "dev" else 0
        audit = {
            "population_access": rows,
            "optimizer_steps_started": steps,
            "optimizer_steps_completed": steps,
            "possible_inflight_optimizer_step": False,
            "unique_dev_sample_events": 1024
            if phase == "dev"
            else 64
            if phase == "dev_reader"
            else 0,
            "test_background_model_access": False,
            "test_signal_model_access": False,
        }
        path = base / phase / "access-audit.json"
        io.exclusive(path, audit)
        resources = {
            "minimum_available_bytes": 9 * 2**30,
            "native_heap_reserved_bytes": 200 * 2**20,
            "peak_rss_bytes": 400 * 2**20,
            "samples": 287,
            "phases": {
                "startup": {"first": {"native_heap_reserved_bytes": 200 * 2**20}}
            },
        }
        record = {
            "phase": phase,
            "status": "failed" if phase == "dev" else "passed",
            "execution_plan_sha256": io.file_hash(tmp_path / io.PLAN),
            "acceptance_sha256": io.file_hash(acceptance_path),
            "model_config_sha256": io.CONFIG_HASH,
            "engineering_policy_sha256": io.PROFILE_HASH,
            "audit_file_sha256": io.file_hash(path),
            "custody_completed": True,
            "view_events": 64 if phase == "dev_reader" else 0,
            "optimizer_steps_started": steps,
            "optimizer_steps_completed": steps,
            "resources": resources,
        }
        io.exclusive(base / phase / "stage-result.json", record)
        stages.append(record)
        io.exclusive(
            base / f"{phase}-reservation.json",
            {
                "plan_sha256": io.file_hash(tmp_path / io.PLAN),
                "slot_sha256": io.file_hash(tmp_path / io.SLOT),
                "maximum_optimizer_steps": steps,
                "status": "reserved_no_automatic_retry",
            },
        )
    gate = {
        "passes": 3,
        "optimizer_steps": 96,
        "unique_events": 1024,
        "feasibility_pass": False,
        "train_pass_seconds": [
            0.5065042919995904,
            0.4505980419999105,
            0.45002770899918687,
        ],
        "score_pass_seconds": 0.3897375420001481,
        "extrapolated_full_cycle_seconds": 749.3431957854029,
    }
    io.exclusive(base / "dev/dev-gate.json", gate)
    io.exclusive(base / "dev/dev-progress.json", {"completed_passes": 3, "steps": 96})
    (base / "dev/resource-samples.jsonl").write_text("{}\n" * 287)
    activation = io.activation(
        {r["phase"]: r for r in stages if r["phase"] in ("dev_reader", "full_custody")},
        accepted,
        io.read(tmp_path / io.PROFILE),
    )
    activation["reader_result_file_sha256"] = {
        p: io.file_hash(base / p / "stage-result.json")
        for p in ("dev_reader", "full_custody")
    }
    io.exclusive(base / "activation.json", activation)
    io.exclusive(
        base / "workflow.json",
        {
            "stages": stages,
            "status": "bounded_study_failed",
            "failed_phase": "dev",
            "error": "Frozen conservative dev extrapolation exceeds180s.",
        },
    )
    return tmp_path


def test_reconciled_historical_budget_without_any_reader(tmp_path):
    r = recon.reconcile(historical_fixture(tmp_path))
    assert r["projection"]["projected_full_cycle_seconds"] == 749.3431957854029
    assert (
        r["access"]["optimizer_steps_completed"] == 96
        and r["access"]["remaining_original_steps"] == 0
    )
    assert (
        r["access"]["view_presentations"] == 4160
        and r["access"]["population_requests"] == 5
    )


def test_reconciliation_rejects_unexpected_consumption(tmp_path):
    root = historical_fixture(tmp_path)
    path = root / recon.BASE / "dev/access-audit.json"
    value = io.read(path)
    value["optimizer_steps_started"] = 97
    io.atomic(path, value)
    with pytest.raises(ValueError):
        recon.reconcile(root)


def test_native_primary_and_optional_unknowns():
    b = collect.DarwinBindings.__new__(collect.DarwinBindings)

    def malloc(zone, stats):
        stats._obj.allocated = 1024
        stats._obj.in_use = 512

    b.malloc = malloc
    b.task_info = None
    b.sysctl = None
    b.task = None
    s = b.process_sample()
    assert s["native_heap_reserved_bytes"] == 1024
    assert s["current_rss_bytes"] is None and s["pressure_dispatch_flags"] is None
    b.malloc = lambda zone, stats: None
    with pytest.raises(collect.ResourceLimitError):
        b.process_sample()


def test_cached_bindings_unsupported_platform(monkeypatch):
    monkeypatch.setattr(collect.platform, "system", lambda: "unsupported")
    with pytest.raises(collect.ResourceLimitError, match="unavailable"):
        collect.DarwinBindings()
