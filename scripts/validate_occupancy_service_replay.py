"""Fresh simulator acceptance; artifact-free full/portable historical fixtures."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

from raregate.simulation import occupancy_protocol as p


def validate():
    root = p.ROOT
    directory = root / "data/task0046-validation" / uuid.uuid4().hex
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
        with log.open("x") as f:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=dict(
                    env,
                    TASK0035_COUNTER_OUTPUT=str(
                        directory / (name + "-historical-research-counters.json")
                    ),
                ),
                stdout=f,
                stderr=subprocess.STDOUT,
                timeout=240,
            )
        checks[name] = dict(
            exit_code=result.returncode,
            elapsed_seconds=time.monotonic() - started,
            log=str(log.relative_to(root)),
            log_sha256=p.file_hash(log),
            command=command,
            scope="artifact-free synthetic full suite; historical model fixtures permitted"
            if cwd != root
            else "new simulator synthetic fixtures only / static checks",
        )
        p.durable_json(
            directory / "checks.json", dict(source_map=current, checks=checks)
        )
        print(name, result.returncode, flush=True)
        p.require(
            result.returncode == 0, "Validation failed and preserved: " + str(log)
        )

    run(
        "focused",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_occupancy_service_replay.py",
            "tests/test_synthetic_trigger_runtime.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0046-artifact-free-") as temp:
        from pathlib import Path

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
                not (isolated / n).exists()
                for n in ("data", "artifacts", "models", "checkpoints")
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
                    "-p",
                    "tests.controlled_activation_counter_plugin",
                    "-q",
                ],
                isolated,
                env,
            )
    run("lint", [sys.executable, "-m", "ruff", "check", "."])
    run("format", [sys.executable, "-m", "ruff", "format", "--check", "."])
    run("dependencies", [sys.executable, "-m", "pip", "check"])
    native = directory / uuid.uuid4().hex
    run(
        "native_synthetic",
        [
            sys.executable,
            "-m",
            "raregate.simulation.occupancy_native",
            "--fixture-directory",
            str(native),
            "--bootstrap",
        ],
    )
    p.require(current == p.source_map(), "Source changed during validation")
    path = p.emit(directory, checks, native / "workflow.json")
    p.verify_acceptance(path)
    roundtrip = directory / uuid.uuid4().hex
    # One admitted native generated replay, separate from bootstrap and real sweep.
    command = [
        sys.executable,
        "-m",
        "raregate.simulation.occupancy_native",
        "--fixture-directory",
        str(roundtrip),
        "--acceptance",
        str(path),
    ]
    with (directory / "roundtrip.txt").open("x") as f:
        result = subprocess.run(
            command,
            cwd=root,
            env=environment,
            stdout=f,
            stderr=subprocess.STDOUT,
            timeout=240,
        )
    p.require(result.returncode == 0, "Admitted generated native roundtrip")
    workflow = p.read(roundtrip / "workflow.json")
    p.require(
        workflow["status"] == p.PARENT_STATUS
        and workflow["fixture_only"] is True
        and workflow["sleep_assertion"]["released"] is True,
        "Accepted fixture roundtrip",
    )
    p.durable_json(
        directory / "admission-roundtrip.json",
        dict(
            task="0046",
            status="software_accepted_synthetic_occupancy_service_replay_roundtrip",
            record_sha256=p.file_hash(path),
            workflow_path=str((roundtrip / "workflow.json").relative_to(root)),
            workflow_sha256=p.file_hash(roundtrip / "workflow.json"),
            source_map=current,
            dependencies=p.dependencies(),
            execution_authorized=False,
        ),
        exclusive=True,
    )
    p.verify_roundtrip(path)
    p.require(current == p.source_map(), "Final unchanged software freeze")
    print("acceptance", str(path), flush=True)
    return directory


if __name__ == "__main__":
    validate()
