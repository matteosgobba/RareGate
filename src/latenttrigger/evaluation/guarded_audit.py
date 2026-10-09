"""Durable pre-read and per-batch exposure; files never manufacture human consent."""

import json
import os
from pathlib import Path

from latenttrigger.benchmarks import protocol as p


def durable(path, document):
    path = Path(path)
    temp = path.with_name(path.name + ".owned-tmp")
    payload = (json.dumps(document, indent=2, allow_nan=False) + "\n").encode()
    if len(payload) > 2**20:
        raise ValueError("Bounded exposure journal exceeded.")
    with temp.open("wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Journal:
    def __init__(self, path, binding):
        self.path = Path(path)
        if self.path.exists():
            raise ValueError("Existing exposure journal; no overwrite/resume.")
        self.document = dict(
            schema_version=1,
            status="authorized_no_population_request_yet",
            binding=binding,
            population_access=[],
            optimizer_updates=0,
        )
        self.persist()

    def persist(self):
        durable(self.path, self.document)

    def request(self, split, expected):
        if split not in ("test_background", "test_signal"):
            raise ValueError("Only preregistered held-out populations.")
        previous = self.document["population_access"]
        order = ("test_background", "test_signal")
        if len(previous) >= 2 or split != order[len(previous)]:
            raise ValueError("Duplicate/out-of-order population request.")
        self.document["status"] = "unblinding_exposed"
        row = dict(
            split=split,
            requested_utc=p.now(),
            allow_test=True,
            include_labels=True,
            dev_only=False,
            expected_count=expected,
            confirmed_events_read=0,
            confirmed_events_scored=0,
            completed_score_batches=0,
            batches=[],
            inflight=dict(kind="iterator_creation"),
        )
        previous.append(row)
        self.persist()
        return row

    def inflight(self, row, kind, index, expected):
        row["inflight"] = dict(
            kind=kind, batch_index=index, expected_rows=expected, utc=p.now()
        )
        self.persist()

    def read(self, row, index, count):
        row["confirmed_events_read"] += count
        row["batches"].append(dict(index=index, rows_read=count, rows_scored=0))
        row["inflight"] = None
        self.persist()

    def scored(self, row, count):
        row["confirmed_events_scored"] += count
        row["completed_score_batches"] += 1
        row["batches"][-1]["rows_scored"] = count
        row["inflight"] = None
        self.persist()

    def failed(self, error):
        self.document.update(
            status="failed_or_interrupted_exposure"
            if self.document["population_access"]
            else "failed_before_population",
            error=str(error),
        )
        self.persist()


def exposure(path):
    if not Path(path).exists():
        return dict(
            population_requests=0,
            confirmed_events_read=0,
            confirmed_events_scored=0,
            potential_inflight=False,
            exposed=False,
            journal_exists=False,
        )
    d = p.read(path)
    rows = d["population_access"]
    return dict(
        population_requests=len(rows),
        confirmed_events_read=sum(r["confirmed_events_read"] for r in rows),
        confirmed_events_scored=sum(r["confirmed_events_scored"] for r in rows),
        potential_inflight=any(r["inflight"] is not None for r in rows),
        exposed=bool(rows),
        journal_exists=True,
        status=d["status"],
    )
