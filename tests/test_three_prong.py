"""Self-contained three-prong HDF/compatibility/score/lifecycle refusal tests."""

import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import h5py
import numpy as np
import pytest
from test_frozen_cpu_benchmark import FakeGuard, sample

from raregate.benchmarks import protocol as p
from raregate.data.acquisition import IntegrityError, verify_file
from raregate.data.features import (
    Parameters,
    canonicalize,
    physical_aggregates,
    standardized_aggregates,
)
from raregate.data.inspection import AGGREGATE_NAMES, event_fingerprints
from raregate.data.metadata import DatasetSource
from raregate.evaluation import three_prong as c
from raregate.evaluation import three_prong_core as n
from raregate.evaluation import three_prong_protocol as q
from raregate.evaluation.guard import Guard, GuardError
from raregate.evaluation.metrics import evaluate_scores
from raregate.evaluation.three_prong_audit import Audit, exposure
from raregate.evaluation.three_prong_smoke import exercise, toy_spec
from raregate.models.autoencoder import CompactAutoencoder
from raregate.models.pca import PCAReconstruction


@pytest.fixture
def toy(tmp_path):
    spec, candidates = toy_spec(tmp_path)
    return tmp_path, spec, candidates


def hdf(tmp_path, width=2100, count=4):
    path = tmp_path / "encoding.h5"
    rows = np.zeros((count, width), np.float64)
    rows[:, :6] = [1, 0, 0, 1, 0, 1]
    if width == 2101:
        rows[:, 2100] = 1
    with h5py.File(path, "w") as handle:
        handle.create_dataset("/df/block0_values", data=rows)
        handle.create_dataset("/df/block0_items", data=np.arange(width))
        handle.create_dataset("/df/axis0", data=np.arange(width))
        handle.create_dataset("/df/axis1", data=np.arange(count))
    return path


@pytest.mark.parametrize("width", [2100, 2101])
def test_supported_fixed_schema_labels_separate(tmp_path, width):
    path = hdf(tmp_path, width)
    with h5py.File(path, "r") as handle:
        ds, w = n.hdf_layout(handle, 4, dict(encoding=dict(widths=[2100, 2101])))
        particles = n.raw_particles(ds[:], w)
        assert particles.shape == (4, 700, 3)
        assert physical_aggregates(canonicalize(particles).padded).shape == (4, 8)


@pytest.mark.parametrize(
    "change", ["count", "dtype", "width", "axis", "table", "mixed", "external"]
)
def test_unsupported_schema_refused_before_stream(tmp_path, change):
    path = hdf(tmp_path)
    with h5py.File(path, "a") as handle:
        if change == "count":
            count = 5
        else:
            count = 4
        if change in ("dtype", "width"):
            data = np.asarray(handle["/df/block0_values"])
            del handle["/df/block0_values"]
            handle.create_dataset(
                "/df/block0_values",
                data=data.astype(np.float32) if change == "dtype" else data[:, :8],
            )
        elif change == "axis":
            handle["/df/axis0"][0] = 8
        elif change == "table":
            handle.create_dataset("/df/table", data=np.zeros(4))
        elif change == "mixed":
            handle.create_dataset("/df/block1_values", data=np.zeros((4, 1)))
        elif change == "external":
            del handle["/df/block0_values"]
            handle["/df/block0_values"] = h5py.ExternalLink("unapproved.h5", "/values")
        with pytest.raises(ValueError):
            n.hdf_layout(handle, count, dict(encoding=dict(widths=[2100, 2101])))


@pytest.mark.parametrize(
    "change", ["negative", "nan", "padding", "nontrailing", "empty", "label"]
)
def test_physical_structure_and_signal_truth_refused(change):
    rows = np.zeros((1, 2101), np.float64)
    rows[0, :6] = [1, 0, 0, 1, 0, 1]
    rows[0, 2100] = 1
    if change == "negative":
        rows[0, 0] = -1
    if change == "nan":
        rows[0, 1] = np.nan
    if change == "padding":
        rows[0, 6:9] = [0, 1, 0]
    if change == "nontrailing":
        rows[0, 9] = 1
    if change == "empty":
        rows[0, :2100] = 0
    if change == "label":
        rows[0, 2100] = 0
    with pytest.raises(ValueError):
        canonicalize(n.raw_particles(rows, 2101))


