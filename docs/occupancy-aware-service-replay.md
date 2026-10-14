# Occupancy-aware paired service replay — Task0046

Task0046 implements a separate, model-free FIFO replay from Task0045's accepted
paired natural-partial/full-control timings. The [actual prompt](prompts/0046-occupancy-aware-service-replay.md)
authorizes one conditional timing-source session after fresh software acceptance,
serialized native roundtrip and immutable freeze. Arrivals, events, toy scores
and queue processing are synthetic. Task0044 and all historical helpers and
allowances remain unchanged.

## Closed source and prospective assignments

The [config](../configs/simulation/occupancy_service_replay_v1.json) fixes exactly
23 files and their sizes/SHA256, totaling 6,489,729 bytes. These contain the five
curated/config/prompt files, consumed Task0045 attempt, plan, workflow, parent
acceptance, owned reporting summary/receipt, and four files per repetition.
Only these paths are opened as timing sources. Every component must be safe,
repository-relative and nonsymlink; embedded raw/model/array/source-map paths
remain inert. The reader uses only the standard library and never imports the
physical service adapters.

Byte custody is followed by checks of the original task/owner0045, paired contract,
selected_partial_raw_to_decisions scope, owned natural packing, actual nonsynthetic
consumed campaign, original config/prompt/model/input identity strings, exact
integration parity and parent acceptance. Worker receipt/output digests, ordinary
zero exits, reaping, deadlines, zero overshoot and assertion release/absence are
required. A body-complete receipt is insufficient. The owned reporting summary
has aggregate_report_body_complete status; the curated summary adds acceptance
and lifecycle and revises geometry. Their distinct whole-file hashes are retained;
explicitly shared timing/count/parity/pooled/paired sections are checked.

All 180 cells, 1,800 curated pairs, aggregate observations/pairs and 4,140 ordered
chronological side records reconcile. The 540 warm durations are excluded from
assignment. Ninety separate vectors retain 20 ordered integer-ns natural/control
pairs keyed by candidate, source repetition, nominal B and anchor k. Pair IDs,
window/order metadata and recorded actual rows/service_B remain attached. Slow and
unfavorable observations remain; no pooling, resampling, clamping, fitted curve or
new jitter. Original timed observations remain 3,600 despite parsed copies and
replay reuse.

Summary serialization uses finite/type checks, exact integer identities and a
32-ULP binary64 rule. The independent standard-library reference reproduces the
writer's binary64 linear-rank and two-branch interpolation arithmetic, including
signed cancellation; generated tests compare it separately with NumPy. This is
mechanical serialization agreement, with no cost multiplier or scientific tolerance.

| Nominal B | Measured anchors A_B | Natural service_B |
| --- | --- | --- |
| 1 | 1 | 1 |
| 8 | 1, 2, 7, 8 | 8 |
| 32 | 1, 2, 8, 31, 32 | B, except k=8 uses8 |
| 128 | 1, 2, 32, 127, 128 | B, except k=32 uses32 |

For every actual dispatch size m, next_anchor chooses the smallest anchor k≥m;
previous_anchor chooses the largest k≤m. Each mapping has natural_anchor and
full_control billing. Natural assigns measured natural_k; control assigns its
contemporaneously paired full-B duration from that same anchor vector. Each variant
completes exactly m admitted synthetic events. It executes no padding, splitting,
extra k/B events or physical service.

When k≠m, assigning k-row natural cost to m events is an explicit unmeasured-work
hypothesis, including under-accounted modeled rows for previous_anchor. Neither
mapping is an empirical upper/lower bound; measured costs need not be monotone.
Even k=m transports a finite warm-window timing into a different synthetic input
and cache history. Nominal B, actual m, selected k, natural service_B/rows and
control B remain distinct. B-slot utilization describes batching, not padding.

Each scenario has one independent zero-initialized cursor per anchor. A dispatch
selects pair cursor[k] mod20, chooses its billing side, then advances only that
cursor. Arrivals, completions, decisions, idle time and audits never advance it.
All anchors start at pair0; their manufactured phase relation and repeating
20-pair cycles are assumptions, not observed cross-anchor chronology. Contrasting
queues can diverge in occupancy, dispatch count, surviving jobs and cursor history.
Source pairing is preserved at lookup; outcomes are deterministic systems contrasts,
without claiming physically paired jobs across scenarios.

