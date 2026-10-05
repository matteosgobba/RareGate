"""Chunked raw scan and local split artifacts for the LHCO R&D audit."""

import hashlib
import importlib.metadata
import json
import platform
import resource
import subprocess
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from latenttrigger.data.acquisition import acquire
from latenttrigger.data.inspection import event_fingerprints, inspect_particles
from latenttrigger.data.metadata import LHCO_RD
from latenttrigger.data.splitting import (
    PROTOCOL,
    SEED,
    assign_groups,
    development_indices,
    group_events,
    split_indices,
    validate_splits,
)

CHUNK_ROWS = 992
NMAX_CANDIDATES = (64, 96, 128, 160, 192, 256, 320, 384, 512, 700)

if TYPE_CHECKING:
    import h5py


def write_json(path: Path, content: dict) -> None:
    """Write human-readable, strict JSON (NaN is not permitted)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, allow_nan=False) + "\n")


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def peak_rss_bytes() -> int:
    """Process lifetime high-water RSS, accounting for macOS/Linux units."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(rss if platform.system() == "Darwin" else rss * 1024)


def open_raw(path: Path) -> "h5py.File":
    """Load optional HDF5 reader/Blosc decoder only for real-file analysis."""
    import h5py
    import hdf5plugin  # noqa: F401 -- register the source's Blosc decoder

    return h5py.File(path, "r")


