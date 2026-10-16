"""Read-only preflight and the single, lineage-bound Task 0011 recovery route."""

import argparse
import hashlib
import json
import math
import os
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import torch

from raregate.data.processed import content_hash
from raregate.models import particle_background as workflow
from raregate.models.particle_set import ROOT, validate_config
from raregate.training.particle_set import (
    ResourceLimitError,
    ResourceMonitor,
    measure_tensor_workspace,
    memory_snapshot,
)

CONFIG = "configs/models/compact_particle_set_autoencoder_v1.json"
OUTPUT = "data/baselines/compact-particle-set-autoencoder-task0011"
LEDGER = "data/baselines/task0011-particle-attempt-budget.json"
PLAN = "data/baselines/task0011-particle-recovery-plan.json"
PROMPT = "docs/prompts/0011-particle-set-resource-recovery.md"
PROMPT_SHA256 = "d5718d5e817872d944223591db82859163f74fc1a83cb245840a8fd07c7e3625"
PREDECESSOR = {
    "data/baselines/task0010-particle-attempt-budget.json": "2a98539f5dc9e9f3653e57681613e19a920954c8fd250f954a5aec9cd974da70",
    "data/baselines/compact-particle-set-autoencoder-v1/workflow.json": "7897e03da20a853f842e201a492e95e08f6d5ac49c7025b3d0ae40cd49900d90",
    "data/baselines/compact-particle-set-autoencoder-v1/dev/access-audit.json": "a9400a16081e6a6c759a93bba45541b0c00c48ea9754333beb849a8da3d58c48",
    "data/baselines/compact-particle-set-autoencoder-v1/dev/stage-result.json": "1e36d40fe8df79c83ee6c821a9c59039f1621b01d485384a43a0a45deb7d69a8",
    "data/task0010-synthetic-acceptance.json": "535554d2673622bba6e9992de792a50bed7fb009dc5b4df5257d544bae3e6575",
    "data/task0010-final-synthetic-acceptance.json": "3037988a7975e6af040d3648b943930bf048b4b9648c193ab754b7f2f2b10020",
    "results/tables/final/task0010-particle-set-gate-summary.json": "f4d73f4a1018b711cea0f2fd187ffd591db32a76cd498a7e53d6007d65feaa22",
}
PROTECTED = {
    "src/raregate/models/particle_set.py": "da5a46714bd6a43a1df5be76521dd2ef6ca68c86a28ee340eb825abe47b32827",
    "src/raregate/data/processed.py": "e2c908271728f0ac83ec865ef0bbf590b720868842a36cc17a8aa28598dd4766",
    "configs/models/particle_set_baseline_design_v1.json": "e358fb51c72e3d68228de2cf05d9dbd0233e4a3d7bca3edc9d7c27ed174af964",
    CONFIG: "0af735aa07f0966f1c97c8c3bea5ce6f9b1e93e80ec282ccbf0fe3f444183302",
    "configs/data/lhco_rnd_v5.json": "2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68",
}


class PreflightTimeout(ResourceLimitError):
    """A single readiness check exhausted its 30-second deadline."""


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exclusive_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as file:
        json.dump(value, file, indent=2, allow_nan=False)
        file.write("\n")


def utc_now():
    return datetime.now(UTC).isoformat()


def check_reading(sample, limits):
    """Recompute exact accounting before applying the original four ceilings."""
    for key in (
        "page_size_bytes",
        "free_pages",
        "inactive_pages",
        "available_bytes",
        "peak_rss_bytes",
        "native_heap_reserved_bytes",
        "native_heap_in_use_bytes",
    ):
        if type(sample.get(key)) is not int or sample[key] < 0:
            raise ResourceLimitError(f"Unavailable/malformed accounting: {key}.")
    if sample["page_size_bytes"] == 0 or sample["native_heap_reserved_bytes"] == 0:
        raise ResourceLimitError("Unavailable page/native heap accounting.")
    derived = (sample["free_pages"] + sample["inactive_pages"]) * sample[
        "page_size_bytes"
    ]
    if (
        sample["available_bytes"] != derived
        or sample.get("available_gib") != derived / 2**30
        or sample.get("available_method") != "Darwin_free_plus_inactive_pages"
        or sample.get("workspace_method")
        != "all_malloc_zone_reserved_bytes_conservative_upper_bound"
    ):
        raise ResourceLimitError("Memory accounting definition/arithmetic mismatch.")
    ResourceMonitor(limits, probe=lambda: sample, monitor_background=False).check(
        launch=True
    )


