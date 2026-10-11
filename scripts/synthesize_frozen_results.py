"""Task0027: deterministic aggregate-only synthesis; no LatentTrigger imports.

Run from any directory with the existing environment. Reads only the nine pinned
curated sources below, writes the five Task0027 tables/figures. Scientific models,
populations, prepared inputs, score/curve arrays and operational routes are absent.
"""

import csv
import hashlib
import io
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("pca-v1", "compact-autoencoder-v2")
BATCHES = (1, 8, 32, 128, 1024)
TARGETS = (0.1, 0.05, 0.01, 0.001)
TABLES = "results/tables/final/"
FIGURES = "results/figures/final/"
SOURCES = {
    "docs/guarded-pca-ae-evaluation.md": "5f95107ccd7d5911c618007c7c857644571f726a2c0d94af71921b50aebcab02",
    TABLES
    + "task0026-guarded-pca-ae-evaluation-summary.json": "d72270e9807b1a2176d46be248ddb697d7a22e10cf5aac4904583ab4fae1e966",
    TABLES
    + "task0026-pca-ae-scientific-comparison.csv": "d3c3119f4bc20fb9a05c1a361d37caa5b7f0b1c8581177eed68eb4c7ba8a8824",
    TABLES
    + "task0026-pca-ae-calibrated-operating-points.csv": "5170f177094e5c8b7273d582650aa572da532986abd09713440a287580b3e886",
    TABLES
    + "task0026-pca-ae-empirical-operating-points.csv": "2a54dded7e88f2434f213e4f0927158d816849d5a4d84c7059ceb30ad412c0cd",
    FIGURES
    + "task0026-pca-ae-roc-pr.png": "2eaf396e9ab83cb8c6d3a0f94b198ff1825d2f3fab9af0634f46f9a30cf42c06",
    "docs/frozen-cpu-benchmark-v2.md": "04892664f5fe9945e698039a8879c09f51c48816c84715b6a43bce84fd6890c4",
    TABLES
    + "task0022-frozen-cpu-benchmark-v2-summary.json": "33c09221548ef56ef1b96f10c951161b65bea8d9565f2f3c100fd5f7a7c5744e",
    TABLES
    + "task0022-frozen-cpu-benchmark-v2-cells.csv": "ddd4d1ed21d11f28999687c757638238bb548e156061525a0c4ded368ed9d75b",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal_number(actual, expected):
    require(math.isfinite(float(actual)), "Nonfinite aggregate")
    require(
        math.isclose(float(actual), float(expected), rel_tol=2e-14, abs_tol=1e-15),
        f"Aggregate disagreement: {actual} != {expected}",
    )


def typed_rows(rows, text_fields):
    return [
        {k: v if k in text_fields else float(v) if v else None for k, v in r.items()}
        for r in rows
    ]


def check_point(row, point):
    equal_number(row["threshold"], point["threshold"])
    for prefix, role in (("background", "background"), ("signal", "signal")):
        p = point[role]
        total = int(row[f"{prefix}_total"])
        count = int(row[f"{prefix}_accepted"])
        require(total > 0 and 0 <= count <= total, "Invalid aggregate count")
        equal_number(row[f"{prefix}_total"], total)
        equal_number(row[f"{prefix}_accepted"], count)
        equal_number(total, p["total"])
        equal_number(count, p["accepted"])
        rate_key = "background_fpr" if prefix == "background" else "signal_efficiency"
        rate = row[rate_key]
        equal_number(rate, count / total)
        equal_number(rate, p["efficiency"])
        low, high = row[f"{prefix}_wilson_low"], row[f"{prefix}_wilson_high"]
        require(0 <= low <= rate <= high <= 1, "Invalid Wilson interval")
        for a, b in zip((low, high), p["wilson_95"], strict=True):
            equal_number(a, b)
    require(row["background_accepted"] > 0, "Expected finite rejection")
    equal_number(row["background_rejection"], 1 / row["background_fpr"])
    equal_number(row["background_rejection"], point["background"]["rejection"])
    require(row["zero_acceptance_upper_95"] is None, "Unexpected zero-tail bound")


def derive(science, cost, comparison, calibrated, empirical, cells):
    """Validate accepted cross-task aggregates and return exactly 10 + 8 rows."""
    require(
        science["phase"] == "A_and_authorized_B_complete_accepted", "Science status"
    )
    require(science["execution_Phase_B"]["status"] == "parent_accepted", "Lifecycle")
    require(
        cost["execution_status"] == "complete_accepted_consumed_no_retry", "Cost status"
    )
    require(cost["comparison_success"] is True, "Unaccepted cost")
    for role in ("test_background", "test_signal"):
        require(
            science["actual_access"][role + "_model_evaluation_accessed"], "Exposure"
        )
    registry = science["identities"]["candidate_registry"]
    require(tuple(r["name"] for r in registry) == NAMES, "Candidate registry")
    require(registry == cost["frozen_models"], "Incompatible scientific identities")
    evaluations = science["scientific_results"]["evaluations"]
    require(len(evaluations) == 2 and len(comparison) == 2, "Two candidates required")
    require(tuple(r["candidate"] for r in comparison) == NAMES, "Comparison identities")
    require(len(calibrated) == 8 and len(empirical) == 14, "Operating row coverage")
    require(len(cells) == 90, "Cost cell coverage")
    # Compare every historical cell/statistic; nanosecond units are explicit keys.
    by_cell = {(r["worker"], r["batch"], r["scope"]): r for r in cells}
    require(len(by_cell) == 90, "Duplicate cost cells")
    require(len(cost["timing_cells"]) == 90, "JSON cost coverage")
    for original in cost["timing_cells"]:
        key = (original["worker"], original["batch"], original["scope"])
        require(key in by_cell, "Missing cost cell")
        for k, value in original.items():
            if isinstance(value, str):
                require(by_cell[key][k] == value, "Cell identity/status mismatch")
            else:
                equal_number(by_cell[key][k], value)
    operating, frontier = [], []
    for name, identity, evaluation, quality in zip(
        NAMES, registry, evaluations, comparison, strict=True
    ):
        require(
            evaluation["model_scientific_sha256"]
            == identity["model_scientific_sha256"],
            "Model identity",
        )
        require(
            evaluation["calibration_scientific_sha256"]
            == identity["results_scientific_sha256"],
            "Calibration identity",
        )
        require(identity["orientation"] == "higher_is_more_anomalous", "Orientation")
        require(
            identity["threshold_decision"] == "score > threshold", "Strict decision"
        )
        require(
            identity["score_definition"] == "sum_squared_reconstruction_residual", "SSE"
        )
        require(
            identity["score_dtype"] == "float64"
            and identity["calibration_count"] == 74823,
            "Score/calibration provenance",
        )
        metrics = evaluation["metrics"]
        for k in (
            "roc_auc",
            "average_precision",
            "background_total",
            "signal_total",
            "signal_prevalence",
        ):
            equal_number(quality[k], metrics[k])
        equal_number(quality["background_total"], 150471)
        equal_number(quality["signal_total"], 100000)
        equal_number(quality["signal_prevalence"], 100000 / 250471)
        rows = [r for r in calibrated if r["candidate"] == name]
        require(
            tuple(r["target_fpr"] for r in rows) == TARGETS,
            "Frozen threshold coverage/order",
        )
        require(len(metrics["calibrated_thresholds"]) == 4, "JSON frozen coverage")
        for row, point, threshold in zip(
            rows, metrics["calibrated_thresholds"], identity["thresholds"], strict=True
        ):
            equal_number(row["target_fpr"], threshold["target_fpr"])
            equal_number(row["target_fpr"], point["target_fpr"])
            equal_number(row["threshold"], threshold["threshold"])
            check_point(row, point)
            derived = dict(row)
            for k in (
                "background_accepted",
                "background_total",
                "signal_accepted",
                "signal_total",
            ):
                derived[k] = int(derived[k])
            derived.update(
                nominal_target_percent=row["target_fpr"] * 100,
                background_fpr_percent=row["background_fpr"] * 100,
                signal_efficiency_percent=row["signal_efficiency"] * 100,
                relative_acceptance=row["signal_efficiency"] / row["background_fpr"],
                selected_signal_fraction=row["signal_accepted"]
                / (row["signal_accepted"] + row["background_accepted"]),
                initial_evaluated_signal_prevalence=quality["signal_prevalence"],
                interpretation_status="post-evaluation descriptive arithmetic from accepted aggregate counts",
            )
            derived["selected_signal_percent"] = (
                derived["selected_signal_fraction"] * 100
            )
            operating.append(derived)
        for kind, metric_key, target_key in (
            ("descriptive_fixed_FPR", "at_fixed_fpr", "target_fpr"),
            ("descriptive_fixed_TPR", "at_fixed_tpr", "target_tpr"),
        ):
            erows = [
                r for r in empirical if r["candidate"] == name and r["kind"] == kind
            ]
            points = metrics[metric_key]
            require(len(erows) == len(points), "Empirical coverage")
            for row, point in zip(erows, points, strict=True):
                equal_number(row["target"], point[target_key])
                require(
                    row["threshold_kind"] == point["threshold_kind"],
                    "Empirical cutoff semantics",
                )
                check_point(row, point)
        groups = [
            g
            for g in cost["timing_groups"]
            if g["model"] == name and g["scope"] == "adapter_decision"
        ]
        require(
            tuple(g["batch"] for g in groups) == BATCHES,
            "Ten adapter cost groups required",
        )
        for g in groups:
            worker_rows = [
                by_cell[(w, g["batch"], "adapter_decision")] for w in g["workers"]
            ]
            require(
                len(worker_rows) == 3 and len(set(g["workers"])) == 3,
                "Three independent workers",
            )
            require(
                all(r["count"] == 200 and r["model"] == name for r in worker_rows),
                "600 invocation pool",
            )
            for r, median, mean in zip(
                worker_rows, g["worker_p50_ns"], g["worker_mean_ns"], strict=True
            ):
                equal_number(r["p50_ns"], median)
                equal_number(r["mean_ns"], mean)
            p50 = g["median_of_worker_medians_ns"]
            mean = g["pooled_600_invocation_mean_ns"]
            require(mean > 0 and p50 > 0, "Invalid ns durations/units")
            equal_number(p50, statistics.median(g["worker_p50_ns"]))
            equal_number(mean, sum(g["worker_mean_ns"]) / 3)
            throughput = g["throughput_from_pooled_mean_events_per_second"]
            equal_number(throughput, g["batch"] * 1e9 / mean)
            row = dict(
                candidate=name,
                batch_size=g["batch"],
                cost_scope="adapter_decision_prepared_features",
                cost_task="0022",
                scientific_reference_task="0026",
                scientific_reference_batch_size=4096,
                roc_auc=quality["roc_auc"],
                average_precision=quality["average_precision"],
                model_scientific_sha256=identity["model_scientific_sha256"],
                median_of_three_worker_p50_batch_ns=p50,
                median_of_three_worker_p50_batch_us=p50 / 1000,
                pooled_600_invocation_mean_batch_ns=mean,
                pooled_600_invocation_mean_batch_us=mean / 1000,
                pooled_mean_amortized_ns_per_event=mean / g["batch"],
                pooled_mean_amortized_us_per_event=mean / g["batch"] / 1000,
                throughput_from_pooled_mean_events_per_second=throughput,
                invocations_per_worker=200,
                pooled_invocations=600,
            )
            for i, r in enumerate(worker_rows, 1):
                for k in (
                    "worker",
                    "p50_ns",
                    "mean_ns",
                    "max_ns",
                    "p95_ns",
                    "p99_ns",
                    "population_std_ns",
                ):
                    row[f"repetition_{i}_{k}"] = r[k]
            frontier.append(row)
    return frontier, operating


def read_sources():
    blobs = {}
    for path, expected in SOURCES.items():
        blob = (ROOT / path).read_bytes()
        require(
            hashlib.sha256(blob).hexdigest() == expected, f"Source byte drift: {path}"
        )
        blobs[path] = blob

    def document(stem):
        return json.loads(blobs[TABLES + stem + ".json"])

    def rows(stem, fields):
        return typed_rows(
            list(csv.DictReader(io.StringIO(blobs[TABLES + stem + ".csv"].decode()))),
            fields,
        )

    science = document("task0026-guarded-pca-ae-evaluation-summary")
    cost = document("task0022-frozen-cpu-benchmark-v2-summary")
    inputs = (
        science,
        cost,
        rows("task0026-pca-ae-scientific-comparison", {"candidate"}),
        rows("task0026-pca-ae-calibrated-operating-points", {"candidate"}),
        rows(
            "task0026-pca-ae-empirical-operating-points",
            {"candidate", "kind", "threshold_kind"},
        ),
        rows(
            "task0022-frozen-cpu-benchmark-v2-cells",
            {"worker", "model", "scope", "status"},
        ),
    )
    return inputs


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plot(frontier, operating):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    plt.rcParams.update(
        {
            "font.size": 10,
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    colors = {NAMES[0]: "#2466a0", NAMES[1]: "#c35b23"}
    labels = {NAMES[0]: "PCA-v1", NAMES[1]: "Compact AE v2"}
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.7))
    for ax, batch, field, scale, xlabel, title in zip(
        axes,
        (1, 1024),
        (
            "median_of_three_worker_p50_batch_us",
            "throughput_from_pooled_mean_events_per_second",
        ),
        (1, 1e6),
        (
            "Adapter B1 batch latency (µs)\nmedian of three worker p50s",
            "Adapter B1024 throughput (million events/s)\nB / pooled mean batch duration, 600 invocations",
        ),
        ("Single-event cost", "Batched cost"),
        strict=True,
    ):
        for name in NAMES:
            row = next(
                r
                for r in frontier
                if r["candidate"] == name and r["batch_size"] == batch
            )
            x, y = row[field] / scale, row["roc_auc"]
            ax.scatter(x, y, s=90, color=colors[name], zorder=3)
            ax.annotate(
                f"{labels[name]}\n{x:.3f}; AUC {y:.6f}",
                (x, y),
                xytext=(0, 12),
                textcoords="offset points",
                ha="center",
                fontsize=9,
            )
        ax.set(
            xlabel=xlabel,
            ylabel="Canonical ROC-AUC (fraction)",
            ylim=(0.42, 0.75),
            title=title,
        )
        ax.set_xlim((0, 34) if batch == 1 else (7, 27))
        ax.grid(alpha=0.2)
    fig.suptitle("Frozen native candidates: sampled quality/cost tradeoff", fontsize=13)
    fig.subplots_adjust(bottom=0.27, top=0.84, wspace=0.28)
    fig.text(
        0.5,
        0.035,
        "Quality: accepted Task0026 native B4096, complete held-out tails; no AUC error bars.\nCost: accepted Task0022 prepared dev features, separate CPU campaign; all outliers retained.\nTwo sampled candidates; no end-to-end or hardware-trigger performance claim.",
        ha="center",
        fontsize=9,
    )
    fig.savefig(
        ROOT / FIGURES / "task0027-quality-cost-frontier.png",
        dpi=180,
        metadata={"Software": "Task0027 aggregate-only Matplotlib"},
    )
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 6))
    for name in NAMES:
        for i, row in enumerate(r for r in operating if r["candidate"] == name):
            x, y = row["background_fpr"] * 100, row["signal_efficiency"] * 100
            xerr = [
                [x - row["background_wilson_low"] * 100],
                [row["background_wilson_high"] * 100 - x],
            ]
            yerr = [
                [y - row["signal_wilson_low"] * 100],
                [row["signal_wilson_high"] * 100 - y],
            ]
            ax.errorbar(
                x,
                y,
                xerr=xerr,
                yerr=yerr,
                fmt="o" if name == NAMES[0] else "s",
                color=colors[name],
                capsize=3,
                markersize=6,
                label=labels[name] if i == 0 else None,
                zorder=3,
            )
            label = f"α={row['nominal_target_percent']:g}%"
            if i == 3:
                label += (
                    f"\n{row['signal_accepted']} S / {row['background_accepted']} B"
                )
            offset = (12, 9) if name == NAMES[1] else (12, -23)
            if i == 3 and name == NAMES[1]:
                offset = (12, 24)
            ax.annotate(
                label,
                (x, y),
                xytext=offset,
                textcoords="offset points",
                fontsize=9,
                color=colors[name],
                bbox={
                    "facecolor": "white",
                    "edgecolor": "none",
                    "alpha": 0.95,
                    "pad": 0.3,
                }
                if i == 3 and name == NAMES[1]
                else None,
            )
    ax.plot(
        [0.04, 20],
        [0.04, 20],
        linestyle="--",
        color="#6e7379",
        lw=1.2,
        label="TPR = FPR",
    )
    ax.set(
        xscale="log",
        yscale="log",
        xlim=(0.04, 20),
        ylim=(0.0003, 50),
        xlabel="Achieved test-background FPR (%) — log scale",
        ylabel="Signal efficiency / TPR (%) — log scale",
        title="All eight original calibration-frozen operating points",
    )
    formatter = FuncFormatter(lambda x, _: f"{x:g}")
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.grid(which="major", alpha=0.2)
    ax.legend(loc="upper left", frameon=False)
    fig.subplots_adjust(bottom=0.24, right=0.88, top=0.9)
    fig.text(
        0.5,
        0.025,
        "α labels are nominal calibration FPRs; plotted coordinates are achieved rates (%).\nBars: existing conditional 95% Wilson intervals; no lines interpolate candidate points.\nAt α=0.1%, AE TPR 0.056% < FPR 0.077091%: no observed enrichment in this mixture.\nBackground N=150471; signal N=100000. Calibration/model/simulation uncertainty excluded.",
        ha="center",
        fontsize=9,
    )
    fig.savefig(
        ROOT / FIGURES / "task0027-calibrated-operating-points.png",
        dpi=180,
        metadata={"Software": "Task0027 aggregate-only Matplotlib"},
    )
    plt.close(fig)
    return matplotlib.__version__


