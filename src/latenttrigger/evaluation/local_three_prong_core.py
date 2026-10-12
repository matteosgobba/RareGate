"""Frozen local numerical custody and exactly-once native signal/cache evaluation."""

import os

import numpy as np
import torch
from sklearn.metrics import precision_recall_curve, roc_curve

from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import protocol as p
from latenttrigger.data.analysis import open_raw
from latenttrigger.data.features import (
    Parameters,
    canonicalize,
    physical_aggregates,
    standardized_aggregates,
)
from latenttrigger.data.inspection import (
    AGGREGATE_NAMES,
    event_fingerprints,
    inspect_particles,
)
from latenttrigger.evaluation import local_three_prong_protocol as q
from latenttrigger.evaluation.guarded_audit import durable
from latenttrigger.evaluation.guarded_core import load_candidate, validate_manifest
from latenttrigger.evaluation.metrics import (
    at_threshold,
    evaluate_scores,
    score_summary,
)
from latenttrigger.evaluation.three_prong_core import check_overlap


def hdf_layout(handle, count, audit=None, boundary=lambda: None):
    import h5py

    paths = ("/df/block0_values", "/df/block0_items", "/df/axis0", "/df/axis1")
    q.require(
        set(handle) == {"df"}
        and isinstance(handle.get("/df", getlink=True), h5py.HardLink),
        "Pinned local group hard link required before dereference",
    )
    q.require(
        isinstance(handle["/df"], h5py.Group)
        and set(handle["/df"]) == {v.rsplit("/", 1)[1] for v in paths},
        "Exact four-dataset pandas-fixed layout",
    )
    for path in paths:
        q.require(
            isinstance(handle.get(path, getlink=True), h5py.HardLink),
            "External/soft link refused",
        )
        ds = handle[path]
        q.require(
            isinstance(ds, h5py.Dataset) and not ds.is_virtual and not ds.external,
            "Virtual/external/unknown dataset",
        )
    values = handle[paths[0]]
    q.require(
        values.shape == (count, 2101) and values.dtype == np.dtype("<f8"),
        "Pinned FP64 width2101/count required",
    )
    for path, kind in zip(paths[1:3], ("column_items", "column_axis"), strict=True):
        axis = handle[path]
        q.require(
            axis.shape == (2101,) and axis.dtype == np.dtype("<i8"),
            "Exact integer column encoding",
        )
        row = audit.request(kind, 2101, source=path) if audit else None
        boundary()
        result = axis[:]
        boundary()
        if audit:
            audit.read(row, len(result))
        q.require(
            np.array_equal(result, np.arange(2101)), "Column ordinal sequence mismatch"
        )
    q.require(
        handle[paths[3]].shape == (count,)
        and handle[paths[3]].dtype == np.dtype("<i8"),
        "Exact row-axis encoding",
    )
    return values


def frozen_features(rows, params):
    q.require(
        rows.ndim == 2 and rows.shape[1] == 2101 and rows.dtype == np.float64,
        "Source FP64 rows/width",
    )
    particles = rows[:, :2100].reshape(-1, 700, 3)
    flags = inspect_particles(particles, rows[:, 2100])
    invalid = {
        name: int(value.sum())
        for name, value in flags.items()
        if name not in ("eligible", "multiplicity")
    }
    invalid["wrong_signal_label"] = int((rows[:, 2100] != 1).sum())
    q.require(
        not any(invalid.values()), "Particle/label validity gate: " + str(invalid)
    )
    # Exact original sequence: source sorting BEFORE physicalFP32 storage, all700slots,
    # then FP64 aggregate accumulation, frozen logs/scaler, finalFP32. No truncation.
    chunk = canonicalize(particles)
    x = standardized_aggregates(physical_aggregates(chunk.padded), params)
    q.require(
        x.shape == (len(rows), 8)
        and x.dtype == np.dtype("<f4")
        and np.isfinite(x).all(),
        "Finite frozen full-event features",
    )
    return x, event_fingerprints(particles), invalid


