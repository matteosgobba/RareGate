"""Fresh guarded Task0015 worker; no data allowed before provenance/live checks."""

import argparse
import os
import signal
import time

from latenttrigger.supervision import particle_bounded_study as parent
from latenttrigger.supervision import particle_launcher as io
from latenttrigger.supervision import particle_sampling_benchmark as bench


def additional_audit(audit_type, path):
    """Retain original hooks; persist cumulative lineage before/after mutation."""

    class AdditionalAudit(audit_type):
        def save(self):
            if not 0 <= self.steps_completed <= self.steps_started <= 96:
                raise ValueError("Additional/cumulative optimizer budget invalid.")
            super().save()
            record = io.read(self.path)
            record.update(
                historical_optimizer_steps_started_completed=96,
                additional_optimizer_steps_started=self.steps_started,
                additional_optimizer_steps_completed=self.steps_completed,
                additional_inflight_steps=self.steps_started - self.steps_completed,
                cumulative_optimizer_steps_started=96 + self.steps_started,
                cumulative_optimizer_steps_ceiling=192,
            )
            io.atomic(self.path, record)

    return AdditionalAudit(path)


def verify_worker(kind, token):
    parent.verify_plan()
    if kind in ("automatic", "manual"):
        target = io.ROOT / (
            parent.READINESS_AUTO if kind == "automatic" else parent.READINESS_MANUAL
        )
        path = target.with_suffix(".reservation.json")
        res = io.read(path)
        if res["mode"] != kind or res["status"] != "read_only_once_no_retry":
            raise ValueError("Wrong readiness provenance.")
    else:
        if kind not in parent.PHASES:
            raise ValueError("Only bounded dev roles allowed.")
        output = io.ROOT / parent.OUTPUT
        parent.authorize(kind, io.read(output / "workflow.json"))
        res = io.read(output / f"{kind}-reservation.json")
        slot = io.read(io.ROOT / parent.SLOT)
        if (
            res["phase"] != kind
            or res["status"] != "reserved_no_automatic_retry"
            or res["maximum_optimizer_steps"] != (96 if kind == "dev" else 0)
            or res["slot_sha256"] != io.file_hash(io.ROOT / parent.SLOT)
            or slot["plan_sha256"] != io.file_hash(io.ROOT / parent.PLAN)
            or slot["maximum_additional_started_steps"] != 96
            or slot["maximum_cumulative_started_steps"] != 192
        ):
            raise ValueError("Foreign/consumed additional-step reservation.")
    if (
        res["token"] != token
        or res["parent_pid"] != os.getppid()
        or res["plan_sha256"] != io.file_hash(io.ROOT / parent.PLAN)
    ):
        raise ValueError("Worker parent/token/manifest/source mismatch.")
    return res


def readiness(monitor):
    rows = []
    started = time.monotonic()
    try:
        with monitor:
            for index in range(3):
                if index:
                    time.sleep(
                        max(0, rows[-1]["sample_monotonic"] + 2.5 - time.monotonic())
                    )
                monitor.check(launch=True)
                rows.append(
                    {"sample_monotonic": time.monotonic(), "guard": monitor.last}
                )
        span = rows[-1]["sample_monotonic"] - rows[0]["sample_monotonic"]
        return {
            "status": "passed"
            if len(rows) == 3 and span >= 5 and time.monotonic() - started <= 30
            else "failed",
            "readings": rows,
            "sample_span_seconds": span,
            "population_requests": 0,
            "new_real_steps": 0,
        }
    except BaseException as exc:
        return {
            "status": "failed",
            "error": str(exc),
            "readings": rows,
            "partial_readings": True,
            "population_requests": 0,
            "new_real_steps": 0,
            "latched_monitor_failure": monitor.error,
        }


