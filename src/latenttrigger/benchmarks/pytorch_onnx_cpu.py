"""Stdlib Task0025 CLI: metadata checks or one exclusive paired CPU campaign."""

import argparse
import os
import resource
import secrets
import sys
import time

from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks import pytorch_onnx_cpu_protocol as q
from latenttrigger.benchmarks.frozen_cpu import supervise
from latenttrigger.benchmarks.frozen_cpu_v2 import fresh_hardware
from latenttrigger.benchmarks.guard import parent_check
from latenttrigger.benchmarks.pytorch_onnx_cpu_statistics import aggregate
from latenttrigger.exports.onnx_protocol import refuse_early_imports


def prerequisites(root=q.ROOT):
    refuse_early_imports()
    parent_check()
    if sys.platform != "darwin":
        raise ValueError(
            "Supported primary Darwin accounting required; no real dispatch."
        )
    spec = q.load(root)
    frozen = q.metadata(root, spec)
    accepted = q.acceptance(root)
    if q.fixed(root, q.OUTPUT).exists():
        raise ValueError("Fixed namespace reserved/partial/foreign/consumed; no retry.")
    return spec, frozen, accepted


def reserve(root, spec, frozen, accepted, started, *, on_created=lambda: None):
    directory = q.fixed(root, q.OUTPUT)
    directory.mkdir(exist_ok=False)
    on_created()
    reservation = dict(
        task="0025",
        status="reserved_no_retry",
        parent_pid=os.getpid(),
        started_monotonic=started,
        reserved_utc=p.now(),
        protocol_canonical_JSON_sha256=q.HASH,
        source_file_sha256=q.source_map(root),
        acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
        frozen_metadata=frozen,
        code=p.code_context(root),
    )
    if reservation["source_file_sha256"] != accepted["source_file_sha256"]:
        raise ValueError("Source changed at atomic reservation; consumed.")
    p.write(directory / "reservation.json", reservation, exclusive=True)
    p.write(directory / "protocol.json", spec, exclusive=True)
    with (directory / "acceptance.json").open("xb") as dst:
        dst.write((root / q.ACCEPTANCE).read_bytes())
    return directory, reservation


def valid_receipt(root, directory, phase, result, dispatch):
    resources = result.get("resources", {})
    valid = (
        result.get("task") == "0025"
        and result.get("phase") == phase
        and result.get("status") == "completed"
        and result.get("source_file_sha256") == q.source_map(root)
        and result.get("protocol_canonical_JSON_sha256") == q.HASH
        and result.get("binding")
        == dict(
            grant_file_sha256=p.file_hash(directory / (phase + "-reservation.json")),
            reservation_file_sha256=p.file_hash(directory / "reservation.json"),
        )
        and result.get("optimizer_updates") == 0
        and result.get("test_background_model_access") is False
        and result.get("test_signal_model_access") is False
        and dispatch["returncode"] == 0
        and dispatch["child_reaped"]
        and dispatch["deadline_passed"]
        and dispatch["parent_error"] is None
        and 0 < result.get("worker_wall_seconds", 0) <= 60
        and 0 < resources.get("peak_rss_bytes", 0) <= 1073741824
        and 0 < resources.get("native_heap_reserved_bytes", 0) <= 536870912
        and resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
        and result.get("effective_threads_before")
        == result.get("effective_threads_after")
        and result.get("providers_before") == result.get("providers_after")
    )
    if phase == "prepare":
        valid &= (
            len(result.get("synthetic", [])) == 4
            and all(
                r["verification"]["status"] == "passed"
                and r["verification"]["decision_mismatches"] == [0] * 4
                and r["verification"]["local_affine_violations"] == 0
                for r in result["synthetic"]
            )
            and result["access"]["original_array_reads_completed"] == 1
            and result["access"]["local_array_reads_completed"] == 0
        )
    else:
        valid &= (
            len(result.get("cells", [])) == 15
            and len(result.get("empty_timer_pair_nanoseconds", [])) == 200
            and [(c["batch"], c["scope"]) for c in result["cells"]]
            == [(b, s) for b in q.BATCHES for s in q.SCOPES]
            and all(
                c["status"] == "completed"
                and c["timed_completed"] == 200
                and c["warmups_completed"] == 20
                and c["latency_nanoseconds"]["count"] == 200
                for c in result["cells"]
            )
            and result["access"]["local_array_reads_completed"] == 1
            and result["access"]["original_array_reads_completed"] == 0
            and result["hashes_before"] == result["hashes_after"]
        )
        valid &= all(
            result["numerical"][w]["status"] == "passed"
            and result["numerical"][w]["decision_mismatches"] == [0] * 4
            and result["numerical"][w]["local_affine_violations"] == 0
            and result["numerical"][w]["windows_verified"] == 1193
            for w in ("before", "after")
        )
    return bool(valid)


