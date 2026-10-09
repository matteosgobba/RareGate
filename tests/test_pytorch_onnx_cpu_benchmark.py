"""Task0025 software tests: synthetic fixtures only, including actual CPU sessions."""

import io
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pytest
import torch
from test_frozen_cpu_benchmark import FakeGuard, sample
from test_onnx_cpu_export import exported as exported
from test_onnx_cpu_export import needs_onnx

from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks import pytorch_onnx_cpu as c
from latenttrigger.benchmarks import pytorch_onnx_cpu_numerics as n
from latenttrigger.benchmarks import pytorch_onnx_cpu_protocol as q
from latenttrigger.benchmarks import pytorch_onnx_cpu_statistics as s
from latenttrigger.benchmarks.frozen_cpu import supervise
from latenttrigger.benchmarks.guard import Guard, GuardError
from latenttrigger.data.inspection import AGGREGATE_NAMES


def accepted_record():
    good = dict(passed=True, violations=0)
    return dict(
        status="passed",
        windows_verified=1193,
        row_window_presentations=5120,
        unique_rows=1024,
        decision_mismatches=[0] * 4,
        local_affine_violations=0,
        hashes_before={},
        hashes_after={},
        reference_comparisons=[good.copy()],
        grids=[
            dict(
                batch=b,
                windows=1024 // b,
                rows=1024,
                status="passed",
                decision_mismatches=[0] * 4,
                local_affine_violations=0,
                same_runtime_repeat_byte_exact=True,
                diagnostic_primary_final_byte_exact=True,
                same_runtime_SSE_byte_exact=True,
                comparisons=[good.copy()],
            )
            for b in q.BATCHES
        ],
    )


@pytest.mark.parametrize(
    "change",
    [
        "status",
        "windows",
        "rows",
        "mismatch",
        "local",
        "hash",
        "grid",
        "comparison",
        "repeat",
        "reference",
    ],
)
def test_admission_inspects_failed_evidence_instead_of_successful_return(change):
    r = accepted_record()
    if change == "status":
        r["status"] = "failed"
    if change == "windows":
        r["windows_verified"] = 1192
    if change == "rows":
        r["row_window_presentations"] = 5119
    if change == "mismatch":
        r["decision_mismatches"][2] = 1
    if change == "local":
        r["local_affine_violations"] = 1
    if change == "hash":
        r["hashes_after"] = {"changed": True}
    if change == "grid":
        r["grids"][0]["status"] = "failed"
    if change == "comparison":
        r["grids"][0]["comparisons"][0]["violations"] = 1
    if change == "repeat":
        r["grids"][0]["same_runtime_repeat_byte_exact"] = False
    if change == "reference":
        r["reference_comparisons"][0]["passed"] = False
    with pytest.raises(ValueError):
        n.admit(r)


def test_complete_gate():
    n.admit(accepted_record())


@pytest.mark.parametrize(
    "key,value",
    [
        ("extra", 1),
        ("output", "elsewhere"),
        ("measurements", 201),
        ("gates", {"rtol": 1}),
        ("input", {"path": "data/processed/full"}),
        ("worker_order", ["ORT1"]),
    ],
)
def test_strict_protocol_unknown_unsafe_override(tmp_path, key, value, monkeypatch):
    spec = dict(schema_version=1, output=q.OUTPUT, measurements=200)
    monkeypatch.setattr(q, "HASH", p.digest(spec))
    path = tmp_path / q.CONFIG
    path.parent.mkdir(parents=True)
    p.write(path, spec)
    assert q.load(tmp_path) == spec
    spec[key] = value
    p.write(path, spec)
    with pytest.raises(ValueError, match="strict"):
        q.load(tmp_path)


@pytest.mark.parametrize("text", ["", "build release 402979a", 'é " \\ \n'])
def test_hash_kind_distinguishes_raw_bytes_and_JSON_string(text):
    hashes = q.build_hashes(text)
    assert hashes["raw_UTF8_byte_sha256"] != hashes["canonical_JSON_string_sha256"]
    q.check_build(text, hashes)
    with pytest.raises(ValueError):
        q.check_build(text, {k: hashes["raw_UTF8_byte_sha256"] for k in hashes})


