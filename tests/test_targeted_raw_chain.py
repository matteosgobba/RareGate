"""Generated paired requests, unchanged natural packing and nested failure accounting."""

import hashlib
from types import SimpleNamespace

import numpy as np
import pytest
from tests.test_targeted_raw_admission import emitted as emitted
from tests.test_targeted_raw_runtime import granted

from raregate.benchmarks import targeted_raw_measure as measure
from raregate.benchmarks import targeted_raw_planning as plan
from raregate.benchmarks import targeted_raw_protocol as p
from raregate.benchmarks import targeted_raw_provider as provider
from raregate.benchmarks.development_raw_synthetic import parameters
from raregate.benchmarks.targeted_raw_service import pack, service


def setup(emitted):
    context, folder, grant, _ = granted(emitted)
    _, permit = p.validate_grant(folder, grant["token"], lambda: 1, root=context.root)
    ids = np.arange(1024, dtype="<i8") * 3
    approval = provider.Approval(ids, hashlib.sha256(ids.tobytes()).hexdigest())

    class Dataset:
        name = "/df/block0_values"
        shape = (1100000, 2101)
        dtype = np.dtype("<f8")
        id = SimpleNamespace(valid=True)
        file = SimpleNamespace(filename=grant["payload_path"])
        seen = []

        def __getitem__(self, key):
            selected, columns = key
            assert columns == slice(None)
            rows = (
                list(range(selected.start, selected.stop))
                if isinstance(selected, slice)
                else selected
            )
            self.seen.append(rows)
            out = np.zeros((len(rows), 2101), dtype="<f8")
            out[:, :3] = [10, 0.1, 0.2]
            return out

    class Toy:
        calls = 0

        def state_dict(self):
            return {}

        def score(self, values, feature_names):
            self.calls += 1
            assert values.flags.owndata and values.dtype == np.float32
            # Deliberately shape-dependent public results: same-shaped references are essential.
            return np.full(len(values), len(values), dtype="<f8")

    dataset = Dataset()
    chain = provider.Chain(
        dataset, approval, permit.path, lambda: 1, permit.deadline, permit=permit
    )
    models = {
        name: (Toy(), np.array([1, 2, 8, 32], dtype="<f8")) for name in plan.CANDIDATES
    }
    channels = p.load()["channels"]
    return folder, chain, dataset, models, channels


def bind(
    chain,
    models,
    channels,
    b=32,
    m=8,
    side="natural_m",
    phase="pre",
    reference=False,
    pos=None,
):
    actual, sb = plan.mapping(b, m, side)
    context = dict(
        B=b,
        m=m,
        side=side,
        actual_rows=actual,
        model_shape_rows=sb,
        wrapper=plan.WRAPPER,
        case_class=plan.case_class(b, m),
        candidate="pca-v1",
        phase=phase,
        window_position=plan.windows(b)[1] if pos is None else pos,
    )
    model, thresholds = models["pca-v1"]
    chain.reset()
    chain.bind(context, model, thresholds, channels, reference=reference)
    return context, model, thresholds


def test_pure_complete_paired_plan_and_geometry():
    counts = plan.counts()
    assert counts["timed"] == dict(calls=7680, rows=303240)
    assert counts["warmup"] == dict(calls=1152, rows=45486)
    assert counts["chain_gates"] == dict(calls=4608, rows=181944)
    assert counts["golden_references"] == dict(calls=2304, rows=90972)
    assert counts["public_service"] == dict(calls=15744, rows=621642)
    assert counts["decision_boolean_values"] == 2486568
    assert counts["per_worker"] == dict(
        raw_calls=4480,
        raw_rows=176890,
        service_calls=5248,
        service_rows=207214,
        reference_calls=768,
        reference_rows=30324,
    )
    ids = np.arange(1024, dtype="<i8") * 3
    geometry = plan.geometry(ids)
    assert sum(r["logical_raw_requests"] for r in geometry["windows"]) == 13440
    assert geometry["unique_raw_rows"] == 384
    assert geometry["repeated_no_cache_decoded_upper_bytes"] == sum(
        r["logical_raw_requests"] * r["per_request_decoded_upper_bytes"]
        for r in geometry["windows"]
    )
    union = set()
    for rep in (1, 2, 3):
        assert plan.candidates(rep)[0] == (
            "compact-autoencoder-v2" if rep == 2 else "pca-v1"
        )
        for candidate in plan.candidates(rep):
            rows = list(plan.schedule(rep, candidate))
            assert len(rows) == 1472
            assert (rows[0]["B"], rows[0]["m"]) == ((128, 128) if rep == 2 else (1, 1))
            for b, m in plan.CASES:
                for phase, n in [("warmup", 3), ("timed", 20)]:
                    block = [
                        r for r in rows if (r["B"], r["m"], r["phase"]) == (b, m, phase)
                    ]
                    assert len(block) == 2 * n
                    for i in range(n):
                        pair = block[2 * i : 2 * i + 2]
                        assert pair[0]["side"] == (
                            plan.SIDES[0] if i % 2 == 0 else plan.SIDES[1]
                        )
                        assert pair[0]["pair_id"] == pair[1]["pair_id"]
                        assert (
                            pair[0]["window_position"]
                            == pair[1]["window_position"]
                            == plan.windows(b)[i % 3]
                        )
                        for r in pair:
                            union.update(
                                ids[
                                    r["window_position"] : r["window_position"]
                                    + r["actual_rows"]
                                ]
                            )
    assert len(union) == 384


