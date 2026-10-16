# RareGate v1: research conclusions and development evidence

The frozen compact autoencoder provides moderate ranking discrimination on the
accepted two-prong signal and weaker discrimination on three-prong signal. Its
strictest calibrated cuts retain very few signal events. The project has an
assessable scientific and computational baseline, followed by bounded development
integration evidence; it has not demonstrated a useful rare-anomaly trigger.

**Preserve the frozen baseline and conclude the current CPU/synthetic/development-
streaming investigation with its explicit partial outcomes.** The CPU/synthetic
phase stays closed within its declared scope. Real PCA and AE integration/parity
were each observed in separate small sessions. Neither whole pilot was accepted:
Task0056 failed on the subsequent AE journal path, and Task0058 retained a global
pre-growth storage-guard defect despite successful native AE checks. Concluding
this narrative does not turn those outcomes green, certify a software release or
establish detector readiness.

Task0059 is metadata-only consolidation (`completed_curated_v1_evidence_consolidation`),
with `operational_readiness: false` and `new_P4_granted: false`. It adds zero new
operational work. The historical raw, feature, inference, decision, custody and
generated numerical activity below remains positive. This is an independent
research snapshot inspired by LHC computing, without official CERN/experiment
affiliation, release tag, completion percentage or promised deployment date.

## Scientific result and its limits

