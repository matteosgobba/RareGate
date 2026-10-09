"""Software device simulation and synthetic CPU fixtures; no physical GPU/data/Git."""

import hashlib
import io
import json
import os
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace as NS

import numpy as np
import pytest
import torch
from test_frozen_cpu_benchmark import FakeGuard, sample

from latenttrigger.benchmarks import arithmetic_cpu_v2 as arithmetic
from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import cpu_mps as controller
from latenttrigger.benchmarks import cpu_mps_device as device
from latenttrigger.benchmarks import cpu_mps_numerics as n
from latenttrigger.benchmarks import cpu_mps_protocol as q
from latenttrigger.benchmarks import cpu_mps_worker as worker
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.guard import GuardError
from latenttrigger.data.inspection import AGGREGATE_NAMES
from latenttrigger.models.autoencoder import CompactAutoencoder


@pytest.fixture
def spec():
    return dict(
        input=dict(
            path="results/benchmarks/task0020-frozen-cpu/prepare/input.npy",
            file_sha256="unused",
            array_bytes_sha256="unused",
        ),
        device_environment_before_imports=dict(
            PYTORCH_ENABLE_MPS_FALLBACK="0", PYTORCH_MPS_FAST_MATH="0"
        ),
        forbidden_environment_overrides=[
            "PYTORCH_MPS_HIGH_WATERMARK_RATIO",
            "PYTORCH_MPS_LOW_WATERMARK_RATIO",
            "PYTORCH_MPS_PREFER_METAL",
        ],
        runtime=dict(thread_environment_before_imports=dict(OMP_NUM_THREADS="1")),
        policy=dict(runtime_torch_build_sha256=p.digest("fixture-build")),
    )


def api(current=0, driver=0):
    return NS(
        synchronize=lambda: None,
        current_allocated_memory=lambda: current,
        driver_allocated_memory=lambda: driver,
    )


@pytest.mark.parametrize(
    "built,available", [(False, False), (True, False), (True, True)]
)
def test_availability_build_distinct_without_physical_probe(
    monkeypatch, spec, built, available
):
    calls = []
    fake = NS(
        backends=NS(
            mps=NS(
                is_built=lambda: built,
                is_available=lambda: available,
                __file__="fixture",
            )
        ),
        mps=NS(__file__="fixture"),
        __config__=NS(show=lambda: "fixture-build"),
        __version__="fixture",
        version=NS(git_version="fixture"),
    )
    monkeypatch.setattr(p, "file_hash", lambda path: calls.append(path) or "fixture")
    monkeypatch.setattr(p, "runtime_versions", lambda: {"torch": "fixture"})
    result = device.availability(fake, spec)
    assert result["is_built"] is built and result["is_available"] is available
    assert result["execution_context"]["sandbox_restriction_cause"] == "unverified"
    assert result["execution_context"]["gpu_physical_absence"] == "not_inferred"
    assert calls == ["fixture", "fixture"]
    if not available:
        with pytest.raises(ValueError, match="unavailable"):
            device.require_available(result)


@pytest.mark.parametrize("built,available", [(False, True), (1, False), (True, None)])
def test_malformed_availability_relation_refused(monkeypatch, spec, built, available):
    fake = NS(
        backends=NS(
            mps=NS(
                is_built=lambda: built,
                is_available=lambda: available,
                __file__="fixture",
            )
        ),
        mps=NS(__file__="fixture"),
    )
    monkeypatch.setattr(p, "file_hash", lambda _: "fixture")
    with pytest.raises(ValueError, match="Malformed"):
        device.availability(fake, spec)


@pytest.mark.parametrize("current,driver", [(0, 0), (268435456, 536870912), (8, 16)])
def test_primary_device_cap_equality_and_semantics(current, driver):
    a = device.DeviceAccounting()
    a.enable(api(current, driver))
    a.sample()
    assert a.report()["tensor_peak_bytes"] == current
    assert a.report()["driver_peak_bytes"] == driver
    assert a.report()["metrics_overlap_host_unified_memory"]


@pytest.mark.parametrize("current,driver", [(268435457, 536870912), (0, 536870913)])
def test_failed_device_peaks_latch_before_caps(current, driver):
    a = device.DeviceAccounting()
    a.enable(api(current, driver))
    with pytest.raises(GuardError, match="cap"):
        a.sample()
    assert a.current_peak == current and a.driver_peak == driver
    with pytest.raises(GuardError):
        a.sample()
    assert a.checks == 1


