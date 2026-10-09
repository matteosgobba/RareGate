# LatentTrigger — Task 0025: Frozen PyTorch/ONNX Runtime Paired CPU Inference Benchmark

You are continuing **LatentTrigger**. Perform **Task0025 only**.

Task0022 supplies the accepted arithmetic-aware CPU benchmark. Task0024 supplies the structurally and numerically accepted ONNX CPU reconstruction artifact derived from the frozen compact-autoencoder-v2.

Implement and execute **one independent, bounded, contemporaneous paired CPU benchmark** comparing canonical PyTorch inference with ONNX Runtime inference for that same frozen AE.

The question is whether the accepted ONNX representation changes measured inference cost under matched conditions. **No speedup is required for acceptance.**

This prompt explicitly authorizes:

1. Implementation and self-contained synthetic software validation.
2. Preregistration and current-source acceptance.
3. One conditional, bounded paired campaign after those prerequisites pass.
4. Reuse of the existing 1024 prepared background-training rows within that campaign.

No additional confirmation is required for these authorized steps.

No fitting, optimizer updates, recalibration, new export, graph optimization experiment, quantization, MPS/device check, CoreML, particle execution or held-out test evaluation is authorized.

## 1. Inspect the repository and preserve prior evidence

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, and the relevant Task0022–0024 prompts, reports, policies, protocols, summaries and handoffs.

Planning inspection found:

```text
branch: main
upstream: origin/main
working tree and index: clean
Task0024 HEAD: cacaefd3ac00a6c657b14109eb19e0119e25ada4
```

Verify live state, full commit identity, upstream and task numbering before work. Preserve unrelated changes.

Save the actual prompt and initial handoff:

```text
docs/prompts/0025-pytorch-onnx-cpu-benchmark.md
docs/handoffs/0025-pytorch-onnx-cpu-benchmark.md
```

Preserve frozen scientific artifacts and all prior executable, protocol, acceptance, receipt and raw-result bytes. Historical reports and handoffs retain their original task-time meaning.

In particular:

- Task0020 remains partial, failed and consumed.
- Task0022 remains the complete historical CPU reference.
- Task0023 remains blocked, without physical MPS equivalence or paired timings. Do not repeat its device check.
- Task0024 remains accepted for ONNX structure and numerical equivalence, with no historical performance measurements.
- Particle updates remain **192/192 consumed**, with canonical local execution deferred.

Implement isolated new benchmark modules. Reuse existing validated loaders, runtime adapters, arithmetic helpers and resource primitives without changing their scientific behavior or reopening old execution routes.

Synced `sources/` remain read-only.

## 2. Bind the accepted artifacts and unchanged environment

Use the accepted primary graph:

```text
results/benchmarks/task0024-ae-onnx-cpu/reconstruction.onnx

size: 11464 bytes
file-byte SHA256:
4250b008fb5dfa6f5951e8448a696a1b3a17a9072a8d945ec1fd683204d04793
```

Reuse the accepted diagnostic graph and its recorded identity for untimed numerical checks. Do not regenerate either graph.

The canonical scientific model remains:

```text
configs/models/compact_autoencoder_v2.json
artifacts/models/compact-autoencoder-v2/model.json
results/tables/final/task0008-autoencoder-convergence-summary.json

model scientific SHA256:
6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b
```

Preserve architecture `8 → 6 → 3 → 6 → 8`, all 155 FP32 parameters, feature names/order, preprocessing/scalers and calibration provenance.

The sole permitted real input source is:

```text
results/benchmarks/task0020-frozen-cpu/prepare/input.npy

shape: [1024, 8]
dtype/layout: contiguous little-endian FP32
file size: 32896 bytes

file-byte SHA256:
7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e

payload-byte SHA256:
2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05
```

These are already-standardized, source-ordered dev-training aggregates. Do not reopen raw data, processed stores, split arrays, selection/calibration populations or test populations.

Verify the Task0024 dependency record and accepted package/build identities. The planning environment includes:

```text
Python 3.12.12
PyTorch 2.14.1
NumPy 2.5.3
ONNX 1.23.2
ONNX Runtime 1.31.0
ONNX Script 0.7.2
```

No dependency installation, upgrade, downgrade or replacement is authorized. Missing or changed prerequisites must produce a concrete blocker rather than a replacement environment or regenerated export.

Keep file-byte hashes, canonical scientific JSON hashes, parameter-payload hashes and build-text hashes explicitly typed. Preserve the distinction between raw UTF-8 build text and its canonical JSON-string representation.

