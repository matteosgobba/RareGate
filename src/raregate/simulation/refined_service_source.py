"""Closed Task0047 metadata reader. Stdlib only; embedded paths stay inert."""

import csv
import hashlib
import io
import json
import math
import struct
import sys
from dataclasses import dataclass, is_dataclass

from raregate.simulation import refined_service_protocol as p
from raregate.simulation.joint_engine import describe, integer

SUMMARY = "results/tables/final/task0047-targeted-partial-raw-decision-summary.json"
CELLS = SUMMARY.replace("summary.json", "cells.csv")
PAIRS = SUMMARY.replace("summary.json", "pairs.csv")
CONFIG = "configs/benchmarks/development_targeted_raw_decision_v1.json"
PROMPT = "docs/prompts/0047-targeted-partial-raw-decision-measurement.md"
ATTEMPT = "results/benchmarks/task0047-targeted-partial-raw-decisions/attempt.json"
SOURCE_STATUS = "parent_accepted_targeted_partial_raw_decision_measurement"
CONTRACT = "395074a5c554d80e4350eeea5041b459e71342c844e96f3b39eac75c5ba7364e"
SIDES = ("natural_m", "full_B_control")
PAIR_FIELDS = "candidate repetition B m wrapper case_class pair pair_id window_index window_position order_label natural_actual_rows control_actual_rows natural_model_shape_rows control_model_shape_rows natural_ns control_ns difference_ns ratio".split()
CELL_FIELDS = "candidate repetition B m side actual_rows model_shape_rows wrapper case_class scope strategy count minimum_ns maximum_ns mean_ns population_std_ns p50_ns p95_ns p99_ns mean_actual_event_ns hypothetical_bill_per_m_ns actual_events_per_second window_call_counts".split()
SELECTION = "results/tables/final/task0047-targeted-partial-selection.csv"
SELECTION_FIELDS = "B m case_class missing_rank selected_for_campaign observed_main_batches observed_main_events observed_main_assigned_ns zero_observed_frequency selection_bundle_sha256".split()


INPUT_INTEGRITY = dict(
    ids="f80a9483f5ddafcac0e05d9fd6de757e5bbfe9e805f65ced1c0aa801cc266f1a",
    golden="2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05",
    parameters="067a9bc07e81969b841018167adac05b6645a76cefd7f4c2967793ad3e99332b",
)
MODEL_INTEGRITY = {
    "pca-v1": [
        "296fce876211d6a298e3edfe211c15625ba164c42430c3402d10b53f264305dd",
        "c240ad0df661e168e446f7d14ab22803377e1cd09a41275f981c7f0cb7639547",
    ],
    "compact-autoencoder-v2": [
        "92e5c96f9b1bc72e4182f58d44b51bc66e9d32c68c0cde92c3064e3703aa26e4",
        "408dc57ea54cc933d4dc4fa62f9940cbd8f3ace0476accb423b328ea39fc21a1",
    ],
}
WORKER_COUNTS = dict(
    membership_loads=1,
    membership_records_inspected=6999,
    selected_IDs=1024,
    golden_loads=1,
    golden_rows=1024,
    HDF_opens=1,
    model_loads=2,
    threshold_loads=2,
    model_instantiations=2,
    raw_requests=4480,
    raw_started_calls=4480,
    raw_requested_rows=176890,
    raw_returned_requests=4480,
    raw_returned_rows=176890,
    feature_requests=4480,
    feature_started_calls=4480,
    feature_requested_rows=176890,
    feature_completed_calls=4480,
    feature_completed_rows=176890,
    adapter_requests=5248,
    adapter_started_calls=5248,
    adapter_requested_rows=207214,
    adapter_completed_calls=5248,
    adapter_completed_rows=207214,
    decision_completed_calls=5248,
    decision_completed_rows=207214,
    decision_boolean_values=828856,
)


def unique_pairs(items):
    result = {}
    for key, value in items:
        p.require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def strict_json(value):
    return json.loads(
        value,
        object_pairs_hook=unique_pairs,
        parse_constant=lambda x: p.require(False, "Nonfinite JSON"),
    )


def finite_tree(value):
    if type(value) is float:
        p.require(math.isfinite(value), "Finite metadata")
    elif type(value) is dict:
        for v in value.values():
            finite_tree(v)
    elif type(value) is list:
        for v in value:
            finite_tree(v)


def service_shape(b, k, side):
    p.require(
        type(b) is int and type(k) is int and (b, k) in p.CASES and side in SIDES,
        "Closed measured shape",
    )
    return (k, k) if side == SIDES[0] else (b, b)


