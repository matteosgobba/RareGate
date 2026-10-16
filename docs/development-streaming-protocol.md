# Development streaming protocol — Task0050, design only

Can a bounded physical development experiment account for real producer offers,
finite queueing, selected HDF reads, frozen features, CPU scoring and four decisions
under declared input histories? Recommend **nominal B8, periodic open-loop row
requests, one local shared-memory descriptor ring, two handle histories and two
repetitions** at 500/2,500/5,000 events/s. This is a software request boundary before
HDF processing, ending at owned decision output. It can establish poor delivery,
overload or inconclusive timing as readily as favorable behavior.

Status: `completed_design_only_development_streaming_protocol`; readiness:
`requires_prerequisites`. All behavior below is **proposed and unimplemented**.
No physical validation occurred. The [declarative specification](../configs/protocols/development_streaming_v1.json)
has `design_only=true`, `execution_authorized=false` and
`operational_allowance_granted=false`; it is neither an old campaign grant nor an
entrypoint. The [design summary](../results/tables/final/task0050-development-streaming-design-summary.json)
binds evidence and static checks. Implementation and any execution need separate
scope and decisions; Task0051 is not launched.

## Evidence and population

Task0049 closes the declared native CPU/synthetic study within scope. Historical
Task0047 supports all B8 occupancies 1–8, leaving 137 occupancies elsewhere
unmeasured. Lookup completeness does not validate streaming. Task0043's warm,
serial B8 means were 3.251953 ms PCA and 3.294765 ms AE; those boundaries excluded
producer/transport/queueing. These are copied motivation, not new service bounds.
No timing vectors or operational payloads were reopened.

Use frozen six-component PCA and compact AE v2 on development background only.
The method reports specify starts `0, floor((1024−B)/2), 1024−B`; at B128 they
are 0/448/896. Their 128-row windows give exactly **384** symbolic prefix positions
`0..127, 448..575, 896..1023`. Smaller historical windows are contained there.
The prefix is the same ascending first 1,024 IDs from the original 6,999-ID source;
1,024 approved/golden rows are not permission to read 1,024 raw rows. No real IDs
are enumerated here. Expansion, new ordering and grouping/scatter need future
checks and authorization; old permissions do not transfer.

## One finite experiment

Let U concatenate those three ascending intervals. Each run offers exactly
768 presentations: position `U[k mod 384]`, k=0…767, reset per run. Thus each row
has two scheduled occurrences per run, not two independent events. Use identity
`(case_id, phase, presentation_index)` for measured, gate and priming work.
Rejected/missed offers are never replaced. Actual reads can consequently differ
between histories; pass labels describe scheduled order, not guaranteed coverage.

| Periodic offered events/s | Offers/run | Horizon seconds | Runs: 2 candidates × 2 histories × 2 repetitions |
| ---: | ---: | ---: | ---: |
| 500 | 768 | 1.536 | 8 |
| 2500 | 768 | 0.3072 | 8 |
| 5000 | 768 | 0.1536 | 8 |

All 24 case IDs and their exact order are in the specification. Repetition 1 uses
ascending rate, PCA→AE, reopened→primed; repetition 2 reverses each nesting order.
No candidate, threshold, queue policy or physics outcome is selected. These are
finite development offered-load questions, never physical LHC rates.

| Deferred alternative | Reason |
| --- | --- |
| Extra nominal B1/B32/B128 | B8 already exposes actual m=1…8; another nominal boundary is not indispensable. |
| Poisson/bursts, capacity/timeout search | Adds separate questions before the physical boundary is understood. |
| Decoded arrays | Moves HDF work and cache ownership to producer; raw rows are 16,808 bytes, features 32 bytes. |
| Independently encoded event payload | No frozen event codec/framing contract exists; separate representation study required. |
| Cold-cache or transport-benefit arm | No OS reset or matched process/path comparison is proposed. |

## Transport, batching and clocks

