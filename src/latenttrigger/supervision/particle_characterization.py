"""Fixed Task0016 diagnostic authorization; one replacement additional allowance."""

import argparse
import json
import math
import os
import secrets
import sys
import time

from latenttrigger.supervision import particle_bounded_study as prior
from latenttrigger.supervision import particle_launcher as io
from latenttrigger.supervision import particle_sampling_benchmark as benchmark

PROMPT = "docs/prompts/0016-particle-runtime-characterization.md"
PROMPT_HASH = "fda62527dbca88e4d05a3724ebbb3d190e9880cef5ce73dc211bfb9e1d021d3d"
AUTHORIZATION = "configs/resources/particle_runtime_characterization_v1.json"
ACCEPTANCE = "data/task0016-synthetic-acceptance.json"
PLAN = "data/baselines/task0016-runtime-characterization-plan.json"
SLOT = "data/baselines/task0016-runtime-characterization-attempt.json"
OUTPUT = "data/baselines/task0016-runtime-characterization-study"
SUPERSESSION = "data/baselines/task0016-task0015-authorization-supersession.json"
READINESS = {
    "automatic": "data/task0016-readiness-auto.json",
    "manual": "data/task0016-readiness-manual.json",
}
PHASES = prior.PHASES
SECONDS = prior.SECONDS
THROUGHPUT_ERROR = "Frozen conservative dev extrapolation exceeds180s."
HISTORY = {
    "data/task0015-synthetic-acceptance.json": "4cd8dea4890895a8cf6d54dc9929a61bc5ab597a733322951baec134dde55f53",
    "data/task0015-final-synthetic-acceptance.json": "861c98c01d7c5a6cc81fdbf0f9a9f9d6589424b34f5164845d27205bbdf9c155",
    "data/task0015-sampling-benchmark/matrix.json": "4d981be4cfc2cb260b1eb2f4815a474aa1cff2a85f28961c1bf67186339406ac",
    "data/task0015-v4-accounting-repair-validation/validation.json": "010819c1850ae5ed85793d1ab9ce4489c27bb04cf78d45fece9a315dec0f8a05",
    "results/tables/final/task0015-particle-bounded-sampling-summary.json": "4c887079f667e8740cd7da7fa5d070db2a153e7c7fe981428e7bf07e6603eabd",
    prior.MONITOR: "68cd539a2b7f6916e60ac1bfcc670a3c65bb22bed1e8a6c0d59cee2f8b0bd62e",
}
MONITOR_SOURCES = {
    "src/latenttrigger/training/particle_monitor_v4.py": "9874d08638e21329bbf4392fc3dc097228ce21742060e8f5a8065c5c1652552f",
    "src/latenttrigger/supervision/particle_sampling.py": "a40d551236bcd5da564cd8aff5b3d7bf046e0bb34de1a1f582592491f51a78f6",
    "src/latenttrigger/supervision/particle_collector.py": "39d66cce6fc6e9e8a98cfec7018c0aacc148be98b5fb7fcacd04c1f10b251fd5",
}


