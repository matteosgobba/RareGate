"""Stdlib exclusive numerical review controller and fresh guarded worker CLI."""

import argparse
import os
import secrets
import sys
import time

from latenttrigger.benchmarks import ae_parity_protocol as q
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.frozen_cpu import supervise
from latenttrigger.benchmarks.guard import Guard, parent_check


def reserve(root, spec, accepted, started, *, synthetic=False, on_created=lambda: None):
    directory = q.fixed_path(root, q.SYNTHETIC if synthetic else q.OUTPUT)
    directory.mkdir(exist_ok=False)
    on_created()
    grant = {
        "task": "0021",
        "mode": "synthetic" if synthetic else "real",
        "status": "reserved_no_retry",
        "parent_pid": os.getpid(),
        "token": secrets.token_hex(24),
        "started_monotonic": started,
        "worker_deadline": started + 58,
        "protocol_canonical_sha256": q.PROTOCOL_HASH,
        "source_sha256": p.source_map(root),
        "reserved_utc": p.now(),
        "code": p.code_context(root),
    }
    if not synthetic:
        if accepted["source_sha256"] != grant["source_sha256"]:
            raise ValueError("Acceptance/source changed during reservation.")
        grant["acceptance_file_sha256"] = p.file_hash(root / q.ACCEPTANCE)
        (directory / "acceptance.json").write_bytes((root / q.ACCEPTANCE).read_bytes())
    p.write(directory / "protocol.json", spec, exclusive=True)
    p.write(directory / "reservation.json", grant, exclusive=True)
    return directory, grant


def verify_worker(token, mode, root=q.ROOT):
    synthetic = mode == "synthetic"
    directory = q.fixed_path(root, q.SYNTHETIC if synthetic else q.OUTPUT)
    spec = q.load(root)
    grant = p.read(directory / "reservation.json")
    if (
        mode not in ("synthetic", "real")
        or grant["token"] != token
        or grant["mode"] != mode
        or grant["parent_pid"] != os.getppid()
        or grant["status"] != "reserved_no_retry"
        or grant["protocol_canonical_sha256"] != q.PROTOCOL_HASH
        or p.digest(p.read(directory / "protocol.json")) != q.PROTOCOL_HASH
        or grant["source_sha256"] != p.source_map(root)
        or not grant["started_monotonic"] <= time.monotonic() < grant["worker_deadline"]
        or grant["worker_deadline"] != grant["started_monotonic"] + 58
        or (directory / "receipt.json").exists()
    ):
        raise ValueError("Foreign/stale/duplicate diagnostic grant/source.")
    q.verify_metadata(root, spec)
    if not synthetic:
        q.verify_acceptance(root, campaign=True)
        if (
            p.file_hash(directory / "acceptance.json")
            != grant["acceptance_file_sha256"]
        ):
            raise ValueError("Review acceptance changed.")
    if any(
        os.environ.get(k) != v
        for k, v in spec["runtime"]["thread_environment_before_imports"].items()
    ):
        raise ValueError("Five thread variables must be set before imports.")
    if any(name in sys.modules for name in ("numpy", "torch", "sklearn", "h5py")):
        raise ValueError("Numerical imports precede guarded environment verification.")
    return directory, grant, spec


