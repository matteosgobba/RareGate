"""Generated-only, no historical collection or operational imports. Native entry is separate."""

import ast
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np
import pytest

from latenttrigger.streaming.generated import GeneratedBackend, gather, gather_plan
from latenttrigger.streaming.protocol import (
    TOKEN,
    Descriptor,
    Scheduler,
    metadata,
    position,
    read_metadata,
)
from latenttrigger.streaming.records import (
    STAGE,
    Store,
    decode,
    encode,
    reconcile,
)
from latenttrigger.streaming.supervision import Monitor, cleanup_children, safety
from latenttrigger.streaming.transport import Ring


class FakeMemory:
    size = 12288

    def __init__(self):
        self.buf = bytearray(self.size)
        self.buf[:8] = b"LTS0051\0"
        struct.pack_into("<II", self.buf, 8, 1, 64)


class FakeLock:
    held = False
    tries = 0

    def acquire(self, block=True, timeout=None):
        self.tries += 1
        if self.held:
            return False
        self.held = True
        return True

    def release(self):
        assert self.held
        self.held = False


def ring():
    return Ring(FakeMemory(), FakeLock())


def descriptor(k=0):
    return Descriptor(1, k, position(k), 0, 0)


def batch(**updates):
    b = dict(
        run=1,
        phase=1,
        batch=0,
        m=1,
        status=1,
        reason=2,
        members=[0],
        positions=[0],
        admissions=[10],
        dequeues=[20],
        subread_starts=[],
        subread_ends=[],
    )
    b.update(updates)
    return b


def test_external_descriptor_bytes():
    blob = Descriptor(7, 9, 448, 100, 111).encode()
    assert len(blob) == 64 and blob[:8] == b"\x01\0\0\0\x07\0\0\0"
    assert int.from_bytes(blob[8:16], "little") == 9
    assert blob[16:24] == b"\xc0\x01\0\0\0\0\0\0"
    assert int.from_bytes(blob[24:32], "little") == 100
    assert int.from_bytes(blob[32:40], "little") == 111
    assert blob[40:56] == b"LT0051-FIXTURE!!" and blob[56:] == bytes(8)
    independent = struct.pack(
        "<HHIQIIQQ16s8s", 1, 0, 3, 2, 896, 0, 5, 8, TOKEN, bytes(8)
    )
    assert Descriptor.decode(independent) == Descriptor(3, 2, 896, 5, 8)


@pytest.mark.parametrize("offset", [0, 2, 20, 40, 56, 63])
def test_descriptor_rejects_reserved_version_token(offset):
    b = bytearray(descriptor().encode())
    b[offset] ^= 1
    with pytest.raises(ValueError):
        Descriptor.decode(b)


@pytest.mark.parametrize(
    "d",
    [
        Descriptor(-1, 0, 0, 0, 0),
        Descriptor(1, 2**64, 0, 0, 0),
        Descriptor(1, 0, 128, 0, 0),
        Descriptor(1, 0, 0, 2, 1),
        Descriptor(1, 0, 0, 0, 0, b"x" * 16),
    ],
)
def test_bad_descriptor(d):
    with pytest.raises(ValueError):
        d.encode()


def test_metadata_independent_bytes():
    expected = (17).to_bytes(8, "little") + (63).to_bytes(8, "little") + bytes(48)
    assert metadata(17, 63) == expected and read_metadata(expected) == (17, 63)
    with pytest.raises(ValueError):
        read_metadata(expected[:-1] + b"x")


@pytest.mark.parametrize(
    "k,p",
    [
        (0, 0),
        (127, 127),
        (128, 448),
        (255, 575),
        (256, 896),
        (383, 1023),
        (384, 0),
        (767, 1023),
    ],
)
def test_symbolic_sequence(k, p):
    assert position(k) == p


@pytest.mark.parametrize(
    "rate,horizon", [(500, 1536000000), (2500, 307200000), (5000, 153600000)]
)
def test_production_formulas_only(rate, horizon):
    s = Scheduler(99, 768, rate)
    assert s.horizon == 99 + horizon
    assert s.intended(767) == 99 + 767 * 10**9 // rate
    assert s.k == 0  # no24casecampaign/arrivalvector


