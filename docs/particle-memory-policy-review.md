# Versioned particle launch-memory policy — Task 0012

## Preregistered engineering decision (before real reader measurements)

This task reviews **launch admission only**. Policy v1 remains historical and
reproducible: Darwin `(free_pages + inactive_pages) * actual_page_size`, launch
8GiB, continuing4GiB, native malloc reservation512MiB, lifetime peakRSS6GiB.
Task0010 failed before any reader at3.694794GiB. Task0011 reserved no recovery;
the explicitly resumed after-reboot readings4.648499/4.624817/4.681854GiB pass
continuing4GiB but fail launch8GiB. Those are environment/admission observations,
not measurements of real particle training memory or convergence.

The revised user prompt explicitly authorizes one **provisional engineering
measurement** with launch4.5GiB and every other ceiling unchanged. The derivation
is4GiB continuing reserve +512MiB admission headroom, equal to the existing
whole-native ceiling; it is not chosen just below an observed favorable sample.
The [sidecar](../configs/resources/particle_memory_policy_v2.json) binds unchanged
design/executable identities and defines engineering version2. It never mutates
the historical model JSON in memory/on disk or claims policy-v1 compliance.

| Contract | Policy v1 | Provisional v2 | Interpretation |
| --- | ---: | ---: | --- |
| Same named free+inactive launch metric | 8589934592bytes/8GiB | 4831838208bytes/4.5GiB | Sole admission threshold change |
| Continuing free+inactive | 4294967296bytes/4GiB | Identical | Fails under load → stop, no floor lowering |
| All native malloc arena reservation | 536870912bytes/512MiB | Identical | Conservative whole-native sampled bound |
| Process lifetime peak RSS | 6442450944bytes/6GiB | Identical | OS high-water, never mislabeled current RSS |
| Dev event/batch/update limits | 1024/32/96 | Identical | Same unused optimization allowance |
| Dev/full-cycle/fit/postfit/two-run seconds | 300/180/36000/3600/79200 | Identical | No canonical fit/postfit authorized here |

Three fresh-CPU readings must all pass launch/continuing/RSS/native/verified
pressure vetoes, span≥5s and complete≤30s, followed by independent worker launch
recheck. Unknown primary accounting fails closed. Optional pressure/current swap/
dirty/private metrics are disclosed unavailable; missing pressure is never
converted into a normal state. A verified warning/critical pressure signal vetoes
admission and live execution. No application cleanup or artificial pressure.

The profile is **provisional** until both one-time reader measurements complete:
dev≤60s, first64 source-ordered frozen dev-train IDs (within original first1024),
two batch32 views with at most one retained; separate full custody constructor/
verify/map/close≤300s with no model-population request. Both have zero neural
reconstruction/score/gradient/optimizer steps. Constructor hashing/structural
checks remain complete, including permitted integrity truth/membership work.
No preprocessing/store rebuild. Failure stops dependent stages without retries.

## Source-level allocation audit and meanings

Frozen store manifests (small-file inspection, not new custody execution) give
dev8494events/1549328particles, files23046077bytes; full1100000events/
195918046particles, files2906842523bytes. Model inputs remain384×4FP32/bool mask;
canonical ragged storage retains every physical particle. Model-view truncation
and labels/metadata are not neural inputs.

| Source path / operation | Source-derived planning inventory | Limits and exclusions |
| --- | --- | --- |
| `processed.verify_store` / `hashlib.file_digest` | Existing runtime reuses262144-byte hashing buffer; no whole-file materialization | Kernel file cache/mapped residency is not this buffer's private allocation |
| `verify_store` mappings | Read-only mmap of schema arrays, then bounded structural chunks992events, ≤694400particles/chunk | Virtual mapped bytes differ from RSS/anonymous allocation; full reader excludes labels after constructor verification |
| Full fingerprint uniqueness | 1.1M×32bytes=35.2MB per dense fingerprint buffer; flatten/sort/result/mask/scratch planning≤128MiB | Conservative inventory, not allocator/RSS measurement; no removal of duplicate checks |
| Chunk validity/order/slots/features | ≤3×694400 boolean finite values, ≤700slots/event, FP64 aggregate checks; planning≤32MiB overlapping scratch | Canonical max700 from frozen contract; no full padded population |
| Global ID/offset/split structural checks | int64 arrays/diffs of~1.1M entries plus boolean masks; planning≤64MiB | Not neural populations or test evaluation |
| Bounded `_batch` | ≤32×700 particles; copied FP32 physical values, uint16slots, offsets/IDs/aggregates; integer index scratch | Owned batches; one at a time |
| `features.model_view` | FP32features196608bytes +boolmask12288bytes atbatch32; ≤384retained/700original/event; bounded FP64 transforms/index/diagnostics | No model loss/score during reader phase; original frozen scalers |
| Later original dev network | 478FP32 parameters1912bytes, FP32gradients/Adam state, measured synthetic tensor peak5228448bytes | Synthetic-only evidence, not real reader/process footprint |

