"""Model-independent metrics for finite score arrays; higher means anomalous."""

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve

from latenttrigger.evaluation.thresholds import (
    background_operating_point,
    efficiency,
    scores_array,
)


def score_summary(scores: np.ndarray) -> dict:
    values = scores_array(scores)
    q = np.quantile(values, [0.5, 0.9, 0.95, 0.99, 0.999], method="linear")
    return {
        "count": len(values),
        "mean": float(values.mean()),
        "std": float(values.std()),
        "min": float(values.min()),
        **dict(
            zip(("median", "p90", "p95", "p99", "p99_9"), map(float, q), strict=True)
        ),
        "max": float(values.max()),
    }


def ks_distance(first: np.ndarray, second: np.ndarray) -> float:
    """Maximum two-sample ECDF distance, with ties; no p-value interpretation."""
    a, b = np.sort(scores_array(first)), np.sort(scores_array(second))
    support = np.unique(np.concatenate([a, b]))
    return float(
        np.max(
            np.abs(
                np.searchsorted(a, support, side="right") / len(a)
                - np.searchsorted(b, support, side="right") / len(b)
            )
        )
    )


def at_threshold(
    background_scores: np.ndarray, signal_scores: np.ndarray, threshold: float
) -> dict:
    return {
        "background": background_operating_point(background_scores, threshold),
        "signal": efficiency(signal_scores, threshold),
    }


def evaluate_labeled_scores(
    labels: np.ndarray,
    scores: np.ndarray,
    *,
    fixed_fprs=(0.1, 0.05, 0.01, 0.001),
    fixed_tprs=(0.5, 0.8, 0.9),
) -> dict:
    """Empirical ROC/AP and attainable operating points; no curve interpolation.

    Fixed-ROC points are descriptive benchmark metrics. They do not replace
    deployment thresholds frozen on independent calibration background.
    """
    y = np.asarray(labels)
    values = scores_array(scores)
    if (
        y.ndim != 1
        or len(y) != len(values)
        or y.dtype.kind not in "biuf"
        or not np.isin(y, [0, 1]).all()
        or len(np.unique(y)) != 2
    ):
        raise ValueError("Binary labels 0/1 with both classes must match scores.")
    bg, sig = values[y == 0], values[y == 1]
    fpr, tpr, thresholds = roc_curve(y, values, pos_label=1, drop_intermediate=False)

    def point(index: int) -> dict:
        # sklearn ROC accepts >= a finite cutoff. Express the same set with
        # the common strict > convention using the immediately lower float64.
        cutoff = thresholds[index]
        with np.errstate(over="ignore"):
            boundary = (
                float(np.nextafter(cutoff, -np.inf)) if np.isfinite(cutoff) else np.inf
            )
        return {
            "threshold": boundary if np.isfinite(boundary) else None,
            "threshold_kind": "strict_gt"
            if np.isfinite(boundary)
            else ("accept_none" if boundary > 0 else "accept_all"),
            **at_threshold(bg, sig, boundary),
        }

    at_fpr, at_tpr = [], []
    for target in fixed_fprs:
        if not np.isfinite(target) or not 0 <= target < 1:
            raise ValueError("Fixed FPR must be in [0,1).")
        allowed = np.flatnonzero(fpr <= target)
        chosen = int(allowed[np.argmax(tpr[allowed])])
        at_fpr.append({"target_fpr": float(target), **point(chosen)})
    for target in fixed_tprs:
        if not np.isfinite(target) or not 0 < target <= 1:
            raise ValueError("Fixed TPR must be in (0,1].")
        chosen = int(np.flatnonzero(tpr >= target)[0])
        at_tpr.append({"target_tpr": float(target), **point(chosen)})
    return {
        "roc_auc": float(roc_auc_score(y, values)),
        "average_precision": float(average_precision_score(y, values)),
        "signal_prevalence": len(sig) / len(values),
        "background_total": len(bg),
        "signal_total": len(sig),
        "at_fixed_fpr": at_fpr,
        "at_fixed_tpr": at_tpr,
    }


def evaluate_scores(
    background_scores: np.ndarray, signal_scores: np.ndarray, **kwargs
) -> dict:
    """Evaluate score orientation as supplied; never silently flip reversed scores."""
    bg, sig = scores_array(background_scores), scores_array(signal_scores)
    return evaluate_labeled_scores(
        np.r_[np.zeros(len(bg), dtype=np.uint8), np.ones(len(sig), dtype=np.uint8)],
        np.concatenate([bg, sig]),
        **kwargs,
    )