def worker(kind, token):
    res = verify_worker(kind, token)
    started = res["started_monotonic"]

    def timeout(*_):
        raise TimeoutError("Import-inclusive bounded worker deadline.")

    signal.signal(signal.SIGALRM, timeout)
    seconds = 30 if kind in ("automatic", "manual") else parent.SECONDS[kind]
    signal.setitimer(
        signal.ITIMER_REAL, max(0.001, seconds - (time.monotonic() - started))
    )
    if kind in ("automatic", "manual"):
        output = io.ROOT / (
            "data/task0015-readiness-auto-evidence"
            if kind == "automatic"
            else "data/task0015-readiness-manual-evidence"
        )
    else:
        output = io.ROOT / parent.OUTPUT / kind
    output.mkdir(exist_ok=False)
    io.exclusive(
        output / "bootstrap-audit.json",
        {"scope": kind, "preparing_no_data": True, "new_real_steps": 0},
    )
    result = {"status": "failed", "phase": kind}
    audit = monitor = None
    try:
        from latenttrigger.supervision.particle_worker import runtime
        from latenttrigger.training.particle_monitor_v4 import (
            MonitorV4,
            optimizer_observer,
            validate_manifest,
        )

        old, config, profile, imported = runtime()
        verify_worker(kind, token)
        acceptance = bench.acceptance()
        manifest = io.read(io.ROOT / parent.MONITOR)
        validate_manifest(manifest, config, profile, acceptance)
        old.bg.verify_acceptance(io.ROOT / bench.ACCEPTANCE, config)
        monitor = MonitorV4(config, profile, manifest, directory=output)
        monitor.started = started
        audit = additional_audit(old.StudyAudit, output / "access-audit.json")
        audit.save()
        if kind in ("automatic", "manual", "dev_readiness"):
            result.update(readiness(monitor))
        else:
            with (
                monitor,
                monitor.deadline(
                    "whole_phase_including_imports",
                    seconds - (time.monotonic() - started),
                ),
            ):
                if kind == "dev_reader":
                    result.update(old.reader_measurement(kind, config, monitor, audit))
                else:
                    monitor.phase = "original_dev_gate"
                    result.update(
                        old.bg.run_dev(
                            io.ROOT / "data/processed/lhco-rd-v1/schema-v1/dev",
                            config,
                            output,
                            monitor,
                            audit,
                            optimizer_observer=optimizer_observer(audit, monitor),
                        )
                    )
            result["status"] = "passed"
        result["runtime_import_setup_seconds"] = imported
    except BaseException as exc:
        result.update(status="failed", error=str(exc), downstream_authorized=False)
        if audit:
            for request in audit.records:
                if request["status"] == "requested":
                    request.update(status="failed_or_interrupted", error=str(exc))
            audit.save()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if monitor:
            try:
                if monitor._active:
                    monitor.close()
            except BaseException as exc:
                result.update(status="failed", cleanup_error=str(exc))
            resources = monitor.report()
        else:
            resources = None
        if audit:
            # Additional budget is separate; every step was durably reserved by original hooks.
            started_steps = audit.steps_started
            completed = audit.steps_completed
        else:
            started_steps = completed = 0
        result.update(
            phase=kind,
            plan_sha256=io.file_hash(io.ROOT / parent.PLAN),
            acceptance_sha256=io.file_hash(io.ROOT / bench.ACCEPTANCE),
            observation_manifest_sha256=io.digest(io.read(io.ROOT / parent.MONITOR)),
            original_steps_started=96,
            new_steps_started=started_steps,
            new_steps_completed=completed,
            new_inflight_steps=started_steps - completed,
            cumulative_steps_started=96 + started_steps,
            resources=resources,
            elapsed_seconds_including_imports=time.monotonic() - started,
            test_background_model_access=False,
            test_signal_model_access=False,
            canonical_authorized=False,
        )
        if kind in ("automatic", "manual"):
            path = io.ROOT / (
                parent.READINESS_AUTO
                if kind == "automatic"
                else parent.READINESS_MANUAL
            )
            io.exclusive(path, result)
        else:
            io.atomic(output / "stage-result.json", result)
    return 0 if result["status"] == "passed" else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--readiness", choices=["automatic", "manual"])
    g.add_argument("--phase", choices=parent.PHASES)
    p.add_argument("--token", required=True)
    a = p.parse_args()
    raise SystemExit(worker(a.readiness or a.phase, a.token))


if __name__ == "__main__":
    main()
