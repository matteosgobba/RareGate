"""Task0031 fresh numerical workers, provisional body then independent parent exit."""

import argparse
import os
import time

from latenttrigger.benchmarks import protocol as p
from latenttrigger.data.three_prong_v3_runtime import ContinuousClock, check_deadline
from latenttrigger.data.three_prong_v3_worker import AssertionMonitor
from latenttrigger.evaluation import local_three_prong_protocol as q
from latenttrigger.evaluation.guard import Guard
from latenttrigger.evaluation.local_three_prong_audit import Audit, exposure


def bindings(root, phase, token, clock, deadline):
    spec = q.load(root)
    base = root / q.OUTPUT
    reservation = p.read(base / "reservation.json")
    grant = p.read(base / (phase + "-grant.json"))
    q.require(
        phase in q.PHASES
        and grant["phase"] == phase
        and grant["token"] == token
        and grant["parent_pid"] == reservation["parent_pid"] == os.getppid()
        and not (base / phase / "receipt.json").exists(),
        "Foreign/duplicate worker/token/parent",
    )
    q.require(
        reservation["source_file_sha256"] == q.source_map(root)
        and reservation["protocol_canonical_JSON_sha256"] == q.HASH
        and grant["reservation_file_byte_sha256"]
        == p.file_hash(base / "reservation.json"),
        "Frozen source/reservation drift",
    )
    seconds = spec["limits"][phase + "_seconds"]
    q.require(
        grant["stage_deadline_continuous"] == grant["started_continuous"] + seconds
        and grant["operation_deadline_continuous"]
        == grant["stage_deadline_continuous"] - 2
        and grant["stage_deadline_continuous"]
        <= reservation["whole_deadline_continuous"]
        and reservation["whole_deadline_continuous"]
        == reservation["reserved_continuous"] + 600
        and grant["sleep_helper_pid"] == reservation["sleep_helper_pid"]
        and grant["sleep_assertion_id"] == reservation["sleep_assertion_id"],
        "Changed continuous grant/assertion",
    )
    for source, target in (
        (q.CONFIG, "protocol.json"),
        (q.ACCEPTANCE, "acceptance.json"),
        (q.CONSENT, "authorization.json"),
    ):
        q.require(
            p.file_hash(base / target) == p.file_hash(root / source),
            "Copied bound bytes changed",
        )
    q.authorization(root, clock=clock, deadline=deadline)
    q.metadata(root, spec, clock=clock, deadline=deadline, check_payload=False)
    q.require(
        list(grant["predecessors"]) == list(q.PHASES[: q.PHASES.index(phase)]),
        "Out-of-order predecessor",
    )
    for prior, sha in grant["predecessors"].items():
        path = q.check_file(
            root,
            q.OUTPUT + "/" + prior + "/parent-acceptance.json",
            sha,
            clock=clock,
            deadline=deadline,
        )
        doc = p.read(path)
        q.require(doc["status"] == "parent_accepted", "Failed predecessor")
        q.check_file(
            root,
            q.OUTPUT + "/" + prior + "/receipt.json",
            doc["receipt_file_byte_sha256"],
            clock=clock,
            deadline=deadline,
        )
        for file, digest in doc["output_file_byte_sha256"].items():
            q.check_file(root, file, digest, clock=clock, deadline=deadline)
    q.require(
        all(
            os.environ.get(k) == v
            for k, v in spec["runtime"]["thread_environment_before_imports"].items()
        ),
        "Preimport thread environment",
    )
    check_deadline(clock, deadline)
    return spec, grant, reservation


