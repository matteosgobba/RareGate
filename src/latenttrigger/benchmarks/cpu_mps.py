"""Stdlib-only one-shot CPU/MPS proof and conditional contemporaneous campaign."""

import argparse
import math
import os
import secrets
import statistics
import subprocess
import sys
import time

from latenttrigger.benchmarks import cpu_mps_protocol as q
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.frozen_cpu import recover_partial, terminate
from latenttrigger.benchmarks.frozen_cpu_v2 import fresh_hardware
from latenttrigger.benchmarks.guard import parent_check


def supervise(command, log, *, root, environment, started, deadline, stage_seconds):
    phase_deadline = min(started + stage_seconds, deadline)
    operation_deadline = phase_deadline - 2
    if time.monotonic() >= operation_deadline:
        raise TimeoutError("Full cleanup slack required before dispatch.")
    child, error = None, None
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
                parent_check(deadline=operation_deadline)
                if log.stat().st_size > 1048576:
                    raise ValueError("Bounded child output exceeded.")
                try:
                    child.wait(timeout=0.05)
                except subprocess.TimeoutExpired:
                    pass
    except BaseException as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if child is not None:
            try:
                terminate(child, min(time.monotonic() + 2, phase_deadline))
            except BaseException as exc:
                error = error or str(exc)
    elapsed = time.monotonic() - started
    return dict(
        returncode=child.returncode if child else None,
        parent_error=error,
        elapsed_seconds_including_imports_cleanup=elapsed,
        child_reaped=child is not None and child.poll() is not None,
        deadline_passed=elapsed <= stage_seconds and time.monotonic() <= deadline,
    )


def make_reservation(
    root, relative, accepted, started, *, on_created=lambda path: None
):
    directory = q.exclusive(root, relative)
    on_created(directory)
    # mkdir is the irreversible consumption point, even if writing is interrupted.
    reservation = dict(
        task="0023",
        status="reserved_no_retry",
        parent_pid=os.getpid(),
        started_monotonic=started,
        utc=p.now(),
        source_sha256=accepted["source_sha256"],
        protocol_canonical_sha256=q.HASH,
        software_acceptance_sha256=p.file_hash(root / q.ACCEPTANCE),
        code=p.code_context(root),
    )
    p.write(directory / "reservation.json", reservation, exclusive=True)
    return directory, reservation


def dispatch(root, directory, phase, environment, deadline, previous, execution=None):
    parent_check(deadline=deadline)
    seconds = 30 if phase == "availability" else 60
    if time.monotonic() + seconds > deadline:
        raise TimeoutError("Insufficient complete stage/cleanup slack before dispatch.")
    child_directory = directory / phase
    child_directory.mkdir(exist_ok=False)
    started = time.monotonic()
    token = secrets.token_hex(24)
    grant = dict(
        phase=phase,
        token=token,
        parent_pid=os.getpid(),
        started_monotonic=started,
        previous_receipt_sha256=previous.copy(),
        reservation_file_sha256=p.file_hash(directory / "reservation.json"),
    )
    if execution:
        grant["execution_acceptance_sha256"] = p.file_hash(
            directory / "execution-acceptance.json"
        )
    p.write(directory / f"{phase}-reservation.json", grant, exclusive=True)
    supervision = supervise(
        [
            sys.executable,
            "-m",
            "latenttrigger.benchmarks.cpu_mps_worker",
            "--phase",
            phase,
            "--token",
            token,
        ],
        child_directory / "worker.log",
        root=root,
        environment=environment,
        started=started,
        deadline=deadline,
        stage_seconds=seconds,
    )
    if not (child_directory / "receipt.json").exists():
        result = recover_partial(child_directory, phase)
    else:
        result = p.read(child_directory / "receipt.json")
        previous[phase] = p.file_hash(child_directory / "receipt.json")
    result["parent_dispatch"] = supervision
    return result


