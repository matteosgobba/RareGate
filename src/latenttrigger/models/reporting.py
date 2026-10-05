"""Small background-only tables and optional scientific figures."""

import csv
from pathlib import Path

import numpy as np


def write_tables(path: Path, scientific: dict) -> None:
    for name, rows in {
        "background-summary.csv": [
            {"split": split, **stats}
            for split, stats in scientific["background_summary"].items()
        ],
        "thresholds.csv": [
            {
                "target_fpr": p["target_fpr"],
                "threshold": p["threshold"],
                "calibration_accepted": p["calibration"]["accepted"],
                "calibration_total": p["calibration"]["total"],
                "calibration_fpr": p["calibration"]["efficiency"],
                "selection_accepted": p["selection"]["accepted"],
                "selection_total": p["selection"]["total"],
                "selection_fpr": p["selection"]["efficiency"],
                "absolute_deviation": p["absolute_deviation"],
                "relative_deviation": p["relative_deviation"],
                "selection_wilson95_lower": p["selection"]["wilson_95"][0],
                "selection_wilson95_upper": p["selection"]["wilson_95"][1],
            }
            for p in scientific["thresholds"]
        ],
    }.items():
        with (path / name).open("w", newline="") as stream:
            writer = csv.DictWriter(
                stream, fieldnames=list(rows[0]), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)


def plot_background(path: Path, model, scores: dict, thresholds: list[dict]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 10})
    components = np.arange(1, 9)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
    axes[0].bar(components, model.explained_variance_ratio)
    axes[0].set(
        xlabel="Principal component",
        ylabel="Explained variance fraction",
        xticks=components,
    )
    axes[1].plot(components, np.cumsum(model.explained_variance_ratio), "o-")
    axes[1].axhline(
        model.target, color="black", linestyle="--", label=f"Target {model.target:.0%}"
    )
    axes[1].axvline(
        model.k, color="tab:red", linestyle=":", label=f"Selected k={model.k}"
    )
    axes[1].set(
        xlabel="Components retained",
        ylabel="Cumulative explained variance",
        xticks=components,
        ylim=(0, 1.03),
    )
    axes[1].legend()
    fig.suptitle(
        f"LHCO R&D v5 PCA — training background only (N={model.training_count:,})"
    )
    fig.savefig(path / "pca-spectrum.png", dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    maximum = max(float(np.log1p(s).max()) for s in scores.values())
    bins = np.linspace(0, maximum, 100)
    labels = ("Training", "Selection validation", "Calibration validation")
    for label, values in zip(labels, scores.values(), strict=True):
        axes[0].hist(
            np.log1p(values),
            bins=bins,
            density=True,
            histtype="step",
            label=f"{label} (N={len(values):,})",
        )
        ordered = np.sort(values)
        ranks = np.unique(np.round(np.geomspace(1, len(values), 1000)).astype(int))
        axes[1].plot(
            np.log1p(ordered[len(values) - ranks]), ranks / len(values), label=label
        )
    axes[0].set(
        xlabel="ln(1 + squared reconstruction score)",
        ylabel="Density in transformed score",
        yscale="log",
    )
    axes[1].set(
        xlabel="ln(1 + squared reconstruction score)",
        ylabel="Empirical fraction at/above plotted score",
        yscale="log",
    )
    for point in thresholds:
        axes[1].axvline(
            np.log1p(point["threshold"]), linestyle=":", color="grey", linewidth=0.8
        )
    axes[0].legend(fontsize=8)
    axes[1].legend(fontsize=8)
    fig.suptitle("LHCO R&D v5 — PCA background-only diagnostics; no test populations")
    fig.savefig(path / "background-scores.png", dpi=170)
    plt.close(fig)
