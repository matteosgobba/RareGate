"""Task0030-only continuous timing, scoped idle assertion and process lifecycle."""

import ctypes
import os
import re
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import UTC, datetime

from raregate.evaluation.guard import GuardError, parent_check


class Timebase(ctypes.Structure):
    _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]


def ticks_ns(ticks, numer, denom):
    if type(ticks) is not int or ticks < 0 or not numer or not denom:
        raise ValueError("Invalid native clock/timebase")
    return ticks * numer // denom  # Integer multiplication BEFORE division/float.


class ContinuousClock:
    def __init__(self):
        if sys.platform != "darwin":
            raise GuardError("Actual macOS continuous bindings required")
        lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        lib.mach_timebase_info.argtypes = [ctypes.POINTER(Timebase)]
        lib.mach_timebase_info.restype = ctypes.c_int
        tb = Timebase()
        if (
            lib.mach_timebase_info(ctypes.byref(tb)) != 0
            or not tb.numer
            or not tb.denom
        ):
            raise GuardError("Unavailable native timebase")
        self.numer, self.denom = tb.numer, tb.denom
        self.read = lib.mach_continuous_time
        self.read.argtypes, self.read.restype = [], ctypes.c_uint64

    def ns(self):
        return ticks_ns(int(self.read()), self.numer, self.denom)

    def __call__(self):
        return self.ns() / 1_000_000_000

    def snapshot(self):
        return dict(
            UTC=datetime.now(UTC).isoformat(),
            ordinary_monotonic_seconds=time.monotonic(),
            continuous_nanoseconds=self.ns(),
            continuous_seconds=self(),
            deadline_clock="mach_continuous_time;integer ticks*numer//denom to ns",
            ordinary_clock=time.get_clock_info("monotonic").implementation,
            timebase=dict(numer=self.numer, denom=self.denom),
        )


def check_deadline(clock, deadline):
    if clock() >= deadline:
        raise GuardError("Continuous deadline exhausted (including suspension)")


@contextmanager
def alarm(clock, deadline):
    """Wake-up alarm is supplementary; continuous checks remain authoritative."""
    check_deadline(clock, deadline)
    old = signal.getsignal(signal.SIGALRM)

    def expired(*_):
        raise GuardError("Independent bounded parent operation interrupted")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, deadline - clock()))
    try:
        yield
        check_deadline(clock, deadline)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def reap(child, deadline, *, clock, sleep=time.sleep):
    """No historical monotonic termination helper; TERM/KILL and bounded polling."""
    if child.poll() is None:
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        term_until = min(deadline, clock() + 0.5)
        while child.poll() is None and clock() < term_until:
            sleep(min(0.02, max(0, term_until - clock())))
    if child.poll() is None:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    while child.poll() is None and clock() < deadline:
        sleep(min(0.02, max(0, deadline - clock())))
    # poll reaps on POSIX. If suspended past deadline, KILL is already sent;
    # disclose missing/late reap instead of inventing a timely lifecycle.
    return dict(
        reaped=child.poll() is not None, cleanup_deadline_met=clock() <= deadline
    )


def capture(command, clock, deadline):
    check_deadline(clock, deadline)
    with alarm(clock, deadline):
        value = subprocess.check_output(
            command,
            text=True,
            stderr=subprocess.STDOUT,
            timeout=min(1, max(0.001, deadline - clock())),
        )
    if len(value.encode()) > 65536:
        raise GuardError("Unbounded native diagnostic output")
    return value


def assertion_id(text, pid):
    match = re.search(
        rf"pid {pid}\(caffeinate\): \[([^\]]+)\].*?PreventUserIdleSystemSleep",
        text,
    )
    if not match or not re.search(r"PreventUserIdleSystemSleep\s+1\b", text):
        raise GuardError("Owned active idle-system sleep assertion not observed")
    return match.group(1)