@pytest.mark.parametrize(
    "current,driver",
    [(True, 1), (1, False), (None, 2), (-1, 2), (3, 2), (0, float("inf"))],
)
def test_malformed_primary_device_accounting_refusal(current, driver):
    a = device.DeviceAccounting()
    a.enable(api(current, driver))
    with pytest.raises(GuardError, match="Malformed"):
        a.sample()
    assert a.error


def test_absent_device_api_and_CPU_not_applicable():
    a = device.DeviceAccounting()
    assert a.sample() is None
    assert a.report()["tensor_peak_bytes"] is None
    assert a.report()["status"] == "not_applicable"
    with pytest.raises(GuardError, match="Unavailable"):
        a.enable(NS())


@pytest.mark.parametrize(
    "pressure,errno,allowed",
    [
        (1, None, True),
        (2, None, True),
        (None, 1, True),
        (4, None, False),
        (7, None, False),
        (None, None, False),
    ],
)
def test_composed_host_pressure_and_device_guard(pressure, errno, allowed):
    a = device.DeviceAccounting()
    a.enable(api(4, 8))
    g = device.DeviceGuard(
        time.monotonic() + 1,
        accounting=a,
        probe=lambda: sample(pressure_dispatch_flags=pressure, pressure_errno=errno),
        notify=False,
    )
    if allowed:
        with g:
            g.check()
        label = {1: "NORMAL", 2: "WARN", None: "unknown"}[pressure]
        assert g.report()["pressure_counts"][label] > 0 and a.checks > 0
    else:
        with pytest.raises(GuardError):
            with g:
                g.check()
    assert not g.report()["owned_thread_alive"]


@pytest.mark.parametrize(
    "key,limit",
    [("peak_rss_bytes", 1073741824), ("native_heap_reserved_bytes", 536870912)],
)
@pytest.mark.parametrize("extra", [0, 1])
def test_host_caps_and_failed_peak_preserved(key, limit, extra):
    g = device.DeviceGuard(
        time.monotonic() + 1,
        accounting=device.DeviceAccounting(),
        probe=lambda: sample(**{key: limit + extra}),
        notify=False,
    )
    if extra:
        with pytest.raises(GuardError):
            g.check()
    else:
        g.check()
    assert g.report()[key] == limit + extra


class FakeTensor:
    def __init__(self, array, kind="cpu", mutate=False):
        self.array, self.device, self.dtype, self.mutate = (
            np.array(array, np.float32),
            NS(type=kind),
            torch.float32,
            mutate,
        )

    def numpy(self):
        return self.array

    def to(self, kind):
        arr = self.array.copy()
        if self.mutate:
            arr.flat[0] += 1
        return FakeTensor(arr, kind)

    def cpu(self):
        return FakeTensor(self.array)


@pytest.mark.parametrize("mutate", [False, True])
def test_exact_FP32_CPU_device_CPU_transfer(monkeypatch, mutate):
    sync = []
    fake = NS(float32=torch.float32, mps=NS(synchronize=lambda: sync.append("sync")))
    value = FakeTensor([0, -0.0, 1, 2], mutate=mutate)
    if mutate:
        with pytest.raises(ValueError, match="mutated"):
            device.exact_roundtrip(fake, value, "mps")
    else:
        result = device.exact_roundtrip(fake, value, "mps")
        assert result.cpu().numpy().tobytes() == value.numpy().tobytes()
    assert sync == ["sync"]


def test_precision_and_device_fallback_refused():
    value = FakeTensor([1])
    value.dtype = torch.float16
    with pytest.raises(ValueError, match="FP32"):
        device.exact_roundtrip(torch, value, "mps")
    value = FakeTensor([1])
    value.to = lambda _: value
    with pytest.raises(ValueError, match="fallback"):
        device.exact_roundtrip(torch, value, "mps")


