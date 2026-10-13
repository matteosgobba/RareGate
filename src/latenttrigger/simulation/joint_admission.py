"""Serialized software verifier → immutable matrix/source freeze → exclusive claim."""

from pathlib import Path

from latenttrigger.simulation import joint_protocol as p
from latenttrigger.simulation.joint_source import Bundle


def freeze(acceptance, base, *, fixture=False, bootstrap=False):
    base = Path(base).absolute()
    p.require(
        (
            base.parent.parent == p.ROOT / p.VALIDATION
            if fixture
            else base.parent == p.ROOT / p.NAMESPACE
        ),
        "Closed Task0044 namespace",
    )
    p.require(not bootstrap or fixture, "Bootstrap generated fixtures only")
    accepted = None if bootstrap else p.verify_acceptance(acceptance)
    if not fixture:
        p.verify_roundtrip(acceptance)
    source_root = base / "sources" if fixture else p.ROOT
    pins = p.read(source_root / "fixture-manifest.json") if fixture else p.PINS
    # Before effects: byte custody only; no timing parsing, no trace generation.
    bundle = Bundle(source_root, pins)
    if not fixture:
        total = bundle.audit["source_bytes"] + sum(
            p.safe(p.ROOT, n).stat().st_size
            for n in p.HISTORICAL_METADATA_PINS
            if n not in pins
        )
        p.require(
            total <= p.LIMITS["source_bundle_bytes"],
            "8MiB timing plus historical metadata byte limit",
        )
        for n, sha in p.HISTORICAL_METADATA_PINS.items():
            p.require(
                p.file_hash(p.safe(p.ROOT, n)) == sha, "Declared original metadata pin"
            )
    plan = dict(
        identity=p.identity(),
        source_map=p.source_map(),
        dependencies=p.dependencies(),
        source_pins=pins,
        historical_metadata_pins={} if fixture else p.HISTORICAL_METADATA_PINS,
        source_root=str(source_root),
        source_bytes=bundle.audit["source_bytes"],
        matrix_sha256=p.digest(p.matrix()),
        expected=p.load_config()["expected"],
        fixture_only=fixture,
        validation_bootstrap=bootstrap,
        software_record=None if accepted is None else str(Path(acceptance).absolute()),
        software_record_sha256=None if accepted is None else p.file_hash(acceptance),
    )
    p.durable_json(base / "plan.json", plan, exclusive=True)
    p.durable_json(
        base / "freeze.json",
        dict(
            task="0044",
            plan_sha256=p.file_hash(base / "plan.json"),
            identity=p.identity(),
            source_map=plan["source_map"],
            dependencies=plan["dependencies"],
        ),
        exclusive=True,
    )
    verify(base, claim=False)
    p.durable_json(
        base / "claim.json",
        dict(
            task="0044",
            freeze_sha256=p.file_hash(base / "freeze.json"),
            plan_sha256=p.file_hash(base / "plan.json"),
            dispatches=1,
        ),
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
    p.require(
        type(fixture) is bool
        and (
            base.parent.parent == p.ROOT / p.VALIDATION
            if fixture
            else base.parent == p.ROOT / p.NAMESPACE
        ),
        "Verified owned namespace",
    )
    p.require(
        plan["identity"] == f["identity"] == p.identity()
        and plan["source_map"] == f["source_map"] == p.source_map()
        and plan["dependencies"] == f["dependencies"] == p.dependencies()
        and f["task"] == "0044"
        and f["plan_sha256"] == p.file_hash(base / "plan.json")
        and plan["matrix_sha256"] == p.digest(p.matrix())
        and plan["expected"] == p.load_config()["expected"],
        "Complete current matrix/source freeze",
    )
    if plan["validation_bootstrap"]:
        p.require(
            fixture
            and plan["software_record"] is None
            and plan["software_record_sha256"] is None,
            "Fixture-only bootstrap",
        )
    else:
        accepted = p.verify_acceptance(plan["software_record"])
        if not fixture:
            p.verify_roundtrip(plan["software_record"])
        p.require(
            p.file_hash(plan["software_record"]) == plan["software_record_sha256"]
            and accepted["status"] == p.STATUS,
            "Frozen serialized acceptance",
        )
    source_root = base / "sources" if fixture else p.ROOT
    p.require(
        plan["source_root"] == str(source_root)
        and plan["source_pins"]
        == (p.read(source_root / "fixture-manifest.json") if fixture else p.PINS),
        "No substituted final source bundle",
    )
    for n, sha in plan["source_pins"].items():
        p.require(
            p.file_hash(p.safe(source_root, n)) == sha, "Frozen timing source bytes"
        )
    p.require(
        plan["historical_metadata_pins"]
        == ({} if fixture else p.HISTORICAL_METADATA_PINS),
        "Closed historical metadata allowlist",
    )
    for n, sha in plan["historical_metadata_pins"].items():
        p.require(
            p.file_hash(p.safe(p.ROOT, n)) == sha, "Frozen historical metadata pin"
        )
    if claim:
        c = p.read(base / "claim.json")
        p.require(
            c
            == dict(
                task="0044",
                freeze_sha256=p.file_hash(base / "freeze.json"),
                plan_sha256=p.file_hash(base / "plan.json"),
                dispatches=1,
            ),
            "Exact owned exclusive claim",
        )
    return plan
