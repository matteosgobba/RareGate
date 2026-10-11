"""Separate Task0030 frozen software/protocol/authorization and prefix lineage."""

import json
import shutil

from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.frozen_cpu_v2_protocol import fixed
from latenttrigger.data import three_prong_acquisition_protocol as old
from latenttrigger.data.three_prong_v3_runtime import check_deadline
from latenttrigger.data.three_prong_v3_transport import hash_bytes

ROOT, require, source_map = p.ROOT, old.require, old.source_map
CONFIG = "configs/acquisition/three_prong_v3.json"
HASH = "268b946af53f3d907ca6153363874b2fae2b3221b2165d83e55184b612862043"
OUTPUT = "results/acquisition/task0030-three-prong"
RAW = "data/task0030-three-prong-acquisition"
ACCEPTANCE = "data/task0030-software-acceptance.json"
PLAN = "data/task0030-acquisition-plan.json"
AUTHORIZATION = "data/task0030-human-authorization.json"
PHASES = ("import", "transfer", "verify")


def load(root=ROOT):
    spec = p.read(fixed(root, CONFIG))
    require(p.digest(spec) == HASH, "Changed Task0030 protocol/source/limits/keys")
    return spec


def metadata(root, spec, *, clock, deadline):
    for name, sha in spec["preserved_file_byte_sha256"].items():
        check_deadline(clock, deadline)
        require(
            p.file_hash(fixed(root, name)) == sha, "Historical bytes changed: " + name
        )
    old.dependencies.check_dependencies(root, old.dependencies.load(root))
    require(p.runtime_versions() == spec["core_versions"], "Native versions changed")
    old.validate_api(p.read(root / spec["primary_metadata_path"]), spec["source"])
    require(
        p.read(root / old.OUTPUT / "parent-acceptance.json")["status"]
        == "failed_consumed_preserved",
        "Task0029 remains failed/consumed",
    )
    check_deadline(clock, deadline)
    return dict(
        status="preserved_old146_sources_receipts_dependencies_source_match",
        numerical_reads=0,
    )


def prefix(root, spec, *, clock, deadline, boundary=lambda: None):
    pin = spec["prefix"]
    path = fixed(root, pin["path"])
    actual = hash_bytes(path, clock=clock, deadline=deadline, boundary=boundary)
    require(
        actual == {k: pin[k] for k in ("bytes", "MD5", "SHA256")},
        "Historical prefix byte mismatch;no zero fallback",
    )
    s = path.lstat()
    progress = p.read(root / old.OUTPUT / "transfer/progress.json")
    require(
        progress["source"] == spec["source"]
        and progress["status"] == "failed_preserved",
        "Prefix source/status mismatch",
    )
    file = next(f for f in progress["files"] if f["name"] == path.name)
    require(
        (
            file["device"],
            file["inode"],
            file["written_bytes"],
            file["durable_bytes"],
            file["durable_prefix_SHA256"],
        )
        == (s.st_dev, s.st_ino, pin["bytes"], pin["bytes"], pin["SHA256"]),
        "Prefix checkpoint inode/size/hash lineage mismatch",
    )
    journal = root / old.OUTPUT / "transfer/checkpoints.jsonl"
    require(
        journal.stat().st_size <= 8 * 2**20, "Unbounded historical checkpoint metadata"
    )
    last = None
    with journal.open() as stream:
        for line in stream:
            check_deadline(clock, deadline)
            require(len(line.encode()) <= 65536, "Unbounded checkpoint record")
            last = json.loads(line)
    require(
        last["current_file"] == file
        and last["durable"] == pin["bytes"]
        and last["source_canonical_JSON_sha256"] == p.digest(spec["source"]),
        "Final checkpoint lineage mismatch",
    )
    workflow = p.read(root / old.OUTPUT / "workflow.json")
    dispatch = p.read(root / old.OUTPUT / "transfer/dispatch.json")
    inventory = next(f for f in workflow["retained_files"] if f["name"] == path.name)
    require(
        dispatch["child_reaped"] is True
        and inventory["byte_integrity"] == actual
        and inventory["retained_bytes_after_reaping"] == pin["bytes"]
        and inventory["accepted_verified_bytes"] == 0,
        "Post-reaping prefix inventory mismatch",
    )
    return dict(
        **actual,
        device=s.st_dev,
        inode=s.st_ino,
        path=pin["path"],
        response_headers=progress["requests"][-1]["response_headers"],
        checkpoint_file_byte_sha256=p.file_hash(journal),
        parent_inventory_file_byte_sha256=p.file_hash(
            root / old.OUTPUT / "workflow.json"
        ),
        status="verified_historical_partial_only_not_complete_integrity",
    )


