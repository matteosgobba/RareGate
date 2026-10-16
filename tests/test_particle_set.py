"""Particle design correctness and gates on synthetic values only."""

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest
import torch

from raregate.data.features import Parameters
from raregate.data.processed import ProcessedStore, content_hash
from raregate.models import particle_background as bg
from raregate.models.autoencoder import validate_config as validate_ae
from raregate.models.particle_set import (
    ParticleSetAutoencoder,
    _event_loss,
    design,
    event_loss,
    executable_config,
    validate_batch,
    validate_completion,
    validate_config,
)
from raregate.training import particle_set as training
from raregate.training.autoencoder import EarlyStopping, deterministic_cpu


@pytest.fixture
def config():
    return executable_config()


def values(counts=(1, 2, 384), *, grad=False):
    generator = torch.Generator().manual_seed(61)
    x = torch.randn(len(counts), 384, 4, generator=generator)
    phi = x[:, :, 2].clone()
    x[:, :, 2], x[:, :, 3] = phi.sin(), phi.cos()
    mask = torch.arange(384)[None, :] < torch.tensor(counts)[:, None]
    x[~mask] = 0
    return x.requires_grad_(grad), mask


def completion(config):
    spec = config["input"]
    provenance = {
        "scope": "canonical_full",
        "processed_scientific_sha256": spec["processed_full_scientific_sha256"],
        **{
            k: spec[k]
            for k in (
                "source_sha256",
                "preprocessing_config_sha256",
                "split_identity_sha256",
            )
        },
    }
    record = {
        "training_count": 699957,
        "selection_count": 74749,
        "stopping_reason": "patience",
        "best_epoch": 1,
        "epochs_executed": 21,
        "bad_epochs_at_stop": 20,
        "history_sha256": "a" * 64,
        "selection_score_sha256": "b" * 64,
        **{
            k: True
            for k in (
                "synthetic_gate",
                "dev_gate",
                "resource_gate",
                "restored_verified",
                "reproduction_verified",
            )
        },
    }
    return record, provenance


def fake_probe(**updates):
    result = {
        "available_bytes": 10 * 2**30,
        "peak_rss_bytes": 100 * 2**20,
        "native_heap_reserved_bytes": 120 * 2**20,
    }
    result.update(updates)
    return lambda: result


def monitor(config, **options):
    return training.ResourceMonitor(
        config["resource_gate"], probe=fake_probe(), monitor_background=False, **options
    )


def synthetic_store(n=67):
    """Real reader methods on tiny in-memory physical records (no real arrays)."""
    store = ProcessedStore.__new__(ProcessedStore)
    store.parameters = Parameters.from_config(
        json.loads(
            (Path(__file__).parents[1] / "configs/data/lhco_rnd_v5.json").read_text()
        )
    )
    counts = np.full(n, 2, dtype=np.uint16)
    particles = np.tile([[10.0, 0.5, 0.7], [1.0, -0.2, -0.6]], (n, 1)).astype(
        np.float32
    )
    store._arrays = {
        "split_codes": np.ones(n, dtype=np.uint8),
        "development": np.ones(n, dtype=bool),
        "event_ids": np.arange(n, dtype=np.int64) * 7,
        "multiplicities": counts,
        "offsets": np.arange(n + 1, dtype=np.int64) * 2,
        "particles": particles,
        "original_slots": np.tile(np.array([0, 1], dtype=np.uint16), n),
        "event_aggregates": np.zeros((n, 8)),
        "event_features": np.zeros((n, 8), dtype=np.float32),
    }
    return store


def test_exact_architecture_initialization_and_config_mapping(config):
    saved = json.loads(
        (
            Path(__file__).parents[1]
            / "configs/models/compact_particle_set_autoencoder_v1.json"
        ).read_text()
    )
    assert saved == config
    validate_config(config)
    with deterministic_cpu(1729, 1):
        model = ParticleSetAutoencoder()
    with deterministic_cpu(1729, 1):
        layers = [
            torch.nn.Linear(a, b, dtype=torch.float32)
            for a, b in [(4, 16), (16, 8), (8, 2), (10, 16), (16, 4)]
        ]
    expected = [v for layer in layers for v in layer.parameters()]
    assert all(
        torch.equal(a, b) for a, b in zip(model.parameters(), expected, strict=True)
    )
    assert model.parameter_count == 478
    assert sum(p.numel() * p.element_size() for p in model.parameters()) == 1912
    assert list(model.state_dict()) == config["architecture"]["parameter_order"]
    assert [list(p.shape) for p in model.parameters()] == config["architecture"][
        "parameter_shapes"
    ]
    assert model.relu.inplace is False
    with pytest.raises(ValueError):
        validate_config(design())
    with pytest.raises(ValueError):
        validate_ae(design())


