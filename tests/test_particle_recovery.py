"""Synthetic accounting, readiness, lineage and one-attempt recovery gates."""

import copy
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from latenttrigger.data.processed import content_hash
from latenttrigger.models import particle_background as bg
from latenttrigger.models import particle_recovery as recovery
from latenttrigger.training import particle_set as training


@pytest.fixture
def config():
    return json.loads((recovery.ROOT / recovery.CONFIG).read_text())


def reading(available=8 * 2**30):
    return {
        **training.parse_vm_stat(
            "Mach Virtual Memory Statistics: (page size of 16384 bytes)\n"
            f"Pages free: {available // 16384}.\nPages inactive: 0.\n"
        ),
        "peak_rss_bytes": 400 * 2**20,
        "native_heap_reserved_bytes": 200 * 2**20,
        "native_heap_in_use_bytes": 150 * 2**20,
        "available_method": "Darwin_free_plus_inactive_pages",
        "workspace_method": "all_malloc_zone_reserved_bytes_conservative_upper_bound",
    }


def sample(config, values, *, duration=0):
    tick = [0.0]
    iterator = iter(values)

    def sleep(seconds):
        tick[0] += seconds

    def probe():
        value = next(iterator)
        tick[0] += duration
        if isinstance(value, Exception):
            raise value
        return value

    return recovery.sample_preflight(
        config, probe=probe, clock=lambda: tick[0], sleep=sleep, context=lambda: {}
    )


def store_preflight(tmp_path, record):
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text("{}")
    record["acceptance_sha256"] = recovery.file_hash(acceptance)
    record["record_sha256"] = content_hash(record)
    path = tmp_path / "preflight.json"
    path.write_text(json.dumps(record))
    return path, acceptance


@pytest.mark.parametrize(
    "page,free,inactive", [(4096, 3, 2), (16384, 0, 524288), (16384, 0, 0)]
)
def test_exact_page_arithmetic(page, free, inactive):
    result = training.parse_vm_stat(
        f"page size of {page} bytes\nPages free: {free}.\nPages inactive: {inactive}.\n"
        "Pages occupied by compressor: 1000.\nSwapouts: 9999.\n"
    )
    assert result["available_bytes"] == page * (free + inactive)
    assert result["available_gib"] == page * (free + inactive) / 2**30
    assert result["context_counters_are_not_available_bytes"] is True


@pytest.mark.parametrize(
    "text",
    [
        "",
        "page size of 0 bytes\nPages free: 1.\nPages inactive: 2.\n",
        "page size of 16384 bytes\nPages free: -1.\nPages inactive: 2.\n",
        "page size of 16384 bytes\nPages free: 1.5\nPages inactive: 2.\n",
        "page size of 16384 bytes\nPages free: 1.\nPages free: 2.\nPages inactive: 2.\n",
        "page size of 16384 bytes\nPages free: 1.\n",
    ],
)
def test_malformed_page_accounting_fails_closed(text):
    with pytest.raises(training.ResourceLimitError):
        training.parse_vm_stat(text)


def test_equality_passes_all_original_limits(config):
    value = reading()
    value["peak_rss_bytes"] = 6 * 2**30
    value["native_heap_reserved_bytes"] = 512 * 2**20
    recovery.check_reading(value, config["resource_gate"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("available_bytes", 1),
        ("available_gib", 9),
        ("free_pages", -1),
        ("page_size_bytes", 0),
        ("peak_rss_bytes", None),
        ("native_heap_reserved_bytes", 0),
        ("native_heap_reserved_bytes", 512 * 2**20 + 1),
        ("peak_rss_bytes", 6 * 2**30 + 1),
        ("available_method", "compressed_plus_active"),
    ],
)
def test_invalid_or_exceeded_probe_rejected(config, field, value):
    data = reading()
    data[field] = value
    with pytest.raises(training.ResourceLimitError):
        recovery.check_reading(data, config["resource_gate"])


