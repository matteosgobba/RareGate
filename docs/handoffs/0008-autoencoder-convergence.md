# Task 0008 — Compact Autoencoder Convergence Closure

## Metadata

- Date: 2026-10-06, Europe/Rome
- Status: completed locally; awaiting user review/commit/push
- Phase: convergence validation of existing compact neural baseline
- Branch/upstream: main / origin/main
- Base commit: `64bb8175f28c4d8a33ecec461effa7d26d23e773`
- Environment: macOS 26.6.2 ARM64, user-specified M5, 16 GiB RAM;
  Python 3.12.12, PyTorch 2.14.1, NumPy 2.5.3, scikit-learn 1.9.1,
  SciPy 1.18.1, Matplotlib 3.11.2, pytest 9.1.1, Ruff 0.16.10.

## Objective / Scope

Resolve Task 0007's epoch-cap uncertainty before a more complex model. Retrain
from scratch under the identical protocol with only max_epochs 200→1000.
In scope: guarded historical prefix verification, original early stopping,
v1/v2 decision, frozen v2, background calibration, independent repeat and reports.
Out of scope: architecture/loss/optimizer/lr/batch/seed/patience/min_delta changes,
schedules, search, signals/test model access, particle networks, exports,
quantization, inference benchmarks or MPS extended training.

## Inspection / Initial validation

