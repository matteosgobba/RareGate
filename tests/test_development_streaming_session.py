"""Focused pure ownership regressions. Actual files use the immutable Task0057 ledger."""

import os
import runpy
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import Mock

import pytest

from raregate.streaming import pilot54, quota, session57, startup55
from raregate.streaming.session_context import GeneratedSession57, SessionFixture57

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / session57.ROOT


@pytest.fixture
def ledger(monkeypatch, tmp_path):
    assert not quota.FDS
    previous = quota.CURRENT
    root = tmp_path / "audit-owned-journal"
    root.mkdir()
    monkeypatch.setattr(sys.modules[__name__], "ROOT", root)
    # A unit-test instance of the historical quota profile, never its run/permit.
    value = quota.Ledger(root, session57.file_plan(), task="0057")
    quota.CURRENT = value
    try:
        yield value
    finally:
        monkeypatch.undo()  # Retire injected I/O failures before fixture cleanup.
        try:
            errors = quota.emergency_release(set(), root)
        finally:
            quota.CURRENT = previous
    assert not errors and not quota.FDS and not quota.MAPPINGS


def journal_at(index):
    directory = ROOT / f"unit-{index}"
    directory.mkdir(exist_ok=True)
    return startup55.Journal(directory / "journal.bin")


def test_late_session_registration_is_retired_by_case_cleanup(ledger):
    before = set(quota.FDS)
    journal = journal_at(0).open()
    fd = journal.fd
    assert fd in quota.FDS
    assert quota.emergency_release(before, journal.path.parent) == []
    assert fd not in quota.FDS
    with pytest.raises(ValueError, match="Stale"):
        journal.write({"must_not_publish": True})


