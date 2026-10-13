# LatentTrigger — Task0038: Prepared-Batch Service Variability and Padding Measurement

You are continuing **LatentTrigger**. Perform **Task0038 only**.

## Objective and authorization

Replace one major Task0037 assumption with bounded engineering evidence: measure the service cost and observed variability of natural-size versus padded batches for the two frozen native CPU baselines, using the same existing1024prepared development-training inputs.

This prompt explicitly authorizes additive implementation, synthetic validation, and **one conditional native development-only measurement session** after successful final-source acceptance and plan freezing. The session may load the specified prepared array in three fresh repetition workers, instantiate the two accepted frozen models, perform numerical/decision checks, and execute the fixed timing matrix. Record this actual prompt as prospective authorization; no further general confirmation is required.

It authorizes zero raw/processed-store construction, new population requests, test/signal/selection/calibration population access, fitting/optimizer updates, threshold recalibration, downloads, scientific metrics or confirmation. Task0034's six new fits are not part of this study. Task0036 remains `unresolved_no_acquisition`. Do not launch Task0039 or rerun Task0037 automatically.

## 1. Inspect and preserve the current baseline

Read applicable instructions, `docs/development.md`, memory, Task0037's report/config/summary/handoff, Task0022's protocol/derivation/numerical helpers/thread enforcement, and relevant Task0020/0021 preparation lineage.

Planning inspection on2026-10-12 Europe/Rome found clean `main` tracking `origin/main`, empty index, HEAD `84252b62f14c6cca442d76d0d4421365b1eb0b2d` (committed Task0037), preceded by committed Task00362427373 and Task003534d7401, memory1.32. Recheck actual state and preserve unrelated edits.

Save actual prompt/initial handoff before substantive work:

- `docs/prompts/0038-prepared-batch-service-measurement.md`
- `docs/handoffs/0038-prepared-batch-service-measurement.md`

Preserve historical source/configs/models/thresholds, accepted and failed receipts, Task0037's fixed scenarios/figures and Task0034's scientific gates. New measurements are a distinct current-host study; no retrospective replacement of Task0022 or explanation of its AE2stall. Task0025 remains failed; particle192/192 consumed/canonical-deferred; all evaluated samples permanently exposed.

## 2. Pin a narrow numerical input boundary

Use only the existing file:

`results/benchmarks/task0020-frozen-cpu/prepare/input.npy`

- Shape1024×8, little-endian C-contiguous FP32.
- Size32896bytes.
- File SHA256 `7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`.
- C-order payload SHA256 `2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05`.

These are already-standardized, source-ordered first1024development-training aggregate rows. Establish that role/order from accepted preparation lineage; length alone is insufficient. Planning byte custody verified the file exists, is nonsymlinked and matches its recorded hash, without a numerical array load.

Each of three repetition workers loads this original array once and reuses it for both candidates/all cases. Planned total:3prepared-array loads/3072loaded rows,1024unique reused development rows. No campaign copy or store reader is needed. Hash/header custody, numerical loads and repeated in-memory presentations are separate counters.

Use exactly the two original frozen native models and their original four thresholds, pinned through Task0022's registry:

- PCA-six `data/baselines/pca-v1/model.json`, file SHA256 `6dd54d8aa788ab27f3cbd674d82c549ce31787b9865a911635d9ebd8faee3190`.
- AE-v2 `artifacts/models/compact-autoencoder-v2/model.json`, file SHA256 `a0b1563c34526bbfd965de6b63d041da2dfa713e9fe4bbc514852595ea813bf5`.

Verify recorded scientific/configuration/calibration identities separately from file hashes. Load each model once per repetition; zero parameter mutation or new model export. Reject missing/altered/symlink/ambiguous inputs; do not regenerate them. Do not load stored scores, memberships, fingerprints, particles, physical features, labels or source IDs.

