"""One owned system-vm_stat sampler; immutable bounded-age host observations."""

import json
import math
import os
import selectors
import socket
import subprocess
import threading
import time
from dataclasses import asdict, dataclass, replace

from latenttrigger.supervision.particle_host import ResourceLimitError, parse_vm_stat

BACKEND = "system_vm_stat_oneshot_host_v4"
CADENCE = 0.05
MAX_AGE = 0.1
MAX_RAW = 16384


def stamp(value):
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
        raise ResourceLimitError("Missing/backward/nonfinite monotonic timestamp.")
    return value


@dataclass(frozen=True)
class HostObservation:
    issuer: str
    generation: int
    query_start: float
    query_end: float
    published_at: float
    page_size_bytes: int
    free_pages: int
    inactive_pages: int
    available_bytes: int
    backend: str
    validated: bool
    synthetic: bool
    raw: str

    def age(self, now, issuer):
        stamp(now)
        for t in (self.query_start, self.query_end, self.published_at):
            stamp(t)
        if (
            self.issuer != issuer
            or type(self.generation) is not int
            or self.generation < 1
            or self.backend != BACKEND
            or self.validated is not True
            or not self.query_start <= self.query_end <= self.published_at <= now
        ):
            raise ResourceLimitError(
                "Invalid host generation/provenance/timestamp order."
            )
        age = now - self.query_start
        if age > MAX_AGE:
            raise ResourceLimitError("Host observation age exceeds100ms.")
        return age

    def primary(self):
        return {
            "page_size_bytes": self.page_size_bytes,
            "free_pages": self.free_pages,
            "inactive_pages": self.inactive_pages,
            "available_bytes": self.available_bytes,
            "available_gib": self.available_bytes / 2**30,
            "available_method": "Darwin_free_plus_inactive_pages",
        }


def observation(row, issuer, generation, now):
    if row.get("backend") != BACKEND or type(row.get("synthetic", False)) is not bool:
        raise ResourceLimitError("Unsupported host collector/provenance.")
    for k in ("page_size_bytes", "free_pages", "inactive_pages", "available_bytes"):
        if type(row.get(k)) is not int or row[k] < 0:
            raise ResourceLimitError("Malformed primary host accounting.")
    if (
        not row["page_size_bytes"]
        or row["available_bytes"]
        != (row["free_pages"] + row["inactive_pages"]) * row["page_size_bytes"]
    ):
        raise ResourceLimitError("Host byte arithmetic mismatch.")
    if type(row.get("raw")) is not str or len(row["raw"].encode()) > MAX_RAW:
        raise ResourceLimitError("Missing/unbounded raw system observation.")
    parsed = parse_vm_stat(row["raw"])
    if any(
        row[k] != parsed[k]
        for k in ("page_size_bytes", "free_pages", "inactive_pages", "available_bytes")
    ):
        raise ResourceLimitError("Raw/parsed primary observation mismatch.")
    o = HostObservation(
        issuer,
        generation,
        row["query_start"],
        row["query_end"],
        now,
        row["page_size_bytes"],
        row["free_pages"],
        row["inactive_pages"],
        row["available_bytes"],
        BACKEND,
        True,
        row.get("synthetic", False),
        row["raw"],
    )
    o.age(now, issuer)
    return o


