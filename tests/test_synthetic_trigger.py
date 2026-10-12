"""Hand timelines and independent tick oracle; no historical timing file loads."""

import copy
import csv
import hashlib
import json
import random
import sys

import pytest

from latenttrigger.simulation import protocol as p
from latenttrigger.simulation import sweep, timing
from latenttrigger.simulation.engine import Policy, Trace, describe, simulate
from latenttrigger.simulation.traces import generate


def trace(times, scores=None):
    return Trace(tuple(times), tuple(scores or [0.995] * len(times)))


def recorded(times, policy, scores=None):
    records = []
    result = simulate(
        trace(times, scores), policy, completed_event=lambda *r: records.append(r)
    )
    return result, records


def oracle(times, policy, scores):
    waiting = []
    active = []
    finish = None
    dispatch = None
    source = 0
    tick = 0
    records = []
    drops = 0
    while source < len(times) or waiting or active:
        if active and finish == tick:
            records.extend(
                (
                    i,
                    dispatch,
                    tick,
                    tuple(scores[i] > t for t in (0.9, 0.95, 0.99, 0.999)),
                )
                for i in active
            )
            active = []
        while source < len(times) and times[source] == tick:
            if len(waiting) + len(active) < policy.capacity:
                waiting.append(source)
            else:
                drops += 1
            source += 1
        if (
            not active
            and waiting
            and (
                len(waiting) >= policy.batch
                or tick - times[waiting[0]] >= policy.timeout_ns
            )
        ):
            active = waiting[: policy.batch]
            waiting = waiting[policy.batch :]
            dispatch = tick
            finish = tick + policy.service_ns
        tick += 1
        assert tick < 1000
    return records, drops


def test_b1_no_queue_and_deadline_equality():
    r, events = recorded([10, 20, 30], Policy(1, 0, 3, 5, 5))
    assert [e[:3] for e in events] == [(0, 10, 15), (1, 20, 25), (2, 30, 35)]
    assert r["dispatch_wait_ns_max"] == 0 and r["latency_ns_mean"] == 5
    assert r["deadline_misses_processed"] == 0 and r["completed_at_horizon"] == 2
    assert r["in_service_at_horizon"] == 1 and r["drain_ns"] == 5


def test_overload_capacity_includes_service():
    r, events = recorded([0, 1, 2, 3, 4], Policy(1, 0, 2, 4, 3))
    assert [e[:3] for e in events] == [(0, 0, 4), (1, 4, 8), (4, 8, 12)]
    assert r["generated"] == 5 and r["overflow_dropped"] == 2 and r["completed"] == 3
    assert r["max_outstanding"] == 2 and r["max_waiting"] == 2
    assert r["latency_ns_count"] == 3 and r["latency_ns_max"] == 8
    assert r["pending_at_horizon"] == 2 and r["busy_to_horizon_ns"] == 4


def test_completion_arrival_and_flush_tie_source_order():
    r, events = recorded([0, 0, 5, 5], Policy(2, 5, 2, 5, 10))
    assert [e[:3] for e in events] == [(0, 0, 5), (1, 0, 5), (2, 5, 10), (3, 5, 10)]
    assert r["overflow_dropped"] == 0 and r["full_batches"] == 2
    r, events = recorded([1, 6], Policy(2, 5, 2, 3, 10))
    assert [e[:3] for e in events] == [(0, 6, 9), (1, 6, 9)]
    assert r["partial_batches"] == 0


def test_expired_oldest_timeout_and_final_partial_padding():
    r, events = recorded([1, 1, 2], Policy(2, 3, 3, 10, 100))
    assert [e[:3] for e in events] == [(0, 1, 11), (1, 1, 11), (2, 11, 21)]
    assert r["partial_batches"] == 1 and r["unused_slots"] == 1
    assert r["slot_utilization"] == 0.75 and r["busy_ns"] == 20
    r, events = recorded([10], Policy(128, 100, 1, 20, 1000))
    assert events[0][:3] == (0, 110, 130)
    assert r["unused_slots"] == 127 and r["max_outstanding"] == 1


