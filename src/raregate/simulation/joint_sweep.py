"""Fixed matrix, shared immutable traces, aggregate CSV and deterministic contrasts."""

import csv

from raregate.simulation import joint_protocol as p
from raregate.simulation.joint_engine import (
    ReplayPolicy,
    simulate,
    validate_result,
)
from raregate.simulation.joint_source import fingerprints
from raregate.simulation.traces import generate

KEYS = (
    "mode",
    "rate",
    "seed",
    "candidate",
    "B",
    "timeout_ns",
    "repetition",
    "assignment",
)
DIFFS = (
    "overflow_dropped",
    "completed",
    "completed_at_horizon",
    "pending_at_horizon",
    "deadline_misses_processed",
    "overflow_fraction",
    "deadline_miss_fraction_processed",
    "overflow_or_late_fraction_generated",
    "dispatch_wait_ns_mean",
    "dispatch_wait_ns_p99",
    "latency_ns_mean",
    "latency_ns_p50",
    "latency_ns_p95",
    "latency_ns_p99",
    "assigned_duration_mean_ns",
    "partial_batches",
    "partial_service_busy_ns",
    "slot_utilization",
    "drain_ns",
)


def write_csv(path, rows):
    with path.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def decode_rows(path):
    # Numeric types explicit from integer spellings; strings never reinterpreted.
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    strings = {
        "mode",
        "candidate",
        "assignment",
        "vector_sha256",
        "original_sample_assignment_counts",
        "trace_sha256",
    }
    return [
        {
            k: (
                v
                if k in strings
                else None
                if v == ""
                else float(v)
                if any(c in v for c in ".eE")
                else int(v)
            )
            for k, v in r.items()
        }
        for r in rows
    ]


def contrast_rows(rows):
    bykey = {tuple(r[k] for k in KEYS): r for r in rows}
    contrasts = []
    for row in rows:
        variant = row["assignment"]
        if variant == "constant":
            continue
        other = bykey[
            tuple(row[k] for k in KEYS[:-1])
            + ("constant" if variant == "cyclic" else "cyclic",)
        ]
        r = {k: row[k] for k in KEYS}
        r.update(
            reference_assignment=other["assignment"],
            trace_sha256=row["trace_sha256"],
            vector_sha256=row["vector_sha256"],
            generated=row["generated"],
            completed_left=row["completed"],
            completed_reference=other["completed"],
            overflow_left=row["overflow_dropped"],
            overflow_reference=other["overflow_dropped"],
            assigned_service_mean_left_ns=row["assigned_duration_mean_ns"],
            assigned_service_mean_reference_ns=other["assigned_duration_mean_ns"],
        )
        r.update(
            {
                k + "_difference": None
                if row[k] is None or other[k] is None
                else row[k] - other[k]
                for k in DIFFS
            }
        )
        contrasts.append(r)
    p.require(
        len(contrasts) == 1008
        and sum(r["assignment"] == "cyclic" for r in contrasts) == 756,
        "Fixed paired contrasts",
    )
    return contrasts


def validate_rows(rows, summary):
    p.require(
        [tuple(r[k] for k in KEYS) for r in rows] == list(p.matrix()),
        "Complete ordered1764matrix",
    )
    traces = {
        (m["mode"], m["nominal_rate"], m["seed"]): m["trace_sha256"]
        for m in summary["traces"]
    }
    vectors = summary["vectors"]
    for r in rows:
        validate_result(r, ReplayPolicy(r["B"], r["timeout_ns"], 1024, 100000000))
        p.require(
            r["generated"] == 5000
            and r["trace_sha256"] == traces[r["mode"], r["rate"], r["seed"]]
            and r["vector_sha256"]
            == vectors[f"{r['candidate']}/{r['B']}/{r['repetition']}"]["sha256"],
            "Shared trace/vector identities",
        )
        counts = [int(n) for n in r["original_sample_assignment_counts"].split(",")]
        p.require(
            len(counts) == 20
            and all(n >= 0 for n in counts)
            and r["dispatch_count"] == r["complete_cycles"] * 20 + r["cycle_remainder"]
            and r["final_cursor"] == r["cycle_remainder"],
            "Cursor/count accounting",
        )
        j = r["dispatch_count"]
        expected = [0] * 20
        if r["assignment"] != "constant":
            for i in range(20):
                index = (
                    19 - i
                    if r["assignment"] == "reverse"
                    else (i + 10) % 20
                    if r["assignment"] == "rotation10"
                    else i
                )
                expected[index] = j // 20 + (i < j % 20)
        p.require(counts == expected, "Original sample assignment counts")
        if r["assignment"] == "constant":
            p.require(
                r["assigned_duration_sum_ns"] == j * r["constant_mean_ceil_ns"],
                "Constant service bill",
            )
    p.require(
        sum(r["generated"] for r in rows) == 8820000
        and all(r["pending"] == 0 for r in rows),
        "Presentations/conservation",
    )
    return rows


