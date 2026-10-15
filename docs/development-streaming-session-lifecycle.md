# Development streaming: session journal ownership and sequential lifecycle

Task0057 repairs the demonstrated lifetime mismatch between a session journal and
case cleanup, then qualifies the **actual shared candidate loop with generated
inputs**. Status: `completed_software_only_streaming_session_lifecycle_repair`;
readiness: `requires_fresh_bounded_operational_authorization`. This supplies no P4,
real AE parity, physical throughput or scientific evidence. Task0056 remains
`partial_failed_development_hdf_pilot_v2`, with its session consumed and its valid
real PCA component preserved.

The clean starting base was main/origin/main, HEAD
`5e64b42a34fb7f2e09d9d657f1070e1025744c8f`, empty index, memory1.51. These are local
facts, without a fresh remote, push or hosted CI check. Memory now advances to1.52.
The [actual prompt](prompts/0057-streaming-session-lifecycle-repair.md) and
[Italian handoff](handoffs/0057-streaming-session-lifecycle-repair.md) were created
before implementation. No pre-existing changes needed separation.

## Defect and focused repair

A deterministic test used an actual newly owned generated file and the original
Journal implementation: snapshot descriptors; construct the journal; first lazy
write; case emergency release; second publication through the same Python object.
The first write registered the fd after the snapshot. Cleanup closed/unregistered
it, but the object retained its numeric fd. The second write reproduced exactly
`QuotaError: Unregistered diagnostic descriptor`. The pre-fix source hash, order,
registration observations and exception are retained privately and copied into the
[curated summary](../results/tables/final/task0057-streaming-session-lifecycle-summary.json).
No operational source was needed to establish this defect.

`pilot54.candidate_session` now owns the single persistent journal, explicitly
opens/registers it **before any per-case snapshot**, runs the original case/core,
retires case resources, checks the same journal, and independently closes it in
its finalizer. The operational wrapper calls this function; the new generated
entrypoint calls that same function with a distinct immutable generated context.
The activation/custody wrapper is not executed or newly qualified here. There is
no copied test controller, per-candidate journal or replacement fd between cases.

Journal identity includes the actual registry tuple object and fstat device/inode.
Both are checked before writes and close. A closed/reused numeric fd cannot
silently target another registered file, including reopening the same pathname.
External numeric reuse with a different inode is also rejected. Safe successful
close is idempotent; unopened close allocates nothing; a failed close retains
ownership so a later checked cleanup remains possible. Open/truncate failures
remain closable. Writes are bounded to65,536B and65,536 successful generations;
short/failed writes propagate rather than inventing a publication.

The short-write regression exposed an additional reader defect: a partial header
could present a zero payload length and reach JSON decoding. The reader now
rejects zero length, invalid CRC/length and malformed JSON as an incomplete record.
No recorder append optimization, threshold change or extra native comparison was
performed. Quota validation was retained.

| Owner | Resource and lifetime | Retirement evidence |
| --- | --- | --- |
| Sequential session | One65,536B tracker journal, opened before case snapshots | Same fd/inode after both case cleanups; one logical final close/unregistration |
| Subject | Heartbeat and its own tracker journal across all15 checks | Independent subject finalizer and externally observed exit/reap |
| Case |12,288B ring, record/output files, bounded samples/phases;21SemLocks | Existing emergency release, mapping close/unlink, gc and semaphore absence |
| Child | Private generated source/model/features, handles, audit and output ownership | Normal close/reap or explicitly retained abnormal/forced cleanup |
| Outer observer | Bounded receipt; no explicit SemLocks | Receipt outside the measured subject, separately reserved4s |

Case cleanup still releases case leaks. No journal-path exemption was added to
`emergency_release`; the registered session fd is already in its snapshot.
Persistent ownership is included in the existing16-fd/3-mapping bounds.

## Frozen qualification and actual outcomes

The [prospective specification](../configs/streaming/development_streaming_session_lifecycle_v1.json)
binds the source/prompt, owners, faults and whole-task ledger. One frozen group
passed all12 existing v2 core expectations and all3 sequential-session expectations
on **40 source/config/test/prompt pins**, bundle
`142d9e0130a5310921c59c0d3ed57f762ed08ebaea5143fa9540d9f0b3cbdfe7`.
CPU runtime and typed tracker policy bytes are unchanged from the base; no extra
CPU bootstrap was required. No source changed during or after native qualification.

