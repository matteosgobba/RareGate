# Native CPU and synthetic trigger study: integrated research closure

<!-- task0049-lead-start -->
The study establishes a reproducible computational baseline and a bounded synthetic
systems result, while leaving practical rare-anomaly usefulness and physical
streaming performance unresolved. Frozen PCA and a compact autoencoder have an
accepted scientific comparison on two signal topologies. The autoencoder ranks
events moderately better, with weaker discrimination on three-prong signal, but
its strictest frozen cuts accept very few signals. That ranking advantage neither
identifies nonlinearity as its cause nor establishes a useful anomaly trigger.

Separate accepted CPU campaigns measure increasingly complete boundaries: a
preloaded model adapter, prepared-row packing and result retention, selected raw
reads and feature construction, and direct raw-to-score-to-decision service.
The current paired campaign measures 32 prescribed partial-occupancy points,
including 15 freshly remeasured references. It leaves 137 legal occupancies
unmeasured. These measurements are finite, warm, dependent development-window
observations, rather than a universal service distribution.

Synthetic FIFO studies establish reproducible batching, overflow and illustrative
deadline behavior under explicit arrivals and cost assignments. The current
refined replay retains material sensitivity to missing occupancies, sample phase
and queue history. Apparent gains under previous-anchor billing include modeled
work deficits; support changes also change control costs. No deployment policy
or measured upper/lower bound follows.

The declared native CPU and synthetic research phase is therefore complete within
scope. Preserve the frozen baseline and choose the next question explicitly. A
design-only development streaming/cache/transport protocol is the default next
decision; independent scientific confirmation remains a separate requirement.
RareGate is independent research inspired by LHC computing, with no implied
official experiment or CERN affiliation.
<!-- task0049-lead-end -->

## What the evidence supports

Four kinds of evidence answer different questions. Software checks establish
declared implementation and serialization properties. Scientific evaluation
describes ranking and frozen operating points on specified populations. Physical
CPU measurements describe timed work on selected development inputs. Synthetic
systems results describe queues driven by generated arrivals and transported
costs. Passing tests or numerical parity does not measure productive throughput,
discover signal, or certify detector deployment. Claim IDs below refer to the
[claim registry](../results/tables/final/task0049-cpu-trigger-claims.csv), which
states denominators, assumptions and unsupported extensions explicitly.

The evidence set is closed: 57 reports, boundary configurations and curated
aggregate tables totaling 26,010,109 bytes, below the 32 MiB input ceiling. The
[evidence registry](../results/tables/final/task0049-cpu-trigger-evidence-registry.csv)
binds every path, source task, role, size and SHA256. Historical parent hashes and
statuses are provenance facts, not fresh operational acceptance. Failed campaigns
remain failed, and consumed allowances remain consumed. No new benchmark, model,
scientific evaluation, trace or queue execution was performed for this synthesis.

## Scientific usefulness and the computational bridge

The frozen baseline contains six-component PCA and the 155-parameter compact AE
v2, sharing eight prescribed aggregate features and their original calibration.
Higher reconstruction SSE remains anomalous; the PCA orientation was not reversed
after its unfavorable result. The accepted global-quality rows are copied below,
rounded only for display to six decimal places. Both signals and the shared
background remain visible. These are contextual scientific facts, not metrics
recomputed by Task0049. [Evidence C01–C03; Task0032](two-three-prong-synthesis.md).

<!-- task0049-table:quality -->
| Candidate | Signal | Accepted AUC | Accepted AP | BG / signal rows |
| --- | --- | --- | --- | --- |
| PCA | two_prong | 0.468489 | 0.364379 | 150471 / 100000 |
| AE | two_prong | 0.660064 | 0.547427 | 150471 / 100000 |
| PCA | three_prong | 0.462953 | 0.360220 | 150471 / 100000 |
| AE | three_prong | 0.585877 | 0.479972 | 150471 / 100000 |
<!-- /task0049-table:quality -->

AE discrimination is moderate for two-prong and weaker for three-prong. PCA and
AE differ in capacity, representation and arithmetic, so their observed ranking
does not isolate a causal contribution from nonlinearity. AP depends on the
evaluated mixture: 100,000 signal rows against 150,471 background rows per signal
topology. That constructed prevalence is not an LHC signal rate. Reusing the
same background scores across topologies supplies a common reference, not an
independent background replication or domain-shift experiment.

