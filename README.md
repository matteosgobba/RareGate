# LatentTrigger

**Hardware-Aware Machine Learning for Real-Time LHC Event Selection**

LatentTrigger is an independent research and engineering project inspired by the
computational challenges of real-time event selection at the Large Hadron
Collider (LHC). It will investigate how anomaly-detection quality changes when
models must meet strict latency, throughput, and memory constraints.

## Motivation

Event selection motivates studying models that are both scientifically useful
and computationally practical. LatentTrigger will treat model quality and
deployment cost as joint design considerations, using LHC-like event data and
clearly stated experimental assumptions.

## Research question

> How much anomaly-detection performance can be retained when machine-learning
> models are optimized for real-time LHC event selection under strict
> computational constraints?

## Project scope

The planned work spans scientific event-data preparation, anomaly-detection
models, scientific evaluation and bias analysis, and hardware-aware inference.
Apple Silicon CPU/GPU measurements will be the initial hardware focus. Later
phases may investigate heterogeneous inference, NVIDIA hardware, and FPGA-oriented
deployment.

## Planned methodology

1. Select and document a suitable dataset, event representation, and reproducible
   preparation procedure.
2. Establish anomaly-detection baselines, then investigate compact autoencoders
   and particle/set models, adding attention only when justified.
3. Evaluate detection performance and potential scientific biases with explicit
   data splits and evaluation assumptions.
4. Measure latency, throughput, and memory under documented hardware and runtime
   conditions, comparing model quality with computational cost.
5. Investigate optimized runtimes, quantization, and a trigger-like event-stream
   simulator in later phases.

## Current status

The [initial native scientific study and integrated synthesis](docs/scientific-synthesis.md)
are complete. Frozen AE v2 has a moderate observed ranking advantage over PCA
for this signal, with higher accepted CPU cost and weak strict-tail utility.
Both test populations remain exposed; Task0027 used only accepted aggregates.
Task0028 adds the [guarded three-prong extension](docs/three-prong-generalization.md):
Phase A software accepted (1333 full/portable tests); the sole explicitly authorized
Phase B failed and is consumed at acquisition's298s operation deadline. Exit1 /
reaped/parent rejected,298.116752s whole; no verified payload/custody/preparation /
scoring/cached numerical reuse or new scientific results. Interrupted raw access
and logs remain recorded; no retry/resume. The study's planned exposed Task0026
background reuse would provide signal-topology evidence without fresh background
domain-shift evidence.
Task0029 adds a separate [bounded acquisition v2](docs/three-prong-acquisition-v2.md):
1414full/portable tests and own146-source acceptance; the sole newly authorized
session failed/consumed after3payload requests (two read timeouts, truncated EOF).
Two valid206continuations,0restart/redirect;29990748Breceived/written/durable/retained,
accepted full bytes0. Partial SHA/progress/receipts preserved, no numerical/HDF /
model work. Monotonic whole445.572426s versus2305.963121s recorded UTC endpoint
span are distinguished; generic200/206Retry-After handling remains a frozen-code
limitation. No further session or reuse of the failed partial is automatic.


Task0030 completes the separately authorized [sleep-aware acquisition v3](docs/three-prong-acquisition-v3.md).
Own153-source/1503 full+portable tests precede the sole session: a verified independent
copy of Task0029's prefix plus205498246 new bytes through one206 yields the complete
235488994-byte file, matching publisher MD5/local SHA. Three workers exit0/reaped /
parent-accepted; idle-system assertion active/release confirmed, continuous reserved
870.632494s, zero overshoot. Structure only: pandas-fixed float64[100000,2101],
Blosc, no dataset values/numerical custody/fingerprints/cache/models/science.
Fresh power logs broadly explain Task0029's clock divergence, without proving
exclusive network-error causation or changing that historical failed result.
At Task0030 completion, numerical custody/uniqueness/overlap/evaluation still
required a separate local-file protocol and authorization. Task0031 below
subsequently completes that scope. Task0030 exposure was originalYES/YES and new
signal modelNO; particle192/deferred and
Task0025/0028/0029failed consumed outcomes preserved. No new acquisition is automatic.


Task0031 completes the separately authorized [local three-prong scientific evaluation](docs/local-three-prong-evaluation.md).
All 100000 events pass labels, axes, particle validity, exact uniqueness and
all-role fingerprint disjointness. Frozen native PCA has ROC-AUC 0.462953 / AP
0.360220; AE has 0.585877 / 0.479972 in a 39.9248% signal mixture. AE retains an
observed advantage, weaker than for the two-prong signal. At the strict threshold,
AE accepts 34 signals and 116 shared background events: relative acceptance
0.4410, selected signal fraction 22.6667%, with no observed enrichment.
All four workers exit normally and are reaped and accepted within 29.058839s
reserved time. Two signal requests yield 50 complete canonical batches and
200000 scored presentations; two original background caches are numerically
loaded, with zero new background forwards, optimizer updates or downloads.
Fresh 1590-test full and portable validation covers 161 source/dependency bindings;
all 153 historical bindings and scientific evidence are preserved. Continuous
deadlines and a temporary idle-system assertion are verified, including release.
Original tests YES/YES and new three-prong model YES are permanent exposure states.
Shared background remains historical evidence; no independent background,
significance or physical-rate claim is added, and original thresholds are unchanged.
The [tables/summary](results/tables/final/task0031-local-three-prong-evaluation-summary.json)
and [ROC/PR](results/figures/final/task0031-three-prong-roc-pr.png) are accepted.
Task0032 below subsequently completes the offline integrated synthesis from
curated aggregates; no subsequent scientific or training task is launched.

