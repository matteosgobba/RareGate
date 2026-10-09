"""Fresh guarded Task0023 availability, device proof, preparation or timing worker."""

import argparse
import os
import shutil
import sys
import time

from latenttrigger.benchmarks import cpu_mps_protocol as q
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.cpu_mps_device import DeviceAccounting, DeviceGuard


def bindings(phase, token, root=q.ROOT):
    proof = phase in ("availability", "synthetic")
    output = q.fixed(root, q.PROOF if proof else q.OUTPUT)
    directory = output / phase
    spec = q.load(root)
    grant = p.read(output / f"{phase}-reservation.json")
    reservation = p.read(output / "reservation.json")
    if (
        phase not in (*q.PHASES, "availability", "synthetic")
        or grant.get("phase") != phase
        or grant.get("token") != token
        or grant.get("parent_pid") != os.getppid()
        or reservation.get("parent_pid") != os.getppid()
        or reservation.get("source_sha256") != p.source_map(root)
        or reservation.get("protocol_canonical_sha256") != q.HASH
        or grant.get("reservation_file_sha256")
        != p.file_hash(output / "reservation.json")
        or (directory / "receipt.json").exists()
    ):
        raise ValueError("Foreign/duplicate source/parent/phase/token grant.")
    seconds = 30 if phase == "availability" else 60
    if (
        not reservation["started_monotonic"]
        <= grant["started_monotonic"]
        <= time.monotonic()
        < grant["started_monotonic"] + seconds - 2
    ):
        raise ValueError("Expired current dispatch/cleanup slack.")
    expected = (
        (() if phase == "availability" else ("availability",))
        if proof
        else q.PHASES[: q.PHASES.index(phase)]
    )
    if list(grant["previous_receipt_sha256"]) != list(expected):
        raise ValueError("Out-of-order/incomplete predecessor grants.")
    for name, digest in grant["previous_receipt_sha256"].items():
        path = output / name / "receipt.json"
        if p.file_hash(path) != digest or p.read(path)["status"] != "completed":
            raise ValueError("Failed/foreign predecessor receipt.")
    q.verify_environment(spec)
    q.software_acceptance(root)
    if not proof:
        execution = p.read(output / "execution-acceptance.json")
        if (
            execution["parent_pid"] != os.getppid()
            or execution["source_sha256"] != p.source_map(root)
            or execution["protocol_canonical_sha256"] != q.HASH
            or execution["status"] != "device_proven"
            or execution["proof_orchestration_seconds"] > 120
        ):
            raise ValueError("Current complete device proof/source required.")
        for name, digest in execution["device_receipt_sha256"].items():
            if p.file_hash(root / q.PROOF / name / "receipt.json") != digest:
                raise ValueError("Device proof receipt changed.")
        if grant["execution_acceptance_sha256"] != p.file_hash(
            output / "execution-acceptance.json"
        ):
            raise ValueError("Current execution acceptance changed.")
    return output, directory, spec, grant, reservation


def audit():
    return dict(
        original_array_reads_attempted=0,
        original_array_reads_completed=0,
        local_array_reads_attempted=0,
        local_array_reads_completed=0,
        rows_loaded=0,
        population_requests=0,
        store_custody_requests=0,
        optimizer_updates=0,
        numerical_forward_input_presentations=0,
        diagnostic_fp64_full_forward_presentations=0,
        diagnostic_fp64_local_affine_row_presentations=0,
        warmup_input_presentations=0,
        measurement_input_presentations=0,
        warmup_forward_input_presentations=0,
        measurement_forward_input_presentations=0,
    )


def verify_hashes(core, cpu_model, model, values, thresholds):
    return dict(
        input=core.array_hash(values),
        CPU_parameters=core.parameter_hash(cpu_model),
        device_parameters=core.parameter_hash(model),
        thresholds=core.array_hash(thresholds),
    )


