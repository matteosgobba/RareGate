"""ADC schema2: bounded structural validation and invariant aggregates.

Units and slot/type semantics are pinned to the publisher descriptor, pp3-4.
No outcome summaries are produced by this module.
"""

import ast
import hashlib
import json
import os
from pathlib import Path

import h5py
import numpy as np

CLASSES = ((1, 0, 1), (2, 1, 5), (3, 5, 9), (4, 9, 19))
CHUNK = 8192


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def write_json(path, value):
    path = Path(path)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def decoded(dataset):
    if dataset.size > 128 or dataset.id.get_storage_size() > 16384:
        raise ValueError("metadata size")
    result = []
    for item in np.asarray(dataset[()]).reshape(-1):
        value = item.decode("utf-8") if isinstance(item, bytes) else str(item)
        if len(value.encode()) > 16384:
            raise ValueError("metadata string size")
        result.append(value)
    if len(result) == 1:
        text = result[0].strip()
        if text.startswith(("[", "(", "{")):
            return ast.literal_eval(text)
    return result


def metadata_mapping(classes, names):
    aliases = {"met": 1, "electron": 2, "muon": 3, "jet": 4, "padding": 0}
    if isinstance(classes, dict):
        mapping = {str(k).strip().lower(): int(v) for k, v in classes.items()}
    else:
        classes = [str(v).strip().lower() for v in classes]
        publisher = {
            "met_class_1": "met",
            "four_ele_class_2": "electron",
            "four_mu_class_3": "muon",
            "ten_jet_class_4": "jet",
        }
        classes = [publisher.get(value, value) for value in classes]
        start = 0 if classes and classes[0] == "padding" else 1
        mapping = {name: i + start for i, name in enumerate(classes)}
    expected = {k: v for k, v in aliases.items() if k != "padding"}
    if mapping not in (expected, aliases):
        raise ValueError("contradictory class mapping")
    names = [str(v).strip().lower() for v in names]
    if names[:3] != ["pt", "eta", "phi"] or len(names) not in (3, 4):
        raise ValueError("contradictory coordinate names")
    if len(names) == 4 and names[3] not in (
        "type",
        "type_id",
        "particle_type",
        "class",
        "class_id",
        "id",
    ):
        raise ValueError("contradictory type name")
    return dict(classes=mapping, names=names, units="GeV/radians per descriptor")


def inspect_header(path):
    with h5py.File(path, "r") as handle:
        keys = set(handle)
        classes = keys & {"Particles_Classes", "Particle_Classes"}
        if not classes or not {"Particles", "Particles_Names"} <= keys:
            raise ValueError("required schema metadata missing")
        if keys - {"Particles", "Particles_Names", *classes}:
            raise ValueError("unexpected HDF dataset")
        for key in keys:
            if not isinstance(handle.get(key, getlink=True), h5py.HardLink):
                raise ValueError("external/soft HDF link")
            ds = handle[key]
            if not isinstance(ds, h5py.Dataset) or ds.is_virtual or ds.external:
                raise ValueError("indirect HDF storage")
            for i in range(ds.id.get_create_plist().get_nfilters()):
                if ds.id.get_create_plist().get_filter(i)[0] not in (1, 2, 3):
                    raise ValueError("unapproved HDF filter")
        data = handle["Particles"]
        if (
            data.ndim != 3
            or data.shape[1:] != (19, 4)
            or not 0 < data.shape[0] <= 15000000
            or data.dtype.kind != "f"
            or data.dtype.itemsize not in (4, 8)
        ):
            raise ValueError("Particles shape/dtype/count")
        mappings = [
            metadata_mapping(decoded(handle[k]), decoded(handle["Particles_Names"]))
            for k in sorted(classes)
        ]
        if any(value != mappings[0] for value in mappings):
            raise ValueError("class-key spellings disagree")
        return dict(
            rows=data.shape[0],
            shape=list(data.shape),
            dtype=str(data.dtype),
            chunks=data.chunks,
            compression=data.compression,
            mapping=mappings[0],
            class_keys=sorted(classes),
        )


