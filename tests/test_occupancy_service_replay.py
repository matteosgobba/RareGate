"""Generated metadata only; independently reasoned queues and serialized authority."""

import json
import random

import pytest

from raregate.simulation import occupancy_admission as admission
from raregate.simulation import occupancy_protocol as p
from raregate.simulation import occupancy_source as source
from raregate.simulation.engine import Policy, Trace
from raregate.simulation.engine import simulate as original_simulate
from raregate.simulation.joint_engine import ReplayPolicy
from raregate.simulation.occupancy_engine import Assignment, anchor, simulate
from raregate.simulation.occupancy_fixture import create
from raregate.simulation.occupancy_runtime import check_access
from raregate.simulation.occupancy_sweep import contrasts


def vectors(b, natural=5, control=7):
    return {
        k: source.PairedVector(
            "pca-v1",
            1,
            b,
            k,
            tuple((natural + i, control + i) for i in range(20)),
            tuple(f"fixture/{b}/{k}/{i}" for i in range(20)),
            source.service_shape(b, k, "natural_m")[1],
        )
        for k in p.ANCHORS[b]
    }


def run(
    times, b=1, t=0, capacity=8, mapping="next_anchor", billing="natural_anchor", q=None
):
    events = []
    a = Assignment(vectors(b) if q is None else q, b, mapping, billing)
    r = simulate(
        Trace(tuple(times), tuple([0.9999] * len(times))),
        ReplayPolicy(b, t, capacity, 10),
        a,
        completed_event=lambda *r: events.append(r),
    )
    return r, events, a


@pytest.mark.parametrize("b", p.ANCHORS)
@pytest.mark.parametrize("mapping", p.MAPPINGS)
def test_exhaustive_mapping(b, mapping):
    for m in range(1, b + 1):
        expected = (
            min(k for k in p.ANCHORS[b] if k >= m)
            if mapping == "next_anchor"
            else max(k for k in p.ANCHORS[b] if k <= m)
        )
        assert anchor(b, m, mapping) == expected
    assert all(anchor(b, k, mapping) == k for k in p.ANCHORS[b])


@pytest.mark.parametrize("bad", [0, -1, 129, True, 1.0, None])
def test_wrong_occupancy(bad):
    with pytest.raises(ValueError):
        anchor(128, bad, "next_anchor")


def test_quarter_helper_argument_not_nominal_identity():
    assert source.service_shape(32, 8, "natural_m") == (8, 8)
    assert source.service_shape(128, 32, "natural_m") == (32, 32)
    assert anchor(128, 31, "next_anchor") == 32
    assert source.service_shape(128, 127, "natural_m") == (127, 128)


def test_independent_anchor_cursors_no_event_advancement_and_reset():
    a = Assignment(vectors(8), 8, "next_anchor", "natural_anchor")
    assert a.next(1) == 5 and a.next(2) == 5 and a.next(3) == 5 and a.next(1) == 6
    for _ in range(41):
        a.next(8)
    r = a.audit()
    assert a.cursors == {1: 2, 2: 1, 7: 1, 8: 41}
    assert r[-1]["cursor_wraps"] == 2 and r[-1]["assignment_counts"] == "3," + ",".join(
        ["2"] * 19
    )
    assert a.report()["dispatch_count"] == 45
    assert Assignment(vectors(8), 8, "next_anchor", "natural_anchor").next(1) == 5


def test_nonmonotone_no_clamp_and_unequal_full_sides():
    q = vectors(8, 100, 1)
    a = Assignment(q, 8, "next_anchor", "natural_anchor")
    b = Assignment(q, 8, "next_anchor", "full_control")
    assert a.next(8) == 100 and b.next(8) == 1
    q[2] = source.PairedVector(
        "pca-v1", 1, 8, 2, ((1, 999),) * 20, tuple(str(i) for i in range(20)), 8
    )
    assert Assignment(q, 8, "next_anchor", "natural_anchor").next(2) == 1


def test_hand_timeline_completion_tie_fifo_drop_tail_and_horizon():
    r, events, a = run(
        [0, 1, 2, 6],
        capacity=2,
        q={
            1: source.PairedVector(
                "pca-v1",
                1,
                1,
                1,
                ((6, 8), (2, 9), (4, 10)) + ((3, 11),) * 17,
                tuple(str(i) for i in range(20)),
                1,
            )
        },
    )
    assert [r[:3] for r in events] == [(0, 0, 6), (1, 6, 8), (3, 8, 12)]
    assert (
        r["overflow_dropped"] == 1
        and r["busy_ns"] == 12
        and r["pending_at_horizon"] == 2
    )
    assert a.cursors[1] == 3 and r["latency_ns_mean"] == 19 / 3


