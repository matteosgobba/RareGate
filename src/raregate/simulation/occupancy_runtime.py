"""Task0046 boundary and acceptance over unchanged clock/assertion/resource guards."""

import os
import re
import stat
import sys
from pathlib import Path

from raregate.simulation import occupancy_protocol as p
from raregate.simulation.runtime import (
    ContinuousClock,
    IdleAssertion,
    SimulationGuard,
    alarm,
    check_deadline,
    parent_check,
    supervise,
)

__all__ = [
    "ContinuousClock",
    "IdleAssertion",
    "SimulationGuard",
    "alarm",
    "check_deadline",
    "parent_check",
    "supervise",
    "storage_check",
    "install_boundary",
    "accept_body",
]


def storage_check(directory):
    total = journals = 0
    for path in directory.rglob("*"):
        try:
            info = path.lstat()
        except FileNotFoundError:
            p.require(
                re.fullmatch(r".+\.json\.[0-9a-f]{32}\.tmp", path.name) is not None,
                "Only vanished owned atomic JSON temporary may race",
            )
            continue
        p.require(not stat.S_ISLNK(info.st_mode), "Owned storage symlink")
        if stat.S_ISREG(info.st_mode):
            n = info.st_size
            limit = (
                64 * 2**20
                if path.name == "guards.jsonl"
                else 2**20
                if path.suffix == ".log"
                else 32 * 2**20
                if path.suffix == ".csv"
                else 4 * 2**20
                if path.suffix == ".json"
                else 8 * 2**20
                if path.suffix == ".png"
                else 128 * 2**20
            )
            p.require(n <= limit, "Owned file ceiling")
            total += n
            journals += n if path.name == "guards.jsonl" else 0
    p.require(journals <= 64 * 2**20, "64MiB combined guard journals")
    p.require(total <= 128 * 2**20, "128MiB owned output")
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
        raise PermissionError("Replay workers prohibit network/subprocesses")
    if event == "import" and any(
        args[0] == m or args[0].startswith(m + ".")
        for m in (
            "torch",
            "sklearn",
            "h5py",
            "raregate.models",
            "raregate.training",
            "raregate.preprocessing",
            "raregate.benchmarks",
            "raregate.data",
        )
    ):
        raise PermissionError("No model/raw/scientific imports")
    if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).absolute()
    real = path.resolve()
    mode, flags = args[1:3]
    writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
        isinstance(flags, int)
        and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
    )
    if writing:
        if not path.is_relative_to(owned) or not real.is_relative_to(owned):
            raise PermissionError("Owned phase writes only")
    elif any(
        path.is_relative_to(root / n) or real.is_relative_to(root / n)
        for n in ("data", "results", "artifacts", "sources", "models", "checkpoints")
    ):
        if not (path == real and (path in allowed or path.is_relative_to(owned))):
            raise PermissionError("Declared timing provenance reads only")
    if path.suffix.lower() in (
        ".npy",
        ".npz",
        ".h5",
        ".hdf5",
        ".root",
        ".pt",
        ".pth",
        ".ckpt",
        ".parquet",
        ".onnx",
    ):
        raise PermissionError("Forbidden source dereference including owned arrays")


def install_boundary(root, owned, allowed):
    root, owned = Path(root).resolve(), Path(owned).resolve()
    sys.addaudithook(
        lambda event, args: check_access(root, owned, allowed, event, args)
    )


def accept_body(body, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    resources = body["resources"]
    outputs = body.get("outputs", {})
    expected = (
        {
            "summary.json",
            "scenarios.csv",
            "contrasts.csv",
            "occupancies.csv",
            "anchor-audit.csv",
        }
        if grant["phase"] == "simulation"
        else {"outcomes.png", "latency.png", "sensitivity.png", "reporting.json"}
    )
    p.require(
        body["status"] == "body_complete_awaiting_exit"
        and body["phase"] == grant["phase"]
        and body["identity"] == p.identity()
        and body["source_map"] == grant["source_map"] == p.source_map()
        and body["dependencies"] == grant["dependencies"] == p.dependencies()
        and body["grant_sha256"] == p.file_hash(directory / "grant.json")
        and set(outputs) == expected,
        "Complete Task0046 body identity",
    )
    p.require(
        type(dispatch["returncode"]) is int
        and dispatch["returncode"] == 0
        and dispatch["parent_confirms_normal_exit"] is True
        and dispatch["child_reaped"] is True
        and dispatch["within_deadline"] is True
        and dispatch["parent_error"] is None,
        "Normal exit/reaped/deadlines",
    )
    p.require(
        resources["latched_error"] is None
        and resources["owned_thread_alive"] is False
        and 0 < resources["peak_rss_bytes"] <= 2**30
        and 0 < resources["native_heap_reserved_bytes"] <= 512 * 2**20
        and 0 <= body["cleanup_seconds"] <= 2
        and body["worker_seconds"] <= p.LIMITS[grant["phase"] + "_seconds"],
        "Worker resource/cleanup ceilings",
    )
    for n, sha in outputs.items():
        p.require(p.file_hash(directory / n) == sha, "Independent output byte check")
    if grant["phase"] == "simulation":
        summary = p.read(directory / "summary.json")
        c = summary["counters"]
        p.require(
            c["scenarios_started"] == c["scenarios_completed"] == 3024
            and c["event_presentations_started"]
            == c["event_presentations_completed"]
            == 15120000
            and c["synthetic_trace_generation_requests"] == 18
            and c["synthetic_unique_events"] == 90000
            and c["inflight"] is None
            and c == p.read(directory / "counters.json"),
            "Full durable coverage counters",
        )
    storage_check(directory)
    check_deadline(clock, deadline)
    return dict(
        status="parent_accepted_phase",
        phase=grant["phase"],
        outputs=outputs,
        terminal_unaccounted_continuous_seconds=max(
            0, dispatch["exit_observed_continuous"] - body["monitor_closed_continuous"]
        ),
    )
