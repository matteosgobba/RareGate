"""New numerical gate outside timers; frozen timing kernels remain untouched."""

import copy

import numpy as np
import torch

from raregate.benchmarks import arithmetic_cpu_v2 as a
from raregate.benchmarks import core


def accumulate(records, record, batch):
    key = (batch, record["comparison"])
    previous = next((x for x in records if (x["batch"], x["comparison"]) == key), None)
    if previous is None:
        records.append(dict(record, batch=batch, windows_verified=1))
    else:
        previous["windows_verified"] += 1
        for field in ("max_absolute_error", "max_bound", "max_error_over_bound"):
            previous[field] = max(previous[field], record[field])
        previous["elements"] += record["elements"]
        previous["violations"] += record["violations"]
        previous["passed"] &= record["passed"]


def exact(actual, reference, name):
    if (
        actual.dtype != reference.dtype
        or actual.shape != reference.shape
        or actual.tobytes() != reference.tobytes()
    ):
        raise a.ArithmeticFailure(
            "Byte-exact same-shape/reference requirement failed: " + name
        )


def verify_ae(model, values, thresholds, channels, windows, guard, records, audit):
    if model.training or model.parameter_count != 155:
        raise a.ArithmeticFailure("Frozen eval155 parameter AE required.")
    a.round_mode()
    guard.boundary("AE_numerical_reference")
    a.supported(values)
    before = {
        "input": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "thresholds": core.array_hash(thresholds),
    }
    reference, traces = a.trace(model, values, audit)
    a.supported(reference)
    audit["numerical_forward_input_presentations"] += 1024
    reference_score = model.score(values, feature_names=channels)
    core.decisions(reference_score, thresholds)
    double = copy.deepcopy(model).double().eval()
    high, traces64 = a.trace(double, values.astype(np.float64), audit, double=True)
    a.supported(high)
    envelope = a.global_envelope(model, traces64, values)
    pair = a.mul_up(2.0, envelope)
    for record in a.local_checks(double, traces, audit):
        accumulate(records, record, 1024)
    accumulate(
        records,
        a.assert_bound(reference, high, envelope, "reference_FP32_vs_FP64"),
        1024,
    )
    ref_separated, _ = core.separated(values, reference, thresholds)
    core.comparison(
        ref_separated,
        reference_score,
        atol=1e-12,
        rtol=1e-12,
        name="reference_same_shape_SSE",
    )
    exact(ref_separated, reference_score, "reference_same_shape_SSE")
    references = {
        "reference_reconstruction_sha256": core.array_hash(reference),
        "reference_scores_sha256": core.array_hash(reference_score),
        "diagnostic_FP64_reference_sha256": core.array_hash(high),
        "envelope_sha256": core.array_hash(envelope),
    }
    decisions = [0] * 4
    margins = np.min(np.abs(reference_score[:, None] - thresholds), axis=0)
    for batch, items in windows.items():
        guard.boundary("AE_B" + str(batch) + "_verification")
        all_outputs = np.empty_like(reference)
        all_public = np.empty_like(reference_score)
        all_local = {
            name: (np.empty_like(inputs), np.empty_like(output))
            for name, (inputs, output) in traces.items()
        }
        for window in items:
            guard.check()
            start = window["start"]
            stop = start + batch
            x = window["values"]
            canonical, local = a.trace(model, x, audit)
            guard.check()
            audit["numerical_forward_input_presentations"] += batch
            with torch.inference_mode():
                prepared = window["forward"]().numpy().copy()
            guard.check()
            audit["numerical_forward_input_presentations"] += batch
            public = model.score(x, feature_names=channels)
            guard.check()
            a.supported(canonical)
            exact(canonical, prepared, "traced_vs_prepared_same_shape")
            exact(canonical, window["reconstruction"], "cached_vs_repeated_same_shape")
            separated, _ = core.separated(x, canonical, thresholds)
            core.comparison(
                separated,
                public,
                atol=1e-12,
                rtol=1e-12,
                name="same_shape_separated_public_SSE",
            )
            exact(separated, public, "same_shape_separated_public_SSE")
            for output in (public, separated):
                checked = core.verify_decisions(
                    output, reference_score[start:stop], thresholds, "frozen_decisions"
                )
                decisions = [
                    v + count
                    for v, count in zip(
                        decisions, checked["mismatches_per_threshold"], strict=True
                    )
                ]
            all_outputs[start:stop] = canonical
            all_public[start:stop] = public
            for name, (inputs, output) in local.items():
                all_local[name][0][start:stop] = inputs
                all_local[name][1][start:stop] = output
            window["reconstruction"] = canonical
        guard.boundary("AE_B" + str(batch) + "_outward_policy")
        # Diagnostics concatenate the actual-B layer inputs/outputs. Each row's
        # FP64 local affine comparison uses those identical stored FP32 inputs;
        # its own rounded full1024 diagnostic arithmetic is included by gamma64.
        for record in a.local_checks(double, all_local, audit):
            accumulate(records, record, batch)
        accumulate(
            records, a.assert_bound(all_outputs, high, envelope, "FP32_vs_FP64"), batch
        )
        accumulate(
            records,
            a.assert_bound(all_outputs, reference, pair, "reconstruction_pair"),
            batch,
        )
        bound, q, evaluation = a.sse_difference_bound(
            values, reference, pair, all_public, reference_score
        )
        score_record = a.assert_bound(
            all_public, reference_score, bound, "canonical_SSE_pair"
        )
        score_record["max_propagation_Q"] = float(q.max(initial=0))
        score_record["max_FP64_evaluation_allowance"] = float(evaluation.max(initial=0))
        accumulate(records, score_record, batch)
    if before != {
        "input": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "thresholds": core.array_hash(thresholds),
    }:
        raise a.ArithmeticFailure("Frozen values/parameters/thresholds mutated.")
    if any(module._forward_hooks for module in model.modules()):
        raise a.ArithmeticFailure("Diagnostic hooks remain installed before timing.")
    a.round_mode()
    del double
    return dict(
        references,
        minimum_reference_threshold_margins=margins.tolist(),
        mismatches_per_threshold=decisions,
        same_shape_reconstruction_and_scores_byte_exact=True,
        hashes=before,
        full_reference_rows=1024,
        all_grid_rows=5120,
        all_grid_windows=1193,
        local_affine_scalar_checks=sum(
            c["elements"]
            for c in records
            if c["comparison"].startswith("local_affine/")
        ),
    )


