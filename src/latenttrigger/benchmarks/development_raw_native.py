"""One metadata resolver reservation; real event timing has no CLI route."""

import argparse
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from latenttrigger.benchmarks import development_raw_protocol as p
from latenttrigger.benchmarks import development_raw_runtime as rt


def worker(directory, token):
    grant = p.read(directory / "grant.json")
    base = directory.parent
    clock = rt.ContinuousClock()
    p.require(
        grant["parent_pid"] == os.getppid()
        and grant["token"] == token
        and directory == directory.resolve()
        and directory.name == "resolver",
        "Owned resolver grant",
    )
    p.require(
        (
            grant["synthetic_only"]
            and base.is_relative_to(p.ROOT / "data/task0039-validation")
        )
        or (not grant["synthetic_only"] and base.parent == p.ROOT / p.OUTPUT),
        "Fixed invocation namespace",
    )
    p.require(
        p.file_hash(base / "plan.json") == grant["plan_sha256"], "Frozen plan identity"
    )
    plan = p.read(base / "plan.json")
    p.require(
        plan["prompt_sha256"] == p.file_hash(p.ROOT / p.PROMPT)
        and plan["source_map"] == p.source_map() == grant["source_map"]
        and p.dependencies() == grant["dependencies"],
        "Final source/dependency/prompt freeze",
    )
    if not grant["synthetic_only"]:
        anchor = p.read(p.ROOT / p.OUTPUT / "attempt.json")
        p.require(
            anchor["directory"] == str(base.relative_to(p.ROOT))
            and anchor["plan_sha256"] == grant["plan_sha256"],
            "Durable single metadata reservation",
        )
        p.require(
            p.native_build() == plan["native_validation_build"],
            "Native build before operational membership access",
        )
    guard = rt.ServiceGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    body = dict(
        status="failed",
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        grant_sha256=p.file_hash(directory / "grant.json"),
    )
    limiter = None
    accelerate = None
    try:
        guard.__enter__()
        spec = p.load()
        p.require(
            all(os.environ.get(k) == v for k, v in spec["thread_environment"].items())
            and all(k not in sys.modules for k in ("numpy", "h5py", "torch")),
            "Environment before numerical imports",
        )
        rt.boundary(directory, grant["synthetic_only"])
        import numpy as np
        from threadpoolctl import threadpool_info, threadpool_limits

        limiter = threadpool_limits(1)
        pools = threadpool_info()
        p.require(
            all(v["num_threads"] == 1 for v in pools), "Effective loaded threadpools"
        )
        if (
            np.show_config(mode="dicts")["Build Dependencies"]["blas"].get("name")
            == "accelerate"
        ):
            from latenttrigger.benchmarks.accelerate_threads import AccelerateThreads

            accelerate = AccelerateThreads()
        body["effective_numeric_threads"] = dict(
            threadpools=pools,
            accelerate=accelerate.report() if accelerate else None,
            Blosc_effective_threads="unknown",
        )
        if grant["synthetic_only"]:
            from latenttrigger.benchmarks.development_raw_synthetic import run

            names, audit = run(directory, guard)
            body["synthetic_access"] = audit
        else:
            p.custody()
            from latenttrigger.benchmarks import (
                development_raw_membership as membership,
            )
            from latenttrigger.benchmarks import (
                development_raw_metadata as md,
            )
            from latenttrigger.benchmarks import (
                development_raw_planning as planning,
            )

            audit = dict(
                membership_load_attempts=0,
                membership_loads=0,
                membership_records_inspected=0,
                selected_IDs=0,
                raw_hash_attempts=0,
                raw_hash_passes=0,
                raw_hash_bytes=0,
                raw_HDF_open_attempts=0,
                raw_HDF_metadata_opens=0,
                operational_raw_event_rows_requested=0,
                operational_raw_event_rows_returned=0,
                operational_golden_feature_loads=0,
            )
            body["access"] = audit

            def persist():
                p.durable_json(directory / "access.json", audit)

            persist()
            guard.boundary("raw_byte_custody")
            md.hash_raw(
                p.fixed(p.ROOT, p.RAW), spec["raw"], audit, persist, guard.check
            )
            guard.boundary("one_membership_load")
            original_load = np.load

            def only_membership(path, *args, **kwargs):
                p.require(
                    Path(path).absolute() == p.ROOT / p.MEMBERSHIP,
                    "No golden/other numeric arrays",
                )
                return original_load(path, *args, **kwargs)

            np.load = only_membership
            try:
                selected = membership.load_once(
                    p.fixed(p.ROOT, p.MEMBERSHIP), spec["membership"], audit, persist
                )
            finally:
                np.load = original_load
            np.save(directory / "selected-ids.npy", selected, allow_pickle=False)
            guard.boundary("one_metadata_HDF_open_no_values")
            metadata = md.inspect(
                p.ROOT / p.RAW, spec["raw"]["audit_schema"], audit, persist
            )
            p.durable_json(
                directory / "metadata.json",
                dict(
                    status="resolved_membership_metadata_only",
                    selected_IDs_payload_sha256=spec["membership"]["selected_sha256"],
                    source_metadata=metadata,
                    future_measurement_execution_authorized=False,
                ),
                exclusive=True,
            )
            p.durable_json(
                directory / "geometry.json", planning.geometry(selected), exclusive=True
            )
            names = ["metadata.json", "geometry.json", "selected-ids.npy"]
        if accelerate:
            accelerate.verify()
        guard.boundary("body_complete")
        body.update(
            status="body_complete_awaiting_exit",
            outputs={name: p.file_hash(directory / name) for name in names},
        )
    except BaseException as exc:
        body["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        cleanup = clock()
        try:
            if accelerate:
                accelerate.restore()
            if limiter:
                limiter.restore_original_limits()
        except BaseException as exc:
            body.update(status="failed", error=str(exc))
        guard.close()
        body.update(
            resources=guard.report(),
            monitor_closed_continuous=clock(),
            cleanup_seconds=clock() - cleanup,
            worker_seconds=clock() - grant["started_continuous"],
            ordinary_worker_seconds=time.monotonic() - grant["started_ordinary"],
        )
        p.durable_json(directory / "receipt.json", body, exclusive=True)
    return (
        0
        if body["status"] == "body_complete_awaiting_exit"
        and body["cleanup_seconds"] <= 2
        and clock() < grant["stage_deadline"]
        else 1
    )


def reserve(base, plan):
    p.durable_json(
        p.ROOT / p.OUTPUT / "attempt.json",
        dict(
            status="reserved_consumed_metadata_only",
            directory=str(base.relative_to(p.ROOT)),
            plan_sha256=p.file_hash(base / "plan.json"),
            prompt_sha256=plan["prompt_sha256"],
        ),
        exclusive=True,
    )


def run(acceptance=None, *, synthetic_directory=None):
    synthetic = synthetic_directory is not None
    clock = rt.ContinuousClock()
    started = clock()
    whole = started + 150
    base = (
        Path(synthetic_directory) if synthetic else p.ROOT / p.OUTPUT / uuid.uuid4().hex
    )
    base.mkdir(parents=True, exist_ok=False)
    workflow = dict(
        status="prerequisites",
        synthetic_only=synthetic,
        reserved=False,
        started=clock.snapshot(),
        source_map=p.source_map(),
        dependencies=p.dependencies(),
    )
    assertion = None
    try:
        with rt.alarm(clock, started + 30):
            spec = p.load()
            if not synthetic:
                p.require(
                    not (p.ROOT / p.OUTPUT / "attempt.json").exists(),
                    "Task0039 membership allowance consumed; no retry",
                )
                accepted = p.acceptance(Path(acceptance))
                workflow["custody"] = p.custody()
            rt.parent_check(clock=clock, deadline=whole)
            p.require(
                shutil.disk_usage(base).free >= 32 * 2**20,
                "Owned32MiB storage admission",
            )
            assertion = rt.IdleAssertion(clock)
            assertion.start(started + 30)
            plan = dict(
                task="0039",
                kind="synthetic_fixture"
                if synthetic
                else "one_membership_and_raw_metadata_resolution",
                source_map=workflow["source_map"],
                dependencies=workflow["dependencies"],
                config_sha256=p.file_hash(p.ROOT / p.CONFIG),
                prompt_sha256=p.file_hash(p.ROOT / p.PROMPT),
                byte_pins={} if synthetic else spec["byte_pins"],
                input_identities={}
                if synthetic
                else {k: spec[k] for k in ("membership", "raw", "golden")},
                acceptance_sha256=None if synthetic else p.file_hash(Path(acceptance)),
                native_validation_build=None if synthetic else accepted["native_build"],
                limits=p.RESOLVER_LIMITS,
                prospective_authorization="actual Task0039 prompt; one6999-ID load, byte custody and HDF metadata only; no event values/golden numeric/model/timing",
                future_measurement_execution_authorized=False,
            )
            p.durable_json(base / "plan.json", plan, exclusive=True)
            p.require(
                p.source_map() == plan["source_map"]
                and p.dependencies() == plan["dependencies"],
                "Freeze before reservation",
            )
            if not synthetic:
                reserve(base, plan)
                workflow["reserved"] = True
            workflow["prerequisite_seconds"] = clock() - started
        directory = base / "resolver"
        directory.mkdir()
        (directory / "tmp").mkdir()
        tick = clock()
        stage = min(whole, tick + 60)
        grant = dict(
            phase="resolver",
            parent_pid=os.getpid(),
            token=uuid.uuid4().hex,
            synthetic_only=synthetic,
            source_map=plan["source_map"],
            dependencies=plan["dependencies"],
            plan_sha256=p.file_hash(base / "plan.json"),
            started_continuous=tick,
            started_ordinary=time.monotonic(),
            operation_deadline=stage - 2,
            stage_deadline=stage,
            assertion_id=assertion.identity,
        )
        p.durable_json(directory / "grant.json", grant, exclusive=True)
        environment = dict(
            os.environ,
            **spec["thread_environment"],
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONPATH=str(p.ROOT / "src") + os.pathsep + str(p.ROOT),
            TMPDIR=str(directory / "tmp"),
        )
        observed = False

        def monitor():
            nonlocal observed
            assertion.check(stage - 2, force=not observed)
            observed = True
            rt.storage(base)

        dispatch = rt.supervise(
            [
                sys.executable,
                "-m",
                "latenttrigger.benchmarks.development_raw_native",
                "--worker",
                str(directory),
                "--token",
                grant["token"],
            ],
            directory / "worker.log",
            root=p.ROOT,
            environment=environment,
            clock=clock,
            operation_deadline=stage - 2,
            stage_deadline=stage,
            whole_deadline=whole,
            monitor=monitor,
        )
        workflow["dispatch"] = dispatch
        body = p.read(directory / "receipt.json")
        workflow["body_sha256"] = p.file_hash(directory / "receipt.json")
        workflow["worker_acceptance"] = rt.accept(
            body, dispatch, grant, directory, clock, stage
        )
        final = clock()
        deadline = min(whole, final + 30)
        with rt.alarm(clock, deadline):
            p.require(
                p.source_map() == plan["source_map"]
                and p.dependencies() == plan["dependencies"],
                "Final frozen identities",
            )
            if not synthetic:
                p.custody()
            workflow["resources"] = body["resources"]
            workflow["access"] = body.get("access", {})
            geometry = p.read(directory / "geometry.json")
            p.durable_json(
                base / "prospective-plan.json",
                dict(
                    future_measurement_execution_authorized=False,
                    scopes=spec["future"],
                    geometry=geometry,
                ),
                exclusive=True,
            )
            assertion.check(deadline, force=True)
            workflow["sleep_assertion"] = assertion.release(deadline)
            workflow.update(
                status="parent_accepted_synthetic_foundation"
                if synthetic
                else "parent_accepted_membership_metadata_resolution",
                controller_peak_RSS_bytes=rt.parent_check(
                    clock=clock, deadline=deadline
                ),
                storage_bytes=rt.storage(base),
                whole_seconds=clock() - started,
                finalization_seconds=clock() - final,
                overshoot_seconds=max(0, clock() - whole),
                finished=clock.snapshot(),
                plan_sha256=p.file_hash(base / "plan.json"),
            )
            p.durable_json(base / "workflow.json", workflow, exclusive=True)
            p.durable_json(
                base / "parent-acceptance.json",
                dict(
                    status=workflow["status"],
                    workflow_sha256=p.file_hash(base / "workflow.json"),
                    plan_sha256=workflow["plan_sha256"],
                    future_measurement_execution_authorized=False,
                ),
                exclusive=True,
            )
            rt.check_deadline(clock, deadline)
    except BaseException as exc:
        workflow.update(
            status="failed_consumed_metadata_no_retry"
            if workflow["reserved"]
            else "failed_before_operational_reservation",
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
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--token")
    parser.add_argument("--acceptance", type=Path)
    parser.add_argument("--synthetic-directory", type=Path)
    args = parser.parse_args()
    if args.worker:
        p.require(
            args.token and args.acceptance is None and args.synthetic_directory is None,
            "Parent grant only",
        )
        raise SystemExit(worker(args.worker, args.token))
    p.require(
        args.token is None
        and (args.acceptance is None) != (args.synthetic_directory is None),
        "Exactly metadata acceptance or owned synthetic mode; no payload timing flag",
    )
    if args.synthetic_directory:
        p.require(
            args.synthetic_directory.absolute().is_relative_to(
                p.ROOT / "data/task0039-validation"
            ),
            "Owned synthetic namespace",
        )
    _, result = run(args.acceptance, synthetic_directory=args.synthetic_directory)
    raise SystemExit(0 if result["status"].startswith("parent_accepted") else 1)


if __name__ == "__main__":
    main()