All sixteen original calibrated points follow, including the original full
threshold precision. The target FPR is a calibration label; achieved background
acceptance is the observed denominator-specific result. Strict comparisons are
`score > threshold`, with ties rejected. No threshold was selected or changed
during this closure.

<!-- task0049-table:calibration -->
| Candidate | Signal | Original target FPR | Frozen threshold | Signal accepted / 100000 | Shared BG accepted / 150471 |
| --- | --- | --- | --- | --- | --- |
| PCA | two_prong | 0.1 | 0.3496768162794852 | 4620 | 14922 |
| PCA | two_prong | 0.05 | 0.5642097175249418 | 852 | 7362 |
| PCA | two_prong | 0.01 | 1.4232146905138892 | 90 | 1416 |
| PCA | two_prong | 0.001 | 4.1356483360291865 | 2 | 124 |
| AE | two_prong | 0.1 | 3.478338537407165 | 23217 | 14793 |
| AE | two_prong | 0.05 | 4.681070974717348 | 13608 | 7357 |
| AE | two_prong | 0.01 | 8.324174660133213 | 3298 | 1424 |
| AE | two_prong | 0.001 | 16.642218868621573 | 56 | 116 |
| PCA | three_prong | 0.1 | 0.3496768162794852 | 3942 | 14922 |
| PCA | three_prong | 0.05 | 0.5642097175249418 | 762 | 7362 |
| PCA | three_prong | 0.01 | 1.4232146905138892 | 43 | 1416 |
| PCA | three_prong | 0.001 | 4.1356483360291865 | 1 | 124 |
| AE | three_prong | 0.1 | 3.478338537407165 | 16438 | 14793 |
| AE | three_prong | 0.05 | 4.681070974717348 | 10326 | 7357 |
| AE | three_prong | 0.01 | 8.324174660133213 | 2662 | 1424 |
| AE | three_prong | 0.001 | 16.642218868621573 | 34 | 116 |
<!-- /task0049-table:calibration -->

At the strictest AE threshold, 56 two-prong and 34 three-prong signals survive
out of 100,000 each, against 116 of the shared 150,471 background rows. These
counts explain why moderate ranking cannot be equated with strong strict-tail
utility. Existing uncertainty metadata remains in the source; this report adds
no curve, confidence interval, significance estimate or scientific ranking
calculation. Toy replay acceptance is unrelated to these physical signal and
background labels, and the two must not be combined into an invented utility.

Scientific evaluation used reference batch B4096, including its complete tails.
The later computational gates cover small, reused development windows at their
actual shapes. Model, scaler, feature and calibration identities link those
studies, but exact same-shaped development score/mask parity does not certify
every test decision under arbitrary streaming batch sizes, runtimes or precision.
No inference was repeated to strengthen that bridge.

## Physical boundaries and honest comparisons

The [CPU boundary table](../results/tables/final/task0049-cpu-service-boundaries.csv)
records every accepted physical campaign, candidate and measured scope: actual
and nominal shape, packing/wrapper, population and windows, timer endpoints,
included/excluded work, cache/thread context, sample schedule, parity and limits.
Its selectors identify every original cell and all three repetitions. The six
campaigns establish complementary evidence, not interchangeable measurements.

Task0022 brackets separate reconstruction, score/decision and public-adapter
scopes on preloaded prepared inputs. The score-only scope uses precomputed
reconstruction; adding it to another measured scope is not a measured joint cost.
Each cell contains 200 timed calls after 20 warm-ups, with three fresh workers
per candidate and fixed batch/scope ordering. Single-thread controls were queried
in the historical campaign. The retained AE2 slow call makes the difference
between means and medians practically important; it is not a measured recurring
stall frequency. [Task0022](frozen-cpu-benchmark-v2.md).

Task0038 adds owned contiguous packing, the public score, four decisions and
first-m result retention. Natural service computes m rows; padded service really
computes B rows, including exact standardized-zero dummy rows. Its window starts
depend on m and are deduplicated. Each side has 50 timed calls per repetition,
with alternating side order. Loading, raw I/O, physical feature construction,
transport and queueing are excluded. The dummy rows are computational work,
not extra physical events. [Task0038](prepared-batch-service-measurement.md).

