"""Canonical CPU inference/timing boundaries; imported only in numeric workers."""

import hashlib
import os
import time

import numpy as np
import torch
from threadpoolctl import threadpool_info, threadpool_limits

from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.accelerate_threads import AccelerateThreads
from latenttrigger.data.processed import ProcessedStore
from latenttrigger.models.autoencoder import CompactAutoencoder
from latenttrigger.models.pca import PCAReconstruction

_accelerate = None


class ThreadLimits:
    def __init__(self, pools, accelerate):
        self.pools, self.accelerate = pools, accelerate

    def restore_original_limits(self):
        try:
            if self.accelerate:
                self.accelerate.restore()
        finally:
            self.pools.restore_original_limits()


class NumericalError(ValueError):
    def __init__(self, message, evidence):
        super().__init__(message)
        self.evidence = evidence


def array_hash(values):
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def configure_threads(specification):
    global _accelerate
    expected = specification["runtime"]["thread_environment_before_imports"]
    if any(os.environ.get(key) != value for key, value in expected.items()):
        raise ValueError("Thread environment must be fixed before numerical imports.")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True, warn_only=False)
    pools = threadpool_limits(limits=1)
    _accelerate = None
    try:
        blas = np.show_config(mode="dicts")["Build Dependencies"]["blas"]
        if blas.get("name") == "accelerate":
            _accelerate = AccelerateThreads()
        limiter = ThreadLimits(pools, _accelerate)
        return limiter, effective_threads()
    except BaseException:
        if _accelerate:
            _accelerate.restore()
        pools.restore_original_limits()
        raise


def effective_threads():
    pools = threadpool_info()
    blas = np.show_config(mode="dicts")["Build Dependencies"]["blas"]
    if (
        not pools
        or any(
            type(pool.get("num_threads")) is not int or pool["num_threads"] != 1
            for pool in pools
        )
        or torch.get_num_threads() != 1
        or torch.get_num_interop_threads() != 1
        or not torch.are_deterministic_algorithms_enabled()
    ):
        raise ValueError(
            "Effective BLAS/OpenMP/PyTorch single-thread enforcement unsupported."
        )
    if blas.get("name") == "accelerate":
        if _accelerate is None:
            raise ValueError("Effective Accelerate threading enforcement unsupported.")
        native = _accelerate.report()
    elif any(
        name in blas.get("name", "").lower() for name in ("openblas", "mkl")
    ) and any(pool.get("user_api") == "blas" for pool in pools):
        native = None
    else:
        raise ValueError("Effective BLAS threading enforcement unsupported.")
    return {
        "pytorch_intra": 1,
        "pytorch_inter": 1,
        "deterministic_algorithms": True,
        "threadpools": pools,
        "numpy_blas_build": blas,
        "accelerate_thread_control": native,
    }


def validate_features(values):
    if (
        values.shape != (1024, 8)
        or values.dtype != np.float32
        or not values.flags.c_contiguous
        or not np.isfinite(values).all()
    ):
        raise ValueError(
            "Expected exactly1024 finite prestandardized FP32 aggregate rows."
        )