def valid(result, phase, source):
    host = result.get("resources", {})
    supervised = result["parent_dispatch"]
    ok = (
        result.get("task") == "0023"
        and result.get("phase") == phase
        and result.get("source_sha256") == source
        and result.get("protocol_canonical_sha256") == q.HASH
        and result.get("status") == "completed"
        and result.get("optimizer_updates") == 0
        and result.get("test_background_model_access") is False
        and result.get("test_signal_model_access") is False
        and host.get("latched_error") is None
        and host.get("owned_thread_alive") is False
        and 0 < host.get("peak_rss_bytes", 0) <= 1073741824
        and 0 < host.get("native_heap_reserved_bytes", 0) <= 536870912
        and supervised["returncode"] == 0
        and supervised["child_reaped"]
        and supervised["deadline_passed"]
        and supervised["parent_error"] is None
    )
    device = result.get("device_resources", {})
    if phase in ("availability", "synthetic") or phase.startswith("MPS"):
        ok &= (
            device.get("status") == "active"
            and device.get("latched_error") is None
            and type(device.get("tensor_peak_bytes")) is int
            and 0 <= device["tensor_peak_bytes"] <= 268435456
            and type(device.get("driver_peak_bytes")) is int
            and 0 <= device["driver_peak_bytes"] <= 536870912
            and device.get("samples", 0) > 0
        )
    else:
        ok &= (
            device.get("status") == "not_applicable"
            and device.get("tensor_peak_bytes") is None
            and device.get("driver_peak_bytes") is None
        )
    access = result.get("access_audit", {})
    ok &= (
        access.get("population_requests") == 0
        and access.get("store_custody_requests") == 0
    )
    if phase == "availability":
        ok &= (
            result.get("constant_device_proof", {}).get("status") == "passed"
            and access.get("rows_loaded") == 0
        )
    elif phase == "synthetic":
        families = result.get("families", [])
        ok &= (
            [f["name"] for f in families]
            == ["constants", "powers", "uniform", "normal"]
            and all(
                f["status"] == "passed" and f["before"] == f["after"] for f in families
            )
            and access.get("rows_loaded") == 0
        )
    elif phase == "prepare":
        ok &= (
            access.get("original_array_reads_completed") == 1
            and access.get("local_array_reads_completed") == 0
            and access.get("rows_loaded") == 1024
        )
    else:
        cells = result.get("cells", [])
        ok &= (
            access.get("local_array_reads_completed") == 1
            and access.get("original_array_reads_completed") == 0
            and access.get("rows_loaded") == 1024
            and len(result.get("empty_timer_pairs_nanoseconds", [])) == 200
            and len(cells) == 15
            and [(c["batch"], c["scope"]) for c in cells]
            == [
                (b, s)
                for b in (1, 8, 32, 128, 1024)
                for s in ("reconstruction", "score_decision", "adapter_decision")
            ]
            and all(
                c.get("status") == "completed"
                and c.get("warmups_completed") == 20
                and c.get("timed_completed") == 200
                and c.get("latency_nanoseconds", {}).get("count") == 200
                for c in cells
            )
            and result.get("hashes_before") == result.get("hashes_after")
            and result.get("numerical", {}).get("before", {}).get("status") == "passed"
            and result["numerical"]["before"] == result["numerical"]["after"]
        )
    return bool(ok)


