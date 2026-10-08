"""Shared-Mac dev preflight/default CLI; one unchanged Task0016 real slot."""

import argparse
import hashlib
import json
import math
import os
import re
import secrets
import subprocess
import sys
import time

from latenttrigger.supervision import particle_characterization as previous
from latenttrigger.supervision import particle_dev_policy as policy
from latenttrigger.supervision import particle_launcher as io
from latenttrigger.supervision import particle_readiness as legacy

PROMPT, PROMPT_HASH, MANIFEST = policy.PROMPT, policy.PROMPT_HASH, policy.POLICY
ACCEPTANCE = "data/task0018-synthetic-acceptance.json"
HISTORY_ROOT = "data/baselines/particle-readiness-history/shared-host-dev-v1"
PLAN = "data/baselines/task0018-shared-host-dev-execution-plan.json"
SLOT, OUTPUT = policy.SLOT, policy.OUTPUT
PHASES, SECONDS = previous.PHASES, previous.SECONDS
OLD_ACCEPTANCE_HASH = "24d2b77529415822ee43f9f192db2c068f191c0a460c13939fb9c7a39c3d396e"
CHANGED_HISTORICAL_SOURCE = "src/latenttrigger/supervision/particle_readiness.py"
HISTORICAL_COMMIT = "b1940509bb0eb107e4d52fc573dadb8d0b03c6a5"


def definition():
    return policy.definition()


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
    legacy.verify_history()
    accepted_path = io.ROOT / legacy.ACCEPTANCE
    if io.file_hash(accepted_path) != OLD_ACCEPTANCE_HASH:
        raise ValueError("Historical Task0017 acceptance changed.")
    accepted = io.read(accepted_path)
    if accepted["pytest_passed"] != 612:
        raise ValueError("Wrong Task0017 accepted suite.")
    for rel, h in accepted["source_sha256"].items():
        if rel == CHANGED_HISTORICAL_SOURCE:
            # Only the default CLI router changes. Verify its original accepted
            # bytes from the actual commit; no blanket historical-source waiver.
            raw = subprocess.check_output(
                ["git", "show", f"{HISTORICAL_COMMIT}:{rel}"], cwd=io.ROOT, timeout=2
            )
            actual = hashlib.sha256(raw).hexdigest()
        else:
            actual = io.file_hash(io.ROOT / rel)
        if actual != h:
            raise ValueError("Historical Task0017 source entry changed: " + rel)
    for suffix, key in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        if io.file_hash(accepted_path.with_suffix(suffix)) != accepted[key]:
            raise ValueError("Historical Task0017 evidence changed.")
    root = io.ROOT / legacy.HISTORY_ROOT
    for directory in root.iterdir():
        if not directory.is_dir():
            raise ValueError("Malformed old readiness history.")
        receipt = io.read(directory / "receipt.json")
        if (
            receipt.get("population_requests") != 0
            or receipt.get("events") != 0
            or receipt.get("new_steps_started") != 0
            or receipt.get("new_inflight_steps") != 0
            or receipt.get("real_slot_reserved_by_check") is not False
        ):
            raise ValueError(
                "Unexpected later historical consumption; reconcile first."
            )


