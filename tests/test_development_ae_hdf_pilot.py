"""0058 focused deterministic checks; no native cases or original payload opens."""

import copy
import hashlib
import itertools
import json
import os
import runpy
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from raregate.streaming import (
    fixture,
    hdf_consumer,
    pilot54,
    pilot58,
    quota,
    startup55,
)
from raregate.streaming.ae_context import (
    AE_PLAN,
    GeneratedFixture58,
    GeneratedSession58,
    PilotContext58,
)
from raregate.streaming.pilot_context import CANDIDATES, PilotContext56, digest

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / pilot58.ROOT
SLOTS = itertools.count(int(os.environ.get("TASK0058_TEST_SLOT_START", "0")))


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    previous = quota.CURRENT
    original_repo = REPO
    assert not quota.FDS
    # Copy only source/config text into an isolated mock repository. No old root,
    # permit, original payload or historical acceptance is opened or reset.
    repo = tmp_path / "audit-owned-mock-repo"
    paths = {e["path"] for e in pilot58.source_manifest(REPO)} | {
        "configs/streaming/development_hdf_consumer_pilot_v2.json"
    }
    for path in paths:
        source = REPO / path
        destination = repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    root = repo / pilot58.ROOT
    root.mkdir(parents=True)
    monkeypatch.setattr(sys.modules[__name__], "REPO", repo)
    monkeypatch.setattr(sys.modules[__name__], "ROOT", root)
    monkeypatch.setattr(sys.modules[__name__], "SLOTS", itertools.count())
    for module in (pilot54, fixture, hdf_consumer):
        monkeypatch.setattr(
            module,
            "__file__",
            str(repo / Path(module.__file__).relative_to(original_repo)),
        )
    # An in-memory/current-source unit binding; the frozen config stays unchanged.
    (repo / pilot58.CONFIG).write_text(json.dumps(spec()))
    value = quota.Ledger(root, pilot58.file_plan(), task="0058")
    quota.CURRENT = value
    value.write_json(
        root / "owner.json",
        dict(
            task="0058",
            candidate_plan=list(AE_PLAN),
            generated_groups=1,
            conditional_P4_sessions=1,
            test_only=True,
            P4=False,
        ),
    )
    try:
        yield value
    finally:
        monkeypatch.undo()
        try:
            errors = quota.emergency_release(set(), root)
        finally:
            quota.CURRENT = previous
    assert not errors and not quota.FDS and not quota.MAPPINGS


def slot():
    n = next(SLOTS)
    assert n < 20
    d = ROOT / f"unit-{os.environ.get('TASK0058_TEST_EXECUTION', '1')}-{n}"
    d.mkdir()
    return d


def spec():
    value = json.loads((REPO / pilot58.CONFIG).read_text())
    current = {e["path"]: e for e in pilot58.source_manifest(REPO)}
    value["source_pins"] = [current[e["path"]] for e in value["source_pins"]]
    return value


def generated(name="ae-only"):
    return GeneratedSession58(
        str(ROOT),
        str(ROOT / "suite-1" / ("session-" + name)),
        digest(pilot58.source_manifest(REPO)),
        name,
    )


def test_exact_original_scope_and_unchanged_arithmetic():
    s = spec()
    pilot58.validate_spec(s, REPO)
    assert tuple(s["candidate_plan"]) == AE_PLAN and len(s["allowed_files"]) == 14
    assert not any(x["role"].startswith("pca-v1:") for x in s["allowed_files"])
    assert sum(x["bytes"] for x in s["allowed_files"] if x["role"] != "raw") == 377025
    assert (
        hashlib.sha256(
            (REPO / "docs/arithmetic-cpu-v2-policy.md").read_bytes()
        ).hexdigest()
        == s["numerical"]["derivation_file_sha256"]
    )
    assert [x["threshold"] for x in s["models"][0]["thresholds"]] == [
        3.478338537407165,
        4.681070974717348,
        8.324174660133213,
        16.642218868621573,
    ]


