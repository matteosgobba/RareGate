"""Task0054 real consumer. Import is data-free; activation is explicit and closed."""

import hashlib
import io
import json
import os
import struct
import zlib
from pathlib import Path

from . import quota
from .generated import gather_plan
from .pilot54 import fixed_path, source_bytes
from .protocol import require


def positions_checked(positions):
    require(
        1 <= len(positions) <= 8
        and all(type(p) is int and 0 <= p < 64 for p in positions),
        "Task0054 only positions0..63, actual1..8",
    )


def gather_real(positions, read, on_start=lambda *_: None, on_return=lambda *_: None):
    positions_checked(positions)  # before allocation or callback
    import numpy as np

    rows = np.empty((len(positions), 2101), dtype="<f8")
    for j, layer in enumerate(gather_plan(positions)):
        selection = [p for p, _ in layer]
        on_start(j, len(selection))
        piece = read(selection)
        require(
            isinstance(piece, np.ndarray)
            and piece.shape == (len(selection), 2101)
            and piece.dtype == np.dtype("<f8")
            and piece.flags.owndata
            and piece.flags.c_contiguous
            and np.isfinite(piece).all()
            and (piece[:, 2100] == 0).all(),
            "Owned finite background2101 selection",
        )
        for row, (_, i) in zip(piece, layer, strict=True):
            rows[i] = row
        on_return(j, len(selection))
    return rows


def public_owned(model, features, thresholds, channels):
    import numpy as np

    require(
        features.shape == (len(features), 8)
        and 1 <= len(features) <= 8
        and features.dtype == np.dtype("<f4")
        and np.isfinite(features).all(),
        "Actual-m frozen8-channel input",
    )
    packed = np.array(features, dtype="<f4", order="C", copy=True)
    scores = model.score(packed, feature_names=channels)
    require(
        isinstance(scores, np.ndarray)
        and scores.shape == (len(features),)
        and scores.dtype == np.dtype("<f8")
        and np.isfinite(scores).all()
        and (scores >= 0).all(),
        "Finite public FP64 SSE",
    )
    return scores.copy(), (scores[:, None] > thresholds[None, :]).copy()


def independent_reference(model, golden, positions, thresholds, channels):
    import numpy as np

    positions_checked(positions)
    # Independent packing and four scalar comparisons; bypass streaming wrapper.
    packed = np.empty((len(positions), 8), dtype="<f4", order="C")
    for i, p in enumerate(positions):
        packed[i, :] = golden[p, :]
    scores = model.score(packed, feature_names=channels)
    require(
        scores.shape == (len(positions),)
        and scores.dtype == np.dtype("<f8")
        and np.isfinite(scores).all()
        and (scores >= 0).all(),
        "Reference finite public SSE",
    )
    masks = np.array(
        [[float(s) > float(t) for t in thresholds] for s in scores], dtype=bool
    )
    return scores.copy(), masks.copy()


class Budget:
    """One consumer's exact stage counts; intents survive a failed operation."""

    CAPS = dict(
        raw_calls=96,
        raw_rows=208,
        feature_calls=96,
        feature_rows=208,
        score_calls=176,
        score_rows=344,
        booleans=1376,
        reference_calls=80,
        reference_rows=136,
        membership_loads=1,
        membership_records=6999,
        golden_loads=1,
        golden_rows=1024,
        model_loads=1,
        threshold_loads=1,
        hdf_opens=2,
        hdf_closes=2,
        schema_checks=4,
    )

    def __init__(self):
        self.counts = {k: 0 for k in self.CAPS}
        self.started = {k: 0 for k in ("raw_calls", "feature_calls", "score_calls")}
        self.returned = dict(self.started)
        self.returned_rows = dict(self.started)
        self.inflight = None

    def add(self, key, n=1):
        require(
            type(n) is int and n >= 0 and self.counts[key] + n <= self.CAPS[key],
            "Task0054 operation budget:" + key,
        )
        self.counts[key] += n

    def begin(self, kind, n):
        require(self.inflight is None and 1 <= n <= 8, "Nonoverlapping bounded service")
        self.add(kind + "_calls")
        self.add(kind + "_rows", n)
        self.started[kind + "_calls"] += 1
        self.inflight = [kind, n]

    def finish(self, observed_rows=None):
        kind, n = self.inflight
        if observed_rows is not None:
            n = observed_rows
        self.returned[kind + "_calls"] += 1
        self.returned_rows[kind + "_calls"] += n
        self.inflight = None


