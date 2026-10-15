# Data-free development streaming software foundation — Task0051

Task0051 implements the concrete software core proposed by [Task0050](development-streaming-protocol.md): descriptor transport, open-loop scheduling, finite credits/FIFO/batching, symbolic selected gather/scatter, owned artificial outputs, fixed records, accounting and supervised cleanup. Status is **`completed_software_only_development_streaming_foundation`**; readiness remains **`requires_native_characterization_and_operational_authorization`**. This is working generated-input software, not the physical 24-case campaign or its native acceptance. P4 grants zero operational work.

The [fixture configuration](../configs/streaming/development_streaming_foundation_v1.json) binds the unchanged design, actual layouts and a separate fixture envelope. The [curated summary](../results/tables/final/task0051-development-streaming-foundation-summary.json) binds sources, checks, every native attempt and remaining prerequisites. Task0050's report/config/summary pins match the supplied 20,769/43,882/23,611-byte anchors. No historical code, config, result or handoff was edited.

## Implemented boundary

New modules live only in `src/latenttrigger/streaming/`. Protocol/transport/records/supervision use the standard library. The generated backend lazily imports installed NumPy only after checking `mode="generated_memory"`. Its synthetic table, eight artificial features, arithmetic score and thresholds `[0,1,64,127]` have no scientific meaning. No data-root/model-path argument, artifact discovery, real provider, HDF codec or operational fallback is shipped. Unsupported CLI/backend modes fail before payload or numerical access. Imports and help create no mapping or child.

| Component | Concrete implementation |
| --- | --- |
| Descriptor | Little endian64B: version u16@0, zero flags u16@2, run u32@4, presentation u64@8, prefix u32@16, zero u32@20, intended/submission u64@24/32, fixture-only16B token@40, zero8B@56 |
| Slot | Descriptor64 + admission u64/sequence u64/zero48B metadata64 |
| Ring | 64slots×128 +4096control =12,288shared bytes; aligned u64 control counters start16, end152; remaining control bytes zero |
| Counts | Unsigned overflow/type errors raise; tail cannot wrap. Count≤768; actual batch m1…8; no padded or mapped scoring |
| Timing policy | Lazy `t0+floor(k*1e9/rate)`; lag>2ms missed; at most4 nonstale attempts per wake; no submit at/after H; no completion feedback |
| Queue | One producer nonblocking lock try; separate capacity/contention rejection. FIFO; 64admitted credits include ring/staged/active; oldest admission1ms timeout; final partial closure drain |
| Input grouping | Stable sort, j-th duplicate in layer j, increasing unique selections per layer, scatter every returned occurrence back to FIFO order |

The concrete mapping uses one **owned temporary file mapped shared across processes**. Initially, POSIX `SharedMemory` creation failed with EPERM in the sandbox before children/arrays. That failed attempt remains recorded. The explicit replacement uses `mmap` with shared writable access, preserving the12,288-byte layout, locking and ownership; backing storage adds12,288B within fixture storage. It is a shared region, not an evidence-file message queue, and there is no runtime fallback. This is an implementation choice compatible with Task0050, not a protocol amendment or privilege request.

Supervisor creates/unlinks; spawned producer/consumer attach/close. A common spawn mutex protects **all** slot/control accesses. Producer tail publication under that lock linearizes admission; releasing the lock makes writes visible. Dequeue frees a slot while retaining its credit. Staging and activation are separate transitions; output availability/credit release share the terminal commit. An original output copied before that commit is not yet advertised. No lock is held during ordinary service, logging, reference work or sleep. The intentional adversarial fixture holds the lock to test contention and death; it is not the core's normal path.

There is no Queue/Pipe/socket event transport, feeder, acknowledgement or result queue. Spawn's own bootstrap/sentinel descriptors and semaphore bookkeeping are runtime infrastructure, not event buffers. Four Events plus one mutex use21SemLocks; their exact OS/native backing size is **not proved** within the proposed65,536B allowance. Python3.12's tracker manages named synchronization objects; the file mapping is explicitly owned/unlinked, never registered as POSIX SharedMemory. Native console evidence contains no tracker-leak warnings; this is not a universal tracker certificate.

## Records and correctness

Producer alone writes event records; consumer alone writes batch/output records; each role owns a phase journal. Supervisor reads payload records after stopping/reaping children. Each event/batch record is512B with explicit version, integer widths, nullable timestamp validity bits, reason/status and CRC. A zero-filled absent record is not a zero timestamp; valid time0 is representable. Corruption/torn/noncanonical records invalidate accounting rather than supplying guessed values. All counters reject overflow. Parent reconciliation and timing lists are bounded by768 entries, never an unbounded duplicate ledger.

