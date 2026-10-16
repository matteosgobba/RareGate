"""Explicit Task0060 portable boundary; opt in, never an operational permit."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Complete historical service/model matrices and large repeated source-bundle
# fixtures are kept out of this finite audit. Their pure guard tests elsewhere run.
EXCLUDED_MODULES = {
    "test_development_decision.py",
    "test_development_payload.py",
    "test_partial_raw_chain.py",
    "test_targeted_raw_chain.py",
    "test_targeted_raw_service.py",
    "test_joint_service_replay.py",
    "test_occupancy_service_replay.py",
    "test_refined_service_replay.py",
    "test_prepared_service.py",
    "test_development_raw.py",
}


def pytest_sessionstart(session):
    """Fail closed on original payload opens and writes into the checkout."""
    if os.environ.get("RAREGATE_AUDIT_OWNED_ROOT") is None:
        raise RuntimeError("Use scripts/run_scientific_audit.py")

    def guard(event, args):
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).absolute()
        if path.is_relative_to(ROOT):
            relative = path.relative_to(ROOT)
            if relative.parts[0] in ("data", "artifacts"):
                raise RuntimeError(f"Task0060 original payload boundary: {relative}")
            mode, flags = args[1:3]
            if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int)
                and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            ):
                raise RuntimeError(f"Task0060 checkout write boundary: {relative}")

    sys.addaudithook(guard)


def pytest_collection_modifyitems(config, items):
    selected, excluded = [], []
    for item in items:
        if item.path.name in EXCLUDED_MODULES:
            excluded.append(item)
        else:
            selected.append(item)
    items[:] = selected
    config.hook.pytest_deselected(items=excluded)


def pytest_runtest_logreport(report):
    # Persist every stage promptly, including failures if the outer bound stops us.
    path = Path(os.environ["RAREGATE_AUDIT_OWNED_ROOT"]) / "reports.jsonl"
    with path.open("a") as stream:
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
