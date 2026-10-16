"""Native frozen scientific behavior with durable guarded batched progress."""

import numpy as np
import torch

from raregate.benchmarks import core
from raregate.benchmarks import protocol as p
from raregate.data.inspection import AGGREGATE_NAMES
from raregate.evaluation.guarded_audit import Journal
from raregate.evaluation.metrics import (
    at_threshold,
    evaluate_scores,
    score_summary,
)
from raregate.models.autoencoder import CompactAutoencoder
from raregate.models.autoencoder import validate_input_store as ae_validate
from raregate.models.pca import PCAReconstruction
from raregate.models.pca import validate_input_store as pca_validate


def load_candidate(root, entry):
    artifact = p.read(root / entry["model_path"])
    results = p.read(root / entry["results_path"])
    config = p.read(root / entry["config_path"])
    art, cal = artifact["scientific"], results["scientific"]
    prov = art["provenance"]
    if (
        p.digest(art) != artifact["scientific_sha256"]
        or p.digest(cal) != results["scientific_sha256"]
        or cal["model_scientific_sha256"] != artifact["scientific_sha256"]
        or cal["provenance"] != prov
        or prov["model_config"] != config
        or p.digest(config) != prov["model_config_sha256"]
        or art["features"] != list(AGGREGATE_NAMES)
        or config["batch_events"] != 4096
        or [t["target_fpr"] for t in cal["thresholds"]]
        != config["thresholds"]["target_fprs"]
    ):
        raise ValueError("Frozen model/config/calibration relationship mismatch.")
    if entry["name"] == "pca-v1":
        model = PCAReconstruction.load(root / entry["model_path"])
        validator = pca_validate
        if model.k != 6:
            raise ValueError("Frozen PCA six components required.")
    elif entry["name"] == "compact-autoencoder-v2":
        model = CompactAutoencoder.load(root / entry["model_path"])
        validator = ae_validate
        if model.parameter_count != 155 or prov.get("scope") != "canonical_full":
            raise ValueError("Canonical full AE155 required.")
        if any(
            v.device.type != "cpu" or v.dtype != torch.float32
            for v in model.parameters()
        ):
            raise ValueError("Native CPU FP32 AE required.")
    else:
        raise ValueError("Only two frozen native candidates.")
    return dict(
        model=model,
        validator=validator,
        artifact=artifact,
        results=results,
        config=config,
    )


def validate_manifest(candidate, manifest):
    candidate["validator"](manifest, candidate["config"])
    art = candidate["artifact"]["scientific"]
    science = candidate["results"]["scientific"]
    prov = art["provenance"]
    if (
        manifest["scientific_sha256"] != prov["processed_scientific_sha256"]
        or science["provenance"] != prov
        or manifest["scientific"]["scope"] != "full"
    ):
        raise ValueError("Full-store frozen provenance mismatch.")
    if (
        art["model_type"] == "compact_autoencoder"
        and art["training"]["training_count"]
        != manifest["scientific"]["counts"]["train_background"]
    ):
        raise ValueError("Canonical full AE training count mismatch.")