## 3. Preregister a fixed, independent campaign

Create a strict protocol, for example:

```text
configs/benchmarks/pytorch_onnx_cpu_v1.json
```

Bind:

- Actual prompt and new executable source identities.
- Accepted scientific model, graph, diagnostic graph, input and calibration identities.
- Dependency/build identities and effective thread/provider settings.
- Exact timing boundaries, window schedule and statistics.
- Numerical admission gates.
- Resource limits, deadlines, accounting and failure behavior.
- One fixed exclusive output namespace.

Use:

```text
results/benchmarks/task0025-pytorch-onnx-cpu/
```

Complete self-contained validation and freeze current-source acceptance before reserving the campaign. Atomically reserve the namespace before executing the frozen-model synthetic study or opening real numerical inputs.

Existing, foreign, partial or consumed campaign state must block a new attempt. Do not overwrite, reset, rename away evidence, choose an alternate namespace or retry a failed reserved attempt.

Metadata/header/hash inspection is distinct from numerical input loading. Record that distinction.

If the campaign fails, preserve its partial evidence and actual counters. Finish unaffected documentation and validation without replaying real work or modifying tolerances.

## 4. Use bounded preparation and fresh sequential workers

Keep the controller stdlib-only. Run at most one numerical worker at a time.

Preparation must:

1. Verify accepted artifacts and runtime settings.
2. Run the four fixed Task0021 synthetic families against the frozen AE and both CPU runtimes under the accepted ONNX arithmetic policy.
3. Require complete numerical acceptance before real input access.
4. Perform exactly one `np.load(..., allow_pickle=False)` of the original prepared input.
5. Validate its header, shape, dtype, layout, finiteness and hashes.
6. Create a byte-identical campaign-local input copy.

The frozen-model synthetic study belongs to this new reserved campaign. It is not an unrecorded preliminary performance experiment.

Execute six fresh timing workers in this exact order:

```text
PyTorch1
ORT1
PyTorch2
ORT2
PyTorch3
ORT3
```

Each worker loads the campaign-local input once. Verification may instantiate the reference runtimes it needs, but only the designated runtime supplies that worker’s timed reconstruction and adapter calls.

Limits:

```text
numerical worker RSS: ≤ 1 GiB
numerical worker native footprint: ≤ 512 MiB
controller RSS: ≤ 128 MiB

preparation: ≤ 60 s
each of six timing workers: ≤ 60 s
aggregation: ≤ 30 s
whole campaign: ≤ 600 s
cleanup grace: ≤ 2 s
```

Parent-enforced deadlines must cover imports, session creation, blocked runtime calls and numerical verification.

Reuse validated fresh boundary checks and the existing 50 ms watcher intent. Place explicit guard queries outside latency timing intervals while including their cost in campaign wall time.

Global available RAM is optional context, without a floor or readiness loop. WARN remains advisory; CRITICAL blocks execution; unavailable pressure information is disclosed.

Record resource sampling methods and actual peaks. Worker lifetime RSS includes setup and diagnostics and must not be presented as incremental model memory.

## 5. Match runtime configuration

Both runtimes use CPU FP32 reconstruction and canonical CPU FP64 scoring.

Preserve the accepted CPU thread environment, effective native thread settings and PyTorch deterministic/inference configuration. Verify effective settings before and after measurements.

ONNX Runtime must retain:

```text
providers: ["CPUExecutionProvider"]
execution mode: sequential
intra-op threads: 1
inter-op threads: 1
graph optimization: ORT_DISABLE_ALL
provider fallback: disabled
```

Audit effective session options and actual providers.

No provider sweep, graph optimization, I/O binding experiment, preallocated-output optimization or changed scoring implementation is permitted.

Do not claim a controlled idle machine, thermal state or power mode unless actually observed. Record observable shared-host context without attributing differences to unmeasured causes.

## 6. Define three explicit timing scopes

Use batches:

```text
[1, 8, 32, 128, 1024]
```

For each batch, measure these scopes in fixed order.

### A. Prepared reconstruction invocation

PyTorch uses the unchanged model on preloaded CPU FP32 tensors under inference mode.

ORT uses the accepted primary session on preloaded FP32 arrays, with prepared feed dictionaries where appropriate.

Exclude disk reads, model/session construction, input preparation and numerical diagnostics.

Document the exact callable boundary. ORT’s Python API dispatch and output creation remain part of an ordinary `session.run` invocation; this is not a claim of pure native-kernel timing.

