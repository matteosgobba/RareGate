"""Task0049: closed, stdlib-only curation of accepted aggregate metadata.

No experiment, operational controller, model, array, network or replay imports.
The Task0046 summary's embedded timing-vector subtree is skipped lexically.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from itertools import islice
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = "configs/reporting/cpu_trigger_synthesis_v1.json"
PREFIX = "results/tables/final/task0049-"
STATUS = "completed_curated_cpu_trigger_synthesis"
CONTEXT = ("mode", "rate", "seed", "candidate", "B", "timeout_ns", "repetition")
SIDES = ("natural_anchor", "full_control")
MAPPINGS = ("next_anchor", "previous_anchor")
SUPPORTS = ("coarse_reference", "refined_32")
METRICS = ("overflow_dropped", "deadline_misses_processed", "latency_ns_p99")
FORBIDDEN_CONSTANTS = {"nan", "+nan", "-nan", "inf", "+inf", "-inf", "infinity"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON: {value}")


def value_end(text, start):
    """Find a JSON value's end without decoding its strings or number arrays."""
    i = start
    stack = []
    quoted = False
    escaped = False
    while i < len(text):
        char = text[i]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
                if not stack:
                    return i + 1
        elif char == '"':
            quoted = True
        elif char in "[{":
            stack.append(char)
        elif char in "]}":
            if not stack:
                break
            require(stack.pop() == ("]" == char and "[" or "{"), "JSON brackets")
            if not stack:
                return i + 1
        elif char == "," and not stack:
            break
        i += 1
    require(not stack and not quoted and i > start, "Incomplete JSON value")
    return i


def project_root(text, omitted):
    """Omit entire root members before semantic JSON decoding, with no traversal."""
    if not omitted:
        return text
    require(text.lstrip().startswith("{"), "Projected JSON must be object")
    i = text.index("{") + 1
    pieces = []
    seen = set()
    decoder = json.JSONDecoder()
    while True:
        while i < len(text) and text[i].isspace():
            i += 1
        if text[i] == "}":
            break
        key, end = decoder.raw_decode(text, i)
        require(isinstance(key, str) and key not in seen, "Root key identity")
        seen.add(key)
        i = end
        while text[i].isspace():
            i += 1
        require(text[i] == ":", "JSON colon")
        i += 1
        while text[i].isspace():
            i += 1
        end = value_end(text, i)
        if key not in omitted:
            pieces.append(json.dumps(key) + ":" + text[i:end])
        i = end
        while text[i].isspace():
            i += 1
        require(text[i] in ",}", "JSON separator")
        if text[i] == "}":
            break
        i += 1
    require(not text[i + 1 :].strip(), "Trailing JSON content")
    require(set(omitted) <= seen, "Missing projected subtree")
    return "{" + ",".join(pieces) + "}"


def decode_json(text, omitted=()):
    return json.loads(
        project_root(text, omitted),
        object_pairs_hook=unique_object,
        parse_float=Decimal,
        parse_constant=reject_constant,
    )


def json_text(value):
    # Decimal strings retain the original printed precision; no float conversion.
    return json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n"


def safe_path(root, relative):
    rel = Path(relative)
    require(not rel.is_absolute() and ".." not in rel.parts, "Repository-relative path")
    path = root / rel
    require(path.is_relative_to(root), "Root containment")
    require(not any(v.is_symlink() for v in (path, *path.parents)), "Symlink source")
    require(path.is_file(), f"Missing source: {relative}")
    return path


def expected_source_paths():
    """Mechanically expand the user's fixed groups, without filesystem discovery."""
    paths = set()
    for task, report, stem in (
        ("0022", "frozen-cpu-benchmark-v2", "frozen-cpu-benchmark-v2"),
        ("0038", "prepared-batch-service-measurement", "prepared-batch-service"),
        ("0040", "development-raw-feature-measurement", "development-raw-feature"),
        ("0043", "development-raw-decision-campaign-v2", "development-raw-decision"),
        (
            "0045",
            "natural-partial-raw-decision-measurement",
            "natural-partial-raw-decision",
        ),
        (
            "0047",
            "targeted-partial-raw-decision-measurement",
            "targeted-partial-raw-decision",
        ),
        ("0037", "synthetic-trigger-simulator", "synthetic-trigger"),
        ("0044", "deterministic-joint-service-replay", "joint-service-replay"),
        ("0046", "occupancy-aware-service-replay", "occupancy-service-replay"),
        ("0048", "refined-support-service-replay", "refined-service-replay"),
    ):
        paths.add("docs/" + report + ".md")
        suffixes = [
            "summary.json",
            "cells.csv"
            if task in ("0022", "0038", "0040", "0043", "0045", "0047")
            else "scenarios.csv",
        ]
        if task in ("0044", "0046", "0048"):
            suffixes.append("contrasts.csv")
        paths.update(
            f"results/tables/final/task{task}-{stem}-{suffix}" for suffix in suffixes
        )
    paths.update(
        (
            "results/tables/final/task0047-targeted-partial-selection.csv",
            "docs/two-three-prong-synthesis.md",
            "results/tables/final/task0032-two-three-prong-synthesis-summary.json",
            "results/tables/final/task0032-global-quality.csv",
            "results/tables/final/task0032-calibrated-utility.csv",
            "docs/confirmation-source-feasibility.md",
            "results/tables/final/task0036-confirmation-source-feasibility-summary.json",
            "results/tables/final/task0023-cpu-mps-benchmark-summary.json",
            "results/tables/final/task0024-ae-onnx-cpu-export-summary.json",
            "docs/pytorch-onnx-cpu-benchmark.md",
            "results/tables/final/task0025-pytorch-onnx-cpu-benchmark-summary.json",
            "results/tables/final/task0039-development-raw-feature-summary.json",
            "results/tables/final/task0041-development-raw-decision-summary.json",
            "results/tables/final/task0042-development-decision-admission-summary.json",
        )
    )
    paths.update(
        "configs/benchmarks/" + name + ".json"
        for name in (
            "frozen_cpu_v2",
            "prepared_batch_service_v1",
            "development_raw_measurement_v1",
            "development_raw_decision_v2",
            "development_partial_raw_decision_v1",
            "development_targeted_raw_decision_v1",
        )
    )
    paths.update(
        "configs/simulation/" + name + ".json"
        for name in (
            "synthetic_trigger_v1",
            "joint_service_replay_v1",
            "occupancy_service_replay_v1",
            "refined_service_replay_v1",
        )
    )
    return paths


def validate_manifest(config):
    require(
        config["task"] == "0049" and config["source_count"] == 57, "Task0049 registry"
    )
    require(config["input_cap_bytes"] == 32 * 1024**2, "Fixed metadata cap")
    rows = config["source_manifest"]
    require(
        len(rows) == 57 and {r["path"] for r in rows} == expected_source_paths(),
        "Exact closed source set",
    )
    require(
        sum(r["bytes"] for r in rows) == config["input_total_bytes"] == 26010109,
        "Registry byte total",
    )
    require(
        config["scope"]["operational_execution_authorized"] is False
        and config["scope"]["source_set_expansion"] is False,
        "Metadata scope only",
    )


