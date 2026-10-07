# Task0015 — Versioned bounded-age particle resource monitoring

Preregistration saved2026-10-07 before timing. Operational repository:
`/Users/matteosgobba/Documents/GitHub/latent-trigger`, main→origin/main,
base8d0e3f95d9a65a072ae9fcbae2ea72e2c28c462e. The user continues normal Mac use
with other applications open; this engineering task requires no dedicated window.
Completed: bounded-age monitoring and synthetic validation; fixed paired material
gate failed, so no real readiness/plan/slot/data/update was invoked. The original
preregistration preceded timing and the outcome is appended below.

## Explicit observation-contract decision

V4 is a new engineering observation contract, **not equivalent to v2/v3 fresh
host collection at every guard**. One owned sampling thread starts a one-shot
system `/usr/bin/vm_stat` query on a monotonic50ms schedule; overdue intervals
are counted/skipped rather than overlapped or caught up by spinning. Each
successful immutable publication contains an issuer, increasing generation,
query-start/end/publication timestamps, parsed integers/backend/raw provenance
and validation status. Batch/pre-step guards may reuse it only while
`guard_now − query_start ≤0.100s`, including equality. Publication/read time
never renews age. Fresh launch/readiness/changed phase entry requests are serviced
synchronously by that same thread before work; a missing qualifying refresh
within100ms fails closed. Main/background guards never spawn duplicate queries.

All guards freshly query their own process's native malloc reserved/in-use,
lifetime peakRSS and optional pressure, and check numerical/deadline limits.
The sampler checks process limits every50ms even while its child query is pending;
nonblocking pipe/select handling allows that protection during external latency.
The only child is task-owned and cleaned up on exit/deadline; subprocess timeout
remains2s. Missing/invalid/stale primary data, low availability, pressure veto,
RSS/native excess or collector failure is latched; later favorable data cannot
clear it. Short publication locks are separate from guard/native/journal locks;
no batch lock is held over a subprocess. Main-thread signal and supervisor
import-inclusive deadlines remain in force. Before optimizer mutation, a fresh
process/latest-host guard precedes durably flushed started-step reservation;
completion is persisted after mutation. Partial/inflight steps remain visible.

100ms bounds observation age at a guard, **not guaranteed termination latency**.
OS sampling itself has no exposed generation timestamp: query-start is a
conservative bound for the trusted system-command observation interval, not a
claim of kernel-counter creation time. Scheduling/GIL/native calls/signal delivery
can delay enforcement or cause fail-closed expiration. Python is not hard real
time. This explicit bounded-age compromise avoids per-batch subprocess costs
without pretending reused values are fresh independent host measurements.

