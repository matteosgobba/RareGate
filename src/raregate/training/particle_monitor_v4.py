"""Explicit v4 bounded host age, fresh process guards; no scientific change."""

import secrets
import signal
import threading
import time

from raregate.supervision import particle_launcher as identity
from raregate.supervision.particle_collector import DarwinBindings
from raregate.supervision.particle_sampling import (
    BACKEND,
    CADENCE,
    MAX_AGE,
    Sampler,
    append_bounded,
    raw_record,
    stamp,
)
from raregate.training.particle_resources import validate_policy, validate_sample
from raregate.training.particle_set import ResourceLimitError, ResourceMonitor

MANIFEST = "configs/resources/particle_resource_monitor_v4.json"
PROMPT = "docs/prompts/0015-particle-bounded-sampling.md"
PROMPT_HASH = "5788c605815db5944dcf1d54f376141d92c28b3520ab410d0a2fcbaf7caaf045"


def definition():
    return {
        "schema_version": 1,
        "implementation_version": 4,
        "monitor_type": "particle_bounded_age_observation_contract",
        "status": "reviewed_contract_synthetic_material_gate_before_bounded_execution",
        "host_backend": BACKEND,
        "process_backend": "cached_DarwinBindings_v3_fresh_each_guard",
        "profile_sha256": identity.PROFILE_HASH,
        "design_sha256": identity.DESIGN_HASH,
        "model_config_sha256": identity.CONFIG_HASH,
        "authorization_prompt_sha256": PROMPT_HASH,
        "host_cadence_seconds": CADENCE,
        "host_age_upper_ceiling_seconds": MAX_AGE,
        "host_age_formula": "guard_now_minus_query_start; publication_and_read_do_not_renew_age",
        "freshness_change": "explicitly_not_equivalent_to_v2_v3_fresh_host_query_each_guard",
        "phase_entry": "fresh_synchronous_thread_owned_query_before_work;100ms_limit",
        "batch_entry_exit": "latest_valid_host_age_le100ms_and_fresh_process_pressure_deadlines",
        "pre_optimizer_step": "fresh_process_guard_and_flushed_reservation_before_mutation",
        "periodic_process_checks": "same_owned_sampling_thread_every50ms_even_query_pending",
        "collector_failure": "latched_no_restart_or_safe_substitution",
        "external_probe_timeout_seconds": 2,
        "journal_limit_bytes_each": 32 * 2**20,
        "observation_limits_are_not_termination_latency_guarantees": True,
        "limits": {
            "minimum_system_available_bytes_at_launch": 4831838208,
            "stop_if_system_available_below_bytes": 4294967296,
            "working_tensor_and_workspace_ceiling_bytes": 536870912,
            "process_peak_rss_ceiling_bytes": 6442450944,
        },
        "phase_limits_seconds": {
            "readiness": 30,
            "dev_reader": 60,
            "dev_readiness": 30,
            "dev": 300,
        },
        "remaining_full_run_limits": {
            "cycle_seconds": 180,
            "fit_per_run_seconds": 36000,
            "postfit_per_run_seconds": 3600,
            "two_run_total_seconds": 79200,
        },
        "material_gate": "three_repetitions_median_complete_v4_le_median_v3_div3_exact_parity",
        "scope": "Task0015_single_conditional_engineering_study_same_original1024_dev_ids",
        "historical_steps_started": 96,
        "maximum_additional_real_steps_started": 96,
        "maximum_cumulative_real_steps_started": 192,
        "canonical_selection_calibration_freeze_authorized": False,
        "source_binding": "current_full_src_and_top_level_tests_actual_acceptance",
        "policy_v1_compliance": False,
    }


def validate_manifest(manifest, config, profile, acceptance=None):
    validate_policy(profile, config, identity.PROFILE_HASH)
    if (
        identity.digest(manifest) != identity.digest(definition())
        or identity.digest(config) != identity.CONFIG_HASH
    ):
        raise ValueError("Unsupported v4 observation/config/profile relationship.")
    if acceptance is not None and (
        acceptance.get("pytest_exit_code") != 0
        or acceptance.get("config_sha256") != identity.CONFIG_HASH
        or acceptance.get("source_sha256") != identity.source_hashes()
    ):
        raise ValueError("Current source-bound acceptance required.")
    return identity.digest(manifest)


