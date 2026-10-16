"""Fresh full/portable source validation with operational artifacts absent."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from raregate.diagnostics import protocol as p


def validate():
    root = p.ROOT
    directory = root / "data/task0033-validation"
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
        path = directory / (name + "-final.txt")
        started = time.monotonic()
        with path.open("w") as stream:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=240,
            )
        checks[name] = dict(
            exit_code=result.returncode,
            log=str(path.relative_to(root)),
            log_sha256=p.file_hash(path),
            elapsed_seconds=time.monotonic() - started,
            command=command,
            cwd_scope="artifact-free isolated source"
            if cwd != root
            else "repository synthetic/code scope",
        )
        print(name, result.returncode, flush=True)
        p.require(result.returncode == 0, name + " validation failed; see " + str(path))

    run(
        "focused",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_feature_score_diagnostics.py",
            "tests/test_three_prong_acquisition_v3.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0033-portable-") as temporary:
        isolated = Path(temporary)
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
        # No data, checkpoints, models, accepted scores/features, or v1/v2 artifact.
        env = dict(
            environment, PYTHONPATH=str(isolated / "src") + os.pathsep + str(isolated)
        )
        run(
            "full",
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "tests.cpu_mps_portable_plugin",
                "-q",
            ],
            isolated,
            env,
        )
        run(
            "portable",
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "tests.cpu_mps_portable_plugin",
                "-q",
            ],
            isolated,
            env,
        )
    run("lint", [sys.executable, "-m", "ruff", "check", "."])
    run("format", [sys.executable, "-m", "ruff", "format", "--check", "."])
    run("dependencies", [sys.executable, "-m", "pip", "check"])
    run("native_synthetic", [sys.executable, "-m", "tests.feature_score_native"])
    p.require(current == p.source_map(), "Sources changed during validation")
    p.durable_json(
        directory / "acceptance-checks.json",
        dict(
            status="passed",
            source_file_sha256=current,
            dependencies=p.runtime_versions(),
            checks=checks,
            operational_numerical_access=0,
            full_and_portable_scope="complete suite twice in artifact-free source checkout; existing portable synthetic legacy schema plugin replaces three historical v1 artifact expectations; no operational candidates/samples",
        ),
    )


if __name__ == "__main__":
    validate()
