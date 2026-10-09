# LatentTrigger — Task 0022: Arithmetic-Aware Frozen CPU Benchmark v2

You are continuing **LatentTrigger**. Perform **Task0022 only**.

Task0021 completed the isolated AE numerical review on the same1024 prepared inputs. It confirmed complete-grid failures of the unchanged v1 reconstruction and score tolerances, byte-exact same-shape repetitions and zero sampled decision mismatches at all four frozen thresholds.

Implement and validate a **separately versioned arithmetic-aware CPU benchmark contract**, then perform **one conditional complete new CPU campaign**.

This prompt explicitly authorizes that prospective benchmark-policy revision and single finite campaign after successful validation, source freeze and prerequisite checks. It does not retrospectively pass Task0020 or replenish its consumed slot.

No fitting, optimizer updates, checkpoint selection, recalibration, particle execution, MPS, export, quantization or test evaluation is authorized.

## 1. Inspect actual state and preserve history

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, and the Task0019–0021 relevant briefs/reports/handoffs/protocols/curated summaries.

Read the complete inactive Task0022 brief in:

```text
docs/ae-batch-parity-review.md
results/tables/final/task0021-ae-batch-parity-review-summary.json
```

Planning inspection found clean `main` tracking `origin/main`, with Task0021 committed at:

`17a7146f775df47f1b542e18300860275f01c10c`

Verify actual status/index, branch/upstream, HEAD and task numbering. Reconcile the later Task0021 commit in current memory without rewriting historical handoffs.

Preserve:

- Frozen PCA, AE v1/v2, preprocessing/scalers/splits and calibration artifacts.
- All Task0020/0021 executable, protocol, acceptance, receipt and curated-result bytes.
- Task0020’s partial failed consumed campaign.
- Task0021’s completed consumed diagnostic review.
- Particle192/192 and canonical execution deferral.
- Unrelated edits and read-only synced `sources/`.

Use isolated new v2 modules and configuration. Do not edit the old comparator, loaders, model arithmetic, timing kernels or consumed launch routes to reinterpret history.

Save the actual prompt and initial handoff before substantive work:

```text
docs/prompts/0022-frozen-cpu-benchmark-v2.md
docs/handoffs/0022-frozen-cpu-benchmark-v2.md
```

## 2. Bind the unchanged scientific inputs

Reuse the exact frozen PCA and compact-autoencoder-v2 configurations, artifacts, calibration-result identities and four strict thresholds recorded by Task0020/0021.

Use existing canonical loaders. Preserve PCA’s six centered/non-whitened FP64 components and AE’s155 FP32 parameters/8→6→3→6→8 architecture.

Stored inputs remain already-standardized FP32 `[1024,8]`; do not scale again. PCA computes FP64, AE forward remains FP32, and both canonical SSE scores retain FP64 cast-before-subtraction, squares and reduction.

The only permitted source of real numerical input is:

```text
results/benchmarks/task0020-frozen-cpu/prepare/input.npy
```

Verify its original preparation/provenance lineage, size, header and hashes before numerical opening. Expected identities include:

```text
file size: 32896 bytes
file SHA256:
7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e

C-order array bytes SHA256:
2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05
```

These are the original first1024 source-ordered dev-training rows. Do not reopen raw/processed stores, perform custody replay, request another population or choose different rows.

A new preparation worker may load this array once and create a bounded byte-identical campaign-local copy for the six fresh workers. Audit the original prepared-array read and subsequent worker reads separately from population requests and numerical presentations.

Missing, altered or incompatible artifacts block execution; do not rebuild/refit/download replacements.

## 3. Derive and implement the arithmetic-aware gate

Create an isolated numerical-policy implementation and a strict versioned protocol, for example:

```text
configs/benchmarks/frozen_cpu_v2.json
```

Bind this actual prompt, scientific identities, arithmetic assumptions, derivation/source, exact protocol, current source acceptance and fixed campaign path. Reject unknown keys, arbitrary tolerances, observed-error multipliers and unsafe overrides.

Use primary numerical-analysis sources for the standard floating-point model, such as:

```text
https://nhigham.com/wp-content/uploads/2023/10/high93s.pdf
https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html
```