@pytest.mark.parametrize(
    "path,value",
    [
        (["training", "batch_size"], 64),
        (["training", "optimizer", "foreach"], True),
        (["objective", "channel_weights"], [1, 1, 1, 1]),
        (["status"], "design_only"),
        (["schema_version"], True),
        (["input", "nmax"], 383),
    ],
)
def test_executable_config_refuses_drift(config, path, value):
    obj = config
    for key in path[:-1]:
        obj = obj[key]
    obj[path[-1]] = value
    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize(
    "angular,predicted,expected", [(0, 0, 0), (0, None, 1 / 6), (0, math.pi, 2 / 3)]
)
def test_hand_angular_cases(angular, predicted, expected):
    x, mask = values((1,))
    x[0, 0] = torch.tensor([0.0, 0.0, math.sin(angular), math.cos(angular)])
    y = x.clone()
    y[0, 0, 2:] = (
        0
        if predicted is None
        else torch.tensor([math.sin(predicted), math.cos(predicted)])
    )
    assert event_loss(x, y, mask).dtype == torch.float64
    assert event_loss(x, y, mask).item() == pytest.approx(
        expected, abs=1e-12, rel=1e-12
    )


def test_weighted_score_seam_offcircle_and_event_weights():
    x, mask = values((1, 2))
    x[:, :, 0] = 0
    y = x.clone()
    y[:, 0, 0] -= 1
    losses = event_loss(x, y, mask)
    np.testing.assert_allclose(losses.numpy(), [1 / 3, 1 / 6], atol=1e-12, rtol=1e-12)
    assert losses.mean().item() == 0.25
    assert losses.sum().item() / 3 != 0.25
    x, mask = values((1,))
    x[0, 0] = torch.tensor([0, 0, 0, 1])
    y = x.clone()
    y[0, 0, 3] = 2
    assert event_loss(x, y, mask).item() == pytest.approx(1 / 6, abs=1e-12)
    eps = 0.001
    x[0, 0, 2:] = torch.tensor([math.sin(math.pi - eps), math.cos(math.pi - eps)])
    y[0, 0, 2:] = torch.tensor([math.sin(-math.pi + eps), math.cos(-math.pi + eps)])
    assert event_loss(x, y, mask).item() == pytest.approx(
        2 * math.sin(eps) ** 2 / 3, abs=1e-12, rel=1e-12
    )


def test_masked_gradients_padding_and_autograd_precision():
    with deterministic_cpu(1729, 1):
        model = ParticleSetAutoencoder()
    x, mask = values((1, 7, 384), grad=True)
    y = model(x, mask)
    local, context = model.encode(x, mask)
    loss = event_loss(x, y, mask).mean()
    loss.backward()
    assert torch.count_nonzero(x.grad[~mask]) == 0
    assert torch.count_nonzero(x.grad[mask]) > 0
    assert torch.count_nonzero(y[~mask]) == torch.count_nonzero(local[~mask]) == 0
    assert all(
        p.grad.dtype == torch.float32 and torch.isfinite(p.grad).all()
        for p in model.parameters()
    )
    assert all(p.grad.abs().sum() > 0 for p in model.parameters())
    changed = x.detach().clone()
    changed[~mask] = torch.finfo(torch.float32).max
    assert torch.equal(model(changed, mask), y)
    assert torch.equal(model.encode(changed, mask)[1], context)
    np.testing.assert_array_equal(
        model.score(changed, mask), model.score(x.detach(), mask)
    )


