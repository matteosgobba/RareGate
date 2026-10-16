# Task0025 — Frozen PyTorch/ONNX Runtime paired CPU benchmark

**Software validated; numerical and timing coverage complete; campaign failed and
consumed. No accepted paired performance comparison.** All 90 scheduled cells,
18,000 measurements, 1,800 warm-ups and 1,200 empty pairs exist. Every worker's
pre/post numerical gates pass. ORT3 wrote its completed receipt after
10.072625084 s, but did not exit. The independent parent deadline terminated and
reaped it after 58.030580209 s (SIGTERM, exit −15), inside the 60 s stage limit.
A local completed receipt does not override a failed process lifecycle.

[Actual prompt](prompts/0025-pytorch-onnx-cpu-benchmark.md),
[handoff](handoffs/0025-pytorch-onnx-cpu-benchmark.md),
[strict protocol](../configs/benchmarks/pytorch_onnx_cpu_v1.json),
[curated JSON](../results/tables/final/task0025-pytorch-onnx-cpu-benchmark-summary.json)
and [90-cell CSV](../results/tables/final/task0025-pytorch-onnx-cpu-benchmark-cells.csv).
Raw timings, numerical/guard records, graphs, arrays, grants, acceptance and logs
remain ignored. All pooled/paired ratios below are **descriptive and provisional**;
none is a campaign-accepted speedup. No source/policy repair or retry followed.

## Verified state, history and bindings

Initial main tracked origin/main, clean working tree and index; full HEAD
`cacaefd3ac00a6c657b14109eb19e0119e25ada4` is the actual Task0024 commit.
Task0022/0023 commits are respectively
`61611341a90f2bd2225559b8a3245ec3e6ed08a7` /
`933cba22a2243ecd81d573bef4af8688678b9d33`. Historical reports/handoffs retain their
task-time staged/uncommitted meanings. Initial ignored snapshots bind 1,147 prior
files, including 114 prior source/dependency entries and small operational records.
Only README, living memory and the index receive overlapping current-state edits.
Synced sources stay read-only; no Git staging, commit or push occurred.

Task0020 remains partial/failed/consumed; Task0022 remains the accepted CPU v2
reference, never included in new denominators/repetitions; Task0023 remains blocked
without physical MPS proof or paired data; its device check was not repeated.
Task0024 remains accepted for export/equivalence without historical performance.
Particle 192/192 remains consumed, canonical local execution deferred.

Reuse unchanged canonical loader, compact-autoencoder-v2 architecture
8 → 6 → 3 → 6 → 8, all 155 FP32 parameters, eight feature names/order, full-training
provenance and frozen scalers. AE v1/PCA history is untouched. Scientific AE SHA256:
`6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b`.
Canonical score is CPU FP64 eight-channel SSE, **casting both input and reconstruction
before subtraction**; higher is anomalous. Strict score > threshold preserves
3.478338537407165, 4.681070974717348, 8.324174660133213, 16.642218868621573.
Calibration inputs were not opened or thresholds regenerated.

Primary reconstruction graph is the existing 11,464 B Task0024 artifact, SHA256
`4250b008fb5dfa6f5951e8448a696a1b3a17a9072a8d945ec1fd683204d04793`.
The existing diagnostic graph is also reused: byte SHA256
`ac50d52acf35c92c8ad28e9be54d881fd423e6845272efc4fe5bb9284dda019a`.
Task0024's receipt records its creation and every primary/final equality, but did
not serialize a separate diagnostic-file SHA field. Task0025 newly binds those
existing bytes from the preserved initial snapshot; this is metadata verification,
not a regenerated graph or a claim of a previously recorded literal SHA.
Graph/initializer audit restores the original manifest and exact parameters.

Only original prepared input:
`results/benchmarks/task0020-frozen-cpu/prepare/input.npy`, 32,896 B,
NPY v1 128 B bounded header, C-contiguous little-endian FP32 [1024,8]. File SHA256
`7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`;
payload SHA256 `2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05`.
Original Task0020 prepared/ID/custody lineage remains immutable. These are already
standardized source-ordered dev-training aggregates, no double scaling/reselection.
Header/file hashing is not numerical opening. No raw/processed store, population,
labels, selection/calibration or test arrays were reopened.

