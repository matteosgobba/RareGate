# Instrumented development request pipeline — contract v2

**How does the explicitly instrumented software-request pipeline behave when its producer, finite FIFO, actual-shape generated work, observers and controls are all part of the experiment?** Task0053 adopts a result-informed exploratory engineering revision. It does not estimate an unseen pipeline with instrumentation removed. Task0052's five eligible event-append exceedances, `partial_generated_streaming_instrumentation_characterization` and `sampled_limits_exceeded` remain permanent historical facts.

Actual outcome: **`completed_generated_streaming_contract_v2_validation`** and
**`generated_software_qualified_under_v2`**, operational readiness false. All12
expectations passed in one frozen suite; no repair/second suite or recorder comparison.
The instrumented pipeline still records10event/4batch diagnostic exceedances; this
qualifies v2 software behavior without passing or relabelling the old append gates.
See the [12-case table](../results/tables/final/task0053-streaming-contract-validation-cases.csv),
[summary](../results/tables/final/task0053-streaming-contract-validation-summary.json)
and [Italian handoff](handoffs/0053-streaming-contract-v2-validation.md).

The finite recorder comparisons did not establish append bounds, and the streaming path exceeded the proposed event limit. Rather than fit a replacement threshold to103.041µs, the actual Task0053 prompt explicitly changes the question and qualification criteria. The [resolved v2 contract](../configs/protocols/development_streaming_v2.json) and [prospective validation specification](../configs/streaming/development_streaming_validation_v2.json) keep operational execution, allowance and readiness false. P4 is ungranted. This is neither independent confirmation of v1, hard real-time validation nor proof of an all-in OS/kernel footprint.

## Explicit decisions and preserved boundary

| Requirement | v1 / historical result | v2 generated qualification |
| --- | --- | --- |
| Append times |50µs/event,200µs/batch proposed validity gates; Task0052 event criterion failed |Same numbers remain diagnostic references. Retain every exceedance, inclusive cost and denominator; no overhead subtraction or replacement samples. |
| Synchronization |65,536B all-in backing unproved |At most21core SemLocks/active case, whole active validation tree≤26; actual outer observer uses0. Purpose/ownership/lifetime, visible allocations and RSS guards required; unknown backing remains unknown. The old byte condition is superseded for generated qualification, never declared met. |
| Python/native attribution |8MiB Python/serialization and512MiB native workspace unproved |Exact owned binary bounds, bounded container cardinalities and enforced RSS guards qualify generated software. The original integration targets remain unvalidated; no exact heap/native allocation attribution is inferred. |
| Global storage/time |Duplicated report storage and inclusive finalization missing in0052 |One immutable task-wide pre-growth ledger covers both possible suites; independent observer spans subject launch/imports through reports, finalization, exit and reaping. Observer receipt is separately reserved outside that interval. |

Identities, finite arithmetic, parity/ownership, conservation, resource/time monitoring and supervised lifecycle remain validity conditions. An append exceedance is an observed diagnostic. Lost accounting, a corrupt normal record, unsafe resource use or unexpected process failure is a validity failure. Expected injected invalidity counts only as a software check when the specified failure, uncertainty and cleanup are observed; it never becomes a valid drained workload.

The frozen scientific baseline, development source roles, feature/scaler/model/calibration identities, full-particle feature semantics and future independent same-shaped references remain unchanged. The v2 JSON binds copied v1 identity/feature/parity/history requirements and original source hashes; it does not freshly verify or execute them. Future raw scope is384symbolic positions `0..127,448..575,896..1023` in the same sorted1024-ID prefix;1024golden rows are a distinct scope. The physical24×768/840s proposal remains unexecuted/ungranted.

Unchanged core:64B little-endian descriptors,64B admission/sequence metadata,4096B control plus64slots =12,288B ring, one mutex over all shared access,64credits including ring/staged/active, staging/active≤8. FIFO by sequence, nominalB8, oldest admission1ms timeout, final partial drain without extra offers. Lazy open-loop intended times `t0+floor(k*1e9/rate)`, horizon `t0+floor(N*1e9/rate)`, lag>2ms missed, at most4nonstale attempts per wake, one nonblocking admission try, contention/capacity rejection and no submission at/afterH. No completion feedback, padded/full-B billing, timing vectors or hidden event Queue/Pipe/socket.

