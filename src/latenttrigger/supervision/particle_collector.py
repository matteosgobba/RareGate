"""Task0014 cached Darwin bindings; exact system vm_stat remains live backend.

Direct Mach VM collection is diagnostic-only: third-party kernel caching prevents
claiming the original synchronous observation semantics. No real execution route.
"""

import ctypes as C
import platform
import resource
import subprocess
import time

from latenttrigger.supervision.particle_host import ResourceLimitError, parse_vm_stat


class MallocStats(C.Structure):
    _fields_ = [
        ("blocks", C.c_uint),
        ("in_use", C.c_size_t),
        ("maximum", C.c_size_t),
        ("allocated", C.c_size_t),
    ]


class TaskBasic(C.Structure):
    _fields_ = [
        ("virtual", C.c_uint64),
        ("resident", C.c_uint64),
        ("maximum", C.c_uint64),
        ("times", C.c_int32 * 4),
        ("policy", C.c_int32),
        ("suspend", C.c_int32),
    ]


class VMRev1(C.Structure):
    _fields_ = (
        [
            (n, C.c_uint32)
            for n in ("free_count", "active_count", "inactive_count", "wire_count")
        ]
        + [
            (n, C.c_uint64)
            for n in (
                "zero_fill_count",
                "reactivations",
                "pageins",
                "pageouts",
                "faults",
                "cow_faults",
                "lookups",
                "hits",
                "purges",
            )
        ]
        + [(n, C.c_uint32) for n in ("purgeable_count", "speculative_count")]
        + [
            (n, C.c_uint64)
            for n in ("decompressions", "compressions", "swapins", "swapouts")
        ]
        + [
            (n, C.c_uint32)
            for n in (
                "compressor_page_count",
                "throttled_count",
                "external_page_count",
                "internal_page_count",
            )
        ]
        + [("total_uncompressed_pages_in_compressor", C.c_uint64)]
    )


def validate_abi():
    if (
        C.sizeof(C.c_uint32) != 4
        or C.sizeof(C.c_uint64) != 8
        or C.sizeof(C.c_void_p) != 8
        or C.sizeof(TaskBasic) != 48
        or C.sizeof(MallocStats) != 32
        or C.sizeof(VMRev1) != 152
        or VMRev1.speculative_count.offset != 92
        or VMRev1.decompressions.offset != 96
    ):
        raise ResourceLimitError("Unsupported Darwin64 ctypes ABI.")


def normalize_native(raw, page_size):
    for key in ("free_count", "inactive_count", "speculative_count"):
        if type(raw.get(key)) is not int or not 0 <= raw[key] <= 2**32 - 1:
            raise ResourceLimitError("Malformed Mach native page counts.")
    if (
        type(page_size) is not int
        or page_size <= 0
        or raw["speculative_count"] > raw["free_count"]
    ):
        raise ResourceLimitError("Impossible speculative subtraction/page size.")
    displayed = raw["free_count"] - raw["speculative_count"]
    available = (displayed + raw["inactive_count"]) * page_size
    return {
        "native_free_count": raw["free_count"],
        "native_speculative_count": raw["speculative_count"],
        "free_pages": displayed,
        "inactive_pages": raw["inactive_count"],
        "page_size_bytes": page_size,
        "available_bytes": available,
        "available_gib": available / 2**30,
        "available_method": "Darwin_free_plus_inactive_pages",
    }


