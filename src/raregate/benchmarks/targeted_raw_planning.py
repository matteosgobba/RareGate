"""Pure Task0047 paired schedule, actual-row budgets and chunk geometry."""

from raregate.simulation.protocol import require

CANDIDATES = ("pca-v1", "compact-autoencoder-v2")
CASES = tuple(
    (b, m)
    for b, ms in (
        (1, (1,)),
        (8, tuple(range(1, 9))),
        (32, (*range(1, 9), 31, 32)),
        (128, (*range(1, 11), 32, 127, 128)),
    )
    for m in ms
)
REFERENCE_CASES = (
    (1, 1),
    (8, 1),
    (8, 2),
    (8, 7),
    (8, 8),
    (32, 1),
    (32, 2),
    (32, 8),
    (32, 31),
    (32, 32),
    (128, 1),
    (128, 2),
    (128, 32),
    (128, 127),
    (128, 128),
)
WRAPPER = "task0047_owned_C_FP32_actual_rows_public_score_strict4_copies_v1"


def case_class(b, m):
    require((b, m) in CASES, "Prescribed32cases")
    return "remeasured_reference" if (b, m) in REFERENCE_CASES else "new_selected_point"


SIDES = ("natural_m", "full_B_control")


def mapping(b, m, side):
    require(
        type(b) is int and type(m) is int and (b, m) in CASES and side in SIDES,
        "Fixed nominal case and side",
    )
    actual = m if side == "natural_m" else b
    service_b = actual
    return actual, service_b


def windows(b):
    require(type(b) is int and b in (1, 8, 32, 128), "Original nominal B windows")
    return (0, (1024 - b) // 2, 1024 - b)


def candidates(rep):
    require(type(rep) is int and rep in (1, 2, 3), "Three fixed repetitions")
    return CANDIDATES if rep != 2 else tuple(reversed(CANDIDATES))


def cases(rep):
    candidates(rep)
    return CASES if rep != 2 else tuple(reversed(CASES))


def schedule(rep, candidate):
    require(candidate in candidates(rep), "Original candidate")
    for b, m in cases(rep):
        for phase, count in (("warmup", 3), ("timed", 20)):
            for i in range(count):
                order = SIDES if i % 2 == 0 else tuple(reversed(SIDES))
                for side_index, side in enumerate(order):
                    actual, service_b = mapping(b, m, side)
                    yield dict(
                        repetition=rep,
                        candidate=candidate,
                        B=b,
                        m=m,
                        side=side,
                        actual_rows=actual,
                        model_shape_rows=service_b,
                        case_class=case_class(b, m),
                        wrapper=WRAPPER,
                        phase=phase,
                        pair=i,
                        pair_id=f"{rep}/{candidate}/{b}/{m}/{phase}/{i}",
                        window_index=i % 3,
                        window_position=windows(b)[i % 3],
                        side_index=side_index,
                        order_label=order[0] + "_first",
                    )


def gate_schedule():
    for b, m in CASES:
        for index, pos in enumerate(windows(b)):
            for side in SIDES:
                actual, service_b = mapping(b, m, side)
                yield dict(
                    B=b,
                    m=m,
                    window_index=index,
                    window_position=pos,
                    side=side,
                    actual_rows=actual,
                    model_shape_rows=service_b,
                    case_class=case_class(b, m),
                    wrapper=WRAPPER,
                )


def counts():
    rows = [r for rep in (1, 2, 3) for c in candidates(rep) for r in schedule(rep, c)]
    components = {
        phase: dict(
            calls=sum(r["phase"] == phase for r in rows),
            rows=sum(r["actual_rows"] for r in rows if r["phase"] == phase),
        )
        for phase in ("timed", "warmup")
    }
    contexts = [r for _ in range(3 * 2 * 2) for r in gate_schedule()]
    refs = dict(calls=len(contexts), rows=sum(r["actual_rows"] for r in contexts))
    gates = {k: 2 * v for k, v in refs.items()}
    raw_calls = (
        components["timed"]["calls"] + components["warmup"]["calls"] + gates["calls"]
    )
    raw_rows = (
        components["timed"]["rows"] + components["warmup"]["rows"] + gates["rows"]
    )
    return dict(
        paired_groups=192,
        cells=384,
        timed_pairs=3840,
        warmup_pairs=576,
        timed=components["timed"],
        warmup=components["warmup"],
        chain_gates=gates,
        golden_references=refs,
        selected_reads_and_feature_constructions=dict(calls=raw_calls, rows=raw_rows),
        public_service=dict(
            calls=raw_calls + refs["calls"], rows=raw_rows + refs["rows"]
        ),
        per_worker=dict(
            raw_calls=raw_calls // 3,
            raw_rows=raw_rows // 3,
            service_calls=(raw_calls + refs["calls"]) // 3,
            service_rows=(raw_rows + refs["rows"]) // 3,
            reference_calls=refs["calls"] // 3,
            reference_rows=refs["rows"] // 3,
        ),
        per_candidate=dict(
            calls=(raw_calls + refs["calls"]) // 2, rows=(raw_rows + refs["rows"]) // 2
        ),
        decision_boolean_values=4 * (raw_rows + refs["rows"]),
        paired_gate_contexts=len(contexts) // 2,
        gate_side_records=len(contexts),
        membership_loads=3,
        membership_ID_records=20997,
        golden_loads=3,
        golden_rows=3072,
        model_threshold_loads_and_instantiations=6,
        HDF_handles=3,
        raw_hash_passes=2,
        raw_hash_bytes=5816520818,
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
        "Ordered approved geometry",
    )
    rows = []
    chunks = set()
    union = set()
    total = 0
    for r in gate_schedule():
        selected = [
            int(v)
            for v in ids[r["window_position"] : r["window_position"] + r["actual_rows"]]
        ]
        cs = {v // 62 for v in selected}
        chunks.update(cs)
        union.update(selected)
        # Every candidate/repetition has timed7/7/6 +warm1 +2pre+2post chain reads.
        requests = 6 * ((7 if r["window_index"] < 2 else 6) + 1 + 4)
        upper = len(cs) * 62 * 2101 * 8
        total += requests * upper
        rows.append(
            dict(
                r,
                geometric_chunks=len(cs),
                logical_raw_requests=requests,
                per_request_decoded_upper_bytes=upper,
            )
        )
    require(len(union) == 384, "Exactly historical384raw rows")
    return dict(
        windows=rows,
        distinct_chunks=len(chunks),
        unique_raw_rows=len(union),
        repeated_no_cache_decoded_upper_bytes=total,
        meaning="geometry only; not measured physical I/O/decompression/cache misses",
    )
