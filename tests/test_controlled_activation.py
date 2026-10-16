"""Meaningful generated-fixture checks; no operational artifacts or sources."""

import copy
import hashlib
import importlib.metadata
import inspect
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import torch

from raregate.models.autoencoder import CompactAutoencoder
from raregate.research.controlled_activation import inference as i
from raregate.research.controlled_activation import models as m
from raregate.research.controlled_activation import protocol as p
from raregate.training.autoencoder import deterministic_cpu, feature_loader


@pytest.fixture(scope="module")
def spec():
    # Bind only this in-memory fixture to the test runtime, retaining frozen files.
    config = p.read(p.ROOT / p.CONFIG)
    config["dependencies"] = dict(
        Python=sys.version,
        Torch=importlib.metadata.version("torch"),
        NumPy=importlib.metadata.version("numpy"),
        torch_build_sha256=hashlib.sha256(torch.__config__.show().encode()).hexdigest(),
        adam_source_sha256=p.file_hash(Path(inspect.getfile(torch.optim.Adam))),
    )
    return p.validate_config(config)


@pytest.mark.parametrize(
    "field", ["Python", "Torch", "NumPy", "torch_build_sha256", "adam_source_sha256"]
)
def test_changed_runtime_identity_refused(spec, field):
    changed = copy.deepcopy(spec)
    changed["dependencies"][field] = "foreign runtime"
    with pytest.raises(ValueError):
        m.verify_runtime(changed)


@pytest.fixture
def pair(spec):
    initial = m.initialization(1729, spec)
    return (
        initial,
        m.factory("nonlinear", 1729, spec, initial),
        m.factory("linear", 1729, spec, initial),
    )


def values(n=17):
    return np.random.default_rng(35).normal(size=(n, 8)).astype(np.float32)


@pytest.mark.parametrize(
    "key,value",
    [
        ("scope", "operational"),
        ("operational_execution", True),
        ("PCA_three", True),
        ("seeds", [1729]),
        ("features", list(reversed(p.FEATURES))),
        ("layers", [8, 6, 4, 6, 8]),
        ("parameters", 156),
        ("forward_dtype", "float64"),
        ("score_dtype", "float32"),
        ("extra", 1),
    ],
)
def test_strict_schema(spec, key, value):
    changed = copy.deepcopy(spec)
    changed[key] = value
    with pytest.raises(ValueError):
        p.validate_config(changed)


@pytest.mark.parametrize(
    "key,value",
    [
        ("learning_rate", 0.01),
        ("batch_size", 17),
        ("max_epochs", 2),
        ("early_stopping_patience", 2),
        ("min_delta", 0.1),
        ("num_threads", 2),
        ("num_workers", 1),
    ],
)
def test_canonical_recipe_not_tiny_override(spec, key, value):
    changed = copy.deepcopy(spec)
    changed["training_contract"][key] = value
    with pytest.raises(ValueError):
        p.validate_config(changed)


def test_design_raw_bytes(spec, tmp_path):
    for name in p.DESIGN_FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((p.ROOT / name).read_bytes())
    p.validate_config(spec, tmp_path)
    (tmp_path / p.DESIGN).write_bytes((tmp_path / p.DESIGN).read_bytes() + b" ")
    with pytest.raises(ValueError):
        p.validate_config(spec, tmp_path)


@pytest.mark.parametrize("seed", p.SEEDS)
def test_factory_historical_and_affine(spec, seed):
    initial = m.initialization(seed, spec)
    n = m.factory("nonlinear", seed, spec, initial)
    linear_model = m.factory("linear", seed, spec, initial)
    with deterministic_cpu(seed, 1):
        historical = CompactAutoencoder()
    assert m.parameter_document(historical) == initial["parameters"]
    x = torch.from_numpy(values())
    with torch.inference_mode():
        assert torch.equal(n(x), historical(x))
        affine = x
        for layer in (
            linear_model.encoder[0],
            linear_model.encoder[2],
            linear_model.decoder[0],
            linear_model.decoder[2],
        ):
            affine = torch.nn.functional.linear(affine, layer.weight, layer.bias)
        assert torch.equal(linear_model(x), affine)
    assert sum(a.numel() for a in n.parameters()) == 155
    assert isinstance(n.encoder[1], torch.nn.ReLU) and isinstance(
        linear_model.encoder[1], torch.nn.Identity
    )