The inventory leaves substantial space within512MiB for a process whose prior
startup native reservation was~180–184MB, but allocator retention/fragmentation
and mapped effects require actual live measurements. These planning numbers are
estimates rather than hard bounds on all VM behavior. The pilot is accepted only
with enforced512MiB native and6GiB RSS/4GiB available checks, signal deadlines and
parent ceilings. Unsupported accounting or exceeded limits stop immediately at
the operational detection boundary. Sampled native maxima can miss short-lived
transients; OS lifetime RSS remains a high-water mark. No safety/latency guarantee
for canonical training follows from these estimates.

Installed physical RAM, virtual address reservations, current/lifetime RSS,
native reserved/in-use and Torch tensor allocations overlap and are never added
together. Read-only mapped pages can be paged/reloaded; an RSS difference is not
proof of private allocation or immediately reclaimable bytes. Apple's
[archived virtual-memory guide](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/ManagingMemory/Articles/AboutMemory.html)
supports these distinctions; its historical page sizes/limits are not adopted.
Actual page size comes from each `vm_stat` reading. Apple's
[Activity Monitor guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac)
describes pressure using free memory, swap rate, wired memory and cached files.
The [XNU pressure documentation](https://github.com/apple-oss-distributions/xnu/blob/main/doc/vm/memorystatus_notify.md)
describes a broader kernel metric, not permission to add all active/compressed
pages to the fixed project metric. Current-swap use differs from cumulative
swapin/swapout counters.

## Monitoring implementation and overhead contract

Original50ms watcher invokes `vm_stat` for every live check; phase/per-batch checks
also invoke it. It retains only the last full raw snapshot, not an unbounded raw
history. New monitor version `policy2-original50ms-compactjournal-v1` keeps this
same50ms wait, existing2s external-probe timeout and original signal/per-batch/
parent deadline mechanisms. Serialized probes record duration, total/max overhead,
sample counts, phase resource extrema and compact journal byte volume. All
overhead stays within whole-stage and original loading+view+training pass times.

Detection is50ms wait plus actual probe duration/GIL scheduling, not a promised
50ms bound. Wall-time alarms interrupt blocked CPU work, and parent deadlines
terminate only owned workers if reporting fails. No deadlines are loosened.
`vm_stat_raw` is retained for three readiness samples; live journals omit it and
keep one compact append per check. Journal volume is measured separately.

Optional own-task current RSS/virtual address size uses the48-byte
`MACH_TASK_BASIC_INFO` ABI in Apple's
[XNU task header](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/task_info.h).
Unsupported/permission errors are explicit. Dirty/private memory has no supported
binding here and is not inferred. Read-only
`kern.memorystatus_vm_pressure_level` returns **dispatch flags**, not internal
enum values:1normal/2warning/4critical, verified from the
[XNU conversion/sysctl implementation](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_memorystatus_notify.c).
Warning/critical flags veto. Readiness also records bounded contextual pressure/
swap/ps commands; `memory_pressure -Q` percentage alone never proves normal.

## Activation, exclusive lineage and original dev budget

The sidecar's activation rule is fixed **before any real read**: both reader
phases must complete with zero updates, exact policy/config identities and all
live limits. Incremental native planning bound is maximum(reader native peak
minus that worker's startup reservation,0) plus4×actual synthetic tensor peak;
add a declared128MiB margin. Require total≤512MiB launch headroom. This empirical
bound is for the bounded dev study; it does not validate full fitting. Larger
demands reject activation rather than lowering the floor or selecting a threshold
after dev losses/throughput. Reader result hashes are frozen in activation evidence.

Fixed ignored plan/output:

```text
data/baselines/task0012-particle-memory-plan.json
data/baselines/task0012-particle-memory-study/
```

Plan binds actual revised prompt, unchanged mathematical/config identities,
exact profile hash, fresh source acceptance, original failure/preflight records,
zero previous consumption and allowed phases. It explicitly supersedes the unused
Task0011 route without resetting/creating its ledger. Each readiness/reader/dev
phase is exclusively reserved before fresh-process dispatch, with token/parent/
plan/source/profile checks and exclusive worker-directory creation. Duplicate,
foreign, stale or out-of-order dispatch fails before readers. No force/task/output
override. Full fitting, selection, freeze and calibration are absent/forbidden.

If activation succeeds, one new stable readiness precedes the original disposable
dev gate: first1024 source-ordered frozen dev-train IDs, batch32, at most3passes/
96updates, one same-sample score pass,≤300s. No weights/reconstructions/codes or
per-event scores persist. Step pre/post hooks journal reserved/completed/inflight
updates without altering Adam numerics. Per-view metadata observation records
presentations and sample-relative seen-bitset/unique counts in ignored audits;
IDs never become neural inputs. Reader64 is part of the same1024 sample, not an
additional optimization/model-selection allowance. No hidden worker/full pipeline.

Complete loading/view/training and scoring timings must satisfy unchanged
`2*(699957*max(train_pass_seconds)/1024+74749*score_pass_seconds/1024)≤180s`.
No loss-improvement criterion or settings tuning. Failure ends dependent work;
passing would establish bounded feasibility only, with canonical baseline pending.

## Future artifact/completion compatibility — specification only

Task0012 produces no trained artifact. Existing model/artifact validator remains
unchanged and cannot treat a v2 study as a v1 completion. Task0013 must implement
a separately versioned artifact/completion envelope before canonical execution:

- Preserve model type/architecture/orderedFP32 parameters, data/split/input/loss/
  score and mathematical/training config identities; no mutation of old8GiB JSON.
- Require a typed **active engineering-policy receipt**, with inline sidecar,
  canonical policy hash/version/type, model-config hash, exact allowed launch-only
  diff, actual monitor implementation, fresh canonical authorization/source
  acceptance and per-run stage/resource evidence. Scope must explicitly admit
  canonical fitting; the current Task0012-only profile/receipt cannot supply it.
- Validate config↔policy↔source↔stage relationships and convergence/restoration/
  exact independent reproduction/freeze prerequisites. Do not reuse generic
  `resource_gate_passed` as evidence of original policy-v1 host compliance. A v2
  receipt must explicitly mark policy-v1 compliance false and actual policy pass.
- Keep policy/attempt engineering provenance, paths/timestamps/timings outside
  mathematical weight identity while binding them in the artifact envelope.
  New completion schema distinguishes v1 and active-policy evidence; old artifacts
  remain valid under their historical validator. Unknown/missing/mismatched
  receipts, scope, profile changes or unresolved convergence block freeze/calibration.

Whitelisted current interface changes: optional engineering optimizer observer in
original `run_dev`; optional audit sample/ID callbacks with metadata only; guard
refusing superseded unused Task0011 recovery. New sidecar/monitor/study modules
handle admission, resource evidence and exclusive routing. Model, preprocessing,
reader semantics, objective, initialization, Adam implementation, score, stopping,
calibration and artifact parsing are unchanged. Synthetic observer-equivalence
tests verify identical updates. No dependency/export/CI framework changes.

## Actual measurements and outcome

**Provisional launch still blocked: no new real reads.** One source-accepted
study invocation reserved/dispatched only its read-only pilot preflight. The
host state differed from the earlier post-reboot Task0011 observation: every
sample is now below both4.5GiB admission and the unchanged4GiB floor. No reader
phase could safely proceed, so no reader-footprint or dev-throughput claim exists.
Original reports/preflight/ledgers remain untouched; no readiness repeat/reset.

Fresh CPU worker, one intra/inter-op thread/determinism, samples2026-10-07,
Europe/Rome UTC+02:00; actual page size16384bytes:

| Time | Free / inactive pages | Available bytes /GiB | Lifetime peak RSS bytes | Current Mach RSS bytes | Native reserved /in-use bytes |
| --- | --- | --- | ---: | ---: | --- |
| 09:04:30.926013 | 3850 /165471 | 2774155264 /2.5836334228515625 | 344866816 | 344899584 | 175816704 /139065840 |
| 09:04:33.431085 | 4089 /162656 | 2731950080 /2.5443267822265625 | 344899584 | 334348288 | 180011008 /139078256 |
| 09:04:35.934302 | 4027 /172706 | 2895593472 /2.6967315673828125 | 344899584 | 332103680 | 180011008 /139089904 |

Span5.008331250s, context/sampling5.047508625s, within30s. All available checks
fail launch/floor; RSS/native ceilings pass. Own-task virtual address reservation
was446326652928bytes, distinct from physical RAM/current RSS/native allocation.
Current Mach and OS lifetime-peak RSS are separately named API observations, not
subtracted to infer dirty/private bytes. Dirty/private remains unmeasured.
`memory_pressure -Q` reports16GiB installed and contextual free36%, not a normal
pressure-state proof or substituted availability. Verified pressure sysctl is
permission-restricted (errno1); current swap/ps telemetry also unavailable. No
categories were added; raw compressor and cumulative swap counters remain local.

Readiness probe durations7.115709/14.897834/17.668959ms, total39.682502ms. These
three read-only observations include primary probe and optional native telemetry;
they do not measure steady watcher duty, reader cost or detector latency. No live
watcher/journal was started because readiness failed. Startup is included in
worker/parent stage accounting; the curated summary records whole-worker duration.

The [small factual summary](../results/tables/final/task0012-particle-memory-policy-summary.json)
contains exact arithmetic/limits, source/profile/lineage hashes and access audit.
Plan and pilot reservation remain exclusive under ignored data. No dev-reader/
full-custody/dev reservation, activation or trained artifact exists. Task0011's
unreserved route remains historically intact and is now explicitly superseded
by this engineering plan, avoiding additive optimization allowances.

```text
Task0012 readiness checks dispatched: 1
Task0012 reader/custody/dev phases reserved or executed: 0
real population requests / view presentations / unique dev events: 0 / 0 / 0
real optimizer steps started / completed: 0 / 0
remaining original dev optimizer allowance: 96
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Execution acceptance: full synthetic suite **362passed**; targeted particle
suites195passed. Final reservation review additionally verifies phase/status/
max-step allowance before a worker directory/read; three rejection cases bring
fresh current-source acceptance to **365passed**. The earlier failed readiness
remains bound to its original362-test source and was never reused or repeated.
One earlier targeted fixture incorrectly expected its computed headroom to fail;
the synthetic startup fixture was corrected, then all195passed. No real stage
used failed tests. Ruff lint/format, dependency/import/CPU smoke pass; actual
acceptance producer renewed workspace5228448bytes/2synthetic updates and source
identities before study and after final review. Acceptance flags were not manually changed. Synthetic
cases cover strict profile/diff/hash, immutable config, equality/unknown/veto,
overhead/deadlines, exact64/no-full-population custody, partial audit, phase/
lineage/predecessor/duplicate rejection,96-step reservation/inflight accounting,
observer numerical equivalence and refusal of full training/calibration. Actual
live reader/watch/dev behavior remains unverified. HostedCI/remote push unverified.

The policy is **reviewed/provisional, not activated**. Source-derived admission
reasoning is explicit, but reader evidence cannot yet justify a frozen dev or
full-run profile. The smallest next decision concerns a stable suitable host
state/accounting envelope that preserves4GiB under load, followed by explicit
new readiness/measurement lineage if authorized. Do not infer a model requirement
or modify the floor from this failure. Parent Torch/runtime imports contribute
host demand but were not separately measured; no causal claim about the drop
from Task0011 or uninspected applications is made. A lighter supervisor could be
reviewed separately, without assuming it restores readiness or bypassing limits.
No automatic retry, phase replay, task numbering or canonicalTask0013 here.
