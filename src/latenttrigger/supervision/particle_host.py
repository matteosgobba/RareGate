"""Pure-stdlib Darwin probes, copied/parity-tested against frozen v2 bindings.

No numeric policy is defined here. Each owned process measures itself; primary
unknowns fail closed in the real worker. Optional context never adds availability.
"""

import ctypes
import ctypes.util
import os
import platform
import re
import resource
import subprocess
import sys
from datetime import UTC, datetime


class ResourceLimitError(RuntimeError):
    """Primary accounting is unavailable or malformed."""


def parse_vm_stat(output: str) -> dict:
    """Strict page accounting; contextual counters never increase availability."""
    headers = re.findall(r"page size of (\d+) bytes", output)
    counts = {}
    for name in ("free", "inactive"):
        values = re.findall(rf"^Pages {name}:\s+(\d+)\.\s*$", output, re.M)
        if len(values) != 1:
            raise ResourceLimitError("Missing/malformed/duplicate vm_stat page count.")
        counts[name] = int(values[0])
    if len(headers) != 1 or int(headers[0]) <= 0:
        raise ResourceLimitError("Missing/malformed vm_stat page size.")
    page_size = int(headers[0])
    available = (counts["free"] + counts["inactive"]) * page_size
    return {
        "page_size_bytes": page_size,
        "free_pages": counts["free"],
        "inactive_pages": counts["inactive"],
        "available_bytes": available,
        "available_gib": available / 2**30,
        "vm_stat_raw": output,
        "context_counters_are_not_available_bytes": True,
    }


def memory_snapshot() -> dict:
    """Darwin free+inactive pages and whole native malloc arena reservation.

    The arena measurement conservatively includes Python/framework allocations,
    not only network tensors. Read-only mapped file pages are covered by RSS.
    Native CPU allocations use malloc; unknown accounting backends fail closed.
    """
    system = platform.system()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if system != "Darwin":
        raise ResourceLimitError("Real resource gate needs verified Darwin accounting.")
    output = subprocess.check_output(["vm_stat"], text=True, timeout=2)
    pages = parse_vm_stat(output)

    class Stats(ctypes.Structure):
        _fields_ = [
            ("blocks", ctypes.c_uint),
            ("in_use", ctypes.c_size_t),
            ("maximum", ctypes.c_size_t),
            ("allocated", ctypes.c_size_t),
        ]

    library = ctypes.CDLL(ctypes.util.find_library("System"))
    library.malloc_zone_statistics.argtypes = [ctypes.c_void_p, ctypes.POINTER(Stats)]
    stats = Stats()
    library.malloc_zone_statistics(None, ctypes.byref(stats))
    if not stats.allocated:
        raise ResourceLimitError(
            "Native workspace/system memory accounting unavailable."
        )
    return {
        **pages,
        "peak_rss_bytes": rss,
        "native_heap_reserved_bytes": stats.allocated,
        "native_heap_in_use_bytes": stats.in_use,
        "workspace_method": "all_malloc_zone_reserved_bytes_conservative_upper_bound",
        "available_method": "Darwin_free_plus_inactive_pages",
    }


def process_context(*, pressure=True):
    """Own-task Mach basic info and read-only XNU dispatch-pressure flags.

    Mach fields/48-byte ABI are from XNU mach/task_info.h; no external command.
    Optional telemetry failure is explicit and never replaces primary accounting.
    """
    result = {
        "dirty_private_bytes": None,
        "dirty_private_status": "not_measured_no_supported_binding",
    }
    try:
        lib = ctypes.CDLL(ctypes.util.find_library("System"), use_errno=True)
        if pressure:
            flags, size = ctypes.c_uint32(), ctypes.c_size_t(4)
            lib.sysctlbyname.argtypes = [
                ctypes.c_char_p,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_size_t),
                ctypes.c_void_p,
                ctypes.c_size_t,
            ]
            rc = lib.sysctlbyname(
                b"kern.memorystatus_vm_pressure_level",
                ctypes.byref(flags),
                ctypes.byref(size),
                None,
                0,
            )
            result.update(
                pressure_dispatch_flags=flags.value
                if rc == 0 and size.value == 4
                else None,
                pressure_errno=ctypes.get_errno() if rc else None,
                pressure_method="XNU_read_only_sysctl_dispatch_flags_1normal_2warning_4critical",
            )
        else:
            result.update(pressure_dispatch_flags=None, pressure_status="not_queried")

        class Basic(ctypes.Structure):
            _fields_ = [
                ("virtual", ctypes.c_uint64),
                ("resident", ctypes.c_uint64),
                ("maximum", ctypes.c_uint64),
                ("times", ctypes.c_int32 * 4),
                ("policy", ctypes.c_int32),
                ("suspend", ctypes.c_int32),
            ]

        task = ctypes.c_uint32.in_dll(lib, "mach_task_self_").value
        info, count = Basic(), ctypes.c_uint32(12)
        lib.task_info.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        rc = lib.task_info(task, 20, ctypes.byref(info), ctypes.byref(count))
        if rc == 0 and count.value == 12 and ctypes.sizeof(Basic) == 48:
            result.update(
                current_rss_bytes=info.resident,
                virtual_address_bytes=info.virtual,
                current_rss_method="own_MACH_TASK_BASIC_INFO_64",
            )
        else:
            result.update(
                current_rss_bytes=None, virtual_address_bytes=None, task_info_error=rc
            )
    except (OSError, AttributeError, ValueError) as exc:
        result.update(
            pressure_dispatch_flags=None,
            current_rss_bytes=None,
            virtual_address_bytes=None,
            optional_telemetry_error=str(exc),
        )
    return result


def heavy_modules():
    return sorted(
        n
        for n in (
            "numpy",
            "torch",
            "pandas",
            "h5py",
            "latenttrigger.data.processed",
            "latenttrigger.training.particle_set",
            "latenttrigger.models.particle_memory_study",
        )
        if n in sys.modules
    )


def snapshot():
    value = memory_snapshot()
    value.update(process_context(pressure=False))
    value.update(
        pid=os.getpid(),
        parent_pid=os.getppid(),
        timestamp_utc=datetime.now(UTC).isoformat(),
        heavy_modules=heavy_modules(),
    )
    return value


def host_context_once():
    result = {"pressure": process_context(pressure=True)}
    for name, command in {
        "installed_ram": ["/usr/sbin/sysctl", "-n", "hw.memsize"],
        "current_swap_use": ["/usr/sbin/sysctl", "vm.swapusage"],
        "pressure_context": ["/usr/bin/memory_pressure", "-Q"],
    }.items():
        try:
            row = subprocess.run(
                command, text=True, capture_output=True, timeout=2, check=False
            )
            result[name] = {
                "status": "available" if row.returncode == 0 else "unavailable",
                "command": command,
                "exit_code": row.returncode,
                "output": row.stdout.strip(),
                "error": row.stderr.strip(),
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            result[name] = {
                "status": "unavailable",
                "command": command,
                "error": str(exc),
            }
    result["interpretation"] = (
        "Context only; categories overlap; cumulative swap counters are not current swap use."
    )
    return result
