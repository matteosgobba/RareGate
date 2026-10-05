"""Training-background-only statistics; scratch streams are not model tensors."""

import gc
import os
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from latenttrigger.data.analysis import (
    CHUNK_ROWS,
    NMAX_CANDIDATES,
    file_sha256,
    open_raw,
    peak_rss_bytes,
    write_json,
)
from latenttrigger.data.inspection import (
    AGGREGATE_NAMES,
    LOG_AGGREGATES,
    Moments,
    aggregate_observations,
    precision_errors,
)
from latenttrigger.data.metadata import LHCO_RD
from latenttrigger.data.splitting import (
    PROTOCOL,
    SEED,
    Groups,
    assign_groups,
    development_indices,
    split_indices,
    validate_splits,
)

QUANTILES = (0.001, 0.01, 0.05, 0.1, 0.5, 0.9, 0.95, 0.99, 0.995, 0.999)


def disk_statistics(path: Path, count: int, *, log: bool = False) -> dict:
    """Exact linear quantiles with mapped in-place partition and bounded histogram.

    For log1p quantiles, transform interpolation endpoints, not the interpolated
    raw quantile. Only scratch order changes; source rows and indices do not.
    """
    if count < 1:
        raise ValueError("Statistics require a nonempty stream.")
    values = np.memmap(path, dtype="<f8", mode="r+", shape=(count,))
    positions = (count - 1) * np.array(QUANTILES)
    lower = np.floor(positions).astype(np.int64)
    upper = np.ceil(positions).astype(np.int64)
    values.partition(np.unique(np.concatenate([lower, upper])))
    lo, hi = np.array(values[lower]), np.array(values[upper])
    if log:
        lo, hi = np.log1p(lo), np.log1p(hi)
    quantiles = lo + (positions - lower) * (hi - lo)
    minimum, maximum = float(values.min()), float(values.max())
    if log:
        minimum, maximum = float(np.log1p(minimum)), float(np.log1p(maximum))
    edges = np.linspace(minimum, maximum if maximum > minimum else minimum + 1, 101)
    counts = np.zeros(100, dtype=np.int64)
    for start in range(0, count, 65536):
        chunk = values[start : start + 65536]
        if log:
            chunk = np.log1p(chunk)
        counts += np.histogram(chunk, bins=edges)[0]
        del chunk
    del values
    gc.collect()
    return {
        "quantiles": {
            str(q): float(v) for q, v in zip(QUANTILES, quantiles, strict=True)
        },
        "histogram": {"edges": edges.tolist(), "counts": counts.tolist()},
    }


def summarize_multiplicity(values: np.ndarray) -> dict:
    """Exact event-weighted population moments and tail quantiles."""
    return {
        "count": len(values),
        "min": int(values.min()),
        "max": int(values.max()),
        "mean": float(values.mean()),
        "std": float(values.std()),
        "quantiles": {
            str(q): float(np.quantile(values, q))
            for q in (0.5, 0.9, 0.95, 0.99, 0.995, 0.999)
        },
        "histogram": np.bincount(values.astype(int), minlength=701).tolist(),
    }


def choose_nmax(candidates: list[dict]) -> int:
    """Predeclared 99% event coverage and 0.1% mean lost scalar-pT rule."""
    for candidate in candidates:
        if (
            candidate["truncated_fraction"] <= 0.01
            and candidate["mean_lost_scalar_pt_fraction"] <= 0.001
        ):
            return candidate["nmax"]
    raise ValueError("No candidate satisfies the predeclared sequence rule.")


def verify_split_artifacts(output: Path, report: dict) -> None:
    """Reject stale/corrupted membership before training-only statistics."""
    for name, metadata in report["artifacts"].items():
        path = output / name
        if (
            path.stat().st_size != metadata["bytes"]
            or file_sha256(path) != metadata["sha256"]
        ):
            raise ValueError(f"Split artifact integrity mismatch: {name}")
    if (
        report["source"] != asdict(LHCO_RD)
        or report["seed"] != SEED
        or report.get("fingerprint_version") != "sorted-triplets-sha256-v1"
    ):
        raise ValueError("Unrecognized source or split/fingerprint policy.")
    if (
        report["protocol"] != PROTOCOL
        or report["integrity"]["eligible_events"] != report["integrity"]["events"]
        or report["duplicates"]["conflicting_label_groups"]
    ):
        raise ValueError("Unresolved integrity/quarantine issue: review before EDA.")

    def load(name: str) -> np.ndarray:
        return np.load(output / f"{name}.npy", allow_pickle=False)

    groups = Groups(
        load("group_fingerprints"),
        load("row_group"),
        load("group_representatives"),
        load("group_sizes"),
        load("group_labels"),
        load("group_conflicts"),
    )
    codes = load("group_split_codes")
    if not np.array_equal(codes, assign_groups(groups)):
        raise ValueError("Split codes do not reproduce the deterministic assignment.")
    validate_splits(groups, codes, load("labels"))
    expected = split_indices(groups, codes)
    expected.update(development_indices(groups, codes))
    for name, indices in expected.items():
        if not np.array_equal(load(name), indices):
            raise ValueError(
                f"Membership does not match frozen group assignment: {name}"
            )


