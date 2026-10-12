"""Current-source synthetic acceptance; full/portable runs have no event artifacts."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from latenttrigger.research.controlled_activation import protocol as p


def validate():
    root = p.ROOT
    directory = root / "data/task0035-validation" / uuid.uuid4().hex
    directory.mkdir(parents=True, exist_ok=False)
    current = p.source_map()
    checks = {}
    environment = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        VECLIB_MAXIMUM_THREADS="1",
    )

    def run(name, command, cwd=root, env=environment):
        log = directory / (name + ".txt")
        started = time.monotonic()
        with log.open("x") as stream:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=dict(
                    env,
                    TASK0035_COUNTER_OUTPUT=str(
                        directory / (name + "-research-counters.json")
                    ),
                ),
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=240,
            )
        checks[name] = dict(
            exit_code=result.returncode,
            elapsed_seconds=time.monotonic() - started,
            command=command,
            log=str(log.relative_to(root)),
            log_sha256=p.file_hash(log),
            scope="artifact-free isolated synthetic source"
            if cwd != root
            else "synthetic/code only",
        )
        p.durable_json(
            directory / "checks.json",
            dict(status="in_progress", source_map=current, checks=checks),
        )
        print(name, result.returncode, flush=True)
        p.require(result.returncode == 0, "Validation failed; preserved " + str(log))

    plugin = ["-p", "tests.controlled_activation_counter_plugin"]
    run(
        "focused",
        [
            sys.executable,
            "-m",
            "pytest",
            *plugin,
            "tests/test_controlled_activation.py",
            "tests/test_controlled_activation_lifecycle.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0035-artifact-free-") as temp:
        isolated = Path(temp)
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
                not (isolated / name).exists()
                for name in ("data", "artifacts", "checkpoints", "models")
            ),
            "Operational artifacts absent",
        )
        env = dict(
            environment, PYTHONPATH=str(isolated / "src") + os.pathsep + str(isolated)
        )
        for name in ("full", "portable"):
            run(
                name,
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-p",
                    "tests.cpu_mps_portable_plugin",
                    *plugin,
                    "-q",
                ],
                isolated,
                env,
            )
    run("lint", [sys.executable, "-m", "ruff", "check", "."])
    run("format", [sys.executable, "-m", "ruff", "format", "--check", "."])
    run("dependencies", [sys.executable, "-m", "pip", "check"])
    run(
        "native_synthetic",
        [sys.executable, "-m", "latenttrigger.research.controlled_activation.native"],
    )
    p.require(current == p.source_map(), "Source changed during validation")
    evidence = dict(
        status="software_accepted_synthetic_only",
        source_map=current,
        dependencies=p.runtime_versions(),
        checks=checks,
        design_prerequisites=p.load_config()["design_files"],
        actual_prompt_sha256=p.file_hash(
            root / "docs/prompts/0035-controlled-activation-synthetic-foundation.md"
        ),
        model_freeze=False,
        source_acceptance=False,
        operational_authorization=False,
        operational_work=0,
        scope="focused plus complete suite twice in artifact-free copies; existing portable legacy schema fixtures; one final native generated-fixture integration",
    )
    p.durable_json(directory / "software-acceptance.json", evidence, exclusive=True)
    print("acceptance", str(directory.relative_to(root)), flush=True)
    return directory


if __name__ == "__main__":
    validate()
