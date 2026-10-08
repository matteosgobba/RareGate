# Canonical particle feasibility and project progression — Task0019

**Decision: defer local canonical particle execution under the unchanged
contracts. Advance Task0020 — Frozen PCA/AE CPU Inference Benchmark Foundation.**
This is an engineering and scheduling decision from existing evidence. Particle
convergence and scientific usefulness remain unresolved. Retain its design and
implementation for a later explicitly authorized full-store/time/environment
decision; completing the particle baseline is not a prerequisite for hardware
work on the already frozen aggregate models.

## Current operational decision

| Field | Adopted state on 2026-10-08, Europe/Rome |
| --- | --- |
| Local canonical particle execution | Deferred; not authorized and not reached |
| Active contracts | Unchanged model/scientific configuration and historical full-run resource/time contracts; shared-host-dev-v1 remains dev-only |
| Historical failures | Task0013 projection749.3431957854029s>180s; Task0015 synthetic2.1403×<3×; Task0018 projection240.72835947066707s>180s, all preserved |
| Measured evidence | Task0018 short dev completed, reader/local guards/eligible numerical parity passed; historical full custody passed separately |
| Future policy proposals | Inactive; neither larger time allowances nor process-local full-run admission is adopted |
| Remaining uncertainty | Full-epoch scaling, sustained residency/allocator behavior, shared-host pressure and interference, convergence horizon, postfit cost and particle discrimination |
| Execution authorization | Documentation only; no canonical training, new particle run, readiness or benchmark execution |
| Remaining development allowance | Original96+additional96=192 completed/192 ceiling; zero inflight; zero remaining |
| Selected next implementation task | Task0020 — Frozen PCA/AE CPU Inference Benchmark Foundation; brief below, not implemented here |

The [curated summary](../results/tables/final/task0019-particle-canonical-feasibility-summary.json)
separates observations, arithmetic, inactive proposals and this decision.
The [prompt](prompts/0019-particle-canonical-feasibility.md) and
[handoff](handoffs/0019-particle-canonical-feasibility.md) record scope and checks.

## Verified state and evidence boundary

Initial worktree/index were clean; `main` tracks `origin/main`. HEAD and the local
tracking ref both equal Task0018 commit
`5da90944d48dd05fc761d23dad77b85c1fa2da60`, after Task0017 `b194050`.
The live [index](handoffs/README.md) ended at0018 when inspected:0019 is this
decision and0020 is the next number. Local ref equality does not establish a
successful remote push or hosted CI run. Memory's old Task0018 awaiting-commit
statement is reconciled in memory revision1.12 and this later handoff. The
[original Task0018 handoff](handoffs/0018-particle-shared-host-policy.md) is intact.

Evidence reviewed includes the [Task0009 design](particle-set-baseline-design.md),
[Task0010 implementation](particle-set-baseline.md),
[Task0011 recovery](particle-set-resource-recovery.md),
[Task0012 policy review](particle-memory-policy-review.md),
[Task0013 accounting](particle-host-readiness.md),
[Task0014 receipt reconciliation](particle-monitor-performance.md),
[Task0015 bounded sampling](particle-bounded-sampling.md),
[Task0016 authorization](particle-runtime-characterization.md),
[Task0017 workflow](particle-readiness-workflow.md),
[Task0018 measured dev report](particle-shared-host-policy.md), their relevant
handoffs/curated summaries/configurations, and original small engineering records.
Old pending statements remain task-time history, not present execution permission.

This task verifies small-file bytes, canonical JSON identities, source acceptance
and receipt relationships. It performs **metadata verification**, not fresh raw
or processed-payload verification. No numerical population arrays were opened;
no store constructor, full-custody replay, readiness/worker command, training,
scoring, calibration, export or inference timing was executed. No synced
`sources/` file, executable, test, dependency, CI or active configuration changed.

### Completed development slot

The actual Task0018 chain is:

1. `data/task0018-synthetic-acceptance.json` (file SHA256
   `1a81fe8181b1bd430f0d55ccdb13363e912d8948d1347eee6e2944ec7515e047`)
   binds74 source/test entries, all still byte-identical. Its670 passing tests
   are historical acceptance, not tests rerun by Task0019.
