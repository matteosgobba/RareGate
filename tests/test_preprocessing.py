"""Synthetic Blosc HDF integration; no network or real dataset in CI."""

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import h5py
import hdf5plugin
import numpy as np
import pytest

from latenttrigger.data.acquisition import AcquisitionResult, Integrity
from latenttrigger.data.inspection import event_fingerprints
from latenttrigger.data.preprocessing import Inputs, build_store, main, prepare_inputs
from latenttrigger.data.processed import (
    ARRAY_DTYPES,
    ProcessedStore,
    StoreIntegrityError,
    content_hash,
    verify_store,
)


@pytest.fixture
def inputs(tmp_path):
    config = json.loads(
        (Path(__file__).parents[1] / "configs/data/lhco_rnd_v5.json").read_text()
    )
    counts = np.array([2, 4, 5, 384, 385, 700, 3, 2, 6, 8], dtype=np.uint16)
    codes = np.array([1, 1, 1, 2, 2, 3, 3, 4, 5, 5], dtype=np.uint8)
    labels = (codes == 5).astype(np.uint8)
    dev = np.zeros(10, dtype=bool)
    dev[[0, 3, 5]] = True
    rows = np.zeros((10, 2101), dtype=np.float64)
    rng = np.random.default_rng(17)
    for i, count in enumerate(counts):
        particles = np.column_stack(
            [
                np.arange(1, count + 1) * (i + 1),
                np.linspace(-1, 1, count),
                np.linspace(-2, 2, count),
            ]
        )
        rows[i, : count * 3] = particles[rng.permutation(count)].ravel()
    rows[:, 2100] = labels
    raw = tmp_path / "fixture.h5"
    with h5py.File(raw, "w") as handle:
        handle.create_dataset(
            "/df/block0_values", data=rows, chunks=(2, 2101), **hdf5plugin.Blosc()
        )
    sha = hashlib.sha256(raw.read_bytes()).hexdigest()
    md5 = hashlib.md5(raw.read_bytes(), usedforsecurity=False).hexdigest()
    config["source"]["dataset"] = "Synthetic LHCO-format test fixture"
    config["source"]["expected_size"] = raw.stat().st_size
    config["source"]["expected_checksum"] = md5
    config["source_integrity"] = {
        "file_size": raw.stat().st_size,
        "verified_checksum": md5,
        "sha256": sha,
    }
    names = {
        1: "train_background",
        2: "validation_selection_background",
        3: "validation_calibration_background",
        4: "test_background",
        5: "test_signal",
    }
    config["split"]["counts"] = {
        name: int((codes == code).sum()) for code, name in names.items()
    }
    config["split"]["counts"].update(
        {f"dev_{names[code]}": int((dev & (codes == code)).sum()) for code in (1, 2, 3)}
    )
    config_bytes = json.dumps(config, sort_keys=True).encode()
    return Inputs(
        raw,
        config_bytes,
        config,
        {"protocol": "synthetic-test-fixture", "seed": 1729},
        "synthetic",
        np.arange(10),
        labels,
        codes,
        counts,
        dev,
        event_fingerprints(rows[:, :2100].reshape(10, 700, 3)),
        "full",
    )


def dev_inputs(inputs):
    return replace(inputs, event_ids=np.flatnonzero(inputs.development), scope="dev")


def test_canonical_storage_reconstruction_features_and_schema(inputs, tmp_path):
    destination = tmp_path / "store"
    manifest = build_store(inputs, destination, chunk_rows=3)
    assert manifest["scientific"]["events"] == 10
    assert manifest["scientific"]["particles"] == inputs.multiplicities.sum()
    assert manifest["schema_version"] == 1
    assert (
        manifest["scientific"]["aggregate_channels"]
        == inputs.config["preprocessing"]["aggregates"]["channels"]
    )
    for name, dtype in ARRAY_DTYPES.items():
        assert (
            np.load(destination / f"{name}.npy", allow_pickle=False).dtype.str == dtype
        )
    with ProcessedStore(destination) as store:
        batch = store.read("validation_selection_background", slice(None))
        assert batch.labels is None
        np.testing.assert_array_equal(batch.event_ids, [3, 4])
        np.testing.assert_array_equal(np.diff(batch.offsets), [384, 385])
        assert batch.model_view().mask.sum() == 768
        assert batch.event_aggregates[1, 0] == 385
        assert batch.event_features.shape == (2, 8)
        with h5py.File(inputs.raw_path) as handle:
            original = handle["/df/block0_values"][4, :2100].reshape(700, 3)
        start, stop = batch.offsets[1:3]
        slots = batch.original_slots[start:stop]
        np.testing.assert_allclose(
            batch.particles[start:stop], original[slots].astype(np.float32)
        )
        assert (np.diff(batch.particles[start:stop, 0]) <= 0).all()


