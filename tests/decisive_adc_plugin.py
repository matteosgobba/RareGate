"""Explicit generated-only Task0061 validation; no real permit creation."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pytest_sessionstart(session):
    owned = Path(os.environ["RAREGATE_ADC_TEST_ROOT"]).resolve()

    def guard(event, args):
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if path.is_relative_to(ROOT / "data") or path.is_relative_to(
            ROOT / "artifacts"
        ):
            if not path.is_relative_to(owned):
                raise PermissionError(
                    "generated validation cannot open real data/model paths"
                )
        if path.is_relative_to(ROOT):
            mode, flags = args[1:3]
            write = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int)
                and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            )
            if write and not path.is_relative_to(owned):
                raise PermissionError("validation checkout write denied")

    sys.addaudithook(guard)


def pytest_runtest_logreport(report):
    target = Path(os.environ["RAREGATE_ADC_TEST_ROOT"]) / "reports.jsonl"
    with target.open("a") as stream:
        stream.write(
            json.dumps(
                dict(
                    nodeid=report.nodeid,
                    stage=report.when,
                    outcome=report.outcome,
                    duration=report.duration,
                    failure=str(report.longrepr) if report.failed else None,
                )
            )
            + "\n"
        )
    module = sys.modules.get("test_decisive_adc") or sys.modules.get(
        "tests.test_decisive_adc"
    )
    if module is not None:
        (target.parent / "toy-work-progress.json").write_text(
            json.dumps(module.TALLY, indent=2) + "\n"
        )


def pytest_sessionfinish(session, exitstatus):
    module = sys.modules.get("test_decisive_adc") or sys.modules.get(
        "tests.test_decisive_adc"
    )
    if module is not None:
        path = Path(os.environ["RAREGATE_ADC_TEST_ROOT"]) / "toy-work.json"
        path.write_text(json.dumps(module.TALLY, indent=2) + "\n")
