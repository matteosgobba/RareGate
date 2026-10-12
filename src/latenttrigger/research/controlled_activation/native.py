"""One fixed generated-fixture worker; no operational CLI/input/source allowance."""

import argparse
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from latenttrigger.research.controlled_activation import protocol as p
from latenttrigger.research.controlled_activation import runtime as rt


def worker(directory, token):
    directory = Path(directory).resolve()
    p.require(
        directory.parent == p.ROOT / "data/task0035-native-invocations"
        and len(directory.name) == 32
        and all(c in "0123456789abcdef" for c in directory.name),
        "Fixed owned native namespace; no input path",
    )
    grant = p.read(directory / "grant.json")
    p.require(
        grant["token"] == token
        and grant["parent_pid"] == os.getppid()
        and grant["synthetic_only"] is True,
        "Owned synthetic grant",
    )
    clock = rt.ContinuousClock()
    guard = rt.SyntheticGuard(
        grant["operation_deadline"], directory=directory, clock=clock
    )
    result = dict(
        status="failed",
        grant_sha256=p.file_hash(directory / "grant.json"),
        source_map=grant["source_map"],
        dependencies=grant["dependencies"],
        config_sha256=grant["config_sha256"],
    )
    models = None
    cleanup_ok = False
    try:
        guard.__enter__()
        p.require(
            p.source_map() == grant["source_map"]
            and p.runtime_versions() == grant["dependencies"],
            "Worker source/dependency identity",
        )
        spec = p.load_config()
        rt.install_boundary(p.ROOT, directory)
        import numpy as np
        import torch

        from latenttrigger.models.autoencoder import CompactAutoencoder
        from latenttrigger.research.controlled_activation import inference, models
        from latenttrigger.training.autoencoder import feature_loader

        guard.context()

        def notify():
            p.durable_json(directory / "counters.json", dict(models.COUNTERS))

        notify()
        rng = np.random.default_rng(241035)
        arrays = {
            r: rng.normal(size=(n, 8)).astype(np.float32)
            for r, n in zip(p.ROLES, (17, 13, 21), strict=True)
        }
        provider = models.SyntheticProvider(arrays)
        background = rng.normal(size=(127, 8)).astype(np.float32)
        signal = rng.normal(size=(131, 8)).astype(np.float32)
        budgets = models.SyntheticSteps()
        reports, pairs, nonlin_loader, initial_hash = [], [], None, None
        bdec, sdec = [], []
        for seed in p.SEEDS:
            initial = models.initialization(seed, spec)
            p.durable_json(
                directory / f"initialization-{seed}.json", initial, exclusive=True
            )
            for arm in p.ARMS:
                model = models.factory(arm, seed, spec, initial)
                with models.deterministic_cpu(seed, 1):
                    if arm == "nonlinear":
                        reference = CompactAutoencoder()
                        p.require(
                            models.parameter_document(reference)
                            == initial["parameters"],
                            "Historical fresh initialization parity",
                        )
                        with torch.inference_mode():
                            tensor = torch.from_numpy(arrays[p.ROLES[1]])
                            p.require(
                                torch.equal(model(tensor), reference(tensor)),
                                "Historical synthetic forward parity",
                            )
                    else:
                        with torch.inference_mode():
                            tensor = torch.from_numpy(arrays[p.ROLES[1]])
                            affine = tensor
                            for layer in (
                                model.encoder[0],
                                model.encoder[2],
                                model.decoder[0],
                                model.decoder[2],
                            ):
                                affine = torch.nn.functional.linear(
                                    affine, layer.weight, layer.bias
                                )
                            p.require(
                                torch.equal(model(tensor), affine),
                                "Intended affine composition",
                            )
                    train = models.role_values(provider, p.ROLES[0], "fit")
                    selection = models.role_values(provider, p.ROLES[1], "selection")
                    loader = models.PairedLoader(train, arm=arm, seed=seed)
                    selector = models.Selection(
                        model, initial["parameters_digest"], selection
                    )
                    opt = models.optimizer(model)
                    for epoch in (1, 2):
                        guard.boundary(f"{arm}-{seed}-epoch-{epoch}")
                        models.epoch_loss(
                            model,
                            loader,
                            opt=opt,
                            budget=budgets,
                            check=guard.check,
                            notify=notify,
                        )
                        loss = models.epoch_loss(
                            model,
                            feature_loader(selection, 4096, shuffle=False, seed=seed),
                            check=guard.check,
                        )
                        selector.update(epoch, loss, model)
                    checkpoint = directory / f"checkpoint-{arm}-{seed}.json"
                    p.durable_json(checkpoint, selector.best, exclusive=True)
                    restored = selector.restore(model, p.read(checkpoint))
                    calibration = models.calibrate(
                        model, provider, p.ROLES[2], restored
                    )
                    bdec.append(models.decisions(model, background, calibration))
                    sdec.append(models.decisions(model, signal, calibration))
                    reports.append(
                        dict(
                            arm=arm,
                            seed=seed,
                            restoration=restored,
                            initialization_digest=initial["parameters_digest"],
                            epoch_orders=loader.epochs,
                            calibration_digest=calibration["sha256"],
                        )
                    )
                    if arm == "nonlinear":
                        nonlin_loader, initial_hash = (
                            loader,
                            initial["parameters_digest"],
                        )
                    else:
                        pairs.append(
                            dict(
                                seed=seed,
                                **models.accept_pair(
                                    nonlin_loader,
                                    loader,
                                    initial_hash,
                                    initial["parameters_digest"],
                                ),
                            )
                        )
                notify()
        bg = inference.Patterns().add(bdec)
        sig = inference.Patterns().add(sdec)
        decision = inference.decide(bg, sig, {k: False for k in inference.ELIGIBILITY})
        report = dict(
            kind="synthetic_only",
            arms=reports,
            pairs=pairs,
            decision=decision,
            aggregate_denominators=[bg.n, sig.n],
            patterns=[bg.counts, sig.counts],
            historical_synthetic_reference_instances=3,
            historical_synthetic_reference_forward_calls=3,
            no_toy_scientific_ranking=True,
            PCA_three_implemented=False,
            operational_population_or_array_access=0,
        )
        p.durable_json(directory / "report.json", report, exclusive=True)
        notify()
        guard.boundary("body_outputs_complete")
        names = {
            "report.json",
            "counters.json",
            *[f"initialization-{s}.json" for s in p.SEEDS],
            *[f"checkpoint-{arm}-{s}.json" for arm, s in p.ORDER],
        }
        result.update(
            status="body_complete_awaiting_exit",
            counters=dict(models.COUNTERS),
            all_pairing_restoration_checks=True,
            outputs={n: p.file_hash(directory / n) for n in names},
        )
    except BaseException as error:
        result["error"] = f"{type(error).__name__}: {error}"
        if models is not None:
            result["counters"] = dict(models.COUNTERS)
    finally:
        cleanup = clock()
        guard.close()
        result.update(
            resources=guard.report(),
            monitor_closed_continuous=clock(),
            cleanup_seconds=clock() - cleanup,
            worker_seconds=clock() - grant["worker_started"],
            worker_ordinary_seconds=time.monotonic() - grant["worker_ordinary_started"],
        )
        p.durable_json(directory / "receipt.json", result, exclusive=True)
        cleanup_ok = clock() - cleanup <= 2 and clock() < grant["stage_deadline"]
    return 0 if result["status"] == "body_complete_awaiting_exit" and cleanup_ok else 1


