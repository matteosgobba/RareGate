"""Fixed Task0014 synthetic matrix; never a real reader/run authorization."""

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from raregate.supervision import particle_launcher as io

OUTPUT = "data/task0014-monitor-benchmark"
ACCEPTANCE = "data/task0014-synthetic-acceptance.json"
ARMS = (
    "collectors",
    "checks_old",
    "checks_v3",
    "workload_compute",
    "workload_old",
    "workload_v3",
)
SPEC = {
    "version": 1,
    "scope": "synthetic_engineering_only_shared_host",
    "order": list(ARMS),
    "overall_deadline_seconds": 120,
    "arm_deadline_seconds": 30,
    "seed": 1729,
    "cpu_intra_inter_threads": [1, 1],
    "batch_size": 32,
    "nmax": 384,
    "resident_physical_batches": 2,
    "isolated_samples_per_collector": 16,
    "complete_checks_per_instrumentation_arm": 32,
    "synthetic_training_steps_per_workload": 16,
    "synthetic_scoring_batches_per_workload": 8,
    "synthetic_guard_fixture_available_bytes": 9663676416,
    "fixture_is_not_host_readiness": True,
    "real_events_steps_authorized": 0,
    "timers": "wall/process_CPU/nested_probe/lock/serialize_IO/audit/view/watcher; overlap_not_additive",
}


def verified_acceptance():
    a = io.read(io.ROOT / ACCEPTANCE)
    if (
        a["pytest_exit_code"] != 0
        or a["config_sha256"] != io.CONFIG_HASH
        or a["source_sha256"] != io.source_hashes()
    ):
        raise ValueError("Fresh current synthetic acceptance required.")
    return a


