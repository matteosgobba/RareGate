"""Owned aggregate validation and sparse paired cost reporting; no source payloads."""

import csv

from raregate.benchmarks import partial_raw_planning as plan
from raregate.benchmarks import partial_raw_protocol as p


def validate_worker(aggregate, rep):
    p.require(
        aggregate["task"] == "0045"
        and aggregate["exact_feature_score_decision_parity"] is True
        and aggregate["unique_raw_rows"] == 384
        and len(aggregate["cells"]) == 60
        and len(aggregate["pairs"]) == 600
        and len(aggregate["gates"]) == 360,
        "Complete paired worker scope/count/parity",
    )
    expected = [r for c in plan.candidates(rep) for r in plan.schedule(rep, c)]
    p.require(
        len(aggregate["chronology"]) == len(expected) == 1380,
        "Complete ordered paired chronology",
    )
    for ordinal, (r, e) in enumerate(
        zip(aggregate["chronology"], expected, strict=True)
    ):
        p.require(
            r["ordinal"] == ordinal
            and type(r["elapsed_ns"]) is int
            and r["elapsed_ns"] > 0
            and all(
                r[k] == e[k]
                for k in (
                    "candidate",
                    "B",
                    "m",
                    "side",
                    "actual_rows",
                    "service_B",
                    "phase",
                    "pair",
                    "pair_id",
                    "window_position",
                    "order_label",
                )
            ),
            "Paired ordered side/window/call identities",
        )
    keys = {
        (c, b, m, s) for c in plan.CANDIDATES for b, m in plan.CASES for s in plan.SIDES
    }
    p.require(
        {(c["candidate"], c["B"], c["m"], c["side"]) for c in aggregate["cells"]}
        == keys,
        "Exact60worker cells",
    )
    for c in aggregate["cells"]:
        actual, sb = plan.mapping(c["B"], c["m"], c["side"])
        values = [
            r["elapsed_ns"]
            for r in aggregate["chronology"]
            if r["candidate"] == c["candidate"]
            and r["B"] == c["B"]
            and r["m"] == c["m"]
            and r["side"] == c["side"]
            and r["phase"] == "timed"
        ]
        p.require(
            c["repetition"] == rep
            and c["actual_rows"] == actual
            and c["service_B"] == sb
            and c["scope"] == p.load()["scope"]
            and c["strategy"] == "natural"
            and c["count"] == 20
            and c["observations_ns"] == values
            and c["window_call_counts"] == [7, 7, 6],
            "Actual natural side coverage/order",
        )
    p.require(
        {r["pair_id"] for r in aggregate["pairs"]}
        == {r["pair_id"] for r in expected if r["phase"] == "timed"},
        "All600unique timed pair identities",
    )
    for pair in aggregate["pairs"]:
        matches = [
            r for r in aggregate["chronology"] if r["pair_id"] == pair["pair_id"]
        ]
        p.require(
            len(matches) == 2 and {r["side"] for r in matches} == set(plan.SIDES),
            "Exactly two separately timed pair sides",
        )
        byside = {r["side"]: r for r in matches}
        n, f = byside["natural_m"], byside["full_B_control"]
        p.require(
            pair["natural_ns"] == n["elapsed_ns"]
            and pair["control_ns"] == f["elapsed_ns"]
            and pair["difference_ns"] == n["elapsed_ns"] - f["elapsed_ns"]
            and pair["ratio"] == n["elapsed_ns"] / f["elapsed_ns"]
            and n["window_position"] == f["window_position"] == pair["window_position"]
            and n["order_label"] == f["order_label"] == pair["order_label"],
            "Exact pair sign/ratio/denominator/ordering",
        )
        p.require(
            pair["repetition"] == rep
            and all(pair[k] == n[k] for k in ("candidate", "B", "m", "pair"))
            and pair["natural_actual_rows"] == n["actual_rows"]
            and pair["control_actual_rows"] == f["actual_rows"]
            and pair["natural_service_B"] == n["service_B"]
            and pair["control_service_B"] == f["service_B"]
            and pair["window_index"] == n["pair"] % 3
            and n["phase"] == f["phase"] == "timed",
            "Complete paired nominal/actual/helper identities",
        )
    expected_gates = [
        dict(r, candidate=c, phase=phase, repetition=rep)
        for c in plan.candidates(rep)
        for phase in ("pre", "post")
        for r in plan.gate_schedule()
    ]
    reference_hashes = {}
    for g, e in zip(aggregate["gates"], expected_gates, strict=True):
        p.require(
            all(g[k] == v for k, v in e.items())
            and g["status"] == "exact_feature_score_decision_bytes_passed"
            and g["feature_score_decision_mismatches"] == [0, 0, 0],
            "Every ordered same-shaped gate identity/parity",
        )
        key = (g["candidate"], g["B"], g["m"], g["side"], g["window_position"])
        h = g["reference_identity"]
        p.require(
            set(h) == {"features", "scores", "decisions"}
            and all(
                type(v) is str and len(v) == 64 and set(v) <= set("0123456789abcdef")
                for v in h.values()
            ),
            "Exact same-shaped output integrity digests",
        )
        if g["phase"] == "pre":
            reference_hashes[key] = h
        else:
            p.require(
                reference_hashes[key] == h,
                "Post reference equals same-shaped pre reference",
            )
    return aggregate