def row_rules(objects):
    x = np.asarray(objects, dtype=np.float64)
    if x.ndim != 3 or x.shape[1:] != (19, 4) or len(x) > CHUNK:
        raise ValueError("bounded [N,19,4] required")
    pt, eta, types = x[:, :, 0], x[:, :, 1], x[:, :, 3]
    rules = {
        "nonfinite": ~np.isfinite(x).all(axis=(1, 2)),
        "padding": ((types == 0) & (x != 0).any(axis=2)).any(axis=1),
        "MET": (types[:, 0] != 1) | (pt[:, 0] < 0) | (eta[:, 0] != 0),
    }
    preselection = np.zeros(len(x), dtype=bool)
    for kind, begin, end in CLASSES[1:]:
        t, p, e = types[:, begin:end], pt[:, begin:end], eta[:, begin:end]
        present = t == kind
        cut, limit = {2: (3.0, 3.0), 3: (3.0, 2.1), 4: (15.0, 4.0)}[kind]
        rules[f"class_{kind}"] = ((t != 0) & ~present).any(axis=1)
        rules[f"cuts_{kind}"] = (
            present & ((p < cut - 1e-5) | (p <= 0) | (np.abs(e) >= limit))
        ).any(axis=1)
        rules[f"prefix_order_{kind}"] = (
            (present[:, 1:] & ~present[:, :-1]) | (p[:, 1:] > p[:, :-1])
        ).any(axis=1)
        if kind in (2, 3):
            preselection |= (present & (p >= 23.0 - 1e-5) & (np.abs(e) < limit)).any(
                axis=1
            )
    rules["lepton_filter"] = ~preselection
    bad = np.logical_or.reduce(list(rules.values()))
    return ~bad, {name: int(value.sum()) for name, value in rules.items()}


def wrap(phi):
    phi = np.asarray(phi, dtype=np.float64)
    return np.where(
        (phi >= -np.pi) & (phi < np.pi), phi, (phi + np.pi) % (2 * np.pi) - np.pi
    )


def fingerprint(event):
    event = np.asarray(event, dtype=np.float64).copy()
    event[:, 2] = wrap(event[:, 2])
    event[event == 0] = 0.0
    value = hashlib.sha256(b"adc-exact-content-v2\0")
    for kind, _, _ in CLASSES:
        coordinates = event[event[:, 3] == kind, :3]
        coordinates = coordinates[
            np.lexsort((coordinates[:, 2], coordinates[:, 1], coordinates[:, 0]))
        ]
        value.update(np.asarray([kind, len(coordinates)], dtype="<f8").tobytes())
        value.update(np.asarray(coordinates, dtype="<f8").tobytes())
    return value.digest()


def split_key(fp):
    return hashlib.sha256(f"adc-split-v2|1729|{fp.hex()}".encode()).digest()


def fingerprints(objects):
    """Same canonical bytes, bounded vectorized class sorting before hashing.

    Input rows have already passed the slot/padding/pT structural rules. Positive
    visible pT places zero padding first in an ascending lexicographic sort.
    """
    x = np.array(objects, dtype=np.float64, copy=True)
    if x.ndim != 3 or x.shape[1:] != (19, 4) or len(x) > CHUNK:
        raise ValueError("bounded fingerprint chunk")
    x[:, :, 2] = wrap(x[:, :, 2])
    x[x == 0] = 0.0
    blocks = []
    for kind, begin, end in CLASSES:
        coords = x[:, begin:end, :3]
        order = np.lexsort((coords[:, :, 2], coords[:, :, 1], coords[:, :, 0]), axis=1)
        canonical = np.ascontiguousarray(
            np.take_along_axis(coords, order[:, :, None], axis=1), dtype="<f8"
        )
        counts = (x[:, begin:end, 3] == kind).sum(axis=1)
        headers = [
            np.asarray([kind, count], dtype="<f8").tobytes()
            for count in range(end - begin + 1)
        ]
        blocks.append((canonical, counts, headers))
    result = []
    for i in range(len(x)):
        value = hashlib.sha256(b"adc-exact-content-v2\0")
        for coords, counts, headers in blocks:
            count = int(counts[i])
            value.update(headers[count])
            if count:
                value.update(memoryview(coords[i, -count:]).cast("B"))
        result.append(value.digest())
    return result


