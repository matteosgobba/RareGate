"""Deterministic particle training, measured resource gates and interruption."""

import ctypes
import ctypes.util
import hashlib
import inspect
import platform
import re
import resource
import signal
import subprocess
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager

import numpy as np
import torch

from latenttrigger.data.processed import content_hash
from latenttrigger.models.particle_set import (
    ParticleSetAutoencoder,
    event_loss,
    finite,
    validate_config,
)
from latenttrigger.training.autoencoder import EarlyStopping, deterministic_cpu


class ResourceLimitError(RuntimeError):
    """An explicit preregistered gate failed; downstream stages are forbidden."""


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


class ResourceMonitor:
    """Check launch and sample every 50ms; signal interrupts blocked CPU work.

    Clock/probe injection lets CI exercise ceilings without hardware/data.
    Deadline alarms interrupt long batches/store verification instead of only
    noticing after completion. Memory thread signals the main thread on failure.
    """

    def __init__(
        self,
        limits,
        *,
        probe=memory_snapshot,
        clock=time.monotonic,
        monitor_background=True,
    ):
        self.limits, self.probe, self.clock = limits, probe, clock
        self.started = clock()
        self.monitor_background = monitor_background
        self.samples = 0
        self.peak = {"peak_rss_bytes": 0, "native_heap_reserved_bytes": 0}
        self.minimum_available = None
        self.error = None
        self.deadlines = {}
        self._done = threading.Event()
        self._thread = None

    def check(self, *, launch=False):
        if self.error:
            raise ResourceLimitError(self.error)
        now = self.clock()
        for name, deadline in tuple(self.deadlines.items()):
            if now > deadline:
                raise ResourceLimitError(f"Time ceiling exceeded: {name}.")
        sample = self.probe()
        self.samples += 1
        for name in self.peak:
            self.peak[name] = max(self.peak[name], sample[name])
        available = sample["available_bytes"]
        self.minimum_available = min(available, self.minimum_available or available)
        self.last = sample
        if (
            launch
            and available < self.limits["minimum_system_available_bytes_at_launch"]
        ):
            raise ResourceLimitError("Launch available memory below 8 GiB.")
        if available < self.limits["stop_if_system_available_below_bytes"]:
            raise ResourceLimitError("Available memory below 4 GiB.")
        if sample["peak_rss_bytes"] > self.limits["process_peak_rss_ceiling_bytes"]:
            raise ResourceLimitError("Process peak RSS above 6 GiB.")
        if (
            sample["native_heap_reserved_bytes"]
            > self.limits["working_tensor_and_workspace_ceiling_bytes"]
        ):
            raise ResourceLimitError(
                "Conservative native workspace bound above 512 MiB."
            )

    def report(self):
        return {
            "elapsed_seconds": self.clock() - self.started,
            "samples": self.samples,
            **self.peak,
            "minimum_available_bytes": self.minimum_available,
            "last_sample": getattr(self, "last", None),
        }

    def _alarm(self, *_):
        if self.error:
            raise ResourceLimitError(self.error)
        raise ResourceLimitError("Monitored wall-time ceiling interrupted operation.")

    def _watch(self):
        while not self._done.wait(0.05):
            try:
                self.check()
            except Exception as exc:
                self.error = str(exc)
                # Python delivers the signal in the main thread, never raises there.
                signal.raise_signal(signal.SIGALRM)
                return

    def __enter__(self):
        self.check(launch=True)
        if self.monitor_background:
            self._previous_handler = signal.signal(signal.SIGALRM, self._alarm)
            self._thread = threading.Thread(target=self._watch, daemon=True)
            self._thread.start()
        return self

    @contextmanager
    def deadline(self, name: str, seconds: float):
        if seconds <= 0:
            raise ResourceLimitError(f"Exhausted remaining time budget: {name}.")
        deadline = self.clock() + seconds
        self.deadlines[name] = deadline
        if self.monitor_background:
            signal.setitimer(
                signal.ITIMER_REAL,
                max(0.001, min(self.deadlines.values()) - self.clock()),
            )
        try:
            yield
            self.check()
        finally:
            self.deadlines.pop(name, None)
            if self.monitor_background:
                delay = (
                    min(self.deadlines.values()) - self.clock() if self.deadlines else 0
                )
                signal.setitimer(signal.ITIMER_REAL, max(0.001, delay) if delay else 0)

    def __exit__(self, *_):
        self._done.set()
        if self._thread:
            self._thread.join(timeout=1)
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, self._previous_handler)


def adam(model, config):
    options = config["training"]["optimizer"].copy()
    options.pop("name")
    options["betas"] = tuple(options["betas"])
    if "decoupled_weight_decay" not in inspect.signature(torch.optim.Adam).parameters:
        options.pop("decoupled_weight_decay")
    return torch.optim.Adam(model.parameters(), **options)


def score_hash(scores):
    return hashlib.sha256(np.asarray(scores, dtype="<f8").tobytes()).hexdigest()


