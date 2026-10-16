"""Finite generated Task0061 checks in a new owned subroot; no real activation."""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    study = ROOT / "data/decisive-v2-adc-task0061"
    owned = study / "tests" / f"validation-{args.attempt}"
    owned.mkdir(exist_ok=False)
    (owned / "tmp").mkdir()
    spec = importlib.util.spec_from_file_location(
        "adc_entrypoint", ROOT / "scripts/prepare_decisive_adc_experiment.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.configure(owned)
    os.environ["RAREGATE_ADC_TEST_ROOT"] = str(owned)
    os.environ["RAREGATE_AUDIT_OWNED_ROOT"] = str(owned)
    from raregate.research.decisive_adc.execution import (
        behavioral_bundle,
        binding_digest,
    )

    bundle = behavioral_bundle()
    (owned / "source-bundle.json").write_text(json.dumps(bundle, indent=2) + "\n")
    command = [
        sys.executable,
        "-B",
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "-p",
        "tests.decisive_adc_plugin",
        "--basetemp",
        str(owned / "fixtures"),
        "--junitxml",
        str(owned / "junit.xml"),
        "-q",
    ]
    command += ["tests/test_decisive_adc.py"] + [
        f"tests/test_{name}.py"
        for name in (
            "evaluation",
            "splitting",
            "inspection",
            "features",
            "pca",
            "autoencoder",
            "scientific_audit",
        )
    ]
    started = time.monotonic()
    reason = None
    storage_peak = rss_peak = 0
    with (owned / "pytest.log").open("x") as output:
        process = subprocess.Popen(
            command,
            env=dict(os.environ),
            cwd=ROOT,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        (owned / "pid.json").write_text(
            json.dumps(dict(pid=process.pid, parent_pid=os.getpid())) + "\n"
        )
        try:
            while process.poll() is None:
                storage = module.owned_bytes(
                    study, ROOT / "artifacts/models/decisive-v2-adc"
                )
                storage_peak = max(storage_peak, storage)
                query = subprocess.run(
                    ["ps", "-o", "rss=", "-p", str(process.pid)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                rss = int(query.stdout.strip() or 0) * 1024
                rss_peak = max(rss_peak, rss)
                inclusive = (
                    datetime.now(UTC) - datetime(2026, 10, 16, 12, 15, 45, tzinfo=UTC)
                ).total_seconds()
                if (
                    storage > 8589934592
                    or rss > 4294967296
                    or time.monotonic() - started > 180
                    or inclusive > 14400 - 10
                ):
                    reason = "generated validation wall/RSS/storage/task stop"
                    break
                time.sleep(0.25)
        except BaseException as error:
            reason = "observer exception: " + repr(error)
        finally:
            module.reap(process)
    record = dict(
        attempt=args.attempt,
        scope="generated-ADC-test-only",
        command=command,
        returncode=process.returncode,
        stop_reason=reason,
        elapsed_including_exit_reap=time.monotonic() - started,
        peak_observed_study_bytes=storage_peak,
        peak_sampled_worker_RSS_bytes=rss_peak,
        bundle_sha256=binding_digest(bundle),
        tests_source_bundle=bundle,
        worker_reaped=True,
    )
    (owned / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print((owned / "pytest.log").read_text()[-18000:])
    print(
        json.dumps(
            {k: v for k, v in record.items() if k != "tests_source_bundle"}, indent=2
        )
    )
    raise SystemExit(process.returncode or bool(reason))


if __name__ == "__main__":
    main()
