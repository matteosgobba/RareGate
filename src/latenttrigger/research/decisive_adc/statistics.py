"""Outcome-independent frozen helpers; no payload IO or evaluation activation."""

import math

import numpy as np
from scipy.stats import beta, binom


def calibration(scores, alpha):
    scores = np.asarray(scores, dtype=np.float64)
    if (
        scores.ndim != 1
        or len(scores) == 0
        or not np.isfinite(scores).all()
        or alpha not in (0.01, 0.001)
    ):
        raise ValueError("calibration scores/rate")
    ordered = np.sort(scores)
    n = len(scores)
    lower = int(binom.ppf(0.01 / (2 * 16), n, 1 - alpha))
    upper = int(binom.ppf(1 - 0.01 / (2 * 16), n, 1 - alpha)) + 1
    # Exactly NumPy higher: zero-based ceil((N-1)*q).
    index = math.ceil((n - 1) * (1 - alpha))
    threshold = float(ordered[index])

    def endpoint(rank):
        if rank < 1:
            return "-infinity"
        if rank > n:
            return "+infinity"
        return float(ordered[rank - 1])

    return dict(
        alpha=alpha,
        N=n,
        threshold=threshold,
        threshold_rank_one_based=index + 1,
        accepted=int(np.count_nonzero(scores > threshold)),
        ties=int(np.count_nonzero(scores == threshold)),
        lower_rank_one_based=lower,
        upper_rank_one_based=upper,
        lower_endpoint=endpoint(lower),
        upper_endpoint=endpoint(upper),
        quantile="higher",
        comparison=">",
        family_delta=0.01,
        stream_rate_pairs=16,
    )


def exact_background_interval(accepted, total):
    if not 0 <= accepted <= total or total <= 0:
        raise ValueError("binomial counts")
    d = 0.01 / 16
    return (
        0.0
        if accepted == 0
        else float(beta.ppf(d / 2, accepted, total - accepted + 1)),
        1.0
        if accepted == total
        else float(beta.ppf(1 - d / 2, accepted + 1, total - accepted)),
    )


def paired_bound(values, support):
    x = np.asarray(values, dtype=np.float64)
    lo, hi = support
    if (
        x.ndim != 1
        or len(x) < 2
        or not np.isfinite(x).all()
        or np.any((x < lo) | (x > hi))
    ):
        raise ValueError("paired values/support")
    logarithm = math.log(4 * 44 / 0.03)
    half = math.sqrt(2 * x.var(ddof=1) * logarithm / len(x)) + 7 * (
        hi - lo
    ) * logarithm / (3 * (len(x) - 1))
    return dict(
        N=len(x),
        mean=float(x.mean()),
        lower=max(lo, float(x.mean() - half)),
        upper=min(hi, float(x.mean() + half)),
        halfwidth=half,
    )


def seed_indicators(scores, thresholds):
    scores = np.asarray(scores)
    if (
        scores.ndim != 2
        or scores.shape[0] not in (1, 3)
        or len(thresholds) != scores.shape[0]
        or not np.isfinite(scores).all()
        or np.isnan(np.asarray(thresholds, dtype=float)).any()
    ):
        raise ValueError("one deterministic or three paired seeds")
    return (scores > np.asarray(thresholds)[:, None]).mean(axis=0)


def cpu_indices(repetition, call_index, batch):
    if (
        repetition not in range(8)
        or call_index not in range(160)
        or batch not in (1, 32, 512)
    ):
        raise ValueError("CPU schedule bounds")
    return ((repetition * 160 + call_index) * batch + np.arange(batch)) % 4096


def deny_final_evaluation(scope):
    if scope != "Task0062-explicit-human-authorized":
        raise PermissionError("Task0062 fresh scope required; Task0061 cannot unblind")


def signal_bounds(
    candidate_scores,
    candidate_cuts,
    reference_scores=None,
    reference_cuts=None,
    factor=1.0,
):
    """Conservative paired bounds; arrays only, with no payload access or choice."""

    def endpoints(cuts, name):
        return [
            float(c[name].replace("infinity", "inf"))
            if isinstance(c[name], str)
            else c[name]
            for c in cuts
        ]

    lower_values = seed_indicators(
        candidate_scores, endpoints(candidate_cuts, "upper_endpoint")
    )
    upper_values = seed_indicators(
        candidate_scores, endpoints(candidate_cuts, "lower_endpoint")
    )
    support = (0.0, 1.0)
    if reference_scores is not None:
        if np.asarray(candidate_scores).shape[1] != np.asarray(reference_scores).shape[
            1
        ] or factor not in (1.0, 0.9):
            raise ValueError("paired event count/factor")
        lower_values -= factor * seed_indicators(
            reference_scores, endpoints(reference_cuts, "lower_endpoint")
        )
        upper_values -= factor * seed_indicators(
            reference_scores, endpoints(reference_cuts, "upper_endpoint")
        )
        support = (-factor, 1.0)
    return dict(
        N=len(lower_values),
        lower=paired_bound(lower_values, support)["lower"],
        upper=paired_bound(upper_values, support)["upper"],
    )


def rate_comparable(left, right, alpha):
    tolerance = {0.01: 0.1, 0.001: 0.3}[alpha] * alpha
    return bool(
        all(
            alpha - tolerance <= lo <= hi <= alpha + tolerance
            for lo, hi in (left, right)
        )
        and left[0] - right[1] >= -tolerance
        and left[1] - right[0] <= tolerance
    )


def cpu_cost_rule(candidate, reference):
    """Eight blocks x three seeds of positive costs, synthetic until Task0062."""
    c, r = np.asarray(candidate), np.asarray(reference)
    if (
        c.ndim != 2
        or r.ndim != 2
        or c.shape[0] != 8
        or r.shape[0] != 8
        or c.shape[1] not in (1, 3)
        or r.shape[1] not in (1, 3)
        or not np.isfinite(c).all()
        or not np.isfinite(r).all()
        or np.any(c <= 0)
        or np.any(r <= 0)
    ):
        raise ValueError("cost block shapes/values")
    ratios = c.mean(axis=1) / r.mean(axis=1)
    return dict(
        ratios=ratios.tolist(),
        median=float(np.median(ratios)),
        blocks_le_point80=int((ratios <= 0.80).sum()),
        passed=bool(np.median(ratios) <= 0.75 and (ratios <= 0.80).sum() >= 7),
    )
