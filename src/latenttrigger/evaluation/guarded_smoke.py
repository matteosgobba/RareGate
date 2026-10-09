"""Native synthetic evaluation/reporting fixture; no operational artifacts/store."""

import json
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from latenttrigger.benchmarks import protocol as p
from latenttrigger.evaluation.guard import Guard


def fixture(directory, *, background=33, signal=17):
    import numpy as np
    import torch

    from latenttrigger.data.inspection import AGGREGATE_NAMES
    from latenttrigger.data.processed import FeatureBatch
    from latenttrigger.evaluation import guarded_core as n
    from latenttrigger.models.autoencoder import CompactAutoencoder
    from latenttrigger.models.pca import PCAReconstruction

    configs = [
        p.read(p.ROOT / "configs/models/pca_baseline.json"),
        p.read(p.ROOT / "configs/models/compact_autoencoder_v2.json"),
    ]
    manifest = dict(
        schema_version=1,
        scientific_sha256="synthetic-full-only",
        scientific=dict(
            scope="full",
            aggregate_channels=list(AGGREGATE_NAMES),
            config_sha256=configs[0]["input"]["preprocessing_config_sha256"],
            counts=dict(
                train_background=16, test_background=background, test_signal=signal
            ),
        ),
    )
    ratios = np.array([0.16] * 6 + [0.02] * 2)
    pca = PCAReconstruction(np.zeros(8), np.eye(8), ratios, ratios, 6, 0.95, 16)
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(1729)
        ae = CompactAutoencoder().eval()
    entries = []
    for name, model, config in zip(
        ("pca-v1", "compact-autoencoder-v2"), (pca, ae), configs, strict=True
    ):
        provenance = dict(
            model_config=config,
            model_config_sha256=p.digest(config),
            processed_scientific_sha256=manifest["scientific_sha256"],
            scope="canonical_full",
        )
        artifact = (
            model.artifact(provenance=provenance, build=dict(synthetic=True))
            if name == "pca-v1"
            else model.artifact(provenance=provenance, training=dict(training_count=16))
        )
        science = dict(
            model_scientific_sha256=artifact["scientific_sha256"],
            provenance=provenance,
            thresholds=[
                dict(target_fpr=target, threshold=t)
                for target, t in zip(
                    (0.1, 0.05, 0.01, 0.001), (0.5, 1.0, 2.0, 4.0), strict=True
                )
            ],
        )
        entry = dict(
            name=name,
            model_path=name + "-model.json",
            config_path=name + "-config.json",
            results_path=name + "-calibration.json",
            model_scientific_sha256=artifact["scientific_sha256"],
        )
        p.write(directory / entry["model_path"], artifact)
        p.write(directory / entry["config_path"], config)
        p.write(
            directory / entry["results_path"],
            dict(scientific=science, scientific_sha256=p.digest(science)),
        )
        entries.append(entry)

    class Store:
        def __init__(self, *args):
            self.manifest = manifest
            self.calls = []
            self.closed = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

        def close(self):
            self.closed = True

        def iter_features(
            self,
            split,
            *,
            batch_size,
            allow_test=False,
            include_labels=False,
            dev_only=False,
        ):
            if not allow_test or not include_labels or dev_only or batch_size != 4096:
                raise ValueError("Synthetic reader permissions.")
            self.calls.append(split)
            count = manifest["scientific"]["counts"][split]
            for start in range(0, count, batch_size):
                ids = np.arange(start, min(start + batch_size, count), dtype=np.int64)
                values = np.tile(np.arange(1, 9, dtype=np.float32) / 16, (len(ids), 1))
                values += np.float32(3 if split == "test_signal" else 0)
                yield FeatureBatch(
                    values,
                    ids,
                    np.full(len(ids), int(split == "test_signal"), np.uint8),
                )

    candidates = [n.load_candidate(directory, e) for e in entries]
    return entries, candidates, Store


def main():
    expected = dict.fromkeys(
        (
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        ),
        "1",
    )
    if any(os.environ.get(k) != v for k, v in expected.items()):
        raise ValueError("Native smoke env before imports.")
    started = time.monotonic()
    guard = Guard(started + 28)
    limiter = None
    try:
        guard.__enter__()
        from latenttrigger.benchmarks import core
        from latenttrigger.evaluation import guarded_core as n
        from latenttrigger.evaluation.guarded_reporting import reporting

        limiter, threads = core.configure_threads(
            dict(runtime=dict(thread_environment_before_imports=expected))
        )
        with TemporaryDirectory(prefix="task0026-native-smoke-") as raw:
            d = Path(raw)
            entries, candidates, Store = fixture(d)
            for phase, candidate in zip(("PCA", "AE"), candidates, strict=True):
                target = d / phase
                target.mkdir()
                store = Store()
                n.evaluate_candidate(
                    candidate,
                    store,
                    target,
                    dict(synthetic_only=True),
                    guard,
                    authorized=True,
                )
                store.close()
            reporting(d, entries, make_figures=True)
        if threads != core.effective_threads():
            raise ValueError("Smoke effective native threads drift.")
    finally:
        if limiter:
            limiter.restore_original_limits()
        guard.close()
    if guard.error:
        raise ValueError(guard.error)
    print(
        json.dumps(
            dict(
                status="body_complete_awaiting_exit",
                synthetic_only=True,
                operational_custody_operations=0,
                real_population_requests=0,
                wall_seconds=time.monotonic() - started,
                resources=guard.report(),
                resource_monitor_closed_monotonic=time.monotonic(),
                effective_threads=threads,
            ),
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