Task0032 completes the [two-/three-prong synthesis and methodological decision brief](docs/two-three-prong-synthesis.md).
Twenty pinned curated sources produce four global-quality rows, all sixteen
calibrated points, eight descriptive topology comparisons, ten scoped native CPU
cost groups and three static figures. AE has higher observed quality on both
signals at higher CPU cost, with weaker three-prong performance and weak strict-tail
utility for both. Shared background is historical evidence, not independent FPR
replication. New arithmetic is post-evaluation description, without significance,
mechanism, combined utility score or physical-trigger claim. All samples retain
exposure YES; new population/array/model/fingerprint/optimizer/download work is zero.
The frozen baseline study is complete within scope. Particle192/192
consumed/canonical deferral and historical failures remain preserved.

Task0033 completes the explicitly authorized [exploratory feature/score diagnostics](docs/exploratory-feature-score-diagnostics.md)
on these exposed samples: one parent-accepted8.778443s session,3feature requests /
350471rows,6stored score loads/700942values and separate3membership loads /
3300000records. Zero new forwards/reconstruction/AUC-AP/significance/fingerprints /
optimizer/downloads. Frozen standardized marginals,48rank associations and all24
original tails are retained;16small-tail feature rows suppressed. Two inspected
figures are curated; an overlapping heatmap is retained only operationally, with
all coefficients in the table.90specific/179focused/1728full+portable checks precede
200-source/43-package freeze and actual prompt-bound consent. Limits/assertion
release pass; sampled monitoring gaps are disclosed. Correlations and distinct
strict-tail profiles generate hypotheses, not causal mechanisms or repaired utility.
No favorable feature/candidate/cut was chosen. Task0034 subsequently completes the
explicitly requested [controlled follow-up protocol](docs/controlled-follow-up-protocol.md).

Task0034 is design only: paired ReLU/identity AEs with the same8→6→3→6→8 biased
layers, bottleneck3/155parameters and three fixed seeds. Exact background-only
training, own checkpoint restoration/calibration, primary alpha0.001, shared-event
uncertainty and numerical decision criteria are specified. The
[source registry](results/tables/final/task0034-confirmation-source-registry.csv)
recommends extra SR QCD plus newly generated XtoYYprime only conditionally:
full-event signal coverage, counts, generation independence, overlap and strict-tail
precision remain unverified; no source accepted or original topology replication
claimed. Nineteen synthetic assertions and metadata/design consistency checks
support the design, with zero new operational access/model/fit/calibration/payload
work. Task0035's synthetic-only software brief is ready to authorize; training,
acquisition and independent confirmation require separate plans/authorizations.
Task0034 launched none of those scopes. Baseline/exposure/failed campaigns /
particle192 remain preserved.

Task0035 now implements the explicitly requested
[synthetic controlled-activation foundation](docs/controlled-activation-synthetic-foundation.md):
separate strict schema/factory, independent paired parameters/actual loader order,
own-state restoration, FP64 SSE/own strict thresholds, integer shared-event moments
and unchanged conditional bounds/gates.189focused/1917full+1917portable tests,
lint/format/dependencies and219source/43package binding pass. Three native
synthetic invocations are preserved: sandbox assertion check and child-module
dispatch fail before numerical work, then the final source is parent-accepted /
exit0/reaped in2.683233s with12started/12completed/0inflight toy updates,65research
forwards/2333rows,6own toy calibrations and verified assertion release. Resource
caps pass; sampling/terminal gaps and unavailable optional RAM context are disclosed.
New operational access/forward/reconstruction/calibration/optimizer/payload work0;
no model/source freeze, scientific ranking or confirmation claim. Software readiness
does not resolve full-event/count/generation/overlap/precision source blockers.
At Task0035 completion, source adequacy was the next separate scope. Task0036 now
completes the [confirmation-source feasibility decision](docs/confirmation-source-feasibility.md):
`unresolved_no_acquisition` for extra QCD/XtoYYprime under the unchanged protocol.
The pinned exporter includes all EFlow objects before its700-object overflow cut;
release coverage, realized strict-SR signal count and selected expanded storage
remain unknown. Requested50000/card is not a completed total or upper bound.
The236843 zero-variance floor and1450034 variance0.001 requirement remain fixed.
18metadata/text retrievals,0searches and one16084B metadata-card download add no
event-payload/model/numerical work. Source acceptance stays false; publisher-bound
representation/run/count/member evidence is the next prerequisite. Background-only
stability remains conditional; training/acquisition/confirmation are separate,
ungranted scopes. No Task0037 launched.

Task0037 subsequently completes the explicitly authorized
[synthetic trigger/queue engineering study](docs/synthetic-trigger-simulator.md):
one FIFO server, actual waiting+in-service capacity/drop-tail, oldest-arrival
flush, modeled padded partial batches and post-processing Uniform toy decisions.
Accepted historical adapter means supply scoped constant costs; no model executes
in the simulator. The fixed324main+54stress matrix uses18traces/90000unique events /
1890000presentations. Final105targeted/2022full+portable/200bindings/43packages;
two native sweeps are preserved, first visuals rejected for title/legend overlap,
layout repaired/revalidated, final6.105818s parent accepted with all3figures checked.
Numerical CSVs are identical; actual total756scenarios/3780000presentations, no
scenario expansion. Buffering/batching/timeouts affect modeled latency and loss;
constant AE2/B12826.2485ms stress is harsh, not recurring-stall evidence. Final
WARN advisory/caps/deadlines/normal exit/reap/assertion release pass, sampling gaps
and optional RAM-context absence disclosed. Source confirmation remains unresolved,
scientific protocol unchanged; no deployment policy, real inference benchmark or
Task0038 launched by that task. The separately authorized Task0038 below measures
prepared-batch service; missing chain costs remain a later scope.


