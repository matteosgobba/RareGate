"""Task0031 self-contained parser/precision/scoring/metrics/custody/lifecycle tests."""

import h5py
import numpy as np
import pytest

from latenttrigger.benchmarks import protocol as p
from latenttrigger.data.features import (
    Parameters,
    canonicalize,
    physical_aggregates,
    standardized_aggregates,
)
from latenttrigger.data.inspection import event_fingerprints
from latenttrigger.data.three_prong_v3_runtime import check_deadline
from latenttrigger.evaluation import local_three_prong as controller
from latenttrigger.evaluation import local_three_prong_core as n
from latenttrigger.evaluation import local_three_prong_protocol as q
from latenttrigger.evaluation import local_three_prong_worker as worker
from latenttrigger.evaluation.guard import GuardError
from latenttrigger.evaluation.local_three_prong_audit import Audit, exposure
from latenttrigger.evaluation.metrics import at_threshold, evaluate_scores
from latenttrigger.evaluation.thresholds import efficiency


class Clock:
    def __init__(self):
        self.t = 0.0
        self.ordinary = 0.0

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


class Guard:
    def __init__(self):
        self.clock = Clock()
        self.deadline = 1000

    def check(self):
        check_deadline(self.clock, self.deadline)

    def boundary(self, *args):
        self.check()


@pytest.fixture
def params():
    return Parameters.from_config(p.read(p.ROOT / "configs/data/lhco_rnd_v5.json"))


def rows(count=4):
    x = np.zeros((count, 2101), np.float64)
    for i in range(count):
        x[i, :6] = [1 + i, 0.2, 0.3, 1.0, -0.1, -0.4]
    x[:, -1] = 1
    return x


def make_hdf(path, values):
    with h5py.File(path, "w") as h:
        h.create_dataset("/df/block0_values", data=values)
        for key in ["axis0", "block0_items"]:
            h.create_dataset("/df/" + key, data=np.arange(values.shape[1]))
        h.create_dataset("/df/axis1", data=np.arange(len(values)))
    return path


@pytest.mark.parametrize(
    "bad",
    [
        "width2100",
        "width2102",
        "float32",
        "axis_order",
        "item_order",
        "extra",
        "soft",
        "external",
        "row_axis",
        "root_soft",
    ],
)
def test_exact_parser_refuses(tmp_path, bad):
    path = make_hdf(tmp_path / "toy.h5", rows())
    with h5py.File(path, "a") as h:
        if bad in ("width2100", "width2102", "float32"):
            del h["/df/block0_values"]
            h.create_dataset(
                "/df/block0_values",
                data=np.zeros(
                    (
                        4,
                        2100
                        if bad == "width2100"
                        else 2102
                        if bad == "width2102"
                        else 2101,
                    ),
                    np.float32 if bad == "float32" else np.float64,
                ),
            )
        if bad == "axis_order":
            h["/df/axis0"][0] = 7
        if bad == "item_order":
            h["/df/block0_items"][0] = 7
        if bad == "extra":
            h.create_dataset("/df/extra", data=[1])
        if bad in ("soft", "external"):
            del h["/df/axis0"]
            h["/df/axis0"] = (
                h5py.SoftLink("/df/block0_items")
                if bad == "soft"
                else h5py.ExternalLink("forbidden.h5", "/x")
            )
        if bad == "row_axis":
            del h["/df/axis1"]
            h.create_dataset("/df/axis1", data=np.arange(3))
        if bad == "root_soft":
            h.move("df", "other")
            h["df"] = h5py.SoftLink("/other")
    with h5py.File(path, "r") as h:
        with pytest.raises(ValueError):
            n.hdf_layout(h, 4)


def test_axes_numeric_accounting(tmp_path):
    path = make_hdf(tmp_path / "toy.h5", rows())
    audit = Audit(tmp_path / "audit.json", dict(synthetic=True))
    with h5py.File(path, "r") as h:
        assert n.hdf_layout(h, 4, audit).shape == (4, 2101)
    assert [r["confirmed_read"] for r in audit.document["records"]] == [2101, 2101]


