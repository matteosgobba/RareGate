"""Validate real dev membership/views and independent raw-event semantics.

Only allowed dev background is read for numerical spot checks. Full-store
verification remains structural and does not explore held-out distributions.
"""

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from latenttrigger.data.analysis import open_raw, peak_rss_bytes, write_json
from latenttrigger.data.processed import ProcessedStore

DEV_ROLES = (
    "train_background",
    "validation_selection_background",
    "validation_calibration_background",
)


def reference_event(raw: np.ndarray, parameters) -> tuple:
    """Independent scalar math oracle for a few events, not the production path."""
    records = []
    for slot, (pt, eta, phi) in enumerate(raw):
        if pt == eta == phi == 0:
            continue
        phi = (
            (phi + math.pi) % (2 * math.pi) - math.pi
            if not -math.pi <= phi < math.pi
            else phi
        )
        records.append((float(pt), float(eta), float(phi), slot))
    records.sort(key=lambda x: (-x[0], x[1], x[2], x[3]))
    physical = np.array([record[:3] for record in records], dtype="<f4")
    physical[physical == 0] = 0
    slots = np.array([record[3] for record in records], dtype=np.uint16)
    triples = physical.astype(np.float64).tolist()
    total = math.fsum(p for p, _, _ in triples)
    px = math.fsum(p * math.cos(phi) for p, _, phi in triples)
    py = math.fsum(p * math.sin(phi) for p, _, phi in triples)
    pz = math.fsum(p * math.sinh(eta) for p, eta, _ in triples)
    energy = math.fsum(p * math.cosh(eta) for p, eta, _ in triples)
    center = math.fsum(p * eta for p, eta, _ in triples) / total
    aggregates = np.array(
        [
            len(triples),
            total,
            max(p for p, _, _ in triples),
            math.hypot(px, py) / total,
            center,
            math.sqrt(
                math.fsum(p * (eta - center) ** 2 for p, eta, _ in triples) / total
            ),
            math.fsum(p * p for p, _, _ in triples) / total**2,
            math.sqrt(max(0, energy**2 - px**2 - py**2 - pz**2)),
        ],
        dtype=np.float64,
    )
    transformed = aggregates.copy()
    for channel in (0, 1, 2, 7):
        transformed[channel] = math.log1p(transformed[channel])
    baseline = (
        (transformed - parameters.aggregate_mean) / parameters.aggregate_std
    ).astype("<f4")
    features = np.array(
        [
            [
                (math.log1p(p / parameters.pt_reference) - parameters.pt_mean)
                / parameters.pt_std,
                (eta - parameters.eta_mean) / parameters.eta_std,
                math.sin(
                    (phi + math.pi) % (2 * math.pi) - math.pi
                    if not -math.pi <= phi < math.pi
                    else phi
                ),
                math.cos(
                    (phi + math.pi) % (2 * math.pi) - math.pi
                    if not -math.pi <= phi < math.pi
                    else phi
                ),
            ]
            for p, eta, phi in triples[: parameters.nmax]
        ],
        dtype="<f4",
    )
    return physical, slots, aggregates, baseline, features


