"""Task0062 extension. Frozen ADC numerics are imported, never modified.

No import-time IO/activation. Real context requires the prompt-bound qualification,
closed freeze verification and exclusive phase intent. Generated contexts cannot
resolve production roots. These are application controls, not an OS sandbox.
"""

import itertools
import json
import math
import os
import resource
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from scipy.stats import norm

from .decisive_adc import data, models
from .decisive_adc import statistics as stats
from .decisive_adc.execution import binding_digest

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "configs/research/decisive_adc_evaluation_v2.json"
SCOPE = "Task0062-explicit-human-authorized"
ARMS = ("compactAE", "referenceAE", "PCA3", "regularizedMahalanobis")
SIGNALS = ("A_to_4l", "LQ_to_btau")
RATES = (0.01, 0.001)
TALLY = dict(
    public_calls=0,
    public_rows=0,
    reconstruction_calls=0,
    reconstruction_rows=0,
    model_loads=0,
)


def utc():
    return datetime.now(UTC).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def no_alias(path):
    path = Path(path).absolute()
    if path.resolve() != path:
        raise ValueError(f"aliased input/output: {path}")
    return path


def extension_bundle(config):
    return {
        name: data.digest(no_alias(ROOT / name)) for name in config["extension_paths"]
    }


def verify_map(mapping, base=None):
    total = 0
    for name, expected in mapping.items():
        path = no_alias(Path(base) / name if base is not None else name)
        if not path.is_file() or data.digest(path) != expected:
            raise ValueError(f"bound input mismatch: {name}")
        total += path.stat().st_size
    return dict(files=len(mapping), bytes=total)


def normalize_runtime(record):
    record = dict(record)
    record["threadpools"] = sorted(
        record["threadpools"], key=lambda p: json.dumps(p, sort_keys=True)
    )
    return record


def verify_freeze(config, runtime_record):
    path = no_alias(ROOT / config["freeze_path"])
    if (
        path.stat().st_size != config["freeze_bytes"]
        or data.digest(path) != config["freeze_sha256"]
    ):
        raise ValueError("accepted revision2 freeze identity")
    freeze = read(path)
    for name, identity in config["immutable_anchors"].items():
        anchor = no_alias(ROOT / name)
        if (
            anchor.stat().st_size != identity["bytes"]
            or data.digest(anchor) != identity["sha256"]
        ):
            raise ValueError(f"immutable anchor mismatch: {name}")
    if (
        freeze["seal_revision"] != 2
        or not freeze["ready_for_Task0062"]
        or len(freeze["files"]) != 184
    ):
        raise ValueError("freeze revision/count/readiness")
    files = verify_map(freeze["files"])
    closed = freeze["implementation_binding"]
    code = verify_map(closed["bundle"], ROOT)
    if binding_digest(closed["bundle"]) != closed["sha256"]:
        raise ValueError("closed behavioral binding digest")
    if normalize_runtime(runtime_record) != normalize_runtime(freeze["runtime"]):
        differences = [
            k
            for k in runtime_record
            if normalize_runtime(runtime_record)[k]
            != normalize_runtime(freeze["runtime"])[k]
        ]
        raise ValueError(f"substantive runtime mismatch: {differences}")
    return freeze, dict(retained_files=files, closed_behavior=code, runtime_equal=True)


def qualify_binding(root, config):
    record = read(root / config.get("binding_path", "private/extension-binding.json"))
    if not record["generated_validation_passed"] or record[
        "bundle"
    ] != extension_bundle(config):
        raise PermissionError("current generated source qualification required")
    if record["sha256"] != binding_digest(record["bundle"]) or record[
        "prompt_sha256"
    ] != data.digest(ROOT / config["prompt_path"]):
        raise PermissionError("prompt/source binding")
    return record


