"""Task0045 final-source acceptance; bootstrap and admitted fixture lifecycle only."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from raregate.benchmarks import partial_raw_protocol as p


def validate():
    root = p.ROOT
    directory = root / "data/task0045-validation" / uuid.uuid4().hex
    directory.mkdir(parents=True)
    source = p.source_map()
    snapshot = directory / "frozen-source"
    for name, sha in source.items():
        path = snapshot / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((root / name).read_bytes())
        p.require(p.file_hash(path) == sha, "Exact final-source snapshot")
    p.durable_json(snapshot / "manifest.json", source, exclusive=True)
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
                timeout=780 if name == "native_synthetic" else 240,
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
            "tests/test_partial_raw_admission.py",
            "tests/test_partial_raw_runtime.py",
            "tests/test_partial_raw_chain.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0045-artifact-free-") as tmp:
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
            "raregate.benchmarks.partial_raw_native",
            "--bootstrap-directory",
            str(native),
        ],
    )
    workflow = p.read(native / "workflow.json")
    p.require(
        workflow["status"] == "parent_accepted_synthetic_natural_partial_raw_decision"
        and workflow["sleep_assertion"]["released"] is True,
        "Native synthetic lifecycle",
    )
    p.require(source == p.source_map(), "Source unchanged across final acceptance")
    from raregate.benchmarks import partial_raw_admission as admission

    context = admission.Context(root)
    path = admission.emit(context, directory, source, checks, native / "workflow.json")
    admission.verify(path, context)
    base, launched = admission.launch(
        path, directory / "roundtrip", context, admission.Mode.SYNTHETIC
    )
    p.require(
        launched["status"] == "parent_accepted_synthetic_natural_partial_raw_decision",
        "Final serialized-record/native Task0045 roundtrip",
    )
    p.require(
        source == p.source_map() and launched["sleep_assertion"]["released"] is True,
        "Final source/lifecycle",
    )
    receipt = dict(
        task="0045",
        status="software_accepted_synthetic_natural_partial_raw_decision_roundtrip",
        record_sha256=p.file_hash(path),
        workflow_path=str((base / "workflow.json").relative_to(root)),
        workflow_sha256=p.file_hash(base / "workflow.json"),
        source_map=source,
        dependencies=p.dependencies(),
        native_build=p.native_build(),
        identity=p.identity(),
        execution_authorized=False,
        admission_plan_sha256=p.file_hash(directory / "roundtrip/admission-plan.json"),
        admission_freeze_sha256=p.file_hash(
            directory / "roundtrip/admission-freeze.json"
        ),
    )
    p.durable_json(directory / "admission-roundtrip.json", receipt, exclusive=True)
    admission.roundtrip(path, context)
    print("acceptance", directory / "software-acceptance.json", flush=True)


if __name__ == "__main__":
    validate()