| Check | Configured offers | Observed workload | Software expectation |
| --- | ---: | --- | --- |
| Existing core12 |560 | Five normal cases plus declared interruption/contention/publication/report failures; torn uncertainty retained |12/12 pass |
| Normal shared PCA→AE |128 |61/64 completed each;3 contention rejections each; all gates and61 references per candidate | Both valid; same journal across cleanup; pass |
| First-candidate failure |128, of which AE64 unattempted | PCA2 submitted/admitted; one failed read, one queued; zero completions; AE not started | Declared fault, stop, retained uncertainty and final close; pass |
| Second-candidate failure |128 | PCA60/64 completed,4 contention rejects,59 realized groups; AE pre-worker publication failure | Valid PCA, invalid AE, typed observation and independent retirement; pass |

All session candidates use nominalB8,64 periodic offers at500/s and0.128s intended
horizon; the core keeps its exact original matrix. Actual groups are processed at
actual m, without padding or lookup timing substitution. Both normal-session
candidates dispatched singleton groups. The valid PCA in the second fault session
had58 singleton groups and one m2 group, each independently referenced after drain.
Artificial class artifacts use the existing serialization/from-artifact/public
score, full700-particle frozen feature functions and strict four comparisons.
Generated inputs and thresholds remain separate from original scientific assets.

The normal journal retained fd5/inode66030287 throughout its session. Successful
generations progressed0→707 after PCA cleanup→708 before AE→1103 after AE cleanup,
then1104 before final close. The two fault journals each opened/closed once too:
final generations312 and390. Device/inode values identify owned files here, not
portable identities. All three sessions restore the entry fd set. All336 case
SemLock-name absence checks pass; no semaphore or child leak is observed.

The first injected read fails after its intent and before the stand-in return.
At the retained stop boundary PCA has27 intended offers:2 submitted and25 unresolved;
37 remain future. The two admitted requests are one failed plus one queued. One
raw call/row remains in-flight uncertain; neither a return nor normal drain is
invented. The consumer is forcibly terminated/reaped during expected fault cleanup;
one final stand-in handle close is unobserved. This does not turn the session valid.

The second injected AE publication occurs after the valid PCA cleanup, while the
journal remains registered. AE's typed tracker observation is10,272,768B, joint
42,336,256B, state observed/96-byte ABI return/errno0; the deliberately failing
publication is retained separately. Neither worker starts, no t0 or payload is
issued, and all64 offers are future. The journal can still retire independently.

The [21-row table](../results/tables/final/task0057-streaming-session-lifecycle-cases.csv)
contains12 core rows,3 session-boundary rows and6 candidate rows including the
unattempted AE. These are different denominators: summing session rows and their
candidate rows would double-count offers. One group used17 underlying dispatches,
880 configured offers at dispatched cases, plus64 unattempted AE offers: **944
planned offers**. Expected injected failures are successful software checks only.

## Generated numerical work and timing interpretation

Core valid-record lower bounds are446 read rows,444 feature/arithmetic-score rows,
443 independent reference rows and444 completed services; torn work stays unknown.
Serialized sessions record294 raw intents/687 requested rows,293 returned calls/
686 rows,293 feature calls/686 rows, **530 public calls/1120 score rows/4480
Booleans**, including237 independent references/434 rows. There are4 generated
membership/golden/model loads,2 creator models and28 serialized files/189,810B.
Deduplicated setup adds128 singleton feature constructions/rows. No optimizer,
original model or HDF file is involved. Eight stand-in handle opens and7 explicit
closes are recorded, with the remaining fault-session close unobserved.

Across core and session cases, event appends have **1446 samples,1 exceedance** of
50µs, maximum69.125µs; batch appends4311 samples,0 above200µs, maximum51.791µs.
The exceedance occurs in normal-session PCA and is preserved. Full offer/batch
cycle and instrumentation aggregates remain in bounded samples/reports; no
observer cost is subtracted. V2's references are diagnostics, not hard append
bounds, and Task0052's five eligible exceedances remain historical failures.