def verify(model, values, thresholds, channels, windows, guard, records, audit):
    if isinstance(model, core.PCAReconstruction):
        result = core.verify_windows(
            model, values, thresholds, channels, windows, guard, records, audit
        )
        for record in records:
            if (
                record["comparison"]
                in (
                    "prepared_vs_canonical_same_shape_reconstruction",
                    "separated_vs_public_same_shape_score",
                )
                and not record["exact_byte_equality"]
            ):
                raise a.ArithmeticFailure("PCA same-shape byte equality failed.")
        result["same_shape_reconstruction_and_scores_byte_exact"] = True
        return result
    return verify_ae(
        model, values, thresholds, channels, windows, guard, records, audit
    )


def load_array(root, specification, audit, *, local=False, persist=lambda: None):
    from raregate.benchmarks import frozen_cpu_v2_protocol as q

    key = "local_array_read_attempts" if local else "original_array_read_attempts"
    if audit.get(key, 0) != 0:
        raise ValueError("Single array load per worker required.")
    path, _ = q.input_file(root, specification, local=local)
    audit[key] = 1
    persist()
    values = np.load(path, allow_pickle=False)
    core.validate_features(values)
    if core.array_hash(values) != specification["input"]["array_bytes_sha256"]:
        raise ValueError("Frozen prepared numerical bytes changed.")
    audit[
        "local_array_reads_completed" if local else "original_array_reads_completed"
    ] = 1
    audit["rows_loaded"] = 1024
    persist()
    return values
