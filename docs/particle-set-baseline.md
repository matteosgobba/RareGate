# Compact particle/set baseline — Task 0010

**Implementation completed; canonical baseline pending.** The fresh-process
launch gate failed before any processed reader construction: available memory
was **3.694793701171875 GiB**, below the frozen **8 GiB** launch minimum. No real
model views, dev optimizer steps, full training, restoration, reproduction,
freeze, calibration or background profiles were reached. This is a host-resource
failure, not evidence about model convergence, CPU throughput or signal quality.

Exact evidence: [gate/resource summary](../results/tables/final/task0010-particle-set-gate-summary.json),
[handoff](handoffs/0010-particle-set-baseline.md), [executable configuration](../configs/models/compact_particle_set_autoencoder_v1.json).
The [design report](particle-set-baseline-design.md),
[design-only specification](../configs/models/particle_set_baseline_design_v1.json)
and [analytic budget](../results/tables/final/task0009-particle-set-design-budget.csv)
remain unchanged historical sources. Task 0009 was committed at `96ef5aa`; the
Task 0010 starting tree/index were clean. No prerequisite commit is pending.
Remote push/hosted CI have not been verified.

## Implementation and configuration fidelity

The new type is `compact_particle_set_autoencoder`, executable config schema1 /
runtime config1 and artifact schema1. It binds design content SHA-256
`3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67`.
Executable config canonical-JSON SHA-256 is
`48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b`.
Neither is a trained-model hash.

Mapping: copy design `input`, `architecture`, `objective`, `score`, `roles`,
`resource_gate`, `calibration_preregistration` and `numerical_acceptance` without
changes; rename `training_preregistration` to `training`; add executable status,
model type, schema/runtime versions and the design hash. Descriptive candidate
comparison/roadmap fields stay in design documentation. Validation compares the
complete executable canonical JSON to this mapping; even bool/integer confusion
or extra fields are rejected. Existing AE/PCA parsers are unchanged and do not
accept the design-only JSON. No dependency version, model choice, numerical
policy, learning rate, seed, cardinality or horizon changed.

`models/particle_set.py` implements five biased shared Linear layers in the exact
construction and serialization order, with FP32 parameters:

| Layer / operation | Result shape | Activation | Parameters |
| --- | --- | --- | ---: |
| Sanitize excluded input before e1 | [B,384,4] | where(mask,X,0) | 0 |
| e1 4→16 | [B,384,16] | ReLU, not in place | 80 |
| e2 16→8; zero padding | [B,384,8] | ReLU, not in place | 136 |
| local 8→2; zero padding | [B,384,2] | Linear | 18 |
| Mean h over valid count | [B,8] | FP64 sum/division, cast FP32 | 0 |
| Concatenate local then broadcast context | [B,384,10] | None | 0 |
| d1 10→16 | [B,384,16] | ReLU, not in place | 176 |
| d2 16→4; zero padding | [B,384,4] | Linear | 68 |
| Total | 478 values, 1,912 FP32 bytes | | **478** |

The shared stateless ReLU module is called at the three prescribed locations.
No skip, attention, learned query, input position, normalization, dropout, count
head or auxiliary loss. `encode(X,M)` returns local code and context;
`reconstruct(X,M)` / forward returns Y; `score(X,M)` returns a NumPy FP64 [B]
vector, following the common evaluation interface. Network inputs can be owned
FP32/bool NumPy arrays via the score adapter or CPU tensors; no dtype cast is
implicit. Differentiable training loss uses only tensors.

Capacity is **2*n_retained+8**, up to776 floats plus validity metadata. Local
codes are an intentional information path; this is not eight-value event-only
compression. Small-n events can transmit essentially all particle information
through context. Learned joint particle features and means retain information
absent from eight fixed aggregates, without demonstrating arbitrary pairwise
geometry, rotation invariance or IRC safety.

## Loss, score and mask behavior

