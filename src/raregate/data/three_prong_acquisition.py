"""Task0029-only stdlib controller, separate network transfer from scientific work."""

import argparse
import json
import os
import re
import secrets
import signal
import sys
import time
from contextlib import contextmanager
from urllib.request import Request

from raregate.benchmarks import protocol as p
from raregate.data import three_prong_acquisition_protocol as q
from raregate.data.three_prong_transport import hash_bytes, opener
from raregate.evaluation.guard import parent_check
from raregate.evaluation.guarded import supervise


@contextmanager
def alarm(deadline):
    old = signal.getsignal(signal.SIGALRM)

    def expired(*_):
        raise TimeoutError("Independent parent preflight/finalization deadline")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, deadline - time.monotonic()))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def network_check(spec):
    """One bounded primary metadata GET, before any reservation/payload request."""
    url = spec["network_preflight"]["metadata_url"]
    with opener()(
        Request(
            url,
            headers={
                "User-Agent": "RareGate/0.1.0",
                "Accept-Encoding": "identity",
            },
        ),
        timeout=10,
    ) as response:
        q.require(
            response.status == 200 and response.geturl() == url,
            "Primary metadata connectivity/source failure",
        )
        content = response.read(16385)
        q.require(len(content) <= 16384, "Unbounded connectivity metadata")
    value = json.loads(content)
    q.validate_api(value, spec["source"])
    return dict(
        status="approved_context_primary_metadata_connectivity_confirmed",
        metadata_requests=1,
        payload_requests=0,
        URL=url,
        bytes=len(content),
        metadata_canonical_JSON_sha256=p.digest(value),
        utc=p.now(),
    )


def controller_rss():
    import resource

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )


def accepted_stage(root, phase, result, dispatch, reservation):
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
        and result.get("timings", {}).get("cleanup_seconds", 3) <= 2
    )
    required = {
        q.OUTPUT + "/" + phase + "/" + f
        for f in (
            ("progress.json", "checkpoints.jsonl", "transfer.json")
            if phase == "transfer"
            else ("integrity.json", "structure.json", "access.json")
        )
    }
    try:
        valid &= set(result.get("output_file_byte_sha256", {})) == required
        for path, h in result.get("output_file_byte_sha256", {}).items():
            valid &= p.file_hash(q.fixed(root, path)) == h
        spec = q.load(root)
        if phase == "transfer":
            progress = p.read(root / q.OUTPUT / "transfer/progress.json")
            transfer = result["transfer"]
            valid &= (
                progress["status"] == "transfer_complete_unverified"
                and progress["source"] == spec["source"]
                and progress["complete_file"] == transfer["complete_file"]
                and re.fullmatch(r"payload-[123]\.part", transfer["complete_file"])
                is not None
                and 0 < len(progress["files"]) <= 3
                and progress["durably_checkpointed_bytes"]
                <= progress["written_bytes"]
                <= progress["received_bytes"]
                and len(progress["requests"]) <= 3
                and progress["redirects_followed"] == 0
                and transfer["complete_bytes"] == spec["source"]["expected_size"]
                and transfer["source"] == spec["source"]
                and transfer["progress_file_byte_sha256"]
                == p.file_hash(root / q.OUTPUT / "transfer/progress.json")
            )
            complete = next(
                f for f in progress["files"] if f["name"] == transfer["complete_file"]
            )
            valid &= (
                complete["durable_bytes"]
                == complete["written_bytes"]
                == spec["source"]["expected_size"]
                and complete["durable_prefix_SHA256"]
                == transfer["complete_prefix_SHA256"]
                and q.fixed(root, q.RAW + "/" + complete["name"]).stat().st_size
                == spec["source"]["expected_size"]
            )
        else:
            integrity = result["integrity"]
            valid &= (
                integrity["status"] == "byte_integrity_verified_awaiting_parent"
                and integrity["source"] == spec["source"]
                and integrity["locally_computed"]["bytes"]
                == spec["source"]["expected_size"]
                and integrity["locally_computed"]["MD5"]
                == spec["source"]["expected_checksum"]
                and result["structure"]["dataset_value_reads"] == 0
            )
            access = p.read(root / q.OUTPUT / "verify/access.json")
            valid &= (
                access["source"] == spec["source"]
                and access["byte_integrity_confirmed"]
                and access["structural_metadata_requested"]
                and access["structural_metadata_completed"]
                and access["dataset_value_reads"] == 0
                and not access["numerical_custody_passed"]
            )
    except (OSError, KeyError, TypeError, ValueError, StopIteration):
        valid = False
    closed, end = (
        result.get("resource_monitor_closed_monotonic"),
        dispatch.get("exit_observed_monotonic"),
    )
    return dict(
        status="parent_accepted" if valid else "parent_rejected",
        phase=phase,
        dispatch=dispatch,
        output_file_byte_sha256=result.get("output_file_byte_sha256", {}),
        receipt_file_byte_sha256=p.file_hash(root / q.OUTPUT / phase / "receipt.json")
        if (root / q.OUTPUT / phase / "receipt.json").exists()
        else None,
        terminal_unaccounted_seconds=max(0, end - closed)
        if closed is not None and end is not None
        else None,
    )


