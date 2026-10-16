"""Generated-only qualification of Task0062; no final population/model access."""

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from latenttrigger.research import decisive_adc_evaluation as e
from latenttrigger.research.decisive_adc import data, models
from latenttrigger.research.decisive_adc import statistics as stats


@pytest.fixture
def generated(tmp_path):
    inputs = tmp_path / "inputs"
    out = tmp_path / "output"
    modelroot = tmp_path / "models"
    for folder in (out / "private", out / "ledger"):
        folder.mkdir(parents=True)
    rng = np.random.default_rng(91)
    freeze = dict(roles={}, calibration=[])
    for role, n in (
        ("development", 64),
        ("final_background", 128),
        ("A_to_4l", 64),
        ("LQ_to_btau", 64),
    ):
        directory = inputs / "prepared" / role
        directory.mkdir(parents=True)
        objects = np.zeros((n, 19, 4), dtype=np.float64)
        objects[:, 0, 0] = rng.uniform(0, 100, n)
        objects[:, 0, 3] = 1
        objects[:, 1, :] = [30, 0.2, 0.1, 2]
        objects[:, 5, :] = [25, -0.4, 2.0, 3]
        objects[:, 9, :] = [20, 0.5, -2.0, 4]
        values = data.features(objects).astype(np.float32)
        np.save(directory / "features.npy", values)
        np.save(directory / "objects.npy", objects)
        freeze["roles"][role] = dict(
            role=role,
            source="train-first-hash-ordered"
            if role == "development"
            else ("background" if role == "final_background" else role),
            rows=n,
            scaler_sha256="generated",
            files={
                name: data.digest(directory / name)
                for name in ("features.npy", "objects.npy")
            },
        )
    (inputs / "private").mkdir()
    data.write_json(
        inputs / "private/scaler.json", dict(mean=[0.0] * 12, std=[1.0] * 12)
    )
    for arm, seed in models.STREAMS:
        if arm in models.LAYERS:
            model = models.ADCNet(arm, int(seed))
            history = dict(state_sha256=models.state_digest(model))
        elif arm == "PCA3":
            model = dict(
                arm=arm,
                mean=np.zeros(12),
                components=np.eye(12)[:3],
                singular_values=np.ones(12),
            )
            history = {}
        else:
            model = dict(arm=arm, mean=np.zeros(12), cholesky=np.eye(12))
            history = {}
        directory = modelroot / arm / seed
        models.save_model(directory, arm, seed, model, history)
        x = np.load(inputs / "prepared/development/features.npy")
        np.save(directory / "development_scores.npy", e.score_shape(model, x, 32))
        for alpha in e.RATES:
            freeze["calibration"].append(
                dict(
                    arm=arm,
                    seed=seed,
                    alpha=alpha,
                    threshold=10.0,
                    lower_endpoint=9.0,
                    upper_endpoint=11.0,
                )
            )
    config = dict(
        root="data/decisive-v2-adc-task0062",
        development_rows=64,
        output_plan="generated",
        cpu_seconds=1200,
    )
    context = e.EvaluationContext(out, inputs, freeze, config, generated=True)
    return context, modelroot


def fake_cpu():
    return dict(
        rows=[
            dict(
                repetition=rep,
                arm=arm,
                seed=seed,
                batch=32,
                boundary="joint",
                mean_ns=(100 if arm == "referenceAE" else 50),
            )
            for rep in range(8)
            for arm, seed in models.STREAMS
        ]
    )


def run_generated(context, modelroot):
    context.unblind(dict(generated=True))
    loaded = {
        f"{a}--{s}": models.load_model(modelroot / a / s) for a, s in models.STREAMS
    }
    for role in ("final_background", *e.SIGNALS):
        x = context.role(role)
        for arm, seed in models.STREAMS:
            e.commit_scores(context, role, arm, seed, loaded[f"{arm}--{seed}"], x)
    result = e.analyze(context, fake_cpu())
    robust = e.robustness(context, loaded)
    bias = e.bias_profiles(context)
    return result, robust, bias


def test_generated_complete_result_and_closed_family(generated):
    context, modelroot = generated
    result, robust, bias = run_generated(context, modelroot)
    assert len(result["inference"]) == 44
    assert len(result["background"]) == 24
    assert len(result["signal"]) == 48
    assert len(result["ranking"]) == 16
    assert len(result["rate_comparability"]) == 12
    assert len(robust["rows"]) == 16 and all(r["passed"] for r in robust["rows"])
    assert len(bias) == 264
    assert all(r["N"] == 64 for r in result["inference"])
    assert all(r["prevalence"] == pytest.approx(1 / 3) for r in result["ranking"])
    assert result["decision"]["verdict"] in (
        "negative_compound_criterion",
        "inconclusive_compound_criterion",
    )


