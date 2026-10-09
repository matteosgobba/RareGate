"""Lazy optional modern exporter, graph/initializer audit and CPU runtime adapter."""

import copy
import importlib
import inspect
from collections import Counter


def optional_modules():
    try:
        return {
            name: importlib.import_module(name)
            for name in ("onnx", "onnxruntime", "onnxscript")
        }
    except ImportError as exc:
        raise RuntimeError(
            "Optional export dependencies absent; install supported export extra before admission."
        ) from exc


def export_reconstruction(model, path):
    import torch

    from latenttrigger.benchmarks import core

    modules = optional_modules()
    signature = inspect.signature(torch.onnx.export)
    if "fallback" in signature.parameters or not all(
        n in signature.parameters for n in ("dynamo", "optimize", "external_data")
    ):
        raise ValueError("Unsupported modern exporter API; no legacy retry.")
    if (
        path.exists()
        or model.training
        or model.parameter_count != 155
        or any(
            p.dtype != torch.float32 or p.device.type != "cpu"
            for p in model.parameters()
        )
    ):
        raise ValueError("Exclusive new export and frozen eval155 FP32 CPU required.")
    before = core.parameter_hash(model)
    example = torch.ones((8, 8), dtype=torch.float32, device="cpu")
    program = torch.export.export(
        model,
        (example,),
        dynamic_shapes={"values": {0: torch.export.Dim("batch", min=1, max=1024)}},
        strict=False,
    )
    exported = torch.onnx.export(
        program,
        f=path,
        dynamo=True,
        input_names=["event_features"],
        output_names=["reconstruction"],
        opset_version=18,
        external_data=False,
        optimize=False,
        verify=False,
        report=False,
        profile=False,
        dump_exported_program=False,
        export_params=True,
        keep_initializers_as_inputs=False,
        artifacts_dir=str(path.parent),
    )
    if core.parameter_hash(model) != before:
        raise ValueError("Export mutated canonical parameters.")
    if not path.is_file() or path.stat().st_size > 1048576:
        raise ValueError("Missing/unbounded primary ONNX export.")
    return dict(
        capture="explicit_torch.export.export_strict=False_single_capture;modern_dynamo=True_ONNXProgram_no_legacy_retry",
        dynamic_constraints=str(program.range_constraints),
        example_shape=[8, 8],
        requested_opset=18,
        optimize=False,
        constant_folding="exporter_transformations_not_disabled_by_optimize=False",
        external_data=False,
        parameters_preserved=True,
        onnx_version=modules["onnx"].__version__,
        ONNXProgram_type=type(exported).__name__,
    )


def _attributes(node, onnx):
    return {v.name: onnx.helper.get_attribute_value(v) for v in node.attribute}


def _bytes_equal(actual, expected):
    return (
        actual.shape == expected.shape
        and actual.dtype == expected.dtype
        and actual.tobytes() == expected.tobytes()
    )


