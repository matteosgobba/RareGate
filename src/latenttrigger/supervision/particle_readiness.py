"""User-triggered read-only history and deliberate run sharing the Task0016 slot."""

import math
import os
import re
import secrets
import sys
import time

from latenttrigger.supervision import particle_characterization as previous
from latenttrigger.supervision import particle_launcher as io

PROMPT = "docs/prompts/0017-particle-readiness-workflow.md"
PROMPT_HASH = "ad3b2490bb2f7860bb4c1f469afbcbb150c8ad2e1a8ecd5e9b0b47561251242a"
MANIFEST = "configs/resources/particle_readiness_workflow_v1.json"
ACCEPTANCE = "data/task0017-synthetic-acceptance.json"
HISTORY_ROOT = "data/baselines/particle-readiness-history/v1"
PLAN = "data/baselines/task0017-readiness-execution-plan.json"
# Exactly one anchor and one real output; no independently spendable Task0017 slot.
SLOT, OUTPUT = previous.SLOT, previous.OUTPUT
PHASES, SECONDS = previous.PHASES, previous.SECONDS
PREDECESSOR = {
    previous.AUTHORIZATION: "18022b248b667567a7d6df54b3bb27f90bc1eae9bd6e8a55513548c0ef7b1b4d",
    previous.ACCEPTANCE: "3fe522513b5a0d0ec00e86e3dc2f6b5083c2ed6f7728abcc4930b873c4b3d79e",
    previous.PLAN: "f4a1ce7569ff7ab5a698ad1fc6b4214ec1d3c3d164bd1697f0d1634611245215",
    previous.SUPERSESSION: "aebec659b36ec3223e521d699d24077fcfe17ef24e8a99ff3362f3bf2bae5465",
    previous.READINESS[
        "automatic"
    ]: "5dc928785eab9971e5a712dd9105f84242c6d64090d0bafd7d8fdb385dcd00eb",
    previous.READINESS[
        "manual"
    ]: "e3004d4bf4184718cdb320286f2c4c70e65933bacc504ac40cd63777ac9ec48e",
    "data/task0016-readiness-auto.reservation.json": "7eeac9c862693a82b5c2066b099d6b962066245882c9af79a600bd0c89c9708b",
    "data/task0016-readiness-manual.reservation.json": "f894822bcb0d0fddb0de26f7c8b060d2a2dd1c6ded502096d6e15e7fa732de87",
}


def definition():
    return {
        "schema_version": 1,
        "implementation_version": 1,
        "task": "0017",
        "type": "explicit_user_readiness_history_shared_Task0016_budget",
        "prompt_sha256": PROMPT_HASH,
        "adopted_Task0016_authorization_sha256": "92e370cba7cb8ba3762ecc91a5c85ff06e1b36c96b8abfa51f754e8d4cdd3bce",
        "adopted_v4_manifest_sha256": previous.prior.MONITOR_HASH,
        "config_sha256": io.CONFIG_HASH,
        "design_sha256": io.DESIGN_HASH,
        "profile_sha256": io.PROFILE_HASH,
        "historical_failed_checks_sha256": PREDECESSOR,
        "history_root": HISTORY_ROOT,
        "check_seconds_including_imports_cleanup": 30,
        "check_only_never_reserves_or_dispatches_real_work": True,
        "readiness_repeated_only_by_explicit_separate_user_invocations": True,
        "run_always_owns_new_readiness_no_receipt_argument": True,
        "readiness_pass_not_execution_permission_or_bearer_token": True,
        "canonical_single_slot": SLOT,
        "single_real_output": OUTPUT,
        "separate_execution_plan": PLAN,
        "original_steps": 96,
        "additional_maximum_started": 96,
        "cumulative_maximum_started": 192,
        "new_optimizer_allowance": 0,
        "phase_order": list(PHASES),
        "phase_limits_seconds": SECONDS,
        "unchanged_projection_target_seconds": 180,
        "diagnostic_after_pressure_veto": "at_most_one_later_system_snapshot_within30s;never_admission_or_veto_reversal",
        "canonical_fit_selection_freeze_calibration_authorized": False,
        "old_records_and_monitor_immutable": True,
    }