Three fresh processes per run: supervisor, producer, consumer. Only the consumer
opens HDF and loads the candidate. One fixed shared-memory ring transports **64-byte
little-endian descriptors**, not event bytes: version/flags u16 each, run u32,
presentation u64, prefix position/reserved u32 each, intended/submission u64 ns,
16-byte source token and eight reserved bytes. The token routes an already bound
source; it is not authorization. Full identities are checked at setup.

Each of 64 slots has another 64 bytes for admission timestamp, enqueue sequence
and reserved framing; a 4,096-byte control page gives 12,288 shared bytes.
Producer scratch is 64 bytes; consumer descriptor copies at most 512 bytes.
Native lock/semaphore bookkeeping has a separate 65,536-byte proposed allowance.
No pipe, socket, feeder, acknowledgement queue or hidden message buffer is allowed.
Shared ready/closed/error flags carry lifecycle state. Their implementation remains
subject to bounded-storage and concurrency review.

Producer computes intended time lazily as `t0+floor(k*10^9/rate)`; no trace is
precomputed. H=`t0+768*10^9/rate`. At each wake, process due k in order: lag over
2 ms becomes a producer miss; attempt at most four nonstale due offers and mark
remaining currently due offers missed by the catch-up cap. No submission at/after
H; unresolved offers become horizon misses. One nonblocking mutex try per submission
rejects contention immediately; no credit rejects capacity. Never wait for service
or shift t0 to hide lateness. Record requested versus achieved delivery explicitly.

FIFO uses enqueue sequence, with intended ties ordered by k. Hold one credit from
admission through output or abnormal terminal failure: ring waiting + consumer
staging + active ≤64, active/staging each ≤8. The producer's single undecided
submission is separately bounded and is not admitted. No output queue is needed:
consumer owns a fixed four-mask output allocation.

When idle, dispatch oldest eight if available; otherwise dispatch available m
when the oldest **admission** age reaches 1 ms. Poll/wait target is at most
100 μs or remaining timeout. Busy service does not flush concurrently; actual m
is fixed at dispatch. At producer closure drain final partials immediately, with
no extra presentations and a hard five-second drain limit from H.

```text
intended offer → producer submission → try-admit / reject
                                      │
                    [bounded descriptor FIFO + credits: 64]
                                      ↓ dequeue / dispatch actual m≤8
 consumer: selected HDF reads → frozen full features → public score / strict4
                                      ↓
                              owned output available
                                      ↓ outside joint service
                       feature/hash records → after-drain reference
```

Use integer `time.perf_counter_ns` on a verified common same-host monotonic epoch
and rate. Record implementation/resolution; nanosecond units do not prove 1 ns
resolution. Cross-process comparability, scheduler behavior and suspend handling
are unmeasured. Separate continuous, suspend-inclusive supervision must reject
clock discontinuity/suspension. Owners and missing transitions are explicit:

| Timestamp / phase | Owner | Meaning |
| --- | --- | --- |
| Intended offer | Producer formula | Original latency origin, even if submission is delayed |
| Submission | Producer | Immediately before one nonblocking admission try |
| Admission / rejection | Producer | Linearized publish or failed try; reason retained |
| Dequeue / dispatch | Consumer | Ring removal into bounded staging / actual m fixed |
| HDF start / return | Consumer | First checked selection / all reads, guards and scatter returned |
| Features | Consumer | Frozen eight features complete |
| Decision / output | Consumer | Actual-shape score/strict4 complete / owned copies available |
| Control end | Consumer | Subsequent feature comparison, hashing and record append complete |
| Startup, identities/loads, pre gates, reopen, priming, ready/t0 | Supervisor/consumer | Outside arrival latency; inside run budget |
| H, closure, drain, references/post gates, cleanup/reaping | Respective owner, supervisor verifies | Distinct lifecycle phases, never substituted for event endpoints |