Normal-session offered-time latency maxima are3.030375ms PCA and2.495333ms AE,
each conditional on61 completions; producer lag uses64 submissions. The other
valid PCA's maximum is3.977ms on60 completions. Each has zero illustrative100ms
misses among completed services. Rejected/future/unresolved requests receive no
imputed latency. These dependent finite generated rows establish no sustained
physical rate, production quantile or independent-event inference. Setup, imports,
logging, control stalls and references are included in their declared histories.
No cache, transport or candidate causal comparison is made.

## Bounds, checks and preserved history

| Envelope | Prospective maximum | Actual scope |
| --- | ---: | --- |
| Complete frozen groups |2 |1; no repair suite or favorable-sample retry |
| Core checks / sessions / underlying dispatches |24 /6 /36 |12 /3 /17 |
| Configured offers |3840 authorized upper;1888 exact two-group plan |944 planned,880 at dispatched cases |
| Core / complete sequential session |5s /20s | Every declared check within bound; sessions6.516399625/1.895271209/2.311176333s |
| Whole qualification |280s =120core+120sessions+40reserves | Subject14.973123708s,18.973123708s including reserved observer4s |
| Global pre-growth storage |32MiB,511 files reserved |30,182,464B reserved for both groups/tests/fixtures/snapshots/failures/curated copies |
| Owned registered fds / mappings |16 /3,143,360 mapped bytes | Persistent journal included; entry sets restored |
| RSS | Outer48MiB; joint inner/tracker80; producer64; consumer1024; aggregate1216; summed-resident512 | Peaks outer28,622,848B, inner32,063,488B, tracker16,826,368B, producer30,064,640B, consumer377,061,376B |

The largest conservative role charge, including the outer reservation, is
499,662,848B; joint charge maximum48,889,856B. These overlapping/non-simultaneous
RSS charges are not unique RAM or precise heap/native workspace attribution.
The external maximum monitor gap is8.710542ms below250ms. The observed subject
interval begins before launching/importing the tested program and ends after
reports/finalizers/exit/reaping; exit0, no forced subject cleanup, owned group absent.
The observer's own receipt is outside that interval, reserved separately. Static
curation afterwards is not an invented measured tail.

The immutable ledger was established before the pre-fix regression or native work.
It covers all attempts and simultaneous final copies, with no quota reset or old
evidence deletion. Ring unlink is resource retirement with its reservation retained.
Owned logical lengths, allocated regular-file blocks, mapped aliases and unknown
filesystem/kernel metadata are reported separately in the summary. Measurable
owned numerical buffers retain the8MiB bound; exact Python8MiB/native512MiB
attribution and decoder effective threading remain unvalidated integration targets.

148 distinct focused/compatibility expectations have passing observations before
native work. Pure execution history is279 checks:276 passed,3 failed. Two initial
failures were the short-header reader and an old fake-fd test missing inode mocks;
a later retry hit an existing empty test directory before file creation. Corrections
and selected reruns are retained; unchanged actual-file tests were not overwritten
or represented as a fresh complete rerun. Lint/format, JSON/CSV/accounting arithmetic,
source identity, historical anchors and local links were checked. All15 native
expectations do have complete coverage on the single final source bundle.

**Zero new operational** custody, HDF/metadata, original array/model or frozen
public-inference work occurred. Historical Task0056 still has two successful custody
passes/5,816,520,818B and valid PCA63/64,207 real raw/features,174 public calls/
342 score rows/1368Booleans; its overall pilot remains failed/consumed. Task0054's
separate custody/failure/consumed session, Task0055 startup qualification, Task0053
v2 qualification and Task0052 partial/negative result are preserved byte-for-byte.
CPU/synthetic0049 closure,0036 unresolved status,0034 gates, permanent YES/YES/YES,
particle192/192 consumed/canonical deferral,0024 accepted export versus0025 failed
performance and no current MPS claim remain unchanged. This independent research
implies no official CERN/experiment affiliation or scientific/detector readiness.

A separately authorized **AE-only** tiny real integration/resource pilot can obtain
the missing real AE evidence. A new two-candidate session would need its own
controller/paired experimental question and grant; it should not automatically
repeat the valid PCA or combine old/new sources into a fictitious paired experiment.
No Task0058, new P4 or24×768/840s study follows automatically.
