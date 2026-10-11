"""Task0029-only bounded transport; owned prefixes are never deleted on failure."""

import errno
import hashlib
import http.client
import json
import os
import re
import socket
import ssl
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from latenttrigger.benchmarks import protocol as p
from latenttrigger.evaluation.guarded_audit import durable


class ResponseFault(ValueError):
    """Identity/header/representation failure: never retry."""


class Truncated(ConnectionError):
    """EOF before the prescribed response bytes; limited recovery may apply."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ResponseFault(f"Redirect refused ({code}); approved URL only")


def opener():
    return build_opener(NoRedirect()).open


def headers(response):
    result = {}
    for key in (
        "Content-Length",
        "Content-Range",
        "Content-Encoding",
        "ETag",
        "Last-Modified",
        "Retry-After",
        "Location",
    ):
        values = response.headers.get_all(key, [])
        if len(values) > 1 or any(len(v.encode()) > 2048 for v in values):
            raise ResponseFault("Duplicate/unbounded response header: " + key)
        result[key] = values[0] if values else None
    return result


def retryable(exc):
    if isinstance(exc, HTTPError):
        return exc.code in (408, 429) or 500 <= exc.code <= 599
    if isinstance(exc, URLError):
        return retryable(exc.reason)
    if isinstance(exc, (ResponseFault, ssl.SSLError)):
        return False
    if isinstance(exc, socket.gaierror):
        return exc.errno == socket.EAI_AGAIN
    if isinstance(
        exc,
        (
            TimeoutError,
            Truncated,
            http.client.RemoteDisconnected,
            http.client.IncompleteRead,
        ),
    ):
        return True
    return isinstance(exc, OSError) and exc.errno in {
        errno.ECONNRESET,
        errno.ECONNABORTED,
        errno.EPIPE,
        errno.ETIMEDOUT,
        errno.ENETUNREACH,
        errno.EHOSTUNREACH,
    }


def retry_delay(exc, attempt, backoffs, utc_now=lambda: datetime.now(UTC)):
    delay = backoffs[attempt - 1]
    value = headers(exc)["Retry-After"] if isinstance(exc, HTTPError) else None
    if value is not None:
        if re.fullmatch(r"[0-9]{1,10}", value):
            asked = int(value)
        else:
            try:
                date = parsedate_to_datetime(value)
                if date.tzinfo is None:
                    raise ValueError("Timezone missing")
                asked = max(0, (date - utc_now()).total_seconds())
            except (ValueError, TypeError, OverflowError) as error:
                raise ResponseFault("Malformed Retry-After; no retry") from error
        delay = max(delay, asked)
    return delay


def response_mode(response, source, offset, previous):
    h = headers(response)
    if response.geturl() != source["url"]:
        raise ResponseFault("Response source URL changed")
    if h["Content-Encoding"] not in (None, "identity"):
        raise ResponseFault("Encoded representation refused")
    size = source["expected_size"]
    if response.status == 200:
        if h["Content-Range"] is not None:
            raise ResponseFault("Content-Range on full response")
        mode, expected = ("restart" if offset else "full"), size
    elif response.status == 206 and 0 < offset < size:
        match = re.fullmatch(
            r"bytes ([0-9]+)-([0-9]+)/([0-9]+)", h["Content-Range"] or ""
        )
        if not match or tuple(map(int, match.groups())) != (offset, size - 1, size):
            raise ResponseFault("Invalid Content-Range offset/end/total")
        for key in ("ETag", "Last-Modified"):
            if previous.get(key) and h[key] and previous[key] != h[key]:
                raise ResponseFault("Changed continuation validator: " + key)
        strong = previous.get("ETag")
        if strong and not strong.startswith("W/") and h["ETag"] != strong:
            raise ResponseFault("Strong continuation validator missing/changed")
        mode, expected = "continue", size - offset
    else:
        raise ResponseFault(f"Unsupported response status/range: {response.status}")
    if h["Content-Length"] is not None and (
        not re.fullmatch(r"[0-9]{1,12}", h["Content-Length"])
        or int(h["Content-Length"]) != expected
    ):
        raise ResponseFault("Content-Length contradicts pinned representation")
    if h["ETag"] is not None and not re.fullmatch(
        r'(?:W/)?"[^"\r\n]{0,512}"', h["ETag"]
    ):
        raise ResponseFault("Malformed entity tag")
    return mode, h


def hash_bytes(path, *, boundary=lambda: None, deadline=None, clock=time.monotonic):
    """Stream byte integrity only, with explicit deadline checks and 1MiB boundaries."""
    md5 = hashlib.md5(usedforsecurity=False)
    sha = hashlib.sha256()
    size = 0
    if deadline is not None and clock() >= deadline:
        raise TimeoutError("Byte-integrity/finalization deadline before open")
    with path.open("rb") as stream:
        while chunk := stream.read(65536):
            if deadline is not None and clock() >= deadline:
                raise TimeoutError("Byte-integrity/finalization deadline")
            md5.update(chunk)
            sha.update(chunk)
            size += len(chunk)
            if size % 2**20 == 0:
                boundary()
    return dict(bytes=size, MD5=md5.hexdigest(), SHA256=sha.hexdigest())


class Transfer:
    """One three-request session, fixed URL and shared deadline; no future resume."""

    def __init__(
        self,
        source,
        policy,
        directory,
        progress,
        *,
        open_response=None,
        boundary=lambda: None,
        clock=time.monotonic,
        sleep=time.sleep,
    ):
        self.source, self.policy, self.directory, self.progress = (
            source,
            policy,
            directory,
            progress,
        )
        self.open_response = open_response or opener()
        self.boundary, self.clock, self.sleep = boundary, clock, sleep
        self.deadline = None
        self.file = self.current = self.sha = None
        if progress.exists():
            raise ResponseFault("Foreign/existing progress;no resume")
        self.journal = progress.with_name("checkpoints.jsonl").open("x")
        self.last_checkpoint = self.last_print = clock()
        self.state = dict(
            source=source,
            status="reserved_no_requests",
            requests=[],
            files=[],
            received_bytes=0,
            written_bytes=0,
            durably_checkpointed_bytes=0,
            continuations=0,
            restarts=0,
            redirects_followed=0,
            redirects_observed=0,
            waits=[],
            inflight=None,
        )
        self.persist()

    def persist(self):
        self.state.update(checkpoint_utc=p.now(), checkpoint_monotonic=self.clock())
        checkpoint = dict(
            utc=self.state["checkpoint_utc"],
            monotonic=self.state["checkpoint_monotonic"],
            source_canonical_JSON_sha256=p.digest(self.source),
            request_count=len(self.state["requests"]),
            received=self.state["received_bytes"],
            written=self.state["written_bytes"],
            durable=self.state["durably_checkpointed_bytes"],
            inflight=self.state["inflight"],
            current_file=self.current,
            status=self.state["status"],
        )
        line = json.dumps(checkpoint, separators=(",", ":"), allow_nan=False) + "\n"
        if (
            self.journal.tell() + len(line.encode())
            > self.policy["checkpoint_journal_bytes"]
        ):
            raise ResponseFault("Bounded checkpoint journal exhausted;preserve bytes")
        self.journal.write(line)
        self.journal.flush()
        os.fsync(self.journal.fileno())
        durable(self.progress, self.state)

    def remaining(self):
        value = self.deadline - self.clock()
        if value <= 0:
            raise TimeoutError("Shared transfer deadline exhausted")
        return value

    def checkpoint(self, *, clear=False):
        if self.file and not self.file.closed:
            self.file.flush()
            os.fsync(self.file.fileno())
            self.current.update(
                durable_bytes=self.current["written_bytes"],
                durable_prefix_SHA256=self.sha.hexdigest(),
            )
        self.state["durably_checkpointed_bytes"] = sum(
            f["durable_bytes"] for f in self.state["files"]
        )
        if clear:
            self.state["inflight"] = None
        self.last_checkpoint = self.clock()
        self.persist()

    def owned_file(self, attempt):
        if self.file:
            self.file.close()
        name = f"payload-{attempt}.part"
        path = self.directory / name
        descriptor = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
        )
        self.file = os.fdopen(descriptor, "wb", buffering=0)
        stat = path.stat()
        self.sha = hashlib.sha256()
        self.current = dict(
            name=name,
            written_bytes=0,
            durable_bytes=0,
            durable_prefix_SHA256=self.sha.hexdigest(),
            device=stat.st_dev,
            inode=stat.st_ino,
        )
        self.state["files"].append(self.current)
        return path

    def print_progress(self, reason, force=False):
        if force or self.clock() - self.last_print >= self.policy["progress_seconds"]:
            print(
                f"Task0029 {reason}; requests={len(self.state['requests'])}; "
                f"received={self.state['received_bytes']} written={self.state['written_bytes']} "
                f"durable={self.state['durably_checkpointed_bytes']}",
                flush=True,
            )
            self.last_print = self.clock()

    def wait(self, seconds):
        if seconds + self.policy["minimum_request_slack_seconds"] >= self.remaining():
            raise TimeoutError("Retry wait does not fit original deadline")
        row = dict(
            seconds=seconds,
            started_utc=p.now(),
            started_monotonic=self.clock(),
            completed=False,
        )
        self.state["waits"].append(row)
        self.state["inflight"] = "retry_wait"
        self.persist()
        until = self.clock() + seconds
        while self.clock() < until:
            self.remaining()
            self.boundary()
            self.print_progress("retry wait")
            self.sleep(min(1, until - self.clock()))
        row.update(
            completed=True, elapsed_seconds=self.clock() - row["started_monotonic"]
        )
        self.state["inflight"] = None
        self.persist()

    def run(self, deadline):
        self.deadline = deadline
        previous = {}
        try:
            for attempt in range(1, self.policy["max_payload_requests"] + 1):
                self.remaining()
                self.boundary()
                offset = self.current["durable_bytes"] if self.current else 0
                if offset >= self.source["expected_size"]:
                    raise ResponseFault(
                        "Full but uncertain previous transfer; preserve without retry"
                    )
                request_headers = {
                    "User-Agent": "LatentTrigger/0.1.0",
                    "Accept-Encoding": "identity",
                }
                if offset:
                    path = self.directory / self.current["name"]
                    stat = path.lstat()
                    if path.is_symlink() or (
                        stat.st_dev,
                        stat.st_ino,
                        stat.st_size,
                    ) != (self.current["device"], self.current["inode"], offset):
                        raise ResponseFault("Owned continuation prefix changed")
                    actual = hash_bytes(
                        path,
                        boundary=self.boundary,
                        deadline=deadline,
                        clock=self.clock,
                    )
                    if actual["SHA256"] != self.current["durable_prefix_SHA256"]:
                        raise ResponseFault("Owned prefix digest changed")
                    request_headers["Range"] = f"bytes={offset}-"
                    tag = previous.get("ETag")
                    if tag and not tag.startswith("W/"):
                        request_headers["If-Range"] = tag
                row = dict(
                    number=attempt,
                    offset=offset,
                    utc=p.now(),
                    monotonic=self.clock(),
                    source_url=self.source["url"],
                    request_headers=request_headers,
                    status="before_network_request",
                )
                self.state["requests"].append(row)
                self.state.update(
                    status="transferring", inflight="connection_or_response"
                )
                self.persist()
                self.print_progress("request starting", True)
                if not self.current:
                    self.owned_file(attempt)
                    self.checkpoint()
                try:
                    request = Request(self.source["url"], headers=request_headers)
                    with self.open_response(
                        request,
                        timeout=min(
                            self.policy["socket_timeout_seconds"], self.remaining()
                        ),
                    ) as response:
                        mode, observed = response_mode(
                            response, self.source, offset, previous
                        )
                        row.update(
                            status="response_validated",
                            response_status=response.status,
                            mode=mode,
                            response_headers=observed,
                            validator_assurance="strong_ETag"
                            if observed["ETag"]
                            and not observed["ETag"].startswith("W/")
                            else "weak_or_missing;final_publisher_MD5_required",
                        )
                        if mode == "restart":
                            self.checkpoint()
                            self.owned_file(attempt)
                            self.state["restarts"] += 1
                        if mode == "continue":
                            self.state["continuations"] += 1
                        previous = observed
                        self.checkpoint()
                        while True:
                            self.remaining()
                            self.state["inflight"] = "read_or_write_since_checkpoint"
                            pending_error = None
                            try:
                                chunk = response.read(self.policy["buffer_bytes"])
                            except http.client.IncompleteRead as incomplete:
                                chunk = incomplete.partial
                                pending_error = incomplete
                            if not chunk:
                                if pending_error:
                                    raise pending_error
                                break
                            self.state["received_bytes"] += len(chunk)
                            if (
                                self.current["written_bytes"] + len(chunk)
                                > self.source["expected_size"]
                            ):
                                raise ResponseFault(
                                    "Oversized response; bytes refused, prefix preserved"
                                )
                            view = memoryview(chunk)
                            while view:
                                written = self.file.write(view)
                                if written is None or written <= 0:
                                    raise OSError("No write progress")
                                self.sha.update(view[:written])
                                self.current["written_bytes"] += written
                                self.state["written_bytes"] += written
                                view = view[written:]
                            if (
                                self.current["written_bytes"]
                                - self.current["durable_bytes"]
                                >= self.policy["checkpoint_bytes"]
                                or self.clock() - self.last_checkpoint
                                >= self.policy["checkpoint_seconds"]
                            ):
                                self.checkpoint()
                                self.boundary()
                            self.print_progress("transferring")
                            if pending_error:
                                raise pending_error
                        self.checkpoint(clear=True)
                        if (
                            self.current["written_bytes"]
                            != self.source["expected_size"]
                        ):
                            raise Truncated("Truncated response; prefix retained")
                        row["status"] = "complete_expected_bytes_unverified"
                        self.state.update(
                            status="transfer_complete_unverified",
                            complete_file=self.current["name"],
                        )
                        self.persist()
                        self.print_progress(
                            "transfer complete, integrity pending", True
                        )
                        return self.directory / self.current["name"]
                except Exception as error:
                    row.update(
                        status="interrupted_or_failed",
                        error=f"{type(error).__name__}: {error}",
                        retryable=retryable(error),
                    )
                    if isinstance(error, ResponseFault) and "Redirect refused" in str(
                        error
                    ):
                        self.state["redirects_observed"] += 1
                    if isinstance(error, HTTPError) and 300 <= error.code < 400:
                        self.state["redirects_observed"] += 1
                    self.checkpoint()  # Does not clear uncertainty on failed requests.
                    if (
                        not retryable(error)
                        or attempt == self.policy["max_payload_requests"]
                    ):
                        if isinstance(error, HTTPError):
                            error.close()
                        raise
                    delay = retry_delay(
                        error, attempt, self.policy["retry_backoff_seconds"]
                    )
                    if isinstance(error, HTTPError):
                        error.close()
                    if self.current["durable_bytes"] >= self.source["expected_size"]:
                        raise ResponseFault(
                            "Full but uncertain interrupted response;preserve without retry"
                        ) from error
                    self.wait(delay)
            raise RuntimeError("Request budget exhausted")
        except BaseException as error:
            self.state.update(
                status="failed_preserved", error=f"{type(error).__name__}: {error}"
            )
            raise
        finally:
            try:
                self.checkpoint()
            finally:
                if self.file:
                    self.file.close()
                self.journal.close()
