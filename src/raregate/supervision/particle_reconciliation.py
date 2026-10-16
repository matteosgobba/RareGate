"""Read-only reconciliation of consumed Task0013; never opens dataset arrays."""

import hashlib
import json
import subprocess

from raregate.supervision import particle_launcher as old

BASE = "data/baselines/task0013-particle-host-study"


def reconcile(root=old.ROOT):
    plan_path = root / old.PLAN
    plan = old.read(plan_path)
    acceptance_path = root / old.ACCEPTANCE
    acceptance = old.read(acceptance_path)
    config = old.read(root / old.CONFIG)
    profile = old.read(root / old.PROFILE)
    if (
        old.digest(config) != old.CONFIG_HASH
        or old.digest(profile) != old.PROFILE_HASH
        or plan["acceptance_sha256"] != old.file_hash(acceptance_path)
        or plan["source_sha256"] != acceptance["source_sha256"]
        or plan["profile_sha256"] != old.PROFILE_HASH
        or plan["config_sha256"] != old.CONFIG_HASH
        or plan["prompt_sha256"] != old.file_hash(root / old.PROMPT)
        or acceptance["pytest_exit_code"] != 0
        or acceptance["pytest_passed"] != 422
    ):
        raise ValueError("Historical mathematical/source acceptance/plan mismatch.")
    for rel, digest in acceptance["source_sha256"].items():
        if old.file_hash(root / rel) != digest:
            # Task0014 repairs only a CI fixture that required ignored files.
            # Preserve/verify its historical accepted bytes from the actual commit;
            # every scientific/runtime source must still match current bytes.
            if rel != "tests/test_particle_host_readiness.py":
                raise ValueError("Historical executable source changed.")
            body = subprocess.check_output(
                ["git", "show", "9d5e03b459a7edc9801a499dccb3a4b1d8cc8f78:" + rel],
                cwd=root,
                timeout=2,
            )
            if hashlib.sha256(body).hexdigest() != digest:
                raise ValueError("Historical accepted test snapshot mismatch.")
    for suffix, key in (
        (".pytest.xml", "pytest_xml_sha256"),
        (".pytest.log", "pytest_log_sha256"),
    ):
        if old.file_hash(acceptance_path.with_suffix(suffix)) != acceptance[key]:
            raise ValueError("Historical acceptance test evidence changed.")
    slot_path = root / old.SLOT
    slot = old.read(slot_path)
    if (
        slot["plan_sha256"] != old.file_hash(plan_path)
        or slot["status"] != "reserved_no_retry"
    ):
        raise ValueError("External slot lineage invalid.")
    directory = root / BASE
    workflow = old.read(directory / "workflow.json")
    if (
        [r["phase"] for r in workflow["stages"]] != list(old.PHASES)
        or workflow["status"] != "bounded_study_failed"
        or workflow["failed_phase"] != "dev"
        or workflow["error"] != "Frozen conservative dev extrapolation exceeds180s."
    ):
        raise ValueError(
            "Unexpected manual outcome; reconcile instead of assigning budget."
        )
    stages = {}
    hashes = {
        old.PLAN: old.file_hash(plan_path),
        old.SLOT: old.file_hash(slot_path),
        old.ACCEPTANCE: old.file_hash(acceptance_path),
    }
    requests = presentations = 0
    for phase in old.PHASES:
        path = directory / phase / "stage-result.json"
        record = old.read(path)
        audit_path = directory / phase / "access-audit.json"
        audit = old.read(audit_path)
        reservation_path = directory / f"{phase}-reservation.json"
        reservation = old.read(reservation_path)
        if (
            record["phase"] != phase
            or record["execution_plan_sha256"] != old.file_hash(plan_path)
            or record["acceptance_sha256"] != old.file_hash(acceptance_path)
            or record["model_config_sha256"] != old.CONFIG_HASH
            or record["engineering_policy_sha256"] != old.PROFILE_HASH
            or record["audit_file_sha256"] != old.file_hash(audit_path)
            or reservation["plan_sha256"] != old.file_hash(plan_path)
            or reservation["slot_sha256"] != old.file_hash(slot_path)
            or reservation["maximum_optimizer_steps"] != (96 if phase == "dev" else 0)
            or reservation["status"] != "reserved_no_automatic_retry"
            or audit["test_background_model_access"] is not False
            or audit["test_signal_model_access"] is not False
            or record["status"] != ("failed" if phase == "dev" else "passed")
        ):
            raise ValueError("Stage/reservation/audit provenance mismatch.")
        for item in audit["population_access"]:
            if (
                item["split"] != "train_background"
                or item["allow_test"] is not False
                or item["include_labels"] is not False
                or item["dev_only"] is not True
                or item["status"] != "completed"
            ):
                raise ValueError("Foreign/incomplete population exposure.")
        requests += len(audit["population_access"])
        presentations += sum(x["events_read"] for x in audit["population_access"])
        if (
            audit["optimizer_steps_started"] != (96 if phase == "dev" else 0)
            or audit["optimizer_steps_completed"] != audit["optimizer_steps_started"]
            or audit["possible_inflight_optimizer_step"] is not False
        ):
            raise ValueError("Unexpected/inflight step consumption.")
        hashes.update(
            {
                str(p.relative_to(root)): old.file_hash(p)
                for p in (path, audit_path, reservation_path)
            }
        )
        stages[phase] = {"status": record["status"], "audit": audit, "record": record}
    gate_path = directory / "dev/dev-gate.json"
    gate = old.read(gate_path)
    progress_path = directory / "dev/dev-progress.json"
    progress = old.read(progress_path)
    if (
        progress != {"completed_passes": 3, "steps": 96}
        or gate["passes"] != 3
        or gate["optimizer_steps"] != 96
        or gate["unique_events"] != 1024
        or gate["feasibility_pass"] is not False
        or presentations != 4160
        or requests != 5
        or stages["dev"]["audit"]["unique_dev_sample_events"] != 1024
        or stages["dev_reader"]["audit"]["unique_dev_sample_events"] != 64
        or [x["events_read"] for x in stages["dev"]["audit"]["population_access"]]
        != [1024] * 4
    ):
        raise ValueError("Historical full dev budget/cardinality not established.")
    train = 699957 * max(gate["train_pass_seconds"]) / 1024
    score = 74749 * gate["score_pass_seconds"] / 1024
    projection = 2 * (train + score)
    if (
        projection != gate["extrapolated_full_cycle_seconds"]
        or projection != 749.3431957854029
    ):
        raise ValueError("Historical throughput calculation mismatch.")
    activation_path = directory / "activation.json"
    activation = old.read(activation_path)
    computed = old.activation(
        {p: stages[p]["record"] for p in ("dev_reader", "full_custody")},
        acceptance,
        profile,
    )
    if (
        any(activation[k] != v for k, v in computed.items())
        or not computed["activated_for_bounded_dev"]
    ):
        raise ValueError("Bounded-dev activation mismatch.")
    for p, h in activation["reader_result_file_sha256"].items():
        if old.file_hash(directory / p / "stage-result.json") != h:
            raise ValueError("Reader receipt changed.")
    hashes.update(
        {
            str(p.relative_to(root)): old.file_hash(p)
            for p in (
                gate_path,
                progress_path,
                activation_path,
                directory / "workflow.json",
                directory / "dev/resource-samples.jsonl",
            )
        }
    )
    journal = [
        json.loads(v)
        for v in (directory / "dev/resource-samples.jsonl").read_text().splitlines()
    ]
    resources = stages["dev"]["record"]["resources"]
    if len(journal) != resources["samples"] or len(journal) != 287:
        raise ValueError("Probe journal/sample count mismatch.")
    return {
        "status": "historical_memory_pass_throughput_failure_no_canonical_model",
        "slot": "consumed_no_retry",
        "reserved_utc": slot["reserved_utc"],
        "stages": stages,
        "activation": activation,
        "gate": gate,
        "projection": {
            "train_term_seconds": train,
            "score_term_seconds": score,
            "factor": 2,
            "projected_full_cycle_seconds": projection,
            "target_seconds": 180,
            "measured_full_epoch": False,
            "probe_time_subtracted": False,
        },
        "access": {
            "population_requests": requests,
            "view_presentations": presentations,
            "reader_presentations": 64,
            "training_presentations": 3072,
            "scoring_presentations": 1024,
            "unique_dev_events": 1024,
            "optimizer_steps_started": 96,
            "optimizer_steps_completed": 96,
            "inflight_steps": 0,
            "remaining_original_steps": 0,
            "recorded_custody_operations": 2,
            "dev_stage_constructor_additional": True,
            "full_population_model_requests": 0,
        },
        "receipt_sha256": hashes,
    }
