# LatentTrigger — Task 0020: Frozen PCA/AE CPU Inference Benchmark Foundation

Original user specification received 2026-10-08 (Europe/Rome), preserved verbatim below.

---

# LatentTrigger — Task 0020: Frozen PCA/AE CPU Inference Benchmark Foundation

You are continuing **LatentTrigger**. Perform **Task0020 only**.

Task0019 deferred local canonical particle execution under unchanged contracts and defined the next bounded CPU benchmark. Implement that benchmark, validate it synthetically, then perform **one conditional real campaign** using frozen PCA and compact-autoencoder-v2 on the same1024 existing dev-training aggregate inputs.

This prompt explicitly authorizes that single campaign after successful validation and prerequisite checks. Task0019’s inactive brief alone did not authorize execution.

No fitting, optimizer updates, checkpoint selection, recalibration, particle execution, MPS, export, quantization or test evaluation is authorized. The consumed192/192 particle updates and canonical characterization anchor remain unchanged.

## 1. Inspect actual state and preserve prerequisites

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, and the complete Task0020 brief in:

```text
docs/particle-canonical-feasibility.md
results/tables/final/task0019-particle-canonical-feasibility-summary.json
```

Verify task numbering, Git status/index, branch/upstream, HEAD and relevant artifacts/source.

Planning inspection found `main` tracking `origin/main`, HEAD `5da90944d48dd05fc761d23dad77b85c1fa2da60`, an empty index and seven uncommitted Task0019 files:

```text
README.md
docs/project-memory.md
docs/handoffs/README.md
docs/prompts/0019-particle-canonical-feasibility.md
docs/handoffs/0019-particle-canonical-feasibility.md
docs/particle-canonical-feasibility.md
results/tables/final/task0019-particle-canonical-feasibility-summary.json
```

Verify current state. If those prerequisite changes remain uncommitted, preserve their initial contents in ignored snapshots and record overlapping live-document edits. Do not stop merely because they are uncommitted, rewrite historical Task0019 records or invoke staging helpers.

Preserve unrelated work, historical receipts/acceptances, PCA/AE artifacts and all particle configurations/source/slots. Synced `sources/` remain read-only.

Save the actual prompt and initial handoff before substantive work:

```text
docs/prompts/0020-frozen-cpu-benchmark.md
docs/handoffs/0020-frozen-cpu-benchmark.md
```

## 2. Bind frozen models, inputs and thresholds

Verify the exact small-file and scientific identities recorded by Task0019, distinguishing file-byte hashes from canonical/scientific JSON hashes.

Use:

| Model | Configuration | Frozen artifact | Calibration results |
| --- | --- | --- | --- |
| PCA | `configs/models/pca_baseline.json` | `data/baselines/pca-v1/model.json` | `results/tables/final/task0006-pca-background-results.json` |
| Compact AE v2 | `configs/models/compact_autoencoder_v2.json` | `artifacts/models/compact-autoencoder-v2/model.json` | `results/tables/final/task0008-autoencoder-convergence-summary.json` |

Load through existing canonical artifact loaders. Preserve full-training provenance, frozen scalers, feature order, score definitions and all four calibrated thresholds. Preserve AE v1 as history.

PCA retains six components, centered non-whitened FP64 reconstruction. AE v2 retains its155 FP32 parameters and `8→6→3→6→8` architecture. Both canonical scores are eight-channel SSE with FP64 subtraction, squares and sum; higher means more anomalous. Cast AE input and reconstruction before subtraction.

Read thresholds from the verified frozen results, using strict `score > threshold`. Do not regenerate thresholds or reopen calibration inputs.

Use only the existing dev store:

```text
data/processed/lhco-rd-v1/schema-v1/dev
```

Its inputs are already standardized FP32 `event_features[B,8]`; do not scale twice. They represent aggregates of all physical particles before truncation.

Implement a narrow benchmark dev-inference compatibility validator. Preserve PCA’s existing full-scope fitting validator and all existing model/evaluation entry points.