@pytest.mark.parametrize(
    "change",
    ["PCA", "root", "allowance", "replacement", "numerical", "threshold", "ledger"],
)
def test_mutated_scope_rejected_without_payload(change):
    s = copy.deepcopy(spec())
    if change == "PCA":
        s["candidate_plan"] = ["pca-v1"]
    if change == "root":
        s["root"] = "data/task0056-validation/session-v2"
    if change == "allowance":
        s["full_study_execution_authorized"] = True
    if change == "replacement":
        s["session_replacement_authorized"] = True
    if change == "numerical":
        s["numerical"]["same_shape_score_atol"] = 1
    if change == "threshold":
        s["models"][0]["thresholds"][0]["threshold"] = 0
    if change == "ledger":
        s["file_ledger"]["owner.json"] += 1
    with pytest.raises(ValueError):
        pilot58.validate_spec(s, REPO)


def test_one_group_reserved_and_all_count_arithmetic():
    p = pilot58.file_plan()
    s = spec()
    assert len(p) == 366 and sum(p.values()) == 21563584 < 33554432
    assert not any("suite-2/" in x for x in p)
    assert 560 + 384 + 64 == s["generated"]["configured_offers"] == 1008
    assert 12 + 2 + 1 + 2 + 1 == s["generated"]["underlying_dispatches"] == 18
    assert pilot58.EXPECTED_CHECKS == 16 and pilot58.TOTAL_CAP == 160 * 10**9
    assert s["maxima"]["raw_rows"] == 4 * sum(range(1, 9)) + 64 == 208
    assert s["maxima"]["score_rows"] == 208 + 2 * sum(range(1, 9)) + 64 == 344
    assert s["maxima"]["booleans"] == 4 * 344 == 1376
    assert s["maxima"]["public_score_calls"] == 32 + 64 + 16 + 64 == 176
    assert s["maxima"]["raw_custody_bytes"] == 2 * 2908260409


def test_wrong_candidate_denied_before_pipeline_or_constructor(ledger, monkeypatch):
    ctx = PilotContext58(str(ROOT), digest(pilot58.source_manifest(REPO)))
    launch = Mock(side_effect=AssertionError("pipeline must not start"))
    monkeypatch.setattr(fixture, "_run_pipeline", launch)
    with pytest.raises(ValueError, match="rejects PCA"):
        fixture.run_scoped_core(
            ROOT / "pilot/pca-v1",
            "pca-v1",
            quota_root=str(ROOT),
            heartbeat=lambda _: None,
            context=ctx,
        )
    assert not launch.called
    open_file = Mock(side_effect=AssertionError("no diagnostic/payload open"))
    monkeypatch.setattr(quota, "open_file", open_file)
    with pytest.raises(ValueError, match="rejects PCA"):
        hdf_consumer.RealBackend(
            ROOT, ROOT / "pilot/pca-v1", "pca-v1", None, None, context=ctx
        )
    assert not open_file.called


def test_immutable_disjoint_generated_capability_and_default_plan(ledger):
    g = generated()
    assert pilot54.candidate_plan(g, REPO) == AE_PLAN
    assert pilot54.candidate_plan(None, REPO) == CANDIDATES
    assert (
        pilot54.candidate_plan(PilotContext56("unused", "unused"), REPO) == CANDIDATES
    )
    with pytest.raises(FrozenInstanceError):
        g.task = "0058"
    with pytest.raises(ValueError):
        g.for_candidate("pca-v1")
    with pytest.raises(ValueError):
        pilot54.controller_binding(g)
    with pytest.raises(ValueError):
        GeneratedFixture58(
            str(ROOT),
            str(ROOT / "suite-1/session-ae-only"),
            g.bundle_sha256,
            "pca-v1",
            "ae-only",
        ).validate_location(REPO)
    with pytest.raises(ValueError):
        PilotContext58(g.root, g.bundle_sha256, task=g.task).specification(REPO)


