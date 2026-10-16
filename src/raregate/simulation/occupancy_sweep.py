"""Fixed3024 replay matrix, streamed occupancy/anchor ledgers and systems contrasts."""

import csv

from raregate.simulation import occupancy_protocol as p
from raregate.simulation.joint_engine import ReplayPolicy, validate_result
from raregate.simulation.occupancy_engine import Assignment, simulate
from raregate.simulation.occupancy_source import deep_size
from raregate.simulation.traces import generate

KEYS = "mode rate seed candidate B timeout_ns repetition mapping billing".split()
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
    "batches",
    "busy_ns",
    "mapped_batches_fraction",
    "mapped_events_fraction",
    "mapped_busy_ns_fraction",
    "modeled_row_work",
)
STRING_FIELDS = set(KEYS) & {"mode", "candidate", "mapping", "billing"} | {
    "trace_sha256",
    "contrast",
    "vector_sha256",
    "pair_order_sha256",
    "assignment_counts",
}


class StreamCSV:
    def __init__(self, path, bound):
        self.path = path
        self.file = path.open("x", newline="")
        self.writer = None
        self.count = 0
        self.bound = bound

    def append(self, row):
        p.require(self.count < self.bound, "Stream row ceiling")
        # Serialize before presentation, so growth is rejected before writing.
        import io

        buffer = io.StringIO(newline="")
        if self.writer is None:
            self.fields = list(row)
        p.require(list(row) == self.fields, "Fixed streamed schema")
        writer = csv.DictWriter(buffer, fieldnames=self.fields, lineterminator="\n")
        if self.count == 0:
            writer.writeheader()
        writer.writerow(row)
        payload = buffer.getvalue()
        p.require(
            self.file.tell() + len(payload.encode()) <= 32 * 2**20, "CSV growth ceiling"
        )
        self.file.write(payload)
        self.count += 1
        self.writer = True

    def close(self):
        self.file.close()


