# Task0026 — Accepted guarded frozen PCA/AE scientific evaluation

**Phases A and authorized B complete and accepted. Both held-out populations are
now exposed.** One approved frozen-plan campaign completes PCA, AE and reporting
with normal exits/reaping in31.094950s;4requests/124batches/500942scored presentations,
250471unique test events. No fitting/optimizer/recalibration/candidate selection.

[Original prompt](prompts/0026-guarded-pca-ae-evaluation.md),
[actual Phase B approval](prompts/0026-phase-b-authorization.md),
[handoff](handoffs/0026-guarded-pca-ae-evaluation.md),
[unchanged protocol](../configs/evaluation/frozen_pca_ae_final_v1.json) and
[curated summary](../results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json).
Original Phase A handoff/report are retained in commit e69d80ed and ignored snapshots;
its readiness/implementation record follows the accepted scientific results below.

## Accepted Phase B scientific findings — 2026-10-09

The human explicitly authorized the unchanged plan in
[the actual Phase B message](prompts/0026-phase-b-authorization.md).
All130source/dependency and scientific/config/calibration/store/plan identities
matched; Phase A acceptance/readiness reused without another readiness action.
At continuation, clean main/origin/main HEAD
`e69d80ed802492be3db965d0ab69ce3e1a50395d` is the verified Phase A commit;
this is the Phase B execution base, not an invented result commit.
Human message is stored in the fixed ignored authorization audit and copied into
the campaign; its file-byte hash is in the curated summary/receipt lineage.

Exactly one final reservation/campaign, fixed PCA→AE→consolidation order, all
processes exit0/reaped/parent_accepted. Whole31.094950s≤600s; no failures, replay,
resume, policy/source changes or test-guided model/threshold selection. Two
candidate constructors still freshly verify full custody as required by the
approved plan; they are not a repeat of the consumed Phase A readiness action.

Both test populations are **now exposed**. Four model/population requests,
124complete score batches,500942confirmed read/scored presentations and250471unique
held-out events. Per candidate:37background batches (36×4096+3015) and25signal
batches (24×4096+1696), source order/complete tails, no uncertain in-flight access.
No train/selection/calibration model population or optimizer update. Never call
these tests untouched or tune candidates against their newly observed behavior.

| Candidate | ROC-AUC | AP | Test background | Test signal | Signal prevalence |
| --- | ---: | ---: | ---: | ---: | ---: |
| PCA-v1 | 0.468488657947 | 0.364379154950 | 150471 | 100000 | 39.924781711% |
| Compact AE v2 | 0.660063802527 | 0.547427268325 | 150471 | 100000 | 39.924781711% |

Prevalence100000/250471=39.924781711256% belongs to the **evaluated held-out
mixture**, not the entire source or physical LHC rates. The figure's "released
sample" label refers to this evaluated mixture. AP depends on prevalence; constant
score AP equals that mixture fraction. AE AP0.547427 is above it; PCA AP0.364379
is below. ROC-AUC uses the supplied higher-SSE orientation; PCA0.468489 is below
0.5 on this sample. No post-test inversion is introduced to improve that result.
No preregistered AUC/AP uncertainty/significance test or extra metric search.

### Calibration-frozen operating points

| Candidate | Calibration target FPR | Frozen threshold | Background accepted /150471 | Realized FPR % [Wilson95%] | Signal accepted /100000 | Signal efficiency % [Wilson95%] | Rejection |
| --- | ---: | ---: | ---: | --- | ---: | --- | ---: |
| PCA-v1 | 0.1 | 0.3496768162794852 | 14922 | 9.916861 [9.766864,10.068905] | 4620 | 4.620000 [4.491628,4.751858] | 10.083836 |
| PCA-v1 | 0.05 | 0.5642097175249418 | 7362 | 4.892637 [4.784791,5.002787] | 852 | 0.852000 [0.796893,0.910883] | 20.438875 |
| PCA-v1 | 0.01 | 1.423214690513889 | 1416 | 0.941045 [0.893498,0.991097] | 90 | 0.090000 [0.073233,0.110601] | 106.264831 |
| PCA-v1 | 0.001 | 4.135648336029186 | 124 | 0.082408 [0.069128,0.098237] | 2 | 0.002000 [0.000548,0.007293] | 1213.475806 |
| Compact AE v2 | 0.1 | 3.478338537407165 | 14793 | 9.831130 [9.681718,9.982593] | 23217 | 23.217000 [22.956344,23.479714] | 10.171770 |
| Compact AE v2 | 0.05 | 4.681070974717348 | 7357 | 4.889314 [4.781503,4.999429] | 13608 | 13.608000 [13.396886,13.821910] | 20.452766 |
| Compact AE v2 | 0.01 | 8.324174660133213 | 1424 | 0.946362 [0.898679,0.996549] | 3298 | 3.298000 [3.189096,3.410492] | 105.667837 |
| Compact AE v2 | 0.001 | 16.64221886862157 | 116 | 0.077091 [0.064285,0.092447] | 56 | 0.056000 [0.043131,0.072706] | 1297.163793 |

