# Source-free streaming startup/resource repair — Task0055

**The final source passes all 12 generated cases and both actual installed CPU
runtime bootstraps.** Status: `completed_software_only_streaming_startup_repair`;
readiness: **`requires_fresh_bounded_operational_authorization`**. This establishes
source-free startup and generated-core behavior under the declared guards. It
performs zero new operational custody, HDF opens, scientific-array/model-artifact
loads, model construction or public inference. Library imports, CPU configuration,
own-resource queries and generated numerical work are positive activity.

Task0054 remains partial/failed: its two successful custody passes read
5,816,520,818B, PCA failed before ready and AE was unattempted. Neither the exact
startup exception nor rejected tracker RSS was retained. The raw-text versus
canonical-JSON Torch digest defect is confirmed from source; it remains a plausible
historical cause, not a recovered traceback. Today's compatible runtime and tracker
observations cannot reconstruct those missing facts. Task0052's partial/negative
instrumentation verdict and five eligible exceedances remain unchanged.

The [actual prompt](prompts/0055-streaming-startup-resource-repair.md),
[immutable prospective configuration](../configs/streaming/development_streaming_startup_v1.json),
[28-case table](../results/tables/final/task0055-streaming-startup-cases.csv),
[summary](../results/tables/final/task0055-streaming-startup-summary.json) and
[Italian handoff](handoffs/0055-streaming-startup-resource-repair.md) bind the scope,
sources, both groups and remaining limits. P4 is ungranted here; the consumed
Task0054 pilot was not activated or replaced. No Task0056 or larger study follows.

## Baseline, defects and deliberate policy revision

Verified start: clean `main`/`origin/main`, HEAD
`0dd42ee74521205b3918a43ef00aacb7be99198d`, empty index, Task0054 committed,
memory 1.49. Local tracking refs were 0/0, without a fresh remote/push/CI check.
Prompt and initial Italian handoff preceded substantive work. Instructions,
living context, Task0054 curated report/config/summary/handoff, Task0053 v2
contract and relevant source/tests were read. No ignored historical native journal,
raw/model payload or recursive historical manifest was reopened. The supplied
17,406/47,001/180,164B Task0054 anchors match exact SHA256; six historical sources
remain byte-preserved.

| Before | Task0055 change and claim |
| --- | --- |
| Consumer coupled installed-runtime startup with source/model work | Shared `RuntimeSession.initialize` is now production-used by RealBackend and independently exercised source-free. Payload initialization has its own explicit, rechecked authorization/source gate. |
| Corrected Torch hash existed but no successful real-library evidence | Four fresh workers actually verify the unchanged canonical-JSON-string pin. Independent encoding tests distinguish raw text. No new build is whitelisted. |
| Tracker query rejected without preserving the value; private 64 + 16 MiB split | Typed observations precede rejection. This task explicitly uses **joint inner+owned-tracker 80 MiB**, outer 48 MiB unchanged. It does not pass the old 16 MiB condition. |
| Hardcoded Task0054 directory/task routing in monitoring | Exact immutable ResourcePolicy applies to the generic fixture, regardless of its directory. Tracker observation is required before children advertise ready/t0. |
| Runtime retained detailed failure evidence but consumer wrapper could omit it | Final 0055.2 copies primary runtime context independently of checkpoint publication, retaining separate report/cleanup failures and partial-constructor state. |

The old synchronization backing-byte claim remains unproved; v2's primitive/
lifetime/visible-allocation/RSS interpretation is unchanged. 50 µs event and 200 µs
batch appends remain diagnostics. Correctness, accounting, clocks, bounded resources
and supervised lifecycle remain validity conditions. Instrumentation and control
stalls stay in the histories; no overhead subtraction, recorder optimization or
comparison campaign occurred.

## Shared runtime and payload-not-armed boundary

