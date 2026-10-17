"""Verify the diagnostic's executable entry point on CPU-only runners."""

import runpy
from pathlib import Path

import pytest
import torch


def test_smoke_test_on_cpu(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The diagnostic runs and reports CPU fallback with MPS unavailable."""
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)
    script = Path(__file__).resolve().parents[2] / "scripts" / "smoke_test.py"

    runpy.run_path(str(script), run_name="__main__")

    output = capsys.readouterr().out
    assert f"PyTorch version: {torch.__version__}" in output
    assert "Selected device: cpu" in output
    assert "MPS available: False" in output
    assert "Smoke test passed." in output