def test_timeout_origin_partial_drain_once_per_dispatch_and_toy_strictness():
    r, e, a = run([1, 1, 2], b=8, t=3)
    assert [v[:3] for v in e] == [(0, 4, 9), (1, 4, 9), (2, 4, 9)]
    assert r["dispatch_count"] == 1 and r["mapped_events"] == 3 and a.cursors[7] == 1
    q = vectors(1, natural=10, control=10)
    r = simulate(
        Trace((0,), (0.9,)),
        ReplayPolicy(1, 0, 1, 10),
        Assignment(q, 1, "next_anchor", "natural_anchor"),
    )
    assert r["deadline_misses_processed"] == 0 and r["toy_0900_selected"] == 0


@pytest.mark.parametrize("seed", range(25))
def test_constant_fixture_matches_original_queue_exactly(seed):
    rng = random.Random(seed)
    b = rng.choice([1, 8, 32, 128])
    t = rng.randrange(10)
    capacity = rng.randrange(1, 9)
    duration = rng.randrange(1, 20)
    tr = Trace(
        tuple(sorted(rng.randrange(50) for _ in range(30))),
        tuple(rng.random() for _ in range(30)),
    )
    q = {
        k: source.PairedVector(
            "pca-v1",
            1,
            b,
            k,
            ((duration, duration),) * 20,
            tuple(str(i) for i in range(20)),
            source.service_shape(b, k, "natural_m")[1],
        )
        for k in p.ANCHORS[b]
    }
    old = original_simulate(tr, Policy(b, t, capacity, duration, 10))
    new = simulate(
        tr,
        ReplayPolicy(b, t, capacity, 10),
        Assignment(q, b, "previous_anchor", "natural_anchor"),
    )
    assert {k: new[k] for k in old} == old


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path.resolve() / "sources"
    return root, create(root)


def mutate(bundle, n, fn):
    root, manifest = bundle
    path = root / n
    v = json.loads(path.read_text())
    fn(v)
    path.write_text(json.dumps(v) + "\n")
    manifest[n] = dict(sha256=p.file_hash(path), bytes=path.stat().st_size)