def prepare_input(
    root, specification, directory, guard, audit, *, factory=ProcessedStore
):
    inputs = specification["input"]
    store_path = root / inputs["store"]
    p.validate_scope(
        store_path,
        inputs["population"],
        inputs["dev_only"],
        inputs["allow_test"],
        inputs["include_labels"],
        root,
    )
    p.validate_dev_manifest(p.read(store_path / "manifest.json"), inputs)
    store = iterator = None
    timings = {}
    try:
        guard.boundary("dev_constructor_custody")
        audit["custody"] = {
            "scope": "dev",
            "operation": "unchanged_full_dev_constructor_verification",
            "status": "started",
            "population_requested": False,
        }
        p.write(directory / "access-audit.json", audit)
        tick = time.perf_counter()
        store = factory(store_path)
        timings["dev_constructor_verification_seconds"] = time.perf_counter() - tick
        audit["custody"]["status"] = "completed"
        guard.boundary("one_public_feature_batch")
        audit["population"] = {
            "split": "train_background",
            "dev_only": True,
            "allow_test": False,
            "include_labels": False,
            "representation": "event_features",
            "status": "started",
            "rows": 0,
            "requests": 1,
        }
        p.write(directory / "access-audit.json", audit)
        tick = time.perf_counter()
        iterator = store.iter_features(
            "train_background",
            batch_size=1024,
            dev_only=True,
            allow_test=False,
            include_labels=False,
        )
        batch = next(iterator)  # Deliberately never request a second batch.
        timings["public_input_loading_seconds"] = time.perf_counter() - tick
        audit["population"]["rows"] = len(batch.event_features)
        audit["population"]["status"] = "loaded_pending_validation"
        p.write(directory / "access-audit.json", audit)
        values, ids = batch.event_features, batch.event_ids
        validate_features(values)
        if (
            batch.labels is not None
            or ids.shape != (1024,)
            or ids.dtype != np.int64
            or not (np.diff(ids) > 0).all()
        ):
            raise ValueError("Truth/count/source-order mismatch in public dev input.")
        tick = time.perf_counter()
        np.save(directory / "input.npy", values, allow_pickle=False)
        record = {
            "shape": [1024, 8],
            "dtype": "float32",
            "input_bytes_sha256": array_hash(values),
            "input_file_sha256": p.file_hash(directory / "input.npy"),
            "source_ids_bytes_sha256": array_hash(ids),
            "unique_rows": 1024,
            "strict_source_order": True,
            "manifest_scientific_sha256": store.manifest["scientific_sha256"],
            "population_requests": 1,
            "population_presentations": 1024,
            "custody_operations": 1,
            "optimizer_updates": 0,
        }
        p.write(directory / "prepared.json", record, exclusive=True)
        timings["input_preparation_and_persistence_seconds"] = (
            time.perf_counter() - tick
        )
        audit["population"]["status"] = "completed"
        audit["population"]["unique_rows"] = 1024
        audit["population"]["ids_sha256"] = record["source_ids_bytes_sha256"]
        return record, timings
    except BaseException:
        if "population" in audit:
            audit["population"]["status"] = "failed"
        elif "custody" in audit:
            audit["custody"]["status"] = "failed"
        raise
    finally:
        tick = time.perf_counter()
        if iterator is not None:
            iterator.close()
        if store is not None:
            store.close()
        timings["input_iterator_store_cleanup_seconds"] = time.perf_counter() - tick
        p.write(directory / "access-audit.json", audit)


def load_input(directory):
    prep = directory / "prepare"
    record = p.read(prep / "prepared.json")
    path = prep / "input.npy"
    if path.stat().st_size > 65536 or p.file_hash(path) != record["input_file_sha256"]:
        raise ValueError("Prepared input file identity/size changed.")
    values = np.load(path, allow_pickle=False)
    validate_features(values)
    if (
        array_hash(values) != record["input_bytes_sha256"]
        or record["unique_rows"] != 1024
    ):
        raise ValueError("Prepared input byte identity/rows changed.")
    return values, record


def load_model(root, entry):
    if entry["name"] == "pca-v1":
        model = PCAReconstruction.load(root / entry["model_path"])
        if model.k != 6:
            raise ValueError("Frozen PCA must retain six components.")
    elif entry["name"] == "compact-autoencoder-v2":
        model = CompactAutoencoder.load(root / entry["model_path"])
        if model.parameter_count != 155 or any(
            v.dtype != torch.float32 or v.device.type != "cpu"
            for v in model.parameters()
        ):
            raise ValueError("Frozen CPU AE155/FP32 parameters required.")
        model.eval()
    else:
        raise ValueError("Unsupported model selector.")
    result = p.read(root / entry["results_path"])
    thresholds = np.array(
        [t["threshold"] for t in result["scientific"]["thresholds"]], dtype=np.float64
    )
    return model, thresholds


def parameter_hash(model):
    if isinstance(model, PCAReconstruction):
        return p.digest(
            {
                "arrays": {
                    key: array_hash(getattr(model, key))
                    for key in (
                        "mean",
                        "components",
                        "explained_variance",
                        "explained_variance_ratio",
                    )
                },
                "k": model.k,
                "target": model.target,
                "training_count": model.training_count,
            }
        )
    return p.digest(
        {
            key: array_hash(value.detach().cpu().numpy())
            for key, value in model.state_dict().items()
        }
    )


def decisions(scores, thresholds):
    if (
        scores.dtype != np.float64
        or scores.ndim != 1
        or not np.isfinite(scores).all()
        or (scores < 0).any()
    ):
        raise NumericalError(
            "Nonfinite/invalid canonical score.",
            {"values": [repr(v) for v in scores[:8]]},
        )
    return scores[:, None] > thresholds[None, :]


def separated(values, reconstruction, thresholds):
    residual = values.astype(np.float64) - reconstruction.astype(np.float64)
    scores = np.sum(residual * residual, axis=1)
    return scores, decisions(scores, thresholds)


