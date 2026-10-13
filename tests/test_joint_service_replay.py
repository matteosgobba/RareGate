"""Generated source fixtures and independent queue timelines; no real timing loads."""

import json
import random
from pathlib import Path

import pytest

from latenttrigger.simulation import joint_admission as admission
from latenttrigger.simulation import joint_protocol as p
from latenttrigger.simulation import joint_source as source
from latenttrigger.simulation.engine import Policy, Trace
from latenttrigger.simulation.engine import simulate as old_simulate
from latenttrigger.simulation.joint_engine import (
    Assignment,
    ReplayPolicy,
    simulate,
    validate_result,
)
from latenttrigger.simulation.joint_fixture import create
from latenttrigger.simulation.joint_runtime import accept_body, check_access


def trace(times):
    return Trace(tuple(times), tuple([0.9999] * len(times)))


def observed(times, q, b=1, t=0, capacity=8):
    records = []
    r = simulate(
        trace(times),
        ReplayPolicy(b, t, capacity, 10),
        tuple(q) * (20 // len(q)),
        completed_event=lambda *r: records.append(r),
    )
    return r, [r[:3] for r in records]


def test_independent_variable_hand_timeline():
    r, events = observed([0, 1, 2, 6], [6, 2, 4, 3], capacity=2)
    # At6 completion frees capacity before arrival. Event2 overflowed at2.
    assert events == [(0, 0, 6), (1, 6, 8), (3, 8, 12)]
    assert r["overflow_dropped"] == 1 and r["busy_ns"] == 12
    assert r["latency_ns_mean"] == 19 / 3 and r["pending_at_horizon"] == 2
    assert r["busy_to_horizon_ns"] == 6 and r["final_cursor"] == 3


def test_partial_multiple_events_share_batch_bill_and_oldest_timeout():
    r, events = observed([1, 1, 2], [10, 3], b=2, t=3, capacity=3)
    assert events == [(0, 1, 11), (1, 1, 11), (2, 11, 14)]
    assert r["partial_batches"] == 1 and r["partial_useful_events"] == 1
    assert r["partial_charged_slots"] == 2 and r["partial_unused_slots"] == 1
    assert r["partial_service_busy_ns"] == 3 and r["assigned_duration_sum_ns"] == 13
    assert r["dispatch_count"] == 2 and r["slot_utilization"] == 0.75
    r, events = observed([10], [20], b=128, t=100, capacity=1)
    assert events == [(0, 110, 130)] and r["partial_slot_utilization"] == 1 / 128


@pytest.mark.parametrize(
    "variant,indices",
    [
        ("cyclic", list(range(20))),
        ("reverse", list(reversed(range(20)))),
        ("rotation10", list(range(10, 20)) + list(range(10))),
    ],
)
def test_exact_cursor_cycle_reset_counts(variant, indices):
    q = tuple(range(1, 21))
    a = Assignment(q, variant)
    assert [a.next() for _ in range(43)] == [q[indices[i % 20]] for i in range(43)]
    r = a.report()
    assert (
        r["dispatch_count"] == 43
        and r["complete_cycles"] == 2
        and r["final_cursor"] == 3
    )
    assert Assignment(q, variant).next() == q[indices[0]]


def test_mean_ceiling_and_no_arrival_consumption():
    a = Assignment((1,) * 19 + (2,), "constant")
    assert a.next() == 2
    assert a.report()["constant_rounding_excess_twentieth_ns"] == 19
    r, _ = observed([1, 1, 1, 2, 3, 100], [5, 3], b=2, capacity=2)
    assert r["dispatch_count"] == 2 and r["overflow_dropped"] == 3


@pytest.mark.parametrize("seed", range(30))
def test_constant_matches_unchanged_task0037_exactly(seed):
    rng = random.Random(seed)
    times = sorted(rng.randrange(0, 40) for _ in range(15))
    scores = tuple(rng.random() for _ in times)
    tr = Trace(tuple(times), scores)
    b, t, c, s, d = [
        rng.randrange(1, 6),
        rng.randrange(10),
        rng.randrange(1, 8),
        rng.randrange(1, 8),
        rng.randrange(20),
    ]
    old = old_simulate(tr, Policy(b, t, c, s, d))
    new = simulate(tr, ReplayPolicy(b, t, c, d), (s,) * 20, "constant")
    assert {k: new[k] for k in old} == old


@pytest.mark.parametrize("seed", range(30))
def test_independent_variable_tick_oracle(seed):
    rng = random.Random(seed)
    times = sorted(rng.randrange(30) for _ in range(12))
    q = tuple(rng.randrange(1, 8) for _ in range(20))
    b, t, cap = rng.randrange(1, 5), rng.randrange(8), rng.randrange(1, 5)
    waiting = []
    active = []
    finish = 0
    tick = 0
    j = 0
    src = 0
    drops = 0
    records = []
    dispatch = 0
    while src < len(times) or waiting or active:
        if active and finish == tick:
            records.extend((i, dispatch, tick) for i in active)
            active = []
        while src < len(times) and times[src] == tick:
            if len(waiting) + len(active) < cap:
                waiting.append(src)
            else:
                drops += 1
            src += 1
        if (
            not active
            and waiting
            and (len(waiting) >= b or tick >= times[waiting[0]] + t)
        ):
            active = waiting[:b]
            waiting = waiting[b:]
            dispatch = tick
            finish = tick + q[j % 20]
            j += 1
        tick += 1
        assert tick < 500
    got = []
    r = simulate(
        trace(times),
        ReplayPolicy(b, t, cap, 10),
        q,
        completed_event=lambda *e: got.append(e[:3]),
    )
    assert (
        got == records and r["overflow_dropped"] == drops and r["dispatch_count"] == j
    )


def test_tie_order_flush_horizon_and_strict_toy_cuts():
    tr = Trace((0, 0, 5, 5), (0.9, 0.95, 0.99, 0.999))
    r = simulate(tr, ReplayPolicy(2, 5, 2, 5), (5,) * 20)
    assert r["overflow_dropped"] == 0 and r["busy_to_horizon_ns"] == 5
    assert r["completed_at_horizon"] == 2 and r["pending_at_horizon"] == 2
    assert r["toy_0900_selected"] == 3 and r["toy_0999_selected"] == 0
    assert r["deadline_misses_processed"] == 0


@pytest.mark.parametrize("bad", [0, -1, 1.0, True, 2**63])
def test_bad_duration_or_virtual_overflow(bad):
    with pytest.raises(ValueError):
        simulate(trace([1]), ReplayPolicy(1, 0, 1, 10), (bad,) * 20)


def test_virtual_finish_overflow():
    with pytest.raises(ValueError):
        simulate(trace([2**63 - 2]), ReplayPolicy(1, 0, 1, 10), (2,) * 20)


@pytest.mark.parametrize(
    "field",
    [
        "generated",
        "admitted",
        "completed",
        "pending",
        "pending_at_horizon",
        "batches",
        "full_batches",
        "modeled_slots",
        "unused_slots",
        "busy_ns",
        "dispatch_count",
        "max_outstanding",
        "on_time_completed",
        "latency_ns_count",
        "end_ns",
        "partial_useful_events",
        "partial_charged_slots",
        "partial_unused_slots",
        "busy_to_horizon_ns",
        "toy_0900_selected",
    ],
)
def test_conservation_every_invariant(field):
    policy = ReplayPolicy(2, 5, 2, 100)
    r = simulate(trace([1, 1, 2]), policy, (3,) * 20)
    r[field] += 100
    with pytest.raises(ValueError):
        validate_result(r, policy)


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / "fixture"
    pins = create(root)
    return root, pins


def mutate(bundle, name, change):
    root, pins = bundle
    path = root / name
    v = json.loads(path.read_text())
    change(v)
    path.write_text(json.dumps(v) + "\n")
    pins[name] = p.file_hash(path)


def test_generated_source_all_counts_and_order(bundle):
    root, pins = bundle
    vectors, audit = source.Bundle(root, pins).load()
    assert len(vectors) == 24 and sum(map(len, vectors.values())) == 480
    assert (
        audit["jsonl_records_parsed"] == 552 and audit["timed_records_selected"] == 480
    )
    assert (
        audit["warmup_records_excluded"] == 72
        and audit["aggregate_observation_copies_parsed"] == 480
    )
    assert (
        audit["aggregate_chronology_duration_copies_parsed"] == 552
        and len(audit["metadata_reads"]) == 19
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "failed"),
        ("task", "0041"),
        ("scope", "foreign"),
        ("one_allowance_consumed", False),
    ],
)
def test_wrong_source_status_task_scope(bundle, field, value):
    mutate(bundle, source.SUMMARY, lambda v: v.__setitem__(field, value))
    with pytest.raises(ValueError):
        source.Bundle(*bundle).load()