class IdleAssertion:
    def __init__(self, clock, *, launch=subprocess.Popen, read=capture):
        self.clock, self.launch, self.read = clock, launch, read
        self.child = None
        self.identity = None
        self.last_checked = -float("inf")
        self.evidence = dict(
            mechanism="/usr/bin/caffeinate -i -w controller_PID",
            controller_pid=os.getpid(),
            display_sleep_permitted=True,
            persistent_settings_changed=False,
            observations=[],
            released=False,
        )

    def start(self, deadline):
        check_deadline(self.clock, deadline)
        self.child = self.launch(
            ["/usr/bin/caffeinate", "-i", "-w", str(os.getpid())],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self.evidence["helper_pid"] = self.child.pid
        # Creation can take a scheduling quantum, inside the prerequisite ceiling.
        until = min(deadline, self.clock() + 2)
        last = None
        while self.clock() < until:
            try:
                self.check(deadline, force=True)
                self.evidence["created"] = self.clock()
                return self
            except GuardError as error:
                last = error
                if self.child.poll() is not None:
                    break
                time.sleep(0.05)
        raise GuardError(f"Sleep assertion setup failed: {last}")

    def check(self, deadline, *, force=False):
        check_deadline(self.clock, deadline)
        if self.child is None or self.child.poll() is not None:
            raise GuardError("Owned sleep helper unexpectedly absent/exited")
        if force or self.clock() - self.last_checked >= 5:
            text = self.read(
                ["/usr/bin/pmset", "-g", "assertions"], self.clock, deadline
            )
            identity = assertion_id(text, self.child.pid)
            if self.identity is not None and identity != self.identity:
                raise GuardError("Owned sleep assertion identity changed")
            self.identity = identity
            sample = self.read(
                ["/bin/ps", "-p", str(self.child.pid), "-o", "pid=,ppid=,rss=,stat="],
                self.clock,
                deadline,
            ).strip()
            values = sample.split()
            if len(values) != 4 or int(values[0]) != self.child.pid:
                raise GuardError("Unavailable helper process accounting")
            self.evidence["observations"].append(
                dict(
                    continuous_seconds=self.clock(),
                    UTC=datetime.now(UTC).isoformat(),
                    assertion_id=identity,
                    active=True,
                    helper_rss_bytes=int(values[2]) * 1024,
                    helper_ppid=int(values[1]),
                    helper_state=values[3],
                    assertion_line=next(
                        line for line in text.splitlines() if identity in line
                    ),
                )
            )
            self.last_checked = self.clock()
        check_deadline(self.clock, deadline)

    def release(self, deadline):
        if self.child is not None:
            lifecycle = reap(
                self.child, min(deadline, self.clock() + 2), clock=self.clock
            )
            self.evidence.update(
                helper_returncode=self.child.returncode, lifecycle=lifecycle
            )
            text = self.read(
                ["/usr/bin/pmset", "-g", "assertions"], self.clock, deadline
            )
            absent = not re.search(rf"pid {self.child.pid}\(caffeinate\):", text)
            absent &= self.identity is None or self.identity not in text
            self.evidence.update(
                released=absent and lifecycle["reaped"],
                released_continuous=self.clock(),
                release_UTC=datetime.now(UTC).isoformat(),
                owned_assertion_absent=absent,
            )
            if not self.evidence["released"]:
                raise GuardError("Sleep assertion release not confirmed")
        return self.evidence


def supervise(
    command,
    log,
    *,
    root,
    environment,
    clock,
    operation_deadline,
    stage_deadline,
    whole_deadline,
    monitor=lambda: None,
    launch=subprocess.Popen,
    sleep=time.sleep,
):
    started = clock()
    child, error, exit_seen = None, None, None
    lifecycle = dict(reaped=False, cleanup_deadline_met=False)
    try:
        check_deadline(clock, operation_deadline)
        with log.open("x") as stream:
            child = launch(
                command,
                cwd=root,
                env=environment,
                stdout=stream,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            while True:
                # Check BEFORE poll and AFTER observing exit: a late exit0 is rejected.
                check_deadline(clock, operation_deadline)
                parent_check(clock=clock, deadline=whole_deadline)
                monitor()
                code = child.poll()
                check_deadline(clock, operation_deadline)
                if code is not None:
                    exit_seen = clock()
                    break
                if log.stat().st_size > 2**20:
                    raise GuardError("Bounded worker log exceeded")
                sleep(0.05)
    except BaseException as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if child is not None:
            lifecycle = reap(
                child, min(stage_deadline, clock() + 2), clock=clock, sleep=sleep
            )
            exit_seen = exit_seen or clock()
    end = clock()
    return dict(
        returncode=child.returncode if child else None,
        parent_error=error,
        child_pid=child.pid if child else None,
        child_reaped=lifecycle["reaped"],
        started_continuous=started,
        exit_observed_continuous=exit_seen,
        end_continuous=end,
        elapsed_continuous_seconds=end - started,
        operation_deadline_continuous=operation_deadline,
        stage_deadline_continuous=stage_deadline,
        overshoot_seconds=max(0, end - stage_deadline),
        within_deadline=end <= stage_deadline and end <= whole_deadline,
        parent_confirms_normal_exit=child is not None
        and child.returncode == 0
        and error is None
        and lifecycle["reaped"]
        and lifecycle["cleanup_deadline_met"],
    )
