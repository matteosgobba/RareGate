# LatentTrigger

**Hardware-Aware Machine Learning for Real-Time LHC Event Selection**

LatentTrigger is an independent research and engineering project inspired by the
computational challenges of real-time event selection at the Large Hadron
Collider (LHC). It will investigate how anomaly-detection quality changes when
models must meet strict latency, throughput, and memory constraints.

## Motivation

Event selection motivates studying models that are both scientifically useful
and computationally practical. LatentTrigger will treat model quality and
deployment cost as joint design considerations, using LHC-like event data and
clearly stated experimental assumptions.

## Research question

> How much anomaly-detection performance can be retained when machine-learning
> models are optimized for real-time LHC event selection under strict
> computational constraints?

## Project scope

The planned work spans scientific event-data preparation, anomaly-detection
models, scientific evaluation and bias analysis, and hardware-aware inference.
Apple Silicon CPU/GPU measurements will be the initial hardware focus. Later
phases may investigate heterogeneous inference, NVIDIA hardware, and FPGA-oriented
deployment.

## Planned methodology

1. Select and document a suitable dataset, event representation, and reproducible
   preparation procedure.
2. Establish anomaly-detection baselines, then investigate compact autoencoders
   and particle/set models, adding attention only when justified.
3. Evaluate detection performance and potential scientific biases with explicit
   data splits and evaluation assumptions.
4. Measure latency, throughput, and memory under documented hardware and runtime
   conditions, comparing model quality with computational cost.
5. Investigate optimized runtimes, quantization, and a trigger-like event-stream
   simulator in later phases.

## Current status

Phase 0.1 establishes the Python package, development tools, tests, CI, data and
results policies, and a CPU/MPS environment diagnostic. The package version is
`0.1.0`. Task 0002 defines the data foundation using the corrected LHC Olympics
2020 R&D particle dataset (Zenodo v5). The [data design](docs/data-design.md)
documents the dataset comparison, background-only protocol, representations, and
provenance plan. Verified acquisition is implemented, and the pinned R&D source
was locally downloaded and checksum-verified in Task 0003. The
[bounded raw audit](docs/raw-data-audit.md) records its schema and integrity checks.
Task 0004 completes the full integrity/duplicate scan, deterministic splits and
[training-background EDA](docs/training-data-eda.md). The
[preprocessing contract](docs/preprocessing-contract.md) is frozen. Task 0005
implements the [deterministic pipeline](docs/preprocessing-pipeline.md), and both
dev and full canonical stores have been locally generated and verified. Task 0006
implements the [PCA baseline](docs/pca-baseline.md), background-only diagnostics
and calibrated thresholds under the [evaluation protocol](docs/evaluation-protocol.md).
Task 0007 adds a frozen [compact autoencoder](docs/compact-autoencoder.md),
reproducible CPU training and separate MPS compatibility checks. Real test
performance remains intentionally embargoed. Task 0008 closes
[convergence under the frozen patience rule](docs/autoencoder-convergence.md);
v2 is now the canonical compact AE. Task 0009 defines a
[478-parameter particle/set autoencoder design](docs/particle-set-baseline-design.md)
with local bottlenecks, pooled context and a linear-cost reconstruction score.
Task 0010 [implements the unchanged design](docs/particle-set-baseline.md), with
247 passing synthetic tests. Its launch gate failed at 3.69 GiB available memory
versus the frozen 8 GiB minimum, before real reader construction or dev updates.
Canonical training, reproduction, freeze and calibration remain pending.
[Task 0011](docs/particle-set-resource-recovery.md) adds a bounded preflight and
one fixed recovery route. The explicit2026-10-07 resumption after reboot/manual
preparation still failed the8GiB launch test at4.6248–4.6819GiB; continuing4GiB,
RSS and native ceilings passed. No recovery attempt was reserved. All real
particle stages remain pending; these records are committed.
[Task 0012](docs/particle-memory-policy-review.md) adds a separate provisional
launch profile of 4.5 GiB while retaining the 4 GiB floor and all other limits.
Its single check fails both at 2.5443–2.6967 GiB; no reader/dev phase ran.
That pilot did not activate v2; the original scientific config and8GiB policy
remain preserved. [Task0013](docs/particle-host-readiness.md) delivered stdlib
supervision and initial accounting. Its later external study is now reconciled:
reader/full custody and bounded-dev activation passed;1024unique events/96steps
completed, then conservative throughput749.343s failed180s. The slot is consumed;
canonical training/calibration remain pending.
[Task0014](docs/particle-monitor-performance.md) adds a separate cached-binding
monitor preserving all observation/limit/scientific contracts, with471synthetic
tests and exact numerical parity. Fixed shared-host timings improve isolated
collection/checks but show no complete-workload gain(0.382→0.388s). No new real
execution. [Task0015](docs/particle-bounded-sampling.md) implements explicitly
versioned50ms host sampling/≤100ms query-start age with fresh process checks.
Final532synthetic tests pass; paired complete-workload gain2.14× misses the3×
real-budget prerequisite. No readiness/real slot/new data/update; original96steps
remain consumed and canonical particle training/calibration remain pending.
[Task0016](docs/particle-runtime-characterization.md) prospectively replaces that
synthetic admission prerequisite for one diagnostic characterization, preserving
its failed result and the real180s target. Separate authorization adopts unchanged
v4;576synthetic tests pass. One automatic readiness guard observes3.558060GiB and
fails the4GiB floor before data/updates. The shared single replacement additional
slot remains unreserved; a reviewed optional Terminal route is available in the
report, without app closure or dedicated use. Canonical stages remain pending.
The later Task0016 manual check separately failed pressureWARN2 with no admitted
available-memory sample. [Task0017](docs/particle-readiness-workflow.md) reconciles
that result and delivers repeatable explicit readiness checks plus a separate
fresh-check run action sharing the same canonical Task0016 slot.612synthetic
tests pass; one check-only integration3.705841GiB fails the floor,0new real work.
A failed safe check no longer needs another task/commit; no automatic polling.
Engineering supports normal Mac use with apps open, without a dedicated window.
The [living project memory](docs/project-memory.md) maintains current decisions,
evidence, limitations and direction.
Development records follow the
[task protocol](docs/development.md)
and [handoff index](docs/handoffs/README.md).

