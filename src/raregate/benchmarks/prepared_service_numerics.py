"""Rowwise extension of unchanged Task0022 arithmetic, never larger tolerances."""

import copy

import numpy as np

from raregate.benchmarks import arithmetic_cpu_v2 as a
from raregate.benchmarks import core
from raregate.benchmarks import prepared_service_protocol as p
from raregate.benchmarks.frozen_cpu_v2_numerics import exact
from raregate.benchmarks.prepared_service import pack, service, starts
from raregate.benchmarks.prepared_service_protocol import CASES, require


def load_prepared(spec, audit, persist, root=p.ROOT):
    require(
        audit.get("prepared_array_load_attempts", 0) == 0,
        "One prepared load per worker",
    )
    path, _ = p.old.input_file(root, spec)
    audit["prepared_array_load_attempts"] = 1
    persist()
    values = np.load(path, allow_pickle=False)
    core.validate_features(values)
    require(
        core.array_hash(values) == spec["input"]["array_bytes_sha256"],
        "Prepared payload identity",
    )
    audit["prepared_array_loads"] = 1
    audit["prepared_rows_loaded"] = 1024
    persist()
    return values


def call(audit, kind, rows, actual, operation, persist=lambda: None):
    """Record each proof call before access; no instrumentation inside service timers."""
    audit[kind + "_calls"] = audit.get(kind + "_calls", 0) + 1
    audit[kind + "_actual_rows"] = audit.get(kind + "_actual_rows", 0) + actual
    audit[kind + "_padding_rows"] = audit.get(kind + "_padding_rows", 0) + rows - actual
    audit["proof_inflight"] = dict(kind=kind, rows=rows, actual=actual)
    persist()
    output = operation()
    audit[kind + "_completed_calls"] = audit.get(kind + "_completed_calls", 0) + 1
    audit["proof_inflight"] = None
    persist()
    return output


