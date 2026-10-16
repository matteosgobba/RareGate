"""Task0062 exclusive evaluator. Import/help are inactive and open no payload."""

import argparse
import json
import os
import resource
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNED = ROOT / "data/decisive-v2-adc-task0062"
CONFIG = ROOT / "configs/research/decisive_adc_evaluation_v2.json"


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


def storage():
    total = 0
    bases = [
        ROOT / "data/decisive-v2-adc-task0061",
        OWNED,
        ROOT / "artifacts/models/decisive-v2-adc",
    ]
    for base in bases:
        for directory, folders, files in os.walk(base, followlinks=False):
            for name in folders + files:
                p = Path(directory) / name
                if p.is_symlink() and not any(
                    p.is_relative_to(b / "tests")
                    and p.resolve().is_relative_to(b / "tests")
                    for b in bases[:2]
                ):
                    raise ValueError("owned alias")
            total += sum((Path(directory) / f).lstat().st_size for f in files)
    for folder in ("results/tables/final", "results/figures/final"):
        total += sum(
            p.stat().st_size
            for p in (ROOT / folder).glob("task006[12]-*")
            if p.is_file()
        )
    for p in [
        ROOT / "src/raregate/research/decisive_adc_evaluation.py",
        Path(__file__),
        ROOT / "tests/test_decisive_adc_evaluation.py",
        CONFIG,
    ]:
        total += p.stat().st_size if p.exists() else 0
    total += sum(
        p.stat().st_size for p in (ROOT / "docs").rglob("*.md")
    )  # Conservative shared documentation charge.
    return total


def dump(path, value):
    with path.open("x") as out:
        json.dump(value, out, indent=2, allow_nan=False)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())


