# Task0018 — Shared-Mac development process policy

Task0018 explicitly replaces the short-development admission heuristic with
[shared-host-dev-v1](../configs/resources/particle_shared_host_dev_policy_v1.json).
This is a versioned engineering decision authorized by the
[actual prompt](prompts/0018-particle-shared-host-policy.md), not a mathematical
model revision or v4-equivalent execution. The user's Mac remains in normal use
with other applications open. No cleanup, dedicated window, reboot, polling,
monitor benchmark or extra optimizer budget is requested.

## Preregistered envelope and rationale (before real access)

| Contract | Historical v2/v4 dev | Shared-host-dev-v1 |
| --- | --- | --- |
| Displayed free+inactive × actual page size | Launch4.5GiB, continuing4GiB; v4 age≤100ms | Optional context only; no minimum/floor/age veto |
| Lifetime own-worker peakRSS |6GiB|512MiB =536870912bytes|
| Whole malloc reserved |512MiB|256MiB =268435456bytes|
| Verified pressure NORMAL1 |Permit|Permit and record|
| Verified pressure WARN2 |Veto|Advisory, permit and record|
| Verified pressure CRITICAL4 |Veto|Veto before data; latch during work|
| Optional pressure unavailable |Disclose unknown|Disclose unknown, permit under tight process/time bounds|
| Primary own-process accounting unavailable/malformed |Fail closed|Fail closed|
| Host queries |50ms host sampler; fresh phase refresh and100ms batch age|One bounded optional system snapshot at startup/phase boundaries|
| Process guards |Fresh at each boundary/pre-step|Fresh at each boundary/pre-step, periodic50ms intent during blocked work|
| Stable global readiness |3readings≥5s within30s|No stability wait; integrity + fresh own-process/pressure preflight≤30s|

The historical Task0013 small dev reached385089536bytes (367.25MiB) lifetimeRSS
and175816704bytes (167.671875MiB) native reserved. Later startup measurements
188399616bytes (179.671875MiB) leave76.328125MiB below256MiB; the dev RSS leaves
144.75MiB below512MiB. These declared process envelopes provide headroom relative
to measured development workers; they do not guarantee machine-wide availability.
RSS/native overlap and must not be summed as disjoint allocations.

The full custody worker reached3351019520bytes RSS and206831616bytes native:
its mapped/full-store footprint is distinct.512MiBRSS is **not a full-store or
canonical-training ceiling**. The small dev manifest contains8494events and
23046077persistent file bytes (21.979MiB, approximately23MB decimal). Full
constructor verification remains mandatory; inspection reads only that small
manifest and historical engineering receipts, without reopening data.

Apple describes pressure using several indicators, including free memory,
swap rate, wired memory and cached files. [Apple memory guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac).
XNU defines dispatch flags1/2/4 for NORMAL/WARN/CRITICAL.
[XNU event definitions](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event_private.h).
Our WARN-advisory and unknown-pressure tolerance are prospective project decisions
for this bounded development scope, not Apple recommendations or proof against
host exhaustion. Allocation/IO/OOM/numerical errors still stop the attempt.

## Implementation, identity and unchanged science

New narrowly scoped process guard reuses cached verified Darwin malloc/getrusage/
task-info/sysctl bindings, existing monitor deadlines/signals, bounded journals,
owned cleanup and the existing pre-step guard/durable step reservation hooks.
Each guard makes a new process query, validates native reserved/in-use types and
method, records actual failed measurements/peaks, and enforces local caps/CRITICAL.
Unknown pressure stays unknown with errno/provenance. Failures latch permanently.
A50ms-intent watcher checks process/pressure/deadlines while constructor/context
work blocks; main-thread signals and parent import-inclusive deadlines remain.
Scheduling, GIL and signal delivery limit practical enforcement/termination;
no hard-real-time latency claim is made.

Optional context uses the existing owned system one-shot vm_stat/parser (displayed
free+inactive, actual page size, no speculative addition), at most2s per query.
Its actual raw output/backend/query-start/end/age/status is retained in bounded
ignored evidence. Low counts, parser/permission/timeout errors or age>100ms cannot
veto work. Context queries occur outside the process-guard lock; periodic process
protection continues. A primary/latched/deadline exception is never swallowed by
context error handling. No direct Mach/stream/new OS backend, artificial pressure,
privilege workaround, OS tuning or app-management action.

Strict typed sidecar binds exact prompt/model/design/input and historical policy/
v4 hashes. Actual execution plan binds the whole new source map/current synthetic
acceptance, policy, original receipts and canonical additional anchor. Unknown
keys/threshold overrides or altered science are rejected. Original model JSON,
v2/v3/v4 manifests/collector/sampler/guard/math are preserved. Only the old CLI
`main` delegates to the new default; original accepted router bytes are verified
from actual commitb194050, with an exact one-path exception. Every other historical
612-source entry must still match its accepted bytes. No wholesale identity waiver.

