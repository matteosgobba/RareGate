"""Independent supported ONNX numerical/strict-decision evidence; no timing."""

import copy

import numpy as np
import torch

from latenttrigger.benchmarks import arithmetic_cpu_v2 as a
from latenttrigger.benchmarks import core
from latenttrigger.benchmarks.frozen_cpu_v2_numerics import exact


def _bound(actual, reference, bound, name):
    try:
        return a.assert_bound(actual, reference, bound, name)
    except a.ArithmeticFailure as exc:
        if not exc.evidence or "violations" not in exc.evidence:
            raise
        return exc.evidence


def _relative(actual, reference):
    error = np.abs(actual.astype(np.float64) - reference.astype(np.float64))
    return float(np.max(error / np.maximum(1.0, np.abs(reference)), initial=0))


def local_runtime(double, outputs, topology, counts):
    records = []
    modules = dict(double.named_modules())
    for row in topology:
        x, y = outputs[row["input"]], outputs[row["output"]]
        if (
            x.dtype != np.float32
            or y.dtype != np.float32
            or x.ndim != 2
            or y.ndim != 2
            or len(x) != len(y)
        ):
            raise ValueError("Invalid actual runtime intermediate precision/shape.")
        a.supported(x)
        a.supported(y)
        if row["kind"] == "affine":
            layer = modules[row["layer"]]
            w = layer.weight.detach().numpy()
            b = layer.bias.detach().numpy()
            with torch.inference_mode():
                reference = layer(torch.from_numpy(x.astype(np.float64))).numpy()
            a.supported(reference)
            counts["diagnostic_fp64_local_affine_row_presentations"] += len(x)
            records.append(
                _bound(
                    y,
                    reference,
                    a.local_affine_bound(x.astype(np.float64), w, b),
                    "ORT_local_affine/" + row["layer"],
                )
            )
        elif row["kind"] == "relu":
            exact(y, np.maximum(x, np.float32(0)), "ORT_exact_ReLU")
        elif row["kind"] == "identity":
            exact(y, x, "ORT_exact_Identity")
    return records


