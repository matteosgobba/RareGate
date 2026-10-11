"""One Task0030 sleep-aware acquisition controller; stdlib, no scientific work."""

import argparse
import json
import os
import re
import secrets
import sys
import time
from urllib.request import Request

from latenttrigger.benchmarks import protocol as p
from latenttrigger.data import three_prong_v3_protocol as q
from latenttrigger.data.three_prong_transport import opener
from latenttrigger.data.three_prong_v3_runtime import (
    ContinuousClock,
    IdleAssertion,
    alarm,
    check_deadline,
    supervise,
)
from latenttrigger.data.three_prong_v3_transport import hash_bytes
from latenttrigger.evaluation.guard import parent_check
from latenttrigger.evaluation.guarded_audit import durable


def network_check(spec, clock, deadline):
    """Exactly one bounded primary metadata GET in approved real execution context."""
    url = spec["network_preflight"]["metadata_url"]
    with alarm(clock, deadline):
        with opener()(
            Request(
                url,
                headers={
                    "User-Agent": "LatentTrigger/0.1.0 Task0030",
                    "Accept-Encoding": "identity",
                },
            ),
            timeout=10,
        ) as response:
            check_deadline(clock, deadline)
            q.require(
                response.status == 200 and response.geturl() == url,
                "Primary metadata source/network mismatch",
            )
            content = response.read(16385)
            check_deadline(clock, deadline)
            q.require(len(content) <= 16384, "Unbounded primary metadata")
        value = json.loads(content)
        q.old.validate_api(value, spec["source"])
    return dict(
        status="approved_context_primary_metadata_connectivity_confirmed",
        URL=url,
        metadata_requests=1,
        payload_requests=0,
        bytes=len(content),
        metadata_canonical_JSON_sha256=p.digest(value),
        received=clock.snapshot(),
    )


def accepted_stage(root, phase, result, dispatch, reservation, *, clock, deadline):
    check_deadline(clock, deadline)
    resource = result.get("resources", {})
    valid = (
        result.get("status") == "body_complete_awaiting_exit"
        and result.get("phase") == phase
        and result.get("source_file_sha256")
        == reservation["source_file_sha256"]
        == q.source_map(root)
        and result.get("protocol_canonical_JSON_sha256") == q.HASH
        and result.get("grant_file_byte_sha256")
        == p.file_hash(root / q.OUTPUT / (phase + "-grant.json"))
        and result.get("optimizer_updates")
        == result.get("model_scoring")
        == result.get("dataset_value_reads")
        == 0
        and dispatch["parent_confirms_normal_exit"]
        and dispatch["child_reaped"]
        and dispatch["within_deadline"]
        and resource.get("latched_error") is None
        and resource.get("owned_thread_alive") is False
        and 0 < resource.get("peak_rss_bytes", 0) <= 6 * 2**30
        and 0 < resource.get("native_heap_reserved_bytes", 0) <= 512 * 2**20
        and result.get("timings", {}).get("cleanup_continuous_seconds", 3) <= 2
    )
    files = {
        "import": ("import.json", "access.json"),
        "transfer": ("progress.json", "checkpoints.jsonl", "transfer.json"),
        "verify": ("integrity.json", "structure.json", "access.json"),
    }[phase]
    required = {q.OUTPUT + "/" + phase + "/" + f for f in files}
    valid &= set(result.get("output_file_byte_sha256", {})) == required
    for path, sha in result.get("output_file_byte_sha256", {}).items():
        valid &= p.file_hash(q.fixed(root, path)) == sha
    spec = q.load(root)
    if valid and phase == "import":
        doc = p.read(root / q.OUTPUT / "import/import.json")
        valid &= (
            doc["status"] == "verified_independent_seed_copy"
            and doc["bytes"] == spec["prefix"]["bytes"]
            and doc["SHA256"] == spec["prefix"]["SHA256"]
            and (doc["device"], doc["inode"])
            != (doc["historical"]["device"], doc["historical"]["inode"])
        )
    elif valid and phase == "transfer":
        doc = p.read(root / q.OUTPUT / "transfer/progress.json")
        valid &= (
            doc["status"] == "transfer_complete_unverified"
            and doc["source"] == spec["source"]
            and len(doc["files"]) <= 7
            and len(doc["requests"]) <= 6
            and doc["historical_seed_bytes_imported"] == spec["prefix"]["bytes"]
            and doc["durably_checkpointed_bytes"]
            <= doc["written_bytes"]
            <= doc["historical_seed_bytes_imported"] + doc["new_received_bytes"]
            and doc["inflight"] is None
            and result["transfer"]["complete_bytes"] == spec["source"]["expected_size"]
            and re.fullmatch(
                r"seed\.part|payload-[1-6]\.part", result["transfer"]["complete_file"]
            )
            is not None
        )
    elif valid:
        valid &= (
            result["integrity"]["status"] == "byte_integrity_verified_awaiting_parent"
            and result["structure"]["dataset_value_reads"] == 0
        )
    check_deadline(clock, deadline)
    return dict(
        status="parent_accepted" if valid else "parent_rejected",
        phase=phase,
        dispatch=dispatch,
        output_file_byte_sha256=result.get("output_file_byte_sha256", {}),
        receipt_file_byte_sha256=p.file_hash(root / q.OUTPUT / phase / "receipt.json")
        if (root / q.OUTPUT / phase / "receipt.json").exists()
        else None,
        terminal_unaccounted_continuous_seconds=max(
            0,
            dispatch["exit_observed_continuous"]
            - result["resource_monitor_closed_continuous"],
        )
        if result.get("resource_monitor_closed_continuous") is not None
        else None,
    )


