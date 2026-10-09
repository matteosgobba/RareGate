# Arithmetic-aware frozen CPU benchmark v2 — Task0022

**The new v2 campaign is complete and accepted:** all six new workers supply
90cells,18000timed invocations,1800warm-ups and1200empty timer pairs. Both models
pass pre/post numerical, frozen-decision and identity checks. This is an explicit
prospective engineering-policy revision authorized by the Task0022 prompt;
Task0020 remains partial/failed/consumed and Task0021 remains a completed consumed
numerical diagnostic. Historical PCA1 is not included in the new repetitions.

[Summary](../results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json),
[90-cell CSV](../results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv),
[strict protocol](../configs/benchmarks/frozen_cpu_v2.json),
[frozen arithmetic derivation](arithmetic-cpu-v2-policy.md),
[actual prompt](prompts/0022-frozen-cpu-benchmark-v2.md) and
[handoff](handoffs/0022-frozen-cpu-benchmark-v2.md) distinguish historical,
newly measured, adopted engineering policy, proposed future work and unknowns.

## Actual state and unchanged science

Initial state: clean `main` tracking `origin/main`, empty index, HEAD
`17a7146f775df47f1b542e18300860275f01c10c`, Task0021 committed. Living memory/index
reconcile that commit; historical handoffs retain their task-time state. Task0019
brief/decision, Task0020 report/handoff/protocol/summary, and the complete Task0021
report/brief/handoff/protocol/summary and original small receipts were inspected.
Task0020/0021 executable/protocol/acceptance/receipt/curated bytes are preserved,
including90previously accepted source entries and40campaign/study files.
Synced sources remain read-only; no unrelated work or staging helper was used.

PCA remains six centered/non-whitened FP64 components, loaded through its existing
canonical loader. AE remains compact-autoencoder-v2,155 exact FP32 parameters,
8→6→3→6→8 with hidden ReLU and linear latent/output, loaded canonically. AE v1 is
history. Full-training provenance, configs/features/scalers/splits and calibration
scientific/file identities are unchanged. Their exact registry is in the protocol;
scientific/canonical JSON hashes are distinct from file-byte hashes.

Only the original prepared input file was numerically opened by preparation:
`results/benchmarks/task0020-frozen-cpu/prepare/input.npy`,32896bytes, C-contiguous
little-endian FP32[1024,8], already standardized. Its bounded NPY1 header is
verified without numerical-framework imports, before array opening. File SHA256:
`7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`;
C-order payload bytes SHA256:
`2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05`.
Preparation reads it once, creates a byte-identical campaign-local copy, and each
of six fresh workers reads that copy once. No raw/processed store is constructed,
no custody replay/population request/row reselection or double scaling occurs.
These are the original first1024 source-ordered dev-training aggregates of all
physical particles before truncation; IDs/labels/truth never enter model tensors.

Both canonical scores remain eight-channel SSE: FP64 cast **before** subtraction,
then squares and sum, higher anomalous. No public score/model arithmetic changed.
Frozen thresholds retain strict `score > threshold`, including rejected ties:

| Historical target FPR | PCA threshold | AE v2 threshold |
| ---: | ---: | ---: |
| 0.1 | 0.3496768162794852 | 3.478338537407165 |
| 0.05 | 0.5642097175249418 | 4.681070974717348 |
| 0.01 | 1.4232146905138892 | 8.324174660133213 |
| 0.001 | 4.1356483360291865 | 16.642218868621573 |

No fitting, optimizer, checkpoint selection, recalibration, particle, MPS, export,
quantization or test evaluation occurred. Particle192/192/remaining0 and canonical
local deferral under unchanged resource/time/science contracts remain intact.

## Active v2 numerical engineering contract

