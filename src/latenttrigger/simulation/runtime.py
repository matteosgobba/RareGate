"""Minimal Task0037 adapters over inspected continuous/macOS guard utilities."""

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
from latenttrigger.simulation import protocol as p

__all__ = [
    "ContinuousClock",
    "IdleAssertion",
    "alarm",
    "check_deadline",
    "supervise",
    "parent_check",
    "SimulationGuard",
    "storage_check",
    "check_access",
    "install_boundary",
    "accept_body",
]


class SimulationGuard(Guard):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("journal_limit", p.LIMITS["guard_journal_bytes"])
        super().__init__(*args, **kwargs)
        self.previous_query = None
        self.max_gap = 0.0

    def check(self):
        with self.lock:
            check_deadline(self.clock, self.deadline)
            super().check()
            check_deadline(self.clock, self.deadline)
            tick = self.last["query_start"]
            if self.previous_query is not None:
                self.max_gap = max(self.max_gap, tick - self.previous_query)
            self.previous_query = tick
            if self.last["peak_rss_bytes"] > p.LIMITS["worker_RSS_bytes"]:
                self.error = self.error or "Task0037 explicit1GiB RSS ceiling"
                self._record()
                raise GuardError(self.error)

    def report(self):
        return dict(
            **super().report(),
            worker_RSS_ceiling_bytes=2**30,
            max_query_start_gap_continuous_seconds=self.max_gap,
            scope="sampled lifetime RSS/native through monitor closure; terminal gap disclosed",
        )


def storage_check(directory):
    total = 0
    for path in directory.rglob("*"):
        p.require(not path.is_symlink(), "Owned output symlink")
        if path.is_file():
            n = path.stat().st_size
            ceiling = (
                64 * 2**20
                if path.name == "guards.jsonl"
                else 2**20
                if path.suffix == ".log"
                else 4 * 2**20
                if path.suffix in (".csv", ".json")
                else 8 * 2**20
                if path.suffix == ".png"
                else 128 * 2**20
            )
            p.require(n <= ceiling, "Owned file bound: " + path.name)
            total += n
    p.require(total <= 128 * 2**20, "128MiB owned storage ceiling")
    return total


def check_access(root, owned, phase, event, args):
    if event in (
        "socket.connect",
        "socket.bind",
        "urllib.Request",
        "subprocess.Popen",
        "os.system",
        "os.exec",
        "os.posix_spawn",
    ):
        raise PermissionError("Synthetic workers forbid network/child execution")
    if event == "import" and any(
        args[0] == m or args[0].startswith(m + ".")
        for m in (
            "torch",
            "sklearn",
            "h5py",
            "scipy",
            "latenttrigger.models",
            "latenttrigger.training",
            "latenttrigger.preprocessing",
        )
    ):
        raise PermissionError(
            "Simulator/reporting prohibit model/population frameworks"
        )
    if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).absolute()
    real = path.resolve()
    mode, flags = args[1:3]
    writing = (isinstance(mode, str) and any(v in mode for v in "wax+")) or (
        isinstance(flags, int)
        and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
    )
    if writing:
        if not path.is_relative_to(owned) or not real.is_relative_to(owned):
            raise PermissionError("Write outside owned output")
    else:
        forbidden = [root / n for n in ("data", "results", "artifacts", "sources")]
        allowed = {root / n for n in p.PINS} if phase == "simulation" else set()
        if (
            any(path.is_relative_to(n) or real.is_relative_to(n) for n in forbidden)
            and not (path.is_relative_to(owned) and real.is_relative_to(owned))
            and not (path == real and real in allowed)
        ):
            raise PermissionError(
                "No source/operational reads; reporting owned aggregates only"
            )
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
    ):
        raise PermissionError("No event/model array files, including owned arrays")


def install_boundary(root, owned, phase):
    root, owned = Path(root).resolve(), Path(owned).resolve()
    sys.addaudithook(lambda event, args: check_access(root, owned, phase, event, args))


def accept_body(body, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    resources = body.get("resources", {})
    outputs = body.get("outputs", {})
    expected = (
        {"aggregates.json", "scenarios.csv"}
        if grant["phase"] == "simulation"
        else {"latency.png", "loss.png", "sensitivity.png", "reporting.json"}
    )
    p.require(
        body.get("status") == "body_complete_awaiting_exit"
        and body.get("phase") == grant["phase"]
        and body.get("source_map") == grant["source_map"] == p.source_map()
        and body.get("dependencies") == grant["dependencies"] == p.dependencies()
        and body.get("grant_sha256") == p.file_hash(directory / "grant.json")
        and set(outputs) == expected,
        "Current-source complete body identity",
    )
    p.require(
        dispatch.get("returncode") == 0
        and type(dispatch.get("returncode")) is int
        and dispatch.get("parent_confirms_normal_exit") is True
        and dispatch.get("child_reaped") is True
        and dispatch.get("within_deadline") is True
        and dispatch.get("parent_error") is None,
        "Normal exit/reaped/continuous deadline",
    )
    p.require(
        resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
        and type(resources.get("peak_rss_bytes")) is int
        and 0 < resources["peak_rss_bytes"] <= 2**30
        and type(resources.get("native_heap_reserved_bytes")) is int
        and 0 < resources["native_heap_reserved_bytes"] <= 512 * 2**20
        and type(body.get("cleanup_seconds")) in (int, float)
        and 0 <= body["cleanup_seconds"] <= 2
        and body.get("worker_seconds", float("inf"))
        <= p.LIMITS[grant["phase"] + "_seconds"],
        "Resource/cleanup ceilings",
    )
    for name, sha in outputs.items():
        p.require(p.file_hash(directory / name) == sha, "Altered owned output")
    if grant["phase"] == "simulation":
        c = body.get("counters", {})
        p.require(
            c.get("synthetic_scenarios_started")
            == c.get("synthetic_scenarios_completed")
            == 378
            and c.get("synthetic_event_presentations_started")
            == c.get("synthetic_event_presentations_completed")
            == 1890000
            and c.get("synthetic_unique_traces") == 18
            and c.get("synthetic_unique_events") == 90000
            and c.get("curated_timing_table_metadata_loads") == 3
            and c.get("new_simulator_model_instantiations_or_forward_calls") == 0,
            "Complete durable synthetic counters",
        )
        p.require(
            p.read(directory / "counters.json") == c, "Durable counters agreement"
        )
        # Parent stays stdlib-only; worker independently validates the full matrix.
        from latenttrigger.simulation.sweep import validate_aggregates

        report = validate_aggregates(p.read(directory / "aggregates.json"))
        p.require(report["counters"] == c, "Aggregate counter agreement")
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