class EvaluationContext:
    def __init__(
        self, output, input_root, freeze, config, binding=None, generated=False
    ):
        self.output, self.input_root = no_alias(output), no_alias(input_root)
        self.freeze, self.config, self.generated = freeze, config, generated
        if generated:
            if self.input_root.is_relative_to(
                ROOT / "data/decisive-v2-adc-task0061"
            ) or self.output == ROOT / config.get(
                "root", "data/decisive-v2-adc-task0062"
            ):
                raise PermissionError("generated context cannot reach production")
            self.counts = {
                r: freeze["roles"][r]["rows"] for r in ("final_background", *SIGNALS)
            }
            if max(self.counts.values()) > 256:
                raise PermissionError("generated counts")
        else:
            if (
                config.get("scope") != SCOPE
                or config.get("task") != "Task0062"
                or self.output != ROOT / config["root"]
                or self.input_root != ROOT / config["input_root"]
            ):
                raise PermissionError("Task0062 exact owner/root/scope")
            current = qualify_binding(self.output, config)
            if (
                binding != current
                or not (
                    self.output
                    / "ledger"
                    / (
                        config.get("required_preflight_phase", "preflight")
                        + "-result.json"
                    )
                ).is_file()
            ):
                raise PermissionError("accepted preflight/binding required")
            preflight = read(
                self.output
                / "ledger"
                / (config.get("required_preflight_phase", "preflight") + "-result.json")
            )
            if (
                not preflight["valid"]
                or preflight["binding_sha256"] != current["sha256"]
            ):
                raise PermissionError("preflight validity/source identity")
            self.counts = config["roles"]
        self.authorized_final = False

    def unblind(self, runtime_record):
        intent = dict(
            schema_version=2,
            scope="generated-evaluation-only" if self.generated else SCOPE,
            utc=utc(),
            freeze_sha256=self.config.get("freeze_sha256"),
            extension_sha256=None
            if self.generated
            else qualify_binding(self.output, self.config)["sha256"],
            prompt_sha256=None
            if self.generated
            else data.digest(ROOT / self.config["prompt_path"]),
            runtime=runtime_record,
            roles=self.counts,
            streams=models.STREAMS,
            cuts=self.freeze["calibration"],
            output_plan=self.config.get("output_plan"),
        )
        data.write_json(self.output / "ledger/final-unblinding-intent.json", intent)
        self.authorized_final = True

    def role(self, role, kind="features"):
        allowed = ("development", "final_background", *SIGNALS)
        if role not in allowed or kind not in ("features", "objects"):
            raise PermissionError("role/kind denied")
        if role != "development" and not self.authorized_final:
            raise PermissionError("final outcome access requires exclusive intent")
        manifest = self.freeze["roles"][role]
        expected = (
            self.config.get("development_rows", 4096)
            if role == "development"
            else self.counts[role]
        )
        if (
            manifest["role"] != role
            or manifest["rows"] != expected
            or manifest["scaler_sha256"]
            != self.freeze["roles"]["development"]["scaler_sha256"]
        ):
            raise ValueError("role/source/count/scaler mismatch")
        source = (
            "train-first-hash-ordered"
            if role == "development"
            else ("background" if role == "final_background" else role)
        )
        if manifest["source"] != source:
            raise ValueError("role source mismatch")
        path = no_alias(self.input_root / "prepared" / role / f"{kind}.npy")
        # Full hashes were checked by preflight; recheck payload identity at role open.
        if data.digest(path) != manifest["files"][f"{kind}.npy"]:
            raise ValueError("role payload mismatch")
        array = np.load(path, mmap_mode="r", allow_pickle=False)
        shape, dtype = (
            ((expected, 12), np.float32)
            if kind == "features"
            else ((expected, 19, 4), np.float64)
        )
        if array.shape != shape or array.dtype != dtype or array.flags.writeable:
            raise ValueError("sealed role shape/dtype/mode")
        return array


def install_guard(context, phase):
    """Supplementary Python IO policy; explicit path checks also cover native reads."""
    permitted = (
        {"development"}
        if phase == "development"
        else {"development", "final_background", *SIGNALS}
    )
    old = context.input_root

    def guard(event, args):
        if event == "sqlite3.connect":
            raise PermissionError("no all-role grouping database in evaluation")
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).absolute().resolve()
        mode, flags = args[1:3]
        write = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int)
            and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        )
        if (
            write
            and path.is_relative_to(ROOT)
            and not path.is_relative_to(context.output)
        ):
            raise PermissionError("read-only frozen context / owned output only")
        if path.is_relative_to(old):
            relative = path.relative_to(old)
            if relative.parts[0] == "prepared" and len(relative.parts) > 1:
                if relative.parts[1] not in permitted or (
                    relative.parts[1] != "development" and not context.authorized_final
                ):
                    raise PermissionError("phase role denial")
            elif relative.parts[0] != "private" or relative.name not in (
                "complete-freeze-v2.json",
                "scaler.json",
            ):
                raise PermissionError("raw/calibration/unused/old ledger denied")

    sys.addaudithook(guard)


def public(model, x):
    out = models.public_score(model, x)
    TALLY["public_calls"] += 1
    TALLY["public_rows"] += len(x)
    if (
        out.dtype != np.float64
        or out.shape != (len(x),)
        or not out.flags.owndata
        or not np.isfinite(out).all()
        or np.any(out < 0)
    ):
        raise ValueError("public score ownership/shape/finite/direction")
    return out


def score_shape(model, values, batch):
    result = np.empty(len(values), dtype=np.float64)
    for start in range(0, len(values), batch):
        n = min(batch, len(values) - start)
        x = np.zeros((batch, 12), dtype=np.float32)
        x[:n] = values[start : start + n]
        result[start : start + n] = public(model, x)[:n]
    return result