def test_required_reload_repeat_and_secondary_shapes(generated):
    context, root = generated
    _, _, rows = e.parity(context, root)
    assert len(rows) == 24 and all(r["qualified"] for r in rows)
    assert all(
        not r["reconstruction_applicable"]
        for r in rows
        if r["arm"] == "regularizedMahalanobis"
    )


@pytest.mark.parametrize(
    "role",
    ["final_background", "A_to_4l", "LQ_to_btau", "train", "calibration", "unused"],
)
def test_protected_role_denial(generated, role):
    with pytest.raises(PermissionError):
        generated[0].role(role)


def test_scope_string_does_not_authorize_production(tmp_path):
    config = dict(
        scope=e.SCOPE,
        task="Task0062",
        root="data/decisive-v2-adc-task0062",
        input_root="data/decisive-v2-adc-task0061",
    )
    with pytest.raises(PermissionError):
        e.EvaluationContext(tmp_path, tmp_path, {}, config)
    with pytest.raises(PermissionError):
        e.EvaluationContext(
            tmp_path, e.ROOT / config["input_root"], {}, config, generated=True
        )


def test_import_and_help_inactive(tmp_path):
    command = [
        sys.executable,
        "-B",
        str(e.ROOT / "scripts/evaluate_decisive_adc_experiment.py"),
        "--help",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert "preflight" in result.stdout and "--worker" not in result.stdout
    source = (e.ROOT / "scripts/evaluate_decisive_adc_experiment.py").read_text()
    assert "if __name__" in source


def test_partial_prefix_is_retained_and_cannot_restart(generated):
    context, root = generated
    context.unblind({})
    model = models.load_model(root / "PCA3/fit")
    with pytest.raises(InterruptedError):
        e.commit_scores(
            context,
            "final_background",
            "PCA3",
            "fit",
            model,
            context.role("final_background"),
            interrupt_after=32,
        )
    path = context.output / "private/final_background--PCA3--fit.npy.partial"
    array = np.load(path, allow_pickle=False)
    assert np.isfinite(array[:32]).all() and np.isnan(array[32:]).all()
    assert not (
        context.output / "private/final_background--PCA3--fit-commit.json"
    ).exists()
    with pytest.raises(FileExistsError):
        e.commit_scores(
            context,
            "final_background",
            "PCA3",
            "fit",
            model,
            context.role("final_background"),
        )


def test_committed_scores_tail_alignment_and_tamper(generated):
    context, root = generated
    context.unblind({})
    model = models.load_model(root / "PCA3/fit")
    # Full role enforces exact count on read; generated 65-row tail is committed but rejected as misaligned.
    x = np.zeros((65, 12), np.float32)
    r = e.commit_scores(context, "final_background", "PCA3", "fit", model, x)
    assert r["calls"] == 3 and r["padded"] == 31 and r["N"] == 65
    with pytest.raises(ValueError, match="alignment"):
        e.load_scores(context, "final_background", "PCA3", "fit")


def test_role_manifest_source_and_shape(generated):
    context, _ = generated
    context.unblind({})
    context.freeze["roles"]["A_to_4l"]["source"] = "background"
    with pytest.raises(ValueError, match="source"):
        context.role("A_to_4l")


def test_seed_indicators_are_not_score_ensemble_or_extra_events():
    scores = np.array([[100.0, 0.0], [0.0, 100.0], [0.0, 0.0]])
    actual = stats.seed_indicators(scores, [1.0, 1.0, 1.0])
    np.testing.assert_array_equal(actual, [1 / 3, 1 / 3])
    assert len(actual) == 2 and not np.array_equal(actual, (scores.mean(axis=0) > 1))


def test_paired_direction_quantile_endpoints_and_support():
    n = 10000
    candidate = np.ones((1, n)) * 2
    reference = np.ones((1, n))
    cuts = [dict(lower_endpoint=1.5, upper_endpoint=2.5)]
    rcuts = [dict(lower_endpoint=0.5, upper_endpoint=1.5)]
    bound = stats.signal_bounds(candidate, cuts, reference, rcuts)
    # Lower evaluates candidate>2.5 minus reference>.5 = -1; upper is +1.
    assert bound["lower"] == -1 and bound["upper"] == 1
    c = [dict(lower_endpoint=1.0, upper_endpoint=1.0)]
    r = [dict(lower_endpoint=3.0, upper_endpoint=3.0)]
    ni = stats.signal_bounds(candidate, c, reference, r, factor=0.9)
    expected_half = 7 * 1.9 * math.log(4 * 44 / 0.03) / (3 * (n - 1))
    assert ni["lower"] == pytest.approx(1 - expected_half) and ni["upper"] == 1
    assert e.reverse_interval(-0.2, 0.3) == (-0.3, 0.2)


@pytest.mark.parametrize("k,n", [(0, 9), (9, 9), (4, 9)])
def test_CP_and_Wilson_scopes(k, n):
    lower, upper = stats.exact_background_interval(k, n)
    wl, wu = e.wilson(k, n)
    if k == 0:
        assert lower == 0 and upper == pytest.approx(1 - (0.01 / 32) ** (1 / 9))
        assert wl == 0 and wu == pytest.approx(
            1.959963984540054**2 / (9 + 1.959963984540054**2)
        )
    if k == 9:
        assert upper == 1 and lower == pytest.approx((0.01 / 32) ** (1 / 9))
    assert 0 <= lower <= k / n <= upper <= 1 and 0 <= wl <= k / n <= wu <= 1


def test_rate_comparability_requires_pair_difference_too():
    assert stats.rate_comparable((0.0097, 0.0103), (0.0097, 0.0103), 0.01)
    assert not stats.rate_comparable((0.0091, 0.0096), (0.0104, 0.0109), 0.01)
    assert not stats.rate_comparable((0.0089, 0.0092), (0.0097, 0.0103), 0.01)


def decision_rows(ni=(0.01, 0.02), eff=(0.2, 0.3), difference=(-0.005, 0.005)):
    rows = []
    for signal in e.SIGNALS:
        for arm in e.ARMS:
            rows.append(
                dict(
                    kind="efficiency",
                    arm=arm,
                    reference="",
                    signal=signal,
                    alpha=0.01,
                    lower=eff[0],
                    upper=eff[1],
                )
            )
        rows.append(
            dict(
                kind="noninferiority",
                arm="compactAE",
                reference="referenceAE",
                signal=signal,
                alpha=0.01,
                lower=ni[0],
                upper=ni[1],
            )
        )
        for baseline in e.ARMS[2:]:
            rows.append(
                dict(
                    kind="difference",
                    arm="compactAE",
                    reference=baseline,
                    signal=signal,
                    alpha=0.01,
                    lower=difference[0],
                    upper=difference[1],
                )
            )
    return rows


@pytest.mark.parametrize(
    "ni,cost,expected",
    [
        ((0.01, 0.02), True, "compact_joint_success"),
        ((-0.02, -0.01), True, "negative_compound_criterion"),
        ((-0.01, 0.02), True, "inconclusive_compound_criterion"),
        ((0.01, 0.02), False, "negative_compound_criterion"),
    ],
)
def test_positive_negative_inconclusive_decisions(ni, cost, expected):
    costs = {
        k: dict(passed=cost)
        for k in (
            "compactAE_over_referenceAE",
            "PCA3_over_compactAE",
            "regularizedMahalanobis_over_compactAE",
        )
    }
    rates = {(a, 0.01): (0.0098, 0.0102) for a in e.ARMS}
    assert e.decision(decision_rows(ni=ni), rates, costs)["verdict"] == expected


def test_baseline_dominance_requires_both_topologies_rate_utility_cost():
    costs = {
        k: dict(passed=True)
        for k in (
            "compactAE_over_referenceAE",
            "PCA3_over_compactAE",
            "regularizedMahalanobis_over_compactAE",
        )
    }
    rates = {(a, 0.01): (0.0098, 0.0102) for a in e.ARMS}
    result = e.decision(
        decision_rows(ni=(-0.02, -0.01), difference=(-0.1, -0.05)), rates, costs
    )
    assert result["baseline_dominance"]["PCA3"]["passed"]
    assert result["verdict"] == "simple_baseline_dominance"
    rates["PCA3", 0.01] = (0.02, 0.03)
    assert not e.decision(decision_rows(difference=(-0.1, -0.05)), rates, costs)[
        "baseline_dominance"
    ]["PCA3"]["passed"]


def test_schedule_independent_integer_oracle():
    for rep in range(8):
        for batch in (1, 32, 512):
            for call in (0, 31, 32, 159):
                actual = stats.cpu_indices(rep, call, batch)
                assert actual.tolist() == [
                    ((rep * 160 + call) * batch + j) % 4096 for j in range(batch)
                ]
    result = stats.cpu_cost_rule(np.full((8, 3), 75.0), np.full((8, 3), 100.0))
    assert result["passed"] and result["median"] == 0.75
    bad = np.full((8, 1), 70.0)
    bad[:2] = 90
    assert not stats.cpu_cost_rule(bad, np.full((8, 1), 100.0))["passed"]


def test_timer_boundary_uses_frozen_score_and_joint_features(generated, monkeypatch):
    context, root = generated
    model = models.load_model(root / "PCA3/fit")
    obj = np.array(context.role("development", "objects")[:32], copy=True)
    scaler = e.read(context.input_root / "private/scaler.json")
    values = data.transform(data.features(obj), scaler)
    a = e.boundary(model, values, obj, scaler, [10.0, 20.0], "algorithm")
    b = e.boundary(model, values, obj, scaler, [10.0, 20.0], "joint")
    np.testing.assert_array_equal(a[0], b[0])
    assert all(x.flags.owndata for x in (a[0], *a[1]))


def test_full_cpu_orchestration_artificial_boundary_skips_secondary(
    generated, monkeypatch
):
    context, root = generated
    # Exercise exact full loop/schedule without real timing acceptance or real models.
    objects = np.zeros((4096, 19, 4), dtype=np.float64)
    monkeypatch.setattr(
        context,
        "role",
        lambda role, kind="features": (
            objects if kind == "objects" else np.zeros((4096, 12), np.float32)
        ),
    )
    monkeypatch.setattr(
        e,
        "boundary",
        lambda model, x, obj, scaler, cuts, name: (
            np.zeros(len(x)),
            (np.zeros(len(x), bool), np.zeros(len(x), bool)),
        ),
    )
    quals = [
        dict(
            arm=a,
            seed=s,
            batch=b,
            qualified=not (a == "compactAE" and s == "1729" and b == 512),
        )
        for a, s in models.STREAMS
        for b in (1, 32, 512)
    ]
    result = e.cpu_measure(
        context,
        {f"{a}--{s}": None for a, s in models.STREAMS},
        np.zeros((4096, 12), np.float32),
        quals,
    )
    assert len(result["rows"]) == 368 and len(result["skipped"]) == 16
    assert sum(r["timed_calls"] for r in result["rows"]) == 47104
    assert sum(r["warmups"] for r in result["rows"]) == 11776


def test_closed_map_hash_and_alias_rejection(tmp_path):
    path = tmp_path / "a"
    path.write_text("frozen")
    assert e.verify_map({str(path): data.digest(path)}) == dict(files=1, bytes=6)
    link = tmp_path / "alias"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="aliased"):
        e.verify_map({str(link): data.digest(path)})
    path.write_text("changed")
    with pytest.raises(ValueError, match="mismatch"):
        e.verify_map({str(path): "wrong"})


