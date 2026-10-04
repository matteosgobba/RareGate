"""Check PyTorch installation and a small computation on the selected device."""

import torch

from latenttrigger.utils.device import get_device


def main() -> None:
    """Report device availability and verify a deterministic tensor operation."""
    device = get_device()
    print(f"PyTorch version: {torch.__version__}")
    print(f"Selected device: {device}")
    print(f"MPS available: {torch.backends.mps.is_available()}")

    tensor = torch.arange(4, dtype=torch.float32).reshape(2, 2)
    tensor = tensor.to(device)
    result = (tensor * 2 + 1).sum()
    # Reading the scalar also waits for the device computation to finish.
    value = result.item()
    if value != 16.0:
        raise RuntimeError(f"Unexpected tensor result: {value}; expected 16.0")

    print(f"Tensor computation on {tensor.device}: {value}")
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