Task0038 separately completes the authorized
[prepared-batch CPU service measurement](docs/prepared-batch-service-measurement.md).
Natural m-row packing and zero-padded B-row packing use the same frozen models
and four original decisions, retaining only actual rows. Three original prepared
array loads reuse1024unique dev-training rows; six canonical model instances,
204cells/10200timings/2040warm-ups/600empty pairs complete with zero numerical
decision mismatches. Fresh100focused/2122full+portable/211bindings/43versions and
native synthetic acceptance precede the one43.942592s parent-accepted real session,
all exits/reaping/caps/temporary assertion release verified. B1024/m1means
natural/padded17.570/64.592µs PCA and39.320/111.707µs AE; near-full differences
are small/mixed, all slow observations retained. Three inspected figures and
204worker-specific cells are curated; raw timings/ledgers/plans/receipts stay ignored.
This is a new packing/adapter/retention boundary, not replacement of Task0022,
production-p99 or whole-trigger evidence. Task0037 scenarios remain unchanged,
Task0036source unresolved and scientific gates intact. Next separate decision:
source/membership-bound raw-read/full-particle feature-construction timing design;
no automaticTask0039, source acquisition or deployment selection.


Task0039 completes the [development raw-feature foundation](docs/development-raw-feature-benchmark-design.md).
One accepted1.867575s metadata resolver loads only6999development IDs and binds
the ascending1024prefix to the original preparation hash. One raw-byte SHA256
pass2908260409B and one HDFmetadata open verify original schema/Blosc/cache without
event values or numerical golden features. The synthetic narrow adapter selects
only approved rows and reuses full-particle frozen feature arithmetic;88targeted/
2210full+portable/223bindings/43packages/31native files plus native synthetic
integration pass. The fixed future36cell/720timed/108warm-up design accounts all
732raw requests/30927row presentations/768feature calls32448rows including gates
and buffers;384unique requested rows from1024approved,312geometric chunks and
24.501GiB repeated no-cache decoded upper bound, not measured I/O. Cache1MiB/521/
w0.75 verified; decoder effective threading/cold-I/O/real parity/costs unknown.
`future_measurement_execution_authorized=false` remains Task0039's configuration;
that task enabled no operational payload CLI or source confirmation. Task0040
uses the separate authorization/controller below; Task0038/0037 are not rerun.


Task0040 completes the separately authorized [development raw-feature measurement](docs/development-raw-feature-measurement.md).
Fresh100focused/2310full+portable/236bindings43packages31native files/native synthetic
acceptance precede the sole19.498497s parent-accepted session:3original ID loads/
3golden loads,1024approved384rawunique,732selected requests30927rows/768feature
constructions32448rows/36cells720timed108warmups. All pre/post exact golden/repeat
bytes, source identities, normal exits/reaping and7observed sleep assertions/release
pass; WARNadvisory/caps/gaps disclosed, no held-out/model/scientific work. Pooled
B128read45.143/features5.778/directjoint50.013ms, all repetitions/outliers/three
inspected figures retained. Fixed sparse warm-cache study, decoder threading/
physical I/O unknown, no production-p99 or summed whole-chain latency. Task0039's
prospective flag/provider/consumed resolver, Task0038/0037 costs and unresolved
confirmation remain unchanged. Next separate joint preprocessing+original frozen
CPU adapter design/authorization; no Task0041 launch or deployment selection.


Task0041 delivers the [direct development raw-to-decision foundation](docs/development-raw-decision-measurement.md),
with107focused/2417full+portable checks and a15.980657s accepted native synthetic
integration of both frozen-style fixture candidates/all984services/exact gates.
The actual measurement did **not** run: emitted/controller-required acceptance status
literals differ. The freeze check failed; the agent incorrectly continued to the
real controller, which rejected admission in0.455644s before reservation/data/models/
rawhash/assertion/timing and consumed the prerequisite marker. Source/deps/build/
config/prompt match; passingchecks are not controller-admissible acceptance.
The cellCSV is header-only, no real cost figures. No retry/reset or executable repair
after failure. Task0040 remains the latest accepted raw boundary, prior contracts
and unresolved scientific route unchanged. Next separate software-only status-contract,
record-admission roundtrip and stop-on-failed-freeze repair; any new real campaign
needs new explicit authorization/namespace/freeze. No repair or replay was launched
in Task0041; the separate authorized Task0042 follows below.


Task0042 completes the [software-only admission repair](docs/development-decision-admission-repair.md):
one strict producer/consumer schema, correct Task0041 chain identity with Task0042
validation ownership, and checked admission→freeze→one synthetic dispatch.
172focused/2482full+portable tests and a final emitted-record native roundtrip pass;
five accepted fixture integrations/one preserved preliminary failure, assertions
released. Original251-entry source snapshot and Task0041failed record/marker/docs/
emptyCSV remain intact. New status `software_accepted_synthetic_admission_repair`
grants no operational attempt, data/model access or real timing. Task0040 is still
the latest accepted raw boundary; a new real campaign requires a separate prompt,
namespace/current acceptance/freeze/allowance. No Task0043 or source acquisition.


