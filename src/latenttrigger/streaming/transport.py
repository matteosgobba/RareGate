"""One12288-byte ring. Every shared control/slot access holds its spawn mutex."""

import mmap
import os
import struct
from pathlib import Path

from . import quota
from .protocol import (
    CONTROL_BYTES,
    MAGIC,
    MAX_U64,
    SHARED_BYTES,
    SLOT_BYTES,
    SLOTS,
    TIMEOUT_NS,
    Descriptor,
    metadata,
    read_metadata,
    require,
    uint,
)

# Every counter is aligned little-endian u64, offsets16..143; bytes152..4095 zero.
FIELDS = (
    "head",
    "tail",
    "pending",
    "staged",
    "active",
    "completed",
    "failed",
    "cancelled",
    "producer_ready",
    "consumer_ready",
    "producer_closed",
    "error",
    "t0",
    "producer_rss",
    "consumer_rss",
    "progress",
    "producer_armed",
)
OFFSETS = {name: 16 + 8 * i for i, name in enumerate(FIELDS)}
U64 = struct.Struct("<Q")


class Region:
    """File-backed MAP_SHARED region in an owned fixture directory, no fallback.

    This is actual shared memory, not a file-message queue: all slots/counters are
    accessed through the one12288-byte mapping while holding the shared mutex.
    The backing file adds12288bytes of owned fixture storage, not another buffer.
    """

    size = SHARED_BYTES

    def __init__(self, path, create=False):
        path = Path(path)
        repo = Path(__file__).resolve().parents[3]
        require(
            path.is_absolute()
            and (
                (
                    path.is_relative_to(repo / "data/task0051-validation")
                    or path.is_relative_to(repo / "data/task0052-validation")
                    or path.is_relative_to(repo / "data/task0053-validation")
                    or path.is_relative_to(repo / "data/task0054-validation")
                    or path.is_relative_to(repo / "data/task0055-validation")
                )
                or path.is_relative_to(Path("/private/tmp"))
                or path.is_relative_to(Path("/tmp"))
            ),
            "Fixture-only region root",
        )
        require(path.parent == path.parent.resolve(), "No symlinked region parent")
        require(
            path.is_absolute()
            and path.name == "fixture-ring.shm"
            and path.parent.is_dir()
            and not path.is_symlink(),
            "Owned fixture region path",
        )
        require(
            (
                (
                    quota.CURRENT.root
                    if quota.CURRENT is not None
                    else path.parent.parent
                )
                / "owner.json"
            ).is_file(),
            "Explicit fixture output ownership",
        )
        self.name = str(path)
        self.fd = quota.open_file(
            path,
            os.O_RDWR | (os.O_CREAT | os.O_EXCL if create else 0) | os.O_NOFOLLOW,
            0o600,
        )
        try:
            if create:
                quota.truncate(self.fd, SHARED_BYTES)
            require(os.fstat(self.fd).st_size == SHARED_BYTES, "Region exact length")
            self.buf = mmap.mmap(self.fd, SHARED_BYTES, access=mmap.ACCESS_WRITE)
            quota.track_mapping(self.buf, self.fd)
        except Exception:
            quota.close(self.fd)
            raise
        self.closed = False

    def close(self):
        if not self.closed:
            self.buf.close()
            quota.retire_mapping(self.buf)
            quota.close(self.fd)
            self.closed = True

    def unlink(self):
        os.unlink(self.name)


