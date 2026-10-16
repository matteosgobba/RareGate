"""Dedicated Task0038 one-winner operational anchor; separate synthetic path."""

import argparse
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from raregate.benchmarks import prepared_service_protocol as p
from raregate.benchmarks import prepared_service_runtime as rt


def reserve(base, plan):
    anchor = p.ROOT / p.OUTPUT / "attempt.json"
    p.durable_json(
        anchor,
        dict(
            status="reserved_consumed",
            directory=str(base.relative_to(p.ROOT)),
            plan_sha256=p.file_hash(base / "plan.json"),
            prompt_sha256=plan["prompt_sha256"],
        ),
        exclusive=True,
    )


def combine(aggregates, synthetic):
    value = {
        key: [r for a in aggregates for r in a[key]]
        for key in ("cells", "paired", "chronology", "gates")
    }
    value["synthetic_only"] = synthetic
    value["access"] = [a["access"] for a in aggregates]
    value["empty_timer_distributions"] = [
        a["empty_timer_distribution"] for a in aggregates
    ]
    from raregate.benchmarks.prepared_service_reporting import validate

    validate(value)
    if not synthetic:
        p.require(
            sum(a["prepared_array_loads"] for a in value["access"]) == 3
            and sum(a["prepared_rows_loaded"] for a in value["access"]) == 3072
            and sum(a["frozen_model_instantiations"] for a in value["access"]) == 6
            and sum(a["timed_completed"] for a in value["access"]) == 10200
            and sum(a["warmup_completed"] for a in value["access"]) == 2040,
            "Complete operational counters",
        )
    return value