def prepare(root, spec, directory, audit, guard):
    local = spec["local_payload"]
    count = spec["source"]["publisher_expected_events"]
    q.check_file(
        root, local["path"], local["SHA256"], clock=guard.clock, deadline=guard.deadline
    )
    params = Parameters.from_config(p.read(root / spec["transform"]["path"]))
    prepared = q.fixed(root, q.PREPARED)
    prepared.mkdir(parents=True, exist_ok=False)
    features = np.lib.format.open_memmap(
        prepared / "event_features.npy", mode="w+", dtype="<f4", shape=(count, 8)
    )
    fingerprints = np.empty(count, dtype="V32")
    raw_row = audit.request("raw_custody", count, source=local["path"])
    preparation = audit.request("signal_preparation", count, source=q.PREPARED)
    validation = dict(
        status="numerical_custody_inflight",
        confirmed_raw_rows=0,
        validated_rows=0,
        nonempty_events=0,
        invalid_categories={
            k: 0
            for k in (
                "unexpected_label",
                "nan",
                "infinity",
                "negative_pt",
                "malformed_padding",
                "non_trailing_padding",
                "empty",
                "wrong_signal_label",
                "transformation_failed_batch_rows",
                "physical_fp32_overflow",
                "axis_order_failure",
            )
        },
        source_batches=[],
    )
    durable(directory / "validity.json", validation)
    try:
        guard.check()
        with open_raw(q.fixed(root, local["path"])) as handle:
            ds = hdf_layout(handle, count, audit, guard.check)
            axis_row = audit.request("row_axis", count, source="/df/axis1")
            for start in range(0, count, 992):
                stop = min(start + 992, count)
                size = stop - start
                audit.inflight(raw_row, "raw_dataset_read", size)
                guard.check()
                rows = ds[start:stop]
                guard.check()
                audit.read(raw_row, len(rows))
                validation["confirmed_raw_rows"] += len(rows)
                audit.inflight(axis_row, "source_row_axis_read", size)
                guard.check()
                axis = handle["/df/axis1"][start:stop]
                guard.check()
                audit.read(axis_row, len(axis))
                if not np.array_equal(axis, np.arange(start, stop)):
                    validation["invalid_categories"]["axis_order_failure"] += int(
                        np.count_nonzero(axis != np.arange(start, stop))
                    )
                    durable(directory / "validity.json", validation)
                    raise ValueError("Source row order mismatch;no reordering/subset")
                particles = rows[:, :2100].reshape(-1, 700, 3)
                flags = inspect_particles(particles, rows[:, 2100])
                for name, value in flags.items():
                    if name not in ("eligible", "multiplicity"):
                        validation["invalid_categories"][name] += int(value.sum())
                validation["invalid_categories"]["wrong_signal_label"] += int(
                    (rows[:, 2100] != 1).sum()
                )
                validation["invalid_categories"]["physical_fp32_overflow"] += int(
                    (np.abs(particles) > np.finfo(np.float32).max)
                    .any(axis=(1, 2))
                    .sum()
                )
                durable(directory / "validity.json", validation)
                q.require(
                    not any(validation["invalid_categories"].values()),
                    "Invalid population gate;preserve categories/no filtering",
                )
                audit.inflight(preparation, "frozen_transform_and_feature_write", size)
                guard.check()
                try:
                    x, fp, _ = frozen_features(rows, params)
                except ValueError:
                    validation["invalid_categories"][
                        "transformation_failed_batch_rows"
                    ] += size
                    durable(directory / "validity.json", validation)
                    raise
                guard.check()
                features[start:stop] = x
                fingerprints[start:stop] = fp
                audit.read(preparation, size)
                validation["validated_rows"] += size
                validation["nonempty_events"] += size
                validation["source_batches"].append(
                    dict(first=start, last=stop - 1, rows=size)
                )
                durable(directory / "validity.json", validation)
                guard.check()
        q.check_file(
            root,
            local["path"],
            local["SHA256"],
            clock=guard.clock,
            deadline=guard.deadline,
        )
        features.flush()
        del features, rows, particles, axis, x, fp
        ref = spec["original_fingerprints"]
        path = q.check_file(
            root, ref["path"], ref["sha256"], clock=guard.clock, deadline=guard.deadline
        )
        q.array_header(path, "|V32", ref["shape"])
        original_row = audit.request(
            "original_fingerprint_integrity", ref["shape"][0], source=ref["path"]
        )
        guard.check()
        original = np.load(path, allow_pickle=False)
        guard.check()
        audit.read(original_row, len(original))
        q.require(
            original.shape == tuple(ref["shape"]) and original.dtype == np.dtype("V32"),
            "Original all-role registry shape/type",
        )
        overlap = check_overlap(fingerprints, original)
        guard.check()
        p.write(directory / "overlap.json", overlap, exclusive=True)
        q.require(
            overlap["within_source_duplicates"]
            == overlap["original_overlap_count"]
            == 0,
            "Exact duplicate/all-role overlap gate;no selection",
        )
        np.save(prepared / "fingerprints.npy", fingerprints, allow_pickle=False)
        for path in (prepared / "event_features.npy", prepared / "fingerprints.npy"):
            with path.open("rb") as stream:
                os.fsync(stream.fileno())
        validation["status"] = "complete_all_rows_valid_unique_disjoint"
        durable(directory / "validity.json", validation)
        science = dict(
            source=spec["source"],
            actual_raw_sha256=local["SHA256"],
            transform=spec["transform"],
            features=spec["features"],
            dtype="<f4",
            count=count,
            label_provenance="verified_all_last_column_labels_1",
            original_training_scientific_sha256=spec["original_store"][
                "scientific_sha256"
            ],
            original_fingerprint_reference=ref,
            cached_background=spec["cached_background"],
            source_order="all_rows_0_to_N_minus_1_no_selection",
            validated_rows=validation["validated_rows"],
            raw_byte_integrity_before_and_after=True,
            nonempty_events=validation["nonempty_events"],
            invalid_categories=validation["invalid_categories"],
            transformation_sequence="sourceFP64_validate_sort_wrap→physicalFP32_all_particles→aggregateFP64→frozen_logs_scaler→featuresFP32",
            **overlap,
            output_file_byte_sha256={
                f.name: p.file_hash(f) for f in prepared.iterdir() if f.is_file()
            },
        )
        manifest = dict(scientific=science, scientific_sha256=p.digest(science))
        q.compatibility(manifest, spec)
        p.write(prepared / "manifest.json", manifest, exclusive=True)
        guard.check()
        return manifest
    except BaseException as error:
        validation.update(
            status="failed_no_subset", error=f"{type(error).__name__}: {error}"
        )
        durable(directory / "validity.json", validation)
        raise


