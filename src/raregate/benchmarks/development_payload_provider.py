"""Authenticated single-worker payload permission, selected rows and durable accounting."""

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from raregate.benchmarks import development_payload_protocol as p
from raregate.benchmarks.development_raw_adapter import Approval, construct, parity
from raregate.benchmarks.development_raw_planning import BATCHES, windows

__all__ = [
    "Approval",
    "construct",
    "parity",
    "validate_grant",
    "Ledger",
    "Payload",
    "golden_once",
]


validate_grant = p.validate_grant


class Ledger:
    """Starts and ends outside timers; errors retain returned and inflight facts."""

    def __init__(self, directory):
        self.directory = directory
        self.audit = dict(
            membership_load_attempts=0,
            membership_loads=0,
            membership_records_inspected=0,
            selected_IDs=0,
            golden_load_attempts=0,
            golden_loads=0,
            golden_rows=0,
            HDF_open_attempts=0,
            HDF_opens=0,
            HDF_closed=False,
            raw_requests=0,
            raw_requested_rows=0,
            raw_returned_requests=0,
            raw_returned_rows=0,
            feature_requests=0,
            feature_requested_rows=0,
            feature_completed_calls=0,
            feature_completed_rows=0,
            inflight=None,
            by_component={},
        )
        self.persist()

    def persist(self):
        p.durable_json(self.directory / "access.json", self.audit)

    def append(self, value):
        with (self.directory / "access-journal.jsonl").open("a") as f:
            f.write(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        p.require(
            (self.directory / "access-journal.jsonl").stat().st_size <= 16 * 2**20,
            "Access journal bound",
        )

    def start(self, component, rows, *, raw=False, feature=False, context=None):
        p.require(self.audit["inflight"] is None, "No hidden inflight operation")
        self.audit["inflight"] = dict(
            component=component, rows=rows, raw=raw, feature=feature, context=context
        )
        for kind, enabled in (("raw", raw), ("feature", feature)):
            if enabled:
                self.audit[kind + "_requests"] += 1
                self.audit[kind + "_requested_rows"] += rows
        self.append(dict(status="started", **self.audit["inflight"]))
        self.persist()

    def finish(self, provider, *, success):
        entry = self.audit["inflight"]
        p.require(entry is not None, "Started accounting required")
        comp = self.audit["by_component"].setdefault(
            entry["component"],
            dict(raw_requests=0, raw_rows=0, feature_calls=0, feature_rows=0),
        )
        if provider.returned:
            self.audit["raw_returned_requests"] += 1
            self.audit["raw_returned_rows"] += provider.returned_rows
            comp["raw_requests"] += 1
            comp["raw_rows"] += provider.returned_rows
        if provider.constructed:
            self.audit["feature_completed_calls"] += 1
            self.audit["feature_completed_rows"] += entry["rows"]
            comp["feature_calls"] += 1
            comp["feature_rows"] += entry["rows"]
        self.append(
            dict(
                status="completed" if success else "interrupted",
                returned=provider.returned,
                returned_rows=provider.returned_rows,
                constructed=provider.constructed,
                **entry,
            )
        )
        if success:
            self.audit["inflight"] = None
        self.persist()


class Payload:
    def __init__(
        self, dataset, approval, path, clock, deadline, *, permit, retained_bytes=0
    ):
        p.require(
            isinstance(permit, p.PayloadPermit)
            and permit.phase.startswith("repetition")
            and permit.pid == os.getpid()
            and permit.path == str(Path(path).absolute())
            and permit.prefix == hashlib.sha256(approval.ids.tobytes()).hexdigest()
            and permit.deadline == deadline
            and clock() < deadline,
            "Authenticated payload permit before backend",
        )
        self.dataset, self.approval = dataset, approval
        self.path = Path(path).absolute()
        p.require(
            self.path == self.path.resolve()
            and Path(dataset.file.filename).absolute() == self.path
            and dataset.name == "/df/block0_values"
            and dataset.shape == (1100000, 2101)
            and dataset.dtype == np.dtype("<f8"),
            "Bound exact payload dataset",
        )
        self.clock, self.deadline = clock, deadline
        self.returned = self.constructed = False
        self.returned_rows = 0
        self.raw_calls = self.feature_calls = 0
        self.retained_bytes = retained_bytes
        self.peak_owned_array_bound_bytes = 0
        self.allowed = {
            tuple(int(v) for v in approval.ids[i : i + b])
            for b in BATCHES
            for i in windows(b)
        }

    def reset(self):
        self.returned = self.constructed = False
        self.returned_rows = 0

    def buffer_check(self, n):
        # Conservative live-chain envelope: 24 FP64 particle-sized temporaries,
        # in addition to explicit raw buffers and result/ID/scaler allocations.
        bound = self.retained_bytes + 24 * n * 700 * 3 * 8 + 1024 * 8 * 4 + 2**20
        p.require(bound <= 64 * 2**20, "Owned64MiB numerical buffer ceiling")
        self.peak_owned_array_bound_bytes = max(
            self.peak_owned_array_bound_bytes, bound
        )

    def read(self, request):
        self.approval.positions(
            request
        )  # before backend, including unauthorized neighbors
        p.require(
            self.clock() < self.deadline and self.raw_calls < 244,
            "Raw grant deadline/budget",
        )
        p.require(
            tuple(int(v) for v in request) in self.allowed,
            "Only fixed approved windows",
        )
        p.require(
            self.dataset.id.valid
            and Path(self.dataset.file.filename).absolute() == self.path,
            "Live owned readonly dataset",
        )
        self.buffer_check(len(request))
        self.raw_calls += 1
        selection = (
            slice(int(request[0]), int(request[-1]) + 1)
            if int(request[-1]) - int(request[0]) + 1 == len(request)
            else request.tolist()
        )
        rows = self.dataset[selection, :]
        self.returned = True
        self.returned_rows = (
            int(rows.shape[0]) if isinstance(rows, np.ndarray) and rows.ndim == 2 else 0
        )
        p.require(
            isinstance(rows, np.ndarray)
            and rows.shape == (len(request), 2101)
            and rows.dtype == np.dtype("<f8")
            and rows.flags.c_contiguous
            and rows.flags.owndata,
            "Exact owned selected rows",
        )
        p.require(np.all(rows[:, 2100] == 0), "Approved background truth guard")
        return rows

    def features(self, rows, parameters):
        p.require(
            self.clock() < self.deadline and self.feature_calls < 256,
            "Construction grant deadline/budget",
        )
        self.buffer_check(len(rows))
        self.feature_calls += 1
        features = construct(rows, parameters)
        self.constructed = True
        return features

    def joint(self, request, parameters):
        return self.features(self.read(request), parameters)


def golden_once(path, spec, ledger):
    a = ledger.audit
    p.require(a["golden_load_attempts"] == 0, "One golden load per worker")
    p.require(
        path.absolute() == path.resolve() and p.file_hash(path) == spec["file_sha256"],
        "Golden byte identity",
    )
    p.header(path, [1024, 8], "<f4", 32896)
    a.update(golden_load_attempts=1, golden_inflight=True)
    ledger.persist()
    values = np.load(path, allow_pickle=False)
    a.update(golden_loads=1, golden_rows=int(values.shape[0]))
    ledger.persist()
    p.require(
        values.shape == (1024, 8)
        and values.dtype == np.dtype("<f4")
        and values.flags.c_contiguous
        and np.isfinite(values).all()
        and hashlib.sha256(values.tobytes()).hexdigest() == spec["payload_sha256"],
        "Golden finite payload identity",
    )
    values.setflags(write=False)
    a["golden_inflight"] = False
    ledger.persist()
    return values
