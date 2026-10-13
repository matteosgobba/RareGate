# Deterministic joint-service FIFO replay — Task0044

This bounded systems study uses the accepted, consumed Task0043 full natural
B-row raw-to-decision services. Its actual prompt authorizes a fixed synthetic
replay after fresh software acceptance and freezing. It authorizes no new raw
access, feature construction, model execution, physical timing or scientific
evaluation. Task0037's constant-cost engine and all historical protocols remain
unchanged. The accepted results and resource evidence appear below.

## Source custody and numerical boundary

The strict config binds 19 files in a 690,916-byte allowlist: original Task0043
config/prompt, curated summary/cells, fixed execution plan/workflow/parent receipt,
and three worker receipts, aggregates, timer contexts and timing JSONL files.
Paths, byte pins, source relationships, accepted scope, exact parity and original
normal exits/reaping/deadlines are checked. Embedded raw/model/array paths are
inert. Original software maps are checked only against their originally bound
entries; new Task0044 files do not invalidate historical completeness.

Each JSONL contains its complete ordered 184-record schedule: 24 warmups and
160 timed calls. Only timed records provide 24 separate immutable vectors, each
20 positive integer nanosecond durations. Ordinal/candidate/B/phase/call and the
logical window cycle must match exactly. Elapsed service is `elapsed_ns`;
continuous timer metadata and intercall gaps never generate service or arrivals.
Aggregate observation/order copies are exact. Statistics use linear quantiles and
population standard deviation; JSON/CSV binary64 copies may differ from stdlib
computations by at most 32 ULP, a mechanical serialization allowance, with no
empirical cost multiplier. All numerical timing copies are accounted separately.

## Dispatch and queue conventions

Every scenario resets j=0. A sample advances only when a batch dispatches,
including partial flush/drain batches. Cyclic uses q[j%20]; reverse uses
q[19-j%20]; rotation10 uses q[(j+10)%20]. Constant control charges
`(sum(q)+19)//20` nanoseconds per batch. Repetitions remain separate and no service
is interpolated between B values. Original-index assignment counts, cycles,
remainder, final cursor and assigned duration sums are checked.

One nonpreemptive FIFO server admits drop-tail while waiting plus actual
in-service events is below1024. Same-time order is completion, source-ordered
arrivals, dispatch/flush. Timeout is oldest waiting original arrival plus timeout;
final drain follows the same policy. Every admitted event completes, pending0.
Latency is combined dispatch wait plus that active batch's captured duration;
no independent queue/batching decomposition is claimed. Busy time sums assigned
batch durations, with a separate horizon-clipped sum.

Every partial m<B batch pays the chosen *full natural B* duration as an explicit
hypothetical bill. Useful events, charged/unused slots, utilization and partial
busy time are reported. No padding executes; this is neither measured natural-m
cost nor a universal bound on physical partial cost.

## Frozen workloads and contrasts

Unchanged `simulation.traces.generate` uses PCG64/SeedSequence
[3700,seed,mode_id,rate,stream_id], independent arrivals and Uniform[0,1) toy
scores. First arrival follows the first gap; periodic gaps are ceiled and Poisson
exponential gaps ceiled to at least1ns. Eighteen immutable traces contain5000
events each, modes periodic/Poisson, seeds41/42/43, rates500/2500/5000 input events/s.
Hashes/horizons/realized rates are retained. Both candidates, seven policies
(B1/0timeout; B8/32/128 at1ms/10ms), three service repetitions and cyclic/constant
produce1512 scenarios. Only Poisson2500/s adds252 reverse/rotation10 cases; main
cyclic baselines are reused. Total1764 scenarios/8,820,000 presentations,
756 cyclic-minus-constant and252 order-minus-cyclic contrasts.

The illustrative deadline is100ms, strict latency>deadline. Toy cuts
0.9/0.95/0.99/0.999 apply after completion solely for inherited conservation;
they are unrelated to original scientific thresholds/masks. Survivor latency
quantiles always retain completed and overflow denominators. Count contrasts are
integers; fraction/latency contrasts are deterministic conditional differences,
without confidence intervals, significance or production causality.

## Software and bounded lifecycle

Generated Task0043-shaped bundles replace all real source files in validation.
Independent hand timelines and a tick oracle cover variable costs; constant
providers match the unchanged Task0037 engine exactly, including toy decisions.
A Task0044 producer emits a serialized closed software record. Its outer verifier
checks owned logs/current source/dependencies and native fixture receipts. Final
source admission also requires the noncircular completed admitted fixture roundtrip.
Freeze and exclusive claim precede assertion/worker dispatch; altered or absent
records/freezes/claims block execution programmatically.

The controller stays stdlib-only. Numerical/reporting workers forbid model/raw
imports, event/model array paths, network and subprocesses. Only declared timing
provenance is readable during replay; reporting receives accepted aggregate CSVs
and compact JSON. At most5000 latency entries are retained per case and released
between cases. Rows are CSV-only, without a duplicated JSON matrix.