@pytest.mark.parametrize(
    "now,expected",
    [
        (0, ["attempt"]),
        (2000000, ["attempt"]),
        (2000001, ["missed_late"]),
        (10000000, ["missed_horizon"]),
    ],
)
def test_lag_horizon_boundaries(now, expected):
    s = Scheduler(0, 1, 100)
    emitted = []
    s.wake(now, lambda k, t, a: emitted.append(a))
    assert emitted == expected


def test_catchup_independent_expectation():
    s = Scheduler(0, 10, 10000)
    got = []
    s.wake(600000, lambda k, t, a: got.append((k, a)))
    assert got == [
        (0, "attempt"),
        (1, "attempt"),
        (2, "attempt"),
        (3, "attempt"),
        (4, "missed_catchup_cap"),
        (5, "missed_catchup_cap"),
        (6, "missed_catchup_cap"),
    ]
    assert s.k == 7 and s.t0 == 0
    got.clear()
    s.wake(1000000, lambda k, t, a: got.append(a))
    assert got == ["missed_horizon"] * 3


def test_ring_capacity_includes_staged_active_and_wrap():
    r = ring()
    for i in range(64):
        assert r.admit(descriptor(i), lambda: 0) == ("admitted", 0, i)
    staged = r.stage(lambda: 0)
    assert len(staged) == 8 and r.snapshot()["pending"] == 64
    assert r.admit(descriptor(64), lambda: 0)[0] == "rejected_capacity"
    r.activate(8, lambda: 0)
    assert r.admit(descriptor(64), lambda: 0)[0] == "rejected_capacity"
    assert r.snapshot()["active"] == 8
    r.finish(8, lambda: 1)
    for i in range(64, 72):
        assert r.admit(descriptor(i), lambda: 2)[0] == "admitted"
    assert r.snapshot()["tail"] == 72 and r.snapshot()["pending"] == 64
    next_group = r.stage(lambda: 3)
    assert [d.presentation for d, _, _, _ in next_group] == list(range(8, 16))
    with pytest.raises(ValueError):
        r.finish(8, lambda: 4)  # staged, not active
    r.activate(8, lambda: 4)
    r.finish(8, lambda: 5, "failed")
    with pytest.raises(ValueError):
        r.finish(8, lambda: 6)
    assert r.snapshot()["failed"] == 8


def test_contention_one_try_and_no_mutation():
    r = ring()
    r.lock.held = True
    before = bytes(r.shm.buf)
    tries = r.lock.tries
    assert r.admit(descriptor(), lambda: 10) == ("rejected_contention", 10, None)
    assert r.lock.tries == tries + 1 and bytes(r.shm.buf) == before


@pytest.mark.parametrize(
    "closed,now,expected", [(False, 999999, 0), (False, 1000000, 1), (True, 1, 1)]
)
def test_partial_oldest_and_closed(closed, now, expected):
    r = ring()
    r.admit(descriptor(), lambda: 0)
    r.update(producer_closed=int(closed))
    assert len(r.stage(lambda: now)) == expected


def test_sequence_overflow_is_not_wrap():
    r = ring()
    r._set("head", 2**64 - 1)
    r._set("tail", 2**64 - 1)
    before = bytes(r.shm.buf)
    with pytest.raises(ValueError):
        r.admit(descriptor(), lambda: 0)
    assert bytes(r.shm.buf) == before


@pytest.mark.parametrize("m", range(1, 9))
def test_generated_shapes_and_independent_oracle(m):
    backend = GeneratedBackend()
    positions = [0, 448, 0, 1023, 449, 448, 1, 896][:m]
    selected = []

    def read(ids):
        selected.append(list(ids))
        return backend.read(ids)

    rows = gather(positions, read)
    assert rows.tolist() == [[float(p), float(p + 1), float(p * 2)] for p in positions]
    assert sum(map(len, selected)) == m
    assert len(selected) == max(positions.count(p) for p in positions)
    assert rows.flags.owndata and not np.shares_memory(rows, backend.table)
    features = backend.features(rows)
    scores, masks = backend.decisions(features)
    backend.reference(positions, scores, masks)
    expected = [[p > t for t in (0, 1, 64, 127)] for p in positions]
    assert masks.tolist() == expected and scores.tolist() == list(map(float, positions))
    assert scores.flags.owndata and masks.flags.owndata
    rows[:] = -1
    assert features[:, 0].tolist() == positions


