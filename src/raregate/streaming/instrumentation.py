"""Bounded generated-only observers; no payload provider, model or operational mode."""

import importlib.util
import os
import struct
import sys
import types
from collections import defaultdict
from pathlib import Path

from . import quota
from .protocol import require

# op, stage, m, updates, start, end, value, auxiliary, reserved, CRC.
SAMPLE = struct.Struct("<IIIIQQQQQQ")
OPS = {
    1: "event_append",
    2: "batch_append",
    3: "offer_cycle",
    4: "batch_cycle",
    5: "phase_append",
    6: "initialization",
    7: "finalization",
    8: "output_write",
    9: "event_observer",
    10: "batch_observer",
}


class Samples:
    """Single writer, fixed 64-byte checksummed samples; stopped-reader only."""

    def __init__(self, path, capacity):
        require(1 <= capacity <= 4096, "Sample capacity")
        self.fd = quota.open_file(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        quota.truncate(self.fd, capacity * SAMPLE.size)
        self.capacity, self.index = capacity, 0

    def add(self, op, stage, m, updates, start, end, value=None, auxiliary=0):
        import zlib

        require(self.index < self.capacity and end >= start, "Sample bound/clock")
        blob = SAMPLE.pack(
            op,
            stage,
            m,
            updates,
            start,
            end,
            end - start if value is None else value,
            auxiliary,
            0,
            0,
        )
        blob = blob[:56] + struct.pack("<Q", zlib.crc32(blob[:56]))
        require(
            quota.pwrite(self.fd, blob, self.index * 64) == 64, "Short sample write"
        )
        self.index += 1

    def close(self):
        if self.fd is not None:
            quota.close(self.fd)
            self.fd = None


def sample_rows(path):
    import zlib

    blob = Path(path).read_bytes()
    require(len(blob) % 64 == 0 and len(blob) <= 4096 * 64, "Sample file bound")
    rows = []
    for i in range(0, len(blob), 64):
        b = blob[i : i + 64]
        if b == bytes(64):
            require(not any(blob[i:]), "Noncontiguous samples")
            break
        r = SAMPLE.unpack(b)
        require(
            r[0] in OPS and r[8] == 0 and r[9] == zlib.crc32(b[:56]), "Invalid sample"
        )
        require(r[5] >= r[4], "Sample clock")
        rows.append(r)
    return rows


def aggregate(values, threshold=None):
    s = sorted(values)
    if not s:
        return dict(
            n=0,
            sum_ns=0,
            mean_ns=None,
            median_ns=None,
            p95_ns=None,
            p99_ns=None,
            maximum_ns=None,
            threshold_ns=threshold,
            exceeds=0,
        )

    def q(p):
        x = (len(s) - 1) * p
        i = int(x)
        return s[i] + (s[min(i + 1, len(s) - 1)] - s[i]) * (x - i)

    return dict(
        n=len(s),
        sum_ns=sum(s),
        mean_ns=sum(s) / len(s),
        median_ns=q(0.5),
        p95_ns=q(0.95),
        p99_ns=q(0.99),
        maximum_ns=s[-1],
        threshold_ns=threshold,
        exceeds=sum(v > threshold for v in s) if threshold else 0,
    )


def grouped_samples(path):
    groups = defaultdict(list)
    for op, stage, m, updates, _, _, value, _, _, _ in sample_rows(path):
        groups[(op, stage, m, updates)].append(value)
    return [
        dict(
            operation=OPS[op],
            stage=stage,
            m=m,
            updates=updates,
            **aggregate(v, 50000 if op == 1 else 200000 if op == 2 else None),
        )
        for (op, stage, m, updates), v in sorted(groups.items())
    ]


def load_baseline(directory):
    """Narrow pinned text package: protocol + records only, never live imports."""
    import hashlib

    pins = {
        "protocol": "15a1c2978704cf0ba32f20b8952014b01daaadb704198c9444e36e1e348faa97",
        "records": "1c64e6efa449a37b33560775137913ce4015c6fb26ffc966ea645ab32133bb03",
    }
    package = "_lt_pinned_0051"
    module = types.ModuleType(package)
    module.__path__ = [str(directory)]
    sys.modules[package] = module
    result = None
    for name, pin in pins.items():
        path = Path(directory) / (name + ".py")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == pin,
            "Pinned baseline identity",
        )
        spec = importlib.util.spec_from_file_location(package + "." + name, path)
        result = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = result
        spec.loader.exec_module(result)
    return result


def update_sequence(kind):
    """256 appends, 128 records × intent/resolution; no real IDs or times."""
    for k in range(128):
        if kind == "event":
            yield (
                k,
                dict(
                    run=1,
                    k=k,
                    prefix=k,
                    status=1,
                    intended=k * 2000000,
                    submission=k * 2000000 + 1,
                    observed=k * 2000000 + 1,
                ),
            )
            yield (
                k,
                dict(
                    run=1,
                    k=k,
                    prefix=k,
                    status=2,
                    intended=k * 2000000,
                    submission=k * 2000000 + 1,
                    admission=k * 2000000 + 2,
                    sequence=k,
                    observed=k * 2000000 + 2,
                ),
            )
        else:
            base = dict(
                run=1,
                batch=k,
                m=1,
                members=[k],
                positions=[k],
                admissions=[k * 2000000 + 2],
                dequeues=[k * 2000000 + 3],
                dispatch=k * 2000000 + 4,
                read_start=k * 2000000 + 5,
                subread_starts=[k * 2000000 + 5],
                read_intents=1,
            )
            yield k, dict(base, status=3)
            yield (
                k,
                dict(
                    base,
                    status=11,
                    subread_ends=[k * 2000000 + 6],
                    read_return=k * 2000000 + 6,
                    read_rows=1,
                    output=k * 2000000 + 10,
                    features=k * 2000000 + 7,
                    decision=k * 2000000 + 8,
                ),
            )
