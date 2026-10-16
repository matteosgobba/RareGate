"""Generated fixtures only; unchanged JSON loaders, no fitting or setup forwards."""

import numpy as np
import torch

from raregate.benchmarks import core
from raregate.benchmarks import development_decision_protocol as p


def models(directory):
    ratios = np.array([0.3, 0.2, 0.15, 0.1, 0.1, 0.08, 0.04, 0.03], dtype="<f8")
    pca = core.PCAReconstruction(
        np.zeros(8), np.eye(8), ratios.copy(), ratios.copy(), 6, 0.9, 100
    )
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(4101)
        ae = core.CompactAutoencoder().eval()
    objects = {"pca-v1": pca, "compact-autoencoder-v2": ae}
    entries = []
    for entry in p.load()["models"]:
        name = entry["name"]
        model = objects[name]
        artifact = (
            model.artifact(provenance={"synthetic_fixture": True}, build={})
            if name == "pca-v1"
            else model.artifact(
                provenance={"synthetic_fixture": True},
                training={"synthetic_fixture": True},
            )
        )
        filename = name + "-fixture-model.json"
        resultname = name + "-fixture-results.json"
        p.durable_json(directory / filename, artifact, exclusive=True)
        # Fixed toy thresholds are fixture constants; no calibration or scientific reuse.
        result = {
            "scientific": {
                "thresholds": [
                    {"target_fpr": alpha, "threshold": value}
                    for alpha, value in zip(
                        [0.1, 0.05, 0.01, 0.001], [0.5, 1.0, 2.0, 4.0], strict=True
                    )
                ]
            }
        }
        p.durable_json(directory / resultname, result, exclusive=True)
        entries.append(dict(entry, model_path=filename, results_path=resultname))
    return entries
