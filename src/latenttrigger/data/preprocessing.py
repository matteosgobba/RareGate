"""Build and verify pinned LHCO ragged stores with frozen Task 0004 inputs."""

import argparse
import gc
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

import numpy as np

from latenttrigger import __version__
from latenttrigger.data.acquisition import acquire, raw_directory
from latenttrigger.data.analysis import (
    CHUNK_ROWS,
    file_sha256,
    open_raw,
    peak_rss_bytes,
    write_json,
)
from latenttrigger.data.eda import verify_split_artifacts
from latenttrigger.data.features import (
    OBJECT_CHANNELS,
    PHYSICAL_CHANNELS,
    Parameters,
    canonicalize,
    physical_aggregates,
    precision_regression,
    standardized_aggregates,
)
from latenttrigger.data.inspection import AGGREGATE_NAMES, event_fingerprints
from latenttrigger.data.metadata import LHCO_RD
from latenttrigger.data.processed import (
    ARRAY_DTYPES,
    ROLES,
    SCHEMA_VERSION,
    StoreIntegrityError,
    array_shapes,
    content_hash,
    verify_store,
)
from latenttrigger.data.splitting import PROTOCOL


@dataclass
class Inputs:
    """Verified source and EXISTING membership; no split generation is performed."""

    raw_path: Path
    config_bytes: bytes
    config: dict
    split_identity: dict
    split_manifest_sha256: str
    event_ids: np.ndarray
    labels: np.ndarray
    split_codes: np.ndarray
    multiplicities: np.ndarray
    development: np.ndarray
    fingerprints: np.ndarray
    scope: str


def prepare_inputs(data_dir: Path, config_path: Path, scope: str) -> Inputs:
    """Reverify source, input artifact hashes/counts and the frozen config binding."""
    if scope not in ("dev", "full"):
        raise ValueError("Choose explicit scope dev or full.")
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    Parameters.from_config(config)
    if config["source"] != asdict(LHCO_RD):
        raise ValueError("Configuration source is not pinned LHCO R&D v5.")
    verified = acquire(data_dir=data_dir, verify_only=True)
    if asdict(verified.integrity) != config["source_integrity"]:
        raise ValueError("Raw source differs from frozen config.")
    directory = data_dir / "analysis" / PROTOCOL
    report = json.loads((directory / "split-manifest.json").read_text())
    verify_split_artifacts(directory, report)
    if (
        report["source_integrity"] != config["source_integrity"]
        or report["counts"] != config["split"]["counts"]
        or report["seed"] != config["split"]["seed"]
        or report["protocol"] != config["split"]["protocol"]
    ):
        raise ValueError(
            "Task 0004 membership counts/provenance do not match; do not regenerate silently."
        )
    for name, sha in config["analysis_provenance"]["split_array_sha256"].items():
        if report["artifacts"][name]["sha256"] != sha:
            raise ValueError(f"Frozen split binding mismatch: {name}")

    def load(name: str) -> np.ndarray:
        return np.load(directory / f"{name}.npy", allow_pickle=False)

    row_group = load("row_group")
    codes = load("group_split_codes")[row_group]
    fingerprints = load("group_fingerprints")[row_group]
    dev_ids = np.sort(np.concatenate([load(f"dev_{name}") for name in list(ROLES)[:3]]))
    development = np.zeros(len(row_group), dtype=bool)
    development[dev_ids] = True
    ids = (
        dev_ids
        if scope == "dev"
        else np.sort(np.concatenate([load(name) for name in ROLES]))
    )
    identity = {
        key: report[key]
        for key in (
            "protocol",
            "seed",
            "fingerprint_version",
            "development_subset",
            "counts",
            "source_integrity",
        )
    }
    identity["array_sha256"] = {
        name: record["sha256"] for name, record in report["artifacts"].items()
    }
    return Inputs(
        verified.path,
        config_bytes,
        config,
        identity,
        file_sha256(directory / "split-manifest.json"),
        ids,
        load("labels"),
        codes,
        load("multiplicities"),
        development,
        fingerprints,
        scope,
    )


