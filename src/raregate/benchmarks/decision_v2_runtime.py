"""Minimal Task0043 source boundary/parent receipt checks over unchanged guards."""

import sys

from raregate.benchmarks import decision_v2_protocol as p
from raregate.benchmarks import development_decision_runtime as shared

ContinuousClock, IdleAssertion, alarm, check_deadline, supervise = (
    shared.ContinuousClock,
    shared.IdleAssertion,
    shared.alarm,
    shared.check_deadline,
    shared.supervise,
)
ServiceGuard, parent_check, inherited_storage, accounting, ProhibitedOperations = (
    shared.ServiceGuard,
    shared.parent_check,
    shared.storage,
    shared.accounting,
    shared.ProhibitedOperations,
)


def storage(base):
    total = inherited_storage(base)
    for phase in ("repetition1", "repetition2", "repetition3", "reporting"):
        directory = base / phase
        if directory.exists():
            journal_bytes = sum(f.stat().st_size for f in directory.glob("*.jsonl"))
            p.require(
                journal_bytes <= 16 * 2**20, "Combined owned worker journals16MiB"
            )
    return total


def boundary(directory, grant):
    allowed = set()
    if grant["phase"] == "reporting":
        allowed = {
            directory.parent / f"repetition{i}" / name
            for i in (1, 2, 3)
            for name in ("aggregate.json", "receipt.json", "grant.json")
        }
    elif not grant["synthetic_only"]:
        spec = p.load()
        allowed = {
            p.ROOT / name
            for name in (
                *spec["byte_pins"],
                *(v["path"] for v in spec["historical_acceptances"].values()),
                p.MEMBERSHIP,
                p.RAW,
                p.GOLDEN,
            )
        }
        # Original-map verification may read only the specific preserved source paths.
        allowed.update(
            p.ROOT / "data/task0042-validation/preserved-original/issued-source" / name
            for name in (
                "scripts/validate_development_raw_decisions.py",
                "src/raregate/benchmarks/development_decision_protocol.py",
                "src/raregate/benchmarks/development_decision_native.py",
                "src/raregate/benchmarks/development_decision_runtime.py",
                "tests/test_development_decision_grants.py",
                "tests/test_development_decision_runtime.py",
            )
        )
    sys.addaudithook(
        lambda event, args: shared.check_access(
            p.ROOT,
            directory,
            allowed,
            event,
            args,
            synthetic=grant["synthetic_only"] and grant["phase"] != "reporting",
        )
    )


def accept(body, dispatch, grant, directory, clock, deadline, *, root=p.ROOT):
    check_deadline(clock, deadline)
    p.require(
        body["status"] == "body_complete_awaiting_exit"
        and body["task"] == "0043"
        and body["identity"] == grant["identity"] == p.identity(root)
        and body["grant_sha256"] == p.file_hash(directory / "grant.json")
        and body["source_map"] == grant["source_map"] == p.source_map(root)
        and body["dependencies"] == grant["dependencies"] == p.dependencies(),
        "Complete Task0043 body/bindings",
    )
    p.require(
        type(dispatch["returncode"]) is int
        and dispatch["returncode"] == 0
        and dispatch["parent_confirms_normal_exit"] is True
        and dispatch["child_reaped"] is True
        and dispatch["within_deadline"] is True
        and dispatch["parent_error"] is None,
        "Normal exit/reaping/deadline",
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
        "Resources/cleanup cap",
    )
    names = (
        {"cells.csv", "summary.json", "joint-cost.png", "chronology.png"}
        if grant["phase"] == "reporting"
        else {"aggregate.json", "timings.jsonl", "timer.json"}
    )
    p.require(set(body["outputs"]) == names, "Fixed output set")
    for name, sha in body["outputs"].items():
        p.require(p.file_hash(directory / name) == sha, "Output bytes")
    if grant["phase"] != "reporting":
        accounting(body["access"])
    return dict(
        task="0043",
        status="parent_accepted_worker",
        normal_exit_reaped=True,
        terminal_resource_gap_seconds=max(
            0, dispatch["end_continuous"] - body["monitor_closed_continuous"]
        ),
    )
