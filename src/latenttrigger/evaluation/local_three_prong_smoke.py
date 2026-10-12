"""Bounded synthetic local custody/scoring/reporting with native guards/assertion."""

import json
import tempfile
from pathlib import Path

from latenttrigger.benchmarks import protocol as p
from latenttrigger.data.three_prong_v3_runtime import ContinuousClock, IdleAssertion
from latenttrigger.evaluation.guard import Guard


def fixture(root):
    import h5py
    import numpy as np

    from latenttrigger.data.three_prong_v3_transport import hash_bytes
    from latenttrigger.evaluation import local_three_prong_protocol as q
    from latenttrigger.evaluation.three_prong_smoke import toy_spec

    spec, candidates = toy_spec(root)  # Self-contained toy models/background only.
    raw = root / "toy.h5"
    with h5py.File(raw, "a") as h:
        old = h["/df/block0_values"][:]
        for name in ("block0_values", "axis0", "block0_items"):
            del h["/df/" + name]
        h.create_dataset(
            "/df/block0_values", data=np.column_stack((old, np.ones(len(old))))
        )
        for name in ("axis0", "block0_items"):
            h.create_dataset("/df/" + name, data=np.arange(2101))
    c = ContinuousClock()
    integrity = hash_bytes(raw, clock=c, deadline=c() + 3)
    spec["source"]["local_payload_sha256"] = integrity["SHA256"]
    spec["source"]["expected_size"] = integrity["bytes"]
    spec["source"]["expected_checksum"] = integrity["MD5"]
    spec["local_payload"] = dict(path="toy.h5", **integrity)
    spec["encoding"]["widths"] = [2101]
    spec["calibrated_background_counts"] = {}
    spec["descriptive_arithmetic"] = dict(scope="synthetic preregistered arithmetic")
    historical = []
    quality = []
    for phase, entry, ref in zip(
        ("PCA", "AE"), spec["candidates"], spec["cached_background"], strict=True
    ):
        entry["thresholds"] = [
            {k: t[k] for k in ("target_fpr", "threshold")} for t in entry["thresholds"]
        ]
        bg = np.load(root / ref["path"], allow_pickle=False)
        spec["calibrated_background_counts"][phase] = [
            int((bg > t["threshold"]).sum()) for t in entry["thresholds"]
        ]
        for t, accepted in zip(
            entry["thresholds"],
            spec["calibrated_background_counts"][phase],
            strict=True,
        ):
            historical.append(
                dict(
                    candidate=entry["name"],
                    target_fpr=t["target_fpr"],
                    threshold=t["threshold"],
                    background_accepted=accepted,
                    background_total=150471,
                    signal_accepted=1,
                    signal_total=100000,
                    signal_efficiency=0.00001,
                )
            )
        quality.append(
            dict(candidate=entry["name"], roc_auc=0.5, average_precision=0.4)
        )
    # Reporting fixed100000/150471 population checks are tested separately;
    # smoke draws toy curves directly without claiming operational populations.
    spec["historical_two_prong"] = dict(
        calibrated_csv="history-cal.csv", comparison_csv="history-quality.csv"
    )
    from latenttrigger.evaluation.local_three_prong_reporting import write_csv

    write_csv(root / "history-cal.csv", historical)
    write_csv(root / "history-quality.csv", quality)
    (root / q.OUTPUT).mkdir(parents=True, exist_ok=True)
    return spec, candidates


def main():
    clock = ContinuousClock()
    started = clock()
    guard = Guard(started + 53, clock=clock, journal_limit=64 * 2**20)
    assertion = IdleAssertion(clock)
    limiter = None
    result = dict(status="failed")
    try:
        guard.__enter__()
        assertion.start(started + 53)
        from latenttrigger.benchmarks import core
        from latenttrigger.evaluation import local_three_prong_core as n
        from latenttrigger.evaluation import local_three_prong_protocol as q
        from latenttrigger.evaluation.local_three_prong_audit import Audit, exposure
        from latenttrigger.evaluation.local_three_prong_reporting import draw

        spec = q.load()
        limiter, threads = core.configure_threads(spec)
        with tempfile.TemporaryDirectory(prefix="task0031-local-toy-") as folder:
            root = Path(folder).resolve()
            spec, _ = fixture(root)
            base = root / q.OUTPUT
            directory = base / "prepare"
            directory.mkdir()
            audit = Audit(directory / "access.json", dict(synthetic=True))
            manifest = n.prepare(root, spec, directory, audit, guard)
            audit.finish("body_complete")
            evaluations = []
            for phase in ("PCA", "AE"):
                directory = base / phase
                directory.mkdir()
                audit = Audit(directory / "access.json", dict(synthetic=True))
                evaluations.append(
                    n.evaluate(root, spec, phase, directory, audit, guard)
                )
                audit.finish("body_complete")
                q.require(
                    exposure(directory / "access.json")["signal_scored_presentations"]
                    == 4,
                    "Toy score once4",
                )
            directory = base / "consolidate"
            directory.mkdir()
            audit = Audit(directory / "access.json", dict(synthetic=True))
            draw(
                base,
                evaluations,
                spec["candidates"],
                directory / "roc-pr.png",
                audit,
                guard,
            )
            target = p.ROOT / "data/task0031-validation/synthetic-roc-pr.png"
            target.write_bytes((directory / "roc-pr.png").read_bytes())
            result = dict(
                status="body_complete_awaiting_exit",
                synthetic_only=True,
                prepared_rows=manifest["scientific"]["count"],
                signal_scored_presentations=8,
                operational_signal_requests=0,
                operational_fingerprint_loads=0,
                operational_cached_background_loads=0,
                optimizer_updates=0,
                native_threads_stable=threads == core.effective_threads(),
                figure_file_byte_sha256=p.file_hash(target),
                elapsed_continuous_seconds=clock() - started,
            )
    finally:
        if limiter:
            limiter.restore_original_limits()
        result["sleep_assertion"] = assertion.release(started + 55)
        guard.close()
        result.update(
            resources=guard.report(), resource_monitor_closed_continuous=clock()
        )
    if (
        guard.error
        or not result.get("native_threads_stable")
        or not result["sleep_assertion"]["released"]
    ):
        raise RuntimeError("Synthetic guard/thread/assertion failure")
    print("SYNTHETIC_RESULT=" + json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