def reconstruction(model, values, batch):
    if isinstance(model, dict) and model["arm"] == "regularizedMahalanobis":
        return None
    result = np.empty((len(values), 12), dtype=np.float64)
    for start in range(0, len(values), batch):
        n = min(batch, len(values) - start)
        x = np.zeros((batch, 12), dtype=np.float32)
        x[:n] = values[start : start + n]
        if isinstance(model, models.ADCNet):
            with torch.inference_mode():
                y = model(torch.from_numpy(x)).numpy().astype(np.float64)
        else:
            centered = x.astype(np.float64) - model["mean"]
            y = centered @ model["components"].T @ model["components"] + model["mean"]
        result[start : start + n] = y[:n]
        TALLY["reconstruction_calls"] += 1
        TALLY["reconstruction_rows"] += batch
    return result


def score_allowance(reference):
    return 1e-5 + 2e-5 * np.maximum(1, np.abs(reference))


def cut_rows(freeze, arm, seed):
    rows = [c for c in freeze["calibration"] if c["arm"] == arm and c["seed"] == seed]
    if [c["alpha"] for c in rows] != list(RATES):
        raise ValueError("stream calibration identities/order")
    return rows


def parity(context, model_root):
    values = np.array(context.role("development"), copy=True)
    rows, loaded, refs = [], {}, {}
    before = dict(TALLY)
    for arm, seed in models.STREAMS:
        key = f"{arm}--{seed}"
        model = models.load_model(model_root / arm / seed)
        reload = models.load_model(model_root / arm / seed)
        TALLY["model_loads"] += 2
        reference = score_shape(model, values, 32)
        repeat = score_shape(model, values, 32)
        restored = score_shape(reload, values, 32)
        if not np.array_equal(reference, repeat) or not np.array_equal(
            reference, restored
        ):
            raise ValueError("required B32 reload/repeat failure")
        frozen_scores = np.load(
            model_root / arm / seed / "development_scores.npy", allow_pickle=False
        )
        if not np.array_equal(reference, frozen_scores):
            raise ValueError("required B32 frozen development identity")
        r32 = reconstruction(model, values, 32)
        cuts = np.array([c["threshold"] for c in cut_rows(context.freeze, arm, seed)])
        for batch in (1, 32, 512):
            scores = reference if batch == 32 else score_shape(model, values, batch)
            rec = r32 if batch == 32 else reconstruction(model, values, batch)
            rec_ok = rec is None or bool(
                np.all(np.abs(rec - r32) <= score_allowance(r32))
            )
            score_ok = bool(
                np.all(np.abs(scores - reference) <= score_allowance(reference))
            )
            flips = (scores[:, None] > cuts) != (reference[:, None] > cuts)
            rows.append(
                dict(
                    arm=arm,
                    seed=seed,
                    batch=batch,
                    qualified=score_ok and rec_ok,
                    score_max_abs=float(np.max(np.abs(scores - reference))),
                    score_min_remaining_allowance=float(
                        np.min(score_allowance(reference) - np.abs(scores - reference))
                    ),
                    reconstruction_applicable=rec is not None,
                    reconstruction_max_abs=None
                    if rec is None
                    else float(np.max(np.abs(rec - r32))),
                    decision_changes=flips.sum(axis=0).tolist(),
                )
            )
            if np.any(flips):
                np.savez(
                    context.output / "private" / f"parity-margins-{key}-B{batch}.npz",
                    reference=reference,
                    scores=scores,
                    margins=reference[:, None] - cuts,
                    changes=flips,
                )
        loaded[key], refs[key] = model, reference
    result = dict(rows=rows, work={k: TALLY[k] - before[k] for k in TALLY})
    data.write_json(context.output / "private/parity.json", result)
    return loaded, values, rows


def boundary(model, values, objects, scaler, thresholds, name):
    x = data.transform(data.features(objects), scaler) if name == "joint" else values
    scores = models.public_score(model, x)
    masks = (scores > thresholds[0], scores > thresholds[1])
    return scores, masks