@pytest.mark.parametrize(
    "field,value",
    [
        ("ordinal", 1),
        ("phase", "timed"),
        ("call", 1),
        ("B", 8),
        ("candidate", "foreign"),
        ("window_position", 1),
        ("elapsed_ns", 0),
        ("elapsed_ns", 1.0),
        ("elapsed_ns", True),
    ],
)
def test_wrong_order_phase_warmup_duration(bundle, field, value):
    root, pins = bundle
    n = p.SOURCE_DIRECTORY + "/repetition1/timings.jsonl"
    path = root / n
    rows = [json.loads(v) for v in path.read_text().splitlines()]
    rows[0][field] = value
    path.write_text("".join(json.dumps(v) + "\n" for v in rows))
    pins[n] = p.file_hash(path)
    # Bind changed bytes through receipt to exercise semantic validation.
    rn = p.SOURCE_DIRECTORY + "/repetition1/receipt.json"
    mutate(bundle, rn, lambda v: v["outputs"].__setitem__("timings.jsonl", pins[n]))
    wn = p.SOURCE_DIRECTORY + "/workflow.json"
    mutate(bundle, wn, lambda v: v["workers"][0].__setitem__("body_sha256", pins[rn]))
    mutate(
        bundle,
        p.SOURCE_DIRECTORY + "/parent-acceptance.json",
        lambda v: v.__setitem__("workflow_sha256", pins[wn]),
    )
    mutate(
        bundle,
        source.SUMMARY,
        lambda v: (
            v["provenance"].__setitem__("workflow_sha256", pins[wn]),
            v["provenance"].__setitem__(
                "parent_acceptance_sha256",
                pins[p.SOURCE_DIRECTORY + "/parent-acceptance.json"],
            ),
        ),
    )
    with pytest.raises(ValueError):
        source.Bundle(*bundle).load()


