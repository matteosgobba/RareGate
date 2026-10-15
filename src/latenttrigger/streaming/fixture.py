"""Explicit bounded generated fixture execution. No operational settings or backend."""

import hashlib
import json
import multiprocessing as mp
import os
import struct
import time
from pathlib import Path

from .generated import GeneratedBackend, gather
from .protocol import Descriptor, Scheduler, position, require
from .records import (
    EVENT_STATUS,
    STAGE,
    Phases,
    Store,
    reconcile,
    stage_projection,
    timing_summary,
)
from .supervision import (
    Clocks,
    Monitor,
    cleanup_children,
    cleanup_snapshot,
    own_rss,
    phase_during_cleanup,
    release_region,
    safety,
)
from .transport import Ring

SCENARIOS = {
    "normal_wrap": (128, 100),
    "capacity": (96, 500),
    "contention": (32, 1000),
    "die_before_return": (8, 500),
    "die_after_return": (8, 500),
    "die_after_output": (8, 500),
    "die_with_mutex": (8, 500),
    "failed_start": (8, 500),
}
RUN_CAP_SECONDS = 5
RSS_CAPS = {"producer": 64 * 1024**2, "consumer": 1024**3, "supervisor": 128 * 1024**2}
STORAGE_CAP = 16 * 1024**2


def _json(path, value):
    blob = (json.dumps(value, allow_nan=False, indent=2) + "\n").encode()
    require(len(blob) <= 65536, "Bounded diagnostic JSON")
    with open(path, "xb") as f:
        f.write(blob)


def _summary(path, role, clocks, stats, **extra):
    _json(
        path,
        {
            "role": role,
            "synthetic_only": True,
            "stats": stats,
            "peak_RSS_bytes": own_rss(),
            "clock_observation": clocks.observation(),
            **extra,
        },
    )


def _producer(name, lock, start, stop, directory, count, rate):
    ring = Ring.attach(name, lock)
    store = Store(Path(directory) / "events.bin", count, "event")
    clocks = Clocks()
    phases = Phases(Path(directory) / "producer-phases.bin", 1)
    phases.append(1, clocks, own_rss())
    stats = {"append_calls": 0, "max_append_ns": 0, "offers_resolved": 0}

    def write(k, e):
        before = clocks.service()
        store.write(k, e)
        stats["max_append_ns"] = max(stats["max_append_ns"], clocks.service() - before)
        stats["append_calls"] += 1

    try:
        ring.update(producer_ready=1, producer_rss=own_rss())
        phases.append(2, clocks, own_rss())
        require(start.wait(2), "Fixture producer start timeout")
        snap = ring.snapshot()
        require(snap is not None, "Producer startup snapshot")
        scheduler = Scheduler(snap["t0"], count, rate)
        ring.update(producer_armed=1)
        phases.append(3, clocks, own_rss())

        def emit(k, intended, action):
            now = clocks.service()
            if action == "attempt":
                if now >= scheduler.horizon:
                    action = "missed_horizon"
                elif now - intended > 2_000_000:
                    action = "missed_late"
            e = dict(
                run=1,
                k=k,
                prefix=position(k),
                cycle=k // 384,
                phase=1,
                intended=intended,
                status=EVENT_STATUS.get(action, 1),
                reason=0,
                observed=now,
            )
            if action != "attempt":
                e.update(reason=e["status"], detection=now)
                write(k, e)
            else:
                e.update(submission=now, status=1)
                write(k, e)  # durable intent precedes possible publication
                outcome, stamp, sequence = ring.admit(
                    Descriptor(1, k, position(k), intended, now), clocks.service
                )
                e.update(status=EVENT_STATUS[outcome], observed=stamp)
                if outcome == "admitted":
                    e.update(admission=stamp, sequence=sequence)
                else:
                    e.update(rejection=stamp, reason=e["status"])
                write(k, e)
            stats["offers_resolved"] += 1

        while scheduler.k < count and not stop.is_set():
            next_time = scheduler.wake(clocks.service(), emit)
            if next_time is not None:
                stop.wait(max(0, (next_time - clocks.service()) / 1e9))
        if not stop.is_set():
            stop.wait(max(0, (scheduler.horizon - clocks.service()) / 1e9))
            ring.update(producer_closed=1, producer_rss=own_rss())
            phases.append(4, clocks, own_rss())
        _summary(Path(directory) / "producer.json", "producer", clocks, stats)
    finally:
        phases.append(9, clocks, own_rss())
        phases.close()
        store.close()
        ring.close()