def test_three_stable_samples_and_no_store_or_allowance(config, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Preflight must not construct reader, optimizer or supervisor")

    monkeypatch.setattr(bg, "open_store", forbidden)
    monkeypatch.setattr(bg, "run_task", forbidden)
    monkeypatch.setattr(training, "adam", forbidden)
    record = sample(config, [reading()] * 3)
    assert record["ready"] and record["sample_span_seconds"] == 5
    assert [r["elapsed_seconds"] for r in record["readings"]] == [0, 2.5, 5]
    assert record["population_requests"] == record["real_optimizer_steps"] == 0
    path, acceptance = store_preflight(tmp_path, record)
    recovery.verify_preflight(path, config, acceptance)
    assert not (tmp_path / recovery.LEDGER).exists()


@pytest.mark.parametrize(
    "values",
    [
        [reading(), reading(7 * 2**30), reading()],
        [RuntimeError("probe unavailable"), reading(), reading()],
        [reading(3 * 2**30)] * 3,
    ],
)
def test_every_sample_retained_no_favorable_selection(config, tmp_path, values):
    record = sample(config, values)
    assert not record["ready"] and len(record["readings"]) == 3
    path, acceptance = store_preflight(tmp_path, record)
    with pytest.raises(ValueError, match="failed"):
        recovery.verify_preflight(path, config, acceptance)


def test_over_30_seconds_not_ready(config):
    record = sample(config, [reading()] * 3, duration=11)
    assert record["elapsed_seconds"] > 30 and not record["ready"]


@pytest.mark.parametrize(
    "mutation", ["digest", "acceptance", "span", "false_pass", "count"]
)
def test_readiness_cannot_be_relabelled_or_reused_stale(config, tmp_path, mutation):
    record = sample(config, [reading()] * 3)
    if mutation == "span":
        record["readings"][-1]["elapsed_seconds"] = 4.9
    elif mutation == "false_pass":
        record["readings"][1]["sample"] = reading(7 * 2**30)
    elif mutation == "count":
        record["real_events"] = 1
    path, acceptance = store_preflight(tmp_path, record)
    if mutation == "digest":
        path.write_text(path.read_text().replace('"ready": true', '"ready": false'))
    if mutation == "acceptance":
        acceptance.write_text('{"changed":true}')
    with pytest.raises((ValueError, training.ResourceLimitError)):
        recovery.verify_preflight(path, config, acceptance)


def predecessor_fixture(tmp_path, config):
    originals = {}
    values = {
        "results/tables/final/task0010-particle-set-gate-summary.json": {
            "executable_config_scientific_sha256": content_hash(config),
            "dev_gate": {
                k: 0
                for k in (
                    "unique_real_events",
                    "population_requests",
                    "optimizer_steps",
                    "passes_completed",
                )
            },
        },
        "data/baselines/compact-particle-set-autoencoder-v1/dev/access-audit.json": {
            "population_access": [],
            "test_background_model_access": False,
            "test_signal_model_access": False,
        },
        "data/baselines/compact-particle-set-autoencoder-v1/workflow.json": {
            "config_sha256": content_hash(config),
            "stages": [
                {
                    "stage": "dev",
                    "status": "failed_or_interrupted",
                    "error": "Launch available memory below 8 GiB.",
                }
            ],
        },
    }
    for rel in recovery.PREDECESSOR:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(values.get(rel, {})))
        originals[rel] = recovery.file_hash(target)
    return originals


@pytest.mark.parametrize("problem", ["hash", "consumption", "config", "audit"])
def test_wrong_predecessor_or_nonzero_consumption_refused(config, tmp_path, problem):
    evidence = predecessor_fixture(tmp_path, config)
    rel = "results/tables/final/task0010-particle-set-gate-summary.json"
    path = tmp_path / rel
    summary = json.loads(path.read_text())
    if problem == "consumption":
        summary["dev_gate"]["optimizer_steps"] = 1
    elif problem == "config":
        summary["executable_config_scientific_sha256"] = "bad"
    elif problem == "audit":
        rel = "data/baselines/compact-particle-set-autoencoder-v1/dev/access-audit.json"
        path = tmp_path / rel
        summary = json.loads(path.read_text())
        summary["population_access"] = [{"events_read": 0}]
    else:
        summary["extra"] = True
    path.write_text(json.dumps(summary))
    if problem != "hash":
        evidence[rel] = recovery.file_hash(path)
    with pytest.raises(ValueError):
        recovery.verify_predecessor(
            config, root=tmp_path, evidence=evidence, protected={}
        )


def test_preserved_original_and_exact_unchanged_contract(config):
    for rel, digest in recovery.PROTECTED.items():
        assert recovery.file_hash(recovery.ROOT / rel) == digest
    assert config["architecture"]["parameter_count"] == 478
    assert (
        content_hash(config)
        == "48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b"
    )


def test_valid_zero_consumption_predecessor(config, tmp_path):
    evidence = predecessor_fixture(tmp_path, config)
    assert (
        recovery.verify_predecessor(
            config, root=tmp_path, evidence=evidence, protected={}
        )
        == evidence
    )


def test_failed_preflight_never_prepares_or_reserves(config, tmp_path, monkeypatch):
    monkeypatch.setattr(recovery, "ROOT", tmp_path)
    monkeypatch.setattr(recovery, "verify_predecessor", lambda *a, **k: {})
    monkeypatch.setattr(bg, "verify_acceptance", lambda *a: {})
    path, acceptance = store_preflight(
        tmp_path, sample(config, [reading(7 * 2**30)] * 3)
    )
    with pytest.raises(ValueError):
        recovery.recover(acceptance, path, config)
    assert not (tmp_path / recovery.PLAN).exists()
    assert not (tmp_path / recovery.LEDGER).exists()


