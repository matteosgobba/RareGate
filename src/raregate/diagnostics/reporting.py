"""Plot owned aggregate tables only. No feature/score reader imports."""

import csv

from raregate.diagnostics import protocol as p

FIGURES = (
    "feature-median-iqr.png",
    "score-quantiles.png",
    "feature-score-associations.png",
)
TABLES = (
    "feature-marginals.csv",
    "score-marginals.csv",
    "feature-score-associations.csv",
    "tail-counts.csv",
    "tail-feature-profiles.csv",
)


def read_aggregates(directory, identities):
    p.require(set(identities) == set(TABLES), "Only five owned aggregate tables")
    tables = {}
    for name, sha in identities.items():
        path = p.fixed(directory, name)
        p.require(
            path.stat().st_size <= 2 * 2**20 and p.file_hash(path) == sha,
            "Altered owned aggregate",
        )
        with path.open() as stream:
            tables[name] = list(csv.DictReader(stream))
    p.require(
        [len(tables[n]) for n in TABLES] == [24, 6, 48, 24, 192], "Aggregate coverage"
    )
    return tables


def render(directory, output, identities, check=lambda: None):
    tables = read_aggregates(directory, identities)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    plt.rcParams.update(
        {"font.size": 11, "axes.titlesize": 11, "figure.facecolor": "white"}
    )
    names = {
        "background": "Background",
        "two_prong": "Two prong",
        "three_prong": "Three prong",
    }
    labels = {
        "multiplicity": "Multiplicity",
        "scalar_pt": "Scalar pT",
        "max_pt": "Maximum pT",
        "pt_balance": "pT balance",
        "weighted_eta_mean": "Weighted eta mean",
        "weighted_eta_std": "Weighted eta spread",
        "pt_concentration": "pT concentration",
        "massless_event_mass": "Massless event mass",
    }
    colors = {"background": "#4c667c", "two_prong": "#b45c27", "three_prong": "#218271"}
    counts = {r["population"]: int(r["count"]) for r in tables[TABLES[0]]}
    fig, axes = plt.subplots(2, 4, figsize=(15, 7.5))
    for i, (feature, ax) in enumerate(zip(p.FEATURES, axes.flat, strict=True)):
        check()
        for j, pop in enumerate(p.POPULATIONS):
            r = next(
                r
                for r in tables[TABLES[0]]
                if r["feature"] == feature and r["population"] == pop
            )
            low, mid, high = [float(r[key]) for key in ("q0.25", "q0.5", "q0.75")]
            ax.plot([low, high], [j, j], color=colors[pop], lw=5, solid_capstyle="butt")
            ax.plot(mid, j, "o", color=colors[pop], mec="white", ms=8)
        ax.set_yticks(range(3), [names[k] for k in p.POPULATIONS])
        ax.invert_yaxis()
        ax.set_title(
            labels[feature] + (" (log1p → z)" if i in (0, 1, 2, 7) else " (z)")
        )
        ax.set_xlabel("Frozen standardized input")
        ax.axvline(0, lw=0.8, color="#bbbbbb", zorder=0)
        ax.grid(axis="x", alpha=0.18)
    fig.suptitle(
        "Exposed populations: feature medians and interquartile ranges", fontsize=17
    )
    fig.text(
        0.5,
        0.025,
        "Background N=150471 • Two prong N=100000 • Three prong N=100000\nDots: medians; bars: p25–p75. These summaries do not display full distributions. No clipping.",
        ha="center",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 0.94))
    fig.savefig(output / FIGURES[0], dpi=160)
    plt.close(fig)
    check()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.3))
    probs = p.QUANTILES
    for candidate, ax in zip(p.CANDIDATES, axes, strict=True):
        for pop in p.POPULATIONS:
            r = next(
                r
                for r in tables[TABLES[1]]
                if r["candidate"] == candidate and r["population"] == pop
            )
            values = [float(r[f"q{q:g}"]) for q in probs]
            p.require(
                all(v > 0 for v in values),
                "Positive plotted quantiles required for log axis",
            )
            ax.plot(
                np.array(probs) * 100,
                values,
                "o-",
                color=colors[pop],
                label=f"{names[pop]} (N={counts[pop]})",
                lw=1.8,
                ms=4,
            )
        points = [
            r
            for r in tables[TABLES[3]]
            if r["candidate"] == candidate and r["population"] == "background"
        ]
        for row in points:
            value = float(row["threshold"])
            ax.axhline(value, color="#666666", linestyle="--", lw=0.8)
            ax.text(
                99.9,
                value,
                f"  α={float(row['target_fpr']):g}",
                va="center",
                fontsize=9,
            )
        ax.set_yscale("log")
        ax.set_xlim(0, 112)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xlabel("Quantile probability (%)")
        ax.set_ylabel("Accepted SSE score (log scale)")
        ax.set_title("PCA-v1" if candidate == "PCA" else "Compact AE v2")
        ax.grid(alpha=0.2)
        ax.legend(loc="lower right", fontsize=9)
    fig.suptitle(
        "Within-candidate score quantiles and original thresholds", fontsize=17
    )
    fig.text(
        0.5,
        0.02,
        "11 fixed quantiles per population; connecting lines are visual guides. Dashed lines: original calibrated thresholds.\nSeparate candidate panels: absolute score magnitudes do not rank discrimination. No score clipping.",
        ha="center",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 0.94))
    fig.savefig(output / FIGURES[1], dpi=160)
    plt.close(fig)
    check()
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for candidate, ax in zip(p.CANDIDATES, axes, strict=True):
        values = np.array(
            [
                [
                    float(
                        next(
                            r
                            for r in tables[TABLES[2]]
                            if r["candidate"] == candidate
                            and r["population"] == pop
                            and r["feature"] == feature
                        )["spearman_rho"]
                        or "nan"
                    )
                    for feature in p.FEATURES
                ]
                for pop in p.POPULATIONS
            ]
        )
        im = ax.imshow(values, vmin=-1, vmax=1, cmap="RdBu_r", aspect="auto")
        for j in range(3):
            for i in range(8):
                ax.text(
                    i,
                    j,
                    "undefined" if np.isnan(values[j, i]) else f"{values[j, i]:.2f}",
                    ha="center",
                    va="center",
                    color="white" if abs(values[j, i]) > 0.55 else "#202020",
                    fontsize=10,
                )
        ax.set_xticks(
            range(8), [labels[f] for f in p.FEATURES], rotation=42, ha="right"
        )
        ax.set_yticks(
            range(3), [f"{names[pop]}\nN={counts[pop]}" for pop in p.POPULATIONS]
        )
        ax.set_title("PCA-v1" if candidate == "PCA" else "Compact AE v2")
    fig.colorbar(
        im,
        ax=list(axes),
        label="Spearman coefficient (average ranks)",
        shrink=0.75,
        pad=0.02,
    )
    fig.suptitle("Feature–score monotonic associations in exposed samples", fontsize=17)
    fig.subplots_adjust(left=0.09, right=0.85, bottom=0.32, top=0.88, wspace=0.4)
    fig.text(
        0.5,
        0.02,
        "48 fixed coefficients. Associations describe the existing scores; they are neither feature importance nor residual attribution.\nNo significance tests or causal claims. Color range covers −1 to +1 without clipping.",
        ha="center",
        fontsize=11,
    )
    fig.savefig(output / FIGURES[2], dpi=160)
    plt.close(fig)
    for name in FIGURES:
        p.require((output / name).stat().st_size <= 8 * 2**20, "Bounded figure")
    p.durable_json(
        output / "reporting-summary.json",
        dict(
            input_scope="owned five aggregate CSVs only",
            population_or_score_array_reloads=0,
            figures=list(FIGURES),
            axes="frozen standardized inputs; original log1p channels identified; SSE log score axes within candidate; heatmap [-1,1]; no clipping",
            exploratory=True,
        ),
        exclusive=True,
    )
