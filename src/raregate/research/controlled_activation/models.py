"""Owned synthetic tensors, exact pairing/selection and arm-aware finite states."""

import hashlib
import inspect
import math
import random
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import BatchSampler, DataLoader, RandomSampler, SequentialSampler

from raregate.research.controlled_activation import protocol as p
from raregate.training.autoencoder import EarlyStopping

SHAPES = {
    "encoder.0.weight": (6, 8),
    "encoder.0.bias": (6,),
    "encoder.2.weight": (3, 6),
    "encoder.2.bias": (3,),
    "decoder.0.weight": (6, 3),
    "decoder.0.bias": (6,),
    "decoder.2.weight": (8, 6),
    "decoder.2.bias": (8,),
}
COUNTERS = dict(
    model_instances=0,
    forward_calls=0,
    forward_rows=0,
    reconstruction_computations=0,
    optimizer_steps_started=0,
    optimizer_steps_completed=0,
    optimizer_steps_inflight=0,
    synthetic_calibrations=0,
)


@contextmanager
def deterministic_cpu(seed, threads=1):
    """Historical CPU stream, without touching CUDA/MPS generators or defaults."""
    p.require(
        type(seed) is int and seed in p.SEEDS and threads == 1,
        "Fixed CPU state context",
    )
    python_state, numpy_state = random.getstate(), np.random.get_state()
    previous_threads = torch.get_num_threads()
    deterministic = torch.are_deterministic_algorithms_enabled()
    warn = torch.is_deterministic_algorithms_warn_only_enabled()
    with torch.random.fork_rng(devices=[]):
        try:
            random.seed(seed)
            np.random.seed(seed)
            torch.default_generator.manual_seed(seed)
            torch.set_num_threads(1)
            torch.use_deterministic_algorithms(True)
            yield
        finally:
            random.setstate(python_state)
            np.random.set_state(numpy_state)
            torch.set_num_threads(previous_threads)
            torch.use_deterministic_algorithms(deterministic, warn_only=warn)


def verify_runtime(spec):
    p.validate_config(spec)
    p.require(
        hashlib.sha256(torch.__config__.show().encode()).hexdigest()
        == spec["dependencies"]["torch_build_sha256"],
        "Torch build changed",
    )
    p.require(
        p.file_hash(Path(inspect.getfile(torch.optim.Adam)))
        == spec["dependencies"]["adam_source_sha256"],
        "Adam implementation changed",
    )
    signature = inspect.signature(torch.optim.Adam)
    actual = {k: signature.parameters[k].default for k in p.ADAM}
    actual["betas"] = list(actual["betas"])
    p.require(
        p.digest(actual) == p.digest(p.ADAM), "Incompatible resolved Adam defaults"
    )


def features(values):
    p.require(
        type(values) is np.ndarray
        and values.dtype == np.float32
        and values.ndim == 2
        and values.shape[1] == 8
        and len(values) > 0
        and np.isfinite(values).all(),
        "Owned in-memory synthetic FP32 [N,8] required",
    )
    return values


class ResearchAE(nn.Module):
    def __init__(self, arm, seed, spec):
        super().__init__()
        p.require(
            arm in p.ARMS and type(seed) is int and seed in p.SEEDS, "Fixed arm/seed"
        )
        verify_runtime(spec)
        self.arm, self.seed, self.design = arm, seed, spec["design_digest"]
        activation = nn.ReLU if arm == "nonlinear" else nn.Identity
        self.encoder = nn.Sequential(
            nn.Linear(8, 6, device="cpu", dtype=torch.float32),
            activation(),
            nn.Linear(6, 3, device="cpu", dtype=torch.float32),
        )
        self.decoder = nn.Sequential(
            nn.Linear(3, 6, device="cpu", dtype=torch.float32),
            activation(),
            nn.Linear(6, 8, device="cpu", dtype=torch.float32),
        )
        p.require(sum(v.numel() for v in self.parameters()) == 155, "155 parameters")
        COUNTERS["model_instances"] += 1

    def forward(self, values):
        p.require(
            values.dtype == torch.float32
            and values.device.type == "cpu"
            and values.ndim == 2
            and values.shape[1] == 8
            and len(values) > 0
            and bool(torch.isfinite(values).all()),
            "Finite FP32 CPU forward",
        )
        COUNTERS["forward_calls"] += 1
        COUNTERS["forward_rows"] += len(values)
        COUNTERS["reconstruction_computations"] += 1
        return self.decoder(self.encoder(values))


