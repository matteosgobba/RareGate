"""Task0057 immutable generated-only session/candidate scopes, never P4."""

import json
import multiprocessing as mp
from dataclasses import dataclass
from pathlib import Path

from . import quota
from .pilot54 import source_bytes
from .pilot_context import CANDIDATES, digest
from .protocol import require


@dataclass(frozen=True)
class GeneratedSession57:
    root: str
    directory: str
    bundle_sha256: str
    fault: str
    task: str = "0057"

    def for_candidate(self, candidate):
        require(candidate in CANDIDATES, "Closed generated candidate")
        return SessionFixture57(
            self.root, self.directory, self.bundle_sha256, candidate, self.fault
        )


@dataclass(frozen=True)
class SessionFixture57:
    root: str
    session: str
    bundle_sha256: str
    candidate: str
    fault: str
    task: str = "0057"

    @property
    def directory(self):
        # Immutable sources deduplicated per frozen group/candidate, never rewritten.
        return str(Path(self.session).parent / "generated" / self.candidate)

    def validate_location(self, repo):
        from . import session57

        root, session = Path(self.root), Path(self.session)
        require(
            self.task == "0057"
            and root == repo / session57.ROOT
            and session.parent.parent == root
            and session.parent.name in ("suite-1", "suite-2")
            and self.fault in session57.SESSIONS
            and session.name == "session-" + self.fault
            and self.candidate in CANDIDATES,
            "Closed generated session location",
        )
        require(
            digest(session57.source_manifest(repo)) == self.bundle_sha256,
            "Current generated session bundle",
        )
        require(
            quota.CURRENT is not None
            and quota.CURRENT.task == "0057"
            and quota.CURRENT.root == root
            and quota.CURRENT.entries == session57.file_plan(),
            "Generated session ledger",
        )

    def specification(self, repo):
        self.validate_location(repo)
        directory = Path(self.directory)
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
            "Only owned serialized session inputs",
        )
        return spec

    def validate_payload(self, repo, candidate, budget):
        require(
            candidate == self.candidate
            and mp.current_process().name == "fixture-consumer"
            and budget.counts == {k: 0 for k in budget.CAPS},
            "Fresh generated consumer only",
        )
        return self.specification(repo)

    def read_source(self, repo, entry):
        require(
            mp.current_process().name == "fixture-consumer"
            and entry in self.specification(repo)["allowed_files"],
            "Closed generated role",
        )
        return source_bytes(repo, entry)
