"""Generated exact/property/integration checks for schema2, never real payloads."""

import hashlib
import json
import subprocess
import sys
from collections import Counter

import h5py
import numpy as np
import pytest
import torch

from raregate.research.decisive_adc import data, models, statistics, study

TALLY = Counter()


@pytest.fixture(autouse=True)
def count_work(monkeypatch):
    initialize = models.ADCNet.__init__
    forward = models.ADCNet.forward
    score = models.public_score
    step = torch.optim.Adam.step

    def init(self, *args, **kwargs):
        initialize(self, *args, **kwargs)
        TALLY["ADC_model_constructions"] += 1

    def call(self, x):
        TALLY["ADC_forward_calls"] += 1
        TALLY["ADC_forward_rows"] += len(x)
        return forward(self, x)

    def public(model, x):
        TALLY["ADC_public_score_calls"] += 1
        TALLY["ADC_public_padded_rows"] += len(x)
        return score(model, x)

    def update(self, *args, **kwargs):
        result = step(self, *args, **kwargs)
        TALLY["toy_Adam_updates"] += 1
        return result

    monkeypatch.setattr(models.ADCNet, "__init__", init)
    monkeypatch.setattr(models.ADCNet, "forward", call)
    monkeypatch.setattr(models, "public_score", public)
    monkeypatch.setattr(torch.optim.Adam, "step", update)