Task0040 separately measures checked selected-HDF read, frozen features on
preloaded raw windows, and the direct read-to-features chain. Each fixed scope
has 20 timed calls per repetition. The direct joint measurement is primary;
component means or medians cannot be stacked into its substitute. Persistent
HDF caches, selection/materialization and unknown decoder threading prevent a
disk-versus-decompression attribution. Geometry counts are not measured I/O or
cache misses. [Task0040](development-raw-feature-measurement.md).

Task0043 directly measures selected raw through frozen features, packing, the
public score, four strict masks and owned results. Loads, hashes, reference/parity
work and explicit monitoring queries lie outside the service pair; transport and
queueing remain excluded. Both candidates, B1/8/32/128 and all three repetitions
are retained. Its full-B timing is a separate boundary from the preloaded adapter
and from raw-to-features. [Task0043](development-raw-decision-campaign-v2.md).

Task0045 pairs natural m-row service with B **real** rows in the containing full
control. Both sides read independently. Windows start from nominal B, unlike
Task0038's m-based convention. The historical helper has legal-shape mappings,
including the quarter case; those guards were not widened. Task0047 uses its own
closed actual-row wrapper through the unchanged public model score. It freshly
remeasures all fifteen references alongside seventeen new points, with actual
model shape m or B, three warm pairs, twenty timed pairs and ten pairs per side
order in each repetition. Thus old and current timings cannot be silently mixed.
[Tasks0045](natural-partial-raw-decision-measurement.md)/[0047](targeted-partial-raw-decision-measurement.md).

For raw campaigns, the same approved 1,024-row development prefix yields a
384-row selected raw union. The B-containing starts are 0, floor((1024−B)/2)
and 1024−B. Timed windows occur 7/7/6 times per cell. One persistent read-only
HDF handle per worker uses the declared 1 MiB/521/.75 cache; the OS has prior
custody/hash history. Effective CPU single threading and unknown decoder/cache
history are different facts. Serial repetitions are not independent trials,
fixed reverse ordering does not remove host drift, and monitoring can interfere.

The fixed examples below expose boundary changes and every repetition rather
than a cross-campaign speedup. They are whole-call means in milliseconds, rounded
to six decimals, with three original cell means shown to three decimals. Existing
pooled per-case means are preferred. Count-weighted reconstruction from cell
aggregates checks their denominators; percentiles are never averaged. No slow,
unfavorable or equal-work observation is removed. [Evidence C04–C06].

<!-- task0049-table:costs -->
| Task | Fixed case / scope / side | Timed count | Whole-call mean ms | All three cell means ms |
| --- | --- | --- | --- | --- |
| 0022 | pca-v1/1/adapter_decision | 600 | 0.008422 | 0.008/0.008/0.009 |
| 0022 | compact-autoencoder-v2/1/adapter_decision | 600 | 0.035217 | 0.024/0.054/0.027 |
| 0038 | pca-v1/1024/1/natural | 150 | 0.017570 | 0.016/0.015/0.022 |
| 0038 | compact-autoencoder-v2/1024/1/natural | 150 | 0.039320 | 0.039/0.039/0.040 |
| 0040 | 128/selected_raw_to_features | 60 | 50.012520 | 47.940/50.004/52.093 |
| 0043 | pca-v1/1 | 60 | 0.572585 | 0.570/0.564/0.583 |
| 0043 | pca-v1/128 | 60 | 48.047652 | 49.213/48.280/46.649 |
| 0043 | compact-autoencoder-v2/1 | 60 | 0.606340 | 0.585/0.604/0.630 |
| 0043 | compact-autoencoder-v2/128 | 60 | 47.514822 | 46.444/48.753/47.348 |
| 0045 | pca-v1/128/32/natural_m | 60 | 12.791603 | 12.955/12.817/12.603 |
| 0045 | pca-v1/128/32/full_B_control | 60 | 48.610510 | 49.493/48.676/47.662 |
| 0045 | compact-autoencoder-v2/128/32/natural_m | 60 | 13.239432 | 13.063/13.904/12.751 |
| 0045 | compact-autoencoder-v2/128/32/full_B_control | 60 | 50.181058 | 49.720/52.924/47.899 |
| 0047 | pca-v1/128/10/natural_m | 60 | 4.455069 | 4.395/4.440/4.531 |
| 0047 | pca-v1/128/10/full_B_control | 60 | 49.077315 | 46.969/49.706/50.556 |
| 0047 | pca-v1/128/32/natural_m | 60 | 12.791770 | 12.501/12.934/12.940 |
| 0047 | pca-v1/128/32/full_B_control | 60 | 48.888608 | 47.124/50.265/49.276 |
| 0047 | compact-autoencoder-v2/128/10/natural_m | 60 | 4.556222 | 4.468/4.511/4.690 |
| 0047 | compact-autoencoder-v2/128/10/full_B_control | 60 | 50.593565 | 49.359/48.295/54.127 |
| 0047 | compact-autoencoder-v2/128/32/natural_m | 60 | 13.228501 | 12.782/13.549/13.354 |
| 0047 | compact-autoencoder-v2/128/32/full_B_control | 60 | 49.932907 | 50.607/48.929/50.262 |
<!-- /task0049-table:costs -->