def acceptance(root=ROOT):
    doc = p.read(fixed(root, ACCEPTANCE))
    require(
        doc["task"] == "0030"
        and doc["status"] == "current_source_software_accepted"
        and doc["protocol_canonical_JSON_sha256"] == HASH
        and doc["protocol_file_byte_sha256"] == p.file_hash(root / CONFIG)
        and doc["source_file_sha256"] == source_map(root)
        and doc["full_passed"] == doc["portable_passed"] > 1414
        and doc["quality"]
        == dict(
            lint="passed",
            format="passed",
            dependencies="passed",
            synthetic_integration="passed_continuous_supervised_native_metadata_only",
            native_bindings="passed_continuous_assertion_creation_and_release",
        ),
        "Current v3 own acceptance required;old acceptance never covers v3",
    )
    for name, sha in doc["validation_evidence_file_byte_sha256"].items():
        require(p.file_hash(fixed(root, name)) == sha, "Validation evidence changed")
    return doc


def plan(root=ROOT):
    spec, accepted = load(root), acceptance(root)
    return dict(
        task="0030",
        specification=spec,
        protocol_canonical_JSON_sha256=HASH,
        software_acceptance_file_byte_sha256=p.file_hash(root / ACCEPTANCE),
        source_file_sha256=accepted["source_file_sha256"],
        scope="one sleep-aware byte acquisition from verified copied prefix;bounded structural metadata only;no numerical/scientific execution",
    )


def authorization(root=ROOT):
    current = plan(root)
    require(p.read(root / PLAN) == current, "Stored current plan required")
    doc = p.read(fixed(root, AUTHORIZATION))
    prompt = current["specification"]["prompt"]
    require(
        doc
        == dict(
            authority="explicit_human_Task0030_prompt_conditional_execution",
            human_message=(root / prompt["path"]).read_text(),
            prompt_file_byte_sha256=prompt["file_byte_sha256"],
            plan_sha256=p.digest(current),
            software_acceptance_file_byte_sha256=current[
                "software_acceptance_file_byte_sha256"
            ],
            source_file_sha256=current["source_file_sha256"],
            UTC=doc["UTC"],
            human_approved_exact_postimplementation_hash=False,
        ),
        "Actual prompt-bound conditional authorization required",
    )
    return current


def namespace(root=ROOT):
    output, raw = fixed(root, OUTPUT), fixed(root, RAW)
    require(
        not output.exists() and not raw.exists(),
        "Task0030 namespace exists/consumed/foreign;no second session",
    )
    return output, raw


def disk_space(root, spec):
    s = spec["storage"]
    budget = (
        7 * spec["source"]["expected_size"]
        + 3 * 64 * 2**20
        + 8 * 2**20
        + s["logs_bytes"]
        + s["metadata_slack_bytes"]
    )
    require(
        budget <= s["required_free_bytes"] == 2 * 2**30,
        "Storage accounting inconsistent",
    )
    available = shutil.disk_usage(root).free
    require(available >= s["required_free_bytes"], "At least2GiB free required")
    return dict(
        required_bytes=s["required_free_bytes"],
        worst_case_retained_and_journal_bytes=budget,
        available_bytes=available,
    )
