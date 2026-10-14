"""Local synthetic transport/preservation/lifecycle and structural-only fixtures."""

import hashlib
import http.client
import io
import json
import os
import socket
import ssl
import subprocess
import sys
import time
from datetime import UTC, datetime
from email.message import Message
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import h5py
import pytest
from test_frozen_cpu_benchmark import sample

from latenttrigger.benchmarks import protocol as p
from latenttrigger.data import three_prong_acquisition as c
from latenttrigger.data import three_prong_acquisition_protocol as q
from latenttrigger.data import three_prong_acquisition_worker as worker
from latenttrigger.data.three_prong_acquisition_smoke import Response, toy_payload
from latenttrigger.data.three_prong_structure import inspect
from latenttrigger.data.three_prong_transport import (
    NoRedirect,
    ResponseFault,
    Transfer,
    hash_bytes,
    retry_delay,
    retryable,
)
from latenttrigger.evaluation import guarded
from latenttrigger.evaluation.guard import Guard


class Clock:
    def __init__(self):
        self.tick = 0

    def __call__(self):
        return self.tick

    def sleep(self, seconds):
        self.tick += seconds


@pytest.fixture
def setup(tmp_path):
    clock = Clock()
    body = b"abcdefghij"
    source = dict(
        url="https://example.invalid/toy",
        expected_size=len(body),
        expected_checksum=hashlib.md5(body, usedforsecurity=False).hexdigest(),
    )
    policy = dict(
        max_payload_requests=3,
        retry_backoff_seconds=[5, 15],
        socket_timeout_seconds=30,
        buffer_bytes=2,
        checkpoint_bytes=4,
        checkpoint_seconds=5,
        progress_seconds=15,
        checkpoint_journal_bytes=8 * 2**20,
        minimum_request_slack_seconds=2,
    )
    directory = tmp_path / "owned"
    directory.mkdir()
    return body, source, policy, directory, tmp_path / "progress.json", clock


def transfer(setup, responses):
    body, source, policy, directory, progress, clock = setup
    queue = iter(responses)
    seen = []

    def opening(request, timeout):
        seen.append((request, timeout))
        value = next(queue)
        if isinstance(value, Exception):
            raise value
        return value

    route = Transfer(
        source,
        policy,
        directory,
        progress,
        open_response=opening,
        clock=clock,
        sleep=clock.sleep,
    )
    return route, seen


class Interrupted(Response):
    def __init__(self, prefix, source, *, error=None, extra=None):
        super().__init__(prefix, source["url"], extra=extra)
        self.headers.replace_header("Content-Length", str(source["expected_size"]))
        self.error = error or TimeoutError("Synthetic interrupted network")

    def read(self, size):
        result = super().read(size)
        if not result:
            raise self.error
        return result


def test_complete_transfer_checkpoint_and_byte_integrity(setup):
    body, source, _, directory, progress, clock = setup
    route, seen = transfer(setup, [Response(body, source["url"])])
    path = route.run(100)
    assert hash_bytes(path)["MD5"] == source["expected_checksum"]
    state = p.read(progress)
    assert (
        state["received_bytes"]
        == state["written_bytes"]
        == state["durably_checkpointed_bytes"]
        == len(body)
    )
    assert len(seen) == 1 and clock() == 0
    rows = [
        json.loads(line)
        for line in progress.with_name("checkpoints.jsonl").read_text().splitlines()
    ]
    assert all(r["durable"] <= r["written"] <= r["received"] for r in rows)
    assert rows[-1]["current_file"]["durable_prefix_SHA256"] == p.file_hash(path)
    assert list(directory.iterdir()) == [path]


def test_valid_206_continuation_and_strong_if_range(setup):
    body, source, _, _, progress, clock = setup
    prefix = Interrupted(body[:4], source, extra={"ETag": '"frozen"'})
    resumed = Response(
        body[4:],
        source["url"],
        status=206,
        extra={"Content-Range": "bytes 4-9/10", "ETag": '"frozen"'},
    )
    route, seen = transfer(setup, [prefix, resumed])
    path = route.run(100)
    assert path.read_bytes() == body and len(seen) == 2 and clock() == 5
    assert seen[1][0].get_header("Range") == "bytes=4-"
    assert seen[1][0].get_header("If-range") == '"frozen"'
    assert p.read(progress)["continuations"] == 1