class MonitorV4(ResourceMonitor):
    def __init__(
        self,
        config,
        profile,
        manifest,
        *,
        directory=None,
        process_probe=None,
        sampler_factory=Sampler,
        collector=None,
        clock=time.monotonic,
        synthetic_fixture=False,
        notify_failure=True,
    ):
        self.manifest_hash = validate_manifest(manifest, config, profile)
        self.config, self.profile, self.directory = config, profile, directory
        self.synthetic_fixture, self.notify_failure = synthetic_fixture, notify_failure
        self.process_probe = (
            DarwinBindings().process_sample if process_probe is None else process_probe
        )
        self._guard_lock = threading.RLock()
        self._active = False
        self._phase = "startup"
        self._previous_handler = None
        self._guard_file = self._host_file = None
        self.phases = {}
        self.host_ages = []
        self.guards = 0
        self.process_checks = 0
        self.reused_guards = 0
        self.guarded_generations = set()
        self.last = None
        self.timing = {
            k: 0.0
            for k in (
                "guard_wall_seconds",
                "guard_process_cpu_seconds",
                "native_process_seconds",
                "guard_lock_wait_seconds",
                "journal_io_seconds",
            )
        }
        super().__init__(
            {**config["resource_gate"], **profile["limits"]},
            clock=clock,
            monitor_background=False,
        )
        self.sampler = sampler_factory(
            secrets.token_hex(16),
            collector=collector,
            on_observation=self._new_host,
            on_tick=self._background_tick,
            on_failure=self._sampling_failure,
            clock=clock,
        )

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, value):
        changed = value != self._phase
        self._phase = value
        if (
            changed
            and self._active
            and threading.current_thread() is threading.main_thread()
        ):
            self.check(fresh=True)

    def _sampling_failure(self, message):
        self.error = self.error or message
        if self.notify_failure and self._active:
            signal.raise_signal(signal.SIGALRM)

    def _latch(self, exc):
        self.error = self.error or str(exc)
        self.last_failure = {
            "phase": self.phase,
            "error": self.error,
            "elapsed_seconds": self.clock() - self.started,
            "process_observation": getattr(self, "last_process_observation", None),
        }
        self.sampler.fail(exc)

    def _deadlines(self):
        if self.error:
            raise ResourceLimitError(self.error)
        for name, end in tuple(self.deadlines.items()):
            if self.clock() > end:
                raise ResourceLimitError(f"Time ceiling exceeded: {name}.")

    def _process(self):
        tick = self.clock()
        value = self.process_probe()
        end = self.clock()
        stamp(tick)
        stamp(end)
        if end < tick:
            raise ResourceLimitError("Backward own-process measurement timestamp.")
        self.process_checks += 1
        self.timing["native_process_seconds"] += end - tick
        self.last_process_observation = {
            **value,
            "process_query_start": tick,
            "process_query_end": end,
        }
        for k in (
            "peak_rss_bytes",
            "native_heap_reserved_bytes",
            "native_heap_in_use_bytes",
        ):
            if type(value.get(k)) is not int or value[k] < 0:
                raise ResourceLimitError("Unknown primary process accounting.")
        if (
            not value["native_heap_reserved_bytes"]
            or value.get("workspace_method")
            != "all_malloc_zone_reserved_bytes_conservative_upper_bound"
        ):
            raise ResourceLimitError("Unknown native reservation method.")
        if value["native_heap_in_use_bytes"] > value["native_heap_reserved_bytes"]:
            raise ResourceLimitError("Malformed native reservation/in-use relation.")
        # Retain valid measured maxima even when this observation triggers a veto.
        for key in self.peak:
            self.peak[key] = max(self.peak[key], value[key])
        phase = self.phases.get(self.phase)
        if phase is not None:
            phase["native_peak_reserved_bytes"] = max(
                phase["native_peak_reserved_bytes"], value["native_heap_reserved_bytes"]
            )
            phase["lifetime_peak_rss_at_samples_bytes"] = max(
                phase["lifetime_peak_rss_at_samples_bytes"], value["peak_rss_bytes"]
            )
        pressure = value.get("pressure_dispatch_flags")
        if pressure is not None and (
            type(pressure) is not int or pressure not in (1, 2, 4)
        ):
            raise ResourceLimitError("Malformed optional pressure accounting.")
        if pressure in (2, 4):
            raise ResourceLimitError("Verified pressure warning/critical veto.")
        if (
            value["peak_rss_bytes"] > 6 * 2**30
            or value["native_heap_reserved_bytes"] > 512 * 2**20
        ):
            raise ResourceLimitError("Process RSS/native ceiling exceeded.")
        return {**value, "process_query_start": tick, "process_query_end": end}

    def _guard(self, host, *, role, launch=False, initial_pending=False):
        wall, cpu = time.monotonic(), time.process_time()
        locktick = time.monotonic()
        with self._guard_lock:
            self.timing["guard_lock_wait_seconds"] += time.monotonic() - locktick
            self._deadlines()
            process = self._process()
            now = self.clock()
            if host is None:
                if initial_pending:
                    return
                raise ResourceLimitError("Missing complete host sample.")
            if host.synthetic and not self.synthetic_fixture:
                raise ResourceLimitError("Synthetic host cannot authorize real guards.")
            age = host.age(now, self.sampler.issuer)
            primary = host.primary()
            sample = {**primary, **process}
            error = None
            try:
                validate_sample(sample, self.config, self.profile, launch=launch)
            except BaseException as exc:
                error = exc
            self.guards += 1
            self.samples = self.guards
            self.host_ages.append(age)
            if role != "background_generation":
                if host.generation in self.guarded_generations:
                    self.reused_guards += 1
                self.guarded_generations.add(host.generation)
            for key in self.peak:
                self.peak[key] = max(self.peak[key], process[key])
            available = host.available_bytes
            self.minimum_available = (
                available
                if self.minimum_available is None
                else min(self.minimum_available, available)
            )
            record = {
                "elapsed_seconds": now - self.started,
                "phase": self.phase,
                "guard_role": role,
                "host_generation": host.generation,
                "host_query_start": host.query_start,
                "host_query_end": host.query_end,
                "host_published_at": host.published_at,
                "host_age_upper_seconds": age,
                "host_backend": host.backend,
                "host_validation_status": "valid_primary_fields",
                "synthetic_not_readiness": host.synthetic,
                "guard_checked_at": now,
                **sample,
            }
            self.last = record
            phase = self.phases.setdefault(
                self.phase,
                {
                    "samples": 0,
                    "minimum_available_bytes": available,
                    "native_peak_reserved_bytes": 0,
                    "lifetime_peak_rss_at_samples_bytes": 0,
                    "first": record,
                    "last": record,
                },
            )
            phase.update(
                samples=phase["samples"] + 1,
                minimum_available_bytes=min(
                    phase["minimum_available_bytes"], available
                ),
                native_peak_reserved_bytes=max(
                    phase["native_peak_reserved_bytes"],
                    process["native_heap_reserved_bytes"],
                ),
                lifetime_peak_rss_at_samples_bytes=max(
                    phase["lifetime_peak_rss_at_samples_bytes"],
                    process["peak_rss_bytes"],
                ),
                last=record,
            )
            if self.directory:
                tick = time.monotonic()
                if self._guard_file is None:
                    self._guard_file = (self.directory / "guard-samples.jsonl").open(
                        "x"
                    )
                append_bounded(self._guard_file, record)
                self.timing["journal_io_seconds"] += time.monotonic() - tick
            if error:
                raise error
            host.age(self.clock(), self.sampler.issuer)
            self._deadlines()
        self.timing["guard_wall_seconds"] += time.monotonic() - wall
        self.timing["guard_process_cpu_seconds"] += time.process_time() - cpu

    def _background_tick(self, host):
        self._guard(host, role="background_periodic", initial_pending=host is None)

    def _new_host(self, host):
        self._guard(host, role="background_generation")
        if self.directory:
            with self._guard_lock:
                if self._host_file is None:
                    self._host_file = (self.directory / "host-samples.jsonl").open("x")
                append_bounded(
                    self._host_file,
                    {"scope": "validated_before_publication", **raw_record(host)},
                )

    def check(self, *, launch=False, fresh=False):
        try:
            self._deadlines()
            host = self.sampler.refresh() if launch or fresh else self.sampler.get()
            self._guard(
                host,
                role="synchronous_fresh" if launch or fresh else "synchronous_batch",
                launch=launch,
            )
        except BaseException as exc:
            self._latch(exc)
            raise

    def __enter__(self):
        if self._active:
            raise ResourceLimitError("Monitor cannot restart or nest.")
        self._active = True
        self._previous_handler = signal.signal(signal.SIGALRM, self._alarm)
        self.monitor_background = True  # retained original signal deadline context
        try:
            self.sampler.start()
            self.check(launch=True)
            return self
        except BaseException:
            self.close()
            raise

    def close(self):
        self._active = False
        self.sampler.close()
        for handle in (self._guard_file, self._host_file):
            if handle:
                handle.close()
        if self._previous_handler is not None:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, self._previous_handler)
            self._previous_handler = None

    def __exit__(self, *_):
        self.close()

    def report(self):
        ages = self.host_ages
        return {
            **super().report(),
            "monitor_implementation_version": "bounded-host-age-v4",
            "observation_manifest_sha256": self.manifest_hash,
            "policy_v1_compliance": False,
            "phases": self.phases,
            "sampler": self.sampler.report(),
            "actual_fresh_process_checks": self.process_checks,
            "guard_records": self.guards,
            "reused_host_guard_records": self.reused_guards,
            "host_age_statistics": {
                "count": len(ages),
                "max_seconds": max(ages) if ages else None,
                "mean_seconds": sum(ages) / len(ages) if ages else None,
            },
            "overlapping_timing_diagnostics": self.timing,
            "last_failure": getattr(self, "last_failure", None),
            "last_process_observation": getattr(self, "last_process_observation", None),
            "synthetic_not_readiness": self.synthetic_fixture,
        }


def optimizer_observer(audit, monitor):
    """A guard before each mutation, then original durable step reservation."""

    def observe(optimizer):
        optimizer.register_step_pre_hook(lambda *_: monitor.check())
        audit.observe_optimizer(optimizer)

    return observe
