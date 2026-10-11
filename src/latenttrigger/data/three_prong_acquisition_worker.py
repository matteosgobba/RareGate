"""Fresh transfer/verification workers; byte custody and HDF metadata only."""

import argparse
import os
import re
import time

from latenttrigger.benchmarks import protocol as p
from latenttrigger.data import three_prong_acquisition_protocol as q
from latenttrigger.data.three_prong_transport import Transfer, hash_bytes
from latenttrigger.evaluation.guard import Guard
from latenttrigger.evaluation.guarded_audit import durable


def bindings(root, phase, token):
    spec = q.load(root)
    base = q.fixed(root, q.OUTPUT)
    reservation = p.read(base / "reservation.json")
    grant = p.read(base / (phase + "-grant.json"))
    q.require(
        phase in q.PHASES
        and grant["phase"] == phase
        and grant["token"] == token
        and grant["parent_pid"] == reservation["parent_pid"] == os.getppid(),
        "Foreign worker/phase/parent/token",
    )
    q.require(
        reservation["source_file_sha256"] == q.source_map(root)
        and reservation["protocol_canonical_JSON_sha256"] == q.HASH
        and grant["reservation_file_byte_sha256"]
        == p.file_hash(base / "reservation.json")
        and not (base / phase / "receipt.json").exists(),
        "Changed/duplicate worker",
    )
    q.require(
        p.file_hash(base / "protocol.json") == p.file_hash(root / q.CONFIG)
        and p.file_hash(base / "acceptance.json")
        == reservation["acceptance_file_byte_sha256"]
        == p.file_hash(root / q.ACCEPTANCE)
        and p.file_hash(base / "authorization.json")
        == reservation["authorization_file_byte_sha256"]
        == p.file_hash(root / q.AUTHORIZATION),
        "Copied identity changed",
    )
    q.authorization(root)
    q.require(
        list(grant["predecessors"]) == list(q.PHASES[: q.PHASES.index(phase)]),
        "Out of order",
    )
    for predecessor, h in grant["predecessors"].items():
        path = base / predecessor / "parent-acceptance.json"
        q.require(p.file_hash(path) == h, "Changed predecessor")
        accepted = p.read(path)
        q.require(accepted["status"] == "parent_accepted", "Failed predecessor")
        for file, sha in accepted["output_file_byte_sha256"].items():
            q.require(
                p.file_hash(q.fixed(root, file)) == sha, "Predecessor output changed"
            )
    q.require(
        all(
            os.environ.get(k) == v
            for k, v in spec["thread_environment_before_imports"].items()
        ),
        "Preimport native thread environment",
    )
    return spec, grant, base


def verify(root, spec, directory, guard):
    from latenttrigger.data.three_prong_structure import inspect

    transfer = p.read(root / q.OUTPUT / "transfer/transfer.json")
    name = transfer["complete_file"]
    q.require(
        re.fullmatch(r"payload-[123]\.part", name) is not None,
        "Only owned completed representation",
    )
    path = q.fixed(root, q.RAW + "/" + name)
    access = dict(
        source=spec["source"],
        byte_integrity_requested=True,
        byte_integrity_confirmed=False,
        byte_read_inflight=True,
        structural_metadata_requested=False,
        structural_metadata_completed=False,
        dataset_value_reads=0,
        numerical_custody_passed=False,
    )
    durable(directory / "access.json", access)
    integrity = hash_bytes(path, boundary=guard.check, deadline=guard.deadline)
    valid = (
        integrity["bytes"] == spec["source"]["expected_size"]
        and integrity["MD5"] == spec["source"]["expected_checksum"]
        and integrity["SHA256"] == transfer["complete_prefix_SHA256"]
    )
    doc = dict(
        status="byte_integrity_verified_awaiting_parent"
        if valid
        else "failed_checksum_or_size_unaccepted",
        source=spec["source"],
        path=str(path.relative_to(root)),
        publisher_MD5=spec["source"]["expected_checksum"],
        locally_computed=integrity,
        transport_file_byte_sha256=p.file_hash(
            root / q.OUTPUT / "transfer/transfer.json"
        ),
    )
    p.write(directory / "integrity.json", doc, exclusive=True)
    access.update(byte_read_inflight=False, byte_integrity_confirmed=valid)
    durable(directory / "access.json", access)
    q.require(valid, "Independent size/MD5/SHA256 verification failed;no retry")
    access["structural_metadata_requested"] = True
    durable(directory / "access.json", access)
    structure = inspect(path, boundary=guard.check)
    p.write(directory / "structure.json", structure, exclusive=True)
    access.update(
        structural_metadata_completed=True, structural_status=structure["status"]
    )
    durable(directory / "access.json", access)
    return doc, structure


def execute(phase, token, root=q.ROOT):
    base, directory = root / q.OUTPUT, root / q.OUTPUT / phase
    grant = p.read(base / (phase + "-grant.json"))
    q.require(
        grant["parent_pid"] == os.getppid()
        and grant["token"] == token
        and not (directory / "receipt.json").exists(),
        "Foreign worker before writes",
    )
    guard = None
    result = dict(
        task="0029",
        phase=phase,
        status="failed",
        optimizer_updates=0,
        model_scoring=0,
        dataset_value_reads=0,
        timings={},
    )
    started = time.monotonic()
    try:
        guard = Guard(
            grant["operation_deadline_monotonic"],
            directory=directory,
            journal_limit=64 * 2**20,
        )
        guard.__enter__()
        spec, grant, base = bindings(root, phase, token)
        result.update(
            source_file_sha256=q.source_map(root),
            protocol_canonical_JSON_sha256=q.HASH,
            grant_file_byte_sha256=p.file_hash(base / (phase + "-grant.json")),
        )
        tick = time.monotonic()
        guard.boundary(phase)
        if phase == "transfer":
            transfer = Transfer(
                spec["source"],
                spec["transport"],
                root / q.RAW,
                directory / "progress.json",
                boundary=guard.check,
            )
            path = transfer.run(grant["operation_deadline_monotonic"])
            result["transfer"] = dict(
                complete_file=path.name,
                complete_bytes=path.stat().st_size,
                complete_prefix_SHA256=transfer.current["durable_prefix_SHA256"],
                source=spec["source"],
                progress_file_byte_sha256=p.file_hash(directory / "progress.json"),
            )
            p.write(directory / "transfer.json", result["transfer"], exclusive=True)
        else:
            result["integrity"], result["structure"] = verify(
                root, spec, directory, guard
            )
        result["timings"]["body_seconds"] = time.monotonic() - tick
        q.metadata(root, spec)
        q.acceptance(root)
        guard.boundary("final_bindings")
        result["status"] = "body_complete_awaiting_exit"
    except BaseException as error:
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        tick = time.monotonic()
        if guard:
            guard.close()
            result["resources"] = guard.report()
            if guard.error:
                result.update(status="failed", guard_error=guard.error)
        result.update(
            resource_monitor_closed_monotonic=time.monotonic(),
            worker_reported_wall_seconds=time.monotonic() - started,
        )
        result["timings"]["cleanup_seconds"] = time.monotonic() - tick
        result["output_file_byte_sha256"] = {
            str(path.relative_to(root)): p.file_hash(path)
            for path in directory.iterdir()
            if path.is_file()
            and path.name
            in {
                "progress.json",
                "checkpoints.jsonl",
                "transfer.json",
                "integrity.json",
                "structure.json",
                "access.json",
            }
        }
        p.write(directory / "receipt.json", result, exclusive=True)
    return 0 if result["status"] == "body_complete_awaiting_exit" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=q.PHASES)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    return execute(args.phase, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
