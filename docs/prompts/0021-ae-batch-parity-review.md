# LatentTrigger — Task 0021: Frozen AE Batch-Shape Numerical Parity Review

You are continuing **LatentTrigger**. Perform **Task0021 only**.

Task0020 implemented the guarded CPU benchmark foundation, passed763 synthetic and portable tests, and consumed its single real campaign. Preparation and PCA1 completed; AE1 failed the across-batch reconstruction gate before timing. Only15/90 cells and3000/18000 timings exist. Preserve that partial failed outcome.

The objectives of Task0021 are to explain the numerical discrepancy as far as the evidence permits, assess its consequences for canonical scores and frozen decisions, and recommend one defensible next numerical contract.

This task authorizes bounded synthetic analysis and **one conditional AE-only real numerical review of the existing prepared1024 inputs**. It authorizes no performance timing, benchmark replay, fitting, optimizer updates, recalibration, MPS or test access.

The Task0020 campaign remains consumed. Particle192/192 and canonical deferral remain unchanged.

## 1. Inspect state and preserve accepted history

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, Task0019’s benchmark brief, and Task0020’s report, handoff, protocol, curated summary and CSV.

Planning inspection found clean `main` tracking `origin/main`, with Task0020 committed at:

`dba4635dfad1f29a06a3b1fb6c138885620be83e`

Verify actual state, task numbering and index. Reconcile the later Task0020 commit in current memory while preserving its historical handoff.

Read the actual small Task0020 records, especially:

```text
results/benchmarks/task0020-frozen-cpu/workflow.json
results/benchmarks/task0020-frozen-cpu/reservation.json
results/benchmarks/task0020-frozen-cpu/acceptance.json
results/benchmarks/task0020-frozen-cpu/AE1/receipt.json
results/benchmarks/task0020-frozen-cpu/prepare/prepared.json
results/benchmarks/task0020-frozen-cpu/prepare/access-audit.json
```

Inspect the accepted numerical implementation, worker, thread enforcement and canonical AE loader/forward/score.

Preserve all Task0020 executable/protocol/acceptance/receipt/CSV bytes, frozen model/config/calibration artifacts, particle source/contracts/slots and unrelated edits. Synced `sources/` remain read-only.

Save the actual prompt and initial handoff before substantive work:

```text
docs/prompts/0021-ae-batch-parity-review.md
docs/handoffs/0021-ae-batch-parity-review.md
```

## 2. Reconstruct the original failure accurately

Verify the recorded comparison:

```text
comparison: reconstruction_across_batch
atol: 1e-6
rtol: 1e-5
actual: -0.09302544593811035
reference: -0.09302345663309097
absolute_error: 1.989305019378662e-6
within_window_index: [0,5]
```

Analytically, `atol + rtol*abs(reference)` is approximately
`1.9302345663309095e-6`, with excess approximately
`5.907045304775261e-8`, or3.060273% of the limit.

Inspect the actual NumPy dtype/promotion used to calculate the implemented bound. Distinguish its executed arithmetic from an ideal FP64 calculation; quantify any difference without changing the historical comparator.

The original receipt verifies:

- Eight B1 prepared-versus-canonical reconstruction and same-shape SSE windows, exactly equal.
- Seven across-batch score/decision windows before failure.
- Zero decision mismatches only in those seven verified windows.
- No completed AE timing or post-timing checks.

Sample-relative row7/channel5 is inferred from the original prefix counts and loop order. Preserve that provenance distinction until the separately authorized review verifies it.

Do not describe the reported1.989305e-6 as the maximum across all1024 events. Earlier verified windows already contain larger absolute differences that pass their own relative bounds.

Preserve the original failure as failed. Do not infer full-grid score/decision equivalence, a corrupted model, convergence failure or scientific-quality failure.

## 3. Review the numerical contract and execution mechanism

Use primary sources and actual installed/runtime evidence.

Read the relevant PyTorch documentation:

```text
https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html
https://docs.pytorch.org/docs/2.14/notes/randomness.html
```

Explain the distinction between:

- Repeating the same operation with the same batch shape.
- Applying mathematically corresponding operations with different batch shapes.
- Numerical closeness of reconstructions.
- Closeness of canonical SSE.
- Identical strict decisions at frozen thresholds.

Deterministic execution does not by itself establish equality across different operation shapes.

Inspect input order/strides/dtypes, model state, inference mode, layer execution, score arithmetic and actual thread settings. Distinguish NumPy’s Accelerate backend from the actual PyTorch execution path; do not attribute a discrepancy to a particular GEMV/GEMM kernel without evidence.

Do not switch backend, precision settings, threads, model arithmetic or batch grid to make the discrepancy disappear.

Audit the comparator, reference slicing and numerical bookkeeping for implementation errors. Any defect found must be reported with its effect on existing evidence. Preserve historical code; add review helpers separately.