@pytest.mark.parametrize(
    "scope", ["reconstruction", "score_decision", "adapter_decision"]
)
def test_completion_order_and_transfer_placement(scope):
    events = []

    def timer():
        events.append("timer")
        return len(events)

    def operation():
        events.append(
            "forward_no_transfer"
            if scope == "reconstruction"
            else "CPU_SSE"
            if scope == "score_decision"
            else "public_input_forward_output_CPU_SSE"
        )
        return "result"

    out, elapsed = n.timed_invocation(
        operation,
        device="mps",
        scope=scope,
        timer=timer,
        sync=lambda _: events.append("sync"),
    )
    assert out == "result" and elapsed > 0
    if scope == "score_decision":
        assert events == ["timer", "CPU_SSE", "timer"]
    else:
        assert events[0:2] == ["sync", "timer"] and events[-2:] == ["sync", "timer"]
    if scope == "reconstruction":
        assert all("transfer" not in e or e == "forward_no_transfer" for e in events)


def synthetic_model():
    model = CompactAutoencoder().eval()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.fill_(0.03125)
    return model


@pytest.mark.parametrize("batch", [1, 8, 32, 128, 1024])
@pytest.mark.parametrize(
    "scope", ["reconstruction", "score_decision", "adapter_decision"]
)
def test_exact_window_schedule_all_three_scopes_timer_pairs(batch, scope):
    model = synthetic_model()
    values = np.ones((1024, 8), np.float32)
    counts = worker.audit()
    items = n.build_windows(model, values, batch, "cpu", counts)
    assert [v["start"] for v in items] == list(range(0, 1024, batch))
    raw = io.StringIO()
    cell = {}
    ticks = iter(range(0, 100000, 5))
    n.run_cell(
        model,
        np.array([1, 2, 3, 4], np.float64),
        AGGREGATE_NAMES,
        items,
        scope,
        batch,
        "cpu",
        FakeGuard(),
        cell,
        raw,
        counts,
        timer=lambda: next(ticks),
    )
    rows = [json.loads(line) for line in raw.getvalue().splitlines()]
    assert (
        len(rows) == 220
        and cell["timed_completed"] == 200
        and cell["warmups_completed"] == 20
    )
    for phase, amount in (("warmup", 20), ("measurement", 200)):
        subset = [r for r in rows if r["phase"] == phase]
        assert [r["start"] for r in subset] == [
            (i % (1024 // batch)) * batch for i in range(amount)
        ]
    assert cell["latency_nanoseconds"]["mean"] == 5
    assert counts["measurement_forward_input_presentations"] == (
        0 if scope == "score_decision" else batch * 200
    )


def test_device_specific_local_checks_and_CPU_reference_synthetic_only():
    model = synthetic_model()
    values = np.ones((1024, 8), np.float32)
    counts = worker.audit()
    windows = {
        b: n.build_windows(model, values, b, "cpu", counts)
        for b in (1, 8, 32, 128, 1024)
    }
    thresholds = np.array([1, 2, 3, 4], np.float64)
    before = n.verify(
        model,
        model,
        values,
        thresholds,
        AGGREGATE_NAMES,
        windows,
        "cpu",
        FakeGuard(),
        counts,
    )
    after = n.verify(
        model,
        model,
        values,
        thresholds,
        AGGREGATE_NAMES,
        windows,
        "cpu",
        FakeGuard(),
        counts,
    )
    assert before == after and before["mismatch_counts"] == [0] * 4
    assert before["local_affine_scalar_checks"] > 0
    assert all(r["passed"] for r in before["comparisons"])
    assert all(not m._forward_hooks for m in model.modules())
    assert (
        counts["original_array_reads_completed"]
        == counts["local_array_reads_completed"]
        == 0
    )


@pytest.mark.parametrize("failure", ["repeat", "nonfinite", "threshold"])
def test_numerical_failures_preserve_strict_refusal(monkeypatch, failure):
    model = synthetic_model()
    values = np.ones((1024, 8), np.float32)
    counts = worker.audit()
    windows = {1024: n.build_windows(model, values, 1024, "cpu", counts)}
    if failure == "repeat":
        windows[1024][0]["reconstruction"][0, 0] += 1
    elif failure == "nonfinite":
        values[0, 0] = np.nan
    else:
        original = model.score
        counter = [0]

        def changed(*args, **kwargs):
            counter[0] += 1
            result = original(*args, **kwargs)
            if counter[0] > 1:
                result[0] = np.nextafter(1.0, np.inf)
            return result

        monkeypatch.setattr(model, "score", changed)
    with pytest.raises(ValueError):
        n.verify(
            model,
            model,
            values,
            np.array([1, 2, 3, 4], np.float64),
            AGGREGATE_NAMES,
            windows,
            "cpu",
            FakeGuard(),
            counts,
        )
    assert all(not m._forward_hooks for m in model.modules())


def test_score_cast_before_subtract_strict_ties_and_nearby_mismatch():
    values = np.zeros((3, 8), np.float32)
    reconstruction = values.copy()
    reconstruction[:, 0] = [
        1,
        np.nextafter(np.float32(1), np.float32(2)),
        np.nextafter(np.float32(1), np.float32(0)),
    ]
    scores, decisions = core.separated(
        values, reconstruction, np.array([1, 2, 3, 4], np.float64)
    )
    assert scores.dtype == np.float64 and decisions[:, 0].tolist() == [
        False,
        True,
        False,
    ]
    with pytest.raises(core.NumericalError):
        core.verify_decisions(
            scores,
            np.array([1.0, 1.0, 1.0]),
            np.array([1, 2, 3, 4.0]),
            "strict_near_ties",
        )


@pytest.mark.parametrize("value", [np.inf, np.nan, 2.0**-50, 2.0**50])
def test_device_operation_domain_refusal(value):
    with pytest.raises(arithmetic.ArithmeticFailure):
        arithmetic.supported(np.array([value]))


def test_device_local_bound_cannot_be_fitted_or_inflated():
    x = np.ones((1, 8))
    w = np.ones((6, 8))
    bias = np.zeros(6)
    bound = arithmetic.local_affine_bound(x, w, bias)
    actual = np.full((1, 6), 8.0)
    actual[0, 0] += float(bound[0, 0]) * 2
    with pytest.raises(arithmetic.ArithmeticFailure) as exc:
        arithmetic.assert_bound(actual, np.full((1, 6), 8.0), bound, "device_local")
    assert (
        exc.value.evidence["violations"] == 1
        and exc.value.evidence["first_failure"]["actual"] > 8
    )


@pytest.mark.parametrize(
    "selector",
    [
        "full/train_background",
        "dev/test_background",
        "dev/test_signal",
        "truth",
        "labels",
    ],
)
def test_unsafe_input_selector_rejected_before_numpy_open(
    monkeypatch, tmp_path, spec, selector
):
    spec["input"]["path"] = selector
    monkeypatch.setattr(
        np, "load", lambda *a, **k: pytest.fail("Numerical opening before refusal")
    )
    with pytest.raises(ValueError, match="Only original"):
        n.read_array(tmp_path, spec, worker.audit())


def test_one_bounded_array_read_hashes_before_open(monkeypatch, tmp_path, spec):
    target = tmp_path / spec["input"]["path"]
    target.parent.mkdir(parents=True)
    values = np.ones((1024, 8), np.float32)
    np.save(target, values, allow_pickle=False)
    spec["input"].update(
        file_sha256=p.file_hash(target), array_bytes_sha256=core.array_hash(values)
    )
    counts = worker.audit()
    actual = n.read_array(tmp_path, spec, counts)
    assert (
        actual.tobytes() == values.tobytes()
        and counts["original_array_reads_completed"] == 1
    )
    with pytest.raises(ValueError, match="One numerical"):
        n.read_array(tmp_path, spec, counts)
    counts = worker.audit()
    spec["input"]["file_sha256"] = "altered"
    monkeypatch.setattr(
        np, "load", lambda *a, **k: pytest.fail("load before file hash")
    )
    with pytest.raises(ValueError, match="identity"):
        n.read_array(tmp_path, spec, counts)
    assert counts["original_array_reads_attempted"] == 0


@pytest.mark.parametrize(
    "key,value",
    [("unknown", True), ("tolerance", 100), ("output", "elsewhere"), ("policy", {})],
)
def test_strict_protocol_unknown_and_overrides(tmp_path, monkeypatch, key, value):
    fixture = {"task": "0023"}
    config = tmp_path / q.CONFIG
    config.parent.mkdir(parents=True)
    monkeypatch.setattr(q, "HASH", p.digest(fixture))
    p.write(config, fixture)
    assert q.load(tmp_path) == fixture
    p.write(config, dict(fixture, **{key: value}))
    with pytest.raises(ValueError, match="Unsupported"):
        q.load(tmp_path)


@pytest.mark.parametrize(
    "key",
    [
        "PYTORCH_MPS_HIGH_WATERMARK_RATIO",
        "PYTORCH_MPS_LOW_WATERMARK_RATIO",
        "PYTORCH_MPS_PREFER_METAL",
    ],
)
def test_no_allocator_operator_search_or_fallback_override(spec, key):
    with pytest.raises(ValueError, match="overrides"):
        q.environment(spec, {key: "1"})
    actual = q.environment(spec, {})
    assert (
        actual["PYTORCH_ENABLE_MPS_FALLBACK"] == actual["PYTORCH_MPS_FAST_MATH"] == "0"
    )


def test_single_exclusive_winner_and_partial_consumption(tmp_path):
    path = tmp_path / q.OUTPUT
    path.parent.mkdir(parents=True)

    def compete(_):
        try:
            q.exclusive(tmp_path, q.OUTPUT)
            return True
        except FileExistsError:
            return False

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(compete, range(8))) == 1
    for state in ("reserved", "partial", "foreign", "inflight", "completed"):
        (path / state).touch()
        with pytest.raises(FileExistsError):
            q.exclusive(tmp_path, q.OUTPUT)


@pytest.mark.parametrize("kind", ["import", "synchronize", "accounting"])
def test_parent_deadline_covers_blocked_native_or_import_and_reaps(
    monkeypatch, tmp_path, kind
):
    def parent(deadline=None):
        if deadline and time.monotonic() > deadline:
            raise TimeoutError("parent deadline")
        return 8 * 2**20

    monkeypatch.setattr(controller, "parent_check", parent)
    command = [
        sys.executable,
        "-c",
        f"import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(20) # blocked {kind}",
    ]
    started = time.monotonic()
    result = controller.supervise(
        command,
        tmp_path / "child.log",
        root=tmp_path,
        environment=os.environ.copy(),
        started=started,
        deadline=started + 2.2,
        stage_seconds=2.2,
    )
    assert (
        result["child_reaped"]
        and result["parent_error"]
        and result["returncode"] == -signal.SIGKILL
    )
    assert result["elapsed_seconds_including_imports_cleanup"] < 2.2


@pytest.mark.parametrize("exit_code", [0, 4])
def test_child_crash_reaped_truthfully(monkeypatch, tmp_path, exit_code):
    monkeypatch.setattr(controller, "parent_check", lambda **_: 8 * 2**20)
    started = time.monotonic()
    result = controller.supervise(
        [sys.executable, "-c", f"raise SystemExit({exit_code})"],
        tmp_path / "child.log",
        root=tmp_path,
        environment=os.environ.copy(),
        started=started,
        deadline=started + 3,
        stage_seconds=3,
    )
    assert result["child_reaped"] and result["returncode"] == exit_code


def test_parent_interruption_closes_owned_process(monkeypatch, tmp_path):
    def interrupt(**_):
        raise KeyboardInterrupt("fixture interruption")

    monkeypatch.setattr(controller, "parent_check", interrupt)
    started = time.monotonic()
    result = controller.supervise(
        [sys.executable, "-c", "import time;time.sleep(20)"],
        tmp_path / "child.log",
        root=tmp_path,
        environment=os.environ.copy(),
        started=started,
        deadline=started + 3,
        stage_seconds=3,
    )
    assert result["child_reaped"] and "KeyboardInterrupt" in result["parent_error"]


def test_unavailable_or_failed_device_stops_before_real_reservation(
    monkeypatch, tmp_path, spec
):
    (tmp_path / q.PROOF).parent.mkdir(parents=True)
    p.write(tmp_path / q.ACCEPTANCE, {})
    monkeypatch.setattr(controller, "parent_check", lambda **_: 8 * 2**20)
    monkeypatch.setattr(controller.sys, "platform", "darwin")
    monkeypatch.setattr(q, "load", lambda _: spec)
    monkeypatch.setattr(q, "software_acceptance", lambda _: dict(source_sha256={}))
    monkeypatch.setattr(q, "metadata", lambda *_: None)
    monkeypatch.setattr(p, "code_context", lambda *_: {})
    monkeypatch.setattr(controller, "fresh_hardware", lambda: {"fixture": True})
    calls = []

    def dispatch(*args, **kwargs):
        calls.append(args[2])
        return dict(
            status="blocked_unavailable", error="MPS unavailable", parent_dispatch={}
        )

    monkeypatch.setattr(controller, "dispatch", dispatch)
    monkeypatch.setattr(controller, "valid", lambda *_: False)
    result = controller.run_automatic(tmp_path)
    assert calls == ["availability"] and result["status"] == "blocked_unavailable"
    assert not result["campaign_reserved"] and not (tmp_path / q.OUTPUT).exists()
    again = controller.run_automatic(tmp_path)
    assert again["status"] == "blocked_before_device_proof" and calls == [
        "availability"
    ]
    assert result["distributions"] == [] and result["paired_ratios"] == []


def test_partial_and_complete_counts_contemporaneous_ratios_only():
    stages = []
    for phase in ("CPU1", "MPS1", "CPU2", "MPS2", "CPU3", "MPS3"):
        cells = []
        kind = "cpu" if phase.startswith("CPU") else "mps"
        for batch in (1, 8, 32, 128, 1024):
            for scope in ("reconstruction", "score_decision", "adapter_decision"):
                times = [20 if kind == "cpu" else 40] * 200
                cells.append(
                    dict(
                        worker=phase,
                        device=kind,
                        batch=batch,
                        scope=scope,
                        status="completed",
                        timed_completed=200,
                        warmups_completed=20,
                        latency_nanoseconds=p.distribution(times, batch),
                    )
                )
        stages.append(dict(cells=cells, empty_timer_pairs_nanoseconds=[1] * 200))
    complete = controller.aggregate(stages)
    assert (
        complete["comparison_success"]
        and complete["counts"]["timed_invocations_completed"] == 18000
    )
    assert len(complete["paired_ratios"]) == 15
    assert all(c["geometric_mean_ratio"] == 0.5 for c in complete["paired_ratios"])
    partial = controller.aggregate(stages[:1])
    assert (
        not partial["comparison_success"]
        and partial["missing_measured_cells"] == 75
        and partial["paired_ratios"] == []
    )
    assert all(c["workers"] == 1 for c in partial["distributions"])


def test_frozen_parameter_clone_preserves_original_scientific_parameters():
    model = synthetic_model()
    before = core.parameter_hash(model)
    cloned = n.transferred_model(model, "cpu")
    assert before == core.parameter_hash(cloned) == core.parameter_hash(model)
    with torch.no_grad():
        next(cloned.parameters()).add_(1)
    assert (
        before == core.parameter_hash(model) and core.parameter_hash(cloned) != before
    )


def test_relu_semantics_are_separately_checked_not_only_output_dtype():
    model = synthetic_model()
    traces = {}
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.ReLU):
            value = np.array([[-1, 0, 1]], np.float32)
            traces[name] = (value, np.maximum(value, 0))
    n.check_relu(model, traces)
    name = next(iter(traces))
    traces[name][1][0, 0] = 0.001
    with pytest.raises(ValueError, match="ReLU"):
        n.check_relu(model, traces)


