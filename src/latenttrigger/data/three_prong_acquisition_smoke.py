"""Guarded synthetic transport/byte/HDF-metadata integration; never live input."""

import hashlib
import io
import json
import tempfile
import time
from email.message import Message
from pathlib import Path

from latenttrigger.data.three_prong_structure import inspect
from latenttrigger.data.three_prong_transport import Transfer, hash_bytes
from latenttrigger.evaluation.guard import Guard


class Response:
    def __init__(self, body, url, *, status=200, extra=None):
        self.stream = io.BytesIO(body)
        self.url, self.status = url, status
        self.headers = Message()
        self.headers["Content-Length"] = str(len(body))
        for k, v in (extra or {}).items():
            self.headers[k] = v

    def geturl(self):
        return self.url

    def read(self, size):
        return self.stream.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stream.close()


def toy_payload(path):
    import h5py

    with h5py.File(path, "w") as h:
        h.create_dataset(
            "/df/block0_values", shape=(100000, 2100), dtype="<f8", chunks=(128, 2100)
        )
        for key, size in (("block0_items", 2100), ("axis0", 2100), ("axis1", 100000)):
            h.create_dataset("/df/" + key, shape=(size,), dtype="<i8", chunks=True)
    return path.read_bytes()  # Toy byte payload only; no dataset values.


def main():
    guard = Guard(time.monotonic() + 28, journal_limit=64 * 2**20)
    try:
        guard.__enter__()
        with tempfile.TemporaryDirectory(prefix="task0029-byte-toy-") as folder:
            root = Path(folder).resolve()
            body = toy_payload(root / "toy.h5")
            source = dict(
                url="https://example.invalid/synthetic",
                expected_size=len(body),
                expected_checksum=hashlib.md5(body, usedforsecurity=False).hexdigest(),
            )
            policy = dict(
                max_payload_requests=3,
                retry_backoff_seconds=[5, 15],
                socket_timeout_seconds=30,
                progress_seconds=15,
                buffer_bytes=65536,
                checkpoint_bytes=2**20,
                checkpoint_seconds=5,
                checkpoint_journal_bytes=8 * 2**20,
                minimum_request_slack_seconds=2,
            )
            owned = root / "owned"
            owned.mkdir()
            transfer = Transfer(
                source,
                policy,
                owned,
                root / "progress.json",
                open_response=lambda req, timeout: Response(body, source["url"]),
                boundary=guard.check,
            )
            path = transfer.run(guard.deadline)
            integrity = hash_bytes(path, boundary=guard.check, deadline=guard.deadline)
            if (
                integrity["bytes"] != len(body)
                or integrity["MD5"] != source["expected_checksum"]
            ):
                raise ValueError("Synthetic byte verification")
            structure = inspect(path, boundary=guard.check)
            if (
                structure["status"] != "compatible_looking_structural_metadata_only"
                or structure["dataset_value_reads"] != 0
            ):
                raise ValueError("Synthetic structure-only inspection")
            result = dict(
                status="body_complete_awaiting_exit",
                synthetic_only=True,
                integrity=integrity,
                structure=structure,
                requests=1,
                operational_payload_requests=0,
                numerical_dataset_reads=0,
                operational_fingerprint_or_cached_score_reads=0,
                model_scoring=0,
            )
    finally:
        guard.close()
    if guard.error:
        raise RuntimeError(guard.error)
    result.update(
        resources=guard.report(), resource_monitor_closed_monotonic=time.monotonic()
    )
    print("SYNTHETIC_RESULT=" + json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
