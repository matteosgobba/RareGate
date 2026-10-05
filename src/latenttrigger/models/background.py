"""PCA fitting and background-only diagnostics; no test evaluation code path."""

import argparse
import json
import platform
import shutil
import subprocess
import time
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import numpy as np

from latenttrigger import __version__
from latenttrigger.data.analysis import file_sha256, peak_rss_bytes, write_json
from latenttrigger.data.inspection import AGGREGATE_NAMES
from latenttrigger.data.processed import ProcessedStore, content_hash
from latenttrigger.evaluation.metrics import ks_distance, score_summary
from latenttrigger.evaluation.thresholds import (
    background_operating_point,
    calibrate_thresholds,
)
from latenttrigger.models.pca import (
    BACKGROUND_ROLES,
    PCAReconstruction,
    validate_input_store,
)


def build_metadata() -> dict:
    root = Path(__file__).resolve().parents[3]
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain", "--untracked-files=all"],
                cwd=root,
                text=True,
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {
        "created_utc": datetime.now(UTC).isoformat(),
        "code_commit": commit,
        "code_working_tree_dirty": dirty,
        "project_version": __version__,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            **{name: version(name) for name in ("numpy", "scikit-learn", "scipy")},
        },
        "code_sha256": {
            str(path.relative_to(root)): file_sha256(path)
            for directory in ("models", "evaluation", "data")
            for path in sorted((root / "src/latenttrigger" / directory).glob("*.py"))
        },
    }


def load_background_features(
    store: ProcessedStore, split: str, audit: list, *, batch_events: int
) -> np.ndarray:
    """Only predefined background roles, rejecting forbidden names before reading."""
    if split not in BACKGROUND_ROLES:
        raise ValueError("Background workflow refuses test/unknown split access.")
    expected = store.manifest["scientific"]["counts"][split]
    values = np.empty((expected, 8), dtype=np.float32)
    record = {
        "split": split,
        "allow_test": False,
        "include_labels": False,
        "representation": "event_features",
        "events_read": 0,
    }
    audit.append(record)
    cursor = 0
    for batch in store.iter_features(split, batch_size=batch_events):
        if batch.labels is not None or cursor + len(batch.event_features) > expected:
            raise ValueError("Unexpected truth/count in background feature reader.")
        stop = cursor + len(batch.event_features)
        values[cursor:stop] = batch.event_features
        cursor = stop
    record["events_read"] = cursor
    if cursor != expected or not np.isfinite(values).all():
        raise ValueError("Background population count/finite feature mismatch.")
    return values


def score_batches(
    model: PCAReconstruction, values: np.ndarray, batch_events: int
) -> np.ndarray:
    scores = np.empty(len(values), dtype=np.float64)
    for start in range(0, len(values), batch_events):
        stop = min(start + batch_events, len(values))
        scores[start:stop] = model.score(
            values[start:stop], feature_names=AGGREGATE_NAMES
        )
    if not np.isfinite(scores).all() or (scores < 0).any():
        raise ValueError("Invalid reconstruction scores.")
    return scores


