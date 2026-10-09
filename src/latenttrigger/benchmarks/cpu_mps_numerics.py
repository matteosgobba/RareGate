"""Device-specific diagnostics and completed scopes; no scientific source edits."""

import copy
import json
import time

import numpy as np
import torch

from latenttrigger.benchmarks import arithmetic_cpu_v2 as a
from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import cpu_mps_protocol as q
from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.cpu_mps_device import exact_roundtrip
from latenttrigger.benchmarks.frozen_cpu_v2_numerics import exact


def synchronize(device):
    if device == "mps":
        torch.mps.synchronize()


def read_array(root, spec, audit, *, local=False, persist=lambda: None):
    key = "local_array_reads" if local else "original_array_reads"
    if audit[key + "_attempted"]:
        raise ValueError("One numerical prepared-array read per fresh worker.")
    path, _ = q.input_file(root, spec, local=local)
    audit[key + "_attempted"] += 1
    persist()
    values = np.load(path, allow_pickle=False)
    core.validate_features(values)
    if core.array_hash(values) != spec["input"]["array_bytes_sha256"]:
        raise ValueError("Frozen FP32 payload changed.")
    audit[key + "_completed"] += 1
    audit["rows_loaded"] = len(values)
    persist()
    return values


def transferred_model(cpu_model, device):
    model = copy.deepcopy(cpu_model).to(device).eval()
    for (_, before), (_, after) in zip(
        cpu_model.named_parameters(), model.named_parameters(), strict=True
    ):
        if after.dtype != torch.float32 or after.device.type != device:
            raise ValueError("Frozen parameter precision/device fallback.")
        synchronize(device)
        if before.detach().numpy().tobytes() != after.detach().cpu().numpy().tobytes():
            raise ValueError("Frozen155 FP32 parameter transfer roundtrip failed.")
    if model.parameter_count != 155 or core.parameter_hash(
        model
    ) != core.parameter_hash(cpu_model):
        raise ValueError("Frozen scientific parameter identities changed.")
    return model


def build_windows(model, values, batch, device, audit):
    result = []
    for start in range(0, 1024, batch):
        view = values[start : start + batch]
        tensor = exact_roundtrip(torch, torch.from_numpy(view), device)

        def forward(tensor=tensor):
            with torch.inference_mode():
                return model(tensor)

        output = forward()
        synchronize(device)
        reconstruction = output.cpu().numpy().copy()
        audit["numerical_forward_input_presentations"] += batch
        a.supported(reconstruction)
        result.append(
            dict(
                start=start,
                values=view,
                tensor=tensor,
                forward=forward,
                reconstruction=reconstruction,
            )
        )
    return result


def traced(model, values, device, audit):
    """Captured actual device affine inputs; transfers only during diagnostics."""
    handles, captures = [], {}
    try:
        for name, module in model.named_modules():
            if isinstance(module, (torch.nn.Linear, torch.nn.ReLU)):

                def hook(module, args, output, name=name):
                    if (
                        args[0].dtype != torch.float32
                        or output.dtype != torch.float32
                        or args[0].device.type != device
                        or output.device.type != device
                    ):
                        raise ValueError(
                            "Unsupported device local affine/activation precision."
                        )
                    synchronize(device)
                    captures[name] = (
                        args[0].detach().cpu().numpy().copy(),
                        output.detach().cpu().numpy().copy(),
                    )

                handles.append(module.register_forward_hook(hook))
        tensor = exact_roundtrip(torch, torch.from_numpy(values), device)
        with torch.inference_mode():
            output = model(tensor)
        synchronize(device)
        audit["numerical_forward_input_presentations"] += len(values)
        return output.cpu().numpy().copy(), captures
    finally:
        for handle in handles:
            handle.remove()


def check_relu(model, captures):
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.ReLU):
            inputs, output = captures[name]
            a.supported(inputs)
            a.supported(output)
            exact(
                output, np.maximum(inputs, np.float32(0)), "device_exact_ReLU/" + name
            )


def error_metrics(actual, reference):
    actual, reference = actual.astype(np.float64), reference.astype(np.float64)
    error = np.abs(actual - reference)
    denominator = np.maximum(np.abs(reference), np.finfo(np.float64).tiny)
    return dict(
        max_abs_error=float(error.max(initial=0)),
        max_relative_error=float((error / denominator).max(initial=0)),
        relative_denominator="max(abs(reference),float64.tiny)",
        byte_equal=actual.tobytes() == reference.tobytes(),
    )


