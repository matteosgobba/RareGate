"""Fixed Task0015 conditional additional budget; shared automatic/manual slot."""

import argparse
import json
import os
import secrets
import sys
import time

from raregate.supervision import particle_launcher as io
from raregate.supervision import particle_sampling_benchmark as bench
from raregate.supervision.particle_reconciliation import reconcile

PROMPT = "docs/prompts/0015-particle-bounded-sampling.md"
PROMPT_HASH = "5788c605815db5944dcf1d54f376141d92c28b3520ab410d0a2fcbaf7caaf045"
MONITOR = "configs/resources/particle_resource_monitor_v4.json"
MONITOR_HASH = "d11640071b854b08dfc9cd59724dd2732abe8ebff1195000e8321e66a1229c63"
PLAN = "data/baselines/task0015-bounded-sampling-plan.json"
SLOT = "data/baselines/task0015-bounded-sampling-attempt.json"
OUTPUT = "data/baselines/task0015-bounded-sampling-study"
READINESS_AUTO = "data/task0015-readiness-auto.json"
READINESS_MANUAL = "data/task0015-readiness-manual.json"
PHASES = ("dev_reader", "dev_readiness", "dev")
SECONDS = {"dev_reader": 60, "dev_readiness": 30, "dev": 300}


def verify_predecessor():
    historical = reconcile()
    a = io.read(io.ROOT / "data/task0014-synthetic-acceptance.json")
    if a["pytest_passed"] != 471 or a["pytest_exit_code"] != 0:
        raise ValueError("Task0014 acceptance identity invalid.")
    for rel, h in a["source_sha256"].items():
        if io.file_hash(io.ROOT / rel) != h:
            raise ValueError("Task0014 historical source changed.")
    summary = io.read(
        io.ROOT
        / "results/tables/final/task0014-particle-monitor-performance-summary.json"
    )
    if summary["validation"]["acceptance_file_sha256"] != io.file_hash(
        io.ROOT / "data/task0014-synthetic-acceptance.json"
    ):
        raise ValueError("Historical acceptance/curated identity mismatch.")
    if summary["historical_task0013"]["receipt_sha256"] != historical["receipt_sha256"]:
        raise ValueError("Historical consumed lineage mismatch.")
    return historical


def verify_material():
    acceptance = bench.acceptance()
    path = io.ROOT / bench.OUTPUT / "matrix.json"
    matrix = io.read(path)
    decision = bench.evaluate(matrix["rows"])
    if (
        matrix["status"] != "completed"
        or matrix["decision"] != decision
        or not decision["material_improvement_pass"]
        or matrix["acceptance_sha256"] != io.file_hash(io.ROOT / bench.ACCEPTANCE)
        or matrix["source_sha256"] != acceptance["source_sha256"]
        or matrix["elapsed_seconds"] > 120
        or any(
            r["elapsed_seconds_including_imports"] > 30
            or r["parent_dispatch"]["returncode"]
            for r in matrix["rows"]
        )
    ):
        raise ValueError(
            "Fixed correctness/parity/material gate did not authorize real spending."
        )
    return decision


