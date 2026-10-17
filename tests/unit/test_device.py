"""Exercise device selection without requiring an Apple GPU."""

import pytest
import torch

from raregate.utils.device import get_device


@pytest.mark.parametrize(
    ("mps_available", "expected_device"),
    [(True, "mps"), (False, "cpu")],
)
def test_get_device(
    monkeypatch: pytest.MonkeyPatch,
    mps_available: bool,
    expected_device: str,
) -> None:
    """MPS availability controls selection, independently of runner hardware."""
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: mps_available)

    assert get_device() == torch.device(expected_device)


def test_cpu_fallback_computes(monkeypatch: pytest.MonkeyPatch) -> None:
    """The fallback device supports an actual tensor computation."""
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)

    tensor = torch.tensor([1.0, 2.0, 3.0]).to(get_device())
    result = tensor.square()

    assert result.device.type == "cpu"
    torch.testing.assert_close(result, torch.tensor([1.0, 4.0, 9.0]))
