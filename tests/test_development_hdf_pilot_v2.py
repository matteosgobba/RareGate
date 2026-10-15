"""Task0056 bounded pure checks; actual class serialization runs only in native cases."""

import io
import json
import runpy
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from latenttrigger.streaming import hdf_consumer as h
from latenttrigger.streaming import pilot56, quota
from latenttrigger.streaming import pilot_context as c


def spec():
    return json.loads(Path(pilot56.CONFIG).read_text())


def test_original_scope_closed_and_accounting_before_native():
    s = spec()
    old = json.loads(
        Path("configs/streaming/development_hdf_consumer_pilot_v1.json").read_text()
    )
    for key in (
        "allowed_files",
        "models",
        "membership",
        "golden",
        "raw",
        "case_order",
        "maxima",
        "cache",
        "runtime",
        "numerical",
    ):
        assert s[key] == old[key]
    assert len(s["allowed_files"]) == 17
    assert s["task"] == "0056" and not s["full_study_execution_authorized"]
    assert [x["offers"] for x in s["case_order"]] == [64, 64]
    assert sum(s["buffer_derivation"].values()) <= 8388608
    assert s["resource_policy"]["inner_tracker_bytes"] == 80 * 1024**2
    assert s["maxima"]["raw_feature_rows"] == 416 and s["maxima"]["score_rows"] == 688
    assert s["maxima"]["booleans"] == 2752


def test_source_bytes_counterexample_and_fixed_cap():
    s = spec()
    fs = {x["role"]: x for x in s["allowed_files"]}
    shared = ["membership", "golden", "transform"] + s["lineage_roles"]
    sizes = [
        sum(
            fs[r]["bytes"]
            for r in shared
            + [name + ":" + k for k in ("model", "config", "calibration")]
        )
        for name in c.CANDIDATES
    ]
    assert sizes == [320343, 377025]
    assert all(262144 < n <= s["source_bytes_bound"] == 393216 for n in sizes)


def test_global_ledger_all_attempts_and_fixture_files():
    plan = pilot56.file_plan()
    assert len(plan) == 504 and sum(plan.values()) == 28631424 < 32 * 1024**2
    for group in (1, 2):
        for name in ("15-serialized-pca", "16-serialized-ae"):
            prefix = f"suite-{group}/{name}/"
            assert len([p for p in plan if p.startswith(prefix + "serialized/")]) == 14
            assert plan[prefix + "consumer-audit.bin"] == 65536
            assert plan[prefix + "fixture-spec.json"] == 32768
    with pytest.raises(quota.QuotaError):
        quota.Ledger(Path.cwd(), plan)
    assert quota.Ledger(Path.cwd(), plan, task="0056").cap == 32 * 1024**2


@pytest.mark.parametrize(
    "root",
    [
        "/tmp/fake",
        "data/task0054-validation/session-v1",
        "data/task0055-validation/task0055",
    ],
)
def test_new_context_rejects_old_roots_without_sources(root):
    with pytest.raises(ValueError):
        c.PilotContext56(root, "bad").specification(Path.cwd())


def test_immutable_and_disjoint_context_types():
    real = c.PilotContext56(str(Path.cwd() / c.ROOT56), "frozen")
    fixture = c.FixtureContext56(
        real.root, real.root + "/suite-1/15-serialized-pca", "frozen", "pca-v1"
    )
    with pytest.raises(FrozenInstanceError):
        real.task = "0054"
    assert type(real) is not type(fixture)
    with pytest.raises(ValueError):
        c.context_from_request(
            real.root,
            dict(task="0054", candidate="pca-v1", context=fixture),
            Path.cwd(),
        )
    with pytest.raises(ValueError):
        c.context_from_request(
            real.root, dict(task="0056", candidate="pca-v1", context={}), Path.cwd()
        )


@pytest.mark.parametrize("pos", [[], [64], [-1], [True], [1.0], [0] * 9])
def test_standin_rejects_scope_before_allocation(pos):
    with pytest.raises(ValueError):
        c.fixture_rows(pos)


def test_strict_dataset_not_HDF_and_fifo_owned():
    handle = c.FixtureHandle()
    dataset = c.FixtureDataset(handle)
    a = dataset[[1, 7], :]
    assert a.shape == (2, 2101) and a.dtype == np.dtype("<f8") and a.flags.owndata
    assert (a[:, 2100] == 0).all()
    with pytest.raises(ValueError):
        dataset[[7, 1], :]
    with pytest.raises(ValueError):
        dataset[slice(0, 8), :]
    handle.close()
    with pytest.raises(ValueError):
        dataset[[1], :]


