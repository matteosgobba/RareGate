"""Synthetic optional ONNX integration, exact graph/bounds and finite refusal."""

import copy
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from types import SimpleNamespace as NS

import numpy as np
import pytest
import torch
from test_frozen_cpu_benchmark import FakeGuard, sample

from latenttrigger.benchmarks import arithmetic_cpu_v2 as a
from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.guard import Guard, GuardError
from latenttrigger.data.inspection import AGGREGATE_NAMES
from latenttrigger.exports import onnx_controller as c
from latenttrigger.exports import onnx_graph as g
from latenttrigger.exports import onnx_numerics as n
from latenttrigger.exports import onnx_protocol as q
from latenttrigger.exports import onnx_worker as w
from latenttrigger.models.autoencoder import CompactAutoencoder

OPTIONAL = all(
    importlib.util.find_spec(name) is not None
    for name in ("onnx", "onnxruntime", "onnxscript")
)
needs_onnx = pytest.mark.skipif(
    not OPTIONAL,
    reason="optional ONNX export dependencies absent; no physical integration claim",
)


def fixture_model():
    model = CompactAutoencoder().eval()
    with torch.no_grad():
        for i, parameter in enumerate(model.parameters()):
            parameter.copy_(
                (
                    torch.arange(parameter.numel(), dtype=torch.float32).reshape(
                        parameter.shape
                    )
                    + i
                    + 1
                )
                / 256
            )
    return model


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    if not OPTIONAL:
        pytest.skip("Optional integration dependencies absent")
    model = fixture_model()
    root = tmp_path_factory.mktemp("synthetic-onnx")
    path = root / "fixture.onnx"
    before = core.parameter_hash(model)
    request = g.export_reconstruction(model, path)
    on = g.optional_modules()["onnx"]
    document = on.load(path, load_external_data=False)
    manifest, inferred = g.audit_graph(document, model)
    g.diagnostic_copy(inferred, manifest, root / "diagnostic.onnx")
    runtime = g.RuntimeAdapter(path, feature_names=AGGREGATE_NAMES)
    diagnostic = g.RuntimeAdapter(
        root / "diagnostic.onnx", feature_names=AGGREGATE_NAMES, diagnostic=True
    )
    yield NS(
        model=model,
        path=path,
        root=root,
        document=document,
        manifest=manifest,
        runtime=runtime,
        diagnostic=diagnostic,
        request=request,
        before=before,
    )
    runtime.close()
    diagnostic.close()


@needs_onnx
def test_actual_modern_export_graph_initializer_provider_contract(exported):
    assert (
        exported.request["requested_opset"] == 18
        and exported.request["optimize"] is False
    )
    assert (
        "constant_folding" in exported.request
        and exported.request["external_data"] is False
    )
    assert exported.manifest["node_histogram"] == {"Gemm": 4, "Relu": 2}
    assert (
        exported.manifest["learned_parameter_scalars"] == 155
        and exported.manifest["learned_tensor_count"] == 8
    )
    assert exported.manifest[
        "FP32_parameter_mapping_exact"
    ] and exported.before == core.parameter_hash(exported.model)
    assert exported.runtime.provenance["selected_providers"] == ["CPUExecutionProvider"]
    assert exported.runtime.provenance["provider_fallback_disabled"]
    assert (
        exported.runtime.provenance["intra_op_threads"]
        == exported.runtime.provenance["inter_op_threads"]
        == 1
    )
    assert not list(exported.root.glob("*.data"))


@needs_onnx
@pytest.mark.parametrize("batch", [1, 8, 32, 128, 1024])
def test_dynamic_batch_actual_runtime_diagnostic_and_own_SSE(batch, exported):
    x = np.ones((batch, 8), np.float32)
    r = exported.runtime.reconstruct(x, feature_names=AGGREGATE_NAMES)
    repeat = exported.runtime.reconstruct(x, feature_names=AGGREGATE_NAMES)
    trace = exported.diagnostic.intermediates(x, feature_names=AGGREGATE_NAMES)
    assert (
        r.shape == (batch, 8)
        and r.dtype == np.float32
        and r.tobytes() == repeat.tobytes() == trace["reconstruction"].tobytes()
    )
    score = exported.runtime.score(x, feature_names=AGGREGATE_NAMES)
    separate, _ = core.separated(x, r, np.array([1, 2, 3, 4.0]))
    assert score.dtype == np.float64 and score.tobytes() == separate.tobytes()