@pytest.mark.parametrize(
    "bad",
    [
        "label0",
        "label2",
        "labelnan",
        "nan",
        "inf",
        "negative",
        "malformed",
        "nontrailing",
        "empty",
        "overflow",
    ],
)
def test_validity_and_padding_no_filter(params, bad):
    x = rows(1)
    if bad == "label0":
        x[0, -1] = 0
    if bad == "label2":
        x[0, -1] = 2
    if bad == "labelnan":
        x[0, -1] = np.nan
    if bad == "nan":
        x[0, 1] = np.nan
    if bad == "inf":
        x[0, 1] = np.inf
    if bad == "negative":
        x[0, 0] = -1
    if bad == "malformed":
        x[0, 6:9] = [0, 1, 0]
    if bad == "nontrailing":
        x[0, 9:12] = [1, 0, 0]
    if bad == "empty":
        x[0, :2100] = 0
    if bad == "overflow":
        x[0, 0] = 1e40
    with pytest.raises(ValueError):
        n.frozen_features(x, params)


def test_exact_physical_precision_sequence(params):
    x = rows(2)
    x[0, 0] = 1.0000000763
    x[0, 1] = 0.200000019
    actual, fp, _ = n.frozen_features(x, params)
    particles = x[:, :2100].reshape(-1, 700, 3)
    expected = standardized_aggregates(
        physical_aggregates(canonicalize(particles).padded), params
    )
    assert np.array_equal(actual, expected) and actual.dtype == np.float32
    assert np.array_equal(fp, event_fingerprints(particles))


def test_aggregate_before_object_truncation(params):
    x = rows(1)
    x[0, :2100] = np.tile([1.0, 0.1, 0.2], 700)
    actual, _, _ = n.frozen_features(x, params)
    truncated = x.copy()
    truncated[0, 384 * 3 : 2100] = 0
    altered, _, _ = n.frozen_features(truncated, params)
    assert not np.array_equal(actual, altered)


def test_fingerprint_raw_precision_not_rounded_features(params):
    x = rows(2)
    x[1] = x[0]
    x[0, 0] = 1.00000001
    x[1, 0] = 1.00000002
    features, fp, _ = n.frozen_features(x, params)
    assert np.array_equal(features[0], features[1]) and fp[0] != fp[1]


def test_signed_zero_phi_order_fingerprint():
    x = np.array(
        [[[1.0, 0.0, 0.0], [2.0, 0.1, 0.2]], [[2.0, 0.1, 0.2], [1.0, -0.0, 2 * np.pi]]]
    )
    assert event_fingerprints(x)[0] == event_fingerprints(x)[1]


@pytest.mark.parametrize(
    "duplicate,overlap", [(False, False), (True, False), (False, True), (True, True)]
)
def test_exact_all_role_overlap(duplicate, overlap):
    original = np.array([bytes([i]) * 32 for i in range(5)], dtype="V32")
    new = np.array(
        [
            b"a" * 32,
            b"a" * 32 if duplicate else b"b" * 32,
            original[-1].tobytes() if overlap else b"c" * 32,
        ],
        dtype="V32",
    )
    result = n.check_overlap(new, original)
    assert result["within_source_duplicates"] == int(duplicate) and result[
        "original_overlap_count"
    ] == int(overlap)
    assert result["all_original_roles_checked"]


class Model:
    def __init__(self, mode="ok"):
        self.calls = []
        self.mode = mode

    def score(self, x, feature_names):
        self.calls.append(len(x))
        out = np.zeros(len(x), np.float64)
        if self.mode == "negative":
            out[:] = -1
        if self.mode == "nonfinite":
            out[:] = np.nan
        if self.mode == "float32":
            out = out.astype(np.float32)
        if self.mode == "shape":
            out = out[:, None]
        if self.mode == "interrupt":
            raise KeyboardInterrupt("synthetic scoring interruption")
        return out


