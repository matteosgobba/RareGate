"""Isolated paired scopes; reuse unchanged arithmetic and canonical public paths."""

import json
import time

import numpy as np
import torch

from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks import pytorch_onnx_cpu_protocol as q
from latenttrigger.exports import onnx_graph as graph


def admit(record):
    if (
        record.get("status") != "passed"
        or record.get("windows_verified") != 1193
        or record.get("row_window_presentations") != 5120
        or record.get("unique_rows") != 1024
        or record.get("decision_mismatches") != [0] * 4
        or record.get("local_affine_violations") != 0
        or record.get("hashes_before") != record.get("hashes_after")
        or [g.get("batch") for g in record.get("grids", [])] != list(q.BATCHES)
    ):
        raise ValueError("Complete numerical gate status/count/identity refusal.")
    for row in [
        *record["reference_comparisons"],
        *(r for g in record["grids"] for r in g["comparisons"]),
    ]:
        if row.get("passed") is not True or row.get("violations") != 0:
            raise ValueError(
                "Preserved numerical violation forbids performance acceptance."
            )
    for g in record["grids"]:
        if (
            g["status"] != "passed"
            or g["decision_mismatches"] != [0] * 4
            or g["local_affine_violations"] != 0
            or g["windows"] != 1024 // g["batch"]
            or g["rows"] != 1024
            or not all(
                g[k] is True
                for k in (
                    "same_runtime_repeat_byte_exact",
                    "diagnostic_primary_final_byte_exact",
                    "same_runtime_SSE_byte_exact",
                )
            )
        ):
            raise ValueError("Grid local/repeat/strict-decision refusal.")


def effective_session(runtime):
    ort = graph.optional_modules()["onnxruntime"]
    session = runtime.session
    options = session.get_session_options()
    if (
        session.get_providers() != ["CPUExecutionProvider"]
        or options.execution_mode != ort.ExecutionMode.ORT_SEQUENTIAL
        or options.intra_op_num_threads != 1
        or options.inter_op_num_threads != 1
        or options.graph_optimization_level
        != ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        or getattr(session, "_enable_fallback", None) is not False
    ):
        raise ValueError("Actual provider/thread/optimization/fallback drift.")
    return dict(runtime.provenance, fallback_effective=False)


def prepare_windows(model, runtime, values, channels, counts, guard):
    result = {}
    with torch.inference_mode():
        for batch in q.BATCHES:
            guard.boundary("prepare_windows_B" + str(batch))
            items = []
            for start in range(0, 1024, batch):
                guard.check()
                x = values[start : start + batch]
                if runtime == "PyTorch":
                    tensor = torch.from_numpy(x)

                    def forward(tensor=tensor):
                        return model(tensor)
                else:
                    feed = {"event_features": x}

                    def forward(feed=feed):
                        return model.session.run(None, feed)[0]

                out = forward()
                rec = out if isinstance(out, np.ndarray) else out.numpy()
                if (
                    rec.dtype != np.float32
                    or rec.shape != x.shape
                    or not np.isfinite(rec).all()
                ):
                    raise ValueError("Invalid prepared reconstruction.")
                counts["prepared_forward_row_presentations"] += batch
                items.append(
                    dict(start=start, values=x, reconstruction=rec, forward=forward)
                )
                guard.check()
            result[batch] = items
    return result


def verify_prepared(
    model, runtime, values, windows, channels, thresholds, counts, guard
):
    """Own same-shape/cache/public equality and zero decisions vs CPU1024 reference."""
    cpu = runtime["cpu"]
    ref = cpu.score(values, feature_names=channels)
    counts["prepared_reference_row_presentations"] += 1024
    with torch.inference_mode():
        for batch, items in windows.items():
            for item in items:
                guard.check()
                x = item["values"]
                actual = item["forward"]()
                actual = actual if isinstance(actual, np.ndarray) else actual.numpy()
                counts["prepared_verification_forward_row_presentations"] += batch
                canonical = (
                    core.reconstruct(model, x, channels)
                    if runtime["name"] == "PyTorch"
                    else model.reconstruct(x, feature_names=channels)
                )
                public = model.score(x, feature_names=channels)
                counts["prepared_verification_forward_row_presentations"] += 2 * batch
                for other in (canonical, item["reconstruction"]):
                    if (
                        actual.tobytes() != other.tobytes()
                        or actual.dtype != other.dtype
                    ):
                        raise ValueError(
                            "Prepared/cached/public reconstruction repeat mismatch."
                        )
                separated, _ = core.separated(x, actual, thresholds)
                core.comparison(
                    separated,
                    public,
                    atol=1e-12,
                    rtol=1e-12,
                    name="prepared_same_shape_SSE",
                )
                core.verify_decisions(
                    public,
                    ref[item["start"] : item["start"] + batch],
                    thresholds,
                    "prepared_vs_CPU1024",
                )
                guard.check()
    return dict(
        windows_verified=1193,
        decisions_per_threshold=5120,
        mismatches=[0] * 4,
        prepared_public_cached_byte_exact=True,
    )


def run_cell(
    model,
    thresholds,
    channels,
    windows,
    scope,
    batch,
    guard,
    cell,
    raw_file,
    *,
    warmups=20,
    measurements=200,
    timer=time.perf_counter_ns,
):
    if scope not in q.SCOPES:
        raise ValueError("Unsupported timing scope.")
    guard.boundary(f"B{batch}/{scope}")
    cell.update(
        batch=batch,
        scope=scope,
        status="running",
        warmups_completed=0,
        timed_completed=0,
    )
    durations = []
    for phase, count in (("warmup", warmups), ("measurement", measurements)):
        for index in range(count):
            window = windows[index % len(windows)]
            x = window["values"]
            if scope == "reconstruction":
                function = window["forward"]
            elif scope == "score_decision":

                def function(x=x, r=window["reconstruction"]):
                    return core.separated(x, r, thresholds)
            else:

                def function(x=x):
                    scores = model.score(x, feature_names=channels)
                    return scores, core.decisions(scores, thresholds)

            guard.check()
            begin = timer() if phase == "measurement" else None
            output = function()
            elapsed = timer() - begin if begin is not None else None
            key = "timed_completed" if phase == "measurement" else "warmups_completed"
            cell[key] += 1
            if elapsed is not None:
                durations.append(elapsed)
            # Persist completed calls before positivity/guard checks can refuse them.
            raw_file.write(
                json.dumps(
                    dict(
                        batch=batch,
                        scope=scope,
                        phase=phase,
                        index=index,
                        start=window["start"],
                        elapsed_ns=elapsed,
                    )
                )
                + "\n"
            )
            raw_file.flush()
            if elapsed is not None and (type(elapsed) is not int or elapsed <= 0):
                raise ValueError(
                    "Nonpositive measured duration; no finite throughput/retry."
                )
            guard.check()
            if scope == "reconstruction":
                finite = (
                    np.isfinite(output).all()
                    if isinstance(output, np.ndarray)
                    else torch.isfinite(output).all().item()
                )
                if not finite:
                    raise ValueError("Nonfinite timed output.")
    cell.update(
        status="completed",
        latency_nanoseconds=p.distribution(durations, batch),
        timed_input_presentations=measurements * batch,
        warmup_input_presentations=warmups * batch,
    )
    return durations