@pytest.mark.parametrize(
    "method", ["missing", "altered", "symlink", "foreign", "oversized"]
)
def test_missing_altered_unsafe_oversized_sources(bundle, method):
    root, pins = bundle
    n = source.CELLS
    path = root / n
    if method == "missing":
        path.unlink()
    elif method == "altered":
        path.write_text("altered")
    elif method == "symlink":
        path.rename(path.with_suffix(".original"))
        path.symlink_to(path.with_suffix(".original"))
    elif method == "foreign":
        pins["../raw.h5"] = "0" * 64
    else:
        path.write_bytes(b" " * (8 * 2**20 + 1))
    with pytest.raises(ValueError):
        source.Bundle(*bundle)


@pytest.mark.parametrize(
    "field", ["child_reaped", "parent_confirms_normal_exit", "within_deadline"]
)
def test_original_worker_exit_guards(bundle, field):
    wn = p.SOURCE_DIRECTORY + "/workflow.json"
    mutate(bundle, wn, lambda v: v["workers"][0]["dispatch"].__setitem__(field, False))
    with pytest.raises(ValueError):
        source.Bundle(*bundle).load()


def test_embedded_forbidden_paths_inert(bundle, monkeypatch):
    root, pins = bundle
    mutate(
        bundle,
        source.SUMMARY,
        lambda v: v.__setitem__(
            "metadata", dict(raw="/forbidden/source.h5", model="/forbidden/model.pt")
        ),
    )
    original = Path.open

    def protected(path, *args, **kwargs):
        assert not str(path).startswith("/forbidden/")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", protected)
    source.Bundle(*bundle).load()


