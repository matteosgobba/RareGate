"""Synthetic narrow access, descriptives, identities, and parent lifecycle gates."""

import ast
from pathlib import Path

import numpy as np
import pytest
from tests.feature_score_fixtures import fixture_plan
from tests.test_three_prong_acquisition_v3 import Child, Clock

from latenttrigger.diagnostics import analysis as a
from latenttrigger.diagnostics import controller as c
from latenttrigger.diagnostics import protocol as p
from latenttrigger.diagnostics import reporting as r
from latenttrigger.diagnostics import runtime as rt
from latenttrigger.diagnostics.reader import (
    AccessLedger,
    NarrowReader,
    validate_membership,
)
from latenttrigger.evaluation.guard import NATIVE_METHOD, PRESSURE_METHOD, GuardError


class NoopGuard:
    def check(self):
        pass

    def boundary(self, _):
        pass


@pytest.fixture
def fixture(tmp_path):
    plan = fixture_plan(tmp_path)
    output = tmp_path / "owned"
    output.mkdir()
    ledger = AccessLedger(output / "access.json")
    return tmp_path, plan, output, ledger


def test_single_load_scope_and_complete_aggregates(fixture, monkeypatch):
    root, plan, output, ledger = fixture
    called = []
    original = np.load

    def load(path, *args, **kwargs):
        called.append(str(Path(path).relative_to(root)))
        return original(path, *args, **kwargs)

    monkeypatch.setattr(np, "load", load)
    p.verify_inputs(root, plan, ledger.record)
    before = {name: p.file_hash(root / name) for name in plan["arrays"]}
    a.analyze(root, plan, output, ledger, NoopGuard())
    assert len(called) == len(set(called)) == 11
    assert set(called) == set(plan["arrays"])
    assert before == {name: p.file_hash(root / name) for name in plan["arrays"]}
    access = ledger.summary()
    assert access["feature_population_requests"] == 3
    assert access["feature_rows_read"] == 80
    assert access["stored_score_array_loads"] == 6
    assert access["stored_score_values_read"] == 160
    assert access["membership_array_loads"] == 3
    assert access["membership_records_read"] == 240
    assert access["potential_inflight"] is None
    summary = p.read(output / "analysis-summary.json")
    assert list(summary["coverage"].values()) == [24, 6, 48, 24, 192]
    assert summary["suppressed_feature_rows"] > 0


@pytest.mark.parametrize(
    "name",
    [
        "particles.npy",
        "fingerprints.npy",
        "event_aggregates.npy",
        "development.npy",
        "train_background",
    ],
)
def test_forbidden_reader_sources(fixture, name):
    root, plan, _, ledger = fixture
    reader = NarrowReader(root, plan, ledger)
    with pytest.raises(ValueError):
        reader.path(plan["original"] + "/" + name)


@pytest.mark.parametrize(
    "mutation",
    [
        "roles",
        "labels",
        "ids",
        "counts",
        "batch_order",
        "same_length_ledger",
        "dev",
        "partial",
        "candidate_ledger",
    ],
)
def test_membership_alignment_rejects(fixture, mutation):
    root, plan, _, _ = fixture
    codes, ids, labels = [
        np.load(root / plan["original"] / (n + ".npy"))
        for n in ("split_codes", "event_ids", "labels")
    ]
    if mutation == "roles":
        codes[0] = 0
    if mutation == "labels":
        labels[26] = 1
    if mutation == "ids":
        ids[25:55] = ids[25:55][::-1]
    if mutation == "counts":
        plan["role_counts"]["test_background"] += 1
    if mutation == "batch_order":
        plan["ledgers"]["PCA"][0]["batches"][0]["first_source_id"] += 1
    if mutation == "same_length_ledger":
        plan["ledgers"]["PCA"][0]["split"] = "test_signal"
    if mutation == "dev":
        plan["ledgers"]["PCA"][0]["dev_only"] = True
    if mutation == "partial":
        plan["ledgers"]["AE"][0]["inflight"] = {}
    if mutation == "candidate_ledger":
        plan["ledgers"]["AE"] = []
    with pytest.raises(ValueError):
        validate_membership(codes, ids, labels, plan)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "altered",
        "reverse_same_length",
        "symlink",
        "header_dtype",
        "header_shape",
    ],
)
def test_array_identity_before_numerical_analysis(fixture, mutation):
    root, plan, _, _ = fixture
    name = plan["scores"]["PCA/background"]
    path = root / name
    if mutation == "missing":
        path.unlink()
    if mutation == "altered":
        path.write_bytes(path.read_bytes()[:-1] + b"x")
    if mutation == "reverse_same_length":
        np.save(path, np.load(path)[::-1])
    if mutation == "symlink":
        other = root / "other.npy"
        path.rename(other)
        path.symlink_to(other)
    if mutation == "header_dtype":
        plan["arrays"][name]["dtype"] = "<f4"
    if mutation == "header_shape":
        plan["arrays"][name]["shape"] = [29]
    with pytest.raises(ValueError):
        p.verify_inputs(root, plan)