@pytest.mark.parametrize("b,m", plan.CASES)
def test_unchanged_owned_mapping_full_extra_rows_and_null_identity(b, m):
    channels = p.load()["channels"]
    values = np.arange(b * 8, dtype="<f4").reshape(b, 8)

    class Toy:
        def score(self, x, feature_names):
            assert x.flags.owndata and not np.shares_memory(x, values)
            return x[:, 0].astype("<f8")

    results = {}
    for side in plan.SIDES:
        actual, sb = plan.mapping(b, m, side)
        source = values[:actual].copy()
        owned = pack(source, b, m, side)
        assert owned.shape == (actual, 8) and not np.shares_memory(owned, source)
        scores, masks = service(
            Toy(),
            np.array([0, 8, 16, 24], dtype="<f8"),
            channels,
            source,
            b,
            m,
            side,
        )
        assert scores.shape == (actual,) and masks.shape == (actual, 4)
        assert np.array_equal(
            masks, scores[:, None] > np.array([0, 8, 16, 24])[None, :]
        )
        results[side] = (scores, masks)
    assert len(results["full_B_control"][0]) == b
    if b == m:
        assert all(
            n.tobytes() == f.tobytes() for n, f in zip(*results.values(), strict=True)
        )
    assert plan.mapping(32, 8, "natural_m") == (8, 8)
    assert plan.mapping(128, 32, "natural_m") == (32, 32)


def test_each_side_uses_its_own_exact_B_based_selection(emitted):
    _, chain, dataset, models, channels = setup(emitted)
    chain.register(models, channels)
    for side in plan.SIDES:
        context, model, thresholds = bind(chain, models, channels, side=side)
        req = chain.approval.ids[
            context["window_position"] : context["window_position"]
            + context["actual_rows"]
        ]
        features, scores, masks = chain.joint(
            req, parameters(), model, thresholds, channels
        )
        assert len(features) == len(scores) == len(masks) == context["actual_rows"]
    assert len(dataset.seen) == 2
    assert dataset.seen[0] == dataset.seen[1][:8] and len(dataset.seen[1]) == 32
    assert chain.raw_calls == chain.feature_calls == chain.service_calls == 2


def test_selection_interval_covers_only_the_complete_requested_ID_set():
    assert provider.exact_selection(np.arange(8, dtype="<i8")) == slice(0, 8)
    assert provider.exact_selection(np.arange(8, dtype="<i8") * 3) == list(
        range(0, 24, 3)
    )


def test_copied_permit_cannot_change_path_prefix_phase_or_deadline(emitted):
    from dataclasses import replace

    context, folder, grant, _ = granted(emitted)
    _, permit = p.validate_grant(folder, grant["token"], lambda: 1, root=context.root)
    for changed in (
        {"path": "/foreign"},
        {"prefix": "0" * 64},
        {"phase": "repetition2"},
        {"deadline": 9999},
        {},
    ):
        with pytest.raises(ValueError):
            p.verify_payload(replace(permit, **changed))


@pytest.mark.parametrize(
    "fault",
    [
        "adjacent",
        "different_window",
        "length",
        "duplicates",
        "dtype",
        "repeat",
        "budget",
        "deadline",
    ],
)
def test_denied_read_before_backend(emitted, fault):
    _, chain, dataset, models, channels = setup(emitted)
    chain.register(models, channels)
    context, _, _ = bind(chain, models, channels)
    req = chain.approval.ids[
        context["window_position"] : context["window_position"] + 8
    ].copy()
    if fault == "adjacent":
        req[0] += 1
    if fault == "different_window":
        req = chain.approval.ids[:8]
    if fault == "length":
        req = req[:7]
    if fault == "duplicates":
        req[1] = req[0]
    if fault == "dtype":
        req = req.astype("<i4")
    if fault == "repeat":
        chain.read_started = True
    if fault == "budget":
        chain.raw_calls = 4480
    if fault == "deadline":
        chain.deadline = 0
    with pytest.raises(ValueError):
        chain.read(req)
    assert dataset.seen == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("B", 1024),
        ("m", 9),
        ("side", "padded"),
        ("actual_rows", 32),
        ("model_shape_rows", 32),
        ("window_position", 508),
        ("candidate", "foreign"),
        ("phase", "fit"),
    ],
)
def test_wrong_case_side_mapping_state_before_backend(emitted, field, value):
    _, chain, dataset, models, channels = setup(emitted)
    chain.register(models, channels)
    context, model, thresholds = bind(chain, models, channels)
    chain.reset()
    context[field] = value
    with pytest.raises(ValueError):
        chain.bind(context, model, thresholds, channels)
    assert dataset.seen == []


