"""Pure generated correctness/guard tests. No native qualification case starts here."""

import importlib.util
import json
import os
import struct
import subprocess
import sys
import types
from pathlib import Path

import pytest

from raregate.streaming import quota
from raregate.streaming.validation_v2 import CASES, file_plan


@pytest.fixture(autouse=True)
def isolated_quota(monkeypatch):
    monkeypatch.setattr(quota, "CURRENT", None)
    monkeypatch.setattr(quota, "FDS", {})
    yield
    for fd in list(quota.FDS):
        try:
            quota.close(fd)
        except OSError:
            pass


def test_full_two_suite_plan_includes_duplicates_and_copies():
    p = file_plan()
    assert len(p) == 294 and sum(p.values()) == 15136928 <= 16777216
    assert sum(n for _, n, _ in CASES) == 560 and len(CASES) == 12
    assert 2 * sum(n for _, n, _ in CASES) == 1120 <= 3072
    assert p["suite-1/01-normal500/producer-samples.bin"] == 768 * 64
    assert "suite-2/12-observer_report_quota/result.json" in p
    assert p["curated-summary-copy.reserved"] == p["aggregate.json"] == 524288
    assert not any("supervisor.json" in name or "producer.json" in name for name in p)


def test_cross_window_total_and_task0052_counterexample(tmp_path):
    with pytest.raises(quota.QuotaError, match="scoped cap"):
        quota.Ledger(tmp_path, {"window1": 9 * 1024**2, "window2": 9 * 1024**2})
    # Task0052's second per-case copies were missing from its prospective sum.
    with pytest.raises(quota.QuotaError):
        quota.Ledger(tmp_path, {"old": 15218688, "copies": 20 * 131072})


def test_reservations_remain_after_cleanup_and_rename(tmp_path):
    ledger = quota.Ledger(tmp_path, {"one.tmp": 20, "final": 20, "attempt2": 20})
    ledger.write_bytes(tmp_path / "one.tmp", b"abc")
    ledger.write_bytes(tmp_path / "attempt2", b"def")
    ledger.rename_temp(tmp_path / "one.tmp", tmp_path / "final")
    assert (tmp_path / "final").read_bytes() == b"abc" and ledger.inventory()[
        "reserved_bytes"
    ] == 60
    (tmp_path / "attempt2").unlink()
    assert ledger.inventory()["reserved_bytes"] == 60
    with pytest.raises(FileExistsError):
        ledger.write_bytes(tmp_path / "final", b"x")


def test_simultaneous_old_new_and_temp_final_are_all_charged(tmp_path):
    ledger = quota.Ledger(tmp_path, {"old": 4, "new.tmp": 4, "final": 4})
    for name in ("old", "new.tmp", "final"):
        ledger.write_bytes(tmp_path / name, b"abcd")
    assert (
        ledger.inventory()["logical_bytes"]
        == ledger.inventory()["reserved_bytes"]
        == 12
    )
    with pytest.raises(quota.QuotaError):
        ledger.rename_temp(tmp_path / "new.tmp", tmp_path / "final")


@pytest.mark.parametrize("kind", ["byte", "json", "truncate", "pwrite"])
def test_pre_growth_rejection_before_side_effect(tmp_path, kind):
    ledger = quota.Ledger(tmp_path, {"file": 16})
    if kind == "byte":
        with pytest.raises(quota.QuotaError):
            ledger.write_bytes(tmp_path / "file", bytes(17))
        assert not (tmp_path / "file").exists()
    elif kind == "json":
        with pytest.raises(quota.QuotaError):
            ledger.write_json(tmp_path / "file", {"payload": "x" * 32})
        assert not (tmp_path / "file").exists()
    else:
        fd = ledger.open(tmp_path / "file", os.O_CREAT | os.O_EXCL | os.O_RDWR)
        with pytest.raises(quota.QuotaError):
            if kind == "truncate":
                quota.truncate(fd, 17)
            else:
                quota.pwrite(fd, b"xx", 15)
        assert os.fstat(fd).st_size == 0
        quota.close(fd)


