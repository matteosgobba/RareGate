"""Task0053 immutable whole-task file reservations, explicit generated activation only."""

import json
import os
import stat
from pathlib import Path

CAP = 16 * 1024**2
CURRENT = None
FDS = {}


class QuotaError(ValueError):
    pass


def check(condition, message):
    if not condition:
        raise QuotaError(message)


class Ledger:
    def __init__(self, root, entries, *, task="0053"):
        check(task in ("0053", "0054", "0055"), "Explicit task quota")
        self.task = task
        self.cap = CAP if task == "0053" else 32 * 1024**2
        self.root = Path(root)
        check(
            self.root.is_absolute() and self.root == self.root.resolve(),
            "Canonical owned root",
        )
        check(len(entries) <= 512, "File cardinality")
        self.entries = entries
        check(
            all(type(n) is int and n >= 0 for n in entries.values()), "Finite file caps"
        )
        check(
            sum(entries.values()) <= self.cap,
            "Whole-task reservation exceeds scoped cap",
        )
        for name in entries:
            check(
                not Path(name).is_absolute() and ".." not in Path(name).parts,
                "Ledger path escape",
            )

    def path(self, path, end=0):
        path = Path(path)
        check(
            path.is_absolute() and path.is_relative_to(self.root), "Outside owned root"
        )
        name = str(path.relative_to(self.root))
        check(name in self.entries, "Undeclared diagnostic path")
        check(
            type(end) is int and 0 <= end <= self.entries[name],
            "Pre-growth quota rejected",
        )
        # Includes existing leaf and every parent; no symlink aliases accepted.
        current = self.root
        for part in Path(name).parts:
            current /= part
            check(not current.is_symlink(), "Symlink in owned path")
        check(path.parent.resolve() == path.parent, "Noncanonical parent")
        return path

    def open(self, path, flags, mode=0o600):
        path = self.path(path)
        check(
            not flags & os.O_TRUNC,
            "Use guarded truncate, never truncate evidence on open",
        )
        fd = os.open(path, flags | os.O_NOFOLLOW, mode)
        try:
            info = os.fstat(fd)
            check(
                stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                "One owned regular file",
            )
            self.path(path, info.st_size)
        except Exception:
            os.close(fd)
            raise
        if len(FDS) >= 16:
            os.close(fd)
            raise QuotaError("Owned diagnostic descriptor cardinality")
        FDS[fd] = (self, path)
        return fd

    def write_bytes(self, path, blob):
        self.path(path, len(blob))  # reject before creation, not after output exists
        fd = self.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        try:
            check(pwrite(fd, blob, 0) == len(blob), "Short owned write")
        finally:
            close(fd)

    def write_json(self, path, value):
        # Cardinality and scalar bounds before encoder allocation. Streaming chunks
        # are guarded before growth; interrupted/short files remain evidence.
        validate_tree(value)
        self.path(path, encoded_size(value) + 1)
        fd = self.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        offset = 0
        try:
            for chunk in json.JSONEncoder(
                allow_nan=False, separators=(",", ":")
            ).iterencode(value):
                blob = chunk.encode("utf-8")
                check(len(blob) <= 262144, "Serialization chunk bound")
                check(pwrite(fd, blob, offset) == len(blob), "Short JSON write")
                offset += len(blob)
            check(pwrite(fd, b"\n", offset) == 1, "Short final newline")
        finally:
            close(fd)

    def rename_temp(self, source, target):
        source = self.path(source)
        check(source.name.endswith(".tmp"), "Only declared temporary can rename")
        target = self.path(target, source.stat().st_size)
        check(not target.exists(), "No evidence replacement")
        # Both simultaneous paths were reserved at full caps; reservation never freed.
        os.rename(source, target)

    def inventory(self):
        logical = blocks = files = 0
        for p in self.root.rglob("*"):
            check(not p.is_symlink(), "Owned metadata symlink")
            if p.is_file():
                info = p.stat()
                self.path(p, info.st_size)
                logical += info.st_size
                blocks += info.st_blocks * 512
                files += 1
        check(
            logical <= sum(self.entries.values()) <= self.cap,
            "Whole-task actual/reserved bound",
        )
        return dict(
            logical_bytes=logical,
            allocated_file_blocks_bytes=blocks,
            file_count=files,
            reserved_bytes=sum(self.entries.values()),
            cap_bytes=self.cap,
            filesystem_kernel_metadata_bytes=None,
        )


