# Particle resource monitor performance — Task0014

## Preregistration before the benchmark matrix

Task0014 runs with the user's applications open, ordinary shared-host use. No
request for a dedicated machine, closing Codex/apps, reboot, readiness window or
real run. Base9d5e03b459a7edc9801a499dccb3a4b1d8cc8f78, clean main/origin/main;
Task0013 commit verified after53b238a. Source/config/receipt hashes are snapshotted.
Current numerical/scientific contracts, sidecar and old runtime remain unchanged.

External Task0013 receipts establish memory/reader/custody and bounded-dev
activation, then throughput failure. The original slot and1024/three-pass/96step/
one-score dev allowance are consumed. No reset, replay, weights reuse or new real
custody/population/events/optimizer step in this task. Full fitting/selection/
restoration/reproduction/freeze/calibration remain unauthorized/unreached.

One fixed six-arm matrix: isolated collectors → old complete checks/journal/audit
→ v3 complete checks/journal/audit → diagnostic compute-only workload → old
instrumented workload → v3 instrumented workload. Overall120s;30s/arm including
imports/CPU preparation, fresh processes, CPU1intra/1inter/deterministic, seed1729.
Collectors16samples each in order old/cached-system/direct-Mach-diagnostic; every
sample retained, no best-of selection. Complete-check arms32synchronous checks
plus unchanged audit saves/background watcher. Workloads16syntheticAdam steps
then8synthetic scoring batches, batch32/Nmax384, at most two physical synthetic
batches resident (full384 and mixed1/48/96/192/384 prefix masks). Use existing
frozen model-view transformation/scalers and corresponding objective/optimizer.
Same two generated inputs/order/initialization/updates across workload arms.

Each instrumented arm performs the actual read-only collector but validates an
**explicit synthetic9GiB guard fixture**; actual OS samples are separately named
and retained. This makes ordinary synthetic validation possible on a shared Mac
without calling those fixtures readiness or accepting a failing real production
stage. Compute-only is diagnostic, never a production no-monitor option. No data
reader/store/real IDs/labels or production workflow entry point. Audit IDs and
request strings are clearly synthetic, in the ignored benchmark directory.

Timing boundaries: external whole arm/import/setup; workload wall/processCPU;
isolated probe wall/processCPU; per-batch and model-view wall; audit saves;
monitor lock wait/probe/serialization/write+flush/watcher wall. V3 timers are
nested/overlapping (process CPU includes multiple threads); do not sum them as
exclusive time or subtract them from historical real pass times. Old collector
calls are wrapped for probe wall/CPU; old journal/audit behavior remains intact.
No performance-dependent parameter search or repetition. If a correction is
needed, retain failures and renew source acceptance before affected-arm work.

## Reviewed observation semantics and selected implementation

Direct public Mach HOST_VM_INFO64 rev1 is implemented **diagnostic-only**, with
cached bindings, validated152-byte/38integer-count ABI, actual kernel page size,
return/count checks and raw native counts. Exact display normalization subtracts
speculative_count from native free_count before adding inactive. Impossible
subtraction/type/width counts fail. No invented vm_stat raw text for this backend.
Installed SDK count/offset/task/malloc ABI is checked via a small compiler input
embedded in accepted benchmark source; temporary generated ABI executable only
prints constants. No new dependency or privilege/configuration change.