def test_runtime_only_ordering_is_harmless():
    first = dict(threadpools=[dict(name="a"), dict(name="b")], versions=dict(torch="x"))
    second = dict(first, threadpools=first["threadpools"][::-1])
    assert e.normalize_runtime(first) == e.normalize_runtime(second)
    second["versions"] = {"torch": "changed"}
    assert e.normalize_runtime(first) != e.normalize_runtime(second)


def test_zero_background_never_infinite_SIC(generated, monkeypatch):
    context, _ = generated
    monkeypatch.setattr(
        e, "load_scores", lambda c, role, arm, seed: np.zeros(c.counts[role])
    )
    result = e.analyze(context, fake_cpu())
    assert all(r["nominal_SIC"] is None for r in result["signal"])
    assert all(r["upper"] > 0 for r in result["background"])


@pytest.fixture(scope="session", autouse=True)
def capture_extension_toy_work():
    yield
    import os

    target = Path(os.environ["LATENTTRIGGER_ADC_TEST_ROOT"]) / "extension-toy-work.json"
    target.write_text(
        json.dumps(
            dict(
                counters=e.TALLY,
                scope="generated public/reconstruction presentations including artificial boundary loop; no real context",
            ),
            indent=2,
        )
        + "\n"
    )


def entry_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "evaluation_entry_generated",
        e.ROOT / "scripts/evaluate_decisive_adc_experiment.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("mode", ["normal", "failure", "timeout"])
