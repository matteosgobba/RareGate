"""Scientific inspection logic using tiny fixtures, independent of HDF5."""

import numpy as np
import pytest

from latenttrigger.data.inspection import (
    Moments,
    aggregate_observations,
    event_fingerprints,
    inspect_particles,
    precision_errors,
)


def test_multiplicity_and_padding_flags():
    particles = np.array(
        [
            [[2, 0, 0], [1, 1, 1], [0, 0, 0]],
            [[2, 0, 0], [0, 0, 0], [1, 1, 1]],
            [[2, 0, 0], [0, 1, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ],
        dtype=float,
    )
    flags = inspect_particles(particles, np.zeros(4))
    np.testing.assert_array_equal(flags["multiplicity"], [2, 2, 1, 0])
    np.testing.assert_array_equal(flags["non_trailing_padding"], [0, 1, 0, 0])
    np.testing.assert_array_equal(flags["malformed_padding"], [0, 0, 1, 0])
    np.testing.assert_array_equal(flags["empty"], [0, 0, 0, 1])
    np.testing.assert_array_equal(flags["eligible"], [1, 0, 0, 0])


@pytest.mark.parametrize(
    "value,flag", [(np.nan, "nan"), (np.inf, "infinity"), (-1, "negative_pt")]
)
def test_nonfinite_and_negative_rejected(value, flag):
    particles = np.array([[[value, 1, 1]]])
    flags = inspect_particles(particles, np.array([0]))
    assert flags[flag][0]
    assert not flags["eligible"][0]


def test_unexpected_truth_rejected():
    flags = inspect_particles(np.ones((1, 2, 3)), np.array([2]))
    assert flags["unexpected_label"][0]
    assert not flags["eligible"][0]


def test_fingerprint_order_padding_endian_and_signed_zero_invariant():
    a = np.array([[[2, -0.0, -1], [1, 1, 0], [0, 0, 0]]])
    b = np.array([[[1, 1, -0.0], [2, 0, -1], [0, 0, 0], [0, 0, 0]]], dtype=">f8")
    assert event_fingerprints(a)[0] == event_fingerprints(b)[0]
    b[0, 0, 0] += 0.01
    assert event_fingerprints(a)[0] != event_fingerprints(b)[0]


def test_fingerprint_phi_boundary_and_determinism():
    a = np.array([[[1, 0, np.pi]]])
    b = np.array([[[1, 0, -np.pi]]])
    assert event_fingerprints(a)[0] == event_fingerprints(b)[0]
    assert event_fingerprints(a)[0] == event_fingerprints(a)[0]


def test_moments_exclude_padding_and_merge_correctly():
    particles = np.array([[[2, 0, 1], [4, 1, 2], [0, 0, 0]]], dtype=float)
    values = particles[particles[:, :, 0] > 0][:, 0]
    moments = Moments()
    for value in values:
        moments.update(np.array([value]))
    result = moments.result()
    assert result["count"] == 2
    assert result["mean"] == 3
    assert result["std"] == 1
    assert result["min"] == 2
    with pytest.raises(ValueError, match="finite"):
        moments.update(np.array([np.nan]))


def test_massless_aggregate_physics_and_padding():
    particles = np.array([[[10, 0, 0], [10, 0, np.pi], [0, 0, 0]]])
    aggregates = aggregate_observations(particles)[0]
    np.testing.assert_allclose(aggregates, [2, 20, 10, 0, 0, 0, 0.5, 20], atol=1e-12)
    with pytest.raises(ValueError, match="nonempty"):
        aggregate_observations(np.zeros((1, 2, 3)))


def test_precision_round_trip_zeros_and_relative_error():
    values = np.array([[0, 0, 0], [1.234567891, -2.123456789, np.pi]])
    result = precision_errors(values)
    assert result["zeros_preserved"]
    assert 0 < max(result["max_relative_nonzero"]) < 1e-7
    assert max(result["max_absolute"]) < 2e-7
