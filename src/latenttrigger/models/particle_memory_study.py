"""Exclusive Task0012 provisional reader study; conditional dev only, never fit."""

import argparse
import json
import secrets
import signal
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

from latenttrigger.data.processed import ProcessedStore, content_hash
from latenttrigger.models import particle_background as bg
from latenttrigger.models import particle_recovery as previous
from latenttrigger.models.particle_set import ROOT, validate_config, validate_store
from latenttrigger.training.particle_resources import (
    PolicyMonitor,
    activation_decision,
    policy_snapshot,
    validate_policy,
    validate_sample,
)
from latenttrigger.training.particle_set import ResourceLimitError

PROFILE = "configs/resources/particle_memory_policy_v2.json"
PLAN = "data/baselines/task0012-particle-memory-plan.json"
OUTPUT = "data/baselines/task0012-particle-memory-study"
PROMPT = "docs/prompts/0012-particle-memory-policy-review.md"
PROMPT_HASH = "e647c97f9d84e5c7a9c0c8e1df76009c0d931421be1bf91b7b92e01185a6b2be"
EXTRA_PREDECESSOR = {
    "results/tables/final/task0011-particle-set-recovery-summary.json": "40e0f094950e34933fb8e672598cecf69257b2ed3dee827e7ba18297a76a170f",
    "data/baselines/task0011-preflight-after-reboot-2026-10-07.json": "e99c614468d6d1c5e737991a34820a02bd9e40ec26e59dc2894889b01d1176eb",
    "data/baselines/task0011-particle-preflight.json": "5d31e61967d6027f576143b807c5c689d56d2932c2957545127328794dfa17ae",
    "data/task0011-reviewed-synthetic-acceptance.json": "1cef87bb612eb7066e1f3e91cb01ba16ff84d3152c2198945098a012c8d79159",
}
PHASES = ("pilot_preflight", "dev_reader", "full_custody", "dev_preflight", "dev")


class PreflightDeadline(ResourceLimitError):
    """One bounded readiness deadline, with earlier readings preserved."""


