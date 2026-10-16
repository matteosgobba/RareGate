"""Stdlib isolated evaluation CLI; readiness never reserves final unblinding."""

import argparse
import os
import secrets
import subprocess
import sys
import time

from raregate.benchmarks import protocol as p
from raregate.benchmarks.frozen_cpu import terminate
from raregate.benchmarks.frozen_cpu_v2 import fresh_hardware
from raregate.evaluation import guarded_protocol as q
from raregate.evaluation.guard import parent_check
from raregate.evaluation.guarded_audit import durable, exposure


def supervise(command, log, *, root, environment, stage_seconds, whole_deadline):
    started = time.monotonic()
    stage_deadline = min(started + stage_seconds, whole_deadline)
    operation_deadline = stage_deadline - 2
    child = None
    error = None
    exit_seen = None
    try:
        if time.monotonic() >= operation_deadline:
            raise TimeoutError("No cleanup slack before dispatch.")
        with log.open("x") as stream:
            child = subprocess.Popen(
                command,
                cwd=root,
                env=environment,
                stdout=stream,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            while child.poll() is None:
                parent_check(deadline=whole_deadline)
                if time.monotonic() >= operation_deadline:
                    raise TimeoutError("Independent import/operation/exit deadline.")
                if log.stat().st_size > 2**20:
                    raise ValueError("Bounded worker log exceeded.")
                try:
                    child.wait(timeout=0.05)
                except subprocess.TimeoutExpired:
                    pass
            exit_seen = time.monotonic()
    except BaseException as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if child is not None:
            try:
                terminate(child, min(time.monotonic() + 2, stage_deadline))
            except BaseException as exc:
                error = error or str(exc)
            exit_seen = exit_seen or time.monotonic()
    elapsed = time.monotonic() - started
    return dict(
        returncode=child.returncode if child else None,
        parent_error=error,
        child_reaped=child is not None and child.poll() is not None,
        started_monotonic=started,
        exit_observed_monotonic=exit_seen,
        stage_seconds=stage_seconds,
        elapsed_seconds=elapsed,
        within_deadline=elapsed <= stage_seconds and time.monotonic() <= whole_deadline,
        parent_confirms_normal_exit=child is not None
        and child.returncode == 0
        and error is None,
    )


def namespace(root, mode):
    if mode not in ("readiness", "final"):
        raise ValueError("Only fixed readiness/final scope; no alternate selector.")
    base = q.fixed(root, q.OUTPUT)
    if base.exists() and any(
        f.name not in ("readiness", "final") or f.is_symlink() for f in base.iterdir()
    ):
        raise ValueError("Foreign evaluation namespace.")
    path = q.fixed(root, q.OUTPUT + "/" + mode)
    if path.exists():
        raise ValueError("Fixed stage reserved/partial/consumed; no retry.")
    return path


def prerequisites(root, mode, *, allow_test=False, approved_plan_sha256=None):
    if any(
        n in sys.modules for n in ("numpy", "torch", "onnx", "onnxruntime", "sklearn")
    ):
        raise ValueError("Controller stays stdlib-only.")
    parent_check()
    if sys.platform != "darwin":
        raise ValueError("Supported primary Darwin execution accounting required.")
    spec = q.load(root)
    meta = q.metadata(root, spec)
    accepted = q.acceptance(root)
    namespace(root, mode)
    consent = plan = None
    if mode == "final":
        consent, plan = q.authorization(
            root, allow_test=allow_test, approved_plan_sha256=approved_plan_sha256
        )
        ready = p.read(root / q.OUTPUT / "readiness/parent-acceptance.json")
        if (
            ready["status"] != "parent_accepted"
            or ready["source_file_sha256"] != q.source_map(root)
            or ready["software_acceptance_file_byte_sha256"]
            != p.file_hash(root / q.ACCEPTANCE)
        ):
            raise ValueError("Accepted current custody readiness required.")
    return spec, meta, accepted, consent, plan


def reserve(
    root,
    mode,
    spec,
    accepted,
    meta,
    *,
    consent=None,
    plan=None,
    on_created=lambda: None,
):
    path = namespace(root, mode)
    path.parent.mkdir(exist_ok=True, parents=True)
    path.mkdir(exist_ok=False)
    on_created()
    reservation = dict(
        task="0026",
        mode=mode,
        status="reserved_no_retry",
        parent_pid=os.getpid(),
        started_monotonic=time.monotonic(),
        reserved_utc=p.now(),
        protocol_canonical_JSON_sha256=q.HASH,
        source_file_sha256=q.source_map(root),
        software_acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
        metadata=meta,
        code=p.code_context(root),
    )
    if reservation["source_file_sha256"] != accepted["source_file_sha256"]:
        raise ValueError("Source changed during reservation; slot consumed.")
    if mode == "final":
        reservation.update(
            plan_canonical_JSON_sha256=p.digest(plan),
            authorization_file_byte_sha256=p.file_hash(root / q.CONSENT),
        )
    p.write(path / "reservation.json", reservation, exclusive=True)
    p.write(path / "protocol.json", spec, exclusive=True)
    with (path / "acceptance.json").open("xb") as f:
        f.write((root / q.ACCEPTANCE).read_bytes())
    if mode == "final":
        with (path / "authorization.json").open("xb") as f:
            f.write((root / q.CONSENT).read_bytes())
        durable(
            path / "test-unblinding.json",
            dict(
                status="authorized_reserved_no_requests_yet",
                planned_candidates=["pca-v1", "compact-autoencoder-v2"],
                authorization_file_byte_sha256=reservation[
                    "authorization_file_byte_sha256"
                ],
                source_file_sha256=q.source_map(root),
                candidate_exposure=[],
            ),
        )
    return path, reservation


def accept_stage(root, directory, result, dispatch, reservation, phase):
    resources = result.get("resources", {})
    valid = (
        result.get("status") == "body_complete_awaiting_exit"
        and result.get("phase") == phase
        and result.get("source_file_sha256")
        == q.source_map(root)
        == reservation["source_file_sha256"]
        and result.get("protocol_canonical_JSON_sha256") == q.HASH
        and result.get("grant_file_byte_sha256")
        == p.file_hash(directory.parent / (phase + "-grant.json"))
        and result.get("optimizer_updates") == 0
        and dispatch["parent_confirms_normal_exit"]
        and dispatch["child_reaped"]
        and dispatch["within_deadline"]
        and resources.get("latched_error") is None
        and resources.get("owned_thread_alive") is False
        and 0 < resources.get("peak_rss_bytes", 0) <= 6442450944
        and 0 < resources.get("native_heap_reserved_bytes", 0) <= 536870912
        and result.get("threads_before") == result.get("threads_after")
        and result.get("timings", {}).get("cleanup_seconds", 3) <= 2
    )
    try:
        if phase == "custody":
            valid &= (
                result.get("custody_operations_completed") == 1
                and result.get("population_requests") == 0
                and result.get("exposure", {}).get("exposed") is False
            )
        elif phase in ("PCA", "AE"):
            access = exposure(directory / "test-unblinding.json")
            valid &= (
                access["population_requests"] == 2
                and access["confirmed_events_read"] == 250471
                and access["confirmed_events_scored"] == 250471
                and not access["potential_inflight"]
            )
            doc = p.read(directory / "evaluation.json")
            entry = q.load(root)["candidates"][0 if phase == "PCA" else 1]
            valid &= (
                p.digest(doc["scientific"]) == doc["scientific_sha256"]
                and doc["scientific"]["model_scientific_sha256"]
                == entry["model_scientific_sha256"]
            )
            valid &= (
                doc["scientific"]["metrics"]["background_total"] == 150471
                and doc["scientific"]["metrics"]["signal_total"] == 100000
            )
            journal = p.read(directory / "test-unblinding.json")
            valid &= [
                v["completed_score_batches"] for v in journal["population_access"]
            ] == [37, 25]
        else:
            valid &= (
                (directory.parent / "comparison.json").exists()
                and (directory.parent / "calibrated-operating-points.csv").exists()
                and (directory.parent / "roc-pr.png").exists()
            )
    except (OSError, KeyError, TypeError, ValueError):
        valid = False
    for name, h in result.get("output_file_byte_sha256", {}).items():
        valid &= p.file_hash(directory / name) == h
    end = dispatch.get("exit_observed_monotonic")
    closed = result.get("resource_monitor_closed_monotonic")
    return dict(
        status="parent_accepted" if valid else "parent_rejected",
        phase=phase,
        dispatch=dispatch,
        receipt_file_byte_sha256=p.file_hash(directory / "receipt.json")
        if (directory / "receipt.json").exists()
        else None,
        output_file_byte_sha256=result.get("output_file_byte_sha256", {}),
        source_file_sha256=q.source_map(root),
        software_acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
        resource_accounting="sampled worker accounting through monitor closure; no continuous/full-lifetime certificate",
        unaccounted_terminal_interval_seconds=max(0, end - closed)
        if end is not None and closed is not None
        else None,
    )


def collect_exposure(base):
    rows = [
        dict(candidate=name, **exposure(base / name / "test-unblinding.json"))
        for name in ("PCA", "AE")
    ]
    return dict(
        candidate_exposure=rows,
        population_requests=sum(v["population_requests"] for v in rows),
        confirmed_events_read=sum(v["confirmed_events_read"] for v in rows),
        confirmed_events_scored=sum(v["confirmed_events_scored"] for v in rows),
        potential_inflight=any(v["potential_inflight"] for v in rows),
        exposed=any(v["exposed"] for v in rows),
    )


def run(root=q.ROOT, mode="readiness", *, allow_test=False, approved_plan_sha256=None):
    started = time.monotonic()
    whole_deadline = started + (60 if mode == "readiness" else 600)
    owned = False
    path = root / q.OUTPUT / mode
    outcome = dict(
        task="0026",
        mode=mode,
        status="blocked_before_reservation",
        stages=[],
        optimizer_updates=0,
    )
    try:
        spec, meta, a, consent, plan = prerequisites(
            root, mode, allow_test=allow_test, approved_plan_sha256=approved_plan_sha256
        )

        def created():
            nonlocal owned
            owned = True

        path, reserved = reserve(
            root, mode, spec, a, meta, consent=consent, plan=plan, on_created=created
        )
        outcome.update(
            status="reserved_no_retry",
            source_file_sha256=q.source_map(root),
            hardware=fresh_hardware(),
        )
        env = dict(
            os.environ,
            **spec["runtime"]["thread_environment_before_imports"],
            PYTHONPATH=str(root / "src"),
        )
        previous = {}
        for phase in (
            ("custody",) if mode == "readiness" else ("PCA", "AE", "consolidate")
        ):
            seconds = (
                60 if mode == "readiness" else (30 if phase == "consolidate" else 120)
            )
            parent_check(deadline=whole_deadline)
            # Readiness is one <=60s lifecycle, including orchestration. Final
            # reserves the complete stage cap before dispatching each child.
            stage_seconds = min(seconds, whole_deadline - time.monotonic())
            if stage_seconds < seconds and mode == "final":
                raise TimeoutError("No complete candidate/consolidation slack.")
            if stage_seconds <= 2:
                raise TimeoutError("No operation/cleanup slack.")
            directory = path / phase
            directory.mkdir()
            tick = time.monotonic()
            token = secrets.token_hex(24)
            grant = dict(
                phase=phase,
                token=token,
                parent_pid=os.getpid(),
                started_monotonic=tick,
                stage_seconds=stage_seconds,
                operation_deadline_monotonic=min(tick + stage_seconds, whole_deadline)
                - 2,
                predecessors=previous.copy(),
                reservation_file_byte_sha256=p.file_hash(path / "reservation.json"),
            )
            p.write(path / (phase + "-grant.json"), grant, exclusive=True)
            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "raregate.evaluation.guarded_worker",
                    "--mode",
                    mode,
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                directory / "worker.log",
                root=root,
                environment=env,
                stage_seconds=stage_seconds,
                whole_deadline=whole_deadline,
            )
            result = (
                p.read(directory / "receipt.json")
                if (directory / "receipt.json").exists()
                else dict(status="receipt_missing", phase=phase)
            )
            outcome["last_dispatch"] = dict(dispatch, phase=phase)
            p.write(directory / "dispatch.json", dispatch, exclusive=True)
            accepted = accept_stage(root, directory, result, dispatch, reserved, phase)
            p.write(directory / "parent-acceptance.json", accepted, exclusive=True)
            previous[phase] = p.file_hash(directory / "parent-acceptance.json")
            outcome["stages"].append(dict(phase=phase, worker=result, parent=accepted))
            p.write(path / "workflow.json", outcome)
            if accepted["status"] != "parent_accepted":
                raise RuntimeError("Parent lifecycle/output/guard refusal: " + phase)
        outcome["status"] = "parent_accepted"
    except BaseException as exc:
        outcome.update(
            status="failed_consumed_no_retry"
            if owned
            else "blocked_before_reservation",
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        outcome.update(
            wall_seconds=time.monotonic() - started,
            controller_peak_rss_bytes=rss if sys.platform == "darwin" else rss * 1024,
            reserved_consumed=owned,
            retry_allowed=False,
            finished_utc=p.now(),
        )
        if (
            outcome["wall_seconds"] > (60 if mode == "readiness" else 600)
            or outcome["controller_peak_rss_bytes"] > 134217728
        ):
            outcome.update(
                status="failed_consumed_no_retry"
                if owned
                else "blocked_before_reservation",
                error="Parent resource/deadline exceeded.",
            )
        if mode == "final":
            outcome.update(collect_exposure(path))
            if owned:
                durable(
                    path / "test-unblinding.json",
                    dict(status=outcome["status"], **collect_exposure(path)),
                )
        else:
            outcome.update(population_requests=0, exposed=False)
        if owned:
            p.write(path / "workflow.json", outcome)
            p.write(
                path / "parent-acceptance.json",
                dict(
                    status=outcome["status"],
                    source_file_sha256=q.source_map(root),
                    software_acceptance_file_byte_sha256=p.file_hash(
                        root / q.ACCEPTANCE
                    ),
                    workflow_file_byte_sha256=p.file_hash(path / "workflow.json"),
                ),
                exclusive=True,
            )
    print(mode, outcome["status"], outcome.get("error", ""))
    return 0 if outcome["status"] == "parent_accepted" else 1


def prepare_plan(root=q.ROOT):
    q.metadata(root, q.load(root))
    q.acceptance(root)
    ready = p.read(root / q.OUTPUT / "readiness/parent-acceptance.json")
    if ready["status"] != "parent_accepted" or ready[
        "source_file_sha256"
    ] != q.source_map(root):
        raise ValueError(
            "Current successful readiness required before final authorization question."
        )
    plan = q.plan(root)
    if (root / q.PLAN).exists():
        if p.read(root / q.PLAN) != plan:
            raise ValueError("Existing changed plan requires new review.")
    else:
        p.write(root / q.PLAN, plan, exclusive=True)
    print(
        "Ready; human authorization pending. Approved-plan canonical SHA256:",
        p.digest(plan),
    )
    print("Command after actual human consent and bound audit record:")
    print(
        ".venv/bin/python -m raregate.evaluation.guarded --run-final --allow-test --plan-sha256 "
        + p.digest(plan)
    )
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check-readiness", action="store_true")
    actions.add_argument("--prepare-plan", action="store_true")
    actions.add_argument("--run-final", action="store_true")
    parser.add_argument("--allow-test", action="store_true")
    parser.add_argument("--plan-sha256")
    args = parser.parse_args()
    if not args.run_final and (args.allow_test or args.plan_sha256):
        parser.error("Test opt-in/plan are only valid on the final authorized action.")
    if args.prepare_plan:
        prepare_plan()
        return 0
    return run(
        mode="final" if args.run_final else "readiness",
        allow_test=args.allow_test,
        approved_plan_sha256=args.plan_sha256,
    )


if __name__ == "__main__":
    raise SystemExit(main())