Continuous macOS time includes suspension. A verified temporary owned idle-system
assertion permits display sleep and changes no persistent settings. Resource
journals are sampled: WARN advisory, CRITICAL/invalid primary accounting veto.
Unknown optional context is disclosed, with no global RAM floor. Caps are30s
prerequisites,120s simulation through reaping,60s reporting,15s finalization,240s
whole, cleanup2s inside caps;1GiB worker RSS/512MiB native/128MiB controller RSS,
64MiB journals/1MiB logs/128MiB owned output,8MiB source bundle/1MiB services/
16MiB traces. Normal exits/reaping, output/source identity and assertion release
are necessary for parent acceptance. Numerical virtual time never sleeps arrivals.

## Interpretation and next decision

Costs are finite historical full-B observations from warm sparse HDF windows.
Cyclic reuse creates artificial20-batch periodicity and a wrap discontinuity.
Ordering preserves the source multiset, but different dispatch counts produce
finite prefixes with different assigned means. These inputs cannot reproduce the
original cache/load/decoder dependence or validate physical transport/backpressure.
Known Task0043 costs informed the fixed rates/deadline: prospective freezing
provides reproducibility, without independent scientific confirmation.

Startup, finite workloads, drain, survivor selection and partial billing limit
interpretation. No production distribution is fitted and no best deployment
policy or CERN throughput/latency requirement is inferred. A separate next decision
may scope measured natural partial raw-to-decision services or another missing
streaming/transport boundary. No Task0045 is implemented or launched. Task0043
remains accepted/consumed; Task0041 failed/consumed; Task0042 software-only;
Task0036 unresolved_no_acquisition; scientific gates, exposure and particle state
remain unchanged.

## Accepted outcome

Final status is **parent_accepted_synthetic_joint_service_replay**, invocation
`f6cee370c24f43a0b95558d4f2e03faa`. The
[1764 scenarios](../results/tables/final/task0044-joint-service-replay-scenarios.csv),
[1008 contrasts](../results/tables/final/task0044-joint-service-replay-contrasts.csv)
and [compact summary](../results/tables/final/task0044-joint-service-replay-summary.json)
retain every candidate/policy/worker/arrival seed and unfavorable case.
All8,820,000 presentations conserve:7,954,126 completed +865,874 overflow,
admitted=completed, final pending0. There are1,998,537 late completions. These are
sums over repeated presentations, not independent events or measured traffic.

| Assignment | Presentations | Completed | Overflow | Late / completed count |
|---|---:|---:|---:|---:|
| Cyclic main |3,780,000|3,357,428|422,572|923,412|
| Matched constant main |3,780,000|3,357,777|422,223|918,148|
| Reverse sensitivity |630,000|619,460|10,540|78,633|
| Rotation10 sensitivity |630,000|619,461|10,539|78,344|

Mean-only control is close for many count outcomes, yet does not reproduce every
fixed outcome. Cyclic-minus-constant overflow differs in119/756 cases (637 equal),
range−10…+16; late counts differ in318/756 (438 equal), range−21…+146. Aggregate
differences are+349 overflow and+5264 late. Survivor p99 differences range
−1.289794…+6.984459ms. The largest positive p99 difference is AE B128/1ms,
Poisson5000/s,seed42,repetition2: both complete3453/5000, dropping1547. Thus a
latency difference can coexist with identical survivor denominators.

The fixed order study changes overflow in only3/252 comparisons, by−1 each.
Reverse-minus-cyclic p99 ranges−2.332566…+8.022939ms and late counts−67…+222;
rotation10-minus-cyclic ranges−2.263778…+3.208104ms and−81…+175. Reverse's largest
positive case is PCA B128/1ms,Poisson2500/s,seed41,repetition1, all5000 completing:
+8.022939ms p99 and+222 late completions. Aggregate late differences are+412
reverse and+123 rotation10; these aggregate signs do not hide negative cases.
Order can matter near a deadline despite little overflow difference. Source
multisets are identical; finite dispatch prefixes and assigned means can differ.

At500/s, cyclic B1 has no overflow or lateness; p99 is0.612–1.732ms PCA and
0.648–2.014ms AE across both modes/all seeds/workers. At2500/s, B1 overflow is
7.82–12.30% PCA /10.34–17.34% AE and survivor p99 is577.926–597.081ms /
599.021–645.700ms. At5000/s, B1 overflow is43.68–45.28% /44.94–47.86%, with
89.864–90.570% /90.265–91.254% of survivors late. Other fixed policies are all in
the CSV; these examples establish no policy recommendation.

Partial billing is substantial:425,677 partial batches,3,347,103 useful events,
11,093,600 charged full-B slots and7,746,497 unused slots (30.1715% aggregate
partial-slot utilization),4246.973707 virtual seconds of partial service busy
summed across scenarios. Of1,705,396 dispatches,962,026 assign original samples and
743,370 assign the constant; original-sample reuse includes47,691 complete cycles
plus8206 remainder assignments. Per-scenario counters/cursors remain separate.
At500/s, cyclic B128 partial utilization ranges17.756–19.434%. The lowest partial
utilization anywhere is2.34375%: PCA B128/1ms,Poisson5000/s,seed41,repetition2,
one final partial batch with3 useful events charged128 slots. These full-B bills
are hypothetical assumptions, without measured natural partial costs.