def test_current_source_acceptance_required_before_reservation(
    config, tmp_path, monkeypatch
):
    monkeypatch.setattr(recovery, "ROOT", tmp_path)
    monkeypatch.setattr(recovery, "verify_predecessor", lambda *a, **k: {})
    path, acceptance = store_preflight(tmp_path, sample(config, [reading()] * 3))
    with pytest.raises(ValueError):
        recovery.recover(acceptance, path, config)
    assert not (tmp_path / recovery.LEDGER).exists()


def test_one_fixed_recovery_plan_and_atomic_ledger(config, tmp_path, monkeypatch):
    original_prompt = (recovery.ROOT / recovery.PROMPT).read_bytes()
    with pytest.raises(TypeError):
        recovery.recover(None, None, config, root=tmp_path)
    monkeypatch.setattr(recovery, "ROOT", tmp_path)
    monkeypatch.setattr(
        recovery, "verify_predecessor", lambda *a, **k: {"prior": "identity"}
    )
    monkeypatch.setattr(bg, "verify_acceptance", lambda *a: {})
    prompt = tmp_path / recovery.PROMPT
    prompt.parent.mkdir(parents=True)
    prompt.write_bytes(original_prompt)
    path, acceptance = store_preflight(tmp_path, sample(config, [reading()] * 3))
    calls = []

    def dispatch(args, conf, **kwargs):
        calls.append(args.output)
        recovery.exclusive_json(
            kwargs["attempt_budget"],
            {"reserved": True, **kwargs["engineering_lineage"]},
        )
        return {"status": "implementation_complete_canonical_pending"}

    monkeypatch.setattr(bg, "run_task", dispatch)
    recovery.recover(acceptance, path, config)
    ledger_bytes = (tmp_path / recovery.LEDGER).read_bytes()
    with pytest.raises(FileExistsError):
        recovery.recover(acceptance, path, config)
    assert calls == [tmp_path / recovery.OUTPUT]
    assert (tmp_path / recovery.LEDGER).read_bytes() == ledger_bytes
    plan = json.loads((tmp_path / recovery.PLAN).read_text())
    assert plan["remaining_resource_contract"] == config["resource_gate"]
    assert plan["prior_real_optimizer_steps"] == 0


def test_original_entry_refuses_consumed_ledger_without_modification(
    config, tmp_path, monkeypatch
):
    monkeypatch.setattr(bg, "ROOT", tmp_path)
    monkeypatch.setattr(bg, "verify_acceptance", lambda *a: {})
    ledger = tmp_path / "data/baselines/task0010-particle-attempt-budget.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("original reservation")
    args = SimpleNamespace(acceptance=None, output=tmp_path / "changed-directory")
    with pytest.raises(FileExistsError):
        bg.run_task(args, config)
    assert ledger.read_text() == "original reservation"
    assert not args.output.exists()


def test_new_worker_rechecks_launch_after_successful_preflight(
    config, tmp_path, monkeypatch
):
    assert sample(config, [reading()] * 3)["ready"]
    monkeypatch.setattr(bg.torch, "set_num_interop_threads", lambda _: None)
    monkeypatch.setattr(
        bg,
        "ResourceMonitor",
        lambda limits: training.ResourceMonitor(
            limits, probe=lambda: reading(7 * 2**30), monitor_background=False
        ),
    )
    monkeypatch.setattr(bg, "run_dev", lambda *a: pytest.fail("Reader stage forbidden"))
    args = SimpleNamespace(
        output=tmp_path / "dev", worker="dev", stage_started=None, stage_budget=300
    )
    assert bg.worker(args, config) == 1
    audit = json.loads((args.output / "access-audit.json").read_text())
    assert audit["population_access"] == []
    result = json.loads((args.output / "stage-result.json").read_text())
    assert result["error"] == "Launch available memory below 8 GiB."
    assert result["downstream_authorized"] is False