## Queue, matrix and auditable modeled work

The separate engine preserves Task0037/0044 mechanics: one nonpreemptive FIFO,
capacity1024 waiting plus in-service events, drop-tail, ties completion then
source-ordered arrivals then dispatch. Full occupancy dispatches immediately when
idle; timeout uses the oldest waiting original arrival, including after service.
Every admitted event drains to completion. Checked integer-ns additions prevent
clock overflow; latency is dispatch wait plus that dispatch's captured service.
Busy time equals the exact assigned duration sum. Toy strict cuts .9/.95/.99/.999
occur only at completion; the illustrative100ms deadline is strictly exceeded.

The unchanged PCG64/SeedSequence generator creates each of18traces once: periodic/
Poisson, rates500/2500/5000events/s, seeds41/42/43,5000events each. Separate arrival/
toy-score streams use [3700,seed,mode_id,rate,stream_id], the original integer gap
rule and source order. Ninety thousand unique synthetic events are reused across
2candidates ×7policies ×3source repetitions ×4variants:3024scenarios and
15,120,000presentations. Policies are B1/zero timeout and B8/32/128 at1/10ms.

Each of756common contexts yields next natural−control, previous natural−control
and interaction (previous natural−control)−(next natural−control):2268contrasts.
The interaction also retains each side's previous−next level changes and all four
generated/completed/overflow/late/batch/busy denominators. No averaging of quantiles,
p-values, confidence intervals or stochastic replication claim.

Occupancy rows are streamed per scenario/m with k, batches, useful events, assigned
busy time, exact/mapped status, natural/control source shapes, modeled row work and
signed k−m and total row differences. Natural modeled work is k per dispatch;
control modeled work is B. Separate anchor rows include all anchors, including
unused ones, the20original-index counts, fingerprints, wraps/remainder, unused
samples and exact duration dot products. These reconstruct scenario busy time,
useful events, full/partial dispatches and exact/mapped totals. Worst-case row
bounds are145584occupancies and12528anchor rows. Empty categories have zeros and
null means with explicit denominators.

Only the current scenario retains ≤5000latencies, waits and batch-size values,
FIFO≤1024 and ≤128occupancy bins/100anchor-index counts. The conservative current
Python workspace bound is4MiB; source payload≤8MiB with64MiB conservative parsed
container envelope; paired lookup≤1MiB, traces≤16MiB. Aggregate container size is
reported separately from payload sizes and sampled RSS/native allocation. CSV row
and32MiB file-growth checks occur before writing; total owned storage≤128MiB and
combined guard journals≤64MiB. No event/dispatch/latency exports are retained.

## Admission and lifecycle

Additive0046producer, strict serialized verifier, immutable freeze, exclusive
claim, controller, independent worker checks and aggregate reporting bind the
actual prompt, config, final code/tests, installed packages/native binaries,
clock/guard/plotting paths and exact matrix/budgets. Generated23-file fixtures are
used in software validation; bootstrap evidence precedes the final emitted-record
admitted native roundtrip and its noncircular receipt. No unconditional admission
success mock is used in the new tests. Artifact-free full/portable historical
regressions can execute toy models/optimizers and are accounted separately.

The source allowance is claimed before operational source precheck. Any failure
consumes it; no altered subset, cost repair or retry is permitted. Prerequisite30s,
simulation120s through exit/reaping, reporting60s, finalization15s, whole240s;
cleanup2s is inside worker caps. WorkerRSS1GiB/native512MiB, controllerRSS128MiB,
source8MiB/lookup1MiB/traces16MiB/storage128MiB/journals64MiB/log1MiB remain fixed.
The parent stays standard-library only. Workers forbid physical imports, array
paths, network and children. Reporting receives only accepted owned aggregates,
with no source reopening or trace/scenario regeneration.

