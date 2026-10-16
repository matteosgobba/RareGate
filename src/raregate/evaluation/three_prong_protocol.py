"""Source-bound three-prong metadata/compatibility plan; no numerical imports."""

import ast
import struct

from raregate.benchmarks import protocol as p
from raregate.benchmarks.frozen_cpu_v2_protocol import fixed
from raregate.exports import onnx_protocol as deps

ROOT = p.ROOT
CONFIG = "configs/evaluation/frozen_three_prong_v1.json"
HASH = "cf5da6448910e59e77ffde3da50123c208e1d0e522d38a2b4727d5f7807e77b6"
OUTPUT = "results/evaluation/task0028-three-prong"
RAW = "data/task0028-three-prong"
PREPARED = RAW + "/prepared"
PLAN = "data/task0028-execution-plan.json"
ACCEPTANCE = "data/task0028-software-acceptance.json"
CONSENT = "data/task0028-human-authorization.json"
PHASES = ("acquire", "prepare", "PCA", "AE", "consolidate")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def source_map(root=ROOT):
    return dict(
        p.source_map(root),
        **{
            name: p.file_hash(root / name)
            for name in ("pyproject.toml", "configs/dependencies/onnx_cpu_v1.json")
        },
    )


def load(root=ROOT):
    spec = p.read(fixed(root, CONFIG))
    require(p.digest(spec) == HASH, "Unsupported strict protocol/source/limit override")
    return spec


def array_header(path, dtype, shape):
    """Read at most 1034 header bytes, never a numerical payload."""
    with path.open("rb") as stream:
        prefix = stream.read(10)
        require(prefix[:8] == b"\x93NUMPY\x01\x00", "Only bounded NPY1")
        length = struct.unpack("<H", prefix[8:])[0]
        require(length <= 1024, "Unbounded NPY header")
        header = ast.literal_eval(stream.read(length).decode("latin1").strip())
    require(
        type(header.get("fortran_order")) is bool
        and type(header.get("shape")) is tuple
        and all(type(v) is int for v in header["shape"])
        and header == dict(descr=dtype, fortran_order=False, shape=tuple(shape)),
        "Wrong cached count/dtype/order",
    )
    require(
        10 + length + shape[0] * (8 if dtype == "<f8" else 32) == path.stat().st_size,
        "NPY byte relation",
    )
    return dict(version=[1, 0], dtype=dtype, shape=shape, header_bytes=10 + length)


def check_file(root, path, digest):
    file = fixed(root, path)
    require(p.file_hash(file) == digest, "File-byte identity mismatch: " + path)
    return file


