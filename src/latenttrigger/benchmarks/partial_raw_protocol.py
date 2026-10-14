"""Closed Task0045 identity, original custody and authenticated phase authority."""

import os
from dataclasses import dataclass
from pathlib import Path

from latenttrigger.benchmarks import development_decision_protocol as old
from latenttrigger.benchmarks.partial_raw_planning import counts

ROOT = old.ROOT
CONFIG = "configs/benchmarks/development_partial_raw_decision_v1.json"
PROMPT = "docs/prompts/0045-natural-partial-raw-decision-measurement.md"
VALIDATION = "data/task0045-validation"
OUTPUT = "results/benchmarks/task0045-natural-partial-raw-decisions"
CONFIG_HASH = "e233fd10b538afe1b6d80c18938810a65a3f7d45f29467a5eebb3645bc7e22aa"
read, require, fixed, digest, file_hash = (
    old.read,
    old.require,
    old.fixed,
    old.digest,
    old.file_hash,
)
durable_json, dependencies, native_build = (
    old.durable_json,
    old.dependencies,
    old.native_build,
)
hash_raw = old.hash_raw
MEMBERSHIP, RAW, GOLDEN, CACHE = old.MEMBERSHIP, old.RAW, old.GOLDEN, old.CACHE


def load(root=ROOT):
    spec = read(fixed(root, CONFIG))
    require(
        digest(spec) == CONFIG_HASH
        and spec["task"] == spec["validation_owner"] == "0045",
        "Fixed Task0045 protocol",
    )
    require(spec["expected"] == counts(), "Derived paired actual-row budget")
    require(
        spec["authorization_prompt"] == PROMPT
        and spec["authorization_prompt_sha256"] == file_hash(fixed(root, PROMPT)),
        "Exact prospective prompt",
    )
    require(
        all(
            spec[k] == old.load()[k]
            for k in (
                "membership",
                "raw",
                "golden",
                "models",
                "channels",
                "runtime",
                "numerical",
                "cache",
            )
        ),
        "Unchanged source/model/arithmetic/cache identities",
    )
    return spec


def source_map(root=ROOT):
    original = old.source_map(root)
    for name in {
        CONFIG,
        PROMPT,
        "results/tables/final/task0042-development-decision-admission-summary.json",
        "configs/benchmarks/development_raw_decision_v2.json",
        "docs/prompts/0043-development-raw-decision-campaign-v2.md",
        "results/tables/final/task0043-development-raw-decision-summary.json",
        "configs/simulation/joint_service_replay_v1.json",
        "docs/prompts/0044-deterministic-joint-service-replay.md",
        "results/tables/final/task0044-joint-service-replay-summary.json",
    }:
        original[name] = file_hash(fixed(root, name))
    return dict(sorted(original.items()))


def identity(root=ROOT):
    spec = load(root)
    return dict(
        task="0045",
        validation_owner="0045",
        protocol_kind=spec["kind"],
        scope=spec["scope"],
        payload_scope=spec["payload_scope"],
        paired_contract_sha256=digest(
            {k: spec[k] for k in ("cases", "sides", "mapping", "schedule", "gates")}
        ),
        packing="owned_natural_actual_rows_no_dummy",
        config_sha256=file_hash(fixed(root, CONFIG)),
        prompt_sha256=file_hash(fixed(root, PROMPT)),
    )


def history(root=ROOT):
    spec = load(root)
    resolved = {}
    for task, item in spec["historical_acceptances"].items():
        path = fixed(root, item["path"])
        require(file_hash(path) == item["sha256"], "Historical record " + task)
        rows = read(path)["source_map"]
        archived = 0
        for name, sha in rows.items():
            current = fixed(root, name)
            if file_hash(current) != sha:
                current = fixed(
                    root / "data/task0042-validation/preserved-original/issued-source",
                    name,
                )
                archived += 1
            require(
                file_hash(current) == sha, "Original map entry " + task + ":" + name
            )
        resolved[task] = dict(entries=len(rows), preserved_original_entries=archived)
    return resolved


def custody(root=ROOT):
    old.custody(root)  # fixed byte/header/scientific lineage; never old admission/CLI
    for name, sha in load(root)["byte_pins"].items():
        require(
            file_hash(fixed(root, name)) == sha,
            "Task0045 historical/source pin " + name,
        )
    return dict(
        task="0045",
        status="original_byte_header_scientific_lineage_verified",
        original_maps=history(root),
        numerical_loads=0,
        model_instantiations=0,
    )


_SEAL = object()
_PAYLOADS = {}


@dataclass(frozen=True)
class Payload:
    root: Path
    phase: str
    pid: int
    path: str
    prefix: str
    deadline: float
    identity: dict
    synthetic: bool
    seal: object


def consume(base, plan, *, root=ROOT, synthetic=False):
    """Exclusive canonical prerequisite/reservation; fixture roots exercise same branch."""
    marker = (
        base / "fixture-attempt.json" if synthetic else root / OUTPUT / "attempt.json"
    )
    require(plan["identity"] == identity(root), "Reservation task/prompt/config")
    if not synthetic:
        prior = read(fixed(root / OUTPUT, "prerequisite-attempt.json"))
        require(
            prior["task"] == "0045"
            and prior["directory"] == str(base.relative_to(root)),
            "Own consumed prerequisite",
        )
    durable_json(
        marker,
        dict(
            task="0045",
            directory=str(base.relative_to(root)),
            plan_sha256=file_hash(base / "plan.json"),
            prompt_sha256=plan["identity"]["prompt_sha256"],
        ),
        exclusive=True,
    )