def test_permutation_equivariance_global_score_and_aligned_gradients():
    torch.manual_seed(1729)
    model = ParticleSetAutoencoder()
    x, mask = values((23,), grad=True)
    order = torch.cat((torch.randperm(23), torch.arange(23, 384)))
    inverse = order.argsort()
    perm = x.detach()[:, order].clone().requires_grad_(True)
    y = model(x, mask)
    py = model(perm, mask)
    torch.testing.assert_close(y, py[:, inverse], atol=1e-6, rtol=1e-5)
    for a, b in zip(model.encode(x, mask), model.encode(perm, mask), strict=True):
        torch.testing.assert_close(
            a, b[:, inverse] if a.ndim == 3 else b, atol=1e-6, rtol=1e-5
        )
    np.testing.assert_allclose(
        model.score(x, mask), model.score(perm, mask), atol=1e-8, rtol=1e-6
    )
    event_loss(x, y, mask).sum().backward()
    event_loss(perm, py, mask).sum().backward()
    torch.testing.assert_close(x.grad, perm.grad[:, inverse], atol=1e-6, rtol=1e-5)
    holes = torch.randperm(384)
    px = x.detach()[:, holes]
    pm = mask[:, holes]
    with pytest.raises(ValueError, match="prefix"):
        model(px, pm)
    hy, hl, hg = model._forward_set(px, pm)
    torch.testing.assert_close(hy[:, holes.argsort()], y, atol=1e-6, rtol=1e-5)
    torch.testing.assert_close(hg, model.encode(x, mask)[1], atol=1e-6, rtol=1e-5)
    np.testing.assert_allclose(
        _event_loss(px, hy, pm).detach().numpy(),
        model.score(x, mask),
        atol=1e-8,
        rtol=1e-6,
    )


def test_uniform_replication_and_repeated_particles():
    model = ParticleSetAutoencoder()
    x, m = values((3,))
    xx = x.clone()
    xx[0, :9] = x[0, :3].repeat_interleave(3, dim=0)
    mm = torch.arange(384)[None, :] < 9
    np.testing.assert_allclose(
        model.score(x, m), model.score(xx, mm), atol=1e-8, rtol=1e-6
    )
    yy = model(xx, mm)
    torch.testing.assert_close(yy[0, 0], yy[0, 1], atol=1e-6, rtol=1e-5)


@pytest.mark.parametrize(
    "failure",
    [
        "dtype",
        "mask_dtype",
        "shape",
        "mask_shape",
        "empty",
        "all_padding",
        "holes",
        "nan_padding",
        "inf_valid",
        "bad_angle",
        "device",
    ],
)
def test_bad_inputs_rejected(failure):
    x, m = values((2,))
    if failure == "dtype":
        x = x.double()
    elif failure == "mask_dtype":
        m = m.int()
    elif failure == "shape":
        x = x[:, :, :3]
    elif failure == "mask_shape":
        m = m[:, :383]
    elif failure == "empty":
        x, m = x[:0], m[:0]
    elif failure == "all_padding":
        m.zero_()
    elif failure == "holes":
        m[0, 1] = False
        m[0, 2] = True
    elif failure == "nan_padding":
        x[0, 3, 0] = float("nan")
    elif failure == "inf_valid":
        x[0, 0, 0] = float("inf")
    elif failure == "bad_angle":
        x[0, 0, 2:] = 0
    elif failure == "device":
        x = x.to("meta")
    with pytest.raises(ValueError):
        validate_batch(x, m)


@pytest.mark.parametrize(
    "failure", ["parameter_nan", "non_fp32", "intermediate_overflow", "output_nan"]
)
def test_nonfinite_and_parameter_failures(failure):
    model = ParticleSetAutoencoder()
    x, m = values((2,))
    with torch.no_grad():
        if failure == "parameter_nan":
            model.e1.weight[0, 0] = float("nan")
        elif failure == "non_fp32":
            model.double()
        elif failure == "intermediate_overflow":
            model.e1.weight.fill_(torch.finfo(torch.float32).max)
            x[0, 0, 0] = 10
        elif failure == "output_nan":
            model.d2.bias[0] = float("nan")
    with pytest.raises(ValueError):
        model(x, m)