def aggregate(stages):
    cells = [c for result in stages for c in result.get("cells", [])]
    counts = dict(
        measured_cells_completed=sum(c.get("status") == "completed" for c in cells),
        timed_invocations_completed=sum(c.get("timed_completed", 0) for c in cells),
        warmups_completed=sum(c.get("warmups_completed", 0) for c in cells),
        empty_timer_pairs=sum(
            len(r.get("empty_timer_pairs_nanoseconds", [])) for r in stages
        ),
    )
    completed = [c for c in cells if c.get("status") == "completed"]
    groups = {}
    for cell in completed:
        groups.setdefault((cell["device"], cell["batch"], cell["scope"]), []).append(
            cell
        )
    distributions = []
    for (device, batch, scope), items in groups.items():
        count = sum(c["latency_nanoseconds"]["count"] for c in items)
        mean = (
            sum(
                c["latency_nanoseconds"]["mean"] * c["latency_nanoseconds"]["count"]
                for c in items
            )
            / count
        )
        distributions.append(
            dict(
                device=device,
                batch=batch,
                scope=scope,
                workers=len(items),
                worker_distributions=[
                    dict(worker=c["worker"], **c["latency_nanoseconds"]) for c in items
                ],
                median_worker_medians_nanoseconds=statistics.median(
                    c["latency_nanoseconds"]["p50"] for c in items
                ),
                pooled_mean_invocation_nanoseconds=mean,
                throughput_events_per_second=batch / (mean / 1e9),
                amortized_nanoseconds_per_event=mean / batch,
            )
        )
    pairs = []
    lookup = {(c["worker"], c["batch"], c["scope"]): c for c in completed}
    for batch in (1, 8, 32, 128, 1024):
        for scope in ("reconstruction", "score_decision", "adapter_decision"):
            ratios = []
            for repetition in (1, 2, 3):
                cpu, mps = (
                    lookup.get((f"CPU{repetition}", batch, scope)),
                    lookup.get((f"MPS{repetition}", batch, scope)),
                )
                if cpu is None or mps is None:
                    continue
                ratio = (
                    cpu["latency_nanoseconds"]["mean"]
                    / mps["latency_nanoseconds"]["mean"]
                )
                ratios.append(
                    dict(
                        pair=repetition,
                        CPU_mean_over_MPS_mean=ratio,
                        MPS_throughput_over_CPU_throughput=ratio,
                    )
                )
            if ratios:
                pairs.append(
                    dict(
                        batch=batch,
                        scope=scope,
                        pairs=ratios,
                        geometric_mean_ratio=math.exp(
                            statistics.fmean(
                                math.log(r["CPU_mean_over_MPS_mean"]) for r in ratios
                            )
                        ),
                        contemporaneous_only=True,
                    )
                )
    return dict(
        counts=counts,
        cells=cells,
        distributions=distributions,
        paired_ratios=pairs,
        missing_measured_cells=90 - counts["measured_cells_completed"],
        comparison_success=counts
        == dict(
            measured_cells_completed=90,
            timed_invocations_completed=18000,
            warmups_completed=1800,
            empty_timer_pairs=1200,
        ),
    )


