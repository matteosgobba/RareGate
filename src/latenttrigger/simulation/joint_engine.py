"""Additive variable-service FIFO engine; Task0037 engine remains unchanged."""

import math
from collections import deque
from dataclasses import dataclass
from fractions import Fraction

MAX_TIME = 2**63 - 1
MAX_EVENTS = 5000
THRESHOLDS = (0.9, 0.95, 0.99, 0.999)
THRESHOLD_KEYS = ("0900", "0950", "0990", "0999")


def integer(value, name, *, minimum=0, maximum=MAX_TIME):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"Invalid finite integer {name}")
    return value


def add_time(a, b):
    return integer(a + b, "time addition")


@dataclass(frozen=True)
class Trace:
    arrivals: tuple[int, ...]
    scores: tuple[float, ...]

    def validate(self):
        if type(self.arrivals) is not tuple or type(self.scores) is not tuple:
            raise ValueError("Immutable source tuples")
        integer(len(self.arrivals), "event count", minimum=1, maximum=MAX_EVENTS)
        if len(self.arrivals) != len(self.scores):
            raise ValueError("Arrival/score alignment")
        previous = 0
        for arrival, score in zip(self.arrivals, self.scores, strict=True):
            integer(arrival, "arrival")
            if arrival < previous:
                raise ValueError("Source order must be nondecreasing")
            if (
                type(score) is not float
                or not math.isfinite(score)
                or not 0 <= score < 1
            ):
                raise ValueError("Finite FP64 toy score in [0,1)")
            previous = arrival
        return self


@dataclass(frozen=True)
class ReplayPolicy:
    batch: int
    timeout_ns: int
    capacity: int
    deadline_ns: int

    def validate(self):
        integer(self.batch, "batch", minimum=1, maximum=1024)
        integer(self.capacity, "capacity", minimum=1, maximum=1024)
        integer(self.timeout_ns, "timeout")
        integer(self.deadline_ns, "deadline")
        return self


def describe(values):
    """Linear quantiles interpolated from integer ns with rational rank positions."""
    n = len(values)
    if not n:
        return dict(
            count=0, mean=None, min=None, p50=None, p95=None, p99=None, max=None
        )
    ordered = sorted(values)

    def quantile(prob):
        rank = Fraction(prob) * (n - 1)
        lo = rank.numerator // rank.denominator
        fraction = rank - lo
        return float(
            ordered[lo] + fraction * (ordered[min(lo + 1, n - 1)] - ordered[lo])
        )

    return dict(
        count=n,
        mean=sum(values) / n,
        min=ordered[0],
        max=ordered[-1],
        p50=quantile("0.5"),
        p95=quantile("0.95"),
        p99=quantile("0.99"),
    )


def simulate(
    trace, policy, q, variant="cyclic", *, poll=lambda: None, completed_event=None
):
    """Completion, source-ordered arrivals, then dispatch at each timestamp.

    Optional completion observer exists for small test fixtures; sweep never exports it.
    Dispatch wait combines busy-server queue wait and idle batch wait.
    """
    trace.validate()
    policy.validate()
    service = Assignment(q, variant)
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
            active_duration = service.next()
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


