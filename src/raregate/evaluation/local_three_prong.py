"""One Task0031 scientific campaign; stdlib parent, continuous gates, no network."""

import argparse
import json
import os
import secrets
import sys
import time

from raregate.benchmarks import protocol as p
from raregate.data.three_prong_v3_runtime import (
    ContinuousClock,
    IdleAssertion,
    check_deadline,
    supervise,
)
from raregate.evaluation import local_three_prong_protocol as q
from raregate.evaluation.guard import parent_check
from raregate.evaluation.guarded_audit import durable
from raregate.evaluation.local_three_prong_audit import exposure


def required_outputs(phase):
    directory = q.OUTPUT + "/" + phase + "/"
    if phase == "prepare":
        return {
            q.PREPARED + "/" + f
            for f in ("event_features.npy", "fingerprints.npy", "manifest.json")
        } | {directory + f for f in ("validity.json", "overlap.json", "access.json")}
    if phase in ("PCA", "AE"):
        return {
            directory + f
            for f in (
                "evaluation.json",
                "background-summary.json",
                "three-prong-scores.npy",
                "curves.npz",
                "access.json",
            )
        }
    return {
        directory + f
        for f in (
            "comparison.json",
            "scientific-comparison.csv",
            "calibrated-operating-points.csv",
            "empirical-operating-points.csv",
            "two-vs-three-prong.csv",
            "roc-pr.png",
            "access.json",
        )
    }


def accepted_stage(root, phase, result, dispatch, reservation, clock, deadline):
    check_deadline(clock, deadline)
    resources = result.get("resources", {})
    access = result.get("exposure", {})
    valid = (
        result.get("status") == "body_complete_awaiting_exit"
        and result.get("phase") == phase
        and result.get("source_file_sha256")
        == reservation["source_file_sha256"]
        == q.source_map(root)
        and result.get("protocol_canonical_JSON_sha256") == q.HASH
        and result.get("grant_file_byte_sha256")
        == p.file_hash(root / q.OUTPUT / (phase + "-grant.json"))
        and result.get("optimizer_updates")
        == result.get("new_original_background_forward_calls")
        == result.get("download_requests")
        == 0
        and dispatch["parent_confirms_normal_exit"]
        and dispatch["child_reaped"]
        and dispatch["within_deadline"]
        and resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
        and 0 < resources.get("peak_rss_bytes", 0) <= 6 * 2**30
        and 0 < resources.get("native_heap_reserved_bytes", 0) <= 512 * 2**20
        and result.get("threads_before") == result.get("threads_after")
        and result.get("timings", {}).get("cleanup_continuous_seconds", 3) <= 2
        and set(result.get("output_file_byte_sha256", {})) == required_outputs(phase)
        and access.get("potential_inflight") is False
    )
    for path, sha in result.get("output_file_byte_sha256", {}).items():
        q.check_file(root, path, sha, clock=clock, deadline=deadline)
    if valid and phase == "prepare":
        spec = q.load(root)
        manifest = p.read(root / q.PREPARED / "manifest.json")
        q.compatibility(manifest, spec)
        valid &= (
            access["raw_custody_requests"] == access["fingerprint_numeric_loads"] == 1
            and access["prepared_rows"] == 100000
            and not access["new_signal_model_accessed"]
        )
        records = {r["kind"]: r for r in access["records"]}
        valid &= (
            records["raw_custody"]["confirmed_read"]
            == records["row_axis"]["confirmed_read"]
            == 100000
            and records["original_fingerprint_integrity"]["confirmed_read"] == 1100000
        )
        valid &= (
            records["column_items"]["confirmed_read"]
            == records["column_axis"]["confirmed_read"]
            == 2101
        )
    elif valid and phase in ("PCA", "AE"):
        records = {r["kind"]: r for r in access["records"]}
        valid &= (
            access["signal_model_requests"] == access["cached_numeric_loads"] == 1
            and access["signal_scored_presentations"] == 100000
            and access["signal_batches"] == 25
            and records["signal_model_evaluation"]["confirmed_read"] == 100000
            and records["signal_model_evaluation"]["batches"] == [4096] * 24 + [1696]
            and records["cached_background_numeric_reuse"]["confirmed_read"] == 150471
            and records["candidate_constructor_provenance"]["confirmed_read"] == 1
        )
        doc = p.read(root / q.OUTPUT / phase / "evaluation.json")
        valid &= (
            p.digest(doc["scientific"]) == doc["scientific_sha256"]
            and doc["scientific"]["parameters_before"]
            == doc["scientific"]["parameters_after"]
        )
        spec = q.load(root)
        valid &= [
            r["background"]["accepted"]
            for r in doc["scientific"]["metrics"]["calibrated_thresholds"]
        ] == spec["calibrated_background_counts"][phase]
    elif valid:
        records = {r["kind"]: r for r in access["records"]}
        valid &= (
            records["reporting_owned_curves"]["confirmed_read"]
            == records["reporting_owned_metrics"]["confirmed_read"]
            == records["historical_aggregate_tables"]["confirmed_read"]
            == 2
        )
        valid &= (
            not access["new_signal_model_accessed"]
            and access["cached_numeric_loads"] == 0
        )
    check_deadline(clock, deadline)
    return dict(
        status="parent_accepted" if valid else "parent_rejected",
        phase=phase,
        dispatch=dispatch,
        output_file_byte_sha256=result.get("output_file_byte_sha256", {}),
        receipt_file_byte_sha256=p.file_hash(root / q.OUTPUT / phase / "receipt.json")
        if (root / q.OUTPUT / phase / "receipt.json").exists()
        else None,
        terminal_unaccounted_continuous_seconds=max(
            0,
            dispatch["exit_observed_continuous"]
            - result["resource_monitor_closed_continuous"],
        )
        if result.get("resource_monitor_closed_continuous") is not None
        else None,
    )


