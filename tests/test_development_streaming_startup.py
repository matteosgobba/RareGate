"""Task0055 deterministic source-free tests, no native case or CPU model instantiation."""

import ast
import ctypes
import errno
import hashlib
import json
import os
import runpy
import struct
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from latenttrigger.streaming import cpu_runtime as cpu
from latenttrigger.streaming import quota
from latenttrigger.streaming import resources as r
from latenttrigger.streaming import startup55 as q


class Oracle:
    def __init__(self, values):
        self.values = iter(values)
        self.pids = []

    def __call__(self, pid):
        self.pids.append(pid)
        value = next(self.values)
        if isinstance(value, Exception):
            raise value
        # Independent OS-layout oracle: pack bytes at documented resident offset.
        buffer = bytearray(96)
        struct.pack_into("<Q", buffer, 8, max(0, value))
        return (
            r.interpret_record(96, 0, struct.unpack_from("<Q", buffer, 8)[0])
            if value >= 0
            else r.interpret_record(96, 0, value)
        )


def budget(
    values, monkeypatch, *, clock=lambda: 0, persist=lambda _: None, relationship=None
):
    monkeypatch.setattr(r, "own_rss", lambda: 20 * 1024**2)
    query = Oracle(values)
    relation = relationship or (
        lambda: dict(
            pid=12345,
            fd=9,
            owner_pid=os.getpid(),
            ownership="independently injected owned relationship",
        )
    )
    return r.TrackerBudget(
        query=query, relationship=relation, clock=clock, persist=persist
    ), query


def test_original_canonical_encoding_independent_expected():
    text = 'CPU flags "quoted"\n'
    expected_bytes = b'"CPU flags \\"quoted\\"\\n"'
    assert json.dumps(text, separators=(",", ":")).encode() == expected_bytes
    assert cpu.canonical_build_hash(text) == hashlib.sha256(expected_bytes).hexdigest()
    assert cpu.canonical_build_hash(text) != hashlib.sha256(text.encode()).hexdigest()
    with pytest.raises(ValueError):
        cpu.RuntimePolicy(expected_build_sha256="new").validate()


def test_OS_structure_size_offset_signed_fields_and_units():
    assert (
        ctypes.sizeof(r.ProcTaskInfo) == 96 and r.ProcTaskInfo.resident_size.offset == 8
    )
    raw = bytearray(96)
    struct.pack_into("<Q", raw, 8, 987654321)
    struct.pack_into("<i", raw, 48, -7)
    value = r.ProcTaskInfo.from_buffer_copy(raw)
    assert value.resident_size == 987654321 and value.policy == -7
    observed = r.interpret_record(96, 0, value.resident_size)
    assert observed["rss_bytes"] == 987654321 and observed["units"] == "bytes"


@pytest.mark.parametrize(
    "length,error,resident,state",
    [
        (0, errno.ESRCH, 0, "exited"),
        (48, 0, 123, "query_error"),
        (-1, errno.EACCES, 0, "query_error"),
        (96, errno.EIO, 123, "query_error"),
        (96, 0, -1, "query_error"),
        (96, 0, 0, "startup_pending"),
        (96, 0, 2**40, "observed"),
    ],
)
def test_typed_OS_results_preserve_raw_values(length, error, resident, state):
    out = r.interpret_record(length, error, resident)
    assert (
        out["state"] == state
        and out["returned_length"] == length
        and out["errno"] == error
        and out["raw_resident_bytes"] == resident
    )
    assert (
        out["rss_bytes"] is None
        if state != "observed"
        else out["rss_bytes"] == resident
    )


def test_joint_policy_reallocation_and_oversize_evidence(monkeypatch):
    b, _ = budget([30 * 1024**2], monkeypatch)
    value = b.observe()
    assert value["joint_conservative_bytes"] == 50 * 1024**2
    assert value["rss_bytes"] > 16 * 1024**2  # old partition not declared passed
    b, _ = budget([70 * 1024**2], monkeypatch)
    with pytest.raises(r.ResourceFailure) as e:
        b.observe()
    assert e.value.evidence["observation"]["rss_bytes"] == 70 * 1024**2
    assert e.value.evidence["observation"]["joint_conservative_bytes"] == 90 * 1024**2
    with pytest.raises(ValueError):
        r.ResourcePolicy(inner_tracker_bytes=81 * 1024**2).validate()


