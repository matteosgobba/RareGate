"""Figures consume owned engineering aggregates, never features/models/scores."""

import csv

from latenttrigger.benchmarks import prepared_service_protocol as p


def validate(value):
    cells = value["cells"]
    synthetic = value["synthetic_only"]
    expected = 68 if synthetic else 204
    required = {
        (c, r, b, m, s)
        for c in ("pca-v1", "compact-autoencoder-v2")
        for r in ((1,) if synthetic else (1, 2, 3))
        for b, m in p.CASES
        for s in ("natural", "padded")
    }
    p.require(
        len(cells) == expected
        and {
            (r["candidate"], r["repetition"], r["B"], r["m"], r["strategy"])
            for r in cells
        }
        == required,
        "Complete unique timing cells",
    )
    p.require(
        all(
            r["count"] == (2 if synthetic else 50)
            and r["min_ns"] >= 0
            and r["min_ns"] <= r["p50_ns"] <= r["p95_ns"] <= r["p99_ns"] <= r["max_ns"]
            and r["executed_shape_rows"]
            == (r["m"] if r["strategy"] == "natural" else r["B"])
            for r in cells
        ),
        "Cell statistics/shape",
    )
    for g in value["gates"]:
        p.require(
            g["before"] == g["after"]
            and g["before"]["status"] == "passed"
            and g["before"]["mismatches_per_threshold"] == [0] * 4,
            "Pre/post numerical gates",
        )
    p.require(
        len(value["chronology"]) == expected * (2 if synthetic else 50)
        and len(value["paired"]) == expected // 2,
        "Complete owned chronology/paired aggregates",
    )
    return cells


def render(directory, poll=lambda: None):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    value = p.read(directory / "aggregate.json")
    cells = validate(value)
    candidates = ("pca-v1", "compact-autoencoder-v2")
    names = []
    fig, axes = plt.subplots(2, 1, figsize=(13, 9), layout="constrained")
    labels = [f"{b}/{m}" for b, m in p.CASES]
    for ax, candidate in zip(axes, candidates, strict=True):
        for r in cells:
            if r["candidate"] != candidate:
                continue
            x = p.CASES.index((r["B"], r["m"])) + (
                -0.13 if r["strategy"] == "natural" else 0.13
            )
            ax.scatter(
                x,
                r["mean_ns"] / 1000,
                c="#1877ae" if r["strategy"] == "natural" else "#e27728",
                marker=("o", "s", "^")[r["repetition"] - 1],
                s=24,
            )
        ax.set(
            title=candidate,
            ylabel="Whole-batch mean service (µs; log)",
            yscale="log",
            xticks=range(17),
            xticklabels=labels,
            xlabel="B / actual m — fixed cases",
        )
        ax.grid(alpha=0.2)
        ax.tick_params(axis="x", labelrotation=35, labelsize=9)
    axes[0].legend(
        handles=[
            Line2D([], [], color="#1877ae", marker="o", linestyle="", label="natural"),
            Line2D([], [], color="#e27728", marker="o", linestyle="", label="padded"),
            *[
                Line2D(
                    [], [], color="gray", marker=m, linestyle="", label=f"repetition{i}"
                )
                for i, m in enumerate(("o", "s", "^"), 1)
            ],
        ],
        loc="upper left",
        ncols=5,
        fontsize=8,
    )
    fig.suptitle(
        "Prepared development rows: packing + frozen CPU adapter + real-row retention\nAll repetitions shown; logarithmic cost axis; no clipping"
    )
    fig.savefig(directory / "partial-cost.png", dpi=155)
    plt.close(fig)
    names.append("partial-cost.png")
    poll()
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), layout="constrained")
    for ax, candidate in zip(axes, candidates, strict=True):
        for r in value["paired"]:
            if r["candidate"] != candidate:
                continue
            x = p.CASES.index((r["B"], r["m"])) + (r["repetition"] - 2) * 0.13
            ax.plot(
                [x, x],
                [r["min_ns"] / 1000, r["max_ns"] / 1000],
                color="#8db0c4",
                alpha=0.6,
            )
            ax.scatter(
                x,
                r["mean_ns"] / 1000,
                c="#1877ae",
                marker=("o", "s", "^")[r["repetition"] - 1],
                s=25,
            )
        ax.axhline(0, c="black", lw=0.7)
        ax.set(
            title=candidate,
            ylabel="Natural − padded (µs; symlog)",
            yscale="symlog",
            xticks=range(17),
            xticklabels=labels,
            xlabel="B / actual m; dots: paired mean, lines: all-call min–max",
        )
        ax.grid(alpha=0.2)
        ax.tick_params(axis="x", labelrotation=35, labelsize=9)
    fig.suptitle(
        "Paired costs: negative means lower natural cost\nAll observed pairs retained; symmetric logarithmic axis, no clipping"
    )
    fig.savefig(directory / "paired-difference.png", dpi=155)
    plt.close(fig)
    names.append("paired-difference.png")
    poll()
    repetitions = sorted({r["repetition"] for r in value["chronology"]})
    fig, axes = plt.subplots(
        len(repetitions),
        1,
        figsize=(13, 3 * len(repetitions)),
        layout="constrained",
        squeeze=False,
    )
    for rep, ax in zip(repetitions, axes[:, 0], strict=True):
        for candidate in candidates:
            for strategy in ("natural", "padded"):
                rows = [
                    r
                    for r in value["chronology"]
                    if r["repetition"] == rep
                    and r["candidate"] == candidate
                    and r["strategy"] == strategy
                ]
                ax.scatter(
                    [r["sequence"] for r in rows],
                    [r["duration_ns"] / 1000 for r in rows],
                    s=3,
                    alpha=0.65,
                    label=candidate + " / " + strategy,
                )
        ax.set(
            title=f"Repetition{rep}: fixed sequential order, changing B/m",
            ylabel="Service (µs; log)",
            yscale="log",
            xlabel="Worker invocation sequence (warm-ups create gaps)",
        )
        ax.grid(alpha=0.2)
    axes[0, 0].legend(loc="upper left", ncols=2, fontsize=8, markerscale=3)
    fig.suptitle(
        "Chronological timed observations — costs mix prespecified shapes\nSerial host observations; no frequency/distribution fit or production-p99 claim"
    )
    fig.savefig(directory / "chronology.png", dpi=155)
    plt.close(fig)
    names.append("chronology.png")
    p.durable_json(
        directory / "reporting.json",
        dict(
            status="aggregate_figures_complete",
            cells=len(cells),
            observations=len(value["chronology"]),
            input_sha256=p.file_hash(directory / "aggregate.json"),
            outputs={n: p.file_hash(directory / n) for n in names},
            display="log costs / symlog differences; all extrema retained, no clipping",
        ),
        exclusive=True,
    )
    return names + ["reporting.json"]


def write_cells(path, cells):
    with path.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(cells[0]))
        writer.writeheader()
        writer.writerows(cells)
