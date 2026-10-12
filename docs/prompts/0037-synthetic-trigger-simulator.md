# LatentTrigger — Task0037: Bounded Synthetic Trigger and Queue Simulator

You are continuing **LatentTrigger**. Perform **Task0037 only**.

## Objective and authorization

Implement a small discrete-event simulator that shows how arrivals, batching, bounded buffering and processing cost affect latency, throughput and event loss. Use entirely synthetic event streams and accepted historical CPU aggregate timing as a clearly labeled service-time reference.

The user explicitly chose **a trigger simulator with synthetic workloads** after Task0036's `unresolved_no_acquisition` decision. This authorizes additive simulator implementation, synthetic validation, a bounded fixed scenario sweep, aggregate plots/reporting and the usual handoff. Complete that work without another general confirmation.

It authorizes zero real event acquisition, operational population/feature/score/fingerprint loads, operational model instantiation/forwards, reconstruction, fitting, calibration or scientific re-evaluation. The simulator itself must not instantiate or execute models. Existing historical model tests may use their synthetic fixtures in artifact-free regression suites; distinguish that test work from the new simulator and from zero operational work. Simulation outputs are systems what-if results, not independent signal confirmation, new inference benchmarks or measured LHC trigger rates. Do not start Task0038 automatically.

## 1. Verify and preserve the project

Read applicable instructions, `docs/development.md`, memory, Task0036's report/summary/handoff, Task0035's accepted synthetic foundation and relevant Task0022/0032 CPU-cost scope/provenance. Inspect actual Git state.

Planning inspection on2026-10-12 Europe/Rome found:

- `main` tracking `origin/main`, HEAD `34d74010aa58b6cd11883d14cdca03643ddc4898`, committed Task0035.
- Task0036 completed but uncommitted: eight intentional paths, empty index, memory1.31.
- Task0036 route `unresolved_no_acquisition`; no confirmation source accepted.
- No existing trigger/queue simulator found in the reviewed source/config tree.

Recheck these facts; commits may have changed. Preserve initial Task0036/unrelated bytes, accounting separately for intended new updates to README/memory/index. Do not require a prior commit, stage earlier work, recreate old acceptance or modify historical task-time records.

Save actual prompt/initial handoff:

- `docs/prompts/0037-synthetic-trigger-simulator.md`
- `docs/handoffs/0037-synthetic-trigger-simulator.md`

Keep the current confirmation route unresolved and unauthorized; do not retire/amend it or conduct another publisher search. Task0032 remains complete, Task0033 exploratory, evaluated samples permanently exposed, Task0025 failed, particle192/192 consumed/canonical-deferred. This engineering task can advance independently of the missing confirmation source.

## 2. Keep the simulator small and explicit

Use a dedicated namespace such as `src/latenttrigger/simulation/`, a strict config `configs/simulation/synthetic_trigger_v1.json`, and a simple reproducible command-line entrypoint. Separate pure event scheduling/statistics, curated timing-input validation, and aggregate reporting. No web app, scheduler framework, device backend, generator, queueing library or dependency installation is needed.

Implement one FIFO, nonpreemptive server. Source events arrive at synthetic integer-nanosecond timestamps. Every admitted event must be processed before its toy score is selected/rejected; selection must not reduce the processing queue in advance.

Buffer capacity counts actual admitted events waiting **plus actual events in service**. Padding slots do not consume event capacity. Overflow uses deterministic drop-tail admission. Dropped events never enter processing/selection. Do not add deadline-based dropping, priority scheduling, parallel servers or adaptive thresholds to this first version.

Support a maximum batch size B and a flush timeout measured from the oldest waiting event's original arrival. If idle and at least B events wait, dispatch immediately. Otherwise dispatch when that oldest timeout expires; if already expired when the server becomes idle, dispatch immediately. A final partial batch obeys the same rule. B1 dispatches immediately.

Use a fixed-shape **modeled padded-batch** service rule: a partial batch with m≤B actual events incurs the configured cost for B slots. Record m/B utilization and unused slots. No padding tensor/model execution occurs. This is an explicit scheduling/cost assumption, not measured partial-batch performance or a validated deployment implementation.

