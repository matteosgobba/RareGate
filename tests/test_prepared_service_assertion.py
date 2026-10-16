"""Synthetic controller assertion failures cannot reserve/access real inputs."""

from contextlib import nullcontext

import pytest

from raregate.benchmarks import prepared_service_native as native
from raregate.benchmarks import prepared_service_protocol as p
from raregate.benchmarks import prepared_service_runtime as rt


@pytest.mark.parametrize("failure", ("setup", "loss", "release"))
def test_assertion_failure_and_release_preserved(tmp_path, monkeypatch, failure):
    spec = p.load()

    class Clock:
        def __call__(self):
            return 1.0

        def snapshot(self):
            return dict(continuous=1.0)

    class Assertion:
        identity = "synthetic"

        def __init__(self, clock):
            self.evidence = dict(released=False)

        def start(self, deadline):
            if failure in ("setup", "release"):
                raise rt.GuardError("setup failure")

        def check(self, deadline, force=False):
            raise rt.GuardError("owned assertion lost")

        def release(self, deadline):
            if failure == "release":
                raise rt.GuardError("release unverified")
            self.evidence["released"] = True
            return self.evidence

    calls = []

    def supervise(*args, **kwargs):
        calls.append("probe")
        kwargs["monitor"]()
        pytest.fail("lost assertion cannot continue")

    monkeypatch.setattr(p, "ROOT", tmp_path)
    monkeypatch.setattr(p, "load", lambda: spec)
    monkeypatch.setattr(p, "source_map", lambda: {})
    monkeypatch.setattr(p, "dependencies", lambda: {})
    monkeypatch.setattr(rt, "ContinuousClock", Clock)
    monkeypatch.setattr(rt, "alarm", lambda *a: nullcontext())
    monkeypatch.setattr(rt, "parent_check", lambda **k: 1)
    monkeypatch.setattr(rt, "IdleAssertion", Assertion)
    monkeypatch.setattr(rt, "supervise", supervise)
    directory, result = native.run(synthetic_directory=tmp_path / "native-fixture")
    assert result["status"] == "failed_before_operational_reservation"
    assert result["reserved"] is False
    assert not (tmp_path / p.OUTPUT / "attempt.json").exists()
    assert not (directory / "parent-acceptance.json").exists()
    if failure == "release":
        assert "release_error" in result["sleep_assertion"]
    else:
        assert result["sleep_assertion"]["released"]
    assert calls == (["probe"] if failure == "loss" else [])
