"""Version0055: typed own-tracker observations, explicit joint resource policy."""

import ctypes
import errno
import os
import sys
import time
from dataclasses import asdict, dataclass
from multiprocessing import resource_tracker

from .protocol import require
from .supervision import own_rss


@dataclass(frozen=True)
class ResourcePolicy:
    name: str = "joint_inner_owned_tracker_v1"
    inner_tracker_bytes: int = 80 * 1024**2
    outer_bytes: int = 48 * 1024**2
    producer_bytes: int = 64 * 1024**2
    consumer_bytes: int = 1024**3
    aggregate_bytes: int = 1216 * 1024**2
    resident_bytes: int = 512 * 1024**2
    tracker_startup_ns: int = 250_000_000

    def validate(self):
        require(
            asdict(self) == asdict(ResourcePolicy()),
            "Exact validated joint resource policy",
        )
        return self


POLICY = ResourcePolicy()


class ResourceFailure(ValueError):
    def __init__(self, reason, evidence):
        super().__init__(reason)
        self.evidence = evidence


class ProcTaskInfo(ctypes.Structure):
    # Installed sys/proc_info.h:6u64+12i32,96B; resident offset8, units bytes.
    _fields_ = [
        (n, ctypes.c_uint64)
        for n in (
            "virtual_size",
            "resident_size",
            "total_user",
            "total_system",
            "threads_user",
            "threads_system",
        )
    ]
    _fields_ += [
        (n, ctypes.c_int32)
        for n in (
            "policy",
            "faults",
            "pageins",
            "cow_faults",
            "messages_sent",
            "messages_received",
            "syscalls_mach",
            "syscalls_unix",
            "csw",
            "threadnum",
            "numrunning",
            "priority",
        )
    ]


def query_pid(pid):
    """Internal only: caller supplies its own PID or runtime-owned tracker PID."""
    if sys.platform != "darwin":
        return dict(
            state="unsupported",
            method="proc_pidinfo_PROC_PIDTASKINFO",
            reason="Darwin ABI required",
            rss_bytes=None,
        )
    library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    fn = library.proc_pidinfo
    fn.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    fn.restype = ctypes.c_int
    record = ProcTaskInfo()
    ctypes.set_errno(0)
    returned = fn(pid, 4, 0, ctypes.byref(record), ctypes.sizeof(record))
    error = ctypes.get_errno()
    return interpret_record(returned, error, record.resident_size)


def interpret_record(returned, error, resident):
    result = dict(
        method="proc_pidinfo_PROC_PIDTASKINFO",
        expected_length=96,
        returned_length=returned,
        errno=error,
        raw_resident_bytes=resident,
        rss_bytes=None,
        units="bytes",
    )
    if returned != 96:
        result.update(
            state="exited" if error in (errno.ESRCH, errno.ENOENT) else "query_error",
            reason="OS return length does not match96B",
        )
    elif error:
        result.update(state="query_error", reason="OS errno with complete record")
    elif type(resident) is not int or resident < 0:
        result.update(state="query_error", reason="Invalid resident value")
    elif resident == 0:
        result.update(
            state="startup_pending",
            reason="OS returned zero; no valid positive RSS yet",
        )
    else:
        result.update(state="observed", rss_bytes=resident)
    return result


def owned_relationship():
    tracker = resource_tracker._resource_tracker
    return dict(
        pid=tracker._pid,
        fd=tracker._fd,
        owner_pid=os.getpid(),
        ownership="this subject multiprocessing.resource_tracker._resource_tracker",
    )


