"""Synthetic-only files; no operational identity or sample is numerically loaded."""

import copy

import numpy as np

from latenttrigger.diagnostics import protocol as p
from latenttrigger.diagnostics.analysis import describe


def fixture_plan(root):
    original, prepared = "data/original", "data/prepared"
    (root / original).mkdir(parents=True)
    (root / prepared).mkdir(parents=True)
    codes = np.array([1] * 25 + [4] * 30 + [5] * 25, dtype=np.uint8)
    ids = np.arange(80, dtype=np.int64)
    labels = (codes == 5).astype(np.uint8)
    features = np.arange(80 * 8, dtype=np.float32).reshape(80, 8) / 100
    features[:25] = np.nan  # Must never be selected or numerically analyzed.
    three = np.arange(25 * 8, dtype=np.float32).reshape(25, 8) / 80
    arrays = {}

    def save(path, value):
        np.save(root / path, value, allow_pickle=False)
        arrays[path] = dict(
            bytes=(root / path).stat().st_size,
            sha256=p.file_hash(root / path),
            dtype=value.dtype.str,
            shape=list(value.shape),
        )

    for name, value in [
        ("event_features", features),
        ("split_codes", codes),
        ("event_ids", ids),
        ("labels", labels),
    ]:
        save(original + "/" + name + ".npy", value)
    save(prepared + "/event_features.npy", three)
    counts = dict(background=30, two_prong=25, three_prong=25)
    ledgers, scores, summaries, thresholds, expected = {}, {}, {}, {}, {}
    for candidate in p.CANDIDATES:
        rows = []
        thresholds[candidate] = [
            dict(target_fpr=t, threshold=v)
            for t, v in zip([0.1, 0.05, 0.01, 0.001], [0.2, 0.4, 0.7, 1.1], strict=True)
        ]
        for pop, code in [("background", 4), ("two_prong", 5)]:
            selected = ids[codes == code]
            n = len(selected)
            rows.append(
                dict(
                    split="test_background" if pop == "background" else "test_signal",
                    allow_test=True,
                    include_labels=True,
                    dev_only=False,
                    expected_count=n,
                    confirmed_events_read=n,
                    confirmed_events_scored=n,
                    status="complete",
                    inflight=None,
                    completed_score_batches=1,
                    batches=[
                        dict(
                            index=0,
                            rows_read=n,
                            rows_scored=n,
                            first_source_id=int(selected[0]),
                            last_source_id=int(selected[-1]),
                        )
                    ],
                )
            )
        ledgers[candidate] = copy.deepcopy(rows)
        for pop in p.POPULATIONS:
            n = counts[pop]
            values = np.linspace(0.05, 1.0, n, dtype=np.float64)
            if candidate == "AE":
                values = values[::-1].copy()
            folder = root / "results" / candidate
            folder.mkdir(parents=True, exist_ok=True)
            path = f"results/{candidate}/{pop}-scores.npy"
            save(path, values)
            scores[candidate + "/" + pop] = path
            for point in thresholds[candidate]:
                expected[f"{candidate}/{pop}/{point['target_fpr']}"] = int(
                    np.count_nonzero(values > point["threshold"])
                )
            if pop == "background":
                stats = describe(values)
                summaries[candidate] = {
                    old: stats[new]
                    for old, new in {
                        "count": "count",
                        "mean": "mean",
                        "std": "std",
                        "min": "min",
                        "max": "max",
                        "median": "q0.5",
                        "p90": "q0.9",
                        "p95": "q0.95",
                        "p99": "q0.99",
                        "p99_9": "q0.999",
                    }.items()
                }
    plan = dict(
        schema=1,
        exploratory=True,
        arrays=arrays,
        metadata={},
        original=original,
        prepared=prepared,
        counts=counts,
        original_rows=80,
        role_counts=dict(
            train_background=25,
            validation_selection_background=0,
            validation_calibration_background=0,
            test_background=30,
            test_signal=25,
        ),
        ledgers=ledgers,
        scores=scores,
        thresholds=thresholds,
        expected_tail_counts=expected,
        historical_score_summaries=summaries,
        features=p.FEATURES,
        log1p_indices=[0, 1, 2, 7],
    )
    p.durable_json(root / "fixture-plan.json", plan, exclusive=True)
    return plan
