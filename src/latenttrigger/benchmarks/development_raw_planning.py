"""Pure prospective scheduling/accounting; chunk geometry is not measured I/O."""

from latenttrigger.benchmarks.development_raw_protocol import require

BATCHES = (1, 8, 32, 128)
SCOPES = (
    "selected_hdf_read",
    "frozen_feature_construction",
    "selected_raw_to_features",
)


def windows(b):
    require(type(b) is int and b in BATCHES, "Fixed B")
    return tuple(dict.fromkeys((0, (1024 - b) // 2, 1024 - b)))


def schedule(rep):
    require(type(rep) is int and rep in (1, 2, 3), "Three fixed workers")
    bs = BATCHES if rep != 2 else tuple(reversed(BATCHES))
    scopes = SCOPES if rep != 2 else tuple(reversed(SCOPES))
    for b in bs:
        for scope in scopes:
            for phase, n in (("warmup", 3), ("timed", 20)):
                for i in range(n):
                    yield dict(
                        repetition=rep,
                        B=b,
                        scope=scope,
                        phase=phase,
                        call=i,
                        window_position=windows(b)[i % 3],
                    )


def counts():
    rows = list(r for rep in (1, 2, 3) for r in schedule(rep))
    read = [r for r in rows if r["scope"] != "frozen_feature_construction"]
    feature = [r for r in rows if r["scope"] != "selected_hdf_read"]
    return dict(
        cells=36,
        timed_calls=sum(r["phase"] == "timed" for r in rows),
        warmup_calls=sum(r["phase"] == "warmup" for r in rows),
        timing_raw_requests=len(read),
        timing_raw_rows=sum(r["B"] for r in read),
        timing_feature_calls=len(feature),
        timing_feature_rows=sum(r["B"] for r in feature),
        owned_feature_buffer_preparation_requests=36,
        owned_feature_buffer_preparation_raw_rows=1521,
        pre_post_gate_raw_requests=144,
        pre_post_gate_raw_rows=6084,
        pre_post_gate_feature_calls=216,
        pre_post_gate_feature_rows=9126,
        total_raw_requests=732,
        total_raw_selected_row_presentations=30927,
        total_feature_calls=768,
        total_feature_row_presentations=32448,
        membership_loads=3,
        membership_ID_records=20997,
        golden_feature_loads=3,
        golden_feature_rows=3072,
        unique_approved_rows=1024,
        raw_hash_custody_passes=2,
        raw_hash_custody_bytes=5816520818,
        HDF_handles=3,
        raw_buffers_per_feature_case=3,
        max_retained_raw_buffers_bytes=3 * 128 * 2101 * 8,
        current_raw_bytes=128 * 2101 * 8,
        explicit_owned_array_buffer_ceiling_bytes=64 * 2**20,
    )


def geometry(ids, chunk_rows=62, columns=2101, itemsize=8):
    require(
        len(ids) == 1024
        and all(0 <= int(v) < 1100000 for v in ids)
        and all(int(ids[i]) < int(ids[i + 1]) for i in range(1023))
        and chunk_rows == 62
        and columns == 2101
        and itemsize == 8,
        "Verified selected IDs/frozen chunk geometry",
    )
    result = []
    unique = set()
    total = 0
    for b in BATCHES:
        for index, start in enumerate(windows(b)):
            chunks = sorted({int(v) // chunk_rows for v in ids[start : start + b]})
            unique.update(chunks)
            # Per worker: read+joint each8/8/7 calls, buffer once, two gates each2reads.
            logical_requests = 3 * ((16 if index < 2 else 14) + 1 + 4)
            row = dict(
                B=b,
                window_position=start,
                selected_rows=b,
                geometric_chunks=len(chunks),
                nominal_decoded_chunk_bytes=chunk_rows * columns * itemsize,
                per_request_decoded_upper_bytes=len(chunks)
                * chunk_rows
                * columns
                * itemsize,
                future_logical_raw_requests=logical_requests,
                source_chunks=chunks,
            )
            total += logical_requests * row["per_request_decoded_upper_bytes"]
            result.append(row)
    return dict(
        windows=result,
        distinct_chunks_for_all_windows=len(unique),
        repeated_no_cache_decoded_upper_bytes=total,
        meaning="geometry only; no payload/decompression/physical-I/O measurement; cache misses unknown",
    )
