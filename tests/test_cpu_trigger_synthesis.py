"""Independent, tiny stdlib metadata fixtures; no operational sources or models."""

import ast
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/summarize_cpu_trigger_study.py"
SPEC = importlib.util.spec_from_file_location("cpu_trigger_synthesis", SCRIPT)
study = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(study)


class MetadataFixtures(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name).resolve()

    def tearDown(self):
        self.directory.cleanup()

    def reader(self, payload, columns=None, count=1, cap=4096):
        name = "fixture.csv" if columns else "fixture.json"
        (self.root / name).write_text(payload)
        encoded = payload.encode()
        config = dict(
            source_manifest=[
                dict(
                    path=name,
                    source_task="fixture",
                    role="test",
                    bytes=len(encoded),
                    sha256=hashlib.sha256(encoded).hexdigest(),
                )
            ],
            input_cap_bytes=cap,
            csv_schemas={
                name: dict(
                    columns=columns,
                    rows=count,
                    string_columns=[],
                    boolean_columns=[],
                    boolean_literals=["False", "True"],
                )
            },
        )
        return study.EvidenceReader(self.root, config)

    def test_duplicate_json_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            study.decode_json('{"a":1,"a":2}')

    def test_nonfinite_json_is_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                study.decode_json('{"a":' + token + "}")

    def test_projection_does_not_decode_nested_payload(self):
        value = '{"task":"0046","vectors":{"secret":[[17,41],[19,43]],"quoted":"}\\"["},"count":90}'
        projected = study.project_root(value, ["vectors"])
        self.assertNotIn("secret", projected)
        self.assertNotIn("17", projected)
        self.assertEqual(
            study.decode_json(value, ["vectors"]), dict(task="0046", count=90)
        )

    def test_projected_root_duplicates_are_rejected(self):
        with self.assertRaises(ValueError):
            study.decode_json('{"vectors":{},"vectors":{}}', ["vectors"])

    def test_unbalanced_projection_is_rejected(self):
        with self.assertRaises(ValueError):
            study.decode_json('{"vectors":[1,2}', ["vectors"])

    def test_projection_preserves_strict_metadata_validation(self):
        with self.assertRaises(ValueError):
            study.decode_json('{"vectors":{},"metadata":{"x":1,"x":2}}', ["vectors"])

    def test_registry_is_mechanically_exactly57(self):
        paths = study.expected_source_paths()
        self.assertEqual(len(paths), 57)
        self.assertNotIn(
            "results/tables/final/task0047-targeted-partial-raw-decision-pairs.csv",
            paths,
        )
        self.assertFalse(any(name.endswith(".jsonl") for name in paths))

    def test_manifest_cannot_replace_source_with_operational_path(self):
        rows = [dict(path=p, bytes=0) for p in study.expected_source_paths()]
        rows[0]["path"] = "data/operational/input.npy"
        config = dict(
            task="0049",
            source_count=57,
            input_cap_bytes=32 * 1024**2,
            source_manifest=rows,
        )
        with self.assertRaisesRegex(ValueError, "Exact closed"):
            study.validate_manifest(config)

    def test_traversal_and_absolute_paths_rejected(self):
        for name in ("../escape.json", "/etc/passwd"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                study.safe_path(self.root, name)

    def test_symlink_source_rejected(self):
        (self.root / "original.json").write_text("{}")
        (self.root / "link.json").symlink_to(self.root / "original.json")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            study.safe_path(self.root, "link.json")

    def test_changed_hash_is_rejected(self):
        reader = self.reader('{"a":1}')
        (self.root / "fixture.json").write_text('{"a":2}')
        with self.assertRaisesRegex(ValueError, "hash drift"):
            reader.json("fixture", "test")

    def test_cap_is_checked_before_read(self):
        reader = self.reader('{"a":1}', cap=2)
        with self.assertRaisesRegex(ValueError, "ceiling"):
            reader.json("fixture", "test")
        self.assertEqual(reader.reads, [])

    def test_foreign_source_rejected_before_open(self):
        reader = self.reader("{}")
        with self.assertRaisesRegex(ValueError, "closed registry"):
            reader.text("unknown.json")

    def test_each_file_read_is_accounted_once(self):
        reader = self.reader('{"a":1}')
        self.assertEqual(reader.json("fixture", "test"), {"a": 1})
        self.assertEqual(reader.total_bytes, 7)
        self.assertEqual(reader.reads[0]["state"], "complete")
        with self.assertRaisesRegex(ValueError, "Repeated"):
            reader.json("fixture", "test")

    def test_csv_duplicate_header_rejected(self):
        reader = self.reader("n,n\n1,2\n", ["n", "n"])
        with self.assertRaisesRegex(ValueError, "uniqueness"):
            list(reader.rows("fixture", "test"))

    def test_csv_wrong_width_rejected(self):
        reader = self.reader("n,m\n1\n", ["n", "m"])
        with self.assertRaisesRegex(ValueError, "width"):
            list(reader.rows("fixture", "test"))

    def test_csv_nonfinite_and_boolean_number_rejected(self):
        for token in ("NaN", "inf", "True"):
            with self.subTest(token=token):
                reader = self.reader("n\n" + token + "\n", ["n"])
                with self.assertRaises(ValueError):
                    list(reader.rows("fixture", "test"))

    def test_csv_missing_row_rejected(self):
        reader = self.reader("n\n1\n", ["n"], count=2)
        with self.assertRaisesRegex(ValueError, "Missing CSV"):
            list(reader.rows("fixture", "test"))

    def test_csv_null_is_not_zero_and_decimal_precision_retained(self):
        reader = self.reader("n,m\n,0.123456789123456789\n", ["n", "m"])
        row = next(reader.rows("fixture", "test"))
        self.assertIsNone(row["n"])
        self.assertEqual(str(row["m"]), "0.123456789123456789")

    def test_recover_integer_sum_from_independent_tiny_sample(self):
        values = [11, 19, 29]
        self.assertEqual(study.recover_integer_sum(sum(values) / len(values), 3), 59)

    def test_fractional_total_is_not_invented(self):
        with self.assertRaisesRegex(ValueError, "Unique integer"):
            study.recover_integer_sum("0.125", 3)

    def test_boolean_cannot_be_count(self):
        with self.assertRaises(ValueError):
            study.integer(True)

    def test_all8_contrast_identities_and_level_changes(self):
        variants = [dict(y=value) for value in (10, 4, 8, 5, 7, 3, 11, 2)]
        expected = [
            (6, None, None),
            (3, None, None),
            (-3, -2, 1),
            (4, None, None),
            (9, None, None),
            (5, 4, -1),
            (-2, -3, -1),
            (6, 3, -3),
        ]
        self.assertEqual(
            [study.family_values(variants, i, "y") for i in range(8)], expected
        )

    def test_quantile_null_propagates_only_when_constituent_needed(self):
        variants = [dict(y=value) for value in (None, 4, 8, 5, 7, 3, 11, 2)]
        self.assertEqual(study.family_values(variants, 3, "y"), (4, None, None))
        self.assertIsNone(study.family_values(variants, 6, "y")[0])

    def test_float_contrast_uses_original_binary64_order(self):
        value = study.binary_difference(study.Decimal("1.0"), study.Decimal("0.7"))
        self.assertTrue(study.contrast_equal(study.Decimal(str(1.0 - 0.7)), value))
        self.assertFalse(study.contrast_equal(study.Decimal("0.3"), value))

    def test_quantile_ranges_are_never_summed(self):
        stats = study.new_range()
        study.range_add(stats, study.Decimal("1.5"))
        study.range_add(stats, None)
        self.assertEqual(stats["sum"], 0)
        self.assertEqual(stats["null"], 1)

    def scenario(self):
        row = dict(
            generated=10,
            admitted=9,
            overflow_dropped=1,
            completed=9,
            pending=0,
            busy_ns=10,
            deadline_misses_processed=2,
            on_time_completed=7,
            completed_at_horizon=7,
            pending_at_horizon=2,
            waiting_at_horizon=1,
            in_service_at_horizon=1,
            end_ns=120,
            horizon_ns=100,
            drain_ns=20,
            full_batches=1,
            partial_batches=1,
            batches=2,
            latency_ns_count=9,
            dispatch_wait_ns_count=9,
            exact_events=4,
            mapped_events=5,
            exact_batches=1,
            mapped_batches=1,
            exact_busy_ns=3,
            mapped_busy_ns=7,
            modeled_row_work=11,
            modeled_minus_actual_rows=2,
        )
        for cut in ("0900", "0950", "0990", "0999"):
            row[f"toy_{cut}_selected"] = 2
            row[f"toy_{cut}_rejected"] = 7
        return row

    def test_independent_tiny_scenario_conserves_events_and_model_work(self):
        study.check_scenario(self.scenario())

    def test_independent_tiny_scenario_rejects_wrong_denominators(self):
        for key in (
            "admitted",
            "pending_at_horizon",
            "latency_ns_count",
            "mapped_events",
            "modeled_row_work",
        ):
            row = self.scenario()
            row[key] += 1
            with self.subTest(key=key), self.assertRaises(ValueError):
                study.check_scenario(row)

    def test_helper_imports_only_stdlib(self):
        tree = ast.parse(SCRIPT.read_text())
        imported = {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        imported |= {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertTrue(
            imported
            <= {
                "__future__",
                "argparse",
                "csv",
                "hashlib",
                "io",
                "json",
                "math",
                "re",
                "collections",
                "decimal",
                "itertools",
                "pathlib",
            }
        )


if __name__ == "__main__":
    unittest.main()