def reconstruct(model, values, channels):
    if isinstance(model, PCAReconstruction):
        return model.reconstruct(values, feature_names=channels)
    with torch.inference_mode():
        return model(torch.from_numpy(values)).cpu().numpy()


def comparison(actual, reference, *, atol, rtol, name):
    actual, reference = np.asarray(actual), np.asarray(reference)
    if (
        actual.shape != reference.shape
        or not np.isfinite(actual).all()
        or not np.isfinite(reference).all()
    ):
        raise NumericalError(
            "Nonfinite/shape comparison failure: " + name,
            {
                "comparison": name,
                "actual_shape": list(actual.shape),
                "actual_values": [repr(v) for v in actual.reshape(-1)[:8]],
            },
        )
    error = np.abs(actual.astype(np.float64) - reference.astype(np.float64))
    relative = error / np.maximum(np.abs(reference.astype(np.float64)), atol)
    good = error <= atol + rtol * np.abs(reference)
    record = {
        "comparison": name,
        "atol": atol,
        "rtol": rtol,
        "max_absolute_error": float(error.max(initial=0)),
        "max_relative_error": float(relative.max(initial=0)),
        "exact_byte_equality": actual.dtype == reference.dtype
        and actual.tobytes() == reference.tobytes(),
        "passed": bool(good.all()),
    }
    if not good.all():
        index = tuple(int(i) for i in np.argwhere(~good)[0])
        record["first_failure"] = {
            "index": list(index),
            "actual": float(actual[index]),
            "reference": float(reference[index]),
        }
        raise NumericalError(
            "Preregistered numerical tolerance failed: " + name, record
        )
    return record


def verify_decisions(actual, reference, thresholds, name):
    left, right = decisions(actual, thresholds), decisions(reference, thresholds)
    counts = np.sum(left != right, axis=0)
    record = {
        "comparison": name,
        "mismatches_per_threshold": counts.tolist(),
        "passed": not bool(counts.any()),
    }
    if counts.any():
        event, threshold = (int(i) for i in np.argwhere(left != right)[0])
        record["first_failure"] = {
            "event_relative_index": event,
            "threshold": float(thresholds[threshold]),
            "actual_score": float(actual[event]),
            "reference_score": float(reference[event]),
        }
        raise NumericalError("Frozen strict-threshold decision mismatch.", record)
    return record


def build_windows(model, values, batch):
    windows = []
    for start in range(0, 1024, batch):
        x = values[start : start + batch]
        if isinstance(model, PCAReconstruction):
            prepared = x.astype(np.float64)
            basis = model.components[: model.k]

            def forward(x=prepared, basis=basis):
                # Exact existing expression and left-to-right operation order.
                return (x - model.mean) @ basis.T @ basis + model.mean
        else:
            tensor = torch.from_numpy(x)

            def forward(x=tensor):
                return model(x)

        with torch.inference_mode():
            raw = forward()
        reconstruction = (
            raw if isinstance(raw, np.ndarray) else raw.detach().cpu().numpy()
        )
        windows.append(
            {
                "start": start,
                "values": x,
                "reconstruction": reconstruction,
                "forward": forward,
            }
        )
    return windows


def _accumulate(records, record):
    key = (record["batch"], record["comparison"])
    previous = next((r for r in records if (r["batch"], r["comparison"]) == key), None)
    if previous is None:
        record.pop("start")
        record["windows_verified"] = 1
        records.append(record)
    else:
        previous["windows_verified"] += 1
        for name in ("max_absolute_error", "max_relative_error"):
            if name in record:
                previous[name] = max(previous[name], record[name])
        if "exact_byte_equality" in record:
            previous["exact_byte_equality"] &= record["exact_byte_equality"]
        if "mismatches_per_threshold" in record:
            previous["mismatches_per_threshold"] = [
                a + b
                for a, b in zip(
                    previous["mismatches_per_threshold"],
                    record["mismatches_per_threshold"],
                    strict=True,
                )
            ]


