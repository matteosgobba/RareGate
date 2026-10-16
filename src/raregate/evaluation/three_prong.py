"""Stdlib-only guarded extension controller; Phase A never reserves real work."""

import argparse
import os
import secrets
import sys
import time

from raregate.benchmarks import protocol as p
from raregate.evaluation import three_prong_protocol as q
from raregate.evaluation.guard import parent_check
from raregate.evaluation.guarded import supervise
from raregate.evaluation.guarded_audit import durable
from raregate.evaluation.three_prong_audit import exposure


def namespace(root):
    base = q.fixed(root, q.OUTPUT)
    q.require(
        not base.exists() and not q.fixed(root, q.RAW).exists(),
        "Distinct real namespace reserved/partial/consumed; no retry/reset/resume",
    )
    return base


def prepare_plan(root=q.ROOT):
    parent_check()
    namespace(root)
    plan = q.plan(root)
    if (root / q.PLAN).exists():
        q.require(p.read(root / q.PLAN) == plan, "Existing changed reviewable plan")
    else:
        p.write(root / q.PLAN, plan, exclusive=True)
    print(
        "Phase A metadata ready; payload custody and human authorization pending. Plan SHA256:",
        p.digest(plan),
    )
    print(
        ".venv/bin/python -m raregate.evaluation.three_prong --run-final --allow-test --plan-sha256 "
        + p.digest(plan)
    )
    return plan


def reserve(root, plan, on_created=lambda: None):
    base = namespace(root)
    base.mkdir(parents=True, exist_ok=False)
    on_created()
    reservation = dict(
        task="0028",
        status="reserved_no_retry",
        parent_pid=os.getpid(),
        protocol_canonical_JSON_sha256=q.HASH,
        source_file_sha256=q.source_map(root),
        software_acceptance_file_byte_sha256=p.file_hash(root / q.ACCEPTANCE),
        authorization_file_byte_sha256=p.file_hash(root / q.CONSENT),
        plan_sha256=p.digest(plan),
        reserved_utc=p.now(),
        code=p.code_context(root),
    )
    p.write(base / "reservation.json", reservation, exclusive=True)
    for origin, destination in (
        (q.CONFIG, "protocol.json"),
        (q.ACCEPTANCE, "acceptance.json"),
        (q.CONSENT, "authorization.json"),
    ):
        with (base / destination).open("xb") as stream:
            stream.write((root / origin).read_bytes())
    return base, reservation


