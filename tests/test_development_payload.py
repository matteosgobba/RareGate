"""Fixed scheduling, exact parity, ephemeral buffers and failure accounting."""

import json
import time
from types import SimpleNamespace

import h5py
import numpy as np
import pytest
from tests.test_development_payload_grants import owned_grant

from raregate.benchmarks import development_payload_measure as measure
from raregate.benchmarks import development_payload_protocol as p
from raregate.benchmarks import development_payload_provider as provider
from raregate.benchmarks import development_payload_runtime as rt
from raregate.benchmarks import development_raw_metadata as md
from raregate.benchmarks import development_raw_planning as design
from raregate.benchmarks.development_raw_synthetic import fixture, parameters


def setup_payload(tmp_path, monkeypatch, rep=1):
    directory, grant = owned_grant(tmp_path, monkeypatch, f"repetition{rep}")
    path, prefix = fixture(directory)
    _, permit = p.validate_grant(directory, grant["token"], time.monotonic)
    handle = h5py.File(path, "r", **p.CACHE)
    md.properties(handle, p.old.load()["raw"]["audit_schema"])
    selected = np.arange(1024, dtype="<i8") * 3
    approval = provider.Approval(selected, prefix)
    payload = provider.Payload(
        handle.get("/df/block0_values"),
        approval,
        path,
        time.monotonic,
        grant["operation_deadline"],
        permit=permit,
    )
    golden = np.empty((1024, 8), dtype="<f4")
    for start in range(0, 1024, 128):
        golden[start : start + 128] = provider.construct(
            handle.get("/df/block0_values")[selected[start : start + 128].tolist(), :],
            parameters(),
        )
    ledger = provider.Ledger(directory)
    return directory, handle, payload, golden, ledger


@pytest.mark.parametrize("rep", [1, 2, 3])
def test_complete_fixed_matrix(tmp_path, monkeypatch, rep):
    directory, handle, payload, golden, ledger = setup_payload(
        tmp_path, monkeypatch, rep
    )
    guard = SimpleNamespace(check=lambda: None, clock=time.monotonic)
    try:
        measure.run(payload, golden, parameters(), ledger, directory, rep, guard)
        ledger.audit.update(
            membership_loads=1,
            membership_records_inspected=6999,
            selected_IDs=1024,
            membership_inflight=False,
            golden_loads=1,
            golden_rows=1024,
            golden_inflight=False,
            HDF_opens=1,
            HDF_closed=True,
        )
        rt.accounting(ledger.audit)
        aggregate = p.read(directory / "aggregate.json")
        assert aggregate["exact_parity"] and len(aggregate["gates"]) == 24
        assert aggregate["peak_retained_raw_buffers_bytes"] == 6454272
        assert aggregate["peak_owned_array_bound_bytes"] <= 64 * 2**20
        records = [
            json.loads(v)
            for v in (directory / "timings.jsonl").read_text().splitlines()
        ]
        assert len(records) == 276
        assert [
            dict(
                (k, v[k])
                for k in (
                    "repetition",
                    "B",
                    "scope",
                    "phase",
                    "call",
                    "window_position",
                )
            )
            for v in records
        ] == list(design.schedule(rep))
        assert payload.raw_calls == 244 and payload.feature_calls == 256
        assert not list(directory.glob("*.npy")) or all(
            v.name.startswith("fixture") for v in directory.glob("*.npy")
        )
    finally:
        handle.close()


@pytest.mark.parametrize(
    "ids_request",
    [
        np.array([1], dtype="<i8"),
        np.array([0, 1, 3], dtype="<i8"),
        np.array([3, 0], dtype="<i8"),
        np.arange(129, dtype="<i8") * 3,
        np.array([0], dtype="<i4"),
        np.array([], dtype="<i8"),
        np.array([0, 0], dtype="<i8"),
    ],
)
def test_unauthorized_before_backend(tmp_path, monkeypatch, ids_request):
    _, handle, payload, _, _ = setup_payload(tmp_path, monkeypatch)
    try:
        before = payload.raw_calls
        with pytest.raises(ValueError):
            payload.read(ids_request)
        assert payload.raw_calls == before
    finally:
        handle.close()


def test_same_approved_but_not_fixed_window(tmp_path, monkeypatch):
    _, handle, payload, _, _ = setup_payload(tmp_path, monkeypatch)
    try:
        with pytest.raises(ValueError, match="fixed approved"):
            payload.read(np.array([3], dtype="<i8"))
        assert payload.raw_calls == 0
    finally:
        handle.close()