2. `data/baselines/task0018-shared-host-dev-execution-plan.json` binds that map,
   policy, historical receipts and readiness ID. File SHA256 is
   `ce175b39027a4b149e45b986d229dd58e437b0d616c133d1fec9954ba029c24b`;
   canonical JSON SHA256 is
   `6783a29979d45b435927be9b4e012f314561db404d11b43ea83b17e6dd148f49`.
   These hash definitions are distinct.
3. `data/baselines/task0016-runtime-characterization-attempt.json` remains
   `reserved_no_retry`, reserved2026-10-08T07:18:29.914017+00:00. Its canonical
   plan hash matches the above plan. This immutable reservation is not a live
   inflight counter, an unfinished-work invitation or a new allowance.
4. `data/baselines/task0016-runtime-characterization-study/workflow.json` records
   `characterization_completed_original_throughput_failed_canonical_blocked`.
   Reader/process-readiness passed; dev completed three passes and scoring,
   with final owned-thread cleanup. `dev/dev-progress.json`, `dev/dev-gate.json`,
   final stage result and access audit agree on96 new completed updates.
5. Original Task0013 dev audit/progress records96 started/completed/zero inflight.
   Task0018 audit records96 additional started/completed/zero inflight and
   cumulative192/192. The same first1024 frozen dev-training IDs were used.

Interpret anchor **together with** completed workflow/audits: the single slot is
consumed, with no retry/manual rerun or remaining update permission. The old CLI
permission line was a preflight snapshot before reservation. It cannot override
the current anchor. No anchor, ledger, receipt or accepted source was rewritten.

Eligible diagnostic objective0.8151977394784519, same-sample mean
0.7520234728718791 and score-byte hash
`31475c619699ee85c2e44a2e74e29a32dea3a5e092b441ccfa54a9e117343a13`
match the original Task0013 records. Those are disposable diagnostics, not
frozen particle weights, convergence or an independent full reproduction.

## Training-time feasibility

The original [executable particle config](../configs/models/compact_particle_set_autoencoder_v1.json)
and [dev policy](../configs/resources/particle_shared_host_dev_policy_v1.json)
retain the exact scientific/training contracts. Recompute from the original
Task0018 `dev/dev-gate.json`, also matched to its curated summary:

```text
train_pass_seconds = [0.16781862499919953,
                      0.13851762500416953,
                      0.13835891600319883]
score_pass_seconds = 0.07742041700112168
P = 2 * (699957 * max(train_pass_seconds) / 1024
         + 74749 * score_pass_seconds / 1024)
  = 2 * (114.71271611187959 + 5.6514636234539495)
  = 240.72835947066707 seconds
```

The first/slowest training pass, both population counts,1024 divisor, factor2
and included view/guard/audit work are preserved. No probe subtraction or
favorable-pass selection. Both the historical749.3431957854029s and current
240.72835947066707s projections fail the original180s threshold. Different
policies and shared-host conditions do not establish a causal monitor speedup.

| Derived planning quantity | Recomputed value |
| --- | ---: |
| Conservative full train+selection cycle | 240.72835947066707s |
| Excess over180s, `(P/180-1)*100` | 33.73797748370393% |
| `200*P/3600` per run | 13.373797748370391h |
| `2*(200*P+3600)/3600` | 28.747595496740782h |
| `floor(36000/P)` before other overhead | 149 cycles |

149 projected cycles leave only131.474438871s arithmetically inside10h before
other costs. This is not an adopted horizon. Keep **max200/patience20/min_delta0**,
complete-selection strict checkpoint improvement (ties retain earliest), best
restoration, independent reload and exact independent CPU reproduction before
freeze/calibration. Earlier patience termination is possible but unmeasured.
Resource/epoch ceilings without patience leave convergence unresolved; neither
reducing to149 nor assuming early stopping repairs the present gate.

`180s*200=36000s=10h`; two `(10h fit+1h postfit)` allowances total22h. Equality
leaves no separate startup slack. The original10h fit deadline includes startup,
verification and cleanup, so even200 exactly180s cycles would exhaust it before
those additional costs. The180s threshold is a project engineering gate for
canonical training, **not measured trigger-inference latency**.

