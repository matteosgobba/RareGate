# LatentTrigger — Task0044: Deterministic Joint-Service Queue Replay

You are continuing **LatentTrigger**. Perform **Task0044 only**.

## Objective and authorization

Implement and run a bounded, deterministic FIFO queue study using the **accepted Task0043 raw-to-decision service sequences**, with prospectively fixed synthetic arrivals. Compare cyclic measured-sequence assignments with a constant-mean control derived from the same samples, and examine a small fixed ordering sensitivity.

This actual prompt authorizes software development, generated-fixture validation, narrow reads of existing accepted timing/provenance artifacts, and the final bounded **synthetic replay sweep** below after fresh acceptance/freezing. It authorizes no new event/model work or physical service measurement. Do not rerun Task0043 or any consumed campaign.

No raw HDF/NPY/processed-store access, membership/golden/features/scientific scores/fingerprints, model loading/instantiation/forward/reconstruction, training/calibration/evaluation, new source acquisition, downloads, device/transport workload, policy selection or Task0045. Historical synthetic regression model/optimizer tests are separate permitted fixture work.

The result is a deterministic systems experiment driven by finite historical service samples. It is not an empirical production service distribution, a physical streaming benchmark, an independent scientific confirmation or a deployment recommendation.

## 1. Verify and preserve the completed baseline

Read applicable instructions, `docs/development.md`, living memory, Task0043 actual prompt/config/report/summary/handoff/provenance and accepted worker output schema; read Task0037 simulator, trace generator, protocol and conservation tests. Inspect the repaired producer/admission/freezing lessons from Task0042 without converting its synthetic permit to another task's authority.

Planning inspection on 2026-10-13 Europe/Rome found clean `main` aligned with `origin/main`, HEAD `d4b92e55e3f8e32eefd5186c303c1d15205bc090`, committed Task0043 and empty index; memory 1.38. Recheck actual Git and preserve unrelated work. Task0043's `6d5fb446...` and older task-time bases remain historical.

Save actual prompt/initial handoff before substantive work:

- `docs/prompts/0044-deterministic-joint-service-replay.md`
- `docs/handoffs/0044-deterministic-joint-service-replay.md`

Task0043 is accepted/consumed; Task0041 remains failed/consumed, Task0042 software-only. Preserve their original source/config/records/flags/markers/results and Task0037's constant-cost simulator. Task0036 remains `unresolved_no_acquisition`; scientific gates, permanent exposure, prior failures and deferred particle model are unchanged.

Use additive replay helpers and a strict new config such as `configs/simulation/joint_service_replay_v1.json`. Do not mutate historical engine/protocol assumptions or weaken their source/namespace checks.

## 2. Load only the accepted service/provenance bundle

The fixed source directory is:

`results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/`

Required curated identities:

| File | SHA256 |
| --- | --- |
| `results/tables/final/task0043-development-raw-decision-summary.json` | `3baa1cc3c04d4b830912a7d7d06d535f23fe85952ed61ee4b63070e973d9a01b` |
| `results/tables/final/task0043-development-raw-decision-cells.csv` | `467583e24cb3f07303208c5e08a7f609da9a0494607bf4b67019e7547756436e` |

Bind the original config/prompt and fixed directory's execution plan, workflow, parent acceptance, and three repetition receipts/aggregates/timers/JSONL files. Take their exact byte pins from the accepted curated provenance and receipt output maps; freeze the complete allowlist before replay. Workflow SHA256 is `2259f76f4f7bd27dab3a2bf803bc4b0bf354e05d42ef69129dab6832b25694f9`; parent acceptance SHA256 is `96b5becdfb04c92fb4fb79b59a9e6cd671aa5fedb2b04e81e8a787665c746c97`.

| Relative JSONL within the fixed directory | SHA256 |
| --- | --- |
| `repetition1/timings.jsonl` | `59591523c9938015539ee90177ed438b041628bfa4c55e93e4141fd81f670cdc` |
| `repetition2/timings.jsonl` | `280134c291899aebbcb50eec91c712984e9498ca964ff8a96a1224d9f6be3957` |
| `repetition3/timings.jsonl` | `025204e86852d61083fefbbf97177d536cbea36beaf496680194ec4a4e4863c4` |

Reject missing/altered/symlink/ambiguous/foreign/oversized sources. Verify Task0043 identity/scope, accepted parent status, workflow/plan/receipt relationships, all numerical worker normal exits/reaping/deadlines, exact parity and receipt output hashes. Historical source maps are checked only against originally bound entries; do not require an old map to include new replay files or rerun an old controller.

