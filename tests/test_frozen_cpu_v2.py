"""Independent rational bounds, synthetic gates, scope and finite v2 control."""

import copy
import io
import struct
import subprocess
import sys
import time
from fractions import Fraction as F

import numpy as np
import pytest
import torch
from test_frozen_cpu_benchmark import FakeGuard, sample

from raregate.benchmarks import arithmetic_cpu_v2 as a
from raregate.benchmarks import core
from raregate.benchmarks import frozen_cpu_v2 as controller
from raregate.benchmarks import frozen_cpu_v2_numerics as n
from raregate.benchmarks import frozen_cpu_v2_protocol as q
from raregate.benchmarks import protocol as p
from raregate.data.inspection import AGGREGATE_NAMES
from raregate.models.autoencoder import CompactAutoencoder

PAIRS = [
    (0.0, 0.0),
    (0.0, 1.0),
    (1.0, 1.0),
    (0.1, 0.2),
    (2.0**-40, 2.0**40),
    (np.nextafter(1.0, 2.0), np.nextafter(1.0, 0.0)),
    (2.0**-100, 2.0**-100),
]


@pytest.mark.parametrize("x,y", PAIRS)
@pytest.mark.parametrize("operation", ["add", "mul", "div"])
def test_each_primitive_encloses_exact_rational(x, y, operation):
    if operation == "div" and y == 0:
        with pytest.raises(a.ArithmeticFailure):
            a.div_up(x, y)
        return
    fn = {"add": a.add_up, "mul": a.mul_up, "div": a.div_up}[operation]
    exact = {
        "add": lambda: F(float(x)) + F(float(y)),
        "mul": lambda: F(float(x)) * F(float(y)),
        "div": lambda: F(float(x)) / F(float(y)),
    }[operation]()
    upper = fn(x, y)
    assert F(float(upper)) >= exact
    if exact == 0:
        assert upper == 0


@pytest.mark.parametrize("n", [3, 6, 8, 16])
@pytest.mark.parametrize("u", [a.U32, a.U64])
def test_gamma_is_upward_exact_fraction(n, u):
    m = 2 * n + 2 if n < 16 else 32
    exact = F(m) * F(u) / (1 - F(m) * F(u))
    assert F(float(a.gamma(m, u))) >= exact


def test_complete_signed_magnitude_dot_is_outward_not_final_blas_ulp():
    x = np.array([[1.0, 2.0**-53, 2.0**-54, 2.0**-55, 0.1, 0.2, 0.3, 0.4]])
    w = np.array([[1.0, 1.0, 1.0, 1.0, -0.2, 0.3, -0.4, 0.5]])
    expected = sum(abs(F(float(x[0, i])) * F(float(w[0, i]))) for i in range(8))
    upper = a.dot_up(np.abs(x), np.abs(w))[0, 0]
    assert F(float(upper)) >= expected
    assert a.sum_up(np.abs(x))[0] >= sum(F(float(v)) for v in x[0])


def test_recurrence_against_independent_exact_rational_fixture():
    x = np.array([[0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8]])
    e = np.full_like(x, 2.0**-30)
    w = np.array(
        [
            [0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8],
            [-1.0, 0.5, -0.25, 0.125, -0.0625, 0.03125, -0.015625, 0.0078125],
        ]
    )
    b = np.array([0.2, -0.3])
    m = 18
    g32 = F(m) * F(a.U32) / (1 - F(m) * F(a.U32))
    g64 = F(m) * F(a.U64) / (1 - F(m) * F(a.U64))
    bound = a.affine_envelope(e, x, w, b)
    for j in range(2):
        magnitude = sum(
            abs(F(float(w[j, k])) * F(float(x[0, k]))) for k in range(8)
        ) + abs(F(float(b[j])))
        propagated = sum(abs(F(float(w[j, k]))) * F(float(e[0, k])) for k in range(8))
        expected = (1 + g32) * propagated + (g32 + g64) * magnitude
        assert F(float(bound[0, j])) >= expected


def test_local_bias_and_rounded_fp64_reference_are_included():
    x = np.ones((2, 8), np.float32)
    w = np.zeros((3, 8))
    b = np.array([1.0, -2.0, 0.0])
    bound = a.local_affine_bound(x, w, b)
    assert bound[0, 0] > 0 and bound[0, 1] > bound[0, 0] and bound[0, 2] == 0
    g32 = a.gamma(18, a.U32)
    g64 = a.gamma(18, a.U64)
    assert np.all(bound >= np.abs(b) * (g32 + g64))
    with pytest.raises(a.ArithmeticFailure):
        a.assert_bound(
            np.array([[1.001, -2.0, 0.0]]), b[None, :], bound[:1], "corrupted_local"
        )