Derive the project recurrence explicitly; a citation alone does not validate its implementation.

### AE reconstruction envelope

Use the Task0021 proposal as the starting specification:

```text
u32 = 2^-24
u64 = 2^-53
gamma_m(u) = m*u / (1-m*u)
m = 2*n+2
E0 = 0
```

Affine input dimensions are8,6,3,6. Let `h64` be fixed rounded FP64 diagnostic activations using the exact stored FP32 parameter values promoted to FP64.

For each affine layer:

```text
M_l = |W_l| |h64_(l-1)| + |b_l|

E_l = (1 + gamma_m(u32)) |W_l| E_(l-1)
      + (gamma_m(u32) + gamma_m(u64)) M_l
```

ReLU is1-Lipschitz and propagates the envelope without amplification.

Document what this bounds: differences between computed FP32 execution and the fixed computed FP64 diagnostic path, including that path’s rounding. The FP64 copy is not exact real-arithmetic truth or a new canonical model.

Require both FP32 shapes to lie within their justified envelopes against that diagnostic path, and across-shape reconstruction differences to satisfy the corresponding pair envelope, `D=2*E_output` when the common envelope is used.

Include local affine checks comparing actual FP32 affine outputs with FP64 diagnostics on those same stored FP32 layer inputs. Violated local assumptions/checks block success; do not enlarge the bound.

### Bound-evaluation accuracy

The Task0021 envelope omitted FP64 evaluation rounding and was explanatory. Do not copy it unchanged into an active gate.

Implement auditable outward/error accounting for all bound operations, including magnitudes, matrix-vector products, gamma constants, recurrence and pair envelope.

Use operation-level outward scalar/vector primitives or an equivalently justified method. One `nextafter` applied only after a multistep BLAS dot product does not establish an upper bound on the whole calculation.

Document rounding, overflow, subnormal/underflow and accumulation assumptions. Either include required absolute underflow allowances or make exclusions checked prerequisites for the supported scope. Do not treat nonfinite bounds as unlimited permission.

Bind the actual CPU build/settings and retain local checks. Distinguish an engineering bound under stated assumptions from a universal backend certificate; exact native-kernel attribution is not established by Task0021.

No decimal slack fitted to observed maxima, hidden multiplier or policy search is permitted.

### Canonical SSE propagation

For reference residual `r=x-y_ref`, reconstruction difference bounded componentwise by `D`, derive an across-shape score bound from:

```text
Q = 2*sum(|r|*D) + sum(D²)
```

Account explicitly for residual computation, FP64 subtraction/square/reduction errors in both canonical scores and outward evaluation of Q. Do not assume the computed residual is exact.

The proposed `gamma_32(u64)` allowance is usable only after deriving its operation count, scale and conversion between computed and exact nonnegative score scales. Use no unexplained epsilon.

Preserve the actual public canonical SSE computation. The bound validates its difference; it does not replace its arithmetic.

Retain:

- Same-shape separated/public score `atol=rtol=1e-12`.
- Byte-exact repeated same-shape reconstruction and score on the supported identical runtime.
- Byte-exact full-reference hashes before/after.
- Finite input/output/score/bound checks.
- Zero strict decision mismatches at every frozen threshold on all1024 rows, every batch, pre/post timing.
- Strict `score > threshold`; ties remain rejected.

PCA retains its original reconstruction/score `atol=rtol=1e-12` checks. Do not apply the AE envelope to PCA.

## 4. Validate the policy before real numerical access

Add independent, meaningful synthetic tests for:

- Gamma constants, dimensions and recurrence.
- Outward calculations checked against exact rational or higher-precision small fixtures.
- Cancellation, near-zero outputs and mixed signs.
- Local affine errors, bias inclusion and FP64 diagnostic rounding.
- ReLU near-zero/sign-change behavior and envelope propagation.
- Score-bound construction, both SSE evaluation errors and zero-score cases.
- Threshold equality/adjacent values and mismatches despite accepted numerical error.
- Nonfinite/overflow/unsupported arithmetic conditions.
- Corrupted parameters, input identity and reference mutation.
- Same-shape score consistency and repeatability.
- Scope refusal before input opening.
- Timing-boundary preservation, guards, blocked imports/native work, cleanup and exclusive campaign/no-retry behavior.

