# Targeted partial-occupancy raw-to-decision measurement — Task0047

## Contract and exploratory selection

Task0047 authorizes one new physical development-only CPU campaign after fresh
software acceptance, emitted-record native roundtrip and immutable freeze. The
[actual prompt](prompts/0047-targeted-partial-raw-decision-measurement.md) and
[closed config](../configs/benchmarks/development_targeted_raw_decision_v1.json)
fix 32 cases before numerical access. All 15 Task0045 reference points are freshly
remeasured with the same new wrapper as the 17 targeted points; historical and
current observations cannot be mixed into one matrix.

| Nominal B | Current m | New points |
| --- | --- | --- |
| 1 | 1 | none |
| 8 | 1–8 | 3, 4, 5, 6 |
| 32 | 1–8, 31, 32 | 3, 4, 5, 6, 7 |
| 128 | 1–10, 32, 127, 128 | 3–10 |

A stdlib-only reader validates the closed ten-file Task0046 metadata bundle,
5,382,736 bytes: config/prompt/curated summary/scenarios/occupancies and accepted
plan/workflow/parent/two worker receipts. Safe relative paths, exact hashes/sizes,
strict JSON/CSV, complete scenario/occupancy reconciliation and normal exit,
reaping and sleep-assertion release are required. Embedded paths are inert;
selection never invokes the Task0046 engine or a physical adapter.

The ranking uses only historical `next_anchor/natural_anchor` dispatch counts,
excluding the 15 exact anchors, descending count then ascending m. The prescribed
17 points cover 99,405/109,080 missing dispatches, 556,462/896,210 associated
completed events, and 677,757,505,837/860,108,214,675 assigned ns: 91.1304%, 62.0906%
and 78.7991%. Busy coverage uses hypothetical assigned costs. This is exploratory
selection from a synthetic replay, not an independent confirmation or production
workload distribution. 137 of 169 possible nominal-B/m combinations remain
unmeasured; zero historical frequency does not make a point measured.

## Physical boundary and unchanged arithmetic

Both sides independently select approved IDs from the original HDF source at
B-based starts 0, floor((1024−B)/2), 1024−B. Natural reads m rows and full control
reads B real rows, retaining all B outputs. The three original membership/golden
loads approve the same 1024 IDs and request exactly the historical 384 raw-row
union. No preloaded full buffer, partial slicing, padding, dummy events, m-based
recentering or extra population is used.

Frozen canonical FP64 sort/wrap precedes physical FP32 conversion; all valid
particles contribute FP64 aggregates before any 384 truncation. Original mass,
log and scaler rules produce final FP32 features. Column2100 checks background
role and stays outside features. Models remain original six-component FP64 PCA
and 155-parameter FP32 CPU AE v2, eight ordered channels, public FP64 SSE and four
strict `score > threshold` decisions. No fitting, store/scaler construction,
optimizer, calibration or scientific evaluation is authorized.

A separate closed Task0047 wrapper validates `(B,m,side)` and actual shape,
allocates/copies one owned C-order FP32 `(actual,8)` buffer, calls the unchanged
public score once and returns owned score/decision copies. Model shape is actual
m or B; no historical service_B argument is manufactured. Task0038/0045 guards
and mappings remain byte preserved. Generated fixtures compare all 15 references
against their historical helper arguments (including quarter service_B8/32) and
all 17 new points against an independent same-shaped public-score/strict-decision
reference. Current PCA code is freshly bound; commit4658fc4 changed fitting-time
contiguity only. Task0047 loads the frozen artifact and never fits it. Superseded
acceptance maps remain immutable historical documents, not live acceptance.

Each same-shaped pre/post gate runs one golden-only service and two independent
complete chains per side. Features/golden, score/decision/repeat/pre/post bytes and
parameter/threshold/input identities must match exactly. Cross-shape bytes are
not an oracle. Full occupancy is equal intended work with separate noisy timings.

## Schedule, budgets and supervision