def inventory(root, clock, deadline):
    raw, base = root / q.RAW, root / q.OUTPUT
    ownership = {}
    if (base / "import/access.json").exists():
        doc = p.read(base / "import/access.json")
        ownership[doc["name"]] = doc
    if (base / "transfer/progress.json").exists():
        ownership.update(
            {f["name"]: f for f in p.read(base / "transfer/progress.json")["files"]}
        )
    rows = []
    for path in sorted(raw.iterdir()):
        if not re.fullmatch(r"seed\.part|payload-[1-6]\.part", path.name):
            continue
        s = path.lstat()
        row = dict(
            name=path.name,
            retained_bytes_after_reaping=s.st_size,
            accepted_complete_bytes=0,
            device=s.st_dev,
            inode=s.st_ino,
            status="retained_unaccepted",
        )
        identity = ownership.get(path.name, {})
        if (
            path.is_symlink()
            or not path.is_file()
            or (s.st_dev, s.st_ino) != (identity.get("device"), identity.get("inode"))
        ):
            row.update(byte_integrity=None, error="Unknown/foreign inode;metadata only")
        else:
            try:
                row["byte_integrity"] = hash_bytes(path, clock=clock, deadline=deadline)
            except BaseException as error:
                row.update(
                    byte_integrity=None, error=f"{type(error).__name__}: {error}"
                )
        rows.append(row)
    return rows


def promote(root, spec, outcome, clock, deadline):
    check_deadline(clock, deadline)
    q.require(
        outcome["sleep_assertion"]["released"] is True,
        "Confirmed assertion release required for acceptance",
    )
    integrity = p.read(root / q.OUTPUT / "verify/integrity.json")
    original = q.fixed(root, integrity["path"])
    row = next(r for r in outcome["retained_files"] if r["name"] == original.name)
    q.require(
        row["byte_integrity"] == integrity["locally_computed"],
        "Complete bytes changed after worker exit",
    )
    destination = root / q.RAW / spec["source"]["filename"]
    check_deadline(clock, deadline)
    os.link(original, destination, follow_symlinks=False)
    check_deadline(clock, deadline)
    manifest = dict(
        status="verified_bytes_acceptance_requires_session_parent",
        required_session_parent_acceptance=q.OUTPUT + "/parent-acceptance.json",
        source=spec["source"],
        publisher_MD5=spec["source"]["expected_checksum"],
        local_SHA256=integrity["locally_computed"]["SHA256"],
        verified_bytes=integrity["locally_computed"]["bytes"],
        file=destination.name,
        retained_complete_representation=original.name,
        promotion="exclusive_hard_link_owned_full_only",
        protocol_canonical_JSON_sha256=q.HASH,
        protocol_file_byte_sha256=p.file_hash(root / q.CONFIG),
        acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
        sleep_assertion_released=True,
        structural_metadata=p.read(root / q.OUTPUT / "verify/structure.json"),
        numerical_custody_passed=False,
        model_evaluation_accessed=False,
    )
    q.require(
        not (root / q.RAW / "manifest.json").exists(), "Exclusive manifest required"
    )
    durable(root / q.RAW / "manifest.json", manifest)
    check_deadline(clock, deadline)
    outcome.update(
        status="parent_accepted_verified_artifact",
        accepted_complete_bytes=manifest["verified_bytes"],
        manifest_file_byte_sha256=p.file_hash(root / q.RAW / "manifest.json"),
    )
    row.update(
        status="accepted_verified_bytes",
        accepted_complete_bytes=manifest["verified_bytes"],
        promoted_name=destination.name,
    )