def rebind(bundle):
    root, m = bundle
    d = p.SOURCE_DIRECTORY
    for phase in ("repetition1", "repetition2", "repetition3", "reporting"):
        prefix = d + "/" + phase + "/"
        mutate(
            bundle,
            prefix + "receipt.json",
            lambda v, prefix=prefix: [
                v["outputs"].__setitem__(name, m[prefix + name]["sha256"])
                for name in v["outputs"]
                if prefix + name in m
            ],
        )
    mutate(
        bundle,
        d + "/workflow.json",
        lambda v: [
            w.__setitem__(
                "body_sha256", m[d + "/" + w["phase"] + "/receipt.json"]["sha256"]
            )
            for w in v["workers"]
        ],
    )
    mutate(
        bundle,
        d + "/parent-acceptance.json",
        lambda v: v.__setitem__("workflow_sha256", m[d + "/workflow.json"]["sha256"]),
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_complete_writer_reader_source_roundtrip(tmp_path, newline):
    root = tmp_path.resolve() / "sources"
    m = create(root, newline=newline)
    vectors, a = source.Bundle(root, m).load()
    assert (
        len(vectors) == 90
        and a["jsonl_records"] == 4140
        and a["timed_records"] == 3600
        and a["warm_records"] == 540
    )
    assert a["retained_vector_python_bytes"] < 2**20
    assert vectors["pca-v1", 1, 128, 32].natural_service_B == 32


@pytest.mark.parametrize(
    "failure",
    [
        "task",
        "owner",
        "status",
        "packing",
        "contract",
        "consumed",
        "extra_pair",
        "missing_pair",
        "wrong_pair",
        "duplicate_cell",
        "bad_gate",
        "pre_post",
        "bad_statistic",
        "wrong_shape",
        "wrong_timer",
        "receipt",
        "exit",
        "reaping",
        "release",
        "report_digest",
        "summary_shared",
        "source_map",
    ],
)
def test_semantic_source_rejection_even_rebound(bundle, failure):
    d = p.SOURCE_DIRECTORY
    agg = d + "/repetition1/aggregate.json"
    summary = source.SUMMARY
    if failure in ("task", "owner", "packing", "contract"):
        key = {
            "task": "task",
            "owner": "validation_owner",
            "packing": "packing",
            "contract": "paired_contract_sha256",
        }[failure]
        mutate(bundle, summary, lambda v: v["identity"].__setitem__(key, "foreign"))
    elif failure == "status":
        mutate(
            bundle,
            summary,
            lambda v: v.__setitem__("status", "body_complete_awaiting_exit"),
        )
    elif failure == "consumed":
        mutate(
            bundle,
            summary,
            lambda v: v.__setitem__("operational_allowance_consumed", False),
        )
    elif failure in ("exit", "reaping", "release", "source_map"):
        mutate(
            bundle,
            d + "/workflow.json",
            lambda v: (
                v["workers"][0]["dispatch"].__setitem__("returncode", 1)
                if failure == "exit"
                else v["workers"][0]["dispatch"].__setitem__("child_reaped", False)
                if failure == "reaping"
                else v["sleep_assertion"].__setitem__("released", False)
                if failure == "release"
                else v["source_map"].__setitem__("additional", "x")
            ),
        )
    elif failure == "report_digest":
        mutate(
            bundle,
            d + "/reporting/receipt.json",
            lambda v: v["outputs"].__setitem__("cells.csv", "0" * 64),
        )
    elif failure == "summary_shared":
        mutate(bundle, summary, lambda v: v["pooled"][0].__setitem__("mean", 999))
    elif failure == "wrong_timer":
        mutate(
            bundle,
            d + "/repetition1/timer.json",
            lambda v: v.__setitem__("storage", "float_ns"),
        )
    elif failure == "receipt":
        mutate(
            bundle,
            d + "/repetition1/receipt.json",
            lambda v: v.__setitem__("status", "failed"),
        )
    else:
        fn = {
            "extra_pair": lambda v: v["pairs"].append(v["pairs"][0]),
            "missing_pair": lambda v: v["pairs"].pop(),
            "wrong_pair": lambda v: v["pairs"][0].__setitem__("difference_ns", 999),
            "duplicate_cell": lambda v: v["cells"].__setitem__(1, v["cells"][0]),
            "bad_gate": lambda v: v["gates"][0].__setitem__(
                "feature_score_decision_mismatches", [1, 0, 0]
            ),
            "pre_post": lambda v: v["gates"][-1]["reference_identity"].__setitem__(
                "scores", "0" * 64
            ),
            "bad_statistic": lambda v: v["cells"][0].__setitem__("mean_ns", 999),
            "wrong_shape": lambda v: v["cells"][0].__setitem__("service_B", 128),
        }[failure]
        mutate(bundle, agg, fn)
    rebind(bundle)
    with pytest.raises((ValueError, KeyError)):
        source.Bundle(*bundle).load()


@pytest.mark.parametrize(
    "failure",
    [
        "missing",
        "foreign",
        "bytes",
        "hash",
        "symlink",
        "duplicate_json",
        "nonfinite",
        "jsonl_missing",
        "jsonl_duplicate",
        "jsonl_wrong_order",
        "jsonl_boolean",
        "csv_duplicate",
        "csv_nonfinite",
    ],
)
def test_closed_source_and_record_failures(bundle, failure):
    root, m = bundle
    name = p.SOURCE_DIRECTORY + "/repetition1/timings.jsonl"
    path = root / name
    if failure == "missing":
        m.pop(name)
    elif failure == "foreign":
        m["data/raw/inert.h5"] = dict(sha256="0" * 64, bytes=1)
    elif failure == "bytes":
        m[name]["bytes"] += 1
    elif failure == "hash":
        m[name]["sha256"] = "0" * 64
    elif failure == "symlink":
        path.unlink()
        path.symlink_to(root / source.CELLS)
    else:
        if failure in ("duplicate_json", "nonfinite"):
            name = source.SUMMARY
            path = root / name
            path.write_text(
                '{"task":"0045","task":"0045"}'
                if failure == "duplicate_json"
                else '{"x":NaN}'
            )
        elif failure.startswith("csv"):
            name = source.PAIRS
            path = root / name
            lines = path.read_text().splitlines()
            if failure == "csv_duplicate":
                lines[-1] = lines[1]
            else:
                lines[1] = lines[1].rsplit(",", 1)[0] + ",NaN"
            path.write_text("\n".join(lines) + "\n")
        else:
            lines = path.read_text().splitlines()
            if failure == "jsonl_missing":
                lines.pop()
            elif failure == "jsonl_duplicate":
                lines[-1] = lines[0]
            elif failure == "jsonl_wrong_order":
                lines[0], lines[1] = lines[1], lines[0]
            else:
                r = json.loads(lines[0])
                r["pair"] = False
                lines[0] = json.dumps(r)
            path.write_text("\n".join(lines) + "\n")
        m[name] = dict(sha256=p.file_hash(path), bytes=path.stat().st_size)
        rebind(bundle)
    with pytest.raises((ValueError, KeyError)):
        source.Bundle(root, m).load()


def test_separately_computed_numpy_serialization_reference():
    import numpy as np

    for q in (
        [1, 10, 999],
        [-200000, 100, 1000, 500000],
        list(range(20)),
        [0.3 + i * 0.03 for i in range(20)],
        [-5] * 19 + [9000000],
    ):
        st = source.stats(q)
        x = np.asarray(q, dtype=np.float64)
        for key, expected in dict(
            mean_ns=float(x.mean()),
            population_std_ns=float(x.std(ddof=0)),
            p50_ns=float(np.quantile(x, 0.5)),
            p95_ns=float(np.quantile(x, 0.95)),
            p99_ns=float(np.quantile(x, 0.99)),
        ).items():
            source.agree(st[key], expected)
    with pytest.raises(ValueError):
        source.agree(True, 1)
    with pytest.raises(ValueError):
        source.agree(float("nan"), 1.0)
    with pytest.raises(ValueError):
        source.agree(1.001, 1.0)


def test_mapping_interaction_signs_and_four_denominators():
    g = []
    for m, b, n in [
        ("next_anchor", "natural_anchor", 7),
        ("next_anchor", "full_control", 3),
        ("previous_anchor", "natural_anchor", 10),
        ("previous_anchor", "full_control", 8),
    ]:
        g.append(
            dict(
                mode="periodic",
                rate=500,
                seed=41,
                candidate="pca-v1",
                B=8,
                timeout_ns=1000000,
                repetition=1,
                mapping=m,
                billing=b,
                trace_sha256="x",
                generated=5000,
                **{
                    k: n
                    for k in __import__(
                        "raregate.simulation.occupancy_sweep", fromlist=["DIFFS"]
                    ).DIFFS
                },
            )
        )
        g[-1].update(completed=100 + n)
    rows = contrasts(g)
    assert [r["busy_ns_difference"] for r in rows] == [4, 2, -2]
    assert (
        rows[-1]["busy_ns_previous_minus_next_natural"] == 3
        and rows[-1]["busy_ns_previous_minus_next_control"] == 5
    )
    assert (
        rows[-1]["previous_natural_completed"] == 110
        and rows[-1]["next_control_completed"] == 103
    )


def test_planner_full_grid_and_bounds():
    assert p.planner() == p.load_config()["expected"]
    assert len(p.matrix()) == 3024 and p.planner()["occupancy_row_bound"] == 145584


@pytest.mark.parametrize(
    "event,args",
    [
        ("import", ("h5py",)),
        ("import", ("raregate.models.pca",)),
        ("subprocess.Popen", ()),
        ("socket.connect", ()),
        ("open", ("/tmp/model.npy", "r", 0)),
    ],
)
def test_no_physical_or_child_effects(tmp_path, event, args):
    with pytest.raises(PermissionError):
        check_access(tmp_path, tmp_path / "owned", set(), event, args)


@pytest.fixture
def software(tmp_path, monkeypatch):
    # Leaf package/source identity fixtures; actual producer/verifiers are never bypassed.
    identity = p.identity()
    monkeypatch.setattr(p, "ROOT", tmp_path.resolve())
    monkeypatch.setattr(p, "identity", lambda: dict(identity))
    monkeypatch.setattr(p, "source_map", lambda: dict(code="generated"))
    monkeypatch.setattr(p, "dependencies", lambda: dict(packages="generated"))
    monkeypatch.setattr(p, "load_config", lambda: dict(expected=p.planner()))
    directory = p.ROOT / p.VALIDATION / ("a" * 32)
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
        log.write_text("generated passed\n")
        checks[name] = dict(
            exit_code=0, log=str(log.relative_to(p.ROOT)), log_sha256=p.file_hash(log)
        )
    base = directory / ("b" * 32)
    base.mkdir()
    phases = []
    for phase in ("simulation", "reporting"):
        owned = base / phase
        owned.mkdir()
        p.durable_json(owned / "grant.json", dict(fixture=True))
        p.durable_json(owned / "out.json", dict(fixture=True))
        body = dict(
            identity=p.identity(),
            source_map=p.source_map(),
            dependencies=p.dependencies(),
            status="body_complete_awaiting_exit",
            phase=phase,
            grant_sha256=p.file_hash(owned / "grant.json"),
            resources=dict(latched_error=None, owned_thread_alive=False),
            outputs={"out.json": p.file_hash(owned / "out.json")},
        )
        p.durable_json(owned / "receipt.json", body)
        phases.append(
            dict(
                phase=phase,
                body_sha256=p.file_hash(owned / "receipt.json"),
                dispatch=dict(
                    returncode=0,
                    child_reaped=True,
                    parent_confirms_normal_exit=True,
                    within_deadline=True,
                    parent_error=None,
                    overshoot_seconds=0,
                ),
            )
        )
    native = base / "workflow.json"
    p.durable_json(
        native,
        dict(
            status=p.PARENT_STATUS,
            fixture_only=True,
            identity=p.identity(),
            source_map=p.source_map(),
            dependencies=p.dependencies(),
            sleep_assertion=dict(
                released=True, owned_assertion_absent=True, lifecycle=dict(reaped=True)
            ),
            overshoot_seconds=0,
            phases=phases,
            counters=dict(
                scenarios_started=3024,
                scenarios_completed=3024,
                event_presentations_started=15120000,
                event_presentations_completed=15120000,
            ),
        ),
    )
    record = p.emit(directory, checks, native)
    return directory, record


def test_serialized_producer_outer_freeze_claim_without_acceptance_mock(software):
    directory, record = software
    assert p.verify_acceptance(record)["status"] == p.STATUS
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
        "task",
        "owner",
        "scope",
        "config",
        "prompt",
        "source",
        "build",
        "status",
        "missing_check",
        "failed_check",
        "log",
        "receipt",
        "native",
        "permission",
    ],
)
def test_emitted_record_rejected_before_claim(software, failure):
    directory, record = software
    v = p.read(record)
    if failure in ("task", "owner", "scope", "config", "prompt"):
        key = {
            "task": "task",
            "owner": "validation_owner",
            "scope": "scope",
            "config": "config_sha256",
            "prompt": "prompt_sha256",
        }[failure]
        v["identity"][key] = "foreign"
    elif failure == "source":
        v["source_map"]["foreign"] = "x"
    elif failure == "build":
        v["dependencies"]["foreign"] = "x"
    elif failure == "status":
        v["status"] = "failed"
    elif failure == "missing_check":
        v["checks"].pop("focused")
    elif failure == "failed_check":
        v["checks"]["focused"]["exit_code"] = 1
    elif failure == "log":
        (directory / "focused.txt").write_text("altered")
    elif failure == "receipt":
        (directory / ("b" * 32) / "simulation/receipt.json").write_text("{}")
    elif failure == "native":
        v["bootstrap_workflow_sha256"] = "0" * 64
    else:
        v["execution_authorized"] = True
    p.durable_json(record, v)
    base = directory / ("c" * 32)
    base.mkdir()
    create(base / "sources")
    with pytest.raises((ValueError, KeyError)):
        admission.freeze(record, base, fixture=True)
    assert not (base / "claim.json").exists()