def definition():
    return {
        "schema_version": 1,
        "authorization_version": 1,
        "type": "Task0016_single_diagnostic_runtime_characterization",
        "task": "0016",
        "authorization_prompt_sha256": PROMPT_HASH,
        "design_sha256": io.DESIGN_HASH,
        "model_config_sha256": io.CONFIG_HASH,
        "profile_sha256": io.PROFILE_HASH,
        "adopted_observation_manifest_sha256": prior.MONITOR_HASH,
        "adopted_monitor_sources_sha256": MONITOR_SOURCES,
        "limits_bytes": {
            "launch_available": 4831838208,
            "continuing_available": 4294967296,
            "native_reserved": 536870912,
            "lifetime_peak_RSS": 6442450944,
        },
        "observation_seconds": {"cadence": 0.05, "age_upper": 0.1, "probe_timeout": 2},
        "unchanged_full_run_policy": {
            "maximum_epochs": 200,
            "patience": 20,
            "min_delta": 0,
            "fit_seconds_per_run": 36000,
            "postfit_seconds_per_run": 3600,
            "two_run_seconds": 79200,
        },
        "historical_evidence_sha256": HISTORY,
        "prospective_synthetic_admission": "current_correctness_source_acceptance_unchanged_numerics_verified_history;no_relative_speed_threshold",
        "superseded_Task0015_synthetic_criterion": "median_complete_v4_le_median_v3_div3",
        "Task0015_historical_material_pass": False,
        "Task0015_paired_median_gain": 2.1402944935480797,
        "Task0015_observation_manifest_not_reinterpreted": True,
        "replaces_unspent_locked_Task0015_additional_budget": True,
        "original_steps_started_completed": 96,
        "maximum_additional_steps_started": 96,
        "maximum_cumulative_steps_started": 192,
        "maximum_unique_dev_IDs_same_original_sample": 1024,
        "reader_subset_events": 64,
        "phase_order": list(PHASES),
        "phase_limits_seconds": SECONDS,
        "readiness_seconds": 30,
        "readiness_readings": 3,
        "readiness_span_minimum_seconds": 5,
        "original_real_cycle_target_seconds": 180,
        "projection": "2*(699957*max(train_pass_seconds)/1024+74749*score_pass_seconds/1024)",
        "additional_scope": "one_fresh_disposable_reader_and_three_pass_dev_diagnostic_only",
        "canonical_fit_selection_calibration_freeze_authorized": False,
        "full_custody_replay_authorized": False,
        "source_acceptance": "current_full_source_map_plus_actual_test_evidence_and_workspace",
    }


def validate_authorization(value):
    if io.digest(value) != io.digest(definition()):
        raise ValueError("Unsupported Task0016 authorization/types/scope.")
    if io.file_hash(io.ROOT / PROMPT) != PROMPT_HASH:
        raise ValueError("Task0016 actual prompt changed.")
    for rel, expected in (
        (io.CONFIG, io.CONFIG_HASH),
        (io.DESIGN, io.DESIGN_HASH),
        (io.PROFILE, io.PROFILE_HASH),
        (prior.MONITOR, prior.MONITOR_HASH),
    ):
        if io.digest(io.read(io.ROOT / rel)) != expected:
            raise ValueError("Scientific/profile/observation relationship changed.")
    for rel, expected in MONITOR_SOURCES.items():
        if io.file_hash(io.ROOT / rel) != expected:
            raise ValueError("Frozen corrected v4 implementation changed.")
    if (
        io.file_hash(io.ROOT / "configs/data/lhco_rnd_v5.json")
        != io.PREDECESSOR["configs/data/lhco_rnd_v5.json"]
    ):
        raise ValueError("Frozen input/scaler identity changed.")
    return io.digest(value)


def current_acceptance():
    a = io.read(io.ROOT / ACCEPTANCE)
    w = a.get("workspace_measurement", {})
    if (
        type(a.get("pytest_exit_code")) is not int
        or a.get("pytest_exit_code") != 0
        or type(a.get("pytest_passed")) is not int
        or a["pytest_passed"] <= 0
        or a.get("pytest_cases") != a["pytest_passed"]
        or a.get("source_sha256") != io.source_hashes()
        or a.get("config_sha256") != io.CONFIG_HASH
        or w.get("parameter_count") != 478
        or w.get("synthetic_optimizer_steps") != 2
        or type(w.get("peak_tensor_bytes")) is not int
        or not 0 < w["peak_tensor_bytes"] <= 512 * 2**20
    ):
        raise ValueError("Actual current full synthetic acceptance required.")
    for suffix, key in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        if io.file_hash((io.ROOT / ACCEPTANCE).with_suffix(suffix)) != a[key]:
            raise ValueError("Current acceptance test evidence changed.")
    return a