def host_context():
    """Bounded, read-only context; unavailable fields do not change the gate."""
    commands = {
        "pressure_context": ["/usr/bin/memory_pressure", "-Q"],
        "installed_ram": ["/usr/sbin/sysctl", "-n", "hw.memsize"],
        "current_swap_use": ["/usr/sbin/sysctl", "vm.swapusage"],
        "current_worker_rss_kib": ["/bin/ps", "-o", "rss=", "-p", str(os.getpid())],
    }
    result = {}
    for name, command in commands.items():
        try:
            completed = subprocess.run(
                command, text=True, capture_output=True, timeout=2, check=False
            )
            result[name] = {
                "command": command,
                "status": "available" if completed.returncode == 0 else "unavailable",
                "exit_code": completed.returncode,
                "output": completed.stdout.strip(),
                "error": completed.stderr.strip(),
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            result[name] = {
                "command": command,
                "status": "unavailable",
                "error": str(exc),
            }
    result["interpretation"] = (
        "Context only. vm_stat compression/page/swap counters are preserved raw; "
        "swapins/swapouts are cumulative, not current swap use. No categories are added."
    )
    return result


def sample_preflight(
    config,
    *,
    probe=memory_snapshot,
    clock=time.monotonic,
    sleep=time.sleep,
    context=host_context,
):
    """No reader, optimizer or attempt reservation; keep every scheduled reading."""
    started = clock()
    record = {
        "schema_version": 1,
        "kind": "task0011_read_only_preflight",
        "started_utc": utc_now(),
        "config_sha256": content_hash(config),
        "context": context(),
        "readings": [],
        "population_requests": 0,
        "real_events": 0,
        "real_optimizer_steps": 0,
        "attempt_reserved": False,
    }
    for index in range(3):
        reading = {"timestamp_utc": utc_now(), "elapsed_seconds": clock() - started}
        timed_out = False
        try:
            if index:
                sleep(
                    max(
                        0,
                        record["readings"][-1]["elapsed_seconds"]
                        + 2.5
                        - (clock() - started),
                    )
                )
            reading.update(timestamp_utc=utc_now(), elapsed_seconds=clock() - started)
            reading["sample"] = probe()
            check_reading(reading["sample"], config["resource_gate"])
            reading["passed"] = True
        except Exception as exc:
            reading.update(passed=False, error=str(exc))
            timed_out = isinstance(exc, PreflightTimeout)
        record["readings"].append(reading)
        if timed_out:
            break
    record["elapsed_seconds"] = clock() - started
    record["sample_span_seconds"] = (
        record["readings"][-1]["elapsed_seconds"]
        - record["readings"][0]["elapsed_seconds"]
    )
    record["ready"] = (
        len(record["readings"]) == 3
        and all(r["passed"] for r in record["readings"])
        and record["sample_span_seconds"] >= 5
        and record["elapsed_seconds"] <= 30
    )
    return record


def verify_preflight(path, config, acceptance):
    record = json.loads(path.read_text())
    digest = record.pop("record_sha256", None)
    if digest != content_hash(record):
        raise ValueError("Preflight record identity mismatch.")
    if (
        record.get("kind") != "task0011_read_only_preflight"
        or record.get("config_sha256") != content_hash(config)
        or record.get("acceptance_sha256") != file_hash(acceptance)
        or not record.get("ready")
        or len(record.get("readings", [])) != 3
        or any(
            record.get(k) != 0
            for k in ("population_requests", "real_events", "real_optimizer_steps")
        )
        or record.get("attempt_reserved") is not False
    ):
        raise ValueError("Preflight is failed, stale or outside read-only scope.")
    times = [r["elapsed_seconds"] for r in record["readings"]]
    if (
        any(type(t) not in (int, float) or not math.isfinite(t) for t in times)
        or times != sorted(times)
        or times[0] < 0
        or times[-1] - times[0] < 5
        or record["sample_span_seconds"] != times[-1] - times[0]
        or not times[-1] <= record["elapsed_seconds"] <= 30
    ):
        raise ValueError("Preflight sampling must span 5 seconds within 30 seconds.")
    for reading in record["readings"]:
        if reading.get("passed") is not True or not reading.get("timestamp_utc"):
            raise ValueError("Every preflight reading must pass.")
        check_reading(reading["sample"], config["resource_gate"])
    return {**record, "record_sha256": digest}


def verify_predecessor(config, *, root=ROOT, evidence=PREDECESSOR, protected=PROTECTED):
    validate_config(config)
    for rel, digest in {**evidence, **protected}.items():
        if file_hash(root / rel) != digest:
            raise ValueError(
                f"Task 0010 predecessor/protected identity mismatch: {rel}"
            )
    summary = json.loads(
        (
            root / "results/tables/final/task0010-particle-set-gate-summary.json"
        ).read_text()
    )
    gate = summary["dev_gate"]
    audit = json.loads(
        (
            root
            / "data/baselines/compact-particle-set-autoencoder-v1/dev/access-audit.json"
        ).read_text()
    )
    prior = json.loads(
        (
            root / "data/baselines/compact-particle-set-autoencoder-v1/workflow.json"
        ).read_text()
    )
    if (
        any(
            gate[k] != 0
            for k in (
                "unique_real_events",
                "population_requests",
                "optimizer_steps",
                "passes_completed",
            )
        )
        or audit["population_access"] != []
        or audit["test_background_model_access"] is not False
        or audit["test_signal_model_access"] is not False
        or len(prior["stages"]) != 1
        or prior["stages"][0]["stage"] != "dev"
        or prior["stages"][0]["status"] != "failed_or_interrupted"
        or prior["stages"][0]["error"] != "Launch available memory below 8 GiB."
        or prior["config_sha256"] != content_hash(config)
        or summary["executable_config_scientific_sha256"] != content_hash(config)
    ):
        raise ValueError(
            "Recovery requires verified original zero consumption and launch failure."
        )
    return dict(evidence)


def verify_worker_lineage(args, parent, config):
    """Bind recovery workers to the fixed reservation and immutable plan."""
    lineage = parent["engineering_lineage"]
    plan_path = ROOT / PLAN
    reservation = json.loads((ROOT / LEDGER).read_text())
    plan = json.loads(plan_path.read_text())
    if (
        lineage != {"task": "0011", "plan_sha256": file_hash(plan_path)}
        or reservation.get("engineering_lineage") != lineage
        or reservation.get("output") != str(ROOT / OUTPUT)
        or reservation.get("config_sha256") != content_hash(config)
        or args.output.parent.resolve() != (ROOT / OUTPUT).resolve()
        or plan.get("config_sha256") != content_hash(config)
        or plan.get("acceptance_sha256") != file_hash(args.acceptance)
        or plan.get("authorization_sha256") != PROMPT_SHA256
    ):
        raise ValueError("Recovery worker/parent/reservation lineage mismatch.")


def recover(acceptance, preflight, config):
    """One fixed Task 0011 plan/output/ledger; original supervisor owns dispatch."""
    root = ROOT
    if (root / "data/baselines/task0012-particle-memory-plan.json").exists():
        raise FileExistsError(
            "Task0011 unused recovery superseded by the Task0012 engineering study."
        )
    if (root / LEDGER).exists() or (root / PLAN).exists() or (root / OUTPUT).exists():
        raise FileExistsError("Task 0011 recovery already prepared/reserved; no retry.")
    predecessor = verify_predecessor(config, root=root)
    workflow.verify_acceptance(acceptance, config)
    verified = verify_preflight(preflight, config, acceptance)
    if file_hash(root / PROMPT) != PROMPT_SHA256:
        raise ValueError("Task 0011 one-attempt authorization prompt changed.")
    plan = {
        "schema_version": 1,
        "task": "0011",
        "authorization_prompt": PROMPT,
        "authorization_sha256": PROMPT_SHA256,
        "maximum_new_attempts": 1,
        "predecessor_file_sha256": predecessor,
        "prior_real_population_requests": 0,
        "prior_real_events": 0,
        "prior_real_optimizer_steps": 0,
        "design_scientific_sha256": config["design_scientific_sha256"],
        "config_sha256": content_hash(config),
        "acceptance_sha256": file_hash(acceptance),
        "preflight_sha256": file_hash(preflight),
        "preflight_record": verified,
        "output": str(root / OUTPUT),
        "exclusive_attempt_ledger": str(root / LEDGER),
        "created_utc": utc_now(),
        "remaining_resource_contract": config["resource_gate"],
        "gate_order": [
            "dev",
            "first_fit",
            "repeat_fit",
            "freeze",
            "background_first",
            "background_repeat",
        ],
        "engineering_only": True,
    }
    exclusive_json(root / PLAN, plan)
    args = SimpleNamespace(
        acceptance=acceptance,
        output=root / OUTPUT,
        config=root / CONFIG,
        store=root / "data/processed/lhco-rd-v1/schema-v1/full",
        dev_store=root / "data/processed/lhco-rd-v1/schema-v1/dev",
    )
    return workflow.run_task(
        args,
        config,
        attempt_budget=root / LEDGER,
        engineering_lineage={"task": "0011", "plan_sha256": file_hash(root / PLAN)},
    )


def renew_acceptance(path, config):
    """Produce acceptance from actual suite exit/count and synthetic allocations."""
    if any(
        p.exists()
        for p in (
            path,
            path.with_suffix(".pytest.log"),
            path.with_suffix(".pytest.xml"),
        )
    ):
        raise FileExistsError(
            "Acceptance output exists; preserve it and choose a new record."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    before = workflow.source_hashes()
    xml = path.with_suffix(".pytest.xml")
    with path.with_suffix(".pytest.log").open("x") as log:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", f"--junitxml={xml}"],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    cases = ET.parse(xml).findall(".//testcase")
    passed = sum(
        not any(c.find(tag) is not None for tag in ("failure", "error", "skipped"))
        for c in cases
    )
    evidence = {
        "pytest_exit_code": result.returncode,
        "pytest_passed": passed,
        "pytest_cases": len(cases),
        "pytest_xml_sha256": file_hash(xml),
        "pytest_log_sha256": file_hash(path.with_suffix(".pytest.log")),
        "config_sha256": content_hash(config),
        "source_sha256": before,
        "workspace_measurement": None,
    }
    if result.returncode == 0 and before == workflow.source_hashes():
        evidence["workspace_measurement"] = measure_tensor_workspace(config)
    exclusive_json(path, evidence)
    workflow.verify_acceptance(path, config)
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--acceptance-only", action="store_true")
    modes.add_argument("--preflight-only", action="store_true")
    modes.add_argument("--recover", action="store_true")
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--preflight", type=Path)
    args = parser.parse_args()
    config = json.loads((ROOT / CONFIG).read_text())
    validate_config(config)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True, warn_only=False)
    if args.acceptance_only:
        result = renew_acceptance(args.acceptance, config)
        print(json.dumps(result, indent=2))
        return
    workflow.verify_acceptance(args.acceptance, config)
    if not args.preflight:
        parser.error("--preflight is required for readiness output or recovery input")
    if args.preflight_only:
        if args.preflight.exists():
            raise FileExistsError("Preflight output exists; preserve all readings.")

        # Interrupt a blocked probe/command while preserving a failed readiness record.
        def alarm(*_):
            raise PreflightTimeout("Preflight exceeded 30 seconds.")

        previous = signal.signal(signal.SIGALRM, alarm)
        signal.setitimer(signal.ITIMER_REAL, 30)
        try:
            result = sample_preflight(config)
        except Exception as exc:
            result = {
                "schema_version": 1,
                "kind": "task0011_read_only_preflight",
                "ready": False,
                "error": str(exc),
                "attempt_reserved": False,
            }
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)
        result["acceptance_sha256"] = file_hash(args.acceptance)
        result["record_sha256"] = content_hash(result)
        exclusive_json(args.preflight, result)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["ready"] else 1)
    result = recover(args.acceptance, args.preflight, config)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "canonical_baseline_completed" else 1)


if __name__ == "__main__":
    main()
