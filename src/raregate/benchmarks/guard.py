"""Benchmark-scoped own-process guards; stdlib and unchanged Darwin bindings."""

import json
import os
import resource
import signal
import subprocess
import sys
import threading
import time

from raregate.supervision.particle_collector import DarwinBindings
from raregate.supervision.particle_host import parse_vm_stat

NATIVE_METHOD = "all_malloc_zone_reserved_bytes_conservative_upper_bound"
PRESSURE_METHOD = "XNU_read_only_sysctl_dispatch_flags_1normal_2warning_4critical"


class GuardError(RuntimeError):
    """Latched process/deadline/accounting veto."""


def parent_check(clock=time.monotonic, deadline=None):
    if any(name in sys.modules for name in ("numpy", "torch", "sklearn", "h5py")):
        raise GuardError("Controller must stay standard-library only.")
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform != "darwin":
        rss *= 1024
    if not 0 < rss <= 134217728:
        raise GuardError("Controller lifetimeRSS ceiling exceeded/unavailable.")
    if deadline is not None and clock() > deadline:
        raise GuardError("Whole campaign deadline exceeded.")
    return rss


class Guard:
    def __init__(
        self,
        deadline,
        *,
        directory=None,
        probe=None,
        clock=time.monotonic,
        notify=True,
        journal_limit=8 * 2**20,
    ):
        self.deadline, self.clock, self.directory = deadline, clock, directory
        self.probe = probe or DarwinBindings().process_sample
        self.notify, self.journal_limit = notify, journal_limit
        self.lock = threading.RLock()
        self.done = threading.Event()
        self.thread = None
        self.error = None
        self.last = None
        self.phase = "startup"
        self.checks = self.periodic_checks = 0
        self.guard_seconds = 0.0
        self.peak_rss = self.native_peak = 0
        self.pressure_counts = {"NORMAL": 0, "WARN": 0, "CRITICAL": 0, "unknown": 0}
        self.contexts = []
        self.journal = None
        self.old_handlers = None

    def _deadline(self):
        if self.error:
            raise GuardError(self.error)
        if self.clock() > self.deadline:
            raise GuardError("Import/operation/cleanup-inclusive worker deadline.")

    def _record(self):
        if self.journal:
            row = (
                json.dumps(
                    {
                        "phase": self.phase,
                        "sample": self.last,
                        "latched_error": self.error,
                    },
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            )
            if self.journal.tell() + len(row.encode()) > self.journal_limit:
                raise GuardError("Bounded guard journal ceiling exceeded.")
            self.journal.write(row)
            self.journal.flush()

    def check(self):
        with self.lock:
            started = self.clock()
            try:
                self._deadline()
                value = self.probe()
                self.last = {
                    key: value.get(key)
                    for key in (
                        "peak_rss_bytes",
                        "native_heap_reserved_bytes",
                        "native_heap_in_use_bytes",
                        "workspace_method",
                        "pressure_dispatch_flags",
                        "pressure_errno",
                        "pressure_method",
                    )
                }
                self.last.update(
                    query_start=started,
                    query_end=self.clock(),
                    rss_method="Darwin_getrusage_SELF_lifetime_bytes",
                )
                self.checks += 1
                for key in (
                    "peak_rss_bytes",
                    "native_heap_reserved_bytes",
                    "native_heap_in_use_bytes",
                ):
                    if type(value.get(key)) is not int or value[key] < 0:
                        raise GuardError("Unavailable/malformed primary accounting.")
                if (
                    not value["peak_rss_bytes"]
                    or not value["native_heap_reserved_bytes"]
                    or value["native_heap_in_use_bytes"]
                    > value["native_heap_reserved_bytes"]
                    or value.get("workspace_method") != NATIVE_METHOD
                    or self.last["query_end"] < started
                ):
                    raise GuardError("Malformed primary method/relation/timestamps.")
                # Preserve actual failed peaks before the limits/pressure veto.
                self.peak_rss = max(self.peak_rss, value["peak_rss_bytes"])
                self.native_peak = max(
                    self.native_peak, value["native_heap_reserved_bytes"]
                )
                pressure, errno = (
                    value.get("pressure_dispatch_flags"),
                    value.get("pressure_errno"),
                )
                if (
                    value.get("pressure_method") != PRESSURE_METHOD
                    or (
                        pressure is not None
                        and (type(pressure) is not int or pressure not in (1, 2, 4))
                    )
                    or (pressure is None and (type(errno) is not int or errno < 0))
                    or (pressure is not None and errno is not None)
                ):
                    raise GuardError("Malformed pressure/provenance.")
                self.pressure_counts[
                    {1: "NORMAL", 2: "WARN", 4: "CRITICAL", None: "unknown"}[pressure]
                ] += 1
                if (
                    value["peak_rss_bytes"] > 1073741824
                    or value["native_heap_reserved_bytes"] > 536870912
                ):
                    raise GuardError("Benchmark worker RSS/native ceiling exceeded.")
                if pressure == 4:
                    raise GuardError("CRITICAL pressure veto.")
                self._deadline()
                self._record()
            except Exception as exc:
                self.error = self.error or str(exc)
                try:
                    self._record()
                except Exception:
                    pass
                raise GuardError(self.error) from exc
            finally:
                self.guard_seconds += self.clock() - started

    def boundary(self, phase):
        self.phase = phase
        self.check()

    def _signal(self, *_):
        self.error = self.error or "Worker signal/deadline interruption."
        raise GuardError(self.error)

    def _watch(self):
        while not self.done.wait(0.05):
            try:
                self.periodic_checks += 1
                self.check()
            except Exception:
                if self.notify:
                    os.kill(os.getpid(), signal.SIGUSR1)
                return

    def __enter__(self):
        if self.directory:
            self.journal = (self.directory / "guards.jsonl").open("x")
        if self.notify:
            self.old_handlers = (
                signal.getsignal(signal.SIGUSR1),
                signal.getsignal(signal.SIGALRM),
            )
            signal.signal(signal.SIGUSR1, self._signal)
            signal.signal(signal.SIGALRM, self._signal)
            signal.setitimer(
                signal.ITIMER_REAL, max(0.001, self.deadline - self.clock())
            )
        try:
            self.check()
            self.thread = threading.Thread(
                target=self._watch, name="frozen-cpu-guard", daemon=True
            )
            self.thread.start()
        except BaseException:
            self.close()
            raise
        return self

    def context(self):
        self.check()
        started = self.clock()
        row = {
            "role": "optional_context_never_admission",
            "query_start": started,
            "status": "unavailable",
        }
        try:
            timeout = min(2, max(0.001, self.deadline - self.clock()))
            raw = subprocess.check_output(
                ["/usr/bin/vm_stat"], text=True, timeout=timeout
            )
            if len(raw.encode()) > 16384:
                raise ValueError("Unbounded context output.")
            row.update(parse_vm_stat(raw), status="available")
        except Exception as exc:
            row["error"] = str(exc)
        finally:
            row["query_end"] = self.clock()
            self.contexts.append(row)
        self.check()

    def close(self):
        self.done.set()
        if self.thread:
            self.thread.join(timeout=1)
            if self.thread.is_alive():
                self.error = self.error or "Owned watcher failed to close."
        if self.old_handlers:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGUSR1, self.old_handlers[0])
            signal.signal(signal.SIGALRM, self.old_handlers[1])
        if self.journal:
            self.journal.close()
            self.journal = None

    def __exit__(self, *_):
        self.close()

    def report(self):
        return {
            "peak_rss_bytes": self.peak_rss,
            "native_heap_reserved_bytes": self.native_peak,
            "checks": self.checks,
            "periodic_checks": self.periodic_checks,
            "guard_seconds_overlapping_not_subtractable": self.guard_seconds,
            "pressure_counts": self.pressure_counts,
            "last_sample": self.last,
            "latched_error": self.error,
            "optional_context": self.contexts,
            "owned_thread_alive": bool(self.thread and self.thread.is_alive()),
        }