Every threshold remains the original background-calibrated value, strict score>τ.
Wilson95% intervals are binomial rate summaries conditional on frozen thresholds
and sampling assumptions, not joint calibration/model/simulation uncertainty.
Achieved background rates are below the nominal targets; some conditional intervals
do not contain the target. This is not permission to recalibrate or a guarantee
of unseen/physical population FPR. Empirical resolutions are1/150471background
and1/100000signal. No operating point here has zero background accepted, so
rejection is finite; the unchanged protocol would report null rejection plus the
one-sided exact upper95% bound if zero occurred, never infinity.

At target1e-3, PCA keeps2signals (0.002%, Wilson0.000548–0.007293%) and124background
(0.082408%); AE keeps56signals (0.056%, Wilson0.043131–0.072706%) and116background
(0.077091%). The AE's higher observed count is real, but absolute sensitivity is
very low at this tight operating point. The PCA tail's2events give limited evidence;
do not extrapolate deeper rejection, advertise universal28×gain or trigger readiness.

### Descriptive empirical ROC points, not deployment thresholds

| Candidate | Descriptive target | Achieved FPR % | Achieved signal efficiency % | Background accepted | Signal accepted |
| --- | --- | ---: | ---: | ---: | ---: |
| PCA-v1 | FPR 0.1 | 9.998604 | 4.711000 | 15045 | 4711 |
| PCA-v1 | FPR 0.05 | 4.995647 | 0.899000 | 7517 | 899 |
| PCA-v1 | FPR 0.01 | 0.998199 | 0.097000 | 1502 | 97 |
| PCA-v1 | FPR 0.001 | 0.071775 | 0.002000 | 108 | 2 |
| PCA-v1 | TPR 0.5 | 53.417602 | 50.000000 | 80378 | 50000 |
| PCA-v1 | TPR 0.8 | 82.391291 | 80.000000 | 123975 | 80000 |
| PCA-v1 | TPR 0.9 | 91.307960 | 90.000000 | 137392 | 90000 |
| Compact AE v2 | FPR 0.1 | 9.999934 | 23.599000 | 15047 | 23599 |
| Compact AE v2 | FPR 0.05 | 4.998305 | 13.820000 | 7521 | 13820 |
| Compact AE v2 | FPR 0.01 | 0.999528 | 3.508000 | 1504 | 3508 |
| Compact AE v2 | FPR 0.001 | 0.098358 | 0.074000 | 148 | 74 |
| Compact AE v2 | TPR 0.5 | 26.916815 | 50.000000 | 40502 | 50000 |
| Compact AE v2 | TPR 0.8 | 60.426926 | 80.000000 | 90925 | 80000 |
| Compact AE v2 | TPR 0.9 | 77.503971 | 90.000000 | 116621 | 90000 |

These thresholds/points are derived descriptively from the complete final ROC,
with attainable rates, no interpolation and strict-gt encoding/explicit accept-none /
accept-all semantics. They are separate from the frozen calibration thresholds.
PCA's1e-3target reaches2signals at FPR0.071775%, rather than manufacturing an
interpolated exact0.1% point; the tie/plateau rule retains the highest cutoff
(lowest FPR) achieving the same maximum signal count. AE's corresponding74signals
at FPR0.098358% do not replace its frozen calibrated result of56signals. Full descriptive
thresholds/counts/intervals are in the empirical CSV/JSON; no test-based threshold
choice is adopted.

