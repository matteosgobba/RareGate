"""Task0032: pinned curated aggregates only, no scientific package imports.

Read boundary: exactly SOURCES; embedded operational paths are metadata, never
followed. Write boundary: exactly OUTPUTS. Reuses pure Task0027 validation in
memory, never its source reader/main/plot. Run with the installed environment:
    .venv/bin/python scripts/synthesize_signal_topologies.py
"""

import csv
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
from types import MappingProxyType

ROOT = Path(__file__).resolve().parents[1]
TABLES = "results/tables/final/"
FIGURES = "results/figures/final/"
SOURCES = MappingProxyType(
    {
        "docs/guarded-pca-ae-evaluation.md": "5f95107ccd7d5911c618007c7c857644571f726a2c0d94af71921b50aebcab02",
        "docs/local-three-prong-evaluation.md": "48f533c80d0a5746df8b5597e9f11b7d7714c011c3a7450c0b26284d7beea21c",
        "docs/frozen-cpu-benchmark-v2.md": "04892664f5fe9945e698039a8879c09f51c48816c84715b6a43bce84fd6890c4",
        "docs/scientific-synthesis.md": "48d3510c51535a65b38e7c18ea84421deeeb2cdc4f441ad0455d7c04212059f3",
        "results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json": "d72270e9807b1a2176d46be248ddb697d7a22e10cf5aac4904583ab4fae1e966",
        "results/tables/final/task0026-pca-ae-scientific-comparison.csv": "d3c3119f4bc20fb9a05c1a361d37caa5b7f0b1c8581177eed68eb4c7ba8a8824",
        "results/tables/final/task0026-pca-ae-calibrated-operating-points.csv": "5170f177094e5c8b7273d582650aa572da532986abd09713440a287580b3e886",
        "results/tables/final/task0026-pca-ae-empirical-operating-points.csv": "2a54dded7e88f2434f213e4f0927158d816849d5a4d84c7059ceb30ad412c0cd",
        "results/tables/final/task0031-local-three-prong-evaluation-summary.json": "1657524c4fa1efe795f8ba97c05cdf3bcf5c75ae8189dfde693a1c0437c09ead",
        "results/tables/final/task0031-three-prong-scientific-comparison.csv": "588f7a61a09c316d667ca5d1e3a55bedd59923d36923060fa238836b0a5a8853",
        "results/tables/final/task0031-three-prong-calibrated-operating-points.csv": "a631028a2716af74f020aac8b0f46081f67ac01705424970666bc0b698975beb",
        "results/tables/final/task0031-three-prong-empirical-operating-points.csv": "a74c4e05380e4bcfc7d782e382213b757a65cc0ecd24889652301e908fc140b0",
        "results/tables/final/task0031-two-vs-three-prong-comparison.csv": "e6f0d9bac0316d277364a10583f11688ae97a8fa23bee0c8751879266ae91665",
        "results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json": "33c09221548ef56ef1b96f10c951161b65bea8d9565f2f3c100fd5f7a7c5744e",
        "results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv": "ddd4d1ed21d11f28999687c757638238bb548e156061525a0c4ded368ed9d75b",
        "results/tables/final/task0027-frozen-scientific-synthesis-summary.json": "9e0e83fd217a81fba50acf4acd99d8d415164e027d167be458ba74dc57b92202",
        "results/tables/final/task0027-quality-cost-frontier.csv": "134f74694e2812b32756a278a5677da1e7442f838db4722c1e1ae1ec65296d67",
        "results/tables/final/task0027-operating-point-interpretation.csv": "f7e2d494ecc7bb85b937b37ca3550e7c03aed6b90a07aa9b5bf4201e5bb74ded",
        "results/figures/final/task0026-pca-ae-roc-pr.png": "2eaf396e9ab83cb8c6d3a0f94b198ff1825d2f3fab9af0634f46f9a30cf42c06",
        "results/figures/final/task0031-three-prong-roc-pr.png": "696f97ce8e1d9551cf74055e990d339ea44fd0b7a9472bc052d492350d037463",
    }
)
CODE_DEPENDENCY = (
    "scripts/synthesize_frozen_results.py",
    "563db15bd1021d5bdc8b3405046fdc82a031416e668743df065e2e24dee531b9",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_path(root, name):
    """Reject symlink redirection, including any existing ancestor."""
    root = Path(root).resolve()
    path = root / name
    require(path.is_relative_to(root), "Outside root")
    require(
        not any(p.is_symlink() for p in [path, *path.parents] if p != root),
        "Symlink boundary",
    )
    return path


def read_source(root, name):
    require(name in SOURCES, "Input not allowlisted")
    blob = bounded_path(root, name).read_bytes()
    require(
        hashlib.sha256(blob).hexdigest() == SOURCES[name], "Altered source: " + name
    )
    return blob


# A pinned pure analysis helper, not a controller/model/population module.
_old_path = bounded_path(ROOT, CODE_DEPENDENCY[0])
require(
    hashlib.sha256(_old_path.read_bytes()).hexdigest() == CODE_DEPENDENCY[1],
    "Historical pure helper changed",
)
_spec = importlib.util.spec_from_file_location("task0027_pure_synthesis", _old_path)
old = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(old)
NAMES, TARGETS, BATCHES = old.NAMES, old.TARGETS, old.BATCHES
FEATURES = (
    "multiplicity",
    "scalar_pt",
    "max_pt",
    "pt_balance",
    "weighted_eta_mean",
    "weighted_eta_std",
    "pt_concentration",
    "massless_event_mass",
)
BG_COUNTS = {NAMES[0]: (14922, 7362, 1416, 124), NAMES[1]: (14793, 7357, 1424, 116)}
ARITHMETIC = "Task0032 post-evaluation descriptive arithmetic from accepted aggregates"
OUTPUTS = MappingProxyType(
    {
        "global": TABLES + "task0032-global-quality.csv",
        "calibrated": TABLES + "task0032-calibrated-utility.csv",
        "comparison": TABLES + "task0032-cross-topology-comparison.csv",
        "cost": TABLES + "task0032-quality-cost.csv",
        "quality_figure": FIGURES + "task0032-global-quality.png",
        "operating_figure": FIGURES + "task0032-calibrated-utility.png",
        "cost_figure": FIGURES + "task0032-quality-cost.png",
        "summary": TABLES + "task0032-two-three-prong-synthesis-summary.json",
    }
)


def write_path(root, key):
    require(key in OUTPUTS, "Output not allowlisted")
    path = bounded_path(root, OUTPUTS[key])
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_inputs(root=ROOT):
    blobs = {name: read_source(root, name) for name in SOURCES}

    def doc(stem):
        return json.loads(blobs[TABLES + stem + ".json"])

    def rows(stem):
        records = list(
            csv.DictReader(io.StringIO(blobs[TABLES + stem + ".csv"].decode()))
        )
        text = {
            "candidate",
            "worker",
            "model",
            "scope",
            "status",
            "kind",
            "point_kind",
            "threshold_kind",
            "model_scientific_sha256",
            "calibration_scientific_sha256",
            "new_signal_scientific_sha256",
            "cost_scope",
            "cost_task",
            "scientific_reference_task",
            "interpretation_status",
            "scientific_reference_batch_size",
        }
        text.update(k for k in records[0] if k.endswith("_worker"))
        return old.typed_rows(records, text)

    return dict(
        science=doc("task0026-guarded-pca-ae-evaluation-summary"),
        three=doc("task0031-local-three-prong-evaluation-summary"),
        cost=doc("task0022-frozen-cpu-benchmark-v2-summary"),
        context=doc("task0027-frozen-scientific-synthesis-summary"),
        two_quality=rows("task0026-pca-ae-scientific-comparison"),
        two_cal=rows("task0026-pca-ae-calibrated-operating-points"),
        two_emp=rows("task0026-pca-ae-empirical-operating-points"),
        three_quality=rows("task0031-three-prong-scientific-comparison"),
        three_cal=rows("task0031-three-prong-calibrated-operating-points"),
        three_emp=rows("task0031-three-prong-empirical-operating-points"),
        prior_comparison=rows("task0031-two-vs-three-prong-comparison"),
        cells=rows("task0022-frozen-cpu-benchmark-v2-cells"),
        prior_cost=rows("task0027-quality-cost-frontier"),
        prior_operating=rows("task0027-operating-point-interpretation"),
    )


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def arithmetic(signal, signal_total, background, background_total):
    tpr, fpr = signal / signal_total, background / background_total
    selected = ratio(signal, signal + background)
    initial = signal_total / (signal_total + background_total)
    return dict(
        relative_acceptance=ratio(tpr, fpr),
        selected_signal_fraction=selected,
        initial_evaluated_signal_prevalence=initial,
        observed_mixture_enrichment=None if selected is None else selected > initial,
        arithmetic_status=ARITHMETIC,
    )


def validate_rate_intervals(row):
    # Check accepted Wilson arithmetic; copy the existing bounds into outputs.
    for prefix, rate in (
        ("background", "background_fpr"),
        ("signal", "signal_efficiency"),
    ):
        n, k = row[prefix + "_total"], row[prefix + "_accepted"]
        old.equal_number(n, int(n))
        old.equal_number(k, int(k))
        require(n > 0 and 0 <= k <= n, "Invalid counts")
        f, z = k / n, 1.959963984540054
        old.equal_number(row[rate], f)
        center = (f + z * z / (2 * n)) / (1 + z * z / n)
        half = z * math.sqrt(f * (1 - f) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        old.equal_number(row[prefix + "_wilson_low"], center - half)
        old.equal_number(row[prefix + "_wilson_high"], center + half)


def coverage(rows, keys, expected):
    actual = [tuple(row[k] for k in keys) for row in rows]
    require(
        len(actual) == len(set(actual)) and set(actual) == set(expected),
        "Missing/duplicate/incompatible row coverage",
    )


def normalize_empirical(rows):
    require(
        all(r["point_kind"] in {"fixed_fpr", "fixed_tpr"} for r in rows),
        "Empirical kind",
    )
    return [
        dict(
            row,
            kind="descriptive_fixed_"
            + ("FPR" if row["point_kind"] == "fixed_fpr" else "TPR"),
            target=row["target_fpr"]
            if row["point_kind"] == "fixed_fpr"
            else row["target_tpr"],
            zero_acceptance_upper_95=None,
        )
        for row in rows
    ]


def derive(inputs):
    two, three, cost, context = (
        inputs[k] for k in ("science", "three", "cost", "context")
    )
    frontier, _ = old.derive(
        two,
        cost,
        inputs["two_quality"],
        inputs["two_cal"],
        inputs["two_emp"],
        inputs["cells"],
    )
    require(
        three["task"] == "0031"
        and three["status"] == "parent_accepted"
        and three["reserved_consumed"]
        and not three["new_campaign_retry_allowed"],
        "Unaccepted three-prong campaign",
    )
    require(
        context["status"] == "completed_offline_synthesis_of_accepted_sources",
        "Task0027 status",
    )
    registry = two["identities"]["candidate_registry"]
    require(
        registry
        == three["candidates"]
        == context["canonical_scientific_identities_from_accepted_registry"],
        "Candidate identity mismatch",
    )
    store = two["identities"]["processed_store"]
    require(
        store
        == three["original_store"]
        == context["processed_store_identity_from_accepted_registry_not_reopened"],
        "Original store identity mismatch",
    )
    transform = three["transform"]
    prepared = three["prepared_manifest"]["scientific"]
    require(
        prepared["dtype"] == "<f4" and prepared["count"] == 100000,
        "Prepared feature representation/count",
    )
    require(
        tuple(three["features"]) == tuple(prepared["features"]) == FEATURES,
        "Feature order",
    )
    require(
        transform == prepared["transform"]
        and transform["file_byte_sha256"]
        == store["metadata_file_byte_sha256"]["configuration.json"]
        and transform["canonical_JSON_sha256"]
        == store["configuration_canonical_JSON_sha256"]
        and transform["preprocessing_parameters_canonical_JSON_sha256"]
        == store["preprocessing_parameters_canonical_JSON_sha256"]
        and prepared["original_training_scientific_sha256"]
        == store["scientific_sha256"],
        "Transform/scaler/training identity mismatch",
    )
    require(
        prepared["transformation_sequence"]
        == "sourceFP64_validate_sort_wrap→physicalFP32_all_particles→aggregateFP64→frozen_logs_scaler→featuresFP32",
        "Precision sequence",
    )
    require(
        two["planned_Phase_B"]["native_CPU_only"]
        and three["metrics_scope"] == two["planned_Phase_B"]["metrics"],
        "Native CPU/score semantics",
    )
    require(
        context["scientific_scope"]["reference_batch"] == 4096,
        "Canonical quality batch",
    )
    require(
        tuple(c["forward_dtype"] for c in registry) == ("float64", "float32"),
        "Native forward dtypes",
    )
    require(
        three["background_shared"]
        and not three["background_independent_generalization_measured"],
        "Shared background scope",
    )
    require(
        all(
            three["scientific_access"][k] == "YES"
            for k in [
                "original_test_background_model_evaluation_accessed",
                "original_test_signal_model_evaluation_accessed",
                "new_three_prong_signal_model_evaluation_accessed",
            ]
        ),
        "Historical exposure",
    )
    require(
        [s["phase"] for s in three["stages"]] == ["prepare", "PCA", "AE", "consolidate"]
        and all(
            s["parent_status"] == "parent_accepted"
            and s["dispatch"]["returncode"] == 0
            and s["dispatch"]["child_reaped"]
            and s["dispatch"]["within_deadline"]
            for s in three["stages"]
        ),
        "Accepted stage lifecycle",
    )
    for cache, identity, evaluation in zip(
        three["cached_background"],
        registry,
        three["scientific_comparison"]["evaluations"],
        strict=True,
    ):
        require(
            cache == evaluation["reused_background_reference"]
            and cache["file_byte_sha256"]
            == two["receipt_lineage_Phase_B"][cache["path"]]
            and cache["original_model_scientific_sha256"]
            == identity["model_scientific_sha256"]
            and cache["calibration_scientific_sha256"]
            == identity["results_scientific_sha256"]
            and cache["shape"] == [150471]
            and cache["dtype"] == "<f8"
            and cache["bytes"] == 1203896,
            "Background reference identity mismatch",
        )
    require(len(three["cached_background"]) == 2, "Two background references")
    for row, evaluation in zip(
        inputs["three_quality"],
        three["scientific_comparison"]["evaluations"],
        strict=True,
    ):
        require(
            row["new_signal_scientific_sha256"]
            == evaluation["new_signal_scientific_sha256"]
            == three["prepared_manifest"]["scientific_sha256"],
            "New signal identity",
        )
    # Validate three-prong with the same pure historical metric/cost checks.
    three_emp = normalize_empirical(inputs["three_emp"])
    adapted = dict(two, scientific_results=three["scientific_comparison"])
    old.derive(
        adapted,
        cost,
        inputs["three_quality"],
        inputs["three_cal"],
        three_emp,
        inputs["cells"],
    )
    expected = [(n, t) for n in NAMES for t in TARGETS]
    for key in ("two_cal", "three_cal", "prior_comparison"):
        coverage(inputs[key], ("candidate", "target_fpr"), expected)
    for rows in (inputs["two_emp"], three_emp):
        coverage(
            rows,
            ("candidate", "kind", "target"),
            [(n, "descriptive_fixed_FPR", t) for n in NAMES for t in TARGETS]
            + [(n, "descriptive_fixed_TPR", t) for n in NAMES for t in (0.5, 0.8, 0.9)],
        )
    for rows in (inputs["two_cal"], inputs["three_cal"], inputs["two_emp"], three_emp):
        for row in rows:
            validate_rate_intervals(row)
    global_rows, operating, comparisons, empirical = [], [], [], []
    for topology, quality, cal, emp, reference in [
        (
            "two_prong",
            inputs["two_quality"],
            inputs["two_cal"],
            inputs["two_emp"],
            "0026",
        ),
        (
            "three_prong",
            inputs["three_quality"],
            inputs["three_cal"],
            three_emp,
            "0031",
        ),
    ]:
        for row, identity in zip(quality, registry, strict=True):
            require(
                0 <= row["roc_auc"] <= 1 and 0 <= row["average_precision"] <= 1,
                "Invalid global quality",
            )
            for field in ["model_scientific_sha256", "calibration_scientific_sha256"]:
                if field in row:
                    require(
                        row[field]
                        == identity[
                            "model_scientific_sha256"
                            if field.startswith("model")
                            else "results_scientific_sha256"
                        ],
                        "CSV scientific identity",
                    )
            global_rows.append(
                dict(
                    candidate=row["candidate"],
                    topology=topology,
                    accepted_task=reference,
                    **{
                        k: row[k]
                        for k in [
                            "roc_auc",
                            "average_precision",
                            "background_total",
                            "signal_total",
                            "signal_prevalence",
                        ]
                    },
                    quality_reference_batch=4096,
                    model_scientific_sha256=identity["model_scientific_sha256"],
                    calibration_scientific_sha256=identity["results_scientific_sha256"],
                )
            )
        for row in cal:
            index = TARGETS.index(row["target_fpr"])
            require(
                row["background_accepted"] == BG_COUNTS[row["candidate"]][index],
                "Fixed historical background count",
            )
            out = {
                k: v
                for k, v in row.items()
                if k not in ["relative_acceptance", "selected_signal_fraction"]
            }
            out.update(
                topology=topology,
                accepted_task=reference,
                **arithmetic(
                    row["signal_accepted"],
                    row["signal_total"],
                    row["background_accepted"],
                    row["background_total"],
                ),
            )
            out.update(
                background_fpr_percent=100 * row["background_fpr"],
                signal_efficiency_percent=100 * row["signal_efficiency"],
                selected_signal_percent=100 * out["selected_signal_fraction"],
            )
            operating.append(out)
        empirical.extend(
            dict(
                row,
                topology=topology,
                accepted_task=reference,
                scope="descriptive attainable ROC evidence; never replaces calibration",
            )
            for row in emp
        )
    for name, target in expected:
        a, b = [
            next(
                r
                for r in operating
                if r["candidate"] == name
                and r["target_fpr"] == target
                and r["topology"] == topology
            )
            for topology in ["two_prong", "three_prong"]
        ]
        for k in a:
            if k.startswith("background_") or k == "threshold":
                require(a[k] == b[k], "Shared background/threshold disagreement")
        qa, qb = [
            next(
                r for r in global_rows if r["candidate"] == name and r["topology"] == t
            )
            for t in ["two_prong", "three_prong"]
        ]
        out = dict(
            candidate=name,
            target_fpr=target,
            threshold=a["threshold"],
            shared_background_accepted=a["background_accepted"],
            shared_background_total=a["background_total"],
            shared_background_fpr=a["background_fpr"],
        )
        for label, row, qrow in [("two_prong", a, qa), ("three_prong", b, qb)]:
            for k in [
                "signal_accepted",
                "signal_total",
                "signal_efficiency",
                "relative_acceptance",
                "selected_signal_fraction",
            ]:
                out[label + "_" + k] = row[k]
            for k in ["roc_auc", "average_precision"]:
                out[label + "_" + k] = qrow[k]
        prior = next(
            r
            for r in inputs["prior_comparison"]
            if r["candidate"] == name and r["target_fpr"] == target
        )
        for k, v in out.items():
            if isinstance(v, str):
                require(prior[k] == v, "Historical comparison candidate")
            else:
                old.equal_number(prior[k], v)
        out.update(
            three_minus_two_roc_auc=qb["roc_auc"] - qa["roc_auc"],
            three_minus_two_AP=qb["average_precision"] - qa["average_precision"],
            signal_efficiency_change_percentage_points=100
            * (b["signal_efficiency"] - a["signal_efficiency"]),
            three_over_two_signal_efficiency_ratio=ratio(
                b["signal_efficiency"], a["signal_efficiency"]
            ),
            arithmetic_status=ARITHMETIC,
        )
        comparisons.append(out)
    # Historical Task0027 tables/JSON must agree, without retrofitting that task.
    require(
        inputs["two_quality"] == context["scientific_reference"],
        "Task0027 scientific consistency",
    )
    require(frontier == context["quality_cost_frontier"], "Task0027 CPU consistency")
    require(
        len(inputs["prior_cost"]) == 10 and len(inputs["prior_operating"]) == 8,
        "Task0027 table coverage",
    )
    for a, b in zip(frontier, inputs["prior_cost"], strict=True):
        for k, v in a.items():
            if isinstance(v, str):
                require(str(b[k]) == v, "Task0027 cost label")
            else:
                old.equal_number(b[k], v)
    coverage(inputs["prior_operating"], ("candidate", "target_fpr"), expected)
    coverage(
        inputs["prior_cost"],
        ("candidate", "batch_size"),
        [(n, b) for n in NAMES for b in BATCHES],
    )
    for r in inputs["prior_operating"]:
        row = next(
            x
            for x in operating
            if x["topology"] == "two_prong"
            and x["candidate"] == r["candidate"]
            and x["target_fpr"] == r["target_fpr"]
        )
        for k in ["relative_acceptance", "selected_signal_fraction"]:
            old.equal_number(r[k], row[k])
    costs = []
    for row in frontier:
        out = {
            k: v
            for k, v in row.items()
            if k
            not in [
                "roc_auc",
                "average_precision",
                "scientific_reference_task",
                "scientific_reference_batch_size",
                "batch_size",
            ]
        }
        out.update(
            cost_batch=row["batch_size"],
            quality_reference_batch=4096,
            independently_measured_quality_at_cost_batch=False,
            shared_background=True,
        )
        for topology in ["two_prong", "three_prong"]:
            qrow = next(
                r
                for r in global_rows
                if r["candidate"] == row["candidate"] and r["topology"] == topology
            )
            for metric in ["roc_auc", "average_precision"]:
                out[topology + "_" + metric] = qrow[metric]
            out[topology + "_quality_task"] = qrow["accepted_task"]
        for repetition in (1, 2, 3):
            cell = next(
                c
                for c in inputs["cells"]
                if c["worker"] == out[f"repetition_{repetition}_worker"]
                and c["batch"] == out["cost_batch"]
                and c["scope"] == "adapter_decision"
            )
            out[f"repetition_{repetition}_min_ns"] = cell["min_ns"]
        costs.append(out)
    for row in global_rows + operating + comparisons + empirical:
        for key, value in list(row.items()):
            if (
                key.endswith(("_accepted", "_total"))
                or key == "quality_reference_batch"
            ):
                row[key] = int(value)
    return dict(
        global_quality=global_rows,
        calibrated_utility=operating,
        cross_topology=comparisons,
        quality_cost=costs,
        empirical_operating_points=empirical,
    )


def plot_outputs(data, root=ROOT):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update(
        {
            "font.size": 10,
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    colors = {NAMES[0]: "#2466a0", NAMES[1]: "#ba4e22"}
    labels = {NAMES[0]: "PCA-v1", NAMES[1]: "Compact AE v2"}
    topologies = ("two_prong", "three_prong")
    topology_labels = {"two_prong": "Two prong", "three_prong": "Three prong"}
    markers = {"two_prong": "o", "three_prong": "s"}
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.2))
    for ax, metric, title in zip(
        axes,
        ["roc_auc", "average_precision"],
        ["ROC-AUC", "Average Precision"],
        strict=True,
    ):
        for i, name in enumerate(NAMES):
            rows = [
                next(
                    r
                    for r in data["global_quality"]
                    if r["candidate"] == name and r["topology"] == t
                )
                for t in topologies
            ]
            # Paired categorical guide, not a model or curve interpolation.
            ax.plot(
                [i - 0.13, i + 0.13],
                [r[metric] for r in rows],
                color=colors[name],
                lw=1,
                alpha=0.5,
            )
            for x, row, t in zip([i - 0.13, i + 0.13], rows, topologies, strict=True):
                ax.scatter(
                    x,
                    row[metric],
                    color=colors[name],
                    marker=markers[t],
                    s=65,
                    zorder=3,
                )
                ax.annotate(
                    f"{row[metric]:.6f}",
                    (x, row[metric]),
                    xytext=(
                        -6 if t == "two_prong" else 6,
                        13 if t == "two_prong" else -20,
                    ),
                    textcoords="offset points",
                    ha="right" if t == "two_prong" else "left",
                    fontsize=9,
                )
        reference = 0.5 if metric == "roc_auc" else 100000 / 250471
        ax.axhline(
            reference,
            color="#777777",
            ls="--",
            lw=1,
            label="AUC 0.5" if metric == "roc_auc" else "Mixture prevalence 0.399248",
        )
        ax.set(
            xticks=[0, 1],
            xticklabels=[labels[n] for n in NAMES],
            xlim=(-0.55, 1.55),
            ylim=(0, 1),
            ylabel=title + " (fraction)",
            title=title,
        )
        ax.grid(axis="y", alpha=0.2)
        ax.legend(loc="upper left", fontsize=8)
    fig.legend(
        handles=[
            Line2D(
                [],
                [],
                marker=markers[t],
                color="#333333",
                linestyle="none",
                label=topology_labels[t],
            )
            for t in topologies
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.89),
        ncol=2,
        frameon=False,
    )
    fig.suptitle("Frozen candidates across two declared signal samples", fontsize=13)
    fig.subplots_adjust(top=0.76, bottom=0.26, wspace=0.25)
    fig.text(
        0.5,
        0.045,
        "Quality: canonical CPU B4096; 100000 signal / 150471 shared background per mixture.\nShared background is historical Task0026 evidence; no AUC/AP intervals or significance test.\nAP reference is evaluated prevalence, not a physical LHC signal rate.",
        ha="center",
        fontsize=9,
    )
    fig.savefig(
        write_path(root, "quality_figure"),
        dpi=180,
        metadata={"Software": "Task0032 pinned aggregate synthesis"},
    )
    plt.close(fig)

    # Separate candidate panels avoid hiding the one-/two-event PCA strict tail.
    fig, axes = plt.subplots(1, 2, figsize=(11, 6))
    for ax, name in zip(axes, NAMES, strict=True):
        for t in topologies:
            rows = [
                r
                for r in data["calibrated_utility"]
                if r["candidate"] == name and r["topology"] == t
            ]
            for row in rows:
                x, y = 100 * row["background_fpr"], 100 * row["signal_efficiency"]
                ax.errorbar(
                    x,
                    y,
                    xerr=[
                        [x - 100 * row["background_wilson_low"]],
                        [100 * row["background_wilson_high"] - x],
                    ],
                    yerr=[
                        [y - 100 * row["signal_wilson_low"]],
                        [100 * row["signal_wilson_high"] - y],
                    ],
                    fmt=markers[t],
                    color=colors[name],
                    markerfacecolor=colors[name] if t == "two_prong" else "white",
                    capsize=3,
                    markersize=6,
                    label=topology_labels[t] if row == rows[0] else None,
                    zorder=3,
                )
            strict = rows[-1]
            ax.text(
                0.03,
                0.96 if t == "two_prong" else 0.89,
                f"{topology_labels[t]} strict: {int(strict['signal_accepted'])} S / {int(strict['background_accepted'])} B",
                transform=ax.transAxes,
                va="top",
                fontsize=9,
            )
        ax.plot(
            [0.05, 15], [0.05, 15], ls="--", color="#777777", lw=1, label="TPR = FPR"
        )
        ax.set(
            xscale="log",
            yscale="log",
            xlim=(0.05, 15),
            ylim=(0.0001, 40),
            xlabel="Achieved background FPR (%) — log scale",
            ylabel="Signal efficiency (%) — log scale",
            title=labels[name],
        )
        ax.grid(alpha=0.2, which="both")
        ax.legend(loc="lower right", fontsize=8)
    fig.suptitle("All sixteen frozen calibrated operating points", fontsize=13)
    fig.subplots_adjust(bottom=0.24, top=0.86, wspace=0.3)
    fig.text(
        0.5,
        0.045,
        "100000 signal / 150471 background per topology; background counts and intervals are shared.\nBoth axes logarithmic to resolve low acceptance; points are unconnected, not a reconstructed ROC.\nBars copy accepted conditional Wilson 95% rate intervals; all original thresholds retained.",
        ha="center",
        fontsize=9,
    )
    fig.savefig(
        write_path(root, "operating_figure"),
        dpi=180,
        metadata={"Software": "Task0032 pinned aggregate synthesis"},
    )
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.6))
    for ax, t in zip(axes, topologies, strict=True):
        for name in NAMES:
            r = next(
                r
                for r in data["quality_cost"]
                if r["candidate"] == name and r["cost_batch"] == 1
            )
            x, y = r["median_of_three_worker_p50_batch_us"], r[t + "_roc_auc"]
            ax.scatter(x, y, color=colors[name], marker=markers[t], s=80, zorder=3)
            ax.annotate(
                f"{labels[name]}\n{x:.3f} µs; AUC {y:.6f}",
                (x, y),
                xytext=(0, 14),
                textcoords="offset points",
                ha="center",
                fontsize=9,
            )
        ax.set(
            xlim=(0, 34),
            ylim=(0, 1),
            xlabel="Historical adapter B1 batch latency (µs)\nmedian of three worker p50 values",
            ylabel="Canonical B4096 ROC-AUC (fraction)",
            title=topology_labels[t],
        )
        ax.grid(alpha=0.2)
    fig.suptitle(
        "Sampled quality/cost tradeoff at one historical adapter batch", fontsize=13
    )
    fig.subplots_adjust(bottom=0.28, top=0.84, wspace=0.26)
    fig.text(
        0.5,
        0.045,
        "Cost: accepted Task0022 native CPU, 1024 preloaded prepared dev-training rows; outliers retained.\nQuality: Task0026 / Task0031 B4096 reference, 100000 signal / 150471 shared background.\nNo quality measured anew at B1, combined utility score, deployment optimum or trigger-rate claim.",
        ha="center",
        fontsize=9,
    )
    fig.savefig(
        write_path(root, "cost_figure"),
        dpi=180,
        metadata={"Software": "Task0032 pinned aggregate synthesis"},
    )
    plt.close(fig)


