"""One fixed stdlib-controlled frozen ONNX export/equivalence attempt."""

import argparse
import os
import secrets
import subprocess
import sys
import time

from raregate.benchmarks import protocol as p
from raregate.benchmarks.frozen_cpu import terminate
from raregate.benchmarks.frozen_cpu_v2 import fresh_hardware
from raregate.benchmarks.guard import parent_check
from raregate.exports import onnx_protocol as q

STAGES = {"startup": 28, "export": 30, "synthetic": 60, "real": 60, "cleanup": 2}
ORDER = tuple(STAGES)


def reserve(root, accepted, started, on_created=lambda path: None):
    directory = q.fixed(root, q.OUTPUT)
    directory.mkdir(exist_ok=False)
    on_created(directory)
    reservation = dict(
        task="0024",
        status="reserved_no_retry",
        parent_pid=os.getpid(),
        started_monotonic=started,
        protocol_canonical_JSON_sha256=q.HASH,
        source_file_sha256=accepted["source_file_sha256"],
        acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
        code=p.code_context(root),
    )
    p.write(directory / "reservation.json", reservation, exclusive=True)
    (directory / "acceptance.json").write_bytes((root / q.ACCEPTANCE).read_bytes())
    (directory / "protocol.json").write_bytes((root / q.CONFIG).read_bytes())
    return directory, reservation