@needs_onnx
@pytest.mark.parametrize(
    "failure",
    [
        "feature_order",
        "FP64",
        "rank",
        "width",
        "empty",
        "unsupported_batch",
        "nan",
        "inf",
    ],
)
def test_runtime_refuses_bad_inputs_before_provider_run(exported, monkeypatch, failure):
    x = np.ones((8, 8), np.float32)
    features = AGGREGATE_NAMES
    if failure == "feature_order":
        features = features[::-1]
    elif failure == "FP64":
        x = x.astype(np.float64)
    elif failure == "rank":
        x = x.reshape(64)
    elif failure == "width":
        x = x[:, :7]
    elif failure == "empty":
        x = x[:0]
    elif failure == "unsupported_batch":
        x = x[:2]
    else:
        x[0, 0] = np.nan if failure == "nan" else np.inf
    monkeypatch.setattr(
        exported.runtime.session,
        "run",
        lambda *a, **k: pytest.fail("Provider called before input refusal"),
    )
    with pytest.raises(ValueError):
        exported.runtime.reconstruct(x, feature_names=features)


@needs_onnx
@pytest.mark.parametrize(
    "kind",
    [
        "custom_domain",
        "unexpected_node",
        "wrong_weight",
        "FP64_weight",
        "extra_initializer",
        "external_data",
        "wrong_shape",
        "wrong_opset",
        "changed_alpha",
        "missing_relu",
    ],
)
def test_graph_exact_refusal(exported, kind):
    on = g.optional_modules()["onnx"]
    doc = copy.deepcopy(exported.document)
    if kind == "custom_domain":
        doc.graph.node[0].domain = "foreign"
    elif kind == "unexpected_node":
        doc.graph.node[0].op_type = "Sigmoid"
    elif kind == "wrong_weight":
        arr = on.numpy_helper.to_array(doc.graph.initializer[0]).copy()
        arr.flat[0] += 1
        doc.graph.initializer[0].CopyFrom(
            on.numpy_helper.from_array(arr, doc.graph.initializer[0].name)
        )
    elif kind == "FP64_weight":
        doc.graph.initializer[0].data_type = on.TensorProto.DOUBLE
    elif kind == "extra_initializer":
        doc.graph.initializer.append(
            on.numpy_helper.from_array(np.array([1], np.float32), "foreign")
        )
    elif kind == "external_data":
        doc.graph.initializer[0].data_location = on.TensorProto.EXTERNAL
        doc.graph.initializer[0].external_data.add(key="location", value="foreign.data")
    elif kind == "wrong_shape":
        doc.graph.input[0].type.tensor_type.shape.dim[1].dim_value = 7
    elif kind == "wrong_opset":
        doc.opset_import[0].version = 19
    elif kind == "changed_alpha":
        for attr in doc.graph.node[0].attribute:
            if attr.name == "alpha":
                attr.f = 2
    elif kind == "missing_relu":
        doc.graph.node[1].op_type = "Identity"
    with pytest.raises(
        (ValueError, on.checker.ValidationError, on.shape_inference.InferenceError)
    ):
        g.audit_graph(doc, exported.model)


@needs_onnx
def test_exact_initializer_transpose_layout_is_permitted(exported):
    on = g.optional_modules()["onnx"]
    doc = copy.deepcopy(exported.document)
    for node in doc.graph.node:
        if node.op_type != "Gemm":
            continue
        name = node.input[1]
        tensor = next(t for t in doc.graph.initializer if t.name == name)
        tensor.CopyFrom(
            on.numpy_helper.from_array(on.numpy_helper.to_array(tensor).T.copy(), name)
        )
        for value in doc.graph.value_info:
            if value.name == name:
                dims = value.type.tensor_type.shape.dim
                first, second = dims[0].dim_value, dims[1].dim_value
                dims[0].dim_value, dims[1].dim_value = second, first
        for attr in node.attribute:
            if attr.name == "transB":
                attr.i = 0
    manifest, _ = g.audit_graph(doc, exported.model)
    assert (
        manifest["FP32_parameter_mapping_exact"]
        and manifest["learned_parameter_scalars"] == 155
    )


