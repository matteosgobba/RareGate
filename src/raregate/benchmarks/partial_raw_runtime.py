"""Minimal Task0045 source boundary/parent receipt checks over unchanged guards."""

import re
import stat
import sys

from raregate.benchmarks import development_decision_runtime as shared
from raregate.benchmarks import partial_raw_protocol as p

ContinuousClock, IdleAssertion, alarm, check_deadline, supervise = (
    shared.ContinuousClock,
    shared.IdleAssertion,
    shared.alarm,
    shared.check_deadline,
    shared.supervise,
)
ServiceGuard, parent_check, ProhibitedOperations = (
    shared.ServiceGuard,
    shared.parent_check,
    shared.ProhibitedOperations,
)


def storage(base):
    total = 0
    for path in base.rglob("*"):
        try:
            info = path.lstat()
        except FileNotFoundError:
            # A durable JSON atomic rename can remove its own temporary between
            # enumeration and stat. Reserve its complete maximum rather than
            # terminating a healthy worker or discounting unknown bytes.
            p.require(
                re.fullmatch(r".+\.json\.[0-9a-f]{32}\.tmp", path.name) is not None,
                "Only owned atomic JSON temporary may disappear",
            )
            total += 4 * 2**20
            continue
        p.require(not stat.S_ISLNK(info.st_mode), "Owned symlink")
        if stat.S_ISREG(info.st_mode):
            p.require(
                info.st_size <= (2**20 if path.suffix == ".log" else 16 * 2**20),
                "Per-file storage bound",
            )
            total += info.st_size
    p.require(total <= 128 * 2**20, "Owned128MiB total storage")
    all_journals = 0
    for phase in ("", "repetition1", "repetition2", "repetition3", "reporting"):
        directory = base / phase
        if directory.exists():
            journal_bytes = sum(f.stat().st_size for f in directory.glob("*.jsonl"))
            all_journals += journal_bytes
            p.require(
                journal_bytes <= 16 * 2**20, "Combined owned worker journals16MiB"
            )
    p.require(all_journals <= 64 * 2**20, "Session64MiB combined journals")
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
        and body["task"] == "0045"
        and body["identity"] == grant["identity"] == p.identity(root)
        and body["grant_sha256"] == p.file_hash(directory / "grant.json")
        and body["source_map"] == grant["source_map"] == p.source_map(root)
        and body["dependencies"] == grant["dependencies"] == p.dependencies(),
        "Complete Task0045 body/bindings",
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
        {
            "cells.csv",
            "pairs.csv",
            "summary.json",
            "joint-cost.png",
            "paired-cost.png",
            "chronology.png",
        }
        if grant["phase"] == "reporting"
        else {"aggregate.json", "timings.jsonl", "timer.json"}
    )
    p.require(set(body["outputs"]) == names, "Fixed output set")
    for name, sha in body["outputs"].items():
        p.require(p.file_hash(directory / name) == sha, "Output bytes")
    if grant["phase"] != "reporting":
        accounting(body["access"])
        from raregate.benchmarks.partial_raw_reporting import validate_worker

        aggregate = p.read(directory / "aggregate.json")
        validate_worker(aggregate, int(grant["phase"][-1]))
        p.require(
            aggregate["accounting"] == body["access"]
            and aggregate["identity"] == grant["identity"]
            and aggregate["registered_model_threshold_hashes"]
            == body["model_parameter_threshold_hashes"]
            and body["Torch_cleanup"]["intra_restored"] is True
            and body["Torch_cleanup"]["deterministic_restored"] is True
            and body["HDF_same_handle_pre_post_checks"] == 2,
            "Independent aggregate/accounting agreement",
        )
    return dict(
        task="0045",
        status="parent_accepted_worker",
        normal_exit_reaped=True,
        terminal_resource_gap_seconds=max(
            0, dispatch["end_continuous"] - body["monitor_closed_continuous"]
        ),
    )


def accounting(a):
    from raregate.benchmarks import partial_raw_planning as plan

    expected = plan.counts()["per_worker"]
    p.require(
        a["task"] == "0045"
        and a["membership_loads"] == 1
        and a["membership_records_inspected"] == 6999
        and a["selected_IDs"] == 1024
        and a["membership_inflight"] is False
        and a["golden_loads"] == 1
        and a["golden_rows"] == 1024
        and a["golden_inflight"] is False
        and a["HDF_opens"] == 1
        and a["HDF_closed"] is True
        and a["model_loads"] == a["threshold_loads"] == a["model_instantiations"] == 2
        and a["model_inflight"] is None
        and a["inflight"] is None,
        "Complete Task0045 original input/model lifecycle",
    )
    p.require(
        a["raw_requests"]
        == a["raw_started_calls"]
        == a["raw_returned_requests"]
        == expected["raw_calls"]
        and a["raw_requested_rows"] == a["raw_returned_rows"] == expected["raw_rows"]
        and a["feature_requests"]
        == a["feature_started_calls"]
        == a["feature_completed_calls"]
        == expected["raw_calls"]
        and a["feature_requested_rows"]
        == a["feature_completed_rows"]
        == expected["raw_rows"]
        and a["adapter_requests"]
        == a["adapter_started_calls"]
        == a["adapter_completed_calls"]
        == a["decision_completed_calls"]
        == expected["service_calls"]
        and a["adapter_requested_rows"]
        == a["adapter_completed_rows"]
        == a["decision_completed_rows"]
        == expected["service_rows"]
        and a["decision_boolean_values"] == 4 * expected["service_rows"],
        "Nested actual-row/call conservation",
    )

    def entry(calls, rows, ref=False):
        return dict(
            raw_calls=0 if ref else calls,
            raw_rows=0 if ref else rows,
            feature_calls=0 if ref else calls,
            feature_rows=0 if ref else rows,
            adapter_calls=calls,
            adapter_rows=rows,
        )

    components = {
        phase: entry(
            plan.counts()[phase]["calls"] // 3, plan.counts()[phase]["rows"] // 3
        )
        for phase in ("timed", "warmup")
    }
    components["chain_gate"] = entry(
        plan.counts()["chain_gates"]["calls"] // 3,
        plan.counts()["chain_gates"]["rows"] // 3,
    )
    components["golden_reference"] = entry(
        plan.counts()["golden_references"]["calls"] // 3,
        plan.counts()["golden_references"]["rows"] // 3,
        True,
    )
    p.require(a["by_component"] == components, "Per-component paired conservation")
    for candidate in plan.CANDIDATES:
        p.require(
            a["by_candidate"][candidate]
            == dict(
                raw_calls=1050,
                raw_rows=42560,
                feature_calls=1050,
                feature_rows=42560,
                adapter_calls=1230,
                adapter_rows=49856,
            ),
            "Per-candidate paired accounting",
        )
    for side in plan.SIDES:
        n = sum(plan.mapping(b, m, side)[0] for b, m in plan.CASES)
        p.require(
            a["by_side"][side]
            == dict(
                raw_calls=1050, raw_rows=70 * n, adapter_calls=1230, adapter_rows=82 * n
            ),
            "Separate physical side work",
        )
    p.require(
        set(a["by_case"]) == {f"{b}/{m}" for b, m in plan.CASES}, "All15nominal cases"
    )
    for b, m in plan.CASES:
        p.require(
            a["by_case"][f"{b}/{m}"]
            == dict(
                raw_calls=140,
                raw_rows=70 * (b + m),
                adapter_calls=164,
                adapter_rows=82 * (b + m),
            ),
            "Per-case full/partial rows",
        )