def verify(
    model, values, thresholds, channels, audit, poll=lambda: None, persist=lambda: None
):
    require(values.shape == (1024, 8) and values.dtype == np.float32, "Reference shape")
    before = [
        core.array_hash(values),
        core.parameter_hash(model),
        core.array_hash(thresholds),
    ]
    ae = isinstance(model, core.CompactAutoencoder)
    internal = dict(
        numerical_forward_input_presentations=0,
        diagnostic_fp64_full_forward_presentations=0,
        diagnostic_fp64_local_affine_row_presentations=0,
    )
    records = []

    def reconstruction(x, actual):
        if ae:
            return call(
                audit,
                "proof_fp32_forward",
                len(x),
                actual,
                lambda: a.trace(model, x, internal),
                persist,
            )
        return call(
            audit,
            "proof_fp64_pca_reconstruction",
            len(x),
            actual,
            lambda: (core.reconstruct(model, x, channels), None),
            persist,
        )

    def public(x, actual):
        return call(
            audit,
            "canonical_adapter",
            len(x),
            actual,
            lambda: model.score(x, feature_names=channels),
            persist,
        )

    reference, trace = reconstruction(values, 1024)
    reference_score = public(values, 1024)
    exact(
        reference_score,
        core.separated(values, reference, thresholds)[0],
        "reference public/separated",
    )
    core.decisions(reference_score, thresholds)
    double = None
    if ae:
        require(
            model.parameter_count == 155 and not model.training, "Frozen eval topology"
        )
        a.round_mode()
        a.supported(values)
        double = copy.deepcopy(model).double().eval()
        high, traces64 = call(
            audit,
            "proof_fp64_full",
            1024,
            1024,
            lambda: a.trace(double, values.astype(np.float64), internal, double=True),
            persist,
        )
        envelope = a.global_envelope(model, traces64, values)
        records.extend(a.local_checks(double, trace, internal))
        audit["proof_fp64_local_actual_rows"] = (
            audit.get("proof_fp64_local_actual_rows", 0) + 4096
        )
        audit["proof_fp64_local_calls"] = audit.get("proof_fp64_local_calls", 0) + 4
        records.append(a.assert_bound(reference, high, envelope, "reference32_vs64"))
    windows = 0
    for b, m in CASES:
        for start in starts(m):
            for strategy in ("natural", "padded"):
                poll()
                x = pack(values[start : start + m], b, strategy)
                exact(x[:m], values[start : start + m], "actual copy")
                require(
                    not np.shares_memory(x, values)
                    and (len(x) == m or np.all(x[m:] == np.float32(0))),
                    "Owned exact zero padding",
                )
                y, local = reconstruction(x, m)
                repeated, _ = reconstruction(x, m)
                exact(y, repeated, "same shape reconstruction")
                scores = public(x, m)
                exact(scores, public(x, m), "same shape score")
                exact(
                    scores,
                    core.separated(x, y, thresholds)[0],
                    "same shape separated/public SSE",
                )
                require(
                    np.isfinite(y).all()
                    and np.isfinite(scores).all()
                    and (scores >= 0).all(),
                    "Finite all actual/dummy outputs",
                )
                target = reference_score[start : start + m]
                if ae:
                    a.supported(y)
                    h, t64 = call(
                        audit,
                        "proof_fp64_full",
                        len(x),
                        m,
                        lambda x=x: a.trace(
                            double, x.astype(np.float64), internal, double=True
                        ),
                        persist,
                    )
                    e = a.global_envelope(model, t64, x)
                    records.extend(a.local_checks(double, local, internal))
                    for k, v in (("actual", 4 * m), ("padding", 4 * (len(x) - m))):
                        audit["proof_fp64_local_" + k + "_rows"] = (
                            audit.get("proof_fp64_local_" + k + "_rows", 0) + v
                        )
                    audit["proof_fp64_local_calls"] += 4
                    records.append(a.assert_bound(y, h, e, "shape32_vs64"))
                    # For actual rows the diagnostic FP64 shapes may differ too.
                    # Check against the FIXED full-reference high path and envelope;
                    # thus the original D=2E theorem applies unchanged.
                    fixed_e = envelope[start : start + m]
                    records.append(
                        a.assert_bound(
                            y[:m],
                            high[start : start + m],
                            fixed_e,
                            "shape32_vs_fixed64",
                        )
                    )
                    pair = a.mul_up(2.0, fixed_e)
                    records.append(
                        a.assert_bound(
                            y[:m],
                            reference[start : start + m],
                            pair,
                            "reconstruction_pair",
                        )
                    )
                    bound, _, _ = a.sse_difference_bound(
                        x[:m], reference[start : start + m], pair, scores[:m], target
                    )
                    records.append(
                        a.assert_bound(scores[:m], target, bound, "SSE_pair")
                    )
                else:
                    for name, actual, expected in (
                        ("PCA reconstruction", y[:m], reference[start : start + m]),
                        ("PCA score", scores[:m], target),
                    ):
                        core.comparison(
                            actual, expected, atol=1e-12, rtol=1e-12, name=name
                        )
                core.verify_decisions(
                    scores[:m], target, thresholds, "actual-row strict decisions"
                )
                kept_s, kept_d = call(
                    audit,
                    "canonical_adapter",
                    len(x),
                    m,
                    lambda start=start, m=m, b=b, strategy=strategy: service(
                        model,
                        thresholds,
                        channels,
                        values[start : start + m],
                        b,
                        strategy,
                    ),
                    persist,
                )
                require(
                    kept_s.shape == (m,) and kept_d.shape == (m, 4), "Dummy exclusion"
                )
                exact(kept_s, scores[:m], "retained actual scores")
                exact(
                    kept_d,
                    core.decisions(scores[:m], thresholds),
                    "retained actual decisions",
                )
                windows += 1
    require(
        before
        == [
            core.array_hash(values),
            core.parameter_hash(model),
            core.array_hash(thresholds),
        ],
        "Input/parameter/threshold mutation",
    )
    require(
        not ae or all(not mod._forward_hooks for mod in model.modules()),
        "Hooks removed",
    )
    return dict(
        status="passed",
        windows_strategies_checked=windows,
        hashes=before,
        reference_reconstruction_sha256=core.array_hash(reference),
        reference_scores_sha256=core.array_hash(reference_score),
        mismatches_per_threshold=[0] * 4,
        bound_comparisons=len(records),
        max_error_over_bound=max(
            (r["max_error_over_bound"] or 0 for r in records), default=0
        ),
        max_absolute_error=max((r["max_absolute_error"] for r in records), default=0),
        diagnostic_model_copies=int(ae),
        internal_audit=internal,
    )