Science remains478parameters/local2+mean8/shared10→16→4, same frozen4channels/
scalers/Nmax384/masks, sole weighted corresponding residual, FP32network and
FP64pool/loss/score, equal event weights, seed1729/exactAdam/batch32/workers0/
CPU1+1/determinism. Numerical limits180s cycle/projection, max200/patience20/
min_delta0,10hfit/run,1hpostfit/run and22htotal are unchanged full-run contracts;
**no full-run execution is authorized here**. No calibration/test populations.

## Default CLI and one unchanged real slot

```bash
cd /Users/matteosgobba/Documents/GitHub/RareGate
.venv/bin/python -m raregate.supervision.particle_readiness --check-readiness
```

Check-only is repeatable by separate explicit user invocations, saves an immutable
unique history ID under `data/baselines/particle-readiness-history/shared-host-dev-v1/`,
and never opens stores/model/optimizer, requests data, scores, creates a real plan
or reserves a slot, even when READY. It prints the chosen policy/dev-only scope,
local readiness, optional global context and pressure truthfully. Full JSON saved;
`--json` optionally prints it.0=ready;2=CRITICAL/local-cap not-ready;1=integrity/
unsupported/accounting/timeout/interruption error. Unknown pressure is not NORMAL.
A consumed real slot is reported separately from resource readiness.

The deliberate action used once in Task0018 is shown for interface review.
**Its shared slot is now consumed; do not execute it again.** Check-only remains
repeatable and cannot replenish that allowance:

```bash
cd /Users/matteosgobba/Documents/GitHub/RareGate
.venv/bin/python -m raregate.supervision.particle_readiness --run-characterization
```

It always owns a new≤30s process preflight; no caller-provided/history bearer
receipt. After a pass, exclusively/atomically create the same Task0016 anchor
`data/baselines/task0016-runtime-characterization-attempt.json` before data.
Output remains `data/baselines/task0016-runtime-characterization-study/`; separate
current plan `data/baselines/task0018-shared-host-dev-execution-plan.json`.
Old plans/checks are preserved, no alternate output or new Task0018 allowance.
Concurrent old/new launch routes can have at most one anchor winner; loser opens
no data. Existing foreign/partial/inflight/consumed reservation refuses work,
including if interruption happened before any optimizer step. No reset or retry.
Older stale source-bound routes cannot bypass current permission.

Fresh workers independently check current source/policy/model/profile/plan/slot/
parent/token/phase and local launch conditions. Fixed phases dev-reader≤60s,
fresh process-only dev-readiness≤30s, then dev≤300s including imports/verification/
views/guards/audit/cleanup. Only dev store and train_background/dev_only accepted
before constructor. First64 of original1024source-ordered IDs/two32views/zero
updates; then disposable fresh model, same1024IDs/seed/shuffle, three passes≤96
started steps and one same-sample score pass. Durable started/completed/inflight
accounting retains original96+new≤96/cumulative≤192. No dev weights or individual
score persistence, full custody replay, selection/calibration/test/fullfit/freeze.
The run action is authorized once conditionally in Task0018 after acceptance;
its actual outcome below determines whether a manual run remains available.

## Validation and actual outcome

**Completed bounded characterization; original throughput target failed.**
One process preflight passed, one canonical anchor was reserved and the fixed
reader/process-readiness/dev workers completed. No retry or real phase replay.
The source map remained identical to the frozen actual acceptance throughout;
subsequent changes are documentation/curation only.

Actual validation: **670synthetic tests pass in7.37s (58new)**; the same670 pass
in6.91s in a temporary checkout without operational data or `.git`. Ruff lint/
format78Pythonfiles, dependency consistency and CPU smoke16/PyTorch2.14.1 pass.
Fresh batch32/full384 CPU profiler:478parameters/two synthetic Adam steps,
5228448peak tensor bytes. This is not real process RSS/native footprint.
Coverage includes low global/WARN/unknown permitted, CRITICAL/caps/equality/
malformed primary/provenance/latching/failed peaks, optional context errors and
age>100ms non-veto, watcher during slow context/blocked work, deadline interruption,
concurrent guards/journals, immutable failed→ready history, one-winner shared
slot, partial/foreign/consumed refusal, default lightweight parent, exact current
source acceptance and one-path historical original-byte verification, forbidden
scopes, pre-step veto preventing reservation/mutation, and exact parameter/Adam/
reconstruction/score parity. All previous legacy v4/role/input tests still pass.
Initial fixture mistakes and a new-guard pre-hook return incompatibility were
corrected before acceptance; no real attempt was spent during those corrections.
HostedCI is unverified, no dependencies/CI/model/reader/math changed.

Preflight ID `af51c4dd9878c7ab1652bacbe55f8000`, UTC07:18:27.522316–07:18:29.603668
on2026-10-08 (09:18Europe/Rome),2.081361208s including0.495057708s framework setup.
Own peakRSS347717632/native188399616bytes pass512/256MiB; pressure is **unknown**,
errno1, permitted without labeling NORMAL. Context `(4588+216576)×16384 =
3623550976bytes =3.374694824GiB`, query43413.284664791–43413.290474958 monotonic,
query-start age0.006001959s. This low value did not decide admission. No global
stability wait or additional readiness attempt occurred.

