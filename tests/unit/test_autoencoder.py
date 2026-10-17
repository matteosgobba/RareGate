"""Small synthetic compact-AE tests; no real data or network access."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from raregate.data.inspection import AGGREGATE_NAMES
from raregate.data.processed import FeatureBatch, content_hash
from raregate.evaluation.run import run_final
from raregate.models.autoencoder import (
    CompactAutoencoder,
    validate_config,
    validate_input_store,
)
from raregate.models.background import load_background_features
from raregate.training.autoencoder import (
    EarlyStopping,
    feature_loader,
    train_autoencoder,
)
from raregate.training.background import run_background


@pytest.fixture
def config():
    return json.loads(
        (
            Path(__file__).parents[2] / "configs/models/compact_autoencoder.json"
        ).read_text()
    )


@pytest.fixture
def features():
    rng = np.random.default_rng(1729)
    return (rng.normal(size=(320, 2)) @ rng.normal(size=(2, 8))).astype(np.float32)


def test_architecture_parameter_count_latent_and_output():
    model = CompactAutoencoder()
    layers = [
        (m.in_features, m.out_features)
        for m in model.modules()
        if isinstance(m, torch.nn.Linear)
    ]
    assert layers == [(8, 6), (6, 3), (3, 6), (6, 8)]
    assert sum(isinstance(m, torch.nn.ReLU) for m in model.modules()) == 2
    assert model.parameter_count == 155
    assert isinstance(model.decoder[-1], torch.nn.Linear)
    assert model(torch.zeros(7, 8)).shape == (7, 8)
    assert model.encode(torch.zeros(7, 8)).shape == (7, 3)
    with pytest.raises(ValueError, match="dimension"):
        CompactAutoencoder(7)
    with pytest.raises(ValueError, match="input"):
        model(torch.zeros(7, 7))


def test_score_sse_zero_and_orientation():
    model = CompactAutoencoder()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
    values = np.zeros((3, 8), dtype=np.float32)
    values[1, 0], values[2, 0] = 1, 2
    np.testing.assert_array_equal(
        model.score(values, feature_names=AGGREGATE_NAMES), [0, 1, 4]
    )
    with pytest.raises(ValueError, match="order"):
        model.score(values, feature_names=AGGREGATE_NAMES[::-1])
    with pytest.raises(ValueError, match="FP32"):
        model.score(values.astype(np.float64), feature_names=AGGREGATE_NAMES)
    values[0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        model.score(values, feature_names=AGGREGATE_NAMES)


def test_exact_json_roundtrip_stable_identity_and_scoring(features, tmp_path):
    model = CompactAutoencoder()
    artifact = model.artifact(provenance={"synthetic": True}, training={})
    path = tmp_path / "model.json"
    path.write_text(json.dumps(artifact))
    loaded = CompactAutoencoder.load(path)
    for name, value in model.state_dict().items():
        assert torch.equal(value, loaded.state_dict()[name])
    assert artifact == loaded.artifact(provenance={"synthetic": True}, training={})
    np.testing.assert_array_equal(
        model.score(features, feature_names=AGGREGATE_NAMES),
        loaded.score(features, feature_names=AGGREGATE_NAMES),
    )
    artifact["scientific"]["parameters"][0]["values"][0][0] += 1
    with pytest.raises(ValueError, match="identity"):
        CompactAutoencoder.from_artifact(artifact)


@pytest.mark.parametrize(
    "mutation", ["shape", "names", "non_fp32", "architecture", "feature_order"]
)
def test_rehashed_inconsistent_artifact_rejected(mutation):
    artifact = CompactAutoencoder().artifact(provenance={}, training={})
    spec = artifact["scientific"]
    if mutation == "shape":
        spec["parameters"][0]["shape"] = [8, 6]
    elif mutation == "names":
        spec["parameters"].reverse()
    elif mutation == "non_fp32":
        spec["parameters"][0]["values"][0][0] = 0.1
    elif mutation == "architecture":
        spec["architecture"] = {**spec["architecture"], "latent_dim": 4}
    else:
        spec["features"].reverse()
    artifact["scientific_sha256"] = content_hash(spec)
    with pytest.raises(ValueError):
        CompactAutoencoder.from_artifact(artifact)


@pytest.mark.parametrize(
    "field,value",
    [
        ("learning_rate", 0),
        ("learning_rate", float("inf")),
        ("min_delta", -1),
        ("max_epochs", 0),
        ("batch_size", 0),
        ("num_workers", 2),
        ("num_threads", 0),
        ("seed", -1),
        ("device", "mps"),
        ("deterministic_algorithms", False),
    ],
)
def test_invalid_training_config(config, field, value):
    config["training"][field] = value
    with pytest.raises(ValueError):
        validate_config(config)


def test_config_role_architecture_and_input_store_guards(config):
    for role in ("fit", "selection", "calibration"):
        bad = copy.deepcopy(config)
        bad["roles"][role] = "test_background"
        with pytest.raises(ValueError):
            validate_config(bad)
    manifest = {
        "schema_version": 1,
        "scientific": {
            "scope": "full",
            "aggregate_channels": list(AGGREGATE_NAMES),
            "config_sha256": config["input"]["preprocessing_config_sha256"],
        },
    }
    validate_input_store(manifest, config)
    manifest["scientific"]["scope"] = "dev"
    with pytest.raises(ValueError, match="scope"):
        validate_input_store(manifest, config)
    validate_input_store(manifest, config, dev=True)
    with pytest.raises(ValueError, match="refuses"):
        load_background_features(
            None, "test_signal", [], batch_events=32, dev_only=True
        )


def test_vectorized_loader_shuffle_reproduces_and_keeps_tail():
    features = np.arange(19 * 8, dtype=np.float32).reshape(19, 8)
    first = list(feature_loader(features, 6, shuffle=True, seed=1729))
    second = list(feature_loader(features, 6, shuffle=True, seed=1729))
    assert [len(batch) for batch in first] == [6, 6, 6, 1]
    assert all(torch.equal(a, b) for a, b in zip(first, second, strict=True))
    assert sorted(torch.cat(first)[:, 0].tolist()) == features[:, 0].tolist()
    assert not torch.equal(torch.cat(first), torch.from_numpy(features))


def test_early_stop_ties_patience_and_snapshot_restoration():
    model = CompactAutoencoder()
    stopper = EarlyStopping(patience=2, min_delta=0)
    assert not stopper.update(1, 1, model)
    snapshot = {k: v.clone() for k, v in model.state_dict().items()}
    with torch.no_grad():
        for p in model.parameters():
            p.add_(1)
    assert not stopper.update(2, 1, model)
    assert stopper.update(3, 1.1, model)
    stopper.restore(model)
    assert stopper.best_epoch == 1
    assert all(torch.equal(v, model.state_dict()[k]) for k, v in snapshot.items())


def test_training_reduces_loss_and_cpu_repeat_is_bitwise(features, config):
    config["training"].update(max_epochs=60, batch_size=64)
    first, history, result = train_autoencoder(features[:240], features[240:], config)
    second, history2, result2 = train_autoencoder(
        features[:240], features[240:], config
    )
    assert history[-1]["training_mse"] < history[0]["training_mse"] * 0.6
    assert history == history2 and result == result2
    assert all(
        torch.equal(v, second.state_dict()[k]) for k, v in first.state_dict().items()
    )
    assert result["restored_selection_mse"] == result["best_selection_mse"]


def test_training_best_state_restored_after_patience(features, config):
    config["training"].update(
        max_epochs=10, batch_size=64, min_delta=100, early_stopping_patience=2
    )
    model, history, result = train_autoencoder(features[:240], features[240:], config)
    assert result["epochs_executed"] == 3 and result["best_epoch"] == 1
    assert result["stopping_reason"] == "patience"
    config["training"]["max_epochs"] = 1
    epoch_one, _, _ = train_autoencoder(features[:240], features[240:], config)
    assert all(
        torch.equal(v, epoch_one.state_dict()[k]) for k, v in model.state_dict().items()
    )
    assert result["restored_selection_mse"] == history[0]["selection_mse"]


@pytest.fixture
def toy_store(features, config):
    class Store:
        calls = []
        populations = dict(
            zip(
                (
                    "train_background",
                    "validation_selection_background",
                    "validation_calibration_background",
                    "test_background",
                    "test_signal",
                ),
                (
                    features[:200],
                    features[200:260],
                    features[260:],
                    features[:20],
                    features[:20] + 20,
                ),
                strict=True,
            )
        )
        manifest = {
            "schema_version": 1,
            "scientific_sha256": "synthetic-only",
            "scientific": {
                "scope": "full",
                "aggregate_channels": list(AGGREGATE_NAMES),
                "config_sha256": config["input"]["preprocessing_config_sha256"],
                "counts": {k: len(v) for k, v in populations.items()},
                "source": {"dataset": "synthetic"},
                "source_integrity": {"sha256": "toy"},
                "split_identity_sha256": "toy",
            },
        }

        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def event_ids(self, split, *, dev_only=False):
            return np.arange(10 if dev_only else len(self.populations[split]))

        def iter_features(
            self,
            split,
            *,
            batch_size,
            allow_test=False,
            include_labels=False,
            dev_only=False,
        ):
            self.calls.append((split, allow_test, include_labels))
            if split.startswith("test_"):
                assert allow_test and include_labels
            values = (
                self.populations[split][:10] if dev_only else self.populations[split]
            )
            for start in range(0, len(values), batch_size):
                batch = values[start : start + batch_size]
                labels = (
                    np.full(len(batch), split == "test_signal", dtype=np.uint8)
                    if include_labels
                    else None
                )
                yield FeatureBatch(batch, np.arange(len(batch)), labels)

    return Store


@pytest.mark.parametrize("dev", [False, True])
def test_synthetic_background_pipeline_and_calibration_after_freeze(
    toy_store, config, tmp_path, monkeypatch, dev
):
    monkeypatch.setattr("raregate.training.background.ProcessedStore", toy_store)
    config["training"].update(max_epochs=3, batch_size=64)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    original = toy_store.iter_features

    def audited(self, split, **kwargs):
        if split == "validation_calibration_background":
            assert (tmp_path / ".out.partial/model.json").exists()
        yield from original(self, split, **kwargs)

    monkeypatch.setattr(toy_store, "iter_features", audited)
    result = run_background(tmp_path, path, tmp_path / "out", dev=dev, plots=False)
    assert [c[0] for c in toy_store.calls] == list(toy_store.populations)[:3]
    assert all(not c[1] and not c[2] for c in toy_store.calls)
    science = result["scientific"]
    assert science["test_model_access"] is False
    assert science["training"]["training_count"] == (10 if dev else 200)
    assert science["provenance"]["scope"] == (
        "dev_diagnostic" if dev else "canonical_full"
    )
    assert all(
        p["calibration"]["efficiency"] <= p["target_fpr"] for p in science["thresholds"]
    )


def test_future_ae_gate_only_on_synthetic_data(
    toy_store, config, tmp_path, monkeypatch
):
    monkeypatch.setattr("raregate.training.background.ProcessedStore", toy_store)
    config["training"].update(max_epochs=2, batch_size=64)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    run_background(tmp_path, path, tmp_path / "background", plots=False)

    class AuditedStore(toy_store):
        def iter_features(self, split, **kwargs):
            audit = json.loads((tmp_path / "final/test-unblinding.json").read_text())
            assert audit["population_access"][-1]["split"] == split
            yield from super().iter_features(split, **kwargs)

    monkeypatch.setattr("raregate.evaluation.run.ProcessedStore", AuditedStore)
    with pytest.raises(ValueError, match="embargo"):
        run_final(
            tmp_path / "background/model.json",
            tmp_path / "background/results.json",
            tmp_path,
            tmp_path / "refused",
        )
    result = run_final(
        tmp_path / "background/model.json",
        tmp_path / "background/results.json",
        tmp_path,
        tmp_path / "final",
        allow_test=True,
    )
    assert result["metrics"]["background_total"] == 20
    assert result["metrics"]["signal_total"] == 20


def test_dev_model_cannot_enter_final_gate(toy_store, config, tmp_path, monkeypatch):
    monkeypatch.setattr("raregate.training.background.ProcessedStore", toy_store)
    monkeypatch.setattr("raregate.evaluation.run.ProcessedStore", toy_store)
    config["training"]["max_epochs"] = 1
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    run_background(tmp_path, path, tmp_path / "dev", dev=True, plots=False)
    calls = list(toy_store.calls)
    with pytest.raises(ValueError, match="canonical"):
        run_final(
            tmp_path / "dev/model.json",
            tmp_path / "dev/results.json",
            tmp_path,
            tmp_path / "final",
            allow_test=True,
        )
    assert toy_store.calls == calls
    assert not (tmp_path / "final").exists()


def test_training_preserves_caller_rng_and_thread_settings(features, config):
    import random

    config["training"]["max_epochs"] = 1
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    torch_state = torch.get_rng_state().clone()
    threads = torch.get_num_threads()
    deterministic = torch.are_deterministic_algorithms_enabled()
    train_autoencoder(features[:240], features[240:], config)
    assert random.getstate() == python_state
    after = np.random.get_state()
    assert after[0] == numpy_state[0] and after[2:] == numpy_state[2:]
    np.testing.assert_array_equal(after[1], numpy_state[1])
    assert torch.equal(torch_state, torch.get_rng_state())
    assert torch.get_num_threads() == threads
    assert torch.are_deterministic_algorithms_enabled() == deterministic
