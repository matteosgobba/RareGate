# Frozen PCA/AE CPU inference benchmark — Task0020

**Foundation implemented and validated; the single real campaign is partial and
failed its AE numerical gate.** Preparation and PCA1 completed. AE1 stopped before
timing; PCA2/AE2/PCA3/AE3 were not dispatched. The campaign is consumed, with no
retry. This is not a complete two-model or three-repetition hardware comparison.

[Curated summary](../results/tables/final/task0020-frozen-cpu-benchmark-summary.json),
[90-row cell table](../results/tables/final/task0020-frozen-cpu-benchmark-cells.csv),
[protocol](../configs/benchmarks/frozen_cpu_v1.json),
[actual prompt](prompts/0020-frozen-cpu-benchmark.md) and
[handoff](handoffs/0020-frozen-cpu-benchmark.md) preserve both the implemented
contract and the actual partial outcome. Missing timing cells are explicit,
not zero-valued measurements.

## Verified prerequisites and frozen contracts

Task0019 was committed after planning inspection, at
`c3008d43ddd6ec8aed5999056dc140faba33d84a`, the actual clean Task0020 base on
`main` tracking `origin/main`. Its original prompt/handoff/report/summary remain
unchanged. Current README/memory/index reconcile that commit through Task0020.
No prerequisite staging helper, commit, push or unrelated-file edit occurred.

