"""Task0031 bounded durable scientific access ledger; every sensitive read declared."""

from raregate.benchmarks import protocol as p
from raregate.evaluation.three_prong_audit import Audit as BaseAudit

KINDS = (
    "raw_custody",
    "signal_preparation",
    "column_items",
    "column_axis",
    "row_axis",
    "original_fingerprint_integrity",
    "candidate_constructor_provenance",
    "signal_model_evaluation",
    "cached_background_numeric_reuse",
    "reporting_owned_curves",
    "reporting_owned_metrics",
    "historical_aggregate_tables",
)


class Audit(BaseAudit):
    def persist(self):
        if len(str(self.document).encode()) > 2**20:
            raise ValueError("Bounded1MiB access ledger ceiling")
        super().persist()

    def request(self, kind, count, *, source=None):
        if kind not in KINDS or any(
            r["kind"] == kind for r in self.document["records"]
        ):
            raise ValueError("Unknown/duplicate declared access")
        row = dict(
            kind=kind,
            source=source,
            requested_UTC=p.now(),
            expected=count,
            confirmed_read=0,
            confirmed_scored=0,
            batches=[],
            inflight="before_open",
        )
        self.document["records"].append(row)
        self.persist()
        return row


def exposure(path):
    doc = p.read(path) if path.exists() else dict(records=[])
    records = doc["records"]
    signal = [r for r in records if r["kind"] == "signal_model_evaluation"]
    return dict(
        new_signal_model_accessed=bool(signal),
        signal_model_requests=len(signal),
        signal_scored_presentations=sum(r["confirmed_scored"] for r in signal),
        signal_batches=sum(len(r["batches"]) for r in signal),
        cached_numeric_loads=sum(
            r["kind"] == "cached_background_numeric_reuse" for r in records
        ),
        fingerprint_numeric_loads=sum(
            r["kind"] == "original_fingerprint_integrity" for r in records
        ),
        raw_custody_requests=sum(r["kind"] == "raw_custody" for r in records),
        prepared_rows=sum(
            r["confirmed_read"] for r in records if r["kind"] == "signal_preparation"
        ),
        potential_inflight=any(r["inflight"] is not None for r in records),
        records=records,
    )
