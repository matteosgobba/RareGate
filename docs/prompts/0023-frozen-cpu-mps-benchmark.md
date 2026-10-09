# LatentTrigger — Task 0023: Frozen CPU/MPS Parity and Inference Comparison Foundation

You are continuing **LatentTrigger**. Perform **Task0023 only**.

Task0022 completed and accepted the arithmetic-aware CPU benchmark:90 cells,18000 measured invocations,1800 warm-ups and three independent workers per model. The frozen scientific models, inputs, canonical scores and thresholds are unchanged.

Implement an isolated CPU/MPS comparison foundation for **compact-autoencoder-v2**, validate it, then conditionally perform **one new finite paired campaign**.

This prompt authorizes one bounded automatic device-availability check, one conditional fixed synthetic device-validation study and one conditional real campaign after successful validation/source freeze. It does not authorize retries, performance tuning or a required speedup.

If MPS is unavailable or its numerical/accounting requirements cannot be established, deliver the validated foundation and precise blocker before real input access or campaign reservation.

No fitting, optimizer updates, calibration, particle execution, PCA/MPS redesign, export, quantization, simulation or test evaluation is authorized.

## 1. Inspect actual state and preserve the staged prerequisite

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, Task0022’s report/handoff/protocol/arithmetic derivation/summary/CSV, and its complete Task0023 brief.

Planning inspection found:

```text
branch: main
upstream: origin/main
HEAD: 17a7146f775df47f1b542e18300860275f01c10c
Task0022: 16 intended files staged, not yet committed
unstaged tracked changes: none observed
```

Verify actual state and live numbering. The user may have committed Task0022 since this inspection.

If Task0022 remains staged, record its exact staged paths/blob identities and preserve that index content. Do not stage, unstage, reset or commit anything. Preserve initial prerequisite snapshots where useful and record overlaps in README/memory/index.

Do not block implementation merely because Task0022 is uncommitted. Treat its accepted working-tree bytes as the verified prerequisite snapshot, without inventing a commit.

Preserve frozen artifacts, all Task0020–0022 source/protocol/acceptance/receipt/result bytes, consumed slots, particle192/192 and local canonical deferral. Synced `sources/` remain read-only.

Save:

```text
docs/prompts/0023-frozen-cpu-mps-benchmark.md
docs/handoffs/0023-frozen-cpu-mps-benchmark.md
```

Keep new device policy/controller/workers/tests isolated. Do not change old launch routes, numerical criteria or timing kernels.

## 2. Bind the unchanged model and prepared inputs

Use the canonical frozen compact-autoencoder-v2 loader, exact155 FP32 parameters, original architecture/features/scalers and all four calibrated thresholds.

Canonical forward remains FP32. Canonical score remains FP64 SSE on CPU, casting both input and reconstruction before subtraction, followed by strict `score > threshold`.

PCA remains the accepted CPU reference from Task0022; this task compares the same frozen AE on CPU versus MPS.

The permitted real input source remains:

```text
results/benchmarks/task0020-frozen-cpu/prepare/input.npy
```

Verify original preparation lineage,32896-byte size, bounded non-pickle FP32 `[1024,8]` header and frozen file/payload hashes before numerical opening.

Use the exact original1024 already-standardized dev-training rows. Do not reopen raw/processed stores, request another population, rebuild/rescale inputs or select different rows.

A new preparation worker may read the original once and create a bounded byte-identical campaign-local copy. Each of six timing workers may read that copy once. Report these reads separately from unique rows and forward/timing presentations.

Verify parameter/input CPU→MPS→CPU round trips preserve FP32 bytes. Do not serialize a new scientific model or change calibration provenance.

## 3. Device availability: one bounded check before real data

Current Task0022 CPU smoke reports `MPS available: False`; the cause is unverified. Historical native MPS compatibility exists but is not current admission evidence.

Implement the foundation and software tests before the actual automatic availability check.

Use one fresh guarded process,≤30s including imports/cleanup, in the execution context intended for the campaign. Record:

- Python executable, architecture, OS/runtime/build and source identity.
- `torch.backends.mps.is_built()` and `is_available()` separately.
- Relevant MPS environment settings and execution-context facts actually known.
- When available, a tiny constant-only MPS tensor operation, completion synchronization, expected result and primary device accounting.
- Actual errors/timeouts and unavailable fields.

No real numerical input, model-training operation or campaign reservation belongs in this check.

Do not infer that the physical GPU is absent from a false availability flag. Attribute a sandbox/context restriction only when evidence establishes it.

