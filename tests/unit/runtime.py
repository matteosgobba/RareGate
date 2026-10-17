"""Small generated model documents for schema compatibility checks."""

import torch

from raregate.data.processed import content_hash
from raregate.models.autoencoder import CompactAutoencoder


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
