"""Task0058 closed AE-only P4 context and disjoint owned generated scopes."""

import json
import multiprocessing as mp
import os
from dataclasses import dataclass
from pathlib import Path

from . import quota
from .pilot54 import source_bytes
from .pilot_context import CANDIDATES, digest
from .protocol import require

AE_PLAN = ("compact-autoencoder-v2",)


@dataclass(frozen=True)
class PilotContext58:
    root: str
    bundle_sha256: str
    task: str = "0058"

    def specification(self, repo):
        from . import pilot58

        require(
            self.task == "0058" and Path(self.root) == repo / pilot58.ROOT,
            "New0058 context",
        )
        spec = pilot58.validate_spec(
            json.loads((repo / pilot58.CONFIG).read_text()), repo
        )
        require(
            digest(pilot58.source_manifest(repo)) == self.bundle_sha256,
            "Current0058 bundle",
        )
        return spec

    def candidate_plan(self, repo):
        require(
            tuple(self.specification(repo)["candidate_plan"]) == AE_PLAN, "AE-only plan"
        )
        return AE_PLAN

    def validate_request(self, repo, candidate):
        require(candidate in AE_PLAN, "Task0058 rejects PCA before startup/access")
        self.candidate_plan(repo)
        from . import pilot58

        require(
            quota.CURRENT is not None
            and quota.CURRENT.task == "0058"
            and quota.CURRENT.root == Path(self.root)
            and quota.CURRENT.entries == pilot58.file_plan(),
            "Scoped0058 ledger",
        )
        owner = json.loads(
            quota.CURRENT.path(Path(self.root) / "owner.json").read_text()
        )
        require(
            owner["task"] == "0058"
            and tuple(owner["candidate_plan"]) == AE_PLAN
            and owner["generated_groups"] == 1
            and owner["conditional_P4_sessions"] == 1,
            "Closed new0058 owner",
        )

    def validate_payload(self, repo, candidate, budget):
        self.validate_request(repo, candidate)
        from . import pilot58

        active = json.loads(
            quota.CURRENT.path(Path(self.root) / "pilot/activation.json").read_text()
        )
        require(
            mp.current_process().name == "fixture-consumer"
            and os.getppid() == active["subject_pid"]
            and active["task"] == self.task
            and active["root"] == self.root
            and active["single_session"] is True
            and active["bundle_sha256"] == self.bundle_sha256
            and tuple(active["candidate_plan"]) == AE_PLAN
            and budget.counts == {k: 0 for k in budget.CAPS},
            "Consumer/parent/task/root/plan/bundle/fresh budget before payload",
        )
        pilot58.check_qualification(Path(self.root), repo)
        return self.specification(repo)

    def read_source(self, repo, entry):
        require(
            mp.current_process().name == "fixture-consumer",
            "Consumer-only original bytes",
        )
        spec = self.specification(repo)
        require(
            entry in spec["allowed_files"]
            and entry["role"] != "raw"
            and not entry["role"].startswith("pca-v1:"),
            "Closed0058 small originals",
        )
        return source_bytes(repo, entry)


@dataclass(frozen=True)
class GeneratedSession58:
    root: str
    directory: str
    bundle_sha256: str
    fault: str
    task: str = "0058-generated"

    def candidate_plan(self, repo):
        require(self.task == "0058-generated", "Generated session identity")
        plan = AE_PLAN if self.fault == "ae-only" else CANDIDATES
        GeneratedFixture58(
            self.root, self.directory, self.bundle_sha256, plan[0], self.fault
        ).validate_location(repo)
        return plan

    def for_candidate(self, candidate):
        plan = AE_PLAN if self.fault == "ae-only" else CANDIDATES
        require(candidate in plan, "Closed generated plan, AE-only rejects PCA")
        return GeneratedFixture58(
            self.root, self.directory, self.bundle_sha256, candidate, self.fault
        )


@dataclass(frozen=True)
class GeneratedFixture58:
    root: str
    session: str
    bundle_sha256: str
    candidate: str
    fault: str
    task: str = "0058-generated"

    @property
    def directory(self):
        return str(Path(self.session).parent / "generated" / self.candidate)

    def validate_location(self, repo):
        from . import pilot58

        root, session = Path(self.root), Path(self.session)
        require(
            self.task == "0058-generated"
            and root == repo / pilot58.ROOT
            and session.parent == root / "suite-1"
            and self.fault in ("normal", "first-failure", "second-failure", "ae-only")
            and session.name == "session-" + self.fault
            and self.candidate in (AE_PLAN if self.fault == "ae-only" else CANDIDATES),
            "Closed0058 generated fixture path/plan",
        )
        require(
            digest(pilot58.source_manifest(repo)) == self.bundle_sha256,
            "Generated final bundle",
        )
        require(
            quota.CURRENT is not None
            and quota.CURRENT.task == "0058"
            and quota.CURRENT.root == root
            and quota.CURRENT.entries == pilot58.file_plan(),
            "Generated0058 immutable ledger",
        )

    def specification(self, repo):
        self.validate_location(repo)
        spec = json.loads((Path(self.directory) / "fixture-spec.json").read_text())
        require(
            spec["generated_only"] is True
            and spec["candidate"] == self.candidate
            and spec["bundle_sha256"] == self.bundle_sha256
            and len(spec["allowed_files"]) == 14
            and all(
                (repo / e["path"]).is_relative_to(Path(self.directory) / "serialized")
                for e in spec["allowed_files"]
            ),
            "Only owned generated artifacts",
        )
        return spec

    def validate_payload(self, repo, candidate, budget):
        require(
            candidate == self.candidate
            and mp.current_process().name == "fixture-consumer"
            and budget.counts == {k: 0 for k in budget.CAPS},
            "Fresh generated consumer",
        )
        return self.specification(repo)

    def read_source(self, repo, entry):
        require(
            mp.current_process().name == "fixture-consumer"
            and entry in self.specification(repo)["allowed_files"],
            "Closed generated role",
        )
        return source_bytes(repo, entry)