def run(acceptance=None, *, synthetic_directory=None):
    synthetic = synthetic_directory is not None
    clock = rt.ContinuousClock()
    started = clock()
    whole = started + 540
    base = (
        Path(synthetic_directory) if synthetic else p.ROOT / p.OUTPUT / uuid.uuid4().hex
    )
    base.mkdir(parents=True, exist_ok=False)
    workflow = dict(
        status="prerequisites",
        synthetic_only=synthetic,
        started=clock.snapshot(),
        phases=[],
        source_map=p.source_map(),
        dependencies=p.dependencies(),
        reserved=False,
    )
    assertion = None
    reserved_deadline = whole

    def dispatch(phase, cap, *, rep=None, build=None, aggregate=None, plan_sha=None):
        directory = base / phase
        directory.mkdir()
        (directory / "tmp").mkdir()
        tick = clock()
        stage = min(whole, reserved_deadline, tick + cap)
        grant = dict(
            phase=phase,
            repetition=rep,
            synthetic_only=synthetic,
            parent_pid=os.getpid(),
            token=uuid.uuid4().hex,
            source_map=workflow["source_map"],
            dependencies=workflow["dependencies"],
            started_continuous=tick,
            started_ordinary=time.monotonic(),
            operation_deadline=stage - 2,
            stage_deadline=stage,
            build=build,
            plan_sha256=plan_sha,
            assertion_id=assertion.identity,
        )
        if aggregate is not None:
            p.durable_json(directory / "aggregate.json", aggregate, exclusive=True)
            grant["aggregate_sha256"] = p.file_hash(directory / "aggregate.json")
        p.durable_json(directory / "grant.json", grant, exclusive=True)
        env = dict(
            os.environ,
            **p.load()["runtime"]["thread_environment_before_imports"],
            PYTHONDONTWRITEBYTECODE="1",
            MPLCONFIGDIR=str(directory / "mpl-cache"),
            XDG_CACHE_HOME=str(directory / "cache"),
            TMPDIR=str(directory / "tmp"),
            PYTHONPATH=str(p.ROOT / "src") + os.pathsep + str(p.ROOT),
        )
        observed = False

        def monitor():
            nonlocal observed
            assertion.check(stage - 2, force=not observed)
            observed = True
            rt.storage(base)

        d = rt.supervise(
            [
                sys.executable,
                "-m",
                "raregate.benchmarks.prepared_service_native",
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
            whole_deadline=min(whole, reserved_deadline),
            monitor=monitor,
        )
        record = dict(phase=phase, dispatch=d)
        workflow["phases"].append(record)
        body = p.read(directory / "receipt.json")
        record.update(
            body_sha256=p.file_hash(directory / "receipt.json"),
            resources=body["resources"],
            worker_seconds=body["worker_seconds"],
            cleanup_seconds=body["cleanup_seconds"],
            acceptance=rt.accept(body, d, grant, directory, clock, stage),
        )
        assertion.check(stage, force=True)
        p.durable_json(directory / "parent-acceptance.json", record, exclusive=True)
        return directory, body

    try:
        with rt.alarm(clock, started + 60):
            spec = p.load()
            if not synthetic:
                p.require(
                    not (p.ROOT / p.OUTPUT / "attempt.json").exists(),
                    "Task0038 already consumed; no retry",
                )
                accepted = p.verify_acceptance(Path(acceptance))
                custody, _ = p.custody()
                workflow["custody_before"] = custody
            rt.parent_check(clock=clock, deadline=whole)
            p.require(
                shutil.disk_usage(base).free >= 128 * 2**20, "Owned storage admission"
            )
            assertion = rt.IdleAssertion(clock)
            assertion.start(started + 60)
            probe, _ = dispatch("probe", min(30, 60 - (clock() - started)))
            build = p.read(probe / "probe.json")
            if not synthetic:
                for k in ("torch_config_sha256", "torch_version", "numpy_version"):
                    p.require(
                        build[k] == accepted["native_build"][k],
                        "Current accepted native build",
                    )
            plan = dict(
                kind="synthetic_validation_plan"
                if synthetic
                else "one_prepared_development_engineering_measurement",
                source_map=workflow["source_map"],
                dependencies=workflow["dependencies"],
                config_sha256=p.file_hash(p.ROOT / p.CONFIG),
                prompt_sha256=p.file_hash(p.ROOT / p.PROMPT),
                byte_pins={} if synthetic else spec["byte_pins"],
                limits=p.LIMITS,
                expected=spec["expected"],
                build=build,
                acceptance_sha256=None if synthetic else p.file_hash(Path(acceptance)),
                prospective_authorization="actual Task0038 prompt bound after fresh final-source acceptance; one session only",
                scientific_source_accepted=False,
            )
            p.durable_json(base / "plan.json", plan, exclusive=True)
            p.require(
                p.source_map() == plan["source_map"]
                and p.dependencies() == plan["dependencies"],
                "Pre-reservation source freeze",
            )
            if not synthetic:
                p.custody()
                reserve(base, plan)
            workflow["reserved"] = not synthetic
            workflow["prerequisite_seconds"] = clock() - started
            reserved_start = clock()
            reserved_deadline = min(whole, reserved_start + 480)
        aggregates = []
        for rep in (1,) if synthetic else (1, 2, 3):
            directory, _ = dispatch(
                f"repetition{rep}",
                120,
                rep=rep,
                build=build,
                plan_sha=p.file_hash(base / "plan.json"),
            )
            aggregates.append(p.read(directory / "aggregate.json"))
        value = combine(aggregates, synthetic)
        p.durable_json(base / "aggregate.json", value, exclusive=True)
        reporting, _ = dispatch(
            "reporting", 60, aggregate=value, plan_sha=p.file_hash(base / "plan.json")
        )
        final = clock()
        deadline = min(whole, reserved_deadline, final + 15)
        with rt.alarm(clock, deadline):
            p.require(
                p.source_map() == plan["source_map"]
                and p.dependencies() == plan["dependencies"],
                "Final source/dependency identities",
            )
            if not synthetic:
                p.custody()
            assertion.check(deadline, force=True)
            workflow["sleep_assertion"] = assertion.release(deadline)
            workflow.update(
                status="parent_accepted_synthetic"
                if synthetic
                else "parent_accepted_prepared_development_measurement",
                controller_peak_RSS_bytes=rt.parent_check(
                    clock=clock, deadline=deadline
                ),
                owned_storage_bytes=rt.storage(base),
                whole_seconds=clock() - started,
                reserved_seconds=clock() - reserved_start,
                finalization_seconds=clock() - final,
                overshoot_seconds=max(0, clock() - whole, clock() - reserved_deadline),
                finished=clock.snapshot(),
                plan_sha256=p.file_hash(base / "plan.json"),
                aggregate_sha256=p.file_hash(base / "aggregate.json"),
                reporting=str(reporting.relative_to(p.ROOT)),
            )
            p.durable_json(base / "workflow.json", workflow, exclusive=True)
            p.durable_json(
                base / "parent-acceptance.json",
                dict(
                    status=workflow["status"],
                    workflow_sha256=p.file_hash(base / "workflow.json"),
                    plan_sha256=workflow["plan_sha256"],
                    assertion_released=True,
                ),
                exclusive=True,
            )
            rt.check_deadline(clock, deadline)
    except BaseException as exc:
        workflow.update(
            status="failed_consumed_no_retry"
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
            "Grant only",
        )
        from raregate.benchmarks.prepared_service_worker import worker

        raise SystemExit(worker(args.worker, args.token))
    p.require(
        args.token is None
        and (args.acceptance is None) != (args.synthetic_directory is None),
        "Exactly one explicit synthetic or accepted real mode",
    )
    if args.synthetic_directory:
        p.require(
            args.synthetic_directory.absolute().is_relative_to(
                p.ROOT / "data/task0038-validation"
            ),
            "Synthetic ignored namespace",
        )
    _, result = run(args.acceptance, synthetic_directory=args.synthetic_directory)
    raise SystemExit(0 if result["status"].startswith("parent_accepted") else 1)


if __name__ == "__main__":
    main()
