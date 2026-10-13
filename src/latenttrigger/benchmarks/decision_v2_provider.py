"""Task0043 authority with unchanged selected-row/feature/natural-service algorithms."""

import hashlib
import os
from pathlib import Path

import numpy as np

from latenttrigger.benchmarks import decision_v2_protocol as p
from latenttrigger.benchmarks import development_decision_provider as algorithms
from latenttrigger.benchmarks.development_decision_planning import gate_schedule

Approval, construct, golden_once = (
    algorithms.Approval,
    algorithms.construct,
    algorithms.golden_once,
)


class Chain(algorithms.Chain):
    """Own authority constructor; no historical permit or global substitution."""

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
            "Task0043 payload before backend",
        )
        self.path = Path(path).absolute()
        p.require(
            self.path == self.path.resolve()
            and Path(dataset.file.filename).absolute() == self.path
            and dataset.name == "/df/block0_values"
            and dataset.shape == (1100000, 2101)
            and dataset.dtype == np.dtype("<f8"),
            "Owned exact dataset",
        )
        self.dataset, self.approval = dataset, approval
        self.clock, self.deadline = clock, deadline
        self.raw_calls = self.feature_calls = self.service_calls = 0
        self.retained_bytes = retained_bytes
        self.peak_owned_array_bound_bytes = 0
        self.allowed = {
            tuple(int(v) for v in approval.ids[pos : pos + b])
            for b, pos in gate_schedule()
        }
        self.reset()


class Ledger(algorithms.Ledger):
    def __init__(self, directory):
        super().__init__(directory)
        self.audit["task"] = "0043"
        self.persist()
