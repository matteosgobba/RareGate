"""Fresh final-source Task0041 acceptance; real prepared/model access is excluded."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from raregate.benchmarks import development_decision_protocol as p


def emit_record(context, directory, source, checks, native):
    """Serialized production contract, exercised by Task0042 roundtrips."""
    from raregate.benchmarks.development_decision_contract import emit

    return emit(
        directory / "software-acceptance.json",
        context,
        source=source,
        dependencies=p.dependencies(),
        build=p.native_build(),
        checks=checks,
        native=native / "workflow.json",
    )


def validate():
    root = p.ROOT
    directory = root / "data/task0041-validation" / uuid.uuid4().hex
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
            "tests/test_development_decision.py",
            "tests/test_development_decision_runtime.py",
            "tests/test_development_decision_grants.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0041-artifact-free-") as tmp:
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
            "raregate.benchmarks.development_decision_native",
            "--synthetic-directory",
            str(native),
        ],
    )
    workflow = p.read(native / "workflow.json")
    p.require(
        workflow["status"] == "parent_accepted_synthetic_raw_decision"
        and workflow["sleep_assertion"]["released"] is True,
        "Native synthetic lifecycle",
    )
    p.require(source == p.source_map(), "Source unchanged across final acceptance")
    from raregate.benchmarks.development_decision_contract import Context

    path = emit_record(Context(root), directory, source, checks, native)
    p.acceptance(path)
    p.durable_json(
        directory / "admission-roundtrip.json",
        dict(
            status="controller_compatible_software_record",
            record_sha256=p.file_hash(path),
            execution_authorized=False,
        ),
        exclusive=True,
    )
    print("acceptance", directory / "software-acceptance.json", flush=True)


if __name__ == "__main__":
    validate()
