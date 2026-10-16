"""Future frozen model test evaluation; explicit opt-in and pre-read audit required.

Task 0006 exercises this gate only with synthetic fixtures. Never invoke this
on the real store during background-only model development.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from raregate.data.analysis import file_sha256, write_json
from raregate.data.inspection import AGGREGATE_NAMES
from raregate.data.processed import ProcessedStore, content_hash
from raregate.evaluation.metrics import at_threshold, evaluate_scores
from raregate.models.background import build_metadata
from raregate.models.pca import PCAReconstruction, validate_input_store


def run_final(
    model_path: Path,
    background_results: Path,
    store_path: Path,
    output: Path,
    *,
    allow_test: bool = False,
) -> dict:
    """Evaluate already-frozen artifacts, recording any unblinding before reads."""
    if allow_test is not True:
        raise ValueError(
            "Final test embargo: explicit --allow-test required; no store opened."
        )
    artifact = json.loads(model_path.read_text())
    model_type = artifact["scientific"]["model_type"]
    if model_type == "pca_reconstruction":
        model = PCAReconstruction.from_artifact(artifact)
        validate_store = validate_input_store
    elif model_type == "compact_autoencoder":
        from raregate.models.autoencoder import CompactAutoencoder
        from raregate.models.autoencoder import (
            validate_input_store as validate_ae_store,
        )

        model = CompactAutoencoder.from_artifact(artifact)
        validate_store = validate_ae_store
    else:
        raise ValueError("Unknown frozen model type.")
    result = json.loads(background_results.read_text())
    science = result["scientific"]
    if (
        content_hash(science) != result["scientific_sha256"]
        or science["model_scientific_sha256"] != artifact["scientific_sha256"]
    ):
        raise ValueError("Frozen calibration/model identity mismatch.")
    provenance = artifact["scientific"]["provenance"]
    if science["provenance"] != provenance:
        raise ValueError("Frozen result/model provenance mismatch.")
    config = provenance["model_config"]
    if content_hash(config) != provenance["model_config_sha256"]:
        raise ValueError("Model config identity mismatch.")
    with ProcessedStore(store_path) as store:
        validate_store(store.manifest, config)
        if model_type == "compact_autoencoder" and (
            provenance.get("scope") != "canonical_full"
            or artifact["scientific"]["training"]["training_count"]
            != store.manifest["scientific"]["counts"]["train_background"]
        ):
            raise ValueError(
                "Only a full canonical background-trained AE may be unblinded."
            )
        if (
            store.manifest["scientific_sha256"]
            != provenance["processed_scientific_sha256"]
        ):
            raise ValueError("Frozen model belongs to a different processed store.")
        if [p["target_fpr"] for p in science["thresholds"]] != config["thresholds"][
            "target_fprs"
        ]:
            raise ValueError("Calibration operating-point mismatch.")
        output.mkdir(parents=True, exist_ok=False)
        audit = {
            **build_metadata(),
            "status": "unblinding_started",
            "population_access": [],
            "model_scientific_sha256": artifact["scientific_sha256"],
            "model_file_sha256": file_sha256(model_path),
            "model_config_sha256": provenance["model_config_sha256"],
            "processed_scientific_sha256": store.manifest["scientific_sha256"],
            "calibration_results_scientific_sha256": result["scientific_sha256"],
            "metrics": [
                "roc_auc",
                "average_precision",
                "fixed_fpr",
                "fixed_tpr",
                "calibrated_threshold_efficiencies",
            ],
        }
        log = output / "test-unblinding.json"
        write_json(log, audit)
        populations = {}
        try:
            for split, expected_label in (("test_background", 0), ("test_signal", 1)):
                record = {
                    "split": split,
                    "requested_utc": datetime.now(UTC).isoformat(),
                    "allow_test": True,
                    "include_labels": True,
                    "events_read": 0,
                }
                audit["population_access"].append(record)
                write_json(log, audit)  # Persist BEFORE the first population read.
                values = np.empty(
                    store.manifest["scientific"]["counts"][split], dtype=np.float64
                )
                cursor = 0
                for batch in store.iter_features(
                    split,
                    batch_size=config["batch_events"],
                    allow_test=True,
                    include_labels=True,
                ):
                    if (
                        batch.labels is None
                        or not (batch.labels == expected_label).all()
                    ):
                        raise ValueError("Unexpected evaluation truth.")
                    count = len(batch.event_features)
                    values[cursor : cursor + count] = model.score(
                        batch.event_features, feature_names=AGGREGATE_NAMES
                    )
                    cursor += count
                    record["events_read"] = cursor
                if cursor != len(values):
                    raise ValueError("Test population count mismatch.")
                write_json(log, audit)
                populations[split] = values
            bg, sig = populations["test_background"], populations["test_signal"]
            metrics = evaluate_scores(
                bg,
                sig,
                fixed_fprs=config["future_metrics"]["fixed_fprs"],
                fixed_tprs=config["future_metrics"]["fixed_tprs"],
            )
            metrics["calibrated_thresholds"] = [
                {
                    "target_fpr": p["target_fpr"],
                    "threshold": p["threshold"],
                    **at_threshold(bg, sig, p["threshold"]),
                }
                for p in science["thresholds"]
            ]
            evaluation = {
                "protocol": config["evaluation_protocol"],
                "model_scientific_sha256": artifact["scientific_sha256"],
                "processed_scientific_sha256": store.manifest["scientific_sha256"],
                "calibration_scientific_sha256": result["scientific_sha256"],
                "metrics": metrics,
            }
            write_json(
                output / "evaluation.json",
                {
                    "scientific": evaluation,
                    "scientific_sha256": content_hash(evaluation),
                },
            )
            audit["status"] = "unblinding_complete"
            audit["evaluation_sha256"] = file_sha256(output / "evaluation.json")
            write_json(log, audit)
            return evaluation
        except BaseException:
            audit["status"] = "unblinding_failed_or_interrupted"
            write_json(log, audit)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--background-results", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-test", action="store_true")
    args = parser.parse_args()
    try:
        run_final(
            args.model,
            args.background_results,
            args.store,
            args.output,
            allow_test=args.allow_test,
        )
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Final evaluation refused/failed: {exc}\n")


if __name__ == "__main__":
    main()
