"""Local PCG64 streams; traces reused exactly, never persisted as event arrays."""

import hashlib
import math
import struct
import sys

from latenttrigger.simulation.engine import MAX_EVENTS, Trace, add_time, integer


def generate(mode, rate, seed, count=5000):
    import numpy as np

    if mode not in ("periodic", "poisson"):
        raise ValueError("Unknown arrival mode")
    integer(rate, "nominal rate", minimum=1)
    integer(seed, "base seed", maximum=2**32 - 1)
    integer(count, "trace count", minimum=1, maximum=MAX_EVENTS)
    mode_id = ("periodic", "poisson").index(mode)
    arrival_key = [3700, seed, mode_id, rate, 0]
    score_key = [3700, seed, mode_id, rate, 1]
    arrivals_rng = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence(arrival_key))
    )
    scores_rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(score_key)))
    gaps = (
        [(1_000_000_000 + rate - 1) // rate] * count
        if mode == "periodic"
        else [
            max(1, math.ceil(float(g)))
            for g in arrivals_rng.exponential(1e9 / rate, size=count)
        ]
    )
    arrival, timestamps = 0, []
    for gap in gaps:
        arrival = add_time(arrival, gap)
        timestamps.append(arrival)
    trace = Trace(
        tuple(timestamps), tuple(float(v) for v in scores_rng.random(count))
    ).validate()
    time_hash = hashlib.sha256(
        b"".join(struct.pack("<q", t) for t in trace.arrivals)
    ).hexdigest()
    score_hash = hashlib.sha256(
        b"".join(struct.pack("<d", s) for s in trace.scores)
    ).hexdigest()
    trace_hash = hashlib.sha256(bytes.fromhex(time_hash + score_hash)).hexdigest()
    retained = sum(
        sys.getsizeof(v)
        for v in (trace, trace.arrivals, trace.scores, *trace.arrivals, *trace.scores)
    )
    return trace, dict(
        mode=mode,
        nominal_rate=rate,
        seed=seed,
        count=count,
        horizon_ns=arrival,
        arrival_sha256=time_hash,
        score_sha256=score_hash,
        trace_sha256=trace_hash,
        arrival_stream_key=arrival_key,
        score_stream_key=score_key,
        generator="NumPy Generator/PCG64/SeedSequence",
        numpy_version=np.__version__,
        time_rule="ceil exponential gaps to >=1ns; periodic ceil(1e9/rate); first arrival after first gap",
        retained_python_bytes=retained,
    )