def test_exclusive_atomic_reservation_preserves_winner(tmp_path, monkeypatch):
    (tmp_path / q.OUTPUT).parent.mkdir(parents=True)
    (tmp_path / "data").mkdir()
    p.write(tmp_path / q.ACCEPTANCE, {})
    monkeypatch.setattr(q, "source_map", lambda root: {})
    monkeypatch.setattr(p, "code_context", lambda root: {})

    def attempt(_):
        try:
            return c.reserve(
                tmp_path, {}, {}, dict(source_file_sha256={}), time.monotonic()
            )[0]
        except FileExistsError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sum(v is not None for v in results) == 1
    original = (tmp_path / q.OUTPUT / "reservation.json").read_bytes()
    with pytest.raises(FileExistsError):
        c.reserve(tmp_path, {}, {}, dict(source_file_sha256={}), time.monotonic())
    assert (tmp_path / q.OUTPUT / "reservation.json").read_bytes() == original


@pytest.mark.parametrize(
    "state", ["foreign", "partial", "reserved_no_retry", "completed"]
)
def test_consumed_namespace_has_no_reset_route(tmp_path, state, monkeypatch):
    directory = tmp_path / q.OUTPUT
    directory.mkdir(parents=True)
    p.write(directory / "reservation.json", dict(status=state))
    monkeypatch.setattr(c, "refuse_early_imports", lambda: None)
    monkeypatch.setattr(c, "parent_check", lambda: 1)
    monkeypatch.setattr(c.sys, "platform", "darwin")
    monkeypatch.setattr(q, "load", lambda root: {})
    monkeypatch.setattr(q, "metadata", lambda *args: {})
    monkeypatch.setattr(q, "acceptance", lambda root: {})
    with pytest.raises(ValueError, match="namespace"):
        c.prerequisites(tmp_path)


class ToyAdapter:
    def __init__(self):
        self.calls = 0

    def score(self, x, *, feature_names):
        self.calls += 1
        return core.separated(x, np.zeros_like(x), np.ones(4))[0]


@pytest.mark.parametrize("batch", q.BATCHES)
@pytest.mark.parametrize("scope", q.SCOPES)
def test_schedule_boundaries_counters_and_forward_free_score(batch, scope):
    calls = []
    model = ToyAdapter()
    guard = FakeGuard()
    x = np.ones((1024, 8), np.float32)
    windows = []
    for start in range(0, 1024, batch):

        def forward(start=start):
            calls.append(start)
            return np.zeros((batch, 8), np.float32)

        windows.append(
            dict(
                start=start,
                values=x[start : start + batch],
                reconstruction=np.zeros((batch, 8), np.float32),
                forward=forward,
            )
        )
    counter = iter(range(400))
    cell = {}
    raw = io.StringIO()
    n.run_cell(
        model,
        np.arange(4, dtype=np.float64),
        AGGREGATE_NAMES,
        windows,
        scope,
        batch,
        guard,
        cell,
        raw,
        timer=lambda: next(counter),
    )
    rows = [json.loads(line) for line in raw.getvalue().splitlines()]
    assert (
        len(rows) == 220
        and cell["timed_completed"] == 200
        and cell["warmups_completed"] == 20
    )
    for phase, count in [("warmup", 20), ("measurement", 200)]:
        assert [r["start"] for r in rows if r["phase"] == phase] == [
            (i % (1024 // batch)) * batch for i in range(count)
        ]
    assert len(calls) == (220 if scope == "reconstruction" else 0)
    assert model.calls == (220 if scope == "adapter_decision" else 0)
    assert cell["latency_nanoseconds"]["mean"] == 1


@pytest.mark.parametrize("elapsed", [0, -1])
def test_nonpositive_timer_keeps_completed_call_and_invalidates(elapsed):
    raw = io.StringIO()
    cell = {}
    timer = iter([10, 10 + elapsed])
    window = dict(
        start=0,
        values=np.ones((1, 8), np.float32),
        reconstruction=np.zeros((1, 8), np.float32),
        forward=lambda: np.zeros((1, 8), np.float32),
    )
    with pytest.raises(ValueError, match="Nonpositive"):
        n.run_cell(
            ToyAdapter(),
            np.ones(4),
            (),
            [window],
            "reconstruction",
            1,
            FakeGuard(),
            cell,
            raw,
            warmups=0,
            measurements=1,
            timer=lambda: next(timer),
        )
    assert (
        cell["timed_completed"] == 1
        and json.loads(raw.getvalue())["elapsed_ns"] == elapsed
    )
    assert cell["status"] == "running" and "latency_nanoseconds" not in cell


@pytest.mark.parametrize("delta", [0.0, np.nextafter(1.0, 2.0) - 1])
def test_FP64_cast_before_subtraction_and_strict_ties(delta):
    x = np.full((1, 8), 1e8, np.float32)
    r = np.ones((1, 8), np.float32)
    scores, _ = core.separated(x, r, np.ones(4))
    assert abs(scores[0] - 8 * (int(1e8) - 1) ** 2) <= 16
    assert scores[0] != float(np.sum((x - r) ** 2))
    decision = core.decisions(np.array([1 + delta]), np.array([1.0, 2.0, 3.0, 4.0]))
    assert bool(decision[0, 0]) == (delta > 0)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0])