def test_storage_not_alias(pair):
    initial, n, linear_model = pair
    prior = copy.deepcopy(initial)
    linear = m.parameter_document(linear_model)
    for a, b in zip(n.parameters(), linear_model.parameters(), strict=True):
        assert a.data_ptr() != b.data_ptr()
    with torch.no_grad():
        next(n.parameters()).add_(1)
    assert m.parameter_document(linear_model) == linear and initial == prior


@pytest.mark.parametrize("failure", [False, True])
def test_caller_rng_and_settings_restored(spec, failure):
    py, np_state, ts = (
        random.getstate(),
        np.random.get_state(),
        torch.get_rng_state().clone(),
    )
    threads, det, warn = (
        torch.get_num_threads(),
        torch.are_deterministic_algorithms_enabled(),
        torch.is_deterministic_algorithms_warn_only_enabled(),
    )
    try:
        with m.deterministic_cpu(1729, 1):
            m.initialization(1729, spec)
            random.random()
            np.random.random()
            torch.rand(3)
            if failure:
                raise RuntimeError("injected")
    except RuntimeError:
        pass
    assert random.getstate() == py and np.array_equal(
        np.random.get_state()[1], np_state[1]
    )
    assert np.random.get_state()[2:] == np_state[2:] and torch.equal(
        torch.get_rng_state(), ts
    )
    assert (
        torch.get_num_threads() == threads
        and torch.are_deterministic_algorithms_enabled() == det
        and torch.is_deterministic_algorithms_warn_only_enabled() == warn
    )


@pytest.mark.parametrize("seed", p.SEEDS)
def test_actual_loader_stream_and_4097_tail(seed):
    x = np.zeros((4097, 8), np.float32)
    x[:, 0] = np.arange(4097)
    historical = feature_loader(x, 4096, shuffle=True, seed=seed)
    current = m.PairedLoader(x, arm="nonlinear", seed=seed)
    hashes = []
    for _ in range(2):
        expected = torch.cat(list(historical))[:, 0].numpy().astype("<i8")
        actual = torch.cat(list(current))[:, 0].numpy().astype("<i8")
        assert np.array_equal(expected, actual)
        assert current.epochs[-1]["batch_sizes"] == [4096, 1]
        assert (
            current.epochs[-1]["order_sha256"]
            == hashlib.sha256(expected.tobytes()).hexdigest()
        )
        hashes.append(current.epochs[-1]["order_sha256"])
    assert hashes[0] != hashes[1]


@pytest.mark.parametrize(
    "mutation", ["seed", "arm", "order", "count", "initial", "partial", "values"]
)
def test_pair_rejects_misalignment(mutation):
    x = values()
    n = m.PairedLoader(x, arm="nonlinear", seed=1729)
    linear_model = m.PairedLoader(x, arm="linear", seed=1729)
    list(n)
    list(linear_model)
    initial = "a" * 64
    if mutation == "seed":
        linear_model.seed = 1730
    if mutation == "arm":
        linear_model.arm = "nonlinear"
    if mutation == "order":
        linear_model.epochs[0]["order_sha256"] = "b" * 64
    if mutation == "count":
        linear_model.epochs[0]["count"] -= 1
    if mutation == "initial":
        initial = "b" * 64
    if mutation == "partial":
        linear_model.pending = {"count": 1, "complete": False}
    if mutation == "values":
        linear_model.feature_hash = "b" * 64
    with pytest.raises(ValueError):
        m.accept_pair(n, linear_model, "a" * 64, initial)


def test_divergent_completed_epochs_not_retrained():
    n = m.PairedLoader(values(), arm="nonlinear", seed=1729)
    linear_model = m.PairedLoader(values(), arm="linear", seed=1729)
    list(n)
    list(linear_model)
    list(n)
    assert (
        m.accept_pair(n, linear_model, "a" * 64, "a" * 64)["missing_later_epochs"] == 1
    )


def test_incomplete_epoch_and_duplicate_rows():
    loader = m.PairedLoader(values(4097), arm="nonlinear", seed=1729)
    iterator = iter(loader)
    next(iterator)
    iterator.close()
    with pytest.raises(ValueError):
        list(loader)
    loader = m.PairedLoader(values(2), arm="nonlinear", seed=1729)
    loader.loader = [(torch.zeros((2, 8)), torch.tensor([0, 0]))]
    with pytest.raises(ValueError):
        list(loader)