Continuous clock includes suspension and supervises exit independently of sampled
resources. A temporary owned idle-system-sleep assertion is actively verified,
released/reaped and confirmed absent before acceptance, including failure exits.
Display sleep is allowed and persistent settings remain untouched. WARN is advisory;
CRITICAL/invalid primary accounting vetoes. Optional context, query and terminal
gaps are disclosed rather than described as gap-free monitoring. Hash-bound outputs,
source coverage, exact counters/audits/conservation, normal exits/reaping, caps,
deadlines and assertion cleanup are all necessary for parent acceptance.

## Interpretation

Full controls process extra real events in Task0045; its source contrast combines
raw selections, features, packing and model shapes and cannot isolate disk/decoder/
model causality. Replay does not reproduce measured paired order/cache context or
partial-only streaming. Its runtime is simulation execution time, not trigger
latency. Next/previous are two chosen hypotheses whose spread need not contain
reality. No interpolation, universal distribution/envelope, production p99 or
policy recommendation follows.

Survivor latency quantiles exclude overflow and can contrast changed survivor
populations. Overflow-or-late fractions use generated-event denominators and
retain both components. Exact/mapped subgroup fractions describe their own queue
histories; they are not counterfactual outcomes. B1 mapping equality is a negative
control; natural/control m=B retains finite unequal measured costs.

Task0044 uses Task0043 and a different assignment contract and remains historical:
no campaign subtraction or rewrite. Transport, detector arrivals and independent
signal confirmation remain unmeasured/unresolved. Scientific gates, permanent
YES/YES/YES, Task0045/0043accepted-consumed, Task0041failed-consumed,
Task0042software-only, Task0036unresolved, Task0025failure and particle192/192 remain.
No Task0047 is launched.


## Actual accepted outcome

Status **parent_accepted_synthetic_occupancy_service_replay**, sole source session
`78a96792b4b04f809e0e0c7717a7b02d`, accepted and consumed. Whole continuous35.930375s,
prerequisites1.626991s, simulation dispatch→reap30.324291s, reporting2.874879s,
finalization.465359s, overshoot0. Both workers exit0/reaped; assertion12active
observations, released/reaped/confirmed absent. This is simulation runtime.

[Scenarios](../results/tables/final/task0046-occupancy-service-replay-scenarios.csv)
retain all3024cases;
[contrasts](../results/tables/final/task0046-occupancy-service-replay-contrasts.csv)
retain2268;
[occupancies](../results/tables/final/task0046-occupancy-service-replay-occupancies.csv)
has18629rows and
[anchor audit](../results/tables/final/task0046-occupancy-service-replay-anchor-audit.csv)
all12528rows. The [summary](../results/tables/final/task0046-occupancy-service-replay-summary.json)
binds closed23pins,90paired fingerprints/source-use counts,18trace hashes,
software evidence, actual counters/resources/lifecycle and failures. All original
vectors/pair indices are used somewhere in the full matrix; scenario-level unused
anchors/samples and wraps remain explicit. There are3,981,226dispatch assignments,
not new measurements. All15,120,000presentations conserve:13,761,044completed +
1,358,956overflow; admitted=completed, pending0. There are3,166,580late survivors.

Each row below sums756contexts/3,780,000repeated generated-event presentations.
It is descriptive arithmetic across the fixed grid, not an independent sample.

| Mapping / billing | Completed | Overflow | Late survivors | Mapped completed events | Mapped busy time |
| --- | ---: | ---: | ---: | ---: | ---: |
| next / natural | 3392514 | 387486 | 923236 | 26.4173% | 44.1412% |
| next / control | 3394551 | 385449 | 884926 | 32.9507% | 56.9710% |
| previous / natural | 3579492 | 200508 | 474904 | 51.5299% | 31.3287% |
| previous / control | 3394487 | 385513 | 883514 | 32.7304% | 56.5879% |

Main next natural−control sums **+2037overflow/+38310late**, despite lower assigned
busy totals. Overflow-or-late/generated changes +1.067381percentage points in the
summed grid; individual contrasts span −33.92…+59.70pp. Main overflow is worse in
138contexts, better90, equal528; survivor p99 changes −119.254…+123.557ms, with
324positive/432negative contrasts. No universal improvement follows.

