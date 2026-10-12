# Bounded synthetic trigger and queue simulator — Task0037

## Scope and implementation

This is an engineering what-if study using synthetic arrivals/scores and accepted
historical prepared-feature CPU adapter aggregates as assumed constant service
costs. It does not run models, benchmark inference, measure LHC rates or confirm
signal discrimination. Task0036's `unresolved_no_acquisition`, source acceptance
false and Task0034's scientific protocol remain unchanged. No Task0038 is launched.

The additive [implementation](../src/latenttrigger/simulation/) has separate
integer-time scheduling/statistics, trace generation, three-file curated timing
validation, fixed sweep, aggregate-only figures and minimal guarded lifecycle.
The [strict config](../configs/simulation/synthetic_trigger_v1.json) fixes every
scenario, score threshold, resource/time bound and scheduling convention.

One FIFO nonpreemptive server admits drop-tail only while waiting **plus actual
events in service** is below1024. Padding consumes no event capacity. Every
admitted event completes processing before its toy score decision. Each partial
batch with m≤B actual events pays the assumed B-slot duration; no tensor/model
padding executes. Actual sizes, unused slots and `completed/(B*batches)` slot
utilization are reported. This fixed-shape partial-batch cost is an assumption,
not measured deployment behavior.

At every integer-nanosecond timestamp: finish the active batch first; admit all
same-time arrivals in original source order; then dispatch if full or the oldest
waiting event's **original arrival plus timeout** has expired. A timeout already
expired during service dispatches immediately when idle. B1 dispatches immediately;
the final partial batch obeys the same rule. Empty dispatch and zero-service
loops are rejected. Checked signed64-bit nonnegative integer times avoid drift.

`dispatch_wait = dispatch−arrival` combines busy-server queue and idle batching
wait without inventing a decomposition. `latency = completion−arrival = wait +
constant_service`. All real batch events finish together. Overflow is excluded
from survivor latency statistics and shown beside them. Deadline misses are
strict `latency>1000000ns`; equality meets the illustrative deadline. Toy selected
misses use each selected count as denominator; an empty selection gives null.

## Curated service inputs and numerical boundary

Only these three small curated sources are permitted; exact byte hashes and every
path component's nonsymlink status are checked. No embedded model/input/receipt
path is followed and no raw timing trace is read:

| Source | SHA256 |
|---|---|
| [Task0022 cells](../results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv) | `ddd4d1ed21d11f28999687c757638238bb548e156061525a0c4ded368ed9d75b` |
| [Task0022 summary](../results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json) | `33c09221548ef56ef1b96f10c951161b65bea8d9565f2f3c100fd5f7a7c5744e` |
| [Task0032 cost arithmetic](../results/tables/final/task0032-quality-cost.csv) | `64883a3668c82edbe34b38fd125326196f579a9f3b58db89e12ce791ed10720d` |

Accepted Task0022 consumed/no-retry status, two actual candidate names/scientific
identities, seven accepted phase exits/reaping/deadlines/receipt lineage and90
unique worker/candidate/batch/scope cells are required. Only the30
`adapter_decision` cells for PCA1–3/pca-v1 and AE1–3/compact-autoencoder-v2 at
B1/8/32/128/1024 supply costs. Per-worker statistics and all ten joined groups
must agree across tables. Other scope values are not added to the adapter timer.

For each main profile use `Decimal` of the CSV worker means, weighted by200 each
over600 invocations, then round upward with `ROUND_CEILING` to integer ns.
All workers/repetitions/outliers are retained; Task0032's pooled mean, amortized
cost and throughput arithmetic are cross-checked. Sensitivity uses individual
worker mean/p99/max, likewise rounded upward, as **constant costs for every batch**.
The AE2/B12826248500ns=26.2485ms maximum must remain present. It is an intentionally
harsh constant stress assumption, not an observed recurring stall or an inferred
cause. p99 service statistics do not guarantee p99 queue latency.