@pytest.mark.parametrize(
    "pid,owner,fd",
    [
        (None, None, 9),
        (-1, "self", 9),
        (True, "self", 9),
        ("x", "self", 9),
        (os.getpid(), "self", 9),
        (12345, -999, 9),
        (12345, "self", None),
    ],
)
def test_ownership_missing_PID_never_queries_arbitrary_process(
    monkeypatch, pid, owner, fd
):
    def relation():
        return dict(
            pid=pid, owner_pid=os.getpid() if owner in (None, "self") else owner, fd=fd
        )

    b, oracle = budget([], monkeypatch, relationship=relation)
    with pytest.raises(r.ResourceFailure):
        b.observe()
    assert oracle.pids == []
    assert b.last["rss_bytes"] is None


def test_not_started_is_unknown_not_measured_zero(monkeypatch):
    b, _ = budget(
        [],
        monkeypatch,
        relationship=lambda: dict(pid=None, owner_pid=os.getpid(), fd=None),
    )
    value = b.observe(required=False)
    assert (
        value["state"] == "not_started"
        and value["rss_bytes"] is None
        and value["joint_conservative_bytes"] is None
    )
    assert value["charge_is_reservation_without_measurement"]


@pytest.mark.parametrize("clock_value", [None, -1, True])
def test_unknown_clock_is_not_valid_zero(monkeypatch, clock_value):
    b, oracle = budget([], monkeypatch, clock=lambda: clock_value)
    with pytest.raises(r.ResourceFailure):
        b.observe()
    assert not oracle.pids and b.last["state"] == "query_error"


def test_valid_zero_clock_and_query_error_evidence(monkeypatch):
    b, _ = budget([8 * 1024**2], monkeypatch)
    assert b.observe()["monotonic_ns"] == 0
    b, _ = budget([OSError(errno.EPERM, "oracle error")], monkeypatch)
    with pytest.raises(r.ResourceFailure) as e:
        b.observe()
    assert e.value.evidence["observation"]["errno"] == errno.EPERM


class Clock:
    def __init__(self):
        self.t = 0

    def continuous(self):
        return self.t

    def observation(self):
        return self.t, self.t, 0

    def wait(self, s):
        self.t += round(s * 1e9)


def test_startup_pending_poll_then_observed_before_readiness(monkeypatch):
    c = Clock()
    b, _ = budget([0, 0, 1024], monkeypatch, clock=c.continuous)
    monitor = Mock()
    value = b.await_ready(c, c.wait, monitor)
    assert value["state"] == "observed" and c.t == 10000000 and b.pending_count == 2
    assert monitor.observe.call_count >= 3
    assert all(x["rss_bytes"] is None for x in b.samples[:2])


def test_startup_deadline_and_post_ready_loss_fail_closed(monkeypatch):
    c = Clock()
    b, _ = budget([0] * 100, monkeypatch, clock=c.continuous)
    with pytest.raises(r.ResourceFailure):
        b.await_ready(c, c.wait, Mock())
    assert c.t == 250000000 and b.first_failure["elapsed_ns"] == 250000000
    b, _ = budget([1024, 0], monkeypatch)
    b.observe()
    with pytest.raises(r.ResourceFailure):
        b.observe()
    assert b.last["raw_resident_bytes"] == 0 and b.last["rss_bytes"] is None


def test_primary_resource_value_survives_report_failure(monkeypatch):
    b, _ = budget(
        [70 * 1024**2], monkeypatch, persist=Mock(side_effect=OSError("report failed"))
    )
    with pytest.raises(r.ResourceFailure) as e:
        b.observe()
    assert e.value.evidence["observation"]["rss_bytes"] == 70 * 1024**2
    assert b.last["report_failure"]["message"] == "report failed"


def fake_runtime(
    monkeypatch, *, mismatch=False, fail_import=None, publish=lambda _: None
):
    trace = []
    limiter = SimpleNamespace(restore_original_limits=lambda: trace.append("restore"))
    core = SimpleNamespace(
        configure_threads=lambda _: (limiter, dict(intra=1, inter=1)),
        effective_threads=lambda: dict(intra=1, inter=1),
    )
    modules = {
        "numpy": SimpleNamespace(__version__="fake-numpy"),
        "torch": SimpleNamespace(
            __version__="fake-torch",
            __config__=SimpleNamespace(show=lambda: "fake build"),
        ),
        "latenttrigger.benchmarks.core": core,
        "h5py": SimpleNamespace(
            __version__="fake-hdf", version=SimpleNamespace(hdf5_version="fake")
        ),
        "hdf5plugin": SimpleNamespace(__version__="fake-plugin"),
    }

    def importer(name):
        trace.append(name)
        if name == fail_import:
            raise ImportError("oracle:" + name)
        return modules[name]

    if not mismatch:
        monkeypatch.setattr(cpu, "canonical_build_hash", lambda _: cpu.EXPECTED_BUILD)
    monkeypatch.setattr(r, "query_pid", lambda _: dict(state="observed", rss_bytes=123))
    session = cpu.RuntimeSession(
        publish=publish, clock=lambda: 0, import_module=importer
    )
    return session, trace


