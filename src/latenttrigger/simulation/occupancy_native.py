"""Bounded two-worker synthetic sweep; fresh acceptance required, no model path."""

import argparse
import csv
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from latenttrigger.simulation import occupancy_admission as admission
from latenttrigger.simulation import occupancy_protocol as p
from latenttrigger.simulation import occupancy_runtime as rt

NAMESPACE = p.ROOT / p.NAMESPACE


def worker(directory, token):
    directory = Path(directory).absolute()
    p.require(
        (
            directory.parent.parent.parent == p.ROOT / p.VALIDATION
            if p.read(directory.parent / "plan.json")["fixture_only"]
            else directory.parent.parent == NAMESPACE
        )
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
    plan = admission.verify(directory.parent)
    p.require(
        grant["plan_sha256"] == p.file_hash(directory.parent / "plan.json")
        and grant["identity"] == p.identity(),
        "Frozen Task0046 worker grant",
    )
    p.durable_json(
        directory / "worker-entry.json",
        dict(
            task="0046", token=token, grant_sha256=p.file_hash(directory / "grant.json")
        ),
        exclusive=True,
    )
    clock = rt.ContinuousClock()
    guard = rt.SimulationGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    result = dict(
        status="failed",
        phase=grant["phase"],
        identity=p.identity(),
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
        p.load_config()
        p.require(
            p.file_hash(p.ROOT / p.CONFIG) == grant["config_sha256"],
            "Fixed config identity",
        )
        source_root = Path(plan["source_root"])
        allowed = (
            {source_root / n for n in plan["source_manifest"]}
            if grant["phase"] == "simulation"
            else set()
        )
        rt.install_boundary(p.ROOT, directory, allowed)
        guard.context()
        if grant["phase"] == "simulation":
            from latenttrigger.simulation import occupancy_sweep as sweep
            from latenttrigger.simulation.occupancy_source import Bundle

            bundle = Bundle(
                source_root,
                plan["source_manifest"],
                audit_path=directory / "source-audit.json",
                purpose="simulation_worker",
            )
            profiles, provenance = bundle.load()

            def notify(counters):
                p.durable_json(directory / "counters.json", dict(counters))

            report = sweep.run(
                profiles, provenance, directory, poll=guard.check, notify=notify
            )
            result["counters"] = report["counters"]
            names = [
                "summary.json",
                "scenarios.csv",
                "contrasts.csv",
                "occupancies.csv",
                "anchor-audit.csv",
            ]
        else:
            # Parent copies only its accepted aggregate JSON; original traces/timing inaccessible.
            p.require(
                p.file_hash(directory / "summary.json") == grant["summary_sha256"],
                "Accepted predecessor aggregate identity",
            )
            p.require(
                p.file_hash(directory / "scenarios.csv") == grant["scenario_sha256"]
                and p.file_hash(directory / "contrasts.csv")
                == grant["contrast_sha256"],
                "Accepted aggregate CSV identities",
            )
            p.require(
                all(
                    p.file_hash(directory / name) == sha
                    for name, sha in grant["audit_sha256"].items()
                ),
                "Accepted occupancy/anchor CSV identities",
            )
            from latenttrigger.simulation.occupancy_reporting import render

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
    from latenttrigger.simulation.occupancy_sweep import (
        contrasts,
        decode_rows,
        validate_rows,
        verify_audits,
    )

    rows = validate_rows(decode_rows(directory / "scenarios.csv"), report)
    audit = verify_audits(directory, rows, report)
    expected = (
        {k: "" if value is None else str(value) for k, value in r.items()}
        for i in range(0, len(rows), 4)
        for r in contrasts(rows[i : i + 4])
    )
    count = 0
    with (directory / "contrasts.csv").open(newline="") as f:
        for actual, wanted in zip(csv.DictReader(f), expected, strict=True):
            p.require(actual == wanted, "Independently recomputed streamed contrast")
            count += 1
    p.require(count == 2268, "Complete contrast count")
    p.require(
        audit["dispatch_assignments"]
        == report["counters"]["dispatch_sample_assignments"],
        "Assignment audit coverage",
    )
    return audit


def run_native(acceptance=None, *, fixture_directory=None, bootstrap=False):
    clock = rt.ContinuousClock()
    started = clock()
    whole = started + 240
    fixture = fixture_directory is not None
    base = (
        Path(fixture_directory).absolute() if fixture else NAMESPACE / uuid.uuid4().hex
    )
    if not bootstrap:
        p.verify_acceptance(acceptance)
        if not fixture:
            p.verify_roundtrip(acceptance)
    p.require(
        fixture or not (NAMESPACE / "attempt.json").exists(),
        "Task0046 allowance already consumed",
    )
    base.mkdir(parents=True, exist_ok=False)
    assertion = parent_guard = None
    workflow = dict(
        status="prerequisites",
        task="0046",
        kind="deterministic_occupancy_service_replay",
        fixture_only=fixture,
        identity=p.identity(),
        started=clock.snapshot(),
        phases=[],
        operational_work=0,
        source_map=p.source_map(),
        dependencies=p.dependencies(),
    )
    try:
        with rt.alarm(clock, min(whole, started + 30)):
            p.load_config()
            if fixture:
                from latenttrigger.simulation.occupancy_fixture import create

                create(base / "sources")
            plan = admission.freeze(
                acceptance, base, fixture=fixture, bootstrap=bootstrap
            )
            parent_guard = rt.SimulationGuard(whole - 2, directory=base, clock=clock)
            parent_guard.__enter__()
            rt.parent_check(clock=clock, deadline=whole)
            p.require(
                shutil.disk_usage(base).free >= 128 * 2**20, "Owned storage admission"
            )
            assertion = rt.IdleAssertion(clock)
            assertion.start(min(whole, started + 30))
            from latenttrigger.simulation.occupancy_source import Bundle

            bundle = Bundle(
                Path(plan["source_root"]),
                plan["source_manifest"],
                audit_path=base / "prerequisite-source-audit.json",
                purpose="claimed_prerequisite",
            )
            vectors, audit = bundle.load()
            workflow["prerequisite_source_audit"] = audit
            del vectors, bundle
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
                identity=p.identity(),
                source_map=plan["source_map"],
                dependencies=plan["dependencies"],
                config_sha256=plan["identity"]["config_sha256"],
                started_continuous=tick,
                started_ordinary=time.monotonic(),
                operation_deadline=stage - 2,
                stage_deadline=stage,
                plan_sha256=p.file_hash(base / "plan.json"),
                assertion_id=assertion.identity,
            )
            if phase == "reporting":
                prior = base / "simulation/summary.json"
                grant["summary_sha256"] = p.file_hash(prior)
                shutil.copyfile(prior, directory / "summary.json")
                for name in (
                    "scenarios.csv",
                    "contrasts.csv",
                    "occupancies.csv",
                    "anchor-audit.csv",
                ):
                    shutil.copyfile(base / "simulation" / name, directory / name)
                grant["scenario_sha256"] = p.file_hash(directory / "scenarios.csv")
                grant["contrast_sha256"] = p.file_hash(directory / "contrasts.csv")
                grant["audit_sha256"] = {
                    name: p.file_hash(directory / name)
                    for name in ("occupancies.csv", "anchor-audit.csv")
                }
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
                parent_guard.check()
                assertion.check(stage_deadline - 2, force=not observed)
                observed = True
                rt.storage_check(base)

            dispatch = rt.supervise(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.simulation.occupancy_native",
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
                report = p.read(directory / "summary.json")
                workflow["independent_aggregate_audit"] = verify_csv(directory, report)
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
            admission.verify(base)
            from latenttrigger.simulation.occupancy_source import Bundle

            custody = Bundle(
                Path(plan["source_root"]),
                plan["source_manifest"],
                audit_path=base / "final-source-byte-audit.json",
                purpose="final_hash_only_custody",
            )
            workflow["final_source_byte_audit"] = custody.audit
            custody.data.clear()
            del custody
            parent_guard.check()
            parent_guard.close()
            workflow["parent_resources"] = parent_guard.report()
            p.require(
                workflow["parent_resources"]["latched_error"] is None,
                "Parent primary guard",
            )
            assertion.check(final_deadline, force=True)
            workflow["sleep_assertion"] = assertion.release(final_deadline)
            workflow.update(
                status=p.PARENT_STATUS,
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
                    task="0046",
                    identity=p.identity(),
                    claim_sha256=p.file_hash(base / "claim.json"),
                ),
                exclusive=True,
            )
            rt.check_deadline(clock, final_deadline)
    except BaseException as e:
        workflow.update(
            status="failed_synthetic_preserved", error=f"{type(e).__name__}: {e}"
        )
        if parent_guard is not None:
            parent_guard.close()
            workflow["parent_resources"] = parent_guard.report()
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
    p.durable_json(base / "workflow.json", workflow)
    return base, workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path)
    parser.add_argument("--fixture-directory", type=Path)
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--token")
    args = parser.parse_args()
    if args.worker:
        p.require(args.token and args.acceptance is None, "Parent grant only")
        raise SystemExit(worker(args.worker, args.token))
    p.require(
        (
            args.acceptance is not None
            or (args.bootstrap and args.fixture_directory is not None)
        )
        and args.token is None,
        "Fresh current-source acceptance required; fixed synthetic inputs",
    )
    base, result = run_native(
        args.acceptance,
        fixture_directory=args.fixture_directory,
        bootstrap=args.bootstrap,
    )
    print(
        dict(
            directory=str(base),
            status=result["status"],
            whole_seconds=result["whole_seconds"],
            error=result.get("error"),
        )
    )
    raise SystemExit(0 if result["status"] == p.PARENT_STATUS else 1)


if __name__ == "__main__":
    main()
