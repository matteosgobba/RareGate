"""Data-free Task0054 checks: no operational file opens or native case launches."""

import ast
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np
import pytest

from raregate.streaming import hdf_consumer as h
from raregate.streaming import pilot54, quota
from raregate.streaming.generated import GeneratedBackend, gather
from raregate.streaming.protocol import Descriptor
from raregate.streaming.records import decode, encode


def test_closed_primary_matrix_and_arithmetic():
    spec = json.loads(Path(pilot54.CONFIG).read_text())
    assert [c["id"] for c in spec["case_order"]] == ["pca-v1", "compact-autoencoder-v2"]
    assert [
        (c["offers"], c["rate_hz"], c["horizon_ns"]) for c in spec["case_order"]
    ] == [(64, 500, 128000000)] * 2
    raw_calls = 2 * 2 * 2 * 8 + 2 * 64
    raw_rows = 2 * 2 * 2 * sum(range(1, 9)) + 2 * 64
    ref_calls, ref_rows = 2 * 2 * 8 + 2 * 64, 2 * 2 * sum(range(1, 9)) + 2 * 64
    assert (raw_calls, raw_rows, raw_calls + ref_calls, raw_rows + ref_rows) == (
        192,
        416,
        352,
        688,
    )
    assert spec["maxima"]["public_score_calls"] == 352
    assert spec["maxima"]["booleans"] == 4 * 688
    assert sum(spec["buffer_derivation"].values()) <= 8 * 1024**2
    assert (
        spec["limits"]["pre_custody_seconds"]
        + 2 * spec["limits"]["run_seconds"]
        + spec["limits"]["post_custody_seconds"]
        + spec["limits"]["reporting_seconds"]
        == 180
    )


def test_whole_task_reservations_preserve_old_cap():
    plan = pilot54.file_plan()
    assert len(plan) == 334 and sum(plan.values()) == 21324448
    assert sum(plan.values()) < 32 * 1024**2
    root = Path.cwd()
    with pytest.raises(quota.QuotaError):
        quota.Ledger(root, plan)  # old default remains16MiB
    ledger = quota.Ledger(root, plan, task="0054")
    assert ledger.cap == 32 * 1024**2
    assert sum(plan.values()) + plan["delivery-summary.json"] < ledger.cap
    assert plan["curated-pilot-summary-copy.reserved"] == plan["delivery-summary.json"]


@pytest.mark.parametrize("positions", [[], [64], [-1], [0] * 9, [False], [1.0]])
def test_scope_rejects_before_reader(positions):
    read = Mock()
    with pytest.raises(ValueError):
        h.gather_real(positions, read)
    read.assert_not_called()


def test_duplicate_layers_scatter_exact_2101_owned():
    seen = []

    def read(pos):
        seen.append(pos)
        a = np.zeros((len(pos), 2101), dtype="<f8")
        a[:, :2100] = np.array(pos)[:, None]
        return a

    phases = []
    pos = [7, 1, 7, 0, 1, 63, 7, 0]
    rows = h.gather_real(
        pos,
        read,
        lambda j, n: phases.append(("i", j, n)),
        lambda j, n: phases.append(("r", j, n)),
    )
    assert seen == [[0, 1, 7, 63], [0, 1, 7], [7]]
    assert rows.flags.owndata and rows.shape == (8, 2101)
    np.testing.assert_array_equal(rows[:, 0], pos)
    assert sum(len(x) for x in seen) == 8 and len(phases) == 6


@pytest.mark.parametrize("fault", ["shape", "dtype", "alias", "finite", "background"])
def test_real_gather_rejects_bad_return(fault):
    a = np.zeros((1, 2101), dtype="<f8")
    if fault == "shape":
        a = a[:, :3].copy()
    if fault == "dtype":
        a = a.astype("f4")
    if fault == "alias":
        a = a.view()
    if fault == "finite":
        a[0, 0] = np.nan
    if fault == "background":
        a[0, 2100] = 1
    returned = Mock()
    with pytest.raises(ValueError):
        h.gather_real([0], lambda _: a, on_return=returned)
    returned.assert_not_called()


def test_generated_reader_remains_three_columns_and_rejects_real_mode():
    with pytest.raises(ValueError):
        GeneratedBackend(mode="real_hdf")
    with pytest.raises(ValueError):
        gather([0], lambda _: np.zeros((1, 2101), dtype="f8"))


