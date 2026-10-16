"""Role-separated orchestration shared by typed generated and real studies."""

import json
import os
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import h5py
import numpy as np

from . import data
from .models import STREAMS, fit_analytical, load_model, save_model, score_rows, train
from .statistics import calibration

REAL_COUNTS = dict(
    train=200000,
    selection=50000,
    calibration=1000000,
    final_background=1000000,
    A_to_4l=40000,
    LQ_to_btau=40000,
)
SOURCES = ("background", "A_to_4l", "LQ_to_btau")
MEMBERSHIP = np.dtype([("source_row", "<i8"), ("fingerprint", "u1", (32,))])


class Study:
    """Real paths/counts are immutable; tiny generated counts cannot be permits."""

    def __init__(self, root, models, scope, counts=None):
        self.root, self.models = Path(root).resolve(), Path(models).resolve()
        self.scope = scope
        if scope == "Task0061-real-ADC-preparation-only":
            if counts is not None:
                raise PermissionError("real role counts cannot be overridden")
            self.counts = REAL_COUNTS.copy()
        elif scope == "generated-ADC-test-only":
            if counts is None or max(counts.values()) > 256:
                raise PermissionError("bounded generated role counts required")
            self.counts = counts.copy()
        else:
            raise PermissionError("unknown study scope")

    def event(self, event, **values):
        record = dict(event=event, scope=self.scope, **values)
        target = self.root / "ledger/events.jsonl"
        with target.open("a") as stream:
            stream.write(json.dumps(record, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    def role(self, name, phase):
        allowed = {
            "train": {"train", "selection", "development"},
            "calibrate": {"calibration", "development"},
            "freeze": {"development"},
        }
        if name not in allowed.get(phase, set()):
            raise PermissionError(f"{phase} cannot open role {name}")
        directory = self.root / "prepared" / name
        manifest = json.loads((directory / "manifest.json").read_text())
        if manifest["role"] != name or manifest["scope"] != self.scope:
            raise PermissionError("role manifest scope mismatch")
        if data.digest(self.root / "private/scaler.json") != manifest["scaler_sha256"]:
            raise ValueError("scaler identity mismatch")
        for filename, digest in manifest["files"].items():
            if data.digest(directory / filename) != digest:
                raise ValueError("role content mismatch")
        return np.load(directory / "features.npy", mmap_mode="r", allow_pickle=False)


def install_phase_guard(study, phase):
    """Supplement explicit loaders; not an OS sandbox over native HDF calls."""
    allowed = {
        "train": {"train", "selection", "development"},
        "calibrate": {"calibration", "development"},
        "freeze": {"development"},
    }[phase]

    def guard(event, args):
        if event == "sqlite3.connect":
            raise PermissionError("all-role group database denied outside preparation")
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if path.is_relative_to(study.root / "private") and (
            path.suffix == ".sqlite" or (phase == "train" and path.suffix == ".npy")
        ):
            raise PermissionError("private non-training population payload denied")
        if path.is_relative_to(study.root / "raw"):
            raise PermissionError("all-role raw payload denied")
        if path.is_relative_to(study.root / "prepared"):
            relative = path.relative_to(study.root / "prepared")
            if relative.parts[0] not in allowed:
                raise PermissionError("protected role payload denied")
        # Also deny all unrelated/historical data/model roots. Runtime/code are read-only.
        repo = Path(__file__).resolve().parents[4]
        for sensitive, own in (
            (repo / "data", study.root),
            (repo / "artifacts", study.models),
        ):
            if path.is_relative_to(sensitive) and not path.is_relative_to(own):
                raise PermissionError("unrelated scientific payload denied")

    sys.addaudithook(guard)


def prepare(study, sources):
    """Validate all sources, exact-group, then gather physically separated roles."""
    if tuple(sources) != SOURCES:
        raise ValueError("exactly three declared labeled sources in order")
    reports = {}
    database = study.root / "private/groups-v2.sqlite"
    if database.exists():
        raise FileExistsError("preserve existing preparation")
    connection = sqlite3.connect(database)
    try:
        connection.executescript(
            "PRAGMA temp_store=FILE; PRAGMA cache_size=-32768; CREATE TABLE groups(fp BLOB PRIMARY KEY, source INTEGER, ordinal INTEGER, ordering BLOB, conflict INTEGER DEFAULT 0) WITHOUT ROWID;"
        )
        for source_id, (name, path) in enumerate(sources.items()):
            header = data.inspect_header(path)
            counts, bad, eligible = Counter(), 0, 0
            study.event("source_header_accepted", source=name, **header)
            with h5py.File(path, "r") as handle:
                ds = handle["Particles"]
                for start in range(0, len(ds), data.CHUNK):
                    objects = np.asarray(
                        ds[start : start + data.CHUNK], dtype=np.float64
                    )
                    good, failures = data.row_rules(objects)
                    counts.update(failures)
                    bad += int((~good).sum())
                    eligible += int(good.sum())
                    records = []
                    for offset, fp in zip(
                        np.flatnonzero(good),
                        data.fingerprints(objects[good]),
                        strict=True,
                    ):
                        records.append(
                            (fp, source_id, start + int(offset), data.split_key(fp))
                        )
                    connection.executemany(
                        "INSERT INTO groups(fp,source,ordinal,ordering) VALUES(?,?,?,?) ON CONFLICT(fp) DO UPDATE SET conflict=MAX(conflict,groups.source!=excluded.source)",
                        records,
                    )
                    connection.commit()
                    study.event(
                        "structural_chunk",
                        source=name,
                        start=start,
                        rows=len(objects),
                        eligible=int(good.sum()),
                        quarantined=int((~good).sum()),
                    )
            unique = connection.execute(
                "SELECT COUNT(*) FROM groups WHERE source=?", (source_id,)
            ).fetchone()[0]
            reports[name] = dict(
                **header,
                eligible_rows=eligible,
                quarantined_rows=bad,
                quarantine_fraction=bad / header["rows"],
                rule_failures=dict(counts),
                unique_groups=unique,
                duplicate_rows=eligible - unique,
            )
            data.write_json(
                study.root / "private" / f"structure-{name}.json", reports[name]
            )
            if bad / header["rows"] > 0.01:
                raise ValueError(f"source-invalid: {name} quarantine exceeds1%")
        conflicts = connection.execute(
            "SELECT COUNT(*) FROM groups WHERE conflict!=0"
        ).fetchone()[0]
        if conflicts:
            raise ValueError(f"source-invalid: {conflicts} cross-label conflict groups")
        if (
            sum(v["quarantined_rows"] for v in reports.values())
            / sum(v["rows"] for v in reports.values())
            > 0.01
        ):
            raise ValueError("pooled quarantine exceeds1%")
        for name, needed in (
            (
                "background",
                sum(
                    study.counts[r]
                    for r in ("train", "selection", "calibration", "final_background")
                ),
            ),
            ("A_to_4l", study.counts["A_to_4l"]),
            ("LQ_to_btau", study.counts["LQ_to_btau"]),
        ):
            if reports[name]["unique_groups"] < needed:
                raise ValueError(f"source-invalid: insufficient unique groups {name}")
        connection.execute("CREATE INDEX role_order ON groups(source,ordering,fp)")
        connection.commit()
        data.write_json(study.root / "private/structure.json", reports)
        offsets = Counter()
        role_records = {}
        for role, count in study.counts.items():
            name = (
                "background"
                if role in ("train", "selection", "calibration", "final_background")
                else role
            )
            source_id = SOURCES.index(name)
            directory = study.root / "prepared" / role
            directory.mkdir()
            membership = np.lib.format.open_memmap(
                directory / "membership.npy",
                mode="w+",
                dtype=MEMBERSHIP,
                shape=(count,),
            )
            cursor = connection.execute(
                "SELECT ordinal,fp FROM groups WHERE source=? ORDER BY ordering,fp LIMIT ? OFFSET ?",
                (source_id, count, offsets[name]),
            )
            for i, (ordinal, fp) in enumerate(cursor):
                membership[i] = (ordinal, np.frombuffer(fp, dtype=np.uint8))
            membership.flush()
            offsets[name] += count
            objects = np.lib.format.open_memmap(
                directory / "objects.npy",
                mode="w+",
                dtype=np.float64,
                shape=(count, 19, 4),
            )
            data.gather(sources[name], membership["source_row"], objects)
            raw_features = np.lib.format.open_memmap(
                directory / "features64.npy",
                mode="w+",
                dtype=np.float64,
                shape=(count, 12),
            )
            for start in range(0, count, data.CHUNK):
                raw_features[start : start + data.CHUNK] = data.features(
                    objects[start : start + data.CHUNK]
                )
            raw_features.flush()
            if role == "train":
                scaler = data.fit_scaler(raw_features)
                data.write_json(study.root / "private/scaler.json", scaler)
            features = np.lib.format.open_memmap(
                directory / "features.npy",
                mode="w+",
                dtype=np.float32,
                shape=(count, 12),
            )
            for start in range(0, count, data.CHUNK):
                features[start : start + data.CHUNK] = data.transform(
                    raw_features[start : start + data.CHUNK], scaler
                )
            features.flush()
            role_records[role] = role_manifest(study, role, name, count)
            study.event(
                "role_sealed",
                role=role,
                rows=count,
                manifest_sha256=data.digest(directory / "manifest.json"),
            )
            del membership, objects, raw_features, features
        # The CPU/symmetry sample is fixed before any scoring, in hash role order.
        development_count = min(4096, study.counts["train"])
        directory = study.root / "prepared/development"
        directory.mkdir()
        for filename in ("objects.npy", "features.npy", "membership.npy"):
            array = np.load(
                study.root / "prepared/train" / filename,
                mmap_mode="r",
                allow_pickle=False,
            )
            np.save(
                directory / filename,
                np.array(array[:development_count], copy=True),
                allow_pickle=False,
            )
        role_records["development"] = role_manifest(
            study, "development", "train-first-hash-ordered", development_count
        )
        data.write_json(study.root / "private/roles.json", role_records)
        return reports
    finally:
        connection.close()


def role_manifest(study, role, source, count):
    directory = study.root / "prepared" / role
    filenames = ("objects.npy", "features.npy", "membership.npy")
    if (directory / "features64.npy").exists():
        filenames += ("features64.npy",)
    record = dict(
        schema_version=2,
        scope=study.scope,
        role=role,
        source=source,
        rows=count,
        scaler_sha256=data.digest(study.root / "private/scaler.json"),
        files={name: data.digest(directory / name) for name in filenames},
    )
    data.write_json(directory / "manifest.json", record)
    for filename in filenames:
        (directory / filename).chmod(0o444)
    return record


def fit_stream(study, arm, seed, generated_options=None):
    if generated_options and study.scope != "generated-ADC-test-only":
        raise PermissionError("no real training overrides")
    training = study.role("train", "train")
    selection = study.role("selection", "train")
    if arm.endswith("AE"):
        model, history = train(
            arm,
            int(seed),
            training,
            selection,
            study.event,
            **(generated_options or {}),
        )
    else:
        study.event("analytical_fit_started", arm=arm, rows=len(training))
        model = fit_analytical(arm, training)
        history = dict(
            schema_version=2,
            arm=arm,
            training_rows=len(training),
            stop_reason="analytical_complete",
        )
    directory = study.models / arm / str(seed)
    record = save_model(directory, arm, seed, model, history)
    reloaded = load_model(directory)
    development = study.role("development", "train")
    original = score_rows(model, development)
    repeat = score_rows(model, development)
    restored = score_rows(reloaded, development)
    if not np.array_equal(original, repeat) or not np.array_equal(original, restored):
        raise ValueError("B32 reload/repeat mismatch")
    np.save(directory / "development_scores.npy", original, allow_pickle=False)
    data.write_json(
        directory / "development-check.json",
        dict(
            rows=len(development),
            public_score_rows=3 * len(development),
            public_calls=3 * ((len(development) + 31) // 32),
            repeat_bitwise=True,
            reload_bitwise=True,
        ),
    )
    study.event(
        "model_frozen",
        arm=arm,
        seed=str(seed),
        model_sha256=data.digest(directory / "model.json"),
    )
    return record


def fit_matrix_manifest(study):
    streams = []
    for arm, seed in STREAMS:
        directory = study.models / arm / seed
        load_model(directory)
        streams.append(
            dict(
                arm=arm,
                seed=seed,
                model_sha256=data.digest(directory / "model.json"),
                history_sha256=data.digest(directory / "history.json"),
                weights_sha256=data.digest(directory / "weights.npz"),
            )
        )
    for seed in (1729, 1730, 1731):
        left, right = [
            json.loads((study.models / arm / str(seed) / "history.json").read_text())[
                "history"
            ]
            for arm in ("compactAE", "referenceAE")
        ]
        if any(
            a["order_sha256"] != b["order_sha256"]
            for a, b in zip(left, right, strict=False)
        ):
            raise ValueError("paired sampler order mismatch")
    return dict(
        schema_version=2,
        streams=streams,
        scaler_sha256=data.digest(study.root / "private/scaler.json"),
    )


def calibrate(study):
    matrix = fit_matrix_manifest(study)
    data.write_json(study.root / "private/precalibration-matrix.json", matrix)
    values = study.role("calibration", "calibrate")
    cuts = []
    for arm, seed in STREAMS:
        model = load_model(study.models / arm / seed)
        target = study.root / "private" / f"calibration-{arm}-{seed}.npy"
        output = np.lib.format.open_memmap(
            target, mode="w+", dtype=np.float64, shape=(len(values),)
        )
        study.event("calibration_stream_started", arm=arm, seed=seed, rows=len(values))
        for start in range(0, len(values), data.CHUNK):
            size = min(data.CHUNK, len(values) - start)
            study.event(
                "calibration_chunk_started",
                arm=arm,
                seed=seed,
                start=start,
                rows=size,
                completed_calls=start // 32,
            )
            score_rows(
                model, values[start : start + size], out=output[start : start + size]
            )
            output.flush()
            study.event(
                "calibration_chunk_completed",
                arm=arm,
                seed=seed,
                completed_rows=start + size,
                completed_calls=(start + size + 31) // 32,
            )
        output.flush()
        for alpha in (0.01, 0.001):
            cuts.append(
                dict(
                    arm=arm,
                    seed=seed,
                    score_sha256=data.digest(target),
                    **calibration(output, alpha),
                )
            )
        study.event(
            "calibration_stream_completed",
            arm=arm,
            seed=seed,
            score_rows=len(values),
            public_calls=(len(values) + 31) // 32,
        )
    data.write_json(study.root / "private/calibration.json", cuts)
    return cuts


def symmetry(study):
    scaler = json.loads((study.root / "private/scaler.json").read_text())
    study.role("development", "freeze")
    directory = study.root / "prepared/development"
    objects = np.array(
        np.load(directory / "objects.npy", mmap_mode="r", allow_pickle=False)[:512],
        copy=True,
    )
    base = data.transform(data.features(objects), scaler)
    cuts = json.loads((study.root / "private/calibration.json").read_text())
    reports = []
    for name in ("rotation", "beam_reflection"):
        transformed = objects.copy()
        if name == "rotation":
            present = transformed[:, :, 3] != 0
            transformed[:, :, 2] = np.where(
                present, data.wrap(transformed[:, :, 2] + 0.7), 0.0
            )
        else:
            transformed[:, :, 1] *= -1
        f0, f1 = data.features(objects), data.features(transformed)
        scaled = data.transform(f1, scaler)
        if not np.allclose(f0, f1, atol=1e-5, rtol=1e-5) or not np.allclose(
            base, scaled, atol=1e-5, rtol=1e-5
        ):
            raise ValueError("required aggregate/scaled identity failed")
        for arm, seed in STREAMS:
            model = load_model(study.models / arm / seed)
            before, after = score_rows(model, base), score_rows(model, scaled)
            error = np.abs(before - after)
            tolerance = 1e-5 + 2e-5 * np.maximum(1.0, np.abs(before))
            if np.any(error > tolerance):
                raise ValueError("required score identity failed")
            margins = []
            for cut in [c for c in cuts if c["arm"] == arm and c["seed"] == seed]:
                threshold = cut["threshold"]
                margins.append(
                    dict(
                        alpha=cut["alpha"],
                        decision_changes=int(
                            np.count_nonzero(
                                (before > threshold) != (after > threshold)
                            )
                        ),
                        before=(before - threshold).tolist(),
                        after=(after - threshold).tolist(),
                    )
                )
            reports.append(
                dict(
                    transformation=name,
                    arm=arm,
                    seed=seed,
                    rows=len(objects),
                    max_feature_error=float(np.max(np.abs(f0 - f1))),
                    max_scaled_error=float(np.max(np.abs(base - scaled))),
                    max_score_error=float(error.max()),
                    margins=margins,
                    public_score_rows=2 * len(objects),
                    public_calls=2 * ((len(objects) + 31) // 32),
                )
            )
    data.write_json(study.root / "private/development-symmetry.json", reports)
    return reports
