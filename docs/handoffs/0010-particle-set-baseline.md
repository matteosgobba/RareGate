# Task 0010 — Compact Particle/Set Baseline Implementation and Background Validation

## Metadata / initial inspection

- Date: 2026-10-06 (Europe/Rome).
- Outcome: **Implementation completed; canonical baseline pending**. Launch
  resource gate failed before real reader construction/optimization.
- Operational Git checkout: `/Users/matteosgobba/Documents/GitHub/latent-trigger`,
  not a read-only synced project mirror. No `sources/` references edited.
- Branch/upstream: `main` / `origin/main`.
- Base/HEAD/local upstream: `96ef5aa86dea798966fa8d0e5cb38582ea84d70c`.
- Initial tree/index clean; Task 0009 actually committed at the base. No
  prerequisite/unrelated changes to absorb or stage separately. Remote push
  and hosted CI are unverified; local ref equality is not remote evidence.
- No applicable AGENTS.md found. Read development/living memory and relevant
  design/preprocessing/evaluation/training/artifact/ignore policies.
- Original pasted request copied from the attachment to
  `docs/prompts/0010-particle-set-baseline.md`; initial handoff saved before code.
- Initial tracked hashes/status/diff/index captured in
  `/private/tmp/task0010-initial.json`, including files later updated by this task.
- Environment: macOS26.6.2 ARM64/Python3.12.12/PyTorch2.14.1/NumPy2.5.3;
  scikit-learn1.9.1/SciPy1.18.1. Existing hardware evidence records M5/16GiB.
  CPU reference, no MPS model experiment or inference benchmark.

## Objective / fidelity / inspected evidence

Implement design v1 exactly and execute conditional gates in order. Task0009
prompt/handoff/report/JSON/budget reviewed, alongside frozen data JSON, processed
reader/model view, existing EarlyStopping, background roles/audits, artifact
loaders, calibration/metrics and final test gate. Small-file checks before real
stages verify design canonical-JSON hash, dev/full manifest scientific hash,
source/preprocessing/split identities and exact configuration file-byte hashes.
No expensive full-store/raw verification was repeated as inspection ceremony.

Historical design SHA-256:
`3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67`.
Executable configuration SHA-256:
`48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b`.
No trained/finalized particle model hash exists.

Configuration mapping is explicit: exact copied input/architecture/objective/
score/roles/resource/calibration/numerical fields; training_preregistration→
training; add executable status, schema/runtime versions, model type and design
identity. Exact canonical-JSON validation rejects scientific drift and design-only
input. Existing PCA/AE loaders/runners and Task0009 specification remain intact.
No dependency versions, preprocessing, splits or scientific policy were changed.

## Implementation / decisions

New minimal modules:

- `models/particle_set.py`: input/config validation, shared encoder/local/context/
  decoder, differentiable FP64 event loss, CPU FP64 score, strict distinct-type
  exact-FP32 JSON artifacts and completion gates.
- `training/particle_set.py`: explicit Adam options, deterministic training,
  event-weighted online summaries/source-ordered selection vectors, strict
  stopping/restoration, allocation measurement, live resource probes/deadlines.
- `models/particle_background.py`: bounded particle views, stage/role/truth
  refusal, persisted request audit and compact progress journal, guarded workflow,
  fresh workers, exact reproduction/freeze and conditional common background
  summaries/calibration/diagnostics. No final test invocation/path added.

Reader receives one minimal extension: optional complete split-relative integer
permutation in `iter_batches`. It validates before particle `_batch`, filters
membership once/epoch, preserves sequential behavior, truth/test guards and tail.
Model views come from ragged `EventBatch.model_view(nmax=384)`, not aggregates.
Stream≤32 padded events; cache allowed IDs/shuffle arrays only. IDs/counts/physical
aggregates/retained-pT fraction remain metadata. Never materialize a padded
population or persist real per-event scores/reconstructions/local codes.

