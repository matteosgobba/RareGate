"""Task0020 stdlib controller: one fixed, exclusive CPU inference campaign."""

import argparse
import json
import os
import secrets
import signal
import statistics
import subprocess
import sys
import time

from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.guard import parent_check


def prerequisites(root=p.ROOT):
    parent_check()
    if sys.platform != "darwin":
        raise ValueError("Real campaign needs supported Darwin native accounting.")
    specification = p.load(root)
    frozen = p.verify_frozen(root, specification)
    accepted = p.verify_acceptance(root, specification)
    parent_check()
    return specification, accepted, frozen


def reserve(root, specification, accepted, frozen, started, *, on_created=lambda: None):
    directory = root / p.OUTPUT
    if directory.resolve() != directory.absolute():
        raise ValueError("Symlink/foreign campaign path refused.")
    # Atomic mkdir consumes the one slot, including an interrupted partial create.
    directory.mkdir(exist_ok=False)
    on_created()
    reservation = {
        "schema_version": 1,
        "task": "0020",
        "status": "reserved_no_retry",
        "reserved_utc": p.now(),
        "started_monotonic": started,
        "parent_pid": os.getpid(),
        "protocol_canonical_sha256": p.PROTOCOL_HASH,
        "acceptance_file_sha256": p.file_hash(root / p.ACCEPTANCE),
        "source_sha256": accepted["source_sha256"],
        "frozen_metadata": frozen,
        "code": p.code_context(root),
        "optimizer_updates": 0,
    }
    p.write(directory / "reservation.json", reservation, exclusive=True)
    with (directory / "acceptance.json").open("xb") as file:
        file.write((root / p.ACCEPTANCE).read_bytes())
    p.write(directory / "protocol.json", specification, exclusive=True)
    return directory


