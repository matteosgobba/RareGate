# Task0048 — Refined-support paired service replay

Task0048 implements a separate, model-free synthetic FIFO replay of the accepted
current Task0047 campaign. One source session is **parent_accepted_synthetic_refined_support_service_replay**;
its Task0048 allowance is consumed. It completed in78.911485s with all6048scenarios,
6048contrasts,39291occupancy rows and39744anchor rows accepted. The actual authorization is
[preserved verbatim](prompts/0048-refined-support-service-replay.md); the
[Italian handoff](handoffs/0048-refined-support-service-replay.md) records actual
execution, failures, accounting and the manual Git workflow.

## Source and support contract

Only the closed 24-file Task0047 metadata bundle is eligible: 17,238,096 bytes,
384 cells, 3,840 timed pairs, 7,680 original timed durations and 1,152 excluded warm
durations in 8,832 chronological side records. The source ceiling is explicitly
24 MiB. No embedded raw, model, feature, array, old selection or old timing path is
followed. All source paths, byte counts and SHA256 pins are in the closed
[configuration](../configs/simulation/refined_service_replay_v1.json).

The stdlib reader checks accepted parent relationships, the distinct curated and
owned reporting bodies, task/owner 0047, original prompt/config/paired contract,
wrapper, exact parity, consumed allowance, receipts/output hashes, ordinary exits,
reaping, deadlines, zero overshoot and assertion release/absence. Each candidate,
source repetition and nominal B/k retains its own immutable 20-pair vector. Side
order alternates 10/10; timed windows have counts 7/7/6. Integer differences and
ratios are checked mechanically. Independently tested 32-ULP binary64 agreement
applies only to serialized statistics, without changing any duration or cost.
All unfavorable, null and slow observations remain.

The selection CSV covers all 169 legal nominal B/m combinations and reconciles
its original digest/classification/count/rank links within this bundle. Its old
selection evidence remains inert. This does not load Task0045 timings or recreate
Task0046 outcomes.

| Nominal B | coarse_reference: 15 current remeasured points | refined_32: all current points |
| ---: | --- | --- |
| 1 | 1 | 1 |
| 8 | 1, 2, 7, 8 | 1–8 |
| 32 | 1, 2, 8, 31, 32 | 1–8, 31, 32 |
| 128 | 1, 2, 32, 127, 128 | 1–10, 32, 127, 128 |

Common anchors share the same current vector, integer fingerprint and original
pair/window/alternating-order fingerprint. Refined support is primary; coarse is
within-current-source sensitivity. Seventeen new points and fifteen references
are kept distinct. There are still 137 physically unmeasured occupancies.

## Assignment and queue

For each actual dispatch m, next_anchor selects the smallest eligible k ≥ m and
previous_anchor the largest k ≤ m. Natural billing uses that pair's natural_k
integer duration; full_control uses its contemporaneous full-B duration in the
same case. Controls are case-specific. No `(B,B)` substitution, cost sorting,
monotonicity, clamping, trimming, pooling, interpolation, resampling or jitter is
used. Natural/control at m=B retain different observed durations.

Every scenario resets one zero cursor per eligible anchor. Dispatch consumes
index cursor[k] modulo 20 and advances only that anchor once. Arrivals,
completions, decisions, audit creation and idle time never advance it. Independent
zero phases across anchors and artificial cycle repetition are assumptions,
not physical chronology. Lookup always completes exactly m admitted synthetic
events; it does not execute k/B physical rows, pad, split or manufacture events.
Natural modeled work counts k rows and control modeled work B rows. For k≠m this
is an unmeasured-work hypothesis, including a signed modeled-row deficit for k<m.

The separate engine preserves FIFO, one nonpreemptive server, capacity 1024
including waiting and active events, drop-tail, and tie order completion →
source-ordered arrivals → dispatch. Full batches start immediately on an idle
server; timeout uses the oldest waiting event's original arrival. Arithmetic is
checked integer ns. Latency equals dispatch wait plus captured service, all
admitted events finally drain and busy time equals the assigned-duration sum.
Time zero precedes the first generated arrival; startup idle time remains in the
full-drain utilization denominator. Horizon/pending and drain descriptors retain
that convention. Four strict toy cuts .9/.95/.99/.999 run after completion; late
means latency strictly greater than the illustrative 100 ms deadline.

