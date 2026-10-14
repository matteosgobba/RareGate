# Paired natural-partial raw-to-decision measurement — Task0045

## Prospective contract

Task0045 supplies a new physical engineering boundary: selected approved raw rows,
unchanged frozen aggregate features, owned natural CPU packing, the original public
score and four strict decisions, then result copies. It compares `natural_m` with
a contemporaneous `full_B_control` that processes and retains all B real rows.
Neither side pads. This is one separately authorized campaign, not a retry or
amendment of Task0043, Task0041, or Task0044.

The [actual prompt](prompts/0045-natural-partial-raw-decision-measurement.md) and
[strict config](../configs/benchmarks/development_partial_raw_decision_v1.json)
fix fifteen cases before access:

| Nominal B | Actual natural m | Natural service_B |
| --- | --- | --- |
| 1 | 1 | 1 |
| 8 | 1, 2, 7, 8 | 8 |
| 32 | 1, 2, 8, 31, 32 | 32, except m=8 uses 8 |
| 128 | 1, 2, 32, 127, 128 | 128, except m=32 uses 32 |

The two explicit quarter mappings call the already supported natural `(8,8)` and
`(32,32)` helpers. Nominal B defines the containing window; actual m defines the
allocated/copied/processed natural rows. The original Task0038 case validator and
packing implementation remain unchanged. Control service_B and actual rows are B.
For each B, both sides use starts `0`, `floor((1024-B)/2)`, `1024-B`. Each side
selects its own exact approved ID prefix from HDF; partial windows are never
recentered or sliced from an already read full raw buffer.

Workers 1/3 run PCA then AE and ascending cases; worker 2 reverses both lists.
Each candidate/case has three warm-up pairs and twenty timed pairs. Window and
order cycles restart for each phase: pair i uses window i mod 3, natural first on
even i and control first on odd i. Timed order is 10/10; windows are 7/7/6.
Before and after each candidate, ascending case/window/side gates run one
same-shaped golden natural service plus two complete chain calls. Feature bytes
must equal golden bytes, and score/mask/repeat bytes must equal that side's
same-shaped reference. Post references and numerical parameters/thresholds must
match pre. Cross-shape score identity is not required or used as an oracle.

The timer starts immediately before the checked selected read and ends after
natural service result copies. File/model loads, preparing approved ID requests,
hashes/parity, durable accounting and explicit guard/thread queries are outside
the timer. Computed features are retained only for the after-timer comparison,
without recomputation or a second standardization.

## Source and arithmetic custody

All Task0039/0040/0043 identities, roles and scientific lineage remain fixed.
The original C-order little-endian int64[6999] membership file is loaded once per
worker and resolved by the accepted domain/uniqueness/sorted-prefix resolver.
Exactly 1024 IDs are approved, with payload SHA256
`f80a9483f5ddafcac0e05d9fd6de757e5bbfe9e805f65ced1c0aa801cc266f1a`.
The union of requested positions is exactly the same three B128 windows as
Task0043, hence the same 384 unique raw rows. The original FP32[1024,8] golden is
loaded once per worker; Task0020's successful preparation is reused while its
overall campaign remains failed.

The two original model entries from `prepared_batch_service_v1.json` bind file,
config, result, scientific and training/calibration provenance hashes, and eight
ordered features. PCA remains six-component FP64; AE v2 remains 155-parameter FP32
CPU in eval/inference mode. Public SSE remains FP64 and all four comparisons are
strict `score > threshold`. Each candidate/threshold set is loaded once per fresh
worker; no pickle, fitting, backend substitution or threshold recalculation.

Features use unchanged `canonicalize` → `physical_aggregates` →
`standardized_aggregates` with frozen Parameters: source FP64 sorting/wrapping,
all valid particles in FP64 aggregates before any 384 truncation, exact mass/log/
scaler rules and final FP32. Background label column 2100 validates role and
stays outside features. No particle view, ProcessedStore or scaler construction.