@pytest.mark.parametrize(
    "outputs",
    [{}, {"score.npy": "a", "stage/score.npy": "a"}, {"foreign/score.npy": "a"}],
)
def test_explicit_receipt_key_refuses_ambiguity(outputs):
    with pytest.raises(ValueError):
        p.receipt_key(outputs, "stage/score.npy", "stage")


@pytest.mark.parametrize("key", ["score.npy", "stage/score.npy"])
def test_receipt_key_conventions(key):
    assert p.receipt_key({key: "a"}, "stage/score.npy", "stage") == "a"


def test_selection_precedes_values_and_duplicate_requests(fixture):
    root, plan, _, ledger = fixture
    reader = NarrowReader(root, plan, ledger)
    with pytest.raises(ValueError):
        reader.feature_population("background")
    reader.memberships()
    assert np.isfinite(reader.feature_population("background")).all()
    with pytest.raises(ValueError):
        reader.feature_population("background")
    with pytest.raises(ValueError):
        reader.memberships()
    reader.close()


@pytest.mark.parametrize("population", p.POPULATIONS)
@pytest.mark.parametrize("mutation", ["nan", "inf", "wrong_dtype"])
def test_finite_feature_requirements(fixture, population, mutation):
    root, plan, _, ledger = fixture
    name = (
        plan["prepared"] + "/event_features.npy"
        if population == "three_prong"
        else plan["original"] + "/event_features.npy"
    )
    x = np.load(root / name)
    if mutation == "wrong_dtype":
        x = x.astype(np.float64)
    else:
        x[-1 if population != "background" else 26, 0] = (
            np.nan if mutation == "nan" else np.inf
        )
    np.save(root / name, x)
    reader = NarrowReader(root, plan, ledger)
    reader.memberships()
    with pytest.raises(ValueError):
        reader.feature_population(population)
    reader.close()


@pytest.mark.parametrize(
    "mutation", ["nan", "inf", "negative", "wrong_dtype", "wrong_length"]
)
def test_score_constraints(fixture, mutation):
    root, plan, _, ledger = fixture
    name = plan["scores"]["PCA/background"]
    values = np.load(root / name)
    if mutation in ("nan", "inf", "negative"):
        values[0] = {"nan": np.nan, "inf": np.inf, "negative": -1}[mutation]
    if mutation == "wrong_dtype":
        values = values.astype(np.float32)
    if mutation == "wrong_length":
        values = values[:-1]
    np.save(root / name, values)
    reader = NarrowReader(root, plan, ledger)
    with pytest.raises(ValueError):
        reader.scores("PCA", "background")


def test_linear_quantile_and_population_std():
    stats = a.describe(np.array([0, 2, 4, 6], dtype=np.float32))
    assert stats["std"] == pytest.approx(np.sqrt(5))
    assert stats["q0.25"] == 1.5 and stats["q0.001"] == 0.006
    assert stats["count"] == 4 and stats["mean"] == 3


