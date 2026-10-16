"""Owned scientific curves/aggregates only; no original cache/signal numeric reload."""

import csv

import numpy as np

from raregate.benchmarks import protocol as p
from raregate.evaluation import local_three_prong_protocol as q


def write_csv(path, rows, fields=None):
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=fields or list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def calibrated_row(name, point):
    bg, sig = point["background"], point["signal"]
    ar = point["preregistered_arithmetic"]
    return dict(
        candidate=name,
        target_fpr=point["target_fpr"],
        threshold=point["threshold"],
        background_accepted=bg["accepted"],
        background_total=bg["total"],
        background_fpr=bg["efficiency"],
        background_wilson_low=bg["wilson_95"][0],
        background_wilson_high=bg["wilson_95"][1],
        background_rejection=bg["rejection"],
        zero_acceptance_upper_95=bg["zero_acceptance_upper_95"],
        signal_accepted=sig["accepted"],
        signal_total=sig["total"],
        signal_efficiency=sig["efficiency"],
        signal_wilson_low=sig["wilson_95"][0],
        signal_wilson_high=sig["wilson_95"][1],
        relative_acceptance=ar["relative_acceptance"],
        selected_signal_fraction=ar["selected_signal_fraction"],
    )


def reporting(root, spec, base, directory, audit, guard):
    q.require(
        [c["name"] for c in spec["candidates"]] == ["pca-v1", "compact-autoencoder-v2"],
        "Fixed complete candidate pair",
    )
    metrics_access = audit.request("reporting_owned_metrics", 2, source=str(base))
    evaluations = []
    for stage, candidate in zip(("PCA", "AE"), spec["candidates"], strict=True):
        guard.check()
        doc = p.read(base / stage / "evaluation.json")
        guard.check()
        audit.read(metrics_access, 1)
        science = doc["scientific"]
        q.require(
            p.digest(science) == doc["scientific_sha256"]
            and science["model_scientific_sha256"]
            == candidate["model_scientific_sha256"]
            and science["calibration_scientific_sha256"]
            == candidate["results_scientific_sha256"],
            "Owned scientific candidate output changed",
        )
        evaluations.append(science)
    q.require(
        all(
            e["metrics"]["background_total"] == 150471
            and e["metrics"]["signal_total"] == 100000
            for e in evaluations
        ),
        "Complete common populations",
    )
    historical = audit.request(
        "historical_aggregate_tables", 2, source=spec["historical_two_prong"]
    )
    with (root / spec["historical_two_prong"]["calibrated_csv"]).open() as stream:
        historical_cal = list(csv.DictReader(stream))
    audit.read(historical, 1)
    guard.check()
    with (root / spec["historical_two_prong"]["comparison_csv"]).open() as stream:
        historical_scientific = list(csv.DictReader(stream))
    audit.read(historical, 1)
    guard.check()
    scientific = []
    calibrated = []
    empirical = []
    comparison = []
    for candidate, e in zip(spec["candidates"], evaluations, strict=True):
        m = e["metrics"]
        name = candidate["name"]
        scientific.append(
            dict(
                candidate=name,
                roc_auc=m["roc_auc"],
                average_precision=m["average_precision"],
                background_total=m["background_total"],
                signal_total=m["signal_total"],
                signal_prevalence=m["signal_prevalence"],
                model_scientific_sha256=e["model_scientific_sha256"],
                calibration_scientific_sha256=e["calibration_scientific_sha256"],
                new_signal_scientific_sha256=e["new_signal_scientific_sha256"],
            )
        )
        old_quality = next(
            row for row in historical_scientific if row["candidate"] == name
        )
        for point in m["calibrated_thresholds"]:
            row = calibrated_row(name, point)
            calibrated.append(row)
            old = next(
                r
                for r in historical_cal
                if r["candidate"] == name
                and float(r["target_fpr"]) == point["target_fpr"]
            )
            q.require(
                float(old["threshold"]) == point["threshold"]
                and int(old["background_accepted"]) == point["background"]["accepted"]
                and int(old["background_total"]) == 150471,
                "Shared historical calibrated identity/counts",
            )
            old_tpr = float(old["signal_efficiency"])
            bg = point["background"]["efficiency"]
            comparison.append(
                dict(
                    candidate=name,
                    target_fpr=point["target_fpr"],
                    threshold=point["threshold"],
                    shared_background_accepted=point["background"]["accepted"],
                    shared_background_total=150471,
                    shared_background_fpr=bg,
                    two_prong_signal_accepted=int(old["signal_accepted"]),
                    two_prong_signal_total=int(old["signal_total"]),
                    two_prong_signal_efficiency=old_tpr,
                    three_prong_signal_accepted=point["signal"]["accepted"],
                    three_prong_signal_total=100000,
                    three_prong_signal_efficiency=point["signal"]["efficiency"],
                    two_prong_relative_acceptance=old_tpr / bg if bg else None,
                    three_prong_relative_acceptance=point["preregistered_arithmetic"][
                        "relative_acceptance"
                    ],
                    two_prong_selected_signal_fraction=int(old["signal_accepted"])
                    / (int(old["signal_accepted"]) + point["background"]["accepted"])
                    if int(old["signal_accepted"]) + point["background"]["accepted"]
                    else None,
                    three_prong_selected_signal_fraction=point[
                        "preregistered_arithmetic"
                    ]["selected_signal_fraction"],
                    two_prong_roc_auc=float(old_quality["roc_auc"]),
                    three_prong_roc_auc=m["roc_auc"],
                    two_prong_average_precision=float(old_quality["average_precision"]),
                    three_prong_average_precision=m["average_precision"],
                    scope="descriptive topology comparison;shared exposed background;no independent significance",
                )
            )
        for kind, key in [("fixed_fpr", "at_fixed_fpr"), ("fixed_tpr", "at_fixed_tpr")]:
            for point in m[key]:
                bg, sig = point["background"], point["signal"]
                empirical.append(
                    dict(
                        candidate=name,
                        point_kind=kind,
                        target_fpr=point.get("target_fpr"),
                        target_tpr=point.get("target_tpr"),
                        threshold=point["threshold"],
                        threshold_kind=point["threshold_kind"],
                        background_accepted=bg["accepted"],
                        background_total=bg["total"],
                        background_fpr=bg["efficiency"],
                        background_wilson_low=bg["wilson_95"][0],
                        background_wilson_high=bg["wilson_95"][1],
                        background_rejection=bg["rejection"],
                        signal_accepted=sig["accepted"],
                        signal_total=sig["total"],
                        signal_efficiency=sig["efficiency"],
                        signal_wilson_low=sig["wilson_95"][0],
                        signal_wilson_high=sig["wilson_95"][1],
                        scope="descriptive attainable ROC point;not adopted calibration threshold",
                    )
                )
    write_csv(directory / "scientific-comparison.csv", scientific)
    write_csv(directory / "calibrated-operating-points.csv", calibrated)
    write_csv(directory / "empirical-operating-points.csv", empirical)
    write_csv(directory / "two-vs-three-prong.csv", comparison)
    draw(base, evaluations, spec["candidates"], directory / "roc-pr.png", audit, guard)
    summary = dict(
        candidate_order=[c["name"] for c in spec["candidates"]],
        evaluations=evaluations,
        background_shared=True,
        capacity_controlled=False,
        preregistered_arithmetic=spec["descriptive_arithmetic"],
        tables_file_byte_sha256={
            f.name: p.file_hash(f)
            for f in directory.iterdir()
            if f.suffix in (".csv", ".png")
        },
        source_scope="frozen new signal+reused exposed background;no new original signal values",
    )
    p.write(directory / "comparison.json", summary, exclusive=True)
    guard.check()
    return summary