def test_processing_precedes_toy_selection_drops_excluded():
    scores = [0.9, 0.95, 0.99, 0.999, 0.9999]
    r, events = recorded([0, 0, 0, 0, 0], Policy(1, 0, 2, 1, 0), scores)
    assert len(events) == 2 and r["overflow_dropped"] == 3
    assert r["toy_0900_selected"] == 1 and r["toy_0950_selected"] == 0
    assert r["toy_0990_selected"] == 0 and r["toy_0999_selected"] == 0
    assert r["toy_0950_deadline_miss_fraction_selected"] is None
    assert r["overflow_or_late_fraction_generated"] == 1


def test_all_four_strict_ties_and_horizon_decisions():
    r, _ = recorded(
        [1, 11, 21, 31, 41], Policy(1, 0, 5, 1, 1), [0.9, 0.95, 0.99, 0.999, 0.9999]
    )
    for key, selected, horizon in zip(
        ("0900", "0950", "0990", "0999"), (4, 3, 2, 1), (3, 2, 1, 0), strict=True
    ):
        assert r[f"toy_{key}_selected"] == selected
        assert r[f"toy_{key}_rejected"] == 5 - selected
        assert r[f"toy_{key}_selected_to_horizon"] == horizon
        assert r[f"toy_{key}_deadline_misses_selected"] == 0


@pytest.mark.parametrize("seed", range(35))
def test_independent_integer_tick_oracle(seed):
    rng = random.Random(seed)
    times = sorted(rng.randrange(0, 40) for _ in range(12))
    scores = [rng.random() for _ in times]
    policy = Policy(
        rng.randint(1, 4),
        rng.randint(0, 9),
        rng.randint(1, 4),
        rng.randint(1, 7),
        rng.randint(0, 15),
    )
    r, actual = recorded(times, policy, scores)
    expected, drops = oracle(times, policy, scores)
    assert actual == expected and r["overflow_dropped"] == drops


def test_linear_quantiles_and_integer_mean():
    r = describe([0, 1, 10, 20])
    assert (
        r["mean"] == 7.75 and r["p50"] == 5.5 and r["p95"] == 18.5 and r["p99"] == 19.7
    )
    assert describe([])["p99"] is None


@pytest.mark.parametrize("times", [(1.0,), (-1,), (True,), (2, 1), (2**63,)])
def test_bad_times(times):
    with pytest.raises(ValueError):
        simulate(trace(times), Policy(1, 0, 1, 1, 1))


@pytest.mark.parametrize(
    "scores", [(float("nan"),), (float("inf"),), (-0.01,), (1.0,), (1,), ()]
)
def test_bad_scores(scores):
    with pytest.raises(ValueError):
        simulate(Trace((1,), scores), Policy(1, 0, 1, 1, 1))


@pytest.mark.parametrize(
    "args",
    [
        (0, 0, 1, 1, 1),
        (1, -1, 1, 1, 1),
        (1, 0, 0, 1, 1),
        (1, 0, 1, 0, 1),
        (1, 0, 1, 1, -1),
        (True, 0, 1, 1, 1),
    ],
)
def test_bad_policy(args):
    with pytest.raises(ValueError):
        simulate(trace([1]), Policy(*args))


def test_time_overflow_and_interrupt():
    with pytest.raises(ValueError):
        simulate(trace([2**63 - 1]), Policy(1, 0, 1, 1, 1))

    def poll():
        raise RuntimeError("runtime deadline")

    with pytest.raises(RuntimeError, match="runtime deadline"):
        simulate(trace([1]), Policy(1, 0, 1, 1, 1), poll=poll)