@pytest.mark.parametrize(
    "event,args",
    [
        ("subprocess.Popen", ()),
        ("socket.connect", ()),
        ("import", ("torch",)),
        ("open", ("/source/file.h5", "r", 0)),
        ("open", ("/repo/data/raw.npy", "r", 0)),
    ],
)
def test_numerical_worker_boundary(event, args):
    with pytest.raises(PermissionError):
        check_access(Path("/repo"), Path("/repo/results/owned"), set(), event, args)


def test_fixed_matrix_pairings():
    rows = p.matrix()
    assert len(rows) == 1764
    assert sum(r[-1] == "cyclic" for r in rows) == 756
    assert sum(r[-1] in ("reverse", "rotation10") for r in rows) == 252
    for r in rows:
        reference = (*r[:-1], "constant" if r[-1] == "cyclic" else "cyclic")
        assert reference in rows


def test_failed_admission_blocks_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "ROOT", tmp_path)
    base = tmp_path / p.NAMESPACE / ("0" * 32)
    base.mkdir(parents=True)
    spy = []
    monkeypatch.setattr(
        p, "verify_acceptance", lambda _: (_ for _ in ()).throw(ValueError("bad"))
    )
    with pytest.raises(ValueError):
        plan = admission.freeze(tmp_path / "record", base)
        spy.append(plan)
    assert spy == [] and not (base / "claim.json").exists()


def rebind(bundle):
    root, pins = bundle
    d = p.SOURCE_DIRECTORY
    for rep in (1, 2, 3):
        n = f"{d}/repetition{rep}/receipt.json"
        mutate(
            bundle,
            n,
            lambda v, rep=rep: v.__setitem__(
                "outputs",
                {
                    f: pins[f"{d}/repetition{rep}/{f}"]
                    for f in ("aggregate.json", "timings.jsonl", "timer.json")
                },
            ),
        )
    mutate(
        bundle,
        d + "/workflow.json",
        lambda v: [
            w.__setitem__("body_sha256", pins[f"{d}/repetition{i + 1}/receipt.json"])
            for i, w in enumerate(v["workers"][:3])
        ],
    )
    mutate(
        bundle,
        d + "/parent-acceptance.json",
        lambda v: v.__setitem__("workflow_sha256", pins[d + "/workflow.json"]),
    )
    mutate(
        bundle,
        source.SUMMARY,
        lambda v: (
            v["provenance"].__setitem__("workflow_sha256", pins[d + "/workflow.json"]),
            v["provenance"].__setitem__(
                "parent_acceptance_sha256", pins[d + "/parent-acceptance.json"]
            ),
        ),
    )


@pytest.mark.parametrize(
    "failure",
    [
        "duplicate_cell",
        "missing_cell",
        "wrong_observations",
        "bad_statistic",
        "bad_gate",
        "missing_record",
        "duplicate_record",
        "wrong_timer",
    ],
)
def test_rebound_source_semantic_defects(bundle, failure):
    root, pins = bundle
    d = p.SOURCE_DIRECTORY
    n = d + "/repetition1/aggregate.json"
    changes = {
        "duplicate_cell": lambda v: v["cells"].__setitem__(1, v["cells"][0]),
        "missing_cell": lambda v: v["cells"].pop(),
        "wrong_observations": lambda v: v["cells"][0]["observations_ns"].__setitem__(
            0, 999
        ),
        "bad_statistic": lambda v: v["cells"][0].__setitem__("mean_ns", 999),
        "bad_gate": lambda v: v["gates"][0].__setitem__(
            "feature_score_decision_mismatches", [1, 0, 0]
        ),
    }
    if failure in changes:
        mutate(bundle, n, changes[failure])
    elif failure == "wrong_timer":
        mutate(
            bundle,
            d + "/repetition1/timer.json",
            lambda v: v.__setitem__("storage", "float"),
        )
    else:
        n = d + "/repetition1/timings.jsonl"
        path = root / n
        rows = path.read_text().splitlines()
        if failure == "missing_record":
            rows.pop()
        else:
            rows.append(rows[0])
        path.write_text("\n".join(rows) + "\n")
        pins[n] = p.file_hash(path)
    rebind(bundle)
    with pytest.raises((ValueError, KeyError)):
        source.Bundle(*bundle).load()


