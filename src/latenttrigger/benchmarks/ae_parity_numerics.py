"""Bounded AE diagnostics; no timing, fitting, stores or threshold selection."""

import copy

import numpy as np
import torch

from latenttrigger.benchmarks import core

LAYERS = ("encoder.0", "encoder.1", "encoder.2", "decoder.0", "decoder.1", "decoder.2")


def families():
    constants = np.repeat(np.array([0, 1, -1, 8], dtype=np.float32), 256)
    row, channel = np.indices((1024, 8))
    powers = np.ldexp((-1.0) ** ((row // 7 + channel) % 2), (row + channel) % 7 - 3)
    return {
        "constants": np.repeat(constants[:, None], 8, axis=1),
        "powers": powers.astype(np.float32),
        "uniform": np.random.default_rng(1729)
        .uniform(-8, 8, (1024, 8))
        .astype(np.float32),
        "normal": np.clip(
            np.random.default_rng(1729).standard_normal((1024, 8)), -8, 8
        ).astype(np.float32),
    }


def finite(*values):
    if any(not np.isfinite(value).all() for value in values):
        raise ValueError("Nonfinite diagnostic output/input.")


def comparison(actual, reference, *, atol=1e-6, rtol=1e-5):
    """Aggregate original executed criterion, also audit ideal FP64 RHS."""
    if actual.shape != reference.shape:
        raise ValueError("Diagnostic comparison shape mismatch.")
    finite(actual, reference)
    error = np.abs(actual.astype(np.float64) - reference.astype(np.float64))
    bound = atol + rtol * np.abs(reference)
    ideal = atol + rtol * np.abs(reference.astype(np.float64))
    bad = error > bound
    coordinates = np.argwhere(bad)
    examples = [
        {
            "index": c.tolist(),
            "actual": float(actual[tuple(c)]),
            "reference": float(reference[tuple(c)]),
            "absolute_error": float(error[tuple(c)]),
            "executed_bound": float(bound[tuple(c)]),
            "ideal_fp64_bound": float(ideal[tuple(c)]),
        }
        for c in coordinates[:8]
    ]
    return {
        "max_absolute_error": float(error.max(initial=0)),
        "max_relative_error": float(
            (error / np.maximum(np.abs(reference.astype(np.float64)), atol)).max(
                initial=0
            )
        ),
        "exact_byte_equality": actual.dtype == reference.dtype
        and actual.tobytes() == reference.tobytes(),
        "violations": int(bad.sum()),
        "passed": not bool(bad.any()),
        "violation_locations": coordinates.tolist(),
        "violation_mask_sha256": core.array_hash(np.packbits(bad)),
        "examples": examples,
        "executed_bound_dtype": str(bound.dtype),
        "max_bound_rounding_difference": float(
            np.abs(bound.astype(np.float64) - ideal).max(initial=0)
        ),
        "promotion_changed_verdicts": int(np.count_nonzero(bad != (error > ideal))),
    }


def decision_review(actual, reference, thresholds):
    left, right = (
        core.decisions(actual, thresholds),
        core.decisions(reference, thresholds),
    )
    mismatch = left != right
    return {
        "mismatches_per_threshold": mismatch.sum(axis=0).tolist(),
        "passed": not bool(mismatch.any()),
        "mismatch_locations": np.argwhere(mismatch).tolist(),
        "minimum_reference_absolute_margins": np.min(
            np.abs(reference[:, None] - thresholds), axis=0
        ).tolist(),
        "minimum_actual_absolute_margins": np.min(
            np.abs(actual[:, None] - thresholds), axis=0
        ).tolist(),
        "max_score_change_over_reference_margin": np.max(
            np.abs(actual - reference)[:, None]
            / np.maximum(
                np.abs(reference[:, None] - thresholds), np.finfo(np.float64).tiny
            ),
            axis=0,
        ).tolist(),
    }


def traced_forward(model, values, audit, *, diagnostic64=False):
    trace = {}
    handles = []
    try:
        for name, module in model.named_modules():
            if name in LAYERS:

                def hook(_module, _inputs, output, name=name):
                    trace[name] = output.detach().cpu().numpy().copy()

                handles.append(module.register_forward_hook(hook))
        key = (
            "fp64_diagnostic_presentations"
            if diagnostic64
            else "fp32_forward_presentations"
        )
        audit[key] += len(values)
        with torch.inference_mode():
            tensor = torch.from_numpy(values)
            # The copy retains exact stored values but encode's FP32 validation
            # is intentionally not applicable to this diagnostic-only FP64 path.
            output = (
                model.decoder(model.encoder(tensor)) if diagnostic64 else model(tensor)
            )
        output = output.detach().cpu().numpy().copy()
        finite(output, *trace.values())
        if tuple(trace) != LAYERS:
            raise ValueError("Unexpected affine/ReLU layer topology.")
        return output, trace
    finally:
        for handle in handles:
            handle.remove()


def affine_roundoff_envelope(model, fp64_trace, values):
    """Explanatory roundoff model, not a certified bound or active acceptance."""
    u = 2.0**-24
    previous = values.astype(np.float64)
    error = np.zeros_like(previous)
    envelope_layers = {}
    for name, module in model.named_modules():
        if name not in LAYERS:
            continue
        if isinstance(module, torch.nn.Linear):
            weights = np.abs(module.weight.detach().numpy().astype(np.float64))
            bias = np.abs(module.bias.detach().numpy().astype(np.float64))
            n = weights.shape[1]
            gamma = (2 * n + 2) * u / (1 - (2 * n + 2) * u)
            magnitude = (np.abs(previous) + error) @ weights.T + bias
            error = error @ weights.T + gamma * magnitude
        elif not isinstance(module, torch.nn.ReLU):
            raise ValueError("Unsupported envelope layer.")
        previous = fp64_trace[name]
        envelope_layers[name] = float(error.max(initial=0))
    return error, envelope_layers


def analyze(model, values, thresholds, channels, guard, result):
    core.validate_features(values)
    if model.training or model.parameter_count != 155:
        raise ValueError("Frozen eval155-parameter model required.")
    audit = result["audit"]
    before = {
        "input": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "thresholds": core.array_hash(thresholds),
    }
    result.update(
        hashes_before=before,
        input_shape=list(values.shape),
        input_strides=list(values.strides),
        input_dtype=str(values.dtype),
        windows=[],
        status="started",
    )
    guard.boundary("full_1024_reference")
    reference, reference_layers = traced_forward(model, values, audit)
    guard.check()
    audit["fp32_forward_presentations"] += 1024
    reference_score = model.score(values, feature_names=channels)
    finite(reference_score)
    guard.check()
    same_ref, _ = core.separated(values, reference, thresholds)
    if not comparison(same_ref, reference_score, atol=1e-12, rtol=1e-12)["passed"]:
        raise ValueError("Full reference separated/public SSE inconsistent.")
    copy64 = copy.deepcopy(model).to(dtype=torch.float64).eval()
    values64 = values.astype(np.float64)
    guard.boundary("fp64_diagnostic_copy")
    high, high_layers = traced_forward(copy64, values64, audit, diagnostic64=True)
    envelope, envelope_layers = affine_roundoff_envelope(model, high_layers, values)
    del copy64
    result["diagnostic64"] = {
        "reference_error": comparison(reference.astype(np.float64), high),
        "roundoff_model_max_bound": float(envelope.max()),
        "layer_bound_maxima": envelope_layers,
        "fp32_reference_error_over_model_bound": float(
            np.max(
                np.abs(reference - high)
                / np.maximum(envelope, np.finfo(np.float64).tiny)
            )
        ),
        "assumptions": "ordinary_FP32_products_and_sums_no_overflow;gamma_(2n+2);ReLU_1_Lipschitz;FP64_reference_not_exact_truth;not_certified_or_active",
    }
    reference_hashes = {
        "reconstruction": core.array_hash(reference),
        "score": core.array_hash(reference_score),
    }
    result["reference_hashes_before"] = reference_hashes
    for batch in (1, 8, 32, 128, 1024):
        guard.boundary("grid_" + str(batch))
        actual = np.empty_like(reference)
        repeat = np.empty_like(reference)
        public = np.empty_like(reference_score)
        actual_layers = {name: np.empty_like(v) for name, v in reference_layers.items()}
        cell = {
            "batch": batch,
            "rows_completed": 0,
            "windows_completed": 0,
            "status": "started",
        }
        result["windows"].append(cell)
        for start in range(0, 1024, batch):
            stop = start + batch
            x = values[start:stop]
            guard.check()
            output, traces = traced_forward(model, x, audit)
            guard.check()
            audit["fp32_forward_presentations"] += batch
            repeat[start:stop] = core.reconstruct(model, x, channels)
            guard.check()
            audit["fp32_forward_presentations"] += batch
            public[start:stop] = model.score(x, feature_names=channels)
            guard.check()
            actual[start:stop] = output
            for name, trace in traces.items():
                actual_layers[name][start:stop] = trace
            finite(output, repeat[start:stop], public[start:stop])
            cell["rows_completed"] += batch
            cell["windows_completed"] += 1
        score, _ = core.separated(values, actual, thresholds)
        repeat_score, _ = core.separated(values, repeat, thresholds)
        layer_records = []
        for name in LAYERS:
            c = comparison(actual_layers[name], reference_layers[name])
            layer_records.append(
                {
                    "layer": name,
                    "max_absolute_error": c["max_absolute_error"],
                    "different_elements": int(
                        np.count_nonzero(actual_layers[name] != reference_layers[name])
                    ),
                    "sign_changes_positive_vs_nonpositive": int(
                        np.count_nonzero(
                            (actual_layers[name] > 0) != (reference_layers[name] > 0)
                        )
                    ),
                }
            )
        r = values.astype(np.float64) - reference.astype(np.float64)
        d = actual.astype(np.float64) - reference.astype(np.float64)
        delta = -2 * np.sum(r * d, axis=1) + np.sum(d * d, axis=1)
        explanatory = 2 * np.sum(np.abs(r * d), axis=1) + np.sum(d * d, axis=1)
        cell.update(
            status="completed",
            reconstruction=comparison(actual, reference),
            separated_score=comparison(score, reference_score),
            public_score=comparison(public, reference_score),
            same_shape_reconstruction=comparison(actual, repeat),
            same_shape_score=comparison(score, public, atol=1e-12, rtol=1e-12),
            repeated_score=comparison(score, repeat_score, atol=1e-12, rtol=1e-12),
            decisions=decision_review(public, reference_score, thresholds),
            prepared_decisions=decision_review(score, reference_score, thresholds),
            layers=layer_records,
            first_divergent_layer=next(
                (c["layer"] for c in layer_records if c["different_elements"]), None
            ),
            sse_propagation={
                "max_absolute_algebra_delta": float(np.abs(delta).max()),
                "max_absolute_explanatory_bound": float(explanatory.max()),
                "max_fp64_evaluation_discrepancy": float(
                    np.abs((score - reference_score) - delta).max()
                ),
                "not_certified_floating_point_bound": True,
            },
            fp64_diagnostic_max_absolute_error=float(
                np.abs(actual.astype(np.float64) - high).max()
            ),
            arithmetic_model_max_error_over_two_envelopes=float(
                np.max(
                    np.abs(actual.astype(np.float64) - reference.astype(np.float64))
                    / np.maximum(2 * envelope, np.finfo(np.float64).tiny)
                )
            ),
        )
        if batch == 1:
            c = (7, 5)
            cell["historical_coordinate"] = {
                "sample_relative_index": list(c),
                "actual": float(actual[c]),
                "reference": float(reference[c]),
                "absolute_error": float(abs(float(actual[c]) - float(reference[c]))),
            }
    guard.boundary("reference_and_identity_recheck")
    audit["fp32_forward_presentations"] += 1024
    post = core.reconstruct(model, values, channels)
    guard.check()
    audit["fp32_forward_presentations"] += 1024
    post_score = model.score(values, feature_names=channels)
    guard.check()
    after = {
        "input": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "thresholds": core.array_hash(thresholds),
    }
    post_hashes = {
        "reconstruction": core.array_hash(post),
        "score": core.array_hash(post_score),
    }
    result.update(hashes_after=after, reference_hashes_after=post_hashes)
    if before != after or reference_hashes != post_hashes:
        raise ValueError("Frozen input/parameter/threshold/reference mutation.")
    result["status"] = "completed"
    result["historical_v1_comparison_passed"] = all(
        c["reconstruction"]["passed"]
        and c["separated_score"]["passed"]
        and c["public_score"]["passed"]
        and c["decisions"]["passed"]
        for c in result["windows"]
    )


def load_prepared(root, specification, audit, persist=lambda: None):
    """One fixed prepared-array read; refusal precedes NumPy opening."""
    from latenttrigger.benchmarks import ae_parity_protocol as q
    from latenttrigger.benchmarks import protocol as p

    expected = "results/benchmarks/task0020-frozen-cpu/prepare/input.npy"
    spec = specification["input"]
    if (
        spec["path"] != expected
        or spec["shape"] != [1024, 8]
        or spec["dtype"] != "float32"
        or spec["loads"] != 1
        or spec["allow_pickle"] is not False
        or audit["prepared_numerical_load_attempts"] != 0
    ):
        raise ValueError("Only one fixed prepared1024 FP32 array read authorized.")
    path = q.fixed_path(root, expected)
    if (
        path.stat().st_size != spec["file_size_bytes"]
        or path.stat().st_size > 65536
        or p.file_hash(path) != spec["file_sha256"]
    ):
        raise ValueError("Prepared file identity/size changed before array open.")
    audit["prepared_numerical_load_attempts"] = 1
    persist()
    values = np.load(path, allow_pickle=False)
    audit["prepared_numerical_loads_completed"] = 1
    audit["unique_reused_real_rows"] = len(values)
    persist()
    core.validate_features(values)
    if core.array_hash(values) != spec["array_bytes_sha256"]:
        raise ValueError("Prepared numerical bytes changed.")
    return values