@pytest.mark.parametrize(
    "wrong",
    [
        "task",
        "root",
        "bundle",
        "role",
        "parent",
        "candidate",
        "ledger",
        "plan",
        "budget",
    ],
)
def test_activation_immediate_guards(ledger, monkeypatch, wrong):
    ctx = PilotContext58(str(ROOT), digest(pilot58.source_manifest(REPO)))
    active = dict(
        task="0058",
        root=str(ROOT),
        bundle_sha256=ctx.bundle_sha256,
        subject_pid=os.getppid(),
        single_session=True,
        candidate_plan=list(AE_PLAN),
    )
    if wrong in ("task", "root", "bundle"):
        active[{"bundle": "bundle_sha256"}.get(wrong, wrong)] = "wrong"
    if wrong == "parent":
        active["subject_pid"] += 100000
    if wrong == "plan":
        active["candidate_plan"] = ["pca-v1"]
    original = Path.read_text

    def read(path, *args, **kw):
        if path == ROOT / "pilot/activation.json":
            return json.dumps(active)
        return original(path, *args, **kw)

    monkeypatch.setattr(Path, "read_text", read)
    monkeypatch.setattr(
        "multiprocessing.current_process",
        lambda: SimpleNamespace(name="bad" if wrong == "role" else "fixture-consumer"),
    )
    qualify = Mock()
    monkeypatch.setattr(pilot58, "check_qualification", qualify)
    budget = hdf_consumer.Budget()
    if wrong == "budget":
        budget.counts["model_loads"] = 1
    if wrong == "ledger":
        monkeypatch.setattr(
            quota, "CURRENT", quota.Ledger(ROOT, ledger.entries, task="0056")
        )
    with pytest.raises(ValueError):
        ctx.validate_payload(
            REPO, "pca-v1" if wrong == "candidate" else AE_PLAN[0], budget
        )
    assert not qualify.called


def test_correct_activation_metadata_still_does_not_load_sources(ledger, monkeypatch):
    ctx = PilotContext58(str(ROOT), digest(pilot58.source_manifest(REPO)))
    active = dict(
        task="0058",
        root=str(ROOT),
        bundle_sha256=ctx.bundle_sha256,
        subject_pid=os.getppid(),
        single_session=True,
        candidate_plan=list(AE_PLAN),
    )
    original = Path.read_text
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda path, *a, **k: (
            json.dumps(active)
            if path == ROOT / "pilot/activation.json"
            else original(path, *a, **k)
        ),
    )
    monkeypatch.setattr(
        "multiprocessing.current_process",
        lambda: SimpleNamespace(name="fixture-consumer"),
    )
    qualify = Mock()
    monkeypatch.setattr(pilot58, "check_qualification", qualify)
    source = Mock(side_effect=AssertionError("no source read"))
    monkeypatch.setattr("raregate.streaming.ae_context.source_bytes", source)
    assert (
        ctx.validate_payload(REPO, AE_PLAN[0], hdf_consumer.Budget())["task"] == "0058"
    )
    assert qualify.call_count == 1 and not source.called


def test_owned_journal_survives_case_cleanup_and_rejects_reuse(ledger):
    d = slot()
    j = startup55.Journal(d / "journal.bin").open()
    identity = j.evidence()
    previous = set(quota.FDS)
    f = ledger.open(d / "case.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    quota.pwrite(f, b"OTHER", 0)
    j.write(dict(candidate="AE"))
    assert quota.emergency_release(previous, d) == [] and f not in quota.FDS
    j.write(dict(final=True))
    assert j.evidence()["inode"] == identity["inode"]
    old = j.fd
    quota.close(old)
    f = ledger.open(d / "case.bin", os.O_RDWR)
    assert old == f
    with pytest.raises(ValueError, match="Stale"):
        j.write({})
    with pytest.raises(ValueError, match="Stale"):
        j.close()
    assert os.pread(f, 5, 0) == b"OTHER"
    quota.close(f)


def report():
    return dict(
        scenario="pilot54",
        normal=True,
        software_checks_passed=True,
        software_checks={},
        synchronization_inventory=dict(owned_names=[]),
        children=[],
        sample_aggregates={},
        accounting=dict(after_stop=dict(completed=1)),
    )


def stub_session(monkeypatch, ledger):
    d = slot()
    j = startup55.Journal(d / "journal.bin")
    ctx = generated()
    monkeypatch.setattr(startup55, "Journal", lambda _: j)
    run = Mock(side_effect=lambda *a, **k: report())
    monkeypatch.setattr(fixture, "run_scoped_core", run)
    original_exists = Path.exists
    original_read = Path.read_text
    monkeypatch.setattr(
        Path,
        "exists",
        lambda p: True if p.name == "consumer-final.json" else original_exists(p),
    )
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda p, *a, **k: (
            json.dumps(dict(valid=True))
            if p.name == "consumer-final.json"
            else original_read(p, *a, **k)
        ),
    )
    return j, ctx, run