def parameter_document(model):
    result = []
    p.require(tuple(model.state_dict()) == tuple(SHAPES), "Parameter names/order")
    for name, tensor in model.state_dict().items():
        a = tensor.detach().cpu().numpy()
        p.require(
            a.dtype == np.float32 and a.shape == SHAPES[name] and np.isfinite(a).all(),
            "Finite FP32 parameter shape",
        )
        raw = a.astype("<f4", copy=False).tobytes()
        result.append(
            dict(
                name=name,
                shape=list(a.shape),
                dtype="<f4",
                hex_bytes=raw.hex(),
                sha256=hashlib.sha256(raw).hexdigest(),
            )
        )
    return result


def decode_parameters(rows):
    p.require(type(rows) is list and len(rows) == 8, "Complete parameters")
    states = {}
    for row, (name, shape) in zip(rows, SHAPES.items(), strict=True):
        p.require(
            type(row) is dict
            and set(row) == {"name", "shape", "dtype", "hex_bytes", "sha256"}
            and row["name"] == name
            and row["shape"] == list(shape)
            and all(type(v) is int for v in row["shape"])
            and row["dtype"] == "<f4",
            "Parameter name/order/shape/dtype",
        )
        text = row["hex_bytes"]
        p.require(
            type(text) is str
            and len(text) == math.prod(shape) * 8
            and all(c in "0123456789abcdef" for c in text),
            "Finite bounded byte representation",
        )
        raw = bytes.fromhex(text)
        p.require(
            hashlib.sha256(raw).hexdigest() == row["sha256"], "Parameter byte identity"
        )
        a = np.frombuffer(raw, dtype="<f4").reshape(shape).copy()
        p.require(np.isfinite(a).all(), "Nonfinite parameter bits")
        states[name] = torch.from_numpy(a)
    return states


def initialization(seed, spec):
    with deterministic_cpu(seed, 1):
        model = ResearchAE("nonlinear", seed, spec)
        rows = parameter_document(model)
    return dict(
        kind="synthetic_initialization_v1",
        seed=seed,
        design=spec["design_digest"],
        parameters=rows,
        parameters_digest=p.digest(rows),
    )


def factory(arm, seed, spec, initial):
    p.require(
        set(initial) == {"kind", "seed", "design", "parameters", "parameters_digest"}
        and initial["kind"] == "synthetic_initialization_v1"
        and type(initial["seed"]) is int
        and initial["seed"] == seed
        and initial["design"] == spec["design_digest"]
        and initial["parameters_digest"] == p.digest(initial["parameters"]),
        "Initialization provenance",
    )
    states = decode_parameters(initial["parameters"])
    with deterministic_cpu(seed, 1):
        model = ResearchAE(arm, seed, spec)
        model.load_state_dict(states, strict=True)
        model.initialization_digest = initial["parameters_digest"]
    return model


def artifact(model, *, initialization_digest, selected_epoch):
    p.require(
        type(selected_epoch) is int and selected_epoch >= 1, "Selected complete epoch"
    )
    science = dict(
        model_type="controlled_activation_synthetic_v1",
        scope="synthetic_only",
        arm=model.arm,
        seed=model.seed,
        design=model.design,
        features=list(p.FEATURES),
        layers=[8, 6, 3, 6, 8],
        parameter_count=155,
        initialization_digest=initialization_digest,
        selected_epoch=selected_epoch,
        parameters=parameter_document(model),
    )
    return dict(scientific=science, scientific_sha256=p.digest(science))


