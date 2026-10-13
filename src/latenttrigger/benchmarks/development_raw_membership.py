"""Only the one approved development ID array may be resolved numerically."""

import hashlib

import numpy as np

from latenttrigger.benchmarks import development_raw_protocol as p


def resolve(values, expected_selected_hash):
    p.require(
        values.shape == (6999,)
        and values.dtype == np.dtype("<i8")
        and values.flags.c_contiguous,
        "Complete little-endian6999-ID source",
    )
    p.require(
        np.all((values >= 0) & (values < 1100000)) and len(np.unique(values)) == 6999,
        "Unique in-domain IDs",
    )
    ordered = np.sort(values, kind="stable")
    selected = np.array(ordered[:1024], dtype="<i8", order="C", copy=True)
    p.require(
        hashlib.sha256(selected.tobytes()).hexdigest() == expected_selected_hash,
        "Historical1024prefix identity; no row substitution",
    )
    selected.setflags(write=False)
    return selected


def load_once(path, spec, audit, persist):
    p.require(
        audit.get("membership_load_attempts", 0) == 0, "One operational membership load"
    )
    p.require(
        path.absolute() == path.resolve() and p.file_hash(path) == spec["file_sha256"],
        "Membership source bytes/nonsymlink",
    )
    p.header(path, [6999], "<i8", 56120)
    audit["membership_load_attempts"] = 1
    audit["membership_inflight"] = True
    persist()
    values = np.load(path, allow_pickle=False)
    audit.update(membership_loads=1, membership_records_inspected=int(values.size))
    persist()
    selected = resolve(values, spec["selected_sha256"])
    audit.update(
        membership_loads=1,
        membership_records_inspected=6999,
        selected_IDs=1024,
        membership_inflight=False,
    )
    persist()
    return selected
