"""Single-writer fixed512-byte journals, CRC and explicit timestamp validity."""

import os
import struct
import zlib

from .protocol import require, uint

RECORD_BYTES = 512
EVENT_MAGIC = b"LTE0051\x00"
BATCH_MAGIC = b"LTB0051\x00"
EVENT_STATUS = {
    "undecided": 1,
    "admitted": 2,
    "rejected_capacity": 3,
    "rejected_contention": 4,
    "missed_late": 5,
    "missed_catchup_cap": 6,
    "missed_horizon": 7,
}
STAGE = {
    "staged": 1,
    "active": 2,
    "read_intent": 3,
    "read_return": 4,
    "feature_intent": 5,
    "features": 6,
    "score_intent": 7,
    "decision": 8,
    "output": 9,
    "control": 10,
    "verified": 11,
    "failed": 12,
    "cancelled": 13,
}
EVENT_TIMES = (
    "intended",
    "submission",
    "admission",
    "rejection",
    "observed",
    "detection",
    "terminal",
)
BATCH_TIMES = (
    "dispatch",
    "read_start",
    "read_return",
    "features",
    "decision",
    "output",
    "control_end",
    "terminal",
)
EVENT_FIELDS = {
    "version": (8, "H"),
    "status": (10, "H"),
    "reason": (12, "H"),
    "phase": (14, "H"),
    "run": (16, "I"),
    "k": (24, "Q"),
    "prefix": (32, "I"),
    "cycle": (36, "I"),
    "sequence": (104, "Q"),
}
EXTRA_TIMES = ("feature_intent", "score_intent", "reference_intent", "reference_return")
BATCH_FIELDS = {
    "version": (8, "H"),
    "phase": (10, "H"),
    "run": (12, "I"),
    "batch": (16, "I"),
    "m": (20, "H"),
    "reason": (22, "H"),
    "status": (24, "H"),
    "missing_reason": (26, "H"),
}
COUNTERS = (
    "read_intents",
    "read_rows",
    "feature_intents",
    "feature_rows",
    "score_intents",
    "score_rows",
    "reference_intents",
    "reference_rows",
)


def _put(buf, offset, fmt, value):
    struct.pack_into("<" + fmt, buf, offset, uint(value, struct.calcsize(fmt) * 8))


def encode(record, kind):
    require(kind in ("event", "batch"), "Record kind")
    event = kind == "event"
    require(
        record.get("status") in (EVENT_STATUS.values() if event else STAGE.values()),
        "Known record state",
    )
    buf = bytearray(RECORD_BYTES)
    buf[:8] = EVENT_MAGIC if event else BATCH_MAGIC
    fields = EVENT_FIELDS if event else BATCH_FIELDS
    for key, (off, fmt) in fields.items():
        _put(buf, off, fmt, record.get(key, 1 if key == "version" else 0))
    times = EVENT_TIMES if event else BATCH_TIMES
    mask, start, mask_offset = 0, 48 if event else 32, 40 if event else 28
    for i, key in enumerate(times):
        value = record.get(key)
        if value is not None:
            mask |= 1 << i
            _put(buf, start + 8 * i, "Q", value)
    if not event:
        for i, key in enumerate(EXTRA_TIMES):
            if record.get(key) is not None:
                mask |= 1 << (8 + i)
                _put(buf, 128 + 8 * i, "Q", record[key])
    _put(buf, mask_offset, "Q" if event else "I", mask)
    if not event:
        require(1 <= record.get("m", 0) <= 8, "Batch record shape")
        for key, off, fmt in (
            ("members", 96, "I"),
            ("positions", 160, "I"),
            ("dequeues", 192, "Q"),
            ("admissions", 256, "Q"),
            ("subread_starts", 320, "Q"),
            ("subread_ends", 384, "Q"),
        ):
            values = record.get(key, [])
            require(len(values) <= 8, "Fixed8-member record")
            if key in ("members", "positions", "dequeues", "admissions"):
                require(len(values) == record["m"], "Complete member fields")
            for i, value in enumerate(values):
                _put(buf, off + i * struct.calcsize(fmt), fmt, value)
        for i, key in enumerate(COUNTERS):
            _put(buf, 448 + 4 * i, "I", record.get(key, 0))
        digest = record.get("digest", bytes(16))
        require(len(digest) == 16, "Fixed digest")
        buf[480:496] = digest
        _put(buf, 496, "Q", record.get("flags", 0))
    _put(buf, 504, "Q", zlib.crc32(buf[:504]))
    return bytes(buf)


