"""Self-contained benchmark contracts, numerics and finite control failures."""

import copy
import io
import json
import os
import subprocess
import sys
import threading
import time
from types import SimpleNamespace

import numpy as np
import pytest

from raregate.benchmarks import (
    accelerate_threads,
    core,
    frozen_cpu,
    guard,
    protocol,
    worker,
)


@pytest.fixture
def spec():
    return protocol.load()


def sample(**changes):
    return {
        "peak_rss_bytes": 32 * 2**20,
        "native_heap_reserved_bytes": 40 * 2**20,
        "native_heap_in_use_bytes": 20 * 2**20,
        "workspace_method": guard.NATIVE_METHOD,
        "pressure_dispatch_flags": None,
        "pressure_errno": 1,
        "pressure_method": guard.PRESSURE_METHOD,
        **changes,
    }


class FakeGuard:
    def __init__(self):
        self.checks = 0

    def check(self):
        self.checks += 1

    def boundary(self, _):
        self.check()


def pca():
    return core.PCAReconstruction(
        np.zeros(8), np.eye(8), np.ones(8), np.full(8, 0.125), 6, 0.95, 1024
    )


@pytest.mark.parametrize(
    "change",
    [
        {"extra": True},
        {"warmups": 21},
        {"measurements": 199},
        {"output": "other"},
        {"batch_grid": [1, 1024]},
        {"optimizer_updates": 1},
        {"schema_version": True},
        {"worker_order": ["AE1", "PCA1"]},
        {"warmups": 20.0},
    ],
)
def test_protocol_exact_no_overrides(tmp_path, spec, change):
    path = tmp_path / protocol.CONFIG
    path.parent.mkdir(parents=True)
    protocol.write(path, spec | change)
    with pytest.raises(ValueError, match="Unsupported protocol"):
        protocol.load(tmp_path)


