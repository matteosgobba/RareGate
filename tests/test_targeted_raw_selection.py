"""Complete generated writer-to-reader selection custody without queue execution."""

import hashlib
import json

import pytest

from raregate.benchmarks import targeted_raw_selection as s
from raregate.benchmarks.targeted_raw_selection_fixture import write


@pytest.fixture
def bundle(tmp_path):
    return tmp_path, write(tmp_path)


def repin(root, manifest, name):
    manifest[name] = dict(
        bytes=(root / name).stat().st_size,
        sha256=hashlib.sha256((root / name).read_bytes()).hexdigest(),
    )


def relink_csv(root, manifest, name):
    """Keep outer generated custody valid so mutations exercise semantic reconciliation."""
    if name not in (s.SCENARIOS, s.OCCUPANCIES):
        return
    receipt = s.DIRECTORY + "/simulation/receipt.json"
    r = json.loads((root / receipt).read_text())
    r["outputs"]["scenarios.csv" if name == s.SCENARIOS else "occupancies.csv"] = (
        manifest[name]["sha256"]
    )
    (root / receipt).write_text(json.dumps(r))
    repin(root, manifest, receipt)
    workflow = s.DIRECTORY + "/workflow.json"
    w = json.loads((root / workflow).read_text())
    w["phases"][0]["body_sha256"] = manifest[receipt]["sha256"]
    (root / workflow).write_text(json.dumps(w))
    repin(root, manifest, workflow)
    for path, field in (
        (s.DIRECTORY + "/parent-acceptance.json", "workflow_sha256"),
        (s.SUMMARY, "workflow_sha256"),
    ):
        v = json.loads((root / path).read_text())
        v[field] = manifest[workflow]["sha256"]
        (root / path).write_text(json.dumps(v))
        repin(root, manifest, path)


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_complete_generated_writer_reader_ranking_conservation_and_inert_paths(
    tmp_path, newline
):
    manifest = write(tmp_path, newline=newline)
    result, audit = s.Bundle(tmp_path, manifest).load()
    assert audit["metadata_opens"] == 10 and audit["scenario_rows"] == 3024
    assert (
        len(result["selection_rows"]) == 169 and len(result["selected_new_cases"]) == 17
    )
    assert result["selected_new_cases"] == [
        [b, m]
        for b, ms in ((8, range(3, 7)), (32, range(3, 8)), (128, range(3, 11)))
        for m in ms
    ]
    assert (
        sum(r["case_class"] == "residual_unmeasured" for r in result["selection_rows"])
        == 137
    )
    assert not (tmp_path / "inert").exists()


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate_scenario",
        "missing_scenario",
        "foreign_scenario",
        "duplicate_occupancy",
        "missing_occupancy",
        "wrong_anchor",
        "wrong_shape",
        "wrong_count",
        "nonfinite",
        "boolean_integer",
        "foreign_case",
        "malformed_row",
    ],
)
def test_changed_records_are_rejected_after_repinning_generated_csv(bundle, fault):
    root, manifest = bundle
    name = s.SCENARIOS if "scenario" in fault else s.OCCUPANCIES
    path = root / name
    lines = path.read_text().splitlines(True)
    if fault.startswith("duplicate"):
        lines.insert(2, lines[1])
    elif fault.startswith("missing"):
        lines.pop(1)
    else:
        import csv
        import io

        rows = list(csv.DictReader(io.StringIO("".join(lines), newline="")))
        r = rows[0]
        field, value = {
            "foreign_scenario": ("candidate", "foreign"),
            "wrong_anchor": ("k", "2"),
            "wrong_shape": ("source_natural_service_B", "8"),
            "wrong_count": ("events", "2"),
            "nonfinite": ("busy_ns", "NaN"),
            "boolean_integer": ("batches", "True"),
            "foreign_case": ("m", "9"),
        }.get(fault, ("extra", "bad"))
        if fault == "malformed_row":
            path.write_text("".join(lines) + "broken,row\n")
        else:
            r[field] = value
            with path.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
    if fault.startswith(("duplicate", "missing")):
        path.write_text("".join(lines))
    repin(root, manifest, name)
    relink_csv(root, manifest, name)
    with pytest.raises((ValueError, KeyError, TypeError)):
        s.Bundle(root, manifest).load()


@pytest.mark.parametrize(
    "fault",
    [
        "status",
        "task",
        "owner",
        "scope",
        "receipt_link",
        "output_link",
        "exit",
        "reap",
        "release",
        "consumed",
        "fixture",
        "plan_link",
        "duplicate_json",
        "nonfinite_json",
        "changed_bytes",
        "symlink",
        "oversize",
        "foreign_path",
        "missing_path",
    ],
)
def test_closed_bundle_relationships_and_paths(bundle, fault):
    root, manifest = bundle
    name = s.SUMMARY
    r = json.loads((root / name).read_text())
    if fault in ("task", "owner", "scope"):
        r["identity"][
            {"task": "task", "owner": "validation_owner", "scope": "scope"}[fault]
        ] = "foreign"
    elif fault == "status":
        r["status"] = "body_complete_awaiting_exit"
    elif fault == "consumed":
        r["operational_allowance_consumed"] = False
    elif fault == "plan_link":
        r["execution_plan_sha256"] = "0" * 64
    elif fault in ("receipt_link", "exit", "reap", "release", "fixture"):
        name = s.DIRECTORY + "/workflow.json"
        r = json.loads((root / name).read_text())
        if fault == "receipt_link":
            r["phases"][0]["body_sha256"] = "0" * 64
        if fault == "exit":
            r["phases"][0]["dispatch"]["returncode"] = True
        if fault == "reap":
            r["phases"][0]["dispatch"]["child_reaped"] = False
        if fault == "release":
            r["sleep_assertion"]["released"] = False
        if fault == "fixture":
            r["fixture_only"] = True
    elif fault == "output_link":
        name = s.DIRECTORY + "/simulation/receipt.json"
        r = json.loads((root / name).read_text())
        r["outputs"]["scenarios.csv"] = "0" * 64
    elif fault == "foreign_path":
        manifest["../foreign.json"] = manifest.pop(s.SUMMARY)
    elif fault == "missing_path":
        manifest.pop(s.SUMMARY)
    elif fault == "symlink":
        q = root / name
        q.rename(q.with_suffix(".other"))
        q.symlink_to(q.with_suffix(".other"))
    elif fault == "oversize":
        manifest[name]["bytes"] = 9 * 2**20
    elif fault == "changed_bytes":
        (root / name).write_text("changed")
    elif fault in ("duplicate_json", "nonfinite_json"):
        (root / name).write_text(
            '{"a":1,"a":2}' if fault == "duplicate_json" else '{"a":NaN}'
        )
        repin(root, manifest, name)
    if fault in (
        "status",
        "task",
        "owner",
        "scope",
        "consumed",
        "plan_link",
        "receipt_link",
        "exit",
        "reap",
        "release",
        "fixture",
        "output_link",
    ):
        (root / name).write_text(json.dumps(r))
        repin(root, manifest, name)
    with pytest.raises((ValueError, KeyError, TypeError)):
        s.Bundle(root, manifest).load()


def test_selection_import_is_stdlib_only():
    import subprocess
    import sys

    code = 'from raregate.benchmarks import targeted_raw_selection;import sys;assert not any(n in sys.modules for n in ("numpy","torch","h5py","raregate.simulation.occupancy_engine","raregate.benchmarks.core"))'
    subprocess.run([sys.executable, "-c", code], check=True)