def decode(blob, kind):
    require(len(blob) == RECORD_BYTES, "Record size")
    if blob == bytes(RECORD_BYTES):
        return None  # explicit absent record, not a zero timestamp
    event = kind == "event"
    require(blob[:8] == (EVENT_MAGIC if event else BATCH_MAGIC), "Record magic")
    require(
        struct.unpack_from("<Q", blob, 504)[0] == zlib.crc32(blob[:504]),
        "Torn/corrupt record",
    )
    fields = EVENT_FIELDS if event else BATCH_FIELDS
    result = {
        key: struct.unpack_from("<" + fmt, blob, off)[0]
        for key, (off, fmt) in fields.items()
    }
    require(result["version"] == 1, "Record version")
    times = EVENT_TIMES if event else BATCH_TIMES
    mask = struct.unpack_from("<Q" if event else "<I", blob, 40 if event else 28)[0]
    require(mask < 1 << (len(times) + (0 if event else 4)), "Unknown timestamp flags")
    for i, key in enumerate(times):
        value = struct.unpack_from("<Q", blob, (48 if event else 32) + 8 * i)[0]
        require(mask & (1 << i) or value == 0, "Invalid null encoding")
        result[key] = value if mask & (1 << i) else None
    if not event:
        for i, key in enumerate(EXTRA_TIMES):
            value = struct.unpack_from("<Q", blob, 128 + 8 * i)[0]
            require(mask & (1 << (8 + i)) or value == 0, "Invalid extra null time")
            result[key] = value if mask & (1 << (8 + i)) else None
        m = result["m"]
        require(1 <= m <= 8, "Batch record shape")
        for key, off, fmt in (
            ("members", 96, "I"),
            ("positions", 160, "I"),
            ("dequeues", 192, "Q"),
            ("admissions", 256, "Q"),
            ("subread_starts", 320, "Q"),
            ("subread_ends", 384, "Q"),
        ):
            size = 8 if key.startswith("subread") else m
            result[key] = list(struct.unpack_from("<" + fmt * size, blob, off))
        for i, key in enumerate(COUNTERS):
            result[key] = struct.unpack_from("<I", blob, 448 + 4 * i)[0]
        result["digest"] = blob[480:496]
        result["flags"] = struct.unpack_from("<Q", blob, 496)[0]
    # Canonical re-encoding also rejects nonzero unused/reserved bytes.
    require(encode(result, kind) == blob, "Noncanonical/reserved record bytes")
    return result


class Store:
    def __init__(self, path, capacity, kind, create=False):
        require(type(capacity) is int and 1 <= capacity <= 768, "Record capacity")
        self.capacity, self.kind = capacity, kind
        self.fd = os.open(
            path, os.O_RDWR | (os.O_CREAT | os.O_EXCL if create else 0), 0o600
        )
        if create:
            os.ftruncate(self.fd, capacity * RECORD_BYTES)
        require(
            os.fstat(self.fd).st_size == capacity * RECORD_BYTES, "Fixed record file"
        )

    def write(self, index, record):
        require(0 <= index < self.capacity, "Record storage overflow")
        blob = encode(record, self.kind)
        require(
            os.pwrite(self.fd, blob, index * RECORD_BYTES) == RECORD_BYTES,
            "Short journal write",
        )

    def read_all(self):
        return [
            decode(os.pread(self.fd, RECORD_BYTES, i * RECORD_BYTES), self.kind)
            for i in range(self.capacity)
        ]

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