@pytest.mark.parametrize(
    "failure", ["plan", "freeze", "claim", "foreign_claim", "manifest", "bootstrap"]
)
def test_immutable_claim_rejection(software, failure):
    directory, record = software
    base = directory / ("c" * 32)
    base.mkdir()
    create(base / "sources")
    admission.freeze(record, base, fixture=True)
    if failure == "manifest":
        (base / "sources/fixture-manifest.json").write_text("{}")
    else:
        name = (
            "plan"
            if failure == "bootstrap"
            else "claim"
            if failure == "foreign_claim"
            else failure
        )
        v = p.read(base / (name + ".json"))
        v["validation_bootstrap"] = True if failure == "bootstrap" else "foreign"
        p.durable_json(base / (name + ".json"), v)
    with pytest.raises((ValueError, KeyError)):
        admission.verify(base)


@pytest.mark.parametrize("failure", ["token", "parent", "phase", "identity", "plan"])
def test_independent_worker_rejects_before_guard_or_source(software, failure):
    import os

    from raregate.simulation import occupancy_native as native

    directory, record = software
    base = directory / ("c" * 32)
    base.mkdir()
    create(base / "sources")
    admission.freeze(record, base, fixture=True)
    owned = base / "simulation"
    owned.mkdir()
    grant = dict(
        token="fixture-token",
        parent_pid=os.getppid(),
        phase="simulation",
        synthetic_only=True,
        plan_sha256=p.file_hash(base / "plan.json"),
        identity=p.identity(),
    )
    if failure == "token":
        grant["token"] = "foreign"
    elif failure == "parent":
        grant["parent_pid"] = -1
    elif failure == "phase":
        grant["phase"] = "reporting"
    elif failure == "identity":
        grant["identity"]["scope"] = "foreign"
    else:
        grant["plan_sha256"] = "0" * 64
    p.durable_json(owned / "grant.json", grant)
    with pytest.raises(ValueError):
        native.worker(owned, "fixture-token")
    assert (
        not (owned / "worker-entry.json").exists()
        and not (owned / "source-audit.json").exists()
    )


