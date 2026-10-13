"""Owned aggregate tables only; never feature/raw/membership providers."""

import csv

import matplotlib
import numpy as np

from latenttrigger.benchmarks import development_payload_protocol as p
from latenttrigger.benchmarks import development_raw_planning as design
from latenttrigger.benchmarks.development_payload_measure import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def collect(base):
    aggregates = []
    for rep in (1, 2, 3):
        folder = base / f"repetition{rep}"
        receipt = p.read(folder / "receipt.json")
        aggregate = p.read(folder / "aggregate.json")
        p.require(
            receipt["status"] == "body_complete_awaiting_exit"
            and receipt["outputs"]["aggregate.json"]
            == p.file_hash(folder / "aggregate.json"),
            "Owned aggregate identity",
        )
        p.require(
            aggregate["exact_parity"] is True
            and len(aggregate["cells"]) == 12
            and len(aggregate["gates"]) == 24,
            "Complete parity/cell aggregates",
        )
        aggregates.append(aggregate)
    cells = [v for a in aggregates for v in a["cells"]]
    p.require(
        len(cells) == 36
        and len({(v["repetition"], v["B"], v["scope"]) for v in cells}) == 36,
        "Unique complete matrix",
    )
    expected = {
        (rep, b, s) for rep in (1, 2, 3) for b in design.BATCHES for s in design.SCOPES
    }
    p.require(
        {(v["repetition"], v["B"], v["scope"]) for v in cells} == expected,
        "Fixed candidate-free coverage",
    )
    pooled = []
    for b in design.BATCHES:
        for scope in design.SCOPES:
            selected = [v for v in cells if v["B"] == b and v["scope"] == scope]
            p.require(
                all(
                    v["count"] == 20 and len(v["observations_ns"]) == 20
                    for v in selected
                ),
                "All20observations",
            )
            times = [int(t) for v in selected for t in v["observations_ns"]]
            pooled.append(
                dict(
                    B=b,
                    scope=scope,
                    **stats(times),
                    mean_selected_event_ns=float(np.mean(times)) / b,
                )
            )
    return aggregates, cells, pooled


def run(directory, guard):
    aggregates, cells, pooled = collect(directory.parent)
    fields = [
        "repetition",
        "B",
        "scope",
        "count",
        "minimum_ns",
        "maximum_ns",
        "mean_ns",
        "population_std_ns",
        "p50_ns",
        "p95_ns",
        "p99_ns",
        "mean_selected_event_ns",
        "selected_events_per_second",
        "window_call_counts",
        "timer_implementation",
        "timer_resolution_seconds",
        "order",
    ]
    with (directory / "cells.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for cell in cells:
            row = {k: cell[k] for k in fields if k in cell}
            row.update(
                window_call_counts="7/7/6",
                timer_implementation=cell["timer"]["implementation"],
                timer_resolution_seconds=cell["timer"]["resolution_seconds"],
                order="descending_B_joint_feature_read"
                if cell["repetition"] == 2
                else "ascending_B_read_feature_joint",
            )
            writer.writerow(row)
    p.durable_json(
        directory / "summary.json",
        dict(
            status="aggregate_report_body_complete",
            cells=36,
            timed_calls=720,
            warmup_calls=108,
            pooled=pooled,
            exact_parity=True,
            geometry=aggregates[0]["geometry"],
            source_role="fixed_sparse_development_training",
            cache="1MiB/521/.75 persistent per worker; warm OS context",
            effective_decoder_threads="unknown",
            tails="20serial observations/cell; no production-p99 or distribution fit",
            max_owned_array_bound_bytes=max(
                a["peak_owned_array_bound_bytes"] for a in aggregates
            ),
        ),
        exclusive=True,
    )
    colors = ["#0072B2", "#D55E00", "#009E73"]
    labels = [
        "Selected HDF read",
        "Frozen feature construction",
        "Direct raw to features",
    ]
    plt.rcParams.update({"font.size": 10, "figure.dpi": 140})
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for _j, (scope, label, color) in enumerate(
        zip(design.SCOPES, labels, colors, strict=True)
    ):
        for rep in (1, 2, 3):
            subset = sorted(
                (v for v in cells if v["scope"] == scope and v["repetition"] == rep),
                key=lambda v: v["B"],
            )
            ax.plot(
                [v["B"] for v in subset],
                [v["mean_ns"] / 1e6 for v in subset],
                color=color,
                marker=["o", "s", "^"][rep - 1],
                alpha=0.8,
                label=f"{label}; rep {rep}",
            )
    ax.set(
        xscale="log",
        yscale="log",
        xlabel="Selected actual development rows per batch (B)",
        ylabel="Whole-batch mean measured cost (ms)",
        title="Fixed sparse development windows; all three repetitions",
    )
    ax.set_xticks(design.BATCHES, labels=design.BATCHES)
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8, ncol=2)
    fig.text(
        0.5,
        0.01,
        "Both axes log; no clipping. Lines join fixed points only. Models, queueing and external transport excluded.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(directory / "scope-cost.png")
    plt.close(fig)
    guard.check()
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for rep, (a, ax) in enumerate(zip(aggregates, axes, strict=True), 1):
        for scope, label, color in zip(design.SCOPES, labels, colors, strict=True):
            series = [
                v
                for v in a["chronological_observations"]
                if v["scope"] == scope and v["phase"] == "timed"
            ]
            ax.scatter(
                [v["ordinal"] for v in series],
                [v["elapsed_ns"] / 1e6 for v in series],
                s=13,
                color=color,
                label=label,
            )
        batch_order = design.BATCHES if rep != 2 else tuple(reversed(design.BATCHES))
        for index, b in enumerate(batch_order):
            ax.text(
                index * 69 + 34,
                0.9,
                f"B={b}",
                transform=ax.get_xaxis_transform(),
                ha="center",
                fontsize=8,
            )
        ax.set(yscale="log", ylabel=f"Rep {rep}: ms")
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8, ncol=3)
    axes[0].set_title(
        "Every timed call retained; fixed case/window order and persistent cache"
    )
    axes[-1].set_xlabel(
        "Chronological invocation position (warm-ups occupy omitted positions)"
    )
    fig.text(
        0.5,
        0.008,
        "Log cost axis; no clipping. Gates/preloads outside timers; sampled monitoring may interfere.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.025, 1, 1))
    fig.savefig(directory / "chronology.png")
    plt.close(fig)
    guard.check()
    geometry = aggregates[0]["geometry"]
    fig, ax = plt.subplots(figsize=(8, 5))
    for idx in range(3):
        rows = [v for v in geometry["windows"] if v["window_index"] == idx]
        ax.plot(
            [v["B"] for v in rows],
            [v["geometric_chunks"] for v in rows],
            marker="o",
            label=["First", "Middle", "Final"][idx],
        )
    ax.set(
        xscale="log",
        xlabel="Selected actual rows per request (B)",
        ylabel="Geometrically intersected 62-row chunks",
        title="Storage geometry only; cache hits and physical I/O unmeasured",
    )
    ax.set_xticks(design.BATCHES, labels=design.BATCHES)
    ax.legend()
    ax.grid(alpha=0.2)
    fig.text(
        0.5,
        0.01,
        "Log B axis; no clipping. One nominal decoded chunk: 1,042,096 bytes. Only selected rows reach Python.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(directory / "geometry.png")
    plt.close(fig)
    return [
        "cells.csv",
        "summary.json",
        "scope-cost.png",
        "chronology.png",
        "geometry.png",
    ]
