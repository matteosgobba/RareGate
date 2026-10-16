"""Task0041 ceilings and lifecycle adapters; no historical controller changes."""

import os
import sys
from pathlib import Path

from raregate.benchmarks import development_decision_protocol as p
from raregate.benchmarks.guard import parent_check
from raregate.benchmarks.prepared_service_runtime import ServiceGuard, storage
from raregate.benchmarks.prepared_service_runtime import (
    check_access as file_access,
)
from raregate.data.three_prong_v3_runtime import (
    ContinuousClock,
    IdleAssertion,
    alarm,
    check_deadline,
    supervise,
)

__all__ = [
    "ServiceGuard",
    "storage",
    "ContinuousClock",
    "IdleAssertion",
    "alarm",
    "check_deadline",
    "supervise",
    "parent_check",
    "boundary",
    "accept",
    "accounting",
]


def boundary(directory, grant):
    allowed = set()
    if not grant["synthetic_only"] and grant["phase"] != "reporting":
        allowed = {
            p.ROOT / v
            for v in (
                *p.load()["byte_pins"],
                *(v["path"] for v in p.load()["historical_acceptances"].values()),
                p.MEMBERSHIP,
                p.RAW,
                p.GOLDEN,
            )
        }
    if grant["phase"] == "reporting":
        allowed = {
            directory.parent / f"repetition{i}" / name
            for i in (1, 2, 3)
            for name in ("aggregate.json", "receipt.json", "grant.json")
        }
    sys.addaudithook(
        lambda event, args: check_access(
            p.ROOT,
            directory,
            allowed,
            event,
            args,
            synthetic=grant["synthetic_only"] and grant["phase"] != "reporting",
        )
    )


def accounting(a):
    from raregate.benchmarks.development_decision_planning import (
        CANDIDATES,
        counts,
    )

    expected = counts()["per_worker"]
    p.require(
        a["membership_loads"] == 1
        and a["membership_records_inspected"] == 6999
        and a["selected_IDs"] == 1024
        and a["membership_inflight"] is False
        and a["golden_loads"] == 1
        and a["golden_rows"] == 1024
        and a["golden_inflight"] is False
        and a["HDF_opens"] == 1
        and a["HDF_closed"] is True
        and a["model_loads"] == a["threshold_loads"] == a["model_instantiations"] == 2
        and a["model_inflight"] is None
        and a["inflight"] is None,
        "Complete original input/model/handle lifecycle",
    )
    p.require(
        a["raw_requests"]
        == a["raw_started_calls"]
        == a["raw_returned_requests"]
        == expected["raw_calls"]
        and a["raw_requested_rows"] == a["raw_returned_rows"] == expected["raw_rows"]
        and a["feature_requests"]
        == a["feature_started_calls"]
        == a["feature_completed_calls"]
        == expected["raw_calls"]
        and a["feature_requested_rows"]
        == a["feature_completed_rows"]
        == expected["raw_rows"]
        and a["adapter_requests"]
        == a["adapter_started_calls"]
        == a["adapter_completed_calls"]
        == a["decision_completed_calls"]
        == expected["service_calls"]
        and a["adapter_requested_rows"]
        == a["adapter_completed_rows"]
        == a["decision_completed_rows"]
        == expected["service_rows"]
        and a["decision_boolean_values"] == 4 * expected["service_rows"],
        "Nested raw/feature/adapter/decision conservation",
    )
    for name in CANDIDATES:
        p.require(
            a["by_candidate"][name]
            == dict(
                raw_calls=140,
                raw_rows=5915,
                feature_calls=140,
                feature_rows=5915,
                adapter_calls=164,
                adapter_rows=6929,
            ),
            "All candidate calls retained",
        )
    p.require(
        a["by_component"]
        == dict(
            timed=dict(
                raw_calls=160,
                raw_rows=6760,
                feature_calls=160,
                feature_rows=6760,
                adapter_calls=160,
                adapter_rows=6760,
            ),
            warmup=dict(
                raw_calls=24,
                raw_rows=1014,
                feature_calls=24,
                feature_rows=1014,
                adapter_calls=24,
                adapter_rows=1014,
            ),
            chain_gate=dict(
                raw_calls=96,
                raw_rows=4056,
                feature_calls=96,
                feature_rows=4056,
                adapter_calls=96,
                adapter_rows=4056,
            ),
            golden_reference=dict(
                raw_calls=0,
                raw_rows=0,
                feature_calls=0,
                feature_rows=0,
                adapter_calls=48,
                adapter_rows=2028,
            ),
        ),
        "Per-component schedule accounting",
    )


