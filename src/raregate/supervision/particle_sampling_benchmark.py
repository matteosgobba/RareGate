"""Fixed three-repetition v3/v4/compute synthetic matrix; no real slot here."""

import argparse
import hashlib
import json
import statistics
import sys
import time

from raregate.supervision import particle_launcher as io
from raregate.supervision.particle_monitor_benchmark import (
    physical_batches,
    summary,
)
from raregate.supervision.particle_sampling import SystemQuery

OUTPUT = "data/task0015-sampling-benchmark"
ACCEPTANCE = "data/task0015-final-synthetic-acceptance.json"
ORDER = [(rep, arm) for rep in (1, 2, 3) for arm in ("v3", "v4", "compute")]
SPEC = {
    "schema_version": 1,
    "scope": "synthetic_paired_three_repetitions_no_real_acceptance",
    "order": [[rep, arm] for rep, arm in ORDER],
    "total_seconds": 120,
    "arm_seconds_including_imports": 30,
    "seed": 1729,
    "cpu_threads": [1, 1],
    "batch_size": 32,
    "nmax": 384,
    "physical_batches": 2,
    "synthetic_steps": 16,
    "scoring_batches": 8,
    "host_cadence_seconds": 0.05,
    "age_upper_seconds": 0.1,
    "guard_fixture": "explicit_9GiB_host_400MiB_RSS_200MiB_native_not_readiness",
    "material_gate": "all_repetitions_pass_exact_parity_and_median_v4_le_median_v3_div3",
}


def acceptance():
    a = io.read(io.ROOT / ACCEPTANCE)
    if (
        a["pytest_exit_code"] != 0
        or type(a.get("pytest_passed")) is not int
        or a["pytest_passed"] <= 0
        or a.get("pytest_cases") != a["pytest_passed"]
        or a["config_sha256"] != io.CONFIG_HASH
        or a["source_sha256"] != io.source_hashes()
        or a.get("workspace_measurement", {}).get("parameter_count") != 478
        or a["workspace_measurement"].get("synthetic_optimizer_steps") != 2
        or type(a["workspace_measurement"].get("peak_tensor_bytes")) is not int
        or not 0 < a["workspace_measurement"]["peak_tensor_bytes"] <= 512 * 2**20
    ):
        raise ValueError("Current source-bound acceptance required.")
    return a


class SyntheticHostQuery(SystemQuery):
    """Costs real system queries; publishes explicit synthetic host guard values."""

    def __init__(self):
        super().__init__()
        self.actual = []

    def finish(self):
        row = super().finish()
        if row is None:
            return None
        self.actual.append(row)
        from raregate.supervision.particle_monitor_benchmark import fixture

        f = fixture()
        return {
            **row,
            **{
                k: f[k]
                for k in (
                    "page_size_bytes",
                    "free_pages",
                    "inactive_pages",
                    "available_bytes",
                )
            },
            "raw": f["vm_stat_raw"],
            "synthetic": True,
        }