All three inspected figures include every displayed point:
[outcomes](../results/figures/final/task0044-joint-service-replay-outcomes.png),
[survivor latency](../results/figures/final/task0044-joint-service-replay-latency.png)
and [contrasts / partial billing](../results/figures/final/task0044-joint-service-replay-sensitivity.png).
Latency uses log axes; signed contrasts use explicit symmetric log thresholds.
No confidence intervals, clipped observations or best-policy highlighting.

## Fresh acceptance, reads and execution history

Final acceptance is
`data/task0044-validation/30bc752c1cff474488bcd5bd3b0be537/software-acceptance.json`:
161 new tests +27 inherited runtime tests =188 focused;2749 full and2749 portable,
lint/format/dependencies and generated native bootstrap +actual serialized-record
roundtrip passed.269 source/config/prompt/test bindings,43 installed packages and
36 installed metadata/native byte pins are frozen. Exact source snapshots remain
ignored. Complete generated suites never numerically load real Task0043 sources.

Three validation versions retain178/185/188 focused and2739/2746/2749 full+portable
counts. Six full/portable processes instrument a historical subset totaling510
fixture-model instances,186 forwards/52,260 rows,186 reconstructions,12 toy optimizer
steps and12 toy calibrations; other legacy fixture work is outside that counter.
No global-zero test-model/optimizer claim is made. Task0044 replay/fixture engines
execute no model, optimizer, calibration or physical service measurement.

There are11 native invocations:9 generated-fixture integrations (7 accepted,
2 failed) and2 real-source replay invocations (1 failed before scenarios,
1 accepted). Preliminary failures are sandbox-blocked process accounting and an
incorrect child entrypoint rejected before numerical work; release/reaping are
preserved. The first real-source worker rejected an incorrect loader assumption:
the original CSV window counts are `7/7/6`, not JSON. It parsed184 original JSONL
records and derived one20-value timed vector before rejection; no arrivals or
scenarios began. Its exact269-source old version/config is recovered and byte
verified in the ignored preservation snapshot. A generated regression and renewed
full acceptance precede the successful invocation. No source samples/matrix
choices are substituted or changed; no replay is repeated to redraw figures.

Successful real replay and independent parent verification load6 JSONLs/1104
records and select960 timed values, representing the same24 vectors/480 original
sample positions. Including the failed source invocation:7 JSONL loads/1288
records/980 selected-or-derived timed values. Duplicate aggregate observations,
chronology and statistics are separately accounted in the compact summary, along
with16 earlier direct metadata JSON inspections and zero earlier JSONL loads.
The fixed19-file numerical/provenance bundle is690,916bytes. Thirteen originally
bound historical software-metadata pins include two overlaps, giving30 unique
metadata/timing files totaling947,791bytes; the11 extra files are byte-only checks,
without following embedded scientific/raw/model paths. Original software maps are
verified against their declared entries, not expanded for Task0044.

Across the7 accepted fixture matrices plus1 accepted real-source matrix:
144 generation requests/720,000 generated event instances, the same18 trace hashes /
90,000 distinct synthetic events,14,112 scenarios/70,560,000 presentations.
The final deliverable is one1764-case matrix. Fixture totals are separately
12,348 scenarios/61,740,000 presentations; failed native invocations add no cases.

Final continuous lifecycle: prerequisites1.096291s; simulation worker12.785279s,
reporting1.857965s; finalization0.422446s; whole16.548633s, overshoot0. Worker RSS
62,881,792/159,186,944bytes, native50,331,648/104,415,232bytes; controller RSS
65,503,232/native62,914,560bytes. Source vectors19,408bytes/traces6,285,148bytes;
owned output11,714,442bytes at acceptance. Caps passed, both workers exit0/reaped.
Eight active assertion observations followed by released/reaped/confirmed absence;
display sleep allowed, no persistent changes. All13,748 primary observations are
WARN advisory; zero CRITICAL/invalid/unknown. Optional RAM context is unavailable.
Query gaps0.055160/0.068850s in workers,0.073616s controller; terminal worker gaps
0.027876/0.083833s. Sampling does not certify unsampled intervals or global resources.
Cleanup0.000158/0.000099s remains inside2s caps. Aggregate-only curation takes0.546s
under a separately declared60s budget, without another simulation.

Task0043 accepted/consumed, Task0041 failed/consumed, Task0042 software-only,
Task0036 unresolved, scientific gates/permanent exposure/prior failures and
particle192/192 consumed canonical deferral are preserved. The next decision is
separately scoped natural partial services or an unmeasured streaming boundary.

An aggregate-only export correction normalizes curated CSV CRLF to LF for Git.
Every CSV field matches the accepted owned original; original receipts/hashes are
unchanged. Its separate60s budget adds zero replay or historical timing loads.