def cpu_measure(context, loaded, values, qualifications):
    objects = np.array(context.role("development", "objects"), copy=True)
    scaler = read(context.input_root / "private/scaler.json")
    qualified = {
        (r["arm"], r["seed"], r["batch"]): r["qualified"] for r in qualifications
    }
    rows, skipped, before = [], [], dict(TALLY)
    started = time.monotonic()
    with (context.output / "private/timings.jsonl").open("x") as trace:
        for rep in range(8):
            order = models.STREAMS[rep:] + models.STREAMS[:rep]
            for arm, seed in order:
                for batch in (1, 32, 512):
                    for name in (
                        ("algorithm", "joint")
                        if rep % 2 == 0
                        else ("joint", "algorithm")
                    ):
                        if not qualified[arm, seed, batch]:
                            skipped.append(
                                dict(
                                    repetition=rep,
                                    arm=arm,
                                    seed=seed,
                                    batch=batch,
                                    boundary=name,
                                    reason="secondary shape unqualified",
                                )
                            )
                            continue
                        durations, warm = [], []
                        cell_cpu = time.process_time_ns()
                        thresholds = [
                            c["threshold"] for c in cut_rows(context.freeze, arm, seed)
                        ]
                        for call in range(160):
                            if (
                                time.monotonic() - started
                                > context.config.get("cpu_seconds", 1200) - 10
                            ):
                                raise TimeoutError("inclusive CPU phase reserve")
                            ix = stats.cpu_indices(rep, call, batch)
                            x = np.array(
                                values[ix], dtype=np.float32, copy=True, order="C"
                            )
                            obj = np.array(objects[ix], copy=True, order="C")
                            t0 = time.perf_counter_ns()
                            result = boundary(
                                loaded[f"{arm}--{seed}"],
                                x,
                                obj,
                                scaler,
                                thresholds,
                                name,
                            )
                            t1 = time.perf_counter_ns()
                            TALLY["public_calls"] += 1
                            TALLY["public_rows"] += batch
                            (warm if call < 32 else durations).append(t1 - t0)
                            # Output validity/consumption is outside clock; allocation and both masks are inside.
                            if any(
                                not z.flags.owndata for z in (result[0], *result[1])
                            ):
                                raise ValueError("timer output ownership")
                            trace.write(
                                json.dumps(
                                    dict(
                                        repetition=rep,
                                        arm=arm,
                                        seed=seed,
                                        batch=batch,
                                        boundary=name,
                                        call=call,
                                        warm=call < 32,
                                        t0_ns=t0,
                                        t1_ns=t1,
                                        duration_ns=t1 - t0,
                                    )
                                )
                                + "\n"
                            )
                        trace.flush()
                        rows.append(
                            dict(
                                repetition=rep,
                                arm=arm,
                                seed=seed,
                                batch=batch,
                                boundary=name,
                                warmups=32,
                                timed_calls=128,
                                mean_ns=float(np.mean(durations)),
                                min_ns=min(durations),
                                max_ns=max(durations),
                                cell_process_cpu_ns=time.process_time_ns() - cell_cpu,
                                lifetime_RSS_bytes=resource.getrusage(
                                    resource.RUSAGE_SELF
                                ).ru_maxrss,
                            )
                        )
        os.fsync(trace.fileno())
    result = dict(
        rows=rows,
        skipped=skipped,
        elapsed_seconds=time.monotonic() - started,
        work={k: TALLY[k] - before[k] for k in TALLY},
    )
    data.write_json(context.output / "private/cpu.json", result)
    return result


def commit_scores(context, role, arm, seed, model, values, interrupt_after=None):
    """One exclusive vector; NaN prefix initialization cannot masquerade as completion."""
    key = f"{role}--{arm}--{seed}"
    partial = context.output / "private" / f"{key}.npy.partial"
    final = context.output / "private" / f"{key}.npy"
    if final.exists() or partial.exists():
        raise FileExistsError("score vector attempt consumed")
    progress = context.output / "ledger" / f"score-{key}.jsonl"
    data.write_json(
        context.output / "ledger" / f"score-{key}-intent.json",
        dict(
            role=role,
            arm=arm,
            seed=seed,
            N=len(values),
            membership_sha256=context.freeze["roles"][role]["files"].get(
                "membership.npy"
            ),
            features_sha256=context.freeze["roles"][role]["files"]["features.npy"],
        ),
    )
    out = np.lib.format.open_memmap(
        partial, mode="w+", dtype=np.float64, shape=(len(values),)
    )
    out[:] = np.nan
    committed = calls = padded = 0
    with progress.open("x") as journal:
        try:
            for start in range(0, len(values), 32):
                n = min(32, len(values) - start)
                x = np.zeros((32, 12), dtype=np.float32)
                x[:n] = values[start : start + n]
                out[start : start + n] = public(model, x)[:n]
                committed += n
                calls += 1
                padded += 32 - n
                if calls % 1024 == 0 or committed == len(values):
                    out.flush()
                    journal.write(
                        json.dumps(
                            dict(
                                completed_rows=committed,
                                completed_calls=calls,
                                padded=padded,
                                maximum_unjournaled_calls=1023,
                                inflight_call_upper=1,
                            )
                        )
                        + "\n"
                    )
                    journal.flush()
                    os.fsync(journal.fileno())
                if interrupt_after is not None and committed >= interrupt_after:
                    raise InterruptedError("generated interruption")
            if not np.isfinite(out).all() or np.any(out < 0):
                raise ValueError("incomplete/nonfinite/negative vector")
            out.flush()
            out = None
            os.rename(partial, final)
            receipt = dict(
                role=role,
                arm=arm,
                seed=seed,
                N=committed,
                calls=calls,
                padded=padded,
                sha256=data.digest(final),
                bytes=final.stat().st_size,
                features_sha256=context.freeze["roles"][role]["files"]["features.npy"],
                membership_sha256=context.freeze["roles"][role]["files"].get(
                    "membership.npy"
                ),
            )
            data.write_json(context.output / "private" / f"{key}-commit.json", receipt)
            return receipt
        except BaseException:
            if out is not None:
                out.flush()
            journal.write(
                json.dumps(
                    dict(
                        failed=True,
                        completed_rows=committed,
                        completed_calls=calls,
                        padded=padded,
                    )
                )
                + "\n"
            )
            journal.flush()
            os.fsync(journal.fileno())
            raise


