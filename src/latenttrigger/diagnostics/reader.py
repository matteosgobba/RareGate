"""Owned test features only; explicit full membership accounting; no broad store."""

import hashlib

import numpy as np

from latenttrigger.diagnostics import protocol as p


class AccessLedger:
    def __init__(self, path):
        self.path = path
        self.records = []
        self.inflight = None
        self.used = set()
        self.flush()

    def flush(self):
        value = self.summary()
        p.require(len(str(value).encode()) < 2**20, "Access journal bound")
        p.durable_json(self.path, value)

    def record(self, kind, source, count):
        self.records.append(dict(kind=kind, source=source, count=count))
        self.flush()

    def begin(self, kind, source, count):
        key = (kind, source)
        p.require(
            key not in self.used and self.inflight is None,
            "Duplicate/inflight numerical request",
        )
        self.used.add(key)
        self.inflight = dict(kind=kind, source=source, expected=count, confirmed=0)
        self.flush()  # BEFORE numerical access.

    def complete(self):
        r = self.inflight
        p.require(r is not None, "Absent request")
        self.records.append(
            dict(kind=r["kind"], source=r["source"], count=r["expected"])
        )
        self.inflight = None
        self.flush()

    def summary(self):
        counts = {
            kind: sum(r["count"] for r in self.records if r["kind"] == kind)
            for kind in ("feature_population", "stored_scores", "membership_metadata")
        }
        return dict(
            records=self.records,
            potential_inflight=self.inflight,
            feature_population_requests=sum(
                r["kind"] == "feature_population" for r in self.records
            ),
            feature_rows_read=counts["feature_population"],
            stored_score_array_loads=sum(
                r["kind"] == "stored_scores" for r in self.records
            ),
            stored_score_values_read=counts["stored_scores"],
            membership_array_loads=sum(
                r["kind"] == "membership_metadata" for r in self.records
            ),
            membership_records_read=counts["membership_metadata"],
            new_model_forward_calls=0,
            new_reconstruction_computations=0,
            new_AUC_AP_or_significance_computations=0,
            new_fingerprint_numeric_loads=0,
            optimizer_updates=0,
            downloads=0,
        )


def validate_membership(codes, ids, labels, plan):
    n = plan["original_rows"]
    p.require(
        codes.shape == ids.shape == labels.shape == (n,)
        and codes.dtype.str == labels.dtype.str == "|u1"
        and ids.dtype.str == "<i8",
        "Membership layout",
    )
    p.require(
        np.array_equal(ids, np.arange(n, dtype=np.int64)),
        "Complete ascending original source IDs",
    )
    roles = {
        "train_background": 1,
        "validation_selection_background": 2,
        "validation_calibration_background": 3,
        "test_background": 4,
        "test_signal": 5,
    }
    p.require(np.isin(codes, list(roles.values())).all(), "Wrong roles")
    p.require(
        {k: int(np.count_nonzero(codes == v)) for k, v in roles.items()}
        == plan["role_counts"],
        "Wrong role counts",
    )
    p.require(
        np.isin(labels, [0, 1]).all()
        and (labels[codes < 5] == 0).all()
        and (labels[codes == 5] == 1).all(),
        "Wrong membership labels",
    )
    selected = {
        name: np.flatnonzero(codes == role)
        for name, role in [("background", 4), ("two_prong", 5)]
    }
    for candidate in p.CANDIDATES:
        ledger = plan["ledgers"][candidate]
        p.require(
            len(ledger) == 2
            and {r["split"] for r in ledger} == {"test_background", "test_signal"},
            "Ledger role coverage",
        )
        for name, positions in selected.items():
            role = "test_background" if name == "background" else "test_signal"
            r = next(r for r in ledger if r["split"] == role)
            count = plan["counts"][name]
            p.require(
                len(positions) == count
                and r["expected_count"]
                == r["confirmed_events_read"]
                == r["confirmed_events_scored"]
                == count
                and r["status"] == "complete"
                and r["inflight"] is None
                and r["allow_test"] is True
                and r["include_labels"] is True
                and r["dev_only"] is False,
                "Complete original role lineage",
            )
            batches = r["batches"]
            p.require(
                r["completed_score_batches"] == len(batches) == (count + 4095) // 4096,
                "Ledger complete batches",
            )
            for i, b in enumerate(batches):
                subset = ids[positions[i * 4096 : (i + 1) * 4096]]
                p.require(
                    b["index"] == i
                    and b["rows_read"] == b["rows_scored"] == len(subset)
                    and b["first_source_id"] == int(subset[0])
                    and b["last_source_id"] == int(subset[-1]),
                    "Accepted batch source order mismatch",
                )
    return selected, {
        k: dict(
            count=len(v),
            first_source_id=int(ids[v[0]]),
            last_source_id=int(ids[v[-1]]),
            selected_ids_raw_bytes_sha256=hashlib.sha256(ids[v].tobytes()).hexdigest(),
        )
        for k, v in selected.items()
    }


