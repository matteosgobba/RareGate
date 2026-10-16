"""Compact FP32 reconstruction network and transparent frozen artifacts."""

import json
from pathlib import Path

import numpy as np
import torch
from torch import nn

from raregate.data.inspection import AGGREGATE_NAMES
from raregate.data.processed import content_hash
from raregate.models.pca import BACKGROUND_ROLES, PROTOCOL, SCORE_DEFINITION

ARCHITECTURE = {
    "input_dim": 8,
    "encoder_hidden": 6,
    "latent_dim": 3,
    "decoder_hidden": 6,
    "activation": "relu",
}


def validate_config(config: dict) -> None:
    """Reject architecture, population or protocol drift before opening data."""
    try:
        inputs, training = config["input"], config["training"]
        if (
            config["schema_version"] != 1
            or config["model_type"] != "compact_autoencoder"
            or config["model"] != ARCHITECTURE
            or config["evaluation_protocol"] != PROTOCOL
            or inputs["processed_schema_version"] != 1
            or inputs["representation"] != "event_features"
            or inputs["features"] != list(AGGREGATE_NAMES)
            or inputs["dtype"] != "float32"
            or len(inputs["preprocessing_config_sha256"]) != 64
            or tuple(config["roles"][r] for r in ("fit", "selection", "calibration"))
            != BACKGROUND_ROLES
            or config["score"]
            != {
                "definition": SCORE_DEFINITION,
                "orientation": "higher_is_more_anomalous",
                "dtype": "float64",
            }
            or config["thresholds"]
            != {
                "target_fprs": [0.1, 0.05, 0.01, 0.001],
                "quantile_method": "higher",
                "decision": "score > threshold",
            }
            or config["diagnostics"]
            != {
                "summary_quantile_method": "linear",
                "stability": "two_sample_ks_distance_without_p_values",
            }
            or config["future_metrics"]
            != {
                "fixed_fprs": [0.1, 0.05, 0.01, 0.001],
                "fixed_tprs": [0.5, 0.8, 0.9],
                "roc_policy": "attainable_empirical_points_no_interpolation",
            }
            or training["device"] != "cpu"
            or training["optimizer"] != "adam"
            or training["loss"] != "mean_squared_reconstruction_error"
            or training["initialization"] != "pytorch_linear_default"
            or training["num_workers"] != 0
            or training["deterministic_algorithms"] is not True
            or not np.isfinite(training["learning_rate"])
            or training["learning_rate"] <= 0
            or not np.isfinite(training["min_delta"])
            or training["min_delta"] < 0
        ):
            raise ValueError(
                "Autoencoder config violates frozen architecture/protocol."
            )
        for key in (
            "batch_size",
            "max_epochs",
            "early_stopping_patience",
            "num_threads",
        ):
            if type(training[key]) is not int or training[key] < 1:
                raise ValueError(f"Invalid training {key}.")
        if type(training["seed"]) is not int or not 0 <= training["seed"] < 2**32:
            raise ValueError("Invalid seed.")
        if (
            type(config["batch_events"]) is not int
            or not 1 <= config["batch_events"] <= 4096
        ):
            raise ValueError("Invalid scoring batch size.")
    except (KeyError, TypeError) as exc:
        raise ValueError("Incomplete autoencoder config.") from exc


def validate_input_store(manifest: dict, config: dict, *, dev: bool = False) -> None:
    validate_config(config)
    science = manifest["scientific"]
    if (
        manifest["schema_version"] != config["input"]["processed_schema_version"]
        or science["aggregate_channels"] != config["input"]["features"]
        or science["config_sha256"] != config["input"]["preprocessing_config_sha256"]
        or science["scope"] not in (("full", "dev") if dev else ("full",))
    ):
        raise ValueError("Processed schema/features/config/scope identity mismatch.")


def feature_array(values: np.ndarray) -> np.ndarray:
    """Validate the existing FP32 feature view without refitting or casting."""
    values = np.asarray(values)
    if (
        values.ndim != 2
        or values.shape[1] != 8
        or len(values) == 0
        or values.dtype != np.float32
        or not np.isfinite(values).all()
    ):
        raise ValueError("Expected finite nonempty FP32 [events,8] features.")
    return np.ascontiguousarray(values)


