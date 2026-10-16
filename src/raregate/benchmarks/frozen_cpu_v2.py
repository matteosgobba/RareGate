"""Stdlib controller for one independent complete frozen CPU v2 campaign."""

import argparse
import os
import secrets
import sys
import time

from raregate.benchmarks import frozen_cpu_v2_protocol as q
from raregate.benchmarks import protocol as p
from raregate.benchmarks.frozen_cpu import (
    aggregate,
    hardware_context,
    recover_partial,
    supervise,
)
from raregate.benchmarks.guard import parent_check


def prerequisites(root=q.ROOT, *, synthetic=False):
    parent_check()
    if sys.platform != "darwin":
        raise ValueError("Supported Darwin primary accounting required for execution.")
    spec = q.load(root)
    frozen = q.metadata(root, spec)
    accepted = None if synthetic else q.acceptance(root)
    parent_check()
    return spec, frozen, accepted


def reserve(
    root, spec, frozen, accepted, started, *, synthetic=False, on_created=lambda: None
):
    directory = q.fixed(root, q.SYNTHETIC if synthetic else q.OUTPUT)
    directory.mkdir(exist_ok=False)
    on_created()
    reservation = {
        "task": "0022",
        "status": "reserved_no_retry",
        "parent_pid": os.getpid(),
        "started_monotonic": started,
        "reserved_utc": p.now(),
        "source_sha256": p.source_map(root),
        "protocol_canonical_sha256": q.HASH,
        "frozen_metadata": frozen,
        "code": p.code_context(root),
    }
    if not synthetic:
        if accepted["source_sha256"] != reservation["source_sha256"]:
            raise ValueError("Acceptance/source changed at reservation.")
        reservation["acceptance_file_sha256"] = p.file_hash(root / q.ACCEPTANCE)
        (directory / "acceptance.json").write_bytes((root / q.ACCEPTANCE).read_bytes())
    p.write(directory / "reservation.json", reservation, exclusive=True)
    p.write(directory / "protocol.json", spec, exclusive=True)
    return directory, reservation


def validate_receipt(root, directory, phase, dispatch):
    receipt_path = (
        directory / "receipt.json"
        if phase == "synthetic"
        else directory / phase / "receipt.json"
    )
    result = p.read(receipt_path)
    resources = result.get("resources", {})
    valid = (
        result.get("task") == "0022"
        and result.get("phase") == phase
        and result.get("status") == "completed"
        and result.get("source_sha256") == p.source_map(root)
        and result.get("binding", {}).get("protocol_canonical_sha256") == q.HASH
        and result["binding"]["grant_file_sha256"]
        == p.file_hash(directory / f"{phase}-reservation.json")
        and result["binding"]["reservation_file_sha256"]
        == p.file_hash(directory / "reservation.json")
        and result.get("optimizer_updates") == 0
        and result.get("test_background_model_access") is False
        and result.get("test_signal_model_access") is False
        and dispatch["returncode"] == 0
        and dispatch["child_reaped"]
        and dispatch["deadline_passed"]
        and dispatch["parent_error"] is None
        and 0 < result["elapsed_seconds_including_imports_cleanup"] <= 60
        and 0 < resources.get("peak_rss_bytes", 0) <= 1073741824
        and 0 < resources.get("native_heap_reserved_bytes", 0) <= 536870912
        and resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
    )
    if phase in q.PHASES[1:] and result.get("status") == "completed":
        valid &= (
            len(result["cells"]) == 15
            and len(result["empty_timer_pair_nanoseconds"]) == 200
        )
        valid &= all(
            c["status"] == "completed"
            and c["warmups_completed"] == 20
            and c["timed_completed"] == 200
            for c in result["cells"]
        )
        valid &= result["hashes_before"] == result["hashes_after"]
        valid &= [(c["batch"], c["scope"]) for c in result["cells"]] == [
            (b, scope)
            for b in (1, 8, 32, 128, 1024)
            for scope in ("reconstruction", "score_decision", "adapter_decision")
        ]
        valid &= all(c["latency_nanoseconds"]["count"] == 200 for c in result["cells"])
        valid &= result["access_audit"]["local_array_reads_completed"] == 1
        valid &= result["access_audit"]["original_array_reads_completed"] == 0
        valid &= all(
            result["numerical"][w]["status"] == "passed" for w in ("before", "after")
        )
        valid &= all(
            c["passed"]
            for w in ("before", "after")
            for c in result["numerical"][w]["comparisons"]
        )
        for key in ("reference_reconstruction_sha256", "reference_scores_sha256"):
            valid &= (
                result["numerical"]["before"][key] == result["numerical"]["after"][key]
            )
        if phase.startswith("AE"):
            valid &= all(
                result["numerical"][w]["mismatches_per_threshold"] == [0] * 4
                for w in ("before", "after")
            )
            for key in ("diagnostic_FP64_reference_sha256", "envelope_sha256"):
                valid &= (
                    result["numerical"]["before"][key]
                    == result["numerical"]["after"][key]
                )
    if phase == "prepare":
        valid &= (
            result["access_audit"]["original_array_reads_completed"] == 1
            and result["access_audit"]["local_array_reads_completed"] == 0
        )
    if phase == "synthetic" and result.get("status") == "completed":
        valid &= len(result["families"]) == 8 and all(
            f["status"] == "completed" for f in result["families"]
        )
        valid &= all(
            c.get("passed") is True
            for f in result["families"]
            for c in f["comparisons"]
        )
    result["parent_dispatch"] = dispatch
    return result, bool(valid)


