"""Direct full natural CPU chain; same-B exact references without extra model calls."""

import hashlib
import json
import time

import numpy as np

from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import development_decision_planning as plan
from latenttrigger.benchmarks import development_decision_protocol as p
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
    requests = {
        (b, pos): chain.approval.ids[pos : pos + b] for b, pos in plan.gate_schedule()
    }
    golden_windows = {
        key: golden[chain.approval.positions(req)] for key, req in requests.items()
    }
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
        b, pos = key
        req = requests[key]
        guard.check()
        chain.reset()
        ledger.start(component, candidate, b, chain=not reference, context=context)
        good = False
        try:
            tick = guard.clock()
            if reference:
                feature = golden_windows[key]
                scores, masks = chain.public(
                    model, thresholds, p.load()["channels"], feature, b
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
            out = identity(feature, scores, masks, b)
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
                        "Exact pre/post same-B golden service bytes",
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
                with (directory / "timings.jsonl").open("a") as f:
                    f.write(json.dumps(record, allow_nan=False) + "\n")
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
                    if row["B"] != previous_b:
                        threads()
                        guard.check()
                        previous_b = row["B"]
                    call(
                        candidate,
                        (row["B"], row["window_position"]),
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
                for key in requests:
                    b, pos = key
                    context = dict(
                        candidate=candidate,
                        B=b,
                        window_position=pos,
                        phase=phase,
                        repetition=repetition,
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
        len(gates) == 48 and len(records) == 184, "Exact per-worker gates and schedule"
    )
    cells = []
    for candidate in plan.CANDIDATES:
        for b in plan.BATCHES:
            selected = [
                v
                for v in records
                if v["candidate"] == candidate and v["B"] == b and v["phase"] == "timed"
            ]
            values = [v["elapsed_ns"] for v in selected]
            p.require(
                len(values) == 20
                and [v["window_position"] for v in selected]
                == [plan.windows(b)[i % 3] for i in range(20)],
                "Complete20call natural joint cell",
            )
            cells.append(
                dict(
                    candidate=candidate,
                    repetition=repetition,
                    B=b,
                    scope="selected_raw_to_decisions",
                    strategy="natural",
                    **stats(values),
                    mean_selected_event_ns=float(np.mean(values)) / b,
                    selected_events_per_second=b * 1e9 / float(np.mean(values)),
                    observations_ns=values,
                    window_call_counts=[7, 7, 6],
                    timer=timer,
                )
            )
    p.durable_json(
        directory / "aggregate.json",
        dict(
            cells=cells,
            gates=gates,
            exact_feature_score_decision_parity=True,
            chronology=[
                {k: v[k] for k in ("candidate", "B", "phase", "ordinal", "elapsed_ns")}
                for v in records
            ],
            peak_owned_array_bound_bytes=chain.peak_owned_array_bound_bytes,
            raw_window_buffers_retained=0,
            accounting=ledger.audit,
        ),
        exclusive=True,
    )
    return ["aggregate.json", "timings.jsonl", "timer.json"]