@pytest.mark.parametrize("failure", ["short", "error"])
def test_short_failed_write_retains_file_and_quota(tmp_path, monkeypatch, failure):
    ledger = quota.Ledger(tmp_path, {"file": 16})
    original = quota.os.pwrite

    def fail(fd, blob, offset):
        if failure == "error":
            raise OSError("injected disk write failure")
        return original(fd, blob[:1], offset)

    monkeypatch.setattr(quota.os, "pwrite", fail)
    with pytest.raises((quota.QuotaError, OSError)):
        ledger.write_bytes(tmp_path / "file", b"abcd")
    assert (tmp_path / "file").exists() and ledger.inventory()["reserved_bytes"] == 16
    assert (tmp_path / "file").stat().st_size in (0, 1)


def test_symlink_path_escape_hardlink_and_undeclared_file(tmp_path):
    root = tmp_path / "owned"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    ledger = quota.Ledger(root, {"child/file": 8, "link": 8, "hard": 8})
    (root / "child").symlink_to(outside, target_is_directory=True)
    (root / "link").symlink_to(outside / "new")
    for path in (root / "child/file", root / "link", root / "missing", outside / "new"):
        with pytest.raises(quota.QuotaError):
            ledger.write_bytes(path, b"x")
    (outside / "original").write_bytes(b"x")
    os.link(outside / "original", root / "hard")
    with pytest.raises(quota.QuotaError):
        ledger.open(root / "hard", os.O_RDWR)
    assert not (outside / "new").exists()


def test_json_size_cardinalities_and_nonfinite_rejected(tmp_path):
    v = {"one": [0, None, "é", True, 1.25], "two": {}}
    actual = (json.dumps(v, separators=(",", ":")) + "\n").encode()
    assert quota.encoded_size(v) + 1 == len(actual)
    ledger = quota.Ledger(tmp_path, {"value": len(actual)})
    ledger.write_json(tmp_path / "value", v)
    assert (tmp_path / "value").read_bytes() == actual
    for v in ([0] * 4097, {"a": float("nan")}, "x" * 65537):
        with pytest.raises((quota.QuotaError, ValueError)):
            quota.validate_tree(v)
            quota.encoded_size(v)


def test_quota_exhaustion_still_closes_cleanup_resource(tmp_path):
    from raregate.streaming.validation_v2 import report_quota_case

    d = tmp_path / "case"
    entries = {
        "case/cleanup-guard.bin": 4096,
        "case/quota-target.bin": 16,
        "case/emergency.txt": 1024,
    }
    ledger = quota.Ledger(tmp_path, entries)
    r = report_quota_case(d, ledger)
    assert r["software_checks_passed"] and not (d / "cleanup-guard.bin").exists()
    assert (
        ledger.inventory()["logical_bytes"] < 1024
        and ledger.inventory()["reserved_bytes"] == 5136
    )


def test_pinned_task0052_record_compatibility(tmp_path):
    from raregate.streaming.instrumentation import update_sequence
    from raregate.streaming.records import decode, encode

    pkg = types.ModuleType("_lt0052contract")
    pkg.__path__ = [str(tmp_path)]
    sys.modules[pkg.__name__] = pkg
    for name in ("protocol", "records"):
        b = subprocess.run(
            [
                "git",
                "show",
                "1155e83f8ab99adfbd7bc0044d4128f9e188e278:src/latenttrigger/streaming/"
                + name
                + ".py",
            ],
            check=True,
            capture_output=True,
        ).stdout
        p = tmp_path / (name + ".py")
        p.write_bytes(b)
        spec = importlib.util.spec_from_file_location(pkg.__name__ + "." + name, p)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    for kind in ("event", "batch"):
        for _, r in list(update_sequence(kind))[:4]:
            old = module.encode(r, kind)
            assert (
                old
                == encode(r, kind)
                == module.encode(module.decode(encode(r, kind), kind), kind)
            )
            assert encode(decode(old, kind), kind) == old
    assert (
        struct.unpack_from("<H", encode({"status": 1, "intended": 0}, "event"), 8)[0]
        == 1
    )


