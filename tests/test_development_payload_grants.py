"""Parent permissions tested with owned text/HDF fixtures, never real sources."""

import os
import time

import pytest

from raregate.benchmarks import development_payload_protocol as p
from raregate.benchmarks import development_payload_provider as provider
from raregate.benchmarks.development_payload_native import (
    reserve,
    synthetic_prefix,
)


def owned_grant(tmp_path, monkeypatch, phase="repetition1"):
    root = tmp_path
    monkeypatch.setattr(p, "ROOT", root)
    monkeypatch.setattr(p, "source_map", lambda: {"synthetic.py": "a" * 64})
    monkeypatch.setattr(p, "dependencies", lambda: {"synthetic": "1"})
    monkeypatch.setattr(p, "native_build", lambda: {"synthetic.so": "b" * 64})
    (root / p.PROMPT).parent.mkdir(parents=True)
    (root / p.PROMPT).write_text("synthetic authorization")
    base = root / p.VALIDATION / "run"
    directory = base / phase
    directory.mkdir(parents=True)
    plan = dict(
        source_map=p.source_map(),
        dependencies=p.dependencies(),
        native_build=p.native_build(),
        prompt_sha256=p.file_hash(root / p.PROMPT),
    )
    p.durable_json(base / "plan.json", plan)
    grant = dict(
        parent_pid=os.getppid(),
        token="c" * 32,
        phase=phase,
        synthetic_only=True,
        operation_deadline=time.monotonic() + 1000,
        plan_sha256=p.file_hash(base / "plan.json"),
        source_map=plan["source_map"],
        dependencies=plan["dependencies"],
        payload_path=str(directory / "fixture.h5"),
        prefix_sha256=synthetic_prefix(),
    )
    p.durable_json(directory / "grant.json", grant)
    return directory, grant


def test_claim_once(tmp_path, monkeypatch):
    directory, grant = owned_grant(tmp_path, monkeypatch)
    _, permit = p.validate_grant(directory, grant["token"], time.monotonic)
    assert permit.pid == os.getpid()
    with pytest.raises(FileExistsError):
        p.validate_grant(directory, grant["token"], time.monotonic)


@pytest.mark.parametrize(
    "field,value",
    [
        ("parent_pid", -1),
        ("token", "x" * 32),
        ("phase", "selection"),
        ("synthetic_only", False),
        ("operation_deadline", 0),
        ("plan_sha256", "0" * 64),
        ("source_map", {}),
        ("dependencies", {}),
    ],
)
def test_foreign_stale_changed_grant(tmp_path, monkeypatch, field, value):
    directory, grant = owned_grant(tmp_path, monkeypatch)
    changed = dict(grant)
    changed[field] = value
    p.durable_json(directory / "grant.json", changed)
    with pytest.raises((ValueError, FileNotFoundError)):
        p.validate_grant(directory, grant["token"], time.monotonic)
    assert not (directory / "claim.json").exists()


def test_cannot_create_bypass_permit():
    with pytest.raises(ValueError):
        p.PayloadPermit({}, object())


def test_no_duplicate_reservation(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "ROOT", tmp_path)
    base = tmp_path / p.OUTPUT / "run"
    base.mkdir(parents=True)
    plan = {"prompt_sha256": "a" * 64}
    p.durable_json(base / "plan.json", plan)
    reserve(base, plan)
    with pytest.raises(FileExistsError):
        reserve(base, plan)


@pytest.mark.parametrize(
    "key",
    [
        "task",
        "model_execution_authorized",
        "limits",
        "design",
        "raw",
        "membership",
        "cache",
    ],
)
def test_fixed_config_rejects_changes(tmp_path, key):
    spec = p.load()
    spec[key] = None
    path = tmp_path / p.CONFIG
    path.parent.mkdir(parents=True)
    p.durable_json(path, spec)
    with pytest.raises(ValueError, match="Fixed payload"):
        p.load(tmp_path)


def test_historical_permission_false():
    assert p.old.load()["future_measurement_execution_authorized"] is False
    assert p.load()["design"]["counts"] == p.old.load()["future"]["counts"]
    assert provider.validate_grant is p.validate_grant