def scan_and_split(root: Path, *, chunk_rows: int = CHUNK_ROWS) -> dict:
    """Verify source, scan structural content, freeze duplicate-safe indices.

    Complete raw data are inspected only for integrity and exact grouping.
    No feature-distribution statistics are calculated before splits exist.
    """
    if chunk_rows < 1:
        raise ValueError("Chunk size must be positive.")
    started = time.perf_counter()
    verified = acquire(data_dir=root / "data", verify_only=True)
    verify_seconds = time.perf_counter() - started
    output = root / "data" / "analysis" / PROTOCOL
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with open_raw(verified.path) as handle:
        dataset = handle["/df/block0_values"]
        if dataset.shape != (1_100_000, 2101) or dataset.dtype != np.dtype("float64"):
            raise ValueError("Unexpected pinned raw schema.")
        if not np.array_equal(handle["/df/axis0"][:], np.arange(2101)):
            raise ValueError("Unexpected column axis.")
        if not np.array_equal(handle["/df/block0_items"][:], np.arange(2101)):
            raise ValueError("Unexpected block column names.")
        n = len(dataset)
        fingerprints = np.zeros(n, dtype="V32")
        multiplicities = np.empty(n, dtype=np.uint16)
        labels = np.full(n, 255, dtype=np.uint8)
        eligible = np.empty(n, dtype=bool)
        counts = {}
        background = signal = index_mismatch = 0
        checkpoint = 0
        for start in range(0, n, chunk_rows):
            stop = min(start + chunk_rows, n)
            rows = dataset[start:stop]
            particles = rows[:, :2100].reshape(-1, 700, 3)
            truth = rows[:, 2100]
            flags = inspect_particles(particles, truth)
            for name, values in flags.items():
                if name not in ("multiplicity", "eligible"):
                    counts[name] = counts.get(name, 0) + int(values.sum())
            ok = flags["eligible"]
            fingerprints[start:stop][ok] = event_fingerprints(particles[ok])
            multiplicities[start:stop] = flags["multiplicity"]
            eligible[start:stop] = ok
            known = np.isin(truth, [0, 1])
            labels[start:stop][known] = truth[known].astype(np.uint8)
            background += int((truth == 0).sum())
            signal += int((truth == 1).sum())
            index_mismatch += int(
                (handle["/df/axis1"][start:stop] != np.arange(start, stop)).sum()
            )
            if stop * 10 // n > checkpoint:
                checkpoint = stop * 10 // n
                print(f"Structural scan and hashing: {100 * stop / n:.0f}%", flush=True)
    scan_metrics = {
        "seconds": time.perf_counter() - started,
        "peak_rss_bytes_lifetime": peak_rss_bytes(),
        "chunk_rows": chunk_rows,
        "raw_chunk_bytes": chunk_rows * 2101 * 8,
    }
    started = time.perf_counter()
    groups = group_events(fingerprints, labels, eligible)
    codes = assign_groups(groups)
    indices = split_indices(groups, codes)
    indices.update(development_indices(groups, codes))
    checks = validate_splits(groups, codes, labels)
    duplicate = groups.sizes > 1
    # No statistical EDA may proceed silently after an integrity violation.
    # Save the structural record and quarantine membership before refusing EDA.
    for name, values in {
        "event_fingerprints": fingerprints,
        "multiplicities": multiplicities,
        "labels": labels,
        "eligible": eligible,
        "row_group": groups.row_group,
        "group_fingerprints": groups.fingerprints,
        "group_representatives": groups.representatives,
        "group_sizes": groups.sizes,
        "group_labels": groups.labels,
        "group_conflicts": groups.conflicts,
        "group_split_codes": codes,
        **indices,
    }.items():
        np.save(output / f"{name}.npy", values, allow_pickle=False)
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    report = {
        "schema_version": 1,
        "created_utc": datetime.now(UTC).isoformat(),
        "fingerprint_version": "sorted-triplets-sha256-v1",
        "source": asdict(LHCO_RD),
        "source_integrity": asdict(verified.integrity),
        "protocol": PROTOCOL,
        "seed": SEED,
        "development_subset": {
            "protocol": "lhco-rd-dev-v1",
            "fraction": 0.01,
            "rounding": "floor separately per background train/validation role",
            "ranking_domain": "dev-subset",
        },
        "code_base_commit": commit,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{
                name: importlib.metadata.version(name)
                for name in ("numpy", "h5py", "hdf5plugin")
            },
        },
        "code_working_tree_dirty": bool(
            subprocess.check_output(
                [
                    "git",
                    "status",
                    "--porcelain",
                    "--untracked-files=all",
                    "--",
                    "src",
                    "scripts",
                ],
                cwd=root,
                text=True,
            ).strip()
        ),
        "integrity": {
            "events": n,
            "background": background,
            "signal": signal,
            "object_slots": 700,
            "events_exceeding_capacity": 0,
            "capacity_note": "Impossible in the validated fixed-width 700-slot schema",
            "axis1_mismatch": index_mismatch,
            **counts,
            "eligible_events": int(eligible.sum()),
            "global_multiplicity_min": int(multiplicities.min()),
            "global_multiplicity_max": int(multiplicities.max()),
            "events_at_capacity": int((multiplicities == 700).sum()),
        },
        "duplicates": {
            "unique_content_groups": len(groups.fingerprints),
            "duplicated_groups": int(duplicate.sum()),
            "events_in_duplicated_groups": int(groups.sizes[duplicate].sum()),
            "largest_group": int(groups.sizes.max()),
            "conflicting_label_groups": int(groups.conflicts.sum()),
            "excluded_duplicate_aliases": int((groups.sizes - 1).sum()),
        },
        "counts": {name: len(values) for name, values in indices.items()},
        "split_validation": checks,
        "performance": {
            "verification_seconds": verify_seconds,
            "structural_scan_and_hashing": scan_metrics,
            "grouping_splitting_persistence_seconds": time.perf_counter() - started,
            "peak_rss_bytes_lifetime": peak_rss_bytes(),
        },
        "artifacts": {
            path.name: {"sha256": file_sha256(path), "bytes": path.stat().st_size}
            for path in sorted(output.glob("*.npy"))
        },
        "analysis_code_sha256": {
            str(path.relative_to(root)): file_sha256(path)
            for path in sorted(
                [
                    *(root / "src/latenttrigger/data").glob("*.py"),
                    root / "scripts/analyze_training_data.py",
                ]
            )
        },
    }
    write_json(output / "split-manifest.json", report)
    print(
        json.dumps(
            {
                "integrity": report["integrity"],
                "duplicates": report["duplicates"],
                "counts": report["counts"],
                "performance": report["performance"],
            },
            indent=2,
        ),
        flush=True,
    )
    if not eligible.all() or index_mismatch or groups.conflicts.any():
        raise ValueError("Integrity/conflicting-label violations: review before EDA.")
    return report
