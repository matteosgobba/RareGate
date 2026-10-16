"""Task0061 only. Help/import do not activate acquisition or scientific work.

The parent configures caches/threads before any numerical-library import.
Real stages require a current generated-test binding and exclusive persisted intent.
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/research/decisive_adc_preparation_v2.json"


def configure(root):
    for name, value in dict(
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        RUFF_NO_CACHE="true",
        PYTHONPATH=os.pathsep.join((str(ROOT), str(ROOT / "src"))),
        XDG_CACHE_HOME=str(root / "cache"),
        MPLCONFIGDIR=str(root / "cache/matplotlib"),
        TMPDIR=str(root / "tmp"),
        OMP_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        VECLIB_MAXIMUM_THREADS="1",
        NUMEXPR_NUM_THREADS="1",
        BLOSC_NTHREADS="1",
    ).items():
        os.environ[name] = value
    sys.path.insert(0, str(ROOT / "src"))


def owned_bytes(root, models):
    paths = [root, models]
    total = 0
    for base in paths:
        for directory, folders, files in os.walk(base, followlinks=False):
            for name in folders + files:
                path = Path(directory) / name
                if path.is_symlink():
                    # Generated tests include convenience links and deliberate
                    # invalid-payload counterexamples. Their internal targets are
                    # contained and never followed; real payload aliases fail.
                    if not (
                        path.is_relative_to(root / "tests")
                        and path.resolve().is_relative_to(root / "tests")
                    ):
                        raise ValueError("owned-path alias")
            total += sum((Path(directory) / name).lstat().st_size for name in files)
    total += sum(
        p.stat().st_size for p in (ROOT / "results/tables/final").glob("task0061-*")
    )
    return total


def worker(stage, root, models):
    from raregate.research.decisive_adc import data
    from raregate.research.decisive_adc.execution import (
        acquire,
        lifetime_rss_bytes,
        read_config,
        runtime,
        verify_binding,
    )
    from raregate.research.decisive_adc.study import (
        Study,
        calibrate,
        fit_stream,
        install_phase_guard,
        prepare,
        symmetry,
    )

    config, protocol = read_config()
    binding = verify_binding(root)
    study = Study(root, models, config["scope"])
    runtime_record, controller = runtime()
    data.write_json(
        root / "diagnostics" / (stage.replace("/", "--") + "-runtime.json"),
        runtime_record,
    )
    study.event(
        "worker_started", stage=stage, pid=os.getpid(), binding_sha256=binding["sha256"]
    )
    if stage == "acquire":
        acquire(root, protocol, config)
    elif stage == "prepare-v2":
        accepted = json.loads((root / "private/acquisition.json").read_text())
        for source in accepted["sources"]:
            if data.digest(root / "raw" / source["filename"]) != source["sha256"]:
                raise ValueError(
                    "accepted source changed before structural preparation"
                )
        prepare(
            study,
            {s["role"]: root / "raw" / s["filename"] for s in protocol["sources"]},
        )
    elif stage == "calibrate":
        install_phase_guard(study, "calibrate")
        calibrate(study)
    elif stage == "freeze":
        install_phase_guard(study, "freeze")
        symmetry(study)
        freeze(study, binding, runtime_record, config, revision=1)
    elif stage == "seal-v2":
        install_phase_guard(study, "freeze")
        prior = json.loads((root / "private/complete-freeze.json").read_text())
        for name in (
            "calibration.json",
            "development-symmetry.json",
            "scaler.json",
            "roles.json",
            "precalibration-matrix.json",
        ):
            path = root / "private" / name
            if data.digest(path) != prior["files"][str(path)]:
                raise ValueError("reused scientific evidence changed")
        freeze(study, binding, runtime_record, config, revision=2)
    else:
        install_phase_guard(study, "train")
        arm, seed = stage.split("/")
        fit_stream(study, arm, seed)
    study.event(
        "worker_completed", stage=stage, lifetime_peak_RSS_bytes=lifetime_rss_bytes()
    )
    controller.restore_original_limits()


def freeze(study, binding, runtime_record, config, revision=2):
    from raregate.research.decisive_adc import data
    from raregate.research.decisive_adc.study import fit_matrix_manifest

    if binding["scope"] != study.scope:
        raise PermissionError("freeze binding scope mismatch")
    real = study.scope == "Task0061-real-ADC-preparation-only"
    files = {}
    acquisition = study.root / "private/acquisition.json"
    if real:
        for source in json.loads(acquisition.read_text())["sources"]:
            files[str(study.root / "raw" / source["filename"])] = source["sha256"]
        preparation_identity = json.loads(
            (study.root / "private/preparation-identity.json").read_text()
        )
        files[preparation_identity["group_database_path"]] = preparation_identity[
            "group_database_sha256"
        ]
    # Bind sealed roles from structural receipts; do not reopen final payloads here.
    roles = json.loads((study.root / "private/roles.json").read_text())
    for role, record in roles.items():
        for name, value in record["files"].items():
            files[str(study.root / "prepared" / role / name)] = value
    for path in (
        list((study.root / "private").glob("*.json"))
        + list(study.models.rglob("*"))
        + list((study.root / "diagnostics").glob("*-runtime.json"))
        + list((study.root / "ledger").glob("*.json"))
        + list((study.root / "private").glob("calibration-*.npy"))
    ):
        if path.is_file() and path.name != "active.json":
            files[str(path)] = data.digest(path)
    manifest = dict(
        schema_version=2,
        seal_revision=revision,
        status="complete_freeze" if real else "generated_complete_freeze_not_a_permit",
        ready_for_Task0062=real,
        final_evaluation_performed=False,
        Task0062_started=False,
        operational_readiness=False,
        scope=study.scope,
        implementation_binding=binding,
        roles=roles,
        models=fit_matrix_manifest(study),
        calibration=json.loads((study.root / "private/calibration.json").read_text()),
        runtime=runtime_record,
        files=files,
        canonical_batch=32,
        tail="zero-pad32 retain actual rows",
        schedule=config["development_schedule"],
        statistics_protocol_sha256=config["protocol_sha256"],
        future_preflight="Verify bound code/config/runtime and all manifest file identities without scoring; record fresh human Task0062 scope and exclusive unblinding intent BEFORE final scoring. This entrypoint cannot evaluate.",
    )
    basename = "complete-freeze" if revision == 1 else "complete-freeze-v2"
    target = study.root / "private" / (basename + ".json")
    data.write_json(target, manifest)
    data.write_json(
        study.root / "private" / (basename + "-identity.json"),
        dict(
            bytes=target.stat().st_size,
            sha256=data.digest(target),
        ),
    )
    target.chmod(0o444)


def observe_process(process, root, models, started, phase_cap, task_start):
    peak_storage = owned_bytes(root, models)
    peak_rss = 0
    reason = None
    while process.poll() is None:
        observed = owned_bytes(root, models)
        peak_storage = max(peak_storage, observed)
        query = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(process.pid)],
            capture_output=True,
            text=True,
            check=False,
        )
        rss = int(query.stdout.strip() or 0) * 1024
        peak_rss = max(peak_rss, rss)
        inclusive = (datetime.now(UTC) - task_start).total_seconds()
        if (
            observed > 8589934592
            or rss > 4294967296
            or time.monotonic() - started > phase_cap - 10
            or inclusive > 14400 - 10
        ):
            reason = "storage/RSS/phase/task resource stop"
            break
        time.sleep(0.25)
    return reason, peak_storage, peak_rss


def reap(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=3)


def run(stage, root, models, config):
    from raregate.research.decisive_adc.data import write_json
    from raregate.research.decisive_adc.execution import (
        behavioral_bundle,
        binding_digest,
        log,
        verify_binding,
    )

    if stage == "bind":
        receipt = json.loads((root / "private/generated-validation.json").read_text())
        bundle = behavioral_bundle()
        if (
            receipt["bundle_sha256"] != binding_digest(bundle)
            or receipt["returncode"] != 0
        ):
            raise ValueError("final-source generated validation missing")
        write_json(
            root / "private/implementation-binding.json",
            dict(
                bundle=bundle,
                sha256=binding_digest(bundle),
                generated_validation_passed=True,
                scope=config["scope"],
                validation=receipt,
            ),
        )
        for name in bundle:
            target = root / "snapshots" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        return
    verify_binding(root)
    order = config["stage_order"]
    for prior in order[: order.index(stage)]:
        receipt = json.loads(
            (root / "ledger" / (prior.replace("/", "--") + ".result.json")).read_text()
        )
        if not receipt["accepted"]:
            raise ValueError("prior incomplete stage; no continuation")
    intent = root / "ledger" / (stage.replace("/", "--") + ".intent.json")
    if intent.exists():
        raise FileExistsError(
            "exclusive stage intent already exists; inspect ledger, never repeat"
        )
    lock = root / "ledger/active.json"
    with lock.open("x") as stream:
        json.dump(
            dict(
                parent_pid=os.getpid(),
                stage=stage,
                created=datetime.now(UTC).isoformat(),
            ),
            stream,
        )
    started = time.monotonic()
    wall_started = datetime.now(UTC)
    write_json(
        intent,
        dict(
            stage=stage,
            utc=wall_started.isoformat(),
            parent_pid=os.getpid(),
            scope=config["scope"],
            attempt=1,
        ),
    )
    log(root, "stage_intent", stage=stage, attempt=1)
    phase_cap = {
        "acquire": 2700,
        "prepare": 1800,
        "calibrate": 1800,
        "freeze": 600,
    }.get(stage, 1200)
    if stage == "prepare-v2":
        phase_cap = (
            1800
            - (
                datetime.now(UTC)
                - datetime.fromisoformat(config["preparation_started_utc"])
            ).total_seconds()
        )
    task_start = datetime.fromisoformat(config["task_started_utc"])
    process = None
    reason = None
    peak_storage = owned_bytes(root, models)
    peak_rss = 0
    try:
        if (wall_started - task_start).total_seconds() > 14400 - 10:
            raise TimeoutError("inclusive task wall budget exhausted")
        with (root / "diagnostics" / (stage.replace("/", "--") + ".log")).open(
            "x"
        ) as output:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-B",
                    str(Path(__file__).resolve()),
                    "--worker",
                    stage,
                ],
                cwd=ROOT,
                env=dict(os.environ),
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            write_json(
                root / "ledger" / (stage.replace("/", "--") + ".pid.json"),
                dict(pid=process.pid, parent_pid=os.getpid(), stage=stage),
            )
            reason, peak_storage, peak_rss = observe_process(
                process, root, models, started, phase_cap, task_start
            )
    except BaseException as error:
        reason = "supervisor exception: " + repr(error)
    finally:
        if process is not None:
            reap(process)
        peak_storage = max(peak_storage, owned_bytes(root, models))
        accepted = process is not None and process.returncode == 0 and reason is None
        elapsed = time.monotonic() - started
        result = dict(
            stage=stage,
            accepted=accepted,
            returncode=None if process is None else process.returncode,
            stop_reason=reason,
            elapsed_inclusive_seconds=elapsed,
            task_elapsed_seconds=(datetime.now(UTC) - task_start).total_seconds(),
            peak_observed_study_bytes=peak_storage,
            peak_sampled_worker_RSS_bytes=peak_rss,
            worker_reaped=process is None or process.poll() is not None,
            ended_utc=datetime.now(UTC).isoformat(),
        )
        write_json(
            root / "ledger" / (stage.replace("/", "--") + ".result.json"), result
        )
        log(root, "stage_result", **result)
        lock.unlink()
        print(json.dumps(result, indent=2))
    if not accepted:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=[
            "bind",
            "acquire",
            "prepare-v2",
            "compactAE/1729",
            "referenceAE/1729",
            "compactAE/1730",
            "referenceAE/1730",
            "compactAE/1731",
            "referenceAE/1731",
            "PCA3/fit",
            "regularizedMahalanobis/fit",
            "calibrate",
            "freeze",
            "seal-v2",
        ],
    )
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--supervise", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.stage is None and args.worker is None and args.supervise is None:
        parser.error("an explicit Task0061 phase is required")
    config = json.loads(CONFIG.read_text())
    root, models = ROOT / config["study_path"], ROOT / config["models_path"]
    if (
        root.resolve() != root
        or models.resolve() != models
        or not (root / "owner.json").is_file()
    ):
        raise ValueError("owned layout missing/aliased")
    configure(root)
    if args.worker:
        # Private dispatch needs the persisted parent intent; not a standalone permit.
        lock = json.loads((root / "ledger/active.json").read_text())
        if lock["stage"] != args.worker or lock["parent_pid"] != os.getppid():
            raise PermissionError("worker requires live stage parent")
        worker(args.worker, root, models)
    elif args.supervise:
        if args.supervise not in config["stage_order"]:
            raise PermissionError("undeclared stage")
        run(args.supervise, root, models, config)
    elif args.stage == "bind":
        run(args.stage, root, models, config)
    else:
        outer(args.stage, root, models, config)


def outer(stage, root, models, config):
    """Observe the entire supervisor including its reporting, exit and reaping."""
    if (root / "ledger/active.json").exists():
        raise RuntimeError(
            "active owner exists; inspect own PID/ledger before any action"
        )
    key = stage.replace("/", "--")
    started = time.monotonic()
    cap = {"acquire": 2700, "prepare": 1800, "calibrate": 1800, "freeze": 600}.get(
        stage, 1200
    )
    if stage == "prepare-v2":
        cap = (
            1800
            - (
                datetime.now(UTC)
                - datetime.fromisoformat(config["preparation_started_utc"])
            ).total_seconds()
        )
    with (root / "ledger" / (key + ".outer-intent.json")).open("x") as output:
        json.dump(
            dict(stage=stage, utc=datetime.now(UTC).isoformat(), pid=os.getpid()),
            output,
        )
        output.flush()
        os.fsync(output.fileno())
    process = subprocess.Popen(
        [sys.executable, "-B", str(Path(__file__).resolve()), "--supervise", stage],
        env=dict(os.environ),
        start_new_session=True,
    )
    reason = None
    try:
        while process.poll() is None:
            elapsed = time.monotonic() - started
            inclusive = (
                datetime.now(UTC) - datetime.fromisoformat(config["task_started_utc"])
            ).total_seconds()
            if (
                elapsed > cap
                or inclusive > 14400 - 10
                or owned_bytes(root, models) > 8589934592
            ):
                reason = "outer inclusive resource stop"
                break
            time.sleep(0.25)
    finally:
        if process.poll() is None:
            pid_path = root / "ledger" / (key + ".pid.json")
            if pid_path.exists():
                worker_pid = json.loads(pid_path.read_text())["pid"]
                query = subprocess.run(
                    ["ps", "-o", "command=", "-p", str(worker_pid)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if str(Path(__file__).resolve()) + " --worker " + stage in query.stdout:
                    try:
                        os.killpg(worker_pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
            reap(process)
        record = dict(
            stage=stage,
            supervisor_returncode=process.returncode,
            stop_reason=reason,
            supervisor_reaped=True,
            elapsed_including_supervisor_reporting_exit_reap=time.monotonic() - started,
            task_elapsed_seconds=(
                datetime.now(UTC) - datetime.fromisoformat(config["task_started_utc"])
            ).total_seconds(),
            study_bytes_at_exit=owned_bytes(root, models),
            observer_finalization_reserve_seconds=10,
        )
        with (root / "diagnostics" / (key + "-outer.json")).open("x") as output:
            json.dump(record, output, indent=2)
            output.write("\n")
        print(json.dumps(record, indent=2))
    if process.returncode != 0 or reason:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
