"""One conditional Task0040 development payload session; separate synthetic fixtures."""

import argparse
import hashlib
import os
import shutil
import struct
import sys
import time
import uuid
from pathlib import Path

from latenttrigger.benchmarks import development_payload_protocol as p
from latenttrigger.benchmarks import development_payload_runtime as rt


def synthetic_prefix():
    return hashlib.sha256(
        b"".join(struct.pack("<q", 3 * i) for i in range(1024))
    ).hexdigest()


def worker(directory, token):
    clock = rt.ContinuousClock()
    grant, permit = p.validate_grant(directory, token, clock)
    guard = rt.ServiceGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    body = dict(
        status="failed",
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        grant_sha256=p.file_hash(directory / "grant.json"),
    )
    limiter = accelerate = handle = None
    ledger = None
    try:
        guard.__enter__()
        spec = p.load()
        p.require(
            all(os.environ.get(k) == v for k, v in spec["thread_environment"].items())
            and all(k not in sys.modules for k in ("numpy", "h5py", "torch")),
            "Environment before numerical imports",
        )
        rt.boundary(directory, grant)
        import numpy as np
        from threadpoolctl import threadpool_info, threadpool_limits

        limiter = threadpool_limits(1)
        if (
            np.show_config(mode="dicts")["Build Dependencies"]["blas"].get("name")
            == "accelerate"
        ):
            from latenttrigger.benchmarks.accelerate_threads import AccelerateThreads

            accelerate = AccelerateThreads()
        pools = threadpool_info()
        p.require(
            all(v["num_threads"] == 1 for v in pools), "Actual numeric threadpools"
        )
        body["effective_threads"] = dict(
            threadpools=pools,
            accelerate=accelerate.report() if accelerate else None,
            Blosc_effective_threads="unknown",
            BLOSC_NTHREADS_requested=os.environ.get("BLOSC_NTHREADS"),
        )
        if grant["phase"] == "reporting":
            from latenttrigger.benchmarks.development_payload_reporting import run

            names = run(directory, guard)
        else:
            import h5py

            from latenttrigger.benchmarks import development_payload_measure as measure
            from latenttrigger.benchmarks import (
                development_payload_provider as provider,
            )
            from latenttrigger.benchmarks import (
                development_raw_membership as membership,
            )
            from latenttrigger.benchmarks import development_raw_metadata as md
            from latenttrigger.benchmarks import development_raw_planning as planning
            from latenttrigger.data.features import Parameters

            ledger = provider.Ledger(directory)
            body["access"] = ledger.audit
            if grant["synthetic_only"]:
                from latenttrigger.benchmarks.development_raw_synthetic import (
                    fixture,
                    parameters,
                )

                path, prefix = fixture(directory)
                member_path = directory / "fixture-membership.npy"
                golden_path = directory / "fixture-golden.npy"
                # Fixture setup is separate synthetic-only work, never operational gates.
                selected = np.arange(1024, dtype="<i8") * 3
                gold = np.empty((1024, 8), dtype="<f4")
                parameters = parameters()
                with h5py.File(path, "r", **p.CACHE) as f:
                    for start in range(0, 1024, 128):
                        gold[start : start + 128] = provider.construct(
                            f.get("/df/block0_values")[
                                selected[start : start + 128].tolist(), :
                            ],
                            parameters,
                        )
                np.save(golden_path, gold, allow_pickle=False)
                member_spec = dict(
                    spec["membership"],
                    file_sha256=p.file_hash(member_path),
                    selected_sha256=prefix,
                )
                golden_spec = dict(
                    spec["golden"],
                    file_sha256=p.file_hash(golden_path),
                    payload_sha256=measure.block_hash(gold),
                )
                body["synthetic_setup"] = dict(
                    feature_calls=8,
                    feature_rows=1024,
                    HDF_fixture_setup_read_handles=1,
                    HDF_fixture_write_handles=1,
                    operational_rows=0,
                )
                del gold, selected
            else:
                p.custody()
                path = p.fixed(p.ROOT, p.RAW)
                member_path = p.fixed(p.ROOT, p.MEMBERSHIP)
                golden_path = p.fixed(p.ROOT, p.GOLDEN)
                member_spec, golden_spec = spec["membership"], spec["golden"]
                parameters = Parameters.from_config(
                    p.read(p.ROOT / spec["transform_config"])
                )
            # Two NPY inputs only, each once. No cached/derived prefix substitute.
            original_load = np.load
            remaining = {member_path: 1, golden_path: 1}

            def allowed_load(path, *args, **kwargs):
                target = Path(path).absolute()
                p.require(
                    target in remaining and remaining[target] == 1,
                    "No alternative/repeated array loads",
                )
                remaining[target] -= 1
                return original_load(path, *args, **kwargs)

            np.load = allowed_load
            try:
                selected = membership.load_once(
                    member_path, member_spec, ledger.audit, ledger.persist
                )
                golden = provider.golden_once(golden_path, golden_spec, ledger)
            finally:
                np.load = original_load
            approval = provider.Approval(selected, member_spec["selected_sha256"])
            guard.boundary("one_readonly_handle_before_pre_gate")
            ledger.audit["HDF_open_attempts"] = 1
            ledger.audit["HDF_inflight"] = True
            ledger.persist()
            handle = h5py.File(path, "r", **p.CACHE)
            ledger.audit["HDF_opens"] = 1
            ledger.persist()
            metadata = md.properties(handle, spec["raw"]["audit_schema"])
            body["HDF_runtime"] = dict(
                metadata=metadata,
                h5py=h5py.__version__,
                HDF5=h5py.version.hdf5_version,
                hdf5plugin=p.dependencies()["packages"]["hdf5plugin"],
                decoder_effective_threads="unknown",
            )
            payload = provider.Payload(
                handle.get("/df/block0_values"),
                approval,
                path,
                clock,
                grant["operation_deadline"],
                permit=permit,
            )
            names = measure.run(
                payload,
                golden,
                parameters,
                ledger,
                directory,
                int(grant["phase"][-1]),
                guard,
            )
            md.properties(handle, spec["raw"]["audit_schema"])
            handle.close()
            handle = None
            ledger.audit.update(HDF_closed=True, HDF_inflight=False)
            ledger.persist()
            for path, expected in (
                (member_path, member_spec["file_sha256"]),
                (golden_path, golden_spec["file_sha256"]),
            ):
                p.require(
                    p.file_hash(path) == expected,
                    "Post numerical input bytes immutable",
                )
            if not grant["synthetic_only"]:
                p.custody()
            agg = p.read(directory / "aggregate.json")
            geometry = planning.geometry(selected)
            for index, row in enumerate(geometry["windows"]):
                row.pop("source_chunks")
                row["window_index"] = index % 3
            geometry["unique_raw_rows"] = len(
                {
                    int(v)
                    for b in planning.BATCHES
                    for pos in planning.windows(b)
                    for v in selected[pos : pos + b]
                }
            )
            agg.update(geometry=geometry, accounting=ledger.audit)
            p.durable_json(directory / "aggregate.json", agg)
            rt.accounting(ledger.audit)
        if accelerate:
            accelerate.verify()
        guard.boundary("body_complete")
        body.update(
            status="body_complete_awaiting_exit",
            outputs={n: p.file_hash(directory / n) for n in names},
        )
    except BaseException as exc:
        body["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        cleanup = clock()
        try:
            if handle is not None:
                handle.close()
                if ledger is not None:
                    ledger.audit["HDF_closed"] = not handle.id.valid
                    ledger.persist()
            if accelerate:
                accelerate.restore()
            if limiter:
                limiter.restore_original_limits()
        except BaseException as exc:
            body.update(status="failed", cleanup_error=str(exc))
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
            status="reserved_consumed_one_development_measurement",
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
    whole = started + 780
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
        workers=[],
    )
    assertion = None
    parent_guard = None
    try:
        with rt.alarm(clock, started + 60):
            spec = p.load()
            build = p.native_build()
            if not synthetic:
                p.require(
                    not (p.ROOT / p.OUTPUT / "attempt.json").exists()
                    and not (p.ROOT / p.OUTPUT / "prerequisite-attempt.json").exists(),
                    "One invocation, failed prerequisites stop without repeating custody",
                )
                p.durable_json(
                    p.ROOT / p.OUTPUT / "prerequisite-attempt.json",
                    dict(
                        directory=str(base.relative_to(p.ROOT)),
                        status="prerequisites_consumed_no_retry",
                    ),
                    exclusive=True,
                )
                accepted = p.acceptance(acceptance)
                workflow["custody"] = p.custody()
                p.require(build == accepted["native_build"], "Accepted native build")
            parent_guard = rt.ServiceGuard(whole - 2, directory=base, clock=clock)
            parent_guard.__enter__()
            rt.parent_check(clock=clock, deadline=whole)
            p.require(
                shutil.disk_usage(base).free >= 128 * 2**20,
                "Owned128MiB storage admission",
            )
            assertion = rt.IdleAssertion(clock)
            assertion.start(started + 60)
            if not synthetic:
                workflow["raw_before"] = {}

                def poll_before():
                    parent_guard.check()
                    rt.check_deadline(clock, started + 60)
                    rt.parent_check(clock=clock, deadline=started + 60)
                    assertion.check(started + 60)

                p.hash_raw(
                    p.fixed(p.ROOT, p.RAW),
                    spec["raw"],
                    workflow["raw_before"],
                    lambda: p.durable_json(
                        base / "raw-before.json", workflow["raw_before"]
                    ),
                    poll_before,
                )
            plan = dict(
                task="0040",
                kind="synthetic_fixed_matrix"
                if synthetic
                else "one_development_raw_feature_measurement",
                source_map=workflow["source_map"],
                dependencies=workflow["dependencies"],
                native_build=build,
                config_sha256=p.file_hash(p.ROOT / p.CONFIG),
                prompt_sha256=p.file_hash(p.ROOT / p.PROMPT),
                acceptance_sha256=None if synthetic else p.file_hash(acceptance),
                inputs={k: spec[k] for k in ("membership", "raw", "golden")},
                design=spec["design"],
                limits=spec["limits"],
                post_custody_seconds=45,
                authorization="actual_Task0040_prompt_bound_to_this_final_plan; no_other_task_allowance",
                raw_before_identity={} if synthetic else workflow["raw_before"],
                preload_order="immediately_before_feature_scope_per_B; buffers_released_before_next_B",
            )
            p.durable_json(base / "plan.json", plan, exclusive=True)
            p.require(
                p.source_map() == plan["source_map"]
                and p.dependencies() == plan["dependencies"],
                "Final freeze before reservation",
            )
            if not synthetic:
                reserve(base, plan)
                workflow["reserved"] = True
            reserved_start = clock()
            reserved_deadline = min(whole, reserved_start + 720)
            workflow["prerequisite_seconds"] = clock() - started
        for phase in ("repetition1", "repetition2", "repetition3", "reporting"):
            directory = base / phase
            directory.mkdir()
            (directory / "tmp").mkdir()
            tick = clock()
            cap = 60 if phase == "reporting" else 180
            # Hold 45s post-custody and 15s parent finalization inside reserved limit.
            stage = min(reserved_deadline - 60, tick + cap)
            payload_path = directory / "fixture.h5" if synthetic else p.ROOT / p.RAW
            grant = dict(
                phase=phase,
                parent_pid=os.getpid(),
                token=uuid.uuid4().hex,
                synthetic_only=synthetic,
                source_map=plan["source_map"],
                dependencies=plan["dependencies"],
                plan_sha256=p.file_hash(base / "plan.json"),
                inputs=plan["inputs"],
                payload_path=str(payload_path),
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
                PYTHONPATH=str(p.ROOT / "src") + os.pathsep + str(p.ROOT),
                TMPDIR=str(directory / "tmp"),
                MPLCONFIGDIR=str(directory / "tmp"),
            )
            observed = False

            def monitor(stage=stage):
                parent_guard.check()
                nonlocal observed
                assertion.check(stage - 2, force=not observed)
                observed = True
                rt.storage(base)

            dispatch = rt.supervise(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.benchmarks.development_payload_native",
                    "--worker",
                    str(directory),
                    "--token",
                    grant["token"],
                ],
                directory / "worker.log",
                root=p.ROOT,
                environment=env,
                clock=clock,
                operation_deadline=stage - 2,
                stage_deadline=stage,
                whole_deadline=whole,
                monitor=monitor,
            )
            # Persist dispatch even if no body survived; body complete never implies accepted.
            item = dict(phase=phase, dispatch=dispatch)
            workflow["workers"].append(item)
            p.durable_json(base / "progress.json", workflow)
            body = p.read(directory / "receipt.json")
            item["body_sha256"] = p.file_hash(directory / "receipt.json")
            item["acceptance"] = rt.accept(
                body, dispatch, grant, directory, clock, stage
            )
        if not synthetic:
            custody_start = clock()
            custody_deadline = min(reserved_deadline - 15, custody_start + 45)
            workflow["raw_after"] = {}
            with rt.alarm(clock, custody_deadline):

                def poll_after():
                    parent_guard.check()
                    rt.check_deadline(clock, custody_deadline)
                    rt.parent_check(clock=clock, deadline=custody_deadline)
                    assertion.check(custody_deadline)

                p.hash_raw(
                    p.fixed(p.ROOT, p.RAW),
                    spec["raw"],
                    workflow["raw_after"],
                    lambda: p.durable_json(
                        base / "raw-after.json", workflow["raw_after"]
                    ),
                    poll_after,
                )
            workflow["post_custody_seconds"] = clock() - custody_start
        final = clock()
        deadline = min(reserved_deadline, whole, final + 15)
        with rt.alarm(clock, deadline):
            p.require(
                p.source_map() == plan["source_map"]
                and p.dependencies() == plan["dependencies"]
                and p.native_build() == build,
                "Final frozen identities",
            )
            if not synthetic:
                p.custody()
            parent_guard.check()
            parent_guard.close()
            workflow["parent_resources"] = parent_guard.report()
            assertion.check(deadline, force=True)
            workflow["sleep_assertion"] = assertion.release(deadline)
            workflow.update(
                status="parent_accepted_synthetic_payload"
                if synthetic
                else "parent_accepted_development_raw_feature_measurement",
                controller_peak_RSS_bytes=rt.parent_check(
                    clock=clock, deadline=deadline
                ),
                storage_bytes=rt.storage(base),
                whole_seconds=clock() - started,
                reserved_seconds=clock() - reserved_start,
                finalization_seconds=clock() - final,
                overshoot_seconds=max(0, clock() - whole, clock() - reserved_deadline),
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
                ),
                exclusive=True,
            )
            rt.check_deadline(clock, deadline)
    except BaseException as exc:
        if parent_guard is not None:
            parent_guard.close()
            workflow["parent_resources"] = parent_guard.report()
        workflow.update(
            status="failed_consumed_no_retry"
            if workflow["reserved"]
            else "failed_prerequisites_no_retry",
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
        "Exactly fresh acceptance or synthetic-only fixtures",
    )
    if args.synthetic_directory:
        p.require(
            args.synthetic_directory.absolute().is_relative_to(p.ROOT / p.VALIDATION),
            "Owned synthetic namespace",
        )
    _, result = run(args.acceptance, synthetic_directory=args.synthetic_directory)
    raise SystemExit(0 if result["status"].startswith("parent_accepted") else 1)


if __name__ == "__main__":
    main()