Public input requires FP32 [B,384,4], boolean [B,384], B≥1, at least one valid
particle/event and a prefix mask. Valid sin/cos norm-squared error must be ≤2e−6
in FP64. Nonfinite input anywhere, including padding, is rejected. Finite excluded
values are sanitized before e1. Local codes/output and excluded input gradients
are exactly zero. An explicitly private `_forward_set` boundary accepts mask
holes for permutation tests; the public/reader contracts remain strict.

For each corresponding valid particle:

```text
r = float64(X) - float64(Y)
d_i = (r0² + r1² + 0.5*r2² + 0.5*r3²) / 3
L_event = score = sum_valid(d_i) / n_retained
L_batch = mean(L_event over actual batch events)
```

Subtraction happens after conversion to FP64. Casts and reductions preserve
training autograd into FP32 parameters/gradients/Adam states. Online history uses
actual event counts, including the tail; selection and restored reporting use
source-ordered score vectors and their FP64 population mean. Online training
objective is distinct from the restored-model training score. No unweighted MSE
label or comparison of its raw magnitude with PCA/AE SSE.

Sin/cos outputs remain unconstrained. Angular residuals are seam-continuous;
zero and off-circle predictions are finite and penalized by the existing squared
residual. No normalization, atan2, projection, circle/count term or matching.
Larger score means more anomalous. No clipping or post-hoc correction. Parameters,
intermediates, reconstructions, losses, gradients and Adam state are checked for
finiteness; optimizer state must be FP32. Failures abort visibly.

Outputs/local codes are equivariant; global context and score invariant within
Task 0009's exact prescribed tolerances/domain. Correspondence follows the local
particle code, not rank alignment between unordered generated sets. Uniform
replication remains mean-score blind within capacity, isolated residuals can be
diluted, and count is supplied rather than independently reconstructed. Original
multiplicity/retained-pT fraction and dropped particles remain outside the model.

## Bounded loader, guards and artifact policy

`models/particle_background.py` rejects test/unknown/truth/incorrect-stage roles
before reader construction. Dev admits train only; fit admits train/selection;
postfreeze calibration requires every completion gate plus canonical identity.
The fit API also verifies factory roles before use and accepts no calibration
argument. One verified `ProcessedStore` stays open per run; construction performs
existing full custody verification only after launch gates permit it.

The reader's optional `iter_batches(order=...)` validates a complete integer
split-relative permutation before particle reads, then uses existing bounded
`_batch` routing. Membership filtering occurs once per epoch. Existing sequential
API, truth checks and test opt-in semantics remain unchanged. This task never
invokes final test evaluation or adds particle support to that gate.

The loader calls `EventBatch.model_view(nmax=384)`, streams≤32 events and keeps
physical aggregates/IDs/counts/retention metadata separate. It never uses the
aggregate loader as particle input. Allowed IDs/shuffle indices are cached; padded
populations, reconstructed populations and local-code populations are not.
Dev membership is exactly the first1,024 source-ordered dev-train IDs; training
permutations use the dedicated seeded generator, scoring uses source order.

Audits persist each population request before model views, including purpose,
scope, representation and disabled test/label flags. Counts advance after each
bounded view in an append-only small journal; completed/failed requests finalize
the JSON snapshot. Exceptions preserve failed status/counts. This avoids writing
an ever-growing full audit on every training batch. An exclusive Task0010 attempt
budget and output directory prevent changing a directory name to silently retry.

Artifact parsing has a distinct type/schema, design/config/input/loss/score
identities, exact ordered FP32 values and prescribed names/shapes. Candidates
require explicit diagnostic opt-in; ordinary loading accepts only frozen models.
Freeze requires full counts/source/store/split scope, strict patience outcome,
best/stopping relation and all correctness/resource/restoration/reproduction
flags. Corrupt, incompatible, dev or incomplete masquerades are refused. No
canonical artifact or narrow ignore exception was created because freeze was
not reached. Existing PCA/AE artifacts/loaders remain intact.

## Resource measurement, interruption and gate outcome

