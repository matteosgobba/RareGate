"""Task0042 software-only acceptance, emitted-record roundtrip and synthetic launch."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from raregate.benchmarks import development_decision_protocol as p


def validate():
    root = p.ROOT
    directory = root / "data/task0042-validation" / uuid.uuid4().hex
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
            "tests/test_development_decision_admission.py",
            "tests/test_development_decision.py",
            "tests/test_development_decision_runtime.py",
            "tests/test_development_decision_grants.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0042-artifact-free-") as tmp:
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
            "--validation-bootstrap",
        ],
    )
    workflow = p.read(native / "workflow.json")
    p.require(
        workflow["status"] == "parent_accepted_synthetic_raw_decision"
        and workflow["sleep_assertion"]["released"] is True,
        "Native synthetic lifecycle",
    )
    p.require(source == p.source_map(), "Source unchanged across final acceptance")
    from scripts.validate_development_raw_decisions import emit_record

    from raregate.benchmarks import development_decision_admission as admission
    from raregate.benchmarks.development_decision_contract import Context

    context = Context(root, "0042")
    path = emit_record(context, directory, source, checks, native)
    # The final immutable record is consumed by the real outer verifier.
    p.acceptance(path, context=context)
    base, launched = admission.launch(
        path, directory / "roundtrip", context, admission.native
    )
    p.require(
        launched["status"] == "parent_accepted_synthetic_raw_decision",
        "Emitted-record native roundtrip",
    )
    p.require(source == p.source_map(), "Final source unchanged through dispatch")
    p.require(
        launched["sleep_assertion"]["released"] is True, "Roundtrip assertion release"
    )
    receipt = dict(
        status="software_accepted_synthetic_admission_repair",
        validation_owner="0042",
        protocol_task="0041",
        record_path=str(path.relative_to(root)),
        record_sha256=p.file_hash(path),
        source_map=source,
        dependencies=p.dependencies(),
        native_build=p.native_build(),
        repair_prompt_sha256=p.file_hash(root / context.prompt),
        admission_plan_sha256=p.file_hash(directory / "roundtrip/admission-plan.json"),
        admission_freeze_sha256=p.file_hash(
            directory / "roundtrip/admission-freeze.json"
        ),
        roundtrip_workflow_path=str((base / "workflow.json").relative_to(root)),
        roundtrip_workflow_sha256=p.file_hash(base / "workflow.json"),
        operational_execution_authorized=False,
    )
    p.durable_json(directory / "repair-acceptance.json", receipt, exclusive=True)
    print("acceptance", directory / "software-acceptance.json", flush=True)


if __name__ == "__main__":
    validate()