def reap(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
    else:
        process.wait()


def observe(command, folder, cap, config):
    started = time.monotonic()
    reason = None
    peak_rss = peak_storage = 0
    with (folder / "output.log").open("x") as out:
        p = subprocess.Popen(
            command,
            env=dict(os.environ),
            cwd=ROOT,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        dump(
            folder / "pid.json",
            dict(
                pid=p.pid,
                parent_pid=os.getpid(),
                start_utc=datetime.now(UTC).isoformat(),
            ),
        )
        try:
            with (folder / "observations.jsonl").open("x") as observations:
                while p.poll() is None:
                    used = storage()
                    query = subprocess.run(
                        ["ps", "-o", "rss=", "-p", str(p.pid)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if query.returncode and "not permitted" in query.stderr.lower():
                        raise RuntimeError("own PID RSS denied")
                    rss = int(query.stdout.strip() or 0) * 1024
                    peak_rss = max(rss, peak_rss)
                    peak_storage = max(used, peak_storage)
                    elapsed = (
                        datetime.now(UTC)
                        - datetime.fromisoformat(config["task_start_utc"])
                    ).total_seconds()
                    observations.write(
                        json.dumps(
                            dict(
                                utc=datetime.now(UTC).isoformat(),
                                rss_bytes=rss,
                                study_bytes=used,
                                phase_elapsed=time.monotonic() - started,
                                task_elapsed=elapsed,
                            )
                        )
                        + "\n"
                    )
                    observations.flush()
                    if (
                        used > config["study_storage_bytes"]
                        or rss > config["worker_rss_bytes"]
                        or time.monotonic() - started
                        > cap - config["cleanup_reserve_seconds"]
                        or elapsed
                        > config["task_seconds"] - config["cleanup_reserve_seconds"]
                    ):
                        reason = "observed storage/RSS/phase/task stop"
                        break
                    time.sleep(0.5)
        except BaseException as error:
            reason = repr(error)
        finally:
            reap(p)
    result = dict(
        returncode=p.returncode,
        stop_reason=reason,
        elapsed_including_import_reporting_exit_reap=time.monotonic() - started,
        peak_sampled_worker_RSS_bytes=peak_rss,
        peak_observed_study_bytes=peak_storage,
        worker_reaped=True,
        task_elapsed_inclusive=(
            datetime.now(UTC) - datetime.fromisoformat(config["task_start_utc"])
        ).total_seconds(),
        end_utc=datetime.now(UTC).isoformat(),
        sampling_limit="own pid and logical retained files; not OS all-write or native/unlinked scratch proof",
    )
    dump(folder / "outer-result.json", result)
    return result


def validation(attempt, config):
    folder = OWNED / "tests" / f"validation-{attempt}"
    folder.mkdir(exist_ok=False)
    (folder / "tmp").mkdir()
    configure(folder)
    os.environ["RAREGATE_ADC_TEST_ROOT"] = str(folder)
    os.environ["RAREGATE_AUDIT_OWNED_ROOT"] = str(folder)
    from raregate.research.decisive_adc.execution import binding_digest
    from raregate.research.decisive_adc_evaluation import extension_bundle

    bundle = extension_bundle(config)
    import shutil

    for name in bundle:
        target = folder / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    dump(folder / "bundle.json", bundle)
    command = [
        sys.executable,
        "-B",
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "-p",
        "tests.decisive_adc_plugin",
        "--basetemp",
        str(folder / "fixtures"),
        "--junitxml",
        str(folder / "junit.xml"),
        "-q",
    ]
    command += [
        f"tests/test_{n}.py"
        for n in (
            "decisive_adc_evaluation",
            "decisive_adc",
            "evaluation",
            "splitting",
            "inspection",
            "features",
            "pca",
            "autoencoder",
            "scientific_audit",
        )
    ]
    result = observe(command, folder, 240, config)
    print((folder / "output.log").read_text()[-14000:])
    print(json.dumps(result))
    if result["returncode"] == 0 and result["stop_reason"] is None:
        if bundle != extension_bundle(config):
            raise ValueError("source changed during validation")
        binding = dict(
            generated_validation_passed=True,
            bundle=bundle,
            sha256=binding_digest(bundle),
            prompt_sha256=bundle[config["prompt_path"]],
            validation=str(folder.relative_to(ROOT)),
            result=result,
        )
        dump(folder / "accepted-binding.json", binding)
    return result


def worker(phase, config):
    from raregate.research import decisive_adc_evaluation as e
    from raregate.research.decisive_adc import data, models
    from raregate.research.decisive_adc.execution import runtime

    binding = e.qualify_binding(OWNED, config)
    intent = e.read(OWNED / "ledger" / f"{phase}-intent.json")
    if (
        intent["binding_sha256"] != binding["sha256"]
        or intent["freeze_sha256"] != config["freeze_sha256"]
        or intent["phase"] != phase
    ):
        raise PermissionError("exclusive phase intent binding")
    rt, controller = runtime()
    dump(OWNED / "diagnostics" / f"{phase}-runtime.json", rt)
    freeze = e.read(ROOT / config["freeze_path"])
    action = config.get("phase_actions", {}).get(phase, phase)
    if action in ("preflight", "postflight"):
        freeze, verification = e.verify_freeze(config, rt)
        result = dict(
            verification=verification,
            runtime=rt,
            binding_sha256=binding["sha256"],
            utc=e.utc(),
        )
    else:
        if e.normalize_runtime(rt) != e.normalize_runtime(freeze["runtime"]):
            raise ValueError("runtime changed")
        context = e.EvaluationContext(
            OWNED, ROOT / config["input_root"], freeze, config, binding
        )
        e.install_guard(context, action)
        if action == "development":
            loaded, values, qualifications = e.parity(
                context, ROOT / config["models_root"]
            )
            dump(
                OWNED / "ledger/cpu-measurement-intent.json",
                dict(
                    utc=e.utc(),
                    binding_sha256=binding["sha256"],
                    runtime=rt,
                    schedule=config["cpu"],
                    parity_sha256=data.digest(OWNED / "private/parity.json"),
                ),
            )
            cpu = e.cpu_measure(context, loaded, values, qualifications)
            result = dict(
                parity_passed=True,
                qualified_shapes=qualifications,
                cpu_cells=len(cpu["rows"]),
                skipped_cells=len(cpu["skipped"]),
                cpu_seconds=cpu["elapsed_seconds"],
            )
        else:
            if (
                action != "final"
                or not e.read(
                    OWNED
                    / "ledger"
                    / (config["required_development_phase"] + "-result.json")
                )["valid"]
            ):
                raise PermissionError("development qualification first")
            loaded = {
                f"{a}--{s}": models.load_model(ROOT / config["models_root"] / a / s)
                for a, s in models.STREAMS
            }
            e.TALLY["model_loads"] += len(loaded)
            context.unblind(rt)
            receipts = []
            for role in ("final_background", *e.SIGNALS):
                values = context.role(role)
                for arm, seed in models.STREAMS:
                    receipts.append(
                        e.commit_scores(
                            context, role, arm, seed, loaded[f"{arm}--{seed}"], values
                        )
                    )
            dump(
                OWNED / "private/score-pass.json",
                dict(
                    receipts=receipts,
                    score_rows=sum(r["N"] for r in receipts),
                    public_calls=sum(r["calls"] for r in receipts),
                    padded_rows=sum(r["padded"] for r in receipts),
                ),
            )
            robustness = e.robustness(context, loaded)
            e.bias_profiles(context)
            analysis = e.analyze(context, e.read(OWNED / "private/cpu.json"))
            result = dict(
                score_rows=sum(r["N"] for r in receipts),
                public_calls=sum(r["calls"] for r in receipts),
                robustness=robustness,
                decision=analysis["decision"],
            )
    result.update(
        valid=True,
        lifetime_peak_RSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        work=e.TALLY,
    )
    dump(OWNED / "ledger" / f"{phase}-result.json", result)
    controller.restore_original_limits()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "phase",
        choices=(
            "validate",
            "preflight",
            "development",
            "preflight-v2",
            "development-v2",
            "final",
            "postflight",
        ),
    )
    parser.add_argument("--attempt", type=int)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    configure(OWNED)
    if args.phase == "validate":
        if args.attempt is None:
            parser.error("validation attempt required")
        r = validation(args.attempt, config)
        raise SystemExit(r["returncode"] or bool(r["stop_reason"]))
    if args.worker:
        try:
            worker(args.phase, config)
        except BaseException as error:
            dump(
                OWNED / "ledger" / f"{args.phase}-failure.json",
                dict(
                    error=repr(error),
                    utc=datetime.now(UTC).isoformat(),
                    lifetime_peak_RSS_bytes=resource.getrusage(
                        resource.RUSAGE_SELF
                    ).ru_maxrss,
                ),
            )
            raise
        return
    from raregate.research.decisive_adc_evaluation import qualify_binding

    binding = qualify_binding(OWNED, config)
    # No repeat: phase intent remains on every exit, even before numerical work.
    folder = OWNED / "diagnostics" / args.phase
    folder.mkdir(exist_ok=False)
    dump(
        OWNED / "ledger" / f"{args.phase}-intent.json",
        dict(
            task="Task0062",
            scope=config["scope"],
            binding_sha256=binding["sha256"],
            freeze_sha256=config["freeze_sha256"],
            utc=datetime.now(UTC).isoformat(),
            phase=args.phase,
            pid=os.getpid(),
        ),
    )
    cap = (
        1200
        if args.phase in ("development", "development-v2")
        else (1800 if args.phase == "final" else 300)
    )
    result = observe(
        [sys.executable, "-B", str(Path(__file__).resolve()), args.phase, "--worker"],
        folder,
        cap,
        config,
    )
    print((folder / "output.log").read_text()[-5000:])
    print(json.dumps(result))
    raise SystemExit(result["returncode"] or bool(result["stop_reason"]))


if __name__ == "__main__":
    main()
