"""Three aggregate-only figures; every point shown, ranges include all observations."""

from raregate.simulation import joint_protocol as p
from raregate.simulation.joint_sweep import decode_rows


def render(directory, poll=lambda: None):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = decode_rows(directory / "scenarios.csv")
    with (directory / "contrasts.csv").open() as f:
        import csv

        contrasts = list(csv.DictReader(f))
    colors = dict(
        cyclic="#166e9a", constant="#e49b22", reverse="#a83372", rotation10="#2e8b57"
    )
    names = []
    for kind in ("outcomes", "latency"):
        poll()
        fig, axes = plt.subplots(2, 3, figsize=(16, 9))
        for ci, c in enumerate(p.CANDIDATES):
            for ri, rate in enumerate((500, 2500, 5000)):
                ax = axes[ci, ri]
                group = [r for r in rows if r["candidate"] == c and r["rate"] == rate]
                for assignment in colors:
                    g = [r for r in group if r["assignment"] == assignment]
                    if not g:
                        continue
                    if kind == "outcomes":
                        x = [100 * r["overflow_fraction"] for r in g]
                        y = [100 * r["deadline_miss_fraction_processed"] for r in g]
                    else:
                        x = [100 * r["completed"] / r["generated"] for r in g]
                        y = [r["latency_ns_p99"] / 1e6 for r in g]
                    ax.scatter(
                        x,
                        y,
                        s=12,
                        alpha=0.65,
                        color=colors[assignment],
                        label=assignment,
                    )
                ax.set_title(
                    f"{c}\n{rate} input events/s; {len(group)} scenarios", fontsize=10
                )
                if kind == "outcomes":
                    ax.set(
                        xlim=(-2, 102),
                        ylim=(-2, 102),
                        xlabel="Overflow / 5000 generated (%)",
                        ylabel="Late / completed survivors (%)",
                    )
                else:
                    ax.set(
                        xlim=(-2, 102),
                        xlabel="Completed survivors / 5000 generated (%)",
                        ylabel="Survivor p99 latency (ms); log scale",
                    )
                    ax.set_yscale("log")
                    ax.axhline(100, color="black", linestyle="--", linewidth=0.8)
                ax.grid(alpha=0.2)
        axes[0, 1].legend(fontsize=8, loc="best")
        fig.subplots_adjust(
            left=0.07, right=0.97, bottom=0.08, top=0.86, hspace=0.48, wspace=0.38
        )
        fig.suptitle(
            "Fixed finite FIFO replay — all seeds, workers, policies and assignments\n"
            + (
                "100 ms strict illustrative deadline; repeated presentations, no uncertainty bands"
                if kind == "outcomes"
                else "Overflow = 100% − completed%; quantiles exclude overflow; dashed line = 100 ms"
            ),
            fontsize=12,
        )
        name = kind + ".png"
        fig.savefig(directory / name, dpi=150, bbox_inches="tight", pad_inches=0.15)
        plt.close(fig)
        names.append(name)
    poll()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), layout="constrained")
    for index, a in enumerate(("cyclic", "reverse", "rotation10")):
        g = [r for r in contrasts if r["assignment"] == a]
        axes[0].scatter(
            [index] * len(g),
            [float(r["latency_ns_p99_difference"]) / 1e6 for r in g],
            s=10,
            alpha=0.4,
            color=colors[a],
        )
        axes[1].scatter(
            [index] * len(g),
            [float(r["overflow_dropped_difference"]) for r in g],
            s=10,
            alpha=0.4,
            color=colors[a],
        )
    for ax in axes[:2]:
        ax.set_xticks(
            range(3),
            ["cyclic − mean", "reverse − cyclic", "rotation10 − cyclic"],
            rotation=20,
        )
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_yscale("symlog", linthresh=0.01)
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Survivor p99 difference (ms); symlog, threshold .01")
    axes[1].set_ylabel("Overflow count difference; symlog, threshold .01")
    for a, color in colors.items():
        g = [r for r in rows if r["assignment"] == a and r["partial_batches"]]
        axes[2].scatter(
            [r["B"] for r in g],
            [100 * r["partial_slot_utilization"] for r in g],
            s=10,
            alpha=0.4,
            color=color,
            label=a,
        )
    axes[2].set(
        xscale="log",
        ylim=(-2, 102),
        xlabel="Charged natural B slots (log scale)",
        ylabel="Useful / charged partial slots (%)",
    )
    axes[2].set_xticks([8, 32, 128], ["8", "32", "128"])
    axes[2].grid(alpha=0.2)
    axes[2].legend(fontsize=8)
    fig.suptitle(
        "756 cyclic/mean and 252 ordering contrasts; all observations\nPartial m < B pays hypothetical full-B service; no measured partial cost or confidence interval",
        fontsize=12,
    )
    fig.savefig(directory / "sensitivity.png", dpi=150)
    plt.close(fig)
    names.append("sensitivity.png")
    p.durable_json(
        directory / "reporting.json",
        dict(
            status="aggregate_only_figures",
            figures=names,
            rows=len(rows),
            contrasts=len(contrasts),
            bounds="all displayed points; log latency / symlog differences, no clipping or confidence intervals",
        ),
        exclusive=True,
    )
    return names + ["reporting.json"]
