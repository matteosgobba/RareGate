"""Duplicate grouping and embargo policy on synthetic events."""

import numpy as np
import pytest

from raregate.data.inspection import event_fingerprints
from raregate.data.splitting import (
    INVALID_GROUP,
    assign_groups,
    development_indices,
    group_events,
    split_indices,
    validate_splits,
)


def fixture_groups(n=2000):
    particles = np.zeros((n, 1, 3))
    particles[:, 0, 0] = np.arange(1, n + 1)
    fingerprints = event_fingerprints(particles)
    labels = np.zeros(n, dtype=np.uint8)
    labels[-100:] = 1
    groups = group_events(fingerprints, labels, np.ones(n, dtype=bool))
    return groups, labels


def test_duplicate_representatives_conflicts_and_quarantine():
    particles = np.array(
        [[[1, 0, 0]], [[1, 0, 0]], [[2, 0, 0]], [[3, 0, 0]], [[4, 0, 0]]]
    )
    labels = np.array([0, 1, 0, 1, 0], dtype=np.uint8)
    groups = group_events(
        event_fingerprints(particles), labels, np.array([1, 1, 1, 1, 0], bool)
    )
    assert len(groups.fingerprints) == 3
    assert groups.sizes.max() == 2
    assert groups.conflicts.sum() == 1
    assert groups.representatives[groups.conflicts][0] == 0
    assert groups.row_group[0] == groups.row_group[1]
    assert groups.row_group[4] == INVALID_GROUP
    codes = assign_groups(groups)
    assert codes[groups.conflicts][0] == 0
    validate_splits(groups, codes, labels)
    codes[groups.conflicts] = 1
    with pytest.raises(ValueError, match="quarantined"):
        validate_splits(groups, codes, labels)


def test_same_label_duplicates_atomic_and_representative_lowest_row():
    particles = np.array([[[1, 0, 0]], [[2, 0, 0]], [[1, 0, 0]]])
    labels = np.zeros(3, dtype=np.uint8)
    groups = group_events(event_fingerprints(particles), labels, np.ones(3, bool))
    codes = assign_groups(groups)
    assert groups.row_group[0] == groups.row_group[2]
    assert sorted(groups.representatives) == [0, 1]
    indices = split_indices(groups, codes)
    rows = np.concatenate(
        [
            indices[name]
            for name in ("train_background", "validation_background", "test_background")
        ]
    )
    assert sorted(rows) == [0, 1]


def test_split_determinism_disjointness_and_signal_embargo():
    groups, labels = fixture_groups()
    codes = assign_groups(groups)
    np.testing.assert_array_equal(codes, assign_groups(groups))
    assert not np.array_equal(codes, assign_groups(groups, seed=1730))
    checks = validate_splits(groups, codes, labels)
    assert checks["group_disjointness"]
    indices = split_indices(groups, codes)
    for left, right in [
        ("train_background", "validation_background"),
        ("train_background", "test_background"),
        ("validation_background", "test_background"),
    ]:
        assert not np.intersect1d(indices[left], indices[right]).size
    assert np.all(labels[indices["train_background"]] == 0)
    assert np.all(labels[indices["validation_background"]] == 0)
    assert len(indices["test_signal"]) == 100
    np.testing.assert_array_equal(
        indices["validation_background"],
        np.sort(
            np.concatenate(
                [
                    indices["validation_selection_background"],
                    indices["validation_calibration_background"],
                ]
            )
        ),
    )


def test_development_subset_deterministic_one_percent_and_no_test():
    groups, _ = fixture_groups()
    codes = assign_groups(groups)
    subsets = development_indices(groups, codes)
    for name, rows in subsets.items():
        np.testing.assert_array_equal(rows, development_indices(groups, codes)[name])
        parent = split_indices(groups, codes)[name.removeprefix("dev_")]
        assert len(rows) == len(parent) // 100
        assert np.isin(rows, parent).all()
        assert not np.isin(rows, groups.representatives[np.isin(codes, [4, 5])]).any()


def test_truth_contamination_validation_fails():
    groups, labels = fixture_groups()
    codes = assign_groups(groups)
    codes[groups.labels == 1] = 1
    with pytest.raises(ValueError, match="contamination"):
        validate_splits(groups, codes, labels)