def test_runtime_common_function_payload_not_armed_and_cleanup(monkeypatch):
    session, trace = fake_runtime(monkeypatch)
    session.initialize()
    assert (
        session.evidence["boundary"] == "payload_not_armed"
        and not session.evidence["payload_armed"]
    )
    assert session.evidence["build"]["torch_version"] == "fake-torch"
    assert session.close() and session.close() and trace.count("restore") == 1
    obj = cpu.RuntimeSession.__new__(cpu.RuntimeSession)
    assert obj.close()


def test_runtime_build_mismatch_preserves_actual_expected_and_raw(monkeypatch):
    session, trace = fake_runtime(monkeypatch, mismatch=True)
    with pytest.raises(cpu.InitializationFailure) as e:
        session.initialize()
    build = e.value.evidence["build"]
    assert build["expected_canonical_sha256"] == cpu.EXPECTED_BUILD
    assert (
        build["actual_canonical_sha256"] == hashlib.sha256(b'"fake build"').hexdigest()
    )
    assert build["raw_text_sha256"] == hashlib.sha256(b"fake build").hexdigest()
    assert trace.count("restore") == 1 and e.value.evidence["primary_failure"]["frames"]


@pytest.mark.parametrize(
    "module", ["numpy", "torch", "latenttrigger.benchmarks.core", "h5py", "hdf5plugin"]
)
def test_real_initialization_import_boundary_failure_is_retained(monkeypatch, module):
    session, trace = fake_runtime(monkeypatch, fail_import=module)
    with pytest.raises(cpu.InitializationFailure) as e:
        session.initialize()
    assert e.value.evidence["primary_failure"]["type"] == "ImportError"
    assert module in trace and not e.value.evidence["payload_armed"]
    assert trace.count("restore") == int(module in ("h5py", "hdf5plugin"))


@pytest.mark.parametrize(
    "step",
    [
        "thread_environment_before_imports",
        "import_numpy",
        "import_torch",
        "import_unchanged_CPU_helpers",
        "configure_and_query_threads",
        "canonical_build_identity",
        "rounding_mode",
        "import_HDF_bindings_plugins_without_open",
        "final_effective_thread_query",
        "payload_not_armed",
    ],
)
def test_failure_before_every_startup_step_cleanup_and_report_fields(monkeypatch, step):
    once = [False]

    def publish(value):
        if value["last_step"] == step and not once[0]:
            once[0] = True
            raise OSError("injected report")

    session, trace = fake_runtime(monkeypatch, publish=publish)
    with pytest.raises(cpu.InitializationFailure) as e:
        session.initialize()
    assert e.value.evidence["last_step"] == step
    assert e.value.evidence["primary_failure"]["message"] == "injected report"
    assert e.value.evidence["report_failure"]["message"] == "injected report"
    assert not session.evidence["payload_armed"]


def test_denial_covers_all17inert_paths_and_other_production_roots(monkeypatch):
    hooks = []
    monkeypatch.setattr(sys, "addaudithook", hooks.append)
    repo = Path.cwd()
    owned = repo / q.ROOT
    counts = q.install_payload_denial(repo, owned)
    config = json.loads(
        (repo / "configs/streaming/development_hdf_consumer_pilot_v1.json").read_text()
    )
    for item in config["allowed_files"]:
        with pytest.raises(PermissionError):
            hooks[0]("open", (str(repo / item["path"]), "r", 0))
    for name in ("data/other.npy", "artifacts/other.json", "results/other.npy"):
        with pytest.raises(PermissionError):
            hooks[0]("open", (str(repo / name), "r", 0))
    hooks[0]("open", (str(owned / "own.json"), "r", 0))
    hooks[0]("open", (str(repo / "src/code.py"), "r", 0))
    assert (
        counts["denied_open_attempts"] == 20
        and counts["production_open_successes"] == 0
    )