class CompactAutoencoder(nn.Module):
    """8→6→3→6→8; ReLU hidden layers, linear latent and output layers."""

    def __init__(self, input_dim: int = 8):
        super().__init__()
        if input_dim != 8:
            raise ValueError("Frozen autoencoder input dimension must be 8.")
        # The frozen contract is CPU FP32 even when a caller changed Torch's
        # ambient defaults. Explicit factories preserve the historical FP32 RNG
        # stream and avoid constructing an unusable FP64 model for FP32 inputs.
        factory = dict(device="cpu", dtype=torch.float32)
        self.encoder = nn.Sequential(
            nn.Linear(8, 6, **factory), nn.ReLU(), nn.Linear(6, 3, **factory)
        )
        self.decoder = nn.Sequential(
            nn.Linear(3, 6, **factory), nn.ReLU(), nn.Linear(6, 8, **factory)
        )

    def encode(self, values: torch.Tensor) -> torch.Tensor:
        if values.ndim != 2 or values.shape[1] != 8 or values.dtype != torch.float32:
            raise ValueError("Expected FP32 [events,8] network input.")
        return self.encoder(values)

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encode(values))

    @property
    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def score(self, values: np.ndarray, *, feature_names) -> np.ndarray:
        """FP32 forward; float64 SSE accumulation on CPU, higher is anomalous."""
        if tuple(feature_names) != AGGREGATE_NAMES:
            raise ValueError("Feature names/order mismatch.")
        values = feature_array(values)
        device = next(self.parameters()).device
        with torch.inference_mode():
            reconstructed = self(torch.from_numpy(values).to(device)).cpu().numpy()
        if not np.isfinite(reconstructed).all():
            raise ValueError("Nonfinite reconstruction.")
        residual = values.astype(np.float64) - reconstructed.astype(np.float64)
        return np.sum(residual * residual, axis=1)

    def artifact(self, *, provenance: dict, training: dict) -> dict:
        """Exact FP32 decimal round trip; no pickle, timestamp or absolute path."""
        parameters = []
        for name, parameter in self.state_dict().items():
            values = parameter.detach().cpu().numpy()
            if values.dtype != np.float32 or not np.isfinite(values).all():
                raise ValueError("Artifact requires finite FP32 parameters.")
            parameters.append(
                {
                    "name": name,
                    "shape": list(values.shape),
                    "dtype": "float32",
                    "values": values.tolist(),
                }
            )
        science = {
            "model_type": "compact_autoencoder",
            "architecture": ARCHITECTURE,
            "features": list(AGGREGATE_NAMES),
            "parameter_count": self.parameter_count,
            "score_definition": SCORE_DEFINITION,
            "orientation": "higher_is_more_anomalous",
            "forward_dtype": "float32",
            "score_dtype": "float64",
            "parameters": parameters,
            "provenance": provenance,
            "training": training,
        }
        return {
            "artifact_version": 1,
            "scientific": science,
            "scientific_sha256": content_hash(science),
        }

    @classmethod
    def from_artifact(cls, artifact: dict) -> "CompactAutoencoder":
        try:
            spec = artifact["scientific"]
            if (
                artifact["artifact_version"] != 1
                or artifact["scientific_sha256"] != content_hash(spec)
                or spec["model_type"] != "compact_autoencoder"
                or spec["architecture"] != ARCHITECTURE
                or spec["features"] != list(AGGREGATE_NAMES)
                or spec["parameter_count"] != 155
                or spec["score_definition"] != SCORE_DEFINITION
                or spec["orientation"] != "higher_is_more_anomalous"
                or spec["forward_dtype"] != "float32"
                or spec["score_dtype"] != "float64"
            ):
                raise ValueError("Model artifact identity/schema mismatch.")
            # Loading does not consume the caller's CPU random sequence.
            with torch.random.fork_rng(devices=[]):
                model = cls()
            reference = model.state_dict()
            if [p["name"] for p in spec["parameters"]] != list(reference):
                raise ValueError("Parameter names/order mismatch.")
            state = {}
            for p in spec["parameters"]:
                values = np.asarray(p["values"], dtype=np.float64)
                exact = values.astype(np.float32)
                if (
                    p["dtype"] != "float32"
                    or p["shape"] != list(reference[p["name"]].shape)
                    or list(values.shape) != p["shape"]
                    or not np.isfinite(values).all()
                    or not np.array_equal(exact.astype(np.float64), values)
                ):
                    raise ValueError("Invalid exact FP32 parameter values/shape.")
                state[p["name"]] = torch.from_numpy(exact.copy())
            model.load_state_dict(state, strict=True)
            return model.eval()
        except (KeyError, TypeError) as exc:
            raise ValueError("Incomplete autoencoder artifact.") from exc

    @classmethod
    def load(cls, path: Path) -> "CompactAutoencoder":
        return cls.from_artifact(json.loads(path.read_text()))


def main() -> None:
    from raregate.training.background import main as train_background

    train_background()


if __name__ == "__main__":
    main()