The unchanged Task0037/0044 generator creates exactly 18 traces once per sweep:
periodic/Poisson × 500/2500/5000 events/s × seeds 41/42/43, 5,000 events each,
PCG64 SeedSequence `[3700, seed, mode_id, rate, stream_id]`, original integer gap
rule and a separate toy-score stream. Hashes identify reuse across the complete
matrix. Policies are (1,0) and B8/32/128 with 1 or 10 ms timeout. Capacity,
deadline, costs, traces and policy grid never adapt to results.

## Contrasts and aggregate schemas

There are 6,048 scenarios: 18 traces × 2 candidates × 7 policies × 3 source
repetitions × 2 supports × 2 mappings × 2 billing sides. They present 30,240,000
events from 90,000 unique synthetic trace positions. Each common context has eight
variants, ordered coarse then refined, next then previous, natural then control.
The deterministic integer scenario_id resolves every identity in the scenario
CSV. Within each context, v0…v7 references in every contrast row identify all eight
constituents and their generated, completed, overflow, late, batch and busy
counts/denominators.

For each numerical outcome or descriptor Y, define D = Y_natural − Y_control:

- Four billing contrasts: next D and previous D within each support.
- Two mapping interactions: previous D − next D, one per support, with both
  natural/control previous-minus-next level changes.
- Two support interactions: refined D − coarse D, one per mapping, with both
  natural/control refined-minus-coarse level changes.

Thus 4+2+2 = 8 records per context, 6,048 contrast records in total. Any missing
constituent produces a null contrast; a missing quantile is never zero. Arithmetic
contrasts of descriptor quantiles do not pair events or estimate confidence
bounds. Quantiles are calculated separately for each completed-survivor scenario,
without averaging across repetitions. Overflow is excluded from survivor p99;
loss plus late/generated retains both components and their generated denominator.
Assigned service means describe synthetic lookup sequences, not pooled physical
cost distributions.

Occupancy rows are keyed `(scenario_id,m)` with selected k, compact vector ID,
point class code, batches/useful events/busy ns, exact/mapped status, source
actual/model rows, modeled work and signed k−m work differences. Code 0 means
remeasured_reference, 1 new_selected_point. Each anchor row includes unused
eligible anchors, original vector/order identities, 20 pair-index counts,
wrap/remainder, unused indices and exact duration dot products. The vector-ID map
in the public summary binds candidate/repetition/B/k, wrapper/class, actual/model
rows and all192integer/order fingerprints. Original integer pairs and pair IDs
remain in the ignored accepted owned summary and unchanged Task0047 pair table. Lookup use never creates measurements.

Ordered verification streams the four CSVs together, keeping only the current
scenario histogram and eight-result contrast context. It reconciles useful and
modeled rows; full/partial, exact/mapped and new/reference use; every anchor's
cursor/dot product; support-specific source-use totals; trace IDs; all contrasts;
and B1/refined-B8 numerical controls. Independently constructed all-full fixtures
compare queue outcomes and executed assignments separately from legitimately
different eligible/unused-anchor provenance.

## Bounded representation and custody

Parent source custody uses 64 KiB byte chunks and fixed pins; full source
aggregate/chronology parsing belongs to the simulation worker. The parsed-source
ceiling is 128 MiB. Live deep container sizes and conservative temporary margins
are checked; parsing temporaries are released before queue work. Retained paired
lookup structures, metadata, counts and current-assignment margin fit 2 MiB;
traces fit 16 MiB. Only current-scenario latency/wait/batch-size arrays (each at
most 5,000 entries), FIFO (at most 1,024), occupancy histogram (at most 128) and
anchor counts (at most 260) persist during that scenario.

Row ceilings are 291,168 occupancies and exactly 39,744 anchors: 27,216 refined
plus 12,528 coarse. These do not grant unlimited output bytes. Serialization
checks row length and file/combined growth before writing: scenario 4 KiB,
contrast 16 KiB, occupancy 256 B, anchor 512 B, with a separately bounded first
header; file ceilings 12/32/32/16 MiB. Combined CSVs have a 56 MiB ceiling, leaving
64 MiB for combined guard journals and 8 MiB for other owned output inside the
unchanged 128 MiB total. Continuous storage checks also cover generated native
fixtures' source inputs. Reporting reads hash-bound accepted predecessor files
without redundant aggregate copies; it retains only bounded plotting coordinates.
No event/dispatch/latency row export is produced.

