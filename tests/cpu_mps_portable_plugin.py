"""Portable legacy schema fixtures in memory; no frozen model artifact files.

Explicitly enabled only by the Task0023 portable runner. Three old schema tests
expect a v1 document at a repository path; replace it with a synthetic155-parameter
document/history, without changing those historical tests or operational bytes.
"""

import json
from pathlib import Path

import pytest
import torch

from latenttrigger.data.processed import content_hash
from latenttrigger.models.autoencoder import CompactAutoencoder

NAMES = {
    "test_controlled_config_only_epoch_ceiling_and_historical_identity",
    "test_v1_readable_and_artifact_schema_version_rejected",
    "test_convergence_reference_rejects_changed_processed_identity",
}


def synthetic_document(config):
    model = CompactAutoencoder().eval()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.fill_(0.03125)
    history = [
        dict(epoch=n, training_mse=1 / n, selection_mse=1 / n) for n in range(1, 4)
    ]
    context = dict(
        model_config=config,
        processed_scientific_sha256="portable_synthetic",
        processed_schema_version=1,
        source={},
        source_integrity={},
        preprocessing_config_sha256=config["input"]["preprocessing_config_sha256"],
        split_identity_sha256="synthetic",
        scope="full",
    )
    artifact = model.artifact(
        provenance=context,
        training=dict(
            best_epoch=3,
            epochs_executed=3,
            history_sha256=content_hash(dict(history=history)),
        ),
    )
    return artifact, history


@pytest.fixture(autouse=True)
def portable_legacy_schema(request, monkeypatch):
    if request.node.name not in NAMES:
        return
    root = Path(request.node.fspath).parents[1]
    config = json.loads((root / "configs/models/compact_autoencoder.json").read_text())
    document, history = synthetic_document(config)
    target = root / "artifacts/models/compact-autoencoder-v1/model.json"
    if target.exists():
        raise AssertionError("Portable validation must not contain frozen artifacts.")
    original = Path.read_text

    def read_text(path, *args, **kwargs):
        return (
            json.dumps(document) if path == target else original(path, *args, **kwargs)
        )

    monkeypatch.setattr(Path, "read_text", read_text)
    from latenttrigger.training import convergence

    monkeypatch.setattr(convergence, "read_history", lambda path: history)
