"""Task0030 fresh import/transport/metadata workers; no scientific data readers."""

import argparse
import os
import re
import subprocess
import time

from raregate.benchmarks import protocol as p
from raregate.data import three_prong_v3_protocol as q
from raregate.data.three_prong_v3_runtime import (
    ContinuousClock,
    assertion_id,
    check_deadline,
)
from raregate.data.three_prong_v3_transport import Transfer, hash_bytes
from raregate.evaluation.guard import Guard, GuardError
from raregate.evaluation.guarded_audit import durable


class AssertionMonitor:
    def __init__(self, grant, clock):
        self.grant, self.clock, self.last = grant, clock, -float("inf")

    def check(self):
        check_deadline(self.clock, self.grant["operation_deadline_continuous"])
        try:
            os.kill(self.grant["sleep_helper_pid"], 0)
            os.kill(self.grant["parent_pid"], 0)
        except ProcessLookupError as error:
            raise GuardError("Sleep helper/controller lost") from error
        if self.clock() - self.last >= 5:
            raw = subprocess.check_output(
                ["/usr/bin/pmset", "-g", "assertions"], text=True, timeout=1
            )
            if (
                len(raw.encode()) > 65536
                or assertion_id(raw, self.grant["sleep_helper_pid"])
                != self.grant["sleep_assertion_id"]
            ):
                raise GuardError("Sleep assertion lost/changed")
            self.last = self.clock()
        check_deadline(self.clock, self.grant["operation_deadline_continuous"])


def bindings(root, phase, token, clock, deadline):
    spec = q.load(root)
    base = root / q.OUTPUT
    reservation, grant = (
        p.read(base / "reservation.json"),
        p.read(base / (phase + "-grant.json")),
    )
    q.require(
        phase in q.PHASES
        and grant["phase"] == phase
        and grant["token"] == token
        and grant["parent_pid"] == reservation["parent_pid"] == os.getppid()
        and not (base / phase / "receipt.json").exists(),
        "Foreign/duplicate/out-of-order worker",
    )
    q.require(
        reservation["source_file_sha256"] == q.source_map(root)
        and reservation["protocol_canonical_JSON_sha256"] == q.HASH
        and grant["reservation_file_byte_sha256"]
        == p.file_hash(base / "reservation.json"),
        "Worker frozen bindings changed",
    )
    for source, target in (
        (q.CONFIG, "protocol.json"),
        (q.ACCEPTANCE, "acceptance.json"),
        (q.AUTHORIZATION, "authorization.json"),
    ):
        q.require(
            p.file_hash(base / target) == p.file_hash(root / source),
            "Copied frozen identity changed",
        )
    seconds = spec["limits"][phase + "_seconds"]
    q.require(
        grant["stage_deadline_continuous"] == grant["started_continuous"] + seconds
        and grant["operation_deadline_continuous"]
        == grant["stage_deadline_continuous"] - 2
        and grant["stage_deadline_continuous"]
        <= reservation["whole_deadline_continuous"]
        and reservation["whole_deadline_continuous"]
        == reservation["reserved_continuous"] + 2000
        and grant["sleep_helper_pid"] == reservation["sleep_helper_pid"]
        and grant["sleep_assertion_id"] == reservation["sleep_assertion_id"],
        "Changed continuous grant or assertion binding",
    )
    q.authorization(root)
    q.metadata(root, spec, clock=clock, deadline=deadline)
    q.require(
        list(grant["predecessors"]) == list(q.PHASES[: q.PHASES.index(phase)]),
        "Wrong predecessor order",
    )
    for name, sha in grant["predecessors"].items():
        path = base / name / "parent-acceptance.json"
        q.require(
            p.file_hash(path) == sha and p.read(path)["status"] == "parent_accepted",
            "Failed/changed predecessor",
        )
        for file, digest in p.read(path)["output_file_byte_sha256"].items():
            q.require(
                p.file_hash(q.fixed(root, file)) == digest,
                "Changed predecessor receipt",
            )
    q.require(
        all(
            os.environ.get(k) == v
            for k, v in spec["thread_environment_before_imports"].items()
        ),
        "Preimport native environment changed",
    )
    check_deadline(clock, deadline)
    return spec, grant, base