Do not follow raw/model/array paths contained in metadata. Read only declared timing/provenance JSON/JSONL/CSV/config/prompt files, bounded to 8 MiB total source bytes. No source numerical library or model import is needed. If original sequences are unavailable, stop: no reconstruction from rounded summary means, substituted worker, omitted outlier or fallback to Task0037 adapter costs.

Each repetition JSONL has 184 records: 160 timed and 24 warm-up. Verify the full ordered schema/schedule, unique ordinals, candidate/B/phase/call and logical window cycling. Select **only** its timed records, preserving within-cell call order 0…19. Derive 24 vectors keyed by candidate, B and repetition, each with 20 strictly positive integer-ns `elapsed_ns` values: 480 values total. Warm-ups are excluded prospectively, not because of their cost; gates/references are never added to the service vectors.

Use `elapsed_ns` as service duration. Continuous timestamp differences and intercall gaps include other instrumentation and must not become service samples or synthetic arrival times.

Check vectors against accepted aggregate observations and curated cell coverage/count/statistics using declared mechanical float-serialization rules. Duration identity/order is exact; no empirical error multiplier. Record all metadata reads, JSONL records parsed/selected and any duplicate numerical timing-statistic copies parsed from aggregates separately. Model scientific hashes/runtime/cache/window/timer context remain historical provenance only.

## 3. Define deterministic service assignment without fitting

For each source vector `q[0…19]`, reset a scenario-local dispatch counter j = 0. Advance it **only when a batch actually dispatches**, once per batch, including partial flush/final-drain batches. Arrivals, overflow, idle waits and individual completions do not consume samples.

- Main cyclic replay: service duration `q[j % 20]`.
- Matched constant control: `ceil(sum(q)/20)` ns, calculated with integer arithmetic.
- Order sensitivity: reversed `q[19 − (j % 20)]` and rotated `q[(j + 10) % 20]`.

Keep all three worker vectors separate; never pool/concatenate workers or interpolate between B values. No random bootstrap/shuffle, fitted distribution, extreme-value replacement or service conditioning on arrivals/scores/backlog. The ordering variants preserve the exact multiset; their finite assigned prefixes need not have the same average when dispatch counts differ.

Record vector fingerprint, original-sample assignment counts, actual dispatch count, complete cycles/remainder, assigned duration sum/min/max and final cursor. Verify assigned sum from original samples/counts. Constant rounding is at most one ns per batch above its exact source mean; do not subtract it. Cyclic reuse creates artificial 20-batch periodicity and a wrap discontinuity, not new measured observations or a stationary production process.

All source costs are **full natural B-row services**. For m < B, charge the same selected B duration as an explicit hypothetical full-B service bill. This does not execute padding, measure natural-m cost or establish an upper bound for all physical partial services. Report partial batch count, useful m, charged B slots, unused slots/utilization and partial-service busy time prominently. Do not call these measured padded costs or reuse the full trace of another B as a partial-cost estimate.

## 4. Extend queue accounting while preserving Task0037 semantics

Use an additive variable-service engine. Reuse unchanged trace/policy/statistic helpers where suitable, but do not pass changing durations through a supposedly constant historical policy or disable its conservation checks.

Keep one nonpreemptive FIFO server; drop-tail admission counts waiting plus in-service actual events; capacity 1024. At a shared timestamp: completion → arrivals in source order → dispatch/flush. Flush deadline is oldest waiting event's original arrival plus timeout; final drain uses the same policy. All admitted events must complete, with pending zero after drain.

Capture the assigned duration in the active batch; each completion latency equals dispatch wait plus **that batch's duration**. Busy time is the sum of assigned durations, with horizon-clipped intervals separately accumulated. It is no longer `constant_service × batches`. Validate generated = overflow + completed, admitted = completed, full/partial/slot counts, outstanding capacity, horizon pending/drain and positive bounded integer virtual times.

Retain Task0037's independent Uniform[0,1) toy-score branch and strict toy cuts 0.9/0.95/0.99/0.999 after completion for conservation compatibility. These are synthetic bookkeeping, not Task0043's original scientific thresholds or masks. Load no real score/mask and make no classifier-efficiency claim.

Scenario outputs include overflow, completion/horizon/drain counts, wait/latency linear quantiles, batch sizes, full/partial utilization, assigned/busy service, illustrative deadline misses and `(overflow + late completed)/generated`. Latency quantiles describe survivors; always show overflow/completed denominators beside them. No invented decomposition of combined dispatch wait into independently measured queue and batching costs.

