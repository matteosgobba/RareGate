"""Independent bytes/state tests; no native IPC worker starts here."""

import os
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import pytest

from latenttrigger.streaming.characterization import BASE
from latenttrigger.streaming.fixture import FixtureStore, close_owned
from latenttrigger.streaming.instrumentation import (
    Samples,
    aggregate,
    grouped_samples,
    load_baseline,
    sample_rows,
    update_sequence,
)
from latenttrigger.streaming.protocol import Scheduler
from latenttrigger.streaming.records import (
    Store,
    decode,
    encode,
    encode_into,
    reconcile,
)


@pytest.fixture
def baseline(tmp_path):
    for name in ("records", "protocol"):
        b = subprocess.run(
            ["git", "show", BASE + ":src/latenttrigger/streaming/" + name + ".py"],
            check=True,
            capture_output=True,
        ).stdout
        (tmp_path / (name + ".py")).write_bytes(b)
    return load_baseline(tmp_path)


@pytest.mark.parametrize("kind", ["event", "batch"])
def test_pinned_bidirectional_bytes_and_accounting(tmp_path, baseline, kind):
    st = Store(tmp_path / (kind + ".bin"), 128, kind, True)
    for i, record in update_sequence(kind):
        old = baseline.encode(record, kind)
        assert encode(record, kind) == old
        assert encode(decode(old, kind), kind) == old
        assert baseline.encode(baseline.decode(encode(record, kind), kind), kind) == old
        st.write(i, record)
    assert len(list(update_sequence(kind))) == 256
    actual = st.read_all()
    assert len(actual) == 128
    if kind == "event":
        blob = os.pread(st.fd, 512, 0)
        assert blob[:8] == b"LTE0051\0"
        assert (
            struct.unpack_from("<Q", blob, 40)[0] == 23
        )  # intended, submission, admission, observed
        assert struct.unpack_from("<QQQ", blob, 48) == (0, 1, 2)
        assert struct.unpack_from("<Q", blob, 504)[0] == zlib.crc32(blob[:504])
    else:
        e = [
            baseline.decode(baseline.encode(r, "event"), "event")
            for _, r in list(update_sequence("event"))[1::2]
        ]
        a = reconcile(e, actual, Scheduler(0, 128, 500), 10**9)
        assert (a["completed"], a["boolean_outputs"], a["active"]) == (128, 512, 0)
    st.close()
    st.close()


def test_scratch_reuse_failure_before_publication(tmp_path):
    st = Store(tmp_path / "event", 1, "event", True)
    st.write(0, dict(status=1, intended=0))
    good = os.pread(st.fd, 512, 0)
    scratch = st.scratch
    with pytest.raises(ValueError):
        st.write(0, dict(status=2, run=2**32))
    assert os.pread(st.fd, 512, 0) == good and st.scratch is scratch
    st.write(0, dict(status=2, submission=0))
    assert st.read_all()[0]["intended"] is None
    assert st.read_all()[0]["submission"] == 0
    st.close()


def test_torn_publication_has_no_fallback(tmp_path):
    st = Store(tmp_path / "event", 1, "event", True)
    st.write(0, dict(status=1, intended=0))
    b = encode(dict(status=2, submission=42), "event")
    st.mapping[:256] = b[:256]
    st.mapping[504:512] = bytes(8)
    with pytest.raises(ValueError, match="Torn"):
        st.read_all()
    st.close()


def test_failed_publish_preserves_actual_previous_intent(tmp_path):
    st = FixtureStore(
        tmp_path / "batch", 1, "batch", True, scenario="failed_publication_cleanup"
    )
    _, b = next(update_sequence("batch"))
    st.write(0, b)
    with pytest.raises(OSError, match="publication"):
        st.write(0, dict(b, status=4, read_return=10))
    assert st.read_all()[0]["read_return"] is None
    assert st.read_all()[0]["status"] == 3
    st.close()


def test_invalid_record_bytes_null_crc_and_size(tmp_path):
    with pytest.raises(ValueError):
        encode_into(dict(status=1), "event", bytearray(511))
    st = Store(tmp_path / "bad", 1, "event", True)
    st.write(0, dict(status=1))
    blob = bytearray(os.pread(st.fd, 512, 0))
    blob[200] = 1
    struct.pack_into("<Q", blob, 504, zlib.crc32(blob[:504]))
    with pytest.raises(ValueError, match="Noncanonical"):
        decode(blob, "event")
    st.close()


def test_samples_exact_quantiles_groups_overflow_and_corruption(tmp_path):
    p = tmp_path / "samples"
    s = Samples(p, 4)
    for v in (0, 50000, 50001, 100000):
        s.add(1, 1, 1, 1, 10, 10 + v)
    with pytest.raises(ValueError):
        s.add(1, 1, 1, 1, 0, 1)
    s.close()
    a = grouped_samples(p)[0]
    assert a["n"] == 4 and a["exceeds"] == 2 and a["median_ns"] == 50000.5
    assert a["sum_ns"] == 200001 and a["p95_ns"] == pytest.approx(92500.15)
    assert len(sample_rows(p)) == 4
    b = bytearray(p.read_bytes())
    b[3] ^= 1
    p.write_bytes(b)
    with pytest.raises(ValueError):
        sample_rows(p)
    assert aggregate([])["mean_ns"] is None


