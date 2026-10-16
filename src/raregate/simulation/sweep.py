"""The fixed324 main and54 constant-worker-cost scenarios, aggregates only."""

import csv
import math
from itertools import product

from raregate.simulation import protocol as p
from raregate.simulation.engine import (
    RESULT_FIELDS,
    Policy,
    integer,
    simulate,
    validate_result,
)
from raregate.simulation.timing import service
from raregate.simulation.traces import generate

TABLE = "scenarios.csv"
AGGREGATE = "aggregates.json"


def scenario_keys():
    main = [
        ("main", m, b, t, r, mode, seed, "pooled600", "mean_ns")
        for m in p.CANDIDATES
        for b, t in p.POLICIES
        for r, mode, seed in product(
            (10000, 100000, 1000000), ("periodic", "poisson"), (41, 42, 43)
        )
    ]
    stress = [
        (
            "sensitivity",
            m,
            128,
            100000,
            100000,
            "poisson",
            seed,
            ("PCA" if m == p.CANDIDATES[0] else "AE") + str(w),
            stat,
        )
        for m in p.CANDIDATES
        for seed, w, stat in product(
            (41, 42, 43), (1, 2, 3), ("mean_ns", "p99_ns", "max_ns")
        )
    ]
    return main + stress


def run(
    profiles,
    provenance,
    config,
    directory,
    *,
    poll=lambda: None,
    notify=lambda *_: None,
):
    p.validate_config(config)
    traces, metadata = {}, []
    for rate, mode, seed in product(
        config["rates_per_second"], config["arrival_modes"], config["seeds"]
    ):
        trace, info = generate(mode, rate, seed)
        traces[(rate, mode, seed)] = trace
        metadata.append(info)
    retained = sum(m["retained_python_bytes"] for m in metadata)
    p.require(
        retained <= p.LIMITS["retained_trace_bytes"], "16MiB retained trace bound"
    )
    rows = []
    counters = dict(
        curated_timing_table_metadata_loads=3,
        synthetic_unique_traces=18,
        synthetic_unique_events=90000,
        synthetic_scenarios_started=0,
        synthetic_scenarios_completed=0,
        synthetic_event_presentations_started=0,
        synthetic_event_presentations_completed=0,
        new_simulator_model_instantiations_or_forward_calls=0,
    )
    notify(counters)
    hashes = {
        (m["nominal_rate"], m["mode"], m["seed"]): m["trace_sha256"] for m in metadata
    }
    for key in scenario_keys():
        group, model, batch, timeout, rate, mode, seed, worker, stat = key
        profile = profiles[(model, batch)]
        raw = (
            profile["pooled_mean_decimal_ns"]
            if worker == "pooled600"
            else next(x[stat] for x in profile["workers"] if x["worker"] == worker)
        )
        duration = service(raw)
        policy = Policy(batch, timeout, 1024, duration, 1000000)
        counters["synthetic_scenarios_started"] += 1
        counters["synthetic_event_presentations_started"] += 5000
        notify(counters)
        result = simulate(traces[(rate, mode, seed)], policy, poll=poll)
        row = dict(
            scenario_id=f"S{len(rows) + 1:03d}",
            group=group,
            candidate=model,
            batch=batch,
            timeout_ns=timeout,
            nominal_rate=rate,
            arrival_mode=mode,
            seed=seed,
            service_worker=worker,
            service_statistic=stat,
            constant_service_decimal_ns=raw,
            service_ns=duration,
            capacity=1024,
            deadline_ns=1000000,
            trace_sha256=hashes[(rate, mode, seed)],
            **result,
        )
        rows.append(row)
        counters["synthetic_scenarios_completed"] += 1
        counters["synthetic_event_presentations_completed"] += 5000
        notify(counters)
    report = dict(
        kind="synthetic_queue_aggregates",
        config_sha256=p.digest(config),
        counters=counters,
        trace_metadata=metadata,
        retained_trace_bytes=retained,
        timing_provenance=provenance,
        rows=rows,
        quantiles="linear; rational rank positions on integer ns; displayed means/quantiles may be fractional ns",
        combined_dispatch_wait="busy-server queue wait plus idle batching wait; no artificial decomposition",
        horizon="final arrival; completion then arrivals then dispatch atH; metrics include startup and same-policy drain",
        toy_scores="Uniform[0,1); independent of arrivals and constant service; four strict decisions only after completion",
        physical_or_confirmation_claim=False,
    )
    validate_aggregates(report)
    p.durable_json(directory / AGGREGATE, report, exclusive=True)
    with (directory / TABLE).open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return report


