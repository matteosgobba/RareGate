"""Synthetic complete chains, original same-B service parity and honest partial budgets."""

import json
import time
from types import SimpleNamespace

import h5py
import numpy as np
import pytest
from tests.test_development_decision_grants import owned_grant

from latenttrigger.benchmarks import core
from latenttrigger.benchmarks import development_decision_measure as measure
from latenttrigger.benchmarks import development_decision_planning as plan
from latenttrigger.benchmarks import development_decision_protocol as p
from latenttrigger.benchmarks import development_decision_provider as provider
from latenttrigger.benchmarks import development_decision_runtime as rt
from latenttrigger.benchmarks.development_decision_synthetic import (
    models as fixture_models,
)
from latenttrigger.benchmarks.development_raw_synthetic import fixture, parameters


def setup_chain(tmp_path, monkeypatch, rep=1):
    directory, grant = owned_grant(tmp_path, monkeypatch, f"repetition{rep}")
    path, prefix = fixture(directory)
    _, permit = p.validate_grant(directory, grant["token"], time.monotonic)
    selected = np.arange(1024, dtype="<i8") * 3
    approval = provider.Approval(selected, prefix)
    handle = h5py.File(path, "r", **p.CACHE)
    chain = provider.Chain(
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
    entries = fixture_models(directory)
    loaded = {}
    hashes = {}
    for entry in entries:
        loaded[entry["name"]] = core.load_model(directory, entry)
        model, thresholds = loaded[entry["name"]]
        hashes[entry["name"]] = (
            core.parameter_hash(model),
            measure.block_hash(thresholds),
        )
    return directory, handle, chain, golden, provider.Ledger(directory), loaded, hashes


@pytest.mark.parametrize("rep", [1, 2, 3])
def test_complete_joint_schedule_exact_service_budget(tmp_path, monkeypatch, rep):
    directory, handle, chain, golden, ledger, loaded, hashes = setup_chain(
        tmp_path, monkeypatch, rep
    )
    counts = {name: 0 for name in plan.CANDIDATES}
    for name, (model, _) in loaded.items():
        method = "forward" if name == "compact-autoencoder-v2" else "reconstruct"
        original = getattr(model, method)

        def observe(*args, name=name, original=original, **kwargs):
            counts[name] += 1
            return original(*args, **kwargs)

        monkeypatch.setattr(model, method, observe)
    try:
        measure.run(
            chain,
            golden,
            parameters(),
            ledger,
            directory,
            rep,
            SimpleNamespace(
                check=lambda: None, clock=time.monotonic, boundary=lambda *a: None
            ),
            loaded,
            hashes,
            lambda: None,
        )
        assert counts == {"pca-v1": 164, "compact-autoencoder-v2": 164}
        assert (
            chain.raw_calls == chain.feature_calls == 280 and chain.service_calls == 328
        )
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
            model_loads=2,
            threshold_loads=2,
            model_instantiations=2,
        )
        rt.accounting(ledger.audit)
        agg = p.read(directory / "aggregate.json")
        assert len(agg["gates"]) == 48 and len(agg["cells"]) == 8
        assert (
            agg["raw_window_buffers_retained"] == 0
            and agg["peak_owned_array_bound_bytes"] <= 64 * 2**20
        )
        records = [
            json.loads(v)
            for v in (directory / "timings.jsonl").read_text().splitlines()
        ]
        assert len(records) == 184 and [
            dict(
                (k, v[k])
                for k in (
                    "repetition",
                    "candidate",
                    "B",
                    "phase",
                    "call",
                    "window_position",
                )
            )
            for v in records
        ] == [v for name in plan.candidates(rep) for v in plan.schedule(rep, name)]
        assert not any(
            v.name.endswith(("scores.npy", "decisions.npy", "features.npy"))
            for v in directory.iterdir()
        )
    finally:
        handle.close()


@pytest.mark.parametrize("failure", ["raw", "feature", "adapter"])
def test_partial_failure_at_each_stage(tmp_path, monkeypatch, failure):
    directory, handle, chain, _, ledger, loaded, _ = setup_chain(tmp_path, monkeypatch)
    model, thresholds = loaded["pca-v1"]

    def failed(*a, **kw):
        raise RuntimeError("owned synthetic interruption")

    target = {"raw": "read", "feature": "features", "adapter": "public"}[failure]
    original = getattr(chain, target)

    def stop(*a, **kw):
        if failure == "raw":
            chain.read_started = True
        if failure == "feature":
            chain.feature_started = True
        if failure == "adapter":
            chain.adapter_started = True
        failed()

    monkeypatch.setattr(chain, target, stop)
    ledger.start("chain_gate", "pca-v1", 1, chain=True, context={})
    try:
        with pytest.raises(RuntimeError):
            chain.joint(
                np.array([0], dtype="<i8"),
                parameters(),
                model,
                thresholds,
                p.load()["channels"],
            )
        ledger.finish(chain, success=False)
        assert ledger.audit["raw_requested_rows"] == 1 and ledger.audit[
            "raw_returned_rows"
        ] == int(failure != "raw")
        assert ledger.audit["feature_completed_rows"] == int(failure == "adapter")
        assert (
            ledger.audit["adapter_completed_rows"] == 0
            and ledger.audit["inflight"] is not None
        )
        assert ledger.audit["inflight"]["nested_progress"]["adapter_started"] == (
            failure == "adapter"
        )
    finally:
        handle.close()
        monkeypatch.setattr(chain, target, original)


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
        np.array([3], dtype="<i8"),
    ],
)
def test_denied_before_backend(tmp_path, monkeypatch, ids_request):
    _, handle, chain, _, _, _, _ = setup_chain(tmp_path, monkeypatch)
    try:
        with pytest.raises(ValueError):
            chain.read(ids_request)
        assert chain.raw_calls == 0
    finally:
        handle.close()


