"""Owned sparse HDF/Blosc fixtures; no real source/golden/model access."""

import hashlib

import h5py
import numpy as np

from latenttrigger.benchmarks import development_raw_adapter as adapter
from latenttrigger.benchmarks import development_raw_membership as membership
from latenttrigger.benchmarks import development_raw_metadata as metadata
from latenttrigger.benchmarks import development_raw_planning as planning
from latenttrigger.benchmarks import development_raw_protocol as p
from latenttrigger.data.features import Parameters


def parameters():
    return Parameters(0.0, 1.0, 0.0, 1.0, np.zeros(8), np.ones(8), 384)


def fixture(directory):
    ids = np.arange(6999, dtype="<i8") * 3
    selected = np.sort(ids)[:1024].copy()
    prefix = hashlib.sha256(selected.tobytes()).hexdigest()
    np.save(directory / "fixture-membership.npy", ids[::-1].copy(), allow_pickle=False)
    path = directory / "fixture.h5"
    with h5py.File(path, "w", **p.CACHE) as f:
        d = f.create_dataset(
            "/df/block0_values",
            shape=(1100000, 2101),
            dtype="<f8",
            chunks=(62, 2101),
            compression=32001,
            compression_opts=(0, 0, 0, 0, 5, 1),
        )
        for start in range(0, 1024, 128):
            event_ids = selected[start : start + 128]
            raw = np.zeros((len(event_ids), 2101), dtype="<f8")
            raw[:, 0] = 10 + event_ids * 0.01
            raw[:, 1] = 0.2
            raw[:, 2] = 0.3
            raw[:, 3:6] = [4.0, -0.2, -0.4]
            # First row retains500particles, including >384 tail.
            if start == 0:
                raw[0, :1500] = np.tile([1.0, 0.1, 0.2], 500)
            d[event_ids.tolist(), :] = raw
    return path, prefix


def run(directory, guard):
    path, prefix = fixture(directory)
    audit = {}
    spec = dict(
        file_sha256=p.file_hash(directory / "fixture-membership.npy"),
        selected_sha256=prefix,
    )
    selected = membership.load_once(
        directory / "fixture-membership.npy", spec, audit, lambda: None
    )
    md = metadata.inspect(path, p.load()["raw"]["audit_schema"], audit, lambda: None)
    approval = adapter.Approval(selected, prefix)
    params = parameters()
    checks = 0
    with h5py.File(path, "r", **p.CACHE) as f:
        d = f.get("/df/block0_values")
        # Golden fixture is GENERATED here from the same approved rows in128windows.
        golden = np.empty((1024, 8), dtype="<f4")
        for i in range(0, 1024, 128):
            golden[i : i + 128] = adapter.joint(
                d, selected[i : i + 128], approval, params
            )
        for b in planning.BATCHES:
            for position in planning.windows(b):
                guard.check()
                request = selected[position : position + b]
                raw = adapter.selected_read(d, request, approval)
                features = adapter.construct(raw, params)
                adapter.parity(features, golden, request, approval)
                adapter.parity(
                    adapter.joint(d, request, approval, params),
                    golden,
                    request,
                    approval,
                )
                checks += 2
    p.durable_json(
        directory / "synthetic.json",
        dict(
            status="synthetic_HDF_filter_cache_adapter_exact_parity_passed",
            checks=checks,
            fixture_selected_hash=prefix,
            metadata=md,
            operational_event_rows=0,
            operational_golden_loads=0,
            native_synthetic_feature_constructions=32,
            decoder_threads_effective="unknown",
        ),
        exclusive=True,
    )
    np.save(directory / "selected-ids.npy", selected, allow_pickle=False)
    p.durable_json(
        directory / "geometry.json", planning.geometry(selected), exclusive=True
    )
    return ["synthetic.json", "geometry.json", "selected-ids.npy"], audit
