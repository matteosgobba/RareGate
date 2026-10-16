"""Fresh simulator acceptance; artifact-free full/portable historical fixtures."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

from raregate.simulation import refined_service_protocol as p

LEGACY_METADATA = (
    "results/tables/final/task0007-autoencoder-training-history.csv",
    "results/tables/final/task0026-pca-ae-calibrated-operating-points.csv",
    "results/tables/final/task0026-pca-ae-scientific-comparison.csv",
    "results/tables/final/task0034-confirmation-source-registry.csv",
    "results/tables/final/task0034-controlled-follow-up-summary.json",
    "results/tables/final/task0039-development-raw-feature-summary.json",
    "results/tables/final/task0040-development-raw-feature-summary.json",
    "results/tables/final/task0042-development-decision-admission-summary.json",
    "results/tables/final/task0043-development-raw-decision-summary.json",
    "results/tables/final/task0044-joint-service-replay-summary.json",
    "results/tables/final/task0045-natural-partial-raw-decision-summary.json",
)


def validate():
    root = p.ROOT
    directory = root / "data/task0048-validation" / uuid.uuid4().hex
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
        import xml.etree.ElementTree as ET

        commands = command if command and isinstance(command[0], list) else [command]
        log = directory / (name + ".txt")
        started = time.monotonic()
        parts = []
        exit_code = 0
        with log.open("x") as f:
            for index, cmd in enumerate(commands):
                p.require(
                    current == p.source_map(),
                    "Source changed before check; preserve superseded evidence",
                )
                test_files = [
                    v for v in cmd if v.startswith("tests/test") and v.endswith(".py")
                ]
                xml = directory / f"{name}-part{index}.xml"
                actual = (
                    cmd + ["--junitxml", str(xml)]
                    if name in ("full", "portable")
                    else cmd
                )
                tick = time.monotonic()
                try:
                    result = subprocess.run(
                        actual,
                        cwd=cwd,
                        env=dict(
                            env,
                            TASK0035_COUNTER_OUTPUT=str(
                                directory
                                / f"{name}-part{index}-historical-research-counters.json"
                            ),
                        ),
                        stdout=f,
                        stderr=subprocess.STDOUT,
                        timeout=240,
                    )
                    exit_code = result.returncode
                except subprocess.TimeoutExpired:
                    exit_code = 124
                part = dict(
                    exit_code=exit_code,
                    elapsed_seconds=time.monotonic() - tick,
                    command=actual,
                    test_files=test_files,
                )
                if xml.exists():
                    suites = list(ET.parse(xml).getroot().iter("testsuite"))
                    part.update(
                        junit=str(xml.relative_to(root)),
                        junit_sha256=p.file_hash(xml),
                        **{
                            key: sum(int(s.get(key, "0")) for s in suites)
                            for key in ("tests", "failures", "errors", "skipped")
                        },
                    )
                parts.append(part)
                if exit_code != 0:
                    break
        checks[name] = dict(
            exit_code=exit_code,
            elapsed_seconds=time.monotonic() - started,
            log=str(log.relative_to(root)),
            log_sha256=p.file_hash(log),
            command=command,
            subchecks=parts,
            scope="artifact-free complete disjoint test-file partition;240s per subprocess; historical fixtures separately counted"
            if cwd != root
            else "model-free generated replay / static checks",
        )
        p.durable_json(
            directory / "checks.json", dict(source_map=current, checks=checks)
        )
        print(name, exit_code, flush=True)
        p.require(exit_code == 0, "Validation failed and preserved: " + str(log))

    run(
        "focused",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_refined_service_replay.py",
            "tests/test_synthetic_trigger_runtime.py",
            "-q",
        ],
    )
    with tempfile.TemporaryDirectory(prefix="task0048-artifact-free-") as temp:
        from pathlib import Path

        isolated = Path(temp)
        copy_audit = []

        def copy_context(source, destination):
            source = Path(source)
            relative = str(source.relative_to(root))
            record = None
            if relative in p.SOURCE_MANIFEST or relative in LEGACY_METADATA:
                p.safe(root, relative)
                record = dict(
                    path=relative,
                    role="code_authorization_fixture_context"
                    if relative in p.SOURCE_MANIFEST
                    else "legacy_aggregate_or_identity_fixture",
                    state="requested",
                    requested_bytes=source.stat().st_size,
                )
                copy_audit.append(record)
                p.durable_json(
                    directory / "software-context-copy-audit.json",
                    dict(opens=copy_audit),
                )
            result = shutil.copyfile(source, destination)
            if record is not None:
                record.update(
                    state="returned",
                    bytes=Path(destination).stat().st_size,
                    sha256=p.file_hash(destination),
                )
                if relative in p.SOURCE_MANIFEST:
                    p.require(
                        record["bytes"] == p.SOURCE_MANIFEST[relative]["bytes"]
                        and record["sha256"] == p.SOURCE_MANIFEST[relative]["sha256"],
                        "Declared code-context bytes",
                    )
                p.durable_json(
                    directory / "software-context-copy-audit.json",
                    dict(opens=copy_audit),
                )
            return result

        for folder in (
            "src",
            "scripts",
            "tests",
            "configs",
            "docs",
            ".github",
        ):
            shutil.copytree(
                root / folder,
                isolated / folder,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                copy_function=copy_context,
            )
        for name in ("pyproject.toml", "README.md", "LICENSE", ".gitignore"):
            shutil.copyfile(root / name, isolated / name)
        # Frozen metadata required by historical regression contracts. No timing vectors.
        for relative in LEGACY_METADATA:
            destination = isolated / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            copy_context(root / relative, destination)
        p.require(
            sorted(v.name for v in (isolated / "results/tables/final").iterdir())
            == sorted(Path(v).name for v in LEGACY_METADATA),
            "Closed11 historical metadata fixtures; pair/cell CSVs and timing JSONLs absent",
        )
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
        all_tests = sorted(
            str(v.relative_to(isolated)) for v in (isolated / "tests").rglob("test*.py")
        )
        new_test = "tests/test_refined_service_replay.py"
        legacy = [v for v in all_tests if v != new_test]
        groups = [legacy[: len(legacy) // 2], legacy[len(legacy) // 2 :], [new_test]]
        p.require(
            sorted(v for group in groups for v in group) == all_tests
            and len(set(v for group in groups for v in group)) == len(all_tests),
            "Complete disjoint full-suite coverage",
        )
        for name in ("full", "portable"):
            prefix = [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "tests.cpu_mps_portable_plugin",
                "-p",
                "tests.controlled_activation_counter_plugin",
                "-q",
            ]
            run(name, [prefix + group for group in groups], isolated, env)
    run("lint", [sys.executable, "-m", "ruff", "check", "."])
    run("format", [sys.executable, "-m", "ruff", "format", "--check", "."])
    run("dependencies", [sys.executable, "-m", "pip", "check"])
    native = directory / uuid.uuid4().hex
    run(
        "native_synthetic",
        [
            sys.executable,
            "-m",
            "raregate.simulation.refined_service_native",
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
        "raregate.simulation.refined_service_native",
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
            task="0048",
            status="software_accepted_synthetic_refined_support_service_replay_roundtrip",
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