@pytest.mark.parametrize("failure", ["raw", "feature", "adapter"])
def test_nested_failure_preserves_request_actual_completion_and_uncertainty(
    emitted, monkeypatch, failure
):
    folder, chain, _, models, channels = setup(emitted)
    chain.register(models, channels)
    context, model, thresholds = bind(chain, models, channels, b=8, m=2)
    ledger = provider.Ledger(folder)

    def stop(*a, **kw):
        setattr(
            chain,
            {
                "raw": "read_started",
                "feature": "feature_started",
                "adapter": "adapter_started",
            }[failure],
            True,
        )
        raise RuntimeError("generated interrupted stage")

    monkeypatch.setattr(
        chain,
        {"raw": "read", "feature": "features", "adapter": "public"}[failure],
        stop,
    )
    ledger.start("chain_gate", "pca-v1", 2, chain=True, context=context)
    with pytest.raises(RuntimeError):
        chain.joint(chain.expected_request, parameters(), model, thresholds, channels)
    ledger.finish(chain, success=False)
    audit = p.read(folder / "access.json")
    assert audit["raw_requested_rows"] == 2
    assert audit["raw_returned_rows"] == (0 if failure == "raw" else 2)
    assert audit["feature_completed_rows"] == (2 if failure == "adapter" else 0)
    assert audit["adapter_completed_rows"] == 0 and audit["inflight"] is not None
    assert audit["inflight"]["nested_progress"]["adapter_started"] == (
        failure == "adapter"
    )


def test_complete_same_shaped_gates_and_schedule_without_extra_service(emitted):
    folder, chain, dataset, models, channels = setup(emitted)
    # Two shape-dependent toy models; no setup or diagnostic forwards.
    hashes = {
        c: (measure.core.parameter_hash(model), measure.block_hash(t))
        for c, (model, t) in models.items()
    }
    golden = np.repeat(
        provider.construct(
            np.array([[10, 0.1, 0.2] + [0] * 2098], dtype="<f8"), parameters()
        ),
        1024,
        axis=0,
    )
    ledger = provider.Ledger(folder)
    measure.run(
        chain,
        golden,
        parameters(),
        ledger,
        folder,
        1,
        SimpleNamespace(check=lambda: None, boundary=lambda *a: None, clock=lambda: 1),
        models,
        hashes,
        lambda: None,
    )
    assert len(dataset.seen) == chain.raw_calls == chain.feature_calls == 4480
    assert chain.service_calls == 5248 and chain.reference_calls == 768
    assert {c: model.calls for c, (model, _) in models.items()} == {
        c: 2624 for c in plan.CANDIDATES
    }
    agg = p.read(folder / "aggregate.json")
    assert (
        len(agg["cells"]) == 128
        and len(agg["pairs"]) == 1280
        and len(agg["gates"]) == 768
    )
    assert all(c["count"] == 20 for c in agg["cells"])
    refs = {
        (g["B"], g["m"], g["side"]): g["reference_identity"]["scores"]
        for g in agg["gates"]
    }
    assert refs[(32, 8, "natural_m")] != refs[(32, 8, "full_B_control")]
    assert agg["raw_window_buffers_retained"] == 0 and agg["unique_raw_rows"] == 384
    from copy import deepcopy

    from raregate.benchmarks.targeted_raw_reporting import validate_worker

    agg["task"] = "0047"
    validate_worker(agg, 1)
    for fault in (
        "duplicate_pair",
        "wrong_pair_shape",
        "missing_gate",
        "wrong_gate_case",
        "changed_post_reference",
        "wrong_cell_rows",
    ):
        changed = deepcopy(agg)
        if fault == "duplicate_pair":
            changed["pairs"][-1] = changed["pairs"][0]
        if fault == "wrong_pair_shape":
            changed["pairs"][0]["natural_model_shape_rows"] = 128
        if fault == "missing_gate":
            changed["gates"].pop()
        if fault == "wrong_gate_case":
            changed["gates"][0]["m"] = 2
        if fault == "changed_post_reference":
            changed["gates"][90]["reference_identity"]["scores"] = "0" * 64
        if fault == "wrong_cell_rows":
            changed["cells"][0]["actual_rows"] = 128
        with pytest.raises(ValueError):
            validate_worker(changed, 1)


