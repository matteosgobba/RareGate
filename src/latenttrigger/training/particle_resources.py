"""Engineering policy v2, with immutable model config and original live ceilings."""

import ctypes
import ctypes.util
import threading
import time

from latenttrigger.data.processed import content_hash
from latenttrigger.models.particle_recovery import check_reading
from latenttrigger.models.particle_set import validate_config
from latenttrigger.training.particle_set import (
    ResourceLimitError,
    ResourceMonitor,
    memory_snapshot,
)


def policy_definition(config):
    validate_config(config)
    old = config["resource_gate"]
    keys = (
        "stop_if_system_available_below_bytes",
        "process_peak_rss_ceiling_bytes",
        "working_tensor_and_workspace_ceiling_bytes",
    )
    return {
        "schema_version": 1,
        "engineering_policy_version": 2,
        "policy_type": "particle_launch_admission",
        "scope": "Task0012_provisional_readers_then_conditionally_bounded_dev_only",
        "status": "provisional; bounded_dev_requires_completed_reader_activation",
        "design_scientific_sha256": config["design_scientific_sha256"],
        "model_config_scientific_sha256": content_hash(config),
        "metric": "Darwin_free_plus_inactive_pages",
        "limits": {
            **{k: old[k] for k in keys},
            "minimum_system_available_bytes_at_launch": 9 * 2**29,
        },
        "supersedes": {
            "policy_version": 1,
            "only_threshold_change": {
                "minimum_system_available_bytes_at_launch": {
                    "old_bytes": old["minimum_system_available_bytes_at_launch"],
                    "new_bytes": 9 * 2**29,
                }
            },
        },
        "headroom_bytes": 512 * 2**20,
        "rationale": "4GiB continuing reserve plus512MiB whole-native admission envelope; mapped effects remain live-guarded",
        "monitor": {
            "implementation_version": "policy2-original50ms-compactjournal-v1",
            "watch_interval_seconds": 0.05,
            "external_probe_timeout_seconds": 2,
            "detection_latency": "50ms wait plus actual probe/GIL scheduling; vm_stat timeout2s; per-batch checks and signal deadlines unchanged",
            "primary_unknown": "fail_closed",
            "pressure_warning_or_critical": "veto",
            "pressure_unknown": "disclose; never infer normal from percentage",
            "raw_vm_stat": "preflight_only; compact phase journals",
            "current_dirty_private_unknown": "disclose; no substitution for peak_RSS/native/available",
        },
        "phase_limits_seconds": {
            "pilot_preflight": 30,
            "dev_reader": 60,
            "full_custody": 300,
            "dev_preflight": 30,
            "dev": 300,
        },
        "reader_sample": {
            "role": "train_background",
            "scope": "frozen_dev",
            "events": 64,
            "batch_size": 32,
            "policy": "first64_of_first1024_source_ordered_dev_train",
            "optimizer_steps": 0,
        },
        "activation": {
            "required_phases": ["dev_reader", "full_custody"],
            "incremental_planning_bound": "max(reader_native_peak_minus_its_startup_reserved,0)+4*synthetic_peak_tensor_bytes",
            "margin_bytes": 128 * 2**20,
            "require_bound_plus_margin_le_headroom": True,
            "meaning": "empirical bounded-dev planning envelope; not a canonical full-run validation or guaranteed mapped-page bound",
        },
        "dev_contract": old["dev"].copy(),
        "extrapolation": old["extrapolation"],
        "remaining_timing_limits": {
            k: old[k]
            for k in (
                "max_full_epoch_cycle_seconds",
                "max_fitting_selection_wall_seconds_per_run",
                "max_restore_reproduce_freeze_background_stage_seconds_per_run",
                "max_two_run_total_wall_seconds",
            )
        },
        "canonical_training_authorized": False,
        "selection_calibration_authorized": False,
        "policy_v1_compliance_claim": False,
    }


def validate_policy(profile, config, expected_hash=None):
    if content_hash(profile) != content_hash(policy_definition(config)):
        raise ValueError("Unsupported engineering profile/type/version/threshold diff.")
    if expected_hash is not None and content_hash(profile) != expected_hash:
        raise ValueError("Engineering profile identity mismatch.")
    return content_hash(profile)


