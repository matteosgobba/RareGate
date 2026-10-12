"""Task0031-only local scientific identities/compatibility; stdlib metadata only."""

import importlib.metadata
import shutil

from latenttrigger.benchmarks import protocol as p
from latenttrigger.data.three_prong_v3_runtime import ContinuousClock, check_deadline
from latenttrigger.data.three_prong_v3_transport import hash_bytes
from latenttrigger.evaluation import three_prong_protocol as old

ROOT, fixed, require, array_header = p.ROOT, old.fixed, old.require, old.array_header
source_map = old.source_map
CONFIG = "configs/evaluation/frozen_three_prong_local_v2.json"
HASH = "25d862a0f77074cb8f476ea3cc445b2c9469db1f1e65ec289899719a556b0244"
OUTPUT = "results/evaluation/task0031-three-prong"
PREPARED = "data/task0031-three-prong/prepared"
ACCEPTANCE = "data/task0031-software-acceptance.json"
PLAN = "data/task0031-execution-plan.json"
CONSENT = "data/task0031-human-authorization.json"
PHASES = ("prepare", "PCA", "AE", "consolidate")
deps = old.deps


def load(root=ROOT):
    spec = p.read(fixed(root, CONFIG))
    require(
        p.digest(spec) == HASH, "Changed fixed local scientific protocol/source/limits"
    )
    return spec


def check_file(root, path, digest, *, clock, deadline):
    check_deadline(clock, deadline)
    file = fixed(root, path)
    actual = hash_bytes(file, clock=clock, deadline=deadline)
    require(actual["SHA256"] == digest, "Changed bound file bytes: " + path)
    return file


def metadata(root, spec, *, clock, deadline, check_payload=True):
    check_deadline(clock, deadline)
    for name, version in spec.get("analysis_versions", {}).items():
        require(
            importlib.metadata.version(name) == version,
            "Pinned plotting distribution changed",
        )
    scientific = scientific_metadata(root, spec, clock, deadline)
    for path, sha in spec["preserved_file_byte_sha256"].items():
        check_file(root, path, sha, clock=clock, deadline=deadline)
    local = spec["local_payload"]
    manifest = p.read(root / local["manifest"])
    parent = p.read(root / local["acquisition_parent"])
    workflow = p.read(root / "results/acquisition/task0030-three-prong/workflow.json")
    integrity = p.read(root / local["integrity"])
    require(
        parent["status"] == workflow["status"] == "parent_accepted_verified_artifact"
        and parent["sleep_assertion_released"]
        and parent["accepted_complete_bytes"] == local["bytes"]
        and parent["workflow_file_byte_sha256"]
        == p.file_hash(root / "results/acquisition/task0030-three-prong/workflow.json")
        and workflow["manifest_file_byte_sha256"]
        == p.file_hash(root / local["manifest"])
        and manifest["required_session_parent_acceptance"]
        == local["acquisition_parent"]
        and manifest["verified_bytes"] == local["bytes"]
        and manifest["publisher_MD5"] == local["MD5"]
        and manifest["local_SHA256"]
        == local["SHA256"]
        == spec["source"]["local_payload_sha256"],
        "Complete accepted acquisition manifest AND required parent required",
    )
    require(
        p.digest(p.read(root / local["acquisition_protocol"]))
        == local["acquisition_protocol_canonical_JSON_sha256"],
        "Acquisition protocol changed",
    )
    require(
        integrity["locally_computed"]
        == dict(bytes=local["bytes"], MD5=local["MD5"], SHA256=local["SHA256"])
        and all(
            workflow["stages"][i]["parent"]["status"] == "parent_accepted"
            and workflow["stages"][i]["parent"]["dispatch"]["child_reaped"]
            for i in range(3)
        ),
        "Acquisition full-byte/normal lifecycle lineage",
    )
    path = fixed(root, local["path"])
    require(
        not path.is_symlink()
        and path.is_file()
        and path.stat().st_size == local["bytes"],
        "Pinned local artifact presence/size",
    )
    if check_payload:
        value = hash_bytes(path, clock=clock, deadline=deadline)
        require(
            value
            == dict(bytes=local["bytes"], MD5=local["MD5"], SHA256=local["SHA256"]),
            "Complete local byte integrity mismatch",
        )
    ref = spec["original_fingerprints"]
    path = check_file(root, ref["path"], ref["sha256"], clock=clock, deadline=deadline)
    array_header(path, "|V32", ref["shape"])
    check_deadline(clock, deadline)
    return dict(
        status="local_byte_and_scientific_metadata_ready_numerical_access_pending",
        original_scientific=scientific,
        local_full_byte_verification=check_payload,
        numerical_loads=0,
        model_instantiations=0,
    )