def accept_stage(root, phase, result, dispatch, reservation):
    """Successful body is insufficient; accept full lifecycle, outputs and gates."""
    valid = False
    try:
        resources = result["resources"]
        valid = (
            result["status"] == "body_complete_awaiting_exit"
            and result["phase"] == phase
            and result["source_file_sha256"]
            == reservation["source_file_sha256"]
            == q.source_map(root)
            and result["protocol_canonical_JSON_sha256"] == q.HASH
            and result["grant_file_byte_sha256"]
            == p.file_hash(root / q.OUTPUT / (phase + "-grant.json"))
            and result["optimizer_updates"]
            == result["new_original_background_forward_calls"]
            == 0
            and dispatch["parent_confirms_normal_exit"]
            and dispatch.get("returncode") == 0
            and dispatch.get("parent_error") is None
            and dispatch["child_reaped"]
            and dispatch["within_deadline"]
            and resources["latched_error"] is None
            and resources["owned_thread_alive"] is False
            and 0 < resources["peak_rss_bytes"] <= 6 * 2**30
            and 0 < resources["native_heap_reserved_bytes"] <= 512 * 2**20
            and result["threads_before"] == result["threads_after"]
            and result["timings"]["cleanup_seconds"] <= 2
            and not result["exposure"]["potential_inflight"]
        )
        required = {str(q.OUTPUT + "/" + phase + "/access.json")}
        if phase == "acquire":
            required.add(q.OUTPUT + "/acquire/acquisition.json")
            acquired = p.read(root / q.OUTPUT / "acquire/acquisition.json")
            spec = q.load(root)
            valid &= (
                acquired["integrity"]["file_size"] == spec["source"]["expected_size"]
                and acquired["integrity"]["verified_checksum"]
                == spec["source"]["expected_checksum"]
                and len(acquired["integrity"]["sha256"]) == 64
            )
        elif phase == "prepare":
            required.update(
                (q.PREPARED + "/manifest.json", q.OUTPUT + "/prepare/overlap.json")
            )
            manifest = p.read(root / q.PREPARED / "manifest.json")
            q.compatibility(manifest, q.load(root))
            records = result["exposure"]["records"]
            valid &= (
                any(
                    r["kind"] == "raw_custody" and r["confirmed_read"] == 100000
                    for r in records
                )
                and any(
                    r["kind"] == "original_fingerprint_integrity"
                    and r["confirmed_read"] == 1100000
                    for r in records
                )
                and any(
                    r["kind"] == "signal_preparation" and r["confirmed_read"] == 100000
                    for r in records
                )
                and not result["exposure"]["new_signal_model_accessed"]
            )
        elif phase in ("PCA", "AE"):
            required.update(
                q.OUTPUT + "/" + phase + "/" + f
                for f in (
                    "evaluation.json",
                    "background-summary.json",
                    "three-prong-scores.npy",
                )
            )
            e = p.read(root / q.OUTPUT / phase / "evaluation.json")
            entry = q.load(root)["candidates"][0 if phase == "PCA" else 1]
            valid &= (
                p.digest(e["scientific"]) == e["scientific_sha256"]
                and e["scientific"]["model_scientific_sha256"]
                == entry["model_scientific_sha256"]
                and e["scientific"]["metrics"]["signal_total"] == 100000
                and e["scientific"]["metrics"]["background_total"] == 150471
                and result["exposure"]["signal_scored_presentations"] == 100000
                and result["exposure"]["signal_batches"] == 25
                and result["exposure"]["cached_numeric_loads"] == 1
            )
            record = next(
                r
                for r in result["exposure"]["records"]
                if r["kind"] == "signal_model_evaluation"
            )
            valid &= record["batches"] == [4096] * 24 + [1696]
        else:
            required.update(
                (
                    q.OUTPUT + "/comparison.json",
                    q.OUTPUT + "/calibrated-operating-points.csv",
                )
            )
        valid &= set(result["output_file_byte_sha256"]) == required
        for path, h in result["output_file_byte_sha256"].items():
            valid &= p.file_hash(q.fixed(root, path)) == h
    except (OSError, ValueError, KeyError, TypeError, StopIteration):
        valid = False
    end, closed = (
        dispatch.get("exit_observed_monotonic"),
        result.get("resource_monitor_closed_monotonic"),
    )
    return dict(
        status="parent_accepted" if valid else "parent_rejected",
        phase=phase,
        dispatch=dispatch,
        receipt_file_byte_sha256=p.file_hash(root / q.OUTPUT / phase / "receipt.json")
        if (root / q.OUTPUT / phase / "receipt.json").exists()
        else None,
        output_file_byte_sha256=result.get("output_file_byte_sha256", {}),
        terminal_unaccounted_seconds=max(0, end - closed)
        if end is not None and closed is not None
        else None,
        resource_scope="observed lifetime peaks through guard closure;RSS/native overlap;terminal gap disclosed;not hard real time",
    )


def collect(base):
    rows = [
        dict(phase=phase, **exposure(base / phase / "access.json"))
        for phase in q.PHASES
    ]
    return dict(
        original_background_model_accessed=True,
        original_signal_model_accessed=True,
        new_three_prong_model_accessed=any(
            r["new_signal_model_accessed"] for r in rows
        ),
        cached_numeric_loads=sum(r["cached_numeric_loads"] for r in rows),
        signal_scored_presentations=sum(r["signal_scored_presentations"] for r in rows),
        signal_batches=sum(r["signal_batches"] for r in rows),
        potential_inflight=any(r["potential_inflight"] for r in rows),
        phase_access=rows,
        new_original_background_forward_calls=0,
    )


