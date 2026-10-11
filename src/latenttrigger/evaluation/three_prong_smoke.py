"""Actual native toy custody/score integration; no operational signal/score input."""

import json
import os
import tempfile
import time
from pathlib import Path

from latenttrigger.benchmarks import protocol as p
from latenttrigger.evaluation.guard import Guard


def toy_spec(root):
    import h5py
    import numpy as np

    from latenttrigger.evaluation import three_prong_protocol as q
    from latenttrigger.evaluation.guarded_smoke import fixture

    entries, candidates, Store = fixture(root, background=33, signal=4)
    original = root / "original"
    original.mkdir()
    p.write(original / "manifest.json", Store().manifest)
    transform = p.read(p.ROOT / "configs/data/lhco_rnd_v5.json")
    p.write(root / "transform.json", transform)
    raw = root / "toy.h5"
    rows = np.zeros((4, 2100), np.float64)
    for i in range(4):
        rows[i, :6] = [1 + i, 0, 0, 1, 0, 1]
    with h5py.File(raw, "w") as h:
        h.create_dataset("/df/block0_values", data=rows)
        h.create_dataset("/df/block0_items", data=np.arange(2100))
        h.create_dataset("/df/axis0", data=np.arange(2100))
        h.create_dataset("/df/axis1", data=np.arange(4))
    import hashlib

    b = raw.read_bytes()
    source = dict(
        dataset="synthetic",
        version="v5",
        record_id=6466204,
        doi="synthetic-only",
        filename=raw.name,
        url="https://example.invalid/no_network",
        expected_size=len(b),
        expected_checksum=hashlib.md5(b, usedforsecurity=False).hexdigest(),
        checksum_algorithm="md5",
        license="CC-BY-4.0",
        publisher_expected_events=4,
        role="reserved_signal_three_prong_evaluation_only",
        local_payload_sha256=None,
    )
    fp = np.asarray([bytes([i]) * 32 for i in range(8)], dtype="V32")
    np.save(original / "fingerprints.npy", fp, allow_pickle=False)
    cached = []
    for entry, candidate in zip(entries, candidates, strict=True):
        x = np.tile(np.arange(1, 9, dtype=np.float32) / 16, (33, 1))
        path = root / (entry["name"] + "-background.npy")
        np.save(
            path,
            candidate["model"].score(
                x,
                feature_names=tuple(
                    transform["preprocessing"]["aggregates"]["channels"]
                ),
            ),
            allow_pickle=False,
        )
        entry["results_scientific_sha256"] = p.read(root / entry["results_path"])[
            "scientific_sha256"
        ]
        entry["thresholds"] = p.read(root / entry["results_path"])["scientific"][
            "thresholds"
        ]
        cached.append(
            dict(
                path=path.name,
                file_byte_sha256=p.file_hash(path),
                bytes=path.stat().st_size,
                shape=[33],
            )
        )
    spec = dict(
        source=source,
        features=transform["preprocessing"]["aggregates"]["channels"],
        candidates=entries,
        cached_background=cached,
        original_store=dict(
            path="original", scientific_sha256=Store().manifest["scientific_sha256"]
        ),
        original_fingerprints=dict(
            path="original/fingerprints.npy",
            bytes=(original / "fingerprints.npy").stat().st_size,
            sha256=p.file_hash(original / "fingerprints.npy"),
            shape=[8],
            dtype="|V32",
        ),
        transform=dict(
            path="transform.json",
            file_byte_sha256=p.file_hash(root / "transform.json"),
            canonical_JSON_sha256=p.digest(transform),
        ),
        limits=dict(chunk_rows=2),
        encoding=dict(widths=[2100, 2101]),
    )
    base = root / q.OUTPUT
    acq = base / "acquire"
    acq.mkdir(parents=True)
    p.write(
        acq / "acquisition.json",
        dict(path=raw.name, integrity=dict(sha256=hashlib.sha256(b).hexdigest())),
    )
    return spec, candidates


def exercise(root, guard):
    from latenttrigger.evaluation import three_prong_core as n
    from latenttrigger.evaluation import three_prong_protocol as q
    from latenttrigger.evaluation.guarded_reporting import reporting
    from latenttrigger.evaluation.three_prong_audit import Audit

    spec, _ = toy_spec(root)
    directory = root / q.OUTPUT / "prepare"
    directory.mkdir()
    n.prepare(
        root,
        spec,
        directory,
        Audit(directory / "access.json", dict(synthetic=True)),
        guard,
    )
    for phase in ("PCA", "AE"):
        directory = root / q.OUTPUT / phase
        directory.mkdir()
        n.evaluate(
            root,
            spec,
            phase,
            directory,
            Audit(directory / "access.json", dict(synthetic=True)),
            guard,
        )
    return reporting(root / q.OUTPUT, spec["candidates"], make_figures=False)


def main():
    from latenttrigger.evaluation import three_prong_protocol as q

    expected = q.load()["runtime"]["thread_environment_before_imports"]
    if any(os.environ.get(k) != v for k, v in expected.items()):
        raise ValueError("Preimport thread environment")
    started = time.monotonic()
    guard = Guard(started + 28)
    limiter = None
    try:
        guard.__enter__()
        from latenttrigger.benchmarks import core

        limiter, threads = core.configure_threads(
            dict(runtime=dict(thread_environment_before_imports=expected))
        )
        with tempfile.TemporaryDirectory(prefix="task0028-toy-") as raw:
            exercise(Path(raw).resolve(), guard)
        if threads != core.effective_threads():
            raise ValueError("Synthetic native thread drift")
    finally:
        if limiter:
            limiter.restore_original_limits()
        guard.close()
    if guard.error:
        raise ValueError(guard.error)
    print(
        json.dumps(
            dict(
                status="body_complete_awaiting_exit",
                synthetic_only=True,
                operational_signal_payloads=0,
                operational_cached_score_loads=0,
                operational_fingerprint_loads=0,
                wall_seconds=time.monotonic() - started,
                resources=guard.report(),
                resource_monitor_closed_monotonic=time.monotonic(),
            ),
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