The common function sets the six single-thread environment requests before NumPy/
Torch imports, imports installed CPU libraries and unchanged core/thread helpers,
configures deterministic Torch intra/inter 1, queries effective OpenMP/Accelerate,
checks rounding and canonical build identity, imports HDF bindings/plugins without
opening a file, queries threads again and returns at **payload_not_armed**.
The runtime policy has no data/model path selector. Future candidate names label
metadata-only worker cases; both execute the identical CPU initialization function.

The actual consumer calls this same function, then a separately gated payload
method. The source-free command cannot invoke that method or reuse the consumed
Task0054 activation. No ProcessedStore construction, model factory, NumPy payload
load, source-byte helper or public score occurs in runtime initialization. Core
imports expose model classes, but bootstrap denial sentinels block constructors,
loaders and scores before CPU helper configuration. NumPy loads and HDF File opens
are also denied. Python-open audits protect all production data/artifact/result
roots and the three model/transform configuration paths outside those roots; they
cover all 17 historical Task0054 files without resolving/hashing them. Generated
producer/consumer lifetimes receive the same file-open denial, including cleanup.
Normal exits require zero denied attempts. Actual runtime workers report 0 denied
opens and 0 production-open successes; API denial counters remain 0.

Fresh spawn avoids illegal Torch interop reinitialization in a reused process.
BLAS limiters are owned/restored independently; Torch state retires with the worker.
A bounded step is published before each fallible action. Exceptions retain type,
message, at most 8 traceback frames, last step, payload-armed state, expected/actual
identity, current RSS when available and lifetime peak. Primary, reporting and
cleanup failures are distinct. Even a failed checkpoint cannot veto the final
consumer failure report attempt or independent close/restoration. Missing subject
reports make the outer receipt fail closed; deterministic loss/receipt tests do
not convert an abnormal workload into a normal run.

## Tracker ABI, readiness and resource interpretation

The installed Command Line Tools SDK `sys/proc_info.h` and `libproc.h` establish
`PROC_PIDTASKINFO=4`, `proc_pidinfo(int,int,uint64_t,void*,int)`, six uint64 plus
twelve int32 fields, **96 B**, resident offset 8 and **byte units**. Source paths,
sizes and hashes are in the configuration. No compilation, privilege escalation,
process inventory or device survey was needed.

Only `multiprocessing.resource_tracker._resource_tracker`'s already-owned PID/fd
relationship is queried. Owner PID, tracker PID, method, timestamp, raw returned
length/errno/resident number and interpreted bytes are retained before a guard.
States are `not_started`, `startup_pending`, `observed`, `exited`, `unsupported`
and `query_error`. An unavailable PID/RSS is not a measured zero; an observed
positive value over a limit remains that positive number. The generic core waits
at most 250 ms, polls at most every 5 ms under continuous monitoring, and cannot launch
ready/service before a valid tracker observation and joint guard. A late positive
query also fails. Observation loss after ready is invalidity.

A pre-tracker subject heartbeat charges the whole 80 MiB supervisor reservation,
explicitly without claiming measured tracker memory. Once observed, tracker
current RSS/observed peak and supervisor lifetime peak are recorded separately;
the conservative joint charge counts the tracker once. Lifetime peaks and shared
pages are not simultaneous exact unique RAM. Every active role retains its v2
cap: producer 64 MiB, consumer 1024 MiB, outer 48 plus inner/tracker 80 within combined
128 MiB; aggregate 1216 MiB and additional conservative summed-resident 512 MiB.
No conversion of RSS into kernel backing, Python heap or native workspace occurs.

| Native observation | Group1 | Final group2 |
| --- | ---: | ---: |
| Tracker observed peak, B |16,596,992|**16,842,752**|
| Maximum joint supervisor+tracker charge, B |47,792,128|**48,332,800**|
| Whole-subject tracker observation count |1,275|1,193|
| Initial `not_started` records |1|1|
| Largest tracker-ready query duration, ns |367,708|418,167|

The final tracker peak is 65,536 B above the old 16 MiB partition, while its joint
charge remains below 83,886,080 B. This supports the new joint policy; it does not
prove which value Task0054 rejected. Native startup was already positive when the
core queried it; zero-RSS pending/deadline/error cases were established by independent
injected-query tests, not invented as native observations. State/cardinality/sample
limits preserve first 32 typed samples, last/first failure, counts and peaks; per-case
fixed journals keep crash-visible bounded snapshots.