def validate_result(r, policy):
    """Conservation and bounded accounting; no missing pending events accepted."""
    for name in (
        "generated",
        "admitted",
        "overflow_dropped",
        "completed",
        "pending",
        "completed_at_horizon",
        "waiting_at_horizon",
        "in_service_at_horizon",
        "pending_at_horizon",
        "batches",
        "full_batches",
        "partial_batches",
        "modeled_slots",
        "unused_slots",
        "max_outstanding",
        "max_waiting",
        "deadline_misses_processed",
        "on_time_completed",
        "horizon_ns",
        "end_ns",
        "drain_ns",
        "busy_ns",
        "busy_to_horizon_ns",
    ):
        integer(r[name], name)
    if not (
        r["generated"] == r["completed"] + r["overflow_dropped"]
        and r["admitted"] == r["completed"]
        and r["pending"] == 0
        and r["completed_at_horizon"] + r["pending_at_horizon"] == r["admitted"]
        and r["pending_at_horizon"]
        == r["waiting_at_horizon"] + r["in_service_at_horizon"]
        and r["batches"] == r["full_batches"] + r["partial_batches"]
        and r["modeled_slots"] == policy.batch * r["batches"]
        and r["unused_slots"] == r["modeled_slots"] - r["completed"]
        and r["busy_ns"] == r["assigned_duration_sum_ns"]
        and r["batches"] == r["dispatch_count"]
        and r["completed"]
        == r["full_batches"] * policy.batch + r["partial_useful_events"]
        and r["partial_charged_slots"] == r["partial_batches"] * policy.batch
        and r["partial_unused_slots"]
        == r["partial_charged_slots"] - r["partial_useful_events"]
        and r["unused_slots"] == r["partial_unused_slots"]
        and 0 <= r["partial_service_busy_ns"] <= r["busy_ns"]
        and 0 <= r["busy_to_horizon_ns"] <= min(r["busy_ns"], r["horizon_ns"])
        and r["busy_ns"] <= r["end_ns"]
        and r["max_outstanding"] <= policy.capacity
        and r["max_waiting"] <= r["max_outstanding"]
        and r["on_time_completed"] + r["deadline_misses_processed"] == r["completed"]
        and r["dispatch_wait_ns_count"] == r["latency_ns_count"] == r["completed"]
        and r["end_ns"] == r["horizon_ns"] + r["drain_ns"]
    ):
        raise ValueError("Conservation/capacity/service mismatch")
    previous = r["completed"]
    for key in THRESHOLD_KEYS:
        n, rejected, late = (
            r[f"toy_{key}_{suffix}"]
            for suffix in ("selected", "rejected", "deadline_misses_selected")
        )
        for value in (
            n,
            rejected,
            late,
            r[f"toy_{key}_selected_to_horizon"],
            r[f"toy_{key}_rejected_to_horizon"],
        ):
            integer(value, "toy count")
        if not (0 <= late <= n <= previous and n + rejected == r["completed"]):
            raise ValueError("Non-nested toy decisions")
        if (
            r[f"toy_{key}_selected_to_horizon"] + r[f"toy_{key}_rejected_to_horizon"]
            != r["completed_at_horizon"]
        ):
            raise ValueError("Horizon toy counts")
        previous = n
    return r


class Assignment:
    """Dispatch-only cursor; counts refer to original sample indices, never events."""

    def __init__(self, q, variant):
        import hashlib
        import struct

        if type(q) is not tuple or len(q) != 20:
            raise ValueError("Immutable20service samples")
        for value in q:
            integer(value, "positive integer service", minimum=1)
        if variant not in ("cyclic", "constant", "reverse", "rotation10"):
            raise ValueError("Closed assignment variant")
        self.q, self.variant = q, variant
        self.mean = (sum(q) + 19) // 20
        self.fingerprint = hashlib.sha256(
            b"".join(struct.pack("<q", v) for v in q)
        ).hexdigest()
        self.j = self.total = 0
        self.counts = [0] * 20
        self.minimum = self.maximum = None

    def next(self):
        index = self.j % 20
        if self.variant == "reverse":
            index = 19 - index
        elif self.variant == "rotation10":
            index = (index + 10) % 20
        value = self.mean if self.variant == "constant" else self.q[index]
        if self.variant != "constant":
            self.counts[index] += 1
        self.j += 1
        self.total = add_time(self.total, value)
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)
        return value

    def report(self):
        expected = (
            self.j * self.mean
            if self.variant == "constant"
            else sum(v * n for v, n in zip(self.q, self.counts, strict=True))
        )
        if self.total != expected or sum(self.counts) != (
            0 if self.variant == "constant" else self.j
        ):
            raise ValueError("Original sample count/sum identity")
        return dict(
            vector_sha256=self.fingerprint,
            assignment=self.variant,
            original_sample_assignment_counts=",".join(map(str, self.counts)),
            dispatch_count=self.j,
            complete_cycles=self.j // 20,
            cycle_remainder=self.j % 20,
            final_cursor=self.j % 20,
            assigned_duration_sum_ns=self.total,
            assigned_duration_min_ns=self.minimum,
            assigned_duration_max_ns=self.maximum,
            assigned_duration_mean_ns=self.total / self.j if self.j else None,
            constant_mean_ceil_ns=self.mean,
            source_mean_ns=sum(self.q) / 20,
            constant_rounding_excess_twentieth_ns=20 * self.mean - sum(self.q),
        )