Exactly two complete raw SHA256 passes are reserved, before numerical access and
after numerical/reporting work: 5,816,520,818 byte presentations. Three read-only
HDF handles span both candidates and both pre/post metadata checks, then close;
no fourth metadata-only opening. Dataset `/df/block0_values` remains
FP64[1100000,2101], chunks[62,2101], exact Blosc32001 pipeline. Each persistent
handle uses 1MiB/521slots/w0=.75 cache. Decoder threading remains unknown.

## Admission, resources and interpretation limits

Task0045 has its own closed provider, permits, producer, serialized outer admission,
immutable freeze/claim, controller and independent worker checks. Old namespace,
owner, globals and budgets are not widened. Generated fixtures are the only
numerical source during software validation. Final acceptance binds actual prompt,
config, sources/tests, installed package/native NumPy/HDF/Blosc/Torch identities,
and canonical JSON-string Torch build identity. A generated bootstrap supplies
native evidence; the emitted immutable record must then pass admitted native
roundtrip with a noncircular sidecar before operational freezing.

The actual prompt authorizes one conditional operational session; its first real
prerequisite consumes the allowance even on failure. No retry, changed inputs,
tolerance repair, diagnostic model passes or second physical campaign is allowed.
Fixed continuous ceilings are prerequisites60s, three workers180s each through
exit/reaping, report60s, postcustody45s, finalization15s, reserved720s, whole780s.
Cleanup2s is inside each worker cap. Limits are workerRSS1GiB, native512MiB,
controllerRSS128MiB, owned numerical arrays64MiB, combined journals16MiB/process
and64MiB/session, worker log1MiB, owned output128MiB. Derived numerical-array
bounds are distinct from sampled RSS/native allocation and the conservative
parent-plus-one-serial-worker native convention.

Environment is set before numerical imports; Torch intra/inter=1, deterministic
CPU, original BLAS/OpenMP/Accelerate limits, requested BLOSC_NTHREADS=1. A temporary
owned idle-system-sleep assertion is checked during stages, released/reaped and
confirmed absent before acceptance; display sleep remains allowed. Resources and
owned state are restored on exit; fresh process teardown owns one-time interop.
WARN is advisory, CRITICAL/invalid primary vetoes. Optional unknown context,
query gaps and terminal gaps must be reported, not treated as continuous sampling.

Difference is `natural_m - full_B_control`; ratio is `natural_m/full_B_control`
from each matched pair. Natural amortization uses actual m. Control physical cost
uses B; control bill/m is only a hypothetical useful-event allocation. At m=B,
both sides perform identical intended work and deviations expose finite ordering/
host effects, without requiring durations to agree.

Quarter points are sparse exploratory engineering anchors informed by Task0044,
not every occupancy or independent scientific confirmation. Prehash, gates,
alternation and repeated sparse windows warm the context; they do not reproduce
partial-only streaming cache history or cold I/O. Control extra B-m rows are real
work. The contrast includes raw selection/features/model shape differences and
cannot isolate disk, decoding, packing or model causality. Chunk geometry is not
physical I/O, decompression, cache misses, effective decoder threading or a
universal upper bound. All workers/calls/slow observations are retained; there is
no subtraction, trimming, fitted/interpolated cost curve or policy selection.

Task0043 full costs and Task0044 hypothetical bills remain historical. This task
does not rewrite/replay them, measure arrivals/queues/transport or confirm a
signal source. A separately authorized future replay must prescribe every
unmeasured occupancy and changed cache/input assumptions. Scientific gates,
YES/YES/YES exposure, Task0041failed/consumed, Task0042software-only,
Task0036unresolved and particle192/canonical-deferred remain unchanged.

## Actual outcome and complete observations

Status **parent_accepted_natural_partial_raw_decision_measurement**. The sole
operational session `1872bdaa920f49598ec8eafcf4ea3c08` is accepted and consumed;
there was no retry. Whole continuous164.220661s, reserved160.995997s,
prerequisites3.298504s, postcustody1.345023s, finalization2.149012s, overshoot0.
The whole clock covers the native controller after outer software admission/
freezing; no numerical source access precedes real prerequisites.