Only generated memory is supported: a fresh1024×3FP64 table, actual-m synthetic eight features, arithmetic score and four owned strict `score > threshold` masks, ties false. The selected gather/scatter and independent generated reference retain the original actual-m behavior. No HDF, even generated, no raw/model/scientific arrays or operational provider. Descriptors represent software row requests, not encoded event bytes or a detector link.

```text
outer observer (no SemLocks; imports/exit/reap boundary)
  └─ subject supervisor → open-loop producer → descriptor FIFO /64inclusive credits
                               ↓ actual m≤8 generated selected read/features/strict4
                         owned outputs → reference/control/journals
                               ↓ case cleanup, named-resource retirement, report close
                         subject CSV/JSON/finalizers → exit → outer wait/reap
                         outer receipt outside measured subject
```

## Recording, reuse and observations

Task0052's recorder is retained: reusable512B encoding scratch, full validation/zeroing/CRC before mmap publication, unchanged512B event/batch format, explicit null versus valid0 timestamps, reserved/canonical checks. File creation/truncation and fixed writes now route through the activated quota guard; no recorder optimization or AB/BA comparison is conducted. Journals are not heap-only buffers. Single writers and stopped readers do not make an in-place record atomic: torn records invalidate accounting and retain uncertainty, never invent an older successful record. Process-crash visibility is distinct from power-loss persistence; no fsync/flush durability claim is made.

The append timer still surrounds the full Store.write call: validation, encoding, allocation inside the operation, CRC and publication. Statistics/sample publication follow. The observer timer includes max/count and the first timing-record publication; the second record cannot recursively time itself, but remains inside complete offer/batch/lifetime work. Offer cycles include record construction, both intent/resolution appends when applicable and admission control. Batch cycles include all stage writes and actual-m generated read/features/score/output/reference/digest/control. These full cycles contain all instrumentation and actual work; they are not isolated logging overhead.

Initialization, mapping/page touches, phase journals, quota checks, output retention, GC/own-name checks, record/sample parsing, JSON-size preflight, serialization/file close and cleanup all contribute to the instrumented history. Per-case homogeneous timing aggregates preserve n,sum/mean/median/p95/p99/max/exceedances with linear `(n−1)p` quantiles; no averaged quantiles or heterogeneous distributions. Interrupted samples/returns remain unknown, not zero. All original samples and output masks remain in owned ignored binary files; curated outputs contain aggregates only.

Each generated case resets k and has N≤128, using symbolic positions0…127. Repeated rows/cases are presentations, not new independent source events. Fresh generated tables and mapping read-touches do not establish cold OS cache. No purge/reboot/app closure, prefetch, timing-vector reuse or causal transport/cache attribution is part of this experiment.

At H/stop preserve `O=U+M+S`, `S=J+Rcapacity+Rcontention+A`, `A=Qring+Qstaged+X+C+F+K`; outputs=4C, false masks still complete. Distinguish configured, due, submitted, admitted, missed, rejected, completed, failed, active/queued and unresolved work. Intended-offer latency cannot conceal delayed producer submission; producer lag, queue wait and directly measured joint service remain separate. Completed-only summaries carry n.100ms remains illustrative; overload and deadline misses are workload results, not automatic retry reasons. Safety retains operation/no-progress2s, design drain5s, monitor gap250ms, discrepancy5ms, child cleanup2s and case5s.

## One global diagnostic ledger

One new ignored Task0053 root holds an immutable ledger before any subject/native case. It reserves **294file entries /15,136,928logical bytes** for two complete suites, within16,777,216B; unused reservations remain charged. The second suite is permitted only after a correctness failure and a new source identity. Source edits while a suite runs are forbidden. Nothing from ignored0051/0052 payloads is reopened or counted as a new allocation.