Phase 0.1 establishes the Python package, development tools, tests, CI, data and
results policies, and a CPU/MPS environment diagnostic. The package version is
`0.1.0`. Task 0002 defines the data foundation using the corrected LHC Olympics
2020 R&D particle dataset (Zenodo v5). The [data design](docs/data-design.md)
documents the dataset comparison, background-only protocol, representations, and
provenance plan. Verified acquisition is implemented, and the pinned R&D source
was locally downloaded and checksum-verified in Task 0003. The
[bounded raw audit](docs/raw-data-audit.md) records its schema and integrity checks.
Task 0004 completes the full integrity/duplicate scan, deterministic splits and
[training-background EDA](docs/training-data-eda.md). The
[preprocessing contract](docs/preprocessing-contract.md) is frozen. Task 0005
implements the [deterministic pipeline](docs/preprocessing-pipeline.md), and both
dev and full canonical stores have been locally generated and verified. Task 0006
implements the [PCA baseline](docs/pca-baseline.md), background-only diagnostics
and calibrated thresholds under the [evaluation protocol](docs/evaluation-protocol.md).
Task 0007 adds a frozen [compact autoencoder](docs/compact-autoencoder.md),
reproducible CPU training and separate MPS compatibility checks. Real test
performance was embargoed during those development tasks; Task0026 later completed
the explicitly authorized frozen evaluation, permanently exposing both tests.
Task 0008 closes
[convergence under the frozen patience rule](docs/autoencoder-convergence.md);
v2 is now the canonical compact AE. Task 0009 defines a
[478-parameter particle/set autoencoder design](docs/particle-set-baseline-design.md)
with local bottlenecks, pooled context and a linear-cost reconstruction score.
Task 0010 [implements the unchanged design](docs/particle-set-baseline.md), with
247 passing synthetic tests. Its launch gate failed at 3.69 GiB available memory
versus the frozen 8 GiB minimum, before real reader construction or dev updates.
Canonical training, reproduction, freeze and calibration remain pending.
[Task 0011](docs/particle-set-resource-recovery.md) adds a bounded preflight and
one fixed recovery route. The explicit2026-10-07 resumption after reboot/manual
preparation still failed the8GiB launch test at4.6248–4.6819GiB; continuing4GiB,
RSS and native ceilings passed. No recovery attempt was reserved. All real
particle stages remain pending; these records are committed.
[Task 0012](docs/particle-memory-policy-review.md) adds a separate provisional
launch profile of 4.5 GiB while retaining the 4 GiB floor and all other limits.
Its single check fails both at 2.5443–2.6967 GiB; no reader/dev phase ran.
That pilot did not activate v2; the original scientific config and8GiB policy
remain preserved. [Task0013](docs/particle-host-readiness.md) delivered stdlib
supervision and initial accounting. Its later external study is now reconciled:
reader/full custody and bounded-dev activation passed;1024unique events/96steps
completed, then conservative throughput749.343s failed180s. The slot is consumed;
canonical training/calibration remain pending.
[Task0014](docs/particle-monitor-performance.md) adds a separate cached-binding
monitor preserving all observation/limit/scientific contracts, with471synthetic
tests and exact numerical parity. Fixed shared-host timings improve isolated
collection/checks but show no complete-workload gain(0.382→0.388s). No new real
execution. [Task0015](docs/particle-bounded-sampling.md) implements explicitly
versioned50ms host sampling/≤100ms query-start age with fresh process checks.
Final532synthetic tests pass; paired complete-workload gain2.14× misses the3×
real-budget prerequisite. No readiness/real slot/new data/update; original96steps
remain consumed and canonical particle training/calibration remain pending.
[Task0016](docs/particle-runtime-characterization.md) prospectively replaces that
synthetic admission prerequisite for one diagnostic characterization, preserving
its failed result and the real180s target. Separate authorization adopts unchanged
v4;576synthetic tests pass. One automatic readiness guard observes3.558060GiB and
fails the4GiB floor before data/updates. At Task0016, the shared replacement
additional slot remained unreserved; its historical Terminal route required no app closure
or dedicated use. Canonical stages remain pending.
The later Task0016 manual check separately failed pressureWARN2 with no admitted
available-memory sample. [Task0017](docs/particle-readiness-workflow.md) reconciles
that result and delivers repeatable explicit readiness checks plus a separate
fresh-check run action sharing the same canonical Task0016 slot.612synthetic
tests pass; one check-only integration3.705841GiB fails the floor,0new real work.
A failed safe check no longer needs another task/commit; no automatic polling.
Engineering supports normal Mac use with apps open, without a dedicated window.
[Task0018](docs/particle-shared-host-policy.md) explicitly makes the short-dev
default a tight process envelope:512MiB RSS/256MiB native, global RAM context only,
WARN advisory/CRITICAL veto, unknown pressure disclosed.670synthetic tests pass.
One real shared-host characterization completes reader64/three1024passes/96new
updates with exact Task0013 numerical parity; dev370.016MiB RSS/179.672MiB native
passes. Projection240.728s still fails180s. Shared slot is **consumed192/192**, no
manual rerun/additional allowance. [Task0019](docs/particle-canonical-feasibility.md)
consolidates feasibility: **local canonical particle execution is deferred under
unchanged contracts**. The current projection exceeds180s by33.737977%;200cycles
project13.373797748h/run, and two runs plus the full1hpostfit allowance each
project28.747595497h before other overhead, versus10hfit/run and22htotal.
Historical full custody3.120880127GiB RSS/197.25MiB native is below6GiB/512MiB,
but does not validate multi-hour training or machine-wide headroom. Convergence
and particle usefulness remain unresolved; design/implementation/history remain
available for a separately authorized resource/time/environment decision.
[Task0020](docs/frozen-cpu-benchmark.md) implements the frozen PCA/AE v2 CPU
benchmark with763 passing synthetic/portable tests and one conditional campaign.
Preparation and PCA1 complete; AE1 fails batch-shape reconstruction parity before
timing (1.989305e-6 error versus approximately1.930235e-6 allowed at that value).
The7.989795s campaign is **partial/consumed**:15of90 cells,3000timings, no retry or
tolerance change. No complete two-model/three-repeat comparison is claimed.
[Task0021](docs/ae-batch-parity-review.md) completes a separate AE-only numerical
review:827full/portable synthetic tests, one read of the existing1024prepared rows,
all1193grid windows. Same-shape repeats are byte exact; across-shape reconstruction
and scores violate v1, but all four strict frozen decisions agree on this sample.
The original row7/channel5 failure is confirmed; no performance timing or replay.
[Task0022](docs/frozen-cpu-benchmark-v2.md) implements an explicitly authorized
arithmetic-aware CPU v2 gate, preserving canonical models/FP64 scores/frozen
thresholds and old failures.942full/portable tests and the fixed synthetic study
pass. One new independent campaign completes90cells/18000timings/1800warm-ups,
with pre/post numerical acceptance and zero sampled decision mismatches,25.6615s
whole wall. All three distributions are retained, including slow outliers.
[Task0023](docs/frozen-cpu-mps-benchmark.md) implements isolated CPU/MPS policy,
guards, synchronization/scopes and tests. One bounded check records MPS build=True /
available=False; an initial build-hash serialization defect is preserved and
software-only repaired without a device replay.1033full/portable tests now pass.
No physical device proof, real array read, paired timing or real reservation.
[Task0024](docs/frozen-ae-onnx-cpu-export.md) adds an optional additive ONNX stack
without changing the original36distributions.1111full/portable tests and actual
synthetic integration pass before114-source freeze. One accepted19.4077sattempt
exports the frozen155FP32AE to11464B/opset18/IR10/fourGemm+twoRelu; all four
synthetic families and1193windows of the reused1024rows pass local/outward/repeat /
strict decision gates.1array read,0population/custody/optimizer/performance timings.
Task0025 implements the [paired PyTorch/ONNX CPU benchmark](docs/pytorch-onnx-cpu-benchmark.md):
1179 full/portable synthetic tests and current-source acceptance precede one campaign.
All 90 cells / 18000 measurements and six pre/post numerical gates complete with
zero frozen-threshold mismatches. ORT3 writes its receipt but fails process exit;
the parent terminates/reaps it at 58.031 s. The 128.781 s campaign is failed and
consumed: [raw descriptive distributions](results/tables/final/task0025-pytorch-onnx-cpu-benchmark-cells.csv)
are preserved, with **no accepted paired performance comparison**. One original
and six local prepared reads reuse 1024 rows, zero population/custody/optimizer
requests. Task0022 CPU v2 and Task0024 ONNX equivalence remain accepted; MPS stays
blocked, CoreML planned, particle 192/192 consumed/canonical deferred. [Task0026](docs/guarded-pca-ae-evaluation.md) completes the explicitly authorized
frozen native scientific evaluation after Phase A validation/readiness. One
31.095 s campaign accepts PCA, AE and reporting with normal exits/reaping:
4test requests/124complete4096-tail batches/500942presentations/250471unique events.
**Both held-out tests are now exposed**, with no retraining/recalibration/candidate
selection. Test-mixture prevalence39.9248%; PCA ROC-AUC0.468489/AP0.364379,
AE0.660064/0.547427. AE accepts more sampled signal at all frozen operating points,
but target1e-3keeps only56/100000signal events (PCA2); different6vs3capacity and
accepted native CPU costs limit interpretation. No physical trigger or universal
neural superiority claim. [Comparison](results/tables/final/task0026-pca-ae-scientific-comparison.csv),
[calibrated rates/intervals](results/tables/final/task0026-pca-ae-calibrated-operating-points.csv),
[ROC/PR figure](results/figures/final/task0026-pca-ae-roc-pr.png),
[summary](results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json) and
[handoff](docs/handoffs/0026-guarded-pca-ae-evaluation.md) preserve evidence.
Task0027 completes the [integrated scientific synthesis](docs/scientific-synthesis.md),
[ten-row native quality/cost table](results/tables/final/task0027-quality-cost-frontier.csv),
[eight-point interpretation](results/tables/final/task0027-operating-point-interpretation.csv),
[curated summary](results/tables/final/task0027-frozen-scientific-synthesis-summary.json)
and [static frontier](results/figures/final/task0027-quality-cost-frontier.png) /
[calibrated utility figure](results/figures/final/task0027-calibrated-operating-points.png).
At the strict AE point, TPR0.00056 < achieved FPR0.0007709127; descriptive relative
acceptance0.7264 and selected signal32.5581% < initial39.9248% show no observed
enrichment in this evaluated slice. No new population/scoring/custody/optimizer
work occurred. Particle192/192 remains consumed/deferred; Task0025 remains failed
and consumed with provisional ratios. The user subsequently authorized Task0028 Phase A for a frozen three-prong
extension with the reused accepted exposed background. [Protocol/report](docs/three-prong-generalization.md)
and [summary](results/tables/final/task0028-three-prong-generalization-summary.json)
record fresh publisher metadata, frozen custody/overlap gates and the approved
plan's actual failed/consumed acquisition outcome. [Phase outcomes](results/tables/final/task0028-phase-outcomes.csv)
distinguish298.033887s failed acquisition from four unstarted phases. Original
YES/YES is permanent; new signal model NO, raw acquisition interrupted/inflight
record retained, cached numeric loads0. The frozen downloader removed its own
incomplete `.part`; all surviving receipts/logs/guards are preserved. Any replacement
requires a separate prospective protocol/source acceptance/namespace/human approval;
no existing test becomes fresh.