def validate_tree(value):
    count = 0

    def visit(x, depth=0):
        nonlocal count
        count += 1
        check(
            count <= 24000 and depth <= 24, "Bounded JSON container cardinality/depth"
        )
        if isinstance(x, dict):
            check(len(x) <= 512, "Bounded dictionary")
            for k, v in x.items():
                check(isinstance(k, str) and len(k) <= 4096, "Bounded JSON key")
                visit(v, depth + 1)
        elif isinstance(x, (list, tuple)):
            check(len(x) <= 4096, "Bounded list")
            for v in x:
                visit(v, depth + 1)
        elif isinstance(x, str):
            check(len(x) <= 65536, "Bounded JSON string")
        else:
            check(x is None or isinstance(x, (int, float, bool)), "JSON scalar")

    visit(value)


def activate(root):
    global CURRENT
    root = Path(root)
    path = root / "ledger.json"
    check(not path.is_symlink() and path.stat().st_size <= 65536, "Ledger metadata")
    data = json.loads(path.read_text())
    check(data["task"] in ("0053", "0054", "0055"), "Task ledger identity")
    CURRENT = Ledger(root, data["files"], task=data["task"])
    check(data["cap_bytes"] == CURRENT.cap, "Scoped task cap")
    return CURRENT


def open_file(path, flags, mode=0o600):
    if CURRENT is None:
        return os.open(path, flags, mode)
    return CURRENT.open(path, flags, mode)


def truncate(fd, length):
    if fd in FDS:
        ledger, path = FDS[fd]
        cap = ledger.entries[str(path.relative_to(ledger.root))]
        check(
            type(length) is int and 0 <= length <= cap, "Pre-growth truncate rejected"
        )
    else:
        check(CURRENT is None, "Unregistered diagnostic descriptor")
    os.ftruncate(fd, length)


def pwrite(fd, blob, offset):
    if fd in FDS:
        ledger, path = FDS[fd]
        cap = ledger.entries[str(path.relative_to(ledger.root))]
        # The open regular inode is already owned/checked; pwrite never follows a
        # pathname. Full cap was reserved before open, without hot-path stat calls.
        check(
            type(offset) is int and 0 <= offset and offset + len(blob) <= cap,
            "Pre-growth write rejected",
        )
    else:
        check(CURRENT is None, "Unregistered diagnostic descriptor")
    return os.pwrite(fd, blob, offset)


def close(fd):
    try:
        os.close(fd)
    finally:
        FDS.pop(fd, None)


def encoded_size(value):
    """Exact compact JSON byte count with bounded scalar temporaries, before open."""
    if isinstance(value, dict):
        return (
            2
            + max(0, len(value) - 1)
            + sum(encoded_size(k) + 1 + encoded_size(v) for k, v in value.items())
        )
    if isinstance(value, (list, tuple)):
        return 2 + max(0, len(value) - 1) + sum(encoded_size(v) for v in value)
    chunk = json.dumps(value, allow_nan=False, separators=(",", ":")).encode()
    check(len(chunk) <= 262144, "Bounded scalar encoding")
    return len(chunk)


MAPPINGS = []


def track_mapping(mapping, fd):
    if CURRENT is not None:
        check(len(MAPPINGS) < 3, "Mapping cardinality")
        check(
            sum(len(m) for m, _ in MAPPINGS) + len(mapping) <= 143360,
            "Mapped byte cardinality",
        )
        MAPPINGS.append((mapping, fd))


def retire_mapping(mapping):
    MAPPINGS[:] = [(m, fd) for m, fd in MAPPINGS if m is not mapping]


def emergency_release(previous_fds, case):
    """Independent of diagnostics and ring mutex, even partial pre-start setup."""
    errors = []
    owned = set(FDS) - set(previous_fds)
    for mapping, fd in list(MAPPINGS):
        if fd in owned:
            try:
                mapping.close()
            except (OSError, ValueError, BufferError) as exc:
                errors.append(str(exc))
            finally:
                retire_mapping(mapping)
    for fd in owned:
        try:
            close(fd)
        except OSError as exc:
            errors.append(str(exc))
    path = Path(case) / "fixture-ring.shm"
    try:
        if path.exists():
            CURRENT.path(path, path.stat().st_size)
            path.unlink()  # resource retirement, full reservation remains charged
    except (OSError, QuotaError) as exc:
        errors.append(str(exc))
    return errors