def test_relu_lipschitz_allows_sign_change_near_zero():
    left = np.array([[-(2.0**-30), 2.0**-30]])
    right = -left
    envelope = a.abs_difference_up(left, right)
    a.assert_bound(np.maximum(left, 0), np.maximum(right, 0), envelope, "ReLU")
    assert np.count_nonzero((left > 0) != (right > 0)) == 2


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf, 2.0**-41, 2.0**41])
def test_supported_band_is_checked_no_clipping(value):
    with pytest.raises(a.ArithmeticFailure):
        a.supported(np.array([value]))


def test_checked_band_equality_and_exact_zero():
    a.supported(np.array([0.0, -a.LOW, a.LOW, a.HIGH, -a.HIGH]))
    assert a.mul_up(0, 1) == a.add_up(0, 0) == 0


@pytest.mark.parametrize(
    "operation",
    [
        lambda: a.mul_up(2.0**-700, 2.0**-700),
        lambda: a.mul_up(np.finfo(float).tiny, 0.5),
        lambda: a.add_up(np.finfo(float).max, np.finfo(float).max),
        lambda: a.div_up(1.0, 0.0),
        lambda: a.gamma(True, a.U32),
        lambda: a.gamma(33, a.U64),
        lambda: a.dot_up(np.ones((2, 3)), np.ones((1, 8))),
        lambda: a.assert_bound(np.zeros(2), np.zeros(2), np.zeros(3), "shape"),
    ],
)
def test_nonfinite_overflow_underflow_unsupported_conditions_fail(operation):
    with pytest.raises(a.ArithmeticFailure):
        operation()


def test_SSE_bound_against_rational_exact_residual_and_both_scores():
    x = np.array([[0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8]], np.float32)
    ref = x + np.float32(0.125)
    actual = ref.copy()
    actual[0, 0] += np.float32(2.0**-20)
    d = a.abs_difference_up(actual, ref)
    s, _ = core.separated(x, actual, np.array([1.0, 2.0, 3.0, 4.0]))
    sr, _ = core.separated(x, ref, np.array([1.0, 2.0, 3.0, 4.0]))
    bound, qval, rounding = a.sse_difference_bound(x, ref, d, s, sr)
    exactQ = sum(
        2 * abs(F(float(x[0, k])) - F(float(ref[0, k]))) * F(float(d[0, k]))
        + F(float(d[0, k])) ** 2
        for k in range(8)
    )
    assert F(float(qval[0])) >= exactQ
    g = F(32) * F(a.U64) / (1 - F(32) * F(a.U64))
    exactRound = g / (1 - g) * (F(float(s[0])) + F(float(sr[0])))
    assert F(float(rounding[0])) >= exactRound
    assert F(float(bound[0])) >= exactQ + exactRound
    assert rounding[0] > 0
    a.assert_bound(s, sr, bound, "score")


def test_zero_score_has_zero_scale_allowance():
    x = np.zeros((1, 8), np.float32)
    bound, qval, evaluation = a.sse_difference_bound(
        x, x, np.zeros_like(x, np.float64), np.zeros(1), np.zeros(1)
    )
    assert bound[0] == qval[0] == evaluation[0] == 0


def test_accepted_error_does_not_excuse_strict_threshold_mismatch():
    ref = np.array([1.0], np.float64)
    actual = np.nextafter(ref, np.inf)
    a.assert_bound(actual, ref, np.array([1e-6]), "numeric_pass")
    with pytest.raises(core.NumericalError):
        core.verify_decisions(actual, ref, np.array([1.0, 2.0, 3.0, 4.0]), "strict")
    assert not core.decisions(ref, np.array([1.0, 2.0, 3.0, 4.0]))[0, 0]


def synthetic_model():
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(1729)
        return CompactAutoencoder().eval()