Audits record purpose, representation, population/scope and disabled test/truth
flags before views; append count journal per batch, finalize JSON on completion/
exception. This preserves failures without whole growing-audit rewrites each
batch. Exclusive output/Task0010 attempt budget prevents automatic retry under
another directory name. Real-stage parent and worker ceilings include startup;
fit includes store verification, background subtracts consumed restoration
budget. Signals/live50ms monitor/per-batch checks and parent timeout interruption
are testable on controlled probes/clocks.

## Exact model / loss / scientific limitations

| Operation | Shape | Parameters |
| --- | --- | ---: |
| Sanitize X using mask; e1 4→16 ReLU | [B,384,16] | 80 |
| e2 16→8 ReLU; padded h zero | [B,384,8] | 136 |
| local 8→2 linear; padding zero | [B,384,2] | 18 |
| g=FP64 sum(h)/valid count, cast FP32 | [B,8] | 0 |
| concatenate [local,g]; d1 10→16 ReLU | [B,384,16] | 176 |
| d2 16→4 linear; padded output zero | [B,384,4] | 68 |
| Total | 478 exact ordered FP32 values /1,912 bytes | 478 |

Biased shared layers constructed e1,e2,local,d1,d2; weight/bias order and shapes
match design. ReLU stateless/not in place. No skipped target/hidden features,
input positions, attention, queries, BatchNorm, dropout or extra heads/losses.
Capacity2n+8 (776 at384); local path and small-n capacity caveats retained.

Public X FP32[B,384,4], M bool[B,384], nonempty prefix; angular norm-squared
FP64 tolerance2e−6. Private non-prefix kernel only for symmetry tests. Reject
nonfinite/unsupported dtype/device/shape/count/mask; finite padding sanitized
before e1; excluded local/output/input gradients exactly zero. Corresponding
particle outputs equivariant; context/score invariant within frozen tolerances.

```text
r = float64(X) - float64(Y)
d_i = (r0²+r1²+0.5*r2²+0.5*r3²)/3
s = L_event = sum_valid(d_i)/n_retained
L_batch = equal event mean over actual B
```

Autograd preserved through FP64 loss into FP32 gradients/Adam states. Every
required numerical value/state checked for finiteness. One CPU FP64 scalar/event,
larger anomalous. Unconstrained sin/cos, continuous seam and radial residuals,
no matching/count penalty/correction/clipping. Online versus restored objective
is distinguished; raw values not compared to PCA/AE SSE. Mean dilution, uniform
replication/count blindness, local-code bypass, truncation/off-circle/limited
context and unknown signal sensitivity remain. No rotation/IRC-safety claim.

## Synthetic acceptance / actual validation

**247 tests pass**:167 prior +80 new particle cases. New coverage includes exact
config/initialization/order, independent formula and angle examples, n1/n384,
empty/dtype/nonfinite/overflow, public/internal permutations and aligned gradients,
finite padding and zero gradients, repeated particles, differentiable FP64→FP32
loss, optimizer updates/state precision, reader once-per-epoch shuffle/coverage/
tails/malformed/foreign positions before reads, stage/truth guards, failed audit,
all calibration prerequisites, strict ties/clones/restoration/patience-at200/cap,
corrupt/rehashed artifacts/incomplete freeze refusal, live deadline interruption,
failed dev blocking dependent stages/retries, and interrupted epochs never
publishing history. Synthetic stores/controlled clocks/probes only; no real data
or large training needed by CI. Tolerances unchanged.

Actual commands/checks:

```bash
PIP_CACHE_DIR=/Users/matteosgobba/Documents/GitHub/latent-trigger/data/task0010-pip-cache \
  .venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pip check
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pytest -q
.venv/bin/python /private/tmp/task0010-acceptance.py
.venv/bin/python -m latenttrigger.models.particle_background \
  --acceptance data/task0010-synthetic-acceptance.json
```