A whole-batch cost divides by actual processed rows for computational
amortization, or by useful m for a stated useful-event bill. These differ for
controls and dummy padding. Service throughput uses actual or useful rows divided
by a defined service duration. Completed-through-horizon throughput instead uses
completed synthetic events divided by the arrival horizon, retaining startup,
overflow and pending effects. None is automatically detector throughput. The
Task0047 examples are authoritative only for their current prescribed cases:
32 of 169 occupancies, leaving 137 unmeasured. Observed extrema are finite calls,
not confidence bounds; no interpolation or monotonic cost function is fitted.

## Synthetic studies: common semantics, different experiments

The [replay comparability table](../results/tables/final/task0049-replay-comparability.csv)
records source campaign/vector scope, assignment and cursor rules, supports,
arrivals, policies, trace hashes, startup/horizon/drain and toy decisions. All
studies use one nonpreemptive FIFO server, drop-tail capacity 1,024 including
active events, and completion-before-arrivals-before-dispatch tie order. Full
batches dispatch immediately; timeouts refer to the oldest original waiting
arrival. Final admitted events drain. These shared rules do not make the grids
or transported costs interchangeable. [Evidence C14–C16].

Task0037 uses rates 10,000/100,000/1,000,000 events/s, a 1 ms illustrative deadline
and B up to 1,024. Its 378 scenarios include a specifically defined constant-cost
sensitivity subset. Task0044 instead uses Task0043 raw-to-decision costs,
500/2,500/5,000 events/s, a 100 ms deadline and seven B1/8/32/128 policies.
It compares cyclic and constant costs, with reverse/rotation controls only in
the stated Poisson-2,500 subset: 1,764 scenarios and 1,008 contrasts. Cyclic−constant
adds 349 overflow and 5,264 late survivors in that finite matrix. This establishes
assignment sensitivity, not a fitted service distribution.

Task0046 uses its own older Task0045 paired vectors, two sparse-anchor mappings
and case-specific natural/control billing: 3,024 scenarios and 2,268 contrasts.
Task0048 uses only current Task0047 vectors, adding refined/coarse support
sensitivity: 6,048 scenarios and 6,048 contrasts. Coarse support contains the
current campaign's remeasured references. Subtracting Task0046 outcomes would
mix campaigns, wrappers and costs, so it cannot isolate a measurement benefit.

Later studies share all eighteen trace hashes: periodic/Poisson, three rates and
seeds 41/42/43, 5,000 positions each, using the declared PCG64/SeedSequence rule
and separate toy-score stream. Repeated generation or scenario presentations
do not create independent events. Task0037 has a different rate grid. The four
strict toy cuts occur after completion and are neither physical TPR/FPR nor
scientific efficiency. Outcome totals are never pooled across incompatible grids.

## Current refined result and remaining mapping dependence

Task0048's 30,240,000 presentations equal 27,544,586 completions plus 2,695,414
overflow drops, with final pending zero and 6,067,628 late completed survivors.
There are 756 common contexts, eight variants per context and eight contrast
families. Each variant presents 3,780,000 generated events. These are repeated-grid
sums, not a physical rate or independent sample size. All eight variant totals
and their useful-event/busy denominators follow. Surplus and deficit are separate
curated modeled-work counts, not extra physical processing. [Evidence C07–C13].

