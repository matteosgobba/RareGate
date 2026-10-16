"""One controlled epoch-ceiling extension; verify history before later training."""

import argparse
import csv
import json
from copy import deepcopy
from pathlib import Path

import numpy as np

from raregate.data.analysis import file_sha256, write_json
from raregate.data.processed import content_hash
from raregate.models.autoencoder import CompactAutoencoder, validate_config
from raregate.training.autoencoder import EarlyStopping
from raregate.training.background import run_background


def validate_extension_config(historical: dict, extended: dict) -> None:
    """Only max_epochs 200→1000 is authorized; no extra identifier is necessary."""
    validate_config(historical)
    validate_config(extended)
    expected = deepcopy(historical)
    if expected["training"]["max_epochs"] != 200:
        raise ValueError("Historical ceiling must be 200.")
    expected["training"]["max_epochs"] = 1000
    if extended != expected:
        raise ValueError("Only training.max_epochs 200→1000 may change.")


def read_history(path: Path) -> list[dict]:
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    history = [
        {
            "epoch": int(row["epoch"]),
            "training_mse": float(row["training_mse"]),
            "selection_mse": float(row["selection_mse"]),
        }
        for row in rows
    ]
    if not history or [r["epoch"] for r in history] != list(range(1, len(history) + 1)):
        raise ValueError("Historical epoch numbering is incomplete.")
    if not np.isfinite(
        [[r["training_mse"], r["selection_mse"]] for r in history]
    ).all():
        raise ValueError("Nonfinite historical history.")
    return history


class HistoricalPrefix:
    """Read-only per-epoch audit; abort immediately on loss/selection/weight drift."""

    def __init__(self, history: list[dict], artifact: dict):
        self.history = history
        self.artifact = artifact
        self.model = CompactAutoencoder.from_artifact(artifact)
        training = artifact["scientific"]["training"]
        if (
            content_hash({"history": history}) != training["history_sha256"]
            or len(history) != training["epochs_executed"]
            or training["best_epoch"] != len(history)
        ):
            raise ValueError("Historical history/artifact endpoint mismatch.")
        self.progression: list[dict] = []
        self.complete = False

    def validate_provenance(self, context: dict) -> None:
        reference = self.artifact["scientific"]["provenance"]
        validate_extension_config(reference["model_config"], context["model_config"])
        for key in (
            "processed_scientific_sha256",
            "processed_schema_version",
            "source",
            "source_integrity",
            "preprocessing_config_sha256",
            "split_identity_sha256",
            "scope",
        ):
            if context[key] != reference[key]:
                raise ValueError(f"Convergence source/protocol mismatch: {key}.")

    def __call__(
        self, model: CompactAutoencoder, history: list[dict], stopping: EarlyStopping
    ) -> None:
        epoch = len(history)
        if epoch > len(self.history):
            if not self.complete:
                raise ValueError("Historical prefix not verified before extension.")
            return
        if epoch != len(self.progression) + 1 or history[-1] != self.history[epoch - 1]:
            raise ValueError(
                f"Historical epoch {epoch} loss mismatch; extension aborted."
            )
        expected_best = (
            int(np.argmin([r["selection_mse"] for r in self.history[:epoch]])) + 1
        )
        if (
            stopping.best_epoch != expected_best
            or stopping.best_loss != self.history[expected_best - 1]["selection_mse"]
            or stopping.bad_epochs != epoch - expected_best
        ):
            raise ValueError(
                f"Historical epoch {epoch} best-state progression mismatch."
            )
        self.progression.append(
            {
                "epoch": epoch,
                "best_epoch": stopping.best_epoch,
                "best_loss": stopping.best_loss,
                "bad_epochs": stopping.bad_epochs,
            }
        )
        if epoch == len(self.history):
            for name, value in model.state_dict().items():
                actual = value.detach().cpu().numpy().view(np.uint8)
                expected = self.model.state_dict()[name].numpy().view(np.uint8)
                if not np.array_equal(actual, expected):
                    raise ValueError(f"Historical endpoint parameter mismatch: {name}.")
            self.complete = True
            print(
                f"Historical prefix verified exactly: {epoch} epochs, best-state progression and FP32 parameter bytes",
                flush=True,
            )

    def report(self) -> dict:
        if not self.complete:
            raise ValueError("Training ended before historical-prefix verification.")
        return {
            "verified": True,
            "epochs_verified": len(self.history),
            "losses_bitwise_equal": True,
            "best_state_progression_equal": True,
            "endpoint_parameter_bytes_equal": True,
            "historical_model_scientific_sha256": self.artifact["scientific_sha256"],
            "historical_history_sha256": content_hash({"history": self.history}),
            "best_state_progression_sha256": content_hash(
                {"progression": self.progression}
            ),
        }