def training_eda(root: Path, report: dict, *, chunk_rows: int = CHUNK_ROWS) -> dict:
    """Read frozen training-background representatives; never summarize test rows."""
    if chunk_rows < 1:
        raise ValueError("Chunk size must be positive.")
    output = root / "data" / "analysis" / PROTOCOL
    verify_split_artifacts(output, report)
    train = np.load(output / "train_background.npy", allow_pickle=False)
    labels = np.load(output / "labels.npy", allow_pickle=False)
    if np.any(labels[train] != 0):
        raise ValueError("Training labels violate the background-only embargo.")
    selection = np.zeros(len(labels), dtype=bool)
    selection[train] = True
    multiplicities = np.load(output / "multiplicities.npy", allow_pickle=False)[train]
    names = ("pt", "eta", "phi")
    scratch = output / "scratch"
    scratch.mkdir(exist_ok=True)
    paths = {name: scratch / f"{name}.f64" for name in (*names, *AGGREGATE_NAMES)}
    streams = {name: path.open("wb") for name, path in paths.items()}
    moments = {name: Moments() for name in (*names, "log1p_pt")}
    aggregate_moments = {name: Moments() for name in AGGREGATE_NAMES}
    transformed_moments = {name: Moments() for name in AGGREGATE_NAMES}
    candidates = [
        {
            "nmax": n,
            "truncated_events": 0,
            "particles_removed": 0,
            "worst_particles_removed": 0,
            "lost_fraction_sum": 0.0,
            "max_lost_scalar_pt_fraction": 0.0,
        }
        for n in NMAX_CANDIDATES
    ]
    precision = {"max_absolute": np.zeros(3), "max_relative_nonzero": np.zeros(3)}
    zeros_preserved = True
    non_descending = zero_valid = outside_phi = boundary_low = boundary_high = 0
    cos_sum = sin_sum = 0.0
    started = time.perf_counter()
    raw_path = (
        root
        / "data/raw/lhco"
        / str(report["source"]["record_id"])
        / report["source"]["filename"]
    )
    try:
        with open_raw(raw_path) as handle:
            dataset = handle["/df/block0_values"]
            checkpoint = 0
            for start in range(0, len(dataset), chunk_rows):
                stop = min(start + chunk_rows, len(dataset))
                take = selection[start:stop]
                if not take.any():
                    continue
                # Decompression touches mixed chunks. Select training rows BEFORE
                # every statistical operation; validation/test values never enter.
                particles = dataset[start:stop][take, :2100].reshape(-1, 700, 3)
                valid = particles[:, :, 0] > 0
                physical = particles[valid]
                for i, name in enumerate(names):
                    values = physical[:, i]
                    moments[name].update(values)
                    streams[name].write(values.astype("<f8", copy=False).tobytes())
                moments["log1p_pt"].update(np.log1p(physical[:, 0]))
                zero_valid += int((physical[:, 0] == 0).sum())
                phi = physical[:, 2]
                outside_phi += int(((phi < -np.pi) | (phi >= np.pi)).sum())
                boundary_low += int((phi < -np.pi + 0.01).sum())
                boundary_high += int((phi >= np.pi - 0.01).sum())
                sin_sum += float(np.sin(phi).sum())
                cos_sum += float(np.cos(phi).sum())
                errors = precision_errors(physical)
                for name in precision:
                    precision[name] = np.maximum(precision[name], errors[name])
                zeros_preserved &= errors["zeros_preserved"] and bool(
                    np.all(particles[~valid].astype(np.float32) == 0)
                )
                pt = particles[:, :, 0]
                non_descending += int((pt[:, 1:] > pt[:, :-1]).any(axis=1).sum())
                ordered_pt = np.sort(pt, axis=1)[:, ::-1]
                total = pt.sum(axis=1)
                counts = valid.sum(axis=1)
                for candidate in candidates:
                    n = candidate["nmax"]
                    removed = np.maximum(counts - n, 0)
                    lost = ordered_pt[:, n:].sum(axis=1) / total
                    candidate["truncated_events"] += int((removed > 0).sum())
                    candidate["particles_removed"] += int(removed.sum())
                    candidate["worst_particles_removed"] = max(
                        candidate["worst_particles_removed"], int(removed.max())
                    )
                    candidate["lost_fraction_sum"] += float(lost.sum())
                    candidate["max_lost_scalar_pt_fraction"] = max(
                        candidate["max_lost_scalar_pt_fraction"], float(lost.max())
                    )
                aggregates = aggregate_observations(particles)
                for i, name in enumerate(AGGREGATE_NAMES):
                    values = aggregates[:, i]
                    aggregate_moments[name].update(values)
                    streams[name].write(values.astype("<f8", copy=False).tobytes())
                    transformed = np.log1p(values) if i in LOG_AGGREGATES else values
                    transformed_moments[name].update(transformed)
                if stop * 10 // len(dataset) > checkpoint:
                    checkpoint = stop * 10 // len(dataset)
                    print(
                        f"Training-only feature scan: {100 * stop / len(dataset):.0f}%",
                        flush=True,
                    )
    finally:
        for stream in streams.values():
            stream.close()
    scan_seconds = time.perf_counter() - started
    started = time.perf_counter()
    feature_stats = {}
    for name in (*names, "log1p_pt"):
        print(f"Exact disk-backed quantiles: {name}", flush=True)
        feature_stats[name] = {
            **moments[name].result(),
            **disk_statistics(
                paths["pt" if name == "log1p_pt" else name],
                moments[name].count,
                log=name == "log1p_pt",
            ),
        }
    aggregate_stats = {}
    for i, name in enumerate(AGGREGATE_NAMES):
        aggregate_stats[name] = {
            **aggregate_moments[name].result(),
            **disk_statistics(paths[name], len(train)),
            "transformed_mean": transformed_moments[name].mean,
            "transformed_std": transformed_moments[name].result()["std"],
            "transform": "log1p" if i in LOG_AGGREGATES else "identity",
        }
    for candidate in candidates:
        truncated = candidate["truncated_events"]
        candidate["truncated_fraction"] = truncated / len(train)
        candidate["mean_particles_removed_when_truncated"] = (
            candidate["particles_removed"] / truncated if truncated else 0.0
        )
        candidate["mean_lost_scalar_pt_fraction"] = candidate.pop(
            "lost_fraction_sum"
        ) / len(train)
    config = {
        "schema_version": 1,
        "source": report["source"],
        "source_integrity": report["source_integrity"],
        "analysis_provenance": {
            "base_commit": report["code_base_commit"],
            "code_working_tree_dirty": report["code_working_tree_dirty"],
            "fingerprint_version": report["fingerprint_version"],
            "environment": report["environment"],
            "split_array_sha256": {
                name: report["artifacts"][name]["sha256"]
                for name in (
                    "train_background.npy",
                    "validation_background.npy",
                    "test_background.npy",
                    "test_signal.npy",
                    "group_split_codes.npy",
                )
            },
            "analysis_code_sha256": {
                str(path.relative_to(root)): file_sha256(path)
                for path in sorted(
                    [
                        *(root / "src/latenttrigger/data").glob("*.py"),
                        root / "scripts/analyze_training_data.py",
                    ]
                )
            },
            "quantile_method": "Exact NumPy linear quantiles via in-place memory-mapped partition",
            "statistical_population": "Only unique train_background representatives; no validation/test feature statistics",
        },
        "split": {
            "protocol": report["protocol"],
            "seed": report["seed"],
            "counts": report["counts"],
            "validation": report["split_validation"],
            "development_subset": report["development_subset"],
        },
        "integrity": report["integrity"],
        "duplicates": report["duplicates"],
        "training_background": {
            "multiplicity": summarize_multiplicity(multiplicities),
            "features": feature_stats,
            "valid_particle_zero_pt": zero_valid,
            "phi_outside_minus_pi_pi": outside_phi,
            "phi_within_0_01_of_lower_boundary": boundary_low,
            "phi_within_0_01_of_upper_boundary": boundary_high,
            "phi_mean_sin": sin_sum / moments["phi"].count,
            "phi_mean_cos": cos_sum / moments["phi"].count,
            "raw_order_non_descending_events": non_descending,
            "precision": {
                **{name: values.tolist() for name, values in precision.items()},
                "zeros_preserved": zeros_preserved,
                "labels_uint8_exact": bool(np.isin(labels, [0, 1]).all()),
            },
            "aggregate_statistics": aggregate_stats,
            "sequence_candidates": candidates,
        },
        "preprocessing": {
            "canonical": {
                "dtype": "float32",
                "channels": ["pt_GeV", "eta", "phi_rad"],
                "retain_all_particles": True,
            },
            "object_view": {
                "channels": [
                    "standardized_log1p_pt",
                    "standardized_eta",
                    "sin_phi",
                    "cos_phi",
                ],
                "pt_reference_GeV": 1.0,
                "pt_mean": moments["log1p_pt"].mean,
                "pt_std": moments["log1p_pt"].result()["std"],
                "eta_mean": moments["eta"].mean,
                "eta_std": moments["eta"].result()["std"],
                "nmax": choose_nmax(candidates),
                "selection_rule": "Smallest candidate with truncation <= 1% and event-mean lost scalar pT <= 0.1%",
                "ordering": "Descending float64 source pT; ascending eta, wrapped phi, original slot for ties",
                "padding": 0.0,
                "mask_true": "real retained particle",
                "dtype": "float32",
            },
            "aggregates": {
                "version": 1,
                "channels": list(AGGREGATE_NAMES),
                "log1p_indices": list(LOG_AGGREGATES),
                "mean": [transformed_moments[name].mean for name in AGGREGATE_NAMES],
                "std": [
                    transformed_moments[name].result()["std"]
                    for name in AGGREGATE_NAMES
                ],
                "fit_population": "Unique training-background events, before truncation",
            },
            "scaling_convention": "Population std (ddof=0), fitted in float64; particle scalers weight valid training particles equally; aggregate scalers weight training events equally",
        },
    }
    write_json(root / "configs/data/lhco_rnd_v5.json", config)
    performance = {
        "training_feature_scan_seconds": scan_seconds,
        "exact_quantiles_histograms_seconds": time.perf_counter() - started,
        "peak_rss_bytes_lifetime": peak_rss_bytes(),
        "scratch_bytes": sum(path.stat().st_size for path in paths.values()),
        "chunk_rows": chunk_rows,
    }
    write_json(output / "eda-performance.json", performance)
    for path in paths.values():
        path.unlink()
    scratch.rmdir()
    print(
        f"Selected Nmax: {config['preprocessing']['object_view']['nmax']}; performance: {performance}",
        flush=True,
    )
    return config