def reconcile(events, batches, scheduler, cutoff):
    """Bounded post-exit projection. Never infer absence of unrecorded side effects."""
    require(
        len(events) == scheduler.count and len(batches) <= scheduler.count,
        "Reconciliation capacity",
    )
    membership = {}
    for b in filter(None, batches):
        for i, k in enumerate(b["members"]):
            require(k not in membership, "Duplicate admitted presentation")
            membership[k] = (b, i)
    out = dict(
        offered=0,
        unresolved=0,
        missed=0,
        submitted=0,
        undecided=0,
        rejected_capacity=0,
        rejected_contention=0,
        admitted=0,
        ring=0,
        staged=0,
        active=0,
        completed=0,
        failed=0,
        cancelled=0,
        future=0,
        uncertain=0,
    )

    def reached(t):
        return t is not None and t <= cutoff

    for k, e in enumerate(events):
        if scheduler.intended(k) > cutoff:
            out["future"] += 1
            continue
        out["offered"] += 1
        bi = membership.get(k)
        admission = e.get("admission") if e else None
        if bi:
            admission = bi[0]["admissions"][bi[1]]
        if e and reached(e.get("submission")):
            out["submitted"] += 1
        elif reached(admission):
            # Admission proves a submission even when its final producer record is missing.
            out["submitted"] += 1
        elif e and reached(e.get("observed")) and e["status"] in (5, 6, 7):
            out["missed"] += 1
            continue
        else:
            out["unresolved"] += 1
            continue
        if reached(admission):
            out["admitted"] += 1
        elif e and reached(e.get("rejection")):
            require(e["status"] in (3, 4), "Rejection reason")
            out["rejected_capacity" if e["status"] == 3 else "rejected_contention"] += 1
            continue
        else:
            out["undecided"] += 1
            out["uncertain"] += 1
            continue
        if not bi or not reached(bi[0]["dequeues"][bi[1]]):
            out["ring"] += 1
        elif reached(bi[0].get("output")):
            out["completed"] += (
                1  # subsequent reference/cleanup failure cannot erase output
            )
        elif reached(bi[0].get("terminal")) and bi[0]["status"] == STAGE["failed"]:
            out["failed"] += 1
        elif reached(bi[0].get("terminal")) and bi[0]["status"] == STAGE["cancelled"]:
            out["cancelled"] += 1
        elif reached(bi[0].get("dispatch")):
            out["active"] += 1
            out["uncertain"] += 1
        else:
            out["staged"] += 1
    require(
        out["offered"] == out["unresolved"] + out["missed"] + out["submitted"],
        "Offer conservation",
    )
    require(
        out["submitted"]
        == out["undecided"]
        + out["rejected_capacity"]
        + out["rejected_contention"]
        + out["admitted"],
        "Submission conservation",
    )
    require(
        out["admitted"]
        == sum(
            out[k]
            for k in ("ring", "staged", "active", "completed", "failed", "cancelled")
        ),
        "Admission conservation",
    )
    out["boolean_outputs"] = 4 * out["completed"]
    return out


class Phases:
    """32 fixed512-byte records per role, single writer; no control-message use."""

    LAYOUT = struct.Struct("<8sHHIQQQ464sQ")

    def __init__(self, path, role, create=False):
        require(role in (1, 2, 3), "Phase owner role")
        self.role, self.index = role, 0
        self.fd = os.open(
            path, os.O_RDWR | (os.O_CREAT | os.O_EXCL if create else 0), 0o600
        )
        if create:
            os.ftruncate(self.fd, 32 * 512)
        require(os.fstat(self.fd).st_size == 32 * 512, "Fixed phase file")

    def append(self, code, clocks, rss):
        require(self.index < 32, "Phase record overflow")
        service, continuous, _ = clocks.observation()
        blob = self.LAYOUT.pack(
            b"LTP0051\x00",
            1,
            self.role,
            uint(code, 32),
            uint(service),
            uint(continuous),
            uint(rss),
            bytes(464),
            0,
        )
        blob = blob[:504] + struct.pack("<Q", zlib.crc32(blob[:504]))
        require(
            os.pwrite(self.fd, blob, self.index * 512) == 512,
            "Phase journal short write",
        )
        self.index += 1

    def read_all(self):
        result = []
        for i in range(32):
            blob = os.pread(self.fd, 512, i * 512)
            if blob == bytes(512):
                continue
            magic, version, role, code, service, continuous, rss, pad, crc = (
                self.LAYOUT.unpack(blob)
            )
            require(
                magic == b"LTP0051\x00"
                and version == 1
                and role == self.role
                and pad == bytes(464)
                and crc == zlib.crc32(blob[:504]),
                "Phase corruption",
            )
            result.append(
                dict(
                    role=role,
                    code=code,
                    service_ns=service,
                    continuous_ns=continuous,
                    RSS_bytes=rss,
                )
            )
        return result

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


