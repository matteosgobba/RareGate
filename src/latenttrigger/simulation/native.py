"""Bounded two-worker synthetic sweep; fresh acceptance required, no model path."""

import argparse
import csv
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from latenttrigger.simulation import protocol as p
from latenttrigger.simulation import runtime as rt

NAMESPACE = p.ROOT / "results/simulation/task0037-synthetic-trigger"


def worker(directory, token):
    directory = Path(directory).absolute()
    p.require(
        directory.parent.parent == NAMESPACE
        and len(directory.parent.name) == 32
        and all(c in "0123456789abcdef" for c in directory.parent.name)
        and directory.name in ("simulation", "reporting"),
        "Fixed owned invocation namespace",
    )
    grant = p.read(directory / "grant.json")
    p.require(
        grant["token"] == token
        and grant["parent_pid"] == os.getppid()
        and grant["phase"] == directory.name
        and grant["synthetic_only"] is True,
        "Parent-owned synthetic grant",
    )
    clock = rt.ContinuousClock()
    guard = rt.SimulationGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    result = dict(
        status="failed",
        phase=grant["phase"],
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        grant_sha256=p.file_hash(directory / "grant.json"),
    )
    try:
        guard.__enter__()
        p.require(
            p.source_map() == grant["source_map"]
            and p.dependencies() == grant["dependencies"],
            "Worker source/dependency freeze",
        )
        config = p.load_config()
        p.require(
            p.file_hash(p.ROOT / p.CONFIG) == grant["config_sha256"],
            "Fixed config identity",
        )
        rt.install_boundary(p.ROOT, directory, grant["phase"])
        guard.context()
        if grant["phase"] == "simulation":
            from latenttrigger.simulation import sweep, timing

            profiles, provenance = timing.load()

            def notify(counters):
                p.durable_json(directory / "counters.json", dict(counters))

            report = sweep.run(
                profiles, provenance, config, directory, poll=guard.check, notify=notify
            )
            result["counters"] = report["counters"]
            names = ["aggregates.json", "scenarios.csv"]
        else:
            # Parent copies only its accepted aggregate JSON; original traces/timing inaccessible.
            p.require(
                p.file_hash(directory / "aggregates.json") == grant["aggregate_sha256"],
                "Accepted predecessor aggregate identity",
            )
            from latenttrigger.simulation.reporting import render

            names = render(directory, poll=guard.check)
        guard.boundary("body_outputs_complete")
        result.update(
            status="body_complete_awaiting_exit",
            outputs={n: p.file_hash(directory / n) for n in names},
        )
    except BaseException as e:
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        cleanup = clock()
        guard.close()
        result.update(
            resources=guard.report(),
            monitor_closed_continuous=clock(),
            cleanup_seconds=clock() - cleanup,
            worker_seconds=clock() - grant["started_continuous"],
            worker_ordinary_seconds=time.monotonic() - grant["started_ordinary"],
        )
        p.durable_json(directory / "receipt.json", result, exclusive=True)
    return (
        0
        if result["status"] == "body_complete_awaiting_exit"
        and result["cleanup_seconds"] <= 2
        and clock() < grant["stage_deadline"]
        else 1
    )


def verify_csv(directory, report):
    with (directory / "scenarios.csv").open(newline="") as f:
        actual = list(csv.DictReader(f))
    expected = [
        {k: "" if v is None else str(v) for k, v in r.items()} for r in report["rows"]
    ]
    p.require(actual == expected, "Complete CSV agrees with accepted aggregate rows")