def write_outputs(data, inputs, root=ROOT):
    for key, field in [
        ("global", "global_quality"),
        ("calibrated", "calibrated_utility"),
        ("comparison", "cross_topology"),
        ("cost", "quality_cost"),
    ]:
        old.write_csv(write_path(root, key), data[field])
    plot_outputs(data, root)
    identities = inputs["science"]["identities"]
    summary = dict(
        task="0032",
        date="2026-10-12",
        timezone="Europe/Rome",
        status="completed_offline_synthesis_of_accepted_sources",
        source_file_byte_sha256=dict(SOURCES),
        pure_code_dependency_file_byte_sha256={CODE_DEPENDENCY[0]: CODE_DEPENDENCY[1]},
        helper_file_byte_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        accepted_source_status=dict(
            Task0022=inputs["cost"]["execution_status"],
            Task0026=inputs["science"]["execution_Phase_B"]["status"],
            Task0031=inputs["three"]["status"],
            Task0027=inputs["context"]["status"],
        ),
        canonical_scientific_identities=identities["candidate_registry"],
        original_store_identity_recorded_not_reopened=identities["processed_store"],
        transform_identity_recorded_not_reopened=inputs["three"]["transform"],
        feature_order=list(FEATURES),
        signal_identities=dict(
            two_prong_processed_scientific_sha256=identities["processed_store"][
                "scientific_sha256"
            ],
            three_prong_prepared_scientific_sha256=inputs["three"]["prepared_manifest"][
                "scientific_sha256"
            ],
        ),
        shared_background_references_recorded_not_loaded=inputs["three"][
            "cached_background"
        ],
        shared_background_independent_replications=0,
        shared_background_historical_measurements_per_candidate=1,
        scientific_scope=inputs["context"]["scientific_scope"],
        cost_scope=inputs["context"]["cost_scope"],
        new_access=dict(
            original_test_background_model_evaluation_accessed="YES",
            original_test_signal_model_evaluation_accessed="YES",
            three_prong_signal_model_evaluation_accessed="YES",
            new_population_accesses_in_Task0032=0,
            new_score_or_curve_array_loads_in_Task0032=0,
            new_model_scoring_in_Task0032=0,
            new_fingerprint_numeric_loads_in_Task0032=0,
            optimizer_updates_in_Task0032=0,
            downloads_in_Task0032=0,
        ),
        arithmetic_status=ARITHMETIC,
        formulas=dict(
            three_minus_two_AUC="AUC_three - AUC_two",
            three_minus_two_AP="AP_three - AP_two",
            signal_efficiency_change_percentage_points="100*(TPR_three-TPR_two)",
            three_over_two_efficiency_ratio="TPR_three/TPR_two; null if TPR_two=0",
            relative_acceptance="(signal_accepted/signal_total)/(background_accepted/background_total); null if FPR=0",
            selected_signal_fraction="signal_accepted/(signal_accepted+background_accepted); null if selected_count=0",
            observed_mixture_enrichment="selected_signal_fraction > initial_evaluated_signal_prevalence; null if undefined",
            percent="100*fraction",
            microseconds="nanoseconds/1000",
            pooled_mean="sum(count_i*mean_ns_i)/600; each of three counts is200",
            throughput_events_per_second="cost_batch*1e9/pooled_mean_batch_ns; never average reciprocals",
            amortized_nanoseconds_per_event="pooled_mean_batch_ns/cost_batch",
        ),
        historical_outcomes=dict(
            Task0025="failed_consumed_provisional_ratios",
            Task0028="failed_consumed",
            Task0029="failed_consumed",
            Task0030="accepted_acquisition_consumed",
            Task0031="accepted_scientific_campaign_consumed",
            particle="192/192_consumed_canonical_deferred",
        ),
        coverage=dict(
            candidates=2,
            topologies=2,
            global_quality_rows=4,
            calibrated_rows=16,
            cross_topology_rows=8,
            adapter_cost_groups=10,
            empirical_rows=28,
        ),
        limitations=[
            "shared previously exposed background is not independent FPR replication/generalization",
            "exact fingerprint disjointness is not complete statistical/simulation independence",
            "preselected simulation and evaluated prevalence are not physical LHC rates/trigger utility",
            "PCA6 vs AE3 latent dimensions do not isolate nonlinearity; residual magnitudes do not rank discrimination",
            "copied conditional Wilson rates exclude calibration/model/simulation uncertainty",
            "no AUC/AP/difference/ratio interval, significance, subgroup analysis or mechanism established",
            "historical cost batches1–1024 and canonical quality B4096 have different scopes",
            "all evaluated populations remain exposed; future confirmation needs independent protocol/population",
        ],
        baseline_study="complete_within_declared_frozen_two_three_prong_scope",
        recommended_decision="close/preserve baseline; decide whether to authorize explicitly exploratory feature/score-tail diagnostics on exposed samples; require independent evaluation before confirmation of any informed model development",
        subsequent_task_launched=False,
        dependencies_changed=False,
        hosted_CI_success_claimed=False,
        regeneration=".venv/bin/python scripts/synthesize_signal_topologies.py",
        **data,
    )
    summary["derived_output_file_byte_sha256"] = {
        OUTPUTS[k]: hashlib.sha256(
            bounded_path(root, OUTPUTS[k]).read_bytes()
        ).hexdigest()
        for k in OUTPUTS
        if k != "summary"
    }
    write_path(root, "summary").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    return summary