@pytest.mark.parametrize("mode", ["periodic", "poisson"])
def test_trace_replay_independent_streams_and_rounding(mode):
    a, info = generate(mode, 100000, 41, 31)
    b, again = generate(mode, 100000, 41, 31)
    assert a == b and info == again
    assert all(y > x for x, y in zip((0, *a.arrivals[:-1]), a.arrivals, strict=True))
    assert info["arrival_stream_key"][:-1] == info["score_stream_key"][:-1]
    assert info["arrival_stream_key"][-1] != info["score_stream_key"][-1]
    import numpy as np

    rng = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence(info["score_stream_key"]))
    )
    assert a.scores == tuple(float(x) for x in rng.random(31))
    if mode == "periodic":
        assert a.arrivals == tuple(10000 * i for i in range(1, 32))
    else:
        import math

        rng = np.random.Generator(
            np.random.PCG64(np.random.SeedSequence(info["arrival_stream_key"]))
        )
        gaps = [max(1, math.ceil(float(x))) for x in rng.exponential(10000, size=31)]
        assert a.arrivals[-1] == sum(gaps)


def test_fixed_schema_and_matrix_counts():
    assert p.load_config() == p.EXPECTED
    keys = sweep.scenario_keys()
    assert len(set(keys)) == len(keys) == 378
    assert sum(k[0] == "main" for k in keys) == 324
    assert sum(k[0] == "sensitivity" for k in keys) == 54
    assert len({k[4:7] for k in keys}) == 18
    for name, value in [
        ("seeds", [41]),
        ("deadline_ns", 1000001),
        ("source_events_per_trace", True),
        ("extra", 1),
    ]:
        altered = copy.deepcopy(p.EXPECTED)
        altered[name] = value
        with pytest.raises(ValueError):
            p.validate_config(altered)


def synthetic_timing(root):
    names = list(p.PINS)
    cells = []
    models = []
    phases = []
    joins = []
    phases.append(
        dict(
            phase="prepare",
            status="completed",
            receipt_file_sha256="prepare",
            parent_dispatch=dict(
                returncode=0, parent_error=None, child_reaped=True, deadline_passed=True
            ),
        )
    )
    for model, prefix in zip(p.CANDIDATES, ("PCA", "AE"), strict=True):
        models.append(dict(name=model, model_scientific_sha256=model + "-toy"))
        for i in (1, 2, 3):
            w = prefix + str(i)
            phases.append(
                dict(
                    phase=w,
                    status="completed",
                    receipt_file_sha256=w,
                    parent_dispatch=dict(
                        returncode=0,
                        parent_error=None,
                        child_reaped=True,
                        deadline_passed=True,
                    ),
                )
            )
            for b in p.BATCHES:
                for scope in ("reconstruction", "score_decision", "adapter_decision"):
                    maximum = (
                        26248500
                        if model == p.CANDIDATES[1]
                        and b == 128
                        and i == 2
                        and scope == "adapter_decision"
                        else 30000
                    )
                    cells.append(
                        dict(
                            worker=w,
                            model=model,
                            batch=b,
                            scope=scope,
                            count=200,
                            min_ns=1,
                            max_ns=maximum,
                            mean_ns=10000 + i,
                            population_std_ns=2,
                            p50_ns=10000,
                            p95_ns=20000,
                            p99_ns=25000,
                            throughput_events_per_second=0,
                            mean_amortized_ns_per_event=0,
                            status="completed",
                        )
                    )
        for b in p.BATCHES:
            group = dict(
                candidate=model,
                cost_batch=b,
                cost_scope="adapter_decision_prepared_features",
                cost_task="0022",
                model_scientific_sha256=model + "-toy",
                pooled_invocations=600,
                invocations_per_worker=200,
                pooled_600_invocation_mean_batch_ns=10002,
                pooled_mean_amortized_ns_per_event=10002 / b,
                throughput_from_pooled_mean_events_per_second=b * 1e9 / 10002,
            )
            for i in (1, 2, 3):
                row = next(
                    x
                    for x in cells
                    if x["worker"] == prefix + str(i)
                    and x["batch"] == b
                    and x["scope"] == "adapter_decision"
                )
                group[f"repetition_{i}_worker"] = row["worker"]
                for field in (
                    "min_ns",
                    "max_ns",
                    "mean_ns",
                    "p50_ns",
                    "p95_ns",
                    "p99_ns",
                    "population_std_ns",
                ):
                    group[f"repetition_{i}_{field}"] = row[field]
            joins.append(group)
    meta = dict(
        task="0022",
        execution_status="complete_accepted_consumed_no_retry",
        comparison_success=True,
        same_scientific_models_scalers_scores_thresholds=True,
        frozen_models=models,
        campaign=dict(
            phases=phases,
            missing_cells=0,
            counts=dict(measured_cells_completed=90),
            fresh_hardware={"synthetic": True},
            runtime_versions={"synthetic": True},
            effective_threads_by_worker={},
        ),
        receipt_lineage=dict(
            phase_receipt_sha256={x["phase"]: x["receipt_file_sha256"] for x in phases}
        ),
        timing_cells=cells,
    )
    for name, rows in ((names[0], cells), (names[2], joins)):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    (root / names[1]).write_text(json.dumps(meta))
    return {n: hashlib.sha256((root / n).read_bytes()).hexdigest() for n in names}