def test_independent_dev_stores_byte_identical_with_different_chunk_sizes(
    inputs, tmp_path
):
    inputs = dev_inputs(inputs)
    left, right = tmp_path / "left", tmp_path / "right"
    a = build_store(inputs, left, chunk_rows=1)
    b = build_store(inputs, right, chunk_rows=2)
    assert a["scientific_sha256"] == b["scientific_sha256"]
    for name in ARRAY_DTYPES:
        assert (left / f"{name}.npy").read_bytes() == (
            right / f"{name}.npy"
        ).read_bytes()
    with ProcessedStore(left) as x, ProcessedStore(right) as y:
        xview = x.read("validation_calibration_background", slice(None)).model_view()
        yview = y.read("validation_calibration_background", slice(None)).model_view()
        np.testing.assert_array_equal(xview.features, yview.features)
        np.testing.assert_array_equal(xview.mask, yview.mask)
        assert xview.n_original[0] == 700 and xview.n_retained[0] == 384


def test_verified_existing_store_reused_without_hdf_read(inputs, tmp_path, monkeypatch):
    destination = tmp_path / "store"
    a = build_store(inputs, destination)

    def fail(*args):
        raise AssertionError("Unexpected rebuild")

    monkeypatch.setattr("latenttrigger.data.preprocessing.open_raw", fail)
    b = build_store(inputs, destination)
    assert a["scientific_sha256"] == b["scientific_sha256"]


def test_corruption_requires_explicit_rebuild_and_old_bytes_retained(inputs, tmp_path):
    destination = tmp_path / "store"
    original = build_store(inputs, destination)
    file = destination / "particles.npy"
    with file.open("r+b") as stream:
        stream.seek(-1, 2)
        stream.write(b"X")
    corrupt = file.read_bytes()
    with pytest.raises(StoreIntegrityError, match="integrity mismatch"):
        verify_store(destination)
    with pytest.raises(StoreIntegrityError, match="--rebuild"):
        build_store(inputs, destination)
    fresh = build_store(inputs, destination, rebuild=True)
    assert fresh["scientific_sha256"] == original["scientific_sha256"]
    backups = list(tmp_path.glob("store.previous-*"))
    assert len(backups) == 1 and (backups[0] / "particles.npy").read_bytes() == corrupt


def test_failed_stage_does_not_promote_or_damage_existing(
    inputs, tmp_path, monkeypatch
):
    destination = tmp_path / "store"
    original = build_store(inputs, destination)

    def fail(*args):
        raise RuntimeError("Controlled write failure")

    monkeypatch.setattr("latenttrigger.data.preprocessing.physical_aggregates", fail)
    with pytest.raises(RuntimeError, match="Controlled"):
        build_store(inputs, destination, rebuild=True)
    assert (
        verify_store(destination)["scientific_sha256"] == original["scientific_sha256"]
    )
    assert not (tmp_path / ".store.partial").exists()
    assert not (tmp_path / ".store.lock").exists()


def test_incomplete_output_and_stale_lock_refused(inputs, tmp_path):
    destination = tmp_path / "store"
    destination.mkdir()
    with pytest.raises(StoreIntegrityError):
        verify_store(destination)
    (tmp_path / ".store.lock").touch()
    with pytest.raises(ValueError, match="Build lock"):
        build_store(inputs, destination, rebuild=True)