def run_native(acceptance):
    clock = rt.ContinuousClock()
    started = clock()
    whole = started + 240
    base = NAMESPACE / uuid.uuid4().hex
    base.mkdir(parents=True, exist_ok=False)
    assertion = None
    workflow = dict(
        status="prerequisites",
        kind="synthetic_trigger_only",
        started=clock.snapshot(),
        phases=[],
        operational_work=0,
        source_map=p.source_map(),
        dependencies=p.dependencies(),
    )
    try:
        with rt.alarm(clock, min(whole, started + 30)):
            accepted = p.verify_acceptance(acceptance)
            p.load_config()
            rt.parent_check(clock=clock, deadline=whole)
            for name, sha in p.PINS.items():
                p.require(
                    p.file_hash(p.nonsymlink(p.ROOT, name)) == sha,
                    "Pinned curated byte custody",
                )
            p.require(
                shutil.disk_usage(base).free >= 128 * 2**20,
                "128MiB owned storage admission",
            )
            plan = dict(
                kind="fixed_synthetic_plan",
                source_map=workflow["source_map"],
                dependencies=workflow["dependencies"],
                config_sha256=p.file_hash(p.ROOT / p.CONFIG),
                prompt_sha256=p.file_hash(p.ROOT / p.PROMPT),
                timing_inputs=p.PINS,
                software_acceptance_sha256=p.file_hash(acceptance),
                software_acceptance_status=accepted["status"],
                scientific_source_acceptance=False,
                operational_model_work=False,
            )
            p.durable_json(base / "plan.json", plan, exclusive=True)
            assertion = rt.IdleAssertion(clock)
            assertion.start(min(whole, started + 30))
            workflow["prerequisite_seconds"] = clock() - started
        for phase in ("simulation", "reporting"):
            directory = base / phase
            directory.mkdir()
            (directory / "tmp").mkdir()
            tick = clock()
            stage = min(whole, tick + p.LIMITS[phase + "_seconds"])
            grant = dict(
                phase=phase,
                synthetic_only=True,
                parent_pid=os.getpid(),
                token=uuid.uuid4().hex,
                source_map=plan["source_map"],
                dependencies=plan["dependencies"],
                config_sha256=plan["config_sha256"],
                started_continuous=tick,
                started_ordinary=time.monotonic(),
                operation_deadline=stage - 2,
                stage_deadline=stage,
                plan_sha256=p.file_hash(base / "plan.json"),
                assertion_id=assertion.identity,
            )
            if phase == "reporting":
                prior = base / "simulation/aggregates.json"
                grant["aggregate_sha256"] = p.file_hash(prior)
                shutil.copyfile(prior, directory / "aggregates.json")
            p.durable_json(directory / "grant.json", grant, exclusive=True)
            env = dict(
                os.environ,
                PYTHONDONTWRITEBYTECODE="1",
                OMP_NUM_THREADS="1",
                OPENBLAS_NUM_THREADS="1",
                MKL_NUM_THREADS="1",
                VECLIB_MAXIMUM_THREADS="1",
                MPLCONFIGDIR=str(directory / "mpl-cache"),
                XDG_CACHE_HOME=str(directory / "cache"),
                TMPDIR=str(directory / "tmp"),
                PYTHONPATH=str(p.ROOT / "src") + os.pathsep + str(p.ROOT),
            )
            observed = False

            def monitor(stage_deadline=stage):
                nonlocal observed
                assertion.check(stage_deadline - 2, force=not observed)
                observed = True
                rt.storage_check(base)

            dispatch = rt.supervise(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.simulation.native",
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
            # Record exit/reaping even when no receipt was produced.
            phase_record = dict(phase=phase, dispatch=dispatch)
            workflow["phases"].append(phase_record)
            body = p.read(directory / "receipt.json")
            phase_record.update(
                body_sha256=p.file_hash(directory / "receipt.json"),
                acceptance=rt.accept_body(
                    body, dispatch, grant, directory, clock, stage
                ),
                resources=body["resources"],
                worker_seconds=body["worker_seconds"],
                cleanup_seconds=body["cleanup_seconds"],
            )
            if phase == "simulation":
                report = p.read(directory / "aggregates.json")
                verify_csv(directory, report)
                workflow["counters"] = report["counters"]
            assertion.check(stage, force=True)
            p.durable_json(
                directory / "parent-acceptance.json", phase_record, exclusive=True
            )
        final_started = clock()
        final_deadline = min(whole, final_started + 15)
        with rt.alarm(clock, final_deadline):
            p.require(
                p.source_map() == plan["source_map"]
                and p.dependencies() == plan["dependencies"],
                "Final source/dependency identity",
            )
            for name, sha in p.PINS.items():
                p.require(
                    p.file_hash(p.nonsymlink(p.ROOT, name)) == sha,
                    "Final curated byte custody",
                )
            assertion.check(final_deadline, force=True)
            workflow["sleep_assertion"] = assertion.release(final_deadline)
            workflow.update(
                status="parent_accepted_synthetic_sweep",
                controller_peak_RSS_bytes=rt.parent_check(
                    clock=clock, deadline=final_deadline
                ),
                storage_bytes=rt.storage_check(base),
                whole_seconds=clock() - started,
                finalization_seconds=clock() - final_started,
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
                    assertion_released=True,
                    synthetic_only=True,
                ),
                exclusive=True,
            )
            rt.check_deadline(clock, final_deadline)
    except BaseException as e:
        workflow.update(
            status="failed_synthetic_preserved", error=f"{type(e).__name__}: {e}"
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
    return base, workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--token")
    args = parser.parse_args()
    if args.worker:
        p.require(args.token and args.acceptance is None, "Parent grant only")
        raise SystemExit(worker(args.worker, args.token))
    p.require(
        args.acceptance is not None and args.token is None,
        "Fresh current-source acceptance required; fixed synthetic inputs",
    )
    base, result = run_native(args.acceptance)
    print(
        dict(
            directory=str(base),
            status=result["status"],
            whole_seconds=result["whole_seconds"],
            error=result.get("error"),
        )
    )
    raise SystemExit(0 if result["status"] == "parent_accepted_synthetic_sweep" else 1)


if __name__ == "__main__":
    main()