def _consumer(name, lock, start, stop, armed, directory, count, scenario):
    ring = Ring.attach(name, lock)
    store = Store(Path(directory) / "batches.bin", count, "batch")
    output = os.open(Path(directory) / "outputs.bin", os.O_RDWR)
    clocks = Clocks()
    phases = Phases(Path(directory) / "consumer-phases.bin", 2)
    phases.append(1, clocks, own_rss())
    backend = GeneratedBackend()
    stats = {
        "batches": 0,
        "append_calls": 0,
        "max_append_ns": 0,
        "read_intents": 0,
        "read_rows": 0,
        "feature_intents": 0,
        "feature_rows": 0,
        "score_intents": 0,
        "score_rows": 0,
        "reference_intents": 0,
        "reference_rows": 0,
        "boolean_outputs": 0,
    }

    def write(b):
        before = clocks.service()
        store.write(b["batch"], b)
        stats["max_append_ns"] = max(stats["max_append_ns"], clocks.service() - before)
        stats["append_calls"] += 1

    try:
        ring.update(consumer_ready=1, consumer_rss=own_rss())
        phases.append(2, clocks, own_rss())
        require(start.wait(2), "Fixture consumer start timeout")
        phases.append(3, clocks, own_rss())
        if scenario in ("contention", "die_with_mutex"):
            # Adversarial fixture only: emulate a misbehaving/dead mutex owner.
            # The real ring never waits/logs/services with its mutex held.
            lock.acquire()
            armed.set()
            if scenario == "die_with_mutex":
                os._exit(73)
            stop.wait(0.15)
            lock.release()
        while not stop.is_set():
            snap = ring.snapshot()
            if snap is None:
                stop.wait(0.0001)
                continue
            if scenario == "capacity" and not snap["producer_closed"]:
                stop.wait(0.0001)  # explicit barrier: fill credits before consumption
                continue
            group = ring.stage(clocks.service)
            if not group:
                if snap["producer_closed"] and snap["pending"] == 0:
                    break
                stop.wait(0.0001)
                continue
            b = dict(
                run=1,
                phase=1,
                batch=stats["batches"],
                m=len(group),
                status=STAGE["staged"],
                reason=1 if len(group) == 8 else (3 if snap["producer_closed"] else 2),
                members=[d.presentation for d, _, _, _ in group],
                positions=[d.prefix for d, _, _, _ in group],
                dequeues=[dq for _, _, _, dq in group],
                admissions=[a for _, a, _, _ in group],
                subread_starts=[],
                subread_ends=[],
            )
            write(b)
            ring.activate(b["m"], clocks.service)
            b.update(dispatch=clocks.service(), status=STAGE["active"])
            write(b)

            def read_start(j, n, b=b):
                b["read_intents"] = b.get("read_intents", 0) + 1
                stats["read_intents"] += 1
                b["subread_starts"].append(clocks.service())
                b["status"] = STAGE["read_intent"]
                write(b)
                if scenario == "die_before_return":
                    os._exit(71)

            def read_return(j, n, b=b):
                b["subread_ends"].append(clocks.service())
                b["read_rows"] = b.get("read_rows", 0) + n
                stats["read_rows"] += n
                b.update(read_return=clocks.service(), status=STAGE["read_return"])
                write(b)
                if scenario == "die_after_return":
                    os._exit(72)

            try:
                b["read_start"] = clocks.service()
                rows = gather(b["positions"], backend.read, read_start, read_return)
                b.update(
                    status=STAGE["feature_intent"],
                    feature_intents=1,
                    feature_intent=clocks.service(),
                )
                stats["feature_intents"] += 1
                write(b)
                features = backend.features(rows)
                b.update(
                    features=clocks.service(),
                    feature_rows=b["m"],
                    status=STAGE["features"],
                )
                stats["feature_rows"] += b["m"]
                write(b)
                b.update(
                    status=STAGE["score_intent"],
                    score_intents=1,
                    score_intent=clocks.service(),
                )
                stats["score_intents"] += 1
                write(b)
                scores, masks = backend.decisions(features)
                b.update(
                    decision=clocks.service(),
                    score_rows=b["m"],
                    status=STAGE["decision"],
                )
                stats["score_rows"] += b["m"]
                write(b)
                for i, k in enumerate(b["members"]):
                    payload = struct.pack("<d4B", float(scores[i]), *map(int, masks[i]))
                    require(
                        os.pwrite(output, payload, 12 * k) == 12,
                        "Output retention write",
                    )
                output_stamp = ring.finish(b["m"], clocks.service)
                b.update(output=output_stamp, status=STAGE["output"])
                write(b)
                stats["boolean_outputs"] += 4 * b["m"]
                if scenario == "die_after_output":
                    os._exit(74)
                b["reference_intents"] = 1
                b["reference_intent"] = clocks.service()
                stats["reference_intents"] += 1
                write(b)
                backend.reference(b["positions"], scores, masks)
                b.update(
                    reference_rows=b["m"],
                    reference_return=clocks.service(),
                    digest=hashlib.sha256(scores.tobytes() + masks.tobytes()).digest()[
                        :16
                    ],
                )
                stats["reference_rows"] += b["m"]
                b.update(control_end=clocks.service(), status=STAGE["verified"])
                write(b)
                stats["batches"] += 1
                ring.update(consumer_rss=own_rss())
            except Exception:
                b.update(
                    terminal=clocks.service(), status=STAGE["failed"], missing_reason=1
                )
                write(b)
                if b.get("output") is None:
                    ring.finish(b["m"], clocks.service, "failed")
                ring.update(error=1)
                raise
        _summary(Path(directory) / "consumer.json", "consumer", clocks, stats)
    finally:
        phases.append(9, clocks, own_rss())
        phases.close()
        os.close(output)
        store.close()
        ring.close()


