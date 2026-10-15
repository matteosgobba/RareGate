"""Own-process observations and bounded cleanup, independent of the ring mutex."""

import ctypes
import resource
import sys
import time

from .protocol import require


class Clocks:
    def __init__(self):
        self.service = time.perf_counter_ns
        if sys.platform == "darwin":

            class Timebase(ctypes.Structure):
                _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]

            lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
            base = Timebase()
            require(
                lib.mach_timebase_info(ctypes.byref(base)) == 0 and base.denom > 0,
                "Continuous timebase",
            )
            lib.mach_continuous_time.restype = ctypes.c_uint64
            self.continuous = lambda: (
                lib.mach_continuous_time() * base.numer // base.denom
            )
        else:
            require(
                hasattr(time, "CLOCK_BOOTTIME"), "Suspend-inclusive clock unsupported"
            )
            self.continuous = lambda: time.clock_gettime_ns(time.CLOCK_BOOTTIME)

    def observation(self):
        before = self.service()
        continuous = self.continuous()
        after = self.service()
        return (before + after) // 2, continuous, after - before


def own_rss():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


class Monitor:
    def __init__(self, service, continuous, gap_ns=250_000_000, drift_ns=5_000_000):
        self.last = (service, continuous)
        self.gap_ns, self.drift_ns = gap_ns, drift_ns
        self.maximum_gap = 0

    def observe(self, service, continuous, *, valid=True):
        require(valid, "Primary monitoring failure")
        ds, dc = service - self.last[0], continuous - self.last[1]
        require(ds >= 0 and dc >= 0, "Clock discontinuity")
        self.maximum_gap = max(self.maximum_gap, dc)
        require(dc <= self.gap_ns, "Primary monitor gap")
        require(abs(dc - ds) <= self.drift_ns, "Clock/suspension discrepancy")
        self.last = (service, continuous)


def safety(
    now,
    start,
    horizon,
    last_progress,
    pending,
    *,
    operation_ns=2_000_000_000,
    drain_ns=5_000_000_000,
    invocation_ns=5_000_000_000,
    cleanup_ns=2_000_000_000,
):
    require(
        now - start < invocation_ns - cleanup_ns, "Fixture deadline (cleanup reserved)"
    )
    require(
        not pending or now - last_progress <= operation_ns,
        "Operation/no-progress timeout",
    )
    require(not pending or now <= horizon + drain_ns, "Drain timeout")


def cleanup_children(children, stop, continuous, deadline_ns):
    """No shared lock or final child acknowledgement; failed starts are legal inputs."""
    stop.set()
    actions = []
    for p in children:
        if p.pid is None:
            actions.append(
                {"name": p.name, "started": False, "normal": False, "exitcode": None}
            )
            p.close()
            continue
        p.join(timeout=max(0, min(0.03, (deadline_ns - continuous()) / 1e9)))
        forced = False
        if p.is_alive():
            p.terminate()
            forced = True
            p.join(timeout=max(0, min(0.15, (deadline_ns - continuous()) / 1e9)))
        if p.is_alive():
            p.kill()
            p.join(timeout=max(0, (deadline_ns - continuous()) / 1e9))
        leaked = p.is_alive()
        actions.append(
            {
                "name": p.name,
                "started": True,
                "normal": not forced and p.exitcode == 0,
                "forced": forced,
                "leaked": leaked,
                "exitcode": p.exitcode,
            }
        )
        if not leaked:
            p.close()
    return actions


def phase_during_cleanup(phases, code, clocks, rss):
    """Diagnostics must never veto child/resource cleanup; caller invalidates run."""
    try:
        phases.append(code, clocks, rss)
        return None
    except (OSError, ValueError, TypeError) as exc:
        return type(exc).__name__ + ": " + str(exc)


def release_region(region):
    """Close and unlink are independent, including failed close and repeated unlink."""
    errors = []
    try:
        region.close()
    except (OSError, ValueError, BufferError) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
    first = again = False
    try:
        first = region.unlink()
        again = region.unlink()
    except (OSError, ValueError) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
    return first, again, errors


def cleanup_snapshot(ring):
    """Optional accounting observation cannot prevent required region release."""
    try:
        return ring.snapshot(), None
    except (ValueError, OSError) as exc:
        return None, type(exc).__name__ + ": " + str(exc)


def synchronization_inventory(lock, events):
    """Count actual runtime SemLock objects; this does not measure backing bytes."""
    sems = [lock._semlock] if lock is not None else []
    roles = []
    for purpose, event in events.items():
        condition = event._cond
        owned = [
            condition._lock._semlock,
            condition._sleeping_count._semlock,
            condition._woken_count._semlock,
            condition._wait_semaphore._semlock,
            event._flag._semlock,
        ]
        sems.extend(owned)
        roles.append(dict(purpose=purpose, actual_SemLocks=len(owned)))
    require(len({s.handle for s in sems}) == len(sems), "Distinct owned SemLocks")
    return dict(
        mutexes=int(lock is not None),
        events=roles,
        actual_SemLocks=len(sems),
        kernel_native_bytes=None,
        allowance_bytes=65536,
        allowance_proved=False,
        ownership="supervisor-created spawn primitives, child shared references; runtime finalizers/tracker unlink names",
    )