def test_strict_four_outputs_owned_and_independent_reference():
    thresholds = np.array([0, 1, 2, 3], dtype="f8")
    features = np.zeros((4, 8), dtype="f4")
    features[:, 0] = [0, 1, 2, 3]
    model = SimpleNamespace(
        score=lambda x, feature_names: np.array(x[:, 0], dtype="f8", copy=True)
    )
    scores, masks = h.public_owned(model, features, thresholds, [])
    ref, rmasks = h.independent_reference(model, features, [3, 2, 1, 0], thresholds, [])
    assert scores.flags.owndata and masks.flags.owndata
    assert not np.diag(masks).any()
    assert masks.tolist() == [
        [False] * 4,
        [True, False, False, False],
        [True, True, False, False],
        [True, True, True, False],
    ]
    assert (
        ref.tobytes() == scores[::-1].tobytes()
        and rmasks.tobytes() == masks[::-1].tobytes()
    )
    features[:] = 100
    assert scores.tolist() == [0, 1, 2, 3]


def test_budget_fixed_work_and_no_renewal():
    b = h.Budget()
    for _phase in range(2):
        for m in range(1, 9):
            for _repeat in range(2):
                for stage in ("raw", "feature", "score"):
                    b.begin(stage, m)
                    b.finish()
                b.add("booleans", 4 * m)
            b.add("reference_calls")
            b.add("reference_rows", m)
            b.begin("score", m)
            b.finish()
            b.add("booleans", 4 * m)
    for _p in range(64):
        for stage in ("raw", "feature", "score"):
            b.begin(stage, 1)
            b.finish()
        b.add("booleans", 4)
        b.add("reference_calls")
        b.add("reference_rows", 1)
        b.begin("score", 1)
        b.finish()
        b.add("booleans", 4)
    assert [
        b.counts[k]
        for k in ("raw_calls", "raw_rows", "score_calls", "score_rows", "booleans")
    ] == [96, 208, 176, 344, 1376]
    with pytest.raises(ValueError):
        b.begin("raw", 1)


@pytest.mark.parametrize("stage", ["raw", "feature", "score"])
def test_stage_failure_keeps_inflight_unknown(stage):
    b = h.Budget()
    b.begin(stage, 8)
    assert b.started[stage + "_calls"] == 1 and b.returned[stage + "_calls"] == 0
    assert b.inflight == [stage, 8]
    with pytest.raises(ValueError):
        b.begin(stage, 1)


def test_gates_exact_two_raw_then_one_reference_every_shape():
    b = h.RealBackend.__new__(h.RealBackend)
    b.gate_digests = []
    trace = []
    b.read = lambda pos: (
        trace.append(("read", len(pos))) or np.zeros((len(pos), 2101), dtype="f8")
    )
    b.features = lambda rows: (
        trace.append(("features", len(rows))) or np.zeros((len(rows), 8), dtype="f4")
    )
    b.decisions = lambda f: (
        trace.append(("public", len(f)))
        or (np.zeros(len(f), dtype="f8"), np.zeros((len(f), 4), dtype=bool))
    )
    b.feature_parity = lambda p, f: trace.append(("parity", len(p)))
    b.reference = lambda p, s, m: trace.append(("reference", len(p))) or str(len(p))
    b.gates()
    assert trace == [
        op
        for m in range(1, 9)
        for op in [("read", m), ("features", m), ("public", m), ("parity", m)] * 2
        + [("reference", m)]
    ]
    assert b.gate_digests == list(map(str, range(1, 9)))


def test_closed_source_rejection_and_hash_without_operational_open():
    repo = Path("/private/tmp")
    for path in ("../escape", "/absolute"):
        with pytest.raises(ValueError):
            pilot54.fixed_path(repo, dict(path=path, bytes=1))
    fake = SimpleNamespace(open=lambda *_: io.BytesIO(b"owned"))
    with patch.object(pilot54, "fixed_path", return_value=fake):
        assert (
            pilot54.source_bytes(
                repo, dict(bytes=5, sha256=hashlib.sha256(b"owned").hexdigest())
            )
            == b"owned"
        )
        with pytest.raises(ValueError):
            pilot54.source_bytes(repo, dict(bytes=5, sha256="wrong"))
    with patch.object(Path, "is_symlink", return_value=True):
        with pytest.raises(ValueError):
            pilot54.fixed_path(repo, dict(path="x", bytes=1))


def test_entrypoint_parse_help_and_errors_do_not_import_backend(monkeypatch):
    import runpy
    import sys

    script = runpy.run_path("scripts/development_hdf_consumer_pilot.py")
    for args, exitcode in [
        (["--help"], 0),
        ([], 2),
        (["--run-pilot", "--root", "/wrong"], 2),
        (["--qualify-generated", "--run-pilot", "--root", "/wrong"], 2),
    ]:
        monkeypatch.setattr(sys, "argv", ["pilot", *args])
        with pytest.raises(SystemExit) as exc:
            script["main"]()
        assert exc.value.code == exitcode