def run_background(
    store_path: Path, config_path: Path, output: Path, *, plots: bool = True
) -> dict:
    """One frozen-policy run; refuse overwriting output and never opt in to tests."""
    config = json.loads(config_path.read_text())
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = output.with_name(f".{output.name}.partial")
    if output.exists() or output.is_symlink() or stage.exists():
        raise ValueError("Output/partial exists; choose a new run directory.")
    stage.mkdir()
    started = time.perf_counter()
    audit, timings, scores = [], {}, {}
    try:
        build = build_metadata()
        with ProcessedStore(store_path) as store:
            validate_input_store(store.manifest, config)
            science = store.manifest["scientific"]
            context = {
                "processed_scientific_sha256": store.manifest["scientific_sha256"],
                "processed_schema_version": store.manifest["schema_version"],
                "source": science["source"],
                "source_integrity": science["source_integrity"],
                "preprocessing_config_sha256": science["config_sha256"],
                "split_identity_sha256": science["split_identity_sha256"],
                "model_config": config,
                "model_config_sha256": content_hash(config),
            }
            for index, split in enumerate(BACKGROUND_ROLES):
                tick = time.perf_counter()
                values = load_background_features(
                    store, split, audit, batch_events=config["batch_events"]
                )
                timings[f"{split}_load_seconds"] = time.perf_counter() - tick
                if index == 0:
                    tick = time.perf_counter()
                    model = PCAReconstruction.fit(
                        values,
                        feature_names=config["input"]["features"],
                        target=config["pca"]["explained_variance_target"],
                    )
                    timings["fit_seconds"] = time.perf_counter() - tick
                    print(
                        f"Fitted {len(values):,} training events; k={model.k}; retained variance={model.explained_variance_ratio[: model.k].sum():.8f}",
                        flush=True,
                    )
                    artifact = model.artifact(provenance=context, build=build)
                    write_json(stage / "model.json", artifact)
                    loaded = PCAReconstruction.load(stage / "model.json")
                    np.testing.assert_array_equal(
                        loaded.score(values[:32], feature_names=AGGREGATE_NAMES),
                        model.score(values[:32], feature_names=AGGREGATE_NAMES),
                    )
                tick = time.perf_counter()
                scores[split] = score_batches(model, values, config["batch_events"])
                timings[f"{split}_score_seconds"] = time.perf_counter() - tick
                np.save(
                    stage / f"{split}-scores.npy", scores[split], allow_pickle=False
                )
                print(
                    f"Background scored: {split}, {len(values):,}; test access disabled",
                    flush=True,
                )
                del values
            train, selection, calibration = (scores[name] for name in BACKGROUND_ROLES)
            summaries = {name: score_summary(values) for name, values in scores.items()}
            thresholds = calibrate_thresholds(
                calibration, config["thresholds"]["target_fprs"]
            )
            for point in thresholds:
                verification = background_operating_point(selection, point["threshold"])
                deviation = verification["efficiency"] - point["target_fpr"]
                point.update(
                    selection=verification,
                    absolute_deviation=abs(deviation),
                    relative_deviation=deviation / point["target_fpr"],
                )
            stability = {
                "train_vs_selection_ks": ks_distance(train, selection),
                "train_vs_calibration_ks": ks_distance(train, calibration),
                "selection_vs_calibration_ks": ks_distance(selection, calibration),
            }
            scientific = {
                "protocol": config["evaluation_protocol"],
                "provenance": context,
                "model_scientific_sha256": artifact["scientific_sha256"],
                "selected_k": model.k,
                "explained_variance": model.explained_variance.tolist(),
                "explained_variance_ratio": model.explained_variance_ratio.tolist(),
                "score_definition": config["score"]["definition"],
                "background_summary": summaries,
                "thresholds": thresholds,
                "stability": stability,
                "population_access": audit,
                "test_model_access": False,
            }
        result = {
            "scientific": scientific,
            "scientific_sha256": content_hash(scientific),
            "build": {
                **build,
                "timings": timings,
                "total_seconds_before_finalize": time.perf_counter() - started,
                "peak_rss_bytes_lifetime": peak_rss_bytes(),
                "model_file_sha256": file_sha256(stage / "model.json"),
            },
        }
        if plots:
            from latenttrigger.models.reporting import plot_background

            tick = time.perf_counter()
            plot_background(stage, model, scores, thresholds)
            timings["plot_seconds"] = time.perf_counter() - tick
        result["build"]["total_seconds_before_finalize"] = time.perf_counter() - started
        result["build"]["peak_rss_bytes_lifetime"] = peak_rss_bytes()
        # Verify both serialized scientific identities before promotion.
        PCAReconstruction.load(stage / "model.json")
        write_json(stage / "results.json", result)
        reloaded = json.loads((stage / "results.json").read_text())
        if reloaded["scientific_sha256"] != content_hash(reloaded["scientific"]):
            raise ValueError("Results identity mismatch.")
        from latenttrigger.models.reporting import write_tables

        write_tables(stage, scientific)
        write_json(
            stage / "run-manifest.json",
            {
                "complete": True,
                "scientific_sha256": result["scientific_sha256"],
                "model_scientific_sha256": artifact["scientific_sha256"],
                "files": {
                    path.name: {
                        "bytes": path.stat().st_size,
                        "sha256": file_sha256(path),
                    }
                    for path in sorted(stage.iterdir())
                },
                "population_access": audit,
                "test_model_access": False,
            },
        )
        if output.exists():
            raise ValueError("Another run created the output; refusing promotion.")
        stage.rename(output)
        print(
            f"Finalized background-only run: {output}\nScientific results: {result['scientific_sha256']}",
            flush=True,
        )
        return result
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=root / "configs/models/pca_baseline.json"
    )
    parser.add_argument(
        "--store", type=Path, default=root / "data/processed/lhco-rd-v1/schema-v1/full"
    )
    parser.add_argument("--output", type=Path, default=root / "data/baselines/pca-v1")
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Numeric results without the optional analysis extra.",
    )
    args = parser.parse_args()
    try:
        run_background(args.store, args.config, args.output, plots=not args.no_plots)
    except (ValueError, OSError, ImportError) as exc:
        parser.exit(1, f"Background run failed: {exc}\n")