Ordinary tests use self-contained fixtures without operational artifacts, data, receipts or `.git`.

Before freezing, perform a fixed bounded synthetic validation of the new policy and startup/operation footprint using the four already defined Task0021 synthetic families and unchanged batch grid/settings. Record coverage, violations and resource costs; do not search seeds/domains/constants until the gate passes.

Synthetic numerical validation does not authorize reading the prepared real array early.

Run the appropriate full synthetic suite, portable checkout, lint/format, dependency consistency and CPU smoke. Report current counts;827 is historical Task0021 acceptance, not the new result.

Create complete current source acceptance covering the new policy/controller/workers/helpers and reused dependencies. Verify historical accepted bytes remain unchanged.

Freeze executable code, numerical policy and protocol before the single real campaign. No real diagnostic trial followed by policy adjustment and benchmark replay is authorized.

## 5. Preserve the exact three timing scopes

Use CPU eager canonical NumPy/PyTorch, deterministic algorithms, PyTorch intra/inter-op1 and verified effective BLAS/OpenMP1, with all five prescribed thread variables set before imports.

Retain the existing thread-enforcement helpers/settings and record actual runtime bindings. No backend switch, precision change, AMP, compilation, quantization or tuning.

Keep the three Task0020 scopes:

1. Prepared model reconstruction, including kernel allocations but excluding loading, preparation, SSE, thresholds and guard queries.
2. Canonical FP64 SSE and four decisions on the actual batch’s precomputed reconstruction, without forward execution.
3. Existing public canonical `score` adapter and four decisions, including its validation/wrapping/conversion/forward/SSE overhead.

Keep identical math and operation order. Numerical-policy evaluation, FP64 diagnostic copies, local affine checks and tracing belong outside timer pairs and remain separately accounted within worker wall.

Remove diagnostic hooks before warm-ups/timing and restore/clean them safely. Do not time a traced or modified model.

Do not sum medians of separate scopes and call them measured end-to-end cost. Raw-source decompression and online feature construction remain unmeasured.

## 6. One complete independent campaign

Use the fixed new exclusive output:

```text
results/benchmarks/task0022-frozen-cpu-v2/
```

Provide an explicit documented v2 campaign CLI. Metadata-only validation cannot reserve or open numerical arrays.

After successful validation/source freeze/prerequisite checks, atomically reserve before real input opening. An existing reserved/foreign/partial/inflight/completed output blocks all real routes. Concurrent launches have at most one winner.

Fresh workers independently verify protocol/source/artifact/parent/phase/predecessor bindings.

Protocol:

| Field | Fixed value |
| --- | --- |
| Models | Frozen PCA and compact AE v2 |
| Worker order | PCA1, AE1, PCA2, AE2, PCA3, AE3 |
| Batch grid | `[1,8,32,128,1024]` |
| Scope order | Reconstruction, score/decision, adapter/decision |
| Per cell |20 warm-ups, then200 timed invocations |
| Window schedule | `start=(i mod (1024/B))*B`, independently reset per phase |
| Timer | `perf_counter_ns`, synchronous CPU |
| Timer context |200 empty pairs per worker; never subtract |
| Complete campaign |90 cells,18000 timings,1800 warm-ups,1200 empty timer pairs |

All six workers must supply their own new measurements and pre/post numerical checks. **Do not merge historical PCA1 into these repetitions.**

Retain the finite envelopes:

- Numeric worker lifetimeRSS≤1GiB; whole-native reservation≤512MiB.
- Stdlib parentRSS≤128MiB.
- One numeric worker at a time.
- Preparation≤60s; each timing worker≤60s; aggregation≤30s.
-450s allocated stages inside600s total, including imports/orchestration/verification/cleanup.
-2s bounded termination/reaping slack inside the budget.
- Fresh guards before data, at phases and before/after timed invocations;50ms watchdog scheduling intent.
- WARN advisory, pressure unavailable explicitly unknown, CRITICAL/malformed primary accounting latched.
- Optional bounded global context with no memory floor, stable-readiness wait or polling.

Global context cannot become a disguised veto. Process caps do not guarantee machine-wide headroom; periodic monitoring can overlap timings and must be disclosed.

