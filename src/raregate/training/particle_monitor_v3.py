"""Versioned cached-binding monitor; numerical policy v2 and science unchanged."""

import json
import threading
import time

from raregate.supervision import particle_launcher as identity
from raregate.supervision.particle_collector import CachedSystemCollector
from raregate.training.particle_resources import (
    PolicyMonitor,
    validate_policy,
    validate_sample,
)
from raregate.training.particle_set import ResourceLimitError

MANIFEST_PATH = "configs/resources/particle_resource_monitor_v3.json"


def definition():
    return {
        "schema_version": 1,
        "implementation_version": 3,
        "monitor_type": "particle_resource_monitor",
        "status": "synthetically_validated_pending_real_revalidation",
        "backend": CachedSystemCollector.backend,
        "implementation": "cached-bindings-flushed-journal-v3",
        "profile_sha256": identity.PROFILE_HASH,
        "design_sha256": identity.DESIGN_HASH,
        "model_config_sha256": identity.CONFIG_HASH,
        "limits": {
            "minimum_system_available_bytes_at_launch": 4831838208,
            "stop_if_system_available_below_bytes": 4294967296,
            "working_tensor_and_workspace_ceiling_bytes": 536870912,
            "process_peak_rss_ceiling_bytes": 6442450944,
        },
        "watch_interval_seconds": 0.05,
        "external_probe_timeout_seconds": 2,
        "observation": {
            "primary": "new_system_vm_stat_snapshot_each_check",
            "free": "displayed_native_free_minus_speculative",
            "page_size": "actual_vm_stat_header",
            "sample_age": "check_completion_minus_query_start_upper_bound_le2s",
            "direct_mach_vm_backend": "diagnostic_only_not_eligible_kernel_cache",
            "stream_backend": "not_selected_no_cached_primary_values",
            "detection": "50ms_wait_plus_probe_lock_GIL_delivery; no hard50ms guarantee",
        },
        "journal": "open_owned_handle_flush_every_sample; no_fsync_claim",
        "audit": "unchanged_synchronous_pre_step_reservation_post_step_completion",
        "synthetic_acceptance_record": "data/task0014-synthetic-acceptance.json",
        "source_binding": "all_src_latenttrigger_py_and_top_level_tests_current_exact_map",
        "real_execution_authorized": False,
        "canonical_training_authorized": False,
        "policy_v1_compliance": False,
    }


def validate_manifest(manifest, config, profile, *, acceptance=None):
    validate_policy(profile, config, identity.PROFILE_HASH)
    if identity.digest(config) != identity.CONFIG_HASH or identity.digest(
        manifest
    ) != identity.digest(definition()):
        raise ValueError(
            "Unsupported monitor implementation/profile/config relationship."
        )
    if acceptance is not None and (
        acceptance.get("pytest_exit_code") != 0
        or acceptance.get("config_sha256") != identity.CONFIG_HASH
        or acceptance.get("source_sha256") != identity.source_hashes()
    ):
        raise ValueError("Current source-bound synthetic acceptance required.")
    return identity.digest(manifest)


