"""Public Accelerate BLAS thread-local mode; no BLAS operator substitution.

ABI and enum verified in the installed vecLib thread_api.h (macOS15+).
https://developer.apple.com/documentation/accelerate/blassetthreading(_:)
"""

import ctypes
import platform
import plistlib
import threading
from pathlib import Path

LIBRARY = "/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate"


class AccelerateThreads:
    def __init__(self, *, library=None):
        if (
            platform.system() != "Darwin"
            or ctypes.sizeof(ctypes.c_uint) != 4
            or ctypes.sizeof(ctypes.c_int) != 4
        ):
            raise ValueError("Unsupported public Accelerate threading ABI/platform.")
        try:
            self.library = library or ctypes.CDLL(LIBRARY)
            self.set = self.library.BLASSetThreading
            self.set.argtypes = [ctypes.c_uint]
            self.set.restype = ctypes.c_int
            self.get = self.library.BLASGetThreading
            self.get.argtypes = []
            self.get.restype = ctypes.c_uint
        except (AttributeError, OSError) as exc:
            raise ValueError("Public Accelerate threading API unavailable.") from exc
        self.owner = threading.get_ident()
        self.previous = self.get()
        if self.previous not in (0, 1):
            raise ValueError("Unknown Accelerate threading mode.")
        self.set_returncode = self.set(1)
        if self.set_returncode != 0:
            raise ValueError("Accelerate single-thread mode unsupported.")
        try:
            self.verify()
        except BaseException:
            self.set(self.previous)
            raise

    def verify(self):
        if threading.get_ident() != self.owner or self.get() != 1:
            raise ValueError("Accelerate single-thread mode/owning thread changed.")

    def report(self):
        self.verify()
        version = None
        try:
            path = Path(LIBRARY).parent / "Resources/Info.plist"
            with path.open("rb") as file:
                version = plistlib.load(file).get("CFBundleVersion")
        except (OSError, ValueError):
            pass
        return {
            "method": "public_BLASSetThreading_success_and_BLASGetThreading_query",
            "library": LIBRARY,
            "framework_bundle_version": version,
            "previous_mode": self.previous,
            "queried_mode": 1,
            "BLAS_THREADING_SINGLE_THREADED_enum": 1,
            "setter_returncode": self.set_returncode,
            "thread_local": True,
            "owner_python_thread_id": self.owner,
            "all_benchmark_BLAS_calls_on_owner_thread": True,
        }

    def restore(self):
        if (
            threading.get_ident() != self.owner
            or self.set(self.previous) != 0
            or self.get() != self.previous
        ):
            raise ValueError("Failed to restore Accelerate thread-local mode.")