[Cells](../results/tables/final/task0045-natural-partial-raw-decision-cells.csv)
contains180 statistics rows,20observations per key. The
[pairs](../results/tables/final/task0045-natural-partial-raw-decision-pairs.csv)
table retains all1800matched pairs, both integer-ns durations, candidate/worker/
nominal B/m/actual rows/service_B/window/order/pair ID, signed difference and
ratio. Joining on candidate/repetition/B/m reconstructs every cell's20original
observations by side. No observation is trimmed. The
[summary](../results/tables/final/task0045-natural-partial-raw-decision-summary.json)
retains90per-worker paired groups and60pooled side distributions. Count/min/max/
mean/population SD/linear p50/p95/p99 use actual observations; percentiles are
never averaged. Warmup chronology, exact references, receipts, freezes and
journals remain ignored; raw/particles/features/scores/masks/event IDs are not
exported. Public source/config/threshold pins stay in the strict config.

Below, each mean pools60observations only within the same candidate/B/m/side.
Paired difference and ratio are computed first per pair, then averaged over that
same prescribed case; mean ratio is not the ratio of side means. These finite
conditional statistics are not a production p99 or a fitted occupancy curve.

### pca-v1

| B/m | Natural mean ms | Full mean ms | Mean paired difference ms | Mean paired ratio | Natural slower pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1/1 | 0.3731 | 0.3718 | 0.0013 | 1.8142 | 30/60 |
| 8/1 | 0.5798 | 3.0952 | -2.5154 | 0.1903 | 0/60 |
| 8/2 | 0.9538 | 3.2642 | -2.3104 | 0.2922 | 0/60 |
| 8/7 | 2.9739 | 3.2467 | -0.2728 | 0.9192 | 11/60 |
| 8/8 | 3.3709 | 3.2616 | 0.1092 | 1.0325 | 39/60 |
| 32/1 | 0.6024 | 12.0950 | -11.4927 | 0.0504 | 0/60 |
| 32/2 | 0.9586 | 12.3433 | -11.3848 | 0.0779 | 0/60 |
| 32/8 | 3.1698 | 12.1486 | -8.9788 | 0.2602 | 0/60 |
| 32/31 | 11.7584 | 12.1176 | -0.3592 | 0.9709 | 16/60 |
| 32/32 | 12.1719 | 12.2556 | -0.0838 | 0.9937 | 31/60 |
| 128/1 | 0.6391 | 48.1836 | -47.5445 | 0.0133 | 0/60 |
| 128/2 | 1.0376 | 49.4255 | -48.3879 | 0.0209 | 0/60 |
| 128/32 | 12.7916 | 48.6105 | -35.8189 | 0.2627 | 0/60 |
| 128/127 | 48.3465 | 48.6429 | -0.2964 | 0.9942 | 25/60 |
| 128/128 | 48.9151 | 50.8319 | -1.9168 | 0.9860 | 32/60 |

### compact-autoencoder-v2

| B/m | Natural mean ms | Full mean ms | Mean paired difference ms | Mean paired ratio | Natural slower pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1/1 | 0.4056 | 0.4036 | 0.0019 | 1.6709 | 30/60 |
| 8/1 | 0.6200 | 3.1328 | -2.5127 | 0.2007 | 0/60 |
| 8/2 | 0.9766 | 3.3027 | -2.3261 | 0.2965 | 0/60 |
| 8/7 | 3.0148 | 3.3836 | -0.3688 | 0.8961 | 6/60 |
| 8/8 | 3.4180 | 3.3845 | 0.0335 | 1.0118 | 29/60 |
| 32/1 | 0.6877 | 12.6082 | -11.9205 | 0.0551 | 0/60 |
| 32/2 | 1.0133 | 12.4488 | -11.4355 | 0.0815 | 0/60 |
| 32/8 | 3.3309 | 12.5523 | -9.2214 | 0.2643 | 0/60 |
| 32/31 | 11.9821 | 12.4790 | -0.4969 | 0.9633 | 14/60 |
| 32/32 | 12.8305 | 12.5484 | 0.2822 | 1.0217 | 32/60 |
| 128/1 | 0.7155 | 49.4528 | -48.7372 | 0.0145 | 0/60 |
| 128/2 | 1.1070 | 50.1273 | -49.0202 | 0.0220 | 0/60 |
| 128/32 | 13.2394 | 50.1811 | -36.9416 | 0.2634 | 0/60 |
| 128/127 | 49.9624 | 50.1862 | -0.2238 | 0.9960 | 28/60 |
| 128/128 | 50.6179 | 50.7874 | -0.1695 | 0.9977 | 28/60 |
At quarter occupancy, paired mean ratios are .2922/.2965 for PCA/AE at8/2,
.2602/.2643 at32/8, and .2627/.2634 at128/32. At128/32, natural means are
12.7916/13.2394ms versus48.6105/50.1811ms controls, with differences
−35.8189/−36.9416ms. These costs include all distinct physical work, not an
isolated model or decoder increment. For PCA128/32, natural cost/m is .399738ms,
control physical cost/B is .379770ms, and the hypothetical control bill/m is
1.519078ms. That last allocation does not describe32physical control rows.