Three fresh workers each load both candidates once. Workers1/3 use PCA→AE and
ascending cases; worker2 AE→PCA and reverse cases. Per candidate/case: three warm
pairs then20 timed pairs, phase-reset window i mod3, natural first on even i and
control first on odd i. Warm windows1/1/1; timed7/7/6; timed order10/10. Timer starts
immediately before checked selected read and ends after packing/public score/four
decisions/result copies. Loads, queries, hashes, references, durable accounting
and retained-feature parity checks are outside the timer.

Planned complete totals (actual values are established only by parent acceptance):
384 cells/192 groups/3840 timed pairs; timed7680 calls303240 rows; warm1152/45486;
chain gates4608/181944; raw reads/features/chain services13440/530670 each;
golden references2304/90972; public services15744/621642, Boolean values2486568.
Per worker4480 reads/features176890 rows,768 references30324 rows,5248 services
207214 rows; per candidate7872 services310821 rows. Three membership loads20997
records/3072 selected, three golden loads3072 rows/1024 unique, six frozen model/
threshold instances, three HDF handles/six same-handle checks, two full SHA256 raw
passes5816520818 byte presentations. Nested intent/started/returned/completed/
inflight journals preserve actual progress on failure.

Continuous clock includes suspension and supervises exit independently of sampled
queries. Caps are prereq60s, three workers180s each through exit/reaping, report60s,
post custody45s, final15s, reserved720s/whole780s, cleanup2s within worker caps.
WorkerRSS1GiB/native512MiB/controller128MiB; owned arrays64MiB; journals16MiB per
process/64MiB session; logs1MiB; output128MiB. Selection payload8MiB and parsed
Python48MiB are separate bounds. Reference/window/request accounting retains
344200 bytes conservatively; particle scratch bound uses24 arrays of128×700×3
FP64 plus raw rows and2MiB model/result margin, below64MiB. No raw buffers are
retained between calls. Python/container envelope is separate: per numerical worker at most2944 side
records,768 gate records,1280 paired records,128 cells with20 integers each,384
reference hashes and192 request/window contexts. A conservative32MiB Python
container/serialization envelope covers these dictionaries/lists and temporary
JSON copies; it is not an extra array allowance. Reporting retains three bounded
aggregates (at most4MiB serialized each), approximately48MiB parsed envelopes,
16MiB summary/statistics workspace and a conservative256MiB plotting allowance,
all within its RSS/native caps. The stdlib parent accepts one worker aggregate at
a time and never retains numerical payloads. Selected-source parsing is released
before dispatch. Source8MiB/parsed48MiB, these derived envelopes, sampled RSS and
native reservation estimates are distinct quantities. Journal appends and timing
record appends check combined16MiB before growth with64KiB guard headroom;
independent storage monitoring verifies16MiB/process,64MiB/session and128MiB total.
Native reservations use parent plus one serial worker, not a global RAM floor.

One readonly HDF handle per worker is checked before/after both candidates:
FP64[1100000,2101], chunks[62,2101], exact Blosc32001 filter/hardlinks/schema,
persistent1MiB/521/.75 cache. Geometry is derived from13440 requests; it is not
measured I/O, decompression or cache misses. BLOSC_NTHREADS=1 is requested;
effective decoder threading remains unknown. Torch intra/inter1, deterministic
CPU and supported BLAS/OpenMP/Accelerate limits are checked; owned state is
restored and fresh process teardown owns interop lifetime. Temporary owned
idle-system-sleep assertion must be active, released/reaped/absent before
acceptance. WARN advisory; CRITICAL/invalid primary accounting veto. Optional
unknown context and sampling/query/terminal gaps are reported.

## Outcome

One session `4b1ae2522d114b47a56a89abccd9918d` is
**parent_accepted_targeted_partial_raw_decision_measurement**; its allowance is
consumed. Whole320.220989s/reserved316.507656s, all four exit0/normal/reaped,
zero overshoot, all counts above completed exactly, no inflight uncertainty.
The final raw SHA equals the original before SHA. All2304 side gates pass exact
same-shaped feature/score/decision parity and pre/post identity.

