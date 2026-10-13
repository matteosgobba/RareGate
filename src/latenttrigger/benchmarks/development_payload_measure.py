"""Fixed raw/read/feature/joint schedule; integrity and accounting outside timers."""

import hashlib
import itertools
import json
import time

import numpy as np

from latenttrigger.benchmarks import development_payload_protocol as p
from latenttrigger.benchmarks import development_raw_planning as plan
from latenttrigger.benchmarks.development_payload_provider import parity


def block_hash(values):
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def stats(values):
    p.require(
        len(values) > 0 and all(type(v) is int and v >= 0 for v in values),
        "Nonnegative integer timer observations",
    )
    x = np.asarray(values, dtype=np.float64)
    return dict(
        count=len(values),
        minimum_ns=int(min(values)),
        maximum_ns=int(max(values)),
        mean_ns=float(x.mean()),
        population_std_ns=float(x.std(ddof=0)),
        **{
            f"p{q}_ns": float(np.quantile(x, q / 100, method="linear"))
            for q in (50, 95, 99)
        },
    )


def run(provider, golden, parameters, ledger, directory, repetition, guard):
    timer = time.get_clock_info("perf_counter")
    timer_context = dict(
        implementation=timer.implementation,
        resolution_seconds=timer.resolution,
        monotonic=timer.monotonic,
        adjustable=timer.adjustable,
        storage="integer_nanoseconds",
        recorded_before_timing=True,
    )
    p.durable_json(directory / "timer.json", timer_context, exclusive=True)
    requests = {
        (b, pos): provider.approval.ids[pos : pos + b]
        for b in plan.BATCHES
        for pos in plan.windows(b)
    }
    expected_features = {
        key: golden[provider.approval.positions(req)].tobytes()
        for key, req in requests.items()
    }
    raw_hashes = {}
    gate_checks = []
    records = []
    buffers = {}
    peak_buffers = 0
    original = dict(
        ids=block_hash(provider.approval.ids),
        golden=block_hash(golden),
        parameters=p.digest(
            dict(
                pt_mean=parameters.pt_mean,
                pt_std=parameters.pt_std,
                eta_mean=parameters.eta_mean,
                eta_std=parameters.eta_std,
                mean=parameters.aggregate_mean.tolist(),
                std=parameters.aggregate_std.tolist(),
                nmax=parameters.nmax,
            )
        ),
    )

    def operation(component, key, kind, context, timed=False):
        nonlocal peak_buffers
        b, pos = key
        req = requests[key]
        guard.check()
        provider.reset()
        ledger.start(
            component,
            b,
            raw=kind in ("read", "joint"),
            feature=kind in ("feature", "joint"),
            context=context,
        )
        success = False
        try:
            # References/window preparation, durable start and guard queries precede timer.
            raw_input = (
                buffers.get(pos)
                if kind == "feature" and component == "timing"
                else None
            )
            start_continuous = guard.clock()
            begin = time.perf_counter_ns()
            if kind == "read":
                output = provider.read(req)
            elif kind == "joint":
                output = provider.joint(req, parameters)
            else:
                p.require(raw_input is not None, "Owned feature-only buffer")
                output = provider.features(raw_input, parameters)
            elapsed = time.perf_counter_ns() - begin
            end_continuous = guard.clock()
            # No read/reconstruction is repeated to check an observation.
            if kind == "read" and key in raw_hashes:
                p.require(
                    block_hash(output) == raw_hashes[key],
                    "Raw-window immutable block equality",
                )
            elif kind != "read":
                p.require(
                    output.tobytes() == expected_features[key],
                    "Exact golden bytes after timer",
                )
            if timed:
                records.append(
                    dict(
                        **context,
                        elapsed_ns=elapsed,
                        start_continuous=start_continuous,
                        end_continuous=end_continuous,
                        continuous_minus_timer_ns=(end_continuous - start_continuous)
                        * 1e9
                        - elapsed,
                    )
                )
                with (directory / "timings.jsonl").open("a") as f:
                    f.write(json.dumps(records[-1], allow_nan=False) + "\n")
                    f.flush()
            success = True
            return output
        finally:
            ledger.finish(provider, success=success)

    def gate(phase):
        for key, req in requests.items():
            b, pos = key
            ctx = dict(phase=phase, B=b, window_position=pos, repetition=repetition)
            raw = operation("gate", key, "read", ctx)
            digest = block_hash(raw)
            if phase == "pre":
                raw_hashes[key] = digest
            else:
                p.require(digest == raw_hashes[key], "Pre/post raw block identity")
            results = []
            for index in range(2):
                provider.reset()
                ledger.start("gate", b, feature=True, context=dict(ctx, repeat=index))
                ok = False
                try:
                    guard.check()
                    f = provider.features(raw, parameters)
                    parity(f, golden, req, provider.approval)
                    results.append(f.tobytes())
                    ok = True
                finally:
                    ledger.finish(provider, success=ok)
            p.require(results[0] == results[1], "Exact repeated feature bytes")
            operation("gate", key, "joint", ctx)
            gate_checks.append(
                dict(**ctx, status="exact_bytes_passed", mismatching_bytes=0)
            )
            del raw, f, results

    gate("pre")
    rows = list(plan.schedule(repetition))
    ordinal = 0
    for b, group in itertools.groupby(rows, key=lambda x: x["B"]):
        group = list(group)
        buffers = {}
        for row in group:
            if row["scope"] == "frozen_feature_construction" and not buffers:
                for pos in plan.windows(b):
                    buffers[pos] = operation(
                        "preload",
                        (b, pos),
                        "read",
                        dict(
                            phase="preload",
                            B=b,
                            window_position=pos,
                            repetition=repetition,
                        ),
                    )
                provider.retained_bytes = sum(v.nbytes for v in buffers.values())
                peak_buffers = max(peak_buffers, provider.retained_bytes)
                provider.buffer_check(b)
            kind = {
                "selected_hdf_read": "read",
                "frozen_feature_construction": "feature",
                "selected_raw_to_features": "joint",
            }[row["scope"]]
            context = dict(row, ordinal=ordinal)
            result = operation(
                "timing", (b, row["window_position"]), kind, context, timed=True
            )
            del result
            ordinal += 1
        buffers.clear()
        provider.retained_bytes = 0
    gate("post")
    p.require(
        original["ids"] == block_hash(provider.approval.ids)
        and original["golden"] == block_hash(golden),
        "Inputs immutable pre/post",
    )
    current = p.digest(
        dict(
            pt_mean=parameters.pt_mean,
            pt_std=parameters.pt_std,
            eta_mean=parameters.eta_mean,
            eta_std=parameters.eta_std,
            mean=parameters.aggregate_mean.tolist(),
            std=parameters.aggregate_std.tolist(),
            nmax=parameters.nmax,
        )
    )
    p.require(current == original["parameters"], "Frozen parameters immutable")
    cells = []
    for b in plan.BATCHES:
        for scope in plan.SCOPES:
            subset = [
                v
                for v in records
                if v["B"] == b and v["scope"] == scope and v["phase"] == "timed"
            ]
            values = [v["elapsed_ns"] for v in subset]
            p.require(
                len(values) == 20
                and [v["window_position"] for v in subset]
                == [plan.windows(b)[i % 3] for i in range(20)],
                "Complete20call cell/order",
            )
            cells.append(
                dict(
                    repetition=repetition,
                    B=b,
                    scope=scope,
                    **stats(values),
                    mean_selected_event_ns=float(np.mean(values)) / b,
                    selected_events_per_second=b * 1e9 / float(np.mean(values)),
                    observations_ns=values,
                    timer=timer_context,
                    window_call_counts=[7, 7, 6],
                )
            )
    p.durable_json(
        directory / "aggregate.json",
        dict(
            cells=cells,
            gates=gate_checks,
            timer=timer_context,
            raw_window_block_hashes={
                f"{b}:{pos}": v for (b, pos), v in raw_hashes.items()
            },
            chronological_observations=[
                {
                    k: v
                    for k, v in row.items()
                    if k in ("ordinal", "B", "scope", "phase", "elapsed_ns")
                }
                for row in records
            ],
            peak_retained_raw_buffers_bytes=peak_buffers,
            peak_owned_array_bound_bytes=provider.peak_owned_array_bound_bytes,
            accounting=ledger.audit,
            exact_parity=True,
        ),
        exclusive=True,
    )
    p.require(len(records) == 276 and len(gate_checks) == 24, "All observations/gates")
    return ["aggregate.json", "timings.jsonl", "timer.json"]