def timing(core, n, root, spec, phase, directory, guard, result):
    import torch

    device = "mps" if phase.startswith("MPS") else "cpu"
    result.update(device=device, repetition=int(phase[-1]))
    tick = time.monotonic()
    guard.boundary("campaign_local_array_once")
    values = n.read_array(
        root,
        spec,
        result["access_audit"],
        local=True,
        persist=lambda: p.write(
            directory / "access-audit.json", result["access_audit"]
        ),
    )
    result["timings"]["input_loading_seconds"] = time.monotonic() - tick
    tick = time.monotonic()
    guard.boundary("canonical_frozen_model_and_device_initialization")
    cpu_model, thresholds = core.load_model(root, spec["model"])
    model = n.transferred_model(cpu_model, device)
    result["timings"]["model_loading_and_device_initialization_seconds"] = (
        time.monotonic() - tick
    )
    before = verify_hashes(core, cpu_model, model, values, thresholds)
    result["hashes_before"] = before
    tick = time.monotonic()
    windows = {
        b: n.build_windows(model, values, b, device, result["access_audit"])
        for b in spec["batch_grid"]
    }
    result["timings"]["window_and_device_preparation_seconds"] = time.monotonic() - tick
    for when in ("before", "after"):
        tick = time.monotonic()
        result["numerical"][when] = n.verify(
            cpu_model,
            model,
            values,
            thresholds,
            spec["input"]["channels"],
            windows,
            device,
            guard,
            result["access_audit"],
        )
        result["timings"]["numerical_" + when + "_seconds"] = time.monotonic() - tick
        if when == "after":
            break
        if any(m._forward_hooks for m in model.modules()):
            raise ValueError("Diagnostic hooks retained before timing.")
        empty = []
        guard.boundary("empty_timer_context")
        for _ in range(200):
            guard.check()
            start = time.perf_counter_ns()
            empty.append(time.perf_counter_ns() - start)
            guard.check()
        result["empty_timer_pairs_nanoseconds"] = empty
        result["empty_timer_distribution_nanoseconds"] = p.distribution(empty)
        with (directory / "timings.jsonl").open("x") as raw:
            with torch.inference_mode():
                for batch, items in windows.items():
                    for scope in spec["scope_order"]:
                        cell = dict(worker=phase)
                        result["cells"].append(cell)
                        n.run_cell(
                            model,
                            thresholds,
                            spec["input"]["channels"],
                            items,
                            scope,
                            batch,
                            device,
                            guard,
                            cell,
                            raw,
                            result["access_audit"],
                        )
                        p.write(directory / "partial.json", result)
    result["hashes_after"] = verify_hashes(core, cpu_model, model, values, thresholds)
    if (
        before != result["hashes_after"]
        or result["numerical"]["before"] != result["numerical"]["after"]
    ):
        raise ValueError(
            "Pre/post frozen reference/parameter/diagnostic identity changed."
        )
    guard.boundary("owned_tensor_model_release")
    del windows, model, cpu_model, thresholds, values
    n.synchronize(device)
    guard.check()