def features(objects):
    x = np.asarray(objects, dtype=np.float64)
    if (
        x.ndim != 3
        or x.shape[1:] != (19, 4)
        or len(x) > CHUNK
        or not np.isfinite(x).all()
    ):
        raise ValueError("bounded finite objects required")
    result = np.zeros((len(x), 12), dtype=np.float64)
    result[:, 0] = np.log1p(x[:, 0, 0])
    for j, kind in enumerate((2, 3, 4)):
        mask = x[:, :, 3] == kind
        pts = np.where(mask, x[:, :, 0], 0.0)
        result[:, 1 + j] = mask.sum(axis=1)
        result[:, 4 + j] = np.log1p(pts.sum(axis=1))
        result[:, 7 + j] = np.log1p(pts.max(axis=1))
    visible = x[:, :, 3] >= 2
    pt = np.where(visible, x[:, :, 0], 0.0)
    phi = wrap(x[:, :, 2])
    total = pt.sum(axis=1)
    result[:, 10] = np.divide(
        np.hypot((pt * np.cos(phi)).sum(axis=1), (pt * np.sin(phi)).sum(axis=1)),
        total,
        out=np.zeros(len(x)),
        where=total != 0,
    )
    mass2 = np.zeros(len(x))
    for i in range(1, 9):
        for j in range(i + 1, 9):
            mask = np.isin(x[:, i, 3], (2, 3)) & np.isin(x[:, j, 3], (2, 3))
            mass2 += np.where(
                mask,
                2
                * x[:, i, 0]
                * x[:, j, 0]
                * (np.cosh(x[:, i, 1] - x[:, j, 1]) - np.cos(phi[:, i] - phi[:, j])),
                0.0,
            )
    result[:, 11] = np.log1p(np.sqrt(np.maximum(mass2, 0.0)))
    if not np.isfinite(result).all():
        raise ValueError("nonfinite aggregate")
    return result


def fit_scaler(training_features):
    x = np.asarray(training_features, dtype=np.float64)
    mean, std = x.mean(axis=0), x.std(axis=0, ddof=0)
    if not np.isfinite(x).all() or np.any(std <= 1e-12):
        raise ValueError("invalid training scaler")
    return dict(
        schema_version=2,
        representation="adc-invariant-aggregates-v2",
        mean=mean.tolist(),
        std=std.tolist(),
        training_rows=len(x),
    )


def transform(x, scaler):
    result = np.asarray(
        (np.asarray(x, dtype=np.float64) - scaler["mean"]) / scaler["std"],
        dtype=np.float32,
    )
    if not np.isfinite(result).all():
        raise ValueError("nonfinite standardized features")
    return np.ascontiguousarray(result)


def gather(source, source_rows, output):
    """One sequential HDF pass; scatter only requested rows in role order."""
    indices = np.argsort(source_rows, kind="stable")
    ordered = np.asarray(source_rows)[indices]
    with h5py.File(source, "r") as handle:
        ds = handle["Particles"]
        for start in range(0, len(ds), CHUNK):
            low, high = np.searchsorted(ordered, (start, min(start + CHUNK, len(ds))))
            if high > low:
                block = np.asarray(ds[start : start + CHUNK], dtype=np.float64)
                output[indices[low:high]] = block[ordered[low:high] - start]
    output.flush()
