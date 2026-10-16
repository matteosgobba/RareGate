"""Development-only process guards; global counters are optional context."""

import selectors
import signal
import threading
import time

from raregate.supervision import particle_dev_policy as policy
from raregate.supervision.particle_collector import DarwinBindings
from raregate.supervision.particle_sampling import (
    SystemQuery,
    append_bounded,
    stamp,
)
from raregate.training.particle_set import ResourceLimitError, ResourceMonitor


class ProcessBudgetGuard(ResourceMonitor):
    def __init__(
        self,
        config,
        manifest,
        *,
        directory=None,
        process_probe=None,
        query_factory=SystemQuery,
        clock=time.monotonic,
        synthetic_fixture=False,
        notify_failure=True,
    ):
        self.policy_hash = policy.validate(manifest, config)
        super().__init__({}, clock=clock, monitor_background=True)
        self.directory = directory
        self.process_probe = process_probe or DarwinBindings().process_sample
        self.query_factory = query_factory
        self.synthetic_fixture = synthetic_fixture
        self.notify_failure = notify_failure
        self._guard_lock = threading.RLock()
        self._active = False
        self._phase = "startup"
        self._guard_file = self._context_file = None
        self.phases, self.contexts = {}, []
        self.process_checks = 0
        self.periodic_checks = 0
        self.last_process_observation = None

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, value):
        changed = value != self._phase
        self._phase = value
        if changed and self._active:
            self.check()
            self.context()
            self.check()

    def _deadlines(self):
        if self.error:
            raise ResourceLimitError(self.error)
        for name, end in tuple(self.deadlines.items()):
            if self.clock() > end:
                raise ResourceLimitError(f"Time ceiling exceeded: {name}.")

    def check(self, *, launch=False):
        # No host query is performed or host age checked here.
        with self._guard_lock:
            try:
                self._deadlines()
                start = stamp(self.clock())
                value = self.process_probe()
                end = stamp(self.clock())
                self.last_process_observation = {
                    **value,
                    "process_query_start": start,
                    "process_query_end": end,
                    "synthetic_not_readiness": self.synthetic_fixture,
                    "backend": "cached_DarwinBindings_fresh_own_process",
                    "peak_rss_method": "Darwin_getrusage_SELF_lifetime_bytes",
                }
                self.last = self.last_process_observation
                self.samples += 1
                self.process_checks += 1
                if end < start:
                    raise ResourceLimitError("Backward process timestamps.")
                for key in (
                    "peak_rss_bytes",
                    "native_heap_reserved_bytes",
                    "native_heap_in_use_bytes",
                ):
                    if type(value.get(key)) is not int or value[key] < 0:
                        raise ResourceLimitError(
                            "Unknown/malformed primary process accounting."
                        )
                if (
                    not value["peak_rss_bytes"]
                    or not value["native_heap_reserved_bytes"]
                    or value.get("workspace_method")
                    != "all_malloc_zone_reserved_bytes_conservative_upper_bound"
                    or value["native_heap_in_use_bytes"]
                    > value["native_heap_reserved_bytes"]
                ):
                    raise ResourceLimitError(
                        "Malformed native/RSS accounting method or relation."
                    )
                for key in self.peak:
                    self.peak[key] = max(self.peak[key], value[key])
                phase = self.phases.setdefault(
                    self.phase,
                    {
                        "checks": 0,
                        "native_peak_reserved_bytes": 0,
                        "lifetime_peak_rss_at_samples_bytes": 0,
                    },
                )
                phase["checks"] += 1
                phase["native_peak_reserved_bytes"] = max(
                    phase["native_peak_reserved_bytes"],
                    value["native_heap_reserved_bytes"],
                )
                phase["lifetime_peak_rss_at_samples_bytes"] = max(
                    phase["lifetime_peak_rss_at_samples_bytes"], value["peak_rss_bytes"]
                )
                pressure = value.get("pressure_dispatch_flags")
                if pressure is not None and (
                    type(pressure) is not int or pressure not in (1, 2, 4)
                ):
                    raise ResourceLimitError("Malformed optional pressure accounting.")
                if (
                    value.get("pressure_method")
                    != "XNU_read_only_sysctl_dispatch_flags_1normal_2warning_4critical"
                ):
                    raise ResourceLimitError("Unknown pressure provenance.")
                if (
                    value["peak_rss_bytes"] > 536870912
                    or value["native_heap_reserved_bytes"] > 268435456
                ):
                    raise ResourceLimitError(
                        "Shared dev process RSS/native ceiling exceeded."
                    )
                if pressure == 4:
                    raise ResourceLimitError("Verified CRITICAL pressure veto.")
                self._deadlines()
                self._record()
                return None
            except Exception as exc:
                self.error = self.error or str(exc)
                self.last_failure = {
                    "phase": self.phase,
                    "error": self.error,
                    "process": self.last_process_observation,
                }
                self._record()
                raise ResourceLimitError(self.error) from exc

    def _record(self):
        if self._guard_file:
            append_bounded(
                self._guard_file,
                {
                    "phase": self.phase,
                    "process": self.last_process_observation,
                    "latched_error": self.error,
                },
                16 * 2**20,
            )

    def context(self):
        """Bounded optional telemetry outside the guard lock; watcher stays live."""
        self.check()
        row = {
            "phase": self.phase,
            "role": "optional_context_never_admission",
            "requested_monotonic": self.clock(),
            "status": "unavailable",
        }
        query, selector = None, None
        try:
            query = self.query_factory(clock=self.clock)
            selector = selectors.DefaultSelector()
            selector.register(query.begin(), selectors.EVENT_READ)
            end = (
                min(query.query_start + 2, *self.deadlines.values())
                if self.deadlines
                else query.query_start + 2
            )
            while self.clock() < end:
                self._deadlines()
                value = query.finish()
                if value is not None:
                    # Exact existing SystemQuery parser; no host100ms admission rule.
                    row.update(
                        value,
                        status="available",
                        age_upper_seconds=self.clock() - value["query_start"],
                    )
                    break
                for key, _ in selector.select(max(0, min(0.05, end - self.clock()))):
                    if query.drain():
                        selector.unregister(key.fd)
            else:
                row["error"] = "Optional context timed out/skipped within2s/deadline."
        except Exception as exc:
            # Only optional telemetry may fail. Live guard/deadline failures propagate.
            self._deadlines()
            row["error"] = str(exc)
        finally:
            if query is not None:
                query.close()
            if selector is not None:
                selector.close()
            row["finished_monotonic"] = self.clock()
            self.contexts.append(row)
            if self._context_file:
                append_bounded(self._context_file, row, 16 * 2**20)
        self.check()
        return row

    def _alarm(self, *_):
        self.error = self.error or "Monitored wall-time ceiling interrupted operation."
        raise ResourceLimitError(self.error)

    def _watch(self):
        while not self._done.wait(0.05):
            try:
                self.periodic_checks += 1
                self.check()
            except Exception:
                if self.notify_failure and self._active:
                    signal.raise_signal(signal.SIGALRM)
                return

    def __enter__(self):
        if self._active:
            raise ResourceLimitError("Process guard already active.")
        if self.directory:
            self._guard_file = (self.directory / "guard-samples.jsonl").open("x")
            self._context_file = (self.directory / "context-samples.jsonl").open("x")
        self._previous_handler = signal.signal(signal.SIGALRM, self._alarm)
        self._active = True
        self._thread = threading.Thread(target=self._watch, daemon=True)
        self._thread.start()
        try:
            self.check(launch=True)
            self.context()
        except BaseException:
            self.close()
            raise
        return self

    def close(self):
        self._done.set()
        if self._thread:
            self._thread.join(timeout=1)
            if self._thread.is_alive():
                self.error = self.error or "Owned process watcher cleanup failed."
        if self._active:
            self._active = False
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, self._previous_handler)
        for file in (self._guard_file, self._context_file):
            if file and not file.closed:
                file.close()

    def __exit__(self, *_):
        self.close()
        if self._thread and self._thread.is_alive():
            raise ResourceLimitError(self.error)

    def report(self):
        return {
            **super().report(),
            "policy": policy.NAME,
            "policy_sha256": self.policy_hash,
            "global_available_role": "context_only_no_floor_no_age_veto",
            "monitor_implementation_version": "process_budget_guard_v1",
            "process_checks": self.process_checks,
            "periodic_checks": self.periodic_checks,
            "phases": self.phases,
            "context_observations": self.contexts,
            "last_process_observation": self.last_process_observation,
            "latched_failure": self.error,
            "last_failure": getattr(self, "last_failure", None),
            "owned_thread_alive": bool(self._thread and self._thread.is_alive()),
            "synthetic_not_readiness": self.synthetic_fixture,
        }