[Selection169rows](../results/tables/final/task0047-targeted-partial-selection.csv),
[384cells](../results/tables/final/task0047-targeted-partial-raw-decision-cells.csv),
[3840pairs](../results/tables/final/task0047-targeted-partial-raw-decision-pairs.csv),
[summary](../results/tables/final/task0047-targeted-partial-raw-decision-summary.json)
and [Italian handoff](handoffs/0047-targeted-partial-raw-decision-measurement.md)
retain the accepted current matrix, all slow/unfavorable observations and provenance.
Every cell has20 timed observations recoverable from its matched pair rows;
owned aggregates retain the ordered observation lists. Each of192 paired groups
has20 signed differences/ratios. Pooled current cells use60 actual observations
within the same candidate/B/m/side. Linear p50/p95/p99 and population SD are
computed from observations; percentiles are not averaged.

The table shows current means over60 observations per side and the mean of60
matched ratios within each candidate/B/m. Ratios are not ratios of means.

| B/m | Class | PCA natural/control ms | PCA mean paired ratio | AE natural/control ms | AE mean paired ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| 8/3 | new | 1.261 / 3.229 | .3888 | 1.277 / 3.194 | .3988 |
| 8/6 | new | 2.600 / 3.319 | .7785 | 2.480 / 3.247 | .7658 |
| 32/3 | new | 1.315 / 12.154 | .1077 | 1.297 / 11.988 | .1080 |
| 32/7 | new | 2.884 / 12.218 | .2357 | 2.846 / 12.031 | .2364 |
| 128/3 | new | 1.531 / 49.472 | .0309 | 1.560 / 48.096 | .0324 |
| 128/10 | new | 4.455 / 49.077 | .0909 | 4.556 / 50.594 | .0907 |
| 128/32 | remeasured | 12.792 / 48.889 | .2612 | 13.229 / 49.933 | .2649 |
| 128/128 | remeasured/null | 48.611 / 48.722 | .9990 | 52.015 / 50.050 | 1.0170 |

333/3840 pairs have natural−control>0:332 remeasured-reference and1 new point.
The new unfavorable pair is worker3/PCA/8/6/pair14/natural-first:8.100041 versus
4.170292ms, difference+3.929749ms, ratio1.942320. All480 equal-intended full-
occupancy pairs remain:231 positive/249 negative, no enforced equality. Across
all observed pairs the signed extremes are−104.921667…+113.213792ms; maximum
observed side call226.994042ms is retained. These are observed extrema and
counts, not a pooled cost distribution across cases or universal bounds.
At B1 the paired-ratio means1.74095(PCA)/1.65901(AE) coexist with nearly equal
side means: matched order/host context matters, and averaging ratios is different
from dividing means. No component cause is identified.

Three figures were inspected both on generated native fixtures and on accepted
owned real results: [joint costs](../results/figures/final/task0047-targeted-partial-joint-cost.png),
[all signed pairs/ratios](../results/figures/final/task0047-targeted-partial-paired-cost.png),
[historical selection coverage/residual gaps](../results/figures/final/task0047-targeted-partial-selection-coverage.png).
Discrete points, explicit ms/log/symlog units, worker/order markers and unfavorable/
null values are retained. No physical rerun or figure regeneration was required.

## Fresh validation, actual resources and metadata accounting

Final record `data/task0047-validation/c754adabdcb243968fcec137ce85d501/software-acceptance.json`:
297 focused,3368 full,3368 portable in copies without operational data/artifacts;
lint/format/dependencies pass.332 current source/config/prompt bindings,43 installed
packages,41 native file pins plus canonical JSON-string Torch build identity.
Generated bootstrap146.179467s and actual admitted emitted-record roundtrip
152.154486s both pass all384 cells/counts/gates/cleanup/reporting before real freeze.
No old acceptance is borrowed, no install/update or hosted CI is claimed.

