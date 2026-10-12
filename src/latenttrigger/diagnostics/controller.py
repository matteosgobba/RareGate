"""Stdlib preparation/reservation/supervision; a consumed session cannot replay."""

import argparse
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from latenttrigger.diagnostics import protocol as p
from latenttrigger.diagnostics.runtime import (
    ContinuousClock,
    IdleAssertion,
    alarm,
    check_deadline,
    parent_check,
    storage_check,
    supervise,
)


def freeze(root=p.ROOT):
    clock = ContinuousClock()
    started, deadline = clock(), clock() + 60
    with alarm(clock, deadline):
        checks = p.read(root / "data/task0033-validation/acceptance-checks.json")
        current = p.source_map(root)
        p.require(
            checks["status"] == "passed"
            and checks["source_file_sha256"] == current
            and checks["dependencies"] == p.runtime_versions(),
            "Fresh current-source acceptance required",
        )
        p.require(
            set(checks["checks"])
            == {
                "focused",
                "full",
                "portable",
                "lint",
                "format",
                "dependencies",
                "native_synthetic",
            },
            "Complete validation evidence",
        )
        for check in checks["checks"].values():
            p.require(
                check["exit_code"] == 0
                and p.file_hash(root / check["log"]) == check["log_sha256"],
                "Validation failure/log mutation",
            )
        acceptance = dict(
            status="software_accepted",
            source_file_sha256=current,
            dependencies=p.runtime_versions(),
            checks=checks["checks"],
            validation_record_sha256=p.file_hash(
                root / "data/task0033-validation/acceptance-checks.json"
            ),
        )
        p.durable_json(root / p.ACCEPTANCE, acceptance, exclusive=True)
        plan = p.build_plan(root)
        p.verify_inputs(root, plan)
        protocol = p.read(root / p.CONFIG)
        p.require(
            protocol["quantile_probabilities"] == p.QUANTILES
            and protocol["minimum_tail_summary_count"] == 20,
            "Fixed descriptive convention",
        )
        plan["binding"] = dict(
            source_file_sha256=current,
            dependencies=p.runtime_versions(),
            software_acceptance_file_sha256=p.file_hash(root / p.ACCEPTANCE),
            protocol_file_sha256=p.file_hash(root / p.CONFIG),
            protocol_canonical_sha256=p.digest(protocol),
            prompt_file_sha256=p.file_hash(root / p.PROMPT),
            base_commit="a671b98",
            new_model_forward_calls=0,
        )
        p.durable_json(root / p.PLAN, plan, exclusive=True)
        authorization = dict(
            status="prospective_authorization",
            actual_prompt_path=p.PROMPT,
            actual_prompt_file_sha256=p.file_hash(root / p.PROMPT),
            actual_prompt=(root / p.PROMPT).read_text(),
            plan_canonical_sha256=p.digest(plan),
            plan_file_sha256=p.file_hash(root / p.PLAN),
            software_acceptance_file_sha256=p.file_hash(root / p.ACCEPTANCE),
            source_file_sha256=current,
            explicit_scope="one exploratory session after successful validation; no further general confirmation required",
            recorded=clock.snapshot(),
        )
        p.durable_json(root / p.AUTH, authorization, exclusive=True)
        parent_check(clock=clock, deadline=deadline)
    return dict(
        status="frozen_authorized",
        plan_canonical_sha256=p.digest(plan),
        metadata_files=len(plan["metadata"]),
        arrays=len(plan["arrays"]),
        byte_header_only=True,
        elapsed_continuous_seconds=clock() - started,
    )