def metadata(root, spec):
    for path, digest in spec["historical_source_file_sha256"].items():
        check_file(root, path, digest)
    check_file(root, spec["prompt"]["path"], spec["prompt"]["file_byte_sha256"])
    deps.check_dependencies(root, deps.load(root))
    require(p.runtime_versions() == spec["core_versions"], "Core runtime changed")
    for path, digest in spec["primary_metadata"]["file_byte_sha256"].items():
        check_file(root, path, digest)
    source = spec["source"]
    api = p.read(root / "data/task0028-validation/zenodo-metadata.json")
    file = next(f for f in api["files"] if f["key"] == source["filename"])
    require(
        api["id"] == source["record_id"]
        and api["metadata"]["doi"] == source["doi"]
        and api["metadata"]["version"] == source["version"],
        "Publisher source/version mismatch",
    )
    require(
        file["size"] == source["expected_size"]
        and file["checksum"] == "md5:" + source["expected_checksum"]
        and file["links"]["self"] == source["url"]
        and api["metadata"]["license"]["id"] == "cc-by-4.0",
        "Publisher size/checksum/URL/license mismatch",
    )
    store = spec["original_store"]
    for name, digest in store["metadata_file_byte_sha256"].items():
        check_file(root, store["path"] + "/" + name, digest)
    manifest = p.read(root / store["path"] / "manifest.json")
    require(
        p.digest(manifest["scientific"])
        == manifest["scientific_sha256"]
        == store["scientific_sha256"],
        "Original training manifest identity",
    )
    transform = p.read(
        check_file(
            root, spec["transform"]["path"], spec["transform"]["file_byte_sha256"]
        )
    )
    require(
        p.digest(transform) == spec["transform"]["canonical_JSON_sha256"],
        "Frozen transform/scaler identity",
    )
    require(
        manifest["scientific"]["files"]["fingerprints.npy"]
        == {
            k: spec["original_fingerprints"][k]
            for k in ("bytes", "sha256", "shape", "dtype")
        },
        "Original fingerprint registry reference",
    )
    fingerprint_path = fixed(root, spec["original_fingerprints"]["path"])
    require(
        fingerprint_path.is_file()
        and fingerprint_path.stat().st_size == spec["original_fingerprints"]["bytes"],
        "Original fingerprint registry presence/size; payload verification deferred",
    )
    for candidate in spec["candidates"]:
        documents = {}
        for kind in ("config", "model", "results"):
            documents[kind] = p.read(
                check_file(
                    root, candidate[kind + "_path"], candidate[kind + "_file_sha256"]
                )
            )
        art, cal = documents["model"], documents["results"]
        require(
            p.digest(documents["config"]) == candidate["config_canonical_sha256"],
            "Model config identity",
        )
        require(
            p.digest(art["scientific"])
            == art["scientific_sha256"]
            == candidate["model_scientific_sha256"],
            "Model scientific identity",
        )
        require(
            p.digest(cal["scientific"])
            == cal["scientific_sha256"]
            == candidate["results_scientific_sha256"],
            "Calibration scientific identity",
        )
        require(
            art["scientific"]["provenance"] == cal["scientific"]["provenance"]
            and art["scientific"]["provenance"]["processed_scientific_sha256"]
            == store["scientific_sha256"]
            and art["scientific"]["features"] == spec["features"],
            "Original training provenance/features",
        )
        require(
            candidate["score_definition"] == "sum_squared_reconstruction_residual"
            and candidate["orientation"] == "higher_is_more_anomalous"
            and candidate["score_dtype"] == "float64"
            and candidate["threshold_decision"] == "score > threshold",
            "Frozen score/decision semantics",
        )
        require(
            [
                {k: t[k] for k in ("target_fpr", "threshold")}
                for t in cal["scientific"]["thresholds"]
            ]
            == candidate["thresholds"],
            "Frozen thresholds",
        )
    for path, digest in spec["accepted_background_lineage_file_byte_sha256"].items():
        check_file(root, path, digest)
    root_accept = p.read(
        root / "results/evaluation/task0026-frozen-pca-ae/final/parent-acceptance.json"
    )
    require(
        root_accept["status"] == "parent_accepted", "Background campaign not accepted"
    )
    headers = []
    for ref, candidate in zip(
        spec["cached_background"], spec["candidates"], strict=True
    ):
        base = root / "results/evaluation/task0026-frozen-pca-ae/final" / ref["phase"]
        parent, receipt = (
            p.read(base / "parent-acceptance.json"),
            p.read(base / "receipt.json"),
        )
        evaluation, audit = (
            p.read(base / "evaluation.json"),
            p.read(base / "test-unblinding.json"),
        )
        require(
            ref["candidate"] == candidate["name"]
            and ref["original_model_scientific_sha256"]
            == candidate["model_scientific_sha256"]
            and ref["calibration_scientific_sha256"]
            == candidate["results_scientific_sha256"],
            "Cached candidate binding",
        )
        require(
            parent["status"] == "parent_accepted"
            and parent["dispatch"]["parent_confirms_normal_exit"]
            and parent["dispatch"]["child_reaped"],
            "Cached background lifecycle",
        )
        require(
            parent["receipt_file_byte_sha256"] == p.file_hash(base / "receipt.json")
            and parent["output_file_byte_sha256"] == receipt["output_file_byte_sha256"],
            "Cached receipt outputs",
        )
        require(
            receipt["output_file_byte_sha256"]["test_background-scores.npy"]
            == ref["file_byte_sha256"],
            "Cached score receipt identity",
        )
        require(
            p.digest(evaluation["scientific"]) == evaluation["scientific_sha256"]
            and evaluation["scientific"]["model_scientific_sha256"]
            == candidate["model_scientific_sha256"]
            and evaluation["scientific"]["calibration_scientific_sha256"]
            == candidate["results_scientific_sha256"]
            and evaluation["scientific"]["metrics"]["background_total"] == 150471,
            "Cached scientific output/count",
        )
        bg = audit["population_access"][0]
        require(
            bg["split"] == "test_background"
            and bg["confirmed_events_read"] == bg["confirmed_events_scored"] == 150471
            and bg["completed_score_batches"] == 37
            and bg["inflight"] is None
            and [b["rows_scored"] for b in bg["batches"]] == [4096] * 36 + [3015],
            "Cached original source-order/full-tail audit",
        )
        path = check_file(root, ref["path"], ref["file_byte_sha256"])
        require(path.stat().st_size == ref["bytes"], "Cached background size")
        headers.append(array_header(path, "<f8", [150471]))
    return dict(
        status="metadata_ready_payload_custody_pending",
        background_headers=headers,
        numeric_cached_loads=0,
        signal_payload_opened=False,
        original_fingerprints_opened=False,
    )


