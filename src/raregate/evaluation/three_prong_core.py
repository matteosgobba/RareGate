"""Streaming source custody and isolated frozen native signal evaluation."""

import numpy as np
import torch

from raregate.benchmarks import core
from raregate.benchmarks import protocol as p
from raregate.data.analysis import open_raw
from raregate.data.features import (
    Parameters,
    canonicalize,
    physical_aggregates,
    standardized_aggregates,
)
from raregate.data.inspection import AGGREGATE_NAMES, event_fingerprints
from raregate.evaluation import three_prong_protocol as q
from raregate.evaluation.guarded_core import load_candidate, validate_manifest
from raregate.evaluation.metrics import (
    at_threshold,
    evaluate_scores,
    score_summary,
)


def hdf_layout(handle, count, spec):
    """Support only documented pandas fixed single FP64 numeric block; fail closed."""
    import h5py

    paths = ("/df/block0_values", "/df/block0_items", "/df/axis0", "/df/axis1")
    q.require("/df/table" not in handle, "Pandas table encoding not supported")
    q.require(
        "/df" in handle and set(handle["/df"]) == {p.rsplit("/", 1)[1] for p in paths},
        "Mixed/unknown pandas blocks refused",
    )
    for path in paths:
        q.require(
            isinstance(handle.get(path, getlink=True), h5py.HardLink),
            "External/soft HDF links refused",
        )
        ds = handle[path]
        q.require(
            isinstance(ds, h5py.Dataset) and not ds.is_virtual and not ds.external,
            "External/virtual/non-dataset HDF refused",
        )
    ds = handle[paths[0]]
    q.require(
        ds.ndim == 2
        and ds.shape[0] == count
        and ds.shape[1] in spec["encoding"]["widths"]
        and ds.dtype == np.dtype("float64"),
        "Unsupported HDF shape/count/dtype",
    )
    width = ds.shape[1]
    for path in paths[1:3]:
        axis = handle[path]
        q.require(
            axis.shape == (width,)
            and axis.dtype.kind in "iu"
            and np.array_equal(axis[:], np.arange(width)),
            "Unknown HDF column definitions/order",
        )
    q.require(
        handle["/df/axis1"].shape == (count,)
        and handle["/df/axis1"].dtype.kind in "iu",
        "Source row-axis encoding",
    )
    return ds, width


def raw_particles(rows, width):
    q.require(
        rows.ndim == 2
        and rows.shape[1] == width
        and width in (2100, 2101)
        and rows.dtype == np.float64,
        "Particle row encoding",
    )
    if width == 2101:
        q.require(np.all(rows[:, 2100] == 1), "Declared signal label mismatch")
    return rows[:, :2100].reshape(-1, 700, 3)


def check_overlap(new, original):
    q.require(
        new.dtype == original.dtype == np.dtype("V32")
        and new.ndim == original.ndim == 1,
        "Fingerprint dtype/shape",
    )
    duplicate = len(new) - len(np.unique(new))
    overlap = len(np.intersect1d(new, original))
    return dict(
        within_source_duplicates=int(duplicate),
        original_overlap_count=int(overlap),
        all_original_roles_checked=True,
    )