Null timestamps require reasons; never insert zero or impute durations. Future
instrumentation must characterize overhead without extra operational runs:
proposed append ceilings 50 μs/event record and 200 μs/batch record. Exceedance
invalidates that instrumented case; retain it without replacement. Do not subtract
overhead. Out-of-service controls still stall the consumer and affect later latency.

## HDF, input custody and parity history

The future study has exactly two whole-file custody SHA256 passes, before all
runs and after all runs, outside latency. Both can warm OS pages. Every run loads
membership once, golden once and one frozen candidate/threshold set. Pre gates
use handle A; close A and release application raw/feature buffers, then open B.
Both handles require original schema/filter and cache **1 MiB / 521 slots / w0 .75**.
Models/golden remain loaded. No prefetch or cross-batch raw/feature cache.

- **Reopened:** no raw warm-up after opening B; measured U then U on B.
- **Primed:** 48 untimed real B8 chains traverse U once (384 rows) on B, check and
  release outputs; measured U then U continues on that same handle.

Pre gates touch positions 0…7 and warm models; golden/reference reads and global
custody also belong to history. Prior runs and uncontrolled host activity persist.
Application reset, reopened HDF cache, first scheduled pass, repeated pass and
priming are distinct. None establishes cold OS/page cache. No purge, reboot,
global cache reset or app closure. The history contrast includes priming work,
time and changing admitted groups; it cannot isolate a cache mechanism.

For arbitrary FIFO groups, stable-sort descriptors by position, assign each position’s j-th
occurrence to layer j (from zero), read layers ascending and positions increasing
within each layer as the minimum number of duplicate-free selections, read only those
selections with the original HDF decoder and scatter into owned FP64[m,2101] FIFO
order. Each logical occurrence returns a row, with at most m subrequests; no
repeated occurrence is served from a cached raw row. This proposed gather/scatter
needs validation. Neighboring-chunk decode never permits returning/analyzing
nonapproved rows; geometry is not a cache-miss, decompression or physical-I/O count.

Keep original FP64 sort/wrap, physical FP32 conversion, all-particle FP64 aggregates,
mass/log/scaler conventions and eight FP32 channels. Never build the particle384
view or load full raw data. Perform one original public score on actual m and
strict `score > threshold`, ties rejected, with owned four-mask copies. No
padding, sparse-anchor interpolation or imported timing bill.

At pre and post gates, ascending m=1…8 uses positions 0…m−1: one independent
golden-only same-shaped reference and two complete raw chains per shape. Require
exact features, scores, masks, repeats and pre/post identities, finite arithmetic,
correct ownership and unchanged parameters/calibration. Historical tolerances
are not enlarged: same-shape score/PCA 1e−12 maxima remain historical; this design
requires byte equality and zero decision mismatches.

Every completed measured batch compares features with ordered golden bytes after
output, retaining grouping, owned score/mask bytes and integrity digests. After drain independently
pack golden rows in **every realized grouping**, repeats included, and call the
public score once, bypassing the new streaming wrapper; independently evaluate
the four strict comparisons for direct byte comparison against retained outputs.
Then run post gates on B and close
it. Thus scheduler-dependent groups are checked exhaustively when realized,
without pretending to enumerate them prospectively. Unobserved groups remain
uncertified. Priming has exact feature/finite/owned checks, not an extra independent
throughput certification. No numerical calls beyond those counted below. Old
small windows and scientific B4096 are not blanket streaming certification.

## Records, conservation and interpretation

Fixed binary records avoid unbounded dictionaries: 768 event slots and up to 768
batch slots, each 512 bytes. Events carry case/phase/presentation/position/cycle,
intended/submission/admission/dequeue times, sequence, batch, terminal status,
reason and output offset. Batches carry ordered members/m, dispatch reason, all
stage/control timestamps, up to eight subread pairs, digests/reference checks,
finite/ownership flags and failure stage. Phase/gate/monitor records have separate
bounded storage. Operational IDs/raw/features/scores are not public curated outputs.

