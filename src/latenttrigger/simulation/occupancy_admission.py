"""Separate Task0046 immutable freeze/claim; no timing source open during freeze."""

from pathlib import Path

from latenttrigger.simulation import occupancy_protocol as p


def location(base, fixture):
    p.require(
        type(fixture) is bool
        and (
            base.parent.parent == p.ROOT / p.VALIDATION
            if fixture
            else base.parent == p.ROOT / p.NAMESPACE
        )
        and len(base.name) == 32
        and all(c in "0123456789abcdef" for c in base.name),
        "Closed Task0046 namespace",
    )


def freeze(acceptance, base, *, fixture=False, bootstrap=False):
    base = Path(base).absolute()
    location(base, fixture)
    p.require(
        type(bootstrap) is bool and (not bootstrap or fixture), "Fixture bootstrap only"
    )
    accepted = None if bootstrap else p.verify_acceptance(acceptance)
    if not fixture:
        p.verify_roundtrip(acceptance)
    manifest = (
        p.read(base / "sources/fixture-manifest.json") if fixture else p.SOURCE_MANIFEST
    )
    p.require(set(manifest) == set(p.SOURCE_MANIFEST), "Closed timing manifest")
    plan = dict(
        identity=p.identity(),
        source_map=p.source_map(),
        dependencies=p.dependencies(),
        source_manifest=manifest,
        source_root=str(base / "sources" if fixture else p.ROOT),
        matrix_sha256=p.digest(p.matrix()),
        expected=p.planner(),
        limits=p.LIMITS,
        fixture_only=fixture,
        validation_bootstrap=bootstrap,
        software_record=None if accepted is None else str(Path(acceptance).absolute()),
        software_record_sha256=None if accepted is None else p.file_hash(acceptance),
        authorization_prompt_sha256=p.identity()["prompt_sha256"],
    )
    p.durable_json(base / "plan.json", plan, exclusive=True)
    p.durable_json(
        base / "freeze.json",
        dict(
            task="0046",
            identity=p.identity(),
            plan_sha256=p.file_hash(base / "plan.json"),
            source_map=plan["source_map"],
            dependencies=plan["dependencies"],
        ),
        exclusive=True,
    )
    verify(base, claim=False)
    claim = dict(
        task="0046",
        identity=p.identity(),
        freeze_sha256=p.file_hash(base / "freeze.json"),
        plan_sha256=p.file_hash(base / "plan.json"),
        dispatches=1,
        fixture_only=fixture,
    )
    p.durable_json(base / "claim.json", claim, exclusive=True)
    if not fixture:
        # Consumed before operational timing-byte access, never retry or reset.
        p.durable_json(
            p.ROOT / p.NAMESPACE / "attempt.json",
            dict(claim, directory=str(base.relative_to(p.ROOT))),
            exclusive=True,
        )
    verify(base)
    return plan


def verify(base, *, claim=True):
    base = Path(base).absolute()
    p.safe(p.ROOT, str((base / "plan.json").relative_to(p.ROOT)))
    plan = p.read(base / "plan.json")
    f = p.read(base / "freeze.json")
    fixture = plan["fixture_only"]
    location(base, fixture)
    p.require(
        plan["identity"] == f["identity"] == p.identity()
        and plan["source_map"] == f["source_map"] == p.source_map()
        and plan["dependencies"] == f["dependencies"] == p.dependencies()
        and f["task"] == "0046"
        and f["plan_sha256"] == p.file_hash(base / "plan.json")
        and plan["matrix_sha256"] == p.digest(p.matrix())
        and plan["expected"] == p.planner() == p.load_config()["expected"]
        and plan["limits"] == p.LIMITS
        and plan["authorization_prompt_sha256"] == p.identity()["prompt_sha256"],
        "Complete current freeze",
    )
    if plan["validation_bootstrap"]:
        p.require(
            plan["validation_bootstrap"] is True
            and fixture
            and plan["software_record"] is None
            and plan["software_record_sha256"] is None,
            "Generated bootstrap only",
        )
    else:
        p.require(plan["validation_bootstrap"] is False, "Typed bootstrap flag")
        p.verify_acceptance(plan["software_record"])
        if not fixture:
            p.verify_roundtrip(plan["software_record"])
        p.require(
            p.file_hash(plan["software_record"]) == plan["software_record_sha256"],
            "Immutable emitted acceptance",
        )
    p.require(
        plan["source_root"] == str(base / "sources" if fixture else p.ROOT)
        and plan["source_manifest"]
        == (
            p.read(base / "sources/fixture-manifest.json")
            if fixture
            else p.SOURCE_MANIFEST
        ),
        "No source substitution",
    )
    if claim:
        expected = dict(
            task="0046",
            identity=p.identity(),
            freeze_sha256=p.file_hash(base / "freeze.json"),
            plan_sha256=p.file_hash(base / "plan.json"),
            dispatches=1,
            fixture_only=fixture,
        )
        p.require(p.read(base / "claim.json") == expected, "Exact exclusive claim")
        if not fixture:
            p.require(
                p.read(p.ROOT / p.NAMESPACE / "attempt.json")
                == dict(expected, directory=str(base.relative_to(p.ROOT))),
                "Owned consumed allowance",
            )
    return plan