## Isolated foundation and fixed protocol

Six new benchmark modules plus self-contained tests retain all old launch routes,
guards, model loaders, arithmetic and timing kernels unchanged. The stdlib-only
controller supports:

```bash
.venv/bin/python -m raregate.benchmarks.pytorch_onnx_cpu --validate-prerequisites
.venv/bin/python -m raregate.benchmarks.pytorch_onnx_cpu --run-campaign
```

The second action is now **consumed and must not be replayed**. Even metadata
validation refuses an existing campaign namespace. No alternate output/reset/
overwrite/retry flag. Atomic mkdir has one winner; reservation precedes the frozen
synthetic study and any numerical input. Parent/token/source/acceptance/predecessor
bindings are independently rechecked in every fresh worker.

Preparation ran four fixed Task0021 families (constants, powers, seed 1729 uniform
and clipped normal) against the frozen AE and both accepted CPU paths. It required
aggregate passed status and every mismatch/violation/coverage count before one
original np.load(allow_pickle=False), then copied byte-identical input. Six fresh
workers each loaded that copy once: PyTorch1, ORT1, PyTorch2, ORT2, PyTorch3, ORT3.
At most one numerical process; no fitting, optimizer, export, graph optimization,
quantization, MPS/CoreML or scientific evaluation.