class SystemQuery:
    """Nonblocking lifecycle of a single owned one-shot query (never a stream)."""

    def __init__(self, *, clock=time.monotonic):
        self.clock = clock
        self.child = None
        self.buffer = bytearray()
        self.eof = False
        self._owner_lock = threading.Lock()

    def begin(self):
        with self._owner_lock:
            if self.child is not None:
                raise ResourceLimitError("Overlapping host subprocess refused.")
            self.query_start = self.clock()
            self.buffer.clear()
            self.eof = False
            self.child = subprocess.Popen(
                ["/usr/bin/vm_stat"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
            )
            os.set_blocking(self.child.stdout.fileno(), False)
            return self.child.stdout.fileno()

    def drain(self):
        if self.child is None:
            raise ResourceLimitError("Missing owned host query.")
        data = os.read(self.child.stdout.fileno(), MAX_RAW + 1)
        if data:
            self.buffer.extend(data)
            if len(self.buffer) > MAX_RAW:
                raise ResourceLimitError("Unbounded system snapshot.")
        else:
            self.eof = True
        return self.eof

    def finish(self):
        if self.child is None:
            return None
        if self.clock() - self.query_start > 2:
            raise ResourceLimitError("System host query2s timeout.")
        if not self.eof or self.child.poll() is None:
            return None
        with self._owner_lock:
            if self.child.returncode != 0:
                raise ResourceLimitError("Owned vm_stat query failed.")
            raw = self.buffer.decode("utf-8", errors="strict")
            end = self.clock()
            self.child.stdout.close()
            self.child = None
        return {
            **parse_vm_stat(raw),
            "backend": BACKEND,
            "query_start": self.query_start,
            "query_end": end,
            "raw": raw,
            "synthetic": False,
        }

    def close(self):
        with self._owner_lock:
            if self.child:
                if self.child.poll() is None:
                    self.child.terminate()
                    try:
                        self.child.wait(timeout=0.2)
                    except subprocess.TimeoutExpired:
                        self.child.kill()
                        self.child.wait(timeout=2)
                self.child.stdout.close()
                self.child = None


class Sampler:
    """Only issuer of host queries; callback checks process caps while query pending."""

    def __init__(
        self,
        issuer,
        *,
        collector=None,
        on_observation=lambda _: None,
        on_tick=lambda _: None,
        on_failure=lambda _: None,
        clock=time.monotonic,
    ):
        self.issuer, self.clock = issuer, clock
        self.collector = SystemQuery(clock=clock) if collector is None else collector
        self.on_observation, self.on_tick, self.on_failure = (
            on_observation,
            on_tick,
            on_failure,
        )
        self.condition = threading.Condition()
        self.latest = None
        self.error = None
        self.generation = 0
        self.host_queries = 0
        self.skipped_intervals = 0
        self.query_count_completed = 0
        self.query_seconds = 0.0
        self.max_query_seconds = 0.0
        self.thread_cpu_seconds = 0.0
        self.refresh_after = None
        self.done = False
        self.thread = None
        self._read, self._write = socket.socketpair()
        self._read.setblocking(False)
        self._write.setblocking(False)

    def wake(self):
        try:
            self._write.send(b"x")
        except (BlockingIOError, OSError):
            pass

    def fail(self, exc):
        notify = False
        with self.condition:
            if self.error is None:
                self.error = str(exc)
                notify = True
            self.condition.notify_all()
        if notify:
            self.on_failure(self.error)
        self.wake()

    def get(self):
        with self.condition:
            if self.error:
                raise ResourceLimitError(self.error)
            value = self.latest
        if value is None:
            raise ResourceLimitError("No complete validated host observation.")
        value.age(self.clock(), self.issuer)
        return value

    def start(self):
        if self.thread is not None:
            raise ResourceLimitError("Sampler cannot restart.")
        self.thread = threading.Thread(
            target=self._loop, name="particle-v4-sampler", daemon=True
        )
        self.thread.start()

    def refresh(self):
        requested = self.clock()
        stamp(requested)
        with self.condition:
            if self.error:
                raise ResourceLimitError(self.error)
            self.refresh_after = max(requested, self.refresh_after or requested)
        self.wake()
        deadline = time.monotonic() + MAX_AGE
        with self.condition:
            while True:
                if self.error:
                    raise ResourceLimitError(self.error)
                value = self.latest
                if value and value.query_start >= requested:
                    value.age(self.clock(), self.issuer)
                    return value
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self.condition.wait(remaining)
        self.fail(
            ResourceLimitError(
                "Fresh synchronous host refresh unavailable within100ms."
            )
        )
        raise ResourceLimitError(self.error)

    def _loop(self):
        thread_cpu = time.thread_time()
        selector = selectors.DefaultSelector()
        selector.register(self._read, selectors.EVENT_READ, "wake")
        now = self.clock()
        next_query = next_process = now
        active_fd = None
        try:
            while not self.done and not self.error:
                now = self.clock()
                stamp(now)
                with self.condition:
                    requested = self.refresh_after
                if self.collector.child is None and (
                    now >= next_query or requested is not None
                ):
                    active_fd = self.collector.begin()
                    self.host_queries += 1
                    selector.register(active_fd, selectors.EVENT_READ, "host")
                    if now >= next_query:
                        missed = max(0, int((now - next_query) / CADENCE))
                        self.skipped_intervals += missed
                        next_query += (missed + 1) * CADENCE
                elif self.collector.child is not None and now >= next_query:
                    missed = max(1, int((now - next_query) / CADENCE) + 1)
                    self.skipped_intervals += missed
                    next_query += missed * CADENCE
                if now >= next_process:
                    self.on_tick(self.latest)
                    next_process = now + CADENCE
                row = self.collector.finish()
                if row is not None:
                    duration = stamp(row["query_end"]) - stamp(row["query_start"])
                    if duration < 0:
                        raise ResourceLimitError("Backward host query timestamp.")
                    self.query_count_completed += 1
                    self.query_seconds += duration
                    self.max_query_seconds = max(self.max_query_seconds, duration)
                    if active_fd is not None:
                        selector.unregister(active_fd)
                        active_fd = None
                    value = observation(
                        row, self.issuer, self.generation + 1, self.clock()
                    )
                    self.on_observation(value)
                    value = replace(value, published_at=self.clock())
                    value.age(self.clock(), self.issuer)
                    with self.condition:
                        if self.error:
                            break
                        self.generation = value.generation
                        self.latest = value
                        if (
                            self.refresh_after is not None
                            and value.query_start >= self.refresh_after
                        ):
                            self.refresh_after = None
                        self.condition.notify_all()
                now = self.clock()
                # No busy polling: wait for pipe/wakeup or next periodic process/host tick.
                timeout = max(
                    0,
                    min(
                        next_process,
                        next_query if self.collector.child is None else next_process,
                    )
                    - now,
                )
                for key, _ in selector.select(timeout):
                    if key.data == "wake":
                        try:
                            self._read.recv(4096)
                        except BlockingIOError:
                            pass
                    elif self.collector.drain():
                        selector.unregister(key.fd)
                        active_fd = None
        except BaseException as exc:
            if not self.done:
                self.fail(exc)
        finally:
            self.collector.close()
            selector.close()
            self.thread_cpu_seconds = time.thread_time() - thread_cpu
            with self.condition:
                self.condition.notify_all()

    def close(self):
        self.done = True
        self.wake()
        if self.thread:
            self.thread.join(timeout=2.25)
        if self.thread and self.thread.is_alive():
            self.collector.close()
            self.wake()
            self.thread.join(timeout=2.25)
        self._read.close()
        self._write.close()
        if self.thread and self.thread.is_alive():
            raise ResourceLimitError("Owned sampler cleanup failed.")

    def report(self):
        return {
            "host_queries_started": self.host_queries,
            "host_generations_published": self.generation,
            "skipped_host_schedule_intervals": self.skipped_intervals,
            "host_queries_completed": self.query_count_completed,
            "overlapping_host_query_wall_seconds": self.query_seconds,
            "maximum_host_query_wall_seconds": self.max_query_seconds,
            "sampling_thread_process_cpu_seconds": self.thread_cpu_seconds,
            "latched_failure": self.error,
            "owned_thread_alive": self.thread.is_alive() if self.thread else False,
        }


def raw_record(obs):
    return asdict(obs)


def append_bounded(handle, value, limit=32 * 2**20):
    encoded = json.dumps(value, allow_nan=False, separators=(",", ":")) + "\n"
    if handle.tell() + len(encoded.encode()) > limit:
        raise ResourceLimitError("Bounded resource journal ceiling exceeded.")
    handle.write(encoded)
    handle.flush()