@pytest.fixture
def software(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "ROOT", tmp_path)
    monkeypatch.setattr(p, "verify_lifecycle", lambda _: None)
    monkeypatch.setattr(p, "source_map", lambda: dict(code="hash"))
    monkeypatch.setattr(p, "dependencies", lambda: dict(packages={}))
    monkeypatch.setattr(
        p,
        "identity",
        lambda: dict(task="0044", kind="deterministic_joint_service_replay"),
    )
    monkeypatch.setattr(p, "load_config", lambda: dict(expected=dict(scenarios=1764)))
    directory = tmp_path / p.VALIDATION / ("a" * 32)
    directory.mkdir(parents=True)
    checks = {}
    for name in (
        "focused",
        "full",
        "portable",
        "lint",
        "format",
        "dependencies",
        "native_synthetic",
    ):
        log = directory / (name + ".txt")
        log.write_text("passed\n")
        checks[name] = dict(
            exit_code=0, log=str(log.relative_to(tmp_path)), log_sha256=p.file_hash(log)
        )
    native = directory / ("b" * 32) / "workflow.json"
    native.parent.mkdir()
    p.durable_json(
        native,
        dict(
            status=p.PARENT_STATUS,
            fixture_only=True,
            sleep_assertion=dict(released=True),
            source_map=p.source_map(),
            dependencies=p.dependencies(),
        ),
    )
    record = p.emit(directory, checks, native)
    return directory, record


def test_actual_producer_serialized_outer_freeze_claim(software):
    directory, record = software
    accepted = p.verify_acceptance(record)
    assert accepted["status"] == p.STATUS
    base = directory / ("c" * 32)
    base.mkdir()
    create(base / "sources")
    admission.freeze(record, base, fixture=True)
    assert admission.verify(base)["software_record_sha256"] == p.file_hash(record)
    with pytest.raises(FileExistsError):
        admission.freeze(record, base, fixture=True)


@pytest.mark.parametrize(
    "failure",
    [
        "wrong_status",
        "wrong_task",
        "extra_field",
        "permission_flag",
        "log_hash",
        "native_hash",
        "native_status",
    ],
)
def test_serialized_record_rejected_before_freeze(software, failure):
    directory, record = software
    value = p.read(record)
    if failure == "wrong_status":
        value["status"] = "software_accepted_synthetic_simulator_only"
    elif failure == "wrong_task":
        value["identity"]["task"] = "0043"
    elif failure == "extra_field":
        value["extra"] = True
    elif failure == "permission_flag":
        value["execution_authorized"] = True
    elif failure == "log_hash":
        value["checks"]["focused"]["log_sha256"] = "0" * 64
    elif failure == "native_hash":
        value["bootstrap_workflow_sha256"] = "0" * 64
    else:
        path = p.ROOT / value["bootstrap_workflow"]
        v = p.read(path)
        v["status"] = "failed"
        p.durable_json(path, v)
        value["bootstrap_workflow_sha256"] = p.file_hash(path)
    p.durable_json(record, value)
    base = directory / ("c" * 32)
    base.mkdir()
    spy = []
    with pytest.raises(ValueError):
        plan = admission.freeze(record, base, fixture=True)
        spy.append(plan)
    assert spy == [] and not (base / "claim.json").exists()