def distribution(values):
    import numpy as np

    x = np.asarray(values, dtype=np.float64)
    p.require(len(x) > 0 and np.isfinite(x).all(), "Finite signed/ratio observations")
    return dict(
        count=len(x),
        minimum=float(x.min()),
        maximum=float(x.max()),
        mean=float(x.mean()),
        population_std=float(x.std(ddof=0)),
        **{
            f"p{q}": float(np.quantile(x, q / 100, method="linear"))
            for q in (50, 95, 99)
        },
    )


def run(directory, guard):
    import matplotlib
    import numpy as np

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    aggregates = []
    for rep in (1, 2, 3):
        guard.check()
        folder = directory.parent / f"repetition{rep}"
        receipt = p.read(folder / "receipt.json")
        p.require(
            receipt["status"] == "body_complete_awaiting_exit"
            and receipt["task"] == "0045"
            and p.file_hash(folder / "aggregate.json")
            == receipt["outputs"]["aggregate.json"],
            "Owned predecessor bytes",
        )
        aggregates.append(validate_worker(p.read(folder / "aggregate.json"), rep))
    cells = [c for a in aggregates for c in a["cells"]]
    pairs = [r for a in aggregates for r in a["pairs"]]
    cell_fields = [
        "candidate",
        "repetition",
        "B",
        "m",
        "side",
        "actual_rows",
        "service_B",
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
        "mean_actual_event_ns",
        "hypothetical_bill_per_m_ns",
        "actual_events_per_second",
        "window_call_counts",
    ]
    with (directory / "cells.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cell_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {k: ("7/7/6" if k == "window_call_counts" else c[k]) for k in cell_fields}
            for c in cells
        )
    with (directory / "pairs.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(pairs[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(pairs)
    pooled = []
    paired_groups = []
    for c in plan.CANDIDATES:
        for b, m in plan.CASES:
            for side in plan.SIDES:
                values = [
                    v
                    for row in cells
                    if (row["candidate"], row["B"], row["m"], row["side"])
                    == (c, b, m, side)
                    for v in row["observations_ns"]
                ]
                actual, sb = plan.mapping(b, m, side)
                pooled.append(
                    dict(
                        candidate=c,
                        B=b,
                        m=m,
                        side=side,
                        actual_rows=actual,
                        service_B=sb,
                        **distribution(values),
                        mean_actual_event_ns=float(np.mean(values)) / actual,
                        hypothetical_bill_per_m_ns=float(np.mean(values)) / m,
                    )
                )
            for rep in (1, 2, 3):
                group = [
                    r
                    for r in pairs
                    if (r["candidate"], r["B"], r["m"], r["repetition"])
                    == (c, b, m, rep)
                ]
                paired_groups.append(
                    dict(
                        candidate=c,
                        B=b,
                        m=m,
                        repetition=rep,
                        difference_ns=distribution([r["difference_ns"] for r in group]),
                        ratio=distribution([r["ratio"] for r in group]),
                        natural_first_pairs=sum(
                            r["order_label"] == "natural_m_first" for r in group
                        ),
                        control_first_pairs=sum(
                            r["order_label"] == "full_B_control_first" for r in group
                        ),
                    )
                )
    p.require(
        len(cells) == 180
        and len(pairs) == 1800
        and len(pooled) == 60
        and len(paired_groups) == 90,
        "Full reporting coverage",
    )
    summary = dict(
        task="0045",
        identity=p.identity(),
        status="aggregate_report_body_complete",
        cells=180,
        timed_calls=3600,
        timed_pairs=1800,
        warmup_calls=540,
        gate_side_records=1080,
        exact_feature_score_decision_parity=True,
        pooled=pooled,
        paired_groups=paired_groups,
        geometry=aggregates[0]["geometry"],
        peak_owned_array_bound_bytes=max(
            a["peak_owned_array_bound_bytes"] for a in aggregates
        ),
        explicit_reference_window_ID_golden_bytes=max(
            a["explicit_reference_window_ID_golden_bytes"] for a in aggregates
        ),
        counts=p.load()["expected"],
        timer_contexts=[a["cells"][0]["timer"] for a in aggregates],
        interpretation="Sparse paired warm-window natural costs; no padded service, unmeasured occupancy interpolation, causal component isolation or deployment policy",
    )
    p.durable_json(directory / "summary.json", summary, exclusive=True)
    colors = {"natural_m": "#126b98", "full_B_control": "#c87715"}
    fig, axes = plt.subplots(2, 4, figsize=(15, 8), layout="constrained")
    for ci, c in enumerate(plan.CANDIDATES):
        for bi, b in enumerate((1, 8, 32, 128)):
            ax = axes[ci, bi]
            for side in plan.SIDES:
                for rep in (1, 2, 3):
                    g = [
                        r
                        for r in cells
                        if r["candidate"] == c
                        and r["B"] == b
                        and r["side"] == side
                        and r["repetition"] == rep
                    ]
                    ax.scatter(
                        [r["m"] for r in g],
                        [r["mean_ns"] / 1e6 for r in g],
                        s=22,
                        color=colors[side],
                        marker=("o", "s", "^")[rep - 1],
                        label=side if rep == 1 else None,
                    )
            ax.set(
                title=f"{c}\nNominal B={b}",
                xlabel="Actual natural m",
                ylabel="Joint mean ms (log)",
            )
            ax.set_yscale("log")
            ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(
        "Natural m versus containing full-B control — all three workers\nSeparate HDF reads; full controls retain all B actual outputs, no padding",
        fontsize=12,
    )
    fig.savefig(directory / "joint-cost.png", dpi=150)
    plt.close(fig)
    guard.check()
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), layout="constrained")
    for ci, c in enumerate(plan.CANDIDATES):
        labels = [f"{b}/{m}" for b, m in plan.CASES]
        for index, (b, m) in enumerate(plan.CASES):
            group = [
                r for r in pairs if r["candidate"] == c and r["B"] == b and r["m"] == m
            ]
            for order, marker in [
                ("natural_m_first", "o"),
                ("full_B_control_first", "x"),
            ]:
                g = [r for r in group if r["order_label"] == order]
                axes[ci, 0].scatter(
                    [index] * len(g),
                    [r["difference_ns"] / 1e6 for r in g],
                    s=8,
                    alpha=0.5,
                    marker=marker,
                    color="#126b98" if order == "natural_m_first" else "#c87715",
                )
                axes[ci, 1].scatter(
                    [index] * len(g),
                    [r["ratio"] for r in g],
                    s=8,
                    alpha=0.5,
                    marker=marker,
                    color="#126b98" if order == "natural_m_first" else "#c87715",
                )
        for ax in axes[ci]:
            ax.set_xticks(range(15), labels, rotation=65)
            ax.grid(alpha=0.2)
            ax.set_title(c)
            ax.set_xlabel("Nominal B / actual m")
        axes[ci, 0].set_ylabel("natural − full (ms); symlog .01")
        axes[ci, 0].set_yscale("symlog", linthresh=0.01)
        axes[ci, 0].axhline(0, color="black", linewidth=0.8)
        axes[ci, 1].set_ylabel("natural / full ratio")
        axes[ci, 1].axhline(1, color="black", linewidth=0.8)
    fig.suptitle(
        "All1800 matched timing pairs; order orange=control first, blue=natural first\nB=m null cases retained; points and range are observations, no confidence intervals",
        fontsize=12,
    )
    fig.savefig(directory / "paired-cost.png", dpi=150)
    plt.close(fig)
    guard.check()
    fig, axes = plt.subplots(3, 2, figsize=(15, 9), layout="constrained")
    for ri, a in enumerate(aggregates):
        for ci, c in enumerate(plan.CANDIDATES):
            ax = axes[ri, ci]
            for side in plan.SIDES:
                g = [
                    r
                    for r in a["chronology"]
                    if r["candidate"] == c
                    and r["side"] == side
                    and r["phase"] == "timed"
                ]
                ax.scatter(
                    [r["ordinal"] for r in g],
                    [r["elapsed_ns"] / 1e6 for r in g],
                    s=6,
                    color=colors[side],
                    label=side,
                )
            ax.set(
                title=f"Worker{ri + 1} / {c}",
                xlabel="Original side-call ordinal (warmups omitted)",
                ylabel="Joint ms (log)",
            )
            ax.set_yscale("log")
            ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(
        "All3600timed calls in fixed chronology; no trimming or stationary-process claim",
        fontsize=12,
    )
    fig.savefig(directory / "chronology.png", dpi=150)
    plt.close(fig)
    guard.check()
    return [
        "cells.csv",
        "pairs.csv",
        "summary.json",
        "joint-cost.png",
        "paired-cost.png",
        "chronology.png",
    ]