def validate_aggregates(report):
    p.require(
        set(report)
        == {
            "kind",
            "config_sha256",
            "counters",
            "trace_metadata",
            "retained_trace_bytes",
            "timing_provenance",
            "rows",
            "quantiles",
            "combined_dispatch_wait",
            "horizon",
            "toy_scores",
            "physical_or_confirmation_claim",
        },
        "Owned aggregate schema; no event exports",
    )
    p.require(
        report["kind"] == "synthetic_queue_aggregates"
        and report["physical_or_confirmation_claim"] is False
        and report["config_sha256"] == p.digest(p.EXPECTED),
        "Aggregate identity",
    )
    rows = report["rows"]
    expected = scenario_keys()
    p.require(
        len(rows) == 378 and len(expected) == 378, "Complete fixed scenario matrix"
    )
    actual = [
        (
            r["group"],
            r["candidate"],
            r["batch"],
            r["timeout_ns"],
            r["nominal_rate"],
            r["arrival_mode"],
            r["seed"],
            r["service_worker"],
            r["service_statistic"],
        )
        for r in rows
    ]
    p.require(
        actual == expected
        and len(set(actual)) == 378
        and [r["scenario_id"] for r in rows] == [f"S{i:03d}" for i in range(1, 379)],
        "Fixed scenario coverage/order",
    )
    metadata = report["trace_metadata"]
    p.require(
        len(metadata) == 18
        and len({m["trace_sha256"] for m in metadata}) == 18
        and sum(m["count"] for m in metadata) == 90000
        and report["retained_trace_bytes"] <= 16 * 2**20,
        "One bounded trace per source key",
    )
    known = {(m["nominal_rate"], m["mode"], m["seed"]): m for m in metadata}
    p.require(
        set(known)
        == set(
            product((10000, 100000, 1000000), ("periodic", "poisson"), (41, 42, 43))
        ),
        "Unique trace memberships",
    )
    for r in rows:
        for name in (
            "batch",
            "timeout_ns",
            "nominal_rate",
            "seed",
            "service_ns",
            "capacity",
            "deadline_ns",
        ):
            integer(r[name], name)
        meta_fields = set(
            "scenario_id group candidate batch timeout_ns nominal_rate arrival_mode seed service_worker service_statistic constant_service_decimal_ns service_ns capacity deadline_ns trace_sha256".split()
        )
        p.require(
            set(r) == RESULT_FIELDS | meta_fields,
            "Scalar aggregate row schema; no per-event exports",
        )
        p.require(
            all(
                v is None or (type(v) in (int, float) and math.isfinite(v) and v >= 0)
                for k, v in r.items()
                if k not in meta_fields
            ),
            "Finite nonnegative aggregate statistics",
        )
        p.require(
            r["generated"] == 5000
            and r["capacity"] == 1024
            and r["deadline_ns"] == 1000000
            and r["trace_sha256"]
            == known[(r["nominal_rate"], r["arrival_mode"], r["seed"])]["trace_sha256"]
            and r["horizon_ns"]
            == known[(r["nominal_rate"], r["arrival_mode"], r["seed"])]["horizon_ns"]
            and r["service_ns"] == service(r["constant_service_decimal_ns"]),
            "Replay/service/source identity",
        )
        validate_result(
            r, Policy(r["batch"], r["timeout_ns"], 1024, r["service_ns"], 1000000)
        )
    c = report["counters"]
    p.require(all(type(v) is int and v >= 0 for v in c.values()), "Integer counters")
    p.require(
        c
        == dict(
            curated_timing_table_metadata_loads=3,
            synthetic_unique_traces=18,
            synthetic_unique_events=90000,
            synthetic_scenarios_started=378,
            synthetic_scenarios_completed=378,
            synthetic_event_presentations_started=1890000,
            synthetic_event_presentations_completed=1890000,
            new_simulator_model_instantiations_or_forward_calls=0,
        ),
        "Exact completed counters/no inflight scenarios",
    )
    return report