def test_average_ranks_ties_and_coefficient():
    x = a.average_ranks(np.array([3.0, 1.0, 1.0, 2.0]))
    assert np.array_equal(x, [4, 1.5, 1.5, 3])
    assert a.rank_coefficient(x, x) == (1, None)
    assert a.rank_coefficient(x, 5 - x) == (-1, None)


@pytest.mark.parametrize(
    "x,y,reason",
    [
        ([1], [1], "fewer_than_two_events"),
        ([1, 1], [1, 2], "constant_feature"),
        ([1, 2], [1, 1], "constant_score"),
        ([1, 1], [1, 1], "constant_feature_and_score"),
    ],
)
def test_undefined_associations(x, y, reason):
    assert a.rank_coefficient(np.array(x), np.array(y)) == (None, reason)


@pytest.mark.parametrize("n", [0, 1, 19, 20, 21])
def test_strict_ties_and_suppression(n):
    x = np.ones((n + 1, 8), np.float32)
    scores = np.r_[1.0, np.full(n, 2.0)]
    count, rows = a.tail_profile(x, scores, 1.0)
    assert count == n
    assert (
        all(
            r["mean"] is None
            and r["suppression_reason"] == "small_tail_descriptive_summary_suppressed"
            for r in rows
        )
        if n < 20
        else all(r["mean"] == 1.0 and r["suppression_reason"] is None for r in rows)
    )


def test_no_significance_api_or_forwards():
    tree = ast.parse(Path(a.__file__).read_text())
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert all(
        not (v or "").startswith(("scipy", "sklearn", "torch", "latenttrigger.models"))
        for v in imports
    )
    text = Path(a.__file__).read_text()
    assert all(
        name not in text
        for name in (
            "spearmanr(",
            "pearsonr(",
            "roc_auc_score(",
            "average_precision_score(",
        )
    )


def test_reporting_aggregate_only(fixture, monkeypatch):
    root, plan, output, ledger = fixture
    a.analyze(root, plan, output, ledger, NoopGuard())
    identities = {n: p.file_hash(output / n) for n in a.TABLES}
    for name in plan["arrays"]:
        (root / name).unlink()
    monkeypatch.setattr(
        np, "load", lambda *_, **__: pytest.fail("Numerical source reopened")
    )
    plotted = root / "plots"
    plotted.mkdir()
    r.render(output, plotted, identities)
    assert all((plotted / n).exists() for n in r.FIGURES)
    assert (
        p.read(plotted / "reporting-summary.json")["population_or_score_array_reloads"]
        == 0
    )


def test_owned_aggregates_altered_rejected(fixture):
    root, plan, output, ledger = fixture
    a.analyze(root, plan, output, ledger, NoopGuard())
    identities = {n: p.file_hash(output / n) for n in a.TABLES}
    (output / a.TABLES[0]).write_text("changed")
    with pytest.raises(ValueError):
        r.read_aggregates(output, identities)


def sample(rss=1, pressure=1):
    return dict(
        peak_rss_bytes=rss,
        native_heap_reserved_bytes=2,
        native_heap_in_use_bytes=1,
        workspace_method=NATIVE_METHOD,
        pressure_dispatch_flags=pressure,
        pressure_errno=1 if pressure is None else None,
        pressure_method=PRESSURE_METHOD,
    )


@pytest.mark.parametrize(
    "rss,pressure,accepted",
    [
        (2**30, 2, True),
        (2**30 + 1, 1, False),
        (1, 4, False),
        (1, None, True),
        (0, 1, False),
    ],
)
def test_task0033_narrow_resource_guard(rss, pressure, accepted):
    clock = Clock()
    guard = rt.DiagnosticGuard(
        5, clock=clock, probe=lambda: sample(rss, pressure), notify=False
    )
    if accepted:
        guard.check()
    else:
        with pytest.raises(GuardError):
            guard.check()
    assert guard.journal_limit == 64 * 2**20