def test_all_grid_local_checks_repeatability_no_hooks_and_hash_preservation():
    model = synthetic_model()
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(1729)
        values = torch.rand(1024, 8).numpy()
    thresholds = np.array([1.0, 2.0, 3.0, 4.0], np.float64)
    before = core.parameter_hash(model)
    windows = {b: core.build_windows(model, values, b) for b in [1, 8, 32, 128, 1024]}
    audit = {
        "numerical_forward_input_presentations": 5120,
        "diagnostic_fp64_full_forward_presentations": 0,
        "diagnostic_fp64_local_affine_row_presentations": 0,
    }
    records = []
    first = n.verify_ae(
        model, values, thresholds, AGGREGATE_NAMES, windows, FakeGuard(), records, audit
    )
    assert first["local_affine_scalar_checks"] == 6 * 1024 * 23
    assert audit == {
        "numerical_forward_input_presentations": 22528,
        "diagnostic_fp64_full_forward_presentations": 1024,
        "diagnostic_fp64_local_affine_row_presentations": 24576,
    }
    assert all(c["passed"] and c["violations"] == 0 for c in records)
    assert first["mismatches_per_threshold"] == [0] * 4
    assert core.parameter_hash(model) == before
    assert not any(m._forward_hooks for m in model.modules())
    post = n.verify_ae(
        model, values, thresholds, AGGREGATE_NAMES, windows, FakeGuard(), [], audit
    )
    assert (
        first["reference_reconstruction_sha256"]
        == post["reference_reconstruction_sha256"]
    )
    assert first["envelope_sha256"] == post["envelope_sha256"]


def test_reference_or_repetition_corruption_fails_even_with_loose_envelope():
    with pytest.raises(a.ArithmeticFailure):
        n.exact(np.zeros((1, 8), np.float32), np.ones((1, 8), np.float32), "reference")


def test_hooks_removed_after_nonfinite_trace_failure():
    model = synthetic_model()

    def fail(*_a, **_k):
        raise RuntimeError("injected failure")

    model.encoder[2].forward = fail
    with pytest.raises(RuntimeError):
        a.trace(
            model,
            np.zeros((1, 8), np.float32),
            {"numerical_forward_input_presentations": 0},
        )
    assert not any(m._forward_hooks for m in model.modules())


@pytest.mark.parametrize(
    "change",
    [
        {"extra": 1},
        {"task": "0020"},
        {"batch_grid": [1]},
        {"numerical": {"observed_error_multiplier": 2}},
        {"output": "other"},
        {"warmups": 21},
        {"input": {"path": "data/processed/full/input.npy"}},
        {"schema_version": True},
        {"runtime": {"device": "mps"}},
        {"optimizer_updates": 1},
    ],
)
def test_protocol_exact_no_unsafe_overrides(tmp_path, change):
    path = tmp_path / q.CONFIG
    path.parent.mkdir(parents=True)
    p.write(path, q.load() | change)
    with pytest.raises(ValueError):
        q.load(tmp_path)


@pytest.mark.parametrize(
    "descr,shape,fortran",
    [
        ("<f8", (1024, 8), False),
        ("|O", (1024, 8), False),
        ("<f4", (1023, 8), False),
        ("<f4", (1024, 8), True),
        ("<f4", (1024, 8), 0),
        ("<f4", (1024.0, 8), False),
    ],
)
def test_header_refusal_without_numpy_open(tmp_path, descr, shape, fortran):
    path = tmp_path / "bad.npy"
    text = (
        repr({"descr": descr, "fortran_order": fortran, "shape": shape}).encode()
        + b"\n"
    )
    path.write_bytes(
        b"\x93NUMPY\x01\x00" + struct.pack("<H", len(text)) + text + b"\0" * 32768
    )
    with pytest.raises(ValueError):
        q.header(path)


def input_fixture(tmp_path):
    spec = q.load()
    path = tmp_path / spec["input"]["path"]
    path.parent.mkdir(parents=True)
    x = np.zeros((1024, 8), np.float32)
    np.save(path, x, allow_pickle=False)
    spec["input"].update(
        file_sha256=p.file_hash(path), array_bytes_sha256=core.array_hash(x)
    )
    return spec, path


def test_input_one_original_read_separate_from_population_counts(tmp_path, monkeypatch):
    spec, path = input_fixture(tmp_path)
    audit = {}
    calls = []
    original = np.load

    def load(path, **kw):
        calls.append((path, kw))
        return original(path, **kw)

    monkeypatch.setattr(n.np, "load", load)
    n.load_array(tmp_path, spec, audit)
    assert calls == [(path, {"allow_pickle": False})]
    assert audit["original_array_reads_completed"] == 1 and audit["rows_loaded"] == 1024
    with pytest.raises(ValueError):
        n.load_array(tmp_path, spec, audit)
    assert len(calls) == 1


