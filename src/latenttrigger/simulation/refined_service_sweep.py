"""Task0048 eight-way current-source replay, compact streams and ordered joins."""

import csv
import io
import math

from latenttrigger.simulation import refined_service_protocol as p
from latenttrigger.simulation.joint_engine import ReplayPolicy, validate_result
from latenttrigger.simulation.refined_service_engine import Assignment, anchor, simulate
from latenttrigger.simulation.refined_service_source import deep_size
from latenttrigger.simulation.traces import generate

KEYS = (
    "mode rate seed candidate B timeout_ns repetition support mapping billing".split()
)
# Every numerical outcome/descriptor is contrasted; context/source IDs are excluded.
STRINGS = {
    "mode",
    "candidate",
    "support",
    "mapping",
    "billing",
    "trace_sha256",
    "contrast",
    "vector_sha256",
    "pair_order_sha256",
    "assignment_counts",
}
FILE_BYTES = {
    "scenarios": 12 * 2**20,
    "contrasts": 32 * 2**20,
    "occupancies": 32 * 2**20,
    "anchor-audit": 16 * 2**20,
}
ROW_BYTES = {
    "scenarios": 4096,
    "contrasts": 16384,
    "occupancies": 256,
    "anchor-audit": 512,
}
CSV_TOTAL_CAP = 56 * 2**20
TOTAL_FIELDS = "generated completed overflow_dropped deadline_misses_processed batches full_batches partial_batches busy_ns exact_batches exact_events exact_busy_ns mapped_batches mapped_events mapped_busy_ns modeled_row_work anchor_minus_actual_rows modeled_minus_actual_rows new_selected_point_batches new_selected_point_events new_selected_point_busy_ns remeasured_reference_batches remeasured_reference_events remeasured_reference_busy_ns".split()


class StreamCSV:
    def __init__(self, path, bound, budget):
        self.file = path.open("x", newline="")
        self.name = path.stem
        self.bound = bound
        self.budget = budget
        self.count = 0
        self.bytes = 0
        self.fields = None

    def append(self, row):
        p.require(self.count < self.bound, "Stream row ceiling")
        buffer = io.StringIO(newline="")
        if self.fields is None:
            self.fields = list(row)
        p.require(list(row) == self.fields, "Fixed compact schema")
        w = csv.DictWriter(buffer, fieldnames=self.fields, lineterminator="\n")
        if not self.count:
            w.writeheader()
        w.writerow(row)
        payload = buffer.getvalue()
        size = len(payload.encode())
        # The first record includes the schema header, budgeted separately.
        p.require(
            size <= ROW_BYTES[self.name] + (32768 if self.count == 0 else 0),
            "Compact row byte envelope",
        )
        p.require(
            self.bytes + size <= FILE_BYTES[self.name]
            and self.budget[0] + size <= CSV_TOTAL_CAP,
            "Prewrite file/combined CSV growth",
        )
        self.file.write(payload)
        self.bytes += size
        self.budget[0] += size
        self.count += 1

    def close(self):
        self.file.close()