These calculations are conservative **small-sample planning extrapolations**,
not measured full epochs, guaranteed deadlines or convergence forecasts. The1h
postfit is a full allowance, not measured cost. Future accounting must separately
record imports/startup, full-store verification, cycle work, restoration/reload,
reproduction comparison, freeze/background scoring/calibration, cleanup, parent
overhead and total wall. Pass timing already includes view preparation/guards;
avoid adding overlapping timers as exclusive costs. Factor2 supplies planning
margin but does not certify coverage of unmodeled startup, scale or long-run costs.

## Full-store resources and ordinary shared Mac use

Original custody lineage is Task0013 plan → invocation → `full_custody-reservation`
→ stage result → audit → workflow. File SHA256 anchors:

| Original small record under `data/baselines/` | File SHA256 |
| --- | --- |
| `task0013-particle-host-plan.json` | `4f23221843818b198557d928fb2783a63d472c502eda0daa1b704bc32c3e29bd` |
| `task0013-particle-host-invocation.json` | `33f7681cdbec5644b3aae0996b4c554a4da80053b3e288730997f690d7a1d1a9` |
| `task0013-particle-host-study/full_custody-reservation.json` | `808e56c43efa703a5da75e937e1b26f4ea5ce915f6fbec88c78c0e26c71f2a54` |
| `task0013-particle-host-study/full_custody/stage-result.json` | `806d118bdedc1db40f923086d81605e111f3cd3bb831adbb6901f40cc0c02d4b` |
| `task0013-particle-host-study/full_custody/access-audit.json` | `32b14395d270594f3df1cf826e276cc9320418df9d892f1afd5888f012d5cb86` |
| `task0013-particle-host-study/workflow.json` | `2e1e826cec0aef58d827893a53f7d12c308f58085bd5028f8a0eae820f63f385` |

The invocation and reservation bind actual plan/slot hashes; result binds the
plan, historical acceptance/profile/model config and audit hash. Workflow embeds
the same passed custody result. Audit contains one completed full constructor
custody operation, no population request, zero views/updates/test access. The
4.217541792s import-inclusive operation includes3.021437708s constructor
verification/mapping; it does not measure full training. The Task0013 workflow
later fails dev throughput; a passed custody phase does not make that workflow
successful. Task0014's curated reconciliation independently agrees with it.

| Observed operation / accounting | Measured bytes / binary units | Applicable historical ceiling | Headroom |
| --- | ---: | ---: | ---: |
| Task0018 small dev lifetimeRSS | 387989504 /370.015625MiB | 536870912 /512MiB, dev only | 148881408 /141.984375MiB (27.731323%) |
| Task0018 whole malloc reservation | 188399616 /179.671875MiB | 268435456 /256MiB, dev only | 80035840 /76.328125MiB (29.815674%) |
| Task0013 full custody lifetimeRSS | 3351019520 /3.120880126953125GiB | 6442450944 /6GiB | 3091431424 /2.879119873046875GiB (47.985331%) |
| Task0013 full custody native reservation | 206831616 /197.25MiB | 536870912 /512MiB whole native | 330039296 /314.75MiB (61.474609%) |

The dev manifest records8494events and23046077 persistent file bytes; full
custody maps2905652652 virtual array bytes. Virtual mappings are not resident
pages or anonymous allocations. LifetimeRSS includes mapped residency; whole
native reservation overlaps RSS, frameworks and tensor allocations. **Do not add
RSS/native as disjoint allocations.** A6GiB process ceiling is not a promise
that a shared16GiB machine has the remaining capacity available. Custody headroom
cannot validate optimizer/epoch/postfit residency, allocator retention, OS cache
effects or hours of concurrent use. The512MiB dev RSS ceiling cannot contain the
observed full-custody footprint, and its256MiB native ceiling is not a validated
full-run policy even though custody's observed native peak is smaller.

Process-local full-run budgets with contextual global telemetry are a defensible
architecture to review: bound the owned workload instead of demanding an idle
Mac. Existing evidence is insufficient to adopt or validate that policy for
hours of full-store work. The historical6GiB RSS/512MiB native ceilings are
starting limits to assess, not a newly validated canonical envelope. Such a
separate decision must specify independent primary accounting, cap equality,
fresh phase/batch/pre-step and periodic checks, import-inclusive parent deadlines,
latched failures, durable attempt/update history and cleanup under blocked native
calls. Sampled accounting/GIL/OS delivery cannot guarantee instantaneous stopping.

