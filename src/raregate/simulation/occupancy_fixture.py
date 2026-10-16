"""Generated23-file timing bundle with complete producer serialization relationships."""

import csv
import io
import json
from pathlib import Path

from raregate.simulation import occupancy_protocol as p
from raregate.simulation import occupancy_source as s


def public_stats(q):
    return {k.replace("_ns", ""): v for k, v in s.stats(q).items()}


def create(root, *, newline="\n"):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    manifest = {}
    d = p.SOURCE_DIRECTORY

    def put(n, value, text=False):
        path = root / n
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            (value if text else json.dumps(value, allow_nan=False) + "\n").encode()
        )
        manifest[n] = dict(sha256=p.file_hash(path), bytes=path.stat().st_size)

    def csv_text(rows):
        out = io.StringIO(newline="")
        w = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator=newline)
        w.writeheader()
        w.writerows(rows)
        return out.getvalue()

    put(
        s.CONFIG,
        dict(
            task="0045",
            models=[
                dict(name=c, model_path="data/inert/model.json") for c in p.CANDIDATES
            ],
        ),
    )
    put(s.PROMPT, "Generated fixture prompt, no numerical access\n", True)
    identity = dict(
        task="0045",
        validation_owner="0045",
        protocol_kind="one_conditional_paired_natural_partial_raw_to_decision_CPU_session_v1",
        scope="selected_partial_raw_to_decisions",
        payload_scope="approved_background_training_1024prefix_15paired_cases_original_CPU_models",
        paired_contract_sha256=s.CONTRACT,
        packing="owned_natural_actual_rows_no_dummy",
        config_sha256=manifest[s.CONFIG]["sha256"],
        prompt_sha256=manifest[s.PROMPT]["sha256"],
    )
    counts = dict(
        timed=dict(calls=3600, rows=145920),
        warmup=dict(calls=540, rows=21888),
        chain_gates=dict(calls=2160, rows=87552),
        golden_references=dict(calls=1080, rows=43776),
        selected_reads_and_feature_constructions=dict(calls=6300, rows=255360),
        public_service=dict(calls=7380, rows=299136),
        decision_boolean_values=1196544,
    )
    plan = dict(
        task="0045",
        identity=identity,
        models=[dict(name=c, model_path="data/inert/model.json") for c in p.CANDIDATES],
        synthetic_only=False,
        validation_bootstrap=False,
        source_map={"data/raw/inert.h5": "0" * 64},
        dependencies={"fixture": "generated"},
        expected=counts,
        authorization_prompt_sha256=identity["prompt_sha256"],
    )
    put(d + "/plan.json", plan)
    timer = dict(
        implementation="generated_fixture_integer_clock",
        resolution_seconds=1e-9,
        monotonic=True,
        adjustable=False,
        storage="integer_ns",
        recorded_before_timing=True,
    )
    allcells = []
    allpairs = []
    workers = []
    for rep in (1, 2, 3):
        prefix = f"{d}/repetition{rep}/"
        records = []
        for ordinal, r in enumerate(s.schedule(rep)):
            # Unequal m=B, nonmonotone anchors and some natural-slower samples retained.
            natural = 200000 + r["m"] * 300000 + rep * 1000 + r["pair"] * 2000
            control = 250000 + r["B"] * 300000 + rep * 1200 + r["pair"] * 1500
            elapsed = (natural if r["side"] == "natural_m" else control) + (
                20000000 if r["side"] == "natural_m" and r["pair"] == 0 else 0
            )
            records.append(
                dict(
                    r,
                    ordinal=ordinal,
                    elapsed_ns=elapsed,
                    start_continuous=float(ordinal + 1),
                    end_continuous=float(ordinal + 1) + elapsed / 1e9,
                    continuous_minus_timer_ns=0.0,
                )
            )
        put(
            prefix + "timings.jsonl",
            "".join(json.dumps(r) + "\n" for r in records),
            True,
        )
        put(prefix + "timer.json", timer)
        pairs = []
        cells = []
        for c in p.CANDIDATES:
            for b, k in p.CASES:
                for i in range(20):
                    nr = next(
                        r
                        for r in records
                        if r["candidate"] == c
                        and r["B"] == b
                        and r["m"] == k
                        and r["phase"] == "timed"
                        and r["pair"] == i
                        and r["side"] == "natural_m"
                    )
                    cr = next(
                        r
                        for r in records
                        if r["pair_id"] == nr["pair_id"]
                        and r["side"] == "full_B_control"
                    )
                    pair = {n: nr[n] for n in s.PAIR_FIELDS[:9]}
                    pair.update(
                        natural_actual_rows=k,
                        control_actual_rows=b,
                        natural_service_B=nr["service_B"],
                        control_service_B=b,
                        natural_ns=nr["elapsed_ns"],
                        control_ns=cr["elapsed_ns"],
                        difference_ns=nr["elapsed_ns"] - cr["elapsed_ns"],
                        ratio=nr["elapsed_ns"] / cr["elapsed_ns"],
                    )
                    pairs.append(pair)
                for side in s.SIDES:
                    q = [
                        x["natural_ns" if side == "natural_m" else "control_ns"]
                        for x in pairs
                        if (x["candidate"], x["B"], x["m"]) == (c, b, k)
                    ]
                    actual, sb = s.service_shape(b, k, side)
                    cell = dict(
                        candidate=c,
                        repetition=rep,
                        B=b,
                        m=k,
                        side=side,
                        actual_rows=actual,
                        service_B=sb,
                        scope=identity["scope"],
                        strategy="natural",
                        **s.stats(q),
                        mean_actual_event_ns=sum(q) / 20 / actual,
                        hypothetical_bill_per_m_ns=sum(q) / 20 / k,
                        actual_events_per_second=1e9 / (sum(q) / 20 / actual),
                        observations_ns=q,
                        window_call_counts=[7, 7, 6],
                        timer=timer,
                    )
                    cells.append(cell)
        gates = [
            dict(
                B=b,
                m=k,
                window_index=wi,
                window_position=pos,
                side=side,
                actual_rows=s.service_shape(b, k, side)[0],
                service_B=s.service_shape(b, k, side)[1],
                candidate=c,
                phase=phase,
                repetition=rep,
                status="exact_feature_score_decision_bytes_passed",
                feature_score_decision_mismatches=[0, 0, 0],
                reference_identity=dict(
                    features="1" * 64, scores="2" * 64, decisions="3" * 64
                ),
            )
            for c in p.CANDIDATES
            for phase in ("pre", "post")
            for b, k in p.CASES
            for wi, pos in enumerate((0, (1024 - b) // 2, 1024 - b))
            for side in s.SIDES
        ]
        models = s.MODEL_INTEGRITY
        inputs = s.INPUT_INTEGRITY
        aggregate = dict(
            task="0045",
            identity=identity,
            cells=cells,
            pairs=pairs,
            gates=gates,
            exact_feature_score_decision_parity=True,
            unique_raw_rows=384,
            raw_window_buffers_retained=0,
            registered_model_threshold_hashes=models,
            input_integrity=inputs,
            accounting=dict(
                s.WORKER_COUNTS,
                HDF_closed=True,
                inflight=None,
                model_inflight=None,
                membership_inflight=False,
                golden_inflight=False,
                HDF_inflight=False,
            ),
            chronology=[
                {
                    k: r[k]
                    for k in "candidate B m side actual_rows service_B phase pair pair_id window_position order_label ordinal elapsed_ns".split()
                }
                for r in records
            ],
        )
        put(prefix + "aggregate.json", aggregate)
        receipt = dict(
            task="0045",
            identity=identity,
            status="body_complete_awaiting_exit",
            source_map=plan["source_map"],
            dependencies=plan["dependencies"],
            outputs={
                n: manifest[prefix + n]["sha256"]
                for n in ("aggregate.json", "timings.jsonl", "timer.json")
            },
            resources=dict(latched_error=None, owned_thread_alive=False),
            cleanup_seconds=0.001,
            model_parameter_threshold_hashes=models,
        )
        put(prefix + "receipt.json", receipt)
        workers.append(
            dict(
                phase=f"repetition{rep}",
                body_sha256=manifest[prefix + "receipt.json"]["sha256"],
                dispatch=dict(
                    returncode=0,
                    child_reaped=True,
                    parent_confirms_normal_exit=True,
                    within_deadline=True,
                    overshoot_seconds=0,
                    parent_error=None,
                    exit_observed_continuous=2.0,
                    stage_deadline_continuous=3.0,
                ),
                acceptance=dict(
                    task="0045",
                    status="parent_accepted_worker",
                    normal_exit_reaped=True,
                ),
            )
        )
        allcells += cells
        allpairs += pairs
    curatedcells = [
        {k: v for k, v in row.items() if k not in ("observations_ns", "timer")}
        | dict(window_call_counts="7/7/6")
        for row in allcells
    ]
    # Actual writer's columns are fixed; preserve both LF/CRLF roundtrips.
    curatedcells = [{k: row[k] for k in s.CELL_FIELDS} for row in curatedcells]
    put(s.CELLS, csv_text(curatedcells), True)
    put(s.PAIRS, csv_text(allpairs), True)
    pooled = []
    groups = []
    for c in p.CANDIDATES:
        for b, k in p.CASES:
            for side in s.SIDES:
                q = [
                    v
                    for row in allcells
                    if (row["candidate"], row["B"], row["m"], row["side"])
                    == (c, b, k, side)
                    for v in row["observations_ns"]
                ]
                st = public_stats(q)
                st["minimum"] = st.pop("minimum")
                st["maximum"] = st.pop("maximum")
                pooled.append(
                    dict(
                        candidate=c,
                        B=b,
                        m=k,
                        side=side,
                        actual_rows=s.service_shape(b, k, side)[0],
                        service_B=s.service_shape(b, k, side)[1],
                        **st,
                    )
                )
            for rep in (1, 2, 3):
                q = [
                    r
                    for r in allpairs
                    if (r["candidate"], r["B"], r["m"], r["repetition"])
                    == (c, b, k, rep)
                ]
                groups.append(
                    dict(
                        candidate=c,
                        B=b,
                        m=k,
                        repetition=rep,
                        difference_ns=public_stats([r["difference_ns"] for r in q]),
                        ratio=public_stats([r["ratio"] for r in q]),
                        natural_first_pairs=10,
                        control_first_pairs=10,
                    )
                )
    report = dict(
        task="0045",
        identity=identity,
        status="aggregate_report_body_complete",
        cells=180,
        timed_calls=3600,
        timed_pairs=1800,
        warmup_calls=540,
        gate_side_records=1080,
        exact_feature_score_decision_parity=True,
        pooled=pooled,
        paired_groups=groups,
        peak_owned_array_bound_bytes=0,
        explicit_reference_window_ID_golden_bytes=0,
        timer_contexts=[timer] * 3,
        interpretation="fixture",
        counts=counts,
        geometry={"historical": "inert"},
    )
    put(d + "/reporting/summary.json", report)
    prefix = d + "/reporting/"
    receipt = dict(
        task="0045",
        identity=identity,
        status="body_complete_awaiting_exit",
        source_map=plan["source_map"],
        dependencies=plan["dependencies"],
        outputs={
            "summary.json": manifest[prefix + "summary.json"]["sha256"],
            "cells.csv": manifest[s.CELLS]["sha256"],
            "pairs.csv": manifest[s.PAIRS]["sha256"],
            "joint-cost.png": "9" * 64,
            "paired-cost.png": "a" * 64,
            "chronology.png": "b" * 64,
        },
        resources=dict(latched_error=None, owned_thread_alive=False),
        cleanup_seconds=0.001,
    )
    put(prefix + "receipt.json", receipt)
    workers.append(
        dict(
            workers[0],
            phase="reporting",
            body_sha256=manifest[prefix + "receipt.json"]["sha256"],
        )
    )
    workflow = dict(
        task="0045",
        identity=identity,
        status=s.SOURCE_STATUS,
        synthetic_only=False,
        validation_bootstrap=False,
        source_map=plan["source_map"],
        dependencies=plan["dependencies"],
        workers=workers,
        overshoot_seconds=0,
        sleep_assertion=dict(
            released=True, owned_assertion_absent=True, lifecycle=dict(reaped=True)
        ),
        plan_sha256=manifest[d + "/plan.json"]["sha256"],
    )
    put(d + "/workflow.json", workflow)
    put(
        d + "/parent-acceptance.json",
        dict(
            task="0045",
            identity=identity,
            status=s.SOURCE_STATUS,
            workflow_sha256=manifest[d + "/workflow.json"]["sha256"],
            plan_sha256=manifest[d + "/plan.json"]["sha256"],
        ),
    )
    put(
        s.ATTEMPT,
        dict(
            task="0045",
            directory=d,
            plan_sha256=manifest[d + "/plan.json"]["sha256"],
            prompt_sha256=identity["prompt_sha256"],
        ),
    )
    final = {k: v for k, v in report.items() if k not in ("counts", "status")}
    final.update(
        status=s.SOURCE_STATUS,
        planned_counts=counts,
        operational_allowance_consumed=True,
        actual_counts={k: 3 * n for k, n in s.WORKER_COUNTS.items()},
        geometry={"historical": "different presentation"},
    )
    put(s.SUMMARY, final)
    p.durable_json(root / "fixture-manifest.json", manifest, exclusive=True)
    p.require(len(manifest) == 23, "Fixture closed23")
    return manifest