def test_frozen_full_particle_transform_and_unit_contract(toy):
    root, spec, _ = toy
    config = p.read(root / "transform.json")
    params = Parameters.from_config(config)
    particles = np.zeros((1, 700, 3), np.float64)
    particles[0, :, 0] = np.arange(1, 701)
    particles[0, :, 2] = 2 * np.pi
    canonical = canonicalize(particles)
    observed = physical_aggregates(canonical.padded)
    actual = standardized_aggregates(observed, params)
    expected = observed.copy()
    expected[:, [0, 1, 2, 7]] = np.log1p(expected[:, [0, 1, 2, 7]])
    expected = ((expected - params.aggregate_mean) / params.aggregate_std).astype(
        np.float32
    )
    assert np.array_equal(actual, expected) and observed[0, 0] == 700
    assert (canonical.padded[:, :, 2] == 0).all()
    config["preprocessing"]["object_view"]["pt_reference_GeV"] = 1000
    with pytest.raises(ValueError):
        Parameters.from_config(config)
    assert spec["features"] == list(AGGREGATE_NAMES)


@pytest.mark.parametrize("change", ["size", "checksum"])
def test_raw_integrity_fail_closed(tmp_path, change):
    import hashlib

    path = tmp_path / "source"
    path.write_bytes(b"toy-only")
    spec = DatasetSource(
        "toy",
        "v5",
        6466204,
        "toy",
        path.name,
        "https://example.invalid",
        8,
        hashlib.md5(b"toy-only", usedforsecurity=False).hexdigest(),
    )
    if change == "size":
        path.write_bytes(b"bad")
    else:
        path.write_bytes(b"bad-only")
    with pytest.raises(IntegrityError):
        verify_file(path, spec)


@pytest.mark.parametrize(
    "field", ["version", "expected_size", "expected_checksum", "url"]
)
def test_protocol_source_mutation_refused(tmp_path, field):
    spec = p.read(p.ROOT / q.CONFIG)
    spec["source"][field] = "wrong"
    path = tmp_path / q.CONFIG
    path.parent.mkdir(parents=True)
    p.write(path, spec)
    with pytest.raises(ValueError, match="strict protocol"):
        q.load(tmp_path)


def test_exact_fingerprint_excludes_labels_slots_and_matches_original_algorithm():
    particles = np.zeros((2, 700, 3), np.float64)
    particles[:, :2] = [[2, 0, 1], [1, 0, -1]]
    particles[1, :2] = particles[1, :2][::-1]
    fp = event_fingerprints(particles)
    assert fp[0] == fp[1]
    result = n.check_overlap(fp, np.asarray([fp[0]], dtype="V32"))
    assert result == dict(
        within_source_duplicates=1,
        original_overlap_count=1,
        all_original_roles_checked=True,
    )


@pytest.mark.parametrize(
    "change",
    [
        "transform",
        "features",
        "dtype",
        "count",
        "training",
        "duplicate",
        "overlap",
        "source",
        "sha",
    ],
)
def test_new_source_compatibility_refuses_alias_or_changed_contract(toy, change):
    root, spec, _ = toy
    directory = root / q.OUTPUT / "prepare"
    directory.mkdir()
    manifest = n.prepare(
        root, spec, directory, Audit(directory / "access.json", {}), FakeGuard()
    )
    science = manifest["scientific"]
    if change == "transform":
        science["transform"] = dict(path="other_scalers")
    elif change == "features":
        science["features"] = science["features"][::-1]
    elif change == "dtype":
        science["dtype"] = "<f8"
    elif change == "count":
        science["count"] = 3
    elif change == "training":
        science["original_training_scientific_sha256"] = "new-signal-not-training"
    elif change == "duplicate":
        science["within_source_duplicates"] = 1
    elif change == "overlap":
        science["original_overlap_count"] = 1
    elif change == "source":
        science["source"] = spec["original_store"]
    elif change == "sha":
        science["actual_raw_sha256"] = "invented"
    manifest["scientific_sha256"] = p.digest(science)
    with pytest.raises(ValueError):
        q.compatibility(manifest, spec)


