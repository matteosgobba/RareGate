"""Task0030 synthetic-only clocks/HTTP/copies/identities/lifecycle failures."""

import hashlib
import io
import json
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import pytest

from raregate.benchmarks import protocol as p
from raregate.data import three_prong_v3 as controller
from raregate.data import three_prong_v3_protocol as q
from raregate.data import three_prong_v3_runtime as rt
from raregate.data import three_prong_v3_worker as worker
from raregate.data.three_prong_acquisition_smoke import Response
from raregate.data.three_prong_transport import ResponseFault
from raregate.data.three_prong_v3_transport import (
    Transfer,
    hash_bytes,
    retry_after,
)
from raregate.evaluation.guard import Guard, GuardError


class Clock:
    def __init__(self):
        self.t, self.ordinary = 0.0, 0.0

    def __call__(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds

    def snapshot(self):
        return dict(
            continuous_seconds=self.t,
            ordinary_monotonic_seconds=self.ordinary,
            UTC="2020-01-01T00:00:00+00:00",
            deadline_clock="injected continuous",
        )


@pytest.fixture
def setup(tmp_path):
    clock = Clock()
    body = b"abcdefghijklmnopqrst"
    seed_bytes = body[:4]
    raw = tmp_path / "raw"
    raw.mkdir()
    path = raw / "seed.part"
    path.write_bytes(seed_bytes)
    stat = path.stat()
    seed = dict(
        name=path.name,
        device=stat.st_dev,
        inode=stat.st_ino,
        bytes=4,
        SHA256=hashlib.sha256(seed_bytes).hexdigest(),
        response_headers={},
    )
    source = dict(
        url="https://example.invalid/fixed",
        expected_size=len(body),
        expected_checksum=hashlib.md5(body, usedforsecurity=False).hexdigest(),
    )
    policy = dict(
        max_payload_requests=6,
        retry_backoff_seconds=[5, 15, 30, 60, 60],
        socket_timeout_seconds=30,
        buffer_bytes=4,
        checkpoint_bytes=4,
        checkpoint_seconds=5,
        checkpoint_journal_bytes=8 * 2**20,
        progress_seconds=15,
        minimum_request_slack_seconds=2,
    )
    return tmp_path, clock, body, raw, seed, source, policy


def transfer(setup, responses, **kwargs):
    root, clock, body, raw, seed, source, policy = setup
    iterator = iter(responses)
    requests = []

    def open_response(req, timeout):
        requests.append(req)
        value = next(iterator)
        if isinstance(value, Exception):
            raise value
        return value

    obj = Transfer(
        source,
        policy,
        raw,
        root / "progress.json",
        seed=seed,
        clock=clock,
        sleep=clock.sleep,
        snapshot=clock.snapshot,
        open_response=open_response,
        **kwargs,
    )
    return obj, requests


def response(setup, body=None, offset=4, status=206, extra=None):
    _, _, full, _, _, source, _ = setup
    headers = (
        {"Content-Range": f"bytes {offset}-{len(full) - 1}/{len(full)}"}
        if status == 206
        else {}
    )
    headers.update(extra or {})
    r = Response(
        full[offset:]
        if body is None and status == 206
        else full
        if body is None
        else body,
        source["url"],
        status=status,
        extra=headers,
    )
    # Advertise expected representation, even a synthetic truncated body.
    r.headers.replace_header(
        "Content-Length", str(len(full) - offset if status == 206 else len(full))
    )
    return r


@pytest.mark.parametrize(
    "ticks,numer,denom",
    [(0, 125, 3), (2**63 + 7, 125, 3), (1, 1, 1), (999999999, 3, 2)],
)
def test_integer_native_timebase(ticks, numer, denom):
    assert rt.ticks_ns(ticks, numer, denom) == ticks * numer // denom


@pytest.mark.parametrize("value", [-1, 1.5, None])
def test_bad_clock_input(value):
    with pytest.raises(ValueError):
        rt.ticks_ns(value, 125, 3)


@pytest.mark.parametrize("jump", [59, 60, 2000])
def test_continuous_suspension_worker(jump):
    c = Clock()
    g = Guard(
        58,
        clock=c,
        notify=False,
        probe=lambda: pytest.fail("expired before accounting"),
    )
    c.sleep(jump)
    assert c.ordinary == 0
    with pytest.raises(GuardError):
        g.check()
    assert g.error


@pytest.mark.parametrize("seconds", [0, 1, 59, 9999])
def test_delta_from_header_receipt(seconds):
    ra = retry_after(str(seconds), 10, datetime(2020, 1, 1, tzinfo=UTC))
    assert ra["not_before_continuous"] == 10 + seconds


@pytest.mark.parametrize(
    "bad", ["-1", "1.5", "garbage", "Wed, 21 Oct 2015 07:28:00", "99999999999"]
)
def test_malformed_retry_after_stops(bad):
    with pytest.raises(ResponseFault):
        retry_after(bad, 0, datetime.now(UTC))


@pytest.mark.parametrize("delta", [-30, 0, 59, 100])
def test_http_date_anchor(delta):
    utc = datetime(2020, 1, 1, tzinfo=UTC)
    ra = retry_after(
        format_datetime(utc + timedelta(seconds=delta), usegmt=True), 100, utc
    )
    assert ra["not_before_continuous"] == 100 + max(0, delta)
    assert "uncertainty" in ra["UTC_uncertainty"]


def test_valid_seed_continuation_and_accounting(setup):
    obj, requests = transfer(setup, [response(setup)])
    path = obj.run(100)
    assert path.read_bytes() == setup[2]
    assert requests[0].headers["Range"] == "bytes=4-"
    assert obj.state["historical_seed_bytes_imported"] == 4
    assert obj.state["new_received_bytes"] == 16
    assert obj.state["written_bytes"] == obj.state["durably_checkpointed_bytes"] == 20
    assert obj.state["accepted_complete_bytes"] == 0
    checkpoint = json.loads(
        (setup[0] / "checkpoints.jsonl").read_text().splitlines()[-1]
    )
    assert (
        "continuous_seconds" in checkpoint
        and "ordinary_monotonic_seconds" in checkpoint["clock_snapshot"]
    )
    assert "monotonic" not in checkpoint


def test_ignored_range_preserves_seed(setup):
    obj, _ = transfer(setup, [response(setup, status=200)])
    path = obj.run(100)
    assert path.name == "payload-1.part" and path.read_bytes() == setup[2]
    assert (setup[3] / "seed.part").read_bytes() == setup[2][:4]
    assert len(obj.state["files"]) == 2 and obj.state["restarts"] == 1
    assert obj.state["written_bytes"] == 24 and obj.state["new_received_bytes"] == 20


@pytest.mark.parametrize("status", [200, 206])
@pytest.mark.parametrize("failure", ["timeout", "truncated"])
@pytest.mark.parametrize("body_elapsed", [0, 70])
def test_successful_response_retry_after_body_failure(
    setup, status, failure, body_elapsed
):
    r = response(setup, status=status, extra={"Retry-After": "59"})
    c = setup[1]

    def read(n):
        c.sleep(body_elapsed)
        if failure == "timeout":
            raise TimeoutError("synthetic body timeout")
        return b""

    r.read = read
    # If first200 created a new empty owned file, next200 full is valid.
    obj, _ = transfer(setup, [r, response(setup, status=200)])
    obj.run(400)
    assert obj.state["waits"][0]["seconds"] == max(5, 59 - body_elapsed)
    assert (
        obj.state["requests"][0]["retry_after"]["kind"]
        == "delta_seconds_from_header_receipt"
    )


@pytest.mark.parametrize(
    "extra",
    [
        {"Content-Range": "bytes 3-19/20"},
        {"Content-Range": "bytes 4-18/20"},
        {"Content-Encoding": "gzip"},
        {"ETag": "invalid"},
    ],
)
def test_invalid_response_no_retry(setup, extra):
    r = response(setup)
    for k, v in extra.items():
        if r.headers[k] is None:
            r.headers[k] = v
        else:
            r.headers.replace_header(k, v)
    obj, requests = transfer(setup, [r])
    with pytest.raises(ResponseFault):
        obj.run(100)
    assert len(requests) == 1 and (setup[3] / "seed.part").read_bytes() == setup[2][:4]


@pytest.mark.parametrize("returned", [None, '"changed"', 'W/"a"'])
def test_strong_validator_drift(setup, returned):
    setup[4]["response_headers"] = {"ETag": '"a"'}
    r = response(setup, extra={"ETag": returned} if returned else {})
    obj, requests = transfer(setup, [r])
    with pytest.raises(ResponseFault):
        obj.run(100)
    assert requests[0].headers["If-range"] == '"a"'


def test_weak_validator_not_if_range(setup):
    setup[4]["response_headers"] = {"ETag": 'W/"a"'}
    obj, requests = transfer(setup, [response(setup, extra={"ETag": 'W/"a"'})])
    obj.run(100)
    assert "If-range" not in requests[0].headers


def test_six_requests_shared_deadline_and_retention(setup):
    obj, requests = transfer(setup, [TimeoutError("temporary")] * 6)
    with pytest.raises(TimeoutError):
        obj.run(400)
    assert len(requests) == 6
    assert [w["seconds"] for w in obj.state["waits"]] == [5, 15, 30, 60, 60]
    assert (
        obj.state["new_received_bytes"] == 0
        and obj.state["durably_checkpointed_bytes"] == 4
    )
    assert (setup[3] / "seed.part").exists()


def test_wait_budget_does_not_reset(setup):
    obj, requests = transfer(setup, [TimeoutError("temporary")] * 6)
    with pytest.raises(GuardError):
        obj.run(15)
    assert len(requests) == 2 and setup[1]() == 5


def test_body_sleep_checks_before_write(setup):
    r = response(setup)
    original = r.read

    def read(n):
        setup[1].sleep(101)
        return original(n)

    r.read = read
    obj, requests = transfer(setup, [r])
    with pytest.raises(GuardError):
        obj.run(100)
    assert len(requests) == 1 and obj.state["written_bytes"] == 4
    assert obj.state["new_received_bytes"] == 4
    assert setup[1].ordinary == 0


@pytest.mark.parametrize("mutation", ["digest", "inode", "symlink"])
def test_seed_identity_before_request(setup, mutation):
    raw, seed = setup[3], setup[4]
    if mutation == "digest":
        (raw / "seed.part").write_bytes(b"zzzz")
    if mutation == "inode":
        seed["inode"] += 1
    if mutation == "symlink":
        target = raw / "foreign"
        target.write_bytes(b"abcd")
        (raw / "seed.part").unlink()
        (raw / "seed.part").symlink_to(target)
    if mutation in ("inode", "symlink"):
        with pytest.raises(ResponseFault):
            transfer(setup, [])
    else:
        obj, requests = transfer(setup, [])
        with pytest.raises(ResponseFault):
            obj.run(100)
        assert not requests


def test_existing_progress_refuses(setup):
    (setup[0] / "progress.json").write_text("{}")
    with pytest.raises(ResponseFault):
        transfer(setup, [])


def test_hash_copy_independent_history(tmp_path):
    c = Clock()
    original = tmp_path / "old"
    original.write_bytes(b"synthetic")
    copied = tmp_path / "new"
    with copied.open("xb", buffering=0) as stream:
        expected = hash_bytes(original, clock=c, deadline=10, copy_to=stream)
    assert hash_bytes(copied, clock=c, deadline=10) == expected
    copied.write_bytes(b"changed")
    assert (
        original.read_bytes() == b"synthetic"
        and original.stat().st_ino != copied.stat().st_ino
    )


def test_copy_deadline_before_open(tmp_path):
    c = Clock()
    c.sleep(10)
    with pytest.raises(GuardError):
        hash_bytes(tmp_path / "missing", clock=c, deadline=5)


class Child:
    pid = 12345
    returncode = None

    def __init__(self, clock, exit_at=0, code=0):
        self.clock, self.exit_at, self.code = clock, exit_at, code

    def poll(self):
        if self.clock() >= self.exit_at:
            self.returncode = self.code
        return self.returncode


@pytest.mark.parametrize(
    "jump,code,accepted", [(0, 0, True), (11, 0, False), (11, 1, False)]
)
def test_parent_late_normal_exit_after_suspension(
    tmp_path, monkeypatch, jump, code, accepted
):
    c = Clock()
    child = Child(c, exit_at=0, code=code)

    def launch(*args, **kwargs):
        c.sleep(jump)
        return child

    monkeypatch.setattr(rt, "parent_check", lambda **kwargs: 1)
    d = rt.supervise(
        [],
        tmp_path / "log",
        root=tmp_path,
        environment={},
        clock=c,
        operation_deadline=8,
        stage_deadline=10,
        whole_deadline=20,
        launch=launch,
        sleep=c.sleep,
    )
    assert d["parent_confirms_normal_exit"] is accepted and d["child_reaped"]
    if jump:
        assert d["overshoot_seconds"] == 1


@pytest.mark.parametrize(
    "text",
    [
        "",
        "PreventUserIdleSystemSleep 0\npid 3(caffeinate): [abc] PreventUserIdleSystemSleep",
        "PreventUserIdleSystemSleep 1\npid 4(caffeinate): [abc] PreventUserIdleSystemSleep",
    ],
)
def test_assertion_needs_owned_active_evidence(text):
    with pytest.raises(GuardError):
        rt.assertion_id(text, 3)


def test_assertion_setup_loss_release(monkeypatch):
    c = Clock()
    child = Child(c, exit_at=999)
    active = True

    def read(command, clock, deadline):
        if command[0] == "/bin/ps":
            return f"{child.pid} 999 100 Ss"
        return (
            f"PreventUserIdleSystemSleep 1\npid {child.pid}(caffeinate): [abc] PreventUserIdleSystemSleep"
            if active
            else ""
        )

    a = rt.IdleAssertion(c, launch=lambda *args, **kwargs: child, read=read)
    a.start(10)
    assert a.identity == "abc"
    active = False
    with pytest.raises(GuardError):
        a.check(10, force=True)
    monkeypatch.setattr(
        rt, "reap", lambda *args, **kwargs: dict(reaped=True, cleanup_deadline_met=True)
    )
    assert a.release(10)["released"]


def test_assertion_setup_exited_fails():
    c = Clock()
    child = Child(c)
    a = rt.IdleAssertion(
        c,
        launch=lambda *args, **kwargs: child,
        read=lambda *args: pytest.fail("exited before pmset"),
    )
    with pytest.raises(GuardError):
        a.start(10)


def test_assertion_release_not_observed_rejects(monkeypatch):
    c = Clock()
    a = rt.IdleAssertion(
        c, read=lambda *args: "pid 12345(caffeinate): [abc] PreventUserIdleSystemSleep"
    )
    a.child = Child(c)
    a.identity = "abc"
    monkeypatch.setattr(
        rt, "reap", lambda *args, **kwargs: dict(reaped=True, cleanup_deadline_met=True)
    )
    with pytest.raises(GuardError):
        a.release(10)
    assert not a.evidence["released"]


def test_promotion_requires_release(tmp_path):
    c = Clock()
    with pytest.raises(ValueError):
        controller.promote(
            tmp_path, {}, dict(sleep_assertion=dict(released=False)), c, 10
        )
    assert not (tmp_path / q.RAW).exists()


def test_late_promotion_before_any_io(tmp_path):
    c = Clock()
    c.sleep(10)
    with pytest.raises(GuardError):
        controller.promote(
            tmp_path, {}, dict(sleep_assertion=dict(released=True)), c, 5
        )


def test_stage_acceptance_late_before_receipt_read(tmp_path):
    c = Clock()
    c.sleep(10)
    with pytest.raises(GuardError):
        controller.accepted_stage(tmp_path, "import", {}, {}, {}, clock=c, deadline=5)


@pytest.mark.parametrize("which", [q.RAW, q.OUTPUT])
def test_consumed_namespace_no_reset(tmp_path, which):
    (tmp_path / which).mkdir(parents=True)
    with pytest.raises(ValueError):
        q.namespace(tmp_path)


def test_pinned_protocol_and_storage():
    spec = q.load()
    assert (
        spec["limits"]["whole_seconds"] == 2000
        and spec["limits"]["import_seconds"] == 60
    )
    assert spec["transport"]["max_payload_requests"] == 6
    assert (
        q.disk_space(q.ROOT, spec)["worst_case_retained_and_journal_bytes"] <= 2 * 2**30
    )


def test_worker_assertion_lost(monkeypatch):
    c = Clock()
    grant = dict(
        parent_pid=1,
        sleep_helper_pid=2,
        sleep_assertion_id="abc",
        operation_deadline_continuous=10,
    )
    monkeypatch.setattr(worker.os, "kill", lambda *args: None)
    monkeypatch.setattr(worker.subprocess, "check_output", lambda *args, **kwargs: "")
    with pytest.raises(GuardError):
        worker.AssertionMonitor(grant, c).check()


@pytest.fixture
def lineage(tmp_path):
    c = Clock()
    path = tmp_path / "data/history/old.part"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"abcd")
    integrity = hash_bytes(path, clock=c, deadline=10)
    pin = dict(path=str(path.relative_to(tmp_path)), **integrity)
    s = path.stat()
    source = dict(url="https://example.invalid/fixed", expected_size=20)
    file = dict(
        name=path.name,
        device=s.st_dev,
        inode=s.st_ino,
        written_bytes=4,
        durable_bytes=4,
        durable_prefix_SHA256=integrity["SHA256"],
    )
    base = tmp_path / q.old.OUTPUT
    (base / "transfer").mkdir(parents=True)
    progress = dict(
        source=source,
        status="failed_preserved",
        files=[file],
        requests=[dict(response_headers={})],
    )
    p.write(base / "transfer/progress.json", progress)
    (base / "transfer/checkpoints.jsonl").write_text(
        json.dumps(
            dict(
                current_file=file,
                durable=4,
                source_canonical_JSON_sha256=p.digest(source),
            )
        )
        + "\n"
    )
    p.write(base / "transfer/dispatch.json", dict(child_reaped=True))
    p.write(
        base / "workflow.json",
        dict(
            retained_files=[
                dict(
                    name=path.name,
                    byte_integrity=integrity,
                    retained_bytes_after_reaping=4,
                    accepted_verified_bytes=0,
                )
            ]
        ),
    )
    return tmp_path, c, path, dict(prefix=pin, source=source), base


