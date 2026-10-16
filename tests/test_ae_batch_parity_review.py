"""Self-contained numerical-review coverage; no operational artifacts or data."""

import copy
import subprocess
import sys
import threading
import time

import numpy as np
import pytest
import torch
from test_frozen_cpu_benchmark import FakeGuard, sample

from raregate.benchmarks import ae_parity_numerics as n
from raregate.benchmarks import ae_parity_protocol as q
from raregate.benchmarks import ae_parity_review as review
from raregate.benchmarks import core
from raregate.benchmarks import protocol as p
from raregate.data.inspection import AGGREGATE_NAMES
from raregate.models.autoencoder import CompactAutoencoder


@pytest.mark.parametrize(
    "change",
    [
        {"extra": 1},
        {"batch_grid": [1]},
        {"performance_timing_authorized": True},
        {"output": "other"},
        {"input": {"path": "data/full"}},
        {"optimizer_updates": 1},
        {"task": "0020"},
        {"schema_version": True},
        {"schema_version": 1.0},
        {"model": {"thresholds": [0]}},
    ],
)
def test_exact_review_protocol_no_overrides(tmp_path, change):
    spec = q.load()
    path = tmp_path / q.CONFIG
    path.parent.mkdir(parents=True)
    p.write(path, spec | change)
    with pytest.raises(ValueError, match="Unsupported"):
        q.load(tmp_path)


def test_synthetic_recipes_are_fixed_separate_and_bounded():
    first, second = n.families(), n.families()
    assert list(first) == ["constants", "powers", "uniform", "normal"]
    for name, values in first.items():
        core.validate_features(values)
        assert np.max(np.abs(values)) <= 8
        assert core.array_hash(values) == core.array_hash(second[name])
    assert np.array_equal(first["constants"][:, 0], np.repeat([0, 1, -1, 8], 256))
    assert set(np.unique(np.abs(first["powers"]))) == {2.0**i for i in range(-3, 4)}


def test_original_failure_dtype_and_comparator_agree_without_edit():
    actual = np.array([[-0.09302544593811035]], np.float32)
    reference = np.array([[-0.09302345663309097]], np.float32)
    result = n.comparison(actual, reference)
    assert not result["passed"] and result["violations"] == 1
    assert result["examples"][0]["absolute_error"] == 1.989305019378662e-6
    assert result["executed_bound_dtype"] == "float32"
    with pytest.raises(core.NumericalError) as raised:
        core.comparison(actual, reference, atol=1e-6, rtol=1e-5, name="original")
    assert raised.value.evidence["max_absolute_error"] == result["max_absolute_error"]


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_all_violations_locations_no_prefix_stop(dtype):
    reference = np.zeros((1024, 8), dtype=dtype)
    actual = reference.copy()
    actual[7, 5] = 2e-6
    actual[1023, 7] = 3e-6
    result = n.comparison(actual, reference)
    assert result["violation_locations"] == [[7, 5], [1023, 7]]
    assert result["violations"] == 2 and not result["passed"]
    assert result["max_absolute_error"] == float(actual[1023, 7])


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_stops_unrelated_to_tolerance(bad):
    with pytest.raises(ValueError, match="Nonfinite"):
        n.comparison(np.array([bad]), np.array([0.0]))


def test_shape_mismatch_not_ignored():
    with pytest.raises(ValueError, match="shape"):
        n.comparison(np.zeros(2), np.zeros(3))


def test_strict_ties_and_near_threshold_mismatches():
    thresholds = np.array([1, 2, 3, 4], dtype=np.float64)
    reference = np.array([1, 2, 3, 4], dtype=np.float64)
    actual = np.nextafter(reference, np.inf)
    result = n.decision_review(actual, reference, thresholds)
    assert result["mismatches_per_threshold"] == [1, 1, 1, 1]
    assert result["minimum_reference_absolute_margins"] == [0, 0, 0, 0]
    assert not result["passed"]


def test_sse_cast_before_subtraction():
    x = np.array([[1e8, 3, 0, 0, 0, 0, 0, 0]], np.float32)
    y = np.array([[-1, 1, 0, 0, 0, 0, 0, 0]], np.float32)
    score, _ = core.separated(x, y, np.array([1, 2, 3, 4], np.float64))
    assert score.dtype == np.float64
    assert score[0] == (1e8 + 1) ** 2 + 4
    assert score[0] != float(np.sum((x - y) ** 2))


