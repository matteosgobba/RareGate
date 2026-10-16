"""Small independent physics/statistical oracles and ambient-state regressions."""

import math
import os
import subprocess
import sys
from itertools import permutations

import numpy as np
import pytest
import torch

from latenttrigger.data.features import canonicalize, physical_aggregates
from latenttrigger.data.inspection import AGGREGATE_NAMES, event_fingerprints
from latenttrigger.evaluation.metrics import evaluate_scores
from latenttrigger.evaluation.thresholds import background_operating_point
from latenttrigger.models.autoencoder import CompactAutoencoder
from latenttrigger.models.pca import PCAReconstruction
from latenttrigger.streaming import quota
from latenttrigger.streaming.records import Store
from latenttrigger.training.autoencoder import (
    deterministic_cpu,
    epoch_loss,
    feature_loader,
)


def test_frozen_FP32_model_ignores_ambient_default_dtype():
    previous = torch.get_default_dtype()
    try:
        with deterministic_cpu(1729, 1):
            baseline = CompactAutoencoder()
        torch.set_default_dtype(torch.float64)
        with deterministic_cpu(1729, 1):
            actual = CompactAutoencoder()
        assert torch.get_default_dtype() == torch.float64
        for key, value in actual.state_dict().items():
            assert value.dtype == torch.float32
            assert torch.equal(value, baseline.state_dict()[key])
    finally:
        torch.set_default_dtype(previous)


def test_back_to_back_physics_and_independent_pair_mass():
    # Two 5 GeV transverse massless vectors: total energy 10, zero 3-momentum.
    raw = np.array([[[5, 0, 0], [5, 0, math.pi], [0, 0, 0]]], dtype=float)
    expected = [2, 10, 5, 0, 0, 0, 0.5, 10]
    np.testing.assert_allclose(physical_aggregates(raw)[0], expected, atol=1e-14)
    # Pairwise Lorentz-product oracle, unlike production's summed four-vector.
    raw[0, 0, 1] = 0.75
    raw[0, 1, 1] = -0.25
    expected_mass = math.sqrt(50 * (math.cosh(1) + 1))
    assert physical_aggregates(raw)[0, -1] == pytest.approx(expected_mass)


@pytest.mark.parametrize("angle", [-4.2, -0.4, 1.1, 7.0])
def test_aggregate_rotation_identity_and_beam_reflection_covariance(angle):
    raw = np.array([[[5, 0.7, 0.1], [3, -0.2, 1.5], [2, 0.3, -2.0]]])
    expected = physical_aggregates(raw)
    transformed = raw.copy()
    transformed[:, :, 2] += angle
    np.testing.assert_allclose(physical_aggregates(transformed), expected, atol=1e-12)
    transformed[:, :, 1] *= -1
    expected[:, 4] *= -1  # Signed eta mean is covariant, not invariant.
    np.testing.assert_allclose(physical_aggregates(transformed), expected, atol=1e-12)


@pytest.mark.parametrize("order", list(permutations(range(3))))
def test_content_permutation_and_padding_identity(order):
    raw = np.array([[[5, 0.7, 0.1], [3, -0.2, 1.5], [2, 0.3, -2.0]]])
    other = np.pad(raw[:, order], ((0, 0), (0, 4), (0, 0)))
    assert np.array_equal(event_fingerprints(raw), event_fingerprints(other))
    np.testing.assert_array_equal(
        canonicalize(raw).padded, canonicalize(other).padded[:, :3]
    )
    np.testing.assert_allclose(physical_aggregates(other), physical_aggregates(raw))


def test_tied_ranking_and_prevalence_with_enumerated_pairs():
    # Signal 1 beats 0 and ties 1; signal 2 beats both: (1.5+2)/4 = 7/8.
    result = evaluate_scores(
        np.array([0.0, 1.0]), np.array([1.0, 2.0]), fixed_fprs=[0.0]
    )
    assert result["roc_auc"] == 7 / 8
    assert result["signal_prevalence"] == 0.5
    # Precision at score 2 is 1; at score 1 it is 2/3, each adds 1/2 recall.
    assert result["average_precision"] == pytest.approx(5 / 6)
    point = result["at_fixed_fpr"][0]
    assert point["background"]["accepted"] == 0 and point["signal"]["accepted"] == 1


def test_zero_count_upper_bound_inverts_exact_binomial_probability():
    value = background_operating_point(np.arange(10.0), 20.0)
    upper = value["zero_acceptance_upper_95"]
    assert (1 - upper) ** 10 == pytest.approx(0.05)
    assert value["rejection"] is None and value["wilson_95"][1] > 0


