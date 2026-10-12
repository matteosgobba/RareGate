"""Task0033-specific 1 GiB cap and finite I/O on Task0030 continuous runtime."""

import os
import sys
from pathlib import Path

from latenttrigger.data.three_prong_v3_runtime import (
    ContinuousClock,
    IdleAssertion,
    alarm,
    check_deadline,
    supervise,
)
from latenttrigger.evaluation.guard import Guard, GuardError, parent_check

__all__ = [
    "ContinuousClock",
    "IdleAssertion",
    "alarm",
    "check_deadline",
    "supervise",
    "parent_check",
    "DiagnosticGuard",
    "install_boundary",
    "storage_check",
]


class DiagnosticGuard(Guard):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("journal_limit", 64 * 2**20)
        super().__init__(*args, **kwargs)
        self.previous_query = None
        self.max_query_gap = 0.0

    def check(self):
        with self.lock:
            super().check()
            tick = self.last["query_start"]
            if self.previous_query is not None:
                self.max_query_gap = max(self.max_query_gap, tick - self.previous_query)
            self.previous_query = tick
            # Explicitly narrower than the immutable historical 6 GiB guard.
            if self.last["peak_rss_bytes"] > 2**30:
                self.error = self.error or "Task0033 1 GiB worker RSS ceiling exceeded"
                self._record()
                raise GuardError(self.error)

    def report(self):
        return dict(
            **super().report(),
            task0033_worker_rss_limit_bytes=2**30,
            max_observed_query_start_gap_continuous_seconds=self.max_query_gap,
            monitoring_scope="sampled primary lifetime RSS/native reservations until monitor closure; parent remains active until reaping; terminal interval disclosed",
        )


def storage_check(base):
    total = 0
    for path in base.rglob("*"):
        if path.is_symlink():
            raise GuardError("Symlink in owned operational output")
        if path.is_file():
            size = path.stat().st_size
            total += size
            if path.name == "guards.jsonl" and size > 64 * 2**20:
                raise GuardError("Guard journal storage exceeded")
            if path.suffix == ".log" and size > 2**20:
                raise GuardError("Worker log exceeded")
            if path.name == "access.json" and size > 2**20:
                raise GuardError("Access journal storage exceeded")
            if path.suffix == ".csv" and size > 2 * 2**20:
                raise GuardError("Aggregate storage exceeded")
            if path.suffix == ".png" and size > 8 * 2**20:
                raise GuardError("Figure storage exceeded")
            if path.suffix == ".json" and size > 4 * 2**20:
                raise GuardError("JSON storage exceeded")
    if total > 256 * 2**20:
        raise GuardError("Total session storage exceeded")
    return total


def install_boundary(root, arrays, metadata, owned, *, phase):
    """Reject operational reads outside the finite input list and all source writes."""
    root, owned = Path(root).resolve(), Path(owned).resolve()
    allowed = {root / name for name in [*arrays, *metadata]}
    if phase == "reporting":
        allowed = {p for p in allowed if p.suffix != ".npy"}
    operational = [root / name for name in ("data", "results", "artifacts")]

    def audit(event, args):
        if event in ("socket.connect", "urllib.Request"):
            raise PermissionError("Task0033 network access prohibited")
        if event == "import" and any(
            args[0] == name or args[0].startswith(name + ".")
            for name in ("torch", "sklearn", "h5py", "scipy", "latenttrigger.models")
        ):
            raise PermissionError("Task0033 candidate/statistical framework prohibited")
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).absolute()
        mode, flags = args[1:3]
        writing = (isinstance(mode, str) and any(v in mode for v in "wax+")) or (
            isinstance(flags, int)
            and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        )
        if writing:
            if not path.is_relative_to(owned):
                raise PermissionError("Write outside owned worker output: " + str(path))
        elif (
            any(path.is_relative_to(folder) for folder in operational)
            and path not in allowed
            and not path.is_relative_to(owned)
        ):
            raise PermissionError("Read outside Task0033 input allowlist: " + str(path))
        if path.suffix in (".npy", ".npz") and path not in allowed:
            raise PermissionError("Unapproved numerical array: " + str(path))

    sys.addaudithook(audit)