@pytest.mark.parametrize(
    "failure",
    [
        "absent_freeze",
        "changed_freeze",
        "absent_claim",
        "changed_claim",
        "changed_plan",
        "changed_source",
    ],
)
def test_frozen_bytes_rechecked_before_executor(software, failure):
    directory, record = software
    base = directory / ("c" * 32)
    base.mkdir()
    create(base / "sources")
    admission.freeze(record, base, fixture=True)
    if failure == "changed_source":
        (base / "sources" / source.CELLS).write_text("changed")
    else:
        path = base / (
            "plan.json"
            if failure == "changed_plan"
            else "claim.json"
            if "claim" in failure
            else "freeze.json"
        )
        if failure.startswith("absent"):
            path.unlink()
        else:
            p.durable_json(path, dict(task="foreign"))
    called = []
    with pytest.raises((ValueError, KeyError, FileNotFoundError)):
        admission.verify(base)
        called.append(True)
    assert called == []


def test_interrupted_freeze_publication_never_claims(software, monkeypatch):
    directory, record = software
    base = directory / ("c" * 32)
    base.mkdir()
    create(base / "sources")
    original = p.durable_json

    def broken(path, value, **kwargs):
        if path.name == "freeze.json":
            raise OSError("fixture interruption")
        return original(path, value, **kwargs)

    monkeypatch.setattr(p, "durable_json", broken)
    with pytest.raises(OSError):
        admission.freeze(record, base, fixture=True)
    assert (base / "plan.json").exists() and not (base / "claim.json").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("returncode", 1),
        ("child_reaped", False),
        ("within_deadline", False),
        ("parent_confirms_normal_exit", False),
        ("parent_error", "late"),
    ],
)
def test_body_complete_cannot_replace_exit_acceptance(
    tmp_path, monkeypatch, field, value
):
    monkeypatch.setattr(p, "identity", lambda: {"task": "0044"})
    monkeypatch.setattr(p, "source_map", lambda: {})
    monkeypatch.setattr(p, "dependencies", lambda: {})
    p.durable_json(tmp_path / "grant.json", {})
    outputs = {
        n: "0" * 64
        for n in ("outcomes.png", "latency.png", "sensitivity.png", "reporting.json")
    }
    grant = dict(phase="reporting", source_map={}, dependencies={})
    body = dict(
        status="body_complete_awaiting_exit",
        phase="reporting",
        identity=p.identity(),
        source_map={},
        dependencies={},
        grant_sha256=p.file_hash(tmp_path / "grant.json"),
        outputs=outputs,
        resources={},
    )
    dispatch = dict(
        returncode=0,
        child_reaped=True,
        within_deadline=True,
        parent_confirms_normal_exit=True,
        parent_error=None,
    )
    dispatch[field] = value
    with pytest.raises(ValueError):
        accept_body(body, dispatch, grant, tmp_path, lambda: 0, 1)


def test_final_source_requires_completed_admission_roundtrip(software):
    directory, record = software
    base = p.ROOT / p.NAMESPACE / ("d" * 32)
    base.mkdir(parents=True)
    with pytest.raises(ValueError):
        admission.freeze(record, base)
    assert not (base / "plan.json").exists() and not (base / "claim.json").exists()