def load_scores(context, role, arm, seed):
    key = f"{role}--{arm}--{seed}"
    receipt = read(context.output / "private" / f"{key}-commit.json")
    path = context.output / "private" / f"{key}.npy"
    manifest = context.freeze["roles"][role]
    if (
        receipt["N"] != context.counts[role]
        or receipt["features_sha256"] != manifest["files"]["features.npy"]
        or receipt["membership_sha256"] != manifest["files"].get("membership.npy")
        or receipt["sha256"] != data.digest(path)
    ):
        raise ValueError("score alignment/identity/count")
    x = np.load(path, mmap_mode="r", allow_pickle=False)
    if (
        x.shape != (context.counts[role],)
        or x.dtype != np.float64
        or not np.isfinite(x).all()
        or np.any(x < 0)
    ):
        raise ValueError("committed score vector")
    return x


def wilson(k, n):
    if not 0 <= k <= n or n <= 0:
        raise ValueError("counts")
    z = float(norm.ppf(0.975))
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, center - half), min(1.0, center + half)


def reverse_interval(lower, upper):
    return -upper, -lower


def cost_decisions(cpu):
    def costs(arm):
        seeds = [s for a, s in models.STREAMS if a == arm]
        result = np.array(
            [
                [
                    next(
                        r["mean_ns"]
                        for r in cpu["rows"]
                        if r["repetition"] == rep
                        and r["arm"] == arm
                        and r["seed"] == seed
                        and r["batch"] == 32
                        and r["boundary"] == "joint"
                    )
                    for seed in seeds
                ]
                for rep in range(8)
            ]
        )
        return result

    return {
        f"{c}_over_{r}": stats.cpu_cost_rule(costs(c), costs(r))
        for c, r in (
            ("compactAE", "referenceAE"),
            ("PCA3", "compactAE"),
            ("regularizedMahalanobis", "compactAE"),
        )
    }


def decision(inference, arm_background, costs):
    def row(kind, arm, signal, alpha=0.01, reference=""):
        return next(
            r
            for r in inference
            if r["kind"] == kind
            and r["arm"] == arm
            and r["reference"] == reference
            and r["signal"] == signal
            and r["alpha"] == alpha
        )

    utility = {
        arm: all(row("efficiency", arm, s)["lower"] >= 0.15 for s in SIGNALS)
        for arm in ARMS
    }
    ni = [
        row("noninferiority", "compactAE", s, reference="referenceAE") for s in SIGNALS
    ]
    retention = all(r["lower"] > 0 for r in ni)
    retention_excluded = any(r["upper"] <= 0 for r in ni)
    utility_excluded = {
        arm: any(row("efficiency", arm, signal)["upper"] < 0.15 for signal in SIGNALS)
        for arm in ARMS
    }
    secondary_utility = (
        {
            arm: all(
                row("efficiency", arm, signal, 0.001)["lower"] >= 0.05
                for signal in SIGNALS
            )
            for arm in ARMS
        }
        if any(r["alpha"] == 0.001 for r in inference)
        else {}
    )

    def rates(a, b):
        return stats.rate_comparable(
            arm_background[a, 0.01], arm_background[b, 0.01], 0.01
        )

    common = rates("compactAE", "referenceAE")
    cpu = costs["compactAE_over_referenceAE"]["passed"]
    success = retention and utility["compactAE"] and common and cpu
    dominance = {}
    for arm in ARMS[2:]:
        # Canonical compact-minus-baseline rows require a reversed interval.
        diff = [row("difference", "compactAE", s, reference=arm) for s in SIGNALS]
        intervals = [reverse_interval(r["lower"], r["upper"]) for r in diff]
        dominance[arm] = dict(
            baseline_minus_compact_intervals=intervals,
            quality_margin=all(lo > 0.01 for lo, hi in intervals),
            utility=utility[arm],
            rate_comparable=rates(arm, "compactAE"),
            cpu=costs[f"{arm}_over_compactAE"]["passed"],
        )
        dominance[arm]["passed"] = all(
            dominance[arm][k]
            for k in ("quality_margin", "utility", "rate_comparable", "cpu")
        )
    verdict = (
        "compact_joint_success"
        if success
        else (
            "simple_baseline_dominance"
            if any(d["passed"] for d in dominance.values())
            else (
                "negative_compound_criterion"
                if not cpu or retention_excluded or utility_excluded["compactAE"]
                else "inconclusive_compound_criterion"
            )
        )
    )
    return dict(
        verdict=verdict,
        compact_success=success,
        retention=retention,
        retention_excluded=retention_excluded,
        compact_reference_rate_comparable=common,
        utility=utility,
        utility_excluded=utility_excluded,
        secondary_utility=secondary_utility,
        cpu_advantage=cpu,
        baseline_dominance=dominance,
    )