def test_generated_api_has_no_operational_selector():
    import inspect

    from raregate.streaming.fixture import run_fixture

    assert "pilot" not in inspect.signature(run_fixture).parameters
    tree = ast.parse(Path("src/raregate/streaming/fixture.py").read_text())
    consumer = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_consumer"
    )
    # Both generated and real paths use the same FIFO/credit/record/consumer function.
    calls = [
        n.func.attr
        for n in ast.walk(consumer)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    ]
    for name in ("stage", "activate", "finish", "retain", "reference"):
        assert name in calls


def test_historical_512_record_and_descriptor_layout_unchanged():
    d = Descriptor(1, 0, 0, 100, 100)
    assert len(d.encode()) == 64 and Descriptor.decode(d.encode()) == d
    record = dict(
        run=1,
        k=0,
        prefix=0,
        cycle=0,
        phase=1,
        intended=100,
        status=5,
        reason=5,
        observed=200,
        detection=200,
    )
    blob = encode(record, "event")
    assert len(blob) == 512 and decode(blob, "event")["intended"] == 100


def test_after_drain_every_group_reference_precedes_post_gates(monkeypatch):
    backend = h.RealBackend.__new__(h.RealBackend)
    trace = []
    backend.clocks = SimpleNamespace(continuous=lambda: 1, service=lambda: 2)
    backend.retained = [
        ([0], np.zeros(1, dtype="f8"), np.zeros((1, 4), dtype=bool), dict(batch=i, m=1))
        for i in range(3)
    ]
    backend.checkpoint = lambda: None
    backend.reference = lambda p, s, m: trace.append("reference")
    backend.gate_digests = list(map(str, range(8)))
    backend.gates = lambda: (
        trace.append("post_gates"),
        backend.gate_digests.extend(list(map(str, range(8)))),
    )
    backend.initial_state = {}
    backend.state = lambda: {}
    backend.core = SimpleNamespace(effective_threads=lambda: {})
    backend.close_handle = lambda: trace.append("close")
    backend.spec = dict(lineage_roles=[])
    backend.entry = dict(name="pca-v1")
    backend.files = dict.fromkeys(
        [
            "membership",
            "golden",
            "transform",
            "pca-v1:model",
            "pca-v1:config",
            "pca-v1:calibration",
        ],
        {},
    )
    backend.repo = Path.cwd()
    backend.directory = Path.cwd()
    backend.budget = h.Budget()
    backend.threads_before = {}
    backend.hdf_metadata = {}
    backend.observations = {}
    monkeypatch.setattr(h, "source_bytes", lambda *_: b"")
    monkeypatch.setattr(
        quota, "CURRENT", SimpleNamespace(write_json=lambda *_: trace.append("report"))
    )
    records = []
    backend.finish(lambda b: records.append(dict(b)))
    assert trace == ["reference"] * 3 + ["post_gates", "close", "report"]
    assert [r["batch"] for r in records] == [0, 0, 1, 1, 2, 2]
    assert all(r.get("reference_rows") == 1 for r in records[1::2])
    assert backend.retained == []


def test_pre_growth_rejection_never_creates_or_overwrites():
    ledger = quota.Ledger(Path.cwd(), {"allowed": 3}, task="0054")
    with patch("os.open") as opened:
        with pytest.raises(quota.QuotaError):
            ledger.write_bytes(Path.cwd() / "allowed", b"four")
        with pytest.raises(quota.QuotaError):
            ledger.write_bytes(Path.cwd() / "escape", b"x")
        opened.assert_not_called()


def test_size_and_hardlink_rejection_before_source_open():
    import stat

    for links, size in [(2, 5), (1, 6)]:
        with (
            patch.object(Path, "is_symlink", return_value=False),
            patch.object(
                Path,
                "stat",
                return_value=SimpleNamespace(
                    st_mode=stat.S_IFREG, st_nlink=links, st_size=size
                ),
            ),
        ):
            with pytest.raises(ValueError):
                pilot54.fixed_path(Path.cwd(), dict(path="owned", bytes=5))


def test_checkpoint_failure_preserves_inflight_intent():
    backend = h.RealBackend.__new__(h.RealBackend)
    backend.budget = h.Budget()
    backend.checkpoint = Mock(side_effect=OSError("short publication"))
    backend.np = np
    backend.ids = np.arange(1024, dtype="i8")
    backend.dataset = Mock()
    with pytest.raises(OSError):
        backend.read([0])
    assert backend.budget.inflight == ["raw", 1]
    backend.dataset.__getitem__.assert_not_called() if hasattr(
        backend.dataset, "__getitem__"
    ) else None
    assert backend.budget.returned["raw_calls"] == 0


