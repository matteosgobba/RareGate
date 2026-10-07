# Task 0012 — Versioned Launch-Memory Policy Review and Bounded Feasibility Validation

## Initial metadata and authorized scope

- Date2026-10-07, Europe/Rome; operational checkout
  `/Users/matteosgobba/Documents/GitHub/latent-trigger`, not a synced mirror.
- Branch/upstream `main`/`origin/main`; base/HEAD
  `502c472686bd08c24ec16873a3d027b8094acccc`.
- Initial tracked tree/index clean; Task0010 `694bffd`, initialTask0011 `50e42b3`,
  resumedTask0011 `502c472` committed locally. Remote push/hostedCI unverified.
- Actual revised attached prompt copied before substantive changes to
  `docs/prompts/0012-particle-memory-policy-review.md`.
- Applicable development/living memory read; no AGENTS.md found. Prior tracked
  and ignored hashes and overlapping document copies preserved under ignored
  `data/task0012-initial-state.json`/`data/task0012-initial-documents/`.
- Explicit scope: engineering launch admission only. Immutable model, inputs,
  score, training and original4GiB continuing floor/512MiB native/6GiB RSS/timing
  limits. No full training, selection, calibration or canonical artifact.

## Preregistered provisional envelope (before any real reader)

Task0012 prompt authorizes one separate bounded engineering measurement under
free+inactive launch≥4.5GiB, continuing≥4GiB, native reserved≤512MiB, lifetime
peakRSS≤6GiB. Derivation: original4GiB continuing reserve plus512MiB admission
headroom, equal to conservative whole-native ceiling; no favorable-sample tuning.
Mapped/file/shared effects still need live availability/RSS checks and cannot
be inferred from tiny synthetic tensor allocations. Reject if source bounds
cannot be enforced. Stable three-sample≥5s/≤30s readiness plus worker recheck.

At most one dev-reader phase≤60s (first64 source-ordered frozen dev-train IDs,
two batch32 views, one batch retained, no network/score/gradient/optimizer), then
one separate full-store custody phase≤300s (constructor verification/mapping/
close only; no full population model request). Exclusive reservation and live
monitor/parent deadlines required; failed phase stops dependent execution.
Verified pressure warning/critical is a veto where available; unknown telemetry
is disclosed. Original8GiB policy never claimed passed.

Only completed justified reader evidence can activate a frozen sidecar for one
original dev feasibility gate≤1024 unique events/96steps/3passes/one score pass/
300s/factor2 extrapolation≤180s. No additive optimization budget. No other stages
authorized. Task0011 unused route must remain unexecuted/superseded, all prior
ledgers/audits/acceptance/preflights preserved.

## Outcome

**Provisional launch still blocked: no new real reads.** The one explicitly
authorized study dispatched only its read-only pilot preflight. All3samples
failed4.5GiB launch and original4GiB continuing floor. No reader/custody/dev
phase was reserved/executed, no activation and no real optimizer step. Policyv2
remains reviewed/provisional/not activated, canonical particle baseline pending.
No claim of original8GiB compliance, reader/model infeasibility or convergence
failure. Stop dependent work; no repeat to fish for a pass.

## Inspected/preserved evidence and source audit

Read Task0009–0011 design/executable configurations, reports/prompts/handoffs/
curated results, dated resumption/preflight, original ledgers/audits and current
source acceptance. Original config mapping, model478/ordered initialization,
guarded processed reader/model view, resource monitor, orchestration, scoring/
calibration/artifact semantics and frozen preprocessing/evaluation reviewed.
Applicable living-memory/development instructions govern this engineering scope.

Verified Task0010 consumed attempt was zero-real-event/update; Task0011 route
has no plan/ledger/output or consumption. Predecessor pinned file hashes verify
before study. Both Task0011 preflights and all prior acceptance/failed-stage
bytes preserved, as are historical reports/handoffs/results and the old manual
staging helper. No source mirror edit. Full-store custody was not repeated as
inspection; only small manifests were read to derive allocation inventory.

