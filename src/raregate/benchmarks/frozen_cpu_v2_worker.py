"""Fresh v2 workers: source-bound preparation, policy verification and timing."""

import argparse
import os
import shutil
import sys
import time

from raregate.benchmarks import frozen_cpu_v2_protocol as q
from raregate.benchmarks import protocol as p
from raregate.benchmarks.guard import Guard


def bindings(phase, token, root=q.ROOT):
    synthetic = phase == "synthetic"
    output = root / (q.SYNTHETIC if synthetic else q.OUTPUT)
    directory = output if synthetic else output / phase
    reservation = p.read(output / "reservation.json")
    grant = p.read(output / f"{phase}-reservation.json")
    spec = q.load(root)
    if (
        phase not in (*q.PHASES, "synthetic")
        or grant["phase"] != phase
        or grant["token"] != token
        or grant["parent_pid"] != os.getppid()
        or reservation["parent_pid"] != os.getppid()
        or grant["reservation_file_sha256"] != p.file_hash(output / "reservation.json")
        or reservation["protocol_canonical_sha256"] != q.HASH
        or p.digest(p.read(output / "protocol.json")) != q.HASH
        or reservation["source_sha256"] != p.source_map(root)
        or output.resolve() != output.absolute()
        or (directory / "receipt.json").exists()
    ):
        raise ValueError("Foreign/duplicate v2 source/protocol/parent/phase grant.")
    if not synthetic:
        accepted = q.acceptance(root, campaign=True)
        if (
            accepted["source_sha256"] != reservation["source_sha256"]
            or p.file_hash(output / "acceptance.json")
            != reservation["acceptance_file_sha256"]
        ):
            raise ValueError("Acceptance binding changed.")
        previous = q.PHASES[: q.PHASES.index(phase)]
        if list(grant["previous_receipt_sha256"]) != list(previous):
            raise ValueError("Out-of-order worker grant.")
        for name, expected in grant["previous_receipt_sha256"].items():
            path = output / name / "receipt.json"
            if p.file_hash(path) != expected or p.read(path)["status"] != "completed":
                raise ValueError("Failed/incomplete predecessor.")
    q.metadata(root, spec)
    if (
        not reservation["started_monotonic"]
        <= grant["started_monotonic"]
        <= time.monotonic()
        < grant["started_monotonic"] + 58
    ):
        raise ValueError("Stale grant/cleanup slack deadline.")
    if any(
        os.environ.get(k) != v
        for k, v in spec["runtime"]["thread_environment_before_imports"].items()
    ):
        raise ValueError("Thread environment must precede numerical imports.")
    if any(n in sys.modules for n in ("numpy", "torch", "sklearn", "h5py")):
        raise ValueError(
            "Numerical import before worker guard/environment verification."
        )
    return output, directory, grant, reservation, spec


