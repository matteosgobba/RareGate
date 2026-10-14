"""Paired actual-row natural CPU chains with exact same-shaped references."""

import hashlib
import json
import time

import numpy as np

from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import targeted_raw_planning as plan
from latenttrigger.benchmarks import targeted_raw_protocol as p
from latenttrigger.benchmarks.development_payload_measure import stats


def block_hash(values):
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def identity(features, scores, masks, b):
    p.require(
        features.shape == (b, 8)
        and features.dtype == np.dtype("<f4")
        and np.isfinite(features).all()
        and scores.shape == (b,)
        and scores.dtype == np.dtype("<f8")
        and np.isfinite(scores).all()
        and np.all(scores >= 0)
        and masks.shape == (b, 4)
        and masks.dtype == np.dtype("bool"),
        "Canonical retained actual-row outputs",
    )
    return dict(
        features=block_hash(features),
        scores=block_hash(scores),
        decisions=block_hash(masks),
    )


def timer_context(directory):
    timer = time.get_clock_info("perf_counter")
    context = dict(
        implementation=timer.implementation,
        resolution_seconds=timer.resolution,
        monotonic=timer.monotonic,
        adjustable=timer.adjustable,
        storage="integer_ns",
        recorded_before_timing=True,
    )
    p.durable_json(directory / "timer.json", context, exclusive=True)
    return context