@pytest.mark.parametrize("count", [1, 4095, 4096, 4097, 100000])
def test_complete_canonical_tail_exactly_once(tmp_path, count):
    audit = Audit(tmp_path / "audit.json", dict(synthetic=True))
    row = audit.request("signal_model_evaluation", count)
    model = Model()
    out = n.score_batches(
        model, np.zeros((count, 8), np.float32), audit, row, Guard(), count
    )
    expected = [4096] * (count // 4096) + ([count % 4096] if count % 4096 else [])
    assert (
        model.calls == row["batches"] == expected
        and len(out) == row["confirmed_scored"] == row["confirmed_read"] == count
    )
    assert exposure(tmp_path / "audit.json")["signal_model_requests"] == 1


@pytest.mark.parametrize(
    "mode", ["negative", "nonfinite", "float32", "shape", "interrupt"]
)
def test_invalid_or_interrupted_score_retains_inflight(tmp_path, mode):
    audit = Audit(tmp_path / "audit.json", dict(synthetic=True))
    row = audit.request("signal_model_evaluation", 4)
    with pytest.raises((ValueError, KeyboardInterrupt)):
        n.score_batches(
            Model(mode), np.zeros((4, 8), np.float32), audit, row, Guard(), 4
        )
    d = exposure(tmp_path / "audit.json")
    assert (
        d["new_signal_model_accessed"]
        and d["potential_inflight"]
        and d["signal_scored_presentations"] == 0
    )


def test_suspend_before_sensitive_read(tmp_path):
    audit = Audit(tmp_path / "audit.json", dict(synthetic=True))
    row = audit.request("signal_model_evaluation", 4)
    g = Guard()
    g.clock.advance(1001)
    model = Model()
    with pytest.raises(GuardError):
        n.score_batches(model, np.zeros((4, 8), np.float32), audit, row, g, 4)
    assert not model.calls and g.clock.ordinary == 0


@pytest.mark.parametrize(
    "bg,sig,expected",
    [(0, 0, (None, None)), (0, 2, (None, 1.0)), (2, 0, (0.0, 0.0)), (2, 3, (1.5, 0.6))],
)
def test_preregistered_arithmetic_undefined(bg, sig, expected):
    r = n.arithmetic(
        dict(accepted=bg, efficiency=bg / 10), dict(accepted=sig, efficiency=sig / 10)
    )
    assert r["relative_acceptance"] == (
        pytest.approx(expected[0]) if expected[0] is not None else None
    )
    assert r["selected_signal_fraction"] == (
        pytest.approx(expected[1]) if expected[1] is not None else None
    )


@pytest.mark.parametrize("threshold", [0.0, 1.0, 2.0, 3.0])
def test_strict_equal_scores_rejected(threshold):
    s = np.array([threshold, threshold + 1, threshold - 1])
    assert efficiency(s, threshold)["accepted"] == 1


def test_ties_plateaus_no_interpolation():
    bg = np.array([0.0, 1.0, 1.0, 2.0])
    sig = np.array([1.0, 1.0, 3.0, 3.0])
    m = evaluate_scores(
        bg, sig, fixed_fprs=[0.0, 0.25, 0.5], fixed_tprs=[0.5, 0.8, 0.9]
    )
    for point in m["at_fixed_fpr"]:
        assert point["background"]["efficiency"] <= point["target_fpr"]
        threshold = (
            np.inf if point["threshold_kind"] == "accept_none" else point["threshold"]
        )
        assert point["signal"] == at_threshold(bg, sig, threshold)["signal"]
    assert m["signal_prevalence"] == 0.5


def test_wilson_conventions_zero_tail():
    r = efficiency(np.zeros(100), 1.0)
    assert r["accepted"] == 0 and 0 <= r["wilson_95"][0] < r["wilson_95"][1] < 0.1
    assert r["resolution"] == 0.01


@pytest.mark.parametrize(
    "kind",
    [
        "raw_custody",
        "original_fingerprint_integrity",
        "cached_background_numeric_reuse",
        "candidate_constructor_provenance",
        "reporting_owned_curves",
    ],
)
def test_preopen_durable_and_duplicate_refusal(tmp_path, kind):
    audit = Audit(tmp_path / "audit.json", dict(synthetic=True))
    r = audit.request(kind, 3, source="toy")
    saved = p.read(tmp_path / "audit.json")
    assert saved["records"][0]["inflight"] == "before_open"
    with pytest.raises(ValueError):
        audit.request(kind, 3)
    audit.read(r, 3)
    assert p.read(tmp_path / "audit.json")["records"][0]["inflight"] is None


def test_unknown_access_refused(tmp_path):
    with pytest.raises(ValueError):
        Audit(tmp_path / "audit.json", {}).request("download", 1)


def test_no_operational_network_fit_paths():
    import ast

    code = (
        p.ROOT / "src/latenttrigger/evaluation/local_three_prong_core.py"
    ).read_text()
    tree = ast.parse(code)
    forbidden = {
        "acquire",
        "fit",
        "backward",
        "step",
        "calibrate_thresholds",
        "iter_features",
    }
    calls = [
        node.func.attr
        if isinstance(node.func, ast.Attribute)
        else node.func.id
        if isinstance(node.func, ast.Name)
        else ""
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    ]
    assert not set(calls) & forbidden


@pytest.mark.parametrize("phase", q.PHASES)
def test_late_body_receipt_rejected_before_outputs(tmp_path, phase):
    c = Clock()
    c.advance(20)
    with pytest.raises(GuardError):
        controller.accepted_stage(tmp_path, phase, {}, {}, {}, c, 10)


@pytest.mark.parametrize("path", [q.OUTPUT, "data/task0031-three-prong"])
def test_foreign_consumed_namespace(tmp_path, path):
    (tmp_path / path).mkdir(parents=True)
    with pytest.raises(ValueError):
        q.namespace(tmp_path)


def test_frozen_scope_counts_paths():
    spec = q.load()
    assert spec["limits"]["chunk_rows"] == 992 and spec["encoding"]["widths"] == [2101]
    assert spec["expected_access"]["signal_score_batches"] == [4096] * 24 + [1696]
    assert spec["expected_access"]["signal_scored_presentations"] == 200000
    assert spec["expected_access"]["cached_background_numeric_loads"] == 2
    assert (
        spec["limits"]["whole_seconds"] == 600
        and "acquire_seconds" not in spec["limits"]
    )


def test_all_exposure_missing_preserves_original_yes(tmp_path):
    r = controller.campaign_exposure(tmp_path)
    assert (
        r["original_test_background_model_accessed"]
        and r["original_test_signal_model_accessed"]
    )
    assert (
        not r["new_three_prong_model_accessed"]
        and r["signal_scored_presentations"] == 0
    )


def test_publication_late_rejects(tmp_path, monkeypatch):
    base = tmp_path / q.OUTPUT
    base.mkdir(parents=True)
    c = Clock()
    monkeypatch.setattr(controller.q, "source_map", lambda root: {})
    write = controller.durable

    def delayed(path, doc):
        write(path, doc)
        if path.name == "parent-acceptance.json":
            c.advance(20)

    monkeypatch.setattr(controller, "durable", delayed)
    outcome = dict(
        status="parent_accepted", sleep_assertion=dict(released=True), exposure={}
    )
    controller.publish(tmp_path, outcome, c, 10)
    assert outcome["status"] == "failed_consumed_no_retry"


def test_assertion_monitor_lost_before_accounting(monkeypatch):
    c = Clock()
    grant = dict(
        parent_pid=1,
        sleep_helper_pid=2,
        sleep_assertion_id="abc",
        operation_deadline_continuous=10,
    )
    monkeypatch.setattr(worker.os, "kill", lambda *args: None)
    monkeypatch.setattr(
        worker.AssertionMonitor.__module__
        and __import__(
            "latenttrigger.data.three_prong_v3_worker", fromlist=["subprocess"]
        ).subprocess,
        "check_output",
        lambda *args, **kwargs: "",
    )
    with pytest.raises(GuardError):
        worker.AssertionMonitor(grant, c).check()


@pytest.fixture
def acquisition_lineage(tmp_path, monkeypatch):
    import hashlib

    monkeypatch.setattr(
        q, "scientific_metadata", lambda *args: dict(status="synthetic_metadata_only")
    )
    raw = tmp_path / "local.h5"
    raw.write_bytes(b"synthetic byte artifact")
    value = dict(
        bytes=raw.stat().st_size,
        MD5=hashlib.md5(raw.read_bytes(), usedforsecurity=False).hexdigest(),
        SHA256=p.file_hash(raw),
    )
    protocol = tmp_path / "acquisition.json"
    p.write(protocol, {"toy": True})
    manifest = dict(
        required_session_parent_acceptance="results/acquisition/task0030-three-prong/parent-acceptance.json",
        verified_bytes=value["bytes"],
        publisher_MD5=value["MD5"],
        local_SHA256=value["SHA256"],
    )
    p.write(tmp_path / "manifest.json", manifest)
    base = tmp_path / "results/acquisition/task0030-three-prong"
    base.mkdir(parents=True)
    workflow = dict(
        status="parent_accepted_verified_artifact",
        manifest_file_byte_sha256=p.file_hash(tmp_path / "manifest.json"),
        stages=[
            dict(
                parent=dict(status="parent_accepted", dispatch=dict(child_reaped=True))
            )
            for _ in range(3)
        ],
    )
    p.write(base / "workflow.json", workflow)
    p.write(
        base / "parent-acceptance.json",
        dict(
            status="parent_accepted_verified_artifact",
            sleep_assertion_released=True,
            accepted_complete_bytes=value["bytes"],
            workflow_file_byte_sha256=p.file_hash(base / "workflow.json"),
        ),
    )
    p.write(tmp_path / "integrity.json", dict(locally_computed=value))
    np.save(tmp_path / "fingerprints.npy", np.zeros(4, dtype="V32"), allow_pickle=False)
    local = dict(
        path="local.h5",
        **value,
        manifest="manifest.json",
        acquisition_parent=str((base / "parent-acceptance.json").relative_to(tmp_path)),
        integrity="integrity.json",
        acquisition_protocol="acquisition.json",
        acquisition_protocol_canonical_JSON_sha256=p.digest({"toy": True}),
    )
    spec = dict(
        local_payload=local,
        source=dict(local_payload_sha256=value["SHA256"]),
        preserved_file_byte_sha256={},
        original_fingerprints=dict(
            path="fingerprints.npy",
            sha256=p.file_hash(tmp_path / "fingerprints.npy"),
            shape=[4],
        ),
    )
    return tmp_path, spec, base


@pytest.mark.parametrize(
    "bad",
    [
        "good",
        "parent_missing",
        "parent_rejected",
        "workflow_hash",
        "release",
        "wrong_md5",
        "raw_mutation",
        "stage_rejected",
        "fingerprint_hash",
    ],
)
def test_manifest_requires_complete_parent_and_byte_identity(acquisition_lineage, bad):
    root, spec, base = acquisition_lineage
    if bad == "parent_missing":
        (base / "parent-acceptance.json").unlink()
    if bad in ("parent_rejected", "workflow_hash", "release"):
        doc = p.read(base / "parent-acceptance.json")
        if bad == "parent_rejected":
            doc["status"] = "failed_consumed_preserved"
        if bad == "workflow_hash":
            doc["workflow_file_byte_sha256"] = "0" * 64
        if bad == "release":
            doc["sleep_assertion_released"] = False
        p.write(base / "parent-acceptance.json", doc)
    if bad == "wrong_md5":
        spec["local_payload"]["MD5"] = "0" * 32
    if bad == "raw_mutation":
        (root / "local.h5").write_bytes(b"z" * (root / "local.h5").stat().st_size)
    if bad == "stage_rejected":
        doc = p.read(base / "workflow.json")
        doc["stages"][1]["parent"]["status"] = "parent_rejected"
        p.write(base / "workflow.json", doc)
        parent = p.read(base / "parent-acceptance.json")
        parent["workflow_file_byte_sha256"] = p.file_hash(base / "workflow.json")
        p.write(base / "parent-acceptance.json", parent)
    if bad == "fingerprint_hash":
        spec["original_fingerprints"]["sha256"] = "0" * 64
    c = Clock()
    if bad == "good":
        assert q.metadata(root, spec, clock=c, deadline=10)["numerical_loads"] == 0
    else:
        with pytest.raises((ValueError, FileNotFoundError)):
            q.metadata(root, spec, clock=c, deadline=10)


@pytest.mark.parametrize("bad", ["count", "dtype", "bytes", "fortran"])
def test_cached_header_refuses_before_numeric_load(tmp_path, bad, monkeypatch):
    shape = 5 if bad == "count" else 4
    dtype = np.float32 if bad == "dtype" else np.float64
    path = tmp_path / "scores.npy"
    if bad == "fortran":
        np.save(path, np.zeros((2, 2), dtype=np.float64, order="F"))
    else:
        np.save(path, np.zeros(shape, dtype=dtype))
    if bad == "bytes":
        path.write_bytes(path.read_bytes() + b"extra")
    monkeypatch.setattr(
        np,
        "load",
        lambda *args, **kwargs: pytest.fail(
            "original numerical load before header gate"
        ),
    )
    with pytest.raises(ValueError):
        q.array_header(path, "<f8", [4])


@pytest.mark.parametrize("bad", ["row_order", "wrong_label", "duplicate", "overlap"])
def test_custody_failure_stops_before_scoring(tmp_path, monkeypatch, bad):
    from latenttrigger.evaluation import local_three_prong_smoke as smoke

    monkeypatch.setattr(smoke, "ContinuousClock", Clock)
    spec, _ = smoke.fixture(tmp_path)
    path = tmp_path / "toy.h5"
    with h5py.File(path, "a") as h:
        if bad == "row_order":
            h["/df/axis1"][0] = 2
        if bad == "wrong_label":
            h["/df/block0_values"][0, 2100] = 0
        if bad == "duplicate":
            h["/df/block0_values"][1] = h["/df/block0_values"][0]
        if bad == "overlap":
            particles = h["/df/block0_values"][0:1, :2100].reshape(1, 700, 3)
            original = np.zeros(8, dtype="V32")
            original[7] = event_fingerprints(particles)[0]
            np.save(tmp_path / "original/fingerprints.npy", original)
    spec["local_payload"]["SHA256"] = p.file_hash(path)
    spec["source"]["local_payload_sha256"] = spec["local_payload"]["SHA256"]
    spec["original_fingerprints"]["sha256"] = p.file_hash(
        tmp_path / "original/fingerprints.npy"
    )
    directory = tmp_path / q.OUTPUT / "prepare"
    directory.mkdir()
    audit = Audit(directory / "access.json", dict(synthetic=True))
    with pytest.raises(ValueError):
        n.prepare(tmp_path, spec, directory, audit, Guard())
    assert not exposure(directory / "access.json")["new_signal_model_accessed"]
    assert not (tmp_path / q.PREPARED / "manifest.json").exists()
    assert p.read(directory / "validity.json")["status"] == "failed_no_subset"


def test_background_count_discrepancy_veto(tmp_path, monkeypatch):
    from latenttrigger.evaluation import local_three_prong_smoke as smoke

    monkeypatch.setattr(smoke, "ContinuousClock", Clock)
    spec, _ = smoke.fixture(tmp_path)
    base = tmp_path / q.OUTPUT
    directory = base / "prepare"
    directory.mkdir()
    g = Guard()
    n.prepare(
        tmp_path,
        spec,
        directory,
        Audit(directory / "access.json", dict(synthetic=True)),
        g,
    )
    spec["calibrated_background_counts"]["PCA"][0] += 1
    directory = base / "PCA"
    directory.mkdir()
    audit = Audit(directory / "access.json", dict(synthetic=True))
    with pytest.raises(ValueError, match="Shared background fixed-count"):
        n.evaluate(tmp_path, spec, "PCA", directory, audit, g)
    access = exposure(directory / "access.json")
    assert (
        access["signal_scored_presentations"] == 4
        and access["cached_numeric_loads"] == 1
    )
    assert not (directory / "evaluation.json").exists()


def test_failed_predecessor_refuses_before_candidate(tmp_path, monkeypatch):
    spec = q.load()
    phase = "PCA"
    parent_pid = worker.os.getppid()
    base = tmp_path / q.OUTPUT
    base.mkdir(parents=True)
    (base / phase).mkdir()
    reservation = dict(
        parent_pid=parent_pid,
        source_file_sha256={},
        protocol_canonical_JSON_sha256=q.HASH,
        reserved_continuous=0.0,
        whole_deadline_continuous=600.0,
        sleep_helper_pid=10,
        sleep_assertion_id="abc",
    )
    p.write(base / "reservation.json", reservation)
    grant = dict(
        phase=phase,
        token="token",
        parent_pid=parent_pid,
        reservation_file_byte_sha256=p.file_hash(base / "reservation.json"),
        started_continuous=0.0,
        stage_deadline_continuous=120.0,
        operation_deadline_continuous=118.0,
        sleep_helper_pid=10,
        sleep_assertion_id="abc",
        predecessors=dict(prepare="sha"),
    )
    p.write(base / "PCA-grant.json", grant)
    (base / "prepare").mkdir()
    p.write(base / "prepare/parent-acceptance.json", dict(status="parent_rejected"))
    monkeypatch.setattr(q, "load", lambda root: spec)
    monkeypatch.setattr(q, "source_map", lambda root: {})
    monkeypatch.setattr(
        worker.p,
        "file_hash",
        lambda path: (
            grant["reservation_file_byte_sha256"]
            if str(path).endswith("reservation.json")
            else "same"
        ),
    )
    monkeypatch.setattr(q, "authorization", lambda *args, **kwargs: {})
    monkeypatch.setattr(q, "metadata", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        q, "check_file", lambda root, path, digest, **kwargs: root / path
    )
    with pytest.raises(ValueError, match="Failed predecessor"):
        worker.bindings(tmp_path, phase, "token", Clock(), 118.0)


def test_owned_reporting_joins_all_thresholds_without_original_cache(tmp_path):
    import shutil

    from sklearn.metrics import precision_recall_curve, roc_curve

    from latenttrigger.evaluation.local_three_prong_reporting import reporting

    spec = q.load()
    base = tmp_path / q.OUTPUT
    base.mkdir(parents=True)
    for name in ["calibrated_csv", "comparison_csv"]:
        original = p.ROOT / spec["historical_two_prong"][name]
        target = tmp_path / spec["historical_two_prong"][name]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, target)
    for phase, entry in zip(("PCA", "AE"), spec["candidates"], strict=True):
        directory = base / phase
        directory.mkdir()
        bg = np.zeros(150471, np.float64)
        for t, count in zip(
            entry["thresholds"],
            spec["calibrated_background_counts"][phase],
            strict=True,
        ):
            bg[:count] = np.nextafter(t["threshold"], np.inf)
        sig = np.linspace(0, entry["thresholds"][-1]["threshold"] * 1.4, 100000)
        metrics = evaluate_scores(bg, sig)
        metrics["calibrated_thresholds"] = [
            dict(
                target_fpr=t["target_fpr"],
                threshold=t["threshold"],
                **at_threshold(bg, sig, t["threshold"]),
            )
            for t in entry["thresholds"]
        ]
        for point in metrics["calibrated_thresholds"]:
            point["preregistered_arithmetic"] = n.arithmetic(
                point["background"], point["signal"]
            )
        labels = np.r_[np.zeros(len(bg), np.uint8), np.ones(len(sig), np.uint8)]
        values = np.r_[bg, sig]
        fpr, tpr, roc_thresholds = roc_curve(labels, values, drop_intermediate=False)
        precision, recall, pr_thresholds = precision_recall_curve(labels, values)
        np.savez(
            directory / "curves.npz",
            fpr=fpr,
            tpr=tpr,
            roc_thresholds=roc_thresholds,
            precision=precision,
            recall=recall,
            pr_thresholds=pr_thresholds,
        )
        e = dict(
            model_scientific_sha256=entry["model_scientific_sha256"],
            calibration_scientific_sha256=entry["results_scientific_sha256"],
            new_signal_scientific_sha256="synthetic-only",
            metrics=metrics,
            owned_curves_file_byte_sha256=p.file_hash(directory / "curves.npz"),
        )
        p.write(
            directory / "evaluation.json",
            dict(scientific=e, scientific_sha256=p.digest(e)),
        )
    output = base / "consolidate"
    output.mkdir()
    audit = Audit(output / "access.json", dict(synthetic=True))
    result = reporting(tmp_path, spec, base, output, audit, Guard())
    import csv

    with (output / "two-vs-three-prong.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 8 and len(result["evaluations"]) == 2
    assert (output / "roc-pr.png").stat().st_size > 10000
    assert exposure(output / "access.json")["cached_numeric_loads"] == 0
    assert [r["confirmed_read"] for r in audit.document["records"]] == [2, 2, 2]