def test_duplicate_layer_indices():
    assert gather_plan([448, 0, 448, 0, 448]) == [
        [(0, 1), (448, 0)],
        [(0, 3), (448, 2)],
        [(448, 4)],
    ]


@pytest.mark.parametrize("positions", [[], list(range(9)), [128], [-1]])
def test_invalid_gather_never_calls_read(positions):
    with pytest.raises(ValueError):
        gather(positions, lambda _: pytest.fail("Read called"))


def test_callback_cannot_return_neighbors_or_aliases():
    b = GeneratedBackend()
    with pytest.raises(ValueError):
        gather([0], lambda _: b.table[:1])
    with pytest.raises(ValueError):
        gather([0], lambda _: b.table[:2].copy())
    with pytest.raises(ValueError):
        b.read([1, 0])
    with pytest.raises(ValueError):
        b.read([0, 0])


def test_strict_ties_all_false_and_nonfinite():
    b = GeneratedBackend()
    f = b.features(b.read([0]))
    s, m = b.decisions(f)
    assert m.tolist() == [[False] * 4]
    f[0, 0] = np.nan
    with pytest.raises(ValueError):
        b.decisions(f)
    with pytest.raises(ValueError):
        b.reference([0], s.reshape(1, 1), m)
    with pytest.raises(ValueError):
        b.reference([0], s, m.reshape(4))
    with pytest.raises(ValueError):
        b.reference([0], s, np.ones((1, 4), dtype=bool))


