# Task 0006 — PCA Baseline and Evaluation Framework

## Metadata

- Date: 2026-10-05, Europe/Rome
- Status: completed locally; awaiting user review/commit/push
- Phase: first anomaly-detection baseline, background-only calibration/evaluation
- Branch/upstream: main / origin/main
- Base commit: `cb079ecb44163c858199b71ffd1e4a0a1e335390`
- Environment: macOS 26.6.2 ARM64, user-specified M5, 16 GiB RAM,
  Python 3.12.12, NumPy 2.5.3, scikit-learn 1.9.1, SciPy 1.18.1,
  PyTorch 2.14.1, Matplotlib 3.11.2, pytest 9.1.1, Ruff 0.16.10.

## Objective / Scope

Fit and freeze PCA on the existing eight standardized full-event aggregates;
training-only component rule; independent background validation and threshold
calibration; reusable finite-sample metrics tested with synthetic scores. Prepare
future audited final evaluation without executing it on real tests. No autoencoder,
Transformer, signal-proxy experiment, optimization search or hardware benchmark.

## Inspection

Starting tree clean. Tasks 0001–0005 committed; HEAD cb079ec is Task 0005.
Read development/data design, preprocessing contract/pipeline, EDA, Task 0005
handoff, exact config, processed reader and relevant source. Confirmed full store
and frozen role counts. Initial free storage 256,266,539,008 bytes. No unrelated
changes existed. Existing fitted preprocessing configuration and old handoffs
remain unchanged; the index confirms Task 0005's actual commit.

## Changes / Files

Created:

- `configs/models/pca_baseline.json` (preregistered modeling/evaluation choices).
- `src/latenttrigger/models/{__init__,pca,background,reporting}.py`.
- `src/latenttrigger/evaluation/{__init__,metrics,thresholds,run}.py`.
- `tests/test_pca.py`, `tests/test_evaluation.py`.
- Task 0006 prompt/handoff, `docs/pca-baseline.md`, `docs/evaluation-protocol.md`.
- Curated two PNG figures, two CSV tables and scientific results JSON under
  `results/{figures,tables}/final/task0006-pca-*`.

Modified: `pyproject.toml` (one modeling dependency), `README.md`, handoff index,
processed reader (guarded feature-only batches) and its test file (one new test).
No source/preprocessing output/config changes. Generated models/score arrays/
run manifests/logs/cache remain ignored under data.

## Technical Decisions / Dependencies

Add **scikit-learn>=1.5,<2** as a modeling runtime dependency, following existing
bounded-major ranges; no custom PCA solver or PyTorch PCA. Installed native ARM64
1.9.1 plus required transitive SciPy/joblib/threadpoolctl/narwhals/cloudpickle.
No new plotting framework, pandas, experiment tracker, storage dependency or
pickle artifact. The existing analysis extra supplies Matplotlib; `--no-plots`
works without it. CI already installs runtime plus dev/data and uses synthetic
fixtures; its configuration was not changed.

Input is existing FP32 `event_features`, exactly: multiplicity, scalar_pt,
max_pt, pt_balance, weighted_eta_mean, weighted_eta_std, pt_concentration,
massless_event_mass. Task 0004 preprocessing means/stds were fitted on training
background only; no refit occurred. Feature-only mmap batches use the existing
split/truth guards and avoid reading full particle records for compact modeling.

PCA uses full SVD, float64 arithmetic, internal mean centering, no whitening or
randomized solver. Fit all eight axes for transparent spectrum; choose smallest
k with training cumulative variance >=95%. The candidate target was recorded
before background validation/calibration; the measured training spectrum confirmed
it was nonpathological, so no alternative criterion was needed. Reject full-rank
selection instead of silently creating a zero residual. Selection diagnostics
never retune k. Score = squared L2 reconstruction residual summed over all eight
channels, larger means more anomalous. Internal PCA centering is a model parameter,
not a replacement preprocessing scaler.

Thresholds use calibration-background higher empirical quantiles and strict
`score > threshold`; ties are handled conservatively. Selection background checks
frozen thresholds independently. Generic metrics use scikit-learn ROC/AP, attainable
ROC points without interpolation, counts/resolution/Wilson95 intervals. Zero
empirical FPR reports null rejection and exact one-sided95 upper bound, not infinity.
No p-value searches; NumPy ECDF KS distance describes background stability.

## Provenance / Model Artifacts