@pytest.mark.parametrize(
    "failure", ["deadline", "raw_budget", "feature_budget", "buffers"]
)
def test_caps_before_value_access(tmp_path, monkeypatch, failure):
    _, handle, payload, _, _ = setup_payload(tmp_path, monkeypatch)
    try:
        if failure == "deadline":
            payload.deadline = 0
        if failure == "raw_budget":
            payload.raw_calls = 244
        if failure == "feature_budget":
            payload.feature_calls = 256
        if failure == "buffers":
            payload.retained_bytes = 64 * 2**20
        with pytest.raises(ValueError):
            if failure == "feature_budget":
                payload.features(np.zeros((1, 2101), dtype="<f8"), parameters())
            else:
                payload.read(np.array([0], dtype="<i8"))
    finally:
        handle.close()


@pytest.mark.parametrize(
    "mutation", ["one_byte", "position_shuffle", "wrong_shape", "nonfinite"]
)
def test_golden_parity_failure_preserves_partial(tmp_path, monkeypatch, mutation):
    directory, handle, payload, golden, ledger = setup_payload(tmp_path, monkeypatch)
    if mutation == "one_byte":
        golden.view("u1")[0, 0] ^= 1
    if mutation == "position_shuffle":
        golden[[0, 1]] = golden[[1, 0]]
    if mutation == "wrong_shape":
        golden = golden[:-1]
    if mutation == "nonfinite":
        golden[0, 0] = np.nan
    try:
        with pytest.raises((ValueError, IndexError)):
            measure.run(
                payload,
                golden,
                parameters(),
                ledger,
                directory,
                1,
                SimpleNamespace(check=lambda: None, clock=time.monotonic),
            )
        assert not (directory / "aggregate.json").exists()
        assert (directory / "access.json").exists()
    finally:
        handle.close()


@pytest.mark.parametrize("fault", ["label", "nonfinite", "empty", "bad_padding"])
def test_invalid_raw_chain(fault):
    rows = np.zeros((1, 2101), dtype="<f8")
    rows[0, :3] = [10, 0.1, 0.2]
    if fault == "label":
        rows[0, -1] = 1
    if fault == "nonfinite":
        rows[0, 1] = np.nan
    if fault == "empty":
        rows.fill(0)
    if fault == "bad_padding":
        rows[0, 7] = 1
    with pytest.raises(ValueError):
        provider.construct(rows, parameters())


def test_all_particles_not384():
    rows = np.zeros((1, 2101), dtype="<f8")
    rows[0, :1500] = np.tile([1, 0.1, 0.2], 500)
    full = provider.construct(rows, parameters())
    rows[0, 384 * 3 :] = 0
    short = provider.construct(rows, parameters())
    assert full[0, 0] > short[0, 0]


def test_partial_error_accounting(tmp_path):
    ledger = provider.Ledger(tmp_path)
    ledger.start("gate", 8, raw=True, feature=True)
    ledger.finish(
        SimpleNamespace(returned=True, returned_rows=8, constructed=False),
        success=False,
    )
    assert ledger.audit["raw_requested_rows"] == ledger.audit["raw_returned_rows"] == 8
    assert (
        ledger.audit["feature_completed_rows"] == 0
        and ledger.audit["inflight"] is not None
    )
    with pytest.raises(ValueError):
        ledger.start("timing", 1, raw=True)


@pytest.mark.parametrize("values", [[10, 20], [0, 0, 0], [11, 13, 101]])
def test_quantiles_population_std(values):
    s = measure.stats(values)
    assert s["population_std_ns"] == np.std(values, ddof=0)
    assert s["p95_ns"] == np.quantile(values, 0.95, method="linear")


@pytest.mark.parametrize("values", [[], [-1], [float("inf")], [True], [1.1]])
def test_invalid_times(values):
    with pytest.raises(ValueError):
        measure.stats(values)


@pytest.mark.parametrize(
    "field,value",
    [
        ("chunks", [63, 2101]),
        ("dtype", "float32"),
        ("shape", [1099999, 2101]),
        ("filters", []),
    ],
)
def test_schema_filter_cache_refusal_no_values(tmp_path, monkeypatch, field, value):
    directory, _ = owned_grant(tmp_path, monkeypatch)
    path, _ = fixture(directory)
    expected = dict(p.old.load()["raw"]["audit_schema"])
    expected[field] = value
    with md.forbid_payload(), h5py.File(path, "r", **p.CACHE) as handle:
        with pytest.raises(ValueError):
            md.properties(handle, expected)