@needs_onnx
def test_equivalent_MatMul_Add_Transpose_representation_is_audited(exported):
    on = g.optional_modules()["onnx"]
    doc = copy.deepcopy(exported.document)
    nodes = []
    for node in doc.graph.node:
        if node.op_type != "Gemm":
            nodes.append(copy.deepcopy(node))
            continue
        x, weight, bias = node.input
        y = node.output[0]
        transpose = weight + "_transpose"
        mm = y + "_matmul"
        nodes.extend(
            [
                on.helper.make_node("Transpose", [weight], [transpose], perm=[1, 0]),
                on.helper.make_node("MatMul", [x, transpose], [mm]),
                on.helper.make_node("Add", [mm, bias], [y]),
            ]
        )
    del doc.graph.node[:]
    doc.graph.node.extend(nodes)
    manifest, _ = g.audit_graph(doc, exported.model)
    assert manifest["node_histogram"] == dict(Transpose=4, MatMul=4, Add=4, Relu=2)


@needs_onnx
@pytest.mark.parametrize("family", ["constants", "powers", "uniform", "normal"])
def test_actual_synthetic_complete_grid_local_and_decision_equivalence(
    exported, family
):
    from latenttrigger.benchmarks.ae_parity_numerics import families

    result = n.verify(
        exported.model,
        exported.runtime,
        exported.diagnostic,
        exported.manifest,
        families()[family],
        np.array([1.0, 2.0, 3.0, 4.0]),
        AGGREGATE_NAMES,
        FakeGuard(),
        w.counts(),
    )
    assert (
        result["status"] == "passed"
        and result["windows_verified"] == 1193
        and result["row_window_presentations"] == 5120
    )
    assert (
        result["decision_mismatches"] == [0] * 4
        and result["local_affine_violations"] == 0
    )
    assert result["hashes_before"] == result["hashes_after"]
    assert all(
        g["same_runtime_repeat_byte_exact"] and g["diagnostic_primary_final_byte_exact"]
        for g in result["grids"]
    )


@pytest.mark.parametrize("missing", ["onnx", "onnxruntime", "onnxscript"])
def test_optional_absence_factual_lazy_failure(monkeypatch, missing):

    def imported(name):
        if name == missing:
            raise ImportError("synthetic missing " + name)
        return NS()

    monkeypatch.setattr(g.importlib, "import_module", imported)
    with pytest.raises(RuntimeError, match="Optional"):
        g.optional_modules()


def test_controller_and_graph_imports_stay_lazy_in_fresh_process(tmp_path):
    code = 'import sys;import latenttrigger.exports.onnx_controller;import latenttrigger.exports.onnx_graph;assert not any(x in sys.modules for x in ("numpy","torch","onnx","onnxruntime","onnxscript"))'
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=dict(os.environ, PYTHONPATH=str(q.ROOT / "src")),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("dimension", [3, 6, 8])
def test_gamma_and_local_affine_bound_cover_exact_rational_rounding(dimension):
    m = 2 * dimension + 2
    u = Fraction(1, 2**24)
    assert Fraction(float(a.gamma(m, a.U32))) >= m * u / (1 - m * u)
    x = np.full((1, dimension), 0.1)
    weight = np.full((1, dimension), -0.2)
    bias = np.array([0.3])
    bound = a.local_affine_bound(x, weight, bias)
    magnitude = sum(
        abs(Fraction(float(x[0, i])) * Fraction(float(weight[0, i])))
        for i in range(dimension)
    ) + abs(Fraction(0.3))
    exact = (
        Fraction(m) * u / (1 - Fraction(m) * u)
        + Fraction(m, 2**53) / (1 - Fraction(m, 2**53))
    ) * magnitude
    assert Fraction(float(bound[0, 0])) >= exact


def test_cancellation_and_rounded_FP64_SSE_allowance_not_just_final_ulp():
    x = np.array([[1.0, 2**-24, -1.0, -(2**-24), 0, 0, 0, 0]])
    upper = a.magnitude(x, np.ones((1, 8)), np.array([0.0]))
    assert upper[0, 0] >= 2 + 2**-23
    values = np.zeros((2, 8), np.float32)
    reference = np.ones((2, 8), np.float32)
    d = np.full((2, 8), 2**-20)
    s = np.full(2, 8.0)
    bound, propagation, evaluation = a.sse_difference_bound(values, reference, d, s, s)
    exact = Fraction(2) * 8 * Fraction(1, 2**20) + 8 * Fraction(1, 2**40)
    assert (
        Fraction(float(propagation[0])) >= exact
        and evaluation[0] > 0
        and bound[0] > propagation[0]
    )