At any cutoff, including H, let O=due intended offers, U=unresolved due offers,
M=producer missed, S=submissions, J=admission undecided, R=queue rejections,
A=admitted, C=completed, F=terminal admitted failures, K=cancelled admitted:

| Nonoverlapping identities | Cutoff rule |
| --- | --- |
| O=U+M+S; S=J+R_capacity+R_contention+A | At H all 768 offers are due; J≤1. Before H, not-yet-due offers remain separate. |
| A=Q_ring+Q_staged+X_active+C+F+K | Separate every queue and active ownership; pending sum ≤64. |
| 768=M+R_capacity+R_contention+C | Normal final drain only: U=J=Q_ring=Q_staged=X=F=K=0. |
| Boolean outputs=4C | Four masks are outputs, not four completed events; false masks still complete. |

Project timestamped linearization records onto H; racing counter snapshots are
insufficient. On abnormal stop preserve unresolved/uncertain operations and future
unoffered work. Output already available remains C if later parity invalidates
the run; F/K contain only rows without output. Each HDF/service intent has disjoint not-started/inflight/returned
(or completed)/failed states and row counts. Separate requested, returned,
constructed and scored rows; never guess returns after a crash.

Per run report S/(H−t0) and A/(H−t0) against requested 768/(H−t0); completion C/768, missed M/768
and rejection R/S (zero-denominator null). Latencies for n=C completed survivors:
output−intended, submission−intended producer lag, dispatch−admission queue wait
(split at dequeue), output−HDF-start direct joint service, output−dispatch batch
execution. Missed-offer detection lag is separate. Report p50/p95/p99 using actual
values, linear convention and n; no averaged run quantiles, dropped-event latency
imputation, production p99 or independent-event inference.

**100 ms is only an illustrative development deadline.** Overload is an observed
result, not a stop: count completed latencies >100 ms, pending overdue at H/stop,
overflow and producer misses separately. No pure transport overhead or benefit is
identified by this single intervention.

## Prospective envelope and readiness

| Count ceiling, all 24 runs | Derivation |
| --- | --- |
| 18,432 offered presentations; ≤384 unique raw IDs | 24×768; same U reused |
| 768 fixed gate raw chains / 3,456 rows | 24×2 phases×2 repeats×8 shapes; rows use sum(1…8)=36 |
| 576 priming chains / 4,608 rows | 12 primed runs×48 / ×384 |
| ≤19,776 HDF requests and feature/chain calls; ≤26,496 raw/feature rows | Measured ≤18,432 singleton calls + fixed gates + priming; subreads ≤measured rows |
| 384 fixed golden calls / 1,728 score rows; ≤18,432 realized-reference calls/rows | Fixed 24×16/×72; reference every measured batch |
| ≤38,592 candidate calls / 46,656 score rows / 186,624 Boolean decisions | Chain+both reference types; four decisions per scored row |
| 24 membership/golden/candidate loads; 167,976 membership and 24,576 golden row presentations | 24×6999 / ×1024; 48 HDF opens/closes, 96 same-handle checks |
| Two raw custody passes / 5,816,520,818 bytes | 2×historical source size; future only |

These are upper bounds, not promised counts: losses and larger batches reduce
calls; validity failures leave incomplete runs. Drain adds zero presentations;
all reference/control/warm-up work is already counted.