def restore_artifact(model, document, *, initialization_digest, selected_epoch):
    expected = {
        "model_type",
        "scope",
        "arm",
        "seed",
        "design",
        "features",
        "layers",
        "parameter_count",
        "initialization_digest",
        "selected_epoch",
        "parameters",
    }
    p.require(
        type(document) is dict and set(document) == {"scientific", "scientific_sha256"},
        "Research artifact envelope",
    )
    s = document["scientific"]
    p.require(
        type(s) is dict
        and set(s) == expected
        and p.digest(s) == document["scientific_sha256"]
        and s["model_type"] == "controlled_activation_synthetic_v1"
        and s["scope"] == "synthetic_only"
        and s["arm"] == model.arm
        and type(s["seed"]) is int
        and s["seed"] == model.seed
        and s["design"] == model.design
        and s["features"] == list(p.FEATURES)
        and s["layers"] == [8, 6, 3, 6, 8]
        and type(s["parameter_count"]) is int
        and s["parameter_count"] == 155
        and s["initialization_digest"] == initialization_digest
        and type(s["selected_epoch"]) is int
        and s["selected_epoch"] == selected_epoch,
        "Wrong/altered research artifact provenance",
    )
    model.load_state_dict(decode_parameters(s["parameters"]), strict=True)
    p.require(parameter_document(model) == s["parameters"], "Restoration byte failure")


def sse(inputs, reconstruction):
    x, y = features(inputs), features(reconstruction)
    p.require(x.shape == y.shape, "Reconstruction shape")
    delta = x.astype(np.float64) - y.astype(np.float64)
    scores = np.sum(delta * delta, axis=1)
    p.require(
        scores.dtype == np.float64
        and np.isfinite(scores).all()
        and (scores >= 0).all(),
        "Finite nonnegative FP64 SSE",
    )
    return scores


def score(model, values):
    values = features(values)
    before = p.digest(parameter_document(model))
    with torch.inference_mode():
        result = sse(values, model(torch.from_numpy(values)).numpy())
    p.require(before == p.digest(parameter_document(model)), "Scoring mutated weights")
    return result


class Selection:
    def __init__(self, model, initial_digest, probe):
        p.require(initial_digest == model.initialization_digest, "Own initialization")
        self.arm, self.seed, self.design = model.arm, model.seed, model.design
        self.initial_digest, self.probe = initial_digest, features(probe).copy()
        self.stopping = EarlyStopping(15, 0.0)
        self.completed_epochs = 0
        self.best = self.best_probe_hash = self.best_digest = None

    def _own(self, model):
        p.require(
            (model.arm, model.seed, model.design) == (self.arm, self.seed, self.design),
            "Other arm checkpoint",
        )

    def update(self, epoch, loss, model, *, complete=True):
        self._own(model)
        p.require(
            complete is True
            and type(epoch) is int
            and epoch == self.completed_epochs + 1
            and type(loss) in (float, int)
            and math.isfinite(loss)
            and loss >= 0,
            "Complete finite sequential selection",
        )
        improving = loss < self.stopping.best_loss
        stop = self.stopping.update(epoch, loss, model)
        self.completed_epochs = epoch
        if improving:
            self.best = artifact(
                model, initialization_digest=self.initial_digest, selected_epoch=epoch
            )
            self.best_probe_hash = hashlib.sha256(
                score(model, self.probe).tobytes()
            ).hexdigest()
            self.best_digest = self.best["scientific_sha256"]
        return stop

    def restore(self, model, document=None):
        self._own(model)
        p.require(
            self.best is not None and self.completed_epochs > 0,
            "Missing selected complete state",
        )
        document = self.best if document is None else document
        p.require(
            document == self.best
            and document.get("scientific_sha256") == self.best_digest,
            "Other/altered selected checkpoint",
        )
        restore_artifact(
            model,
            document,
            initialization_digest=self.initial_digest,
            selected_epoch=self.stopping.best_epoch,
        )
        p.require(
            hashlib.sha256(score(model, self.probe).tobytes()).hexdigest()
            == self.best_probe_hash,
            "Selected-state score identity",
        )
        result = dict(
            selected_epoch=self.stopping.best_epoch,
            complete_epochs=self.completed_epochs,
            checkpoint_digest=document["scientific_sha256"],
            selected_bytes_verified=True,
            selected_score_identity=True,
            stop_reason="patience"
            if self.stopping.bad_epochs >= 15
            else "synthetic_cap",
        )
        result["parameter_digest"] = p.digest(parameter_document(model))
        model.restoration_proof = dict(result)
        model.eval()
        return result