The existing check command now defaults to shared-host-dev-v1 and stays data-free.
The [living project memory](docs/project-memory.md) maintains current decisions,
evidence, limitations and direction.
Development records follow the
[task protocol](docs/development.md)
and [handoff index](docs/handoffs/README.md).

## Repository structure

```text
latent-trigger/
├── .github/workflows/ci.yml     # CPU-only lint and test jobs
├── configs/data/               # Frozen data decisions and fitted statistics
├── data/README.md              # Local dataset policy
├── docs/                       # Data design, development protocol, task records
├── notebooks/exploration/      # Future exploratory notebooks
├── results/
│   ├── figures/
│   ├── tables/
│   └── benchmarks/
├── scripts/smoke_test.py        # Lightweight PyTorch diagnostic
├── scripts/analyze_training_data.py # Chunked scan, splits and training-only EDA
├── scripts/validate_preprocessing.py # Dev reconstruction and reproducibility checks
├── src/latenttrigger/
│   ├── __init__.py
│   ├── data/acquisition.py      # Pinned, verified LHCO download CLI
│   ├── benchmarks/             # Guarded frozen CPU inference benchmark
│   ├── data/preprocessing.py    # Frozen transforms and verified ragged stores
│   └── utils/device.py          # MPS-first, CPU fallback selection
├── tests/
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

Empty working directories are retained with `.gitkeep` files. Downloaded and
processed data stay under `data/` and are ignored by Git. Generated outputs under
`results/` are also ignored by default. Later, selected final figures and small
result tables can be committed deliberately under `results/figures/final/` and
`results/tables/final/`; these directories are reserved for curated artifacts.
Checkpoints and large experiment artifacts must remain local.

## Installation

Use Python **3.12** for the primary development environment. The supported range
is **3.11–3.12** (`>=3.11,<3.13`), a conservative range with stable PyTorch macOS
ARM64 wheels. Both versions are covered by CI. Use a native ARM64 Python on Apple
Silicon; a standard virtual environment and pip are sufficient.

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data]"
python -c "import latenttrigger; print(latenttrigger.__version__)"
```

