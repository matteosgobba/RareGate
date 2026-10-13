"""Task0040 ceilings and lifecycle adapters; no historical controller changes."""

import sys

from latenttrigger.benchmarks import development_payload_protocol as p
from latenttrigger.benchmarks.development_raw_runtime import check_access
from latenttrigger.benchmarks.guard import parent_check
from latenttrigger.benchmarks.prepared_service_runtime import ServiceGuard, storage
from latenttrigger.data.three_prong_v3_runtime import (
    ContinuousClock,
    IdleAssertion,
    alarm,
    check_deadline,
    supervise,
)

__all__ = [
    "ServiceGuard",
    "storage",
    "ContinuousClock",
    "IdleAssertion",
    "alarm",
    "check_deadline",
    "supervise",
    "parent_check",
    "boundary",
    "accept",
    "accounting",
]


def boundary(directory, grant):
    allowed = set()
    if not grant["synthetic_only"] and grant["phase"] != "reporting":
        allowed = {
            p.ROOT / v for v in (*p.load()["byte_pins"], p.MEMBERSHIP, p.RAW, p.GOLDEN)
        }
    if grant["phase"] == "reporting":
        allowed = {
            directory.parent / f"repetition{i}" / name
            for i in (1, 2, 3)
            for name in ("aggregate.json", "receipt.json", "grant.json")
        }
    sys.addaudithook(
        lambda event, args: check_access(p.ROOT, directory, allowed, event, args)
    )


def accounting(a):
    p.require(
        a["membership_loads"] == 1
        and a["membership_records_inspected"] == 6999
        and a["selected_IDs"] == 1024
        and a["membership_inflight"] is False
        and a["golden_loads"] == 1
        and a["golden_rows"] == 1024
        and a["golden_inflight"] is False
        and a["HDF_opens"] == 1
        and a["HDF_closed"] is True
        and a["raw_requests"] == a["raw_returned_requests"] == 244
        and a["raw_requested_rows"] == a["raw_returned_rows"] == 10309
        and a["feature_requests"] == a["feature_completed_calls"] == 256
        and a["feature_requested_rows"] == a["feature_completed_rows"] == 10816
        and a["inflight"] is None,
        "Exact per-worker access conservation",
    )
    p.require(
        a["by_component"]
        == dict(
            timing=dict(
                raw_requests=184, raw_rows=7774, feature_calls=184, feature_rows=7774
            ),
            preload=dict(
                raw_requests=12, raw_rows=507, feature_calls=0, feature_rows=0
            ),
            gate=dict(
                raw_requests=48, raw_rows=2028, feature_calls=72, feature_rows=3042
            ),
        ),
        "Timing/preload/gate access split",
    )


def accept(body, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    p.require(
        body["status"] == "body_complete_awaiting_exit"
        and body["grant_sha256"] == p.file_hash(directory / "grant.json")
        and body["source_map"] == grant["source_map"] == p.source_map()
        and body["dependencies"] == grant["dependencies"] == p.dependencies(),
        "Complete frozen body",
    )
    p.require(
        type(dispatch.get("returncode")) is int
        and dispatch["returncode"] == 0
        and dispatch["parent_confirms_normal_exit"] is True
        and dispatch["child_reaped"] is True
        and dispatch["within_deadline"] is True
        and dispatch["parent_error"] is None,
        "Normal exit/reaping/continuous cap",
    )
    r = body["resources"]
    cap = 60 if grant["phase"] == "reporting" else 180
    p.require(
        r["latched_error"] is None
        and r["owned_thread_alive"] is False
        and 0 < r["peak_rss_bytes"] <= 2**30
        and 0 < r["native_heap_reserved_bytes"] <= 512 * 2**20
        and body["cleanup_seconds"] <= 2
        and body["worker_seconds"] <= cap,
        "Resources/cleanup/worker caps",
    )
    expected = (
        {
            "cells.csv",
            "summary.json",
            "scope-cost.png",
            "chronology.png",
            "geometry.png",
        }
        if grant["phase"] == "reporting"
        else {"aggregate.json", "timings.jsonl", "timer.json"}
    )
    p.require(set(body["outputs"]) == expected, "Fixed output coverage")
    for name, sha in body["outputs"].items():
        p.require(p.file_hash(directory / name) == sha, "Output identity")
    if grant["phase"] != "reporting":
        accounting(body["access"])
    return dict(
        status="parent_accepted_worker",
        normal_exit_reaped=True,
        terminal_resource_gap_seconds=max(
            0, dispatch["end_continuous"] - body["monitor_closed_continuous"]
        ),
    )
