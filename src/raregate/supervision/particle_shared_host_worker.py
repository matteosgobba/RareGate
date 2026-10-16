"""Fresh shared-host development workers; scientific functions unchanged."""

import argparse
import os
import signal
import time

from raregate.supervision import particle_dev_policy as policy
from raregate.supervision import particle_launcher as io
from raregate.supervision import particle_shared_host as parent
from raregate.supervision.particle_bounded_worker import (
    additional_audit,
)
from raregate.supervision.particle_characterization_worker import (
    run_characterization,
)


def verify_check(uid, token):
    directory = parent.invocation_path(uid)
    res = io.read(directory / "reservation.json")
    if (
        res["invocation_id"] != uid
        or res["action"] not in ("check_readiness", "run_characterization")
        or res["parent_pid"] != os.getppid()
        or res["token"] != token
        or res["binding"] != parent.identity()
    ):
        raise ValueError("Readiness parent/token/current source identity mismatch.")
    return res


def verify_phase(kind, token):
    policy.scope(kind)
    plan = parent.verify_plan()
    if kind not in parent.PHASES:
        raise ValueError("Only existing bounded diagnostic phases authorized.")
    directory = io.ROOT / parent.OUTPUT
    parent.previous.prior.authorize(kind, io.read(directory / "workflow.json"))
    res = io.read(directory / f"{kind}-reservation.json")
    if (
        res["phase"] != kind
        or res["token"] != token
        or res["parent_pid"] != os.getppid()
        or res["plan_sha256"] != io.file_hash(io.ROOT / parent.PLAN)
        or res["slot_sha256"] != io.file_hash(io.ROOT / parent.SLOT)
        or res["maximum_optimizer_steps"] != (96 if kind == "dev" else 0)
    ):
        raise ValueError("Foreign worker phase/parent/token/plan/budget.")
    return res, plan


def timeout(*_):
    raise TimeoutError("Original import-inclusive worker/check deadline.")


def check_worker(uid, token):
    directory = parent.invocation_path(uid)
    raw = io.read(directory / "reservation.json")
    started = raw["started_monotonic"]
    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, 30 - (time.monotonic() - started)))
    res = verify_check(uid, token)
    io.exclusive(
        directory / "bootstrap-audit.json",
        {
            "invocation_id": uid,
            "started_utc": io.now(),
            "population_requests": 0,
            "events": 0,
            "optimizer_steps": 0,
            "real_slot_reserved": False,
        },
    )
    result = {
        "status": "error",
        "invocation_id": uid,
        "action": res["action"],
        "binding": res["binding"],
        "reservation_sha256": io.file_hash(directory / "reservation.json"),
        "started_utc": res["started_utc"],
        "check_only_zero_data_steps": True,
        "real_slot_reserved_by_check": False,
    }
    monitor = None
    try:
        from raregate.supervision.particle_worker import runtime
        from raregate.training.particle_process_budget import ProcessBudgetGuard

        old, config, _profile, imported = runtime()
        verify_check(uid, token)
        old.bg.verify_acceptance(io.ROOT / parent.ACCEPTANCE, config)
        monitor = ProcessBudgetGuard(
            config, io.read(io.ROOT / parent.MANIFEST), directory=directory
        )
        monitor.started = started
        with (
            monitor,
            monitor.deadline(
                "whole_preflight_including_imports", 30 - (time.monotonic() - started)
            ),
        ):
            monitor.check(launch=True)
            result["status"] = "ready"
        result["runtime_import_setup_seconds"] = imported
    except BaseException as exc:
        result.update(
            status=parent.classify_failure(str(exc)),
            error=str(exc),
            partial_evidence_retained=True,
        )
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if monitor and monitor._active:
            try:
                monitor.close()
            except BaseException as exc:
                result.update(status="error", cleanup_error=str(exc))
        result.update(
            finished_utc=io.now(),
            finished_monotonic=time.monotonic(),
            elapsed_seconds_including_imports_cleanup=time.monotonic() - started,
            resources=monitor.report() if monitor else None,
            execution_permission=parent.permission(),
            population_requests=0,
            events=0,
            new_steps_started=0,
            new_steps_completed=0,
            new_inflight_steps=0,
            cumulative_started_steps=96,
            canonical_authorized=False,
            test_background_model_access=False,
            test_signal_model_access=False,
        )
        if result["elapsed_seconds_including_imports_cleanup"] > 30:
            result.update(
                status="error",
                error="Readiness original30s ceiling exceeded; no admission",
            )
        io.exclusive(directory / "receipt.json", result)
    return (
        0
        if result["status"] == "ready"
        else 2
        if result["status"] == "not_ready"
        else 1
    )


