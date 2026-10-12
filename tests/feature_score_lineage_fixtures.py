"""Small synthetic accepted-lineage JSONs; no operational artifacts are read."""

import csv

from latenttrigger.diagnostics import protocol as p


def lineage_fixture(root, monkeypatch):
    def put(path, value):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        p.durable_json(file, value)
        return p.file_hash(file)

    def science(path, value):
        doc = dict(scientific=value, scientific_sha256=p.digest(value))
        put(path, doc)
        return doc

    config = dict(
        preprocessing=dict(
            aggregates=dict(channels=p.FEATURES, log1p_indices=[0, 1, 2, 7])
        )
    )
    config_hash = put(p.ORIGINAL + "/configuration.json", config)
    split = dict(protocol="synthetic", counts={})
    orig = dict(
        events=1100000,
        source_rows=1100000,
        aggregate_channels=p.FEATURES,
        config_sha256=config_hash,
        split_identity=split,
        split_identity_sha256=p.digest(split),
        counts=dict(
            train_background=699957,
            validation_selection_background=74749,
            validation_calibration_background=74823,
            test_background=150471,
            test_signal=100000,
        ),
        files={
            "event_features.npy": dict(
                bytes=35200128,
                sha256=p.FEATURE_HASHES[0],
                shape=[1100000, 8],
                dtype="<f4",
            ),
            **{
                name: dict(
                    bytes=128,
                    sha256="synthetic",
                    shape=[1100000],
                    dtype="|u1" if name != "event_ids.npy" else "<i8",
                )
                for name in ("split_codes.npy", "labels.npy", "event_ids.npy")
            },
        },
    )
    original = dict(
        scientific=orig,
        scientific_sha256=p.digest(orig),
        complete=True,
        schema_version=1,
    )
    original_hash = put(p.ORIGINAL + "/manifest.json", original)
    monkeypatch.setattr(p, "STORE_ID", original["scientific_sha256"])
    prep = dict(
        features=p.FEATURES,
        count=100000,
        validated_rows=100000,
        nonempty_events=100000,
        dtype="<f4",
        source_order="all_rows_0_to_N_minus_1_no_selection",
        label_provenance="verified_all_last_column_labels_1",
        invalid_categories=dict(synthetic=0),
        original_training_scientific_sha256=p.STORE_ID,
        transform=dict(
            file_byte_sha256=config_hash,
            canonical_JSON_sha256=p.digest(config),
            preprocessing_parameters_canonical_JSON_sha256=p.digest(
                config["preprocessing"]
            ),
        ),
        output_file_byte_sha256={"event_features.npy": p.FEATURE_HASHES[1]},
    )
    prepared = science(p.PREPARED + "/manifest.json", prep)
    monkeypatch.setattr(p, "PREPARED_ID", prepared["scientific_sha256"])

    def accepted(base, phase, receipt):
        path = base + "/" + phase
        receipt["source_file_sha256"] = {
            name: p.file_hash(p.ROOT / name)
            for name in (
                "src/latenttrigger/data/processed.py",
                "src/latenttrigger/evaluation/guarded_core.py",
                "src/latenttrigger/evaluation/local_three_prong_core.py",
            )
        }
        receipt.update(status="body_complete_awaiting_exit", phase=phase)
        sha = put(path + "/receipt.json", receipt)
        put(
            path + "/parent-acceptance.json",
            dict(
                status="parent_accepted",
                phase=phase,
                receipt_file_byte_sha256=sha,
                output_file_byte_sha256=receipt["output_file_byte_sha256"],
                dispatch=dict(
                    returncode=0,
                    child_reaped=True,
                    parent_confirms_normal_exit=True,
                    within_deadline=True,
                    parent_error=None,
                ),
            ),
        )

    for base in (p.OLD, p.NEW):
        sha = put(base + "/workflow.json", dict(synthetic=True))
        put(
            base + "/parent-acceptance.json",
            dict(status="parent_accepted", workflow_file_byte_sha256=sha),
        )
    prepared_path = p.PREPARED + "/event_features.npy"
    accepted(
        p.NEW,
        "prepare",
        dict(
            prepared_scientific=prepared,
            output_file_byte_sha256={
                prepared_path: p.FEATURE_HASHES[1],
                p.PREPARED + "/manifest.json": p.file_hash(
                    root / p.PREPARED / "manifest.json"
                ),
            },
        ),
    )
    points = []
    for candidate, label in [("PCA", "pca-v1"), ("AE", "compact-autoencoder-v2")]:
        old_stage, new_stage = p.OLD + "/" + candidate, p.NEW + "/" + candidate
        thresholds = [
            dict(target_fpr=t, threshold=v)
            for t, v in zip([0.1, 0.05, 0.01, 0.001], [0.3, 0.5, 1.0, 4.0], strict=True)
        ]
        old_ev = science(
            old_stage + "/evaluation.json",
            dict(
                processed_scientific_sha256=p.STORE_ID,
                model_scientific_sha256="synthetic-model-" + candidate,
                calibration_scientific_sha256="synthetic-calibration",
            ),
        )
        science(
            new_stage + "/evaluation.json",
            dict(
                new_signal_scientific_sha256=p.PREPARED_ID,
                model_scientific_sha256=old_ev["scientific"]["model_scientific_sha256"],
                calibration_scientific_sha256="synthetic-calibration",
                parameters_before="synthetic",
                parameters_after="synthetic",
            ),
        )
        ledger_sha = put(
            old_stage + "/test-unblinding.json",
            dict(
                status="scientific_body_complete_awaiting_exit",
                binding=dict(
                    store=dict(
                        scientific_sha256=p.STORE_ID,
                        metadata_file_byte_sha256={"manifest.json": original_hash},
                    ),
                    candidate=dict(thresholds=thresholds),
                ),
                population_access=[],
                parameters_before="synthetic",
                parameters_after="synthetic",
            ),
        )
        summary_sha = put(old_stage + "/background-summary.json", dict(count=150471))
        old_outputs = {
            "evaluation.json": p.file_hash(root / old_stage / "evaluation.json"),
            "test-unblinding.json": ledger_sha,
            "background-summary.json": summary_sha,
            "test_background-scores.npy": p.SCORE_HASHES[candidate + "/background"],
            "test_signal-scores.npy": p.SCORE_HASHES[candidate + "/two_prong"],
        }
        accepted(
            p.OLD,
            candidate,
            dict(
                verified_store_scientific_sha256=p.STORE_ID,
                output_file_byte_sha256=old_outputs,
            ),
        )
        accepted(
            p.NEW,
            candidate,
            dict(
                output_file_byte_sha256={
                    new_stage + "/evaluation.json": p.file_hash(
                        root / new_stage / "evaluation.json"
                    ),
                    new_stage + "/three-prong-scores.npy": p.SCORE_HASHES[
                        candidate + "/three_prong"
                    ],
                },
                exposure=dict(
                    potential_inflight=False,
                    records=[
                        dict(
                            kind="signal_model_evaluation",
                            source=prepared_path,
                            expected=100000,
                            confirmed_read=100000,
                            confirmed_scored=100000,
                            batches=[4096] * 24 + [1696],
                        )
                    ],
                ),
            ),
        )
        for threshold in thresholds:
            for topology in ("two_prong", "three_prong"):
                points.append(
                    dict(
                        candidate=label,
                        topology=topology,
                        **threshold,
                        background_accepted=3,
                        signal_accepted=2,
                        background_total=150471,
                        signal_total=100000,
                    )
                )
    table = root / "results/tables/final/task0032-calibrated-utility.csv"
    table.parent.mkdir(parents=True)
    with table.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(points[0]))
        writer.writeheader()
        writer.writerows(points)
    for summary_path, key, base in [
        (
            "results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json",
            "receipt_lineage_Phase_B",
            p.OLD,
        ),
        (
            "results/tables/final/task0031-local-three-prong-evaluation-summary.json",
            "operational_evidence_file_byte_sha256",
            p.NEW,
        ),
    ]:
        put(
            summary_path,
            {
                key: {
                    str(path.relative_to(root)): p.file_hash(path)
                    for path in (root / base).rglob("*.json")
                }
            },
        )
    return p.build_plan(root)