Editable reinstall succeeds; package0.1.0 imported from operational source;
no broken dependencies; lint/format and 247-test full suite pass. CPU model smoke
and exact count/bytes pass. First sandbox editable build could not resolve the
build-backend host; authorized native retry succeeded with `--no-deps`. Existing
runtime versions unchanged. One formula fixture initially used random FP32
values minus1 and expected an exactly1 residual at1e−12; changed fixture to exact
0/−1, preserving tolerance and production loss. No scientific tuning occurred.
Generic MPS smoke not needed/run; particle reference stays CPU-only. Hosted CI
not observed. Final links/diff/exclusion/historical checks recorded below.

## Measured resources / actual dev gate

The synthetic worst-shape batch32/full384 CPU allocation timeline includes
forward, differentiable loss, backward, temporaries and two synthetic Adam steps
(to include initialized state): **5,228,448 bytes (4.986236572265625MiB)** peak live
tensor allocations. This is measured synthetic allocation, not analytic inventory
or real-run peak RSS/workspace/latency. The code separately conservatively bounds
Darwin whole native malloc arena reservation against512MiB and lifetime process
RSS against6GiB, including framework/runtime and mapped-store overhead. Sampling
is not a general exact profiler of arbitrary VM allocations; reference CPU
operators plus tensor allocation measurement define the accounting boundary.

Fresh real-stage launch attempt, no reader constructed:

| Measurement | Actual |
| --- | ---: |
| Available bytes = Darwin free+inactive pages | **3,967,254,528** |
| Available GiB | **3.694793701171875** |
| Required launch available bytes | **8,589,934,592 (8GiB)** |
| Worker lifetime peak RSS bytes | 356,663,296 (0.3321685791015625GiB) |
| Native malloc arena reservation bytes | 184,205,312 (175.671875MiB) |
| Native heap in-use bytes | 138,792,912 |
| Worker elapsed including startup | 1.3417417500168085s |
| Supervisor elapsed | 1.5579908340005204s |
| Resource samples | 1 |

**Gate failed: Launch available memory below8GiB.** Also below the continuing
4GiB floor, but launch minimum is the first recorded failure. No automatic retry,
limit change or application/process shutdown. Unique real dev events0, steps0,
passes0; train/score-pass timing and factor2 extrapolation **not reached**. No
conclusion about CPU throughput/model convergence follows. Small launch RSS and
synthetic tensor allocations are not substitutes for the dev feasibility gate.

Ignored evidence: `data/baselines/compact-particle-set-autoencoder-v1/workflow.json`,
`dev/stage-result.json`, `dev/access-audit.json`, `dev.log`; exclusive
`data/baselines/task0010-particle-attempt-budget.json`; source-bound synthetic
acceptance JSON under data. Curated factual small gate summary under results/final.
No empty success history/threshold/profile table, figure or model was generated.

## Conditional policy and stages not reached

Frozen CPU seed/shuffle1729/default ordered Linear initialization, explicit Adam
lr.001/betas(.9,.999)/eps1e−8/zero decay/foreach=False/fused=False/remaining design
switches; batch32/workers0/tail retained, one intra/inter-op thread, deterministic
algorithms, no AMP/schedule/clipping/accumulation/fallback. Full train699,957 and
selection74,749; equal-event score, strict improvement/min_delta0, patience20,
max200, earliest ties/patience priority at200. Cap without patience unresolved.

Ceilings preserved: dev300s/1024 events/3passes/96steps/same-sample score; frozen
factor2 extrapolation≤180s; every actual full cycle180s; fit+selection36,000s/run;
postfit3,600s/run; two complete repetitions79,200s; working tensors/workspace512MiB,
RSS6GiB, launch≥8GiB and continuing available≥4GiB. No resource observation changes
model or training policy. Remaining postfit budget accounts for restoration
before background; parent timeout includes worker startup/verification.

Real dev views, canonical training, best restoration/reload verification,
independent fresh reproduction, freeze and calibration/diagnostics **not reached**.
No best/stopping epoch, online/restored objective, selected score, trained artifact
size/hash, threshold/FPR or profile is reported. Conditional code preserves the
required exact parameter/history/shuffle/score identity checks and frozen common
calibration/KS/interval/diagnostic contracts; actual real behavior remains unverified.