def test_help_malformed_and_generic_guard_not_task_routed(monkeypatch):
    script = runpy.run_path(q.SCRIPT)
    for args, code in [
        (["--help"], 0),
        ([], 2),
        (["--qualify-source-free", "--root", "/wrong"], 2),
        (["--run-pilot", "--root", "/wrong"], 2),
    ]:
        monkeypatch.setattr(sys, "argv", ["startup", *args])
        with pytest.raises(SystemExit) as e:
            script["main"]()
        assert e.value.code == code
    fixture = ast.parse(Path("src/latenttrigger/streaming/fixture.py").read_text())
    core = next(
        n
        for n in fixture.body
        if isinstance(n, ast.FunctionDef) and n.name == "_run_pipeline"
    )
    calls = [ast.unparse(n.func) for n in ast.walk(core) if isinstance(n, ast.Call)]
    assert calls.index("resources.await_ready") < calls.index("producer.start")
    text = Path("src/latenttrigger/streaming/validation_v2.py").read_text()
    assert 'quota.CURRENT.task == "0054"' not in text
    assert "heartbeat_joint(peaks, POLICY)" in text
    runtime_source = Path("src/latenttrigger/streaming/cpu_runtime.py").read_text()
    assert (
        "source_bytes(" not in runtime_source
        and "np.load(" not in runtime_source
        and ".score(" not in runtime_source
    )


def test_global_plan_and_finite_matrix():
    files = q.file_plan()
    assert sum(files.values()) <= 32 * 1024**2 and len(files) <= 512
    assert sum(n for _, n, _ in q.v2.CASES) == 560
    assert len(q.BOOTSTRAPS) == 2 and len(q.v2.CASES) == 12
    assert "suite-2/14-runtime-ae-metadata/runtime.bin" in files
    assert len([k for k in files if "/attempt-" in k]) == 28
    with pytest.raises(quota.QuotaError):
        quota.Ledger(Path.cwd(), files)


@pytest.mark.parametrize("mode", ["normal", "missing_subject", "receipt_failure"])
def test_outer_missing_final_report_regression_retains_receipt_and_reaping(
    monkeypatch, mode
):
    root = Path.cwd() / q.ROOT
    directory = root / "suite-1"
    written = {}
    events = []

    class ObservedClock:
        t = 0

        def continuous(self):
            return self.t

        def observation(self):
            self.t += 100000000
            return self.t, self.t, 0

    clock = ObservedClock()

    class Process:
        pid = 424242
        code = None
        polls = 0

        def poll(self):
            self.polls += 1
            if self.polls == 3 and mode != "missing_subject":
                written[directory / "subject.json"] = dict(
                    qualified=True, rows=[], tracker={}, primary_failure=None
                )
                events.append(("report", clock.t))
            if self.polls >= 4:
                self.code = 0
            return self.code

        def wait(self, timeout=None):
            events.append(("reap", clock.t))
            return self.code

    def write(path, value):
        if mode == "receipt_failure" and path.name == "observer.json":
            raise OSError("receipt failed")
        written[path] = value

    ledger = SimpleNamespace(
        inventory=lambda: {},
        write_json=write,
        write_bytes=lambda p, b: written.update({p: b}),
    )
    monkeypatch.setattr(q, "Clocks", lambda: clock)
    monkeypatch.setattr(q, "prepare", lambda *_: (ledger, directory, []))
    monkeypatch.setattr(q, "own_rss", lambda: 1024)
    monkeypatch.setattr(q.subprocess, "Popen", lambda *_a, **_k: Process())
    monkeypatch.setattr(q.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        q.v2,
        "tree_cleanup",
        lambda *_: dict(
            subject_reaped=True, owned_group_absent=True, forced=False, exitcode=0
        ),
    )
    monkeypatch.setattr(
        q.v2,
        "read_heartbeat",
        lambda _: (b"LTH0053\0", 1, clock.t, 1024, 0, 0, 1024, 0),
    )
    monkeypatch.setattr(Path, "exists", lambda p: p in written)
    monkeypatch.setattr(Path, "read_text", lambda p: json.dumps(written[p]))
    result = q.observe(root, 1)
    assert result["qualified"] == (mode == "normal")
    assert result["cleanup"]["subject_reaped"] and "reap" in [n for n, _ in events]
    if mode == "missing_subject":
        assert "missing after exit/reap" in result["missing_subject_report"]
    if mode == "receipt_failure":
        assert directory / "observer-emergency.txt" in written