@pytest.mark.parametrize("change", ["duplicate", "overlap", "row_axis"])
def test_custody_failure_preserves_evidence_without_scoring(toy, change):
    root, spec, _ = toy
    raw = root / "toy.h5"
    if change in ("duplicate", "row_axis"):
        with h5py.File(raw, "a") as handle:
            if change == "duplicate":
                handle["/df/block0_values"][1] = handle["/df/block0_values"][0]
            else:
                handle["/df/axis1"][1] = 0
        import hashlib

        b = raw.read_bytes()
        spec["source"]["expected_size"] = len(b)
        spec["source"]["expected_checksum"] = hashlib.md5(
            b, usedforsecurity=False
        ).hexdigest()
        p.write(
            root / q.OUTPUT / "acquire/acquisition.json",
            dict(path=raw.name, integrity=dict(sha256=hashlib.sha256(b).hexdigest())),
        )
    else:
        with h5py.File(raw, "r") as handle:
            fp = event_fingerprints(
                n.raw_particles(handle["/df/block0_values"][:], 2100)
            )
        original = np.zeros(8, dtype="V32")
        original[0] = fp[0]
        np.save(root / "original/fingerprints.npy", original, allow_pickle=False)
        spec["original_fingerprints"]["sha256"] = p.file_hash(
            root / "original/fingerprints.npy"
        )
    directory = root / q.OUTPUT / "prepare"
    directory.mkdir()
    audit = Audit(directory / "access.json", {})
    with pytest.raises(ValueError):
        n.prepare(root, spec, directory, audit, FakeGuard())
    assert not (root / q.PREPARED / "manifest.json").exists()
    assert exposure(directory / "access.json")["new_signal_model_accessed"] is False
    if change != "row_axis":
        assert (directory / "overlap.json").exists()


@pytest.mark.parametrize("change", ["dtype", "count", "hash", "negative", "nonfinite"])
def test_cached_score_wrong_identity_count_type_or_domain(tmp_path, change):
    values = np.arange(5, dtype=np.float64)
    if change == "dtype":
        values = values.astype(np.float32)
    if change == "negative":
        values[0] = -1
    if change == "nonfinite":
        values[0] = np.nan
    path = tmp_path / "cached.npy"
    np.save(path, values, allow_pickle=False)
    ref = dict(
        bytes=path.stat().st_size,
        file_byte_sha256=p.file_hash(path),
        shape=[6 if change == "count" else 5],
    )
    if change == "hash":
        ref["file_byte_sha256"] = "wrong"
    with pytest.raises(ValueError):
        n.cached_scores(path, ref)


@pytest.mark.parametrize("model_kind", ["PCA", "AE"])
def test_actual_native_full_tail_and_metric_equivalence(tmp_path, model_kind):
    import torch

    x = np.tile(np.arange(8, dtype=np.float32) / 16, (100000, 1))
    if model_kind == "PCA":
        model = PCAReconstruction(
            np.zeros(8), np.eye(8), np.ones(8), np.ones(8), 6, 0.95, 16
        )
    else:
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(1729)
            model = CompactAutoencoder().eval()
    audit = Audit(tmp_path / "access.json", {})
    row = audit.request("signal_model_evaluation", 100000)
    scores = n.score_batches(model, x, audit, row, FakeGuard(), 100000)
    assert row["batches"] == [4096] * 24 + [1696] and row["confirmed_scored"] == 100000
    for start in range(0, 100000, 4096):
        y = x[start : start + 4096]
        recon = (
            model.reconstruct(y, feature_names=AGGREGATE_NAMES)
            if model_kind == "PCA"
            else model(torch.from_numpy(y)).detach().numpy()
        )
        expected = ((y.astype(np.float64) - recon.astype(np.float64)) ** 2).sum(axis=1)
        assert np.array_equal(scores[start : start + len(y)], expected)
    bg = np.asarray([0, 0.5, 1, 2, 4], dtype=np.float64)
    expected = evaluate_scores(
        bg, scores, fixed_fprs=[0.1, 0.05, 0.01, 0.001], fixed_tprs=[0.5, 0.8, 0.9]
    )
    assert expected["background_total"] == 5 and expected["signal_total"] == 100000


def test_real_toy_prepare_both_candidates_and_unchanged_metrics(tmp_path):
    result = exercise(tmp_path, FakeGuard())
    for phase, evaluation in zip(("PCA", "AE"), result["evaluations"], strict=True):
        bg = np.load(
            tmp_path / (evaluation["reused_background_reference"]["path"]),
            allow_pickle=False,
        )
        sig = np.load(
            tmp_path / q.OUTPUT / phase / "three-prong-scores.npy", allow_pickle=False
        )
        expected = evaluate_scores(
            bg, sig, fixed_fprs=[0.1, 0.05, 0.01, 0.001], fixed_tprs=[0.5, 0.8, 0.9]
        )
        assert all(evaluation["metrics"][k] == v for k, v in expected.items())
        for point in evaluation["metrics"]["calibrated_thresholds"]:
            t = point["threshold"]
            assert point["background"]["accepted"] == int((bg > t).sum()) and point[
                "signal"
            ]["accepted"] == int((sig > t).sum())
    assert (tmp_path / q.OUTPUT / "calibrated-operating-points.csv").exists()