@pytest.mark.parametrize(
    "mode",
    ["normal", "report_stall", "failed_start", "finalizer_exit", "receipt_failure"],
)
def test_pilot_external_report_boundary_with_fake_program(monkeypatch, mode):
    import subprocess

    from raregate.streaming import supervision

    class Clock:
        t = 0

        def continuous(self):
            return self.t

        def observation(self):
            self.t += 100000000
            return self.t, self.t, 0

    c = Clock()
    events = []
    written = {}
    root = Path.cwd() / "data/task0054-validation/session-v1"
    spec = dict(
        software_prerequisites_passed=True,
        pilot_scope_authorized=True,
        full_study_execution_authorized=False,
        thread_environment={},
    )
    ledger = SimpleNamespace(
        task="0054",
        entries=pilot54.file_plan(),
        inventory=lambda: {},
        write_bytes=lambda p, b: written.update({p: b}),
    )

    def write(p, v):
        events.append(("write", c.t))
        if mode == "receipt_failure" and p.name == "observer.json":
            raise OSError("receipt")
        written[p] = v

    ledger.write_json = write

    class Receipt:
        def read_text(self):
            return json.dumps(dict(qualified=True, source_manifest=[]))

    class Process:
        pid = 123456
        polls = 0
        code = None

        def poll(self):
            self.polls += 1
            if mode not in ("report_stall", "failed_start") and self.polls == 3:
                written[root / "pilot/subject.json"] = dict(
                    qualified=mode != "finalizer_exit"
                )
                events.append(("final_report", c.t))
            if mode not in ("report_stall", "failed_start") and self.polls >= 4:
                self.code = 0 if mode != "finalizer_exit" else 1
            return self.code

        def wait(self, timeout=None):
            events.append(("reap", c.t))
            return self.code

    process = Process()

    def launch(*a, **kw):
        events.append(("launch", c.t))
        if mode == "failed_start":
            raise OSError("start")
        return process

    def cleanup(*a):
        events.append(("cleanup", c.t))
        return dict(
            subject_reaped=True,
            owned_group_absent=True,
            forced=mode == "report_stall",
            exitcode=process.code,
        )

    monkeypatch.setattr(quota, "activate", lambda _: ledger)
    monkeypatch.setattr(pilot54, "source_manifest", lambda _: [])
    monkeypatch.setattr(pilot54, "validate_spec", lambda *_: None)
    monkeypatch.setattr(Path, "glob", lambda *_: iter([Receipt()]))
    monkeypatch.setattr(Path, "mkdir", lambda *_a, **_k: None)
    monkeypatch.setattr(Path, "exists", lambda p: p in written)
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda p: json.dumps(spec if str(p).endswith(pilot54.CONFIG) else written[p]),
    )
    monkeypatch.setattr(supervision, "Clocks", lambda: c)
    monkeypatch.setattr(supervision, "own_rss", lambda: 1024)
    monkeypatch.setattr(subprocess, "Popen", launch)
    monkeypatch.setattr(pilot54.v2, "tree_cleanup", cleanup)
    monkeypatch.setattr(
        pilot54.v2,
        "read_heartbeat",
        lambda _: (
            b"LTH0053\0",
            (5 << 32) + 1,
            0 if mode == "report_stall" else c.t,
            1024,
            0,
            0,
            1024,
            0,
        ),
    )
    monkeypatch.setattr("time.sleep", lambda _: None)
    result = pilot54.observe_pilot(root)
    assert result["qualified"] == (mode == "normal")
    if mode != "failed_start":
        assert "cleanup" in [e[0] for e in events]
        assert result["subject_continuous_bracket_ns"][0] <= next(
            t for n, t in events if n == "launch"
        )
        assert result["subject_continuous_bracket_ns"][1] >= next(
            t for n, t in events if n == "cleanup"
        )
    if mode == "report_stall":
        assert "heartbeat" in result["problem"]
    if mode == "receipt_failure":
        assert root / "pilot/observer-emergency.txt" in written


def test_build_identity_matches_original_canonical_json_string():
    text = 'PyTorch built with:\n  CPU C++ flags "quoted"\n'
    expected = hashlib.sha256(
        json.dumps(
            text, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()
    assert h.canonical_build_hash(text) == expected
    assert h.canonical_build_hash(text) != hashlib.sha256(text.encode()).hexdigest()


def test_initialization_failure_diagnostics_cannot_veto_cleanup(monkeypatch):
    backend = SimpleNamespace(
        checkpoint=Mock(), phase="imports", budget=h.Budget(), observations={}
    )
    write = Mock()
    monkeypatch.setattr(quota, "CURRENT", SimpleNamespace(write_json=write))
    assert (
        h.record_initialization_failure(
            backend, Path.cwd() / "dummy", ValueError("build")
        )
        is None
    )
    assert write.call_args.args[1]["valid"] is False
    assert write.call_args.args[1]["budget"]["counts"]["raw_calls"] == 0
    write.side_effect = quota.QuotaError("full")
    assert (
        h.record_initialization_failure(
            backend, Path.cwd() / "dummy", ValueError("build")
        )
        == "QuotaError"
    )