def test_controller_bad_serialized_record_has_no_dispatch_effect(software, monkeypatch):
    from tests.runtime_fixtures import SyntheticClock

    from raregate.simulation import occupancy_native as native

    directory, record = software
    v = p.read(record)
    v["identity"]["task"] = "foreign"
    p.durable_json(record, v)
    monkeypatch.setattr(native.rt, "ContinuousClock", SyntheticClock)
    base = directory / ("c" * 32)
    with pytest.raises(ValueError):
        native.run_native(record, fixture_directory=base)
    assert not base.exists()


def test_owned_progress_audit_updates_existing_destination(bundle, tmp_path):
    root, m = bundle
    log = tmp_path / "audit.json"
    v, a = source.Bundle(root, m, audit_path=log).load()
    assert p.read(log) == a and len(v) == 90 and len(a["opens"]) == 23


@pytest.mark.parametrize("n", [1, 8, 32, 128])
def test_full_occupancy_only_mapping_negative_control(n):
    q = vectors(n)
    r1, _, a1 = run([1] * n, b=n, t=1, capacity=n, q=q, mapping="next_anchor")
    r2, _, a2 = run([1] * n, b=n, t=1, capacity=n, q=q, mapping="previous_anchor")
    assert r1 == r2 and a1.audit() == a2.audit() and r1["mapped_events"] == 0