def test_selection_strict_ties_deterioration_and_own_restore(pair):
    initial, n, linear_model = pair
    s = m.Selection(n, initial["parameters_digest"], values())
    assert not s.update(1, 1.0, n)
    selected = m.parameter_document(n)
    with torch.no_grad():
        next(n.parameters()).add_(1)
    for epoch in range(2, 17):
        assert s.update(epoch, 1.0 if epoch < 4 else 2.0, n) == (epoch == 16)
    result = s.restore(n)
    assert result["selected_epoch"] == 1 and result["stop_reason"] == "patience"
    assert m.parameter_document(n) == selected
    with pytest.raises(ValueError):
        s.restore(linear_model)


def test_divergent_stopping_and_independent_best(pair):
    initial, n, linear_model = pair
    a = m.Selection(n, initial["parameters_digest"], values())
    b = m.Selection(linear_model, initial["parameters_digest"], values())
    for e in range(1, 17):
        stop_a = a.update(e, 1.0, n)
    for e in range(1, 18):
        stop_b = b.update(e, 1.0 if e == 1 else 0.5, linear_model)
    assert stop_a and stop_b and a.completed_epochs == 16 and b.completed_epochs == 17
    assert a.stopping.best_epoch == 1 and b.stopping.best_epoch == 2
    assert a.best is not b.best


@pytest.mark.parametrize("loss", [float("nan"), float("inf"), -1.0])
def test_nonfinite_or_invalid_selection(pair, loss):
    initial, n, _ = pair
    s = m.Selection(n, initial["parameters_digest"], values())
    with pytest.raises(ValueError):
        s.update(1, loss, n)


def test_missing_incomplete_and_restore_failure(pair, monkeypatch):
    initial, n, _ = pair
    s = m.Selection(n, initial["parameters_digest"], values())
    with pytest.raises(ValueError):
        s.restore(n)
    with pytest.raises(ValueError):
        s.update(1, 1.0, n, complete=False)
    s.update(1, 1.0, n)
    monkeypatch.setattr(n, "load_state_dict", lambda *a, **k: None)
    with torch.no_grad():
        next(n.parameters()).add_(1)
    with pytest.raises(ValueError):
        s.restore(n)


@pytest.mark.parametrize(
    "mutation",
    [
        "name",
        "shape",
        "dtype",
        "arm",
        "seed",
        "design",
        "bits",
        "missing",
        "extra",
        "nonfinite",
    ],
)
def test_safe_artifact_rejects_mutation(pair, mutation):
    initial, n, _ = pair
    doc = m.artifact(
        n, initialization_digest=initial["parameters_digest"], selected_epoch=1
    )
    science = doc["scientific"]
    row = science["parameters"][0]
    if mutation == "name":
        row["name"] = "foreign"
    if mutation == "shape":
        row["shape"] = [8, 6]
    if mutation == "dtype":
        row["dtype"] = "<f8"
    if mutation == "arm":
        science["arm"] = "linear"
    if mutation == "seed":
        science["seed"] = 1730
    if mutation == "design":
        science["design"] = "a" * 64
    if mutation == "bits":
        row["hex_bytes"] = "0" + row["hex_bytes"][1:]
        row["sha256"] = "b" * 64
    if mutation == "missing":
        science["parameters"].pop()
    if mutation == "extra":
        science["foreign"] = True
    if mutation == "nonfinite":
        raw = np.full((6, 8), np.nan, np.float32).tobytes()
        row["hex_bytes"] = raw.hex()
        row["sha256"] = hashlib.sha256(raw).hexdigest()
    doc["scientific_sha256"] = p.digest(science)
    with pytest.raises(ValueError):
        m.restore_artifact(
            n, doc, initialization_digest=initial["parameters_digest"], selected_epoch=1
        )


def test_artifact_roundtrip_and_historical_rejection(pair, tmp_path):
    initial, n, linear_model = pair
    doc = m.artifact(
        linear_model,
        initialization_digest=initial["parameters_digest"],
        selected_epoch=1,
    )
    path = tmp_path / "owned.json"
    p.durable_json(path, doc)
    m.restore_artifact(
        linear_model,
        p.read(path),
        initialization_digest=initial["parameters_digest"],
        selected_epoch=1,
    )
    with pytest.raises(ValueError):
        CompactAutoencoder.from_artifact(doc)


def test_FP64_before_subtraction():
    x = np.full((1, 8), 2**24, np.float32)
    y = np.full((1, 8), -1.0, np.float32)
    result = m.sse(x, y)
    assert result[0] == 8 * (2**24 + 1) ** 2
    assert result[0] != np.sum((x - y).astype(np.float64) ** 2)