def run_fixture(directory, scenario):
    """One invocation; supervisor is this process, with exactly two spawned roles."""
    entered = time.perf_counter_ns()
    require(scenario in SCENARIOS, "Unknown fixture, no operational mode")
    directory = Path(directory)
    directory.mkdir(mode=0o700)  # no reuse/overwrite of earlier evidence
    count, rate = SCENARIOS[scenario]
    clocks = Clocks()
    started = clocks.continuous() - (time.perf_counter_ns() - entered)
    observation = clocks.observation()
    monitor = Monitor(*observation[:2])
    ctx = mp.get_context("spawn")
    lock = ctx.Lock()
    producer_start, consumer_start, stop, armed = (ctx.Event() for _ in range(4))
    ring = Ring.create(lock, directory)
    shared_name = ring.shm.name
    for filename, kind in (("events.bin", "event"), ("batches.bin", "batch")):
        st = Store(directory / filename, count, kind, True)
        st.close()
    for role, name in ((1, "producer"), (2, "consumer"), (3, "supervisor")):
        phase = Phases(directory / (name + "-phases.bin"), role, True)
        phase.close()
    phases = Phases(directory / "supervisor-phases.bin", 3)
    phases.append(1, clocks, own_rss())
    fd = os.open(directory / "outputs.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    os.ftruncate(fd, count * 12)
    os.close(fd)
    producer = ctx.Process(
        name="fixture-producer",
        target=_producer,
        args=(shared_name, lock, producer_start, stop, str(directory), count, rate),
    )
    consumer = ctx.Process(
        name="fixture-consumer",
        target=_consumer,
        args=(
            shared_name,
            lock,
            consumer_start,
            stop,
            armed,
            str(directory),
            count,
            scenario,
        ),
    )
    children = [producer, consumer]
    problem = None
    samples = 0
    max_rss = {"supervisor": own_rss(), "producer": 0, "consumer": 0}
    t0 = None
    last_snapshot = None
    try:
        producer.start()
        if scenario == "failed_start":
            raise RuntimeError("Injected second-child start failure")
        consumer.start()
        while True:
            service, continuous, _ = clocks.observation()
            monitor.observe(service, continuous)
            samples += 1
            snap = ring.snapshot()
            if snap:
                last_snapshot = snap
                for role in ("producer", "consumer"):
                    max_rss[role] = max(max_rss[role], snap[role + "_rss"])
                if snap["producer_ready"] and snap["consumer_ready"]:
                    break
            require(
                all(p.exitcode is None for p in children), "Child exited before ready"
            )
            safety(continuous, started, continuous, continuous, 0)
            stop.wait(0.005)
        t0 = clocks.service() + 100_000_000
        ring.update(t0=t0)
        producer_start.set()
        while True:
            service, continuous, _ = clocks.observation()
            monitor.observe(service, continuous)
            safety(continuous, started, continuous, continuous, 0)
            snap = ring.snapshot()
            if snap and snap["producer_armed"]:
                break
            require(producer.exitcode is None, "Producer failed before arming")
            stop.wait(0.001)
        consumer_start.set()
        if scenario in ("contention", "die_with_mutex"):
            while not armed.is_set():
                service, continuous, _ = clocks.observation()
                monitor.observe(service, continuous)
                safety(continuous, started, continuous, continuous, 0)
                require(consumer.exitcode is None, "Consumer failed before mutex fault")
                stop.wait(0.001)
        scheduler = Scheduler(t0, count, rate)
        while any(p.is_alive() for p in children):
            service, continuous, _ = clocks.observation()
            monitor.observe(service, continuous)
            samples += 1
            require(
                not any(p.exitcode not in (None, 0) for p in children), "Child failure"
            )
            snap = ring.snapshot()
            if snap:
                last_snapshot = snap
                require(not snap["error"], "Child error state")
                pending = snap["pending"]
                last_progress = snap["progress"] or t0
                safety(
                    continuous,
                    started,
                    continuous + (scheduler.horizon - service),
                    continuous - (service - last_progress),
                    pending,
                )
                for role in ("producer", "consumer"):
                    max_rss[role] = max(max_rss[role], snap[role + "_rss"])
            else:
                safety(continuous, started, continuous, continuous, 0)
            max_rss["supervisor"] = max(max_rss["supervisor"], own_rss())
            require(
                all(max_rss[r] <= RSS_CAPS[r] for r in max_rss), "Fixture RSS ceiling"
            )
            require(
                sum(max_rss.values()) <= 1216 * 1024**2, "Fixture aggregate RSS ceiling"
            )
            require(
                sum(p.stat().st_size for p in directory.iterdir()) <= STORAGE_CAP,
                "Fixture storage",
            )
            stop.wait(0.005)
        require(all(p.exitcode == 0 for p in children), "Child abnormal exit")
    except Exception as exc:
        problem = type(exc).__name__ + ": " + str(exc)
    finally:
        cleanup_start = clocks.continuous()
        phase_error = phase_during_cleanup(phases, 7, clocks, own_rss())
        if phase_error:
            problem = problem or "Cleanup phase journal: " + phase_error
        exits = cleanup_children(
            children,
            stop,
            clocks.continuous,
            min(started + 5_000_000_000, cleanup_start + 2_000_000_000),
        )
        final_snapshot, snapshot_error = cleanup_snapshot(ring)
        if snapshot_error:
            problem = problem or "Cleanup snapshot: " + snapshot_error
        if final_snapshot is not None:
            last_snapshot = final_snapshot
        first_unlink, repeated_unlink, region_errors = release_region(ring)
        if region_errors:
            problem = problem or "Region cleanup: " + str(region_errors)
        try:
            leftover = open(shared_name, "rb")
        except FileNotFoundError:
            absent = True
        else:
            absent = False
            leftover.close()
        phase_error = phase_during_cleanup(phases, 8, clocks, own_rss())
        if phase_error:
            problem = problem or "Cleanup phase journal: " + phase_error
        phases.close()
        cleanup_ns = clocks.continuous() - cleanup_start
    event_store = Store(directory / "events.bin", count, "event")
    batch_store = Store(directory / "batches.bin", count, "batch")
    try:
        events, batches = event_store.read_all(), batch_store.read_all()
    finally:
        event_store.close()
        batch_store.close()
    cutoff = clocks.service()
    scheduler = Scheduler(t0 if t0 is not None else cutoff + 1, count, rate)
    accounting = {
        "horizon": reconcile(events, batches, scheduler, scheduler.horizon)
        if t0 is not None
        else None,
        "after_stop": reconcile(events, batches, scheduler, cutoff),
    }
    stage_counts = {
        k: sum(b.get(k, 0) for b in filter(None, batches))
        for k in (
            "read_intents",
            "read_rows",
            "feature_intents",
            "feature_rows",
            "score_intents",
            "score_rows",
            "reference_intents",
            "reference_rows",
        )
    }
    live_batches = list(filter(None, batches))
    stage_counts["read_returned_calls"] = sum(
        sum(t > 0 for t in b["subread_ends"]) for b in live_batches
    )
    stage_counts["read_inflight_uncertain_calls"] = (
        stage_counts["read_intents"] - stage_counts["read_returned_calls"]
    )
    for intent, stamp in (("feature", "features"), ("score", "decision")):
        returned = sum(b.get(stamp) is not None for b in live_batches)
        stage_counts[intent + "_returned_calls"] = returned
        stage_counts[intent + "_inflight_uncertain_calls"] = (
            stage_counts[intent + "_intents"] - returned
        )
    stage_counts["reference_inflight_uncertain_calls"] = stage_counts[
        "reference_intents"
    ] - sum(b["reference_rows"] > 0 for b in live_batches)
    phase_counts = {}
    for role, name in ((1, "producer"), (2, "consumer"), (3, "supervisor")):
        ph = Phases(directory / (name + "-phases.bin"), role)
        phase_counts[name] = ph.read_all()
        ph.close()
    normal = problem is None and all(x["normal"] for x in exits)
    final = accounting["after_stop"]
    expected_fault = {
        "die_before_return": 71,
        "die_after_return": 72,
        "die_after_output": 74,
        "die_with_mutex": 73,
    }
    checks = {
        "cleanup_absent": absent,
        "no_leaked_child": not any(e.get("leaked") for e in exits),
    }
    if scenario in ("normal_wrap", "capacity", "contention"):
        checks["normal_exit"] = normal
        checks["pending_zero_records"] = (
            sum(
                final[k]
                for k in ("ring", "staged", "active", "undecided", "unresolved")
            )
            == 0
        )
        checks["pending_zero_shared"] = (
            last_snapshot is not None and last_snapshot["pending"] == 0
        )
        if scenario == "normal_wrap":
            checks["wrap_observed"] = final["admitted"] > 64
        if scenario == "capacity":
            checks["capacity_rejected"] = (
                final["rejected_capacity"] > 0
                and last_snapshot is not None
                and last_snapshot["tail"] >= 64
            )
        if scenario == "contention":
            checks["contention_rejected"] = final["rejected_contention"] > 0
    elif scenario == "failed_start":
        checks["failed_start_observed"] = (
            problem is not None
            and "start failure" in problem
            and any(not e["started"] for e in exits)
        )
    else:
        checks["injected_exit_observed"] = any(
            e["exitcode"] == expected_fault[scenario] for e in exits
        )
        if scenario == "die_before_return":
            checks["read_uncertain"] = (
                stage_counts["read_inflight_uncertain_calls"] > 0
                and final["active"] > 0
            )
        if scenario == "die_after_return":
            checks["returned_not_constructed"] = (
                stage_counts["read_rows"] > 0
                and stage_counts["feature_rows"] == 0
                and final["active"] > 0
            )
        if scenario == "die_after_output":
            checks["completion_retained"] = (
                final["completed"] > 0 and stage_counts["reference_rows"] == 0
            )
    require(
        absent
        and first_unlink
        and not repeated_unlink
        and cleanup_ns <= 2_000_000_000
        and not any(e.get("leaked") for e in exits),
        "Cleanup validity",
    )
    elapsed = clocks.continuous() - started
    require(elapsed <= 5_000_000_000, "Fixture whole duration")
    report = dict(
        scenario=scenario,
        software_checks=checks,
        software_checks_passed=all(checks.values()),
        phase_observations=phase_counts,
        fixture_only=True,
        arrival_clock_issued=t0 is not None,
        timing_observations=timing_summary(events, batches, cutoff),
        configured_offers=count,
        actual_resolved_offers=sum(e is not None for e in events),
        normal=normal,
        problem=problem,
        elapsed_ns=elapsed,
        cleanup_ns=cleanup_ns,
        children=exits,
        shared_memory_bytes=12288,
        shared_name=shared_name,
        unlinked=absent,
        repeated_unlink_safe=not repeated_unlink,
        monitor_samples=samples,
        maximum_monitor_gap_ns=monitor.maximum_gap,
        clock_bracket_ns=observation[2],
        service_clock=time.get_clock_info("perf_counter").__dict__,
        own_process_peak_RSS_bytes=max_rss,
        accounting=accounting,
        synthetic_stage_counts=stage_counts,
        stage_projection_after_stop=stage_projection(batches, cutoff),
        stage_projection_at_H=stage_projection(batches, scheduler.horizon)
        if t0 is not None
        else None,
        synchronization="1spawn mutex +4Events (21SemLocks); OS/native allocation unknown, P2 remains open",
        timestamp_scope="same-host actual fixture process clocks, synthetic read/feature/score stages;no operational certification",
    )
    _json(directory / "supervisor.json", report)
    require(
        clocks.continuous() - started <= 5_000_000_000,
        "Fixture including final records5s",
    )
    return report


def validate_generated(output, scenarios=tuple(SCENARIOS)):
    """Explicit activation only. Settings cannot specify real providers or payload paths."""
    entered = time.perf_counter_ns()
    require(
        1 <= len(scenarios) <= 12
        and len(set(scenarios)) == len(scenarios)
        and all(s in SCENARIOS for s in scenarios),
        "Bounded distinct fixture scenarios",
    )
    require(sum(SCENARIOS[s][0] for s in scenarios) <= 1536, "Fixture offer envelope")
    output = Path(output)
    require(
        output.is_absolute() and not output.exists(),
        "New absolute owned fixture directory required",
    )
    # Only ignored task-owned output root, or an explicitly named /tmp child.
    parent = output.parent.resolve()
    repo = Path(__file__).resolve().parents[3]
    allowed = repo / "data/task0051-validation"
    require(
        parent == allowed
        or parent == Path("/private/tmp")
        or parent == Path("/tmp").resolve(),
        "Fixture output root only",
    )
    parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(mode=0o700)
    _json(
        output / "owner.json",
        {"task": "0051", "kind": "generated_fixture_diagnostics", "operational": False},
    )
    clocks = Clocks()
    begin = clocks.continuous() - (time.perf_counter_ns() - entered)
    reports = []
    for i, scenario in enumerate(scenarios):
        require(
            clocks.continuous() - begin < 85_000_000_000,
            "Native fixture total deadline",
        )
        # Attempt declaration is a test log, never an operational authorization/grant.
        _json(
            output / f"attempt-{i + 1}.json",
            {"scenario": scenario, "configured_offers": SCENARIOS[scenario][0]},
        )
        try:
            report = run_fixture(output / f"{i + 1:02d}-{scenario}", scenario)
        except Exception as exc:
            report = {
                "scenario": scenario,
                "configured_offers": SCENARIOS[scenario][0],
                "software_checks_passed": False,
                "harness_error": type(exc).__name__ + ": " + str(exc),
                "partial_evidence_retained": True,
            }
        reports.append(report)
        _json(output / f"result-{i + 1}.json", report)
        if not report["software_checks_passed"]:
            break
        require(
            sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
            <= STORAGE_CAP,
            "Total fixture diagnostics",
        )
    elapsed = clocks.continuous() - begin
    require(elapsed <= 90_000_000_000, "Native fixture total90s")
    result = {
        "fixture_only": True,
        "attempts": reports,
        "elapsed_ns": elapsed,
        "configured_offers": sum(r["configured_offers"] for r in reports),
        "unattempted_scenarios": list(scenarios[len(reports) :]),
        "software_checks_passed": all(r["software_checks_passed"] for r in reports)
        and len(reports) == len(scenarios),
        "diagnostic_bytes": sum(
            p.stat().st_size for p in output.rglob("*") if p.is_file()
        ),
    }
    _json(output / "fixture-results.json", result)
    require(
        clocks.continuous() - begin <= 90_000_000_000, "Native fixture finalization90s"
    )
    return result