def campaign_exposure(root):
    stages = {
        phase: exposure(root / q.OUTPUT / phase / "access.json") for phase in q.PHASES
    }
    return dict(
        stages=stages,
        original_test_background_model_accessed=True,
        original_test_signal_model_accessed=True,
        new_three_prong_model_accessed=any(
            e["new_signal_model_accessed"] for e in stages.values()
        ),
        signal_model_requests=sum(e["signal_model_requests"] for e in stages.values()),
        signal_scored_presentations=sum(
            e["signal_scored_presentations"] for e in stages.values()
        ),
        signal_batches=sum(e["signal_batches"] for e in stages.values()),
        cached_background_numeric_loads_requested=sum(
            e["cached_numeric_loads"] for e in stages.values()
        ),
        original_fingerprint_numeric_loads_requested=sum(
            e["fingerprint_numeric_loads"] for e in stages.values()
        ),
        numerical_preparation_rows=sum(e["prepared_rows"] for e in stages.values()),
        raw_numerical_custody_requests=sum(
            e["raw_custody_requests"] for e in stages.values()
        ),
        potential_inflight=any(e["potential_inflight"] for e in stages.values()),
        new_original_background_forward_calls=0,
        optimizer_updates=0,
        download_requests=0,
    )


def publish(root, outcome, clock, deadline):
    base = root / q.OUTPUT

    def write_parent():
        durable(base / "workflow.json", outcome)
        durable(
            base / "parent-acceptance.json",
            dict(
                status=outcome["status"],
                workflow_file_byte_sha256=p.file_hash(base / "workflow.json"),
                source_file_sha256=q.source_map(root),
                protocol_canonical_JSON_sha256=q.HASH,
                sleep_assertion_released=outcome["sleep_assertion"].get(
                    "released", False
                ),
                publication_observed_continuous=clock(),
                acceptance_deadline_continuous=deadline,
                exposure=outcome["exposure"],
            ),
        )

    write_parent()
    try:
        check_deadline(clock, deadline)
    except BaseException as error:
        outcome.update(
            status="failed_consumed_no_retry",
            publication_error=f"{type(error).__name__}: {error}",
            publication_overshoot_seconds=max(0, clock() - deadline),
        )
        write_parent()