def summary(values):
    return {
        "count": len(values),
        "values": values,
        "total": sum(values),
        "mean": sum(values) / len(values) if values else None,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def fixture(clock=time.monotonic):
    from raregate.supervision.particle_host import parse_vm_stat

    tick = clock()
    return {
        **parse_vm_stat(
            "page size of 16384 bytes\nPages free: 589824.\nPages inactive: 0.\n"
        ),
        "available_method": "Darwin_free_plus_inactive_pages",
        "workspace_method": "all_malloc_zone_reserved_bytes_conservative_upper_bound",
        "peak_rss_bytes": 400 * 2**20,
        "native_heap_reserved_bytes": 200 * 2**20,
        "native_heap_in_use_bytes": 150 * 2**20,
        "pressure_dispatch_flags": None,
        "collector_backend": "system_vm_stat_oneshot_cached_bindings_v3",
        "sample_started_monotonic": tick,
        "sample_finished_monotonic": tick,
        "primary_values_reused": False,
        "diagnostic_guard_fixture": True,
    }


def physical_batches():
    import numpy as np

    rng = np.random.default_rng(1729)
    result = []
    for index in range(2):
        counts = (
            np.full(32, 384)
            if index == 0
            else np.resize(np.array([1, 48, 96, 192, 384]), 32)
        )
        offsets = np.r_[0, np.cumsum(counts)].astype(np.int64)
        particles = []
        for n in counts:
            particles.append(
                np.column_stack(
                    (
                        np.sort(rng.uniform(0.1, 30, n))[::-1],
                        rng.uniform(-2, 2, n),
                        rng.uniform(-np.pi, np.pi, n),
                    )
                ).astype(np.float32)
            )
        result.append((np.concatenate(particles), offsets))
    return result


def sdk_receipt(directory):
    # The compiler input is stamped in this accepted source; generated temp binary
    # only reports SDK ABI constants, never accesses a host/data population.
    code = """#include <stdio.h>
#include <stddef.h>
#include <mach/host_info.h>
#include <mach/task_info.h>
#include <malloc/malloc.h>
int main(void){printf("%u %zu %zu %zu %zu\\n",HOST_VM_INFO64_REV1_COUNT,
 offsetof(vm_statistics64_data_t,swapped_count),offsetof(vm_statistics64_data_t,speculative_count),
 sizeof(mach_task_basic_info_data_t),sizeof(malloc_statistics_t));return 0;}
"""
    try:
        with tempfile.TemporaryDirectory(prefix="raregate-abi-") as temp:
            binary = Path(temp) / "abi"
            r = subprocess.run(
                ["/usr/bin/xcrun", "clang", "-x", "c", "-", "-o", str(binary)],
                input=code,
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
            if r.returncode:
                return {"status": "unavailable", "error": r.stderr[-2000:]}
            row = subprocess.check_output([str(binary)], text=True, timeout=2).strip()
            if row != "38 152 92 48 32":
                raise ValueError("Installed SDK ABI differs from reviewed bindings.")
            return {
                "status": "verified",
                "rev1_count_size_spec_offset_task_malloc": row,
            }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "error": str(exc)}


def arm(name, directory):
    entered = time.monotonic()
    import numpy as np
    import torch

    from raregate.data.features import Parameters, model_view
    from raregate.models.particle_memory_study import StudyAudit
    from raregate.models.particle_set import ParticleSetAutoencoder, event_loss
    from raregate.supervision.particle_collector import (
        CachedSystemCollector,
        MachDiagnosticCollector,
    )
    from raregate.training.autoencoder import deterministic_cpu
    from raregate.training.particle_monitor_v3 import MonitorV3, definition
    from raregate.training.particle_resources import PolicyMonitor, policy_snapshot
    from raregate.training.particle_set import adam

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True, warn_only=False)
    verified_acceptance()
    config, profile = io.read(io.ROOT / io.CONFIG), io.read(io.ROOT / io.PROFILE)
    manifest = io.read(io.ROOT / "configs/resources/particle_resource_monitor_v3.json")
    if manifest != definition():
        raise ValueError("Implementation manifest changed.")
    setup = time.monotonic() - entered
    result = {
        "arm": name,
        "scope": "synthetic_diagnostic_not_resource_acceptance",
        "runtime_import_setup_wall_seconds": setup,
        "real_events_steps": 0,
        "guard_accounting": "explicit_synthetic_fixture_not_host_readiness",
        "timers_overlap_not_additive": True,
    }
    if name == "collectors":
        result["sdk_abi"] = sdk_receipt(directory)
        result["platform"] = {
            "macOS": __import__("platform").mac_ver()[0],
            "kernel_release": os.uname().release,
            "kernel_version": os.uname().version,
            "machine": os.uname().machine,
        }
        try:
            sig = subprocess.run(
                ["/usr/bin/codesign", "-d", "-vvv", "/usr/bin/vm_stat"],
                text=True,
                capture_output=True,
                timeout=2,
                check=False,
            )
            result["system_vm_stat_signature"] = {
                "exit_code": sig.returncode,
                "text": sig.stderr[-4000:],
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            result["system_vm_stat_signature"] = {"error": str(exc)}
        result["collectors"] = {}
        direct = None
        try:
            for label in ("old", "cached_system", "direct_mach_diagnostic"):
                if label == "old":
                    probe = policy_snapshot
                elif label == "cached_system":
                    probe = CachedSystemCollector()
                else:
                    direct = MachDiagnosticCollector()
                    probe = direct
                rows = []
                wall = []
                cpu = []
                for _ in range(16):
                    tick, ct = time.monotonic(), time.process_time()
                    sample = probe()
                    wall.append(time.monotonic() - tick)
                    cpu.append(time.process_time() - ct)
                    rows.append(sample)
                result["collectors"][label] = {
                    "wall_seconds": summary(wall),
                    "process_cpu_seconds": summary(cpu),
                    "snapshots": rows,
                }
                io.atomic(directory / "progress.json", result)
        finally:
            if direct:
                direct.close()
        result["status"] = "completed"
        return result

    compute_only = name == "workload_compute"
    v3 = name.endswith("v3")
    observed = []
    probe_cpu = []
    probe_wall = []
    collect = CachedSystemCollector() if v3 else policy_snapshot

    def diagnostic_probe():
        tick, ct = time.monotonic(), time.process_time()
        actual = collect()
        probe_wall.append(time.monotonic() - tick)
        probe_cpu.append(time.process_time() - ct)
        observed.append(
            {
                k: actual.get(k)
                for k in (
                    "available_bytes",
                    "free_pages",
                    "inactive_pages",
                    "page_size_bytes",
                    "native_heap_reserved_bytes",
                    "peak_rss_bytes",
                    "pressure_dispatch_flags",
                )
            }
        )
        # Only synthetic work runs. Observed host values are retained separately;
        # guard fixtures never purport to authorize a real production stage.
        return fixture()

    monitor = None
    if not compute_only:
        monitor = (
            MonitorV3(
                config,
                profile,
                manifest,
                probe=diagnostic_probe,
                journal=directory / "journal.jsonl",
                synthetic_fixture=True,
            )
            if v3
            else PolicyMonitor(
                config,
                profile,
                probe=diagnostic_probe,
                journal=directory / "journal.jsonl",
            )
        )

    class TimedAudit(StudyAudit):
        def __init__(self, path):
            self.save_seconds = 0.0
            self.save_calls = 0
            super().__init__(path)

        def save(self):
            tick = time.monotonic()
            try:
                super().save()
            finally:
                self.save_seconds += time.monotonic() - tick
                self.save_calls += 1

    audit = (
        TimedAudit(directory / "synthetic-access-audit.json")
        if not compute_only
        else None
    )
    if audit:
        audit.bind_sample(np.arange(1024, dtype=np.int64))
        audit.save()
    wall, ct = time.monotonic(), time.process_time()
    steps = []
    scores = []
    views = []
    from contextlib import nullcontext

    with monitor if monitor else nullcontext(), deterministic_cpu(1729, 1):
        model = ParticleSetAutoencoder()
        optimizer = adam(model, config)
        if audit:
            audit.observe_optimizer(optimizer)
        if name.startswith("checks"):
            for _i in range(32):
                monitor.check()
                audit.observe_ids(np.arange(32, dtype=np.int64))
        else:
            physical = physical_batches()
            params = Parameters.from_config(
                io.read(io.ROOT / "configs/data/lhco_rnd_v5.json")
            )
            request = None
            for i in range(24):
                if audit and i % 2 == 0:
                    request = audit.request(
                        "train_background", "synthetic_only_fake_ids", True, 64
                    )
                tick = time.monotonic()
                if monitor:
                    monitor.check()
                viewtick = time.monotonic()
                view = model_view(*physical[i % 2], params)
                views.append(time.monotonic() - viewtick)
                x, mask = torch.from_numpy(view.features), torch.from_numpy(view.mask)
                if audit:
                    audit.advance(request, 32)
                    audit.observe_ids(
                        np.arange((i % 2) * 32, (i % 2 + 1) * 32, dtype=np.int64)
                    )
                if i < 16:
                    optimizer.zero_grad(set_to_none=True)
                    loss = event_loss(x, model(x, mask), mask).mean()
                    loss.backward()
                    optimizer.step()
                    model.validate_parameters()
                else:
                    scores.append(model.score(x, mask))
                if audit and i % 2 == 1:
                    request["status"] = "completed"
                    audit.save()
                if monitor:
                    monitor.check()
                steps.append(time.monotonic() - tick)
                io.atomic(
                    directory / "progress.json",
                    {
                        "scope": "synthetic_only",
                        "completed_batches": i + 1,
                        "completed_synthetic_steps": min(i + 1, 16),
                        "real_steps": 0,
                        "batch_wall_seconds": steps,
                    },
                )
            final_x, final_mask = x, mask

            def tensor_hash(tensors):
                h = hashlib.sha256()
                for value in tensors:
                    h.update(value.detach().cpu().numpy().tobytes())
                return h.hexdigest()

            result["numerical_identity"] = {
                "ordered_parameters_sha256": tensor_hash(list(model.parameters())),
                "adam_state_sha256": tensor_hash(
                    [
                        v
                        for state in optimizer.state.values()
                        for v in state.values()
                        if isinstance(v, torch.Tensor)
                    ]
                ),
                "reconstruction_sha256": tensor_hash([model(final_x, final_mask)]),
                "score_sha256": hashlib.sha256(
                    np.concatenate(scores).astype("<f8").tobytes()
                ).hexdigest(),
                "final_objective": loss.item(),
                "synthetic_optimizer_steps": 16,
            }
    result.update(
        status="completed",
        workload_wall_seconds=time.monotonic() - wall,
        workload_process_cpu_seconds=time.process_time() - ct,
        batch_wall_seconds=summary(steps),
        view_transform_wall_seconds=summary(views),
        audit_save_seconds=audit.save_seconds if audit else 0,
        audit_save_calls=audit.save_calls if audit else 0,
        probe_wall_seconds=summary(probe_wall),
        probe_process_cpu_seconds=summary(probe_cpu),
        observed_OS_snapshots_not_readiness=observed,
        resource_report=monitor.report() if monitor else None,
    )
    return result


def timeout(*_):
    raise TimeoutError("Import-inclusive30-second arm deadline.")


def child(name):
    directory = io.ROOT / OUTPUT / name
    reservation = io.read(directory / "reservation.json")
    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(
        signal.ITIMER_REAL,
        max(0.001, reservation["deadline_monotonic"] - time.monotonic()),
    )
    result = {"arm": name, "status": "failed"}
    try:
        result = arm(name, directory)
    except BaseException as exc:
        result.update(status="failed", error=str(exc))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        result["elapsed_seconds_including_imports"] = (
            time.monotonic() - reservation["started_monotonic"]
        )
        io.atomic(directory / "result.json", result)
    return 0 if result["status"] == "completed" else 1


def matrix():
    started = time.monotonic()
    io.assert_lightweight()
    verified_acceptance()
    directory = io.ROOT / OUTPUT
    directory.mkdir(exist_ok=False)
    io.exclusive(directory / "preregistration.json", SPEC)
    state = {
        "scope": "one_fixed_synthetic_matrix_shared_host",
        "status": "started",
        "arms": [],
        "acceptance_sha256": io.file_hash(io.ROOT / ACCEPTANCE),
        "source_sha256": io.source_hashes(),
    }
    io.atomic(directory / "matrix.json", state)
    try:
        for name in ARMS:
            tick = time.monotonic()
            remaining = min(30, 120 - (tick - started))
            if remaining <= 0:
                raise TimeoutError("Overall120-second matrix deadline.")
            sub = directory / name
            sub.mkdir()
            io.exclusive(
                sub / "reservation.json",
                {"started_monotonic": tick, "deadline_monotonic": tick + remaining},
            )
            receipt = io.dispatch(
                [
                    sys.executable,
                    "-m",
                    "raregate.supervision.particle_monitor_benchmark",
                    "--arm",
                    name,
                ],
                sub / "arm.log",
                remaining,
                started=tick,
            )
            result = (
                io.read(sub / "result.json")
                if (sub / "result.json").exists()
                else {
                    "arm": name,
                    "status": "failed",
                    "error": "Missing worker receipt",
                }
            )
            result["parent_dispatch"] = receipt
            state["arms"].append(result)
            io.atomic(directory / "matrix.json", state)
            if result["status"] != "completed" or receipt["returncode"]:
                raise RuntimeError("Arm failure; fixed matrix stops.")
        identities = [
            r["numerical_identity"]
            for r in state["arms"]
            if r["arm"].startswith("workload")
        ]
        if not all(v == identities[0] for v in identities):
            raise ValueError("Synthetic numerical parity failure.")
        state["status"] = "completed"
    except BaseException as exc:
        state.update(status="failed", error=str(exc))
    state["elapsed_seconds"] = time.monotonic() - started
    io.atomic(directory / "matrix.json", state)
    io.assert_lightweight()
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--matrix", action="store_true")
    group.add_argument("--arm", choices=ARMS)
    args = parser.parse_args()
    if args.arm:
        raise SystemExit(child(args.arm))
    result = matrix()
    print(
        json.dumps(
            {"status": result["status"], "elapsed_seconds": result["elapsed_seconds"]}
        )
    )
    if result["status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