def test_real_prefix_lineage_and_independent_import(lineage):
    root, c, path, spec, _ = lineage
    q.prefix(root, spec, clock=c, deadline=10)
    (root / q.RAW).mkdir(parents=True)
    directory = root / "worker"
    directory.mkdir()
    imported = worker.import_seed(root, spec, directory, c, 10, lambda: None)
    assert imported["bytes"] == 4 and imported["new_received_bytes"] == 0
    assert imported["inode"] != path.stat().st_ino
    copied = root / q.RAW / "seed.part"
    copied.write_bytes(b"zzzz")
    assert path.read_bytes() == b"abcd"


@pytest.mark.parametrize(
    "mismatch",
    ["hash", "MD5", "checkpoint", "inode", "inventory", "not_reaped", "symlink"],
)
def test_prefix_lineage_rejects_before_network(lineage, mismatch):
    root, c, path, spec, base = lineage
    if mismatch == "hash":
        spec["prefix"]["SHA256"] = "0" * 64
    if mismatch == "MD5":
        spec["prefix"]["MD5"] = "0" * 32
    if mismatch in ("checkpoint", "inode"):
        doc = p.read(base / "transfer/progress.json")
        doc["files"][0]["durable_bytes" if mismatch == "checkpoint" else "inode"] += 1
        p.write(base / "transfer/progress.json", doc)
    if mismatch == "inventory":
        doc = p.read(base / "workflow.json")
        doc["retained_files"][0]["accepted_verified_bytes"] = 4
        p.write(base / "workflow.json", doc)
    if mismatch == "not_reaped":
        p.write(base / "transfer/dispatch.json", dict(child_reaped=False))
    if mismatch == "symlink":
        other = path.with_name("other")
        other.write_bytes(b"abcd")
        path.unlink()
        path.symlink_to(other)
    with pytest.raises((ValueError, ResponseFault)):
        q.prefix(root, spec, clock=c, deadline=10)
    assert not (root / q.RAW).exists()