### Background residuals, capacity and accepted native CPU context

| Test background summary | PCA-v1 | AE v2 |
| --- | ---: | ---: |
| mean | 0.170172541029 | 1.70321526569 |
| std | 0.328760784165 | 1.68053707506 |
| min | 3.28890754053e-07 | 0.00885568855866 |
| median | 0.0927169482613 | 1.23708738032 |
| p90 | 0.347651718992 | 3.44586566837 |
| p95 | 0.556097950201 | 4.63925665669 |
| p99 | 1.38155798994 | 8.18916716322 |
| p99_9 | 3.88556480897 | 15.7209112841 |
| max | 28.4027825972 | 71.3873686527 |

These are test-background score summaries, linear quantiles/population std from
existing scientific helpers. PCA lower mean residual0.170173 versus AE1.703215
is not a quality ranking. Retained dimensions6versus3 differ; observed differences
do not isolate the causal effect of nonlinearity, bottleneck size or particular
features. No new feature-level bias diagnostic or signal-process generalization
has been measured here.

Accepted Task0022preloaded-dev CPU adapter context: median of three worker p50s
B1PCA8.125µs /AE24.708µs; B1024PCA44.4585µs /AE85.5µs. Pooled B1024throughput
22.324739M /11.871389M events/s comes from600invocations per model. These are
historical scoped native inference costs, not new contemporaneous repeats,
Task0026end-to-end latency or physical trigger capacity. B4096evaluation wall
contains custody, metrics, audit, serialization and resource checks; do not divide
it into a new inference benchmark. Task0025provisional speed ratios are not used.

### Actual resource/lifecycle acceptance and remaining limits

| Stage | Worker body s | Parent-observed lifecycle s | Exit / reap | Observed RSS GiB | Whole native MiB | Unaccounted terminal s |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| PCA | 10.126706 | 10.464501 | 0 / yes | 2.228317261 | 209.250000 | 0.338449541 |
| AE | 8.446787 | 8.714494 | 0 / yes | 2.717468262 | 199.671875 | 0.268158750 |
| consolidate | 11.155332 | 11.446585 | 0 / yes | 0.405334473 | 252.093750 | 0.292504583 |

Parent peak30343168B=28.9375MiB≤128MiB. Largest observed worker RSS2917859328B
and whole-native264339456B remain below6GiB/512MiB; RSS/native overlap, peaks
include constructor/setup/diagnostics, not isolated model allocations. Both
candidate lifecycle intervals are≤120s, consolidation11.446585s≤30s, whole
31.094950s≤600s. Model-population scoring+metrics+serialization spans0.509961s
PCA /0.519485sAE; those combined intervals are not pure forward timing. Constructor
custody spans6.407523s /5.847427s and consolidation reporting9.152711s are separately
recorded. Imports/thread setup/cleanup stay inside deadlines.

Every body guard closes without latch; every child exits normally and is reaped
before parent acceptance. Terminal memory gaps0.338450/0.268159/0.292505s are
explicit; no continuous/full-lifetime resource certificate or hard-real-time promise.
Pressure queries are unknown/errno1 and disclosed; global availability contextual,
no floor/readiness loop/app/cache/privilege changes. Shared-host variability remains;
no inference of dedicated thermal/power state or causal optimization.

### Curated outputs and validation

[Scientific comparison CSV](../results/tables/final/task0026-pca-ae-scientific-comparison.csv),
[frozen calibrated operating points](../results/tables/final/task0026-pca-ae-calibrated-operating-points.csv),
[descriptive empirical operating points](../results/tables/final/task0026-pca-ae-empirical-operating-points.csv),
[curated ROC/PR figure](../results/figures/final/task0026-pca-ae-roc-pr.png)
and the existing [summary](../results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json)
retain exact values/counts/intervals/provenance. Figure is a byte-identical copy of
the accepted campaign output and visually inspected; curve/score arrays remain
ignored, along with authorization/unblinding/raw execution evidence. No numerical
population replay or new model artifact during curation/metadata validation.