Runtime unchanged: Python 3.12.12, PyTorch 2.14.1, NumPy 2.5.3, ONNX 1.23.2,
ORT 1.31.0, ONNX Script 0.7.2. All 43 package versions, original core file/build
identities and dependency declaration/record verify; no installation. Typed raw
UTF-8 and canonical JSON-string build hashes are bound separately, including ORT
release 402979a. Effective Torch intra/inter 1, deterministic/inference mode,
OpenMP pools 1 and native Accelerate mode 1 restore before/after. Five CPU thread
environment variables are 1 before imports. ORT CPUExecutionProvider only,
sequential, intra/inter 1, ORT_DISABLE_ALL and fallback disabled are audited via
session options/providers and installed fallback state, for primary and diagnostic.
Installed source and [official ORT API](https://onnxruntime.ai/docs/api/python/api_summary.html)
confirm ordinary session.run/feed/output semantics and explicit fallback control.
No I/O binding, output preallocation, operator replacement, AMP or compilation.

Ascending batches [1,8,32,128,1024], then three scopes; 20 untimed warm-ups and
200 timed calls per cell. Contiguous start=(i mod(1024/B))*B resets independently
for warm-up and measurement. perf_counter_ns is synchronous CPU completion;
clock monotonic/nonadjustable, observed resolution 1 ns. Measured duration ≤0
retains the completed call and invalidates/stops without retry; empty zero pairs
would remain context. Actual measured durations are positive. Timer and watcher
costs are not subtracted. Hooks, preparation, guard queries, diagnostics and disk
IO are outside pairs; all remain inside process/campaign budgets.

1. **Prepared reconstruction:** frozen Torch model(preloaded FP32 tensor), including
   its intrinsic encode validation/allocations; or primary session.run(None,
   prepared feed)[0], including Python API dispatch/output allocations. No disk,
   session setup, FP64 score/thresholds or diagnostics. This is an ordinary invocation,
   not isolated native-kernel timing. Prepared/public/cache same-shape agreement
   is checked outside timing.
2. **CPU score/decision:** corresponding actual-batch cached reconstruction, unchanged
   core.separated FP64 casts/SSE/finite checks/four comparisons. No forward. Shared
   CPU postprocessing, not ONNX graph acceleration.
3. **Public adapter/decision on prepared features:** unchanged model.score or accepted
   RuntimeAdapter.score then same four decisions. Includes path validation/wrapping/
   forward/SSE; excludes reading/loading/session construction. Raw reading,
   all-particle aggregate construction and preprocessing remain unmeasured.

## Descriptive measurements, not accepted speedup

Each cell retains count/min/max/mean/population std/linear p50/p95/p99. Each runtime
pool uses all 600 invocations across three workers. Throughput=B/(mean_ns/1e9);
amortized mean time/event=mean/B, distinct from B1 single-event latency. Median
of worker p50s is separately reported; not pooled p50. Pair i ratio=PyTorch_i
mean/ORT_i mean, above one means lower observed ORT latency. Keep all three ratios,
their geometric mean and separately the ratio of pooled means. No reciprocal
latency averaging or inverse-tail throughput percentile. Matching throughput ratio
ORT/PyTorch equals the ratio of latency means. No historical Task0022 denominator.

| B | Scope | PyTorch mean µs | ORT mean µs | PyTorch throughput M events/s | ORT throughput M events/s | Three pair ratios | Geometric mean | Pooled mean ratio |
| ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 1 | reconstruction | 12.607 | 6.604 | 0.0793 | 0.1514 | 1.775/1.845/2.162 | 1.920 | 1.909 |
| 1 | score_decision | 5.255 | 5.820 | 0.1903 | 0.1718 | 0.715/1.067/1.022 | 0.920 | 0.903 |
| 1 | adapter_decision | 72.184 | 15.594 | 0.0139 | 0.0641 | 9.950/1.673/1.511 | 2.930 | 4.629 |
| 128 | reconstruction | 18.045 | 11.410 | 7.0935 | 11.2187 | 1.540/1.601/1.604 | 1.582 | 1.582 |
| 128 | score_decision | 7.371 | 7.823 | 17.3662 | 16.3628 | 0.894/0.964/0.975 | 0.944 | 0.942 |
| 128 | adapter_decision | 46.756 | 23.691 | 2.7376 | 5.4029 | 3.034/1.430/1.387 | 1.819 | 1.974 |
| 1024 | reconstruction | 53.420 | 38.410 | 19.1689 | 26.6594 | 1.453/1.394/1.327 | 1.390 | 1.391 |
| 1024 | score_decision | 23.733 | 23.085 | 43.1460 | 44.3574 | 1.063/0.904/1.133 | 1.029 | 1.028 |
| 1024 | adapter_decision | 92.033 | 68.366 | 11.1265 | 14.9781 | 1.365/1.263/1.412 | 1.345 | 1.346 |

All forward raw pair ratios exceed one across all batches. That directional
observation is not accepted campaign performance or universal superiority. Public
adapter B1 is especially variable: PyTorch worker means 169.292 / 23.662 / 23.599 µs,
ORT 17.014 / 14.146 / 15.622 µs; PyTorch1 maximum 1.594166 ms and p99 1.171790 ms.
Consequently pooled mean ratio 4.629 differs sharply from pair geometric mean 2.930.
B128 adapter ratios 3.034 / 1.430 / 1.387 also retain the first-worker outliers.
At B1024 the adapter ratios 1.365 / 1.263 / 1.412 are more similar, still provisional.
Score-only ratios near one and varying direction concern the same CPU arithmetic.
No causal claim about scheduler, thermal state, monitor or cache explains outliers.

All five batches and all three worker distributions are in JSON/CSV. Limited
200-call linear p99 samples interpolate near the final observations; 600-call
pools mix process contexts. Three ordered pairs provide limited repetition evidence.
Fixed Torch-first ordering, shared-host activity, warm prepared inputs and periodic
watcher interference limit inference. Do not sum separate-scope medians into
measured end-to-end latency or extrapolate these rates to physical triggers.

## Numerical gates and identities

Reuse unchanged [Task0024 arithmetic derivation](arithmetic-onnx-cpu-v1-policy.md),
normal FP32/FMA bounded-reduction assumptions, FP64 outward propagation/local
actual-input affine/ReLU checks, support band [2^-40,2^40]. FP32 dtype alone does
not prove unknown native kernel internals. The diagnostic is rounded FP64 evidence,
not exact real arithmetic or a new model. No fitted epsilon/domain/seed search.
[PyTorch numerical accuracy](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html)
explains why byte equality across execution implementations cannot be assumed.

Every timing worker's pre/post gates cover 1,193 windows / 5,120 row-window
presentations, all 1,024 rows at each batch, both runtimes. Inspect status and all
failed evidence rather than assume return implies success. Separate prepared/cached/
public gates also check every window and canonical CPU1024 decisions. Full canonical
CPU, own ORT, FP64 diagnostic/envelope references and model/input/threshold hashes
restore; primary and diagnostic bytes, providers/threads/source restore. No hooks
remain during warm-up or timing. Cross-runtime bytes differ; own-repeat,
primary/diagnostic final and same-shape separated/public FP64 SSE are byte exact;
established SSE atol=rtol=1e-12 passes.

All 12 worker gates: 14,316 windows, 3,108,864 local affine scalar checks, zero local
violations. Reconstruction max absolute 3.910064697265625e-5, maximum pointwise
error/bound 0.00787368586649532 (0.787369%); SSE max 4.850380439513913e-5, ratio
0.0016074927437233696 (0.160749%); maximum local ratio 0.27309913548849507.
Relative descriptions divide by max(1,abs(reference)); admission uses independent
pointwise outward bounds. Four threshold mismatches **0/0/0/0**, with 61,440 checks
per threshold in the ORT full-grid gates plus 61,440 in designated prepared-path
gates. Synthetic families independently pass 1,036,288 local scalar checks / zero
decisions before real opening. Minimum CPU1024 margins 0.00933623417,
0.004083978687, 0.1601266843, 3.752131356.

These are scoped numerical observations; they do not establish universal decisions,
held-out FPR, AUC/AP, signal sensitivity or scientific equivalence on unseen rows.

## Resource, lifecycle, access and provenance

| Stage | Worker reported seconds | Parent lifetime seconds / exit | Observed RSS MiB | Whole native MiB |
| --- | ---: | --- | ---: | ---: |
| prepare | 14.967328 | 15.254553 / 0 | 386.687500 | 199.671875 |
| PyTorch1 | 10.709045 | 11.096466 / 0 | 398.140625 | 199.671875 |
| ORT1 | 10.620929 | 10.874653 / 0 | 348.187500 | 199.671875 |
| PyTorch2 | 10.485247 | 10.772335 / 0 | 398.484375 | 195.671875 |
| ORT2 | 10.957767 | 11.291536 / 0 | 397.453125 | 199.671875 |
| PyTorch3 | 10.799836 | 11.067498 / 0 | 379.812500 | 203.671875 |
| ORT3 | 10.072625 | 58.030580 / -15 | 358.843750 | 199.671875 |

Caps: worker RSS 1 GiB / whole native 512 MiB; stdlib parent 128 MiB; preparation
60 s, six timing workers 60 s each, aggregation 30 s; 450 s allocated stages /
600 s whole; 2 s terminate/kill/reap slack inside deadlines. Whole campaign
128.780991583 s; parent peak 38,748,160 B = 36.953125 MiB. Observed numeric-worker
RSS maximum 417,841,152 B = 398.484375 MiB; whole native 213,565,440 B = 203.671875 MiB.
RSS/native overlap, not disjoint allocations or incremental model memory. These
samples include imports/setup/diagnostics through reported guard closure. During
ORT3's subsequent exit wait the worker watcher had already closed; terminal memory
behavior is unknown, so a full-lifetime ORT3 memory envelope is **not certified**.
Independent parent supervision still covered the process and successfully reaped it.

All numerical receipts report closed watchers/no guard latch. All primary pressure
queries returned unknown/errno1, not NORMAL. WARN is advisory, CRITICAL or malformed
primary accounting latches; unknown pressure is explicitly permitted under finite
caps. Optional start/end vm_stat context has no floor/stability/readiness veto.
50 ms watcher scheduling intent can overlap CPU timings; overlapping guard counters
cannot be subtracted. GIL/OS scheduling and termination limits are not hard real time.

The first six stages (preparation plus five workers) exited 0. ORT3 exit −15 / parent
timeout invalidates acceptance despite all measurements/gates/recorded cleanup.
Its ~48 s gap after worker receipt is not an instrumented shutdown component and
has no established cause. No normal aggregation stage was reached; failure-path
aggregation preserved raw distributions/counts, without separately measuring its
exclusive wall. No caps/deadlines/tolerances were enlarged; no repair or replay.

Reads: one original + six local np.load, byte-identical copy; 1,024 unique existing
rows. New population/store-custody requests 0, optimizer updates 0. Scheduled timed
row presentations 4,294,800 (2,863,200 forward; 1,431,600 score-only), warm-up
429,480 (286,320 forward; 143,160 score-only). Verification additionally presents
172,032 Torch and 208,896 ORT forward rows, 61,440 diagnostic-ORT rows; FP64 diagnostic
12,288 full-model rows and 540,672 local affine rows. Window preparation contributes
30,720 forward rows; prepared equality checks 184,320 forward rows and 12,288 CPU
reference rows. Those repeats are not unique rows or new population requests.
Exact synthetic counts remain separate in the summary; no real scores were saved.

Fresh filtered MacBook Pro/Mac17,2, Apple M5, 16 GB, CPU descriptor proc10:4:6:0,
arm64/macOS26.6.2; AC power, battery 100%, load 3.7705/3.5977/3.6636. Native sysctl
fields and thermal warnings remain unknown; no claimed idle host or controlled
thermal/power mode, no application contents inspected or managed.

## Validation and one scientific next step

Before real reservation: 1,179 full and 1,179 portable tests, 68 new tests;
actual optional toy ONNX CPU sessions verify all three scopes and provider drift.
Portable copy has no data/artifacts/receipts/sources/Git; unchanged narrow historical
schema fixture plugin. Test coverage includes strict unknown/unsafe selectors,
atomic competing reservations and consumed/partial refusal, exact schedules/counts,
forward-free postprocessing, FP64 cast/ties/nonfinite, failed aggregate gates,
prevention/invalidation semantics, pooled/geometric ratio distinctions, malformed
pressure/failed caps, blocked native/import parent deadlines and owned cleanup.
Synthetic tests do not prove absence of every runtime teardown failure: ORT3 exposes
that unresolved execution limit. Historical 1,111 is not current acceptance.

Ruff lint/format and dependency consistency pass. Data-free protected smoke runs
30 synthetic cells / 6,000 measurements within 30 s including process supervision:
8.449468625 s worker, 441.093750 MiB RSS / 215.671875 MiB native, guard closed.
121 source/dependency files, protocol/prompt and validation receipts freeze before
reservation. Final checks recompute raw statistics/counters/JSON/CSV agreement,
all prior/source/scientific/graph/receipt byte relationships, links/whitespace and
Git exclusions without reopening numerical arrays. Hosted CI remains **unverified**.

Recommend **Task0026 — Guarded Frozen PCA/AE Final Scientific Comparison**.
The existing [evaluation-v1 contract](evaluation-protocol.md) already specifies
frozen candidates, independent calibration/strict thresholds, ROC-AUC/AP,
calibrated efficiencies, attainable fixed-FPR/TPR points and count/interval limits.
The existing evaluation.run.run_final supports both current canonical model types;
small model/calibration/full-manifest metadata agree. No new scientific metric,
retraining, threshold revision or hardware branch is a prerequisite.

The narrow implementation prerequisite is finite **full-store evaluation**
orchestration: independent parent deadline/process budgets, one sequential worker,
source/identity gates, exclusive output/partial failure handling and pre-read
exposure audit, with self-contained synthetic acceptance. Current run_final lacks
those resource/deadline/campaign protections; dev benchmark caps do not establish
full-store admission. A separately authorized task must preregister limits based
on historical full-custody lineage (custody is not scoring measurement), freeze
exact candidate/config/calibration identities and the existing 4,096-row evaluation
batch/tail semantics, then authorize one audited final evaluation of native PCA-v1
and compact AE v2. Report 150,471 background / 100,000 signal rows, prevalence,
all frozen operating points and uncertainty, preserve interruption as exposure;
do not optimize models after unblinding. This brief is inactive, not implemented
or permission to access tests. ORT shutdown investigation, MPS/CoreML, quantization
and simulation remain optional separate work, not automatic scientific blockers.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```
