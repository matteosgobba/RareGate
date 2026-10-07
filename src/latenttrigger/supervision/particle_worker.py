"""Fresh Task0013 diagnostic/reader workers; no heavy imports before dispatch."""

import argparse
import os
import signal
import subprocess
import sys
import time

from latenttrigger.supervision import particle_host as host
from latenttrigger.supervision import particle_launcher as ctl


def alarm(*_):
    raise TimeoutError("Import-inclusive worker deadline exceeded.")


def runtime():
    """Exact Task0012 runtime stack and real-reader CPU preparation, no objects."""
    tick = time.monotonic()
    from latenttrigger.models import particle_memory_study as old

    old.torch.set_num_threads(1)
    old.torch.set_num_interop_threads(1)
    old.torch.use_deterministic_algorithms(True, warn_only=False)
    config, profile = ctl.read(ctl.ROOT / ctl.CONFIG), ctl.read(ctl.ROOT / ctl.PROFILE)
    old.validate_config(config)
    old.validate_policy(profile, config, ctl.PROFILE_HASH)
    return old, config, profile, time.monotonic() - tick


def diagnostic_child(name):
    tick = time.monotonic()
    directory = ctl.ROOT / ctl.EXPERIMENT / name
    reservation = ctl.read(directory / "reservation.json")
    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(
        signal.ITIMER_REAL,
        max(0.001, reservation["deadline_monotonic"] - time.monotonic()),
    )
    ctl.verify_plan()
    old, config, profile, imported = (None, None, None, 0)
    if name != "stdlib_baseline":
        old, config, profile, imported = runtime()
    flags = ctl.read(ctl.ROOT / ctl.EXPERIMENT / "experiment.json")["context"][
        "pressure"
    ].get("pressure_dispatch_flags")
    startup = time.monotonic() - tick
    rows = []
    try:
        for i in range(3):
            if i:
                time.sleep(
                    max(0, rows[-1]["sample_monotonic"] + 2.5 - time.monotonic())
                )
            row = {"sample_monotonic": time.monotonic(), "index": i}
            try:
                row["sample"] = host.snapshot()
                row["sample"]["pressure_dispatch_flags"] = flags
                row["pressure_source"] = (
                    "single_experiment_context_query; readiness rechecks independently"
                )
                if old:
                    old.validate_sample(row["sample"], config, profile, launch=True)
                    row["admission_pass"] = True
                else:
                    row["admission_pass"] = None
            except Exception as exc:
                row.update(admission_pass=False, error=str(exc))
            rows.append(row)
            ctl.exclusive(directory / f"child-{i}.json", row)
        ctl.exclusive(
            directory / "child-ready.json",
            {
                "pid": os.getpid(),
                "parent_pid": os.getppid(),
                "runtime_import_and_cpu_setup_seconds": imported,
                "python_entry_to_prepared_seconds": startup,
                "external_dispatch_to_prepared_seconds": tick
                + startup
                - reservation["started_monotonic"],
                "readings": rows,
                "heavy_modules": host.heavy_modules(),
                "cpu_setup": "1intra/1inter/deterministic" if old else "stdlib_only",
            },
        )
        # Stay alive while parent reports its own footprint, never instantiate data.
        while not (directory / "release-child.json").exists():
            time.sleep(0.01)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def diagnostic_parent(name):
    tick = time.monotonic()
    directory = ctl.ROOT / ctl.EXPERIMENT / name
    reservation = ctl.read(directory / "reservation.json")
    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(
        signal.ITIMER_REAL,
        max(0.001, reservation["deadline_monotonic"] - time.monotonic()),
    )
    ctl.verify_plan()
    imported = 0
    if name == "legacy_double_stack":
        imported = runtime()[3]
    else:
        ctl.assert_lightweight()
    startup = time.monotonic() - tick
    child = None
    result = {
        "configuration": name,
        "status": "failed",
        "parent_readings": [],
        "parent_import_and_cpu_setup_seconds": imported,
        "parent_python_entry_to_prepared_seconds": startup,
        "parent_external_dispatch_to_prepared_seconds": tick
        + startup
        - reservation["started_monotonic"],
        "parent_pid": os.getpid(),
        "parent_parent_pid": os.getppid(),
        "parent_heavy_modules": host.heavy_modules(),
    }
    try:
        with (directory / "child.log").open("x") as log:
            child = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.supervision.particle_worker",
                    "--diagnostic-child",
                    name,
                ],
                cwd=ctl.ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            for i in range(3):
                while not (directory / f"child-{i}.json").exists():
                    if child.poll() is not None:
                        raise RuntimeError(
                            "Diagnostic child exited before measurements."
                        )
                    if (directory / "child.log").stat().st_size > ctl.LOG_LIMIT:
                        raise RuntimeError("Diagnostic log ceiling.")
                    time.sleep(0.01)
                result["parent_readings"].append(
                    {"sample_monotonic": time.monotonic(), "sample": host.snapshot()}
                )
                ctl.atomic(directory / "result.json", result)
            while not (directory / "child-ready.json").exists():
                if child.poll() is not None:
                    raise RuntimeError("Diagnostic child exited before final receipt.")
                time.sleep(0.01)
            result["child"] = ctl.read(directory / "child-ready.json")
            rows = result["child"]["readings"]
            span = rows[-1]["sample_monotonic"] - rows[0]["sample_monotonic"]
            result.update(
                status="completed",
                child_sample_span_seconds=span,
                worker_observations_all_pass=len(rows) == 3
                and span >= 5
                and all(r.get("admission_pass") is True for r in rows),
            )
            ctl.exclusive(directory / "release-child.json", {"released": True})
            child.wait(timeout=2)
            if child.returncode != 0:
                raise RuntimeError("Diagnostic child cleanup failed.")
    except BaseException as exc:
        result.update(
            status="failed", error=str(exc), worker_observations_all_pass=False
        )
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=2)
        signal.setitimer(signal.ITIMER_REAL, 0)
        result["elapsed_seconds_including_imports"] = (
            time.monotonic() - reservation["started_monotonic"]
        )
        ctl.atomic(directory / "result.json", result)
    return 0 if result["status"] == "completed" else 1