def test_artifact_roundtrip_status_and_frozen_identity(config, tmp_path):
    model = ParticleSetAutoencoder()
    record, prov = completion(config)
    artifact = model.artifact(
        config=config, provenance=prov, training=record, finalized=True
    )
    path = tmp_path / "model.json"
    path.write_text(json.dumps(artifact))
    loaded = ParticleSetAutoencoder.load(path)
    assert (
        loaded.artifact(config=config, provenance=prov, training=record, finalized=True)
        == artifact
    )
    x, m = values((1, 4))
    np.testing.assert_array_equal(model.score(x, m), loaded.score(x, m))
    candidate = model.artifact(config=config, provenance={}, training={})
    with pytest.raises(ValueError):
        ParticleSetAutoencoder.from_artifact(candidate)
    ParticleSetAutoencoder.from_artifact(candidate, allow_candidate=True)


@pytest.mark.parametrize(
    "mutation",
    [
        "hash",
        "type",
        "version",
        "shape",
        "order",
        "dtype",
        "inexact",
        "source",
        "scope",
        "completion",
        "config",
        "nonfinite",
        "bool_version",
    ],
)
def test_corrupt_or_rehashed_incompatible_artifacts(config, mutation):
    record, prov = completion(config)
    artifact = ParticleSetAutoencoder().artifact(
        config=config, provenance=prov, training=record, finalized=True
    )
    s = artifact["scientific"]
    if mutation == "hash":
        s["parameters"][0]["values"][0][0] += 1
    elif mutation == "type":
        s["model_type"] = "compact_autoencoder"
    elif mutation == "version":
        artifact["artifact_version"] = 2
    elif mutation == "bool_version":
        artifact["artifact_version"] = True
    elif mutation == "shape":
        s["parameters"][0]["shape"] = [4, 16]
    elif mutation == "order":
        s["parameters"].reverse()
    elif mutation == "dtype":
        s["parameters"][0]["dtype"] = "float64"
    elif mutation == "inexact":
        s["parameters"][0]["values"][0][0] = 0.123456789
    elif mutation == "source":
        s["provenance"]["source_sha256"] = "f" * 64
    elif mutation == "scope":
        s["provenance"]["scope"] = "dev_diagnostic"
    elif mutation == "completion":
        s["training"]["reproduction_verified"] = False
    elif mutation == "config":
        s["config"]["training"]["batch_size"] = 64
    elif mutation == "nonfinite":
        s["parameters"][0]["values"][0][0] = float("inf")
    if mutation not in ["hash", "nonfinite"]:
        artifact["scientific_sha256"] = content_hash(s)
    with pytest.raises(ValueError):
        ParticleSetAutoencoder.from_artifact(artifact)


@pytest.mark.parametrize(
    "field,value",
    [
        ("epochs_executed", 200),
        ("best_epoch", True),
        ("stopping_reason", "max_epochs"),
        ("dev_gate", False),
        ("training_count", 1024),
    ],
)
def test_completion_prevents_invalid_promotion(config, field, value):
    record, prov = completion(config)
    record[field] = value
    with pytest.raises(ValueError):
        validate_completion(record, prov)