@pytest.mark.parametrize(
    "change",
    [
        {"path": "data/processed/dev/input.npy"},
        {"path": "test_signal.npy"},
        {"file_sha256": "0" * 64},
    ],
)
def test_scope_identity_refusal_before_numpy_open(tmp_path, monkeypatch, change):
    spec, _ = input_fixture(tmp_path)
    spec["input"].update(change)
    monkeypatch.setattr(n.np, "load", lambda *_a, **_k: pytest.fail("Forbidden open"))
    with pytest.raises(ValueError):
        n.load_array(tmp_path, spec, {})


def test_stdlib_controller_fresh_import_has_no_numeric_frameworks():
    script = 'import sys;import raregate.benchmarks.frozen_cpu_v2;assert not any(n in sys.modules for n in ("numpy","torch","sklearn","h5py"))'
    child = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=10
    )
    assert child.returncode == 0, child.stderr


@pytest.mark.parametrize(
    "state", ["reserved", "partial", "inflight", "completed", "foreign"]
)
def test_all_existing_output_states_refuse_without_reset(tmp_path, state):
    path = tmp_path / q.OUTPUT
    path.mkdir(parents=True)
    (path / "state").write_text(state)
    with pytest.raises(FileExistsError):
        controller.reserve(tmp_path, q.load(), {}, {}, time.monotonic())
    assert (path / "state").read_text() == state


