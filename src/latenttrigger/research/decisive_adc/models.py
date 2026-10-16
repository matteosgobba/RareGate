"""New twelve-input models, finite fitting and canonical public scoring."""

import hashlib
import inspect
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

from .data import digest, write_json

LAYERS = {"compactAE": (12, 8, 3, 8, 12), "referenceAE": (12, 32, 16, 3, 16, 32, 12)}
STREAMS = [(arm, str(seed)) for seed in (1729, 1730, 1731) for arm in LAYERS] + [
    ("PCA3", "fit"),
    ("regularizedMahalanobis", "fit"),
]
ADAM = dict(
    lr=0.001,
    betas=(0.9, 0.999),
    eps=1e-8,
    weight_decay=0.0,
    amsgrad=False,
    foreach=False,
    fused=False,
    maximize=False,
    capturable=False,
    differentiable=False,
    decoupled_weight_decay=False,
)


class ADCNet(nn.Module):
    def __init__(self, arm, seed):
        super().__init__()
        with torch.random.fork_rng(devices=[]):
            torch.random.default_generator.manual_seed(seed)
            widths = LAYERS[arm]
            layers = []
            for i, (before, after) in enumerate(
                zip(widths[:-1], widths[1:], strict=True)
            ):
                layers.append(
                    nn.Linear(before, after, device="cpu", dtype=torch.float32)
                )
                if i not in (len(widths) // 2 - 1, len(widths) - 2):
                    layers.append(nn.ReLU())
            self.network = nn.Sequential(*layers)

    def forward(self, x):
        if (
            x.device.type != "cpu"
            or x.dtype != torch.float32
            or x.ndim != 2
            or x.shape[1] != 12
        ):
            raise ValueError("ADC CPU FP32[N,12] required")
        return self.network(x)


def state_digest(model):
    result = hashlib.sha256()
    for name, tensor in model.state_dict().items():
        array = tensor.detach().cpu().numpy()
        result.update(
            name.encode()
            + str(array.shape).encode()
            + str(array.dtype).encode()
            + array.tobytes()
        )
    return result.hexdigest()


def selection_loss(model, values, batch=2048):
    total = 0.0
    with torch.inference_mode():
        for start in range(0, len(values), batch):
            x = torch.from_numpy(
                np.array(values[start : start + batch], dtype=np.float32, copy=True)
            )
            loss = torch.mean((model(x) - x) ** 2).item()
            total += len(x) * loss
    return total / len(values)


def train(arm, seed, training, selection, progress, epochs=80, patience=8, batch=2048):
    model = ADCNet(arm, seed)
    if not set(ADAM) <= set(inspect.signature(torch.optim.Adam).parameters):
        raise ValueError("installed Adam does not support frozen options")
    optimizer = torch.optim.Adam(model.parameters(), **ADAM)
    resolved = {k: optimizer.defaults[k] for k in ADAM}
    if resolved != ADAM:
        raise ValueError("Adam options differ")
    sampler = torch.Generator(device="cpu").manual_seed(seed)
    values = torch.from_numpy(np.array(training, dtype=np.float32, copy=True))
    best, best_epoch, wait, history, updates = math.inf, None, 0, [], 0
    best_state = None
    progress(
        "fit_initialized",
        parameters=sum(p.numel() for p in model.parameters()),
        sampler_seed=seed,
    )
    started = time.monotonic()
    for epoch in range(1, epochs + 1):
        order = torch.randperm(len(values), generator=sampler)
        order_hash = hashlib.sha256(order.numpy().astype("<i8").tobytes()).hexdigest()
        total, batches = 0.0, 0
        progress(
            "epoch_started", epoch=epoch, order_sha256=order_hash, rows=len(values)
        )
        for start in range(0, len(values), batch):
            x = values[order[start : start + batch]]
            progress(
                "batch_started",
                epoch=epoch,
                batch=batches + 1,
                rows=len(x),
                updates_completed=updates,
            )
            optimizer.zero_grad(set_to_none=True)
            loss = torch.mean((model(x) - x) ** 2)
            if not torch.isfinite(loss):
                raise ValueError("nonfinite training loss")
            loss.backward()
            optimizer.step()
            updates += 1
            batches += 1
            total += len(x) * loss.item()
            progress(
                "batch_completed",
                epoch=epoch,
                batch=batches,
                rows=len(x),
                updates_completed=updates,
            )
        val = selection_loss(model, selection, batch)
        if not math.isfinite(val):
            raise ValueError("nonfinite selection loss")
        if val < best:
            best, best_epoch, wait = val, epoch, 0
            best_state = {
                name: value.detach().clone()
                for name, value in model.state_dict().items()
            }
        else:
            wait += 1
        row = dict(
            epoch=epoch,
            training_loss=total / len(values),
            selection_loss=val,
            order_sha256=order_hash,
            batches=batches,
            training_rows=len(values),
            selection_rows=len(selection),
            selected_epoch=best_epoch,
            elapsed_seconds=time.monotonic() - started,
        )
        history.append(row)
        progress("epoch_completed", **row)
        if wait >= patience:
            break
    model.load_state_dict(best_state, strict=True)
    restored = selection_loss(model, selection, batch)
    if restored != best:
        raise ValueError("restored-selection loss mismatch")
    model.eval()
    return model, dict(
        schema_version=2,
        arm=arm,
        seed=seed,
        history=history,
        selected_epoch=best_epoch,
        best_selection_loss=best,
        restored_selection_loss=restored,
        updates=updates,
        training_rows_presented=updates // math.ceil(len(values) / batch) * len(values),
        selection_rows_presented=(len(history) + 1) * len(selection),
        stop_reason="patience" if wait >= patience else "epoch_cap",
        state_sha256=state_digest(model),
        adam_resolved=resolved,
        parameters=sum(p.numel() for p in model.parameters()),
    )


def fit_analytical(arm, training):
    x = np.array(training, dtype=np.float64, copy=True)
    mean = x.mean(axis=0)
    centered = x - mean
    if arm == "PCA3":
        _, singular, vt = np.linalg.svd(centered, full_matrices=False)
        return dict(
            arm=arm, mean=mean, components=vt[:3].copy(), singular_values=singular
        )
    if arm != "regularizedMahalanobis":
        raise ValueError("unknown analytical arm")
    covariance = centered.T @ centered / len(x)
    regularized = 0.9 * covariance + 0.1 * np.trace(covariance) / 12 * np.eye(12)
    return dict(arm=arm, mean=mean, cholesky=np.linalg.cholesky(regularized))


def save_model(directory, arm, seed, model, history):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    if isinstance(model, ADCNet):
        arrays = {
            key: value.detach().numpy() for key, value in model.state_dict().items()
        }
    else:
        arrays = {key: value for key, value in model.items() if key != "arm"}
    with (directory / "weights.npz").open("xb") as stream:
        np.savez(stream, **arrays)
    write_json(directory / "history.json", history)
    record = dict(
        schema_version=2,
        representation="adc-invariant-aggregates-v2",
        input_dim=12,
        arm=arm,
        seed=str(seed),
        weights_sha256=digest(directory / "weights.npz"),
        history_sha256=digest(directory / "history.json"),
        score="higher; FP64 SSE/quadratic; canonical B32 padded tail",
    )
    write_json(directory / "model.json", record)
    return record


def load_model(directory):
    directory = Path(directory)
    record = json.loads((directory / "model.json").read_text())
    if (
        record["schema_version"] != 2
        or record["input_dim"] != 12
        or record["representation"] != "adc-invariant-aggregates-v2"
    ):
        raise ValueError("ADC schema2 contract")
    if (
        digest(directory / "weights.npz") != record["weights_sha256"]
        or digest(directory / "history.json") != record["history_sha256"]
    ):
        raise ValueError("model content mismatch")
    with np.load(directory / "weights.npz", allow_pickle=False) as archive:
        arrays = {k: archive[k].copy() for k in archive}
    if record["arm"] in LAYERS:
        model = ADCNet(record["arm"], int(record["seed"]))
        if any(value.dtype != np.float32 for value in arrays.values()):
            raise ValueError("FP32 weights required")
        model.load_state_dict(
            {k: torch.from_numpy(v) for k, v in arrays.items()}, strict=True
        )
        model.eval()
        if (
            state_digest(model)
            != json.loads((directory / "history.json").read_text())["state_sha256"]
        ):
            raise ValueError("state reload mismatch")
        return model
    return dict(arm=record["arm"], **arrays)


def public_score(model, x):
    x = np.asarray(x)
    if (
        x.dtype != np.float32
        or x.shape not in ((1, 12), (32, 12), (512, 12))
        or not np.isfinite(x).all()
    ):
        raise ValueError("public CPU shape/dtype")
    if isinstance(model, ADCNet):
        with torch.inference_mode():
            prediction = (
                model(torch.from_numpy(np.array(x, copy=True)))
                .numpy()
                .astype(np.float64)
            )
        scores = np.square(prediction - x.astype(np.float64)).sum(axis=1)
    else:
        centered = x.astype(np.float64) - model["mean"]
        if model["arm"] == "PCA3":
            residual = (
                centered - (centered @ model["components"].T) @ model["components"]
            )
            scores = np.square(residual).sum(axis=1)
        elif model["arm"] == "regularizedMahalanobis":
            solved = np.linalg.solve(model["cholesky"], centered.T)
            scores = np.square(solved).sum(axis=0)
        else:
            raise ValueError("unknown score arm")
    if not np.isfinite(scores).all() or np.any(scores < 0):
        raise ValueError("invalid public score")
    return scores.copy()


def score_rows(model, values, out=None):
    output = np.empty(len(values), dtype=np.float64) if out is None else out
    for start in range(0, len(values), 32):
        actual = min(32, len(values) - start)
        batch = np.zeros((32, 12), dtype=np.float32)
        batch[:actual] = values[start : start + actual]
        output[start : start + actual] = public_score(model, batch)[:actual]
    return output