An **inactive conservative full-run pressure proposal** would admit NORMAL only
with other proven gates; WARN would veto/latch, CRITICAL would veto/latch, and
unavailable pressure would block long-run admission rather than be called NORMAL.
Malformed primary measurements fail closed. Any alternative WARN/unknown treatment
would require an explicit bounded rationale and enforcement review before a
separately authorized run. Global free+inactive, pressure provenance and swap/
thermal context could be recorded without treating cumulative counters as free
capacity; no new metric/backend or numerical threshold is adopted here.
Task0018's seconds-long dev permission for WARN/unknown is **not** evidence of
multi-hour suitability. Its live pressure was unknown, not a measured WARN pass.

Exact remaining prerequisites for any future particle run: separately authorize
a compatible resource/time/environment policy and finite attempt budget, validate
its guards synthetically, bind current source/config/artifact identities, justify
full-store and sustained-training risk from an explicitly bounded scope, and
preserve ceiling failures/no-retry semantics before dependent canonical stages.
Task0019 grants none of those executions and replenishes no Task0016/0018 slot.
No app closure, reboot, cache/swap manipulation, privilege workaround, dedicated
window or repeated readiness polling is a prerequisite for project progression.

## Alternatives assessed together

| Route | Evidence and consequence | Decision |
| --- | --- | --- |
| Retain contracts and defer local canonical particle execution | Both projected cycles fail180s;200 current projected cycles exceed10h/run and two runs plus allowances exceed22h; full-training resource behavior unmeasured | **Adopt now.** Preserve particle branch and progress frozen aggregate CPU hardware work |
| Explicit future resource/time-policy revision | Could change feasibility by accepting a larger workload/time cost, without changing scientific objective; requires separate authorization, versioned enforcement/artifact compatibility and bounded failure handling | Inactive proposal; no threshold/config/launch change |
| Actually supported future environment | Might offer capacity/throughput, but no alternative execution host or access/runtime readiness is verified in inspected project evidence | Conditional future route; verify actual access, exact software/input compatibility and bounded execution policy before claiming support |

For the second route, an illustrative **300s** cycle ceiling with200 cycles is
60000s=16h40m per run; two such cycle allowances plus3600s postfit each are
127200s=35h20m. Imports/full custody/cleanup and any other costs still need
separate slack **above** those cycle sums or must consume their allowances.
Leaving10h/22h while merely changing180→300 would be inconsistent. This example
is **not adopted**, not measured speed or scientific improvement, and does not
resolve full-store/pressure uncertainty. A future policy must list precise
cycle/fit/postfit/overall limits, enforcement, immutable historical profiles,
engineering-vs-scientific identity rules, current source acceptance, independent
reproduction/freeze compatibility, finite attempt authorization and stop/no-retry
behavior. No silent relaxation, reduced horizon, weight reuse or automatic retrain.

The chosen route is therefore **Task0020 on frozen PCA and compact AE v2**.

## Task0020 implementation brief

**Task0020 — Frozen PCA/AE CPU Inference Benchmark Foundation** is the next
implementation task after this decision, subject to rechecking the live index.
This brief is inactive planning; Task0019 does not implement or execute it.
Task0020 should implement and synthetically validate the bounded benchmark, then
perform only its explicitly authorized single campaign. It needs no separate
readiness/monitor-design task and no particle development slot.

### Frozen inputs, models, calibration and numerical boundaries

| Identity / actual path | Frozen identity |
| --- | --- |
| `configs/data/lhco_rnd_v5.json` | File SHA256 `2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68` |
| Split membership | Scientific SHA256 `74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea` |
| `data/processed/lhco-rd-v1/schema-v1/dev/manifest.json` | Scientific SHA256 `2eb34e5b811c12ae5c47afba1ecdb6322feb7c7774b6c9ec5331abe78b3c9a2a` |
| Full training provenance, `.../schema-v1/full/manifest.json` | Scientific SHA256 `d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2` |
| `configs/models/pca_baseline.json` | Canonical JSON SHA256 `e61e43bc57afc010286bf2b1deff91167b4951644d52d882ecbd1cf10f938f95` |
| `data/baselines/pca-v1/model.json` | Scientific SHA256 `d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f` |
| `results/tables/final/task0006-pca-background-results.json` | Scientific SHA256 `285a254847424870b5bee08e5a218733dcbe553ff7a4d00ec5c9493288600ccb` |
| `configs/models/compact_autoencoder_v2.json` | Canonical JSON SHA256 `0af02cba0dcab4cd750b19f6357fe5030aadb56c7c0422c4f35ea4adc1521800` |
| `artifacts/models/compact-autoencoder-v2/model.json` | Scientific SHA256 `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b` |
| `results/tables/final/task0008-autoencoder-convergence-summary.json` | Scientific SHA256 `324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33` |