## 5. Freeze the synthetic arrival and scenario matrix

Use unchanged `simulation.traces.generate`: PCG64/SeedSequence keys `[3700, seed, mode_id, rate, stream_id]`, separate arrival/toy-score streams, periodic ceil gaps or exponential gaps ceiled to at least 1 ns, first arrival after the first gap. Preserve the inherited stream-key domain rather than changing historical code.

Generate once and reuse exact immutable traces: 5000 events each; seeds 41/42/43; periodic and Poisson modes; rates **500, 2500, 5000 input events/s**. Thus 18 traces and 90,000 unique synthetic events. Hash timestamps/toy scores and record actual horizons/realized rates. All comparisons receive the same trace bytes.

Policies: `(B=1, timeout=0)` and B = 8/32/128 each with timeout **1 ms or 10 ms**: seven policies. Capacity 1024 and illustrative latency deadline **100 ms**, strict lateness `latency > deadline`. This engineering comparison deadline is neither a CERN requirement nor an amendment of Task0037's separate 1 ms illustration.

These rates and deadline are chosen with Task0043's costs already known. Freezing them before replay makes the systems experiment reproducible; it does not make it independent scientific confirmation.

Main matrix: 18 arrivals × two candidates × seven policies × three service repetitions × {cyclic, matched constant} = **1512 scenarios**.

Ordering sensitivity: only the existing Poisson/2500-events/s traces, all three arrival seeds, both candidates/seven policies/three service repetitions, × {reverse, rotation10} = **252 additional scenarios**. Compare each with its corresponding main cyclic scenario; do not duplicate the baseline simulation.

Final totals: **1764 scenarios, 8,820,000 event presentations**, 756 cyclic-minus-constant contrasts and 252 order-minus-cyclic contrasts. Pure planning must derive/test unique keys, pairing, counts and shared trace/vector identities. No adaptive grid, B1024, capacity search, extra rates/seeds/offsets or timing-driven policy selection.

Contrasts retain integer count differences and declared fraction/latency differences, completed denominators and actual assigned-service means. They are deterministic outcomes conditional on these inputs, not statistical significance, confidence intervals or causal production-model comparisons.

## 6. Fresh validation, admission and bounded execution

Test the strict accepted-source loader using generated provenance/receipt/timing bundles: wrong status/task/scope/hash/order/phase/count, duplicate/missing cells, warm-up contamination, float/zero durations, unsafe paths and forbidden source dereferencing. Tests must not numerically load the real Task0043 bundle during software validation.

Test exact cursor/reset/cycle/reverse/rotation behavior, mean ceiling, partial billing, multiple completions sharing a batch cost, tie order, oldest-arrival timeout, overflow with in-service capacity, final drain, horizon clipping, virtual-time overflow and every conservation invariant. Under a constant provider, the new engine must match the unchanged Task0037 engine exactly on representative fixtures, including toy counts. Use independent hand-solvable variable-cost fixtures, not only implementation-shaped tests.

Run focused/full/portable artifact-free suites, lint/format/dependencies and bounded native synthetic integration of the new producer → serialized acceptance → outer verifier → freeze/claim → replay/report lifecycle. Source fixtures replace Task0043 artifacts in validation. If a bootstrap is necessary, it is generated-fixture-only and cannot bypass final source admission. After final software acceptance/freezing, run the requested sweep on the exact accepted source bundle.

Use a closed Task0044 identity, authoritative matching software status/record schema and separate `data/task0044-validation/` and `results/benchmarks/task0044-joint-service-replay/` namespaces. No Task0041/0042/0043 permission reuse. Freeze actual prompt/config/sources/tests/installed dependencies and exact source pins/matrix before the final sweep. Failed admission/freezing must block dispatch programmatically; controller/report acceptance requires normal exit/reaping and independent source/output checks.

Preserve source/matrix choices and failed evidence. Do not repeat the matrix merely to redraw figures; a reporting-only correction can use owned aggregates with its own declared validation/budget. Any additional replay invocation must be explicitly accounted for, not hidden in final-only counts.

Fixed bounds: prerequisites 30 s; simulation worker 120 s through exit/reaping; reporting 60 s; finalization 15 s; whole 240 s; cleanup 2 s inside caps. Worker RSS 1 GiB/native reserved 512 MiB/controller RSS 128 MiB; journal 64 MiB/log 1 MiB/owned output 128 MiB; source bundle 8 MiB, retained service vectors 1 MiB, retained arrival traces 16 MiB; at most 5000 latency entries per scenario, released between cases. Keep JSON summaries bounded; complete rows belong in CSV rather than an oversized duplicated JSON matrix. These caps do not prove runtime feasibility.

