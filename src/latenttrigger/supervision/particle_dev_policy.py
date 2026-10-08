"""Strict Task0018 development-only envelope; no canonical execution permission."""

from latenttrigger.supervision import particle_launcher as io

POLICY = "configs/resources/particle_shared_host_dev_policy_v1.json"
PROMPT = "docs/prompts/0018-particle-shared-host-policy.md"
PROMPT_HASH = "b4e4a0530d0eaaf53a6ba14bbfb296baf47f5a24f3e0a6e801bdcaff49adc1b3"
NAME = "shared-host-dev-v1"
DEV = "data/processed/lhco-rd-v1/schema-v1/dev"
SLOT = "data/baselines/task0016-runtime-characterization-attempt.json"
OUTPUT = "data/baselines/task0016-runtime-characterization-study"


def definition():
    return {
        "schema_version": 1,
        "policy_version": 1,
        "type": "bounded_development_process_budget",
        "name": NAME,
        "authorization_task": "0018",
        "authorization_prompt_sha256": PROMPT_HASH,
        "config_sha256": io.CONFIG_HASH,
        "design_sha256": io.DESIGN_HASH,
        "input_identity": io.read(io.ROOT / io.CONFIG)["input"],
        "historical_policy_v2_sha256": io.PROFILE_HASH,
        "historical_observation_v4_sha256": "d11640071b854b08dfc9cd59724dd2732abe8ebff1195000e8321e66a1229c63",
        "implementation": "process_budget_guard_v1_cached_DarwinBindings",
        "source_acceptance": "current_complete_src_and_top_level_tests;execution_plan_binds_actual_acceptance",
        "global_available": "context_only_displayed_free_plus_inactive_times_actual_page_size",
        "global_minimum_at_launch_bytes": None,
        "global_continuing_floor_bytes": None,
        "host_age_is_workload_veto": False,
        "equivalent_to_v4_host_primary": False,
        "process_lifetime_peak_rss_ceiling_bytes": 536870912,
        "whole_native_malloc_reserved_ceiling_bytes": 268435456,
        "pressure": {
            "1": "normal_permit",
            "2": "warning_advisory_permit",
            "4": "critical_veto",
            "unknown": "disclose_permit",
            "malformed": "fail_closed",
        },
        "watcher_intent_seconds": 0.05,
        "context_query_timeout_seconds": 2,
        "context": "one_bounded_optional_system_vm_stat_at_startup_and_phase_boundaries;never_admission",
        "primary": "fresh_own_process_peak_RSS_whole_malloc_reserved_in_use_and_pressure_each_boundary_and_pre_step",
        "allowed_store": DEV,
        "allowed_population": "train_background",
        "dev_only": True,
        "allowed_phases": ["check", "dev_reader", "dev_readiness", "dev"],
        "phase_limits_seconds": {
            "check": 30,
            "dev_reader": 60,
            "dev_readiness": 30,
            "dev": 300,
        },
        "reader_first_ids": 64,
        "sample_first_source_ordered_ids": 1024,
        "training_passes": 3,
        "scoring_passes": 1,
        "batch_size": 32,
        "workers": 0,
        "cpu_intra_threads": 1,
        "cpu_inter_threads": 1,
        "canonical_single_slot": SLOT,
        "single_real_output": OUTPUT,
        "original_started_steps": 96,
        "additional_started_ceiling": 96,
        "cumulative_started_ceiling": 192,
        "new_optimizer_allowance": 0,
        "projection": "2*(699957*max(train_pass_seconds)/1024+74749*score_pass_seconds/1024)",
        "projection_target_seconds": 180,
        "full_run_limits_unchanged_not_authorized": {
            "max_epochs": 200,
            "patience": 20,
            "min_delta": 0,
            "cycle_seconds": 180,
            "fit_seconds": 36000,
            "postfit_seconds": 3600,
            "two_run_seconds": 79200,
        },
        "full_store_selection_calibration_test_fit_freeze_authorized": False,
    }


def validate(policy, config):
    if (
        io.digest(policy) != io.digest(definition())
        or io.digest(config) != io.CONFIG_HASH
        or io.digest(io.read(io.ROOT / io.DESIGN)) != io.DESIGN_HASH
        or io.digest(io.read(io.ROOT / io.PROFILE)) != io.PROFILE_HASH
        or io.file_hash(io.ROOT / PROMPT) != PROMPT_HASH
    ):
        raise ValueError(
            "Unsupported shared-host dev policy/science/prompt relationship."
        )
    return io.digest(policy)


def scope(phase, store=DEV, population="train_background", dev_only=True):
    if (
        phase not in ("check", "dev_reader", "dev_readiness", "dev")
        or store != DEV
        or population != "train_background"
        or dev_only is not True
    ):
        raise ValueError(
            "Only fixed dev store/background characterization scope authorized."
        )