def schedule(rep):
    integer(rep, "repetition", minimum=1, maximum=3)
    candidates = p.CANDIDATES if rep != 2 else p.CANDIDATES[::-1]
    cases = p.CASES if rep != 2 else p.CASES[::-1]
    for c in candidates:
        for b, k in cases:
            for phase, n in (("warmup", 3), ("timed", 20)):
                for i in range(n):
                    order = SIDES if i % 2 == 0 else SIDES[::-1]
                    for side_index, side in enumerate(order):
                        actual, service_b = service_shape(b, k, side)
                        yield dict(
                            repetition=rep,
                            candidate=c,
                            B=b,
                            m=k,
                            side=side,
                            actual_rows=actual,
                            model_shape_rows=service_b,
                            case_class=p.point_class(b, k),
                            wrapper=p.WRAPPER,
                            phase=phase,
                            pair=i,
                            pair_id=f"{rep}/{c}/{b}/{k}/{phase}/{i}",
                            window_index=i % 3,
                            window_position=(0, (1024 - b) // 2, 1024 - b)[i % 3],
                            side_index=side_index,
                            order_label=order[0] + "_first",
                        )


def stats(q):
    d = describe(q)
    mean = sum(q) / len(q)
    ordered = sorted(q)

    def quantile(prob):
        rank = (len(q) - 1) * prob
        lo = int(rank)
        fraction = rank - lo
        a, b = float(ordered[lo]), float(ordered[min(lo + 1, len(q) - 1)])
        difference = b - a
        return (
            a + difference * fraction
            if fraction < 0.5
            else b - difference * (1 - fraction)
        )

    return dict(
        count=len(q),
        minimum_ns=d["min"],
        maximum_ns=d["max"],
        mean_ns=mean,
        population_std_ns=math.sqrt(sum((x - mean) ** 2 for x in q) / len(q)),
        p50_ns=quantile(0.5),
        p95_ns=quantile(0.95),
        p99_ns=quantile(0.99),
    )


def agree(actual, expected):
    p.require(
        type(actual) in (int, float)
        and type(expected) in (int, float)
        and math.isfinite(actual)
        and math.isfinite(expected),
        "Finite numeric serialization",
    )
    if type(expected) is int:
        p.require(actual == expected, "Exact integer statistic")
    else:
        p.require(
            abs(actual - expected)
            <= 32 * max(math.ulp(float(actual)), math.ulp(expected)),
            "32ULP mechanical serialization",
        )


def check_stats(value, q):
    for name, expected in stats(q).items():
        if name == "count":
            p.require(
                type(value[name]) is int and value[name] == expected, "Exact count"
            )
        else:
            agree(value[name], expected)


def parse_csv(data, fields):
    reader = csv.DictReader(io.StringIO(data.decode(), newline=""))
    p.require(
        reader.fieldnames == fields,
        "Closed CSV header without duplicate/foreign fields",
    )
    rows = list(reader)
    p.require(
        rows
        and list(rows[0]) == fields
        and all(set(r) == set(fields) and None not in r.values() for r in rows),
        "Closed CSV schema",
    )
    strings = {
        "candidate",
        "side",
        "scope",
        "strategy",
        "pair_id",
        "order_label",
        "window_call_counts",
        "wrapper",
        "case_class",
        "selection_bundle_sha256",
    }
    floats = {
        "ratio",
        "minimum_ns",
        "maximum_ns",
        "mean_ns",
        "population_std_ns",
        "p50_ns",
        "p95_ns",
        "p99_ns",
        "mean_actual_event_ns",
        "hypothetical_bill_per_m_ns",
        "actual_events_per_second",
    }
    for r in rows:
        for k, v in r.items():
            if k in strings:
                continue
            if k in floats:
                r[k] = float(v)
                p.require(math.isfinite(r[k]), "Finite CSV statistic")
            else:
                p.require(
                    v and (v.isdecimal() or (v[0] == "-" and v[1:].isdecimal())),
                    "Integer CSV spelling",
                )
                r[k] = int(v)
    return rows


@dataclass(frozen=True)
class PairedVector:
    candidate: str
    repetition: int
    B: int
    k: int
    pairs: tuple
    pair_ids: tuple
    natural_model_shape_rows: int
    case_class: str = ""

    @property
    def sha256(self):
        return hashlib.sha256(
            b"".join(struct.pack("<qq", a, b) for a, b in self.pairs)
        ).hexdigest()

    @property
    def order_sha256(self):
        return p.digest(
            [
                (
                    pid,
                    i % 3,
                    (0, (1024 - self.B) // 2, 1024 - self.B)[i % 3],
                    SIDES[i % 2] + "_first",
                )
                for i, pid in enumerate(self.pair_ids)
            ]
        )

    def metadata(self):
        return dict(
            candidate=self.candidate,
            repetition=self.repetition,
            B=self.B,
            k=self.k,
            sha256=self.sha256,
            pair_order_sha256=self.order_sha256,
            count=20,
            wrapper=p.WRAPPER,
            case_class=self.case_class,
            natural_actual_rows=self.k,
            natural_model_shape_rows=self.natural_model_shape_rows,
            control_actual_rows=self.B,
            control_model_shape_rows=self.B,
            paired_integer_payload=[list(q) for q in self.pairs],
            pair_ids=list(self.pair_ids),
        )


def deep_size(value, seen=None):
    seen = set() if seen is None else seen
    if id(value) in seen:
        return 0
    seen.add(id(value))
    n = sys.getsizeof(value)
    if isinstance(value, dict):
        n += sum(deep_size(x, seen) for pair in value.items() for x in pair)
    elif isinstance(value, (tuple, list)):
        n += sum(deep_size(x, seen) for x in value)
    elif is_dataclass(value) and not isinstance(value, type):
        n += deep_size(value.__dict__, seen)
    return n


class Bundle:
    def __init__(
        self, root, manifest, *, audit_path=None, purpose="session_source_validation"
    ):
        self.audit = dict(
            task="0048",
            purpose=purpose,
            source_manifest=manifest,
            metadata_opens=0,
            source_bytes=0,
            jsonl_loads=0,
            jsonl_records=0,
            timed_records=0,
            warm_records=0,
            duration_copies=0,
            opens=[],
        )
        self.audit_path = audit_path
        self.data = {}
        self.manifest = manifest
        p.require(
            set(manifest) == set(p.SOURCE_MANIFEST) and len(manifest) == 24,
            "Exact24file allowlist",
        )
        paths = {n: p.safe(root, n) for n in manifest}
        p.require(
            sum(q.stat().st_size for q in paths.values())
            <= p.LIMITS["source_bundle_bytes"],
            "24MiB bundle",
        )
        for n, q in paths.items():
            pin = manifest[n]
            p.require(
                set(pin) == {"sha256", "bytes"}
                and type(pin["bytes"]) is int
                and q.stat().st_size == pin["bytes"],
                "Exact source size",
            )
            record = dict(path=n, requested_bytes=pin["bytes"], state="requested")
            self.audit["opens"].append(record)
            self.persist()
            b = q.read_bytes()
            self.audit["metadata_opens"] += 1
            self.audit["source_bytes"] += len(b)
            record.update(
                state="returned", bytes=len(b), sha256=hashlib.sha256(b).hexdigest()
            )
            self.persist()
            p.require(
                len(b) == pin["bytes"] and record["sha256"] == pin["sha256"],
                "Source byte pin",
            )
            self.data[n] = b

    def persist(self):
        if self.audit_path is not None:
            p.durable_json(self.audit_path, self.audit)

    def json(self, n):
        v = strict_json(self.data[n])
        finite_tree(v)
        return v

    def load(self):
        try:
            return self.validate()
        finally:
            self.persist()
            self.data.clear()

    def validate_selection(self, final, report, plan, config):
        reader = csv.DictReader(io.StringIO(self.data[SELECTION].decode(), newline=""))
        p.require(reader.fieldnames == SELECTION_FIELDS, "Closed selection header")
        rows = list(reader)
        p.require(
            len(rows) == 169 and list(rows[0]) == SELECTION_FIELDS,
            "Selection CSV schema/count",
        )
        selected = []
        references = []
        new = []
        selection = report["selection"]
        p.require(
            final["selection"] == selection
            and selection["task"] == "0047"
            and selection["status"] == "closed_selection_verified",
            "Closed current selection",
        )
        bundle_hash = p.digest(selection["source_manifest"])
        p.require(
            config["selection_manifest"] == selection["source_manifest"],
            "Selection metadata digest links",
        )
        for raw, (b, m) in zip(
            rows,
            (
                (nominal, actual)
                for nominal in p.ANCHORS
                for actual in range(1, nominal + 1)
            ),
            strict=True,
        ):
            p.require(
                set(raw) == set(SELECTION_FIELDS) and None not in raw.values(),
                "Selection emitted fields",
            )
            p.require(
                raw["B"] == str(b) and raw["m"] == str(m),
                "All legal ordered nominal occupancies",
            )
            expected = (
                p.point_class(b, m) if (b, m) in p.CASES else "residual_unmeasured"
            )
            p.require(
                raw["case_class"] == expected
                and raw["selected_for_campaign"] == str(int((b, m) in p.CASES))
                and raw["selection_bundle_sha256"] == bundle_hash,
                "Selection class/digest",
            )
            for key in (
                "observed_main_batches",
                "observed_main_events",
                "observed_main_assigned_ns",
                "zero_observed_frequency",
            ):
                p.require(raw[key].isdecimal(), "Selection integer spelling")
            p.require(
                int(raw["observed_main_events"])
                == m * int(raw["observed_main_batches"])
                and int(raw["zero_observed_frequency"])
                == int(raw["observed_main_batches"] == "0"),
                "Selection field conservation",
            )
            if expected == "remeasured_reference":
                p.require(raw["missing_rank"] == "", "Reference unranked")
                references.append([b, m])
            else:
                p.require(
                    raw["missing_rank"].isdecimal() and int(raw["missing_rank"]) >= 1,
                    "Missing rank",
                )
            if expected == "new_selected_point":
                new.append([b, m])
            if (b, m) in p.CASES:
                selected.append([b, m])
        p.require(
            references == selection["reference_cases"]
            and new == selection["selected_new_cases"]
            and len(references) == 15
            and len(new) == 17,
            "Selection measured32/residual137",
        )
        for nominal in p.ANCHORS:
            missing = [
                r
                for r in rows
                if int(r["B"]) == nominal and int(r["m"]) not in p.COARSE[nominal]
            ]
            ranked = sorted(
                missing, key=lambda r: (-int(r["observed_main_batches"]), int(r["m"]))
            )
            p.require(
                all(int(r["missing_rank"]) == i + 1 for i, r in enumerate(ranked)),
                "Selection rank/count tie serialization",
            )
        for label, chosen in (
            (
                "coverage_selected",
                [r for r in rows if r["case_class"] == "new_selected_point"],
            ),
            (
                "coverage_missing",
                [r for r in rows if r["case_class"] != "remeasured_reference"],
            ),
        ):
            expected = {
                key: sum(int(r[field]) for r in chosen)
                for key, field in (
                    ("batches", "observed_main_batches"),
                    ("events", "observed_main_events"),
                    ("busy_ns", "observed_main_assigned_ns"),
                )
            }
            p.require(
                selection[label] == expected, "Selection coverage within closed bundle"
            )
        for key in ("batches", "events", "busy_ns"):
            agree(
                selection["coverage_fraction"][key],
                selection["coverage_selected"][key]
                / selection["coverage_missing"][key],
            )
        self.audit.update(
            selection_rows=169,
            reference_points=15,
            new_points=17,
            residual_unmeasured_points=137,
        )

    def validate(self):
        d = p.SOURCE_DIRECTORY
        final = self.json(SUMMARY)
        report = self.json(d + "/reporting/summary.json")
        plan = self.json(d + "/plan.json")
        workflow = self.json(d + "/workflow.json")
        parent = self.json(d + "/parent-acceptance.json")
        attempt = self.json(ATTEMPT)
        config = self.json(CONFIG)
        ident = final["identity"]
        p.require(
            config["models"] == plan["models"],
            "Complete original model metadata entries, inert paths",
        )
        p.require(
            all(
                type(final["actual_counts"][k]) is int
                and final["actual_counts"][k] == 3 * n
                for k, n in WORKER_COUNTS.items()
            ),
            "Actual complete historical counts",
        )
        p.require(
            ident
            == dict(
                task="0047",
                validation_owner="0047",
                protocol_kind="one_conditional_targeted_paired_natural_raw_to_decision_CPU_session_v1",
                scope="selected_targeted_partial_raw_to_decisions",
                payload_scope="approved_background_training_1024prefix_32paired_cases_original_CPU_models",
                paired_contract_sha256=CONTRACT,
                packing=p.WRAPPER,
                config_sha256=self.manifest[CONFIG]["sha256"],
                prompt_sha256=self.manifest[PROMPT]["sha256"],
            ),
            "Original paired identity",
        )
        for value in (final, report, plan, workflow, parent):
            p.require(
                value["task"] == "0047" and value["identity"] == ident,
                "Source task/owner identity",
            )
        p.require(
            final["status"] == workflow["status"] == parent["status"] == SOURCE_STATUS
            and report["status"] == "aggregate_report_body_complete"
            and final["operational_allowance_consumed"] is True
            and workflow["synthetic_only"] is False
            and workflow["validation_bootstrap"] is False
            and plan["synthetic_only"] is False
            and plan["validation_bootstrap"] is False,
            "Accepted actual consumed campaign",
        )
        p.require(
            config["task"] == "0047"
            and plan["authorization_prompt_sha256"] == ident["prompt_sha256"]
            and parent["workflow_sha256"]
            == self.manifest[d + "/workflow.json"]["sha256"]
            and parent["plan_sha256"]
            == workflow["plan_sha256"]
            == attempt["plan_sha256"]
            == self.manifest[d + "/plan.json"]["sha256"]
            and attempt["task"] == "0047"
            and attempt["directory"] == d
            and attempt["prompt_sha256"] == ident["prompt_sha256"],
            "Parent/plan/attempt links",
        )
        p.require(
            workflow["overshoot_seconds"] == 0
            and workflow["sleep_assertion"]["released"] is True
            and workflow["sleep_assertion"]["owned_assertion_absent"] is True
            and workflow["sleep_assertion"]["lifecycle"]["reaped"] is True,
            "Source assertion lifecycle",
        )
        p.require(
            all(final[k] == report[k] for k in report if k not in ("status", "counts"))
            and final["counts"] == report["counts"] == plan["expected"],
            "Shared owned/final summary sections",
        )
        self.validate_selection(final, report, plan, config)
        p.require(
            (
                final["cells"],
                final["timed_calls"],
                final["timed_pairs"],
                final["warmup_calls"],
                final["gate_side_records"],
            )
            == (384, 7680, 3840, 1152, 2304)
            and all(
                type(final[n]) is int
                for n in (
                    "cells",
                    "timed_calls",
                    "timed_pairs",
                    "warmup_calls",
                    "gate_side_records",
                )
            )
            and final["exact_feature_score_decision_parity"] is True,
            "Complete original coverage/parity",
        )
        cells = parse_csv(self.data[CELLS], CELL_FIELDS)
        pairs = parse_csv(self.data[PAIRS], PAIR_FIELDS)
        p.require(len(cells) == 384 and len(pairs) == 3840, "Curated row coverage")
        vectors = {}
        all_cells = []
        all_pairs = []
        model_ids = None
        input_ids = None
        p.require(
            [w["phase"] for w in workflow["workers"]]
            == ["repetition1", "repetition2", "repetition3", "reporting"],
            "Source four workers",
        )
        for w in workflow["workers"]:
            phase = w["phase"]
            prefix = d + "/" + phase + "/"
            receipt = self.json(prefix + "receipt.json")
            dispatch = w["dispatch"]
            p.require(
                w["body_sha256"] == self.manifest[prefix + "receipt.json"]["sha256"]
                and receipt["task"] == "0047"
                and receipt["identity"] == ident
                and receipt["status"] == "body_complete_awaiting_exit"
                and receipt["source_map"]
                == workflow["source_map"]
                == plan["source_map"]
                and receipt["dependencies"]
                == workflow["dependencies"]
                == plan["dependencies"],
                "Source receipt identity/digest",
            )
            p.require(
                type(dispatch["returncode"]) is int
                and dispatch["returncode"] == 0
                and dispatch["child_reaped"] is True
                and dispatch["parent_confirms_normal_exit"] is True
                and dispatch["within_deadline"] is True
                and dispatch["overshoot_seconds"] == 0
                and dispatch["parent_error"] is None
                and dispatch["exit_observed_continuous"]
                <= dispatch["stage_deadline_continuous"]
                and w["acceptance"]["status"] == "parent_accepted_worker"
                and w["acceptance"]["task"] == "0047"
                and w["acceptance"]["normal_exit_reaped"] is True,
                "Source accepted normal exits",
            )
            p.require(
                receipt["resources"]["latched_error"] is None
                and receipt["resources"]["owned_thread_alive"] is False
                and 0 <= receipt["cleanup_seconds"] <= 2,
                "Source resources cleanup",
            )
            for name, sha in receipt["outputs"].items():
                if prefix + name in self.manifest:
                    p.require(
                        sha == self.manifest[prefix + name]["sha256"],
                        "Source owned output digest",
                    )
            expected_outputs = (
                {
                    "summary.json",
                    "cells.csv",
                    "pairs.csv",
                    "joint-cost.png",
                    "paired-cost.png",
                    "selection-coverage.png",
                    "selection.csv",
                }
                if phase == "reporting"
                else {"aggregate.json", "timings.jsonl", "timer.json"}
            )
            # Reporting figures/table copies are outside closed24; their digest strings are inert.
            p.require(
                set(receipt["outputs"]) == expected_outputs, "Source output contract"
            )
            if phase == "reporting":
                p.require(
                    receipt["outputs"]["summary.json"]
                    == self.manifest[d + "/reporting/summary.json"]["sha256"]
                    and receipt["outputs"]["cells.csv"]
                    == self.manifest[CELLS]["sha256"]
                    and receipt["outputs"]["selection.csv"]
                    == self.manifest[SELECTION]["sha256"]
                    and receipt["outputs"]["pairs.csv"]
                    == self.manifest[PAIRS]["sha256"],
                    "Owned report/table digests",
                )
                continue
            rep = int(phase[-1])
            aggregate = self.json(prefix + "aggregate.json")
            timer = self.json(prefix + "timer.json")
            p.require(
                aggregate["task"] == "0047"
                and aggregate["identity"] == ident
                and aggregate["exact_feature_score_decision_parity"] is True
                and aggregate["unique_raw_rows"] == 384
                and aggregate["raw_window_buffers_retained"] == 0,
                "Source aggregate parity/shape",
            )
            p.require(
                aggregate["input_integrity"] == INPUT_INTEGRITY
                and aggregate["registered_model_threshold_hashes"] == MODEL_INTEGRITY,
                "Original numerical identity strings",
            )
            p.require(
                all(
                    type(aggregate["accounting"][k]) is int
                    and aggregate["accounting"][k] == n
                    for k, n in WORKER_COUNTS.items()
                )
                and aggregate["accounting"]["HDF_closed"] is True
                and all(
                    aggregate["accounting"][k] is None
                    for k in ("inflight", "model_inflight")
                )
                and all(
                    aggregate["accounting"][k] is False
                    for k in ("membership_inflight", "golden_inflight", "HDF_inflight")
                ),
                "Complete consumed physical source ledger without inflight",
            )
            if model_ids is None:
                model_ids = aggregate["registered_model_threshold_hashes"]
                input_ids = aggregate["input_integrity"]
            p.require(
                model_ids
                == aggregate["registered_model_threshold_hashes"]
                == receipt["model_parameter_threshold_hashes"]
                and input_ids == aggregate["input_integrity"],
                "Original input/model agreement",
            )
            p.require(
                timer["storage"] == "integer_ns"
                and timer["recorded_before_timing"] is True
                and timer["monotonic"] is True
                and timer["adjustable"] is False
                and 0 < timer["resolution_seconds"] < 1,
                "Original timer",
            )
            parsed_bytes = deep_size(
                (
                    self.data,
                    final,
                    report,
                    plan,
                    workflow,
                    parent,
                    config,
                    cells,
                    pairs,
                    aggregate,
                )
            )
            self.audit["parsed_python_bytes_peak"] = max(
                self.audit.get("parsed_python_bytes_peak", 0), parsed_bytes
            )
            p.require(
                parsed_bytes + 24 * 2**20 <= p.LIMITS["parsed_source_python_bytes"],
                "Parsed source plus chronology/workspace envelope",
            )
            lines = self.data[prefix + "timings.jsonl"].splitlines()
            self.audit["jsonl_loads"] += 1
            records = []
            for line in lines:
                r = strict_json(line)
                finite_tree(r)
                records.append(r)
                self.audit["jsonl_records"] += 1
                self.audit[
                    "timed_records" if r.get("phase") == "timed" else "warm_records"
                ] += 1
            p.require(len(records) == 2944, "Chronology2944")
            expected = list(schedule(rep))
            p.require(len(expected) == len(records), "Schedule count")
            for ordinal, (r, e) in enumerate(zip(records, expected, strict=True)):
                p.require(
                    set(r)
                    == set(e)
                    | {
                        "ordinal",
                        "elapsed_ns",
                        "start_continuous",
                        "end_continuous",
                        "continuous_minus_timer_ns",
                    }
                    and all(type(r[k]) is type(v) and r[k] == v for k, v in e.items())
                    and type(r["ordinal"]) is int
                    and r["ordinal"] == ordinal,
                    "Exact chronological side identity",
                )
                integer(r["elapsed_ns"], "source duration", minimum=1)
                p.require(
                    ordinal == 0
                    or r["start_continuous"] >= records[ordinal - 1]["end_continuous"],
                    "Chronology continuous order",
                )
                p.require(
                    type(r["start_continuous"]) is float
                    and type(r["end_continuous"]) is float
                    and r["end_continuous"] >= r["start_continuous"],
                    "Continuous timestamps",
                )
            p.require(
                len(aggregate["chronology"]) == 2944
                and all(
                    p.digest(x) == p.digest({k: r[k] for k in x})
                    for x, r in zip(aggregate["chronology"], records, strict=True)
                ),
                "Aggregate chronological copies",
            )
            timed = {
                (r["candidate"], r["B"], r["m"], r["pair"], r["side"]): r
                for r in records
                if r["phase"] == "timed"
            }
            p.require(len(timed) == 2560, "Unique timed source records")
            for c in p.CANDIDATES:
                for b, k in p.CASES:
                    group = []
                    for i in range(20):
                        nr = timed[c, b, k, i, SIDES[0]]
                        cr = timed[c, b, k, i, SIDES[1]]
                        pair = {n: nr[n] for n in PAIR_FIELDS[:11]}
                        pair.update(
                            natural_actual_rows=k,
                            control_actual_rows=b,
                            natural_model_shape_rows=nr["model_shape_rows"],
                            control_model_shape_rows=b,
                            natural_ns=nr["elapsed_ns"],
                            control_ns=cr["elapsed_ns"],
                            difference_ns=nr["elapsed_ns"] - cr["elapsed_ns"],
                            ratio=nr["elapsed_ns"] / cr["elapsed_ns"],
                        )
                        group.append(pair)
                    ac = [
                        x
                        for x in aggregate["pairs"]
                        if (x["candidate"], x["B"], x["m"]) == (c, b, k)
                    ]
                    pc = [
                        x
                        for x in pairs
                        if (x["candidate"], x["repetition"], x["B"], x["m"])
                        == (c, rep, b, k)
                    ]
                    p.require(
                        ac == pc == group
                        and all(
                            type(x[n]) is type(y[n])
                            for x, y in zip(ac, group, strict=True)
                            for n in PAIR_FIELDS
                        ),
                        "All ordered paired duration copies",
                    )
                    vectors[c, rep, b, k] = PairedVector(
                        c,
                        rep,
                        b,
                        k,
                        tuple((x["natural_ns"], x["control_ns"]) for x in group),
                        tuple(x["pair_id"] for x in group),
                        service_shape(b, k, SIDES[0])[1],
                        p.point_class(b, k),
                    )
                    all_pairs += group
                    for side in SIDES:
                        q = [
                            x["natural_ns" if side == SIDES[0] else "control_ns"]
                            for x in group
                        ]
                        selected = [
                            x
                            for x in aggregate["cells"]
                            if (x["candidate"], x["B"], x["m"], x["side"])
                            == (c, b, k, side)
                        ]
                        curated = [
                            x
                            for x in cells
                            if (
                                x["candidate"],
                                x["repetition"],
                                x["B"],
                                x["m"],
                                x["side"],
                            )
                            == (c, rep, b, k, side)
                        ]
                        p.require(
                            len(selected) == len(curated) == 1, "Unique side cells"
                        )
                        cell = selected[0]
                        cc = curated[0]
                        p.require(
                            p.digest(cell["observations_ns"]) == p.digest(q)
                            and cell["window_call_counts"] == [7, 7, 6]
                            and cc["window_call_counts"] == "7/7/6"
                            and cell["timer"] == timer,
                            "Cell raw observation/order",
                        )
                        shape = service_shape(b, k, side)
                        p.require(
                            (cell["actual_rows"], cell["model_shape_rows"]) == shape
                            and cell["scope"] == ident["scope"]
                            and cell["strategy"] == "natural"
                            and cell["wrapper"] == p.WRAPPER
                            and cell["case_class"] == p.point_class(b, k),
                            "Natural source packing",
                        )
                        check_stats(cell, q)
                        check_stats(cc, q)
                        for name in (
                            "candidate",
                            "repetition",
                            "B",
                            "m",
                            "side",
                            "actual_rows",
                            "model_shape_rows",
                            "wrapper",
                            "case_class",
                            "scope",
                            "strategy",
                        ):
                            p.require(
                                type(cell[name]) is type(cc[name])
                                and cell[name] == cc[name],
                                "Curated cell identity",
                            )
                        for name, expected_value in dict(
                            mean_actual_event_ns=sum(q) / 20 / shape[0],
                            hypothetical_bill_per_m_ns=sum(q) / 20 / k,
                            actual_events_per_second=1e9 / (sum(q) / 20 / shape[0]),
                        ).items():
                            agree(cell[name], expected_value)
                            agree(cc[name], expected_value)
                        all_cells.append(cell)
            p.require(
                len(aggregate["cells"]) == 128
                and len(aggregate["pairs"]) == 1280
                and len(aggregate["gates"]) == 768,
                "Per-worker copies/gates",
            )
            live = deep_size(
                (
                    self.data,
                    final,
                    report,
                    plan,
                    workflow,
                    parent,
                    config,
                    cells,
                    pairs,
                    aggregate,
                    records,
                    expected,
                    timed,
                    all_cells,
                    all_pairs,
                    vectors,
                )
            )
            self.audit["parsed_python_bytes_peak"] = max(
                self.audit.get("parsed_python_bytes_peak", 0), live
            )
            p.require(
                live + 8 * 2**20 <= p.LIMITS["parsed_source_python_bytes"],
                "Live parsed containers plus8MiB temporary margin",
            )
            gates = aggregate["gates"]
            contexts = {}
            for g in gates:
                p.require(
                    all(
                        type(g[n]) is int
                        for n in (
                            "B",
                            "m",
                            "window_index",
                            "window_position",
                            "actual_rows",
                            "model_shape_rows",
                            "repetition",
                        )
                    ),
                    "Exact gate integer fields",
                )
                p.require(
                    g["repetition"] == rep
                    and g["candidate"] in p.CANDIDATES
                    and g["phase"] in ("pre", "post")
                    and g["status"] == "exact_feature_score_decision_bytes_passed"
                    and g["feature_score_decision_mismatches"] == [0, 0, 0]
                    and all(
                        type(x) is int for x in g["feature_score_decision_mismatches"]
                    ),
                    "Exact gate evidence",
                )
                b, k, side = g["B"], g["m"], g["side"]
                p.require(
                    (g["actual_rows"], g["model_shape_rows"])
                    == service_shape(b, k, side)
                    and g["wrapper"] == p.WRAPPER
                    and g["case_class"] == p.point_class(b, k)
                    and g["window_index"] in (0, 1, 2)
                    and g["window_position"]
                    == (0, (1024 - b) // 2, 1024 - b)[g["window_index"]],
                    "Gate context",
                )
                key = (g["candidate"], b, k, side, g["window_index"])
                p.require((key, g["phase"]) not in contexts, "Unique gates")
                contexts[key, g["phase"]] = g["reference_identity"]
            p.require(
                len(contexts) == 768
                and all(
                    contexts[key, "pre"] == contexts[key, "post"]
                    for key, phase in contexts
                    if phase == "pre"
                ),
                "Same-shaped pre/post references",
            )
        p.require(
            len(vectors) == 192 and len(all_cells) == 384 and len(all_pairs) == 3840,
            "Complete source matrix",
        )
        p.require(
            len({(r["candidate"], r["B"], r["m"], r["side"]) for r in report["pooled"]})
            == 128
            and len(
                {
                    (r["candidate"], r["repetition"], r["B"], r["m"])
                    for r in report["paired_groups"]
                }
            )
            == 192,
            "Unique pooled/paired summary keys",
        )
        for row in report["pooled"]:
            q = [
                v
                for cell in all_cells
                if (cell["candidate"], cell["B"], cell["m"], cell["side"])
                == (row["candidate"], row["B"], row["m"], row["side"])
                for v in cell["observations_ns"]
            ]
            transformed = {
                (
                    "minimum_ns"
                    if n == "minimum"
                    else "maximum_ns"
                    if n == "maximum"
                    else n + "_ns"
                    if n not in ("count",)
                    else n
                ): v
                for n, v in row.items()
                if n
                in (
                    "count",
                    "minimum",
                    "maximum",
                    "mean",
                    "population_std",
                    "p50",
                    "p95",
                    "p99",
                )
            }
            check_stats(transformed, q)
        p.require(
            len(report["pooled"]) == 128 and len(report["paired_groups"]) == 192,
            "Shared summary groups",
        )
        for row in report["paired_groups"]:
            q = vectors[row["candidate"], row["repetition"], row["B"], row["m"]].pairs
            for name, values in (
                ("difference_ns", [a - b for a, b in q]),
                ("ratio", [a / b for a, b in q]),
            ):
                expected = stats(values)
                actual = row[name]
                for n, v in expected.items():
                    source_name = n.replace("_ns", "")
                    agree(actual[source_name], v)
            p.require(
                row["natural_first_pairs"] == row["control_first_pairs"] == 10,
                "Balanced pair ordering",
            )
        self.audit.update(
            duration_copies=30720,
            warm_duration_copies=1152,
            duration_copy_locations=dict(
                aggregate_chronology_timed=7680,
                aggregate_chronology_warm=1152,
                aggregate_cell_observations=7680,
                aggregate_pairs=7680,
                curated_pairs=7680,
            ),
            paired_vectors=192,
            unique_original_timed_observations=7680,
            retained_vector_python_bytes=deep_size(vectors),
            source_identity=ident,
            source_acceptance_sha256=self.manifest[d + "/parent-acceptance.json"][
                "sha256"
            ],
        )
        p.require(
            self.audit["retained_vector_python_bytes"] <= 2 * 2**20,
            "2MiB retained paired lookup",
        )
        self.audit["unfavorable_pairs"] = sum(
            a > b for v in vectors.values() for a, b in v.pairs
        )
        self.audit["full_occupancy_unfavorable_pairs"] = sum(
            a > b for v in vectors.values() if v.B == v.k for a, b in v.pairs
        )
        self.audit["new_point_unfavorable_pairs"] = sum(
            a > b
            for v in vectors.values()
            if v.case_class == "new_selected_point"
            for a, b in v.pairs
        )
        self.data.clear()
        return vectors, self.audit


def custody(root, manifest, *, audit_path, purpose):
    """Parent byte-only bounded custody; no chronology/aggregate parsing or copies."""
    p.require(
        set(manifest) == set(p.SOURCE_MANIFEST) and len(manifest) == 24,
        "Closed custody allowlist",
    )
    audit = dict(
        task="0048",
        purpose=purpose,
        metadata_opens=0,
        source_bytes=0,
        parsed_loads=0,
        jsonl_loads=0,
        jsonl_records=0,
        opens=[],
    )
    p.require(
        sum(v["bytes"] for v in manifest.values()) <= 24 * 2**20, "24MiB byte custody"
    )
    for name, pin in manifest.items():
        path = p.safe(root, name)
        p.require(path.stat().st_size == pin["bytes"], "Custody size")
        record = dict(path=name, requested_bytes=pin["bytes"], state="requested")
        audit["opens"].append(record)
        p.durable_json(audit_path, audit)
        h = hashlib.sha256()
        size = 0
        with path.open("rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                size += len(block)
                p.require(size <= pin["bytes"], "Custody growth")
                h.update(block)
        record.update(state="returned", bytes=size, sha256=h.hexdigest())
        audit["metadata_opens"] += 1
        audit["source_bytes"] += size
        p.durable_json(audit_path, audit)
        p.require(
            size == pin["bytes"] and h.hexdigest() == pin["sha256"],
            "Custody pinned bytes",
        )
    return audit