Historical scope: preloaded standardized development features on the recorded
shared Mac/runtime; adapter validation/wrapping, forward, FP64 SSE and four
decisions are already included. Raw I/O, physical feature construction, transport
and queueing are excluded. The [accepted CPU synthesis](two-three-prong-synthesis.md)
supplies this scope. The simulator adds only synthetic queue/batch wait to the
assumed service. Neither simulator wall time nor modeled delay is a new physical
inference or detector end-to-end measurement. No empirical service distribution
is reconstructed from sparse quantiles.

## Fixed workloads and accounting

NumPy Generator/PCG64 uses separate SeedSequence keys
`[3700,seed,mode_id,rate,stream_id]`, mode0periodic/1Poisson,
stream0arrival/1score. Seeds41/42/43, rates10000/100000/1000000 per simulated second,
5000events per trace. Periodic gap is integer `ceil(1e9/rate)` (exact for these
rates). Exponential Poisson gaps are rounded upward to at least1ns, so quantization
slightly changes the process; report actual5000/H, not nominal rate as realized.
First arrival follows its first gap; H is the final arrival. Each immutable trace
has little-endian int64 arrival/FP64 score hashes and a joint hash, reused across
both cost candidates and every policy. Scores are Uniform[0,1), independent of
arrivals/service by assumption; strict toy cuts0.9/0.95/0.99/0.999 are applied only
after completion. They are not historical SSE cutoffs, calibrated operating points,
signal labels or physics efficiencies.

Main:2cost candidates×9policies×3rates×2modes×3seeds=324scenarios. Policies are
B1/0timeout and B8/32/128/1024 each at100/1000µs. Sensitivity adds54scenarios for
Poisson100000/s, B128/100µs,3seeds×2candidates×3workers×3constant statistics.
Total378scenarios/1890000presentations, using18traces/90000unique synthetic events.
All outcomes are retained; no policy winner or deployment target is selected.

Counters separately describe arrivals through H and same-policy full drain.
At H, record completed, waiting, in-service and total pending after the stated
tie ordering. Final conservation requires generated=dropped+completed,
admitted=completed, pending0 and selected+rejected=completed at every toy cut.
Maximum outstanding/waiting, busy time, batches/sizes/utilization, unused slots,
latencies and deadline losses are checked. Throughput-to-H divides completed-by-H
by H; full throughput divides all completed by last completion time; drain-only
throughput uses post-H completions/drain duration. Busy utilization likewise has
explicit H or full-duration denominators. Startup/drain are included; no stationary
capacity follows. Quantiles use fixed linear interpolation with rational rank
positions on integer ns; mean/quantile display can have fractional ns.

## Validation, execution and findings

Final status **`parent_accepted_synthetic_sweep`**, invocation
`29adbd34fce9432dace973aea3e1daa3`. The
[378-row/93-column table](../results/tables/final/task0037-synthetic-trigger-scenarios.csv)
retains every prescribed scenario; the
[summary](../results/tables/final/task0037-synthetic-trigger-summary.json) binds
source/provenance,18 trace hashes, exact counters, lifecycle/resources and limits.
Final main totals:1620000presentations=1528515completed+91485overflow; sensitivity
270000=258111completed+11889overflow. All admitted complete; final pending0.
These totals combine repeated scenario presentations, not independent events.

| Fixed profile | B1 | B8 | B32 | B128 | B1024 |
|---|---:|---:|---:|---:|---:|
| PCA pooled mean, upward-rounded ns/batch |8423|8777|17974|15982|45869|
| AE v2 pooled mean, upward-rounded ns/batch |35218|29807|35810|110925|86258|

The AE B1 mean35.218µs differs from its historical24.708µs median; the prescribed
mean preserves all repetitions. AE B128 pooled110.925µs likewise retains AE2's
large historical observations. No median substitution or outlier removal.