Event layout includes presentation/prefix/cycle, intended/submission/admission/rejection/observation/detection/terminal times and enqueue sequence. Batch layout uses u32 members@96…127 (count≤768), four extra operation times@128…159, u32 positions@160, u64 dequeues@192/admissions@256, eight subread starts@320/returns@384, eight u32 stage counters@448, digest16@480, flags@496, CRC@504. Dispatch/read/feature/decision/output/control/terminal timestamp fields occupy32…95. Validity bits@28 cover both timestamp groups. Three32-entry phase journals use512B records with role, phase code, service/continuous clocks, own RSS and CRC.

Every generated callback checks exact selected shape/ownership/increasing positions; neighboring or aliased returns fail. Tests cover every m, duplicate/reversed/noncontiguous positions, strict ties, all-false masks, finite checks and owned copies. Independent direct table indexing and scalar comparisons bypass gather/features/decision wrappers. Native fixture references run outside joint service and stall later consumption. Physical full-particle features, frozen-score/public-model parity, HDF handles/cache histories and the future after-drain public references remain interfaces/prerequisites, not performed work.

Projection at arbitrary cutoffs/H/after stop uses timestamped transitions:
`O=U+M+S`, `S=J+Rcapacity+Rcontention+A`,
`A=Qring+Qstaged+X+C+F+K`. Missing producer completion may be corroborated by consumer admission records; otherwise uncertainty remains. Per-stage intent/returned/failed/inflight counts and row denominators are separately projected. Output remains C if subsequent checking fails; false masks complete service, four masks are not four events. Aborted pending work is retained, never rewritten as successful drain. If startup never issued t0, H is absent and all configured offers remain unoffered.

## Supervision and measured fixture scope

Service timestamps use `perf_counter_ns`. On this host, separate suspension-inclusive supervision uses Mach continuous time; the portable alternative requires CLOCK_BOOTTIME. Injectable observations test backward clocks, monitoring failure/gaps, suspension discrepancy, deadlines and stalls. Fixture monitor target5ms, maximum gap250ms and discrepancy detector5ms are explicit; they do not certify every operational clock fault. Design operation/no-progress2s and drain5s remain separate from the illustrative100ms workload observation. Native invocation cap5s includes up to2s cleanup; the supervisor stops body work before the cleanup reserve.

Cleanup signals stop, joins/terminates/kills/reaps as necessary, then closes/unlinks owned mapping independently of the dead ring mutex or final acknowledgement. Forced termination cannot produce a normal exit. Repeated unlink is safe; reopened backing-file checks confirm absence. Failed starts and stubborn/leaked child behavior are covered. Final journal-full/close/snapshot-error guards prevent diagnostic failures from vetoing resource release; a terminal-counter overflow preflight preserves credits before mutation. Those final guards were validated deterministically after native fixtures, without adding a thirteenth attempt. Native observations bind their actual source snapshots; no claim of a fresh final-source full native matrix is made.

## Actual validation and generated activity

**82 focused tests pass**, lint and format pass. Only the new test file was collected; no shared legacy utility changed, so no historical suite/model fixture matrix was run. Initial focused stages68/73/77/80 also passed; early formatting/closure-binding lint findings were corrected. Import/help/malformed-mode audits reject operational imports/files; source audit finds no old data/model/controller imports or message-queue APIs.

| Native version / attempts | Actual result |
| --- | --- |
| v1 /1 | POSIX setup EPERM, no producer/consumer started, no generated arrays; preserved, unattempted seven scenarios not claimed passed |
| v2 /8 | All eight software fixture checks pass: normal wrap,64credit fill/32capacity rejections,32forced contention rejections, before-return/after-return/after-output deaths, mutex-owner death, failed second start |
| v3 /3 | Affected paths after output-commit/stage timestamp refinement pass: normal wrap, after-output death, mutex-owner death |
| Total /12 | 568configured artificial offers≤1536; largest128. Eleven expected checks pass, including seven intentional abnormal cases; four normal drained cases. No further native invocations performed |

Recorded validation intervals total4.656941582s (<90s); largest invocation1.510224833s (<5s). Enclosing tool-command intervals total approximately5.12s and also include unit/lint/output work; clock scopes differ and no service cost is inferred. Owned ignored diagnostics/source snapshots were1,358,584B at reporting (<16MiB; final checks may append small bounded text logs).

Across actual started fixture runs, at their respective stop cutoffs:411due offers =11unresolved +2missed +398submitted; submissions =329admitted +32capacity +37contention. Admitted =318completed +9ring +2active. There are29not-yet-due configured offers, plus the initial unstarted POSIX attempt's128configured offers. These sums describe separate fixture runs, not independent events or a rate. The two normal-wrap runs retain1 and3 contention rejections respectively, with127 and125 completions; no unfavorable observation was removed.

