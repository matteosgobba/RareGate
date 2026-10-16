# Particle host readiness — Task 0013

## Preregistration before accounting or study execution

Base `53b238a83a4cc8f29b09b6e40d69d777588fc1c5`, clean main/origin/main,
2026-10-07 Europe/Rome. Task0012 commit verified locally; push/hosted CI unknown.
One accounting experiment and one conditional bounded successor are authorized
by [the exact prompt](prompts/0013-particle-host-readiness.md). No canonical
training, selection, restoration, reproduction, freeze or calibration.

Scientific design/config/preprocessing/reader/model/dev/optimizer/score code and
the v2 sidecar remain byte-identical. Model478/local2+mean8, seed1729, CPU1/1,
batch32, FP32 network/FP64 pooling/residuals, equal event weighting are preserved.
Admission4831838208bytes, continuing4294967296bytes, native536870912bytes,
lifetime peakRSS6442450944bytes and original time/event/update limits unchanged.
V1's8GiB launch is historical, never claimed passed. The v2 sidecar keeps its
Task0012 scope; a separate Task0013 execution manifest supplies successor
authorization without changing that profile or granting canonical scope.

Accounting is fixed in order: stdlib controller/probe; legacy actual Task0012
parent+fresh prepared child stacks; lightweight parent+fresh prepared worker.
Overall180s, each30s including startup/imports; three timestamped paired own-task
snapshots spaced2.5s, spanning≥5s. Parent and child report themselves while alive
together; neither constructs a store/model/optimizer, opens arrays/raw files,
scores or updates. The legacy parent also receives the same CPU preparation,
explicitly recorded; no artificial allocation or memory-pressure generation.
The stdlib experiment orchestrator stays alive in all three configurations.
Pressure/current swap/installed-RAM queries occur once for diagnostic context,
with permission failures retained; no optional process inventory is requested.
Actual page size/raw free+inactive determine availability. Wired/active/file/
compressor and cumulative swaps remain context, never added or treated as current
swap usage. Missing primary accounting fails admission; optional pressure unknown
is disclosed and warning/critical vetoes. Diagnostic pressure is the one context
query; official readiness/live workers independently re-query via original v2.

The lightweight controller imports only stdlib and new pure-stdlib supervision
helpers. Scientific validators and unchanged Task0012 reader/audit/dev/monitor
functions stay in fresh workers. Darwin parse/malloc/Mach bindings are isolated
copies with synthetic arithmetic parity; no shared scientific helper is changed.
Fresh-process import/source-map coverage checks prevent hidden framework imports.
All executable changes are under `src/raregate`, covered by source acceptance.

Fixed ignored execution manifest `data/baselines/task0013-particle-host-plan.json`
is preparation, not reservation. It binds actual prompt, both old acceptances,
historical failure/zero-consumption hashes, unchanged profile/design/config and
fresh complete source acceptance. One exclusive invocation file and fixed study
directory serve automatic and external execution together. No force/reset/root/
output override, phase replay, additive budget or alternate task route. Each phase
reserves before dispatch; workers check token/parent/manifest/slot/source/profile
before runtime and repeat real validators before data. Bounded logs1MiB, compact
journals16MiB, parent deadlines/owned-process cleanup and partial bootstrap/access
audits preserve interruption evidence. Original50ms watcher,2s probe timeout,
signals and per-batch checks remain unchanged. Log ceilings are engineering
evidence bounds, not relaxed resource/scientific limits.

Only if every prepared configuration3 observation passes may the controller invoke
the study automatically. That invocation consumes the shared slot and starts its
own fresh three-reading readiness≤30s. If diagnostic admission fails/unknown, the
slot remains unreserved for user-controlled Terminal execution. Official order:
readiness → dev reader≤60s, first64 of same first1024 dev train, two32views/one
retained → separate full custody≤300s, constructor verify/map/close/no population
request → unchanged activation → fresh dev readiness → original dev≤300s,
1024unique/three passes/96started updates/one same-sample score pass. Each actual
reader/dev worker independently launch-checks before constructing data.

Activation is exactly maximum(reader native peak minus its own startup reserve,0)
+4×synthetic tensor peak+128MiB≤512MiB, with complete zero-update/resource/identity
receipts. The controller's stdlib mirror is parity-tested against unchanged v2.
This empirical bounded-dev envelope does not establish canonical/mapped-page
safety. Dev uses the original factor-two extrapolation:
`2*(699957*max_train_pass_seconds/1024+74749*score_pass_seconds/1024)≤180s`.
Loading/view preparation remains inside pass/stage times. Started/completed/inflight
steps are persisted by original audit hooks; disposable weights/per-event outputs
are never saved. Failures stop dependencies; no canonical stage is supported.

Apple's [Activity Monitor guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac)
describes pressure using free memory, swap rate, wired and cached files; it does
not replace the frozen metric. The [archived VM guide](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/ManagingMemory/Articles/AboutMemory.html)
explains virtual/resident/shared mappings; historical sizes are not adopted.
[XNU task-info](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/task_info.h)
supports own-task currentRSS; [pressure conversion](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_memorystatus_notify.c)
defines dispatch flags1/2/4. Summed processRSS overlaps shared pages and is not
unique physical memory. Sequential host variation/cache/external activity limits
causal attribution; process savings cannot explain the historical~2GiB change
without evidence or demonstrate reader feasibility.

