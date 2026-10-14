"""Task0047 worker assembly using unchanged arithmetic, scheduling and cleanup."""

import os
import sys
import time
from pathlib import Path

from latenttrigger.benchmarks import targeted_raw_protocol as p
from latenttrigger.benchmarks import targeted_raw_runtime as rt


def worker(directory, token):
    clock = rt.ContinuousClock()
    grant, permit = p.validate_grant(directory, token, clock)
    guard = rt.ServiceGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    body = dict(
        status="failed",
        task="0047",
        identity=grant["identity"],
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        grant_sha256=p.file_hash(directory / "grant.json"),
    )
    limiter = handle = blocked = None
    ledger = None
    torch_previous = None
    try:
        guard.__enter__()
        spec = p.load()
        p.require(
            all(os.environ.get(k) == v for k, v in spec["thread_environment"].items())
            and all(k not in sys.modules for k in ("numpy", "torch", "h5py")),
            "Environment before numerical/model imports",
        )
        rt.boundary(directory, grant)
        if grant["phase"] == "reporting":
            from latenttrigger.benchmarks.targeted_raw_reporting import run

            names = run(directory, guard)
            summary = p.read(directory / "summary.json")
            summary.update(task="0047", identity=grant["identity"])
            p.durable_json(directory / "summary.json", summary)
        else:
            import h5py
            import numpy as np

            from latenttrigger.benchmarks import core
            from latenttrigger.benchmarks import (
                development_raw_membership as membership,
            )
            from latenttrigger.benchmarks import development_raw_metadata as md
            from latenttrigger.benchmarks import targeted_raw_measure as measure
            from latenttrigger.benchmarks import (
                targeted_raw_planning as planning,
            )
            from latenttrigger.benchmarks import (
                targeted_raw_provider as provider,
            )
            from latenttrigger.data.features import Parameters

            blocked = rt.ProhibitedOperations(core)
            torch_previous = dict(
                intra=core.torch.get_num_threads(),
                deterministic=core.torch.are_deterministic_algorithms_enabled(),
            )
            limiter, threads = core.configure_threads(spec)
            body["effective_threads_before"] = dict(
                **threads,
                BLOSC_NTHREADS_requested=os.environ.get("BLOSC_NTHREADS"),
                effective_decoder_threads="unknown",
            )
            build = dict(
                torch_config_canonical_JSON_string_sha256=p.digest(
                    core.torch.__config__.show()
                ),
                torch_version=str(core.torch.__version__),
                numpy_version=np.__version__,
            )
            p.require(
                build["torch_config_canonical_JSON_string_sha256"]
                == grant["native_build"]["torch_config_canonical_JSON_string_sha256"]
                == spec["numerical"]["runtime_torch_build_sha256"]
                and build["torch_version"] == grant["native_build"]["torch_version"],
                "Accepted canonical Torch CPU build; no raw-vs-JSON hash confusion",
            )
            body["runtime_build"] = build
            ledger = provider.Ledger(directory)
            body["access"] = ledger.audit
            if grant["synthetic_only"]:
                from latenttrigger.benchmarks.development_decision_synthetic import (
                    models as fixture_models,
                )
                from latenttrigger.benchmarks.development_raw_synthetic import (
                    fixture,
                    parameters,
                )

                path, prefix = fixture(directory)
                member_path = directory / "fixture-membership.npy"
                golden_path = directory / "fixture-golden.npy"
                selected = np.arange(1024, dtype="<i8") * 3
                gold = np.empty((1024, 8), dtype="<f4")
                parameters = parameters()
                with h5py.File(path, "r", **p.CACHE) as f:
                    for start in range(0, 1024, 128):
                        gold[start : start + 128] = provider.construct(
                            f.get("/df/block0_values")[
                                selected[start : start + 128].tolist(), :
                            ],
                            parameters,
                        )
                np.save(golden_path, gold, allow_pickle=False)
                member_spec = dict(
                    spec["membership"],
                    file_sha256=p.file_hash(member_path),
                    selected_sha256=prefix,
                )
                golden_spec = dict(
                    spec["golden"],
                    file_sha256=p.file_hash(golden_path),
                    payload_sha256=measure.block_hash(gold),
                )
                entries = fixture_models(directory)
                model_root = directory
                body["synthetic_setup"] = dict(
                    feature_calls=8,
                    feature_rows=1024,
                    raw_requests=8,
                    raw_rows=1024,
                    model_fixture_creations=2,
                    setup_model_forward_calls=0,
                    HDF_read_handles=1,
                    HDF_write_handles=1,
                    operational_rows=0,
                )
                del selected, gold
            else:
                p.custody()
                path = p.fixed(p.ROOT, p.RAW)
                member_path = p.fixed(p.ROOT, p.MEMBERSHIP)
                golden_path = p.fixed(p.ROOT, p.GOLDEN)
                member_spec, golden_spec = spec["membership"], spec["golden"]
                parameters = Parameters.from_config(
                    p.read(p.ROOT / spec["transform_config"])
                )
                entries = spec["models"]
                model_root = p.ROOT
            original_load = np.load
            remaining = {member_path: 1, golden_path: 1}

            def only_original_arrays(path, *args, **kwargs):
                target = Path(path).absolute()
                p.require(
                    target in remaining and remaining[target] == 1,
                    "Only original membership/golden, once",
                )
                remaining[target] -= 1
                return original_load(path, *args, **kwargs)

            np.load = only_original_arrays
            try:
                selected = membership.load_once(
                    member_path, member_spec, ledger.audit, ledger.persist
                )
                golden = provider.golden_once(golden_path, golden_spec, ledger)
            finally:
                np.load = original_load
            approval = provider.Approval(selected, member_spec["selected_sha256"])
            loaded = {}
            model_identities = {}
            entry_map = {v["name"]: v for v in entries}
            for name in planning.candidates(int(grant["phase"][-1])):
                entry = entry_map[name]
                ledger.audit["model_load_attempts"] += 1
                ledger.audit["model_inflight"] = dict(
                    candidate=name, operation="original_JSON_model_and_threshold_load"
                )
                ledger.persist()
                model, thresholds = core.load_model(model_root, entry)
                ledger.audit["model_loads"] += 1
                ledger.audit["model_instantiations"] += 1
                ledger.audit["threshold_loads"] += 1
                ledger.persist()
                expected_thresholds = np.array(
                    [
                        v["threshold"]
                        for v in (
                            p.read(model_root / entry["results_path"])["scientific"][
                                "thresholds"
                            ]
                            if grant["synthetic_only"]
                            else entry["thresholds"]
                        )
                    ],
                    dtype="<f8",
                )
                p.require(
                    thresholds.shape == (4,)
                    and thresholds.dtype == np.dtype("<f8")
                    and np.isfinite(thresholds).all()
                    and thresholds.tobytes() == expected_thresholds.tobytes(),
                    "Original threshold bytes, no calibration",
                )
                artifact = p.read(model_root / entry["model_path"])
                p.require(
                    core.parameter_hash(model)
                    == p.old.expected_parameter_hash(artifact),
                    "Exact loaded parameter bytes versus bound source artifact",
                )
                loaded[name] = (model, thresholds)
                model_identities[name] = (
                    core.parameter_hash(model),
                    measure.block_hash(thresholds),
                )
                ledger.audit["model_inflight"] = None
                ledger.persist()
            body["model_parameter_threshold_hashes"] = {
                k: list(v) for k, v in model_identities.items()
            }
            guard.boundary("one_HDF_handle_across_both_candidate_blocks")
            ledger.audit.update(HDF_open_attempts=1, HDF_inflight=True)
            ledger.persist()
            handle = h5py.File(path, "r", **p.CACHE)
            ledger.audit["HDF_opens"] = 1
            ledger.persist()
            metadata = md.properties(handle, spec["raw"]["audit_schema"])
            body["HDF_same_handle_pre_post_checks"] = 1
            body["HDF_runtime"] = dict(
                metadata=metadata,
                h5py=h5py.__version__,
                HDF5=h5py.version.hdf5_version,
                hdf5plugin=p.dependencies()["packages"]["hdf5plugin"],
                effective_decoder_threads="unknown",
            )
            chain = provider.Chain(
                handle.get("/df/block0_values"),
                approval,
                path,
                clock,
                grant["operation_deadline"],
                permit=permit,
            )
            names = measure.run(
                chain,
                golden,
                parameters,
                ledger,
                directory,
                int(grant["phase"][-1]),
                guard,
                loaded,
                model_identities,
                core.effective_threads,
            )
            md.properties(handle, spec["raw"]["audit_schema"])
            body["HDF_same_handle_pre_post_checks"] = 2
            handle.close()
            handle = None
            ledger.audit.update(HDF_closed=True, HDF_inflight=False)
            ledger.persist()
            for source, expected in (
                (member_path, member_spec["file_sha256"]),
                (golden_path, golden_spec["file_sha256"]),
            ):
                p.require(p.file_hash(source) == expected, "Post input byte identity")
            if not grant["synthetic_only"]:
                p.custody()
            body["effective_threads_after"] = core.effective_threads()
            agg = p.read(directory / "aggregate.json")
            agg.update(
                task="0047",
                identity=grant["identity"],
                accounting=ledger.audit,
                geometry=planning.geometry(selected),
            )
            p.durable_json(directory / "aggregate.json", agg)
            rt.accounting(ledger.audit)
        guard.boundary("body_complete")
        body.update(
            status="body_complete_awaiting_exit",
            outputs={n: p.file_hash(directory / n) for n in names},
        )
    except BaseException as exc:
        body["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        cleanup = clock()
        try:
            if handle is not None:
                handle.close()
                if ledger is not None:
                    ledger.audit["HDF_closed"] = not handle.id.valid
                    ledger.persist()
            if limiter:
                limiter.restore_original_limits()
            if blocked:
                blocked.restore()
            if torch_previous is not None:
                core.torch.set_num_threads(torch_previous["intra"])
                core.torch.use_deterministic_algorithms(torch_previous["deterministic"])
                body["Torch_cleanup"] = dict(
                    intra_restored=True,
                    deterministic_restored=True,
                    interop_lifetime="owned_fresh_process;one_time_setting_released_by_normal_exit_reaping",
                )
        except BaseException as exc:
            body.update(status="failed", cleanup_error=str(exc))
        guard.close()
        body.update(
            resources=guard.report(),
            monitor_closed_continuous=clock(),
            cleanup_seconds=clock() - cleanup,
            worker_seconds=clock() - grant["started_continuous"],
            ordinary_worker_seconds=time.monotonic() - grant["started_ordinary"],
        )
        p.durable_json(directory / "receipt.json", body, exclusive=True)
    return (
        0
        if body["status"] == "body_complete_awaiting_exit"
        and body["cleanup_seconds"] <= 2
        and clock() < grant["stage_deadline"]
        else 1
    )