class IndexedDataset:
    def __init__(self, values):
        self.values = torch.from_numpy(features(values))

    def __len__(self):
        return len(self.values)

    def __getitem__(self, indices):
        return self.values[indices], torch.tensor(indices, dtype=torch.int64)


class PairedLoader:
    """Hash only emitted batches; shared sampler/loader RNG exactly as historical."""

    def __init__(self, values, *, arm, seed, shuffle=True):
        p.require(type(seed) is int and seed in p.SEEDS, "Fixed loader seed")
        p.require(arm in p.ARMS, "Fixed loader arm")
        self.n, self.seed = len(features(values)), seed
        self.arm = arm
        self.feature_hash = hashlib.sha256(values.tobytes()).hexdigest()
        dataset = IndexedDataset(values)
        generator = torch.Generator().manual_seed(seed)
        sampler = (
            RandomSampler(dataset, generator=generator)
            if shuffle
            else SequentialSampler(dataset)
        )
        self.loader = DataLoader(
            dataset,
            sampler=BatchSampler(sampler, 4096, drop_last=False),
            batch_size=None,
            num_workers=0,
            generator=generator,
        )
        self.epochs, self.pending = [], None

    def __iter__(self):
        p.require(self.pending is None, "Previous epoch incomplete")
        seen, hasher, count, batches = (
            np.zeros(self.n, dtype=bool),
            hashlib.sha256(),
            0,
            [],
        )
        self.pending = dict(count=0, complete=False)
        for values, indices in self.loader:
            ids = indices.numpy()
            p.require(
                ids.ndim == 1
                and len(ids) == len(values)
                and (ids >= 0).all()
                and (ids < self.n).all()
                and len(np.unique(ids)) == len(ids)
                and not seen[ids].any(),
                "Row coverage/uniqueness",
            )
            p.require(
                len(values) == min(4096, self.n - count),
                "Complete canonical batch/tail",
            )
            seen[ids] = True
            hasher.update(ids.astype("<i8", copy=False).tobytes())
            count += len(ids)
            batches.append(len(ids))
            self.pending["count"] = count
            yield values
        p.require(count == self.n and seen.all(), "Incomplete emitted epoch")
        self.epochs.append(
            dict(
                seed=self.seed,
                epoch=len(self.epochs) + 1,
                count=count,
                unique=count,
                batch_sizes=batches,
                order_sha256=hasher.hexdigest(),
                complete=True,
            )
        )
        self.pending = None


def accept_pair(nonlin, linear, initial_nonlin, initial_linear):
    p.require(
        nonlin.arm == "nonlinear"
        and linear.arm == "linear"
        and nonlin.n == linear.n
        and nonlin.feature_hash == linear.feature_hash
        and nonlin.seed == linear.seed
        and nonlin.seed in p.SEEDS
        and initial_nonlin == initial_linear
        and nonlin.pending is None
        and linear.pending is None
        and nonlin.epochs
        and linear.epochs,
        "Complete matching pair",
    )
    common = min(len(nonlin.epochs), len(linear.epochs))
    p.require(
        nonlin.epochs[:common] == linear.epochs[:common],
        "Actual consumed permutation mismatch",
    )
    return dict(
        common_epochs=common,
        identical_consumed_orders=True,
        missing_later_epochs=abs(len(nonlin.epochs) - len(linear.epochs)),
    )


class SyntheticProvider:
    def __init__(self, arrays):
        self.arrays = {k: features(v).copy() for k, v in arrays.items()}
        self.calls = []

    def get(self, role):
        self.calls.append(role)
        return self.arrays[role].copy()


def role_values(provider, role, purpose):
    expected = dict(fit=p.ROLES[0], selection=p.ROLES[1], calibration=p.ROLES[2])
    p.require(
        purpose in expected and role == expected[purpose],
        "Role forbidden before provider call",
    )
    p.require(type(provider) is SyntheticProvider, "In-memory synthetic provider only")
    return features(provider.get(role))