def main():
    inputs = load_inputs()
    data = derive(inputs)
    references = [
        (0.4684886579473786, 0.36437915494963025),
        (0.6600638025267328, 0.5474272683246686),
        (0.4629531325637498, 0.36022029761655994),
        (0.5858771149922577, 0.479971651666809),
    ]
    for row, (auc, ap) in zip(data["global_quality"], references, strict=True):
        old.equal_number(row["roc_auc"], auc)
        old.equal_number(row["average_precision"], ap)
    for name, expected in zip(NAMES, [8.125, 24.708], strict=True):
        row = next(
            r
            for r in data["quality_cost"]
            if r["candidate"] == name and r["cost_batch"] == 1
        )
        old.equal_number(row["median_of_three_worker_p50_batch_us"], expected)
    # Bound evidence hashes recorded in older curated summaries, without following paths.
    for record in inputs["science"]["curated_outputs"]:
        require(
            SOURCES[record["path"]] == record["file_byte_sha256"],
            "Task0026 curated lineage",
        )
    for name, digest in inputs["three"]["curated_artifacts_file_byte_sha256"].items():
        require(SOURCES[name] == digest, "Task0031 curated lineage")
    for name, digest in inputs["context"]["source_file_byte_sha256"].items():
        require(SOURCES[name] == digest, "Task0027 curated source lineage")
    write_outputs(data, inputs)
    print(
        "Task0032 offline synthesis complete: 4 global / 16 calibrated / 8 comparisons / 10 cost groups; all new access/scoring counts zero"
    )


if __name__ == "__main__":
    main()
