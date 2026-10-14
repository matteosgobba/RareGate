"""Portable clocks for generated controller fixtures; no native accounting."""

import time


class SyntheticClock:
    def __call__(self):
        return time.monotonic()

    def snapshot(self):
        return dict(continuous_seconds=self(), ordinary_monotonic_seconds=self())
