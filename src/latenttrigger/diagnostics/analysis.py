"""Fixed descriptive arithmetic; NumPy ranks only, no inference/significance API."""

import csv
import math

import numpy as np

from latenttrigger.diagnostics import protocol as p
from latenttrigger.diagnostics.reader import NarrowReader

TABLES = (
    "feature-marginals.csv",
    "score-marginals.csv",
    "feature-score-associations.csv",
    "tail-counts.csv",
    "tail-feature-profiles.csv",
)


def describe(values):
    p.require(
        values.ndim == 1 and len(values) > 0 and np.isfinite(values).all(),
        "Finite nonempty description",
    )
    x = values.astype(np.float64)
    q = np.quantile(x, p.QUANTILES, method="linear")
    return dict(
        count=len(x),
        mean=float(np.mean(x, dtype=np.float64)),
        std=float(np.std(x, ddof=0, dtype=np.float64)),
        min=float(np.min(x)),
        max=float(np.max(x)),
        **{
            f"q{prob:g}": float(value)
            for prob, value in zip(p.QUANTILES, q, strict=True)
        },
    )


def average_ranks(values):
    p.require(
        values.ndim == 1 and len(values) > 0 and np.isfinite(values).all(),
        "Finite ranks",
    )
    order = np.argsort(values, kind="stable")
    x = values[order]
    starts = np.r_[0, np.flatnonzero(x[1:] != x[:-1]) + 1]
    stops = np.r_[starts[1:], len(x)]
    ranked = np.empty(len(x), dtype=np.float64)
    ranked[order] = np.repeat((starts + stops - 1) / 2 + 1, stops - starts)
    return ranked


def rank_coefficient(feature_ranks, score_ranks):
    p.require(
        feature_ranks.shape == score_ranks.shape
        and np.isfinite(feature_ranks).all()
        and np.isfinite(score_ranks).all(),
        "Finite matching ranks",
    )
    if len(feature_ranks) < 2:
        return None, "fewer_than_two_events"
    x = feature_ranks - np.mean(feature_ranks)
    y = score_ranks - np.mean(score_ranks)
    xx, yy = float(np.sum(x * x)), float(np.sum(y * y))
    if xx == 0 or yy == 0:
        return (
            None,
            "constant_feature_and_score"
            if xx == yy == 0
            else "constant_feature"
            if xx == 0
            else "constant_score",
        )
    rho = float(np.sum(x * y) / math.sqrt(xx * yy))
    return (
        (float(np.clip(rho, -1, 1)), None)
        if math.isfinite(rho)
        else (None, "undefined_rank_correlation")
    )


def tail_profile(x, scores, threshold):
    selected = scores > threshold
    count = int(np.count_nonzero(selected))
    if count < 20:
        return count, [
            dict(
                mean=None,
                median=None,
                p25=None,
                p75=None,
                suppression_reason="small_tail_descriptive_summary_suppressed",
            )
            for _ in range(8)
        ]
    # Only in-memory reused features/scores. No additional population access.
    tail = x[selected].astype(np.float64)
    q = np.quantile(tail, [0.25, 0.5, 0.75], axis=0, method="linear")
    means = np.mean(tail, axis=0, dtype=np.float64)
    return count, [
        dict(
            mean=float(means[i]),
            median=float(q[1, i]),
            p25=float(q[0, i]),
            p75=float(q[2, i]),
            suppression_reason=None,
        )
        for i in range(8)
    ]


def write_table(path, rows):
    p.require(rows and len(rows) < 1000, "Aggregate coverage")
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    p.require(path.stat().st_size <= 2 * 2**20, "Aggregate table bound")


def check_historical_summary(candidate, stats, historical):
    mapping = {
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
    }
    for old, new in mapping.items():
        p.require(
            old in historical
            and math.isclose(stats[new], historical[old], rel_tol=1e-12, abs_tol=1e-14),
            "Historical score summary mismatch " + candidate + "/" + old,
        )


def analyze(root, plan, directory, ledger, guard):
    tables = {name: [] for name in TABLES}
    reader = NarrowReader(root, plan, ledger, guard.check)
    try:
        alignment = reader.memberships()
        for population in p.POPULATIONS:
            guard.boundary("features/" + population)
            x = reader.feature_population(population)
            ranks = []
            for i, feature in enumerate(p.FEATURES):
                guard.check()
                base = dict(
                    population=population,
                    feature=feature,
                    standardized_input=True,
                    log1p_before_standardization=i in plan["log1p_indices"],
                )
                tables[TABLES[0]].append(dict(**base, **describe(x[:, i])))
                ranks.append(average_ranks(x[:, i]))
            for candidate in p.CANDIDATES:
                guard.boundary("scores/" + candidate + "/" + population)
                scores = reader.scores(candidate, population)
                stats = describe(scores)
                if population == "background":
                    check_historical_summary(
                        candidate, stats, plan["historical_score_summaries"][candidate]
                    )
                tables[TABLES[1]].append(
                    dict(
                        candidate=candidate,
                        population=population,
                        score="accepted_eight_channel_SSE_FP64",
                        **stats,
                    )
                )
                score_ranks = average_ranks(scores)
                for feature, feature_ranks in zip(p.FEATURES, ranks, strict=True):
                    guard.check()
                    rho, reason = rank_coefficient(feature_ranks, score_ranks)
                    tables[TABLES[2]].append(
                        dict(
                            candidate=candidate,
                            population=population,
                            feature=feature,
                            count=len(scores),
                            spearman_rho=rho,
                            undefined_reason=reason,
                        )
                    )
                for point in plan["thresholds"][candidate]:
                    guard.check()
                    count, profiles = tail_profile(x, scores, point["threshold"])
                    target = point["target_fpr"]
                    p.require(
                        count
                        == plan["expected_tail_counts"][
                            f"{candidate}/{population}/{target}"
                        ],
                        "Task0032 exact accepted tail count mismatch",
                    )
                    base = dict(
                        candidate=candidate,
                        population=population,
                        **point,
                        denominator=len(scores),
                        accepted_count=count,
                        accepted_fraction=count / len(scores),
                        decision="strict_score_gt_threshold",
                    )
                    tables[TABLES[3]].append(base)
                    for feature, profile in zip(p.FEATURES, profiles, strict=True):
                        tables[TABLES[4]].append(
                            dict(
                                **base,
                                feature=feature,
                                standardized_input=True,
                                **profile,
                            )
                        )
                del scores, score_ranks
            del x, ranks
        p.require(
            [len(tables[n]) for n in TABLES] == [24, 6, 48, 24, 192],
            "Complete preregistered coverage",
        )
        for name, rows in tables.items():
            guard.check()
            write_table(p.checked_output(directory, name), rows)
        p.durable_json(
            directory / "analysis-summary.json",
            dict(
                status="descriptive_body_complete",
                coverage={k: len(v) for k, v in tables.items()},
                alignment=alignment,
                three_prong_alignment="accepted complete source order and prepared scientific identity",
                score_summary_crosschecks="two accepted background summaries: count/mean/std/min/max/median/p90/p95/p99/p99.9; no accepted signal marginal summaries available",
                suppressed_feature_rows=sum(
                    bool(r["suppression_reason"]) for r in tables[TABLES[4]]
                ),
                ranks_reused="24 feature rank arrays; each reused for both candidates",
                repeated_in_memory_calculations="marginals/ranks/correlation/four tails reuse owned arrays",
            ),
            exclusive=True,
        )
    finally:
        reader.close()