def bound_details(candidate, cuts, reference=None, reference_cuts=None, factor=1.0):
    result = stats.signal_bounds(candidate, cuts, reference, reference_cuts, factor)

    def endpoint(rows, key):
        return [float(str(c[key]).replace("infinity", "inf")) for c in rows]

    lower = stats.seed_indicators(candidate, endpoint(cuts, "upper_endpoint"))
    upper = stats.seed_indicators(candidate, endpoint(cuts, "lower_endpoint"))
    if reference is not None:
        lower -= factor * stats.seed_indicators(
            reference, endpoint(reference_cuts, "lower_endpoint")
        )
        upper -= factor * stats.seed_indicators(
            reference, endpoint(reference_cuts, "upper_endpoint")
        )
    result.update(
        lower_endpoint_mean=float(lower.mean()),
        upper_endpoint_mean=float(upper.mean()),
        lower_endpoint_variance_ddof1=float(lower.var(ddof=1)),
        upper_endpoint_variance_ddof1=float(upper.var(ddof=1)),
    )
    return result


def analyze(context, cpu):
    from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve

    background = []
    signal_rows = []
    inference = []
    ranking = []
    rate_rows = []
    arm_bg = {}
    arm_fpr = {}
    bg = {
        f"{a}--{s}": load_scores(context, "final_background", a, s)
        for a, s in models.STREAMS
    }
    signals = {
        sig: {f"{a}--{s}": load_scores(context, sig, a, s) for a, s in models.STREAMS}
        for sig in SIGNALS
    }
    for alpha in RATES:
        for arm in ARMS:
            intervals = []
            points = []
            for a, seed in models.STREAMS:
                if a != arm:
                    continue
                scores = bg[f"{arm}--{seed}"]
                cut = next(
                    c
                    for c in cut_rows(context.freeze, arm, seed)
                    if c["alpha"] == alpha
                )
                k = int(np.count_nonzero(scores > cut["threshold"]))
                n = len(scores)
                ci = stats.exact_background_interval(k, n)
                wi = wilson(k, n)
                intervals.append(ci)
                points.append(k / n)
                background.append(
                    dict(
                        scope="stream",
                        arm=arm,
                        seed=seed,
                        alpha=alpha,
                        N=n,
                        accepted=k,
                        ties=int(np.count_nonzero(scores == cut["threshold"])),
                        fpr=k / n,
                        lower=ci[0],
                        upper=ci[1],
                        wilson95_lower=wi[0],
                        wilson95_upper=wi[1],
                        threshold=cut["threshold"],
                        interval="CP simultaneous delta=.01/16 at frozen empirical cut",
                    )
                )
            arm_bg[arm, alpha] = tuple(np.mean(intervals, axis=0))
            arm_fpr[arm, alpha] = float(np.mean(points))
            background.append(
                dict(
                    scope="arm_finite_seed_mean",
                    arm=arm,
                    seed="mean" if len(points) == 3 else "fit",
                    alpha=alpha,
                    N=context.counts["final_background"],
                    accepted=None,
                    ties=None,
                    fpr=arm_fpr[arm, alpha],
                    lower=arm_bg[arm, alpha][0],
                    upper=arm_bg[arm, alpha][1],
                    wilson95_lower=None,
                    wilson95_upper=None,
                    threshold=None,
                    interval="mean of simultaneous seed CP endpoints; not pooled counts",
                )
            )
        for a, b in itertools.combinations(ARMS, 2):
            ci, cj = arm_bg[a, alpha], arm_bg[b, alpha]
            rate_rows.append(
                dict(
                    arm=a,
                    reference=b,
                    alpha=alpha,
                    lower=ci[0] - cj[1],
                    upper=ci[1] - cj[0],
                    comparable=stats.rate_comparable(ci, cj, alpha),
                )
            )
        for sig in SIGNALS:
            scores_by_arm = {}
            cuts_by_arm = {}
            indicators = {}
            for arm in ARMS:
                seeds = [s for a, s in models.STREAMS if a == arm]
                scores = np.stack([signals[sig][f"{arm}--{seed}"] for seed in seeds])
                cuts = [
                    next(
                        c
                        for c in cut_rows(context.freeze, arm, seed)
                        if c["alpha"] == alpha
                    )
                    for seed in seeds
                ]
                scores_by_arm[arm], cuts_by_arm[arm] = scores, cuts
                indicators[arm] = stats.seed_indicators(
                    scores, [c["threshold"] for c in cuts]
                )
                for seed, vector, cut in zip(seeds, scores, cuts, strict=True):
                    k = int(np.count_nonzero(vector > cut["threshold"]))
                    signal_rows.append(
                        dict(
                            scope="stream",
                            signal=sig,
                            arm=arm,
                            seed=seed,
                            alpha=alpha,
                            N=len(vector),
                            accepted=k,
                            ties=int(np.count_nonzero(vector == cut["threshold"])),
                            efficiency=k / len(vector),
                            background_fpr=next(
                                r["fpr"]
                                for r in background
                                if r["scope"] == "stream"
                                and r["arm"] == arm
                                and r["seed"] == seed
                                and r["alpha"] == alpha
                            ),
                            nominal_SIC=None,
                        )
                    )
                point = float(indicators[arm].mean())
                fpr = arm_fpr[arm, alpha]
                signal_rows.append(
                    dict(
                        scope="arm_finite_seed_mean",
                        signal=sig,
                        arm=arm,
                        seed="mean" if len(seeds) == 3 else "fit",
                        alpha=alpha,
                        N=len(indicators[arm]),
                        accepted=None,
                        ties=None,
                        efficiency=point,
                        background_fpr=fpr,
                        nominal_SIC=point / math.sqrt(fpr) if fpr > 0 else None,
                    )
                )
                bounds = bound_details(scores, cuts)
                inference.append(
                    dict(
                        kind="efficiency",
                        arm=arm,
                        reference="",
                        signal=sig,
                        alpha=alpha,
                        point=point,
                        support_width=1.0,
                        **bounds,
                    )
                )
            for a, b in itertools.combinations(ARMS, 2):
                bounds = bound_details(
                    scores_by_arm[a], cuts_by_arm[a], scores_by_arm[b], cuts_by_arm[b]
                )
                inference.append(
                    dict(
                        kind="difference",
                        arm=a,
                        reference=b,
                        signal=sig,
                        alpha=alpha,
                        point=float((indicators[a] - indicators[b]).mean()),
                        support_width=2.0,
                        **bounds,
                    )
                )
            bounds = bound_details(
                scores_by_arm["compactAE"],
                cuts_by_arm["compactAE"],
                scores_by_arm["referenceAE"],
                cuts_by_arm["referenceAE"],
                factor=0.9,
            )
            inference.append(
                dict(
                    kind="noninferiority",
                    arm="compactAE",
                    reference="referenceAE",
                    signal=sig,
                    alpha=alpha,
                    point=float(
                        (
                            indicators["compactAE"] - 0.9 * indicators["referenceAE"]
                        ).mean()
                    ),
                    support_width=1.9,
                    **bounds,
                )
            )
    if len(inference) != 44:
        raise AssertionError("complete fixed inference family")
    for sig in SIGNALS:
        for arm, seed in models.STREAMS:
            b, s = bg[f"{arm}--{seed}"], signals[sig][f"{arm}--{seed}"]
            labels = np.r_[
                np.zeros(len(b), dtype=np.uint8), np.ones(len(s), dtype=np.uint8)
            ]
            values = np.r_[b, s]
            fpr, tpr, thresholds = roc_curve(labels, values, drop_intermediate=False)
            # No maximization/threshold choice; retain only nearest achievable points to the two prespecified x coordinates.
            attainable = [
                dict(
                    target=alpha,
                    fpr=float(fpr[i]),
                    tpr=float(tpr[i]),
                    threshold=None
                    if not np.isfinite(thresholds[i])
                    else float(thresholds[i]),
                )
                for alpha in RATES
                for i in [int(np.argmin(np.abs(fpr - alpha)))]
            ]
            ranking.append(
                dict(
                    signal=sig,
                    arm=arm,
                    seed=seed,
                    background_N=len(b),
                    signal_N=len(s),
                    prevalence=len(s) / len(values),
                    auc=float(roc_auc_score(labels, values)),
                    ap=float(average_precision_score(labels, values)),
                    attainable_points=attainable,
                )
            )
    costs = cost_decisions(cpu)
    verdict = decision(inference, arm_bg, costs)
    result = dict(
        background=background,
        signal=signal_rows,
        inference=inference,
        ranking=ranking,
        rate_comparability=rate_rows,
        cost_rules=costs,
        decision=verdict,
        inference_estimand="population-quantile efficiencies; calibration delta=.01 + background delta=.01 + signal EB delta=.03; finite seeds shared events N, not 3N",
        deployment_points="frozen empirical cuts; descriptive; strict >",
    )
    data.write_json(context.output / "private/analysis.json", result)
    return result