def test_generated_process_reporting_and_cleanup(tmp_path, monkeypatch, mode):
    import datetime

    entry = entry_module()
    monkeypatch.setattr(entry, "storage", lambda: 1234)
    now = datetime.datetime.now(datetime.UTC).isoformat()
    config = dict(
        task_start_utc=now,
        study_storage_bytes=10000,
        worker_rss_bytes=4294967296,
        cleanup_reserve_seconds=0,
        task_seconds=7200,
    )
    script = {
        "normal": "print('generated worker')",
        "failure": "raise SystemExit(7)",
        "timeout": "import time; time.sleep(20)",
    }[mode]
    result = entry.observe(
        [sys.executable, "-B", "-c", script],
        tmp_path,
        0.2 if mode == "timeout" else 10,
        config,
    )
    assert result["worker_reaped"]
    assert result["returncode"] == (
        {"normal": 0, "failure": 7}.get(mode, result["returncode"])
    )
    assert (result["stop_reason"] is not None) == (mode == "timeout")
    assert (tmp_path / "outer-result.json").is_file()


def test_actual_supplementary_phase_IO_guard(generated):
    context, _ = generated
    script = f"""from types import SimpleNamespace
from pathlib import Path
from latenttrigger.research.decisive_adc_evaluation import install_guard
c=SimpleNamespace(input_root=Path({str(context.input_root)!r}),output=Path({str(context.output)!r}),authorized_final=False)
install_guard(c,'development')
assert (c.input_root/'prepared/development/features.npy').open('rb').read(6)==b'\\x93NUMPY'
for p in [c.input_root/'prepared/final_background/features.npy',c.input_root/'raw/background.h5']:
 try: p.open('rb')
 except PermissionError: pass
 else: raise AssertionError('protected IO allowed')
try: (c.input_root/'prepared/development/features.npy').open('wb')
except PermissionError: pass
else: raise AssertionError('frozen input writable')
"""
    subprocess.run(
        [sys.executable, "-B", "-c", script], check=True, capture_output=True, text=True
    )


