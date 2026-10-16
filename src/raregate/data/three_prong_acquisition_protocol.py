"""Strict Task0029 acquisition-only identities; no scientific/numerical readers."""

import shutil

from raregate.benchmarks import protocol as p
from raregate.benchmarks.frozen_cpu_v2_protocol import fixed
from raregate.exports import onnx_protocol as dependencies

ROOT = p.ROOT
CONFIG = "configs/acquisition/three_prong_v2.json"
HASH = "c66c2b454554d5a123a73cc3b594d2c9759874459d1a14b2004a42d325f64f64"
OUTPUT = "results/acquisition/task0029-three-prong"
RAW = "data/task0029-three-prong-acquisition"
ACCEPTANCE = "data/task0029-software-acceptance.json"
AUTHORIZATION = "data/task0029-human-authorization.json"
PLAN = "data/task0029-acquisition-plan.json"
PHASES = ("transfer", "verify")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_map(root=ROOT):
    return dict(
        p.source_map(root),
        **{
            name: p.file_hash(root / name)
            for name in (
                "pyproject.toml",
                "configs/dependencies/onnx_cpu_v1.json",
            )
        },
    )


def load(root=ROOT):
    spec = p.read(fixed(root, CONFIG))
    require(p.digest(spec) == HASH, "Changed acquisition protocol/source/keys/limits")
    return spec


def metadata(root, spec):
    for path, h in spec["preserved_file_byte_sha256"].items():
        require(
            p.file_hash(fixed(root, path)) == h,
            "Historical/prompt/source metadata changed: " + path,
        )
    dependencies.check_dependencies(root, dependencies.load(root))
    require(
        p.runtime_versions() == spec["core_versions"],
        "Pinned native distributions changed",
    )
    api = p.read(root / spec["primary_metadata_path"])
    validate_api(api, spec["source"])
    require(
        p.read(root / "results/evaluation/task0028-three-prong/workflow.json")["status"]
        == "failed_consumed_no_retry",
        "Preserve consumed Task0028",
    )
    return dict(
        status="source_metadata_and_old_bytes_match", operational_numeric_reads=0
    )


def validate_api(api, source):
    entry = next((f for f in api["files"] if f["key"] == source["filename"]), {})
    require(
        api["id"] == source["record_id"]
        and api["metadata"]["doi"] == source["doi"]
        and api["metadata"]["version"] == source["version"]
        and api["metadata"]["license"]["id"] == "cc-by-4.0"
        and entry.get("size") == source["expected_size"]
        and entry.get("checksum") == "md5:" + source["expected_checksum"]
        and entry.get("links", {}).get("self") == source["url"],
        "Primary source/version/size/checksum/URL/license mismatch",
    )


def acceptance(root=ROOT):
    doc = p.read(fixed(root, ACCEPTANCE))
    require(
        doc["task"] == "0029"
        and doc["status"] == "current_source_software_accepted"
        and doc["protocol_canonical_JSON_sha256"] == HASH
        and doc["protocol_file_byte_sha256"] == p.file_hash(root / CONFIG)
        and doc["source_file_sha256"] == source_map(root)
        and doc["full_passed"] == doc["portable_passed"] > 1333
        and doc["quality"]
        == dict(
            lint="passed",
            format="passed",
            dependencies="passed",
            synthetic_integration="passed_guarded_native_metadata_only",
        ),
        "Current own source/protocol/software acceptance required",
    )
    for path, h in doc["validation_evidence_file_byte_sha256"].items():
        require(p.file_hash(fixed(root, path)) == h, "Acceptance evidence changed")
    return doc


def plan(root=ROOT):
    spec = load(root)
    accepted = acceptance(root)
    return dict(
        task="0029",
        specification=spec,
        protocol_canonical_JSON_sha256=HASH,
        software_acceptance_file_byte_sha256=p.file_hash(root / ACCEPTANCE),
        source_file_sha256=accepted["source_file_sha256"],
        readiness=metadata(root, spec),
        scope="one separately authorized byte acquisition session and structural metadata only;no numerical custody/model/science",
    )


def authorization(root=ROOT):
    current = plan(root)
    require(p.read(root / PLAN) == current, "Current stored plan required")
    doc = p.read(fixed(root, AUTHORIZATION))
    prompt = current["specification"]["prompt"]
    require(
        doc
        == dict(
            authority="explicit_human_Task0029_prompt_conditional_execution",
            human_message=(root / prompt["path"]).read_text(),
            prompt_file_byte_sha256=prompt["file_byte_sha256"],
            plan_sha256=p.digest(current),
            software_acceptance_file_byte_sha256=current[
                "software_acceptance_file_byte_sha256"
            ],
            source_file_sha256=current["source_file_sha256"],
            utc=doc["utc"],
            human_approved_exact_postimplementation_hash=False,
            binding="Actual user prompt authorizes conditional implementation/acceptance then one acquisition;no additional general confirmation",
        ),
        "Actual prompt-bound conditional human authorization required",
    )
    return current


def namespace(root=ROOT):
    output, raw = fixed(root, OUTPUT), fixed(root, RAW)
    require(
        not output.exists() and not raw.exists(),
        "Existing/partial/foreign/consumed session refuses new launch;no cross-session resume/reset",
    )
    return output, raw


def disk_space(root, spec):
    need = spec["storage"]["required_free_bytes"]
    available = shutil.disk_usage(root).free
    require(
        available >= need,
        "Insufficient space for three retained representations and bounded journals",
    )
    return dict(required_bytes=need, available_bytes=available)
