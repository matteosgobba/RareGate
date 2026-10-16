"""Transparent PCA reconstruction baseline fitted by scikit-learn full SVD."""

import json
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA

from raregate.data.inspection import AGGREGATE_NAMES
from raregate.data.processed import content_hash

SCORE_DEFINITION = "sum_squared_reconstruction_residual"
PROTOCOL = "latenttrigger-evaluation-v1"
BACKGROUND_ROLES = (
    "train_background",
    "validation_selection_background",
    "validation_calibration_background",
)


def validate_config(config: dict) -> None:
    """Fail rather than silently reinterpret the preregistered modeling policy."""
    try:
        pca, inputs = config["pca"], config["input"]
        if (
            config["schema_version"] != 1
            or config["model_type"] != "pca_reconstruction"
            or config["evaluation_protocol"] != PROTOCOL
            or inputs["processed_schema_version"] != 1
            or inputs["representation"] != "event_features"
            or tuple(inputs["features"]) != AGGREGATE_NAMES
            or inputs["dtype"] != "float32"
            or pca["svd_solver"] != "full"
            or pca["fit_dtype"] != "float64"
            or pca["whiten"] is not False
            or pca["random_state"] is not None
            or pca["component_rule"] != "smallest_k_cumulative_variance_at_least_target"
            or not 0 < pca["explained_variance_target"] < 1
            or pca["reject_full_rank"] is not True
            or config["score"]
            != {
                "definition": SCORE_DEFINITION,
                "orientation": "higher_is_more_anomalous",
                "dtype": "float64",
            }
            or tuple(
                config["roles"][role] for role in ("fit", "selection", "calibration")
            )
            != BACKGROUND_ROLES
            or config["thresholds"]["quantile_method"] != "higher"
            or config["thresholds"]["decision"] != "score > threshold"
            or config["future_metrics"]["roc_policy"]
            != "attainable_empirical_points_no_interpolation"
            or config["diagnostics"]
            != {
                "summary_quantile_method": "linear",
                "stability": "two_sample_ks_distance_without_p_values",
            }
            or not 1 <= config["batch_events"] <= 4096
        ):
            raise ValueError("Model config violates evaluation/feature protocol v1.")
        for key in ("preprocessing_config_sha256",):
            if len(inputs[key]) != 64:
                raise ValueError("Missing preprocessing identity.")
        fprs = config["thresholds"]["target_fprs"]
        if not fprs or len(set(fprs)) != len(fprs) or any(not 0 < x < 1 for x in fprs):
            raise ValueError("Invalid calibration target FPRs.")
    except (KeyError, TypeError) as exc:
        raise ValueError("Incomplete model config.") from exc


def validate_input_store(manifest: dict, config: dict) -> None:
    validate_config(config)
    science = manifest["scientific"]
    if (
        manifest["schema_version"] != config["input"]["processed_schema_version"]
        or science["aggregate_channels"] != config["input"]["features"]
        or science["config_sha256"] != config["input"]["preprocessing_config_sha256"]
        or science["scope"] != "full"
    ):
        raise ValueError(
            "Processed schema/features/config/full-scope identity mismatch."
        )


def _features(values: np.ndarray, feature_names) -> np.ndarray:
    if tuple(feature_names) != AGGREGATE_NAMES:
        raise ValueError("Feature names/order mismatch.")
    values = np.asarray(values)
    if (
        values.ndim != 2
        or values.shape[1] != 8
        or values.dtype.kind not in "iuf"
        or not np.isfinite(values).all()
    ):
        raise ValueError("Expected finite numeric [events,8] features.")
    return values.astype(np.float64)