@pytest.mark.parametrize("tag", [None, 'W/"weak"'])
def test_missing_weak_validator_not_sent_as_if_range(setup, tag):
    body, source, _, _, progress, _ = setup
    extra = {"ETag": tag} if tag else {}
    route, seen = transfer(
        setup,
        [
            Interrupted(body[:4], source, extra=extra),
            Response(
                body[4:],
                source["url"],
                status=206,
                extra={"Content-Range": "bytes 4-9/10", **extra},
            ),
        ],
    )
    assert route.run(100).read_bytes() == body
    assert seen[1][0].get_header("If-range") is None
    assert p.read(progress)["requests"][-1]["validator_assurance"].startswith(
        "weak_or_missing"
    )


def test_200_ignored_range_restarts_and_preserves_prefix(setup):
    body, source, _, directory, progress, _ = setup
    route, seen = transfer(
        setup, [Interrupted(body[:4], source), Response(body, source["url"])]
    )
    path = route.run(100)
    assert path.name == "payload-2.part" and path.read_bytes() == body
    assert (directory / "payload-1.part").read_bytes() == body[:4]
    state = p.read(progress)
    assert state["restarts"] == 1 and state["continuations"] == 0
    assert (
        state["written_bytes"] == state["durably_checkpointed_bytes"] == 14
        and len(seen) == 2
    )


@pytest.mark.parametrize(
    "value",
    [
        "bytes 3-9/10",
        "bytes 4-8/10",
        "bytes 4-9/11",
        "bytes */10",
        "bytes 4-9/*",
        "garbage",
    ],
)
def test_invalid_range_preserves_without_retry(setup, value):
    body, source, _, directory, progress, _ = setup
    route, seen = transfer(
        setup,
        [
            Interrupted(body[:4], source),
            Response(
                body[4:], source["url"], status=206, extra={"Content-Range": value}
            ),
        ],
    )
    with pytest.raises(ResponseFault):
        route.run(100)
    assert len(seen) == 2 and (directory / "payload-1.part").read_bytes() == body[:4]
    assert p.read(progress)["status"] == "failed_preserved"


@pytest.mark.parametrize(
    "extra", [{"ETag": '"changed"'}, {}, {"Last-Modified": "new", "ETag": '"old"'}]
)
def test_changed_or_missing_strong_validator_refuses(setup, extra):
    body, source, _, directory, _, _ = setup
    route, seen = transfer(
        setup,
        [
            Interrupted(
                body[:4], source, extra={"ETag": '"old"', "Last-Modified": "old"}
            ),
            Response(
                body[4:],
                source["url"],
                status=206,
                extra={"Content-Range": "bytes 4-9/10", **extra},
            ),
        ],
    )
    with pytest.raises(ResponseFault):
        route.run(100)
    assert len(seen) == 2 and (directory / "payload-1.part").stat().st_size == 4


@pytest.mark.parametrize("code", [408, 429, 500, 503, 599])
def test_retryable_http_then_success(setup, code):
    body, source, _, _, progress, clock = setup
    h = Message()
    h["Retry-After"] = "7"
    failure = HTTPError(source["url"], code, "toy", h, io.BytesIO())
    route, seen = transfer(setup, [failure, Response(body, source["url"])])
    assert route.run(100).read_bytes() == body and len(seen) == 2 and clock() == 7
    assert p.read(progress)["waits"][0]["completed"]


@pytest.mark.parametrize("code", [301, 403, 404, 416])
def test_nonretryable_http_retains_empty_owned_file(setup, code):
    _, source, _, directory, _, _ = setup
    failure = HTTPError(source["url"], code, "toy", Message(), io.BytesIO())
    route, seen = transfer(setup, [failure])
    with pytest.raises(HTTPError):
        route.run(100)
    assert len(seen) == 1 and (directory / "payload-1.part").exists()


def test_retry_budget_backoffs_share_original_deadline(setup):
    _, _, _, directory, progress, clock = setup
    route, seen = transfer(
        setup, [TimeoutError("1"), TimeoutError("2"), TimeoutError("3")]
    )
    with pytest.raises(TimeoutError):
        route.run(100)
    assert len(seen) == 3 and clock() == 20
    assert [r["seconds"] for r in p.read(progress)["waits"]] == [5, 15]
    assert len(list(directory.iterdir())) == 1


