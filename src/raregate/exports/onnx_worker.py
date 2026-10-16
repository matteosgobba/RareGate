"""Fresh guarded frozen export, synthetic acceptance and one prepared-array read."""

import argparse
import hashlib
import os
import sys
import time

from raregate.benchmarks import protocol as p
from raregate.benchmarks.guard import Guard
from raregate.exports import onnx_protocol as q


def bindings(token, root=q.ROOT):
    q.refuse_early_imports()
    directory = q.fixed(root, q.OUTPUT)
    reservation = p.read(directory / "reservation.json")
    grant = p.read(directory / "worker-grant.json")
    spec = q.load(root)
    if (
        grant["token"] != token
        or grant["parent_pid"] != os.getppid()
        or reservation["parent_pid"] != os.getppid()
        or reservation["source_file_sha256"] != q.source_map(root)
        or reservation["protocol_canonical_JSON_sha256"] != q.HASH
        or p.digest(p.read(directory / "protocol.json")) != q.HASH
        or grant["reservation_file_byte_sha256"]
        != p.file_hash(directory / "reservation.json")
        or p.file_hash(directory / "acceptance.json")
        != reservation["acceptance_file_byte_sha256"]
        or (directory / "receipt.json").exists()
        or not reservation["started_monotonic"]
        <= grant["started_monotonic"]
        <= time.monotonic()
        < grant["whole_deadline_monotonic"]
    ):
        raise ValueError("Foreign/stale/source/parent/duplicate grant or acceptance.")
    q.acceptance(root)
    q.check_dependencies(root, spec)
    if any(
        os.environ.get(k) != v
        for k, v in spec["runtime"]["thread_environment_before_imports"].items()
    ):
        raise ValueError("Thread environment must precede numerical imports.")
    return directory, grant, spec


def counts():
    return dict(
        numerical_forward_input_presentations=0,
        diagnostic_fp64_full_forward_presentations=0,
        diagnostic_fp64_local_affine_row_presentations=0,
        ORT_forward_input_presentations=0,
        ORT_diagnostic_input_presentations=0,
    )


def open_real(root, spec, access, persist=lambda: None):
    if access["array_read_attempts"] or access.get("synthetic_admitted") is not True:
        raise ValueError(
            "One real numerical read only after full frozen synthetic admission."
        )
    path, _ = q.input_file(root, spec)
    access["array_read_attempts"] = 1
    persist()
    import numpy as np

    from raregate.benchmarks import core

    values = np.load(path, allow_pickle=False)
    core.validate_features(values)
    if core.array_hash(values) != spec["input"]["array_bytes_sha256"]:
        raise ValueError("Frozen input payload byte identity mismatch.")
    access.update(array_reads_completed=1, unique_reused_rows=1024)
    persist()
    return values


