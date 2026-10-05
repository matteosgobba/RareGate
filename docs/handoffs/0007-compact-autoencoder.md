# Task 0007 — Compact Autoencoder Baseline

## Metadata

- Date: 2026-10-05, Europe/Rome
- Status: completed locally; awaiting user review/commit/push
- Phase: compact neural reconstruction baseline, background-only development
- Branch/upstream: main / origin/main
- Base commit: `56a74096f3c90c2e43348150b6f5d43f70ca765c`
- Environment: macOS 26.6.2 ARM64, user-specified M5, 16 GiB RAM;
  Python 3.12.12, PyTorch 2.14.1, NumPy 2.5.3, scikit-learn 1.9.1,
  SciPy 1.18.1, Matplotlib 3.11.2, pytest 9.1.1, Ruff 0.16.10.

## Objective / Scope

Implement/freeze one compact nonlinear background reconstruction baseline using
Task 0005's unchanged eight-feature view and Task 0006's evaluation protocol.
Canonical CPU training, selection-background early stopping, calibration after
freezing, transparent tiny model, independent rerun and separate MPS compatibility.
No real test scoring/distributions/metrics, signal proxies, hyperparameter search,
particle models, attention, export, quantization or inference benchmarking.

## Inspection

Starting tree clean. Tasks 0001–0006 committed; HEAD 56a7409 is Task 0006.
Read development/evaluation protocols, PCA/config/report and Task 0006 handoff,
preprocessing contract/pipeline, relevant model/evaluation/data/device code,
dependencies and ignore/result policy. Confirmed main tracks origin/main.
Full store verified before edits; scientific identity remains
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`.
Initial available disk approximately 244 GiB. No unrelated changes existed.
No preprocessing changes or historical prompt/handoff modifications.

## Changes / Files

Created:

- `configs/models/compact_autoencoder.json` — preregistered architecture/training/protocol.
- `src/latenttrigger/models/autoencoder.py` — pure network, score, exact JSON artifact.
- `src/latenttrigger/training/__init__.py`, `autoencoder.py`, `background.py` —
  feature-only batching, deterministic CPU training, early stopping, orchestration,
  exclusive output, history/results and isolated MPS diagnostic.
- `tests/test_autoencoder.py` — 28 synthetic tests/cases.
- Task 0007 prompt (exact supplied attachment), this handoff and
  `docs/compact-autoencoder.md`.
- `artifacts/models/compact-autoencoder-v1/model.json` — tiny intentional frozen artifact.
- Curated tables `results/tables/final/task0007-autoencoder-{background-summary.csv,
  thresholds.csv,training-history.csv,results.json,pca-comparison.csv}`.
- Curated figures `results/figures/final/task0007-autoencoder-{training-history.png,
  background-scores.png}`; both visually inspected.

Modified `.gitignore` (one exact JSON exception), main/data READMEs, handoff index,
shared background helper (dev-only feature loading and training code hashes),
shared reporting (extract same score-distribution plot), future evaluation gate
(two explicit frozen-model types, canonical AE guard). PCA numerical code,
metrics/threshold semantics, source/data config and existing CI unchanged.

## Technical Decisions / Dependencies

Architecture **8→6→3→6→8**, four biased Linear layers, ReLU only after the two
hidden layers; linear latent/output. **155** trainable parameters: 54+21+24+56.
Input order: multiplicity, scalar_pt, max_pt, pt_balance, weighted_eta_mean,
weighted_eta_std, pt_concentration, massless_event_mass. Existing FP32 standardized
full-event aggregate inputs only; no labels/IDs/split/particle records in model.

Configuration saved before canonical run, unchanged thereafter: Adam lr=0.001,
batch 4,096, maximum 200 epochs, patience 15, min_delta 0, seed 1729. Default PyTorch Linear
initialization and default remaining Adam settings. CPU canonical scientific run;
one intra-op thread, observed inter-op 10, deterministic algorithms, seeded
Python/NumPy/torch and independent seeded loader generator, workers 0, no dropped
tail. BatchSampler disables automatic batching for vectorized indexing. Caller
RNG/thread/determinism states restored. No new dependency; existing Torch/NumPy,
shared evaluation functions and optional analysis Matplotlib suffice.

Optimization uses event-weighted channel-mean MSE. Scoring uses FP32 forward and
CPU float64 SSE accumulation over eight channels, higher anomalous; no rescaling.
Strict improvement selects snapshots; 15 consecutive failures would stop. Best
state always restored. Calibration absent from training function and first loaded
only after frozen artifact export. Separate MPS smoke exports nothing.

JSON stores exact FP32 values/shapes/names in fixed parameter order, feature/schema/
architecture/score metadata, config/source/processed/preprocessing/split identities
and deterministic selection record. Scientific hash excludes timestamps/paths/
environment/timings. Hash and exact FP32/schema/shape/name checks reject corruption.
Tiny JSON is deliberately tracked; checkpoint formats/neighbors remain ignored.
Future gate reuses existing metrics and requires explicit opt-in, canonical-full
AE scope and full training count; tested only on synthetic fixtures.

## Results / Provenance

Source: LHCO R&D v5 Zenodo record 6466204, DOI 10.5281/zenodo.6466204, corrected v2 file.
Raw MD5 `629789d55813be3860781b084ae7f1de`, SHA-256
`5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`.
Frozen preprocessing identity
`2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`;
split identity
`74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea`.
Exact model config and config hash are embedded in artifact provenance.

Canonical train **699957**, selection **74749**, calibration **74823**. All inputs,
losses, reconstructions and scores finite. Dev diagnostic separately used
**6999/747/748**; dev model cannot enter final gate. Full model **200 epochs**,
best **200**, stopping reason **max_epochs**, patience not triggered, bad epochs 0.
Online training MSE at best **0.22106828705179374**; restored training MSE
**0.22100737705508344**; best/restored selection MSE **0.22261241728016284**.

Model scientific SHA-256:
`30dadcdc20fa788d5442e031f44694346d2ac152c9b647b77e17351558a1610e`.
Portable deterministic JSON **11945 bytes**, raw parameter payload 620 bytes.
Results scientific SHA-256:
`490f8cf757ea2f2ab46dc7cee58c8d1b5b40b29cb06b799df7d8361987c222cd`.

| Population | Mean SSE | Std | Median | p99 | p99.9 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 1.76805903 | 1.75090194 | 1.27390986 | 8.58919378 | 16.55759438 | 60.35954274 |
| Selection | 1.78089936 | 1.77122877 | 1.27688274 | 8.70885965 | 16.29073783 | 46.17539573 |
| Calibration | 1.77238256 | 1.74759089 | 1.27072766 | 8.63797953 | 16.50140621 | 35.97693649 |

Exact min/p90/p95 and all moments are in curated JSON/CSV. KS distances:
train/selection 0.003388391474; train/calibration 0.003285154347;
selection/calibration 0.004888069666. No diagnostic-guided tuning.

| Target | SSE threshold | Calibration accepted / 74823 | Selection accepted / 74749 | Selection FPR |
| ---: | ---: | ---: | ---: | ---: |
| 0.1 | 3.613707299930235 | 7482 | 7498 | 0.1003090342345717 |
| 0.05 | 4.862834912896428 | 3741 | 3751 | 0.05018127332807128 |
| 0.01 | 8.638938683116985 | 748 | 772 | 0.010327897363175426 |
| 0.001 | 16.547151319930283 | 74 | 73 | 0.0009766016936681428 |

Unchanged higher-quantile strict `score > threshold` convention, calibration-only fitting.
Wilson/count/resolution/deviations are in JSON and thresholds CSV; no refit.
Bounded first 4,096 training-only latent means [-0.6874434,1.5663032,-4.7775930],
std [3.3940365,2.8956327,4.4486336]; finite and no std <=1e-6 collapse.

Background-only PCA comparison in report/CSV: latent 6 vs 3, PCA saved 88 numerical
values (not neural trainable parameters) vs AE 155; JSON 9,253 vs 11,945 bytes with
different metadata overhead; historical PCA fit 0.104816s vs AE training 31.181s.
PCA training mean SSE 0.170393083 vs AE 1.768059028 is not anomaly sensitivity;
latent ranks differ. Shared KS/rate diagnostics only; no AUC/AP/quality ranking
or direct absolute-threshold comparison. No real signal information used.

## Reproducibility / Resources / MPS

Two independent full CPU runs with identical config/seed: identical best epoch,
parameters (maximum difference 0), JSON model bytes, scientific hashes, all three
score-array bytes, thresholds/summaries/history, CSVs and PNGs. Build metadata
and timings differ. Ignored `data/task0007-reproducibility.json` records checks.

Canonical training 31.181045709s; scoring train/selection/calibration
0.028290792/0.003093791/0.003073083s; whole 47.747129542s including full custody
verification and first-use font setup; peak lifetime RSS 2,255,962,112 bytes (2.10 GiB).
Repeat training 32.438092166s, whole 39.352909959s; peak 3,094,134,784 bytes (2.88 GiB).
RSS includes verifier/mmap pages, not isolated network memory. Aggregate matrices
~27.2 MB; no particle-array copy for model training. Engineering observations only,
not controlled inference benchmarks or CPU/MPS speedup claims.

Existing native MPS smoke passes (result 16). Separate MPS FP32 network performs
five Adam steps and finite inference/SSE on 256 dev-training events, losses
0.999993265→0.993118167. Reader loads 6,999 dev-training vectors before bounding
that tensor; audit explicitly records 6,999. No model exported, CPU artifact
untouched, no validation/test populations. Native Metal checks require running
outside filesystem sandbox; successful execution was authorized and completed.

## Validation

Actual project-environment commands:

```bash
python -m pip install -e ".[dev,data,analysis]"
python -m pip check
python -c "import latenttrigger; print(latenttrigger.__version__)"
python -m latenttrigger.data.preprocessing --verify data/processed/lhco-rd-v1/schema-v1/full
ruff check .
ruff format --check .
python -m pytest -q
python -m latenttrigger.models.autoencoder --dev --output data/baselines/compact-autoencoder-v1-dev --no-plots
python -m latenttrigger.models.autoencoder --config configs/models/compact_autoencoder.json
python -m latenttrigger.models.autoencoder --output data/baselines/compact-autoencoder-v1-repeat
python scripts/smoke_test.py
python -m latenttrigger.models.autoencoder --device mps --smoke
```

Editable install succeeded using existing dependencies; pip check no broken
requirements; import 0.1.0. Full suite **148 passed** (120 existing +28 new).
Ruff lint/format pass. CPU smoke with MPS availability patched false passes;
native MPS smoke passes. Full store verifies; dev and canonical AE pipelines,
background calibration and independent repeat complete. Future AE test gate
and dev rejection validated only synthetically. Both plots visually inspected.
Final relative-link/Git ignore/whitespace/security review recorded below.
No hosted CI, automatic staging, commit or push.

Audited canonical/repeat/dev/MPS records: only three permitted background roles,
allow_test=False, include_labels=False; **test_background model requests=0**,
**test_signal model requests=0**. Calibration only after export; no real test
unblinding file. Store hashing and structural verification read full artifact
bytes/label-role integrity as authorized custody, without test distributions,
model scores or performance. No real test-signal performance inspected.

## Issues / Limitations / Rejected Alternatives

Initial synthetic future-gate assertion used a wrong metric dictionary key;
corrected to existing background_total/signal_total API, with suite passing.
Sandboxed editable install could not reach build dependencies; authorized native
install succeeded. No dependency/config change resulted. Optional plots warmed
font caches kept under ignored data. No remaining execution blocker.

Training improved at epoch200 cap; convergence is not claimed. No additional
training/search after observing results. Pure-background simulated aggregate
baseline loses particle structure; anomaly performance unknown. Exact local CPU
reproducibility does not guarantee cross-version/device bitwise identity. Finite
calibration tails and non-comparable PCA/AE latent ranks limit interpretation.

Rejected architecture/latent/learning-rate sweeps, MPS canonical selection,
calibration early stopping, score normalization, extra features/scaler refits,
pickle-only artifact, training frameworks/trackers, GPU worker tuning and premature
export. No new dependencies and no test-informed decisions.

## Follow-up / Git

Next **Task 0008 — Particle-Level Autoencoder or Set-Based Neural Baseline Design**:
specify a compact mask-aware set model from existing canonical particle views;
no automatic Transformer choice. Preserve test embargo. This broadens modeling
representation before export optimization of an untested discrimination candidate.

Base remains 56a7409. No resulting commit invented; no files staged/committed/pushed.
Prompt, handoff, config, source, tests, tiny model and curated reports belong in
one user-reviewed commit. Suggested message:
`feat: add compact autoencoder anomaly baseline`.

Final review: **99 relative links** in **19 maintained Markdown files** passed;
**24 intended task files** are small, trackable and free of trailing whitespace
or credential/key patterns. **45 local/generated/neighbor artifact paths** were
verified ignored. Exact supplied prompt preserved byte for byte. Curated model
parameters match the independent repeat; both run manifests match every actual
output file hash/size. No real test-unblinding record exists under data. Final
Ruff lint/format, diff review and `git diff --check` pass. Git index remains
untouched; historical handoffs and frozen preprocessing configuration unchanged.
