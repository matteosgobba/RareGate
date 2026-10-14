"""Closed10-file Task0046 metadata selection; stdlib only, no engine execution."""

import csv
import hashlib
import io
import math

from latenttrigger.benchmarks import targeted_raw_planning as grid
from latenttrigger.simulation.occupancy_protocol import digest, matrix, require, safe
from latenttrigger.simulation.occupancy_source import deep_size, strict_json

DIRECTORY = "results/simulations/task0046-occupancy-service-replay/78a96792b4b04f809e0e0c7717a7b02d"
CONFIG = "configs/simulation/occupancy_service_replay_v1.json"
PROMPT = "docs/prompts/0046-occupancy-aware-service-replay.md"
SUMMARY = "results/tables/final/task0046-occupancy-service-replay-summary.json"
SCENARIOS = SUMMARY.replace("summary.json", "scenarios.csv")
OCCUPANCIES = SUMMARY.replace("summary.json", "occupancies.csv")
NAMES = (
    CONFIG,
    PROMPT,
    SUMMARY,
    SCENARIOS,
    OCCUPANCIES,
    *(
        DIRECTORY + "/" + n
        for n in (
            "plan.json",
            "workflow.json",
            "parent-acceptance.json",
            "simulation/receipt.json",
            "reporting/receipt.json",
        )
    ),
)
KEYS = "mode rate seed candidate B timeout_ns repetition mapping billing".split()
STRINGS = {"mode", "candidate", "mapping", "billing", "trace_sha256"}
INTEGER_FIELDS = set(KEYS) - STRINGS | set(
    "generated admitted overflow_dropped completed pending batches full_batches partial_batches busy_ns exact_batches exact_events exact_busy_ns mapped_batches mapped_events mapped_busy_ns modeled_row_work anchor_minus_actual_rows modeled_minus_actual_rows m k events exact_point source_natural_actual_rows source_natural_service_B source_control_actual_rows source_control_service_B modeled_rows k_minus_m".split()
)


def parse_row(row):
    require(None not in row and None not in row.values(), "Closed CSV row")
    result = {}
    for k, v in row.items():
        if k in STRINGS:
            result[k] = v
        elif k in INTEGER_FIELDS:
            require(
                v and (v.isdecimal() or v[0] == "-" and v[1:].isdecimal()),
                "Exact integer metadata",
            )
            result[k] = int(v)
        elif v == "":
            result[k] = None
        else:
            result[k] = float(v)
            require(math.isfinite(result[k]), "Finite CSV value")
    return result


def lookup(b, m, mapping):
    anchors = {
        1: (1,),
        8: (1, 2, 7, 8),
        32: (1, 2, 8, 31, 32),
        128: (1, 2, 32, 127, 128),
    }
    require(
        type(m) is int
        and 1 <= m <= b
        and mapping in ("next_anchor", "previous_anchor"),
        "Source occupancy/mapping",
    )
    return (
        min(k for k in anchors[b] if k >= m)
        if mapping == "next_anchor"
        else max(k for k in anchors[b] if k <= m)
    )


