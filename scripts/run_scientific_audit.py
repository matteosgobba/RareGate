"""Run the generated portable audit once in a fresh, cache-contained process.

No historical native validation entrypoint, acquisition or source acceptance runs.
The outer bounds are fail-stop observations, not pre-growth storage guarantees.
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--tests", nargs="+", help="Explicit focused generated tests")
    args = parser.parse_args()
    owned = args.root.absolute()
    if owned.exists() or owned.is_relative_to(ROOT):
        parser.error("Choose a new audit-owned directory outside the checkout")
    owned.mkdir(parents=True)
    environment = dict(os.environ)
    environment.update(
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTHONPATH=os.pathsep.join((str(ROOT), str(ROOT / "src"))),
        XDG_CACHE_HOME=str(owned / "cache"),
        MPLCONFIGDIR=str(owned / "matplotlib"),
        TMPDIR=str(owned / "tmp"),
        LATENTTRIGGER_AUDIT_OWNED_ROOT=str(owned),
        RUFF_NO_CACHE="true",
        OMP_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        VECLIB_MAXIMUM_THREADS="1",
        NUMEXPR_NUM_THREADS="1",
        BLOSC_NTHREADS="1",
    )
    (owned / "tmp").mkdir()
    command = [
        sys.executable,
        "-B",
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "-p",
        "tests.scientific_audit_plugin",
        "--basetemp",
        str(owned / "fixtures"),
        "--junitxml",
        str(owned / "junit.xml"),
        "-q",
    ]
    if args.collect_only:
        command.append("--collect-only")
    if args.tests:
        command.extend(args.tests)
    started = time.monotonic()
    bundle = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for folder in ("src", "tests", "scripts", "configs", ".github")
        for path in sorted((ROOT / folder).rglob("*"))
        if path.is_file() and path.suffix in (".py", ".json", ".yml")
    }
    (owned / "source-bundle.json").write_text(json.dumps(bundle, indent=2) + "\n")
    # One bounded process group. No favorable-scheduling or automatic retry loop.
    with (owned / "pytest.log").open("x") as log:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        reason = None
        peak_bytes = 0
        try:
            while process.poll() is None:
                size = sum(p.stat().st_size for p in owned.rglob("*") if p.is_file())
                peak_bytes = max(peak_bytes, size)
                if time.monotonic() - started > 180 or size > 2 * 1024**3:
                    reason = "180s wall or 2GiB observed storage ceiling"
                    break
                time.sleep(0.25)
        finally:
            if process.poll() is None:
                import signal

                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
    result = dict(
        command=command,
        returncode=process.returncode,
        stop_reason=reason,
        elapsed_seconds=time.monotonic() - started,
        observed_peak_owned_bytes=peak_bytes,
        source_bundle_sha256=hashlib.sha256(
            json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        dependency_versions={
            name: importlib.metadata.version(name)
            for name in (
                "numpy",
                "torch",
                "scikit-learn",
                "scipy",
                "pytest",
                "ruff",
                "h5py",
            )
        },
        environment={
            k: environment[k]
            for k in (
                "PYTHONDONTWRITEBYTECODE",
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
                "XDG_CACHE_HOME",
                "MPLCONFIGDIR",
                "TMPDIR",
            )
        },
        root=str(owned),
        note="Generated fits/forwards/calibration are positive work; no scientific usefulness evidence",
    )
    (owned / "run.json").write_text(json.dumps(result, indent=2) + "\n")
    print((owned / "pytest.log").read_text()[-14000:])
    print(json.dumps(result, indent=2))
    raise SystemExit(process.returncode or bool(reason))


if __name__ == "__main__":
    main()