Reject full-store paths, unsupported populations, labels/truth, test access and altered identities before constructing a store. Missing artifacts or incompatible runtime stop factually; do not refit, download replacements or silently fall back.

## 3. Preregister the exact benchmark protocol

Create a strict versioned benchmark protocol, for example:

```text
configs/benchmarks/frozen_cpu_v1.json
```

Bind this actual prompt, Task0019 brief, frozen input/model/calibration identities, exact timing semantics, source acceptance, limits and single-campaign paths. Reject unknown keys, arbitrary threshold overrides and unsafe selectors.

Use these fixed values:

| Field | Protocol |
| --- | --- |
| Device | CPU only; eager canonical NumPy/PyTorch operations |
| Threads | PyTorch intra-op1/inter-op1; effective BLAS/OpenMP1 |
| Environment before numerical imports | OMP_NUM_THREADS, MKL_NUM_THREADS, OPENBLAS_NUM_THREADS, VECLIB_MAXIMUM_THREADS, NUMEXPR_NUM_THREADS all1 |
| Precision | Stored inputs FP32; PCA computation FP64; AE forward FP32; scores/thresholds FP64 |
| Sample | First1024 source-ordered dev `train_background` IDs; `dev_only=True`, `allow_test=False`, `include_labels=False` |
| Batch grid | `[1,8,32,128,1024]` |
| Worker order | PCA1, AE1, PCA2, AE2, PCA3, AE3 |
| Per-worker order | Ascending batches; reconstruction, score/decision, canonical adapter/decision |
| Per cell | 20 untimed warm-ups, then200 timed invocations |
| Windows | `start=(i mod (1024/B))*B`; reset independently for warm-up and measurement in each cell |
| Timer | `perf_counter_ns`; synchronous CPU completion |
| Timer context | 200 empty timer pairs per worker; report without subtraction |

Inspect effective thread pools, using available `threadpoolctl` where needed. Verify actual enforcement and versions rather than inferring single threading from environment variables. Unsupported enforcement blocks the campaign.

Use deterministic algorithms and AE eval/inference mode. No compilation, AMP, quantization, operator replacement or performance tuning.

Prepare input windows outside timed regions. Retain all scheduled measurements; no favorable-run selection, adaptive repetition, early timing stop or retry.

## 4. One preparation worker and three distinct timing scopes

The preparation worker performs full constructor verification of the **small dev store**, then requests exactly one public `ProcessedStore.iter_features` batch of1024 dev-training rows and stops. Close the iterator/store explicitly.

Do not use private memmap slicing or an all-population convenience loader. Audit dev custody verification separately from the1024-row population request.

Persist only bounded prepared input and ID/provenance hashes in ignored campaign output. The same inputs serve both models and all six workers. IDs never enter model tensors.

Report these scopes separately:

1. **Prepared reconstruction:** PCA FP64 matrix reconstruction or frozen AE forward on preloaded FP32 CPU tensors. Include kernel allocations. Exclude loading, input preparation, scoring, thresholds, logging and guard queries. Preserve canonical arithmetic and disclose validation inherently retained by the invoked code.
2. **Score/decision:** stored FP32 input and a corresponding precomputed reconstruction. Include required FP64 conversions, SSE, finite validation and all four strict threshold comparisons. Exclude forward execution.
3. **Canonical adapter/decision:** call the existing public `score` on preloaded FP32 NumPy inputs, then all four comparisons. Include its validation, wrapping, conversion, forward and SSE overhead.

For scope2, precompute bounded reconstructions using each grid’s actual batch shape. Do not accidentally compare a split full1024 reconstruction against a different-batch forward under the stricter same-batch tolerance.

Keep frozen canonical source unchanged. The prepared PCA kernel must preserve the existing expression and operation order; verify it against canonical reconstruction.

Record actual imports, model loading, dev verification, input loading/preparation, numerical verification, guard work, cleanup and whole-worker/campaign wall separately. Do not sum medians from separate scopes and call that measured end-to-end latency. Raw-source decompression and online feature computation remain unmeasured.

## 5. Numerical and decision verification before interpretation

In each model worker, obtain references from existing canonical implementations on all1024 rows as one batch.

