"""Fixed Task0013 stdlib supervisor: accounting once, one shared bounded study."""

import argparse
import hashlib
import json
import os
import secrets
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from raregate.supervision import particle_host as host

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "configs/models/compact_particle_set_autoencoder_v1.json"
DESIGN = "configs/models/particle_set_baseline_design_v1.json"
PROFILE = "configs/resources/particle_memory_policy_v2.json"
PROMPT = "docs/prompts/0013-particle-host-readiness.md"
PROMPT_HASH = "652ce7907f6aa1833ed543a8d89c7f4e31fb1d009c80e1c29997ee1cfb571750"
PROFILE_HASH = "a3e237d8a191d9b906744a497ef7e687c739bc8418dd2e53e78db3e54b24d287"
CONFIG_HASH = "48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b"
DESIGN_HASH = "3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67"
ACCEPTANCE = "data/task0013-synthetic-acceptance.json"
PLAN = "data/baselines/task0013-particle-host-plan.json"
SLOT = "data/baselines/task0013-particle-host-invocation.json"
OUTPUT = "data/baselines/task0013-particle-host-study"
EXPERIMENT = "data/baselines/task0013-particle-host-accounting"
PHASES = ("pilot_preflight", "dev_reader", "full_custody", "dev_preflight", "dev")
CONFIGURATIONS = ("stdlib_baseline", "legacy_double_stack", "lightweight_prepared")
LIMITS_SECONDS = dict(zip(PHASES, (30, 60, 300, 30, 300), strict=True))
LOG_LIMIT = 2**20
JOURNAL_LIMIT = 16 * 2**20
# Pinned historical evidence; generated once from inspected predecessor records.
PREDECESSOR = {
    "configs/resources/particle_memory_policy_v2.json": "3d495f62256bc3e92b988178fcf9a63185ae655382cead477ccf39a3e524c370",
    "data/baselines/task0010-particle-attempt-budget.json": "2a98539f5dc9e9f3653e57681613e19a920954c8fd250f954a5aec9cd974da70",
    "data/baselines/compact-particle-set-autoencoder-v1/workflow.json": "7897e03da20a853f842e201a492e95e08f6d5ac49c7025b3d0ae40cd49900d90",
    "data/baselines/compact-particle-set-autoencoder-v1/dev/access-audit.json": "a9400a16081e6a6c759a93bba45541b0c00c48ea9754333beb849a8da3d58c48",
    "data/baselines/compact-particle-set-autoencoder-v1/dev/stage-result.json": "1e36d40fe8df79c83ee6c821a9c59039f1621b01d485384a43a0a45deb7d69a8",
    "data/task0010-synthetic-acceptance.json": "535554d2673622bba6e9992de792a50bed7fb009dc5b4df5257d544bae3e6575",
    "data/task0010-final-synthetic-acceptance.json": "3037988a7975e6af040d3648b943930bf048b4b9648c193ab754b7f2f2b10020",
    "results/tables/final/task0010-particle-set-gate-summary.json": "f4d73f4a1018b711cea0f2fd187ffd591db32a76cd498a7e53d6007d65feaa22",
    "src/raregate/models/particle_set.py": "da5a46714bd6a43a1df5be76521dd2ef6ca68c86a28ee340eb825abe47b32827",
    "src/raregate/data/processed.py": "e2c908271728f0ac83ec865ef0bbf590b720868842a36cc17a8aa28598dd4766",
    "configs/models/particle_set_baseline_design_v1.json": "e358fb51c72e3d68228de2cf05d9dbd0233e4a3d7bca3edc9d7c27ed174af964",
    "configs/models/compact_particle_set_autoencoder_v1.json": "0af735aa07f0966f1c97c8c3bea5ce6f9b1e93e80ec282ccbf0fe3f444183302",
    "configs/data/lhco_rnd_v5.json": "2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68",
    "results/tables/final/task0011-particle-set-recovery-summary.json": "40e0f094950e34933fb8e672598cecf69257b2ed3dee827e7ba18297a76a170f",
    "data/baselines/task0011-preflight-after-reboot-2026-10-07.json": "e99c614468d6d1c5e737991a34820a02bd9e40ec26e59dc2894889b01d1176eb",
    "data/baselines/task0011-particle-preflight.json": "5d31e61967d6027f576143b807c5c689d56d2932c2957545127328794dfa17ae",
    "data/task0011-reviewed-synthetic-acceptance.json": "1cef87bb612eb7066e1f3e91cb01ba16ff84d3152c2198945098a012c8d79159",
    "data/task0012-final-synthetic-acceptance.json": "fe33d6822071b3eab8280fa73e107d05365ef4577349f9b6420f585598430844",
    "data/task0012-synthetic-acceptance.json": "ce7f3d7944a1e512a0f548a7965cd4afc79a2af401cba029096a6138238cea1a",
    "data/baselines/task0012-particle-memory-study/workflow.json": "9cf927cd2e8f76d3dff628e9ca303f67d2f11b23c630afc8ea54725096f15955",
    "data/baselines/task0012-particle-memory-study/pilot_preflight-reservation.json": "6fc2b7d43387c6b5465ff466a3517647536802aca5c57b468be546c5292cc2f5",
    "data/baselines/task0012-particle-memory-study/pilot_preflight/stage-result.json": "58d5e64120c50c5527f1674786a7a7400e0b7679c36eb6e64453a1f4dde68c86",
    "data/baselines/task0012-particle-memory-study/pilot_preflight/access-audit.json": "0a0806a332dca43eedf9ed9561eaba68ed8087c5dd95bc048eb9bd11dcfe617a",
    "data/baselines/task0012-particle-memory-plan.json": "8d9dc461db3e86259b161f69b7309c32573049f904b21a83edac51962715058c",
    "results/tables/final/task0012-particle-memory-policy-summary.json": "d9dcb2717c6b7bf1fe208feb983332c1ae556df4d9dd77f9e274840bbaf35cb8",
}


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def atomic(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def exclusive(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as file:
        file.write(json.dumps(value, indent=2, allow_nan=False) + "\n")


def now():
    return datetime.now(UTC).isoformat()


def assert_lightweight():
    forbidden = host.heavy_modules()
    forbidden += [
        n
        for n in sys.modules
        if n.startswith(("raregate.data.", "raregate.training.", "raregate.models."))
    ]
    if forbidden:
        raise RuntimeError(f"Controller imported heavy stack: {forbidden}")


def source_hashes(root=ROOT):
    paths = [
        *sorted((root / "src/raregate").rglob("*.py")),
        *sorted((root / "tests").glob("*.py")),
    ]
    return {str(p.relative_to(root)): file_hash(p) for p in paths}


def verify_acceptance(root=ROOT):
    evidence = read(root / ACCEPTANCE)
    if (
        evidence.get("pytest_exit_code") != 0
        or type(evidence.get("pytest_passed")) is not int
        or evidence["pytest_passed"] <= 0
        or evidence.get("pytest_cases") != evidence["pytest_passed"]
        or evidence.get("config_sha256") != CONFIG_HASH
        or evidence.get("source_sha256") != source_hashes(root)
        or evidence.get("workspace_measurement", {}).get("parameter_count") != 478
        or evidence["workspace_measurement"].get("synthetic_optimizer_steps") != 2
        or type(evidence["workspace_measurement"].get("peak_tensor_bytes")) is not int
        or not 0 < evidence["workspace_measurement"]["peak_tensor_bytes"] <= 512 * 2**20
    ):
        raise ValueError("Current complete source-bound synthetic acceptance required.")
    for suffix, field in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        if file_hash((root / ACCEPTANCE).with_suffix(suffix)) != evidence[field]:
            raise ValueError("Acceptance test evidence identity changed.")
    return evidence


def verify_prior(root=ROOT):
    for rel, expected in PREDECESSOR.items():
        if file_hash(root / rel) != expected:
            raise ValueError(f"Predecessor identity changed: {rel}")
    old = root / "data/baselines/task0012-particle-memory-study"
    state = read(old / "workflow.json")
    audit = read(old / "pilot_preflight/access-audit.json")
    if (
        state["status"] != "provisional_launch_still_blocked"
        or len(state["stages"]) != 1
        or state["stages"][0]["phase"] != "pilot_preflight"
        or state["stages"][0]["status"] != "failed"
        or audit["population_access"]
        or audit["custody_access"]
        or audit["optimizer_steps_started"] != 0
        or audit["optimizer_steps_completed"] != 0
        or audit["unique_dev_sample_events"] != 0
        or audit["test_background_model_access"] is not False
        or audit["test_signal_model_access"] is not False
    ):
        raise ValueError(
            "Prior consumption/failure must be reconciled; budget refused."
        )
    if any(
        (old / f"{p}-reservation.json").exists() or (old / p).exists()
        for p in PHASES[1:]
    ):
        raise ValueError("Unexpected later Task0012 consumption.")
    for rel in (
        "task0011-particle-recovery-plan.json",
        "task0011-particle-attempt-budget.json",
        "compact-particle-set-autoencoder-task0011",
    ):
        if (root / "data/baselines" / rel).exists():
            raise ValueError("Unexpected Task0011 recovery; reconcile first.")


def verify_inputs(root=ROOT):
    for rel, expected in (
        (CONFIG, CONFIG_HASH),
        (DESIGN, DESIGN_HASH),
        (PROFILE, PROFILE_HASH),
    ):
        if digest(read(root / rel)) != expected:
            raise ValueError("Unchanged scientific/resource identity required.")
    if file_hash(root / PROMPT) != PROMPT_HASH:
        raise ValueError("Task0013 authorization prompt changed.")
    verify_prior(root)
    return verify_acceptance(root)


def plan_definition(root=ROOT):
    verify_inputs(root)
    return {
        "schema_version": 1,
        "execution_authorization_version": 1,
        "task": "0013",
        "scope": "successor_bounded_readers_conditional_original_dev",
        "fixed_output": str(root / OUTPUT),
        "prompt_sha256": PROMPT_HASH,
        "predecessor_file_sha256": PREDECESSOR,
        "profile_sha256": PROFILE_HASH,
        "config_sha256": CONFIG_HASH,
        "design_sha256": DESIGN_HASH,
        "acceptance_sha256": file_hash(root / ACCEPTANCE),
        "source_sha256": source_hashes(root),
        "gate_order": list(PHASES),
        "phase_limits_seconds": LIMITS_SECONDS,
        "prior_real_steps": 0,
        "maximum_cumulative_steps_started": 96,
        "maximum_unique_dev_events": 1024,
        "maximum_training_passes": 3,
        "maximum_same_sample_score_passes": 1,
        "supersedes_unused_task0011_and_consumed_task0012_pilot": True,
        "canonical_selection_freeze_calibration_authorized": False,
        "policy_v1_compliance": False,
        "profile_scope_is_historical": "Task0012",
    }


def prepare(root=ROOT):
    plan = plan_definition(root)
    path = root / PLAN
    if path.exists():
        if read(path) != plan:
            raise ValueError("Prepared manifest changed/stale; no overwrite.")
    else:
        exclusive(path, plan)
    return plan


def authorize(phase, state):
    if phase not in PHASES:
        raise ValueError("Fit/selection/freeze/calibration/test stages forbidden.")
    pos = PHASES.index(phase)
    if [r.get("phase") for r in state["stages"]] != list(PHASES[:pos]) or any(
        r.get("status") != "passed" for r in state["stages"]
    ):
        raise ValueError("Missing/failed/out-of-order gate; no dependent execution.")
    if pos >= 3 and not state.get("activation", {}).get("activated_for_bounded_dev"):
        raise ValueError("Completed reader activation required.")


def activation(results, acceptance, profile):
    # Exact stdlib mirror of frozen v2 activation_decision; parity tested.
    if set(results) != {"dev_reader", "full_custody"} or any(
        r.get("status") != "passed" for r in results.values()
    ):
        raise ValueError("Both completed readers required.")
    increments = []
    for name, r in results.items():
        m = r["resources"]
        if (
            r.get("engineering_policy_sha256") != digest(profile)
            or r.get("model_config_sha256") != CONFIG_HASH
            or r.get("custody_completed") is not True
            or r.get("view_events") != (64 if name == "dev_reader" else 0)
            or r.get("optimizer_steps_started") != 0
            or r.get("optimizer_steps_completed") != 0
            or m["minimum_available_bytes"] < 4 * 2**30
            or m["native_heap_reserved_bytes"] > 512 * 2**20
            or m["peak_rss_bytes"] > 6 * 2**30
        ):
            raise ValueError("Invalid zero-step reader identity/resources.")
        startup = m["phases"]["startup"]["first"]["native_heap_reserved_bytes"]
        increments.append(max(0, m["native_heap_reserved_bytes"] - startup))
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


def stop_owned(child):
    # Each dispatched process owns a new session. Kill remaining owned descendants
    # even if its immediate parent already exited; never inspect unrelated PIDs.
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    child.wait(timeout=2)


def dispatch(command, log_path, seconds, *, started=None, journal=None):
    started = time.monotonic() if started is None else started
    child = None
    try:
        with log_path.open("x") as log:
            child = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            while child.poll() is None:
                if time.monotonic() - started > seconds:
                    raise TimeoutError(
                        "Import-inclusive parent phase deadline exceeded."
                    )
                if log_path.stat().st_size > LOG_LIMIT or (
                    journal
                    and journal.exists()
                    and journal.stat().st_size > JOURNAL_LIMIT
                ):
                    raise RuntimeError("Bounded phase log/journal ceiling exceeded.")
                time.sleep(0.05)
            if time.monotonic() - started > seconds:
                raise TimeoutError("Import-inclusive parent phase deadline exceeded.")
            if log_path.stat().st_size > LOG_LIMIT:
                raise RuntimeError("Bounded phase log ceiling exceeded.")
            return {
                "returncode": child.returncode,
                "elapsed_seconds_including_imports": time.monotonic() - started,
            }
    finally:
        if child is not None:
            stop_owned(child)


def verify_plan(root=ROOT):
    plan = plan_definition(root)
    if read(root / PLAN) != plan:
        raise ValueError("Fixed execution manifest mismatch/stale acceptance.")
    return plan


def run_study(root=ROOT):
    assert_lightweight()
    verify_plan(root)
    if (root / SLOT).exists() or (root / OUTPUT).exists():
        raise FileExistsError(
            "Single Task0013 study invoked; automatic/manual slot consumed."
        )
    token = secrets.token_hex(24)
    exclusive(
        root / SLOT,
        {
            "task": "0013",
            "token": token,
            "plan_sha256": file_hash(root / PLAN),
            "reserved_utc": now(),
            "status": "reserved_no_retry",
            "canonical_authorized": False,
        },
    )
    output = root / OUTPUT
    output.mkdir(exist_ok=False)
    state = {
        "task": "0013",
        "status": "started",
        "stages": [],
        "policy_v1_compliance": False,
        "canonical_training_authorized": False,
    }
    ledger = output / "workflow.json"
    atomic(ledger, state)
    phase = PHASES[0]
    try:
        for phase in PHASES:
            authorize(phase, state)
            verify_plan(root)
            started = time.monotonic()
            reservation = {
                "phase": phase,
                "token": secrets.token_hex(24),
                "plan_sha256": file_hash(root / PLAN),
                "slot_sha256": file_hash(root / SLOT),
                "started_monotonic": started,
                "parent_pid": os.getpid(),
                "status": "reserved_no_automatic_retry",
                "maximum_optimizer_steps": 96 if phase == "dev" else 0,
            }
            exclusive(output / f"{phase}-reservation.json", reservation)
            receipt = dispatch(
                [
                    sys.executable,
                    "-m",
                    "raregate.supervision.particle_worker",
                    "--worker",
                    phase,
                    "--token",
                    reservation["token"],
                ],
                output / f"{phase}.log",
                LIMITS_SECONDS[phase],
                started=started,
                journal=output / phase / "resource-samples.jsonl",
            )
            path = output / phase / "stage-result.json"
            result = (
                read(path)
                if path.exists()
                else {
                    "phase": phase,
                    "status": "failed",
                    "error": "No final worker receipt; partial audit retained",
                }
            )
            result["parent_receipt"] = receipt
            state["stages"].append(result)
            atomic(ledger, state)
            if (
                receipt["returncode"] != 0
                or result.get("status") != "passed"
                or result.get("engineering_policy_sha256") != PROFILE_HASH
                or result.get("model_config_sha256") != CONFIG_HASH
                or result.get("execution_plan_sha256") != file_hash(root / PLAN)
                or result.get("acceptance_sha256") != file_hash(root / ACCEPTANCE)
            ):
                raise RuntimeError(result.get("error", "Phase failed/foreign receipt."))
            if phase == "full_custody":
                state["activation"] = activation(
                    {
                        r["phase"]: r
                        for r in state["stages"]
                        if r["phase"] in ("dev_reader", "full_custody")
                    },
                    verify_acceptance(root),
                    read(root / PROFILE),
                )
                state["activation"]["reader_result_file_sha256"] = {
                    p: file_hash(output / p / "stage-result.json")
                    for p in ("dev_reader", "full_custody")
                }
                exclusive(output / "activation.json", state["activation"])
                atomic(ledger, state)
                if not state["activation"]["activated_for_bounded_dev"]:
                    state["status"] = "reviewed_provisional_not_activated"
                    break
        else:
            state["status"] = "bounded_feasibility_established_canonical_pending"
    except BaseException as exc:
        state.update(status="bounded_study_failed", failed_phase=phase, error=str(exc))
        if not state["stages"] or state["stages"][-1]["phase"] != phase:
            state["stages"].append(
                {
                    "phase": phase,
                    "status": "failed_or_interrupted",
                    "error": str(exc),
                    "partial_audit_must_be_reconciled": True,
                }
            )
    atomic(ledger, state)
    assert_lightweight()
    return state


def experiment():
    started = time.monotonic()
    assert_lightweight()
    verify_plan()
    directory = ROOT / EXPERIMENT
    directory.mkdir(exist_ok=False)
    prereg = {
        "task": "0013",
        "scope": "one_data_free_accounting_experiment",
        "configuration_order": list(CONFIGURATIONS),
        "overall_seconds": 180,
        "each_configuration_seconds_including_imports": 30,
        "readings": 3,
        "spacing_seconds": 2.5,
        "minimum_span_seconds": 5,
        "no_dataset_store_model_optimizer_or_score": True,
        "plan_sha256": file_hash(ROOT / PLAN),
        "acceptance_sha256": file_hash(ROOT / ACCEPTANCE),
    }
    exclusive(directory / "preregistration.json", prereg)
    state = {
        "status": "started",
        "configurations": [],
        "context": host.host_context_once(),
        "study_invoked": False,
    }
    atomic(directory / "experiment.json", state)
    try:
        for name in CONFIGURATIONS:
            tick = time.monotonic()
            remaining = min(30, 180 - (tick - started))
            if remaining <= 0:
                raise TimeoutError("Overall180-second diagnostic deadline.")
            sub = directory / name
            sub.mkdir()
            exclusive(
                sub / "reservation.json",
                {
                    "name": name,
                    "started_monotonic": tick,
                    "deadline_monotonic": tick + remaining,
                    "plan_sha256": file_hash(ROOT / PLAN),
                },
            )
            receipt = dispatch(
                [
                    sys.executable,
                    "-m",
                    "raregate.supervision.particle_worker",
                    "--diagnostic-parent",
                    name,
                ],
                sub / "parent.log",
                remaining,
                started=tick,
            )
            result = (
                read(sub / "result.json")
                if (sub / "result.json").exists()
                else {
                    "configuration": name,
                    "status": "failed",
                    "error": "Missing diagnostic receipt",
                }
            )
            result["parent_dispatch"] = receipt
            state["configurations"].append(result)
            atomic(directory / "experiment.json", state)
            if receipt["returncode"] or result["status"] != "completed":
                raise RuntimeError("Diagnostic failed; no study admission.")
        last = state["configurations"][-1]
        state["fully_prepared_worker_admission"] = last["worker_observations_all_pass"]
        state["status"] = "completed"
    except BaseException as exc:
        state.update(
            status="failed", error=str(exc), fully_prepared_worker_admission=False
        )
    state["elapsed_seconds"] = time.monotonic() - started
    atomic(directory / "experiment.json", state)
    # Only the one fixed authorized successor; observations never bypass readiness.
    if state.get("fully_prepared_worker_admission") is True:
        state["study_invoked"] = True
        atomic(directory / "experiment.json", state)
        state["study_result"] = run_study()
        atomic(directory / "experiment.json", state)
    assert_lightweight()
    return state


def interruption(*_):
    raise InterruptedError("Owned controller interrupted; exclusive receipts retained.")


def main():
    signal.signal(signal.SIGTERM, interruption)
    signal.signal(signal.SIGHUP, interruption)
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--experiment-once", action="store_true")
    modes.add_argument("--run-once", action="store_true")
    args = parser.parse_args()
    assert_lightweight()
    result = (
        prepare()
        if args.prepare
        else experiment()
        if args.experiment_once
        else run_study()
    )
    print(json.dumps(result, indent=2, allow_nan=False))
    if result.get("status") in ("failed", "bounded_study_failed"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
