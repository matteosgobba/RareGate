# Task 0009 — Particle-Level / Set-Aware Neural Baseline Design

## Metadata

- Date: 2026-10-06, Europe/Rome.
- Status: **completed locally, design only; awaiting user review/commit/push**.
- Operational repository: `/Users/matteosgobba/Documents/GitHub/latent-trigger`;
  this is the Git working checkout, not a read-only synced `sources/` mirror.
- Branch/upstream: `main` / `origin/main`.
- Base/HEAD/local upstream: `06450773e75a4d670c771d154714e0cb4d4d9557`.
- Environment checked: macOS 26.6.2 ARM64, Python 3.12.12; installed PyTorch
  2.14.1, NumPy 2.5.3, scikit-learn 1.9.1, SciPy 1.18.1. Existing task evidence
  records user-specified M5 and 16 GiB RAM; no hardware benchmark run here.
- Initial changes: only untracked, user-authored `docs/project-memory.md`; copied
  before editing to `/private/tmp/task0009-project-memory-before.md`.
- No staged changes initially or finally. No repository/ancestor `AGENTS.md`
  found. Read development protocol and the entire living memory before design.
- Remote push and hosted CI not independently verified. Local ref equality and
  commit presence are the only Git synchronization evidence.

## Objective / scope

Choose one complete, defensible unsupervised particle/set model and scalar
anomaly score, reusing the frozen representation, with exact correspondence,
capacity, resource and future convergence/calibration contracts. No new model
implementation/training/scoring, real data inspection, thresholds, dependencies,
CI, preprocessing, splits, existing runners, exports or hardware measurements.
The [actual user prompt](../prompts/0009-particle-set-baseline-design.md) and initial
handoff were saved before substantive design work. Initial handoff recorded the
base, pre-existing memory and pending validation; this completion record replaces
its pending sections with factual outcomes.

## Inspected evidence / Task 0008 verification

Read operational README/development/memory, preprocessing contract/pipeline,
evaluation protocol, Task 0004 EDA/handoff and Task 0005 handoff, compact AE and
convergence reports/Task 0008 handoff, frozen data JSON, AE v1/v2 configs, curated
convergence results/history and canonical artifact. Inspected particle
`features.py`/`processed.py`, existing model/background/training guards and
artifact/scoring code, calibration functions/final unblinding gate, Git ignore
and local data/artifact policies. No synced source was edited.

Small-file checks performed (no model forward, no real arrays):

- V1/v2 artifact scientific canonical-JSON hashes recompute correctly. V2
  `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b`;
  results `324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33`.
- V2 parameter list contains 155 exact FP32 values and the recorded architecture
  8→6→3→6→8. Training artifact: best381, stopped396, patience15,
  selection/restored MSE **0.21447598731176187**.
- V2 config equals v1 with only max_epochs changed to1000; its canonical hash
  matches artifact provenance. Frozen preprocessing file-byte hash also matches.
- Curated v2 history has396 rows; first200 equal the complete Task 0007 history
  exactly. Minimum selection occurs at381 and equals artifact restored MSE.
- Independent ignored CPU repeat model matches canonical artifact/scientific
  hash; existing repeat audit reports bitwise parameters, both prefixes verified,
  exact scientific results/score-byte hashes and zero test accesses.
- Read only full-store manifest JSON to reconcile source/config/split/scientific
  metadata. Did not instantiate `ProcessedStore`, hash the full store/raw source,
  rebuild preprocessing or rerun expensive custody checks.

These verify stored evidence, not a new reproducibility experiment. Historical
167-test outcome is retained as Task 0008 evidence; pytest was not rerun here.
No integrity problem requiring AE/PCA retraining was found.

## Candidate comparison and final decision

Exactly three concrete candidates are compared in the
[design report](../particle-set-baseline-design.md), with primary-source attribution
and a distinction between published set methods and proposed unsupervised heads:

1. Event-only mean8 AE, fixed scalar output queries, shared9→16→4 decoder,
   symmetric Chamfer objective:444 parameters,153600 dense MAC/event at384,
   quadratic scoring. Rejected initially for correspondence/duplicate-frequency
   ambiguity and matching cost. Reconsider if fixed event-only compression becomes
   necessary under a new matching/resource contract.
2. **Selected: local2 plus mean8 equivariant particle AE**,478 parameters,
   165888 dense MAC/event, corresponding-particle loss/score. Complete,
   transparent local information path with linear network and scoring cost.
