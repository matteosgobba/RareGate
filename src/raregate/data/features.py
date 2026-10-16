"""Frozen LHCO physical canonicalization and model views, without framework I/O."""

from dataclasses import dataclass

import numpy as np

from raregate.data.inspection import (
    AGGREGATE_NAMES,
    LOG_AGGREGATES,
    aggregate_observations,
    inspect_particles,
)

PHYSICAL_CHANNELS = ("pt_GeV", "eta", "phi_rad")
OBJECT_CHANNELS = ("standardized_log1p_pt", "standardized_eta", "sin_phi", "cos_phi")


@dataclass(frozen=True)
class Parameters:
    """Read fitted parameters; there is deliberately no fitting method."""

    pt_mean: float
    pt_std: float
    eta_mean: float
    eta_std: float
    aggregate_mean: np.ndarray
    aggregate_std: np.ndarray
    nmax: int
    pt_reference: float = 1.0

    @classmethod
    def from_config(cls, config: dict) -> "Parameters":
        spec = config["preprocessing"]
        physical, objects, aggregates = (
            spec["canonical"],
            spec["object_view"],
            spec["aggregates"],
        )
        if (
            config["schema_version"] != 1
            or tuple(physical["channels"]) != PHYSICAL_CHANNELS
            or physical["dtype"] != "float32"
            or not physical["retain_all_particles"]
            or tuple(objects["channels"]) != OBJECT_CHANNELS
            or objects["dtype"] != "float32"
            or objects["nmax"] != 384
            or objects["padding"] != 0
            or objects["pt_reference_GeV"] != 1
            or tuple(aggregates["channels"]) != AGGREGATE_NAMES
            or tuple(aggregates["log1p_indices"]) != LOG_AGGREGATES
            or aggregates["version"] != 1
        ):
            raise ValueError("Configuration does not match preprocessing contract v1.")
        mean = np.asarray(aggregates["mean"], dtype=np.float64)
        std = np.asarray(aggregates["std"], dtype=np.float64)
        scalars = np.array(
            [objects[k] for k in ("pt_mean", "pt_std", "eta_mean", "eta_std")]
        )
        if (
            mean.shape != (8,)
            or std.shape != (8,)
            or not np.isfinite(mean).all()
            or not np.isfinite(std).all()
            or not np.isfinite(scalars).all()
            or (std <= 0).any()
            or objects["pt_std"] <= 0
            or objects["eta_std"] <= 0
        ):
            raise ValueError(
                "Frozen scalers must be finite, with positive standard deviations."
            )
        mean.setflags(write=False)
        std.setflags(write=False)
        return cls(*scalars.tolist(), mean, std, objects["nmax"])


def wrap_phi(phi: np.ndarray) -> np.ndarray:
    """Preserve in-range float64 angles; wrap outside [-pi,pi), normalize zero."""
    values = np.array(phi, dtype=np.float64, copy=True)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite phi.")
    outside = (values < -np.pi) | (values >= np.pi)
    values[outside] = (values[outside] + np.pi) % (2 * np.pi) - np.pi
    values[values == 0] = 0.0
    return values


@dataclass
class CanonicalChunk:
    """All sorted particles for a bounded raw batch; padding stays temporary."""

    padded: np.ndarray
    original_slots: np.ndarray
    counts: np.ndarray
    source_order: np.ndarray
    wrapped_float64: np.ndarray

    @property
    def valid(self) -> np.ndarray:
        return np.arange(self.padded.shape[1])[None, :] < self.counts[:, None]


def canonicalize(particles: np.ndarray) -> CanonicalChunk:
    """Validate, sort source float64 before rounding, and preserve every particle."""
    values = np.array(particles, dtype=np.float64, copy=True)
    flags = inspect_particles(values, np.zeros(len(values)))
    if not flags["eligible"].all():
        bad = [
            name
            for name, rows in flags.items()
            if name not in ("eligible", "multiplicity") and rows.any()
        ]
        raise ValueError(f"Invalid raw particles: {', '.join(bad)}")
    if values.shape[1] > 700:
        raise ValueError("Source exceeds 700 object slots.")
    values[values == 0] = 0.0
    values[:, :, 2] = wrap_phi(values[:, :, 2])
    if np.abs(values).max() > np.finfo(np.float32).max:
        raise ValueError("Physical value cannot be stored as finite FP32.")
    slots = np.broadcast_to(
        np.arange(values.shape[1], dtype=np.uint16), values.shape[:2]
    )
    key = np.where(values[:, :, 0] > 0, -values[:, :, 0], np.inf)
    order = np.lexsort((slots, values[:, :, 2], values[:, :, 1], key), axis=1)
    ordered = np.take_along_axis(values, order[:, :, None], axis=1)
    return CanonicalChunk(
        ordered.astype("<f4"),
        np.take_along_axis(slots, order, axis=1),
        flags["multiplicity"],
        order,
        ordered,
    )


def physical_aggregates(padded: np.ndarray) -> np.ndarray:
    """Contract's eight full-event quantities, accumulating in float64."""
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            features = aggregate_observations(padded.astype(np.float64))
    except FloatingPointError as exc:
        raise ValueError("Aggregate arithmetic exceeded finite float64 range.") from exc
    if not np.isfinite(features).all():
        raise ValueError("Nonfinite full-event aggregate.")
    return features


