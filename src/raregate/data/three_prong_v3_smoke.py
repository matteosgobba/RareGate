"""Bounded native continuous/guard integration on unallocated synthetic HDF only."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from raregate.data.three_prong_acquisition_smoke import Response, toy_payload
from raregate.data.three_prong_structure import inspect
from raregate.data.three_prong_v3_runtime import ContinuousClock, IdleAssertion
from raregate.data.three_prong_v3_transport import Transfer, hash_bytes
from raregate.evaluation.guard import Guard


def main():
    clock = ContinuousClock()
    start = clock()
    guard = Guard(start + 28, clock=clock, journal_limit=64 * 2**20)
    assertion = IdleAssertion(clock)
    result = dict(status="failed")
    try:
        guard.__enter__()
        assertion.start(start + 28)
        with tempfile.TemporaryDirectory(prefix="task0030-byte-toy-") as folder:
            root = Path(folder).resolve()
            body = toy_payload(root / "toy.h5")
            source = dict(
                url="https://example.invalid/synthetic",
                expected_size=len(body),
                expected_checksum=hashlib.md5(body, usedforsecurity=False).hexdigest(),
            )
            owned = root / "owned"
            owned.mkdir()
            seed_path = owned / "seed.part"
            historical = root / "historical.part"
            historical.write_bytes(body[:100])
            with seed_path.open("xb", buffering=0) as stream:
                original = hash_bytes(
                    historical,
                    copy_to=stream,
                    clock=clock,
                    deadline=start + 28,
                    boundary=guard.check,
                )
                os.fsync(stream.fileno())
            stat = seed_path.stat()
            seed = dict(
                **original, name="seed.part", device=stat.st_dev, inode=stat.st_ino
            )
            if stat.st_ino == historical.stat().st_ino:
                raise ValueError("Synthetic copy distinct inode")
            policy = dict(
                max_payload_requests=6,
                retry_backoff_seconds=[5, 15, 30, 60, 60],
                socket_timeout_seconds=30,
                progress_seconds=15,
                buffer_bytes=65536,
                checkpoint_bytes=2**20,
                checkpoint_seconds=5,
                checkpoint_journal_bytes=8 * 2**20,
                minimum_request_slack_seconds=2,
            )

            def boundary():
                guard.check()
                assertion.check(start + 28)

            transfer = Transfer(
                source,
                policy,
                owned,
                root / "progress.json",
                seed=seed,
                clock=clock,
                snapshot=clock.snapshot,
                boundary=boundary,
                open_response=lambda req, timeout: Response(
                    body[100:],
                    source["url"],
                    status=206,
                    extra={"Content-Range": f"bytes 100-{len(body) - 1}/{len(body)}"},
                ),
            )
            path = transfer.run(start + 28)
            integrity = hash_bytes(
                path, clock=clock, deadline=start + 28, boundary=boundary
            )
            structure = inspect(path, boundary=boundary)
            if (
                integrity["MD5"] != source["expected_checksum"]
                or structure["dataset_value_reads"] != 0
                or structure["status"] != "compatible_looking_structural_metadata_only"
            ):
                raise ValueError("Synthetic full integrity/metadata")
            if (
                historical.read_bytes() != body[:100]
                or transfer.state["new_received_bytes"] != len(body) - 100
            ):
                raise ValueError("Synthetic history/counters")
            result = dict(
                status="body_complete_awaiting_exit",
                synthetic_only=True,
                integrity=integrity,
                structure=structure,
                imported_seed_bytes=100,
                new_received_bytes=len(body) - 100,
                requests=1,
                operational_payload_requests=0,
                numerical_dataset_reads=0,
                model_scoring=0,
                elapsed_continuous_seconds=clock() - start,
            )
    finally:
        result["sleep_assertion"] = assertion.release(start + 30)
        guard.close()
        result.update(
            resources=guard.report(), resource_monitor_closed_continuous=clock()
        )
    if guard.error or not result["sleep_assertion"]["released"]:
        raise RuntimeError("Synthetic guard/assertion lifecycle failed")
    print("SYNTHETIC_RESULT=" + json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
