"""Fresh guarded numerical workers; internal phases require parent reservations."""

import argparse
import os
import sys
import time

from raregate.benchmarks import protocol as p
from raregate.benchmarks.guard import Guard


def verify_phase(phase, token, root=p.ROOT):
    if phase not in p.PHASES:
        raise ValueError("Unsupported phase.")
    directory = root / p.OUTPUT
    reservation = p.read(directory / "reservation.json")
    grant = p.read(directory / f"{phase}-reservation.json")
    specification = p.load(root)
    accepted = p.verify_acceptance(root, specification, campaign=True)
    frozen = p.verify_frozen(root, specification)
    if (
        grant["phase"] != phase
        or grant["token"] != token
        or grant["parent_pid"] != os.getppid()
        or reservation["parent_pid"] != os.getppid()
        or grant["reservation_file_sha256"]
        != p.file_hash(directory / "reservation.json")
        or reservation["source_sha256"] != accepted["source_sha256"]
        or reservation["acceptance_file_sha256"]
        != p.file_hash(directory / "acceptance.json")
        or reservation["protocol_canonical_sha256"] != p.PROTOCOL_HASH
        or p.digest(p.read(directory / "protocol.json")) != p.PROTOCOL_HASH
        or reservation["frozen_metadata"] != frozen
        or not reservation["started_monotonic"]
        <= grant["started_monotonic"]
        <= time.monotonic()
        or directory.resolve() != directory.absolute()
        or (directory / phase / "receipt.json").exists()
    ):
        raise ValueError("Foreign/stale/duplicate worker source/artifact/parent grant.")
    expected_previous = p.PHASES[: p.PHASES.index(phase)]
    if list(grant["previous_receipt_sha256"]) != list(expected_previous):
        raise ValueError("Out-of-order phase grant.")
    for previous, value in grant["previous_receipt_sha256"].items():
        path = directory / previous / "receipt.json"
        if p.file_hash(path) != value or p.read(path)["status"] != "completed":
            raise ValueError("Dependent stage has not completed.")
    return grant, reservation, specification


def check_environment(specification):
    if any(
        os.environ.get(k) != v
        for k, v in specification["runtime"][
            "thread_environment_before_imports"
        ].items()
    ):
        raise ValueError("Set all five thread variables before numerical imports.")
    if any(name in sys.modules for name in ("numpy", "torch", "sklearn", "h5py")):
        raise ValueError(
            "Numerical framework imported before worker environment verification."
        )


def timing_worker(core, root, specification, phase, directory, guard, result):
    import torch

    entry = specification["models"][0 if phase.startswith("PCA") else 1]
    guard.boundary("load_prepared_input")
    tick = time.perf_counter()
    values, prepared = core.load_input(root / p.OUTPUT)
    result["timings"]["prepared_input_load_seconds"] = time.perf_counter() - tick
    guard.boundary("load_frozen_model")
    tick = time.perf_counter()
    model, thresholds = core.load_model(root, entry)
    result["timings"]["model_load_seconds"] = time.perf_counter() - tick
    hashes = {
        "input_bytes": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "threshold_bytes": core.array_hash(thresholds),
    }
    result.update(
        model=entry["name"],
        repetition=int(phase[-1]),
        prepared_input=prepared,
        hashes_before=hashes,
    )
    channels = specification["input"]["channels"]
    tick = time.perf_counter()
    windows = {
        batch: core.build_windows(model, values, batch)
        for batch in specification["batch_grid"]
    }
    result["in_memory_audit"]["numerical_forward_input_presentations"] += 5 * 1024
    result["timings"]["window_and_grid_reconstruction_preparation_seconds"] = (
        time.perf_counter() - tick
    )
    for when in ("before", "after"):
        tick = time.perf_counter()
        records = []
        result["numerical"][when] = {"comparisons": records, "status": "started"}
        reference = core.verify_windows(
            model,
            values,
            thresholds,
            channels,
            windows,
            guard,
            records,
            result["in_memory_audit"],
        )
        result["numerical"][when].update(reference, status="passed")
        result["timings"][f"numerical_{when}_seconds"] = time.perf_counter() - tick
        if when == "after":
            break
        guard.boundary("empty_timer_pairs")
        empty = []
        for _ in range(200):
            guard.check()
            start = time.perf_counter_ns()
            empty.append(time.perf_counter_ns() - start)
            guard.check()
        result["empty_timer_pair_nanoseconds"] = empty
        result["empty_timer_distribution_nanoseconds"] = p.distribution(empty)
        with (directory / "timings.jsonl").open("x") as raw, torch.inference_mode():
            for batch, batch_windows in windows.items():
                for scope in specification["scope_order"]:
                    cell = {"model": entry["name"], "worker": phase}
                    result["cells"].append(cell)
                    core.run_cell(
                        model,
                        thresholds,
                        channels,
                        batch_windows,
                        scope,
                        batch,
                        guard,
                        cell,
                        raw,
                    )
    guard.boundary("post_timing_identity_verification")
    result["hashes_after"] = {
        "input_bytes": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "threshold_bytes": core.array_hash(thresholds),
    }
    if result["hashes_after"] != hashes:
        raise ValueError("Frozen input/parameter/threshold mutation.")
    for key in (
        "reference_reconstruction_sha256",
        "reference_scores_sha256",
        "sample_decision_counts",
    ):
        if result["numerical"]["before"][key] != result["numerical"]["after"][key]:
            raise ValueError("Canonical full1024 reference changed after timing.")
    core.load_input(root / p.OUTPUT)  # Recheck bounded persisted bytes as well.


