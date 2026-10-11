"""Aggregate-only synthetic tests; no models, real data or historical acceptance."""

import copy
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "frozen_synthesis",
    Path(__file__).parents[1] / "scripts/synthesize_frozen_results.py",
)
synthesis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(synthesis)


@pytest.fixture
def aggregates():
    identities, evaluations, comparison, calibrated, empirical = [], [], [], [], []
    cells, groups = [], []
    for index, name in enumerate(synthesis.NAMES):
        thresholds = [
            dict(target_fpr=t, threshold=i + 1.0)
            for i, t in enumerate(synthesis.TARGETS)
        ]
        identity = dict(
            name=name,
            model_scientific_sha256=f"model{index}",
            results_scientific_sha256=f"calibration{index}",
            orientation="higher_is_more_anomalous",
            threshold_decision="score > threshold",
            score_definition="sum_squared_reconstruction_residual",
            score_dtype="float64",
            calibration_count=74823,
            thresholds=thresholds,
        )
        identities.append(identity)
        quality = dict(
            roc_auc=0.5 + index / 10,
            average_precision=0.4 + index / 10,
            background_total=150471,
            signal_total=100000,
            signal_prevalence=100000 / 250471,
        )
        comparison.append(dict(candidate=name, **quality))
        points = []
        for i, t in enumerate(synthesis.TARGETS):
            b, s = (124, 2) if index == 0 else (116, 56)
            bp, sp = b / 150471, s / 100000
            point = dict(
                target_fpr=t,
                threshold=i + 1.0,
                background=dict(
                    accepted=b,
                    total=150471,
                    efficiency=bp,
                    wilson_95=[bp / 2, bp * 2],
                    rejection=1 / bp,
                ),
                signal=dict(
                    accepted=s, total=100000, efficiency=sp, wilson_95=[sp / 2, sp * 2]
                ),
            )
            points.append(point)
            row = dict(
                candidate=name,
                target_fpr=t,
                threshold=i + 1.0,
                background_accepted=b,
                background_total=150471,
                background_fpr=bp,
                background_wilson_low=bp / 2,
                background_wilson_high=bp * 2,
                background_rejection=1 / bp,
                zero_acceptance_upper_95=None,
                signal_accepted=s,
                signal_total=100000,
                signal_efficiency=sp,
                signal_wilson_low=sp / 2,
                signal_wilson_high=sp * 2,
            )
            calibrated.append(row)
            empirical.append(
                dict(
                    **{k: v for k, v in row.items() if k != "target_fpr"},
                    kind="descriptive_fixed_FPR",
                    target=t,
                    threshold_kind="strict_gt",
                )
            )
        tpr_points = [
            dict(points[i], target_tpr=t, threshold_kind="strict_gt")
            for i, t in enumerate((0.5, 0.8, 0.9))
        ]
        for i, t in enumerate((0.5, 0.8, 0.9)):
            row = calibrated[-4 + i]
            empirical.append(
                dict(
                    **{k: v for k, v in row.items() if k != "target_fpr"},
                    kind="descriptive_fixed_TPR",
                    target=t,
                    threshold_kind="strict_gt",
                )
            )
        quality.update(
            calibrated_thresholds=points,
            at_fixed_fpr=[dict(p, threshold_kind="strict_gt") for p in points],
            at_fixed_tpr=tpr_points,
        )
        evaluations.append(
            dict(
                model_scientific_sha256=f"model{index}",
                calibration_scientific_sha256=f"calibration{index}",
                metrics=quality,
            )
        )
        for batch in synthesis.BATCHES:
            workers = [f"{'PCA' if index == 0 else 'AE'}{j}" for j in (1, 2, 3)]
            means = [1000.0, 2000.0, 9000.0]  # Retained slow repetition matters.
            medians = [800.0, 900.0, 1000.0]
            for j, worker in enumerate(workers):
                for scope in ("reconstruction", "score_decision", "adapter_decision"):
                    cells.append(
                        dict(
                            worker=worker,
                            model=name,
                            batch=batch,
                            scope=scope,
                            count=200,
                            p50_ns=medians[j],
                            mean_ns=means[j],
                            max_ns=means[j] * 10,
                            p95_ns=means[j] * 2,
                            p99_ns=means[j] * 3,
                            population_std_ns=100,
                            status="completed",
                        )
                    )
            mean = sum(means) / 3
            groups.append(
                dict(
                    model=name,
                    batch=batch,
                    scope="adapter_decision",
                    workers=workers,
                    worker_p50_ns=medians,
                    worker_mean_ns=means,
                    median_of_worker_medians_ns=900,
                    pooled_600_invocation_mean_ns=mean,
                    throughput_from_pooled_mean_events_per_second=batch * 1e9 / mean,
                )
            )
    science = dict(
        phase="A_and_authorized_B_complete_accepted",
        execution_Phase_B=dict(status="parent_accepted"),
        actual_access=dict(
            test_background_model_evaluation_accessed=True,
            test_signal_model_evaluation_accessed=True,
        ),
        identities=dict(candidate_registry=identities),
        scientific_results=dict(evaluations=evaluations),
    )
    cost = dict(
        execution_status="complete_accepted_consumed_no_retry",
        comparison_success=True,
        frozen_models=copy.deepcopy(identities),
        timing_cells=copy.deepcopy(cells),
        timing_groups=groups,
    )
    return science, cost, comparison, calibrated, empirical, cells


def test_pool_retains_outlier_and_strict_slice_arithmetic(aggregates):
    frontier, operating = synthesis.derive(*aggregates)
    assert len(frontier) == 10 and len(operating) == 8
    assert frontier[0]["median_of_three_worker_p50_batch_us"] == 0.9
    assert frontier[0]["pooled_600_invocation_mean_batch_ns"] == 4000
    assert frontier[0]["throughput_from_pooled_mean_events_per_second"] == 250000
    assert operating[-1]["relative_acceptance"] == pytest.approx(0.726411724137931)
    assert operating[-1]["selected_signal_fraction"] == pytest.approx(56 / 172)


@pytest.mark.parametrize(
    "mutation",
    [
        "status",
        "identity",
        "missing_threshold",
        "duplicate_threshold",
        "missing_batch",
        "duplicate_cell",
        "count",
        "interval",
        "units",
        "nonfinite",
        "exposure",
    ],
)
def test_refuses_incompatible_or_incomplete_aggregates(aggregates, mutation):
    science, cost, _, calibrated, _, cells = aggregates
    if mutation == "status":
        cost["execution_status"] = "failed_consumed_no_retry"
    elif mutation == "identity":
        cost["frozen_models"][0]["model_scientific_sha256"] = "different"
    elif mutation == "missing_threshold":
        calibrated.pop()
    elif mutation == "duplicate_threshold":
        calibrated[-1] = calibrated[-2].copy()
    elif mutation == "missing_batch":
        cost["timing_groups"].pop()
    elif mutation == "duplicate_cell":
        cells[-1] = cells[-2].copy()
    elif mutation == "count":
        calibrated[-1]["signal_accepted"] = -1
    elif mutation == "interval":
        calibrated[-1]["signal_wilson_low"] = 1
    elif mutation == "units":
        # A throughput mistakenly based on µs in a nanosecond field must fail.
        cost["timing_groups"][0]["throughput_from_pooled_mean_events_per_second"] *= (
            1000
        )
    elif mutation == "nonfinite":
        cells[0]["mean_ns"] = float("nan")
    elif mutation == "exposure":
        science["actual_access"]["test_signal_model_evaluation_accessed"] = False
    with pytest.raises(ValueError):
        synthesis.derive(*aggregates)