| Reserved group | Role and limits |
| --- | --- |
| Fixed binary files |Each streaming case: ring12,288B; event+batch1024N; outputs12N; phases3×32×512; samples768×64 and4096×64. AtN128 total505,344B. Files back mappings once as owned payload. |
| Case reporting |One authoritative compact result≤131,072B per attempted case, one reserved1024B emergency. No duplicate producer/consumer/supervisor JSON or window copies. Counter preflight≤1024B. |
| Zero-offer case |4096B cleanup guard,16B quota target, bounded emergency and result. A17B final-report attempt must be rejected before creating the target. |
| Shared/task reporting |Ledger65,536B, owner1024B, historical manifest8192B, two source bundles≤524,288B each, prospective manifests≤65,536B, observer receipts8192B each, heartbeat4096B each, suite CSV16,384B and subject summary8192B each, one final aggregate524,288B and CSV32,768B. |
| Simultaneous delivery copies |Additional unmaterialized reservations charge curated summary524,288B, CSV32,768B and text131,072B; they are not falsely counted as materialized files. No serialization temporary file is used; declared temp/final pairs remain fully charged if used. |

Every create/open-for-write, truncate, pwrite and rename checks the immutable path/cap reservation first. JSON container and exact encoded-size checks precede file creation; bounded chunks are streamed to an exclusive new file. Short/failed writes retain the partial file and reservation. No old evidence is overwritten to regain space. Mutable ring/record/heartbeat slots are explicit protocol state, not replacement case reports. Resource unlink retires the ring/guard while its reservation remains charged. Cleanup is independent of logging acknowledgement and ring mutex, including partial setup and quota failure.

Paths must remain canonical within the owned root; symlinks, hard-linked write targets, undeclared paths, truncate-on-open and evidence replacement are rejected. The root is private to these cooperating generated processes; concurrent external tampering is unsupported. Logical lengths are the pre-growth cap; own-file allocated blocks are reported separately. This neither bounds filesystem/kernel metadata universally nor equates backing files with extra owned mapping payload.

Owned mapping registry≤3/143,360B per process, diagnostic descriptors≤16; Store scratch512B each and shared zero template512B/process. Generated numeric payload bound34,080B is retained. Records/rows≤128 per case, samples≤4096/role, suite rows≤12, task rows≤24. JSON limits are24,000nodes, depth24, dictionary512keys, list4096items, string65,536chars, scalar serialization chunk262,144B. Runtime bootstrap/sentinel/tracker objects are separately acknowledged infrastructure, not event buffers; their backing/workspace attribution remains unknown.

## External lifetime, synchronization and resources

Outer48MiB and inner80MiB split the original128MiB supervisor allowance. Producer64MiB/consumer1024MiB and aggregate1216MiB remain. Own RSS is checked in the hot roles and heartbeat/observer; the generated conservative resident charge also requires summed role RSS≤512MiB. This is a stronger resident guard, not exact native allocation attribution or certification of the512MiB integration workspace target. Peaks/shared pages overlap and are not unique host RAM.

One mutex/four Events actually contain21distinct SemLocks: producer-start, consumer-start, stop and adversarial-armed; supervisor owns, children share spawn references, named primitives retire after each case. The outer observer creates no explicit Event/SemLock, so the active count is21≤26. Own sem_open queries after GC use no create flag, close any obtained reference and require names absent before the next case. The outer also requires its own process session/tracker group absent after reaping. Unknown OS/kernel backing remains unknown; no wrapper-size/RSS translation is used.

The small outer process starts its continuous/service observation before Popen launches the subject, covering the subject's imports, setup, cases, all CSV/JSON work, close/finalizers and interpreter exit. It ends only after wait/reaping and owned-group retirement. Missing reports, forced termination or unknown descendants cannot qualify. A fresh fixed4096B heartbeat supports role RSS and2s reporting-liveness checks; startup/import allowance7.5s and primary250ms monitor gap remain explicit. Diagnostic stdout/stderr are prospectively DEVNULL, avoiding unbounded print/pipe storage; bounded journals, error fields and exit codes are authoritative.

A launch reserves75s total: subject deadline70s, whole-tree cleanup through72s, observer receipt/overhead through75s. Two launches therefore fit150s, with at most120s of24case envelopes plus15s setup and15s finalization/observer work. The observer receipt is outside measured subject time and separately charged5s/launch; no self-referential claim includes its own final write. Post-write total checks enforce75s. The subject's own per-case interval ends after case report close/resource retirement/storage audit; CSV-row formatting is suite aggregation inside the external subject lifetime.

