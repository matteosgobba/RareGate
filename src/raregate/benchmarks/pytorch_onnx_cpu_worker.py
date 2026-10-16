"""Fresh source-bound Task0025 preparation or one designated runtime worker."""

import argparse
import os
import shutil
import time

from raregate.benchmarks import protocol as p
from raregate.benchmarks import pytorch_onnx_cpu_protocol as q
from raregate.benchmarks.guard import Guard
from raregate.exports import onnx_protocol as old
from raregate.exports.onnx_worker import counts


def bindings(root, phase, token):
    old.refuse_early_imports()
    spec = q.load(root)
    output = q.fixed(root, q.OUTPUT)
    reservation = p.read(output / "reservation.json")
    grant = p.read(output / (phase + "-reservation.json"))
    if (
        phase not in q.PHASES
        or grant["phase"] != phase
        or grant["token"] != token
        or grant["parent_pid"] != os.getppid()
        or reservation["parent_pid"] != os.getppid()
        or reservation["source_file_sha256"] != q.source_map(root)
        or reservation["protocol_canonical_JSON_sha256"] != q.HASH
        or p.digest(p.read(output / "protocol.json")) != q.HASH
        or grant["reservation_file_sha256"] != p.file_hash(output / "reservation.json")
        or p.file_hash(output / "acceptance.json")
        != reservation["acceptance_file_byte_sha256"]
        or (output / phase / "receipt.json").exists()
        or not reservation["started_monotonic"]
        <= grant["started_monotonic"]
        <= time.monotonic()
        < grant["started_monotonic"] + 58
        or list(grant["previous_receipt_sha256"])
        != list(q.PHASES[: q.PHASES.index(phase)])
    ):
        raise ValueError(
            "Foreign/stale/duplicate/out-of-order parent/source/acceptance grant."
        )
    for name, digest in grant["previous_receipt_sha256"].items():
        path = output / name / "receipt.json"
        if p.file_hash(path) != digest or p.read(path)["status"] != "completed":
            raise ValueError("Failed/changed predecessor.")
    if any(
        os.environ.get(k) != v
        for k, v in spec["runtime"]["thread_environment_before_imports"].items()
    ):
        raise ValueError("Thread environment must precede numerical imports.")
    q.acceptance(root)
    q.metadata(root, spec)
    return spec, grant, reservation