Project metadata and dependencies live in `pyproject.toml`. Runtime dependencies
are PyTorch, NumPy and scikit-learn (PCA and mature evaluation metrics). NumPy also
prevents a missing-NumPy warning during PyTorch initialization. The `dev` extra
adds pytest and Ruff. Hatchling builds the `src/`
package and reads the version from `src/latenttrigger/__init__.py`.
The optional `data` extra adds h5py and the source's required Blosc decoder,
hdf5plugin, for raw auditing/preprocessing and synthetic HDF integration tests.
Acquisition itself uses the Python standard library.
The optional `analysis` extra adds Matplotlib for EDA figures; see
[the data workflow](data/README.md) for analysis installation and reproduction.
Dependency ranges allow compatible updates; exact experiment environments will
be recorded when experiments are introduced.

The macOS PyTorch wheel provides CPU and MPS support. MPS availability depends on
the installed PyTorch build, macOS version, and hardware. The project selects CPU
when MPS is unavailable.

For a CPU-only Linux environment, install the CPU wheel before the project to
avoid downloading GPU runtime dependencies:

```bash
python -m pip install "torch>=2.6,<3" --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[dev,data]"
```

## Apple Silicon / MPS diagnostic

With the project environment active, run:

```bash
python scripts/smoke_test.py
```

The diagnostic reports the PyTorch version, selected device, and MPS availability.
It creates a small float32 tensor, moves it to the selected device, checks a
deterministic computation, and prints `Smoke test passed.` only after successful
execution. It downloads no data and trains no model.

The reusable device utility is available as:

```python
from latenttrigger.utils.device import get_device

device = get_device()
```

## Dataset acquisition

```bash
python -m latenttrigger.data.acquisition
```

The command verifies the pinned source before accepting or reusing it. Data and
local manifests remain ignored. See [the acquisition workflow](data/README.md)
for installation, verification, safe replacement, and bounded-audit commands.

With the Task 0004 split artifacts present, build the convenience subset first:

```bash
python -m latenttrigger.data.preprocessing --scope dev
```

The [preprocessing workflow](docs/preprocessing-pipeline.md) documents full builds,
independent verification, bounded reading and the test embargo. Generated arrays
and manifests remain local.

## PCA baseline

With the verified full processed store present:

```bash
python -m pip install -e ".[dev,data,analysis]"
python -m latenttrigger.models.pca --config configs/models/pca_baseline.json
```