def run(phase, token, root=q.ROOT):
    started = time.monotonic()
    result = dict(
        task="0023",
        phase=phase,
        status="failed",
        source_sha256=p.source_map(root),
        protocol_canonical_sha256=q.HASH,
        cells=[],
        numerical={},
        timings={},
        access_audit=audit(),
        optimizer_updates=0,
        test_background_model_access=False,
        test_signal_model_access=False,
    )
    directory = (
        root / (q.PROOF if phase in ("availability", "synthetic") else q.OUTPUT) / phase
    )
    guard = limiter = None
    accounting = DeviceAccounting()
    if phase in ("availability", "synthetic"):
        accounting.status = "unverified"
    try:
        _, directory, spec, grant, _ = bindings(phase, token, root)
        seconds = 30 if phase == "availability" else 60
        guard = DeviceGuard(
            grant["started_monotonic"] + seconds - 2,
            directory=directory,
            accounting=accounting,
            journal_limit=16777216,
        )
        guard.__enter__()
        guard.context()
        guard.boundary("frozen_metadata_before_import")
        q.metadata(root, spec)
        tick = time.monotonic()
        import torch

        from latenttrigger.benchmarks import core
        from latenttrigger.benchmarks import cpu_mps_numerics as n
        from latenttrigger.benchmarks.cpu_mps_device import (
            availability,
            require_available,
            tiny_proof,
        )

        result["timings"]["numerical_import_seconds"] = time.monotonic() - tick
        guard.boundary("thread_enforcement_and_device_prerequisites")
        limiter, result["effective_threads"] = core.configure_threads(spec)
        result["availability"] = availability(torch, spec)
        if not result["availability"]["is_available"]:
            accounting.status = "unavailable_not_sampled"
            result["status"] = "blocked_unavailable"
            require_available(result["availability"])
        if phase == "availability":
            result["constant_device_proof"] = tiny_proof(torch, accounting, guard)
        elif phase == "synthetic":
            accounting.enable(torch.mps)
            guard.boundary("small_frozen_artifact_and_fixed_synthetic_only")
            cpu_model, thresholds = core.load_model(root, spec["model"])
            model = n.transferred_model(cpu_model, "mps")
            from latenttrigger.benchmarks.ae_parity_numerics import families

            result["families"] = []
            for name, values in families().items():
                guard.boundary("fixed_synthetic_" + name)
                windows = {
                    b: n.build_windows(model, values, b, "mps", result["access_audit"])
                    for b in spec["batch_grid"]
                }
                before = n.verify(
                    cpu_model,
                    model,
                    values,
                    thresholds,
                    spec["input"]["channels"],
                    windows,
                    "mps",
                    guard,
                    result["access_audit"],
                )
                after = n.verify(
                    cpu_model,
                    model,
                    values,
                    thresholds,
                    spec["input"]["channels"],
                    windows,
                    "mps",
                    guard,
                    result["access_audit"],
                )
                if before != after:
                    raise ValueError(
                        "Synthetic device/CPU reference repeatability failed."
                    )
                result["families"].append(
                    dict(name=name, status="passed", before=before, after=after)
                )
                p.write(directory / "partial.json", result)
                del windows, values
            del model, cpu_model, thresholds
            torch.mps.synchronize()
        elif phase == "prepare":
            tick = time.monotonic()
            guard.boundary("original_prepared_array_once")
            values = n.read_array(
                root,
                spec,
                result["access_audit"],
                persist=lambda: p.write(
                    directory / "access-audit.json", result["access_audit"]
                ),
            )
            source, _ = q.input_file(root, spec)
            with (
                (directory / "input.npy").open("xb") as target,
                source.open("rb") as original,
            ):
                shutil.copyfileobj(original, target, length=32896)
            q.input_file(root, spec, local=True)
            result["prepared_payload_sha256"] = core.array_hash(values)
            result["timings"]["loading_and_byte_identical_copy_seconds"] = (
                time.monotonic() - tick
            )
            del values
        else:
            if phase.startswith("MPS"):
                accounting.enable(torch.mps)
            timing(core, n, root, spec, phase, directory, guard, result)
        guard.boundary("post_work_source_thread_and_context_checks")
        result["effective_threads_after"] = core.effective_threads()
        if result["effective_threads"] != result["effective_threads_after"] or result[
            "source_sha256"
        ] != p.source_map(root):
            raise ValueError("Source/effective runtime mutated.")
        q.metadata(root, spec)
        guard.context()
        result["status"] = "completed"
    except BaseException as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["failed_values"] = getattr(exc, "evidence", None)
    finally:
        tick = time.monotonic()
        # Drop owned references without manipulating global caches or allocator policy.
        model = windows = cpu_model = values = thresholds = None
        if accounting.status == "active":
            try:
                import torch

                torch.mps.synchronize()
            except BaseException as exc:
                result.update(status="failed", cleanup_synchronization_error=str(exc))
        if limiter:
            try:
                limiter.restore_original_limits()
            except BaseException as exc:
                result.update(status="failed", cleanup_error=str(exc))
        if guard:
            guard.close()
            result["resources"] = guard.report()
            if guard.error:
                result["status"] = "failed"
        result["device_resources"] = accounting.report()
        result["timings"]["cleanup_seconds"] = time.monotonic() - tick
        result["elapsed_seconds_including_imports_cleanup"] = time.monotonic() - started
        if directory.exists():
            p.write(directory / "receipt.json", result, exclusive=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", choices=(*q.PHASES, "availability", "synthetic"), required=True
    )
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    result = run(args.phase, args.token)
    print(f"{args.phase}: {result['status']}")
    return 0 if result["status"] == "completed" else 2


if __name__ == "__main__":
    sys.exit(main())