## 4. Bounded synthetic analysis with frozen weights

Load the small frozen compact-autoencoder-v2 artifact through its canonical loader. Preserve the exact155 FP32 parameter values and artifact identity.

Preregister one fixed synthetic study before executing it:

- CPU, existing deterministic settings, intra/inter-op1 and verified effective thread enforcement.
- Batch grid `[1,8,32,128,1024]`.
- Four1024×8 input families: zero/constant cases, a fixed signed power-of-two pattern, seeded uniform values in `[-8,8]`, and seeded standard-normal values clipped to `[-8,8]`.
- Seed1729; record exact generation recipes and input hashes.
- One guarded fresh worker,≤60s including imports and cleanup,1GiB RSS/512MiB whole native.
- No seed/domain search, timing benchmark or selection of favorable results.

For every family, compare identical rows across the batch grid against the full1024 reference. Measure repeatability at identical shapes, reconstruction and score differences, historical-tolerance violations, and strict-decision differences at the frozen thresholds.

Trace the existing affine/ReLU layers to locate the first divergence and its propagation. Report preactivation differences, output differences and ReLU sign changes where informative.

A diagnostic FP64 copy of the same stored parameter values is permitted solely as a higher-precision comparison. It is not a new canonical model, deployment variant or replacement runtime. Do not serialize it as a model or claim exact real-arithmetic ground truth.

Keep synthetic results separate from real-input findings. Failure to reproduce the historical discrepancy synthetically is a valid result; do not expand the study until a desired explanation appears.

Tests must use self-contained synthetic models/stores. Ordinary tests must not require the frozen operational artifact or ignored campaign files.

## 5. One conditional real numerical review

Create a strict review-only protocol, for example:

```text
configs/benchmarks/ae_batch_parity_review_v1.json
```

Bind the actual prompt, source acceptance, frozen AE/config/results/threshold identities, Task0020 lineage and exact prepared-input identity.

Use one exclusive new review directory:

```text
results/benchmarks/task0021-ae-batch-parity-review/
```

This is a separately authorized diagnostic allowance. It cannot replenish or continue Task0020, enable timing or authorize another output path.

Before opening numerical data, verify the original workflow, preparation audit/metadata, input-file size/hash and frozen provenance. The permitted numerical input is only:

```text
results/benchmarks/task0020-frozen-cpu/prepare/input.npy
```

Load it once as a bounded, non-pickle FP32 `[1024,8]` array. Do not reopen processed/raw stores, request another population, rebuild inputs or select different rows. Hashing metadata/file bytes and loading a numerical array must be reported distinctly.

After successful synthetic validation and source freeze, atomically reserve the review before real numerical input access. Existing foreign/partial/inflight/completed output blocks execution; competing launches have at most one winner.

Run one fresh AE review worker:

- ≤60s including imports, input/model loading, diagnostics and cleanup.
- LifetimeRSS≤1GiB, whole-native reservation≤512MiB.
- Stdlib parentRSS≤128MiB.
- Total real review≤120s including orchestration/aggregation/cleanup.
- One numeric worker; existing fresh process checks and50ms watcher intent.
- WARN advisory, unknown pressure disclosed, CRITICAL latched; malformed primary accounting fails closed.
- Optional bounded global context, no free-memory floor/readiness wait.
- Parent deadlines and bounded termination/reaping; no budget extension.

Use the unchanged CPU/thread/precision/model settings and frozen thresholds from Task0020.

Compute full1024 references and review **every window in every grid batch**, including B1. Collect:

- Same-shape reconstruction/SSE consistency.
- Repeatability at identical shapes.
- Across-shape reconstruction and public/prepared score differences.
- Counts and locations of violations under the unchanged v1 criteria.
- Decision mismatch counts for each frozen threshold.
- Score distance to each threshold and the largest observed score changes.
- Layerwise divergence and relevant ReLU changes.
- Input, parameter, threshold and reference hashes before/after.

Confirm or refute the inferred historical row7/channel5 location using the identical input bytes. Report changed runtime bindings explicitly; do not assume exact reproduction across versions.

This is a diagnostic review. Expected violations of the old across-shape tolerance are findings to aggregate, not grounds to silently stop coverage at the first violation or claim benchmark acceptance. Preserve `passed:false` for violated comparisons. Resource/integrity/nonfinite failures still stop and latch.

Do not catch and ignore unrelated exceptions. Do not modify the old verifier’s behavior.

Keep per-event arrays in bounded memory. Persist aggregates, hashes and a small bounded set of discrepancy coordinates/values, without labels or event IDs.

A failure after reservation consumes this review, even at zero numerical rows. No repair followed by replay is authorized. Preserve partial evidence and finish with the exact blocker.

## 6. Assess score and threshold consequences