def verify(
    model,
    runtime,
    diagnostic,
    manifest,
    values,
    thresholds,
    channels,
    guard,
    counts,
    *,
    persist=lambda state: None,
):
    if (
        values.shape != (1024, 8)
        or values.dtype != np.float32
        or model.training
        or model.parameter_count != 155
    ):
        raise ValueError("Frozen eval155/FP32[1024,8] verification required.")
    a.round_mode()
    a.supported(values)
    for parameter in model.parameters():
        a.supported(parameter.detach().numpy())
    before = dict(
        input_payload_byte_sha256=core.array_hash(values),
        parameter_payload_sha256=core.parameter_hash(model),
        threshold_payload_byte_sha256=core.array_hash(thresholds),
    )
    guard.boundary("fresh_PyTorch1024_and_FP64_reference")
    reference, traces = a.trace(model, values, counts)
    a.supported(reference)
    scores = model.score(values, feature_names=channels)
    counts["numerical_forward_input_presentations"] += 1024
    core.decisions(scores, thresholds)
    double = copy.deepcopy(model).double().eval()
    high, traces64 = a.trace(double, values.astype(np.float64), counts, double=True)
    envelope = a.global_envelope(model, traces64, values)
    pair = a.add_up(envelope, envelope)
    reference_records = [
        _bound(reference, high, envelope, "PyTorch_reference_vs_diagnostic")
    ]
    try:
        reference_records.extend(a.local_checks(double, traces, counts))
    except a.ArithmeticFailure as exc:
        if not exc.evidence:
            raise
        reference_records.append(exc.evidence)
    grids = []
    result = dict(
        status="running",
        reference_reconstruction_payload_byte_sha256=core.array_hash(reference),
        reference_scores_payload_byte_sha256=core.array_hash(scores),
        diagnostic_FP64_payload_byte_sha256=core.array_hash(high),
        envelope_payload_byte_sha256=core.array_hash(envelope),
        minimum_reference_threshold_margins=np.min(
            np.abs(scores[:, None] - thresholds), axis=0
        ).tolist(),
        reference_comparisons=reference_records,
        grids=grids,
        unique_rows=1024,
        windows_verified=0,
        row_window_presentations=0,
        hashes_before=before,
    )
    for batch in (1, 8, 32, 128, 1024):
        guard.boundary("equivalence_B" + str(batch))
        all_output = np.empty_like(values)
        all_scores = np.empty_like(scores)
        torch_output = np.empty_like(values)
        local_records = []
        same_score_error = 0.0
        decision_mismatches = [0] * 4
        examples = []
        for start in range(0, 1024, batch):
            guard.check()
            x = values[start : start + batch]
            primary = runtime.reconstruct(x, feature_names=channels)
            repeat = runtime.reconstruct(x, feature_names=channels)
            counts["ORT_forward_input_presentations"] += 2 * batch
            exact(primary, repeat, "ORT_same_shape_repeat")
            a.supported(primary)
            outputs = diagnostic.intermediates(x, feature_names=channels)
            counts["ORT_diagnostic_input_presentations"] += batch
            exact(
                outputs["reconstruction"], primary, "diagnostic_primary_final_equality"
            )
            local_records.extend(
                local_runtime(double, outputs, manifest["topology"], counts)
            )
            separated, _ = core.separated(x, primary, thresholds)
            public = runtime.score(x, feature_names=channels)
            counts["ORT_forward_input_presentations"] += batch
            check = core.comparison(
                separated,
                public,
                atol=1e-12,
                rtol=1e-12,
                name="ORT_same_runtime_separated_adapter_SSE",
            )
            same_score_error = max(same_score_error, check["max_absolute_error"])
            exact(separated, public, "ORT_same_shape_SSE")
            native, native_traces = a.trace(model, x, counts)
            a.supported(native)
            native_score = model.score(x, feature_names=channels)
            counts["numerical_forward_input_presentations"] += batch
            native_sep, _ = core.separated(x, native, thresholds)
            exact(native_sep, native_score, "PyTorch_same_shape_SSE")
            try:
                local_records.extend(a.local_checks(double, native_traces, counts))
            except a.ArithmeticFailure as exc:
                if not exc.evidence:
                    raise
                local_records.append(exc.evidence)
            mismatch = core.decisions(public, thresholds) != core.decisions(
                scores[start : start + batch], thresholds
            )
            decision_mismatches = [
                old + int(v)
                for old, v in zip(
                    decision_mismatches, mismatch.sum(axis=0), strict=True
                )
            ]
            for row, col in np.argwhere(mismatch)[: max(0, 4 - len(examples))]:
                examples.append(
                    dict(
                        row=int(start + row),
                        threshold_index=int(col),
                        actual_score=float(public[row]),
                        reference_score=float(scores[start + row]),
                        threshold=float(thresholds[col]),
                    )
                )
            all_output[start : start + batch] = primary
            all_scores[start : start + batch] = public
            torch_output[start : start + batch] = native
            result["windows_verified"] += 1
            result["row_window_presentations"] += batch
            guard.check()
        records = [
            _bound(all_output, high, envelope, "ORT_vs_FP64"),
            _bound(torch_output, high, envelope, "PyTorch_shape_vs_FP64"),
            _bound(all_output, reference, pair, "ORT_vs_PyTorch1024_reconstruction"),
        ]
        bound, q, evaluation = a.sse_difference_bound(
            values, reference, pair, all_scores, scores
        )
        records.append(_bound(all_scores, scores, bound, "ORT_vs_PyTorch1024_SSE"))
        local_violations = sum(r["violations"] for r in local_records)
        grids.append(
            dict(
                batch=batch,
                windows=1024 // batch,
                rows=1024,
                status="passed"
                if not any(decision_mismatches)
                and not local_violations
                and all(r["passed"] for r in records)
                else "failed",
                reconstruction_max_abs_error=float(
                    np.max(
                        np.abs(
                            all_output.astype(np.float64) - reference.astype(np.float64)
                        )
                    )
                ),
                reconstruction_max_relative_error=_relative(all_output, reference),
                reconstruction_bound_max=float(pair.max()),
                reconstruction_max_error_over_bound=records[2]["max_error_over_bound"],
                SSE_max_abs_error=float(np.max(np.abs(all_scores - scores))),
                SSE_max_relative_error=_relative(all_scores, scores),
                SSE_bound_max=float(bound.max()),
                SSE_max_error_over_bound=records[3]["max_error_over_bound"],
                SSE_propagation_Q_max=float(q.max()),
                SSE_FP64_evaluation_allowance_max=float(evaluation.max()),
                decision_mismatches=decision_mismatches,
                decision_examples=examples,
                minimum_ORT_threshold_margins=np.min(
                    np.abs(all_scores[:, None] - thresholds), axis=0
                ).tolist(),
                same_runtime_repeat_byte_exact=True,
                diagnostic_primary_final_byte_exact=True,
                same_runtime_SSE_max_abs_error=same_score_error,
                same_runtime_SSE_byte_exact=True,
                cross_runtime_reconstruction_byte_equal=all_output.tobytes()
                == reference.tobytes(),
                cross_runtime_scores_byte_equal=all_scores.tobytes()
                == scores.tobytes(),
                local_affine_scalar_checks=sum(r["elements"] for r in local_records),
                local_affine_violations=local_violations,
                local_max_error_over_bound=max(
                    (
                        r["max_error_over_bound"]
                        for r in local_records
                        if r["max_error_over_bound"] is not None
                    ),
                    default=0,
                ),
                failed_local_examples=[r for r in local_records if not r["passed"]][:4],
                comparisons=records,
            )
        )
        persist(result)
    guard.boundary("restored_references_and_frozen_values")
    with torch.inference_mode():
        restored = model(torch.from_numpy(values)).numpy()
    counts["numerical_forward_input_presentations"] += 1024
    restored_score = model.score(values, feature_names=channels)
    counts["numerical_forward_input_presentations"] += 1024
    exact(restored, reference, "restored_PyTorch1024_reconstruction")
    exact(restored_score, scores, "restored_PyTorch1024_SSE")
    after = dict(
        input_payload_byte_sha256=core.array_hash(values),
        parameter_payload_sha256=core.parameter_hash(model),
        threshold_payload_byte_sha256=core.array_hash(thresholds),
    )
    if before != after:
        raise ValueError("Frozen parameter/input/threshold mutation.")
    if any(module._forward_hooks for module in model.modules()):
        raise ValueError("Diagnostic hooks leaked.")
    result.update(
        status="passed"
        if all(row["status"] == "passed" for row in grids)
        and all(row["passed"] for row in reference_records)
        else "failed",
        hashes_after=after,
        relative_error_denominator="max(1,abs(reference))",
        local_affine_scalar_checks=sum(
            row["local_affine_scalar_checks"] for row in grids
        )
        + sum(
            row["elements"]
            for row in reference_records
            if "local_affine/" in row["comparison"]
        ),
        local_affine_violations=sum(row["local_affine_violations"] for row in grids)
        + sum(row["violations"] for row in reference_records),
        decision_mismatches=[
            sum(row["decision_mismatches"][k] for row in grids) for k in range(4)
        ],
    )
    del double
    return result
