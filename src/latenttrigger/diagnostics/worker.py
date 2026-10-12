"""Two fresh guarded workers; completed bodies await independent parent acceptance."""

import argparse
import os
import time
from pathlib import Path

from latenttrigger.diagnostics import protocol as p
from latenttrigger.diagnostics.runtime import (
    ContinuousClock,
    DiagnosticGuard,
    install_boundary,
)


def execute(base, phase, token):
    clock = ContinuousClock()
    base = Path(base)
    directory = base / phase
    grant = p.read(base / (phase + "-grant.json"))
    p.require(
        grant["token"] == token
        and grant["parent_pid"] == os.getppid()
        and grant["phase"] == phase,
        "Foreign worker grant",
    )
    guard = DiagnosticGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    result = dict(
        phase=phase,
        status="failed",
        started=clock.snapshot(),
        source_file_sha256=grant["source_file_sha256"],
        grant_file_byte_sha256=p.file_hash(base / (phase + "-grant.json")),
        plan_file_byte_sha256=grant["plan_file_byte_sha256"],
    )
    cleanup_start = None
    try:
        guard.__enter__()
        p.require(
            grant["source_file_sha256"] == p.source_map(),
            "Current source differs from grant",
        )
        p.require(grant["dependencies"] == p.runtime_versions(), "Dependency identity")
        plan = p.read(base / "plan.json")
        p.require(
            p.file_hash(base / "plan.json") == grant["plan_file_byte_sha256"]
            and p.digest(plan) == grant["plan_canonical_sha256"],
            "Plan identity",
        )
        reservation = p.read(base / "reservation.json")
        p.require(
            grant["reservation_file_byte_sha256"]
            == p.file_hash(base / "reservation.json")
            and reservation["parent_pid"] == os.getppid(),
            "Reservation identity",
        )
        p.require(
            all(os.environ.get(k) == v for k, v in grant["thread_environment"].items()),
            "Thread environment must precede imports",
        )
        root = Path(grant["input_root"])
        if phase == "analysis":
            install_boundary(
                root, plan["arrays"], plan["metadata"], directory, phase=phase
            )
            from latenttrigger.diagnostics.analysis import TABLES, analyze
            from latenttrigger.diagnostics.reader import AccessLedger

            ledger = AccessLedger(directory / "access.json")
            guard.context()
            p.verify_inputs(root, plan, ledger.record)
            guard.boundary("before_numerical_population_access")
            analyze(root, plan, directory, ledger, guard)
            result["access"] = ledger.summary()
            outputs = [*TABLES, "analysis-summary.json", "access.json"]
        else:
            analysis = base / "analysis"
            prior = p.read(analysis / "parent-acceptance.json")
            p.require(
                prior["status"] == "parent_accepted"
                and p.file_hash(analysis / "parent-acceptance.json")
                == grant["predecessor_parent_sha256"],
                "Unaccepted/altered analysis",
            )
            from latenttrigger.diagnostics.reporting import FIGURES, TABLES, render

            identities = {n: prior["output_file_byte_sha256"][n] for n in TABLES}
            allowed = (
                [str((analysis / n).relative_to(root)) for n in TABLES]
                if analysis.is_relative_to(root)
                else []
            )
            # Synthetic fixture root is separate: use common parent only for the
            # I/O boundary, with absolute aggregate identities converted below.
            boundary_root = root if allowed else base.parent
            allowed = allowed or [
                str((analysis / n).relative_to(boundary_root)) for n in TABLES
            ]
            install_boundary(boundary_root, [], allowed, directory, phase=phase)
            guard.context()
            render(analysis, directory, identities, guard.check)
            result["access"] = dict(
                population_or_score_array_reloads=0,
                input_scope="five owned aggregate CSVs",
            )
            outputs = [*FIGURES, "reporting-summary.json"]
        guard.boundary("outputs_complete")
        result["output_file_byte_sha256"] = {
            name: p.file_hash(directory / name) for name in outputs
        }
        result["status"] = "body_complete_awaiting_exit"
    except BaseException as error:
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        cleanup_start = clock()
        guard.close()
        result.update(
            resources=guard.report(),
            monitor_closed_continuous=clock(),
            cleanup_continuous_seconds=clock() - cleanup_start,
            finished=clock.snapshot(),
            worker_elapsed_continuous_seconds=clock() - grant["started_continuous"],
            worker_elapsed_ordinary_seconds=time.monotonic()
            - grant["started_ordinary"],
        )
        p.durable_json(directory / "receipt.json", result, exclusive=True)
    return 0 if result["status"] == "body_complete_awaiting_exit" else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--phase", choices=["analysis", "reporting"], required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    raise SystemExit(execute(args.base, args.phase, args.token))


if __name__ == "__main__":
    main()
