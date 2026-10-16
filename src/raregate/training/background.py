"""Compact AE orchestration: train/selection first, calibration after freezing."""

import argparse
import csv
import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch

from raregate.data.analysis import file_sha256, peak_rss_bytes, write_json
from raregate.data.processed import ProcessedStore, content_hash
from raregate.evaluation.metrics import ks_distance, score_summary
from raregate.evaluation.thresholds import (
    background_operating_point,
    calibrate_thresholds,
)
from raregate.models.autoencoder import (
    CompactAutoencoder,
    validate_config,
    validate_input_store,
)
from raregate.models.background import (
    build_metadata,
    load_background_features,
    score_batches,
)
from raregate.models.pca import BACKGROUND_ROLES
from raregate.models.reporting import write_tables
from raregate.training.autoencoder import (
    deterministic_cpu,
    epoch_loss,
    feature_loader,
    train_autoencoder,
)

if TYPE_CHECKING:
    from raregate.training.convergence import HistoricalPrefix


def plot_training(path: Path, history: list[dict], training: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    epochs = [row["epoch"] for row in history]
    for field, label in (
        ("training_mse", "Training (online)"),
        ("selection_mse", "Selection validation"),
    ):
        axis.plot(epochs, [row[field] for row in history], label=label)
    axis.axvline(
        training["best_epoch"],
        linestyle=":",
        color="black",
        label=f"Selected epoch {training['best_epoch']}",
    )
    if training["epochs_executed"] != training["best_epoch"]:
        axis.axvline(
            training["epochs_executed"], linestyle="--", color="grey", label="Stopped"
        )
    axis.set(
        xlabel="Epoch",
        ylabel="Mean squared reconstruction error (8 channels)",
        yscale="log",
        title="LHCO R&D v5 — compact AE; train / selection background only",
    )
    axis.legend()
    fig.savefig(path / "training-history.png", dpi=170)
    plt.close(fig)


def run_background(
    store_path: Path,
    config_path: Path,
    output: Path,
    *,
    dev: bool = False,
    plots: bool = True,
    save_scores: bool = True,
    convergence_reference: "HistoricalPrefix | None" = None,
) -> dict:
    """Exclusive output, frozen CPU model, feature-only audited background reads."""
    config = json.loads(config_path.read_text())
    validate_config(config)  # Before opening the store or creating outputs.
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
        build["environment"]["torch"] = torch.__version__
        build["torch_threads"] = config["training"]["num_threads"]
        build["torch_interop_threads"] = torch.get_num_interop_threads()
        with ProcessedStore(store_path) as store:
            validate_input_store(store.manifest, config, dev=dev)
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
                "scope": "dev_diagnostic" if dev else "canonical_full",
            }
            if convergence_reference is not None:
                convergence_reference.validate_provenance(context)
            values = {}
            for role in BACKGROUND_ROLES[:2]:
                tick = time.perf_counter()
                values[role] = load_background_features(
                    store,
                    role,
                    audit,
                    batch_events=config["batch_events"],
                    dev_only=dev,
                )
                audit[-1]["purpose"] = (
                    "gradient_training"
                    if role == BACKGROUND_ROLES[0]
                    else "early_stopping"
                )
                timings[f"{role}_load_seconds"] = time.perf_counter() - tick
            tick = time.perf_counter()
            model, history, training = train_autoencoder(
                values[BACKGROUND_ROLES[0]],
                values[BACKGROUND_ROLES[1]],
                config,
                progress=True,
                on_epoch=convergence_reference,
            )
            timings["training_seconds"] = time.perf_counter() - tick
            artifact = model.artifact(provenance=context, training=training)
            write_json(stage / "model.json", artifact)
            restored = CompactAutoencoder.load(stage / "model.json")
            for name, parameter in model.state_dict().items():
                if not torch.equal(parameter, restored.state_dict()[name]):
                    raise ValueError("Serialized model parameter mismatch.")
            convergence_checks = None
            if convergence_reference is not None:
                from raregate.training.convergence import canonical_decision

                convergence_checks = convergence_reference.report()
                # A second evaluation using the JSON-reloaded frozen network.
                with deterministic_cpu(
                    config["training"]["seed"], config["training"]["num_threads"]
                ):
                    independently_restored_mse = epoch_loss(
                        restored,
                        feature_loader(
                            values[BACKGROUND_ROLES[1]],
                            config["training"]["batch_size"],
                            shuffle=False,
                            seed=config["training"]["seed"],
                        ),
                    )
                if independently_restored_mse != training["best_selection_mse"]:
                    raise ValueError(
                        "JSON-restored best validation loss differs from selected epoch."
                    )
                convergence_checks["independently_restored_selection_mse"] = (
                    independently_restored_mse
                )
                convergence_checks["canonical_decision"] = canonical_decision(
                    training,
                    convergence_reference.artifact["scientific"]["training"],
                    prefix_verified=convergence_checks["verified"],
                    protocol_intact=True,
                )
            # Calibration is first requested AFTER best-state restoration and export.
            role = BACKGROUND_ROLES[2]
            tick = time.perf_counter()
            values[role] = load_background_features(
                store, role, audit, batch_events=config["batch_events"], dev_only=dev
            )
            audit[-1]["purpose"] = "frozen_threshold_calibration"
            timings[f"{role}_load_seconds"] = time.perf_counter() - tick
            with deterministic_cpu(
                config["training"]["seed"], config["training"]["num_threads"]
            ):
                for role in BACKGROUND_ROLES:
                    tick = time.perf_counter()
                    scores[role] = score_batches(
                        restored, values[role], config["batch_events"]
                    )
                    timings[f"{role}_score_seconds"] = time.perf_counter() - tick
                    if save_scores:
                        np.save(
                            stage / f"{role}-scores.npy",
                            scores[role],
                            allow_pickle=False,
                        )
                sample = values[BACKGROUND_ROLES[0]][:4096]
                with torch.inference_mode():
                    latent = (
                        restored.encode(torch.from_numpy(sample))
                        .numpy()
                        .astype(np.float64)
                    )
                if not np.isfinite(latent).all():
                    raise ValueError("Nonfinite latent representation.")
                latent_stats = {
                    "population": "train_background",
                    "sampling": "first_min_4096_in_source_ordinal_order",
                    "count": len(sample),
                    "mean": latent.mean(axis=0).tolist(),
                    "std_ddof0": latent.std(axis=0).tolist(),
                    "collapsed_std_threshold": 1e-6,
                    "collapsed": (latent.std(axis=0) <= 1e-6).tolist(),
                }
            train, selection, calibration = (scores[name] for name in BACKGROUND_ROLES)
            thresholds = calibrate_thresholds(
                calibration, config["thresholds"]["target_fprs"]
            )
            for point in thresholds:
                check = background_operating_point(selection, point["threshold"])
                delta = check["efficiency"] - point["target_fpr"]
                point.update(
                    selection=check,
                    absolute_deviation=abs(delta),
                    relative_deviation=delta / point["target_fpr"],
                )
            scientific = {
                "protocol": config["evaluation_protocol"],
                "provenance": context,
                "model_scientific_sha256": artifact["scientific_sha256"],
                "parameter_count": model.parameter_count,
                "latent_dim": 3,
                "training": training,
                "training_history": history,
                "latent_training_sanity": latent_stats,
                "score_definition": config["score"]["definition"],
                "background_summary": {
                    role: score_summary(scores[role]) for role in BACKGROUND_ROLES
                },
                "thresholds": thresholds,
                "stability": {
                    "train_vs_selection_ks": ks_distance(train, selection),
                    "train_vs_calibration_ks": ks_distance(train, calibration),
                    "selection_vs_calibration_ks": ks_distance(selection, calibration),
                },
                "population_access": audit,
                "test_model_access": False,
            }
            if convergence_checks is not None:
                scientific["convergence_checks"] = convergence_checks
            if not save_scores:
                scientific["score_array_sha256"] = {
                    role: hashlib.sha256(
                        np.asarray(scores[role], dtype="<f8").tobytes()
                    ).hexdigest()
                    for role in BACKGROUND_ROLES
                }
        write_tables(stage, scientific)
        with (stage / "training-history.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(
                stream, fieldnames=list(history[0]), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(history)
        if plots:
            from raregate.models.reporting import plot_score_distributions

            plot_training(stage, history, training)
            plot_score_distributions(stage, scores, thresholds, model_name="Compact AE")
        build.update(
            timings=timings,
            total_seconds_before_finalize=time.perf_counter() - started,
            peak_rss_bytes_lifetime=peak_rss_bytes(),
            model_bytes=(stage / "model.json").stat().st_size,
        )
        result = {
            "scientific": scientific,
            "scientific_sha256": content_hash(scientific),
            "build": build,
        }
        write_json(stage / "results.json", result)
        write_json(
            stage / "run-manifest.json",
            {
                "complete": True,
                "model_scientific_sha256": artifact["scientific_sha256"],
                "scientific_sha256": result["scientific_sha256"],
                "population_access": audit,
                "test_model_access": False,
                "files": {
                    p.name: {"bytes": p.stat().st_size, "sha256": file_sha256(p)}
                    for p in sorted(stage.iterdir())
                },
            },
        )
        if output.exists():
            raise ValueError("Another run created output; refusing promotion.")
        stage.rename(output)
        print(
            f"Frozen background-only AE: best epoch {training['best_epoch']}; {artifact['scientific_sha256']}\nOutput: {output}",
            flush=True,
        )
        return result
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def mps_smoke(store_path: Path, config_path: Path) -> dict:
    """Separate bounded dev-training compatibility check; never exports a model."""
    config = json.loads(config_path.read_text())
    validate_config(config)
    if not torch.backends.mps.is_available():
        raise ValueError("MPS unavailable; compatibility check cannot run.")
    audit = []
    with ProcessedStore(store_path) as store:
        validate_input_store(store.manifest, config, dev=True)
        values = load_background_features(
            store, "train_background", audit, batch_events=4096, dev_only=True
        )[:256]
    with deterministic_cpu(
        config["training"]["seed"], config["training"]["num_threads"]
    ):
        model = CompactAutoencoder().to("mps")
        tensor = torch.from_numpy(values).to("mps")
        optimizer = torch.optim.Adam(
            model.parameters(), lr=config["training"]["learning_rate"]
        )
        losses = []
        for _ in range(5):
            optimizer.zero_grad(set_to_none=True)
            reconstruction = model(tensor)
            loss = torch.nn.functional.mse_loss(reconstruction, tensor)
            if not torch.isfinite(loss) or not torch.isfinite(reconstruction).all():
                raise ValueError("MPS nonfinite reconstruction/loss.")
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        from raregate.data.inspection import AGGREGATE_NAMES

        scores = model.score(values, feature_names=AGGREGATE_NAMES)
        if not np.isfinite(scores).all():
            raise ValueError("MPS nonfinite scores.")
    return {
        "device": "mps",
        "events": len(values),
        "steps": 5,
        "losses": losses,
        "scores_finite": True,
        "model_exported": False,
        "population_access": audit,
        "test_model_access": False,
        "purpose": "compatibility_only_not_model_selection",
    }


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=root / "configs/models/compact_autoencoder.json"
    )
    parser.add_argument(
        "--store", type=Path, default=root / "data/processed/lhco-rd-v1/schema-v1/full"
    )
    parser.add_argument(
        "--output", type=Path, default=root / "data/baselines/compact-autoencoder-v1"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Only frozen dev membership; never a canonical model.",
    )
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Bounded MPS compatibility only; writes no model.",
    )
    args = parser.parse_args()
    try:
        if args.device == "mps" and args.smoke and not args.dev:
            print(json.dumps(mps_smoke(args.store, args.config), indent=2))
        elif args.device != "cpu" or args.smoke:
            raise ValueError(
                "Canonical training is CPU; MPS requires --device mps --smoke."
            )
        else:
            run_background(
                args.store,
                args.config,
                args.output,
                dev=args.dev,
                plots=not args.no_plots,
            )
    except (ValueError, OSError, ImportError) as exc:
        parser.exit(1, f"Autoencoder run refused/failed: {exc}\n")