class RealBackend:
    """Constructed only inside explicitly activated Task0054 consumer."""

    def __init__(self, root, directory, candidate, clocks, progress):
        from .pilot54 import CONFIG, source_manifest
        from .validation_v2 import fingerprint

        self.repo = Path(__file__).resolve().parents[3]
        self.root, self.directory, self.clocks, self.progress = (
            Path(root),
            Path(directory),
            clocks,
            progress,
        )
        self.handle = self.limiter = None
        self.fd = quota.open_file(
            self.directory / "consumer-audit.bin", os.O_CREAT | os.O_EXCL | os.O_RDWR
        )
        quota.truncate(self.fd, 65536)
        self.budget, self.generation = Budget(), 0
        self.phase, self.observations, self.gate_digests = "imports", {}, []
        self.retained = []
        self.spec = json.loads((self.repo / CONFIG).read_text())
        active = json.loads((self.root / "pilot/activation.json").read_text())
        prospective = json.loads((self.root / "pilot/prospective.json").read_text())
        require(
            active["task"] == "0054"
            and active["single_session"]
            and prospective["bundle_sha256"] == fingerprint(source_manifest(self.repo)),
            "Bound activated pilot/source before numeric imports",
        )
        require(
            candidate in ("pca-v1", "compact-autoencoder-v2"), "One original candidate"
        )
        self.entry = next(x for x in self.spec["models"] if x["name"] == candidate)
        self.files = {x["role"]: x for x in self.spec["allowed_files"]}
        self.checkpoint()
        import numpy as np

        from latenttrigger.benchmarks import core
        from latenttrigger.data.features import Parameters
        from latenttrigger.data.inspection import AGGREGATE_NAMES

        self.np, self.core, self.channels = np, core, list(AGGREGATE_NAMES)
        self.limiter, self.threads_before = core.configure_threads(self.spec)
        require(
            canonical_build_hash(core.torch.__config__.show())
            == self.spec["numerical"]["runtime_torch_build_sha256"],
            "Original supported Torch build",
        )
        import ctypes

        require(ctypes.CDLL(None).fegetround() == 0, "CPU round-to-nearest")
        self.checkpoint()
        # Hash only this candidate's small original sources, not the other model.
        roles = ["membership", "golden", "transform"] + list(self.spec["lineage_roles"])
        roles += [candidate + ":" + k for k in ("model", "config", "calibration")]
        self.loaded = {
            role: source_bytes(self.repo, self.files[role]) for role in roles
        }
        for role in self.spec["lineage_roles"]:
            item = json.loads(self.loaded[role])
            if role == "dev_manifest":
                require(
                    item["scientific_sha256"] == self.spec["dev_scientific_sha256"],
                    "Frozen dev lineage",
                )
        validate_lineage(
            {
                k: json.loads(self.loaded[k])
                for k in list(self.spec["lineage_roles"]) + ["transform"]
            },
            self.spec,
        )
        require(
            sum(len(b) for b in self.loaded.values()) <= 262144,
            "Source byte buffers262144B",
        )
        self.budget.add("membership_loads")
        values = np.load(io.BytesIO(self.loaded["membership"]), allow_pickle=False)
        require(
            values.shape == (6999,)
            and values.dtype == np.dtype("<i8")
            and ((values >= 0) & (values < 1100000)).all()
            and len(np.unique(values)) == 6999,
            "Original6999 background membership",
        )
        self.budget.add("membership_records", 6999)
        self.ids = np.array(
            np.sort(values, kind="stable")[:1024], dtype="<i8", copy=True
        )
        require(
            hashlib.sha256(self.ids.tobytes()).hexdigest()
            == self.spec["membership"]["selected_sha256"],
            "Original1024 prefix",
        )
        del values
        self.ids.setflags(write=False)
        self.budget.add("golden_loads")
        self.golden = np.load(io.BytesIO(self.loaded["golden"]), allow_pickle=False)
        require(
            self.golden.shape == (1024, 8)
            and self.golden.dtype == np.dtype("<f4")
            and np.isfinite(self.golden).all()
            and hashlib.sha256(self.golden.tobytes()).hexdigest()
            == self.spec["golden"]["payload_sha256"],
            "Original golden payload",
        )
        self.budget.add("golden_rows", 1024)
        self.golden.setflags(write=False)
        self.parameters = Parameters.from_config(json.loads(self.loaded["transform"]))
        artifact = json.loads(self.loaded[candidate + ":model"])
        calibration = json.loads(self.loaded[candidate + ":calibration"])
        config = json.loads(self.loaded[candidate + ":config"])

        def digest(x):
            return hashlib.sha256(
                json.dumps(x, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()

        require(
            artifact["scientific_sha256"] == self.entry["model_scientific_sha256"]
            and digest(artifact["scientific"]) == artifact["scientific_sha256"]
            and calibration["scientific_sha256"]
            == self.entry["results_scientific_sha256"]
            and digest(calibration["scientific"]) == calibration["scientific_sha256"]
            and digest(config) == self.entry["config_canonical_sha256"],
            "Original scientific/config identities",
        )
        self.budget.add("model_loads")
        self.model = (
            core.PCAReconstruction if candidate == "pca-v1" else core.CompactAutoencoder
        ).from_artifact(artifact)
        if candidate == "pca-v1":
            require(self.model.k == 6, "Frozen PCA6")
        else:
            require(
                self.model.parameter_count == 155
                and all(
                    p.dtype == core.torch.float32 and p.device.type == "cpu"
                    for p in self.model.parameters()
                ),
                "Frozen CPU AE155",
            )
            self.model.eval()
        self.budget.add("threshold_loads")
        self.thresholds = np.array(
            [x["threshold"] for x in calibration["scientific"]["thresholds"]],
            dtype="<f8",
        )
        require(
            self.thresholds.shape == (4,)
            and self.thresholds.tobytes()
            == np.array(
                [x["threshold"] for x in self.entry["thresholds"]], dtype="<f8"
            ).tobytes(),
            "Frozen strict4 thresholds",
        )
        from latenttrigger.benchmarks.development_decision_protocol import (
            expected_parameter_hash,
        )

        require(
            core.parameter_hash(self.model) == expected_parameter_hash(artifact),
            "Original artifact parameter bytes",
        )
        self.initial_state = self.state()
        self.loaded.clear()  # no second model/array load; originals checked again as bytes after work
        self.phase = "pre_gates"
        self.open_handle()
        self.gates()
        self.close_handle()
        self.phase = "reopened_no_raw_warmup"
        self.open_handle()
        self.checkpoint()

    def checkpoint(self):
        from .supervision import own_rss

        self.generation += 1
        self.progress()
        item = dict(
            phase=self.phase,
            continuous_ns=self.clocks.continuous(),
            rss_bytes=own_rss(),
        )
        previous = self.observations.get(self.phase)
        self.observations[self.phase] = dict(
            first_ns=previous["first_ns"] if previous else item["continuous_ns"],
            last_ns=item["continuous_ns"],
            lifetime_peak_RSS_bytes=item["rss_bytes"],
        )
        require(len(self.observations) <= 8, "Bounded phase observations")
        data = dict(
            generation=self.generation,
            phase=self.phase,
            budget=self.budget.__dict__,
            peak_RSS_bytes=own_rss(),
            observations=self.observations,
        )
        b = json.dumps(data, separators=(",", ":"), allow_nan=False).encode()
        require(len(b) <= 4072, "Fixed consumer state bound")
        header = struct.pack(
            "<QQII", self.generation, self.clocks.continuous(), len(b), zlib.crc32(b)
        )
        blob = header + b + bytes(4096 - 24 - len(b))
        require(
            quota.pwrite(self.fd, blob, 4096 * (self.generation % 2)) == 4096,
            "Consumer checkpoint write",
        )

    def open_handle(self):
        import h5py

        from latenttrigger.benchmarks.development_raw_metadata import properties

        self.budget.add("hdf_opens")
        self.checkpoint()
        path = fixed_path(self.repo, self.files["raw"])
        self.handle = h5py.File(path, "r", **self.spec["cache"])
        self.budget.add("schema_checks")
        self.hdf_metadata = properties(self.handle, self.spec["raw"]["audit_schema"])
        self.dataset = self.handle["/df/block0_values"]
        self.checkpoint()

    def close_handle(self):
        from latenttrigger.benchmarks.development_raw_metadata import properties

        if self.handle is not None:
            self.budget.add("schema_checks")
            properties(self.handle, self.spec["raw"]["audit_schema"])
            identifier = self.handle.id
            self.handle.close()
            self.handle = None
            require(not identifier.valid, "HDF handle closed")
            self.budget.add("hdf_closes")
            self.checkpoint()

    def read(self, positions):
        positions_checked(positions)
        require(
            all(a < b for a, b in zip(positions, positions[1:], strict=False)),
            "Increasing duplicate-free selected positions",
        )
        self.budget.begin("raw", len(positions))
        self.checkpoint()
        request = self.ids[positions]
        self.last_hdf_start = self.clocks.service()
        rows = self.dataset[request.tolist(), :]
        self.last_hdf_return = self.clocks.service()
        self.budget.finish(
            int(rows.shape[0])
            if isinstance(rows, self.np.ndarray) and rows.ndim == 2
            else 0
        )
        self.checkpoint()
        require(
            rows.shape == (len(positions), 2101)
            and rows.dtype == self.np.dtype("<f8")
            and rows.flags.owndata
            and rows.flags.c_contiguous
            and self.np.isfinite(rows).all()
            and (rows[:, 2100] == 0).all(),
            "Exact approved raw rows",
        )
        return rows

    def features(self, rows):
        from latenttrigger.benchmarks.development_raw_adapter import construct

        require(
            rows.ndim == 2 and rows.shape[1] == 2101 and 1 <= len(rows) <= 8,
            "Real feature shape1..8",
        )
        self.budget.begin("feature", len(rows))
        self.checkpoint()
        features = construct(rows, self.parameters)
        self.last_feature_end = self.clocks.service()
        self.budget.finish()
        self.checkpoint()
        return features

    def decisions(self, features):
        self.budget.begin("score", len(features))
        self.checkpoint()
        output = public_owned(self.model, features, self.thresholds, self.channels)
        self.last_decision_end = self.clocks.service()
        self.budget.add("booleans", 4 * len(features))
        self.budget.finish()
        self.checkpoint()
        return output

    def reference(self, positions, scores, masks):
        self.budget.add("reference_calls")
        self.budget.add("reference_rows", len(positions))
        self.budget.begin("score", len(positions))
        self.checkpoint()
        ref, decisions = independent_reference(
            self.model, self.golden, positions, self.thresholds, self.channels
        )
        self.budget.add("booleans", 4 * len(positions))
        self.budget.finish()
        self.checkpoint()
        require(
            ref.tobytes() == scores.tobytes()
            and decisions.tobytes() == masks.tobytes(),
            "Exact independent same-shape public score/masks",
        )
        return hashlib.sha256(ref.tobytes() + decisions.tobytes()).hexdigest()

    def feature_parity(self, positions, features):
        require(
            features.tobytes() == self.golden[positions].tobytes(),
            "Exact full-particle golden feature bytes",
        )

    def gates(self):
        for m in range(1, 9):
            positions = list(range(m))
            first = None
            for _ in range(2):
                rows = gather_real(positions, self.read)
                features = self.features(rows)
                scores, masks = self.decisions(features)
                self.feature_parity(positions, features)
                value = (scores.tobytes(), masks.tobytes())
                require(first is None or value == first, "Exact gate repeats")
                first = value
                del rows, features
            digest = self.reference(positions, scores, masks)
            self.gate_digests.append(digest)
            require(len(self.gate_digests) <= 16, "Fixed16gate contexts")

    def retain(self, positions, features, scores, masks, batch):
        self.phase = "arrival_control"
        self.feature_parity(positions, features)
        self.checkpoint()
        require(
            len(self.retained) < 64
            and sum(len(x[0]) for x in self.retained) + len(positions) <= 64,
            "Bounded64 private outputs",
        )
        self.retained.append(
            (list(positions), scores.copy(), masks.copy(), dict(batch))
        )

    def finish(self, write):
        post_start = self.clocks.continuous()
        self.phase = "after_drain_references"
        self.checkpoint()
        for positions, scores, masks, b in self.retained:
            b.update(reference_intents=1, reference_intent=self.clocks.service())
            write(b)
            self.reference(positions, scores, masks)
            b.update(
                reference_rows=len(positions),
                reference_return=self.clocks.service(),
                control_end=self.clocks.service(),
                status=11,
                digest=hashlib.sha256(scores.tobytes() + masks.tobytes()).digest()[:16],
            )
            write(b)
        self.retained.clear()
        self.phase = "post_gates"
        self.gates()
        require(
            self.gate_digests[:8] == self.gate_digests[8:], "Pre/post gate identities"
        )
        require(
            self.state() == self.initial_state,
            "Frozen parameter/input/scaler/threshold identities",
        )
        self.threads_after = self.core.effective_threads()
        self.close_handle()
        for role in (
            ["membership", "golden", "transform"]
            + list(self.spec["lineage_roles"])
            + [self.entry["name"] + ":" + k for k in ("model", "config", "calibration")]
        ):
            source_bytes(self.repo, self.files[role])
        require(
            self.clocks.continuous() - post_start <= 10_000_000_000,
            "References/post10s",
        )
        self.phase = "closed_verified"
        self.checkpoint()
        quota.CURRENT.write_json(
            self.directory / "consumer-final.json",
            dict(
                valid=True,
                budget=self.budget.__dict__,
                gate_contexts=16,
                exact_pre_post_gate_parity=True,
                all_realized_group_references=True,
                state_identities=self.initial_state,
                threads_before=self.threads_before,
                threads_after=self.threads_after,
                decoder_threads=dict(requested="1", effective="unknown"),
                hdf=self.hdf_metadata,
                phase_observations=self.observations,
                owned_numerical_buffer_bound_bytes=8388608,
                native_workspace_attribution="unvalidated",
                python_heap_attribution="unvalidated",
            ),
        )

    def state(self):
        return dict(
            parameters=self.core.parameter_hash(self.model),
            thresholds=hashlib.sha256(self.thresholds.tobytes()).hexdigest(),
            golden=hashlib.sha256(self.golden.tobytes()).hexdigest(),
            ids=hashlib.sha256(self.ids.tobytes()).hexdigest(),
            scalers=hashlib.sha256(
                self.parameters.aggregate_mean.tobytes()
                + self.parameters.aggregate_std.tobytes()
            ).hexdigest(),
        )

    def close(self):
        try:
            if self.handle is not None:
                self.handle.close()
                self.handle = None
        finally:
            try:
                if self.limiter is not None:
                    self.limiter.restore_original_limits()
            finally:
                if hasattr(self, "fd"):
                    quota.close(self.fd)


def validate_lineage(docs, spec):
    """Pure seven-document validation; every embedded payload link stays inert."""

    def digest(x):
        return hashlib.sha256(
            json.dumps(x, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    manifest, config, split = (
        docs["dev_manifest"],
        docs["transform"],
        docs["split_manifest"],
    )
    science = manifest["scientific"]
    prepared, receipt = docs["prepared"], docs["prepare_receipt"]
    acquire, audit = docs["acquisition"], docs["raw_audit"]
    require(
        manifest["scientific_sha256"]
        == digest(science)
        == spec["dev_scientific_sha256"]
        and science["scope"] == "dev"
        and science["counts"]["train_background"] == 6999
        and science["counts"]["test_background"]
        == science["counts"]["test_signal"]
        == 0,
        "Dev-only lineage",
    )
    require(
        science["config_sha256"]
        == science["files"]["configuration.json"]["sha256"]
        == next(x["sha256"] for x in spec["allowed_files"] if x["role"] == "transform")
        and config == docs["dev_configuration"],
        "Frozen scaler/config binding",
    )
    require(
        science["split_identity_sha256"] == digest(science["split_identity"])
        and science["split_identity"]["array_sha256"]["dev_train_background.npy"]
        == split["artifacts"]["dev_train_background.npy"]["sha256"]
        == spec["membership"]["file_sha256"]
        and split["counts"]["dev_train_background"] == 6999
        and split["counts"] == config["split"]["counts"]
        and science["split_identity"]["development_subset"]
        == split["development_subset"]
        == config["split"]["development_subset"]
        and split["protocol"] == config["split"]["protocol"]
        and split["seed"] == config["split"]["seed"],
        "Original split/source role",
    )
    require(
        all(
            science["split_identity"]["array_sha256"][name]
            == split["artifacts"][name]["sha256"]
            == sha
            for name, sha in config["analysis_provenance"]["split_array_sha256"].items()
        ),
        "Inert split metadata hashes",
    )
    population = receipt["access_audit"]["population"]
    require(
        receipt["status"] == "completed"
        and population["split"] == "train_background"
        and population["dev_only"] is True
        and population["allow_test"] is False
        and population["include_labels"] is False
        and population["status"] == "completed"
        and population["rows"] == population["unique_rows"] == 1024
        and population["ids_sha256"]
        == prepared["source_ids_bytes_sha256"]
        == spec["membership"]["selected_sha256"]
        and prepared["strict_source_order"] is True
        and prepared["manifest_scientific_sha256"] == manifest["scientific_sha256"]
        and prepared["input_file_sha256"] == spec["golden"]["file_sha256"]
        and prepared["input_bytes_sha256"] == spec["golden"]["payload_sha256"],
        "Original golden/preparation roles",
    )
    for doc in (
        config["source_integrity"],
        split["source_integrity"],
        science["source_integrity"],
    ):
        require(
            doc["sha256"] == spec["raw"]["file_sha256"]
            and doc["file_size"] == spec["raw"]["size_bytes"],
            "Raw lineage",
        )
    require(
        acquire["sha256"] == spec["raw"]["file_sha256"]
        and acquire["source"]["record_id"] == 6466204
        and acquire["source"]["version"] == "v5"
        and acquire["verified_checksum"] == spec["raw"]["publisher_md5"]
        and audit["datasets"]["df/block0_values"] == spec["raw"]["audit_schema"],
        "Original acquisition/schema metadata",
    )


def canonical_build_hash(text):
    """Original CPU policy hashes the canonical JSON string, not raw build text."""
    return hashlib.sha256(
        json.dumps(
            text, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def record_initialization_failure(backend, path, exc):
    """Bounded failure evidence; cleanup must proceed even if this cannot write."""
    try:
        backend.checkpoint()
        quota.CURRENT.write_json(
            path,
            dict(
                valid=False,
                initialization_failed=True,
                error_type=type(exc).__name__,
                error=str(exc)[:500],
                phase=backend.phase,
                budget=backend.budget.__dict__,
                phase_observations=backend.observations,
                operational_parity_unperformed=True,
            ),
        )
        return None
    except (OSError, ValueError, AttributeError) as report_exc:
        return type(report_exc).__name__