def verify_worker(phase, token):
    if phase not in ctl.PHASES:
        raise ValueError("Only bounded successor phases authorized.")
    plan = ctl.verify_plan()
    output = ctl.ROOT / ctl.OUTPUT
    state = ctl.read(output / "workflow.json")
    slot = ctl.read(ctl.ROOT / ctl.SLOT)
    reservation = ctl.read(output / f"{phase}-reservation.json")
    ctl.authorize(phase, state)
    if (
        reservation.get("phase") != phase
        or reservation.get("token") != token
        or reservation.get("status") != "reserved_no_automatic_retry"
        or reservation.get("maximum_optimizer_steps") != (96 if phase == "dev" else 0)
        or reservation.get("plan_sha256") != ctl.file_hash(ctl.ROOT / ctl.PLAN)
        or reservation.get("slot_sha256") != ctl.file_hash(ctl.ROOT / ctl.SLOT)
        or slot.get("plan_sha256") != ctl.file_hash(ctl.ROOT / ctl.PLAN)
        or slot.get("task") != "0013"
        or slot.get("status") != "reserved_no_retry"
        or reservation.get("parent_pid") != os.getppid()
        or plan["canonical_selection_freeze_calibration_authorized"] is not False
    ):
        raise ValueError(
            "Successor worker reservation/parent/source/authorization mismatch."
        )
    return reservation