Own-session SIGTERM permits inner finally blocks to reap roles; SIGKILL is the bounded fallback, independent of ring mutex and diagnostics. Group absence is checked; forced cleanup never invents proof that grandchildren exited normally. Service uses perf_counter_ns, supervision Mach continuous/timebase or CLOCK_BOOTTIME; advertised service resolution and observation brackets are retained. A few same-host samples do not calibrate cross-process equality or certify operational scheduling.

## Prospective final-source qualification

Exactly12cases in fixed order:128offers at500/2500/5000Hz;96at500Hz with capacity fill barrier;32at1000Hz forced contention;8at500Hz each for pre-return, post-return, post-output/dead-mutex owner, failed second start, torn publication, failed-publication plus cleanup journal/snapshot/overflow/close; final zero-offer observer/report-quota path. One suite configures560offers; both possible suites1120, below3072. No AB comparisons, warm-up presents, sample selection or favorable scheduling/drop assertion. Slot reuse is explicitly required in normal500; other exact counts are observations unless controlled by the fixture.

Case12 deliberately rejects growth of a final-report target, writes bounded emergency evidence and retires an owned cleanup guard. Its software expectation also requires the independent outer receipt after the subject closes final reports and exits; it cannot self-certify that lifetime. Fake-clock tests exercise reporting stalls, failed launch, finalizer exit and receipt failure before native work. The eleven streaming fixtures retain explicit crash barriers, CRC/uncertainty and overflow/cleanup controls.

Qualification requires all12software expectations and complete global storage/time evidence on **one final frozen source bundle**. Earlier-source passes cannot fill final gaps; if one repair requires a new bundle, only one complete second suite is available, all failures retained. Append exceedances never invalidate otherwise correct v2 cases, nor erase0052's old verdict. Operational readiness remains false.

## Actual final-source result

Start was clean main/empty index,710tracked paths, HEAD1155e83f8ab99adfbd7bc0044d4128f9e188e278,
Task0052 committed, memory1.47. Local origin/main0/0 does not prove a fresh remote,
push or CI. All supplied Task0052 anchors matched exact20,058/19,836/257,627bytes
and SHA256; nine historical inputs remain unchanged. No ignored0051/0052 fixture
payload was reopened. Their committed source and curated evidence remain historical.

The frozen bundle is `1e015d6d6575e1004c337a1d6d84fec416bbf63ed91e25377e3bf876aed3e03e`.
All12cases/560configured offers passed the declared software expectations on that
bundle; code/config/test/prompt hashes match before/after and at delivery. Native
unexpected failures0; expected invalid cases7, valid drained cases5. The second
suite was neither needed nor run; its file reservations remain charged.120focused
tests, lint and format pass. Pure tests cover independent bytes/CRC/nulls and pinned
0051/0052 backward compatibility, global cross-attempt/duplicate/temp/final bounds,
short/failed writes, path escapes, setup/cleanup failures and fake observer reporting
stalls/finalizer/receipt/launch errors. No test started a native qualification case,
no full historical/model/native matrix or dependency installation ran.

| Native case | Configured / completed | Observed loss or expected invalidity |
| --- | ---: | --- |
|500/s|128 /116|11producer misses,1contention rejection; slot reuse observed |
|2500/s|128 /123|2misses,3contention rejections |
|5000/s|128 /119|3misses,6contention rejections |
|Capacity barrier|96 /64|31capacity+1contention rejections;50illustrative100ms deadline misses |
|Forced contention|32 /0|32contention rejections, normal supervised drain |
|Pre-return|8 /0|read intent uncertain; queued/active/unresolved retained |
|Post-return|8 /0|one returned row, no constructed features |
|Post-output/dead owner|8 /1|completed output survives death while actual mutex held |
|Failed second start|8 /0|configured offers distinct from0issued submissions; no fabricated H |
|Torn publication|8 /unknown|CRC invalidity; accounting/stage totals null, not zero |
|Failed publication/cleanup|8 /0|OSError, overflow preflight preserves credits; phase/snapshot/close failures cannot veto cleanup |
|Outer report/quota|0 /0|17Breport rejected before16Btarget creation; bounded emergency retained, guard retired; outer exit/reap receipt true |

