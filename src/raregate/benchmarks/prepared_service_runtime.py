"""Narrow Task0038 adapters; continuous time is independent of timer samples."""

import os
import sys
from pathlib import Path

from raregate.benchmarks import prepared_service_protocol as p
from raregate.benchmarks.guard import Guard, parent_check
from raregate.benchmarks.guard import GuardError as BenchmarkGuardError
from raregate.data.three_prong_v3_runtime import (
    ContinuousClock,
    IdleAssertion,
    alarm,
    check_deadline,
    supervise,
)
from raregate.evaluation.guard import GuardError

__all__ = [
    "GuardError",
    "parent_check",
    "ContinuousClock",
    "IdleAssertion",
    "alarm",
    "check_deadline",
    "supervise",
    "ServiceGuard",
    "storage",
    "boundary",
    "accept",
]


class ServiceGuard(Guard):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("journal_limit", 16 * 2**20)
        super().__init__(*args, **kwargs)
        self.previous = None
        self.max_gap = 0.0

    def check(self):
        with self.lock:
            try:
                check_deadline(self.clock, self.deadline)
                super().check()
            except (GuardError, BenchmarkGuardError) as exc:
                self.error = self.error or str(exc)
                raise GuardError(self.error) from exc
            tick = self.last["query_start"]
            if self.previous is not None:
                self.max_gap = max(self.max_gap, tick - self.previous)
            self.previous = tick
            if self.last["peak_rss_bytes"] > 2**30:
                self.error = "Task0038 explicit1GiB RSS veto"
                raise GuardError(self.error)
            check_deadline(self.clock, self.deadline)

    def report(self):
        return dict(
            **super().report(),
            worker_RSS_ceiling_bytes=2**30,
            max_query_start_gap_seconds=self.max_gap,
        )


def storage(directory):
    total = 0
    for path in Path(directory).rglob("*"):
        p.require(not path.is_symlink(), "Owned symlink")
        if path.is_file():
            size = path.stat().st_size
            cap = (
                16 * 2**20
                if path.name == "guards.jsonl"
                else 2**20
                if path.suffix == ".log"
                else 16 * 2**20
            )
            p.require(size <= cap, "Per-file storage bound")
            total += size
    p.require(total <= 128 * 2**20, "Owned128MiB total storage")
    return total


def check_access(root, owned, allowed, event, args):
    if event in (
        "socket.connect",
        "socket.bind",
        "urllib.Request",
        "subprocess.Popen",
        "os.system",
        "os.exec",
        "os.posix_spawn",
    ):
        raise PermissionError("Worker network/child execution forbidden")
    if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).absolute()
    real = path.resolve()
    mode, flags = args[1:3]
    writing = (isinstance(mode, str) and any(v in mode for v in "wax+")) or (
        isinstance(flags, int)
        and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
    )
    own = path.is_relative_to(owned) and real.is_relative_to(owned)
    if writing and not own:
        raise PermissionError("Write outside owned output")
    if not writing:
        protected = any(
            path.is_relative_to(root / n) or real.is_relative_to(root / n)
            for n in ("data", "results", "artifacts", "sources")
        )
        if protected and not own and not (path == real and real in allowed):
            raise PermissionError("Unallowed operational source")
        if path.suffix.lower() in (
            ".npy",
            ".npz",
            ".pt",
            ".pth",
            ".h5",
            ".hdf5",
            ".root",
            ".parquet",
        ) and not (path == real and real in allowed):
            raise PermissionError("Array access forbidden")


def boundary(directory, *, numerical, synthetic):
    allowed = (
        {p.ROOT / n for n in p.load()["byte_pins"]}
        if numerical and not synthetic
        else set()
    )
    sys.addaudithook(
        lambda event, args: check_access(p.ROOT, directory, allowed, event, args)
    )


def accept(body, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    p.require(
        body.get("status") == "body_complete_awaiting_exit"
        and body.get("grant_sha256") == p.file_hash(directory / "grant.json")
        and body.get("source_map") == grant["source_map"] == p.source_map()
        and body.get("dependencies") == grant["dependencies"] == p.dependencies(),
        "Body/source/grant identity",
    )
    p.require(
        type(dispatch.get("returncode")) is int
        and dispatch["returncode"] == 0
        and dispatch.get("parent_confirms_normal_exit") is True
        and dispatch.get("child_reaped") is True
        and dispatch.get("within_deadline") is True
        and dispatch.get("parent_error") is None,
        "Normal exit/reaping/deadline required",
    )
    r = body["resources"]
    p.require(
        r["latched_error"] is None
        and r["owned_thread_alive"] is False
        and 0 < r["peak_rss_bytes"] <= 2**30
        and 0 < r["native_heap_reserved_bytes"] <= 512 * 2**20
        and body["cleanup_seconds"] <= 2,
        "Resources/cleanup",
    )
    cap = 60 if grant["phase"] == "reporting" else 120
    p.require(
        0 <= body.get("worker_seconds", 0) <= cap, "Continuous worker duration ceiling"
    )
    expected = (
        {"probe.json"}
        if grant["phase"] == "probe"
        else {"cells.csv", "aggregate.json", "timings.jsonl"}
        if grant["phase"].startswith("repetition")
        else {
            "partial-cost.png",
            "paired-difference.png",
            "chronology.png",
            "reporting.json",
        }
    )
    p.require(set(body["outputs"]) == expected, "Complete owned outputs")
    for name, sha in body["outputs"].items():
        p.require(p.file_hash(directory / name) == sha, "Output identity")
    return dict(
        status="parent_accepted_worker",
        terminal_unmonitored_gap_seconds=max(
            0, dispatch["end_continuous"] - body["monitor_closed_continuous"]
        ),
        normal_exit_reaped=True,
    )
