"""One fresh repetition, or a source-free runtime/thread probe."""

import csv
import json
import os
import sys
import time

from raregate.benchmarks import prepared_service_protocol as p
from raregate.benchmarks import prepared_service_runtime as rt


def synthetic_models():
    import numpy as np
    import torch

    from raregate.benchmarks import core

    torch.manual_seed(3800)
    ae = core.CompactAutoencoder().eval()
    pca = core.PCAReconstruction(
        np.zeros(8), np.eye(8), np.ones(8), np.ones(8) / 8, 6, 0.7, 1024
    )
    # Generated owned values only; no fit, artifact, or population reader.
    values = np.random.default_rng(3800).normal(0, 0.5, (1024, 8)).astype(np.float32)
    thresholds = np.array([0.2, 1.0, 4.0, 16.0], np.float64)
    return values, {"pca-v1": pca, "compact-autoencoder-v2": ae}, thresholds


def repeat(directory, grant, spec, guard, clock, body):
    import numpy as np

    from raregate.benchmarks import core
    from raregate.benchmarks import prepared_service as s
    from raregate.benchmarks import prepared_service_numerics as n

    audit = dict(
        prepared_array_load_attempts=0,
        prepared_array_loads=0,
        prepared_rows_loaded=0,
        frozen_model_load_attempts=0,
        frozen_model_instantiations=0,
        timed_started=0,
        timed_completed=0,
        warmup_started=0,
        warmup_completed=0,
        inflight=None,
        service_actual_rows=0,
        service_padding_rows=0,
        service_canonical_adapter_calls=0,
    )
    body["access"] = audit

    def persist():
        p.durable_json(directory / "access.json", audit)

    synthetic = grant["synthetic_only"]
    if synthetic:
        values, models, toy_thresholds = synthetic_models()
        audit["synthetic_models"] = 2
    else:
        p.custody()
        values = n.load_prepared(spec, audit, persist)
    rep = grant["repetition"]
    order = list(spec["models"])
    if rep == 2:
        order.reverse()
    cells = []
    paired = []
    chronology = []
    gates = []
    empty = []
    for _ in range(200):
        start = time.perf_counter_ns()
        empty.append(time.perf_counter_ns() - start)
    body["empty_timer_ns"] = empty
    with (directory / "timings.jsonl").open("x") as raw:
        sequence = 0
        for entry in order:
            guard.boundary("model/" + entry["name"])
            if synthetic:
                model = models[entry["name"]]
                thresholds = toy_thresholds.copy()
            else:
                audit["frozen_model_load_attempts"] += 1
                persist()
                model, thresholds = core.load_model(p.ROOT, entry)
                audit["frozen_model_instantiations"] += 1
                persist()
            pre = n.verify(
                model,
                values,
                thresholds,
                spec["input"]["channels"],
                audit,
                poll=guard.check,
                persist=persist,
            )
            persist()
            for b, m in s.cases(rep):
                samples = {k: [] for k in ("natural", "padded")}
                differences = []
                for phase, count in (
                    ("warmup", 2 if synthetic else 10),
                    ("timed", 2 if synthetic else 50),
                ):
                    for pair, start, strategies in s.schedule(b, m, count):
                        durations = {}
                        for position, strategy in enumerate(strategies):
                            guard.check()
                            core.effective_threads()
                            shape = m if strategy == "natural" else b
                            row = dict(
                                candidate=entry["name"],
                                repetition=rep,
                                B=b,
                                m=m,
                                strategy=strategy,
                                phase=phase,
                                pair=pair,
                                pair_position=position,
                                window_start=start,
                                sequence=sequence,
                                continuous_before_ns=clock.ns(),
                            )
                            audit[phase + "_started"] += 1
                            audit["inflight"] = row.copy()
                            persist()
                            # View and proof instrumentation are outside the timer.
                            window = values[start : start + m]
                            tick = time.perf_counter_ns()
                            scores, mask = s.service(
                                model,
                                thresholds,
                                spec["input"]["channels"],
                                window,
                                b,
                                strategy,
                            )
                            elapsed = time.perf_counter_ns() - tick
                            row.update(
                                duration_ns=elapsed,
                                continuous_after_ns=clock.ns(),
                                executed_rows=shape,
                                actual_rows=m,
                                padding_rows=shape - m,
                            )
                            p.require(
                                scores.shape == (m,) and mask.shape == (m, 4),
                                "Retained real rows only",
                            )
                            audit[phase + "_completed"] += 1
                            audit["inflight"] = None
                            audit["service_canonical_adapter_calls"] += 1
                            audit["service_actual_rows"] += m
                            audit["service_padding_rows"] += shape - m
                            raw.write(json.dumps(row, separators=(",", ":")) + "\n")
                            raw.flush()
                            os.fsync(raw.fileno())
                            persist()
                            guard.check()
                            sequence += 1
                            if phase == "timed":
                                samples[strategy].append(elapsed)
                                durations[strategy] = elapsed
                                chronology.append(
                                    {
                                        k: row[k]
                                        for k in (
                                            "candidate",
                                            "repetition",
                                            "B",
                                            "m",
                                            "strategy",
                                            "sequence",
                                            "duration_ns",
                                            "continuous_before_ns",
                                            "continuous_after_ns",
                                        )
                                    }
                                )
                        if phase == "timed":
                            differences.append(
                                durations["natural"] - durations["padded"]
                            )
                for strategy, observations in samples.items():
                    shape = m if strategy == "natural" else b
                    cells.append(
                        dict(
                            candidate=entry["name"],
                            repetition=rep,
                            B=b,
                            m=m,
                            strategy=strategy,
                            candidate_position=order.index(entry),
                            case_order="descending" if rep == 2 else "ascending",
                            executed_shape_rows=shape,
                            padding_rows=shape - m,
                            slot_utilization=m / shape,
                            useful_events_per_second=m
                            * 1e9
                            / float(np.mean(observations)),
                            mean_ns_per_actual_event=float(np.mean(observations)) / m,
                            **s.distribution(observations),
                        )
                    )
                paired.append(
                    dict(
                        candidate=entry["name"],
                        repetition=rep,
                        B=b,
                        m=m,
                        contrast="natural_minus_padded_ns",
                        **s.distribution(differences),
                    )
                )
            post = n.verify(
                model,
                values,
                thresholds,
                spec["input"]["channels"],
                audit,
                poll=guard.check,
                persist=persist,
            )
            p.require(pre == post, "Byte-identical canonical/reference/proof pre/post")
            gates.append(dict(candidate=entry["name"], before=pre, after=post))
            persist()
    p.require(
        audit["inflight"] is None
        and len(cells) == 68
        and audit["timed_completed"] == (136 if synthetic else 3400)
        and audit["warmup_completed"] == (136 if synthetic else 680),
        "Complete paired repetition accounting",
    )
    with (directory / "cells.csv").open("x", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(cells[0]))
        writer.writeheader()
        writer.writerows(cells)
    aggregate = dict(
        cells=cells,
        paired=paired,
        chronology=chronology,
        gates=gates,
        access=audit,
        empty_timer_distribution=s.distribution(empty),
        source_map=grant["source_map"],
        synthetic_only=synthetic,
    )
    p.durable_json(directory / "aggregate.json", aggregate, exclusive=True)
    body["numerical_gates"] = gates
    return ["cells.csv", "aggregate.json", "timings.jsonl"]