<!-- task0049-table:variants -->
| Current support / mapping / side | Completed | Overflow | Late survivors | Mapped event % | Mapped busy % | Modeled surplus / deficit |
| --- | --- | --- | --- | --- | --- | --- |
| coarse_reference/next_anchor/natural_anchor | 3398719 | 381281 | 852814 | 26.1459 | 44.1473 | 1232479 / 0 |
| coarse_reference/next_anchor/full_control | 3399123 | 380877 | 875117 | 32.3013 | 56.6702 | 3775478 / 0 |
| coarse_reference/previous_anchor/natural_anchor | 3589832 | 190168 | 409071 | 52.2386 | 32.2416 | 0 / 1098737 |
| coarse_reference/previous_anchor/full_control | 3399360 | 380640 | 859155 | 32.5306 | 56.7839 | 3833345 / 0 |
| refined_32/next_anchor/natural_anchor | 3399223 | 380777 | 852258 | 9.1235 | 10.6613 | 104609 / 0 |
| refined_32/next_anchor/full_control | 3399168 | 380832 | 873972 | 19.1196 | 31.5834 | 3780793 / 0 |
| refined_32/previous_anchor/natural_anchor | 3559910 | 220090 | 472767 | 27.3306 | 15.2802 | 0 / 473944 |
| refined_32/previous_anchor/full_control | 3399251 | 380749 | 872474 | 19.2371 | 31.6024 | 3771366 / 0 |
<!-- /task0049-table:variants -->

Define D=natural−control. Positive loss/lateness means harm on the natural side.
Mapping interaction is previous D−next D; support interaction is refined D−coarse D.
All family signs, null counts and per-context ranges remain visible below. The
refined next sum of −55 overflow hides 77 harmful contexts; its late sum of
−21,714 hides 171 harmful contexts. Previous retains 32 harmful overflow contexts
and 110 harmful late contexts despite larger favorable sums. Cancellation is
therefore central to interpretation, rather than evidence of universal benefit.

<!-- task0049-table:contrasts -->
| Family (756 contexts each) | Sum D overflow | Sum D late | Overflow −/0/+/null | Late −/0/+/null | Per-context survivor-p99 contrast range ms |
| --- | --- | --- | --- | --- | --- |
| coarse_reference/next_natural_minus_control | 404 | -22303 | 172/503/81/0 | 229/358/169/0 | -108.508 to 231.352 |
| coarse_reference/previous_natural_minus_control | -190472 | -450084 | 222/505/29/0 | 308/354/94/0 | -463.510 to 16.022 |
| coarse_reference/mapping_interaction | -190876 | -427781 | 156/600/0/0 | 218/466/72/0 | -562.455 to 7.083 |
| refined_32/next_natural_minus_control | -55 | -21714 | 174/505/77/0 | 225/360/171/0 | -108.508 to 231.352 |
| refined_32/previous_natural_minus_control | -160659 | -399707 | 216/508/32/0 | 294/352/110/0 | -453.741 to 16.022 |
| refined_32/mapping_interaction | -160604 | -377993 | 120/636/0/0 | 206/505/45/0 | -542.253 to 5.525 |
| next_anchor/support_interaction | -459 | 589 | 65/663/28/0 | 87/585/84/0 | -32.628 to 13.624 |
| previous_anchor/support_interaction | 29813 | 50377 | 24/672/60/0 | 117/542/97/0 | -386.314 to 419.229 |
<!-- /task0049-table:contrasts -->

Quantile interactions are arithmetic descriptor contrasts. Survivor p99 excludes
overflow and can describe different survivor populations after queue divergence;
it is not event-paired inference, a production p99 or a confidence envelope.
The table gives extrema and signs across contexts, without averaging or summing
percentiles. Missing quantiles propagate nulls, never zero. Generated-denominator
overflow-or-late fractions keep loss and late survivors distinct from the
completed-survivor denominator.

Both natural and control levels change under refined support:

<!-- task0049-table:levels -->
| Refined−coarse | Δ natural overflow | Δ control overflow | ΔD overflow | Δ natural late | Δ control late | ΔD late |
| --- | --- | --- | --- | --- | --- | --- |
| next_anchor | -504 | -45 | -459 | -556 | -1145 | 589 |
| previous_anchor | 29922 | 109 | 29813 | 63696 | 13319 | 50377 |
<!-- /task0049-table:levels -->

