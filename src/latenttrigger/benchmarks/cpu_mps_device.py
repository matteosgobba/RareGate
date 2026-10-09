"""Late-import device evidence, exact transfers and primary allocation caps."""

import os
import platform
import sys
import threading
import time

from latenttrigger.benchmarks import protocol as p
from latenttrigger.benchmarks.guard import Guard, GuardError


class DeviceAccounting:
    """Composed with unchanged host Guard; failed peaks are latched before veto."""

    def __init__(self):
        self.api = None
        self.status = "not_applicable"
        self.current_peak = self.driver_peak = None
        self.checks = 0
        self.last = None
        self.error = None
        self.lock = threading.RLock()

    def enable(self, api):
        if not all(
            callable(getattr(api, n, None))
            for n in (
                "synchronize",
                "current_allocated_memory",
                "driver_allocated_memory",
            )
        ):
            raise GuardError("Unavailable primary MPS accounting/completion API.")
        self.api, self.status = api, "active"
        self.current_peak = self.driver_peak = 0

    def sample(self):
        with self.lock:
            if self.error:
                raise GuardError(self.error)
            if self.api is None:
                return None
            tick = time.monotonic()
            try:
                current = self.api.current_allocated_memory()
                driver = self.api.driver_allocated_memory()
                self.checks += 1
                self.last = dict(
                    current_tensor_bytes=current,
                    driver_bytes=driver,
                    query_start=tick,
                    query_end=time.monotonic(),
                    method="torch.mps.primary_native_APIs",
                )
                if (
                    type(current) is not int
                    or type(driver) is not int
                    or current < 0
                    or driver < 0
                    or current > driver
                ):
                    raise GuardError("Malformed/unavailable primary device accounting.")
                self.current_peak = max(self.current_peak, current)
                self.driver_peak = max(self.driver_peak, driver)
                if current > 268435456 or driver > 536870912:
                    raise GuardError("MPS tensor/driver cap exceeded.")
                return self.last
            except Exception as exc:
                self.error = self.error or str(exc)
                raise GuardError(self.error) from exc

    def probe(self, host_probe):
        def combined():
            host = host_probe()
            # Host guard retains extra device samples in this accounting object.
            self.sample()
            return host

        return combined

    def report(self):
        return dict(
            status=self.status,
            tensor_peak_bytes=self.current_peak,
            driver_peak_bytes=self.driver_peak,
            samples=self.checks,
            last_sample=self.last,
            latched_error=self.error,
            metrics_overlap_host_unified_memory=True,
        )


class DeviceAdmissionError(ValueError):
    def __init__(self, message, evidence):
        super().__init__(message)
        self.evidence = evidence


def availability(torch, spec):
    api_files = {
        "torch.mps": p.file_hash(torch.mps.__file__),
        "torch.backends.mps": p.file_hash(torch.backends.mps.__file__),
    }
    expected_api = spec.get("runtime", {}).get("mps_python_api_file_sha256")
    if expected_api is not None and api_files != expected_api:
        raise DeviceAdmissionError(
            "Installed primary MPS API bytes changed.", api_files
        )
    built = torch.backends.mps.is_built()
    available = torch.backends.mps.is_available()
    if (
        type(built) is not bool
        or type(available) is not bool
        or (available and not built)
    ):
        raise DeviceAdmissionError(
            "Malformed build/availability relation.",
            dict(is_built=built, is_available=available),
        )
    build = torch.__config__.show()
    import hashlib

    result = dict(
        is_built=built,
        is_available=available,
        python_executable=sys.executable,
        python_version=sys.version,
        architecture=platform.machine(),
        os=platform.platform(),
        os_version=platform.mac_ver()[0],
        runtime_versions=p.runtime_versions(),
        torch_version=torch.__version__,
        torch_git_version=torch.version.git_version,
        torch_build=build,
        torch_build_sha256=hashlib.sha256(build.encode()).hexdigest(),
        torch_build_canonical_JSON_sha256=p.digest(build),
        pid=os.getpid(),
        parent_pid=os.getppid(),
        requested_environment=spec["device_environment_before_imports"],
        effective_environment={
            k: os.environ.get(k)
            for k in (
                *spec["device_environment_before_imports"],
                *spec["forbidden_environment_overrides"],
            )
        },
        execution_context={
            "fresh_process": True,
            "sandbox_restriction_cause": "unverified",
            "gpu_physical_absence": "not_inferred",
            "Metal_version": None,
            "GPU_core_count": None,
            "native_kernel": None,
        },
        installed_api_file_sha256=api_files,
    )
    if (
        result["torch_build_canonical_JSON_sha256"]
        != spec["policy"]["runtime_torch_build_sha256"]
    ):
        raise DeviceAdmissionError("Unsupported pinned PyTorch build.", result)
    return result


def tiny_proof(torch, accounting, guard):
    accounting.enable(torch.mps)
    guard.boundary("constant_only_MPS_operation")
    value = output = None
    try:
        value = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32, device="mps")
        if value.device.type != "mps":
            raise ValueError("MPS fallback/operand device refusal.")
        output = value * 2
        torch.mps.synchronize()
        actual = output.cpu().tolist()
        guard.check()
        if actual != [2.0, 4.0, 6.0]:
            raise ValueError("Constant-only physical result mismatch: " + repr(actual))
        return dict(
            status="passed",
            expected=[2.0, 4.0, 6.0],
            actual=actual,
            synchronization="forward_then_completion_then_CPU_copy",
        )
    finally:
        del output, value
        torch.mps.synchronize()
        guard.check()


def require_available(evidence):
    if evidence.get("is_built") is not True or evidence.get("is_available") is not True:
        raise ValueError("MPS unavailable in this execution context; cause unverified.")


def exact_roundtrip(torch, tensor, device):
    if tensor.dtype != torch.float32 or tensor.device.type != "cpu":
        raise ValueError("FP32 CPU transfer source required.")
    before = tensor.numpy().tobytes()
    transferred = tensor.to(device)
    if transferred.dtype != torch.float32 or transferred.device.type != device:
        raise ValueError("Device/precision fallback refused.")
    if device == "mps":
        torch.mps.synchronize()
    restored = transferred.cpu()
    if restored.numpy().tobytes() != before:
        raise ValueError("FP32 transfer roundtrip mutated bytes.")
    return transferred


class DeviceGuard(Guard):
    """Host failure precedence; both accounting paths outside timer pairs."""

    def __init__(self, *args, accounting, **kwargs):
        self.accounting = accounting
        super().__init__(*args, **kwargs)

    def check(self):
        super().check()
        try:
            self.accounting.sample()
        except Exception as exc:
            self.error = self.error or str(exc)
            raise GuardError(self.error) from exc
