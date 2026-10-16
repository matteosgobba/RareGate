"""Guarded data-free ONNX/CPU fixture footprint; no frozen model or MPS check."""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

from raregate.benchmarks.guard import Guard


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
        raise ValueError("Smoke thread environment before imports required.")
    started = time.monotonic()
    guard = Guard(started + 28)
    limiter = runtime = diagnostic = None
    try:
        guard.__enter__()
        import numpy as np
        import torch

        from raregate.benchmarks import core
        from raregate.benchmarks.ae_parity_numerics import families
        from raregate.data.inspection import AGGREGATE_NAMES
        from raregate.exports import onnx_graph as graph
        from raregate.exports import onnx_numerics as n
        from raregate.exports.onnx_worker import counts
        from raregate.models.autoencoder import CompactAutoencoder

        limiter, threads = core.configure_threads(
            dict(runtime=dict(thread_environment_before_imports=expected))
        )
        model = CompactAutoencoder().eval()
        with torch.no_grad():
            for i, parameter in enumerate(model.parameters()):
                parameter.copy_(
                    (
                        torch.arange(parameter.numel(), dtype=torch.float32).reshape(
                            parameter.shape
                        )
                        + i
                        + 1
                    )
                    / 256
                )
        with tempfile.TemporaryDirectory(prefix="task0024-smoke-") as raw:
            directory = Path(raw)
            path = directory / "synthetic.onnx"
            graph.export_reconstruction(model, path)
            on = graph.optional_modules()["onnx"]
            manifest, inferred = graph.audit_graph(
                on.load(path, load_external_data=False), model
            )
            graph.diagnostic_copy(inferred, manifest, directory / "diagnostic.onnx")
            runtime = graph.RuntimeAdapter(path, feature_names=AGGREGATE_NAMES)
            diagnostic = graph.RuntimeAdapter(
                directory / "diagnostic.onnx",
                feature_names=AGGREGATE_NAMES,
                diagnostic=True,
            )
            result = n.verify(
                model,
                runtime,
                diagnostic,
                manifest,
                families()["constants"],
                np.array([1.0, 2.0, 3.0, 4.0]),
                AGGREGATE_NAMES,
                guard,
                counts(),
            )
            if result["status"] != "passed":
                raise ValueError("Synthetic fixture equivalence failed.")
            runtime.close()
            diagnostic.close()
            runtime = diagnostic = None
    finally:
        try:
            if runtime:
                runtime.close()
            if diagnostic:
                diagnostic.close()
            if limiter:
                limiter.restore_original_limits()
        finally:
            guard.close()
    if guard.error:
        raise RuntimeError(guard.error)
    print(
        json.dumps(
            dict(
                status="passed",
                wall_seconds=time.monotonic() - started,
                resources=guard.report(),
                effective_threads=threads,
                synthetic_windows=result["windows_verified"],
                MPS_check_performed=False,
                real_input_read=False,
            ),
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