def test_nonfinite_negative_scores_refused(value):
    with pytest.raises(core.NumericalError):
        core.decisions(np.array([value]), np.ones(4))


def synthetic_stages(tmp_path, *, incomplete=False):
    stages = [dict(phase="prepare", status="completed")]
    for phase in q.PHASES[1:]:
        d = tmp_path / phase
        d.mkdir()
        cells = []
        with (d / "timings.jsonl").open("w") as raw:
            for b in q.BATCHES:
                for scope in q.SCOPES:
                    ns = [
                        100 * int(phase[-1]) * (2 if phase.startswith("PyTorch") else 1)
                    ] * 200
                    cells.append(
                        dict(
                            batch=b,
                            scope=scope,
                            status="completed",
                            latency_nanoseconds=p.distribution(ns, b),
                        )
                    )
                    for kind, count in [("warmup", 20), ("measurement", 200)]:
                        for i in range(count):
                            raw.write(
                                json.dumps(
                                    dict(
                                        batch=b,
                                        scope=scope,
                                        phase=kind,
                                        index=i,
                                        start=(i % (1024 // b)) * b,
                                        elapsed_ns=ns[i % 200]
                                        if kind == "measurement"
                                        else None,
                                    )
                                )
                                + "\n"
                            )
        stages.append(
            dict(
                phase=phase,
                status="failed" if incomplete and phase == "ORT3" else "completed",
                runtime_name="PyTorch" if phase.startswith("PyTorch") else "ORT",
                cells=cells,
                empty_timer_pair_nanoseconds=[1] * 200,
            )
        )
    return stages


def test_pooled_all600_population_stats_ratios_and_normalization(tmp_path):
    result = s.aggregate(synthetic_stages(tmp_path), tmp_path)
    assert result["comparison_success"] and len(result["cells"]) == 90
    assert (
        result["counts"]["timed_invocations"] == 18000
        and result["counts"]["warmup_invocations"] == 1800
    )
    assert result["counts"]["timed_forward_row_presentations"] == 2863200
    pool = next(
        v for v in result["pooled"] if v["batch"] == 128 and v["runtime"] == "ORT"
    )
    stats = pool["latency_nanoseconds"]
    assert (
        stats["count"] == 600
        and stats["mean"] == 200
        and stats["mean_amortized_nanoseconds_per_event"] == 200 / 128
    )
    assert stats["throughput_events_per_second"] == 128 / (200 / 1e9)
    assert all(
        r["PyTorch_over_ORT_mean_ratios"] == [2] * 3
        and r["geometric_mean"] == 2
        and r["pooled_mean_ratio"] == 2
        for r in result["paired_ratios"]
    )


def test_post_failure_invalidates_raw_performance_without_deleting(tmp_path):
    result = s.aggregate(synthetic_stages(tmp_path, incomplete=True), tmp_path)
    assert (
        not result["comparison_success"]
        and result["counts"]["timed_invocations"] == 18000
    )
    assert all(not r["performance_accepted"] for r in result["paired_ratios"])
    assert all(not r["performance_accepted"] for r in result["pooled"])


def test_missing_partial_workers_not_manufactured_zero(tmp_path):
    assert s.aggregate([], tmp_path)["pooled"] == []
    d = tmp_path / "PyTorch1"
    d.mkdir()
    p.write(
        d / "access.json",
        dict(local_array_read_attempts=1, local_array_reads_completed=0),
    )
    recovered = c.recover(d, "PyTorch1")
    assert (
        recovered["status"] == "failed"
        and recovered["possible_inflight_invocation_unknown"]
    )
    assert recovered["access"]["local_array_reads_completed"] == 0


@pytest.mark.parametrize(
    "metric,limit",
    [("peak_rss_bytes", 1073741824), ("native_heap_reserved_bytes", 536870912)],
)
@pytest.mark.parametrize("extra", [0, 1])
def test_caps_equality_and_failed_peak(metric, limit, extra):
    guard = Guard(
        time.monotonic() + 5,
        probe=lambda: sample(**{metric: limit + extra}),
        notify=False,
    )
    if extra:
        with pytest.raises(GuardError):
            guard.check()
    else:
        guard.check()
    assert guard.report()[metric] == limit + extra


@pytest.mark.parametrize(
    "flag,errno,passes",
    [
        (1, None, True),
        (2, None, True),
        (None, 1, True),
        (4, None, False),
        ("1", None, False),
    ],
)
def test_pressure_disclosure_and_veto(flag, errno, passes):
    guard = Guard(
        time.monotonic() + 5,
        probe=lambda: sample(pressure_dispatch_flags=flag, pressure_errno=errno),
        notify=False,
    )
    if passes:
        guard.check()
    else:
        with pytest.raises(GuardError):
            guard.check()
    assert guard.error is None if passes else guard.error is not None


def test_blocked_import_native_parent_deadline_reaps(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "latenttrigger.benchmarks.frozen_cpu.parent_check", lambda **kwargs: 1
    )
    result = supervise(
        [sys.executable, "-c", "import time; time.sleep(4)"],
        tmp_path / "worker.log",
        root=tmp_path,
        environment=os.environ.copy(),
        started=time.monotonic() - 57.8,
        campaign_deadline=time.monotonic() + 4,
    )
    assert result["child_reaped"] and "deadline" in result["parent_error"]


@pytest.mark.parametrize("runtime", ["PyTorch", "ORT"])
@needs_onnx
def test_actual_cpu_runtime_three_scope_integration(exported, runtime):
    values = np.ones((1024, 8), np.float32)
    counts = dict(
        prepared_forward_row_presentations=0,
        prepared_reference_row_presentations=0,
        prepared_verification_forward_row_presentations=0,
    )
    chosen = exported.model if runtime == "PyTorch" else exported.runtime
    before = core.parameter_hash(exported.model)
    windows = n.prepare_windows(
        chosen, runtime, values, AGGREGATE_NAMES, counts, FakeGuard()
    )
    n.verify_prepared(
        chosen,
        dict(cpu=exported.model, name=runtime),
        values,
        windows,
        AGGREGATE_NAMES,
        np.array([1.0, 2.0, 3.0, 4.0]),
        counts,
        FakeGuard(),
    )
    n.effective_session(exported.runtime)
    with torch.inference_mode():
        for batch in q.BATCHES:
            for scope in q.SCOPES:
                cell = {}
                raw = io.StringIO()
                n.run_cell(
                    chosen,
                    np.array([1.0, 2.0, 3.0, 4.0]),
                    AGGREGATE_NAMES,
                    windows[batch],
                    scope,
                    batch,
                    FakeGuard(),
                    cell,
                    raw,
                    warmups=1,
                    measurements=2,
                )
                assert cell["timed_completed"] == 2
    assert (
        before == core.parameter_hash(exported.model)
        and counts["prepared_forward_row_presentations"] == 5120
    )


@pytest.mark.parametrize(
    "change", ["provider", "intra", "inter", "optimization", "fallback"]
)
@needs_onnx
def test_effective_runtime_refuses_drift(exported, monkeypatch, change):
    session = exported.runtime.session
    options = session.get_session_options()
    if change == "provider":
        monkeypatch.setattr(
            session, "get_providers", lambda: ["AzureExecutionProvider"]
        )
    elif change == "fallback":
        monkeypatch.setattr(session, "_enable_fallback", True)
    else:
        if change == "intra":
            options.intra_op_num_threads = 2
        if change == "inter":
            options.inter_op_num_threads = 2
        if change == "optimization":
            options.graph_optimization_level = __import__(
                "onnxruntime"
            ).GraphOptimizationLevel.ORT_ENABLE_ALL
        monkeypatch.setattr(session, "get_session_options", lambda: options)
    with pytest.raises(ValueError, match="drift"):
        n.effective_session(exported.runtime)


def test_controller_import_is_stdlib_without_optional_stack():
    source = Path(c.__file__).parents[2]
    env = dict(os.environ, PYTHONPATH=str(source))
    code = "import sys; from latenttrigger.benchmarks import pytorch_onnx_cpu; assert not any(n in sys.modules for n in ('numpy','torch','onnx','onnxruntime','onnxscript'))"
    subprocess.run([sys.executable, "-c", code], env=env, check=True, timeout=5)