def perform_timing(core, n, root, spec, phase, directory, guard, result):
    guard.boundary("campaign_local_input")
    values = n.load_array(
        root,
        spec,
        result["access_audit"],
        local=True,
        persist=lambda: p.write(
            directory / "access-audit.json", result["access_audit"]
        ),
    )
    entry = spec["models"][0 if phase.startswith("PCA") else 1]
    guard.boundary("frozen_model_load")
    model, thresholds = core.load_model(root, entry)
    result.update(model=entry["name"], repetition=int(phase[-1]))
    before = {
        "input": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "thresholds": core.array_hash(thresholds),
    }
    result["hashes_before"] = before
    guard.boundary("prepare_actual_batch_windows")
    tick = time.monotonic()
    windows = {b: core.build_windows(model, values, b) for b in spec["batch_grid"]}
    result["in_memory_audit"]["numerical_forward_input_presentations"] += 5120
    result["timings"]["window_preparation_seconds"] = time.monotonic() - tick
    for when in ("before", "after"):
        tick = time.monotonic()
        records = []
        result["numerical"][when] = {"status": "started", "comparisons": records}
        reference = n.verify(
            model,
            values,
            thresholds,
            spec["input"]["channels"],
            windows,
            guard,
            records,
            result["in_memory_audit"],
        )
        result["numerical"][when].update(reference, status="passed")
        result["timings"]["numerical_" + when + "_seconds"] = time.monotonic() - tick
        if when == "after":
            break
        if (
            any(m._forward_hooks for m in model.modules())
            if hasattr(model, "modules")
            else False
        ):
            raise ValueError("Diagnostic hooks remain before timing.")
        guard.boundary("empty_timer_context")
        empty = []
        for _ in range(200):
            guard.check()
            start = time.perf_counter_ns()
            empty.append(time.perf_counter_ns() - start)
            guard.check()
        result["empty_timer_pair_nanoseconds"] = empty
        result["empty_timer_distribution_nanoseconds"] = p.distribution(empty)
        with (
            (directory / "timings.jsonl").open("x") as raw,
            core.torch.inference_mode(),
        ):
            for batch, items in windows.items():
                for scope in spec["scope_order"]:
                    cell = {"model": entry["name"], "worker": phase}
                    result["cells"].append(cell)
                    core.run_cell(
                        model,
                        thresholds,
                        spec["input"]["channels"],
                        items,
                        scope,
                        batch,
                        guard,
                        cell,
                        raw,
                    )
    guard.boundary("post_timing_identity_checks")
    after = {
        "input": core.array_hash(values),
        "parameters": core.parameter_hash(model),
        "thresholds": core.array_hash(thresholds),
    }
    result["hashes_after"] = after
    if before != after:
        raise ValueError("Frozen input/parameter/threshold mutation.")
    for key in ("reference_reconstruction_sha256", "reference_scores_sha256"):
        if result["numerical"]["before"][key] != result["numerical"]["after"][key]:
            raise ValueError("Canonical full-reference mutation.")
    if phase.startswith("AE"):
        for key in ("diagnostic_FP64_reference_sha256", "envelope_sha256"):
            if result["numerical"]["before"][key] != result["numerical"]["after"][key]:
                raise ValueError("Diagnostic reference/envelope mutation.")


def perform_synthetic(core, n, root, spec, guard, result):
    from raregate.benchmarks.ae_parity_numerics import families

    result["families"] = []
    for name, values in families().items():
        for entry in spec["models"]:
            guard.boundary("synthetic/" + name + "/" + entry["name"])
            model, thresholds = core.load_model(root, entry)
            before = core.parameter_hash(model)
            windows = {
                b: core.build_windows(model, values, b) for b in spec["batch_grid"]
            }
            audit = {
                "numerical_forward_input_presentations": 5120,
                "diagnostic_fp64_full_forward_presentations": 0,
                "diagnostic_fp64_local_affine_row_presentations": 0,
            }
            family = {
                "name": name,
                "model": entry["name"],
                "input_hash": core.array_hash(values),
                "status": "started",
                "comparisons": [],
                "audit": audit,
            }
            result["families"].append(family)
            family.update(
                n.verify(
                    model,
                    values,
                    thresholds,
                    spec["input"]["channels"],
                    windows,
                    guard,
                    family["comparisons"],
                    audit,
                ),
                status="completed",
            )
            if before != core.parameter_hash(model):
                raise ValueError("Synthetic operational artifact parameter mutation.")