## Frozen native qualification and actual runtime results

Two fixed groups were consumed, **28/28 maximum native invocations**: 24 generated
cases with 1,120 configured artificial offers (limit 3,072), and 4 zero-offer runtime
workers. All expected software checks passed. Expected injected crashes, torn
records and report quota failure remain abnormal fixtures with preserved accounting
uncertainty; they are not valid drained workloads. Each group has 5 normal cases,
7 specified failure checks and 2 runtime bootstraps.

The first group bound source 0055.1
`24eee96cc423fdcc85ec1b60e16cc520d21284693222cdc80aa874496dad33f0`.
Review after that pass found the actual consumer failure-wrapper propagation gap.
A documented correctness repair, with unchanged pins/resource limits, justified
the second complete group. The **final 0055.2 bundle** is
`277539820154b19012d53b5a4ec1f05093244b7efa1877f3e09649cbba43e7d0`.
All12+2final cases pass on those same 30 source/config/prompt pins; no earlier-source
pass supplies final coverage. No source changed during either group or afterward.

| Source-free actual CPU worker | Inclusive case seconds | Captured lifetime RSS peak, B | Outcome |
| --- | ---: | ---: | --- |
|Group1 PCA metadata|3.502728916|374,784,000|payload_not_armed; normal exit/reap|
|Group1 AE metadata|2.073095542|374,833,152|payload_not_armed; normal exit/reap|
|Final PCA metadata|2.942929542|349,306,880|payload_not_armed; normal exit/reap|
|Final AE metadata|2.078856333|374,964,224|payload_not_armed; normal exit/reap|

All four report Torch 2.14.1, NumPy 2.5.3, h5py 3.16.0/HDF5 2.0.0, rounding mode 0,
Torch intra/inter 1, deterministic algorithms, both loaded OpenMP pools 1, and
successful public Accelerate setter/getter single-thread mode 1 on the owning
thread. Plugin import succeeded; its version attribute was unavailable and decoder
effective threading remains unknown. Before/after effective-thread queries pass;
limiter cleanup reports no error. These are runtime configuration observations,
not tests of numerical model behavior or decoder/model workspace under service.

Expected/actual canonical Torch hash in every worker:
`6d6fa299a6d76bc6add8bfff4916da33cbc1636da24e90df594e6434f918b26c`.
Raw-text diagnostic hash:
`7dc7bbe085616975d2b87b5c43ed0bd5e4a3a26e8e1013db641518c8d46daa1c`.
The differing definitions are explicit. No original failure traceback is recovered.
Metadata-selector timing/RSS differences do not compare PCA versus AE: neither
candidate exists in these workers, and import/cache/host histories are uncontrolled.

Final generated normal cases complete 127/123/122/64/0 of 128/128/128/96/32 configured
offers. Losses, scheduling lag, queueing and conditional latency summaries remain
per case. 100 ms is illustrative. Across both groups, reconciled-record lower bounds
are 879 read rows, 873 feature/arithmetic-score rows, 871 reference rows and 873 completed
services / 3,492 primary Boolean outputs. Torn cases retain unknown work. All four
runtime workers offer 0 events and perform 0 scientific scores.

Across both groups 2,116 event appends contain 2 diagnostic exceedances, max 98,667 ns;
4,314 batch appends contain 0 exceedances, max 67,042 ns. Group1's event exceedance is
in contention; final group's is in torn publication. Denominators, homogeneous
cycle/append aggregates and unfavorable observations are retained; no sample
replacement, percentile fitting or uninstrumented-throughput claim is made.

## Validation, whole-task envelope and limits

