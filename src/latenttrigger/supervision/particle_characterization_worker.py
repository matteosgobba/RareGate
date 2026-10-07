"""Fresh Task0016 guarded workers; old v4/scientific code remains immutable."""

import argparse
import os
import signal
import time

from latenttrigger.supervision import particle_characterization as parent
from latenttrigger.supervision import particle_launcher as io
from latenttrigger.supervision.particle_bounded_worker import (
    additional_audit,
    readiness,
)


def verify_worker(kind, token):
    plan = parent.verify_plan()
    if kind in parent.READINESS:
        res = io.read(
            (io.ROOT / parent.READINESS[kind]).with_suffix(".reservation.json")
        )
        if res["mode"] != kind or res["status"] != "read_only_once_no_retry":
            raise ValueError("Foreign readiness provenance.")
    else:
        if kind not in parent.PHASES:
            raise ValueError(
                "Canonical/selection/calibration/test/custody-full forbidden."
            )
        directory = io.ROOT / parent.OUTPUT
        parent.prior.authorize(kind, io.read(directory / "workflow.json"))
        res = io.read(directory / f"{kind}-reservation.json")
        slot = io.read(io.ROOT / parent.SLOT)
        if (
            slot["task"] != "0016"
            or slot["status"] != "reserved_no_retry"
            or slot["maximum_additional_started_steps"] != 96
            or slot["maximum_cumulative_started_steps"] != 192
            or slot["plan_sha256"] != io.file_hash(io.ROOT / parent.PLAN)
            or res["phase"] != kind
            or res["status"] != "reserved_no_automatic_retry"
            or res["maximum_optimizer_steps"] != (96 if kind == "dev" else 0)
            or res["slot_sha256"] != io.file_hash(io.ROOT / parent.SLOT)
        ):
            raise ValueError("Foreign/consumed additional-budget reservation.")
    if (
        res["token"] != token
        or res["parent_pid"] != os.getppid()
        or res["plan_sha256"] != io.file_hash(io.ROOT / parent.PLAN)
    ):
        raise ValueError("Current worker parent/token/source/provenance mismatch.")
    return res, plan


def run_characterization(old, config, output, monitor, audit, plan, observer):
    try:
        gate = old.bg.run_dev(
            io.ROOT / "data/processed/lhco-rd-v1/schema-v1/dev",
            config,
            output,
            monitor,
            audit,
            optimizer_observer=observer,
        )
        throughput_error = None
    except old.ResourceLimitError as exc:
        if str(exc) != parent.THROUGHPUT_ERROR:
            raise
        monitor.check()  # A latched live failure cannot be reclassified as throughput-only.
        path = output / "dev-gate.json"
        if not path.exists():
            raise
        gate = io.read(path)
        if gate.get("feasibility_pass") is not False:
            raise
        throughput_error = str(exc)
    audit.save()
    parent.complete_gate(gate, io.read(audit.path))
    comparison = parent.numeric_comparison(gate, plan)
    if comparison["canonical_proposal_blocked"]:
        io.atomic(output / "numerical-comparison.json", comparison)
        raise ValueError(
            "Diagnostic numerical comparison unresolved; no rerun/canonical proposal."
        )
    return {
        "status": "passed"
        if throughput_error is None
        else "characterization_completed_original_throughput_failed",
        "original_throughput_error": throughput_error,
        "original_throughput_pass": gate["feasibility_pass"],
        "dev_gate": gate,
        "numeric_comparison": comparison,
        "canonical_authorized": False,
    }


def worker(kind, token):
    res, plan = verify_worker(kind, token)
    started = res["started_monotonic"]
    seconds = 30 if kind in parent.READINESS else parent.SECONDS[kind]

    def alarm(*_):
        raise TimeoutError("Import-inclusive characterization worker deadline.")

    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(
        signal.ITIMER_REAL, max(0.001, seconds - (time.monotonic() - started))
    )
    output = io.ROOT / (
        f"data/task0016-readiness-{kind}-evidence"
        if kind in parent.READINESS
        else f"{parent.OUTPUT}/{kind}"
    )
    output.mkdir(exist_ok=False)
    io.exclusive(
        output / "bootstrap-audit.json",
        {"phase": kind, "new_steps_started": 0, "no_data_yet": True},
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
        accepted = parent.current_acceptance()
        manifest = io.read(io.ROOT / parent.prior.MONITOR)
        validate_manifest(manifest, config, profile, accepted)
        old.bg.verify_acceptance(io.ROOT / parent.ACCEPTANCE, config)
        monitor = MonitorV4(config, profile, manifest, directory=output)
        monitor.started = started
        audit = additional_audit(old.StudyAudit, output / "access-audit.json")
        audit.save()
        if kind in (*parent.READINESS, "dev_readiness"):
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
        new_started = audit.steps_started if audit else 0
        new_completed = audit.steps_completed if audit else 0
        result.update(
            phase=kind,
            plan_sha256=io.file_hash(io.ROOT / parent.PLAN),
            current_acceptance_sha256=io.file_hash(io.ROOT / parent.ACCEPTANCE),
            authorization_sha256=plan["authorization_sha256"],
            observation_manifest_sha256=parent.prior.MONITOR_HASH,
            original_steps_started_completed=96,
            new_steps_started=new_started,
            new_steps_completed=new_completed,
            new_inflight_steps=new_started - new_completed,
            cumulative_started_steps=96 + new_started,
            resources=monitor.report() if monitor else None,
            elapsed_seconds_including_imports=time.monotonic() - started,
            audit_sha256=io.file_hash(audit.path) if audit else None,
            test_background_model_access=False,
            test_signal_model_access=False,
            canonical_authorized=False,
        )
        if kind in parent.READINESS:
            io.exclusive(io.ROOT / parent.READINESS[kind], result)
        else:
            io.atomic(output / "stage-result.json", result)
    return (
        0
        if result["status"]
        in ("passed", "characterization_completed_original_throughput_failed")
        else 1
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--readiness", choices=list(parent.READINESS))
    choice.add_argument("--phase", choices=parent.PHASES)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    raise SystemExit(worker(args.readiness or args.phase, args.token))


if __name__ == "__main__":
    main()