def validate(store_path: Path, data_dir: Path, repeat_path: Path | None) -> dict:
    started = time.perf_counter()
    with ProcessedStore(store_path) as store:
        manifest = store.manifest
        repeat = ProcessedStore(repeat_path) if repeat_path else None
        try:
            if repeat:
                assert (
                    manifest["scientific_sha256"]
                    == repeat.manifest["scientific_sha256"]
                )
                assert (
                    manifest["scientific"]["files"]
                    == repeat.manifest["scientific"]["files"]
                )
            count = particles = truncated = 0
            candidates = []
            for role in DEV_ROLES:
                ids = store.event_ids(role, dev_only=True)
                expected = np.load(
                    data_dir / "analysis/lhco-rd-v1" / f"dev_{role}.npy",
                    allow_pickle=False,
                )
                np.testing.assert_array_equal(ids, expected)
                candidates.append((role, int(ids[0])))
                largest = (-1, None)
                for batch in store.iter_batches(role, batch_size=256, dev_only=True):
                    view = batch.model_view()
                    assert batch.labels is None
                    assert np.isfinite(view.features).all()
                    assert np.isfinite(batch.event_aggregates).all()
                    assert np.isfinite(batch.event_features).all()
                    np.testing.assert_array_equal(
                        view.mask.sum(axis=1), np.minimum(batch.multiplicities, 384)
                    )
                    assert (view.features[~view.mask] == 0).all()
                    assert (view.retained_pt_fraction > 0).all()
                    assert (view.retained_pt_fraction <= 1 + 1e-14).all()
                    count += len(batch.event_ids)
                    particles += len(batch.particles)
                    truncated += int((batch.multiplicities > 384).sum())
                    maximum = int(np.argmax(batch.multiplicities))
                    if batch.multiplicities[maximum] > largest[0]:
                        largest = (
                            int(batch.multiplicities[maximum]),
                            int(batch.event_ids[maximum]),
                        )
                    if repeat:
                        other = repeat.read_ids(role, batch.event_ids, dev_only=True)
                        for name in (
                            "particles",
                            "offsets",
                            "original_slots",
                            "event_ids",
                            "event_aggregates",
                            "event_features",
                        ):
                            np.testing.assert_array_equal(
                                getattr(batch, name), getattr(other, name)
                            )
                        other_view = other.model_view()
                        for name in (
                            "features",
                            "mask",
                            "n_original",
                            "n_retained",
                            "retained_pt_fraction",
                        ):
                            np.testing.assert_array_equal(
                                getattr(view, name), getattr(other_view, name)
                            )
                candidates.append((role, largest[1]))
            config = json.loads((store_path / "configuration.json").read_text())
            assert count == sum(
                config["split"]["counts"][f"dev_{role}"] for role in DEV_ROLES
            )
            assert count == 8494 and particles == 1549328 and truncated == 27
            source = config["source"]
            raw_path = (
                data_dir / "raw/lhco" / str(source["record_id"]) / source["filename"]
            )
            spots = []
            with open_raw(raw_path) as handle:
                for role, event_id in candidates:
                    batch = store.read_ids(role, np.array([event_id]), dev_only=True)
                    raw = handle["/df/block0_values"][event_id, :2100].reshape(700, 3)
                    physical, slots, aggregates, baseline, features = reference_event(
                        raw, store.parameters
                    )
                    np.testing.assert_array_equal(batch.particles, physical)
                    np.testing.assert_array_equal(batch.original_slots, slots)
                    np.testing.assert_allclose(
                        batch.event_aggregates[0], aggregates, rtol=2e-12, atol=2e-9
                    )
                    np.testing.assert_allclose(
                        batch.event_features[0], baseline, rtol=2e-6, atol=2e-6
                    )
                    np.testing.assert_allclose(
                        batch.model_view().features[0, : len(features)],
                        features,
                        rtol=2e-6,
                        atol=2e-7,
                    )
                    spots.append(
                        {
                            "event_id": event_id,
                            "split": role,
                            "particles": len(physical),
                            "aggregate_max_absolute_error": float(
                                np.max(np.abs(batch.event_aggregates[0] - aggregates))
                            ),
                            "baseline_max_absolute_error": float(
                                np.max(np.abs(batch.event_features[0] - baseline))
                            ),
                            "object_max_absolute_error": float(
                                np.max(
                                    np.abs(
                                        batch.model_view().features[0, : len(features)]
                                        - features
                                    )
                                )
                            ),
                        }
                    )
            return {
                "scientific_sha256": manifest["scientific_sha256"],
                "scope": manifest["scientific"]["scope"],
                "dev_events": count,
                "dev_particles": particles,
                "dev_truncated_at_384": truncated,
                "independent_repeat_identical": repeat is not None,
                "spot_checks": spots,
                "seconds": time.perf_counter() - started,
                "peak_rss_bytes_lifetime": peak_rss_bytes(),
            }
        finally:
            if repeat:
                repeat.close()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store", type=Path, default=root / "data/processed/lhco-rd-v1/schema-v1/dev"
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument(
        "--report", type=Path, default=root / "data/task0005-validation.json"
    )
    args = parser.parse_args()
    report = validate(args.store, args.data_dir, args.repeat)
    write_json(args.report, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