@pytest.mark.parametrize("remaining", [5, 7, 19])
def test_wait_or_retry_after_cannot_extend_deadline(setup, remaining):
    _, source, _, _, progress, _ = setup
    h = Message()
    h["Retry-After"] = "20"
    route, seen = transfer(
        setup, [HTTPError(source["url"], 429, "toy", h, io.BytesIO())]
    )
    with pytest.raises(TimeoutError, match="original deadline"):
        route.run(remaining)
    assert len(seen) == 1 and p.read(progress)["status"] == "failed_preserved"


@pytest.mark.parametrize(
    "value", ["bad", "-2", "100000000000", "Fri, 31 Dec 1999 23:59:59"]
)
def test_invalid_retry_after_refuses(value):
    h = Message()
    h["Retry-After"] = value
    with pytest.raises(ResponseFault):
        retry_delay(HTTPError("toy", 503, "toy", h, io.BytesIO()), 1, [5, 15])


def test_retry_after_http_date():
    h = Message()
    h["Retry-After"] = "Sun, 11 Oct 2026 10:00:20 GMT"
    assert (
        retry_delay(
            HTTPError("toy", 503, "toy", h, io.BytesIO()),
            1,
            [5, 15],
            lambda: datetime(2026, 10, 11, 10, 0, tzinfo=UTC),
        )
        == 20
    )


@pytest.mark.parametrize(
    "error,expected",
    [
        (URLError(socket.gaierror(socket.EAI_AGAIN, "toy")), True),
        (URLError(socket.gaierror(socket.EAI_NONAME, "toy")), False),
        (URLError(ssl.SSLCertVerificationError("toy")), False),
        (http.client.RemoteDisconnected("toy"), True),
        (ResponseFault("toy"), False),
        (OSError("disk"), False),
    ],
)
def test_specific_transient_conditions_only(error, expected):
    assert retryable(error) is expected


def test_truncated_eof_recovers_prefix(setup):
    body, source, _, _, _, _ = setup
    response = Response(body[:4], source["url"])
    response.headers.replace_header("Content-Length", "10")
    route, _ = transfer(
        setup,
        [
            response,
            Response(
                body[4:],
                source["url"],
                status=206,
                extra={"Content-Range": "bytes 4-9/10"},
            ),
        ],
    )
    assert route.run(100).read_bytes() == body


def test_incomplete_read_received_partial_is_preserved(setup):
    body, source, _, _, progress, _ = setup

    class Incomplete(Response):
        def read(self, size):
            raise http.client.IncompleteRead(body[:4], 6)

    first = Incomplete(body, source["url"])
    route, _ = transfer(
        setup,
        [
            first,
            Response(
                body[4:],
                source["url"],
                status=206,
                extra={"Content-Range": "bytes 4-9/10"},
            ),
        ],
    )
    assert route.run(100).read_bytes() == body
    assert p.read(progress)["received_bytes"] == 10


def test_oversized_response_never_writes_extra(setup):
    body, source, _, directory, progress, _ = setup
    response = Response(body + b"xx", source["url"])
    response.headers.replace_header("Content-Length", "10")
    route, seen = transfer(setup, [response])
    with pytest.raises(ResponseFault, match="Oversized"):
        route.run(100)
    state = p.read(progress)
    assert len(seen) == 1 and state["received_bytes"] == 12
    assert state["written_bytes"] == state["durably_checkpointed_bytes"] == 10
    assert (directory / "payload-1.part").read_bytes() == body


@pytest.mark.parametrize(
    "change", ["url", "encoding", "length", "duplicate", "unsolicited206", "entity_tag"]
)
def test_identity_and_malformed_response_no_retry(setup, change):
    body, source, _, _, _, _ = setup
    r = Response(body, source["url"])
    if change == "url":
        r.url = "https://example.invalid/other"
    if change == "encoding":
        r.headers["Content-Encoding"] = "gzip"
    if change == "length":
        r.headers.replace_header("Content-Length", "9")
    if change == "duplicate":
        r.headers["Content-Length"] = "10"
    if change == "unsolicited206":
        r.status = 206
    if change == "entity_tag":
        r.headers["ETag"] = "malformed"
    route, seen = transfer(setup, [r])
    with pytest.raises(ResponseFault):
        route.run(100)
    assert len(seen) == 1


def test_redirect_never_followed():
    with pytest.raises(ResponseFault, match="Redirect refused"):
        NoRedirect().redirect_request(
            None, None, 302, "toy", Message(), "https://other.invalid"
        )


