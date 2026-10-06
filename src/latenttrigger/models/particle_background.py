"""Audited particle streaming and sequential, gated background orchestration."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

from latenttrigger.data.analysis import write_json
from latenttrigger.data.processed import ProcessedStore, content_hash
from latenttrigger.evaluation.metrics import ks_distance, score_summary
from latenttrigger.evaluation.thresholds import (
    background_operating_point,
    calibrate_thresholds,
)
from latenttrigger.models.background import build_metadata
from latenttrigger.models.particle_set import (
    ROOT,
    ParticleSetAutoencoder,
    validate_completion,
    validate_config,
    validate_store,
)
from latenttrigger.training.autoencoder import deterministic_cpu
from latenttrigger.training.particle_set import (
    ResourceLimitError,
    ResourceMonitor,
    adam,
    epoch,
    fit,
    score_hash,
)

ROLES = (
    "train_background",
    "validation_selection_background",
    "validation_calibration_background",
)


class Audit:
    def __init__(self, path=None):
        self.path, self.records = path, []

    def save(self):
        if self.path:
            write_json(
                self.path,
                {
                    "population_access": self.records,
                    "test_background_model_access": False,
                    "test_signal_model_access": False,
                },
            )

    def advance(self, record, count):
        record["events_read"] += count
        if self.path:
            with self.path.with_suffix(".jsonl").open("a") as file:
                file.write(
                    json.dumps(
                        {
                            "request": len(self.records) - 1,
                            "events_read": record["events_read"],
                        }
                    )
                    + "\n"
                )

    def request(self, split, purpose, dev, expected):
        record = {
            "split": split,
            "purpose": purpose,
            "representation": "particle_model_view",
            "dev_only": dev,
            "allow_test": False,
            "include_labels": False,
            "expected_events": expected,
            "events_read": 0,
            "status": "requested",
        }
        self.records.append(record)
        self.save()
        return record


def require_role(split, stage, *, include_labels=False, completion=None):
    if include_labels or split not in ROLES:
        raise ValueError(
            "Particle background workflow refuses test/truth/unknown role."
        )
    allowed = {"dev": ROLES[:1], "fit": ROLES[:2], "postfreeze": ROLES}
    if stage not in allowed or split not in allowed[stage]:
        raise ValueError("Population is unavailable at this prerequisite stage.")
    if stage == "postfreeze":
        if not completion:
            raise ValueError(
                "Calibration requires frozen/reproduced completion evidence."
            )
        validate_completion(*completion)


def open_store(path, config, roles, *, stage, completion=None, factory=ProcessedStore):
    """Reject forbidden roles/truth before store construction/custody verification."""
    validate_config(config)
    if not roles:
        raise ValueError("Explicit population roles required.")
    for split in roles:
        require_role(split, stage, completion=completion)
    store = factory(path)
    try:
        validate_store(store.manifest, config, dev=stage == "dev")
    except BaseException:
        store.close()
        raise
    return store


class ParticleBatches:
    """Bounded real model views; metadata is returned separately from X and mask."""

    def __init__(
        self,
        store,
        split,
        audit,
        *,
        stage,
        purpose,
        dev=False,
        dev_ids=None,
        completion=None,
    ):
        require_role(split, stage, completion=completion)
        self.store, self.role, self.audit = store, split, audit
        self.stage, self.purpose, self.dev = stage, purpose, dev
        self.ids = store.event_ids(split, allow_test=False, dev_only=dev)
        self.dev_ids = dev_ids
        if dev_ids is not None:
            if (
                len(dev_ids) != 1024
                or not dev
                or split != ROLES[0]
                or not np.array_equal(dev_ids, self.ids[:1024])
            ):
                raise ValueError(
                    "Dev gate requires exactly first1024 frozen dev-training IDs."
                )
            self.expected = 1024
        else:
            self.expected = len(self.ids)
        if self.expected == 0:
            raise ValueError("Empty allowed particle population.")

    def __call__(self, order=None):
        record = self.audit.request(self.role, self.purpose, self.dev, self.expected)
        try:
            if self.dev_ids is not None:
                selected_ids = self.dev_ids
                if order is not None:
                    order = np.asarray(order)
                    if (
                        order.dtype.kind not in "iu"
                        or order.shape != (1024,)
                        or not np.array_equal(np.sort(order), np.arange(1024))
                    ):
                        raise ValueError(
                            "Dev order must permute all1024 sample positions."
                        )
                    selected_ids = selected_ids[order]
                batches = (
                    self.store.read_ids(
                        self.role,
                        selected_ids[start : start + 32],
                        allow_test=False,
                        include_labels=False,
                        dev_only=True,
                    )
                    for start in range(0, 1024, 32)
                )
            else:
                batches = self.store.iter_batches(
                    self.role,
                    batch_size=32,
                    dev_only=self.dev,
                    allow_test=False,
                    include_labels=False,
                    order=order,
                )
            for batch in batches:
                if batch.labels is not None or len(batch.event_ids) > 32:
                    raise ValueError("Unexpected truth/unbounded particle batch.")
                view = batch.model_view(nmax=384)
                self.audit.advance(record, len(view.features))
                metadata = {
                    "event_ids": batch.event_ids,
                    "n_original": view.n_original,
                    "n_retained": view.n_retained,
                    "retained_pt_fraction": view.retained_pt_fraction,
                    "physical_event_aggregates": batch.event_aggregates,
                }
                yield (
                    torch.from_numpy(view.features),
                    torch.from_numpy(view.mask),
                    metadata,
                )
            if record["events_read"] != self.expected:
                raise ValueError("Incomplete particle population.")
            record["status"] = "completed"
            self.audit.save()
        except BaseException as exc:
            record.update(status="failed_or_interrupted", error=str(exc))
            self.audit.save()
            raise


def provenance(store, config):
    spec = config["input"]
    return {
        "scope": "canonical_full",
        "processed_scientific_sha256": store.manifest["scientific_sha256"],
        **{
            key: spec[key]
            for key in (
                "source_sha256",
                "preprocessing_config_sha256",
                "split_identity_sha256",
            )
        },
    }


def verify_acceptance(path, config):
    evidence = json.loads(Path(path).read_text())
    from latenttrigger.data.analysis import file_sha256

    if (
        evidence.get("pytest_exit_code") != 0
        or evidence.get("config_sha256") != content_hash(config)
        or not evidence.get("workspace_measurement")
        or evidence["workspace_measurement"]["peak_tensor_bytes"] > 512 * 2**20
    ):
        raise ValueError("Synthetic acceptance/resource measurement not verified.")
    expected_paths = source_hashes()
    if evidence.get("source_sha256") != expected_paths:
        raise ValueError(
            "Acceptance source changed; repeat synthetic checks before reads."
        )
    for rel, digest in expected_paths.items():
        if file_sha256(ROOT / rel) != digest:
            raise ValueError("Acceptance code identity mismatch.")
    return evidence


def source_hashes():
    from latenttrigger.data.analysis import file_sha256

    paths = [
        *sorted((ROOT / "src/latenttrigger").rglob("*.py")),
        *sorted((ROOT / "tests").glob("*.py")),
    ]
    return {str(path.relative_to(ROOT)): file_sha256(path) for path in paths}


def run_dev(store_path, config, output, monitor, audit):
    timings, steps = [], 0
    # Launch/resource checks happen before constructing a reader.
    with monitor.deadline("whole_dev_gate", 300):
        monitor.check()
        started = time.monotonic()
        with open_store(store_path, config, ROLES[:1], stage="dev") as store:
            verification = time.monotonic() - started
            ids = store.event_ids(ROLES[0], dev_only=True)[:1024]
            batches = ParticleBatches(
                store,
                ROLES[0],
                audit,
                stage="dev",
                purpose="bounded_dev_training",
                dev=True,
                dev_ids=ids,
            )
            with deterministic_cpu(1729, 1):
                model = ParticleSetAutoencoder()
                optimizer = adam(model, config)
                shuffle = torch.Generator(device="cpu").manual_seed(1729)
                for _ in range(3):
                    tick = time.monotonic()
                    order = torch.randperm(1024, generator=shuffle).numpy()
                    objective = epoch(
                        model,
                        batches(order),
                        monitor,
                        optimizer=optimizer,
                        expected=1024,
                    )
                    timings.append(time.monotonic() - tick)
                    steps += 32
                    write_json(
                        output / "dev-progress.json",
                        {"completed_passes": len(timings), "steps": steps},
                    )
                batches.purpose = "bounded_dev_same_sample_scoring"
                tick = time.monotonic()
                mean, scores = epoch(model, batches(), monitor, expected=1024)
                score_seconds = time.monotonic() - tick
        extrapolation = 2 * (
            699957 * max(timings) / 1024 + 74749 * score_seconds / 1024
        )
        result = {
            "scope": "disposable_dev_diagnostic",
            "passes": 3,
            "optimizer_steps": steps,
            "unique_events": 1024,
            "train_pass_seconds": timings,
            "score_pass_seconds": score_seconds,
            "verification_seconds": verification,
            "last_online_objective": objective,
            "same_sample_score_mean": mean,
            "same_sample_score_sha256": score_hash(scores),
            "extrapolated_full_cycle_seconds": extrapolation,
            "feasibility_pass": extrapolation <= 180,
            "resources": monitor.report(),
        }
        write_json(output / "dev-gate.json", result)
        if not result["feasibility_pass"]:
            raise ResourceLimitError(
                "Frozen conservative dev extrapolation exceeds180s."
            )
        return result


def run_fit(store_path, config, output, monitor, audit):
    tick = monitor.started
    with open_store(store_path, config, ROLES[:2], stage="fit") as store:
        train = ParticleBatches(
            store, ROLES[0], audit, stage="fit", purpose="gradient_training"
        )
        selection = ParticleBatches(
            store, ROLES[1], audit, stage="fit", purpose="early_stopping"
        )
        if (train.expected, selection.expected) != (699957, 74749):
            raise ValueError("Canonical fitting counts mismatch.")

        def progress(row, stopping):
            with (output / "history.jsonl").open("a") as file:
                file.write(json.dumps(row, allow_nan=False) + "\n")
            print(
                f"Epoch {row['epoch']}: online={row['online_training_objective']:.9g}; "
                f"selection={row['selection_mean_score']:.9g}; best={stopping.best_epoch}; "
                f"bad={stopping.bad_epochs}",
                flush=True,
            )

        # Include verification/startup in fitting deadline, never hide it.
        remaining = 36000 - (time.monotonic() - tick)
        with monitor.deadline("fit_including_verification", remaining):
            model, history, training = fit(
                train, selection, config, monitor, on_epoch=progress
            )
        write_json(output / "training.json", {"history": history, "training": training})
        if training["stopping_reason"] != "patience":
            raise ResourceLimitError("Convergence unresolved at200-epoch ceiling.")
        postfit_started = time.monotonic()
        with monitor.deadline("postfit", 3600):
            candidate = model.artifact(
                config=config, provenance=provenance(store, config), training=training
            )
            write_json(output / "candidate.json", candidate)
            loaded = ParticleSetAutoencoder.load(
                output / "candidate.json", allow_candidate=True
            )
            for name, value in model.state_dict().items():
                if not torch.equal(value, loaded.state_dict()[name]):
                    raise ValueError("Reloaded parameter bytes differ.")
            with deterministic_cpu(1729, 1):
                mean, scores = epoch(loaded, selection(), monitor, expected=74749)
            if (
                mean != training["best_selection_mean_score"]
                or score_hash(scores) != training["selection_score_sha256"]
            ):
                raise ValueError(
                    "Restored selection scores differ from selected checkpoint."
                )
            training["restored_verified"] = True
            candidate = model.artifact(
                config=config, provenance=provenance(store, config), training=training
            )
            write_json(output / "candidate.json", candidate)
        return {
            "scope": "canonical_candidate",
            "training": training,
            "candidate_scientific_sha256": candidate["scientific_sha256"],
            "postfit_elapsed_seconds": time.monotonic() - postfit_started,
            "resources": monitor.report(),
        }


def compare_repetitions(first, second):
    for key in ("scientific_sha256", "scientific"):
        if first[key] != second[key]:
            raise ValueError("Independent scientific particle reproduction mismatch.")


def profiles(scores, variables, edges, thresholds):
    rows = []
    for name, values in variables.items():
        boundaries = edges[name]
        indices = np.searchsorted(boundaries, values, side="right")
        for index in range(len(boundaries) + 1):
            selected = scores[indices == index]
            row = {
                "variable": name,
                "bin": index,
                "count": len(selected),
                "mean_score": float(selected.mean()) if len(selected) else None,
                "median_score": float(np.median(selected)) if len(selected) else None,
                "p99_score": float(np.quantile(selected, 0.99, method="linear"))
                if len(selected)
                else None,
                "max_score": float(selected.max()) if len(selected) else None,
                "operating_points": [
                    background_operating_point(selected, p["threshold"])
                    for p in thresholds
                ]
                if len(selected)
                else [],
                "edges": boundaries.tolist(),
                "merged_bins": 10 - (len(boundaries) + 1)
                if name != "truncation_flag"
                else 0,
            }
            rows.append(row)
    return rows


def run_postfreeze(store_path, config, output, monitor, audit, artifact_path):
    artifact = json.loads(Path(artifact_path).read_text())
    model = ParticleSetAutoencoder.from_artifact(artifact)
    science = artifact["scientific"]
    completion = (science["training"], science["provenance"])
    scores, variables, summaries, hashes = {}, {}, {}, {}
    with monitor.deadline("postfit", 3600):
        with open_store(
            store_path, config, ROLES, stage="postfreeze", completion=completion
        ) as store:
            for split in ROLES:
                batches = ParticleBatches(
                    store,
                    split,
                    audit,
                    stage="postfreeze",
                    purpose="frozen_background_reporting",
                    completion=completion,
                )
                chunks, values = [], {}
                for x, mask, metadata in batches():
                    monitor.check()
                    chunks.append(model.score(x, mask))
                    physical = metadata["physical_event_aggregates"]
                    observed = {
                        "n_retained": metadata["n_retained"],
                        "n_original": metadata["n_original"],
                        "truncation_flag": metadata["n_original"]
                        > metadata["n_retained"],
                        "retained_pt_fraction": metadata["retained_pt_fraction"],
                        "scalar_pt": physical[:, 1],
                        "max_pt": physical[:, 2],
                        "massless_event_mass": physical[:, 7],
                    }
                    for name, v in observed.items():
                        values.setdefault(name, []).append(v)
                scores[split] = np.concatenate(chunks)
                variables[split] = {
                    name: np.concatenate(v) for name, v in values.items()
                }
                hashes[split] = score_hash(scores[split])
                summaries[split] = score_summary(scores[split])
            thresholds = calibrate_thresholds(
                scores[ROLES[2]], [0.1, 0.05, 0.01, 0.001]
            )
            for point in thresholds:
                point["selection"] = background_operating_point(
                    scores[ROLES[1]], point["threshold"]
                )
                delta = point["selection"]["efficiency"] - point["target_fpr"]
                point.update(
                    absolute_deviation=abs(delta),
                    relative_deviation=delta / point["target_fpr"],
                )
            train = variables[ROLES[0]]
            edges = {
                name: np.array([0.5])
                if name == "truncation_flag"
                else np.unique(
                    np.quantile(values, np.arange(1, 10) / 10, method="linear")
                )
                for name, values in train.items()
            }
            result = {
                "model_scientific_sha256": artifact["scientific_sha256"],
                "score_array_sha256": hashes,
                "background_summary": summaries,
                "restored_training_mean_score": summaries[ROLES[0]]["mean"],
                "thresholds": thresholds,
                "stability": {
                    f"{a}_vs_{b}": ks_distance(scores[a], scores[b])
                    for a, b in [
                        (ROLES[0], ROLES[1]),
                        (ROLES[0], ROLES[2]),
                        (ROLES[1], ROLES[2]),
                    ]
                },
                "diagnostic_profiles": {
                    split: profiles(scores[split], variables[split], edges, thresholds)
                    for split in ROLES
                },
            }
            write_json(
                output / "background-results.json",
                {"scientific": result, "scientific_sha256": content_hash(result)},
            )
    return {"status": "background_completed", "resources": monitor.report()}


def worker(args, config):
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    audit = Audit(output / "access-audit.json")
    audit.save()
    monitor = ResourceMonitor(config["resource_gate"])
    if args.stage_started is not None:
        monitor.started = args.stage_started
    try:
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        torch.use_deterministic_algorithms(True, warn_only=False)
        with (
            monitor,
            monitor.deadline(
                "whole_stage_including_startup",
                args.stage_budget - (time.monotonic() - monitor.started),
            ),
        ):
            if args.worker == "dev":
                result = run_dev(args.dev_store, config, output, monitor, audit)
            elif args.worker == "fit":
                result = run_fit(args.store, config, output, monitor, audit)
            else:
                result = run_postfreeze(
                    args.store, config, output, monitor, audit, args.artifact
                )
        result.update(status="passed", engineering=build_metadata())
    except BaseException as exc:
        result = {
            "status": "failed_or_interrupted",
            "error": str(exc),
            "resources": monitor.report(),
            "downstream_authorized": False,
        }
    write_json(output / "stage-result.json", result)
    print(json.dumps(result), flush=True)
    return 0 if result["status"] == "passed" else 1


def run_task(args, config, *, attempt_budget=None):
    verify_acceptance(args.acceptance, config)
    if attempt_budget is None:
        attempt_budget = ROOT / "data/baselines/task0010-particle-attempt-budget.json"
    attempt_budget.parent.mkdir(parents=True, exist_ok=True)
    with attempt_budget.open("x") as file:
        json.dump(
            {
                "config_sha256": content_hash(config),
                "output": str(args.output),
                "status": "attempt_reserved_no_automatic_retry",
            },
            file,
        )
    args.output.mkdir(parents=True, exist_ok=False)
    ledger = args.output / "workflow.json"
    state = {
        "config_sha256": content_hash(config),
        "stages": [],
        "status": "started",
        "gate_order": [
            "dev",
            "first_fit",
            "repeat_fit",
            "freeze",
            "background_first",
            "background_repeat",
        ],
    }
    write_json(ledger, state)
    started = time.monotonic()
    canonical_started = None

    def dispatch(kind, name, artifact=None):
        directory = args.output / name
        budget = 300 if kind == "dev" else (39600 if kind == "fit" else 3600)
        if kind == "postfreeze":
            fit_name = "first" if name == "background-first" else "repeat"
            fit_result = next(v for v in state["stages"] if v["stage"] == fit_name)
            budget -= fit_result["postfit_elapsed_seconds"]
        child_started = time.monotonic()
        command = [
            sys.executable,
            "-m",
            "latenttrigger.models.particle_background",
            "--worker",
            kind,
            "--stage-started",
            str(child_started),
            "--stage-budget",
            str(budget),
            "--output",
            str(directory),
            "--config",
            str(args.config),
            "--store",
            str(args.store),
            "--dev-store",
            str(args.dev_store),
            "--acceptance",
            str(args.acceptance),
        ]
        if artifact:
            command.extend(["--artifact", str(artifact)])
        timeout = budget
        if canonical_started is not None:
            timeout = min(budget, 79200 - (time.monotonic() - canonical_started))
        with (args.output / f"{name}.log").open("w") as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            try:
                child.wait(timeout=max(0.001, timeout))
            except subprocess.TimeoutExpired:
                child.terminate()
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                state["status"] = "resource_ceiling_interrupted"
                write_json(ledger, state)
                raise ResourceLimitError(
                    "Supervisor wall-time ceiling interrupted worker."
                ) from None
        result_path = directory / "stage-result.json"
        result = (
            json.loads(result_path.read_text())
            if result_path.exists()
            else {"status": "failed", "error": "worker terminated without final report"}
        )
        state["stages"].append({"stage": name, **result})
        write_json(ledger, state)
        if result["status"] != "passed":
            raise ResourceLimitError(result.get("error", "Gate failed."))
        return directory

    try:
        dispatch("dev", "dev")
        canonical_started = time.monotonic()
        first = dispatch("fit", "first")
        second = dispatch("fit", "repeat")
        a = json.loads((first / "candidate.json").read_text())
        b = json.loads((second / "candidate.json").read_text())
        compare_repetitions(a, b)
        model = ParticleSetAutoencoder.from_artifact(a, allow_candidate=True)
        training = a["scientific"]["training"]
        training["reproduction_verified"] = True
        frozen = model.artifact(
            config=config,
            provenance=a["scientific"]["provenance"],
            training=training,
            finalized=True,
        )
        artifact = args.output / "frozen-model.json"
        write_json(artifact, frozen)
        one = dispatch("postfreeze", "background-first", artifact)
        two = dispatch("postfreeze", "background-repeat", artifact)
        x = json.loads((one / "background-results.json").read_text())
        y = json.loads((two / "background-results.json").read_text())
        if x != y:
            raise ValueError("Independent frozen background results differ.")
        state["status"] = "canonical_baseline_completed"
    except BaseException as exc:
        state.update(status="implementation_complete_canonical_pending", error=str(exc))
    state["elapsed_seconds"] = time.monotonic() - started
    write_json(ledger, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/models/compact_particle_set_autoencoder_v1.json",
    )
    parser.add_argument(
        "--store", type=Path, default=ROOT / "data/processed/lhco-rd-v1/schema-v1/full"
    )
    parser.add_argument(
        "--dev-store",
        type=Path,
        default=ROOT / "data/processed/lhco-rd-v1/schema-v1/dev",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/baselines/compact-particle-set-autoencoder-v1",
    )
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument(
        "--worker", choices=["dev", "fit", "postfreeze"], help=argparse.SUPPRESS
    )
    parser.add_argument("--artifact", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--stage-started", type=float, help=argparse.SUPPRESS)
    parser.add_argument(
        "--stage-budget", type=float, default=300, help=argparse.SUPPRESS
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    validate_config(config)
    verify_acceptance(args.acceptance, config)
    if args.worker:
        # Worker invocation needs the parent ledger confirming the preceding gate.
        parent = json.loads((args.output.parent / "workflow.json").read_text())
        prior = parent["stages"]
        if args.worker == "fit" and not any(
            x["stage"] == "dev" and x["status"] == "passed" for x in prior
        ):
            raise ValueError("Canonical training requires passed dev gate.")
        if args.worker == "postfreeze" and (not args.artifact or len(prior) < 3):
            raise ValueError(
                "Background stage requires two reproduced fits and freeze."
            )
        raise SystemExit(worker(args, config))
    result = run_task(args, config)
    print(json.dumps(result, indent=2), flush=True)
    raise SystemExit(0 if result["status"] == "canonical_baseline_completed" else 1)


if __name__ == "__main__":
    main()
