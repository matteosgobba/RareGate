"""Strict Phase A/B metadata, frozen plan and human-consent audit binding."""

from raregate.benchmarks import protocol as p
from raregate.benchmarks import pytorch_onnx_cpu_protocol as prior
from raregate.exports import onnx_protocol as deps

ROOT = p.ROOT
CONFIG = "configs/evaluation/frozen_pca_ae_final_v1.json"
HASH = "be7c18a5ea0bed3cafc2083d3592814d315cbfddedf71a59781a82aa2ff82d3f"
OUTPUT = "results/evaluation/task0026-frozen-pca-ae"
ACCEPTANCE = "data/task0026-software-acceptance.json"
PLAN = "data/task0026-evaluation-plan.json"
CONSENT = "data/task0026-human-authorization.json"
CANDIDATES = ("PCA", "AE")
POPULATIONS = (("test_background", 150471, 0), ("test_signal", 100000, 1))
fixed = prior.fixed
source_map = prior.source_map


def load(root=ROOT):
    spec = p.read(root / CONFIG)
    if p.digest(spec) != HASH:
        raise ValueError(
            "Unsupported strict evaluation protocol/keys/candidate/path override."
        )
    return spec


def metadata(root, spec):
    prior.metadata(root, prior.load(root))
    deps.check_dependencies(root, deps.load(root))
    for name, digest in spec["historical_full_custody"][
        "receipt_lineage_file_byte_sha256"
    ].items():
        if p.file_hash(root / name) != digest:
            raise ValueError("Historical full custody lineage changed.")
    for key in ("prior_source_file_sha256", "prior_evidence_file_sha256"):
        for name, h in spec[key].items():
            if p.file_hash(fixed(root, name)) != h:
                raise ValueError("Preserved evidence/source identity changed: " + name)
    if p.file_hash(root / spec["prompt"]["path"]) != spec["prompt"]["file_byte_sha256"]:
        raise ValueError("Actual prompt identity mismatch.")
    store = spec["store"]
    path = fixed(root, store["path"])
    for name, h in store["metadata_file_byte_sha256"].items():
        if p.file_hash(path / name) != h:
            raise ValueError("Full-store metadata byte mismatch.")
    doc = p.read(path / "manifest.json")
    science = doc["scientific"]
    config = p.read(path / "configuration.json")
    if (
        doc["scientific_sha256"] != store["scientific_sha256"]
        or p.digest(science) != doc["scientific_sha256"]
        or p.digest(config) != store["configuration_canonical_JSON_sha256"]
        or p.file_hash(path / "configuration.json") != science["config_sha256"]
        or science["scope"] != "full"
        or p.digest(science["split_identity"]) != store["split_identity_sha256"]
        or science["aggregate_channels"] != spec["features"]
        or science["counts"] != store["counts"]
    ):
        raise ValueError(
            "Full store/scaler/split/features scientific identity mismatch."
        )
    for entry in spec["candidates"]:
        documents = {}
        for kind in ("config", "model", "results"):
            file = fixed(root, entry[kind + "_path"])
            if p.file_hash(file) != entry[kind + "_file_sha256"]:
                raise ValueError("Frozen candidate/calibration file byte mismatch.")
            documents[kind] = p.read(file)
        if p.digest(documents["config"]) != entry["config_canonical_sha256"]:
            raise ValueError("Frozen config canonical JSON mismatch.")
        for kind in ("model", "results"):
            d = documents[kind]
            if (
                p.digest(d["scientific"]) != d["scientific_sha256"]
                or d["scientific_sha256"] != entry[kind + "_scientific_sha256"]
            ):
                raise ValueError("Frozen scientific candidate/calibration mismatch.")
        art = documents["model"]["scientific"]
        cal = documents["results"]["scientific"]
        prov = art["provenance"]
        if (
            cal["model_scientific_sha256"] != entry["model_scientific_sha256"]
            or cal["provenance"] != prov
            or prov["processed_scientific_sha256"] != store["scientific_sha256"]
            or prov["model_config"] != documents["config"]
            or prov["model_config_sha256"] != entry["config_canonical_sha256"]
            or art["features"] != spec["features"]
            or documents["config"]["batch_events"] != 4096
            or [
                {"target_fpr": t["target_fpr"], "threshold": t["threshold"]}
                for t in cal["thresholds"]
            ]
            != entry["thresholds"]
        ):
            raise ValueError(
                "Frozen provenance/feature/batch/threshold relationship mismatch."
            )
    return dict(
        metadata_verified=True,
        full_payload_verified=False,
        population_requests=0,
        store_scientific_sha256=store["scientific_sha256"],
    )