class MonitorV3(PolicyMonitor):
    """Retain original watcher/signals/deadlines and synchronous guards/audit.

    Timers are nested/overlapping diagnostics, never additive critical-path claims.
    A synthetic probe must be explicitly declared, and never supplies readiness.
    """

    def __init__(
        self,
        config,
        profile,
        manifest,
        *,
        probe=None,
        journal=None,
        clock=time.monotonic,
        monitor_background=True,
        synthetic_fixture=False,
    ):
        self.manifest_hash = validate_manifest(manifest, config, profile)
        self.synthetic_fixture = synthetic_fixture
        self._journal_handle = None
        self.timing = {
            k: 0.0
            for k in (
                "check_wall_seconds",
                "check_process_cpu_seconds",
                "lock_wait_seconds",
                "probe_wall_seconds",
                "serialization_seconds",
                "journal_write_flush_seconds",
                "watcher_check_wall_seconds",
            )
        }
        self.check_threads = {}
        super().__init__(
            config,
            profile,
            journal=journal,
            probe=CachedSystemCollector() if probe is None else probe,
            clock=clock,
            monitor_background=monitor_background,
        )

    def check(self, *, launch=False):
        wall, cpu = time.monotonic(), time.process_time()
        locktick = time.monotonic()
        try:
            with self._check_lock:
                self.timing["lock_wait_seconds"] += time.monotonic() - locktick
                if self.error:
                    raise ResourceLimitError(self.error)
                for name, end in tuple(self.deadlines.items()):
                    if self.clock() > end:
                        raise ResourceLimitError(f"Time ceiling exceeded: {name}.")
                tick = self.clock()
                sample = self.probe()
                duration = self.clock() - tick
                self.probe_seconds += duration
                self.probe_max_seconds = max(self.probe_max_seconds, duration)
                self.timing["probe_wall_seconds"] += duration
                # Strict method/age identity; no native/cache/unknown backend fallback.
                if sample.get("collector_backend") != CachedSystemCollector.backend:
                    raise ResourceLimitError("Unsupported collector backend/freshness.")
                if (
                    sample.get("diagnostic_guard_fixture")
                    and not self.synthetic_fixture
                ):
                    raise ResourceLimitError(
                        "Synthetic fixture cannot authorize live checks."
                    )
                start, end = (
                    sample.get("sample_started_monotonic"),
                    sample.get("sample_finished_monotonic"),
                )
                if (
                    type(start) not in (float, int)
                    or type(end) not in (float, int)
                    or not 0 <= end - start <= 2
                    or not 0 <= self.clock() - start <= 2
                    or sample.get("primary_values_reused") is not False
                ):
                    raise ResourceLimitError(
                        "Missing/stale/nonfinite primary observation."
                    )
                compact = {k: v for k, v in sample.items() if k != "vm_stat_raw"}
                # Numeric/provenance guard before maxima to reject malformed values.
                failure = None
                try:
                    validate_sample(sample, self.config, self.profile, launch=launch)
                except ResourceLimitError as exc:
                    failure = exc
                self.samples += 1
                self.last = compact
                for key in self.peak:
                    if type(sample.get(key)) is int:
                        self.peak[key] = max(self.peak[key], sample[key])
                available = sample.get("available_bytes")
                if type(available) is int:
                    self.minimum_available = (
                        available
                        if self.minimum_available is None
                        else min(self.minimum_available, available)
                    )
                    phase = self.phases.setdefault(
                        self.phase,
                        {
                            "samples": 0,
                            "minimum_available_bytes": available,
                            "native_peak_reserved_bytes": 0,
                            "lifetime_peak_rss_at_samples_bytes": 0,
                            "first": compact,
                            "last": compact,
                        },
                    )
                    phase.update(
                        samples=phase["samples"] + 1,
                        minimum_available_bytes=min(
                            phase["minimum_available_bytes"], available
                        ),
                        native_peak_reserved_bytes=max(
                            phase["native_peak_reserved_bytes"],
                            sample.get("native_heap_reserved_bytes", 0),
                        ),
                        lifetime_peak_rss_at_samples_bytes=max(
                            phase["lifetime_peak_rss_at_samples_bytes"],
                            sample.get("peak_rss_bytes", 0),
                        ),
                        last=compact,
                    )
                if self.journal:
                    tick = time.monotonic()
                    encoded = (
                        json.dumps(
                            {
                                "elapsed_seconds": self.clock() - self.started,
                                "phase": self.phase,
                                "probe_seconds": duration,
                                **compact,
                            },
                            allow_nan=False,
                        )
                        + "\n"
                    )
                    self.timing["serialization_seconds"] += time.monotonic() - tick
                    tick = time.monotonic()
                    if self._journal_handle is None:
                        self._journal_handle = self.journal.open("a")
                    self._journal_handle.write(encoded)
                    self._journal_handle.flush()
                    self.timing["journal_write_flush_seconds"] += (
                        time.monotonic() - tick
                    )
                if failure:
                    raise failure
                for name, end in tuple(self.deadlines.items()):
                    if self.clock() > end:
                        raise ResourceLimitError(f"Time ceiling exceeded: {name}.")
        except BaseException as exc:
            self.last_failure = {
                "phase": self.phase,
                "error": str(exc),
                "elapsed_seconds": self.clock() - self.started,
            }
            raise
        finally:
            elapsed = time.monotonic() - wall
            self.timing["check_wall_seconds"] += elapsed
            self.timing["check_process_cpu_seconds"] += time.process_time() - cpu
            thread = threading.current_thread().name
            self.check_threads[thread] = self.check_threads.get(thread, 0) + 1
            if threading.current_thread() is not threading.main_thread():
                self.timing["watcher_check_wall_seconds"] += elapsed

    def close(self):
        if self._journal_handle:
            self._journal_handle.close()
            self._journal_handle = None

    def __exit__(self, *args):
        try:
            super().__exit__(*args)
        finally:
            self.close()

    def report(self):
        return {
            **super().report(),
            "monitor_implementation_version": "cached-bindings-flushed-journal-v3",
            "implementation_manifest_sha256": self.manifest_hash,
            "synthetic_fixture_not_readiness": self.synthetic_fixture,
            "overlapping_timing_diagnostics": self.timing,
            "check_threads": self.check_threads,
            "last_failure": getattr(self, "last_failure", None),
        }