**96 focused tests pass on final source**, including 57 new startup/resource cases,
36 prior focused integration checks and 3 relevant pure v2 checks. Independent byte/
OS-layout/query oracles cover canonical encoding, actual/expected mismatch,
zero/negative/oversized/error/late RSS, owner/PID mistakes, valid 0 clock versus
unknown, exact joint 80 MiB inequality, readiness/deadlines, each initialization
step/import failure, partial construction, short publication, primary/report/cleanup
separation and missing-final-report regression. File-access/entrypoint audits prove
normal, malformed, failure and cleanup paths remain source-free.

One early unit denial test found three configuration paths not covered by root-only
blocking; it was fixed before native work. All 419 pure-check executions are retained
(1 early failure/418 passes across runs). One dot in the early log became NUL while
`pwrite` was deliberately mocked; the original log remains and a stable guarded
writer recheck passed. These are not extra native invocations or hidden retries.
Lint/format, JSON/CSV, arithmetic, links, historical hashes and final source identity
are checked. No historical full/native/model suite or dependency install ran.

An immutable **370-entry / 22,349,984 B** pre-growth ledger covers both groups,
source snapshots, all case/phase/output/timing/tracker/bootstrap journals, attempts,
failures, reports, receipts and simultaneous curated copies under 32 MiB. No old
Task0054 directory is read or charged. No evidence is erased to recover quota.
Source snapshots ≤786,432 B/group, case reports ≤131,072 B, runtime worker/parent reports
≤32,768/65,536 B, startup/resource journals 65,536 B. Core ring/records/samples,
3 mappings / 143,360 B per process, descriptor/cardinality and 34,080 B generated numeric
bound remain. Metadata has ≤24 startup steps, 32 first tracker samples, 8 traceback frames;
publication/JSON/tree/FD bounds are enforced. Heap/native/kernel attribution remains
unknown. Own-file logical lengths and allocated blocks are separately reported.

External subject intervals are 9.345746166 s and 8.830618916 s: **18.176365082 s** total,
including imports, all cases/reconciliation/reporting/finalization/exit/reaping.
Two 4 s observer reserves give 26.176365082 s charged versus 200 s. Each group is capped
at 100 s with remaining-time admission; subject 96 s, cleanup through 98 s, receipt by 100 s.
The receipt's own write is outside the measured subject and separately reserved.
Static curation is outside these programs, not an inferred measured tail.

Every generated case is below5s, every runtime case below10s. Maximum generated
cleanup 32.220041 ms, inner monitor gap 30.038250 ms and outer 9.237917 ms stay within
2 s / 250 ms. Outer exits 0, no forced group action, all subjects reaped and owned groups
absent. Twenty-two streaming cases retire **462 own semaphore names**; core 21,
runtime/outer 0 explicit SemLocks, cap 26. An all-observed-role-peak conservative upper
charge of 503,644,160 B (including reserved outer 48 MiB and nonconcurrent producer peak)
is below 512 MiB; it is not measured simultaneous physical RAM. RSS is sampled with
captured own lifetime peaks; no uninterrupted instantaneous workspace guarantee or
post-exit unique-RAM attribution is claimed.

P1 has complete final-source generated correctness and shared CPU startup evidence.
P2 gains typed tracker/CPU-thread/import-RSS evidence under the revised joint policy;
real HDF/cache/model integration, 8 MiB Python and 512 MiB native-workspace attribution,
effective decoder threads and service behavior remain unvalidated. P3 remains an
instrumented generated/runtime observation, not detector/event-byte transport or
physical throughput. P4 remains ungranted here. If desired, the next separate
decision is a fresh narrow pilot prompt for the unchanged PCA→AE two 64-offer B8/
500 s⁻¹ workloads; none is granted or executed by this task.

CPU/synthetic Task0049 closure, Task0036 unresolved_no_acquisition, Task0034 scientific gates,
permanent YES/YES/YES, particle 192/192 consumed/canonical deferral, Task0024 accepted export
versus Task0025 failed performance, historical outcomes and no current MPS claim persist.
No strict-tail usefulness, physical efficiency, causal nonlinearity, independent
scientific confirmation, detector readiness or official CERN/experiment affiliation
follows from this independent research engineering task.