def run(root=q.ROOT):
    clock = ContinuousClock()
    started = clock()
    ordinary = time.monotonic()
    preflight_deadline = started + 60
    assertion = IdleAssertion(clock)
    owned = False
    base = root / q.OUTPUT
    spec = None
    whole_deadline = None
    outcome = dict(
        task="0031",
        status="blocked_before_reservation",
        started=clock.snapshot(),
        stages=[],
        optimizer_updates=0,
        download_requests=0,
        new_original_background_forward_calls=0,
    )
    try:
        parent_check(clock=clock, deadline=preflight_deadline)
        current = q.authorization(root, clock=clock, deadline=preflight_deadline)
        spec = current["specification"]
        q.namespace(root)
        ready = q.metadata(
            root, spec, clock=clock, deadline=preflight_deadline, check_payload=True
        )
        space = q.disk_space(root, spec)
        assertion.start(preflight_deadline)
        assertion.check(preflight_deadline, force=True)
        outcome["preflight_continuous_seconds"] = clock() - started
        reserved = clock()
        whole_deadline = reserved + 600
        base.mkdir(parents=True, exist_ok=False)
        owned = True
        (root / "data/task0031-three-prong").mkdir(parents=True, exist_ok=False)
        reservation = dict(
            task="0031",
            parent_pid=os.getpid(),
            reserved=clock.snapshot(),
            reserved_continuous=reserved,
            whole_deadline_continuous=whole_deadline,
            protocol_canonical_JSON_sha256=q.HASH,
            source_file_sha256=q.source_map(root),
            acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
            authorization_file_byte_sha256=p.file_hash(root / q.CONSENT),
            plan_sha256=p.digest(current),
            readiness=ready,
            storage=space,
            sleep_helper_pid=assertion.child.pid,
            sleep_assertion_id=assertion.identity,
            code=p.code_context(root),
        )
        q.require(
            reservation["source_file_sha256"] == current["source_file_sha256"],
            "Source drift during reservation;consumed",
        )
        p.write(base / "reservation.json", reservation, exclusive=True)
        for source, target in (
            (q.CONFIG, "protocol.json"),
            (q.ACCEPTANCE, "acceptance.json"),
            (q.CONSENT, "authorization.json"),
        ):
            with (base / target).open("xb") as stream:
                stream.write((root / source).read_bytes())
        environment = dict(
            os.environ,
            **spec["runtime"]["thread_environment_before_imports"],
            PYTHONPATH=str(root / "src"),
            PYTHONUNBUFFERED="1",
        )
        previous = {}
        for phase in q.PHASES:
            assertion.check(whole_deadline)
            parent_check(clock=clock, deadline=whole_deadline)
            seconds = spec["limits"][phase + "_seconds"]
            q.require(
                clock() + seconds + 15 <= whole_deadline,
                "Complete phase/finalization slack required",
            )
            directory = base / phase
            directory.mkdir()
            (directory / "mpl-cache").mkdir()
            token = secrets.token_hex(24)
            tick = clock()
            stage_deadline = tick + seconds
            grant = dict(
                phase=phase,
                token=token,
                parent_pid=os.getpid(),
                started=clock.snapshot(),
                started_continuous=tick,
                operation_deadline_continuous=stage_deadline - 2,
                stage_deadline_continuous=stage_deadline,
                predecessors=previous.copy(),
                reservation_file_byte_sha256=p.file_hash(base / "reservation.json"),
                sleep_helper_pid=assertion.child.pid,
                sleep_assertion_id=assertion.identity,
            )
            p.write(base / (phase + "-grant.json"), grant, exclusive=True)
            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "raregate.evaluation.local_three_prong_worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                directory / "worker.log",
                root=root,
                environment=dict(
                    environment, MPLCONFIGDIR=str(directory / "mpl-cache")
                ),
                clock=clock,
                operation_deadline=stage_deadline - 2,
                stage_deadline=stage_deadline,
                whole_deadline=whole_deadline,
                monitor=lambda: assertion.check(whole_deadline),
            )
            durable(directory / "dispatch.json", dispatch)
            result = (
                p.read(directory / "receipt.json")
                if (directory / "receipt.json").exists()
                else dict(status="receipt_missing")
            )
            try:
                accepted = accepted_stage(
                    root, phase, result, dispatch, reservation, clock, stage_deadline
                )
            except BaseException as error:
                accepted = dict(
                    status="parent_rejected",
                    phase=phase,
                    dispatch=dispatch,
                    error=f"{type(error).__name__}: {error}",
                )
            durable(directory / "parent-acceptance.json", accepted)
            outcome["stages"].append(dict(phase=phase, worker=result, parent=accepted))
            print(
                f"Task0031 {phase}: {accepted['status']}; continuous={dispatch['elapsed_continuous_seconds']:.6f}s",
                flush=True,
            )
            q.require(
                accepted["status"] == "parent_accepted",
                "Failed stage stops campaign: " + phase,
            )
            previous[phase] = p.file_hash(directory / "parent-acceptance.json")
        outcome["status"] = "all_stages_parent_accepted"
    except BaseException as error:
        outcome.update(
            status="failed_consumed_no_retry"
            if owned
            else "blocked_before_reservation",
            error=f"{type(error).__name__}: {error}",
        )
    finally:
        tick = clock()
        final_deadline = min(tick + 15, whole_deadline) if whole_deadline else tick + 15
        try:
            outcome["sleep_assertion"] = assertion.release(final_deadline)
            if owned:
                outcome["exposure"] = campaign_exposure(root)
                if outcome["status"] == "all_stages_parent_accepted":
                    q.metadata(
                        root,
                        spec,
                        clock=clock,
                        deadline=final_deadline,
                        check_payload=True,
                    )
                    q.acceptance(root, clock=clock, deadline=final_deadline)
                    q.require(
                        outcome["sleep_assertion"]["released"]
                        and not outcome["exposure"]["potential_inflight"]
                        and outcome["exposure"]["signal_scored_presentations"] == 200000
                        and outcome["exposure"][
                            "cached_background_numeric_loads_requested"
                        ]
                        == 2,
                        "Complete access/release acceptance",
                    )
                    outcome["status"] = "parent_accepted"
            parent_check(clock=clock, deadline=final_deadline)
        except BaseException as error:
            outcome.update(
                status="failed_consumed_no_retry"
                if owned
                else "blocked_before_reservation",
                finalization_error=f"{type(error).__name__}: {error}",
                sleep_assertion=assertion.evidence,
                exposure=campaign_exposure(root),
            )
        outcome.update(
            finished=clock.snapshot(),
            finalization_continuous_seconds=clock() - tick,
            elapsed_continuous_seconds=clock() - started,
            elapsed_ordinary_monotonic_seconds=time.monotonic() - ordinary,
            reserved_consumed=owned,
            new_campaign_retry_allowed=False,
            reserved_continuous_seconds=clock() - reserved if owned else None,
            whole_overshoot_seconds=max(0, clock() - whole_deadline)
            if whole_deadline
            else 0,
            controller_peak_RSS_bytes=parent_check(clock=clock),
        )
        if owned:
            publish(root, outcome, clock, final_deadline)
        else:
            path = root / "data/task0031-validation/prerequisite-outcome.json"
            q.require(not path.exists(), "Existing prerequisite evidence preserved")
            durable(path, outcome)
    print(
        json.dumps(
            dict(
                status=outcome["status"],
                reserved_consumed=owned,
                elapsed_continuous_seconds=outcome["elapsed_continuous_seconds"],
            )
        ),
        flush=True,
    )
    return 0 if outcome["status"] == "parent_accepted" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-final", action="store_true", required=True)
    parser.parse_args()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