def prepare(root, spec, directory, audit, guard):
    from raregate.data.acquisition import verify_file
    from raregate.data.metadata import DatasetSource

    count = spec["source"]["publisher_expected_events"]
    acquired = p.read(root / q.OUTPUT / "acquire/acquisition.json")
    source = DatasetSource(
        **{
            k: v
            for k, v in spec["source"].items()
            if k not in ("publisher_expected_events", "role", "local_payload_sha256")
        }
    )
    raw = q.fixed(root, acquired["path"])
    row = audit.request("raw_custody", count)
    integrity = verify_file(raw, source)
    q.require(
        integrity.sha256 == acquired["integrity"]["sha256"],
        "Acquired raw bytes changed",
    )
    params = Parameters.from_config(p.read(root / spec["transform"]["path"]))
    original_ref = spec["original_fingerprints"]
    original_row = audit.request(
        "original_fingerprint_integrity", original_ref["shape"][0]
    )
    guard.boundary("original_fingerprint_integrity_only")
    path = q.check_file(root, original_ref["path"], original_ref["sha256"])
    q.require(
        path.stat().st_size == original_ref["bytes"], "Original fingerprint bytes"
    )
    q.array_header(path, "|V32", original_ref["shape"])
    original = np.load(path, allow_pickle=False, mmap_mode="r")
    q.require(
        original.shape == tuple(original_ref["shape"])
        and original.dtype == np.dtype("V32"),
        "Original all-role registry",
    )
    audit.read(original_row, len(original))
    preparation = audit.request("signal_preparation", count)
    prepared = q.fixed(root, q.PREPARED)
    prepared.mkdir(parents=True, exist_ok=False)
    features = np.lib.format.open_memmap(
        prepared / "event_features.npy", mode="w+", dtype="<f4", shape=(count, 8)
    )
    fingerprints = np.empty(count, dtype="V32")
    label_provenance = None
    with open_raw(raw) as handle:
        dataset, width = hdf_layout(handle, count, spec)
        label_provenance = (
            "verified_all_last_column_labels_1"
            if width == 2101
            else "no_label_column;publisher_declared_signal_only_not_independently_proven"
        )
        for start in range(0, count, spec["limits"]["chunk_rows"]):
            stop = min(start + spec["limits"]["chunk_rows"], count)
            audit.inflight(row, "raw_read", stop - start)
            guard.check()
            rows = dataset[start:stop]
            q.require(
                np.array_equal(handle["/df/axis1"][start:stop], np.arange(start, stop)),
                "Raw source-order mismatch",
            )
            particles = raw_particles(rows, width)
            chunk = canonicalize(particles)
            fingerprints[start:stop] = event_fingerprints(particles)
            x = standardized_aggregates(physical_aggregates(chunk.padded), params)
            q.require(
                x.dtype == np.float32
                and x.shape == (stop - start, 8)
                and np.isfinite(x).all(),
                "Frozen feature preparation",
            )
            features[start:stop] = x
            audit.read(row, stop - start)
            audit.read(preparation, stop - start)
            guard.check()
    features.flush()
    del features
    guard.boundary("complete_exact_overlap")
    overlap = check_overlap(fingerprints, original)
    p.write(directory / "overlap.json", overlap, exclusive=True)
    q.require(
        overlap["within_source_duplicates"] == overlap["original_overlap_count"] == 0,
        "Exact duplicates/overlap; no favorable subset or scoring",
    )
    np.save(prepared / "fingerprints.npy", fingerprints, allow_pickle=False)
    science = dict(
        source=spec["source"],
        actual_raw_sha256=integrity.sha256,
        transform=spec["transform"],
        features=spec["features"],
        dtype="<f4",
        count=count,
        label_provenance=label_provenance,
        original_training_scientific_sha256=spec["original_store"]["scientific_sha256"],
        original_fingerprint_reference=original_ref,
        cached_background=spec["cached_background"],
        source_order="all_rows_0_to_N_minus_1_no_selection",
        **overlap,
        output_file_byte_sha256={
            f.name: p.file_hash(f) for f in prepared.iterdir() if f.is_file()
        },
    )
    manifest = dict(scientific=science, scientific_sha256=p.digest(science))
    q.compatibility(manifest, spec)
    p.write(prepared / "manifest.json", manifest, exclusive=True)
    return manifest


def validate_prepared(root, spec):
    base = q.fixed(root, q.PREPARED)
    manifest = p.read(base / "manifest.json")
    science = q.compatibility(manifest, spec)
    acquired = p.read(root / q.OUTPUT / "acquire/acquisition.json")
    q.require(
        science["actual_raw_sha256"] == acquired["integrity"]["sha256"],
        "Raw/feature custody binding",
    )
    for filename, digest in science["output_file_byte_sha256"].items():
        q.require(
            filename in ("event_features.npy", "fingerprints.npy"),
            "Unknown prepared payload",
        )
        q.check_file(root, q.PREPARED + "/" + filename, digest)
    q.require(
        set(science["output_file_byte_sha256"])
        == {"event_features.npy", "fingerprints.npy"},
        "Complete preparation outputs",
    )
    return manifest