Changing support can select a different control case, consume a different
sample phase and alter subsequent occupancy. Both supports share identical
current vectors at common anchors, yet those interactions do not causally isolate
the benefit of adding measurements. Lower billed busy time also need not produce
lower latency or loss in every context.

Natural next still maps 9.1235% of completed useful events and 10.6613% of assigned
busy time; previous maps 27.3306% and 15.2802%. Next's modeled surplus is 104,609
rows. Previous's deficit is 473,944: assigning a measured k<m cost to m useful
events undercounts source-modeled work. Previous is not a measured lower bound,
nor next an upper bound; nonmonotone finite costs and queue histories need not
bracket reality. Independent zero-origin modulo-20 anchor cursors impose artificial
cross-anchor phases and repeated cycles. Lookup pairing does not physically pair
jobs or survivors in queues that have diverged.

Refined B8 has all m1…8 anchors, zero mapped use and next/previous equality per
billing side. Even exact k=m still transports warm finite observations to another
input/cache history. New residual occupancies can appear in a refined queue but
not its matched coarse queue. The existing curated counts below are context-local
appearances outside all 32 measured points, not new physical measurements or
global discoveries. No occupancy ledger was reopened to reproduce them.

<!-- task0049-table:residuals -->
| Refined mapping / side | Matched contexts with new residual / 756 | Batches | Useful events | Assigned busy ns |
| --- | --- | --- | --- | --- |
| next_anchor/natural_anchor | 143 | 493 | 28808 | 15990157528 |
| next_anchor/full_control | 114 | 223 | 9395 | 8705324108 |
| previous_anchor/natural_anchor | 137 | 21201 | 382135 | 94227792556 |
| previous_anchor/full_control | 170 | 1186 | 53072 | 57750556347 |
<!-- /task0049-table:residuals -->

## Closure decision and unresolved evidence

Close the declared CPU/synthetic phase and preserve its frozen baseline. The
accepted measurements and reproducible systems sensitivities answer the bounded
engineering questions; inconclusive deployment utility is a valid research outcome.
Further sparse points are not automatically the most informative next step, and
filling all 137 gaps would still leave streaming/cache/transport history unresolved.
No policy is selected. [Decision claims C20–C23].

The default next decision is **design only**: specify a target development
workload, input role and allowed host scope; define timer start/end, transport
placement, batching/arrival and source/cache history; derive resource/output
envelopes; and state success, failure and stop criteria before execution. The
design should distinguish cold/warm or repeated-input assumptions from a physical
detector stream and specify what independent evidence each conclusion would need.
It should identify evidence that could reject the model as well as support it.
The following is a proposed design target, not an executable plan or renewed
allowance:

- **Workload and role:** a bounded development-background stream using the frozen
  PCA/AE and eight features, with actual occupancies within nominal B1/8/32/128.
  Start from the already declared 500/2,500/5,000 events/s load questions; design
  how arrivals and backpressure would be represented before choosing any run.
  Repeated development rows must be labeled repeated inputs, never new independent
  events. Held-out populations and new sources require separate authorization.
- **Boundary and source history:** define software ingress before decode through
  owned four-decision output, exposing transport, preparation, service and waiting
  as separately recorded boundaries. Prescribe cache initialization, handle
  lifetime, input order and reuse; compare only histories that the design actually
  controls. Do not infer a physical detector link from an in-memory transport.
- **Host and resources:** specify one documented native CPU environment and
  effective threads. Derive maximum live buffers, queue state, retained output,
  process/native memory and continuous-time ceilings from the proposed workload;
  justify feasibility before asking for execution. Historical caps are evidence,
  not a granted budget for this new protocol.
- **Success and stop criteria:** require complete generated/admitted/dropped/
  pending/completed accounting, declared-shape parity, explicit timestamps and
  missing observations, preserved unfavorable cases and supervised normal exits.
  Stop on identity, parity, finite-arithmetic, resource or deadline failure.
  A feasible protocol or an explicit infeasibility result is useful; success
  need not mean lower cost. Physics usefulness still needs independent scientific
  confirmation under the unchanged gates.

No implementation, operational budget reservation, source acquisition or Task0050
is authorized here. Other runtime/precision/hardware or particle options are
separate choices, not prerequisites for closure.