def run_native():
    clock = rt.ContinuousClock()
    started = clock()
    whole = started + 120
    directory = p.ROOT / "data/task0035-native-invocations" / uuid.uuid4().hex
    directory.mkdir(parents=True, exist_ok=False)
    assertion = None
    workflow = dict(
        kind="synthetic_only",
        status="prerequisites",
        started=clock.snapshot(),
        source_map=p.source_map(),
        dependencies=p.runtime_versions(),
        counters=dict(
            optimizer_steps_started=0,
            optimizer_steps_completed=0,
            optimizer_steps_inflight=0,
        ),
        operational_work=0,
    )
    dispatch = None
    try:
        with rt.alarm(clock, min(whole, started + 30)):
            p.load_config()
            rt.parent_check(clock=clock, deadline=whole)
            p.require(
                shutil.disk_usage(directory).free >= 128 * 2**20,
                "Owned storage admission",
            )
            assertion = rt.IdleAssertion(clock)
            assertion.start(min(whole, started + 30))
            workflow["prerequisite_seconds"] = clock() - started
        tick = clock()
        stage = min(whole, tick + 60)
        grant = dict(
            synthetic_only=True,
            parent_pid=os.getpid(),
            token=uuid.uuid4().hex,
            config_sha256=p.file_hash(p.ROOT / p.CONFIG),
            source_map=workflow["source_map"],
            dependencies=workflow["dependencies"],
            worker_started=tick,
            worker_ordinary_started=time.monotonic(),
            operation_deadline=stage - 2,
            stage_deadline=stage,
            assertion_id=assertion.identity,
        )
        p.durable_json(directory / "grant.json", grant, exclusive=True)
        (directory / "tmp").mkdir()
        env = dict(
            os.environ,
            PYTHONDONTWRITEBYTECODE="1",
            OMP_NUM_THREADS="1",
            OPENBLAS_NUM_THREADS="1",
            MKL_NUM_THREADS="1",
            VECLIB_MAXIMUM_THREADS="1",
            TORCH_HOME=str(directory / "torch-cache"),
            TORCHINDUCTOR_CACHE_DIR=str(directory / "compiler-cache"),
            XDG_CACHE_HOME=str(directory / "cache"),
            TMPDIR=str(directory / "tmp"),
            PYTHONPATH=str(p.ROOT / "src") + os.pathsep + str(p.ROOT),
        )
        # First forced observation follows launch, then fixed inherited5s cadence.
        observed = False

        def monitor():
            nonlocal observed
            assertion.check(stage - 2, force=not observed)
            observed = True
            rt.storage_check(directory)

        dispatch = rt.supervise(
            [
                sys.executable,
                "-m",
                "latenttrigger.research.controlled_activation.native",
                "--worker",
                str(directory),
                "--token",
                grant["token"],
            ],
            directory / "worker.log",
            root=p.ROOT,
            environment=env,
            clock=clock,
            operation_deadline=stage - 2,
            stage_deadline=stage,
            whole_deadline=whole,
            monitor=monitor,
        )
        workflow["dispatch"] = dispatch
        final_started = clock()
        final_deadline = min(whole, final_started + 15)
        with rt.alarm(clock, final_deadline):
            body = p.read(directory / "receipt.json")
            workflow["counters"] = body.get("counters", workflow["counters"])
            accepted = rt.accept_body(
                body, dispatch, grant, directory, clock, final_deadline
            )
            assertion.check(final_deadline, force=True)
            workflow["sleep_assertion"] = assertion.release(final_deadline)
            workflow.update(
                status="parent_accepted_synthetic",
                acceptance=accepted,
                resources=body["resources"],
                worker_seconds=body["worker_seconds"],
                storage_bytes=rt.storage_check(directory),
                controller_peak_RSS_bytes=rt.parent_check(
                    clock=clock, deadline=final_deadline
                ),
                whole_seconds=clock() - started,
                finalization_seconds=clock() - final_started,
                overshoot_seconds=max(0, clock() - whole),
                finished=clock.snapshot(),
            )
            p.durable_json(directory / "workflow.json", workflow, exclusive=True)
            p.durable_json(
                directory / "parent-acceptance.json",
                dict(
                    status="parent_accepted_synthetic",
                    workflow_sha256=p.file_hash(directory / "workflow.json"),
                    source_map=workflow["source_map"],
                    synthetic_only=True,
                    assertion_released=True,
                ),
                exclusive=True,
            )
            rt.check_deadline(clock, final_deadline)
    except BaseException as error:
        workflow.update(
            status="failed_synthetic_preserved",
            error=f"{type(error).__name__}: {error}",
            dispatch=dispatch,
        )
        if (directory / "counters.json").is_file():
            try:
                workflow["counters"] = p.read(directory / "counters.json")
            except BaseException as counter_error:
                workflow["counter_recovery_error"] = str(counter_error)
                workflow["counter_values_are_last_known_only"] = True
        if assertion is not None and not assertion.evidence["released"]:
            try:
                workflow["sleep_assertion"] = assertion.release(min(whole, clock() + 2))
            except BaseException as e:
                workflow["sleep_assertion"] = dict(
                    assertion.evidence, release_error=str(e)
                )
        workflow.update(
            whole_seconds=clock() - started,
            overshoot_seconds=max(0, clock() - whole),
            finished=clock.snapshot(),
        )
        # A late publication cannot leave an accepted marker standing.
        marker = directory / "parent-acceptance.json"
        if marker.exists():
            marker.rename(directory / "rejected-publication.json")
        p.durable_json(directory / "workflow.json", workflow)
    return directory, workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--token")
    args = parser.parse_args()
    if args.worker:
        p.require(args.token, "Owned grant required")
        raise SystemExit(worker(args.worker, args.token))
    p.require(args.token is None, "No arbitrary token/input")
    directory, result = run_native()
    print(
        dict(
            directory=str(directory),
            status=result["status"],
            error=result.get("error"),
            counters=result["counters"],
            whole_seconds=result["whole_seconds"],
        )
    )
    raise SystemExit(0 if result["status"] == "parent_accepted_synthetic" else 1)


if __name__ == "__main__":
    main()