Verify the prepared callable agrees with its canonical public path outside timing intervals.

### B. CPU score and decision

Use each runtime’s corresponding precomputed, same-shape reconstruction.

Time the unchanged canonical calculation:

1. Cast input and reconstruction to FP64 before subtraction.
2. Square and sum eight residual channels.
3. Apply all four frozen strict `score > threshold` decisions.

Include the casts and arithmetic. Exclude reconstruction inference.

Use the same postprocessing implementation for both runtimes. Explain that this scope measures shared CPU postprocessing rather than ONNX graph execution.

### C. Public adapter score and decision

PyTorch uses the canonical public `model.score` path followed by four strict decisions.

ORT uses the accepted public runtime adapter’s `score` path followed by the same decisions.

Include the validation, wrapping, reconstruction and score work that the respective public paths perform. Exclude disk access, model loading and session construction.

Label this as the public adapter operating on prepared features. Raw event reading, aggregate construction and preprocessing remain outside its boundary.

## 7. Fix invocation scheduling and retain all observations

Within every cell:

```text
warm-up invocations: 20
timed invocations: 200
```

Use contiguous windows from the same 1024 rows:

```text
start = (invocation_index % (1024 / batch_size)) * batch_size
```

Reset invocation indexing separately for warm-up and measurement. Use the same schedule for both runtimes.

Use `perf_counter_ns` around synchronous CPU calls. Numerical diagnostics, instrumentation hooks and explicit guard queries remain outside the timed region; intrinsic public-adapter validation stays inside its declared boundary.

Record 200 empty timer pairs per timing worker. Retain their distribution as context; do not subtract it from measured durations.

A complete campaign contains:

```text
6 workers × 5 batches × 3 scopes = 90 cells
90 × 200 = 18000 timed invocations
90 × 20 = 1800 warm-up invocations
6 × 200 = 1200 empty timer pairs
```

Keep every timing, including outliers. No adaptive repetitions, fastest-run selection, trimming, workload changes or additional campaign.

Account separately for:

- Source and campaign-local numerical loads.
- Unique real rows reused: 1024.
- Numerical verification presentations.
- Warm-up and timed presentations.
- Forward calls versus score-only work.
- New population requests and optimizer updates: zero.

Declare timer-resolution and nonpositive-duration handling before execution. Never fabricate finite throughput from an invalid denominator.

## 8. Require numerical gates before and after timing

Reuse the accepted Task0024 ONNX arithmetic derivation and independent local evidence.

Do not tune epsilon, tolerances, supported value bands or thresholds using this campaign’s results.

Every timing worker must pass pre- and post-measurement verification over all five batch sizes and all 1193 windows covering the 1024 rows per batch.

Require:

- Finite supported inputs, outputs, intermediate values and bounds.
- Graph/initializer/parameter identities and effective runtime settings.
- Same-runtime same-shape repeat equality.
- Diagnostic final-output equality with the primary ONNX graph.
- Independent local affine/ReLU checks.
- Accepted outward reconstruction and SSE bounds.
- Separated versus public same-shape score agreement under the established gate.
- Zero mismatches at each of the four frozen strict thresholds.
- Restored reference, parameter, input, threshold and graph identities.
- No diagnostic hooks left attached during timing.

Cross-runtime outputs need not be byte identical. Acceptance uses the existing justified bounds plus independent decision checks.

Inspect the verifier’s aggregate status and all violation/mismatch counts. Some helpers preserve failed evidence instead of raising immediately: **returning from a helper does not imply acceptance**.

A failed pre-gate forbids timing. A failed post-gate invalidates that worker’s performance acceptance, while preserving its raw observations.

Agreement on these background-training samples is not a universal numerical certificate, a measured test FPR or evidence of signal discrimination.

## 9. Report distributions and paired comparisons correctly

For every runtime, repetition, batch and scope, report:

- Invocation count.
- Mean, standard deviation, minimum and maximum.
- p50, p95 and p99, with the quantile method specified.
- Batch latency and explicitly normalized time per event.
- Throughput computed as `batch_size / mean_batch_seconds`.

Report all three worker distributions per runtime. Distinguish pooled statistics from summaries of worker statistics.

For contemporaneous pair `i`, preregister:

```text
paired speed ratio_i =
PyTorch_i mean batch latency / ORT_i mean batch latency
```

A ratio above one means ORT was faster for that matched cell.

Report all three ratios and their geometric mean. Separately report the ratio of pooled means; do not conflate these summaries.