def test_same_runtime_SSE_tie_and_near_threshold_strict_decisions():
    theta = np.array([1.0, 2.0, 3.0, 4.0])
    score = np.array([1.0, np.nextafter(1.0, np.inf), np.nextafter(1.0, 0.0)])
    assert core.decisions(score, theta)[:, 0].tolist() == [False, True, False]
    with pytest.raises(core.NumericalError):
        core.verify_decisions(score, np.ones(3), theta, "near_threshold")


@pytest.mark.parametrize("kind", ["unknown", "opset", "path", "epsilon"])
def test_strict_protocol_refuses_arbitrary_overrides(tmp_path, monkeypatch, kind):
    fixture = {"task": "0024"}
    path = tmp_path / q.CONFIG
    path.parent.mkdir(parents=True)
    p.write(path, fixture)
    monkeypatch.setattr(q, "HASH", p.digest(fixture))
    assert q.load(tmp_path) == fixture
    p.write(path, dict(fixture, **{kind: "unsafe"}))
    with pytest.raises(ValueError, match="Unsupported"):
        q.load(tmp_path)


@pytest.mark.parametrize(
    "selector",
    [
        "processed/full",
        "processed/dev/test_background",
        "processed/dev/test_signal",
        "truth",
        "labels",
    ],
)
def test_no_unsafe_input_open_before_refusal(tmp_path, selector, monkeypatch):
    spec = dict(input=dict(path=selector))
    access = dict(array_read_attempts=0, synthetic_admitted=True)
    monkeypatch.setattr(
        np, "load", lambda *a, **k: pytest.fail("Real open before scope refusal")
    )
    with pytest.raises(ValueError, match="Only original"):
        w.open_real(tmp_path, spec, access)
    assert access["array_read_attempts"] == 0


def test_real_input_header_identity_and_one_read_after_synthetic(tmp_path, monkeypatch):
    name = "results/benchmarks/task0020-frozen-cpu/prepare/input.npy"
    path = tmp_path / name
    path.parent.mkdir(parents=True)
    values = np.ones((1024, 8), np.float32)
    np.save(path, values, allow_pickle=False)
    spec = dict(
        input=dict(
            path=name,
            file_sha256=p.file_hash(path),
            array_bytes_sha256=core.array_hash(values),
        )
    )
    access = dict(array_read_attempts=0, synthetic_admitted=False)
    with pytest.raises(ValueError, match="synthetic"):
        w.open_real(tmp_path, spec, access)
    access.update(synthetic_admitted=True, array_reads_completed=0)
    actual = w.open_real(tmp_path, spec, access)
    assert actual.tobytes() == values.tobytes() and access["array_reads_completed"] == 1
    with pytest.raises(ValueError, match="One real"):
        w.open_real(tmp_path, spec, access)
    access["array_read_attempts"] = 0
    spec["input"]["file_sha256"] = "changed"
    monkeypatch.setattr(
        np, "load", lambda *a, **k: pytest.fail("open before file/hash refusal")
    )
    with pytest.raises(ValueError, match="identity"):
        w.open_real(tmp_path, spec, access)


def test_exclusive_competing_reservations_preserve_foreign_partial(tmp_path):
    (tmp_path / q.OUTPUT).parent.mkdir(parents=True)

    def attempt(_):
        try:
            q.fixed(tmp_path, q.OUTPUT).mkdir()
            return True
        except FileExistsError:
            return False

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(attempt, range(8))) == 1
    for state in ("partial", "foreign", "inflight", "completed"):
        (tmp_path / q.OUTPUT / state).touch()
        with pytest.raises(FileExistsError):
            q.fixed(tmp_path, q.OUTPUT).mkdir()


@pytest.mark.parametrize(
    "key,limit",
    [("peak_rss_bytes", 1073741824), ("native_heap_reserved_bytes", 536870912)],
)
@pytest.mark.parametrize("extra", [0, 1])
def test_exact_caps_and_failed_peaks_preserved(key, limit, extra):
    guard = Guard(
        time.monotonic() + 1, probe=lambda: sample(**{key: limit + extra}), notify=False
    )
    if extra:
        with pytest.raises(GuardError):
            guard.check()
    else:
        guard.check()
    assert guard.report()[key] == limit + extra