This fits training background, selects six PCA components by the 95% training
variance rule, and calibrates/checks background thresholds. It never scores real
test populations. See [the measured report](docs/pca-baseline.md) for results,
reproduction and [the evaluation contract](docs/evaluation-protocol.md).

## Compact autoencoder

With the verified full store and existing analysis extra installed:

```bash
python -m latenttrigger.training.convergence
```

The canonical 155-parameter model trains on CPU, selects its epoch using
selection background, then calibrates thresholds on separate calibration
background. See [the report](docs/compact-autoencoder.md) for reproduction,
the historical v1 artifact and MPS smoke mode. The
[convergence report](docs/autoencoder-convergence.md) records finalized canonical v2;
real tests remain held out.

## Testing

The [frozen CPU benchmark](docs/frozen-cpu-benchmark.md) documents timing scopes,
thread enforcement, numerical checks, caps and the consumed Task0020 campaign.
Its explicit `--run-campaign` action is consumed. The isolated
[AE numerical review](docs/ae-batch-parity-review.md) adds
`python -m latenttrigger.benchmarks.ae_parity_review --run-review` and
`--synthetic-study`; both fixed Task0021 actions have now completed and cannot be
replayed. These historical actions provide no new performance allowance.
The isolated [v2 benchmark](docs/frozen-cpu-benchmark-v2.md) uses
`python -m latenttrigger.benchmarks.frozen_cpu_v2 --run-campaign`; its fixed
Task0022slot is also now complete/consumed. `--validate-prerequisites` remains
metadata-only, never an execution grant.942full/portable checks cover the frozen
new source/policy; raw arrays/timings/receipts/acceptance remain ignored. The
[arithmetic derivation](docs/arithmetic-cpu-v2-policy.md) is frozen separately from
the result report. No replay/reset/alternate output is authorized.

The isolated [CPU/MPS foundation](docs/frozen-cpu-mps-benchmark.md) exposes
`python -m latenttrigger.benchmarks.cpu_mps --run-campaign`. Its one device-proof
attempt is consumed/blocked; the real campaign remains unreserved. Do not rerun:
no old proof or final software-only repair acceptance grants device execution.
[Device derivation](docs/arithmetic-mps-v1-policy.md) requires physical numerical /
accounting proof. New91cases/1033full+portable checks pass; no timing CSV is created.

The isolated [ONNX CPU foundation](docs/frozen-ae-onnx-cpu-export.md) provides
`python -m latenttrigger.exports.onnx_controller --run-export`; its single frozen
attempt is complete/consumed, not replayable. The optional `export` extra and
[pinned wheel/baseline record](configs/dependencies/onnx_cpu_v1.json) document the
additive dependencies; binary exports/diagnostics/acceptances/receipts stay ignored.
No performance campaign or test exposure occurred.

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

Device-selection tests simulate both MPS availability states. CPU tensor and
diagnostic tests perform real computations while forcing the CPU fallback, so
the suite works on ordinary CPU-only CI runners. GitHub Actions runs these checks
on pushes and pull requests for Python 3.11 and 3.12.

To format code during development, run `python -m ruff format .`.

## Roadmap

