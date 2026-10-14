"""Task0026 synthetic native scientific equivalence, audit and process refusal."""

import copy
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pytest
from test_frozen_cpu_benchmark import FakeGuard, sample

from latenttrigger.benchmarks import protocol as p
from latenttrigger.evaluation import guarded as c
from latenttrigger.evaluation import guarded_core as n
from latenttrigger.evaluation import guarded_protocol as q
from latenttrigger.evaluation.guard import Guard, GuardError
from latenttrigger.evaluation.guarded_audit import Journal, exposure
from latenttrigger.evaluation.guarded_reporting import reporting
from latenttrigger.evaluation.guarded_smoke import fixture
from latenttrigger.evaluation.run import run_final


@pytest.fixture
def toy(tmp_path):
    entries, candidates, Store = fixture(tmp_path)
    return entries, candidates, Store


@pytest.mark.parametrize("index", [0, 1])
def test_actual_native_equivalence_with_unchanged_final_scientific_gate(
    toy, tmp_path, monkeypatch, index
):
    entries, candidates, Store = toy
    monkeypatch.setattr("latenttrigger.evaluation.run.ProcessedStore", Store)
    entry = entries[index]
    target = tmp_path / "old"
    old = run_final(
        tmp_path / entry["model_path"],
        tmp_path / entry["results_path"],
        tmp_path,
        target,
        allow_test=True,
    )
    new = tmp_path / "new"
    new.mkdir()
    actual = n.evaluate_candidate(
        candidates[index],
        Store(),
        new,
        dict(synthetic_authorization=True),
        FakeGuard(),
        authorized=True,
    )
    assert (
        old == actual
        and p.digest(old) == p.read(new / "evaluation.json")["scientific_sha256"]
    )
    audit = p.read(new / "test-unblinding.json")
    assert [r["confirmed_events_read"] for r in audit["population_access"]] == [33, 17]
    assert [r["completed_score_batches"] for r in audit["population_access"]] == [1, 1]


@pytest.mark.parametrize("index", [0, 1])
def test_embargo_rejected_before_population(toy, tmp_path, index):
    _, candidates, Store = toy
    store = Store()
    with pytest.raises(ValueError, match="embargo"):
        n.evaluate_candidate(candidates[index], store, tmp_path, {}, FakeGuard())
    assert store.calls == [] and not (tmp_path / "test-unblinding.json").exists()


@pytest.mark.parametrize(
    "kind",
    ["model", "calibration", "provenance", "config", "feature", "batch", "unknown"],
)
def test_frozen_metadata_refusal_before_reader(toy, tmp_path, kind):
    entries, _, _ = toy
    entry = entries[1]
    file = tmp_path / entry["results_path"]
    doc = p.read(file)
    if kind == "unknown":
        entry = dict(entry, name="ONNX")
    elif kind in ("model", "calibration", "provenance"):
        if kind == "model":
            doc["scientific"]["model_scientific_sha256"] = "wrong"
        if kind == "calibration":
            doc["scientific_sha256"] = "wrong"
        if kind == "provenance":
            doc["scientific"]["provenance"]["scope"] = "dev"
        if kind != "calibration":
            doc["scientific_sha256"] = p.digest(doc["scientific"])
        p.write(file, doc)
    else:
        path = tmp_path / entry["config_path"]
        config = p.read(path)
        if kind == "config":
            config["input"]["processed_schema_version"] = 999
        if kind == "feature":
            config["input"]["features"] = config["input"]["features"][::-1]
        if kind == "batch":
            config["batch_events"] = 32
        p.write(path, config)
    with pytest.raises(ValueError):
        n.load_candidate(tmp_path, entry)


@pytest.mark.parametrize("index", [0, 1])
def test_store_identity_scope_and_full_AE_training_count(toy, index):
    _, candidates, Store = toy
    m = copy.deepcopy(Store().manifest)
    m["scientific_sha256"] = "wrong"
    with pytest.raises(ValueError):
        n.validate_manifest(candidates[index], m)
    m = copy.deepcopy(Store().manifest)
    m["scientific"]["scope"] = "dev"
    with pytest.raises(ValueError):
        n.validate_manifest(candidates[index], m)
    if index == 1:
        m = copy.deepcopy(Store().manifest)
        m["scientific"]["counts"]["train_background"] = 17
        with pytest.raises(ValueError):
            n.validate_manifest(candidates[index], m)