def estimated_bytes(inputs: Inputs) -> int:
    """NPY payload/header/config estimate; caller adds free-space safety margin."""
    events = len(inputs.event_ids)
    particles = int(inputs.multiplicities[inputs.event_ids].sum(dtype=np.int64))
    shapes = array_shapes(events, particles)
    return (
        sum(
            int(np.prod(shapes[name])) * np.dtype(dtype).itemsize + 256
            for name, dtype in ARRAY_DTYPES.items()
        )
        + len(inputs.config_bytes)
        + 65536
    )


def _build_metadata() -> dict:
    root = Path(__file__).resolve().parents[3]
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(
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
        )
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {
        "created_utc": datetime.now(UTC).isoformat(),
        "project_version": __version__,
        "code_commit": commit,
        "code_working_tree_dirty": dirty,
        "code_sha256": {
            file.name: file_sha256(file)
            for file in sorted(Path(__file__).parent.glob("*.py"))
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{name: version(name) for name in ("numpy", "h5py", "hdf5plugin")},
        },
    }


def _write_stage(inputs: Inputs, path: Path, chunk_rows: int) -> dict:
    params = Parameters.from_config(inputs.config)
    ids = inputs.event_ids
    if ids.ndim != 1 or len(ids) < 1 or (np.diff(ids) <= 0).any():
        raise ValueError("Expected sorted unique source row IDs.")
    e = len(ids)
    p = int(inputs.multiplicities[ids].sum(dtype=np.int64))
    shapes = array_shapes(e, p)
    maps = {}
    started = time.perf_counter()
    regression = {
        "raw_max_absolute": [0.0] * 3,
        "raw_max_relative_nonzero": [0.0] * 3,
        "wrapped_max_absolute": [0.0] * 3,
        "zeros_preserved": True,
        "resorting_after_cast_changes_events": 0,
        "wrapped_phi_outside_math_interval_after_cast": 0,
        "raw_phi_requiring_wrap": 0,
    }
    try:
        for name, dtype in ARRAY_DTYPES.items():
            maps[name] = np.lib.format.open_memmap(
                path / f"{name}.npy", mode="w+", dtype=dtype, shape=shapes[name]
            )
        maps["offsets"][0] = 0
        for name, values in {
            "event_ids": ids,
            "multiplicities": inputs.multiplicities[ids],
            "labels": inputs.labels[ids],
            "split_codes": inputs.split_codes[ids],
            "development": inputs.development[ids],
            "fingerprints": inputs.fingerprints[ids],
        }.items():
            maps[name][:] = values
        cursor = 0
        checkpoint = 0
        with open_raw(inputs.raw_path) as handle:
            dataset = handle["/df/block0_values"]
            if dataset.shape != (len(inputs.labels), 2101) or dataset.dtype != np.dtype(
                "float64"
            ):
                raise ValueError("Raw HDF shape/dtype mismatch.")
            for start in range(0, e, chunk_rows):
                stop = min(start + chunk_rows, e)
                raw_ids = ids[start:stop]
                # Slice contiguous full ranges; sparse dev rows use bounded HDF
                # fancy selection, not a full decompressed table or event list.
                rows = (
                    dataset[int(raw_ids[0]) : int(raw_ids[-1]) + 1]
                    if raw_ids[-1] - raw_ids[0] + 1 == len(raw_ids)
                    else dataset[raw_ids]
                )
                if not np.array_equal(rows[:, 2100], inputs.labels[raw_ids]):
                    raise ValueError("Raw labels disagree with frozen membership.")
                raw = rows[:, :2100].reshape(-1, 700, 3)
                if not np.array_equal(
                    event_fingerprints(raw), inputs.fingerprints[raw_ids]
                ):
                    raise ValueError(
                        "Raw event content disagrees with Task 0004 identity."
                    )
                chunk = canonicalize(raw)
                if not np.array_equal(chunk.counts, inputs.multiplicities[raw_ids]):
                    raise ValueError(
                        "Raw multiplicities disagree with frozen metadata."
                    )
                valid = chunk.valid
                size = int(chunk.counts.sum(dtype=np.int64))
                maps["particles"][cursor : cursor + size] = chunk.padded[valid]
                maps["original_slots"][cursor : cursor + size] = chunk.original_slots[
                    valid
                ]
                maps["offsets"][start + 1 : stop + 1] = cursor + np.cumsum(
                    chunk.counts, dtype=np.int64
                )
                physical = physical_aggregates(chunk.padded)
                maps["event_aggregates"][start:stop] = physical
                maps["event_features"][start:stop] = standardized_aggregates(
                    physical, params
                )
                observed = precision_regression(raw, chunk)
                for name in (
                    "raw_max_absolute",
                    "raw_max_relative_nonzero",
                    "wrapped_max_absolute",
                ):
                    regression[name] = np.maximum(
                        regression[name], observed[name]
                    ).tolist()
                regression["zeros_preserved"] &= observed["zeros_preserved"]
                for name in (
                    "resorting_after_cast_changes_events",
                    "wrapped_phi_outside_math_interval_after_cast",
                    "raw_phi_requiring_wrap",
                ):
                    regression[name] += observed[name]
                cursor += size
                if stop * 10 // e > checkpoint:
                    checkpoint = stop * 10 // e
                    for array in maps.values():
                        array.flush()
                    print(
                        f"Preprocessing {inputs.scope}: {100 * stop / e:.0f}% ({stop:,}/{e:,} events)",
                        flush=True,
                    )
        if cursor != p:
            raise ValueError("Canonical particle count mismatch; output not finalized.")
        for array in maps.values():
            array.flush()
    finally:
        maps.clear()
        gc.collect()
    (path / "configuration.json").write_bytes(inputs.config_bytes)
    files = {}
    for name in ARRAY_DTYPES:
        file = path / f"{name}.npy"
        files[file.name] = {
            "bytes": file.stat().st_size,
            "sha256": file_sha256(file),
            "shape": list(shapes[name]),
            "dtype": np.dtype(ARRAY_DTYPES[name]).str,
        }
    files["configuration.json"] = {
        "bytes": len(inputs.config_bytes),
        "sha256": file_sha256(path / "configuration.json"),
    }
    science = {
        "scope": inputs.scope,
        "events": e,
        "particles": p,
        "source_rows": len(inputs.labels),
        "source": inputs.config["source"],
        "source_integrity": inputs.config["source_integrity"],
        "config_sha256": files["configuration.json"]["sha256"],
        "split_identity": inputs.split_identity,
        "split_identity_sha256": content_hash(inputs.split_identity),
        "counts": {
            name: int((inputs.split_codes[ids] == code).sum())
            for name, code in ROLES.items()
        },
        "canonical_channels": list(PHYSICAL_CHANNELS),
        "model_channels": list(OBJECT_CHANNELS),
        "aggregate_channels": list(AGGREGATE_NAMES),
        "canonical_semantics": "All physical particles; source-float64 sorting before FP32; ragged; no truncation",
        "default_nmax": params.nmax,
        "files": files,
    }
    build = {
        **_build_metadata(),
        "input_split_manifest_sha256": inputs.split_manifest_sha256,
        "chunk_rows": chunk_rows,
        "write_hash_seconds": time.perf_counter() - started,
        "peak_rss_bytes_lifetime": peak_rss_bytes(),
        "precision_regression": regression,
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "scientific": science,
        "scientific_sha256": content_hash(science),
        "build": build,
    }
    write_json(path / "manifest.json", manifest)
    return manifest