def run(phase, token):
    # Bootstrap prevents foreign writes; parent deadline also covers this read.
    output = q.ROOT / (q.SYNTHETIC if phase == "synthetic" else q.OUTPUT)
    grant = p.read(output / f"{phase}-reservation.json")
    directory = output if phase == "synthetic" else output / phase
    if (
        grant.get("token") != token
        or grant.get("parent_pid") != os.getppid()
        or (directory / "receipt.json").exists()
    ):
        raise ValueError("Foreign/duplicate worker before writes.")
    started = grant["started_monotonic"]
    result = {
        "task": "0022",
        "phase": phase,
        "status": "failed",
        "cells": [],
        "numerical": {},
        "timings": {},
        "in_memory_audit": {
            "numerical_forward_input_presentations": 0,
            "diagnostic_fp64_full_forward_presentations": 0,
            "diagnostic_fp64_local_affine_row_presentations": 0,
        },
        "access_audit": {
            "original_array_read_attempts": 0,
            "original_array_reads_completed": 0,
            "local_array_read_attempts": 0,
            "local_array_reads_completed": 0,
            "population_requests": 0,
            "store_custody_operations": 0,
            "optimizer_updates": 0,
        },
        "optimizer_updates": 0,
        "test_background_model_access": False,
        "test_signal_model_access": False,
        "binding": {
            "protocol_canonical_sha256": q.HASH,
            "grant_file_sha256": p.file_hash(output / f"{phase}-reservation.json"),
            "reservation_file_sha256": p.file_hash(output / "reservation.json"),
        },
    }
    limiter = guard = None
    try:
        guard = Guard(
            started + 58,
            directory=None if phase == "synthetic" else directory,
            journal_limit=16 * 2**20,
        )
        guard.__enter__()
        _, _, _, reservation, spec = bindings(phase, token)
        result["source_sha256"] = reservation["source_sha256"]
        guard.boundary("framework_import")
        tick = time.monotonic()
        from raregate.benchmarks import core
        from raregate.benchmarks import frozen_cpu_v2_numerics as n

        result["timings"]["framework_import_seconds"] = time.monotonic() - tick
        guard.boundary("unchanged_thread_enforcement")
        tick = time.monotonic()
        limiter, result["threads_before"] = core.configure_threads(spec)
        result["timings"]["thread_enforcement_seconds"] = time.monotonic() - tick
        build = core.torch.__config__.show()
        if p.digest(build) != spec["numerical"]["runtime_torch_build_sha256"]:
            raise ValueError("Supported frozen CPU build changed.")
        result.update(torch_build=build, runtime_versions=p.runtime_versions())
        guard.context()
        if phase == "prepare":
            guard.boundary("original_prepared_array_load")
            tick = time.monotonic()
            values = n.load_array(
                q.ROOT,
                spec,
                result["access_audit"],
                persist=lambda: p.write(
                    directory / "access-audit.json", result["access_audit"]
                ),
            )
            result["timings"]["original_array_load_seconds"] = time.monotonic() - tick
            source, _ = q.input_file(q.ROOT, spec)
            with source.open("rb") as src, (directory / "input.npy").open("xb") as dst:
                shutil.copyfileobj(src, dst, length=65536)
            q.input_file(q.ROOT, spec, local=True)
            p.write(
                directory / "prepared.json",
                {
                    "file_sha256": spec["input"]["file_sha256"],
                    "array_bytes_sha256": core.array_hash(values),
                    "shape": [1024, 8],
                    "dtype": "float32",
                    "source_file": spec["input"]["path"],
                    "byte_identical_copy": True,
                },
            )
        elif phase == "synthetic":
            perform_synthetic(core, n, q.ROOT, spec, guard, result)
        else:
            perform_timing(core, n, q.ROOT, spec, phase, directory, guard, result)
        guard.boundary("final_bindings")
        q.metadata(q.ROOT, spec)
        if reservation["source_sha256"] != p.source_map():
            raise ValueError("Frozen source changed during worker.")
        result["threads_after"] = core.effective_threads()
        guard.context()
        guard.boundary("cleanup")
        result["status"] = "completed"
    except BaseException as exc:
        result.update(
            status="failed", error=str(exc), exception_type=type(exc).__name__
        )
        if hasattr(exc, "evidence"):
            result["failed_numerical_values"] = exc.evidence
    finally:
        tick = time.monotonic()
        try:
            if limiter:
                limiter.restore_original_limits()
        except BaseException as exc:
            result.update(status="failed", cleanup_error=str(exc))
        if guard:
            guard.close()
            result["resources"] = guard.report()
            if guard.error:
                result.update(status="failed", guard_error=guard.error)
        result["timings"]["cleanup_seconds"] = time.monotonic() - tick
        result["elapsed_seconds_including_imports_cleanup"] = time.monotonic() - started
        if result["elapsed_seconds_including_imports_cleanup"] > 60:
            result.update(status="failed", error="60sworker budget exceeded")
        p.write(directory / "access-audit.json", result["access_audit"])
        p.write(directory / "receipt.json", result)
    return 0 if result["status"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=(*q.PHASES, "synthetic"), required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    return run(args.phase, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