@pytest.mark.parametrize(
    "fault", ["feature", "score", "mask", "parameters", "threshold"]
)
def test_exact_gate_refuses_changed_outputs_or_state(tmp_path, monkeypatch, fault):
    directory, handle, chain, golden, ledger, loaded, hashes = setup_chain(
        tmp_path, monkeypatch
    )
    original = chain.joint

    def mutate(*args, **kwargs):
        f, s, m = original(*args, **kwargs)
        if fault == "feature":
            f.view("u1")[0, 0] ^= 1
        if fault == "score":
            s.view("u1")[0] ^= 1
        if fault == "mask":
            m[0, 0] = ~m[0, 0]
        if fault == "parameters":
            loaded["pca-v1"][0].mean[0] += 1
        if fault == "threshold":
            loaded["pca-v1"][1][0] += 1
        return f, s, m

    monkeypatch.setattr(chain, "joint", mutate)
    try:
        with pytest.raises(ValueError):
            measure.run(
                chain,
                golden,
                parameters(),
                ledger,
                directory,
                1,
                SimpleNamespace(
                    check=lambda: None, clock=time.monotonic, boundary=lambda *a: None
                ),
                loaded,
                hashes,
                lambda: None,
            )
        assert not (directory / "aggregate.json").exists()
        assert (directory / "access.json").exists()
    finally:
        handle.close()


@pytest.mark.parametrize(
    "fault",
    ["deadline", "raw_budget", "feature_budget", "service_budget", "buffer", "B1024"],
)
def test_fixed_caps_before_operation(tmp_path, monkeypatch, fault):
    _, handle, chain, _, _, loaded, _ = setup_chain(tmp_path, monkeypatch)
    model, thresholds = loaded["pca-v1"]
    if fault == "deadline":
        chain.deadline = 0
    if fault == "raw_budget":
        chain.raw_calls = 280
    if fault == "feature_budget":
        chain.feature_calls = 280
    if fault == "service_budget":
        chain.service_calls = 328
    if fault == "buffer":
        chain.retained_bytes = 64 * 2**20
    try:
        with pytest.raises(ValueError):
            if fault in ("service_budget", "B1024"):
                chain.public(
                    model,
                    thresholds,
                    p.load()["channels"],
                    np.zeros((1024 if fault == "B1024" else 1, 8), dtype="<f4"),
                    1024 if fault == "B1024" else 1,
                )
            elif fault == "feature_budget":
                chain.features(np.zeros((1, 2101), dtype="<f8"), parameters())
            else:
                chain.read(np.array([0], dtype="<i8"))
    finally:
        handle.close()


def test_planner_derived_counts_geometry():
    c = plan.counts()
    assert c["selected_reads_and_feature_constructions"] == dict(calls=840, rows=35490)
    assert (
        c["public_service"] == dict(calls=984, rows=41574)
        and c["decision_boolean_values"] == 166296
    )
    assert c["timed"] == dict(calls=480, rows=20280) and c["warmup"] == dict(
        calls=72, rows=3042
    )
    assert c["per_worker"] == dict(
        raw_calls=280,
        raw_rows=11830,
        service_calls=328,
        service_rows=13858,
        reference_calls=48,
        reference_rows=2028,
    )
    assert c["gate_window_records"] == 144 and c["raw_buffer_preloads"] == 0
    g = plan.geometry(np.arange(1024, dtype="<i8") * 3)
    assert (
        sum(v["logical_raw_requests"] for v in g["windows"]) == 840
        and g["unique_raw_rows"] == 384
    )


@pytest.mark.parametrize("fault", ["label", "empty", "padding", "nonfinite"])
def test_original_full_particle_validation(fault):
    rows = np.zeros((1, 2101), dtype="<f8")
    rows[0, :3] = [10, 0.1, 0.2]
    if fault == "label":
        rows[0, -1] = 1
    if fault == "empty":
        rows.fill(0)
    if fault == "padding":
        rows[0, 7] = 1
    if fault == "nonfinite":
        rows[0, 2] = np.nan
    with pytest.raises(ValueError):
        provider.construct(rows, parameters())


def test_tail_beyond384_remains_in_aggregates():
    raw = np.zeros((1, 2101), dtype="<f8")
    raw[0, :1500] = np.tile([1, 0.1, 0.2], 500)
    full = provider.construct(raw, parameters())
    raw[0, 384 * 3 :] = 0
    assert full[0, 0] > provider.construct(raw, parameters())[0, 0]