def test_every_resource_close_attempted_despite_failure():
    calls = []

    class Bad:
        def close(self):
            calls.append("bad")
            raise OSError("bad close")

    class Good:
        def close(self):
            calls.append("good")

    assert close_owned([Bad(), Good()]) == ["bad close"] and calls == ["bad", "good"]


def test_new_entry_help_and_errors_do_not_activate(tmp_path):
    root = Path(__file__).resolve().parents[1]
    code = """
import sys,runpy
from unittest.mock import patch
sys.argv=['characterize','--help']
with patch('multiprocessing.get_context',side_effect=AssertionError('IPC on help')):
 runpy.run_path('scripts/characterize_development_streaming.py',run_name='__main__')
"""
    r = subprocess.run(
        [sys.executable, "-c", code], cwd=root, capture_output=True, text=True
    )
    assert r.returncode == 0 and "generated" in r.stdout
    for argv in (
        [],
        ["--backend", "physical"],
        ["--run-generated-characterization", "--output", str(tmp_path / "bad")],
    ):
        r = subprocess.run(
            [sys.executable, "scripts/characterize_development_streaming.py", *argv],
            cwd=root,
            capture_output=True,
        )
        assert r.returncode != 0 and not (tmp_path / "bad").exists()


def test_recorder_cleanup_receives_callable_clock(tmp_path, monkeypatch):
    from latenttrigger.streaming import characterization as c

    class Event:
        def set(self):
            pass

    class Child:
        exitcode = 0

        def start(self):
            pass

        def is_alive(self):
            return False

    class Context:
        def Event(self):
            return Event()

        def Process(self, **kwargs):
            return Child()

    def cleanup(children, stop, clock, deadline):
        assert callable(clock) and isinstance(clock(), int)
        return [dict(started=True, normal=True, leaked=False, exitcode=0)]

    monkeypatch.setattr(c.mp, "get_context", lambda _: Context())
    monkeypatch.setattr(c, "synchronization_inventory", lambda *args: {})
    monkeypatch.setattr(c, "cleanup_children", cleanup)
    result = c.run_recorder(tmp_path, tmp_path, "A")
    assert result["cleanup_ns"] >= 0 and result["sample_aggregates"] is None


def test_observer_sample_cardinality_bound(tmp_path):
    # Two append+observer samples per attempted event append, two appends and
    # one full offer cycle, plus five phases/init/final; no native child starts.
    samples = Samples(tmp_path / "producer-samples", 768)
    for _ in range(5 * 128 + 7):
        samples.add(1, 1, 1, 1, 0, 1)
    assert samples.index == 647 and samples.index <= samples.capacity
    samples.close()
    assert 2 * (11 * 128 + 1) + 2 * 128 + 8 <= 4096


def test_native_overflow_injection_has_same_preflight_as_core():
    from test_development_streaming_foundation import descriptor, ring

    from latenttrigger.streaming.fixture import exercise_terminal_preflight

    r = ring()
    r.admit(descriptor(), lambda: 1)
    r.update(producer_closed=1)
    r.stage(lambda: 2)
    r.activate(1, lambda: 3)
    result = exercise_terminal_preflight(r, 1, lambda: 4)
    assert result["credits_preserved"] and r.snapshot()["active"] == 1
    r.finish(1, lambda: 5, "failed")
    assert r.snapshot()["pending"] == 0 and r.snapshot()["failed"] == 1


def test_closed_native_phase_guard_cannot_veto_cleanup(tmp_path):
    from latenttrigger.streaming.records import Phases
    from latenttrigger.streaming.supervision import Clocks, phase_during_cleanup

    phase = Phases(tmp_path / "phase", 3, True)
    phase.close()
    assert phase_during_cleanup(phase, 7, Clocks(), 1) is not None


def test_startup_snapshot_contention_is_bounded_without_arrivals():
    from latenttrigger.streaming.fixture import startup_snapshot

    class Clock:
        t = 0

        def continuous(self):
            self.t += 1000000
            return self.t

    class Stop:
        def is_set(self):
            return False

        def wait(self, seconds):
            assert seconds == 0.0001

    class Ring:
        calls = 0

        def snapshot(self):
            self.calls += 1
            return None if self.calls < 3 else {"t0": 42}

    assert startup_snapshot(Ring(), Stop(), Clock()) == {"t0": 42}

    class Blocked:
        def snapshot(self):
            return None

    with pytest.raises(ValueError, match="timeout"):
        startup_snapshot(Blocked(), Stop(), Clock())