def execute(token, root=q.ROOT):
    started = time.monotonic()
    directory = root / q.OUTPUT
    guard = limiter = runtime = diagnostic = None
    stages = {}
    current = None
    result = dict(
        task="0024",
        status="failed",
        source_file_sha256=q.source_map(root),
        protocol_canonical_JSON_sha256=q.HASH,
        stages=stages,
        synthetic=[],
        real={},
        counts=counts(),
        access=dict(
            array_read_attempts=0,
            array_reads_completed=0,
            unique_reused_rows=0,
            population_requests=0,
            store_custody_requests=0,
            synthetic_admitted=False,
        ),
        optimizer_updates=0,
        performance_timer_invocations=0,
        test_background_model_access=False,
        test_signal_model_access=False,
    )

    def partial():
        p.write(directory / "partial.json", result)

    def access():
        p.write(directory / "access.json", result["access"])

    def phase(name, limit):
        nonlocal current
        now = time.monotonic()
        if current is not None:
            stages[current]["elapsed_seconds"] = (
                now - stages[current]["started_monotonic"]
            )
        current = name
        stages[name] = dict(
            started_monotonic=now, limit_seconds=limit, status="started"
        )
        guard.deadline = min(whole_deadline, now + limit)
        p.write(
            directory / "phase.json",
            dict(name=name, started_monotonic=now, token=token),
        )
        guard.boundary(name)
        partial()

    try:
        directory, grant, spec = bindings(token, root)
        whole_deadline = grant["whole_deadline_monotonic"]
        guard = Guard(
            min(whole_deadline, grant["started_monotonic"] + 28),
            directory=directory,
            journal_limit=16777216,
        )
        guard.__enter__()
        guard.context()
        import_tick = time.monotonic()
        from raregate.benchmarks import core
        from raregate.benchmarks.ae_parity_numerics import families
        from raregate.exports import onnx_graph as graph
        from raregate.exports import onnx_numerics as numerical

        graph.optional_modules()
        result["import_seconds"] = time.monotonic() - import_tick
        limiter, result["effective_threads_before"] = core.configure_threads(spec)
        import torch

        build = torch.__config__.show()
        if (
            p.digest(build)
            != spec["runtime"]["torch_build_canonical_JSON_string_sha256"]
            or hashlib.sha256(build.encode()).hexdigest()
            != spec["runtime"]["torch_build_raw_UTF8_byte_sha256"]
        ):
            raise ValueError("Pinned CPU build hash-kind contract failed.")
        result["runtime"] = dict(
            core_versions=p.runtime_versions(),
            optional_versions=q.check_dependencies(root, spec),
            torch_build_canonical_JSON_string_sha256=p.digest(build),
            torch_build_raw_UTF8_byte_sha256=hashlib.sha256(build.encode()).hexdigest(),
        )
        q.frozen_metadata(root, spec)
        phase("export", 30)
        model, thresholds = core.load_model(root, spec["model"])
        channels = spec["input"]["channels"]
        initial_parameter_hash = core.parameter_hash(model)
        initial_threshold_hash = core.array_hash(thresholds)
        path = directory / "reconstruction.onnx"
        result["export"] = graph.export_reconstruction(model, path)
        document = graph.optional_modules()["onnx"].load(path, load_external_data=False)
        manifest, inferred = graph.audit_graph(document, model)
        result["graph_manifest"] = manifest
        p.write(directory / "graph-manifest.json", manifest, exclusive=True)
        graph.diagnostic_copy(inferred, manifest, directory / "diagnostic.onnx")
        runtime = graph.RuntimeAdapter(path, feature_names=channels)
        diagnostic = graph.RuntimeAdapter(
            directory / "diagnostic.onnx", feature_names=channels, diagnostic=True
        )
        result["providers"] = runtime.provenance
        ort = graph.optional_modules()["onnxruntime"]
        result["runtime"]["ORT_build_text"] = ort.get_build_info()
        result["runtime"]["ORT_build_raw_UTF8_byte_sha256"] = hashlib.sha256(
            ort.get_build_info().encode()
        ).hexdigest()
        result["runtime"]["ORT_build_canonical_JSON_string_sha256"] = p.digest(
            ort.get_build_info()
        )
        result["artifact"] = dict(
            path="reconstruction.onnx",
            file_size_bytes=path.stat().st_size,
            file_byte_sha256=p.file_hash(path),
            graph_manifest_canonical_JSON_sha256=p.digest(manifest),
            canonical_scientific_model_sha256=spec["model"]["model_scientific_sha256"],
            parameter_payload_sha256=initial_parameter_hash,
        )
        p.write(directory / "export-frozen.json", result["artifact"], exclusive=True)
        stages["export"]["status"] = "passed"
        phase("synthetic", 60)
        for name, values in families().items():
            entry = dict(
                name=name,
                input_payload_byte_sha256=core.array_hash(values),
                verification={},
            )
            result["synthetic"].append(entry)
            entry["verification"] = numerical.verify(
                model,
                runtime,
                diagnostic,
                manifest,
                values,
                thresholds,
                channels,
                guard,
                result["counts"],
                persist=lambda state, entry=entry: (
                    entry.update(verification=state),
                    partial(),
                ),
            )
            partial()
        if any(
            entry["verification"]["status"] != "passed" for entry in result["synthetic"]
        ):
            raise ValueError(
                "Frozen synthetic numerical/strict-decision refusal; real array unopened."
            )
        if (
            p.file_hash(path) != result["artifact"]["file_byte_sha256"]
            or core.parameter_hash(model) != initial_parameter_hash
        ):
            raise ValueError("Export/parameter mutated before real opening.")
        result["access"]["synthetic_admitted"] = True
        access()
        stages["synthetic"]["status"] = "passed"
        phase("real", 60)
        values = open_real(root, spec, result["access"], persist=access)
        real_counts = counts()
        result["real_counts"] = real_counts
        result["real"] = numerical.verify(
            model,
            runtime,
            diagnostic,
            manifest,
            values,
            thresholds,
            channels,
            guard,
            real_counts,
            persist=lambda state: (result.update(real=state), partial()),
        )
        if result["real"]["status"] != "passed":
            raise ValueError("Complete real-grid numerical/strict-decision refusal.")
        if (
            p.file_hash(path) != result["artifact"]["file_byte_sha256"]
            or p.digest(p.read(directory / "graph-manifest.json"))
            != result["artifact"]["graph_manifest_canonical_JSON_sha256"]
            or core.parameter_hash(model) != initial_parameter_hash
            or core.array_hash(thresholds) != initial_threshold_hash
        ):
            raise ValueError(
                "Export/manifest/frozen parameter/threshold mutation after verification."
            )
        result["effective_threads_after"] = core.effective_threads()
        if result["effective_threads_before"] != result[
            "effective_threads_after"
        ] or result["source_file_sha256"] != q.source_map(root):
            raise ValueError("Current source/effective threading mutated.")
        q.check_dependencies(root, spec)
        q.frozen_metadata(root, spec)
        guard.context()
        stages["real"]["status"] = "passed"
        result["status"] = "completed_accepted"
    except BaseException as exc:
        result.update(
            error=f"{type(exc).__name__}: {exc}",
            failed_values=getattr(exc, "evidence", None),
        )
        if current:
            stages[current]["status"] = "failed"
    finally:
        tick = time.monotonic()
        if current:
            stages[current]["elapsed_seconds"] = (
                tick - stages[current]["started_monotonic"]
            )
        if guard:
            try:
                guard.deadline = min(grant["whole_deadline_monotonic"], tick + 2)
                p.write(
                    directory / "phase.json",
                    dict(name="cleanup", started_monotonic=tick, token=token),
                )
                if runtime:
                    runtime.close()
                if diagnostic:
                    diagnostic.close()
                model = values = thresholds = document = inferred = None
                if limiter:
                    limiter.restore_original_limits()
            except BaseException as exc:
                result.update(status="failed", cleanup_error=str(exc))
            finally:
                guard.close()
            result["resources"] = guard.report()
            if guard.error:
                result["status"] = "failed"
        result["cleanup_seconds"] = time.monotonic() - tick
        result["worker_wall_seconds"] = time.monotonic() - started
        if directory.exists():
            p.write(directory / "receipt.json", result, exclusive=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    result = execute(args.token)
    print("Frozen ONNX worker:", result["status"])
    return 0 if result["status"] == "completed_accepted" else 2


if __name__ == "__main__":
    sys.exit(main())