Starting tree clean; main tracks origin/main. Tasks 0001–0007 committed; HEAD 64bb817
is Task 0007. Read development/evaluation protocols, Task 0007 report/handoff,
config/history/artifact, training/model/reader code, dependencies and ignore policy.
Available disk approximately 242 GiB. Full store independently verifies before
source edits with scientific identity
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`.

Before source edits, fresh v1 CPU training exactly reproduced all 200 historical
epoch losses, complete selection record and every FP32 parameter; training
31.039205334 s. Only train 699,957 and selection 74,749 feature records requested,
with test/label access disabled. No per-event scores written by this preflight.
Historical Task 0007 prompt/handoff/config/model/history/results remain intact.

## Changes / Files

Created:

- `configs/models/compact_autoencoder_v2.json`.
- `src/latenttrigger/training/convergence.py` — controlled config validation,
  read-only historical-prefix observer, supersession decision, CLI and report.
- `tests/test_autoencoder_convergence.py` — 19 meaningful synthetic cases.
- Task 0008 prompt/handoff and `docs/autoencoder-convergence.md`.
- `artifacts/models/compact-autoencoder-v2/model.json` — tiny intentional artifact.
- `results/tables/final/task0008-autoencoder-convergence-history.csv`.
- `results/tables/final/task0008-autoencoder-convergence-summary.json`.
- `results/tables/final/task0008-autoencoder-background-summary.csv`.
- `results/tables/final/task0008-autoencoder-thresholds.csv`.
- `results/figures/final/task0008-autoencoder-convergence.png` — visually inspected.

Modified:

- Training core: optional read-only epoch observer; unchanged updates/RNG/stop logic.
- Background orchestration: provenance/prefix checks, independent JSON-restored
  validation, optional score persistence disabled for Task 0008, score-byte hashes.
- `.gitignore`: narrow v2/model.json exception; v1 and neighboring ignore rules preserved.
- Main README, historical model report (dated additive supersession note only),
  handoff index (Task 0007 commit confirmation and Task 0008 entry).

No model-network, preprocessing, metric, threshold, dependency or CI changes.
Local outputs/logs/cache/manifests are ignored under data. Task 0008 writes no
per-event score arrays or checkpoints; only summaries and byte hashes survive.

## Technical Decisions / Dependencies

V2 config was saved before the extension. Exact config diff is solely
`training.max_epochs: 200 → 1000`; otherwise byte-equivalent JSON structure/values.
No extra version field is needed: config hash and artifact directory identify v2.
Retain 8→6→3→6→8, ReLU hidden layers, linear latent/output, 155 parameters.
Input order unchanged: multiplicity, scalar_pt, max_pt, pt_balance,
weighted_eta_mean, weighted_eta_std, pt_concentration, massless_event_mass.

Adam lr=0.001/default remaining settings, batch 4,096, seed 1729, initialization,
deterministic shuffled vectorized DataLoader/zero workers/no dropped tail,
CPU one intra-op thread (observed inter-op 10), MSE, min_delta 0 and patience 15
all unchanged. Train/selection alone enter optimization/early stopping. Caller
CPU RNG/thread settings restored. No new dependencies.

Observer verifies each first 200 loss and best-state progression immediately;
at 200 it compares endpoint FP32 parameter bytes against historical frozen v1.
Any mismatch aborts before later training/calibration. History hash must match
artifact, and processed/source/preprocessing/split/scope identities must match
before optimization. Synthetic tests confirm observer does not perturb training.

After best-state restoration and JSON export, independently evaluate the reloaded
network on selection background; exact equality with best-epoch MSE required.
Then access calibration solely for thresholds/descriptive diagnostics. Supersession
uses the user's four conditions before calibration, never signal metrics.
The CLI is `python -m latenttrigger.training.convergence`; old Task 0007 CLI
continues to reproduce its historical config by default.

## First-200 reproduction / Extended Results

Both from-scratch extensions reproduce every first 200 training and selection
loss exactly, identical best-state progression and bitwise epoch 200 weights.
Historical model scientific SHA-256:
`30dadcdc20fa788d5442e031f44694346d2ac152c9b647b77e17351558a1610e`.
Historical best-epoch/loss/failure-count progression is reconstructed from the
verified selection history and unchanged strict rule. Intermediate historical
weight checkpoints were not saved; parameter states are compared at epoch 200.
Historical history SHA-256:
`374d179255fc3f59d5bc1b04f8d6048c4f673a23b36e9c03b2ad912e49976fd3`.
Best-state progression SHA-256:
`23d6b850d55044e06551f47da4e3e87025bbc83ea09d0b2158c9bcaa7229a99e`.

Canonical populations: train 699,957, selection 74,749, calibration 74,823;
all finite eight-dimensional FP32 inputs. **396 epochs executed**, best **381**,
stop **396**, reason **patience**, **15 consecutive non-improvements**.
Best-epoch online training MSE **0.21318465057790426**;
restored training MSE **0.21305374425537163**;
best/restored/independently JSON-reloaded selection MSE **0.21447598731176187**.
Last-epoch online training MSE 0.21303870896544005 and selection MSE 0.2146456583262472
are not the frozen model's selected metrics. Best-state restoration is verified.

V1 selection MSE 0.22261241728016284; improvement **0.008136429968400971**,
**3.654975795%**. Frozen training improves 0.22100737705508344→0.21305374425537163,
absolute 0.007953632799711813. Endpoint is no longer determined by the epoch cap.
**Convergence is closed under the frozen patience rule**, not a mathematical global
minimum/stationarity claim. No protocol extension or post-hoc criterion change.

## Canonical Decision / Artifact

All four conditions hold: prefix exact; training beyond 200; selection MSE strictly
better; protocol/embargo intact. **compact-autoencoder-v2 supersedes
compact-autoencoder-v1 as the canonical compact AE baseline.** V1 remains historical.

V2 uses unchanged interchange **artifact_version=1** (model generation v2),
exact ordered FP32 parameters, architecture/feature/config/source/preprocessing/
processed/split identities and selected-state record. No timestamp/path enters
scientific identity. **155 parameters**, JSON **11941 bytes**; raw parameter payload 620 bytes.

Model scientific SHA-256:
`6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b`.
Background-results scientific SHA-256:
`324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33`.
Precise config hash is embedded in model/results provenance and convergence report.
Source LHCO R&D v5 Zenodo record 6466204 / DOI 10.5281/zenodo.6466204; unchanged corrected raw
MD5 `629789d55813be3860781b084ae7f1de`, SHA-256
`5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`.
Preprocessing hash
`2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`;
split identity
`74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea`.

## Background Summaries / Calibration

Same FP32 forward / float64 raw SSE score, higher anomalous; unchanged higher
calibration quantile, strict score>threshold and independent selection checks.
Calibration never affects training, selected epoch or canonical decision.

| Population | Mean SSE | Std | Median | p99 | p99.9 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 1.704429949 | 1.691040285 | 1.236608266 | 8.234200551 | 16.17732256 | 70.74881845 |
| Selection | 1.715807900 | 1.709946430 | 1.241012641 | 8.329682544 | 16.02839949 | 43.98110727 |
| Calibration | 1.715854399 | 1.702551942 | 1.233158025 | 8.323759407 | 16.43895702 | 40.72891122 |

Exact count/min/p90/p95/all statistics are in curated JSON/CSV. V1/v2 comparison
is in the report, background only. Lower average loss does not guarantee each
individual event improves; training maximum 60.36→70.75 was neither clipped nor used
to change model policy. Architecture/parameter count/artifact format identical.
KS train/selection 0.003453399662, train/calibration 0.004705428147,
selection/calibration 0.004736056356. No significance/p-value tuning or PCA rerun.

| Target FPR | SSE threshold | Calibration accepted / 74823 | Selection accepted / 74749 | Selection FPR |
| ---: | ---: | ---: | ---: | ---: |
| 0.1 | 3.478338537407165 | 7482 | 7475 | 0.10000133781053927 |
| 0.05 | 4.681070974717348 | 3741 | 3698 | 0.04947223374225742 |
| 0.01 | 8.324174660133213 | 748 | 749 | 0.010020200939143 |
| 0.001 | 16.642218868621573 | 74 | 64 | 0.0008561987451337141 |

Target 1e-3 selection Wilson 95% [0.000670616343,0.001093081950], accepted 64.
Signed relative deviation -14.3801% is absolute FPR deviation 0.000143801255,
with finite tail counts. It does not imply better anomaly discrimination.
Full intervals/counts/resolutions/calibration rates are in the curated thresholds.

## Reproducibility / Runtime / Resources

Two independent CPU extensions: same prefix, stop 396, best 381, all 396 history rows,
parameter bytes (difference 0), model/results hashes, background score-array byte
SHA-256, thresholds/summaries, CSVs, summary JSON and PNG. No tolerance relaxation.
Scores exist only in memory; hashes use little-endian float64 row-order bytes.
Ignored `data/task0008-reproducibility.json` records equality checks; both local run
manifests bind every final file hash/size including convergence reports.

First training 59.700382250s; train/selection/calibration scoring
0.029426500/0.003079792/0.010419209s. Core run before finalization 66.846885583s,
RSS snapshot/lifetime high-water 2,051,489,792 bytes (1.91 GiB), before subsequent
convergence plotting/report finalization. Repeat training 59.063456375s;
scoring 0.029672375/0.002977083/0.003111833s; core 66.036752583s;
RSS 2,553,315,328 bytes (2.38 GiB). Verification/mmap pages contribute to RSS.
These are engineering observations, not controlled model/hardware benchmarks.
CPU smoke and native MPS tensor smoke both pass (16); no new MPS training experiment.

## Validation / Test Access

Actual project-environment commands:

```bash
python -m pip install -e ".[dev,data,analysis]"
python -m pip check
python -c "import latenttrigger; print(latenttrigger.__version__)"
python -m latenttrigger.data.preprocessing --verify data/processed/lhco-rd-v1/schema-v1/full
ruff check .
ruff format --check .
python -m pytest -q
python scripts/smoke_test.py
python -m latenttrigger.training.convergence
python -m latenttrigger.training.convergence --output data/baselines/compact-autoencoder-v2-repeat
```

Editable installation succeeded; dependency check no broken requirements; import 0.1.0.
Full pytest **167 passed** (148 existing +19 new cases). Ruff lint/format pass.
CPU smoke with MPS availability patched false passes; native MPS smoke passes.
Full store verifies. V1 preflight, both historical-prefix/extended runs, restored
validation, background scoring/calibration and reproducibility checks pass.
The convergence figure was visually inspected. No hosted CI run claimed.
Final documentation/ignore/diff/security/history preservation review recorded below.

**test_background accessed: NO; test_signal accessed: NO** for real model/evaluation.
Preflight only requests train/selection; each extension requests exactly
train 699,957/selection 74,749/calibration 74,823 with allow_test=False and labels=False.
No real test-unblinding record. Full-store hashing/structural label-role integrity
reads are separately authorized custody; no test distributions, model scores,
labels for optimization or signal metrics were observed. No signal information used.

## Issues / Limitations / Rejected Alternatives

No scientific/reproducibility blocker. Early stopping closes the preregistered
operational criterion, not proof of global optimality or perfectly flat training
loss. Finite calibration tails, aggregate representation, simulation/background
assumptions and cross-platform reproducibility remain limitations.

Rejected checkpoint continuation, extra epoch extensions, patience/min_delta
adjustment, new optimizer/lr/schedule/loss/architecture, signal-guided supersession,
score normalization, production per-event score storage, MPS extended training and
premature particle-model/export work. No dependency changes.

## Follow-up / Git

Next **Task 0009 — Particle-Level / Set-Aware Neural Baseline Design**: choose a
compact mask-aware architecture/objective compatible with the canonical particle
view and future hardware constraints; do not automatically choose a Transformer.
Preserve real-test embargo. Compact AE v2 is the finalized baseline under its rule.

Base remains 64bb817. No resulting commit invented; no files staged, committed or
pushed by Codex. All task source/config/tests/prompt/handoff/reports/tiny model
belong in one user-reviewed commit. Suggested message:
`fix: close compact autoencoder convergence`.

Final review passed: **18 intended files** are small, trackable and free of
trailing whitespace/credential-key patterns; **116 relative links** in **21
maintained Markdown files** resolve. **25 historical files** (including prior
prompts/handoffs, Task 0007 artifacts/results/config and unchanged network source)
remain byte-identical to HEAD. **31 generated/neighbor/cache paths** verified
ignored. Curated model/scientific identities and every local manifest file hash/
size match actual outputs; both runs contain no NPY score file. No real unblinding
record exists. Git index remains untouched. Final Ruff and `git diff --check`
pass. One temporary review helper initially passed strings to a Path-only hashing
utility; corrected and the complete review reran successfully, with no production
or scientific change.
