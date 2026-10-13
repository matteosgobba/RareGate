"""Only synthetic memberships/HDF/event arrays; no operational golden/model access."""

import hashlib
from types import SimpleNamespace

import h5py
import numpy as np
import pytest

from latenttrigger.benchmarks import development_raw_adapter as a
from latenttrigger.benchmarks import development_raw_membership as m
from latenttrigger.benchmarks import development_raw_metadata as md
from latenttrigger.benchmarks import development_raw_planning as plan
from latenttrigger.benchmarks import development_raw_protocol as p
from latenttrigger.benchmarks.development_raw_synthetic import parameters
from latenttrigger.data.features import (
    canonicalize,
    physical_aggregates,
    standardized_aggregates,
)


def approval():
    ids = np.arange(1024, dtype="<i8") * 3
    return a.Approval(ids, hashlib.sha256(ids.tobytes()).hexdigest())


def raw_rows(n):
    raw = np.zeros((n, 2101), dtype="<f8")
    raw[:, 0:3] = [10.0, 0.4, 0.5]
    raw[:, 3:6] = [3.0, -0.2, -0.3]
    return raw


class Spy:
    shape = (1100000, 2101)
    ndim = 2
    dtype = np.dtype("<f8")
    file = SimpleNamespace(filename="/tmp/task0039-generated-fixture.h5")

    def __init__(self):
        self.requests = []

    def __getitem__(self, index):
        selected, cols = index
        assert cols == slice(None)
        ids = (
            list(range(selected.start, selected.stop))
            if isinstance(selected, slice)
            else selected
        )
        self.requests.append(ids)
        rows = raw_rows(len(ids))
        rows[:, 0] = np.array(ids) + 1
        return rows


@pytest.mark.parametrize("b", plan.BATCHES)
def test_exact_selected_rows_no_neighbors_source_sentinels(b):
    approved = approval()
    request = approved.ids[:b]
    spy = Spy()
    raw = a.selected_read(spy, request, approved)
    assert spy.requests == [request.tolist()]
    assert raw[:, 0].tolist() == (request + 1).tolist() and raw.shape == (b, 2101)
    if b > 1:
        assert 1 not in spy.requests[0]


@pytest.mark.parametrize(
    "bad",
    ("adjacent", "unordered", "duplicate", "empty", "float", "oversize", "outside"),
)
def test_reject_before_provider(bad):
    approved = approval()
    spy = Spy()
    request = approved.ids[:8].copy()
    if bad == "adjacent":
        request[1] += 1
    if bad == "unordered":
        request = request[::-1].copy()
    if bad == "duplicate":
        request[1] = request[0]
    if bad == "empty":
        request = np.array([], dtype="<i8")
    if bad == "float":
        request = request.astype(float)
    if bad == "oversize":
        request = approved.ids[:129]
    if bad == "outside":
        request[-1] = 1100000
    with pytest.raises(ValueError):
        a.selected_read(spy, request, approved)
    assert not spy.requests


def test_contiguous_slice_only_exact_request_and_operational_path_disabled():
    ids = np.arange(1024, dtype="<i8")
    approved = a.Approval(ids, hashlib.sha256(ids.tobytes()).hexdigest())
    spy = Spy()
    a.selected_read(spy, ids[20:28], approved)
    assert spy.requests == [list(range(20, 28))]
    spy.file = SimpleNamespace(filename=str(p.ROOT / p.RAW))
    with pytest.raises(ValueError):
        a.selected_read(spy, ids[:1], approved)
    assert len(spy.requests) == 1
    with pytest.raises(ValueError):
        a.Approval(
            ids, hashlib.sha256(ids.tobytes()).hexdigest(), role="test_background"
        )


@pytest.mark.parametrize(
    "failure",
    ("label", "nan", "inf", "negative_pt", "bad_padding", "empty", "nontrailing"),
)
def test_particle_semantics(failure):
    raw = raw_rows(1)
    if failure == "label":
        raw[0, -1] = 1
    if failure == "nan":
        raw[0, 0] = np.nan
    if failure == "inf":
        raw[0, 1] = np.inf
    if failure == "negative_pt":
        raw[0, 0] = -1
    if failure == "bad_padding":
        raw[0, 7] = 1
    if failure == "empty":
        raw[:] = 0
    if failure == "nontrailing":
        raw[0, 0:3] = 0
    with pytest.raises(ValueError):
        a.construct(raw, parameters())


