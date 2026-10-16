"""Three curated inputs only; no following historical model/array/receipt paths."""

import csv
import hashlib
import io
import json
import math
from decimal import ROUND_CEILING, Decimal

from raregate.simulation import protocol as p


def numeric(value):
    d = Decimal(str(value))
    p.require(d.is_finite() and d >= 0, "Finite nonnegative timing aggregate")
    return d


def same(a, b):
    return math.isclose(
        float(numeric(a)), float(numeric(b)), rel_tol=1e-12, abs_tol=1e-9
    )


def service(value):
    d = numeric(value)
    p.require(d > 0, "Positive service duration")
    result = int(d.to_integral_value(rounding=ROUND_CEILING))
    p.require(result <= 2**63 - 1, "Integer ns overflow")
    return result


def load(root=p.ROOT, *, identities=p.PINS, ledger=None):
    """Exactly one byte read and numerical parse per allowed file; test pins injectable."""
    p.require(set(identities) == set(p.PINS), "Three input allowlist identities")
    buffers = {}
    if ledger is None:
        ledger = []
    for relative, sha in identities.items():
        path = p.nonsymlink(root, relative)
        raw = path.read_bytes()
        p.require(
            hashlib.sha256(raw).hexdigest() == sha, "Altered curated input: " + relative
        )
        buffers[relative] = raw
        ledger.append(
            dict(path=relative, sha256=sha, bytes=len(raw), numerical_loads=1)
        )
    names = list(p.PINS)
    cells = list(csv.DictReader(io.StringIO(buffers[names[0]].decode())))
    accepted = json.loads(buffers[names[1]])
    joined = list(csv.DictReader(io.StringIO(buffers[names[2]].decode())))
    p.require(
        accepted["task"] == "0022"
        and accepted["execution_status"] == "complete_accepted_consumed_no_retry"
        and accepted["comparison_success"] is True
        and accepted["same_scientific_models_scalers_scores_thresholds"] is True,
        "Accepted Task0022 status",
    )
    models = {
        m["name"]: m["model_scientific_sha256"] for m in accepted["frozen_models"]
    }
    p.require(
        len(accepted["frozen_models"]) == len(models) == 2
        and set(models) == set(p.CANDIDATES),
        "Actual candidate identities",
    )
    workers = {
        name: [("PCA" if name == p.CANDIDATES[0] else "AE") + str(i) for i in (1, 2, 3)]
        for name in p.CANDIDATES
    }
    phases = accepted["campaign"]["phases"]
    p.require(
        len(phases) == 7
        and {x["phase"] for x in phases}
        == {"prepare", *(w for names in workers.values() for w in names)},
        "Unique accepted worker phases",
    )
    for phase in phases:
        d = phase["parent_dispatch"]
        p.require(
            phase["status"] == "completed"
            and d["returncode"] == 0
            and d["child_reaped"] is True
            and d["deadline_passed"] is True
            and d["parent_error"] is None,
            "Accepted historical normal exit/reap/deadline",
        )
        p.require(
            accepted["receipt_lineage"]["phase_receipt_sha256"][phase["phase"]]
            == phase["receipt_file_sha256"],
            "Curated receipt lineage",
        )
    p.require(
        accepted["campaign"]["missing_cells"] == 0
        and accepted["campaign"]["counts"]["measured_cells_completed"] == 90,
        "Historical coverage",
    )
    expected = {
        (w, m, b, s)
        for m in p.CANDIDATES
        for w in workers[m]
        for b in p.BATCHES
        for s in ("reconstruction", "score_decision", "adapter_decision")
    }
    keyed = {}
    for row in cells:
        key = (row["worker"], row["model"], int(row["batch"]), row["scope"])
        p.require(
            key not in keyed
            and key in expected
            and row["status"] == "completed"
            and int(row["count"]) == 200,
            "Ambiguous timing coverage/count/scope",
        )
        keyed[key] = row
    p.require(
        set(keyed) == expected and len(cells) == 90, "Complete unique timing cells"
    )
    metadata = {}
    for row in accepted["timing_cells"]:
        key = (row["worker"], row["model"], row["batch"], row["scope"])
        p.require(key not in metadata, "Duplicate summary cell")
        metadata[key] = row
    p.require(set(metadata) == expected, "Summary coverage agreement")
    groups = {}
    for row in joined:
        key = (row["candidate"], int(row["cost_batch"]))
        p.require(
            key not in groups
            and row["cost_scope"] == "adapter_decision_prepared_features"
            and row["cost_task"] == "0022"
            and row["model_scientific_sha256"] == models[row["candidate"]],
            "Ambiguous joined cost/model/scope",
        )
        groups[key] = row
    p.require(
        len(joined) == 10
        and set(groups) == {(m, b) for m in p.CANDIDATES for b in p.BATCHES},
        "Ten joined cost groups",
    )
    result = {}
    for model in p.CANDIDATES:
        for batch in p.BATCHES:
            repetitions = []
            for i, worker in enumerate(workers[model], 1):
                key = (worker, model, batch, "adapter_decision")
                row = keyed[key]
                meta = metadata[key]
                join = groups[(model, batch)]
                for field in (
                    "min_ns",
                    "mean_ns",
                    "max_ns",
                    "p50_ns",
                    "p95_ns",
                    "p99_ns",
                    "population_std_ns",
                ):
                    p.require(
                        same(row[field], meta[field])
                        and same(row[field], join[f"repetition_{i}_{field}"]),
                        "Cross-table worker statistic",
                    )
                ordered = [
                    numeric(row[f])
                    for f in ("min_ns", "p50_ns", "p95_ns", "p99_ns", "max_ns")
                ]
                p.require(
                    ordered == sorted(ordered)
                    and ordered[0] <= numeric(row["mean_ns"]) <= ordered[-1]
                    and join[f"repetition_{i}_worker"] == worker,
                    "Timing order/worker",
                )
                repetitions.append(
                    dict(
                        worker=worker,
                        count=200,
                        **{
                            f: str(numeric(row[f]))
                            for f in ("mean_ns", "p99_ns", "max_ns")
                        },
                    )
                )
            mean = sum(numeric(r["mean_ns"]) * r["count"] for r in repetitions) / sum(
                r["count"] for r in repetitions
            )
            join = groups[(model, batch)]
            p.require(
                int(join["pooled_invocations"]) == 600
                and int(join["invocations_per_worker"]) == 200
                and same(mean, join["pooled_600_invocation_mean_batch_ns"])
                and same(
                    mean / Decimal(batch), join["pooled_mean_amortized_ns_per_event"]
                )
                and same(
                    Decimal(batch) * Decimal(10**9) / mean,
                    join["throughput_from_pooled_mean_events_per_second"],
                ),
                "Task0032 pooled arithmetic",
            )
            result[(model, batch)] = dict(
                candidate=model,
                batch=batch,
                pooled_mean_decimal_ns=str(mean),
                service_ns=service(mean),
                workers=repetitions,
                model_scientific_sha256=models[model],
            )
    p.require(
        service(result[(p.CANDIDATES[1], 128)]["workers"][1]["max_ns"]) == 26248500,
        "Preserve AE2 B12826.2485ms outlier",
    )
    return result, dict(
        source_loads=ledger,
        curated_numerical_loads=3,
        profiles=list(result.values()),
        historical_hardware=accepted["campaign"]["fresh_hardware"],
        historical_runtime=accepted["campaign"]["runtime_versions"],
        historical_effective_threads=accepted["campaign"][
            "effective_threads_by_worker"
        ],
        cost_scope="adapter_decision: prepared development inputs; validation/wrapping/forward/FP64 SSE/four decisions included; excludes physical features/raw I/O/transport/queueing",
        rounding="Decimal CSV worker means weighted by200/600, ROUND_CEILING to integer ns; no favorable repetition removal",
        empirical_distribution_reproduced=False,
    )
