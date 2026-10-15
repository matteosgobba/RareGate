"""Explicit bounded generated fixture execution. No operational settings or backend."""

import hashlib
import json
import multiprocessing as mp
import os
import struct
import time
from pathlib import Path

from . import quota
from .generated import GeneratedBackend, gather
from .instrumentation import Samples, grouped_samples
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
from .resources import POLICY, TrackerBudget
from .supervision import (
    Clocks,
    Monitor,
    cleanup_children,
    cleanup_snapshot,
    own_rss,
    phase_during_cleanup,
    release_region,
    safety,
    synchronization_inventory,
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
SCENARIOS52 = {
    "normal500": (128, 500),
    "normal2500": (128, 2500),
    "normal5000": (128, 5000),
    "capacity": (96, 500),
    "contention": (32, 1000),
    "die_before_return": (8, 500),
    "die_after_return": (8, 500),
    "die_after_output": (8, 500),
    "die_with_mutex": (8, 500),
    "failed_start": (8, 500),
    "torn_publication": (8, 500),
    "failed_publication_cleanup": (8, 500),
}


class FixtureStore(Store):
    """Explicit artificial publisher faults, never an operational replacement."""

    def __init__(self, *args, scenario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.scenario = scenario
        self.injected = False

    def write(self, index, record):
        inject = not self.injected and record.get("status") == STAGE["read_return"]
        if inject and self.scenario == "failed_publication_cleanup":
            self.injected = True
            raise OSError("Injected record publication failure before copy")
        if inject and self.scenario == "torn_publication":
            from .records import encode_into

            encode_into(record, self.kind, self.scratch)
            offset = index * 512
            self.mapping[offset : offset + 256] = self.scratch[:256]
            self.mapping[offset + 504 : offset + 512] = bytes(8)
            os._exit(75)
        return super().write(index, record)


def startup_snapshot(ring, stop, clocks):
    """Startup may contend with supervisor polling; no arrival has begun."""
    deadline = clocks.continuous() + 50_000_000
    while not stop.is_set() and clocks.continuous() < deadline:
        snap = ring.snapshot()
        if snap is not None:
            return snap
        stop.wait(0.0001)
    raise ValueError("Producer startup snapshot timeout/stop")


def exercise_terminal_preflight(ring, m, clock):
    before = ring.snapshot()
    require(
        before is not None and before["active"] == m, "Actual active preflight shape"
    )
    ring.update(failed=(1 << 64) - 1)
    try:
        ring.finish(m, clock, "failed")
    except ValueError as exc:
        error = str(exc)
    else:
        raise ValueError("Expected terminal overflow")
    after = ring.snapshot()
    preserved = all(
        after[k] == before[k] for k in ("pending", "active", "staged", "head", "tail")
    )
    require(
        preserved and "overflow" in error, "Terminal preflight must preserve credits"
    )
    ring.update(failed=before["failed"])
    return dict(credits_preserved=preserved, error=error, m=m)


class ObservedPhases:
    def __init__(self, phases, samples, clocks):
        self.phases, self.samples, self.clocks = phases, samples, clocks

    def append(self, code, clocks, rss):
        start = self.clocks.service()
        self.phases.append(code, clocks, rss)
        self.samples.add(5, code, 0, 1, start, self.clocks.service())

    def close(self):
        self.phases.close()


def close_owned(objects):
    errors = []
    for obj in objects:
        try:
            obj.close()
        except (ValueError, OSError, BufferError) as exc:
            errors.append(str(exc))
    return errors


RUN_CAP_SECONDS = 5
RSS_CAPS = {"producer": 64 * 1024**2, "consumer": 1024**3, "supervisor": 128 * 1024**2}
STORAGE_CAP = 16 * 1024**2


def _json(path, value):
    if quota.CURRENT is not None:
        quota.CURRENT.write_json(path, value)
        return
    blob = (json.dumps(value, allow_nan=False, indent=2) + "\n").encode()
    require(len(blob) <= 131072, "Bounded diagnostic JSON")
    with open(path, "xb") as f:
        f.write(blob)


def _summary(path, role, clocks, stats, **extra):
    if quota.CURRENT is not None:
        # v2 retains phase/sample journals plus exit codes; no duplicate child JSON.
        return
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


def _producer(
    name, lock, start, stop, directory, count, rate, quota_root=None, setup_seconds=2
):
    if quota_root is not None:
        quota.activate(quota_root)
    from .startup55 import install_payload_denial

    payload_audit = install_payload_denial(
        Path(__file__).resolve().parents[3],
        quota.CURRENT.root if quota.CURRENT is not None else Path(directory),
    )
    clocks = Clocks()
    init = clocks.service()
    samples = Samples(Path(directory) / "producer-samples.bin", 768)
    ring = Ring.attach(name, lock)
    store = Store(Path(directory) / "events.bin", count, "event")
    phases = ObservedPhases(
        Phases(Path(directory) / "producer-phases.bin", 1), samples, clocks
    )
    samples.add(6, 0, 0, 0, init, clocks.service())
    phases.append(1, clocks, own_rss())
    stats = {"append_calls": 0, "max_append_ns": 0, "offers_resolved": 0}

    def write(k, e):
        before = clocks.service()
        store.write(k, e)
        end = clocks.service()
        stats["max_append_ns"] = max(stats["max_append_ns"], end - before)
        stats["append_calls"] += 1
        samples.add(1, e["status"], 1, 1, before, end)
        samples.add(9, e["status"], 1, 1, before, clocks.service())

    try:
        require(
            payload_audit["denied_open_attempts"] == 0,
            "Unexpected producer payload access",
        )
        ring.update(producer_ready=1, producer_rss=own_rss())
        phases.append(2, clocks, own_rss())
        require(start.wait(setup_seconds), "Bounded producer setup timeout")
        snap = startup_snapshot(ring, stop, clocks)
        scheduler = Scheduler(snap["t0"], count, rate)
        ring.update(producer_armed=1)
        phases.append(3, clocks, own_rss())

        def emit(k, intended, action):
            require(own_rss() <= RSS_CAPS["producer"], "Producer own RSS ceiling")
            cycle = clocks.service()
            writes = stats["append_calls"]
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
                write(k, e)  # process-crash-visible intent before possible publication
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
            samples.add(
                3,
                e["status"],
                1,
                stats["append_calls"] - writes,
                cycle,
                clocks.service(),
            )

        while scheduler.k < count and not stop.is_set():
            next_time = scheduler.wake(clocks.service(), emit)
            if next_time is not None:
                stop.wait(max(0, (next_time - clocks.service()) / 1e9))
        if not stop.is_set():
            stop.wait(max(0, (scheduler.horizon - clocks.service()) / 1e9))
            ring.update(producer_closed=1, producer_rss=own_rss())
            phases.append(4, clocks, own_rss())
        require(
            payload_audit["denied_open_attempts"] == 0,
            "Unexpected producer payload access",
        )
        _summary(Path(directory) / "producer.json", "producer", clocks, stats)
    finally:
        final_start = clocks.service()
        error = phase_during_cleanup(phases, 9, clocks, own_rss())
        errors = close_owned([phases, store, ring])
        try:
            samples.add(
                7, int(bool(error or errors)), 0, 0, final_start, clocks.service()
            )
        finally:
            samples.close()


def _consumer(
    name,
    lock,
    start,
    stop,
    armed,
    directory,
    count,
    scenario,
    quota_root=None,
    pilot=None,
):
    if quota_root is not None:
        quota.activate(quota_root)
    clocks = Clocks()
    init = clocks.service()
    samples = Samples(Path(directory) / "consumer-samples.bin", 4096)
    ring = Ring.attach(name, lock)
    store = FixtureStore(
        Path(directory) / "batches.bin", count, "batch", scenario=scenario
    )
    output = quota.open_file(Path(directory) / "outputs.bin", os.O_RDWR)
    phases = ObservedPhases(
        Phases(Path(directory) / "consumer-phases.bin", 2), samples, clocks
    )
    phases.append(1, clocks, own_rss())
    backend = None
    payload_audit = None
    if pilot is None:
        from .startup55 import install_payload_denial

        payload_audit = install_payload_denial(
            Path(__file__).resolve().parents[3],
            quota.CURRENT.root if quota.CURRENT is not None else Path(directory),
        )
        backend = GeneratedBackend()
        require(
            payload_audit["denied_open_attempts"] == 0,
            "Unexpected generated payload access",
        )
    else:
        from .pilot_context import FixtureContext56
        from .session_context import SessionFixture57

        if type(pilot.get("context")) in (FixtureContext56, SessionFixture57):
            from .startup55 import install_payload_denial

            payload_audit = install_payload_denial(
                Path(__file__).resolve().parents[3], quota.CURRENT.root
            )
        from .hdf_consumer import RealBackend

        backend = RealBackend.__new__(RealBackend)
        try:
            RealBackend.__init__(
                backend,
                quota_root,
                directory,
                pilot["candidate"],
                clocks,
                lambda: ring.update(consumer_rss=own_rss(), progress=clocks.service()),
                context=pilot.get("context"),
            )
        except BaseException as exc:
            from .hdf_consumer import record_initialization_failure

            try:
                record_initialization_failure(
                    backend, Path(directory) / "consumer-final.json", exc
                )
            finally:
                try:
                    quota.close(output)
                finally:
                    close_owned([backend, phases, store, ring, samples])
            raise
    samples.add(6, 0, 0, 0, init, clocks.service())
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
        end = clocks.service()
        stats["max_append_ns"] = max(stats["max_append_ns"], end - before)
        stats["append_calls"] += 1
        samples.add(2, b["status"], b["m"], 1, before, end)
        samples.add(10, b["status"], b["m"], 1, before, clocks.service())

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
            cycle = clocks.service()
            writes = stats["append_calls"]
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
                if pilot is not None:
                    b["subread_starts"][-1] = backend.last_hdf_start
                b["subread_ends"].append(
                    clocks.service() if pilot is None else backend.last_hdf_return
                )
                b["read_rows"] = b.get("read_rows", 0) + n
                stats["read_rows"] += n
                b.update(read_return=clocks.service(), status=STAGE["read_return"])
                write(b)
                if scenario == "die_after_return":
                    os._exit(72)

            try:
                b["read_start"] = clocks.service()
                if pilot is None:
                    rows = gather(b["positions"], backend.read, read_start, read_return)
                else:
                    from .hdf_consumer import gather_real

                    rows = gather_real(
                        b["positions"], backend.read, read_start, read_return
                    )
                b.update(
                    status=STAGE["feature_intent"],
                    feature_intents=1,
                    feature_intent=clocks.service(),
                )
                stats["feature_intents"] += 1
                write(b)
                features = backend.features(rows)
                b.update(
                    features=clocks.service()
                    if pilot is None
                    else backend.last_feature_end,
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
                    decision=clocks.service()
                    if pilot is None
                    else backend.last_decision_end,
                    score_rows=b["m"],
                    status=STAGE["decision"],
                )
                stats["score_rows"] += b["m"]
                write(b)
                output_start = clocks.service()
                for i, k in enumerate(b["members"]):
                    payload = struct.pack("<d4B", float(scores[i]), *map(int, masks[i]))
                    require(
                        quota.pwrite(output, payload, 12 * k) == 12,
                        "Output retention write",
                    )
                samples.add(8, 0, b["m"], b["m"], output_start, clocks.service())
                output_stamp = ring.finish(b["m"], clocks.service)
                b.update(output=output_stamp, status=STAGE["output"])
                write(b)
                stats["boolean_outputs"] += 4 * b["m"]
                if scenario == "die_after_output":
                    # Explicit combined post-output/dead-mutex-owner barrier.
                    require(lock.acquire(timeout=0.05), "Post-output fault mutex")
                    armed.set()
                    os._exit(74)
                if pilot is None:
                    b["reference_intents"] = 1
                    b["reference_intent"] = clocks.service()
                    stats["reference_intents"] += 1
                    write(b)
                    backend.reference(b["positions"], scores, masks)
                    b.update(reference_rows=b["m"], reference_return=clocks.service())
                    stats["reference_rows"] += b["m"]
                else:
                    backend.retain(b["positions"], features, scores, masks, b)
                b["digest"] = hashlib.sha256(
                    scores.tobytes() + masks.tobytes()
                ).digest()[:16]
                del rows, features, scores, masks
                b.update(control_end=clocks.service(), status=STAGE["verified"])
                write(b)
                stats["batches"] += 1
                require(own_rss() <= RSS_CAPS["consumer"], "Consumer own RSS ceiling")
                ring.update(consumer_rss=own_rss())
                samples.add(
                    4,
                    b["status"],
                    b["m"],
                    stats["append_calls"] - writes,
                    cycle,
                    clocks.service(),
                )
            except Exception:
                b.update(
                    terminal=clocks.service(), status=STAGE["failed"], missing_reason=1
                )
                write(b)
                if b.get("output") is None:
                    if scenario == "failed_publication_cleanup":
                        observed = exercise_terminal_preflight(
                            ring, b["m"], clocks.service
                        )
                        _json(Path(directory) / "counter-preflight.json", observed)
                    ring.finish(b["m"], clocks.service, "failed")
                ring.update(error=1)
                raise
        if pilot is not None:
            backend.finish(write)
        if payload_audit is not None:
            require(
                payload_audit["denied_open_attempts"] == 0,
                "Unexpected generated payload access",
            )
        _summary(Path(directory) / "consumer.json", "consumer", clocks, stats)
    except BaseException as exc:
        if pilot is not None:
            from .hdf_consumer import record_initialization_failure

            record_initialization_failure(
                backend,
                Path(directory) / "consumer-final.json",
                exc,
                initialization=False,
            )
        raise
    finally:
        final_start = clocks.service()
        error = phase_during_cleanup(phases, 9, clocks, own_rss())
        try:
            quota.close(output)
        finally:
            errors = close_owned(
                ([backend] if pilot is not None and backend is not None else [])
                + [phases, store, ring]
            )
            try:
                samples.add(
                    7, int(bool(error or errors)), 0, 0, final_start, clocks.service()
                )
            finally:
                samples.close()
            if pilot is not None:
                require(not errors, "Consumer resource close failure")


def run_fixture(
    directory,
    scenario,
    *,
    task52=False,
    quota_root=None,
    heartbeat=None,
    resource_policy=POLICY,
    resource_publish=lambda _: None,
):
    """Generated-only API; operational options are deliberately absent."""
    return _run_pipeline(
        directory,
        scenario,
        task52=task52,
        quota_root=quota_root,
        heartbeat=heartbeat,
        resource_policy=resource_policy,
        resource_publish=resource_publish,
    )


def run_pilot_core(directory, candidate, *, quota_root, heartbeat):
    """Task0054-only entry, validated activation is mandatory before spawning."""
    require(
        candidate in ("pca-v1", "compact-autoencoder-v2") and quota_root is not None,
        "Closed pilot candidate",
    )
    active = json.loads((Path(quota_root) / "pilot/activation.json").read_text())
    require(
        active["task"] == "0054" and active["single_session"],
        "Explicit pilot activation",
    )
    return _run_pipeline(
        directory,
        "pilot54",
        quota_root=quota_root,
        heartbeat=heartbeat,
        pilot=dict(candidate=candidate),
    )


def run_scoped_core(
    directory,
    candidate,
    *,
    quota_root,
    heartbeat,
    context,
    resource_publish=lambda _: None,
):
    """0056 context only; no generated-to-real fallback or legacy activation."""
    from .pilot_context import context_from_request
    from .session_context import SessionFixture57

    if type(context) is SessionFixture57:
        require(
            context.root == quota_root and candidate == context.candidate,
            "Generated session request scope",
        )
        require(
            Path(directory) == Path(context.session) / candidate,
            "Session case location",
        )
        context.validate_location(Path(__file__).resolve().parents[3])
    else:
        request = dict(task="0056", candidate=candidate, context=context)
        context_from_request(quota_root, request, Path(__file__).resolve().parents[3])
    return _run_pipeline(
        directory,
        "pilot54",
        quota_root=quota_root,
        heartbeat=heartbeat,
        pilot=dict(candidate=candidate, context=context),
        resource_policy=POLICY,
        resource_publish=resource_publish,
    )


def _run_pipeline(
    directory,
    scenario,
    *,
    task52=False,
    quota_root=None,
    heartbeat=None,
    pilot=None,
    resource_policy=POLICY,
    resource_publish=lambda _: None,
):
    """Shared actual producer/ring/batching/consumer/record/lifecycle core."""
    if quota_root is not None:
        quota.activate(quota_root)
    from .pilot_context import FixtureContext56
    from .session_context import SessionFixture57

    scoped_fixture = pilot is not None and type(pilot.get("context")) in (
        FixtureContext56,
        SessionFixture57,
    )
    whole_seconds = 15 if scoped_fixture else (30 if pilot else 5)
    entered = time.perf_counter_ns()
    cases = (
        {"pilot54": (64, 500)}
        if pilot is not None
        else (SCENARIOS52 if task52 else SCENARIOS)
    )
    require(scenario in cases, "Unknown fixture, no operational mode")
    directory = Path(directory)
    directory.mkdir(mode=0o700)  # no reuse/overwrite of earlier evidence
    count, rate = cases[scenario]
    clocks = Clocks()
    started = clocks.continuous() - (time.perf_counter_ns() - entered)
    observation = clocks.observation()
    monitor = Monitor(*observation[:2])
    ctx = mp.get_context("spawn")
    lock = ctx.Lock()
    producer_start, consumer_start, stop, armed = (ctx.Event() for _ in range(4))
    sync_inventory = synchronization_inventory(
        lock,
        dict(
            producer_start=producer_start,
            consumer_start=consumer_start,
            stop=stop,
            adversarial_armed=armed,
        ),
    )
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
    fd = quota.open_file(
        directory / "outputs.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600
    )
    quota.truncate(fd, count * 12)
    quota.close(fd)
    producer = ctx.Process(
        name="fixture-producer",
        target=_producer,
        args=(
            shared_name,
            lock,
            producer_start,
            stop,
            str(directory),
            count,
            rate,
            quota_root,
            10 if pilot is not None else 2,
        ),
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
            quota_root,
            pilot,
        ),
    )
    children = [producer, consumer]
    problem = None
    samples = 0
    max_rss = {"supervisor": own_rss(), "producer": 0, "consumer": 0}
    t0 = None
    last_snapshot = None
    resources = TrackerBudget(resource_policy, persist=resource_publish)
    try:
        resources.await_ready(clocks, stop.wait, monitor)
        producer.start()
        if scenario == "failed_start":
            raise RuntimeError("Injected second-child start failure")
        consumer.start()
        while True:
            service, continuous, _ = clocks.observation()
            monitor.observe(service, continuous)
            resources.observe(peaks=max_rss)
            samples += 1
            if heartbeat is not None:
                heartbeat(max_rss)
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
            if pilot is None:
                safety(continuous, started, continuous, continuous, 0)
            else:
                require(continuous - started <= 10_000_000_000, "Pilot setup10s")
            stop.wait(0.005)
        t0 = clocks.service() + 100_000_000
        ring.update(t0=t0)
        producer_start.set()
        while True:
            service, continuous, _ = clocks.observation()
            monitor.observe(service, continuous)
            resources.observe(peaks=max_rss)
            if pilot is None:
                safety(continuous, started, continuous, continuous, 0)
            else:
                require(continuous - started <= 10_000_000_000, "Pilot setup10s")
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
            resources.observe(peaks=max_rss)
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
                if pilot is None:
                    safety(
                        continuous,
                        started,
                        continuous + (scheduler.horizon - service),
                        continuous - (service - last_progress),
                        pending,
                    )
                else:
                    require(
                        continuous - started <= (whole_seconds - 2) * 1_000_000_000,
                        "Pilot cleanup reserve",
                    )
                    require(
                        not consumer.is_alive()
                        or service - last_progress <= 2_000_000_000,
                        "Pilot active operation/control2s",
                    )
                    require(
                        not pending or service <= scheduler.horizon + 5_000_000_000,
                        "Pilot drain5s",
                    )
                for role in ("producer", "consumer"):
                    max_rss[role] = max(max_rss[role], snap[role + "_rss"])
            else:
                require(
                    continuous - started <= (whole_seconds - 2) * 1_000_000_000,
                    "Invocation guard",
                )
            max_rss["supervisor"] = max(max_rss["supervisor"], own_rss())
            if heartbeat is not None:
                heartbeat(max_rss)
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
        if scenario == "failed_publication_cleanup":
            phases.close()
        phase_error = phase_during_cleanup(phases, 7, clocks, own_rss())
        if phase_error:
            problem = problem or "Cleanup phase journal: " + phase_error
        exits = cleanup_children(
            children,
            stop,
            clocks.continuous,
            min(
                started + whole_seconds * 1_000_000_000,
                cleanup_start + 2_000_000_000,
            ),
        )
        if scenario == "failed_publication_cleanup":
            # Children are reaped: corrupt one counter under the actual mutex to
            # exercise Ring._invariant in the guarded cleanup snapshot.
            require(lock.acquire(timeout=0.05), "Cleanup injection mutex")
            try:
                ring._set("pending", 65)
            finally:
                lock.release()
            final_snapshot, snapshot_error = cleanup_snapshot(ring)
        else:
            final_snapshot, snapshot_error = cleanup_snapshot(ring)
        if snapshot_error:
            problem = problem or "Cleanup snapshot: " + snapshot_error
        if final_snapshot is not None:
            last_snapshot = final_snapshot
        if scenario == "failed_publication_cleanup":

            class FailedClose:
                def close(self):
                    ring.close()
                    raise OSError("Injected post-close diagnostic failure")

                def unlink(self):
                    return ring.unlink()

            first_unlink, repeated_unlink, region_errors = release_region(FailedClose())
        else:
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
    invalid_records = []
    event_store = Store(directory / "events.bin", count, "event")
    batch_store = Store(directory / "batches.bin", count, "batch")
    try:
        events = event_store.read_all()
        try:
            batches = batch_store.read_all()
        except ValueError as exc:
            # Invalid publication prevents exact conservation; never substitute old bytes.
            invalid_records.append(str(exc))
            batches = []
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
    if scenario in (
        "pilot54",
        "normal_wrap",
        "normal500",
        "normal2500",
        "normal5000",
        "capacity",
        "contention",
    ):
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
        if scenario in ("normal_wrap", "normal500"):
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
    elif scenario == "torn_publication":
        checks["torn_detected"] = bool(invalid_records) and any(
            e["exitcode"] == 75 for e in exits
        )
    elif scenario == "failed_publication_cleanup":
        checks["publication_failure_observed"] = any(e["exitcode"] == 1 for e in exits)
        preflight_path = directory / "counter-preflight.json"
        checks["terminal_preflight_preserved_credits"] = (
            preflight_path.exists()
            and json.loads(preflight_path.read_text())["credits_preserved"]
        )
        checks["diagnostic_failures_retained"] = bool(
            phase_error and snapshot_error and region_errors
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
            checks["dead_owner_combined"] = final_snapshot is None
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
    require(elapsed <= whole_seconds * 1_000_000_000, "Invocation whole duration")
    report = dict(
        scenario=scenario,
        software_checks=checks,
        software_checks_passed=all(checks.values()),
        phase_observations=phase_counts,
        fixture_only=pilot is None,
        payload_denial_enforced=pilot is None,
        payload_audit_scope="Python open denial throughout generated/producer lifecycle; no HDF/model backend; normal exits also require zero denied attempts",
        arrival_clock_issued=t0 is not None,
        timing_observations=timing_summary(events, batches, cutoff)
        if not invalid_records
        else None,
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
        accounting=accounting if not invalid_records else None,
        accounting_status="invalid_uncertain" if invalid_records else "reconciled",
        invalid_records=invalid_records,
        cleanup_diagnostic_errors=dict(
            phase=phase_error, snapshot=snapshot_error, region=region_errors
        ),
        sample_aggregates={
            role: grouped_samples(directory / (role + "-samples.bin"))
            if (directory / (role + "-samples.bin")).exists()
            else None
            for role in ("producer", "consumer")
        },
        child_summary_available={
            role: (directory / (role + ".json")).exists()
            for role in ("producer", "consumer")
        },
        synthetic_stage_counts=stage_counts if not invalid_records else None,
        observed_final_shared_counters=last_snapshot,
        synchronization_inventory=sync_inventory,
        tracker_resource_observations=resources.summary(),
        cross_process_service_observation=dict(
            parent_interval_ns=[observation[0], cutoff],
            phase_timestamps_within_parent_interval=all(
                observation[0] <= phase["service_ns"] <= cutoff
                for role in ("producer", "consumer")
                for phase in phase_counts[role]
            ),
            uncertainty="spawn/monitor brackets only, not clock equality or calibrated offset",
        ),
        stage_projection_after_stop=stage_projection(batches, cutoff)
        if not invalid_records
        else None,
        stage_projection_at_H=stage_projection(batches, scheduler.horizon)
        if t0 is not None and not invalid_records
        else None,
        synchronization="1spawn mutex +4Events (21SemLocks); OS/native allocation unknown, P2 remains open",
        timestamp_scope="same-host actual fixture process clocks, synthetic read/feature/score stages;no operational certification",
    )
    if quota_root is None:
        _json(directory / "supervisor.json", report)
    require(
        clocks.continuous() - started <= whole_seconds * 1_000_000_000,
        "Invocation including final records",
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
