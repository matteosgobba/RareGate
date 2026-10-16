"""Generated metadata only; independently reasoned queues and serialized authority."""

import json
import random

import pytest

from raregate.simulation import refined_service_admission as admission
from raregate.simulation import refined_service_protocol as p
from raregate.simulation import refined_service_source as source
from raregate.simulation.engine import Policy, Trace
from raregate.simulation.engine import simulate as original_simulate
from raregate.simulation.joint_engine import ReplayPolicy
from raregate.simulation.refined_service_engine import (
    Assignment as ActualAssignment,
)
from raregate.simulation.refined_service_engine import anchor as actual_anchor
from raregate.simulation.refined_service_engine import simulate
from raregate.simulation.refined_service_fixture import create
from raregate.simulation.refined_service_runtime import check_access
from raregate.simulation.refined_service_sweep import contrasts


def Assignment(v, b, mapping, billing):
    return ActualAssignment(v, b, mapping, billing, "coarse_reference")


def anchor(b, m, mapping):
    return actual_anchor(b, m, mapping, "coarse_reference")


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
            p.point_class(b, k),
        )
        for k in p.COARSE[b]
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


@pytest.mark.parametrize("b", p.COARSE)
@pytest.mark.parametrize("mapping", p.MAPPINGS)
def test_exhaustive_mapping(b, mapping):
    for m in range(1, b + 1):
        expected = (
            min(k for k in p.COARSE[b] if k >= m)
            if mapping == "next_anchor"
            else max(k for k in p.COARSE[b] if k <= m)
        )
        assert anchor(b, m, mapping) == expected
    assert all(anchor(b, k, mapping) == k for k in p.COARSE[b])


@pytest.mark.parametrize("bad", [0, -1, 129, True, 1.0, None])
def test_wrong_occupancy(bad):
    with pytest.raises(ValueError):
        anchor(128, bad, "next_anchor")


def test_quarter_helper_argument_not_nominal_identity():
    assert source.service_shape(32, 8, "natural_m") == (8, 8)
    assert source.service_shape(128, 32, "natural_m") == (32, 32)
    assert anchor(128, 31, "next_anchor") == 32
    assert source.service_shape(128, 127, "natural_m") == (127, 127)


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
            p.point_class(b, k),
        )
        for k in p.COARSE[b]
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
        len(vectors) == 192
        and a["jsonl_records"] == 8832
        and a["timed_records"] == 7680
        and a["warm_records"] == 1152
    )
    assert a["retained_vector_python_bytes"] < 2 * 2**20
    assert vectors["pca-v1", 1, 128, 32].natural_model_shape_rows == 32


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
            "wrong_shape": lambda v: v["cells"][0].__setitem__("model_shape_rows", 128),
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
                '{"task":"0047","task":"0047"}'
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


def test_all_eight_contrast_signs_and_denominators():
    context = []
    for sid, (support, mapping, billing) in enumerate(
        (s, m, b) for s in p.SUPPORTS for m in p.MAPPINGS for b in p.BILLINGS
    ):
        context.append(
            dict(
                scenario_id=sid,
                mode="periodic",
                rate=500,
                seed=41,
                candidate="pca-v1",
                B=8,
                timeout_ns=1000000,
                repetition=1,
                support=support,
                mapping=mapping,
                billing=billing,
                trace_sha256="x",
                generated=5000,
                completed=100 + sid,
                overflow_dropped=4,
                deadline_misses_processed=3,
                batches=2,
                busy_ns=[7, 3, 10, 8, 9, 4, 12, 5][sid],
                nullable=None,
            )
        )
    rows = contrasts(context)
    assert [r["busy_ns_difference"] for r in rows] == [4, 2, -2, 5, 7, 2, 1, 5]
    assert rows[-1]["busy_ns_natural_level_change"] == 2
    assert rows[-1]["busy_ns_control_level_change"] == -3
    assert all(
        r["nullable_difference"] is None
        and r["v7_completed"] == 107
        and r["v0_generated"] == 5000
        for r in rows
    )