@pytest.mark.parametrize(
    "purpose,role",
    [
        (a, b)
        for a in ("fit", "selection", "calibration")
        for b in (
            "test_background",
            "test_signal",
            "confirmation_background",
            "confirmation_signal",
            *p.ROLES,
        )
        if b != dict(fit=p.ROLES[0], selection=p.ROLES[1], calibration=p.ROLES[2])[a]
    ],
)
def test_roles_before_provider(purpose, role):
    provider = m.SyntheticProvider({r: values() for r in p.ROLES})
    with pytest.raises(ValueError):
        m.role_values(provider, role, purpose)
    assert provider.calls == []


def test_equal_event_loss_and_readonly_selection(pair):
    _, n, _ = pair
    x = values(4097)
    x[-1] *= 10
    prior = m.parameter_document(n)
    got = m.epoch_loss(n, feature_loader(x, 4096, shuffle=False, seed=1729))
    with torch.no_grad():
        batch = torch.from_numpy(x)
        expected = torch.nn.functional.mse_loss(n(batch), batch).item()
    assert got == pytest.approx(expected, rel=2e-7) and m.parameter_document(n) == prior


def test_synthetic_update_cap_and_counters(pair):
    _, n, _ = pair
    budget = m.SyntheticSteps()
    opt = m.optimizer(n)
    start = m.COUNTERS["optimizer_steps_completed"]
    for _ in range(2):
        m.epoch_loss(n, [torch.from_numpy(values())], opt=opt, budget=budget)
    assert m.COUNTERS["optimizer_steps_completed"] - start == 2
    with pytest.raises(ValueError):
        m.epoch_loss(n, [torch.from_numpy(values())], opt=opt, budget=budget)


@pytest.mark.parametrize("equal", [False, True])
def test_own_calibration_ties_quantile_and_provenance(pair, equal):
    initial, n, linear_model = pair
    if equal:
        with torch.no_grad():
            for param in n.parameters():
                param.zero_()
        fixture = np.zeros((21, 8), np.float32)
    else:
        fixture = values(21)
    s = m.Selection(n, initial["parameters_digest"], fixture)
    s.update(1, 1.0, n)
    restored = s.restore(n)
    provider = m.SyntheticProvider({p.ROLES[2]: fixture})
    cal = m.calibrate(n, provider, p.ROLES[2], restored)
    scores = m.score(n, fixture)
    for t in cal["record"]["thresholds"]:
        assert t["index"] == math.ceil(20 * (1 - t["alpha"]))
        assert t["value"] == np.sort(scores)[t["index"]]
    assert not m.decisions(n, fixture, cal).any()
    with pytest.raises(ValueError):
        m.decisions(linear_model, fixture, cal)
    altered = copy.deepcopy(cal)
    altered["record"]["thresholds"][0]["value"] += 1
    altered["sha256"] = p.digest(altered["record"])
    with pytest.raises(ValueError):
        m.decisions(n, fixture, altered)
    with pytest.raises(ValueError):
        m.calibrate(n, provider, p.ROLES[2], restored)


def test_all_patterns_direct_and_chunk_merge():
    rows = [[bool(pattern & (1 << j)) for j in range(6)] for pattern in range(64)]
    columns = list(map(list, zip(*rows, strict=True)))
    whole = i.Patterns().add(columns)
    split = (
        i.Patterns()
        .add([c[:19] for c in columns])
        .merge(i.Patterns().add([c[19:] for c in columns]))
    )
    direct = np.array(
        [sum(int(r[2 * j]) - int(r[2 * j + 1]) for j in range(3)) / 3 for r in rows]
    )
    assert whole.counts == split.counts == [1] * 64
    assert whole.moments()["mean"] == pytest.approx(direct.mean())
    assert whole.moments()["variance"] == pytest.approx(direct.var(ddof=1))


@pytest.mark.parametrize("n", [10, 10**12, 10**25])
def test_large_sparse_integer_moments_no_cancellation(n):
    counts = [0] * 64
    counts[21] = n - 1
    counts[42] = 1
    r = i.Patterns(counts, denominator=n).moments()
    expected = Fraction(n * ((n - 1) * 9 + 9) - ((n - 1) * 3 - 3) ** 2, 9 * n * (n - 1))
    assert r["rational_variance"] == [expected.numerator, expected.denominator]
    assert r["variance"] > 0 and r["mean"] == float(Fraction(n - 2, n))
    assert r["seed_contrasts"] == [r["mean"]] * 3