Native CPU tensor/workspace accounting has two independent parts:

- **Measured tensor allocations:** PyTorch CPU memory-allocation timeline on a
  synthetic full384/batch32 forward/loss/backward/Adam workload, including
  temporaries and two synthetic updates to cover initialized optimizer state.
  Measured peak **5,228,448 bytes (4.986236572265625 MiB)**. This is an allocation
  measurement on synthetic values, not the analytic Task0009 inventory or a
  measurement of real training memory/latency.
- **External native workspace:** Darwin `malloc_zone_statistics(NULL)` arena
  reservation, sampled alongside resources, conservatively includes framework,
  Python/NumPy and native malloc workspace as well as tensor allocation. Its
  all-heap reservation is checked against512MiB; clean mapped store pages are
  separately included in process lifetime peak RSS. Unsupported accounting fails
  closed. A 50ms monitor, per-batch checks, SIGALRM wall deadlines and parent
  worker deadlines interrupt violations; controlled synthetic tests exercise
  interruption and downstream refusal. Sampling is not a general exact profiler
  of arbitrary external/VM allocations; the selected CPU operator set and
  measured tensor temporaries bound the intended reference implementation.

Available memory is explicitly `(free_pages+inactive_pages)*page_size` from
Darwin `vm_stat` (same conservative operational convention used for launch and
monitoring). Compressed, speculative and active pages are not counted as
available. Lifetime RSS comes from `getrusage`, Darwin bytes. Measurements and
engineering boundaries remain outside model scientific identity.

| Reached gate measurement | Actual | Frozen limit | Outcome |
| --- | ---: | ---: | --- |
| Available memory at launch | 3,967,254,528 bytes /3.694794GiB | ≥8,589,934,592 bytes /8GiB | **Fail** |
| Worker lifetime peak RSS at launch | 356,663,296 bytes /0.332169GiB | ≤6GiB | Below ceiling at launch only |
| Native heap arena reservation at launch | 184,205,312 bytes /175.671875MiB | ≤512MiB | Below ceiling at launch only |
| Worker elapsed including startup | 1.341742s | Dev≤300s | Interrupted at launch |
| Supervisor whole attempt elapsed | 1.557991s | Bound preserved | No dependent stage |

The initial check failed before reader construction and before the resource
monitor could authorize real processing. Population requests0, unique real
events0, optimizer steps0, passes0. Train/score-pass timings and frozen-factor2
extrapolation are **not available**. A synthetic allocation check and small
launch RSS do not replace the missing real dev/workspace/throughput gate.

No attempt was repeated, no application/process was killed to free memory, and
no batch/device/thread/horizon/factor/architecture limit was changed. The ignored
attempt ledger/audit/failure snapshot are retained. The next task must make a
bounded recovery decision and verify≥8GiB availability before another launch;
the original96-step dev allowance is entirely unused. Inference benchmark work
is deferred until the particle baseline's prerequisite gates are resolved.

## Implemented conditional stages — not executed on real populations

The orchestrator requires source-bound synthetic acceptance before launching a
fresh CPU process. It enforces the frozen sequence and limits: dev≤300s; each
full train+selection cycle≤180s; fitting/selection≤36,000s/run including startup/
verification; total postfit≤3,600s/run; two complete repetitions≤79,200s. Remaining
postfit budget subtracts restoration/reload time before background work. A parent
ceiling includes startup/store verification and terminates an over-budget worker.
Completed history is emitted only after both populations and deadline checks;
interrupted/partial epochs cannot become selected published history.

Full fit uses CPU seed1729/default ordered FP32 Linear initialization; separate
shuffle generator1729 advanced each epoch; explicit Adam lr.001/betas(.9,.999)/
eps1e−8/zero decay and all design switches; batch32/workers0/tail retained; one
intra/inter-op thread; deterministic algorithms and no AMP/schedule/clipping/
accumulation/fallback. Strict full-selection mean improvement, min_delta0,
patience20/max200, earliest ties and patience priority at200 are implemented.
Cap/resource failures remain convergence unresolved, with no freeze/calibration.