def build_store(
    inputs: Inputs,
    destination: Path,
    *,
    chunk_rows: int = CHUNK_ROWS,
    rebuild: bool = False,
) -> dict:
    """Stage, fully verify, then promote; preserve old output until replacement passes."""
    if not 1 <= chunk_rows <= 4096:
        raise ValueError("Chunk rows must be in [1,4096].")
    destination = Path(destination).expanduser().absolute()
    if destination.is_symlink():
        raise ValueError("Refusing a symlink output.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock = destination.with_name(f".{destination.name}.lock")
    stage = destination.with_name(f".{destination.name}.partial")
    try:
        guard = lock.open("x")
    except FileExistsError as exc:
        raise ValueError(
            f"Build lock exists: {lock}; confirm no builder is running before removing it."
        ) from exc
    try:
        with guard:
            guard.write(f"pid={os.getpid()}\n")
        if destination.exists() and not rebuild:
            try:
                existing = verify_store(destination)
            except StoreIntegrityError as exc:
                raise StoreIntegrityError(
                    f"Invalid existing output; explicit --rebuild required. {exc}"
                ) from exc
            expected_config = hashlib.sha256(inputs.config_bytes).hexdigest()
            if (
                existing["scientific"]["scope"] != inputs.scope
                or existing["scientific"]["config_sha256"] != expected_config
                or existing["scientific"]["split_identity_sha256"]
                != content_hash(inputs.split_identity)
            ):
                raise StoreIntegrityError(
                    "Existing output has different frozen inputs; explicit --rebuild required."
                )
            print("Verified existing processed store; build not required.", flush=True)
            return existing
        if destination.exists() and not destination.is_dir():
            raise ValueError("Output destination is not a directory.")
        if stage.exists():
            raise ValueError(
                f"Partial output exists: {stage}; confirm no builder is running, then remove that partial deliberately."
            )
        required = estimated_bytes(inputs)
        margin = max(512 * 1024**2, required // 10)
        free = shutil.disk_usage(destination.parent).free
        print(
            f"Output: {destination}\nEstimated new bytes: {required:,}; margin: {margin:,}; free: {free:,}",
            flush=True,
        )
        if free < required + margin:
            raise OSError("Insufficient disk space for staging plus safety margin.")
        stage.mkdir()
        try:
            manifest = _write_stage(inputs, stage, chunk_rows)
            started = time.perf_counter()
            verify_store(stage)
            manifest["build"]["verification_seconds"] = time.perf_counter() - started
            manifest["build"]["peak_rss_bytes_lifetime"] = peak_rss_bytes()
            write_json(stage / "manifest.json", manifest)
            backup = None
            if destination.exists():
                backup = destination.with_name(
                    f"{destination.name}.previous-{uuid4().hex}"
                )
                destination.rename(backup)
            try:
                stage.rename(destination)
            except OSError:
                if backup is not None:
                    backup.rename(destination)
                raise
            if backup is not None:
                print(f"Previous output retained at {backup}", flush=True)
            print(
                f"Verified and finalized: {destination}\nScientific identity: {manifest['scientific_sha256']}",
                flush=True,
            )
            return manifest
        except BaseException:
            # Remove only this invocation's staging tree. A hard kill can leave
            # it/lock behind; neither is ever accepted as finalized output.
            if stage.exists():
                shutil.rmtree(stage)
            raise
    finally:
        lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--scope", choices=("dev", "full"))
    operation.add_argument("--verify", type=Path, metavar="STORE")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--chunk-rows", type=int, default=CHUNK_ROWS)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    try:
        if args.verify is not None:
            if args.rebuild or args.output:
                parser.error("--verify cannot be combined with --rebuild/--output.")
            manifest = verify_store(args.verify)
            print(
                f"Verified processed store: {args.verify}\nScientific identity: {manifest['scientific_sha256']}"
            )
        else:
            data_dir = (
                args.data_dir.expanduser().resolve()
                if args.data_dir
                else raw_directory().parents[2]
            )
            config = (
                args.config
                or raw_directory().parents[3] / "configs/data/lhco_rnd_v5.json"
            )
            inputs = prepare_inputs(data_dir, config, args.scope)
            destination = (
                args.output
                or data_dir
                / "processed"
                / PROTOCOL
                / f"schema-v{SCHEMA_VERSION}"
                / args.scope
            )
            manifest = build_store(
                inputs, destination, chunk_rows=args.chunk_rows, rebuild=args.rebuild
            )
            print(
                json.dumps(
                    {
                        "events": manifest["scientific"]["events"],
                        "particles": manifest["scientific"]["particles"],
                        "counts": manifest["scientific"]["counts"],
                    },
                    indent=2,
                )
            )
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"Preprocessing failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
