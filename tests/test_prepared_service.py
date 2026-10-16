"""Task0038 tests only owned synthetic arrays/models and text fixtures."""

import copy
import json

import numpy as np
import pytest

from raregate.benchmarks import core
from raregate.benchmarks import prepared_service as s
from raregate.benchmarks import prepared_service_numerics as n
from raregate.benchmarks import prepared_service_protocol as p
from raregate.benchmarks.prepared_service_worker import synthetic_models


@pytest.mark.parametrize("b,m", p.CASES)
def test_owned_padding_and_full_semantics(b, m):
    values = np.arange(m * 8, dtype=np.float32).reshape(m, 8)
    for strategy in ("natural", "padded"):
        packed = s.pack(values, b, strategy)
        assert not np.shares_memory(values, packed)
        assert packed.flags.c_contiguous and np.array_equal(packed[:m], values)
        assert np.array_equal(packed[m:], np.zeros((len(packed) - m, 8), np.float32))
    if m == b:
        assert np.array_equal(s.pack(values, b, "natural"), s.pack(values, b, "padded"))


@pytest.mark.parametrize("b,m", p.CASES)
def test_paired_schedule(b, m):
    windows = s.starts(m)
    rows = list(s.schedule(b, m, 50))
    assert len(rows) == 50 and sum(r[2][0] == "natural" for r in rows) == 25
    assert all(start == windows[i % len(windows)] for i, start, _ in rows)
    assert s.starts(1024) == (0,) and len(s.starts(m)) == len(set(s.starts(m)))
    assert list(s.schedule(b, m, 10))[0] == list(s.schedule(b, m, 50))[0]


@pytest.mark.parametrize("rep", (1, 2, 3))
def test_fixed_cases(rep):
    assert s.cases(rep) == (tuple(reversed(p.CASES)) if rep == 2 else p.CASES)
    assert len(p.CASES) == 17
    assert 3 * 2 * 17 * 2 == 204 and 204 * 50 == 10200 and 204 * 10 == 2040


@pytest.mark.parametrize("value", (0, -1, True, 1.5, 1025))
def test_bad_m(value):
    with pytest.raises(ValueError):
        s.starts(value)


@pytest.mark.parametrize("mode", ("bad", "shape", "dtype", "strided"))
def test_invalid_packing(mode):
    x = np.ones((2, 8), np.float32)
    strategy = "natural"
    if mode == "bad":
        strategy = "adaptive"
    if mode == "shape":
        x = np.ones((2, 7), np.float32)
    if mode == "dtype":
        x = x.astype(np.float64)
    if mode == "strided":
        x = np.ones((2, 16), np.float32)[:, ::2]
    with pytest.raises(ValueError):
        s.pack(x, 8, strategy)


def test_score_cast_ties_dummy_excluded_after_scoring():
    class Model:
        def score(self, values, feature_names):
            self.rows = len(values)
            return np.array(
                [1.0, 2.0, 3.0, 4.0, 100.0, 100.0, 100.0, 100.0], np.float64
            )

    model = Model()
    thresholds = np.array([1.0, 2.0, 3.0, 4.0])
    scores, mask = s.service(
        model, thresholds, [], np.ones((2, 8), np.float32), 8, "padded"
    )
    assert model.rows == 8 and scores.tolist() == [1, 2]
    assert mask.tolist() == [[False] * 4, [True, False, False, False]]
    assert not np.shares_memory(scores, mask)


def test_linear_quantiles_population_sd():
    r = s.distribution([1, 3, 5, 7])
    assert r["mean_ns"] == 4 and r["population_std_ns"] == np.sqrt(5)
    assert r["p50_ns"] == 4 and r["p95_ns"] == pytest.approx(6.7)
    assert s.distribution([-5, 5])["mean_ns"] == 0
    for value in ([np.nan], [], [[1, 2]]):
        with pytest.raises(ValueError):
            s.distribution(value)