def test_one_candidate_acceptance_and_single_journal(ledger, monkeypatch):
    j, ctx, run = stub_session(monkeypatch, ledger)
    value = pilot54.candidate_session(
        ROOT, Path(ctx.directory), ctx, lambda _: None, save_case_reports=False
    )
    assert value["accepted"] and value["intended_candidates"] == value[
        "attempted_candidates"
    ] == list(AE_PLAN)
    assert value["unattempted_candidates"] == [] and run.call_count == 1
    assert j.opens == j.close_count == 1 and not quota.FDS


@pytest.mark.parametrize("fault", ["report", "checkpoint", "close", "missing", "zero"])
def test_shared_final_report_and_cleanup_errors(ledger, monkeypatch, fault):
    j, ctx, run = stub_session(monkeypatch, ledger)
    if fault == "report":
        monkeypatch.setattr(
            ledger, "write_json", Mock(side_effect=quota.QuotaError("report quota"))
        )
    if fault == "checkpoint":
        monkeypatch.setattr(j, "write", Mock(side_effect=OSError("checkpoint failed")))
    if fault == "missing":
        monkeypatch.setattr(
            Path, "exists", lambda p: False if p.name == "consumer-final.json" else True
        )
    if fault == "zero":
        r = report()
        r["accounting"]["after_stop"]["completed"] = 0
        run.side_effect = lambda *a, **k: r
    if fault == "close":
        close = j.close

        def fail():
            close()
            raise OSError("final close failure")

        monkeypatch.setattr(j, "close", fail)
    v = pilot54.candidate_session(
        ROOT,
        Path(ctx.directory),
        ctx,
        lambda _: None,
        save_case_reports=fault == "report",
    )
    assert not v["accepted"] and j.close_count == 1 and not quota.FDS
    if fault == "report":
        assert v["report_failure"]["message"] == "report quota"
    if fault == "close":
        assert v["cleanup_failures"][0]["message"] == "final close failure"


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        [],
        ["--candidate", "pca-v1"],
        ["--run-pilot", "--root", "data/task0056-validation/session-v2"],
        ["--qualify-generated", "--group", "2", "--root", str(ROOT)],
    ],
)
def test_help_import_and_malformed_arguments_inactive(ledger, monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["ae-pilot"] + args)
    with pytest.raises(SystemExit):
        runpy.run_path(str(REPO / pilot58.SCRIPT), run_name="__main__")
    assert not (ROOT / "pilot/activation.json").exists()


def test_payload_denial_includes_configs_and_all_lifecycle_phases(monkeypatch):
    hooks = []
    monkeypatch.setattr(sys, "addaudithook", hooks.append)
    audit = startup55.install_payload_denial(REPO, ROOT)
    for phase in ("import", "work", "error", "finalizer"):
        for p in (
            "data/raw/forbidden.h5",
            "artifacts/models/compact-autoencoder-v2/model.json",
            "results/benchmarks/forbidden.npy",
            "configs/models/compact_autoencoder_v2.json",
            "configs/models/pca_baseline.json",
            "configs/data/lhco_rnd_v5.json",
        ):
            with pytest.raises(PermissionError):
                hooks[0]("open", (str(REPO / p), "rb", 0))
        hooks[0]("open", (str(ROOT / (phase + ".generated")), "rb", 0))
    assert audit == dict(denied_open_attempts=24, production_open_successes=0)


def test_second_group_rejected_before_any_native_or_metadata_read():
    with pytest.raises(ValueError, match="one reserved"):
        pilot58.prepare_group(ROOT, 2, REPO)