def verify(
    cpu_model, model, values, thresholds, channels, windows, device, guard, audit
):
    a.round_mode()
    a.supported(values)
    for parameter in cpu_model.parameters():
        a.supported(parameter.detach().numpy())
    hashes = dict(
        input=core.array_hash(values),
        cpu_parameters=core.parameter_hash(cpu_model),
        device_parameters=core.parameter_hash(model),
        thresholds=core.array_hash(thresholds),
    )
    if hashes["cpu_parameters"] != hashes["device_parameters"]:
        raise ValueError("CPU/device parameter roundtrip mismatch.")
    guard.boundary("fresh_CPU1024_and_device_reference")
    cpu_reference, cpu_traces = a.trace(cpu_model, values, audit)
    cpu_scores = cpu_model.score(values, feature_names=channels)
    audit["numerical_forward_input_presentations"] += 1024
    device_reference, local_reference = traced(model, values, device, audit)
    repeated, _ = traced(model, values, device, audit)
    exact(device_reference, repeated, "own_device_full_reference_repeat")
    double = copy.deepcopy(cpu_model).double().eval()
    high, high_traces = a.trace(double, values.astype(np.float64), audit, double=True)
    envelope = a.global_envelope(cpu_model, high_traces, values)
    pair = a.add_up(envelope, envelope)
    records = []
    for traces in (cpu_traces, local_reference):
        check_relu(model, traces)
        records.extend(a.local_checks(double, traces, audit))
    records.append(
        a.assert_bound(cpu_reference, high, envelope, "CPU_reference_vs_diagnostic")
    )
    records.append(
        a.assert_bound(
            device_reference, high, envelope, "device_reference_vs_diagnostic"
        )
    )
    device_scores = model.score(values, feature_names=channels)
    synchronize(device)
    audit["numerical_forward_input_presentations"] += 1024
    ref_separated, _ = core.separated(values, device_reference, thresholds)
    core.comparison(
        ref_separated,
        device_scores,
        atol=1e-12,
        rtol=1e-12,
        name="device_reference_public_SSE",
    )
    exact(ref_separated, device_scores, "device_reference_public_SSE")
    core.verify_decisions(
        device_scores, cpu_scores, thresholds, "device_full_reference_decisions"
    )
    grids = []
    for batch, items in windows.items():
        guard.boundary(f"{device}_B{batch}_local_device_checks")
        reconstructed = np.empty_like(values)
        scores = np.empty(1024, dtype=np.float64)
        all_local = {
            name: (np.empty_like(x), np.empty_like(y))
            for name, (x, y) in local_reference.items()
        }
        for window in items:
            guard.check()
            start, stop = window["start"], window["start"] + batch
            output, captures = traced(model, window["values"], device, audit)
            with torch.inference_mode():
                repeat = window["forward"]()
            synchronize(device)
            audit["numerical_forward_input_presentations"] += batch
            exact(output, repeat.cpu().numpy(), "same_shape_unhooked_repeat")
            exact(output, window["reconstruction"], "actual_shape_cached_repeat")
            public = model.score(window["values"], feature_names=channels)
            synchronize(device)
            audit["numerical_forward_input_presentations"] += batch
            separated, _ = core.separated(window["values"], output, thresholds)
            core.comparison(
                separated,
                public,
                atol=1e-12,
                rtol=1e-12,
                name="same_shape_separated_public_SSE",
            )
            exact(separated, public, "same_shape_SSE")
            core.verify_decisions(
                public,
                cpu_scores[start:stop],
                thresholds,
                "all_grid_CPU_reference_decisions",
            )
            reconstructed[start:stop], scores[start:stop] = output, public
            for name, (x, y) in captures.items():
                all_local[name][0][start:stop], all_local[name][1][start:stop] = x, y
            guard.check()
        check_relu(model, all_local)
        local = a.local_checks(double, all_local, audit)
        for row in local:
            row["batch"] = batch
        records.extend(local)
        a.supported(reconstructed)
        records.extend(
            [
                a.assert_bound(
                    reconstructed, high, envelope, f"{batch}_device_vs_diagnostic"
                ),
                a.assert_bound(
                    reconstructed, cpu_reference, pair, f"{batch}_device_vs_CPU"
                ),
            ]
        )
        bound, _, _ = a.sse_difference_bound(
            values, cpu_reference, pair, scores, cpu_scores
        )
        records.append(
            a.assert_bound(scores, cpu_scores, bound, f"{batch}_SSE_CPU_bound")
        )
        grids.append(
            dict(
                batch=batch,
                reconstruction=error_metrics(reconstructed, cpu_reference),
                score=error_metrics(scores, cpu_scores),
                mismatch_counts=[0] * 4,
                same_shape_byte_exact=True,
            )
        )
    restored = dict(
        input=core.array_hash(values),
        cpu_parameters=core.parameter_hash(cpu_model),
        device_parameters=core.parameter_hash(model),
        thresholds=core.array_hash(thresholds),
    )
    if hashes != restored or any(m._forward_hooks for m in model.modules()):
        raise ValueError("Frozen mutation or diagnostic hook retained.")
    a.round_mode()
    return dict(
        status="passed",
        device=device,
        comparisons=records,
        grids=grids,
        hashes=hashes,
        CPU_reference_reconstruction_sha256=core.array_hash(cpu_reference),
        CPU_reference_scores_sha256=core.array_hash(cpu_scores),
        device_reference_reconstruction_sha256=core.array_hash(device_reference),
        device_reference_scores_sha256=core.array_hash(device_scores),
        diagnostic_sha256=core.array_hash(high),
        envelope_sha256=core.array_hash(envelope),
        local_affine_scalar_checks=sum(
            r["elements"]
            for r in records
            if r["comparison"].startswith("local_affine/")
        ),
        minimum_CPU_threshold_margins=np.min(
            np.abs(cpu_scores[:, None] - thresholds), axis=0
        ).tolist(),
        mismatch_counts=[0] * 4,
        own_reference_repeat_byte_exact=True,
        parameter_input_roundtrips_byte_exact=True,
        operation_contract="conditional_fixed_domain_local_checks;not_universal_Metal_certificate",
    )