def atomic_json(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def verify_unused_predecessor(config):
    previous.verify_predecessor(config)
    for rel, digest in EXTRA_PREDECESSOR.items():
        if previous.file_hash(ROOT / rel) != digest:
            raise ValueError("Task0011 predecessor identity changed.")
    if any(
        (ROOT / p).exists() for p in (previous.LEDGER, previous.PLAN, previous.OUTPUT)
    ):
        raise ValueError(
            "Task0011 recovery may have consumed allowance; reconcile before study."
        )
    if previous.file_hash(ROOT / PROMPT) != PROMPT_HASH:
        raise ValueError("Task0012 authorization prompt changed.")


def authorize_phase(phase, state):
    if phase not in PHASES:
        raise ValueError(
            "Only Task0012 readiness/readers/dev allowed; fit/calibration forbidden."
        )
    position = PHASES.index(phase)
    if [r["phase"] for r in state["stages"]] != list(PHASES[:position]) or any(
        r["status"] != "passed" for r in state["stages"]
    ):
        raise ValueError(
            "Previous gate failed/missing/foreign; dependent stage forbidden."
        )
    if position >= 3 and not state.get("activation", {}).get(
        "activated_for_bounded_dev"
    ):
        raise ValueError(
            "Frozen justified policy activation required before dev readiness."
        )


class StudyAudit(bg.Audit):
    """Counts/seen-bitset and reserved/completed steps, no scores or raw IDs."""

    def __init__(self, path):
        super().__init__(path)
        self.custody, self.steps_started, self.steps_completed = [], 0, 0
        self.sample_positions, self.seen = {}, np.zeros(1024, dtype=bool)

    def save(self):
        atomic_json(
            self.path,
            {
                "population_access": self.records,
                "custody_access": self.custody,
                "optimizer_steps_started": self.steps_started,
                "optimizer_steps_completed": self.steps_completed,
                "possible_inflight_optimizer_step": self.steps_started
                != self.steps_completed,
                "unique_dev_sample_events": int(self.seen.sum()),
                "sample_relative_seen_bitset_hex": np.packbits(self.seen)
                .tobytes()
                .hex(),
                "test_background_model_access": False,
                "test_signal_model_access": False,
            },
        )

    def request(self, split, purpose, dev, expected):
        if split != "train_background" or dev is not True or expected not in (64, 1024):
            raise ValueError(
                "Study refuses foreign/selection/calibration/test/truth population."
            )
        return super().request(split, purpose, dev, expected)

    def bind_sample(self, ids):
        if (
            ids.shape != (1024,)
            or ids.dtype.kind not in "iu"
            or not (np.diff(ids) > 0).all()
        ):
            raise ValueError("Expected exactly source-ordered frozen1024 dev sample.")
        self.sample_positions = {int(v): i for i, v in enumerate(ids)}

    def observe_ids(self, ids):
        if not self.sample_positions or any(
            int(v) not in self.sample_positions for v in ids
        ):
            raise ValueError("View contains foreign/unbound development IDs.")
        for value in ids:
            self.seen[self.sample_positions[int(value)]] = True
        self.save()

    def observe_optimizer(self, optimizer):
        def before(*_):
            if self.steps_started >= 96 or self.steps_started != self.steps_completed:
                raise ValueError(
                    "Original cumulative96-step allowance exhausted/inflight."
                )
            self.steps_started += 1
            self.save()  # reservation persisted before real optimizer mutation

        def after(*_):
            self.steps_completed += 1
            self.save()

        optimizer.register_step_pre_hook(before)
        optimizer.register_step_post_hook(after)


def stable_preflight(
    config,
    profile,
    *,
    probe=policy_snapshot,
    clock=time.monotonic,
    sleep=time.sleep,
    context=previous.host_context,
):
    started, rows = clock(), []
    contextual = context()
    for index in range(3):
        row = {
            "timestamp_utc": previous.utc_now(),
            "elapsed_seconds": clock() - started,
        }
        tick = clock()
        timed_out = False
        try:
            if index:
                sleep(max(0, rows[-1]["elapsed_seconds"] + 2.5 - (clock() - started)))
            row.update(
                timestamp_utc=previous.utc_now(), elapsed_seconds=clock() - started
            )
            tick = clock()
            row["sample"] = probe()
            validate_sample(row["sample"], config, profile, launch=True)
            row["passed"] = True
        except Exception as exc:
            row.update(passed=False, error=str(exc))
            timed_out = isinstance(exc, PreflightDeadline)
        row["probe_seconds"] = clock() - tick
        rows.append(row)
        if timed_out:
            break
    span = rows[-1]["elapsed_seconds"] - rows[0]["elapsed_seconds"]
    elapsed = clock() - started
    return {
        "status": "passed"
        if len(rows) == 3
        and all(r["passed"] for r in rows)
        and span >= 5
        and elapsed <= 30
        else "failed",
        "readings": rows,
        "context": contextual,
        "sample_span_seconds": span,
        "elapsed_seconds": elapsed,
        "engineering_policy_sha256": content_hash(profile),
        "model_config_sha256": content_hash(config),
        "scope": "read_only_stable_preflight",
        "policy_v1_compliance": False,
        "population_requests": 0,
        "real_events": 0,
        "real_optimizer_steps": 0,
    }


def reader_measurement(phase, config, monitor, audit):
    if phase not in ("dev_reader", "full_custody"):
        raise ValueError("Unsupported custody/view phase.")
    scope = "dev" if phase == "dev_reader" else "full"
    path = ROOT / f"data/processed/lhco-rd-v1/schema-v1/{scope}"
    timings, store = {}, None
    custody = {
        "scope": scope,
        "operation": "unchanged_full_constructor_custody_verification",
        "population_requested": False,
        "status": "requested",
    }
    audit.custody.append(custody)
    audit.save()
    try:
        monitor.phase = "constructor_verification_and_mapping"
        monitor.check()
        tick = time.monotonic()
        store = ProcessedStore(path)
        validate_store(store.manifest, config, dev=scope == "dev")
        timings["constructor_verification_and_mapping_seconds"] = (
            time.monotonic() - tick
        )
        monitor.check()
        mapped = sum(a.nbytes for a in store._arrays.values())
        if phase == "dev_reader":
            monitor.phase = "sample_membership"
            ids = store.event_ids("train_background", allow_test=False, dev_only=True)[
                :1024
            ]
            audit.bind_sample(ids)
            request = audit.request(
                "train_background", "engineering_reader_first64", True, 64
            )
            monitor.phase = "two_bounded_views"
            tick = time.monotonic()
            for start in (0, 32):
                monitor.check()
                batch = store.read_ids(
                    "train_background",
                    ids[start : start + 32],
                    allow_test=False,
                    include_labels=False,
                    dev_only=True,
                )
                view = batch.model_view(nmax=384)
                if batch.labels is not None or len(view.features) != 32:
                    raise ValueError("Malformed/truth/unbounded reader view.")
                audit.advance(request, 32)
                audit.observe_ids(batch.event_ids)
                monitor.check()
                del view, batch
                monitor.phase = "batch_release"
                monitor.check()
                monitor.phase = "two_bounded_views"
            timings["two_views_including_accounting_and_release_seconds"] = (
                time.monotonic() - tick
            )
            request["status"] = "completed"
            audit.save()
        monitor.phase = "reader_close"
        tick = time.monotonic()
        store.close()
        store = None
        timings["close_seconds"] = time.monotonic() - tick
        monitor.check()
        custody["status"] = "completed"
        audit.save()
        return {
            "timings": timings,
            "mapped_array_virtual_bytes": int(mapped),
            "custody_completed": True,
            "view_events": 64 if scope == "dev" else 0,
            "mapped_bytes_are_not_RSS_or_anonymous_allocation": True,
        }
    except BaseException as exc:
        custody.update(status="failed_or_interrupted", error=str(exc))
        audit.save()
        for request in audit.records:
            if request["status"] == "requested":
                request.update(status="failed_or_interrupted", error=str(exc))
        audit.save()
        raise
    finally:
        if store is not None:
            store.close()


def worker(phase, token, acceptance, config, profile):
    plan_path, output = ROOT / PLAN, ROOT / OUTPUT
    plan = json.loads(plan_path.read_text())
    state = json.loads((output / "workflow.json").read_text())
    reservation = json.loads((output / f"{phase}-reservation.json").read_text())
    authorize_phase(phase, state)
    if (
        reservation.get("phase") != phase
        or reservation.get("maximum_optimizer_steps") != (96 if phase == "dev" else 0)
        or reservation.get("status") != "reserved_no_automatic_retry"
        or reservation["token"] != token
        or reservation["plan_sha256"] != previous.file_hash(plan_path)
        or plan["acceptance_sha256"] != previous.file_hash(acceptance)
        or plan["profile_sha256"] != validate_policy(profile, config)
        or plan["config_sha256"] != content_hash(config)
    ):
        raise ValueError("Worker acceptance/profile/config/parent lineage mismatch.")
    directory = output / phase
    directory.mkdir(exist_ok=False)
    audit = StudyAudit(directory / "access-audit.json")
    audit.save()
    monitor = PolicyMonitor(
        config, profile, journal=directory / "resource-samples.jsonl"
    )
    monitor.started = reservation["started_monotonic"]
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True, warn_only=False)
    result = {}
    try:
        if phase.endswith("preflight"):

            def alarm(*_):
                raise PreflightDeadline("Preflight30-second deadline.")

            old = signal.signal(signal.SIGALRM, alarm)
            signal.setitimer(
                signal.ITIMER_REAL,
                max(0.001, 30 - (time.monotonic() - monitor.started)),
            )
            try:
                result = stable_preflight(config, profile)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old)
        else:
            seconds = profile["phase_limits_seconds"][phase]
            with (
                monitor,
                monitor.deadline(
                    "whole_phase_including_startup",
                    seconds - (time.monotonic() - monitor.started),
                ),
            ):
                if phase == "dev":
                    monitor.phase = "original_dev_gate"
                    result = bg.run_dev(
                        ROOT / "data/processed/lhco-rd-v1/schema-v1/dev",
                        config,
                        directory,
                        monitor,
                        audit,
                        optimizer_observer=audit.observe_optimizer,
                    )
                else:
                    result = reader_measurement(phase, config, monitor, audit)
            result["status"] = "passed"
    except BaseException as exc:
        result.update(status="failed", error=str(exc), downstream_authorized=False)
    result.update(
        phase=phase,
        resources=monitor.report(),
        audit_file_sha256=previous.file_hash(audit.path),
        engineering_policy_sha256=content_hash(profile),
        model_config_sha256=content_hash(config),
        acceptance_sha256=previous.file_hash(acceptance),
        policy_v1_compliance=False,
        optimizer_steps_started=audit.steps_started,
        optimizer_steps_completed=audit.steps_completed,
        unique_dev_sample_events=int(audit.seen.sum()),
    )
    atomic_json(directory / "stage-result.json", result)
    print(json.dumps(result), flush=True)
    return 0 if result["status"] == "passed" else 1


