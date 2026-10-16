"""Task0030 six-request transport: copied seed, continuous bounds, header anchors."""

import hashlib
import http.client
import json
import os
import re
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError
from urllib.request import Request

from raregate.benchmarks import protocol as p
from raregate.data.three_prong_transport import (
    ResponseFault,
    Truncated,
    headers,
    response_mode,
    retryable,
)
from raregate.data.three_prong_transport import (
    Transfer as PreviousTransfer,
)
from raregate.data.three_prong_v3_runtime import check_deadline
from raregate.evaluation.guard import GuardError


def hash_bytes(path, *, clock, deadline, boundary=lambda: None, copy_to=None):
    """Byte-only read/copy, checks before and after blocking IO; no HDF open."""
    check_deadline(clock, deadline)
    before = path.lstat()
    if path.is_symlink() or not path.is_file():
        raise ResponseFault("Regular non-symlink byte artifact required")
    md5, sha, size = hashlib.md5(usedforsecurity=False), hashlib.sha256(), 0
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ResponseFault("Byte file changed on open")
        while True:
            check_deadline(clock, deadline)
            chunk = stream.read(65536)
            check_deadline(clock, deadline)
            if not chunk:
                break
            if copy_to is not None:
                view = memoryview(chunk)
                while view:
                    check_deadline(clock, deadline)
                    n = copy_to.write(view)
                    check_deadline(clock, deadline)
                    if n is None or n <= 0:
                        raise OSError("No import copy progress")
                    view = view[n:]
            md5.update(chunk)
            sha.update(chunk)
            size += len(chunk)
            if size % 2**20 == 0:
                boundary()
    after = path.lstat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ) or size != before.st_size:
        raise ResponseFault("Byte file mutated while hashing/copying")
    boundary()
    check_deadline(clock, deadline)
    return dict(bytes=size, MD5=md5.hexdigest(), SHA256=sha.hexdigest())


def retry_after(value, header_continuous, header_utc):
    """Prospective policy for failed bodies of validated200/206 AND HTTP errors."""
    if value is None:
        return dict(value=None, not_before_continuous=None, kind="absent")
    if re.fullmatch(r"[0-9]{1,10}", value):
        seconds, kind = int(value), "delta_seconds_from_header_receipt"
    else:
        try:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                raise ValueError("Timezone missing")
            seconds = max(0, (date - header_utc).total_seconds())
            kind = "HTTP_date_via_header_UTC_anchor"
        except (ValueError, TypeError, OverflowError) as error:
            raise ResponseFault("Malformed Retry-After;preserve and stop") from error
    return dict(
        value=value,
        kind=kind,
        not_before_continuous=header_continuous + seconds,
        header_continuous=header_continuous,
        header_UTC=header_utc.isoformat(),
        UTC_uncertainty="HTTP date seconds precision and local UTC clock uncertainty;"
        "converted once, subsequent elapsed enforcement uses continuous time",
    )


