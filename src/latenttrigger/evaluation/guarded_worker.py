"""Fresh native custody/evaluation worker; body receipt awaits parent-confirmed exit."""

import argparse
import os
import sys
import time

from latenttrigger.benchmarks import protocol as p
from latenttrigger.evaluation import guarded_protocol as q
from latenttrigger.evaluation.guard import Guard
from latenttrigger.evaluation.guarded_audit import exposure


def bindings(root, mode, phase, token):
    spec = q.load(root)
    base = q.fixed(root, q.OUTPUT + "/" + mode)
    grant = p.read(base / (phase + "-grant.json"))
    reserved = p.read(base / "reservation.json")
    if (
        mode not in ("readiness", "final")
        or phase
        not in (("custody",) if mode == "readiness" else ("PCA", "AE", "consolidate"))
        or grant["phase"] != phase
        or grant["token"] != token
        or grant["parent_pid"] != os.getppid()
        or reserved["parent_pid"] != os.getppid()
        or reserved["source_file_sha256"] != q.source_map(root)
        or reserved["protocol_canonical_JSON_sha256"] != q.HASH
        or grant["reservation_file_byte_sha256"]
        != p.file_hash(base / "reservation.json")
        or p.file_hash(base / "acceptance.json")
        != reserved["software_acceptance_file_byte_sha256"]
        or p.digest(p.read(base / "protocol.json")) != q.HASH
        or (base / phase / "receipt.json").exists()
    ):
        raise ValueError("Foreign/source/parent/token/protocol/duplicate worker grant.")
    prior = (
        ()
        if mode == "readiness"
        else ("PCA", "AE", "consolidate")[: ("PCA", "AE", "consolidate").index(phase)]
    )
    if list(grant["predecessors"]) != list(prior):
        raise ValueError("Out-of-order final worker.")
    for name, h in grant["predecessors"].items():
        if (
            p.file_hash(base / name / "parent-acceptance.json") != h
            or p.read(base / name / "parent-acceptance.json")["status"]
            != "parent_accepted"
        ):
            raise ValueError("Failed/incomplete predecessor.")
        accepted = p.read(base / name / "parent-acceptance.json")
        if (
            p.file_hash(base / name / "receipt.json")
            != accepted["receipt_file_byte_sha256"]
        ):
            raise ValueError("Predecessor receipt identity changed.")
        for filename, digest in accepted["output_file_byte_sha256"].items():
            if p.file_hash(base / name / filename) != digest:
                raise ValueError("Predecessor scientific/score/audit output mutation.")
    if any(
        name in sys.modules
        for name in ("numpy", "torch", "sklearn", "onnx", "onnxruntime")
    ):
        raise ValueError("Framework import before guard/source/thread checks.")
    if any(
        os.environ.get(k) != v
        for k, v in spec["runtime"]["thread_environment_before_imports"].items()
    ):
        raise ValueError("Pinned thread environment must precede imports.")
    q.acceptance(root)
    q.metadata(root, spec)
    if mode == "final":
        consent, plan = q.authorization(
            root,
            allow_test=True,
            approved_plan_sha256=reserved["plan_canonical_JSON_sha256"],
        )
        if p.file_hash(root / q.CONSENT) != reserved["authorization_file_byte_sha256"]:
            raise ValueError("Authorization changed after reservation.")
    else:
        consent = plan = None
    return base, grant, reserved, spec, consent, plan