The capacity survivor maximum is193.168084ms(n64), with50deadline misses, versus
12.724333/3.771042/3.318750ms maxima for the three normal load cases(n116/123/119).
These are conditional finite stub observations, not production percentiles or HDF
service bounds. Source order/histories/control stalls and input reuse remain those
prospectively declared; no adverse observation was replaced.

All retained append samples:1,041event,10exceedances, maximum963,000ns;1,970batch,
4exceedances, maximum2,074,625ns. Normal500 contributes9event and all4batch
exceedances; the post-return fault context contributes1event exceedance. Grouped
statistics retain stages/m/update counts and fault context. Observed complete cycles
have529offer samples(max4,352,792ns),177batch samples(max12,353,584ns); maxima are
context only, not pooled distributions or isolated overhead. Phase append reached
3,592,708ns, initialization53,865,583ns, finalization324,959ns and output loop294,166ns.
No causal claim identifies encoding/filesystem/scheduling as the source.

From ten valid-record streaming reports, lower bounds are181read intents/425returned
rows,178feature+arithmetic-score calls/423rows,177reference calls/422rows,423completed
services/1,692primary Boolean outputs and1,688reference Boolean comparisons. The torn
run's stage work remains unknown. Ten generated backends were constructed; unit
numerical/record activity is additional. This positive generated work is distinct
from zero operational data/model/HDF/public inference work.

The external observer measured **3.426913083s** from before Popen/import through
all subject reporting/finalizers/exit/reap and owned session retirement. Summed
complete case intervals are3.301730208s; they do not substitute for the larger
external interval. Its5s observer overhead reservation gives8.426913083s charged
against150s; post-receipt75s guard passed. Maximum case546.627583ms(<5s), child
cleanup32.246750ms(<2s), inner monitor gap30.996417ms and outer16.543875ms(<250ms).
Outer actions were unforced, exit0/reaped/session absent. The observer receipt's
own last write is outside subject time. Static document/result curation is outside
the tested program and separately reserved; the subject itself produced its case
JSON, CSV and qualification JSON before exit, so no subject-reporting tail is inferred.

Immediately after the observer receipt the owned root had4,645,602logical bytes;
its earlier pre-receipt inventory is explicitly timestamped in that immutable
receipt. Final root/curated-copy byte and allocated-block accounting is in the summary,
under the same15,136,928B reservation/16MiBcap. No earlier file was discarded to
recover quota. The294entry ledger includes the unused second suite and simultaneous
curated copies; actual small output is supplementary to, not a replacement for,
pre-growth proof. Metadata attribution remains unknown.

Captured peak RSS: producer25,247,744B, consumer33,865,728B, inner27,836,416B and
outer23,298,048B; largest same-case peak sum including outer109,903,872B. They
satisfy the enforced role/resident-charge guards but are not unique RAM or exact
Python/native workspace attribution. All231own semaphore names across eleven
streaming cases were absent after retirement; active explicit count21, observer0,
cap26. The old65,536B claim remains unproved.

P1 now has complete final-bundle generated correctness/cleanup coverage. V2's
primitive/lifetime and visible binary/container/RSS conditions qualify; P2 real
HDF/cache/model/Python/native workspace and effective threads remain unresolved.
P3 supports this instrumented generated software observation, not operational
clock/scheduling or hard real-time behavior. **P4 remains ungranted**. Next is one
separately scoped decision on selected-HDF/frozen-PCA/AE consumer integration and
resource/cache/workspace/effective-thread checks under explicit operational
authorization; no integration, recorder benchmark or Task0054 follows now.

CPU/synthetic0049closure, Task0036unresolved_no_acquisition, Task0034gates,
YES/YES/YES, particle192/192consumed/canonical deferral, all historical outcomes,
accepted0024export versus failed0025performance and no current MPS claim remain.
No strict-tail utility, physical signal efficiency, causal nonlinearity, detector
readiness or official CERN/experiment affiliation is inferred.

