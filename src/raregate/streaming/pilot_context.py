"""0056 explicit immutable scope; fixture capabilities cannot arm real sources."""

import hashlib
import json
import multiprocessing as mp
import os
from dataclasses import dataclass
from pathlib import Path

from . import quota
from .pilot54 import source_bytes
from .protocol import require

CONFIG56 = "configs/streaming/development_hdf_consumer_pilot_v2.json"
ROOT56 = "data/task0056-validation/session-v2"
CANDIDATES = ("pca-v1", "compact-autoencoder-v2")


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


@dataclass(frozen=True)
class PilotContext56:
    root: str
    bundle_sha256: str
    task: str = "0056"

    def specification(self, repo):
        from . import pilot56

        require(
            self.task == "0056" and Path(self.root) == repo / ROOT56, "New0056 owner"
        )
        spec = json.loads((repo / CONFIG56).read_text())
        pilot56.validate_spec(spec, repo)
        require(
            digest(pilot56.source_manifest(repo)) == self.bundle_sha256,
            "Current0056 bundle",
        )
        return spec

    def validate_payload(self, repo, candidate, budget):
        from . import pilot56

        spec = self.specification(repo)
        ledger = quota.CURRENT
        require(
            ledger is not None
            and ledger.task == "0056"
            and ledger.root == Path(self.root)
            and ledger.entries == pilot56.file_plan(),
            "Scoped immutable ledger before payload",
        )
        active = json.loads((ledger.root / "pilot/activation.json").read_text())
        require(
            candidate in CANDIDATES
            and mp.current_process().name == "fixture-consumer"
            and os.getppid() == active["subject_pid"]
            and active["task"] == self.task
            and active["single_session"] is True
            and active["bundle_sha256"] == self.bundle_sha256
            and active["root"] == self.root,
            "Task/bundle/consumer/parent/activation immediately before payload",
        )
        pilot56.check_qualification(ledger.root, repo)
        require(
            budget.counts == {k: 0 for k in budget.CAPS}, "Fresh candidate load budget"
        )
        return spec

    def read_source(self, repo, entry):
        # Only a real consumer receives this context; fixed_path rejects redirects.
        require(
            mp.current_process().name == "fixture-consumer",
            "Consumer-only source bytes",
        )
        allowed = self.specification(repo)["allowed_files"]
        require(
            entry in allowed and entry["role"] != "raw", "Closed small payload role"
        )
        return source_bytes(repo, entry)


@dataclass(frozen=True)
class FixtureContext56:
    """Distinct generated type: no operational activation, paths or identity fallback."""

    root: str
    directory: str
    bundle_sha256: str
    candidate: str

    def specification(self, repo):
        from . import pilot56

        root, directory = Path(self.root), Path(self.directory)
        require(
            root == repo / ROOT56
            and directory.is_relative_to(root)
            and directory.parent.name in ("suite-1", "suite-2")
            and directory.name
            == (
                "15-serialized-pca"
                if self.candidate == CANDIDATES[0]
                else "16-serialized-ae"
            )
            and self.candidate in CANDIDATES,
            "Closed generated fixture context",
        )
        require(
            digest(pilot56.source_manifest(repo)) == self.bundle_sha256,
            "Fixture final source",
        )
        spec = json.loads((directory / "fixture-spec.json").read_text())
        require(
            spec["generated_only"] is True
            and spec["candidate"] == self.candidate
            and spec["bundle_sha256"] == self.bundle_sha256
            and len(spec["allowed_files"]) == 14
            and all(
                (repo / x["path"]).is_relative_to(directory / "serialized")
                for x in spec["allowed_files"]
            ),
            "Only own serialized fixture files",
        )
        return spec

    def validate_payload(self, repo, candidate, budget):
        require(
            candidate == self.candidate
            and mp.current_process().name == "fixture-consumer",
            "Fixture consumer only",
        )
        require(
            quota.CURRENT.task == "0056" and str(quota.CURRENT.root) == self.root,
            "Fixture quota",
        )
        require(
            budget.counts == {k: 0 for k in budget.CAPS}, "Fixture fresh load budget"
        )
        return self.specification(repo)

    def read_source(self, repo, entry):
        require(
            mp.current_process().name == "fixture-consumer",
            "Fixture consumer-only bytes",
        )
        require(
            entry in self.specification(repo)["allowed_files"], "Closed fixture role"
        )
        return source_bytes(repo, entry)


def context_from_request(root, request, repo):
    """Never accepts fixture dictionaries as operational contexts."""
    from . import pilot56

    require(
        type(request) is dict and request.get("task") == "0056", "Explicit0056 request"
    )
    require(set(request) in ({"task", "candidate", "context"},), "Closed request keys")
    context = request["context"]
    require(
        type(context) in (PilotContext56, FixtureContext56), "Typed scope, no fallback"
    )
    require(
        Path(root) == repo / ROOT56 and context.root == str(root), "Canonical0056 root"
    )
    require(
        context.bundle_sha256 == digest(pilot56.source_manifest(repo)),
        "Current request bundle",
    )
    if type(context) is FixtureContext56:
        require(request["candidate"] == context.candidate, "Fixture candidate")
    if type(context) is PilotContext56:
        context.specification(repo)
    else:
        directory = Path(context.directory)
        require(
            directory.is_relative_to(Path(root))
            and directory.parent.name in ("suite-1", "suite-2")
            and directory.name in ("15-serialized-pca", "16-serialized-ae"),
            "Fixture location before source creation",
        )
    return context


def fixture_rows(positions):
    """Independent strict dataset stand-in; only synthetic positions0..63."""
    import numpy as np

    from .hdf_consumer import positions_checked

    positions_checked(positions)
    rows = np.zeros((len(positions), 2101), dtype="<f8")
    # Three nonzero particles; all700 slots still pass canonical processing.
    for i, p in enumerate(positions):
        rows[i, :9] = [10 + p / 8, 0.2, 0.1, 6, -0.3, -0.4, 2, 0.5, 0.7]
    return rows


class FixtureHandle:
    def __init__(self):
        self.valid = True

    def close(self):
        self.valid = False


class FixtureDataset:
    def __init__(self, handle):
        self.handle = handle

    def __getitem__(self, selection):
        from .hdf_consumer import positions_checked

        rows, columns = selection
        require(type(rows) is list, "Explicit selected positions only")
        positions_checked(rows)
        require(
            self.handle.valid
            and columns == slice(None)
            and all(a < b for a, b in zip(rows, rows[1:], strict=False)),
            "Strict fixture selection, no intervals",
        )
        return fixture_rows(rows)