def test_wrong_cache_refused(tmp_path, monkeypatch):
    directory, _ = owned_grant(tmp_path, monkeypatch)
    path, _ = fixture(directory)
    with (
        md.forbid_payload(),
        h5py.File(
            path, "r", rdcc_nbytes=2**21, rdcc_nslots=521, rdcc_w0=0.75
        ) as handle,
    ):
        with pytest.raises(ValueError, match="cache"):
            md.properties(handle, p.old.load()["raw"]["audit_schema"])


@pytest.mark.parametrize("wrong", ["payload", "nonfinite", "duplicate_load"])
def test_golden_load_constraints(tmp_path, wrong):
    golden = np.zeros((1024, 8), dtype="<f4")
    if wrong == "nonfinite":
        golden[0, 0] = np.nan
    path = tmp_path / "golden.npy"
    np.save(path, golden, allow_pickle=False)
    ledger = provider.Ledger(tmp_path)
    spec = dict(
        file_sha256=p.file_hash(path),
        payload_sha256=measure.block_hash(golden) if wrong != "payload" else "0" * 64,
    )
    if wrong == "duplicate_load":
        ledger.audit["golden_load_attempts"] = 1
    with pytest.raises(ValueError):
        provider.golden_once(path, spec, ledger)


def test_nonsymlink_sources_and_header(tmp_path):
    source = tmp_path / "owned.npy"
    np.save(source, np.zeros((1024, 8), dtype="<f4"))
    p.header(source, [1024, 8], "<f4", 32896)
    alias = tmp_path / "alias.npy"
    alias.symlink_to(source)
    with pytest.raises(ValueError):
        p.fixed(tmp_path, "alias.npy")
    with pytest.raises(ValueError):
        p.header(source, [1024, 8], "<f8", 32896)


def test_custody_once_and_changed_source(tmp_path):
    source = tmp_path / "raw"
    source.write_bytes(b"owned synthetic bytes")
    expected = dict(size_bytes=source.stat().st_size, file_sha256=p.file_hash(source))
    audit = {}
    p.hash_raw(source, expected, audit, lambda: None, lambda: None)
    assert audit["passes"] == 1 and audit["bytes"] == len(b"owned synthetic bytes")
    with pytest.raises(ValueError):
        p.hash_raw(source, expected, audit, lambda: None, lambda: None)
    source.write_bytes(b"changed synthetic txt")
    with pytest.raises(ValueError):
        p.hash_raw(source, expected, {}, lambda: None, lambda: None)


def test_failed_backend_does_not_claim_rows_returned(tmp_path, monkeypatch):
    directory, handle, payload, _, ledger = setup_payload(tmp_path, monkeypatch)
    original = payload.dataset

    class Broken:
        file = original.file
        id = original.id

        def __getitem__(self, key):
            raise RuntimeError("synthetic interrupted HDF read")

    payload.dataset = Broken()
    ledger.start("gate", 1, raw=True)
    try:
        with pytest.raises(RuntimeError):
            payload.read(np.array([0], dtype="<i8"))
        ledger.finish(payload, success=False)
        assert (
            ledger.audit["raw_requested_rows"] == 1
            and ledger.audit["raw_returned_rows"] == 0
        )
        assert ledger.audit["inflight"] is not None
    finally:
        handle.close()


@pytest.mark.parametrize(
    "failure",
    [
        "missing_cell",
        "duplicate_cell",
        "wrong_count",
        "missing_observation",
        "bad_identity",
        "parity",
    ],
)
def test_aggregate_report_rejects_incomplete_owned_inputs(tmp_path, failure):
    from raregate.benchmarks import development_payload_reporting as reporting

    for rep in (1, 2, 3):
        d = tmp_path / f"repetition{rep}"
        d.mkdir()
        cells = [
            dict(
                repetition=rep,
                B=b,
                scope=scope,
                count=20,
                observations_ns=list(range(1, 21)),
            )
            for b in design.BATCHES
            for scope in design.SCOPES
        ]
        if rep == 1:
            if failure == "missing_cell":
                cells.pop()
            if failure == "duplicate_cell":
                cells[-1] = cells[0]
            if failure == "wrong_count":
                cells[0]["count"] = 19
            if failure == "missing_observation":
                cells[0]["observations_ns"].pop()
        agg = dict(cells=cells, gates=[{}] * 24, exact_parity=failure != "parity")
        p.durable_json(d / "aggregate.json", agg)
        receipt = dict(
            status="body_complete_awaiting_exit",
            outputs={"aggregate.json": p.file_hash(d / "aggregate.json")},
        )
        if failure == "bad_identity":
            receipt["outputs"]["aggregate.json"] = "0" * 64
        p.durable_json(d / "receipt.json", receipt)
    with pytest.raises(ValueError):
        reporting.collect(tmp_path)
