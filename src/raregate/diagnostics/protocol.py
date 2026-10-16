"""Finite input boundary and accepted lineage; standard library only."""

import ast
import csv
import importlib.metadata
import os
import platform
import struct
import sys
from pathlib import Path

from raregate.benchmarks.protocol import digest, file_hash, read, write

ROOT = Path(__file__).resolve().parents[3]
CONFIG = "configs/diagnostics/exposed_feature_score_v1.json"
OUTPUT = "results/diagnostics/task0033-exposed-feature-score"
PROMPT = "docs/prompts/0033-exploratory-feature-score-diagnostics.md"
ACCEPTANCE = "data/task0033-software-acceptance.json"
PLAN = "data/task0033-execution-plan.json"
AUTH = "data/task0033-human-authorization.json"
ORIGINAL = "data/processed/lhco-rd-v1/schema-v1/full"
PREPARED = "data/task0031-three-prong/prepared"
OLD = "results/evaluation/task0026-frozen-pca-ae/final"
NEW = "results/evaluation/task0031-three-prong"
FEATURES = [
    "multiplicity",
    "scalar_pt",
    "max_pt",
    "pt_balance",
    "weighted_eta_mean",
    "weighted_eta_std",
    "pt_concentration",
    "massless_event_mass",
]
POPULATIONS = ("background", "two_prong", "three_prong")
CANDIDATES = ("PCA", "AE")
QUANTILES = [0.001, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 0.999]
STORE_ID = "d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2"
PREPARED_ID = "089f6c2c168a999fd0eaeca68414bc19633a0454e2981f9bc30e21a4dd22e622"
SCORE_HASHES = {
    "PCA/background": "7e8762a1b675c637ed1533eab1b96686bc7ffd364666aea022a0f6e48766987d",
    "PCA/two_prong": "93917e81ec79b489594899f8fcf5a00b60f3a84d17d550d6e31a9d8130249712",
    "AE/background": "65711ecda105801c07855d9f6d8e4d5fa9264daac993b8ed10e362166c5efee3",
    "AE/two_prong": "a2bc271d313d818ef82e596c115cfad8864c4a27892ea09595602e76828873a7",
    "PCA/three_prong": "5b818a3a0157a1752b0a3194b25f6392e55e7785e4b04341733cc87fc3fa6148",
    "AE/three_prong": "5f8d58a5e8aa15c337f9e5a0314bcb829ed9244617b8a82e4922119dcf63dff2",
}
FEATURE_HASHES = [
    "213d94d939141a7c0c8eb48641a3f6ecb185b9346d5f9cf2c2bedb15cab53015",
    "3059ff96b75268839d6e55e8aca1bb3fe019dab3cb19d4cbbb1dabe9cafb7f93",
]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def fixed(root, relative):
    p = Path(relative)
    require(not p.is_absolute() and ".." not in p.parts, "Nonrelative input")
    result = Path(root) / p
    require(
        not any(v.is_symlink() for v in [result, *result.parents]), "Symlink source"
    )
    require(result.is_file(), "Missing source: " + relative)
    return result


def header(path):
    """Read only bounded NPY metadata, with no NumPy import/mapping."""
    with path.open("rb") as stream:
        require(stream.read(6) == b"\x93NUMPY", "NPY magic")
        version = stream.read(2)
        require(version in (b"\x01\x00", b"\x02\x00"), "NPY version")
        n = struct.unpack(
            "<H" if version[0] == 1 else "<I", stream.read(2 if version[0] == 1 else 4)
        )[0]
        require(0 < n <= 4096, "Bounded header")
        value = ast.literal_eval(stream.read(n).decode("latin1"))
        offset = stream.tell()
    require(
        set(value) == {"descr", "fortran_order", "shape"}
        and value["fortran_order"] is False,
        "NPY layout",
    )
    return dict(dtype=value["descr"], shape=list(value["shape"]), offset=offset)


def runtime_versions():
    packages = {
        d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
    }
    return dict(
        python=sys.version,
        platform=platform.platform(),
        installed_packages=dict(sorted(packages.items())),
    )


def source_map(root=ROOT):
    paths = sorted(
        {
            p
            for folder in ("src", "scripts", "tests", "configs")
            for p in (root / folder).rglob("*")
            if p.is_file()
            and p.suffix in (".py", ".json")
            and "__pycache__" not in p.parts
        }
    )
    paths.append(root / "pyproject.toml")
    return {str(p.relative_to(root)): file_hash(p) for p in paths}