def test_operational_mode_fails_before_numpy_import(monkeypatch):
    import builtins

    old = builtins.__import__

    def guard(name, *a, **kw):
        assert name != "numpy"
        return old(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", guard)
    with pytest.raises(ValueError):
        GeneratedBackend(mode="physical")


def test_event_external_bytes_and_null_zero():
    blob = bytearray(512)
    blob[:8] = b"LTE0051\0"
    struct.pack_into("<HHHHI", blob, 8, 1, 1, 7, 1, 5)
    struct.pack_into("<Q", blob, 24, 2)
    struct.pack_into("<I", blob, 32, 448)
    struct.pack_into("<Q", blob, 40, 3)  # intended0 valid; submission10 valid
    struct.pack_into("<Q", blob, 56, 10)
    struct.pack_into("<Q", blob, 504, zlib.crc32(blob[:504]))
    r = decode(blob, "event")
    assert r["intended"] == 0 and r["submission"] == 10 and r["admission"] is None
    assert r["k"] == 2 and r["prefix"] == 448


@pytest.mark.parametrize(
    "kind,r", [("event", dict(k=0, status=1, intended=0)), ("batch", batch())]
)
def test_fixed_records_crc_reserved_and_overflow(kind, r):
    blob = encode(r, kind)
    assert len(blob) == 512
    assert decode(blob, kind)["status"] == 1
    bad = bytearray(blob)
    bad[50] ^= 1
    with pytest.raises(ValueError):
        decode(bad, kind)
    if kind == "event":
        bad = bytearray(blob)
        bad[200] = 1
        struct.pack_into("<Q", bad, 504, zlib.crc32(bad[:504]))
        with pytest.raises(ValueError):
            decode(bad, kind)
    with pytest.raises(ValueError):
        encode({**r, "run": 2**32}, kind)


def test_record_bounds_and_blank_absence(tmp_path):
    st = Store(tmp_path / "events.bin", 1, "event", True)
    assert st.read_all() == [None]
    st.write(0, dict(status=1, intended=0))
    with pytest.raises(ValueError):
        st.write(1, {})
    st.close()
    st.close()
    assert (tmp_path / "events.bin").stat().st_size == 512


def test_projection_independent_cutoffs_and_output_later_invalid():
    scheduler = Scheduler(0, 4, 1000000)
    events = [
        dict(status=2, intended=0, submission=100, admission=200, observed=200),
        dict(status=3, intended=1000, submission=1100, rejection=1200, observed=1200),
        dict(status=1, intended=2000, submission=2100, observed=2100),
        dict(status=5, intended=3000, observed=9000),
    ]
    b = batch(
        admissions=[200],
        dequeues=[250],
        dispatch=300,
        output=500,
        status=STAGE["failed"],
        terminal=600,
    )
    a = reconcile(events, [b], scheduler, 150)
    assert (a["offered"], a["submitted"], a["undecided"], a["admitted"]) == (1, 1, 1, 0)
    a = reconcile(events, [b], scheduler, 275)
    assert (a["staged"], a["completed"], a["active"]) == (1, 0, 0)
    a = reconcile(events, [b], scheduler, 400)
    assert a["active"] == 1 and a["completed"] == 0
    a = reconcile(events, [b], scheduler, 10000)
    assert (
        a["offered"],
        a["missed"],
        a["submitted"],
        a["rejected_capacity"],
        a["undecided"],
        a["completed"],
        a["failed"],
        a["boolean_outputs"],
    ) == (4, 1, 3, 1, 1, 1, 0, 4)
    with pytest.raises(ValueError):
        reconcile(events, [b, b], scheduler, 10000)


@pytest.mark.parametrize("stage", ["read_intent", "read_return", "decision"])
def test_abort_never_fabricates_pending_zero(stage):
    s = Scheduler(0, 1, 500)
    e = [dict(status=2, submission=0, admission=1, observed=1)]
    b = batch(admissions=[1], dequeues=[2], dispatch=3, status=STAGE[stage])
    a = reconcile(e, [b], s, s.horizon)
    assert a["active"] == 1 and a["completed"] == 0 and a["uncertain"] == 1


@pytest.mark.parametrize(
    "svc,cont,valid",
    [
        (-1, 1, True),
        (1, -1, True),
        (1, 300000000, True),
        (1, 6000000, True),
        (1, 1, False),
    ],
)
def test_monitor_faults(svc, cont, valid):
    with pytest.raises(ValueError):
        Monitor(0, 0).observe(svc, cont, valid=valid)


def test_illustrative_deadline_is_not_safety_stop():
    safety(100000001, 0, 0, 0, 1)  # 100ms missed, but2s safety intact
    with pytest.raises(ValueError):
        safety(2000000001, 0, 0, 0, 1)
    with pytest.raises(ValueError):
        safety(3000000000, 0, 0, 3000000000, 0)
    with pytest.raises(ValueError):
        safety(6000000000, 0, 0, 6000000000, 1, invocation_ns=20000000000)


class FakeProcess:
    name = "fake-child"

    def __init__(self, started=True, stubborn=False):
        self.pid = 1 if started else None
        self.exitcode = None
        self.stubborn = stubborn
        self.alive = started

    def join(self, timeout):
        pass

    def is_alive(self):
        return self.alive

    def terminate(self):
        if not self.stubborn:
            self.alive = False
            self.exitcode = -15

    def kill(self):
        self.terminate()

    def close(self):
        pass


class Stop:
    def set(self):
        pass


def test_cleanup_ignores_mutex_failed_start_and_detects_leak():
    results = cleanup_children(
        [FakeProcess(False), FakeProcess(), FakeProcess(stubborn=True)],
        Stop(),
        lambda: 0,
        2_000_000_000,
    )
    assert (
        not results[0]["started"] and results[1]["forced"] and not results[1]["normal"]
    )
    assert results[2]["leaked"]


def test_import_and_help_audit(tmp_path):
    root = Path(__file__).resolve().parents[1]
    code = """
import sys,runpy
from pathlib import Path
root=Path.cwd()
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)):
  p=str(args[0]);assert not any(x in p for x in ('/data/','/artifacts/','.npy','.h5','.pt'))
 if event=='import':assert not any(str(args[0]).startswith(x) for x in ('torch','h5py','latenttrigger.models','latenttrigger.data'))
sys.addaudithook(audit)
import latenttrigger.streaming.fixture
from unittest.mock import patch
with patch('multiprocessing.shared_memory.SharedMemory',side_effect=AssertionError('shared memory on help')):
 sys.argv=['validator','--help']
 runpy.run_path('scripts/validate_development_streaming_foundation.py',run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=root, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert "generated" in result.stdout
    for argv in (
        [],
        ["--backend", "physical"],
        ["--run-generated-fixtures", "--output", str(root / "data/raw")],
    ):
        r = subprocess.run(
            [
                sys.executable,
                str(root / "scripts/validate_development_streaming_foundation.py"),
                *argv,
            ],
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0 and not (tmp_path / "created").exists()


def test_no_forbidden_import_or_message_channel():
    root = Path(__file__).resolve().parents[1]
    # The source-free core's import boundary. Later explicitly gated HDF/model
    # adapters are tested separately; they were not part of this core contract.
    for name in (
        "protocol",
        "records",
        "transport",
        "generated",
        "supervision",
        "fixture",
    ):
        file = root / "src/latenttrigger/streaming" / (name + ".py")
        tree = ast.parse(file.read_text())
        imports = [
            n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
        ]
        assert not any(
            "models" in s or "benchmarks" in s or "latenttrigger.data" in s
            for s in imports
        )
        calls = [
            n.func.attr
            for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        ]
        assert not set(calls) & {
            "Queue",
            "SimpleQueue",
            "Pipe",
            "socket",
            "load",
            "loadtxt",
            "read_hdf",
        }


def test_batch_layout_external_offsets():
    b = batch(
        m=2,
        members=[7, 8],
        positions=[448, 0],
        dequeues=[20, 21],
        admissions=[10, 11],
        dispatch=30,
        subread_starts=[40, 44],
        subread_ends=[42, 45],
        read_intents=2,
        read_rows=2,
    )
    blob = encode(b, "batch")
    assert blob[:8] == b"LTB0051\0" and int.from_bytes(blob[20:22], "little") == 2
    assert int.from_bytes(blob[32:40], "little") == 30
    assert blob[96:104] == (7).to_bytes(4, "little") + (8).to_bytes(4, "little")
    assert blob[160:168] == (448).to_bytes(4, "little") + bytes(4)
    assert int.from_bytes(blob[192:200], "little") == 20
    assert int.from_bytes(blob[320:328], "little") == 40
    assert int.from_bytes(blob[384:392], "little") == 42
    assert int.from_bytes(blob[448:452], "little") == 2


def test_phase_storage_and_observed_faults(tmp_path):
    from latenttrigger.streaming.records import Phases

    class C:
        def observation(self):
            return 10, 11, 1

    p = Phases(tmp_path / "phase.bin", 1, True)
    p.append(2, C(), 123)
    assert p.read_all() == [
        dict(role=1, code=2, service_ns=10, continuous_ns=11, RSS_bytes=123)
    ]
    p.index = 32
    with pytest.raises(ValueError):
        p.append(3, C(), 1)
    p.close()
    p.close()
    assert (tmp_path / "phase.bin").stat().st_size == 16384


def test_timing_keeps_100ms_observation_without_imputing_drop():
    from latenttrigger.streaming.records import timing_summary

    e = [
        dict(status=2, intended=0, submission=1, admission=2),
        dict(status=3, intended=3, submission=4, rejection=5),
    ]
    b = batch(
        admissions=[2], dequeues=[3], dispatch=4, read_start=5, output=100_000_001
    )
    result = timing_summary(e, [b], 200_000_000)
    assert result["completed_illustrative_100ms_misses"] == 1
    assert result["offered_latency"] == dict(n=1, maximum_ns=100_000_001)
    assert result["producer_lag"]["n"] == 2
    assert result["pending_overdue_at_cutoff"] == 0


def test_horizon_linearization_and_undecided_crash():
    s = Scheduler(100, 1, 500)
    h = s.horizon
    e = [
        dict(status=2, intended=100, submission=h - 1, admission=h + 1, observed=h + 1)
    ]
    a = reconcile(e, [], s, h)
    assert a["submitted"] == 1 and a["undecided"] == 1 and a["admitted"] == 0
    assert reconcile(e, [], s, h + 2)["ring"] == 1


def test_record_unknown_state_before_write():
    with pytest.raises(ValueError):
        encode(dict(status=999), "event")
    with pytest.raises(ValueError):
        encode(batch(status=999), "batch")


def test_credit_release_timestamp_is_output_commit():
    r = ring()
    r.admit(descriptor(), lambda: 1)
    r.update(producer_closed=1)
    r.stage(lambda: 2)
    r.activate(1, lambda: 3)
    assert r.finish(1, lambda: 17) == 17
    snap = r.snapshot()
    assert snap["completed"] == 1 and snap["pending"] == 0 and snap["progress"] == 17


def test_explicit_cancellation_is_not_uncertain_completion():
    s = Scheduler(0, 1, 500)
    e = [dict(status=2, submission=0, admission=1, observed=1)]
    b = batch(
        admissions=[1], dequeues=[2], dispatch=3, status=STAGE["cancelled"], terminal=4
    )
    a = reconcile(e, [b], s, 10)
    assert a["cancelled"] == 1 and a["failed"] == a["completed"] == a["active"] == 0


def test_stage_projection_independent_cutoffs():
    from latenttrigger.streaming.records import stage_projection

    b = batch(
        m=2,
        members=[0, 1],
        positions=[0, 1],
        admissions=[1, 2],
        dequeues=[3, 4],
        subread_starts=[5],
        subread_ends=[10],
        read_intents=1,
        read_rows=2,
        feature_intent=12,
        features=15,
        score_intent=17,
        decision=20,
    )
    at7 = stage_projection([b], 7)
    assert at7["read"] == dict(
        intents=1, returned_calls=0, returned_rows=0, failed=0, inflight_uncertain=1
    )
    assert stage_projection([b], 13)["read"]["returned_rows"] == 2
    assert stage_projection([b], 13)["feature"]["inflight_uncertain"] == 1
    assert stage_projection([b], 16)["feature"]["returned_calls"] == 1
    assert stage_projection([b], 18)["score"]["inflight_uncertain"] == 1
    assert stage_projection([b], 21)["score"]["returned_rows"] == 2


def test_extra_stage_timestamps_and_record_bound():
    b = batch(feature_intent=0, score_intent=5, reference_intent=6, reference_return=7)
    blob = encode(b, "batch")
    assert len(blob) == 512
    r = decode(blob, "batch")
    assert (
        r["feature_intent"] == 0
        and r["score_intent"] == 5
        and r["reference_return"] == 7
    )
    assert int.from_bytes(blob[136:144], "little") == 5


def test_failed_cleanup_journal_cannot_prevent_release():
    from latenttrigger.streaming.supervision import phase_during_cleanup, release_region

    class BrokenPhases:
        def append(self, *args):
            raise OSError("injected full storage")

    class Region:
        calls = 0

        def close(self):
            raise BufferError("injected remaining view")

        def unlink(self):
            self.calls += 1
            return self.calls == 1

    region = Region()
    assert "full storage" in phase_during_cleanup(BrokenPhases(), 7, None, 1)
    first, again, errors = release_region(region)
    assert first and not again and errors and region.calls == 2


def test_fixture_config_matches_core_and_not_grant():
    import json

    from latenttrigger.streaming.fixture import SCENARIOS
    from latenttrigger.streaming.protocol import SHARED_BYTES

    cfg = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "configs/streaming/development_streaming_foundation_v1.json"
        ).read_text()
    )
    assert (
        cfg["fixture_only"]
        and not cfg["operational_execution_authorized"]
        and not cfg["operational_allowance_granted"]
    )
    assert cfg["transport"]["shared_bytes"] == SHARED_BYTES == 12288
    assert [
        (x["name"], x["offers"], x["rate_per_second"]) for x in cfg["fixture_scenarios"]
    ] == [(k, *v) for k, v in SCENARIOS.items()]


def test_region_rejects_operational_path_before_open(monkeypatch):
    import os

    from latenttrigger.streaming.transport import Region

    def no_open(*args, **kwargs):
        pytest.fail("Opened unsupported path")

    monkeypatch.setattr(os, "open", no_open)
    with pytest.raises(ValueError):
        Region("/some/production/raw/fixture-ring.shm")


def test_terminal_overflow_preserves_credits():
    r = ring()
    r.admit(descriptor(), lambda: 1)
    r.update(producer_closed=1)
    r.stage(lambda: 2)
    r.activate(1, lambda: 3)
    r._set("completed", 2**64 - 1)
    before = bytes(r.shm.buf)
    with pytest.raises(ValueError):
        r.finish(1, lambda: 4)
    assert bytes(r.shm.buf) == before


def test_cleanup_snapshot_failure_is_optional():
    from latenttrigger.streaming.supervision import cleanup_snapshot

    class Broken:
        def snapshot(self):
            raise ValueError("injected corrupt counters")

    snap, error = cleanup_snapshot(Broken())
    assert snap is None and "corrupt counters" in error