The [complete Task0019 brief](particle-canonical-feasibility.md#task0020-implementation-brief)
is the design basis. This task's prompt separately authorized one conditional
campaign after current validation. Small-file and scientific hashes were checked
before reservation and independently by each fresh worker. The frozen registry:

| Model | Configuration | Artifact | Calibration evidence |
| --- | --- | --- | --- |
| PCA v1 | `configs/models/pca_baseline.json` | `data/baselines/pca-v1/model.json` | `results/tables/final/task0006-pca-background-results.json` |
| Compact AE v2 | `configs/models/compact_autoencoder_v2.json` | `artifacts/models/compact-autoencoder-v2/model.json` | `results/tables/final/task0008-autoencoder-convergence-summary.json` |

PCA scientific SHA256 is
`d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f`;
AE v2 is `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b`.
Their result scientific hashes remain
`285a254847424870b5bee08e5a218733dcbe553ff7a4d00ec5c9493288600ccb` and
`324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33`.
Complete file-byte hashes and config canonical hashes are in the protocol/summary;
these are distinct identity definitions. Existing canonical artifact loaders are
used, with six centered/non-whitened FP64 PCA components and the unchanged155
FP32 AE parameters/8→6→3→6→8 architecture (best381, stop396). Preserve AE v1.

Both models retain full-training provenance, full processed scientific identity
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`, preprocessing
file SHA256 `2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`
and split scientific identity
`74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea`.
The input is existing dev `event_features` FP32 `[1024,8]`, already standardized
from all physical particles before truncation. Dev manifest scientific identity
is `2eb34e5b811c12ae5c47afba1ecdb6322feb7c7774b6c9ec5331abe78b3c9a2a`.
No scaler is applied again. Frozen feature order, scalers and scientific source
are preserved. The benchmark's dev-inference validator does not weaken PCA's
full-scope fitting validator. No full-store constructor or raw source hash replay.

Canonical scores are eight-channel SSE, higher anomalous, with FP64 subtraction,
squares and sum. AE casts both input and reconstruction before subtraction.
Thresholds are read from verified frozen results (74823 calibration events,
`higher` quantile historically), with strict `score > threshold`; no calibration
population was reopened:

| Target FPR | PCA | AE v2 |
| ---: | ---: | ---: |
| 0.1 | 0.3496768162794852 | 3.478338537407165 |
| 0.05 | 0.5642097175249418 | 4.681070974717348 |
| 0.01 | 1.4232146905138892 | 8.324174660133213 |
| 0.001 | 4.1356483360291865 | 16.642218868621573 |

## Implemented fixed protocol and timing boundaries

Protocol canonical SHA256:
`f1f94ead0232fc5fa0d5bd069dc1c13e8b0828e3dcb4b34436787d098b14e777`.
Exact canonical validation rejects unknown keys, altered values/precision,
arbitrary thresholds and unsafe selectors. Duplicate/nonfinite JSON is rejected.
The stdlib controller and guarded numeric workers are separate from particle
execution policies, permissions and slots. All old source/config/acceptance bytes
are preserved.

- CPU eager NumPy/PyTorch, deterministic algorithms, PyTorch intra-op1/inter-op1
  and verified effective BLAS/OpenMP1. Five prescribed thread variables are set
  before imports. PCA computes FP64; AE forward FP32; both scores/thresholds FP64.
- One preparation worker: full small-dev constructor verification, then exactly
  one public `ProcessedStore.iter_features` batch1024 from source-ordered dev
  `train_background`, no labels/test; iterator/store explicitly closed. Persist
  only bounded prepared inputs and ID/provenance hashes, no ID/score arrays.
- Batches1/8/32/128/1024; planned workers PCA1,AE1,PCA2,AE2,PCA3,AE3. Per worker,
  ascending batches and reconstruction→score/decision→adapter/decision.
- Each cell20 untimed warm-ups then200 timed invocations. Reset the window index
  independently for warm-up and measurement: `start=(i mod (1024/B))*B`.
  Windows are prepared outside timed regions; no adaptive repeats/best selection.
- `perf_counter_ns`, synchronous CPU completion.200 empty timer pairs per worker
  are separate context and never subtracted.

The three scopes:

1. **Prepared reconstruction:** prevalidated PCA FP64 input and the exact existing
   left-to-right `(x-mean) @ basis.T @ basis + mean` expression, or frozen AE
   forward on preloaded FP32 CPU tensors in eval/inference mode. Include kernel
   allocations. AE's existing encode shape/dtype validation remains inherent.
   Exclude input preparation/loading, SSE, decisions, logging and guard queries.
2. **Score/decision:** FP32 input and reconstruction precomputed at that grid's
   actual batch shape; FP64 casts/subtraction/SSE, finite checks and all four
   strict comparisons. No forward. The full1024 reconstruction is not substituted
   for a different-batch reconstruction in the same-shape comparison.
3. **Canonical adapter/decision:** existing public `score` on preloaded FP32 NumPy
   input, then all four decisions. Include validation, wrapping/conversion,
   forward, SSE and finite checks; exclude disk/input preparation.

Imports/model loading/dev verification/input preparation/numerical verification/
guard work/cleanup/whole-worker and campaign walls are separate receipts. Timings
overlap where marked and are not summed or subtracted as exclusive costs. Raw
source decompression and online feature construction remain unmeasured.

### Actual thread enforcement

NumPy2.5.3 uses Apple Accelerate. `threadpoolctl` reports the Torch/sklearn OpenMP
pools but does not report Accelerate as a BLAS pool. The initial synthetic startup
check correctly blocked that incomplete proof before any real slot/data.

The new benchmark helper uses the public Accelerate `BLASSetThreading`/query API,
with unsigned32-bit enum1 for single-thread mode, setter success0 and a subsequent
getter result1 on the computation's owning Python thread. It checks ownership/
mode again after successful timing and restores the previous mode on cleanup.
All benchmark BLAS calls occur on that thread; the watchdog does no numeric work.
This enforces the requested thread setting without replacing BLAS/operators or
changing model arithmetic. Unsupported/missing/inconsistent APIs block admission.
Apple documents the setting as thread-local and defines the single-thread mode.
[Apple setter documentation](https://developer.apple.com/documentation/accelerate/blassetthreading%28_%3A%29),
[threading constants](https://developer.apple.com/documentation/accelerate/blas_threading).
Installed SDK `vecLib/thread_api.h` independently supplies the ABI/enum; its hash
and actual runtime setter/query receipts are retained as ignored evidence.
Observed framework bundle version is `Accelerate 1.11`. Effective OpenMP pools
each report1; unavailable library version fields remain null.

## Finite guards and one consumed campaign

Each numerical worker (including preparation) is capped at1GiB lifetimeRSS and
512MiB whole-native reservation; stdlib controller128MiB RSS. One numeric worker
at a time. Preparation60s, each timing worker60s, aggregation30s:450s allocated
stages inside600s total including imports/gaps/orchestration/verification/cleanup.
Workers/parent reserve2s cleanup/terminate-kill-reap slack; parent deadlines cover
blocked imports/native work. Guards enforce fresh own-process/native/pressure at
startup/phases and before/after timed invocations, plus a50ms-intent watchdog.
Actual failed peaks latch; primary/provenance failures fail closed. WARN advisory,
unknown disclosed/permitted under these finite caps, CRITICAL veto/latch. No
global available-memory floor or stability/readiness polling. Optional context
is bounded2s at worker start/end; failure/staleness/low values do not decide admission.
Failed AE1 stopped before its end context; its startup context remains recorded.

Periodic watchdog/GIL/OS scheduling can overlap timed operations and limit
termination responsiveness. These are guarded shared-host observations, with no
hard-real-time or uncontended-cost guarantee. RSS/native overlap and are not added
as disjoint allocations; process caps are not machine-wide headroom promises.

Validated metadata/current source acceptance precede an atomic fixed-directory
reservation at `results/benchmarks/task0020-frozen-cpu/`. Any existing partial/
foreign/inflight/completed directory blocks all real routes. A concurrent loser
cannot overwrite the winner's workflow. Fresh workers verify parent/token/phase,
prior receipt hashes, protocol, current source and frozen artifacts before data.
Failure after reservation consumes the campaign and stops all dependents.

The CLI action actually used once is shown for interface/history review.
**The fixed slot is consumed; do not repeat this command.**

```bash
.venv/bin/python -m latenttrigger.benchmarks.frozen_cpu --run-campaign
```

Metadata-only prerequisite checking does not reserve or read numerical inputs;
a pass is not new campaign permission:

```bash
.venv/bin/python -m latenttrigger.benchmarks.frozen_cpu --validate-prerequisites
```

## Validation, source freeze and actual execution

**763 synthetic tests pass in8.14s (93 new)**;763 also pass in8.05s in an isolated
checkout without operational data or `.git`. Ruff lint/format152 files, dependency
consistency and forced CPU smoke16/PyTorch2.14.1 pass. No dependency/CI change or
hosted CI claim. New coverage includes fixed scope/dev compatibility, single
public batch/closure, source/identity/precision/thread enforcement, timer/window
boundaries, SSE/strict ties/near-threshold failures, failed values/peaks, caps/
pressure/latched vetoes, watcher/blocked-child deadlines, cleanup, partial/crash
counts and atomic reservation/no-retry behavior. Fixtures are self-contained.

Final benchmark-specific synthetic startup/operation footprint:336101376bytes
RSS and184205312bytes whole native, below the prescribed caps; no real population
or optimizer work. Public Accelerate mode was verified. Initial unsupported
threadpool-only proof and corrected fixture assertions remain separate from the
final source-bound evidence; no real allowance was spent during those changes.

New acceptance file SHA256:
`cc61e7c1f42777ca5ea40f5192fe8d39be57041d67f1218d5a332e578549297e`.
It freezes86 applicable source/test/script entries, protocol, full/portable logs/
XML, dependency/smoke/lint evidence, runtime and synthetic footprint. The ignored
precondition under `data/` is copied byte-for-byte into the exclusive campaign
directory before data. Historical particle acceptances stay unchanged. All86
executable entries stayed identical through the actual campaign and curation.

One conditional campaign ran for **7.989795207999123s**. Controller peakRSS is
28049408bytes=26.75MiB. Every reached process/deadline guard passed, every child
was reaped and final owned watchers closed. The outcome is
`failed_consumed_no_retry`; no executable repair or real replay followed it.

| Reached stage | Outcome | Worker wall incl imports/cleanup | Parent dispatch wall | PeakRSS bytes | Whole-native peak bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| Preparation | Completed1024 rows | 2.143532958s | 2.428334958s | 363200512 | 188399616 |
| PCA1 | Completed15 cells | 3.458894000s | 3.756146458s | 306675712 | 180011008 |
| AE1 | Numerical gate failed before timing | 1.385260292s | 1.705775458s | 362086400 | 180011008 |

Preparation constructor verification0.049506000s, public input load0.000072417s,
input preparation/persistence0.000714583s and iterator/store closure0.000034917s.
Audited custody1 is distinct from the one1024-row population request. Same
prepared byte hashes serve all model workers; source IDs are provenance hashes
and never model features. No full processed store or raw source was reopened.

Actual versus planned: **15/90 cells,3000/18000 timed invocations,300/1800
warm-ups,200/1200 empty timer pairs**.75 cells are missing. PCA has one successful
worker, not three; AE has zero timing workers. In-memory timing presentations are
715800 measured+71580 warm-up=787380, reusing the same1024 rows. Numerical/model
preparation/reference checks account for47128 forward-input presentations.
These are distinct from1024 population rows loaded; unique real rows remain1024.
Optimizer updates0. No score arrays or new model artifacts persisted.

### AE1 numerical failure

Preregistered tolerances are unchanged: same-shape separated SSE vs public score
`atol=rtol=1e-12`; across-shape PCA reconstruction/score `1e-12/1e-12`; AE
reconstruction/propagated score `atol=1e-6,rtol=1e-5`. Relative diagnostic errors
use `max(abs(reference),comparison_atol)`; acceptance is elementwise
`abs(error)<=atol+rtol*abs(reference)`. Strict-threshold decisions require zero
mismatches against the canonical full1024 reference regardless of numeric tolerance.

AE1 fails **reconstruction across batch shapes**:

| Original failed value | Receipt value |
| --- | ---: |
| Within-window index | `[0,5]` |
| Batch1 reconstruction | -0.09302544593811035 |
| Full1024 reference reconstruction | -0.09302345663309097 |
| Maximum absolute error in this comparison | 1.989305019378662e-6 |
| Maximum relative diagnostic error | 2.1384982792297272e-5 |
| Analytic tolerance at this reference value | approximately1.9302345663309095e-6 |

Receipt prefix counts and the frozen ascending B1 window loop locate this at
sample-relative row7, channel5 (`weighted_eta_std`): eight same-shape reconstruction/
SSE windows verified, seven across-shape/decision windows verified before the
failure. The original failure records `[0,5]`; row7 is a documented inference
from those counts, not a freshly reopened ID/input. Larger absolute errors in
earlier windows can pass because the relative term depends on each reference
value. No tolerance/threshold/sample/grid/precision was changed.

This is an observed FP32 batch-shape parity failure; its mechanism has not been
isolated by new measurements. It is not a convergence/scientific-quality result,
and does not invalidate the preserved canonical AE artifact/calibration. AE's
whole1024 reference was computed, but all-grid score/decision parity and post-timing
checks were not reached. No successful AE equivalence, threshold stability or AE
timing comparison is claimed. Sparse actual failed values remain in its receipt.

PCA verifies every grid window on all1024 rows before and after timing, with zero
decision mismatches, max absolute numeric error3.552713678800501e-15 and identical
pre/post full-reference score/reconstruction hashes. Its parameter/input/threshold
hashes match before/after. AE's frozen file identities are preserved, but its
aborted in-memory post-timing checks are not claimed completed.

## Retained single-worker PCA timing observations

These are **PCA1 p50 batch-invocation microseconds**, each based on200 retained
timings. They are not three-worker median estimates or a PCA/AE ranking:

| Batch | Reconstruction | Score/decision | Public adapter/decision |
| ---: | ---: | ---: | ---: |
| 1 | 2.542 | 5.125 | 8.916 |
| 8 | 2.833 | 5.292 | 8.834 |
| 32 | 3.334 | 5.542 | 9.8335 |
| 128 | 6.291 | 8.250 | 15.833 |
| 1024 | 18.084 | 22.6455 | 50.396 |

Every completed cell's count/min/max/mean/population std/p50/p95/p99 (linear
quantiles), `B/(mean_ns/1e9)` throughput and `mean_ns/B` amortized time/event are in
the curated JSON/CSV. Batch>1 amortized time is not single-event latency. Inverse
tail latency is not presented as a throughput percentile. The JSON's observed
worker-median groups contain only one worker and are explicitly incomplete; no
three-worker summary is manufactured.200 samples give limited p99 tail support.
Fixed ascending order, normal shared-host load and watchdog interference limit
generalization. Separate-scope medians cannot be added as measured end-to-end cost.

## Hardware, software and practical limits

Observed environment: macOS26.6.2/arm64, Python3.12.12, PyTorch2.14.1, NumPy2.5.3,
scikit-learn1.9.1, SciPy1.18.1; all runtime/threadpool versions are in receipts.
Native `sysctl` hardware/build queries were restricted. A separate bounded,
filtered `system_profiler SPHardwareDataType` metadata capture after the campaign
reports **MacBook Pro/Mac17,2, Apple M5,16 GB**, processor descriptor
`proc 10:4:6:0` (ten total indicated; the exact raw descriptor is retained).
Fresh exact RAM bytes/sysctl core details remain unavailable. That0.122624s
metadata capture is separate from the7.989795s campaign wall and does no numeric work.
Device serial/UUID were excluded.

Shared-host start load averages3.9106445/2.7758789/2.4570313, AC power/battery80%,
apps open/no content inspection or app management. `pmset -g therm` returned
error text0xe00002bc despite command success: thermal/performance values are
**unavailable**, not NORMAL. Recorded pressure is unknown/errno1 at every reached
guard, not live NORMAL or WARN. Optional available-memory context spans
2.415328979–2.570404053GiB and does not decide admission. No idle window, reboot,
cache/swap manipulation, privileged workaround or repeated readiness polling.

Different compression capacities and FP64/FP32 reconstruction kernels require
reporting each model's own score semantics. Dev threshold counts are not newly
calibrated FPR, model quality, AUC/AP or signal discrimination. No physical
trigger throughput/deadline, MPS/export/quantization or final-test result follows.

## Operational decision and next bounded task

Retain the implemented foundation, passed synthetic acceptance,15 PCA1 cells and
unchanged AE failure as **partial v1 evidence**. The campaign is consumed. Do not
reset/delete/change outputs, rerun, relax tolerances, omit B1 or continue remaining
workers to complete a comparison. Frozen PCA/AE v1/v2 and all particle artifacts/
source/contracts/receipts remain unchanged; particle192/192 still consumed and
canonical execution deferred under [Task0019](particle-canonical-feasibility.md).

The condition for a CPU/MPS comparison is not met. Proposed next **Task0021 —
Frozen AE Batch-Shape Numerical Parity Review**, subject to the live index: use
existing failed receipts, frozen source/small model metadata and bounded
self-contained synthetic analysis to assess this numerical contract and scientific/
artifact compatibility. Preserve failed v1 and strict frozen thresholds; any new
real verification/replay or versioned numerical-policy change requires explicit
finite authorization and its own guarded identity/slot. None is granted here.
Establish a complete CPU reference before CPU/MPS comparison; do not implement
that follow-up, refit or recalibrate in Task0020.

```yaml
new_real_population_accesses: 1
new_dev_custody_operations: 1
unique_real_rows: 1024
population_presentations: 1024
new_optimizer_updates: 0
particle_remaining_granted_dev_updates: 0
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```