class Bundle:
    def __init__(
        self,
        root,
        manifest,
        *,
        audit_path=None,
        purpose="physical_prerequisite_selection",
    ):
        self.manifest = manifest
        self.audit_path = audit_path
        self.data = {}
        self.audit = dict(
            task="0047",
            purpose=purpose,
            metadata_opens=0,
            source_bytes=0,
            scenario_rows=0,
            occupancy_rows=0,
            opens=[],
        )
        require(set(manifest) == set(NAMES), "Exact10selection paths")
        paths = {n: safe(root, n) for n in manifest}
        require(
            sum(q.stat().st_size for q in paths.values()) <= 8 * 2**20, "Selection8MiB"
        )
        for n, q in paths.items():
            pin = manifest[n]
            require(
                set(pin) == {"sha256", "bytes"}
                and type(pin["bytes"]) is int
                and q.stat().st_size == pin["bytes"],
                "Exact size",
            )
            entry = dict(path=n, state="requested", requested_bytes=pin["bytes"])
            self.audit["opens"].append(entry)
            self.persist()
            with q.open("rb") as f:
                b = f.read(pin["bytes"] + 1)
            self.audit["metadata_opens"] += 1
            self.audit["source_bytes"] += len(b)
            entry.update(
                state="returned", bytes=len(b), sha256=hashlib.sha256(b).hexdigest()
            )
            self.persist()
            require(
                len(b) == pin["bytes"] and entry["sha256"] == pin["sha256"],
                "Selection bytes changed",
            )
            self.data[n] = b

    def persist(self):
        if self.audit_path:
            from latenttrigger.simulation.protocol import durable_json

            durable_json(self.audit_path, self.audit)

    def value(self, n):
        return strict_json(self.data[n])

    def csv(self, n):
        reader = csv.DictReader(io.StringIO(self.data[n].decode(), newline=""))
        fields = reader.fieldnames
        require(fields and len(fields) == len(set(fields)), "Unique CSV columns")
        for row in reader:
            yield parse_row(row)

    def load(self):
        try:
            return self.validate()
        finally:
            self.persist()

    def validate(self):
        d = DIRECTORY
        summary = self.value(SUMMARY)
        plan = self.value(d + "/plan.json")
        w = self.value(d + "/workflow.json")
        parent = self.value(d + "/parent-acceptance.json")
        config = self.value(CONFIG)
        identity = summary["identity"]
        require(
            identity == plan["identity"] == w["identity"] == parent["identity"]
            and identity["task"] == identity["validation_owner"] == "0046"
            and identity["scope"] == "closed_Task0045_timing_metadata_synthetic_FIFO"
            and identity["assignment_contract_sha256"]
            == "84f71df37c4b48801ce49f3c113b306c5bc90a0017e1b1e58da4f051071eb83d"
            and identity["config_sha256"] == self.manifest[CONFIG]["sha256"]
            and identity["prompt_sha256"] == self.manifest[PROMPT]["sha256"]
            and config["task"] == config["validation_owner"] == "0046",
            "Accepted original0046identity",
        )
        status = "parent_accepted_synthetic_occupancy_service_replay"
        require(
            summary["status"] == w["status"] == parent["status"] == status
            and summary["operational_allowance_consumed"] is True
            and w["fixture_only"] is False
            and plan["fixture_only"] is False
            and plan["validation_bootstrap"] is False,
            "Consumed actual replay source",
        )
        require(
            parent["workflow_sha256"]
            == summary["workflow_sha256"]
            == self.manifest[d + "/workflow.json"]["sha256"]
            and parent["plan_sha256"]
            == summary["execution_plan_sha256"]
            == w["plan_sha256"]
            == self.manifest[d + "/plan.json"]["sha256"],
            "Source parent/workflow/plan links",
        )
        require(
            w["overshoot_seconds"] == 0
            and w["sleep_assertion"]["released"] is True
            and w["sleep_assertion"]["owned_assertion_absent"] is True
            and w["sleep_assertion"]["lifecycle"]["reaped"] is True,
            "Accepted source cleanup",
        )
        require(
            [q["phase"] for q in w["phases"]] == ["simulation", "reporting"],
            "Source two phases",
        )
        for phase in w["phases"]:
            name = phase["phase"]
            receipt = self.value(d + "/" + name + "/receipt.json")
            dispatch = phase["dispatch"]
            require(
                phase["body_sha256"]
                == self.manifest[d + "/" + name + "/receipt.json"]["sha256"]
                and receipt["identity"] == identity
                and receipt["source_map"] == plan["source_map"] == w["source_map"]
                and receipt["dependencies"] == plan["dependencies"] == w["dependencies"]
                and receipt["status"] == "body_complete_awaiting_exit"
                and receipt["phase"] == name,
                "Source accepted body linkage",
            )
            require(
                type(dispatch["returncode"]) is int
                and dispatch["returncode"] == 0
                and dispatch["child_reaped"] is True
                and dispatch["parent_confirms_normal_exit"] is True
                and dispatch["within_deadline"] is True
                and dispatch["parent_error"] is None
                and dispatch["overshoot_seconds"] == 0,
                "Normal source exits/reaping",
            )
            if name == "simulation":
                require(
                    receipt["outputs"]["scenarios.csv"]
                    == self.manifest[SCENARIOS]["sha256"]
                    and receipt["outputs"]["occupancies.csv"]
                    == self.manifest[OCCUPANCIES]["sha256"],
                    "Owned CSV digests",
                )
        scenarios = {}
        totals = {}
        expected = list(matrix())
        for index, r in enumerate(self.csv(SCENARIOS)):
            self.audit["scenario_rows"] += 1
            key = tuple(r[k] for k in KEYS)
            require(
                index < len(expected)
                and key == expected[index]
                and key not in scenarios
                and r["generated"] == 5000
                and r["admitted"] == r["completed"]
                and r["generated"] == r["completed"] + r["overflow_dropped"]
                and r["pending"] == 0
                and r["batches"] == r["full_batches"] + r["partial_batches"]
                and r["exact_events"] + r["mapped_events"] == r["completed"]
                and r["exact_batches"] + r["mapped_batches"] == r["batches"]
                and r["exact_busy_ns"] + r["mapped_busy_ns"] == r["busy_ns"],
                "All ordered source scenarios/conservation",
            )
            scenarios[key] = r
            totals[key] = {
                n: 0
                for n in (
                    "batches",
                    "events",
                    "busy_ns",
                    "modeled_rows",
                    "exact_batches",
                    "exact_events",
                    "exact_busy_ns",
                    "mapped_batches",
                    "mapped_events",
                    "mapped_busy_ns",
                )
            }
        require(len(scenarios) == 3024, "Exact scenario matrix")
        missing = {
            (b, m): dict(batches=0, events=0, busy_ns=0)
            for b in (1, 8, 32, 128)
            for m in range(1, b + 1)
        }
        current = None
        group = -1
        last_m = 0
        for r in self.csv(OCCUPANCIES):
            self.audit["occupancy_rows"] += 1
            key = tuple(r[k] for k in KEYS)
            if key != current:
                group += 1
                require(
                    group < len(expected) and key == expected[group],
                    "Ordered occupancy scenario groups",
                )
                current = key
                last_m = 0
            b, m, k = r["B"], r["m"], r["k"]
            require(
                last_m < m <= b and k == lookup(b, m, r["mapping"]),
                "Unique scenario/m and anchor",
            )
            last_m = m
            natural_sb = k if (b, k) in ((32, 8), (128, 32)) else b
            require(
                r["batches"] > 0
                and r["events"] == m * r["batches"]
                and r["busy_ns"] > 0
                and r["exact_point"] == int(k == m)
                and r["source_natural_actual_rows"] == k
                and r["source_natural_service_B"] == natural_sb
                and r["source_control_actual_rows"]
                == r["source_control_service_B"]
                == b
                and r["modeled_rows"]
                == r["batches"] * (k if r["billing"] == "natural_anchor" else b)
                and r["k_minus_m"] == k - m
                and r["anchor_minus_actual_rows"] == (k - m) * r["batches"]
                and r["modeled_minus_actual_rows"] == r["modeled_rows"] - r["events"],
                "Occupancy source shape/count/rowwork",
            )
            t = totals[key]
            for n in ("batches", "events", "busy_ns", "modeled_rows"):
                t[n] += r[n]
            for n in ("batches", "events", "busy_ns"):
                t[("exact_" if k == m else "mapped_") + n] += r[n]
            if r["mapping"] == "next_anchor" and r["billing"] == "natural_anchor":
                for n in ("batches", "events", "busy_ns"):
                    missing[b, m][n] += r[n]
        require(
            group + 1 == 3024
            and self.audit["occupancy_rows"]
            == summary["audit_row_counts"]["occupancies"]
            and self.audit["occupancy_rows"] <= 145584,
            "Complete occupancy coverage",
        )
        for key, t in totals.items():
            r = scenarios[key]
            require(
                t["events"] == r["completed"]
                and t["modeled_rows"] == r["modeled_row_work"]
                and all(t[n] == r[n] for n in t if n not in ("events", "modeled_rows")),
                "Every occupancy reconciles to unique scenario",
            )
        for mapping in ("next_anchor", "previous_anchor"):
            for billing in ("natural_anchor", "full_control"):
                table = summary["totals"][mapping + "/" + billing]
                require(
                    all(
                        sum(
                            r[n]
                            for key, r in scenarios.items()
                            if key[-2:] == (mapping, billing)
                        )
                        == table[n]
                        for n in (
                            "generated",
                            "completed",
                            "overflow_dropped",
                            "batches",
                            "busy_ns",
                            "mapped_batches",
                            "mapped_events",
                            "mapped_busy_ns",
                            "modeled_row_work",
                            "anchor_minus_actual_rows",
                            "modeled_minus_actual_rows",
                        )
                    ),
                    "Summary aggregate totals",
                )
        table = []
        selected = set()
        coverage = {n: 0 for n in ("batches", "events", "busy_ns")}
        denominator = dict(coverage)
        for b in (1, 8, 32, 128):
            ranked = sorted(
                (m for m in range(1, b + 1) if (b, m) not in grid.REFERENCE_CASES),
                key=lambda m: (-missing[b, m]["batches"], m),
            )
            chosen = set(ranked[: {1: 0, 8: 4, 32: 5, 128: 8}[b]])
            for m in range(1, b + 1):
                ref = (b, m) in grid.REFERENCE_CASES
                new = m in chosen
                row = missing[b, m]
                selected.update([(b, m)] if new else [])
                table.append(
                    dict(
                        B=b,
                        m=m,
                        case_class="remeasured_reference"
                        if ref
                        else "new_selected_point"
                        if new
                        else "residual_unmeasured",
                        missing_rank=None if ref else ranked.index(m) + 1,
                        selected_for_campaign=int(ref or new),
                        observed_main_batches=row["batches"],
                        observed_main_events=row["events"],
                        observed_main_assigned_ns=row["busy_ns"],
                        zero_observed_frequency=int(row["batches"] == 0),
                        selection_bundle_sha256=digest(self.manifest),
                    )
                )
                if not ref:
                    for n in denominator:
                        denominator[n] += row[n]
                        coverage[n] += row[n] * int(new)
        require(
            selected == set(grid.CASES) - set(grid.REFERENCE_CASES)
            and len(table) == 169,
            "Prescribed exploratory17selection plus15references",
        )
        self.audit.update(
            parsed_python_container_bytes=deep_size(
                (scenarios, totals, missing, summary, table)
            ),
            selected_new_points=len(selected),
            residual_unmeasured_points=137,
        )
        require(
            self.audit["parsed_python_container_bytes"] <= 48 * 2**20,
            "Selection parsed48MiB envelope separate from array cap",
        )
        result = dict(
            task="0047",
            status="closed_selection_verified",
            source_manifest=self.manifest,
            source_identity=identity,
            selected_new_cases=[list(q) for q in sorted(selected)],
            reference_cases=[list(q) for q in grid.REFERENCE_CASES],
            coverage_selected=coverage,
            coverage_missing=denominator,
            coverage_fraction={
                k: coverage[k] / denominator[k] if denominator[k] else None
                for k in denominator
            },
            selection_rows=table,
            source_occupancy_rows=self.audit["occupancy_rows"],
            source_scenario_rows=3024,
            interpretation="Exploratory ranking of old next/natural synthetic replay missing occupancy counts; busy coverage is hypothetical assigned cost; no production or independent confirmation",
        )
        self.data.clear()
        return result, self.audit
