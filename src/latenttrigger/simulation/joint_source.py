"""Stdlib-only accepted Task0043 loader. Embedded event/model paths are inert."""

import csv
import hashlib
import io
import json
import math
import struct
import sys

from latenttrigger.benchmarks.development_decision_planning import candidates, schedule
from latenttrigger.simulation import joint_protocol as p
from latenttrigger.simulation.engine import describe, integer

SUMMARY = "results/tables/final/task0043-development-raw-decision-summary.json"
CELLS = "results/tables/final/task0043-development-raw-decision-cells.csv"
SOURCE_STATUS = "parent_accepted_development_raw_decision_measurement"
STATS = (
    "count",
    "minimum_ns",
    "maximum_ns",
    "mean_ns",
    "population_std_ns",
    "p50_ns",
    "p95_ns",
    "p99_ns",
)


def unique_pairs(items):
    value = {}
    for k, v in items:
        p.require(k not in value, "Ambiguous duplicate JSON key")
        value[k] = v
    return value


def statistics(q):
    d = describe(q)
    mean = sum(q) / len(q)
    return dict(
        count=len(q),
        minimum_ns=min(q),
        maximum_ns=max(q),
        mean_ns=mean,
        population_std_ns=math.sqrt(sum((x - mean) ** 2 for x in q) / len(q)),
        p50_ns=d["p50"],
        p95_ns=d["p95"],
        p99_ns=d["p99"],
    )


def compare_stats(q, cell):
    for k, v in statistics(q).items():
        actual = cell[k]
        if k in ("count", "minimum_ns", "maximum_ns"):
            p.require(
                type(actual) is int and actual == v, "Exact duration/count statistic"
            )
        else:
            p.require(
                type(actual) in (int, float)
                and math.isfinite(actual)
                and abs(actual - v)
                <= 32 * max(math.ulp(float(actual)), math.ulp(float(v))),
                "Mechanical binary64 statistic serialization: " + k,
            )


