"""Closed Task0045 selected prefix/side authority; unchanged feature and service math."""

import hashlib
import os
from pathlib import Path

import numpy as np

from raregate.benchmarks import partial_raw_planning as plan
from raregate.benchmarks import partial_raw_protocol as p
from raregate.benchmarks.development_decision_provider import (
    Ledger as OriginalLedger,
)
from raregate.benchmarks.development_payload_provider import (
    golden_once as golden_once,
)
from raregate.benchmarks.development_raw_adapter import Approval as Approval
from raregate.benchmarks.development_raw_adapter import construct as construct
from raregate.benchmarks.prepared_service import service


def exact_selection(request):
    """Called only after complete identity approval; never select adjacent gap rows."""
    return (
        slice(int(request[0]), int(request[-1]) + 1)
        if int(request[-1]) - int(request[0]) + 1 == len(request)
        else request.tolist()
    )


class Chain:
    def __init__(
        self, dataset, approval, path, clock, deadline, *, permit, retained_bytes=0
    ):
        p.verify_payload(permit)
        p.require(
            permit.phase.startswith("repetition")
            and permit.pid == os.getpid()
            and permit.path == str(Path(path).absolute())
            and permit.prefix == hashlib.sha256(approval.ids.tobytes()).hexdigest()
            and permit.deadline == deadline
            and clock() < deadline,
            "Task0045 authority before backend",
        )
        self.path = Path(path).absolute()
        p.require(
            self.path == self.path.resolve()
            and Path(dataset.file.filename).absolute() == self.path
            and dataset.name == "/df/block0_values"
            and dataset.shape == (1100000, 2101)
            and dataset.dtype == np.dtype("<f8"),
            "Exact owned raw dataset",
        )
        self.dataset, self.approval, self.clock, self.deadline = (
            dataset,
            approval,
            clock,
            deadline,
        )
        self.raw_calls = self.feature_calls = self.service_calls = (
            self.reference_calls
        ) = 0
        self.retained_bytes = retained_bytes
        self.peak_owned_array_bound_bytes = 0
        self.models = None
        self.context = None
        self.reference = False
        self.raw_ids_used = set()
        self.reset()

    def reset(self):
        self.returned = self.constructed = self.serviced = False
        self.read_started = self.feature_started = self.adapter_started = False
        self.returned_rows = 0
        self.context = None

    def register(self, models, channels):
        p.require(
            self.models is None and set(models) == set(plan.CANDIDATES),
            "One registration of original candidates",
        )
        self.models = models
        self.channels = tuple(channels)

    def bind(self, context, model, thresholds, channels, *, reference=False):
        p.require(
            self.context is None and self.models is not None,
            "Fresh call state and models",
        )
        actual, sb = plan.mapping(context["B"], context["m"], context["side"])
        p.require(
            context["actual_rows"] == actual
            and type(context["actual_rows"]) is int
            and context["service_B"] == sb
            and type(context["service_B"]) is int
            and context["window_position"] in plan.windows(context["B"])
            and type(context["window_position"]) is int
            and context["candidate"] in self.models
            and context["phase"] in ("pre", "post", "warmup", "timed")
            and type(reference) is bool
            and (not reference or context["phase"] in ("pre", "post")),
            "Fixed side/shape/window/reference state",
        )
        owned_model, owned_thresholds = self.models[context["candidate"]]
        p.require(
            model is owned_model
            and thresholds is owned_thresholds
            and tuple(channels) == self.channels,
            "Registered original model/threshold/feature identities",
        )
        self.context = dict(context)
        self.reference = reference
        self.model, self.thresholds = model, thresholds
        self.expected_request = self.approval.ids[
            context["window_position"] : context["window_position"] + actual
        ]

    def buffer_check(self, n):
        bound = self.retained_bytes + 24 * n * 700 * 3 * 8 + n * 2101 * 8 + 2 * 2**20
        p.require(bound <= 64 * 2**20, "Owned64MiB numerical arrays")
        self.peak_owned_array_bound_bytes = max(
            self.peak_owned_array_bound_bytes, bound
        )

    def read(self, request):
        p.require(
            self.context is not None
            and not self.reference
            and not self.read_started
            and self.clock() < self.deadline
            and self.raw_calls < 2100,
            "Selected side read state/deadline/budget",
        )
        self.approval.positions(request)
        p.require(
            np.array_equal(request, self.expected_request),
            "Exact nominal-B-based side prefix before backend",
        )
        p.require(
            self.dataset.id.valid
            and Path(self.dataset.file.filename).absolute() == self.path,
            "Live owned dataset",
        )
        self.buffer_check(len(request))
        self.read_started = True
        self.raw_calls += 1
        self.raw_ids_used.update(int(v) for v in request)
        selection = exact_selection(request)
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
        p.require(np.all(rows[:, 2100] == 0), "Approved background role")
        return rows

    def features(self, rows, parameters):
        p.require(
            self.context is not None
            and not self.reference
            and self.returned
            and not self.feature_started
            and len(rows) == self.context["actual_rows"]
            and self.clock() < self.deadline
            and self.feature_calls < 2100,
            "Feature stage and budget",
        )
        self.buffer_check(len(rows))
        self.feature_started = True
        self.feature_calls += 1
        values = construct(rows, parameters)
        self.constructed = True
        return values

    def public(self, model, thresholds, channels, features, service_b):
        p.require(
            self.context is not None
            and (self.reference or self.constructed)
            and not self.adapter_started
            and model is self.model
            and thresholds is self.thresholds
            and tuple(channels) == self.channels
            and service_b == self.context["service_B"]
            and type(service_b) is int
            and len(features) == self.context["actual_rows"]
            and self.clock() < self.deadline
            and self.service_calls < 2460
            and (not self.reference or self.reference_calls < 360),
            "Natural owned actual-row service state/identity/budget",
        )
        self.buffer_check(len(features))
        self.adapter_started = True
        self.service_calls += 1
        self.reference_calls += int(self.reference)
        output = service(model, thresholds, channels, features, service_b, "natural")
        self.serviced = True
        return output

    def joint(self, request, parameters, model, thresholds, channels):
        values = self.features(self.read(request), parameters)
        scores, masks = self.public(
            model, thresholds, channels, values, self.context["service_B"]
        )
        return values, scores, masks


class Ledger(OriginalLedger):
    def __init__(self, directory):
        super().__init__(directory)
        self.audit.update(task="0045", by_side={}, by_case={})
        self.persist()

    def finish(self, provider, *, success):
        e = self.audit["inflight"]
        side = e["context"]["side"]
        key = f"{e['context']['B']}/{e['context']['m']}"
        for group, name in (("by_side", side), ("by_case", key)):
            row = self.audit[group].setdefault(
                name, dict(raw_calls=0, raw_rows=0, adapter_calls=0, adapter_rows=0)
            )
            row["raw_calls"] += int(provider.returned)
            row["raw_rows"] += provider.returned_rows
            row["adapter_calls"] += int(provider.serviced)
            row["adapter_rows"] += e["rows"] * int(provider.serviced)
        super().finish(provider, success=success)