def refuse_Task0015_consumption():
    paths = [
        prior.PLAN,
        prior.SLOT,
        prior.OUTPUT,
        prior.READINESS_AUTO,
        prior.READINESS_MANUAL,
    ]
    paths += [
        str(io.ROOT / p)
        .removeprefix(str(io.ROOT) + "/")
        .replace(".json", ".reservation.json")
        for p in (prior.READINESS_AUTO, prior.READINESS_MANUAL)
    ]
    paths += [
        "data/task0015-readiness-auto-evidence",
        "data/task0015-readiness-manual-evidence",
    ]
    if any((io.ROOT / p).exists() for p in paths):
        raise ValueError(
            "Unexpected Task0015 execution; reconcile, no additional allowance."
        )


def verify_history():
    refuse_Task0015_consumption()
    historical = prior.verify_predecessor()
    for rel, expected in HISTORY.items():
        if io.file_hash(io.ROOT / rel) != expected:
            raise ValueError("Pinned Task0015 history changed.")
    initial = io.read(io.ROOT / "data/task0015-synthetic-acceptance.json")
    final = io.read(io.ROOT / "data/task0015-final-synthetic-acceptance.json")
    matrix = io.read(io.ROOT / "data/task0015-sampling-benchmark/matrix.json")
    repair = io.read(
        io.ROOT / "data/task0015-v4-accounting-repair-validation/validation.json"
    )
    if (
        initial["pytest_passed"] != 530
        or final["pytest_passed"] != 532
        or initial["pytest_exit_code"] != 0
        or final["pytest_exit_code"] != 0
        or matrix["acceptance_sha256"]
        != HISTORY["data/task0015-synthetic-acceptance.json"]
        or matrix["source_sha256"] != initial["source_sha256"]
        or matrix["decision"] != benchmark.evaluate(matrix["rows"])
        or matrix["decision"]["material_improvement_pass"] is not False
        or matrix["decision"]["exact_numerical_parity"] is not True
        or repair["source_sha256"] != final["source_sha256"]
        or repair["acceptance_sha256"]
        != HISTORY["data/task0015-final-synthetic-acceptance.json"]
        or any(
            r["numerical_identity"] != matrix["rows"][0]["numerical_identity"]
            for r in repair["rows"]
        )
    ):
        raise ValueError("Historical original paired/final repair evidence mismatch.")
    # Final Task0015 entries are unchanged historical files, not today's complete map.
    for rel, expected in final["source_sha256"].items():
        if io.file_hash(io.ROOT / rel) != expected:
            raise ValueError("Historical corrected source entry changed.")
    for path, a in (
        ("data/task0015-synthetic-acceptance.json", initial),
        ("data/task0015-final-synthetic-acceptance.json", final),
    ):
        for suffix, key in (
            (".pytest.xml", "pytest_xml_sha256"),
            (".pytest.log", "pytest_log_sha256"),
        ):
            if io.file_hash((io.ROOT / path).with_suffix(suffix)) != a[key]:
                raise ValueError("Historical test evidence changed.")
    return historical


def plan_definition():
    a = current_acceptance()
    authorization_hash = validate_authorization(io.read(io.ROOT / AUTHORIZATION))
    h = verify_history()
    return {
        "schema_version": 1,
        "task": "0016",
        "scope": "diagnostic_only",
        "authorization_sha256": authorization_hash,
        "prompt_sha256": PROMPT_HASH,
        "current_acceptance_sha256": io.file_hash(io.ROOT / ACCEPTANCE),
        "source_sha256": a["source_sha256"],
        "predecessor_receipt_sha256": h["receipt_sha256"],
        "Task0015_original_history_sha256": HISTORY,
        "original_steps": 96,
        "additional_started_maximum": 96,
        "cumulative_started_maximum": 192,
        "fixed_output": str(io.ROOT / OUTPUT),
        "phase_order": list(PHASES),
        "phase_limits_seconds": SECONDS,
        "canonical_authorized": False,
        "historical_torch_version": io.read(io.ROOT / io.ACCEPTANCE)[
            "workspace_measurement"
        ]["torch_version"],
        "current_torch_version": a["workspace_measurement"]["torch_version"],
    }