def run(
    chain,
    golden,
    parameters,
    ledger,
    directory,
    repetition,
    guard,
    models,
    model_identities,
    threads,
):
    timer = timer_context(directory)
    references = {}
    gates = []
    records = []
    ordinal = 0
    contexts = list(plan.gate_schedule())
    requests = {
        (r["B"], r["m"], r["window_position"], r["side"]): chain.approval.ids[
            r["window_position"] : r["window_position"] + r["actual_rows"]
        ]
        for r in contexts
    }
    chain.register(models, p.load()["channels"])
    golden_windows = {
        key: golden[chain.approval.positions(req)] for key, req in requests.items()
    }
    retained = (
        sum(v.nbytes for v in requests.values())
        + sum(v.nbytes for v in golden_windows.values())
        + golden.nbytes
        + chain.approval.ids.nbytes
    )
    p.require(retained < 2 * 2**20, "Reference/window/ID/golden envelope")
    chain.retained_bytes = retained
    expected_features = {key: block_hash(v) for key, v in golden_windows.items()}
    input_identity = dict(
        ids=block_hash(chain.approval.ids),
        golden=block_hash(golden),
        parameters=p.digest(
            dict(
                mean=parameters.aggregate_mean.tolist(),
                std=parameters.aggregate_std.tolist(),
                scalars=[
                    parameters.pt_mean,
                    parameters.pt_std,
                    parameters.eta_mean,
                    parameters.eta_std,
                    parameters.nmax,
                ],
            )
        ),
    )

    def call(
        candidate,
        key,
        component,
        phase,
        model,
        thresholds,
        context,
        *,
        reference=False,
        timed=False,
    ):
        b, m, pos, side = key
        actual, service_b = plan.mapping(b, m, side)
        req = requests[key]
        guard.check()
        chain.reset()
        chain.bind(context, model, thresholds, channels, reference=reference)
        ledger.start(component, candidate, actual, chain=not reference, context=context)
        good = False
        try:
            tick = guard.clock()
            if reference:
                feature = golden_windows[key]
                scores, masks = chain.public(
                    model, thresholds, p.load()["channels"], feature, service_b
                )
                elapsed = None
            else:
                # All lookup/intent/hash/query work precedes the pair; only the checked chain is timed.
                begin = time.perf_counter_ns()
                feature, scores, masks = chain.joint(
                    req, parameters, model, thresholds, channels
                )
                elapsed = time.perf_counter_ns() - begin
            end = guard.clock()
            out = identity(feature, scores, masks, actual)
            p.require(
                out["features"] == expected_features[key],
                "Exact approved-position frozen-feature bytes",
            )
            refkey = (candidate, key)
            if reference:
                if phase == "pre":
                    references[refkey] = out
                else:
                    p.require(
                        out == references[refkey],
                        "Exact pre/post same-shaped golden service bytes",
                    )
            else:
                p.require(
                    out == references[refkey],
                    "Exact feature/score/decision parity and repeats",
                )
            if timed:
                record = dict(
                    **context,
                    ordinal=ordinal,
                    elapsed_ns=elapsed,
                    start_continuous=tick,
                    end_continuous=end,
                    continuous_minus_timer_ns=(end - tick) * 1e9 - elapsed,
                )
                records.append(record)
                payload = json.dumps(record, allow_nan=False) + "\n"
                p.require(
                    sum(q.stat().st_size for q in directory.glob("*.jsonl"))
                    + len(payload.encode())
                    + 64 * 1024
                    <= 16 * 2**20,
                    "Combined journal ceiling before timed-record growth",
                )
                with (directory / "timings.jsonl").open("a") as f:
                    f.write(payload)
                    f.flush()
            good = True
            return out
        finally:
            ledger.finish(chain, success=good)

    channels = p.load()["channels"]
    for candidate in plan.candidates(repetition):
        model, thresholds = models[candidate]
        before = (core.parameter_hash(model), block_hash(thresholds))
        p.require(
            before == model_identities[candidate],
            "Loaded original parameter/threshold identities",
        )
        for phase in ("pre", "timing", "post"):
            if phase == "timing":
                previous_b = None
                for row in plan.schedule(repetition, candidate):
                    if (row["B"], row["m"]) != previous_b:
                        threads()
                        guard.check()
                        previous_b = (row["B"], row["m"])
                    call(
                        candidate,
                        (row["B"], row["m"], row["window_position"], row["side"]),
                        row["phase"],
                        phase,
                        model,
                        thresholds,
                        row,
                        timed=True,
                    )
                    ordinal += 1
            else:
                threads()
                guard.boundary(f"{candidate}_{phase}_gate")
                for r in contexts:
                    key = (r["B"], r["m"], r["window_position"], r["side"])
                    context = dict(
                        r, candidate=candidate, phase=phase, repetition=repetition
                    )
                    start = guard.clock()
                    reference = call(
                        candidate,
                        key,
                        "golden_reference",
                        phase,
                        model,
                        thresholds,
                        context,
                        reference=True,
                    )
                    for repeat in (0, 1):
                        call(
                            candidate,
                            key,
                            "chain_gate",
                            phase,
                            model,
                            thresholds,
                            dict(context, repeat=repeat),
                        )
                    gates.append(
                        dict(
                            **context,
                            status="exact_feature_score_decision_bytes_passed",
                            feature_score_decision_mismatches=[0, 0, 0],
                            reference_identity=reference,
                            start_continuous=start,
                            end_continuous=guard.clock(),
                        )
                    )
        p.require(
            before == (core.parameter_hash(model), block_hash(thresholds)),
            "Unchanged parameters/thresholds after candidate block",
        )
        threads()
    p.require(
        input_identity["ids"] == block_hash(chain.approval.ids)
        and input_identity["golden"] == block_hash(golden)
        and input_identity["parameters"]
        == p.digest(
            dict(
                mean=parameters.aggregate_mean.tolist(),
                std=parameters.aggregate_std.tolist(),
                scalars=[
                    parameters.pt_mean,
                    parameters.pt_std,
                    parameters.eta_mean,
                    parameters.eta_std,
                    parameters.nmax,
                ],
            )
        ),
        "Immutable membership/golden/transform numerical state",
    )
    p.require(
        len(gates) == 768 and len(records) == 2944,
        "Exact per-worker gates and schedule",
    )
    cells = []
    pairs = []
    for candidate in plan.CANDIDATES:
        for b, m in plan.CASES:
            sides = {}
            for side in plan.SIDES:
                selected = [
                    v
                    for v in records
                    if v["candidate"] == candidate
                    and v["B"] == b
                    and v["m"] == m
                    and v["side"] == side
                    and v["phase"] == "timed"
                ]
                values = [v["elapsed_ns"] for v in selected]
                p.require(
                    len(values) == 20
                    and [v["pair"] for v in selected] == list(range(20))
                    and [v["window_position"] for v in selected]
                    == [plan.windows(b)[i % 3] for i in range(20)],
                    "Complete20paired natural services",
                )
                actual, service_b = plan.mapping(b, m, side)
                sides[side] = selected
                cells.append(
                    dict(
                        candidate=candidate,
                        repetition=repetition,
                        B=b,
                        m=m,
                        side=side,
                        actual_rows=actual,
                        model_shape_rows=service_b,
                        wrapper=plan.WRAPPER,
                        case_class=plan.case_class(b, m),
                        scope=p.load()["scope"],
                        strategy="natural",
                        **stats(values),
                        mean_actual_event_ns=float(np.mean(values)) / actual,
                        hypothetical_bill_per_m_ns=float(np.mean(values)) / m,
                        actual_events_per_second=actual * 1e9 / float(np.mean(values)),
                        observations_ns=values,
                        window_call_counts=[7, 7, 6],
                        timer=timer,
                    )
                )
            for natural, control in zip(
                sides["natural_m"], sides["full_B_control"], strict=True
            ):
                p.require(
                    natural["pair_id"] == control["pair_id"]
                    and natural["window_position"] == control["window_position"]
                    and natural["order_label"] == control["order_label"],
                    "Matched pair identity",
                )
                pairs.append(
                    dict(
                        candidate=candidate,
                        repetition=repetition,
                        B=b,
                        m=m,
                        wrapper=plan.WRAPPER,
                        case_class=plan.case_class(b, m),
                        pair=natural["pair"],
                        pair_id=natural["pair_id"],
                        window_index=natural["window_index"],
                        window_position=natural["window_position"],
                        order_label=natural["order_label"],
                        natural_actual_rows=m,
                        control_actual_rows=b,
                        natural_model_shape_rows=plan.mapping(b, m, "natural_m")[1],
                        control_model_shape_rows=b,
                        natural_ns=natural["elapsed_ns"],
                        control_ns=control["elapsed_ns"],
                        difference_ns=natural["elapsed_ns"] - control["elapsed_ns"],
                        ratio=natural["elapsed_ns"] / control["elapsed_ns"],
                    )
                )
    p.require(
        len(cells) == 128 and len(pairs) == 1280 and len(chain.raw_ids_used) == 384,
        "Full per-worker cells/pairs/exact384raw rows",
    )
    p.durable_json(
        directory / "aggregate.json",
        dict(
            cells=cells,
            pairs=pairs,
            input_integrity=input_identity,
            registered_model_threshold_hashes={
                k: list(v) for k, v in model_identities.items()
            },
            unique_raw_rows=len(chain.raw_ids_used),
            gates=gates,
            exact_feature_score_decision_parity=True,
            chronology=[
                {
                    k: v[k]
                    for k in (
                        "candidate",
                        "B",
                        "m",
                        "side",
                        "actual_rows",
                        "model_shape_rows",
                        "wrapper",
                        "case_class",
                        "phase",
                        "pair",
                        "pair_id",
                        "window_position",
                        "order_label",
                        "ordinal",
                        "elapsed_ns",
                    )
                }
                for v in records
            ],
            explicit_reference_window_ID_golden_bytes=retained,
            peak_owned_array_bound_bytes=chain.peak_owned_array_bound_bytes,
            raw_window_buffers_retained=0,
            accounting=ledger.audit,
        ),
        exclusive=True,
    )
    return ["aggregate.json", "timings.jsonl", "timer.json"]