@pytest.mark.parametrize(
    "fault", ["none", "report", "heartbeat", "close", "activation"]
)
def test_actual_outer_subject_uses_one_plan_and_independent_finalization(
    ledger, monkeypatch, fault
):
    monkeypatch.setattr(quota, "activate", lambda _: ledger)
    d = slot()
    fd = ledger.open(d / "journal.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    ctx = PilotContext58(str(ROOT), digest(pilot58.source_manifest(REPO)))
    identity = pilot58.source_manifest(REPO)
    original_read = Path.read_text
    prospective = dict(source_manifest=identity, bundle_sha256=digest(identity))
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda path, *a, **k: (
            json.dumps(prospective)
            if path == ROOT / "pilot/prospective.json"
            else original_read(path, *a, **k)
        ),
    )
    monkeypatch.setattr(pilot58, "check_qualification", Mock())
    monkeypatch.setattr(ledger, "open", lambda *a, **k: fd)
    writes = []

    def write(path, value):
        if path == ROOT / "pilot/activation.json" and fault == "activation":
            raise quota.QuotaError("activation write failure")
        if path == ROOT / "pilot/subject.json" and fault == "report":
            raise quota.QuotaError("subject report quota")
        writes.append((path, copy.deepcopy(value)))

    monkeypatch.setattr(ledger, "write_json", write)
    monkeypatch.setattr(ledger, "write_bytes", Mock())
    custody = Mock(side_effect=lambda *a, **k: dict(passed=True, fixture=True, bytes=0))
    monkeypatch.setattr(pilot54, "custody", custody)
    monkeypatch.setattr(pilot54, "custody_progress", lambda _: [])
    result = dict(
        accepted=True,
        candidates=[dict(candidate=AE_PLAN[0], software_checks_passed=True)],
        intended_candidates=list(AE_PLAN),
        attempted_candidates=list(AE_PLAN),
        unattempted_candidates=[],
        primary_failure=None,
        report_failure=None,
        cleanup_failures=[],
    )
    loop = Mock(return_value=result)
    monkeypatch.setattr(pilot54, "candidate_session", loop)

    def heartbeat(fd, clocks, peaks, generation):
        if fault == "heartbeat" and generation >> 32 == 5:
            raise OSError("final heartbeat failed")

    monkeypatch.setattr(pilot54.v2, "write_heartbeat", heartbeat)
    real_close = quota.close
    if fault == "close":
        monkeypatch.setattr(
            quota, "close", Mock(side_effect=OSError("heartbeat close failed"))
        )
    code = pilot54.pilot_subject(ROOT, context=ctx)
    final = next(v for path, v in reversed(writes) if path.name.startswith("subject"))
    if fault == "activation":
        assert custody.call_count == loop.call_count == 0
        assert not final["qualified"] and code == 1
        assert final["attempted_candidates"] == []
        assert final["unattempted_candidates"] == list(AE_PLAN)
        assert not final["operational_access_activated"] and fd not in quota.FDS
        assert final["primary_failure"]["message"] == "activation write failure"
        return
    assert custody.call_count == 2 and loop.call_count == 1
    assert (
        final["intended_candidates"] == final["attempted_candidates"] == list(AE_PLAN)
    )
    assert final["unattempted_candidates"] == [] and len(final["cases"]) == 1
    assert final["qualified"] == (fault == "none") and code == int(fault != "none")
    if fault == "report":
        assert final["report_failure"]["message"] == "subject report quota"
    if fault == "heartbeat":
        assert final["report_failure"]["message"] == "final heartbeat failed"
    if fault == "close":
        assert final["cleanup_failures"][0]["message"] == "heartbeat close failed"
        monkeypatch.setattr(quota, "close", real_close)
        real_close(fd)
    else:
        assert fd not in quota.FDS


def test_generated_artifact_capability_rejects_original_entry_before_open(
    ledger, monkeypatch
):
    ctx = generated().for_candidate(AE_PLAN[0])
    monkeypatch.setattr(
        "multiprocessing.current_process",
        lambda: SimpleNamespace(name="fixture-consumer"),
    )
    owned = dict(
        role="compact-autoencoder-v2:model",
        path=str(Path(ctx.directory).relative_to(REPO) / "serialized/model.bin"),
    )
    monkeypatch.setattr(
        GeneratedFixture58, "specification", lambda *a: dict(allowed_files=[owned])
    )
    read = Mock(side_effect=AssertionError("must reject before reading"))
    monkeypatch.setattr("raregate.streaming.ae_context.source_bytes", read)
    original = next(
        e
        for e in spec()["allowed_files"]
        if e["role"] == "compact-autoencoder-v2:model"
    )
    with pytest.raises(ValueError, match="Closed generated role"):
        ctx.read_source(REPO, original)
    assert not read.called
