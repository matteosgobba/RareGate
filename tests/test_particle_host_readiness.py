"""Synthetic Task0013 controller/probe lineage; never real host/data study."""

import json
import os
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from latenttrigger.models import particle_background as bg
from latenttrigger.models import particle_memory_study as old
from latenttrigger.supervision import particle_host as host
from latenttrigger.supervision import particle_launcher as ctl
from latenttrigger.supervision import particle_worker as worker
from latenttrigger.training import particle_resources as resources
from latenttrigger.training.particle_set import parse_vm_stat


@pytest.fixture
def config():
    return ctl.read(ctl.ROOT / ctl.CONFIG)


@pytest.fixture
def profile():
    return ctl.read(ctl.ROOT / ctl.PROFILE)


def test_fresh_stdlib_import_and_source_acceptance():
    code = """
import json,sys
from latenttrigger.supervision import particle_launcher as c
from latenttrigger.supervision import particle_worker
c.assert_lightweight()
print(json.dumps(c.source_hashes()))
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ctl.ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=True,
    )
    mapping = json.loads(result.stdout)
    assert mapping == bg.source_hashes()
    for name in ("particle_host", "particle_launcher", "particle_worker"):
        assert f"src/latenttrigger/supervision/{name}.py" in mapping
    assert "tests/test_particle_host_readiness.py" in mapping


@pytest.mark.parametrize(
    "pages,page_size", [(1, 4096), (294912, 16384), (0, 16384), (7, 65536)]
)
def test_pure_probe_exact_parity(pages, page_size):
    raw = (
        f"page size of {page_size} bytes\nPages free: {pages}.\nPages inactive: 123.\n"
    )
    assert host.parse_vm_stat(raw) == parse_vm_stat(raw)
    assert host.parse_vm_stat(raw)["available_bytes"] == (pages + 123) * page_size


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "Pages free: 1.\nPages inactive: 2.",
        "page size of 0 bytes\nPages free: 1.\nPages inactive: 2.",
        "page size of 4096 bytes\nPages free: 1.\nPages free: 2.\nPages inactive: 3.",
    ],
)
def test_missing_malformed_probe_fail_closed(raw):
    with pytest.raises(host.ResourceLimitError):
        host.parse_vm_stat(raw)


def test_optional_telemetry_missing_disclosed(monkeypatch):
    monkeypatch.setattr(
        host.ctypes,
        "CDLL",
        lambda *a, **kw: (_ for _ in ()).throw(OSError("restricted")),
    )
    result = host.process_context()
    assert result["current_rss_bytes"] is None
    assert result["pressure_dispatch_flags"] is None
    assert result["dirty_private_bytes"] is None


def test_historical_profile_configs_unchanged_and_strict(config, profile):
    assert ctl.digest(config) == ctl.CONFIG_HASH
    assert ctl.digest(profile) == ctl.PROFILE_HASH
    assert resources.validate_policy(profile, config) == ctl.PROFILE_HASH
    assert profile["scope"].startswith("Task0012")
    assert ctl.digest(ctl.read(ctl.ROOT / ctl.DESIGN)) == ctl.DESIGN_HASH


def reader_result(phase):
    return {
        "status": "passed",
        "engineering_policy_sha256": ctl.PROFILE_HASH,
        "model_config_sha256": ctl.CONFIG_HASH,
        "custody_completed": True,
        "view_events": 64 if phase == "dev_reader" else 0,
        "optimizer_steps_started": 0,
        "optimizer_steps_completed": 0,
        "resources": {
            "minimum_available_bytes": 4 * 2**30,
            "native_heap_reserved_bytes": 200 * 2**20,
            "peak_rss_bytes": 400 * 2**20,
            "phases": {
                "startup": {"first": {"native_heap_reserved_bytes": 100 * 2**20}}
            },
        },
    }


@pytest.mark.parametrize("increment", [0, 100 * 2**20, 400 * 2**20])
def test_activation_math_exact_frozen_parity(profile, increment):
    results = {p: reader_result(p) for p in ("dev_reader", "full_custody")}
    results["dev_reader"]["resources"]["native_heap_reserved_bytes"] = (
        100 * 2**20 + increment
    )
    evidence = {"workspace_measurement": {"peak_tensor_bytes": 5228448}}
    assert ctl.activation(results, evidence, profile) == resources.activation_decision(
        results, evidence, profile
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("optimizer_steps_started", 1),
        ("custody_completed", False),
        ("view_events", 65),
        ("engineering_policy_sha256", "wrong"),
    ],
)
def test_activation_invalid_receipt(profile, field, value):
    results = {p: reader_result(p) for p in ("dev_reader", "full_custody")}
    results["dev_reader"][field] = value
    with pytest.raises(ValueError):
        ctl.activation(
            results, {"workspace_measurement": {"peak_tensor_bytes": 1}}, profile
        )


@pytest.mark.parametrize(
    "phase",
    [
        "fit",
        "selection",
        "freeze",
        "background",
        "calibration",
        "test_background",
        "test_signal",
    ],
)
def test_forbidden_phase(phase):
    with pytest.raises(ValueError):
        ctl.authorize(phase, {"stages": []})


def test_phase_order_activation_and_failed_block():
    state = {"stages": []}
    ctl.authorize("pilot_preflight", state)
    with pytest.raises(ValueError):
        ctl.authorize("dev_reader", state)
    state["stages"] = [{"phase": "pilot_preflight", "status": "failed"}]
    with pytest.raises(ValueError):
        ctl.authorize("dev_reader", state)
    state["stages"] = [{"phase": p, "status": "passed"} for p in ctl.PHASES[:3]]
    with pytest.raises(ValueError):
        ctl.authorize("dev_preflight", state)
    state["activation"] = {"activated_for_bounded_dev": True}
    ctl.authorize("dev_preflight", state)


@pytest.fixture
def lineage_root(tmp_path, monkeypatch):
    monkeypatch.setattr(ctl, "ROOT", tmp_path)
    for rel in ctl.PREDECESSOR:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((bg.ROOT / rel).read_bytes())
    return tmp_path


def test_prior_exact_and_original_byte_preservation(lineage_root):
    ctl.verify_prior(lineage_root)
    for rel, digest in ctl.PREDECESSOR.items():
        assert ctl.file_hash(lineage_root / rel) == digest


@pytest.mark.parametrize(
    "later", ["dev_reader-reservation.json", "full_custody", "dev-reservation.json"]
)
def test_unexpected_later_consumption_refused(lineage_root, later):
    (lineage_root / "data/baselines/task0012-particle-memory-study" / later).write_text(
        "{}"
    )
    with pytest.raises(ValueError):
        ctl.verify_prior(lineage_root)


def test_task0011_ledger_not_loophole(lineage_root):
    (lineage_root / "data/baselines/task0011-particle-attempt-budget.json").write_text(
        "{}"
    )
    with pytest.raises(ValueError):
        ctl.verify_prior(lineage_root)


def test_predecessor_tamper_refused(lineage_root):
    path = lineage_root / next(iter(ctl.PREDECESSOR))
    path.write_text("changed")
    with pytest.raises(ValueError):
        ctl.verify_prior(lineage_root)


def test_exclusive_preparation_not_study_slot(tmp_path, monkeypatch):
    monkeypatch.setattr(ctl, "plan_definition", lambda r: {"scope": "bounded_only"})
    assert ctl.prepare(tmp_path) == ctl.prepare(tmp_path)
    assert not (tmp_path / ctl.SLOT).exists() and not (tmp_path / ctl.OUTPUT).exists()
    (tmp_path / ctl.PLAN).write_text("{}")
    with pytest.raises(ValueError):
        ctl.prepare(tmp_path)


def test_duplicate_study_refuses_before_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(ctl, "assert_lightweight", lambda: None)
    monkeypatch.setattr(ctl, "verify_plan", lambda r: None)
    ctl.exclusive(tmp_path / ctl.SLOT, {"consumed": True})
    monkeypatch.setattr(
        ctl, "dispatch", lambda *a, **k: pytest.fail("dispatched retry")
    )
    with pytest.raises(FileExistsError):
        ctl.run_study(tmp_path)


def test_failed_preflight_consumes_only_single_slot(tmp_path, monkeypatch):
    monkeypatch.setattr(ctl, "assert_lightweight", lambda: None)
    monkeypatch.setattr(ctl, "verify_plan", lambda r: None)
    ctl.exclusive(tmp_path / ctl.PLAN, {"mock": True})
    calls = []

    def fake(command, log, seconds, **kw):
        calls.append(command)
        path = tmp_path / ctl.OUTPUT / "pilot_preflight"
        path.mkdir()
        ctl.atomic(
            path / "stage-result.json",
            {"phase": "pilot_preflight", "status": "failed", "error": "availability"},
        )
        return {"returncode": 1, "elapsed_seconds_including_imports": 5}

    monkeypatch.setattr(ctl, "dispatch", fake)
    state = ctl.run_study(tmp_path)
    assert len(calls) == 1 and state["status"] == "bounded_study_failed"
    assert (tmp_path / ctl.SLOT).exists()
    assert not (tmp_path / ctl.OUTPUT / "dev_reader-reservation.json").exists()
    with pytest.raises(FileExistsError):
        ctl.run_study(tmp_path)


def test_parent_timeout_preserves_invocation_and_partial_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(ctl, "assert_lightweight", lambda: None)
    monkeypatch.setattr(ctl, "verify_plan", lambda r: None)
    ctl.exclusive(tmp_path / ctl.PLAN, {"mock": True})
    monkeypatch.setattr(
        ctl, "dispatch", lambda *a, **k: (_ for _ in ()).throw(TimeoutError("deadline"))
    )
    state = ctl.run_study(tmp_path)
    assert state["stages"][0]["partial_audit_must_be_reconciled"]
    assert (tmp_path / ctl.OUTPUT / "pilot_preflight-reservation.json").exists()
    assert not (tmp_path / ctl.OUTPUT / "dev_reader-reservation.json").exists()


@pytest.fixture
def worker_lineage(tmp_path, monkeypatch):
    monkeypatch.setattr(ctl, "ROOT", tmp_path)
    monkeypatch.setattr(
        ctl,
        "verify_plan",
        lambda **kw: {"canonical_selection_freeze_calibration_authorized": False},
    )
    ctl.exclusive(tmp_path / ctl.PLAN, {"mock": True})
    ctl.exclusive(
        tmp_path / ctl.SLOT,
        {
            "task": "0013",
            "status": "reserved_no_retry",
            "plan_sha256": ctl.file_hash(tmp_path / ctl.PLAN),
        },
    )
    output = tmp_path / ctl.OUTPUT
    ctl.exclusive(output / "workflow.json", {"stages": []})
    r = {
        "phase": "pilot_preflight",
        "token": "one",
        "status": "reserved_no_automatic_retry",
        "maximum_optimizer_steps": 0,
        "parent_pid": os.getppid(),
        "started_monotonic": time.monotonic(),
        "plan_sha256": ctl.file_hash(tmp_path / ctl.PLAN),
        "slot_sha256": ctl.file_hash(tmp_path / ctl.SLOT),
    }
    ctl.exclusive(output / "pilot_preflight-reservation.json", r)
    return output, r


@pytest.mark.parametrize(
    "field,value",
    [
        ("token", "wrong"),
        ("phase", "dev"),
        ("maximum_optimizer_steps", 96),
        ("status", "completed"),
        ("plan_sha256", "bad"),
        ("slot_sha256", "bad"),
        ("parent_pid", -1),
    ],
)
def test_worker_independent_reservation_recheck(worker_lineage, field, value):
    output, r = worker_lineage
    r[field] = value
    ctl.atomic(output / "pilot_preflight-reservation.json", r)
    with pytest.raises(ValueError):
        worker.verify_worker("pilot_preflight", "one")
    assert not (output / "pilot_preflight").exists()


def test_worker_launch_recheck_stops_before_reader(
    tmp_path, monkeypatch, config, profile
):
    # Original monitor, mocked probe/reader; passing supervisor does not grant data.
    monkeypatch.setattr(ctl, "ROOT", tmp_path)
    ctl.exclusive(tmp_path / ctl.PLAN, {})
    ctl.exclusive(tmp_path / ctl.ACCEPTANCE, {})
    monkeypatch.setattr(
        worker, "verify_worker", lambda *a: {"started_monotonic": time.monotonic()}
    )
    (tmp_path / ctl.OUTPUT).mkdir()
    bad = {
        **host.parse_vm_stat(
            "page size of 16384 bytes\nPages free: 1.\nPages inactive: 0.\n"
        ),
        "peak_rss_bytes": 1,
        "native_heap_reserved_bytes": 1,
        "native_heap_in_use_bytes": 1,
        "available_method": "Darwin_free_plus_inactive_pages",
        "workspace_method": "all_malloc_zone_reserved_bytes_conservative_upper_bound",
    }
    fake = SimpleNamespace(
        StudyAudit=old.StudyAudit,
        PolicyMonitor=lambda c, p, **kw: resources.PolicyMonitor(
            c, p, probe=lambda: bad, monitor_background=False
        ),
        bg=SimpleNamespace(verify_acceptance=lambda *a: None),
        reader_measurement=lambda *a: pytest.fail("Reader opened after failed launch"),
    )
    monkeypatch.setattr(worker, "runtime", lambda: (fake, config, profile, 0))
    assert worker.real_worker("dev_reader", "one") == 1
    audit = ctl.read(tmp_path / ctl.OUTPUT / "dev_reader/access-audit.json")
    assert audit["custody_access"] == [] and audit["population_access"] == []
    assert audit["optimizer_steps_started"] == 0


def test_bounded_parent_owns_timeout_only(tmp_path):
    with pytest.raises(TimeoutError):
        ctl.dispatch(
            [sys.executable, "-c", "import time;time.sleep(10)"],
            tmp_path / "own.log",
            0.05,
        )
    assert (tmp_path / "own.log").exists()


def test_diagnostic_excludes_training_store_calls():
    import ast

    tree = ast.parse(
        (ctl.ROOT / "src/latenttrigger/supervision/particle_worker.py").read_text()
    )
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in (
            "runtime",
            "diagnostic_parent",
            "diagnostic_child",
        ):
            names = {
                n.func.attr
                for n in ast.walk(node)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            }
            assert not names & {
                "run_study",
                "run_dev",
                "open_store",
                "ProcessedStore",
                "ParticleSetAutoencoder",
                "adam",
                "score",
                "step",
            }


def test_controller_limits_no_hidden_override():
    assert ctl.LIMITS_SECONDS == dict(
        zip(ctl.PHASES, (30, 60, 300, 30, 300), strict=True)
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "latenttrigger.supervision.particle_launcher",
            "--run-once",
            "--force",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2


@pytest.mark.parametrize("admitted", [False, True])
def test_one_diagnostic_fixed_order_conditional_slot(tmp_path, monkeypatch, admitted):
    monkeypatch.setattr(ctl, "ROOT", tmp_path)
    monkeypatch.setattr(ctl, "assert_lightweight", lambda: None)
    monkeypatch.setattr(ctl, "verify_plan", lambda: None)
    ctl.exclusive(tmp_path / ctl.PLAN, {})
    ctl.exclusive(tmp_path / ctl.ACCEPTANCE, {})
    monkeypatch.setattr(
        host,
        "host_context_once",
        lambda: {"pressure": {"pressure_dispatch_flags": None}},
    )
    calls = []

    def dispatch(command, log, seconds, **kw):
        calls.append(command[-1])
        ctl.atomic(
            log.parent / "result.json",
            {
                "configuration": command[-1],
                "status": "completed",
                "worker_observations_all_pass": admitted,
            },
        )
        return {"returncode": 0, "elapsed_seconds_including_imports": 5}

    monkeypatch.setattr(ctl, "dispatch", dispatch)
    runs = []
    monkeypatch.setattr(
        ctl, "run_study", lambda: runs.append("single") or {"status": "pending"}
    )
    result = ctl.experiment()
    assert calls == list(ctl.CONFIGURATIONS)
    assert runs == (["single"] if admitted else [])
    assert result["study_invoked"] is admitted
    with pytest.raises(FileExistsError):
        ctl.experiment()
    assert len(runs) == int(admitted)
    assert not (
        tmp_path / ctl.SLOT
    ).exists()  # mock; real invocation exclusively reserves


@pytest.fixture
def fake_acceptance(tmp_path):
    path = tmp_path / ctl.ACCEPTANCE
    path.parent.mkdir(parents=True)
    for suffix in (".pytest.log", ".pytest.xml"):
        path.with_suffix(suffix).write_text("synthetic evidence")
    evidence = {
        "pytest_exit_code": 0,
        "pytest_passed": 1,
        "pytest_cases": 1,
        "config_sha256": ctl.CONFIG_HASH,
        "source_sha256": ctl.source_hashes(tmp_path),
        "pytest_log_sha256": ctl.file_hash(path.with_suffix(".pytest.log")),
        "pytest_xml_sha256": ctl.file_hash(path.with_suffix(".pytest.xml")),
        "workspace_measurement": {
            "parameter_count": 478,
            "synthetic_optimizer_steps": 2,
            "peak_tensor_bytes": 5228448,
        },
    }
    ctl.exclusive(path, evidence)
    return tmp_path, evidence


@pytest.mark.parametrize(
    "field,value",
    [
        ("pytest_exit_code", 1),
        ("pytest_cases", 2),
        ("config_sha256", "changed"),
        ("source_sha256", {"foreign": "hash"}),
    ],
)
def test_stale_or_wrong_source_acceptance_refused(fake_acceptance, field, value):
    root, evidence = fake_acceptance
    evidence[field] = value
    ctl.atomic(root / ctl.ACCEPTANCE, evidence)
    with pytest.raises(ValueError):
        ctl.verify_acceptance(root)


def test_actual_acceptance_logs_independently_bound(fake_acceptance):
    root, evidence = fake_acceptance
    assert ctl.verify_acceptance(root) == evidence
    (root / ctl.ACCEPTANCE).with_suffix(".pytest.log").write_text("changed")
    with pytest.raises(ValueError):
        ctl.verify_acceptance(root)


def test_tampered_config_profile_prompt_block_before_reservation(tmp_path, monkeypatch):
    for rel in (ctl.CONFIG, ctl.DESIGN, ctl.PROFILE, ctl.PROMPT):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ctl.ROOT / rel).read_bytes())
    monkeypatch.setattr(ctl, "verify_prior", lambda r: None)
    monkeypatch.setattr(ctl, "verify_acceptance", lambda r: {"synthetic": True})
    assert ctl.verify_inputs(tmp_path) == {"synthetic": True}
    profile = ctl.read(tmp_path / ctl.PROFILE)
    profile["limits"]["minimum_system_available_bytes_at_launch"] -= 1
    ctl.atomic(tmp_path / ctl.PROFILE, profile)
    with pytest.raises(ValueError):
        ctl.verify_inputs(tmp_path)
    assert not (tmp_path / ctl.SLOT).exists()


def test_parent_bounded_stdout(tmp_path):
    with pytest.raises(RuntimeError, match="log"):
        ctl.dispatch(
            [sys.executable, "-c", "print('x'*1100000)"], tmp_path / "own.log", 5
        )


def test_worker_bootstrap_import_exception_audited(tmp_path, monkeypatch):
    monkeypatch.setattr(ctl, "ROOT", tmp_path)
    ctl.exclusive(tmp_path / ctl.PLAN, {})
    ctl.exclusive(tmp_path / ctl.ACCEPTANCE, {})
    (tmp_path / ctl.OUTPUT).mkdir()
    monkeypatch.setattr(
        worker, "verify_worker", lambda *a: {"started_monotonic": time.monotonic()}
    )
    monkeypatch.setattr(
        worker,
        "runtime",
        lambda: (_ for _ in ()).throw(ImportError("synthetic import failure")),
    )
    assert worker.real_worker("pilot_preflight", "one") == 1
    record = ctl.read(tmp_path / ctl.OUTPUT / "pilot_preflight/stage-result.json")
    assert record["optimizer_steps_started"] == 0 and record["resources"] is None
    assert "synthetic import failure" in record["error"]
    assert (tmp_path / ctl.OUTPUT / "pilot_preflight/bootstrap-audit.json").exists()