def acceptance(root=ROOT):
    doc = p.read(fixed(root, ACCEPTANCE))
    require(
        doc["task"] == "0028"
        and doc["protocol_canonical_JSON_sha256"] == HASH
        and doc["protocol_file_byte_sha256"] == p.file_hash(root / CONFIG)
        and doc["source_file_sha256"] == source_map(root),
        "Current new-source acceptance required",
    )
    require(
        doc["full_passed"] == doc["portable_passed"]
        and doc["full_passed"] > 1271
        and doc["quality"]
        == dict(
            lint="passed",
            format="passed",
            dependencies="passed",
            synthetic_integration="passed_actual_native",
        ),
        "Full/portable/synthetic quality acceptance",
    )
    for item in doc["validation_evidence"]:
        check_file(root, item["path"], item["file_byte_sha256"])
    return doc


def plan(root=ROOT):
    spec = load(root)
    a = acceptance(root)
    ready = metadata(root, spec)
    return dict(
        task="0028",
        phase="B_requires_explicit_human_authorization",
        protocol_canonical_JSON_sha256=HASH,
        software_acceptance_file_byte_sha256=p.file_hash(root / ACCEPTANCE),
        source_file_sha256=a["source_file_sha256"],
        specification=spec,
        readiness=ready,
        scope="new_signal_topology_with_reused_exposed_background;not_independent_signal_background_or_background_domain_shift",
        authorization_covers=[
            "one_pinned_payload_acquisition",
            "integrity_only_raw_and_original_fingerprint_overlap_audit",
            "frozen_feature_preparation",
            "one_new_signal_evaluation_per_frozen_candidate",
            "two_numeric_accepted_background_score_reuses",
            "no_post_test_fit_recalibration_candidate_or_threshold_selection",
        ],
    )


def authorization(root, allow_test, approved_hash):
    require(
        allow_test is True, "Phase B requires explicit human consent before reservation"
    )
    current = plan(root)
    require(
        p.digest(current) == approved_hash and p.read(root / PLAN) == current,
        "Reviewed plan/source changed",
    )
    consent = p.read(fixed(root, CONSENT))
    require(
        set(consent)
        == {
            "authority",
            "human_message",
            "utc",
            "approved_plan_sha256",
            "acceptance_file_byte_sha256",
            "source_file_sha256",
            "authorized_scope",
        },
        "Strict human audit fields",
    )
    require(
        consent["authority"] == "explicit_human_user_message"
        and isinstance(consent["human_message"], str)
        and consent["human_message"].strip()
        and consent["approved_plan_sha256"] == approved_hash
        and consent["acceptance_file_byte_sha256"] == p.file_hash(root / ACCEPTANCE)
        and consent["source_file_sha256"] == source_map(root)
        and consent["authorized_scope"] == current["authorization_covers"],
        "Actual source-bound human authorization required",
    )
    return current, consent


def compatibility(prepared, spec):
    """Isolated new-source contract; never mislabel it as the original store."""
    require(
        prepared["scientific_sha256"] == p.digest(prepared["scientific"]),
        "Prepared scientific identity",
    )
    science = prepared["scientific"]
    require(
        science["source"] == spec["source"]
        and isinstance(science["actual_raw_sha256"], str)
        and len(science["actual_raw_sha256"]) == 64
        and set(science["actual_raw_sha256"]) <= set("0123456789abcdef")
        and science["transform"] == spec["transform"]
        and science["features"] == spec["features"]
        and science["dtype"] == "<f4"
        and science["count"] == spec["source"]["publisher_expected_events"],
        "New signal/source/scaler/feature compatibility",
    )
    require(
        science["original_training_scientific_sha256"]
        == spec["original_store"]["scientific_sha256"]
        and science["original_fingerprint_reference"] == spec["original_fingerprints"]
        and science["cached_background"] == spec["cached_background"],
        "Original training/reference compatibility",
    )
    require(
        science["within_source_duplicates"] == science["original_overlap_count"] == 0
        and science["all_original_roles_checked"] is True,
        "Duplicate/overlap refusal; no subset",
    )
    require(
        science["source"] != spec["original_store"],
        "New source must retain distinct identity",
    )
    return science