All actual events in a batch complete at its service-finish timestamp. At ties, process completion before arrivals, arrivals in source order, then eligible dispatch/flush; state this ordering and test it. Timers must never dispatch an empty batch. Use stable event identity/tie keys and checked nonnegative finite integer time; avoid float-time drift and zero-time event loops.

## 3. Use only accepted curated CPU timing

Numerical access is restricted to these small curated timing tables/metadata, not any score/model/event array or raw timing trace:

| Source | SHA256 observed in planning |
| --- | --- |
| `results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv` | `ddd4d1ed21d11f28999687c757638238bb548e156061525a0c4ded368ed9d75b` |
| `results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json` | `33c09221548ef56ef1b96f10c951161b65bea8d9565f2f3c100fd5f7a7c5744e` |
| `results/tables/final/task0032-quality-cost.csv` | `64883a3668c82edbe34b38fd125326196f579a9f3b58db89e12ce791ed10720d` |

Verify exact bytes, nonsymlink paths, accepted Task0022 status/lineage, unique candidate/batch/scope/worker coverage and cross-table agreement. Reject absent/altered inputs; do not rerun CPU benchmarking. Do not follow paths embedded in receipts/metadata to reopen operational artifacts.

Use only `adapter_decision` scope for `pca-v1` and `compact-autoencoder-v2` at B1/8/32/128/1024. Validate actual candidate identifiers rather than assuming their spelling. The historical adapter already includes input wrapping/validation, forward, FP64 SSE and four decisions; do not add overlapping reconstruction or score-decision timings.

Main scenarios use each candidate/batch's count-weighted pooled mean over all three200-invocation workers. Preserve all repetitions and outliers; never choose the fastest worker or replace the mean with a favorable median. Represent each pooled mean as a **constant assumed batch service time**, rounded upward to an integer nanosecond with documented arithmetic. Cross-check against Task0032's cost arithmetic.

This does not reproduce an empirical service-time distribution. Do not sample from invented distributions fitted to p50/p95/p99 or imply that constant mean service preserves queue tails. The limited sensitivity experiment below uses individual-worker mean/p99/max values as separately labeled constant-cost stress assumptions, not measured frequencies.

Historical cost applies to preloaded standardized development features on the recorded shared Mac/runtime. It excludes raw I/O, physical feature construction, transport and queueing. The simulator's modeled delay includes its synthetic queue/batch wait plus this scoped assumed service; it is not whole-detector or end-to-end measured latency. Simulator wall time is also not inference latency.

## 4. Fix synthetic arrivals and toy decisions before the sweep

Generate5000source events per trace, with base seeds41/42/43, separate declared RNG streams for arrival times and toy scores. Record generator algorithm/environment and deterministic input hashes. Reuse each identical arrival/score trace across candidates and batching policies; do not generate a more favorable workload per candidate.

Two arrival modes:

- Periodic arrivals at10000/100000/1000000events per simulated second.
- Poisson-process arrivals at the same nominal rates, using independent exponential gaps rounded upward to≥1ns. Disclose time quantization and report realized N/horizon rather than pretending it equals the nominal rate exactly.

First arrival is after its first gap; horizon H is the final arrival timestamp. Run arrivals through H and then drain every admitted event under the same scheduling policy. Keep metrics before H separate from full-drain metrics; startup/drain transients are included, so no stationary-rate claim follows.

Each source event has one independent synthetic score Uniform[0,1). Apply strict `score > threshold` at toy thresholds0.9/0.95/0.99/0.999 after service completion. These are illustrative synthetic decisions, not historical SSE thresholds or new calibration. Do not compare toy scores to frozen model cutoffs, introduce signal labels, or report physics TPR/AP/AUC/enrichment. The score is reused across policies/candidates; assumed independence from service cost is an explicit limitation.

## 5. Execute only the prescribed finite matrix

Main matrix:

- Two historical candidate-cost profiles.
- Nine batching policies: B1/timeout0; B8/32/128/1024 each with timeout100µs and1000µs.
- Three nominal rates, two arrival modes and three trace seeds.
- Capacity1024actual events and illustrative per-event latency deadline1000µs.
-5000arrivals per scenario.

