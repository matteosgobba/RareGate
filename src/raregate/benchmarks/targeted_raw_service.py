"""Task0047 closed owned actual-row packing and unchanged public score/strict decisions."""

import numpy as np

from raregate.benchmarks import core
from raregate.benchmarks import targeted_raw_planning as plan
from raregate.data.inspection import AGGREGATE_NAMES
from raregate.simulation.protocol import require


def pack(window, b, m, side):
    actual, _ = plan.mapping(b, m, side)
    require(
        isinstance(window, np.ndarray)
        and window.shape == (actual, 8)
        and window.dtype == np.dtype("<f4")
        and window.flags.c_contiguous
        and np.isfinite(window).all(),
        "Exact finite C-order FP32 actual rows",
    )
    owned = np.empty((actual, 8), dtype=np.float32, order="C")
    owned[:] = window
    return owned


def service(model, thresholds, channels, window, b, m, side):
    actual, _ = plan.mapping(b, m, side)
    require(
        isinstance(thresholds, np.ndarray)
        and thresholds.shape == (4,)
        and thresholds.dtype == np.dtype("<f8")
        and np.isfinite(thresholds).all(),
        "Original finite FP64 threshold set",
    )
    require(
        tuple(channels) == tuple(AGGREGATE_NAMES), "Original ordered eight channels"
    )
    owned = pack(window, b, m, side)
    scores = model.score(owned, feature_names=channels)
    require(
        isinstance(scores, np.ndarray)
        and scores.shape == (actual,)
        and scores.dtype == np.dtype("<f8")
        and np.isfinite(scores).all()
        and np.all(scores >= 0),
        "Original public FP64 scores for all actual rows",
    )
    decisions = core.decisions(scores, thresholds)
    return scores.copy(), decisions.copy()
