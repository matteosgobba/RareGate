"""Task0052 fixed generated characterization; explicit activation, no operational mode."""

import hashlib
import json
import multiprocessing as mp
import os
import subprocess
from pathlib import Path

from .fixture import RSS_CAPS, SCENARIOS52, _json, run_fixture
from .instrumentation import Samples, grouped_samples, load_baseline, update_sequence
from .protocol import Scheduler, require
from .records import Store, decode, encode, reconcile
from .supervision import (
    Clocks,
    Monitor,
    cleanup_children,
    own_rss,
    synchronization_inventory,
)

BASE = "2f59ae1fafd77455b001393482a5bea84ddb1fc8"
CONFIG = "configs/streaming/development_streaming_instrumentation_v1.json"


def manifest(root):
    paths = sorted((root / "src/latenttrigger/streaming").glob("*.py"))
    paths += [
        root / CONFIG,
        root / "scripts/characterize_development_streaming.py",
        root / "tests/test_development_streaming_instrumentation.py",
        root / "tests/test_development_streaming_foundation.py",
        root / "docs/prompts/0052-generated-streaming-instrumentation.md",
    ]
    return [
        dict(
            path=str(p.relative_to(root)),
            size_bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(),
        )
        for p in paths
        for b in [p.read_bytes()]
    ]


def recorder_worker(directory, baseline, side):
    clocks = Clocks()
    begin = clocks.continuous()
    init = clocks.service()
    directory = Path(directory)
    directory.mkdir()
    samples = Samples(directory / "samples.bin", 1032)
    module = load_baseline(baseline) if side == "A" else None
    cls = module.Store if module else Store
    stores = {
        k: cls(directory / (k + ".bin"), 128, k, True) for k in ("event", "batch")
    }
    # Both sides: zero file creation, explicit full-file pread (first read/page history).
    # Candidate additionally maps/touches its pages and allocates512B scratch.
    for st in stores.values():
        require(os.pread(st.fd, 65536, 0) == bytes(65536), "Blank pre-read history")
    samples.add(6, 0, 0, 0, init, clocks.service())
    try:
        for kind, st in stores.items():
            for index, record in update_sequence(kind):
                start = clocks.service()
                st.write(index, record)
                end = clocks.service()
                samples.add(
                    1 if kind == "event" else 2, record["status"], 1, 1, start, end
                )
                samples.add(
                    9 if kind == "event" else 10,
                    record["status"],
                    1,
                    1,
                    start,
                    clocks.service(),
                )
        events, batches = [stores[k].read_all() for k in ("event", "batch")]
        for kind, st in stores.items():
            final = list(update_sequence(kind))[1::2]
            for index, record in final:
                blob = os.pread(st.fd, 512, index * 512)
                # Decode current canonical bytes, independently decode pinned when A;
                # deterministic suite separately proves both directions + external offsets.
                require(blob == encode(record, kind), "Compatible record bytes")
                require(decode(blob, kind) is not None, "Readable record")
        a = reconcile(events, batches, Scheduler(0, 128, 500), 10**9)
        require(
            a["completed"] == 128 and a["boolean_outputs"] == 512,
            "Independent expected accounting",
        )
    finally:
        final = clocks.service()
        for st in stores.values():
            st.close()
        samples.add(7, 0, 0, 0, final, clocks.service())
        samples.close()
    _json(
        directory / "worker.json",
        dict(
            side=side,
            accounting=a,
            generated_offers=0,
            event_appends=256,
            batch_appends=256,
            peak_RSS_bytes=own_rss(),
            clock_observation=clocks.observation(),
            continuous_elapsed_ns=clocks.continuous() - begin,
            sample_aggregates=grouped_samples(directory / "samples.bin"),
        ),
    )