def test_durable_pre_request_pre_read_and_pre_score_order(toy, tmp_path, monkeypatch):
    _, candidates, Store = toy
    target = tmp_path / "audit"
    target.mkdir()
    original = Store.iter_features

    def read(self, split, **kwargs):
        doc = p.read(target / "test-unblinding.json")
        row = doc["population_access"][-1]
        assert row["split"] == split and row["inflight"]["kind"] == "read"
        yield from original(self, split, **kwargs)

    monkeypatch.setattr(Store, "iter_features", read)
    score = candidates[0]["model"].score

    def score_audit(values, **kwargs):
        row = p.read(target / "test-unblinding.json")["population_access"][-1]
        assert (
            row["confirmed_events_read"] == len(values)
            and row["inflight"]["kind"] == "score"
        )
        assert row["confirmed_events_scored"] == 0
        return score(values, **kwargs)

    monkeypatch.setattr(candidates[0]["model"], "score", score_audit)
    n.evaluate_candidate(
        candidates[0], Store(), target, {}, FakeGuard(), authorized=True
    )
    assert not exposure(target / "test-unblinding.json")["potential_inflight"]


@pytest.mark.parametrize(
    "failure", ["read", "score", "labels", "nonfinite", "shape", "order", "extra"]
)
def test_interruption_and_bad_batches_preserve_actual_and_unknown_access(
    toy, tmp_path, monkeypatch, failure
):
    _, candidates, Store = toy
    target = tmp_path / "failed"
    target.mkdir()
    original = Store.iter_features

    def read(self, split, **kwargs):
        if failure == "read":
            raise InterruptedError("Synthetic blocked read")
        for batch in original(self, split, **kwargs):
            if failure == "labels":
                batch.labels[:] = 1
            if failure == "nonfinite":
                batch.event_features[0, 0] = np.nan
            if failure == "shape":
                batch.event_features = batch.event_features[:1]
            if failure == "order":
                batch.event_ids = batch.event_ids[::-1]
            yield batch
            if failure == "extra":
                yield batch

    monkeypatch.setattr(Store, "iter_features", read)
    if failure == "score":

        def stop(*args, **kwargs):
            raise InterruptedError("Synthetic blocked score")

        monkeypatch.setattr(candidates[0]["model"], "score", stop)
    with pytest.raises((ValueError, InterruptedError)):
        n.evaluate_candidate(
            candidates[0], Store(), target, {}, FakeGuard(), authorized=True
        )
    audit = exposure(target / "test-unblinding.json")
    assert audit["exposed"] and audit["population_requests"] == 1
    if failure == "read":
        assert audit["confirmed_events_read"] == 0 and audit["potential_inflight"]
    elif failure == "score":
        assert (
            audit["confirmed_events_read"] == 33
            and audit["confirmed_events_scored"] == 0
            and audit["potential_inflight"]
        )
    elif failure == "extra":
        assert (
            audit["confirmed_events_read"] == 66
            and audit["confirmed_events_scored"] == 33
        )
    else:
        assert (
            audit["confirmed_events_read"] > 0 and audit["confirmed_events_scored"] == 0
        )


@pytest.mark.parametrize("index", [0, 1])
def test_exact_real_sized_synthetic_batch_tails_and_counts(tmp_path, index):
    entries, candidates, Store = fixture(tmp_path, background=150471, signal=100000)
    target = tmp_path / "complete"
    target.mkdir()
    n.evaluate_candidate(
        candidates[index], Store(), target, {}, FakeGuard(), authorized=True
    )
    doc = p.read(target / "test-unblinding.json")
    background, signal = doc["population_access"]
    assert [b["rows_scored"] for b in background["batches"]] == [4096] * 36 + [3015]
    assert [b["rows_scored"] for b in signal["batches"]] == [4096] * 24 + [1696]
    assert (
        exposure(target / "test-unblinding.json")["confirmed_events_scored"] == 250471
    )


@pytest.mark.parametrize(
    "key,val",
    [
        ("extra", True),
        ("candidate_order", ["AE", "PCA"]),
        ("output", "other"),
        ("limits", {"RSS": 999}),
        ("populations", ["train_background"]),
    ],
)
def test_strict_protocol_unsafe_fields(tmp_path, monkeypatch, key, val):
    spec = dict(schema_version=1, candidate_order=["PCA", "AE"], output=q.OUTPUT)
    monkeypatch.setattr(q, "HASH", p.digest(spec))
    path = tmp_path / q.CONFIG
    path.parent.mkdir(parents=True)
    p.write(path, spec)
    assert q.load(tmp_path) == spec
    spec[key] = val
    p.write(path, spec)
    with pytest.raises(ValueError):
        q.load(tmp_path)