Six-component PCA and the 155-parameter compact AE v2 share eight frozen aggregate
features, scalers and original calibration. Higher reconstruction SSE is anomalous;
PCA's unfavorable orientation was not reversed. The accepted scientific reference
used B4096, including tails. The four quality rows below are copied from
[Task0049's scientific aggregates](../results/tables/final/task0049-cpu-trigger-synthesis-summary.json),
`/scientific_context/quality_rows`, rounded only for display. No metric, curve,
interval or scientific comparison was recomputed. [Claims V01–V04.]

| Candidate | Signal topology | Accepted AUC | Accepted AP | Background / signal rows |
| --- | --- | ---: | ---: | ---: |
| PCA6 | two_prong | 0.468489 | 0.364379 | 150471 / 100000 |
| AE v2 | two_prong | 0.660064 | 0.547427 | 150471 / 100000 |
| PCA6 | three_prong | 0.462953 | 0.360220 | 150471 / 100000 |
| AE v2 | three_prong | 0.585877 | 0.479972 | 150471 / 100000 |

AE's approximately0.660/0.586 AUC describes moderate ranking and weaker three-prong
performance. AP depends on the evaluated mixture of 100000 signal against 150471
background rows per topology; this prevalence is not an LHC rate. The background
scores are shared across the two topologies, not independent background replication.
The models also differ in capacity, representation and arithmetic, so the observed
ranking difference cannot identify a causal effect of nonlinearity.

The [complete16 original operating points](cpu-trigger-study-synthesis.md#scientific-usefulness-and-the-computational-bridge)
retain every cut and the original threshold precision. At the strictest AE cut,
56 two-prong and 34 three-prong signals survive out of 100000 each, against 116 of
150471 shared background events. Four decisions use strict `score > threshold`,
with ties rejected. Neither a target calibration FPR nor these sparse tail counts
establish a useful rare-signal trigger, significance or physical signal efficiency.
No threshold/model selection or new independent confirmation follows.

Task0036 remains `unresolved_no_acquisition`; Task0034 scientific gates remain
unchanged. Permanent test exposure is YES/YES/YES. An appropriate independent
scientific evaluation route is needed for stronger usefulness/generalization
claims; more engineering parity or repeated exposed data cannot supply it.

## What the native CPU and synthetic studies established

Task0049 is the authoritative consolidation of the earlier accepted evidence,
not a request to reconcile its 57 underlying files again. Its
[report](cpu-trigger-study-synthesis.md), [Italian brief](cpu-trigger-study-decision-brief.md),
[23-row boundary table](../results/tables/final/task0049-cpu-service-boundaries.csv)
and [claims](../results/tables/final/task0049-cpu-trigger-claims.csv) remain unchanged.
The six accepted physical campaigns answer distinct timing questions. [V05–V06.]

| Campaign | Directly measured boundary | Key inclusion/exclusion |
| --- | --- | --- |
| Task0022 | Preloaded CPU reconstruction, precomputed-reconstruction score/decision, public adapter | Separate scopes; excludes raw reads/features, transport and queueing |
| Task0038 | Owned prepared packing → public score → four decisions → retained first-m results | Natural m and genuinely padded B computations; excludes raw/physical features |
| Task0040 | Selected HDF read, features from preloaded raw, and directly measured joint read→features | Persistent handle/cache; no model or transport; component sums cannot replace joint time |
| Task0043 | Selected raw → frozen features → owned packing → public score/four masks/owned result | Loading, custody, parity/reference and explicit monitoring queries outside service pair; no queue |
| Task0045 | Paired natural m versus containing full B real-row raw→decision work | Independent reads per side; B-based windows and historical helper mappings |
| Task0047 | Current actual-row paired service at 32 prescribed occupancies | Own wrapper,17 new points+15 freshly remeasured references; old campaign costs not substituted |

These measurements must not be added/subtracted to manufacture a joint boundary,
component overhead or cross-campaign speedup. Complete original cells, repetitions,
slow calls and adverse pairs remain in the linked tables. Raw campaigns used a
1024-row approved development prefix and 384 historically selected raw rows, with
warm dependent windows, persistent HDF handles and prior custody history. Serial
repetitions are not independent trials. Decoder threading, OS cache and contention
limit causal interpretation; chunk geometry is not measured I/O or cache misses.

The current occupancy evidence covers32 of 169 legal points and leaves137 missing;
333 unfavorable source pairs are preserved. All B8 occupancies having lookup
support does not validate streaming. No interpolation, monotonic service law or
universal service bound is implied.

The [four-study comparability table](../results/tables/final/task0049-replay-comparability.csv)
and [complete refined conclusions](../results/tables/final/task0049-refined-replay-conclusions.csv)
retain the prescribed grids, cursor/phase rules and all contrast families.
Synthetic FIFO simulations transport finite measured costs under explicit arrival,
capacity, tie and drain rules. Their repeated scenarios/presentations are neither
physical event rates nor independent event samples. Current Task0048 totals are
30240000 presentations =27544586 completions+2695414 overflow, pending0;6067628
late survivors are conditional on completion. These are copied sums, not a new
replay or new latency distribution. [V07–V08.]

Refined next-anchor natural work still relies on mapped events (9.1235%); previous
mapping relies on 27.3306% and retains a473944 modeled-row deficit. Refined next's
summed overflow/lateness differences of−55/−21714 hide77/171 harmful contexts;
previous mapping also retains harmful contexts. Refined/coarse support changes
control billing and queue history as well as natural service. Thus apparent gains
cannot identify a causal support benefit or justify a deployment policy. Do not
subtract older Task0046 outcomes from current Task0048 to isolate a measurement
benefit, pool incompatible grids or select only favorable cases.

Task0049's methodological deviation remains explicit: two early generic parses
incidentally decoded embedded Task0046 timing vectors; they were unused, and its
final projection omitted that subtree. Task0059 hashes only its declared curated
references, selects aggregates and does not reopen those old vector/trace payloads
or repeat their decoding. [V09.]

## Generated software and the explicitly instrumented contract

The [development protocol](development-streaming-protocol.md) proposed a finite
physical study; the 24×768/840 s study remains ungranted. The implemented core uses
64 B software row descriptors, a12288 B bounded ring and 64 inclusive credits,
including staged/active work. FIFO nominalB8 dispatch uses actual m and an oldest-
admission1 ms timeout. Open-loop intended offer times expose producer lag; missed
or rejected offers are not replaced. Owned score/mask availability is a service
boundary, while references and final cleanup determine later validity. [V10–V11.]

Generated arrays, arithmetic, serialized artificial models, public scoring,
records/CRC, process clocks and lifecycle checks are positive software work. They
are distinct from original-data/model inference. Expected injected faults can pass
software expectations while remaining invalid/incomplete workloads, with unknown
in-flight work retained. Passing earlier-source cases never supplies missing final-
source coverage. This distinction explains the source-specific qualifications:

| Evidence | Established within its source scope | Boundary retained |
| --- | --- | --- |
| Task0051 foundation | Generated finite queue/accounting and ownership behavior | Not operational HDF/model acceptance |
| Task0052 instrumentation | Bounded revision and recorded finite observations | `partial_generated_streaming_instrumentation_characterization`; `sampled_limits_exceeded`; incomplete final-source coverage |
| Task0053 explicit v2 |12 final-source generated expectations pass | Changed question/requirements, not confirmation of the old contract |
| Task0055 startup/tracker | Shared source-free runtime and final 12 generated+2CPU bootstraps qualify | Own bundle27753982…; no real parity and no recovery of Task0054's missing traceback |
| Task0057 shared lifecycle |12 core+3 actual shared-controller expectations qualify | Own bundle142d9e01…; eager journal survives case cleanup and retires once; no P4 supplied |
| Task0058 AE-only prerequisite |16 final-source expectations pass,18 underlying dispatches | One1008-planned-offer group; artificial and real outcomes remain separate |

Task0052's five eligible event-append exceedances (maximum 103041 ns) remain a
negative historical result. Task0053 explicitly adopted the instrumented request
pipeline as its exploratory question:50 µs/event and 200 µs/batch became diagnostic
references, with every exceedance retained. They are not hard append guarantees.
Inclusive observers/control/logging costs remain; no subtraction estimates an
unobserved pipeline with instrumentation removed. [V12–V14,V17,V22.]

V2 also replaced the unproved65536 B all-in synchronization backing condition with
primitive-count/lifetime and visible allocation inventory:21 core SemLocks, tree≤26,
plus resource guards. Kernel backing remains unknown. Task0055 explicitly replaced
private inner64+tracker16 MiB with joint inner+owned-tracker80 MiB, without passing
the old16 MiB condition or increasing the outer aggregate allowance. Exact Python-
heap/native-workspace attribution and effective decoder threading remain unproved;
RSS and the 7444432 B owned numerical-buffer derivation do not establish them.
These historical changes are claim changes, not universal resource certification.

Task0058's169 distinct passing-covered expectations are not169 simultaneously clean
tests:411 pure executions include three failures, plus two adapter errors retained.
Its26 curated rows describe boundaries/candidates/custody, not26 native invocations.
Artificial serialized work includes702 public calls/1466 score rows/5864 Booleans,
separate from real AE. Overlapping test populations and generated/real/scientific
event counts are not added into a global success count.

## Separate real development integration observations

Two narrowly authorized sessions supplied the missing real component evidence.
They are adjacent observations, not a paired PCA–AE comparison. Their full bundle
identities are preserved in the [claims registry](../results/tables/final/task0059-v1-claims.csv)
and [snapshot summary](../results/tables/final/task0059-v1-consolidation-summary.json).
[V15–V19.]

| Component / source | Source bundle prefix | Component checks | Whole source outcome |
| --- | --- | --- | --- |
| PCA, Task0056 | `38a3031a333eb853` | passed | `partial_failed_development_hdf_pilot_v2`; pilot accepted false |
| AE v2, Task0058 | `6cd0fc14666ea54d` | passed | `partial_bounded_development_ae_hdf_pilot_storage_guard_gap`; pilot accepted false |

| Observed work, including gates/references | Task0056 PCA | Task0058 AE |
| --- | ---: | ---: |
| Offered /completed /contention rejects |64 /63 /1 |64 /62 /2 |
| Raw /feature rows |207 /207 |206 /206 |
| Public calls /score rows /Boolean outputs |174 /342 /1368 |168 /340 /1360 |
| Deferred realized-group references |63 |60 |
| Pre/post shape contexts, m1…8 |16 |16 |
| Raw custody passes /bytes in that session |2 /5816520818 |2 /5816520818 |
| Component integration/parity |passed |passed |
| Whole pilot accepted |false |false |

Both used 64 periodic software requests at 500/s,128 ms horizon, nominalB8,
positions0…63 of the original sorted development prefix, no wrap/replacement.
PCA actually dispatched63 m1 groups; AE dispatched58 m1 and two m2 groups. Gates
use positions0…7, two full raw chains plus a same-shaped golden/public reference
per shape, before/after streaming. The distinct1024-row golden approval permits
reference selection, not scoring1024 rows by default. Four masks are four Boolean
outputs per score row, not four completed events. The public totals include repeated
gates and references; no independent physical-event population is invented.

Only the consumer loads original membership/golden/one frozen candidate and opens
selected HDF. Ingress transports approved row descriptors before HDF processing,
not independently encoded detector event bytes. The actual chain uses owned
FP64[m,2101] raw rows, full700-particle frozen features, eight FP32 channels, public
actual-m scoring, FP64 SSE and strict four masks. Owned output comes before deferred
same-shaped golden references and final acceptance. Every realized completed group
received its own reference. No source inputs or models were reloaded for Task0059.

Service/output timing includes producer scheduling, queue waits, instrumentation
and controls according to the recorded boundaries; custody, loading/gates and later
references are outside arrival service but inside the externally observed pilot
lifetime. HandleA gates followed by handleB reopen with 1 MiB/521slots/w0 .75 and no
B warm-up do not establish cold OS cache. Custody, gates, model/golden loads and
prior host activity can warm inputs. NominalB8,500/s pacing and tiny survivor
latencies do not establish sustained capacity, full-B8 throughput, production p99,
cache/transport causality or scientific efficiency. Separate sessions cannot rank
candidates or pool latency percentiles.

Task0056's valid PCA component remains separate from its whole-session failure:
AE tracker publication hit `Unregistered diagnostic descriptor` before workers,
with a valid RSS sample. Task0057 repaired that ownership path on generated inputs.
Task0058 subsequently observed real AE parity with normal journal teardown; it
did not retrospectively accept Task0056. Earlier Task0054 is a third separate
historical fact: two successful custody passes/5816520818 B, PCA startup failure
before ready, no issued offers or real service, AE unattempted. That session is
failed/consumed; its missing exception is not recovered. Repeated custody of one
file is positive byte work, not new independent data.

## Storage exception that prevents Task0058 acceptance

The final Task0058 flags remain exactly:
`native_pilot_checks_passed: true`, `real_AE_integration_parity_observed: true`,
`pilot_accepted: false`, operational readiness false, P4 consumed. Its narrower
native observer `qualified: true` and prospective configuration do not override
whole-task acceptance. [V20–V21; original AE report](development-ae-hdf-pilot.md).

Task0058 recorded three formatter-cache files changed outside its pre-growth ledger.
Their full then-current logical lengths totaled 24124 B; allocated regular-file
blocks totaled 32768 B. Previous lengths and growth deltas are unknown. These are
reported historical facts, not Task0059 cache observations. The12136251 B observed
logical charge and 366-entry21563584 B reservation fit32 MiB, but cannot prove that
all writes were guarded before growth. The defect is not measured24124 B growth
or cap exhaustion. Logical bytes, allocated blocks, reservations and unmeasured
filesystem/kernel metadata have different scopes.

No retrospective reservation, cache deletion, amended native receipt or waiver
occurs. A future source-free tooling correction can disable caches or explicitly
control them before writing; it cannot recover the historical contract. Repeating
real inference solely to fix formatter accounting adds no missing integration
observation. Task0059 uses bytecode-disabled standard-library metadata snippets,
no Ruff/pytest/project imports, and does not inspect or reset old caches.

## Decision register and reproducibility boundary

| Question / claim | Existing evidence | Missing evidence | Consequence now / condition for reopening |
| --- | --- | --- | --- |
| Useful rare-anomaly ranking/generalization |Four accepted quality rows and 16 frozen points |Appropriate independent evaluation route; strict-tail usefulness |Keep moderate/limited wording. Reopen for a new scientific question under unchanged0034 gates, not more engineering parity |
| Native computational costs |Six accepted boundaries;32 occupancy points |137 occupancies and any new host/boundary |Preserve existing scoped costs. Measure further only if a specific decision needs them and fresh scope is granted |
| Physical transport/cache/sustained load |Finite instrumented PCA/AE request observations |Defined physical boundary/history, workload/host and success/stop criteria |No detector/rate/cache claim. New bounded authorization required;24×768/840 s remains ungranted |
| Global tooling storage guard |Task0058 known cache exception |Prospectively controlled future tooling writes |Keep historical failure. Source-free correction only; no real repeat for cache accounting |
| Heap/native/decoder/kernel attribution |Visible buffers, counts/lifetimes, own RSS/thread observations |Supported exact attribution/effective decoder evidence |State unknowns; do not infer them from RSS or revive old partition/backing claims |
| Particle and other execution branches |Particle192/192 consumed;0024 accepted ONNX export/equivalence |Canonical particle feasibility/usefulness;0025 performance remains failed; no current MPS proof |Keep canonical deferral and separate outcomes; no automatic new execution |
| Current investigation |Frozen science,closed CPU/synthetic,partial integration narrative |No missing evidence required to document the limitations |Conclude now; reopen only for a distinct claim and appropriate scientific/operational scope |

A reader can reproduce the copied tables, status distinctions, selectors and simple
count checks from the 39 pinned curated inputs (3376089 unique bytes, below8 MiB).
The [input registry](../results/tables/final/task0059-v1-evidence-registry.csv) binds
paths/roles/sizes/SHA256; the [24 claims](../results/tables/final/task0059-v1-claims.csv)
bind JSON pointers, CSV row selectors and report headings. Metadata read/recheck
counts are reported separately from unique bytes. Starting identities of living
documents are separate from immutable evidence. Embedded paths are inert.

This snapshot cannot reproduce per-append/per-event distributions, original raw
parity, model execution or old queue replays from curated aggregates. Those would
require ignored/original payloads and a separately authorized task. No such files
were opened here. The historical57-source registry is provenance, not traversal
permission. No new scientific metric, distribution, uncertainty, benchmark, native
fixture, acquisition, reservation or P4 was performed/granted.

The construction/check recipe is: use `python3 -B` standard-library snippets;
verify only the registry's explicit paths/sizes/hashes; lexically select declared
aggregate JSON pointers without decoding unselected vector subtrees; read aggregate
CSV selectors; check count conservation, output schemas, links and immutable pins;
then inspect Git. Do not run prior report helpers, project modules or historical
suites. Output identities are recorded where noncircular; the summary does not hash
itself. This documentation completion preserves all historical positive activity,
partial failures and consumed allowances, including0049's inspection deviation,
0036 unresolved status,0034 gates,YES/YES/YES,particle192/192,0024 accepted export
versus0025 failed performance and no current MPS claim. No next task is launched.