@pytest.mark.parametrize("problem", ["exception", "timeout"])
def test_supervisor_preserves_reservation_and_blocks_later_stages(
    config, tmp_path, monkeypatch, problem
):
    monkeypatch.setattr(bg, "verify_acceptance", lambda *a: {})
    calls = []

    class Child:
        def __init__(self, command, **kwargs):
            calls.append(command)
            directory = Path(command[command.index("--output") + 1])
            directory.mkdir()
            bg.Audit(directory / "access-audit.json").save()
            if problem == "exception":
                raise OSError("controlled dispatch failure")

        def wait(self, timeout=None):
            if len(calls) == 1 and not getattr(self, "terminated", False):
                raise subprocess.TimeoutExpired("synthetic", timeout)

        def terminate(self):
            self.terminated = True

    monkeypatch.setattr(bg.subprocess, "Popen", Child)
    args = SimpleNamespace(
        acceptance=None,
        output=tmp_path / "workflow",
        config=tmp_path / "config",
        store=tmp_path / "full",
        dev_store=tmp_path / "dev",
    )
    ledger = tmp_path / "exclusive-ledger.json"
    state = bg.run_task(
        args, config, attempt_budget=ledger, engineering_lineage={"task": "0011"}
    )
    assert ledger.exists() and len(calls) == 1
    assert state["status"] == "implementation_complete_canonical_pending"
    assert (
        json.loads((args.output / "dev/access-audit.json").read_text())[
            "population_access"
        ]
        == []
    )
    with pytest.raises(FileExistsError):
        bg.run_task(args, config, attempt_budget=ledger)


def test_test_and_calibration_guards_unchanged():
    for role in ("test_background", "test_signal", "validation_calibration_background"):
        with pytest.raises(ValueError):
            bg.require_role(role, "dev")


def test_context_unavailable_is_reported_not_counted(monkeypatch):
    monkeypatch.setattr(
        recovery.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=1, stdout="", stderr="permission restricted"
        ),
    )
    context = recovery.host_context()
    assert context["current_swap_use"]["status"] == "unavailable"
    assert "cumulative" in context["interpretation"]
    assert "available_bytes" not in context


def test_preflight_copy_does_not_mutate_model_config(config):
    original = copy.deepcopy(config)
    sample(config, [reading()] * 3)
    assert config == original


def test_preflight_timeout_preserves_earlier_readings_and_stops(config):
    record = sample(config, [reading(), recovery.PreflightTimeout("deadline")])
    assert len(record["readings"]) == 2 and not record["ready"]
    assert record["readings"][0]["passed"] is True
    assert record["readings"][1]["error"] == "deadline"
    assert record["attempt_reserved"] is False


@pytest.mark.parametrize("wrong", [False, True])
def test_worker_lineage_requires_fixed_plan_reservation_and_acceptance(
    config, tmp_path, monkeypatch, wrong
):
    monkeypatch.setattr(recovery, "ROOT", tmp_path)
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text("{}")
    plan = {
        "config_sha256": content_hash(config),
        "acceptance_sha256": recovery.file_hash(acceptance),
        "authorization_sha256": recovery.PROMPT_SHA256,
    }
    recovery.exclusive_json(tmp_path / recovery.PLAN, plan)
    lineage = {
        "task": "0011",
        "plan_sha256": recovery.file_hash(tmp_path / recovery.PLAN),
    }
    reservation = {
        "config_sha256": content_hash(config),
        "output": str(tmp_path / recovery.OUTPUT),
        "engineering_lineage": lineage,
    }
    if wrong:
        reservation["engineering_lineage"] = {"task": "other"}
    recovery.exclusive_json(tmp_path / recovery.LEDGER, reservation)
    args = SimpleNamespace(
        output=tmp_path / recovery.OUTPUT / "dev", acceptance=acceptance
    )
    if wrong:
        with pytest.raises(ValueError, match="lineage"):
            recovery.verify_worker_lineage(
                args, {"engineering_lineage": lineage}, config
            )
    else:
        recovery.verify_worker_lineage(args, {"engineering_lineage": lineage}, config)


def test_acceptance_generator_records_actual_failure_without_workspace(
    config, tmp_path, monkeypatch
):
    calls = []

    def suite(command, **kwargs):
        calls.append(command)
        xml = next(v.split("=", 1)[1] for v in command if v.startswith("--junitxml="))
        Path(xml).write_text(
            "<testsuites><testsuite><testcase/><testcase><failure/></testcase></testsuite></testsuites>"
        )
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr(recovery.subprocess, "run", suite)
    monkeypatch.setattr(
        recovery,
        "measure_tensor_workspace",
        lambda *a: pytest.fail("Failed suite cannot authorize workspace/run"),
    )
    path = tmp_path / "acceptance.json"
    with pytest.raises(ValueError, match="not verified"):
        recovery.renew_acceptance(path, config)
    evidence = json.loads(path.read_text())
    assert evidence["pytest_exit_code"] == 1 and evidence["pytest_passed"] == 1
    assert evidence["pytest_cases"] == 2 and evidence["workspace_measurement"] is None
    with pytest.raises(FileExistsError):
        recovery.renew_acceptance(path, config)
    assert len(calls) == 1