def test_manifest_and_dtype_corruption_checked(inputs, tmp_path):
    destination = tmp_path / "store"
    manifest = build_store(inputs, destination)
    features = destination / "event_features.npy"
    np.save(features, np.load(features, allow_pickle=False).astype(np.float64))
    record = manifest["scientific"]["files"][features.name]
    record.update(
        bytes=features.stat().st_size,
        sha256=hashlib.sha256(features.read_bytes()).hexdigest(),
        dtype="<f8",
    )
    manifest["scientific_sha256"] = content_hash(manifest["scientific"])
    (destination / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(StoreIntegrityError, match="Shape/dtype"):
        verify_store(destination)


def test_reader_embargo_explicit_labels_and_wrong_split_ids(inputs, tmp_path):
    destination = tmp_path / "store"
    build_store(inputs, destination)
    with ProcessedStore(destination) as store:
        with pytest.raises(ValueError, match="embargo"):
            store.read("test_signal", slice(None))
        with pytest.raises(ValueError, match="evaluation-only"):
            store.read("train_background", slice(0, 1), include_labels=True)
        with pytest.raises(ValueError, match="permitted"):
            store.read_ids("train_background", np.array([8]))
        with pytest.raises(ValueError, match="absent"):
            store.read_ids("train_background", np.array([100]))
        evaluation = store.read(
            "test_signal", slice(None), allow_test=True, include_labels=True
        )
        np.testing.assert_array_equal(evaluation.labels, [1, 1])
        assert evaluation.model_view().features.shape[-1] == 4
        assert evaluation.event_features.shape[-1] == 8
        assert all(
            batch.labels is None
            for batch in store.iter_batches("train_background", batch_size=2)
        )
        ids = np.concatenate(
            [b.event_ids for b in store.iter_batches("train_background", batch_size=2)]
        )
        np.testing.assert_array_equal(ids, [0, 1, 2])
        dev = store.read("train_background", slice(None), dev_only=True)
        np.testing.assert_array_equal(dev.event_ids, [0])
    with pytest.raises(ValueError, match="closed"):
        store.event_ids("train_background")


def test_split_count_mismatch_fails_without_regeneration(tmp_path, monkeypatch):
    config = json.loads(
        (Path(__file__).parents[1] / "configs/data/lhco_rnd_v5.json").read_text()
    )
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    integrity = Integrity(**config["source_integrity"])
    monkeypatch.setattr(
        "latenttrigger.data.preprocessing.acquire",
        lambda **kwargs: AcquisitionResult(tmp_path / "fake", integrity, False),
    )
    monkeypatch.setattr(
        "latenttrigger.data.preprocessing.verify_split_artifacts", lambda *args: None
    )
    report = {
        "source_integrity": config["source_integrity"],
        "counts": dict(config["split"]["counts"]),
        "seed": 1729,
        "protocol": "lhco-rd-v1",
    }
    report["counts"]["train_background"] += 1
    directory = tmp_path / "analysis/lhco-rd-v1"
    directory.mkdir(parents=True)
    (directory / "split-manifest.json").write_text(json.dumps(report))
    with pytest.raises(ValueError, match="membership counts"):
        prepare_inputs(tmp_path, path, "full")


def test_cli_requires_scope_and_verify_is_independent_of_source(
    inputs, tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr("sys.argv", ["preprocessing"])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    destination = tmp_path / "store"
    manifest = build_store(inputs, destination)
    monkeypatch.setattr("sys.argv", ["preprocessing", "--verify", str(destination)])
    main()
    assert manifest["scientific_sha256"] in capsys.readouterr().out


@pytest.mark.parametrize(
    "field,value", [("default_nmax", 128), ("split_identity_sha256", "wrong")]
)
def test_semantic_identity_checked_even_with_rehashed_manifest(
    inputs, tmp_path, field, value
):
    destination = tmp_path / "store"
    manifest = build_store(inputs, destination)
    manifest["scientific"][field] = value
    manifest["scientific_sha256"] = content_hash(manifest["scientific"])
    (destination / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(StoreIntegrityError, match="Feature/split identity"):
        verify_store(destination)


def test_disk_budget_checked_before_staging(inputs, tmp_path, monkeypatch):
    from collections import namedtuple

    usage = namedtuple("Usage", "total used free")
    monkeypatch.setattr(
        "latenttrigger.data.preprocessing.shutil.disk_usage",
        lambda _: usage(100, 99, 1),
    )
    with pytest.raises(OSError, match="Insufficient disk"):
        build_store(inputs, tmp_path / "store")
    assert not (tmp_path / "store").exists()
    assert not (tmp_path / ".store.partial").exists()
    assert not (tmp_path / ".store.lock").exists()