@pytest.mark.parametrize("content", ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'])
def test_strict_json(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content)
    with pytest.raises(ValueError):
        protocol.read(path)


@pytest.mark.parametrize(
    "split,dev,test,labels",
    [
        ("test_background", True, False, False),
        ("test_signal", True, True, True),
        ("validation_selection_background", True, False, False),
        ("train_background", False, False, False),
        ("train_background", True, True, False),
        ("train_background", True, False, True),
        ("train_background", 1, False, False),
        ("unknown", True, False, False),
    ],
)
def test_scope_refusal(tmp_path, split, dev, test, labels):
    with pytest.raises(ValueError):
        protocol.validate_scope(
            tmp_path / "data/processed/lhco-rd-v1/schema-v1/dev",
            split,
            dev,
            test,
            labels,
            tmp_path,
        )


def test_full_and_symlink_scope_refusal(tmp_path):
    expected = tmp_path / "data/processed/lhco-rd-v1/schema-v1/dev"
    expected.parent.mkdir(parents=True)
    full = expected.with_name("full")
    full.mkdir()
    for path in [full, full / ".." / "dev"]:
        with pytest.raises(ValueError):
            protocol.validate_scope(
                path, "train_background", True, False, False, tmp_path
            )
    expected.symlink_to(full, target_is_directory=True)
    with pytest.raises(ValueError):
        protocol.validate_scope(
            expected, "train_background", True, False, False, tmp_path
        )


def synthetic_manifest(tmp_path):
    split = {"seed": 1729}
    channels = [str(i) for i in range(8)]
    science = {
        "scope": "dev",
        "aggregate_channels": channels,
        "config_sha256": "c" * 64,
        "split_identity": split,
        "split_identity_sha256": protocol.digest(split),
        "counts": {"train_background": 1024, "test_background": 0, "test_signal": 0},
    }
    manifest = {
        "schema_version": 1,
        "complete": True,
        "scientific": science,
        "scientific_sha256": protocol.digest(science),
    }
    expected = {
        "scientific_sha256": manifest["scientific_sha256"],
        "channels": channels,
        "preprocessing_file_sha256": "c" * 64,
        "split_scientific_sha256": protocol.digest(split),
        "store": "data/processed/lhco-rd-v1/schema-v1/dev",
        "population": "train_background",
        "dev_only": True,
        "allow_test": False,
        "include_labels": False,
    }
    path = tmp_path / expected["store"] / "manifest.json"
    path.parent.mkdir(parents=True)
    protocol.write(path, manifest)
    return manifest, expected


@pytest.mark.parametrize(
    "field,value",
    [
        ("scope", "full"),
        ("config_sha256", "bad"),
        ("aggregate_channels", ["wrong"]),
        ("split_identity_sha256", "bad"),
    ],
)
def test_dev_identity_mismatch(tmp_path, field, value):
    manifest, expected = synthetic_manifest(tmp_path)
    manifest["scientific"][field] = value
    manifest["scientific_sha256"] = protocol.digest(manifest["scientific"])
    with pytest.raises(ValueError):
        protocol.validate_dev_manifest(manifest, expected)


def test_dev_validator_does_not_relax_pca_fit(tmp_path):
    from raregate.models.pca import validate_input_store

    manifest, expected = synthetic_manifest(tmp_path)
    protocol.validate_dev_manifest(manifest, expected)
    config = protocol.read(protocol.ROOT / "configs/models/pca_baseline.json")
    manifest["scientific"]["aggregate_channels"] = config["input"]["features"]
    manifest["scientific"]["config_sha256"] = config["input"][
        "preprocessing_config_sha256"
    ]
    with pytest.raises(ValueError, match="full-scope"):
        validate_input_store(manifest, config)


def test_prepare_public_one_batch_explicit_close(tmp_path):
    _, expected = synthetic_manifest(tmp_path)
    directory = tmp_path / "output"
    directory.mkdir()
    seen = []
    values = np.ones((1024, 8), dtype=np.float32)
    ids = np.arange(1024, dtype=np.int64) * 2

    class Store:
        manifest = protocol.read(tmp_path / expected["store"] / "manifest.json")

        def __init__(self, path):
            seen.append(("constructor", path))

        def iter_features(self, split, **options):
            seen.append((split, options))
            try:
                yield SimpleNamespace(event_features=values, event_ids=ids, labels=None)
                raise AssertionError("Second batch must never be requested")
            finally:
                seen.append("iterator_closed")

        def close(self):
            seen.append("store_closed")

    audit = {}
    record, times = core.prepare_input(
        tmp_path, {"input": expected}, directory, FakeGuard(), audit, factory=Store
    )
    assert record["unique_rows"] == record["population_presentations"] == 1024
    assert record["source_ids_bytes_sha256"] == core.array_hash(ids)
    assert seen[-2:] == ["iterator_closed", "store_closed"]
    assert seen[1] == (
        "train_background",
        {
            "batch_size": 1024,
            "dev_only": True,
            "allow_test": False,
            "include_labels": False,
        },
    )
    assert audit["custody"]["status"] == audit["population"]["status"] == "completed"
    assert "input_iterator_store_cleanup_seconds" in times
    assert not (directory / "ids.npy").exists()


def test_prepare_refuses_before_constructor(tmp_path):
    _, expected = synthetic_manifest(tmp_path)
    called = []
    with pytest.raises(ValueError):
        core.prepare_input(
            tmp_path,
            {"input": expected | {"population": "test_signal"}},
            tmp_path,
            FakeGuard(),
            {},
            factory=lambda path: called.append(path),
        )
    assert not called


@pytest.mark.parametrize(
    "shape,dtype",
    [((1023, 8), np.float32), ((1024, 9), np.float32), ((1024, 8), np.float64)],
)
def test_exact_input_rows_dtype(shape, dtype):
    with pytest.raises(ValueError):
        core.validate_features(np.zeros(shape, dtype=dtype))


def test_frozen_small_bytes_refused_before_any_store(tmp_path, spec):
    bad = copy.deepcopy(spec)
    bad["prompt"] = {"path": "prompt.md", "file_sha256": "a" * 64}
    (tmp_path / "prompt.md").write_text("synthetic changed prompt")
    with pytest.raises(ValueError, match="Prompt/brief"):
        protocol.verify_frozen(tmp_path, bad)


@pytest.mark.parametrize("flag,errno", [(1, None), (2, None), (None, 1)])
def test_guard_normal_warn_unknown_permitted(flag, errno):
    g = guard.Guard(
        time.monotonic() + 10,
        probe=lambda: sample(pressure_dispatch_flags=flag, pressure_errno=errno),
        notify=False,
    )
    g.check()
    assert g.error is None
    assert sum(g.pressure_counts.values()) == 1


def test_guard_equality_and_actual_failed_peak_latch():
    measurements = iter(
        [
            sample(peak_rss_bytes=1073741824, native_heap_reserved_bytes=536870912),
            sample(peak_rss_bytes=1073741825),
            sample(),
        ]
    )
    g = guard.Guard(
        time.monotonic() + 10, probe=lambda: next(measurements), notify=False
    )
    g.check()
    with pytest.raises(guard.GuardError, match="ceiling"):
        g.check()
    assert g.peak_rss == 1073741825
    before = g.checks
    with pytest.raises(guard.GuardError):
        g.check()
    assert g.checks == before


@pytest.mark.parametrize(
    "changes",
    [
        {"peak_rss_bytes": None},
        {"peak_rss_bytes": True},
        {"native_heap_reserved_bytes": 0},
        {"native_heap_in_use_bytes": 999999999},
        {"workspace_method": "unsupported"},
        {"pressure_dispatch_flags": 4, "pressure_errno": None},
        {"pressure_dispatch_flags": 3, "pressure_errno": None},
        {"pressure_dispatch_flags": True, "pressure_errno": None},
        {"pressure_method": "invented"},
        {"pressure_errno": None},
        {"native_heap_reserved_bytes": 536870913},
    ],
)
def test_guard_malformed_primary_pressure_and_critical_latch(changes):
    g = guard.Guard(
        time.monotonic() + 10, probe=lambda: sample(**changes), notify=False
    )
    with pytest.raises(guard.GuardError):
        g.check()
    assert g.error


def test_guard_deadline_and_owned_cleanup(tmp_path):
    g = guard.Guard(
        time.monotonic() + 2, directory=tmp_path, probe=sample, notify=False
    )
    with g:
        time.sleep(0.07)
    assert g.periodic_checks >= 1
    assert not g.report()["owned_thread_alive"]
    assert (tmp_path / "guards.jsonl").exists()
    expired = guard.Guard(0, probe=sample, notify=False)
    with pytest.raises(guard.GuardError):
        expired.check()


def test_guard_enter_failure_closes_journal(tmp_path):
    g = guard.Guard(
        time.monotonic() + 10,
        directory=tmp_path,
        probe=lambda: sample(pressure_dispatch_flags=4, pressure_errno=None),
        notify=False,
    )
    with pytest.raises(guard.GuardError):
        with g:
            pass
    assert g.journal is None
    assert not g.report()["owned_thread_alive"]


@pytest.mark.parametrize(
    "raw",
    [
        "bad",
        "Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 0.\nPages inactive: 0.\n",
    ],
)
def test_optional_context_low_malformed_not_veto(monkeypatch, raw):
    monkeypatch.setattr(guard.subprocess, "check_output", lambda *a, **k: raw)
    g = guard.Guard(time.monotonic() + 10, probe=sample, notify=False)
    g.context()
    assert not g.error
    assert g.contexts[0]["role"] == "optional_context_never_admission"


def test_optional_context_timeout_not_veto(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("context", 2)

    monkeypatch.setattr(guard.subprocess, "check_output", timeout)
    g = guard.Guard(time.monotonic() + 10, probe=sample, notify=False)
    g.context()
    assert g.contexts[0]["status"] == "unavailable" and not g.error


def test_sse_cast_before_subtraction_and_strict_tie():
    x = np.array([[16777216, 1, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
    y = np.array([[-1, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
    threshold = np.array([float(16777217**2 + 1), 0, 1, 1e20], dtype=np.float64)
    score, accepted = core.separated(x, y, threshold)
    assert score[0] == 16777217**2 + 1
    assert accepted.tolist() == [[False, True, True, False]]


def test_near_threshold_mismatch_even_within_numeric_tolerance():
    reference = np.array([1.0], dtype=np.float64)
    actual = np.array([1.0 + 1e-10], dtype=np.float64)
    thresholds = np.array([1, 2, 3, 4], dtype=np.float64)
    assert core.comparison(actual, reference, atol=1e-6, rtol=1e-5, name="near")[
        "passed"
    ]
    with pytest.raises(core.NumericalError, match="decision mismatch") as exc:
        core.verify_decisions(actual, reference, thresholds, "near")
    assert exc.value.evidence["mismatches_per_threshold"] == [1, 0, 0, 0]
    assert exc.value.evidence["first_failure"]["actual_score"] == actual[0]


@pytest.mark.parametrize("bad", [np.nan, np.inf, -1])
def test_nonfinite_negative_score_rejected(bad):
    with pytest.raises(core.NumericalError):
        core.decisions(np.array([bad], dtype=np.float64), np.zeros(4, dtype=np.float64))


def test_relative_denominator_and_failed_values():
    record = core.comparison(
        np.array([1e-13]), np.zeros(1), atol=1e-12, rtol=1e-12, name="zero"
    )
    assert record["max_relative_error"] == pytest.approx(0.1)
    with pytest.raises(core.NumericalError) as exc:
        core.comparison(
            np.array([2.0]), np.array([1.0]), atol=1e-12, rtol=1e-12, name="wrong"
        )
    assert exc.value.evidence["first_failure"]["actual"] == 2


def test_pca_kernel_order_and_same_batch_precomputation():
    values = np.linspace(-1, 1, 8192, dtype=np.float32).reshape(1024, 8)
    model = pca()
    for batch in (1, 8, 32, 128, 1024):
        windows = core.build_windows(model, values, batch)
        assert len(windows) == 1024 // batch
        for window in windows:
            np.testing.assert_array_equal(
                window["reconstruction"],
                model.reconstruct(
                    window["values"],
                    feature_names=core.PCAReconstruction.__module__
                    and protocol.load()["input"]["channels"],
                ),
            )


@pytest.mark.parametrize(
    "scope", ["reconstruction", "score_decision", "adapter_decision"]
)
def test_exact_schedule_scope_boundaries_and_timer_pairs(scope):
    seen = []
    values = np.zeros((1024, 8), dtype=np.float32)
    windows = []
    for start in range(0, 1024, 128):
        x = values[start : start + 128]

        def forward(start=start, x=x):
            seen.append(start)
            return x

        windows.append(
            {"start": start, "values": x, "reconstruction": x, "forward": forward}
        )

    class Model:
        def score(self, x, *, feature_names):
            seen.append("adapter")
            return np.zeros(len(x), dtype=np.float64)

    g, cell, raw = FakeGuard(), {}, io.StringIO()
    counter = iter(range(1000))
    durations = core.run_cell(
        Model(),
        np.ones(4, dtype=np.float64),
        [],
        windows,
        scope,
        128,
        g,
        cell,
        raw,
        timer=lambda: next(counter),
    )
    rows = [json.loads(line) for line in raw.getvalue().splitlines()]
    assert len(durations) == cell["timed_completed"] == 200
    assert cell["warmups_completed"] == 20
    assert g.checks == 441
    assert [r["start"] for r in rows[:20]] == [i % 8 * 128 for i in range(20)]
    assert [r["start"] for r in rows[20:]] == [i % 8 * 128 for i in range(200)]
    assert cell["latency_nanoseconds"]["count"] == 200
    if scope == "reconstruction":
        assert len(seen) == 220 and seen[20] == 0
    elif scope == "score_decision":
        assert not seen  # No forward/public model call in this scope.
    else:
        assert seen == ["adapter"] * 220


def test_numerical_every_window_grid_reference_and_hashes():
    values = np.zeros((1024, 8), dtype=np.float32)
    model = pca()
    windows = {b: core.build_windows(model, values, b) for b in (1, 8, 32, 128, 1024)}
    records, audit = [], {"numerical_forward_input_presentations": 0}
    result = core.verify_windows(
        model,
        values,
        np.ones(4, dtype=np.float64),
        protocol.load()["input"]["channels"],
        windows,
        FakeGuard(),
        records,
        audit,
    )
    assert len(records) == 35
    assert all(r["windows_verified"] == 1024 // r["batch"] for r in records)
    assert all(r["passed"] for r in records)
    assert result["sample_decision_counts"] == [0, 0, 0, 0]
    before = core.parameter_hash(model)
    model.mean[0] = 1
    assert core.parameter_hash(model) != before


def test_distribution_linear_quantile_and_defined_throughput():
    values = [10, 20, 30, 40]
    stats = protocol.distribution(values, 8)
    for q in (0.5, 0.95, 0.99):
        assert stats[f"p{int(100 * q)}"] == np.quantile(values, q, method="linear")
    assert stats["throughput_events_per_second"] == 8 / (25 / 1e9)
    assert stats["mean_amortized_nanoseconds_per_event"] == 25 / 8


def reservation_fixture(tmp_path, monkeypatch):
    (tmp_path / protocol.OUTPUT).parent.mkdir(parents=True)
    (tmp_path / protocol.ACCEPTANCE).parent.mkdir(parents=True)
    protocol.write(tmp_path / protocol.ACCEPTANCE, {"source_sha256": {}})
    monkeypatch.setattr(
        protocol, "code_context", lambda root: {"commit": None, "source_sha256": {}}
    )


def test_exclusive_one_winner_and_partial_refusal(tmp_path, monkeypatch, spec):
    reservation_fixture(tmp_path, monkeypatch)
    results = []
    owned = []

    def attempt():
        try:
            frozen_cpu.reserve(
                tmp_path,
                spec,
                {"source_sha256": {}},
                {},
                time.monotonic(),
                on_created=lambda: owned.append(True),
            )
            results.append("won")
        except FileExistsError:
            results.append("lost")

    threads = [threading.Thread(target=attempt) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert results.count("won") == len(owned) == 1
    assert results.count("lost") == 3
    assert (
        protocol.read(tmp_path / protocol.OUTPUT / "reservation.json")["status"]
        == "reserved_no_retry"
    )
    with pytest.raises(FileExistsError):
        frozen_cpu.reserve(tmp_path, spec, {"source_sha256": {}}, {}, time.monotonic())


def test_reservation_race_loser_cannot_overwrite_winner(tmp_path, monkeypatch, spec):
    reservation_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        frozen_cpu, "prerequisites", lambda root: (spec, {"source_sha256": {}}, {})
    )
    original = frozen_cpu.reserve

    def race(root, *args, **kwargs):
        directory = root / protocol.OUTPUT
        directory.mkdir()
        protocol.write(directory / "workflow.json", {"winner": True})
        return original(root, *args, **kwargs)

    monkeypatch.setattr(frozen_cpu, "reserve", race)
    result = frozen_cpu.run_campaign(tmp_path)
    assert not result["reserved_consumed"]
    assert protocol.read(tmp_path / protocol.OUTPUT / "workflow.json") == {
        "winner": True
    }


@pytest.mark.parametrize("state", ["partial", "completed", "foreign", "inflight"])
def test_existing_any_state_blocks_without_mutation(tmp_path, state):
    directory = tmp_path / protocol.OUTPUT
    directory.mkdir(parents=True)
    protocol.write(directory / "reservation.json", {"status": state})
    before = protocol.file_hash(directory / "reservation.json")
    result = frozen_cpu.run_campaign(tmp_path)
    assert (
        result["status"] == "blocked_before_reservation"
        and not result["reserved_consumed"]
    )
    assert protocol.file_hash(directory / "reservation.json") == before


def test_foreign_worker_cannot_create_records(tmp_path):
    directory = tmp_path / protocol.OUTPUT
    (directory / "prepare").mkdir(parents=True)
    protocol.write(
        directory / "prepare-reservation.json",
        {"phase": "prepare", "token": "correct", "parent_pid": os.getppid()},
    )
    with pytest.raises(ValueError, match="Foreign"):
        worker.phase_worker("prepare", "wrong", tmp_path)
    assert not list((directory / "prepare").iterdir())


def test_parent_deadline_kills_blocked_child_and_reaps(tmp_path, monkeypatch):
    monkeypatch.setattr(frozen_cpu, "parent_check", lambda **kwargs: 1)
    started = time.monotonic() - 57.8
    result = frozen_cpu.supervise(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        tmp_path / "log",
        root=tmp_path,
        environment={"PATH": os.defpath},
        started=started,
        campaign_deadline=time.monotonic() + 3,
    )
    assert result["parent_error"] and result["child_reaped"]
    assert result["elapsed_seconds_including_imports_cleanup"] <= 60


def test_child_crash_recorded_without_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(frozen_cpu, "parent_check", lambda **kwargs: 1)
    result = frozen_cpu.supervise(
        [sys.executable, "-c", "raise RuntimeError('synthetic crash')"],
        tmp_path / "log",
        root=tmp_path,
        environment={"PATH": os.defpath},
        started=time.monotonic(),
        campaign_deadline=time.monotonic() + 5,
    )
    assert result["returncode"] != 0 and result["child_reaped"]
    assert "synthetic crash" in (tmp_path / "log").read_text()


def test_truthful_partial_aggregation_and_all_worker_medians():
    cell = {
        "model": "pca-v1",
        "batch": 1,
        "scope": "reconstruction",
        "status": "completed",
        "timed_completed": 200,
        "warmups_completed": 20,
        "latency_nanoseconds": {"p50": 5},
    }
    partial = {
        "model": "pca-v1",
        "batch": 8,
        "scope": "score_decision",
        "status": "running",
        "timed_completed": 3,
        "warmups_completed": 20,
    }
    result = frozen_cpu.aggregate([{"phase": "PCA1", "cells": [cell, partial]}])
    assert result["missing_measured_cells"] == 89
    assert result["counts"]["timed_invocations_completed"] == 203
    assert not result["comparison_success"]
    full = frozen_cpu.aggregate(
        [
            {
                "phase": f"PCA{i}",
                "cells": [cell | {"latency_nanoseconds": {"p50": value}}],
            }
            for i, value in enumerate((1, 10, 100), 1)
        ]
    )
    assert (
        full["median_of_worker_medians"][0]["median_of_worker_medians_nanoseconds"]
        == 10
    )


def test_stdlib_controller_fresh_process():
    code = "import sys,json; from raregate.benchmarks import frozen_cpu; print(json.dumps([x for x in ('numpy','torch','sklearn','h5py') if x in sys.modules]))"
    output = subprocess.check_output([sys.executable, "-c", code], text=True)
    assert json.loads(output) == []


def test_thread_environment_refusal_before_import(spec, monkeypatch):
    monkeypatch.delenv("OMP_NUM_THREADS", raising=False)
    with pytest.raises(ValueError, match="before numerical imports"):
        worker.check_environment(spec)


def test_effective_thread_unsupported_blocks(monkeypatch):
    monkeypatch.setattr(
        core, "threadpool_info", lambda: [{"user_api": "blas", "num_threads": 2}]
    )
    with pytest.raises(ValueError, match="enforcement unsupported"):
        core.effective_threads()


@pytest.mark.parametrize(
    "mutation",
    ["source", "old_suite", "footprint", "thread_proof", "runtime", "quality"],
)
def test_current_acceptance_cannot_use_old_or_stale_evidence(
    tmp_path, monkeypatch, spec, mutation
):
    versions = {"python": "synthetic"}
    sources = {"synthetic.py": "a" * 64}
    monkeypatch.setattr(protocol, "runtime_versions", lambda: versions)
    monkeypatch.setattr(protocol, "source_map", lambda root: sources)
    accepted = {
        "schema_version": 1,
        "task": "0020",
        "protocol_canonical_sha256": protocol.PROTOCOL_HASH,
        "source_sha256": sources,
        "pytest_passed": 747,
        "pytest_cases": 747,
        "pytest_exit_code": 0,
        "portable_passed": 747,
        "runtime_versions": versions,
        "validation_evidence": [],
        "quality_checks": {
            "ruff_lint": "passed",
            "ruff_format": "passed",
            "pip_check": "passed",
            "cpu_smoke": "passed",
        },
        "footprint": {
            "status": "passed",
            "synthetic_only": True,
            "effective_threads_verified": True,
            "source_sha256": sources,
            "peak_rss_bytes": 32 * 2**20,
            "native_heap_reserved_bytes": 64 * 2**20,
        },
    }
    path = tmp_path / protocol.ACCEPTANCE
    path.parent.mkdir()
    protocol.write(path, accepted)
    protocol.verify_acceptance(tmp_path, spec)
    if mutation == "source":
        accepted["source_sha256"] = {}
    elif mutation == "old_suite":
        accepted["pytest_passed"] = accepted["pytest_cases"] = accepted[
            "portable_passed"
        ] = 670
    elif mutation == "footprint":
        accepted["footprint"]["peak_rss_bytes"] = 1073741825
    elif mutation == "thread_proof":
        accepted["footprint"]["effective_threads_verified"] = False
    elif mutation == "runtime":
        accepted["runtime_versions"] = {}
    else:
        accepted["quality_checks"]["cpu_smoke"] = "failed"
    protocol.write(path, accepted)
    with pytest.raises(ValueError):
        protocol.verify_acceptance(tmp_path, spec)


def test_canonical_artifact_loaders_called_and_ae_eval_preserved(tmp_path):
    model = core.CompactAutoencoder()
    artifact = model.artifact(provenance={}, training={})
    protocol.write(tmp_path / "ae.json", artifact)
    protocol.write(
        tmp_path / "result.json",
        {"scientific": {"thresholds": [{"threshold": x} for x in (1, 2, 3, 4)]}},
    )
    loaded, thresholds = core.load_model(
        tmp_path,
        {
            "name": "compact-autoencoder-v2",
            "model_path": "ae.json",
            "results_path": "result.json",
        },
    )
    assert not loaded.training and loaded.parameter_count == 155
    assert core.parameter_hash(model) == core.parameter_hash(loaded)
    assert thresholds.dtype == np.float64


def test_timing_reconstruction_nonfinite_retains_completed_call(tmp_path):
    x = np.zeros((1, 8), dtype=np.float32)
    windows = [
        {
            "start": 0,
            "values": x,
            "reconstruction": x,
            "forward": lambda: np.full((1, 8), np.nan),
        }
    ]
    cell, raw = {}, io.StringIO()
    with pytest.raises(core.NumericalError) as exc:
        core.run_cell(
            None,
            np.ones(4),
            [],
            windows,
            "reconstruction",
            1,
            FakeGuard(),
            cell,
            raw,
            warmups=0,
            measurements=2,
        )
    assert cell["timed_completed"] == 1 and cell["status"] == "running"
    assert any("nan" in value for value in exc.value.evidence["actual_values"])
    assert len(raw.getvalue().splitlines()) == 1


def test_recover_crash_partial_counts_and_torn_record(tmp_path):
    path = tmp_path / "timings.jsonl"
    rows = [
        {"batch": 8, "scope": "score_decision", "phase": "warmup", "elapsed_ns": None},
        {
            "batch": 8,
            "scope": "score_decision",
            "phase": "measurement",
            "elapsed_ns": 10,
        },
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows) + '{"torn":')
    partial = frozen_cpu.recover_partial(tmp_path, "PCA1")
    assert partial["possible_inflight_invocation"]
    assert partial["counts_are_flushed_lower_bounds"]
    assert (
        partial["cells"][0]["timed_completed"]
        == partial["cells"][0]["warmups_completed"]
        == 1
    )
    assert frozen_cpu.aggregate([partial])["missing_measured_cells"] == 90


def test_blocked_operation_watcher_latches_without_fake_success():
    values = iter([sample(), sample(pressure_dispatch_flags=4, pressure_errno=None)])
    g = guard.Guard(time.monotonic() + 5, probe=lambda: next(values), notify=False)
    with g:
        time.sleep(0.08)
        with pytest.raises(guard.GuardError, match="CRITICAL"):
            g.check()
    assert g.error and not g.report()["owned_thread_alive"]


class NativeFunction:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args):
        return self.function(*args)


def native_thread_library(*, setter_result=0, ignore_set=False, initial=0):
    state = {"mode": initial}

    def setter(mode):
        if setter_result == 0 and not ignore_set:
            state["mode"] = mode
        return setter_result

    return SimpleNamespace(
        BLASSetThreading=NativeFunction(setter),
        BLASGetThreading=NativeFunction(lambda: state["mode"]),
    ), state


def test_accelerate_public_set_get_and_restore(monkeypatch):
    monkeypatch.setattr(accelerate_threads.platform, "system", lambda: "Darwin")
    library, state = native_thread_library()
    control = accelerate_threads.AccelerateThreads(library=library)
    assert state["mode"] == control.report()["queried_mode"] == 1
    assert control.report()["setter_returncode"] == 0
    control.restore()
    assert state["mode"] == 0


@pytest.mark.parametrize(
    "options", [{"setter_result": -1}, {"ignore_set": True}, {"initial": 9}]
)
def test_accelerate_unsupported_or_unverified_mode_blocks(monkeypatch, options):
    monkeypatch.setattr(accelerate_threads.platform, "system", lambda: "Darwin")
    library, _ = native_thread_library(**options)
    with pytest.raises(ValueError):
        accelerate_threads.AccelerateThreads(library=library)


def test_accelerate_owner_thread_and_post_timing_mode_recheck(monkeypatch):
    monkeypatch.setattr(accelerate_threads.platform, "system", lambda: "Darwin")
    library, state = native_thread_library()
    control = accelerate_threads.AccelerateThreads(library=library)
    errors = []

    def other_thread():
        try:
            control.verify()
        except ValueError as exc:
            errors.append(str(exc))

    thread = threading.Thread(target=other_thread)
    thread.start()
    thread.join()
    assert errors
    state["mode"] = 0
    with pytest.raises(ValueError):
        control.verify()


def test_accelerate_symbols_unavailable_blocks(monkeypatch):
    monkeypatch.setattr(accelerate_threads.platform, "system", lambda: "Darwin")
    with pytest.raises(ValueError, match="unavailable"):
        accelerate_threads.AccelerateThreads(library=SimpleNamespace())
