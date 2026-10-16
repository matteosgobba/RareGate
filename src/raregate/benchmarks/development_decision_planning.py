"""Pure fixed Task0041 schedule/accounting; no numerical or model imports."""

from raregate.benchmarks.development_raw_planning import BATCHES, windows
from raregate.simulation.protocol import require

CANDIDATES = ("pca-v1", "compact-autoencoder-v2")


def candidates(rep):
    require(type(rep) is int and rep in (1, 2, 3), "Three fixed repetition workers")
    return CANDIDATES if rep != 2 else tuple(reversed(CANDIDATES))


def schedule(rep, candidate):
    require(candidate in candidates(rep), "Only frozen candidates")
    bs = BATCHES if rep != 2 else tuple(reversed(BATCHES))
    for b in bs:
        for phase, n in (("warmup", 3), ("timed", 20)):
            for i in range(n):
                yield dict(
                    repetition=rep,
                    candidate=candidate,
                    B=b,
                    phase=phase,
                    call=i,
                    window_position=windows(b)[i % 3],
                )


def gate_schedule():
    for b in BATCHES:
        for pos in windows(b):
            yield b, pos


def counts():
    calls = [v for rep in (1, 2, 3) for c in candidates(rep) for v in schedule(rep, c)]
    component = {
        phase: dict(
            calls=sum(v["phase"] == phase for v in calls),
            rows=sum(v["B"] for v in calls if v["phase"] == phase),
        )
        for phase in ("timed", "warmup")
    }
    gate_windows = [
        b
        for _rep in (1, 2, 3)
        for _c in CANDIDATES
        for _phase in ("pre", "post")
        for b, _ in gate_schedule()
    ]
    refs = dict(calls=len(gate_windows), rows=sum(gate_windows))
    gates = dict(calls=2 * refs["calls"], rows=2 * refs["rows"])
    raw_calls = sum(v["calls"] for v in component.values()) + gates["calls"]
    raw_rows = sum(v["rows"] for v in component.values()) + gates["rows"]
    service_calls = raw_calls + refs["calls"]
    service_rows = raw_rows + refs["rows"]
    return dict(
        cells=len(CANDIDATES) * len(BATCHES) * 3,
        timed=component["timed"],
        warmup=component["warmup"],
        chain_gates=gates,
        golden_references=refs,
        selected_reads_and_feature_constructions=dict(calls=raw_calls, rows=raw_rows),
        public_service=dict(calls=service_calls, rows=service_rows),
        per_worker=dict(
            raw_calls=raw_calls // 3,
            raw_rows=raw_rows // 3,
            service_calls=service_calls // 3,
            service_rows=service_rows // 3,
            reference_calls=refs["calls"] // 3,
            reference_rows=refs["rows"] // 3,
        ),
        per_candidate=dict(calls=service_calls // 2, rows=service_rows // 2),
        decision_boolean_values=service_rows * 4,
        gate_window_records=refs["calls"],
        membership_loads=3,
        membership_ID_records=3 * 6999,
        golden_loads=3,
        golden_rows=3072,
        model_threshold_loads_and_instantiations=6,
        HDF_handles=3,
        raw_hash_passes=2,
        raw_hash_bytes=2 * 2908260409,
        unique_approved_rows=1024,
        unique_raw_rows=384,
        raw_buffer_preloads=0,
        dummy_rows=0,
    )


def geometry(ids):
    require(
        len(ids) == 1024
        and all(int(ids[i]) < int(ids[i + 1]) for i in range(1023))
        and all(0 <= int(v) < 1100000 for v in ids),
        "Exact ordered geometry universe",
    )
    rows = []
    union = set()
    unique_rows = set()
    upper = 0
    for b in BATCHES:
        for index, start in enumerate(windows(b)):
            selected = [int(v) for v in ids[start : start + b]]
            chunks = {v // 62 for v in selected}
            union.update(chunks)
            unique_rows.update(selected)
            # Per candidate/worker: timed7/7/6 + warm1 + gates2pre/2post.
            n = 6 * ((7 if index < 2 else 6) + 1 + 4)
            decoded = len(chunks) * 62 * 2101 * 8
            upper += n * decoded
            rows.append(
                dict(
                    B=b,
                    window_position=start,
                    window_index=index,
                    selected_rows=b,
                    geometric_chunks=len(chunks),
                    per_request_decoded_upper_bytes=decoded,
                    logical_raw_requests=n,
                )
            )
    return dict(
        windows=rows,
        distinct_chunks=len(union),
        unique_raw_rows=len(unique_rows),
        repeated_no_cache_decoded_upper_bytes=upper,
        meaning="geometry_only_not_physical_IO_decompression_or_cache_misses",
    )
