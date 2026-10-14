"""PCA fit/artifact, background guards and future unblinding on toy features."""

import json
from pathlib import Path

import numpy as np
import pytest

from latenttrigger.data.inspection import AGGREGATE_NAMES
from latenttrigger.data.processed import FeatureBatch
from latenttrigger.evaluation.run import run_final
from latenttrigger.models.background import load_background_features, run_background
from latenttrigger.models.pca import (
    PCAReconstruction,
    validate_config,
    validate_input_store,
)


@pytest.fixture
def features():
    rng = np.random.default_rng(1729)
    latent = rng.normal(size=(240, 2))
    return (
        latent @ rng.normal(size=(2, 8)) + rng.normal(scale=0.03, size=(240, 8))
    ).astype(np.float32)


@pytest.fixture
def config():
    return json.loads(
        (Path(__file__).parents[1] / "configs/models/pca_baseline.json").read_text()
    )


def test_pca_rule_reconstruction_score_direction_and_repeat(features):
    first = PCAReconstruction.fit(features, feature_names=AGGREGATE_NAMES)
    second = PCAReconstruction.fit(features, feature_names=AGGREGATE_NAMES)
    assert first.k == int(
        np.searchsorted(first.explained_variance_ratio.cumsum(), 0.95) + 1
    )
    assert first.k == 2
    np.testing.assert_array_equal(first.components, second.components)
    assert (
        first.reconstruct(features, feature_names=AGGREGATE_NAMES).shape
        == features.shape
    )
    outlier = first.mean + 10 * first.components[-1]
    assert first.score(outlier[None, :], feature_names=AGGREGATE_NAMES)[
        0
    ] == pytest.approx(100)
    assert first.score(features, feature_names=AGGREGATE_NAMES).shape == (240,)
    assert first.score(features, feature_names=AGGREGATE_NAMES).max() < 1


@pytest.mark.parametrize("training_events", [120, 240])
@pytest.mark.parametrize("score_events", [32, 240])
def test_transparent_artifact_identity_roundtrip_and_corruption(
    features, training_events, score_events
):
    model = PCAReconstruction.fit(
        features[:training_events], feature_names=AGGREGATE_NAMES
    )
    artifact = model.artifact(provenance={"toy": True}, build={})
    loaded = PCAReconstruction.from_artifact(json.loads(json.dumps(artifact)))
    assert loaded.artifact(provenance={"toy": True}, build={}) == artifact
    np.testing.assert_array_equal(
        model.score(features[:score_events], feature_names=AGGREGATE_NAMES),
        loaded.score(features[:score_events], feature_names=AGGREGATE_NAMES),
    )
    artifact["scientific"]["mean"][0] += 1
    with pytest.raises(ValueError, match="identity"):
        PCAReconstruction.from_artifact(artifact)


def test_bad_dimensions_order_and_constant_features(features):
    with pytest.raises(ValueError, match="events,8"):
        PCAReconstruction.fit(features[:, :7], feature_names=AGGREGATE_NAMES)
    with pytest.raises(ValueError, match="order"):
        PCAReconstruction.fit(features, feature_names=AGGREGATE_NAMES[::-1])
    with pytest.raises(ValueError, match="constant"):
        PCAReconstruction.fit(np.ones((12, 8)), feature_names=AGGREGATE_NAMES)
    with pytest.raises(ValueError, match="all eight"):
        PCAReconstruction.fit(
            np.random.default_rng(1).normal(size=(3000, 8)),
            feature_names=AGGREGATE_NAMES,
            target=0.9999,
        )


@pytest.mark.parametrize(
    "field", ["features", "processed_schema_version", "preprocessing_config_sha256"]
)
def test_input_schema_and_provenance_mismatch(config, field):
    science = {
        "scope": "full",
        "aggregate_channels": list(AGGREGATE_NAMES),
        "config_sha256": config["input"]["preprocessing_config_sha256"],
    }
    manifest = {"schema_version": 1, "scientific": science}
    validate_input_store(manifest, config)
    if field == "features":
        science["aggregate_channels"].reverse()
    elif field == "processed_schema_version":
        manifest["schema_version"] = 2
    else:
        science["config_sha256"] = "wrong"
    with pytest.raises(ValueError, match="mismatch"):
        validate_input_store(manifest, config)