Expected coverage: **324main scenarios**, using18unique generated traces/90000unique synthetic source events, replayed as1620000scenario event presentations. Those are synthetic counts, not dataset accesses. All scenarios and outcomes must be retained; no policy winner or deployment target is selected.

Add one fixed sensitivity slice only: nominal100000/s, Poisson arrivals, B128/timeout100µs, capacity1024/deadline1000µs, all three seeds and both candidates. For each of the three historical workers, use that worker's mean, p99 and maximum adapter cost as three separate constant-service assumptions. This adds **54scenarios/270000presentations**, reusing existing traces;378scenarios/1890000presentations total.

Explicitly retain the AE2B128 historical26.2485msmaximum where verified in the accepted table. Assuming it for every batch is an intentionally harsh scenario, not an observed recurring stall. Do not infer an outlier's cause or extrapolate a p99 timing statistic to a p99 queue-latency guarantee.

Do not expand seeds/rates/capacity/deadline/service profiles after seeing the output. Synthetic software bugs may be corrected and the fixed matrix rerun with versioned evidence; that is validation, not an operational scientific allowance. Preserve failed/partial run receipts and report actual invocations.

## 6. Report accounting and latency precisely

For every scenario report generated/admitted/overflow-dropped/completed/pending counts; four selected/rejected toy counts; full/partial batch counts and actual batch-size/slot-utilization summaries; maximum outstanding/waiting queue; server busy time/utilization; horizon/drain duration and throughput with explicit denominators.

Account for queue occupancy at H before draining, including any actual events in service. After complete drain, generated=overflow-dropped+completed and admitted=completed. Selected+rejected=completed separately at each toy threshold; threshold counts are nested. Missing events, double completion or unexplained pending work invalidate the result.

For completed admitted events report count, mean, minimum, p50/p95/p99 and maximum of dispatch waiting and total modeled latency. Service duration is the configured batch duration. Every dropped event is excluded from latency statistics but its count/rate must be shown beside them; low survivor latency does not imply low loss. Use fixed linear quantiles with integer-time provenance and clear ns/µs/ms conversions.

If separating busy-server queue wait from idle batching wait, define an exact decomposition and test its sum. Otherwise report combined dispatch wait and label it honestly; do not fabricate a split. Deadline misses use strict total latency>1000µs, so equality meets the illustrative deadline. State denominators for processed misses, selected-event misses and overflow loss; dropped events are not successful on-time decisions.

No confidence intervals, hypothesis tests or significance are needed for these finite fixed workloads. Report seed variability directly; do not treat a deterministic mean-cost model as validated stochastic latency or steady-state capacity.

## 7. Validate semantics before bounded execution

Use small hand-computable fixtures and a simple independent reference/oracle where useful. Cover:

- B1periodic service with no queue and exact service latency.
- Known overloaded FIFO timelines, capacity including in-service events and drop-tail counts.
- Completion/arrival/flush ties, oldest timeout after server-busy periods and final partial batches.
- Modeled padded costs, unused slots, no empty dispatch or zero-time loop.
- Horizon versus drain accounting, latency deadline equality and exclusion of dropped-event latency.
- Strict toy-score ties/nesting and decisions after processing only.
- Replay reproducibility/common traces, RNG-stream separation and nanosecond rounding.
- Missing/altered/symlink/unaccepted timing inputs, ambiguous coverage, preserved worker outliers and no overlap of timing scopes.
- Aggregate-report boundary, malformed config/counts/times, incomplete output and resource/deadline failures.

Run relevant targeted/full/portable synthetic suites in artifact-free source copies using the existing approach, plus lint/format/dependency checks. No operational model/sample access or new simulator model-fitting path is permitted; reused historical synthetic model-test activity is a separate scope. A fresh source/dependency/config acceptance must cover new simulator code; Task0035's1917tests do not automatically cover it. Do not claim hosted CI or a real detector/hardware test.

## 8. Bounded synthetic sweep and aggregate reporting

Keep ordinary validation distinct from the fixed sweep. Reuse inspected continuous-clock, scoped assertion and process-accounting utilities through minimal adapters; do not modify historical controllers or build a generic execution platform.