def test_durable_inflight_access_survives_interrupted_score(tmp_path):
    class Broken:
        def score(self, x, **kwargs):
            doc = p.read(tmp_path / "access.json")
            assert doc["records"][0]["inflight"]["kind"] == "score"
            raise KeyboardInterrupt("interrupted")

    audit = Audit(tmp_path / "access.json", {})
    row = audit.request("signal_model_evaluation", 4)
    with pytest.raises(KeyboardInterrupt):
        n.score_batches(
            Broken(), np.ones((4, 8), np.float32), audit, row, FakeGuard(), 4
        )
    audit.finish("failed", "interrupt")
    state = exposure(tmp_path / "access.json")
    assert (
        state["new_signal_model_accessed"]
        and state["potential_inflight"]
        and state["signal_scored_presentations"] == 0
    )


def test_unique_reservation_and_consumed_refusal(tmp_path, monkeypatch):
    for path in (q.ACCEPTANCE, q.CONSENT, q.CONFIG):
        f = tmp_path / path
        f.parent.mkdir(parents=True, exist_ok=True)
        p.write(f, {})
    monkeypatch.setattr(q, "source_map", lambda root: {})

    def reserve():
        try:
            c.reserve(tmp_path, {})
        except (ValueError, FileExistsError):
            return False
        return True

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(lambda _: reserve(), range(2))) == 1
    with pytest.raises(ValueError):
        c.namespace(tmp_path)


def test_failed_first_stage_prevents_dependents_and_remains_consumed(
    tmp_path, monkeypatch
):
    for path in (q.ACCEPTANCE, q.CONSENT, q.CONFIG):
        f = tmp_path / path
        f.parent.mkdir(parents=True, exist_ok=True)
        p.write(f, {})
    monkeypatch.setattr(q, "source_map", lambda root: {})
    monkeypatch.setattr(q, "authorization", lambda *args: ({}, {}))
    monkeypatch.setattr(
        q,
        "load",
        lambda root: dict(
            limits=dict(acquire_seconds=300),
            runtime=dict(thread_environment_before_imports={}),
        ),
    )
    monkeypatch.setattr(c, "parent_check", lambda **kwargs: 0)
    monkeypatch.setattr(
        c, "sys", SimpleNamespace(platform="darwin", executable=sys.executable)
    )
    calls = []

    def fail(*args, **kwargs):
        calls.append(args[0])
        return dict(
            parent_confirms_normal_exit=False,
            child_reaped=True,
            within_deadline=True,
            returncode=-15,
        )

    monkeypatch.setattr(c, "supervise", fail)
    assert c.run(tmp_path, allow_test=True, plan_sha256="synthetic") == 1
    assert (
        len(calls) == 1
        and p.read(tmp_path / q.OUTPUT / "workflow.json")["status"]
        == "failed_consumed_no_retry"
    )
    assert (
        c.run(tmp_path, allow_test=True, plan_sha256="synthetic") == 1
        and len(calls) == 1
    )


@pytest.mark.parametrize(
    "change", ["rss", "native", "pressure", "accounting", "deadline"]
)
def test_guard_resource_deadline_failures_latched(change):
    values = sample()
    if change == "rss":
        values["peak_rss_bytes"] = 6 * 2**30 + 1
    elif change == "native":
        values["native_heap_reserved_bytes"] = 512 * 2**20 + 1
    elif change == "pressure":
        values["pressure_dispatch_flags"] = 4
        values["pressure_errno"] = None
    elif change == "accounting":
        values["peak_rss_bytes"] = None
    guard = Guard(
        0 if change == "deadline" else time.monotonic() + 5,
        probe=lambda: values,
        notify=False,
    )
    with pytest.raises(GuardError):
        guard.check()
    assert guard.error
    guard.close()
    assert not guard.report()["owned_thread_alive"]


def test_new_controller_imports_stdlib_only_in_fresh_parent(tmp_path):
    code = "import sys;from raregate.evaluation import three_prong;assert not any(x in sys.modules for x in ('numpy','torch','h5py','sklearn','onnx','onnxruntime'))"
    subprocess.run([sys.executable, "-c", code], check=True, timeout=10)


