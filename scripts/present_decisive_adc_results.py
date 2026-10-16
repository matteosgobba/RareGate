"""Presentation only: reproduce Task0062 figures from curated scalar tables.

Added after unblinding to fix clipped labels. No event/model/score-vector access,
statistical estimation, gate calculation, threshold choice or experimental repeat.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("compactAE", "referenceAE", "PCA3", "regularizedMahalanobis")
NAMES = ("compact AE", "reference AE", "PCA3", "Mahalanobis")
COLORS = ("#2878B5", "#DD6B20", "#3A923A", "#8856A7")
SIGNALS = ("A_to_4l", "LQ_to_btau")


def draw(summary, points, costs, destination):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    destination.mkdir(parents=True, exist_ok=True)
    primary = [
        r
        for r in summary["inference_family"]
        if r["kind"] == "efficiency" and r["alpha"] == 0.01
    ]

    def endpoint(arm, signal):
        return next(r for r in primary if r["arm"] == arm and r["signal"] == signal)

    def means(arm):
        return [
            np.mean(
                [
                    float(r["mean_ns"])
                    for r in costs
                    if r["scope"] == "measured_stream_cell"
                    and int(r["batch"]) == 32
                    and r["boundary"] == "joint"
                    and r["arm"] == arm
                    and int(r["repetition"]) == rep
                ]
            )
            / 1000
            for rep in range(8)
        ]

    fig, axes = plt.subplots(
        1, 2, figsize=(10, 4.6), sharey=True, constrained_layout=True
    )
    for ax, signal in zip(axes, SIGNALS, strict=True):
        for i, arm in enumerate(ARMS):
            r = endpoint(arm, signal)
            ax.vlines(i, r["lower"], r["upper"], color=COLORS[i], linewidth=3)
            ax.scatter(i, r["point"], color=COLORS[i], s=40, zorder=3)
            seeds = [
                float(s["efficiency"])
                for s in points
                if s["scope"] == "stream"
                and s["signal"] == signal
                and s["arm"] == arm
                and float(s["alpha"]) == 0.01
            ]
            positions = (
                [i] if len(seeds) == 1 else np.linspace(i - 0.12, i + 0.12, len(seeds))
            )
            ax.scatter(positions, seeds, marker="x", color="black", s=24, zorder=4)
        ax.axhline(0.15, color="gray", linestyle="--", linewidth=1)
        ax.set_xticks(range(4), NAMES, rotation=20, ha="right")
        ax.set_ylim(0, 1)
        ax.set_title(signal.replace("_", " "))
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Signal efficiency (primary target FPR 0.01)")
    fig.suptitle(
        "Intervals: simultaneous population-quantile bounds\nDots/crosses: empirical-cut arm mean / individual seeds",
        fontsize=11,
    )
    fig.savefig(destination / "task0062-adc-primary-efficiency.png", dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(
        1, 2, figsize=(10, 4.6), sharey=True, constrained_layout=True
    )
    xmax = max(float(np.median(means(a))) for a in ARMS) * 1.4
    for ax, signal in zip(axes, SIGNALS, strict=True):
        for i, arm in enumerate(ARMS):
            r = endpoint(arm, signal)
            x = float(np.median(means(arm)))
            ax.vlines(x, r["lower"], r["upper"], color=COLORS[i], linewidth=3)
            ax.scatter(x, r["point"], color=COLORS[i], s=40, label=NAMES[i])
        ax.legend(loc="upper left", fontsize=9)
        ax.set_title(signal.replace("_", " "))
        ax.set_xlabel("Joint B32 cost (µs/call)\nmedian of 8 arm block means")
        ax.set_xlim(0, xmax)
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Signal efficiency; population-quantile bounds")
    fig.suptitle(
        "Direct measured quality/cost tradeoffs at fixed empirical cuts", fontsize=11
    )
    fig.savefig(destination / "task0062-adc-quality-cost.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.6), constrained_layout=True)
    for name, rule in summary["cost_rules"].items():
        ax.plot(
            range(1, 9), rule["ratios"], marker="o", label=name.replace("_over_", " / ")
        )
    ax.axhline(0.75, color="black", linestyle="--", label="median requirement ≤0.75")
    ax.axhline(0.8, color="gray", linestyle=":", label="≥7/8 blocks must be ≤0.80")
    ax.set_ylim(bottom=0)
    ax.set_xticks(range(1, 9))
    ax.set_xlabel("Paired repetition block (all 8)")
    ax.set_ylabel("Joint B32 ratio of mean costs")
    ax.set_title("Finite workload cost gates; seeds averaged before ratios")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.savefig(destination / "task0062-adc-paired-cost-ratios.png", dpi=170)
    plt.close(fig)


def main():
    from evaluate_decisive_adc_experiment import OWNED, configure

    configure(OWNED)
    tables = ROOT / "results/tables/final"
    summary = json.loads((tables / "task0062-adc-evaluation-summary.json").read_text())
    with (tables / "task0062-adc-signal-operating-points.csv").open() as f:
        points = list(csv.DictReader(f))
    with (tables / "task0062-adc-cpu-costs.csv").open() as f:
        costs = list(csv.DictReader(f))
    draw(summary, points, costs, ROOT / "results/figures/final")


if __name__ == "__main__":
    main()
