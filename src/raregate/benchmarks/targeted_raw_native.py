"""One checked Task0047 campaign entry; generated bootstrap is separately typed."""

import argparse
import os
import shutil
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from raregate.benchmarks import targeted_raw_admission as a
from raregate.benchmarks import targeted_raw_protocol as p
from raregate.benchmarks import targeted_raw_runtime as rt
from raregate.benchmarks.development_decision_native import synthetic_prefix

_BOOTSTRAP_SEAL = object()


@dataclass(frozen=True)
class Bootstrap:
    context: a.Context
    directory: Path
    seal: object


def bootstrap(directory, context=None):
    context = context or a.Context(p.ROOT)
    directory = Path(directory).absolute()
    a.safe(directory, context)
    return run(Bootstrap(context, directory, _BOOTSTRAP_SEAL))


def admitted(capability):
    if isinstance(capability, Bootstrap):
        p.require(capability.seal is _BOOTSTRAP_SEAL, "Private generated bootstrap")
        a.safe(capability.directory, capability.context)
        return capability.context, capability.directory, True, True
    current = a.verify_frozen(capability)
    p.require(
        p.read(p.fixed(current.directory, "launch-claim.json"))
        == a.claim_fields(current),
        "Independent checked coordinator claim",
    )
    synthetic = current.mode is a.Mode.SYNTHETIC
    base = (
        current.directory / "native"
        if synthetic
        else current.context.root / p.OUTPUT / uuid.uuid4().hex
    )
    return current.context, base, synthetic, False