def test_unsupported_physical_operation_has_no_CPU_fallback():
    a = device.DeviceAccounting()
    fake = NS(mps=api(), float32=torch.float32)
    calls = []

    def unsupported(*args, **kwargs):
        calls.append(kwargs["device"])
        raise NotImplementedError("fixture unsupported MPS operator")

    fake.tensor = unsupported
    with pytest.raises(NotImplementedError, match="unsupported"):
        device.tiny_proof(fake, a, FakeGuard())
    assert calls == ["mps"] and a.status == "active"


def test_pinned_build_refuses_other_runtime(monkeypatch, spec):
    fake = NS(
        backends=NS(
            mps=NS(is_built=lambda: True, is_available=lambda: True, __file__="fixture")
        ),
        mps=NS(__file__="fixture"),
        __config__=NS(show=lambda: "different-build"),
        __version__="fixture",
        version=NS(git_version="fixture"),
    )
    monkeypatch.setattr(p, "file_hash", lambda _: "fixture")
    with pytest.raises(ValueError, match="pinned"):
        device.availability(fake, spec)


def test_unknown_thread_enforcement_is_not_inferred_from_environment(monkeypatch):
    monkeypatch.setattr(core, "threadpool_info", lambda: [dict(num_threads=2)])
    with pytest.raises(ValueError, match="Effective"):
        core.effective_threads()