def audit_graph(document, model):
    import numpy as np
    import torch

    onnx = optional_modules()["onnx"]
    onnx.checker.check_model(document, full_check=True)
    if document.graph.sparse_initializer or document.training_info:
        raise ValueError("Sparse/training graph unsupported.")
    imports = {x.domain: x.version for x in document.opset_import}
    if imports.get("", imports.get("ai.onnx")) != 18:
        raise ValueError("Only preregistered opset18.")
    if len(document.graph.input) != 1 or len(document.graph.output) != 1:
        raise ValueError(
            "Only one reconstruction input/output; no embedded score/scaler."
        )
    expected_names = ("event_features", "reconstruction")
    for value, name in zip(
        (*document.graph.input, *document.graph.output), expected_names, strict=True
    ):
        kind = value.type.tensor_type
        dims = kind.shape.dim
        if (
            value.name != name
            or kind.elem_type != onnx.TensorProto.FLOAT
            or len(dims) != 2
            or not dims[0].dim_param
            or dims[0].HasField("dim_value")
            or dims[1].dim_value != 8
            or dims[1].dim_param
        ):
            raise ValueError(
                "FP32 dynamic batch/fixed-width8 names/types/shapes required."
            )
    if (
        document.graph.input[0].type.tensor_type.shape.dim[0].dim_param
        != document.graph.output[0].type.tensor_type.shape.dim[0].dim_param
    ):
        raise ValueError("Input/output batch symbols differ.")
    initializers = {}
    for tensor in document.graph.initializer:
        if (
            tensor.name in initializers
            or tensor.data_type != onnx.TensorProto.FLOAT
            or tensor.data_location == onnx.TensorProto.EXTERNAL
            or tensor.external_data
        ):
            raise ValueError("Duplicate/non-FP32/external initializer refusal.")
        array = onnx.numpy_helper.to_array(tensor).copy()
        if array.dtype != np.float32 or not np.isfinite(array).all():
            raise ValueError("Invalid learned tensor.")
        initializers[tensor.name] = array
    if len(initializers) != 8 or sum(x.size for x in initializers.values()) != 155:
        raise ValueError("Exactly eight learned tensors/155 FP32 scalars required.")
    layers = [
        (name, layer)
        for name, layer in model.named_modules()
        if isinstance(layer, torch.nn.Linear)
    ]
    if [(m.in_features, m.out_features) for _, m in layers] != [
        (8, 6),
        (6, 3),
        (3, 6),
        (6, 8),
    ]:
        raise ValueError("Frozen affine topology mismatch.")
    constants = {name: (value, {name}) for name, value in initializers.items()}
    current = "event_features"
    stage = 0
    await_relu = False
    pending = None
    manifest = []
    used = set()
    histogram = Counter()
    defined = set(initializers) | {current}

    def parameter(name):
        if name not in constants:
            raise ValueError("Unresolved/nonconstant affine parameter.")
        return constants[name]

    def affine(output, weight, bias, origins):
        nonlocal current, stage, await_relu
        if stage >= 4 or await_relu:
            raise ValueError("Extra affine/missing ReLU.")
        name, layer = layers[stage]
        w = layer.weight.detach().numpy()
        b = layer.bias.detach().numpy()
        if not _bytes_equal(weight, w) or not _bytes_equal(bias, b):
            raise ValueError("Original FP32 weights/bias mapping mismatch at " + name)
        manifest.append(
            dict(
                kind="affine",
                layer=name,
                input=current,
                output=output,
                input_width=layer.in_features,
                output_width=layer.out_features,
                parameter_origins=sorted(origins),
                weight_shape=list(w.shape),
                bias_shape=list(b.shape),
            )
        )
        used.update(origins)
        current = output
        stage += 1
        await_relu = stage in (1, 3)

    for node in document.graph.node:
        if (
            node.domain not in ("", "ai.onnx")
            or node.op_type
            not in ("Gemm", "MatMul", "Add", "Transpose", "Relu", "Identity")
            or len(node.output) != 1
            or not node.output[0]
            or node.output[0] in defined
            or any(name not in defined for name in node.input)
        ):
            raise ValueError("Unexpected custom/topology/operator/dependency.")
        attrs = _attributes(node, onnx)
        out = node.output[0]
        histogram[node.op_type] += 1
        if node.op_type in ("Transpose", "Identity") and node.input[0] in constants:
            array, origin = parameter(node.input[0])
            if node.op_type == "Transpose":
                if attrs != {"perm": [1, 0]} or array.ndim != 2:
                    raise ValueError("Only parameter matrix transpose.")
                array = array.T.copy()
            elif attrs:
                raise ValueError("Unexpected Identity attribute.")
            constants[out] = (array, origin)
        elif node.op_type == "Gemm":
            if (
                pending
                or len(node.input) != 3
                or node.input[0] != current
                or attrs.get("alpha", 1.0) != 1.0
                or attrs.get("beta", 1.0) != 1.0
                or attrs.get("transA", 0) != 0
                or attrs.get("transB", 0) not in (0, 1)
                or set(attrs) - {"alpha", "beta", "transA", "transB"}
            ):
                raise ValueError("Unsupported affine Gemm semantics.")
            weight, origin = parameter(node.input[1])
            bias, bias_origin = parameter(node.input[2])
            affine(
                out,
                weight if attrs.get("transB", 0) else weight.T,
                bias,
                origin | bias_origin,
            )
        elif node.op_type == "MatMul":
            if (
                pending
                or await_relu
                or len(node.input) != 2
                or node.input[0] != current
                or attrs
            ):
                raise ValueError("Unsupported MatMul branch.")
            weight, origin = parameter(node.input[1])
            pending = (out, weight.T, origin)
        elif node.op_type == "Add":
            if (
                pending is None
                or len(node.input) != 2
                or attrs
                or pending[0] not in node.input
            ):
                raise ValueError("Only affine MatMul+bias Add.")
            bias_name = node.input[1] if node.input[0] == pending[0] else node.input[0]
            bias, bias_origin = parameter(bias_name)
            affine(out, pending[1], bias, pending[2] | bias_origin)
            pending = None
        elif node.op_type == "Relu":
            if (
                not await_relu
                or pending
                or len(node.input) != 1
                or node.input[0] != current
                or attrs
            ):
                raise ValueError("ReLU topology mismatch.")
            manifest.append(dict(kind="relu", input=current, output=out))
            current = out
            await_relu = False
        elif node.op_type == "Identity":
            if len(node.input) != 1 or node.input[0] != current or attrs or pending:
                raise ValueError("Activation identity topology mismatch.")
            manifest.append(dict(kind="identity", input=current, output=out))
            current = out
        else:
            raise ValueError("Unsupported topology/transpose on activations.")
        defined.add(out)
    if (
        stage != 4
        or await_relu
        or pending
        or current != "reconstruction"
        or used != set(initializers)
        or sum(m["kind"] == "relu" for m in manifest) != 2
    ):
        raise ValueError("Incomplete reconstruction/frozen initializer coverage.")
    # All invoked operators are standard. Unreachable function declarations are
    # metadata, not execution/provider dependencies; checker validates them.
    inferred = onnx.shape_inference.infer_shapes(
        document, strict_mode=True, data_prop=True
    )
    return dict(
        status="passed",
        opset_imports=imports,
        IR_version=document.ir_version,
        input_name="event_features",
        output_name="reconstruction",
        batch_symbol=document.graph.input[0].type.tensor_type.shape.dim[0].dim_param,
        node_histogram=dict(histogram),
        topology=manifest,
        learned_parameter_scalars=155,
        learned_tensor_count=8,
        FP32_parameter_mapping_exact=True,
        external_data=False,
        unused_function_declarations=[
            dict(domain=f.domain, name=f.name) for f in document.functions
        ],
        initializer_manifest=[
            dict(
                name=name,
                shape=list(value.shape),
                dtype="float32",
                payload_byte_sha256=__import__("hashlib")
                .sha256(value.tobytes())
                .hexdigest(),
            )
            for name, value in initializers.items()
        ],
    ), inferred


