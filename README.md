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
2. Establish anomaly-detection baselines, then investigate autoencoders and
   particle/set-based Transformer models.
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
[bounded raw audit](docs/raw-data-audit.md) records its schema and integrity checks;
preprocessing and splits are not implemented yet. Development records follow the
[task protocol](docs/development.md)
and [handoff index](docs/handoffs/README.md).

## Repository structure

```text
latent-trigger/
├── .github/workflows/ci.yml     # CPU-only lint and test jobs
├── configs/                    # Future experiment configuration
├── data/README.md              # Local dataset policy
├── docs/                       # Data design, development protocol, task records
├── notebooks/exploration/      # Future exploratory notebooks
├── results/
│   ├── figures/
│   ├── tables/
│   └── benchmarks/
├── scripts/smoke_test.py        # Lightweight PyTorch diagnostic
├── src/latenttrigger/
│   ├── __init__.py
│   ├── data/acquisition.py      # Pinned, verified LHCO download CLI
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
python -m pip install -e ".[dev]"
python -c "import latenttrigger; print(latenttrigger.__version__)"
```

Project metadata and dependencies live in `pyproject.toml`. Runtime dependencies
are PyTorch and NumPy; NumPy prevents a missing-NumPy warning during PyTorch
initialization. The `dev` extra adds pytest and Ruff. Hatchling builds the `src/`
package and reads the version from `src/latenttrigger/__init__.py`.
The optional `data` extra adds h5py and the source's required Blosc decoder,
hdf5plugin, for raw auditing. Acquisition itself uses the Python standard library.
Dependency ranges allow compatible updates; exact experiment environments will
be recorded when experiments are introduced.

The macOS PyTorch wheel provides CPU and MPS support. MPS availability depends on
the installed PyTorch build, macOS version, and hardware. The project selects CPU
when MPS is unavailable.

For a CPU-only Linux environment, install the CPU wheel before the project to
avoid downloading GPU runtime dependencies:

```bash
python -m pip install "torch>=2.6,<3" --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[dev]"
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
- [ ] Task 0004: training-background EDA and schema validation.
- [ ] Implement reproducible scientific preprocessing after the audit.
- [ ] Establish anomaly-detection baselines and scientific evaluation.
- [ ] Investigate autoencoders and particle/set-based Transformer models.
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