def execute(phase, token, root=q.ROOT):
    clock = ContinuousClock()
    base = root / q.OUTPUT
    directory = base / phase
    grant = p.read(base / (phase + "-grant.json"))
    q.require(
        grant["parent_pid"] == os.getppid()
        and grant["token"] == token
        and not (directory / "receipt.json").exists(),
        "Foreign worker before writes",
    )
    started = clock()
    ordinary = time.monotonic()
    guard = limiter = audit = None
    outputs = []
    result = dict(
        task="0031",
        phase=phase,
        status="failed",
        optimizer_updates=0,
        new_original_background_forward_calls=0,
        download_requests=0,
        timings={},
        started=clock.snapshot(),
    )
    try:
        guard = Guard(
            grant["operation_deadline_continuous"],
            clock=clock,
            directory=directory,
            journal_limit=64 * 2**20,
        )
        guard.__enter__()
        monitor = AssertionMonitor(grant, clock)
        probe = guard.probe

        def asserted_probe():
            monitor.check()
            return probe()

        guard.probe = asserted_probe
        guard.check()
        spec, grant, reservation = bindings(root, phase, token, clock, guard.deadline)
        result.update(
            source_file_sha256=q.source_map(root),
            protocol_canonical_JSON_sha256=q.HASH,
            grant_file_byte_sha256=p.file_hash(base / (phase + "-grant.json")),
        )
        audit = Audit(
            directory / "access.json",
            dict(
                phase=phase,
                plan_sha256=reservation["plan_sha256"],
                source_file_sha256=reservation["source_file_sha256"],
                specification_sha256=q.HASH,
            ),
        )
        from latenttrigger.benchmarks import core
        from latenttrigger.evaluation import local_three_prong_core as n

        limiter, result["threads_before"] = core.configure_threads(spec)
        q.require(
            p.digest(core.torch.__config__.show())
            == spec["torch_build_canonical_JSON_string_sha256"]
            and p.runtime_versions() == spec["core_versions"],
            "Frozen native runtime/build",
        )
        guard.context()
        guard.boundary(phase)
        tick = clock()
        if phase == "prepare":
            result["prepared_scientific"] = n.prepare(
                root, spec, directory, audit, guard
            )
            outputs = [
                root / q.PREPARED / f
                for f in ("event_features.npy", "fingerprints.npy", "manifest.json")
            ] + [directory / f for f in ("validity.json", "overlap.json")]
        elif phase in ("PCA", "AE"):
            result["evaluation"] = n.evaluate(
                root, spec, phase, directory, audit, guard
            )
            outputs = [
                directory / f
                for f in (
                    "evaluation.json",
                    "background-summary.json",
                    "three-prong-scores.npy",
                    "curves.npz",
                )
            ]
        else:
            from latenttrigger.evaluation.local_three_prong_reporting import reporting

            result["comparison"] = reporting(root, spec, base, directory, audit, guard)
            outputs = [
                directory / f
                for f in (
                    "comparison.json",
                    "scientific-comparison.csv",
                    "calibrated-operating-points.csv",
                    "empirical-operating-points.csv",
                    "two-vs-three-prong.csv",
                    "roc-pr.png",
                )
            ]
        result["timings"]["body_continuous_seconds"] = clock() - tick
        result["threads_after"] = core.effective_threads()
        q.require(
            result["threads_before"] == result["threads_after"],
            "Stable effective native threads",
        )
        q.metadata(
            root, spec, clock=clock, deadline=guard.deadline, check_payload=False
        )
        q.acceptance(root, clock=clock, deadline=guard.deadline)
        guard.boundary("final_bindings")
        result["status"] = "body_complete_awaiting_exit"
    except BaseException as error:
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        tick = clock()
        if limiter:
            try:
                limiter.restore_original_limits()
            except BaseException as error:
                result.update(status="failed", cleanup_error=str(error))
        if audit:
            audit.finish(result["status"], result.get("error"))
            outputs.append(directory / "access.json")
        if guard:
            guard.close()
            result["resources"] = guard.report()
            if guard.error:
                result.update(status="failed", guard_error=guard.error)
        result.update(
            resource_monitor_closed_continuous=clock(),
            finished=clock.snapshot(),
            worker_elapsed_continuous_seconds=clock() - started,
            worker_elapsed_ordinary_monotonic_seconds=time.monotonic() - ordinary,
        )
        result["timings"]["cleanup_continuous_seconds"] = clock() - tick
        if (
            result["timings"]["cleanup_continuous_seconds"] > 2
            or clock() >= grant["stage_deadline_continuous"]
        ):
            result["status"] = "failed"
        result["exposure"] = exposure(directory / "access.json")
        result["output_file_byte_sha256"] = {
            str(f.relative_to(root)): p.file_hash(f) for f in outputs if f.is_file()
        }
        p.write(directory / "receipt.json", result, exclusive=True)
    return 0 if result["status"] == "body_complete_awaiting_exit" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=q.PHASES)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    return execute(args.phase, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