def publish(root, outcome, clock, deadline):
    """Durable parent record; a publication overrun supersedes any provisional success."""
    base = root / q.OUTPUT

    def write_parent():
        durable(base / "workflow.json", outcome)
        durable(
            base / "parent-acceptance.json",
            dict(
                status=outcome["status"],
                accepted_complete_bytes=outcome["accepted_complete_bytes"],
                sleep_assertion_released=outcome["sleep_assertion"].get(
                    "released", False
                ),
                workflow_file_byte_sha256=p.file_hash(base / "workflow.json"),
                source_file_sha256=q.source_map(root),
                protocol_canonical_JSON_sha256=q.HASH,
                publication_observed_continuous=clock(),
                acceptance_deadline_continuous=deadline,
            ),
        )

    write_parent()
    try:
        check_deadline(clock, deadline)
    except BaseException as error:
        outcome.update(
            status="failed_consumed_preserved",
            accepted_complete_bytes=0,
            publication_error=f"{type(error).__name__}: {error}",
            publication_overshoot_seconds=max(0, clock() - deadline),
        )
        for row in outcome.get("retained_files", []):
            row.update(accepted_complete_bytes=0, status="retained_unaccepted")
        # Evidence writes after an overrun are rejection records, never new acceptance.
        write_parent()