def test_all_particles_before384_and_rounded_physical_chain():
    raw = raw_rows(1)
    raw[0, :1500] = np.tile([1.0, 0.1, 0.2], 500)
    feature = a.construct(raw, parameters())
    assert feature[0, 0] == np.float32(np.log1p(500)) and feature[0, 1] == np.float32(
        np.log1p(500)
    )
    changed = raw.copy()
    changed[0, 3 * 499] = 20
    assert not np.array_equal(a.construct(changed, parameters()), feature)
    raw = raw_rows(1)
    raw[0, :6] = [10 + 1e-8, 0, np.pi, 10, -0.0, -np.pi]
    c = canonicalize(raw[:, :2100].reshape(1, 700, 3))
    assert c.original_slots[0, 0] == 0 and not np.signbit(c.padded[c.padded == 0]).any()
    expected = standardized_aggregates(physical_aggregates(c.padded), parameters())
    assert a.construct(raw, parameters()).tobytes() == expected.tobytes()


@pytest.mark.parametrize("b", plan.BATCHES)
def test_exact_batch_parity_synthetic(b):
    approved = approval()
    raw = raw_rows(1024)
    raw[:, 0] = 10 + np.arange(1024) / 100
    canonical = canonicalize(raw[:, :2100].reshape(1024, 700, 3))
    golden = standardized_aggregates(
        physical_aggregates(canonical.padded), parameters()
    )
    for start in plan.windows(b):
        result = a.construct(raw[start : start + b], parameters())
        a.parity(result, golden, approved.ids[start : start + b], approved)
        wrong = result.copy()
        wrong[0, 0] = np.nextafter(wrong[0, 0], np.float32(np.inf))
        with pytest.raises(ValueError):
            a.parity(wrong, golden, approved.ids[start : start + b], approved)


def test_mass_guard_unchanged_and_overflow(monkeypatch):
    raw = raw_rows(1)
    raw[0, :] = 0
    raw[0, :3] = [1.0, 20.0, 0.0]
    assert np.isfinite(a.construct(raw, parameters())).all()
    raw[0, 1] = 1000
    with pytest.raises(ValueError):
        a.construct(raw, parameters())
    raw[0, 1] = 1
    monkeypatch.setattr(np, "cosh", lambda x: np.zeros_like(x))
    with pytest.raises(ValueError, match="negative mass"):
        a.construct(raw, parameters())


@pytest.mark.parametrize(
    "failure",
    (
        "wrong_prefix",
        "duplicate",
        "partial",
        "float",
        "negative",
        "outside",
        "same_length_wrong_ID",
    ),
)
def test_resolver_invalid_membership(failure):
    values = np.arange(6999, dtype="<i8")
    expected = hashlib.sha256(values[:1024].tobytes()).hexdigest()
    if failure == "wrong_prefix":
        expected = "0" * 64
    if failure == "duplicate":
        values[-1] = values[0]
    if failure == "partial":
        values = values[:-1]
    if failure == "float":
        values = values.astype(float)
    if failure == "negative":
        values[0] = -1
    if failure == "outside":
        values[0] = 1100000
    if failure == "same_length_wrong_ID":
        values[0] = 90000
    with pytest.raises(ValueError):
        m.resolve(values, expected)


def test_unsorted_single_ID_load_durable_and_no_replacement(tmp_path, monkeypatch):
    values = np.arange(6999, dtype="<i8")[::-1].copy()
    path = tmp_path / "ids.npy"
    np.save(path, values)
    spec = dict(
        file_sha256=p.file_hash(path),
        selected_sha256=hashlib.sha256(
            np.arange(1024, dtype="<i8").tobytes()
        ).hexdigest(),
    )
    audit = {}
    seen = []
    old = np.load

    def load(*args, **kw):
        assert seen[-1]["membership_inflight"] is True
        return old(*args, **kw)

    monkeypatch.setattr(np, "load", load)
    selected = m.load_once(path, spec, audit, lambda: seen.append(audit.copy()))
    assert (
        np.array_equal(selected, np.arange(1024))
        and audit["membership_loads"] == 1
        and audit["membership_records_inspected"] == 6999
    )
    with pytest.raises(ValueError):
        m.load_once(path, spec, audit, lambda: None)


@pytest.mark.parametrize("failure", ("missing", "altered", "symlink", "header"))
def test_reject_ID_source_before_numeric(tmp_path, monkeypatch, failure):
    path = tmp_path / "ids.npy"
    np.save(path, np.arange(6999, dtype="<i8"))
    spec = dict(file_sha256=p.file_hash(path), selected_sha256="0" * 64)
    if failure == "missing":
        path.unlink()
    if failure == "altered":
        path.write_bytes(path.read_bytes()[:-1] + b"x")
    if failure == "symlink":
        dest = tmp_path / "other.npy"
        path.rename(dest)
        path.symlink_to(dest)
    if failure == "header":
        np.save(path, np.arange(6999, dtype="<f8"))
        spec["file_sha256"] = p.file_hash(path)
    monkeypatch.setattr(np, "load", lambda *args, **kw: pytest.fail("Prohibited load"))
    with pytest.raises((ValueError, FileNotFoundError)):
        m.load_once(path, spec, {}, lambda: None)