All these small identities were recomputed from JSON/config bytes in Task0019;
recorded payload digests were not recomputed. Model artifacts retain full-store
training provenance; dev timing does not turn them into dev-trained models.
Preserve [AE v1](../artifacts/models/compact-autoencoder-v1/model.json) and its
configuration/results as history. No fitting, checkpoint selection, calibration,
parameter conversion, model export or threshold regeneration.

Use existing schema1 `event_features` FP32 `[B,8]`, standardized with training-only
frozen scalers. Order: multiplicity, scalar_pt, max_pt, pt_balance,
weighted_eta_mean, weighted_eta_std, pt_concentration, massless_event_mass.
Multiplicity/scalar_pt/max_pt/mass use their frozen log1p transforms; the other
channels retain their specified transforms; all are standardized before the
single FP32 output cast. They derive from **all** physical particles before
truncation. Read exact means/stds from the hashed configuration; do not reapply a
scaler to already standardized inputs. Labels/IDs/splits never enter model tensors.

PCA: six retained components, centered non-whitened reconstruction in CPU FP64,
`x_hat=(x-mu)@W.T@W+mu`. AE v2: frozen155 FP32 parameters,8→6→3→6→8, hidden ReLU,
linear latent/output, best381/stopped396; CPU FP32 forward. Each model's canonical
score is SSE across eight standardized channels, FP64 subtraction/squares/sum,
higher anomalous. AE input/reconstruction must be cast **before** subtracting.
Use [PCAReconstruction](../src/latenttrigger/models/pca.py) and
[CompactAutoencoder](../src/latenttrigger/models/autoencoder.py) loaders and
canonical `reconstruct`/forward/`score` implementations for references.

Frozen `higher` calibration thresholds, strict `score > threshold`, from74823
calibration events (load small results only; do not reopen calibration inputs):

| Target FPR | PCA threshold | Compact AE v2 threshold |
| ---: | ---: | ---: |
| 0.1 | 0.3496768162794852 | 3.478338537407165 |
| 0.05 | 0.5642097175249418 | 4.681070974717348 |
| 0.01 | 1.4232146905138892 | 8.324174660133213 |
| 0.001 | 4.1356483360291865 | 16.642218868621573 |

Threshold/model/provenance links must match before data. Report each model's own
scores/decisions and sample counts, not a ranking from their different residual
scales/compression capacities or dev acceptance interpreted as calibrated FPR.
No discrimination, AUC/AP or final-test measurement in this benchmark.

### Fixed bounded CPU protocol

| Choice | Preregistered Task0020 value and rationale |
| --- | --- |
| Runtime | CPU only, canonical eager NumPy/PyTorch operators; no compilation/export/AMP/quantization |
| Threads | Fresh processes; PyTorch intra-op1/inter-op1, deterministic algorithms; OMP_NUM_THREADS/MKL_NUM_THREADS/OPENBLAS_NUM_THREADS/VECLIB_MAXIMUM_THREADS/NUMEXPR_NUM_THREADS=1 before imports; inspect effective BLAS/OpenMP pools and enforce1 using existing threadpoolctl if needed; fail unsupported enforcement rather than claim1 |
| Precision | Stored inputs FP32; prepared PCA input/computation FP64; AE weights/forward FP32; both scores/thresholds FP64 |
| Sample | First1024 source-ordered IDs of existing dev `train_background`, `dev_only=True`, `allow_test=False`, `include_labels=False`; same1024 for both models, no score-dependent selection |
| Preparation | One fresh worker≤60s including imports, full **dev** constructor verification and cleanup; one `iter_features` batch1024 then stop; close store; persist ignored exact input/ID hashes and bounded prepared1024×8 input. No full-store constructor or payload hash |
| Batch grid | `[1,8,32,128,1024]`; divisors of1024 cover individual request, small batches and throughput without growing the sample |
| Repetitions | Three fresh workers per model, six total; fixed dispatch PCA1,AE1,PCA2,AE2,PCA3,AE3 to reduce family/time confounding; no timing-selected retry |
| Per-worker order | Batches ascending, scopes reconstruction → score/decision → canonical adapter+decision; fixed order and shared-host/order limitation disclosed |
| Warm-up / measurement | 20 untimed invocations then200 timed invocations per batch/scope/worker; cycle contiguous windows `start=(i mod (1024/B))*B`, independently reset for each phase; input slices prepared outside timed region |
| Timer / statistics | `perf_counter_ns`, synchronous CPU completion; record200 empty timer pairs separately, never subtract; per-cell count/min/max/mean/population std and p50/p95/p99 with linear quantiles; report all three workers and median of worker medians, no best-run selection |
| Throughput | B divided by measured seconds per invocation; distribution of batch invocation time and time/B kept distinct from single-event latency; no trigger deadline claim |
| Campaign budget | Preparation60s + six workers≤60s each + aggregation≤30s =450s allocated stages; parent total≤600s from campaign start includes orchestration/gaps/imports/verification/cleanup; no automatic budget extension |