def process_context():
    """Own-task Mach basic info and read-only XNU dispatch-pressure flags.

    Mach fields/48-byte ABI are from XNU mach/task_info.h; no external command.
    Optional telemetry failure is explicit and never replaces primary accounting.
    """
    result = {
        "dirty_private_bytes": None,
        "dirty_private_status": "not_measured_no_supported_binding",
    }
    try:
        lib = ctypes.CDLL(ctypes.util.find_library("System"), use_errno=True)
        pressure, size = ctypes.c_uint32(), ctypes.c_size_t(4)
        lib.sysctlbyname.argtypes = [
            ctypes.c_char_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        rc = lib.sysctlbyname(
            b"kern.memorystatus_vm_pressure_level",
            ctypes.byref(pressure),
            ctypes.byref(size),
            None,
            0,
        )
        result.update(
            pressure_dispatch_flags=pressure.value
            if rc == 0 and size.value == 4
            else None,
            pressure_errno=ctypes.get_errno() if rc else None,
            pressure_method="XNU_read_only_sysctl_dispatch_flags_1normal_2warning_4critical",
        )

        class Basic(ctypes.Structure):
            _fields_ = [
                ("virtual", ctypes.c_uint64),
                ("resident", ctypes.c_uint64),
                ("maximum", ctypes.c_uint64),
                ("times", ctypes.c_int32 * 4),
                ("policy", ctypes.c_int32),
                ("suspend", ctypes.c_int32),
            ]

        task = ctypes.c_uint32.in_dll(lib, "mach_task_self_").value
        info, count = Basic(), ctypes.c_uint32(12)
        lib.task_info.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        rc = lib.task_info(task, 20, ctypes.byref(info), ctypes.byref(count))
        if rc == 0 and count.value == 12 and ctypes.sizeof(Basic) == 48:
            result.update(
                current_rss_bytes=info.resident,
                virtual_address_bytes=info.virtual,
                current_rss_method="own_MACH_TASK_BASIC_INFO_64",
            )
        else:
            result.update(
                current_rss_bytes=None, virtual_address_bytes=None, task_info_error=rc
            )
    except (OSError, AttributeError, ValueError) as exc:
        result.update(
            pressure_dispatch_flags=None,
            current_rss_bytes=None,
            virtual_address_bytes=None,
            optional_telemetry_error=str(exc),
        )
    return result


def policy_snapshot():
    sample = memory_snapshot()
    sample.update(process_context())
    return sample


def validate_sample(sample, config, profile, *, launch):
    # Reuse original strict arithmetic/method validation with a synthetic available
    # metric unchanged; only its engineering admission threshold is separate.
    # check_reading takes a limits dict, never the model config; no mutation.
    limits = {**config["resource_gate"], **profile["limits"]}
    if not launch:
        limits["minimum_system_available_bytes_at_launch"] = limits[
            "stop_if_system_available_below_bytes"
        ]
    try:
        check_reading(sample, limits)
    except ResourceLimitError as exc:
        if str(exc) == "Launch available memory below 8 GiB.":
            raise ResourceLimitError(
                "Policy v2 launch available memory below4.5GiB."
                if launch
                else "Available memory below original4GiB continuing floor."
            ) from None
        raise
    pressure = sample.get("pressure_dispatch_flags")
    if pressure is not None and type(pressure) is not int:
        raise ResourceLimitError("Malformed pressure dispatch accounting.")
    if pressure is not None and pressure & 6:
        raise ResourceLimitError("Verified OS pressure warning/critical veto.")
    if pressure not in (None, 1, 2, 4):
        raise ResourceLimitError("Unsupported pressure dispatch accounting.")


class PolicyMonitor(ResourceMonitor):
    """Unchanged 50ms/signals/deadlines; compact serialized checks and overhead."""

    def __init__(
        self,
        config,
        profile,
        *,
        journal=None,
        probe=policy_snapshot,
        clock=time.monotonic,
        monitor_background=True,
    ):
        self.policy_hash = validate_policy(profile, config)
        self.config, self.profile = config, profile
        self.journal, self.phase = journal, "startup"
        self.phases, self.probe_seconds, self.probe_max_seconds = {}, 0.0, 0.0
        self._check_lock = threading.Lock()
        super().__init__(
            config["resource_gate"],
            probe=probe,
            clock=clock,
            monitor_background=monitor_background,
        )

    def check(self, *, launch=False):
        import json

        with self._check_lock:
            if self.error:
                raise ResourceLimitError(self.error)
            for name, end in tuple(self.deadlines.items()):
                if self.clock() > end:
                    raise ResourceLimitError(f"Time ceiling exceeded: {name}.")
            tick = self.clock()
            sample = self.probe()
            duration = self.clock() - tick
            self.probe_seconds += duration
            self.probe_max_seconds = max(duration, self.probe_max_seconds)
            compact = {k: v for k, v in sample.items() if k != "vm_stat_raw"}
            self.samples += 1
            self.last = compact
            for key in self.peak:
                self.peak[key] = max(self.peak[key], sample[key])
            available = sample["available_bytes"]
            self.minimum_available = min(
                available,
                self.minimum_available
                if self.minimum_available is not None
                else available,
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
                    sample["native_heap_reserved_bytes"],
                ),
                lifetime_peak_rss_at_samples_bytes=max(
                    phase["lifetime_peak_rss_at_samples_bytes"],
                    sample["peak_rss_bytes"],
                ),
                last=compact,
            )
            if self.journal:
                with self.journal.open("a") as file:
                    file.write(
                        json.dumps(
                            {
                                "elapsed_seconds": self.clock() - self.started,
                                "phase": self.phase,
                                "probe_seconds": duration,
                                **compact,
                            }
                        )
                        + "\n"
                    )
            validate_sample(sample, self.config, self.profile, launch=launch)
            # A slow probe must not hide an expired wall-time budget.
            for name, end in tuple(self.deadlines.items()):
                if self.clock() > end:
                    raise ResourceLimitError(f"Time ceiling exceeded: {name}.")

    def report(self):
        return {
            **super().report(),
            "engineering_policy_sha256": self.policy_hash,
            "policy_v1_compliance": False,
            "phases": self.phases,
            "probe_total_seconds": self.probe_seconds,
            "probe_max_seconds": self.probe_max_seconds,
            "monitor_implementation_version": self.profile["monitor"][
                "implementation_version"
            ],
            "journal_bytes": self.journal.stat().st_size
            if self.journal and self.journal.exists()
            else 0,
        }