def acceptance(root=ROOT, *, clock=None, deadline=None):
    clock = clock or ContinuousClock()
    deadline = deadline or clock() + 15
    doc = p.read(fixed(root, ACCEPTANCE))
    require(
        doc["task"] == "0031"
        and doc["status"] == "current_source_software_accepted"
        and doc["protocol_canonical_JSON_sha256"] == HASH
        and doc["protocol_file_byte_sha256"] == p.file_hash(root / CONFIG)
        and doc["source_file_sha256"] == source_map(root)
        and doc["full_passed"] == doc["portable_passed"] > 1503
        and doc["quality"]
        == dict(
            lint="passed",
            format="passed",
            dependencies="passed",
            synthetic_integration="passed_native_continuous_supervised_and_figures",
        ),
        "Own current local-science software acceptance required",
    )
    for path, sha in doc["validation_evidence_file_byte_sha256"].items():
        check_file(root, path, sha, clock=clock, deadline=deadline)
    check_deadline(clock, deadline)
    return doc


def plan(root=ROOT, *, clock=None, deadline=None):
    clock = clock or ContinuousClock()
    deadline = deadline or clock() + 15
    spec = load(root)
    accepted = acceptance(root, clock=clock, deadline=deadline)
    return dict(
        task="0031",
        specification=spec,
        protocol_canonical_JSON_sha256=HASH,
        software_acceptance_file_byte_sha256=p.file_hash(root / ACCEPTANCE),
        source_file_sha256=accepted["source_file_sha256"],
        scope="one local three-prong signal study;shared exposed Task0026 background;no independent BG generalization/no new significance",
        authorized_access=spec["expected_access"],
        failure="first gate/lifecycle/guard/continuous deadline failure stops;retained evidence;no retry/resume/second campaign",
    )


def authorization(root=ROOT, *, clock=None, deadline=None):
    current = plan(root, clock=clock, deadline=deadline)
    doc = p.read(fixed(root, CONSENT))
    prompt = current["specification"]["prompt"]
    require(
        p.read(root / PLAN) == current
        and doc
        == dict(
            authority="actual_human_Task0031_prospective_conditional_scope",
            human_message=(root / prompt["path"]).read_text(),
            prompt_file_byte_sha256=prompt["file_byte_sha256"],
            UTC=doc["UTC"],
            plan_sha256=p.digest(current),
            acceptance_file_byte_sha256=current["software_acceptance_file_byte_sha256"],
            source_file_sha256=current["source_file_sha256"],
            human_approved_exact_postimplementation_hash=False,
        ),
        "Actual prompt-bound prospective consent/current plan required",
    )
    return current


def namespace(root=ROOT):
    base, prepared = fixed(root, OUTPUT), fixed(root, "data/task0031-three-prong")
    require(
        not base.exists() and not prepared.exists(),
        "Existing/partial/foreign/consumed local campaign;no resume/reset",
    )
    return base, prepared


def disk_space(root, spec):
    space = spec["storage"]
    budget = (
        space["guards_bytes"]
        + space["max_prepared_arrays_bytes"]
        + 2 * space["max_candidate_arrays_bytes"]
        + space["max_reporting_bytes"]
        + 4 * (space["access_ledger_bytes_each"] + space["log_bytes_each"])
        + space["metadata_slack_bytes"]
    )
    free = shutil.disk_usage(root).free
    require(
        budget <= space["required_free_bytes"] <= free,
        "Fixed prepared/score/curve/journal/log storage budget",
    )
    return dict(
        required_free_bytes=space["required_free_bytes"],
        worst_case_bytes=budget,
        available_bytes=free,
    )


def compatibility(manifest, spec):
    science = old.compatibility(manifest, spec)
    require(
        science["actual_raw_sha256"] == spec["source"]["local_payload_sha256"]
        and science["label_provenance"] == "verified_all_last_column_labels_1"
        and science["validated_rows"] == science["count"]
        and science["nonempty_events"] == science["count"]
        and all(value == 0 for value in science["invalid_categories"].values())
        and science["transformation_sequence"]
        == "sourceFP64_validate_sort_wrap→physicalFP32_all_particles→aggregateFP64→frozen_logs_scaler→featuresFP32",
        "Complete distinct-source numerical/precision compatibility",
    )
    return science


def scientific_metadata(root, spec, clock, deadline):
    def checked(root, path, digest):
        return check_file(root, path, digest, clock=clock, deadline=deadline)

    for path, digest in spec["historical_source_file_sha256"].items():
        checked(root, path, digest)
    checked(root, spec["prompt"]["path"], spec["prompt"]["file_byte_sha256"])
    deps.check_dependencies(root, deps.load(root))
    require(p.runtime_versions() == spec["core_versions"], "Core runtime changed")
    for path, digest in spec["primary_metadata"]["file_byte_sha256"].items():
        checked(root, path, digest)
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
        checked(root, store["path"] + "/" + name, digest)
    manifest = p.read(root / store["path"] / "manifest.json")
    require(
        p.digest(manifest["scientific"])
        == manifest["scientific_sha256"]
        == store["scientific_sha256"],
        "Original training manifest identity",
    )
    transform = p.read(
        checked(root, spec["transform"]["path"], spec["transform"]["file_byte_sha256"])
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
                checked(
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
        checked(root, path, digest)
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
        path = checked(root, ref["path"], ref["file_byte_sha256"])
        require(path.stat().st_size == ref["bytes"], "Cached background size")
        headers.append(array_header(path, "<f8", [150471]))
    return dict(
        status="metadata_ready_payload_custody_pending",
        background_headers=headers,
        numeric_cached_loads=0,
        signal_payload_opened=False,
        original_fingerprints_opened=False,
    )