def supervise(
    command, directory, environment, root, started, token, *, wall_seconds=180
):
    deadline = started + wall_seconds
    operation_deadline = deadline - 2
    child = error = None
    stage_starts = {}
    observed = []
    log = directory / "worker.log"
    try:
        with log.open("x") as out:
            child = subprocess.Popen(
                command,
                cwd=root,
                env=environment,
                stdout=out,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            stage_starts["startup"] = started
            while child.poll() is None:
                parent_check(deadline=operation_deadline)
                current = "startup"
                if (directory / "phase.json").exists():
                    phase = p.read(directory / "phase.json")
                    name = phase["name"]
                    tick = phase["started_monotonic"]
                    if (
                        phase.get("token") != token
                        or name not in STAGES
                        or not started <= tick <= time.monotonic()
                    ):
                        raise ValueError("Foreign/malformed phase telemetry.")
                    if name not in stage_starts:
                        if observed and ORDER.index(name) <= ORDER.index(observed[-1]):
                            raise ValueError("Repeated/regressed stage deadline.")
                        stage_starts[name] = tick
                        observed.append(name)
                    elif stage_starts[name] != tick:
                        raise ValueError("Stage deadline reset refused.")
                    current = name
                if time.monotonic() > stage_starts[current] + STAGES[current]:
                    raise TimeoutError("Independent parent stage deadline: " + current)
                if log.stat().st_size > 1048576:
                    raise ValueError("Bounded worker log ceiling.")
                try:
                    child.wait(timeout=0.05)
                except subprocess.TimeoutExpired:
                    pass
    except BaseException as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if child is not None:
            try:
                terminate(child, min(time.monotonic() + 2, deadline))
            except BaseException as exc:
                error = error or str(exc)
    elapsed = time.monotonic() - started
    return dict(
        returncode=child.returncode if child else None,
        parent_error=error,
        child_reaped=child is not None and child.poll() is not None,
        wall_seconds=elapsed,
        deadline_passed=elapsed <= wall_seconds,
        observed_stages=observed,
    )


def valid(result, dispatch, source):
    resources = result.get("resources", {})
    return bool(
        result.get("task") == "0024"
        and result.get("status") == "completed_accepted"
        and result.get("source_file_sha256") == source
        and result.get("protocol_canonical_JSON_sha256") == q.HASH
        and dispatch["returncode"] == 0
        and dispatch["parent_error"] is None
        and dispatch["child_reaped"]
        and dispatch["deadline_passed"]
        and 0 < resources.get("peak_rss_bytes", 0) <= 1073741824
        and 0 < resources.get("native_heap_reserved_bytes", 0) <= 536870912
        and resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
        and result.get("real", {}).get("status") == "passed"
        and result["real"].get("windows_verified") == 1193
        and result["real"].get("row_window_presentations") == 5120
        and result["real"].get("decision_mismatches") == [0] * 4
        and len(result.get("synthetic", [])) == 4
        and all(f["verification"]["status"] == "passed" for f in result["synthetic"])
        and result.get("access", {}).get("array_reads_completed") == 1
        and result["access"].get("population_requests") == 0
        and result["access"].get("store_custody_requests") == 0
        and result.get("optimizer_updates") == 0
        and result.get("performance_timer_invocations") == 0
        and result.get("test_background_model_access") is False
        and result.get("test_signal_model_access") is False
    )


def run(root=q.ROOT):
    start = time.monotonic()
    directory = None
    outcome = dict(
        task="0024",
        status="blocked_before_reservation",
        reserved=False,
        optimizer_updates=0,
        performance_timer_invocations=0,
        test_background_model_access=False,
        test_signal_model_access=False,
    )
    try:
        parent_check()
        if sys.platform != "darwin":
            raise ValueError(
                "Supported primary Darwin own-process accounting required."
            )
        path = q.fixed(root, q.OUTPUT)
        if path.exists() or path.is_symlink():
            raise ValueError(
                "Fixed output foreign/reserved/partial/inflight/completed; no reset/retry."
            )
        spec = q.load(root)
        q.check_dependencies(root, spec)
        frozen = q.frozen_metadata(root, spec)
        accepted = q.acceptance(root)

        def created(path):
            nonlocal directory
            directory = path

        directory, reservation = reserve(root, accepted, start, created)
        outcome.update(
            reserved=True,
            status="reserved_no_retry",
            frozen_metadata=frozen,
            hardware=fresh_hardware(),
        )
        worker_start = time.monotonic()
        token = secrets.token_hex(24)
        grant = dict(
            token=token,
            parent_pid=os.getpid(),
            started_monotonic=worker_start,
            whole_deadline_monotonic=start + 178,
            reservation_file_byte_sha256=p.file_hash(directory / "reservation.json"),
        )
        p.write(directory / "worker-grant.json", grant, exclusive=True)
        environment = dict(
            os.environ,
            **spec["runtime"]["thread_environment_before_imports"],
            PYTHONPATH=str(root / "src"),
        )
        dispatch = supervise(
            [
                sys.executable,
                "-m",
                "raregate.exports.onnx_worker",
                "--token",
                token,
            ],
            directory,
            environment,
            root,
            worker_start,
            token,
            wall_seconds=max(0.001, 180 - (worker_start - start)),
        )
        outcome["dispatch"] = dispatch
        if (directory / "receipt.json").exists():
            result = p.read(directory / "receipt.json")
        else:
            result = (
                p.read(directory / "partial.json")
                if (directory / "partial.json").exists()
                else dict(status="worker_receipt_missing")
            )
            if (directory / "access.json").exists():
                result["access"] = p.read(directory / "access.json")
            result["possible_inflight_work"] = True
        outcome["worker"] = result
        if not valid(result, dispatch, reservation["source_file_sha256"]):
            raise ValueError(
                "Failed/incomplete consumed frozen export/equivalence; no replay."
            )
        outcome["status"] = "complete_accepted_consumed_no_retry"
    except BaseException as exc:
        outcome.update(
            status="failed_consumed_no_retry"
            if directory is not None
            else "blocked_before_reservation",
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        outcome["whole_attempt_wall_seconds"] = time.monotonic() - start
        outcome["parent_peak_rss_bytes"] = parent_check()
        if directory is not None:
            p.write(directory / "workflow.json", outcome)
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-export", action="store_true", required=True)
    parser.parse_args()
    result = run()
    print(f"Task0024: {result['status']}; reserved={result['reserved']}")
    if result.get("error"):
        print(result["error"])
    return 0 if result["status"] == "complete_accepted_consumed_no_retry" else 2


if __name__ == "__main__":
    sys.exit(main())
