"""Contract mathematics, ordering before rounding and masked views."""

import json
from pathlib import Path

import numpy as np
import pytest

from raregate.data.features import (
    Parameters,
    canonicalize,
    model_view,
    particle_features,
    physical_aggregates,
    precision_regression,
    standardized_aggregates,
    wrap_phi,
)


@pytest.fixture
def config():
    return json.loads(
        (Path(__file__).parents[1] / "configs/data/lhco_rnd_v5.json").read_text()
    )


@pytest.fixture
def parameters(config):
    return Parameters.from_config(config)


def test_frozen_scalers_validate_and_do_not_fit(config):
    config["preprocessing"]["object_view"]["pt_std"] = 0
    with pytest.raises(ValueError, match="Frozen scalers"):
        Parameters.from_config(config)


def test_particle_channels_match_frozen_formulas(parameters):
    values = np.array([[np.e - 1, 1, np.pi / 2], [0, 0, -0.0], [1e30, -1, 0]])
    out = particle_features(values, parameters)
    assert out.dtype == np.float32
    np.testing.assert_allclose(
        out[:, 0],
        (np.log1p(values[:, 0]) - parameters.pt_mean) / parameters.pt_std,
        rtol=1e-7,
    )
    np.testing.assert_allclose(
        out[:, 1], (values[:, 1] - parameters.eta_mean) / parameters.eta_std, rtol=1e-7
    )
    np.testing.assert_allclose(out[0, 2:], [1, 0], atol=1e-7)
    np.testing.assert_allclose(out[1, 2:], [0, 1], atol=1e-7)
    assert np.isfinite(out).all()


def test_phi_rounding_boundaries_and_signed_zero():
    values = np.array([np.float32(np.pi), np.pi, -np.pi, 0.2, -0.0])
    wrapped = wrap_phi(values)
    assert ((wrapped >= -np.pi) & (wrapped < np.pi)).all()
    assert wrapped[3] == values[3]
    assert not np.signbit(wrapped[4])
    np.testing.assert_allclose(np.sin(wrapped), np.sin(values), atol=1e-15)
    with pytest.raises(ValueError, match="Nonfinite"):
        wrap_phi(np.array([np.inf]))


def test_all_sort_keys_and_padding_strip():
    raw = np.array(
        [[[1, 0, 1], [2, 1, 0], [2, -1, 0.5], [2, -1, -0.5], [2, -1, -0.5], [0, 0, 0]]]
    )
    chunk = canonicalize(raw)
    assert chunk.counts[0] == 5
    np.testing.assert_array_equal(chunk.original_slots[0], [3, 4, 2, 1, 0, 5])
    assert chunk.padded.dtype == np.float32
    np.testing.assert_array_equal(
        chunk.padded[0, :5], raw[0, [3, 4, 2, 1, 0]].astype(np.float32)
    )


def test_ordering_before_conversion_and_view_preserves_it(parameters):
    raw = np.array([[[1 + 2e-8, -1, 0], [1 + 4e-8, 1, 0]]])
    chunk = canonicalize(raw)
    np.testing.assert_array_equal(chunk.original_slots[0], [1, 0])
    diagnostic = precision_regression(raw, chunk)
    assert diagnostic["resorting_after_cast_changes_events"] == 1
    view = model_view(chunk.padded[chunk.valid], np.array([0, 2]), parameters, nmax=1)
    assert (
        view.features[0, 0, 1]
        == particle_features(chunk.padded[0, :1], parameters)[0, 1]
    )
    assert diagnostic["raw_max_absolute"][0] > 0


@pytest.mark.parametrize("count", [2, 383, 384, 385, 700])
def test_default_view_boundaries_padding_mask_and_all_particles_retained(
    count, parameters
):
    raw = np.zeros((1, 700, 3))
    raw[0, :count, 0] = np.arange(1, count + 1)
    chunk = canonicalize(raw)
    particles = chunk.padded[chunk.valid]
    assert len(particles) == count
    view = model_view(particles, np.array([0, count]), parameters)
    assert view.features.shape == (1, 384, 4)
    assert view.mask.dtype == bool and view.mask.sum() == min(count, 384)
    assert (view.features[~view.mask] == 0).all()
    np.testing.assert_allclose(
        view.features[0, : min(count, 384)],
        particle_features(particles[:384], parameters),
    )
    assert view.n_original[0] == count
    assert view.retained_pt_fraction[0] == pytest.approx(
        particles[:384, 0].sum(dtype=np.float64) / particles[:, 0].sum(dtype=np.float64)
    )


def test_batch_views_alternate_length_and_invalid_offsets(parameters):
    physical = np.array([[4, 0, 0], [2, 0, 0], [1, 1, 1]], dtype=np.float32)
    view = model_view(physical, np.array([0, 2, 3]), parameters, nmax=1)
    np.testing.assert_array_equal(view.mask, [[True], [True]])
    np.testing.assert_allclose(view.retained_pt_fraction, [2 / 3, 1])
    with pytest.raises(ValueError, match="offsets"):
        model_view(physical, np.array([0, 0, 3]), parameters)
    with pytest.raises(ValueError, match="Nmax"):
        model_view(physical, np.array([0, 3]), parameters, nmax=0)


def test_each_aggregate_against_hand_computable_massless_event(parameters):
    event = np.array([[[3, 1, 0], [4, -1, np.pi], [0, 0, 0]]])
    expected = [
        2,
        7,
        4,
        1 / 7,
        -1 / 7,
        np.sqrt(48) / 7,
        25 / 49,
        np.sqrt(48) * np.cosh(1),
    ]
    actual = physical_aggregates(event)
    np.testing.assert_allclose(actual[0], expected, atol=1e-12)
    transformed = np.array(expected)
    transformed[[0, 1, 2, 7]] = np.log1p(transformed[[0, 1, 2, 7]])
    expected_scaled = (
        transformed - parameters.aggregate_mean
    ) / parameters.aggregate_std
    np.testing.assert_allclose(
        standardized_aggregates(actual, parameters)[0], expected_scaled, rtol=1e-6
    )


@pytest.mark.parametrize(
    "particle", [[0, 1, 0], [-1, 0, 0], [np.nan, 0, 0], [1e100, 0, 0]]
)
def test_invalid_raw_rejected_instead_of_discarded(particle):
    with pytest.raises(ValueError):
        canonicalize(np.array([[particle]], dtype=float))


def test_fp32_zero_regression_and_wrapped_phi_error():
    raw = np.array(
        [[[float(np.float32(1.1)), 0, float(np.float32(np.pi))], [0, -0.0, 0]]]
    )
    chunk = canonicalize(raw)
    result = precision_regression(raw, chunk)
    assert result["raw_max_absolute"] == [0, 0, 0]
    assert result["raw_max_relative_nonzero"] == [0, 0, 0]
    assert 0 < result["wrapped_max_absolute"][2] < 2e-7
    assert result["zeros_preserved"]
    assert result["wrapped_phi_outside_math_interval_after_cast"] == 0