## Repository structure

```text
latent-trigger/
├── .github/workflows/ci.yml     # CPU-only lint and test jobs
├── configs/data/               # Frozen data decisions and fitted statistics
├── data/README.md              # Local dataset policy
├── docs/                       # Data design, development protocol, task records
├── notebooks/exploration/      # Future exploratory notebooks
├── results/
│   ├── figures/
│   ├── tables/
│   └── benchmarks/
├── scripts/smoke_test.py        # Lightweight PyTorch diagnostic
├── scripts/analyze_training_data.py # Chunked scan, splits and training-only EDA
├── scripts/validate_preprocessing.py # Dev reconstruction and reproducibility checks
├── src/latenttrigger/
│   ├── __init__.py
│   ├── data/acquisition.py      # Pinned, verified LHCO download CLI
│   ├── data/preprocessing.py    # Frozen transforms and verified ragged stores
│   └── utils/device.py          # MPS-first, CPU fallback selection
├── tests/
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

Empty working directories are retained with `.gitkeep` files. Downloaded and
processed data stay under `data/` and are ignored by Git. Generated outputs under
`results/` are also ignored by default. Later, selected final figures and small
result tables can be committed deliberately under `results/figures/final/` and
`results/tables/final/`; these directories are reserved for curated artifacts.
Checkpoints and large experiment artifacts must remain local.

## Installation

Use Python **3.12** for the primary development environment. The supported range
is **3.11–3.12** (`>=3.11,<3.13`), a conservative range with stable PyTorch macOS
ARM64 wheels. Both versions are covered by CI. Use a native ARM64 Python on Apple
Silicon; a standard virtual environment and pip are sufficient.

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data]"
python -c "import latenttrigger; print(latenttrigger.__version__)"
```

Project metadata and dependencies live in `pyproject.toml`. Runtime dependencies
are PyTorch, NumPy and scikit-learn (PCA and mature evaluation metrics). NumPy also
prevents a missing-NumPy warning during PyTorch initialization. The `dev` extra
adds pytest and Ruff. Hatchling builds the `src/`
package and reads the version from `src/latenttrigger/__init__.py`.
The optional `data` extra adds h5py and the source's required Blosc decoder,
hdf5plugin, for raw auditing/preprocessing and synthetic HDF integration tests.
Acquisition itself uses the Python standard library.
The optional `analysis` extra adds Matplotlib for EDA figures; see
[the data workflow](data/README.md) for analysis installation and reproduction.
Dependency ranges allow compatible updates; exact experiment environments will
be recorded when experiments are introduced.

The macOS PyTorch wheel provides CPU and MPS support. MPS availability depends on
the installed PyTorch build, macOS version, and hardware. The project selects CPU
when MPS is unavailable.

For a CPU-only Linux environment, install the CPU wheel before the project to
avoid downloading GPU runtime dependencies:

```bash
python -m pip install "torch>=2.6,<3" --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[dev,data]"
```

## Apple Silicon / MPS diagnostic

With the project environment active, run:

```bash
python scripts/smoke_test.py
```