1024 FP32×8 is32768 input bytes. Selection is deterministic and bounded; repeated
timing reuses those inputs and does not enlarge unique population access.
200 records support descriptive tail quantiles with modest work; p99 has limited
tail resolution and shared-host distributions are conditional observations.
Store verification reads all dev payloads as custody separately from the1024
model-input request; preserve that distinction and audit both. Existing PCA
`validate_input_store` requires full scope: the benchmark needs its own narrow
dev-inference compatibility check, without relaxing the fitting validator.
Use public `ProcessedStore.iter_features`, not private memmap slicing or the
all-population `load_background_features` convenience routine.

Three scopes must be reported separately:

1. **Reconstruction:** prepared, prevalidated PCA FP64 arrays/frozen matrix
   operations, or preloaded AE FP32 CPU tensors and frozen forward under eval/
   inference mode. Include kernel allocations; exclude input loading, FP32→FP64
   preparation, tensor wrapping, scoring, thresholding, logging and guard queries.
2. **Score/decision:** prepared stored FP32 input and the corresponding precomputed
   canonical reconstruction; include required FP64 conversions, subtraction,
   squares/sum, finite validation and all four strict threshold comparisons.
   No forward. Precomputed reconstructions are bounded by the same1024 events.
3. **Canonical adapter+decision:** call each existing public `score` on the
   preloaded FP32 NumPy input, then all four strict comparisons. Include its
   validation/wrapping/conversion/forward/SSE overhead; exclude disk/preprocessing.

Also report actual import/model loading/dev verification/input loading/preparation/
numerical verification/guard/cleanup and whole-worker/campaign wall separately.
Do not sum medians of separate scopes as if they measured combined end-to-end
latency. Raw-source decompression and online feature computation remain unmeasured.

### Numerical verification, guard implementation and acceptance

Before timing, compute canonical references on the1024 rows in one batch (within
the existing4096 batch limit), then verify every grid window, both reconstruction
and each model's canonical scores/decisions. After timing, recheck outputs and
frozen parameter/input/threshold hashes. Same-batch separated SSE vs public
canonical score uses `atol=1e-12,rtol=1e-12`. Across batch shapes, PCA reconstruction
and scores use `atol=1e-12,rtol=1e-12`; AE FP32 reconstruction and its propagated
SSE use `atol=1e-6,rtol=1e-5`. Record max absolute/relative errors and exact byte
equality where obtained. These are preregistered verification tolerances, not
permission to change arithmetic. Require **zero strict-threshold decision
mismatches at every frozen threshold** versus the1024 reference, even if numeric
error is within tolerance. Any mismatch/nonfinite blocks a successful comparison;
retain the failure and do not change sample, threshold or tolerances to pass.

Require a new benchmark-scoped controller/guard, validated **within Task0020**;
do not point particle policy/router at unsupported PCA/AE phases. Low-level
accounting helpers may be reused after scope review without changing their
historical bytes. Proposed limits: each numeric worker lifetimeRSS≤1GiB
(1073741824bytes), whole-native malloc reservation≤512MiB (536870912bytes);
stdlib parentRSS≤128MiB (134217728bytes), one numeric worker at a time. These are
finite engineering ceilings to validate, not measured PCA/AE requirements or a
canonical particle policy. They allow framework/import/dev-custody overhead
around tiny tensors; benchmark-specific synthetic measurements must fit before
real input dispatch. If they do not fit, record blocked/failure, do not enlarge
them during the campaign.