def evaluate_candidate(
    candidate, store, directory, binding, guard, *, authorized=False
):
    if authorized is not True:
        raise ValueError(
            "Test embargo: human-authorized plan required before populations."
        )
    validate_manifest(candidate, store.manifest)
    model = candidate["model"]
    config = candidate["config"]
    cal = candidate["results"]["scientific"]
    before = core.parameter_hash(model)
    journal = Journal(directory / "test-unblinding.json", binding)
    populations = {}
    iterator = None
    try:
        with torch.inference_mode():
            for split, label in [("test_background", 0), ("test_signal", 1)]:
                count = store.manifest["scientific"]["counts"][split]
                row = journal.request(
                    split, count
                )  # Durable BEFORE constructing public iterator.
                guard.boundary("request/" + split)
                iterator = store.iter_features(
                    split,
                    batch_size=4096,
                    allow_test=True,
                    include_labels=True,
                    dev_only=False,
                )
                scores = np.empty(count, np.float64)
                cursor = 0
                previous_id = -1
                batch_index = 0
                while cursor < count:
                    expected = min(4096, count - cursor)
                    journal.inflight(row, "read", batch_index, expected)
                    guard.check()
                    batch = next(iterator)
                    actual = len(batch.event_features)
                    journal.read(row, batch_index, actual)
                    guard.check()
                    x = batch.event_features
                    event_ids = batch.event_ids
                    labels = batch.labels
                    if (
                        actual != expected
                        or x.dtype != np.float32
                        or x.shape != (expected, 8)
                        or not x.flags.c_contiguous
                        or not np.isfinite(x).all()
                        or labels is None
                        or labels.shape != (expected,)
                        or not (labels == label).all()
                        or event_ids.shape != (expected,)
                        or event_ids.dtype != np.int64
                        or not (np.diff(event_ids) > 0).all()
                        or event_ids[0] <= previous_id
                    ):
                        raise ValueError(
                            "Public batch count/features/source order/truth separation refusal."
                        )
                    previous_id = int(event_ids[-1])
                    row["batches"][-1].update(
                        first_source_id=int(event_ids[0]), last_source_id=previous_id
                    )
                    journal.inflight(row, "score", batch_index, expected)
                    guard.check()
                    output = model.score(x, feature_names=AGGREGATE_NAMES)
                    if (
                        output.dtype != np.float64
                        or output.shape != (expected,)
                        or not np.isfinite(output).all()
                        or (output < 0).any()
                    ):
                        raise ValueError("Invalid canonical finite FP64 SSE score.")
                    scores[cursor : cursor + expected] = output
                    cursor += expected
                    batch_index += 1
                    journal.scored(row, expected)
                    guard.check()
                journal.inflight(row, "verify_iterator_end", batch_index, 0)
                guard.check()
                try:
                    extra = next(iterator)
                except StopIteration:
                    row["inflight"] = None
                    row["status"] = "complete"
                    journal.persist()
                else:
                    journal.read(row, batch_index, len(extra.event_features))
                    raise ValueError("Unexpected extra source batch; no scoring/retry.")
                finally:
                    iterator.close()
                    iterator = None
                populations[split] = scores
        guard.boundary("scientific_metrics")
        bg, sig = populations["test_background"], populations["test_signal"]
        metrics = evaluate_scores(
            bg,
            sig,
            fixed_fprs=config["future_metrics"]["fixed_fprs"],
            fixed_tprs=config["future_metrics"]["fixed_tprs"],
        )
        metrics["calibrated_thresholds"] = [
            dict(
                target_fpr=t["target_fpr"],
                threshold=t["threshold"],
                **at_threshold(bg, sig, t["threshold"]),
            )
            for t in cal["thresholds"]
        ]
        evaluation = dict(
            protocol=config["evaluation_protocol"],
            model_scientific_sha256=candidate["artifact"]["scientific_sha256"],
            processed_scientific_sha256=store.manifest["scientific_sha256"],
            calibration_scientific_sha256=candidate["results"]["scientific_sha256"],
            metrics=metrics,
        )
        guard.boundary("serialization")
        p.write(
            directory / "evaluation.json",
            dict(scientific=evaluation, scientific_sha256=p.digest(evaluation)),
            exclusive=True,
        )
        p.write(
            directory / "background-summary.json", score_summary(bg), exclusive=True
        )
        for split, values in populations.items():
            np.save(directory / (split + "-scores.npy"), values, allow_pickle=False)
        if before != core.parameter_hash(model):
            raise ValueError("Frozen candidate mutation.")
        journal.document.update(
            status="scientific_body_complete_awaiting_exit",
            output_file_sha256=p.file_hash(directory / "evaluation.json"),
            parameters_before=before,
            parameters_after=core.parameter_hash(model),
        )
        journal.persist()
        return evaluation
    except BaseException as exc:
        journal.failed(exc)
        raise
    finally:
        if iterator is not None:
            iterator.close()