def import_seed(root, spec, directory, clock, deadline, boundary):
    original = q.prefix(root, spec, clock=clock, deadline=deadline, boundary=boundary)
    path = root / q.RAW / "seed.part"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    stat = os.fstat(fd)
    access = dict(
        status="copy_inflight",
        name=path.name,
        device=stat.st_dev,
        inode=stat.st_ino,
        historical=original,
        imported_bytes_confirmed=0,
        copy_inflight=True,
        numerical_dataset_reads=0,
    )
    durable(directory / "access.json", access)
    with os.fdopen(fd, "wb", buffering=0) as stream:
        q.require(
            (stat.st_dev, stat.st_ino) != (original["device"], original["inode"]),
            "Distinct writable inode required",
        )
        copied = hash_bytes(
            root / original["path"],
            copy_to=stream,
            clock=clock,
            deadline=deadline,
            boundary=boundary,
        )
        stream.flush()
        os.fsync(stream.fileno())
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    actual = hash_bytes(path, clock=clock, deadline=deadline, boundary=boundary)
    historical = q.prefix(root, spec, clock=clock, deadline=deadline, boundary=boundary)
    q.require(
        copied == actual == {k: original[k] for k in ("bytes", "MD5", "SHA256")}
        and historical == original,
        "Copy/history identity changed",
    )
    doc = dict(
        **actual,
        name=path.name,
        device=stat.st_dev,
        inode=stat.st_ino,
        historical=original,
        response_headers=original["response_headers"],
        status="verified_independent_seed_copy",
        imported_seed_bytes=actual["bytes"],
        new_received_bytes=0,
        durable_bytes=actual["bytes"],
    )
    p.write(directory / "import.json", doc, exclusive=True)
    access.update(
        status="copied_verified_durable",
        imported_bytes_confirmed=actual["bytes"],
        copy_inflight=False,
    )
    durable(directory / "access.json", access)
    check_deadline(clock, deadline)
    return doc


def verify(root, spec, directory, clock, deadline, boundary):
    from raregate.data.three_prong_structure import inspect

    transfer = p.read(root / q.OUTPUT / "transfer/transfer.json")
    name = transfer["complete_file"]
    q.require(
        re.fullmatch(r"seed\.part|payload-[1-6]\.part", name),
        "Only owned completed representation",
    )
    path = q.fixed(root, q.RAW + "/" + name)
    access = dict(
        byte_integrity_requested=True,
        byte_integrity_confirmed=False,
        byte_read_inflight=True,
        structural_metadata_requested=False,
        structural_metadata_completed=False,
        dataset_value_reads=0,
        numerical_custody_passed=False,
    )
    durable(directory / "access.json", access)
    integrity = hash_bytes(path, clock=clock, deadline=deadline, boundary=boundary)
    valid = (
        integrity["bytes"] == spec["source"]["expected_size"]
        and integrity["MD5"] == spec["source"]["expected_checksum"]
        and integrity["SHA256"] == transfer["complete_prefix_SHA256"]
    )
    doc = dict(
        status="byte_integrity_verified_awaiting_parent"
        if valid
        else "failed_checksum_unaccepted",
        path=str(path.relative_to(root)),
        source=spec["source"],
        locally_computed=integrity,
        publisher_MD5=spec["source"]["expected_checksum"],
    )
    p.write(directory / "integrity.json", doc, exclusive=True)
    access.update(byte_read_inflight=False, byte_integrity_confirmed=valid)
    durable(directory / "access.json", access)
    q.require(valid, "Independent full size/MD5/SHA mismatch;no retry")
    boundary()
    access["structural_metadata_requested"] = True
    durable(directory / "access.json", access)
    structure = inspect(path, boundary=boundary)
    boundary()
    p.write(directory / "structure.json", structure, exclusive=True)
    access.update(
        structural_metadata_completed=True, structural_status=structure["status"]
    )
    durable(directory / "access.json", access)
    check_deadline(clock, deadline)
    return doc, structure