Any failure after reservation consumes the campaign, preserves actual peaks/partial evidence and stops dependents. No overwrite, reset, alternate output, remaining-worker continuation or repair/replay is authorized.

If blocked before reservation, deliver the validated implementation and exact blocker without requesting an idle Mac or another readiness task.

## 7. Report numerical acceptance and performance separately

For every model/batch/scope/worker cell retain count/min/max/mean/population std and p50/p95/p99 with linear quantiles.

Report all three worker distributions and median of worker medians. Define throughput explicitly, including `B/mean invocation seconds`; distinguish batch latency, amortized time/event and single-event latency.

For AE report:

- Observed reconstruction and SSE differences.
- Derived envelope maxima and observed-error/envelope ratios.
- Local affine check coverage and failures.
- Same-shape repeatability and pre/post reference identities.
- Frozen threshold mismatch counts and actual sample margins.
- Numerical-verification/diagnostic costs separately from timed kernels.

Conservative bounds may permit more drift than observed. Quantify that conservatism and do not present envelope size as measured error.

The arithmetic bound and zero sampled threshold mismatches are independent requirements. Neither establishes universal decision equivalence, unchanged calibration FPR, test acceptance or improved scientific discrimination.

Record actual hardware/software/build/thread/precision/timer/source provenance and shared-host conditions. Distinguish fresh metadata from historical M5/16GB observations; unavailable fields remain unknown. No app-content inspection or app management.

Report original prepared-input reads, campaign-local worker reads,1024 unique reused rows, numerical versus timed/warm-up presentations, zero new population/store-custody requests and zero optimizer updates.

The campaign’s wall/deadline accounting is separate from model latency. Do not subtract timer/monitor overhead or claim uncontended/hard-real-time trigger performance.

## 8. Deliverables and memory

Create:

```text
docs/frozen-cpu-benchmark-v2.md
results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json
results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv
```

Include a concise derivation/assumptions section linked to the numerical policy and primary sources. Keep raw arrays, diagnostics, timings, guard/audit receipts, acceptance records, logs and snapshots ignored.

Update README, living memory and handoff index in place. Record the explicit prospective engineering-policy revision and its actual outcome while preserving v1 failures, Task0021 findings, canonical model/calibration identities and particle deferral.

Verify JSON/CSV/report agreement, expected/actual counts, receipt lineage, frozen and historical source identities, links, exclusions, whitespace and actual diff.

State:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Hosted CI remains unverified unless directly established.

If complete and accepted, propose one bounded Task0023 CPU/MPS comparison brief with actual MPS availability, separate device numerical/decision validation and finite authorization. The CPU arithmetic contract is not automatically a certificate for MPS.

If incomplete/blocked, identify the failed requirement, retained measurements and missing evidence; do not propose MPS as if its CPU prerequisite passed.

## 9. Informative final delivery

Follow the standing preference in `docs/development.md`.

Write a self-contained Italian final response, approximately600–1000 words excluding Git, adjusted to the actual findings. Include:

- What changed in the numerical contract, why, and what remained scientifically frozen.
- How bound evaluation was validated, with assumptions and practical limits.
- Actual complete/partial campaign coverage and resources.
- A readable PCA/AE timing table, including batch1 latency and representative throughput batches.
- Numerical error/envelope ratios, same-shape repeatability and threshold mismatch results.
- Current tests/checks and verification gaps.
- Interpretation: what the measurements support and what remains unresolved.
- One recommended concrete next task.
- Report, JSON, CSV and handoff links and test-exposure declarations.

Distinguish historical, newly measured, inferred, proposed and unverified statements. Explain key technical terms. Do not replace substantive findings with bare test counts or “see report”.

Missing cells remain missing, not zero. A numerical-policy revision is not a measured speedup or a retroactive v1 pass.

## 10. Required final Git section — last section of the response

Do not automatically stage, commit or push.

End with exact status/diff/index review, selective `git add --` for the actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push for the verified branch/upstream.

Include this prompt/handoff, new protocol/policy/controller/workers/tests, report/curated JSON/CSV and affected README/memory/index files. Exclude operational inputs/arrays, receipts, acceptances, logs, snapshots, caches and unrelated work.

Proceed with **Task0022 only**.