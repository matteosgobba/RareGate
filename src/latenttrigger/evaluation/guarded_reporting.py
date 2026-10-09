"""Preregistered scientific table/ROC/PR outputs; scores and curves stay ignored."""

import csv

import numpy as np
from sklearn.metrics import precision_recall_curve, roc_curve

from latenttrigger.benchmarks import protocol as p


def reporting(directory, candidates, *, make_figures=True):
    if [c["name"] for c in candidates] != ["pca-v1", "compact-autoencoder-v2"]:
        raise ValueError("Only complete frozen native candidate pair in fixed order.")
    evaluations = []
    for stage, candidate in zip(("PCA", "AE"), candidates, strict=True):
        file = directory / stage / "evaluation.json"
        doc = p.read(file)
        if (
            p.digest(doc["scientific"]) != doc["scientific_sha256"]
            or doc["scientific"]["model_scientific_sha256"]
            != candidate["model_scientific_sha256"]
        ):
            raise ValueError("Incomplete/mutated scientific candidate output.")
        evaluations.append(doc["scientific"])
    if any(
        e["metrics"]["background_total"]
        != evaluations[0]["metrics"]["background_total"]
        or e["metrics"]["signal_total"] != evaluations[0]["metrics"]["signal_total"]
        for e in evaluations
    ):
        raise ValueError("Candidate populations differ; cannot consolidate.")
    summary = dict(
        protocol="latenttrigger-evaluation-v1",
        candidate_order=[c["name"] for c in candidates],
        evaluations=evaluations,
        capacities=dict(
            PCA_retained_components=6, AE_latent_dimensions=3, AE_parameters=155
        ),
        capacity_controlled_linearity_experiment=False,
        CPU_context="Task0022 accepted native CPU reference only; Task0025 speedups provisional/unaccepted",
        background_summaries=[
            p.read(directory / s / "background-summary.json") for s in ("PCA", "AE")
        ],
    )
    p.write(directory / "comparison.json", summary, exclusive=True)
    with (directory / "calibrated-operating-points.csv").open(
        "x", newline=""
    ) as stream:
        fields = [
            "candidate",
            "target_fpr",
            "threshold",
            "background_accepted",
            "background_total",
            "background_fpr",
            "background_wilson_low",
            "background_wilson_high",
            "background_rejection",
            "zero_acceptance_upper_95",
            "signal_accepted",
            "signal_total",
            "signal_efficiency",
            "signal_wilson_low",
            "signal_wilson_high",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for candidate, e in zip(candidates, evaluations, strict=True):
            for point in e["metrics"]["calibrated_thresholds"]:
                bg, sig = point["background"], point["signal"]
                writer.writerow(
                    dict(
                        candidate=candidate["name"],
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
                    )
                )
    if make_figures:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
        for stage, candidate, e in zip(
            ("PCA", "AE"), candidates, evaluations, strict=True
        ):
            bg = np.load(
                directory / stage / "test_background-scores.npy", allow_pickle=False
            )
            sig = np.load(
                directory / stage / "test_signal-scores.npy", allow_pickle=False
            )
            if (
                len(bg) != e["metrics"]["background_total"]
                or len(sig) != e["metrics"]["signal_total"]
                or not np.isfinite(bg).all()
                or not np.isfinite(sig).all()
            ):
                raise ValueError("Reporting score identity/count/nonfinite mismatch.")
            labels = np.r_[np.zeros(len(bg), np.uint8), np.ones(len(sig), np.uint8)]
            scores = np.r_[bg, sig]
            fpr, tpr, roc_thresholds = roc_curve(
                labels, scores, drop_intermediate=False
            )
            precision, recall, pr_thresholds = precision_recall_curve(labels, scores)
            np.savez(
                directory / (stage + "-curves.npz"),
                fpr=fpr,
                tpr=tpr,
                roc_thresholds=roc_thresholds,
                precision=precision,
                recall=recall,
                pr_thresholds=pr_thresholds,
            )
            axes[0].plot(fpr, tpr, label=candidate["name"])
            axes[1].plot(recall, precision, label=candidate["name"])
            points = e["metrics"]["calibrated_thresholds"]
            axes[0].scatter(
                [p["background"]["efficiency"] for p in points],
                [p["signal"]["efficiency"] for p in points],
                marker="o",
                label=candidate["name"] + " frozen thresholds",
            )
        prevalence = evaluations[0]["metrics"]["signal_prevalence"]
        axes[0].set(
            xlabel="Background FPR",
            ylabel="Signal efficiency",
            title="Empirical ROC; circles: frozen calibration",
        )
        axes[1].axhline(prevalence, color="gray", linestyle=":")
        axes[1].set(
            xlabel="Signal recall",
            ylabel="Precision",
            title=f"Released sample PR; signal prevalence {prevalence:.4f}",
        )
        for ax in axes:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.legend(fontsize=7)
            ax.grid(alpha=0.2)
        fig.savefig(directory / "roc-pr.png", dpi=180)
        plt.close(fig)
    return summary