Whole reader constructor still hashes all files, checks complete schema/source/
split/duplicate identities, scans bounded992-row structural validity chunks and
maps read-only arrays. Full manifest files2906842523bytes,195918046particles/
1100000events; dev23046077bytes/1549328particles/8494events. `hashlib.file_digest`
in installed runtime reuses262144-byte buffer. Fingerprint uniqueness and global
metadata allocate bounded dense scratch; structural chunks≤992×700particles.
`_batch` copies≤32×700 physical particles; model views≤32×384×4 with bounded
FP64 transformations. Source inventory estimates differ from measured VM/native
footprint; see report. No full padded population. Parent runtime footprint is
included in host availability but not separately measured as reader/worker RSS.

Primary references read: Apple's
[Activity Monitor memory guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac),
[archived VM guide](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/ManagingMemory/Articles/AboutMemory.html),
[XNU pressure documentation](https://github.com/apple-oss-distributions/xnu/blob/main/doc/vm/memorystatus_notify.md),
[task-info ABI](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/task_info.h) and
[pressure dispatch/sysctl conversion](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_memorystatus_notify.c).
Archive's historical page sizes/limits not reused. Kernel broader availability
is not substituted for project free+inactive. Pressure sysctl returns dispatch
flags1normal/2warning/4critical, not internal enum; verified warning/critical veto.

## Exact version/implementation decisions

Sidecar schema1/engineering-policy2, model/config version unchanged. Profile
canonical SHA256 `a3e237d8a191d9b906744a497ef7e687c739bc8418dd2e53e78db3e54b24d287`;
file-byte SHA256 `3d495f62256bc3e92b988178fcf9a63185ae655382cead477ccf39a3e524c370`.
Model design canonical SHA256
`3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67`;
executable canonical SHA256
`48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b`.
Their historical bytes remain unchanged. No trained-model hash.

Strict sidecar validation compares exact known type/version/scope/hash and sole
launch8→4.5GiB diff; all continuing/native/RSS/time/step fields unchanged. No
arbitrary profile/config override, bool/type confusion or old-config mutation.
New `training/particle_resources.py` retains original50ms watcher/signals/deadlines
through a separate named monitor, serializes probes, compacts journal/raw handling,
records overhead/phases and optional own-task Mach RSS/virtual/pressure. Unknown
primary accounting fails closed; unknown pressure/current-swap/dirty-private is
disclosed. No artificial pressure, application cleanup or uninspected app content.

New `models/particle_memory_study.py` is a fixed exclusive one-study route. Plan
binds actual revised prompt, exact design/config/profile/source acceptance and
predecessor/zero-consumption lineage. Each readiness/reader/dev phase reserves
before dispatch; worker token/parent/plan/source/config/profile/phase/status/step
allowance and exclusive directory checked. Fit/selection/calibration/freeze are
not supported. Wrong/stale/foreign/duplicate invocation fails before reads; no
force/root/task/output retry option. Task0011 now refuses its superseded unused
route when the Task0012 plan exists; its own original ledger remains absent.

Whitelisted changes to old code: original dev accepts optional optimizer observer;
audits may observe sample binding/per-view IDs solely for accounting; no Adam/
loss/loader/math alteration. Observer pre/post hooks preserve identical synthetic
updates and reserve/journal≤96started/completed/inflight steps. Sample-relative
seen-bitset/unique and presentation counts are ignored engineering metadata,
never model inputs or scores. Dev weights would be disposable and never reused.
No source change to particle model, processed reader, original monitor, stopping,
calibration or artifact parsers. Future typed active-policy artifact/completion
compatibility is specified in report, not implemented/called here. Genericv1
`resource_gate_passed` cannot prove v2 compliance; current profile admits no
canonical training. Timestamp/path/probe timings remain engineering provenance.

Activation criterion was frozen before reads: both zero-update reader phases
complete under all limits and exact identities; bound=max(reader native peak minus
its startup,0)+4×synthetic tensor peak, plus128MiB declared margin≤512MiB headroom.
Larger demands reject activation, without thresholds selected after dev losses/
timings. This empirical bounded-dev envelope does not validate full fitting or
all mapped-page effects. No criterion evaluation was possible because readers
were not reached.

## Actual bounded execution / evidence

Actual command, after source acceptance:

```bash
.venv/bin/python -m latenttrigger.models.particle_memory_study --run-study \
  --acceptance data/task0012-synthetic-acceptance.json
```

Exit1. Only `pilot_preflight` reservation and worker executed. Samples2026-10-07,
Europe/Rome UTC+02:00; actual page16384bytes, exact `(free+inactive)*page`:

| Time | Free / inactive pages | Available bytes /GiB | Peak RSS bytes | Current Mach RSS bytes | Native reserved /in-use bytes |
| --- | --- | --- | ---: | ---: | --- |
| 09:04:30.926013 | 3850 /165471 | 2774155264 /2.5836334228515625 | 344866816 | 344899584 | 175816704 /139065840 |
| 09:04:33.431085 | 4089 /162656 | 2731950080 /2.5443267822265625 | 344899584 | 334348288 | 180011008 /139078256 |
| 09:04:35.934302 | 4027 /172706 | 2895593472 /2.6967315673828125 | 344899584 | 332103680 | 180011008 /139089904 |

Span5.008331250000083s, context/sampling5.047508625000319s, whole worker including
startup6.4967512079997505s. All launch/floor checks fail; all native/RSS checks
pass. Raw snapshots preserve every reading. Current Mach RSS is independently
supported; virtual reservation446326652928bytes is not physical allocation.
Dirty/private unmeasured, current swap/ps queries permission-restricted, pressure
dispatch query errno1. `memory_pressure -Q`16GiB/free36% is context, not verified
normal pressure or project available bytes. No compressed/active pages added,
no cumulative swaps interpreted as current use/rates.

Measured readiness probes7.115709/14.897834/17.668959ms; total39.682502ms. Original
monitor retained last raw only; new readiness preserves3raw, live journal compact.
No live watcher started/journal written because readiness failed; steady overhead,
reader verification/loading costs and dev timings remain unmeasured.50ms detection
also includes probe/GIL scheduling (external command≤2s); deadlines unchanged.
Do not call readiness probe time detector latency or infer model CPU feasibility.

Ignored identities:

| Evidence | File-byte SHA256 |
| --- | --- |
| Execution acceptance `data/task0012-synthetic-acceptance.json` | `ce7f3d7944a1e512a0f548a7965cd4afc79a2af401cba029096a6138238cea1a` |
| Plan `data/baselines/task0012-particle-memory-plan.json` | `8d9dc461db3e86259b161f69b7309c32573049f904b21a83edac51962715058c` |
| Pilot reservation | `6fc2b7d43387c6b5465ff466a3517647536802aca5c57b468be546c5292cc2f5` |
| Pilot stage result | `58d5e64120c50c5527f1674786a7a7400e0b7679c36eb6e64453a1f4dde68c86` |
| Pilot access audit | `0a0806a332dca43eedf9ed9561eaba68ed8087c5dd95bc048eb9bd11dcfe617a` |

Pilot reservation remains consumed/read-only; no dev-reader/full-custody/dev
reservation, activation or model artifact. Prior failure evidence never deleted,
renamed, reset or overwritten. No actual population/custody request even began.

```text
read-only readiness checks dispatched: 1
reader/custody/dev phases reserved or executed: 0
real custody operations/population requests/view presentations: 0 / 0 / 0
unique real dev events/optimizer steps started/completed: 0 / 0 / 0
remaining original dev unique events/passes/steps/score passes: 1024 / 3 / 96 / 1
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

No dev timing/extrapolation/optimization loss, full training/selection,
restoration/reproduction/freeze/calibration or background distributions. Custody
would be disclosed separately but was not executed. PCA/AEv1/v2 unchanged; no
signal/test metrics, MPS particle training, export/quantization/detector benchmark,
NVIDIA/TensorRT/hls4ml or trigger simulation.

## Validation and final review

- Initial targeted suite190passed/1failed: synthetic activation fixture expected
  rejection despite calculated bound still within512MiB. Corrected fixture startup
  reserve to test actual larger demand; then195passed. No real stage used failure.
- Actual full suite362passed before sole study; source-bound acceptance generated
  from actual pytest XML/exit code and unchanged synthetic allocation profiler.
  Execution source-map canonical SHA256
  `fb6cea30c52a20e951a86cbbf06f3a6903fd69966b2977e040b70e6bb2cbfe33`.
- Final review made reservation phase/status/maximum-step validation strict;
  3additional synthetic cases. Fresh final full suite **365passed**, source-map
  SHA256 `89152fa7b119fbbee99c3cf831605d214c8ede81b425ffbd7dc4d58d20ec6453`;
  final acceptance file `data/task0012-final-synthetic-acceptance.json`, SHA256
  `fe33d6822071b3eab8280fa73e107d05365ef4577349f9b6420f585598430844`.
  Actual failed readiness remains tied to original execution acceptance; no
  resampling, hidden dispatch or stale acceptance reuse after review.
- Synthetic allocation measurement in both actual acceptance runs5228448bytes,
  batch32/full384/two synthetic Adam steps; real optimizer consumption0.
- Ruff lint/format (final94files), dependency check/no broken requirements,
  existing editable imports and CPU smoke passed. No dependencies/CI change.
- Cases cover exact type/version/hash/diff/config immutability, byte arithmetic/
  equality/unknown/veto, overhead/compact journal/blocked signal deadlines, phase
  order and full-fit/calibration refusal, exact64/no-population custody paths,
  partial audits, foreign membership,96-step/inflight limits/numeric equivalence,
  duplicate/timeout/stale/predecessor/worker launch recheck and strict lineage.
- Final JSON/report/source identities, historical hashes, local links/exclusions,
  intended scope and `git diff --check` verified. HostedCI/remote push unverified.

## Memory / files / next dependency / manual Git

Living memory revision1.5 updates engineering decision/history/current state and
roadmap in place: v1 historical, v2 reviewed/provisional/not activated; reader
and canonical validations pending. Actual host floor failure now blocks even the
permitted4.5GiB pilot; no model requirement or cause of changing host availability
is inferred. Typed future artifact/active-policy receipt is an implementation
prerequisite before any canonical run, not a completed feature or trained hash.

The smallest next decision is bounded host-readiness/accounting preparation
preserving original4GiB while under load, then an explicitly authorized new
readiness/reader lineage only when admission4.5GiB is stable. Existing study is
exclusive and cannot be replayed/reset. A lighter parent/runtime bootstrap may
be separately reviewed without assuming its unmeasured footprint resolves the
shortage. No continuing-floor relaxation, task numbering or canonicalTask0013
proposal/execution here; positive reader/dev feasibility evidence is absent.

Intended Task0012 paths (13):

```text
README.md
docs/handoffs/README.md
docs/project-memory.md
docs/prompts/0012-particle-memory-policy-review.md
docs/handoffs/0012-particle-memory-policy-review.md
docs/particle-memory-policy-review.md
configs/resources/particle_memory_policy_v2.json
results/tables/final/task0012-particle-memory-policy-summary.json
src/latenttrigger/training/particle_resources.py
src/latenttrigger/models/particle_memory_study.py
src/latenttrigger/models/particle_background.py
src/latenttrigger/models/particle_recovery.py
tests/test_particle_memory_policy.py
```

Initial prerequisites fully committed/tree clean; no prerequisite helper needed
or executed. Ignored: initial hashes/doc copies, actual acceptance XML/log/profiler
outputs, exclusive plan/workflow/reservation/audit/raw preflight/console, final
validation notes and normal test caches. No datasets, arrays, checkpoints/models
or success-shaped calibrated output staged. User reviews selective13files,
cached diff/whitespace, then commits `feat: add provisional particle memory policy`
and pushes `origin main`; no staging/commit/push by the agent.