The1259full/portable/80newcase software acceptance from Phase A is reused exactly;
no executable/protocol/dependency change means no redundant synthetic-suite claim.
Phase B final checks independently validate source/authorization/plan/model /
calibration/store/output/receipt/grant identities, durable request/batch/exposure
arithmetic, rate/interval/CSV/JSON/report agreement, figure hash/visual quality,
links/whitespace/Git exclusions. Fresh read-only Ruff lint and format checks
pass (217 formatted files), and pip reports no broken requirements. Pip disables
its inaccessible user cache without any dependency or permission change.
Hosted CI remains unverified.

### Supported conclusion and one next task

For these two frozen native aggregate baselines on this held-out signal mixture,
AE has a better observed ranking and more accepted signal at all four original
calibrated thresholds, with higher accepted CPU cost. Discrimination is modest,
and sensitivity at tight background rejection remains poor. PCA's frozen higher
residual is not a useful high-tail selector for this signal in these measurements.
This is evidence about the declared candidates/sample, not universal neural
superiority or proof that nonlinearity caused the difference. No candidate is
retrained/recalibrated/selected in response; both frozen comparison identities persist.

Recommend **Task0027 — Frozen scientific synthesis and quality/cost frontier**,
using only accepted Task0026tables/figure and Task0022native CPU cost summaries to
produce the integrated scientific report/frontier, finite-sample/capacity/input /
preprocessing/host limits and reproducibility package. No new population/scoring,
model/threshold selection, export or hardware branch is required. New model
development cannot reuse these tests as untouched: it needs a separately explicit
methodological decision and new evaluation protocol/population. No Task0027work
implemented here. Particle192/192and local canonical deferral unchanged;
Task0025failed/consumed/unknown shutdown remains preserved.

```yaml
test_background model/evaluation accessed: YES
test_signal model/evaluation accessed: YES
```

Optimizer updates0. This first scientific evaluation is accepted and consumed;
no replay/resume allowance remains.

## Preserved Phase A implementation/readiness record

## Actual state and preserved scientific history

Phase A initial main tracked origin/main, clean index and working tree, full HEAD
`2f3cde01c9a2c91780d22df791c897891338fdc5` is the verified Task0025 commit.
Task0024 is `cacaefd3ac00a6c657b14109eb19e0119e25ada4`.
Living memory/index reconcile the actual commit; old handoffs retain task-time meaning.
Initial ignored snapshot hashes 1,229 prior files; all 121 prior source/dependency
entries and old scientific/configuration/acceptance/receipt/result bytes remain.
Only README/project-memory/index receive current-state overlap edits.
Synced sources are read-only; no staging/commit/push or installed-package changes.

Task0025 stays failed/consumed despite complete 90-cell numerical/timing coverage:
ORT3 completed body receipt, parent timeout/−15/reaping, provisional statistics and
unknown exit cause are preserved. No repair/replay or speedup reinterpretation.
Task0022 remains the accepted native CPU-cost reference; Task0024 ONNX equivalence
is valid, not a third scientific candidate. Task0023 device outcome is not rerun.
Particle 192/192 remains consumed/canonical locally deferred. This prospective short
evaluation policy grants no particle fitting/time extension or new dev allowance.

## Frozen candidate and input registry

| Candidate | Config | Artifact | Calibration | Model scientific SHA256 |
| --- | --- | --- | --- | --- |
| PCA-v1 | `configs/models/pca_baseline.json` | `data/baselines/pca-v1/model.json` | `results/tables/final/task0006-pca-background-results.json` | `d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f` |
| Compact AE v2 | `configs/models/compact_autoencoder_v2.json` | `artifacts/models/compact-autoencoder-v2/model.json` | `results/tables/final/task0008-autoencoder-convergence-summary.json` | `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b` |

Actual file-byte hashes, canonical config JSON hashes, scientific model/calibration
hashes and relationships are explicitly bound in protocol/summary. Use the existing
canonical loaders and full-scope validators; neither fitting validator is weakened.
PCA six components, centered/non-whitened FP64; native AE 8 → 6 → 3 → 6 → 8,
155 exact FP32 parameters, best selected epoch 381/stopped 396 state unchanged.
AE v1 stays historical. Both canonical scores are eight-channel SSE, higher anomalous;
AE casts input and reconstruction to FP64 before subtraction. No score flip,
ONNX substitution, fitting, optimizer, model choice or recalibration.