def test_late_positive_tracker_never_advertises_ready(monkeypatch):
    clock = Clock()
    b, _ = budget([1024], monkeypatch, clock=clock.continuous)

    def late(pid):
        clock.t = 300000000
        return dict(state="observed", rss_bytes=1024)

    b.query = late
    with pytest.raises(r.ResourceFailure) as exc:
        b.await_ready(clock, clock.wait, Mock())
    assert exc.value.evidence["elapsed_ns"] == 300000000
    assert exc.value.evidence["observation"]["rss_bytes"] == 1024


@pytest.mark.parametrize("state", ["unsupported", "exited", "query_error"])
def test_unavailable_tracker_is_not_silent_or_zero(monkeypatch, state):
    b, _ = budget([], monkeypatch)
    b.query = lambda _: dict(state=state, rss_bytes=None, reason="oracle refusal")
    with pytest.raises(r.ResourceFailure) as exc:
        b.observe()
    assert exc.value.evidence["observation"]["reason"] == "oracle refusal"
    assert exc.value.evidence["observation"]["rss_bytes"] is None


def test_joint80MiB_equality_is_allowed(monkeypatch):
    b, _ = budget([60 * 1024**2], monkeypatch)
    assert b.observe()["joint_conservative_bytes"] == 80 * 1024**2


def test_runtime_primary_report_and_cleanup_failures_are_separate(monkeypatch):
    session, trace = fake_runtime(monkeypatch, mismatch=True)

    def restore():
        raise OSError("restore failed")

    session.import_module("latenttrigger.benchmarks.core").configure_threads = (
        lambda _: (SimpleNamespace(restore_original_limits=restore), {})
    )

    def publish(value):
        if value["primary_failure"] is not None:
            raise OSError("failure report failed")

    session.publish = publish
    with pytest.raises(cpu.InitializationFailure) as exc:
        session.initialize()
    evidence = exc.value.evidence
    assert (
        evidence["primary_failure"]["message"]
        == "Unsupported actual Torch build identity"
    )
    assert evidence["report_failure"]["message"] == "failure report failed"
    assert evidence["cleanup_failures"][0]["message"] == "restore failed"


def test_journal_short_write_and_partial_constructor_cleanup(monkeypatch):
    journal = q.Journal(Path("/private/tmp/never-opened"))
    monkeypatch.setattr(quota, "open_file", lambda *_: 9876)
    monkeypatch.setattr(quota, "truncate", lambda *_: None)
    monkeypatch.setattr(quota, "pwrite", lambda *_: 1)
    close = Mock()
    monkeypatch.setattr(quota, "close", close)
    with pytest.raises(ValueError):
        journal.write(dict(state="query_error", rss_bytes=None))
    journal.close()
    journal.close()
    close.assert_called_once_with(9876)
    q.Journal(Path("/private/tmp/never-opened")).close()


def test_consumer_wrapper_preserves_runtime_primary_when_checkpoint_fails(monkeypatch):
    from latenttrigger.streaming.hdf_consumer import record_initialization_failure

    evidence = dict(
        last_step="import_torch",
        primary_failure=dict(type="ImportError", message="original runtime import"),
        build=dict(expected="pin", actual="mismatch"),
        cleanup_failures=[],
    )
    backend = SimpleNamespace(
        runtime=SimpleNamespace(evidence=evidence),
        phase="imports",
        payload_armed=False,
        checkpoint=Mock(side_effect=OSError("checkpoint failed")),
    )
    writer = Mock()
    monkeypatch.setattr(quota, "CURRENT", SimpleNamespace(write_json=writer))
    assert (
        record_initialization_failure(
            backend, Path("/private/tmp/not-created"), ImportError("original")
        )
        is None
    )
    saved = writer.call_args.args[1]
    assert (
        saved["runtime"] == evidence
        and saved["primary_failure"]["type"] == "ImportError"
    )
    assert saved["report_failure"]["message"] == "checkpoint failed"
    assert not saved["payload_armed"] and saved["budget"] is None


def test_consumer_wrapper_partial_constructor_and_report_failure_independent(
    monkeypatch,
):
    from latenttrigger.streaming.hdf_consumer import record_initialization_failure

    writer = Mock(side_effect=quota.QuotaError("full"))
    monkeypatch.setattr(quota, "CURRENT", SimpleNamespace(write_json=writer))
    assert (
        record_initialization_failure(
            SimpleNamespace(), Path("/private/tmp/not-created"), ValueError("original")
        )
        == "QuotaError"
    )
    saved = writer.call_args.args[1]
    assert (
        saved["phase"] == "partial_constructor"
        and saved["primary_failure"]["message"] == "original"
    )