def optimizer(model):
    options = dict(p.ADAM, betas=tuple(p.ADAM["betas"]))
    return torch.optim.Adam(model.parameters(), lr=0.001, **options)


class SyntheticSteps:
    """Fixed per-fixture profile; fresh objects in unit tests, one per native call."""

    def __init__(self):
        self.started = {key: 0 for key in p.ORDER}

    def start(self, model):
        key = (model.arm, model.seed)
        p.require(
            key in self.started and self.started[key] < 2,
            "Two synthetic steps per arm/seed",
        )
        self.started[key] += 1


def epoch_loss(
    model, loader, *, opt=None, budget=None, check=lambda: None, notify=lambda: None
):
    model.train(opt is not None)
    total, count = 0.0, 0
    before = p.digest(parameter_document(model)) if opt is None else None
    with torch.set_grad_enabled(opt is not None):
        for values in loader:
            check()
            if opt is not None:
                p.require(
                    type(budget) is SyntheticSteps,
                    "Bounded synthetic optimizer profile required",
                )
                opt.zero_grad(set_to_none=True)
            reconstruction = model(values)
            loss = nn.functional.mse_loss(reconstruction, values)
            p.require(
                bool(torch.isfinite(loss))
                and bool(torch.isfinite(reconstruction).all()),
                "Finite loss",
            )
            if opt is not None:
                loss.backward()
                budget.start(model)
                COUNTERS["optimizer_steps_started"] += 1
                COUNTERS["optimizer_steps_inflight"] += 1
                notify()
                opt.step()
                COUNTERS["optimizer_steps_completed"] += 1
                COUNTERS["optimizer_steps_inflight"] -= 1
                notify()
            total += loss.item() * len(values)
            count += len(values)
            check()
    p.require(
        count > 0 and (before is None or before == p.digest(parameter_document(model))),
        "Selection mutation/empty epoch",
    )
    return total / count


def calibrate(model, provider, role, restored):
    p.require(
        not hasattr(model, "calibration_digest"),
        "One synthetic calibration per restored model",
    )
    p.require(
        type(restored) is dict
        and restored == getattr(model, "restoration_proof", None)
        and restored["selected_bytes_verified"]
        and restored["selected_score_identity"]
        and restored["parameter_digest"] == p.digest(parameter_document(model)),
        "Restore before calibration",
    )
    values = role_values(provider, role, "calibration")
    values_score = score(model, values)
    thresholds = [
        dict(
            alpha=a,
            index=math.ceil((len(values_score) - 1) * (1 - a)),
            value=float(np.quantile(values_score, 1 - a, method="higher")),
        )
        for a in p.ALPHAS
    ]
    COUNTERS["synthetic_calibrations"] += 1
    record = dict(
        kind="controlled_activation_synthetic_calibration_v1",
        scope="synthetic_only",
        arm=model.arm,
        seed=model.seed,
        design=model.design,
        state_digest=p.digest(parameter_document(model)),
        quantile="higher",
        decision="score > threshold",
        primary_alpha=0.001,
        count=len(values_score),
        thresholds=thresholds,
        fixture_sha256=hashlib.sha256(values.tobytes()).hexdigest(),
    )
    model.calibration_digest = p.digest(record)
    return dict(record=record, sha256=p.digest(record))


def decisions(model, values, calibrated):
    r = calibrated["record"]
    p.require(
        calibrated["sha256"]
        == p.digest(r)
        == getattr(model, "calibration_digest", None)
        and r["kind"] == "controlled_activation_synthetic_calibration_v1"
        and r["scope"] == "synthetic_only"
        and (r["arm"], r["seed"], r["design"]) == (model.arm, model.seed, model.design)
        and r["state_digest"] == p.digest(parameter_document(model))
        and r["quantile"] == "higher"
        and r["decision"] == "score > threshold"
        and r["primary_alpha"] == 0.001
        and [t["alpha"] for t in r["thresholds"]] == list(p.ALPHAS)
        and all(math.isfinite(t["value"]) and t["value"] >= 0 for t in r["thresholds"]),
        "Threshold provenance",
    )
    return score(model, values) > r["thresholds"][-1]["value"]