def test_owned_natural_service_and_strict_ties():
    from latenttrigger.benchmarks.prepared_service import pack, service

    class Toy:
        def score(self, x, feature_names):
            assert x.flags.owndata and x.shape == (8, 8)
            return np.arange(8, dtype="<f8")

    x = np.zeros((8, 8), dtype="<f4")
    owned = pack(x, 8, "natural")
    assert not np.shares_memory(x, owned)
    scores, masks = service(
        Toy(), np.array([0, 1, 3, 7], dtype="<f8"), [], x, 8, "natural"
    )
    assert (
        masks[0].tolist() == [False] * 4
        and not masks[7, 3]
        and np.array_equal(masks, scores[:, None] > np.array([0, 1, 3, 7])[None, :])
    )


@pytest.mark.parametrize(
    "fault", ["parameter_byte", "feature_order", "scientific_hash", "wrong_name"]
)
def test_fixture_model_identity_same_length_refusal(tmp_path, fault):
    entries = fixture_models(tmp_path)
    entry = entries[1]
    path = tmp_path / entry["model_path"]
    artifact = p.read(path)
    if fault == "parameter_byte":
        artifact["scientific"]["parameters"][0]["values"][0][0] += 0.1
    if fault == "feature_order":
        artifact["scientific"]["features"][0], artifact["scientific"]["features"][1] = (
            artifact["scientific"]["features"][1],
            artifact["scientific"]["features"][0],
        )
    if fault == "scientific_hash":
        artifact["scientific_sha256"] = "0" * 64
    if fault == "wrong_name":
        entry = dict(entry, name="compact-autoencoder-v1")
    p.durable_json(path, artifact)
    with pytest.raises(ValueError):
        core.load_model(tmp_path, entry)


@pytest.mark.parametrize(
    "fault", ["duplicate", "wrong_prefix", "wrong_dtype", "partial"]
)
def test_original_membership_resolver_refusal(fault):
    from latenttrigger.benchmarks.development_raw_membership import resolve

    ids = np.arange(6999, dtype="<i8") * 3
    expected = measure.block_hash(ids[:1024])
    if fault == "duplicate":
        ids[1] = ids[0]
    if fault == "wrong_prefix":
        ids[0] = 21000
    if fault == "wrong_dtype":
        ids = ids.astype("<i4")
    if fault == "partial":
        ids = ids[:-1]
    with pytest.raises(ValueError):
        resolve(ids, expected)


@pytest.mark.parametrize(
    "field,value",
    [
        ("chunks", [63, 2101]),
        ("dtype", "float32"),
        ("shape", [1100000, 2100]),
        ("filters", []),
    ],
)
def test_metadata_refusal_before_values(tmp_path, monkeypatch, field, value):
    from latenttrigger.benchmarks import development_raw_metadata as md

    directory, _ = owned_grant(tmp_path, monkeypatch)
    path, _ = fixture(directory)
    expected = dict(p.old.load()["raw"]["audit_schema"])
    expected[field] = value
    with md.forbid_payload(), h5py.File(path, "r", **p.CACHE) as handle:
        with pytest.raises(ValueError):
            md.properties(handle, expected)


@pytest.mark.parametrize(
    "fault",
    [
        "missing_cell",
        "duplicate",
        "short_cell",
        "wrong_strategy",
        "altered_receipt",
        "parity",
    ],
)
def test_aggregate_only_reporting_boundary(tmp_path, fault):
    from latenttrigger.benchmarks import development_decision_reporting as reporting

    for rep in (1, 2, 3):
        d = tmp_path / f"repetition{rep}"
        d.mkdir()
        cells = [
            dict(
                repetition=rep,
                candidate=c,
                B=b,
                scope="selected_raw_to_decisions",
                strategy="natural",
                count=20,
                observations_ns=list(range(1, 21)),
            )
            for c in plan.CANDIDATES
            for b in plan.BATCHES
        ]
        if rep == 1:
            if fault == "missing_cell":
                cells.pop()
            if fault == "duplicate":
                cells[-1] = cells[0]
            if fault == "short_cell":
                cells[0]["observations_ns"].pop()
            if fault == "wrong_strategy":
                cells[0]["strategy"] = "padded"
        p.durable_json(
            d / "aggregate.json",
            dict(
                cells=cells,
                gates=[{}] * 48,
                exact_feature_score_decision_parity=fault != "parity",
            ),
        )
        receipt = dict(
            status="body_complete_awaiting_exit",
            outputs={"aggregate.json": p.file_hash(d / "aggregate.json")},
        )
        if fault == "altered_receipt":
            receipt["outputs"]["aggregate.json"] = "0" * 64
        p.durable_json(d / "receipt.json", receipt)
    with pytest.raises(ValueError):
        reporting.collect(tmp_path)


def test_loaded_parameter_bytes_match_static_fixture_artifact(tmp_path):
    entries = fixture_models(tmp_path)
    for entry in entries:
        model, _ = core.load_model(tmp_path, entry)
        assert core.parameter_hash(model) == p.expected_parameter_hash(
            p.read(tmp_path / entry["model_path"])
        )