def receipt_key(outputs, path, stage):
    """Only an exact repo-relative key or the stage-owned basename is admissible."""
    require(str(Path(path).parent) == stage, "Foreign stage output")
    keys = [k for k in outputs if k == path or k == Path(path).name]
    require(len(keys) == 1, "Absent or ambiguous receipt output key")
    return outputs[keys[0]]


def build_plan(root=ROOT):
    """Byte/header/JSON-only planning. No numerical source or candidate access."""
    evidence = {}
    order_code = {}

    def order_proof(receipt, paths):
        for path in paths:
            actual = file_hash(ROOT / path)
            require(
                receipt["source_file_sha256"].get(path) == actual,
                "Accepted source-order implementation changed",
            )
            order_code[path] = actual

    def meta(path):
        p = fixed(root, path)
        evidence[path] = file_hash(p)
        return read(p)

    def science(path):
        d = meta(path)
        require(
            digest(d["scientific"]) == d["scientific_sha256"], "Scientific identity"
        )
        return d

    def accepted(base, phase=None):
        stage = base + ("/" + phase if phase else "")
        parent = meta(stage + "/parent-acceptance.json")
        require(parent["status"] == "parent_accepted", "Unaccepted predecessor")
        if phase:
            r = meta(stage + "/receipt.json")
            require(
                parent["receipt_file_byte_sha256"] == evidence[stage + "/receipt.json"],
                "Receipt identity",
            )
            require(
                r["status"] == "body_complete_awaiting_exit"
                and parent["phase"] == r["phase"] == phase,
                "Body/phase lineage",
            )
            dispatch = parent["dispatch"]
            require(
                dispatch["returncode"] == 0
                and dispatch["child_reaped"]
                and dispatch["parent_confirms_normal_exit"]
                and dispatch["within_deadline"]
                and dispatch["parent_error"] is None,
                "Historical lifecycle",
            )
            require(
                r["output_file_byte_sha256"] == parent["output_file_byte_sha256"],
                "Output parent/receipt mismatch",
            )
            return parent, r
        workflow = stage + "/workflow.json"
        meta(workflow)
        require(
            parent["workflow_file_byte_sha256"] == evidence[workflow],
            "Workflow identity",
        )
        return parent

    original = science(ORIGINAL + "/manifest.json")
    s = original["scientific"]
    config = meta(ORIGINAL + "/configuration.json")
    require(
        original["complete"] is True
        and original["schema_version"] == 1
        and original["scientific_sha256"] == STORE_ID,
        "Original store identity",
    )
    require(
        s["events"] == s["source_rows"] == 1100000
        and s["aggregate_channels"] == FEATURES,
        "Original scientific layout",
    )
    require(
        s["config_sha256"] == evidence[ORIGINAL + "/configuration.json"]
        and digest(s["split_identity"]) == s["split_identity_sha256"],
        "Configuration/split identity",
    )
    require(
        config["preprocessing"]["aggregates"]["channels"] == FEATURES
        and config["preprocessing"]["aggregates"]["log1p_indices"] == [0, 1, 2, 7],
        "Frozen feature transformations",
    )
    arrays = {}
    for name in (
        "event_features.npy",
        "split_codes.npy",
        "event_ids.npy",
        "labels.npy",
    ):
        arrays[ORIGINAL + "/" + name] = dict(s["files"][name])
    require(
        arrays[ORIGINAL + "/event_features.npy"]
        == dict(
            bytes=35200128, sha256=FEATURE_HASHES[0], shape=[1100000, 8], dtype="<f4"
        ),
        "Original feature pin",
    )
    accepted(OLD)
    accepted(NEW)
    pp, pr = accepted(NEW, "prepare")
    order_proof(pr, ["src/raregate/evaluation/local_three_prong_core.py"])
    prepared = science(PREPARED + "/manifest.json")
    ps = prepared["scientific"]
    require(
        prepared == pr["prepared_scientific"]
        and prepared["scientific_sha256"] == PREPARED_ID,
        "Prepared lineage",
    )
    require(
        receipt_key(
            pp["output_file_byte_sha256"], PREPARED + "/manifest.json", PREPARED
        )
        == evidence[PREPARED + "/manifest.json"],
        "Prepared manifest output identity",
    )
    require(
        ps["features"] == FEATURES
        and ps["count"] == ps["validated_rows"] == ps["nonempty_events"] == 100000
        and ps["dtype"] == "<f4"
        and ps["source_order"] == "all_rows_0_to_N_minus_1_no_selection"
        and ps["label_provenance"] == "verified_all_last_column_labels_1"
        and not any(ps["invalid_categories"].values()),
        "Prepared validity/order",
    )
    require(
        ps["original_training_scientific_sha256"] == STORE_ID
        and ps["transform"]["file_byte_sha256"]
        == evidence[ORIGINAL + "/configuration.json"]
        and ps["transform"]["canonical_JSON_sha256"] == digest(config)
        and ps["transform"]["preprocessing_parameters_canonical_JSON_sha256"]
        == digest(config["preprocessing"]),
        "Shared frozen transformation",
    )
    prepared_path = PREPARED + "/event_features.npy"
    require(
        receipt_key(pp["output_file_byte_sha256"], prepared_path, PREPARED)
        == ps["output_file_byte_sha256"]["event_features.npy"]
        == FEATURE_HASHES[1],
        "Prepared feature pin",
    )
    arrays[prepared_path] = dict(
        bytes=3200128, shape=[100000, 8], dtype="<f4", sha256=FEATURE_HASHES[1]
    )
    ledgers, scores, summaries, candidate_ids = {}, {}, {}, {}
    for candidate in CANDIDATES:
        old_stage, new_stage = OLD + "/" + candidate, NEW + "/" + candidate
        op, ore = accepted(OLD, candidate)
        np_, nr = accepted(NEW, candidate)
        order_proof(
            ore,
            [
                "src/raregate/data/processed.py",
                "src/raregate/evaluation/guarded_core.py",
            ],
        )
        order_proof(nr, ["src/raregate/evaluation/local_three_prong_core.py"])
        ev = science(old_stage + "/evaluation.json")
        nev = science(new_stage + "/evaluation.json")
        for stage, parent in [(old_stage, op), (new_stage, np_)]:
            path = stage + "/evaluation.json"
            require(
                receipt_key(parent["output_file_byte_sha256"], path, stage)
                == evidence[path],
                "Evaluation custody",
            )
        require(
            ore["verified_store_scientific_sha256"]
            == ev["scientific"]["processed_scientific_sha256"]
            == STORE_ID,
            "Original evaluation store",
        )
        require(
            nev["scientific"]["new_signal_scientific_sha256"] == PREPARED_ID,
            "New score/prepared alignment",
        )
        for key in ("model_scientific_sha256", "calibration_scientific_sha256"):
            require(
                ev["scientific"][key] == nev["scientific"][key], "Candidate lineage"
            )
        candidate_ids[candidate] = {
            key: ev["scientific"][key]
            for key in ("model_scientific_sha256", "calibration_scientific_sha256")
        }
        ledger_path = old_stage + "/test-unblinding.json"
        ledger = meta(ledger_path)
        require(
            receipt_key(op["output_file_byte_sha256"], ledger_path, old_stage)
            == evidence[ledger_path],
            "Accepted ledger identity",
        )
        require(
            ledger["status"] == "scientific_body_complete_awaiting_exit"
            and ledger["binding"]["store"]["scientific_sha256"] == STORE_ID
            and ledger["binding"]["store"]["metadata_file_byte_sha256"]["manifest.json"]
            == evidence[ORIGINAL + "/manifest.json"],
            "Ledger store binding",
        )
        require(
            ledger["parameters_before"] == ledger["parameters_after"],
            "Frozen original parameters",
        )
        require(
            nev["scientific"]["parameters_before"]
            == nev["scientific"]["parameters_after"],
            "Frozen new parameters",
        )
        ledgers[candidate] = ledger["population_access"]
        require(nr["exposure"]["potential_inflight"] is False, "Incomplete new access")
        records = [
            r
            for r in nr["exposure"]["records"]
            if r["kind"] == "signal_model_evaluation"
        ]
        require(
            len(records) == 1
            and records[0]["source"] == prepared_path
            and records[0]["expected"]
            == records[0]["confirmed_read"]
            == records[0]["confirmed_scored"]
            == 100000
            and records[0]["batches"] == [4096] * 24 + [1696],
            "Complete prepared source-order score coverage",
        )
        for population, stage, parent, filename in [
            ("background", old_stage, op, "test_background-scores.npy"),
            ("two_prong", old_stage, op, "test_signal-scores.npy"),
            ("three_prong", new_stage, np_, "three-prong-scores.npy"),
        ]:
            path = stage + "/" + filename
            sha = receipt_key(parent["output_file_byte_sha256"], path, stage)
            require(sha == SCORE_HASHES[candidate + "/" + population], "Score pin")
            n = 150471 if population == "background" else 100000
            arrays[path] = dict(bytes=n * 8 + 128, shape=[n], dtype="<f8", sha256=sha)
            scores[candidate + "/" + population] = path
        summary_path = old_stage + "/background-summary.json"
        summaries[candidate] = meta(summary_path)
        require(
            receipt_key(op["output_file_byte_sha256"], summary_path, old_stage)
            == evidence[summary_path],
            "Historical summary custody",
        )
    table_path = "results/tables/final/task0032-calibrated-utility.csv"
    p = fixed(root, table_path)
    evidence[table_path] = file_hash(p)
    with p.open() as stream:
        points = list(csv.DictReader(stream))
    thresholds, expected = {}, {}
    for candidate, label in [("PCA", "pca-v1"), ("AE", "compact-autoencoder-v2")]:
        thresholds[candidate] = []
        for target in [0.1, 0.05, 0.01, 0.001]:
            rows = [
                r
                for r in points
                if r["candidate"] == label and float(r["target_fpr"]) == target
            ]
            require(
                len(rows) == 2
                and {r["topology"] for r in rows} == {"two_prong", "three_prong"}
                and len({r["threshold"] for r in rows}) == 1,
                "Complete original thresholds",
            )
            threshold = float(rows[0]["threshold"])
            thresholds[candidate].append(dict(target_fpr=target, threshold=threshold))
            require(
                int(rows[0]["background_accepted"])
                == int(rows[1]["background_accepted"]),
                "Shared background",
            )
            expected[f"{candidate}/background/{target}"] = int(
                rows[0]["background_accepted"]
            )
            for row in rows:
                require(
                    int(row["background_total"]) == 150471
                    and int(row["signal_total"]) == 100000,
                    "Tail denominator",
                )
                expected[f"{candidate}/{row['topology']}/{target}"] = int(
                    row["signal_accepted"]
                )
        ledger = meta(OLD + "/" + candidate + "/test-unblinding.json")
        require(
            ledger["binding"]["candidate"]["thresholds"] == thresholds[candidate],
            "Calibrated thresholds lineage",
        )
    for summary_path, registry_key, prefix in [
        (
            "results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json",
            "receipt_lineage_Phase_B",
            OLD,
        ),
        (
            "results/tables/final/task0031-local-three-prong-evaluation-summary.json",
            "operational_evidence_file_byte_sha256",
            NEW,
        ),
    ]:
        registry = meta(summary_path)[registry_key]
        for path, sha in evidence.items():
            if path.startswith(prefix + "/"):
                require(
                    path in registry and registry[path] == sha,
                    "Accepted curated receipt lineage missing/altered: " + path,
                )
    return dict(
        schema=1,
        exploratory=True,
        arrays=arrays,
        metadata=evidence,
        original=ORIGINAL,
        prepared=PREPARED,
        original_identity=STORE_ID,
        prepared_identity=PREPARED_ID,
        counts=dict(background=150471, two_prong=100000, three_prong=100000),
        original_rows=1100000,
        role_counts=s["counts"],
        ledgers=ledgers,
        scores=scores,
        thresholds=thresholds,
        expected_tail_counts=expected,
        historical_score_summaries=summaries,
        candidates=candidate_ids,
        accepted_source_order_code_sha256=order_code,
        features=FEATURES,
        log1p_indices=[0, 1, 2, 7],
        questions=[
            "frozen feature marginals",
            "within-candidate score marginals",
            "within-population feature-score monotonic association",
            "original strict-threshold feature profiles",
        ],
    )


def verify_inputs(root, plan, journal=lambda *args, **kwargs: None):
    for path, sha in plan["metadata"].items():
        p = fixed(root, path)
        require(file_hash(p) == sha, "Altered metadata: " + path)
        journal("byte_hash", path, p.stat().st_size)
    for path, identity in plan["arrays"].items():
        p = fixed(root, path)
        require(
            p.stat().st_size == identity["bytes"]
            and file_hash(p) == identity["sha256"],
            "Altered array: " + path,
        )
        journal("byte_hash", path, identity["bytes"])
        h = header(p)
        require(
            h["shape"] == identity["shape"]
            and h["dtype"] == identity["dtype"]
            and h["offset"] == 128,
            "Array header",
        )
        journal("array_header", path, h["offset"])


def checked_output(directory, name):
    require(
        Path(name).name == name and not (directory / name).exists(),
        "Duplicate/nonlocal output",
    )
    return directory / name


def durable_json(path, value, exclusive=False):
    write(path, value, exclusive=exclusive)
    with path.open("rb") as stream:
        os.fsync(stream.fileno())