def main():
    inputs = read_sources()
    frontier, operating = derive(*inputs)
    science, cost = inputs[:2]
    write_csv(ROOT / TABLES / "task0027-quality-cost-frontier.csv", frontier)
    write_csv(ROOT / TABLES / "task0027-operating-point-interpretation.csv", operating)
    matplotlib_version = plot(frontier, operating)
    summary = {
        "schema_version": 1,
        "task": "0027",
        "date": "2026-10-11",
        "timezone": "Europe/Rome",
        "status": "completed_offline_synthesis_of_accepted_sources",
        "repository_base": {
            "branch": "main",
            "upstream": "origin/main",
            "HEAD": "839f8cd68a87c776d84afa2e189e157536258b2d",
            "initial_index_and_worktree": "clean",
            "Task0026_Phase_B_local_commit_verified": True,
            "push_and_hosted_CI": "unverified",
        },
        "source_file_byte_sha256": SOURCES,
        "canonical_scientific_identities_from_accepted_registry": science["identities"][
            "candidate_registry"
        ],
        "processed_store_identity_from_accepted_registry_not_reopened": science[
            "identities"
        ]["processed_store"],
        "historical_status": {
            "Task0022": cost["execution_status"],
            "Task0023": "software validated; sole MPS availability check blocked; no physical/paired measurement",
            "Task0024": "accepted export/equivalence, not performance",
            "Task0025": "failed_consumed_no_retry; provisional ratios excluded",
            "Task0026": "authorized scientific evaluation parent_accepted_consumed_no_retry",
        },
        "candidate_capacity": {
            "PCA_retained_components": 6,
            "PCA_centered_non_whitened": True,
            "AE_architecture": [8, 6, 3, 6, 8],
            "AE_parameters": 155,
            "AE_forward_dtype": "float32",
            "canonical_score_dtype": "float64",
        },
        "scientific_scope": {
            "reference_batch": 4096,
            "complete_tails": [3015, 1696],
            "background_total": 150471,
            "signal_total": 100000,
            "signal_prevalence": 100000 / 250471,
            "orientation": "higher_is_more_anomalous",
            "decision": "score > threshold",
            "independently_measured_held_out_quality_for_each_cost_batch": False,
        },
        "cost_scope": {
            "public_adapter": "validation/wrapping/conversion/native forward/FP64 SSE/four strict decisions on prepared features",
            "prepared_dev_training_rows": 1024,
            "batch_sizes": list(BATCHES),
            "invocations_per_worker_per_cell": 200,
            "workers_per_candidate": 3,
            "pooled_invocations_per_group": 600,
            "outliers_filtered": False,
            "hardware_historical": "Apple M5 / Mac17,2 / 16 GB / shared host / arm64 macOS26.6.2",
            "effective_CPU_threads_historical": "Torch intra/inter 1; OpenMP 1; public Accelerate mode 1",
            "runtime_versions_historical": cost["campaign"]["runtime_versions"],
            "excluded": [
                "input loading",
                "raw processing",
                "feature construction/preprocessing",
                "queueing",
                "Task0026 whole campaign wall",
                "Task0025 provisional ratios",
            ],
        },
        "formulas": {
            "median_batch_ns": "median(worker_1_p50_ns,worker_2_p50_ns,worker_3_p50_ns)",
            "pooled_mean_batch_ns": "sum(worker_mean_ns * 200) / 600; accepted JSON value retained after arithmetic check",
            "throughput_events_per_second": "batch_size * 1e9 / pooled_mean_batch_ns",
            "mean_amortized_ns_per_event": "pooled_mean_batch_ns / batch_size",
            "ns_to_us": "ns / 1000",
            "fraction_to_percent": "fraction * 100",
            "relative_acceptance": "(signal_accepted/signal_total)/(background_accepted/background_total)",
            "selected_signal_fraction": "signal_accepted/(signal_accepted+background_accepted)",
            "initial_evaluated_prevalence": "100000/(100000+150471)",
        },
        "Task0027_arithmetic_status": "post-evaluation descriptive arithmetic from accepted aggregate counts; not newly preregistered Task0026 metrics or an additional experiment",
        "scientific_reference": inputs[2],
        "quality_cost_frontier": frontier,
        "operating_point_interpretation": operating,
        "exposure": {
            "test_background_model_evaluation_accessed": "YES",
            "test_signal_model_evaluation_accessed": "YES",
            "origin": "existing Task0026 exposure; not new Task0027 access",
            "existing_population_requests": 4,
            "existing_scored_presentations": 500942,
            "existing_unique_held_out_events": 250471,
            "can_be_reblinded": False,
        },
        "new_Task0027_counts": {
            "population_requests": 0,
            "test_population_requests": 0,
            "model_scoring": 0,
            "scored_events": 0,
            "custody_operations": 0,
            "optimizer_updates": 0,
            "model_execution": 0,
            "runtime_benchmarks": 0,
            "exports": 0,
            "MPS_checks": 0,
            "particle_updates": 0,
        },
        "particle": {
            "completed_updates": 192,
            "consumed_allowance": 192,
            "remaining_updates": 0,
            "canonical_training": "deferred",
        },
        "limits": [
            "Two sampled candidates; no continuous/universal Pareto frontier",
            "Global canonical quality is not per-cost-batch scientific validation",
            "Different retained dimensions 6 vs 3; no causal nonlinearity isolation",
            "AP/selected fractions depend on evaluated mixture, not LHC rates or physical purity",
            "Wilson intervals conditional on frozen threshold/sampling; no calibration/model/simulation uncertainty",
            "No AUC/AP, ratio or model-difference interval/significance result",
            "No strict-tail observed AE enrichment; no deeper tail extrapolation",
            "Bias diagnostics, other signals/populations and generalization unmeasured",
            "Numerical sampled gates not universal backend/held-out decision equivalence",
            "Shared-host warm-cache costs, fixed order, limited repetition/tail resolution and retained outliers",
            "No physical MPS proof, accepted ONNX performance, CoreML/reduced-precision/streaming/trigger suitability",
        ],
        "regeneration": {
            "command": ".venv/bin/python scripts/synthesize_frozen_results.py",
            "helper_validation_separate_from_historical_acceptance": True,
            "historical_Task0026_tests": "1259 full/portable acceptance preserved, not rerun and not coverage of this helper",
            "Task0027_helper_validation": "12 synthetic aggregate tests passed; scoped Ruff lint/format passed",
            "renderer": "Matplotlib "
            + matplotlib_version
            + " / Agg / DejaVu Sans / 180 dpi; same installed environment",
            "deterministic": "fixed source hashes, order, formulas and outputs; renderer bytes may differ across environments",
        },
    }
    summary["derived_output_file_byte_sha256"] = {
        p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
        for p in (
            TABLES + "task0027-quality-cost-frontier.csv",
            TABLES + "task0027-operating-point-interpretation.csv",
            FIGURES + "task0027-quality-cost-frontier.png",
            FIGURES + "task0027-calibrated-operating-points.png",
        )
    }
    (ROOT / TABLES / "task0027-frozen-scientific-synthesis-summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    print(
        "Validated pinned accepted aggregates; wrote 10 frontier rows, 8 operating rows, 2 figures and summary. New model/population work: zero."
    )


if __name__ == "__main__":
    main()
