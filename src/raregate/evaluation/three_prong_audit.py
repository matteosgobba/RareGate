"""Separate raw custody, preparation, new model exposure and cached-score reuse."""

from raregate.benchmarks import protocol as p
from raregate.evaluation.guarded_audit import durable

KINDS = (
    "raw_acquisition",
    "raw_custody",
    "original_fingerprint_integrity",
    "signal_preparation",
    "signal_model_evaluation",
    "cached_background_numeric_reuse",
)


class Audit:
    def __init__(self, path, binding):
        if path.exists():
            raise ValueError("Existing audit; no resume")
        self.path = path
        self.document = dict(
            binding=binding,
            status="authorized_no_access_yet",
            records=[],
            optimizer_updates=0,
        )
        self.persist()

    def persist(self):
        durable(self.path, self.document)

    def request(self, kind, count):
        if kind not in KINDS or any(
            r["kind"] == kind for r in self.document["records"]
        ):
            raise ValueError("Unknown/duplicate access")
        row = dict(
            kind=kind,
            requested_utc=p.now(),
            expected=count,
            confirmed_read=0,
            confirmed_scored=0,
            batches=[],
            inflight="before_open",
        )
        self.document["records"].append(row)
        self.persist()  # fsync BEFORE network/open/np.load
        return row

    def inflight(self, row, kind, count):
        row["inflight"] = dict(kind=kind, expected=count)
        self.persist()

    def read(self, row, count):
        row["confirmed_read"] += count
        row["inflight"] = None
        self.persist()

    def scored(self, row, count):
        row["confirmed_scored"] += count
        row["batches"].append(count)
        row["inflight"] = None
        self.persist()

    def finish(self, status, error=None):
        self.document.update(status=status, error=error)
        self.persist()


def exposure(path):
    if not path.exists():
        return dict(
            new_signal_model_accessed=False,
            cached_numeric_loads=0,
            signal_scored_presentations=0,
            signal_batches=0,
            potential_inflight=False,
            records=[],
        )
    doc = p.read(path)
    records = doc["records"]
    signal = [r for r in records if r["kind"] == "signal_model_evaluation"]
    return dict(
        new_signal_model_accessed=bool(signal),
        cached_numeric_loads=sum(
            r["kind"] == "cached_background_numeric_reuse" for r in records
        ),
        signal_scored_presentations=sum(r["confirmed_scored"] for r in signal),
        signal_batches=sum(len(r["batches"]) for r in signal),
        potential_inflight=any(r["inflight"] is not None for r in records),
        records=records,
    )
