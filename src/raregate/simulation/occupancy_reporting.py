"""Aggregate-only plotting; all seeds/repetitions, signed null/adverse effects."""

from raregate.simulation import occupancy_protocol as p
from raregate.simulation.occupancy_sweep import decode_rows


def render(directory, poll=lambda: None):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = decode_rows(directory / "scenarios.csv")
    contrasts = decode_rows(directory / "contrasts.csv")
    names = []
    layout = []
    labels = (
        "next_natural_minus_control",
        "previous_natural_minus_control",
        "mapping_interaction",
    )
    colors = {1: "#00749b", 2: "#b45f06", 3: "#963b7b"}
    markers = {41: "o", 42: "^", 43: "s"}
    for kind in ("outcomes", "latency", "sensitivity"):
        poll()
        fig, axes = plt.subplots(2, 3, figsize=(17, 9))
        for ci, candidate in enumerate(p.CANDIDATES):
            for col, label in enumerate(labels):
                ax = axes[ci, col]
                group = [
                    r
                    for r in contrasts
                    if r["candidate"] == candidate and r["contrast"] == label
                ]
                if kind == "sensitivity":
                    group = [
                        r
                        for r in rows
                        if r["candidate"] == candidate
                        and (r["mapping"], r["billing"])
                        == (
                            ("next_anchor", "natural_anchor"),
                            ("previous_anchor", "natural_anchor"),
                            ("next_anchor", "full_control"),
                        )[col]
                    ]
                for rep in (1, 2, 3):
                    for seed in (41, 42, 43):
                        g = [
                            r
                            for r in group
                            if r["repetition"] == rep and r["seed"] == seed
                        ]
                        if kind == "outcomes":
                            x = [100 * r["overflow_fraction_difference"] for r in g]
                            y = [
                                100
                                * r["overflow_or_late_fraction_generated_difference"]
                                for r in g
                            ]
                        elif kind == "latency":
                            x = [r["latency_ns_mean_difference"] / 1e6 for r in g]
                            y = [r["latency_ns_p99_difference"] / 1e6 for r in g]
                        else:
                            x = [100 * r["mapped_events_fraction"] for r in g]
                            y = [100 * r["mapped_busy_ns_fraction"] for r in g]
                        ax.scatter(
                            x,
                            y,
                            s=13,
                            alpha=0.6,
                            color=colors[rep],
                            marker=markers[seed],
                            label=f"rep{rep}, seed{seed}",
                        )
                ax.set_title(
                    f"{candidate}\n"
                    + (
                        label.replace("_", " ")
                        if kind != "sensitivity"
                        else f"{group[0]['mapping']} / {group[0]['billing']}"
                    ),
                    fontsize=10,
                )
                if kind == "outcomes":
                    ax.set(
                        xlabel="Δ overflow / generated (percentage points)",
                        ylabel="Δ (overflow + late) / generated (pp)",
                    )
                elif kind == "latency":
                    ax.set(
                        xlabel="Δ survivor mean latency (ms)",
                        ylabel="Δ survivor p99 latency (ms)",
                    )
                else:
                    ax.set(
                        xlabel="Mapped events / completed survivors (%)",
                        ylabel="Mapped busy time / all assigned busy (%)",
                        xlim=(-2, 102),
                        ylim=(-2, 102),
                    )
                if kind != "sensitivity":
                    ax.axhline(0, c="black", lw=0.7)
                    ax.axvline(0, c="black", lw=0.7)
                    ax.set_xscale("symlog", linthresh=0.01)
                    ax.set_yscale("symlog", linthresh=0.01)
                ax.grid(alpha=0.2)
        fig.subplots_adjust(
            left=0.07, right=0.98, bottom=0.10, top=0.83, hspace=0.50, wspace=0.42
        )
        handles, legend_labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, legend_labels, loc="lower center", ncol=9, fontsize=8)
        fig.suptitle(
            {
                "outcomes": "Deterministic paired-cost contrasts; all arrival modes/rates/policies/seeds/source repetitions\n100 ms strict toy deadline; generated denominator5000; signed axes symlog threshold0.01pp",
                "latency": "Completed-survivor latency contrasts; all756contexts per contrast\nSurvivor populations can differ; signed axes symlog threshold0.01ms; no averaged quantiles",
                "sensitivity": "Dependence on unmeasured occupancy assignments (k ≠ m)\nAll seeds/repetitions; descriptive event/busy fractions, no empirical bound or policy recommendation",
            }[kind],
            fontsize=12,
        )
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        p.require(
            all(
                ax.get_tightbbox(renderer).y0 > fig.bbox.y0
                and ax.get_tightbbox(renderer).x0 > fig.bbox.x0
                for ax in axes.flat
            ),
            "Figure label layout within canvas",
        )
        name = kind + ".png"
        fig.savefig(directory / name, dpi=150, bbox_inches="tight", pad_inches=0.15)
        plt.close(fig)
        names.append(name)
        layout.append(
            dict(figure=name, axes=6, all_contexts=True, labels_within_canvas=True)
        )
    p.durable_json(
        directory / "reporting.json",
        dict(
            task="0046",
            status="aggregate_only_figures",
            figures=names,
            rows=len(rows),
            contrasts=len(contrasts),
            layout_checks=layout,
            scope="all seeds and source repetitions; signed null/unfavorable effects retained; no clipping, inference or source opens",
        ),
        exclusive=True,
    )
    return names + ["reporting.json"]