3. One-head width8 attention addition (Q,K,V,O biased), then selected local/mean
   decoder:766 parameters,2623488 MAC/event and two principal n² FP32 attention
   tensors. Rejected for ~15.8× MAC without a demonstrated interaction need.
   Reconsider only through a new versioned interaction/resource decision.

All are analytically feasible in bounded 16 GiB batches, but CPU wall time is
unknown. Selection used completeness/simplicity/resource reasoning, no candidate
training/search, new background inspection, calibration or published signal ranking.

## Architecture, exact objective / score and information audit

Inputs FP32[B,384,4], bool[B,384], True=retained particle; exact ordered channels
and scalers from unchanged hashed Task 0004 JSON. Leading-pT retained prefix,
source-before-cast ordering, transformed-then-zero padding and saved splits
unchanged. Original counts/retained-pT fraction are diagnostic, not neural features.

Five shared biased Linear layers:

| Layer | Shape / activation | Parameters |
| --- | --- | ---: |
| e1 | 4→16, ReLU; [B,384,16] | 80 |
| e2 | 16→8, ReLU; masked h [B,384,8] | 136 |
| local | 8→2, linear; masked ℓ [B,384,2] | 18 |
| mean context | g=Σvalid h/n; [B,8], FP64 pool then FP32 | 0 |
| d1 | concatenate [ℓ,g],10→16, ReLU; [B,384,16] | 176 |
| d2 | 16→4, linear; masked Y[B,384,4] | 68 |
| Total | 478 FP32 parameters /1,912 bytes | 478 |

Sanitize excluded X before the first layer; zero excluded h,ℓ and Y; use one
mask/count in pooling/objective/output validity. No raw X/h skip to decoder,
input slot identities, queries, count head or auxiliary terms. Distinct particles
receive their own local code. Valid code capacity is **2n+8** real values plus
mask metadata (776 at n384); it is not an eight-value event compression. Small-n
context can carry essentially all targets. Particle correlations and learned
joint-feature means use information absent from the eight fixed aggregates;
no pairwise geometry, rotation invariance or IRC safety is established.

For corresponding input/output particle i:

```text
d_i = (r0²+r1²+0.5*r2²+0.5*r3²)/3
s(X) = L_event = sum_valid(d_i)/n_retained
L_batch = sum_event(L_event)/actual_batch_events
L_epoch = sum_individual_event_losses/actual_population_events
```

Exactly one score, finite nonnegative FP64 CPU scalar/event, larger anomalous.
Network FP32, pool FP64→FP32, training/selection/score residuals and reductions
FP64; gradients return to FP32 parameters. Sin/cos predictions unconstrained:
unit-pair angular contribution before/3 is1−cos(Δphi); zero output pair contributes
0.5 and off-circle outputs have ordinary radial residuals. No phi residual,
projection, extra penalty, score correction, count term or clipping.

Output is equivariant because each shared decoder receives permuted local code
and unchanged pooled context. Score/global context invariant mathematically;
FP32 latent/output tolerances atol1e−6/rtol1e−5 and FP64 score atol1e−8/rtol1e−6
are fixed for well-scaled synthetic tests. Padding gradients must be exactly zero.
Public reader/adapter still requires prefixes; arbitrary-hole mask permutations
are tested only at the internal kernel boundary. Nonempty n1/n384 accepted;
empty/malformed/nonfinite batches rejected. Repeated particles have no matching
ambiguity; uniform replication leaves mean score unchanged within capacity.
Counts are supplied, not reconstructed, and removed particles remain invisible.
PCA/AE SSE contracts and artifacts are unchanged; raw losses are incomparable.

## Resource calculations and future protocol

[Budget CSV](../../results/tables/final/task0009-particle-set-design-budget.csv),
49 checked rows; units bytes/MiB/MAC/scalar_ops/count. One MAC is one Linear
multiply-accumulate; biases, activations, reduction/casts excluded.

- MAC/event=384×(64+128+16+160+64)=165888; B32=5308416.
- Input and output each6,144 bytes atB1 /196,608 atB32; masks384 /12,288.
- Largest network shape[B,384,16],24,576 /786,432 bytes (0.75MiB atB32).
- Score arithmetic15n/event (5,760 at384), no pairwise tensor/solver.
- Parameters+gradients+two Adam moments7,648 bytes; ten step scalars40;
  best-state snapshot1,912. Allocation inventory313BNmax+48B+9600 gives
  129,840 /3,857,280 bytes; 4× planning envelope519,360 /15,429,120 bytes.
  These omit runtime/allocator/mmap overhead and are estimates, not peak RSS.
