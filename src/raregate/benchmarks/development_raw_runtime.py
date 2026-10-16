"""Task0039 metadata scope over preserved continuous/sleep/process utilities."""

import os
import sys
from pathlib import Path

from raregate.benchmarks import development_raw_protocol as p
from raregate.benchmarks.guard import parent_check
from raregate.benchmarks.prepared_service_runtime import ServiceGuard
from raregate.data.three_prong_v3_runtime import (
    ContinuousClock,
    IdleAssertion,
    alarm,
    check_deadline,
    supervise,
)

__all__ = [
    "ServiceGuard",
    "ContinuousClock",
    "IdleAssertion",
    "alarm",
    "check_deadline",
    "supervise",
    "parent_check",
    "boundary",
    "storage",
    "accept",
]


def check_access(root, owned, allowed, event, args):
    if event in (
        "socket.connect",
        "socket.bind",
        "subprocess.Popen",
        "os.system",
        "os.exec",
        "os.posix_spawn",
        "urllib.Request",
    ):
        raise PermissionError("Resolver/fixtures forbid network and child execution")
    if event == "import" and any(
        args[0] == name or args[0].startswith(name + ".")
        for name in (
            "torch",
            "sklearn",
            "raregate.models",
            "raregate.training",
            "raregate.data.preprocessing",
            "raregate.data.processed",
        )
    ):
        raise PermissionError(
            "No model, store, preprocessing controller or broad validator"
        )
    if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).absolute()
    real = path.resolve()
    mode, flags = args[1:3]
    writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
        isinstance(flags, int)
        and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
    )
    own = path.is_relative_to(owned) and real.is_relative_to(owned)
    if writing and not own:
        raise PermissionError("Only owned writes")
    protected = any(
        path.is_relative_to(root / n) or real.is_relative_to(root / n)
        for n in ("data", "results", "artifacts", "sources")
    )
    if not writing and protected and not own and not (path == real and real in allowed):
        raise PermissionError("Unallowed operational source")
    if path.suffix.lower() in (".npz", ".pt", ".pth", ".root", ".parquet"):
        raise PermissionError("Operational array/model files forbidden")


def boundary(owned, synthetic):
    allowed = (
        set()
        if synthetic
        else {
            p.ROOT / n for n in (*p.load()["byte_pins"], p.MEMBERSHIP, p.GOLDEN, p.RAW)
        }
    )
    sys.addaudithook(
        lambda event, args: check_access(p.ROOT, owned, allowed, event, args)
    )


def storage(directory):
    total = 0
    for path in directory.rglob("*"):
        p.require(not path.is_symlink(), "Owned symlink")
        if path.is_file():
            cap = (
                16 * 2**20
                if path.name == "guards.jsonl"
                else 2**20
                if path.suffix == ".log"
                else 16 * 2**20
            )
            p.require(path.stat().st_size <= cap, "Owned per-file cap")
            total += path.stat().st_size
    p.require(total <= 32 * 2**20, "Resolver32MiB owned cap")
    return total


def accept(body, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    p.require(
        body["status"] == "body_complete_awaiting_exit"
        and body["source_map"] == grant["source_map"] == p.source_map()
        and body["dependencies"] == grant["dependencies"] == p.dependencies()
        and body["grant_sha256"] == p.file_hash(directory / "grant.json"),
        "Complete source-bound body",
    )
    p.require(
        type(dispatch.get("returncode")) is int
        and dispatch["returncode"] == 0
        and dispatch["parent_confirms_normal_exit"] is True
        and dispatch["child_reaped"] is True
        and dispatch["within_deadline"] is True
        and dispatch["parent_error"] is None,
        "Normal exit/reaping/continuous deadlines",
    )
    r = body["resources"]
    p.require(
        r["latched_error"] is None
        and r["owned_thread_alive"] is False
        and 0 < r["peak_rss_bytes"] <= 2**30
        and 0 < r["native_heap_reserved_bytes"] <= 512 * 2**20
        and body["cleanup_seconds"] <= 2
        and body["worker_seconds"] <= 60,
        "Resource/cleanup caps",
    )
    expected = (
        {"synthetic.json", "geometry.json", "selected-ids.npy"}
        if grant["synthetic_only"]
        else {"metadata.json", "geometry.json", "selected-ids.npy"}
    )
    p.require(set(body["outputs"]) == expected, "Complete fixed owned outputs")
    for name, sha in body["outputs"].items():
        p.require(p.file_hash(directory / name) == sha, "Output identity")
    if not grant["synthetic_only"]:
        a = body["access"]
        p.require(
            a["membership_loads"] == 1
            and a["membership_records_inspected"] == 6999
            and a["selected_IDs"] == 1024
            and a["membership_inflight"] is False
            and a["raw_HDF_metadata_opens"] == 1
            and a["HDF_handle_closed"] is True
            and a["HDF_metadata_inflight"] is False
            and a["raw_hash_passes"] == 1
            and a["raw_hash_bytes"] == 2908260409,
            "Exact membership/hash/metadata-only accounting",
        )
    return dict(
        status="parent_accepted_metadata_worker",
        terminal_resource_gap_seconds=max(
            0, dispatch["end_continuous"] - body["monitor_closed_continuous"]
        ),
    )