def run(root=q.ROOT, *, allow_test=False, plan_sha256=None):
    started = time.monotonic()
    deadline = started + 900
    owned = False
    base = root / q.OUTPUT
    outcome = dict(
        task="0028", status="blocked_before_reservation", stages=[], optimizer_updates=0
    )
    try:
        parent_check()
        q.require(
            sys.platform == "darwin",
            "Supported Darwin primary process accounting required",
        )
        plan, _ = q.authorization(root, allow_test, plan_sha256)

        def created():
            nonlocal owned
            owned = True

        base, reservation = reserve(root, plan, on_created=created)
        spec = q.load(root)
        env = dict(
            os.environ,
            **spec["runtime"]["thread_environment_before_imports"],
            PYTHONPATH=str(root / "src"),
        )
        previous = {}
        for phase in q.PHASES:
            seconds = spec["limits"][phase + "_seconds"]
            parent_check(deadline=deadline)
            q.require(
                time.monotonic() + seconds <= deadline,
                "No complete stage plus cleanup slack",
            )
            directory = base / phase
            directory.mkdir()
            token = secrets.token_hex(24)
            tick = time.monotonic()
            grant = dict(
                phase=phase,
                token=token,
                parent_pid=os.getpid(),
                started_monotonic=tick,
                operation_deadline_monotonic=min(tick + seconds, deadline) - 2,
                predecessors=previous.copy(),
                reservation_file_byte_sha256=p.file_hash(base / "reservation.json"),
            )
            p.write(base / (phase + "-grant.json"), grant, exclusive=True)
            dispatch = supervise(
                [
                    sys.executable,
                    "-m",
                    "raregate.evaluation.three_prong_worker",
                    "--phase",
                    phase,
                    "--token",
                    token,
                ],
                directory / "worker.log",
                root=root,
                environment=env,
                stage_seconds=seconds,
                whole_deadline=deadline,
            )
            result = (
                p.read(directory / "receipt.json")
                if (directory / "receipt.json").exists()
                else dict(status="receipt_missing")
            )
            accepted = accept_stage(root, phase, result, dispatch, reservation)
            p.write(directory / "dispatch.json", dispatch, exclusive=True)
            p.write(directory / "parent-acceptance.json", accepted, exclusive=True)
            previous[phase] = p.file_hash(directory / "parent-acceptance.json")
            outcome["stages"].append(dict(phase=phase, parent=accepted, worker=result))
            durable(base / "exposure.json", collect(base))
            p.write(base / "workflow.json", outcome)
            q.require(
                accepted["status"] == "parent_accepted",
                "Failed/incomplete stage; stop: " + phase,
            )
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

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
            1 if sys.platform == "darwin" else 1024
        )
        outcome.update(
            wall_seconds=time.monotonic() - started,
            controller_peak_RSS_bytes=rss,
            reserved_consumed=owned,
            retry_allowed=False,
            **collect(base),
        )
        if outcome["wall_seconds"] > 900 or rss > 128 * 2**20:
            outcome["status"] = (
                "failed_consumed_no_retry" if owned else "blocked_before_reservation"
            )
        if owned:
            durable(base / "exposure.json", collect(base))
            p.write(base / "workflow.json", outcome)
            p.write(
                base / "parent-acceptance.json",
                dict(
                    status=outcome["status"],
                    workflow_file_byte_sha256=p.file_hash(base / "workflow.json"),
                    source_file_sha256=q.source_map(root),
                ),
                exclusive=True,
            )
    print(outcome["status"], outcome.get("error", ""))
    return 0 if outcome["status"] == "parent_accepted" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare-plan", action="store_true")
    action.add_argument("--run-final", action="store_true")
    parser.add_argument("--allow-test", action="store_true")
    parser.add_argument("--plan-sha256")
    args = parser.parse_args()
    if args.prepare_plan:
        if args.allow_test or args.plan_sha256:
            parser.error("Opt-in/plan only on explicit authorized Phase B")
        prepare_plan()
        return 0
    return run(allow_test=args.allow_test, plan_sha256=args.plan_sha256)


if __name__ == "__main__":
    raise SystemExit(main())