Synthetic validation must use synthetic arrays/models only. Before reservation, operational checks are bounded metadata/header/byte custody; do not numerically load this prepared array or use operational model tensors in tests.

## 3. Define one new service boundary

Create a separate strict protocol, such as `configs/benchmarks/prepared_batch_service_v1.json`, and small additive helpers. Preserve historical validators and consumed campaign routes.

Measure **`prepared_batch_service`** from an existing preloaded FP32 feature-window view through owned input construction, the canonical public score adapter, four original strict decisions and retention of the m actual rows.

Two strategies:

- `natural`: allocate an owned contiguous m×8FP32 batch and copy the m actual rows.
- `padded`: allocate an owned B×8FP32 batch, copy the m actual rows, and fill only trailing B−m rows with exact FP32zero. Score/decide all B rows; return only the first m. Padding is synthetic zero in standardized coordinates, not a physical empty event.

At m=B both strategies use the same no-padding construction semantics. Synthetic padding rows must never count as source events, accepted events or useful throughput. No queue-dependent feature construction, raw I/O, transport, device transfer, scientific calibration or actual event selection is measured.

The public models, operation order, dtypes, FP64-before-subtraction SSE and strict original cutoffs remain unchanged. CPU eager only, original effective single-thread policy, no AMP/compile/quantization/export/device change. Set thread environment before numerical imports and verify actual PyTorch/BLAS/Accelerate controls; environment variables alone are insufficient.

This boundary includes packing and real-row result retention, unlike the historical preloaded adapter timer. Report the distinction; do not advertise a direct Task0022speedup or add overlapping scope medians into an end-to-end latency. Input/model loading, proof instrumentation, hashing, logging, guard queries and reporting are outside timer pairs; normal background monitoring remains active and its possible interference is disclosed.

## 4. Fix the paired timing matrix

Use target B in1/8/32/128/1024. For B1 use m1; for each larger B use m in1/2/B−1/B. This gives17(B,m)cases per candidate/strategy.

For each m, use up to three deduplicated contiguous source windows starting at0, floor((1024−m)/2), and1024−m. Cycle deterministically through them, resetting the schedule per case. Both strategies in a pair receive the identical actual-row window; no random window search or different inputs per candidate.

Three fresh sequential repetition workers, each covering both candidates. Worker1/3: PCA then AE, ascending B/m. Worker2: AE then PCA, descending B/m. Disclose this fixed order; it is not full control of host drift.

Each case uses10warm-up pairs then50timed pairs. Within each phase, alternate natural→padded and padded→natural by pair index. Timed pairs thus have25of each ordering; retain ordering and window identity in the raw timing record. Preserve all slow calls and interruptions; no fastest-run selection, trimming, fitted outlier rule or overhead subtraction.

Expected coverage:

-3repetitions×2candidates×17cases×2strategies = **204timing cells**.
-50observations/cell = **10200timed service invocations**.
-10warm-up observations/cell = **2040warm-up invocations**.
-200empty timer pairs per worker,600total, reported as context and never subtracted.

Use synchronous CPU `perf_counter_ns` intervals with recorded resolution/implementation; independently supervise continuous deadlines. Record chronological invocation order and continuous stage timestamps outside service timer intervals. A suspension/clock discrepancy must not be hidden by removing a slow call or using virtual time. Same-host serial observations are not i.i.d. production service samples.

Keep raw per-call timing sequences in ignored operational artifacts, with candidate/repetition/B/m/strategy/order/window-position metadata and hashes. Do not persist per-event features, scores, masks or labels. These sequences can support a later explicitly defined replay; this task must not fit a service distribution or infer stall frequency from50observations.

## 5. Validate real-row numerical invariance before and after timing

