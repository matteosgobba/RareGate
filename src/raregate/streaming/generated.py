"""The only backend shipped: generated memory and artificial scores, no file paths."""

from typing import Protocol

from .protocol import approved, require


class Backend(Protocol):
    def read(self, positions): ...
    def features(self, rows): ...
    def decisions(self, features): ...
    def reference(self, positions, scores, masks): ...


def gather_plan(positions):
    require(
        1 <= len(positions) <= 8 and all(approved(p) for p in positions),
        "Symbolic batch1..8",
    )
    occurrences = {}
    layers = []
    for i in sorted(range(len(positions)), key=lambda j: positions[j]):
        p = positions[i]
        layer = occurrences.get(p, 0)
        occurrences[p] = layer + 1
        if layer == len(layers):
            layers.append([])
        layers[layer].append((p, i))
    return layers


def gather(positions, read, on_start=lambda *_: None, on_return=lambda *_: None):
    # Lazy numeric import only on explicit generated execution.
    import numpy as np

    rows = np.empty((len(positions), 3), dtype=np.float64)
    for j, layer in enumerate(gather_plan(positions)):
        selection = [p for p, _ in layer]
        on_start(j, len(selection))
        piece = read(selection)
        require(
            isinstance(piece, np.ndarray)
            and piece.shape == (len(selection), 3)
            and piece.dtype == np.float64
            and piece.flags.owndata
            and piece.flags.c_contiguous
            and np.isfinite(piece).all(),
            "Owned exact generated selected rows",
        )
        for row, (_, i) in zip(piece, layer, strict=True):
            rows[i] = row
        on_return(j, len(selection))
    return rows


class GeneratedBackend:
    def __init__(self, *, mode="generated_memory"):
        require(
            mode == "generated_memory",
            "Operational mode unsupported before numeric import",
        )
        import numpy as np

        self.np = np
        p = np.arange(1024, dtype=np.float64)
        self.table = np.column_stack((p, p + 1, p * 2))
        self.thresholds = np.array([0, 1, 64, 127], dtype=np.float64)

    def read(self, positions):
        require(
            1 <= len(positions) <= 8
            and all(approved(p) for p in positions)
            and all(a < b for a, b in zip(positions, positions[1:], strict=False)),
            "Strict selected fixture callback",
        )
        return self.table[positions].copy()

    def features(self, rows):
        np = self.np
        require(
            rows.ndim == 2
            and 1 <= len(rows) <= 8
            and rows.shape[1] == 3
            and np.isfinite(rows).all(),
            "Generated read shape/finite",
        )
        features = np.empty((len(rows), 8), dtype=np.float32)
        features[:, :3] = rows
        for i in range(3, 8):
            features[:, i] = rows[:, 0] + i
        return features

    def decisions(self, features):
        np = self.np
        require(
            features.shape == (len(features), 8)
            and 1 <= len(features) <= 8
            and np.isfinite(features).all(),
            "Actual generated feature shape/finite",
        )
        scores = np.array(features[:, 0], dtype=np.float64, copy=True)
        masks = (scores[:, None] > self.thresholds[None, :]).copy()
        return scores.copy(), masks.copy()

    def reference(self, positions, scores, masks):
        # Independent direct indexing and scalar comparison, bypassing planner/features/decision wrapper.
        np = self.np
        require(
            1 <= len(positions) <= 8 and all(approved(p) for p in positions),
            "Reference symbolic scope",
        )
        expected = np.array([self.table[p, 0] for p in positions], dtype=np.float64)
        decisions = np.array(
            [[float(s) > float(t) for t in self.thresholds] for s in expected],
            dtype=bool,
        )
        require(
            scores.shape == (len(positions),)
            and scores.dtype == np.float64
            and masks.shape == (len(positions), 4)
            and masks.dtype == bool
            and scores.flags.owndata
            and masks.flags.owndata
            and np.isfinite(scores).all(),
            "Owned actual-shape generated outputs",
        )
        require(
            scores.tobytes() == expected.tobytes()
            and masks.tobytes() == decisions.tobytes(),
            "Independent generated reference",
        )