def test_exclusive_reservation_concurrency_and_ownership(tmp_path, monkeypatch):
    import threading

    (tmp_path / q.OUTPUT).parent.mkdir(parents=True)
    accept = tmp_path / q.ACCEPTANCE
    accept.parent.mkdir()
    accept.write_text("{}")
    monkeypatch.setattr(p, "source_map", lambda root: {})
    monkeypatch.setattr(p, "code_context", lambda root: {})
    winners = []

    def attempt():
        try:
            controller.reserve(
                tmp_path,
                q.load(),
                {},
                {"source_sha256": {}},
                time.monotonic(),
                on_created=lambda: winners.append("owned"),
            )
        except FileExistsError:
            pass

    threads = [threading.Thread(target=attempt) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert winners == ["owned"]


def test_unchanged_timing_kernel_schedule_and_policy_outside_timer():
    model = synthetic_model()
    x = np.ones((1024, 8), np.float32)
    windows = core.build_windows(model, x, 8)
    audit = []

    class Timer:
        def __call__(self):
            audit.append("timer")
            return len(audit)

    cell = {}
    raw = io.StringIO()
    core.run_cell(
        model,
        np.array([1.0, 2.0, 3.0, 4.0]),
        AGGREGATE_NAMES,
        windows,
        "reconstruction",
        8,
        FakeGuard(),
        cell,
        raw,
        warmups=2,
        measurements=3,
        timer=Timer(),
    )
    assert cell["warmups_completed"] == 2 and cell["timed_completed"] == 3
    assert len(audit) == 6
    import json

    starts = [json.loads(line)["start"] for line in raw.getvalue().splitlines()]
    assert starts == [0, 8, 0, 8, 16]
    assert not any(m._forward_hooks for m in model.modules())


@pytest.mark.parametrize(
    "changes",
    [
        {"peak_rss_bytes": 1073741825},
        {"native_heap_reserved_bytes": 536870913},
        {"pressure_dispatch_flags": 4, "pressure_errno": None},
        {"peak_rss_bytes": None},
        {"pressure_dispatch_flags": 3, "pressure_errno": None},
    ],
)
def test_reused_guards_latch_failed_peaks_and_veto(changes):
    from raregate.benchmarks.guard import Guard

    guard = Guard(time.monotonic() + 10, probe=lambda: sample(**changes), notify=False)
    with pytest.raises(RuntimeError):
        guard.check()
    assert guard.error
    if changes.get("peak_rss_bytes"):
        assert guard.peak_rss == changes["peak_rss_bytes"]


@pytest.mark.parametrize("pressure,errno", [(1, None), (2, None), (None, 1)])
def test_equal_caps_pressure_WARN_unknown_advisory(pressure, errno):
    from raregate.benchmarks.guard import Guard

    with Guard(
        time.monotonic() + 10,
        probe=lambda: sample(
            peak_rss_bytes=1073741824,
            native_heap_reserved_bytes=536870912,
            pressure_dispatch_flags=pressure,
            pressure_errno=errno,
        ),
        notify=False,
    ) as guard:
        guard.check()
    assert not guard.report()["owned_thread_alive"]


def fake_receipt(tmp_path, phase="AE1"):
    directory = tmp_path / "out"
    directory.mkdir()
    (directory / phase).mkdir()
    p.write(directory / "reservation.json", {"task": "synthetic"})
    p.write(directory / f"{phase}-reservation.json", {"phase": phase})
    cells = [
        {
            "batch": b,
            "scope": scope,
            "status": "completed",
            "warmups_completed": 20,
            "timed_completed": 200,
            "latency_nanoseconds": {"count": 200},
        }
        for b in (1, 8, 32, 128, 1024)
        for scope in ("reconstruction", "score_decision", "adapter_decision")
    ]
    record = {
        "status": "passed",
        "comparisons": [{"passed": True}],
        "reference_reconstruction_sha256": "r",
        "reference_scores_sha256": "s",
        "diagnostic_FP64_reference_sha256": "d",
        "envelope_sha256": "e",
        "mismatches_per_threshold": [0] * 4,
    }
    receipt = {
        "task": "0022",
        "phase": phase,
        "status": "completed",
        "source_sha256": {},
        "binding": {
            "protocol_canonical_sha256": q.HASH,
            "grant_file_sha256": p.file_hash(directory / f"{phase}-reservation.json"),
            "reservation_file_sha256": p.file_hash(directory / "reservation.json"),
        },
        "optimizer_updates": 0,
        "test_background_model_access": False,
        "test_signal_model_access": False,
        "elapsed_seconds_including_imports_cleanup": 1,
        "cells": cells,
        "empty_timer_pair_nanoseconds": [1] * 200,
        "hashes_before": {"input": "i", "parameters": "p"},
        "hashes_after": {"input": "i", "parameters": "p"},
        "access_audit": {
            "local_array_reads_completed": 1,
            "original_array_reads_completed": 0,
        },
        "numerical": {"before": copy.deepcopy(record), "after": copy.deepcopy(record)},
        "resources": {
            "peak_rss_bytes": 1073741824,
            "native_heap_reserved_bytes": 536870912,
            "latched_error": None,
            "owned_thread_alive": False,
        },
    }
    dispatch = {
        "returncode": 0,
        "child_reaped": True,
        "deadline_passed": True,
        "parent_error": None,
    }
    p.write(directory / phase / "receipt.json", receipt)
    return directory, receipt, dispatch


def test_valid_new_receipt_exact_caps_is_accepted(tmp_path, monkeypatch):
    directory, _, dispatch = fake_receipt(tmp_path)
    monkeypatch.setattr(p, "source_map", lambda root: {})
    _, valid = controller.validate_receipt(tmp_path, directory, "AE1", dispatch)
    assert valid


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "duplicate",
        "wrong_order",
        "warmup",
        "count",
        "hash",
        "reference",
        "envelope",
        "decision",
        "local_violation",
        "array_read",
        "original_read",
        "guard",
        "rss",
        "native",
        "deadline",
        "crash",
        "unreaped",
        "hooks",
        "failed",
    ],
)
def test_truthful_incomplete_or_mutated_receipt_is_refused(
    tmp_path, monkeypatch, change
):
    directory, receipt, dispatch = fake_receipt(tmp_path)
    if change == "missing":
        receipt["cells"].pop()
    elif change == "duplicate":
        receipt["cells"][1] = copy.deepcopy(receipt["cells"][0])
    elif change == "wrong_order":
        receipt["cells"].reverse()
    elif change == "warmup":
        receipt["cells"][0]["warmups_completed"] = 19
    elif change == "count":
        receipt["cells"][0]["latency_nanoseconds"]["count"] = 199
    elif change == "hash":
        receipt["hashes_after"]["parameters"] = "changed"
    elif change == "reference":
        receipt["numerical"]["after"]["reference_scores_sha256"] = "changed"
    elif change == "envelope":
        receipt["numerical"]["after"]["envelope_sha256"] = "changed"
    elif change == "decision":
        receipt["numerical"]["before"]["mismatches_per_threshold"] = [1, 0, 0, 0]
    elif change == "local_violation":
        receipt["numerical"]["after"]["comparisons"][0]["passed"] = False
    elif change == "array_read":
        receipt["access_audit"]["local_array_reads_completed"] = 0
    elif change == "original_read":
        receipt["access_audit"]["original_array_reads_completed"] = 1
    elif change == "guard":
        receipt["resources"]["latched_error"] = "critical"
    elif change == "rss":
        receipt["resources"]["peak_rss_bytes"] += 1
    elif change == "native":
        receipt["resources"]["native_heap_reserved_bytes"] += 1
    elif change == "deadline":
        dispatch["deadline_passed"] = False
    elif change == "crash":
        dispatch["returncode"] = -9
    elif change == "unreaped":
        dispatch["child_reaped"] = False
    elif change == "hooks":
        receipt["resources"]["owned_thread_alive"] = True
    elif change == "failed":
        receipt["status"] = "failed"
    p.write(directory / "AE1/receipt.json", receipt)
    monkeypatch.setattr(p, "source_map", lambda root: {})
    _, valid = controller.validate_receipt(tmp_path, directory, "AE1", dispatch)
    assert not valid