def activation_decision(results, acceptance, profile):
    if set(results) != {"dev_reader", "full_custody"} or any(
        v.get("status") != "passed" for v in results.values()
    ):
        raise ValueError("Both complete reader phases required for policy activation.")
    increments = []
    for phase_name, record in results.items():
        resources = record["resources"]
        if (
            record.get("engineering_policy_sha256") != content_hash(profile)
            or record.get("model_config_sha256")
            != profile["model_config_scientific_sha256"]
            or record.get("custody_completed") is not True
            or record.get("view_events") != (64 if phase_name == "dev_reader" else 0)
            or record.get("optimizer_steps_started") != 0
            or record.get("optimizer_steps_completed") != 0
            or resources["minimum_available_bytes"]
            < profile["limits"]["stop_if_system_available_below_bytes"]
            or resources["native_heap_reserved_bytes"]
            > profile["limits"]["working_tensor_and_workspace_ceiling_bytes"]
            or resources["peak_rss_bytes"]
            > profile["limits"]["process_peak_rss_ceiling_bytes"]
        ):
            raise ValueError(
                "Reader resource/identity/custody/zero-step evidence invalid."
            )
        startup = resources["phases"]["startup"]["first"]["native_heap_reserved_bytes"]
        increments.append(max(0, resources["native_heap_reserved_bytes"] - startup))
    bound = (
        max(increments) + 4 * acceptance["workspace_measurement"]["peak_tensor_bytes"]
    )
    margin = profile["activation"]["margin_bytes"]
    return {
        "activated_for_bounded_dev": bound + margin <= profile["headroom_bytes"],
        "incremental_planning_bound_bytes": bound,
        "declared_margin_bytes": margin,
        "bound_plus_margin_bytes": bound + margin,
        "launch_headroom_bytes": profile["headroom_bytes"],
        "canonical_authorized": False,
        "policy_v1_compliance": False,
    }