Pooled throughput must use all 600 timings per runtime/cell. It is not an average of reciprocal invocation latencies.

Historical Task0022 timings provide context only. They are not denominators or extra contemporaneous repetitions.

Interpret reconstruction, postprocessing and adapter results separately. Do not infer scientific quality, hardware-trigger readiness or universal runtime superiority from this benchmark.

Three process pairs and 200 observations per cell provide limited repeat and tail evidence. Explain the observed variability without overstating confidence.

## 10. Validate software and campaign accounting

Add meaningful self-contained tests for:

- Strict protocol validation, exclusive reservation and consumed-state handling.
- Correct worker order, batch/window scheduling and complete counts.
- Timing boundaries and forward-free score-only cells.
- FP64-before-subtraction scoring and strict threshold ties.
- Numerical failures stopping or invalidating timing.
- Aggregation, normalization, paired ratios and partial/missing workers.
- Effective provider/thread checks.
- Correctly typed build and artifact hashes.
- Resource/deadline failure propagation and cleanup.
- Source/input accounting and preservation of prior evidence.

Use toy fixtures and temporary synthetic artifacts for tests. Do not load operational data or frozen-model numerical inputs through the test suite.

Run actual optional CPU runtime integration tests when the installed dependencies permit them. Do not silently replace them with mocks while claiming runtime integration passed.

Run the appropriate full suite, Ruff, dependency consistency, synthetic CPU smoke, link/JSON/CSV checks and whitespace checks. Verify portability without operational data or `.git`.

The historical 1111-test result belongs to Task0024. Report the actual new counts and checks. Hosted CI remains unverified unless a real run is inspected.

Complete relevant validation before source acceptance and campaign execution. Do not alter the accepted executable or policy after reservation and then reuse the consumed campaign as evidence for the altered version.

## 11. Produce curated results and reconcile living documentation

Create:

```text
docs/pytorch-onnx-cpu-benchmark.md
results/tables/final/task0025-pytorch-onnx-cpu-benchmark-summary.json
results/tables/final/task0025-pytorch-onnx-cpu-benchmark-cells.csv
```

Keep raw timings, logs, receipts, source acceptance, numerical arrays and graph copies ignored under the campaign namespace. Do not add ONNX binaries or raw evidence to Git.

Curated results must distinguish:

- Implemented software.
- Attempted and completed execution.
- Numerical acceptance.
- Performance acceptance.
- Partial results and consumed-state consequences.
- Measured findings, interpretation and remaining uncertainty.

Update README, living memory and the handoff index consistently.

Reconcile stale current objective/milestone rows: CPU v2 is complete; ONNX export/equivalence is accepted; MPS remains blocked; CoreML remains planned. Add Task0025 performance status according to its actual outcome.

Preserve historical failures and task-time records. Increment the living-memory revision from the verified current revision, without inventing results or commit identities.

Identify the shortest justified next step toward the central frozen PCA/AE scientific comparison. Check whether the existing final-evaluation contract is sufficient or whether a narrowly defined prerequisite remains. Avoid making additional hardware branches automatic prerequisites for scientific closure.

No held-out evaluation is authorized by this task.

## 12. Deliver an informative Italian final response

Write a self-contained final response in **Italian**, approximately **600–1000 words excluding Git commands**, with normal spacing around numbers and units.

Explain:

1. Actual completion/acceptance status.
2. What was implemented and which artifacts were reused.
3. What the three scopes include and exclude.
4. Main PyTorch/ORT results, especially batches 1, 128 and 1024, with latency, throughput and paired ratios.
5. Whether any advantage is consistent across repetitions and where variability matters.
6. Numerical errors, pointwise bound utilization and four-threshold mismatch counts.
7. Input access, invocation counts, resource peaks and wall times versus limits.
8. Validation and unverified checks.
9. Scientific interpretation, limitations and one concrete next step.

Link the report, curated JSON/CSV and handoff. Avoid a bare success statement or unexplained test count.

Include:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Report optimizer updates zero and particle 192/192 unchanged.

Finish with manual Git commands for the actual branch/upstream:

- Status and tracked/untracked review.
- Unstaged and staged diff review.
- Explicit selective `git add --` listing only intentional files.
- Staged diff and whitespace checks.
- An outcome-appropriate Conventional Commit.
- Push to the verified upstream.

Do not stage, commit or push automatically. Exclude raw receipts, timings, acceptance snapshots, logs, numerical arrays and ONNX binaries.