The separately frozen [derivation](arithmetic-cpu-v2-policy.md) gives assumptions,
operation counts, recurrence and outward implementation in full. It uses the
standard rounding/summation model from
[Higham1993, sections1–3](https://nhigham.com/wp-content/uploads/2023/10/high93s.pdf)
and the shape-dependent arithmetic distinction in
[PyTorch numerical accuracy](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html).
The project recurrence and implementation are independently derived/tested;
a citation is not treated as validation.

For n=8,6,3,6, set m=2n+2, u32=2^-24, u64=2^-53 and gamma_m=m*u/(1-m*u).
With fixed rounded FP64 diagnostic activations using exact promoted FP32 weights,
`M=|W|*|h64|+|b|` and
`E_next=(1+gamma32)*|W|*E_previous+(gamma32+gamma64)*M`, startingE0=0.
The terms cover incoming perturbation and rounding of **both** execution paths.
ReLU is1-Lipschitz. Each FP32 shape must lie within E against that diagnostic;
across-shape reconstruction must lie within D=2E. The FP64 copy is neither a new
canonical artifact nor exact real-arithmetic truth. Local affine checks use the
actual stored FP32 inputs of every layer, compare with rounded FP64 evaluation,
and veto on failure; no bound is expanded to pass.

Every nonzero input/parameter/affine input/output/reference activation must lie
within the preregistered `[2^-40,2^40]` band. That band gives a normal FP32 product/
partial-sum lattice down to2^-126 and bounds magnitudes below overflow; it also
leaves ample FP64 exponent room. Unsupported/nonfinite/subnormal bound operations
fail closed. Values are never clipped. Current FE_TONEAREST(0) is checked, build
pinned and single threading verified; no precision/backend/flush setting changes.
This is an engineering bound under ordinary bounded IEEE operation assumptions,
not a universal certificate of a named native GEMV/GEMM implementation.

Bounds use an outward step **after every** FP64 elementwise product/add/division,
a downward positive denominator, exact magnitudes, and per-term outward dot/sum
accumulation. A BLAS dot followed by one nextafter is not used. Gamma, M, recurrence,
pair factor, observed absolute differences and score allowances all receive
operation-level accounting. Exact zeros remain zero; infinity is never permission.

For exact reference residual r and reconstruction bound D,
`Q=2*sum(|r|*D)+sum(D²)` bounds the exact SSE change. Computed residualrho is
not assumed exact: use outward `|r|<=|rho|/(1-u64)`. Eight subtractions, eight
squares and at most eight reduction additions give24operations; squared residual
rounding-factor paths are also below32. The fixed gamma32(u64) ceiling yields
`|Scomputed−Texact|<=g*Texact<=g/(1−g)*Scomputed`. Add the allowances of **both**
computed scores to outward Q. No fitted epsilon or observed-error multiplier.
The public canonical score itself stays unchanged.

Independent gates preserve same-shape separated/public SSE1e-12/1e-12,
byte-exact reconstruction/score repeats and full-reference pre/post hashes,
finite/band/local assumptions, and zero strict decision mismatches on every1024row
and grid before/after timing. PCA retains its original1e-12/1e-12 reconstruction/
score checks and never receives the AE envelope. Input/parameter/threshold or
reference mutation vetoes completion. Old v1 failures are not relabeled passes.

## Implementation, validation and freeze

Only isolated new policy/protocol/numerics/controller/worker modules and115focused
self-contained tests were added. Existing loaders, model arithmetic, old
comparators, timing kernels, guards, thread enforcement and consumed routes retain
historical bytes. The new controller remains stdlib-only; fresh workers verify
prompt/protocol/source/artifacts/parent/phase/predecessor receipts independently.
The CLI is `python -m latenttrigger.benchmarks.frozen_cpu_v2 --run-campaign`.
`--validate-prerequisites` verifies metadata/header/source without reservation or
numerical opening; `--synthetic-validation` is a separate fixed synthetic route.
Both execution routes are now consumed; do not replay/reset/choose another output.

942full tests and942portable tests pass, with no operational data/receipts or
`.git` in the portable copy. New tests check outward primitives/gamma/complete
recurrence/SSE against exact rational fixtures, cancellation/bias/FP64 rounding,
ReLU sign changes, zero bounds/scores, threshold ties and adjacent representable
values, unsupported bands/nonfinite/overflow/underflow, mutation/repeatability,
header/identity/scope refusal before NumPy opening, strict policy overrides,
timer schedule/boundaries, exclusive competing reservations, truthful incomplete
receipts and failure/no-retry behavior. Reused full-suite tests cover blocked
imports/native work, deadlines/crashes/interruption/cleanup and effective threads.
Lint/format/dependency consistency/CPU smoke pass; hosted CI remains unverified.

Before freeze, one fixed fresh worker evaluated the four Task0021 recipes for
both frozen models: constants0/+1/−1/+8, signed powers2^-3…2^3, independent seed1729
uniform[-8,8] and clipped standard normal. No seed/domain/constant search.
All8family/model cases and five batches complete with zero v2 violations/frozen
mismatches. AE local checks cover565248scalar comparisons across the four families;
all repeat checks pass. Synthetic worker6.168936834s/whole6.536453083s,
RSS352124928bytes=335.8125MiB/native188399616bytes=179.671875MiB, inside fixed caps.
It performs180224canonical forward row presentations (90112PCA FP64/90112AE FP32),
4096diagnostic FP64 full forwards and98304local-affine row presentations;
these latter rows are layer operations, not full-model forward counts.
No numerical real prepared input was opened during synthetic validation.

All96applicable source/test/script hashes, policy derivation, protocol, runtime,
validation and successful synthetic footprint were frozen before reservation.
Acceptance file SHA256:
`042e00394e593c9f214fdf66e79effb63f62466a9ab0e648b84afb9735517510`;
protocol canonical SHA256:
`3727d8d81e8f62db920c4d418713117acd02466da31f71e55c7a8ba3424f98fa`.
No executable/policy repair, real diagnostic trial or replay occurred afterwards.
The new16MiB raw guard-journal ceiling was preregistered for additional local
verification checks; it does not enlarge RSS/native/time caps or any old policy.

## Exact timing protocol and new measurements

CPU eager NumPy/PyTorch, intra/inter-op1, effective BLAS/OpenMP1 and deterministic
algorithms. The five thread variables are set before imports and actual pools/
public Accelerate thread-local mode queried; environment variables alone are not
proof. Stored inputs FP32, PCA FP64, AE forward FP32, scores/thresholds FP64.
No AMP, compilation, quantization, operator replacement or performance tuning.

Worker orderPCA1,AE1,PCA2,AE2,PCA3,AE3; ascending batches1/8/32/128/1024 and
reconstruction→score/decision→adapter/decision. Each cell20warm-ups then200timed
invocations. Reset `start=(i mod(1024/B))*B` independently for each phase.
`perf_counter_ns`, synchronous CPU,200empty pairs per worker, never subtracted.
All scheduled measurements remain, including slow outliers.

1. Prepared reconstruction includes kernel allocation, excludes loading/window
   preparation/SSE/threshold/log/guard queries; original PCA operation order and
   frozen AE forward remain unchanged.
2. Score/decision uses that actual batch's precomputed reconstruction, casts to
   FP64 before subtraction, computes canonical SSE/finite checks/four strict
   comparisons; excludes forward.
3. Public adapter/decision invokes existing public score on FP32 NumPy inputs,
   including validation/wrapping/conversion/forward/SSE and four comparisons.

Policy/tracing/local FP64 diagnostics are outside timer pairs. All hooks are
removed before warm-ups. Raw decompression/online features are unmeasured.
A sum of separate scope medians is not an end-to-end latency measurement.

The table uses **median of the three worker p50s**, in microseconds. Adapter
throughput is B divided by the pooled mean invocation seconds: equal-weight mean
of three200-call worker means. It is distinct from inverse p50/tail latency.
The CSV retains every worker's count/min/max/mean/population std/p50/p95/p99
(linear quantiles), throughputB/mean and amortized mean time/event.

| Model | B | Reconstruction p50 µs | Score/decision p50 µs | Adapter/decision p50 µs | Adapter throughput events/s from pooled mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| PCA | 1 | 2.417 | 4.708 | 8.125 | 118734 |
| AE v2 | 1 | 12.3955 | 5.125 | 24.708 | 28395 |
| PCA | 128 | 5.625 | 7.1665 | 15.5205 | 8009318 |
| AE v2 | 128 | 17.792 | 7.2085 | 31.792 | 1153938 |
| PCA | 1024 | 18.000 | 21.8335 | 44.4585 | 22324739 |
| AE v2 | 1024 | 52.083 | 21.542 | 85.500 | 11871389 |

All5batches/3scopes/3workers per model are in the summary/CSV. B1 represents
single-event latency; large-B latency is for the entire batch, and time/B is an
amortized quantity. PCA's canonical adapter is faster in this campaign; this
compares fixed pipelines, not discrimination/quality or equivalent compression.

AE2 B128 adapter retains max26.2485ms, mean267.5986µs andp50=54.875µs, versus
AE1/AE3 means31.706725/33.46831µs. That shared-host tail lowers pooled throughput;
it is not discarded or attributed to a specific monitor/app/kernel without proof.
200samplep99 has limited tail resolution; fixed order, warm cache, host variability,
OS scheduling and periodic watchdog overlap limit generalization. No uncontended
cost, physical trigger rate/deadline or model-quality speedup claim.

## Measured numerical acceptance

All three AE workers pre/post reproduce the following values; errors and
**envelope maxima** are different quantities. Ratios are maximum pointwise
observed-error/its-envelope, not a ratio of independent maxima.

| AE batch | Reconstruction max error | Pair envelope max | Max reconstruction ratio | Canonical SSE max error | SSE envelope max | Max SSE ratio |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5.4359436035e-5 | 0.01475455108148 | 0.0102172935183 | 2.0492837961e-4 | 0.09171214094300 | 0.00401697313793 |
| 8 | 1.3351440430e-5 | 0.01475455108148 | 0.00766465862452 | 1.1829054195e-4 | 0.09171214094300 | 0.00206137025853 |
| 32 | 1.3351440430e-5 | 0.01475455108148 | 0.00766465862452 | 1.1829054195e-4 | 0.09171214094300 | 0.00206137025853 |
| 128 | 1.3351440430e-5 | 0.01475455108148 | 0.00766465862452 | 1.1829054195e-4 | 0.09171214094300 | 0.00206137025853 |
| 1024 | 0 | 0.01475455108148 | 0 | 0 | 0.09171214094300 | 0 |

The bounds are deliberately conservative; their sizes are not measured drift.
Every FP32 shape also passes its single envelope against rounded FP64 diagnostic
activations. Each AE pre/post gate checks141312local-affine scalar outputs;
847872total across three workers/two gates. Maximum local-affine error/bound
ratio0.27309913548849507; violations0. Same-shape reconstruction/public-separated
SSE is byte-exact, full-reference/diagnostic/envelope hashes restore exactly,
parameter/input/threshold hashes remain unchanged. No diagnostic artifact is saved.
PCA keeps its original1e-12/1e-12 criteria and passes every grid pre/post with
byte-exact same-shape comparisons and zero frozen decision mismatches.

All AE strict threshold mismatches are0/0/0/0 on every1024row/grid pre/post.
Computed full-reference sample minimum margins to its four thresholds are
0.009336234173192182/0.004083978687090983/0.16012668428443355/3.752131356020776.
Those are newly computed reference-sample margins; per-grid actual margins were
not separately retained in v2. Agreement on these rows does not certify universal
decisions, calibration FPR, test acceptance or signal discrimination. The active
v2 contract validates this controlled CPU scope; the same numerical differences
still fail historical v1, which remains preserved as failed.

## Resource, wall, access and provenance

Complete wall25.661480791997747s includes imports, metadata/orchestration,
preparation, all six numerical/timing workers, gaps, aggregation and cleanup.
Controller peak28344320bytes=27.03125MiB; aggregation0.00007658299s.
Workers finish2.2396–4.6297s, each≤60s; one numerical worker at a time.
450sallocated stages fit inside the600swhole budget;2scleanup/reaping slack
is reserved inside it. Guards make fresh own-process checks before data and at
phases/before-after invocations, plus50mswatcher intent. Parent deadlines cover
blocked imports/native work; all children reaped and owned watchers closed.

| Stage | Worker wall seconds | Peak RSS bytes | Whole-native reserved bytes |
| --- | ---: | ---: | ---: |
| Prepare | 2.239602083 | 343916544 | 180011008 |
| PCA1 | 2.745669584 | 360726528 | 180011008 |
| AE1 | 3.511928750 | 365543424 | 192593920 |
| PCA2 | 2.861215459 | 361021440 | 184205312 |
| AE2 | 4.629725791 | 331120640 | 184205312 |
| PCA3 | 3.198735334 | 360726528 | 184205312 |
| AE3 | 4.265463083 | 360218624 | 184205312 |

Maximum RSS348.609375MiB and native183.671875MiB stay below1GiB/512MiB;
parent stays below128MiB. RSS/native can overlap and are not added as disjoint
allocations. Process caps do not guarantee machine-wide headroom or hard real-time
stopping. All live pressure samples are unknown/errno1, not NORMAL/WARN; WARN
would be advisory, CRITICAL/malformed primary accounting latched. Optional global
available context has no floor/stability wait/readiness veto. No app contents,
closure/reboot/cache/swap/privilege workaround or idle window was requested.

AE numerical verification including traces/local FP64/policy costs is separately
accounted outside timers: before0.6479/0.7948/1.0323s; after0.6434/0.6475/0.6875s.
PCA verification before/after0.3109–0.3539s. Imports/thread/window/cleanup and whole
worker costs are recorded. Timing-worker model/input loading is included in wall
but not individually instrumented; no claim that its cost was measured separately.
Monitoring overlaps can affect kernel samples; guard counters are not subtracted.

Fresh filtered hardware metadata inside the campaign reports MacBook Pro/Mac17,2,
Apple M5,16GB and processor descriptor`proc 10:4:6:0`. arm64/macOS26.6.2,
AC power/battery80%, load averages2.79785/2.95166/2.66797 recorded. Hardware native
sysctl fields are unavailable; thermal queries report errors despite exit0 and
remain unknown. No serial/UUID or app contents are retained. This fresh filtered
hardware capture is distinct from the historical Task0020 M5 observations.
Versions: Python3.12.12, NumPy2.5.3, PyTorch2.14.1, sklearn1.9.1, SciPy1.18.1,
threadpoolctl3.7.0. Actual pools/Accelerate mode/build/precision/source/commit/dirty
identities are recorded. Timer metadata queried afterwards in the same bound
runtime reports monotonic perf_counter; it is labeled post-campaign metadata.

Original numerical array reads1, campaign-local reads6, unique reused rows1024;
new population/store-custody/optimizer requests0. Canonical numerical forward
presentations239616; timed input presentations4294800; warm-up429480. Additional
FP64 diagnostic full-forward presentations6144 and local-affine row operations
147456 are reported separately; local rows are not whole-model forward counts.
Preparation/byte hashes/header verification are distinct from numerical reads.
No test inputs, new population arrays or model artifacts are persisted. Raw inputs,
traces/aggregates/timings/guards/access/acceptance/source snapshots/logs stay ignored.

## Recommended bounded Task0023 brief

**Task0023 — Frozen CPU/MPS Parity and Inference Comparison Foundation** is the
next bounded route, subject to live numbering and separate explicit finite
conditional authorization. This document implements/executes none of it.
CPU v2 supplies a complete accepted reference and unchanged scientific identities.
Current CPU smoke reports `MPS available:False`; the physical M5/build flag alone
is not usable MPS availability, and the cause of this runtime result is unverified.

1. Verify current artifacts/input/threshold/source identities and preserve v1/v2/
   Task0021 history and particle deferral. Implement isolated device support,
   numerical policy, protocol/controller/worker/tests. Do not edit old routes.
   No fitting/calibration/export/quantization/test work.
2. After synthetic validation/source freeze, make one bounded fresh MPS availability
   check before any real numerical input or campaign reservation. If unavailable,
   deliver the validated foundation with that exact blocker, zero real rows/slot;
   no CPU fallback disguised as MPS, polling, app closure or privilege request.
3. If actually supported, first validate device-specific arithmetic and frozen
   decisions on the four fixed synthetic families in one guarded≤60sdata-free
   worker. The CPU gamma contract is **not** an automatic MPS certificate.
   Pin actual Metal/PyTorch build/operators/precision and derive a defensible
   supported device rule; if not established, stop before the real campaign.
4. Keep AE FP32 parameters/input/forward, canonical FP64 SSE on CPU after obtaining
   reconstruction, strict frozen thresholds/features/scalers. Use current PCA/AE
   CPU reference scientifically, and compare frozen AE CPU versus MPS; do not
   invent an MPS PCA FP64 implementation or permit CPU operator fallback silently.
   Verify parameter/input round trips, same-shape repeats, finite/local supported
   arithmetic, every1024row/grid and zero threshold mismatches pre/post.
5. New real path `results/benchmarks/task0023-cpu-mps/`, one exclusive finite
   separately authorized campaign, source/parent/predecessor bindings and no retry.
   Reuse exact prepared1024rows, not stores/populations. Use paired independent
   AE workersCPU1,MPS1,CPU2,MPS2,CPU3,MPS3 for contemporaneous shared-host context;
   do not claim a causal speedup from a favorable comparison to historical times.
6. Preserve batches1/8/32/128/1024,20warm-ups/200invocations, fixed windows and
   three scopes. Prepared MPS reconstruction uses preloaded device tensors,
   explicit pre-timer synchronization and completion synchronization inside the
   pair. Scope2uses corresponding precomputed CPU reconstruction and canonical
   FP64 SSE/decisions, no forward/transfer. Public adapter includes CPU→MPS input,
   forward, output→CPU/synchronization, FP64 SSE and decisions. Report transfer/
   synchronization placement; never compare asynchronous dispatch time to CPU
   completion or assume MPS supports canonical FP64 arithmetic.
7. Engineering caps to preregister/test: host worker1GiB RSS/512MiB whole native,
   parent128MiB, device current allocations≤256MiB/driver allocations≤512MiB;
   primary device queries must be available/valid. Device and host budgets may
   overlap on unified memory; do not sum them as disjoint usage. One numerical
   worker, preparation≤60s,six workers≤60s,aggregation≤30s,450sallocated/600swhole,
   bounded2scleanup, fresh primary guards/50msintent/contextual pressure asCPUv2.
   Validate blocked GPU sync/import/driver queries and cleanup; no cap extension.
8. Preserve all three distributions/tails, pooled means and median worker medians,
   numerical/resource/provenance/availability/transfer context, truthful partial
   failures and raw exclusions. If any requirement fails after reservation,
   consume/stop with evidence, no repair/continuation/replay. Acceptance requires
   correctness and finite execution, not a required speedup. The outcome can be
   a supported comparison or an unavailable/unsupported device foundation.

MPS, exports, quantization, simulation and final unblinding remain future work.
The CPU measurements establish inference costs on this frozen sample/runtime,
not scientific superiority or physical trigger performance.

## Final validation and delivery

Final metadata-only checks recompute current/old source/config/model/result/receipt
relationships, raw timing counts/statistics and JSON/CSV/report agreement, byte
identical prepared copy, local links/whitespace/exclusions and actual Git scope.
No numerical population/input replay is part of that validation. Memory revision
1.15 records active prospective v2 and complete CPU results; historical handoffs
remain unchanged. Final response follows the informative planning-handoff preference.
Hosted CI remains unverified, and no resulting Task0022commit/push is claimed.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```