def test_loss_averages_events_including_short_tail():
    class Zero(torch.nn.Module):
        def forward(self, values):
            return torch.zeros_like(values)

    values = np.zeros((5, 8), dtype=np.float32)
    values[-1] = 10
    # Four zero events plus one event with channel-MSE 100; event mean = 20.
    assert epoch_loss(Zero(), feature_loader(values, 4, shuffle=False, seed=1)) == 20


def test_PCA_rank_and_score_with_known_diagonal_covariance():
    scales = np.array([10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0])
    axes = np.diag(scales)
    values = np.concatenate([axes, -axes])
    model = PCAReconstruction.fit(values, feature_names=AGGREGATE_NAMES, target=0.8)
    # Sum variances is 380; first four give 294, first five 330.
    assert model.k == 5
    np.testing.assert_allclose(
        model.score(values, feature_names=AGGREGATE_NAMES),
        np.r_[np.zeros(5), [25.0, 16.0, 9.0], np.zeros(5), [25.0, 16.0, 9.0]],
        atol=1e-25,
    )


@pytest.mark.parametrize("emergency", [False, True])
def test_exported_mapping_keeps_ownership_until_successful_close(
    tmp_path, monkeypatch, emergency
):
    assert not quota.FDS and not quota.MAPPINGS
    ledger = quota.Ledger(tmp_path, {"events.bin": 512, "other.bin": 8})
    monkeypatch.setattr(quota, "CURRENT", ledger)
    record = Store(tmp_path / "events.bin", 1, "event", True)
    mapping, fd = record.mapping, record.fd
    exported = memoryview(mapping)  # OS mmap.close must fail while exported.
    other = ledger.open(tmp_path / "other.bin", os.O_RDWR | os.O_CREAT | os.O_EXCL)
    try:
        if emergency:
            errors = quota.emergency_release(set(), tmp_path)
            assert errors and other not in quota.FDS
        else:
            with pytest.raises(BufferError):
                record.close()
            assert record.fd == fd
        assert fd in quota.FDS and any(m is mapping for m, _ in quota.MAPPINGS)
        assert not mapping.closed
        exported.release()
        if emergency:
            assert quota.emergency_release(set(), tmp_path) == []
        else:
            record.close()
            quota.close(other)
        assert mapping.closed and not quota.FDS and not quota.MAPPINGS
    finally:
        exported.release()
        if not mapping.closed:
            mapping.close()
        quota.retire_mapping(mapping)
        for handle in (fd, other):
            if handle in quota.FDS:
                quota.close(handle)


def test_mapping_cleanup_in_bounded_fresh_process(tmp_path):
    code = """
import errno, os, pathlib, sys
from latenttrigger.streaming import quota
from latenttrigger.streaming.records import Store
root = pathlib.Path(sys.argv[1])
quota.CURRENT = quota.Ledger(root, {'record.bin':512})
record = Store(root/'record.bin', 1, 'event', True)
fd = record.fd
view = memoryview(record.mapping)
assert quota.emergency_release(set(), root)
assert fd in quota.FDS and len(quota.MAPPINGS)==1
view.release()
assert quota.emergency_release(set(), root)==[]
assert not quota.FDS and not quota.MAPPINGS
try:
    os.fstat(fd)
except OSError as exc:
    assert exc.errno == errno.EBADF
else:
    raise AssertionError('native descriptor survived successful cleanup')
print('generated mapping and descriptor retired')
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert result.stdout.strip() == "generated mapping and descriptor retired"


def test_descriptor_close_failure_keeps_registry_until_confirmed_retirement(
    tmp_path, monkeypatch
):
    assert not quota.FDS and not quota.MAPPINGS
    monkeypatch.setattr(quota, "CURRENT", quota.Ledger(tmp_path, {"events.bin": 512}))
    record = Store(tmp_path / "events.bin", 1, "event", True)
    fd = record.fd
    close = os.close

    def fail(handle):
        if handle == fd:
            raise OSError("injected close failed before syscall")
        close(handle)

    monkeypatch.setattr(os, "close", fail)
    try:
        with pytest.raises(OSError, match="injected close"):
            record.close()
        assert os.fstat(fd).st_size == 512  # Independent OS oracle: still live.
        assert record.fd == fd and fd in quota.FDS
        assert record.mapping is None and not quota.MAPPINGS
    finally:
        monkeypatch.setattr(os, "close", close)
        record.close()
    assert not quota.FDS