def synthetic_model():
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(1729)
        return CompactAutoencoder().eval()


def test_trace_retains_module_state_and_removes_hooks_even_on_error():
    model = synthetic_model()
    before = core.parameter_hash(model)
    x = np.zeros((8, 8), np.float32)
    result, trace = n.traced_forward(model, x, {"fp32_forward_presentations": 0})
    assert tuple(trace) == n.LAYERS
    assert np.array_equal(result, core.reconstruct(model, x, None))
    assert core.parameter_hash(model) == before
    assert not any(m._forward_hooks for m in model.modules())
    with pytest.raises(ValueError):
        n.traced_forward(
            model,
            np.full((1, 8), np.nan, np.float32),
            {"fp32_forward_presentations": 0},
        )
    assert not any(m._forward_hooks for m in model.modules())


def test_full_grid_coverage_bookkeeping_repeatability_and_hashes():
    model = synthetic_model()
    values = n.families()["uniform"]
    thresholds = np.array([1, 2, 3, 4], np.float64)
    result = {
        "audit": {"fp32_forward_presentations": 0, "fp64_diagnostic_presentations": 0}
    }
    n.analyze(model, values, thresholds, AGGREGATE_NAMES, FakeGuard(), result)
    assert result["status"] == "completed"
    assert result["hashes_before"] == result["hashes_after"]
    assert result["reference_hashes_before"] == result["reference_hashes_after"]
    assert result["audit"] == {
        "fp32_forward_presentations": 19456,
        "fp64_diagnostic_presentations": 1024,
    }
    for cell in result["windows"]:
        assert (
            cell["rows_completed"] == 1024
            and cell["windows_completed"] == 1024 // cell["batch"]
        )
        assert cell["same_shape_reconstruction"]["exact_byte_equality"]
        assert cell["same_shape_score"]["exact_byte_equality"]
        assert cell["repeated_score"]["exact_byte_equality"]


def test_diagnostic64_keeps_exact_parameters_and_relu_lipschitz():
    model = synthetic_model()
    before = core.parameter_hash(model)
    double = copy.deepcopy(model).double()
    values = np.zeros((1024, 8), np.float64)
    output, trace = n.traced_forward(
        double, values, {"fp64_diagnostic_presentations": 0}, diagnostic64=True
    )
    bounds, layers = n.affine_roundoff_envelope(model, trace, values.astype(np.float32))
    assert np.isfinite(output).all() and (bounds >= 0).all()
    assert list(layers) == list(n.LAYERS)
    assert layers["encoder.0"] == layers["encoder.1"]
    assert core.parameter_hash(model) == before
    for left, right in zip(model.parameters(), double.parameters(), strict=True):
        assert torch.equal(left.double(), right)


@pytest.mark.parametrize(
    "state", ["reserved", "partial", "inflight", "completed", "foreign"]
)
def test_consumed_fixed_output_refuses_every_state(tmp_path, monkeypatch, state):
    directory = tmp_path / q.OUTPUT
    directory.mkdir(parents=True)
    (directory / "state").write_text(state)
    with pytest.raises(FileExistsError):
        review.reserve(tmp_path, q.load(), {}, time.monotonic())
    assert (directory / "state").read_text() == state