def timing_summary(events, batches, cutoff):
    """Conditional generated-fixture observations; never impute missing outputs."""
    require(len(events) <= 768 and len(batches) <= 768, "Timing buffer capacity")
    values = {
        k: []
        for k in ("offered_latency", "producer_lag", "queue_wait", "joint_service")
    }
    pending_overdue = 0
    for e in filter(None, events):
        if e.get("submission") is not None and e["submission"] <= cutoff:
            require(e["submission"] >= e["intended"], "Producer clock ordering")
            values["producer_lag"].append(e["submission"] - e["intended"])
    for b in filter(None, batches):
        for i, k in enumerate(b["members"]):
            e = events[k]
            if b.get("output") is not None and b["output"] <= cutoff:
                require(e is not None, "Missing offer origin")
                values["offered_latency"].append(b["output"] - e["intended"])
                values["queue_wait"].append(b["dispatch"] - b["admissions"][i])
                values["joint_service"].append(b["output"] - b["read_start"])
            elif (
                e
                and b["admissions"][i] <= cutoff
                and cutoff - e["intended"] > 100_000_000
            ):
                pending_overdue += 1
    # Include ring-resident pending rows, disjoint from batches.
    members = {k for b in filter(None, batches) for k in b["members"]}
    for k, e in enumerate(events):
        if (
            k not in members
            and e
            and e.get("admission") is not None
            and e["admission"] <= cutoff
            and cutoff - e["intended"] > 100_000_000
        ):
            pending_overdue += 1
    result = {}
    for key, samples in values.items():
        require(all(x >= 0 for x in samples), "Cross-process/stage clock ordering")
        result[key] = {
            "n": len(samples),
            "maximum_ns": max(samples) if samples else None,
        }
    result["completed_illustrative_100ms_misses"] = sum(
        x > 100_000_000 for x in values["offered_latency"]
    )
    result["pending_overdue_at_cutoff"] = pending_overdue
    result["interpretation"] = (
        "Generated fixture maxima/counts only; no operational p99, overhead subtraction, throughput or physical inference"
    )
    return result


def stage_projection(batches, cutoff):
    """Per-operation intent/return/failure/uncertainty projected at any timestamp."""
    from collections import Counter

    result = {
        key: dict(
            intents=0, returned_calls=0, returned_rows=0, failed=0, inflight_uncertain=0
        )
        for key in ("read", "feature", "score", "reference")
    }
    for b in filter(None, batches):
        counts = Counter(b["positions"])
        layer_rows = [
            sum(n > j for n in counts.values()) for j in range(max(counts.values()))
        ]
        returned_layers = 0
        row_count = 0
        while (
            returned_layers < len(layer_rows)
            and row_count + layer_rows[returned_layers] <= b["read_rows"]
        ):
            row_count += layer_rows[returned_layers]
            returned_layers += 1
        require(row_count == b["read_rows"], "Selected row return ledger")
        failed = (
            b.get("terminal") is not None
            and b["terminal"] <= cutoff
            and b["status"] == STAGE["failed"]
        )
        for j in range(b["read_intents"]):
            if b["subread_starts"][j] > cutoff:
                continue
            result["read"]["intents"] += 1
            if j < returned_layers and b["subread_ends"][j] <= cutoff:
                result["read"]["returned_calls"] += 1
                result["read"]["returned_rows"] += layer_rows[j]
            else:
                result["read"]["failed" if failed else "inflight_uncertain"] += 1
        for stage, end in (
            ("feature", "features"),
            ("score", "decision"),
            ("reference", "reference_return"),
        ):
            intent = b.get(stage + "_intent")
            if intent is None or intent > cutoff:
                continue
            result[stage]["intents"] += 1
            if b.get(end) is not None and b[end] <= cutoff:
                result[stage]["returned_calls"] += 1
                result[stage]["returned_rows"] += b["m"]
            else:
                result[stage]["failed" if failed else "inflight_uncertain"] += 1
    return result