def run_study(acceptance, config, profile):
    bg.verify_acceptance(acceptance, config)
    validate_policy(profile, config)
    verify_unused_predecessor(config)
    output, plan_path = ROOT / OUTPUT, ROOT / PLAN
    if output.exists() or plan_path.exists():
        raise FileExistsError("Task0012 study reserved; no retry/reset.")
    plan = {
        "schema_version": 1,
        "task": "0012",
        "scope": "engineering_readers_and_conditional_original_dev_only",
        "prompt_sha256": PROMPT_HASH,
        "predecessor_file_sha256": {**previous.PREDECESSOR, **EXTRA_PREDECESSOR},
        "config_sha256": content_hash(config),
        "design_sha256": config["design_scientific_sha256"],
        "profile_sha256": content_hash(profile),
        "acceptance_sha256": previous.file_hash(acceptance),
        "created_utc": previous.utc_now(),
        "fixed_output": str(output),
        "prior_real_optimizer_steps": 0,
        "maximum_total_real_optimizer_steps": 96,
        "supersedes_unused_task0011_route": True,
        "gate_order": list(PHASES),
        "canonical_or_calibration_authorized": False,
    }
    previous.exclusive_json(plan_path, plan)
    output.mkdir(exist_ok=False)
    state = {
        "task": "0012",
        "status": "started",
        "stages": [],
        "engineering_policy_sha256": content_hash(profile),
        "config_sha256": content_hash(config),
        "policy_v1_compliance": False,
    }
    ledger = output / "workflow.json"
    atomic_json(ledger, state)
    active_phase = "pilot_preflight"

    def dispatch(phase):
        nonlocal active_phase
        active_phase = phase
        authorize_phase(phase, state)
        token = secrets.token_hex(24)
        started = time.monotonic()
        previous.exclusive_json(
            output / f"{phase}-reservation.json",
            {
                "phase": phase,
                "token": token,
                "plan_sha256": previous.file_hash(plan_path),
                "started_monotonic": started,
                "status": "reserved_no_automatic_retry",
                "maximum_optimizer_steps": 96 if phase == "dev" else 0,
            },
        )
        with (output / f"{phase}.log").open("x") as log:
            child = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.models.particle_memory_study",
                    "--worker",
                    phase,
                    "--token",
                    token,
                    "--acceptance",
                    str(acceptance),
                ],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            try:
                child.wait(timeout=profile["phase_limits_seconds"][phase])
            except subprocess.TimeoutExpired:
                child.terminate()
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
        path = output / phase / "stage-result.json"
        result = (
            json.loads(path.read_text())
            if path.exists()
            else {
                "phase": phase,
                "status": "failed",
                "error": "Worker terminated/timeout before final report; reservation/audit retained",
            }
        )
        state["stages"].append(result)
        atomic_json(ledger, state)
        if result["status"] != "passed":
            raise ResourceLimitError(result.get("error", "Stable preflight failed."))
        if result.get("engineering_policy_sha256") != content_hash(
            profile
        ) or result.get("model_config_sha256") != content_hash(config):
            raise ValueError("Foreign phase result identity.")
        return result

    try:
        dispatch("pilot_preflight")
        a = dispatch("dev_reader")
        b = dispatch("full_custody")
        state["activation"] = activation_decision(
            {"dev_reader": a, "full_custody": b},
            bg.verify_acceptance(acceptance, config),
            profile,
        )
        state["activation"]["reader_result_file_sha256"] = {
            p: previous.file_hash(output / p / "stage-result.json")
            for p in ("dev_reader", "full_custody")
        }
        atomic_json(ledger, state)
        previous.exclusive_json(output / "activation.json", state["activation"])
        if not state["activation"]["activated_for_bounded_dev"]:
            state["status"] = "policy_reviewed_not_activated"
        else:
            dispatch("dev_preflight")
            dispatch("dev")
            state["status"] = (
                "bounded_policy_v2_feasibility_established_canonical_pending"
            )
    except BaseException as exc:
        state.update(
            status="provisional_launch_still_blocked"
            if active_phase == "pilot_preflight"
            else (
                "reader_measurement_failed"
                if active_phase in ("dev_reader", "full_custody")
                else "policy_v2_dev_gate_failed"
            ),
            error=str(exc),
            failed_phase=active_phase,
        )
    state["canonical_training_authorized"] = False
    atomic_json(ledger, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--acceptance-only", action="store_true")
    mode.add_argument("--run-study", action="store_true")
    mode.add_argument("--worker", choices=PHASES, help=argparse.SUPPRESS)
    parser.add_argument("--token", help=argparse.SUPPRESS)
    parser.add_argument("--acceptance", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / previous.CONFIG).read_text())
    validate_config(config)
    profile = json.loads((ROOT / PROFILE).read_text())
    validate_policy(profile, config)
    if args.acceptance_only:
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        torch.use_deterministic_algorithms(True, warn_only=False)
        print(json.dumps(previous.renew_acceptance(args.acceptance, config), indent=2))
        return
    bg.verify_acceptance(args.acceptance, config)
    if args.worker:
        raise SystemExit(
            worker(args.worker, args.token, args.acceptance, config, profile)
        )
    result = run_study(args.acceptance, config, profile)
    print(json.dumps(result, indent=2))
    raise SystemExit(
        0
        if result["status"]
        == "bounded_policy_v2_feasibility_established_canonical_pending"
        else 1
    )


if __name__ == "__main__":
    main()
