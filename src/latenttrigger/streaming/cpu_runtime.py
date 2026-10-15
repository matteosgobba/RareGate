"""0055 shared actual CPU bootstrap; returns before a payload-not-armed boundary."""

import hashlib
import importlib
import json
import os
import traceback
from dataclasses import dataclass

from .protocol import require
from .supervision import own_rss

ENVIRONMENT = {
    name: "1"
    for name in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "BLOSC_NTHREADS",
    )
}
EXPECTED_BUILD = "6d6fa299a6d76bc6add8bfff4916da33cbc1636da24e90df594e6434f918b26c"


@dataclass(frozen=True)
class RuntimePolicy:
    expected_build_sha256: str = EXPECTED_BUILD
    device: str = "cpu"
    intra: int = 1
    inter: int = 1
    deterministic: bool = True

    def validate(self):
        require(
            self == RuntimePolicy(),
            "Frozen CPU runtime policy; no selector/alternate build",
        )
        return self


RUNTIME_POLICY = RuntimePolicy()


def canonical_build_hash(text):
    return hashlib.sha256(
        json.dumps(
            text, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


class InitializationFailure(ValueError):
    def __init__(self, evidence):
        super().__init__(evidence["primary_failure"]["message"])
        self.evidence = evidence


def exception_record(exc):
    return dict(
        type=type(exc).__name__,
        message=str(exc)[:700],
        frames=[
            dict(file=x.filename, line=x.lineno, function=x.name)
            for x in traceback.extract_tb(exc.__traceback__, limit=8)
        ],
    )


class RuntimeSession:
    def __init__(
        self,
        policy=RUNTIME_POLICY,
        *,
        publish=lambda _: None,
        clock=None,
        import_module=importlib.import_module,
    ):
        from .supervision import Clocks

        self.policy = policy.validate()
        self.clock = clock or Clocks().continuous
        self.publish = publish
        self.import_module = import_module
        self.limiter = None
        self.core = self.np = None
        self.evidence = dict(
            payload_armed=False,
            boundary="runtime_start",
            steps=[],
            primary_failure=None,
            report_failure=None,
            cleanup_failures=[],
            build=None,
            thread_environment=dict(ENVIRONMENT),
            generated_helper_arithmetic="no explicit forward/score; library import/configuration activity only",
        )

    def checkpoint(self, step):
        self.evidence["last_step"] = step
        self.evidence["last_monotonic_ns"] = self.clock()
        self.evidence["own_lifetime_peak_RSS_bytes"] = own_rss()
        from .resources import query_pid

        self.evidence["own_current_RSS_observation"] = query_pid(os.getpid())
        self.evidence["steps"].append(
            dict(
                step=step, monotonic_ns=self.clock(), lifetime_peak_RSS_bytes=own_rss()
            )
        )
        require(len(self.evidence["steps"]) <= 24, "Bounded runtime steps")
        try:
            self.publish(self.evidence)
        except (OSError, ValueError) as exc:
            self.evidence["report_failure"] = exception_record(exc)
            raise

    def initialize(self):
        try:
            self.checkpoint("thread_environment_before_imports")
            for key, value in ENVIRONMENT.items():
                os.environ[key] = value
            self.checkpoint("import_numpy")
            self.np = self.import_module("numpy")
            self.checkpoint("import_torch")
            torch = self.import_module("torch")
            self.checkpoint("import_unchanged_CPU_helpers")
            self.core = self.import_module("latenttrigger.benchmarks.core")
            self.checkpoint("configure_and_query_threads")
            self.limiter, threads = self.core.configure_threads(
                dict(
                    runtime=dict(
                        thread_environment_before_imports={
                            k: v
                            for k, v in ENVIRONMENT.items()
                            if k != "BLOSC_NTHREADS"
                        }
                    )
                )
            )
            self.evidence["threads"] = threads
            self.checkpoint("canonical_build_identity")
            text = torch.__config__.show()
            self.evidence["build"] = dict(
                expected_canonical_sha256=self.policy.expected_build_sha256,
                actual_canonical_sha256=canonical_build_hash(text),
                raw_text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                method="SHA256(canonical JSON string representation)",
                torch_version=str(torch.__version__),
                numpy_version=self.np.__version__,
            )
            require(
                self.evidence["build"]["actual_canonical_sha256"]
                == self.policy.expected_build_sha256,
                "Unsupported actual Torch build identity",
            )
            self.checkpoint("rounding_mode")
            import ctypes

            mode = ctypes.CDLL(None).fegetround()
            self.evidence["rounding_mode"] = mode
            require(mode == 0, "Supported round-to-nearest mode required")
            self.checkpoint("import_HDF_bindings_plugins_without_open")
            hdf = self.import_module("h5py")
            plugin = self.import_module("hdf5plugin")
            self.evidence["HDF_libraries"] = dict(
                h5py=hdf.__version__,
                HDF5=hdf.version.hdf5_version,
                plugin_version=getattr(plugin, "__version__", None),
                files_opened=0,
                decoder_effective_threads="unknown",
            )
            self.checkpoint("final_effective_thread_query")
            self.evidence["threads_after"] = self.core.effective_threads()
            self.evidence["boundary"] = "payload_not_armed"
            self.checkpoint("payload_not_armed")
            return self
        except BaseException as exc:
            self.evidence["primary_failure"] = exception_record(exc)
            self.evidence["own_lifetime_peak_RSS_bytes"] = own_rss()
            from .resources import query_pid

            self.evidence["own_current_RSS_observation"] = query_pid(os.getpid())
            self.close()
            try:
                self.publish(self.evidence)
            except (OSError, ValueError) as report:
                self.evidence["report_failure"] = exception_record(report)
            raise InitializationFailure(self.evidence) from exc

    def close(self):
        if not hasattr(self, "evidence"):
            self.evidence = dict(cleanup_failures=[])
        if getattr(self, "limiter", None) is not None:
            limiter, self.limiter = self.limiter, None
            try:
                limiter.restore_original_limits()
            except BaseException as exc:
                self.evidence["cleanup_failures"].append(exception_record(exc))
        self.evidence["limiter_owned"] = False
        self.evidence["thread_initialization_lifetime"] = (
            "fresh worker; Torch interop not reset/reinitialized; process exit retires runtime"
        )
        return not self.evidence["cleanup_failures"]
