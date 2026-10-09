"""Data-free forced CPU software footprint; never queries MPS availability."""

import os
import sys
import time

from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.cpu_mps_device import DeviceAccounting, DeviceGuard


def main():
    expected = dict.fromkeys(
        (
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        ),
        "1",
    )
    if any(os.environ.get(k) != v for k, v in expected.items()):
        raise ValueError("CPU smoke thread settings must precede imports.")
    guard = DeviceGuard(time.monotonic() + 28, accounting=DeviceAccounting())
    limiter = None
    try:
        guard.__enter__()
        import numpy as np
        import torch

        from latenttrigger.benchmarks import core
        from latenttrigger.benchmarks import cpu_mps_numerics as n
        from latenttrigger.benchmarks.cpu_mps_worker import audit
        from latenttrigger.data.inspection import AGGREGATE_NAMES
        from latenttrigger.models.autoencoder import CompactAutoencoder

        limiter, threads = core.configure_threads(
            dict(runtime=dict(thread_environment_before_imports=expected))
        )
        model = CompactAutoencoder().eval()
        with torch.no_grad():
            for parameter in model.parameters():
                parameter.fill_(0.03125)
        values = np.ones((1024, 8), dtype=np.float32)
        thresholds = np.array([1, 2, 3, 4], dtype=np.float64)
        counts = audit()
        windows = {
            b: n.build_windows(model, values, b, "cpu", counts)
            for b in (1, 8, 32, 128, 1024)
        }
        result = n.verify(
            model,
            model,
            values,
            thresholds,
            AGGREGATE_NAMES,
            windows,
            "cpu",
            guard,
            counts,
        )
        if result["mismatch_counts"] != [0] * 4:
            raise ValueError("CPU software fixture failed.")
        guard.check()
    finally:
        try:
            if limiter:
                limiter.restore_original_limits()
        finally:
            guard.close()
    if guard.error:
        raise RuntimeError(guard.error)
    print("CPU software smoke passed; MPS availability was not queried.")
    print(
        __import__("json").dumps(
            dict(
                runtime=p.runtime_versions(),
                threads=threads,
                counts=counts,
                resources=guard.report(),
            ),
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