def test_import_existing_seed_no_overwrite(lineage):
    root, c, _, spec, _ = lineage
    (root / q.RAW).mkdir(parents=True)
    seed = root / q.RAW / "seed.part"
    seed.write_bytes(b"foreign")
    directory = root / "worker"
    directory.mkdir()
    with pytest.raises(FileExistsError):
        worker.import_seed(root, spec, directory, c, 10, lambda: None)
    assert seed.read_bytes() == b"foreign"


def test_retained_foreign_inode_not_read(setup, monkeypatch):
    root, c, _, raw, _, _, _ = setup
    output = root / q.OUTPUT
    output.mkdir(parents=True)
    (root / q.RAW).mkdir(parents=True)
    (root / q.RAW / "seed.part").write_bytes(b"foreign")
    monkeypatch.setattr(
        controller,
        "hash_bytes",
        lambda *args, **kwargs: pytest.fail("foreign artifact read"),
    )
    rows = controller.inventory(root, c, 10)
    assert rows[0]["byte_integrity"] is None and rows[0]["accepted_complete_bytes"] == 0


@pytest.mark.parametrize("bad", ["wrong_MD5", "late", "already_promoted"])
def test_promotion_gate_synthetic(tmp_path, monkeypatch, bad):
    c = Clock()
    raw = tmp_path / q.RAW
    raw.mkdir(parents=True)
    path = raw / "seed.part"
    path.write_bytes(b"full synthetic")
    integrity = hash_bytes(path, clock=c, deadline=10)
    base = tmp_path / q.OUTPUT
    (base / "verify").mkdir(parents=True)
    p.write(
        base / "verify/integrity.json",
        dict(path=str(path.relative_to(tmp_path)), locally_computed=integrity),
    )
    p.write(base / "verify/structure.json", dict(dataset_value_reads=0))
    spec = dict(source=dict(filename="full.h5", expected_checksum=integrity["MD5"]))
    row = dict(name=path.name, byte_integrity=dict(integrity))
    outcome = dict(sleep_assertion=dict(released=True), retained_files=[row])
    if bad == "wrong_MD5":
        row["byte_integrity"]["MD5"] = "0" * 32
    if bad == "late":
        c.sleep(11)
    if bad == "already_promoted":
        (raw / "full.h5").write_bytes(b"preserved")
    monkeypatch.setattr(controller.p, "file_hash", lambda path: "synthetic-sha")
    with pytest.raises((ValueError, GuardError, FileExistsError)):
        controller.promote(tmp_path, spec, outcome, c, 10)
    assert not (raw / "manifest.json").exists()