- FP64 pool conversion is [B,384,8], same bytes as largest FP32 hidden tensor,
  explicitly covered by additional envelope headroom. Approximate backward2×
  forward gives full train+selection epoch360,743,362,560 MAC before I/O/overhead.
- Future working tensors/workspace≤512MiB, process RSS≤6GiB; launch available≥8GiB,
  stop below4GiB. No full padded population; batch32 streamed from ragged store.

Fixed future training: CPU, seed/shuffle1729, fixed layer order/default Linear
uniform initialization (checked in installed PyTorch source), ordinary Adam
lr0.001/betas0.9,0.999/eps1e−8, all other options explicitly false/zero in JSON;
no scheduler/clipping/AMP/accumulation/fallback. Batch32, workers0, uniform shuffled
train each epoch without replacement, tail retained; sequential selection/scoring.
One intra-op/inter-op thread, deterministic algorithms, fresh canonical process.
Train699,957, selection74,749; exact event weighting as above.

Full selection mean score chooses checkpoint by strict improvement, min_delta0,
ties keep earliest best and count as failures, patience20, max200. Restore best;
exact independent JSON reload selection score/parameter verification and fresh
CPU rerun must reproduce history/stop/weights/scientific hash/score bytes before
freeze/calibration. Cap without patience = **convergence unresolved**.

Future staged gates: synthetic correctness → disposable dev/resource check →
authorized canonical training → restore/reproduce → freeze → calibration.
Dev only first1,024 frozen dev-train IDs, max3 passes/96 steps plus one same-sample
score pass,≤300s. Conservative measured extrapolation
`2*(699957*t_train_pass/1024+74749*t_score_pass/1024)≤180s` using max train pass
and including views. Full cycles≤180s; fitting/selection≤10h/run, postfit≤1h/run,
two repetitions≤22h. Memory and finiteness gates apply throughout. Failed gates
block dependent work; no automatic horizon, batch, device or architecture change.
No execution of this protocol is authorized in Task 0009.

Future calibration after freeze/reproduction:74,823 calibration background,
FPRs0.1/0.05/0.01/0.001, existing higher quantile and strict score>threshold.
Reuse summaries/KS/Wilson/counts/resolution/zero-acceptance bound and transfer to
selection without retuning. Descriptive diagnostics versus original/retained N,
truncation/retained-pT fraction, scalar/max pT and mass proxy use postfreeze
train-defined bins, tails preserved. Selection is early-stopping-exposed;
calibration estimates thresholds and is not independent threshold validation.
No diagnostics feed back into architecture/objective/score within a frozen run.

## Files / living memory / implementation routing

Nine intended files (all explicitly listed in manual Git delivery):

- New task prompt and this handoff.
- New `docs/particle-set-baseline-design.md`.
- New `configs/models/particle_set_baseline_design_v1.json` (design_only).
- New `results/tables/final/task0009-particle-set-design-budget.csv` (analytic).
- Existing untracked user memory updated in place, intended for first tracking.
- README status/design links; development protocol's mandatory memory read/update;
  handoff index Task0008 local commit confirmation and Task0009 entry.

Memory revision1.1 updates current state/objectives/model registry/decision register,
resource limits/roadmap/open questions/references in place, retaining user-authored
vision, source/split/preprocessing/PCA/AE evidence and maintenance instructions.
Selected design and limitations replace the earlier unresolved menu. Particle
state explicitly designed; implementation/training/calibration pending. Canonical
AE v2 remains155 parameters/best381/stop396, no fictitious particle weights/hash.

Task0010 minimal interfaces are specified in the design report: shared particle
module with encode/reconstruct/event_loss/score, train/selection-only fit, audited
particle-background streaming and existing evaluation functions. The aggregate
loader is explicitly unsuitable. Current reader fully verifies on construction;
future run opens one instance. A minimal guarded iterator extension for validated
split-relative shuffled order avoids repeated whole-split metadata filtering;
it is a proposed interface, not an existing capability. No runner/reader was
modified. Exact architecture, ordered trained parameters, input/loss/score/
training/source/split identities belong in future scientific content; engineering
paths/times stay outside. Design hash is not a trained-model hash.