def recover(directory, phase):
    result = (
        p.read(directory / "partial.json")
        if (directory / "partial.json").exists()
        else dict(phase=phase, cells=[])
    )
    if (directory / "access.json").exists():
        result["access"] = p.read(directory / "access.json")
    result.update(
        status="failed", receipt_missing=True, possible_inflight_invocation_unknown=True
    )
    return result


def run_campaign(root=q.ROOT):
    started = time.monotonic()
    deadline = started + 600
    owned = False
    directory = root / q.OUTPUT
    outcome = dict(
        task="0025",
        status="blocked_before_reservation",
        stages=[],
        optimizer_updates=0,
        test_background_model_access=False,
        test_signal_model_access=False,
    )
    try:
        spec, frozen, accepted = prerequisites(root)

        def created():
            nonlocal owned
            owned = True

        directory, reservation = reserve(
            root, spec, frozen, accepted, started, on_created=created
        )
        outcome.update(
            status="running_reserved_no_retry",
            source_file_sha256=reservation["source_file_sha256"],
            protocol_canonical_JSON_sha256=q.HASH,
            hardware=fresh_hardware(),
        )
        env = dict(
            os.environ,
            **spec["runtime"]["thread_environment_before_imports"],
            PYTHONPATH=str(root / "src"),
        )
        previous = {}
        for phase in q.PHASES:
            parent_check(deadline=deadline)
            if time.monotonic() + 62 > deadline:
                raise TimeoutError("Insufficient worker/cleanup slack.")
            d = directory / phase
            d.mkdir()
            tick = time.monotonic()
            token = secrets.token_hex(24)
            grant = dict(
                phase=phase,
                token=token,
                parent_pid=os.getpid(),
                started_monotonic=tick,
                previous_receipt_sha256=previous.copy(),
                reservation_file_sha256=p.file_hash(directory / "reservation.json"),
            )
            p.write(directory / (phase + "-reservation.json"), grant, exclusive=True)
            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.benchmarks.pytorch_onnx_cpu_worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                d / "worker.log",
                root=root,
                environment=env,
                started=tick,
                campaign_deadline=deadline,
            )
            outcome["last_dispatch"] = dict(dispatch, phase=phase)
            if (d / "receipt.json").exists():
                result = p.read(d / "receipt.json")
                valid = valid_receipt(root, directory, phase, result, dispatch)
                if not valid:
                    result["status"] = "failed"
                previous[phase] = p.file_hash(d / "receipt.json")
            else:
                result = recover(d, phase)
                valid = False
            result["parent_dispatch"] = dispatch
            outcome["stages"].append(result)
            p.write(directory / "workflow.json", outcome)
            if not valid:
                raise RuntimeError("Failed/incomplete phase: " + phase)
        tick = time.monotonic()
        outcome.update(aggregate(outcome["stages"], directory))
        outcome["aggregation_seconds"] = time.monotonic() - tick
        if outcome["aggregation_seconds"] > 30 or not outcome["comparison_success"]:
            raise ValueError("Incomplete campaign or aggregation deadline.")
        parent_check(deadline=deadline)
        outcome["status"] = "completed_accepted"
    except BaseException as exc:
        outcome.update(
            status="failed_consumed_no_retry"
            if owned
            else "blocked_before_reservation",
            error=f"{type(exc).__name__}: {exc}",
        )
        if owned:
            try:
                outcome.update(aggregate(outcome["stages"], directory))
            except BaseException as aggregation_error:
                outcome["aggregation_error"] = str(aggregation_error)
        outcome["comparison_success"] = False
    finally:
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        outcome.update(
            reserved_consumed=owned,
            retry_allowed=False,
            wall_seconds=time.monotonic() - started,
            controller_peak_rss_bytes=rss if sys.platform == "darwin" else rss * 1024,
            finished_utc=p.now(),
        )
        if (
            outcome["wall_seconds"] > 600
            or outcome["controller_peak_rss_bytes"] > 134217728
        ):
            outcome.update(
                status="failed_consumed_no_retry"
                if owned
                else "blocked_before_reservation",
                comparison_success=False,
                error="Controller resource/deadline exceeded.",
            )
        if owned:
            p.write(directory / "workflow.json", outcome)
    print(outcome["status"], outcome.get("counts", {}), outcome.get("error", ""))
    return 0 if outcome["status"] == "completed_accepted" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--validate-prerequisites", action="store_true")
    actions.add_argument("--run-campaign", action="store_true")
    args = parser.parse_args()
    if args.validate_prerequisites:
        prerequisites()
        print(
            "Metadata/header/current source verified; zero numerical opening/reservation."
        )
        return 0
    return run_campaign()


if __name__ == "__main__":
    raise SystemExit(main())
