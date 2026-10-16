"""Score conventions and finite empirical operating points on synthetic arrays."""

import numpy as np
import pytest

from raregate.evaluation.metrics import (
    at_threshold,
    evaluate_labeled_scores,
    evaluate_scores,
    ks_distance,
)
from raregate.evaluation.thresholds import (
    background_operating_point,
    calibrate_thresholds,
)


def test_perfect_separation_auc_ap_fixed_operating_points():
    result = evaluate_scores(np.arange(10), np.arange(20, 25))
    assert result["roc_auc"] == result["average_precision"] == 1
    assert result["signal_prevalence"] == 1 / 3
    for point in result["at_fixed_fpr"]:
        assert point["signal"]["efficiency"] == 1
        assert point["background"]["accepted"] == 0
        assert point["background"]["rejection"] is None
    for point in result["at_fixed_tpr"]:
        assert point["signal"]["efficiency"] >= point["target_tpr"]
        assert point["background"]["efficiency"] == 0


def test_reversed_orientation_is_not_silently_flipped():
    assert evaluate_scores([2, 3], [0, 1])["roc_auc"] == 0


def test_identical_tied_distributions_auc_and_prevalence_ap():
    result = evaluate_scores([0, 1, 2], [0, 1, 2])
    assert result["roc_auc"] == result["average_precision"] == 0.5
    tied = evaluate_scores(np.ones(999), np.ones(1))
    assert tied["average_precision"] == 0.001
    assert tied["at_fixed_fpr"][-1]["signal"]["accepted"] == 0
    assert tied["at_fixed_tpr"][0]["background"]["accepted"] == 999


def test_empirical_points_do_not_interpolate_across_ties():
    result = evaluate_scores([0, 1, 1, 1], [1, 2], fixed_fprs=[0.1], fixed_tprs=[0.8])
    point = result["at_fixed_fpr"][0]
    assert point["signal"]["efficiency"] == 0.5
    assert point["background"]["efficiency"] == 0
    assert result["at_fixed_tpr"][0]["background"]["efficiency"] == 0.75


def test_threshold_higher_quantile_strict_comparison_and_determinism():
    scores = np.arange(10)
    points = calibrate_thresholds(scores, [0.1, 0.5])
    assert points == calibrate_thresholds(scores[::-1], [0.1, 0.5])
    assert points[0]["threshold"] == 9 and points[0]["calibration"]["accepted"] == 0
    assert points[1]["threshold"] == 5 and points[1]["calibration"]["accepted"] == 4
    assert at_threshold([0, 1, 2], [2, 3], 2)["signal"]["accepted"] == 1
    assert calibrate_thresholds([1, 1, 1], [0.5])[0]["calibration"]["accepted"] == 0


def test_zero_fpr_reports_counts_resolution_and_bound():
    point = calibrate_thresholds([1], [0.001])[0]
    assert point["below_empirical_resolution"]
    bg = point["calibration"]
    assert bg["accepted"] == 0 and bg["total"] == 1 and bg["resolution"] == 1
    assert bg["rejection"] is None and bg["zero_acceptance_upper_95"] == pytest.approx(
        0.95
    )
    other = background_operating_point([0, 1, 2, 3], 1)
    assert other["accepted"] == 2 and other["rejection"] == 2
    assert other["wilson_95"][0] < 0.5 < other["wilson_95"][1]


@pytest.mark.parametrize("bad", [[], [np.nan], [np.inf], [[1, 2]], ["1"], [1 + 2j]])
def test_invalid_score_arrays_rejected(bad):
    with pytest.raises(ValueError):
        evaluate_scores(bad, [1])


@pytest.mark.parametrize("labels", [[0, 0], [1, 1], [0, 2], [0, np.nan], [0], [[0, 1]]])
def test_invalid_or_degenerate_labels_rejected(labels):
    with pytest.raises(ValueError):
        evaluate_labeled_scores(labels, [1, 2])


@pytest.mark.parametrize("target", [0, 1, -0.1, np.nan])
def test_invalid_calibration_fpr_rejected(target):
    with pytest.raises(ValueError):
        calibrate_thresholds([0, 1], [target])


def test_ks_ties_and_drift():
    assert ks_distance([0, 1, 1], [1, 0, 1]) == 0
    assert ks_distance([0, 0], [1, 1]) == 1


def test_random_like_independent_toy_scores():
    rng = np.random.default_rng(1729)
    result = evaluate_scores(rng.normal(size=2500), rng.normal(size=2500))
    assert abs(result["roc_auc"] - 0.5) < 0.04
    assert abs(result["average_precision"] - 0.5) < 0.04


def test_extreme_finite_lowest_score_accept_all_kind():
    minimum = -np.finfo(np.float64).max
    result = evaluate_scores([minimum], [minimum], fixed_tprs=[1])
    point = result["at_fixed_tpr"][0]
    assert point["threshold"] is None and point["threshold_kind"] == "accept_all"
    assert point["signal"]["accepted"] == point["background"]["accepted"] == 1