def run(vectors, audit, directory, *, poll=lambda: None, notify=lambda c: None):
    traces = {}
    metadata = []
    for mode in ("periodic", "poisson"):
        for rate in (500, 2500, 5000):
            for seed in (41, 42, 43):
                poll()
                trace, meta = generate(mode, rate, seed)
                traces[mode, rate, seed] = trace
                meta["realized_rate_events_per_second"] = (
                    5000 * 1e9 / meta["horizon_ns"]
                )
                metadata.append(meta)
    retained = sum(m["retained_python_bytes"] for m in metadata)
    p.require(retained <= p.LIMITS["retained_trace_bytes"], "16MiB arrival traces")
    hashes = fingerprints(vectors)
    vector_meta = {
        f"{c}/{b}/{rep}": dict(
            sha256=hashes[f"{c}/{b}/{rep}"],
            count=20,
            sum_ns=sum(q),
            minimum_ns=min(q),
            maximum_ns=max(q),
            mean_ns=sum(q) / 20,
            constant_ceil_ns=(sum(q) + 19) // 20,
        )
        for (c, b, rep), q in vectors.items()
    }
    counters = dict(
        synthetic_trace_generation_requests=18,
        synthetic_unique_events=90000,
        scenarios_started=0,
        scenarios_completed=0,
        event_presentations_started=0,
        event_presentations_completed=0,
        new_replay_model_calls=0,
    )
    rows = []
    notify(counters)
    for mode, rate, seed, c, b, t, rep, variant in p.matrix():
        counters["scenarios_started"] += 1
        counters["event_presentations_started"] += 5000
        if len(rows) % 32 == 0:
            notify(counters)
        trace = traces[mode, rate, seed]
        r = simulate(
            trace,
            ReplayPolicy(b, t, 1024, 100000000),
            vectors[c, b, rep],
            variant,
            poll=poll,
        )
        rows.append(
            dict(
                zip(KEYS, (mode, rate, seed, c, b, t, rep, variant), strict=True),
                trace_sha256=next(
                    m["trace_sha256"]
                    for m in metadata
                    if (m["mode"], m["nominal_rate"], m["seed"]) == (mode, rate, seed)
                ),
                **{k: v for k, v in r.items() if k != "assignment"},
            )
        )
        counters["scenarios_completed"] += 1
        counters["event_presentations_completed"] += 5000
    summary = dict(
        task="0044",
        status="body_complete_awaiting_exit",
        source_audit=audit,
        vectors=vector_meta,
        traces=metadata,
        retained_trace_bytes=retained,
        counters=counters,
        expected=p.load_config()["expected"],
        matrix_sha256=p.digest(p.matrix()),
    )
    validate_rows(rows, summary)
    contrasts = contrast_rows(rows)
    summary["totals"] = {
        a: {
            k: sum(r[k] for r in rows if r["assignment"] == a)
            for k in (
                "generated",
                "completed",
                "overflow_dropped",
                "deadline_misses_processed",
                "batches",
                "full_batches",
                "partial_batches",
                "partial_useful_events",
                "partial_charged_slots",
                "partial_unused_slots",
                "partial_service_busy_ns",
                "busy_ns",
                "complete_cycles",
                "cycle_remainder",
            )
        }
        for a in ("cyclic", "constant", "reverse", "rotation10")
    }
    summary["contrast_ranges"] = {
        a: {
            k: dict(
                min=min(
                    r[k + "_difference"] for r in contrasts if r["assignment"] == a
                ),
                max=max(
                    r[k + "_difference"] for r in contrasts if r["assignment"] == a
                ),
                nonzero=sum(
                    r[k + "_difference"] != 0 for r in contrasts if r["assignment"] == a
                ),
            )
            for k in (
                "overflow_dropped",
                "deadline_misses_processed",
                "latency_ns_p99",
                "assigned_duration_mean_ns",
            )
        }
        for a in ("cyclic", "reverse", "rotation10")
    }
    write_csv(directory / "scenarios.csv", rows)
    write_csv(directory / "contrasts.csv", contrasts)
    notify(counters)
    p.durable_json(directory / "summary.json", summary, exclusive=True)
    return summary