| Proposed resource ceiling | Derivation / limitation |
| --- | --- |
| Shared transport 12,288 B; sync bookkeeping 65,536 B | 64×128+4096; native primitive bound still prerequisite |
| Raw owned 134,464 B plus read scratch 134,464 B | Each 8×2101×8; aliases excluded |
| Particle scratch 3,225,600 B; model/reference 2 MiB | Proposed 24×8×700×3×8; implementation allocation proof missing |
| Owned arrays/records 8 MiB; Python/serialization 8 MiB | Explicit inventory 7,667,952 B includes caches, framing/copies, IDs/golden, 786,432 B event/batch records and 6,144 B transient scores and 3,072 B retained masks; native/model workspace partly assumed |
| Consumer/producer/supervisor RSS 1024/64/128 MiB; aggregate 1216 MiB | Serial runs, three concurrent processes; shared pages may overlap |
| Native aggregate 512 MiB: consumer 384, producer/supervisor 64 each | Includes libraries, decoder/cache metadata/workspaces; overlaps RSS, not extra physical RAM |
| Diagnostics 4 MiB/run; global 8 MiB; owned storage 128 MiB | 96+8=104 MiB, 24 MiB headroom; 64 KiB pre-growth guard |
| Run ≤30 s including cleanup ≤2 s | Setup10 + horizon≤1.536 + drain5 + references/post10 + cleanup2 =28.536 s |
| Whole study ≤840 s, no reservation | 24×30 + pre-custody45 + post-custody45 + reporting/final cleanup30 |
| Operation/no-progress hard timeout 2 s; monitoring gap ≤250 ms | Monitor target100 ms; drain5 s remains separate |

Charging all 46,656 scored rows at historical B1 AE mean .606340 ms/row with an
explicit 4× planning factor gives 113.15759616 s. This warm serial heuristic
includes reference-only rows conservatively; it is neither a service bound nor
proof the ceilings fit. Historical host context is MacBook Pro/Mac17,2 Apple M5,
16 GB, arm64 macOS26.6.2, with restricted sysctl/thermal observations. Current
hardware/resources were not probed. Future CPU/build/effective Torch intra/inter1,
BLAS/OpenMP/Accelerate1 and decoder threading need verification; requested
BLOSC_NTHREADS=1 historically did not establish effective threads. Library
workspace, OS caches and host contention remain uncertain.

Validity requires identities/parity, complete accounting, bounded records/resources
and normal supervised exits/reaping/handle closure/shared-memory removal. Hard
stop on any identity/parity/nonfinite/unexpected-population failure, ceiling,
accounting loss, monitor failure/CRITICAL pressure, >250 ms primary gap, clock
fault, two-second operation stall or cleanup/process failure. WARN is advisory;
optional unknown context is disclosed. Stop the study on first validity failure,
retain slow/unfavorable/partial observations and unattempted case statuses; no
automatic retry, replacement or limit relaxation. A valid poor workload result
is distinct from invalid instrumentation/lifecycle and from unresolved science.

**Named prerequisites:** P1 new ordering/gather/transport/accounting implementation
review and data-free failure fixtures; P2 proven allocations/native workspace,
cache metadata, synchronization and effective threads under these caps; P3 clocks,
scheduling/logging/monitoring/cleanup characterization; P4 separately authorized
operational identities, population/grouping scope and ceilings. Consequently the
design is complete but requires prerequisites, not operationally ready.

The CPU/synthetic closure, Task0036 `unresolved_no_acquisition`, Task0034 gates,
permanent YES/YES/YES, particle192/192 consumed/canonical deferral, all historical
outcomes, accepted Task0024 export versus failed Task0025 campaign and no current
MPS claim remain. This engineering question cannot establish strict-tail anomaly
usefulness, signal efficiency, causal nonlinearity or detector readiness.
RareGate remains independent research without official CERN/experiment affiliation.

References: [Task0049 synthesis](cpu-trigger-study-synthesis.md),
[decision brief](cpu-trigger-study-decision-brief.md),
[raw-feature method](development-raw-feature-measurement.md),
[joint-service method](development-raw-decision-campaign-v2.md),
[targeted method](targeted-partial-raw-decision-measurement.md),
[preprocessing](preprocessing-contract.md),
[scientific gates](controlled-follow-up-protocol.md),
[source decision](confirmation-source-feasibility.md),
[Task0050 Italian handoff](handoffs/0050-development-streaming-protocol-design.md).