Mathematical row independence is not bitwise cross-shape assurance; see [PyTorch's numerical-accuracy documentation](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html). Verify the fixed new shapes/padding paths synthetically before operational access.

Retain Task0022's accepted arithmetic-aware AE policy, local/band/finite assumptions, outward primitives, unchanged public SSE and exact same-shape repetitions. Retain PCA's original tolerances. Inspect whether the derivation applies unchanged to each new shape and zero padding; add separate adapters/tests, not a larger empirical tolerance or a mutation of the historical proof.

For each distinct timed window/case, pre/post checks must establish:

- Correct actual-row preservation and dummy-row exclusion.
- Finite reconstruction/SSE for actual and padding rows, unchanged inputs/parameters/thresholds.
- Same-shape separated/public score consistency and repeatability.
- Natural and padded first-m outputs within the accepted cross-shape numerical contract against the corresponding canonical1024-row reference.
- **Zero actual-row decision mismatches** at all four original thresholds.
- Byte-identical canonical full-reference hashes before/after timing.

Use appropriate diagnostic accounting for FP64/local-layer proof work; remove hooks before warm-up/timing. Do not require AE cross-shape bitwise equality where the unchanged contract uses operation-level bounds. Do not weaken gates because padding introduces a different native kernel.

If the policy cannot be justified on synthetic fixtures, finish before reservation with the specific blocker. If an operational gate fails, preserve raw/partial evidence and reject the one session; no diagnostic replay, inversion, threshold adjustment, source repair or second real attempt inside Task0038.

No score marginal, feature association, AUC/AP, significance, signal efficiency or useful-candidate selection is authorized. Numerical threshold checks assess pipeline invariance on development rows only.

## 6. Validate and freeze before the single actual session

Test strict configuration/input/role boundaries, source/header/identity rejection, matching windows, padding construction/m=B equality, dummy-mask exclusion, score casting and strict ties, output/parameter mutation, unsupported arithmetic assumptions, complete paired schedule and all timing observations.

Cover exact counts, real-versus-padding row accounting, source loads once per worker, raw-sequence preservation, aggregate-only reporting, incomplete/pre/post/lifecycle rejection, atomic one-winner reservation, simulated suspension, assertion loss/release and resource/deadline failures.

Run targeted tests, full/portable suites in artifact-free source copies, lint/format/dependencies, and bounded native synthetic integration exercising both strategies/new shapes and guard/thread/gate paths. Historical synthetic regressions may instantiate/update fixture models; report that scope separately. No dependency installation or operational numerical trial during validation.

Bind a fresh final source/config/test/dependency/build map, synthetic acceptance, unchanged input/model/threshold/proof identities, exact matrix and this actual prompt. Old2022test acceptance does not cover new code. Freeze the plan before reserving the dedicated Task0038anchor/output; do not call old Task0022's consumed execution route.

## 7. Execute within fixed bounds

Suggested namespace `results/benchmarks/task0038-prepared-batch-service/`, with one durable canonical attempt anchor. Before reservation verify source/plan/acceptance/input byte identities, exact native runtime/thread support and resource prerequisites without operational numerical access. No repeated readiness polling or idle-Mac requirement.

Fixed limits:

| Scope | Ceiling |
| --- | ---: |
| Prerequisites before reservation |60s |
| Each of three repetition workers, dispatch through normal exit/reaping |120s |
| Aggregate reporting worker |60s |
| Parent finalization |15s |
| Reserved session |480s |
| Whole invocation including prerequisites |540s |
| Cleanup inside each worker cap |2s |
| Worker RSS |1GiB |
| Whole native reservation |512MiB |
| Controller RSS |128MiB |
| Guard journal per worker |16MiB |
| Text log per worker |1MiB |
| Total owned output storage |128MiB |

Verify temporary owned idle-system-sleep assertion before reservation/during workers, permit display sleep, confirm release/reaping on every exit and change no persistent power settings. Continuous deadlines include suspension. WARN advisory; CRITICAL/invalid-primary-accounting veto; unavailable pressure and monitoring gaps disclosed; global available RAM is context only.

Each worker verifies its own grant, source/dependency/input identities and effective threads, durably records its prepared-array/model loads before access, and tracks completed/inflight calls and actual/padding/proof row presentations. Reporting consumes owned aggregate tables/receipts only, never feature/model/score inputs or raw arrays requiring scientific access.

Accept only normal exit/reaping, all204cells/10200timings/2040warm-ups, successful pre/post gates, source/output identities, caps/deadlines and verified assertion release. Body-complete followed by blocked shutdown remains failed, as learned from Task0025. Retain raw outliers, terminal accounting gaps and actual overshoot.

One reserved operational engineering session only. Failure consumes it even with zero timing cells. Stop without retry/reset or implementation changes after reservation. Synthetic software iteration before freezing is permitted and separately counted.

## 8. Report measured scope and remaining chain gaps

Produce:

- `docs/prepared-batch-service-measurement.md`
- Task0038 prompt/handoff and strict benchmark config.
- Additive service/validation/worker/reporting helpers and synthetic tests.
- `results/tables/final/task0038-prepared-batch-service-cells.csv`
- `results/tables/final/task0038-prepared-batch-service-summary.json`
- At most three readable inspected figures for partial-batch cost, paired strategy differences and chronological variability.

For every cell retain count/min/max/mean/population std/p50/p95/p99 with fixed linear quantiles, actual useful m/mean throughput, executed shape, padding rows/slot utilization, repetition/order and timer context. Label whole-batch latency versus amortized actual-event cost. Keep worker-specific results and all raw observations; if combining repetitions use pooled observations/count-weighted means, not averaged percentiles. With50calls per cell, disclose limited tail resolution and dependence rather than making a production-p99 claim.

Report paired natural-minus-padded differences descriptively, all repetitions and unfavorable observations. Distinguish current-host measured service from Task0037's constant assumptions and historical Task0022 scope. Do not select a deployment batch/timeout, claim source generalization or change the simulator automatically.

Include a short chain-gap table: prepared-row packing is measured here; raw HDF I/O/decompression, full-particle feature construction, external transport, actual streaming/queue scheduling and device-specific paths remain unmeasured. Identify the smallest later development-only measurement and its source/membership/access/clock boundaries. No raw row identifiers or missing stage costs are manufactured. A sum of scope medians is not measured whole-chain latency.

Update README/index/memory from revision1.32. Preserve all accepted Task0037 artifacts and the unchanged unresolved scientific route. Detailed timings, parameter/score scratch, logs, ledgers, receipts, plans and acceptance maps remain ignored; curate only intentionally small summaries/tables/figures/source/docs.

The Italian final handoff should explain actual numerical outcome, natural/padded findings, variability, counts, validation, continuous resource/lifecycle evidence and a concrete next step. Include:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
new_population_requests_in_Task0038: 0
raw_or_processed_store_constructions_in_Task0038: 0
new_test_signal_selection_calibration_population_accesses: 0
new_development_prepared_array_loads: ACTUAL_COUNT
prepared_rows_loaded_unique_reused_rows: ACTUAL_COUNTS
frozen_engineering_model_instantiations: ACTUAL_COUNT
canonical_engineering_adapter_forward_calls: ACTUAL_COUNTS
actual_development_padding_and_proof_row_presentations: ACTUAL_COUNTS
timing_cells_timed_warmup_invocations: ACTUAL_COUNTS
stored_scientific_score_or_fingerprint_array_loads: 0
optimizer_updates_in_operational_Task0038: 0
new_threshold_calibrations_AUC_AP_or_significance: 0
downloads: 0
operational_measurement_session: ACTUAL_STATUS
```

Do not claim zero numerical/model access: this prompt authorizes new engineering inference and prepared-development reads. Historical exposureYES does not imply new test access. Synthetic regressions/validation are separate from the single operational session.

Finish with actual Git review, selective staging, staged review, Conventional Commit and push commands for the verified branch/upstream. Do not stage, commit or push. Do not launch Task0039.

Proceed with **Task0038 only**.