def plan_definition():
    verify_material()
    h = verify_predecessor()
    if io.file_hash(io.ROOT / PROMPT) != PROMPT_HASH:
        raise ValueError("Task0015 prompt changed.")
    profile = io.read(io.ROOT / io.PROFILE)
    config = io.read(io.ROOT / io.CONFIG)
    manifest = io.read(io.ROOT / MONITOR)
    if (
        io.digest(profile) != io.PROFILE_HASH
        or io.digest(config) != io.CONFIG_HASH
        or io.digest(io.read(io.ROOT / io.DESIGN)) != io.DESIGN_HASH
        or io.digest(manifest) != MONITOR_HASH
    ):
        raise ValueError("Unchanged scientific/numerical identity required.")
    return {
        "schema_version": 1,
        "task": "0015",
        "scope": "single_additional_engineering_revalidation_only",
        "prompt_sha256": PROMPT_HASH,
        "profile_sha256": io.PROFILE_HASH,
        "model_config_sha256": io.CONFIG_HASH,
        "design_sha256": io.DESIGN_HASH,
        "observation_manifest_sha256": io.digest(manifest),
        "acceptance_sha256": io.file_hash(io.ROOT / bench.ACCEPTANCE),
        "source_sha256": io.source_hashes(),
        "synthetic_matrix_sha256": io.file_hash(io.ROOT / bench.OUTPUT / "matrix.json"),
        "predecessor_receipt_sha256": h["receipt_sha256"],
        "Task0014_acceptance_sha256": io.file_hash(
            io.ROOT / "data/task0014-synthetic-acceptance.json"
        ),
        "historical_steps_started_completed": 96,
        "additional_steps_started_maximum": 96,
        "cumulative_steps_started_maximum": 192,
        "same_unique_dev_ID_sample": 1024,
        "phase_order": list(PHASES),
        "phase_limits_seconds": SECONDS,
        "fixed_output": str(io.ROOT / OUTPUT),
        "canonical_selection_freeze_calibration_authorized": False,
    }


def prepare():
    p = plan_definition()
    path = io.ROOT / PLAN
    if path.exists():
        if io.read(path) != p:
            raise ValueError("Fixed prepared manifest changed; no overwrite.")
    else:
        io.exclusive(path, p)
    return p


def verify_plan():
    expected = plan_definition()
    if io.read(io.ROOT / PLAN) != expected:
        raise ValueError("Current execution/source/predecessor mismatch.")
    return expected


def authorize(phase, state):
    if phase not in PHASES:
        raise ValueError("Fit/selection/calibration/test/custody-full forbidden.")
    pos = PHASES.index(phase)
    if [r["phase"] for r in state["stages"]] != list(PHASES[:pos]) or any(
        r["status"] != "passed" for r in state["stages"]
    ):
        raise ValueError("Prior missing/failed/foreign phase blocks downstream.")