@pytest.mark.parametrize(
    "flags,errno,valid",
    [
        (1, None, True),
        (2, None, True),
        (None, 1, True),
        (4, None, False),
        (7, None, False),
    ],
)
def test_pressure_advisory_unknown_critical_malformed(flags, errno, valid):
    guard = Guard(
        time.monotonic() + 1,
        probe=lambda: sample(pressure_dispatch_flags=flags, pressure_errno=errno),
        notify=False,
    )
    if valid:
        guard.check()
    else:
        with pytest.raises(GuardError):
            guard.check()


@pytest.mark.parametrize("operation", ["import", "export", "runtime"])
def test_blocked_native_parent_deadline_terminates_and_reaps(
    tmp_path, monkeypatch, operation
):
    def check(deadline=None):
        if deadline and time.monotonic() > deadline:
            raise TimeoutError("parent deadline")
        return 8 * 2**20

    monkeypatch.setattr(c, "parent_check", check)
    code = (
        "import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(20)"
    )
    directory = tmp_path
    started = time.monotonic()
    result = c.supervise(
        [sys.executable, "-c", code],
        directory,
        os.environ.copy(),
        tmp_path,
        started,
        "synthetic",
        wall_seconds=2.2,
    )
    assert (
        result["child_reaped"]
        and result["parent_error"]
        and result["returncode"] == -signal.SIGKILL
    )


@pytest.mark.parametrize("code", [0, 3])
def test_native_child_exit_reaped_truthfully(tmp_path, monkeypatch, code):
    monkeypatch.setattr(c, "parent_check", lambda **_: 8 * 2**20)
    result = c.supervise(
        [sys.executable, "-c", f"raise SystemExit({code})"],
        tmp_path,
        os.environ.copy(),
        tmp_path,
        time.monotonic(),
        "fixture",
        wall_seconds=3,
    )
    assert result["child_reaped"] and result["returncode"] == code


def test_build_string_JSON_hash_and_raw_text_are_different_contracts():
    raw = "fixture build\n"
    text = hashlib.sha256(raw.encode()).hexdigest()
    canonical = p.digest(raw)
    assert (
        canonical != text
        and canonical
        == hashlib.sha256(json.dumps(raw, separators=(",", ":")).encode()).hexdigest()
    )


@needs_onnx
def test_critical_primary_diagnostic_mismatch_stops_before_numeric_claim(
    exported, monkeypatch
):
    original = exported.diagnostic.intermediates

    def changed(*args, **kwargs):
        trace = original(*args, **kwargs)
        trace["reconstruction"][0, 0] += 1
        return trace

    monkeypatch.setattr(exported.diagnostic, "intermediates", changed)
    with pytest.raises(a.ArithmeticFailure, match="diagnostic_primary"):
        n.verify(
            exported.model,
            exported.runtime,
            exported.diagnostic,
            exported.manifest,
            np.ones((1024, 8), np.float32),
            np.array([1.0, 2.0, 3.0, 4.0]),
            AGGREGATE_NAMES,
            FakeGuard(),
            w.counts(),
        )


@needs_onnx
def test_same_runtime_nondeterminism_is_critical(exported, monkeypatch):
    original = exported.runtime.reconstruct
    calls = [0]

    def unstable(*args, **kwargs):
        output = original(*args, **kwargs)
        calls[0] += 1
        if calls[0] % 2 == 0:
            output[0, 0] += 1
        return output

    monkeypatch.setattr(exported.runtime, "reconstruct", unstable)
    with pytest.raises(a.ArithmeticFailure, match="ORT_same_shape_repeat"):
        n.verify(
            exported.model,
            exported.runtime,
            exported.diagnostic,
            exported.manifest,
            np.ones((1024, 8), np.float32),
            np.array([1.0, 2.0, 3.0, 4.0]),
            AGGREGATE_NAMES,
            FakeGuard(),
            w.counts(),
        )


@needs_onnx
def test_supported_bound_failure_retains_complete_grid_and_failed_status(
    exported, monkeypatch
):
    original = n._bound

    def refused(*args, **kwargs):
        record = original(*args, **kwargs)
        if record["comparison"] == "ORT_vs_PyTorch1024_reconstruction":
            record.update(passed=False, violations=1)
        return record

    monkeypatch.setattr(n, "_bound", refused)
    result = n.verify(
        exported.model,
        exported.runtime,
        exported.diagnostic,
        exported.manifest,
        np.ones((1024, 8), np.float32),
        np.array([1.0, 2.0, 3.0, 4.0]),
        AGGREGATE_NAMES,
        FakeGuard(),
        w.counts(),
    )
    assert (
        result["status"] == "failed"
        and result["windows_verified"] == 1193
        and len(result["grids"]) == 5
    )
    assert all(row["status"] == "failed" for row in result["grids"])