All351natural-slower pairs are retained:100/1320true partial pairs and251/480null
m=B pairs. True partial differences span−58.505583…+3.430125ms, ratios
.010364…1.116384. Null differences span−100.614667…+5.497958ms, ratios
.263420…3.749211. Null1/1 pooled side means are close, while mean paired ratios
1.8142/1.6709 are asymmetric; finite side order/host effects and averaging ratios
matter. No equal-duration requirement, favorable-only selection or cache-cause
attribution is made. The slowest retained timed call is151.721125ms.

Three figures were visually inspected for readable labels, all workers/order
labels and visible slow/unfavorable observations:
[joint costs](../results/figures/final/task0045-natural-partial-raw-decision-joint-cost.png),
[signed differences/ratios](../results/figures/final/task0045-natural-partial-raw-decision-paired-cost.png),
[chronology](../results/figures/final/task0045-natural-partial-raw-decision-chronology.png).

## Actual access and parity accounting

All following are completed actual work, independently reconciled by the parent:

| Component | Calls | Actual row presentations |
| --- | ---: | ---: |
| Timed complete chains | 3600 | 145920 |
| Warm-up complete chains | 540 | 21888 |
| Pre/post chain repeats | 2160 | 87552 |
| Selected reads / feature constructions, each | 6300 | 255360 |
| Golden-only references | 1080 | 43776 |
| Public score/four decisions services | 7380 | 299136 |

Three original membership loads inspect20997records from the same6999-record
source, selecting3072records/1024unique approved IDs. Three original golden
loads present3072rows/1024unique. Actual raw union384unique is separate from
255360repeated requested/returned/completed row presentations. All6300reads and
features complete, all7380services complete; inflight uncertainty is absent.
Natural-side raw work1050calls/26810rows per worker, control1050/58310; natural
services1230/31406, control1230/68306. Thus each worker totals2100reads/features
on85120rows,360references on14592rows,2460services on99712rows.

Six original model and threshold instantiations complete: three PCA and three
AE. Each candidate across workers has3690public computations on149568rows:
3690PCA reconstructions and3690AE forwards/reconstructions separately. All four
decisions yield1196544Boolean values. There are540paired gate contexts/
1080side gate records; feature/score/decision byte mismatches0/0/0 against each
same-shaped golden service, including repeat and pre/post identities. Every
warm/timed output passes the after-timer comparison. Inputs, Parameters, model
parameters and thresholds remain unchanged.

All three readonly HDF handles pass two schema/filter/hard-link/cache checks on
the same handle: six checks, three closes. Both rawSHApasses complete,
5816520818byte presentations, same original SHA256 before/after. No MD5,
preload, raw copy, source scan, padding, dummy event, ProcessedStore constructor,
optimizer/scaler/calibration/scientific/fingerprint/held-out/download/device/
transport/simulator work is added operationally. Authorized feature construction,
model inference/reconstruction and decisions are positive actual work above.

The6300-read geometric plan has312distinct source chunks and
217339541760B=202.413222GiB repeated no-cache decoded upper geometry. It is
re-derived from this paired plan, not copied from Task0043's840reads; physical
I/O/decompression/cache misses and decoder threads remain unmeasured.

## Fresh software validation and retained failures

