"""Owned aggregates only; constant-cost what-if figures, no trace/model reads."""

from latenttrigger.simulation import protocol as p
from latenttrigger.simulation.sweep import AGGREGATE, validate_aggregates

FIGURES = ("latency.png", "loss.png", "sensitivity.png")


def render(directory, *, poll=lambda: None):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    report = validate_aggregates(p.read(directory / AGGREGATE))
    rows = report["rows"]
    markers = {41: "o", 42: "^", 43: "s"}
    colors = {p.CANDIDATES[0]: "#2166ac", p.CANDIDATES[1]: "#d6604d"}
    labels = {p.CANDIDATES[0]: "PCA cost", p.CANDIDATES[1]: "AE v2 cost"}
    policy_labels = ["B1\n0"] + [f"B{b}\n{t // 1000}µs" for b, t in p.POLICIES[1:]]
    for measure, filename, title in [
        ("latency_ns_p99", "latency.png", "Modeled survivor latency p99"),
        ("overflow_fraction", "loss.png", "Drop-tail overflow loss / generated"),
    ]:
        fig, axes = plt.subplots(3, 2, figsize=(15, 11), layout="constrained")
        for i, rate in enumerate((10000, 100000, 1000000)):
            for j, mode in enumerate(("periodic", "poisson")):
                ax = axes[i, j]
                for r in rows:
                    if (
                        r["group"] != "main"
                        or r["nominal_rate"] != rate
                        or r["arrival_mode"] != mode
                    ):
                        continue
                    x = (
                        p.POLICIES.index((r["batch"], r["timeout_ns"]))
                        + (-0.16 if r["candidate"] == p.CANDIDATES[0] else 0.16)
                        + (r["seed"] - 42) * 0.035
                    )
                    y = (
                        r[measure] / 1000
                        if measure.startswith("latency")
                        else r[measure] * 100
                    )
                    ax.scatter(
                        x,
                        y,
                        color=colors[r["candidate"]],
                        marker=markers[r["seed"]],
                        s=22,
                        alpha=0.85,
                    )
                ax.set_title(f"{mode}; nominal {rate:,}/s")
                ax.set_xticks(range(9), policy_labels, fontsize=8)
                ax.set_ylabel(
                    "p99 latency (µs), completed only"
                    if measure.startswith("latency")
                    else "overflow / 5000 generated (%)"
                )
                ax.grid(alpha=0.18)
                if measure.startswith("latency"):
                    ax.set_yscale("log")
                    ax.axhline(1000, color="gray", ls="--", lw=1)
                else:
                    ax.set_ylim(-2, 102)
        handles = [
            plt.Line2D([], [], marker="o", ls="", color=colors[m], label=labels[m])
            for m in p.CANDIDATES
        ]
        handles += [
            plt.Line2D(
                [], [], marker=markers[s], ls="", color="black", label=f"seed{s}"
            )
            for s in markers
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=5)
        fig.suptitle(
            title
            + "; fixed pooled mean service, padded partial batches\n5000 arrivals; capacity1024; full drain; points show all seeds; no stationary or deployment claim",
            fontsize=12,
        )
        poll()
        fig.savefig(directory / filename, dpi=160)
        plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(15, 9), layout="constrained")
    for i, model in enumerate(p.CANDIDATES):
        workers = ["PCA" + str(w) if i == 0 else "AE" + str(w) for w in (1, 2, 3)]
        choices = [("pooled600", "mean_ns")] + [
            (w, s) for w in workers for s in ("mean_ns", "p99_ns", "max_ns")
        ]
        chosen = [
            r
            for r in rows
            if r["candidate"] == model
            and r["nominal_rate"] == 100000
            and r["arrival_mode"] == "poisson"
            and r["batch"] == 128
            and r["timeout_ns"] == 100000
        ]
        for r in chosen:
            x = (
                choices.index((r["service_worker"], r["service_statistic"]))
                + (r["seed"] - 42) * 0.055
            )
            for j, y in enumerate(
                (r["latency_ns_p99"] / 1e6, r["overflow_fraction"] * 100)
            ):
                axes[i, j].scatter(
                    x, y, color=colors[model], marker=markers[r["seed"]], s=30
                )
        ticks = ["pooled\nmean"] + [
            w + "\n" + s.replace("_ns", "") for w, s in choices[1:]
        ]
        for j in (0, 1):
            ax = axes[i, j]
            ax.set_xticks(range(10), ticks, fontsize=8)
            ax.grid(alpha=0.18)
            ax.set_title(labels[model])
            ax.set_ylabel(
                "p99 survivor latency (ms)" if j == 0 else "overflow / generated (%)"
            )
            if j == 0:
                ax.set_yscale("log")
                ax.axhline(1, color="gray", ls="--", lw=1)
            else:
                ax.set_ylim(-2, 102)
    fig.suptitle(
        "Fixed stress: Poisson100000/s; B128 / timeout100µs; capacity1024; all three seeds\nEach mean/p99/max is constant for every batch; AE2 max26.2485ms is intentionally harsh, not a recurring measured stall",
        fontsize=12,
    )
    fig.legend(
        handles=[
            plt.Line2D(
                [], [], marker=markers[s], ls="", color="black", label=f"seed{s}"
            )
            for s in markers
        ],
        loc="outside lower center",
        ncol=3,
    )
    poll()
    fig.savefig(directory / "sensitivity.png", dpi=160)
    plt.close(fig)
    p.durable_json(
        directory / "reporting.json",
        dict(
            kind="aggregate_only_figures",
            figures=list(FIGURES),
            aggregate_sha256=p.file_hash(directory / AGGREGATE),
            scientific_or_physical_claim=False,
            display="Latency uses log axes with no clipping; loss0–100%; discrete points, all seed variation; deadline illustrative",
        ),
        exclusive=True,
    )
    return [*FIGURES, "reporting.json"]
