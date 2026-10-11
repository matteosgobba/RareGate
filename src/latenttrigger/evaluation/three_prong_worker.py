"""Fresh sequential worker: native extension bodies await independent parent exit."""

import argparse
import os
import time
from dataclasses import asdict

from latenttrigger.benchmarks import protocol as p
from latenttrigger.evaluation import three_prong_protocol as q
from latenttrigger.evaluation.guard import Guard
from latenttrigger.evaluation.three_prong_audit import Audit, exposure


def bindings(root, phase, token):
    spec = q.load(root)
    base = q.fixed(root, q.OUTPUT)
    reservation = p.read(base / "reservation.json")
    grant = p.read(base / (phase + "-grant.json"))
    q.require(
        phase in q.PHASES
        and grant["phase"] == phase
        and grant["token"] == token
        and grant["parent_pid"] == reservation["parent_pid"] == os.getppid(),
        "Foreign worker parent/phase/token",
    )
    q.require(
        grant["reservation_file_byte_sha256"] == p.file_hash(base / "reservation.json")
        and reservation["protocol_canonical_JSON_sha256"] == q.HASH
        and reservation["source_file_sha256"] == q.source_map(root)
        and not (base / phase / "receipt.json").exists(),
        "Reservation/source/protocol/duplicate worker",
    )
    q.require(
        p.file_hash(base / "acceptance.json")
        == reservation["software_acceptance_file_byte_sha256"]
        == p.file_hash(root / q.ACCEPTANCE)
        and p.digest(p.read(base / "protocol.json")) == q.HASH,
        "Campaign copied acceptance/protocol",
    )
    q.require(
        p.file_hash(base / "authorization.json")
        == reservation["authorization_file_byte_sha256"]
        == p.file_hash(root / q.CONSENT),
        "Authorization copy",
    )
    q.authorization(root, True, reservation["plan_sha256"])
    q.metadata(root, spec)
    q.acceptance(root)
    expected = list(q.PHASES[: q.PHASES.index(phase)])
    q.require(list(grant["predecessors"]) == expected, "Out-of-order worker")
    for prior, digest in grant["predecessors"].items():
        accepted = p.read(
            q.check_file(
                root, q.OUTPUT + "/" + prior + "/parent-acceptance.json", digest
            )
        )
        q.require(accepted["status"] == "parent_accepted", "Failed predecessor")
        q.check_file(
            root,
            q.OUTPUT + "/" + prior + "/receipt.json",
            accepted["receipt_file_byte_sha256"],
        )
        for path, h in accepted["output_file_byte_sha256"].items():
            q.check_file(root, path, h)
    q.require(
        all(
            os.environ.get(k) == v
            for k, v in spec["runtime"]["thread_environment_before_imports"].items()
        ),
        "Pinned preimport thread environment",
    )
    return spec, grant, reservation, base


def execute(phase, token, root=q.ROOT):
    base = q.fixed(root, q.OUTPUT)
    directory = base / phase
    grant = p.read(base / (phase + "-grant.json"))
    q.require(
        grant.get("token") == token
        and grant.get("parent_pid") == os.getppid()
        and not (directory / "receipt.json").exists(),
        "Foreign worker before writes",
    )
    result = dict(
        task="0028",
        phase=phase,
        status="failed",
        optimizer_updates=0,
        new_original_background_forward_calls=0,
        timings={},
    )
    guard = limiter = audit = None
    outputs = []
    started = time.monotonic()
    try:
        guard = Guard(grant["operation_deadline_monotonic"], directory=directory)
        guard.__enter__()
        spec, grant, reservation, base = bindings(root, phase, token)
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
        tick = time.monotonic()
        if phase == "acquire":
            from latenttrigger.data.acquisition import acquire
            from latenttrigger.data.metadata import DatasetSource

            source = DatasetSource(
                **{
                    k: v
                    for k, v in spec["source"].items()
                    if k
                    not in ("publisher_expected_events", "role", "local_payload_sha256")
                }
            )
            row = audit.request("raw_acquisition", source.expected_size)
            guard.boundary("authorized_pinned_acquisition")
            acquired = acquire(
                data_dir=q.fixed(root, q.RAW),
                source=source,
                replace_invalid=False,
                timeout=30,
            )
            audit.read(row, acquired.integrity.file_size)
            doc = dict(
                path=str(acquired.path.relative_to(root)),
                integrity=asdict(acquired.integrity),
                downloaded=acquired.downloaded,
            )
            p.write(directory / "acquisition.json", doc, exclusive=True)
            outputs = [directory / "acquisition.json"]
            result["threads_before"] = result["threads_after"] = {}
        else:
            from latenttrigger.benchmarks import core
            from latenttrigger.evaluation import three_prong_core as n

            limiter, result["threads_before"] = core.configure_threads(spec)
            q.require(
                p.digest(core.torch.__config__.show())
                == spec["torch_build_canonical_JSON_string_sha256"]
                and p.runtime_versions() == spec["core_versions"],
                "Pinned native runtime/build",
            )
            guard.context()
            if phase == "prepare":
                result["prepared_scientific"] = n.prepare(
                    root, spec, directory, audit, guard
                )
                outputs = [
                    root / q.PREPARED / "manifest.json",
                    directory / "overlap.json",
                ]
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
                    )
                ]
            else:
                from latenttrigger.evaluation.guarded_reporting import reporting

                result["comparison"] = reporting(
                    base, spec["candidates"], make_figures=False
                )
                outputs = [
                    base / f
                    for f in ("comparison.json", "calibrated-operating-points.csv")
                ]
            result["threads_after"] = core.effective_threads()
            q.require(
                result["threads_before"] == result["threads_after"],
                "Effective native threads changed",
            )
        result["timings"][phase + "_body_seconds"] = time.monotonic() - tick
        q.metadata(root, spec)
        q.acceptance(root)
        guard.boundary("final_bindings")
        result["status"] = "body_complete_awaiting_exit"
    except BaseException as exc:
        result.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    finally:
        tick = time.monotonic()
        if limiter:
            try:
                limiter.restore_original_limits()
            except BaseException as exc:
                result.update(status="failed", cleanup_error=str(exc))
        if audit:
            audit.finish(result["status"], result.get("error"))
            outputs.append(directory / "access.json")
        if guard:
            guard.close()
            result["resources"] = guard.report()
            if guard.error:
                result.update(status="failed", guard_error=guard.error)
        result.update(
            resource_monitor_closed_monotonic=time.monotonic(),
            worker_reported_wall_seconds=time.monotonic() - started,
        )
        result["timings"]["cleanup_seconds"] = time.monotonic() - tick
        if result["timings"]["cleanup_seconds"] > 2:
            result["status"] = "failed"
        result["exposure"] = exposure(directory / "access.json")
        result["output_file_byte_sha256"] = {
            str(f.relative_to(root)): p.file_hash(f) for f in outputs if f.is_file()
        }
        p.write(directory / "receipt.json", result, exclusive=True)
    return 0 if result["status"] == "body_complete_awaiting_exit" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=q.PHASES, required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    return execute(args.phase, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