def timed_invocation(
    function,
    *,
    device,
    scope,
    timer=time.perf_counter_ns,
    sync=synchronize,
    measured=True,
):
    if scope not in (
        "reconstruction",
        "score_decision",
        "adapter_decision",
    ) or device not in ("cpu", "mps"):
        raise ValueError("Unsupported device/scope.")
    if scope != "score_decision":
        sync(device)  # Clear pending work before the start timestamp.
    start = timer() if measured else None
    output = function()
    if scope != "score_decision":
        sync(device)  # Completion is included; reconstruction never copies to CPU here.
    elapsed = timer() - start if measured else None
    return output, elapsed


def run_cell(
    model,
    thresholds,
    channels,
    items,
    scope,
    batch,
    device,
    guard,
    cell,
    raw,
    audit,
    *,
    warmups=20,
    measurements=200,
    timer=time.perf_counter_ns,
):
    if len(items) != 1024 // batch:
        raise ValueError("Fixed source-ordered windows required.")
    guard.boundary(f"B{batch}/{scope}")
    cell.update(
        device=device,
        batch=batch,
        scope=scope,
        status="running",
        warmups_completed=0,
        timed_completed=0,
    )
    durations = []
    for phase, count in (("warmup", warmups), ("measurement", measurements)):
        for index in range(count):
            item = items[index % len(items)]
            if scope == "reconstruction":
                function = item["forward"]
            elif scope == "score_decision":

                def function(item=item):
                    return core.separated(
                        item["values"], item["reconstruction"], thresholds
                    )
            else:

                def function(item=item):
                    scores = model.score(item["values"], feature_names=channels)
                    return scores, core.decisions(scores, thresholds)

            guard.check()
            output, elapsed = timed_invocation(
                function,
                device=device,
                scope=scope,
                timer=timer,
                measured=phase == "measurement",
            )
            if phase == "measurement":
                durations.append(elapsed)
                cell["timed_completed"] += 1
            else:
                cell["warmups_completed"] += 1
            audit[phase + "_input_presentations"] += batch
            if scope != "score_decision":
                audit[phase + "_forward_input_presentations"] += batch
            raw.write(
                json.dumps(
                    dict(
                        batch=batch,
                        scope=scope,
                        device=device,
                        phase=phase,
                        index=index,
                        start=item["start"],
                        elapsed_ns=elapsed,
                    )
                )
                + "\n"
            )
            raw.flush()
            guard.check()
            if scope == "reconstruction":
                # Outside timer: CPU transfer solely for finite verification.
                if not np.isfinite(output.detach().cpu().numpy()).all():
                    raise ValueError("Nonfinite timed reconstruction.")
    cell.update(
        status="completed",
        latency_nanoseconds=p.distribution(durations, batch),
        timed_input_presentations=measurements * batch,
        warmup_input_presentations=warmups * batch,
    )
