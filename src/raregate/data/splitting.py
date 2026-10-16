"""Versioned exact-content groups and deterministic held-out membership."""

import hashlib
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

PROTOCOL = "lhco-rd-v1"
SEED = 1729
SPLIT_NAMES = {
    0: "quarantine",
    1: "train_background",
    2: "validation_selection_background",
    3: "validation_calibration_background",
    4: "test_background",
    5: "test_signal",
}
INVALID_GROUP = np.iinfo(np.uint32).max


@dataclass
class Groups:
    """Unique fingerprints, row membership, representatives and label conflicts."""

    fingerprints: NDArray
    row_group: NDArray
    representatives: NDArray
    sizes: NDArray
    labels: NDArray
    conflicts: NDArray


def group_events(fingerprints: NDArray, labels: NDArray, eligible: NDArray) -> Groups:
    """Group eligible content and retain lowest source-row representative."""
    rows = np.flatnonzero(eligible)
    unique, inverse, counts = np.unique(
        fingerprints[rows], return_inverse=True, return_counts=True
    )
    row_group = np.full(len(labels), INVALID_GROUP, dtype=np.uint32)
    row_group[rows] = inverse
    representatives = np.full(len(unique), len(labels), dtype=np.int64)
    np.minimum.at(representatives, inverse, rows)
    low = np.full(len(unique), 255, dtype=np.uint8)
    high = np.zeros(len(unique), dtype=np.uint8)
    np.minimum.at(low, inverse, labels[rows])
    np.maximum.at(high, inverse, labels[rows])
    return Groups(unique, row_group, representatives, counts, low, low != high)


def domain_digest(fingerprint: np.void, domain: str, seed: int = SEED) -> bytes:
    """Hash the exact documented UTF-8 domain separator and fingerprint hex."""
    content = f"{PROTOCOL}|{seed}|{domain}|{fingerprint.tobytes().hex()}"
    return hashlib.sha256(content.encode("utf-8")).digest()


def assign_groups(groups: Groups, seed: int = SEED) -> NDArray:
    """Assign whole groups, using hash fractions for 70/15/15 background splits."""
    codes = np.zeros(len(groups.fingerprints), dtype=np.uint8)
    # Integer cutoffs implement u = uint64 / 2**64 without float rounding.
    train_limit = (70 * 2**64 + 99) // 100
    validation_limit = (85 * 2**64 + 99) // 100
    for i, fingerprint in enumerate(groups.fingerprints):
        if groups.conflicts[i]:
            continue
        if groups.labels[i] == 1:
            codes[i] = 5
            continue
        value = int.from_bytes(domain_digest(fingerprint, "bg-split", seed)[:8], "big")
        if value < train_limit:
            codes[i] = 1
        elif value < validation_limit:
            role = int.from_bytes(
                domain_digest(fingerprint, "val-role", seed)[:8], "big"
            )
            codes[i] = 2 if role < 2**63 else 3
        else:
            codes[i] = 4
    return codes


def split_indices(groups: Groups, codes: NDArray) -> dict[str, NDArray]:
    """Return sorted representative rows, excluding quarantined groups."""
    indices = {
        name: np.sort(groups.representatives[codes == code])
        for code, name in SPLIT_NAMES.items()
        if code != 0
    }
    indices["validation_background"] = np.sort(
        np.concatenate(
            [
                indices["validation_selection_background"],
                indices["validation_calibration_background"],
            ]
        )
    )
    return indices


def development_indices(groups: Groups, codes: NDArray, seed: int = SEED) -> dict:
    """Select floor(1% of groups) independently in each permitted background role."""
    result = {}
    for code in (1, 2, 3):
        ids = np.flatnonzero(codes == code)
        ranks = np.array(
            [domain_digest(groups.fingerprints[i], "dev-subset", seed) for i in ids],
            dtype="V32",
        )
        selected = ids[np.argsort(ranks, kind="stable")[: len(ids) // 100]]
        result[f"dev_{SPLIT_NAMES[code]}"] = np.sort(groups.representatives[selected])
    return result


def validate_splits(groups: Groups, codes: NDArray, labels: NDArray) -> dict:
    """Check disjointness at group level, label embargo and row atomicity."""
    if (
        len(codes) != len(groups.fingerprints)
        or not np.isin(codes, list(SPLIT_NAMES)).all()
    ):
        raise ValueError("Invalid group split codes.")
    if np.any(codes[groups.conflicts] != 0):
        raise ValueError("Conflicting-label groups must be quarantined.")
    bg = np.isin(codes, [1, 2, 3, 4])
    if np.any(groups.labels[bg] != 0) or np.any(groups.labels[codes == 5] != 1):
        raise ValueError("Split label contamination.")
    group_sets = [set(np.flatnonzero(codes == c)) for c in (1, 2, 3, 4, 5)]
    for i, left in enumerate(group_sets):
        for right in group_sets[i + 1 :]:
            if left & right:
                raise ValueError("Duplicate groups overlap splits.")
    valid = groups.row_group != INVALID_GROUP
    row_codes = np.zeros(len(labels), dtype=np.uint8)
    row_codes[valid] = codes[groups.row_group[valid]]
    if np.any(labels[np.isin(row_codes, [1, 2, 3])] != 0):
        raise ValueError("Signal in background training or validation.")
    return {
        "group_disjointness": True,
        "background_only_training_validation": True,
        "conflicts_quarantined": True,
        "row_counts": {
            name: int((row_codes == c).sum()) for c, name in SPLIT_NAMES.items()
        },
    }
