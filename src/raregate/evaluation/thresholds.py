"""Background-only quantile calibration; every decision uses score > threshold."""

from statistics import NormalDist

import numpy as np


def scores_array(scores: np.ndarray) -> np.ndarray:
    """Reject empty, nonfinite, nonnumeric or multidimensional score inputs."""
    values = np.asarray(scores)
    if values.ndim != 1 or values.size == 0 or values.dtype.kind not in "iuf":
        raise ValueError("Scores must be a nonempty real numeric vector.")
    values = values.astype(np.float64)
    if not np.isfinite(values).all():
        raise ValueError("Scores must be finite.")
    return values


def efficiency(scores: np.ndarray, threshold: float) -> dict:
    """Empirical acceptance, counts and Wilson 95% interval; never extrapolate."""
    values = scores_array(scores)
    if np.isnan(threshold):
        raise ValueError("Threshold cannot be NaN.")
    count, total = int((values > threshold).sum()), len(values)
    rate = count / total
    z = NormalDist().inv_cdf(0.975)
    center = (rate + z * z / (2 * total)) / (1 + z * z / total)
    half = (
        z
        * np.sqrt(rate * (1 - rate) / total + z * z / (4 * total**2))
        / (1 + z * z / total)
    )
    return {
        "accepted": count,
        "total": total,
        "efficiency": rate,
        "resolution": 1 / total,
        "wilson_95": [max(0.0, float(center - half)), min(1.0, float(center + half))],
    }


def background_operating_point(scores: np.ndarray, threshold: float) -> dict:
    """Zero accepted background means unresolved rejection, not infinity."""
    result = efficiency(scores, threshold)
    result["rejection"] = 1 / result["efficiency"] if result["accepted"] else None
    result["zero_acceptance_upper_95"] = (
        float(-np.expm1(np.log(0.05) / result["total"]))
        if not result["accepted"]
        else None
    )
    return result


def calibrate_thresholds(
    background_scores: np.ndarray, target_fprs: list[float]
) -> list[dict]:
    """Use higher quantiles and strict >, conservatively handling empirical ties.

    For sorted N scores use index ceil((N-1)*(1-alpha)); accept strictly larger.
    Thus calibration empirical acceptance cannot exceed alpha. This is not a
    guarantee about the population acceptance or an independent validation sample.
    """
    scores = scores_array(background_scores)
    if not target_fprs or len(set(target_fprs)) != len(target_fprs):
        raise ValueError("Supply unique target FPRs.")
    results = []
    for alpha in target_fprs:
        if not np.isfinite(alpha) or not 0 < alpha < 1:
            raise ValueError("Target FPR must be in (0,1).")
        threshold = float(np.quantile(scores, 1 - alpha, method="higher"))
        result = background_operating_point(scores, threshold)
        results.append(
            {
                "target_fpr": float(alpha),
                "threshold": threshold,
                "calibration": result,
                "expected_tail_count": float(alpha * len(scores)),
                "below_empirical_resolution": bool(alpha < 1 / len(scores)),
            }
        )
    return results