If unavailable, stop automatic device execution and deliver the foundation with zero real rows and an unreserved campaign. Do not poll, search execution contexts until one passes, reinstall libraries, request privileges, alter OS/sandbox settings, close apps or silently fall back to CPU.

Fresh campaign workers must still independently verify device prerequisites; that is protection against changed state, not a readiness loop.

Provide a concrete validated CLI/manual path and its remaining conditions where useful. Do not launch it automatically after a blocker or treat an old availability receipt as reusable admission.

## 4. Preregister a separate device numerical policy

Create a strict isolated protocol and device-policy specification, for example:

```text
configs/benchmarks/frozen_cpu_mps_v1.json
```

Bind this prompt, accepted CPU reference, frozen scientific identities, exact input, runtime/settings, numerical assumptions, timing semantics, resource limits, source acceptance and fixed paths.

Consult installed APIs/source and primary documentation:

- [MPS backend](https://docs.pytorch.org/docs/2.14/notes/mps.html)
- [MPS environment variables](https://docs.pytorch.org/docs/2.14/mps_environment_variables.html)
- [Synchronization](https://docs.pytorch.org/docs/2.14/generated/torch.mps.synchronize.html)
- [Tensor allocations](https://docs.pytorch.org/docs/2.14/generated/torch.mps.current_allocated_memory.html)
- [Driver allocations](https://docs.pytorch.org/docs/2.14/generated/torch.mps.driver_allocated_memory.html)

Reject unknown fields, arbitrary tolerances and unsafe overrides.

Pin ordinary FP32 forward, no AMP/compilation/quantization or backend search. Set CPU fallback and optional MPS fast math disabled before imports under this prospective benchmark profile; record the requested/effective settings. Preserve the normal operator selection and allocator configuration, without watermark tuning or disabling allocator protections.

The CPU arithmetic contract is not automatically a Metal certificate. Derive the supported MPS reconstruction/local-affine/score checks independently.

You may reuse validated outward arithmetic primitives. If adopting the same layer recurrence/operation counts, justify their applicability to the supported device semantics and retain device-specific local checks, input/activation support conditions and actual build/operator/precision evidence.

Do not interpret FP32 output dtype alone as proof of every internal accumulation rule. Do not require a named native kernel when a supported operation-level contract is sufficient, but state unknown kernel details honestly.

No tolerance may be fitted to real-input maxima, multiplied until passing or selected through a policy search. Unsupported assumptions block before the real campaign.

Preserve:

- Finite inputs, reconstructions, scores and bounds.
- Frozen parameter/input/threshold round trips and identities.
- Supported local affine checks and propagated reconstruction/SSE bounds.
- Same-shape repeatability under the admitted deterministic runtime.
- Same-shape separated/public FP64 SSE `atol=rtol=1e-12`.
- Zero frozen-decision mismatches against the canonical CPU1024 reference for every row/grid before and after timing.
- Restored CPU and device reference hashes pre/post, without requiring cross-device byte equality.

The FP64 diagnostic path and bound evaluation remain on CPU and outside timer pairs. They are not new canonical model variants.

## 5. Validate software and the device separately

Add self-contained tests covering:

- Availability/build/context distinctions and unavailable exit before input/slot.
- Unsupported MPS operations/fallback refusal.
- Exact FP32 transfers and parameter preservation.
- Device-policy/local arithmetic/score-bound refusal.
- Synchronization ordering and transfer placement.
- Same-shape repeats, nonfinite results and threshold ties/mismatches.
- Host/device accounting types, cap equality/exceedance and failed peaks.
- Blocked GPU synchronization/import/accounting, parent deadlines and cleanup.
- Exclusive reservation, competing launches and truthful partial/blocked summaries.

Ordinary tests and portable CI fixtures must run without a physical GPU, operational data, artifacts, receipts or `.git`. Simulated device tests prove software behavior, not actual MPS support.

Run the appropriate full suite, lint/format, portable validation, dependency consistency and CPU smoke.942 is historical acceptance; report current results.

Freeze executable/protocol/policy bytes before actual device proof. If the bounded availability check passes, run **one fixed data-free synthetic device-validation worker≤60s**, using the four Task0021 families and batch grid.

Load only the small frozen AE artifact and synthetic inputs. Verify CPU/MPS numerical/local/round-trip/repeatability/strict-decision behavior under the preregistered device policy.

Apply the fixed host/device caps. Preserve its exclusive evidence; no seed/domain/operator/tolerance search or repeated synthetic device study.

If device validation fails, preserve the blocker and stop before real data. Do not repair code and replay it within this device-validation allowance.

Bind successful software acceptance, availability and device-validation receipts into final execution acceptance, verifying unchanged source throughout. Device proof and blocked outcomes must remain distinguishable.

Availability≤30s and device validation≤60s are separate from the≤600s real-campaign budget. Total automatic availability/device-proof orchestration is bounded≤120s, with no extension.

## 6. Correct timing boundaries and synchronization

Compare three scopes:

1. **Prepared reconstruction.** CPU uses preloaded FP32 CPU tensors. MPS uses preloaded device tensors. Input transfer is outside this scope. Synchronize pending MPS work before the start timestamp; forward and completion synchronization are inside the timed pair. Do not copy output to CPU inside this kernel-only scope.
2. **Score/decision on CPU.** Use the corresponding actual-batch precomputed reconstruction already copied to CPU outside timing. Include canonical FP64 casts/SSE/finite checks/four decisions. No forward or device transfer. Label this CPU postprocessing for both paths, not GPU scoring.
3. **Canonical adapter/decision.** Invoke existing public score with the model on the selected device and FP32 NumPy inputs, then four decisions. For MPS include input transfer, forward, output transfer/completion, CPU FP64 SSE and decisions. Explicitly establish synchronization placement and completion inside the measured pair.

Never compare asynchronous dispatch time with completed CPU computation. Retain all transfers inherent in the canonical adapter; do not replace it with a faster custom score.

Prepare window slices outside timers. Remove diagnostic hooks before warm-ups. Resource queries and numerical verification are outside timer pairs but included in wall budgets.

Report loading/model-device initialization/window/device preparation, numerical checks, synchronization/guard/cleanup and whole-worker costs with actual timer coverage. Do not invent separately measured transfer components when only a combined path was timed.

Do not sum separate-scope medians as measured end-to-end latency.

## 7. One contemporaneous paired campaign

Only after successful availability/device validation/current acceptance, atomically reserve:

```text
results/benchmarks/task0023-cpu-mps/
```

Existing foreign/reserved/partial/inflight/completed output blocks every real route. No alternate output, reset, overwrite or replay selector grants another campaign.

Run preparation and six fresh AE workers:

```text
CPU1, MPS1, CPU2, MPS2, CPU3, MPS3
```

Use one numeric worker at a time and independent current source/parent/phase/predecessor/device checks.

Fixed protocol:

| Field | Value |
| --- | --- |
| Batches | `[1,8,32,128,1024]` |
| Per-worker order | Ascending batch; reconstruction, score/decision, adapter/decision |
| Per cell |20 warm-ups,200 measured invocations |
| Windows | `start=(i mod(1024/B))*B`, independently reset per phase |
| Timer | `perf_counter_ns`, completed execution |
| Empty timer context |200 pairs per worker, no subtraction |
| Complete campaign |90 cells,18000 timings,1800 warm-ups,1200 empty pairs |

Each worker validates all1024 rows at every batch before/after timing, against a fresh canonical CPU reference bound to the accepted scientific/runtime identity. Check the device’s own full-reference repeatability separately.

Historical Task0022 results are context, not new CPU repetitions. Do not merge them into this paired campaign or use them as the primary speedup denominator.

No adaptive repeats, favorable-run selection, batch omission or required acceleration.

## 8. Finite host and device protection

Preregister and validate:

| Resource/stage | Limit |
| --- | --- |
| Numeric worker lifetimeRSS |≤1GiB |
| Whole-native reservation |≤512MiB |
| Stdlib parentRSS |≤128MiB |
| MPS tensor current allocations |≤256MiB |
| MPS driver allocations |≤512MiB |
| Preparation |≤60s |
| Each timing worker |≤60s |
| Aggregation |≤30s |
| Allocated stages / total campaign |450s /600s |
| Cleanup/terminate-kill-reap slack |Bounded2s inside budgets |
| Periodic checks |50ms scheduling intent |

For MPS workers, device accounting must use available validated primary APIs, with fresh samples before data/at phases/before-after invocations and periodic intent during blocked work. Preserve current versus driver allocation semantics and actual failed peaks.

CPU workers report device accounting as not applicable, not fabricated zeros. GPU query/synchronization hangs remain covered by independent parent deadlines.

Host/device metrics can overlap on unified memory; do not sum them as disjoint usage. Recommended working-set metadata is not available/free RAM or permission to exceed fixed caps.

Preserve contextual pressure behavior: WARN advisory, unknown disclosed, CRITICAL/malformed primary accounting latched. Global availability remains optional bounded context with no floor/stability loop.

Do not change allocator limits, purge caches or extend caps to pass. Release owned tensors/models, synchronize cleanup where possible, close watchers and reap every child. State practical scheduling/termination limits.

Any failure after real reservation consumes the campaign, retains partial evidence and stops dependent workers. No repair, continuation or replay is authorized.

## 9. Results, comparisons and limits

Report every completed cell’s count/min/max/mean/population std/p50/p95/p99 with linear quantiles, all three worker distributions and median worker medians.

Define throughput from pooled invocation means, keeping batch latency and amortized time/event distinct. Define paired CPU/MPS latency ratios and throughput ratios explicitly; report all three pairs and aggregation method.

Use matching scopes and contemporaneous workers. Score-only scope is CPU postprocessing, so its variations do not measure MPS kernel acceleration.

Retain outliers and shared-host interference; do not subtract timer/monitor/synchronization costs. Historical AE2 outliers remain historical and are not attributed without evidence.

Report numerical errors/bound ratios/local checks, same-shape repeatability, sampled decision mismatches/margins, round-trip identities, device peaks and actual transfers/synchronization placement.

Record actual build/Metal/MPS/runtime/thread/hardware/execution context. Unknown GPU core counts, thermal fields or native kernel details stay unknown.

Agreement on1024 dev-training rows does not establish universal decisions, recalibrated FPR, signal discrimination or physical trigger readiness. No scientific retraining/calibration/test exposure occurs.

## 10. Deliverables and next step

Create:

```text
docs/frozen-cpu-mps-benchmark.md
results/tables/final/task0023-cpu-mps-benchmark-summary.json
```

If timing cells exist, curate the corresponding small CSV. Unavailable outcomes must not manufacture zero-valued timing measurements.

Keep protocols/new foundation/helpers/tests tracked intentionally; keep inputs, raw timings, device proof, guards, acceptance, logs and snapshots ignored.

Update README, living memory and index with implemented versus physically validated versus executed states. Preserve accepted CPU v2, old failures, particle192/192/deferral and scientific identities.

Report actual prepared-array reads,1024 unique reused rows only if accessed, population/store-custody requests0 and optimizer updates0. State:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Verify JSON/CSV/report/count/statistic agreement, identities/receipt lineage, links, exclusions and whitespace. Hosted CI remains unverified unless directly established.

A slower MPS result is valid evidence. If unavailable/unsupported, report zero real access/unreserved campaign and one concrete independent next project step from the accepted CPU reference, such as a bounded export/equivalence foundation. Do not propose another automatic MPS-readiness task series.

Do not implement that next task here.

## 11. Informative Italian final response

Follow the standing preference in `docs/development.md`.

Provide a self-contained Italian response, approximately600–1000 words excluding Git, scaled to the actual outcome. Include:

- What was implemented and what was physically validated.
- Actual availability/build/context evidence and any blocker.
- Numerical policy, supported assumptions and strict-decision results.
- Complete/partial coverage, host/device peaks, wall and access counts.
- CPU/MPS comparison table and clearly defined ratios if measurements exist.
- Transfer/synchronization placement, outliers and practical limits.
- Current tests/checks and unverified claims.
- One recommended concrete next task.
- Report/summary/CSV/handoff links and exposure declarations.

For unavailable outcomes, explain the validated software scope and absent device proof/measurements. Do not call simulated tests MPS acceptance or substitute historical CPU numbers for missing paired results.

## 12. Required final Git section — last section of the response

Do not automatically stage, commit or push, and preserve the user’s existing index.

Inspect final actual state before writing commands.

If the index still contains only the staged Task0022 prerequisite, provide a manual sequence that first reviews and commits those existing staged bytes, then selectively stages/reviews/commits Task0023 and pushes the actual branch. Do not stage overlapping Task0023 README/memory/index changes before that first manual commit.

If Task0022 was already committed, provide the ordinary Task0023-only sequence. Do not invent its commit or alter unrelated staged work.

Include exact status/diff/index review, selective `git add --`, staged stat/diff, `git diff --cached --check`, outcome-accurate Conventional Commit messages and verified branch/upstream push.

Include actual task files; exclude operational inputs/arrays, receipts, device proof, acceptances, logs, snapshots, caches and unrelated work.

Proceed with **Task0023 only**.