def test_controller_stops_after_failed_phase_and_never_replays(tmp_path, monkeypatch):
    spec = q.load()
    (tmp_path / q.OUTPUT).parent.mkdir(parents=True)
    accept = tmp_path / q.ACCEPTANCE
    accept.parent.mkdir()
    accept.write_text("{}")
    monkeypatch.setattr(
        controller,
        "prerequisites",
        lambda *args, **kw: (spec, {}, {"source_sha256": {}}),
    )
    monkeypatch.setattr(controller, "parent_check", lambda **kw: 1)
    monkeypatch.setattr(controller, "fresh_hardware", lambda: {})
    monkeypatch.setattr(p, "source_map", lambda root: {})
    monkeypatch.setattr(p, "code_context", lambda root: {})
    calls = []

    def fail(command, *args, **kw):
        calls.append(command)
        return {
            "returncode": 1,
            "child_reaped": True,
            "deadline_passed": True,
            "parent_error": None,
        }

    monkeypatch.setattr(controller, "supervise", fail)
    assert controller.run_campaign(tmp_path) == 1
    assert len(calls) == 1
    state = p.read(tmp_path / q.OUTPUT / "workflow.json")
    assert (
        state["status"] == "failed_consumed_no_retry"
        and not state["comparison_success"]
    )
    assert state["missing_measured_cells"] == 90
    assert controller.run_campaign(tmp_path) == 1
    assert len(calls) == 1


def test_wrong_phase_binding_refused_before_framework_or_array_import(
    tmp_path, monkeypatch
):
    from raregate.benchmarks import frozen_cpu_v2_worker as worker

    directory = tmp_path / q.OUTPUT
    directory.mkdir(parents=True)
    p.write(directory / "reservation.json", {"parent_pid": 1})
    p.write(
        directory / "AE1-reservation.json",
        {"phase": "AE1", "token": "wrong", "parent_pid": 1},
    )
    spec = q.load()
    monkeypatch.setattr(q, "load", lambda root: spec)
    # Wrong token is evaluated before any numerical metadata/source/opening.
    with pytest.raises(ValueError):
        worker.bindings("AE1", "expected", tmp_path)


def test_gamma_dimensions_and_underflow_exclusions():
    assert a.DIMENSIONS == (8, 6, 3, 6)
    assert a.SSE_OPERATION_CEILING == 32
    with pytest.raises(a.ArithmeticFailure):
        a.sub_down(np.finfo(float).tiny, np.nextafter(np.finfo(float).tiny, 0))


def test_rounding_mode_checked_without_changing_it(monkeypatch):
    class Query:
        def __call__(self):
            return 1

    class Library:
        fegetround = Query()

    monkeypatch.setattr(a.ctypes, "CDLL", lambda name: Library())
    with pytest.raises(a.ArithmeticFailure):
        a.round_mode()


def test_zero_bound_failure_preserves_truthful_ratio_and_failed_values():
    with pytest.raises(a.ArithmeticFailure) as caught:
        a.assert_bound(np.ones(1), np.zeros(1), np.zeros(1), "zero_bound")
    evidence = caught.value.evidence
    assert evidence["max_error_over_bound"] is None
    assert evidence["nonzero_error_at_zero_bound"] == 1
    assert evidence["violations"] == 1 and not evidence["passed"]
    assert evidence["first_failure"]["bound"] == 0