def test_complete_receipt_with_wrong_device_accounting_not_accepted():
    result = dict(
        task="0023",
        phase="availability",
        source_sha256={},
        protocol_canonical_sha256=q.HASH,
        status="completed",
        optimizer_updates=0,
        test_background_model_access=False,
        test_signal_model_access=False,
        resources=dict(
            latched_error=None,
            owned_thread_alive=False,
            peak_rss_bytes=64 * 2**20,
            native_heap_reserved_bytes=32 * 2**20,
        ),
        parent_dispatch=dict(
            returncode=0, child_reaped=True, deadline_passed=True, parent_error=None
        ),
        device_resources=dict(
            status="active",
            latched_error=None,
            tensor_peak_bytes=None,
            driver_peak_bytes=None,
            samples=1,
        ),
        access_audit=dict(
            population_requests=0, store_custody_requests=0, rows_loaded=0
        ),
        constant_device_proof=dict(status="passed"),
    )
    assert not controller.valid(result, "availability", {})
    result["device_resources"].update(tensor_peak_bytes=12, driver_peak_bytes=1024)
    assert controller.valid(result, "availability", {})
    result["parent_dispatch"]["returncode"] = 3
    assert not controller.valid(result, "availability", {})


def test_atomic_creation_consumes_even_if_reservation_write_fails(
    monkeypatch, tmp_path
):
    (tmp_path / q.PROOF).parent.mkdir(parents=True)
    p.write(tmp_path / q.ACCEPTANCE, {})
    monkeypatch.setattr(
        p, "write", lambda *a, **k: (_ for _ in ()).throw(OSError("interrupted write"))
    )
    monkeypatch.setattr(p, "code_context", lambda *_: {})
    owned = []
    with pytest.raises(OSError):
        controller.make_reservation(
            tmp_path,
            q.PROOF,
            dict(source_sha256={}),
            time.monotonic(),
            on_created=owned.append,
        )
    assert owned == [tmp_path / q.PROOF] and owned[0].exists()
    with pytest.raises(FileExistsError):
        q.exclusive(tmp_path, q.PROOF)