def test_concurrent_reservation_has_one_winner(tmp_path, monkeypatch):
    (tmp_path / q.OUTPUT).parent.mkdir(parents=True)
    monkeypatch.setattr(p, "source_map", lambda root: {})
    monkeypatch.setattr(p, "code_context", lambda root: {})
    monkeypatch.setattr(p, "file_hash", lambda path: "a" * 64)
    acceptance = tmp_path / q.ACCEPTANCE
    acceptance.parent.mkdir()
    acceptance.write_text("{}")
    wins = []

    def attempt():
        try:
            review.reserve(tmp_path, q.load(), {"source_sha256": {}}, time.monotonic())
            wins.append(True)
        except FileExistsError:
            wins.append(False)

    threads = [threading.Thread(target=attempt) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert wins.count(True) == 1 and wins.count(False) == 3


def test_symlink_output_refused(tmp_path):
    directory = tmp_path / q.OUTPUT
    directory.parent.mkdir(parents=True)
    other = tmp_path / "other"
    other.mkdir()
    directory.symlink_to(other)
    with pytest.raises(ValueError, match="Symlink"):
        review.reserve(tmp_path, q.load(), {}, time.monotonic())


@pytest.mark.parametrize(
    "field,value",
    [
        ("peak_rss_bytes", 1073741825),
        ("native_heap_reserved_bytes", 536870913),
        ("pressure_dispatch_flags", 4),
        ("pressure_dispatch_flags", 3),
        ("workspace_method", "bad"),
        ("peak_rss_bytes", None),
    ],
)
def test_reused_guard_fails_closed_and_latches(field, value):
    guard = review.Guard(
        time.monotonic() + 10, probe=lambda: sample(**{field: value}), notify=False
    )
    with pytest.raises(RuntimeError):
        guard.check()
    assert guard.error
    with pytest.raises(RuntimeError):
        guard.check()
    if field == "peak_rss_bytes" and value:
        assert guard.peak_rss == value


@pytest.mark.parametrize("pressure,errno", [(1, None), (2, None), (None, 1)])
def test_reused_caps_equal_and_pressure_advisory(pressure, errno):
    guard = review.Guard(
        time.monotonic() + 10,
        probe=lambda: sample(
            peak_rss_bytes=1073741824,
            native_heap_reserved_bytes=536870912,
            pressure_dispatch_flags=pressure,
            pressure_errno=errno,
        ),
        notify=False,
    )
    guard.check()
    assert guard.error is None and sum(guard.pressure_counts.values()) == 1


def test_unrelated_operation_exception_is_not_numerical_finding():
    model = synthetic_model()

    def fail(*_args, **_kwargs):
        raise RuntimeError("synthetic unrelated error")

    model.forward = fail
    with pytest.raises(RuntimeError, match="unrelated"):
        n.traced_forward(
            model, np.zeros((1, 8), np.float32), {"fp32_forward_presentations": 0}
        )
    assert not any(m._forward_hooks for m in model.modules())


def test_review_controller_has_no_numeric_imports_in_fresh_process(tmp_path):
    code = 'import sys; import raregate.benchmarks.ae_parity_review; assert not any(k in sys.modules for k in ("numpy","torch","sklearn","h5py"))'
    child = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=10
    )
    assert child.returncode == 0, child.stderr


def test_historical_source_mismatch_refused_before_array_open(tmp_path):
    spec = q.load()
    path = tmp_path / spec["prompt"]["path"]
    path.parent.mkdir(parents=True)
    path.write_text("altered")
    with pytest.raises(ValueError, match="binding changed"):
        q.verify_metadata(tmp_path, spec)


def test_owned_guard_cleanup():
    with review.Guard(time.monotonic() + 10, probe=sample, notify=False) as guard:
        guard.check()
    assert not guard.report()["owned_thread_alive"]


def prepared_fixture(tmp_path):
    spec = q.load()
    values = n.families()["normal"]
    path = tmp_path / spec["input"]["path"]
    path.parent.mkdir(parents=True)
    np.save(path, values, allow_pickle=False)
    spec["input"].update(
        file_sha256=p.file_hash(path),
        file_size_bytes=path.stat().st_size,
        array_bytes_sha256=core.array_hash(values),
    )
    audit = {
        "prepared_numerical_load_attempts": 0,
        "prepared_numerical_loads_completed": 0,
        "unique_reused_real_rows": 0,
    }
    return spec, values, path, audit


def test_only_one_bounded_nonpickle_array_open(tmp_path, monkeypatch):
    spec, values, path, audit = prepared_fixture(tmp_path)
    original = n.np.load
    calls = []

    def tracked(path, **kwargs):
        calls.append((path, kwargs))
        return original(path, **kwargs)

    monkeypatch.setattr(n.np, "load", tracked)
    loaded = n.load_prepared(tmp_path, spec, audit)
    assert np.array_equal(loaded, values)
    assert calls == [(path, {"allow_pickle": False})]
    assert audit == {
        "prepared_numerical_load_attempts": 1,
        "prepared_numerical_loads_completed": 1,
        "unique_reused_real_rows": 1024,
    }
    with pytest.raises(ValueError, match="one fixed"):
        n.load_prepared(tmp_path, spec, audit)
    assert len(calls) == 1


