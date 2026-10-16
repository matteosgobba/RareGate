"""Integer-time, one-server FIFO scheduling and finite-workload statistics."""

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
class Policy:
    batch: int
    timeout_ns: int
    capacity: int
    service_ns: int
    deadline_ns: int

    def validate(self):
        integer(self.batch, "batch", minimum=1, maximum=1024)
        integer(self.capacity, "capacity", minimum=1, maximum=1024)
        integer(self.timeout_ns, "timeout")
        integer(self.service_ns, "service", minimum=1)
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


def simulate(trace, policy, *, poll=lambda: None, completed_event=None):
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
                if wait < 0 or latency != wait + policy.service_ns:
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
            finish = add_time(now, policy.service_ns)
            size = len(active)
            batch_sizes.append(size)
            full += size == policy.batch
            partial += size < policy.batch
            busy += policy.service_ns
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
        and r["busy_ns"] == policy.service_ns * r["batches"]
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


RESULT_FIELDS = (
    set(
        (
            "generated admitted overflow_dropped completed pending completed_at_horizon "
            "waiting_at_horizon in_service_at_horizon pending_at_horizon horizon_ns end_ns "
            "drain_ns realized_arrival_events_per_second completed_throughput_to_horizon_events_per_second "
            "completed_full_drain_events_per_second drain_only_completed_events_per_second "
            "overflow_fraction max_outstanding max_waiting busy_ns busy_to_horizon_ns "
            "utilization_to_horizon utilization_full_drain batches full_batches partial_batches "
            "modeled_slots unused_slots slot_utilization deadline_misses_processed "
            "deadline_miss_fraction_processed on_time_completed overflow_or_late_fraction_generated"
        ).split()
    )
    | {
        prefix + "_" + suffix
        for prefix in ("dispatch_wait_ns", "latency_ns", "batch_actual_size")
        for suffix in ("count", "mean", "min", "max", "p50", "p95", "p99")
    }
    | {
        f"toy_{key}_{suffix}"
        for key in THRESHOLD_KEYS
        for suffix in (
            "selected",
            "rejected",
            "selected_to_horizon",
            "rejected_to_horizon",
            "deadline_misses_selected",
            "deadline_miss_fraction_selected",
        )
    }
)