## Measured accounting and blocked admission

The sole data-free experiment completed in20.817059334s. Each configuration
completed within30s including imports and child cleanup. Parent/child lifetimes
were simultaneous only within their own configuration. No official study was
invoked or reserved: configuration3 has three failures of4.5GiB launch and4GiB
continuing availability. This is a host-admission result, not model infeasibility
or convergence failure. V2 remains reviewed/provisional/not activated.

UTC timestamps below are2026-10-07; Europe/Rome is UTC+02:00. Every raw header
reports16384bytes/page. These are diagnostic child host observations, not official
stable readiness receipts. Exact parent raw snapshots are also retained locally.

| Configuration | UTC time | Free /inactive pages | Available bytes | GiB |
| --- | --- | --- | ---: | ---: |
| stdlib_baseline | 08:44:51.413749 | 3873 /228555 | 3808100352 | 3.546569824 |
| stdlib_baseline | 08:44:53.920878 | 3795 /221362 | 3688972288 | 3.435623169 |
| stdlib_baseline | 08:44:56.427683 | 3888 /238333 | 3968548864 | 3.695999146 |
| legacy_double_stack | 08:44:59.844646 | 3963 /203548 | 3399860224 | 3.166366577 |
| legacy_double_stack | 08:45:02.344096 | 4850 /201865 | 3386818560 | 3.154220581 |
| legacy_double_stack | 08:45:04.852663 | 3821 /203121 | 3390537728 | 3.157684326 |
| lightweight_prepared | 08:45:06.761900 | 12851 /198203 | 3457908736 | 3.220428467 |
| lightweight_prepared | 08:45:09.277683 | 6570 /201690 | 3412131840 | 3.177795410 |
| lightweight_prepared | 08:45:11.784938 | 5697 /206917 | 3483467776 | 3.244232178 |

Own-process measurements below use maxima across the three samples. CurrentRSS,
OS lifetime high-waterRSS and malloc reservation/in-use are distinct, overlapping
measurements; no totals or reclaimed-host-memory claim is made. CurrentRSS and
high-water are queried at slightly different instants, so one later currentRSS
sample can exceed the earlier high-water query by a small amount.

| Configuration /process | PID /parentPID | Max currentRSS bytes | Lifetime peakRSS bytes | Max native reserved /in-use bytes | Runtime import+CPU setup seconds |
| --- | --- | ---: | ---: | --- | ---: |
| stdlib_baseline /parent | 41397 /41393 | 22364160 | 22380544 | 33554432 /2918832 | 0.000000000 |
| stdlib_baseline /child | 41398 /41397 | 22265856 | 22282240 | 37748736 /2914464 | 0.000000000 |
| legacy_double_stack /parent | 41433 /41393 | 312721408 | 357105664 | 175816704 /138969056 | 1.937808833 |
| legacy_double_stack /child | 41446 /41433 | 357072896 | 357072896 | 180011008 /138967072 | 1.282323625 |
| lightweight_prepared /parent | 41499 /41393 | 22200320 | 22200320 | 29360128 /2918992 | 0.000000000 |
| lightweight_prepared /child | 41500 /41499 | 357171200 | 357154816 | 175816704 /139131152 | 1.247551666 |

| Configuration | Child sample span seconds | Parent sample span seconds | Whole dispatched configuration seconds |
| --- | ---: | ---: | ---: |
| stdlib_baseline | 5.010154084 | 5.010811291 | 5.175210041 |
| legacy_double_stack | 5.007371000 | 5.006922125 | 8.923264166 |
| lightweight_prepared | 5.010064917 | 5.023326542 | 6.691521000 |

The baseline and light parents load no heavy modules. The legacy parent and both
prepared children load `numpy`, `torch`, `raregate.data.processed`,
`raregate.models.particle_memory_study`, `raregate.training.particle_set`.
Pandas/h5py are not loaded by this actual runtime stack. ChildCPU setup is1intra/
1inter/deterministic, matching real reader workers. The legacy parent is also
prepared; this explicitly recorded setup is additional to its import shape.
The stdlib controller/probe children instantiate no scientific objects.

The legacy versus light parent lifetime-peak difference is334905344bytes
(319.391MiB); native-reservation difference146456576bytes(139.672MiB).
This establishes a smaller observed supervisor process footprint. It does not
establish unique physical-memory savings: shared pages overlap, and host/cache/
external activity changed across configurations. Light host availability stayed
3.177795–3.244232GiB, below both thresholds; the historical~2GiB Task0011→0012
change remains causally unexplained. No unrelated process content was inspected
or workload closed. No machine-wide changes, artificial pressure, polling for
favorable values, additional experiment or official in-app preflight occurred.

Installed16GiB is reported by `memory_pressure -Q`; direct `hw.memsize` and current
swap queries are permission-restricted. Contextual free46% is not admission or
verified normal pressure. The one pressure-dispatch query returns errno1/unknown.
Own-task Mach currentRSS/virtual size succeeds; dirty/private is not measured.
Active/wired/file/compressor and cumulative swap counters are retained in raw
local receipts and the small curated numeric summary, not added together. No
optional process inventory was requested; no escalation for missing telemetry.