Previous natural−control sums −185005overflow/−408610late; outcome fraction changes
−15.704101pp in the summed grid, individual −98.30…+58.94pp. Its natural modeled
row work is2497839 versus3579492completed useful events: **−1081653rows**. Main
next natural models4623512 versus3392514useful events: **+1230998rows**. These signed
hypothetical row differences are central to interpreting the sensitivity; none is
executed physical work. Previous p99 contrasts span −500.976…+123.557ms.
Interaction p99 is −473.696…+12.591ms; outcome-fraction interaction −97.20…+15.92pp,
including43unfavorable contexts. B1 mappings agree exactly for each side, while
natural/control effects remain noisy and unequal at full occupancy.

Three accepted figures were visually inspected, with readable labels, explicit
units/denominators, all seeds/repetitions and null/unfavorable points:
[loss/lateness contrasts](../results/figures/final/task0046-occupancy-service-replay-outcomes.png),
[survivor latency contrasts](../results/figures/final/task0046-occupancy-service-replay-latency.png),
[mapping reliance](../results/figures/final/task0046-occupancy-service-replay-sensitivity.png).
The reliance panels explicitly show next-natural, previous-natural and next-control;
the full four-variant reliance is in every scenario and the table above. Signed
contrasts use symlog with .01pp/.01ms linear thresholds; no data clipping or bands.

Final software evidence:167focused,3071full and3071portable tests, artifact-free
copies, lint/format/dependencies passed;294code/config/prompt bindings,43installed
packages and36installed native/metadata pins. Final generated bootstrap32.183913s
and actual emitted-record roundtrip34.100509s passed. Six native fixture invocations
are retained: four complete accepted matrices, a zero-scenario duplicate-audit
failure and a later atomic-temporary race failure. The latter retains722completed/
723started scenarios,3,610,000completed/3,615,000started presentations and
1,202,853assignments in completed scenarios, with the current scenario uncertain;
worker terminated/reaped and assertion released. It is not a complete matrix.
The temporary scan now uses one lstat and narrowly handles vanished owned JSON
atomic temporaries; parent contrast verification streams records. All failure
receipts/counters and earlier acceptance records remain ignored and preserved.

Two software versions ran full/portable checks. Their four instrumented historical
research subsets total340model instances,124forwards/reconstructions on34840rows,
8started/completed toy optimizer updates and8synthetic calibrations; other legacy
fixture activity lies outside those subset counters. The new replay's generated
bundles/native workers execute no models/optimizers. Four accepted fixture matrices
add60,480,000presentations; failed roundtrip adds the partial coverage above.
Repeated trace generation reuses the same90,000trace positions, not new measurements
or independently acquired events.

Preparatory source custody is3closed-bundle reads:69opens/19,469,187bytes,
9JSONLbyte opens/12420line records. Initial schema inspection parses6JSONLrecords
plus aggregate copies; two full validations parse8280records. One signed percentile
reference rejection is preserved. Operational session: prerequisite full validation,
worker full validation and final hash-only custody, each23opens/6489729bytes:
69opens/19,469,187bytes; six semantic JSONLloads/8280records,7200timed and1080warm
presentations. Final3JSONLbyte opens only hash bytes and parse no records. Each full
semantic load also checks14400timed duration copies plus540warm chronological copies;
original unique timed observations remain3600. Code/docs/package hashing and fixture
metadata are outside this closed-source ledger.

Sampled worker peaks RSS222838784B/native150667264B; controllerRSS108216320B,
parent native79495168B, conservative parent-plus-one-serial-worker native230162432B.
Owned storage36406677B; aggregate Python containers54318194B, retained traces6285148B,
combined lookup/current-assignment margin722834B. Current scenario workspace bound4MiB
and caps remain distinct from sampled allocation. Query-start max gaps simulation
.112593s/report.116076s/parent.202091s; terminal gaps.048777/.082212s. All primary
queries NORMAL; optional worker context is unavailable because subprocesses are
denied. These are sampled observations, not gap-free accounting or unique global RAM.

New operational raw/event/membership/golden/features/scientific score/event-fingerprint
payload loads, model/reconstruction/optimizer/scaler/calibration/scientific metrics,
HDF/raw custody/download/device/physical service counts are all0. This does not erase
Task0045's positive physical work or historical/fixture activity. The next bounded
decision is to scope missing occupancy or streaming/transport evidence separately;
these two mappings do not select a policy or automatically authorize Task0047.