Full processed schema1 scientific SHA-256:
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`.
Frozen preprocessing config:
`2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`.
Split identity:
`74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea`.
Raw source SHA-256:
`5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`,
MD5 `629789d55813be3860781b084ae7f1de`, Zenodo v5 DOI 10.5281/zenodo.6466204.
Run/model provenance binds these identities, source record, full model config,
feature order, training count, library version and code base/dirty module hashes.
Transparent model.json stores mean, all eight axes, eigenvalues/ratios and chosen
k. Build timestamps/environment/timings are separate from scientific identity;
no absolute machine paths. Small numerical artifacts stay locally readable JSON.

Model scientific SHA-256: `d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f`.
Results scientific SHA-256: `285a254847424870b5bee08e5a218733dcbe553ff7a4d00ec5c9493288600ccb`.
Model config canonical-JSON SHA-256: `e61e43bc57afc010286bf2b1deff91167b4951644d52d882ecbd1cf10f938f95`.

## Results

Fit population **699,957 train-background events**, eight features, **k=6**.
Training explained-variance ratios (all eight):

`0.3219324231546216, 0.2252978910618275, 0.1439153392022868, 0.1250002341781398, 0.112100546985104, 0.05045443005093641, 0.01431746903759137, 0.006981666329492553`.

First five cumulative=0.928246434582; first six=0.978700864633. No signal performance influenced this choice.

| Background population | N | Mean | Std | Median | p99 | p99.9 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train_background | 699957 | 0.1703930829 | 0.3264928276 | 0.09292943414 | 1.3908934 | 4.011884665 | 19.73276191 |
| validation_selection_background | 74749 | 0.1722455227 | 0.3307743981 | 0.0934420925 | 1.427817212 | 4.005847267 | 13.79041322 |
| validation_calibration_background | 74823 | 0.1728282536 | 0.3370284958 | 0.09375141511 | 1.423173655 | 4.118285218 | 14.8868256 |

Full min/p90/p95 values are in the [measured report](../pca-baseline.md) and
[curated CSV](../../results/tables/final/task0006-pca-background-summary.csv).
Finite right tails were observed, with no clipping or retuning. Training average
residual agrees with discarded sample-covariance eigenvalues times (N-1)/N
within ~7e-16. Maximum ECDF distances: train/selection 0.004469786845,
train/calibration 0.005223804426, selection/calibration 0.002330908732.

| Target FPR | Threshold | Calibration accepted/74823 | Selection accepted/74749 | Selection FPR | Absolute deviation | Signed relative deviation |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 0.349676816279485 | 7482 | 7425 | 0.0993324325409 | 0.000667567459096 | -0.66757% |
| 0.05 | 0.564209717524942 | 3741 | 3729 | 0.0498869550094 | 0.000113044990568 | -0.22609% |
| 0.01 | 1.42321469051389 | 748 | 754 | 0.0100870914661 | 8.70914661066e-05 | +0.87091% |
| 0.001 | 4.13564833602919 | 74 | 71 | 0.000949845482883 | 5.01545171173e-05 | -5.01545% |

Only 71 selection events populate the 1e-3 tail; Wilson95 interval
[0.000753179,0.001197803]. No tail extrapolation or real signal efficiency/AUC/AP
was produced. Diagnostic tables/figures are background-only.

## Test Embargo

**No real test_background or test_signal population was requested by model or
evaluation readers. No model scores/distributions/performance were inspected
on either.** Both real runs log exactly train, selection and calibration roles
with allow_test=false/include_labels=false and counts 699957/74749/74823. Code
rejects any other role before calling the reader. Full-store integrity verification
necessarily reads byte content and structural metadata across all artifacts,
as explicitly required; that custody operation is not model test unblinding.

The separate future evaluation CLI requires explicit --allow-test and frozen
model/calibration/data identity matches. It writes a persistent UTC/model/commit/
metric access record before each test-population read, including failed/partial
unblinding status. Only synthetic fixtures exercised this path in Task 0006;
no real test-unblinding record/output exists. The protocol reserves real final
benchmark for a later explicitly authorized frozen-candidate evaluation stage.

## Reproducibility / Runtime

Two independently executed full background runs (`data/baselines/pca-v1` and
`pca-v1-repeat`) produced identical k, numeric model parameters (maximum difference 0),
scientific hashes, thresholds/summaries, score-array bytes, CSV tables and PNGs.
All local run-manifest file sizes/hashes verified. Timestamp/model-file-byte hashes
may differ; scientific model/results identities exclude transient build metadata.
Scientific result JSON and CSVs are curated; no model or score arrays enter Git.

Final Git review found stdlib CSV's CRLF output triggered whitespace checks.
The exporter now emits Unix newlines. Two final independent runs in `pca-v1-final`
and `pca-v1-final-repeat` regenerated LF tables, with scientific identities,
parameters/scores/figures unchanged. Both final tables/PNGs match byte-for-byte
and were copied to the curated paths. All run-manifest hashes were reverified.
The source integrity/protocol never changed.

First run fit 0.122026 s; train score 0.019536 s; selection score 0.001991 s;
calibration score 0.002271 s; plotting 9.23757 s; total before finalize 16.1463 s;
lifetime RSS 2,182,856,704 bytes (2.03 GiB), dominated by full-store integrity/mmap
verification. Repeat fit 0.104467 s, total15.6977 s, RSS 2,407,530,496 bytes (2.24 GiB).
These are engineering observations, not formal inference benchmarks. Largest
model input is a compact 699957x8 FP32 matrix (~22.4 MB), promoted for full SVD;
raw HDF and full padded/particle matrices are not loaded by fitting/scoring.

Final LF run: fit 0.104816 s; train scoring 0.020592 s; selection 0.001967 s;
calibration 0.002660 s; plotting 0.637593 s; total 8.920701 s;
peak RSS 2,410,004,480 bytes (2.24 GiB). Independent final run: fit 0.105915 s,
total 7.898338 s, peak 2,582,708,224 bytes (2.41 GiB). Local XDG_CACHE_HOME and
MPLCONFIGDIR kept font caches under ignored data and resolved the earlier warnings.

## Validation

Actual commands (project .venv Python/Ruff):

```bash
python -m pip install -e ".[dev,data,analysis]"
python -m pip check
python -c "import latenttrigger, sklearn; print(latenttrigger.__version__, sklearn.__version__)"
python -m latenttrigger.data.preprocessing --verify data/processed/lhco-rd-v1/schema-v1/full
ruff check .
ruff format --check .
python -m pytest
python -m latenttrigger.models.pca --config configs/models/pca_baseline.json
python -m latenttrigger.models.pca --config configs/models/pca_baseline.json \
  --output data/baselines/pca-v1-repeat