def test_foreign_owned_filename_never_overwritten(setup):
    body, source, _, directory, _, _ = setup
    target = directory / "payload-1.part"
    target.write_bytes(b"foreign")
    route, seen = transfer(setup, [Response(body, source["url"])])
    with pytest.raises(FileExistsError):
        route.run(100)
    assert target.read_bytes() == b"foreign" and seen == []


def test_interrupted_write_keeps_uncertainty_and_durable_prefix(setup):
    body, source, _, directory, progress, _ = setup
    route, _ = transfer(setup, [Response(body, source["url"])])
    original = route.owned_file

    class BrokenWrite:
        def __init__(self, inner):
            self.inner = inner

        @property
        def closed(self):
            return self.inner.closed

        def write(self, value):
            self.inner.write(value[:1])
            raise OSError("synthetic uncertain write")

        def flush(self):
            self.inner.flush()

        def fileno(self):
            return self.inner.fileno()

        def close(self):
            self.inner.close()

    def replace(attempt):
        path = original(attempt)
        route.file = BrokenWrite(route.file)
        return path

    route.owned_file = replace
    with pytest.raises(OSError):
        route.run(100)
    state = p.read(progress)
    assert (
        state["received_bytes"] == 2
        and state["written_bytes"] == state["durably_checkpointed_bytes"] == 0
    )
    assert (
        state["inflight"] is not None
        and (directory / "payload-1.part").stat().st_size == 1
    )


def test_checkpoint_journal_exhaustion_keeps_files(setup):
    body, source, policy, directory, progress, _ = setup
    policy["checkpoint_journal_bytes"] = 2500
    route, _ = transfer(setup, [Response(body, source["url"])])
    with pytest.raises(ResponseFault, match="journal"):
        route.run(100)
    assert list(directory.iterdir()) and progress.exists()


def test_structural_inspection_reads_no_dataset_or_axes(tmp_path, monkeypatch):
    path = tmp_path / "toy.h5"
    toy_payload(path)
    monkeypatch.setattr(
        h5py.Dataset,
        "__getitem__",
        lambda *args: pytest.fail("Dataset numeric read forbidden"),
    )
    monkeypatch.setattr(
        h5py.Dataset,
        "read_direct",
        lambda *args: pytest.fail("Dataset numeric read forbidden"),
    )
    result = inspect(path)
    assert result["status"] == "compatible_looking_structural_metadata_only"
    assert result["dataset_value_reads"] == 0 and not result["numerical_custody_passed"]


@pytest.mark.parametrize(
    "change", ["dtype", "table", "mixed", "external", "soft", "vlen_attr"]
)
def test_structural_unsupported_or_attribute_skipped(tmp_path, change):
    path = tmp_path / "toy.h5"
    toy_payload(path)
    with h5py.File(path, "a") as handle:
        if change == "dtype":
            del handle["/df/block0_values"]
            handle.create_dataset("/df/block0_values", shape=(100000, 2100), dtype="f4")
        if change == "table":
            handle.create_dataset("/df/table", shape=(1,), dtype="i8")
        if change == "mixed":
            handle.create_dataset("/df/extra", shape=(1,), dtype="f8")
        if change in ("external", "soft"):
            handle["/df/foreign"] = (
                h5py.ExternalLink("never-open.h5", "/value")
                if change == "external"
                else h5py.SoftLink("/df/axis0")
            )
        if change == "vlen_attr":
            handle["/df"].attrs["pandas_type"] = "frame"
    result = inspect(path)
    if change == "vlen_attr":
        assert result["nodes"][0]["attributes"]["pandas_type"]["status"].startswith(
            "skipped"
        )
    else:
        assert result["status"] == "unsupported_structure"
    assert result["dataset_value_reads"] == 0


def test_inspection_error_keeps_byte_artifact(tmp_path):
    path = tmp_path / "invalid.h5"
    path.write_bytes(b"not HDF")
    assert inspect(path)["status"] == "inspection_error" and path.exists()


@pytest.mark.parametrize("mode", ["raw", "output", "partial"])
def test_session_existing_or_consumed_refused(tmp_path, mode):
    root = tmp_path.resolve()
    path = root / (q.RAW if mode == "raw" else q.OUTPUT)
    path.mkdir(parents=True)
    if mode == "partial":
        (path / "partial").write_bytes(b"x")
    with pytest.raises(ValueError, match="session refuses"):
        q.namespace(root)


