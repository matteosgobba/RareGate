<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/branding/raregate-logo-v2-dark.png">
    <img src="assets/branding/raregate-logo-v2.png" alt="RareGate" width="520">
  </picture>
</p>

<p align="center">
  <strong>Hardware-aware anomaly detection for LHC event selection</strong>
</p>

<p align="center">
  <a href="#results">Results</a> &nbsp;·&nbsp;
  <a href="#getting-started">Getting started</a> &nbsp;·&nbsp;
  <a href="docs/scientific-report.md">Scientific report</a>
</p>

RareGate studies the trade-off between anomaly detection and computational cost
in event selection inspired by the Large Hadron Collider (LHC). It compares
compact neural networks with classical statistical methods on simulated
collisions, measuring signal acceptance and CPU time.

The aim is to test whether a smaller model still offers a useful advantage when
feature construction, scoring and selection are measured together.

## How it works

1. **Prepare the events.** Verify public HDF5 data, remove exact duplicates and
   separate training, selection, calibration and evaluation. The final ADC2021
   study uses 12 aggregates of missing transverse momentum, electrons, muons
   and jets.
2. **Compare the detectors.** Train compact and reference autoencoders
   (271 and 1,999 parameters) on background events, alongside three-component
   PCA and regularized Mahalanobis distance. Fit preprocessing on training data
   only; reserve signals for evaluation.
3. **Measure quality and cost.** Freeze background-calibrated cuts, compare
   signal efficiencies with paired uncertainty bounds, and measure CPU cost
   across batch sizes. Check numerical parity and selection effects.

Earlier [LHC Olympics (LHCO) studies](docs/earlier-studies.md) cover
anomaly-detection baselines, synthetic queues and bounded streaming prototypes.

## Results

The final ADC2021 comparison uses **1,000,000 background events and 40,000 per
signal**, with a lepton prefilter. Below are signal efficiencies at a **1% target
background acceptance**, with CPU times per batch of 32 events:

| Method | A → 4ℓ | LQ → bτ | CPU (µs) |
|:--|--:|--:|--:|
| Compact AE | 37.33% | 6.90% | 284.9 |
| Reference AE | 50.53% | 10.63% | 295.4 |
| PCA3 | 22.72% | 11.91% | 266.3 |
| Mahalanobis | 50.13% | 15.84% | 269.1 |

CPU times cover in-memory objects → features/scaling → scores, masks and owned
outputs. Data loading and HDF5 I/O are excluded; these are not detector latencies.

![Signal efficiency versus measured joint CPU cost for the ADC comparison](results/figures/quality-cost.png)

*Signal efficiency versus joint CPU cost. Vertical intervals include calibration
uncertainty; points use the frozen empirical cuts.*

**The smaller autoencoder lost sensitivity without meeting the required CPU
saving.** The paired bounds excluded 90% retention of reference efficiency on
both signals, and the joint cost reduction fell short of 25%.

Mahalanobis is the recommended baseline for these features and this workload:
it outperformed compact on both signals. Its absolute 15% LQ utility target
remains unresolved, with a simultaneous bound of **14.65–16.97%**. No method
met all the preregistered quality and cost requirements.

<details>
<summary>Measurement details</summary>

Neural efficiencies average three separately trained seeds, without ensembling.
CPU times are medians of eight block means from the recorded single-thread
macOS arm64 run, with neural seeds averaged within each block. The figure's
intervals bound efficiency at the population background quantile, including
calibration uncertainty.

The [scientific report](docs/scientific-report.md) provides the uncertainty analysis,
selection profiles, timing boundaries and result tables.

</details>

## Getting started

Use **Python 3.11 or 3.12** (3.12 recommended) and Git. A CPU is sufficient.
The installation includes NumPy, scikit-learn, PyTorch, HDF5 support, Matplotlib
and development tools.

```bash
git clone https://github.com/matteosgobba/RareGate.git
cd RareGate
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data,analysis]"
python scripts/smoke_test.py
```

The smoke test checks a small tensor computation. On Windows, activate with
`.venv\Scripts\activate`. For
CPU-only Linux, install PyTorch from its
[CPU wheel index](https://download.pytorch.org/whl/cpu) before the editable install.

To run the development checks:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

CI is configured for Python 3.11 and 3.12. Tests use generated inputs.

Data, processed arrays and most models stay outside Git. For experiment setup,
see the
[ADC protocol](docs/experiment-design.md),
[data preparation](docs/data-preparation.md) and
[usage guide](docs/usage-guide.md).

## Repository layout

```text
src/raregate/  Data, models, training, evaluation, benchmarks and streaming
configs/      Data, model and optional-runtime specifications
scripts/      Data preparation, validation and diagnostics
tests/unit/   Generated numerical, model and data-contract tests
results/      Selected scientific figures and numerical tables
artifacts/    Selected small historical model artifacts
docs/         Scientific findings, methodology, data and usage guides
data/         Local datasets and derived stores; excluded from version control
assets/       Project branding
```

Further reading: [evaluation methods](docs/evaluation-methods.md) ·
[installation and workflow](docs/usage-guide.md).

## Scope and limitations

Results depend on the simulation, object preselection, features and training
budgets. They do not establish physical LHC rates or discovery significance;
the software is **not a deployment-ready trigger**. Engineering prototypes
retain the limitations documented in their reports.

RareGate is an independent project with no official affiliation with or
endorsement by CERN, ATLAS, CMS or CERN openlab.

## Author and acknowledgements

Created by **Matteo Sgobba** · [GitHub](https://github.com/matteosgobba) ·
[LinkedIn](https://www.linkedin.com/in/matteosgobba/)

This work uses public datasets from the
[ADC2021 authors](https://mpp-hep.github.io/ADC2021/)
([data descriptor](https://doi.org/10.1038/s41597-022-01187-8)) and the
[LHC Olympics 2020 creators](https://doi.org/10.5281/zenodo.6466204), with NumPy,
scikit-learn, PyTorch, h5py and Matplotlib. Dataset versions and provenance are
recorded in the experiment protocols.

**License:** [MIT](LICENSE) for the code; **CC BY 4.0** for the referenced datasets,
with their respective attribution requirements.