- [x] Phase 0.1: package foundation, tooling, tests, CI, and CPU/MPS diagnostic.
- [x] Task 0002: select the dataset and define the data/history protocols.
- [x] Task 0003: verified R&D acquisition and bounded raw-schema audit.
- [x] Task 0004: training-background EDA, duplicate-safe splits and schema validation.
- [x] Task 0005: deterministic preprocessing; dev/full stores locally verified.
- [x] Task 0006: PCA baseline and background evaluation; real test populations embargoed.
- [x] Task 0007: compact autoencoder, reproducible CPU model and background calibration.
- [x] Task 0008: convergence closure; canonical v2 selected with unchanged patience rule.
- [x] Task 0009: compact particle/set design, exact loss/score and future resource gates.
- [x] Task 0010: particle/set implementation and synthetic validation; launch gate failed, canonical baseline pending.
- [x] Task 0011: bounded recovery routing/readiness; host still blocks launch, no recovery data attempt.
- [x] Task 0012: launch admission reviewed; provisional 4.5 GiB requirement still blocked, zero readers/dev updates.
- [x] Task0013: lightweight supervision delivered; later external study consumed96steps, passed memory and failed throughput.
- [x] Task0014: external receipts reconciled; v3 resource instrumentation tested on synthetic inputs, no new real access.
- [x] Task0015: bounded-age v4 tested; synthetic2.14×gain below3×, no real revalidation unlocked.
- [x] Task0016: prospective diagnostic admission reviewed; automatic readiness blocked, zero new real data/steps.
- [x] Task0017: independent user-triggered check history/shared-slot run action; manualWARN reconciled, one check-only integration, no real work.
- [x] Task0018: shared-host dev process policy; one complete96step characterization/exact parity,240.728s target failure; cumulative192consumed.
- [x] Task0019: consolidated canonical feasibility/resource/time decision; local particle execution deferred, contracts/history unchanged, zero new execution.
- [x] Task0020: guarded frozen CPU foundation/763synthetic+portable tests; one partial campaign, PCA1measured/AE parity veto, no retry/refit/recalibration/test access.
- [x] Task0021: complete guarded AE numerical parity review/827full+portable tests; v1 failures preserved, sampled frozen decisions agree, no timing.
- [x] Task0022: arithmetic-aware CPU v2/942full+portable tests; complete90cell/18000timing campaign and frozen numerical/decision acceptance; historical failures unchanged.
- [x] Task0023: isolated CPU/MPS foundation/1033full+portable tests; one check build=True/available=False, software hash fix without replay;0real input/slot/timings, no physical MPS acceptance.
- [x] Task0024: additive optional ONNX CPU foundation/1111full+portable tests; one accepted frozen155parameter export and full synthetic/1024row equivalence,0performance timings.
- [x] Task0025: isolated paired CPU foundation / 1179 full + portable tests; 90 measured cells and passing numerical gates, but ORT3 exit deadline fails; consumed, no accepted paired speedup.
- [x] Task0026 Phase A: guarded native scientific evaluation/reporting,1259 tests/source freeze and one accepted full-store custody-only check, no test populations/scores.
- [x] Task0026 Phase B: explicit human approval, one accepted frozen PCA/AE final evaluation, all scientific tables/figure/counts/lifecycle curated; both tests exposed, no post-test tuning/replay.
- [x] Task0027: integrated frozen scientific synthesis; ten adapter cost groups/all eight calibrated points/static figures, zero new scientific execution.
- [x] Task0028 Phase A: isolated three-prong protocol/guarded foundation, 62 new cases / 1333 full+portable tests / protected toy integration; source-bound plan and metadata ready.
- [x] Task0028 Phase B attempt: explicit human approval, one frozen acquisition campaign; failed/consumed at deadline, exit1/reaped, no retry/resume or later phases. Task0028 itself produces no scientific result; Task0031 later supplies the accepted local-file study.
- [x] Task0029: own146-source/1414full+portable/81new-case byte-only acquisition foundation; sole3request session failed/consumed,29990748Bpartial preserved, no verified artifact/HDF/numerical science. Clock and200/206Retry-After limitations recorded.
- [x] Task0031: accepted local three-prong evaluation with shared exposed background; all original thresholds preserved.
- [x] Task0032: integrated two-/three-prong synthesis and quality/cost decision brief; frozen baseline complete within scope, zero new scientific execution.
- [x] Task0033: accepted exploratory frozen-feature/score diagnostics on exposed samples;3requests/350471feature rows,6loads/700942scores,48associations/all24original tails,16suppressed profile rows/two curated figures; no new model work or independent confirmation.
- [x] Task0034: design-only paired activation comparison and conditional independent-source protocol; primary strict-tail estimands/uncertainty/criteria/resource brief, zero operational numerical access; synthetic-only Task0035 proposed, not launched.
- [x] Task0035: separate synthetic controlled-activation foundation;189focused/1917full+portable checks, final native accepted with12toy updates/all6arms/paired orders/own restoration/calibration; zero operational work, confirmation source unresolved.
- [x] Task0036: pinned confirmation-source feasibility completed as `unresolved_no_acquisition`;30evidence rows, unchanged precision/gates, realized counts/complete-event coverage/expanded storage unresolved;1small metadata archive, zero event-payload or operational scientific work.
- [x] Task0037: model-free synthetic FIFO trigger simulator;324main+54fixed stress scenarios/378row table/3inspected figures, fresh105targeted/2022full+portable acceptance, final native parent-accepted with release;2actual sweeps after layout repair, scientific route unchanged/no deployment or physical-inference claim.
- [x] Task0038: one accepted prepared-development CPU natural/padded service study,204cells/10200timings/2040warm-ups, fresh100targeted/2122full+portable, all numerical/lifecycle gates pass and assertion released; no Task0037 rerun or scientific confirmation.
- [x] Task0039: synthetic narrow HDF-to-frozen-feature adapter and fixed future design; one accepted6999-ID resolution/exact1024prefix/raw byte+HDFmetadata custody,88targeted/2210full+portable; real raw/golden/parity/timing unmeasured in that task; its config remains payload-unauthorized.
- [x] Task0040: one accepted development selected-read/full-frozen-feature/direct-joint session,36cells/720timed/108warmups, exact golden parity and original membership/source identity; no models/held-out/scientific work.
- [x] Task0041 bounded outcome: direct CPU chain/planner synthetically validated107focused/2417full+portable; sole real prerequisite failed/consumed before numerical work on inconsistent acceptance status, no measured costs or retry.
- [x] Task0042: strict emitted-record admission and fail-closed synthetic freeze/dispatch,172focused/2482full+portable/current256bindings, final native roundtrip accepted; original Task0041 failure consumed/preserved, zero new operational work.
- [x] Initial native PCA/AE scientific quality versus scoped CPU cost comparison; independent generalization and physical deployment remain open.
- [ ] Feature-level bias diagnostics, capacity-controlled comparison, other signals/populations and strict-tail utility.
- [x] Frozen PCA/AE CPU reference: Task0022 complete and accepted.
- [ ] Physical CPU/MPS comparison: Task0023 blocked, no current device proof.
- [x] ONNX CPU export/structural/numerical equivalence: Task0024 accepted; Task0025 paired performance remains unaccepted.
- [ ] Explore optional CoreML, heterogeneous inference and quantization.
- [ ] Build a trigger-like event-stream simulator.
- [ ] Investigate CUDA/TensorRT on Linux/NVIDIA hardware in later phases.
- [ ] Optionally explore FPGA-oriented deployment with hls4ml.

## Disclaimer

LatentTrigger is an independent project. It is not an official CERN, ATLAS, CMS,
or CERN openlab project and does not imply affiliation with or endorsement by
those organizations. Future trigger-like experiments will be research
approximations whose assumptions and limitations must be documented.

The software is released under the [MIT License](LICENSE).