def decode_rows(path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    result = []
    for row in rows:
        p.require(None not in row and None not in row.values(), "Aggregate CSV shape")
        result.append(
            {
                k: v
                if k in STRING_FIELDS
                else None
                if v == ""
                else float(v)
                if any(c in v for c in ".eE")
                else int(v)
                for k, v in row.items()
            }
        )
    return result


def contrasts(context):
    first = context[0]
    base = {k: first[k] for k in KEYS[:-2]}
    bykey = {(r["mapping"], r["billing"]): r for r in context}
    p.require(len(bykey) == 4, "Four contrasting variants")
    nn, nc, pn, pc = (
        bykey[m, b]
        for m, b in (
            ("next_anchor", "natural_anchor"),
            ("next_anchor", "full_control"),
            ("previous_anchor", "natural_anchor"),
            ("previous_anchor", "full_control"),
        )
    )
    result = []
    for name in (
        "next_natural_minus_control",
        "previous_natural_minus_control",
        "mapping_interaction",
    ):
        row = dict(
            base,
            contrast=name,
            trace_sha256=first["trace_sha256"],
            generated=first["generated"],
        )
        for label, r in zip(
            ("next_natural", "next_control", "previous_natural", "previous_control"),
            (nn, nc, pn, pc),
            strict=True,
        ):
            for key in (
                "completed",
                "overflow_dropped",
                "deadline_misses_processed",
                "generated",
                "batches",
                "busy_ns",
            ):
                row[label + "_" + key] = r[key]
        for metric in DIFFS:
            nd = (
                None
                if nn[metric] is None or nc[metric] is None
                else nn[metric] - nc[metric]
            )
            pd = (
                None
                if pn[metric] is None or pc[metric] is None
                else pn[metric] - pc[metric]
            )
            row[metric + "_difference"] = (
                nd
                if name.startswith("next")
                else pd
                if name.startswith("previous")
                else None
                if nd is None or pd is None
                else pd - nd
            )
            row[metric + "_previous_minus_next_natural"] = (
                None
                if pn[metric] is None or nn[metric] is None
                else pn[metric] - nn[metric]
            )
            row[metric + "_previous_minus_next_control"] = (
                None
                if pc[metric] is None or nc[metric] is None
                else pc[metric] - nc[metric]
            )
        result.append(row)
    return result


def validate_rows(rows, summary):
    p.require(
        [tuple(r[k] for k in KEYS) for r in rows] == list(p.matrix()),
        "Complete ordered3024matrix",
    )
    traces = {
        (v["mode"], v["nominal_rate"], v["seed"]): v["trace_sha256"]
        for v in summary["traces"]
    }
    for r in rows:
        validate_result(r, ReplayPolicy(r["B"], r["timeout_ns"], 1024, 100000000))
        p.require(
            r["generated"] == 5000
            and r["trace_sha256"] == traces[r["mode"], r["rate"], r["seed"]]
            and r["exact_events"] + r["mapped_events"] == r["completed"]
            and r["exact_batches"] + r["mapped_batches"] == r["batches"]
            and r["exact_busy_ns"] + r["mapped_busy_ns"] == r["busy_ns"]
            and r["modeled_minus_actual_rows"]
            == r["modeled_row_work"] - r["completed"],
            "Scenario identity/occupancy conservation",
        )
    for i in range(0, len(rows), 4):
        g = rows[i : i + 4]
        if g[0]["B"] == 1:
            for left, right in ((g[0], g[2]), (g[1], g[3])):
                p.require(
                    {k: v for k, v in left.items() if k != "mapping"}
                    == {k: v for k, v in right.items() if k != "mapping"},
                    "B1 mapping negative control",
                )
    return rows


def verify_audits(directory, rows, summary):
    byscenario = {tuple(r[k] for k in KEYS): r for r in rows}
    totals = {
        key: dict(
            batches=0,
            events=0,
            busy_ns=0,
            modeled_rows=0,
            exact_batches=0,
            exact_events=0,
            exact_busy_ns=0,
            mapped_batches=0,
            mapped_events=0,
            mapped_busy_ns=0,
        )
        for key in byscenario
    }
    ordered_keys = list(byscenario)
    scenario_index = -1
    current_key = None
    last_m = 0
    anchor_totals = {}
    oc = 0
    with (directory / "occupancies.csv").open(newline="") as f:
        for raw in csv.DictReader(f):
            r = {k: v if k in STRING_FIELDS else int(v) for k, v in raw.items()}
            key = tuple(r[k] for k in KEYS)
            if key != current_key:
                scenario_index += 1
                p.require(
                    scenario_index < len(ordered_keys)
                    and key == ordered_keys[scenario_index],
                    "Ordered occupancy scenario groups",
                )
                current_key = key
                last_m = 0
            p.require(
                type(r["m"]) is int and last_m < r["m"] <= r["B"],
                "Unique ascending current occupancy",
            )
            last_m = r["m"]
            oc += 1
            from raregate.simulation.occupancy_engine import anchor

            p.require(
                r["k"] == anchor(r["B"], r["m"], r["mapping"])
                and r["events"] == r["m"] * r["batches"]
                and r["exact_point"] == int(r["m"] == r["k"])
                and r["k_minus_m"] == r["k"] - r["m"]
                and r["anchor_minus_actual_rows"] == r["batches"] * (r["k"] - r["m"])
                and r["modeled_rows"]
                == r["batches"]
                * (r["k"] if r["billing"] == "natural_anchor" else r["B"])
                and r["modeled_minus_actual_rows"] == r["modeled_rows"] - r["events"],
                "Occupancy modeled work",
            )
            t = totals[key]
            for name in ("batches", "events", "busy_ns", "modeled_rows"):
                t[name] += r[name]
            for name in ("batches", "events", "busy_ns"):
                t[("exact_" if r["exact_point"] else "mapped_") + name] += r[name]
            ak = (*key, r["k"])
            q = anchor_totals.setdefault(ak, [0, 0])
            q[0] += r["batches"]
            q[1] += r["busy_ns"]
    p.require(scenario_index + 1 == len(ordered_keys), "All occupancy scenario groups")
    p.require(
        oc <= p.planner()["occupancy_row_bound"]
        and oc == summary["audit_row_counts"]["occupancies"],
        "Occupancy row count",
    )
    seen = set()
    ac = 0
    source_use = {key: [0] * 20 for key in summary["vectors"]}
    with (directory / "anchor-audit.csv").open(newline="") as f:
        for raw in csv.DictReader(f):
            r = {
                k: v
                if k in STRING_FIELDS
                else None
                if v == ""
                else float(v)
                if "." in v
                else int(v)
                for k, v in raw.items()
            }
            key = tuple(r[k] for k in KEYS)
            ak = (*key, r["k"])
            p.require(ak not in seen and key in totals, "Unique anchor identity")
            seen.add(ak)
            ac += 1
            vector_key = f"{r['candidate']}/{r['repetition']}/{r['B']}/{r['k']}"
            v = summary["vectors"][vector_key]
            counts = list(map(int, r["assignment_counts"].split(",")))
            j = r["dispatch_count"]
            p.require(
                len(counts) == 20
                and counts == [j // 20 + int(i < j % 20) for i in range(20)]
                and r["cursor_wraps"] == j // 20
                and r["cursor_remainder"] == j % 20
                and r["unused_samples"] == sum(n == 0 for n in counts)
                and r["vector_sha256"] == v["sha256"]
                and r["pair_order_sha256"] == v["pair_order_sha256"],
                "Anchor cursor/fingerprint",
            )
            side = p.BILLINGS.index(r["billing"])
            busy = sum(
                pair[side] * n
                for pair, n in zip(v["paired_integer_payload"], counts, strict=True)
            )
            p.require(
                r["assigned_busy_ns"] == busy
                and anchor_totals.get(ak, [0, 0]) == [j, busy],
                "Independent anchor duration dot product",
            )
            source_use[vector_key] = [
                a + b for a, b in zip(source_use[vector_key], counts, strict=True)
            ]
    p.require(
        ac == p.planner()["anchor_row_bound"] == summary["audit_row_counts"]["anchors"],
        "All anchor categories including zeros",
    )
    for key, t in totals.items():
        row = byscenario[key]
        for n in (
            "batches",
            "busy_ns",
            "exact_batches",
            "exact_events",
            "exact_busy_ns",
            "mapped_batches",
            "mapped_events",
            "mapped_busy_ns",
        ):
            p.require(t[n] == row[n], "Scenario histogram totals")
        p.require(
            t["events"] == row["completed"]
            and t["modeled_rows"] == row["modeled_row_work"],
            "Useful/model rows",
        )
    p.require(source_use == summary["source_use_counts"], "All source-use counts")
    return dict(
        occupancies=oc,
        anchors=ac,
        dispatch_assignments=sum(sum(q) for q in source_use.values()),
    )


def run(vectors, audit, directory, *, poll=lambda: None, notify=lambda c: None):
    traces = {}
    metadata = []
    counters = dict(
        synthetic_trace_generation_requests=0,
        synthetic_unique_events=0,
        scenarios_started=0,
        scenarios_completed=0,
        event_presentations_started=0,
        event_presentations_completed=0,
        dispatch_sample_assignments=0,
        new_replay_model_calls=0,
        inflight=None,
    )
    for mode in ("periodic", "poisson"):
        for rate in (500, 2500, 5000):
            for seed in (41, 42, 43):
                counters["synthetic_trace_generation_requests"] += 1
                notify(counters)
                poll()
                trace, meta = generate(mode, rate, seed)
                traces[mode, rate, seed] = trace
                metadata.append(meta)
                counters["synthetic_unique_events"] += 5000
    retained = sum(m["retained_python_bytes"] for m in metadata)
    p.require(retained <= 16 * 2**20, "16MiB retained traces")
    vector_meta = {
        f"{c}/{rep}/{b}/{k}": v.metadata() for (c, rep, b, k), v in vectors.items()
    }
    source_use = {key: [0] * 20 for key in vector_meta}
    lookup_bytes = deep_size((vectors, vector_meta, source_use))
    p.require(
        lookup_bytes + 64 * 1024 <= 2**20,
        "1MiB vectors, lookup metadata/counts and current assignment margin",
    )
    rows = []
    context = []
    contrast_rows = []
    streams = {
        name: StreamCSV(directory / (name + ".csv"), bound)
        for name, bound in (
            ("scenarios", 3024),
            ("contrasts", 2268),
            ("occupancies", 145584),
            ("anchor-audit", 12528),
        )
    }
    try:
        for key in p.matrix():
            mode, rate, seed, c, b, t, rep, mapping, billing = key
            counters["scenarios_started"] += 1
            counters["event_presentations_started"] += 5000
            counters["inflight"] = dict(zip(KEYS, key, strict=True))
            notify(counters)
            poll()
            service = Assignment(
                {k: vectors[c, rep, b, k] for k in p.ANCHORS[b]}, b, mapping, billing
            )
            result = simulate(
                traces[mode, rate, seed],
                ReplayPolicy(b, t, 1024, 100000000),
                service,
                poll=poll,
            )
            row = dict(
                zip(KEYS, key, strict=True),
                trace_sha256=next(
                    m["trace_sha256"]
                    for m in metadata
                    if (m["mode"], m["nominal_rate"], m["seed"]) == (mode, rate, seed)
                ),
                **result,
            )
            streams["scenarios"].append(row)
            rows.append(row)
            context.append(row)
            base = {k: row[k] for k in KEYS}
            for occ in sorted(service.occupancies.values(), key=lambda x: x["m"]):
                streams["occupancies"].append(dict(base, **occ))
            for ar in service.audit():
                streams["anchor-audit"].append(dict(base, **ar))
                vk = f"{c}/{rep}/{b}/{ar['k']}"
                counts = map(int, ar["assignment_counts"].split(","))
                source_use[vk] = [
                    a + n for a, n in zip(source_use[vk], counts, strict=True)
                ]
            if len(context) == 4:
                for contrast in contrasts(context):
                    streams["contrasts"].append(contrast)
                    contrast_rows.append(contrast)
                context = []
            counters["scenarios_completed"] += 1
            counters["event_presentations_completed"] += 5000
            counters["dispatch_sample_assignments"] += row["dispatch_count"]
            counters["inflight"] = None
        notify(counters)
    finally:
        for stream in streams.values():
            stream.close()
    summary = dict(
        task="0046",
        identity=p.identity(),
        status="body_complete_awaiting_exit",
        source_audit=audit,
        vectors=vector_meta,
        source_use_counts=source_use,
        traces=metadata,
        retained_trace_bytes=retained,
        retained_vector_python_bytes=deep_size(vectors),
        combined_paired_lookup_python_bytes_with_current_margin=lookup_bytes
        + 64 * 1024,
        aggregate_python_bytes=deep_size((rows, contrast_rows)),
        counters=counters,
        expected=p.planner(),
        matrix_sha256=p.digest(p.matrix()),
        audit_row_counts=dict(
            occupancies=streams["occupancies"].count,
            anchors=streams["anchor-audit"].count,
        ),
        memory_envelope=dict(
            current_latency_entries_max=5000,
            current_wait_entries_max=5000,
            current_batch_size_entries_max=5000,
            current_FIFO_entries_max=1024,
            current_occupancy_entries_max=128,
            current_anchor_counts_max=100,
            conservative_current_python_workspace_bytes=4 * 2**20,
            source_parse_bytes_cap=8 * 2**20,
            source_parse_python_conservative_bytes=64 * 2**20,
            retained_traces_cap=16 * 2**20,
            retained_lookup_cap=2**20,
            owned_output_cap=128 * 2**20,
        ),
    )
    validate_rows(rows, summary)
    verify_audits(directory, rows, summary)
    summary["totals"] = {
        m + "/" + b: {
            name: sum(r[name] for r in rows if (r["mapping"], r["billing"]) == (m, b))
            for name in (
                "generated",
                "completed",
                "overflow_dropped",
                "deadline_misses_processed",
                "batches",
                "full_batches",
                "partial_batches",
                "busy_ns",
                "mapped_batches",
                "mapped_events",
                "mapped_busy_ns",
                "modeled_row_work",
                "anchor_minus_actual_rows",
                "modeled_minus_actual_rows",
            )
        }
        for m in p.MAPPINGS
        for b in p.BILLINGS
    }
    summary["contrast_ranges"] = {
        name: {
            metric: dict(
                minimum=min(
                    r[metric + "_difference"]
                    for r in contrast_rows
                    if r["contrast"] == name
                ),
                maximum=max(
                    r[metric + "_difference"]
                    for r in contrast_rows
                    if r["contrast"] == name
                ),
                negative=sum(
                    r[metric + "_difference"] < 0
                    for r in contrast_rows
                    if r["contrast"] == name
                ),
                positive=sum(
                    r[metric + "_difference"] > 0
                    for r in contrast_rows
                    if r["contrast"] == name
                ),
                zero=sum(
                    r[metric + "_difference"] == 0
                    for r in contrast_rows
                    if r["contrast"] == name
                ),
            )
            for metric in (
                "overflow_dropped",
                "deadline_misses_processed",
                "latency_ns_p99",
                "overflow_or_late_fraction_generated",
            )
        }
        for name in (
            "next_natural_minus_control",
            "previous_natural_minus_control",
            "mapping_interaction",
        )
    }
    p.require(
        len(rows) == 3024
        and len(contrast_rows) == 2268
        and counters["event_presentations_completed"] == 15120000,
        "Complete fixed sweep",
    )
    p.durable_json(directory / "summary.json", summary, exclusive=True)
    return summary