The diagnostic reports the PyTorch version, selected device, and MPS availability.
It creates a small float32 tensor, moves it to the selected device, checks a
deterministic computation, and prints `Smoke test passed.` only after successful
execution. It downloads no data and trains no model.

The reusable device utility is available as:

```python
from latenttrigger.utils.device import get_device

device = get_device()
```

## Dataset acquisition

```bash
python -m latenttrigger.data.acquisition
```

The command verifies the pinned source before accepting or reusing it. Data and
local manifests remain ignored. See [the acquisition workflow](data/README.md)
for installation, verification, safe replacement, and bounded-audit commands.

With the Task 0004 split artifacts present, build the convenience subset first:

```bash
python -m latenttrigger.data.preprocessing --scope dev
```

The [preprocessing workflow](docs/preprocessing-pipeline.md) documents full builds,
independent verification, bounded reading and the test embargo. Generated arrays
and manifests remain local.

## PCA baseline

With the verified full processed store present:

```bash
python -m pip install -e ".[dev,data,analysis]"
python -m latenttrigger.models.pca --config configs/models/pca_baseline.json
```

This fits training background, selects six PCA components by the 95% training
variance rule, and calibrates/checks background thresholds. It never scores real
test populations. See [the measured report](docs/pca-baseline.md) for results,
reproduction and [the evaluation contract](docs/evaluation-protocol.md).

## Compact autoencoder

With the verified full store and existing analysis extra installed:

```bash
python -m latenttrigger.training.convergence
```

The canonical 155-parameter model trains on CPU, selects its epoch using
selection background, then calibrates thresholds on separate calibration
background. See [the report](docs/compact-autoencoder.md) for reproduction,
the historical v1 artifact and MPS smoke mode. The
[convergence report](docs/autoencoder-convergence.md) records finalized canonical v2;
real tests remain held out.

## Testing

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

Device-selection tests simulate both MPS availability states. CPU tensor and
diagnostic tests perform real computations while forcing the CPU fallback, so
the suite works on ordinary CPU-only CI runners. GitHub Actions runs these checks
on pushes and pull requests for Python 3.11 and 3.12.

To format code during development, run `python -m ruff format .`.

## Roadmap

- [x] Phase 0.1: package foundation, tooling, tests, CI, and CPU/MPS diagnostic.
- [x] Task 0002: select the dataset and define the data/history protocols.
- [x] Task 0003: verified R&D acquisition and bounded raw-schema audit.
- [x] Task 0004: training-background EDA, duplicate-safe splits and schema validation.
- [x] Task 0005: deterministic preprocessing; dev/full stores locally verified.
- [x] Task 0006: PCA baseline and background evaluation; real test populations embargoed.
- [x] Task 0007: compact autoencoder, reproducible CPU model and background calibration.
- [x] Task 0008: convergence closure; canonical v2 selected with unchanged patience rule.
- [x] Task 0009: compact particle/set design, exact loss/score and future resource gates.
- [x] Task 0010: particle/set implementation and synthetic validation; launch gate failed, canonical baseline pending.
- [x] Task 0011: bounded recovery routing/readiness; host still blocks launch, no recovery data attempt.
- [x] Task 0012: launch admission reviewed; provisional 4.5 GiB requirement still blocked, zero readers/dev updates.
- [x] Task0013: lightweight supervision delivered; later external study consumed96steps, passed memory and failed throughput.
- [x] Task0014: external receipts reconciled; v3 resource instrumentation tested on synthetic inputs, no new real access.
- [x] Task0015: bounded-age v4 tested; synthetic2.14×gain below3×, no real revalidation unlocked.
- [x] Task0016: prospective diagnostic admission reviewed; automatic readiness blocked, zero new real data/steps.
- [x] Task0017: independent user-triggered check history/shared-slot run action; manualWARN reconciled, one check-only integration, no real work.
- [ ] Reconcile future user-triggered characterization receipts; actual-policy artifacts/canonical authorization remain separate.
- [ ] Study scientific biases and compare performance with computational cost.
- [ ] Benchmark Apple Silicon CPU/GPU latency, throughput, and memory.
- [ ] Explore heterogeneous inference, ONNX Runtime, CoreML, and quantization.
- [ ] Build a trigger-like event-stream simulator.
- [ ] Investigate CUDA/TensorRT on Linux/NVIDIA hardware in later phases.
- [ ] Optionally explore FPGA-oriented deployment with hls4ml.

## Disclaimer

LatentTrigger is an independent project. It is not an official CERN, ATLAS, CMS,
or CERN openlab project and does not imply affiliation with or endorsement by
those organizations. Future trigger-like experiments will be research
approximations whose assumptions and limitations must be documented.

The software is released under the [MIT License](LICENSE).