## Actual design validation and limitations

Executed `.venv/bin/python` standalone helpers under `/private/tmp`, JSON parsing,
49 budget-row recomputations, tensor-dimension/parameter/bytes/MAC arithmetic,
training tails and completeness/resource/calibration-field checks. Synthetic
scalar/NumPy cases: exact reconstruction0, pT residual1→1/3, two residuals1/0→1/6,
finite padding exclusion, matched permutations, uniform replication, mean-context
permutation, full384, empty/mask rejection, opposite angular pair2/3, zero/doubled
angular prediction1/6, seam±(pi−0.001)≈6.6666644444447e−7, event versus particle
weighting (1/4 versus2/9). No trainable network or training loop constructed.

Canonical-JSON design content SHA-256:
`3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67`.
This identifies a specification without learned weights, not a model artifact.
Formula/report/JSON/CSV agreement, relative local links, tracked/untracked scope,
historical bytes and whitespace checks pass. Final counts are recorded below.
The validation helper initially treated `git diff --no-index`'s difference exit
code1 as failure; corrected to accept a clean difference. Whitespace review then
caught default CSV CRLF endings; normalized CSV/generator to LF and reran checks.
No scientific/production behavior changed by those corrections. Final optimizer
source review corrected the inventory to ten Adam step scalars (one per weight
or bias tensor), forty bytes; this adds20 bytes to the inventory and80 to its
4× envelope. All affected report/JSON/CSV arithmetic was revalidated.

Future, unexecuted acceptance checks: actual neural output/latent equivariance,
input/parameter padding gradients, initialization/shuffle/determinism, guards and
particle loader reads, exact serialization/restoration/reproduction, overflow
rejection, measured memory/wall time, convergence and background validation.
No full pytest, store verification, exports or benchmarks were run for these
specification/documentation changes. Operator portability is reasoned only;
FP64 pooling/scoring and masks/reductions require future backend verification.

Final review: **49 budget rows**, **123 relative local documentation links**,
**104 historical tracked files byte-identical**, **nine intended files**, and
tracked/untracked whitespace checks pass. Git index remains empty. The living
memory diff was reviewed against its pre-task copy; original objectives, user
content and scientific history remain, with affected current-state sections
updated. No production, dependency, CI, data/configuration or historical task
record was modified.

## Access audit

- New real model/evaluation requests: train0, selection0, calibration0.
- test_background requests0; test_signal requests0.
- No processed reader instantiated, no raw/NPY particles/features/labels opened,
  no new or existing model trained/scored. Existing small JSON/CSV reports and
  manifest metadata read; synthetic arithmetic only.
- No new threshold or score distribution, no signal/test physics or latent
  distribution, no AUC/AP/FPR/signal-efficiency calculation.

```text
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

No design blocker remains. Local code capacity, weak count sensitivity, rare
residual dilution, off-circle predictions, truncation, eight-mean context,
CPU feasibility/convergence and unknown signal usefulness remain limitations.
A complete design is not evidence of trained convergence or trigger readiness.

## Follow-up / Git

Propose **Task 0010 — Compact Particle/Set Baseline Implementation and Background
Validation**, reconciled with live index and gated on synthetic/resource feasibility.
Do not execute automatically. Preserve PCA/AE and test embargo. No files staged,
committed or pushed by Codex; base unchanged; no resulting commit invented.

Manual delivery, run from the operational repository. The index was empty at
final review; if unrelated staged work has since appeared, preserve it and keep
it out of this task's commit before continuing.

```bash
git status --short --branch
git diff -- README.md docs/development.md docs/handoffs/README.md
git add -- README.md docs/development.md docs/handoffs/README.md \
  docs/project-memory.md docs/prompts/0009-particle-set-baseline-design.md \
  docs/handoffs/0009-particle-set-baseline-design.md \
  docs/particle-set-baseline-design.md \
  configs/models/particle_set_baseline_design_v1.json \
  results/tables/final/task0009-particle-set-design-budget.csv
git status --short --branch
git diff --cached --stat
git diff --cached
git diff --cached --check
git commit -m "docs: define compact particle set baseline"
git push origin main
```

Only local helpers/backups/review output are under `/private/tmp/task0009-*`:
`project-memory-before.md`, `write-spec.py`, `update-memory.py`, `validate.py`,
`validation.json` and final memory-diff review. None belongs in Git. No local
model/data/checkpoint/cache/log artifact was generated by this task.