def canonical_decision(
    training: dict, historical: dict, *, prefix_verified: bool, protocol_intact: bool
) -> dict:
    """Supersession depends on background selection only, separate from convergence."""
    current, previous = training["best_selection_mse"], historical["best_selection_mse"]
    conditions = {
        "historical_prefix_verified": prefix_verified is True,
        "continued_beyond_historical_ceiling": training["epochs_executed"] > 200,
        "selection_mse_strictly_improved": bool(
            np.isfinite(current) and np.isfinite(previous) and current < previous
        ),
        "protocol_and_embargo_intact": protocol_intact is True,
    }
    return {
        "conditions": conditions,
        "canonical_model": "compact-autoencoder-v2"
        if all(conditions.values())
        else "compact-autoencoder-v1",
        "selection_mse_improvement": previous - current,
        "selection_mse_relative_improvement": (previous - current) / previous,
        "convergence_status": "closed_under_frozen_patience_rule"
        if training["stopping_reason"] == "patience"
        else "unresolved_epoch_cap",
        "stopping_epoch": training["epochs_executed"],
    }


def recent_trend(history: list[dict]) -> dict:
    """Descriptive evidence only; never used as a new stopping criterion."""
    result = {}
    for window in (50, 100):
        if len(history) <= window:
            continue
        values = np.asarray(
            [row["selection_mse"] for row in history[-window:]], dtype=np.float64
        )
        previous = history[-window - 1]["selection_mse"]
        result[str(window)] = {
            "endpoint_improvement_over_epochs": previous - history[-1]["selection_mse"],
            "least_squares_slope_mse_per_epoch": float(
                np.polyfit(np.arange(window), values, 1)[0]
            ),
        }
    return result


def plot_convergence(path: Path, history: list[dict], training: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    epochs = [row["epoch"] for row in history]
    for axis in axes:
        axis.plot(
            epochs, [r["training_mse"] for r in history], label="Training (online)"
        )
        axis.plot(
            epochs, [r["selection_mse"] for r in history], label="Selection validation"
        )
        axis.axvline(
            200, color="grey", linestyle="--", label="Historical epoch-200 cap"
        )
        axis.axvline(
            training["best_epoch"],
            color="black",
            linestyle=":",
            label=f"Best {training['best_epoch']}",
        )
        axis.axvline(
            training["epochs_executed"],
            color="tab:red",
            linestyle="-.",
            label=f"Stopped {training['epochs_executed']}",
        )
        axis.set(xlabel="Epoch", ylabel="Reconstruction MSE (8 channels)")
    axes[0].set(title="Complete controlled run", yscale="log")
    axes[0].legend(fontsize=8)
    tail = [r for r in history if r["epoch"] >= 200]
    if tail:
        axes[1].set(
            xlim=(195, training["epochs_executed"] + 5),
            ylim=(
                min(min(r["training_mse"], r["selection_mse"]) for r in tail) * 0.995,
                max(max(r["training_mse"], r["selection_mse"]) for r in tail) * 1.005,
            ),
        )
    axes[1].set_title("After historical boundary (expanded scale)")
    fig.suptitle("LHCO R&D v5 — compact AE convergence; background only")
    fig.savefig(path / "convergence.png", dpi=170)
    plt.close(fig)


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=root / "configs/models/compact_autoencoder_v2.json",
    )
    parser.add_argument(
        "--historical-model",
        type=Path,
        default=root / "artifacts/models/compact-autoencoder-v1/model.json",
    )
    parser.add_argument(
        "--historical-history",
        type=Path,
        default=root / "results/tables/final/task0007-autoencoder-training-history.csv",
    )
    parser.add_argument(
        "--store", type=Path, default=root / "data/processed/lhco-rd-v1/schema-v1/full"
    )
    parser.add_argument(
        "--output", type=Path, default=root / "data/baselines/compact-autoencoder-v2"
    )
    args = parser.parse_args()
    try:
        artifact = json.loads(args.historical_model.read_text())
        config = json.loads(args.config.read_text())
        validate_extension_config(
            artifact["scientific"]["provenance"]["model_config"], config
        )
        reference = HistoricalPrefix(read_history(args.historical_history), artifact)
        result = run_background(
            args.store,
            args.config,
            args.output,
            plots=False,
            save_scores=False,
            convergence_reference=reference,
        )
        science = result["scientific"]
        plot_convergence(args.output, science["training_history"], science["training"])
        summary = {
            "scientific": science,
            "scientific_sha256": result["scientific_sha256"],
            "recent_selection_trend": recent_trend(science["training_history"]),
        }
        write_json(args.output / "convergence-summary.json", summary)
        manifest_path = args.output / "run-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["convergence_reports_complete"] = True
        manifest["files"] = {
            p.name: {"bytes": p.stat().st_size, "sha256": file_sha256(p)}
            for p in sorted(args.output.iterdir())
            if p != manifest_path
        }
        write_json(manifest_path, manifest)
        print(json.dumps(science["convergence_checks"]["canonical_decision"], indent=2))
    except (ValueError, OSError, ImportError) as exc:
        parser.exit(1, f"Convergence run refused/failed: {exc}\n")


if __name__ == "__main__":
    main()