def test_planner_full_grid_and_bounds():
    assert p.planner() == p.load_config()["expected"]
    assert len(p.matrix()) == 6048 and p.planner()["occupancy_row_bound"] == 291168


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
    (p.ROOT / "tests").mkdir()
    for i in range(3):
        (p.ROOT / "tests" / f"test_generated_{i}.py").write_text(
            "# generated lifecycle unit fixture\n"
        )
    for name in ("full", "portable"):
        parts = []
        for i in range(3):
            xml = directory / f"{name}-part{i}.xml"
            xml.write_text(
                '<testsuites><testsuite tests="1" failures="0" errors="0" skipped="0"><testcase name="generated"/></testsuite></testsuites>'
            )
            parts.append(
                dict(
                    exit_code=0,
                    elapsed_seconds=1.0,
                    test_files=[f"tests/test_generated_{i}.py"],
                    junit=str(xml.relative_to(p.ROOT)),
                    junit_sha256=p.file_hash(xml),
                    tests=1,
                    failures=0,
                    errors=0,
                    skipped=0,
                )
            )
        checks[name]["subchecks"] = parts
    base = directory / ("b" * 32)
    base.mkdir()
    phases = []
    for phase in ("simulation", "reporting"):
        owned = base / phase
        owned.mkdir()
        p.durable_json(owned / "grant.json", dict(fixture=True))
        expected_outputs = (
            (
                "summary.json",
                "scenarios.csv",
                "contrasts.csv",
                "occupancies.csv",
                "anchor-audit.csv",
            )
            if phase == "simulation"
            else ("outcomes.png", "latency.png", "sensitivity.png", "reporting.json")
        )
        for name in expected_outputs:
            (owned / name).write_text("generated unit-test evidence")
        body = dict(
            identity=p.identity(),
            source_map=p.source_map(),
            dependencies=p.dependencies(),
            status="body_complete_awaiting_exit",
            phase=phase,
            grant_sha256=p.file_hash(owned / "grant.json"),
            resources=dict(
                latched_error=None,
                owned_thread_alive=False,
                peak_rss_bytes=1024,
                native_heap_reserved_bytes=1024,
            ),
            cleanup_seconds=0.01,
            worker_seconds=1.0,
            outputs={name: p.file_hash(owned / name) for name in expected_outputs},
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
                scenarios_started=6048,
                scenarios_completed=6048,
                event_presentations_started=30240000,
                event_presentations_completed=30240000,
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
        "wrapper",
        "support",
        "scope",
        "config",
        "prompt",
        "source",
        "build",
        "status",
        "missing_check",
        "failed_check",
        "failed_subcheck",
        "missing_subcheck",
        "duplicate_coverage",
        "log",
        "receipt",
        "native",
        "permission",
    ],
)
def test_emitted_record_rejected_before_claim(software, failure):
    directory, record = software
    v = p.read(record)
    if failure in ("task", "owner", "scope", "config", "prompt", "wrapper", "support"):
        key = {
            "task": "task",
            "owner": "validation_owner",
            "scope": "scope",
            "config": "config_sha256",
            "prompt": "prompt_sha256",
            "wrapper": "source_wrapper",
            "support": "lookup_support",
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
    elif failure == "failed_subcheck":
        v["checks"]["full"]["subchecks"][0]["exit_code"] = 1
    elif failure == "missing_subcheck":
        v["checks"]["full"]["subchecks"].pop()
    elif failure == "duplicate_coverage":
        v["checks"]["full"]["subchecks"][1]["test_files"] = v["checks"]["full"][
            "subchecks"
        ][0]["test_files"]
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

    from raregate.simulation import refined_service_native as native

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

    from raregate.simulation import refined_service_native as native

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
    assert p.read(log) == a and len(v) == 192 and len(a["opens"]) == 24


@pytest.mark.parametrize("n", [1, 8, 32, 128])
def test_full_refined_service_only_mapping_negative_control(n):
    q = vectors(n)
    r1, _, a1 = run([1] * n, b=n, t=1, capacity=n, q=q, mapping="next_anchor")
    r2, _, a2 = run([1] * n, b=n, t=1, capacity=n, q=q, mapping="previous_anchor")
    assert r1 == r2 and a1.audit() == a2.audit() and r1["mapped_events"] == 0


def test_storage_scan_owned_atomic_temp_race(tmp_path, monkeypatch):
    from pathlib import Path

    from raregate.simulation.refined_service_runtime import storage_check

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


def refined_vectors(b):
    return {
        k: source.PairedVector(
            "pca-v1",
            1,
            b,
            k,
            tuple((200 + k * 3 + i, 300 + b + k * 7 + i) for i in range(20)),
            tuple(f"1/pca-v1/{b}/{k}/timed/{i}" for i in range(20)),
            k,
            p.point_class(b, k),
        )
        for k in p.REFINED[b]
    }


@pytest.mark.parametrize("support", p.SUPPORTS)
@pytest.mark.parametrize("b", p.REFINED)
@pytest.mark.parametrize("mapping", p.MAPPINGS)
def test_both_support_mappings_exhaustive(support, b, mapping):
    ks = p.SUPPORTS[support][b]
    for m in range(1, b + 1):
        expected = (
            min(k for k in ks if k >= m)
            if mapping == "next_anchor"
            else max(k for k in ks if k <= m)
        )
        assert actual_anchor(b, m, mapping, support) == expected


@pytest.mark.parametrize("b", p.REFINED)
@pytest.mark.parametrize("billing", p.BILLINGS)
def test_independent_all_full_support_control_executed_outcomes(b, billing):
    v = refined_vectors(b)
    outcomes = []
    executed = []
    for support in p.SUPPORTS:
        for mapping in p.MAPPINGS:
            service = ActualAssignment(
                {k: v[k] for k in p.SUPPORTS[support][b]}, b, mapping, billing, support
            )
            result = simulate(
                Trace((1,) * (2 * b), (0.9999,) * (2 * b)),
                ReplayPolicy(b, 10, 1024, 100),
                service,
            )
            outcomes.append(result)
            # Eligible/unused anchors differ legitimately; executed assignments do not.
            executed.append([a for a in service.audit() if a["dispatch_count"]])
    assert all(r == outcomes[0] for r in outcomes)
    assert all(r == executed[0] for r in executed)
    assert outcomes[0]["mapped_events"] == 0


@pytest.mark.parametrize("billing", p.BILLINGS)
def test_refined_b8_exact_for_all_occupancies_and_cursors(billing):
    v = refined_vectors(8)
    results = []
    for mapping in p.MAPPINGS:
        a = ActualAssignment(v, 8, mapping, billing, "refined_32")
        durations = [a.next(m) for m in list(range(1, 9)) * 3]
        assert all(
            a.report()["mapped_" + n] == 0 for n in ("batches", "events", "busy_ns")
        )
        results.append((durations, a.audit(), a.report()))
    assert results[0] == results[1]


def test_shared_anchors_same_objects_and_case_specific_control():
    v = refined_vectors(128)
    coarse = {k: v[k] for k in p.COARSE[128]}
    assert all(
        coarse[k] is v[k] and coarse[k].metadata() == v[k].metadata() for k in coarse
    )
    a = ActualAssignment(v, 128, "next_anchor", "full_control", "refined_32")
    assert a.next(3) == v[3].pairs[0][1] != v[128].pairs[0][1]
    assert a.next(4) == v[4].pairs[0][1]
    assert a.cursors[3] == a.cursors[4] == 1 and a.cursors[128] == 0


def test_previous_mapping_retains_signed_deficit_no_clamp():
    v = refined_vectors(128)
    a = ActualAssignment(v, 128, "previous_anchor", "natural_anchor", "refined_32")
    assert a.next(30) == v[10].pairs[0][0]
    assert a.report()["modeled_minus_actual_rows"] == -20
    assert a.occupancies[30]["k_minus_m"] == -20


@pytest.mark.parametrize("bad", [True, 0, -1, 1.0, float("nan"), float("inf")])
def test_duration_exact_integer_validation(bad):
    v = refined_vectors(1)
    v[1] = source.PairedVector(
        "pca-v1", 1, 1, 1, ((bad, 1),) * 20, ("x",) * 20, 1, "remeasured_reference"
    )
    with pytest.raises(ValueError):
        ActualAssignment(v, 1, "next_anchor", "natural_anchor")


@pytest.mark.parametrize(
    "field",
    [
        "wrapper",
        "case_class",
        "model_shape_rows",
        "repetition",
        "pair",
        "window_index",
        "side_index",
        "ordinal",
        "elapsed_ns",
    ],
)
def test_source_side_identity_rejects_rebound_field(bundle, field):
    root, m = bundle
    name = p.SOURCE_DIRECTORY + "/repetition1/timings.jsonl"
    path = root / name
    lines = path.read_text().splitlines()
    v = json.loads(lines[0])
    v[field] = False if field not in ("wrapper", "case_class") else "foreign"
    lines[0] = json.dumps(v)
    path.write_text("\n".join(lines) + "\n")
    m[name] = dict(sha256=p.file_hash(path), bytes=path.stat().st_size)
    rebind(bundle)
    with pytest.raises(ValueError):
        source.Bundle(root, m).load()


@pytest.mark.parametrize("field", source.SELECTION_FIELDS)
def test_selection_complete_emitted_fields_rejected(bundle, field):
    import csv
    import io

    root, m = bundle
    path = root / source.SELECTION
    rows = list(csv.DictReader(io.StringIO(path.read_text(), newline="")))
    rows[0][field] = "foreign"
    out = io.StringIO(newline="")
    w = csv.DictWriter(out, fieldnames=source.SELECTION_FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    path.write_text(out.getvalue())
    m[source.SELECTION] = dict(sha256=p.file_hash(path), bytes=path.stat().st_size)
    rebind(bundle)
    with pytest.raises((ValueError, KeyError)):
        source.Bundle(root, m).load()


def test_compact_stream_prewrite_growth_and_stream_decode(tmp_path):
    from raregate.simulation.refined_service_sweep import StreamCSV, decode_rows

    path = tmp_path / "occupancies.csv"
    budget = [0]
    stream = StreamCSV(path, 1, budget)
    stream.append(dict(scenario_id=0, m=1))
    stream.file.flush()
    before = path.read_bytes()
    with pytest.raises(ValueError):
        stream.append(dict(scenario_id=0, m=2))
    stream.close()
    assert path.read_bytes() == before and list(decode_rows(path)) == [
        dict(scenario_id=0, m=1)
    ]
    path = tmp_path / "scenarios.csv"
    stream = StreamCSV(path, 1, [56 * 2**20])
    with pytest.raises(ValueError):
        stream.append(dict(scenario_id=0))
    stream.close()
    assert path.stat().st_size == 0


def test_source_custody_no_parse_and_no_source_copies(bundle, tmp_path):
    root, m = bundle
    out = tmp_path / "custody.json"
    audit = source.custody(root, m, audit_path=out, purpose="generated-byte-only")
    assert (
        audit["metadata_opens"] == 24
        and audit["jsonl_records"] == audit["parsed_loads"] == 0
    )
    assert len(audit["opens"]) == 24 and audit == p.read(out)


def test_reader_imports_only_stdlib_and_pure_helpers():
    import ast
    from pathlib import Path

    tree = ast.parse(Path(source.__file__).read_text())
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert all(
        not any(
            word in (name or "")
            for word in ("benchmarks", "models", "training", "data.")
        )
        for name in imports
    )


def test_explicit_byte_and_python_envelopes():
    from raregate.simulation.refined_service_sweep import CSV_TOTAL_CAP, FILE_BYTES

    assert p.LIMITS["source_bundle_bytes"] == 24 * 2**20
    assert sum(v["bytes"] for v in p.SOURCE_MANIFEST.values()) == 17238096 > 16 * 2**20
    assert p.LIMITS["parsed_source_python_bytes"] == 128 * 2**20
    assert p.LIMITS["retained_service_vectors_bytes"] == 2 * 2**20
    assert (
        max(FILE_BYTES.values()) <= 32 * 2**20
        and CSV_TOTAL_CAP + 64 * 2**20 + 8 * 2**20 == 128 * 2**20
    )
    counts = {
        s: sum(len(a[b]) for b, t in p.POLICIES) * 18 * 2 * 3 * 4
        for s, a in p.SUPPORTS.items()
    }
    assert counts == dict(coarse_reference=12528, refined_32=27216)


@pytest.mark.parametrize(
    "field",
    [
        "raw_started_calls",
        "feature_started_calls",
        "feature_requested_rows",
        "adapter_started_calls",
        "adapter_requested_rows",
    ],
)
def test_original_producer_started_requested_counts(bundle, field):
    mutate(
        bundle,
        p.SOURCE_DIRECTORY + "/repetition1/aggregate.json",
        lambda v: v["accounting"].__setitem__(field, False),
    )
    rebind(bundle)
    with pytest.raises(ValueError):
        source.Bundle(*bundle).load()


def test_duplicate_csv_header_rejected_before_value_reconciliation():
    fields = source.PAIR_FIELDS
    payload = (
        ",".join(fields + [fields[-1]])
        + "\n"
        + ",".join("1" for _ in range(len(fields) + 1))
        + "\n"
    ).encode()
    with pytest.raises(ValueError, match="header"):
        source.parse_csv(payload, fields)


@pytest.fixture
def compact_join(tmp_path, monkeypatch):
    from raregate.simulation import refined_service_sweep as sweep
    from raregate.simulation.traces import generate

    trace, meta = generate("periodic", 500, 41)
    v = refined_vectors(1)[1]
    keys = p.matrix()[:8]
    context = []
    rows = {n: [] for n in ("scenarios", "contrasts", "occupancies", "anchor-audit")}
    use = {s: {"0": [0] * 20} for s in p.SUPPORTS}
    totals = sweep.totals_template()
    ranges = {}
    for sid, key in enumerate(keys):
        support, mapping, billing = key[-3:]
        a = ActualAssignment({1: v}, 1, mapping, billing, support)
        result = simulate(trace, ReplayPolicy(1, 0, 1024, 100000000), a)
        row = dict(
            scenario_id=sid,
            **dict(zip(sweep.KEYS, key, strict=True)),
            trace_sha256=meta["trace_sha256"],
            **result,
        )
        rows["scenarios"].append(row)
        context.append(row)
        sweep.update_totals(totals, row)
        for occ in a.occupancies.values():
            rows["occupancies"].append(
                dict(
                    scenario_id=sid,
                    **{
                        k: 0 if k in ("vector_id", "point_class") else value
                        for k, value in occ.items()
                    },
                )
            )
        for ar in a.audit():
            rows["anchor-audit"].append(
                dict(
                    scenario_id=sid,
                    **{
                        k: 0 if k in ("vector_id", "point_class") else value
                        for k, value in ar.items()
                    },
                )
            )
            use[support]["0"] = [
                x + n
                for x, n in zip(
                    use[support]["0"],
                    map(int, ar["assignment_counts"].split(",")),
                    strict=True,
                )
            ]
    rows["contrasts"] = contrasts(context)
    for row in rows["contrasts"]:
        sweep.update_ranges(ranges, row)
    budget = [0]
    for name, group in rows.items():
        stream = sweep.StreamCSV(tmp_path / (name + ".csv"), 8, budget)
        for row in group:
            stream.append(row)
        stream.close()
    summary = dict(
        vectors={"0": v.metadata()},
        traces=[meta],
        source_use_counts=use,
        totals=totals,
        contrast_ranges=ranges,
        audit_row_counts=dict(occupancies=8, anchors=8),
    )
    expected = p.planner()
    expected.update(scenarios=8, contrasts=8, anchor_row_bound=8, occupancy_row_bound=8)
    monkeypatch.setattr(p, "matrix", lambda: keys)
    monkeypatch.setattr(p, "planner", lambda: expected)
    return tmp_path, summary


def test_independent_ordered_compact_join(compact_join):
    from raregate.simulation.refined_service_sweep import verify_csv

    result = verify_csv(*compact_join)
    assert (
        result["scenarios"]
        == result["contrasts"]
        == result["anchors"]
        == result["occupancies"]
        == 8
    )


@pytest.mark.parametrize(
    "failure",
    [
        "occupancy_id",
        "occupancy_class",
        "occupancy_count",
        "anchor_id",
        "anchor_order",
        "anchor_dot",
        "contrast_id",
        "contrast_sign",
        "scenario_class",
    ],
)
def test_compact_join_tamper_rejected(compact_join, failure):
    import csv

    from raregate.simulation.refined_service_sweep import verify_csv

    directory, summary = compact_join
    name = (
        "occupancies"
        if failure.startswith("occupancy")
        else "anchor-audit"
        if failure.startswith("anchor")
        else "contrasts"
        if failure.startswith("contrast")
        else "scenarios"
    )
    path = directory / (name + ".csv")
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    field = {
        "occupancy_id": "scenario_id",
        "occupancy_class": "point_class",
        "occupancy_count": "batches",
        "anchor_id": "vector_id",
        "anchor_order": "pair_order_sha256",
        "anchor_dot": "assigned_busy_ns",
        "contrast_id": "v0_scenario_id",
        "contrast_sign": "busy_ns_difference",
        "scenario_class": "remeasured_reference_batches",
    }[failure]
    rows[0][field] = "99" if "sha256" not in field else "0" * 64
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises((ValueError, KeyError)):
        verify_csv(directory, summary)


@pytest.mark.parametrize("controller", [False, True])
def test_continuous_controller_rss_role(controller):
    from raregate.evaluation.guard import (
        NATIVE_METHOD,
        PRESSURE_METHOD,
        GuardError,
    )
    from raregate.simulation.refined_service_runtime import SimulationGuard

    value = dict(
        peak_rss_bytes=128 * 2**20 + 1,
        native_heap_reserved_bytes=10000,
        native_heap_in_use_bytes=5000,
        workspace_method=NATIVE_METHOD,
        pressure_dispatch_flags=2,
        pressure_errno=None,
        pressure_method=PRESSURE_METHOD,
    )
    guard = SimulationGuard(
        10, probe=lambda: value, clock=lambda: 0, controller=controller
    )
    if controller:
        with pytest.raises(GuardError, match="controller RSS"):
            guard.check()
    else:
        guard.check()
    assert guard.report()["role"] == ("controller" if controller else "worker")


def test_live_trace_memory_counts_dataclass_payloads():
    from raregate.simulation.traces import generate

    trace, meta = generate("poisson", 500, 41)
    live = source.deep_size({("poisson", 500, 41): trace})
    assert meta["retained_python_bytes"] <= live < 16 * 2**20
    assert live > 5000 * (28 + 24)


def test_boolean_dispatch_claim_rejected(software):
    directory, record = software
    base = directory / ("c" * 32)
    base.mkdir()
    create(base / "sources")
    admission.freeze(record, base, fixture=True)
    claim = p.read(base / "claim.json")
    claim["dispatches"] = True
    p.durable_json(base / "claim.json", claim)
    with pytest.raises(ValueError, match="claim"):
        admission.verify(base)


def test_foreign_bootstrap_namespace_rejected_before_writes(tmp_path, monkeypatch):
    from tests.runtime_fixtures import SyntheticClock

    from raregate.simulation import refined_service_native as native

    monkeypatch.setattr(native.rt, "ContinuousClock", SyntheticClock)
    foreign = tmp_path / ("a" * 32)
    with pytest.raises(ValueError, match="namespace"):
        native.run_native(fixture_directory=foreign, bootstrap=True)
    assert not foreign.exists()