def fake_plan():
    return dict(
        software_acceptance_file_byte_sha256="frozen-acceptance",
        source_file_sha256={"code": "frozen-source"},
        candidate_order=["PCA", "AE"],
    )


def consent_fixture(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    plan = fake_plan()
    monkeypatch.setattr(q, "plan", lambda root: plan)
    p.write(tmp_path / q.PLAN, plan)
    consent = dict(
        authority="explicit_human_user_message",
        human_message="Synthetic human approval of both frozen candidates and exact populations, one pass, no later tuning.",
        utc=p.now(),
        approved_plan_canonical_JSON_sha256=p.digest(plan),
        software_acceptance_file_byte_sha256=plan[
            "software_acceptance_file_byte_sha256"
        ],
        source_file_sha256=plan["source_file_sha256"],
        candidates=["pca-v1", "compact-autoencoder-v2"],
        events_per_candidate={"test_background": 150471, "test_signal": 100000},
        passes_per_candidate=1,
        no_post_test_training_or_selection=True,
    )
    p.write(tmp_path / q.CONSENT, consent)
    return plan, consent


@pytest.mark.parametrize(
    "change",
    [
        "optin",
        "plan",
        "source",
        "count",
        "candidate",
        "message",
        "authority",
        "passes",
        "selection",
        "unknown",
    ],
)
def test_human_authorization_audit_exact_plan_and_scope(tmp_path, monkeypatch, change):
    plan, consent = consent_fixture(tmp_path, monkeypatch)
    if change == "source":
        consent["source_file_sha256"] = {}
    if change == "count":
        consent["events_per_candidate"]["test_background"] = 1
    if change == "candidate":
        consent["candidates"] = ["ONNX"]
    if change == "message":
        consent["human_message"] = ""
    if change == "authority":
        consent["authority"] = "local_file_created"
    if change == "passes":
        consent["passes_per_candidate"] = 2
    if change == "selection":
        consent["no_post_test_training_or_selection"] = False
    if change == "unknown":
        consent["extra"] = True
    p.write(tmp_path / q.CONSENT, consent)
    with pytest.raises(ValueError):
        q.authorization(
            tmp_path,
            allow_test=change != "optin",
            approved_plan_sha256="changed" if change == "plan" else p.digest(plan),
        )


def test_exact_authorization_is_an_audit_binding_not_implicit_consent(
    tmp_path, monkeypatch
):
    plan, consent = consent_fixture(tmp_path, monkeypatch)
    assert q.authorization(
        tmp_path, allow_test=True, approved_plan_sha256=p.digest(plan)
    ) == (consent, plan)


@pytest.mark.parametrize("mode", ["readiness", "final"])
def test_atomic_stage_and_separate_final_slot(tmp_path, monkeypatch, mode):
    (tmp_path / "data").mkdir()
    p.write(tmp_path / q.ACCEPTANCE, {})
    monkeypatch.setattr(q, "source_map", lambda root: {})
    monkeypatch.setattr(p, "code_context", lambda root: {})
    if mode == "final":
        p.write(tmp_path / q.CONSENT, {})

    def reserve(_):
        try:
            return c.reserve(
                tmp_path, mode, {}, dict(source_file_sha256={}), {}, consent={}, plan={}
            )[0]
        except FileExistsError:
            return None
        except ValueError as exc:
            # The losing thread can observe the winner before mkdir is attempted.
            assert str(exc) == "Fixed stage reserved/partial/consumed; no retry."
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(reserve, range(2)))
    assert sum(v is not None for v in results) == 1
    assert not (
        tmp_path / q.OUTPUT / ("final" if mode == "readiness" else "readiness")
    ).exists()
    with pytest.raises(ValueError):
        c.namespace(tmp_path, mode)


@pytest.mark.parametrize(
    "state", ["foreign", "partial", "reserved_no_retry", "parent_accepted"]
)
def test_no_reset_of_existing_stage(tmp_path, state):
    path = tmp_path / q.OUTPUT / "readiness"
    path.mkdir(parents=True)
    p.write(path / "reservation.json", dict(status=state))
    with pytest.raises(ValueError):
        c.namespace(tmp_path, "readiness")


