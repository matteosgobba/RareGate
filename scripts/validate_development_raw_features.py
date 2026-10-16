"""Fresh final-source Task0039 acceptance; real prepared/model access is excluded."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from raregate.benchmarks import development_raw_protocol as p


def validate():
    root = p.ROOT
    directory = root / "data/task0039-validation" / uuid.uuid4().hex
    directory.mkdir(parents=True)
    source = p.source_map()
    checks = {}
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        **p.load()["thread_environment"],
    )

    def check(name, command, cwd=root, environment=env):
        log = directory / (name + ".txt")
        started = time.monotonic()
        with log.open("x") as f:
            r = subprocess.run(
                command,
                cwd=cwd,
                env=dict(
                    environment,
                    TASK0035_COUNTER_OUTPUT=str(
                        directory / (name + "-historical-research-counters.json")
                    ),
                ),
                stdout=f,
                stderr=subprocess.STDOUT,
                timeout=240,
            )
        checks[name] = dict(
            exit_code=r.returncode,
            elapsed_seconds=time.monotonic() - started,
            command=command,
            log=str(log.relative_to(root)),
            log_sha256=p.file_hash(log),
            scope="new synthetic only / static checks"
            if cwd == root
            else "artifact-free historical/new synthetic fixtures; legacy model forwards/updates permitted",
        )
        p.durable_json(
            directory / "checks.json", dict(source_map=source, checks=checks)
        )
        print(name, r.returncode, flush=True)
        p.require(r.returncode == 0, "Validation failed; preserved " + str(log))

    check(
        "focused",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_development_raw.py",
            "tests/test_development_raw_runtime.py",
            "tests/test_development_raw_custody.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0039-artifact-free-") as tmp:
        isolated = Path(tmp)
        for folder in (
            "src",
            "scripts",
            "tests",
            "configs",
            "docs",
            "results/tables/final",
            ".github",
        ):
            shutil.copytree(
                root / folder,
                isolated / folder,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        for name in ("pyproject.toml", "README.md", "LICENSE", ".gitignore"):
            shutil.copyfile(root / name, isolated / name)
        p.require(
            all(
                not (isolated / v).exists()
                for v in ("data", "artifacts", "models", "checkpoints")
            ),
            "Operational artifacts absent",
        )
        for name in ("full", "portable"):
            check(
                name,
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-p",
                    "tests.cpu_mps_portable_plugin",
                    "-p",
                    "tests.controlled_activation_counter_plugin",
                    "-q",
                ],
                isolated,
                dict(
                    env, PYTHONPATH=str(isolated / "src") + os.pathsep + str(isolated)
                ),
            )
    check("lint", [sys.executable, "-m", "ruff", "check", "."])
    check("format", [sys.executable, "-m", "ruff", "format", "--check", "."])
    check("dependencies", [sys.executable, "-m", "pip", "check"])
    native = directory / "native-synthetic"
    check(
        "native_synthetic",
        [
            sys.executable,
            "-m",
            "raregate.benchmarks.development_raw_native",
            "--synthetic-directory",
            str(native),
        ],
    )
    workflow = p.read(native / "workflow.json")
    p.require(
        workflow["status"] == "parent_accepted_synthetic_foundation"
        and workflow["sleep_assertion"]["released"] is True,
        "Native synthetic lifecycle",
    )
    p.require(source == p.source_map(), "Source unchanged across final acceptance")
    acceptance = dict(
        status="software_accepted_synthetic_raw_feature_foundation",
        source_map=source,
        dependencies=p.dependencies(),
        config_sha256=p.file_hash(root / p.CONFIG),
        prompt_sha256=p.file_hash(root / p.PROMPT),
        checks=checks,
        native_receipt_path=str((native / "workflow.json").relative_to(root)),
        native_receipt_sha256=p.file_hash(native / "workflow.json"),
        native_build=p.native_build(),
        operational_reservation=False,
        synthetic_only=True,
        metadata_scope="only the separate fixed6999-ID/raw-byte/HDF-metadata resolver can be reserved; no payload timing permission",
    )
    p.durable_json(directory / "software-acceptance.json", acceptance, exclusive=True)
    print("acceptance", directory / "software-acceptance.json", flush=True)


if __name__ == "__main__":
    validate()