def score_batches(model, features, audit, row, guard, count):
    q.require(
        features.shape == (count, 8) and features.dtype == np.float32,
        "Signal feature shape/dtype/count",
    )
    scores = np.empty(count, np.float64)
    with torch.inference_mode():
        for start in range(0, count, 4096):
            stop = min(start + 4096, count)
            audit.inflight(row, "feature_read", stop - start)
            guard.check()
            x = np.array(features[start:stop], dtype=np.float32, order="C", copy=True)
            audit.read(row, stop - start)
            q.require(np.isfinite(x).all(), "Nonfinite signal features")
            audit.inflight(row, "score", stop - start)
            guard.check()
            value = model.score(x, feature_names=AGGREGATE_NAMES)
            q.require(
                value.dtype == np.float64
                and value.shape == (stop - start,)
                and np.isfinite(value).all()
                and (value >= 0).all(),
                "Canonical finite FP64 SSE",
            )
            scores[start:stop] = value
            audit.scored(row, stop - start)
            guard.check()
    return scores


def cached_scores(path, reference):
    q.require(
        p.file_hash(path) == reference["file_byte_sha256"]
        and path.stat().st_size == reference["bytes"],
        "Cached score identity/size before numeric reuse",
    )
    q.array_header(path, "<f8", [reference["shape"][0]])
    scores = np.load(path, allow_pickle=False, mmap_mode="r")
    q.require(
        scores.shape == tuple(reference["shape"])
        and scores.dtype == np.float64
        and np.isfinite(scores).all()
        and (scores >= 0).all(),
        "Cached score count/dtype/finite SSE",
    )
    return scores


def evaluate(root, spec, phase, directory, audit, guard):
    index = 0 if phase == "PCA" else 1
    entry, ref = spec["candidates"][index], spec["cached_background"][index]
    manifest = validate_prepared(root, spec)
    candidate = load_candidate(root, entry)
    # Original validators apply to the genuine ORIGINAL training manifest only.
    validate_manifest(
        candidate, p.read(root / spec["original_store"]["path"] / "manifest.json")
    )
    model = candidate["model"]
    before = core.parameter_hash(model)
    row = audit.request(
        "signal_model_evaluation", spec["source"]["publisher_expected_events"]
    )
    features = np.load(
        q.fixed(root, q.PREPARED + "/event_features.npy"),
        allow_pickle=False,
        mmap_mode="r",
    )
    sig = score_batches(model, features, audit, row, guard, len(features))
    reuse = audit.request("cached_background_numeric_reuse", 150471)
    guard.boundary("cached_background_reuse_not_forward")
    bg = cached_scores(q.fixed(root, ref["path"]), ref)
    audit.read(reuse, len(bg))
    metrics = evaluate_scores(
        bg, sig, fixed_fprs=[0.1, 0.05, 0.01, 0.001], fixed_tprs=[0.5, 0.8, 0.9]
    )
    metrics["calibrated_thresholds"] = [
        dict(
            target_fpr=t["target_fpr"],
            threshold=t["threshold"],
            **at_threshold(bg, sig, t["threshold"]),
        )
        for t in entry["thresholds"]
    ]
    for point in metrics["calibrated_thresholds"]:
        b, s = point["background"], point["signal"]
        point["descriptive_post_evaluation_arithmetic"] = dict(
            relative_acceptance=s["efficiency"] / b["efficiency"]
            if b["accepted"]
            else None,
            selected_signal_fraction=s["accepted"] / (s["accepted"] + b["accepted"])
            if s["accepted"] + b["accepted"]
            else None,
            scope="accepted aggregate count arithmetic;no ratio uncertainty/significance/physical purity",
        )
    evaluation = dict(
        protocol="latenttrigger-evaluation-v1",
        model_scientific_sha256=entry["model_scientific_sha256"],
        calibration_scientific_sha256=entry["results_scientific_sha256"],
        new_signal_scientific_sha256=manifest["scientific_sha256"],
        reused_background_reference=ref,
        background_is_fresh_independent_measurement=False,
        metrics=metrics,
    )
    q.require(before == core.parameter_hash(model), "Frozen parameter mutation")
    p.write(
        directory / "evaluation.json",
        dict(scientific=evaluation, scientific_sha256=p.digest(evaluation)),
        exclusive=True,
    )
    p.write(directory / "background-summary.json", score_summary(bg), exclusive=True)
    np.save(directory / "three-prong-scores.npy", sig, allow_pickle=False)
    return evaluation