@pytest.mark.parametrize("bad", ["malformed_success", "malformed_error"])
def test_retry_after_malformed_preserves(setup, bad):
    from urllib.error import HTTPError

    r = response(setup, extra={"Retry-After": "nonsense"})
    if bad == "malformed_error":
        r = HTTPError(setup[5]["url"], 503, "temporary", r.headers, io.BytesIO(b""))
    obj, requests = transfer(setup, [r])
    with pytest.raises(ResponseFault):
        obj.run(100)
    assert len(requests) == 1 and (setup[3] / "seed.part").read_bytes() == b"abcd"


def test_http_error_retry_after(setup):
    from urllib.error import HTTPError

    r = response(setup, extra={"Retry-After": "59"})
    error = HTTPError(setup[5]["url"], 429, "temporary", r.headers, io.BytesIO(b""))
    obj, _ = transfer(setup, [error, response(setup)])
    obj.run(100)
    assert obj.state["waits"][0]["seconds"] == 59
    assert obj.state["requests"][0]["response_status"] == 429


@pytest.mark.parametrize(
    "error",
    [
        ValueError("storage"),
        PermissionError("access"),
        ResponseFault("source"),
        GuardError("critical"),
    ],
)
def test_fatal_failures_no_retry(setup, error):
    obj, requests = transfer(setup, [error])
    with pytest.raises(type(error)):
        obj.run(100)
    assert len(requests) == 1


