"""Stdlib distributions and paired/pooled summaries, including partial coverage."""

import json
import math
import statistics

from raregate.benchmarks import protocol as p
from raregate.benchmarks import pytorch_onnx_cpu_protocol as q


def aggregate(stages, directory):
    cells = []
    raw = {}
    for stage in stages:
        phase = stage["phase"]
        if phase == "prepare":
            continue
        for cell in stage.get("cells", []):
            cells.append(
                dict(
                    cell,
                    worker=phase,
                    runtime=stage.get("runtime_name"),
                    performance_accepted=stage.get("status") == "completed",
                )
            )
        path = directory / phase / "timings.jsonl"
        if path.exists():
            for line in path.read_text().splitlines():
                row = json.loads(line)
                key = (phase, row["batch"], row["scope"])
                raw.setdefault(key, dict(warmup=[], measurement=[]))[
                    row["phase"]
                ].append(row)
    counts = dict(
        completed_cells=sum(c["status"] == "completed" for c in cells),
        timed_invocations=sum(len(v["measurement"]) for v in raw.values()),
        warmup_invocations=sum(len(v["warmup"]) for v in raw.values()),
        empty_timer_pairs=sum(
            len(s.get("empty_timer_pair_nanoseconds", [])) for s in stages
        ),
    )
    for kind, phase in (("timed", "measurement"), ("warmup", "warmup")):
        counts[kind + "_input_row_presentations"] = sum(
            k[1] * len(v[phase]) for k, v in raw.items()
        )
        counts[kind + "_forward_row_presentations"] = sum(
            k[1] * len(v[phase]) for k, v in raw.items() if k[2] != "score_decision"
        )
    pooled, pairs = [], []
    successful = [s["phase"] for s in stages if s.get("status") == "completed"] == list(
        q.PHASES
    )
    for batch in q.BATCHES:
        for scope in q.SCOPES:
            means = {}
            for runtime in ("PyTorch", "ORT"):
                names = [runtime + str(i) for i in (1, 2, 3)]
                samples = [
                    r["elapsed_ns"]
                    for n in names
                    for r in raw.get((n, batch, scope), {}).get("measurement", [])
                ]
                valid = len(samples) == 600 and all(
                    type(n) is int and n > 0 for n in samples
                )
                if valid:
                    stats = p.distribution(samples, batch)
                    means[runtime] = stats["mean"]
                    medians = [
                        p.quantile(
                            [
                                r["elapsed_ns"]
                                for r in raw[(name, batch, scope)]["measurement"]
                            ],
                            0.5,
                        )
                        for name in names
                    ]
                    pooled.append(
                        dict(
                            runtime=runtime,
                            batch=batch,
                            scope=scope,
                            latency_nanoseconds=stats,
                            median_worker_medians_ns=statistics.median(medians),
                            performance_accepted=successful,
                        )
                    )
            if len(means) == 2:
                ratios = []
                for i in (1, 2, 3):
                    means_pair = [
                        statistics.mean(
                            r["elapsed_ns"]
                            for r in raw[(rt + str(i), batch, scope)]["measurement"]
                        )
                        for rt in ("PyTorch", "ORT")
                    ]
                    ratios.append(means_pair[0] / means_pair[1])
                pairs.append(
                    dict(
                        batch=batch,
                        scope=scope,
                        PyTorch_over_ORT_mean_ratios=ratios,
                        geometric_mean=math.exp(
                            statistics.mean(math.log(r) for r in ratios)
                        ),
                        pooled_mean_ratio=means["PyTorch"] / means["ORT"],
                        performance_accepted=successful,
                    )
                )
    return dict(
        cells=cells,
        counts=counts,
        pooled=pooled,
        paired_ratios=pairs,
        comparison_success=successful
        and counts
        == dict(
            completed_cells=90,
            timed_invocations=18000,
            warmup_invocations=1800,
            empty_timer_pairs=1200,
            timed_input_row_presentations=4294800,
            timed_forward_row_presentations=2863200,
            warmup_input_row_presentations=429480,
            warmup_forward_row_presentations=286320,
        ),
    )