@dataclass
class PCAReconstruction:
    """All eight fitted axes retained for transparency; only first k reconstruct."""

    mean: np.ndarray
    components: np.ndarray
    explained_variance: np.ndarray
    explained_variance_ratio: np.ndarray
    k: int
    target: float
    training_count: int

    @classmethod
    def fit(
        cls, values: np.ndarray, *, feature_names, target: float = 0.95
    ) -> "PCAReconstruction":
        values = _features(values, feature_names)
        if len(values) < 9 or not np.isfinite(target) or not 0 < target < 1:
            raise ValueError(
                "Need at least nine events and a variance target in (0,1)."
            )
        if not (values.var(axis=0) > 0).all():
            raise ValueError("PCA input has constant features.")
        fitted = PCA(n_components=8, svd_solver="full", whiten=False).fit(values)
        ratios = fitted.explained_variance_ratio_
        k = int(np.searchsorted(np.cumsum(ratios), target, side="left") + 1)
        if k >= 8:
            raise ValueError(
                "Variance target keeps all eight dimensions; review the preregistered rule before proceeding."
            )
        return cls(
            fitted.mean_,
            # Match JSON reload layout so BLAS rounding survives the roundtrip.
            np.ascontiguousarray(fitted.components_),
            fitted.explained_variance_,
            ratios,
            k,
            target,
            len(values),
        )

    def reconstruct(self, values: np.ndarray, *, feature_names) -> np.ndarray:
        values = _features(values, feature_names)
        basis = self.components[: self.k]
        return (values - self.mean) @ basis.T @ basis + self.mean

    def score(self, values: np.ndarray, *, feature_names) -> np.ndarray:
        values = _features(values, feature_names)
        residual = values - self.reconstruct(values, feature_names=feature_names)
        return np.sum(residual * residual, axis=1)

    def artifact(self, *, provenance: dict, build: dict) -> dict:
        science = {
            "model_type": "pca_reconstruction",
            "features": list(AGGREGATE_NAMES),
            "score_definition": SCORE_DEFINITION,
            "orientation": "higher_is_more_anomalous",
            "fit_library": "scikit-learn",
            "fit_library_version": version("scikit-learn"),
            "fit_dtype": "float64",
            "solver": "full",
            "whiten": False,
            "mean": self.mean.tolist(),
            "components": self.components.tolist(),
            "explained_variance": self.explained_variance.tolist(),
            "explained_variance_ratio": self.explained_variance_ratio.tolist(),
            "selected_k": self.k,
            "variance_target": self.target,
            "training_count": self.training_count,
            "provenance": provenance,
        }
        return {
            "artifact_version": 1,
            "scientific": science,
            "scientific_sha256": content_hash(science),
            "build": build,
        }

    @classmethod
    def from_artifact(cls, artifact: dict) -> "PCAReconstruction":
        try:
            spec = artifact["scientific"]
            if (
                artifact["artifact_version"] != 1
                or artifact["scientific_sha256"] != content_hash(spec)
                or spec["model_type"] != "pca_reconstruction"
                or tuple(spec["features"]) != AGGREGATE_NAMES
                or spec["score_definition"] != SCORE_DEFINITION
                or spec["orientation"] != "higher_is_more_anomalous"
                or spec["fit_dtype"] != "float64"
                or spec["solver"] != "full"
                or spec["whiten"] is not False
            ):
                raise ValueError("Model artifact identity/schema mismatch.")
            arrays = [
                np.asarray(spec[name], dtype=np.float64)
                for name in (
                    "mean",
                    "components",
                    "explained_variance",
                    "explained_variance_ratio",
                )
            ]
            mean, components, variance, ratios = arrays
            if (
                mean.shape != (8,)
                or components.shape != (8, 8)
                or variance.shape != (8,)
                or ratios.shape != (8,)
                or not all(np.isfinite(a).all() for a in arrays)
                or (variance < 0).any()
                or (ratios < 0).any()
                or not np.isclose(ratios.sum(), 1)
                or not np.allclose(components @ components.T, np.eye(8), atol=1e-10)
                or not 0 < spec["variance_target"] < 1
                or not 1 <= spec["selected_k"] < 8
                or spec["training_count"] < 9
                or spec["selected_k"]
                != int(
                    np.searchsorted(
                        np.cumsum(ratios), spec["variance_target"], side="left"
                    )
                    + 1
                )
            ):
                raise ValueError("Invalid fitted PCA parameters.")
            return cls(
                *arrays,
                spec["selected_k"],
                spec["variance_target"],
                spec["training_count"],
            )
        except (KeyError, TypeError) as exc:
            raise ValueError("Incomplete model artifact.") from exc

    @classmethod
    def load(cls, path: Path) -> "PCAReconstruction":
        return cls.from_artifact(json.loads(path.read_text()))


def main() -> None:
    from raregate.models.background import main as run_background

    run_background()


if __name__ == "__main__":
    main()