def robustness(context, loaded):
    objects = np.array(context.role("final_background", "objects")[:512], copy=True)
    values = np.array(context.role("final_background")[:512], copy=True)
    scaler = read(context.input_root / "private/scaler.json")
    original = data.features(objects)
    transformed_rows = []
    before = dict(TALLY)
    margins = {}
    for name in ("rotation", "beam_reflection"):
        obj = objects.copy()
        if name == "rotation":
            mask = obj[:, :, 3] != 0
            obj[:, :, 2][mask] += 0.7
        else:
            obj[:, :, 1] *= -1
        feat = data.features(obj)
        scaled = data.transform(feat, scaler)
        if not np.allclose(feat, original, atol=1e-5, rtol=1e-5) or not np.allclose(
            scaled, values, atol=1e-5, rtol=1e-5
        ):
            raise ValueError("required feature identity failure")
        for arm, seed in models.STREAMS:
            base = load_scores(context, "final_background", arm, seed)[: len(obj)]
            scores = score_shape(loaded[f"{arm}--{seed}"], scaled, 32)
            allowance = score_allowance(base)
            error = np.abs(scores - base)
            cuts = np.array(
                [c["threshold"] for c in cut_rows(context.freeze, arm, seed)]
            )
            flips = (base[:, None] > cuts) != (scores[:, None] > cuts)
            margins[f"{name}--{arm}--{seed}"] = dict(
                original=(base[:, None] - cuts).tolist(),
                transformed=(scores[:, None] - cuts).tolist(),
                decision_changes=flips.tolist(),
                score_abs_error=error.tolist(),
            )
            transformed_rows.append(
                dict(
                    scope="required_identity",
                    transformation=name,
                    arm=arm,
                    seed=seed,
                    N=len(obj),
                    feature_max_abs=float(np.max(np.abs(feat - original))),
                    scaled_max_abs=float(np.max(np.abs(scaled - values))),
                    score_max_abs=float(error.max()),
                    score_min_remaining_allowance=float((allowance - error).min()),
                    decision_changes_primary=int(flips[:, 0].sum()),
                    decision_changes_secondary=int(flips[:, 1].sum()),
                    passed=bool(np.all(error <= allowance)),
                )
            )
            if not np.all(error <= allowance):
                data.write_json(
                    context.output / "private/robustness-failure.json",
                    dict(rows=transformed_rows, margins=margins),
                )
                raise ValueError("required score identity failure")
    data.write_json(context.output / "private/robustness-margins.json", margins)
    result = dict(rows=transformed_rows, work={k: TALLY[k] - before[k] for k in TALLY})
    data.write_json(context.output / "private/robustness.json", result)
    return result