def validate_grant(directory, token, clock, *, root=ROOT):
    from latenttrigger.benchmarks import partial_raw_admission as admission
    from latenttrigger.benchmarks.development_decision_native import synthetic_prefix

    directory = Path(directory).absolute()
    base = directory.parent
    grant = read(fixed(directory, "grant.json"))
    plan = read(fixed(base, "plan.json"))
    spec = load(root)
    require(
        directory == directory.resolve()
        and grant["parent_pid"] == os.getppid()
        and grant["token"] == token
        and type(token) is str
        and len(token) == 32,
        "Owned Task0045 parent/token",
    )
    require(
        grant["phase"] in ("repetition1", "repetition2", "repetition3", "reporting")
        and directory.name == grant["phase"]
        and clock() < grant["operation_deadline"],
        "Fixed phase/deadline",
    )
    require(
        grant["identity"] == plan["identity"] == identity(root)
        and grant["task"] == plan["task"] == "0045"
        and plan["kind"]
        == ("synthetic_fixed_matrix" if grant["synthetic_only"] else spec["kind"]),
        "Task/kind/scope/config/prompt grant",
    )
    require(
        type(grant["synthetic_only"]) is bool
        and (
            (grant["synthetic_only"] and base.is_relative_to(root / VALIDATION))
            or (not grant["synthetic_only"] and base.parent == root / OUTPUT)
        ),
        "Closed grant namespace",
    )
    require(
        file_hash(base / "plan.json") == grant["plan_sha256"]
        and grant["source_map"] == plan["source_map"] == source_map(root)
        and grant["dependencies"] == plan["dependencies"] == dependencies()
        and grant["native_build"] == plan["native_build"] == native_build(),
        "Frozen current phase bindings",
    )
    require(
        grant["inputs"]
        == plan["inputs"]
        == {k: spec[k] for k in ("membership", "raw", "golden")}
        and grant["models"] == plan["models"] == spec["models"]
        and grant["expected"] == plan["expected"] == spec["expected"]
        and plan["limits"] == spec["limits"],
        "Exact input/model/threshold/budget grant",
    )
    cap = 60 if grant["phase"] == "reporting" else 180
    require(
        grant["operation_deadline"] == grant["stage_deadline"] - 2
        and 0 < grant["stage_deadline"] - grant["started_continuous"] <= cap
        and grant["stage_deadline"]
        <= plan["reserved_deadline_continuous"]
        <= plan["whole_deadline_continuous"]
        and plan["authorization_prompt_sha256"] == spec["authorization_prompt_sha256"],
        "Fixed continuous stage and prospective authorization bounds",
    )
    expected = directory / "fixture.h5" if grant["synthetic_only"] else root / RAW
    require(
        grant["payload_path"] == str(expected)
        and grant["prefix_sha256"]
        == (
            synthetic_prefix()
            if grant["synthetic_only"]
            else spec["membership"]["selected_sha256"]
        ),
        "Exact payload/prefix",
    )
    if plan["validation_bootstrap"] is False:
        frozen = admission.reload(
            Path(plan["admission_directory"]), admission.Context(root)
        )
        require(
            frozen.freeze_sha256
            == plan["admission_freeze_sha256"]
            == grant["admission_freeze_sha256"]
            and plan["record_sha256"] == grant["record_sha256"] == frozen.record_sha256
            and frozen.mode.value
            == ("synthetic" if grant["synthetic_only"] else "operational"),
            "Independent worker admitted scope/freeze",
        )
        require(
            read(fixed(frozen.directory, "launch-claim.json"))
            == admission.claim_fields(frozen),
            "Independent coordinator claim",
        )
    else:
        require(
            plan["validation_bootstrap"] is True
            and grant["synthetic_only"] is True
            and plan["admission_freeze_sha256"] is None,
            "Only generated validation bootstrap",
        )
    if not grant["synthetic_only"]:
        anchor = read(fixed(root / OUTPUT, "attempt.json"))
        require(
            anchor["task"] == "0045"
            and anchor["directory"] == str(base.relative_to(root))
            and anchor["plan_sha256"] == grant["plan_sha256"],
            "Own one-session anchor",
        )
    durable_json(
        directory / "claim.json",
        dict(
            task="0045",
            pid=os.getpid(),
            token_sha256=old.hashlib.sha256(token.encode()).hexdigest(),
        ),
        exclusive=True,
    )
    permit = Payload(
        root,
        grant["phase"],
        os.getpid(),
        str(expected),
        grant["prefix_sha256"],
        grant["operation_deadline"],
        grant["identity"],
        grant["synthetic_only"],
        _SEAL,
    )
    _PAYLOADS[id(permit)] = permit
    return grant, permit


def verify_payload(permit):
    require(
        isinstance(permit, Payload)
        and permit.seal is _SEAL
        and _PAYLOADS.get(id(permit)) is permit
        and permit.identity == identity(permit.root)
        and permit.pid == os.getpid(),
        "Closed Task0045 payload authority",
    )


STATUS = "software_accepted_synthetic_natural_partial_raw_decision"
ROLE = "task0045_final_source_synthetic_software_validation"
CHECKS = frozenset(
    (
        "focused",
        "full",
        "portable",
        "lint",
        "format",
        "dependencies",
        "native_synthetic",
    )
)