After a successful patience endpoint, conditional code restores best, writes an
ignored candidate, reloads exact parameters and independently verifies selected
score bytes/mean. Two fresh fits must have identical scientific artifacts/history/
shuffle/selected scores. Freeze is then separate. Conditional postfreeze scoring
uses bounded source-ordered batches and memory-only compact vectors; summaries,
KS, higher calibration quantiles, strict>threshold, counts/Wilson/zero-count
handling are reused. Diagnostics use train-defined linear-quantile bins with
merged ties/overflow/empty-bin reporting and frozen transfer. These paths have
synthetic coverage but actual convergence, reproduction and real-data behavior
are unverified. No finalized model, real histories, thresholds, distributions or
profiles are claimed or curated for stages not reached.

## Actual validation and reproduction commands

**247 synthetic tests pass** (167 prior +80 particle-specific). Coverage includes
exact config mapping/initialization/parameters, independent numeric loss and
angle cases, mask/cardinality/permutations/gradients, dtype/nonfinite rejection,
real reader methods on synthetic records, shuffle/tails/guards/audit failures,
strict stopping/restoration/cap, artifacts/freeze refusal, live deadline
interruption, optimizer precision and failed-gate/retry refusal.
Prescribed tolerances were not loosened. An initial numeric test used random
FP32 targets minus1, whose stored residual was not exactly1; corrected the
hand-computable fixture to exactly representable0/−1. No model/loss changed.

Editable installation succeeds, package0.1.0 imports from the operational source,
dependency consistency passes, Ruff lint/format pass, CPU model smoke and exact
478/1,912 checks pass. Initial sandbox build-backend network resolution failed;
the authorized installation completed with `--no-deps`, leaving runtime versions
unchanged. PyTorch2.14.1/NumPy2.5.3/Python3.12.12 remain the reference environment.
No generic MPS smoke or particle MPS experiment was needed/run. Hosted CI is
unverified. Documentation links/exclusions/historical hashes/diff checks are in
the handoff.

Safe synthetic reproduction in the editable checkout:

```bash
.venv/bin/python -m pip check
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pytest -q
```

The gated command actually executed was:

```bash
.venv/bin/python -m latenttrigger.models.particle_background \
  --acceptance data/task0010-synthetic-acceptance.json
```

It exited1 with a preserved launch failure. Do not rerun/delete its attempt
ledger to bypass this outcome. The local acceptance record binds all source/test
hashes/config to the passing suite and measured synthetic workspace. New code
requires renewed synthetic acceptance; new real attempts require the next bounded
decision. Large artifacts/logs/audits/pip cache/acceptance remain ignored under
`data/`; only the factual small gate summary is curated now.


Final review corrected the total canonical-run timer to start after the separate
dev stage, preserving the exact22h canonical budget rather than charging dev
time to it. The247-test suite, lint/format and synthetic workspace measurement
were revalidated. Original gate-attempt acceptance remains preserved in
`data/task0010-synthetic-acceptance.json`; final source-bound acceptance is
separate in `data/task0010-final-synthetic-acceptance.json`. No real attempt was
repeated and the recorded launch outcome is unchanged.

## Exposure and remaining limitations

No real processed reader opened; no raw/NPY particle/features/labels read.
Only small config/manifests/report metadata were inspected. Every new real
model/evaluation population count is zero, including train/selection/calibration.

```text
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

PCA and canonical AE v2 are unchanged. Particle model implementation exists;
canonical fitting/convergence/restoration/reproduction/freeze/calibration and
signal sensitivity are pending. Mean dilution, uniform-replication/count
blindness, local capacity, truncation, off-circle outputs and eight-mean context
limitations remain. Selection will be reused for early stopping, calibration
for threshold estimation; neither supplies every form of untouched validation.
No export, quantization, latency claim or trigger-readiness evidence was created.