class DarwinBindings:
    """Resolve library/signatures once; every sample obtains new measurements."""

    def __init__(self):
        if platform.system() != "Darwin":
            raise ResourceLimitError("Darwin bindings unavailable; no fallback.")
        validate_abi()
        self.lib = C.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
        self.malloc = self.lib.malloc_zone_statistics
        self.malloc.argtypes = [C.c_void_p, C.POINTER(MallocStats)]
        self.malloc.restype = None
        self.task = None
        self.task_info = self.sysctl = None
        try:
            self.task_info = self.lib.task_info
            self.task_info.argtypes = [
                C.c_uint32,
                C.c_uint32,
                C.c_void_p,
                C.POINTER(C.c_uint32),
            ]
            self.task_info.restype = C.c_int
            self.task = C.c_uint32.in_dll(self.lib, "mach_task_self_").value
        except (AttributeError, ValueError):
            self.task_info = None
        try:
            self.sysctl = self.lib.sysctlbyname
            self.sysctl.argtypes = [
                C.c_char_p,
                C.c_void_p,
                C.POINTER(C.c_size_t),
                C.c_void_p,
                C.c_size_t,
            ]
            self.sysctl.restype = C.c_int
        except AttributeError:
            self.sysctl = None

    def process_sample(self):
        stats = MallocStats()
        self.malloc(None, C.byref(stats))
        if not stats.allocated or stats.in_use > stats.allocated:
            raise ResourceLimitError(
                "Native whole-malloc accounting unavailable/malformed."
            )
        result = {
            "native_heap_reserved_bytes": stats.allocated,
            "native_heap_in_use_bytes": stats.in_use,
            "workspace_method": "all_malloc_zone_reserved_bytes_conservative_upper_bound",
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "dirty_private_bytes": None,
            "dirty_private_status": "not_measured",
        }
        info, count = TaskBasic(), C.c_uint32(12)
        rc = (
            self.task_info(self.task, 20, C.byref(info), C.byref(count))
            if self.task_info
            else -1
        )
        result.update(
            current_rss_bytes=info.resident if rc == 0 and count.value == 12 else None,
            virtual_address_bytes=info.virtual
            if rc == 0 and count.value == 12
            else None,
            current_rss_method="own_MACH_TASK_BASIC_INFO_64",
            task_info_error=rc if rc else None,
            task_info_return_count=count.value,
        )
        pressure, size = C.c_uint32(), C.c_size_t(4)
        rc = (
            self.sysctl(
                b"kern.memorystatus_vm_pressure_level",
                C.byref(pressure),
                C.byref(size),
                None,
                0,
            )
            if self.sysctl
            else -1
        )
        result.update(
            pressure_dispatch_flags=pressure.value
            if rc == 0 and size.value == 4
            else None,
            pressure_errno=C.get_errno() if rc else None,
            pressure_method="XNU_read_only_sysctl_dispatch_flags_1normal_2warning_4critical",
        )
        return result


class CachedSystemCollector:
    backend = "system_vm_stat_oneshot_cached_bindings_v3"

    def __init__(
        self, *, bindings=None, run=subprocess.check_output, clock=time.monotonic
    ):
        self.bindings = DarwinBindings() if bindings is None else bindings
        self.run, self.clock = run, clock

    def __call__(self):
        tick = self.clock()
        # Retain exact system binary/2s timeout. Never reuse a primary value.
        raw = self.run(["/usr/bin/vm_stat"], text=True, timeout=2)
        pages = parse_vm_stat(raw)
        result = {**pages, **self.bindings.process_sample()}
        finished = self.clock()
        result.update(
            collector_backend=self.backend,
            sample_started_monotonic=tick,
            sample_finished_monotonic=finished,
            sample_age_upper_seconds=finished - tick,
            kernel_generation_time="unexposed; within synchronous system-query interval",
            primary_values_reused=False,
        )
        if finished - tick > 2 or finished < tick:
            raise ResourceLimitError(
                "Primary observation age/collection deadline exceeded2s."
            )
        return result


class MachDiagnosticCollector:
    """Public HOST_VM_INFO64 rev1 ABI, explicitly rejected for live monitoring."""

    backend = "host_statistics64_rev1_diagnostic_only"

    def __init__(self):
        self.bindings = DarwinBindings()
        lib = self.bindings.lib
        self.host_self = lib.mach_host_self
        self.host_self.restype = C.c_uint32
        self.host = self.host_self()
        self.vm = lib.host_statistics64
        self.vm.argtypes = [C.c_uint32, C.c_int, C.c_void_p, C.POINTER(C.c_uint32)]
        self.vm.restype = C.c_int
        self.page_size = C.c_uint64.in_dll(lib, "vm_kernel_page_size").value
        if not self.host or not self.page_size:
            raise ResourceLimitError("Mach host/kernel page accounting unavailable.")
        self.deallocate = lib.mach_port_deallocate
        self.deallocate.argtypes = [C.c_uint32, C.c_uint32]
        self.deallocate.restype = C.c_int

    def __call__(self):
        tick = time.monotonic()
        data, count = VMRev1(), C.c_uint32(38)
        rc = self.vm(self.host, 4, C.byref(data), C.byref(count))
        if rc or count.value != 38:
            raise ResourceLimitError("Unsupported HOST_VM_INFO64 rev1 return/count.")
        raw = {n: int(getattr(data, n)) for n, _ in VMRev1._fields_}
        return {
            **normalize_native(raw, self.page_size),
            **self.bindings.process_sample(),
            "collector_backend": self.backend,
            "raw_native_counts": raw,
            "host_statistics_return_count": count.value,
            "call_started_monotonic": tick,
            "call_finished_monotonic": time.monotonic(),
            "kernel_sample_age_seconds": None,
            "freshness": "third_party_cache_unexposed; not a live50ms observation",
            "real_monitor_eligible": False,
        }

    def close(self):
        if self.host:
            self.deallocate(self.bindings.task, self.host)
            self.host = 0