def test_eager_session_survives_case_cleanup_and_single_close(ledger):
    j = journal_at(0).open()
    identity = j.evidence()
    previous = set(quota.FDS)
    fd = ledger.open(j.path.parent / "case.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    quota.pwrite(fd, b"case", 0)
    j.write(dict(candidate="PCA"))
    assert quota.emergency_release(previous, j.path.parent) == []
    assert fd not in quota.FDS
    j.write(dict(candidate="AE"))
    assert j.evidence()["inode"] == identity["inode"] and j.evidence()["opens"] == 1
    assert startup55.read_journal(j.path) == dict(candidate="AE")
    j.close()
    j.close()
    assert j.evidence()["closes"] == 1 and j.closed and not quota.FDS
    with pytest.raises(ValueError, match="finalized"):
        j.write({})


def test_numeric_fd_reuse_cannot_write_or_close_other_owned_file(ledger):
    j = journal_at(1).open()
    old = j.fd
    quota.close(old)
    fd = ledger.open(j.path.parent / "case.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    assert fd == old  # Lowest available numeric fd is deterministically reused.
    quota.pwrite(fd, b"OTHER", 0)
    with pytest.raises(ValueError, match="Stale"):
        j.write({"wrong": True})
    with pytest.raises(ValueError, match="Stale"):
        j.close()
    assert os.pread(fd, 5, 0) == b"OTHER" and fd in quota.FDS
    quota.close(fd)


def test_external_fd_reuse_inode_guard(ledger):
    j = journal_at(2).open()
    old = j.fd
    os.close(old)  # Simulate an external owner violating the registry.
    ledger.path(j.path.parent / "case.bin", 5)
    fd = os.open(j.path.parent / "case.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    assert fd == old
    os.write(fd, b"OTHER")
    with pytest.raises(ValueError, match="inode"):
        j.write({})
    with pytest.raises(ValueError, match="inode"):
        j.close()
    assert os.pread(fd, 5, 0) == b"OTHER"
    os.close(fd)
    quota.FDS.pop(fd)


def test_short_and_failed_write_keep_close_independent(ledger, monkeypatch):
    j = journal_at(int(os.environ.get("TASK0057_WRITE_TEST_SLOT", "3"))).open()
    original = quota.pwrite
    monkeypatch.setattr(quota, "pwrite", lambda fd, b, o: original(fd, b[:7], o))
    with pytest.raises(ValueError, match="Short"):
        j.write({"a": 1})
    assert j.generation == 0 and startup55.read_journal(j.path) is None
    monkeypatch.setattr(
        quota, "pwrite", Mock(side_effect=quota.QuotaError("quota failure"))
    )
    with pytest.raises(quota.QuotaError):
        j.write({})
    j.close()
    assert not quota.FDS


def test_partial_open_truncate_failure_still_closes(ledger, monkeypatch):
    j = journal_at(4)
    monkeypatch.setattr(quota, "truncate", Mock(side_effect=OSError("truncate failed")))
    with pytest.raises(OSError):
        j.open()
    assert j.fd in quota.FDS and j.opens == 1
    j.close()
    assert not quota.FDS


def test_failed_close_does_not_forget_registration(ledger, monkeypatch):
    j = journal_at(5).open()
    fd = j.fd
    close = os.close
    monkeypatch.setattr(os, "close", Mock(side_effect=OSError("close failed")))
    with pytest.raises(OSError):
        j.close()
    assert fd in quota.FDS and not j.closed
    monkeypatch.setattr(os, "close", close)
    j.close()
    j.close()
    assert j.close_count == 1 and fd not in quota.FDS


def test_unopened_close_is_safe_and_does_not_allocate(ledger):
    j = journal_at(6)
    j.close()
    j.close()
    assert j.opens == j.close_count == 0 and not j.path.exists()


def fake_case_report():
    return dict(
        scenario="pilot54",
        normal=True,
        software_checks_passed=True,
        synchronization_inventory=dict(owned_names=[]),
        children=[],
        sample_aggregates={},
    )


def shared_stub(monkeypatch, index):
    from raregate.streaming import fixture

    j = journal_at(index)
    monkeypatch.setattr(startup55, "Journal", lambda path: j)
    run = Mock(side_effect=lambda *a, **k: fake_case_report())
    monkeypatch.setattr(fixture, "run_scoped_core", run)
    context = GeneratedSession57(str(ROOT), str(j.path.parent), "fake", "normal")
    return j, run, context


def test_missing_consumer_report_is_invalid_and_session_closes(ledger, monkeypatch):
    j, run, ctx = shared_stub(monkeypatch, 7)
    result = pilot54.candidate_session(
        ROOT, j.path.parent, ctx, lambda _: None, save_case_reports=False
    )
    assert not result["accepted"] and result["primary_failure"]
    assert (
        len(result["candidates"]) == 1
        and result["candidates"][0]["real_consumer"] is None
    )
    assert run.call_count == 1 and result["journal_after_close"]["closes"] == 1


def test_intercase_publication_failure_does_not_start_ae_or_prevent_close(
    ledger, monkeypatch
):
    j, run, ctx = shared_stub(monkeypatch, 8)
    monkeypatch.setattr(
        j, "write", Mock(side_effect=ValueError("intercase checkpoint failed"))
    )
    result = pilot54.candidate_session(
        ROOT, j.path.parent, ctx, lambda _: None, save_case_reports=False
    )
    assert "intercase checkpoint failed" in result["primary_failure"]["message"]
    assert run.call_count == 1 and result["journal_after_close"]["closes"] == 1
    assert result["unattempted_candidates"] == ["compact-autoencoder-v2"]


def test_session_finalizer_failure_retains_primary_and_retired_fd(ledger, monkeypatch):
    j, run, ctx = shared_stub(monkeypatch, 9)
    close = j.close

    def failed_close():
        close()
        raise OSError("finalizer close diagnostic failure")

    monkeypatch.setattr(j, "close", failed_close)
    result = pilot54.candidate_session(
        ROOT, j.path.parent, ctx, lambda _: None, save_case_reports=False
    )
    assert result["primary_failure"] and len(result["cleanup_failures"]) == 1
    assert result["journal_after_close"]["closes"] == 1 and not quota.FDS


def test_whole_task_ledger_and_exact_bounds():
    f = session57.file_plan()
    assert len(f) == 511 and sum(f.values()) == 30182464 < 33554432
    assert sum(n for _, n, _ in session57.v2.CASES) == 560
    assert 2 * (560 + 3 * 128) == 1888 <= 3840
    assert 2 * (12 + 2 + 1 + 2) == 34 <= 36
    assert session57.TOTAL_CAP == 280_000_000_000
    assert session57.BOOTSTRAPS == ()
    ledger = quota.Ledger(ROOT, f, task="0057")
    with pytest.raises(quota.QuotaError):
        ledger.path(ROOT / "unit-0/case.bin", 65)
    with pytest.raises(quota.QuotaError):
        ledger.path(ROOT / "../outside", 1)


def test_context_is_immutable_disjoint_and_rejects_real_paths(monkeypatch):
    from raregate.streaming.pilot_context import PilotContext56

    c = SessionFixture57("/tmp/no", "/tmp/no/session-normal", "bad", "pca-v1", "normal")
    assert type(c) is not PilotContext56
    with pytest.raises(FrozenInstanceError):
        c.task = "0056"
    with pytest.raises(ValueError):
        c.validate_location(REPO)


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        [],
        ["--run-pilot", "--root", str(ROOT)],
        ["--qualify-generated", "--root", "data/task0056-validation/session-v2"],
    ],
)
def test_entry_help_and_errors_are_inactive(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["validate"] + args)
    with pytest.raises(SystemExit):
        runpy.run_path(str(REPO / session57.SCRIPT), run_name="__main__")


def test_fault_expectations_do_not_accept_missing_reports():
    value = dict(
        candidates=[],
        cleanup_failures=[],
        journal_before_close=dict(registered=False),
        journal_after_close=dict(closed=False, opens=0, closes=0),
        journal_checkpoints=[],
        accepted=False,
        unattempted_candidates=list(session57.CANDIDATES),
    )
    for name in session57.SESSIONS:
        assert not all(session57.session_expectations(name, value).values())


def test_payload_denial_survives_error_and_finalizer_paths(monkeypatch):
    hooks = []
    monkeypatch.setattr(sys, "addaudithook", hooks.append)
    counts = startup55.install_payload_denial(REPO, ROOT)
    assert len(hooks) == 1
    for phase in ("normal", "error", "finalization"):
        for path in (
            "data/raw/forbidden.h5",
            "artifacts/models/forbidden.json",
            "results/benchmarks/forbidden.npy",
            "configs/data/lhco_rnd_v5.json",
            "configs/models/pca_baseline.json",
            "configs/models/compact_autoencoder_v2.json",
        ):
            with pytest.raises(PermissionError):
                hooks[0]("open", (str(REPO / path), "rb", 0))
        hooks[0]("open", (str(ROOT / (phase + ".generated")), "rb", 0))
    assert counts == dict(denied_open_attempts=18, production_open_successes=0)


def test_shared_function_has_no_activation_or_custody():
    import inspect

    body = inspect.getsource(pilot54.candidate_session)
    assert "custody(" not in body and "activation.json" not in body
    operational = inspect.getsource(pilot54.pilot_subject)
    generated = inspect.getsource(session57.run_integrations)
    assert "candidate_session(" in operational and "candidate_session(" in generated
    assert "run_pilot" not in Path(session57.SCRIPT).read_text()