def phase_worker(phase, token, root=p.ROOT):
    phase_directory = root / p.OUTPUT / phase
    raw_grant = p.read(root / p.OUTPUT / f"{phase}-reservation.json")
    if (
        raw_grant.get("phase") != phase
        or raw_grant.get("token") != token
        or raw_grant.get("parent_pid") != os.getppid()
        or (phase_directory / "receipt.json").exists()
    ):
        raise ValueError(
            "Foreign/duplicate invocation refused before any worker writes."
        )
    started = raw_grant["started_monotonic"]
    # Leave two seconds for worker cleanup/receipt and parent termination/reaping.
    guard = None
    limiter = None
    result = {
        "phase": phase,
        "status": "failed",
        "started_utc": p.now(),
        "timings": {},
        "cells": [],
        "numerical": {},
        "in_memory_audit": {"numerical_forward_input_presentations": 0},
        "optimizer_updates": 0,
        "test_background_model_access": False,
        "test_signal_model_access": False,
    }
    result["binding"] = {
        "protocol_canonical_sha256": p.PROTOCOL_HASH,
        "acceptance_file_sha256": p.file_hash(root / p.OUTPUT / "acceptance.json"),
        "grant_file_sha256": p.file_hash(root / p.OUTPUT / f"{phase}-reservation.json"),
    }
    audit = {
        "optimizer_updates": 0,
        "test_background_model_access": False,
        "test_signal_model_access": False,
    }
    try:
        guard = Guard(started + 58, directory=phase_directory)
        with guard:
            grant, reservation, specification = verify_phase(phase, token, root)
            p.write(
                phase_directory / "bootstrap.json",
                {
                    "phase": phase,
                    "parent_pid": os.getppid(),
                    "grant_file_sha256": p.file_hash(
                        root / p.OUTPUT / f"{phase}-reservation.json"
                    ),
                    "real_population_requests_so_far": 0,
                },
                exclusive=True,
            )
            check_environment(specification)
            result["binding"] = {
                "protocol_canonical_sha256": p.PROTOCOL_HASH,
                "acceptance_file_sha256": reservation["acceptance_file_sha256"],
                "grant_file_sha256": p.file_hash(
                    root / p.OUTPUT / f"{phase}-reservation.json"
                ),
            }
            guard.boundary("numerical_imports")
            tick = time.perf_counter()
            from raregate.benchmarks import core

            result["timings"]["numerical_import_seconds"] = time.perf_counter() - tick
            guard.boundary("effective_thread_enforcement")
            tick = time.perf_counter()
            limiter, result["threads_before"] = core.configure_threads(specification)
            result["timings"]["thread_enforcement_seconds"] = time.perf_counter() - tick
            result["runtime_versions"] = p.runtime_versions()
            guard.boundary("worker_start_context")
            guard.context()
            verify_phase(phase, token, root)  # Fresh binding again before any data.
            if phase == "prepare":
                record, timings = core.prepare_input(
                    root, specification, phase_directory, guard, audit
                )
                result.update(prepared_input=record, access_audit=audit)
                result["timings"].update(timings)
            else:
                timing_worker(
                    core, root, specification, phase, phase_directory, guard, result
                )
            result["threads_after"] = core.effective_threads()
            p.verify_frozen(root, specification)
            p.verify_acceptance(root, specification, campaign=True)
            guard.boundary("worker_end_context")
            guard.context()
            result["status"] = "completed"
    except BaseException as exc:
        result.update(
            status="failed", error=str(exc), exception_type=type(exc).__name__
        )
        if hasattr(exc, "evidence"):
            result["failed_numerical_values"] = exc.evidence
    finally:
        tick = time.perf_counter()
        if limiter:
            limiter.restore_original_limits()
        if guard:
            guard.close()
            result["resources"] = guard.report()
            if guard.error or result["resources"]["owned_thread_alive"]:
                result.update(status="failed", guard_error=guard.error)
        result["timings"]["final_cleanup_seconds"] = time.perf_counter() - tick
        result.update(
            finished_utc=p.now(),
            elapsed_seconds_including_imports_cleanup=time.monotonic() - started,
        )
        if result["elapsed_seconds_including_imports_cleanup"] > 60:
            result.update(status="failed", error="Whole worker60s budget exceeded.")
        if audit.get("custody") or audit.get("population"):
            result["access_audit"] = audit
        if phase_directory.is_dir():
            p.write(phase_directory / "receipt.json", result, exclusive=True)
    return 0 if result["status"] == "completed" else 1


