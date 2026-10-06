"""Controlled extension/versioning tests use tiny synthetic histories/features."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from latenttrigger.data.processed import FeatureBatch, content_hash
from latenttrigger.models.autoencoder import CompactAutoencoder, validate_config
from latenttrigger.training.autoencoder import EarlyStopping, train_autoencoder
from latenttrigger.training.background import run_background
from latenttrigger.training.convergence import (
    HistoricalPrefix,
    canonical_decision,
    validate_extension_config,
)

ROOT = Path(__file__).parents[1]


def test_controlled_config_only_epoch_ceiling_and_historical_identity():
    first = json.loads((ROOT / "configs/models/compact_autoencoder.json").read_text())
    second = json.loads(
        (ROOT / "configs/models/compact_autoencoder_v2.json").read_text()
    )
    historical = json.loads(
        (ROOT / "artifacts/models/compact-autoencoder-v1/model.json").read_text()
    )
    assert first == historical["scientific"]["provenance"]["model_config"]
    assert first["training"]["max_epochs"] == 200
    validate_extension_config(first, second)
    second["training"]["learning_rate"] *= 2
    with pytest.raises(ValueError, match="Only"):
        validate_extension_config(first, second)


@pytest.mark.parametrize("value", [0, 1000.0, "1000", True])
def test_max_epochs_requires_positive_integer(value):
    cfg = json.loads((ROOT / "configs/models/compact_autoencoder_v2.json").read_text())
    cfg["training"]["max_epochs"] = value
    with pytest.raises(ValueError, match="max_epochs"):
        validate_config(cfg)


@pytest.fixture
def reference():
    model = CompactAutoencoder()
    history = [
        {"epoch": n, "training_mse": 1 / n, "selection_mse": 1 / n} for n in range(1, 4)
    ]
    artifact = model.artifact(
        provenance={},
        training={
            "best_epoch": 3,
            "epochs_executed": 3,
            "history_sha256": content_hash({"history": history}),
        },
    )
    return model, history, artifact


def test_prefix_checks_each_epoch_best_progression_and_exact_weights(reference):
    model, history, artifact = reference
    audit = HistoricalPrefix(history, artifact)
    stopper = EarlyStopping(15, 0)
    for n, row in enumerate(history, 1):
        stopper.update(n, row["selection_mse"], model)
        audit(model, history[:n], stopper)
    report = audit.report()
    assert report["epochs_verified"] == 3
    assert report["endpoint_parameter_bytes_equal"] is True
    audit(model, history + [history[-1]], stopper)  # Later epochs cannot alter prefix.


@pytest.mark.parametrize("kind", ["loss", "progression", "parameters", "incomplete"])
def test_prefix_mismatch_blocks_extension(reference, kind):
    model, history, artifact = reference
    audit = HistoricalPrefix(history, artifact)
    stopper = EarlyStopping(15, 0)
    for n, row in enumerate(history[:2], 1):
        stopper.update(n, row["selection_mse"], model)
        audit(model, history[:n], stopper)
    if kind == "incomplete":
        with pytest.raises(ValueError, match="before"):
            audit.report()
        return
    stopper.update(3, history[-1]["selection_mse"], model)
    if kind == "loss":
        history = copy.deepcopy(history)
        history[-1]["training_mse"] += 0.01
    elif kind == "progression":
        stopper.best_epoch = 1
    else:
        with torch.no_grad():
            next(model.parameters()).add_(0.01)
    with pytest.raises(ValueError, match="mismatch"):
        audit(model, history, stopper)


@pytest.mark.parametrize(
    "failure", [None, "prefix", "protocol", "epochs", "improvement"]
)
def test_canonical_supersession_four_conditions(failure):
    training = {
        "epochs_executed": 300,
        "best_selection_mse": 0.2,
        "stopping_reason": "patience",
    }
    if failure == "epochs":
        training["epochs_executed"] = 200
    if failure == "improvement":
        training["best_selection_mse"] = 0.22
    decision = canonical_decision(
        training,
        {"best_selection_mse": 0.22},
        prefix_verified=failure != "prefix",
        protocol_intact=failure != "protocol",
    )
    assert decision["canonical_model"] == (
        "compact-autoencoder-v2" if failure is None else "compact-autoencoder-v1"
    )
    assert decision["convergence_status"] == "closed_under_frozen_patience_rule"
    training["stopping_reason"] = "max_epochs"
    assert (
        canonical_decision(
            training,
            {"best_selection_mse": 0.22},
            prefix_verified=True,
            protocol_intact=True,
        )["convergence_status"]
        == "unresolved_epoch_cap"
    )


def test_v1_readable_and_artifact_schema_version_rejected():
    artifact = json.loads(
        (ROOT / "artifacts/models/compact-autoencoder-v1/model.json").read_text()
    )
    model = CompactAutoencoder.from_artifact(artifact)
    assert model.parameter_count == 155
    artifact["artifact_version"] = 2
    with pytest.raises(ValueError, match="schema"):
        CompactAutoencoder.from_artifact(artifact)


def test_epoch_observer_preserves_training_and_output(reference):
    config = json.loads((ROOT / "configs/models/compact_autoencoder.json").read_text())
    config["training"].update(max_epochs=3, batch_size=32)
    features = np.random.default_rng(1).normal(size=(120, 8)).astype(np.float32)
    first, history, info = train_autoencoder(features[:80], features[80:], config)
    seen = []

    def observer(model, rows, stopping):
        seen.append((len(rows), stopping.best_epoch))

    second, repeated, info2 = train_autoencoder(
        features[:80], features[80:], config, on_epoch=observer
    )
    assert history == repeated and info == info2
    assert len(seen) == 3
    assert all(
        torch.equal(v, second.state_dict()[k]) for k, v in first.state_dict().items()
    )


def test_convergence_provenance_and_no_score_persistence(tmp_path, monkeypatch):
    config = json.loads((ROOT / "configs/models/compact_autoencoder.json").read_text())
    config["training"].update(max_epochs=3, batch_size=32)
    features = np.random.default_rng(1).normal(size=(120, 8)).astype(np.float32)
    model, history, training = train_autoencoder(
        features[:80], features[80:100], config
    )
    context = {"model_config": config}
    artifact = model.artifact(provenance=context, training=training)
    prefix = HistoricalPrefix(history, artifact)
    # Toy three-epoch audit exercises the same reader/freeze boundary without
    # pretending it is the real 200→1000 scientific extension.
    monkeypatch.setattr(prefix, "validate_provenance", lambda context: None)

    class Store:
        calls = []
        manifest = {
            "schema_version": 1,
            "scientific_sha256": "synthetic",
            "scientific": {
                "aggregate_channels": config["input"]["features"],
                "config_sha256": config["input"]["preprocessing_config_sha256"],
                "scope": "full",
                "source": {},
                "source_integrity": {},
                "split_identity_sha256": "toy",
                "counts": {
                    "train_background": 80,
                    "validation_selection_background": 20,
                    "validation_calibration_background": 20,
                },
            },
        }

        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def iter_features(self, split, *, batch_size):
            self.calls.append(split)
            if split == "validation_calibration_background":
                assert (tmp_path / ".run.partial/model.json").exists()
                assert prefix.complete
            mapping = {
                "train_background": features[:80],
                "validation_selection_background": features[80:100],
                "validation_calibration_background": features[100:],
            }
            assert split in mapping
            values = mapping[split]
            yield FeatureBatch(values, np.arange(len(values)), None)

    monkeypatch.setattr("latenttrigger.training.background.ProcessedStore", Store)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    result = run_background(
        tmp_path,
        path,
        tmp_path / "run",
        plots=False,
        save_scores=False,
        convergence_reference=prefix,
    )
    assert not list((tmp_path / "run").glob("*.npy"))
    assert len(result["scientific"]["score_array_sha256"]) == 3
    assert result["scientific"]["convergence_checks"]["verified"] is True
    assert (
        result["scientific"]["convergence_checks"][
            "independently_restored_selection_mse"
        ]
        == training["best_selection_mse"]
    )
    loaded = CompactAutoencoder.load(tmp_path / "run/model.json")
    assert all(
        torch.equal(v, loaded.state_dict()[k]) for k, v in model.state_dict().items()
    )


def test_convergence_reference_rejects_changed_processed_identity():
    from latenttrigger.training.convergence import read_history

    artifact = json.loads(
        (ROOT / "artifacts/models/compact-autoencoder-v1/model.json").read_text()
    )
    history = read_history(
        ROOT / "results/tables/final/task0007-autoencoder-training-history.csv"
    )
    reference = HistoricalPrefix(history, artifact)
    context = copy.deepcopy(artifact["scientific"]["provenance"])
    context["model_config"] = json.loads(
        (ROOT / "configs/models/compact_autoencoder_v2.json").read_text()
    )
    context["model_config_sha256"] = content_hash(context["model_config"])
    reference.validate_provenance(context)
    context["processed_scientific_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="processed_scientific_sha256"):
        reference.validate_provenance(context)