def verify_windows(
    model, values, thresholds, channels, windows_by_batch, guard, records, audit
):
    guard.boundary("numerical_verification")
    reference = reconstruct(model, values, channels)
    reference_score = model.score(values, feature_names=channels)
    audit["numerical_forward_input_presentations"] += 2048
    decisions(reference_score, thresholds)
    tolerance = (1e-12, 1e-12) if isinstance(model, PCAReconstruction) else (1e-6, 1e-5)
    for batch, windows in windows_by_batch.items():
        for window in windows:
            guard.check()
            start, x = window["start"], window["values"]
            canonical = reconstruct(model, x, channels)
            same_shape_score = model.score(x, feature_names=channels)
            audit["numerical_forward_input_presentations"] += 2 * batch
            with torch.inference_mode():
                output = window["forward"]()
            actual = (
                output
                if isinstance(output, np.ndarray)
                else output.detach().cpu().numpy()
            )
            audit["numerical_forward_input_presentations"] += batch
            same_shape_separated, _ = separated(x, canonical, thresholds)
            prepared_score, _ = separated(x, actual, thresholds)
            for name, left, right, tol in [
                (
                    "prepared_vs_canonical_same_shape_reconstruction",
                    actual,
                    canonical,
                    tolerance,
                ),
                (
                    "separated_vs_public_same_shape_score",
                    same_shape_separated,
                    same_shape_score,
                    (1e-12, 1e-12),
                ),
                (
                    "reconstruction_across_batch",
                    actual,
                    reference[start : start + batch],
                    tolerance,
                ),
                (
                    "score_across_batch",
                    prepared_score,
                    reference_score[start : start + batch],
                    tolerance,
                ),
                (
                    "public_score_across_batch",
                    same_shape_score,
                    reference_score[start : start + batch],
                    tolerance,
                ),
            ]:
                record = comparison(left, right, atol=tol[0], rtol=tol[1], name=name)
                record.update(batch=batch, start=start)
                _accumulate(records, record)
            for name, left in [
                ("prepared_decisions", prepared_score),
                ("public_decisions", same_shape_score),
            ]:
                record = verify_decisions(
                    left, reference_score[start : start + batch], thresholds, name
                )
                record.update(batch=batch, start=start)
                _accumulate(records, record)
            # The score-only scope keeps this grid shape's fresh reconstruction.
            window["reconstruction"] = canonical
            guard.check()
    return {
        "reference_reconstruction_sha256": array_hash(reference),
        "reference_scores_sha256": array_hash(reference_score),
        "sample_decision_counts": decisions(reference_score, thresholds)
        .sum(axis=0)
        .tolist(),
        "relative_error_denominator": "max(abs(reference),comparison_atol)",
    }


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
    if scope not in ("reconstruction", "score_decision", "adapter_decision"):
        raise ValueError("Unsupported timing scope.")
    guard.boundary(f"B{batch}/{scope}")
    durations = []
    cell.update(
        batch=batch,
        scope=scope,
        warmups_completed=0,
        timed_completed=0,
        status="running",
    )
    for phase, count in (("warmup", warmups), ("measurement", measurements)):
        for index in range(count):
            window = windows[index % len(windows)]
            x = window["values"]
            if scope == "reconstruction":
                function = window["forward"]
            elif scope == "score_decision":

                def function(x=x, r=window["reconstruction"]):
                    return separated(x, r, thresholds)
            else:

                def function(x=x):
                    score = model.score(x, feature_names=channels)
                    return score, decisions(score, thresholds)

            guard.check()
            started = timer() if phase == "measurement" else None
            output = function()
            elapsed = timer() - started if started is not None else None
            if phase == "measurement":
                durations.append(elapsed)
                cell["timed_completed"] += 1
            else:
                cell["warmups_completed"] += 1
            # Record completed invocations even if their subsequent guard fails.
            if raw_file:
                raw_file.write(
                    __import__("json").dumps(
                        {
                            "batch": batch,
                            "scope": scope,
                            "phase": phase,
                            "index": index,
                            "start": window["start"],
                            "elapsed_ns": elapsed,
                        }
                    )
                    + "\n"
                )
                raw_file.flush()
            guard.check()
            if scope == "reconstruction":
                finite = (
                    bool(np.isfinite(output).all())
                    if isinstance(output, np.ndarray)
                    else bool(torch.isfinite(output).all())
                )
                if not finite:
                    raise NumericalError(
                        "Nonfinite timed reconstruction.",
                        {
                            "batch": batch,
                            "scope": scope,
                            "actual_values": [
                                repr(v)
                                for v in (
                                    output
                                    if isinstance(output, np.ndarray)
                                    else output.detach().cpu().numpy()
                                ).reshape(-1)[:8]
                            ],
                        },
                    )
    cell.update(
        status="completed",
        latency_nanoseconds=p.distribution(durations, batch),
        timed_input_presentations=measurements * batch,
        warmup_input_presentations=warmups * batch,
    )
    return durations