## Study state, remaining allowance and external Terminal procedure

The fixed successor manifest exists; invocation file/study output remain absent.
No readiness/reader/custody/dev study phase has been dispatched/reserved. Zero
real custody operations, population requests, model views/unique events,
optimizer steps started/completed/inflight. Original1024unique/three passes/
96started updates/one same-sample score pass all remain available. Activation,
reader footprints/loading times/dev extrapolation are unmeasured. Full training,
selection/restoration/reproduction/freeze/calibration/artifact/threshold/score
populations are not authorized or reached. PCA/AEv1/v2 remain unchanged.

The **single external study remains pending/unreserved**. The user may close
chosen unnecessary workloads, including Codex if desired, then execute once from
an external Terminal using the existing environment (no install/sudo needed):

```bash
cd /Users/matteosgobba/Documents/GitHub/RareGate
/Users/matteosgobba/Documents/GitHub/RareGate/.venv/bin/python -m raregate.supervision.particle_launcher --run-once
```

This command verifies current source acceptance/configs/profile/prompt/lineage,
exclusively consumes the same single slot, then performs fresh readiness before
any data. A failing readiness consumes that invocation and blocks all later
stages; do not rerun, delete/change paths, reset a ledger or rerun accounting.
The command works independently of Codex. This task did not open Terminal,
close Codex or execute the external route. Ignore any old Task0011/0012 run
commands as historical routes; neither provides another budget.

Receipts remain under fixed ignored `data/baselines/task0013-particle-host-study/`
and `task0013-particle-host-invocation.json`. The current curated summary records
**pending execution**. A later task must reconcile the eventual manual workflow,
reservations/audits/started/inflight counts before assigning any budget; do not
replay a consumed dev gate. If manual reader/dev feasibility passes, propose
Task0014 for typed actual-policy artifact/completion compatibility and canonical
background training under an explicit versioned full-run authorization. Until
then, next dependency is user-controlled host preparation and this delivered
Terminal path, not another identical in-app preflight implementation task.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## Actual validation and identities

Full final synthetic suite422passed in6.58s, including57new Task0013 cases.
The first targeted run had46passed/one fixture failure (missing fake study parent
directory); corrected the fixture, then57passed. No real stage used that failure.
The actual existing acceptance producer bound pytest XML/log exit/counts and all
source/tests; synthetic batch32/full384 allocation peak remains5228448bytes with
2syntheticAdam updates/478parameters. Real updates are zero. No acceptance flag
was manually set. No executable source edit followed acceptance/measurement.

Ruff lint/format passed(56Python files in src/tests/scripts); pipcheck/imports and
explicit CPU16.0smoke passed. A preliminary smoke command incorrectly passed an
argument to `get_device()`; corrected the command to explicitCPU, no source change.
No dependencies/CI changes or reinstall. Current reader/model/dev/Adam/monitor
files are byte-identical to Task0012; existing numerical/guard/observer-equivalence
coverage still passes. New cases cover fresh import/source inclusion, pure probe
parity/malformed/unknown context, immutable profile/type/hashes, activation parity,
phase/full-fit/calibration/test refusal, prior/later/foreign/duplicate/source
rejection, preparation versus reservation, independent worker launch recheck,
bootstrap exceptions, parent timeout/log bounds and conditional single routing.
Future real reader/live watch/custody/dev behavior remains unverified.

| Identity | SHA256 |
| --- | --- |
| Engineering profile (canonical) | `a3e237d8a191d9b906744a497ef7e687c739bc8418dd2e53e78db3e54b24d287` |
| Mathematical design (canonical) | `3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67` |
| Executable config (canonical) | `48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b` |
| Actual Task0013 prompt | `652ce7907f6aa1833ed543a8d89c7f4e31fb1d009c80e1c29997ee1cfb571750` |
| Final acceptance file | `339c6ed984823e205564c753e7409e54482e36dc8cfa78f537b0508cd731c755` |
| Source-map canonical | `2c34f8878eed9d1fb784b651bdb20065396e324679dadd8866f3a6984fded09d` |
| Prepared execution manifest | `4f23221843818b198557d928fb2783a63d472c502eda0daa1b704bc32c3e29bd` |
| Experiment preregistration | `2d4fe17ba6b35f4fa40d053cf529d5a2354358fab51c65909239602aa67a486f` |
| Actual experiment receipt | `c8cabd0054ba48f99f94c1d6999f79b5f9286cc0c1a465b6eb911777f8d3dee7` |

Final checks preserve134old tracked files plus24pinned records and four old
acceptanceXML/log hashes;123local links resolve, JSON/arithmetic/current acceptance
and the exact12-file scope/empty index/whitespace checks pass. Details are in the
[handoff](handoffs/0013-particle-host-readiness.md). See the
[curated summary](../results/tables/final/task0013-particle-host-readiness-summary.json).
HostedCI and remote push remain unverified; no staging/commit/push performed.
