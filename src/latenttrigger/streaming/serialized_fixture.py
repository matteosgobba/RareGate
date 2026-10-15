"""0056 generated serialization fixture; no original artifacts or fitted parameters."""

import hashlib
import io
import json
from pathlib import Path

from . import quota
from .pilot_context import FixtureContext56, digest, fixture_rows
from .protocol import require


def prepare_sources(context, runtime, progress):
    from .session_context import SessionFixture57

    require(
        type(context) in (FixtureContext56, SessionFixture57),
        "Only serialized generated scope",
    )
    if type(context) is SessionFixture57:
        context.validate_location(Path(__file__).resolve().parents[3])
        if (Path(context.directory) / "fixture-spec.json").exists():
            spec = context.specification(Path(__file__).resolve().parents[3])
            return dict(
                generated=True,
                reused_serialized_sources=True,
                setup_raw_rows=0,
                setup_feature_calls=0,
                setup_feature_rows=0,
                creator_models=0,
                serialized_models=0,
                loader_models=1,
                setup_public_score_calls=0,
                optimizer_steps=0,
                HDF_files_opened=0,
                serialized_files=0,
                serialized_bytes=0,
                artifact_sha256=next(
                    e["sha256"]
                    for e in spec["allowed_files"]
                    if e["role"] == context.candidate + ":model"
                ),
            )
    np, core = runtime.np, runtime.core
    from latenttrigger.benchmarks.development_raw_adapter import construct
    from latenttrigger.data.features import (
        OBJECT_CHANNELS,
        PHYSICAL_CHANNELS,
        Parameters,
    )
    from latenttrigger.data.inspection import AGGREGATE_NAMES, LOG_AGGREGATES

    repo = Path(__file__).resolve().parents[3]
    directory = Path(context.directory)
    target = directory / "serialized"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    target.mkdir(mode=0o700)
    ledger = quota.CURRENT
    require(
        ledger.task == ("0057" if type(context) is SessionFixture57 else "0056")
        and str(ledger.root) == context.root,
        "Own fixture ledger",
    )
    entries = []

    def emit(role, value):
        name = role.split(":")[-1]
        path = target / (name + ".bin")
        if isinstance(value, np.ndarray):
            stream = io.BytesIO()
            np.save(stream, value, allow_pickle=False)
            blob = stream.getvalue()
        else:
            blob = (
                json.dumps(
                    value, sort_keys=True, separators=(",", ":"), allow_nan=False
                )
                + "\n"
            ).encode()
        ledger.write_bytes(path, blob)
        entry = dict(
            role=role,
            path=str(path.relative_to(repo)),
            bytes=len(blob),
            sha256=hashlib.sha256(blob).hexdigest(),
            format="generated",
        )
        entries.append(entry)
        return entry

    raw = emit(
        "raw",
        dict(generated_strict_dataset_standin=True, positions="0..63", no_HDF=True),
    )
    member = np.arange(6999, dtype="<i8")
    member_entry = emit("membership", member)
    selected_hash = hashlib.sha256(member[:1024].tobytes()).hexdigest()
    del member
    counts = dict(dev_train_background=6999)
    source = dict(sha256=raw["sha256"], file_size=raw["bytes"])
    split = dict(
        counts=counts,
        artifacts={"dev_train_background.npy": dict(sha256=member_entry["sha256"])},
        development_subset="artificial",
        protocol="fixture-only",
        seed=0,
        source_integrity=source,
    )
    config = dict(
        schema_version=1,
        preprocessing=dict(
            canonical=dict(
                channels=list(PHYSICAL_CHANNELS),
                dtype="float32",
                retain_all_particles=True,
            ),
            object_view=dict(
                channels=list(OBJECT_CHANNELS),
                dtype="float32",
                nmax=384,
                padding=0,
                pt_reference_GeV=1,
                pt_mean=0.0,
                pt_std=1.0,
                eta_mean=0.0,
                eta_std=1.0,
            ),
            aggregates=dict(
                channels=list(AGGREGATE_NAMES),
                log1p_indices=list(LOG_AGGREGATES),
                version=1,
                mean=[0.0] * 8,
                std=[1.0] * 8,
            ),
        ),
        split={
            k: split[k] for k in ("counts", "development_subset", "protocol", "seed")
        },
        analysis_provenance=dict(
            split_array_sha256={"dev_train_background.npy": member_entry["sha256"]}
        ),
        source_integrity=source,
    )
    transform = emit("transform", config)
    emit("dev_configuration", config)
    parameters = Parameters.from_config(config)
    golden = np.zeros((1024, 8), dtype="<f4")
    # Independent prior golden setup:64 separate1row feature constructions; no score.
    for p in range(64):
        progress()
        golden[p] = construct(fixture_rows([p]), parameters)[0]
    gold = emit("golden", golden)
    gold_hash = hashlib.sha256(golden.tobytes()).hexdigest()
    del golden
    emit("split_manifest", split)
    split_identity = dict(
        array_sha256={"dev_train_background.npy": member_entry["sha256"]},
        development_subset=split["development_subset"],
    )
    science = dict(
        scope="dev",
        counts=dict(train_background=6999, test_background=0, test_signal=0),
        config_sha256=transform["sha256"],
        files={"configuration.json": dict(sha256=transform["sha256"])},
        split_identity=split_identity,
        split_identity_sha256=digest(split_identity),
        source_integrity=source,
    )
    manifest = dict(scientific=science, scientific_sha256=digest(science))
    emit("dev_manifest", manifest)
    emit(
        "prepared",
        dict(
            source_ids_bytes_sha256=selected_hash,
            strict_source_order=True,
            manifest_scientific_sha256=manifest["scientific_sha256"],
            input_file_sha256=gold["sha256"],
            input_bytes_sha256=gold_hash,
        ),
    )
    emit(
        "prepare_receipt",
        dict(
            status="completed",
            access_audit=dict(
                population=dict(
                    split="train_background",
                    dev_only=True,
                    allow_test=False,
                    include_labels=False,
                    status="completed",
                    rows=1024,
                    unique_rows=1024,
                    ids_sha256=selected_hash,
                )
            ),
        ),
    )
    emit(
        "acquisition",
        dict(
            sha256=raw["sha256"],
            source=dict(record_id=6466204, version="v5"),
            verified_checksum="generated-not-publisher",
        ),
    )
    schema = dict(generated_strict_dataset_standin=True)
    emit("raw_audit", dict(datasets={"df/block0_values": schema}))
    if context.candidate == "pca-v1":
        model = core.PCAReconstruction(
            np.zeros(8),
            np.eye(8),
            np.ones(8),
            np.array([0.2, 0.18, 0.16, 0.14, 0.12, 0.1, 0.06, 0.04]),
            6,
            0.85,
            16,
        )
        artifact = model.artifact(
            provenance=dict(generated=True), build=dict(generated=True)
        )
    else:
        with core.torch.random.fork_rng(devices=[]):
            model = core.CompactAutoencoder()
        with core.torch.no_grad():
            for parameter in model.parameters():
                parameter.zero_()
        artifact = model.artifact(
            provenance=dict(generated=True),
            training=dict(optimizer_steps=0, not_fitted=True),
        )
    # Actual unchanged artifact interface; the creator model is released before loader.
    del model
    model_entry = emit(context.candidate + ":model", artifact)
    model_config = dict(generated_only=True, candidate=context.candidate)
    emit(context.candidate + ":config", model_config)
    thresholds = [dict(threshold=t) for t in (0.0, 0.001, 1.0, 10.0)]
    cal_science = dict(
        model_scientific_sha256=artifact["scientific_sha256"], thresholds=thresholds
    )
    calibration = dict(scientific=cal_science, scientific_sha256=digest(cal_science))
    emit(context.candidate + ":calibration", calibration)
    entry = dict(
        name=context.candidate,
        model_scientific_sha256=artifact["scientific_sha256"],
        results_scientific_sha256=calibration["scientific_sha256"],
        config_canonical_sha256=digest(model_config),
        thresholds=thresholds,
    )
    spec = dict(
        generated_only=True,
        candidate=context.candidate,
        bundle_sha256=context.bundle_sha256,
        models=[entry],
        allowed_files=entries,
        lineage_roles=[
            "split_manifest",
            "dev_manifest",
            "dev_configuration",
            "prepared",
            "prepare_receipt",
            "acquisition",
            "raw_audit",
        ],
        dev_scientific_sha256=manifest["scientific_sha256"],
        membership=dict(
            selected_sha256=selected_hash, file_sha256=member_entry["sha256"]
        ),
        golden=dict(payload_sha256=gold_hash, file_sha256=gold["sha256"]),
        raw=dict(
            file_sha256=raw["sha256"],
            size_bytes=raw["bytes"],
            publisher_md5="generated-not-publisher",
            audit_schema=schema,
        ),
        cache=dict(rdcc_nbytes=1048576, rdcc_nslots=521, rdcc_w0=0.75),
    )
    require(
        len(entries) == 14 and sum(e["bytes"] for e in entries) <= 196608,
        "Prospective serialized cardinality/bytes",
    )
    ledger.write_json(directory / "fixture-spec.json", spec)
    return dict(
        generated=True,
        setup_raw_rows=64,
        setup_feature_calls=64,
        setup_feature_rows=64,
        creator_models=1,
        serialized_models=1,
        loader_models=1,
        setup_public_score_calls=0,
        optimizer_steps=0,
        HDF_files_opened=0,
        serialized_files=len(entries),
        serialized_bytes=sum(e["bytes"] for e in entries),
        golden_file_rows=1024,
        golden_populated_rows=64,
        artifact_sha256=model_entry["sha256"],
    )