def run(capability):
    # Invalid software/freeze/scope causes no controller/prerequisite side effects.
    context, base, synthetic, is_bootstrap = admitted(capability)
    root = context.root
    spec = p.load(root)
    clock = rt.ContinuousClock()
    started = clock()
    whole = started + 780
    base.mkdir(parents=True, exist_ok=False)
    workflow = dict(
        task="0047",
        identity=p.identity(root),
        status="prerequisites",
        synthetic_only=synthetic,
        validation_bootstrap=is_bootstrap,
        reserved=False,
        actual_controller_invocation=not synthetic,
        started=clock.snapshot(),
        source_map=p.source_map(root),
        dependencies=p.dependencies(),
        workers=[],
        raw_before={},
        raw_after={},
    )
    assertion = parent_guard = None
    reserved_start = reserved_deadline = None
    try:
        with rt.alarm(clock, started + 60):
            if not synthetic:
                marker = root / p.OUTPUT / "prerequisite-attempt.json"
                p.require(
                    not (root / p.OUTPUT / "attempt.json").exists(),
                    "One Task0047 allowance",
                )
                p.durable_json(
                    marker,
                    dict(
                        task="0047",
                        directory=str(base.relative_to(root)),
                        status="prerequisites_consumed_no_retry",
                        admission_freeze_sha256=capability.freeze_sha256,
                        prompt_sha256=spec["authorization_prompt_sha256"],
                    ),
                    exclusive=True,
                )
            build = p.native_build()
            workflow["native_build"] = build
            parent_guard = rt.ServiceGuard(whole - 2, directory=base, clock=clock)
            parent_guard.__enter__()
            rt.parent_check(clock=clock, deadline=whole)
            if not synthetic:
                a.verify_frozen(capability)
                workflow["custody"] = p.custody(root)
            from raregate.benchmarks.targeted_raw_selection import Bundle

            if synthetic:
                from raregate.benchmarks.targeted_raw_selection_fixture import (
                    write,
                )

                selection_root = base / "selection-source"
                selection_manifest = write(selection_root)
            else:
                selection_root = root
                selection_manifest = spec["selection_manifest"]
            selection, selection_audit = Bundle(
                selection_root,
                selection_manifest,
                audit_path=base / "selection-audit.json",
                purpose="generated_native_selection"
                if synthetic
                else "physical_prerequisite_selection",
            ).load()
            p.durable_json(base / "selection.json", selection, exclusive=True)
            workflow["selection_audit"] = selection_audit
            workflow["selection_sha256"] = p.file_hash(base / "selection.json")
            p.require(
                shutil.disk_usage(base).free >= spec["limits"]["owned_storage_bytes"],
                "Owned128MiB storage admission",
            )
            assertion = rt.IdleAssertion(clock)
            assertion.start(started + 60)
            if not synthetic:

                def poll_before():
                    parent_guard.check()
                    rt.check_deadline(clock, started + 60)
                    rt.parent_check(clock=clock, deadline=started + 60)
                    assertion.check(started + 60)

                p.hash_raw(
                    p.fixed(root, p.RAW),
                    spec["raw"],
                    workflow["raw_before"],
                    lambda: p.durable_json(
                        base / "raw-before.json", workflow["raw_before"]
                    ),
                    poll_before,
                )
            reservation_tick = clock()
            plan = dict(
                whole_deadline_continuous=whole,
                reserved_start_continuous=reservation_tick,
                reserved_deadline_continuous=min(whole, reservation_tick + 720),
                task="0047",
                identity=p.identity(root),
                kind="synthetic_fixed_matrix" if synthetic else spec["kind"],
                synthetic_only=synthetic,
                validation_bootstrap=is_bootstrap,
                admission_directory=None if is_bootstrap else str(capability.directory),
                admission_freeze_sha256=None
                if is_bootstrap
                else capability.freeze_sha256,
                record_sha256=None if is_bootstrap else capability.record_sha256,
                source_map=workflow["source_map"],
                dependencies=workflow["dependencies"],
                native_build=build,
                inputs={k: spec[k] for k in ("membership", "raw", "golden")},
                models=spec["models"],
                expected=spec["expected"],
                limits=spec["limits"],
                authorization_prompt_sha256=spec["authorization_prompt_sha256"],
                raw_before_identity=workflow["raw_before"],
                selection_sha256=workflow["selection_sha256"],
            )
            p.require(
                plan["source_map"] == p.source_map(root)
                and plan["dependencies"] == p.dependencies(),
                "Final execution freeze before reservation",
            )
            p.durable_json(base / "plan.json", plan, exclusive=True)
            p.consume(base, plan, root=root, synthetic=synthetic)
            workflow["reserved"] = not synthetic
            reserved_start = plan["reserved_start_continuous"]
            reserved_deadline = plan["reserved_deadline_continuous"]
            workflow["prerequisite_seconds"] = clock() - started
        for phase in ("repetition1", "repetition2", "repetition3", "reporting"):
            directory = base / phase
            directory.mkdir()
            (directory / "tmp").mkdir()
            tick = clock()
            stage = min(
                reserved_deadline - 60, tick + (60 if phase == "reporting" else 180)
            )
            grant = dict(
                task="0047",
                identity=plan["identity"],
                record_sha256=plan["record_sha256"],
                phase=phase,
                parent_pid=os.getpid(),
                token=uuid.uuid4().hex,
                synthetic_only=synthetic,
                source_map=plan["source_map"],
                dependencies=plan["dependencies"],
                native_build=build,
                plan_sha256=p.file_hash(base / "plan.json"),
                admission_freeze_sha256=plan["admission_freeze_sha256"],
                inputs=plan["inputs"],
                models=plan["models"],
                expected=plan["expected"],
                selection_sha256=plan["selection_sha256"],
                payload_path=str(
                    directory / "fixture.h5" if synthetic else root / p.RAW
                ),
                prefix_sha256=synthetic_prefix()
                if synthetic
                else spec["membership"]["selected_sha256"],
                started_continuous=tick,
                started_ordinary=time.monotonic(),
                operation_deadline=stage - 2,
                stage_deadline=stage,
                assertion_id=assertion.identity,
            )
            p.durable_json(directory / "grant.json", grant, exclusive=True)
            env = dict(
                os.environ,
                **spec["thread_environment"],
                PYTHONDONTWRITEBYTECODE="1",
                PYTHONPATH=str(root / "src") + os.pathsep + str(root),
                TMPDIR=str(directory / "tmp"),
                MPLCONFIGDIR=str(directory / "tmp"),
            )
            observed = False

            def monitor(stage=stage):
                nonlocal observed
                parent_guard.check()
                assertion.check(stage - 2, force=not observed)
                observed = True
                rt.storage(base)

            dispatch = rt.supervise(
                [
                    sys.executable,
                    "-m",
                    "raregate.benchmarks.targeted_raw_native",
                    "--worker",
                    str(directory),
                    "--token",
                    grant["token"],
                ],
                directory / "worker.log",
                root=root,
                environment=env,
                clock=clock,
                operation_deadline=stage - 2,
                stage_deadline=stage,
                whole_deadline=whole,
                monitor=monitor,
            )
            item = dict(phase=phase, dispatch=dispatch)
            workflow["workers"].append(item)
            p.durable_json(base / "progress.json", workflow)
            p.require(
                (directory / "receipt.json").is_file(),
                "Worker missing final receipt; dispatch=" + repr(dispatch),
            )
            body = p.read(directory / "receipt.json")
            item["body_sha256"] = p.file_hash(directory / "receipt.json")
            item["acceptance"] = rt.accept(
                body, dispatch, grant, directory, clock, stage, root=root
            )
            # Conservative parent + one serial worker native reservation convention.
            combined = (
                parent_guard.report()["native_heap_reserved_bytes"]
                + body["resources"]["native_heap_reserved_bytes"]
            )
            p.require(
                combined <= 512 * 2**20,
                "Parent-plus-serial-worker native512MiB reservation",
            )
            item["parent_plus_serial_worker_native_upper_bytes"] = combined
        if not synthetic:
            post_start = clock()
            post_deadline = min(reserved_deadline - 15, post_start + 45)
            with rt.alarm(clock, post_deadline):

                def poll_after():
                    parent_guard.check()
                    rt.check_deadline(clock, post_deadline)
                    rt.parent_check(clock=clock, deadline=post_deadline)
                    assertion.check(post_deadline)

                p.hash_raw(
                    p.fixed(root, p.RAW),
                    spec["raw"],
                    workflow["raw_after"],
                    lambda: p.durable_json(
                        base / "raw-after.json", workflow["raw_after"]
                    ),
                    poll_after,
                )
            workflow["post_custody_seconds"] = clock() - post_start
        final = clock()
        deadline = min(whole, reserved_deadline, final + 15)
        with rt.alarm(clock, deadline):
            p.require(
                p.source_map(root) == plan["source_map"]
                and p.dependencies() == plan["dependencies"]
                and p.native_build() == build,
                "Final immutable source/packages/build",
            )
            if not synthetic:
                p.custody(root)
                final_bundle = Bundle(
                    root,
                    spec["selection_manifest"],
                    audit_path=base / "selection-final-byte-audit.json",
                    purpose="final_selection_byte_custody",
                )
                workflow["selection_final_byte_audit"] = final_bundle.audit
                final_bundle.data.clear()
            if not is_bootstrap:
                a.verify_frozen(capability)
            parent_guard.check()
            parent_guard.close()
            workflow["parent_resources"] = parent_guard.report()
            assertion.check(deadline, force=True)
            workflow["sleep_assertion"] = assertion.release(deadline)
            workflow.update(
                status="parent_accepted_synthetic_targeted_partial_raw_decision"
                if synthetic
                else "parent_accepted_targeted_partial_raw_decision_measurement",
                whole_seconds=clock() - started,
                reserved_seconds=clock() - reserved_start,
                finalization_seconds=clock() - final,
                overshoot_seconds=max(0, clock() - whole, clock() - reserved_deadline),
                controller_peak_RSS_bytes=rt.parent_check(
                    clock=clock, deadline=deadline
                ),
                storage_bytes=rt.storage(base),
                finished=clock.snapshot(),
                plan_sha256=p.file_hash(base / "plan.json"),
            )
            evidence_names = (
                {
                    f"repetition{i}/{name}"
                    for i in (1, 2, 3)
                    for name in (
                        "receipt.json",
                        "grant.json",
                        "access.json",
                        "access-journal.jsonl",
                        "aggregate.json",
                        "timings.jsonl",
                        "timer.json",
                        "guards.jsonl",
                        "worker.log",
                    )
                }
                | {
                    "reporting/" + name
                    for name in (
                        "receipt.json",
                        "grant.json",
                        "guards.jsonl",
                        "worker.log",
                        "selection.csv",
                        "cells.csv",
                        "pairs.csv",
                        "summary.json",
                        "joint-cost.png",
                        "paired-cost.png",
                        "selection-coverage.png",
                    )
                }
                | {
                    "plan.json",
                    "guards.jsonl",
                    "selection.json",
                    "selection-audit.json",
                }
            )
            workflow["owned_evidence_sha256"] = {
                name: p.file_hash(base / name) for name in sorted(evidence_names)
            }
            p.durable_json(base / "workflow.json", workflow, exclusive=True)
            p.durable_json(
                base / "parent-acceptance.json",
                dict(
                    task="0047",
                    identity=plan["identity"],
                    status=workflow["status"],
                    workflow_sha256=p.file_hash(base / "workflow.json"),
                    plan_sha256=workflow["plan_sha256"],
                ),
                exclusive=True,
            )
            rt.check_deadline(clock, deadline)
    except BaseException as exc:
        if parent_guard is not None:
            parent_guard.close()
            workflow["parent_resources"] = parent_guard.report()
        workflow.update(
            status="failed_synthetic_validation"
            if synthetic
            else (
                "failed_consumed_no_retry"
                if workflow["reserved"]
                else "failed_prerequisites_no_retry"
            ),
            error=f"{type(exc).__name__}: {exc}",
        )
        if assertion is not None and not assertion.evidence["released"]:
            try:
                workflow["sleep_assertion"] = assertion.release(min(whole, clock() + 2))
            except BaseException as release:
                workflow["sleep_assertion"] = dict(
                    assertion.evidence, release_error=str(release)
                )
        workflow.update(
            whole_seconds=clock() - started,
            overshoot_seconds=max(0, clock() - whole),
            finished=clock.snapshot(),
        )
        if (base / "parent-acceptance.json").exists():
            (base / "parent-acceptance.json").rename(base / "rejected-publication.json")
        p.durable_json(base / "workflow.json", workflow)
    if parent_guard is not None:
        parent_guard.close()
    print(
        dict(
            directory=str(base),
            status=workflow["status"],
            whole_seconds=workflow["whole_seconds"],
        ),
        flush=True,
    )
    return base, workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--acceptance", type=Path)
    group.add_argument("--bootstrap-directory", type=Path)
    group.add_argument("--worker", type=Path)
    parser.add_argument("--token")
    args = parser.parse_args()
    if args.worker:
        p.require(args.token is not None, "Parent-issued worker token only")
        from raregate.benchmarks.targeted_raw_worker import worker

        raise SystemExit(worker(args.worker, args.token))
    p.require(args.token is None, "No foreign worker token")
    if args.bootstrap_directory:
        _, w = bootstrap(args.bootstrap_directory)
    else:
        _, w = a.launch(
            args.acceptance,
            args.acceptance.absolute().parent / "operational-freeze",
            a.Context(p.ROOT),
            a.Mode.OPERATIONAL,
        )
    raise SystemExit(0 if w["status"].startswith("parent_accepted") else 1)


if __name__ == "__main__":
    main()