Final review corrected the total canonical-run timer to start after the separate
dev stage, preserving the exact22h canonical budget rather than charging dev
time to it. The247-test suite, lint/format and synthetic workspace measurement
were revalidated. Original gate-attempt acceptance remains preserved in
`data/task0010-synthetic-acceptance.json`; final source-bound acceptance is
separate in `data/task0010-final-synthetic-acceptance.json`. No real attempt was
repeated and the recorded launch outcome is unchanged.

## Access audit / exclusions

- All new real model/evaluation population requests0: train0, selection0,
  calibration0, test_background0, test_signal0.
- No `ProcessedStore` constructed in the real attempt, no real raw/NPY particle,
  feature or label arrays opened; only small config/manifest/report metadata read.
- No whole-store/raw custody verification needed/run because launch stopped first.
- No PCA/AE real retraining, test distributions/losses/AUC/AP/FPR/signal efficiency,
  final-unblinding invocation, MPS particle training, export/quantization/latency,
  Transformer/NVIDIA/TensorRT/hls4ml/trigger simulation.

```text
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## Files / memory / next decision

Thirteen intended files:

- README, handoff index, living memory updated in place.
- Existing processed reader extended minimally with guarded order iteration.
- New three implementation modules and80-case synthetic test file.
- New exact executable config, Task0010 actual prompt/handoff, implementation
  report and small factual gate/resource summary.

Task0009 prompt/handoff/report/design JSON/budget remain unchanged; user content,
PCA/AE results/configs/artifacts and historical records preserved. No CI/dependency/
ignore-rule modifications. Initial prerequisites were committed/clean, so ordinary
selective staging isolates this task; no separate prerequisite commit is needed.
Git index remains untouched.

Memory revision1.2 records exact implemented/tested state, resource failure,
measurement/unknown distinctions, unchanged scientific limitations, pending
canonical stages and a new next dependency. Recommend **Task0011 — Bounded
Particle/Set Resource-Gate Recovery and Background Validation**: explicitly
authorize one fresh attempt only after≥8GiB available, retain failed evidence and
original unused96-step budget/limits. This may address host-memory conditions;
it does not authorize architectural/device/batch/thread/horizon changes. Benchmark
protocol/foundation follows only after baseline prerequisite gates complete.
No next task automatically executed.

## Final review / manual Git delivery

Final review passed: **13 intended files**, **109 prior tracked files byte-identical**
(including all Task0009 scientific records, PCA/AE and CI/dependencies),
**224 local Markdown links** resolve, **11 generated/neighbor/cache paths**
verified ignored, strict config/source-bound acceptance checks pass, no canonical
stage artifact exists, and tracked/untracked whitespace checks pass. Initial tree
was clean and Task0009 committed. Index remains empty. Review details are saved
in `/private/tmp/task0010-review.json`. No commit/push performed, base unchanged.
Suggested gated-outcome message:
`feat: implement gated particle set baseline`.

```bash
git status --short --branch
git diff -- README.md docs/project-memory.md docs/handoffs/README.md \
  src/latenttrigger/data/processed.py
git add -- README.md docs/project-memory.md docs/handoffs/README.md \
  src/latenttrigger/data/processed.py \
  src/latenttrigger/models/particle_set.py \
  src/latenttrigger/training/particle_set.py \
  src/latenttrigger/models/particle_background.py \
  tests/test_particle_set.py \
  configs/models/compact_particle_set_autoencoder_v1.json \
  docs/prompts/0010-particle-set-baseline.md \
  docs/handoffs/0010-particle-set-baseline.md \
  docs/particle-set-baseline.md \
  results/tables/final/task0010-particle-set-gate-summary.json
git status --short --branch
git diff --cached --stat
git diff --cached
git diff --cached --check
git commit -m "feat: implement gated particle set baseline"
git push origin main
```

Local helpers/initial snapshot are `/private/tmp/task0010-*`; generated gate
reports/audits/acceptance/attempt reservation/build cache/editable metadata stay
ignored. None belongs in staging or a scientific model identity. No real score,
reconstruction, latent array/checkpoint/frozen artifact exists for this task.