def real_worker(phase, token):
    # All checks before runtime/store; real validators repeat after CPU preparation.
    reservation = verify_worker(phase, token)
    started = reservation["started_monotonic"]
    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(
        signal.ITIMER_REAL,
        max(0.001, ctl.LIMITS_SECONDS[phase] - (time.monotonic() - started)),
    )
    directory = ctl.ROOT / ctl.OUTPUT / phase
    directory.mkdir(exist_ok=False)
    ctl.exclusive(
        directory / "bootstrap-audit.json",
        {
            "phase": phase,
            "status": "preparing_no_data",
            "population_requests": 0,
            "optimizer_steps": 0,
            "pid": os.getpid(),
            "parent_pid": os.getppid(),
        },
    )
    monitor = audit = None
    result = {"phase": phase, "status": "failed"}
    try:
        old, config, profile, imported = runtime()
        verify_worker(phase, token)
        old.bg.verify_acceptance(ctl.ROOT / ctl.ACCEPTANCE, config)
        audit = old.StudyAudit(directory / "access-audit.json")
        audit.save()
        monitor = old.PolicyMonitor(
            config, profile, journal=directory / "resource-samples.jsonl"
        )
        monitor.started = started
        result["runtime_import_and_cpu_setup_seconds"] = imported
        if phase.endswith("preflight"):
            # Alarm/parent cover import-inclusive30s. Preserve completed readings.
            def deadline(*_):
                raise old.PreflightDeadline(
                    "Import-inclusive readiness30-second deadline."
                )

            signal.signal(signal.SIGALRM, deadline)
            result.update(old.stable_preflight(config, profile))
        else:
            # Monitor.__enter__ rechecks launch before reader or dev access.
            with (
                monitor,
                monitor.deadline(
                    "whole_phase_including_startup",
                    ctl.LIMITS_SECONDS[phase] - (time.monotonic() - started),
                ),
            ):
                if phase == "dev":
                    monitor.phase = "original_dev_gate"
                    result.update(
                        old.bg.run_dev(
                            ctl.ROOT / "data/processed/lhco-rd-v1/schema-v1/dev",
                            config,
                            directory,
                            monitor,
                            audit,
                            optimizer_observer=audit.observe_optimizer,
                        )
                    )
                else:
                    result.update(old.reader_measurement(phase, config, monitor, audit))
            result["status"] = "passed"
    except BaseException as exc:
        result.update(status="failed", error=str(exc), downstream_authorized=False)
        if audit is not None:
            for request in audit.records:
                if request.get("status") == "requested":
                    request.update(status="failed_or_interrupted", error=str(exc))
            audit.save()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        result.update(
            phase=phase,
            execution_plan_sha256=ctl.file_hash(ctl.ROOT / ctl.PLAN),
            acceptance_sha256=ctl.file_hash(ctl.ROOT / ctl.ACCEPTANCE),
            engineering_policy_sha256=ctl.PROFILE_HASH,
            model_config_sha256=ctl.CONFIG_HASH,
            policy_v1_compliance=False,
            canonical_authorized=False,
            elapsed_seconds_including_imports=time.monotonic() - started,
            resources=monitor.report() if monitor else None,
            optimizer_steps_started=audit.steps_started if audit else 0,
            optimizer_steps_completed=audit.steps_completed if audit else 0,
            unique_dev_sample_events=int(audit.seen.sum()) if audit else 0,
            audit_file_sha256=ctl.file_hash(audit.path) if audit else None,
        )
        ctl.atomic(directory / "stage-result.json", result)
    return 0 if result["status"] == "passed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--worker", choices=ctl.PHASES)
    mode.add_argument("--diagnostic-parent", choices=ctl.CONFIGURATIONS)
    mode.add_argument("--diagnostic-child", choices=ctl.CONFIGURATIONS)
    parser.add_argument("--token")
    args = parser.parse_args()
    if args.diagnostic_parent:
        code = diagnostic_parent(args.diagnostic_parent)
    elif args.diagnostic_child:
        diagnostic_child(args.diagnostic_child)
        code = 0
    else:
        code = real_worker(args.worker, args.token)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