class FakeClocks:
    def __init__(self):
        self.t = 1000000

    def continuous(self):
        self.t += 1000000
        return self.t

    def observation(self):
        t = self.continuous()
        return t, t, 0


@pytest.mark.parametrize(
    "mode",
    ["normal", "report_stall", "failed_start", "finalizer_exit", "receipt_failure"],
)
def test_outer_boundary_reporting_failure_timeout_and_reaping(
    tmp_path, monkeypatch, mode
):
    from raregate.streaming import validation_v2 as v

    c = FakeClocks()
    directory = tmp_path / "suite-1"
    directory.mkdir()
    ledger = quota.Ledger(
        tmp_path,
        {
            "suite-1/observer.json": 8192,
            "suite-1/observer-emergency.txt": 1024,
            "suite-1/subject.json": 8192,
        },
    )
    events = []

    class Process:
        pid = 424242
        code = None
        polls = 0

        def poll(self):
            self.polls += 1
            if mode not in ("report_stall", "failed_start") and self.polls == 3:
                events.append(("report_write", c.continuous()))
                ledger.write_json(
                    directory / "subject.json",
                    {
                        "qualified": mode != "finalizer_exit",
                        "all_owned_children_reaped": True,
                    },
                )
            if mode not in ("report_stall", "failed_start") and self.polls >= 4:
                self.code = 1 if mode == "finalizer_exit" else 0
            return self.code

        def wait(self, timeout=None):
            events.append(("reaped", c.continuous()))
            return self.code

    p = Process()

    def launch(*args, **kwargs):
        events.append(("launch_before_import", c.continuous()))
        if mode == "failed_start":
            raise OSError("injected Popen start failure")
        return p

    def kill(pid, sig):
        assert pid == p.pid
        p.code = -15

    monkeypatch.setattr(v, "Clocks", lambda: c)
    monkeypatch.setattr(v, "prepare", lambda *args: (ledger, directory, []))
    monkeypatch.setattr(v, "own_rss", lambda: 1024)
    monkeypatch.setattr(v.subprocess, "Popen", launch)
    monkeypatch.setattr(v.os, "killpg", kill)
    monkeypatch.setattr(v, "owned_group_exists", lambda pid: False)
    monkeypatch.setattr(v.time, "sleep", lambda _: None)
    heartbeat_time = c.t
    monkeypatch.setattr(
        v,
        "read_heartbeat",
        lambda _: (
            b"LTH0053\0",
            1,
            heartbeat_time if mode == "report_stall" else c.t,
            1024,
            0,
            0,
            1024,
            0,
        ),
    )
    if mode == "receipt_failure":
        original = ledger.write_json

        def write(path, value):
            if path.name == "observer.json":
                raise OSError("injected receipt finalizer failure")
            return original(path, value)

        monkeypatch.setattr(ledger, "write_json", write)
    r = v.observe(tmp_path, 1)
    assert r["qualified"] == (mode == "normal"), r
    if mode != "failed_start":
        assert r["cleanup"]["subject_reaped"]
        assert r["subject_continuous_bracket_ns"][0] <= events[0][1]
        assert r["subject_continuous_bracket_ns"][1] >= max(t for _, t in events)
    else:
        assert r["cleanup"] is None and r["subject"] is None
    if mode == "report_stall":
        assert r["cleanup"]["forced"] and "liveness" in r["problem"]
    if mode == "receipt_failure":
        assert (directory / "observer-emergency.txt").exists()