Explain how reconstruction discrepancies propagate to SSE. For reference residual `r=x-y_ref` and reconstruction change `d=y_actual-y_ref`:

```text
S_actual - S_ref = -2*r·d + ||d||²
```

The corresponding absolute-value bound can help interpret score changes. Account for FP64 evaluation/reduction rounding before presenting any computed bound as rigorous; distinguish explanatory algebra from a certified floating-point guarantee.

A small reconstruction discrepancy does not automatically preserve decisions near a threshold. Report actual decision mismatches and score margins at all four frozen thresholds.

Zero mismatches on these1024 dev-training inputs establish agreement on that sample, not unchanged FPR on calibration/test or universal deployment equivalence. Synthetic threshold cases test logic, not physics acceptance.

Do not reopen calibration/selection/test populations, retune thresholds, discard troublesome rows or rank scientific model quality from reconstruction errors.

## 7. Make one explicit prospective recommendation

Compare these routes using the actual findings:

1. Retain the current numerical contract and leave the full benchmark blocked.
2. Recommend a separately versioned batch-shape numerical contract with justified reconstruction, score and decision requirements.
3. Treat a demonstrated implementation defect as requiring a correction and newly authorized campaign.

Choose one recommended next route and explain scientific/artifact compatibility.

Any proposed tolerance or acceptance metric must be justified from arithmetic, model/input scope and measured diagnostics. Do not merely multiply the historical error by a safety factor, round upward to a passing value or remove reconstruction checking without justification.

Preserve finite-output checks, same-shape consistency, canonical FP64 SSE and strict frozen decisions. Document any remaining uncertainty.

Proposed benchmark-policy changes remain **inactive in Task0021**. Do not modify `frozen_cpu_v1.json`, retroactively pass Task0020, implement a benchmark v2 or launch performance measurements.

If a revised contract is defensible, provide an implementation-ready Task0022 brief for a separately authorized complete CPU campaign. It must produce its own independent repetitions; historical PCA1 cannot be silently combined with new workers into one three-repetition campaign.

MPS remains downstream of a complete accepted CPU reference.

## 8. Deliverables and validation

Create:

```text
docs/ae-batch-parity-review.md
results/tables/final/task0021-ae-batch-parity-review-summary.json
```

Add only the small review protocol, isolated diagnostic helpers and meaningful focused tests required. Keep existing canonical/Task0020 source and artifacts unchanged.

Run appropriate synthetic tests, the full self-contained suite, lint/format and portability checks. Freeze current review source before the real diagnostic. Preserve historical763-test acceptance rather than reporting it as newly run evidence.

Validate numerical bookkeeping, failed/successful status distinctions, JSON, identity/receipt relationships, local links, whitespace and output exclusions. Raw diagnostics, arrays, logs and acceptance records remain ignored.

Update README, memory and index in place. Record actual synthetic versus real presentations, prepared-input numerical reads, unique reused real rows, zero new store population requests/custody operations and zero optimizer updates.

State:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Retain Task0020 partial/consumed status and particle192/192/canonical deferral. Hosted CI stays unverified unless directly established.

## 9. Persist the user’s delivery preference

The user explicitly requests more informative final task outputs.

Add a concise standing requirement to `docs/development.md` and reference it from living memory: future task responses must explain the completed work, key data, validation, limitations, decisions and next step in enough detail to serve as a useful handoff to the planning chat.

Write the final response in Italian, using clear prose and compact tables where helpful. Aim for approximately600–1000 words excluding Git, scaled to the actual work; completeness matters more than an exact count.

The response must stand alone and include:

- Overall outcome and what was actually implemented, inspected and executed.
- The original failure and how the review confirmed, refined or failed to explain it.
- A table of reconstruction/score errors, violated criteria, threshold mismatch counts, repeatability and coverage by batch.
- Resource/time measurements and actual data access/presentation counts.
- Tests/checks actually run and remaining verification gaps.
- What the results imply for canonical artifacts, calibrated decisions and future benchmarks.
- The selected recommendation, remaining uncertainties and concrete next-task scope.
- Links to report, curated summary and handoff, plus test-exposure declarations.

Clearly label historical, newly measured, inferred, proposed and unverified statements. Explain technical terms when needed. Do not replace substantive findings with “see report”, raw logs or a bare test count.

If execution is partial/blocked, report actual coverage and missing evidence rather than filling the table with zeros or generic assurances.

## 10. Required final Git section — last section of the response

Do not automatically stage, commit or push.

End with exact status/diff/index review, selective `git add --` for the actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push for the verified branch/upstream.

Include this prompt/handoff, report/summary, review protocol/helpers/tests and affected development/README/memory/index files. Exclude diagnostic inputs/arrays, receipts, acceptances, logs, snapshots, caches and unrelated work.

Proceed with **Task0021 only**.