Observed finite fixed-workload outcomes, across both arrival modes/all three seeds:

| B1 scenario | Overflow/generated | Survivor p99 latency | Deadline misses/completed |
|---|---:|---:|---:|
| PCA, nominal100000/s |0%|8.423–165.811µs|0%|
| AE v2, nominal100000/s |50.84–51.78%|36.063ms|98.34–98.58%|
| PCA, nominal1000000/s |67.44–67.78%|8.625ms|91.56–91.74%|
| AE v2, nominal1000000/s |76.64–76.72%|36.063ms|97.51–97.52%|

Batching changes finite backlog/loss under these costs, but sparse tested policies
establish no optimum. At10000/s, B1024/100µs has no overflow and only0.192–0.196%
slot utilization: roughly two real events pay for1024 modeled slots. Conversely,
B32/1000µs at that rate has no overflow yet p99latency1.018ms PCA/1.036ms AE and
processed deadline misses9.10–10.88%/9.10–12.84%. Batch wait can breach the toy
deadline even without overflow; a larger nominal B is not guaranteed useful.

In the fixed AE2/B128 Poisson100000/s stress, worker-mean constant267599ns yields
no overflow, p99≈0.532ms and no processed misses. Constant p99 cost1161230ns
yields no overflow but p99latency2.318–2.382ms and100% processed misses. Constant
maximum26248500ns yields79.18–79.36% overflow and227.029–227.342ms survivor p99,
with100% processed misses. This is a systems sensitivity to **assumed recurring
cost**, not evidence that the historical outlier recurs. No cause or frequency
of the outlier, empirical distribution or deployment guarantee is inferred.

The Poisson traces' realized rates vary: nominal100000/s produces approximately
98912/102293/101999 per virtual second for seeds41/42/43. Periodic rates are exact
for the prescribed integer gaps. Startup/drain, finite seeds and quantization are
visible in the table. Scores affect only post-service selected counts; they
cannot repair queue loss. No physics acceptance/TPR/AP/AUC or uncertainty test.

[Latency](../results/figures/final/task0037-synthetic-trigger-latency.png),
[overflow](../results/figures/final/task0037-synthetic-trigger-loss.png) and
[fixed sensitivity](../results/figures/final/task0037-synthetic-trigger-sensitivity.png)
were all visually inspected. Latency axes are logarithmic with no clipping; loss
axes include0–100%. Markers show all three seeds, categorical policies are discrete
and unconnected. The dashed latency line is the illustrative1ms deadline. Survivor
latency must be read with the loss figure/table. No continuous optimum is implied.

Fresh final acceptance:
`data/task0037-validation/f73ef9fc01194dfe9eeddb8a42c7e98b/software-acceptance.json`:
200source/config/prompt bindings,43 installed distribution version identities,
105targeted tests and2022full+2022portable, lint/format/dependencies pass. Full
suites run in artifact-free source copies; historical synthetic model fixtures are
explicitly permitted. Per final full/portable process, existing controlled-
activation helpers record85instances/31forwards+reconstructions/8710rows/2started /
2completed updates/0inflight/2synthetic calibrations. Other legacy synthetic
model work is unquantified; globally zero regression forwards/updates are not
claimed. New simulator/operational model work remains zero.

Hand timelines/35independent integer-tick oracle cases cover FIFO/capacity/ties /
oldest timeout/final padding/horizon/drain/deadline equality/strict four-score ties.
Synthetic timing fixtures cover altered/missing/symlink/unaccepted/ambiguous inputs,
scope/arithmetic/outlier preservation; boundary/lifecycle/resource/assertion loss /
release/deadline suspension and incomplete-output vetoes are tested. Initial mock
configuration failure was fixed before acceptance; all versions/checks preserved.
Task0035's old1917acceptance is not reused to cover this new code.