Worker RSS is capped at 1 GiB, native reserved at 512 MiB and controller RSS at
128 MiB, including continuous controller checks. These sampled quantities are
reported separately from derived Python/representation bounds. Continuous time
includes suspension. Prerequisite custody is capped at 30 s, simulation through
normal exit/reaping at 120 s, reporting at 60 s, finalization at 15 s and whole
session at 240 s; 2 s cleanup slack stays inside worker caps. CRITICAL pressure or
invalid primary accounting veto; WARN is advisory. Optional context and query/
terminal gaps are explicit. An owned temporary idle-system-sleep assertion must
be active during stages then released, reaped and confirmed absent; display sleep
is permitted. No persistent settings, global RAM floor, cache purge or app closure.

## Interpretation

Finite warm-window costs are transported to synthetic input/cache histories and
manufactured cycles. Even k=m, including complete refined B8 lookup, does not
reproduce physical streaming inputs, cache history or measurement order. The two
mappings are hypotheses; neither is a measured bound and their spread need not
contain reality. Source pairing at lookup does not physically pair jobs or
survivors after queues/cursors diverge.

A support change can alter the selected natural and control cases, sample phases
and subsequent queue histories. Both level changes are therefore published;
interactions do not isolate a causal benefit from adding measurements. Task0046
outcomes are not subtracted and its historical 91.1% selection coverage is not
used as this replay's exact-point fraction. New/reference subgroup usage is
accounting, not a counterfactual experiment.

No interpolation, empirical service envelope, universal service distribution,
production p99, causal component effect, p-value/confidence interval, independence
of source repetitions, scientific confirmation or deployment policy follows.
Simulation wall time is not physical trigger latency. Transport/detector arrivals
and an independent signal source remain unresolved. Task0048 adds zero operational
raw/feature/membership/golden/scientific-score/event-fingerprint loads, HDF/raw
custody, models/reconstruction/optimizers/calibration/scientific metrics,
downloads and physical timing. Artifact-free legacy model/optimizer fixtures are
separately positive work, without a global-zero claim. Permanent YES/YES/YES and
all historical accepted/consumed/failed/unresolved states remain unchanged.

## Fresh software evidence

Focused fixtures cover every support/mapping occupancy, pair preservation,
case-specific controls, cursor independence/reset/wrap, signed modeled deficits,
B1/refined-B8/all-full controls, independent FIFO/tie/overflow/timeout/drain
examples, all eight contrast signs/nulls/denominators, compact ordered joins and
tampering, exact producer serialization, source identity/type/chronology failures,
and real producer→serialized admission→immutable freeze/claim→worker rejection.
The live-container check traverses dataclass payloads, including trace tuples.
A continuous controller guard enforces its own 128 MiB ceiling. Foreign fixture
namespaces are rejected before writes; Boolean dispatch claims are rejected.

Full and portable acceptance use complete disjoint test-file partitions in an
artifact-free copy, each subprocess bounded at 240 s. The strict outer reader
checks every exit, hash-bound XML terminal result, zero errors/failures/skips and
complete unique file coverage. Static checks and dependencies also pass before
an accepted generated native bootstrap can supply software evidence. The final
immutable emitted record must itself pass an admitted generated native run and a
noncircular roundtrip receipt. Old Task0047 physical-chain tests do not accept the
new engine, and no historical acceptance is reused.

Historical regressions require eleven explicitly allowlisted frozen aggregate or
identity metadata files; the initially proposed three-file subset failed their
fixture contracts and was corrected before final acceptance. The Task0045 summary is used for historical byte-identity
checks; no Task0045 timing vectors are parsed or assigned. Original timing pair/
cell CSVs and timing JSONLs are absent from the final copied fixture context.
Task0047 config/prompt code-context copies and these eleven references have a
separate before/after byte-copy journal. Earlier broader copies, incomplete or
superseded software checks, the software-suite timeout, missing-reference fixture
failure and the sandboxed native process-accounting failure remain recorded in
the handoff; they are not operational source sweeps. No dependency is installed
or updated, and no hosted CI result is claimed.