class Ring:
    def __init__(self, shm, lock, owner=False):
        require(shm.size == SHARED_BYTES, "Exact shared allocation")
        self.shm, self.lock, self.owner = shm, lock, owner
        self.closed = False

    @classmethod
    def create(cls, lock, directory):
        shm = Region(Path(directory) / "fixture-ring.shm", create=True)
        shm.buf[:] = bytes(SHARED_BYTES)
        shm.buf[:8] = MAGIC
        struct.pack_into("<II", shm.buf, 8, 1, SLOTS)
        return cls(shm, lock, True)

    @classmethod
    def attach(cls, name, lock):
        shm = Region(name)
        try:
            obj = cls(shm, lock)
            require(
                bytes(shm.buf[:8]) == MAGIC
                and struct.unpack_from("<II", shm.buf, 8) == (1, 64),
                "Ring header",
            )
            return obj
        except Exception:
            shm.close()
            raise

    def _get(self, name):
        return U64.unpack_from(self.shm.buf, OFFSETS[name])[0]

    def _set(self, name, value):
        U64.pack_into(self.shm.buf, OFFSETS[name], uint(value))

    def _invariant(self):
        h, t = self._get("head"), self._get("tail")
        require(h <= t and t - h <= SLOTS, "Ring indices")
        require(
            self._get("pending")
            == t - h + self._get("staged") + self._get("active")
            <= SLOTS,
            "Credit conservation",
        )
        require(
            self._get("staged") <= 8 and self._get("active") <= 8, "Stage/active bound"
        )

    def update(self, **values):
        require(self.lock.acquire(timeout=0.05), "Status mutex unavailable")
        try:
            for key, value in values.items():
                self._set(key, value)
        finally:
            self.lock.release()

    def snapshot(self):
        if not self.lock.acquire(False):
            return None
        try:
            self._invariant()
            return {k: self._get(k) for k in FIELDS}
        finally:
            self.lock.release()

    def admit(self, descriptor, clock):
        blob = descriptor.encode()  # malformed input has no shared side effect
        if not self.lock.acquire(False):
            return "rejected_contention", clock(), None
        try:
            self._invariant()
            stamp = clock()
            if self._get("pending") == SLOTS:
                return "rejected_capacity", stamp, None
            tail = self._get("tail")
            require(tail < MAX_U64, "Sequence overflow")
            offset = CONTROL_BYTES + (tail % SLOTS) * SLOT_BYTES
            self.shm.buf[offset : offset + 64] = blob
            self.shm.buf[offset + 64 : offset + 128] = metadata(stamp, tail)
            # Tail publication under the shared mutex is the admission linearization.
            self._set("tail", tail + 1)
            self._set("pending", self._get("pending") + 1)
            self._set("progress", stamp)
            self._invariant()
            return "admitted", stamp, tail
        finally:
            self.lock.release()

    def stage(self, clock):
        if not self.lock.acquire(False):
            return []
        try:
            self._invariant()
            require(
                self._get("staged") == self._get("active") == 0, "Single service owner"
            )
            head, tail = self._get("head"), self._get("tail")
            count = tail - head
            if not count:
                return []
            now = clock()
            start = CONTROL_BYTES + (head % SLOTS) * SLOT_BYTES
            oldest, _ = read_metadata(bytes(self.shm.buf[start + 64 : start + 128]))
            require(now >= oldest, "Clock before admission")
            if (
                count < 8
                and now - oldest < TIMEOUT_NS
                and not self._get("producer_closed")
            ):
                return []
            batch = []
            for i in range(min(8, count)):
                offset = CONTROL_BYTES + ((head + i) % SLOTS) * SLOT_BYTES
                d = Descriptor.decode(bytes(self.shm.buf[offset : offset + 64]))
                admission, seq = read_metadata(
                    bytes(self.shm.buf[offset + 64 : offset + 128])
                )
                require(seq == head + i, "FIFO sequence")
                batch.append((d, admission, seq, now))
            self._set("head", head + len(batch))  # slot reusable, credit still held
            self._set("staged", len(batch))
            self._invariant()
            return batch
        finally:
            self.lock.release()

    def activate(self, m, clock):
        require(self.lock.acquire(timeout=0.05), "Dispatch mutex")
        try:
            require(
                self._get("active") == 0 and self._get("staged") == m and 1 <= m <= 8,
                "Dispatch shape",
            )
            self._set("staged", 0)
            self._set("active", m)
            self._set("progress", clock())
            self._invariant()
        finally:
            self.lock.release()

    def finish(self, m, clock, terminal="completed"):
        require(terminal in ("completed", "failed", "cancelled"), "Terminal state")
        require(self.lock.acquire(timeout=0.05), "Terminal mutex")
        try:
            require(
                self._get("active") == m and 1 <= m <= 8, "Exactly one credit release"
            )
            require(self._get(terminal) <= MAX_U64 - m, "Terminal counter overflow")
            stamp = uint(clock())
            self._set("active", 0)
            self._set("pending", self._get("pending") - m)
            self._set(terminal, self._get(terminal) + m)
            self._set("progress", stamp)
            self._invariant()
            return stamp
        finally:
            self.lock.release()

    def close(self):
        if not self.closed:
            self.shm.close()
            self.closed = True

    def unlink(self):
        require(self.owner, "Only supervisor unlinks")
        try:
            self.shm.unlink()
            return True
        except FileNotFoundError:
            return False