def acceptance(root=ROOT):
    a = p.read(root / ACCEPTANCE)
    if (
        a.get("task") != "0026"
        or a.get("protocol_canonical_JSON_sha256") != HASH
        or a.get("protocol_file_byte_sha256") != p.file_hash(root / CONFIG)
        or a.get("source_file_sha256") != source_map(root)
        or type(a.get("full_passed")) is not int
        or a["full_passed"] <= 1179
        or a.get("portable_passed") != a["full_passed"]
        or a.get("quality")
        != dict(
            lint="passed",
            format="passed",
            dependencies="passed",
            synthetic_integration="passed_actual_native",
        )
        or a.get("guarded_smoke", {}).get("status") != "parent_accepted"
    ):
        raise ValueError(
            "Current complete evaluation software/source acceptance required."
        )
    for v in a["validation_evidence"]:
        if p.file_hash(root / v["path"]) != v["file_byte_sha256"]:
            raise ValueError("Acceptance evidence drift.")
    return a


def plan(root=ROOT):
    spec = load(root)
    a = acceptance(root)
    metadata(root, spec)
    return dict(
        schema_version=1,
        task="0026",
        protocol_canonical_JSON_sha256=HASH,
        software_acceptance_file_byte_sha256=p.file_hash(root / ACCEPTANCE),
        source_file_sha256=a["source_file_sha256"],
        candidates=spec["candidates"],
        store=spec["store"],
        features=spec["features"],
        execution_order=list(CANDIDATES),
        batch_size=4096,
        populations=spec["populations"],
        metrics=spec["metrics"],
        limits=spec["limits"],
        output=OUTPUT + "/final",
        authorization_required=True,
        passes_per_candidate=1,
        no_post_test_training_or_selection=True,
    )


def authorization(root, *, allow_test, approved_plan_sha256):
    if allow_test is not True:
        raise ValueError(
            "Test embargo: explicit --allow-test and human authorization required before reservation."
        )
    current = plan(root)
    if p.digest(current) != approved_plan_sha256:
        raise ValueError("Approved plan/source identities changed.")
    stored = p.read(root / PLAN)
    if stored != current:
        raise ValueError("Reviewable plan changed; new review required.")
    consent = p.read(root / CONSENT)
    expected = {
        "authority",
        "human_message",
        "utc",
        "approved_plan_canonical_JSON_sha256",
        "software_acceptance_file_byte_sha256",
        "source_file_sha256",
        "candidates",
        "events_per_candidate",
        "passes_per_candidate",
        "no_post_test_training_or_selection",
    }
    if (
        set(consent) != expected
        or consent["authority"] != "explicit_human_user_message"
        or not isinstance(consent["human_message"], str)
        or not consent["human_message"].strip()
        or consent["approved_plan_canonical_JSON_sha256"] != approved_plan_sha256
        or consent["software_acceptance_file_byte_sha256"]
        != current["software_acceptance_file_byte_sha256"]
        or consent["source_file_sha256"] != current["source_file_sha256"]
        or consent["candidates"] != ["pca-v1", "compact-autoencoder-v2"]
        or consent["events_per_candidate"]
        != {"test_background": 150471, "test_signal": 100000}
        or type(consent["passes_per_candidate"]) is not int
        or consent["passes_per_candidate"] != 1
        or consent["no_post_test_training_or_selection"] is not True
    ):
        raise ValueError("Explicit human authorization audit/identity/scope mismatch.")
    # This is an audit binding, not a mechanism for deriving human consent. Only
    # create CONSENT after the actual user approves the presented current plan.
    return consent, current