class TrackerBudget:
    def __init__(
        self,
        policy=POLICY,
        *,
        query=query_pid,
        relationship=owned_relationship,
        clock=time.monotonic_ns,
        persist=lambda _: None,
    ):
        self.policy = policy.validate()
        self.query, self.relationship, self.clock, self.persist = (
            query,
            relationship,
            clock,
            persist,
        )
        self.owner = os.getpid()
        self.ready_pid = None
        self.started_ns = None
        self.first_failure = None
        self.samples = []
        self.last = None
        self.count = self.pending_count = 0
        self.peak_tracker = 0
        self.maximum_joint = 0

    def observe(self, *, required=True, peaks=None):
        now = self.clock()
        relation = self.relationship()
        pid = relation.get("pid")
        if type(now) is not int or now < 0:
            observation = dict(
                state="query_error",
                reason="Unknown/invalid monotonic timestamp",
                rss_bytes=None,
            )
        elif relation.get("owner_pid") != self.owner or os.getpid() != self.owner:
            observation = dict(
                state="query_error", reason="Ownership process mismatch", rss_bytes=None
            )
        elif pid is None:
            observation = dict(
                state="exited" if self.ready_pid else "not_started",
                rss_bytes=None,
                reason="No runtime-owned tracker PID",
            )
        elif (
            type(pid) is not int
            or pid <= 0
            or pid == self.owner
            or relation.get("fd") is None
        ):
            observation = dict(
                state="query_error",
                reason="Invalid owned tracker PID/fd",
                rss_bytes=None,
            )
        elif self.ready_pid is not None and pid != self.ready_pid:
            observation = dict(
                state="query_error", reason="Owned tracker PID changed", rss_bytes=None
            )
        else:
            try:
                observation = self.query(pid)
            except (OSError, ValueError) as exc:
                observation = dict(
                    state="query_error",
                    reason=str(exc)[:300],
                    errno=getattr(exc, "errno", None),
                    rss_bytes=None,
                )
        observation = dict(
            observation,
            pid=pid,
            owner_pid=self.owner,
            ownership=relation.get("ownership"),
            monotonic_ns=now,
        )
        if observation["state"] == "observed":
            self.ready_pid = pid
            self.peak_tracker = max(self.peak_tracker, observation["rss_bytes"])
        self.count += 1
        self.pending_count += int(
            observation["state"] in ("not_started", "startup_pending")
        )
        observation["inner_lifetime_peak_RSS_bytes"] = own_rss()
        observation["tracker_observed_peak_RSS_bytes"] = self.peak_tracker or None
        observation["joint_conservative_bytes"] = (
            own_rss() + self.peak_tracker if self.ready_pid else None
        )
        if observation["joint_conservative_bytes"] is not None:
            self.maximum_joint = max(
                self.maximum_joint, observation["joint_conservative_bytes"]
            )
        self.last = observation
        if len(self.samples) < 32:
            self.samples.append(observation)
        failure = None
        if required and observation["state"] != "observed":
            failure = "Required tracker observation invalid"
        if (
            observation["joint_conservative_bytes"] is not None
            and observation["joint_conservative_bytes"]
            > self.policy.inner_tracker_bytes
        ):
            failure = "Joint inner-plus-owned-tracker80MiB exceeded"
        peaks = peaks or {}
        charged = (
            observation["joint_conservative_bytes"]
            if self.ready_pid
            else self.policy.inner_tracker_bytes
        )
        observation["charge_is_reservation_without_measurement"] = (
            self.ready_pid is None
        )
        total = (
            charged
            + self.policy.outer_bytes
            + peaks.get("producer", 0)
            + peaks.get("consumer", 0)
        )
        observation["conservative_role_charge_bytes"] = total
        if total > self.policy.resident_bytes or total > self.policy.aggregate_bytes:
            failure = "Summed resident/aggregate guard"
        if failure and self.first_failure is None:
            self.first_failure = dict(reason=failure, observation=observation)
        # Preserve the value/typed failure before applying a rejection.
        try:
            self.persist(self.summary())
        except (OSError, ValueError) as exc:
            report_failure = dict(type=type(exc).__name__, message=str(exc)[:300])
            self.last["report_failure"] = report_failure
            if self.first_failure is None:
                self.first_failure = dict(
                    reason="Tracker diagnostic publication failed",
                    observation=observation,
                )
            raise ResourceFailure(
                failure or "Tracker diagnostic publication failed", self.first_failure
            ) from exc
        if failure:
            raise ResourceFailure(failure, self.first_failure or observation)
        return observation

    def await_ready(self, clocks, wait, monitor):
        self.started_ns = clocks.continuous()
        while True:
            service, continuous, _ = clocks.observation()
            monitor.observe(service, continuous)
            value = self.observe(required=False)
            after_query = clocks.continuous()
            elapsed = after_query - self.started_ns
            value["startup_elapsed_ns"] = elapsed
            service_after, continuous_after, _ = clocks.observation()
            monitor.observe(service_after, continuous_after)
            if elapsed > self.policy.tracker_startup_ns:
                self.first_failure = dict(
                    reason="Tracker query returned after startup deadline",
                    observation=value,
                    elapsed_ns=elapsed,
                )
                self.persist(self.summary())
                raise ResourceFailure(
                    "Tracker startup observation late", self.first_failure
                )
            if value["state"] == "observed":
                return value
            if (
                value["state"] not in ("not_started", "startup_pending")
                or continuous - self.started_ns >= self.policy.tracker_startup_ns
            ):
                self.first_failure = dict(
                    reason="Tracker startup deadline/state",
                    observation=value,
                    elapsed_ns=continuous - self.started_ns,
                )
                self.persist(self.summary())
                raise ResourceFailure(
                    "Tracker startup observation failed closed", self.first_failure
                )
            wait(
                min(
                    0.005,
                    (self.policy.tracker_startup_ns - (continuous - self.started_ns))
                    / 1e9,
                )
            )

    def summary(self):
        return dict(
            policy=asdict(self.policy),
            observation_count=self.count,
            pending_count=self.pending_count,
            first_samples=self.samples,
            last=self.last,
            first_failure=self.first_failure,
            ready_pid=self.ready_pid,
            maximum_joint_charge_bytes=self.maximum_joint,
            tracker_peak_bytes=self.peak_tracker or None,
            startup_started_ns=self.started_ns,
            interpretation="current tracker RSS + inner lifetime peak; conservative peaks/overlapping pages, not unique simultaneous RAM or native workspace",
        )


_HEARTBEAT_STATE = None


def heartbeat_joint(peaks, policy=POLICY):
    global _HEARTBEAT_STATE
    policy.validate()
    if _HEARTBEAT_STATE is None or _HEARTBEAT_STATE.owner != os.getpid():
        _HEARTBEAT_STATE = TrackerBudget(policy)
    required = (
        _HEARTBEAT_STATE.ready_pid is not None
        or owned_relationship()["pid"] is not None
    )
    result = _HEARTBEAT_STATE.observe(required=required, peaks=peaks)
    return (
        result["joint_conservative_bytes"]
        if result["state"] == "observed"
        else policy.inner_tracker_bytes
    )