def prepare():
    plan = plan_definition()
    supersession = {
        "task": "0016",
        "prompt_sha256": PROMPT_HASH,
        "authorization_sha256": plan["authorization_sha256"],
        "Task0015_original_history_sha256": HISTORY,
        "supersedes_unspent_additional_budget_not_original_failure": True,
        "additional_started_maximum": 96,
        "cumulative_started_maximum": 192,
    }
    for rel, value in ((SUPERSESSION, supersession), (PLAN, plan)):
        path = io.ROOT / rel
        if path.exists():
            if io.read(path) != value:
                raise ValueError("Fixed prospective provenance changed; no overwrite.")
        else:
            io.exclusive(path, value)
    return plan


def verify_plan():
    expected = plan_definition()
    if io.read(io.ROOT / PLAN) != expected:
        raise ValueError("Current plan/source/authorization/lineage mismatch.")
    return expected


def project(train, score):
    if (
        type(train) is not list
        or len(train) != 3
        or any(
            type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in train
        )
        or type(score) not in (int, float)
        or not math.isfinite(score)
        or score <= 0
    ):
        raise ValueError("Complete finite original timing inputs required.")
    return 2 * (699957 * max(train) / 1024 + 74749 * score / 1024)


def complete_gate(gate, audit):
    projected = project(gate["train_pass_seconds"], gate["score_pass_seconds"])
    if (
        any(
            type(gate[k]) is not int
            for k in ("passes", "optimizer_steps", "unique_events")
        )
        or any(
            type(audit[k]) is not int
            for k in (
                "optimizer_steps_started",
                "optimizer_steps_completed",
                "unique_dev_sample_events",
            )
        )
        or gate["passes"] != 3
        or gate["optimizer_steps"] != 96
        or gate["unique_events"] != 1024
        or gate["extrapolated_full_cycle_seconds"] != projected
        or gate["feasibility_pass"] is not (projected <= 180)
        or audit["optimizer_steps_started"] != 96
        or audit["optimizer_steps_completed"] != 96
        or audit["possible_inflight_optimizer_step"] is not False
        or audit["unique_dev_sample_events"] != 1024
        or len(audit["population_access"]) != 4
        or any(
            x["status"] != "completed"
            or x["events_read"] != 1024
            or x["split"] != "train_background"
            or x["allow_test"] is not False
            or x["include_labels"] is not False
            or x["dev_only"] is not True
            for x in audit["population_access"]
        )
    ):
        raise ValueError(
            "Incomplete/foreign/inflight characterization cannot be completed."
        )
    return projected


def numeric_comparison(gate, plan):
    old = io.read(
        io.ROOT / "data/baselines/task0013-particle-host-study/dev/dev-gate.json"
    )
    if plan["historical_torch_version"] != plan["current_torch_version"]:
        return {
            "status": "runtime_binding_different_comparison_unresolved",
            "canonical_proposal_blocked": True,
        }
    fields = (
        "last_online_objective",
        "same_sample_score_mean",
        "same_sample_score_sha256",
    )
    result = {
        "status": "exact_match"
        if all(gate[k] == old[k] for k in fields)
        else "unexplained_numerical_mismatch",
        "compared_fields": list(fields),
        "old_values": {k: old[k] for k in fields},
        "new_values": {k: gate[k] for k in fields},
    }
    result["canonical_proposal_blocked"] = result["status"] != "exact_match"
    return result