def worker(token, mode):
    started = time.monotonic()
    directory, grant, spec = verify_worker(token, mode)
    result = {
        "task": "0021",
        "mode": mode,
        "status": "started",
        "families": [],
        "audit": {
            "prepared_numerical_load_attempts": 0,
            "prepared_numerical_loads_completed": 0,
            "unique_reused_real_rows": 0,
            "new_store_population_requests": 0,
            "new_store_custody_operations": 0,
            "optimizer_updates": 0,
        },
        "source_sha256": grant["source_sha256"],
        "protocol_canonical_sha256": q.PROTOCOL_HASH,
        "reservation_file_sha256": p.file_hash(directory / "reservation.json"),
        "test_background_model_access": False,
        "test_signal_model_access": False,
        "runtime_versions": p.runtime_versions(),
        "stage_wall_seconds": {},
    }
    guard = Guard(
        grant["worker_deadline"], directory=None if mode == "synthetic" else directory
    )
    limiter = None
    try:
        guard.__enter__()
        guard.boundary("numerical_imports")
        tick = time.monotonic()
        from latenttrigger.benchmarks import ae_parity_numerics as n
        from latenttrigger.benchmarks import core

        result["stage_wall_seconds"]["imports"] = time.monotonic() - tick
        guard.boundary("thread_enforcement")
        limiter, result["threads_before"] = core.configure_threads(spec)
        result["torch_build"] = n.torch.__config__.show()
        result["torch_dispatch_linear_cpu"] = n.torch._C._dispatch_dump_table(
            "aten::addmm"
        )
        guard.context()
        guard.boundary("canonical_frozen_loader")
        model, thresholds = core.load_model(q.ROOT, spec["model"])
        channels = spec["frozen_input_provenance"]["channels"]
        if mode == "synthetic":
            inputs = n.families()
        else:
            guard.boundary("before_single_prepared_array_load")
            q.verify_metadata(q.ROOT, spec)
            values = n.load_prepared(
                q.ROOT,
                spec,
                result["audit"],
                persist=lambda: p.write(
                    directory / "access-audit.json", result["audit"]
                ),
            )
            inputs = {"prepared_real": values}
        guard.boundary("inputs_ready")
        for name, values in inputs.items():
            family = {
                "name": name,
                "audit": {
                    "fp32_forward_presentations": 0,
                    "fp64_diagnostic_presentations": 0,
                },
                "status": "started",
            }
            result["families"].append(family)
            tick = time.monotonic()
            n.analyze(model, values, thresholds, channels, guard, family)
            result["stage_wall_seconds"][name] = time.monotonic() - tick
            p.write(directory / "partial.json", result)
        guard.boundary("final_bindings")
        q.verify_metadata(q.ROOT, spec)
        if grant["source_sha256"] != p.source_map():
            raise ValueError("Review source mutation.")
        result["threads_after"] = core.effective_threads()
        guard.context()
        guard.boundary("cleanup")
        result["status"] = "completed"
    except BaseException as exc:
        result.update(
            status="failed", exception_type=type(exc).__name__, error=str(exc)
        )
    finally:
        tick = time.monotonic()
        try:
            if limiter:
                limiter.restore_original_limits()
        except BaseException as exc:
            result.update(status="failed", cleanup_error=str(exc))
        guard.close()
        result["resources"] = guard.report()
        if guard.error:
            result.update(status="failed", guard_error=guard.error)
        result["stage_wall_seconds"]["cleanup"] = time.monotonic() - tick
        result["worker_wall_seconds_including_imports_cleanup"] = (
            time.monotonic() - started
        )
        if result["worker_wall_seconds_including_imports_cleanup"] > 60:
            result.update(status="failed", deadline_error="60s exceeded")
        p.write(directory / "receipt.json", result)
    return 0 if result["status"] == "completed" else 1


def validate_receipt(directory, grant, dispatch):
    receipt = p.read(directory / "receipt.json")
    if (
        receipt.get("task") != "0021"
        or receipt.get("mode") != grant["mode"]
        or receipt.get("reservation_file_sha256")
        != p.file_hash(directory / "reservation.json")
        or receipt.get("source_sha256") != grant["source_sha256"]
        or receipt.get("protocol_canonical_sha256") != q.PROTOCOL_HASH
        or receipt.get("test_background_model_access") is not False
        or receipt.get("test_signal_model_access") is not False
        or receipt.get("audit", {}).get("optimizer_updates") != 0
        or not dispatch["child_reaped"]
        or not dispatch["deadline_passed"]
        or dispatch["parent_error"] is not None
        or dispatch["returncode"] != 0
        or receipt.get("status") != "completed"
        or receipt.get("resources", {}).get("latched_error") is not None
        or receipt.get("resources", {}).get("owned_thread_alive") is not False
    ):
        raise ValueError("Diagnostic incomplete/failed or binding/cleanup invalid.")
    expected_names = (
        ["constants", "powers", "uniform", "normal"]
        if grant["mode"] == "synthetic"
        else ["prepared_real"]
    )
    if [f["name"] for f in receipt["families"]] != expected_names:
        raise ValueError("Incomplete family coverage.")
    for family in receipt["families"]:
        if (
            family["status"] != "completed"
            or [c["batch"] for c in family["windows"]] != [1, 8, 32, 128, 1024]
            or any(
                c["status"] != "completed"
                or c["rows_completed"] != 1024
                or c["windows_completed"] != 1024 // c["batch"]
                for c in family["windows"]
            )
            or family["hashes_before"] != family["hashes_after"]
            or family["reference_hashes_before"] != family["reference_hashes_after"]
        ):
            raise ValueError("Incomplete windows or frozen integrity failed.")
    return receipt


