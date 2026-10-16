"""Bounded, NumPy-only raw-event inspection; no preprocessing output is produced."""

import hashlib
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


def inspect_particles(particles: NDArray, labels: NDArray) -> dict[str, NDArray]:
    """Return per-row structural flags and positive-pT multiplicity.

    Padding is exactly (0, 0, 0). A zero-pT, nonzero-angle slot is malformed;
    any non-padding slot after the first padding slot is non-trailing padding.
    """
    if particles.ndim != 3 or particles.shape[2] != 3:
        raise ValueError("Expected particles with shape [events, slots, 3].")
    if labels.shape != (len(particles),):
        raise ValueError("Expected one label per event.")
    padding = np.all(particles == 0, axis=2)
    pt = particles[:, :, 0]
    flags = {
        "unexpected_label": ~np.isin(labels, [0, 1]),
        "nan": np.isnan(particles).any(axis=(1, 2)) | np.isnan(labels),
        "infinity": np.isinf(particles).any(axis=(1, 2)) | np.isinf(labels),
        "negative_pt": (pt < 0).any(axis=1),
        "malformed_padding": ((pt == 0) & ~padding).any(axis=1),
        "non_trailing_padding": (np.maximum.accumulate(padding, axis=1) & ~padding).any(
            axis=1
        ),
        "empty": (pt > 0).sum(axis=1) == 0,
    }
    flags["multiplicity"] = (pt > 0).sum(axis=1).astype(np.uint16)
    flags["eligible"] = ~np.logical_or.reduce(list(flags.values())[:-1])
    return flags


def event_fingerprints(particles: NDArray) -> NDArray:
    """SHA-256 of count and canonical sorted float64 triplets, excluding truth.

    Remove zero padding, canonicalize signed zero, wrap only out-of-range phi
    into [-pi, pi), and lexicographically sort (pT, eta, phi). Count is uint64
    little endian; triplets are float64 little endian. Input must be valid.
    Particle operations are vectorized; hashlib requires one digest per event.
    """
    values = np.array(particles, dtype="<f8", copy=True)
    values[values == 0] = 0.0
    phi = values[:, :, 2]
    wrap = (phi < -np.pi) | (phi >= np.pi)
    phi[wrap] = (phi[wrap] + np.pi) % (2 * np.pi) - np.pi
    phi[phi == 0] = 0.0
    valid = values[:, :, 0] > 0
    counts = valid.sum(axis=1)
    keys = np.where(valid, values[:, :, 0], np.inf)
    order = np.lexsort((phi, values[:, :, 1], keys), axis=1)
    values = np.take_along_axis(values, order[:, :, None], axis=1)
    fingerprints = np.empty(len(values), dtype="V32")
    for i, count in enumerate(counts):
        digest = hashlib.sha256(np.asarray(count, dtype="<u8").tobytes())
        digest.update(values[i, :count].tobytes())
        fingerprints[i] = digest.digest()
    return fingerprints


@dataclass
class Moments:
    """Merge float64 population moments from bounded batches."""

    count: int = 0
    mean: float = 0.0
    m2: float = 0.0
    minimum: float = float("inf")
    maximum: float = float("-inf")

    def update(self, values: NDArray) -> None:
        values = np.asarray(values, dtype=np.float64).ravel()
        if not len(values):
            return
        if not np.isfinite(values).all():
            raise ValueError("Statistics require finite values.")
        n = len(values)
        mean = float(values.mean())
        m2 = float(np.square(values - mean).sum())
        delta = mean - self.mean
        total = self.count + n
        self.m2 += m2 + delta**2 * self.count * n / total
        self.mean += delta * n / total
        self.count = total
        self.minimum = min(self.minimum, float(values.min()))
        self.maximum = max(self.maximum, float(values.max()))

    def result(self) -> dict:
        if not self.count:
            raise ValueError("No observations.")
        return {
            "count": self.count,
            "min": self.minimum,
            "max": self.maximum,
            "mean": self.mean,
            "std": float(np.sqrt(self.m2 / self.count)),
        }


AGGREGATE_NAMES = (
    "multiplicity",
    "scalar_pt",
    "max_pt",
    "pt_balance",
    "weighted_eta_mean",
    "weighted_eta_std",
    "pt_concentration",
    "massless_event_mass",
)
LOG_AGGREGATES = (0, 1, 2, 7)


def aggregate_observations(particles: NDArray) -> NDArray:
    """Compute eight physical summaries for EDA, excluding zero padding.

    Mass assumes massless constituents. These observations are not persisted
    as a production feature matrix; Task 0005 will implement that contract.
    """
    pt, eta, phi = np.moveaxis(particles, -1, 0)
    total = pt.sum(axis=1)
    if (total <= 0).any():
        raise ValueError("Aggregates require nonempty, positive-pT events.")
    px = (pt * np.cos(phi)).sum(axis=1)
    py = (pt * np.sin(phi)).sum(axis=1)
    pz = (pt * np.sinh(eta)).sum(axis=1)
    energy = (pt * np.cosh(eta)).sum(axis=1)
    center = (pt * eta).sum(axis=1) / total
    spread = np.sqrt((pt * (eta - center[:, None]) ** 2).sum(axis=1) / total)
    mass2 = energy**2 - px**2 - py**2 - pz**2
    tolerance = 64 * np.finfo(np.float64).eps * (energy**2 + pz**2 + px**2 + py**2)
    if (mass2 < -tolerance).any():
        raise ValueError("Materially negative mass squared.")
    return np.column_stack(
        [
            (pt > 0).sum(axis=1),
            total,
            pt.max(axis=1),
            np.hypot(px, py) / total,
            center,
            spread,
            (pt**2).sum(axis=1) / total**2,
            np.sqrt(np.maximum(mass2, 0)),
        ]
    )


def precision_errors(values: NDArray) -> dict:
    """Measure FP32 round-trip errors; relative errors exclude exact zeros."""
    restored = values.astype(np.float32).astype(np.float64)
    error = np.abs(restored - values)
    relative = np.divide(
        error, np.abs(values), out=np.zeros_like(error), where=values != 0
    )
    return {
        "max_absolute": error.max(axis=0).tolist(),
        "max_relative_nonzero": relative.max(axis=0).tolist(),
        "zeros_preserved": bool(np.all(restored[values == 0] == 0)),
    }