def inventory(raw, deadline, *, ownership=None):
    rows = []
    for path in sorted(raw.iterdir()):
        if path.name == "manifest.json" or path.is_symlink() or not path.is_file():
            continue
        row = dict(
            name=path.name,
            retained_bytes_after_reaping=path.stat().st_size,
            accepted_verified_bytes=0,
            status="retained_unaccepted",
        )
        if ownership is not None and (
            path.name not in ownership
            or (path.stat().st_dev, path.stat().st_ino)
            != (ownership[path.name]["device"], ownership[path.name]["inode"])
        ):
            row.update(
                byte_integrity=None,
                digest_unavailable_reason="Unknown/foreign inode;metadata only,not read",
            )
            rows.append(row)
            continue
        try:
            row["byte_integrity"] = hash_bytes(path, deadline=deadline)
        except (Exception, KeyboardInterrupt) as error:
            row.update(
                byte_integrity=None,
                digest_unavailable_reason=f"{type(error).__name__}: {error}",
            )
        rows.append(row)
    return rows


def finalize(root, spec, outcome, *, raw_owned, deadline):
    parent_check(deadline=deadline)
    raw = root / q.RAW
    progress_path = root / q.OUTPUT / "transfer/progress.json"
    ownership = (
        {f["name"]: f for f in p.read(progress_path)["files"]}
        if progress_path.exists()
        else {}
    )
    rows = inventory(raw, deadline, ownership=ownership) if raw_owned else []
    outcome["retained_files"] = rows
    if outcome["status"] == "all_workers_parent_accepted":
        integrity = p.read(root / q.OUTPUT / "verify/integrity.json")
        original = q.fixed(root, integrity["path"])
        row = next(r for r in rows if r["name"] == original.name)
        q.require(
            row["byte_integrity"] == integrity["locally_computed"],
            "Complete bytes changed after accepted verification",
        )
        parent_check(deadline=deadline)
        destination = raw / spec["source"]["filename"]
        os.link(
            original, destination, follow_symlinks=False
        )  # Atomic exclusive promotion; never overwrite.
        # Keep the owned full .part as evidence: two names share one inode, not two copies.
        manifest = dict(
            status="verified_bytes_acceptance_requires_session_parent",
            required_session_parent_acceptance=q.OUTPUT + "/parent-acceptance.json",
            source=spec["source"],
            publisher_MD5=spec["source"]["expected_checksum"],
            local_SHA256=integrity["locally_computed"]["SHA256"],
            verified_bytes=integrity["locally_computed"]["bytes"],
            file=destination.name,
            retained_complete_representation=original.name,
            byte_verification_file_byte_sha256=p.file_hash(
                root / q.OUTPUT / "verify/integrity.json"
            ),
            transport_file_byte_sha256=p.file_hash(
                root / q.OUTPUT / "transfer/progress.json"
            ),
            protocol_canonical_JSON_sha256=q.HASH,
            protocol_file_byte_sha256=p.file_hash(root / q.CONFIG),
            acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
            structural_metadata=p.read(root / q.OUTPUT / "verify/structure.json"),
            numerical_custody_passed=False,
            model_evaluation_accessed=False,
        )
        p.write(raw / "manifest.json", manifest, exclusive=True)
        parent_check(deadline=deadline)
        row.update(
            status="accepted_verified_bytes",
            accepted_verified_bytes=row["retained_bytes_after_reaping"],
            promoted_name=destination.name,
            promotion="exclusive_hard_link;owned_full_representation_retained_same_inode",
        )
        outcome.update(
            status="parent_accepted_verified_artifact",
            manifest_file_byte_sha256=p.file_hash(raw / "manifest.json"),
            accepted_verified_bytes=manifest["verified_bytes"],
        )
    parent_check(deadline=deadline)