The metric remains displayed free+inactive times actual parsed page size. Apple's
[vm_stat source](https://github.com/apple-oss-distributions/system_cmds/blob/main/vm_stat/vm_stat.c)
subtracts speculative from native free for display; no speculative/active/
compressed pages are newly counted. Public
[XNU host implementation](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/kern/host.c)
can cache third-party host-statistics calls, so direct Mach remains diagnostic-only.
No interval stream, alternate backend, privileges or primary-safe substitution.
Original strict parser/cached Darwin ABI/bindings are reused unchanged. Unknown
optional pressure is explicitly recorded; verified warning/critical is a veto.

The strict [v4 manifest](../configs/resources/particle_resource_monitor_v4.json)
binds unchanged mathematical design/config/profile hashes and this prompt,
backend/observation/version/limits and conditional scope. Worker validators
require its exact canonical relationship plus current full source acceptance;
stdlib-only controller also pins its canonical hash. V4 is not a mathematical
model version and grants no canonical training/artifact compatibility.

## Preserved limits, scientific definition and lineage

Launch4831838208bytes(4.5GiB), continuing4294967296(4GiB), native536870912(512MiB),
lifetimeRSS6442450944(6GiB);50ms watch/2s probe; readiness30s spanning≥5s/3fresh
readings, reader60s/dev300s; factor2/180s cycle gate unchanged. Full-run policy
remains36000s fit/run,3600s postfit/run,79200s two-run total, max200/patience20/
min_delta0/earliest ties; none of that canonical scope is authorized here.

Unchanged478-parameter equivariant4→16→8/local2+mean8/shared10→16→4 model,
ordered initialization/seed1729/CPU1+1/workers0/batch32/default exact Adam config,
FP32 network/FP64 pooling-residual-score and equal event weighting. Corresponding
loss/score is valid-particle mean `(r0²+r1²+0.5r2²+0.5r3²)/3`, larger anomalous.
Frozen feature/scaler/mask/Nmax384/split guards unchanged; no model selection from
dev losses, no new input or tuning. PCA and both AE generations preserved.

Task0013's consumed external receipts are reverified read-only:1024unique original
source-ordered dev IDs, first64 reader subset +3072training +1024scoring=4160
presentations/5population requests,96started/completed real updates,0inflight.
Two recorded custody operations plus the dev constructor are distinct from
population access. Bounded-dev v2 activation190340736≤536870912 and memory pass
are historical; throughput fails, not convergence:

```text
train term699957×max([.5065042919995904,.4505980419999105,.45002770899918687])/1024
 =346.22189913589574s
score term74749×.3897375420001481/1024=28.44969875680573s
2×(train+score)=749.3431957854029s>180s
```

No subtraction of overlapping probes, slower-pass removal or factor change.
Task0014's fixed complete workload0.381828500→0.388047000s established no gain.
Those historical records remain intact. New≤96steps would be a deliberately
additional engineering allowance, cumulative≤192, not recovered old allowance.

## Fixed performance matrix preregistration

One matrix≤120s total; nine fresh workers≤30s each including imports. Fixed order:
rep1(v3,v4,compute), rep2(v3,v4,compute), rep3(v3,v4,compute). No best-of selection,
parameter iteration or repeats without a correctness repair. CPU1/1,seed1729,
batch32/Nmax384; exactly the two full/mixed physical synthetic batches from
Task0014, existing frozen model-view transforms;16updates plus8score batches;
at most two physical batches resident. Identical fresh model/Adam/objective.
V3 and v4 retain complete checks, journals, access/step audit and progress IO;
compute-only is diagnostic, never a production monitor option. Both monitored
arms use identical cumulative-audit writes for fair accounting. Hashes compare
ordered parameters/Adam tensors/reconstructions/FP64scores/final objective after
identical work, without persisting weights or score populations.

Actual system snapshots/process-query cost are measured and retained separately
from explicit synthetic9GiB/400MiBRSS/200MiBnative guard fixtures. These permit
synthetic work under low shared-host availability, **never real readiness**.
Import/setup/initialization, workload wall/processCPU, batch/view timings, queries,
guards/process checks/reuse/ages, lock/journal/audit/progress IO and sampler CPU
are reported separately. Nested/concurrent timings overlap and must not be
summed or subtracted from historical749.343s. Fixed repetitions and medians
measure comparative engineering behavior, not real throughput or signal quality.

Real budget unlock requires all correctness/current acceptance/age-enforcement
checks, exact numerical parity and median complete v4≤median complete v3/3.
Missing/failed arm or uncertainty blocks real-plan/readiness/slot creation.
A synthetic3× gain would still not establish the historical4.163× gap or180s.

## Conditional route contract (no execution implied)

Only a passing fixed matrix permits the exact Task0015 plan/readiness route.
A fresh three-reading≤30s readiness is attempted automatically at most once;
insufficient/unknown readiness leaves the real slot unreserved. It is not a
request to close apps or poll. Optional user-chosen Terminal execution shares
that same exclusive slot and performs fresh readiness; it is offered only if
synthetic criteria pass and the slot remains available. Reader/dev workers
independently verify current source/manifest/profile/prompt/parent/token and
launch before any store. Reservation precedes dispatch; duplicate/refailed
phases cannot retry or select another directory. Readiness receipts are separate
from optimizer allowance. Full custody is not replayed.

Fixed phases: fresh first64/two32/zero-update dev-reader≤60s, fresh dev-readiness,
then fresh disposable same1024/three-pass≤96started-updates/one-score dev≤300s.
Original96 + new started/completed/inflight are persisted cumulatively≤192.
Frozen extrapolation `2*(699957*max(train_times)/1024+74749*score_time/1024)≤180s`
includes loading/view/monitor costs. Any reserved/dispatched failure consumes the
attempt and blocks successors. No dev weights reused/persisted, fit/selection/
calibration/freeze/export/trained artifact/full-population request authorized.
Future full-run/artifact compatibility and current custody guarding remain pending.

## Actual validation, measurements and outcome

The paired matrix completed in **14.910046s**, all nine arms below30s including
imports. No best-of selection, dropped repetition or parameter search. Full initial
acceptance was530passing tests. Numerical identities across all nine arms match
exactly, including final synthetic objective0.6362434050239961. Scores/state
hashes are synthetic comparison evidence, not trained model identities.

| Rep /arm | Import/setup s | Enter/init s | Worker incl imports s | Workload wall s | Workload CPU s | Host queries | Fresh process checks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 /v3 |1.208850|0.011061|1.634473|0.387104667|0.259649|55|55|
| 1 /v4 |1.153183|0.059288|1.366780|0.177554792|0.127866|4|73|
| 1 /compute |1.178973|0.001086|1.284771|0.068581667|0.067558|0|0|
| 2 /v3 |1.165585|0.011518|1.583038|0.381356958|0.252948|55|55|
| 2 /v4 |1.160833|0.059193|1.379660|0.179057750|0.129723|4|73|
| 2 /compute |1.172451|0.001039|1.277441|0.069689125|0.068470|0|0|
| 3 /v3 |1.174428|0.009076|1.580567|0.368484750|0.250077|55|55|
| 3 /v4 |1.190355|0.059344|1.410865|0.178179666|0.128946|4|73|
| 3 /compute |1.180481|0.001031|1.289549|0.070384625|0.068863|0|0|

Complete-workload medians: v3 **0.381356958s**, v4 **0.178179666s**, compute
0.069689125s. Ratio **2.140294494×**, below the required3× (v4 ceiling
0.127118986s). Gain is supported for this bounded synthetic comparison, but
**material unlock fails**. Initialization/startup remains in complete workload;
subtracting it or audit/probes to cross3× is forbidden. Three v4 repetitions each
publish4host generations, record72guards/64reuse records/73fresh process checks;
the extra process check occurs while the first query is pending. These are not
72independent host samples. Max guard ages56.246/56.225/56.414ms, no latched
failure, no skipped host interval; all owned threads/children closed. Maximum
observed one-shot query durations7.903/6.863/7.308ms; measured costs do not
establish future scheduling or kernel freshness guarantees.

| Rep | v3 check/probe/lock wall s | v4 guard/native/lock wall s | v4 journal wall s | v4 sampler CPU s | v3 /v4 audit81saves wall s |
| --- | --- | --- | ---: | ---: | --- |
| 1 |.294558/.268082/.022508|.010352/.008385/.000034|.001260|.017145|.028921/.034607|
| 2 |.288117/.262813/.021692|.014797/.009127/.000324|.004629|.016274|.028766/.028438|
| 3 |.270745/.252829/.014344|.014107/.008534/.000034|.004792|.016771|.031088/.027890|

V3 serializer/write/flush and watcher timers, all progress-file/view/batch/import
CPU timings and exact per-repetition statistics are curated in the summary.
V4 journal timer includes JSON serialization/write/flush; these components are
not independently exclusive. ThreadCPU, queries, guards/audits and wall time
are nested or concurrent, never added as exclusive attribution or subtracted
from historical749.343s. V4 avoids repeated host queries per batch and has a
longer synchronous startup refresh here; residual work includes physical views,
input/finite checks, FP64 math, model/Adam and durable audit IO. Fixed order,
cache/import/scheduling/shared-host variation limit causal/statistical claims.
No historical real extrapolation is recalculated from synthetic timing.

Actual OS availability in paired arms was4.2344–4.3654GiB, parsed page size16384.
Those are query-cost observations, not three-reading readiness or launch acceptance.
Optional pressure remains unknown where Darwin access is restricted. Synthetic
9GiB host/process fixtures are separately named and never promoted to production
readiness. No app content/inventory/termination, cleanup or exclusive use requested.

### Final review correction and renewed acceptance

After the matrix, inspection found that a process-limit veto happened before
updating reported process maxima, so the failed RSS/native reading could be
omitted from maxima. The guard already stopped correctly. A narrow correction
now retains actual own-process observations/global and existing-phase maxima
before the veto, and includes the failed observation in the failure receipt.
No mathematical/threshold/observation change or timing-driven adjustment. Two
new synthetic cases verify actual failed values; earlier530-test acceptance and
matrix bytes are preserved. Current **532tests pass in5.57s**, new61over Task0014;
actual source-bound final acceptance is separate from the original record.

Only affected v4 validation was repeated, fixed reps1/2/3 in three fresh workers,
4.794864s overall, each≤30s. This is **not a second paired gate** and cannot replace
or combine favorably with the original comparison. Final-code v4 workloads are
0.177907208/0.175391500/0.176332042s (median0.176332042), CPU
0.130350/0.127464/0.128133s; same exact numerical identities,4queries/72guards/
73process checks each, max ages56.653/56.339/56.264ms, no errors/owned leaks.
Original pre-correction paired timing is labeled with its own source/acceptance;
current source requires final acceptance. The real route rejects material/source
unlock. No claim that this follow-up qualifies a3× gain; no further timing search.

Full Ruff lint/format63Pythonfiles, dependency consistency and explicit CPU16smoke
pass. The initial generic package smoke command was unsupported because no
`__main__` exists; it did not access data and was replaced by explicit CPU work.
The full pre-correction suite also passed in a temporary checkout with no data/
.git (530tests5.92s); final affected61tests also pass in2.34s without operational data/.git. Final
review verifies153unchanged old tracked files/61historical engineering records,
131local links,14intended files, JSON/arithmetic/whitespace and empty index. Actual profiler again measures5228448bytes at batch32/full384,
478parameters/two synthetic Adam updates. This is tensor allocation, not real
reader/native footprint. Hosted CI and future real v4 behavior remain unverified.
Tests cover ages/equality/staleness/generation/timestamps, primary arithmetic/
parser parity, partial/slow/error queries, latched failures, pressure/limits,
concurrent guards, fresh per-boundary process checks, signals/deadlines during
blocked work, owned cleanup, strict source/manifest, stdlib parent/worker bootstrap,
phase/budget/order/duplicate/readiness timeout behavior and exact numerical
parity. Ordinary tests use self-contained fixtures, no operational receipts/data.

### Completion and next dependency

**Engineering completed; material-improvement gate failed; canonical baseline
pending.** Task0015 new custody/population/events/started/completed/inflight
updates: **0/0/0/0/0/0**. No readiness, plan, ledger/attempt, reader, dev or any
later canonical stage was dispatched. Original96real updates remain consumed;
new allowance is unspent but **not unlocked**, cumulative96/192conditional ceiling.
The optional real Terminal route is **not available for this outcome**: the
material prerequisite failed, regardless of the unreserved slot. The supported
controller refuses it; do not use another output/task label to evade that result.

V4 is implemented/synthetically validated, not activated on real data or compatible
with finalized full-run artifacts yet. Task0014's proposed v3 rerun is superseded
by this explicit bounded-age decision/evidence. Next requires only a new bounded
engineering/runtime-budget decision, with explicit authorization if any additional
work is chosen. No automatic optimization allowance,3×/180s relaxation, real
benchmark, model tuning or Task0016 training. The180s target connects200cycles to
10h/run and22h two-run budget; historical749.343s is a projected small-sample
engineering failure, not measured full fit or convergence. Any budget review must
be versioned. Shared-Mac use stays an enduring preference; no readiness window
is required to finish this task.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Original scientific JSON/profile/v2/v3 implementations and historical source
acceptances/manual receipts/ledgers/results/artifacts remain byte-identical.
Only README/current memory/index change among pre-existing tracked files. Ignored
local evidence contains initial snapshots, both acceptances/log/XML/profiling,
one original paired matrix and separate affected-v4 repair validation, portability
records; no data arrays, weights/individual real scores or production launchers.
See [handoff](handoffs/0015-particle-bounded-sampling.md) and
[curated summary](../results/tables/final/task0015-particle-bounded-sampling-summary.json).