def test_reader_shuffle_coverage_tail_no_repeated_filtering():
    store = synthetic_store()
    order = np.random.default_rng(1729).permutation(67)
    original = store._positions
    calls = []

    def positions(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    store._positions = positions
    batches = list(store.iter_batches("train_background", batch_size=32, order=order))
    assert [len(b.event_ids) for b in batches] == [32, 32, 3]
    assert len(calls) == 1
    np.testing.assert_array_equal(
        np.concatenate([b.event_ids for b in batches]), order * 7
    )
    assert all(b.labels is None for b in batches)
    sequential = list(store.iter_batches("train_background", batch_size=32))
    np.testing.assert_array_equal(
        np.concatenate([b.event_ids for b in sequential]), np.arange(67) * 7
    )


@pytest.mark.parametrize(
    "order",
    [
        np.arange(66),
        np.zeros(67, dtype=int),
        np.arange(67, dtype=float),
        np.arange(67) + 1,
        np.arange(67).reshape(1, 67),
        np.ones(67, dtype=bool),
    ],
)
def test_reader_bad_shuffle_refused_before_particle_read(order):
    store = synthetic_store()
    store._batch = lambda *a, **k: pytest.fail("must reject before particle read")
    with pytest.raises(ValueError):
        list(store.iter_batches("train_background", batch_size=32, order=order))


def test_particle_stream_uses_real_model_view_and_keeps_metadata_outside():
    store = synthetic_store()
    audit = bg.Audit()
    batches = bg.ParticleBatches(
        store, "train_background", audit, stage="fit", purpose="synthetic"
    )
    received = list(batches())
    assert [len(x) for x, m, meta in received] == [32, 32, 3]
    x, m, meta = received[0]
    assert x.shape == (32, 384, 4) and x.dtype == torch.float32
    assert m.dtype == torch.bool and (m.sum(1) == 2).all()
    assert not x[:, 2:].any() and "n_original" in meta
    assert (
        audit.records[0]["events_read"] == 67
        and audit.records[0]["status"] == "completed"
    )


@pytest.mark.parametrize(
    "split,stage,labels",
    [
        ("test_background", "fit", False),
        ("test_signal", "dev", False),
        ("unknown", "fit", False),
        ("train_background", "fit", True),
        ("validation_calibration_background", "fit", False),
        ("validation_selection_background", "dev", False),
    ],
)
def test_forbidden_role_or_truth_before_constructor(config, split, stage, labels):
    with pytest.raises(ValueError):
        bg.require_role(split, stage, include_labels=labels)
    with pytest.raises(ValueError):
        bg.open_store(
            Path("unused"),
            config,
            [split],
            stage=stage,
            factory=lambda p: pytest.fail("constructor called"),
        ) if not labels else bg.require_role(split, stage, include_labels=True)


def test_calibration_requires_every_gate(config):
    record, prov = completion(config)
    for key in [
        "synthetic_gate",
        "dev_gate",
        "resource_gate",
        "restored_verified",
        "reproduction_verified",
    ]:
        failed = copy.deepcopy(record)
        failed[key] = False
        with pytest.raises(ValueError):
            bg.require_role(
                "validation_calibration_background",
                "postfreeze",
                completion=(failed, prov),
            )
    bg.require_role(
        "validation_calibration_background", "postfreeze", completion=(record, prov)
    )


def test_failed_audit_and_tail_weighted_epoch(config, tmp_path):
    store = synthetic_store()
    audit = bg.Audit(tmp_path / "audit.json")
    batches = bg.ParticleBatches(
        store, "train_background", audit, stage="fit", purpose="synthetic"
    )
    store._batch = lambda *a, **k: (_ for _ in ()).throw(ValueError("read failure"))
    with pytest.raises(ValueError):
        list(batches())
    saved = json.loads((tmp_path / "audit.json").read_text())["population_access"][0]
    assert saved["status"] == "failed_or_interrupted" and saved["events_read"] == 0

    class Scorer:
        def train(self, *a):
            pass

        def score(self, x, mask):
            return x[:, 0, 0].double().numpy()

    x, m = values((1,) * 35)
    x[:, 0, 0] = torch.arange(35)
    stream = [(x[:32], m[:32], {}), (x[32:], m[32:], {})]
    mean, scores = training.epoch(Scorer(), stream, monitor(config), expected=35)
    assert mean == 17 and len(scores) == 35


def test_optimizer_options_and_nonzero_valid_updates(config):
    with deterministic_cpu(1729, 1):
        model = ParticleSetAutoencoder()
    opt = training.adam(model, config)
    before = [p.clone() for p in model.parameters()]
    x, m = values(
        (
            3,
            4,
        )
    )
    result = training.epoch(
        model, [(x, m, {})], monitor(config), optimizer=opt, expected=2
    )
    assert math.isfinite(result)
    assert any(
        not torch.equal(a, b) for a, b in zip(before, model.parameters(), strict=True)
    )
    assert opt.defaults["foreach"] is opt.defaults["fused"] is False
    assert opt.defaults["lr"] == 0.001 and opt.defaults["weight_decay"] == 0
    assert all(
        v.dtype == torch.float32
        for state in opt.state.values()
        for v in state.values()
        if isinstance(v, torch.Tensor)
    )


@pytest.mark.parametrize(
    "field,value,launch",
    [
        ("available_bytes", 7 * 2**30, True),
        ("available_bytes", 3 * 2**30, False),
        ("peak_rss_bytes", 7 * 2**30, False),
        ("native_heap_reserved_bytes", 513 * 2**20, False),
    ],
)
def test_live_memory_ceilings(config, field, value, launch):
    m = training.ResourceMonitor(
        config["resource_gate"],
        probe=fake_probe(**{field: value}),
        monitor_background=False,
    )
    with pytest.raises(training.ResourceLimitError):
        m.check(launch=launch)
    assert m.samples == 1


def test_time_deadline_interrupt_and_epoch_failure_history(config):
    now = [0.0]
    m = training.ResourceMonitor(
        config["resource_gate"],
        probe=fake_probe(),
        clock=lambda: now[0],
        monitor_background=False,
    )
    with pytest.raises(training.ResourceLimitError):
        with m.deadline("epoch_cycle", 180):
            now[0] = 181
            m.check()
    assert not m.deadlines


def test_stopping_ties_clone_restore_and_cap_priority():
    model = ParticleSetAutoencoder()
    stop = EarlyStopping(20, 0)
    with torch.no_grad():
        model.e1.bias.fill_(1)
    assert not stop.update(180, 1, model)
    with torch.no_grad():
        model.e1.bias.fill_(2)
    for ep in range(181, 200):
        assert not stop.update(ep, 1, model)
    assert stop.update(200, 1, model)
    stop.restore(model)
    assert torch.all(model.e1.bias == 1)
    assert stop.best_epoch == 180 and stop.bad_epochs == 20


def test_fit_strict_checkpoint_restoration_and_exact_repetition(config, monkeypatch):
    def run():
        calls = [0]

        def fake_epoch(model, batches, mon, *, optimizer=None, expected=None):
            if optimizer is not None:
                calls[0] += 1
                with torch.no_grad():
                    model.e1.bias.fill_(calls[0])
                return 0.5
            mean = 1.0 if calls[0] >= 3 else 2.0
            return mean, np.array([mean] * 4)

        monkeypatch.setattr(training, "epoch", fake_epoch)

        def train(order):
            return iter(())

        def selection():
            return iter(())

        train.role = "train_background"
        selection.role = "validation_selection_background"
        return training.fit(
            train, selection, config, monitor(config), train_count=4, selection_count=4
        )

    a, ha, ra = run()
    b, hb, rb = run()
    assert (
        ra["best_epoch"] == 3
        and ra["epochs_executed"] == 23
        and ra["stopping_reason"] == "patience"
    )
    assert torch.all(a.e1.bias == 3)
    assert ha == hb and ra == rb
    assert all(
        torch.equal(p, q) for p, q in zip(a.parameters(), b.parameters(), strict=True)
    )


def test_fit_refuses_calibration_factory_before_access(config):
    def forbidden():
        pytest.fail("read attempted")

    forbidden.role = "validation_calibration_background"
    with pytest.raises(ValueError):
        training.fit(forbidden, forbidden, config, monitor(config))


def test_profiles_tied_bins_empty_overflow_and_frozen_thresholds():
    scores = np.array([0.0, 1.0, 2.0, 3.0])
    variables = {
        "n_original": np.array([1, 1, 9, 99]),
        "truncation_flag": np.array([0, 0, 0, 1]),
    }
    rows = bg.profiles(
        scores,
        variables,
        {"n_original": np.array([2, 8]), "truncation_flag": np.array([0.5])},
        [{"threshold": 2.0}],
    )
    assert rows[1]["count"] == 0 and rows[1]["mean_score"] is None
    assert rows[2]["count"] == 2 and rows[2]["operating_points"][0]["accepted"] == 1


def test_reproduction_mismatch_blocks_freeze(config):
    record, prov = completion(config)
    a = ParticleSetAutoencoder().artifact(
        config=config, provenance=prov, training=record, finalized=True
    )
    b = copy.deepcopy(a)
    b["scientific_sha256"] = "c" * 64
    with pytest.raises(ValueError):
        bg.compare_repetitions(a, b)


def test_deadline_interrupts_a_blocked_operation(config):
    import time

    mon = training.ResourceMonitor(config["resource_gate"], probe=fake_probe())
    started = time.monotonic()
    with mon, pytest.raises(training.ResourceLimitError):
        with mon.deadline("synthetic_short_alarm", 0.02):
            time.sleep(0.3)
    assert time.monotonic() - started < 0.2


def test_failed_dev_supervisor_blocks_every_later_stage_and_retry(
    config, tmp_path, monkeypatch
):
    from types import SimpleNamespace

    monkeypatch.setattr(bg, "verify_acceptance", lambda *a: {})
    calls = []

    class Child:
        def __init__(self, command, **kwargs):
            calls.append(command)
            output = Path(command[command.index("--output") + 1])
            output.mkdir()
            (output / "stage-result.json").write_text(
                json.dumps(
                    {
                        "status": "failed_or_interrupted",
                        "error": "controlled dev failure",
                    }
                )
            )

        def wait(self, **kwargs):
            return 1

    monkeypatch.setattr(bg.subprocess, "Popen", Child)
    args = SimpleNamespace(
        output=tmp_path / "output",
        acceptance=tmp_path / "acceptance.json",
        config=tmp_path / "config.json",
        store=tmp_path / "full",
        dev_store=tmp_path / "dev",
    )
    result = bg.run_task(args, config, attempt_budget=tmp_path / "budget.json")
    assert result["status"] == "implementation_complete_canonical_pending"
    assert len(calls) == 1 and calls[0][calls[0].index("--worker") + 1] == "dev"
    assert not (args.output / "frozen-model.json").exists()
    args.output = tmp_path / "different-output"
    with pytest.raises(FileExistsError):
        bg.run_task(args, config, attempt_budget=tmp_path / "budget.json")


def test_dev_sample_shuffles_complete_first_1024_and_scores_source_order():
    store = synthetic_store(1100)
    audit = bg.Audit()
    ids = store.event_ids("train_background", dev_only=True)[:1024]
    batches = bg.ParticleBatches(
        store,
        "train_background",
        audit,
        stage="dev",
        purpose="synthetic_dev",
        dev=True,
        dev_ids=ids,
    )
    order = np.random.default_rng(1729).permutation(1024)
    received = list(batches(order))
    np.testing.assert_array_equal(
        np.concatenate([meta["event_ids"] for x, m, meta in received]), ids[order]
    )
    np.testing.assert_array_equal(
        np.concatenate([meta["event_ids"] for x, m, meta in batches()]), ids
    )
    store._batch = lambda *a, **k: pytest.fail(
        "malformed permutation reached particle reader"
    )
    with pytest.raises(ValueError):
        list(batches(np.zeros(1024, dtype=int)))


def test_fitting_incomplete_epoch_never_publishes_history(config, monkeypatch):
    completed = []

    def abort(*a, **k):
        raise training.ResourceLimitError("controlled epoch interruption")

    monkeypatch.setattr(training, "epoch", abort)

    def train(order):
        return iter(())

    def select():
        return iter(())

    train.role = "train_background"
    select.role = "validation_selection_background"
    with pytest.raises(training.ResourceLimitError):
        training.fit(
            train,
            select,
            config,
            monitor(config),
            on_epoch=lambda *a: completed.append(a),
            train_count=4,
            selection_count=4,
        )
    assert completed == []


def test_epoch_cap_remains_unresolved_and_cannot_freeze(config, monkeypatch):
    calls = [0]

    def controlled(model, batches, mon, *, optimizer=None, expected=None):
        if optimizer is not None:
            calls[0] += 1
            return 0.5
        value = 1 / (calls[0] + 1)
        return value, np.full(4, value, dtype=np.float64)

    monkeypatch.setattr(training, "epoch", controlled)

    def train(order):
        return iter(())

    def select():
        return iter(())

    train.role = "train_background"
    select.role = "validation_selection_background"
    model, history, record = training.fit(
        train, select, config, monitor(config), train_count=4, selection_count=4
    )
    assert len(history) == 200 and record["stopping_reason"] == "max_epochs"
    assert record["bad_epochs_at_stop"] == 0 and record["best_epoch"] == 200
    _valid, prov = completion(config)
    with pytest.raises(ValueError):
        model.artifact(config=config, provenance=prov, training=record, finalized=True)
