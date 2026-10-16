"""Three aggregate-only figures, streamed input and bounded plotting coordinates."""

from raregate.simulation import refined_service_protocol as p
from raregate.simulation.refined_service_source import deep_size
from raregate.simulation.refined_service_sweep import decode_rows


def render(directory, aggregate, poll=lambda: None):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import SymLogNorm
    from matplotlib.lines import Line2D

    # Retain coordinates/labels only, never duplicate whole aggregate dictionaries.
    billing = []
    support = []
    residual = []
    sc = cc = 0
    for row in decode_rows(aggregate / "contrasts.csv"):
        cc += 1
        name = row["contrast"]
        base = (row["candidate"], row["seed"], row["repetition"])
        if name.startswith("refined_32/") and name.endswith("natural_minus_control"):
            billing.append(
                (
                    *base,
                    int("/previous_" in name),
                    100 * row["overflow_fraction_difference"],
                    100 * row["overflow_or_late_fraction_generated_difference"],
                )
            )
        if name.endswith("/support_interaction"):
            for level in ("difference", "natural_level_change", "control_level_change"):
                support.append(
                    (
                        *base,
                        int(name.startswith("previous")),
                        level,
                        100 * row["overflow_fraction_" + level],
                        100 * row["overflow_or_late_fraction_generated_" + level],
                    )
                )
    for row in decode_rows(aggregate / "scenarios.csv"):
        sc += 1
        if row["support"] == "refined_32":
            residual.append(
                (
                    row["candidate"],
                    row["seed"],
                    row["repetition"],
                    p.MAPPINGS.index(row["mapping"]) * 2
                    + p.BILLINGS.index(row["billing"]),
                    100 * row["mapped_events_fraction"],
                    100 * row["mapped_busy_ns_fraction"],
                    100 * row["modeled_minus_actual_rows"] / row["completed"],
                )
            )
    p.require(
        sc == cc == 6048 and deep_size((billing, support, residual)) <= 8 * 2**20,
        "Complete bounded aggregate plotting inputs",
    )
    markers = ["o", "^", "s", "D", "v", "P", "X", "<", ">"]
    colors = {1: "#00749b", 2: "#b45f06", 3: "#963b7b"}
    legend = [
        Line2D(
            [],
            [],
            linestyle="",
            marker=markers[(rep - 1) * 3 + seed - 41],
            color=colors[rep],
            label=f"rep {rep}, seed {seed}",
        )
        for rep in (1, 2, 3)
        for seed in (41, 42, 43)
    ]
    names = []
    layouts = []

    def finish(fig, axes, name, title):
        fig.suptitle(title, fontsize=12, y=0.985)
        fig.legend(handles=legend, loc="lower center", ncol=9, fontsize=8)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        p.require(
            all(
                (bbox := ax.get_tightbbox(renderer)).x0 >= fig.bbox.x0
                and bbox.y0 >= fig.bbox.y0
                and bbox.x1 <= fig.bbox.x1
                and bbox.y1 <= fig.bbox.y1
                for ax in axes.flat
            ),
            "All figure labels inside canvas",
        )
        fig.savefig(directory / name, dpi=135)
        plt.close(fig)
        names.append(name)
        layouts.append(
            dict(
                figure=name,
                axes=axes.size,
                labels_within_canvas=True,
                all_seed_repetitions=True,
            )
        )
        poll()

    def scatter(ax, group, signed=True):
        for rep in (1, 2, 3):
            for seed in (41, 42, 43):
                g = [r for r in group if r[1:3] == (seed, rep)]
                ax.scatter(
                    [r[-2] for r in g],
                    [r[-1] for r in g],
                    s=14,
                    alpha=0.65,
                    color=colors[rep],
                    marker=markers[(rep - 1) * 3 + seed - 41],
                )
        ax.grid(alpha=0.2)
        if signed:
            ax.axhline(0, c="black", lw=0.7)
            ax.axvline(0, c="black", lw=0.7)
            ax.set_xscale("symlog", linthresh=0.01)
            ax.set_yscale("symlog", linthresh=0.01)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ci, c in enumerate(p.CANDIDATES):
        for mi, m in enumerate(p.MAPPINGS):
            ax = axes[ci, mi]
            scatter(ax, [r for r in billing if r[0] == c and r[3] == mi])
            ax.set(
                title=f"{c} / {m}",
                xlabel="Natural − control overflow / generated (pp)",
                ylabel="Natural − control (overflow + late) / generated (pp)",
            )
    fig.subplots_adjust(
        left=0.09, right=0.97, bottom=0.12, top=0.87, hspace=0.48, wspace=0.40
    )
    finish(
        fig,
        axes,
        "outcomes.png",
        "Current refined support: billing loss/lateness contrasts, all modes/rates/policies\nStrict 100 ms illustrative deadline; generated denominator 5000; symlog threshold 0.01 pp; null/adverse points retained",
    )
    fig, axes = plt.subplots(4, 3, figsize=(18, 16))
    for ci, c in enumerate(p.CANDIDATES):
        for mi, m in enumerate(p.MAPPINGS):
            for col, level in enumerate(
                ("natural_level_change", "difference", "control_level_change")
            ):
                ax = axes[ci * 2 + mi, col]
                scatter(
                    ax,
                    [r for r in support if r[0] == c and r[3] == mi and r[4] == level],
                )
                ax.set(
                    title=f"{c} / {m}\n"
                    + {
                        "difference": "D refined − D coarse",
                        "natural_level_change": "Natural: refined − coarse",
                        "control_level_change": "Control: refined − coarse",
                    }[level],
                    xlabel="Δ overflow / generated (pp)",
                    ylabel="Δ (overflow + late) / generated (pp)",
                )
    fig.subplots_adjust(
        left=0.07, right=0.98, bottom=0.07, top=0.91, hspace=0.65, wspace=0.40
    )
    finish(
        fig,
        axes,
        "latency.png",
        "Within-current-campaign support sensitivity and both level changes\nD = natural − control; support interaction = D refined − D coarse; symlog threshold 0.01 pp; all contexts retained\nSupport changes selected case, sample phase and queue history: no causal isolation of adding measurements",
    )
    # Color in the residual figure describes modeled-row surplus; markers carry seed/repetition.
    legend = [
        Line2D(
            [],
            [],
            linestyle="",
            marker=markers[(rep - 1) * 3 + seed - 41],
            color="#555555",
            label=f"rep {rep}, seed {seed}",
        )
        for rep in (1, 2, 3)
        for seed in (41, 42, 43)
    ]
    fig, axes = plt.subplots(2, 4, figsize=(20, 9))
    norm = SymLogNorm(
        linthresh=1,
        vmin=min(r[-1] for r in residual),
        vmax=max(r[-1] for r in residual),
        base=10,
    )
    for ci, c in enumerate(p.CANDIDATES):
        for vi in range(4):
            ax = axes[ci, vi]
            g = [r for r in residual if r[0] == c and r[3] == vi]
            for rep in (1, 2, 3):
                for seed in (41, 42, 43):
                    q = [r for r in g if r[1:3] == (seed, rep)]
                    artist = ax.scatter(
                        [r[-3] for r in q],
                        [r[-2] for r in q],
                        c=[r[-1] for r in q],
                        cmap="coolwarm",
                        norm=norm,
                        s=16,
                        alpha=0.6,
                        marker=markers[(rep - 1) * 3 + seed - 41],
                    )
            ax.set(
                title=f"{c}\n{p.MAPPINGS[vi // 2]} / {p.BILLINGS[vi % 2]}",
                xlabel="Mapped useful events / completed (%)",
                ylabel="Mapped assigned busy / all assigned busy (%)",
                xlim=(-2, 102),
                ylim=(-2, 102),
            )
            ax.grid(alpha=0.2)
    fig.subplots_adjust(
        left=0.06, right=0.90, bottom=0.13, top=0.83, hspace=0.55, wspace=0.45
    )
    cax = fig.add_axes((0.93, 0.20, 0.012, 0.54))
    fig.colorbar(
        artist,
        cax=cax,
        label="Modeled row surplus / completed (%)\nSigned symlog color, linear ±1%",
    )
    finish(
        fig,
        axes,
        "sensitivity.png",
        "Refined support residual occupancy dependence; all modes/rates/policies/seeds/repetitions\nNatural models k rows, control B rows, useful completion m; signed deficit for k < m; exact lookup still transports finite warm samples",
    )
    p.durable_json(
        directory / "reporting.json",
        dict(
            task="0048",
            status="aggregate_only_figures",
            figures=names,
            rows=sc,
            contrasts=cc,
            layout_checks=layouts,
            retained_plot_coordinate_python_bytes=deep_size(
                (billing, support, residual)
            ),
            scope="owned aggregate streams only; no source opens, regeneration, models or scientific scores",
        ),
        exclusive=True,
    )
    return names + ["reporting.json"]