def epoch(model, batches, monitor, *, optimizer=None, expected=None):
    """Owned streamed views, actual event-weighted online objective or score vector."""
    total, count, vectors = 0.0, 0, []
    training = optimizer is not None
    model.train(training)
    with torch.set_grad_enabled(training):
        for x, mask, _metadata in batches:
            monitor.check()
            if training:
                optimizer.zero_grad(set_to_none=True)
                values = event_loss(x, model(x, mask), mask)
                values.mean().backward()
                for name, p in model.named_parameters():
                    if p.grad is None or p.grad.dtype != torch.float32:
                        raise ValueError("Missing/non-FP32 particle gradient.")
                    finite(p.grad, f"gradient {name}")
                optimizer.step()
                model.validate_parameters()
                for state in optimizer.state.values():
                    for value in state.values():
                        if isinstance(value, torch.Tensor):
                            if value.dtype != torch.float32:
                                raise ValueError("Non-FP32 Adam state.")
                            finite(value, "Adam state")
                total += values.detach().sum().item()
            else:
                values = model.score(x, mask)
                vectors.append(values)
            count += len(x)
            monitor.check()
    if count == 0 or (expected is not None and count != expected):
        raise ValueError("Particle population count mismatch.")
    if training:
        return total / count
    scores = np.concatenate(vectors)
    return float(scores.sum(dtype=np.float64) / count), scores


def fit(
    train_batches: Callable,
    selection_batches: Callable,
    config,
    monitor,
    *,
    on_epoch=None,
    train_count=699957,
    selection_count=74749,
):
    """Fit API has only train/selection factories; no calibration argument."""
    validate_config(config)
    if (
        getattr(train_batches, "role", None) != "train_background"
        or getattr(selection_batches, "role", None) != "validation_selection_background"
    ):
        raise ValueError(
            "Fit accepts only explicit training and selection backgrounds."
        )
    settings = config["training"]
    with deterministic_cpu(settings["seed"], settings["num_threads"]):
        model = ParticleSetAutoencoder()
        optimizer = adam(model, config)
        shuffle = torch.Generator(device="cpu").manual_seed(settings["shuffle_seed"])
        stop = EarlyStopping(settings["patience"], settings["min_delta"])
        history, selected_hash = [], None
        with monitor.deadline("fitting_selection", 36000):
            for number in range(1, settings["max_epochs"] + 1):
                with monitor.deadline("epoch_cycle", 180):
                    order = torch.randperm(train_count, generator=shuffle).numpy()
                    online = epoch(
                        model,
                        train_batches(order),
                        monitor,
                        optimizer=optimizer,
                        expected=train_count,
                    )
                    selection_mean, scores = epoch(
                        model, selection_batches(), monitor, expected=selection_count
                    )
                    row = {
                        "epoch": number,
                        "online_training_objective": online,
                        "selection_mean_score": selection_mean,
                        "selection_score_sha256": score_hash(scores),
                        "shuffle_sha256": hashlib.sha256(
                            order.astype("<i8").tobytes()
                        ).hexdigest(),
                    }
                    previous = stop.best_epoch
                    done = stop.update(number, selection_mean, model)
                    if stop.best_epoch != previous:
                        selected_hash = row["selection_score_sha256"]
                    # Only after both complete populations and deadline checks succeed.
                    monitor.check()
                history.append(row)
                if on_epoch:
                    on_epoch(row, stop)
                if done:
                    break
        record = {
            "training_count": train_count,
            "selection_count": selection_count,
            "epochs_executed": len(history),
            "best_epoch": stop.best_epoch,
            "best_selection_mean_score": stop.best_loss,
            "best_online_training_objective": history[stop.best_epoch - 1][
                "online_training_objective"
            ],
            "bad_epochs_at_stop": stop.bad_epochs,
            "stopping_reason": "patience" if done else "max_epochs",
            "selection_score_sha256": selected_hash,
            "history_sha256": content_hash({"history": history}),
            "synthetic_gate": True,
            "dev_gate": True,
            "resource_gate": True,
            "restored_verified": False,
            "reproduction_verified": False,
        }
        if done:
            stop.restore(model)
        return model.eval(), history, record


def measure_tensor_workspace(config):
    """Measure live ATen/autograd allocation timeline on worst-size synthetic data.

    External native malloc reservations are independently bounded during real
    stages; the profiler measures temporary tensor allocations rather than an
    analytic inventory. No real events or model settings are selected here.
    """
    from torch.profiler import ProfilerActivity, profile

    validate_config(config)
    with deterministic_cpu(1729, 1):
        x = torch.zeros(32, 384, 4)
        x[:, :, 3] = 1
        mask = torch.ones(32, 384, dtype=torch.bool)
        model = ParticleSetAutoencoder()
        optimizer = adam(model, config)
        with profile(
            activities=[ProfilerActivity.CPU],
            profile_memory=True,
            record_shapes=True,
            with_stack=True,
        ) as measured:
            for _ in range(2):
                optimizer.zero_grad(set_to_none=True)
                event_loss(x, model(x, mask), mask).mean().backward()
                optimizer.step()
        current = peak = 0
        for _time, action, _key, size in measured._memory_profile().timeline:
            if action.name in ("PREEXISTING", "CREATE"):
                current += size
            elif action.name == "DESTROY":
                current -= size
            peak = max(peak, current)
        return {
            "scope": "synthetic_full_cardinality_batch32",
            "method": "PyTorch_CPU_allocation_timeline_including_autograd_temporaries",
            "synthetic_optimizer_steps": 2,
            "peak_tensor_bytes": peak,
            "parameter_count": model.parameter_count,
            "torch_version": torch.__version__,
            "external_workspace_accounting": "whole_native_malloc_arena_reservation_during_real_stages",
        }