def test_help_and_malformed_mode_in_process_create_no_backend(monkeypatch, capsys):
    import runpy

    def bad(*args, **kwargs):
        pytest.fail("Native launch during help/error")

    monkeypatch.setattr(subprocess, "Popen", bad)
    monkeypatch.setattr(sys, "argv", ["validate", "--help"])
    with pytest.raises(SystemExit) as e:
        runpy.run_path(
            "scripts/validate_development_streaming_v2.py", run_name="__main__"
        )
    assert e.value.code == 0 and "generated" in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["validate", "--backend", "physical"])
    with pytest.raises(SystemExit):
        runpy.run_path(
            "scripts/validate_development_streaming_v2.py", run_name="__main__"
        )


def test_partial_setup_failure_emergency_release_ignores_diagnostic_failure(
    tmp_path, monkeypatch
):
    import mmap

    case = tmp_path / "case"
    case.mkdir()
    ledger = quota.Ledger(tmp_path, {"case/fixture-ring.shm": 4096, "case/broken": 1})
    monkeypatch.setattr(quota, "CURRENT", ledger)
    fd = ledger.open(case / "fixture-ring.shm", os.O_CREAT | os.O_EXCL | os.O_RDWR)
    quota.truncate(fd, 4096)
    mapping = mmap.mmap(fd, 4096)
    quota.track_mapping(mapping, fd)
    with pytest.raises(quota.QuotaError):
        ledger.write_bytes(case / "broken", b"xx")
    assert quota.emergency_release(set(), case) == []
    assert not quota.FDS and mapping.closed and not (case / "fixture-ring.shm").exists()
    assert ledger.inventory()["reserved_bytes"] == 4097


def test_unregistered_fd_cannot_write_when_v2_active(tmp_path, monkeypatch):
    ledger = quota.Ledger(tmp_path, {"file": 1})
    monkeypatch.setattr(quota, "CURRENT", ledger)
    fd = os.open(tmp_path / "file", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    try:
        with pytest.raises(quota.QuotaError):
            quota.pwrite(fd, b"x", 0)
    finally:
        os.close(fd)


def test_resolved_v2_contract_and_plan_agree():
    root = Path(__file__).resolve().parents[1]
    contract = json.loads(
        (root / "configs/protocols/development_streaming_v2.json").read_text()
    )
    plan = json.loads(
        (
            root / "configs/streaming/development_streaming_validation_v2.json"
        ).read_text()
    )
    assert (
        not contract["operational_execution_authorized"]
        and not plan["operational_readiness"]
    )
    assert contract["synchronization"]["core_SemLocks_max"] == 21
    assert contract["synchronization"]["wholeactive_tree_max"] == 26
    assert contract["historical_Task0052"]["eligible_event_exceeds"] == 5
    assert plan["whole_task_storage"]["files"] == file_plan()
    assert (
        plan["whole_task_storage"]["reserved_bytes"]
        == sum(file_plan().values())
        == 15136928
    )
    assert [(x["id"], x["offers"], x["rate_hz"]) for x in plan["matrix"]] == list(CASES)
    assert (
        plan["envelope"]["planned_primary_offers"] == sum(n for _, n, _ in CASES) == 560
    )


def test_remaining_owned_group_is_not_silently_accepted(monkeypatch):
    from raregate.streaming import validation_v2 as v

    clock = FakeClocks()

    class Exited:
        pid = 424242

        def poll(self):
            return 0

    alive = [True]
    monkeypatch.setattr(v, "owned_group_exists", lambda pid: alive[0])
    monkeypatch.setattr(v.time, "sleep", lambda _: None)

    def kill(pid, sig):
        assert pid == 424242
        alive[0] = False

    monkeypatch.setattr(v.os, "killpg", kill)
    result = v.tree_cleanup(Exited(), clock, clock.t + 5000000)
    assert result["forced"] and result["owned_group_absent"]
    assert result["actions"] == ["SIGKILL_remaining_owned_group"]