def run_recorder(directory, baseline, side):
    clocks = Clocks()
    begin = clocks.continuous()
    observation = clocks.observation()
    monitor = Monitor(*observation[:2])
    ctx = mp.get_context("spawn")
    stop = ctx.Event()  # 5 SemLocks, recorder supervisor only; not an event buffer.
    sync_inventory = synchronization_inventory(None, dict(cleanup_stop=stop))
    child = ctx.Process(
        target=recorder_worker,
        args=(str(directory), str(baseline), side),
        name="recorder-" + side,
    )
    problem = None
    try:
        child.start()
        while child.is_alive():
            svc, cont, _ = clocks.observation()
            monitor.observe(svc, cont)
            require(cont - begin < 3_000_000_000, "Recorder body deadline")
            require(own_rss() <= RSS_CAPS["supervisor"], "Supervisor RSS")
            stop.wait(0.005)
        require(child.exitcode == 0, "Recorder worker failed")
    except Exception as exc:
        problem = str(exc)
    finally:
        cleanup = clocks.continuous()
        exits = cleanup_children(
            [child],
            stop,
            clocks.continuous,
            min(begin + 5_000_000_000, cleanup + 2_000_000_000),
        )
        cleanup_ns = clocks.continuous() - cleanup
    path = directory / "worker.json"
    result = (
        json.loads(path.read_text()) if path.exists() else dict(sample_aggregates=None)
    )
    result.update(
        synchronization_inventory=sync_inventory,
        problem=problem,
        children=exits,
        cleanup_ns=cleanup_ns,
        elapsed_ns=clocks.continuous() - begin,
        maximum_monitor_gap_ns=monitor.maximum_gap,
        parent_service_bracket_ns=[observation[0], clocks.service()],
        parent_clock_bracket_ns=observation[2],
        supervisor_RSS_bytes=own_rss(),
    )
    require(result["elapsed_ns"] <= 5_000_000_000, "Recorder total deadline")
    require(
        not result.get("peak_RSS_bytes")
        or result["peak_RSS_bytes"] <= RSS_CAPS["producer"],
        "Recorder RSS",
    )
    result["software_checks_passed"] = problem is None and not any(
        x.get("leaked") for x in exits
    )
    return result


def characterize(output):
    root = Path(__file__).resolve().parents[3]
    output = Path(output)
    require(
        output.is_absolute()
        and not output.exists()
        and output.parent == root / "data/task0052-validation",
        "New task0052 owned directory",
    )
    cfg = json.loads((root / CONFIG).read_text())
    require(
        cfg["fixture_only"]
        and not cfg["operational_execution_authorized"]
        and not cfg["operational_allowance_granted"],
        "Fixture-only configuration",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(mode=0o700)
    clocks = Clocks()
    begin = clocks.continuous()
    _json(
        output / "owner.json", dict(task="0052", generated_only=True, operational=False)
    )
    baseline = output / "baseline"
    baseline.mkdir()
    for name in ("protocol", "records"):
        b = subprocess.run(
            ["git", "show", BASE + ":src/latenttrigger/streaming/" + name + ".py"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
        (baseline / (name + ".py")).write_bytes(b)
    load_baseline(baseline)  # identity check before spawning
    sources = manifest(root)
    _json(
        output / "prospective.json",
        dict(
            config=cfg,
            source_manifest=sources,
            source_manifest_sha256=hashlib.sha256(
                json.dumps(sources, sort_keys=True).encode()
            ).hexdigest(),
            plan=cfg["invocations"],
            no_native_started_yet=True,
        ),
    )
    attempts = []
    for index, case in enumerate(cfg["invocations"], 1):
        require(
            len(attempts) + cfg.get("prior_native_invocations", 0) < 20
            and clocks.continuous() - begin < 115_000_000_000,
            "Task0052 total envelope",
        )
        _json(output / f"attempt-{index:02d}.json", case)
        path = output / f"{index:02d}-{case['id']}"
        try:
            if case["kind"] == "recorder":
                report = run_recorder(path, baseline, case["side"])
            else:
                require(
                    tuple(case["offers_rate"]) == SCENARIOS52[case["scenario"]],
                    "Prospective case agreement",
                )
                report = run_fixture(path, case["scenario"], task52=True)
        except Exception as exc:
            report = dict(
                software_checks_passed=False,
                harness_error=type(exc).__name__ + ": " + str(exc),
                sample_aggregates=None,
                partial_evidence_retained=True,
            )
        report = dict(case=case, **report)
        attempts.append(report)
        _json(output / f"result-{index:02d}.json", report)
        require(
            sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
            <= 16 * 1024**2,
            "Owned storage",
        )
        if not report["software_checks_passed"]:
            break  # no replacement of failed/slow runs
    result = dict(
        attempts=attempts,
        source_manifest=sources,
        final_source_unchanged=manifest(root) == sources,
        elapsed_ns=clocks.continuous() - begin,
        invocation_count=len(attempts),
        configured_offers=sum(
            c.get("offers_rate", [0])[0] for c in cfg["invocations"][: len(attempts)]
        ),
        unattempted=[c["id"] for c in cfg["invocations"][len(attempts) :]],
        whole_characterization_cap_ns=120_000_000_000,
    )
    # Compact result retains per-invocation aggregates; samples/records stay ignored.
    blob = (json.dumps(result, allow_nan=False, indent=2) + "\n").encode()
    require(len(blob) <= 2 * 1024**2, "Aggregate JSON bound")
    with open(output / "characterization.json", "xb") as f:
        f.write(blob)
    require(
        clocks.continuous() - begin <= 120_000_000_000, "Total including finalization"
    )
    require(
        sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) <= 16 * 1024**2,
        "Final storage",
    )
    return result
