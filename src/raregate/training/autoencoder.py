"""Deterministic CPU training and best-selection-state restoration."""

import random
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import (
    BatchSampler,
    DataLoader,
    Dataset,
    RandomSampler,
    SequentialSampler,
)

from raregate.models.autoencoder import (
    CompactAutoencoder,
    feature_array,
    validate_config,
)


class FeatureDataset(Dataset):
    """Feature-only tensor with vectorized batch indexing; no truth/IDs."""

    def __init__(self, values: np.ndarray):
        self.values = torch.from_numpy(feature_array(values))

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, index: int | list[int]) -> torch.Tensor:
        return self.values[index]


def feature_loader(
    values: np.ndarray, batch_size: int, *, shuffle: bool, seed: int
) -> DataLoader:
    dataset = FeatureDataset(values)
    generator = torch.Generator().manual_seed(seed)
    sampler = (
        RandomSampler(dataset, generator=generator)
        if shuffle
        else SequentialSampler(dataset)
    )
    # Disable automatic batching: the sampler sends a whole list to __getitem__.
    return DataLoader(
        dataset,
        sampler=BatchSampler(sampler, batch_size, drop_last=False),
        batch_size=None,
        num_workers=0,
        generator=generator,
    )


@contextmanager
def deterministic_cpu(seed: int, threads: int) -> Iterator[None]:
    """Seed all used RNGs, enable deterministic kernels, then restore caller state."""
    python_state, numpy_state = random.getstate(), np.random.get_state()
    previous_threads = torch.get_num_threads()
    previous = torch.are_deterministic_algorithms_enabled()
    previous_warn = torch.is_deterministic_algorithms_warn_only_enabled()
    with torch.random.fork_rng(devices=[]):
        try:
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            torch.set_num_threads(threads)
            torch.use_deterministic_algorithms(True)
            yield
        finally:
            random.setstate(python_state)
            np.random.set_state(numpy_state)
            torch.set_num_threads(previous_threads)
            torch.use_deterministic_algorithms(previous, warn_only=previous_warn)


@dataclass
class EarlyStopping:
    """Strict min_delta improvement; stop after patience consecutive failures."""

    patience: int
    min_delta: float
    best_loss: float = float("inf")
    best_epoch: int = 0
    bad_epochs: int = 0
    best_state: dict | None = None

    def update(self, epoch: int, loss: float, model: nn.Module) -> bool:
        if not np.isfinite(loss):
            raise ValueError("Nonfinite selection loss.")
        if loss < self.best_loss - self.min_delta:
            self.best_loss, self.best_epoch, self.bad_epochs = loss, epoch, 0
            self.best_state = {
                k: v.detach().cpu().clone() for k, v in model.state_dict().items()
            }
        else:
            self.bad_epochs += 1
        return self.bad_epochs >= self.patience

    def restore(self, model: nn.Module) -> None:
        if self.best_state is None:
            raise ValueError("No best model state available.")
        model.load_state_dict(self.best_state)


def epoch_loss(model: CompactAutoencoder, loader: DataLoader, optimizer=None) -> float:
    """Equal-event MSE over eight channels; validation never updates weights."""
    training = optimizer is not None
    model.train(training)
    total, events = 0.0, 0
    with torch.set_grad_enabled(training):
        for values in loader:
            if training:
                optimizer.zero_grad(set_to_none=True)
            reconstructed = model(values)
            loss = nn.functional.mse_loss(reconstructed, values)
            if not torch.isfinite(loss) or not torch.isfinite(reconstructed).all():
                raise ValueError(
                    "Nonfinite training/validation loss or reconstruction."
                )
            if training:
                loss.backward()
                optimizer.step()
            total += loss.item() * len(values)
            events += len(values)
    return total / events


def train_autoencoder(
    train: np.ndarray,
    selection: np.ndarray,
    config: dict,
    *,
    progress: bool = False,
    on_epoch: Callable[[CompactAutoencoder, list[dict], EarlyStopping], None]
    | None = None,
) -> tuple[CompactAutoencoder, list[dict], dict]:
    """Only train and selection inputs; calibration/test are absent from this API."""
    validate_config(config)
    settings = config["training"]
    with deterministic_cpu(settings["seed"], settings["num_threads"]):
        model = CompactAutoencoder().cpu()
        training_loader = feature_loader(
            train, settings["batch_size"], shuffle=True, seed=settings["seed"]
        )
        selection_loader = feature_loader(
            selection, settings["batch_size"], shuffle=False, seed=settings["seed"]
        )
        optimizer = torch.optim.Adam(model.parameters(), lr=settings["learning_rate"])
        stopping = EarlyStopping(
            settings["early_stopping_patience"], settings["min_delta"]
        )
        history = []
        for epoch in range(1, settings["max_epochs"] + 1):
            row = {
                "epoch": epoch,
                "training_mse": epoch_loss(model, training_loader, optimizer),
                "selection_mse": epoch_loss(model, selection_loader),
            }
            history.append(row)
            stop = stopping.update(epoch, row["selection_mse"], model)
            if on_epoch is not None:
                on_epoch(model, history, stopping)
            if progress and (epoch == 1 or epoch % 10 == 0 or stop):
                print(
                    f"Epoch {epoch}: train MSE={row['training_mse']:.8f}; selection MSE={row['selection_mse']:.8f}",
                    flush=True,
                )
            if stop:
                break
        stopping.restore(model)
        model.eval()
        best = history[stopping.best_epoch - 1]
        result = {
            "training_count": len(train),
            "selection_count": len(selection),
            "epochs_executed": len(history),
            "best_epoch": stopping.best_epoch,
            "best_epoch_online_training_mse": best["training_mse"],
            "best_selection_mse": best["selection_mse"],
            "restored_training_mse": epoch_loss(
                model,
                feature_loader(
                    train, settings["batch_size"], shuffle=False, seed=settings["seed"]
                ),
            ),
            "restored_selection_mse": epoch_loss(model, selection_loader),
            "stopping_reason": "patience"
            if stopping.bad_epochs >= stopping.patience
            else "max_epochs",
            "bad_epochs_at_stop": stopping.bad_epochs,
            "last_epoch": history[-1],
            "history_sha256": None,
        }
        # No timing/environment fields enter the scientific selection record.
        from raregate.data.processed import content_hash

        result["history_sha256"] = content_hash({"history": history})
        return model, history, result