def test_storage_scan_owned_atomic_temp_race(tmp_path, monkeypatch):
    from pathlib import Path

    from raregate.simulation.occupancy_runtime import storage_check

    published = tmp_path / "counters.json"
    published.write_text("{}")
    temporary = tmp_path / ("counters.json." + "a" * 32 + ".tmp")
    temporary.write_text("{}")
    original_stat = Path.stat
    calls = {}

    def racing_stat(path, *args, **kwargs):
        if path == temporary:
            calls[str(path)] = calls.get(str(path), 0) + 1
            if calls[str(path)] == 1:
                raise FileNotFoundError(2, "atomic replacement before lstat")
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", racing_stat)
    assert storage_check(tmp_path) == 2


@pytest.mark.parametrize("mode", ["periodic", "poisson"])
@pytest.mark.parametrize("rate", [500, 2500, 5000])
@pytest.mark.parametrize("seed", [41, 42, 43])
def test_existing_generator_contract_independent_streams(mode, rate, seed):
    import hashlib
    import math
    import struct

    import numpy as np

    from raregate.simulation.traces import generate

    tr, meta = generate(mode, rate, seed, count=31)
    mode_id = ("periodic", "poisson").index(mode)
    times = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence([3700, seed, mode_id, rate, 0]))
    )
    scores = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence([3700, seed, mode_id, rate, 1]))
    )
    gaps = (
        [(1000000000 + rate - 1) // rate] * 31
        if mode == "periodic"
        else [max(1, math.ceil(float(v))) for v in times.exponential(1e9 / rate, 31)]
    )
    expected = []
    now = 0
    for gap in gaps:
        now += gap
        expected.append(now)
    assert tr.arrivals == tuple(expected) and tr.scores == tuple(
        float(v) for v in scores.random(31)
    )
    ah = hashlib.sha256(b"".join(struct.pack("<q", t) for t in expected)).hexdigest()
    sh = hashlib.sha256(b"".join(struct.pack("<d", t) for t in tr.scores)).hexdigest()
    assert meta["trace_sha256"] == hashlib.sha256(bytes.fromhex(ah + sh)).hexdigest()