def test_actual_controller_stops_before_guard_assertion_worker(software, monkeypatch):
    from latenttrigger.simulation import joint_native as native

    directory, record = software
    monkeypatch.setattr(native, "NAMESPACE", p.ROOT / p.NAMESPACE)
    called = []
    monkeypatch.setattr(
        native.rt, "IdleAssertion", lambda *a: called.append("assertion")
    )
    monkeypatch.setattr(
        native.rt, "SimulationGuard", lambda *a, **k: called.append("guard")
    )
    monkeypatch.setattr(
        native.rt, "supervise", lambda *a, **k: called.append("dispatch")
    )
    base, w = native.run_native(record)
    assert w["status"] == "failed_synthetic_preserved" and called == []
    assert not (base / "claim.json").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("returncode", 1),
        ("child_reaped", False),
        ("within_deadline", False),
        ("parent_confirms_normal_exit", False),
        ("parent_error", "bad"),
    ],
)
def test_outer_native_receipt_verifier_rejects_lifecycle(
    tmp_path, monkeypatch, field, value
):
    monkeypatch.setattr(p, "identity", lambda: {"task": "0044"})
    monkeypatch.setattr(p, "source_map", lambda: {})
    monkeypatch.setattr(p, "dependencies", lambda: {})
    w = dict(
        status=p.PARENT_STATUS,
        fixture_only=True,
        identity=p.identity(),
        source_map={},
        dependencies={},
        sleep_assertion=dict(
            released=True, owned_assertion_absent=True, lifecycle=dict(reaped=True)
        ),
        overshoot_seconds=0,
        counters=dict(
            scenarios_started=1764,
            scenarios_completed=1764,
            event_presentations_started=8820000,
            event_presentations_completed=8820000,
        ),
        phases=[
            dict(
                phase="simulation",
                dispatch=dict(
                    returncode=0,
                    child_reaped=True,
                    parent_confirms_normal_exit=True,
                    within_deadline=True,
                    parent_error=None,
                    overshoot_seconds=0,
                ),
            ),
            dict(phase="reporting"),
        ],
    )
    w["phases"][0]["dispatch"][field] = value
    p.durable_json(tmp_path / "workflow.json", w)
    with pytest.raises(ValueError):
        p.verify_lifecycle(tmp_path / "workflow.json")


def test_exact_original_slash_csv_serialization(bundle):
    import csv

    root, pins = bundle
    with (root / source.CELLS).open() as f:
        rows = list(csv.DictReader(f))
    assert all(r["window_call_counts"] == "7/7/6" for r in rows)
    rows[0]["window_call_counts"] = "[7, 7, 6]"
    with (root / source.CELLS).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    pins[source.CELLS] = p.file_hash(root / source.CELLS)
    mutate(
        bundle,
        source.SUMMARY,
        lambda v: v["results"].__setitem__("table_sha256", pins[source.CELLS]),
    )
    with pytest.raises(ValueError):
        source.Bundle(*bundle).load()


def test_historical_source_map_only_original_entries(bundle):
    root, pins = bundle
    d = p.SOURCE_DIRECTORY
    original = root / "src/historical.py"
    original.parent.mkdir()
    original.write_text("historical_source = True\n")
    sm = {"src/historical.py": p.file_hash(original)}
    for n in (
        d + "/plan.json",
        d + "/workflow.json",
        *(f"{d}/repetition{r}/receipt.json" for r in (1, 2, 3)),
    ):
        mutate(bundle, n, lambda v: v.__setitem__("source_map", sm))
    mutate(
        bundle,
        d + "/workflow.json",
        lambda v: v.__setitem__("plan_sha256", pins[d + "/plan.json"]),
    )
    mutate(
        bundle,
        d + "/parent-acceptance.json",
        lambda v: v.__setitem__("plan_sha256", pins[d + "/plan.json"]),
    )
    mutate(
        bundle,
        source.SUMMARY,
        lambda v: (
            v["validation"].__setitem__("source_map_canonical_sha256", p.digest(sm)),
            v["provenance"].__setitem__(
                "execution_plan_sha256", pins[d + "/plan.json"]
            ),
        ),
    )
    rebind(bundle)
    (root / "src/new_replay.py").write_text("new = True\n")
    source.Bundle(*bundle).load()
    original.write_text("changed = True\n")
    with pytest.raises(ValueError):
        source.Bundle(*bundle).load()


def test_ambiguous_jsonl_keys_rejected(bundle):
    root, pins = bundle
    n = p.SOURCE_DIRECTORY + "/repetition1/timings.jsonl"
    path = root / n
    rows = path.read_text().splitlines()
    rows[0] = rows[0].replace("{", '{"elapsed_ns": 0, ', 1)
    path.write_text("\n".join(rows) + "\n")
    pins[n] = p.file_hash(path)
    rebind(bundle)
    with pytest.raises(ValueError):
        source.Bundle(*bundle).load()