@needs_onnx
def test_parameter_mutation_cannot_restore_success(exported, monkeypatch):
    model = copy.deepcopy(exported.model)
    original = exported.runtime.reconstruct
    calls = [0]

    def mutate(*args, **kwargs):
        output = original(*args, **kwargs)
        calls[0] += 1
        if calls[0] == 3:
            with torch.no_grad():
                next(model.parameters()).add_(0.125)
        return output

    monkeypatch.setattr(exported.runtime, "reconstruct", mutate)
    with pytest.raises(ValueError, match="restored_|mutation"):
        n.verify(
            model,
            exported.runtime,
            exported.diagnostic,
            exported.manifest,
            np.ones((1024, 8), np.float32),
            np.array([1.0, 2.0, 3.0, 4.0]),
            AGGREGATE_NAMES,
            FakeGuard(),
            w.counts(),
        )


@pytest.mark.parametrize(
    "bad", ["provider", "intra_threads", "inter_threads", "optimization", "fallback"]
)
def test_effective_runtime_not_inferred_from_requested_options(monkeypatch, bad):
    options = NS()
    effective = NS(
        execution_mode=1,
        intra_op_num_threads=1,
        inter_op_num_threads=1,
        graph_optimization_level=0,
    )
    if bad == "intra_threads":
        effective.intra_op_num_threads = 2
    if bad == "inter_threads":
        effective.inter_op_num_threads = 2
    if bad == "optimization":
        effective.graph_optimization_level = 3
    session = NS(
        get_session_options=lambda: effective,
        get_providers=lambda: (
            ["CPUExecutionProvider", "CoreMLExecutionProvider"]
            if bad == "provider"
            else ["CPUExecutionProvider"]
        ),
        disable_fallback=(None if bad == "fallback" else lambda: None),
    )
    fake = NS(
        SessionOptions=lambda: options,
        ExecutionMode=NS(ORT_SEQUENTIAL=1),
        GraphOptimizationLevel=NS(ORT_DISABLE_ALL=0),
        InferenceSession=lambda *a, **k: session,
    )
    monkeypatch.setattr(g, "optional_modules", lambda: {"onnxruntime": fake})
    with pytest.raises(ValueError, match="Effective|fallback"):
        g.RuntimeAdapter("synthetic", feature_names=AGGREGATE_NAMES)


def test_feature_order_refused_before_any_session_construction(monkeypatch):
    monkeypatch.setattr(
        g,
        "optional_modules",
        lambda: pytest.fail("Optional imports before feature refusal"),
    )
    with pytest.raises(ValueError, match="feature order"):
        g.RuntimeAdapter("synthetic", feature_names=AGGREGATE_NAMES[::-1])


def test_frozen_source_mismatch_refused_before_old_metadata_or_input(
    tmp_path, monkeypatch
):
    path = tmp_path / "synthetic.py"
    path.write_text("changed\n")
    spec = dict(
        historical_source_file_sha256={"synthetic.py": "expected"},
        historical_file_sha256={},
        prerequisite_files={},
    )
    monkeypatch.setattr(
        q.old, "metadata", lambda *a: pytest.fail("Old metadata after source refusal")
    )
    with pytest.raises(ValueError, match="historical identity"):
        q.frozen_metadata(tmp_path, spec)


def test_parent_interruption_owns_cleanup_and_reaping(tmp_path, monkeypatch):
    def interrupt(**kwargs):
        raise KeyboardInterrupt("synthetic user interruption")

    monkeypatch.setattr(c, "parent_check", interrupt)
    result = c.supervise(
        [sys.executable, "-c", "import time;time.sleep(20)"],
        tmp_path,
        os.environ.copy(),
        tmp_path,
        time.monotonic(),
        "fixture",
        wall_seconds=3,
    )
    assert result["child_reaped"] and "KeyboardInterrupt" in result["parent_error"]


def test_partial_worker_never_claims_equivalence_success():
    result = dict(
        task="0024",
        status="failed",
        source_file_sha256={},
        protocol_canonical_JSON_sha256=q.HASH,
    )
    dispatch = dict(
        returncode=1, parent_error=None, child_reaped=True, deadline_passed=True
    )
    assert not c.valid(result, dispatch, {})