## Accepted current-source results

The final source session `b1815dee77c5462d889d5fc4e15db3c7` starts/completes6048
scenarios and30,240,000presentations, with27,544,586completed survivors,
2,695,414overflow drops,6,067,628late survivors and final pending0.
There are7,896,652dispatch sample assignments; repeated lookup never adds source
measurements. Each variant has756contexts and3,780,000generated presentations.
These grid sums are engineering summaries of repeated synthetic inputs.

| Current support / mapping | Natural overflow | Control overflow | D overflow | Natural late | Control late | D late |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| coarse / next | 381281 | 380877 | +404 | 852814 | 875117 | −22303 |
| coarse / previous | 190168 | 380640 | −190472 | 409071 | 859155 | −450084 |
| refined / next | 380777 | 380832 | −55 | 852258 | 873972 | −21714 |
| refined / previous | 220090 | 380749 | −160659 | 472767 | 872474 | −399707 |

Aggregate cancellation hides unfavorable contexts. Refined next has77positive,
174negative and505zero overflow contrasts, with individual D from−102to+375events;
late D has171positive/225negative/360zero and ranges−1059to+754. Refined previous
has32positive overflow and110positive late contrasts. Refined survivor-p99 D ranges
−108.508…+231.352ms(next),−453.741…+16.022ms(previous), without averaged quantiles.
The refined mapping interaction sums−160604overflow/−377993late; neither mapping
is a physical bound or a policy recommendation.

| Refined − coarse within mapping | Natural overflow level | Control overflow level | Support D interaction | Natural late level | Control late level | Support D interaction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| next | −504 | −45 | −459 | −556 | −1145 | +589 |
| previous | +29922 | +109 | +29813 | +63696 | +13319 | +50377 |

Control levels change as well as natural levels. Summed assigned busy changes
are−429.612499s natural/+0.295364s control(next) and+206.020397s natural/
+3.387494s control(previous), across the same756contexts. These are changes in
synthetic assigned busy time, not newly measured execution time. Support
interactions of survivor-p99 range−32.628…+13.624ms(next) and
−386.314…+419.229ms(previous); they are arithmetic descriptor sensitivities.

| Support / mapping / billing | Mapped batches / all batches | Mapped events / completed | Mapped busy / assigned busy | Modeled rows minus completed |
| --- | ---: | ---: | ---: | ---: |
| coarse / next / natural | 10.1298% | 26.1459% | 44.1473% | +1232479 |
| coarse / next / control | 13.4686% | 32.3013% | 56.6702% | +3775478 |
| coarse / previous / natural | 23.2733% | 52.2386% | 32.2416% | −1098737 |
| coarse / previous / control | 13.6244% | 32.5306% | 56.7839% | +3833345 |
| refined / next / natural | 0.7443% | 9.1235% | 10.6613% | +104609 |
| refined / next / control | 3.0517% | 19.1196% | 31.5834% | +3780793 |
| refined / previous / natural | 3.7612% | 27.3306% | 15.2802% | −473944 |
| refined / previous / control | 3.0598% | 19.2371% | 31.6024% | +3771366 |

Exact fractions are the complements, with their actual batch/completed/busy
denominators in the summary and scenario rows. Surplus and deficit are also
reported separately. New selected anchors bill515977/1060580useful natural events
(next/previous),449298/776004control events; subgroup use is not a counterfactual
cost distribution. Common current reference vectors remain identical.

Changed history creates residual occupancies absent from the matched coarse
scenario even though support has grown. These are context-local appearances,
not previously unobserved points globally or new physical measurements:

| Mapping / billing | Contexts with new residual m / 756 | Such batches | Such useful events | Such assigned busy ns |
| --- | ---: | ---: | ---: | ---: |
| next / natural | 143 | 493 | 28808 | 15990157528 |
| next / control | 114 | 223 | 9395 | 8705324108 |
| previous / natural | 137 | 21201 | 382135 | 94227792556 |
| previous / control | 170 | 1186 | 53072 | 57750556347 |

Residual means `(B,m)` outside all32physically measured cases. Full context-local
union lists and source new/reference usage remain in the aggregate summary.
The new exact fractions were measured in this replay, without borrowing91.1%
from Task0046 selection coverage.

