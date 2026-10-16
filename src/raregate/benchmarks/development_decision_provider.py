"""Separate Task0041 full-chain permission; old payload paths remain unchanged."""

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from raregate.benchmarks import development_decision_protocol as p
from raregate.benchmarks.development_payload_provider import (
    golden_once as golden_once,
)
from raregate.benchmarks.development_raw_adapter import (
    Approval as Approval,
)
from raregate.benchmarks.development_raw_adapter import (
    construct as construct,
)
from raregate.benchmarks.development_raw_adapter import (
    parity as parity,
)
from raregate.benchmarks.development_raw_planning import BATCHES, windows
from raregate.benchmarks.prepared_service import service


class Chain:
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
        self.returned = self.constructed = self.serviced = False
        self.read_started = self.feature_started = self.adapter_started = False
        self.returned_rows = 0
        self.raw_calls = self.feature_calls = self.service_calls = 0
        self.retained_bytes = retained_bytes
        self.peak_owned_array_bound_bytes = 0
        self.allowed = {
            tuple(int(v) for v in approval.ids[i : i + b])
            for b in BATCHES
            for i in windows(b)
        }

    def reset(self):
        self.returned = self.constructed = self.serviced = False
        self.read_started = self.feature_started = self.adapter_started = False
        self.returned_rows = 0

    def buffer_check(self, n):
        # Conservative live-chain envelope: 24 FP64 particle-sized temporaries,
        # in addition to explicit raw buffers and result/ID/scaler allocations.
        bound = self.retained_bytes + 24 * n * 700 * 3 * 8 + n * 2101 * 8 + 2 * 2**20
        p.require(bound <= 64 * 2**20, "Owned64MiB numerical buffer ceiling")
        self.peak_owned_array_bound_bytes = max(
            self.peak_owned_array_bound_bytes, bound
        )

    def read(self, request):
        self.approval.positions(
            request
        )  # before backend, including unauthorized neighbors
        p.require(
            self.clock() < self.deadline and self.raw_calls < 280,
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
        self.read_started = True
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
            self.clock() < self.deadline and self.feature_calls < 280,
            "Construction grant deadline/budget",
        )
        self.buffer_check(len(rows))
        self.feature_started = True
        self.feature_calls += 1
        features = construct(rows, parameters)
        self.constructed = True
        return features

    def public(self, model, thresholds, channels, features, b):
        p.require(
            self.clock() < self.deadline
            and self.service_calls < 328
            and b in BATCHES
            and len(features) == b,
            "Only fixed full natural CPU service; deadline/budget",
        )
        self.buffer_check(b)
        self.adapter_started = True
        self.service_calls += 1
        output = service(model, thresholds, channels, features, b, "natural")
        self.serviced = True
        return output

    def joint(self, request, parameters, model, thresholds, channels):
        features = self.features(self.read(request), parameters)
        scores, masks = self.public(model, thresholds, channels, features, len(request))
        return features, scores, masks


class Ledger:
    """Durable intents outside timer; nested progress flushed on return or exception."""

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
            model_load_attempts=0,
            model_loads=0,
            threshold_loads=0,
            model_instantiations=0,
            model_inflight=None,
            raw_requests=0,
            raw_requested_rows=0,
            raw_started_calls=0,
            raw_returned_requests=0,
            raw_returned_rows=0,
            feature_requests=0,
            feature_requested_rows=0,
            feature_started_calls=0,
            feature_completed_calls=0,
            feature_completed_rows=0,
            adapter_requests=0,
            adapter_requested_rows=0,
            adapter_started_calls=0,
            adapter_completed_calls=0,
            adapter_completed_rows=0,
            decision_completed_calls=0,
            decision_completed_rows=0,
            decision_boolean_values=0,
            inflight=None,
            by_component={},
            by_candidate={},
        )
        self.persist()

    def persist(self):
        p.durable_json(self.directory / "access.json", self.audit)

    def append(self, value):
        path = self.directory / "access-journal.jsonl"
        with path.open("a") as f:
            f.write(json.dumps(value, allow_nan=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        p.require(path.stat().st_size <= 16 * 2**20, "Access journal cap")

    def start(self, component, candidate, rows, *, chain, context):
        p.require(
            self.audit["inflight"] is None
            and candidate in ("pca-v1", "compact-autoencoder-v2"),
            "Fixed nonoverlapping operation",
        )
        self.audit["inflight"] = dict(
            component=component,
            candidate=candidate,
            rows=rows,
            chain=chain,
            context=context,
            intended_stages=["raw", "feature", "adapter_decisions"]
            if chain
            else ["adapter_decisions"],
            nested_progress="not_yet_observed;intent_durable_before_timer;flush_after_return_or_exception",
        )
        for kind in ("raw", "feature", "adapter") if chain else ("adapter",):
            self.audit[kind + "_requests"] += 1
            self.audit[kind + "_requested_rows"] += rows
        self.append(dict(status="started_intent", **self.audit["inflight"]))
        self.persist()

    def finish(self, provider, *, success):
        e = self.audit["inflight"]
        p.require(e is not None, "Started operation required")
        progress = dict(
            raw_started=provider.read_started,
            raw_returned=provider.returned,
            returned_rows=provider.returned_rows,
            feature_started=provider.feature_started,
            feature_completed=provider.constructed,
            adapter_started=provider.adapter_started,
            adapter_decisions_completed=provider.serviced,
        )
        for key, on in [
            ("raw_started_calls", provider.read_started),
            ("raw_returned_requests", provider.returned),
            ("feature_started_calls", provider.feature_started),
            ("feature_completed_calls", provider.constructed),
            ("adapter_started_calls", provider.adapter_started),
            ("adapter_completed_calls", provider.serviced),
        ]:
            self.audit[key] += int(on)
        self.audit["raw_returned_rows"] += provider.returned_rows
        self.audit["feature_completed_rows"] += e["rows"] * int(provider.constructed)
        self.audit["adapter_completed_rows"] += e["rows"] * int(provider.serviced)
        self.audit["decision_completed_calls"] += int(provider.serviced)
        self.audit["decision_completed_rows"] += e["rows"] * int(provider.serviced)
        self.audit["decision_boolean_values"] += 4 * e["rows"] * int(provider.serviced)
        for group, key in [
            ("by_component", e["component"]),
            ("by_candidate", e["candidate"]),
        ]:
            row = self.audit[group].setdefault(
                key,
                dict(
                    raw_calls=0,
                    raw_rows=0,
                    feature_calls=0,
                    feature_rows=0,
                    adapter_calls=0,
                    adapter_rows=0,
                ),
            )
            row["raw_calls"] += int(provider.returned)
            row["raw_rows"] += provider.returned_rows
            row["feature_calls"] += int(provider.constructed)
            row["feature_rows"] += e["rows"] * int(provider.constructed)
            row["adapter_calls"] += int(provider.serviced)
            row["adapter_rows"] += e["rows"] * int(provider.serviced)
        self.append(
            dict(
                status="completed" if success else "interrupted", progress=progress, **e
            )
        )
        if success:
            self.audit["inflight"] = None
        else:
            self.audit["inflight"]["nested_progress"] = progress
        self.persist()