class EvidenceReader:
    """One bounded read of each explicit file per pass; all reads are journaled."""

    def __init__(self, root, config):
        self.root, self.config = Path(root), config
        self.manifest = {v["path"]: v for v in config["source_manifest"]}
        require(
            len(self.manifest) == len(config["source_manifest"]), "Duplicate source"
        )
        self.reads = []
        self.total_bytes = 0
        self.completed = set()
        self.csv_counts = {}

    def path(self, task, role):
        matches = [
            r["path"]
            for r in self.manifest.values()
            if r["source_task"] == task and r["role"] == role
        ]
        require(len(matches) == 1, f"Source role: {task}/{role}")
        return matches[0]

    def chunks(self, relative):
        require(relative in self.manifest, "Source outside closed registry")
        require(relative not in self.completed, "Repeated source in one pass")
        meta = self.manifest[relative]
        path = safe_path(self.root, relative)
        require(path.stat().st_size == meta["bytes"], "Source size drift")
        require(
            self.total_bytes + meta["bytes"] <= self.config["input_cap_bytes"],
            "Total input ceiling",
        )
        digest = hashlib.sha256()
        row = dict(
            path=relative, source_task=meta["source_task"], bytes=0, state="reading"
        )
        self.reads.append(row)
        with path.open("rb") as handle:
            while block := handle.read(65536):
                row["bytes"] += len(block)
                self.total_bytes += len(block)
                require(row["bytes"] <= meta["bytes"], "Input grew during read")
                require(self.total_bytes <= self.config["input_cap_bytes"], "Input cap")
                digest.update(block)
                row["sha256"] = digest.hexdigest()
                yield block
        row.update(sha256=digest.hexdigest(), state="complete")
        require(row["bytes"] == meta["bytes"], "Short source read")
        require(row["sha256"] == meta["sha256"], "Source hash drift")
        self.completed.add(relative)

    def text(self, relative):
        return b"".join(self.chunks(relative)).decode("utf-8", errors="strict")

    def json(self, task, role):
        relative = self.path(task, role)
        return decode_json(
            self.text(relative),
            self.config.get("metadata_projection", {}).get(relative, ()),
        )

    def rows(self, task, role):
        relative = self.path(task, role)
        schema = self.config["csv_schemas"][relative]

        def lines():
            pending = b""
            for block in self.chunks(relative):
                pending += block
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    require(len(line) <= 131072, "CSV line envelope")
                    yield (line + b"\n").decode("utf-8", errors="strict")
                require(len(pending) <= 131072, "CSV line envelope")
            if pending:
                yield pending.decode("utf-8", errors="strict")

        rows = csv.reader(lines(), strict=True)
        header = next(rows)
        require(header == schema["columns"], "Exact CSV columns/order")
        require(
            len(set(header)) == len(header) and all(header), "CSV header uniqueness"
        )
        count = 0
        for values in rows:
            require(len(values) == len(header), "CSV row width")
            result = {}
            for key, value in zip(header, values, strict=True):
                require(value.lower() not in FORBIDDEN_CONSTANTS, "Nonfinite CSV")
                if key in schema["string_columns"]:
                    result[key] = value
                elif key in schema["boolean_columns"]:
                    false, true = schema["boolean_literals"]
                    require(value in (false, true), "CSV Boolean")
                    result[key] = value == true
                elif value == "":
                    result[key] = None
                else:
                    require(len(value) <= 128, "Numeric token envelope")
                    require(
                        re.fullmatch(
                            r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", value
                        ),
                        f"Numeric CSV column: {key}",
                    )
                    result[key] = (
                        int(value) if re.fullmatch(r"-?\d+", value) else Decimal(value)
                    )
                    require(Decimal(result[key]).is_finite(), "Finite CSV number")
            count += 1
            require(count <= schema["rows"], "Extra CSV row")
            yield result
        require(count == schema["rows"], "Missing CSV row")
        self.csv_counts[relative] = count


def integer(value):
    require(type(value) is int, "Exact non-Boolean integer required")
    return value


def source_equal(actual, expected):
    if actual is None or expected is None:
        return actual is expected
    if isinstance(actual, (int, Decimal)) and not isinstance(actual, bool):
        return Decimal(actual) == Decimal(expected)
    return actual == expected


def binary_difference(left, right):
    if left is None or right is None:
        return None
    if type(left) is int and type(right) is int:
        return left - right
    result = float(left) - float(right)
    require(math.isfinite(result), "Finite descriptor arithmetic")
    return result


def contrast_equal(actual, expected):
    if actual is None or expected is None:
        return actual is expected
    if type(expected) is int:
        return type(actual) is int and actual == expected
    return math.isfinite(float(actual)) and float(actual) == expected


def recover_integer_sum(mean, count):
    """Recover a unique integer-ns total inside the printed mean's binary64 cell."""
    integer(count)
    require(count > 0, "Positive timed count")
    numeric = float(mean)
    require(math.isfinite(numeric) and numeric > 0, "Positive mean")
    with localcontext() as context:
        context.prec = 80
        center = Decimal.from_float(numeric) * count
        bound = Decimal.from_float(math.ulp(numeric)) * count
        nearest = int(center.to_integral_value())
        require(
            bound < Decimal("0.5") and abs(center - nearest) <= bound,
            "Unique integer-ns sum",
        )
    return nearest


def check_scenario(row):
    for key in (
        "generated",
        "admitted",
        "completed",
        "overflow_dropped",
        "pending",
        "busy_ns",
    ):
        require(integer(row[key]) >= 0, "Nonnegative scenario count")
    require(
        row["generated"] == row["admitted"] + row["overflow_dropped"],
        "Admission conservation",
    )
    require(
        row["admitted"] == row["completed"] + row["pending"] and row["pending"] == 0,
        "Final drain",
    )
    require(
        row["deadline_misses_processed"] + row["on_time_completed"] == row["completed"],
        "Late survivors",
    )
    require(
        row["completed_at_horizon"] + row["pending_at_horizon"] == row["admitted"],
        "Horizon conservation",
    )
    require(
        row["waiting_at_horizon"] + row["in_service_at_horizon"]
        == row["pending_at_horizon"],
        "Horizon state",
    )
    require(row["end_ns"] - row["horizon_ns"] == row["drain_ns"], "Drain duration")
    require(
        row["full_batches"] + row["partial_batches"] == row["batches"],
        "Batch conservation",
    )
    require(
        row["latency_ns_count"] == row["dispatch_wait_ns_count"] == row["completed"],
        "Survivor denominator",
    )
    for cut in ("0900", "0950", "0990", "0999"):
        require(
            row[f"toy_{cut}_selected"] + row[f"toy_{cut}_rejected"] == row["completed"],
            "Toy cut conservation",
        )
    if "exact_events" in row:
        for suffix, denominator in (
            ("events", "completed"),
            ("batches", "batches"),
            ("busy_ns", "busy_ns"),
        ):
            require(
                row["exact_" + suffix] + row["mapped_" + suffix] == row[denominator],
                "Mapping conservation",
            )
        require(
            row["modeled_row_work"] - row["completed"]
            == row["modeled_minus_actual_rows"],
            "Modeled work",
        )