def execute(phase, token, root=q.ROOT):
    clock = ContinuousClock()
    base, directory = root / q.OUTPUT, root / q.OUTPUT / phase
    grant = p.read(base / (phase + "-grant.json"))
    q.require(
        grant["parent_pid"] == os.getppid()
        and grant["token"] == token
        and not (directory / "receipt.json").exists(),
        "Foreign worker before writes",
    )
    started, ordinary = clock(), time.monotonic()
    guard = None
    result = dict(
        task="0030",
        phase=phase,
        status="failed",
        optimizer_updates=0,
        model_scoring=0,
        dataset_value_reads=0,
        timings={},
        started=clock.snapshot(),
    )
    try:
        guard = Guard(
            grant["operation_deadline_continuous"],
            clock=clock,
            directory=directory,
            journal_limit=64 * 2**20,
        )
        guard.__enter__()
        monitor = AssertionMonitor(grant, clock)

        def boundary():
            guard.check()
            monitor.check()

        boundary()
        spec, grant, base = bindings(root, phase, token, clock, guard.deadline)
        result.update(
            source_file_sha256=q.source_map(root),
            protocol_canonical_JSON_sha256=q.HASH,
            grant_file_byte_sha256=p.file_hash(base / (phase + "-grant.json")),
        )
        tick = clock()
        guard.boundary(phase)
        if phase == "import":
            result["import"] = import_seed(
                root, spec, directory, clock, guard.deadline, boundary
            )
        elif phase == "transfer":
            seed = p.read(base / "import/import.json")
            transfer = Transfer(
                spec["source"],
                spec["transport"],
                root / q.RAW,
                directory / "progress.json",
                seed=seed,
                boundary=boundary,
                clock=clock,
                snapshot=clock.snapshot,
            )
            path = transfer.run(guard.deadline)
            doc = dict(
                complete_file=path.name,
                complete_bytes=path.stat().st_size,
                complete_prefix_SHA256=transfer.current["durable_prefix_SHA256"],
                source=spec["source"],
            )
            result["transfer"] = doc
            p.write(directory / "transfer.json", doc, exclusive=True)
        else:
            result["integrity"], result["structure"] = verify(
                root, spec, directory, clock, guard.deadline, boundary
            )
        result["timings"]["body_continuous_seconds"] = clock() - tick
        q.metadata(root, spec, clock=clock, deadline=guard.deadline)
        q.acceptance(root)
        boundary()
        result["status"] = "body_complete_awaiting_exit"
    except BaseException as error:
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        tick = clock()
        if guard:
            guard.close()
            result["resources"] = guard.report()
            if guard.error:
                result.update(status="failed", guard_error=guard.error)
        closed = clock()
        result["resource_monitor_closed_continuous"] = closed
        result["timings"]["cleanup_continuous_seconds"] = closed - tick
        result.update(
            finished=clock.snapshot(),
            worker_elapsed_continuous_seconds=clock() - started,
            worker_elapsed_ordinary_monotonic_seconds=time.monotonic() - ordinary,
        )
        result["output_file_byte_sha256"] = {
            str(path.relative_to(root)): p.file_hash(path)
            for path in directory.iterdir()
            if path.is_file()
            and path.name
            in {
                "import.json",
                "access.json",
                "progress.json",
                "checkpoints.jsonl",
                "transfer.json",
                "integrity.json",
                "structure.json",
            }
        }
        if clock() >= grant["stage_deadline_continuous"]:
            result.update(status="failed", late_receipt=True)
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