def dispatch_readiness(mode):
    if mode not in ("automatic", "manual"):
        raise ValueError("Only fixed automatic/manual readiness routes supported.")
    verify_plan()
    target = io.ROOT / (READINESS_AUTO if mode == "automatic" else READINESS_MANUAL)
    reservation = target.with_suffix(".reservation.json")
    token = secrets.token_hex(24)
    started = time.monotonic()
    io.exclusive(
        reservation,
        {
            "token": token,
            "mode": mode,
            "plan_sha256": io.file_hash(io.ROOT / PLAN),
            "parent_pid": os.getpid(),
            "started_monotonic": started,
            "status": "read_only_once_no_retry",
        },
    )
    try:
        result = io.dispatch(
            [
                sys.executable,
                "-m",
                "raregate.supervision.particle_bounded_worker",
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
        result = {"returncode": 1, "dispatch_error": str(exc)}
    if not target.exists():
        io.exclusive(
            target,
            {
                "status": "failed",
                "error": "Readiness terminated before receipt; no data reservation.",
                "new_real_steps": 0,
                "population_requests": 0,
                "parent_dispatch": result,
            },
        )
    receipt = io.read(target)
    if result["returncode"] or receipt.get("status") != "passed":
        return False, receipt
    if receipt.get("plan_sha256") != io.file_hash(io.ROOT / PLAN) or receipt.get(
        "acceptance_sha256"
    ) != io.file_hash(io.ROOT / bench.ACCEPTANCE):
        raise ValueError("Foreign readiness receipt.")
    return True, receipt


def study(mode):
    io.assert_lightweight()
    if mode not in ("automatic", "manual"):
        raise ValueError("Unsupported route.")
    prepare()
    if (io.ROOT / SLOT).exists() or (io.ROOT / OUTPUT).exists():
        raise FileExistsError("Shared Task0015 attempt consumed; no retry.")
    ready, receipt = dispatch_readiness(mode)
    if not ready:
        return {
            "status": "readiness_deferred_attempt_unreserved",
            "mode": mode,
            "readiness": receipt,
            "new_real_steps": 0,
            "original_steps": 96,
            "cumulative_steps": 96,
            "slot_reserved": False,
        }
    started = time.monotonic()
    token = secrets.token_hex(24)
    io.exclusive(
        io.ROOT / SLOT,
        {
            "task": "0015",
            "status": "reserved_no_retry",
            "token": token,
            "plan_sha256": io.file_hash(io.ROOT / PLAN),
            "readiness_sha256": io.file_hash(
                io.ROOT / (READINESS_AUTO if mode == "automatic" else READINESS_MANUAL)
            ),
            "original_steps_started": 96,
            "maximum_additional_started_steps": 96,
            "maximum_cumulative_started_steps": 192,
        },
    )
    output = io.ROOT / OUTPUT
    output.mkdir(exist_ok=False)
    state = {
        "task": "0015",
        "status": "started",
        "stages": [],
        "original_steps_started": 96,
        "slot_reserved": True,
        "canonical_authorized": False,
    }
    ledger = output / "workflow.json"
    io.atomic(ledger, state)
    phase = "dev_reader"
    try:
        for phase in PHASES:
            verify_plan()
            authorize(phase, state)
            started = time.monotonic()
            stage_token = secrets.token_hex(24)
            io.exclusive(
                output / f"{phase}-reservation.json",
                {
                    "phase": phase,
                    "token": stage_token,
                    "parent_pid": os.getpid(),
                    "plan_sha256": io.file_hash(io.ROOT / PLAN),
                    "slot_sha256": io.file_hash(io.ROOT / SLOT),
                    "started_monotonic": started,
                    "status": "reserved_no_automatic_retry",
                    "maximum_optimizer_steps": 96 if phase == "dev" else 0,
                },
            )
            parent = io.dispatch(
                [
                    sys.executable,
                    "-m",
                    "raregate.supervision.particle_bounded_worker",
                    "--phase",
                    phase,
                    "--token",
                    stage_token,
                ],
                output / f"{phase}.log",
                SECONDS[phase],
                started=started,
                journal=output / phase / "guard-samples.jsonl",
            )
            path = output / phase / "stage-result.json"
            record = (
                io.read(path)
                if path.exists()
                else {
                    "phase": phase,
                    "status": "failed",
                    "error": "Partial worker evidence retained; no retry.",
                }
            )
            record["parent_dispatch"] = parent
            state["stages"].append(record)
            io.atomic(ledger, state)
            if (
                parent["returncode"]
                or record["status"] != "passed"
                or record.get("plan_sha256") != io.file_hash(io.ROOT / PLAN)
                or record.get("acceptance_sha256")
                != io.file_hash(io.ROOT / bench.ACCEPTANCE)
            ):
                raise RuntimeError(
                    record.get("error", "Foreign/failed worker receipt.")
                )
        state["status"] = "bounded_v4_real_dev_passed_canonical_pending"
    except BaseException as exc:
        state.update(
            status="bounded_v4_attempt_failed", failed_phase=phase, error=str(exc)
        )
        if not state["stages"] or state["stages"][-1]["phase"] != phase:
            state["stages"].append(
                {
                    "phase": phase,
                    "status": "failed_or_interrupted",
                    "partial_audit_must_be_reconciled": True,
                }
            )
    io.atomic(ledger, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--automatic", action="store_true")
    parser.add_argument("--run-once", action="store_true")
    args = parser.parse_args()
    if args.automatic == args.run_once:
        parser.error("Choose exactly one supported route.")
    result = study("automatic" if args.automatic else "manual")
    print(json.dumps(result, indent=2))
    if result["status"] not in (
        "bounded_v4_real_dev_passed_canonical_pending",
        "readiness_deferred_attempt_unreserved",
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