@pytest.mark.parametrize("jump", [5, 50, 500])
def test_continuous_deadline_advances_during_suspension(jump):
    clock = Clock()
    clock.sleep(jump)
    assert clock.ordinary == 0
    with pytest.raises(GuardError):
        rt.check_deadline(clock, 4)


@pytest.mark.parametrize(
    "jump,code,accepted", [(0, 0, True), (11, 0, False), (0, 1, False)]
)
def test_normal_exit_reaped_still_requires_timely_parent(
    tmp_path, monkeypatch, jump, code, accepted
):
    from latenttrigger.data import three_prong_v3_runtime as old

    clock = Clock()
    child = Child(clock, exit_at=0, code=code)

    def launch(*args, **kwargs):
        clock.sleep(jump)
        return child

    monkeypatch.setattr(old, "parent_check", lambda **kwargs: 1)
    result = rt.supervise(
        [],
        tmp_path / "log",
        root=tmp_path,
        environment={},
        clock=clock,
        operation_deadline=8,
        stage_deadline=10,
        whole_deadline=20,
        launch=launch,
        sleep=clock.sleep,
    )
    assert result["parent_confirms_normal_exit"] is accepted


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "failed"),
        ("source_file_sha256", {}),
        ("plan_file_byte_sha256", "foreign"),
    ],
)
def test_body_complete_not_parent_accepted(fixture, monkeypatch, field, value):
    _, _, output, _ = fixture
    grant = dict(
        phase="analysis", source_file_sha256={"a": "b"}, plan_file_byte_sha256="plan"
    )
    p.durable_json(output.parent / "analysis-grant.json", grant)
    result = dict(
        status="body_complete_awaiting_exit",
        phase="analysis",
        source_file_sha256=grant["source_file_sha256"],
        plan_file_byte_sha256="plan",
        grant_file_byte_sha256=p.file_hash(output.parent / "analysis-grant.json"),
        resources=dict(
            peak_rss_bytes=1,
            native_heap_reserved_bytes=1,
            latched_error=None,
            owned_thread_alive=False,
        ),
        cleanup_continuous_seconds=0,
        output_file_byte_sha256={},
    )
    result[field] = value
    monkeypatch.setattr(p, "source_map", lambda: grant["source_file_sha256"])
    dispatch = dict(
        parent_confirms_normal_exit=True, child_reaped=True, within_deadline=True
    )
    with pytest.raises(ValueError):
        c.validate_body(result, dispatch, grant, output, Clock(), 5)


def test_durable_inflight_retained(fixture, monkeypatch):
    root, plan, _, ledger = fixture
    reader = NarrowReader(root, plan, ledger)
    monkeypatch.setattr(
        np, "load", lambda *a, **k: (_ for _ in ()).throw(OSError("interrupted read"))
    )
    with pytest.raises(OSError):
        reader.scores("AE", "three_prong")
    saved = p.read(ledger.path)
    assert (
        saved["stored_score_array_loads"] == 0
        and saved["potential_inflight"]["expected"] == 25
    )


def test_duplicate_metadata_json_keys(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError):
        p.read(path)


