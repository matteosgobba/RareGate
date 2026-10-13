"""Owned cost/identity aggregates only; no model/data instantiation or source reads."""

import csv

import matplotlib
import numpy as np

from latenttrigger.benchmarks import development_decision_planning as plan
from latenttrigger.benchmarks import development_decision_protocol as p
from latenttrigger.benchmarks.development_payload_measure import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def collect(base):
    aggregates = []
    for rep in (1, 2, 3):
        folder = base / f"repetition{rep}"
        receipt = p.read(folder / "receipt.json")
        agg = p.read(folder / "aggregate.json")
        p.require(
            receipt["status"] == "body_complete_awaiting_exit"
            and receipt["outputs"]["aggregate.json"]
            == p.file_hash(folder / "aggregate.json"),
            "Owned aggregate identity",
        )
        p.require(
            agg["exact_feature_score_decision_parity"] is True
            and len(agg["cells"]) == 8
            and len(agg["gates"]) == 48,
            "Complete joint parity/cells/gates",
        )
        aggregates.append(agg)
    cells = [v for a in aggregates for v in a["cells"]]
    p.require(
        len(cells) == 24
        and {(v["repetition"], v["candidate"], v["B"]) for v in cells}
        == {
            (i, c, b) for i in (1, 2, 3) for c in plan.CANDIDATES for b in plan.BATCHES
        },
        "Complete unique fixed matrix",
    )
    pooled = []
    for candidate in plan.CANDIDATES:
        for b in plan.BATCHES:
            group = [v for v in cells if v["candidate"] == candidate and v["B"] == b]
            p.require(
                all(
                    v["count"] == 20
                    and v["strategy"] == "natural"
                    and v["scope"] == "selected_raw_to_decisions"
                    and len(v["observations_ns"]) == 20
                    for v in group
                ),
                "Only full natural joint cells/all20calls",
            )
            values = [v for row in group for v in row["observations_ns"]]
            pooled.append(
                dict(
                    candidate=candidate,
                    B=b,
                    **stats(values),
                    mean_selected_event_ns=float(np.mean(values)) / b,
                )
            )
    return aggregates, cells, pooled


def run(directory, guard):
    aggregates, cells, pooled = collect(directory.parent)
    fields = [
        "repetition",
        "candidate",
        "B",
        "scope",
        "strategy",
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
        "candidate_B_order",
        "timer_implementation",
        "timer_resolution_seconds",
        "cache",
    ]
    with (directory / "cells.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in cells:
            out = {k: row[k] for k in fields if k in row}
            out.update(
                window_call_counts="7/7/6",
                candidate_B_order="AE_PCA_descendingB"
                if row["repetition"] == 2
                else "PCA_AE_ascendingB",
                timer_implementation=row["timer"]["implementation"],
                timer_resolution_seconds=row["timer"]["resolution_seconds"],
                cache="1MiB_521_0.75_persistent_handle",
            )
            writer.writerow(out)
    p.durable_json(
        directory / "summary.json",
        dict(
            status="aggregate_report_body_complete",
            cells=24,
            timed_calls=480,
            warmup_calls=72,
            pooled=pooled,
            exact_feature_score_decision_parity=True,
            geometry=aggregates[0]["geometry"],
            cache="warm_OS_prehashed_pregated;persistent1MiB521.75",
            effective_decoder_threads="unknown",
            tails="20serial calls/cell;no production-p99/independent distribution/capacity guarantee",
            peak_owned_array_bound_bytes=max(
                v["peak_owned_array_bound_bytes"] for v in aggregates
            ),
        ),
        exclusive=True,
    )
    labels = {"pca-v1": "PCA-six", "compact-autoencoder-v2": "AE-v2"}
    colors = {"pca-v1": "#0072B2", "compact-autoencoder-v2": "#D55E00"}
    plt.rcParams.update({"font.size": 10, "figure.dpi": 140})
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    for candidate in plan.CANDIDATES:
        for rep in (1, 2, 3):
            group = sorted(
                (
                    v
                    for v in cells
                    if v["candidate"] == candidate and v["repetition"] == rep
                ),
                key=lambda v: v["B"],
            )
            for ax, field, scale in (
                (axes[0], "mean_ns", 1e6),
                (axes[1], "mean_selected_event_ns", 1e3),
            ):
                ax.plot(
                    [v["B"] for v in group],
                    [v[field] / scale for v in group],
                    color=colors[candidate],
                    marker=["o", "s", "^"][rep - 1],
                    label=f"{labels[candidate]}; rep {rep}",
                    alpha=0.8,
                )
    for ax in axes:
        ax.set(
            xscale="log",
            yscale="log",
            xlabel="Actual selected rows per full natural batch (B)",
        )
        ax.set_xticks(plan.BATCHES, labels=plan.BATCHES)
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Mean whole raw-to-decision batch cost (ms)")
    axes[1].set_ylabel("Mean amortized selected-event cost (µs)")
    axes[0].legend(fontsize=8, ncol=2)
    fig.suptitle(
        "Direct selected-development CPU raw-to-decision service — all repetitions"
    )
    fig.text(
        0.5,
        0.008,
        "Log axes; no clipping. Lines join fixed points only. File/model loading, transport and queueing excluded.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(directory / "joint-cost.png")
    plt.close(fig)
    guard.check()
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for rep, (agg, ax) in enumerate(zip(aggregates, axes, strict=True), 1):
        for candidate in plan.candidates(rep):
            group = [
                v
                for v in agg["chronology"]
                if v["candidate"] == candidate and v["phase"] == "timed"
            ]
            ax.scatter(
                [v["ordinal"] for v in group],
                [v["elapsed_ns"] / 1e6 for v in group],
                s=13,
                color=colors[candidate],
                label=labels[candidate],
            )
        bs = plan.BATCHES if rep != 2 else tuple(reversed(plan.BATCHES))
        for block, _c in enumerate(plan.candidates(rep)):
            for index, b in enumerate(bs):
                ax.text(
                    block * 92 + index * 23 + 11,
                    1.015,
                    f"B={b}",
                    transform=ax.get_xaxis_transform(),
                    fontsize=8,
                    ha="center",
                )
        ax.axvline(91.5, color="gray", alpha=0.4)
        ax.set(yscale="log", ylabel=f"Rep {rep}: ms")
        ax.grid(alpha=0.2)
    axes[0].set_title(
        "All timed observations; fixed candidate/B/window order and persistent cache",
        pad=28,
    )
    axes[0].legend(fontsize=8, ncol=2)
    axes[-1].set_xlabel(
        "Chronological call position (warm-ups occupy omitted positions)"
    )
    fig.text(
        0.5,
        0.008,
        "Log cost axis; no clipping or slow-call removal. Pre/post references outside timers; monitoring may interfere.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.025, 1, 1))
    fig.savefig(directory / "chronology.png")
    plt.close(fig)
    return ["cells.csv", "summary.json", "joint-cost.png", "chronology.png"]