def accept(body, dispatch, grant, directory, clock, deadline):
    check_deadline(clock, deadline)
    p.require(
        body["status"] == "body_complete_awaiting_exit"
        and body["identity"] == grant["identity"]
        and body["grant_sha256"] == p.file_hash(directory / "grant.json")
        and body["source_map"] == grant["source_map"] == p.source_map()
        and body["dependencies"] == grant["dependencies"] == p.dependencies(),
        "Complete frozen body",
    )
    p.require(
        type(dispatch.get("returncode")) is int
        and dispatch["returncode"] == 0
        and dispatch["parent_confirms_normal_exit"] is True
        and dispatch["child_reaped"] is True
        and dispatch["within_deadline"] is True
        and dispatch["parent_error"] is None,
        "Normal exit/reaping/continuous cap",
    )
    r = body["resources"]
    cap = 60 if grant["phase"] == "reporting" else 180
    p.require(
        r["latched_error"] is None
        and r["owned_thread_alive"] is False
        and 0 < r["peak_rss_bytes"] <= 2**30
        and 0 < r["native_heap_reserved_bytes"] <= 512 * 2**20
        and body["cleanup_seconds"] <= 2
        and body["worker_seconds"] <= cap,
        "Resources/cleanup/worker caps",
    )
    expected = (
        {
            "cells.csv",
            "summary.json",
            "joint-cost.png",
            "chronology.png",
        }
        if grant["phase"] == "reporting"
        else {"aggregate.json", "timings.jsonl", "timer.json"}
    )
    p.require(set(body["outputs"]) == expected, "Fixed output coverage")
    for name, sha in body["outputs"].items():
        p.require(p.file_hash(directory / name) == sha, "Output identity")
    if grant["phase"] != "reporting":
        accounting(body["access"])
    return dict(
        status="parent_accepted_worker",
        normal_exit_reaped=True,
        terminal_resource_gap_seconds=max(
            0, dispatch["end_continuous"] - body["monitor_closed_continuous"]
        ),
    )


def check_access(root, owned, allowed, event, args, *, synthetic=False):
    if synthetic and event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).absolute()
        if (
            path == path.resolve()
            and path.is_relative_to(owned)
            and path.suffix in (".npy", ".h5")
        ):
            allowed = set(allowed) | {path}
    file_access(root, owned, allowed, event, args)
    if event == "import" and any(
        args[0] == name or args[0].startswith(name + ".")
        for name in (
            "raregate.training",
            "raregate.models.background",
            "raregate.models.particle",
            "raregate.data.preprocessing",
            "onnxruntime",
            "onnx",
        )
    ):
        raise PermissionError(
            "No training, preprocessing controller or alternate backend"
        )


class ProhibitedOperations:
    """Core may import ProcessedStore; all store/fitting/optimizer calls are refused."""

    def __init__(self, core):
        self.originals = []

        def refused(*args, **kwargs):
            raise PermissionError(
                "Task0041 prohibits store, fitting and optimizer execution"
            )

        targets = [
            (core, "prepare_input"),
            (core.ProcessedStore, "__init__"),
            (core.ProcessedStore, "iter_features"),
            (core.ProcessedStore, "iter_batches"),
            (core.PCAReconstruction, "fit"),
        ]
        from sklearn.decomposition import PCA

        targets.extend((PCA, name) for name in ("fit", "fit_transform"))
        targets.extend(
            [
                (core.torch.optim.Optimizer, "__init__"),
                (core.torch.optim.Adam, "step"),
                (core.torch.optim.SGD, "step"),
            ]
        )
        for obj, name in targets:
            self.originals.append((obj, name, obj.__dict__[name]))
            setattr(obj, name, refused)

    def restore(self):
        for obj, name, original in reversed(self.originals):
            setattr(obj, name, original)