def bias_profiles(context):
    objects = context.role("final_background", "objects")
    n = len(objects)
    bins = {
        name: np.empty(n, dtype=np.uint8) for name in ("MET_GeV", "leptons", "jets")
    }
    for start in range(0, n, 8192):
        o = objects[start : start + 8192]
        bins["MET_GeV"][start : start + len(o)] = np.searchsorted(
            [30.0, 60.0, 120.0], o[:, 0, 0], side="right"
        )
        types = o[:, :, 3]
        bins["leptons"][start : start + len(o)] = (
            np.minimum(((types == 2) | (types == 3)).sum(axis=1), 3) - 1
        )
        bins["jets"][start : start + len(o)] = np.minimum((types == 4).sum(axis=1), 3)
    labels = {
        "MET_GeV": ["[0,30)", "[30,60)", "[60,120)", "[120,infinity)"],
        "leptons": ["1", "2", ">=3"],
        "jets": ["0", "1", "2", ">=3"],
    }
    rows = []
    for alpha in RATES:
        for arm in ARMS:
            indicators = []
            for a, seed in models.STREAMS:
                if a != arm:
                    continue
                score = load_scores(context, "final_background", arm, seed)
                cut = next(
                    c
                    for c in cut_rows(context.freeze, arm, seed)
                    if c["alpha"] == alpha
                )
                accepted = score > cut["threshold"]
                indicators.append(accepted)
                for name, indices in bins.items():
                    for ix, label in enumerate(labels[name]):
                        mask = indices == ix
                        den = int(mask.sum())
                        num = int(accepted[mask].sum())
                        rows.append(
                            dict(
                                scope="bias_stream",
                                arm=arm,
                                seed=seed,
                                alpha=alpha,
                                profile=name,
                                bin=label,
                                N=den,
                                accepted=num if den >= 20 else None,
                                acceptance=num / den if den >= 20 else None,
                                suppressed=den < 20,
                            )
                        )
            avg = np.mean(indicators, axis=0)
            for name, indices in bins.items():
                for ix, label in enumerate(labels[name]):
                    mask = indices == ix
                    den = int(mask.sum())
                    rows.append(
                        dict(
                            scope="bias_arm_finite_seed_mean",
                            arm=arm,
                            seed="mean" if len(indicators) == 3 else "fit",
                            alpha=alpha,
                            profile=name,
                            bin=label,
                            N=den,
                            accepted=None,
                            acceptance=float(avg[mask].mean()) if den >= 20 else None,
                            suppressed=den < 20,
                        )
                    )
    data.write_json(context.output / "private/bias.json", rows)
    return rows
