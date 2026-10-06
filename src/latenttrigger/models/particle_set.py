"""Frozen design-v1 CPU particle reconstruction and strict transparent artifacts."""

import json
from pathlib import Path

import numpy as np
import torch
from torch import nn

from latenttrigger.data.processed import content_hash

ROOT = Path(__file__).resolve().parents[3]
DESIGN_PATH = ROOT / "configs/models/particle_set_baseline_design_v1.json"
DESIGN_HASH = "3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67"
MODEL_TYPE = "compact_particle_set_autoencoder"
LAYERS = (("e1", 4, 16), ("e2", 16, 8), ("local", 8, 2), ("d1", 10, 16), ("d2", 16, 4))


def design() -> dict:
    spec = json.loads(DESIGN_PATH.read_text())
    if content_hash(spec) != DESIGN_HASH:
        raise ValueError(
            "Design identity mismatch; do not silently change methodology."
        )
    return spec


def executable_config() -> dict:
    spec = design()
    config = {
        "schema_version": 1,
        "runtime_config_version": 1,
        "status": "executable",
        "model_type": MODEL_TYPE,
        "design_id": spec["design_id"],
        "design_version": spec["design_version"],
        "design_scientific_sha256": DESIGN_HASH,
        "evaluation_protocol": spec["evaluation_protocol"],
    }
    for key in (
        "input",
        "architecture",
        "objective",
        "score",
        "roles",
        "resource_gate",
        "calibration_preregistration",
        "numerical_acceptance",
    ):
        config[key] = spec[key]
    config["training"] = spec["training_preregistration"]
    return config


def validate_config(config: dict) -> None:
    if content_hash(config) != content_hash(executable_config()):
        raise ValueError("Executable config violates design v1 or is design_only.")


def validate_store(manifest: dict, config: dict, *, dev: bool = False) -> None:
    validate_config(config)
    spec, science = config["input"], manifest["scientific"]
    scope = "dev" if dev else "full"
    if (
        manifest["schema_version"] != spec["processed_schema_version"]
        or manifest.get("complete") is not True
        or content_hash(science) != manifest["scientific_sha256"]
        or manifest["scientific_sha256"] != spec[f"processed_{scope}_scientific_sha256"]
        or science["scope"] != scope
        or science["config_sha256"] != spec["preprocessing_config_sha256"]
        or science["split_identity_sha256"] != spec["split_identity_sha256"]
        or science["source_integrity"]["sha256"] != spec["source_sha256"]
        or science["model_channels"] != spec["channels"]
        or science["default_nmax"] != 384
    ):
        raise ValueError("Particle source/schema/preprocessing/split/scope mismatch.")


def finite(value: torch.Tensor, name: str) -> None:
    if not torch.isfinite(value).all():
        raise ValueError(f"Nonfinite {name}.")


def validate_batch(x: torch.Tensor, mask: torch.Tensor, *, prefix: bool = True) -> None:
    if (
        not isinstance(x, torch.Tensor)
        or not isinstance(mask, torch.Tensor)
        or x.ndim != 3
        or x.shape[1:] != (384, 4)
        or x.shape[0] < 1
        or x.dtype != torch.float32
        or mask.dtype != torch.bool
        or mask.shape != x.shape[:2]
        or x.device.type != "cpu"
        or mask.device.type != "cpu"
    ):
        raise ValueError("Expected nonempty CPU FP32 [B,384,4] and boolean [B,384].")
    finite(x, "input including padding")
    counts = mask.sum(dim=1)
    if (counts == 0).any():
        raise ValueError("Empty/all-padding event.")
    if prefix and not torch.equal(mask, torch.arange(384)[None, :] < counts[:, None]):
        raise ValueError("Public mask must be a valid prefix.")
    pair = x[:, :, 2:].to(torch.float64)
    if ((pair.square().sum(dim=2) - 1).abs()[mask] > 2e-6).any():
        raise ValueError("Invalid input angular pair.")