def test_portable_schema_substitution_is_synthetic_not_operational():
    from cpu_mps_portable_plugin import synthetic_document

    config = dict(input=dict(preprocessing_config_sha256="fixture"))
    document, history = synthetic_document(config)
    assert (
        document["scientific"]["provenance"]["processed_scientific_sha256"]
        == "portable_synthetic"
    )
    assert (
        len(history) == 3 and document["scientific"]["training"]["epochs_executed"] == 3
    )
    assert CompactAutoencoder.from_artifact(document).parameter_count == 155


def test_installed_primary_api_bytes_refused_before_actual_device_flags(
    monkeypatch, spec
):
    def unexpected():
        pytest.fail("Flags queried before installed source refusal")

    fake = NS(
        backends=NS(
            mps=NS(is_built=unexpected, is_available=unexpected, __file__="fixture")
        ),
        mps=NS(__file__="fixture"),
    )
    spec["runtime"]["mps_python_api_file_sha256"] = {
        "torch.mps": "expected",
        "torch.backends.mps": "expected",
    }
    monkeypatch.setattr(p, "file_hash", lambda _: "changed")
    with pytest.raises(device.DeviceAdmissionError, match="API bytes") as exc:
        device.availability(fake, spec)
    assert exc.value.evidence["torch.mps"] == "changed"


def test_build_digest_uses_CPU_reference_JSON_convention_and_reports_raw_separately(
    monkeypatch, spec
):
    fake = NS(
        backends=NS(
            mps=NS(
                is_built=lambda: True, is_available=lambda: False, __file__="fixture"
            )
        ),
        mps=NS(__file__="fixture"),
        __config__=NS(show=lambda: "fixture-build"),
        __version__="fixture",
        version=NS(git_version="fixture"),
    )
    monkeypatch.setattr(p, "file_hash", lambda _: "fixture")
    result = device.availability(fake, spec)
    assert result["torch_build_canonical_JSON_sha256"] == p.digest("fixture-build")
    assert result["torch_build_sha256"] == hashlib.sha256(b"fixture-build").hexdigest()
    assert result["torch_build_canonical_JSON_sha256"] != result["torch_build_sha256"]
    assert result["is_available"] is False