def campaign(*, synthetic=False, root=q.ROOT):
    started = time.monotonic()
    deadline = started + (60 if synthetic else 120)
    owned = False
    directory = None
    workflow = {
        "task": "0021",
        "status": "failed_consumed_no_retry",
        "mode": "synthetic" if synthetic else "real",
    }
    try:
        parent_check(deadline=deadline)
        if sys.platform != "darwin":
            raise ValueError("Supported Darwin primary accounting required.")
        spec = q.load(root)
        metadata = q.verify_metadata(root, spec)
        accepted = None if synthetic else q.verify_acceptance(root)
        parent_check(deadline=deadline)

        def created():
            nonlocal owned
            owned = True

        dispatch_start = time.monotonic()
        directory, grant = reserve(
            root,
            spec,
            accepted,
            dispatch_start,
            synthetic=synthetic,
            on_created=created,
        )
        workflow.update(metadata_verification=metadata, started_utc=p.now())
        environment = dict(os.environ)
        environment.update(spec["runtime"]["thread_environment_before_imports"])
        environment["PYTHONPATH"] = str(root / "src")
        command = [
            sys.executable,
            "-m",
            "latenttrigger.benchmarks.ae_parity_review",
            "--worker",
            grant["token"],
            "--mode",
            grant["mode"],
        ]
        dispatch = supervise(
            command,
            directory / "worker.log",
            root=root,
            environment=environment,
            started=dispatch_start,
            campaign_deadline=deadline,
        )
        workflow["dispatch"] = dispatch
        receipt = validate_receipt(directory, grant, dispatch)
        workflow.update(
            status="completed_consumed_no_retry",
            receipt_file_sha256=p.file_hash(directory / "receipt.json"),
            families_completed=len(receipt["families"]),
        )
        if not synthetic:
            q.verify_acceptance(root, campaign=True)
            q.verify_metadata(root, spec)
        parent_check(deadline=deadline)
    except BaseException as exc:
        workflow.update(exception_type=type(exc).__name__, error=str(exc))
        if directory and (directory / "receipt.json").exists():
            workflow["receipt_file_sha256"] = p.file_hash(directory / "receipt.json")
    finally:
        workflow["whole_review_wall_seconds"] = time.monotonic() - started
        try:
            workflow["parent_peak_rss_bytes"] = parent_check()
        except BaseException as exc:
            import resource

            raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            workflow["parent_peak_rss_bytes"] = (
                raw if sys.platform == "darwin" else raw * 1024
            )
            workflow.update(
                status="failed_consumed_no_retry", parent_accounting_error=str(exc)
            )
        if workflow["whole_review_wall_seconds"] > (60 if synthetic else 120):
            workflow.update(
                status="failed_consumed_no_retry",
                error="Whole review deadline exceeded",
            )
        if owned:
            # Ownership is acquired immediately after mkdir; failed reservation
            # creation remains consumed, and a competing loser never writes here.
            directory = root / (q.SYNTHETIC if synthetic else q.OUTPUT)
            p.write(directory / "workflow.json", workflow)
    print(
        workflow["status"] if owned else "blocked_before_reservation",
        workflow.get("error", ""),
    )
    return 0 if workflow["status"] == "completed_consumed_no_retry" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--synthetic-study", action="store_true")
    action.add_argument("--run-review", action="store_true")
    action.add_argument("--validate-prerequisites", action="store_true")
    action.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--mode", choices=("synthetic", "real"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.worker, args.mode)
    if args.mode:
        parser.error("mode requires owned worker grant")
    if args.validate_prerequisites:
        parent_check()
        spec = q.load()
        q.verify_metadata(q.ROOT, spec)
        q.verify_acceptance()
        if (q.ROOT / q.OUTPUT).exists():
            raise ValueError("Diagnostic already reserved/consumed; no retry.")
        print("Review prerequisites verified; no numerical array opened.")
        return 0
    return campaign(synthetic=args.synthetic_study)


if __name__ == "__main__":
    raise SystemExit(main())