def run(root=q.ROOT, *, network_authorized=False):
    started = time.monotonic()
    whole_deadline = started + 1900
    owned = raw_owned = False
    base = root / q.OUTPUT
    outcome = dict(
        task="0029",
        status="blocked_before_reservation",
        stages=[],
        optimizer_updates=0,
        new_model_scoring=0,
        numerical_dataset_reads=0,
        cached_background_numeric_loads=0,
        original_fingerprint_numeric_loads=0,
        original_test_background_model_accessed=True,
        original_test_signal_model_accessed=True,
        new_three_prong_model_accessed=False,
        accepted_verified_bytes=0,
    )
    try:
        parent_check()
        q.require(
            sys.platform == "darwin" and network_authorized is True,
            "Approved network execution context and Darwin accounting required before reservation",
        )
        current = q.authorization(root)
        spec = current["specification"]
        q.namespace(root)
        space = q.disk_space(root, spec)
        with alarm(min(time.monotonic() + 15, whole_deadline)):
            connected = network_check(spec)
        q.require(
            whole_deadline - time.monotonic() >= 1875,
            "Complete stage/finalization slack required before reservation",
        )
        base.mkdir(parents=True, exist_ok=False)
        owned = True
        (root / q.RAW).mkdir(parents=True, exist_ok=False)
        raw_owned = True
        reservation = dict(
            task="0029",
            parent_pid=os.getpid(),
            reserved_utc=p.now(),
            protocol_canonical_JSON_sha256=q.HASH,
            source_file_sha256=q.source_map(root),
            acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
            authorization_file_byte_sha256=p.file_hash(root / q.AUTHORIZATION),
            plan_sha256=p.digest(current),
            network=connected,
            storage=space,
            code=p.code_context(root),
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
            parent_check(deadline=whole_deadline)
            seconds = spec["limits"][phase + "_seconds"]
            q.require(
                time.monotonic() + seconds + 15 <= whole_deadline,
                "No complete next phase/finalization slack",
            )
            directory = base / phase
            directory.mkdir()
            token = secrets.token_hex(24)
            tick = time.monotonic()
            grant = dict(
                phase=phase,
                token=token,
                parent_pid=os.getpid(),
                started_monotonic=tick,
                operation_deadline_monotonic=tick + seconds - 2,
                predecessors=previous.copy(),
                reservation_file_byte_sha256=p.file_hash(base / "reservation.json"),
            )
            p.write(base / (phase + "-grant.json"), grant, exclusive=True)
            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "raregate.data.three_prong_acquisition_worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                directory / "worker.log",
                root=root,
                environment=environment,
                stage_seconds=seconds,
                whole_deadline=whole_deadline,
            )
            result = (
                p.read(directory / "receipt.json")
                if (directory / "receipt.json").exists()
                else dict(status="receipt_missing")
            )
            accepted = accepted_stage(root, phase, result, dispatch, reservation)
            p.write(directory / "dispatch.json", dispatch, exclusive=True)
            p.write(directory / "parent-acceptance.json", accepted, exclusive=True)
            previous[phase] = p.file_hash(directory / "parent-acceptance.json")
            outcome["stages"].append(dict(phase=phase, worker=result, parent=accepted))
            p.write(base / "workflow.json", outcome)
            q.require(
                accepted["status"] == "parent_accepted",
                "Failed stage stops session: " + phase,
            )
        outcome["status"] = "all_workers_parent_accepted"
    except BaseException as error:
        outcome.update(
            status="failed_consumed_preserved"
            if owned
            else "blocked_before_reservation",
            error=f"{type(error).__name__}: {error}",
        )
    finally:
        if owned:
            tick = time.monotonic()
            deadline = min(tick + 15, whole_deadline)
            try:
                with alarm(deadline):
                    finalize(
                        root,
                        q.load(root),
                        outcome,
                        raw_owned=raw_owned,
                        deadline=deadline,
                    )
            except BaseException as error:
                outcome.update(
                    status="failed_consumed_preserved",
                    finalization_error=f"{type(error).__name__}: {error}",
                    accepted_verified_bytes=0,
                )
                for row in outcome.get("retained_files", []):
                    row.update(status="retained_unaccepted", accepted_verified_bytes=0)
            outcome["finalization_seconds"] = time.monotonic() - tick
        rss = controller_rss()
        outcome.update(
            wall_seconds=time.monotonic() - started,
            controller_peak_RSS_bytes=rss,
            reserved_consumed=owned,
            new_session_retry_allowed=False,
            finished_utc=p.now(),
        )
        if outcome["wall_seconds"] > 1900 or rss > 128 * 2**20:
            outcome.update(
                status="failed_consumed_preserved"
                if owned
                else "blocked_before_reservation",
                accepted_verified_bytes=0,
            )
            for row in outcome.get("retained_files", []):
                row.update(status="retained_unaccepted", accepted_verified_bytes=0)
        if owned:
            p.write(base / "workflow.json", outcome)
            p.write(
                base / "parent-acceptance.json",
                dict(
                    status=outcome["status"],
                    workflow_file_byte_sha256=p.file_hash(base / "workflow.json"),
                    source_file_sha256=q.source_map(root),
                ),
                exclusive=True,
            )
    print(outcome["status"], outcome.get("error", ""), flush=True)
    return 0 if outcome["status"] == "parent_accepted_verified_artifact" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-acquisition", action="store_true", required=True)
    parser.add_argument("--network-authorized", action="store_true")
    args = parser.parse_args()
    return run(network_authorized=args.network_authorized)


if __name__ == "__main__":
    raise SystemExit(main())