def worker(directory, token):
    grant = p.read(directory / "grant.json")
    p.require(
        grant["token"] == token
        and grant["parent_pid"] == os.getppid()
        and directory.absolute() == directory.resolve()
        and directory.name == grant["phase"],
        "Parent owned grant",
    )
    base = directory.parent
    p.require(
        (
            grant["synthetic_only"] is True
            and base.is_relative_to(p.ROOT / "data/task0038-validation")
        )
        or (
            grant["synthetic_only"] is False
            and base.parent == p.ROOT / p.OUTPUT
            and len(base.name) == 32
            and all(c in "0123456789abcdef" for c in base.name)
        ),
        "Fixed owned worker namespace",
    )
    if grant["phase"] != "probe":
        plan = p.read(base / "plan.json")
        p.require(
            p.file_hash(base / "plan.json") == grant["plan_sha256"]
            and plan["source_map"] == grant["source_map"]
            and plan["config_sha256"] == p.file_hash(p.ROOT / p.CONFIG)
            and plan["prompt_sha256"] == p.file_hash(p.ROOT / p.PROMPT),
            "Worker frozen plan and actual prompt",
        )
        if not grant["synthetic_only"]:
            anchor = p.read(p.ROOT / p.OUTPUT / "attempt.json")
            p.require(
                anchor["directory"] == str(base.relative_to(p.ROOT))
                and anchor["plan_sha256"] == grant["plan_sha256"],
                "Durable consumed operational anchor",
            )
            for prior in range(1, (grant["repetition"] or 4)):
                accepted = p.read(base / f"repetition{prior}/parent-acceptance.json")
                p.require(
                    accepted["acceptance"]["status"] == "parent_accepted_worker"
                    and accepted["body_sha256"]
                    == p.file_hash(base / f"repetition{prior}/receipt.json"),
                    "Accepted predecessor before next phase",
                )
    spec = p.load()
    clock = rt.ContinuousClock()
    guard = rt.ServiceGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    body = dict(
        status="failed",
        grant_sha256=p.file_hash(directory / "grant.json"),
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        phase=grant["phase"],
    )
    limiter = None
    try:
        guard.__enter__()
        p.require(
            p.source_map() == grant["source_map"]
            and p.dependencies() == grant["dependencies"],
            "Worker frozen source/dependency",
        )
        p.require(
            all(
                os.environ.get(k) == v
                for k, v in spec["runtime"]["thread_environment_before_imports"].items()
            )
            and all(k not in sys.modules for k in ("numpy", "torch")),
            "Thread environment before numerical imports",
        )
        rt.boundary(
            directory,
            numerical=grant["phase"].startswith("repetition"),
            synthetic=grant["synthetic_only"],
        )
        if grant["phase"] == "reporting":
            p.require(
                p.file_hash(directory / "aggregate.json") == grant["aggregate_sha256"],
                "Owned aggregate identity",
            )
            from raregate.benchmarks.prepared_service_reporting import render

            names = render(directory, poll=guard.check)
        else:
            from raregate.benchmarks import core

            limiter, threads = core.configure_threads(spec)
            body["threads_before"] = threads
            build = dict(
                torch_config_sha256=p.digest(core.torch.__config__.show()),
                torch_version=str(core.torch.__version__),
                numpy_version=core.np.__version__,
                thread_support=threads,
            )
            p.require(
                build["torch_config_sha256"]
                == spec["numerical"]["runtime_torch_build_sha256"],
                "Frozen native build",
            )
            if grant["phase"] == "probe":
                p.durable_json(directory / "probe.json", build, exclusive=True)
                names = ["probe.json"]
            else:
                p.require(
                    build["torch_config_sha256"]
                    == grant["build"]["torch_config_sha256"]
                    and build["torch_version"] == grant["build"]["torch_version"]
                    and build["numpy_version"] == grant["build"]["numpy_version"],
                    "Runtime build freeze",
                )
                names = repeat(directory, grant, spec, guard, clock, body)
            body["threads_after"] = core.effective_threads()
        guard.boundary("body_outputs_complete")
        body.update(
            status="body_complete_awaiting_exit",
            outputs={n: p.file_hash(directory / n) for n in names},
        )
    except BaseException as exc:
        body["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        tick = clock()
        try:
            if limiter:
                limiter.restore_original_limits()
        except BaseException as exc:
            body.update(status="failed", error=str(exc))
        guard.close()
        body.update(
            resources=guard.report(),
            monitor_closed_continuous=clock(),
            cleanup_seconds=clock() - tick,
            worker_seconds=clock() - grant["started_continuous"],
            worker_ordinary_seconds=time.monotonic() - grant["started_ordinary"],
        )
        p.durable_json(directory / "receipt.json", body, exclusive=True)
    return (
        0
        if body["status"] == "body_complete_awaiting_exit"
        and body["cleanup_seconds"] <= 2
        and clock() < grant["stage_deadline"]
        else 1
    )