def test_competing_reservation_one_winner(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    path = tmp_path / "exclusive"

    def reserve():
        try:
            path.mkdir(exist_ok=False)
            return True
        except FileExistsError:
            return False

    with ThreadPoolExecutor(2) as pool:
        assert sum(pool.map(lambda _: reserve(), range(2))) == 1


def test_disk_capacity_for_three_representations(monkeypatch, tmp_path):
    monkeypatch.setattr(
        q.shutil, "disk_usage", lambda root: type("Disk", (), {"free": 9})()
    )
    with pytest.raises(ValueError, match="Insufficient space"):
        q.disk_space(tmp_path, {"storage": {"required_free_bytes": 10}})


def test_guard_long_journal_capacity(tmp_path):
    record = {"phase": "transfer", "sample": sample(), "latched_error": None}
    assert len(json.dumps(record).encode()) < 1024
    assert 40000 * 1024 < 64 * 2**20
    with Guard(
        time.monotonic() + 2,
        directory=tmp_path,
        probe=sample,
        notify=False,
        journal_limit=64 * 2**20,
    ) as guard:
        guard.check()
    assert guard.journal_limit == 64 * 2**20 and guard.error is None


@pytest.mark.parametrize(
    "script,normal",
    [
        ("pass", True),
        ("raise SystemExit(1)", False),
        ("import time;time.sleep(10)", False),
    ],
)
def test_independent_parent_exit_reaping_and_hang(
    tmp_path, monkeypatch, script, normal
):
    monkeypatch.setattr(guarded, "parent_check", lambda **kwargs: 1)
    result = guarded.supervise(
        [sys.executable, "-c", script],
        tmp_path / "worker.log",
        root=tmp_path,
        environment=os.environ,
        stage_seconds=2.25,
        whole_deadline=time.monotonic() + 3,
    )
    assert result["parent_confirms_normal_exit"] is normal and result["child_reaped"]


def test_parent_finalization_deadline_interrupts():
    with pytest.raises(TimeoutError):
        with c.alarm(time.monotonic() + 0.02):
            time.sleep(1)


def test_stdlib_controller_import_without_numerical_modules(tmp_path):
    code = "import sys;import latenttrigger.data.three_prong_acquisition;assert not any(n in sys.modules for n in ('numpy','torch','h5py','sklearn','onnx','onnxruntime'))"
    assert (
        subprocess.run([sys.executable, "-c", code], capture_output=True).returncode
        == 0
    )


def test_verification_checksum_failure_retains_complete_file(tmp_path):
    root = tmp_path.resolve()
    raw = root / q.RAW
    raw.mkdir(parents=True)
    target = raw / "payload-1.part"
    target.write_bytes(b"wrong")
    base = root / q.OUTPUT / "transfer"
    base.mkdir(parents=True)
    p.write(
        base / "transfer.json",
        dict(complete_file=target.name, complete_prefix_SHA256=p.file_hash(target)),
    )
    directory = root / q.OUTPUT / "verify"
    directory.mkdir()
    source = dict(expected_size=5, expected_checksum="0" * 32)
    guard = type(
        "Guard", (), {"deadline": time.monotonic() + 5, "check": lambda self: None}
    )()
    with pytest.raises(ValueError, match="verification failed"):
        worker.verify(root, {"source": source}, directory, guard)
    assert (
        target.read_bytes() == b"wrong"
        and p.read(directory / "integrity.json")["status"]
        == "failed_checksum_or_size_unaccepted"
    )
    assert not p.read(directory / "access.json")["structural_metadata_requested"]


def test_failure_inventory_retains_bytes_and_partial_digest(tmp_path):
    path = tmp_path / "payload-1.part"
    path.write_bytes(b"prefix")
    rows = c.inventory(tmp_path, time.monotonic() + 5)
    assert (
        rows[0]["retained_bytes_after_reaping"] == 6
        and rows[0]["accepted_verified_bytes"] == 0
    )
    assert rows[0]["byte_integrity"]["SHA256"] == p.file_hash(path) and path.exists()


def test_unavailable_digest_explained_without_deletion(tmp_path):
    path = tmp_path / "payload-1.part"
    path.write_bytes(b"prefix")
    row = c.inventory(tmp_path, time.monotonic() - 1)[0]
    assert (
        row["byte_integrity"] is None
        and "deadline" in row["digest_unavailable_reason"]
        and path.exists()
    )


@pytest.fixture
def controlled_session(tmp_path, monkeypatch):
    root = tmp_path.resolve()
    body = b"abcdefghij"
    source = dict(
        filename="toy.h5",
        url="https://example.invalid/synthetic",
        expected_size=10,
        expected_checksum=hashlib.md5(body, usedforsecurity=False).hexdigest(),
    )
    spec = dict(
        source=source,
        storage=dict(required_free_bytes=1),
        thread_environment_before_imports={},
        limits=dict(transfer_seconds=1800, verify_seconds=60),
    )
    for path in (q.CONFIG, q.ACCEPTANCE, q.AUTHORIZATION):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        p.write(file, dict(synthetic=True))
    monkeypatch.setattr(q, "load", lambda root: spec)
    monkeypatch.setattr(q, "authorization", lambda root: dict(specification=spec))
    monkeypatch.setattr(q, "source_map", lambda root: {"synthetic": "unchanged"})
    monkeypatch.setattr(c, "parent_check", lambda **kwargs: 1)
    monkeypatch.setattr(c, "controller_rss", lambda: 2**20)
    monkeypatch.setattr(
        c, "sys", SimpleNamespace(platform="darwin", executable=sys.executable)
    )
    monkeypatch.setattr(
        c, "network_check", lambda spec: dict(synthetic=True, payload_requests=0)
    )
    calls = []

    def dispatch(command, log, **kwargs):
        phase = command[4]
        calls.append(phase)
        directory = root / q.OUTPUT / phase
        log.write_text("synthetic only\n")
        result = dict(
            task="0029",
            phase=phase,
            status="body_complete_awaiting_exit",
            source_file_sha256={"synthetic": "unchanged"},
            protocol_canonical_JSON_sha256=q.HASH,
            grant_file_byte_sha256=p.file_hash(
                root / q.OUTPUT / (phase + "-grant.json")
            ),
            optimizer_updates=0,
            model_scoring=0,
            dataset_value_reads=0,
            resources=dict(
                latched_error=None,
                owned_thread_alive=False,
                peak_rss_bytes=10000,
                native_heap_reserved_bytes=10000,
            ),
            timings=dict(cleanup_seconds=0.01),
            resource_monitor_closed_monotonic=time.monotonic(),
        )
        if phase == "transfer":
            raw = root / q.RAW / "payload-1.part"
            raw.write_bytes(body)
            stat = raw.stat()
            progress = dict(
                status="transfer_complete_unverified",
                source=source,
                requests=[dict(number=1)],
                redirects_followed=0,
                received_bytes=10,
                written_bytes=10,
                durably_checkpointed_bytes=10,
                complete_file=raw.name,
                files=[
                    dict(
                        name=raw.name,
                        written_bytes=10,
                        durable_bytes=10,
                        durable_prefix_SHA256=p.file_hash(raw),
                        device=stat.st_dev,
                        inode=stat.st_ino,
                    )
                ],
            )
            p.write(directory / "progress.json", progress)
            (directory / "checkpoints.jsonl").write_text("{}\n")
            result["transfer"] = dict(
                complete_file=raw.name,
                complete_bytes=10,
                complete_prefix_SHA256=p.file_hash(raw),
                source=source,
                progress_file_byte_sha256=p.file_hash(directory / "progress.json"),
            )
            p.write(directory / "transfer.json", result["transfer"])
        else:
            result["integrity"] = dict(
                status="byte_integrity_verified_awaiting_parent",
                source=source,
                path=q.RAW + "/payload-1.part",
                locally_computed=hash_bytes(root / q.RAW / "payload-1.part"),
            )
            result["structure"] = dict(
                status="inspection_error",
                dataset_value_reads=0,
                numerical_custody_passed=False,
            )
            p.write(directory / "integrity.json", result["integrity"])
            p.write(directory / "structure.json", result["structure"])
            p.write(
                directory / "access.json",
                dict(
                    source=source,
                    byte_integrity_confirmed=True,
                    structural_metadata_requested=True,
                    structural_metadata_completed=True,
                    dataset_value_reads=0,
                    numerical_custody_passed=False,
                ),
            )
        result["output_file_byte_sha256"] = {
            str(f.relative_to(root)): p.file_hash(f)
            for f in directory.iterdir()
            if f.name not in ("worker.log",)
        }
        p.write(directory / "receipt.json", result)
        return dict(
            returncode=0,
            parent_error=None,
            child_reaped=True,
            within_deadline=True,
            parent_confirms_normal_exit=True,
            elapsed_seconds=0.01,
            exit_observed_monotonic=time.monotonic(),
        )

    monkeypatch.setattr(c, "supervise", dispatch)
    return root, spec, calls, dispatch


def test_controller_accepts_bytes_with_structural_error_separately(controlled_session):
    root, spec, calls, _ = controlled_session
    assert c.run(root, network_authorized=True) == 0 and calls == ["transfer", "verify"]
    raw = root / q.RAW
    part = raw / "payload-1.part"
    final = raw / spec["source"]["filename"]
    assert part.read_bytes() == final.read_bytes() == b"abcdefghij"
    assert part.stat().st_ino == final.stat().st_ino
    assert (
        p.read(raw / "manifest.json")["structural_metadata"]["status"]
        == "inspection_error"
    )
    outcome = p.read(root / q.OUTPUT / "workflow.json")
    assert (
        outcome["accepted_verified_bytes"] == 10 and outcome["new_model_scoring"] == 0
    )
    with pytest.raises(ValueError, match="session refuses"):
        q.namespace(root)


@pytest.mark.parametrize(
    "phase,exitcode", [("transfer", 1), ("transfer", -15), ("verify", 1)]
)
def test_parent_failed_exit_stops_and_preserves_complete_unaccepted(
    controlled_session, monkeypatch, phase, exitcode
):
    root, _, calls, dispatch = controlled_session

    def rejected(command, log, **kwargs):
        result = dispatch(command, log, **kwargs)
        if command[4] == phase:
            result.update(returncode=exitcode, parent_confirms_normal_exit=False)
        return result

    monkeypatch.setattr(c, "supervise", rejected)
    assert c.run(root, network_authorized=True) == 1
    assert calls == (["transfer"] if phase == "transfer" else ["transfer", "verify"])
    outcome = p.read(root / q.OUTPUT / "workflow.json")
    assert (
        outcome["status"] == "failed_consumed_preserved"
        and outcome["accepted_verified_bytes"] == 0
    )
    assert (root / q.RAW / "payload-1.part").read_bytes() == b"abcdefghij"
    assert not (root / q.RAW / "manifest.json").exists()


def test_parent_promotion_never_overwrites_foreign_file(
    controlled_session, monkeypatch
):
    root, spec, _, dispatch = controlled_session

    def foreign(command, log, **kwargs):
        result = dispatch(command, log, **kwargs)
        if command[4] == "verify":
            (root / q.RAW / spec["source"]["filename"]).write_bytes(b"foreign")
        return result

    monkeypatch.setattr(c, "supervise", foreign)
    assert c.run(root, network_authorized=True) == 1
    assert (root / q.RAW / spec["source"]["filename"]).read_bytes() == b"foreign"
    assert p.read(root / q.OUTPUT / "workflow.json")["accepted_verified_bytes"] == 0


def test_unsupported_platform_refused_before_reservation(
    controlled_session, monkeypatch
):
    root, _, calls, _ = controlled_session
    monkeypatch.setattr(c, "sys", SimpleNamespace(platform="linux"))
    assert c.run(root, network_authorized=True) == 1 and calls == []
    assert not (root / q.OUTPUT).exists() and not (root / q.RAW).exists()


def test_network_permission_required_before_reservation(controlled_session):
    root, _, calls, _ = controlled_session
    assert c.run(root, network_authorized=False) == 1 and calls == []
    assert not (root / q.OUTPUT).exists() and not (root / q.RAW).exists()


def test_denied_connectivity_never_consumes_session(controlled_session, monkeypatch):
    root, _, calls, _ = controlled_session

    def denied(spec):
        raise URLError("synthetic network denied")

    monkeypatch.setattr(c, "network_check", denied)
    assert (
        c.run(root, network_authorized=True) == 1
        and calls == []
        and not (root / q.OUTPUT).exists()
    )


def test_inventory_foreign_inode_only_stat_no_read(tmp_path, monkeypatch):
    path = tmp_path / "foreign"
    path.write_bytes(b"foreign")
    monkeypatch.setattr(
        c,
        "hash_bytes",
        lambda *args, **kwargs: pytest.fail("Foreign bytes must not be read"),
    )
    row = c.inventory(tmp_path, time.monotonic() + 5, ownership={})[0]
    assert row["retained_bytes_after_reaping"] == 7 and row["byte_integrity"] is None