| Actual phase | Status | Whole wall incl imports/cleanup | Lifetime peakRSS | Whole native peak |
| --- | --- | ---: | ---: | ---: |
| Dev reader64/two32views |Passed|1.580294750s|387940352bytes|188399616bytes|
| Fresh process-only dev readiness |Passed|1.392263041s|360579072bytes|180011008bytes|
| Dev1024/three passes/score |Completed,180s target failed|1.971522875s|387989504bytes (370.015625MiB)|188399616bytes (179.671875MiB)|

Reader constructor verification0.049126208s, two views with accounting/release
0.023099375s, mapping22947712virtual array bytes (not RSS). The dev stage separately
verified its constructor in0.032475958s. No full-store custody replay. One audited
dev custody operation plus the separately recorded dev constructor; five
train_background/dev_only requests:64reader+3072training+1024scoring=4160presentations,
all within the same1024unique original IDs.96newstarted/completed updates,0inflight,
original96+new96=**192/192consumed**, no remaining granted steps. No weights or
individual real scores persisted; only existing diagnostic mean/hash records.

All measured guards passed local caps with no latched failure. Final receipts
show owned threads closed. Reader/dev-readiness/dev each record47/5/373 fresh
process checks, respectively1/0/10periodic checks included in those totals;
9/1/2optional context queries, distinct from process checks. Context ranges
3.292740–3.357941GiB /3.291077GiB /3.330978–3.335541GiB, all below4GiB. Pressure
remained unknown at recorded guards. No live WARN claim; WARN permission is
established synthetically.50ms is scheduling intent, not a termination guarantee.

Training pass times are exactly
`[0.16781862499919953, 0.13851762500416953, 0.13835891600319883]s`;
scoring`0.07742041700112168s`. View preparation, batch guards/audits stay included.
Unchanged calculation:

`2 × (114.71271611187959 + 5.6514636234539495) =240.72835947066707s >180s`.

The slowest first pass and factor2 are retained. No probe subtraction, favorable
pass selection or target change. Historical749.3431957854029s stays failed;
these are distinct small-sample projections under different policies/shared-host
conditions, not a causal monitor speedup or measured full epoch.

Eligible same-PyTorch2.14.1 comparison is exact: last online objective
0.8151977394784519, same-sample mean0.7520234728718791 and score-byte SHA256
`31475c619699ee85c2e44a2e74e29a32dea3a5e092b441ccfa54a9e117343a13`
match Task0013. Disposable diagnostic code/score hash is not a trained-model
scientific identity, restored score or signal result. Canonical fit/selection/
restoration/independent reproduction/freeze/calibration never started.

Anchor is consumed and immutable, plan SHA256
`ce175b39027a4b149e45b986d229dd58e437b0d616c133d1fec9954ba029c24b`.
Actual acceptance file SHA256
`1a81fe8181b1bd430f0d55ccdb13363e912d8948d1347eee6e2944ec7515e047`;
policy canonical SHA256
`5fa1dbcaeb9ed50070a0bfcdd149a8a5bc40ce23d2b908b18d003574be04f8fb`.
The brief CLI's execution-permission line is the preflight snapshot from before
reservation; it says unreserved at that earlier point. The completed workflow,
canonical anchor and curated summary establish **consumed now/no manual rerun**.
Check-only can still inspect resources and report unavailable execution permission.

## Next consolidated decision

Propose **Task0019 — Canonical Particle Execution Feasibility and Budget Decision**,
not another monitor/readiness optimization. Decide together whether canonical
execution can coexist with shared Mac use, what full-store process/pressure
policy is defensible using its actual3.121GiB historical RSS/197.25MiB native
footprint, and whether to retain or explicitly/versionedly revise training-time
contracts. The bounded dev512/256MiB profile cannot authorize that full store.
No further real optimization allowance or full execution is implied.

At240.728s projected/cycle,200cycles would take13.3738h/run before postfit, versus
original10hfit/run and22htwo-run total; the old180s ceiling corresponds to10h for
200cycles (plus1hpostfit/run). This explains the engineering role of180s and the
current blocker. It is a conservative small-sample planning projection; no actual
full epoch or convergence horizon is measured, and patience might stop earlier.
A future review must preserve convergence-unresolved on resource/epoch ceilings,
reproduction/freeze-before-calibration and test embargo. No implicit new horizon.

If a full run cannot reasonably coexist with normal use or a defensible time/
resource budget, keep the particle branch pending and progress a hardware
measurement foundation for frozen PCA/aggregate AE independently. No dedicated
Mac demand, additional readiness window, automatic training or entire-project
block on finding an idle host.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Historical749.3431957854029s>180s, Task0014 no complete-workload gain, Task0015
2.1403×below3×, Task0016 prospective diagnostic review and Task0017 failed safe
checks remain factual. Synthetic validation is not a new real throughput result,
convergence or canonical artifact. The next dependency will consolidate actual
canonical feasibility, full-store process envelope and training-time budget;
no further monitor-optimization/readiness task series or automatic canonical run.