def run_automatic(root=q.ROOT):
    start = time.monotonic()
    proof_deadline = start + 120
    proof_directory = real_directory = None
    outcome = dict(
        task="0023",
        status="blocked_before_device_proof",
        device_proof=[],
        stages=[],
        campaign_reserved=False,
        physical_device_validated=False,
        optimizer_updates=0,
        test_background_model_access=False,
        test_signal_model_access=False,
    )
    try:
        parent_check(deadline=proof_deadline)
        if sys.platform != "darwin":
            raise ValueError("Supported primary Darwin host accounting required.")
        if any(
            (root / name).exists() or (root / name).is_symlink()
            for name in (q.PROOF, q.OUTPUT)
        ):
            raise ValueError(
                "Existing device proof/campaign reserved/partial/foreign/consumed; no retry."
            )
        spec, accepted = q.load(root), q.software_acceptance(root)
        q.metadata(root, spec)
        environment = q.environment(spec)
        environment["PYTHONPATH"] = str(root / "src")

        def proof_created(path):
            nonlocal proof_directory
            proof_directory = path

        proof_directory, _ = make_reservation(
            root, q.PROOF, accepted, start, on_created=proof_created
        )
        outcome.update(
            source_sha256=accepted["source_sha256"],
            protocol_canonical_sha256=q.HASH,
            hardware=fresh_hardware(),
        )
        previous = {}
        for phase in ("availability", "synthetic"):
            result = dispatch(
                root, proof_directory, phase, environment, proof_deadline, previous
            )
            outcome["device_proof"].append(result)
            p.write(proof_directory / "workflow.json", outcome)
            if not valid(result, phase, accepted["source_sha256"]):
                outcome["status"] = (
                    "blocked_unavailable"
                    if result.get("status") == "blocked_unavailable"
                    else "blocked_device_proof_failed_no_retry"
                )
                raise ValueError(
                    result.get("error", "Incomplete physical device proof.")
                )
        parent_check(deadline=proof_deadline)
        q.software_acceptance(root)
        execution = dict(
            task="0023",
            status="device_proven",
            parent_pid=os.getpid(),
            source_sha256=accepted["source_sha256"],
            protocol_canonical_sha256=q.HASH,
            software_acceptance_sha256=p.file_hash(root / q.ACCEPTANCE),
            device_receipt_sha256=previous,
            proof_orchestration_seconds=time.monotonic() - start,
        )
        p.write(
            proof_directory / "execution-acceptance.json", execution, exclusive=True
        )
        outcome["physical_device_validated"] = True
        # No alternate run/reusable receipt route. Only this live parent continues.
        campaign_start = time.monotonic()
        deadline = campaign_start + 600
        q.metadata(root, spec)

        def real_created(path):
            nonlocal real_directory
            real_directory = path

        real_directory, _ = make_reservation(
            root, q.OUTPUT, accepted, campaign_start, on_created=real_created
        )
        outcome["campaign_reserved"] = True
        (real_directory / "execution-acceptance.json").write_bytes(
            (proof_directory / "execution-acceptance.json").read_bytes()
        )
        previous = {}
        for phase in q.PHASES:
            result = dispatch(
                root, real_directory, phase, environment, deadline, previous, execution
            )
            outcome["stages"].append(result)
            p.write(real_directory / "workflow.json", outcome)
            if not valid(result, phase, accepted["source_sha256"]):
                raise ValueError("Incomplete/failed consumed real phase: " + phase)
        tick = time.monotonic()
        outcome.update(aggregate(outcome["stages"]))
        outcome["aggregation_seconds"] = time.monotonic() - tick
        if outcome["aggregation_seconds"] > 30 or not outcome["comparison_success"]:
            raise ValueError("Incomplete finite aggregation/counts.")
        parent_check(deadline=deadline)
        outcome["campaign_wall_seconds"] = time.monotonic() - campaign_start
        outcome["status"] = "completed_consumed_no_retry"
    except BaseException as exc:
        if real_directory is not None or (
            outcome["physical_device_validated"] and (root / q.OUTPUT).exists()
        ):
            outcome.update(
                status="failed_campaign_consumed_no_retry", campaign_reserved=True
            )
        elif (
            outcome["status"] == "blocked_before_device_proof"
            and proof_directory is not None
        ):
            outcome["status"] = "blocked_device_proof_failed_no_retry"
        outcome["error"] = f"{type(exc).__name__}: {exc}"
        outcome.update(aggregate(outcome["stages"]))
    finally:
        outcome["whole_automatic_wall_seconds"] = time.monotonic() - start
        outcome["parent_peak_rss_bytes"] = parent_check()
        if proof_directory is not None:
            p.write(proof_directory / "workflow.json", outcome)
        if real_directory is not None:
            p.write(real_directory / "workflow.json", outcome)
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-campaign",
        action="store_true",
        required=True,
        help="One fresh availability check, conditional device proof and single paired campaign; fixed outputs; no retry.",
    )
    parser.parse_args()
    result = run_automatic()
    print(
        f"Task0023: {result['status']}; real reservation={result['campaign_reserved']}; physical validation={result['physical_device_validated']}"
    )
    if result.get("error"):
        print(result["error"])
    return 0 if result["status"] == "completed_consumed_no_retry" else 2


if __name__ == "__main__":
    sys.exit(main())