def test_curated_fixture_load_once_pooled_and_outlier(tmp_path):
    pins = synthetic_timing(tmp_path)
    ledger = []
    profiles, meta = timing.load(tmp_path, identities=pins, ledger=ledger)
    assert len(ledger) == 3 and sum(x["numerical_loads"] for x in ledger) == 3
    assert len(profiles) == 10 and profiles[(p.CANDIDATES[0], 1)]["service_ns"] == 10002
    assert (
        timing.service(profiles[(p.CANDIDATES[1], 128)]["workers"][1]["max_ns"])
        == 26248500
    )
    assert not meta["empirical_distribution_reproduced"]
    assert timing.service("1.00001") == 2


@pytest.mark.parametrize(
    "failure",
    [
        "missing",
        "altered",
        "symlink_file",
        "symlink_directory",
        "unaccepted",
        "duplicate",
        "bad_candidate",
        "scope",
        "counts",
        "nan",
        "lineage",
        "joined",
        "outlier",
    ],
)
def test_bad_timing_fixture(tmp_path, failure):
    pins = synthetic_timing(tmp_path)
    names = list(pins)
    if failure == "missing":
        (tmp_path / names[0]).unlink()
    elif failure == "altered":
        (tmp_path / names[0]).write_text("altered")
    elif failure == "symlink_file":
        path = tmp_path / names[0]
        renamed = path.with_name("alias.csv")
        path.rename(renamed)
        path.symlink_to(renamed)
    elif failure == "symlink_directory":
        path = tmp_path / "results/tables/final"
        target = tmp_path / "alias"
        path.rename(target)
        path.symlink_to(target)
    else:
        j = json.loads((tmp_path / names[1]).read_text())
        if failure == "unaccepted":
            j["execution_status"] = "failed"
        elif failure == "duplicate":
            j["timing_cells"].append(j["timing_cells"][0])
        elif failure == "bad_candidate":
            j["frozen_models"][0]["name"] = "unknown"
        elif failure == "scope":
            j["timing_cells"][0]["scope"] = "other"
        elif failure == "counts":
            j["campaign"]["missing_cells"] = 1
        elif failure == "nan":
            next(x for x in j["timing_cells"] if x["scope"] == "adapter_decision")[
                "mean_ns"
            ] = float("nan")
        elif failure == "lineage":
            j["receipt_lineage"]["phase_receipt_sha256"]["AE2"] = "wrong"
        elif failure in ("joined", "outlier"):
            path = tmp_path / names[2]
            raw = path.read_text()
            path.write_text(raw.replace("10002", "99999", 1))
            pins[names[2]] = hashlib.sha256(path.read_bytes()).hexdigest()
        (tmp_path / names[1]).write_text(json.dumps(j))
        pins[names[1]] = hashlib.sha256((tmp_path / names[1]).read_bytes()).hexdigest()
    with pytest.raises((ValueError, KeyError)):
        timing.load(tmp_path, identities=pins)


def test_import_boundary_has_no_model_path():
    assert "latenttrigger.simulation.engine" in sys.modules
    source = (p.ROOT / "src/latenttrigger/simulation/engine.py").read_text()
    assert "import torch" not in source and "latenttrigger.models" not in source