Before timing, verify every grid window:

- Same-batch separated SSE versus public canonical score: `atol=1e-12`, `rtol=1e-12`.
- Across batch shapes, PCA reconstruction and scores: `atol=1e-12`, `rtol=1e-12`.
- Across batch shapes, AE FP32 reconstruction and propagated scores: `atol=1e-6`, `rtol=1e-5`.
- **Zero decision mismatches at every frozen threshold** against the1024 reference.

Record maximum absolute/relative errors, comparison definitions and exact byte equality where obtained. Use an explicit stable relative-error denominator convention.

After timing, recheck numerical outputs and frozen parameter/input/threshold hashes. Preserve actual failed values and partial results.

Any nonfinite, numerical failure, decision mismatch or mutation blocks a successful comparison. Do not change tolerances, thresholds, sample, precision or batch grid to pass. Keep precomputed outputs bounded; real per-event scores need not be persisted.

## 6. Benchmark-specific finite resource protection

Implement a small benchmark-scoped controller/worker/guard. Reuse verified low-level accounting/deadline/cleanup helpers where suitable, preserving their historical bytes. Do not route this campaign through particle execution policies or slots.

Fixed envelopes:

| Scope | Limit |
| --- | --- |
| Each numerical worker, including preparation | LifetimeRSS≤1073741824bytes =1GiB |
| Each numerical worker whole-native reservation | ≤536870912bytes =512MiB |
| Stdlib controller lifetimeRSS | ≤134217728bytes =128MiB |
| Concurrent numerical workers | One |
| Preparation worker | ≤60s |
| Each of six timing workers | ≤60s |
| Aggregation | ≤30s |
| Allocated stages | 450s |
| Whole campaign | ≤600s, including imports/orchestration/verification/gaps/cleanup |
| Periodic process watcher | 50ms scheduling intent |
| Optional context query | ≤2s |
| Terminate/kill/reap grace | Bounded2s, inside campaign budget |

The controller stays free of numerical-framework imports. Validate benchmark-specific synthetic startup/operation footprints before real dispatch. These are chosen engineering caps, not measured requirements; do not enlarge them to complete a failed campaign.

Obtain fresh own-process RSS/native/pressure before data, at phase boundaries and before/after every timed invocation. Queries stay outside timer pairs but inside wall budgets. Preserve failed peaks and latch failures.

NORMAL permits; WARN is disclosed/advisory; CRITICAL vetoes/latches. Unavailable pressure is explicitly unknown and permitted under these finite limits. Malformed pressure/provenance and unavailable/malformed primary process accounting fail closed.

Global available memory is bounded optional context at worker start/end, with no floor, stability wait or readiness loop. Low/unavailable/stale context cannot become a disguised admission veto.

Periodic guards may overlap timed operations. Disclose that interference; never subtract overlapping monitor counters or claim uncontended cost.

Parent deadlines cover blocked imports/native work. Reserve cleanup slack before dispatch. Record interruption/crash/termination honestly, close owned threads/processes and reap children. State scheduling/GIL/OS enforcement limits without claiming hard real-time stopping.

## 7. Validate, freeze, then execute one conditional campaign

Implement a usable CLI with a documented explicit campaign action and concise output. Synthetic tests and validation must not spend the real allowance.

Use one fixed exclusive campaign reservation/output:

```text
results/benchmarks/task0020-frozen-cpu/
```

An existing reserved/partial/foreign/inflight/completed output blocks every real route. No alternative output, reset, overwrite or replay flag creates another allowance. Concurrent launches have at most one winner.

Validate prerequisites before reservation, then atomically reserve before real store construction or numerical input access. Fresh workers independently verify the current protocol/source/artifact bindings.

Add meaningful self-contained synthetic coverage for:

- Scope/population/truth refusal before constructor.
- Frozen identity mismatch and dev compatibility without weakening fitting.
- Exactly1024 rows, deterministic source order and no second batch.
- Window/repetition schedule, three scope boundaries and timer accounting.
- SSE precision, strict ties/near-threshold mismatches and nonfinite outputs.
- Effective thread enforcement and frozen parameter/input preservation.
- Cap equality/exceedance, failed peaks, WARN/unknown disclosure and CRITICAL/malformed vetoes.
- Blocked imports/native work, parent deadlines, crashes/interruption and owned cleanup.
- Exclusive reservation, consumed/partial refusal and truthful incomplete summaries.

Ordinary tests must use synthetic fixtures without operational data, receipts or `.git`. Run the appropriate full synthetic suite, lint/format, dependency/CPU smoke and portability checks. Do not add a speedup acceptance threshold or synthetic optimization matrix.

Freeze all executable helpers and the complete applicable source map in a new benchmark acceptance **before real work**. Preserve old particle acceptance records; do not relabel670 historical tests as current acceptance.

After successful validation and prerequisite checks, perform exactly one campaign: preparation plus the fixed six sequential timing workers and aggregation. Do not pause for another confirmation; this prompt supplies conditional authorization.

A failure after reservation consumes the campaign even with zero inputs/timings. Preserve partial evidence, stop dependent stages and finish without retry. A later replay requires separate authorization. If prerequisites block before reservation, deliver the validated implementation and exact blocker without polling or resource cleanup requests.

No executable repairs followed by real replay inside this allowance.

## 8. Report measured results and practical limits

For every completed model/batch/scope/worker cell, report count/min/max/mean/population std and p50/p95/p99 using linear quantiles. Retain all three worker distributions and median of worker medians.

A complete campaign has90 measured cells and18000 timed invocations, plus1800 warm-ups. Treat empty timer pairs separately. Partial campaigns must disclose actual counts and missing cells.

Define throughput aggregation explicitly, including `B/mean invocation seconds`; distinguish batch latency, amortized time/event and single-event latency. Do not call inverse-tail latency a throughput percentile without defining the transformation.

Capture actual hardware/chip/RAM/core counts, OS/build/architecture, runtime/library/threadpool versions, effective threads, precision, timer metadata, code commit/dirty/source identities and frozen model/input/calibration identities.

Record shared-host use and available power/thermal/load context without inspecting application content or managing apps. Unknown fields remain unknown.

Explain limited p99 resolution, fixed ordering, watchdog interference and host variability. Different residual scales and dev threshold acceptance do not establish model quality, calibrated FPR, AUC/AP or signal discrimination. No physical trigger-rate/deadline claim.

## 9. Deliverables, memory and next step

Create:

```text
docs/frozen-cpu-benchmark.md
results/tables/final/task0020-frozen-cpu-benchmark-summary.json
```

Optionally curate one small CSV for the same measurements. Keep prepared inputs, IDs, numerical/audit/guard records, source acceptance and raw timing receipts ignored under the fixed campaign output. Do not persist new model artifacts.

Update README, `docs/project-memory.md` and the handoff index in place. Distinguish implementation/validation from actual complete, partial or blocked execution. Keep particle canonical deferral and consumed192/192 unchanged.

State actual population/custody access, unique rows, presentations and zero optimizer updates. Report:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Verify report/summary agreement, frozen identities, receipt lineage, links, JSON, whitespace and Git exclusions. Hosted CI stays unverified unless directly established.

Acceptance is numerical/decision correctness, guarded finite execution, identity preservation and honest evidence—not a required speedup. On success, propose one bounded next CPU/MPS comparison task using these reference measurements; availability and scientific parity remain prerequisites. Do not implement that next task here.

## 10. Required final Git section — last section of the response

Do not automatically stage, commit or push.

End with exact status/diff/index review, selective `git add --` of actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push for the verified branch/upstream.

Include this prompt/handoff, protocol, new benchmark implementation/tests, report/curated results and affected README/memory/index files. Exclude raw campaign evidence, inputs, acceptances, snapshots, logs, caches and unrelated changes.

If Task0019 remains uncommitted, identify its prerequisite files explicitly. Provide a reviewable manual Git sequence covering both intended task scopes without resetting files or claiming an isolated Task0020 commit. Preserve both tasks’ prompt/handoff records.

Proceed with **Task0020 only**.