def test_interruption_preserves_progress(setup):
    obj, requests = transfer(setup, [response(setup)])

    def interrupted(n):
        raise KeyboardInterrupt("synthetic interruption")

    obj.open_response = lambda *args, **kwargs: response(setup)
    r = response(setup)
    r.read = interrupted
    obj.open_response = lambda *args, **kwargs: r
    with pytest.raises(KeyboardInterrupt):
        obj.run(100)
    assert (
        obj.state["status"] == "failed_preserved" and obj.state["inflight"] is not None
    )
    assert (setup[3] / "seed.part").read_bytes() == b"abcd"


@pytest.mark.parametrize("overrun", [False, True])
def test_publication_overrun_supersedes_acceptance(tmp_path, monkeypatch, overrun):
    c = Clock()
    base = tmp_path / q.OUTPUT
    base.mkdir(parents=True)
    monkeypatch.setattr(
        controller.q, "source_map", lambda root: {"synthetic": "identity"}
    )
    original = controller.durable

    def writing(path, doc):
        original(path, doc)
        if overrun and path.name == "parent-acceptance.json":
            c.sleep(11)

    monkeypatch.setattr(controller, "durable", writing)
    outcome = dict(
        status="parent_accepted_verified_artifact",
        accepted_complete_bytes=20,
        sleep_assertion=dict(released=True),
        retained_files=[dict(accepted_complete_bytes=20)],
    )
    controller.publish(tmp_path, outcome, c, 10)
    parent = p.read(base / "parent-acceptance.json")
    assert parent["accepted_complete_bytes"] == (0 if overrun else 20)
    assert parent["status"] == (
        "failed_consumed_preserved" if overrun else "parent_accepted_verified_artifact"
    )