@pytest.mark.parametrize(
    "bad", [[0] * 63, [0] * 63 + [True], [0] * 63 + [-1], [0] * 63 + [1.0]]
)
def test_pattern_counts_invalid(bad):
    with pytest.raises(ValueError):
        i.Patterns(bad)


def test_decision_coverage_boolean_order_denominator():
    with pytest.raises(ValueError):
        i.Patterns(order=list(reversed(p.ORDER)))
    with pytest.raises(ValueError):
        i.Patterns([1] * 64, denominator=192)
    with pytest.raises(ValueError):
        i.Patterns().add([[True]] * 5)
    with pytest.raises(ValueError):
        i.Patterns().add([[1]] * 6)
    with pytest.raises(ValueError):
        i.Patterns().add([[True]] * 5 + [[True, False]])


@pytest.mark.parametrize("n", [0, 1, 2, 20000])
def test_undefined_and_constant_positive(n):
    result = i.eb(0.0, 0.0, n, delta=0.025, lower=-1.0, upper=1.0)
    assert result["defined"] == (n >= 2)
    if n >= 2:
        assert result["halfwidth"] > 0


def test_affine_scaling_theorem_and_family():
    a = i.eb(0.1, 0.002, 20000, delta=0.025, lower=-1.0, upper=1.0)
    b = i.eb(0.55, 0.0005, 20000, delta=0.025, lower=0.0, upper=1.0)
    assert a["halfwidth"] == pytest.approx(2 * b["halfwidth"])
    assert a["halfwidth"] == pytest.approx(
        math.sqrt(2 * 0.002 * math.log(160) / 20000) + 14 * math.log(160) / (3 * 19999)
    )
    assert 0.025 + 0.0125 + 6 * (0.0125 / 6) == pytest.approx(0.05)


@pytest.mark.parametrize(
    "variance,expected",
    [
        (0.0, 236843),
        (0.0002, 579973),
        (0.001, 1450034),
        (0.002, 2481145),
        (0.01, 10618749),
    ],
)
def test_design_planning_floors(variance, expected):
    assert i.planning_minimum(variance) == expected


def interval(lower, upper, half=0.00009):
    return dict(
        defined=True, lower=lower, upper=upper, mean=(lower + upper) / 2, halfwidth=half
    )


def gates(sig=None, bg=None, rates=None, eligible=None):
    return i.evaluate_gates(
        sig or interval(0.00021, 0.00039),
        bg or interval(-0.00005, 0.00005),
        rates or [interval(0.0008, 0.0012, 0.0002)] * 6,
        eligible or {k: True for k in i.ELIGIBILITY},
    )


@pytest.mark.parametrize(
    "lo,hi,label",
    [
        (0.00021, 0.00039, "nonlinear_advantage"),
        (-0.00039, -0.00021, "linear_advantage"),
        (-0.00009, 0.00009, "practical_equivalence"),
        (-0.0003, -0.00012, "no_practical_nonlinear_advantage"),
        (0.0002, 0.00038, "inconclusive"),
        (0.00012, 0.0003, "inconclusive"),
    ],
)
def test_gate_labels_and_precedence(lo, hi, label):
    assert gates(interval(lo, hi))["label"] == label


@pytest.mark.parametrize("key", i.ELIGIBILITY)
def test_missing_eligibility_blocks_favorable(key):
    eligible = {k: True for k in i.ELIGIBILITY}
    eligible[key] = False
    r = gates(eligible=eligible)
    assert (
        r["label"] == "inconclusive"
        and not r["claim_permitted"]
        and key in r["reasons"]
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda s, b, r: s.update(halfwidth=float(np.nextafter(0.0001, math.inf))),
        lambda s, b, r: b.update(halfwidth=float(np.nextafter(0.0001, math.inf))),
        lambda s, b, r: r[0].update(halfwidth=float(np.nextafter(0.0002, math.inf))),
        lambda s, b, r: b.update(upper=float(np.nextafter(0.0001, math.inf))),
        lambda s, b, r: r[0].update(lower=float(np.nextafter(0.00075, -math.inf))),
        lambda s, b, r: r[1].update(upper=float(np.nextafter(0.00125, math.inf))),
    ],
)
def test_exact_failure_boundaries(mutate):
    s, b, r = (
        interval(0.00021, 0.00039, 0.0001),
        interval(-0.0001, 0.0001, 0.0001),
        [
            interval(0.00075, 0.00115, 0.0002),
            interval(0.00085, 0.00125, 0.0002),
            *[interval(0.0008, 0.0012, 0.0002) for _ in range(4)],
        ],
    )
    assert gates(s, b, r)["flags"]["nonlinear_advantage"]
    mutate(s, b, r)
    assert not gates(s, b, r)["flags"]["nonlinear_advantage"]