def execute(phase, token, root=q.ROOT):
    output = q.fixed(root, q.OUTPUT)
    directory = output / phase
    grant = p.read(output / (phase + "-reservation.json"))
    if (
        grant.get("token") != token
        or grant.get("parent_pid") != os.getppid()
        or (directory / "receipt.json").exists()
    ):
        raise ValueError("Foreign worker before owned writes.")
    started = grant["started_monotonic"]
    result = dict(
        task="0025",
        phase=phase,
        status="failed",
        cells=[],
        numerical={},
        synthetic=[],
        counts=counts(),
        prepared_counts=dict(
            prepared_forward_row_presentations=0,
            prepared_reference_row_presentations=0,
            prepared_verification_forward_row_presentations=0,
        ),
        access=dict(
            original_array_read_attempts=0,
            original_array_reads_completed=0,
            local_array_read_attempts=0,
            local_array_reads_completed=0,
            unique_reused_rows=0,
            population_requests=0,
            store_custody_requests=0,
        ),
        timings={},
        optimizer_updates=0,
        test_background_model_access=False,
        test_signal_model_access=False,
    )
    guard = limiter = runtime = diagnostic = None
    model = windows = values = None

    def partial():
        p.write(directory / "partial.json", result)

    def access():
        p.write(directory / "access.json", result["access"])

    def stage(name, function):
        guard.boundary(name)
        tick = time.monotonic()
        try:
            return function()
        finally:
            result["timings"][name + "_seconds"] = time.monotonic() - tick
            partial()

    try:
        guard = Guard(started + 58, directory=directory, journal_limit=16777216)
        guard.__enter__()
        spec, grant, reservation = bindings(root, phase, token)
        result.update(
            source_file_sha256=reservation["source_file_sha256"],
            protocol_canonical_JSON_sha256=q.HASH,
            binding=dict(
                grant_file_sha256=p.file_hash(output / (phase + "-reservation.json")),
                reservation_file_sha256=p.file_hash(output / "reservation.json"),
            ),
        )
        tick = time.monotonic()
        from raregate.benchmarks import core
        from raregate.benchmarks import pytorch_onnx_cpu_numerics as n
        from raregate.benchmarks.ae_parity_numerics import families
        from raregate.exports import onnx_graph as graph
        from raregate.exports import onnx_numerics as numerical

        graph.optional_modules()
        result["timings"]["numerical_imports_seconds"] = time.monotonic() - tick
        limiter, result["effective_threads_before"] = stage(
            "thread_enforcement", lambda: core.configure_threads(spec)
        )
        q.check_build(core.torch.__config__.show(), spec["builds"]["torch"])
        q.check_build(
            graph.optional_modules()["onnxruntime"].get_build_info(),
            spec["builds"]["ORT"],
        )
        result["runtime_versions"] = p.runtime_versions()
        result["optional_versions"] = old.check_dependencies(root, old.load(root))
        guard.context()
        model, thresholds = stage(
            "model_loading", lambda: core.load_model(root, spec["model"])
        )
        channels = spec["input"]["channels"]

        def sessions():
            on = graph.optional_modules()["onnx"]
            document = on.load(
                root / spec["graphs"]["reconstruction"]["path"],
                load_external_data=False,
            )
            manifest, _ = graph.audit_graph(document, model)
            if p.digest(manifest) != p.digest(
                p.read(
                    root / "results/benchmarks/task0024-ae-onnx-cpu/graph-manifest.json"
                )
            ):
                raise ValueError("Accepted graph/initializer manifest drift.")
            primary = graph.RuntimeAdapter(
                root / spec["graphs"]["reconstruction"]["path"], feature_names=channels
            )
            try:
                diag = graph.RuntimeAdapter(
                    root / spec["graphs"]["diagnostic"]["path"],
                    feature_names=channels,
                    diagnostic=True,
                )
            except BaseException:
                primary.close()
                raise
            return primary, diag, manifest

        runtime, diagnostic, manifest = stage("graph_audit_session_loading", sessions)
        result["providers_before"] = [
            n.effective_session(r) for r in (runtime, diagnostic)
        ]
        initial = dict(
            parameters=core.parameter_hash(model),
            thresholds=core.array_hash(thresholds),
        )
        if phase == "prepare":

            def synthetic():
                for name, x in families().items():
                    item = dict(name=name, verification={}, counts=counts())
                    result["synthetic"].append(item)
                    item["verification"] = numerical.verify(
                        model,
                        runtime,
                        diagnostic,
                        manifest,
                        x,
                        thresholds,
                        channels,
                        guard,
                        item["counts"],
                        persist=lambda state, item=item: (
                            item.update(verification=state),
                            partial(),
                        ),
                    )
                    n.admit(item["verification"])

            stage("frozen_four_family_validation", synthetic)
            if len(result["synthetic"]) != 4:
                raise ValueError("Incomplete frozen synthetic admission.")
            result["access"]["synthetic_admitted"] = True

        def load():
            local = phase != "prepare"
            path = q.input_path(root, spec, local=local)
            kind = "local" if local else "original"
            result["access"][kind + "_array_read_attempts"] += 1
            access()
            x = core.np.load(path, allow_pickle=False)
            core.validate_features(x)
            if core.array_hash(x) != spec["input"]["array_bytes_sha256"]:
                raise ValueError("Input payload byte mutation.")
            result["access"].update(
                {kind + "_array_reads_completed": 1, "unique_reused_rows": 1024}
            )
            access()
            return x

        values = stage("input_loading", load)
        if phase == "prepare":

            def copy():
                with (
                    q.input_path(root, spec).open("rb") as src,
                    (directory / "input.npy").open("xb") as dst,
                ):
                    shutil.copyfileobj(src, dst, length=65536)
                q.input_path(root, spec, local=True)
                p.write(
                    directory / "prepared.json",
                    dict(
                        file_byte_sha256=spec["input"]["file_sha256"],
                        payload_byte_sha256=core.array_hash(values),
                        byte_identical_copy=True,
                    ),
                    exclusive=True,
                )

            stage("input_byte_copy", copy)
        else:
            name = "PyTorch" if phase.startswith("PyTorch") else "ORT"
            result.update(runtime_name=name, repetition=int(phase[-1]))
            chosen = model if name == "PyTorch" else runtime
            initial["input"] = core.array_hash(values)
            result["hashes_before"] = initial
            windows = stage(
                "window_preparation",
                lambda: n.prepare_windows(
                    chosen, name, values, channels, result["prepared_counts"], guard
                ),
            )
            for when in ("before", "after"):

                def verify(when=when):
                    result["numerical"][when] = numerical.verify(
                        model,
                        runtime,
                        diagnostic,
                        manifest,
                        values,
                        thresholds,
                        channels,
                        guard,
                        result["counts"],
                        persist=lambda state: (
                            result["numerical"].update({when: state}),
                            partial(),
                        ),
                    )
                    n.admit(result["numerical"][when])
                    result["numerical"][when + "_prepared"] = n.verify_prepared(
                        chosen,
                        dict(cpu=model, name=name),
                        values,
                        windows,
                        channels,
                        thresholds,
                        result["prepared_counts"],
                        guard,
                    )
                    reference = runtime.reconstruct(values, feature_names=channels)
                    scores = runtime.score(values, feature_names=channels)
                    result["counts"]["ORT_forward_input_presentations"] += 2048
                    result["numerical"][when + "_ORT_reference"] = dict(
                        reconstruction=core.array_hash(reference),
                        scores=core.array_hash(scores),
                    )

                stage("numerical_" + when, verify)
                if when == "after":
                    break
                if any(m._forward_hooks for m in model.modules()):
                    raise ValueError("Diagnostic hooks remain during timing.")
                info = time.get_clock_info("perf_counter")
                if not info.monotonic or info.adjustable or not 0 < info.resolution < 1:
                    raise ValueError("Unsupported monotonic timer metadata.")
                result["timer_metadata"] = dict(
                    implementation=info.implementation,
                    monotonic=info.monotonic,
                    adjustable=info.adjustable,
                    resolution_seconds=info.resolution,
                )
                empty = []
                for _ in range(200):
                    guard.check()
                    begin = time.perf_counter_ns()
                    elapsed = time.perf_counter_ns() - begin
                    if elapsed < 0:
                        raise ValueError("Negative empty timer pair.")
                    empty.append(elapsed)
                    guard.check()
                result["empty_timer_pair_nanoseconds"] = empty
                result["empty_timer_distribution_nanoseconds"] = p.distribution(empty)

                def timing():
                    with (
                        (directory / "timings.jsonl").open("x") as raw,
                        core.torch.inference_mode(),
                    ):
                        for batch, items in windows.items():
                            for scope in q.SCOPES:
                                cell = dict(worker=phase, runtime=name)
                                result["cells"].append(cell)
                                n.run_cell(
                                    chosen,
                                    thresholds,
                                    channels,
                                    items,
                                    scope,
                                    batch,
                                    guard,
                                    cell,
                                    raw,
                                )
                                partial()

                stage("scheduled_timing_with_guards", timing)
            result["hashes_after"] = dict(
                parameters=core.parameter_hash(model),
                thresholds=core.array_hash(thresholds),
                input=core.array_hash(values),
            )
            if (
                result["hashes_before"] != result["hashes_after"]
                or result["numerical"]["before_ORT_reference"]
                != result["numerical"]["after_ORT_reference"]
            ):
                raise ValueError(
                    "Frozen input/parameter/threshold/device reference mutation."
                )
            for key in (
                "reference_reconstruction_payload_byte_sha256",
                "reference_scores_payload_byte_sha256",
                "diagnostic_FP64_payload_byte_sha256",
                "envelope_payload_byte_sha256",
            ):
                if (
                    result["numerical"]["before"][key]
                    != result["numerical"]["after"][key]
                ):
                    raise ValueError("Canonical restored reference/envelope drift.")
        guard.boundary("final_bindings")
        if initial["parameters"] != core.parameter_hash(model) or initial[
            "thresholds"
        ] != core.array_hash(thresholds):
            raise ValueError("Frozen model/calibration mutation.")
        q.metadata(root, spec)
        if q.source_map(root) != reservation["source_file_sha256"]:
            raise ValueError("Source changed after admission.")
        result["effective_threads_after"] = core.effective_threads()
        result["providers_after"] = [
            n.effective_session(r) for r in (runtime, diagnostic)
        ]
        if (
            result["effective_threads_before"] != result["effective_threads_after"]
            or result["providers_before"] != result["providers_after"]
        ):
            raise ValueError("Effective runtime drift.")
        guard.context()
        result["status"] = "completed"
    except BaseException as exc:
        result.update(
            error=f"{type(exc).__name__}: {exc}",
            failed_values=getattr(exc, "evidence", None),
        )
    finally:
        tick = time.monotonic()
        try:
            if guard:
                guard.deadline = min(started + 60, tick + 2)
            windows = model = values = None
            if runtime:
                runtime.close()
            if diagnostic:
                diagnostic.close()
            if limiter:
                limiter.restore_original_limits()
        except BaseException as exc:
            result.update(status="failed", cleanup_error=str(exc))
        finally:
            if guard:
                guard.close()
                result["resources"] = guard.report()
                if guard.error:
                    result.update(status="failed", guard_error=guard.error)
        result["timings"]["cleanup_seconds"] = time.monotonic() - tick
        result["worker_wall_seconds"] = time.monotonic() - started
        if result["worker_wall_seconds"] > 60:
            result.update(status="failed", error="60s deadline exceeded")
        access()
        p.write(directory / "receipt.json", result, exclusive=True)
    return 0 if result["status"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=q.PHASES, required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    return execute(args.phase, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