def draw(base, evaluations, candidates, path, audit, guard):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), layout="constrained")
    curves_access = audit.request("reporting_owned_curves", 2, source=str(base))
    colors = ["#28649b", "#c05d28"]
    for stage, candidate, e, color in zip(
        ("PCA", "AE"), candidates, evaluations, colors, strict=True
    ):
        guard.check()
        curve_path = base / stage / "curves.npz"
        q.require(
            p.file_hash(curve_path) == e["owned_curves_file_byte_sha256"],
            "Owned curve bytes changed",
        )
        with np.load(curve_path, allow_pickle=False) as curves:
            fpr, tpr, precision, recall = (
                curves[k] for k in ("fpr", "tpr", "precision", "recall")
            )
        guard.check()
        audit.read(curves_access, 1)
        q.require(
            all(np.isfinite(v).all() for v in (fpr, tpr, precision, recall)),
            "Finite owned curves",
        )
        axes[0].plot(
            fpr,
            tpr,
            color=color,
            label=f"{candidate['name']} · AUC {e['metrics']['roc_auc']:.4f}",
        )
        axes[1].plot(
            recall,
            precision,
            color=color,
            label=f"{candidate['name']} · AP {e['metrics']['average_precision']:.4f}",
        )
        points = e["metrics"]["calibrated_thresholds"]
        axes[0].scatter(
            [v["background"]["efficiency"] for v in points],
            [v["signal"]["efficiency"] for v in points],
            color=color,
            edgecolor="white",
            linewidth=0.6,
            s=30,
            zorder=4,
        )
        pr = [
            v
            for v in points
            if v["preregistered_arithmetic"]["selected_signal_fraction"] is not None
        ]
        axes[1].scatter(
            [v["signal"]["efficiency"] for v in pr],
            [v["preregistered_arithmetic"]["selected_signal_fraction"] for v in pr],
            color=color,
            edgecolor="white",
            linewidth=0.6,
            s=30,
            zorder=4,
        )
    axes[0].plot([0, 1], [0, 1], color="gray", linestyle=":", linewidth=1)
    axes[1].axhline(
        evaluations[0]["metrics"]["signal_prevalence"],
        color="gray",
        linestyle=":",
        label=f"Mixture prevalence {evaluations[0]['metrics']['signal_prevalence']:.4f}",
    )
    axes[0].set(
        xlabel="Shared background FPR (fraction)",
        ylabel="Three-prong signal efficiency (fraction)",
        title="Frozen native three-prong ROC",
    )
    axes[1].set(
        xlabel="Three-prong signal recall (fraction)",
        ylabel="Selected signal fraction / precision",
        title="Released-mixture precision–recall",
    )
    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.2)
        ax.legend(fontsize=7, loc="best")
    fig.suptitle(
        "Circles: all four original calibrated thresholds · shared exposed Task0026 background",
        fontsize=10,
    )
    guard.check()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    guard.check()