There were **two actual fixed native invocations**, both exit0/reaped and
numerically parent-accepted. First`5755e3bb24984ef091614652e7128eed` took5.535386s;
its latency/loss upper legends overlapped titles, so its figures were not curated.
Only reporting layout was corrected and revalidated; second6.105818s passes all
three visual checks. Their378-row CSVs are byte-identical. Source-version-bound
receipts/plans/acceptances are unchanged. No scenario expansion or failed native
attempt. Across both actual sweeps:36 generation requests/180000synthetic events
(identical18 trace hashes/90000unique events),756scenarios/3780000presentations,
six curated numerical source loads. Final deliverable presents one fixed matrix.
Six earlier authorized prefix/JSON inspections are accounted separately:12 such
curated-input reads in Task0037's direct inspection/sweep handling. Hash custody,
in-memory reuse, synthetic fixtures and historical regression activity are separate.

Final continuous timing: prerequisites0.160031s; simulation dispatch/reap3.308455s
(worker3.259250s), reporting2.446330s(worker2.386706s), finalization0.072890s,
whole6.105818s, overshoot0. Cleanup0.000482s/0.000112s inside ceilings. Worker RSS
52527104/129613824B, native41943040/102039552B, controller39075840B, owned storage
5536034B at final measurement; retained trace object payload estimate6122304B.
Simulation2870/reporting42 **WARN** observations are advisory;0CRITICAL/unknown
primary pressure, no latched accounting error. Optional global-RAM context is
unavailable because worker subprocesses are forbidden; it is never admission.
Sample gaps0.052096/0.107185s and terminal unmonitored intervals0.049905/0.061834s
are disclosed. No continuous-memory or physical-suspension certificate.
Six active owned assertion observations; release/absence/TERM/reaping confirmed,
display sleep allowed and no persistent power settings changed.

## Reproduction and bounded lifecycle

```bash
.venv/bin/python scripts/validate_synthetic_trigger.py
.venv/bin/python -m latenttrigger.simulation.native \
  --acceptance data/task0037-validation/f73ef9fc01194dfe9eeddb8a42c7e98b/software-acceptance.json
```

Acceptance binds current source, dependencies, config and actual prompt. The
entrypoint permits no arbitrary event/model/cost path or expanded matrix. Each
invocation uses a fresh ignored UUID under `results/simulation/task0037-synthetic-trigger/`;
partial failures/receipts are preserved. Input byte custody and plan freezing
precede reservation; the simulation worker numerically loads each allowed source
once, generates each trace once and reuses memory. Reporting sees only the copied
parent-accepted aggregate JSON. No per-event output is curated or written by sweep.

Inspected Task0030 continuous-clock/owned idle-sleep assertion/reaping and
historical guard utilities are reused through narrow adapters. Limits30s
prerequisites/120s simulation dispatch-through-reap/60s reporting/15s finalization /
240s whole;2s cleanup inside each worker ceiling. Explicit1GiB RSS/512MiB native /
128MiB parent,64MiB journal/1MiB log/128MiB owned storage; retained trace payload
≤16MiB, at most5000wait/latency entries per scenario and1024outstanding events.
WARN advisory, CRITICAL/invalid-primary veto, unavailable pressure disclosed and
global RAM contextual. Host suspension consumes continuous deadlines; virtual
nanoseconds never control runtime ceilings. Owned assertion must be verified
before/during workers and released/reaped; display sleep remains permitted,
persistent settings unchanged. Body-complete cannot accept without normal exit /
reap/source/output/matrix/conservation/resource/deadline/release checks.

## Next engineering decision

Before any deployment policy, separately authorize development-only measurement
of service-time variability and missing chain costs: bounded raw-event I/O,
physical feature construction and transport, with matching scope/host/thread/batch
identities. A prospective variable-service synthetic extension could then use an
accepted service sequence and explicitly defined sampling/dependence assumptions.
Do not infer a distribution from current p50/p99/max, rescore exposed tests or
acquire a confirmation source. Neither follow-up is launched automatically.
