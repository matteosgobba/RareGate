"""Verify LHCO and inspect metadata plus 32 fixed rows; never perform physics EDA."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import h5py
import hdf5plugin  # Import registers the source's Blosc decoder with h5py.
import numpy as np

from latenttrigger.data.acquisition import AcquisitionError, acquire
from latenttrigger.data.metadata import LHCO_RD


def audit_file(path: Path) -> dict[str, object]:
    """Inspect a previously verified artifact using a fixed, class-agnostic sample."""
    datasets: dict[str, object] = {}
    with h5py.File(path, "r") as file:

        def describe(name: str, obj: h5py.Group | h5py.Dataset) -> None:
            if isinstance(obj, h5py.Dataset):
                properties = obj.id.get_create_plist()
                filters = []
                for i in range(properties.get_nfilters()):
                    identifier, flags, parameters, label = properties.get_filter(i)
                    filters.append(
                        {
                            "id": identifier,
                            "flags": flags,
                            "parameters": list(parameters),
                            "name": label.decode(),
                        }
                    )
                datasets[name] = {
                    "shape": list(obj.shape),
                    "dtype": str(obj.dtype),
                    "chunks": list(obj.chunks) if obj.chunks else None,
                    "filters": filters,
                }

        file.visititems(describe)
        values = file["df/block0_values"]
        if values.shape != (1_100_000, 2101) or values.dtype != np.dtype("float64"):
            raise AcquisitionError(
                "Raw shape/dtype differs from the audited v5 schema."
            )
        columns_ok = np.array_equal(file["df/axis0"][:], np.arange(2101))
        columns_ok &= np.array_equal(file["df/block0_items"][:], np.arange(2101))
        if not columns_ok or file["df/axis1"].shape != (1_100_000,):
            raise AcquisitionError("Unexpected raw axes/column mapping.")
        positions = np.linspace(0, values.shape[0] - 1, 32, dtype=np.int64)
        rows = np.stack([values[int(i), :] for i in positions])
        source_indexes = np.array([file["df/axis1"][int(i)] for i in positions])
        particles = rows[:, :2100].reshape(32, 700, 3)
        pt = particles[:, :, 0]
        padding = pt == 0
        valid = pt > 0
        counts = valid.sum(axis=1)
        checks = {
            "nan_values": int(np.isnan(rows).sum()),
            "infinite_values": int(np.isinf(rows).sum()),
            "negative_pt_slots": int((pt < 0).sum()),
            "nonzero_angles_in_zero_pt_slots": int(
                (padding & np.any(particles[:, :, 1:] != 0, axis=2)).sum()
            ),
            "valid_slots_after_padding": int(
                (valid & (np.cumsum(padding, axis=1) > 0)).sum()
            ),
            "empty_rows": int((counts == 0).sum()),
            "unexpected_labels": int((~np.isin(rows[:, 2100], [0, 1])).sum()),
        }
        result = {
            "audit_version": "lhco-raw-audit-v1",
            "groups": sorted(file.keys()),
            "datasets": datasets,
            "stored_attributes": {
                "pytables_format_version": file.attrs[
                    "PYTABLES_FORMAT_VERSION"
                ].decode(),
                "pandas_type": file["df"].attrs["pandas_type"].decode(),
                "pandas_version": file["df"].attrs["pandas_version"].decode(),
            },
            "uncompressed_values_bytes": values.nbytes,
            "sample": {
                "policy": "32 equally spaced row ordinals; class-agnostic integrity only",
                "row_ordinals": positions.tolist(),
                "source_indexes_match_row_ordinals": bool(
                    np.array_equal(source_indexes, positions)
                ),
                "label_values": np.unique(rows[:, 2100]).tolist(),
                "quality_counts": checks,
                "valid_particle_count": {
                    "minimum": int(counts.min()),
                    "maximum": int(counts.max()),
                    "mean": float(counts.mean()),
                },
                "zero_padding_slots": int(padding.sum()),
                "valid_phi_outside_minus_pi_pi": int(
                    (valid & (np.abs(particles[:, :, 2]) > np.pi)).sum()
                ),
                "raw_payload_bytes": rows.nbytes,
            },
            "bounded_quality_passed": not any(checks.values()),
        }
    return result


def main() -> int:
    """Save only aggregate structural findings beside ignored acquisition state."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, help="Data root containing raw/")
    args = parser.parse_args()
    try:
        acquisition = acquire(args.data_dir, verify_only=True)
        result = audit_file(acquisition.path)
        result["source_integrity"] = asdict(acquisition.integrity)
        result["source"] = asdict(LHCO_RD)
        result["local_file"] = acquisition.path.name
        result["reader_versions"] = {
            "h5py": h5py.__version__,
            "hdf5": h5py.version.hdf5_version,
            "hdf5plugin": hdf5plugin.version,
            "numpy": np.__version__,
        }
        output = acquisition.path.with_name("raw-schema-audit.json")
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        print(f"Local structural report: {output}")
        return 0 if result["bounded_quality_passed"] else 1
    except (AcquisitionError, OSError, KeyError) as error:
        print(f"Raw audit failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