def synthetic_footprint():
    """Data-free real-process startup/operation validation; never a real slot."""
    started = time.monotonic()
    specification = p.load()
    check_environment(specification)
    result = {
        "status": "failed",
        "synthetic_only": True,
        "optimizer_updates": 0,
        "source_sha256": p.source_map(),
        "real_population_requests": 0,
    }
    guard = limiter = None
    try:
        guard = Guard(started + 58)
        with guard:
            from raregate.benchmarks import core

            limiter, threads = core.configure_threads(specification)
            core.torch.manual_seed(1729)
            ae = core.CompactAutoencoder().eval()
            pca = core.PCAReconstruction(
                core.np.zeros(8),
                core.np.eye(8),
                core.np.ones(8),
                core.np.full(8, 0.125),
                6,
                0.95,
                1024,
            )
            values = core.np.linspace(-1, 1, 8192, dtype=core.np.float32).reshape(
                1024, 8
            )
            thresholds = core.np.array([0.1, 0.5, 1, 4], dtype=core.np.float64)
            for model in (pca, ae):
                windows = {
                    b: core.build_windows(model, values, b)
                    for b in specification["batch_grid"]
                }
                core.verify_windows(
                    model,
                    values,
                    thresholds,
                    specification["input"]["channels"],
                    windows,
                    guard,
                    [],
                    {"numerical_forward_input_presentations": 0},
                )
                with core.torch.inference_mode():
                    for batch, batch_windows in windows.items():
                        for scope in specification["scope_order"]:
                            core.run_cell(
                                model,
                                thresholds,
                                specification["input"]["channels"],
                                batch_windows,
                                scope,
                                batch,
                                guard,
                                {},
                                None,
                                warmups=1,
                                measurements=2,
                            )
            result.update(
                status="passed",
                effective_threads_verified=True,
                threads=threads,
                runtime_versions=p.runtime_versions(),
            )
    except BaseException as exc:
        result.update(error=str(exc), exception_type=type(exc).__name__)
        if hasattr(exc, "evidence"):
            result["failed_numerical_values"] = exc.evidence
    finally:
        if limiter:
            limiter.restore_original_limits()
        if guard:
            guard.close()
            result.update(guard.report())
            if guard.error:
                result["status"] = "failed"
        result["elapsed_seconds"] = time.monotonic() - started
    print(__import__("json").dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-footprint", action="store_true")
    parser.add_argument("--phase", choices=p.PHASES)
    parser.add_argument("--token")
    args = parser.parse_args()
    if args.synthetic_footprint:
        if args.phase or args.token:
            parser.error("Synthetic validation cannot request a real phase.")
        return synthetic_footprint()
    if not args.phase or not args.token:
        parser.error("Internal real phases require an actual parent grant/token.")
    return phase_worker(args.phase, args.token)


if __name__ == "__main__":
    sys.exit(main())
