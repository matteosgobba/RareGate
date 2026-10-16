"""Generated provenance/timer/receipt bundles only; no historical numerical reads."""

import csv
import io
import json
from pathlib import Path

from raregate.benchmarks.development_decision_planning import candidates, schedule
from raregate.simulation import joint_protocol as p
from raregate.simulation import joint_source as source


def create(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    files = {}
    d = p.SOURCE_DIRECTORY

    def put(n, v, text=False):
        path = root / n
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(v if text else json.dumps(v, allow_nan=False) + "\n")
        files[n] = p.file_hash(path)

    config = dict(
        task="0043",
        scope="selected_raw_to_decisions",
        kind="one_conditional_selected_development_raw_to_decision_CPU_session_v2",
        payload_scope="approved_background_training_1024prefix_12windows_native_CPU_original_models",
    )
    put("configs/benchmarks/development_raw_decision_v2.json", config)
    put(
        "docs/prompts/0043-development-raw-decision-campaign-v2.md",
        "Generated Task0043-shaped fixture only\n",
        True,
    )
    ident = dict(
        task="0043",
        validation_owner="0043",
        protocol_kind=config["kind"],
        scope=config["scope"],
        payload_scope=config["payload_scope"],
        config_sha256=files["configs/benchmarks/development_raw_decision_v2.json"],
        prompt_sha256=files[
            "docs/prompts/0043-development-raw-decision-campaign-v2.md"
        ],
    )
    plan = dict(
        task="0043",
        identity=ident,
        synthetic_only=False,
        validation_bootstrap=False,
        source_map={},
        dependencies={},
    )
    put(d + "/plan.json", plan)
    workers = []
    allcells = []
    timer = dict(
        implementation="fixture",
        resolution_seconds=1e-9,
        monotonic=True,
        adjustable=False,
        storage="integer_ns",
        recorded_before_timing=True,
    )
    for rep in (1, 2, 3):
        prefix = f"{d}/repetition{rep}/"
        records = []
        now = 1.0
        for ordinal, r in enumerate(
            row for c in candidates(rep) for row in schedule(rep, c)
        ):
            elapsed = (
                150000
                + rep * 1000
                + (2000 if r["candidate"] == p.CANDIDATES[1] else 0)
                + r["call"] * 3000
            ) * r["B"]
            records.append(
                dict(
                    r,
                    ordinal=ordinal,
                    elapsed_ns=elapsed,
                    start_continuous=now,
                    end_continuous=now + elapsed / 1e9,
                    continuous_minus_timer_ns=0.0,
                )
            )
            now += 1
        put(
            prefix + "timings.jsonl",
            "".join(json.dumps(r) + "\n" for r in records),
            True,
        )
        put(prefix + "timer.json", timer)
        cells = []
        for c in p.CANDIDATES:
            for b in (1, 8, 32, 128):
                q = [
                    r["elapsed_ns"]
                    for r in records
                    if r["candidate"] == c and r["B"] == b and r["phase"] == "timed"
                ]
                cell = dict(
                    candidate=c,
                    B=b,
                    repetition=rep,
                    scope="selected_raw_to_decisions",
                    strategy="natural",
                    **source.statistics(q),
                    observations_ns=q,
                    window_call_counts=[7, 7, 6],
                    timer=timer,
                )
                cells.append(cell)
                allcells.append(
                    {
                        k: v
                        for k, v in cell.items()
                        if k not in ("observations_ns", "timer")
                    }
                    | dict(actual_batch_rows=b)
                )
        agg = dict(
            task="0043",
            identity=ident,
            cells=cells,
            gates=[
                dict(
                    status="exact_feature_score_decision_bytes_passed",
                    feature_score_decision_mismatches=[0, 0, 0],
                )
                for _ in range(48)
            ],
            exact_feature_score_decision_parity=True,
            chronology=[
                {k: r[k] for k in ("candidate", "B", "phase", "ordinal", "elapsed_ns")}
                for r in records
            ],
        )
        put(prefix + "aggregate.json", agg)
        receipt = dict(
            task="0043",
            identity=ident,
            status="body_complete_awaiting_exit",
            source_map={},
            dependencies={},
            outputs={
                n: files[prefix + n]
                for n in ("aggregate.json", "timer.json", "timings.jsonl")
            },
        )
        put(prefix + "receipt.json", receipt)
        workers.append(
            dict(
                phase=f"repetition{rep}",
                body_sha256=files[prefix + "receipt.json"],
                dispatch=dict(
                    returncode=0,
                    child_reaped=True,
                    parent_confirms_normal_exit=True,
                    within_deadline=True,
                    parent_error=None,
                    overshoot_seconds=0,
                    exit_observed_continuous=2.0,
                    stage_deadline_continuous=3.0,
                ),
                acceptance=dict(
                    task="0043",
                    status="parent_accepted_worker",
                    normal_exit_reaped=True,
                ),
            )
        )
    workers.append(dict(workers[0], phase="reporting"))
    w = dict(
        task="0043",
        identity=ident,
        status=source.SOURCE_STATUS,
        synthetic_only=False,
        validation_bootstrap=False,
        sleep_assertion=dict(released=True),
        overshoot_seconds=0,
        source_map={},
        dependencies={},
        plan_sha256=files[d + "/plan.json"],
        workers=workers,
    )
    put(d + "/workflow.json", w)
    put(
        d + "/parent-acceptance.json",
        dict(
            task="0043",
            identity=ident,
            status=source.SOURCE_STATUS,
            workflow_sha256=files[d + "/workflow.json"],
            plan_sha256=files[d + "/plan.json"],
        ),
    )
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(allcells[0]))
    writer.writeheader()
    for c in allcells:
        writer.writerow(c | dict(window_call_counts="7/7/6"))
    put(source.CELLS, out.getvalue(), True)
    summary = dict(
        task="0043",
        status=source.SOURCE_STATUS,
        scope="selected_raw_to_decisions_CPU_natural_fixed_development_windows",
        one_allowance_consumed=True,
        provenance=dict(
            config_path="configs/benchmarks/development_raw_decision_v2.json",
            prompt_path="docs/prompts/0043-development-raw-decision-campaign-v2.md",
            config_file_sha256=ident["config_sha256"],
            config_canonical_sha256=p.digest(config),
            prompt_sha256=ident["prompt_sha256"],
            operational_directory=d,
            workflow_sha256=files[d + "/workflow.json"],
            parent_acceptance_sha256=files[d + "/parent-acceptance.json"],
            execution_plan_sha256=files[d + "/plan.json"],
        ),
        validation=dict(source_map_canonical_sha256=p.digest({})),
        parity=dict(
            exact_feature_score_mask_bytes=True,
            feature_score_mask_mismatches=[0, 0, 0],
            every_timed_warmup_output_checked=True,
            pre_post_golden_references_exact=True,
        ),
        results=dict(
            cells=24,
            timed_calls=480,
            warmup_calls=72,
            table_sha256=files[source.CELLS],
            pooled=[
                dict(
                    candidate=c,
                    B=b,
                    **source.statistics(
                        [
                            v
                            for rep in (1, 2, 3)
                            for cell in allcells
                            if cell["candidate"] == c
                            and cell["B"] == b
                            and cell["repetition"] == rep
                            for v in [
                                (
                                    150000
                                    + rep * 1000
                                    + (2000 if c == p.CANDIDATES[1] else 0)
                                    + i * 3000
                                )
                                * b
                                for i in range(20)
                            ]
                        ]
                    ),
                )
                for c in p.CANDIDATES
                for b in (1, 8, 32, 128)
            ],
        ),
    )
    put(source.SUMMARY, summary)
    p.durable_json(root / "fixture-manifest.json", files, exclusive=True)
    return files
