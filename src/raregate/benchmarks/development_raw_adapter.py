"""Narrow selected-row adapter; only synthetic providers enabled in Task0039."""

import hashlib
from pathlib import Path

import numpy as np

from raregate.benchmarks import development_raw_protocol as p
from raregate.data.features import (
    canonicalize,
    physical_aggregates,
    standardized_aggregates,
)


class Approval:
    def __init__(self, ids, expected_hash, *, role="development_train_background"):
        p.require(
            role == "development_train_background", "No alternative population role"
        )
        p.require(
            ids.shape == (1024,)
            and ids.dtype == np.dtype("<i8")
            and np.all((ids >= 0) & (ids < 1100000))
            and np.all(np.diff(ids) > 0),
            "Exactly1024strict ordered approved IDs",
        )
        self.ids = np.array(ids, dtype="<i8", copy=True)
        p.require(
            hashlib.sha256(self.ids.tobytes()).hexdigest() == expected_hash,
            "Approved source-order identity",
        )
        self.ids.setflags(write=False)

    def positions(self, request):
        p.require(
            isinstance(request, np.ndarray)
            and request.ndim == 1
            and request.dtype == np.dtype("<i8")
            and 1 <= len(request) <= 128
            and np.all(np.diff(request) > 0),
            "Checked increasing int64request, max128",
        )
        pos = np.searchsorted(self.ids, request)
        p.require(np.all(pos < len(self.ids)), "Unapproved row")
        p.require(
            np.array_equal(self.ids[pos], request),
            "Unapproved row, no adjacent interval exposure",
        )
        return pos


def synthetic_provider(dataset):
    """A future authorized controller must be implemented separately in Task0040."""
    file = getattr(dataset, "file", None)
    name = getattr(file, "filename", None)
    if name is not None:
        path = Path(name).resolve()
        protected = any(
            path.is_relative_to(p.ROOT / n)
            for n in ("data", "artifacts", "results", "sources")
        )
        p.require(
            not protected or path.is_relative_to(p.ROOT / "data/task0039-validation"),
            "Task0039 operational event reader disabled",
        )


def selected_read(dataset, request, approval):
    approval.positions(request)  # permission before backend call
    synthetic_provider(dataset)
    p.require(
        dataset.ndim == 2
        and dataset.shape[1] == 2101
        and dataset.dtype == np.dtype("<f8"),
        "Fixed raw layout",
    )
    p.require(int(request[-1]) < dataset.shape[0], "Source range")
    selection = (
        slice(int(request[0]), int(request[-1]) + 1)
        if int(request[-1]) - int(request[0]) + 1 == len(request)
        else request.tolist()
    )
    rows = dataset[selection, :]
    p.require(
        isinstance(rows, np.ndarray)
        and rows.shape == (len(request), 2101)
        and rows.dtype == np.dtype("<f8")
        and rows.flags.c_contiguous
        and rows.flags.owndata,
        "Owned exact selected raw matrix",
    )
    p.require(
        np.all(rows[:, 2100] == 0), "Approved development rows must be background"
    )
    return rows


def construct(rows, parameters):
    p.require(
        rows.ndim == 2
        and 1 <= len(rows) <= 128
        and rows.shape[1] == 2101
        and rows.dtype == np.dtype("<f8")
        and np.all(rows[:, 2100] == 0),
        "Bounded FP64 background raw batch",
    )
    chunk = canonicalize(rows[:, :2100].reshape(-1, 700, 3))
    features = standardized_aggregates(physical_aggregates(chunk.padded), parameters)
    p.require(
        features.shape == (len(rows), 8)
        and features.dtype == np.dtype("<f4")
        and np.isfinite(features).all(),
        "Finite owned frozen features",
    )
    return features


def joint(dataset, request, approval, parameters):
    return construct(selected_read(dataset, request, approval), parameters)


def parity(features, golden, request, approval):
    positions = approval.positions(request)
    p.require(
        golden.shape == (1024, 8)
        and golden.dtype == np.dtype("<f4")
        and features.shape == (len(request), 8)
        and features.dtype == np.dtype("<f4")
        and features.tobytes() == golden[positions].tobytes(),
        "Exact approved-position feature parity; no empirical tolerance",
    )