def terminate(child, deadline):
    """Terminate group, then kill/reap within a two-second reserved grace."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        if child.poll() is not None:
            child.wait()
            return
        try:
            os.killpg(child.pid, sig)
        except ProcessLookupError:
            pass
        try:
            child.wait(timeout=max(0.001, min(1, deadline - time.monotonic())))
            return
        except subprocess.TimeoutExpired:
            pass
    if child.poll() is None:
        raise RuntimeError("Child not reaped inside bounded cleanup grace.")


def supervise(command, log, *, root, environment, started, campaign_deadline):
    phase_deadline = started + 60
    execution_deadline = min(phase_deadline, campaign_deadline) - 2
    if time.monotonic() >= execution_deadline:
        raise TimeoutError("Insufficient cleanup slack before dispatch.")
    child = None
    error = None
    try:
        with log.open("x") as output:
            child = subprocess.Popen(
                command,
                cwd=root,
                env=environment,
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            while child.poll() is None:
                parent_check(deadline=campaign_deadline)
                if time.monotonic() >= execution_deadline:
                    raise TimeoutError("Import/native/operation parent deadline.")
                if log.stat().st_size > 2**20:
                    raise ValueError("Bounded worker output exceeded.")
                try:
                    child.wait(timeout=0.05)
                except subprocess.TimeoutExpired:
                    pass
    except BaseException as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if child is not None:
            try:
                terminate(
                    child, min(time.monotonic() + 2, phase_deadline, campaign_deadline)
                )
            except BaseException as exc:
                error = error or str(exc)
    elapsed = time.monotonic() - started
    return {
        "returncode": child.returncode if child else None,
        "parent_error": error,
        "elapsed_seconds_including_imports_cleanup": elapsed,
        "child_reaped": child is not None and child.poll() is not None,
        "deadline_passed": elapsed <= 60 and time.monotonic() <= campaign_deadline,
    }


def hardware_context():
    result = {
        "platform": sys.platform,
        "shared_host": "normal_shared_Mac_use_apps_open;no_app_content_inspected",
        "load_average": list(os.getloadavg()),
        "power_thermal_status": "unknown_until_query",
    }
    for key in (
        "hw.model",
        "machdep.cpu.brand_string",
        "hw.memsize",
        "hw.physicalcpu",
        "hw.logicalcpu",
        "hw.perflevel0.physicalcpu",
        "hw.perflevel1.physicalcpu",
        "kern.osproductversion",
        "kern.osversion",
    ):
        try:
            value = subprocess.check_output(
                ["/usr/sbin/sysctl", "-n", key],
                text=True,
                stderr=subprocess.PIPE,
                timeout=1,
            ).strip()
            result[key] = int(value) if value.isdigit() else value
        except (OSError, subprocess.SubprocessError) as exc:
            result[key] = {"status": "unavailable", "error": str(exc)}
    import platform

    result.update(architecture=platform.machine(), os=platform.platform())
    for key, command in (
        ("power", ["/usr/bin/pmset", "-g", "batt"]),
        ("thermal", ["/usr/bin/pmset", "-g", "therm"]),
    ):
        try:
            result[key] = {
                "status": "available",
                "raw": subprocess.check_output(
                    command, text=True, stderr=subprocess.PIPE, timeout=1
                )[:4096],
            }
        except (OSError, subprocess.SubprocessError) as exc:
            result[key] = {"status": "unavailable", "error": str(exc)}
    return result


def validate_receipt(root, directory, phase, dispatch):
    result = p.read(directory / phase / "receipt.json")
    if (
        result.get("phase") != phase
        or result.get("binding", {}).get("protocol_canonical_sha256") != p.PROTOCOL_HASH
        or result.get("binding", {}).get("acceptance_file_sha256")
        != p.file_hash(directory / "acceptance.json")
        or result.get("binding", {}).get("grant_file_sha256")
        != p.file_hash(directory / f"{phase}-reservation.json")
        or result.get("optimizer_updates") != 0
        or result.get("test_background_model_access") is not False
        or result.get("test_signal_model_access") is not False
    ):
        raise ValueError("Foreign/malformed worker receipt.")
    resources = result.get("resources", {})
    valid = (
        dispatch["returncode"] == 0
        and dispatch["child_reaped"]
        and dispatch["deadline_passed"]
        and not dispatch["parent_error"]
        and result["status"] == "completed"
        and 0 <= result["elapsed_seconds_including_imports_cleanup"] <= 60
        and 0 < resources.get("peak_rss_bytes", 0) <= 1073741824
        and 0 < resources.get("native_heap_reserved_bytes", 0) <= 536870912
        and resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
    )
    if phase != "prepare" and result["status"] == "completed":
        valid &= (
            len(result["cells"]) == 15
            and all(
                c["status"] == "completed"
                and c["timed_completed"] == 200
                and c["warmups_completed"] == 20
                for c in result["cells"]
            )
            and all(
                result["numerical"][when]["status"] == "passed"
                for when in ("before", "after")
            )
            and result["hashes_before"] == result["hashes_after"]
        )
    result["parent_dispatch"] = dispatch
    return result, bool(valid)


def aggregate(stages):
    """Report every retained cell; no inference from missing/failed cells."""
    cells = [
        cell
        for stage in stages
        if stage["phase"] != "prepare"
        for cell in stage.get("cells", [])
    ]
    totals = {
        "measured_cells_completed": sum(c.get("status") == "completed" for c in cells),
        "timed_invocations_completed": sum(c.get("timed_completed", 0) for c in cells),
        "warmups_completed": sum(c.get("warmups_completed", 0) for c in cells),
        "timed_input_presentations": sum(
            c.get("timed_completed", 0) * c["batch"] for c in cells
        ),
        "warmup_input_presentations": sum(
            c.get("warmups_completed", 0) * c["batch"] for c in cells
        ),
        "empty_timer_pairs": sum(
            len(s.get("empty_timer_pair_nanoseconds", [])) for s in stages
        ),
        "numerical_forward_input_presentations": sum(
            s.get("in_memory_audit", {}).get("numerical_forward_input_presentations", 0)
            for s in stages
        ),
    }
    groups = {}
    for cell in cells:
        key = (cell.get("model"), cell.get("batch"), cell.get("scope"))
        if cell.get("status") == "completed":
            groups.setdefault(key, []).append(cell["latency_nanoseconds"]["p50"])
    medians = [
        {
            "model": key[0],
            "batch": key[1],
            "scope": key[2],
            "workers": len(values),
            "median_of_worker_medians_nanoseconds": statistics.median(values),
        }
        for key, values in groups.items()
    ]
    return {
        "counts": totals,
        "cells": cells,
        "median_of_worker_medians": medians,
        "missing_measured_cells": 90 - totals["measured_cells_completed"],
        "comparison_success": totals["measured_cells_completed"] == 90
        and totals["timed_invocations_completed"] == 18000
        and totals["warmups_completed"] == 1800,
    }


def recover_partial(directory, phase):
    """Flushed completed calls are a lower bound when a child dies without receipt."""
    result = {
        "phase": phase,
        "status": "missing_worker_receipt",
        "cells": [],
        "possible_inflight_invocation": True,
        "counts_are_flushed_lower_bounds": True,
        "optimizer_updates": 0,
        "test_background_model_access": False,
        "test_signal_model_access": False,
    }
    audit_path = directory / "access-audit.json"
    if audit_path.exists():
        result["access_audit"] = p.read(audit_path)
    raw_path = directory / "timings.jsonl"
    cells = {}
    if raw_path.exists():
        if raw_path.stat().st_size > 4 * 2**20:
            raise ValueError("Unbounded partial timing journal.")
        with raw_path.open() as file:
            for line in file:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    break  # Preserve torn final record as interrupted, not completed.
                key = (row["batch"], row["scope"])
                cell = cells.setdefault(
                    key,
                    {
                        "model": "pca-v1"
                        if phase.startswith("PCA")
                        else "compact-autoencoder-v2",
                        "worker": phase,
                        "batch": key[0],
                        "scope": key[1],
                        "status": "partial",
                        "timed_completed": 0,
                        "warmups_completed": 0,
                    },
                )
                counter = (
                    "timed_completed"
                    if row["phase"] == "measurement"
                    else "warmups_completed"
                )
                cell[counter] += 1
    result["cells"] = list(cells.values())
    return result


def run_campaign(root=p.ROOT):
    started = time.monotonic()
    deadline = started + 600
    directory = root / p.OUTPUT
    outcome = {
        "schema_version": 1,
        "task": "0020",
        "status": "blocked_before_reservation",
        "started_utc": p.now(),
        "stages": [],
        "optimizer_updates": 0,
        "test_background_model_access": False,
        "test_signal_model_access": False,
    }
    reserved = False
    try:
        if directory.exists() or directory.is_symlink():
            raise ValueError(
                "Fixed campaign output already exists; slot consumed/partial/foreign, no retry."
            )
        specification, accepted, frozen = prerequisites(root)

        def own_slot():
            nonlocal reserved
            reserved = True

        directory = reserve(
            root, specification, accepted, frozen, started, on_created=own_slot
        )
        outcome["status"] = "running_reserved_no_retry"
        outcome.update(
            protocol_canonical_sha256=p.PROTOCOL_HASH,
            acceptance_file_sha256=p.file_hash(directory / "acceptance.json"),
            hardware=hardware_context(),
        )
        parent_check(deadline=deadline)
        env = dict(
            os.environ, **specification["runtime"]["thread_environment_before_imports"]
        )
        previous = {}
        for phase in p.PHASES:
            parent_check(deadline=deadline)
            if time.monotonic() + 62 > deadline:
                raise TimeoutError(
                    "Insufficient campaign/cleanup slack before next phase."
                )
            phase_directory = directory / phase
            phase_directory.mkdir()
            phase_started = time.monotonic()
            token = secrets.token_hex(24)
            grant = {
                "phase": phase,
                "token": token,
                "parent_pid": os.getpid(),
                "started_monotonic": phase_started,
                "previous_receipt_sha256": previous.copy(),
                "reservation_file_sha256": p.file_hash(directory / "reservation.json"),
            }
            p.write(directory / f"{phase}-reservation.json", grant, exclusive=True)
            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.benchmarks.worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                phase_directory / "worker.log",
                root=root,
                environment=env,
                started=phase_started,
                campaign_deadline=deadline,
            )
            outcome["last_dispatch"] = {"phase": phase, **dispatch}
            if (phase_directory / "receipt.json").exists():
                receipt, valid = validate_receipt(root, directory, phase, dispatch)
                outcome["stages"].append(receipt)
                previous[phase] = p.file_hash(phase_directory / "receipt.json")
            else:
                outcome["stages"].append(recover_partial(phase_directory, phase))
                valid = False
            p.write(directory / "workflow.json", outcome)
            if not valid:
                raise RuntimeError("Failed/incomplete phase: " + phase)
        aggregation_started = time.monotonic()
        outcome.update(aggregate(outcome["stages"]))
        if not outcome["comparison_success"]:
            raise RuntimeError("Scheduled campaign counts incomplete.")
        outcome["aggregation_seconds"] = time.monotonic() - aggregation_started
        if outcome["aggregation_seconds"] > 30:
            raise TimeoutError("Aggregation30s ceiling exceeded.")
        parent_check(deadline=deadline)
        outcome["status"] = "completed"
    except BaseException as exc:
        outcome.update(
            status="failed_consumed_no_retry"
            if reserved
            else "blocked_before_reservation",
            error=f"{type(exc).__name__}: {exc}",
        )
        outcome.update(aggregate(outcome["stages"]))
        outcome["comparison_success"] = False
    finally:
        outcome.update(
            finished_utc=p.now(),
            wall_seconds=time.monotonic() - started,
            reserved_consumed=reserved,
            retry_allowed=False,
            controller_peak_rss_bytes=__import__("resource")
            .getrusage(__import__("resource").RUSAGE_SELF)
            .ru_maxrss,
        )
        if outcome["wall_seconds"] > 600:
            outcome.update(
                status="failed_consumed_no_retry"
                if reserved
                else "blocked_before_reservation",
                comparison_success=False,
                error="Whole600s campaign ceiling exceeded.",
            )
        if reserved:
            p.write(directory / "workflow.json", outcome)
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--run-campaign",
        action="store_true",
        help="Execute the one authorized fixed campaign after current acceptance.",
    )
    action.add_argument(
        "--validate-prerequisites",
        action="store_true",
        help="Small metadata/acceptance only; never reserves or opens data.",
    )
    args = parser.parse_args()
    if args.validate_prerequisites:
        try:
            prerequisites()
            print(
                "Frozen identities and current benchmark acceptance verified; no slot/data access."
            )
            return 0
        except Exception as exc:
            print("Prerequisite blocked: " + str(exc))
            return 1
    outcome = run_campaign()
    print(
        json.dumps(
            {
                key: outcome.get(key)
                for key in (
                    "status",
                    "error",
                    "reserved_consumed",
                    "counts",
                    "wall_seconds",
                )
            },
            indent=2,
        )
    )
    return 0 if outcome["status"] == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