def diagnostic_copy(document, manifest, path):
    onnx = optional_modules()["onnx"]
    diagnostic = copy.deepcopy(document)
    names = {
        v.name: v
        for v in (
            *document.graph.input,
            *document.graph.output,
            *document.graph.value_info,
        )
    }
    existing = {v.name for v in diagnostic.graph.output}
    for row in manifest["topology"]:
        for name in (row["input"], row["output"]):
            if name in existing:
                continue
            if name not in names:
                raise ValueError("Missing inferred intermediate type/shape.")
            diagnostic.graph.output.append(copy.deepcopy(names[name]))
            existing.add(name)
    onnx.checker.check_model(diagnostic, full_check=True)
    if path.exists():
        raise ValueError("Exclusive diagnostic artifact required.")
    onnx.save_model(diagnostic, path, save_as_external_data=False)
    return diagnostic


class RuntimeAdapter:
    """Primary CPU-only reconstruction, external canonical FP64 score adapter."""

    def __init__(self, path, *, feature_names, diagnostic=False):
        from latenttrigger.data.inspection import AGGREGATE_NAMES

        if tuple(feature_names) != AGGREGATE_NAMES:
            raise ValueError(
                "Frozen canonical feature order required before session construction."
            )
        self.features = tuple(feature_names)
        self.diagnostic = diagnostic
        ort = optional_modules()["onnxruntime"]
        options = ort.SessionOptions()
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.intra_op_num_threads = options.inter_op_num_threads = 1
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        self.session = ort.InferenceSession(
            str(path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        if not callable(getattr(self.session, "disable_fallback", None)):
            raise ValueError("Provider fallback control unavailable.")
        self.session.disable_fallback()
        effective = self.session.get_session_options()
        if (
            self.session.get_providers() != ["CPUExecutionProvider"]
            or effective.execution_mode != ort.ExecutionMode.ORT_SEQUENTIAL
            or effective.intra_op_num_threads != 1
            or effective.inter_op_num_threads != 1
            or effective.graph_optimization_level
            != ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        ):
            raise ValueError(
                "Effective CPU provider/thread/optimization requirements failed."
            )
        if (
            len(self.session.get_inputs()) != 1
            or self.session.get_inputs()[0].name != "event_features"
            or self.session.get_inputs()[0].type != "tensor(float)"
            or self.session.get_inputs()[0].shape[1] != 8
            or not isinstance(self.session.get_inputs()[0].shape[0], str)
        ):
            raise ValueError("Runtime input signature mismatch.")
        self.names = [o.name for o in self.session.get_outputs()]
        if self.names[0] != "reconstruction" or (
            not diagnostic and len(self.names) != 1
        ):
            raise ValueError("Runtime reconstruction outputs mismatch.")
        self.provenance = dict(
            available_providers=ort.get_available_providers(),
            selected_providers=self.session.get_providers(),
            execution_mode="ORT_SEQUENTIAL",
            intra_op_threads=effective.intra_op_num_threads,
            inter_op_threads=effective.inter_op_num_threads,
            graph_optimization="ORT_DISABLE_ALL",
            provider_fallback_disabled=True,
            ort_version=ort.__version__,
        )

    def validate(self, values, feature_names):
        import numpy as np

        if (
            tuple(feature_names) != self.features
            or not isinstance(values, np.ndarray)
            or values.dtype != np.float32
            or values.ndim != 2
            or values.shape[1] != 8
            or values.shape[0] not in (1, 8, 32, 128, 1024)
            or not np.isfinite(values).all()
        ):
            raise ValueError(
                "Frozen feature order/FP32 finite supported batch[B,8] required."
            )

    def reconstruct(self, values, *, feature_names):
        import numpy as np

        self.validate(values, feature_names)
        output = self.session.run(None, {"event_features": values})[0]
        if (
            output.dtype != np.float32
            or output.shape != values.shape
            or not np.isfinite(output).all()
        ):
            raise ValueError("Invalid finite FP32 reconstruction.")
        return output

    def intermediates(self, values, *, feature_names):
        if not self.diagnostic:
            raise ValueError("Diagnostic session required.")
        self.validate(values, feature_names)
        return dict(
            zip(
                self.names,
                self.session.run(None, {"event_features": values}),
                strict=True,
            )
        )

    def score(self, values, *, feature_names):
        import numpy as np

        output = self.reconstruct(values, feature_names=feature_names)
        residual = values.astype(np.float64) - output.astype(np.float64)
        score = np.sum(residual * residual, axis=1)
        if not np.isfinite(score).all():
            raise ValueError("Nonfinite canonical CPU FP64 SSE.")
        return score

    def close(self):
        self.session = None
