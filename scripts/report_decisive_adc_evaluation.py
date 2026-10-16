"""Reproduce curated Task0062 tables/figures from committed private evidence only.

No models, event features or inference calls. No real evidence is read on import.
"""

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def csv_rows(path, rows):
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def read(path):
    return json.loads(path.read_text())


def export(root, tables, figures):
    import matplotlib
    import numpy as np

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from raregate.research.decisive_adc.data import digest

    analysis = read(root / "private/analysis.json")
    cpu = read(root / "private/cpu.json")
    robust = read(root / "private/robustness.json")
    bias = read(root / "private/bias.json")
    for folder in (tables, figures):
        folder.mkdir(parents=True, exist_ok=True)
    prefix = "task0062-adc-"
    csv_rows(tables / (prefix + "background-acceptance.csv"), analysis["background"])
    csv_rows(tables / (prefix + "signal-operating-points.csv"), analysis["signal"])
    csv_rows(tables / (prefix + "paired-inference.csv"), analysis["inference"])
    costs = [dict(scope="measured_stream_cell", **r) for r in cpu["rows"]]
    costs += [dict(scope="skipped_secondary_shape", **r) for r in cpu["skipped"]]
    costs += [
        dict(
            scope="paired_primary_arm_ratio",
            comparison=name,
            repetition=rep,
            ratio=ratio,
        )
        for name, rule in analysis["cost_rules"].items()
        for rep, ratio in enumerate(rule["ratios"])
    ]
    csv_rows(tables / (prefix + "cpu-costs.csv"), costs)
    csv_rows(tables / (prefix + "robustness.csv"), robust["rows"] + bias)
    arms = ["compactAE", "referenceAE", "PCA3", "regularizedMahalanobis"]
    names = ["compact AE", "reference AE", "PCA3", "Mahalanobis"]
    colors = ["#2878B5", "#DD6B20", "#3A923A", "#8856A7"]
    signals = ["A_to_4l", "LQ_to_btau"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True, constrained_layout=True)
    for ax, signal in zip(axes, signals, strict=True):
        for i, arm in enumerate(arms):
            r = next(
                r
                for r in analysis["inference"]
                if r["kind"] == "efficiency"
                and r["signal"] == signal
                and r["arm"] == arm
                and r["alpha"] == 0.01
            )
            ax.vlines(i, r["lower"], r["upper"], color=colors[i], linewidth=3)
            ax.scatter([i], [r["point"]], color=colors[i], s=35, zorder=3)
            seeds = [
                s["efficiency"]
                for s in analysis["signal"]
                if s["scope"] == "stream"
                and s["signal"] == signal
                and s["arm"] == arm
                and s["alpha"] == 0.01
            ]
            ax.scatter(
                np.linspace(i - 0.12, i + 0.12, len(seeds)),
                seeds,
                marker="x",
                color="black",
                s=28,
                zorder=4,
            )
        ax.axhline(0.15, color="gray", linestyle="--", linewidth=1)
        ax.set_xticks(range(4), names, rotation=20, ha="right")
        ax.set_ylim(0, 1)
        ax.set_title(signal.replace("_", " "))
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Signal efficiency (primary target FPR 0.01)")
    fig.suptitle(
        "Intervals: population-quantile simultaneous bounds\nDots/crosses: empirical-cut arm mean / individual seeds",
        fontsize=11,
    )
    fig.savefig(figures / (prefix + "primary-efficiency.png"), dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True, constrained_layout=True)
    for ax, signal in zip(axes, signals, strict=True):
        for i, arm in enumerate(arms):
            means = [
                np.mean(
                    [
                        r["mean_ns"]
                        for r in cpu["rows"]
                        if r["arm"] == arm
                        and r["repetition"] == rep
                        and r["batch"] == 32
                        and r["boundary"] == "joint"
                    ]
                )
                / 1000
                for rep in range(8)
            ]
            r = next(
                r
                for r in analysis["inference"]
                if r["kind"] == "efficiency"
                and r["signal"] == signal
                and r["arm"] == arm
                and r["alpha"] == 0.01
            )
            x = float(np.median(means))
            ax.vlines(x, r["lower"], r["upper"], color=colors[i], linewidth=2)
            ax.scatter(x, r["point"], label=names[i], color=colors[i])
            ax.annotate(
                names[i],
                (x, r["point"]),
                xytext=(4, 4 + i * 3),
                textcoords="offset points",
                fontsize=8,
            )
        ax.set_title(signal.replace("_", " "))
        ax.set_xlabel("Joint B32 cost: median of 8 arm block means (µs/call)")
        ax.set_ylim(0, 1)
        ax.set_xlim(left=0)
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Signal efficiency; population-quantile bounds")
    fig.suptitle(
        "Direct measured cost versus fixed-cut efficiency; no deployment rate claim",
        fontsize=11,
    )
    fig.savefig(figures / (prefix + "quality-cost.png"), dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    for name, rule in analysis["cost_rules"].items():
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
    fig.savefig(figures / (prefix + "paired-cost-ratios.png"), dpi=170)
    plt.close(fig)
    phases = {
        p: read(root / "ledger" / f"{p}-result.json")
        for p in ("preflight-v2", "development-v2", "final", "postflight")
    }
    outers = {p: read(root / "diagnostics" / p / "outer-result.json") for p in phases}
    if not all(r["valid"] for r in phases.values()) or not all(
        r.get("returncode", 0) == 0 and r.get("stop_reason") is None
        for r in outers.values()
    ):
        raise ValueError("incomplete/invalid phase cannot produce completed summary")
    binding = read(root / "private/extension-binding-v2.json")
    summary = dict(
        schema_version=2,
        task="Task0062",
        status="generated_evaluation_result"
        if binding.get("generated")
        else "completed_preregistered_adc_evaluation",
        scope="generated-evaluation-only"
        if binding.get("generated")
        else "Task0062-explicit-human-authorized",
        valid=True,
        completed=True,
        final_evaluation_performed=True,
        Task0063_started=False,
        operational_readiness=False,
        scientific_verdict=analysis["decision"],
        rate_comparability=analysis["rate_comparability"],
        cost_rules=analysis["cost_rules"],
        inference_family=analysis["inference"],
        ranking_secondary=analysis["ranking"],
        accepted_freeze_sha256="e425d1bc50c644caf7c3fad1f2317472e33eca68686022d4eac52bf04d804ce6",
        extension_binding=binding,
        score_pass=read(root / "private/score-pass.json"),
        parity=read(root / "private/parity.json"),
        robustness=robust,
        phases=phases,
        prior_attempts={
            p.parent.name: read(p)
            for p in sorted((root / "diagnostics").glob("*/outer-result.json"))
            if p.parent.name in ("preflight", "development")
        },
        resources=outers,
        qualification_scope="B32 all eight streams required; secondary shapes explicitly listed in parity/skips",
        tooling=dict(
            resource_observation="sampled own PID plus lifetime worker RSS and logical retained storage; no OS all-write proof",
            caches="disabled/contained",
            new_fit_attempts=0,
            new_acquisition=0,
            new_calibration=0,
        ),
        caveats=[
            "conditional approximately independent unique event groups; generator independence not proved",
            "three finite seeds share N=40000 events, not 120000",
            "population-quantile bounds differ from empirical-cut descriptive estimates",
            "all six neural models reached 80 epoch cap; not convergence or optimality",
            "13,451,915 actual background rows; nominal SM mixture not verified",
            "lepton-prefiltered simulation and capped provided objects; not detector readiness",
        ],
        output_identities={
            str(p.relative_to(ROOT)): dict(bytes=p.stat().st_size, sha256=digest(p))
            for folder in (tables, figures)
            for p in sorted(folder.glob(prefix + "*"))
            if p.is_file() and p.suffix in (".csv", ".png")
        },
    )
    (tables / (prefix + "evaluation-summary.json")).write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    return summary


def main():
    from evaluate_decisive_adc_experiment import OWNED, configure

    configure(OWNED)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    summary = export(
        OWNED, ROOT / "results/tables/final", ROOT / "results/figures/final"
    )
    print(json.dumps(summary["scientific_verdict"], indent=2))


if __name__ == "__main__":
    main()