def verify_readiness_receipt(receipt):
    """Independent live-provenance audit before reserving data work."""
    rows = receipt.get("readings")
    if (
        receipt.get("status") != "passed"
        or type(rows) is not list
        or len(rows) != 3
        or receipt.get("plan_sha256") != io.file_hash(io.ROOT / PLAN)
        or receipt.get("current_acceptance_sha256")
        != io.file_hash(io.ROOT / ACCEPTANCE)
        or type(receipt.get("new_steps_started")) is not int
        or receipt.get("new_steps_started") != 0
    ):
        raise ValueError("Actual complete current readiness receipt required.")
    times = [r.get("sample_monotonic") for r in rows]
    if (
        any(type(t) not in (int, float) or not math.isfinite(t) for t in times)
        or times[-1] - times[0] < 5
        or times != sorted(times)
        or not 0 <= receipt["elapsed_seconds_including_imports"] <= 30
    ):
        raise ValueError("Bounded stable readiness timing invalid.")
    sampler = receipt["resources"]["sampler"]
    if (
        sampler["latched_failure"] is not None
        or sampler["owned_thread_alive"] is not False
    ):
        raise ValueError("Readiness sampling/cleanup failed.")
    for row in rows:
        g = row["guard"]
        if (
            g.get("synthetic_not_readiness") is not False
            or g.get("host_backend") != "system_vm_stat_oneshot_host_v4"
            or g.get("host_validation_status") != "valid_primary_fields"
            or type(g.get("host_age_upper_seconds")) not in (int, float)
            or not 0 <= g["host_age_upper_seconds"] <= 0.1
            or (
                g.get("pressure_dispatch_flags") is not None
                and type(g.get("pressure_dispatch_flags")) is not int
            )
            or g.get("pressure_dispatch_flags") not in (None, 1)
            or type(g.get("available_bytes")) is not int
            or g["available_bytes"] < 4831838208
            or type(g.get("native_heap_reserved_bytes")) is not int
            or not 0 < g["native_heap_reserved_bytes"] <= 536870912
            or type(g.get("peak_rss_bytes")) is not int
            or not 0 < g["peak_rss_bytes"] <= 6442450944
        ):
            raise ValueError("Synthetic/invalid live readiness guard refused.")
    return True


def dispatch_readiness(mode):
    if mode not in READINESS:
        raise ValueError("Only fixed automatic/manual route.")
    verify_plan()
    target = io.ROOT / READINESS[mode]
    token, started = secrets.token_hex(24), time.monotonic()
    io.exclusive(
        target.with_suffix(".reservation.json"),
        {
            "mode": mode,
            "token": token,
            "parent_pid": os.getpid(),
            "plan_sha256": io.file_hash(io.ROOT / PLAN),
            "started_monotonic": started,
            "status": "read_only_once_no_retry",
        },
    )
    try:
        dispatch = io.dispatch(
            [
                sys.executable,
                "-m",
                "latenttrigger.supervision.particle_characterization_worker",
                "--readiness",
                mode,
                "--token",
                token,
            ],
            target.with_suffix(".log"),
            30,
            started=started,
        )
    except BaseException as exc:
        dispatch = {"returncode": 1, "error": str(exc)}
    if not target.exists():
        io.exclusive(
            target,
            {
                "status": "failed",
                "error": "Readiness ended before complete receipt; no real reservation.",
                "new_steps_started": 0,
                "population_requests": 0,
                "parent_dispatch": dispatch,
            },
        )
    receipt = io.read(target)
    if dispatch["returncode"] or receipt["status"] != "passed":
        return False, receipt
    verify_readiness_receipt(receipt)
    return True, receipt


def reserve_additional(mode):
    verify_plan()
    refuse_Task0015_consumption()
    if mode not in READINESS or (io.ROOT / OUTPUT).exists():
        raise ValueError("Invalid/consumed additional route.")
    ready = io.read(io.ROOT / READINESS[mode])
    verify_readiness_receipt(ready)
    io.exclusive(
        io.ROOT / SLOT,
        {
            "task": "0016",
            "status": "reserved_no_retry",
            "replaces_locked_Task0015_allowance": True,
            "mode": mode,
            "plan_sha256": io.file_hash(io.ROOT / PLAN),
            "readiness_sha256": io.file_hash(io.ROOT / READINESS[mode]),
            "original_steps": 96,
            "maximum_additional_started_steps": 96,
            "maximum_cumulative_started_steps": 192,
        },
    )


