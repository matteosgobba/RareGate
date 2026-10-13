"""Owned packing/public adapter/real-row retention, with no model loading."""

import numpy as np

from latenttrigger.benchmarks import core
from latenttrigger.benchmarks.prepared_service_protocol import CASES, require


def starts(m):
    require(type(m) is int and 1 <= m <= 1024, "Actual row count")
    return tuple(dict.fromkeys((0, (1024 - m) // 2, 1024 - m)))


def cases(repetition):
    require(type(repetition) is int and repetition in (1, 2, 3), "Fixed repetition")
    return CASES if repetition != 2 else tuple(reversed(CASES))


def schedule(b, m, count):
    require(
        (b, m) in CASES and type(count) is int and count > 0, "Fixed shape/pair count"
    )
    windows = starts(m)
    for pair in range(count):
        order = ("natural", "padded") if pair % 2 == 0 else ("padded", "natural")
        yield pair, windows[pair % len(windows)], order


def pack(window, b, strategy):
    require(
        strategy in ("natural", "padded")
        and (b, len(window)) in CASES
        and window.shape == (len(window), 8)
        and window.dtype == np.float32
        and window.flags.c_contiguous,
        "FP32 contiguous fixed service window",
    )
    n = len(window) if strategy == "natural" else b
    owned = np.empty((n, 8), dtype=np.float32, order="C")
    owned[: len(window)] = window
    if n > len(window):
        owned[len(window) :] = np.float32(0)
    return owned


def service(model, thresholds, channels, window, b, strategy):
    owned = pack(window, b, strategy)
    scores = model.score(owned, feature_names=channels)
    decisions = core.decisions(scores, thresholds)
    return scores[: len(window)].copy(), decisions[: len(window)].copy()


def distribution(values):
    x = np.asarray(values, dtype=np.float64)
    require(
        x.ndim == 1 and len(x) > 0 and np.isfinite(x).all(),
        "Complete finite observations",
    )
    return dict(
        count=len(x),
        min_ns=float(x.min()),
        max_ns=float(x.max()),
        mean_ns=float(x.mean()),
        population_std_ns=float(x.std(ddof=0)),
        **{
            f"p{p}_ns": float(np.quantile(x, p / 100, method="linear"))
            for p in (50, 95, 99)
        },
    )