def decode_rows(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        p.require(
            reader.fieldnames is not None
            and len(reader.fieldnames) == len(set(reader.fieldnames)),
            "Unique CSV fields",
        )
        for raw in reader:
            p.require(None not in raw and None not in raw.values(), "CSV emitted shape")
            row = {}
            for k, v in raw.items():
                row[k] = (
                    v
                    if k in STRINGS
                    else None
                    if v == ""
                    else float(v)
                    if any(c in v for c in ".eE")
                    else int(v)
                )
                if type(row[k]) is float:
                    p.require(math.isfinite(row[k]), "Finite aggregate CSV")
            yield row


def delta(a, b):
    return None if a is None or b is None else a - b


def contrasts(context):
    p.require(len(context) == 8, "Eight current variants")
    first = context[0]
    base = {k: first[k] for k in KEYS[:7]}
    bykey = {(r["support"], r["mapping"], r["billing"]): r for r in context}
    p.require(
        len(bykey) == 8
        and all(
            {k: r[k] for k in base} == base
            and r["trace_sha256"] == first["trace_sha256"]
            for r in context
        ),
        "Common contrast context",
    )
    metrics = [
        k for k in first if k not in KEYS and k not in ("scenario_id", "trace_sha256")
    ]
    output = []

    def record(name, terms, natural, control):
        row = dict(base, contrast=name, trace_sha256=first["trace_sha256"])
        # Every row references all eight IDs and their generated/survivor denominators.
        for i, r in enumerate(context):
            for key in (
                "scenario_id",
                "generated",
                "completed",
                "overflow_dropped",
                "deadline_misses_processed",
                "batches",
                "busy_ns",
            ):
                row[f"v{i}_{key}"] = r[key]
        for metric in metrics:
            values = [r[metric] for sign, r in terms]
            row[metric + "_difference"] = (
                None
                if any(v is None for v in values)
                else delta(values[0], values[1])
                if len(values) == 2
                else delta(delta(values[0], values[1]), delta(values[2], values[3]))
            )
            row[metric + "_natural_level_change"] = (
                None
                if natural is None
                else delta(natural[0][metric], natural[1][metric])
            )
            row[metric + "_control_level_change"] = (
                None
                if control is None
                else delta(control[0][metric], control[1][metric])
            )
        output.append(row)

    for support in p.SUPPORTS:
        nn, nc, pn, pc = (
            bykey[support, m, b]
            for m, b in (
                (p.MAPPINGS[0], p.BILLINGS[0]),
                (p.MAPPINGS[0], p.BILLINGS[1]),
                (p.MAPPINGS[1], p.BILLINGS[0]),
                (p.MAPPINGS[1], p.BILLINGS[1]),
            )
        )
        record(support + "/next_natural_minus_control", [(1, nn), (-1, nc)], None, None)
        record(
            support + "/previous_natural_minus_control", [(1, pn), (-1, pc)], None, None
        )
        record(
            support + "/mapping_interaction",
            [(1, pn), (-1, pc), (-1, nn), (1, nc)],
            (pn, nn),
            (pc, nc),
        )
    for mapping in p.MAPPINGS:
        cn, cc, rn, rc = (
            bykey[s, mapping, b]
            for s, b in (
                ("coarse_reference", p.BILLINGS[0]),
                ("coarse_reference", p.BILLINGS[1]),
                ("refined_32", p.BILLINGS[0]),
                ("refined_32", p.BILLINGS[1]),
            )
        )
        record(
            mapping + "/support_interaction",
            [(1, rn), (-1, rc), (-1, cn), (1, cc)],
            (rn, cn),
            (rc, cc),
        )
    return output


def numerical_controls(context):
    def equivalent(a, b):
        omitted = {"scenario_id", "support", "mapping"}
        return {k: v for k, v in a.items() if k not in omitted} == {
            k: v for k, v in b.items() if k not in omitted
        }

    if context[0]["B"] == 1:
        for side in p.BILLINGS:
            group = [r for r in context if r["billing"] == side]
            p.require(
                all(equivalent(group[0], r) for r in group),
                "B1 support/mapping control per billing side",
            )
    if context[0]["B"] == 8:
        for side in p.BILLINGS:
            group = [
                r
                for r in context
                if r["billing"] == side and r["support"] == "refined_32"
            ]
            p.require(
                equivalent(*group)
                and all(
                    r["mapped_" + name] == 0
                    for r in group
                    for name in ("batches", "events", "busy_ns")
                ),
                "Refined B8 exact mapping control",
            )


def totals_template():
    return {
        "/".join((s, m, b)): {n: 0 for n in TOTAL_FIELDS}
        for s in p.SUPPORTS
        for m in p.MAPPINGS
        for b in p.BILLINGS
    }


def update_totals(t, row):
    q = t["/".join(row[k] for k in ("support", "mapping", "billing"))]
    for n in TOTAL_FIELDS:
        q[n] += row[n]


def update_ranges(ranges, row):
    group = ranges.setdefault(row["contrast"], {})
    for key in row:
        if not key.endswith(
            ("_difference", "_natural_level_change", "_control_level_change")
        ):
            continue
        v = row[key]
        q = group.setdefault(
            key,
            dict(
                minimum=None,
                maximum=None,
                negative=0,
                positive=0,
                zero=0,
                null=0,
                sum=0,
            ),
        )
        if v is None:
            q["null"] += 1
            continue
        q["minimum"] = v if q["minimum"] is None else min(q["minimum"], v)
        q["maximum"] = v if q["maximum"] is None else max(q["maximum"], v)
        q["negative"] += v < 0
        q["positive"] += v > 0
        q["zero"] += v == 0
        q["sum"] += v


def vector_id(v):
    return (
        p.CANDIDATES.index(v.candidate) * 96
        + (v.repetition - 1) * 32
        + p.CASES.index((v.B, v.k))
    )


def verify_csv(directory, summary, *, poll=lambda: None):
    """Ordered four-file join: one scenario histogram and eight results at a time."""

    def peekable(path):
        it = iter(decode_rows(path))
        return it, next(it, None)

    oi, occ = peekable(directory / "occupancies.csv")
    ai, ar = peekable(directory / "anchor-audit.csv")
    ci = iter(decode_rows(directory / "contrasts.csv"))
    si = iter(decode_rows(directory / "scenarios.csv"))
    source_use = {
        s: {
            k: [0] * 20
            for k in summary["vectors"]
            if s == "refined_32"
            or summary["vectors"][k]["case_class"] == "remeasured_reference"
        }
        for s in p.SUPPORTS
    }
    totals = totals_template()
    ranges = {}
    context = []
    oc = ac = cc = 0
    hashes = {
        (t["mode"], t["nominal_rate"], t["seed"]): t["trace_sha256"]
        for t in summary["traces"]
    }
    for sid, key in enumerate(p.matrix()):
        row = next(si, None)
        p.require(
            row is not None
            and row["scenario_id"] == sid
            and tuple(row[k] for k in KEYS) == key,
            "Ordered complete scenario ID/context",
        )
        b = row["B"]
        support = row["support"]
        mapping = row["mapping"]
        billing = row["billing"]
        validate_result(row, ReplayPolicy(b, row["timeout_ns"], 1024, 100000000))
        p.require(
            row["generated"] == 5000
            and row["trace_sha256"] == hashes[row["mode"], row["rate"], row["seed"]],
            "Unchanged trace identity",
        )
        sums = {
            n: 0
            for n in (
                "batches",
                "events",
                "busy_ns",
                "modeled_rows",
                "exact_batches",
                "mapped_batches",
                "exact_events",
                "mapped_events",
                "exact_busy_ns",
                "mapped_busy_ns",
                "anchor_minus_actual_rows",
                "new_selected_point_batches",
                "new_selected_point_events",
                "new_selected_point_busy_ns",
                "remeasured_reference_batches",
                "remeasured_reference_events",
                "remeasured_reference_busy_ns",
            )
        }
        byanchor = {}
        full_batches = partial_events = partial_busy = 0
        last = 0
        while occ is not None and occ["scenario_id"] == sid:
            m, k = occ["m"], occ["k"]
            oc += 1
            v = summary["vectors"][str(occ["vector_id"])]
            p.require(
                last < m <= b
                and k == anchor(b, m, mapping, support)
                and v["candidate"] == row["candidate"]
                and v["repetition"] == row["repetition"]
                and (v["B"], v["k"]) == (b, k),
                "Ordered occupancy vector join",
            )
            last = m
            full_batches += occ["batches"] if m == b else 0
            partial_events += occ["events"] if m < b else 0
            partial_busy += occ["busy_ns"] if m < b else 0
            p.require(
                occ["point_class"] == int(v["case_class"] == "new_selected_point")
                and occ["events"] == m * occ["batches"]
                and occ["exact_point"] == int(m == k)
                and occ["k_minus_m"] == k - m
                and occ["source_natural_actual_rows"]
                == occ["source_natural_model_shape_rows"]
                == k
                and occ["source_control_actual_rows"]
                == occ["source_control_model_shape_rows"]
                == b
                and occ["modeled_rows"]
                == occ["batches"] * (k if billing == "natural_anchor" else b)
                and occ["modeled_minus_actual_rows"]
                == occ["modeled_rows"] - occ["events"]
                and occ["anchor_minus_actual_rows"] == occ["batches"] * (k - m),
                "Occupancy accounting",
            )
            for n in (
                "batches",
                "events",
                "busy_ns",
                "modeled_rows",
                "anchor_minus_actual_rows",
            ):
                sums[n] += occ[n]
            for n in ("batches", "events", "busy_ns"):
                sums[("exact_" if m == k else "mapped_") + n] += occ[n]
                sums[v["case_class"] + "_" + n] += occ[n]
            p.require(
                type(occ["batches"]) is int
                and occ["batches"] >= 1
                and type(occ["busy_ns"]) is int
                and occ["busy_ns"] >= 1,
                "Positive occupancy assignments",
            )
            q = byanchor.setdefault(k, [0, 0])
            q[0] += occ["batches"]
            q[1] += occ["busy_ns"]
            occ = next(oi, None)
        p.require(
            last > 0
            and full_batches == row["full_batches"]
            and partial_events == row["partial_useful_events"]
            and partial_busy == row["partial_service_busy_ns"],
            "Every scenario full/partial occupancy group",
        )
        for k in p.SUPPORTS[support][b]:
            p.require(
                ar is not None and ar["scenario_id"] == sid and ar["k"] == k,
                "Every eligible anchor including unused, ordered ID",
            )
            ac += 1
            v = summary["vectors"][str(ar["vector_id"])]
            p.require(
                (v["candidate"], v["repetition"], v["B"], v["k"])
                == (row["candidate"], row["repetition"], b, k)
                and ar["vector_sha256"] == v["sha256"]
                and ar["pair_order_sha256"] == v["pair_order_sha256"]
                and ar["point_class"] == int(v["case_class"] == "new_selected_point"),
                "Anchor original vector/order identity",
            )
            counts = [int(x) for x in ar["assignment_counts"].split(",")]
            j = ar["dispatch_count"]
            busy = sum(
                pair[p.BILLINGS.index(billing)] * n
                for pair, n in zip(v["paired_integer_payload"], counts, strict=True)
            )
            p.require(
                len(counts) == 20
                and counts == [j // 20 + int(i < j % 20) for i in range(20)]
                and ar["cursor_wraps"] == j // 20
                and ar["cursor_remainder"] == j % 20
                and ar["unused_samples"] == sum(n == 0 for n in counts)
                and busy == ar["assigned_busy_ns"]
                and byanchor.get(k, [0, 0]) == [j, busy]
                and ar["assigned_mean_ns"] == (busy / j if j else None),
                "Independent exact duration dot product/cycle",
            )
            source_use[support][str(ar["vector_id"])] = [
                a + n
                for a, n in zip(
                    source_use[support][str(ar["vector_id"])], counts, strict=True
                )
            ]
            ar = next(ai, None)
        for n in sums:
            target = (
                "completed"
                if n == "events"
                else "modeled_row_work"
                if n == "modeled_rows"
                else n
            )
            p.require(sums[n] == row[target], "Scenario/audit conservation")
        for n, den in (
            ("batches", row["batches"]),
            ("events", row["completed"]),
            ("busy_ns", row["busy_ns"]),
        ):
            p.require(
                row["mapped_" + n + "_fraction"]
                == (row["mapped_" + n] / den if den else None),
                "Mapped denominators",
            )
        p.require(
            row["modeled_minus_actual_rows"]
            == row["modeled_row_work"] - row["completed"],
            "Signed modeled row deficit/surplus",
        )
        update_totals(totals, row)
        context.append(row)
        if len(context) == 8:
            numerical_controls(context)
            for expected in contrasts(context):
                actual = next(ci, None)
                p.require(
                    actual == expected,
                    "Eight independent contrast identities and denominators",
                )
                update_ranges(ranges, actual)
                cc += 1
            context = []
        if sid % 64 == 0:
            poll()
    p.require(
        next(si, None) is None
        and next(ci, None) is None
        and occ is None
        and ar is None,
        "No foreign trailing aggregate rows",
    )
    p.require(
        cc == p.planner()["contrasts"]
        and ac == p.planner()["anchor_row_bound"]
        and oc == summary["audit_row_counts"]["occupancies"]
        and ac == summary["audit_row_counts"]["anchors"]
        and oc <= p.planner()["occupancy_row_bound"],
        "Complete compact audit counts",
    )
    p.require(
        source_use == summary["source_use_counts"]
        and totals == summary["totals"]
        and ranges == summary["contrast_ranges"],
        "Independent streamed summaries",
    )
    return dict(
        occupancies=oc,
        anchors=ac,
        contrasts=cc,
        scenarios=p.planner()["scenarios"],
        dispatch_assignments=sum(
            sum(q) for s in source_use.values() for q in s.values()
        ),
        numerical_controls="B1 and refined B8 passed; shared anchors use identical vectors",
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
    retained = deep_size(traces)
    p.require(retained <= 16 * 2**20, "Retained trace envelope")
    vector_meta = {str(vector_id(v)): v.metadata() for v in vectors.values()}
    source_use = {
        s: {
            str(vector_id(v)): [0] * 20
            for v in vectors.values()
            if s == "refined_32" or v.case_class == "remeasured_reference"
        }
        for s in p.SUPPORTS
    }
    lookup = deep_size((vectors, vector_meta, source_use)) + 128 * 1024
    p.require(
        lookup <= 2 * 2**20, "Paired lookup envelope plus current assignment margin"
    )
    totals = totals_template()
    ranges = {}
    context = []
    budget = [0]
    streams = {
        n: StreamCSV(directory / (n + ".csv"), bound, budget)
        for n, bound in (
            ("scenarios", 6048),
            ("contrasts", 6048),
            ("occupancies", 291168),
            ("anchor-audit", 39744),
        )
    }
    try:
        for sid, key in enumerate(p.matrix()):
            mode, rate, seed, c, b, t, rep, support, mapping, billing = key
            counters["scenarios_started"] += 1
            counters["event_presentations_started"] += 5000
            counters["inflight"] = sid
            notify(counters)
            poll()
            service = Assignment(
                {k: vectors[c, rep, b, k] for k in p.SUPPORTS[support][b]},
                b,
                mapping,
                billing,
                support,
            )
            result = simulate(
                traces[mode, rate, seed],
                ReplayPolicy(b, t, 1024, 100000000),
                service,
                poll=poll,
            )
            row = dict(
                scenario_id=sid,
                **dict(zip(KEYS, key, strict=True)),
                trace_sha256=next(
                    m["trace_sha256"]
                    for m in metadata
                    if (m["mode"], m["nominal_rate"], m["seed"]) == (mode, rate, seed)
                ),
                **result,
            )
            streams["scenarios"].append(row)
            context.append(row)
            update_totals(totals, row)
            for occ in sorted(service.occupancies.values(), key=lambda x: x["m"]):
                v = vectors[c, rep, b, occ["k"]]
                streams["occupancies"].append(
                    dict(
                        scenario_id=sid,
                        **{
                            k: (
                                vector_id(v)
                                if k == "vector_id"
                                else int(v.case_class == "new_selected_point")
                                if k == "point_class"
                                else value
                            )
                            for k, value in occ.items()
                        },
                    )
                )
            for ar in service.audit():
                v = vectors[c, rep, b, ar["k"]]
                vid = str(vector_id(v))
                streams["anchor-audit"].append(
                    dict(
                        scenario_id=sid,
                        **{
                            k: (
                                int(vid)
                                if k == "vector_id"
                                else int(v.case_class == "new_selected_point")
                                if k == "point_class"
                                else value
                            )
                            for k, value in ar.items()
                        },
                    )
                )
                source_use[support][vid] = [
                    a + n
                    for a, n in zip(
                        source_use[support][vid],
                        map(int, ar["assignment_counts"].split(",")),
                        strict=True,
                    )
                ]
            if len(context) == 8:
                numerical_controls(context)
                for contrast in contrasts(context):
                    streams["contrasts"].append(contrast)
                    update_ranges(ranges, contrast)
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
        task="0048",
        identity=p.identity(),
        status="body_complete_awaiting_exit",
        source_manifest=audit["source_manifest"],
        source_audit=audit,
        vectors=vector_meta,
        source_use_counts=source_use,
        traces=metadata,
        retained_trace_bytes=retained,
        combined_paired_lookup_python_bytes_with_current_margin=lookup,
        counters=counters,
        expected=p.planner(),
        matrix_sha256=p.digest(p.matrix()),
        audit_row_counts=dict(
            occupancies=streams["occupancies"].count,
            anchors=streams["anchor-audit"].count,
        ),
        totals=totals,
        contrast_ranges=ranges,
        compact_csv_bytes=budget[0],
        memory_envelope=dict(
            current_latency_entries_max=5000,
            current_wait_entries_max=5000,
            current_batch_size_entries_max=5000,
            current_FIFO_entries_max=1024,
            current_occupancy_entries_max=128,
            current_anchor_counts_max=260,
            current_contrast_results_max=8,
            current_python_workspace_bytes=8 * 2**20,
            parsed_source_python_cap=128 * 2**20,
            source_bytes_cap=24 * 2**20,
            retained_lookup_cap=2 * 2**20,
            retained_traces_cap=16 * 2**20,
            aggregate_descriptors_python_bytes=deep_size((totals, ranges)),
            csv_total_prewrite_cap=CSV_TOTAL_CAP,
            csv_per_file_caps=FILE_BYTES,
            csv_row_byte_caps=ROW_BYTES,
            guard_cap=64 * 2**20,
            other_owned_reserved_bytes=8 * 2**20,
        ),
        contrast_definition="D=natural-control; mapping=previous D-next D; support=refined D-coarse D; all level changes carry both sides; null if any constituent is null; v0..v7 follow ordered support/mapping/billing matrix; descriptor quantiles are arithmetic sensitivities, not event-paired effects",
        point_class_codes={"0": "remeasured_reference", "1": "new_selected_point"},
        interpretation="Finite warm-window samples transported to synthetic FIFO jobs with zero-origin independent per-anchor mod20 cycles; cross-anchor phase manufactured; controls case-specific. k!=m is an unmeasured-work hypothesis, k<m may under-account rows. No bound, interpolation, monotonicity, causal isolation, production p99, confidence claim or policy selection; physical pairing does not pair diverging queue jobs/survivors.",
    )
    p.require(
        counters["scenarios_completed"] == 6048
        and counters["event_presentations_completed"] == 30240000,
        "Complete sweep",
    )
    verify_csv(directory, summary, poll=poll)
    p.durable_json(directory / "summary.json", summary, exclusive=True)
    return summary
