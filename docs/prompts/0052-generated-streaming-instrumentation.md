# LatentTrigger — Task0052: Generated Streaming Instrumentation Repair and Native Characterization

You are continuing **LatentTrigger**. Perform **Task0052 only**.

## Objective and authorized boundary

Make a bounded engineering decision about the streaming foundation's instrumentation before operational integration. Task0051 implements the generated-input core, but event-record appends reached **714 μs**, exceeding the proposed **50 μs** ceiling, synchronization uses **21 SemLocks** with unproved backing size, and its last cleanup/overflow guards have deterministic coverage only.

Inspect and improve the recording path where justified; preserve its accounting and crash observability; characterize the revised implementation against the pinned Task0051 baseline; and exercise the final code through bounded native generated fixtures. A negative result is valid. Do not keep changing measurement boundaries or running experiments until a favorable maximum appears.

This prompt authorizes changes confined to the streaming foundation and focused fixtures; generated memory/records and arithmetic stubs; bounded same-host process/clock/synchronization/logging observations; own-resource checks; curated documentation and results. This is a **new Task0052 generated-only scope**, not renewal of Task0051's exhausted fixture envelope or acceptance of the physical study.

**P4 remains ungranted.** No production raw/HDF access or raw-file hashes; no real membership/golden/features/scores/fingerprints or model artifacts; no frozen/public-model inference, reconstruction, training, optimization, calibration, science metrics, acquisition, old timing-vector loading, trigger replay, old operational controllers, device survey, dependency installation or reservation. No HDF files, real or generated. Do not implement or execute the 24-case physical campaign, change scientific gates, or launch Task0053.

## 1. Verify the baseline and preserve evidence

Read applicable instructions, `docs/development.md`, README, memory and handoff index; inspect Git, branch/upstream, index and unrelated changes. Planning inspection on **2026-10-15 Europe/Rome** found clean `main` tracking `origin/main`, empty index, HEAD **`2f59ae1fafd77455b001393482a5bea84ddb1fc8`**, Task0051 committed and memory **1.46**. Task0050 commit `3521c8f6…` and Task0049 `42ab4458…` remain historical. Recheck; local tracking refs do not prove a fresh remote, push or CI result.

Save this actual prompt at `docs/prompts/0052-generated-streaming-instrumentation.md` and an initial handoff at `docs/handoffs/0052-generated-streaming-instrumentation.md` before substantive work.

Read Task0050's protocol/spec and Task0051's report/config/summary/handoff. Verify these Task0051 anchors:

| Input | Bytes | SHA256 |
| --- | ---: | --- |
| `docs/development-streaming-software-foundation.md` | 15687 | `44901d0f5b1c83e62c2ddb2ec66313877d56bfd2887de4310604ae3a9bd34e96` |
| `configs/streaming/development_streaming_foundation_v1.json` | 8211 | `a275966652d9d0c0fe97262213dfb4ee85edbfc54c3e9c0eb9983ed4f086c0b4` |
| `results/tables/final/task0051-development-streaming-foundation-summary.json` | 80200 | `7313a54eb1ef3881ab05cfa0165a8eb16ef46182f892cee3e12b05fcfbb56ef0` |

Inspect the current streaming modules and focused tests as code. Do not reopen ignored Task0051 operational/fixture evidence; its curated aggregate results suffice. The pinned Git source is available for a narrow generated baseline adapter. No full repository copy, worktree, legacy suite or 57-source reconciliation is needed.

Preserve historical reports, configs, summaries, prompts and handoffs byte-for-byte. Task0052 may version and change the **live streaming implementation**; bind its new source hashes and preserve Task0051's source identity through the committed base or small ignored text snapshots. Do not describe historical native checks as tests of modified code.

## 2. Define the recording boundary before measuring

Task0051's producer wrapper times `Store.write`, including encode/CRC and `pwrite`; accepted offers normally write an intent and a resolved record. Consumer batches write multiple stage updates. A maximum append time alone does not describe total instrumentation per offer or batch. The observation does not identify filesystem writes, encoding, contention or host scheduling as its cause.

Before native execution, specify:

- The baseline and candidate recording operations and exactly which validation, encoding, allocation, CRC, copy/publication, write and statistics updates each timing includes.
- Complete producer instrumentation per offered presentation, including both intent and resolution when applicable; complete consumer instrumentation per realized batch, with actual m and stage-update count.
- Initialization/preallocation/page-touch history, phase journaling, output retention, finalization/flush and cleanup costs. Count moved/deferred work rather than making it disappear.
- Which observations test the proposed **50,000 ns/event-append** and **200,000 ns/batch-append** ceilings, and which are additional whole-path diagnostics. Preserve Task0050's existing meanings; if ambiguous, document that limitation instead of silently choosing an easier boundary.