[Apple vm_stat](https://github.com/apple-oss-distributions/system_cmds/blob/main/vm_stat/vm_stat.c)
uses the displayed free convention; its interval stream can abbreviate overflowing
columns. [VM structures](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/vm_statistics.h)
and [host definitions](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/host_info.h)
establish the public ABI. [XNU host.c](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/kern/host.c)
rate-limits third-party calls using cached results in a one-second window with a
random2–10request allowance, while platform binaries take a different path. The
API gives no generation timestamp. Fast/unchanged/changed values do not prove
50ms freshness, nor are published main-branch sources proof of the exact running
kernel's internals. Native-direct is not selected for enforcement; no entitlement
or privileged-port workaround. Installed OS/SDK and read-only system-signature
metadata will be retained with the benchmark, with unavailable checks explicit.

A long-lived vm_stat interval stream was considered but not selected: latest-value
reuse would weaken synchronous before/after-batch observation; waiting for a fresh
50ms sample at every check would add latency. Output abbreviations/partial delivery/
unexposed acquisition timestamps add protocol complexity. No unvalidated stream
implementation is exposed or claimed supported; no owned persistent stream child.

The conservative v3 candidate retains a new exact `/usr/bin/vm_stat` snapshot
**on every check**,2s external timeout and existing display/page-size metric. It
caches library/symbol/signature bindings only, not primary values. Whole native
malloc/current/lifetimeRSS/optional pressure are sampled per call. Strict v3
implementation manifest binds unchanged design/config/profile, identical numerical
limits, source acceptance and **no real/full-run authorization**. V2 JSON/runtime
stay byte-identical. Monitor retains50ms watcher, serialized synchronous guards,
original signals/deadlines, stage minima/peaks and pre-step audit reservations.
Owned journal handle is flushed every sample (same OS-flush durability class,
no fsync claim) and closed on exit; no asynchronous reservation or unchecked gap.
A primary observation older than2s from query start is rejected conservatively;
API generation is unexposed within the synchronous system query interval. Detection
still includes watcher wait, probe, lock, GIL and OS delivery, never a hard50ms bound.

Synthetic CI review found Task0013's lineage fixture copied ignored operational
receipts. It is made self-contained while retaining the original assertions;
accepted historical test bytes remain in commit9d5e03b and are verified explicitly
when reconciling that sole test-source change. Scientific/runtime source and all
old records remain byte-identical. New reconciliation tests use synthetic receipts,
not ignored machine files. No CI workflow/dependency change.

## Reconciled external study: immutable real history

The external slot was reserved2026-10-07T09:19:08.489981UTC (11:19:08.489981
Europe/Rome) and is consumed. Pilot readiness8.814041/8.728348/8.697464GiB passed;
dev reader64 and separate full-store custody passed. Full custody lifetimeRSS
3351019520bytes/native206831616bytes stay below6GiB/512MiB; no full-population
model request. Exact v2 activation passed **bounded dev only**:
56123008incremental bound+134217728margin=190340736≤536870912bytes.
Dev readiness passed. No inference of present host availability or full-run scope.

Five recorded dev/train-background population requests: first64 reader views,
three1024training passes and1024scoring=4160presentations within the same1024
unique source-ordered IDs.96started/completed updates, no inflight, no allowance
left. Two recorded constructor-custody operations(dev reader/full custody), plus
a separate dev-stage verified constructor established by source/verification
receipt0.030140417s, which is not recorded in custody_access. This distinction
prevents silently calling the dev reader constructor a population request or
claiming its empty custody list means no constructor ran. No test model access.

Training timings `[0.5065042919995904,0.4505980419999105,0.45002770899918687]`s,
score0.3897375420001481s per1024. Preserve the slowest pass and factor2:

```text
training term =699957×0.5065042919995904/1024 =346.22189913589574s
scoring term  =74749×0.3897375420001481/1024  =28.44969875680573s
conservative projection =2×(training+scoring)=749.3431957854029s >180s
```

This is projected from a small development sample, not a measured full epoch.
Memory/activation passed, throughput failed; not convergence failure. No canonical
fitting/selection/restoration/reproduction/freeze/calibration/artifact was reached.
Do not subtract probes, remove the first/slowest pass, alter factor2 or target.
The historical failed result/progress/score hash and all original receipts remain
byte-identical; original Task0013 curated pending summary/report are task-time
records, superseded for current state by this reconciliation, not overwritten.

Call graph: original ResourceMonitor/PolicyMonitor launch/phase/deadline checks,
before/after every epoch batch and50ms watcher → serialized check lock → vm_stat
subprocess+fresh library/classes/symbol lookup+malloc/Mach/pressure → guards,
compact JSON append/open/write/close. ParticleBatches prepares the frozen view,
advances/saves audit and observes/saves IDs. Adam observer reserves/saves before
mutation, completes/saves after. Store verification, shuffle, transforms, finite/
mask/angular validation, loss/backward/optimizer and score also consume time.
Journal records287probes/1.316605680018256s total/max0.00705841600029089s.
Worker3.0156337919997895s includes1.1284318750003877s import/setup. Probe sum is
nested synchronous/background work across phases, not an exclusive critical path.
Historical CPU/lock/thread/IO split was not measured; no app blame/all-cost claim.

## Actual fixed synthetic matrix

One matrix completed in11.199130208s, every fresh arm below30s including imports.
No affected-arm retries/code correction needed, no source edit after acceptance
or measurement. Applications remained under ordinary user-controlled use; no
cleanup, readiness poll, app-content inspection or dedicated window requested.

| Isolated collector | Samples | Mean wall ms | Min /max wall ms | Mean processCPU ms | Enforcement eligibility |
| --- | ---: | ---: | --- | ---: | --- |
| old | 16 | 5.099982 | 4.052250 /10.826084 | 2.283313 | retained exact system snapshot semantics |
| cached_system | 16 | 3.657977 | 3.430750 /3.828083 | 1.551438 | retained exact system snapshot semantics |
| direct_mach_diagnostic | 16 | 0.098175 | 0.086583 /0.150125 | 0.098250 | diagnostic only; cache age unexposed |

Isolated calls exclude collector construction, SDK and signature queries; external
whole-arm time includes them. No best-of timing or discarded samples. Direct16
calls reported only2distinct native free/speculative/inactive triples; consistent
with caching, not proof of sample freshness/cache age. SDK compiled constants
`38 152 92 48 32` verify rev1 count/size/speculative offset/task/malloc layouts.
Actual reported OS26.6.2/kernel25.6.0/xnu12377.161.14~5/arm64; raw signed-system
vm_stat metadata says platform identifier26, authority display unavailable.
Published source behavior informs risk, not an exact running-kernel proof or
reason to grant direct-Mach enforcement. Full metadata/raw counts remain ignored.

| Arm | Whole worker incl imports s | Workload wall s | Workload processCPU s | Probes | Audit saves /wall s |
| --- | ---: | ---: | ---: | ---: | --- |
| collectors | 2.603338417 | — | — | 48isolated | — |
| checks_old | 1.402281209 | 0.178666958 | 0.095518000 | 35 | 33 /0.010486917 |
| checks_v3 | 1.350722875 | 0.160282542 | 0.083482000 | 35 | 33 /0.010676498 |
| workload_compute | 1.260072833 | 0.070795750 | 0.069235000 | 0 | 0 /0.000000000 |
| workload_old | 1.594536250 | 0.381828500 | 0.251420000 | 55 | 81 /0.015134248 |
| workload_v3 | 1.587866125 | 0.388047000 | 0.256724000 | 55 | 81 /0.015999877 |

Isolated mean cached-system collection is28.275%lower, complete-check wall is
10.290%lower. **No complete-workload speedup was observed:** old0.381828500s,
v30.388047000s (1.6286%longer); compute-only0.070795750s. Fixed order/cold imports/
cache/scheduler/normal shared-host variation limit attribution. These are short
synthetic point observations, not latency benchmarks, real throughput acceptance
or proof of a significant improvement. No parameter selection or repeated search.
All32check and24batch/16collector timings are retained in local receipts and
curated summary rather than selecting minima. Common diagnostic progress IO is
included in workload wall; per-batch timers exclude the subsequent progress write.

V3 workload overlapping wall timers: check0.305719083s, probe0.277591498s,
lockwait0.024046294s, serialization0.001292213s, journalwrite/flush0.000717333s,
watcherchecks0.042704373s. Actual wrapper probe0.276491255s counts55samples;
small differences reflect fixture/wrapper overhead and timer boundaries. Audit
81saves0.015999877s. Do not add these nested/concurrent timers or subtract them
from original749.343s. Old workload55probes0.273928416s/audit0.015134248s confirms
instrumentation is material in this workload, without exclusive causal accounting.

All three workload arms have exact same ordered FP32 parameters, Adam tensors,
reconstruction/FP64 score byte hashes and final objective0.6362434050239961 after
16syntheticupdates. Comparison hashes are synthetic evidence, not trained/frozen
particle artifact identities. Same unchanged model/objective/initialization/Adam,
view/scalers/batch/thread settings; no real weights reused or persisted.

Observed OS availability during isolated collections is approximately3.320–3.331
GiB, below production floor; this is **not** readiness. Actual samples remain
separate from the explicit9GiB fixture used only on synthetic work; no failing
live production check was relabeled accepted. No real admission/run attempted.
Native direct output keeps raw/normalized counts separately, no fabricated text;
permission-restricted optional pressure remains unknown. Current real reader/full
training behavior under v3 is unmeasured, all numerical limits stay unchanged.

## Validation, preservation and implementation status

Full final suite **471passed in5.28s**, including49new synthetic tests; existing
Task0013 fixture assertion coverage preserved with self-contained CI records.
Targeted combined106passed. Actual producer bound source/XML/log exit/counts and
unchanged synthetic allocation measurement5228448bytes/478parameters/2Adam steps.
No hand-set acceptance flags. Ruff61Pythonfiles/lint/format, dependencies/no broken
requirements and explicitCPU16smoke pass; no dependency or CI workflow change.
A second portability check ran471tests in a temporary synthetic checkout with no
operational data/ or .git(5.81s), then removed it. This verifies self-contained
fixtures, not hosted/LinuxCI. Final preservation covers142old tracked files,
32manual receipt hashes,127local links and exact14-file scope/empty index; JSON,
source/manifest/numerical/time/byte identities and whitespace checks pass.
Current source acceptance covers all four new modules, tests and embedded SDK ABI
helper code; temporary compiled executable is derived from that stamped input,
not an unstamped launcher in ignored data. HostedCI unverified.

Tests cover native speculative normalization/overflow/impossible subtraction,
ABI/unsupported/return-count behavior, optional/primary unknowns, exact limits/
pressure veto, collector timeout/no fallback/staleness, concurrent flushed journal,
expired deadlines, failure receipt, strict manifest/current source relationships,
stdlib parent, fakeguard rejection for live checks, deterministic state/Adam/
reconstruction/loss/score parity and synthetic historical-budget reconciliation.
Owned process cleanup uses existing tested supervisor; no persistent stream child.
Production resource collector/guard exceptions remain fail-closed, synchronous
reservations unchanged. V3 is implemented/tested, **not real-activated**.

Old v2 JSON/collector/runtime, model/scalers/reader/training/dev and scientific
artifacts/Task0013 manual receipts stay byte-identical. Sole prior executable-file
change is a test fixture portability repair; its accepted original is verified
from commit9d5e03b when checking historical source identity. No historical handoff/
summary overwrite, Git staging helper, ledger reset or new real slot. Final
history/link/JSON/whitespace/scope checks are recorded in the handoff.

## Proposed next validation; no authorization here

Propose **Task0015 — Bounded Runtime Revalidation under the Reviewed Monitor**:
separate versioned user prompt/execution manifest binds actual v3 implementation,
unchanged profile/math, fresh complete source acceptance, consumed lineage and
one non-retryable output/ledger. One fresh three-reading readiness, fresh guarded
dev-reader(first64/two32/zero updates) under60s, fresh dev-readiness, then one
same fixed1024/three-pass/96started-updates/one-score disposable gate≤300s,
view preparation included, factor2/180s unchanged. Preserve phase/minima/peaks/
sample method-age/pre/post step/inflight/failure records; any failure blocks
later execution. No full-store custody replay solely as ceremony, selection,
calibration, artifact, weight reuse or architecture/score tuning. Old full custody
validates its old monitor/environment; future full-run compatibility/live full-store
coverage remains a separately authorized prerequisite.

An additional96steps is **proposed, not granted**, justified by changed monitored
gradient/score workload. It must be explicitly authorized and accounted cumulatively
(original96+new≤96→192started), same1024frozendev IDs, no model-selection allowance.
No new ledger or real route is created in Task0014. No synthetic speedup or passing
180s claim; recorded component benefit and complete-workload uncertainty must be
carried into the next prompt. If more engineering evidence is chosen first,
review only synchronous collection/lock/IO with a separately bounded protocol.

180s supports max200cycles×180=36000s/10h perfit; twofits72000s plus7200spostfit
fits79200s/22h total. The failed conservative749.343s projection is4.163×target;
200such projectedcycles≈149869s/41.63h perfit is an illustrative budget conflict,
not measured training duration or convergence. Any future target/resource-policy
review must be explicit/versioned; no silent limit/horizon/device/model/HPO change.
Normal app use may affect future availability/timing; user chooses scheduling and
contemporaneous guards decide. No dedicated Mac, closing apps/Codex, reboot,
another readiness window or indefinite polling is required to finish this task.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Task0014 new real custody/population/events/steps: **0/0/0/0**. Historical steps
now reconciled96, remaining original0, no inflight. Canonical particle model
and all selection/restoration/reproduction/freeze/calibration remain pending.

| Identity | SHA256 |
| --- | --- |
| v3 manifest canonical | `ad786f3cdd779e7ffdb33ec12d78c46d5bdc2a207fd4570b60a736855d6a344a` |
| Unchanged v2 profile | `a3e237d8a191d9b906744a497ef7e687c739bc8418dd2e53e78db3e54b24d287` |
| Unchanged mathematical config | `48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b` |
| Actual471-test acceptance | `c4b4415627ade9ec0fd906d1784f213503203caf1185e3392eeb812cc21dece0` |
| Current source-map canonical | `5f8c4f2aadcfba0d4ced92ae1965e758aabe75480582a9329c01bfcf65430509` |
| Fixed benchmark preregistration | `690f0b9df4a3905eceef029c0f28cd1f6da636aac9b5ec98a37b857353379ed8` |
| Actual matrix receipt | `209ff911f70b7d90fc72eea23cd8bb77d34815eebe2f1b504e2f9fcd590ee56a` |

See [curated evidence](../results/tables/final/task0014-particle-monitor-performance-summary.json),
[implementation manifest](../configs/resources/particle_resource_monitor_v3.json)
and [handoff](handoffs/0014-particle-monitor-performance.md). Memory revision1.7
updates current consumed-slot/throughput/monitor state in place, preserving
canonical PCA/AEv2 and historical memory entries. No automatic Git delivery.
