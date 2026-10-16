"""One bounded native synthetic integration, run explicitly before freeze."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.feature_score_fixtures import fixture_plan

from raregate.diagnostics import protocol as p


def main():
    with tempfile.TemporaryDirectory(prefix="task0033-native-") as directory:
        root = Path(directory)
        fixture_plan(root)
        run = subprocess.run(
            [
                sys.executable,
                "-m",
                "raregate.diagnostics.controller",
                "--synthetic-root",
                str(root),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(run.stdout)
        print(run.stderr)
        if run.returncode:
            for path in (root / "session").rglob("*.log"):
                print(path.name, path.read_text())
            for path in (root / "session").rglob("receipt.json"):
                print(path.name, path.read_text()[:4000])
        assert run.returncode == 0
        workflow = p.read(root / "session/workflow.json")
        assert (
            workflow["status"] == "parent_accepted"
            and workflow["sleep_assertion"]["released"]
        )
        assert workflow["stages"]["analysis"]["access"]["feature_rows_read"] == 80
        assert (
            workflow["stages"]["analysis"]["access"]["stored_score_values_read"] == 160
        )
        p.durable_json(
            p.ROOT / "data/task0033-validation/native-synthetic.json", workflow
        )
        print(
            json.dumps(
                dict(
                    status="passed",
                    elapsed=workflow["reserved_continuous_seconds"],
                    operational_numerical_access=0,
                )
            )
        )


if __name__ == "__main__":
    main()