Final record: `data/task0045-validation/c5d9634ddf0a4d7ca2050a79eb315739/software-acceptance.json`.
172focused,2921full and2921portable artifact-free tests pass, as do lint, format
and dependencies. It binds298source/metadata entries,43installed distributions,
41native file identities including TorchCPU/HDF/Blosc/NumPy, actual prompt/config,
paired scope/shape/packing/schedule/budgets and canonical JSON-string Torch build.
Final bootstrap102.746576s and actual emitted-record admitted roundtrip94.216284s
are each parent accepted, all180cells/paired gates/counters/normal exits/reaping/
assertion release. The sidecar does not modify or circularly certify its input
record. Operational freezing requires this roundtrip; old grants are rejected.

Five native fixture invocations are retained: one58.391436s complete-body
publication failure from a journal filename, one31.341330s partial rejection from
an atomic-temporary enumeration race, one944.558936s continuous deadline failure
(ordinary endpoint40.239327s, compatible with suspension), then the two final
accepted native matrices. The latter failure records incomplete timely reaping/
release; a separate later readonly confirmation observes all owned PIDs and the
assertion absent, without rewriting its original failure. Atomic transient
handling now reserves4MiB for a disappeared recognized JSON temporary and vetoes
unrecognized disappearance; all memory/storage caps remain fixed. These are
software evidence, not failed or retried operational source campaigns.

Durable fixture lower-known totals are26725reads/features on1090961rows,
31393completed public services on1279124rows,5116496Boolean values,28loaded
fixture model/threshold instances. One127-row golden reference remains inflight
in the suspended fixture evidence and is not added as completed. Fourteen setups
reach fixture model/golden loaders:112setup raw/feature calls on14336rows,
28fixture-creator model objects in addition to28loads,14write+14setup-read HDF
handles, zero setup forwards. Final dedicated unit suites each execute2498toy
public score services on100974rows, separately from native model forwards.
Six full/portable instrumented historical research subsets across the preserved
validation versions have510model instances,186forwards/reconstructions on52260rows,
12toy optimizer updates and12synthetic calibrations. Other unchanged legacy
fixture activity lies outside that instrumented subset; no global-zero fixture
model, numerical, forward or optimizer claim is made. An earlier focused
acceptance failure (165passed/5failed) and all source snapshots/logs are preserved.

## Actual lifecycle and resources

Numerical dispatch-through-reap durations57.226544/47.730071/45.177413s; bodies
56.677646/47.496017/44.907587s. Reporting dispatch5.561614s. All fourexit0,
normal exits independently confirmed/reaped, all worker cleanups below2s and no
guard latch. Max numerical lifetimeRSS404832256B; native reserved207470592B;
controllerRSS51265536B. Parent-plus-one-serial-worker native upper245219328B;
owned output26832267B. Explicit live-array bound55858176B includes the128-row
chain envelope and a2MiB reference/result/ID/scaler margin; retained approved
requests/golden windows/source ID/golden arrays186880B fit inside that margin.
No raw window buffers are retained. These are conservative allocation bounds,
not measured unique physical memory; sampled native/RSS accounting is separate.

Numerical primary pressure samples NORMAL6602/WARN3315/CRITICAL0/unknown0;
report65NORMAL; controller6370NORMAL/4632WARN, all advisory WARN retained.
Max worker query-start gap3.500353s and parent gap2.843063s; exit terminal gaps
.549615/.235053/.273158/.087250s are explicit. Resource sampling is not claimed
continuous through these gaps; independent continuous deadlines supervise exits.
Optional unavailable/unobserved context remains unknown and available RAM is no
admission floor. The assertion has35active observations, then release/helper
reaping/absence confirmed before acceptance. Environment/thread/determinism and
owned resources restore; one-time interop belongs to the reaped fresh process.
Display sleep permitted, no persistent setting/cache purge/app closure.

## Next decision

Task0045 closes the prescribed natural-partial physical boundary only. A future
separately authorized replay must version its treatment of every unmeasured m and
changed cache/input history; these sparse points do not rewrite Task0044 or select
a deployment/batching policy. No automatic Task0046, source acquisition,
scientific confirmation or changed particle gate follows. The detailed Italian
[handoff](handoffs/0045-natural-partial-raw-decision-measurement.md) records manual
Git delivery and preserves all historical states/exposure/failures.