No model imports/network/subprocesses inside numerical replay workers beyond owned supervised controller children. Use existing continuous clock, temporary verified idle-system assertion, pressure/resource guards and cleanup: WARN advisory; CRITICAL/invalid primary veto; display sleep allowed, no persistent settings/global RAM floor. Declare query/terminal gaps, unknown optional context, exact exits/reaping/assertion release and actual storage/peaks. This is virtual-time simulation, never wall-clock arrival sleeping or a new physical benchmark.

## 7. Curated outputs and interpretation

Produce:

- `docs/deterministic-joint-service-replay.md`, actual prompt and detailed handoff.
- Strict config, additive replay helpers, focused tests and validation entrypoint.
- `results/tables/final/task0044-joint-service-replay-scenarios.csv`.
- `results/tables/final/task0044-joint-service-replay-contrasts.csv`.
- `results/tables/final/task0044-joint-service-replay-summary.json`.
- At most three readable inspected figures covering overflow/late outcomes, survivor latency with denominators, and mean-control/order/partial-billing sensitivity.

Retain all workers/seeds/unfavorable cases. Figure ranges must include every displayed observation/contrast; log/symmetric-log axes and any min–max bands are explicit, not confidence intervals. Do not publish a best policy or hide low partial utilization.

Raw replay ledgers, source vectors/sequences, arrivals/toy scores, grants/receipts and any per-event fixture diagnostics remain ignored. Curated outputs are aggregate systems results and source identities. Source samples are finite measured full-B costs from warm sparse HDF windows; synthetic arrivals do not recreate their cache/load/decoder dependence. Replaying them does not physically run HDF/features/models or validate transport/backpressure behavior.

Explain whether mean-only assignment or order changes these fixed queue outcomes, including cases of little difference. Partial billing, cycle alignment, fixed finite workloads/startup/drain and survivor selection limit interpretation. Do not fit a production distribution, extrapolate a CERN throughput/latency requirement or change the original benchmarks/simulator/scientific protocols.

Update README/index/memory from verified 1.38, preserving Task0043 accepted/consumed, Task0041 failed/consumed, Task0042 software-only, Task0036 unresolved, scientific gates/exposure/failures/particle state. The next decision may separately scope measured natural partial raw-to-decision services if this billing assumption matters, or another missing streaming/transport boundary. Do not implement it or launch Task0045 automatically.

## 8. Self-contained Italian handoff and manual Git

Explain actual replay outcome, main and ordering contrasts, partial-cost assumptions, source custody, conservation, fresh validation, continuous resources/lifecycle/release, limitations and next decision. No global-zero test-model claim: historical synthetic regressions have actual fixture model/optimizer activity, separately disclosed.

Include:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
Task0043_status_preserved: parent_accepted_development_raw_decision_measurement
accepted_timing_JSONL_loads_records_timed_selected: ACTUAL_COUNTS
service_vectors_unique_values: ACTUAL_COUNTS
other_provenance_aggregate_timing_reads: ACTUAL_COUNTS
synthetic_trace_generation_requests_unique_events: ACTUAL_COUNTS
replay_scenarios_started_completed_event_presentations: ACTUAL_COUNTS
main_and_order_contrasts: ACTUAL_COUNTS
service_assignments_cycles_partial_batches: ACTUAL_COUNTS
conservation_final_pending: ACTUAL_STATUS
new_event_feature_membership_golden_scientific_score_fingerprint_loads: 0
new_raw_HDF_access_or_byte_hash_passes: 0
new_replay_model_instantiations_forward_reconstruction_calls: 0
new_operational_optimizer_calibration_scientific_evaluations: 0
new_physical_service_timing_measurements: 0
downloads: 0
replay_invocations_status: ACTUAL_COUNTS_AND_STATUS
```

Distinguish all historical-timing numerical reads, generated unique events, repeated presentations and assigned sample reuses. Use `parent_accepted_synthetic_joint_service_replay` only after complete fixed coverage, conservation, output/source identity and normal lifecycle checks; do not call replay a new operational CPU campaign.

Finish with actual Git review, selective staging, staged review, Conventional Commit and push commands for verified branch/upstream. Do not stage, commit or push. Preserve unrelated work and exclude ignored sequences/fixtures/receipts. Do not launch Task0045.

Proceed with **Task0044 only**.