Preserved software failures: initial test collection from direct pytest invocation
(2 collection errors/no tests); copied fixture status mismatch18failed/171passed;
copied scope assertion1failed/295passed; final-v1 generated resource-guard fixture
1failed/296passed. Final-v1 stops before full/native/freezing; no physical allowance
is consumed by these generated tests. Final-v2 fixes that fixture while retaining
the actual early controller memory guard. There are two actual native fixture
integrations and no new native fixture failure. Historical Task0045/0046 failures
are unchanged. Owned-only curation removed inappropriate cross-case cost means;
it retains category counts/extrema and separate per-case distributions, with the
prepublication draft preserved ignored. No measurement/source/code was changed.

Native generated matrices execute31488 public services1243284 rows,26880 governed
raw/feature calls1061340 rows, plus48 setup raw/feature calls6144 rows;12 creator
and12 loaded models,12 threshold loads. Six dedicated public-model fixture suites
execute1536 public scores60648 rows,12 creator+12 loaded models; six complete toy
worker-plan tests execute31488 toy public calls1243284 rows (a subset, other direct
toy calls remain separate). Two instrumented legacy subsets report170 model
instances/62 forwards-reconstructions17420 rows/4 optimizer steps completed and
4 synthetic calibrations; unrelated historical fixtures are outside this subset.
This positive fixture work is not operational work and is not globally zero.

Actual worker RSS peaks372293632/378847232/336986112/report152616960B; maximum
native reserved203276288B; controller114425856B, native69386240B. Parent-plus-one-
serial-worker native upper272662528B, a conservative sampled convention, not a
simultaneous/global RAM measure. Numerical bound56202376B, retained request/window/
golden/ID344200B. Owned storage60127622B; worker combined journals13010678/
13013749/13030209B, total including parent/report47161270B, within all caps.

Dispatch-through-reaping97.252629/97.289772/99.083146/report11.797523s;
prereq3.810659/postcustody1.302670/final2.173606s. Cleanup≤.000371s.
65 active sleep-assertion observations; release/reaping/confirmed absence before
parent acceptance. Worker/report WARN21279, parentWARN16958, CRITICAL/invalid0;
WARN remains advisory and all costs are conditional on this host context.
Worker query-start gap maxima.124929/.087107/.094395/report.119805s,
parent.088607s; terminal resource gaps.305962/.348168/.300728/report.075569s.
Continuous exit supervision remains independent. Optional context is unknown/
not observed; no gap-free monitoring claim or guard-time subtraction.

Selection bundle preparation:2 complete byte loads/20 opens10765472B, one semantic
load3024scenario/18629occupancy rows. Session:pre semantic10opens5382736B plus final
byte-only10opens5382736B; final parses0CSV records. Broader tracked-file byte-
preservation/code/config/docs inspections are separate. Selection reader never
calls a queue engine or dereferences embedded raw/event/model paths.
Geometry derives13440 requests,312 distinct chunks and repeated no-cache decode
upper451886172672B; it is geometry, not measured physical I/O/decode/cache misses.

## Interpretation and preserved history

Costs include different selected rows, feature work, model shapes and all real
full-control outputs; differences cannot isolate disk/decoder/packing/model
causes. Natural amortization uses m physical rows; full physical amortization B;
full cost/m is explicitly hypothetical useful-event billing. Every slow,
unfavorable and null observation is retained. Percentiles use actual observations
within current candidate/B/m/side; no averaging percentiles, fitting, interpolation,
monotonicity, universal bound, productionp99 or policy recommendation.

The warm paired windows, gates, hashes and persistent cache do not reproduce cold
I/O or partial-only streaming histories. Task0045/0046 are historical context;
no pooling, campaign subtraction, automatic queue replay or Task0048. Residual
occupancies, streaming/transport/detector workloads and independent signal source
remain unresolved. Scientific gates, permanentYES/YES/YES, Task0036unresolved,
Task0041failed/consumed, Task0042software-only, Task0043/0045/0046accepted/consumed,
Task0044accepted replay, Task0025failure and particle192/192 remain unchanged.