def validate_prepared(root, spec, guard):
    manifest = p.read(root / q.PREPARED / "manifest.json")
    science = q.compatibility(manifest, spec)
    q.require(
        set(science["output_file_byte_sha256"])
        == {"event_features.npy", "fingerprints.npy"},
        "Complete owned prepared artifacts",
    )
    for file, sha in science["output_file_byte_sha256"].items():
        q.check_file(
            root,
            q.PREPARED + "/" + file,
            sha,
            clock=guard.clock,
            deadline=guard.deadline,
        )
    guard.check()
    return manifest


def score_batches(model, features, audit, row, guard, count):
    q.require(
        features.shape == (count, 8) and features.dtype == np.float32,
        "Prepared feature shape/type",
    )
    scores = np.empty(count, np.float64)
    with torch.inference_mode():
        for start in range(0, count, 4096):
            stop = min(start + 4096, count)
            audit.inflight(row, "feature_read", stop - start)
            guard.check()
            x = np.array(features[start:stop], dtype=np.float32, order="C", copy=True)
            guard.check()
            audit.read(row, len(x))
            q.require(np.isfinite(x).all(), "Nonfinite frozen feature")
            audit.inflight(row, "native_score", stop - start)
            guard.check()
            value = model.score(x, feature_names=AGGREGATE_NAMES)
            guard.check()
            q.require(
                value.dtype == np.float64
                and value.shape == (len(x),)
                and np.isfinite(value).all()
                and (value >= 0).all(),
                "Finite nonnegative canonical FP64 SSE",
            )
            scores[start:stop] = value
            audit.scored(row, len(x))
            guard.check()
    q.require(
        row["batches"]
        == [4096] * (count // 4096) + ([count % 4096] if count % 4096 else []),
        "Complete canonical tail/batch accounting",
    )
    return scores


def arithmetic(background, signal):
    return dict(
        relative_acceptance=signal["efficiency"] / background["efficiency"]
        if background["accepted"]
        else None,
        selected_signal_fraction=signal["accepted"]
        / (signal["accepted"] + background["accepted"])
        if signal["accepted"] + background["accepted"]
        else None,
        scope="preregistered aggregate arithmetic;no ratioCI/significance/physical purity",
    )


def evaluate(root, spec, phase, directory, audit, guard):
    index = 0 if phase == "PCA" else 1
    entry, ref = spec["candidates"][index], spec["cached_background"][index]
    manifest = validate_prepared(root, spec, guard)
    constructor = audit.request(
        "candidate_constructor_provenance", 1, source=entry["model_path"]
    )
    guard.check()
    candidate = load_candidate(root, entry)
    validate_manifest(
        candidate, p.read(root / spec["original_store"]["path"] / "manifest.json")
    )
    guard.check()
    audit.read(constructor, 1)
    model = candidate["model"]
    before = core.parameter_hash(model)
    row = audit.request(
        "signal_model_evaluation",
        manifest["scientific"]["count"],
        source=q.PREPARED + "/event_features.npy",
    )
    guard.check()
    features = np.load(
        q.fixed(root, q.PREPARED + "/event_features.npy"),
        allow_pickle=False,
        mmap_mode="r",
    )
    guard.check()
    sig = score_batches(model, features, audit, row, guard, len(features))
    path = q.check_file(
        root,
        ref["path"],
        ref["file_byte_sha256"],
        clock=guard.clock,
        deadline=guard.deadline,
    )
    q.array_header(path, "<f8", ref["shape"])
    reuse = audit.request(
        "cached_background_numeric_reuse", ref["shape"][0], source=ref["path"]
    )
    guard.check()
    bg = np.load(path, allow_pickle=False)
    guard.check()
    audit.read(reuse, len(bg))
    q.require(
        bg.dtype == np.float64
        and bg.shape == tuple(ref["shape"])
        and np.isfinite(bg).all()
        and (bg >= 0).all(),
        "Cached finite nonnegative FP64 score vector",
    )
    metrics = evaluate_scores(
        bg, sig, fixed_fprs=[0.1, 0.05, 0.01, 0.001], fixed_tprs=[0.5, 0.8, 0.9]
    )
    guard.check()
    metrics["calibrated_thresholds"] = [
        dict(
            target_fpr=t["target_fpr"],
            threshold=t["threshold"],
            **at_threshold(bg, sig, t["threshold"]),
        )
        for t in entry["thresholds"]
    ]
    q.require(
        [point["background"]["accepted"] for point in metrics["calibrated_thresholds"]]
        == spec["calibrated_background_counts"][phase],
        "Shared background fixed-count gate discrepancy",
    )
    for point in metrics["calibrated_thresholds"]:
        point["preregistered_arithmetic"] = arithmetic(
            point["background"], point["signal"]
        )
    labels = np.r_[np.zeros(len(bg), np.uint8), np.ones(len(sig), np.uint8)]
    scores = np.r_[bg, sig]
    fpr, tpr, roc_thresholds = roc_curve(labels, scores, drop_intermediate=False)
    precision, recall, pr_thresholds = precision_recall_curve(labels, scores)
    guard.check()
    np.savez(
        directory / "curves.npz",
        fpr=fpr,
        tpr=tpr,
        roc_thresholds=roc_thresholds,
        precision=precision,
        recall=recall,
        pr_thresholds=pr_thresholds,
    )
    np.save(directory / "three-prong-scores.npy", sig, allow_pickle=False)
    after = core.parameter_hash(model)
    q.require(before == after, "Frozen parameter mutation")
    evaluation = dict(
        protocol="latenttrigger-evaluation-v1",
        model_scientific_sha256=entry["model_scientific_sha256"],
        calibration_scientific_sha256=entry["results_scientific_sha256"],
        new_signal_scientific_sha256=manifest["scientific_sha256"],
        reused_background_reference=ref,
        background_is_fresh_independent_measurement=False,
        metrics=metrics,
        parameters_before=before,
        parameters_after=after,
        owned_curves_file_byte_sha256=p.file_hash(directory / "curves.npz"),
        signal_scores_file_byte_sha256=p.file_hash(
            directory / "three-prong-scores.npy"
        ),
    )
    p.write(
        directory / "evaluation.json",
        dict(scientific=evaluation, scientific_sha256=p.digest(evaluation)),
        exclusive=True,
    )
    p.write(directory / "background-summary.json", score_summary(bg), exclusive=True)
    guard.check()
    return evaluation