def plot_eda(root: Path, config: dict) -> None:
    """Curate seven measured training-background panels in three small figures."""
    cache = root / "data/analysis" / PROTOCOL / "plot-cache"
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = root / "results/figures/final"
    output.mkdir(parents=True, exist_ok=True)
    stats = config["training_background"]
    context = f"LHCO R&D v5 · unique training background (n={stats['multiplicity']['count']:,})"
    hist = np.array(stats["multiplicity"]["histogram"])
    x = np.arange(len(hist))
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), constrained_layout=True)
    axes[0].stairs(hist, np.arange(len(hist) + 1) - 0.5)
    axes[0].set(xlabel="Particle multiplicity", ylabel="Events", title="Multiplicity")
    axes[1].step(x, hist.cumsum() / hist.sum(), where="post")
    axes[1].set(
        xlabel="Particle multiplicity",
        ylabel="Cumulative event fraction",
        title="Multiplicity ECDF",
        ylim=(0, 1.01),
    )
    candidates = stats["sequence_candidates"]
    axes[2].plot(
        [c["nmax"] for c in candidates],
        [100 * c["truncated_fraction"] for c in candidates],
        marker="o",
    )
    axes[2].axhline(1, color="gray", linestyle="--", label="1% criterion")
    axes[2].axvline(
        config["preprocessing"]["object_view"]["nmax"],
        color="tab:orange",
        linestyle=":",
        label="Selected Nmax",
    )
    axes[2].set(
        xlabel="Maximum retained particles",
        ylabel="Events truncated [%]",
        title="Sequence-length candidates",
    )
    axes[2].legend(fontsize=8)
    fig.suptitle(context, fontsize=10)
    fig.savefig(output / "task0004-multiplicity.png", dpi=140)
    plt.close(fig)
    for filename, names, labels in [
        (
            "task0004-momentum.png",
            ("pt", "log1p_pt"),
            ("pT [GeV]", "log(1 + pT / 1 GeV)"),
        ),
        (
            "task0004-angles.png",
            ("eta", "phi"),
            ("Pseudorapidity eta [dimensionless]", "Azimuth phi [rad]"),
        ),
    ]:
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), constrained_layout=True)
        for ax, name, label in zip(axes, names, labels, strict=True):
            histogram = stats["features"][name]["histogram"]
            ax.stairs(histogram["counts"], histogram["edges"])
            ax.set(xlabel=label, ylabel="Valid particles", title=name)
            if name == "pt":
                ax.set_yscale("log")
        fig.suptitle(context, fontsize=10)
        fig.savefig(output / filename, dpi=140)
        plt.close(fig)