def test_body_complete_hang_is_terminated_reaped_without_success(tmp_path):
    log = tmp_path / "hang.log"
    result = tmp_path / "dispatch.json"
    body = tmp_path / "body.json"
    child = f"from pathlib import Path;import time;Path({str(body)!r}).write_text('body_complete_awaiting_exit');time.sleep(20)"
    # Resource admission is a fixture; process exit, deadlines and reaping are real.
    code = f"""
import json
import os
import sys
import time
from pathlib import Path
from raregate.evaluation import guarded

guarded.parent_check = lambda **kwargs: 1
dispatch = guarded.supervise(
    [sys.executable, '-c', {child!r}],
    Path({str(log)!r}),
    root=Path({str(tmp_path)!r}),
    environment=dict(os.environ),
    stage_seconds=2.5,
    whole_deadline=time.monotonic() + 5,
)
Path({str(result)!r}).write_text(json.dumps(dispatch))
"""
    subprocess.run([sys.executable, "-c", code], check=True, timeout=10)
    d = p.read(result)
    assert (
        body.exists()
        and d["child_reaped"]
        and not d["parent_confirms_normal_exit"]
        and d["returncode"] != 0
        and d["within_deadline"]
    )


def test_unsupported_platform_refused_before_reservation(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(c, "parent_check", lambda **kwargs: 1)
    monkeypatch.setattr(c, "sys", SimpleNamespace(platform="linux"))
    assert c.run(tmp_path, allow_test=True, plan_sha256="synthetic") == 1
    assert (
        "Supported Darwin primary process accounting required"
        in capsys.readouterr().out
    )
    assert not (tmp_path / q.OUTPUT).exists()


def test_human_consent_refused_before_real_reservation(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="human consent"):
        q.authorization(tmp_path, False, None)
    current = dict(authorization_covers=["one_pinned_payload_acquisition"])
    monkeypatch.setattr(q, "plan", lambda root: current)
    (tmp_path / "data").mkdir()
    p.write(tmp_path / q.PLAN, current)
    with pytest.raises(FileNotFoundError):
        q.authorization(tmp_path, True, p.digest(current))
    assert not (tmp_path / q.OUTPUT).exists()


@pytest.mark.parametrize(
    "change", ["returncode", "normal_exit", "cleanup", "resource", "missing_output"]
)
def test_parent_never_promotes_complete_body_with_failed_lifecycle(
    tmp_path, monkeypatch, change
):
    phase = "consolidate"
    base = tmp_path / q.OUTPUT
    directory = base / phase
    directory.mkdir(parents=True)
    p.write(base / (phase + "-grant.json"), {})
    p.write(base / "comparison.json", {})
    (base / "calibrated-operating-points.csv").write_text("synthetic\n")
    p.write(directory / "access.json", {})
    paths = [
        q.OUTPUT + "/comparison.json",
        q.OUTPUT + "/calibrated-operating-points.csv",
        q.OUTPUT + "/consolidate/access.json",
    ]
    result = dict(
        status="body_complete_awaiting_exit",
        phase=phase,
        source_file_sha256={},
        protocol_canonical_JSON_sha256=q.HASH,
        grant_file_byte_sha256=p.file_hash(base / (phase + "-grant.json")),
        optimizer_updates=0,
        new_original_background_forward_calls=0,
        resources=dict(
            latched_error=None,
            owned_thread_alive=False,
            peak_rss_bytes=1,
            native_heap_reserved_bytes=1,
        ),
        threads_before={},
        threads_after={},
        timings=dict(cleanup_seconds=0),
        exposure=dict(potential_inflight=False),
        output_file_byte_sha256={path: p.file_hash(tmp_path / path) for path in paths},
    )
    dispatch = dict(
        parent_confirms_normal_exit=True,
        child_reaped=True,
        within_deadline=True,
        returncode=0,
        parent_error=None,
    )
    monkeypatch.setattr(q, "source_map", lambda root: {})
    p.write(directory / "receipt.json", result)
    reservation = dict(source_file_sha256={})
    assert (
        c.accept_stage(tmp_path, phase, result, dispatch, reservation)["status"]
        == "parent_accepted"
    )
    if change == "returncode":
        dispatch["returncode"] = -15
    elif change == "normal_exit":
        dispatch["parent_confirms_normal_exit"] = False
    elif change == "cleanup":
        result["timings"]["cleanup_seconds"] = 3
    elif change == "resource":
        result["resources"]["latched_error"] = "cap"
    elif change == "missing_output":
        result["output_file_byte_sha256"].pop(paths[0])
    assert (
        c.accept_stage(tmp_path, phase, result, dispatch, reservation)["status"]
        == "parent_rejected"
    )


@pytest.mark.parametrize("pressure", [1, 2, None])
def test_normal_warn_unknown_pressure_scopes(pressure):
    values = sample()
    values["pressure_dispatch_flags"] = pressure
    values["pressure_errno"] = 1 if pressure is None else None
    guard = Guard(time.monotonic() + 5, probe=lambda: values, notify=False)
    guard.check()
    guard.close()
    assert not guard.error and sum(guard.report()["pressure_counts"].values()) == 1