Suggested operational namespace: `results/simulation/task0037-synthetic-trigger/`, ignored. Load each allowed curated timing source once for the sweep, generate each unique synthetic trace once, reuse in memory, and let plotting consume owned aggregates only. Never copy processed stores or write per-event traces/scores as curated outputs. Small owned test fixtures are permitted.

Fixed invocation limits:30s prerequisites;120s simulation worker dispatch through normal exit/reaping;60s aggregate reporting worker;15s parent finalization;240s whole invocation. Cleanup2s is inside each worker cap. Worker RSS1GiB, whole-native reservation512MiB, controller128MiB; guard journal64MiB/worker, log1MiB/worker, owned storage128MiB. Bound synthetic in-memory buffers explicitly.

Actual wall-clock supervision is independent of simulated event time. Continuous deadlines include host suspension; virtual service/arrival timestamps never serve as runtime accounting. Verify the temporary owned idle-sleep assertion before/during workers and verify release/reaping; permit display sleep and change no persistent settings. WARN advisory, CRITICAL/invalid-primary veto, unavailable pressure disclosed, global RAM contextual. No idle-Mac requirement or monitoring-optimization task.

Accept the final synthetic sweep only after normal exit/reaping, complete matrix/conservation checks, source/output identities, deadlines/resources and assertion release. Body-complete alone is insufficient. Disclose gaps/overshoot and any actual failed attempts. Ordinary synthetic repair/revalidation is authorized; never overwrite old receipts or label simulated execution as a real inference campaign.

## 9. Deliver usable artifacts and the next engineering decision

Produce:

- `docs/synthetic-trigger-simulator.md`
- Task0037 prompt/handoff and fixed simulation configuration.
- Separate simulator/curated-input/reporting helpers, tests and validation/run entrypoint.
- `results/tables/final/task0037-synthetic-trigger-scenarios.csv`
- `results/tables/final/task0037-synthetic-trigger-summary.json`
- At most three readable scientific plots of latency/loss/batching or fixed stress sensitivity.

Plot actual fixed-scenario outcomes with candidate-cost, arrival, batch/timeout and units clearly labeled. Show seed variation directly; declare clipping/log scales. Visually inspect every curated figure. Do not imply a continuous optimum between sparse scenarios, infer an empirical service distribution from constants, or conceal dropped events behind good survivor latency.

Update README/index/memory from the verified revision1.31. Explain that the synthetic trigger study is an engineering branch using completed baseline cost context; Task0036's unresolved source and Task0034's unchanged scientific claim remain intact.

The Italian final handoff should explain implemented behavior, coverage/accounting, queue/batching/loss findings, fixed-cost sensitivity, validation/native status/resources/release, and limits. Include actual counters:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
new_operational_population_requests_in_Task0037: 0
new_event_feature_score_membership_fingerprint_loads_in_Task0037: 0
new_simulator_model_instantiations_or_forward_calls: 0
operational_reconstruction_calibration_scientific_evaluations_in_Task0037: 0
operational_optimizer_updates_in_Task0037: 0
event_payload_downloads_in_Task0037: 0
new_operational_physical_inference_timing_measurements_in_Task0037: 0
curated_timing_table_metadata_loads: ACTUAL_COUNT
synthetic_unique_traces_events_generated: ACTUAL_COUNTS
synthetic_scenarios_event_presentations: ACTUAL_COUNTS
simulation_invocations_final_status: ACTUAL_COUNTS_AND_STATUS
```

YES preserves historical exposure. Curated numerical timing reads and synthetic scores/events are actual new numerical work; do not claim globally zero numerical access. Disclose reused historical synthetic model-test work separately instead of claiming all regression suites have globally zero forwards/updates.

Conclude with a concrete follow-up for validating service-time variability or measuring the missing chain costs on separately authorized development workloads. Do not acquire a confirmation source, rescore exposed tests, choose a deployment policy or launch that follow-up automatically.

Finish with actual Git review, selective staging, staged review, Conventional Commit and push commands for the verified branch/upstream. Do not stage, commit or push. If Task0036 remains uncommitted, keep its paths distinct and preserve its bytes except disclosed living-document updates; do not sweep prior/unrelated work into Task0037 staging commands.

Proceed with **Task0037 only**.
