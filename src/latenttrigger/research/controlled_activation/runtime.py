"""Task0035 narrow adapters: fixed 1GiB/128MiB storage, continuous lifecycle."""

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
from latenttrigger.research.controlled_activation import protocol as p

__all__ = [
    "ContinuousClock",
    "IdleAssertion",
    "alarm",
    "check_deadline",
    "supervise",
    "parent_check",
    "SyntheticGuard",
    "storage_check",
    "install_boundary",
    "accept_body",
]


class SyntheticGuard(Guard):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("journal_limit", p.LIMITS["guard_journal_bytes"])
        super().__init__(*args, **kwargs)
        self.last_query = None
        self.max_gap = 0.0

    def check(self):
        with self.lock:
            check_deadline(self.clock, self.deadline)
            super().check()
            check_deadline(self.clock, self.deadline)
            tick = self.last["query_start"]
            if self.last_query is not None:
                self.max_gap = max(self.max_gap, tick - self.last_query)
            self.last_query = tick
            if self.last["peak_rss_bytes"] > p.LIMITS["worker_RSS_bytes"]:
                self.error = self.error or "Task0035 explicit 1GiB RSS ceiling"
                self._record()
                raise GuardError(self.error)

    def report(self):
        return dict(
            **super().report(),
            worker_RSS_ceiling_bytes=2**30,
            max_query_start_gap_continuous_seconds=self.max_gap,
            scope="sampled lifetime RSS/native; no continuous memory or physical-suspension certificate",
        )


def storage_check(base):
    total = 0
    for path in base.rglob("*"):
        p.require(not path.is_symlink(), "Symlink in owned synthetic workspace")
        if path.is_file():
            size = path.stat().st_size
            total += size
            limit = (
                p.LIMITS["guard_journal_bytes"]
                if path.name == "guards.jsonl"
                else p.LIMITS["worker_log_bytes"]
                if path.suffix == ".log"
                else 2**20
                if path.suffix == ".json"
                else p.LIMITS["storage_bytes"]
            )
            p.require(size <= limit, "Owned file ceiling: " + path.name)
    p.require(total <= p.LIMITS["storage_bytes"], "128MiB total owned storage")
    return total


def check_open(root, owned, allowed, event, args):
    if event in (
        "socket.connect",
        "socket.bind",
        "urllib.Request",
        "subprocess.Popen",
        "os.system",
        "os.exec",
        "os.posix_spawn",
    ):
        raise PermissionError(
            "Synthetic numerical worker: network/child execution prohibited"
        )
    if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).absolute()
    # Reject symlink aliases by comparing both lexical and canonical targets.
    real = path.resolve()
    mode, flags = args[1:3]
    writing = (isinstance(mode, str) and any(v in mode for v in "wax+")) or (
        isinstance(flags, int)
        and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
    )
    if writing and (not path.is_relative_to(owned) or not real.is_relative_to(owned)):
        raise PermissionError("Write outside owned synthetic fixtures")
    forbidden = [root / name for name in ("data", "results", "artifacts", "sources")]
    if not writing and any(
        real.is_relative_to(v) or path.is_relative_to(v) for v in forbidden
    ):
        if real not in allowed and not real.is_relative_to(owned):
            raise PermissionError("Operational/synced source read prohibited")
    if path.suffix.lower() in (
        ".npy",
        ".npz",
        ".h5",
        ".hdf5",
        ".pt",
        ".pth",
        ".ckpt",
        ".root",
        ".parquet",
    ):
        raise PermissionError(
            "No numerical or model-file input path; synthetic arrays generated in memory"
        )


def install_boundary(root, owned):
    root, owned = Path(root).resolve(), Path(owned).resolve()
    allowed = {root / name for name in p.DESIGN_FILES}
    sys.addaudithook(lambda event, args: check_open(root, owned, allowed, event, args))


def accept_body(body, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    r = body.get("resources", {})
    c = body.get("counters", {})
    expected = {
        "report.json",
        "counters.json",
        *[f"initialization-{s}.json" for s in p.SEEDS],
        *[f"checkpoint-{arm}-{s}.json" for arm, s in p.ORDER],
    }
    p.require(
        body.get("status") == "body_complete_awaiting_exit"
        and body.get("source_map") == grant["source_map"] == p.source_map()
        and body.get("dependencies") == grant["dependencies"] == p.runtime_versions()
        and body.get("grant_sha256") == p.file_hash(directory / "grant.json")
        and body.get("config_sha256")
        == grant["config_sha256"]
        == p.file_hash(p.ROOT / p.CONFIG)
        and dispatch.get("parent_confirms_normal_exit") is True
        and dispatch.get("child_reaped") is True
        and dispatch.get("within_deadline") is True
        and dispatch.get("returncode") == 0
        and type(dispatch.get("returncode")) is int
        and dispatch.get("parent_error") is None
        and r.get("latched_error") is None
        and r.get("owned_thread_alive") is False
        and type(r.get("peak_rss_bytes")) is int
        and 0 < r["peak_rss_bytes"] <= 2**30
        and type(r.get("native_heap_reserved_bytes")) is int
        and 0 < r["native_heap_reserved_bytes"] <= 512 * 2**20
        and type(body.get("cleanup_seconds")) in (int, float)
        and 0 <= body["cleanup_seconds"] <= 2
        and all(
            type(c.get(k)) is int and c[k] >= 0
            for k in (
                "model_instances",
                "forward_calls",
                "forward_rows",
                "reconstruction_computations",
                "optimizer_steps_started",
                "optimizer_steps_completed",
                "optimizer_steps_inflight",
                "synthetic_calibrations",
            )
        )
        and c["model_instances"] == 9
        and c["forward_calls"] > 0
        and c["forward_rows"] > 0
        and c["reconstruction_computations"] == c["forward_calls"]
        and c.get("optimizer_steps_started") == c.get("optimizer_steps_completed") == 12
        and c.get("optimizer_steps_inflight") == 0
        and c.get("synthetic_calibrations") == 6
        and body.get("all_pairing_restoration_checks") is True
        and set(body.get("outputs", {})) == expected,
        "Body-complete rejected by lifecycle/source/counter/resource acceptance",
    )
    for name, sha in body["outputs"].items():
        p.require(
            "/" not in name and p.file_hash(directory / name) == sha,
            "Altered owned output",
        )
    p.require(p.read(directory / "counters.json") == c, "Durable counters differ")
    report = p.read(directory / "report.json")
    p.require(
        report["kind"] == "synthetic_only"
        and len(report["arms"]) == 6
        and len(report["pairs"]) == 3
        and [(r["arm"], r["seed"]) for r in report["arms"]] == list(p.ORDER)
        and all(
            r["restoration"]["selected_bytes_verified"] is True
            and r["restoration"]["selected_score_identity"] is True
            and r["restoration"]["complete_epochs"] == 2
            and r["restoration"]["selected_epoch"] in (1, 2)
            for r in report["arms"]
        )
        and [r["seed"] for r in report["pairs"]] == list(p.SEEDS)
        and all(
            r["identical_consumed_orders"] is True
            and r["common_epochs"] == 2
            and r["missing_later_epochs"] == 0
            for r in report["pairs"]
        )
        and report["decision"]["claim_permitted"] is False
        and report["decision"]["label"] == "inconclusive",
        "Toy acceptance must remain inconclusive",
    )
    storage_check(directory)
    check_deadline(clock, deadline)
    return dict(
        status="parent_accepted_synthetic",
        outputs=body["outputs"],
        terminal_unaccounted_continuous_seconds=max(
            0, dispatch["exit_observed_continuous"] - body["monitor_closed_continuous"]
        ),
    )