@pytest.mark.parametrize(
    "change",
    [
        {"path": "data/processed/full/input.npy"},
        {"path": "data/test_signal/input.npy"},
        {"shape": [1023, 8]},
        {"dtype": "float64"},
        {"loads": 2},
        {"allow_pickle": True},
        {"file_sha256": "0" * 64},
        {"file_size_bytes": 1},
    ],
)
def test_array_refusal_precedes_numpy_open(tmp_path, monkeypatch, change):
    spec, _, _, audit = prepared_fixture(tmp_path)
    spec["input"].update(change)
    monkeypatch.setattr(
        n.np, "load", lambda *_a, **_k: pytest.fail("Forbidden numerical open")
    )
    with pytest.raises(ValueError):
        n.load_prepared(tmp_path, spec, audit)
    assert audit["prepared_numerical_load_attempts"] == 0


def receipt_fixture(tmp_path):
    directory = tmp_path
    grant = {"mode": "real", "source_sha256": {"synthetic": "a"}}
    p.write(directory / "reservation.json", grant)
    cells = [
        {
            "batch": b,
            "status": "completed",
            "rows_completed": 1024,
            "windows_completed": 1024 // b,
        }
        for b in (1, 8, 32, 128, 1024)
    ]
    receipt = {
        "task": "0021",
        "mode": "real",
        "source_sha256": grant["source_sha256"],
        "protocol_canonical_sha256": q.PROTOCOL_HASH,
        "reservation_file_sha256": p.file_hash(directory / "reservation.json"),
        "test_background_model_access": False,
        "test_signal_model_access": False,
        "audit": {"optimizer_updates": 0},
        "status": "completed",
        "resources": {"latched_error": None, "owned_thread_alive": False},
        "families": [
            {
                "name": "prepared_real",
                "status": "completed",
                "windows": cells,
                "hashes_before": {"a": "x"},
                "hashes_after": {"a": "x"},
                "reference_hashes_before": {"b": "x"},
                "reference_hashes_after": {"b": "x"},
                "historical_v1_comparison_passed": False,
            }
        ],
    }
    dispatch = {
        "child_reaped": True,
        "deadline_passed": True,
        "parent_error": None,
        "returncode": 0,
    }
    p.write(directory / "receipt.json", receipt)
    return grant, receipt, dispatch


def test_completed_diagnostic_preserves_false_old_acceptance(tmp_path):
    grant, _, dispatch = receipt_fixture(tmp_path)
    receipt = review.validate_receipt(tmp_path, grant, dispatch)
    assert receipt["families"][0]["historical_v1_comparison_passed"] is False


@pytest.mark.parametrize(
    "change",
    [
        "rows",
        "windows",
        "hash",
        "reference",
        "missing_batch",
        "failed",
        "reap",
        "deadline",
        "crash",
        "guard",
    ],
)
def test_incomplete_summary_is_not_success(tmp_path, change):
    grant, receipt, dispatch = receipt_fixture(tmp_path)
    family = receipt["families"][0]
    if change == "rows":
        family["windows"][0]["rows_completed"] = 7
    elif change == "windows":
        family["windows"][0]["windows_completed"] = 7
    elif change == "hash":
        family["hashes_after"]["a"] = "altered"
    elif change == "reference":
        family["reference_hashes_after"]["b"] = "altered"
    elif change == "missing_batch":
        family["windows"].pop()
    elif change == "failed":
        receipt["status"] = "failed"
    elif change == "reap":
        dispatch["child_reaped"] = False
    elif change == "deadline":
        dispatch["deadline_passed"] = False
    elif change == "crash":
        dispatch["returncode"] = -9
    elif change == "guard":
        receipt["resources"]["latched_error"] = "critical"
    p.write(tmp_path / "receipt.json", receipt)
    with pytest.raises(ValueError):
        review.validate_receipt(tmp_path, grant, dispatch)


def test_layer_sign_change_metric_uses_affine_and_relu_boundaries():
    model = synthetic_model()
    values = n.families()["powers"]
    _, trace = n.traced_forward(model, values, {"fp32_forward_presentations": 0})
    assert (trace["encoder.0"] < 0).any()
    assert (trace["encoder.1"] >= 0).all()
    assert np.array_equal(trace["encoder.1"], np.maximum(trace["encoder.0"], 0))
    assert np.array_equal(trace["decoder.1"], np.maximum(trace["decoder.0"], 0))