Generated work:264selected-read intents/319returned rows (one uncertain read intent),262feature and arithmetic-score calls/318rows each,260independent reference calls/316rows. Primary outputs1272Booleans, reference comparisons1264Booleans. Ten consumer backends constructed generated memory tables; no frozen model/public score occurred. Unit-generated numerical activity is additional and not inflated into these native counts.

Maximum sampled role lifetime RSS: supervisor25,591,808B, producer25,264,128B, consumer33,800,192B; maximum per-invocation sum84,623,360B. Shared pages/role peaks overlap; this is not unique host RAM. Failed-start zeros mean unobserved roles, not zero allocation. Maximum monitoring gap21.533208ms, cleanup32.068291ms. Native reservation/kernel sizes and global resources were not measured. No unrelated process/application/device survey occurred.

Available child summaries show event append maximum714,000ns and batch append173,625ns. Three generated event-append observations exceed the proposed50µs operational ceiling. They remain visible; neither those observations nor the lower final-normal maxima validate operational50µs/200µs limits or a distribution. Abnormal children often have no final summary. No overhead subtraction or stub-throughput claim follows.

## Allocation inventory and prerequisite decision

| Fixed owned component | Bound / interpretation |
| --- | --- |
| Shared mapping |12,288B, backing file aliases same mapping, counted once as owned memory |
| Event + batch files |2×768×512 =786,432B at design record count; fixture uses≤128each |
| Phase files |3×32×512 =49,152B |
| Output score/masks |12×768 =9216B; fixture≤1536B; no curated event payload |
| Binary storage peak including mapping |857,088B at768,194,048B at128 |
| Generated numerical buffers |Conservative34,080B: table/constructor vector/thresholds plus bounded raw/feature/score/mask copies; aliases excluded |
| Reconciliation / serialization |≤768event and batch objects each,768member entries and timing samples per family; each JSON≤65,536B. Exact Python/native bytes remain unproved |

| Prerequisite | Implemented / deterministic / native evidence | Remaining decision |
| --- | --- | --- |
| P1 | Working core,82tests; actual spawn/mapping/FIFO/failure/cleanup paths observed in11checks. Final cleanup-error guards deterministic only | Software foundation complete; no physical campaign runner |
| P2 | Exact core binary layout/cardinalities; bounded generated buffers; own-process RSS observations |21SemLocks backing, Python/native/library workspace, real HDF/cache metadata/model allocations/effective threads unresolved |
| P3 | Injectable clocks/monitoring/safety/cleanup and cutoff accounting; limited own-process observations | Operational scheduler/clock comparability, valid supervision and full-service logging overhead unvalidated; generated event ceiling exceedances retained |
| P4 | No operational capability or allowance | Separate explicit authorization required;24×768/840s study remains prospective |

The next decision is separately scoped native characterization and operational implementation/authorization after these gaps are reviewed. No Task0052, reservation or physical study follows. CPU/synthetic closure, Task0036 `unresolved_no_acquisition`, Task0034 gates, YES/YES/YES, particle192/192 consumed/canonical deferral, every historical outcome, accepted Task0024 export versus failed Task0025 performance and no current MPS claim remain. Generated correctness cannot establish strict-tail usefulness, physical signal efficiency, causal nonlinearity or detector readiness. LatentTrigger remains independent research without official CERN/experiment affiliation.

## Reproduction

These commands are examples, not another authorized run in this task. Its12native attempts are already exhausted. Focused checks are routine; a later native invocation needs a separately scoped fixture decision, not P4 or a Task0050 grant.

```sh
.venv/bin/python -m pytest -q tests/test_development_streaming_foundation.py
.venv/bin/ruff check src/latenttrigger/streaming tests/test_development_streaming_foundation.py scripts/validate_development_streaming_foundation.py
.venv/bin/ruff format --check src/latenttrigger/streaming tests/test_development_streaming_foundation.py scripts/validate_development_streaming_foundation.py
.venv/bin/python scripts/validate_development_streaming_foundation.py --help
# Future separately scoped generated smoke only; choose a NEW absolute owned directory:
.venv/bin/python scripts/validate_development_streaming_foundation.py --run-generated-fixtures --output /Users/matteosgobba/Documents/GitHub/latent-trigger/data/task0051-validation/future-generated-smoke
```

See the [Italian handoff](handoffs/0051-development-streaming-software-foundation.md) for scope, limitations and manual Git delivery.