def study(mode):
    io.assert_lightweight()
    if mode not in READINESS:
        raise ValueError("Only fixed automatic/manual route.")
    if (io.ROOT / SLOT).exists() or (io.ROOT / OUTPUT).exists():
        raise FileExistsError("Additional real attempt consumed; no retry.")
    prepare()
    ready, receipt = dispatch_readiness(mode)
    if not ready:
        return {
            "status": "readiness_deferred_attempt_unreserved",
            "mode": mode,
            "readiness": receipt,
            "new_steps_started": 0,
            "cumulative_started": 96,
            "slot_reserved": False,
        }
    reserve_additional(mode)
    directory = io.ROOT / OUTPUT
    directory.mkdir(exist_ok=False)
    state = {
        "task": "0016",
        "status": "started",
        "stages": [],
        "slot_reserved": True,
        "canonical_authorized": False,
        "original_steps": 96,
    }
    ledger = directory / "workflow.json"
    io.atomic(ledger, state)
    phase = PHASES[0]
    try:
        for phase in PHASES:
            verify_plan()
            prior.authorize(phase, state)
            started, token = time.monotonic(), secrets.token_hex(24)
            io.exclusive(
                directory / f"{phase}-reservation.json",
                {
                    "phase": phase,
                    "token": token,
                    "parent_pid": os.getpid(),
                    "plan_sha256": io.file_hash(io.ROOT / PLAN),
                    "slot_sha256": io.file_hash(io.ROOT / SLOT),
                    "started_monotonic": started,
                    "status": "reserved_no_automatic_retry",
                    "maximum_optimizer_steps": 96 if phase == "dev" else 0,
                },
            )
            dispatched = io.dispatch(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.supervision.particle_characterization_worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                directory / f"{phase}.log",
                SECONDS[phase],
                started=started,
                journal=directory / phase / "guard-samples.jsonl",
            )
            result_path = directory / phase / "stage-result.json"
            result = (
                io.read(result_path)
                if result_path.exists()
                else {
                    "phase": phase,
                    "status": "failed",
                    "error": "No final worker result; retain partial audit.",
                }
            )
            result["parent_dispatch"] = dispatched
            state["stages"].append(result)
            io.atomic(ledger, state)
            supported_status = (
                ("passed", "characterization_completed_original_throughput_failed")
                if phase == "dev"
                else ("passed",)
            )
            if (
                dispatched["returncode"]
                or result["status"] not in supported_status
                or result.get("plan_sha256") != io.file_hash(io.ROOT / PLAN)
                or result.get("current_acceptance_sha256")
                != io.file_hash(io.ROOT / ACCEPTANCE)
            ):
                raise RuntimeError(
                    result.get("error", "Failed/foreign worker receipt.")
                )
        state["status"] = (
            "characterization_completed_original_throughput_failed_canonical_blocked"
            if state["stages"][-1]["status"] != "passed"
            else "bounded_v4_characterization_passed_canonical_pending"
        )
    except BaseException as exc:
        state.update(
            status="bounded_v4_characterization_attempt_failed",
            failed_phase=phase,
            error=str(exc),
        )
        if not state["stages"] or state["stages"][-1]["phase"] != phase:
            state["stages"].append(
                {
                    "phase": phase,
                    "status": "failed_or_interrupted",
                    "partial_audit_must_be_reconciled": True,
                }
            )
    audit_path = directory / "dev/access-audit.json"
    audit = io.read(audit_path) if audit_path.exists() else {}
    state.update(
        new_steps_started=audit.get("optimizer_steps_started", 0),
        new_steps_completed=audit.get("optimizer_steps_completed", 0),
        new_inflight_steps=audit.get("optimizer_steps_started", 0)
        - audit.get("optimizer_steps_completed", 0),
        cumulative_started_steps=96 + audit.get("optimizer_steps_started", 0),
    )
    io.atomic(ledger, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--automatic", action="store_true")
    choice.add_argument("--run-once", action="store_true")
    args = parser.parse_args()
    result = study("automatic" if args.automatic else "manual")
    print(json.dumps(result, indent=2))
    if result["status"] == "bounded_v4_characterization_attempt_failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