python scripts/smoke_test.py
python -m latenttrigger.evaluation.run --help
git diff --check
```

Editable install succeeds; pip check no broken requirements; import 0.1.0/scikit-learn
1.9.1. Full suite **120 passed** (84 existing +36 new). Ruff lint/format pass.
CPU smoke passes with MPS availability patched false; native MPS outside sandbox
passes with result 16 on mps:0. Full store integrity/schema/counts verified.
Real PCA fit/background scoring/calibration/selection verification completed;
independent reproducibility and local artifacts/hash/audit checks passed.
Future metric definitions and test gate work on synthetic fixtures only. Figures
were visually inspected before curating. Final links/Git exclusion/diff reviews
are recorded below before completion; no stage/commit/push or hosted CI run.

The final pair used the same CLI with `--output data/baselines/pca-v1-final` and
`--output data/baselines/pca-v1-final-repeat` and local cache environment variables.
After the newline fix, the full pytest suite again passed **120 tests**.

Final review passed: **86** relative links in **23** Markdown files; **49** inspected
local/generated paths ignored; all **25** intended task files small and trackable,
with clean text whitespace and no credential/key patterns. Run metadata is portable;
both final audits contain only the three allowed background roles. No real test
unblinding record exists. Historical handoffs and fitted preprocessing config
are unchanged; Git index remains untouched. Final Ruff and diff checks pass.

## Issues / Limitations / Rejected Alternatives

Sandbox font-cache permissions produced harmless Matplotlib/fontconfig warnings;
figures were generated correctly, inspected and identical in the repeat run.
A local MPLCONFIGDIR cache was used for repetition; all such caches remain ignored.
An extreme negative finite ROC cutoff could underflow its predecessor to -inf;
fixed the future metric marker to accept_all and added a synthetic regression test.
It does not affect the background PCA runs or reported artifacts.

No scientific blocker. No cross-platform BLAS bitwise identity or detector
sensitivity claim. Finite calibration tails limit precision. Reader verification
faults memory-mapped output pages into RSS, so lifetime peak is not model memory
alone. Full scientific timestamps are separate from numeric identity. Optional
figures need the existing analysis extra; numeric runs do not. Output directories
are exclusive and not automatically replaced/resumed.

Rejected: custom PCA linear algebra, randomized/whitened PCA, refitting scalers,
signal-guided component tuning, interpolated unattainable ROC points, infinite
zero-FPR rejection, pickle-only model artifacts, fabricated anomaly proxies,
pandas for tiny CSVs, and experiment-tracking services.

## Follow-up / Git

Next **Task 0007 — Compact Autoencoder Baseline**, reusing the frozen representation,
separate background selection/calibration roles and evaluation protocol. Preserve
both real test populations' embargo while developing models.

Base remains cb079ec; no resulting commit exists. No files were staged, committed
or pushed. Prompt/handoff/index belong with implementation/config/curated small
results in one user-reviewed commit. Suggested message:
`feat: add PCA anomaly baseline and evaluation framework`.
