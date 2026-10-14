"""Occupancy-dependent assignment; unchanged FIFO mechanics in a separate engine."""

from collections import deque

from latenttrigger.simulation import occupancy_protocol as p
from latenttrigger.simulation.joint_engine import (
    THRESHOLD_KEYS,
    THRESHOLDS,
    add_time,
    describe,
    integer,
    validate_result,
)
from latenttrigger.simulation.occupancy_source import PairedVector


def anchor(b, m, mapping):
    integer(b, "nominal B", minimum=1, maximum=128)
    integer(m, "actual dispatch rows", minimum=1, maximum=b)
    p.require(b in p.ANCHORS and mapping in p.MAPPINGS, "Closed anchor mapping")
    return (
        next(k for k in p.ANCHORS[b] if k >= m)
        if mapping == "next_anchor"
        else next(k for k in reversed(p.ANCHORS[b]) if k <= m)
    )


class Assignment:
    def __init__(self, vectors, b, mapping, billing):
        p.require(
            mapping in p.MAPPINGS and billing in p.BILLINGS and b in p.ANCHORS,
            "Closed variant",
        )
        p.require(
            set(vectors) == set(p.ANCHORS[b])
            and all(
                isinstance(v, PairedVector)
                and v.B == b
                and v.k == k
                and type(v.pairs) is tuple
                and len(v.pairs) == 20
                for k, v in vectors.items()
            ),
            "Complete immutable anchors",
        )
        for vector in vectors.values():
            for pair in vector.pairs:
                p.require(type(pair) is tuple and len(pair) == 2, "Immutable pair")
                for duration in pair:
                    integer(duration, "positive duration", minimum=1)
        self.vectors, self.b, self.mapping, self.billing = vectors, b, mapping, billing
        self.cursors = {k: 0 for k in vectors}
        self.counts = {k: [0] * 20 for k in vectors}
        self.occupancies = {}
        self.total = self.j = 0
        self.minimum = self.maximum = None

    def next(self, m):
        k = anchor(self.b, m, self.mapping)
        index = self.cursors[k] % 20
        duration = self.vectors[k].pairs[index][p.BILLINGS.index(self.billing)]
        self.cursors[k] += 1
        self.counts[k][index] += 1
        self.j += 1
        self.total = add_time(self.total, duration)
        self.minimum = duration if self.minimum is None else min(self.minimum, duration)
        self.maximum = duration if self.maximum is None else max(self.maximum, duration)
        row = self.occupancies.setdefault(
            m,
            dict(
                m=m,
                k=k,
                batches=0,
                events=0,
                busy_ns=0,
                exact_point=int(k == m),
                source_natural_actual_rows=k,
                source_natural_service_B=self.vectors[k].natural_service_B,
                source_control_actual_rows=self.b,
                source_control_service_B=self.b,
                modeled_rows=0,
                k_minus_m=k - m,
                anchor_minus_actual_rows=0,
                modeled_minus_actual_rows=0,
            ),
        )
        modeled = k if self.billing == "natural_anchor" else self.b
        row["batches"] += 1
        row["events"] += m
        row["busy_ns"] = add_time(row["busy_ns"], duration)
        row["modeled_rows"] += modeled
        row["anchor_minus_actual_rows"] += k - m
        row["modeled_minus_actual_rows"] += modeled - m
        return duration

    def audit(self):
        result = []
        for k, v in self.vectors.items():
            counts = self.counts[k]
            j = self.cursors[k]
            side = p.BILLINGS.index(self.billing)
            busy = sum(pair[side] * n for pair, n in zip(v.pairs, counts, strict=True))
            p.require(
                counts == [j // 20 + int(i < j % 20) for i in range(20)],
                "Independent anchor cycle",
            )
            result.append(
                dict(
                    k=k,
                    vector_sha256=v.sha256,
                    pair_order_sha256=p.digest(v.pair_ids),
                    assignment_counts=",".join(map(str, counts)),
                    dispatch_count=j,
                    cursor_wraps=j // 20,
                    cursor_remainder=j % 20,
                    unused_samples=sum(n == 0 for n in counts),
                    assigned_busy_ns=busy,
                    assigned_mean_ns=busy / j if j else None,
                )
            )
        p.require(
            sum(r["assigned_busy_ns"] for r in result) == self.total,
            "Anchor dot product busy",
        )
        return result

    def report(self):
        exact = [r for r in self.occupancies.values() if r["exact_point"]]
        mapped = [r for r in self.occupancies.values() if not r["exact_point"]]
        p.require(
            sum(r["batches"] for r in self.occupancies.values()) == self.j
            and sum(r["busy_ns"] for r in self.occupancies.values()) == self.total,
            "Occupancy service conservation",
        )
        result = dict(
            dispatch_count=self.j,
            assigned_duration_sum_ns=self.total,
            assigned_duration_mean_ns=self.total / self.j if self.j else None,
            assigned_duration_min_ns=self.minimum,
            assigned_duration_max_ns=self.maximum,
            modeled_row_work=sum(r["modeled_rows"] for r in self.occupancies.values()),
            anchor_minus_actual_rows=sum(
                r["anchor_minus_actual_rows"] for r in self.occupancies.values()
            ),
            modeled_minus_actual_rows=sum(
                r["modeled_minus_actual_rows"] for r in self.occupancies.values()
            ),
        )
        for label, rows in (("exact", exact), ("mapped", mapped)):
            for name in ("batches", "events", "busy_ns"):
                result[label + "_" + name] = sum(r[name] for r in rows)
        for name, total in (
            ("batches", self.j),
            ("events", sum(r["events"] for r in self.occupancies.values())),
            ("busy_ns", self.total),
        ):
            result["mapped_" + name + "_fraction"] = (
                result["mapped_" + name] / total if total else None
            )
        return result


def simulate(trace, policy, service, *, poll=lambda: None, completed_event=None):
    """Completion, source-ordered arrivals, then dispatch at each timestamp.

    Optional completion observer exists for small test fixtures; sweep never exports it.
    Dispatch wait combines busy-server queue wait and idle batch wait.
    """
    trace.validate()
    policy.validate()
    arrivals, scores = trace.arrivals, trace.scores
    horizon = arrivals[-1]
    waiting, active = deque(), []
    finish = dispatch = None
    source = now = admitted = dropped = completed = 0
    max_outstanding = max_waiting = busy = busy_h = completed_h = 0
    full = partial = misses = 0
    partial_useful = partial_busy = 0
    active_duration = None
    waits, latencies, batch_sizes = [], [], []
    selected = [0] * 4
    selected_h = [0] * 4
    selected_misses = [0] * 4
    at_h = None
    ticks = 0
    poll()
    while source < len(arrivals) or waiting or active:
        times = []
        if source < len(arrivals):
            times.append(arrivals[source])
        if active:
            times.append(finish)
        elif waiting:
            times.append(max(now, add_time(arrivals[waiting[0]], policy.timeout_ns)))
        tick = min(times)
        if tick < now:
            raise ValueError("Virtual clock regressed")
        now = tick
        ticks += 1
        if ticks % 1024 == 0:
            poll()
        if active and finish == now:
            for identity in active:
                wait = dispatch - arrivals[identity]
                latency = now - arrivals[identity]
                if wait < 0 or latency != wait + active_duration:
                    raise ValueError("Latency accounting")
                waits.append(wait)
                latencies.append(latency)
                completed += 1
                miss = latency > policy.deadline_ns
                misses += miss
                completed_h += now <= horizon
                decisions = tuple(scores[identity] > t for t in THRESHOLDS)
                for k, decision in enumerate(decisions):
                    selected[k] += decision
                    selected_h[k] += decision and now <= horizon
                    selected_misses[k] += decision and miss
                if completed_event is not None:
                    completed_event(identity, dispatch, now, decisions)
            active = []
            finish = dispatch = None
        while source < len(arrivals) and arrivals[source] == now:
            if len(waiting) + len(active) < policy.capacity:
                waiting.append(source)
                admitted += 1
                max_waiting = max(max_waiting, len(waiting))
                max_outstanding = max(max_outstanding, len(waiting) + len(active))
            else:
                dropped += 1
            source += 1
        if (
            not active
            and waiting
            and (
                len(waiting) >= policy.batch
                or now >= add_time(arrivals[waiting[0]], policy.timeout_ns)
            )
        ):
            active = [waiting.popleft() for _ in range(min(policy.batch, len(waiting)))]
            dispatch = now
            active_duration = service.next(len(active))
            finish = add_time(now, active_duration)
            size = len(active)
            batch_sizes.append(size)
            full += size == policy.batch
            partial += size < policy.batch
            busy = add_time(busy, active_duration)
            if size < policy.batch:
                partial_useful += size
                partial_busy = add_time(partial_busy, active_duration)
            busy_h += max(0, min(finish, horizon) - min(dispatch, horizon))
        if now == horizon and at_h is None:
            at_h = dict(
                completed_at_horizon=completed_h,
                waiting_at_horizon=len(waiting),
                in_service_at_horizon=len(active),
                pending_at_horizon=len(waiting) + len(active),
            )
    poll()
    if at_h is None or admitted != completed or len(arrivals) != dropped + completed:
        raise ValueError("Incomplete or nonconserved drain")
    batches = full + partial
    slots = batches * policy.batch
    result = dict(
        generated=len(arrivals),
        admitted=admitted,
        overflow_dropped=dropped,
        completed=completed,
        pending=0,
        **at_h,
        horizon_ns=horizon,
        end_ns=now,
        drain_ns=now - horizon,
        realized_arrival_events_per_second=len(arrivals) * 1e9 / horizon
        if horizon
        else None,
        completed_throughput_to_horizon_events_per_second=completed_h * 1e9 / horizon
        if horizon
        else None,
        completed_full_drain_events_per_second=completed * 1e9 / now if now else None,
        drain_only_completed_events_per_second=(completed - completed_h)
        * 1e9
        / (now - horizon)
        if now > horizon
        else None,
        overflow_fraction=dropped / len(arrivals),
        max_outstanding=max_outstanding,
        max_waiting=max_waiting,
        busy_ns=busy,
        busy_to_horizon_ns=busy_h,
        utilization_to_horizon=busy_h / horizon if horizon else None,
        utilization_full_drain=busy / now if now else None,
        batches=batches,
        full_batches=full,
        partial_batches=partial,
        modeled_slots=slots,
        unused_slots=slots - completed,
        slot_utilization=completed / slots if slots else None,
        deadline_misses_processed=misses,
        deadline_miss_fraction_processed=misses / completed if completed else None,
        on_time_completed=completed - misses,
        overflow_or_late_fraction_generated=(dropped + misses) / len(arrivals),
    )
    for name, values in (
        ("dispatch_wait_ns", waits),
        ("latency_ns", latencies),
        ("batch_actual_size", batch_sizes),
    ):
        result.update({name + "_" + k: v for k, v in describe(values).items()})
    for k, key in enumerate(THRESHOLD_KEYS):
        result.update(
            {
                f"toy_{key}_selected": selected[k],
                f"toy_{key}_rejected": completed - selected[k],
                f"toy_{key}_selected_to_horizon": selected_h[k],
                f"toy_{key}_rejected_to_horizon": completed_h - selected_h[k],
                f"toy_{key}_deadline_misses_selected": selected_misses[k],
                f"toy_{key}_deadline_miss_fraction_selected": selected_misses[k]
                / selected[k]
                if selected[k]
                else None,
            }
        )
    result.update(service.report())
    result.update(
        partial_useful_events=partial_useful,
        partial_charged_slots=partial * policy.batch,
        partial_unused_slots=partial * policy.batch - partial_useful,
        partial_slot_utilization=partial_useful / (partial * policy.batch)
        if partial
        else None,
        partial_service_busy_ns=partial_busy,
    )
    validate_result(result, policy)
    return result