Fresh own-process RSS/native/pressure checks before data, at phases and before/
after each timed invocation; a50ms-intent watchdog during blocked work; accounting
queries outside timed pairs but included in worker/campaign wall. Parent deadlines
cover imports and blocked children, with terminate then bounded kill/reap (2s grace
inside total budget); reserve cleanup slack before another worker. Latch failures;
never let an interrupted timing look completed. Primary unavailable/malformed
accounting fails closed. Global free+inactive is optional bounded context at
worker start/end (≤2s/query), no available-memory floor or stable readiness loop.
For this separate ≤600s benchmark proposal NORMAL permits, WARN is recorded as
advisory, CRITICAL stops/latches, unavailable pressure is explicitly disclosed
under the process/deadline caps. This finite benchmark policy is independent of
particle dev permission and cannot establish multi-hour full-store suitability.
The periodic watchdog and concurrent host work can overlap a timed invocation;
disclose that interference and never subtract overlapping monitor counters or
claim uncontended model cost from this shared-host protocol.

Synthetic acceptance must cover scope/role/truth refusal **before** constructor;
frozen config/model/results/hash mismatch; dev compatibility without weakening
full fitting; exactly1024 input rows/no overread; grid/window schedule and each
timing boundary; score/strict-tie/near-threshold decision mismatch; nonfinite
outputs; explicit effective threads/precision; resource equality/exceedance/
failed-peak capture; unknown/malformed pressure; blocked imports/native work and
parent deadlines; worker crash/interruption/partial evidence; owned cleanup;
exclusive single-campaign reservation/no overwrite/retry and truthful summaries.
Ordinary tests must be self-contained with synthetic stores/models and never
require ignored real receipts or data. Run appropriate tests/lint in Task0020;
this brief does not create execution acceptance.

Implementation targets may be a small `src/latenttrigger/benchmarks/` module,
controller/worker and focused tests. Keep existing fit/evaluation entry points,
frozen loaders/math/configs/artifacts and particle slot unchanged. Bind the exact
new protocol/source acceptance before one explicit campaign; exclusive reservation
before real data. Failure consumes that campaign, retains partial/audit/guard
records, stops dependents and permits no automatic replay. A correction requiring
real replay needs separate authorization. Missing artifacts/runtime/accounting
stop with a factual status; do not refit/download/fallback to complete the table.

Capture actual hardware model/chip/installed RAM/core counts, OS/build/architecture,
Python/PyTorch/NumPy/scikit-learn/BLAS/threadpool versions, effective threads,
precision, code commit/dirty hashes, timer metadata and model/input/calibration
identities. Record normal shared use/apps open, power/thermal/load context where
available without inspecting app content or requiring app management; unavailable
fields stay unknown. Report monitor/timer overhead and ordering limits truthfully.

Proposed raw output: ignored `results/benchmarks/task0020-frozen-cpu/` with one
reservation/protocol, bounded prepared input, numerical checks, raw timings and
audits/resources. Curate only a small
`results/tables/final/task0020-frozen-cpu-benchmark-summary.json` and optional small
CSV, plus report/prompt/handoff/memory/index updates. Acceptance is frozen identity
preservation, guard/synthetic checks and an honest complete or blocked campaign
outcome, not a required speedup. MPS, ONNX/CoreML, reduced precision/quantization,
trigger simulation and final test evaluation remain separate later tasks.

## Task0019 validation and exposure

Arithmetic was recomputed from original small receipts, not copied from a
rounded report. Small JSON syntax/scientific hashes, calibration/model links,
source acceptance and original custody/dev lineage were checked. Final review
checks document/summary agreement, local links, whitespace, exact intended-file
scope, empty index and preservation of tracked frozen inputs plus ignored
engineering record hashes. Temporary metadata validation/snapshots stay ignored
under `data/task0019-*`. No670-test rerun or new source acceptance was needed.
Hosted CI and remote push remain unverified.

```yaml
new_real_population_accesses: 0
new_optimizer_updates: 0
remaining_granted_dev_updates: 0
canonical_training_authorized: false
active_particle_resource_or_time_contract_changed: false
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```