def worker(rep, arm, directory):
    entered = time.monotonic()
    entered_cpu = time.process_time()
    from contextlib import nullcontext

    import numpy as np
    import torch

    from raregate.data.features import Parameters, model_view
    from raregate.models.particle_memory_study import StudyAudit
    from raregate.models.particle_set import ParticleSetAutoencoder, event_loss
    from raregate.supervision.particle_bounded_worker import additional_audit
    from raregate.supervision.particle_collector import (
        CachedSystemCollector,
        DarwinBindings,
    )
    from raregate.supervision.particle_monitor_benchmark import fixture
    from raregate.training.autoencoder import deterministic_cpu
    from raregate.training.particle_monitor_v3 import MonitorV3
    from raregate.training.particle_monitor_v4 import MonitorV4, optimizer_observer
    from raregate.training.particle_set import adam

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    acceptance()
    config = io.read(io.ROOT / io.CONFIG)
    profile = io.read(io.ROOT / io.PROFILE)
    setup = time.monotonic() - entered
    setup_cpu = time.process_time() - entered_cpu
    monitor_started = time.monotonic()
    actual_process = []
    probe_wall = []
    collector = CachedSystemCollector() if arm == "v3" else None
    host_query = SyntheticHostQuery() if arm == "v4" else None
    bindings = DarwinBindings() if arm == "v4" else None

    def native_fixture():
        t = time.monotonic()
        actual = bindings.process_sample()
        probe_wall.append(time.monotonic() - t)
        actual_process.append(actual)
        f = fixture()
        return {
            k: f[k]
            for k in (
                "native_heap_reserved_bytes",
                "native_heap_in_use_bytes",
                "workspace_method",
                "peak_rss_bytes",
                "pressure_dispatch_flags",
            )
        }

    def v3_fixture():
        t = time.monotonic()
        actual = collector()
        probe_wall.append(time.monotonic() - t)
        actual_process.append(actual)
        return fixture()

    monitor = None
    if arm == "v3":
        monitor = MonitorV3(
            config,
            profile,
            io.read(io.ROOT / "configs/resources/particle_resource_monitor_v3.json"),
            probe=v3_fixture,
            journal=directory / "guards.jsonl",
            synthetic_fixture=True,
        )
    if arm == "v4":
        monitor = MonitorV4(
            config,
            profile,
            io.read(io.ROOT / "configs/resources/particle_resource_monitor_v4.json"),
            process_probe=native_fixture,
            collector=host_query,
            directory=directory,
            synthetic_fixture=True,
        )

    audit_base = type(additional_audit(StudyAudit, directory / "synthetic-audit.json"))

    class TimedAudit(audit_base):
        def __init__(self, path):
            self.save_seconds = 0.0
            self.save_calls = 0
            super().__init__(path)

        def save(self):
            t = time.monotonic()
            try:
                super().save()
            finally:
                self.save_seconds += time.monotonic() - t
                self.save_calls += 1

    audit = TimedAudit(directory / "synthetic-audit.json") if arm != "compute" else None
    if audit:
        audit.bind_sample(np.arange(1024, dtype=np.int64))
        audit.save()
    physical = physical_batches()
    params = Parameters.from_config(io.read(io.ROOT / "configs/data/lhco_rnd_v5.json"))
    batch_times = []
    view_times = []
    scores = []
    progress_io_seconds = 0.0
    wall, cpu = time.monotonic(), time.process_time()
    with monitor if monitor else nullcontext(), deterministic_cpu(1729, 1):
        model = ParticleSetAutoencoder()
        opt = adam(model, config)
        if audit:
            if arm == "v4":
                optimizer_observer(audit, monitor)(opt)
            else:
                audit.observe_optimizer(opt)
        init_done = time.monotonic()
        init_cpu = time.process_time() - cpu
        for i in range(24):
            t = time.monotonic()
            if audit and i % 2 == 0:
                request = audit.request(
                    "train_background", "synthetic_only_fake_ids", True, 64
                )
            if monitor:
                monitor.check()
            vt = time.monotonic()
            v = model_view(*physical[i % 2], params)
            view_times.append(time.monotonic() - vt)
            x, mask = torch.from_numpy(v.features), torch.from_numpy(v.mask)
            if audit:
                audit.advance(request, 32)
                audit.observe_ids(
                    np.arange((i % 2) * 32, (i % 2 + 1) * 32, dtype=np.int64)
                )
            if i < 16:
                opt.zero_grad(set_to_none=True)
                values = event_loss(x, model(x, mask), mask)
                loss = values.mean()
                loss.backward()
                opt.step()
                model.validate_parameters()
            else:
                scores.append(model.score(x, mask))
            if audit and i % 2 == 1:
                request["status"] = "completed"
                audit.save()
            if monitor:
                monitor.check()
            batch_times.append(time.monotonic() - t)
            progress_tick = time.monotonic()
            io.atomic(
                directory / "progress.json",
                {
                    "synthetic_steps_completed": min(i + 1, 16),
                    "batches_completed": i + 1,
                    "real_steps": 0,
                },
            )
            progress_io_seconds += time.monotonic() - progress_tick

        def hash_tensors(values):
            h = hashlib.sha256()
            for v in values:
                h.update(v.detach().cpu().numpy().tobytes())
            return h.hexdigest()

        numeric = {
            "parameters": hash_tensors(model.parameters()),
            "adam": hash_tensors(
                v
                for state in opt.state.values()
                for v in state.values()
                if isinstance(v, torch.Tensor)
            ),
            "reconstruction": hash_tensors([model(x, mask)]),
            "scores": hashlib.sha256(
                np.concatenate(scores).astype("<f8").tobytes()
            ).hexdigest(),
            "final_objective": loss.item(),
        }
    duration = time.monotonic() - wall
    cpuduration = time.process_time() - cpu
    return {
        "rep": rep,
        "arm": arm,
        "status": "completed",
        "scope": "synthetic_fixture_not_readiness",
        "runtime_import_setup_seconds": setup,
        "runtime_import_setup_process_cpu_seconds": setup_cpu,
        "monitor_bindings_audit_fixture_setup_seconds": wall - monitor_started,
        "initialization_enter_monitor_seconds": init_done - wall,
        "initialization_enter_monitor_process_cpu_seconds": init_cpu,
        "workload_wall_seconds": duration,
        "workload_process_cpu_seconds": cpuduration,
        "batch_wall_seconds": summary(batch_times),
        "view_wall_seconds": summary(view_times),
        "audit_save_seconds": audit.save_seconds if audit else 0,
        "audit_save_calls": audit.save_calls if audit else 0,
        "progress_file_io_seconds": progress_io_seconds,
        "probe_wall_seconds": summary(probe_wall),
        "numerical_identity": numeric,
        "resources": monitor.report() if monitor else None,
        "actual_host_snapshots_not_readiness": host_query.actual
        if host_query
        else None,
        "actual_process_observations_not_guard_fixture": actual_process,
        "new_real_events_steps": 0,
        "new_real_slot": False,
    }


