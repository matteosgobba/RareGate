"""Exact bounded statistics and predeclared decisions on controlled data."""

from dataclasses import asdict

import numpy as np
import pytest

from raregate.data.analysis import file_sha256
from raregate.data.eda import (
    choose_nmax,
    disk_statistics,
    summarize_multiplicity,
    verify_split_artifacts,
)
from raregate.data.inspection import event_fingerprints
from raregate.data.metadata import LHCO_RD
from raregate.data.splitting import (
    PROTOCOL,
    SEED,
    assign_groups,
    development_indices,
    group_events,
    split_indices,
)


@pytest.mark.parametrize("log", [False, True])
def test_disk_quantiles_match_numpy_and_histogram_preserves_count(tmp_path, log):
    values = np.array([0.1, 1, 3, 10, 21, 100], dtype="<f8")
    path = tmp_path / "values.f64"
    values.tofile(path)
    result = disk_statistics(path, len(values), log=log)
    expected = np.log1p(values) if log else values
    for q, measured in result["quantiles"].items():
        assert measured == pytest.approx(np.quantile(expected, float(q)))
    assert sum(result["histogram"]["counts"]) == len(values)


def test_multiplicity_tail_statistics_exact():
    values = np.array([1, 2, 3, 100], dtype=np.uint16)
    result = summarize_multiplicity(values)
    assert result["mean"] == 26.5
    assert result["quantiles"]["0.5"] == 2.5
    assert result["quantiles"]["0.99"] == pytest.approx(97.09)
    assert sum(result["histogram"]) == 4


def test_sequence_rule_requires_both_coverage_and_momentum():
    candidates = [
        {
            "nmax": 64,
            "truncated_fraction": 0.02,
            "mean_lost_scalar_pt_fraction": 0.0001,
        },
        {
            "nmax": 96,
            "truncated_fraction": 0.009,
            "mean_lost_scalar_pt_fraction": 0.002,
        },
        {
            "nmax": 128,
            "truncated_fraction": 0.01,
            "mean_lost_scalar_pt_fraction": 0.001,
        },
        {
            "nmax": 160,
            "truncated_fraction": 0.001,
            "mean_lost_scalar_pt_fraction": 0.00001,
        },
    ]
    assert choose_nmax(candidates) == 128
    with pytest.raises(ValueError, match="No candidate"):
        choose_nmax(candidates[:2])


@pytest.fixture
def saved_membership(tmp_path):
    particles = np.zeros((1000, 1, 3))
    particles[:, 0, 0] = np.arange(1, 1001)
    labels = np.zeros(1000, dtype=np.uint8)
    labels[-100:] = 1
    groups = group_events(event_fingerprints(particles), labels, np.ones(1000, bool))
    codes = assign_groups(groups)
    arrays = {
        "group_fingerprints": groups.fingerprints,
        "row_group": groups.row_group,
        "group_representatives": groups.representatives,
        "group_sizes": groups.sizes,
        "group_labels": groups.labels,
        "group_conflicts": groups.conflicts,
        "group_split_codes": codes,
        "labels": labels,
        **split_indices(groups, codes),
        **development_indices(groups, codes),
    }
    for name, values in arrays.items():
        np.save(tmp_path / f"{name}.npy", values, allow_pickle=False)
    report = {
        "source": asdict(LHCO_RD),
        "seed": SEED,
        "protocol": PROTOCOL,
        "fingerprint_version": "sorted-triplets-sha256-v1",
        "integrity": {"eligible_events": 1000, "events": 1000},
        "duplicates": {"conflicting_label_groups": 0},
        "artifacts": {
            p.name: {"sha256": file_sha256(p), "bytes": p.stat().st_size}
            for p in tmp_path.glob("*.npy")
        },
    }
    verify_split_artifacts(tmp_path, report)
    return tmp_path, report


def test_split_artifact_corruption_rejected(saved_membership):
    output, report = saved_membership
    path = output / "train_background.npy"
    with path.open("r+b") as stream:
        stream.seek(-1, 2)
        stream.write(b"X")
    with pytest.raises(ValueError, match="integrity mismatch"):
        verify_split_artifacts(output, report)


def test_split_membership_semantics_checked_beyond_checksum(saved_membership):
    output, report = saved_membership
    path = output / "train_background.npy"
    np.save(path, np.array([999], dtype=np.int64), allow_pickle=False)
    report["artifacts"][path.name] = {
        "sha256": file_sha256(path),
        "bytes": path.stat().st_size,
    }
    with pytest.raises(ValueError, match="Membership does not match"):
        verify_split_artifacts(output, report)


def test_split_policy_mismatch_rejected(saved_membership):
    output, report = saved_membership
    report["seed"] += 1
    with pytest.raises(ValueError, match="Unrecognized"):
        verify_split_artifacts(output, report)