def current_acceptance():
    a = io.read(io.ROOT / ACCEPTANCE)
    w = a.get("workspace_measurement", {})
    if (
        type(a.get("pytest_exit_code")) is not int
        or a["pytest_exit_code"] != 0
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
        raise ValueError("Current full source-bound synthetic acceptance required.")
    for suffix, key in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        if io.file_hash((io.ROOT / ACCEPTANCE).with_suffix(suffix)) != a[key]:
            raise ValueError("Current acceptance evidence identity changed.")
    return a


def verify_history():
    previous.verify_history()
    for rel, h in PREDECESSOR.items():
        if io.file_hash(io.ROOT / rel) != h:
            raise ValueError("Task0016 failed-check lineage changed; reconcile first.")
    accepted = io.read(io.ROOT / previous.ACCEPTANCE)
    if accepted["pytest_passed"] != 576:
        raise ValueError("Wrong historical Task0016 acceptance.")
    for rel, h in accepted["source_sha256"].items():
        if io.file_hash(io.ROOT / rel) != h:
            raise ValueError("Historical Task0016 source entry changed.")
    for suffix, key in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        if (
            io.file_hash((io.ROOT / previous.ACCEPTANCE).with_suffix(suffix))
            != accepted[key]
        ):
            raise ValueError("Historical Task0016 test evidence changed.")
    plan = io.read(io.ROOT / previous.PLAN)
    if (
        plan["source_sha256"] != accepted["source_sha256"]
        or plan["current_acceptance_sha256"] != PREDECESSOR[previous.ACCEPTANCE]
    ):
        raise ValueError("Historical source/plan mismatch.")
    for mode in previous.READINESS:
        r = io.read(io.ROOT / previous.READINESS[mode])
        audit_path = (
            io.ROOT / f"data/task0016-readiness-{mode}-evidence/access-audit.json"
        )
        a = io.read(audit_path)
        if (
            r["status"] != "failed"
            or r["plan_sha256"] != PREDECESSOR[previous.PLAN]
            or r["current_acceptance_sha256"] != PREDECESSOR[previous.ACCEPTANCE]
            or r["audit_sha256"] != io.file_hash(audit_path)
            or r["new_steps_started"] != 0
            or r["new_steps_completed"] != 0
            or r["new_inflight_steps"] != 0
            or a["population_access"]
            or a["custody_access"]
            or a["optimizer_steps_started"] != 0
            or a["optimizer_steps_completed"] != 0
            or a["unique_dev_sample_events"] != 0
            or a["possible_inflight_optimizer_step"] is not False
        ):
            raise ValueError(
                "Failed read-only predecessor unexpectedly consumed data/steps."
            )
    manual = io.read(io.ROOT / previous.READINESS["manual"])
    if (
        manual["resources"]["last_process_observation"]["pressure_dispatch_flags"] != 2
        or manual["resources"]["minimum_available_bytes"] is not None
    ):
        raise ValueError("Task0016 manual WARN/unmeasured-memory evidence changed.")


def identity():
    verify_history()
    previous.validate_authorization(io.read(io.ROOT / previous.AUTHORIZATION))
    if (
        io.digest(io.read(io.ROOT / MANIFEST)) != io.digest(definition())
        or io.file_hash(io.ROOT / PROMPT) != PROMPT_HASH
    ):
        raise ValueError("Unsupported readiness workflow/prompt.")
    a = current_acceptance()
    return {
        "workflow_sha256": io.digest(definition()),
        "prompt_sha256": PROMPT_HASH,
        "current_acceptance_sha256": io.file_hash(io.ROOT / ACCEPTANCE),
        "source_sha256": a["source_sha256"],
        "config_sha256": io.CONFIG_HASH,
        "profile_sha256": io.PROFILE_HASH,
        "v4_sha256": previous.prior.MONITOR_HASH,
        "historical_torch_version": io.read(io.ROOT / io.ACCEPTANCE)[
            "workspace_measurement"
        ]["torch_version"],
        "current_torch_version": a["workspace_measurement"]["torch_version"],
    }


def invocation_path(value):
    if type(value) is not str or re.fullmatch(r"[a-f0-9]{32}", value) is None:
        raise ValueError("Unsafe readiness history ID.")
    return io.ROOT / HISTORY_ROOT / value


def permission():
    if (io.ROOT / SLOT).exists():
        return {
            "available": False,
            "reason": "canonical real slot exists (consumed/partial/foreign); no reset",
            "original_steps": 96,
            "additional_ceiling": 96,
            "cumulative_ceiling": 192,
        }
    if (io.ROOT / OUTPUT).exists() or (io.ROOT / PLAN).exists():
        return {
            "available": False,
            "reason": "unexpected fixed real output/plan without slot; reconcile",
            "original_steps": 96,
            "additional_ceiling": 96,
            "cumulative_ceiling": 192,
        }
    return {
        "available": True,
        "reason": "one already authorized additional slot unreserved",
        "original_steps": 96,
        "additional_ceiling": 96,
        "cumulative_ceiling": 192,
    }


def classify_failure(message):
    expected = (
        "Verified pressure warning/critical veto.",
        "Available memory below original4GiB continuing floor.",
        "Policy v2 launch available memory below4.5GiB.",
        "Verified OS pressure warning/critical veto.",
        "Process RSS/native ceiling exceeded.",
        "Host observation age exceeds100ms.",
        "Fresh synchronous host refresh unavailable within100ms.",
    )
    return "not_ready" if message in expected else "error"


def validate_check(receipt, res):
    if receipt.get("status") not in ("ready", "not_ready", "error"):
        raise ValueError("Unsupported readiness receipt status.")
    if (
        receipt.get("invocation_id") != res["invocation_id"]
        or receipt.get("reservation_sha256")
        != io.file_hash(invocation_path(res["invocation_id"]) / "reservation.json")
        or receipt.get("binding") != res["binding"]
        or receipt.get("action") != res["action"]
        or receipt.get("check_only_zero_data_steps") is not True
        or receipt.get("real_slot_reserved_by_check") is not False
    ):
        raise ValueError("Foreign/malformed readiness receipt.")
    elapsed = receipt.get("elapsed_seconds_including_imports_cleanup")
    if (
        type(elapsed) not in (int, float)
        or not math.isfinite(elapsed)
        or not 0 <= elapsed <= 30
    ):
        raise ValueError("Readiness deadline exceeded.")
    if receipt["status"] != "ready":
        return False
    rows = receipt.get("readings")
    if type(rows) is not list or len(rows) != 3:
        raise ValueError("Partial readiness cannot be ready.")
    times = [x.get("sample_monotonic") for x in rows]
    if (
        any(type(t) not in (int, float) or not math.isfinite(t) for t in times)
        or times != sorted(times)
        or times[-1] - times[0] < 5
        or not res["started_monotonic"]
        <= times[0]
        <= times[-1]
        <= receipt.get("finished_monotonic", -1)
        <= res["started_monotonic"] + 30
        or receipt.get("finished_monotonic", float("inf")) > time.monotonic()
    ):
        raise ValueError("Stale/invalid readiness timing.")
    for row in rows:
        g = row["guard"]
        if (
            g.get("synthetic_not_readiness") is not False
            or g.get("host_backend") != "system_vm_stat_oneshot_host_v4"
            or g.get("host_validation_status") != "valid_primary_fields"
            or type(g.get("host_age_upper_seconds")) not in (int, float)
            or not 0 <= g.get("host_age_upper_seconds", 1) <= 0.1
            or type(g.get("available_bytes")) is not int
            or g["available_bytes"] < 4831838208
            or type(g.get("native_heap_reserved_bytes")) is not int
            or not 0 < g.get("native_heap_reserved_bytes", 0) <= 536870912
            or type(g.get("peak_rss_bytes")) is not int
            or not 0 < g.get("peak_rss_bytes", 0) <= 6442450944
            or (
                g.get("pressure_dispatch_flags") is not None
                and type(g.get("pressure_dispatch_flags")) is not int
            )
            or g.get("pressure_dispatch_flags") not in (None, 1)
        ):
            raise ValueError("Synthetic/invalid live readiness guard.")
    if (
        receipt["resources"]["sampler"]["latched_failure"] is not None
        or receipt["resources"]["sampler"]["owned_thread_alive"] is not False
    ):
        raise ValueError("Sampling/cleanup failure cannot admit work.")
    return True


def check(action):
    """Exactly one check; no real plan/slot/worker dispatch even if READY."""
    if action not in ("check_readiness", "run_characterization"):
        raise ValueError("Unsupported explicit action.")
    uid = secrets.token_hex(16)
    directory = invocation_path(uid)
    directory.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    res = {
        "schema_version": 1,
        "invocation_id": uid,
        "action": action,
        "parent_pid": os.getpid(),
        "token": secrets.token_hex(24),
        "started_monotonic": started,
        "started_utc": io.now(),
        "binding": None,
    }
    receipt = None
    try:
        res["binding"] = identity()
        io.exclusive(directory / "reservation.json", res)
        dispatch = io.dispatch(
            [
                sys.executable,
                "-m",
                "latenttrigger.supervision.particle_readiness_worker",
                "--check",
                uid,
                "--token",
                res["token"],
            ],
            directory / "worker.log",
            30,
            started=started,
        )
        path = directory / "receipt.json"
        if path.exists():
            receipt = io.read(path)
            validate_check(receipt, res)
        else:
            raise RuntimeError(
                f"Worker ended before receipt; returncode={dispatch['returncode']}"
            )
    except BaseException as exc:
        if not (directory / "reservation.json").exists():
            io.exclusive(directory / "reservation.json", res)
        receipt = {
            "status": "error",
            "error": str(exc),
            "invocation_id": uid,
            "action": action,
            "binding": res["binding"],
            "started_utc": res["started_utc"],
            "finished_utc": io.now(),
            "check_only_zero_data_steps": True,
            "real_slot_reserved_by_check": False,
            "partial_evidence_retained": True,
            "finished_monotonic": time.monotonic(),
            "elapsed_seconds_including_imports_cleanup": time.monotonic() - started,
        }
        if not (directory / "receipt.json").exists():
            io.exclusive(directory / "receipt.json", receipt)
        else:
            io.exclusive(directory / "controller-error.json", receipt)
    effective = directory / "controller-error.json"
    receipt["receipt_path"] = str(
        effective if effective.exists() else directory / "receipt.json"
    )
    receipt["execution_permission"] = permission()
    return receipt


def reserve_real(receipt):
    """Only caller's freshly dispatched run check; one atomic canonical anchor."""
    if receipt.get("action") != "run_characterization" or not permission()["available"]:
        raise ValueError("No fresh run action or real budget available.")
    directory = invocation_path(receipt["invocation_id"])
    res = io.read(directory / "reservation.json")
    bind = identity()
    if (
        res["parent_pid"] != os.getpid()
        or res["action"] != "run_characterization"
        or time.monotonic() - res["started_monotonic"] > 30
        or bind != res["binding"]
        or not validate_check(io.read(directory / "receipt.json"), res)
    ):
        raise ValueError("A historical/foreign pass is not an execution token.")
    plan = {
        "schema_version": 1,
        "implementation_task": "0017",
        "budget_authorization_task": "0016",
        "binding": bind,
        "readiness_id": receipt["invocation_id"],
        "readiness_receipt_sha256": io.file_hash(directory / "receipt.json"),
        "phase_order": list(PHASES),
        "fixed_output": str(io.ROOT / OUTPUT),
        "historical_torch_version": bind["historical_torch_version"],
        "current_torch_version": bind["current_torch_version"],
        "original_steps": 96,
        "additional_started_maximum": 96,
        "cumulative_started_maximum": 192,
        "canonical_authorized": False,
    }
    io.exclusive(
        io.ROOT / SLOT,
        {
            "task": "0016",
            "implementation_task": "0017",
            "status": "reserved_no_retry",
            "plan_canonical_sha256": io.digest(plan),
            "readiness_id": plan["readiness_id"],
            "original_steps": 96,
            "maximum_additional_started_steps": 96,
            "maximum_cumulative_started_steps": 192,
            "reserved_utc": io.now(),
        },
    )
    # Any interruption from this point consumes the slot, including incomplete plan/output.
    io.exclusive(io.ROOT / PLAN, plan)
    return plan


def verify_plan():
    plan = io.read(io.ROOT / PLAN)
    slot = io.read(io.ROOT / SLOT)
    if (
        plan["binding"] != identity()
        or slot.get("implementation_task") != "0017"
        or slot.get("task") != "0016"
        or slot.get("status") != "reserved_no_retry"
        or slot.get("plan_canonical_sha256") != io.digest(plan)
        or slot.get("maximum_cumulative_started_steps") != 192
        or slot.get("maximum_additional_started_steps") != 96
        or plan["fixed_output"] != str(io.ROOT / OUTPUT)
        or plan["phase_order"] != list(PHASES)
    ):
        raise ValueError("Foreign/source-stale/consumed execution lineage.")
    return plan


def dispatch_real(plan):
    directory = io.ROOT / OUTPUT
    directory.mkdir(exist_ok=False)
    state = {
        "implementation_task": "0017",
        "budget_task": "0016",
        "status": "started",
        "stages": [],
        "readiness_id": plan["readiness_id"],
        "canonical_authorized": False,
    }
    io.atomic(directory / "workflow.json", state)
    phase = PHASES[0]
    try:
        for phase in PHASES:
            verify_plan()
            previous.prior.authorize(phase, state)
            started = time.monotonic()
            token = secrets.token_hex(24)
            io.exclusive(
                directory / f"{phase}-reservation.json",
                {
                    "phase": phase,
                    "token": token,
                    "parent_pid": os.getpid(),
                    "plan_sha256": io.file_hash(io.ROOT / PLAN),
                    "slot_sha256": io.file_hash(io.ROOT / SLOT),
                    "started_monotonic": started,
                    "started_utc": io.now(),
                    "maximum_optimizer_steps": 96 if phase == "dev" else 0,
                },
            )
            parent = io.dispatch(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.supervision.particle_readiness_worker",
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
            path = directory / phase / "stage-result.json"
            result = (
                io.read(path)
                if path.exists()
                else {
                    "phase": phase,
                    "status": "failed",
                    "error": "Partial worker evidence retained",
                }
            )
            result["parent_dispatch"] = parent
            state["stages"].append(result)
            io.atomic(directory / "workflow.json", state)
            supported = (
                ("passed", "characterization_completed_original_throughput_failed")
                if phase == "dev"
                else ("passed",)
            )
            if (
                parent["returncode"]
                or result["status"] not in supported
                or result.get("plan_sha256") != io.file_hash(io.ROOT / PLAN)
            ):
                raise RuntimeError(result.get("error", "Failed/foreign worker receipt"))
        state["status"] = (
            "characterization_completed_original_throughput_failed_canonical_blocked"
            if state["stages"][-1]["status"] != "passed"
            else "bounded_characterization_passed_canonical_pending"
        )
    except BaseException as exc:
        state.update(
            status="real_attempt_failed_nonretryable",
            failed_phase=phase,
            error=str(exc),
        )
    a_path = directory / "dev/access-audit.json"
    a = io.read(a_path) if a_path.exists() else {}
    state.update(
        new_steps_started=a.get("optimizer_steps_started", 0),
        new_steps_completed=a.get("optimizer_steps_completed", 0),
        cumulative_started_steps=96 + a.get("optimizer_steps_started", 0),
        new_inflight_steps=a.get("optimizer_steps_started", 0)
        - a.get("optimizer_steps_completed", 0),
    )
    io.atomic(directory / "workflow.json", state)
    return state


def invoke(action):
    io.assert_lightweight()
    receipt = check(action)
    if action == "check_readiness" or receipt["status"] != "ready":
        return receipt
    try:
        plan = reserve_real(receipt)
        result = dispatch_real(plan)
        return {
            "status": result["status"],
            "readiness": receipt,
            "real_result": result,
            "real_slot_reserved": True,
        }
    except BaseException as exc:
        return {
            "status": "error",
            "error": str(exc),
            "readiness": receipt,
            "real_slot_exists": (io.ROOT / SLOT).exists(),
            "no_retry_after_reservation": True,
        }


def brief(result):
    r = result.get("readiness", result)
    s = r.get("resources") or {}
    process = s.get("last_process_observation") or {}
    flags = process.get("pressure_dispatch_flags")
    pressure = {1: "NORMAL", 2: "WARN", 4: "CRITICAL"}.get(flags, "unknown")
    last = s.get("last_sample") or {}
    available = last.get("available_gib")
    memory = (
        f"{available:.6f} GiB" if available is not None else "unmeasured in readiness"
    )
    diagnostic = r.get("later_diagnostic") or {}
    if diagnostic.get("available_gib") is not None:
        memory += (
            f"; later diagnostic {diagnostic['available_gib']:.6f} GiB (not admission)"
        )
    label = {"ready": "READY", "not_ready": "NOT READY", "error": "ERROR"}.get(
        result["status"], result["status"]
    )
    lines = [f"{label}: available {memory}; pressure {pressure}."]
    if result.get("error") or r.get("error"):
        lines.append(str(result.get("error") or r.get("error")))
    if "real_result" not in result:
        lines.append(
            "Readiness check: zero data/events/steps; no real slot reserved by check."
        )
    else:
        run = result["real_result"]
        lines.append(
            f"Real updates started/completed: {run['new_steps_started']}/{run['new_steps_completed']}; cumulative started {run['cumulative_started_steps']}/192."
        )
    if result.get("real_slot_exists"):
        lines.append("Canonical real slot exists; no retry/reset is permitted.")
    if r.get("execution_permission"):
        lines.append("Execution permission: " + r["execution_permission"]["reason"])
    lines.append("Receipt: " + str(r.get("receipt_path", "unknown")))
    return "\n".join(lines)


def main():
    # Task0018 explicitly replaces the default short-dev admission policy.
    # Old functions/manifests remain historical; no accidental global-RAM default.
    from latenttrigger.supervision.particle_shared_host import main as shared_main

    shared_main()


if __name__ == "__main__":
    main()