class Transfer(PreviousTransfer):
    """Reuse unchanged owned checkpoint mechanics, never the v2 execution loop."""

    def __init__(self, *args, seed, snapshot=None, **kwargs):
        self.snapshot = snapshot or (
            lambda: dict(
                UTC=datetime.now(UTC).isoformat(),
                ordinary_monotonic_seconds=time.monotonic(),
                continuous_seconds=self.clock(),
                deadline_clock="injected continuous",
            )
        )
        super().__init__(*args, **kwargs)
        path = self.directory / seed["name"]
        s = path.lstat()
        if path.is_symlink() or (s.st_dev, s.st_ino, s.st_size) != (
            seed["device"],
            seed["inode"],
            seed["bytes"],
        ):
            self.journal.close()
            raise ResponseFault("Foreign/mismatched imported seed")
        self.current = dict(
            name=seed["name"],
            device=s.st_dev,
            inode=s.st_ino,
            written_bytes=s.st_size,
            durable_bytes=s.st_size,
            durable_prefix_SHA256=seed["SHA256"],
            imported_seed_bytes=s.st_size,
        )
        self.file = None  # Open for append ONLY after validated exact206.
        self.sha = hashlib.sha256()
        self.state.update(
            files=[self.current],
            historical_seed_bytes_imported=s.st_size,
            written_bytes=s.st_size,
            durably_checkpointed_bytes=s.st_size,
            new_received_bytes=0,
            accepted_complete_bytes=0,
            seed_lineage=seed,
            inflight_uncertainty="network buffers not observed are unknown",
        )
        self.persist()

    def persist(self):
        from raregate.evaluation.guarded_audit import durable

        self.state.update(
            checkpoint_UTC=datetime.now(UTC).isoformat(),
            checkpoint_continuous_seconds=self.clock(),
            clock_snapshot=self.snapshot(),
            new_received_bytes=self.state["received_bytes"],
        )
        checkpoint = dict(
            clock_snapshot=self.state["clock_snapshot"],
            continuous_seconds=self.state["checkpoint_continuous_seconds"],
            source_canonical_JSON_sha256=p.digest(self.source),
            request_count=len(self.state["requests"]),
            imported_seed_bytes=self.state.get("historical_seed_bytes_imported", 0),
            new_received=self.state["received_bytes"],
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
            raise ResponseFault("Bounded8MiB checkpoint journal exhausted")
        self.journal.write(line)
        self.journal.flush()
        os.fsync(self.journal.fileno())
        durable(self.progress, self.state)

    def remaining(self):
        check_deadline(self.clock, self.deadline)
        return self.deadline - self.clock()

    def checkpoint(self, *, clear=False):
        super().checkpoint(clear=clear)

    def owned_file(self, attempt):
        if len(self.state["files"]) >= 7:
            raise ResponseFault("Seven-representation ceiling")
        path = super().owned_file(attempt)
        descriptor = os.open(self.directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return path

    def print_progress(self, reason, force=False):
        if force or self.clock() - self.last_print >= self.policy["progress_seconds"]:
            print(
                f"Task0030 {reason}; requests={len(self.state['requests'])}; "
                f"imported={self.state.get('historical_seed_bytes_imported', 0)} "
                f"new_received={self.state['received_bytes']} written={self.state['written_bytes']} "
                f"durable={self.state['durably_checkpointed_bytes']}",
                flush=True,
            )
            self.last_print = self.clock()

    def wait(self, seconds):
        if seconds + self.policy["minimum_request_slack_seconds"] >= self.remaining():
            raise GuardError("Retry wait cannot fit shared continuous budget")
        row = dict(
            seconds=seconds,
            started=self.snapshot(),
            started_continuous=self.clock(),
            completed=False,
        )
        self.state["waits"].append(row)
        self.state["inflight"] = "retry_wait"
        self.persist()
        until = row["started_continuous"] + seconds
        while self.clock() < until:
            self.remaining()
            self.boundary()
            self.print_progress("retry wait")
            self.sleep(min(1, max(0, until - self.clock())))
        self.remaining()
        row.update(
            completed=True,
            elapsed_continuous_seconds=self.clock() - row["started_continuous"],
        )
        self.state["inflight"] = None
        self.persist()

    def prefix(self, offset, deadline):
        path = self.directory / self.current["name"]
        s = path.lstat()
        if path.is_symlink() or (s.st_dev, s.st_ino, s.st_size) != (
            self.current["device"],
            self.current["inode"],
            offset,
        ):
            raise ResponseFault("Owned continuation identity changed")
        actual = hash_bytes(
            path, clock=self.clock, deadline=deadline, boundary=self.boundary
        )
        if actual["SHA256"] != self.current["durable_prefix_SHA256"]:
            raise ResponseFault("Owned continuation prefix digest changed")
        # Rebuild streaming hash once at each request. Bounded read, no values.
        self.sha = hashlib.sha256()
        with path.open("rb") as stream:
            while True:
                self.remaining()
                chunk = stream.read(65536)
                self.remaining()
                if not chunk:
                    break
                self.sha.update(chunk)
        return path

    def run(self, deadline):
        self.deadline = deadline
        previous = self.state["seed_lineage"].get("response_headers", {})
        try:
            for attempt in range(1, self.policy["max_payload_requests"] + 1):
                self.remaining()
                self.boundary()
                offset = self.current["durable_bytes"]
                if offset >= self.source["expected_size"]:
                    raise ResponseFault("Full uncertain representation;no retry")
                path = self.prefix(offset, deadline)
                request_headers = {
                    "User-Agent": "RareGate/0.1.0 Task0030 bounded-byte-acquisition",
                    "Accept-Encoding": "identity",
                }
                if offset:
                    request_headers["Range"] = f"bytes={offset}-"
                    tag = previous.get("ETag")
                    if tag and not tag.startswith("W/"):
                        request_headers["If-Range"] = tag
                row = dict(
                    number=attempt,
                    offset=offset,
                    started=self.snapshot(),
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
                ra = dict(value=None, not_before_continuous=None, kind="absent")
                try:
                    self.remaining()
                    with self.open_response(
                        Request(self.source["url"], headers=request_headers),
                        timeout=min(
                            self.policy["socket_timeout_seconds"], self.remaining()
                        ),
                    ) as response:
                        received_at, received_utc = self.clock(), datetime.now(UTC)
                        self.remaining()
                        mode, observed = response_mode(
                            response, self.source, offset, previous
                        )
                        row.update(
                            response_status=response.status,
                            mode=mode,
                            response_headers=observed,
                            header_continuous=received_at,
                            header_UTC=received_utc.isoformat(),
                        )
                        ra = retry_after(
                            observed["Retry-After"], received_at, received_utc
                        )
                        row.update(
                            response_status=response.status,
                            mode=mode,
                            response_headers=observed,
                            header_receipt=self.snapshot(),
                            retry_after=ra,
                            status="response_validated",
                            validator_assurance="strong_ETag"
                            if observed["ETag"]
                            and not observed["ETag"].startswith("W/")
                            else "weak_or_missing;full_publisher_MD5_required",
                        )
                        if mode == "restart":
                            self.owned_file(attempt)
                            self.state["restarts"] += 1
                        else:
                            if self.file:
                                self.file.close()
                            self.file = os.fdopen(
                                os.open(
                                    path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW
                                ),
                                "ab",
                                buffering=0,
                            )
                            self.state["continuations"] += 1
                        previous = observed
                        self.checkpoint()
                        while True:
                            self.remaining()
                            self.boundary()
                            self.state["inflight"] = "read_or_write_since_checkpoint"
                            pending = None
                            try:
                                chunk = response.read(self.policy["buffer_bytes"])
                            except http.client.IncompleteRead as error:
                                chunk, pending = error.partial, error
                            self.state["received_bytes"] += len(chunk)
                            self.remaining()  # No further payload write after suspension.
                            if not chunk:
                                if pending:
                                    raise pending
                                break
                            if (
                                self.current["written_bytes"] + len(chunk)
                                > self.source["expected_size"]
                            ):
                                raise ResponseFault(
                                    "Oversized response refused before write"
                                )
                            view = memoryview(chunk)
                            while view:
                                self.remaining()
                                try:
                                    n = self.file.write(view)
                                except OSError as storage_error:
                                    raise ResponseFault(
                                        "Payload storage write failed;no transport retry"
                                    ) from storage_error
                                if n is None or n <= 0:
                                    raise OSError("No write progress")
                                self.sha.update(view[:n])
                                self.current["written_bytes"] += n
                                self.state["written_bytes"] += n
                                self.remaining()
                                view = view[n:]
                            if (
                                self.current["written_bytes"]
                                - self.current["durable_bytes"]
                                >= self.policy["checkpoint_bytes"]
                                or self.clock() - self.last_checkpoint
                                >= self.policy["checkpoint_seconds"]
                            ):
                                self.checkpoint()
                            self.print_progress("transferring")
                            if pending:
                                raise pending
                        self.remaining()
                        self.checkpoint(clear=True)
                        if (
                            self.current["written_bytes"]
                            != self.source["expected_size"]
                        ):
                            raise Truncated("EOF before pinned full size")
                        row["status"] = "complete_expected_bytes_unverified"
                        row["ended"] = self.snapshot()
                        self.state.update(
                            status="transfer_complete_unverified",
                            complete_file=self.current["name"],
                        )
                        self.persist()
                        self.remaining()
                        return self.directory / self.current["name"]
                except Exception as error:
                    if isinstance(error, HTTPError):
                        at, utc = self.clock(), datetime.now(UTC)
                        observed = headers(error)
                        row.update(
                            response_status=error.code,
                            response_headers=observed,
                            header_continuous=at,
                            header_UTC=utc.isoformat(),
                        )
                        if error.geturl() != self.source["url"]:
                            error.close()
                            raise ResponseFault(
                                "HTTP error source URL changed"
                            ) from error
                        try:
                            ra = retry_after(observed["Retry-After"], at, utc)
                        except BaseException:
                            error.close()
                            raise
                        row.update(
                            response_status=error.code,
                            response_headers=observed,
                            header_receipt=self.snapshot(),
                            retry_after=ra,
                        )
                        error.close()
                    row.update(
                        status="interrupted_or_failed",
                        error=f"{type(error).__name__}: {error}",
                        ended=self.snapshot(),
                        retryable=retryable(error),
                    )
                    if isinstance(error, ResponseFault) and "Redirect refused" in str(
                        error
                    ):
                        self.state["redirects_observed"] += 1
                    self.checkpoint()  # Preserve observed bytes and uncertainty.
                    if (
                        not retryable(error)
                        or attempt == self.policy["max_payload_requests"]
                    ):
                        raise
                    self.remaining()
                    if self.current["durable_bytes"] >= self.source["expected_size"]:
                        raise ResponseFault(
                            "Full uncertain interrupted body;preserve without retry"
                        ) from error
                    minimum = self.policy["retry_backoff_seconds"][attempt - 1]
                    remaining_ra = max(
                        0, (ra["not_before_continuous"] or self.clock()) - self.clock()
                    )
                    row["recovery"] = dict(
                        minimum_backoff_seconds=minimum,
                        remaining_retry_after_seconds=remaining_ra,
                        planned_wait_seconds=max(minimum, remaining_ra),
                        computed_continuous=self.clock(),
                    )
                    self.wait(max(minimum, remaining_ra))
            raise GuardError("Six-request budget exhausted")
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