Retain all attempts, slow calls and exceedances. Record count, sum/mean, median, p95, p99, maximum and threshold-exceedance count by homogeneous operation/case/repetition, separately for baseline and candidate. Define criterion eligibility prospectively; report fault-injected/incomplete observations separately without deleting them. Quantiles use actual samples and stated convention; do not average quantiles, pool heterogeneous stages, subtract clock overhead or infer a universal bound from finite calls. Abnormal children with missing summaries have unknown samples, not zero cost.

## 3. Implement a small, accounting-preserving improvement

Inspect the actual call path first. Prefer a focused change such as bounded preallocated encoding/storage over a new logging framework. A file-backed shared mapping may be suitable, but do not presume it is faster or required. Keep the **64B descriptor, 12,288B ring, 64 inclusive credits, FIFO/B8/1ms timeout, open-loop rules, 512B record semantics, strict-four decisions and actual-shape generated backend** intact.

Preserve explicit intent/return/output transitions, valid-zero versus null timestamps, CRC/noncanonical-byte detection, ownership and bounded cutoff reconstruction. Faster logging must not lose evidence of a process dying before return, after return, after output or during record publication. If a record tears, retain invalid/uncertain state; do not invent the previous or completed operation. No credit is released merely to make diagnostics easier.

No private-heap-only buffering that vanishes with the writer, dropping intermediate records to pass a timing criterion, or timing only a small copy while moving encoding outside the reported boundary. If work is deferred, measure and bound it separately and include it in the full instrumentation result. Finalizer/diagnostic failure must never prevent child/resource cleanup. Do not call an unflushed `pwrite` or mapping power-loss durable: distinguish process-crash observability from persistence across host/power failure.

Update exact buffer/copy/file/mapping inventories, including baseline comparison storage, timestamp samples, retained outputs and reconciliation. Keep the existing design's resource ceilings; do not hide additional mappings or flush buffers outside ownership/storage accounting. Import/help/error paths remain side-effect-free; production paths/models remain unsupported.

## 4. Resolve what can be known about synchronization and clocks

Audit the current one mutex/four Events and their **21 SemLocks**. Record purpose, owner, lifetime and actual created-object count. Remove redundant primitives only if this yields a simpler correct implementation without weakening startup, publication, stop or dead-owner cleanup. Do not replace locks with unverified shared-byte atomicity, uncontrolled busy spinning or a hidden message queue.

Document visible allocations/handles and runtime tracking/cleanup; measure only quantities supported by the host. `sizeof` a wrapper, RSS deltas and a primitive count do not prove kernel/native backing bytes. If the **65,536B** synchronization allowance cannot be established, leave that specific P2 item unresolved and state the minimum future evidence or explicit budget-definition decision needed. Do not fabricate an exact size or silently reinterpret the allowance.

Record service/continuous clock implementations and resolution, limited same-host cross-process comparability observations with explicit brackets/uncertainty, monitor gaps and cleanup duration. Avoid claiming exact clock equality or operational scheduling validity from a few samples. Supervisor cleanup must still work when a child dies holding the ring mutex and when journal, snapshot, close or counter checks fail. Own-process observations are allowed; unrelated application/process/device surveys are not.

## 5. Use a prospectively bounded characterization

Complete deterministic correctness/compatibility tests before native work. Save the exact planned generated cases, record sequences, orders, repetitions, thresholds, budgets and source/config hashes prospectively. No new operational grant/admission system is required.

Use two complementary checks:

**Paired recorder characterization.** Plan three paired repetitions of pinned Task0051 baseline versus candidate with fixed **AB / BA / AB** order. Each side performs **256 event-record appends and 256 batch-record appends**, using the same valid generated record/update sequence and declared allocation/page history. Exercise genuine encode/publication paths, not already encoded bytes alone. Use a bounded fixture-only baseline adapter/source snapshot; no production monkeypatch or ambiguous import of whichever live implementation happens to be installed. Baseline and candidate must produce independently checked compatible records and accounting. Report comparison assumptions and host/order dependence; favorable finite differences do not identify the sole cause or guarantee a ceiling.

**Final-source generated streaming checks.** Run the actual revised producer/consumer/core. Cover normal delivery at **500/2500/5000 offers/s**, slot reuse, capacity and forced contention, pre-return/post-return/post-output interruption, dead mutex owner, failed start, torn/failed record publication and cleanup diagnostic failure. Combine injections where meaningful; use explicit barriers and deterministic unit tests for precise interleavings. Overload, misses and timing exceedances are observable results, not grounds to replace a run until it looks good. Do not run the full 24-case matrix or infer HDF/model performance from stub throughput.

The separate Task0052 generated envelope is:

- **20 native child-process invocations maximum**, counting setup failures, aborts, comparison workers, affected reruns and checks started from tests. One bounded producer/consumer fixture case counts as one invocation; paired recorder work counts too.
- At most **128 configured artificial offers per streaming invocation**, **2560 configured offers total** across all attempts. Recorder-only workers offer zero events and are counted separately.
- At most **four paired recorder attempts** including failures/reruns: **2048 event-record appends and 2048 batch-record appends maximum** across both sides of those comparisons. Streaming-path record updates are separately counted and bounded by their offers/stages.
- **5 s per invocation including cleanup**, **120 s total native-characterization wall time including setup/finalization**, **16 MiB total owned diagnostics**. Retain Task0050's existing per-process/aggregate RSS outer guards; observed generated RSS is not future decoder/model feasibility.

This budget permits the planned comparisons and failure checks plus limited affected repairs; it does not authorize an optimization search. Fix correctness defects within scope and rerun affected checks within the totals. After the last behavior change, require new native evidence for affected paths on the **final source hashes**; earlier-version observations remain labeled historical within this task. If budget or host limitations prevent that, report exactly which paths lack final-source coverage. Do not claim full native revalidation or replenish the budget automatically.

Run focused tests of changed streaming code and independent expected layouts/CRC/state transitions, including read compatibility with records generated by the pinned Task0051 encoder and failure uncertainty. Lint/format relevant code. No historical full suites, model/native matrices, new dependency/build or privilege escalation to retry POSIX shared-memory creation. Keep the explicit file-backed mapping and fresh owned ignored directories; no runtime fallback or overwritten prior evidence.

## 6. Make a decision, including an unfavorable one

Separate software correctness, observed generated instrumentation performance and operational readiness. A correct revision may still exceed the proposed ceilings. **Any observed over-ceiling eligible candidate append must remain a failure of that candidate's sampled ceiling criterion**; a later favorable run does not erase it. Evaluate the baseline separately. With no exceedance, say only that the finite generated cases met that criterion, not that future service has a hard bound.

Do not raise the 50/200μs limits to declare success. If correct instrumentation cannot satisfy them, recommend an explicit later protocol/budget decision or an alternative architecture, with the evidence that motivates it. A future revision is not adopted by this task. Stop expanding generated tests when they no longer address a named uncertainty.

Produce:

- Focused versioned implementation/test changes; retain fixture-only entrypoints. Add a characterization entrypoint only if the existing one cannot express this scope cleanly.
- `configs/streaming/development_streaming_instrumentation_v1.json` — pinned baseline/candidate identity, actual timing boundaries/layouts, prospective cases/orders/envelope and fixture-only flags; operational execution/allowance remain false.
- `docs/development-streaming-instrumentation.md` — English report leading with the actual instrumentation decision, comparison evidence, final-source native coverage and remaining P2/P3/P4 limits.
- `results/tables/final/task0052-streaming-instrumentation-cases.csv` — small per-case/operation/repetition aggregates, including failures, coverage, counts, exceedances and units; no operational payloads.
- `results/tables/final/task0052-streaming-instrumentation-summary.json` — all attempts/source versions, generated work/record operations, exact resource/clock observations and prerequisite decision.
- Actual prompt and self-contained Italian handoff; README/index/memory updated in place from the verified revision.

Use **`completed_generated_streaming_instrumentation_characterization`** when the bounded characterization and claimed checks are complete, even if its engineering result is unfavorable. Record separate instrumentation status `sampled_limits_met`, `sampled_limits_exceeded` or `incomplete`; record actual prerequisite readiness without suggesting operational acceptance. Unfinished required validation is a partial result, not completed characterization by assertion.

Report P1 retained/revalidated coverage, P2 measured/bounded versus opaque synchronization/Python/native/workspace items, P3 generated clock/logging/supervision evidence versus operational uncertainty, and **P4 ungranted**. Real HDF/model integration, workspace/effective-thread checks and the physical 24×768/840s proposal remain future decisions. Recommend one next concrete step based on the result; do not launch it.

Preserve Task0049 CPU/synthetic closure, Task0036 unresolved status, Task0034 gates, permanent YES/YES/YES, particle192/192 consumed/canonical deferral, all historical outcomes, accepted Task0024 export versus failed Task0025 performance and no current MPS claim. Generated timings/correctness cannot establish scientific strict-tail usefulness, physical signal efficiency, causal nonlinearity or detector readiness. No implied official CERN/experiment affiliation.

Final Italian delivery must explain the code change, exact generated comparisons and negative observations, all attempts/remaining gaps and the next separate decision. Generated numerical/record/timing activity is positive; **operational** data/model/inference work remains zero. Verify historical evidence bytes and local links, then finish with exact **manual Git review, selective staging, staged review, Conventional Commit and push commands last** for the actual branch/upstream. Exclude ignored diagnostics and unrelated changes. Do not stage, commit or push.

Proceed with **Task0052 generated instrumentation repair and characterization only**.