def phase_worker(kind, token):
    res, plan = verify_phase(kind, token)
    started = res["started_monotonic"]
    seconds = parent.SECONDS[kind]
    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(
        signal.ITIMER_REAL, max(0.001, seconds - (time.monotonic() - started))
    )
    output = io.ROOT / parent.OUTPUT / kind
    output.mkdir(exist_ok=False)
    io.exclusive(
        output / "bootstrap-audit.json",
        {"phase": kind, "timestamp_utc": io.now(), "no_data_yet": True},
    )
    result = {"status": "failed", "phase": kind}
    audit = monitor = None
    try:
        from raregate.supervision.particle_worker import runtime
        from raregate.training.particle_monitor_v4 import optimizer_observer
        from raregate.training.particle_process_budget import ProcessBudgetGuard

        old, config, _profile, imported = runtime()
        verify_phase(kind, token)
        manifest = io.read(io.ROOT / parent.MANIFEST)
        parent.current_acceptance()
        old.bg.verify_acceptance(io.ROOT / parent.ACCEPTANCE, config)
        monitor = ProcessBudgetGuard(config, manifest, directory=output)
        monitor.started = started
        audit = additional_audit(old.StudyAudit, output / "access-audit.json")
        audit.save()
        with (
            monitor,
            monitor.deadline(
                "whole_phase_including_imports", seconds - (time.monotonic() - started)
            ),
        ):
            # Fresh worker startup + fresh process checks at the phase entry.
            policy.scope(kind)
            monitor.check(launch=True)
            if kind == "dev_readiness":
                result["status"] = "passed"
            elif kind == "dev_reader":
                result.update(old.reader_measurement(kind, config, monitor, audit))
                result["status"] = "passed"
            else:
                monitor.phase = "original_dev_gate"
                result.update(
                    run_characterization(
                        old,
                        config,
                        output,
                        monitor,
                        audit,
                        plan,
                        optimizer_observer(audit, monitor),
                    )
                )
        result["runtime_import_setup_seconds"] = imported
    except BaseException as exc:
        result.update(status="failed", error=str(exc))
        if audit:
            for r in audit.records:
                if r["status"] == "requested":
                    r.update(status="failed_or_interrupted", error=str(exc))
            audit.save()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if monitor and monitor._active:
            try:
                monitor.close()
            except BaseException as exc:
                result.update(status="failed", cleanup_error=str(exc))
        started_steps = audit.steps_started if audit else 0
        completed = audit.steps_completed if audit else 0
        result.update(
            phase=kind,
            plan_sha256=io.file_hash(io.ROOT / parent.PLAN),
            current_acceptance_sha256=plan["binding"]["current_acceptance_sha256"],
            readiness_id=plan["readiness_id"],
            finished_utc=io.now(),
            resources=monitor.report() if monitor else None,
            elapsed_seconds_including_imports=time.monotonic() - started,
            original_steps=96,
            new_steps_started=started_steps,
            new_steps_completed=completed,
            new_inflight_steps=started_steps - completed,
            cumulative_started_steps=96 + started_steps,
            canonical_authorized=False,
            test_background_model_access=False,
            test_signal_model_access=False,
        )
        if result["elapsed_seconds_including_imports"] > seconds:
            result.update(
                status="failed",
                error="Import/verification/cleanup-inclusive phase ceiling exceeded.",
            )
        io.atomic(output / "stage-result.json", result)
    return (
        0
        if result["status"]
        in ("passed", "characterization_completed_original_throughput_failed")
        else 1
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check")
    g.add_argument("--phase", choices=parent.PHASES)
    p.add_argument("--token", required=True)
    a = p.parse_args()
    raise SystemExit(
        check_worker(a.check, a.token) if a.check else phase_worker(a.phase, a.token)
    )


if __name__ == "__main__":
    main()