@pytest.mark.parametrize(
    "metric,limit",
    [("peak_rss_bytes", 6442450944), ("native_heap_reserved_bytes", 536870912)],
)
@pytest.mark.parametrize("extra", [0, 1])
def test_evaluation_caps_preserve_failed_peaks(metric, limit, extra):
    guard = Guard(
        time.monotonic() + 5,
        probe=lambda: sample(**{metric: limit + extra}),
        notify=False,
    )
    if extra:
        with pytest.raises(GuardError):
            guard.check()
    else:
        guard.check()
    assert guard.report()[metric] == limit + extra


@pytest.mark.parametrize(
    "flags,errno,admitted",
    [
        (1, None, True),
        (2, None, True),
        (None, 1, True),
        (4, None, False),
        ("1", None, False),
        (None, None, False),
    ],
)
def test_evaluation_pressure_and_primary_fail_closed(flags, errno, admitted):
    guard = Guard(
        time.monotonic() + 5,
        probe=lambda: sample(pressure_dispatch_flags=flags, pressure_errno=errno),
        notify=False,
    )
    if admitted:
        guard.check()
    else:
        with pytest.raises(GuardError):
            guard.check()


@pytest.mark.parametrize(
    "change",
    [
        {"peak_rss_bytes": None},
        {"native_heap_reserved_bytes": False},
        {"workspace_method": "unknown"},
        {"native_heap_in_use_bytes": 999999999},
    ],
)
def test_malformed_primary_never_admits(change):
    g = Guard(time.monotonic() + 3, probe=lambda: sample(**change), notify=False)
    with pytest.raises(GuardError):
        g.check()


@pytest.mark.parametrize(
    "behavior", ["body_then_hang", "nonzero", "interrupt", "normal"]
)
def test_parent_supervises_actual_exit_not_success_receipt(
    tmp_path, monkeypatch, behavior
):
    monkeypatch.setattr(c, "parent_check", lambda **kwargs: 1)
    code = "from pathlib import Path; Path('receipt.json').write_text('{\"status\":\"body_complete_awaiting_exit\"}'); "
    if behavior == "body_then_hang":
        code += "import time; time.sleep(4)"
    if behavior == "nonzero":
        code += "raise SystemExit(3)"
    if behavior == "interrupt":
        code += "import os,signal; os.kill(os.getpid(),signal.SIGTERM)"
    dispatch = c.supervise(
        [sys.executable, "-c", code],
        tmp_path / "log",
        root=tmp_path,
        environment=os.environ.copy(),
        stage_seconds=2.2,
        whole_deadline=time.monotonic() + 4,
    )
    assert (tmp_path / "receipt.json").exists() and dispatch["child_reaped"]
    assert dispatch["parent_confirms_normal_exit"] == (behavior == "normal")
    if behavior == "body_then_hang":
        assert "exit deadline" in dispatch["parent_error"]


def test_reporting_refuses_incomplete_pair_and_preserves_strict_metrics(toy, tmp_path):
    entries, candidates, Store = toy
    with pytest.raises(OSError):
        reporting(tmp_path, entries, make_figures=False)
    for phase, candidate in zip(("PCA", "AE"), candidates, strict=True):
        target = tmp_path / phase
        target.mkdir()
        n.evaluate_candidate(
            candidate, Store(), target, {}, FakeGuard(), authorized=True
        )
    result = reporting(tmp_path, entries, make_figures=True)
    assert (tmp_path / "roc-pr.png").stat().st_size > 1000
    assert (
        len((tmp_path / "calibrated-operating-points.csv").read_text().splitlines())
        == 9
    )
    assert result["capacity_controlled_linearity_experiment"] is False
    assert result["evaluations"][0]["metrics"]["background_total"] == 33


def test_guard_failure_propagates_and_owned_watcher_closes():
    with pytest.raises(GuardError):
        with Guard(0, probe=sample, notify=False):
            pass
    g = Guard(time.monotonic() + 2, probe=sample, notify=False)
    with g:
        g.check()
    assert not g.report()["owned_thread_alive"]