class Bundle:
    """A complete closed manifest, read once; byte custody and numerical accounting."""

    def __init__(self, root=p.ROOT, pins=None, directory=p.SOURCE_DIRECTORY):
        self.root = root
        self.pins = p.PINS if pins is None else pins
        self.directory = directory
        expected = {
            SUMMARY,
            CELLS,
            "configs/benchmarks/development_raw_decision_v2.json",
            "docs/prompts/0043-development-raw-decision-campaign-v2.md",
            *(
                directory + "/" + n
                for n in ("plan.json", "workflow.json", "parent-acceptance.json")
            ),
            *(
                f"{directory}/repetition{r}/{n}"
                for r in (1, 2, 3)
                for n in (
                    "receipt.json",
                    "aggregate.json",
                    "timer.json",
                    "timings.jsonl",
                )
            ),
        }
        p.require(
            set(self.pins) == expected, "Complete19file manifest; no foreign paths"
        )
        self.data = {}
        self.audit = dict(
            metadata_reads=[],
            source_bytes=0,
            jsonl_loads=0,
            jsonl_records_parsed=0,
            timed_records_selected=0,
            warmup_records_excluded=0,
            aggregate_observation_copies_parsed=0,
            aggregate_chronology_duration_copies_parsed=0,
            aggregate_cell_statistic_copies_parsed=0,
            curated_cell_statistic_copies_parsed=0,
            curated_pooled_statistic_copies_parsed=0,
        )
        total = sum(p.safe(root, n).stat().st_size for n in self.pins)
        p.require(
            total <= p.LIMITS["source_bundle_bytes"],
            "8MiB complete source bound before reads",
        )
        for n, sha in self.pins.items():
            path = p.safe(root, n)
            with path.open("rb") as f:
                data = f.read(p.LIMITS["source_bundle_bytes"] + 1)
            p.require(
                len(data) <= p.LIMITS["source_bundle_bytes"]
                and hashlib.sha256(data).hexdigest() == sha,
                "Pinned source bytes: " + n,
            )
            self.data[n] = data
            self.audit["metadata_reads"].append(
                dict(path=n, bytes=len(data), sha256=sha)
            )
            self.audit["source_bytes"] += len(data)
        p.require(self.audit["source_bytes"] == total, "Stable source sizes")

    def json(self, name):
        def pairs(items):
            d = {}
            for k, v in items:
                p.require(k not in d, "Duplicate JSON key")
                d[k] = v
            return d

        return json.loads(
            self.data[name],
            object_pairs_hook=pairs,
            parse_constant=lambda s: (_ for _ in ()).throw(
                ValueError("Nonfinite JSON")
            ),
        )

    def load(self, *, check_historical_sources=True):
        d = self.directory
        summary = self.json(SUMMARY)
        config = self.json("configs/benchmarks/development_raw_decision_v2.json")
        provenance = summary["provenance"]
        p.require(
            summary["task"] == "0043"
            and summary["status"] == SOURCE_STATUS
            and summary["scope"]
            == "selected_raw_to_decisions_CPU_natural_fixed_development_windows"
            and summary["one_allowance_consumed"] is True,
            "Accepted consumed Task0043 scope",
        )
        for n, k in [
            ("workflow.json", "workflow_sha256"),
            ("parent-acceptance.json", "parent_acceptance_sha256"),
            ("plan.json", "execution_plan_sha256"),
        ]:
            p.require(
                provenance[k] == self.pins[d + "/" + n], "Curated provenance link"
            )
        for n, k in [
            (
                "configs/benchmarks/development_raw_decision_v2.json",
                "config_file_sha256",
            ),
            (
                "docs/prompts/0043-development-raw-decision-campaign-v2.md",
                "prompt_sha256",
            ),
        ]:
            p.require(provenance[k] == self.pins[n], "Original config/prompt pin")
        p.require(
            provenance["operational_directory"] == d
            and provenance["config_canonical_sha256"] == p.digest(config)
            and config["task"] == "0043"
            and config["scope"] == "selected_raw_to_decisions",
            "Original source identity",
        )
        workflow = self.json(d + "/workflow.json")
        plan = self.json(d + "/plan.json")
        parent = self.json(d + "/parent-acceptance.json")
        identity = plan["identity"]
        p.require(
            identity == workflow["identity"] == parent["identity"]
            and identity["task"] == "0043"
            and identity["validation_owner"] == "0043"
            and identity["scope"] == "selected_raw_to_decisions"
            and identity["config_sha256"] == self.pins[provenance["config_path"]]
            and identity["prompt_sha256"] == self.pins[provenance["prompt_path"]]
            and identity["protocol_kind"] == config["kind"]
            and identity["payload_scope"] == config["payload_scope"],
            "Task0043 plan identity",
        )
        p.require(
            parent["status"] == workflow["status"] == SOURCE_STATUS
            and parent["task"] == workflow["task"] == plan["task"] == "0043"
            and parent["workflow_sha256"] == self.pins[d + "/workflow.json"]
            and parent["plan_sha256"]
            == workflow["plan_sha256"]
            == self.pins[d + "/plan.json"]
            and workflow["synthetic_only"] is False
            and plan["synthetic_only"] is False
            and workflow["validation_bootstrap"] is False
            and plan["validation_bootstrap"] is False
            and workflow["sleep_assertion"]["released"] is True
            and workflow["overshoot_seconds"] == 0,
            "Accepted parent relationships/lifecycle",
        )
        p.require(
            workflow["source_map"] == plan["source_map"]
            and workflow["dependencies"] == plan["dependencies"],
            "Historical maps agree",
        )
        if check_historical_sources:
            # Only old declared source entries; new additive files are irrelevant.
            for n, sha in plan["source_map"].items():
                p.require(
                    (
                        n.endswith(".py")
                        and n.split("/")[0] in ("src", "scripts", "tests")
                    )
                    or n in p.HISTORICAL_METADATA_PINS,
                    "Only originally bound software/metadata entries",
                )
                path = p.safe(self.root, n)
                p.require(
                    p.file_hash(path) == sha, "Originally bound source entry: " + n
                )
                if not n.endswith(".py"):
                    self.audit.setdefault(
                        "historical_metadata_hash_only_reads", []
                    ).append(dict(path=n, bytes=path.stat().st_size, sha256=sha))
        p.require(
            p.digest(plan["source_map"])
            == summary["validation"]["source_map_canonical_sha256"],
            "Accepted historical source map canonical identity",
        )
        p.require(
            [w["phase"] for w in workflow["workers"]]
            == ["repetition1", "repetition2", "repetition3", "reporting"],
            "Complete original worker order",
        )
        for w in workflow["workers"]:
            x = w["dispatch"]
            a = w["acceptance"]
            p.require(
                type(x["returncode"]) is int
                and x["returncode"] == 0
                and x["child_reaped"] is True
                and x["parent_confirms_normal_exit"] is True
                and x["within_deadline"] is True
                and x["parent_error"] is None
                and x["overshoot_seconds"] == 0
                and x["exit_observed_continuous"] <= x["stage_deadline_continuous"]
                and a["status"] == "parent_accepted_worker"
                and a["task"] == "0043"
                and a["normal_exit_reaped"] is True,
                "Original normal worker exit/reap/deadline",
            )
        parity = summary["parity"]
        p.require(
            parity["exact_feature_score_mask_bytes"] is True
            and parity["feature_score_mask_mismatches"] == [0, 0, 0]
            and parity["every_timed_warmup_output_checked"] is True
            and parity["pre_post_golden_references_exact"] is True,
            "Accepted exact parity",
        )
        csv_cells = list(csv.DictReader(io.StringIO(self.data[CELLS].decode())))
        p.require(
            len(csv_cells) == 24
            and summary["results"]["cells"] == 24
            and summary["results"]["timed_calls"] == 480
            and summary["results"]["warmup_calls"] == 72
            and summary["results"]["table_sha256"] == self.pins[CELLS],
            "Curated complete coverage",
        )
        cells = {}
        for cell in csv_cells:
            key = (cell["candidate"], int(cell["B"]), int(cell["repetition"]))
            p.require(
                key not in cells
                and cell["scope"] == "selected_raw_to_decisions"
                and cell["strategy"] == "natural",
                "Unique natural cells",
            )
            cells[key] = cell
        vectors = {}
        for rep in (1, 2, 3):
            prefix = f"{d}/repetition{rep}/"
            receipt = self.json(prefix + "receipt.json")
            agg = self.json(prefix + "aggregate.json")
            timer = self.json(prefix + "timer.json")
            p.require(
                receipt["task"] == agg["task"] == "0043"
                and receipt["identity"] == agg["identity"] == identity
                and receipt["status"] == "body_complete_awaiting_exit"
                and receipt["source_map"] == plan["source_map"]
                and receipt["dependencies"] == plan["dependencies"]
                and workflow["workers"][rep - 1]["body_sha256"]
                == self.pins[prefix + "receipt.json"]
                and set(receipt["outputs"])
                == {"aggregate.json", "timings.jsonl", "timer.json"}
                and all(
                    self.pins[prefix + n] == sha
                    for n, sha in receipt["outputs"].items()
                ),
                "Receipt output map/identity",
            )
            p.require(
                timer["monotonic"] is True
                and timer["adjustable"] is False
                and timer["storage"] == "integer_ns"
                and timer["recorded_before_timing"] is True
                and timer["resolution_seconds"] > 0,
                "Integer timer context",
            )
            records = [
                json.loads(line, object_pairs_hook=unique_pairs)
                for line in self.data[prefix + "timings.jsonl"].splitlines()
            ]
            self.audit["jsonl_loads"] += 1
            self.audit["jsonl_records_parsed"] += len(records)
            expected = [row for c in candidates(rep) for row in schedule(rep, c)]
            p.require(
                len(records) == len(expected) == 184, "184full records per worker"
            )
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
                    "Exact ordered schema/cell/phase/call/window schedule",
                )
                integer(r["elapsed_ns"], "positive int ns source", minimum=1)
                p.require(
                    all(
                        type(r[k]) in (int, float) and math.isfinite(r[k])
                        for k in (
                            "start_continuous",
                            "end_continuous",
                            "continuous_minus_timer_ns",
                        )
                    )
                    and r["end_continuous"] >= r["start_continuous"]
                    and (
                        not ordinal
                        or r["start_continuous"]
                        >= records[ordinal - 1]["end_continuous"]
                    ),
                    "Original continuous metadata order",
                )
            p.require(
                agg["exact_feature_score_decision_parity"] is True
                and len(agg["gates"]) == 48
                and all(
                    g["status"] == "exact_feature_score_decision_bytes_passed"
                    and g["feature_score_decision_mismatches"] == [0, 0, 0]
                    for g in agg["gates"]
                ),
                "Aggregate exact gates",
            )
            self.audit["warmup_records_excluded"] += 24
            expected_chron = [
                {k: r[k] for k in ("candidate", "B", "phase", "ordinal", "elapsed_ns")}
                for r in records
            ]
            p.require(
                p.digest(agg["chronology"]) == p.digest(expected_chron),
                "Aggregate duration/order exact copy",
            )
            self.audit["aggregate_chronology_duration_copies_parsed"] += len(
                agg["chronology"]
            )
            self.audit["aggregate_observation_copies_parsed"] += sum(
                len(c["observations_ns"]) for c in agg["cells"]
            )
            self.audit["aggregate_cell_statistic_copies_parsed"] += len(
                agg["cells"]
            ) * len(STATS)
            p.require(len(agg["cells"]) == 8, "Eight worker cells")
            seen = set()
            for c in agg["cells"]:
                key = (c["candidate"], c["B"], rep)
                p.require(
                    type(c["B"]) is int
                    and type(c["repetition"]) is int
                    and all(type(v) is int for v in c["observations_ns"]),
                    "Strict worker cell types",
                )
                p.require(
                    key not in seen
                    and c["repetition"] == rep
                    and c["scope"] == "selected_raw_to_decisions"
                    and c["strategy"] == "natural"
                    and c["window_call_counts"] == [7, 7, 6]
                    and c["timer"] == timer,
                    "Unique worker natural cell",
                )
                seen.add(key)
                q = tuple(
                    r["elapsed_ns"]
                    for r in records
                    if r["candidate"] == key[0]
                    and r["B"] == key[1]
                    and r["phase"] == "timed"
                )
                p.require(
                    len(q) == 20 and list(q) == c["observations_ns"],
                    "Only20ordered timed services",
                )
                self.audit["timed_records_selected"] += len(q)
                compare_stats(q, c)
                cc = cells[key]
                parsed = {
                    k: int(cc[k])
                    if k in ("count", "minimum_ns", "maximum_ns")
                    else float(cc[k])
                    for k in STATS
                }
                compare_stats(q, parsed)
                self.audit["curated_cell_statistic_copies_parsed"] += len(STATS)
                p.require(
                    cc["window_call_counts"] == "7/7/6"
                    and int(cc["actual_batch_rows"]) == key[1],
                    "Curated window/fullB coverage",
                )
                vectors[key] = q
        expected_keys = {
            (c, b, r) for c in p.CANDIDATES for b in (1, 8, 32, 128) for r in (1, 2, 3)
        }
        p.require(
            set(vectors) == set(cells) == expected_keys, "24separate vectors/480samples"
        )
        pools = summary["results"]["pooled"]
        p.require(
            len(pools) == 8
            and {(c["candidate"], c["B"]) for c in pools}
            == {(c, b) for c in p.CANDIDATES for b in (1, 8, 32, 128)},
            "Complete curated pooled statistics",
        )
        for cell in pools:
            q = tuple(
                v
                for rep in (1, 2, 3)
                for v in vectors[cell["candidate"], cell["B"], rep]
            )
            compare_stats(q, cell)
        self.audit["curated_pooled_statistic_copies_parsed"] = len(pools) * len(STATS)
        retained = sum(
            sys.getsizeof(v) for q in vectors.values() for v in (q, *q)
        ) + sys.getsizeof(vectors)
        p.require(
            retained <= p.LIMITS["retained_service_vectors_bytes"],
            "1MiB retained services",
        )
        self.audit.update(
            retained_service_vector_bytes=retained,
            service_vectors=24,
            service_values=480,
        )
        return vectors, self.audit


def fingerprints(vectors):
    return {
        f"{c}/{b}/{r}": hashlib.sha256(
            b"".join(struct.pack("<q", v) for v in q)
        ).hexdigest()
        for (c, b, r), q in vectors.items()
    }