def test_exclusive_generated_unblinding_intent(generated):
    context, _ = generated
    context.unblind({})
    with pytest.raises(FileExistsError):
        context.unblind({})


def test_curated_tables_and_figures_generated_only(generated):
    import importlib.util

    context, root = generated
    result, robust, bias = run_generated(context, root)
    cpu = fake_cpu()
    cpu["skipped"] = []
    data.write_json(context.output / "private/cpu.json", cpu)
    data.write_json(context.output / "private/parity.json", dict(rows=[], work={}))
    data.write_json(context.output / "private/score-pass.json", dict(generated=True))
    data.write_json(
        context.output / "private/extension-binding-v2.json", dict(generated=True)
    )
    (context.output / "diagnostics").mkdir()
    for phase in ("preflight-v2", "development-v2", "final", "postflight"):
        data.write_json(
            context.output / "ledger" / f"{phase}-result.json", dict(valid=True)
        )
        folder = context.output / "diagnostics" / phase
        folder.mkdir()
        data.write_json(folder / "outer-result.json", dict(generated=True))
    for old_phase in ("preflight", "development"):
        folder = context.output / "diagnostics" / old_phase
        folder.mkdir()
        data.write_json(
            folder / "outer-result.json", dict(generated=True, phase=old_phase)
        )
    spec = importlib.util.spec_from_file_location(
        "evaluation_report_generated",
        e.ROOT / "scripts/report_decisive_adc_evaluation.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary = module.export(
        context.output, context.output / "tables", context.output / "figures"
    )
    assert len(list((context.output / "tables").glob("*.csv"))) == 5
    assert len(list((context.output / "figures").glob("*.png"))) == 3
    assert len(summary["inference_family"]) == 44
    assert set(summary["prior_attempts"]) == {"preflight", "development"}


def test_bound_details_independent_Bernoulli_variance():
    result = e.bound_details(
        np.array([[0.0, 0.0, 2.0, 2.0]]), [dict(lower_endpoint=1.0, upper_endpoint=1.0)]
    )
    assert result["N"] == 4
    assert result["lower_endpoint_mean"] == 0.5 and result["upper_endpoint_mean"] == 0.5
    assert result["lower_endpoint_variance_ddof1"] == pytest.approx(1 / 3)
    assert result["upper_endpoint_variance_ddof1"] == pytest.approx(1 / 3)


def test_development_source_contract_is_training_hash_subset(generated):
    context, _ = generated
    assert (
        context.freeze["roles"]["development"]["source"] == "train-first-hash-ordered"
    )
    assert context.role("development").shape == (64, 12)
    context.freeze["roles"]["development"]["source"] = "background"
    with pytest.raises(ValueError, match="source"):
        context.role("development")