def test_schedule_counts_geometry_independent_oracle():
    c = plan.counts()
    assert c["cells"] == 36 and c["timed_calls"] == 720 and c["warmup_calls"] == 108
    total = []
    for rep in (1, 2, 3):
        rows = list(plan.schedule(rep))
        total += rows
        for b in plan.BATCHES:
            for scope in plan.SCOPES:
                timed = [
                    r
                    for r in rows
                    if r["B"] == b and r["scope"] == scope and r["phase"] == "timed"
                ]
                assert [
                    sum(r["window_position"] == x for r in timed)
                    for x in plan.windows(b)
                ] == [7, 7, 6]
    rawsum = sum(r["B"] for r in total if r["scope"] != "frozen_feature_construction")
    assert (
        rawsum == 23322
        and c["total_raw_selected_row_presentations"] == rawsum + 1521 + 6084 == 30927
    )
    geo = plan.geometry(np.arange(1024, dtype="<i8") * 3)
    assert sum(r["future_logical_raw_requests"] for r in geo["windows"]) == 732
    assert (
        sum(
            r["selected_rows"] * r["future_logical_raw_requests"]
            for r in geo["windows"]
        )
        == 30927
    )
    for r in geo["windows"]:
        selected = set(
            range(r["window_position"] * 3, (r["window_position"] + r["B"]) * 3, 3)
        )
        chunks = {
            i
            for i in range(17742)
            if selected.intersection(range(i * 62, (i + 1) * 62))
        }
        assert r["geometric_chunks"] == len(chunks)
    assert (
        c["total_feature_row_presentations"] == 32448
        and c["max_retained_raw_buffers_bytes"] == 6454272
    )


def hdf_fixture(tmp_path):

    path = tmp_path / "fixture.h5"
    with h5py.File(path, "w") as f:
        f.create_dataset(
            "/df/block0_values",
            shape=(1100000, 2101),
            dtype="<f8",
            chunks=(62, 2101),
            compression=32001,
            compression_opts=(0, 0, 0, 0, 5, 1),
        )
    return path


def test_HDF_metadata_no_dataset_values_effective_cache_cleanup(tmp_path, monkeypatch):
    path = hdf_fixture(tmp_path)
    called = []
    monkeypatch.setattr(
        h5py.Dataset,
        "__getitem__",
        lambda *x: pytest.fail("Metadata read event payload"),
    )
    audit = {}
    result = md.inspect(
        path,
        p.load()["raw"]["audit_schema"],
        audit,
        lambda: called.append(audit.copy()),
    )
    assert (
        result["event_dataset_values_read"] == 0
        and result["effective_dataset_chunk_cache"] == p.CACHE
        and audit["raw_HDF_metadata_opens"] == 1
        and audit["HDF_handle_closed"]
    )
    with pytest.raises(ValueError):
        md.inspect(path, p.load()["raw"]["audit_schema"], audit, lambda: None)


@pytest.mark.parametrize("failure", ("soft", "external", "alias", "schema", "cache"))
def test_HDF_metadata_schema_links_cache_rejected(tmp_path, failure):
    path = hdf_fixture(tmp_path)
    with h5py.File(path, "r+") as f:
        if failure == "soft":
            f["df/original"] = f["df/block0_values"]
            del f["df/block0_values"]
            f["df/block0_values"] = h5py.SoftLink("/df/original")
        if failure == "external":
            del f["df/block0_values"]
            f["df/block0_values"] = h5py.ExternalLink("missing.h5", "/events")
        if failure == "alias":
            f["alias"] = f["df/block0_values"]
    expected = p.load()["raw"]["audit_schema"].copy()
    if failure == "schema":
        expected["shape"] = [1100001, 2101]
    audit = {}
    if failure == "cache":
        with h5py.File(path, "r", rdcc_nbytes=2048) as f:
            with pytest.raises(ValueError):
                md.properties(f, expected)
    else:
        with pytest.raises(ValueError):
            md.inspect(path, expected, audit, lambda: None)
        assert (
            audit["raw_HDF_metadata_opens"] == 1 and audit["HDF_handle_closed"] is True
        )


def test_raw_custody_byte_counts_and_no_retry(tmp_path):
    path = tmp_path / "fixture.bin"
    path.write_bytes(b"x" * 3000)
    audit = {}
    spec = dict(size_bytes=3000, file_sha256=p.file_hash(path))
    md.hash_raw(path, spec, audit, lambda: None, lambda: None)
    assert audit["raw_hash_passes"] == 1 and audit["raw_hash_bytes"] == 3000
    with pytest.raises(ValueError):
        md.hash_raw(path, spec, audit, lambda: None, lambda: None)
    audit = {}
    spec["file_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        md.hash_raw(path, spec, audit, lambda: None, lambda: None)
    assert audit["raw_hash_passes"] == 1 and audit["raw_hash_bytes"] == 3000