def test_tiny_synthetic_cannot_meet_precision():
    patterns = i.Patterns([20] + [0] * 63)
    result = i.decide(patterns, patterns, {k: True for k in i.ELIGIBILITY})
    assert (
        result["label"] == "inconclusive" and "precision_failure" in result["reasons"]
    )


def test_wilson_zero_rate_conditional_only():
    result = i.wilson(0, 1000)
    assert result["zero_rate_upper_95"] == pytest.approx(1 - 0.05 ** (1 / 1000))
    assert result["wilson_95"][0] >= 0 and "descriptive" in result["scope"]


def test_no_significance_or_operational_reader_in_new_code():
    text = "\n".join(
        f.read_text()
        for f in (p.ROOT / "src/raregate/research/controlled_activation").glob("*.py")
    )
    for forbidden in (
        "spearmanr(",
        "pearsonr(",
        "roc_auc_score(",
        "average_precision_score(",
        "ProcessedStore(",
        "np.load(",
        "torch.load(",
    ):
        assert forbidden not in text


def test_explicit_FP32_independent_of_caller_default(spec):
    previous = torch.get_default_dtype()
    try:
        torch.set_default_dtype(torch.float64)
        initial = m.initialization(1729, spec)
        model = m.factory("linear", 1729, spec, initial)
        assert all(v.dtype == torch.float32 for v in model.parameters())
        assert torch.get_default_dtype() == torch.float64
    finally:
        torch.set_default_dtype(previous)


def test_affine_closed_form_FP64_reference(pair):
    _, _, linear = pair
    matrix = torch.eye(8, dtype=torch.float64)
    bias = torch.zeros(8, dtype=torch.float64)
    for layer in (
        linear.encoder[0],
        linear.encoder[2],
        linear.decoder[0],
        linear.decoder[2],
    ):
        weight = layer.weight.detach().double()
        matrix = weight @ matrix
        bias = weight @ bias + layer.bias.detach().double()
    x = torch.from_numpy(values())
    with torch.no_grad():
        result = linear(x).double()
    assert torch.allclose(result, x.double() @ matrix.T + bias, atol=2e-7, rtol=2e-6)


def test_unrestored_or_changed_state_cannot_calibrate(pair):
    initial, model, _ = pair
    provider = m.SyntheticProvider({p.ROLES[2]: values(21)})
    with pytest.raises(ValueError):
        m.calibrate(
            model,
            provider,
            p.ROLES[2],
            dict(selected_bytes_verified=True, selected_score_identity=True),
        )
    assert provider.calls == []
    select = m.Selection(model, initial["parameters_digest"], values())
    select.update(1, 1.0, model)
    restored = select.restore(model)
    with torch.no_grad():
        next(model.parameters()).add_(1)
    with pytest.raises(ValueError):
        m.calibrate(model, provider, p.ROLES[2], restored)
    assert provider.calls == []


@pytest.mark.parametrize(
    "x",
    [
        np.zeros((0, 8), np.float32),
        np.zeros((2, 7), np.float32),
        np.zeros((2, 8), np.float64),
        np.full((2, 8), np.nan, np.float32),
        "operational.npy",
    ],
)
def test_owned_feature_constraints(x):
    with pytest.raises(ValueError):
        m.features(x)


@pytest.mark.parametrize("n", [0, 1])
def test_zero_singleton_aggregate_inconclusive(n):
    patterns = i.Patterns([n] + [0] * 63)
    result = i.decide(patterns, patterns, {k: True for k in i.ELIGIBILITY})
    assert result["label"] == "inconclusive" and not result["claim_permitted"]
    assert "undefined_interval" in result["reasons"]


def test_mutated_counts_and_invalid_gate_data():
    patterns = i.Patterns([2] + [0] * 63)
    patterns.counts[0] = -1
    with pytest.raises(ValueError):
        patterns.moments()
    with pytest.raises(ValueError):
        i.evaluate_gates(
            {},
            interval(0.0, 0.0001),
            [interval(0.0008, 0.0012)] * 6,
            {k: True for k in i.ELIGIBILITY},
        )
    with pytest.raises(ValueError):
        gates(eligible={"source_accepted": True})
    assert not gates()["actual_confirmation_claim"]