def _event_loss(x: torch.Tensor, y: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    if y.shape != x.shape or y.dtype != torch.float32 or y.device.type != "cpu":
        raise ValueError("Expected CPU FP32 reconstruction with input shape.")
    finite(y, "reconstruction")
    # Where excludes the target path too; finite large padding cannot affect gradients.
    residual = torch.where(mask[:, :, None], x.double() - y.double(), 0.0)
    weights = residual.new_tensor([1.0, 1.0, 0.5, 0.5])
    per_particle = (residual.square() * weights).sum(dim=2) / 3.0
    result = per_particle.sum(dim=1) / mask.sum(dim=1).double()
    finite(result, "event loss")
    return result


def event_loss(x: torch.Tensor, y: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Differentiable FP64 corresponding-particle loss; equal event weighting."""
    validate_batch(x, mask)
    return _event_loss(x, y, mask)


class ParticleSetAutoencoder(nn.Module):
    """Shared local2/mean8 distributed code; CPU reference only."""

    def __init__(self):
        super().__init__()
        for name, inputs, outputs in LAYERS:
            setattr(
                self, name, nn.Linear(inputs, outputs, bias=True, dtype=torch.float32)
            )
        self.relu = nn.ReLU(inplace=False)

    @property
    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def validate_parameters(self) -> None:
        for name, p in self.named_parameters():
            if p.device.type != "cpu" or p.dtype != torch.float32:
                raise ValueError("Particle model requires CPU FP32 parameters.")
            finite(p, f"parameter {name}")

    def _encoded(self, x, mask):
        self.validate_parameters()
        valid = mask[:, :, None]
        x0 = torch.where(valid, x, 0.0)
        a = self.relu(self.e1(x0))
        finite(a, "e1 activation")
        h = self.relu(self.e2(a))
        finite(h, "e2 activation")
        h = torch.where(valid, h, 0.0)
        local = self.local(h)
        finite(local, "local code")
        local = torch.where(valid, local, 0.0)
        context = (h.double().sum(dim=1) / mask.sum(dim=1)[:, None]).float()
        finite(context, "context")
        return local, context

    def encode(self, x, mask):
        validate_batch(x, mask)
        return self._encoded(x, mask)

    def _compute(self, x, mask):
        local, context = self._encoded(x, mask)
        c = torch.cat((local, context[:, None, :].expand(-1, 384, -1)), dim=2)
        v = self.relu(self.d1(c))
        finite(v, "decoder hidden")
        y = self.d2(v)
        finite(y, "decoder output")
        return torch.where(mask[:, :, None], y, 0.0), local, context

    def _forward_set(self, x, mask):
        """Internal non-prefix boundary for consistent set-permutation tests."""
        validate_batch(x, mask, prefix=False)
        return self._compute(x, mask)

    def forward(self, x, mask):
        validate_batch(x, mask)
        return self._compute(x, mask)[0]

    def reconstruct(self, x, mask):
        return self(x, mask)

    def score(self, x, mask) -> np.ndarray:
        if isinstance(x, np.ndarray) and isinstance(mask, np.ndarray):
            x = torch.from_numpy(np.ascontiguousarray(x))
            mask = torch.from_numpy(np.ascontiguousarray(mask))
        with torch.inference_mode():
            y = self(x, mask)
            scores = _event_loss(x, y, mask).numpy().copy()
        if scores.dtype != np.float64 or not np.isfinite(scores).all():
            raise ValueError("Invalid canonical particle score.")
        return scores

    def artifact(
        self, *, config: dict, provenance: dict, training: dict, finalized: bool = False
    ) -> dict:
        validate_config(config)
        self.validate_parameters()
        if finalized:
            validate_completion(training, provenance)
        params = [
            {
                "name": name,
                "shape": list(p.shape),
                "dtype": "float32",
                "values": p.detach().numpy().tolist(),
            }
            for name, p in self.state_dict().items()
        ]
        science = {
            "model_type": MODEL_TYPE,
            "runtime_artifact_version": 1,
            "design_scientific_sha256": DESIGN_HASH,
            "status": "frozen" if finalized else "diagnostic_candidate",
            "parameter_count": 478,
            "architecture": config["architecture"],
            "input": config["input"],
            "objective": config["objective"],
            "score": config["score"],
            "parameters": params,
            "config": config,
            "config_sha256": content_hash(config),
            "provenance": provenance,
            "training": training,
        }
        return {
            "artifact_version": 1,
            "scientific": science,
            "scientific_sha256": content_hash(science),
        }

    @classmethod
    def from_artifact(cls, artifact: dict, *, allow_candidate: bool = False):
        try:
            science = artifact["scientific"]
            config = science["config"]
            validate_config(config)
            if (
                type(artifact["artifact_version"]) is not int
                or artifact["artifact_version"] != 1
                or content_hash(science) != artifact["scientific_sha256"]
                or science["model_type"] != MODEL_TYPE
                or type(science["runtime_artifact_version"]) is not int
                or science["runtime_artifact_version"] != 1
                or science["design_scientific_sha256"] != DESIGN_HASH
                or science["parameter_count"] != 478
                or science["config_sha256"] != content_hash(config)
                or any(
                    science[key] != config[key]
                    for key in ("architecture", "input", "objective", "score")
                )
                or science["status"] not in ("frozen", "diagnostic_candidate")
                or (not allow_candidate and science["status"] != "frozen")
            ):
                raise ValueError("Particle artifact identity/schema/status mismatch.")
            if science["status"] == "frozen":
                validate_completion(science["training"], science["provenance"])
            with torch.random.fork_rng(devices=[]):
                model = cls()
            reference = model.state_dict()
            params = science["parameters"]
            if [p["name"] for p in params] != list(reference):
                raise ValueError("Particle parameter names/order mismatch.")
            state = {}
            for p in params:
                if np.asarray(p["values"]).dtype.kind not in "fiu":
                    raise ValueError("Nonnumeric particle parameter values.")
                values = np.asarray(p["values"], dtype=np.float64)
                exact = values.astype(np.float32)
                if (
                    p["dtype"] != "float32"
                    or p["shape"] != list(reference[p["name"]].shape)
                    or list(values.shape) != p["shape"]
                    or not np.isfinite(values).all()
                    or not np.array_equal(exact.astype(np.float64), values)
                ):
                    raise ValueError("Invalid exact FP32 particle parameter/shape.")
                state[p["name"]] = torch.from_numpy(exact.copy())
            model.load_state_dict(state, strict=True)
            return model.eval()
        except (KeyError, TypeError, OverflowError) as exc:
            raise ValueError("Incomplete particle artifact.") from exc

    @classmethod
    def load(cls, path: Path, *, allow_candidate: bool = False):
        return cls.from_artifact(
            json.loads(Path(path).read_text()), allow_candidate=allow_candidate
        )


def validate_completion(training: dict, provenance: dict) -> None:
    spec = executable_config()["input"]
    if (
        any(
            type(training.get(k)) is not int
            for k in (
                "training_count",
                "selection_count",
                "best_epoch",
                "epochs_executed",
                "bad_epochs_at_stop",
            )
        )
        or provenance.get("scope") != "canonical_full"
        or provenance.get("processed_scientific_sha256")
        != spec["processed_full_scientific_sha256"]
        or provenance.get("preprocessing_config_sha256")
        != spec["preprocessing_config_sha256"]
        or provenance.get("split_identity_sha256") != spec["split_identity_sha256"]
        or provenance.get("source_sha256") != spec["source_sha256"]
        or training.get("training_count") != 699957
        or training.get("selection_count") != 74749
        or training.get("stopping_reason") != "patience"
        or training.get("bad_epochs_at_stop") != 20
        or training.get("epochs_executed", 0) != training.get("best_epoch", 0) + 20
        or not 1
        <= training.get("best_epoch", 0)
        <= training.get("epochs_executed", 0)
        <= 200
        or not all(
            training.get(k) is True
            for k in (
                "synthetic_gate",
                "dev_gate",
                "resource_gate",
                "restored_verified",
                "reproduction_verified",
            )
        )
        or len(training.get("history_sha256", "")) != 64
        or len(training.get("selection_score_sha256", "")) != 64
    ):
        raise ValueError("Cannot freeze incomplete/dev/incompatible particle baseline.")
