"""PyTorch device selection for Apple Silicon and CPU environments."""

import torch


def get_device() -> torch.device:
    """Return an MPS device when available, otherwise a CPU device.

    Availability depends on the PyTorch build, operating system, and hardware.
    """
    return torch.device("mps" if torch.backends.mps.is_available() else "cpu")