def standardized_aggregates(physical: np.ndarray, parameters: Parameters) -> np.ndarray:
    """Apply frozen log channels and event scalers, with one final FP32 cast."""
    values = np.array(physical, dtype=np.float64, copy=True)
    if values.ndim != 2 or values.shape[1] != 8 or not np.isfinite(values).all():
        raise ValueError("Expected finite [events,8] physical aggregates.")
    if (values[:, LOG_AGGREGATES] < 0).any():
        raise ValueError("Log aggregate channels must be nonnegative.")
    values[:, LOG_AGGREGATES] = np.log1p(values[:, LOG_AGGREGATES])
    return ((values - parameters.aggregate_mean) / parameters.aggregate_std).astype(
        "<f4"
    )


def particle_features(particles: np.ndarray, parameters: Parameters) -> np.ndarray:
    """Transform real particles; pT=0 is mathematically valid, never a mask rule."""
    values = np.asarray(particles, dtype=np.float64)
    if (
        values.ndim != 2
        or values.shape[1] != 3
        or not np.isfinite(values).all()
        or (values[:, 0] < 0).any()
    ):
        raise ValueError("Expected finite [particles,3] with nonnegative pT.")
    phi = wrap_phi(values[:, 2])
    return np.column_stack(
        [
            (np.log1p(values[:, 0] / parameters.pt_reference) - parameters.pt_mean)
            / parameters.pt_std,
            (values[:, 1] - parameters.eta_mean) / parameters.eta_std,
            np.sin(phi),
            np.cos(phi),
        ]
    ).astype("<f4")


@dataclass
class ModelView:
    """Four feature channels and separate mask/truncation metadata."""

    features: np.ndarray
    mask: np.ndarray
    n_original: np.ndarray
    n_retained: np.ndarray
    retained_pt_fraction: np.ndarray


def model_view(
    particles: np.ndarray,
    offsets: np.ndarray,
    parameters: Parameters,
    *,
    nmax: int | None = None,
) -> ModelView:
    """Derive a bounded batch from canonical order; never re-sort rounded ties."""
    nmax = parameters.nmax if nmax is None else nmax
    if (
        not isinstance(nmax, (int, np.integer))
        or isinstance(nmax, bool)
        or not 1 <= nmax <= 700
    ):
        raise ValueError("Nmax must be an integer in [1,700].")
    if (
        offsets.ndim != 1
        or offsets.dtype.kind not in "iu"
        or len(offsets) < 1
        or offsets[0] != 0
        or offsets[-1] != len(particles)
        or (np.diff(offsets) <= 0).any()
    ):
        raise ValueError("Invalid nonempty-event ragged offsets.")
    counts = np.diff(offsets)
    kept = np.minimum(counts, nmax)
    mask = np.arange(nmax)[None, :] < kept[:, None]
    features = np.zeros((len(counts), nmax, 4), dtype="<f4")
    if not len(counts):
        return ModelView(features, mask, counts, kept, np.empty(0, dtype=np.float64))
    positions = offsets[:-1, None] + np.arange(nmax)[None, :]
    selected = positions[mask]
    features[mask] = particle_features(particles[selected], parameters)
    total = np.add.reduceat(particles[:, 0].astype(np.float64), offsets[:-1])
    retained = np.add.reduceat(
        particles[selected, 0].astype(np.float64), np.r_[0, np.cumsum(kept)[:-1]]
    )
    return ModelView(features, mask, counts, kept, retained / total)


def precision_regression(raw: np.ndarray, chunk: CanonicalChunk) -> dict:
    """Structural precision diagnostic, with no fitting or distribution tuning."""
    from raregate.data.inspection import precision_errors

    physical = raw[raw[:, :, 0] > 0]
    raw_errors = precision_errors(physical)
    valid = chunk.valid
    rounded = chunk.padded.astype(np.float64)
    wrapped_error = np.abs(rounded[valid] - chunk.wrapped_float64[valid]).max(axis=0)
    # A diagnostic only: model views preserve SOURCE order even if rounding
    # would create ties and change the outcome of a new sort.
    slots = chunk.original_slots
    key = np.where(valid, -rounded[:, :, 0], np.inf)
    rounded_order = np.lexsort(
        (slots, wrap_phi(rounded[:, :, 2]), rounded[:, :, 1], key), axis=1
    )
    changed = np.any(rounded_order != np.arange(rounded.shape[1])[None, :], axis=1)
    return {
        "raw_max_absolute": raw_errors["max_absolute"],
        "raw_max_relative_nonzero": raw_errors["max_relative_nonzero"],
        "wrapped_max_absolute": wrapped_error.tolist(),
        "zeros_preserved": bool(np.all(chunk.padded[~valid] == 0)),
        "raw_phi_requiring_wrap": int(
            ((physical[:, 2] < -np.pi) | (physical[:, 2] >= np.pi)).sum()
        ),
        "resorting_after_cast_changes_events": int(changed.sum()),
        "wrapped_phi_outside_math_interval_after_cast": int(
            ((rounded[valid, 2] < -np.pi) | (rounded[valid, 2] >= np.pi)).sum()
        ),
    }
