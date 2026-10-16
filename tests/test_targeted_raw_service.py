"""Generated original loaders and exact public same-shaped wrapper references."""

import json
import os
from pathlib import Path

import numpy as np
import pytest

from raregate.benchmarks import core
from raregate.benchmarks import prepared_service as historical
from raregate.benchmarks import targeted_raw_planning as p
from raregate.benchmarks import targeted_raw_service as s
from raregate.benchmarks.development_decision_synthetic import models
from raregate.data.inspection import AGGREGATE_NAMES


@pytest.fixture(scope="module")
def candidates(tmp_path_factory):
    root = tmp_path_factory.mktemp("task0047-model-fixtures")
    entries = models(root)
    loaded = {e["name"]: core.load_model(root, e) for e in entries}
    counts = {k: dict(calls=0, rows=0) for k in loaded}
    for key, (model, _) in loaded.items():
        original = model.score

        def counted(values, feature_names, original=original, key=key):
            counts[key]["calls"] += 1
            counts[key]["rows"] += len(values)
            return original(values, feature_names=feature_names)

        model.score = counted
    yield loaded
    if os.environ.get("TASK0047_FIXTURE_COUNTER_OUTPUT"):
        Path(os.environ["TASK0047_FIXTURE_COUNTER_OUTPUT"]).write_text(
            json.dumps(
                dict(
                    model_instances=2,
                    threshold_instances=2,
                    public_calls=counts,
                    optimizer_calls=0,
                    calibration_calls=0,
                )
            )
        )


@pytest.mark.parametrize("candidate", p.CANDIDATES)
@pytest.mark.parametrize("b,m", p.CASES)
def test_generated_model_parity_old15_and_independent_new17(
    candidates, candidate, b, m
):
    model, thresholds = candidates[candidate]
    full = np.arange(b * 8, dtype="<f4").reshape(b, 8) / 100
    for side in p.SIDES:
        actual, _ = p.mapping(b, m, side)
        window = full[:actual].copy()
        got = s.service(model, thresholds, AGGREGATE_NAMES, window, b, m, side)
        if (b, m) in p.REFERENCE_CASES:
            service_b = (
                actual if side == "natural_m" and (b, m) in ((32, 8), (128, 32)) else b
            )
            ref = historical.service(
                model, thresholds, AGGREGATE_NAMES, window, service_b, "natural"
            )
        else:
            owned = np.empty((actual, 8), dtype="<f4", order="C")
            owned[:] = window
            score = model.score(owned, feature_names=AGGREGATE_NAMES)
            ref = (score.copy(), np.column_stack([score > t for t in thresholds]))
        assert all(a.tobytes() == r.tobytes() for a, r in zip(got, ref, strict=True))
        assert all(a.flags.owndata for a in got)
        packed = s.pack(window, b, m, side)
        window.fill(-999)
        assert not np.shares_memory(window, packed) and np.all(packed >= 0)


@pytest.mark.parametrize(
    "fault",
    [
        "unsupported",
        "boolB",
        "wrong_side",
        "wrong_shape",
        "dtype",
        "nonfinite",
        "noncontiguous",
        "thresholds",
        "channels",
    ],
)
def test_denied_before_model_effect_and_exact_single_public_call(fault):
    class Model:
        calls = 0

        def score(self, values, feature_names):
            self.calls += 1
            assert values.flags.owndata and values.shape == (3, 8)
            return np.array([1, 2, 3], dtype="<f8")

    model = Model()
    b, m, side = 8, 3, "natural_m"
    x = np.ones((3, 8), dtype="<f4")
    t = np.array([1, 2, 3, 4], dtype="<f8")
    channels = AGGREGATE_NAMES
    if fault == "unsupported":
        b = 32
        m = 9
    if fault == "boolB":
        b = True
    if fault == "wrong_side":
        side = "padded"
    if fault == "wrong_shape":
        x = x[:2]
    if fault == "dtype":
        x = x.astype("<f8")
    if fault == "nonfinite":
        x[0, 0] = np.inf
    if fault == "noncontiguous":
        x = x[:, ::-1]
    if fault == "thresholds":
        t = t[:3]
    if fault == "channels":
        channels = channels[::-1]
    with pytest.raises(ValueError):
        s.service(model, t, channels, x, b, m, side)
    assert model.calls == 0
    scores, masks = s.service(
        model,
        np.array([1, 2, 3, 4], dtype="<f8"),
        AGGREGATE_NAMES,
        np.zeros((3, 8), dtype="<f4"),
        8,
        3,
        "natural_m",
    )
    assert model.calls == 1 and masks[0].tolist() == [False] * 4