Independent scientific confirmation remains Task0036
`unresolved_no_acquisition`: completeness, units, independence, counts and storage
acceptance are missing under unchanged Task0034 gates. All three evaluated
populations remain exposed permanently; result-informed new model development
needs an adequate independent route. Particle code and diagnostic characterizations
are not canonical trained usefulness; 192/192 is consumed and execution remains
deferred. Original accepted/consumed, failed and software-only states persist.

Task0024 accepted ONNX export/equivalence is distinct from Task0025's rejected
performance campaign. Completed numerical/timing bodies did not overcome ORT3's
failed normal exit; its shutdown cause remains unverified. Task0023 is an old
failed/unavailable-device snapshot, not a current MPS check. Task0039 supplied
membership metadata, Task0041 no accepted real measurement and Task0042 software
repair. These explanatory records are excluded from accepted physical costs.
[Evidence C17–C19].

## Reproduction, precision and verification limits

From the repository root, the isolated stdlib helper processes only the explicit
manifest, streams large CSVs and keeps the current eight-scenario/eight-contrast
context. Every source read records bytes/hash; embedded paths are inert. It checks
source statuses, schemas, finite values, physical cell counts, per-case weighted
means, all four scientific rows and sixteen copied calibrated points, earlier
replay aggregates, current conservation/constituent references, every descriptor
contrast and B1/refined-B8 controls. Shared later trace hashes are compared without
generating traces. The report tables are mechanically checked against these facts.

```sh
.venv/bin/python scripts/summarize_cpu_trigger_study.py --check \
  --audit data/task0049-validation/reproduction-check.json
.venv/bin/python -m unittest tests.test_cpu_trigger_synthesis -v
.venv/bin/ruff check scripts/summarize_cpu_trigger_study.py tests/test_cpu_trigger_synthesis.py
.venv/bin/ruff format --check scripts/summarize_cpu_trigger_study.py tests/test_cpu_trigger_synthesis.py
```

Running without `--check` rebuilds only six Task0049 metadata outputs. Machine
JSON preserves copied decimal tokens as strings and integers as integers; CSVs
retain original decimal precision. Display conversion is ns/1,000,000 to ms,
with declared rounding. A uniquely recoverable integer-duration sum from each
rounded cell mean checks count-weighted pooling; seven Task0022 pooled means
differ by one binary64 serialization ULP. That representational check changes no
timing or experimental tolerance. Percentiles are copied within their original
case, never averaged across cells or physically heterogeneous cases.

One inspection deviation is explicit: two early generic parses of the allowlisted
Task0046 summary incidentally decoded its embedded 90 timing vectors, containing
3,600 original duration values per parse. They were not analyzed or assigned.
The final reader lexically omits that subtree before semantic decoding, with
dedicated fixtures. No timing-pair CSV, timing JSONL or ignored operational
evidence was opened. Task0049's raw/model/HDF/optimizer/scientific-metric/download/
physical-timing/replay/trace work is zero; metadata reads and descriptive curation
are positive work. Historical model/optimizer fixture activity remains historical,
not globally zero. Small independent metadata fixtures and relevant static checks
are appropriate here; no fresh full-suite, native or hosted-CI result is claimed.

## References and reproducible outputs

- [Closed registry and derivation rules](../configs/reporting/cpu_trigger_synthesis_v1.json).
- [Evidence registry](../results/tables/final/task0049-cpu-trigger-evidence-registry.csv), [CPU boundaries](../results/tables/final/task0049-cpu-service-boundaries.csv), [replay comparability](../results/tables/final/task0049-replay-comparability.csv).
- [Current conclusions](../results/tables/final/task0049-refined-replay-conclusions.csv), [claims](../results/tables/final/task0049-cpu-trigger-claims.csv), [machine summary](../results/tables/final/task0049-cpu-trigger-synthesis-summary.json).
- [Italian decision brief](cpu-trigger-study-decision-brief.md) and [Task0049 handoff](handoffs/0049-cpu-trigger-study-synthesis.md).
- Existing inspected figures: [Task0043 joint costs](../results/figures/final/task0043-development-raw-decision-joint-cost.png), [Task0048 billing outcomes](../results/figures/final/task0048-refined-service-replay-outcomes.png), [support interactions](../results/figures/final/task0048-refined-service-replay-support.png), [residual dependence](../results/figures/final/task0048-refined-service-replay-residual.png). They remain unchanged; Task0049 creates no new figure.