def objects(n, offset=0):
    x = np.zeros((n, 19, 4), dtype=np.float64)
    for i in range(n):
        k = i + offset
        x[i, 0] = [k + 0.5, 0, 0.05 * k, 1]
        for begin, _end, kind, count in (
            (1, 5, 2, 1 + i % 4),
            (5, 9, 3, (i // 3) % 5),
            (9, 19, 4, (i // 7) % 11),
        ):
            for j in range(count):
                pt = 40 + 0.1 * k if j == 0 else (15 - j if kind != 4 else 35 - j)
                x[i, begin + j] = [
                    pt,
                    0.1 * j + 0.001 * (i % 3),
                    0.2 * j + 0.01 * i,
                    kind,
                ]
    return x


def hdf(path, x, spelling="Particles_Classes"):
    with h5py.File(path, "x") as handle:
        handle.create_dataset("Particles", data=x, compression="gzip", chunks=True)
        handle.create_dataset(
            spelling,
            data=np.asarray(
                [
                    "MET_class_1",
                    "Four_Ele_class_2",
                    "Four_Mu_class_3",
                    "Ten_Jet_class_4",
                ],
                dtype="S16",
            ),
        )
        handle.create_dataset(
            "Particles_Names",
            data=np.asarray(["Pt", "Eta", "Phi", "Class"], dtype="S5"),
        )
    return path


def generated(tmp_path):
    root = tmp_path / "generated"
    root.mkdir()
    for folder in ("raw", "prepared", "private", "ledger"):
        (root / folder).mkdir()
    paths = {
        name: hdf(root / "raw" / (name + ".h5"), objects(128, offset=10000 * j))
        for j, name in enumerate(study.SOURCES)
    }
    context = study.Study(
        root,
        tmp_path / "models",
        "generated-ADC-test-only",
        dict(
            train=32,
            selection=8,
            calibration=16,
            final_background=8,
            A_to_4l=8,
            LQ_to_btau=8,
        ),
    )
    return context, paths


@pytest.mark.parametrize("spelling", ["Particles_Classes", "Particle_Classes"])
def test_schema_spellings_and_mapping(tmp_path, spelling):
    path = hdf(tmp_path / "fixture.h5", objects(3), spelling)
    report = data.inspect_header(path)
    assert report["rows"] == 3 and report["mapping"]["classes"]["muon"] == 3


@pytest.mark.parametrize(
    "mutation", ["shape", "dtype", "classes", "names", "link", "virtual", "spellings"]
)
def test_header_rejects_contradictions(tmp_path, mutation):
    path = hdf(tmp_path / "bad.h5", objects(3))
    with h5py.File(path, "r+") as f:
        if mutation in ("shape", "dtype"):
            del f["Particles"]
            f["Particles"] = np.zeros(
                (3, 18, 4) if mutation == "shape" else (3, 19, 4),
                dtype=np.int32 if mutation == "dtype" else np.float64,
            )
        elif mutation in ("classes", "names"):
            key = "Particles_Classes" if mutation == "classes" else "Particles_Names"
            del f[key]
            f[key] = np.asarray(["wrong"], dtype="S5")
        elif mutation == "link":
            del f["Particles"]
            f["Particles"] = h5py.ExternalLink("other.h5", "Particles")
        elif mutation == "virtual":
            del f["Particles"]
            layout = h5py.VirtualLayout((3, 19, 4), dtype=np.float64)
            layout[:] = h5py.VirtualSource("other.h5", "Particles", shape=(3, 19, 4))
            f.create_virtual_dataset("Particles", layout)
        else:
            f["Particle_Classes"] = np.asarray(["wrong"], dtype="S5")
    with pytest.raises((ValueError, KeyError)):
        data.inspect_header(path)


@pytest.mark.parametrize(
    "mutation",
    ["nonfinite", "padding", "MET", "type", "cuts", "eta", "prefix", "order", "filter"],
)
def test_structural_rules(tmp_path, mutation):
    x = objects(3)
    if mutation == "nonfinite":
        x[0, 0, 2] = np.nan
    elif mutation == "padding":
        x[0, 4, 2] = 0.1
    elif mutation == "MET":
        x[0, 0, 1] = 0.2
    elif mutation == "type":
        x[0, 1, 3] = 4
    elif mutation == "cuts":
        x[0, 1, 0] = 2.9
    elif mutation == "eta":
        x[0, 1, 1] = 3.0
    elif mutation == "prefix":
        x[0, 2] = x[0, 1]
        x[0, 1] = 0
    elif mutation == "order":
        x[1, 2, 0] = 100.0
    else:
        x[0, 1, 0] = 22.0
    good, counts = data.row_rules(x)
    assert (~good).sum() >= 1 and sum(counts.values()) >= 1
    x = objects(1)
    x[0, 0, 0] = 0
    assert data.row_rules(x)[0].all()


def test_boundaries_quarantine_and_conflicts(tmp_path):
    x = objects(1)
    x[0, 1, 0] = 23.0 - 5e-6
    assert data.row_rules(x)[0].all()
    x[0, 1, 0] = 23.0 - 2e-5
    assert not data.row_rules(x)[0].all()
    context, paths = generated(tmp_path)
    with h5py.File(paths["background"], "r+") as f:
        f["Particles"][0, 0, 1] = 1
    reports = study.prepare(context, paths)
    assert reports["background"]["quarantined_rows"] == 1
    assert reports["background"]["quarantine_fraction"] == 1 / 128


@pytest.mark.parametrize("failure", ["too_many_bad", "conflict", "insufficient"])
def test_source_failures_stop_before_any_fit(tmp_path, failure):
    context, paths = generated(tmp_path)
    if failure == "too_many_bad":
        with h5py.File(paths["background"], "r+") as f:
            f["Particles"][:3, 0, 1] = 1
    elif failure == "conflict":
        with h5py.File(paths["A_to_4l"], "r+") as f:
            f["Particles"][0] = objects(1)[0]
    else:
        with h5py.File(paths["background"], "r+") as f:
            f["Particles"][:] = np.repeat(objects(1), 128, axis=0)
    with pytest.raises(ValueError, match="source-invalid"):
        study.prepare(context, paths)
    assert not context.models.exists()


def test_feature_exact_vectors_and_independent_four_vector_mass():
    x = np.zeros((1, 19, 4))
    x[0, 0] = [0, 0, 0, 1]
    x[0, 1] = [5, 0, 0, 2]
    x[0, 2] = [5, 0, np.pi, 2]
    f = data.features(x)[0]
    np.testing.assert_allclose(
        f[[0, 1, 2, 3, 4, 7, 10, 11]],
        [0, 2, 0, 0, np.log(11), np.log(6), 0, np.log(11)],
        atol=1e-14,
    )
    x = objects(20)
    f = data.features(x)
    for row, actual in zip(x, f[:, 11], strict=True):
        leptons = row[np.isin(row[:, 3], (2, 3))]
        energy = sum(p * np.cosh(e) for p, e, _, _ in leptons)
        px = sum(p * np.cos(a) for p, _, a, _ in leptons)
        py = sum(p * np.sin(a) for p, _, a, _ in leptons)
        pz = sum(p * np.sinh(e) for p, e, _, _ in leptons)
        expected = np.log1p(
            np.sqrt(max(energy * energy - px * px - py * py - pz * pz, 0))
        )
        assert actual == pytest.approx(expected, abs=2e-12)


@pytest.mark.parametrize(
    "kind", ["permutation", "padding", "rotation", "reflection", "signed_zero"]
)
def test_representation_properties(kind):
    x = objects(20)
    changed = x.copy()
    if kind == "permutation":
        changed[:, 1:5] = changed[:, [4, 2, 1, 3]]
    elif kind == "padding":
        changed[:, 4] = 0
        x[:, 4] = 0
    elif kind == "rotation":
        changed[:, :, 2] = np.where(
            changed[:, :, 3] != 0, data.wrap(changed[:, :, 2] + 0.7), 0.0
        )
    elif kind == "reflection":
        changed[:, :, 1] *= -1
    else:
        changed[changed == 0] = -0.0
    np.testing.assert_allclose(data.features(x), data.features(changed), atol=1e-12)
    if kind not in ("rotation", "reflection"):
        assert [data.fingerprint(r) for r in x] == [
            data.fingerprint(r) for r in changed
        ]


def test_canonical_bytes_oracle():
    x = np.zeros((19, 4))
    x[0] = [0, 0, 0, 1]
    x[1] = [25, 0, 0, 2]
    parts = [
        b"adc-exact-content-v2\0",
        np.array([1, 1, 0, 0, 0], dtype="<f8").tobytes(),
        np.array([2, 1, 25, 0, 0], dtype="<f8").tobytes(),
        np.array([3, 0, 4, 0], dtype="<f8").tobytes(),
    ]
    assert data.fingerprint(x) == hashlib.sha256(b"".join(parts)).digest()
    assert data.fingerprints(x[None])[0] == hashlib.sha256(b"".join(parts)).digest()
    sample = objects(128)
    sample[sample == 0] = -0.0
    assert data.fingerprints(sample) == [data.fingerprint(row) for row in sample]


def test_large_header_is_not_a_full_array_allocation(tmp_path):
    path = hdf(tmp_path / "header.h5", objects(1))
    with h5py.File(path, "r+") as f:
        del f["Particles"]
        f.create_dataset(
            "Particles",
            shape=(13451915, 19, 4),
            dtype=np.float64,
            chunks=(8192, 1, 1),
            compression="gzip",
        )
    assert path.stat().st_size < 16384
    assert data.inspect_header(path)["rows"] == 13451915
    assert (
        data.metadata_mapping(["MET", "electron", "muon", "jet"], ["pT", "eta", "phi"])[
            "classes"
        ]["jet"]
        == 4
    )


def test_roles_duplicate_representative_scaler_and_denial(tmp_path):
    context, paths = generated(tmp_path)
    with h5py.File(paths["background"], "r+") as f:
        f["Particles"][127] = f["Particles"][0]
    reports = study.prepare(context, paths)
    assert reports["background"]["unique_groups"] == 127
    assert reports["background"]["duplicate_rows"] == 1
    scaler = json.loads((context.root / "private/scaler.json").read_text())
    training = np.load(context.root / "prepared/train/objects.npy")
    expected = data.features(training)
    np.testing.assert_array_equal(scaler["mean"], expected.mean(axis=0))
    np.testing.assert_array_equal(scaler["std"], expected.std(axis=0))
    all_ids = []
    for role in context.counts:
        membership = np.load(context.root / "prepared" / role / "membership.npy")
        fingerprints = [r.tobytes() for r in membership["fingerprint"]]
        assert fingerprints == sorted(
            fingerprints, key=lambda fp: (data.split_key(fp), fp)
        )
        all_ids.extend(fingerprints)
    assert len(set(all_ids)) == len(all_ids)
    assert not (
        np.load(context.root / "prepared/train/membership.npy")["source_row"] == 127
    ).any()
    for role in ("calibration", "final_background", "A_to_4l", "LQ_to_btau"):
        with pytest.raises(PermissionError):
            context.role(role, "train")
    with pytest.raises(PermissionError):
        context.role("train", "calibrate")
    code = "from pathlib import Path; from raregate.research.decisive_adc.study import Study,install_phase_guard; import sys; s=Study(sys.argv[1],sys.argv[2],'generated-ADC-test-only',dict(train=1)); install_phase_guard(s,'train'); Path(sys.argv[3]).read_bytes()"
    private_scores = context.root / "private/forbidden-calibration.npy"
    np.save(private_scores, np.zeros(3))
    for forbidden in (
        paths["background"],
        context.root / "prepared/final_background/features.npy",
        context.root / "private/groups-v2.sqlite",
        private_scores,
    ):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                code,
                str(context.root),
                str(context.models),
                str(forbidden),
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode != 0 and "PermissionError" in result.stderr
        TALLY["bounded_negative_IO_children"] += 1
    sqlite_code = "from raregate.research.decisive_adc.study import Study,install_phase_guard; import sqlite3,sys; s=Study(sys.argv[1],sys.argv[2],'generated-ADC-test-only',dict(train=1)); install_phase_guard(s,'train'); sqlite3.connect(sys.argv[3])"
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            sqlite_code,
            str(context.root),
            str(context.models),
            str(context.root / "private/groups-v2.sqlite"),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode != 0 and "PermissionError" in result.stderr
    TALLY["bounded_negative_IO_children"] += 1


@pytest.mark.parametrize("arm,parameters", [("compactAE", 271), ("referenceAE", 1999)])
def test_cpu_fp32_factories_and_rng_isolation(arm, parameters):
    state = torch.random.get_rng_state().clone()
    before = torch.get_default_dtype()
    try:
        torch.set_default_dtype(torch.float64)
        model = models.ADCNet(arm, 1729)
        assert sum(p.numel() for p in model.parameters()) == parameters
        assert all(
            p.dtype == torch.float32 and p.device.type == "cpu"
            for p in model.parameters()
        )
        assert torch.equal(state, torch.random.get_rng_state())
    finally:
        torch.set_default_dtype(before)


def test_selected_state_ties_and_tail_order(tmp_path, monkeypatch):
    x = np.random.default_rng(1).normal(size=(17, 12)).astype(np.float32)
    states = []
    losses = iter([3.0, 2.0, 2.0, 2.0, 2.0])

    def loss(model, values, batch):
        states.append(models.state_digest(model))
        return next(losses)

    monkeypatch.setattr(models, "selection_loss", loss)
    events = []
    model, history = models.train(
        "compactAE",
        1729,
        x,
        x,
        lambda event, **v: events.append((event, v)),
        epochs=8,
        patience=2,
        batch=8,
    )
    assert history["selected_epoch"] == 2 and history["stop_reason"] == "patience"
    assert models.state_digest(model) == states[1] == states[-1]
    assert history["updates"] == 12
    assert [v["rows"] for e, v in events if e == "batch_completed"] == [8, 8, 1] * 4
    gen = torch.Generator().manual_seed(1729)
    expected = [
        hashlib.sha256(
            torch.randperm(17, generator=gen).numpy().astype("<i8").tobytes()
        ).hexdigest()
        for _ in range(4)
    ]
    assert [r["order_sha256"] for r in history["history"]] == expected


def test_analytical_oracles_and_public_tail_ownership():
    x = np.zeros((24, 12), dtype=np.float32)
    for i in range(12):
        x[2 * i, i] = 12 - i
        x[2 * i + 1, i] = -(12 - i)
    pca = models.fit_analytical("PCA3", x)
    query = np.zeros((32, 12), dtype=np.float32)
    query[0, 3] = 5
    assert models.public_score(pca, query)[0] == 25
    maha = models.fit_analytical("regularizedMahalanobis", x)
    diagonal = np.array([(12 - i) ** 2 / 12 for i in range(12)])
    expected = 25 / (0.9 * diagonal[3] + 0.1 * diagonal.mean())
    assert models.public_score(maha, query)[0] == pytest.approx(expected)
    output = models.score_rows(pca, query[:1])
    saved = output.copy()
    models.score_rows(pca, query)
    np.testing.assert_array_equal(output, saved)
    assert len(output) == 1 and output.flags.owndata


def test_calibration_ties_rank_oracle_and_sentinels():
    for alpha, expected in ((0.01, (989658, 990340)), (0.001, (998890, 999107))):
        result = statistics.calibration(np.arange(1000000, dtype=float), alpha)
        assert (
            result["lower_rank_one_based"],
            result["upper_rank_one_based"],
        ) == expected
        assert (
            result["lower_endpoint"] == expected[0] - 1
            and result["upper_endpoint"] == expected[1] - 1
        )
    tied = statistics.calibration(np.array([0, 0, 2, 2, 2, 2.0]), 0.01)
    assert tied["threshold"] == 2 and tied["accepted"] == 0 and tied["ties"] == 4
    assert tied["upper_endpoint"] == "+infinity"
    singleton = statistics.calibration(np.array([1.0]), 0.01)
    assert (
        singleton["lower_endpoint"] == "-infinity"
        and singleton["upper_endpoint"] == "+infinity"
    )
    lower, upper = statistics.exact_background_interval(0, 10)
    assert lower == 0 and (1 - upper) ** 10 == pytest.approx(0.01 / 32)
    one = statistics.paired_bound(np.full(40000, 0.1), (-0.9, 1))
    assert one["N"] == 40000 and one["mean"] == pytest.approx(0.1)
    assert one["halfwidth"] == pytest.approx(
        7 * 1.9 * np.log(4 * 44 / 0.03) / (3 * 39999)
    )
    np.testing.assert_array_equal(
        statistics.seed_indicators(np.array([[1, 0], [0, 0], [1, 1]]), [0.5] * 3),
        [2 / 3, 1 / 3],
    )