def test_stdlib_controller_and_no_alternate_output_cli():
    env = dict(os.environ, PYTHONPATH=str(Path(c.__file__).parents[2]))
    code = "import sys;from latenttrigger.evaluation import guarded;assert not any(k in sys.modules for k in ('numpy','torch','onnx','onnxruntime','sklearn'))"
    subprocess.run([sys.executable, "-c", code], env=env, check=True, timeout=5)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "latenttrigger.evaluation.guarded",
            "--check-readiness",
            "--output",
            "elsewhere",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode != 0 and "unrecognized arguments" in result.stderr


@pytest.mark.parametrize("mode", ["other", "../final", "../../sources", "test_signal"])
def test_unknown_scope_cannot_create_namespace(tmp_path, mode):
    with pytest.raises(ValueError):
        c.namespace(tmp_path, mode)
    assert not (tmp_path / q.OUTPUT).exists()


@pytest.mark.parametrize(
    "failure",
    ["normal", "timeout", "nonzero", "not_reaped", "guard", "watcher", "RSS", "source"],
)
def test_parent_acceptance_requires_more_than_complete_body(
    tmp_path, monkeypatch, failure
):
    (tmp_path / "data").mkdir()
    p.write(tmp_path / q.ACCEPTANCE, {})
    base = tmp_path / "readiness"
    directory = base / "custody"
    directory.mkdir(parents=True)
    p.write(base / "custody-grant.json", {})
    monkeypatch.setattr(q, "source_map", lambda root: {})
    result = dict(
        status="body_complete_awaiting_exit",
        phase="custody",
        source_file_sha256={},
        protocol_canonical_JSON_sha256=q.HASH,
        grant_file_byte_sha256=p.file_hash(base / "custody-grant.json"),
        optimizer_updates=0,
        resources=dict(
            latched_error=None,
            owned_thread_alive=False,
            peak_rss_bytes=1000000,
            native_heap_reserved_bytes=1000000,
        ),
        threads_before={"intra": 1},
        threads_after={"intra": 1},
        timings={"cleanup_seconds": 0.001},
        custody_operations_completed=1,
        population_requests=0,
        exposure={"exposed": False},
        resource_monitor_closed_monotonic=100.0,
        output_file_byte_sha256={},
    )
    dispatch = dict(
        parent_confirms_normal_exit=True,
        child_reaped=True,
        within_deadline=True,
        exit_observed_monotonic=100.1,
    )
    if failure in ("timeout", "nonzero"):
        dispatch["parent_confirms_normal_exit"] = False
    if failure == "not_reaped":
        dispatch["child_reaped"] = False
    if failure == "guard":
        result["resources"]["latched_error"] = "CRITICAL"
    if failure == "watcher":
        result["resources"]["owned_thread_alive"] = True
    if failure == "RSS":
        result["resources"]["peak_rss_bytes"] = 6442450945
    if failure == "source":
        result["source_file_sha256"] = {"changed": "file"}
    p.write(directory / "receipt.json", result)
    accepted = c.accept_stage(
        tmp_path, directory, result, dispatch, {"source_file_sha256": {}}, "custody"
    )
    assert (accepted["status"] == "parent_accepted") == (failure == "normal")
    assert accepted["unaccounted_terminal_interval_seconds"] == pytest.approx(0.1)


def test_missing_body_receipt_never_promoted_and_exposure_not_erased(
    tmp_path, monkeypatch
):
    (tmp_path / "data").mkdir()
    p.write(tmp_path / q.ACCEPTANCE, {})
    directory = tmp_path / "PCA"
    directory.mkdir()
    monkeypatch.setattr(q, "source_map", lambda root: {})
    j = Journal(directory / "test-unblinding.json", {"synthetic": True})
    row = j.request("test_background", 150471)
    j.inflight(row, "read", 0, 4096)
    accepted = c.accept_stage(
        tmp_path,
        directory,
        {"status": "receipt_missing"},
        dict(
            parent_confirms_normal_exit=False,
            child_reaped=True,
            within_deadline=True,
            exit_observed_monotonic=100,
        ),
        {"source_file_sha256": {}},
        "PCA",
    )
    assert accepted["status"] == "parent_rejected"
    access = exposure(directory / "test-unblinding.json")
    assert access["exposed"] and access["potential_inflight"]


def test_monotonic_guard_deadline_is_latched():
    g = Guard(1, probe=sample, clock=lambda: 2, notify=False)
    with pytest.raises(GuardError):
        g.check()
    assert g.report()["latched_error"] is not None