def run(root=q.ROOT, *, network_authorized=False):
    clock = ContinuousClock()
    started, ordinary = clock(), time.monotonic()
    preflight_deadline = started + 60
    owned = raw_owned = False
    assertion = IdleAssertion(clock)
    spec = None
    base = root / q.OUTPUT
    outcome = dict(
        task="0030",
        status="blocked_before_reservation",
        stages=[],
        started=clock.snapshot(),
        optimizer_updates=0,
        new_model_scoring=0,
        numerical_dataset_reads=0,
        cached_background_numeric_loads=0,
        original_fingerprint_numeric_loads=0,
        original_test_background_model_accessed=True,
        original_test_signal_model_accessed=True,
        new_three_prong_model_accessed=False,
        accepted_complete_bytes=0,
    )
    whole_deadline = None
    try:
        parent_check(clock=clock, deadline=preflight_deadline)
        q.require(
            network_authorized is True and sys.platform == "darwin",
            "Approved context and Darwin required",
        )
        current = q.authorization(root)
        spec = current["specification"]
        q.namespace(root)
        outcome["metadata"] = q.metadata(
            root, spec, clock=clock, deadline=preflight_deadline
        )
        outcome["historical_prefix"] = q.prefix(
            root, spec, clock=clock, deadline=preflight_deadline
        )
        space = q.disk_space(root, spec)
        assertion.start(preflight_deadline)
        connected = network_check(spec, clock, min(preflight_deadline, clock() + 15))
        assertion.check(preflight_deadline, force=True)
        outcome["preflight_continuous_seconds"] = clock() - started
        reserved = clock()
        whole_deadline = reserved + spec["limits"]["whole_seconds"]
        base.mkdir(parents=True, exist_ok=False)
        owned = True
        (root / q.RAW).mkdir(parents=True, exist_ok=False)
        raw_owned = True
        reservation = dict(
            task="0030",
            parent_pid=os.getpid(),
            reserved=clock.snapshot(),
            reserved_continuous=reserved,
            whole_deadline_continuous=whole_deadline,
            source_file_sha256=q.source_map(root),
            protocol_canonical_JSON_sha256=q.HASH,
            acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
            authorization_file_byte_sha256=p.file_hash(root / q.AUTHORIZATION),
            plan_sha256=p.digest(current),
            network=connected,
            storage=space,
            sleep_helper_pid=assertion.child.pid,
            sleep_assertion_id=assertion.identity,
            historical_prefix=outcome["historical_prefix"],
            code=p.code_context(root),
        )
        q.require(
            reservation["source_file_sha256"] == current["source_file_sha256"],
            "Source drift while reserving;consumed",
        )
        p.write(base / "reservation.json", reservation, exclusive=True)
        for source, target in (
            (q.CONFIG, "protocol.json"),
            (q.ACCEPTANCE, "acceptance.json"),
            (q.AUTHORIZATION, "authorization.json"),
        ):
            with (base / target).open("xb") as stream:
                stream.write((root / source).read_bytes())
        environment = dict(
            os.environ,
            **spec["thread_environment_before_imports"],
            PYTHONPATH=str(root / "src"),
            PYTHONUNBUFFERED="1",
        )
        previous = {}
        for phase in q.PHASES:
            assertion.check(whole_deadline)
            parent_check(clock=clock, deadline=whole_deadline)
            seconds = spec["limits"][phase + "_seconds"]
            q.require(
                clock() + seconds + 15 <= whole_deadline,
                "Complete next phase/finalization slack required",
            )
            directory = base / phase
            directory.mkdir()
            token, tick = secrets.token_hex(24), clock()
            stage_deadline = tick + seconds
            grant = dict(
                phase=phase,
                token=token,
                started_continuous=tick,
                parent_pid=os.getpid(),
                started=clock.snapshot(),
                operation_deadline_continuous=stage_deadline - 2,
                stage_deadline_continuous=stage_deadline,
                predecessors=previous.copy(),
                reservation_file_byte_sha256=p.file_hash(base / "reservation.json"),
                sleep_helper_pid=assertion.child.pid,
                sleep_assertion_id=assertion.identity,
            )
            p.write(base / (phase + "-grant.json"), grant, exclusive=True)
            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "latenttrigger.data.three_prong_v3_worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                directory / "worker.log",
                root=root,
                environment=environment,
                clock=clock,
                operation_deadline=stage_deadline - 2,
                stage_deadline=stage_deadline,
                whole_deadline=whole_deadline,
                monitor=lambda: assertion.check(whole_deadline),
            )
            durable(directory / "dispatch.json", dispatch)
            result = (
                p.read(directory / "receipt.json")
                if (directory / "receipt.json").exists()
                else dict(status="receipt_missing")
            )
            try:
                accepted = accepted_stage(
                    root,
                    phase,
                    result,
                    dispatch,
                    reservation,
                    clock=clock,
                    deadline=stage_deadline,
                )
            except BaseException as error:
                accepted = dict(
                    status="parent_rejected",
                    phase=phase,
                    dispatch=dispatch,
                    error=f"{type(error).__name__}: {error}",
                )
            durable(directory / "parent-acceptance.json", accepted)
            outcome["stages"].append(dict(phase=phase, worker=result, parent=accepted))
            print(
                f"Task0030 {phase}: {accepted['status']}; continuous={dispatch['elapsed_continuous_seconds']:.3f}s",
                flush=True,
            )
            q.require(
                accepted["status"] == "parent_accepted",
                "Failed stage stops session: " + phase,
            )
            previous[phase] = p.file_hash(directory / "parent-acceptance.json")
        outcome["status"] = "all_workers_parent_accepted"
    except BaseException as error:
        outcome.update(
            status="failed_consumed_preserved"
            if owned
            else "blocked_before_reservation",
            error=f"{type(error).__name__}: {error}",
        )
    finally:
        final_started = clock()
        final_deadline = (
            min(final_started + 15, whole_deadline)
            if whole_deadline
            else final_started + 15
        )
        try:
            # Assertion release is required on every outcome, BEFORE byte acceptance.
            outcome["sleep_assertion"] = assertion.release(final_deadline)
            if raw_owned:
                outcome["retained_files"] = inventory(root, clock, final_deadline)
                outcome["historical_prefix_after_session"] = q.prefix(
                    root, spec, clock=clock, deadline=final_deadline
                )
            if outcome["status"] == "all_workers_parent_accepted":
                q.metadata(root, spec, clock=clock, deadline=final_deadline)
                q.acceptance(root)
                promote(root, spec, outcome, clock, final_deadline)
            parent_check(clock=clock, deadline=final_deadline)
        except BaseException as error:
            outcome.update(
                status="failed_consumed_preserved"
                if owned
                else "blocked_before_reservation",
                finalization_error=f"{type(error).__name__}: {error}",
                accepted_complete_bytes=0,
                sleep_assertion=assertion.evidence,
            )
            for row in outcome.get("retained_files", []):
                row.update(accepted_complete_bytes=0, status="retained_unaccepted")
        outcome.update(
            finished=clock.snapshot(),
            finalization_continuous_seconds=clock() - final_started,
            elapsed_continuous_seconds=clock() - started,
            elapsed_ordinary_monotonic_seconds=time.monotonic() - ordinary,
            reserved_consumed=owned,
            new_session_retry_allowed=False,
            controller_peak_RSS_bytes=parent_check(clock=clock),
            reserved_continuous_seconds=clock() - reserved if owned else None,
            whole_overshoot_seconds=max(0, clock() - whole_deadline)
            if whole_deadline
            else 0,
        )
        if owned:
            publish(root, outcome, clock, final_deadline)
        else:
            path = root / "data/task0030-validation/prerequisite-outcome.json"
            q.require(not path.exists(), "Preserve existing prerequisite outcome")
            durable(path, outcome)
    print(
        json.dumps(
            {
                k: outcome[k]
                for k in (
                    "status",
                    "accepted_complete_bytes",
                    "reserved_consumed",
                    "elapsed_continuous_seconds",
                )
            }
        ),
        flush=True,
    )
    return 0 if outcome["status"] == "parent_accepted_verified_artifact" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-session", action="store_true", required=True)
    parser.add_argument("--network-authorized", action="store_true", required=True)
    args = parser.parse_args()
    return run(network_authorized=args.network_authorized)


if __name__ == "__main__":
    raise SystemExit(main())