@pytest.mark.parametrize("fault", ["label", "empty", "padding", "nonfinite"])
def test_unchanged_feature_semantics(fault):
    raw = np.zeros((1, 2101), dtype="<f8")
    raw[0, :3] = [10, 0.1, 0.2]
    if fault == "label":
        raw[0, -1] = 1
    if fault == "empty":
        raw.fill(0)
    if fault == "padding":
        raw[0, 7] = 1
    if fault == "nonfinite":
        raw[0, 2] = np.nan
    with pytest.raises(ValueError):
        provider.construct(raw, parameters())


def test_full_particle_tail_remains_in_aggregates():
    raw = np.zeros((1, 2101), dtype="<f8")
    raw[0, :1500] = np.tile([1, 0.1, 0.2], 500)
    full = provider.construct(raw, parameters())
    raw[0, 384 * 3 :] = 0
    assert full[0, 0] > provider.construct(raw, parameters())[0, 0]


@pytest.mark.parametrize("fault", ["features", "scores", "decisions"])
def test_same_shaped_gate_refuses_any_output_byte_mutation(emitted, monkeypatch, fault):
    folder, chain, _, models, _ = setup(emitted)
    hashes = {
        c: (measure.core.parameter_hash(model), measure.block_hash(t))
        for c, (model, t) in models.items()
    }
    golden = np.repeat(
        provider.construct(
            np.array([[10, 0.1, 0.2] + [0] * 2098], dtype="<f8"), parameters()
        ),
        1024,
        axis=0,
    )
    original = chain.joint

    def corrupt(*a, **kw):
        f, s, m = original(*a, **kw)
        values = {"features": f, "scores": s, "decisions": m}[fault]
        values.view("u1").flat[0] ^= 1
        return f, s, m

    monkeypatch.setattr(chain, "joint", corrupt)
    ledger = provider.Ledger(folder)
    with pytest.raises(ValueError):
        measure.run(
            chain,
            golden,
            parameters(),
            ledger,
            folder,
            1,
            SimpleNamespace(
                check=lambda: None, boundary=lambda *a: None, clock=lambda: 1
            ),
            models,
            hashes,
            lambda: None,
        )
    assert ledger.audit["inflight"] is not None
    assert chain.raw_calls == 1 and chain.service_calls == 2
    assert not (folder / "aggregate.json").exists()


@pytest.mark.parametrize(
    "fault",
    [
        "features_before_read",
        "service_before_features",
        "reference_read",
        "wrong_model",
        "wrong_thresholds",
        "service_budget",
        "reference_budget",
        "wrong_model_shape_rows",
        "oversized_array",
    ],
)
def test_stage_and_model_authority_denials(emitted, fault):
    _, chain, dataset, models, channels = setup(emitted)
    chain.register(models, channels)
    context, model, thresholds = bind(
        chain,
        models,
        channels,
        reference=fault in ("reference_read", "reference_budget"),
    )
    raw = np.zeros((8, 2101), dtype="<f8")
    raw[:, :3] = [10, 0.1, 0.2]
    features = np.zeros((8, 8), dtype="<f4")
    if fault == "service_budget":
        chain.service_calls = 5248
    if fault == "reference_budget":
        chain.reference_calls = 768
    if fault == "oversized_array":
        chain.retained_bytes = 64 * 2**20
    with pytest.raises(ValueError):
        if fault == "features_before_read":
            chain.features(raw, parameters())
        elif fault in ("reference_read", "oversized_array"):
            chain.read(chain.expected_request)
        elif fault in ("wrong_model", "wrong_thresholds"):
            chain.reset()
            chain.bind(
                context,
                object() if fault == "wrong_model" else model,
                thresholds.copy() if fault == "wrong_thresholds" else thresholds,
                channels,
            )
        else:
            chain.constructed = fault != "service_before_features"
            chain.public(
                model,
                thresholds,
                channels,
                features,
                32 if fault == "wrong_model_shape_rows" else 8,
            )
    assert dataset.seen == []


def test_journal_growth_refused_before_write(tmp_path):
    ledger = provider.Ledger(tmp_path)
    journal = tmp_path / "access-journal.jsonl"
    with journal.open("wb") as f:
        f.truncate(16 * 2**20 - 64 * 1024)
    before = journal.stat().st_size
    with pytest.raises(ValueError, match="before growth"):
        ledger.append(dict(operation="denied"))
    assert journal.stat().st_size == before
