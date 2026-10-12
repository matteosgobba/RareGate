"""Synthetic aggregates and disposable boundary fixtures only; no scientific IO."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from test_frozen_synthesis import aggregates as historical_fixture

SPEC = importlib.util.spec_from_file_location(
    "signal_topology_synthesis",
    Path(__file__).parents[1] / "scripts/synthesize_signal_topologies.py",
)
synthesis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(synthesis)


def wilson(k, n):
    import math

    z = 1.959963984540054
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [c - h, c + h]


def update_point(row, point, b, s):
    row.update(
        background_accepted=b,
        signal_accepted=s,
        background_fpr=b / 150471,
        signal_efficiency=s / 100000,
        background_rejection=150471 / b,
    )
    for prefix, k, n in [("background", b, 150471), ("signal", s, 100000)]:
        low, high = wilson(k, n)
        row[prefix + "_wilson_low"], row[prefix + "_wilson_high"] = low, high
        point[prefix].update(
            accepted=k, total=n, efficiency=k / n, wilson_95=[low, high]
        )
    point["background"]["rejection"] = 150471 / b


@pytest.fixture
def inputs():
    two, cost, quality, cal, emp, cells = copy.deepcopy(
        historical_fixture.__wrapped__()
    )
    for row in cells:
        row["min_ns"] = row["p50_ns"] / 2
    cost["timing_cells"] = copy.deepcopy(cells)
    old = synthesis.old
    registry = two["identities"]["candidate_registry"]
    for identity, dtype in zip(registry, ["float64", "float32"], strict=True):
        identity["forward_dtype"] = dtype
    cost["frozen_models"] = copy.deepcopy(registry)
    store = dict(
        scientific_sha256="training",
        configuration_canonical_JSON_sha256="config",
        preprocessing_parameters_canonical_JSON_sha256="scaler",
        metadata_file_byte_sha256={"configuration.json": "bytes"},
    )
    transform = dict(
        file_byte_sha256="bytes",
        canonical_JSON_sha256="config",
        preprocessing_parameters_canonical_JSON_sha256="scaler",
    )
    two["identities"]["processed_store"] = store
    two["planned_Phase_B"] = dict(
        native_CPU_only=True, metrics=dict(score="FP64 casts before SSE")
    )
    two["receipt_lineage_Phase_B"] = {}
    for i, name in enumerate(synthesis.NAMES):
        evaluation = two["scientific_results"]["evaluations"][i]
        metrics = json.loads(json.dumps(evaluation["metrics"]))
        evaluation["metrics"] = metrics
        rows = [r for r in cal if r["candidate"] == name]
        erows = [r for r in emp if r["candidate"] == name]
        for j, (row, point) in enumerate(
            zip(rows, metrics["calibrated_thresholds"], strict=True)
        ):
            update_point(
                row,
                point,
                synthesis.BG_COUNTS[name][j],
                (1000, 500, 100, 2 if i == 0 else 56)[j],
            )
            update_point(
                erows[j],
                metrics["at_fixed_fpr"][j],
                synthesis.BG_COUNTS[name][j],
                int(row["signal_accepted"]),
            )
        for j, t in enumerate([0.5, 0.8, 0.9]):
            update_point(
                erows[4 + j],
                metrics["at_fixed_tpr"][j],
                int([0.6, 0.85, 0.95][j] * 150471),
                int(t * 100000),
            )
    frontier, operating = old.derive(two, cost, quality, cal, emp, cells)
    context = dict(
        status="completed_offline_synthesis_of_accepted_sources",
        canonical_scientific_identities_from_accepted_registry=copy.deepcopy(registry),
        processed_store_identity_from_accepted_registry_not_reopened=copy.deepcopy(
            store
        ),
        scientific_scope=dict(reference_batch=4096),
        scientific_reference=copy.deepcopy(quality),
        quality_cost_frontier=copy.deepcopy(frontier),
        cost_scope={},
    )
    three_quality = copy.deepcopy(quality)
    three_cal = copy.deepcopy(cal)
    three_emp = copy.deepcopy(emp)
    evaluations = copy.deepcopy(two["scientific_results"]["evaluations"])
    caches = []
    for i, (identity, evaluation, qrow) in enumerate(
        zip(registry, evaluations, three_quality, strict=True)
    ):
        name = identity["name"]
        qrow.update(
            roc_auc=qrow["roc_auc"] - 0.01,
            average_precision=qrow["average_precision"] - 0.02,
            model_scientific_sha256=identity["model_scientific_sha256"],
            calibration_scientific_sha256=identity["results_scientific_sha256"],
            new_signal_scientific_sha256="newsignal",
        )
        evaluation["metrics"].update(
            roc_auc=qrow["roc_auc"], average_precision=qrow["average_precision"]
        )
        evaluation["new_signal_scientific_sha256"] = "newsignal"
        cache = dict(
            path=f"opaque/{name}",
            file_byte_sha256=f"cache{i}",
            original_model_scientific_sha256=identity["model_scientific_sha256"],
            calibration_scientific_sha256=identity["results_scientific_sha256"],
            shape=[150471],
            dtype="<f8",
            bytes=1203896,
        )
        caches.append(cache)
        evaluation["reused_background_reference"] = copy.deepcopy(cache)
        two["receipt_lineage_Phase_B"][cache["path"]] = cache["file_byte_sha256"]
        for j, row in enumerate(r for r in three_cal if r["candidate"] == name):
            update_point(
                row,
                evaluation["metrics"]["calibrated_thresholds"][j],
                int(row["background_accepted"]),
                (800, 400, 50, 1 if i == 0 else 34)[j],
            )
    three_emp = [
        dict(
            row,
            point_kind="fixed_fpr"
            if row["kind"] == "descriptive_fixed_FPR"
            else "fixed_tpr",
            target_fpr=row["target"]
            if row["kind"] == "descriptive_fixed_FPR"
            else None,
            target_tpr=row["target"]
            if row["kind"] == "descriptive_fixed_TPR"
            else None,
        )
        for row in three_emp
    ]
    three = dict(
        task="0031",
        status="parent_accepted",
        reserved_consumed=True,
        new_campaign_retry_allowed=False,
        candidates=copy.deepcopy(registry),
        original_store=copy.deepcopy(store),
        transform=copy.deepcopy(transform),
        features=list(synthesis.FEATURES),
        prepared_manifest=dict(
            scientific_sha256="newsignal",
            scientific=dict(
                dtype="<f4",
                count=100000,
                features=list(synthesis.FEATURES),
                transform=copy.deepcopy(transform),
                original_training_scientific_sha256="training",
                transformation_sequence="sourceFP64_validate_sort_wrap→physicalFP32_all_particles→aggregateFP64→frozen_logs_scaler→featuresFP32",
            ),
        ),
        metrics_scope=copy.deepcopy(two["planned_Phase_B"]["metrics"]),
        background_shared=True,
        background_independent_generalization_measured=False,
        scientific_access={
            k: "YES"
            for k in [
                "original_test_background_model_evaluation_accessed",
                "original_test_signal_model_evaluation_accessed",
                "new_three_prong_signal_model_evaluation_accessed",
            ]
        },
        stages=[
            dict(
                phase=phase,
                parent_status="parent_accepted",
                dispatch=dict(returncode=0, child_reaped=True, within_deadline=True),
            )
            for phase in ["prepare", "PCA", "AE", "consolidate"]
        ],
        cached_background=caches,
        scientific_comparison=dict(evaluations=evaluations),
    )
    prior = []
    for a, b in zip(cal, three_cal, strict=True):
        row = dict(
            candidate=a["candidate"],
            target_fpr=a["target_fpr"],
            threshold=a["threshold"],
            shared_background_accepted=a["background_accepted"],
            shared_background_total=a["background_total"],
            shared_background_fpr=a["background_fpr"],
        )
        for label, op, qualities in [
            ("two_prong", a, quality),
            ("three_prong", b, three_quality),
        ]:
            for key in ["signal_accepted", "signal_total", "signal_efficiency"]:
                row[label + "_" + key] = op[key]
            arithmetic = synthesis.arithmetic(
                op["signal_accepted"],
                op["signal_total"],
                op["background_accepted"],
                op["background_total"],
            )
            for key in ["relative_acceptance", "selected_signal_fraction"]:
                row[label + "_" + key] = arithmetic[key]
            qrow = next(q for q in qualities if q["candidate"] == a["candidate"])
            for key in ["roc_auc", "average_precision"]:
                row[label + "_" + key] = qrow[key]
        prior.append(row)
    return dict(
        science=two,
        three=three,
        cost=cost,
        context=context,
        two_quality=quality,
        two_cal=cal,
        two_emp=emp,
        three_quality=three_quality,
        three_cal=three_cal,
        three_emp=three_emp,
        prior_comparison=prior,
        cells=cells,
        prior_cost=copy.deepcopy(frontier),
        prior_operating=copy.deepcopy(operating),
    )


def test_coverage_arithmetic_and_cost_scopes(inputs):
    data = synthesis.derive(inputs)
    assert [
        len(data[k])
        for k in [
            "global_quality",
            "calibrated_utility",
            "cross_topology",
            "quality_cost",
            "empirical_operating_points",
        ]
    ] == [4, 16, 8, 10, 28]
    strict = [
        r
        for r in data["calibrated_utility"]
        if r["candidate"] == synthesis.NAMES[1] and r["target_fpr"] == 0.001
    ]
    assert [r["selected_signal_fraction"] for r in strict] == pytest.approx(
        [56 / 172, 34 / 150]
    )
    assert all(r["observed_mixture_enrichment"] is False for r in strict)
    comparison = data["cross_topology"][-1]
    assert comparison["signal_efficiency_change_percentage_points"] == pytest.approx(
        -0.022
    )
    assert comparison["three_over_two_signal_efficiency_ratio"] == pytest.approx(
        34 / 56
    )
    assert comparison["three_minus_two_roc_auc"] == pytest.approx(-0.01)
    assert comparison["three_minus_two_AP"] == pytest.approx(-0.02)
    cost = data["quality_cost"][0]
    assert cost["pooled_600_invocation_mean_batch_ns"] == 4000  # Slow repetition kept.
    assert cost["throughput_from_pooled_mean_events_per_second"] == 250000
    assert cost["quality_reference_batch"] == 4096 and cost["cost_batch"] == 1
    assert cost["independently_measured_quality_at_cost_batch"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        "status",
        "cost_status",
        "identity",
        "orientation",
        "transform",
        "scaler",
        "features",
        "precision",
        "prepared_dtype",
        "prepared_count",
        "native",
        "score",
        "batch",
        "cache",
        "new_signal",
        "background",
        "count",
        "interval",
        "threshold",
        "missing_threshold",
        "duplicate_threshold",
        "empirical_missing",
        "empirical_duplicate",
        "empirical_kind",
        "quality_duplicate",
        "missing_cost",
        "cost_unit",
        "cost_outlier",
        "prior_comparison",
        "prior_cost",
        "prior_operating",
        "stage",
        "exposure",
        "prevalence",
    ],
)
def test_refuses_incompatible_or_incomplete_synthetic_evidence(inputs, mutation):
    three = inputs["three"]
    if mutation == "status":
        three["status"] = "body_complete"
    elif mutation == "cost_status":
        inputs["cost"]["comparison_success"] = False
    elif mutation == "identity":
        three["candidates"][0]["model_scientific_sha256"] = "other"
    elif mutation == "orientation":
        inputs["science"]["identities"]["candidate_registry"][0]["orientation"] = (
            "lower"
        )
    elif mutation == "transform":
        three["transform"]["file_byte_sha256"] = "other"
    elif mutation == "scaler":
        three["transform"]["preprocessing_parameters_canonical_JSON_sha256"] = "other"
    elif mutation == "features":
        three["features"].reverse()
    elif mutation == "precision":
        three["prepared_manifest"]["scientific"]["transformation_sequence"] = "allFP64"
    elif mutation == "prepared_dtype":
        three["prepared_manifest"]["scientific"]["dtype"] = "<f8"
    elif mutation == "prepared_count":
        three["prepared_manifest"]["scientific"]["count"] = 99999
    elif mutation == "native":
        inputs["science"]["planned_Phase_B"]["native_CPU_only"] = False
    elif mutation == "score":
        three["metrics_scope"]["score"] = "FP32 SSE"
    elif mutation == "batch":
        inputs["context"]["scientific_scope"]["reference_batch"] = 1024
    elif mutation == "cache":
        three["cached_background"][0]["file_byte_sha256"] = "other"
    elif mutation == "new_signal":
        inputs["three_quality"][0]["new_signal_scientific_sha256"] = "foreign"
    elif mutation == "background":
        inputs["three_cal"][0]["background_accepted"] += 1
    elif mutation == "count":
        inputs["three_cal"][0]["signal_total"] += 1
    elif mutation == "interval":
        inputs["three_cal"][0]["signal_wilson_low"] += 0.0001
    elif mutation == "threshold":
        inputs["three_cal"][0]["threshold"] += 0.01
    elif mutation == "missing_threshold":
        inputs["three_cal"].pop()
    elif mutation == "duplicate_threshold":
        inputs["three_cal"][-1] = copy.deepcopy(inputs["three_cal"][-2])
    elif mutation == "empirical_missing":
        inputs["three_emp"].pop()
    elif mutation == "empirical_duplicate":
        inputs["three_emp"][-1] = copy.deepcopy(inputs["three_emp"][-2])
    elif mutation == "empirical_kind":
        inputs["three_emp"][-1]["point_kind"] = "arbitrary"
    elif mutation == "quality_duplicate":
        inputs["three_quality"][-1] = copy.deepcopy(inputs["three_quality"][0])
    elif mutation == "missing_cost":
        inputs["cells"].pop()
    elif mutation == "cost_unit":
        inputs["cells"][2]["mean_ns"] *= 0.001
    elif mutation == "cost_outlier":
        inputs["cost"]["timing_groups"][0]["pooled_600_invocation_mean_ns"] = 900
    elif mutation == "prior_comparison":
        inputs["prior_comparison"][0]["three_prong_signal_accepted"] += 1
    elif mutation == "prior_cost":
        inputs["prior_cost"][0]["median_of_three_worker_p50_batch_ns"] += 1
    elif mutation == "prior_operating":
        inputs["prior_operating"][-1] = copy.deepcopy(inputs["prior_operating"][-2])
    elif mutation == "stage":
        three["stages"][0]["dispatch"]["child_reaped"] = False
    elif mutation == "exposure":
        three["scientific_access"][
            "new_three_prong_signal_model_evaluation_accessed"
        ] = "NO"
    elif mutation == "prevalence":
        inputs["three_quality"][0]["signal_prevalence"] = 0.5
    with pytest.raises((ValueError, KeyError)):
        synthesis.derive(inputs)


@pytest.mark.parametrize(
    "n,d,expected", [(0, 0, None), (1, 0, None), (0, 2, 0), (2, 4, 0.5)]
)
def test_undefined_ratios(n, d, expected):
    assert synthesis.ratio(n, d) == expected


def test_empty_slice_is_undefined():
    result = synthesis.arithmetic(0, 100, 0, 200)
    assert (
        result["relative_acceptance"]
        is result["selected_signal_fraction"]
        is result["observed_mixture_enrichment"]
        is None
    )


@pytest.mark.parametrize(
    "name",
    [
        "data/raw.h5",
        "results/evaluation/x/scores.npy",
        "data/fingerprints.npy",
        "../secret.json",
        "/tmp/input.json",
    ],
)
def test_input_boundary_before_open(tmp_path, monkeypatch, name):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unapproved file opened")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="allowlisted"):
        synthesis.read_source(tmp_path, name)


def test_missing_altered_and_symlink_source(tmp_path, monkeypatch):
    name = "docs/fixture.md"
    digest = hashlib.sha256(b"synthetic").hexdigest()
    monkeypatch.setattr(synthesis, "SOURCES", {name: digest})
    with pytest.raises(FileNotFoundError):
        synthesis.read_source(tmp_path, name)
    file = tmp_path / name
    file.parent.mkdir()
    file.write_bytes(b"altered")
    with pytest.raises(ValueError, match="Altered"):
        synthesis.read_source(tmp_path, name)
    file.unlink()
    file.symlink_to(tmp_path / "foreign")
    with pytest.raises(ValueError, match="Symlink"):
        synthesis.read_source(tmp_path, name)
    file.unlink()
    file.write_bytes(b"synthetic")
    assert synthesis.read_source(tmp_path, name) == b"synthetic"


def test_output_boundary_and_historical_preservation(tmp_path, inputs):
    before = copy.deepcopy(inputs)
    historical = tmp_path / "docs/history.md"
    historical.parent.mkdir()
    historical.write_text("unchanged")
    synthesis.derive(inputs)
    assert inputs == before and historical.read_text() == "unchanged"
    with pytest.raises(ValueError, match="Output"):
        synthesis.write_path(tmp_path, "task0027")
    parent = tmp_path / "results"
    parent.symlink_to(tmp_path / "foreign")
    with pytest.raises(ValueError, match="Symlink"):
        synthesis.write_path(tmp_path, "global")


def test_synthetic_render_and_json_csv_agreement(tmp_path, inputs):
    data = synthesis.derive(inputs)
    out = synthesis.write_outputs(data, inputs, tmp_path)
    assert out["new_access"]["new_score_or_curve_array_loads_in_Task0032"] == 0
    for key in ["quality_figure", "operating_figure", "cost_figure"]:
        file = tmp_path / synthesis.OUTPUTS[key]
        assert file.read_bytes().startswith(b"\x89PNG")
    saved = json.loads((tmp_path / synthesis.OUTPUTS["summary"]).read_text())
    assert saved["calibrated_utility"] == data["calibrated_utility"]
    for name, digest in saved["derived_output_file_byte_sha256"].items():
        assert hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == digest