def execute(mode, phase, token, root=q.ROOT):
    base = q.fixed(root, q.OUTPUT + "/" + mode)
    directory = base / phase
    grant = p.read(base / (phase + "-grant.json"))
    if (
        grant.get("token") != token
        or grant.get("parent_pid") != os.getppid()
        or (directory / "receipt.json").exists()
    ):
        raise ValueError("Foreign/duplicate worker before writes.")
    started = grant["started_monotonic"]
    deadline = grant["operation_deadline_monotonic"]
    guard = limiter = store = None
    candidate = None
    result = dict(
        task="0026",
        mode=mode,
        phase=phase,
        status="failed",
        timings={},
        custody_operations_started=0,
        custody_operations_completed=0,
        population_requests=0,
        optimizer_updates=0,
    )

    def stage(name, function):
        guard.boundary(name)
        tick = time.monotonic()
        try:
            return function()
        finally:
            result["timings"][name + "_seconds"] = time.monotonic() - tick
            p.write(directory / "partial.json", result)

    try:
        guard = Guard(deadline, directory=directory)
        guard.__enter__()
        base, grant, reserved, spec, consent, plan = bindings(root, mode, phase, token)
        result.update(
            source_file_sha256=reserved["source_file_sha256"],
            protocol_canonical_JSON_sha256=q.HASH,
            grant_file_byte_sha256=p.file_hash(base / (phase + "-grant.json")),
        )
        tick = time.monotonic()
        from latenttrigger.benchmarks import core
        from latenttrigger.data.processed import ProcessedStore
        from latenttrigger.evaluation import guarded_core as n

        result["timings"]["numerical_imports_seconds"] = time.monotonic() - tick
        limiter, result["threads_before"] = stage(
            "native_thread_enforcement", lambda: core.configure_threads(spec)
        )
        if (
            p.digest(core.torch.__config__.show())
            != spec["torch_build_canonical_JSON_string_sha256"]
            or p.runtime_versions() != spec["core_versions"]
        ):
            raise ValueError("Pinned native build/runtime changed.")
        guard.context()
        if phase == "consolidate":
            from latenttrigger.evaluation.guarded_reporting import reporting

            result["comparison"] = stage(
                "reporting", lambda: reporting(base, spec["candidates"])
            )
        else:
            entries = (
                spec["candidates"]
                if mode == "readiness"
                else [spec["candidates"][0 if phase == "PCA" else 1]]
            )
            loaded = stage(
                "frozen_candidate_loading",
                lambda: [n.load_candidate(root, entry) for entry in entries],
            )
            result["custody_operations_started"] = 1
            p.write(
                directory / "custody.json",
                dict(
                    status="started",
                    constructor="unchanged ProcessedStore full verify_store",
                    population_requests=0,
                ),
                exclusive=True,
            )
            store = stage(
                "full_store_constructor_custody",
                lambda: ProcessedStore(q.fixed(root, spec["store"]["path"])),
            )
            for c in loaded:
                n.validate_manifest(c, store.manifest)
            result["custody_operations_completed"] = 1
            p.write(
                directory / "custody.json",
                dict(
                    status="completed",
                    constructor="unchanged ProcessedStore full verify_store",
                    population_requests=0,
                    store_scientific_sha256=store.manifest["scientific_sha256"],
                ),
            )
            if (
                store.manifest["scientific_sha256"]
                != spec["store"]["scientific_sha256"]
            ):
                raise ValueError("Verified custody store identity mismatch.")
            result["verified_store_scientific_sha256"] = store.manifest[
                "scientific_sha256"
            ]
            if mode == "final":
                candidate = loaded[0]
                binding = dict(
                    authorization_file_byte_sha256=reserved[
                        "authorization_file_byte_sha256"
                    ],
                    explicit_human_message=consent["human_message"],
                    plan_canonical_JSON_sha256=p.digest(plan),
                    source_file_sha256=q.source_map(root),
                    code=p.code_context(root),
                    candidate=entries[0],
                    store=spec["store"],
                    metrics=spec["metrics"],
                )
                result["scientific_output"] = stage(
                    "population_scoring_metrics_serialization",
                    lambda: n.evaluate_candidate(
                        candidate, store, directory, binding, guard, authorized=True
                    ),
                )
            loaded = candidate = None
            stage("store_cleanup", store.close)
            store = None
        guard.boundary("restore_final_identities")
        q.metadata(root, spec)
        q.acceptance(root)
        result["threads_after"] = core.effective_threads()
        if result["threads_before"] != result["threads_after"]:
            raise ValueError("Native effective threads changed.")
        guard.context()
        result["status"] = "body_complete_awaiting_exit"
    except BaseException as exc:
        result.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    finally:
        tick = time.monotonic()
        try:
            if store:
                store.close()
            candidate = None
            if limiter:
                limiter.restore_original_limits()
        except BaseException as exc:
            result.update(status="failed", cleanup_error=str(exc))
        finally:
            if guard:
                guard.close()
                result["resources"] = guard.report()
                if guard.error:
                    result.update(status="failed", guard_error=guard.error)
        result["resource_monitor_closed_monotonic"] = time.monotonic()
        result["timings"]["cleanup_seconds"] = time.monotonic() - tick
        result["exposure"] = exposure(directory / "test-unblinding.json")
        result["population_requests"] = result["exposure"]["population_requests"]
        result["worker_reported_wall_seconds"] = time.monotonic() - started
        if (
            result["worker_reported_wall_seconds"] > grant["stage_seconds"]
            or result["timings"]["cleanup_seconds"] > 2
        ):
            result.update(
                status="failed", error="Worker body/cleanup deadline exceeded."
            )
        result["output_file_byte_sha256"] = {
            f.name: p.file_hash(f)
            for f in directory.iterdir()
            if f.is_file()
            and f.name
            in (
                "evaluation.json",
                "background-summary.json",
                "test_background-scores.npy",
                "test_signal-scores.npy",
                "test-unblinding.json",
            )
        }
        p.write(directory / "receipt.json", result, exclusive=True)
    return 0 if result["status"] == "body_complete_awaiting_exit" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("readiness", "final"), required=True)
    parser.add_argument(
        "--phase", choices=("custody", "PCA", "AE", "consolidate"), required=True
    )
    parser.add_argument("--token", required=True)
    a = parser.parse_args()
    return execute(a.mode, a.phase, a.token)


if __name__ == "__main__":
    raise SystemExit(main())
