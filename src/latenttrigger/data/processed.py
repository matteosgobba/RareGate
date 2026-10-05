"""Schema-v1 processed store verification and split-guarded NumPy reading."""

import hashlib
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from latenttrigger.data.analysis import CHUNK_ROWS, file_sha256
from latenttrigger.data.features import (
    OBJECT_CHANNELS,
    PHYSICAL_CHANNELS,
    ModelView,
    Parameters,
    model_view,
    standardized_aggregates,
)
from latenttrigger.data.inspection import AGGREGATE_NAMES
from latenttrigger.data.splitting import SPLIT_NAMES

SCHEMA_VERSION = 1
MAX_BATCH_EVENTS = 4096
ROLES = {name: code for code, name in SPLIT_NAMES.items() if code}
ARRAY_DTYPES = {
    "particles": "<f4",
    "original_slots": "<u2",
    "offsets": "<i8",
    "event_ids": "<i8",
    "multiplicities": "<u2",
    "labels": "|u1",
    "split_codes": "|u1",
    "development": "|b1",
    "fingerprints": "|V32",
    "event_aggregates": "<f8",
    "event_features": "<f4",
}


class StoreIntegrityError(ValueError):
    """A processed store is incomplete, incompatible or corrupt."""


def content_hash(content: dict) -> str:
    """Canonical JSON identity; no timestamp or output-directory dependency."""
    return hashlib.sha256(
        json.dumps(
            content, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def array_shapes(events: int, particles: int) -> dict[str, tuple]:
    return {
        "particles": (particles, 3),
        "original_slots": (particles,),
        "offsets": (events + 1,),
        "event_aggregates": (events, 8),
        "event_features": (events, 8),
        **{
            name: (events,)
            for name in ARRAY_DTYPES
            if name
            not in (
                "particles",
                "original_slots",
                "offsets",
                "event_aggregates",
                "event_features",
            )
        },
    }


def verify_store(path: Path, *, chunk_rows: int = CHUNK_ROWS) -> dict:
    """Hash every artifact, validate schema and scan bounded structural metadata.

    Validation uses labels only for membership integrity, never model decisions.
    There is no raw-data or network dependency for this command.
    """
    path = Path(path)
    arrays = {}
    try:
        if not 1 <= chunk_rows <= MAX_BATCH_EVENTS:
            raise StoreIntegrityError("Verification chunk rows must be in [1,4096].")
        if path.is_symlink() or not path.is_dir():
            raise StoreIntegrityError("Expected a real processed-store directory.")
        manifest = json.loads((path / "manifest.json").read_text())
        if (
            manifest.get("schema_version") != SCHEMA_VERSION
            or manifest.get("complete") is not True
        ):
            raise StoreIntegrityError("Incomplete or unsupported processed schema.")
        science = manifest["scientific"]
        if content_hash(science) != manifest["scientific_sha256"]:
            raise StoreIntegrityError("Scientific manifest identity mismatch.")
        e, p = science["events"], science["particles"]
        expected_shapes = array_shapes(e, p)
        required = {f"{name}.npy" for name in ARRAY_DTYPES} | {"configuration.json"}
        if set(science["files"]) != required or {
            item.name for item in path.iterdir()
        } != required | {"manifest.json"}:
            raise StoreIntegrityError("Unexpected or missing store files.")
        for name, record in science["files"].items():
            file = path / name
            if (
                file.is_symlink()
                or not file.is_file()
                or file.stat().st_size != record["bytes"]
                or file_sha256(file) != record["sha256"]
            ):
                raise StoreIntegrityError(f"File integrity mismatch: {name}")
            if name.endswith(".npy"):
                key = name.removesuffix(".npy")
                array = np.load(file, mmap_mode="r", allow_pickle=False)
                if (
                    array.dtype.str != ARRAY_DTYPES[key]
                    or array.shape != expected_shapes[key]
                    or list(array.shape) != record["shape"]
                    or array.dtype.str != record["dtype"]
                ):
                    raise StoreIntegrityError(f"Shape/dtype mismatch: {name}")
                arrays[key] = array
        config = json.loads((path / "configuration.json").read_text())
        params = Parameters.from_config(config)
        if (
            science["canonical_channels"] != list(PHYSICAL_CHANNELS)
            or science["model_channels"] != list(OBJECT_CHANNELS)
            or science["aggregate_channels"] != list(AGGREGATE_NAMES)
            or science["default_nmax"] != params.nmax
            or content_hash(science["split_identity"])
            != science["split_identity_sha256"]
        ):
            raise StoreIntegrityError("Feature/split identity mismatch.")
        if (
            science["config_sha256"] != science["files"]["configuration.json"]["sha256"]
            or science["source_integrity"] != config["source_integrity"]
            or science["source"] != config["source"]
        ):
            raise StoreIntegrityError("Source/config provenance mismatch.")
        if science["scope"] not in ("dev", "full") or e < 1 or p < e:
            raise StoreIntegrityError("Invalid scope/cardinality.")
        offsets = arrays["offsets"]
        if (
            offsets[0] != 0
            or offsets[-1] != p
            or not np.array_equal(np.diff(offsets), arrays["multiplicities"])
            or (np.diff(offsets) <= 0).any()
            or (np.diff(offsets) > 700).any()
        ):
            raise StoreIntegrityError("Invalid canonical offsets/multiplicities.")
        ids = arrays["event_ids"]
        if (np.diff(ids) <= 0).any() or ids[0] < 0 or ids[-1] >= science["source_rows"]:
            raise StoreIntegrityError("Invalid/duplicate source event IDs.")
        codes, labels, dev = (
            arrays["split_codes"],
            arrays["labels"],
            arrays["development"],
        )
        if (
            not np.isin(codes, list(ROLES.values())).all()
            or not np.isin(labels, [0, 1]).all()
            or (labels[codes < 5] != 0).any()
            or (labels[codes == 5] != 1).any()
            or np.isin(codes[dev], [4, 5]).any()
        ):
            raise StoreIntegrityError("Split, label or development embargo violation.")
        counts = {name: int((codes == code).sum()) for name, code in ROLES.items()}
        if counts != science["counts"]:
            raise StoreIntegrityError("Manifest split counts mismatch.")
        for name, count in counts.items():
            expected = (
                config["split"]["counts"].get(f"dev_{name}", 0)
                if science["scope"] == "dev"
                else config["split"]["counts"][name]
            )
            if count != expected:
                raise StoreIntegrityError(f"Frozen membership count mismatch: {name}")
        if science["scope"] == "dev" and not dev.all():
            raise StoreIntegrityError("Dev scope contains non-dev events.")
        for name in (
            "train_background",
            "validation_selection_background",
            "validation_calibration_background",
        ):
            if (
                int((dev & (codes == ROLES[name])).sum())
                != config["split"]["counts"][f"dev_{name}"]
            ):
                raise StoreIntegrityError("Frozen dev-role count mismatch.")
        if len(np.unique(arrays["fingerprints"])) != e:
            raise StoreIntegrityError("Duplicate groups in canonical representatives.")
        for start in range(0, e, chunk_rows):
            stop = min(start + chunk_rows, e)
            left, right = int(offsets[start]), int(offsets[stop])
            physical = arrays["particles"][left:right]
            if (
                not np.isfinite(physical).all()
                or (physical[:, 0] <= 0).any()
                or (np.abs(physical[:, 2]) > np.pi + 2e-7).any()
            ):
                raise StoreIntegrityError("Invalid physical canonical particle.")
            increase = np.diff(physical[:, 0]) > 0
            increase[offsets[start + 1 : stop] - left - 1] = False
            if increase.any():
                raise StoreIntegrityError("Canonical pT order violation.")
            local = offsets[start : stop + 1] - left
            mask = np.arange(700)[None, :] < np.diff(local)[:, None]
            slots = np.full((stop - start, 700), 700, dtype=np.uint16)
            slots[mask] = arrays["original_slots"][left:right]
            ordered_slots = np.sort(slots, axis=1)
            duplicate = (ordered_slots[:, 1:] == ordered_slots[:, :-1]) & (
                ordered_slots[:, 1:] < 700
            )
            if duplicate.any() or (arrays["original_slots"][left:right] >= 700).any():
                raise StoreIntegrityError("Invalid original particle slots.")
            aggregates = arrays["event_aggregates"][start:stop]
            features = arrays["event_features"][start:stop]
            if (
                not np.isfinite(aggregates).all()
                or not np.isfinite(features).all()
                or not np.array_equal(aggregates[:, 0], np.diff(local))
                or not np.array_equal(
                    features, standardized_aggregates(aggregates, params)
                )
            ):
                raise StoreIntegrityError("Invalid physical/scaled aggregate fields.")
        return manifest
    except (OSError, KeyError, TypeError, ValueError, OverflowError) as exc:
        if isinstance(exc, StoreIntegrityError):
            raise
        raise StoreIntegrityError(f"Cannot verify processed store: {exc}") from exc
    finally:
        arrays.clear()


@dataclass
class EventBatch:
    """Owned bounded arrays: model features separated from truth and provenance."""

    particles: np.ndarray
    offsets: np.ndarray
    original_slots: np.ndarray
    event_ids: np.ndarray
    multiplicities: np.ndarray
    event_aggregates: np.ndarray
    event_features: np.ndarray
    split_codes: np.ndarray
    labels: np.ndarray | None
    parameters: Parameters

    def model_view(self, *, nmax: int | None = None) -> ModelView:
        return model_view(self.particles, self.offsets, self.parameters, nmax=nmax)


class ProcessedStore:
    """Verified mmap reader. Split names and test opt-in are mandatory."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.manifest = verify_store(self.path)
        self.parameters = Parameters.from_config(
            json.loads((self.path / "configuration.json").read_text())
        )
        self._arrays = {
            name: np.load(self.path / f"{name}.npy", mmap_mode="r", allow_pickle=False)
            for name in ARRAY_DTYPES
            if name != "labels"
        }

    def __enter__(self) -> "ProcessedStore":
        return self

    def __exit__(self, *_args) -> None:
        self.close()

    def close(self) -> None:
        """Release mappings; returned batches own their data independently."""
        self._arrays.clear()

    def _positions(self, split: str, *, allow_test: bool, dev_only: bool) -> np.ndarray:
        if not self._arrays:
            raise ValueError("Reader is closed.")
        if split not in ROLES:
            raise ValueError(f"Choose one explicit split: {', '.join(ROLES)}")
        if split.startswith("test_") and not allow_test:
            raise ValueError("Test embargo: evaluation requires allow_test=True.")
        selected = self._arrays["split_codes"] == ROLES[split]
        if dev_only:
            selected &= self._arrays["development"]
        return np.flatnonzero(selected)

    def event_ids(
        self, split: str, *, allow_test: bool = False, dev_only: bool = False
    ) -> np.ndarray:
        positions = self._positions(split, allow_test=allow_test, dev_only=dev_only)
        return np.array(self._arrays["event_ids"][positions])

    def _batch(self, positions: np.ndarray, *, include_labels: bool) -> EventBatch:
        if len(positions) > MAX_BATCH_EVENTS:
            raise ValueError(
                f"Read at most {MAX_BATCH_EVENTS} events; use iter_batches."
            )
        source_offsets = self._arrays["offsets"]
        counts = self._arrays["multiplicities"][positions]
        offsets = np.r_[0, np.cumsum(counts, dtype=np.int64)]
        flat = np.repeat(source_offsets[positions] - offsets[:-1], counts) + np.arange(
            offsets[-1]
        )
        labels = None
        if include_labels:
            labels = np.array(
                np.load(self.path / "labels.npy", mmap_mode="r", allow_pickle=False)[
                    positions
                ]
            )
        return EventBatch(
            self._arrays["particles"][flat],
            offsets,
            self._arrays["original_slots"][flat],
            self._arrays["event_ids"][positions],
            counts,
            self._arrays["event_aggregates"][positions],
            self._arrays["event_features"][positions],
            self._arrays["split_codes"][positions],
            labels,
            self.parameters,
        )

    @staticmethod
    def _label_permission(split: str, allow_test: bool, include_labels: bool) -> None:
        if include_labels and (not allow_test or not split.startswith("test_")):
            raise ValueError(
                "Truth is evaluation-only: explicit test split and allow_test=True required."
            )

    def read(
        self,
        split: str,
        selection: slice | np.ndarray,
        *,
        allow_test: bool = False,
        include_labels: bool = False,
        dev_only: bool = False,
    ) -> EventBatch:
        """Selection indexes the requested split, not global/source event ordinals."""
        positions = self._positions(split, allow_test=allow_test, dev_only=dev_only)
        self._label_permission(split, allow_test, include_labels)
        selected = np.asarray(positions[selection], dtype=np.int64)
        if selected.ndim != 1:
            raise ValueError("Choose a slice or one-dimensional index array.")
        return self._batch(selected, include_labels=include_labels)

    def read_ids(
        self,
        split: str,
        event_ids: np.ndarray,
        *,
        allow_test: bool = False,
        include_labels: bool = False,
        dev_only: bool = False,
    ) -> EventBatch:
        """Resolve explicit source row ordinals within one permitted split."""
        self._positions(split, allow_test=allow_test, dev_only=dev_only)
        self._label_permission(split, allow_test, include_labels)
        ids = np.asarray(event_ids)
        if ids.ndim != 1 or ids.dtype.kind not in "iu":
            raise ValueError("Expected one-dimensional integer source event IDs.")
        positions = np.searchsorted(self._arrays["event_ids"], ids)
        if (positions >= len(self._arrays["event_ids"])).any() or not np.array_equal(
            self._arrays["event_ids"][positions], ids
        ):
            raise ValueError("Requested source event is absent.")
        if (self._arrays["split_codes"][positions] != ROLES[split]).any() or (
            dev_only and not self._arrays["development"][positions].all()
        ):
            raise ValueError("Requested event is outside the permitted split/subset.")
        return self._batch(positions, include_labels=include_labels)

    def iter_batches(
        self,
        split: str,
        *,
        batch_size: int = 256,
        allow_test: bool = False,
        include_labels: bool = False,
        dev_only: bool = False,
    ) -> Iterator[EventBatch]:
        """Filter membership once, then yield bounded owned batches."""
        if not 1 <= batch_size <= MAX_BATCH_EVENTS:
            raise ValueError("Invalid batch size.")
        self._label_permission(split, allow_test, include_labels)
        positions = self._positions(split, allow_test=allow_test, dev_only=dev_only)
        for start in range(0, len(positions), batch_size):
            yield self._batch(
                positions[start : start + batch_size], include_labels=include_labels
            )