| Calibration target FPR | Frozen PCA threshold | Frozen AE v2 threshold |
| ---: | ---: | ---: |
| 0.1 | 0.3496768162794852 | 3.478338537407165 |
| 0.05 | 0.5642097175249418 | 4.681070974717348 |
| 0.01 | 1.4232146905138892 | 8.324174660133213 |
| 0.001 | 4.1356483360291865 | 16.642218868621573 |

All decisions remain strict score > threshold; ties rejected. Calibration artifacts
supply thresholds; no calibration/selection/training population reread is planned.
Six versus three latent dimensions do not isolate linearity at equal capacity.

Full processed store `data/processed/lhco-rd-v1/schema-v1/full`, scientific SHA256
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`;
split identity `74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea`.
Eight features/order and frozen preprocessing/scalers verify against full training
provenance. Manifest `config_sha256` denotes the configuration **file-byte** hash
`2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`;
the same JSON's canonical hash is
`4eae7a9f689ad8bd9faaa56f439e33540fddc586a8e9a51be96ea78dc52ec8ea`.
They are separately typed, not assumed interchangeable. Before readiness, checks
used small metadata only; freshness of multi-GB payload verification comes only
from the single authorized constructor check.

## Isolated execution and complete lifecycle

Eight new evaluation modules reuse unchanged scientific loaders/reader/metrics /
thresholds/native thread controls. The old `evaluation.run.run_final` route remains
byte-identical. Because it lacks durable batch progress and guards, the new route
wraps its unchanged primitives, with exact scientific equivalence tests for both
model families. Stdlib parent; fresh sequential CPU workers; at most one numerical
child. No ONNX session, MPS query, export, quantization or library replacement.

Pinned Python 3.12.12 / NumPy 2.5.3 / Torch 2.14.1 / sklearn 1.9.1, all existing
optional/core package versions/files and Torch build identity are verified.
All five CPU thread environment variables are 1 before imports; Torch intra/inter
1, deterministic algorithms/inference mode, OpenMP pools 1 and Accelerate mode 1
are checked before/after. No backend search, changed batching or precision.

Fixed namespace: `results/evaluation/task0026-frozen-pca-ae/`, distinct atomic
`readiness/` and `final/` reservations. A readiness reservation consumes only its
one custody check. Existing/foreign/partial/completed state refuses reset/retry;
no alternate path/selector. Parent/nonce/phase/predecessor/source/acceptance/output
identities are independently rechecked; final predecessor score/audit/receipt hashes
must match before consolidation. A first-candidate failure prevents the second.

A body writes `body_complete_awaiting_exit`. Only the parent accepts normal exit 0,
reaping, deadline, complete output/identities and no latched guard/owned watcher
failure. Timeout/signal/nonzero exit cannot promote a successful body receipt.
No forced os._exit and no timeout success. Parent deadline covers imports, custody,
score/metrics/serialization, cleanup and actual process exit, including hangs after
body completion. Failed journals/dispatch/receipt evidence are preserved.

## Prospective full-store resource policy and actual custody check

| Scope | Fixed prospective ceiling |
| --- | --- |
| Numerical worker lifetime RSS samples | 6 GiB = 6,442,450,944 B |
| Whole native reservation | 512 MiB = 536,870,912 B |
| Stdlib controller RSS | 128 MiB = 134,217,728 B |
| Entire readiness action | 60 s |
| Each future candidate process | 120 s |
| Future consolidation process | 30 s |
| Whole future final campaign | 600 s |
| Terminate/kill/reap slack | 2 s inside the relevant cap |
| Periodic process checks | 50 ms scheduling intent |

New isolated guard keeps validated Darwin getrusage SELF lifetime-RSS and
all-malloc-zone reserved-byte accounting/pressure behavior, with evaluation6GiB
ceiling. Old benchmark guard's1GiB ceiling and all historical bytes are unchanged.
Fresh own-process checks precede data and phase/batch boundaries, plus periodic
intent. Invalid/missing primary accounting or CRITICAL latches; WARN advisory;
unknown pressure is explicitly disclosed/permitted. vm_stat availability is bounded
optional context ≤2 s, without floor, wait, idle window or app/cache/privilege changes.
RSS/native overlap; do not sum virtual mappings, resident pages and heap reservations.
Sampling/GIL/OS limits prevent continuous or hard-real-time enforcement claims.

Original full-custody lineage:
`data/baselines/task0013-particle-host-study/full_custody/stage-result.json`,
SHA256 `806d118bdedc1db40f923086d81605e111f3cd3bb831adbb6901f40cc0c02d4b`,
linked to its original workflow. Historical3351019520B =3.120880127GiB RSS /
206831616B =197.25MiB native was custody only, not scoring or sustained training.
6GiB is a prospective short-evaluation cap, not spare-machine-RAM evidence or
canonical particle permission. A lower new peak is not an optimization claim.

After complete software validation/source freeze, one fresh worker loaded small
frozen artifacts without forward calls and constructed the **unchanged**
ProcessedStore. Constructor verify_store freshly hashes every declared file and
validates schema/membership/labels/particle order/preprocessing/standardized features;
2,906,842,523 declared payload/file bytes. No public model population iterator or
real score was called. This integrity scan is permitted custody, distinct from
model/evaluation access to tests; it reports no physics distributions/performance.

| Actual readiness measurement | Value | Scope |
| --- | ---: | --- |
| Constructor custody | 7.041105584 s | Full unchanged constructor verification |
| Numeric imports | 1.458171875 s | Worker-covered runtime imports |
| Native thread enforcement | 0.563270584 s | Outside custody but inside worker deadline |
| Frozen artifact loading | 0.007139833 s | No model forward/population |
| Worker body/report | 9.463768834 s | Through owned cleanup |
| Parent-observed child lifecycle | 9.879654042 s | Exit 0 / reaped / accepted |
| Entire readiness | 10.173717584 s | ≤60 s, including parent/orchestration |
| Observed worker RSS | 2,264,907,776 B =2.109359741GiB | Lifetime peak at samples |
| Observed whole-native peak | 219,414,528 B =209.25MiB | Conservative zone reservation |
| Parent RSS peak | 30,261,248 B =28.859375MiB | Stdlib lifetime peak |

179 guard samples /169periodic; pressure all unknown/errno1, no fabricated NORMAL.
Guard closed/no latch; actual parent exit0 and reaping confirmed. The interval from
monitor closure to observed exit is **0.416119625 s**, whose terminal memory accounting
is unavailable. State this explicitly: accepted finite lifecycle/observed policy,
not a continuous full-lifetime memory certificate. Parent supervision remains active.
Optional availability3.17847→2.56895GiB is context, never an admission floor.
No readiness retry, new particle slot or guaranteed future scoring budget.

## Phase A preregistration record — authorization was then pending

Plan canonical JSON SHA256:
`2c97dc2ac903de4a911968bc2f97725cd3d80e18498b1003604c9e4562e3d86f`.
Local preregistered plan `data/task0026-evaluation-plan.json` binds the exact
candidates/config/calibration/store/features, scientific metrics, fixed caps,
130 source/dependency identities and software acceptance byte SHA256
`1d0e4ddcb3b0d0c9e5cb12dbd4bfb85bff00950ddfa3d4238720d5e0431662cd`.
Source/protocol/science changes require a new reviewable acceptance/plan; old human
approval must not be reused for a changed executable or scientific plan.

Order **PCA, then AE**, one pass per population/candidate, native CPU only:

| Population per candidate | Rows | Full batches ×4096 | Final batch | Score batches |
| --- | ---: | ---: | ---: | ---: |
| test_background | 150471 | 36 | 3015 | 37 |
| test_signal | 100000 | 24 | 1696 | 25 |

Totals: two candidates, four model/population requests,124score batches,
500942scored event presentations,250471unique held-out events reused across models.
Use source order, complete tails, FP32 standardized features, labels/IDs separate
from tensors. No training/selection/calibration populations or new rows are needed.

Durable `test-unblinding.json` is atomically fsynced before each population request
and each iterator read/score. Bind explicit human message/authorization/plan, actual
commit/base/dirty source, frozen candidate/config/calibration/store/split, planned
metrics/flags/counts. Confirmed reads/scored counts persist every batch; separately
retain potential in-flight read/score state. Abrupt termination cannot silently
replace exposure with zero. Failed/interrupted first request is still exposure;
no retry/resume/second candidate after failure or test-guided optimization.

Preregistered scientific outputs reuse ROC-AUC with supplied orientation, AP as
recall-increment weighting, counts/prevalence, frozen-calibration FPR/TPR and strict
ties, existing95%Wilson/exact zero-background bounds/null rejection. Descriptive
fixed-FPR0.1/0.05/0.01/0.001 and fixed-TPR0.5/0.8/0.9 points are attainable empirical
ROC points, distinct from deployable calibration thresholds. No interpolation,
tail extrapolation, significance search or new threshold fitting. Add existing
background score summaries, capacity context and accepted Task0022 CPU costs only.
Task0025 provisional ratios are not accepted deployment context.

After complete authorized lifecycle acceptance, reporting creates comparison JSON /
calibrated operating-point CSV /static ROC+PR PNG with released prevalence and
separate frozen-threshold markers. Scores/curve arrays and all execution/audit files
remain ignored; only deliberately curated small tables/figures may enter Git.
Expected scientific outputs: `final/PCA/evaluation.json`, `final/AE/evaluation.json`,
`final/comparison.json`, `final/calibrated-operating-points.csv`, `final/roc-pr.png`;
local per-candidate/root exposure, receipt and parent-acceptance records accompany them.
At the end of Phase A no real test metrics or figures existed; the accepted Phase B outputs are above.

Implemented actions:

```bash
# Already consumed: do not repeat the custody check.
.venv/bin/python -m latenttrigger.evaluation.guarded --check-readiness
# Metadata-only package preparation; no final reservation/access.
.venv/bin/python -m latenttrigger.evaluation.guarded --prepare-plan
# Only after actual explicit human consent and its bound audit record:
.venv/bin/python -m latenttrigger.evaluation.guarded --run-final --allow-test --plan-sha256 2c97dc2ac903de4a911968bc2f97725cd3d80e18498b1003604c9e4562e3d86f
```

The last command was not executed during Phase A; it was executed once after the actual human approval recorded above. It refuses before final reservation
without explicit opt-in, the unchanged plan, current acceptance/readiness and the
bound `data/task0026-human-authorization.json` record. **That file is an audit
binding, not evidence from which the agent may infer human consent.** It must only
be written after the actual human approves the presented plan; no such record was created in Phase A. The actual human message now binds the Phase B authorization record. CLI flags, elapsed time, implementation approval and readiness are
not consent. At Phase A completion the final slot and tests were unreserved/unexposed; Phase B exposure above supersedes that historical state.

## Software and final verification

1259full tests /1259portable /80newcases pass, including actual native NumPy/sklearn /
PyTorch scientific equivalence to unchanged run_final for both models. Fixtures
exercise exact full-count4096tails, correct features/truth/order/finite scores,
strict ties/empirical ROC/zero acceptance through existing metric tests, identity /
source/consent/scope/unknown-key refusal, atomic competing reservations, durable
pre-read/per-batch audit and in-flight interruption, cap equality/exceeded peaks /
malformed accounting/pressure, deadlines/cleanup/reaping and completed-body hang.
Reporting/ROC+PR/CSV tested on synthetic artifacts only. Portable copy has no
operational data/models/receipts/sources/Git; historical narrow fixture plugin is
unchanged. No installed-package modifications or ONNX integration needed.

Guarded synthetic smoke body10.004946708s /parent10.322180791s≤30s, exit0/reaped,
381550592B RSS /198311936B native, observed unknown pressure and closed guard.
Source/protocol/dependency acceptance freezes130files before real custody; all
prior bytes retained. Final validation checks small metadata, plan/receipt/grant /
acceptance/source/scientific relationships, exact access arithmetic, JSON/local
links/whitespace and Git exclusions. It does not repeat payload custody or open
scientific population arrays. Hosted CI remains **unverified**.