def validate_body(result, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    resources = result.get("resources", {})
    valid = (
        result.get("status") == "body_complete_awaiting_exit"
        and result.get("phase") == grant["phase"]
        and result.get("source_file_sha256")
        == grant["source_file_sha256"]
        == p.source_map()
        and result.get("plan_file_byte_sha256") == grant["plan_file_byte_sha256"]
        and result.get("grant_file_byte_sha256")
        == p.file_hash(directory.parent / (grant["phase"] + "-grant.json"))
        and dispatch["parent_confirms_normal_exit"]
        and dispatch["child_reaped"]
        and dispatch["within_deadline"]
        and resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
        and 0 < resources.get("peak_rss_bytes", 0) <= 2**30
        and 0 < resources.get("native_heap_reserved_bytes", 0) <= 512 * 2**20
        and result.get("cleanup_continuous_seconds", 3) <= 2
    )
    from latenttrigger.diagnostics.reporting import FIGURES, TABLES

    expected = (
        {*TABLES, "analysis-summary.json", "access.json"}
        if grant["phase"] == "analysis"
        else {*FIGURES, "reporting-summary.json"}
    )
    valid = valid and set(result.get("output_file_byte_sha256", {})) == expected
    for name, sha in result.get("output_file_byte_sha256", {}).items():
        path = p.fixed(directory, name)
        p.require(p.file_hash(path) == sha, "Worker output identity")
        check_deadline(clock, deadline)
    p.require(valid, "Completed body rejected by parent lifecycle/source/resource gate")
    if grant["phase"] == "analysis":
        a = result["access"]
        n = sum(grant["counts"].values())
        p.require(
            a["potential_inflight"] is None
            and a["feature_population_requests"] == 3
            and a["feature_rows_read"] == n
            and a["stored_score_array_loads"] == 6
            and a["stored_score_values_read"] == 2 * n
            and a["membership_array_loads"] == 3
            and a["membership_records_read"] == 3 * grant["original_rows"],
            "Final access ledger agreement",
        )
    return dict(
        status="parent_accepted",
        phase=grant["phase"],
        dispatch=dispatch,
        receipt_file_byte_sha256=p.file_hash(directory / "receipt.json"),
        output_file_byte_sha256=result["output_file_byte_sha256"],
        terminal_unaccounted_continuous_seconds=max(
            0,
            dispatch["exit_observed_continuous"] - result["monitor_closed_continuous"],
        ),
    )


def run_session(plan, base, *, root=p.ROOT, input_root=None, synthetic=False):
    input_root = input_root or root
    clock, assertion = ContinuousClock(), None
    started, prereq_deadline = clock(), clock() + 60
    workflow = dict(
        status="prerequisites", synthetic=synthetic, stages={}, started=clock.snapshot()
    )
    reserved, session_started = False, None
    # Exclusive directory, including failures before reservation: no overwrite.
    base.mkdir(parents=True, exist_ok=False)
    try:
        with alarm(clock, prereq_deadline):
            parent_check(clock=clock, deadline=prereq_deadline)
            spec = p.read(root / p.CONFIG)
            p.require(shutil.disk_usage(base).free >= 256 * 2**20, "Storage admission")
            if not synthetic:
                binding = plan["binding"]
                p.require(
                    binding["source_file_sha256"] == p.source_map(root)
                    and binding["dependencies"] == p.runtime_versions()
                    and binding["protocol_file_sha256"] == p.file_hash(root / p.CONFIG)
                    and binding["prompt_file_sha256"] == p.file_hash(root / p.PROMPT)
                    and binding["software_acceptance_file_sha256"]
                    == p.file_hash(root / p.ACCEPTANCE),
                    "Frozen binding changed",
                )
                auth = p.read(root / p.AUTH)
                acceptance = p.read(root / p.ACCEPTANCE)
                p.require(
                    auth["plan_canonical_sha256"] == p.digest(plan)
                    and auth["source_file_sha256"] == binding["source_file_sha256"]
                    and auth["software_acceptance_file_sha256"]
                    == binding["software_acceptance_file_sha256"]
                    and auth["actual_prompt_file_sha256"]
                    == binding["prompt_file_sha256"]
                    and acceptance["status"] == "software_accepted"
                    and acceptance["source_file_sha256"] == p.source_map(root),
                    "Prospective authorization/acceptance",
                )
                p.require(
                    plan == p.build_plan(root), "Frozen input lineage changed"
                ) if "binding" not in plan else p.require(
                    {k: v for k, v in plan.items() if k != "binding"}
                    == p.build_plan(root),
                    "Frozen input lineage changed",
                )
            p.verify_inputs(input_root, plan)
            assertion = IdleAssertion(clock).start(prereq_deadline)
            workflow["prerequisite_continuous_seconds"] = clock() - started
            workflow["prerequisite_byte_hashes"] = len(plan["metadata"]) + len(
                plan["arrays"]
            )
            workflow["prerequisite_array_headers"] = len(plan["arrays"])
            p.durable_json(base / "plan.json", plan, exclusive=True)
            p.durable_json(base / "protocol.json", spec, exclusive=True)
            if not synthetic:
                shutil.copyfile(root / p.AUTH, base / "authorization.json")
                shutil.copyfile(root / p.ACCEPTANCE, base / "acceptance.json")
            check_deadline(clock, prereq_deadline)
        session_started, whole_deadline = clock(), clock() + 240
        reservation = dict(
            status="reserved_consumed_no_replay",
            parent_pid=os.getpid(),
            source_file_sha256=p.source_map(root),
            dependencies=p.runtime_versions(),
            plan_canonical_sha256=p.digest(plan),
            plan_file_byte_sha256=p.file_hash(base / "plan.json"),
            started=clock.snapshot(),
            continuous_deadline=whole_deadline,
            synthetic=synthetic,
        )
        p.durable_json(base / "reservation.json", reservation, exclusive=True)
        reserved = True
        workflow["status"] = "reserved_consumed"
        for phase, limit in [("analysis", 120), ("reporting", 60)]:
            tick = clock()
            stage_deadline = min(tick + limit, whole_deadline)
            operation_deadline = stage_deadline - 2
            assertion.check(operation_deadline, force=True)
            directory = base / phase
            directory.mkdir()
            grant = dict(
                phase=phase,
                token=uuid.uuid4().hex,
                parent_pid=os.getpid(),
                started_continuous=tick,
                started_ordinary=time.monotonic(),
                operation_deadline=operation_deadline,
                stage_deadline=stage_deadline,
                input_root=str(input_root),
                counts=plan["counts"],
                original_rows=plan["original_rows"],
                source_file_sha256=reservation["source_file_sha256"],
                dependencies=reservation["dependencies"],
                plan_canonical_sha256=p.digest(plan),
                plan_file_byte_sha256=reservation["plan_file_byte_sha256"],
                reservation_file_byte_sha256=p.file_hash(base / "reservation.json"),
                thread_environment=spec["thread_environment"],
            )
            if phase == "reporting":
                grant["predecessor_parent_sha256"] = p.file_hash(
                    base / "analysis/parent-acceptance.json"
                )
            p.durable_json(base / (phase + "-grant.json"), grant, exclusive=True)
            environment = dict(
                os.environ,
                **spec["thread_environment"],
                PYTHONDONTWRITEBYTECODE="1",
                MPLCONFIGDIR=str(directory / "mpl-cache"),
            )

            def monitor(deadline=operation_deadline):
                assertion.check(deadline)
                storage_check(base)

            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.diagnostics.worker",
                    "--base",
                    str(base),
                    "--phase",
                    phase,
                    "--token",
                    grant["token"],
                ],
                base / (phase + ".log"),
                root=root,
                environment=environment,
                clock=clock,
                operation_deadline=operation_deadline,
                stage_deadline=stage_deadline,
                whole_deadline=whole_deadline,
                monitor=monitor,
            )
            workflow["stages"][phase] = dict(dispatch=dispatch)
            p.durable_json(directory / "dispatch.json", dispatch, exclusive=True)
            with alarm(clock, stage_deadline):
                result = p.read(directory / "receipt.json")
                accepted = validate_body(
                    result, dispatch, grant, directory, clock, stage_deadline
                )
                assertion.check(stage_deadline, force=True)
                p.durable_json(
                    directory / "parent-acceptance.json", accepted, exclusive=True
                )
            workflow["stages"][phase].update(
                accepted=accepted,
                resources=result["resources"],
                access=result["access"],
            )
            p.durable_json(base / "workflow.json", workflow)
        final_started = clock()
        final_deadline = min(final_started + 15, whole_deadline)
        with alarm(clock, final_deadline):
            assertion.check(final_deadline, force=True)
            p.verify_inputs(
                input_root, plan
            )  # byte custody only; no numerical reopening
            p.require(
                reservation["source_file_sha256"] == p.source_map(root),
                "Final source identity",
            )
            workflow["sleep_assertion"] = assertion.release(final_deadline)
            workflow["storage_bytes"] = storage_check(base)
            workflow.update(
                status="parent_accepted",
                finished=clock.snapshot(),
                reserved_continuous_seconds=clock() - session_started,
                whole_continuous_seconds=clock() - started,
                session_overshoot_seconds=max(0, clock() - whole_deadline),
                controller_peak_rss_bytes=parent_check(
                    clock=clock, deadline=final_deadline
                ),
                finalization_continuous_seconds=clock() - final_started,
                finalization_deadline_continuous=final_deadline,
            )
            p.durable_json(base / "workflow.json", workflow)
            p.durable_json(
                base / "parent-acceptance.json",
                dict(
                    status="parent_accepted",
                    workflow_file_sha256=p.file_hash(base / "workflow.json"),
                    plan_canonical_sha256=p.digest(plan),
                    source_file_sha256=reservation["source_file_sha256"],
                    assertion_released=workflow["sleep_assertion"]["released"],
                ),
                exclusive=True,
            )
            check_deadline(clock, final_deadline)
        return workflow
    except BaseException as error:
        workflow.update(
            status="failed_consumed" if reserved else "failed_before_reservation",
            error=f"{type(error).__name__}: {error}",
            finished=clock.snapshot(),
        )
        if assertion is not None and not assertion.evidence["released"]:
            try:
                workflow["sleep_assertion"] = assertion.release(clock() + 2)
            except BaseException as release_error:
                workflow["sleep_assertion"] = dict(
                    assertion.evidence, release_error=str(release_error)
                )
        workflow["reserved_continuous_seconds"] = (
            clock() - session_started if session_started else 0
        )
        p.durable_json(base / "workflow.json", workflow)
        return workflow


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--synthetic-root", type=Path)
    args = parser.parse_args()
    if args.freeze:
        print(freeze())
        return
    if args.synthetic_root:
        root = args.synthetic_root.resolve()
        result = run_session(
            p.read(root / "fixture-plan.json"),
            root / "session",
            input_root=root,
            synthetic=True,
        )
    else:
        result = run_session(p.read(p.ROOT / p.PLAN), p.ROOT / p.OUTPUT)
    print(
        {
            k: result.get(k)
            for k in (
                "status",
                "error",
                "reserved_continuous_seconds",
                "whole_continuous_seconds",
            )
        }
    )
    raise SystemExit(0 if result["status"] == "parent_accepted" else 1)


if __name__ == "__main__":
    main()