def identity():
    verify_history()
    policy.validate(io.read(io.ROOT / MANIFEST), io.read(io.ROOT / io.CONFIG))
    if (
        io.digest(io.read(io.ROOT / MANIFEST)) != io.digest(definition())
        or io.file_hash(io.ROOT / PROMPT) != PROMPT_HASH
    ):
        raise ValueError("Unsupported readiness workflow/prompt.")
    a = current_acceptance()
    return {
        "workflow_sha256": io.digest(definition()),
        "policy": policy.NAME,
        "historical_Task0017_acceptance_sha256": OLD_ACCEPTANCE_HASH,
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
    if (
        (io.ROOT / OUTPUT).exists()
        or (io.ROOT / PLAN).exists()
        or (io.ROOT / legacy.PLAN).exists()
    ):
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
    return (
        "not_ready"
        if message
        in (
            "Verified CRITICAL pressure veto.",
            "Shared dev process RSS/native ceiling exceeded.",
        )
        else "error"
    )


def validate_check(receipt, res):
    if receipt.get("status") not in ("ready", "not_ready", "error"):
        raise ValueError("Unsupported preflight receipt status.")
    if (
        receipt.get("invocation_id") != res["invocation_id"]
        or receipt.get("reservation_sha256")
        != io.file_hash(invocation_path(res["invocation_id"]) / "reservation.json")
        or receipt.get("binding") != res["binding"]
        or receipt.get("action") != res["action"]
        or receipt.get("check_only_zero_data_steps") is not True
        or receipt.get("real_slot_reserved_by_check") is not False
    ):
        raise ValueError("Foreign/malformed preflight receipt.")
    elapsed = receipt.get("elapsed_seconds_including_imports_cleanup")
    finished = receipt.get("finished_monotonic")
    if (
        type(elapsed) not in (int, float)
        or not math.isfinite(elapsed)
        or not 0 <= elapsed <= 30
        or type(finished) not in (int, float)
        or not math.isfinite(finished)
        or not res["started_monotonic"] <= finished <= res["started_monotonic"] + 30
        or finished > time.monotonic()
    ):
        raise ValueError("Stale/invalid preflight deadline.")
    if receipt["status"] != "ready":
        return False
    resources = receipt.get("resources") or {}
    g = resources.get("last_process_observation") or {}
    if (
        resources.get("policy") != policy.NAME
        or resources.get("synthetic_not_readiness") is not False
        or resources.get("latched_failure") is not None
        or resources.get("owned_thread_alive") is not False
        or g.get("synthetic_not_readiness") is not False
        or g.get("backend") != "cached_DarwinBindings_fresh_own_process"
        or type(g.get("peak_rss_bytes")) is not int
        or not 0 < g["peak_rss_bytes"] <= 536870912
        or type(g.get("native_heap_reserved_bytes")) is not int
        or not 0 < g["native_heap_reserved_bytes"] <= 268435456
        or g.get("pressure_dispatch_flags") not in (None, 1, 2)
        or (
            g.get("pressure_dispatch_flags") is not None
            and type(g["pressure_dispatch_flags"]) is not int
        )
        or not res["started_monotonic"]
        <= g.get("process_query_start", -1)
        <= g.get("process_query_end", -1)
        <= finished
    ):
        raise ValueError("Invalid live process-budget preflight.")
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
                "latenttrigger.supervision.particle_shared_host_worker",
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
        "implementation_task": "0018",
        "budget_authorization_task": "0016",
        "policy_authorization_task": "0018",
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
            "implementation_task": "0018",
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
        or slot.get("implementation_task") != "0018"
        or slot.get("task") != "0016"
        or slot.get("status") != "reserved_no_retry"
        or slot.get("plan_canonical_sha256") != io.digest(plan)
        or slot.get("maximum_cumulative_started_steps") != 192
        or slot.get("maximum_additional_started_steps") != 96
        or plan["fixed_output"] != str(io.ROOT / OUTPUT)
        or plan["phase_order"] != list(PHASES)
        or plan.get("original_steps") != 96
        or plan.get("additional_started_maximum") != 96
        or plan.get("cumulative_started_maximum") != 192
        or plan.get("policy_authorization_task") != "0018"
        or plan.get("canonical_authorized") is not False
    ):
        raise ValueError("Foreign/source-stale/consumed execution lineage.")
    return plan


def dispatch_real(plan):
    directory = io.ROOT / OUTPUT
    directory.mkdir(exist_ok=False)
    state = {
        "implementation_task": "0018",
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
                    "latenttrigger.supervision.particle_shared_host_worker",
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
    contexts = s.get("context_observations") or []
    last = contexts[-1] if contexts else {}
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
    lines = [
        f"Policy {policy.NAME}: bounded dev only; {label}.",
        f"Global context {memory} (no floor); pressure {pressure}.",
    ]
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
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-readiness", action="store_true")
    group.add_argument("--run-characterization", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    result = invoke(
        "check_readiness" if args.check_readiness else "run_characterization"
    )
    print(json.dumps(result, indent=2) if args.json else brief(result))
    status = result["status"]
    raise SystemExit(
        0
        if status in ("ready", "bounded_characterization_passed_canonical_pending")
        else 2
        if status
        in (
            "not_ready",
            "characterization_completed_original_throughput_failed_canonical_blocked",
        )
        else 1
    )


if __name__ == "__main__":
    main()