def test_parent_output_storage_bound(tmp_path):
    path = tmp_path / "large.log"
    with path.open("wb") as stream:
        stream.truncate(2**20 + 1)
    with pytest.raises(GuardError):
        rt.storage_check(tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        "prepared_order",
        "prepared_label",
        "prepared_transform",
        "new_model",
        "new_prepared",
        "new_source",
        "new_batches",
        "parent_exit",
        "receipt_identity",
        "score_identity",
        "ambiguous_key",
        "old_store",
        "ledger_manifest",
        "parameters",
    ],
)
def test_synthetic_accepted_lineage_refuses_changes(tmp_path, monkeypatch, mutation):
    from tests.feature_score_lineage_fixtures import lineage_fixture

    lineage_fixture(tmp_path, monkeypatch)
    if mutation.startswith("prepared_"):
        path = tmp_path / p.PREPARED / "manifest.json"
        d = p.read(path)
        if mutation == "prepared_order":
            d["scientific"]["source_order"] = "reverse"
        if mutation == "prepared_label":
            d["scientific"]["label_provenance"] = "unknown"
        if mutation == "prepared_transform":
            d["scientific"]["transform"]["file_byte_sha256"] = "other"
    elif mutation in ("new_model", "new_prepared", "parameters"):
        path = tmp_path / p.NEW / "PCA/evaluation.json"
        d = p.read(path)
        key = {
            "new_model": "model_scientific_sha256",
            "new_prepared": "new_signal_scientific_sha256",
            "parameters": "parameters_after",
        }[mutation]
        d["scientific"][key] = "other"
    elif mutation in ("new_source", "new_batches"):
        path = tmp_path / p.NEW / "PCA/receipt.json"
        d = p.read(path)
        row = d["exposure"]["records"][0]
        if mutation == "new_source":
            row["source"] = "foreign-same-length.npy"
        else:
            row["batches"][-1] = 1695
    elif mutation == "ledger_manifest":
        path = tmp_path / p.OLD / "PCA/test-unblinding.json"
        d = p.read(path)
        d["binding"]["store"]["metadata_file_byte_sha256"]["manifest.json"] = "other"
    elif mutation == "old_store":
        path = tmp_path / p.OLD / "PCA/receipt.json"
        d = p.read(path)
        d["verified_store_scientific_sha256"] = "other"
    else:
        path = tmp_path / p.OLD / "PCA/parent-acceptance.json"
        d = p.read(path)
        if mutation == "parent_exit":
            d["dispatch"]["returncode"] = 1
        if mutation == "receipt_identity":
            d["receipt_file_byte_sha256"] = "other"
        if mutation == "score_identity":
            d["output_file_byte_sha256"]["test_signal-scores.npy"] = "other"
        if mutation == "ambiguous_key":
            d["output_file_byte_sha256"][p.OLD + "/PCA/test_signal-scores.npy"] = d[
                "output_file_byte_sha256"
            ]["test_signal-scores.npy"]
    p.durable_json(path, d)
    with pytest.raises(ValueError):
        p.build_plan(tmp_path)


def test_synthetic_lineage_full_binding(tmp_path, monkeypatch):
    from tests.feature_score_lineage_fixtures import lineage_fixture

    plan = lineage_fixture(tmp_path, monkeypatch)
    assert len(plan["arrays"]) == 11 and len(plan["metadata"]) == 28
    assert plan["counts"] == dict(
        background=150471, two_prong=100000, three_prong=100000
    )


@pytest.mark.parametrize("failure", ["setup", "loss", "release"])
def test_controller_assertion_failures_preserved(fixture, monkeypatch, failure):
    root, plan, _, _ = fixture
    clock = Clock()
    monkeypatch.setattr(c, "ContinuousClock", lambda: clock)
    monkeypatch.setattr(c, "parent_check", lambda **kwargs: 1)

    class Assertion:
        evidence = dict(released=False)

        def __init__(self, _):
            pass

        def start(self, deadline):
            if failure == "setup":
                raise GuardError("setup failure")
            return self

        def check(self, deadline, force=False):
            if failure == "loss":
                raise GuardError("owned assertion lost")

        def release(self, deadline):
            if failure == "release":
                raise GuardError("release absent")
            self.evidence = dict(released=True)
            return self.evidence

    monkeypatch.setattr(c, "IdleAssertion", Assertion)
    monkeypatch.setattr(
        c,
        "supervise",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            GuardError("synthetic dispatch failure")
        ),
    )
    result = c.run_session(plan, root / "session", input_root=root, synthetic=True)
    assert result["status"] == (
        "failed_before_reservation" if failure == "setup" else "failed_consumed"
    )
    assert result["error"]
    assert (root / "session/workflow.json").exists()
    if failure == "release":
        assert result["sleep_assertion"]["released"] is False
    with pytest.raises(FileExistsError):
        c.run_session(plan, root / "session", input_root=root, synthetic=True)