@pytest.mark.parametrize("candidate", ("pca-v1", "compact-autoencoder-v2"))
def test_new_shape_proof_only_synthetic(candidate):
    values, models, thresholds = synthetic_models()
    model = models[candidate]
    original = core.parameter_hash(model)
    audit = {}
    before = n.verify(model, values, thresholds, p.load()["input"]["channels"], audit)
    assert before["status"] == "passed" and before["windows_strategies_checked"] == 96
    assert before["mismatches_per_threshold"] == [0] * 4
    assert core.parameter_hash(model) == original
    assert (
        audit["canonical_adapter_calls"]
        == audit["canonical_adapter_completed_calls"]
        == 289
    )
    assert audit["proof_inflight"] is None
    if candidate.startswith("compact"):
        assert all(not module._forward_hooks for module in model.modules())


def test_unsupported_arithmetic_and_mutation(monkeypatch):
    from raregate.benchmarks import arithmetic_cpu_v2 as a

    for v in ([np.inf], [2.0**-45], [2.0**45]):
        with pytest.raises(a.ArithmeticFailure):
            a.supported(v)
    a.supported(np.zeros((8, 8), np.float32))
    values, models, t = synthetic_models()
    model = models["pca-v1"]
    original = model.score

    def mutate(x, **kw):
        output = original(x, **kw)
        model.mean[0] += 1
        return output

    monkeypatch.setattr(model, "score", mutate)
    with pytest.raises(ValueError):
        n.verify(model, values, t, p.load()["input"]["channels"], {})


def prepared_fixture(tmp_path):
    x = np.arange(8192, dtype=np.float32).reshape(1024, 8)
    spec = copy.deepcopy(p.load())
    path = tmp_path / spec["input"]["path"]
    path.parent.mkdir(parents=True)
    np.save(path, x, allow_pickle=False)
    spec["input"]["file_sha256"] = p.file_hash(path)
    spec["input"]["array_bytes_sha256"] = core.array_hash(x)
    return spec, path


def test_single_synthetic_array_load_durable_before(tmp_path, monkeypatch):
    spec, path = prepared_fixture(tmp_path)
    audit = {}
    events = []
    original = np.load

    def load(*args, **kwargs):
        assert events[-1]["prepared_array_load_attempts"] == 1
        return original(*args, **kwargs)

    monkeypatch.setattr(np, "load", load)
    n.load_prepared(spec, audit, lambda: events.append(audit.copy()), root=tmp_path)
    assert audit["prepared_array_loads"] == 1 and audit["prepared_rows_loaded"] == 1024
    with pytest.raises(ValueError):
        n.load_prepared(spec, audit, lambda: None, root=tmp_path)
    assert path.is_file()


@pytest.mark.parametrize(
    "failure", ("altered", "missing", "symlink", "header", "role", "payload")
)
def test_source_rejections_before_numeric_load(tmp_path, failure, monkeypatch):
    spec, path = prepared_fixture(tmp_path)
    if failure == "altered":
        path.write_bytes(path.read_bytes()[:-1] + b"x")
    if failure == "missing":
        path.unlink()
    if failure == "symlink":
        target = tmp_path / "fixture.npy"
        path.rename(target)
        path.symlink_to(target)
    if failure == "header":
        np.save(path, np.zeros((512, 16), np.float32))
        spec["input"]["file_sha256"] = p.file_hash(path)
    if failure == "role":
        spec["input"]["path"] = "test.npy"
    if failure == "payload":
        spec["input"]["array_bytes_sha256"] = "0" * 64
    if failure != "payload":
        monkeypatch.setattr(
            np, "load", lambda *a, **k: pytest.fail("Numerical opening before custody")
        )
    with pytest.raises((ValueError, FileNotFoundError)):
        n.load_prepared(spec, {}, lambda: None, root=tmp_path)


@pytest.mark.parametrize(
    "field", ("warmup_pairs", "timed_pairs", "models", "input", "limits", "unknown")
)
def test_strict_config(tmp_path, field):
    spec = p.load()
    spec[field] = None
    path = tmp_path / p.CONFIG
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(spec))
    with pytest.raises(ValueError):
        p.load(tmp_path)


def test_proof_call_failure_inflight_retained():
    audit = {}
    events = []
    with pytest.raises(RuntimeError):
        n.call(
            audit,
            "canonical_adapter",
            8,
            1,
            lambda: (_ for _ in ()).throw(RuntimeError("failure")),
            lambda: events.append(audit.copy()),
        )
    assert (
        audit["canonical_adapter_calls"] == 1 and audit["proof_inflight"]["rows"] == 8
    )
    assert events and "canonical_adapter_completed_calls" not in audit