class NarrowReader:
    def __init__(self, root, plan, ledger, check=lambda: None):
        self.root, self.plan, self.ledger, self.check = root, plan, ledger, check
        self.membership = None
        self.original_map = None
        self.alignment = None

    def path(self, name):
        p.require(name in self.plan["arrays"], "Input outside numerical allowlist")
        return p.fixed(self.root, name)

    def memberships(self):
        p.require(self.membership is None, "Repeated membership scan")
        values = []
        for name in ("split_codes.npy", "event_ids.npy", "labels.npy"):
            source = self.plan["original"] + "/" + name
            self.check()
            self.ledger.begin("membership_metadata", source, self.plan["original_rows"])
            values.append(np.load(self.path(source), allow_pickle=False))
            self.ledger.complete()
            self.ledger.record("implicit_numpy_array_header", source, 128)
        self.membership, self.alignment = validate_membership(*values, self.plan)
        self.ledger.record(
            "membership_validation",
            "original roles/IDs/labels; no feature values",
            self.plan["original_rows"],
        )
        return self.alignment

    def feature_population(self, population):
        p.require(population in p.POPULATIONS, "Wrong feature population")
        p.require(
            self.membership is not None, "Select memberships before feature values"
        )
        count = self.plan["counts"][population]
        self.check()
        self.ledger.begin("feature_population", population, count)
        if population != "three_prong":
            if self.original_map is None:
                name = self.plan["original"] + "/event_features.npy"
                self.original_map = np.load(
                    self.path(name), mmap_mode="r", allow_pickle=False
                )
                self.ledger.record("feature_header_mapping_no_population_scan", name, 1)
                self.ledger.record("implicit_numpy_array_header", name, 128)
            x = np.array(
                self.original_map[self.membership[population]], copy=True, order="C"
            )
        else:
            name = self.plan["prepared"] + "/event_features.npy"
            x = np.load(self.path(name), allow_pickle=False)
            self.ledger.record("implicit_numpy_array_header", name, 128)
        self.ledger.complete()
        self.check()
        p.require(
            x.shape == (count, 8) and x.dtype.str == "<f4" and np.isfinite(x).all(),
            "Complete finite FP32 frozen features",
        )
        return x

    def scores(self, candidate, population):
        name = self.plan["scores"][candidate + "/" + population]
        count = self.plan["counts"][population]
        self.check()
        self.ledger.begin("stored_scores", name, count)
        values = np.load(self.path(name), allow_pickle=False)
        self.ledger.complete()
        self.ledger.record("implicit_numpy_array_header", name, 128)
        self.check()
        p.require(
            values.shape == (count,)
            and values.dtype.str == "<f8"
            and np.isfinite(values).all()
            and (values >= 0).all(),
            "Complete finite nonnegative FP64 scores",
        )
        return values

    def close(self):
        if self.original_map is not None:
            self.original_map._mmap.close()
        self.original_map = self.membership = None