def add_totals(totals, row, fields):
    for key in fields:
        totals[key] += integer(row[key])


def range_add(stats, value):
    if value is None:
        stats["null"] += 1
        return
    stats["negative" if value < 0 else "positive" if value > 0 else "zero"] += 1
    stats["minimum"] = (
        value if stats["minimum"] is None else min(stats["minimum"], value)
    )
    stats["maximum"] = (
        value if stats["maximum"] is None else max(stats["maximum"], value)
    )
    # Only additive event-count metrics are summed. Quantiles are never summed.
    if type(value) is int:
        stats["sum"] += value


def new_range():
    return dict(
        minimum=None, maximum=None, negative=0, positive=0, zero=0, null=0, sum=0
    )


def family_values(variants, number, field):
    """Return D, natural level change, control level change in source operation order."""
    values = [row[field] for row in variants]
    differences = [binary_difference(values[i], values[i + 1]) for i in (0, 2, 4, 6)]
    if number in (0, 1, 3, 4):
        return differences[{0: 0, 1: 1, 3: 2, 4: 3}[number]], None, None
    if number in (2, 5):
        offset = 0 if number == 2 else 4
        return (
            binary_difference(differences[offset // 2 + 1], differences[offset // 2]),
            binary_difference(values[offset + 2], values[offset]),
            binary_difference(values[offset + 3], values[offset + 1]),
        )
    offset = 0 if number == 6 else 2
    return (
        binary_difference(differences[2 + offset // 2], differences[offset // 2]),
        binary_difference(values[4 + offset], values[offset]),
        binary_difference(values[5 + offset], values[1 + offset]),
    )


def refined_replay(reader, summary):
    scenarios = iter(reader.rows("0048", "synthetic_scenarios"))
    contrasts = iter(reader.rows("0048", "synthetic_contrasts"))
    totals = {key: Counter() for key in summary["totals"]}
    fields = list(next(iter(summary["totals"].values())))
    ranges = {
        key: {metric: new_range() for metric in METRICS}
        for key in summary["contrast_ranges"]
    }
    levels = {key: Counter() for key in ranges}
    families = list(summary["contrast_ranges"])
    require(
        families
        == [
            "coarse_reference/next_natural_minus_control",
            "coarse_reference/previous_natural_minus_control",
            "coarse_reference/mapping_interaction",
            "refined_32/next_natural_minus_control",
            "refined_32/previous_natural_minus_control",
            "refined_32/mapping_interaction",
            "next_anchor/support_interaction",
            "previous_anchor/support_interaction",
        ],
        "Eight contrast families",
    )
    contexts = 0
    seen_contexts = set()
    b1_controls = 0
    b8_controls = 0
    trace_map = {}
    for context_id in range(756):
        group = list(islice(scenarios, 8))
        require(len(group) == 8, "Eight variants per context")
        context = tuple(group[0][k] for k in CONTEXT)
        require(context not in seen_contexts, "Unique complete context")
        seen_contexts.add(context)
        for index, row in enumerate(group):
            require(
                row["scenario_id"] == 8 * context_id + index, "Ordered scenario IDs"
            )
            require(
                tuple(row[k] for k in CONTEXT) == context, "Complete scenario context"
            )
            require(
                (row["support"], row["mapping"], row["billing"])
                == (SUPPORTS[index // 4], MAPPINGS[index % 4 // 2], SIDES[index % 2]),
                "Variant identity",
            )
            check_scenario(row)
            key = "/".join(row[k] for k in ("support", "mapping", "billing"))
            add_totals(totals[key], row, fields)
            trace_key = row["mode"], row["rate"], row["seed"]
            require(
                trace_map.setdefault(trace_key, row["trace_sha256"])
                == row["trace_sha256"],
                "Trace reuse",
            )
        descriptor_fields = [
            key
            for key, value in group[0].items()
            if key not in (*CONTEXT, "scenario_id", "trace_sha256")
            and (value is None or type(value) is int or isinstance(value, Decimal))
        ]
        compare_fields = [
            key
            for key in descriptor_fields
            if not key.startswith(("new_selected_point_", "remeasured_reference_"))
        ]
        if group[0]["B"] == 1:
            for side in (0, 1):
                for index in (side + 2, side + 4, side + 6):
                    require(
                        all(
                            group[index][key] == group[side][key]
                            for key in compare_fields
                        ),
                        "B1 numerical control",
                    )
            b1_controls += 1
        if group[0]["B"] == 8:
            for side in (0, 1):
                require(
                    all(
                        group[4 + side][key] == group[6 + side][key]
                        for key in compare_fields
                    ),
                    "Refined B8 equality",
                )
                require(
                    all(
                        group[4 + side][key] == 0
                        for key in ("mapped_batches", "mapped_events", "mapped_busy_ns")
                    ),
                    "Refined B8 exact lookup",
                )
            b8_controls += 1
        for number, family in enumerate(families):
            row = next(contrasts)
            require(
                tuple(row[k] for k in CONTEXT) == context and row["contrast"] == family,
                "Contrast context/family",
            )
            require(row["trace_sha256"] == group[0]["trace_sha256"], "Contrast trace")
            for i, variant in enumerate(group):
                for key in (
                    "scenario_id",
                    "generated",
                    "completed",
                    "overflow_dropped",
                    "deadline_misses_processed",
                    "batches",
                    "busy_ns",
                ):
                    require(
                        row[f"v{i}_{key}"] == variant[key],
                        "Constituent reference/denominator",
                    )
            for field in descriptor_fields:
                if field + "_difference" not in row:
                    continue
                expected = family_values(group, number, field)
                for suffix, value in zip(
                    ("_difference", "_natural_level_change", "_control_level_change"),
                    expected,
                    strict=True,
                ):
                    require(
                        contrast_equal(row[field + suffix], value),
                        f"Contrast arithmetic: {field}{suffix}",
                    )
            for metric in METRICS:
                range_add(ranges[family][metric], row[metric + "_difference"])
                if metric != "latency_ns_p99":
                    for side in ("natural", "control"):
                        value = row[metric + "_" + side + "_level_change"]
                        if value is not None:
                            levels[family][metric + "_" + side + "_level_change"] += (
                                integer(value)
                            )
        contexts += 1
    require(
        next(scenarios, None) is None and next(contrasts, None) is None,
        "Complete ordered streams",
    )
    require(contexts == 756, "Complete contexts")
    require(
        b1_controls == 108 and b8_controls == 216,
        "Full numerical-control context coverage",
    )
    require(
        all(dict(value) == summary["totals"][key] for key, value in totals.items()),
        "Eight summary totals",
    )
    for family, metrics in ranges.items():
        for metric, values in metrics.items():
            source = summary["contrast_ranges"][family][metric + "_difference"]
            for key in ("minimum", "maximum", "negative", "positive", "zero", "null"):
                require(
                    source_equal(values[key], source[key]),
                    "Published contrast range/signs",
                )
            if metric != "latency_ns_p99":
                require(values["sum"] == source["sum"], "Published count contrast sum")
            else:
                values.pop("sum")
    overall = {key: sum(value[key] for value in totals.values()) for key in fields}
    require(
        [
            overall[k]
            for k in (
                "generated",
                "completed",
                "overflow_dropped",
                "deadline_misses_processed",
            )
        ]
        == [30240000, 27544586, 2695414, 6067628],
        "Current aggregate counts",
    )
    return dict(
        contexts=contexts,
        totals=totals,
        overall=overall,
        contrast_ranges=ranges,
        level_changes=levels,
        B1_contexts_checked=b1_controls,
        refined_B8_contexts_checked=b8_controls,
        trace_hashes={"/".join(map(str, k)): v for k, v in trace_map.items()},
    )


def physical_key(task, row):
    if task == "0022":
        return row["model"], row["batch"], row["scope"]
    if task == "0038":
        return row["candidate"], row["B"], row["m"], row["strategy"]
    if task == "0040":
        return row["B"], row["scope"]
    if task == "0043":
        return row["candidate"], row["B"]
    return row["candidate"], row["B"], row["m"], row["side"]


def physical_metadata(reader, summaries, config):
    groups = []
    boundaries = []
    counts = {}
    notes = []
    for task in ("0022", "0038", "0040", "0043", "0045", "0047"):
        summary = summaries[task]
        cells = defaultdict(list)
        selected = defaultdict(list)
        for row_number, row in enumerate(reader.rows(task, "physical_cells"), start=2):
            count = integer(row["count"])
            require(
                count == (200 if task == "0022" else 50 if task == "0038" else 20),
                "Timed samples per cell",
            )
            for field, value in row.items():
                if (field.endswith("_ns") or field in ("count",)) and value is not None:
                    require(Decimal(value) >= 0, "Nonnegative physical statistic")
            if task == "0047":
                require(
                    row["wrapper"]
                    == "task0047_owned_C_FP32_actual_rows_public_score_strict4_copies_v1",
                    "Current actual-row wrapper",
                )
                require(
                    row["actual_rows"]
                    == row["model_shape_rows"]
                    == (row["m"] if row["side"] == "natural_m" else row["B"]),
                    "Current model shape",
                )
            key = physical_key(task, row)
            cells[key].append((row_number, row))
            candidate = row.get("candidate", row.get("model", "no_model"))
            flavor = row.get(
                "side", row.get("strategy", row.get("scope", "full_natural"))
            )
            if task == "0022":
                flavor = row["scope"]
            selected[candidate, flavor].append(row_number)
        pooled = (
            summary["timing_groups"]
            if task == "0022"
            else summary["pooled_cells"]
            if task == "0038"
            else summary["results"]["pooled"]
            if task == "0043"
            else summary["pooled"]
        )
        require(len(cells) == len(pooled), "Complete physical case pools")
        for entry in pooled:
            key = physical_key(task, entry)
            repetitions = cells.pop(key)
            require(len(repetitions) == 3, "Three physical repetitions")
            total_count = sum(row["count"] for _, row in repetitions)
            total_ns = sum(
                recover_integer_sum(row["mean_ns"], row["count"])
                for _, row in repetitions
            )
            mean = (
                entry["pooled_600_invocation_mean_ns"]
                if task == "0022"
                else entry.get("mean_ns", entry.get("mean"))
            )
            count = 600 if task == "0022" else entry["count"]
            require(count == total_count, "Pooled timed denominator")
            expected = total_ns / total_count
            discrepancy = abs(float(mean) - expected)
            require(
                discrepancy <= math.ulp(expected),
                "Pooled mean serialization consistency",
            )
            if discrepancy:
                notes.append(
                    dict(
                        task=task,
                        case=list(key),
                        difference_ULP=str(discrepancy / math.ulp(expected)),
                    )
                )
            groups.append(
                dict(
                    task=task,
                    case=list(key),
                    count=count,
                    mean_ns=mean,
                    recovered_timed_sum_ns=total_ns,
                    source_summary_key=(
                        "timing_groups"
                        if task == "0022"
                        else "pooled_cells"
                        if task == "0038"
                        else "results.pooled"
                        if task == "0043"
                        else "pooled"
                    ),
                    source_cell_rows=[n for n, _ in repetitions],
                    repetition_mean_ns=[row["mean_ns"] for _, row in repetitions],
                    original_pooled_statistics=entry,
                )
            )
        require(not cells, "No missing physical pools")
        counts[task] = dict(
            cells=sum(map(len, selected.values())),
            timed_calls=sum(g["count"] for g in groups if g["task"] == task),
            pooled_groups=len(pooled),
        )
        for (candidate, flavor), rows in selected.items():
            method = config["physical_methods"][task]
            boundaries.append(
                dict(
                    boundary_id=f"CPU{task}-{len(boundaries) + 1:02}",
                    task=task,
                    status=summary.get("execution_status", summary.get("status")),
                    candidate=candidate,
                    measured_scope=flavor,
                    **method,
                    repetitions=3,
                    timed_cells=len(rows),
                    timed_calls=sum(
                        g["count"]
                        for g in groups
                        if g["task"] == task
                        and all(n in rows for n in g["source_cell_rows"])
                    ),
                    units="integer ns whole invocation; actual/useful row denominators explicit; machine decimal precision preserved",
                    evidence_path=reader.path(task, "physical_cells"),
                    source_rows="/".join(map(str, rows)),
                )
            )
    return dict(
        case_groups=groups, campaign_counts=counts, mean_serialization_notes=notes
    ), boundaries


def previous_replay(reader, task, summary):
    published = summary["scenario_groups"] if task == "0037" else summary["totals"]
    totals = {key: Counter() for key in published}
    trace_map = {}
    rows = 0
    for row in reader.rows(task, "synthetic_scenarios"):
        check_scenario(row)
        key = (
            row["group"]
            if task == "0037"
            else row["assignment"]
            if task == "0044"
            else row["mapping"] + "/" + row["billing"]
        )
        require(key in totals, "Earlier replay variant")
        for field in published[key]:
            if field == "scenarios":
                totals[key][field] += 1
            elif field == "event_presentations":
                totals[key][field] += row["generated"]
            elif field in row and type(row[field]) is int:
                totals[key][field] += row[field]
        trace_key = (
            row.get("mode", row.get("arrival_mode")),
            row.get("rate", row.get("nominal_rate")),
            row["seed"],
        )
        require(
            trace_map.setdefault(trace_key, row["trace_sha256"]) == row["trace_sha256"],
            "Earlier trace reuse",
        )
        rows += 1
    for key, expected in published.items():
        for field, value in expected.items():
            if type(value) is int:
                require(
                    totals[key][field] == value,
                    f"Earlier aggregate agreement: {task}/{key}/{field}",
                )
    contrasts = Counter()
    differences = defaultdict(Counter)
    if task != "0037":
        for row in reader.rows(task, "synthetic_contrasts"):
            family = row["assignment"] if task == "0044" else row["contrast"]
            contrasts[family] += 1
            for field in ("overflow_dropped", "deadline_misses_processed"):
                differences[family][field] += integer(row[field + "_difference"])
        require(
            sum(contrasts.values()) == (1008 if task == "0044" else 2268),
            "Earlier contrast count",
        )
    return dict(
        scenarios=rows,
        totals=totals,
        contrast_family_counts=contrasts,
        additive_count_contrast_sums=differences,
        trace_hashes={"/".join(map(str, k)): v for k, v in trace_map.items()},
    )


def scientific_metadata(reader, summary):
    quality = list(reader.rows("0032", "scientific_quality_rows"))
    calibrated = list(reader.rows("0032", "scientific_calibrated_rows"))
    for table, original in (
        (quality, summary["global_quality"]),
        (calibrated, summary["calibrated_utility"]),
    ):
        require(len(table) == len(original), "All scientific rows retained")
        for left, right in zip(table, original, strict=True):
            require(set(left) == set(right), "Scientific column identity")
            require(
                all(source_equal(left[k], right[k]) for k in left),
                "Scientific copied facts agree",
            )
    require(len(quality) == 4 and len(calibrated) == 16, "Scientific scope")
    require(
        {r["quality_reference_batch"] for r in quality} == {4096},
        "Scientific reference shape",
    )
    require(
        {r["background_total"] for r in quality} == {150471}, "Shared BG denominator"
    )
    require(
        {r["signal_total"] for r in quality} == {100000}, "Both signal denominators"
    )
    require(
        len({(r["candidate"], r["topology"]) for r in quality}) == 4,
        "Both candidates/topologies",
    )
    for candidate in ("pca-v1", "compact-autoencoder-v2"):
        for target in (
            Decimal("0.1"),
            Decimal("0.05"),
            Decimal("0.01"),
            Decimal("0.001"),
        ):
            selected = [
                r
                for r in calibrated
                if r["candidate"] == candidate and r["target_fpr"] == target
            ]
            require(
                len(selected) == 2
                and selected[0]["threshold"] == selected[1]["threshold"],
                "Frozen calibration shared",
            )
            require(
                all(
                    selected[0][k] == selected[1][k]
                    for k in (
                        "background_accepted",
                        "background_total",
                        "background_fpr",
                    )
                ),
                "Shared historical BG",
            )
    return dict(
        quality_rows=quality,
        calibrated_points=calibrated,
        newly_computed_scientific_metrics=0,
        rule="Copied accepted facts only; no new AUC/AP/curve/threshold/interval/significance or ranking calculation",
    )


def selection_metadata(reader, summary, boundary):
    counts = Counter()
    seen = set()
    supports = {int(k): set(v) for k, v in boundary["supports"]["refined_32"].items()}
    for row in reader.rows("0047", "occupancy_selection"):
        key = row["B"], row["m"]
        require(
            key not in seen and row["B"] in supports and 1 <= row["m"] <= row["B"],
            "Selection occupancy identity",
        )
        seen.add(key)
        counts[row["case_class"]] += 1
        require(
            row["selected_for_campaign"] == (row["m"] in supports[row["B"]]),
            "Selection/current support",
        )
    require(
        len(seen) == 169 and sum(len(v) for v in supports.values()) == 32,
        "Current occupancy matrix",
    )
    require(
        sorted(counts.values()) == [15, 17, 137],
        "Current reference/new/unmeasured classification",
    )
    require(
        summary["cells"] == 384 and summary["timed_pairs"] == 3840,
        "Current measurement coverage",
    )
    return dict(
        legal_occupancies=169,
        measured=32,
        unmeasured=137,
        classifications=dict(counts),
        all_source_unfavorable_pairs_preserved=333,
        new_point_unfavorable_pairs=1,
        full_occupancy_unfavorable_pairs=231,
    )


def build_replay_table(reader, configs, studies):
    result = []
    for task in ("0037", "0044", "0046", "0048"):
        config, study = configs[task], studies[task]
        old = task in ("0037", "0044")
        result.append(
            dict(
                task=task,
                timing_source={
                    "0037": "Task0022 preloaded adapter aggregate means;worker constants for sensitivity",
                    "0044": "Task0043 full raw-to-decision",
                    "0046": "Task0045 paired natural/control15points",
                    "0048": "Task0047 current paired32points;coarse15current references",
                }[task],
                vector_scope={
                    "0037": "Count-weighted600-invocation adapter mean per candidate/B;separate worker mean/p99/max constants",
                    "0044": "24 separate candidate/repetition/B ordered20sample vectors",
                    "0046": "90 separate paired20position vectors;3600original durations;embedded payload omitted here",
                    "0048": "192 separate paired20position vectors;7680original durations",
                }[task],
                assignment_cursor_phase={
                    "0037": "Fixed ceiling-rounded constant;no sample cursor",
                    "0044": "Zero-origin modulo20 cyclic;ceil mean constant;reverse/rotation10 for stated subset",
                    "0046": "Independent zero-origin per-anchor modulo20;one advance/dispatch",
                    "0048": "Independent zero-origin per-anchor modulo20;reset each scenario;shared vectors at common support anchors",
                }[task],
                partial_billing_mapping={
                    "0037": "Full-B constant for m synthetic events;hypothetical padded-slot accounting",
                    "0044": "Full-B measured duration billed to m actual synthetic events;no physical padding",
                    "0046": "Next/previous sparse anchor;natural_k or contemporaneous same-case full-B control",
                    "0048": "Refined32/coarse15 next/previous anchor;natural_k or same-case full-B control",
                }[task],
                rates_per_second=json.dumps(
                    config.get(
                        "rates_per_second", config.get("arrivals", {}).get("rates")
                    )
                ),
                seeds="41/42/43",
                arrival_modes="periodic/poisson",
                events_per_trace=5000,
                generator="PCG64 SeedSequence[3700,seed,mode_id,rate,stream_id];periodic/exponential integer gaps;separate toy scores",
                trace_identity_rule="18 hashes checked against scenario rows;later0044/0046/0048 identical;0037 different workload grid",
                trace_hashes=json.dumps(study["trace_hashes"], sort_keys=True),
                policies=json.dumps(config["policies"]),
                capacity=1024,
                deadline_ns=config["deadline_ns"],
                startup_horizon_drain="Time zero includes startup;trace horizon retained;final admitted drain;survivor latency excludes overflow",
                toy_cuts="strict .9/.95/.99/.999 after completion;independent synthetic scores,no physical TPR/FPR",
                scenarios=study["scenarios"] if task != "0048" else 6048,
                contrasts=sum(study["contrast_family_counts"].values())
                if task not in ("0037", "0048")
                else 0
                if task == "0037"
                else 6048,
                presentations=sum(
                    v.get("generated", v.get("event_presentations", 0))
                    for v in study["totals"].values()
                ),
                unique_trace_positions_within_study=90000,
                interpretation="Finite synthetic sensitivity;repeated presentations are not independent events;no cross-grid pooling or deployment policy",
                source=reader.path(task, "synthetic_scenarios"),
                method_source=reader.path(task, "synthetic_method_report"),
                original_grid=old,
            )
        )
    return result


def build_conclusion_table(study, summary):
    rows = []
    for variant, totals in study["totals"].items():
        account = summary["variant_accounting"][variant]
        rows.append(
            dict(
                record_type="variant_totals",
                identifier=variant,
                contexts=756,
                **totals,
                mapped_event_fraction=str(
                    Decimal(totals["mapped_events"]) / Decimal(totals["completed"])
                ),
                mapped_busy_fraction=str(
                    Decimal(totals["mapped_busy_ns"]) / Decimal(totals["busy_ns"])
                ),
                modeled_row_surplus=account["modeled_row_surplus"],
                modeled_row_deficit=account["modeled_row_deficit"],
                evidence="Task0048 scenarios,complete ordered variant;summary.variant_accounting for separate surplus/deficit",
                derivation="Exact count sums;fractions use completed events or assigned busy ns;separate work components copied from curated metadata,not rederived from forbidden occupancy ledger",
            )
        )
    for family, metrics in study["contrast_ranges"].items():
        row = dict(
            record_type="contrast_family",
            identifier=family,
            contexts=756,
            evidence="Task0048 contrasts,contrast=" + family,
            derivation="Every scenario/constituent/denominator and arithmetic identity checked in each of756contexts;quantile extrema/signs only,no percentile average or sum",
        )
        for metric, stats in metrics.items():
            row.update({metric + "_difference_" + k: v for k, v in stats.items()})
        row.update(study["level_changes"][family])
        rows.append(row)
    for variant, counts in summary["residual_occupancy_support_changes"].items():
        rows.append(
            dict(
                record_type="context_local_residual_change",
                identifier=variant,
                contexts=756,
                **{k: v for k, v in counts.items() if type(v) is int},
                evidence="Task0048 summary.residual_occupancy_support_changes."
                + variant,
                derivation="Copied curated counts;residual m outside measured32 and absent in matched coarse context;not new physical measurement or global discovery",
            )
        )
    return rows


def validate_statuses(summaries):
    expected = {
        "0022": "complete_accepted_consumed_no_retry",
        "0038": "parent_accepted_prepared_development_measurement",
        "0040": "parent_accepted_development_raw_feature_measurement",
        "0043": "parent_accepted_development_raw_decision_measurement",
        "0045": "parent_accepted_natural_partial_raw_decision_measurement",
        "0047": "parent_accepted_targeted_partial_raw_decision_measurement",
        "0037": "parent_accepted_synthetic_sweep",
        "0044": "parent_accepted_synthetic_joint_service_replay",
        "0046": "parent_accepted_synthetic_occupancy_service_replay",
        "0048": "parent_accepted_synthetic_refined_support_service_replay",
    }
    for task, status in expected.items():
        require(
            summaries[task].get("execution_status", summaries[task].get("status"))
            == status,
            f"Historical source status: {task}",
        )
    require(
        summaries["0025"]["outcome"]["performance_comparison_accepted"] is False,
        "Rejected0025 preserved",
    )
    require(
        summaries["0024"]["numerical_equivalence_accepted"] is True,
        "Accepted export distinct",
    )
    require(
        summaries["0023"]["physical_device_validated"] is False, "No new device claim"
    )
    require(
        summaries["0041"]["status"] == "failed_prerequisites_no_retry",
        "Failed admission remains failed",
    )
    require(
        summaries["0042"]["status"] == "software_accepted_synthetic_admission_repair",
        "Software-only repair",
    )
    require(
        summaries["0036"]["confirmation_source_accepted"] is False
        and summaries["0036"]["route_decision"] == "unresolved_no_acquisition",
        "Independent confirmation unresolved",
    )


def csv_text(rows):
    columns = list(dict.fromkeys(key for row in rows for key in row))
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {key: "" if value is None else value for key, value in row.items()}
        )
    return out.getvalue()


def markdown_table(columns, rows):
    return "\n".join(
        [
            "| " + " | ".join(columns) + " |",
            "| " + " | ".join("---" for _ in columns) + " |",
            *("| " + " | ".join(map(str, row)) + " |" for row in rows),
        ]
    )


def display_decimal(value, scale=1, places=6):
    return format(Decimal(str(value)) / Decimal(scale), f".{places}f")


def report_tables(summary):
    science = summary["scientific_context"]
    tables = {}
    names = {"pca-v1": "PCA", "compact-autoencoder-v2": "AE"}
    tables["quality"] = markdown_table(
        ["Candidate", "Signal", "Accepted AUC", "Accepted AP", "BG / signal rows"],
        [
            (
                names[r["candidate"]],
                r["topology"],
                display_decimal(r["roc_auc"]),
                display_decimal(r["average_precision"]),
                "150471 / 100000",
            )
            for r in science["quality_rows"]
        ],
    )
    tables["calibration"] = markdown_table(
        [
            "Candidate",
            "Signal",
            "Original target FPR",
            "Frozen threshold",
            "Signal accepted / 100000",
            "Shared BG accepted / 150471",
        ],
        [
            (
                names[r["candidate"]],
                r["topology"],
                r["target_fpr"],
                r["threshold"],
                r["signal_accepted"],
                r["background_accepted"],
            )
            for r in science["calibrated_points"]
        ],
    )
    cost_rows = []
    for group in summary["physical"]["case_groups"]:
        task, case = group["task"], group["case"]
        include = (
            task == "0022"
            and case[1] == 1
            and case[2] == "adapter_decision"
            or task == "0038"
            and case[1:] == [1024, 1, "natural"]
            or task == "0040"
            and case == [128, "selected_raw_to_features"]
            or task == "0043"
            and case[1] in (1, 128)
            or task == "0045"
            and case[1:3] == [128, 32]
            or task == "0047"
            and case[1] == 128
            and case[2] in (10, 32)
        )
        if include:
            cost_rows.append(
                (
                    task,
                    "/".join(map(str, case)),
                    group["count"],
                    display_decimal(group["mean_ns"], 1000000),
                    "/".join(
                        display_decimal(v, 1000000, 3)
                        for v in group["repetition_mean_ns"]
                    ),
                )
            )
    tables["costs"] = markdown_table(
        [
            "Task",
            "Fixed case / scope / side",
            "Timed count",
            "Whole-call mean ms",
            "All three cell means ms",
        ],
        cost_rows,
    )
    current = summary["replay_studies"]["0048"]
    tables["variants"] = markdown_table(
        [
            "Current support / mapping / side",
            "Completed",
            "Overflow",
            "Late survivors",
            "Mapped event %",
            "Mapped busy %",
            "Modeled surplus / deficit",
        ],
        [
            (
                key,
                row["completed"],
                row["overflow_dropped"],
                row["deadline_misses_processed"],
                display_decimal(
                    100 * Decimal(row["mapped_events"]) / Decimal(row["completed"]),
                    places=4,
                ),
                display_decimal(
                    100 * Decimal(row["mapped_busy_ns"]) / Decimal(row["busy_ns"]),
                    places=4,
                ),
                str(summary["current_variant_accounting"][key]["modeled_row_surplus"])
                + " / "
                + str(
                    summary["current_variant_accounting"][key]["modeled_row_deficit"]
                ),
            )
            for key, row in current["totals"].items()
        ],
    )
    family_rows = []
    for key, values in current["contrast_ranges"].items():
        overflow, late, quantile = (values[k] for k in METRICS)

        def signs(value):
            return "/".join(
                str(value[k]) for k in ("negative", "zero", "positive", "null")
            )

        family_rows.append(
            (
                key,
                overflow["sum"],
                late["sum"],
                signs(overflow),
                signs(late),
                display_decimal(quantile["minimum"], 1000000, 3)
                + " to "
                + display_decimal(quantile["maximum"], 1000000, 3),
            )
        )
    tables["contrasts"] = markdown_table(
        [
            "Family (756 contexts each)",
            "Sum D overflow",
            "Sum D late",
            "Overflow −/0/+/null",
            "Late −/0/+/null",
            "Per-context survivor-p99 contrast range ms",
        ],
        family_rows,
    )
    tables["levels"] = markdown_table(
        [
            "Refined−coarse",
            "Δ natural overflow",
            "Δ control overflow",
            "ΔD overflow",
            "Δ natural late",
            "Δ control late",
            "ΔD late",
        ],
        [
            (
                mapping,
                current["level_changes"][mapping + "/support_interaction"][
                    "overflow_dropped_natural_level_change"
                ],
                current["level_changes"][mapping + "/support_interaction"][
                    "overflow_dropped_control_level_change"
                ],
                current["contrast_ranges"][mapping + "/support_interaction"][
                    "overflow_dropped"
                ]["sum"],
                current["level_changes"][mapping + "/support_interaction"][
                    "deadline_misses_processed_natural_level_change"
                ],
                current["level_changes"][mapping + "/support_interaction"][
                    "deadline_misses_processed_control_level_change"
                ],
                current["contrast_ranges"][mapping + "/support_interaction"][
                    "deadline_misses_processed"
                ]["sum"],
            )
            for mapping in MAPPINGS
        ],
    )
    tables["residuals"] = markdown_table(
        [
            "Refined mapping / side",
            "Matched contexts with new residual / 756",
            "Batches",
            "Useful events",
            "Assigned busy ns",
        ],
        [
            (
                key,
                row["contexts_with_new_residual_occupancies"],
                row["new_residual_batches"],
                row["new_residual_events"],
                row["new_residual_busy_ns"],
            )
            for key, row in summary["residual_occupancy_support_changes"].items()
        ],
    )
    return tables


def document_checks(root, summary):
    report = root / "docs/cpu-trigger-study-synthesis.md"
    brief = root / "docs/cpu-trigger-study-decision-brief.md"
    if not report.is_file() or not brief.is_file():
        return dict(status="report_documents_pending")
    english, italian = report.read_text(), brief.read_text()
    tables = report_tables(summary)
    for name, table in tables.items():
        expected = (
            f"<!-- task0049-table:{name} -->\n{table}\n<!-- /task0049-table:{name} -->"
        )
        require(expected in english, f"Report/table agreement: {name}")
    prose = "\n".join(
        line
        for line in english.split("## References")[0].splitlines()
        if not line.startswith(("|", "<!--"))
    )
    words = len(prose.split())
    brief_words = len(italian.split())
    lead = english.split("<!-- task0049-lead-start -->")[1].split(
        "<!-- task0049-lead-end -->"
    )[0]
    require(2000 <= words <= 3500, "English prose word envelope")
    require(200 <= len(lead.split()) <= 300, "Outcome lead word envelope")
    require(500 <= brief_words <= 800, "Italian brief word envelope")
    return dict(
        status="report_tables_and_lengths_checked",
        english_prose_words=words,
        english_lead_words=len(lead.split()),
        italian_brief_words=brief_words,
        generated_tables_checked=len(tables),
        new_figures=0,
    )


def synthesize(reader):
    config = reader.config
    summaries = {}
    boundary_configs = {}
    # Reports are method evidence, not links to be followed or new runtime checks.
    method_checks = []
    for source in config["source_manifest"]:
        role, task = source["role"], source["source_task"]
        if source["format"] == "md":
            text = reader.text(source["path"])
            require(text.startswith("#") and len(text) > 100, "Method report structure")
            method_checks.append(dict(path=source["path"], words=len(text.split())))
        elif source["format"] == "json":
            value = reader.json(task, role)
            if role.endswith("boundary_config"):
                boundary_configs[task] = value
            else:
                require(value.get("task") == task, "Summary source task identity")
                summaries[task] = value
    validate_statuses(summaries)
    physical, boundaries = physical_metadata(reader, summaries, config)
    science = scientific_metadata(reader, summaries["0032"])
    selection = selection_metadata(reader, summaries["0047"], boundary_configs["0048"])
    studies = {
        task: previous_replay(reader, task, summaries[task])
        for task in ("0037", "0044", "0046")
    }
    studies["0048"] = refined_replay(reader, summaries["0048"])
    require(
        studies["0044"]["trace_hashes"]
        == studies["0046"]["trace_hashes"]
        == studies["0048"]["trace_hashes"],
        "Identical later trace hashes",
    )
    require(
        len(reader.completed) == 57
        and reader.total_bytes == config["input_total_bytes"],
        "Exact57 source completeness",
    )
    replay_table = build_replay_table(reader, boundary_configs, studies)
    conclusion_table = build_conclusion_table(studies["0048"], summaries["0048"])
    claims = config["claims"]
    for claim in claims:
        require(
            claim["class"]
            in {
                "physical_measurement",
                "synthetic_result",
                "scientific_context",
                "software_only",
                "unresolved",
            },
            "Claim class",
        )
        require(
            all(path in reader.manifest for path in claim["evidence_paths"].split("|")),
            "Claim evidence is allowlisted",
        )
    outputs = {
        PREFIX + "cpu-trigger-evidence-registry.csv": csv_text(
            config["source_manifest"]
        ),
        PREFIX + "cpu-service-boundaries.csv": csv_text(boundaries),
        PREFIX + "replay-comparability.csv": csv_text(replay_table),
        PREFIX + "refined-replay-conclusions.csv": csv_text(conclusion_table),
        PREFIX + "cpu-trigger-claims.csv": csv_text(claims),
    }
    summary = dict(
        task="0049",
        status=STATUS,
        kind="metadata_only_phase_closure_no_operational_reacceptance",
        phase_decision="Close declared native CPU and synthetic study within scope;preserve frozen baseline",
        next_separately_scoped_question="Design-only development streaming/cache/transport protocol;no implementation,acquisition,resource reservation orTask0050 authorization",
        source_count=57,
        source_bytes=reader.total_bytes,
        input_cap_bytes=config["input_cap_bytes"],
        source_manifest=config["source_manifest"],
        rules=config["rules"],
        source_read_accounting=dict(
            source_opens=len(reader.reads),
            bytes=reader.total_bytes,
            reads=reader.reads,
            scope="This reproducible helper pass only;preparatory and final byte-hash passes separately journaled in Task0049 handoff",
        ),
        schema_row_counts=reader.csv_counts,
        method_reports=method_checks,
        physical=physical,
        scientific_context=science,
        current_occupancy_matrix=selection,
        replay_studies=studies,
        current_variant_accounting=summaries["0048"]["variant_accounting"],
        residual_occupancy_support_changes=summaries["0048"][
            "residual_occupancy_support_changes"
        ],
        verification=dict(
            source_hashes_sizes_and_57file_set=True,
            schema_finite_types=True,
            source_statuses_preserved=True,
            physical_count_weighted_means=True,
            scientific_4plus16_copied_rows=True,
            earlier_replay_aggregate_conservation=True,
            current_all8variants_and8contrast_families=True,
            constituent_ID_denominators_and_signs=True,
            B1_and_refinedB8_numerical_controls=True,
            shared_later18trace_hashes=True,
            original_source_preservation="Byte hashes checked during every read;final57file recheck required before delivery",
        ),
        metadata_projection=config["metadata_projection"],
        scope_inspection_finding=config["scope_inspection_finding"],
        operational_prohibited_work=dict(
            raw_event_membership_golden_feature_scientific_score_fingerprint_loads=0,
            HDF_raw_custody=0,
            models_inference_reconstruction=0,
            optimizer_fitting_calibration=0,
            new_scientific_metrics_intervals_significance=0,
            acquisition_download=0,
            hardware_runtime_availability_checks=0,
            physical_timing=0,
            queue_replay=0,
            trace_generation=0,
            old_workflow_controller_calls=0,
            new_grants_reservations_claims_assertions=0,
        ),
        timing_payload_scope_note="Two early generic metadata inspections decoded embedded0046timing arrays,not used;explicit exception above. Final helper omits them. No timing-pair CSV/JSONL or ignored operational evidence opened.",
        scientific_state=dict(
            baseline="complete_within_frozen_two_three_prong_scope",
            confirmation="unresolved_no_acquisition",
            exposure=["YES", "YES", "YES"],
            particle="192/192consumed_canonical_deferred",
            affiliation="Independent research inspired by LHC computing;no official experiment/CERN affiliation",
        ),
        historical_activity="Earlier physical campaigns and generated/model/optimizer fixtures remain positive historical activity;Task0049 does not repeat them or claim a global zero.",
        copied_facts_versus_arithmetic=dict(
            copied="Source statuses,scientific metrics/calibration,method boundaries,original pooled per-case statistics,separate surplus/deficit and residual occupancy counts",
            derived="Exact CSV count sums/conservation,unique integer-duration totals from cell means,scoped weighted means,scenario contrast identities/sign/ranges and denominator fractions",
            forbidden="No scientific metric/CI,pooling across cost cases,percentile averaging,source-sequence arithmetic,replay or experiment",
        ),
        new_figures=0,
        figure_policy="Existing figure links suffice;historical PNGs unchanged",
        claims=len(claims),
        validation_scope="Small independent metadata helper fixtures and relevant lint/format;no fresh full-suite/native/hosted-CI claim",
        output_hashes={
            name: hashlib.sha256(text.encode()).hexdigest()
            for name, text in outputs.items()
        },
    )
    summary["document_checks"] = document_checks(reader.root, summary)
    summary["recorded_task0049_checks"] = config.get("recorded_task0049_checks", {})
    summary["own_reproduction_artifact_hashes"] = {
        name: hashlib.sha256((reader.root / name).read_bytes()).hexdigest()
        for name in (
            CONFIG,
            "scripts/summarize_cpu_trigger_study.py",
            "tests/test_cpu_trigger_synthesis.py",
            "docs/prompts/0049-cpu-trigger-study-synthesis.md",
        )
    }
    if summary["document_checks"]["status"] == "report_documents_pending":
        summary["status"] = "metadata_checked_report_documents_pending"
    outputs[PREFIX + "cpu-trigger-synthesis-summary.json"] = json_text(summary)
    require(
        sum(len(text.encode()) for text in outputs.values()) <= 4 * 1024**2,
        "Small curated output envelope",
    )
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify existing curated outputs without changing them",
    )
    parser.add_argument(
        "--audit",
        type=Path,
        help="Write this pass's metadata read journal under data/task0049-validation",
    )
    args = parser.parse_args()
    if args.audit:
        audit = args.audit.absolute()
        require(
            audit.parent == ROOT / "data/task0049-validation"
            and not audit.exists()
            and not audit.is_symlink(),
            "Use a fresh own metadata audit path; existing journals are preserved",
        )
    config = decode_json(safe_path(ROOT, CONFIG).read_text())
    validate_manifest(config)
    for path, sha in config["mandatory_anchors"].items():
        require(
            next(r for r in config["source_manifest"] if r["path"] == path)["sha256"]
            == sha,
            "Mandatory registry anchor",
        )
    reader = EvidenceReader(ROOT, config)
    try:
        outputs, summary = synthesize(reader)
        for name, text in outputs.items():
            path = ROOT / name
            if args.check:
                require(
                    path.read_bytes() == text.encode(), f"Curated output drift: {name}"
                )
            else:
                require(not path.is_symlink(), "Output symlink")
                path.write_text(text)
        print(
            json.dumps(
                dict(
                    status=summary["status"],
                    mode="check" if args.check else "curate",
                    source_opens=len(reader.reads),
                    source_bytes=reader.total_bytes,
                    outputs=len(outputs),
                    current_contexts=756,
                    new_experiments=0,
                )
            )
        )
    finally:
        if args.audit:
            audit = args.audit.absolute()
            require(
                audit.parent == ROOT / "data/task0049-validation"
                and not audit.is_symlink(),
                "Own metadata audit path",
            )
            with audit.open("x") as handle:
                handle.write(
                    json_text(
                        dict(
                            task="0049",
                            mode="check" if args.check else "curate",
                            source_opens=len(reader.reads),
                            source_bytes=reader.total_bytes,
                            reads=reader.reads,
                        )
                    )
                )


if __name__ == "__main__":
    main()