def fresh_hardware():
    import json
    import subprocess

    result = hardware_context()
    try:
        raw = subprocess.check_output(
            ["/usr/sbin/system_profiler", "-json", "SPHardwareDataType"],
            text=True,
            stderr=subprocess.PIPE,
            timeout=2,
        )
        if len(raw.encode()) > 65536:
            raise ValueError("Bounded hardware metadata exceeded.")
        values = json.loads(raw)["SPHardwareDataType"][0]
        result["fresh_hardware_profile"] = {
            key: values.get(key)
            for key in (
                "machine_name",
                "machine_model",
                "chip_type",
                "physical_memory",
                "number_processors",
            )
        }
        result["fresh_hardware_profile"]["status"] = "available"
    except (
        OSError,
        subprocess.SubprocessError,
        ValueError,
        KeyError,
        IndexError,
    ) as exc:
        result["fresh_hardware_profile"] = {"status": "unknown", "error": str(exc)}
    # Successful process exit does not make pmset's reported errors valid context.
    if "Error:" in result.get("thermal", {}).get("raw", ""):
        result["thermal"]["status"] = "unknown"
    return result


def run_campaign(root=q.ROOT, *, synthetic=False):
    started = time.monotonic()
    deadline = started + (60 if synthetic else 600)
    directory = root / (q.SYNTHETIC if synthetic else q.OUTPUT)
    owned = False
    outcome = {
        "schema_version": 1,
        "task": "0022",
        "status": "blocked_before_reservation",
        "stages": [],
        "optimizer_updates": 0,
        "test_background_model_access": False,
        "test_signal_model_access": False,
    }
    try:
        if directory.exists() or directory.is_symlink():
            raise ValueError(
                "Fixed v2 output reserved/partial/foreign/consumed; no retry."
            )
        spec, frozen, accepted = prerequisites(root, synthetic=synthetic)

        def created():
            nonlocal owned
            owned = True

        directory, reservation = reserve(
            root,
            spec,
            frozen,
            accepted,
            started,
            synthetic=synthetic,
            on_created=created,
        )
        outcome.update(
            status="running_reserved_no_retry",
            source_sha256=reservation["source_sha256"],
            protocol_canonical_sha256=q.HASH,
            started_utc=p.now(),
        )
        if not synthetic:
            outcome["hardware"] = fresh_hardware()
        environment = dict(
            os.environ, **spec["runtime"]["thread_environment_before_imports"]
        )
        environment["PYTHONPATH"] = str(root / "src")
        previous = {}
        for phase in ("synthetic",) if synthetic else q.PHASES:
            parent_check(deadline=deadline)
            if not synthetic and time.monotonic() + 62 > deadline:
                raise TimeoutError(
                    "Insufficient full worker/cleanup slack before dispatch."
                )
            phase_directory = directory if synthetic else directory / phase
            if not synthetic:
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
                    "raregate.benchmarks.frozen_cpu_v2_worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                phase_directory / "worker.log",
                root=root,
                environment=environment,
                started=phase_started,
                campaign_deadline=deadline,
            )
            outcome["last_dispatch"] = dict(dispatch, phase=phase)
            if (phase_directory / "receipt.json").exists():
                result, valid = validate_receipt(root, directory, phase, dispatch)
                previous[phase] = p.file_hash(phase_directory / "receipt.json")
            else:
                result = recover_partial(phase_directory, phase)
                valid = False
            outcome["stages"].append(result)
            p.write(directory / "workflow.json", outcome)
            if not valid:
                raise RuntimeError("Failed/incomplete v2 phase: " + phase)
        tick = time.monotonic()
        if not synthetic:
            outcome.update(aggregate(outcome["stages"]))
            if (
                not outcome["comparison_success"]
                or outcome["counts"]["empty_timer_pairs"] != 1200
            ):
                raise ValueError("New independent campaign counts incomplete.")
        outcome["aggregation_seconds"] = time.monotonic() - tick
        if outcome["aggregation_seconds"] > 30:
            raise TimeoutError("30s aggregation budget exceeded.")
        parent_check(deadline=deadline)
        outcome["status"] = "completed"
    except BaseException as exc:
        outcome.update(
            status="failed_consumed_no_retry"
            if owned
            else "blocked_before_reservation",
            error=f"{type(exc).__name__}: {exc}",
        )
        if not synthetic:
            outcome.update(aggregate(outcome["stages"]))
            outcome["comparison_success"] = False
    finally:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        outcome.update(
            reserved_consumed=owned,
            retry_allowed=False,
            wall_seconds=time.monotonic() - started,
            controller_peak_rss_bytes=rss if sys.platform == "darwin" else rss * 1024,
            finished_utc=p.now(),
        )
        if (
            outcome["wall_seconds"] > (60 if synthetic else 600)
            or outcome["controller_peak_rss_bytes"] > 134217728
        ):
            outcome.update(
                status="failed_consumed_no_retry"
                if owned
                else "blocked_before_reservation",
                comparison_success=False,
                error="Controller budget exceeded.",
            )
        if owned:
            p.write(directory / "workflow.json", outcome)
    print(outcome["status"], outcome.get("counts", {}), outcome.get("error", ""))
    return 0 if outcome["status"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--run-campaign", action="store_true")
    action.add_argument("--synthetic-validation", action="store_true")
    action.add_argument("--validate-prerequisites", action="store_true")
    args = parser.parse_args()
    if args.validate_prerequisites:
        prerequisites()
        if (q.ROOT / q.OUTPUT).exists():
            raise ValueError("Campaign already reserved/consumed; no retry.")
        print(
            "v2 metadata/source/header prerequisites verified; no numerical array opening or reservation."
        )
        return 0
    return run_campaign(synthetic=args.synthetic_validation)


if __name__ == "__main__":
    raise SystemExit(main())