def test_npy_loader_contract_owned_shape_dtype_and_nonpickle():
    # Explicit generated serialized2x8, not a model/operational artifact.
    out = io.BytesIO()
    np.save(out, np.arange(16, dtype="<f4").reshape(2, 8), allow_pickle=False)
    a = h.load_npy_owned(out.getvalue(), (2, 8), "<f4")
    assert a.shape == (2, 8) and a.dtype == np.dtype("<f4") and a.flags.owndata


@pytest.mark.parametrize(
    "args,code",
    [
        (["--help"], 0),
        ([], 2),
        (["--run-pilot", "--root", "/wrong"], 2),
        (["--run-pilot", "--qualify-generated", "--root", "/wrong"], 2),
    ],
)
def test_entry_errors_help_do_not_open_or_import_numeric(monkeypatch, args, code):
    command = runpy.run_path("scripts/development_hdf_consumer_pilot_v2.py")
    monkeypatch.setattr(sys, "argv", ["pilot", *args])
    with pytest.raises(SystemExit) as exc:
        command["main"]()
    assert exc.value.code == code


def test_runtime_and_source_free_entry_cannot_load_fixture_or_real_payload():
    import inspect

    from latenttrigger.streaming.cpu_runtime import RuntimeSession
    from latenttrigger.streaming.fixture import run_fixture

    assert "context" not in inspect.signature(run_fixture).parameters
    assert "pilot" not in inspect.signature(run_fixture).parameters
    assert "_initialize_payload" not in inspect.getsource(RuntimeSession.initialize)


def test_partial_constructor_close_and_primary_error_retained(monkeypatch):
    b = h.RealBackend.__new__(h.RealBackend)
    b.handle = None
    b.limiter = None
    b.phase = "source_bytes"
    b.payload_armed = True
    b.budget = h.Budget()
    b.observations = {}
    b.checkpoint = Mock(side_effect=OSError("report failure"))
    records = []
    monkeypatch.setattr(
        quota, "CURRENT", SimpleNamespace(write_json=lambda p, x: records.append(x))
    )
    assert (
        h.record_initialization_failure(b, Path("not-opened"), TypeError("loader type"))
        is None
    )
    assert records[0]["primary_failure"]["type"] == "TypeError"
    assert records[0]["report_failure"]["type"] == "OSError"
    b.close()


def test_payload_rejects_missing_qualification_before_any_source_bytes(monkeypatch):
    root = Path.cwd() / c.ROOT56
    ctx = c.PilotContext56(str(root), "identity")
    monkeypatch.setattr(ctx.__class__, "specification", lambda *_: {})
    monkeypatch.setattr(
        quota,
        "CURRENT",
        SimpleNamespace(task="0056", root=root, entries=pilot56.file_plan()),
    )
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda *_: json.dumps(
            dict(
                subject_pid=0,
                task="0056",
                single_session=True,
                bundle_sha256="identity",
                root=str(root),
            )
        ),
    )
    with pytest.raises(ValueError):
        ctx.validate_payload(Path.cwd(), "pca-v1", h.Budget())


def test_scientific_lineage_mutation_is_not_accepted():
    with pytest.raises((ValueError, KeyError)):
        h.validate_lineage(
            {"dev_manifest": {}, "transform": {}, "split_manifest": {}}, {}
        )


@pytest.mark.parametrize("shape,dtype", [((1, 16), "<f4"), ((2, 8), "<f8")])
def test_serialized_array_schema_rejected_before_coercion(shape, dtype):
    stream = io.BytesIO()
    np.save(stream, np.zeros((2, 8), dtype="<f4"), allow_pickle=False)
    with pytest.raises(ValueError):
        h.load_npy_owned(stream.getvalue(), shape, dtype)


def test_post_service_failure_is_distinct_from_startup(monkeypatch):
    b = h.RealBackend.__new__(h.RealBackend)
    b.phase = "post_gates"
    b.payload_armed = True
    b.budget = h.Budget()
    b.observations = {}
    b.checkpoint = lambda: None
    records = []
    monkeypatch.setattr(
        quota, "CURRENT", SimpleNamespace(write_json=lambda p, x: records.append(x))
    )
    h.record_initialization_failure(
        b, Path("not-opened"), ValueError("reference mismatch"), initialization=False
    )
    assert not records[0]["initialization_failed"] and records[0]["payload_armed"]
    assert (
        records[0]["phase"] == "post_gates"
        and records[0]["primary_failure"]["message"] == "reference mismatch"
    )