def evaluate(rows):
    if (
        len(rows) != 9
        or [(r["rep"], r["arm"]) for r in rows] != ORDER
        or any(r.get("status") != "completed" for r in rows)
    ):
        return {
            "material_improvement_pass": False,
            "reason": "Incomplete/failed prescribed matrix.",
        }
    parity = all(r["numerical_identity"] == rows[0]["numerical_identity"] for r in rows)
    med = {
        arm: statistics.median(
            r["workload_wall_seconds"] for r in rows if r["arm"] == arm
        )
        for arm in ("v3", "v4", "compute")
    }
    complete_ages = all(
        r["resources"]["host_age_statistics"]["max_seconds"] <= 0.1
        and r["resources"]["sampler"]["latched_failure"] is None
        and not r["resources"]["sampler"]["owned_thread_alive"]
        for r in rows
        if r["arm"] == "v4"
    )
    return {
        "material_improvement_pass": parity
        and complete_ages
        and med["v4"] <= med["v3"] / 3,
        "exact_numerical_parity": parity,
        "all_v4_age_and_failure_checks_pass": complete_ages,
        "median_workload_seconds": med,
        "v3_over_v4_median_ratio": med["v3"] / med["v4"],
        "real180s_gate_established": False,
    }


def matrix():
    io.assert_lightweight()
    acceptance()
    started = time.monotonic()
    directory = io.ROOT / OUTPUT
    directory.mkdir(exist_ok=False)
    io.exclusive(directory / "preregistration.json", SPEC)
    state = {
        "status": "started",
        "scope": "fixed_synthetic_matrix_only",
        "rows": [],
        "source_sha256": io.source_hashes(),
        "acceptance_sha256": io.file_hash(io.ROOT / ACCEPTANCE),
    }
    try:
        for rep, arm in ORDER:
            t = time.monotonic()
            seconds = min(30, 120 - (t - started))
            if seconds <= 0:
                raise TimeoutError("Overall120-second matrix ceiling.")
            sub = directory / f"{rep}-{arm}"
            sub.mkdir()
            io.exclusive(
                sub / "reservation.json",
                {"started_monotonic": t, "deadline_monotonic": t + seconds},
            )
            receipt = io.dispatch(
                [
                    sys.executable,
                    "-m",
                    "raregate.supervision.particle_sampling_benchmark",
                    "--arm",
                    arm,
                    "--rep",
                    str(rep),
                ],
                sub / "worker.log",
                seconds,
                started=t,
            )
            row = (
                io.read(sub / "result.json")
                if (sub / "result.json").exists()
                else {
                    "rep": rep,
                    "arm": arm,
                    "status": "failed",
                    "error": "Missing final worker receipt",
                }
            )
            row["parent_dispatch"] = receipt
            state["rows"].append(row)
            io.atomic(directory / "matrix.json", state)
            if receipt["returncode"] or row["status"] != "completed":
                raise RuntimeError("Matrix arm failed; no real authorization.")
        state["status"] = "completed"
    except BaseException as exc:
        state.update(status="failed", error=str(exc))
    state["decision"] = evaluate(state["rows"])
    state["elapsed_seconds"] = time.monotonic() - started
    io.atomic(directory / "matrix.json", state)
    return state


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--matrix", action="store_true")
    g.add_argument("--arm", choices=["v3", "v4", "compute"])
    p.add_argument("--rep", type=int, choices=[1, 2, 3])
    args = p.parse_args()
    if args.matrix:
        result = matrix()
        print(json.dumps({"status": result["status"], "decision": result["decision"]}))
        if result["status"] != "completed":
            raise SystemExit(1)
        return
    import signal

    directory = io.ROOT / OUTPUT / f"{args.rep}-{args.arm}"
    res = io.read(directory / "reservation.json")

    def alarm(*_):
        raise TimeoutError("Import-inclusive30-second arm deadline.")

    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(
        signal.ITIMER_REAL, max(0.001, res["deadline_monotonic"] - time.monotonic())
    )
    row = {"rep": args.rep, "arm": args.arm, "status": "failed"}
    try:
        row = worker(args.rep, args.arm, directory)
    except BaseException as exc:
        row.update(status="failed", error=str(exc), partial_progress_preserved=True)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        row["elapsed_seconds_including_imports"] = (
            time.monotonic() - res["started_monotonic"]
        )
        io.atomic(directory / "result.json", row)
    raise SystemExit(0 if row["status"] == "completed" else 1)


if __name__ == "__main__":
    main()