## Evidence, resources and curated outputs

Final software record `e66943af8eeb4315970f4ea16e7d0253` (SHA256
`30245db9d1a8e685e30519e44b8aaf20ae6fa8a1380f2739cda4358fc549b010`)
binds324source/config/prompt paths,43installed packages and36native/metadata files.
250focused checks and3591full+3591portable checks pass; full/portable partitions
are1730+1638+223tests, every exit0 and XML result hash-bound. Lint/format/pipcheck
pass. Final generated bootstrap71.420867s and emitted-record roundtrip75.160743s
both accept complete matrices, resources, exits and cleanup. Earlier failures and
superseded versions remain explicit in the Italian handoff. No install/update or
hosted CI result is claimed.

Actual source worker69.933625s/reporting3.631421s, prereq1.630978s/final0.541362s,
whole78.911485s; exit0/reaped/zeroovershoot, cleanup≤0.000202s. Nineteen active sleep
assertion observations, then release/reap/confirmed absence. Worker RSS peaks
120995840/174948352B, native60358656/113868800B; controller66961408B/native50331648B.
Conservative parent-plus-max-serial-worker native upper164200448B is not a global
RAM floor or simultaneous peak. Parsed source live containers41125773B, retained
paired lookup1563500B, traces6290173B; descriptor containers1165031B. These derived
container quantities differ from sampled RSS/native. Owned storage56527103B;
CSV payload25979114B, all caps unchanged. Guard journals/logs remain ignored.

Worker/report WARN55556,parentWARN2743; CRITICAL/invalid0. Query-start gap maxima
0.085897s simulation/0.325999s reporting/0.699812s parent; terminal unaccounted gaps
0.047682/0.103931s. Optional context is unknown/not observed; continuous clock/
exit supervision remains independent, without a gap-free claim or subtracting
guard time. These are shared-host engineering results.

Final source custody72opens/51714288B:24pre byte-only,24worker parsed,
24post byte-only. Only worker parses3JSONL/8832records; unique7680timed and1152
excluded warm durations,30720timed duplicate copies and1152warm copies. Reporting
and owned metadata curation open zero original sources and regenerate zero queues/
traces. Curation streams current-context occupancy sets, preserves all CSV/PNG
bytes and takes0.700s for the initial metadata/copy pass. All192ordered sequences,
detailed assertions/receipts/claims/logs remain ignored; public summary contains
fingerprints, aggregate lifecycle and engineering counts.

[Scenarios](../results/tables/final/task0048-refined-service-replay-scenarios.csv),
[contrasts](../results/tables/final/task0048-refined-service-replay-contrasts.csv),
[occupancies](../results/tables/final/task0048-refined-service-replay-occupancies.csv),
[anchor audit](../results/tables/final/task0048-refined-service-replay-anchor-audit.csv)
and [summary](../results/tables/final/task0048-refined-service-replay-summary.json)
are curated engineering metadata. The three inspected figures show
[current refined billing](../results/figures/final/task0048-refined-service-replay-outcomes.png),
[support interactions and both levels](../results/figures/final/task0048-refined-service-replay-support.png)
and [residual mapping/model-row dependence](../results/figures/final/task0048-refined-service-replay-residual.png).
All seeds/source repetitions and unfavorable/null effects remain; signed axes use
symlog0.01pp and the residual color scale is signed symlog with linear±1%.

Four generated native invocations include one pre-scenario sandbox failure and
three complete accepted fixture matrices (one preliminary, two final):90.72M
presentations/54trace generations. One actual-source matrix adds30.24M/18. The
same90kPCG64positions repeat; they are not additional acquired events. Five
persisted instrumented legacy subsets report340model instances/124forwards and
reconstructions34840rows/8completed toy optimizer steps/8synthetic calibrations;
one subset is zero after fixture setup failure. Two interrupted full invocations
lack terminal counters, and other historical fixtures are outside that subset:
positive legacy activity is not globally zero. The new replay runs zero models.

The next bounded decision needs a separate scope for residual-occupancy or
streaming/cache/transport evidence. It does not select a deployment policy, renew
any consumed allowance, acquire data, alter scientific gates or start Task0049.