def test_background_config_cannot_point_at_tests(config):
    config["roles"]["fit"] = "test_background"
    with pytest.raises(ValueError, match="protocol"):
        validate_config(config)
    with pytest.raises(ValueError, match="refuses"):
        load_background_features(None, "test_signal", [], batch_events=32)


def test_final_gate_refuses_before_any_store_open(tmp_path, monkeypatch):
    def forbidden(*args):
        raise AssertionError("No store should open")

    monkeypatch.setattr("latenttrigger.evaluation.run.ProcessedStore", forbidden)
    with pytest.raises(ValueError, match="no store opened"):
        run_final(
            tmp_path / "missing",
            tmp_path / "missing-results",
            tmp_path,
            tmp_path / "output",
        )
    assert not (tmp_path / "output").exists()


@pytest.fixture
def toy_store(features, config):
    class Store:
        calls = []
        populations = {
            "train_background": features[:120],
            "validation_selection_background": features[120:180],
            "validation_calibration_background": features[180:],
            "test_background": features[:20],
            "test_signal": features[:20] + 20,
        }
        manifest = {
            "schema_version": 1,
            "scientific_sha256": "synthetic-store-only",
            "scientific": {
                "scope": "full",
                "aggregate_channels": list(AGGREGATE_NAMES),
                "config_sha256": config["input"]["preprocessing_config_sha256"],
                "counts": {k: len(v) for k, v in populations.items()},
                "source": {"dataset": "synthetic"},
                "source_integrity": {"sha256": "synthetic"},
                "split_identity_sha256": "synthetic",
            },
        }

        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def iter_features(
            self, split, *, batch_size, allow_test=False, include_labels=False
        ):
            if split.startswith("test_"):
                assert allow_test is True and include_labels is True
            self.calls.append(split)
            values = self.populations[split]
            for start in range(0, len(values), batch_size):
                chunk = values[start : start + batch_size]
                labels = (
                    np.full(len(chunk), int(split == "test_signal"), dtype=np.uint8)
                    if include_labels
                    else None
                )
                yield FeatureBatch(chunk, np.arange(start, start + len(chunk)), labels)

    return Store


def test_background_pipeline_and_independent_repeat_no_test_access(
    toy_store, config, tmp_path, monkeypatch
):
    monkeypatch.setattr("latenttrigger.models.background.ProcessedStore", toy_store)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    first = run_background(tmp_path, path, tmp_path / "one", plots=False)
    second = run_background(tmp_path, path, tmp_path / "two", plots=False)
    assert first["scientific_sha256"] == second["scientific_sha256"]
    assert all("test_" not in call for call in toy_store.calls)
    assert [r["events_read"] for r in first["scientific"]["population_access"]] == [
        120,
        60,
        60,
    ]
    assert first["scientific"]["test_model_access"] is False
    assert (tmp_path / "one/background-summary.csv").exists()


def test_final_opt_in_records_before_synthetic_test_read(
    toy_store, config, tmp_path, monkeypatch
):
    monkeypatch.setattr("latenttrigger.models.background.ProcessedStore", toy_store)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    run_background(tmp_path, path, tmp_path / "background", plots=False)

    class AuditedStore(toy_store):
        def iter_features(self, split, **kwargs):
            record = json.loads((tmp_path / "final/test-unblinding.json").read_text())
            assert record["population_access"][-1]["split"] == split
            yield from super().iter_features(split, **kwargs)

    monkeypatch.setattr("latenttrigger.evaluation.run.ProcessedStore", AuditedStore)
    result = run_final(
        tmp_path / "background/model.json",
        tmp_path / "background/results.json",
        tmp_path,
        tmp_path / "final",
        allow_test=True,
    )
    assert result["metrics"]["roc_auc"] == 1
    assert (
        json.loads((tmp_path / "final/test-unblinding.json").read_text())["status"]
        == "unblinding_complete"
    )
