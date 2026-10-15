# LatentTrigger — Task0051: Data-Free Development Streaming Software Foundation

You are continuing **LatentTrigger**. Perform **Task0051 only**.

## Objective and explicit scope

Implement and validate the software core of Task0050's proposed development streaming study: fixed descriptor transport, open-loop producer scheduling, finite-credit FIFO/batching, symbolic gather/scatter, fixed records, conservation and supervised lifecycle. Use **generated inputs and explicit fixture backends only**. Deliver working software with meaningful failure tests, not another design-only report or a general streaming framework.

Task0050 is `completed_design_only_development_streaming_protocol`, readiness `requires_prerequisites`. This task addresses **P1**, the new implementation and data-free correctness evidence, and the portions of **P2/P3** that can be established without operational data/models. The full 24-case physical campaign remains unimplemented/unexecuted. Do not claim to resolve actual HDF/model workspace, effective decoder/model threads, physical score parity, cache histories or workload performance through generated fixtures. **P4 remains ungranted.**

This prompt authorizes new streaming-core code, focused tests, generated in-memory arrays and model-free arithmetic stubs, bounded actual shared-memory/multiprocess fixture exercises, their own process/clock/resource observations, static inspection of relevant existing code, documentation and curated software results. Fix routine software defects and rerun affected tests within the fixture envelope without another general confirmation.

No real-data/model campaign: no production raw/HDF access, including HDF metadata opens or raw-file hashing; no membership, golden, feature, score, fingerprint or model-artifact loads; no frozen-model instantiation/public scoring, reconstruction, training, optimizer, calibration or scientific metrics; no acquisition, old timing-vector reads, synthetic trigger replay, old controller invocation, new device/MPS/runtime survey, dependency installation, operational reservation or Task0052. Do not use the Task0050 design JSON as execution authorization.

## 1. Verify and preserve the starting state

Read applicable instructions, `docs/development.md`, README, handoff index and actual living memory. Inspect Git branch, HEAD, upstream, index, tracked/untracked changes and existing environment. Preserve unrelated changes.

Planning inspection on **2026-10-15 Europe/Rome** found clean `main` tracking `origin/main`, empty index, HEAD **`3521c8f6c61e63f32ae63eb6892043b4c267d856`**, with Task0050 committed and memory **1.45**. Task0049 is committed as `42ab4458002997e1ed45ff8ecdd6aae95dd2729f`; neither task has pending changes in that snapshot. Recheck and distinguish local tracking refs from a fresh remote/push/CI verification. Preserve earlier task-time bases.

Save this actual prompt to `docs/prompts/0051-development-streaming-software-foundation.md`; create an initial Italian handoff at `docs/handoffs/0051-development-streaming-software-foundation.md` before substantive work.

Read Task0050's protocol, declarative specification, summary and handoff. Verify these planning anchors:

| Historical input | Bytes | SHA256 |
| --- | ---: | --- |
| `docs/development-streaming-protocol.md` | 20769 | `923b2222f9e23a6610586848b0e2feb804c653c73c0405bd5030a0039c30d8f1` |
| `configs/protocols/development_streaming_v1.json` | 43882 | `8ccad6fd2c006251454046dc026033834a758c04f00f3c071a501f3629dfba8f` |
| `results/tables/final/task0050-development-streaming-design-summary.json` | 23611 | `ba5208274083fbb5f1335e01cc1fb1270988c856dc7142347399b73d842ea586` |

Inspect only relevant source as text for integration conventions and safe import boundaries. Do not traverse embedded data paths or reopen old quantitative payloads. Use Task0049's synthesis for historical context if necessary; do not rerun its helper or re-reconcile 57 sources. Hash text/config/curated files used as evidence, not the raw source.

Keep Task0050 and historical code/configs/results byte-preserved. Prefer a small new `src/latenttrigger/streaming/` namespace and focused tests. Reuse pure utilities only after checking that imports cannot load data, models or old controllers. Do not repair unrelated legacy code or widen its guards.

## 2. Implement the concrete contract

The core must implement Task0050 semantics rather than merely simulate a similar queue:

- **64-byte little-endian descriptors**, the specified reserved-zero fields and 16-byte routing token; **64 bytes of slot metadata**, **64 slots**, **4096 control bytes**, **12,288 shared bytes**. Define offsets, widths, alignment, counter limits and version checks explicitly; serialize and validate the actual bytes.
- One descriptor ring and bounded synchronization/status objects; no `multiprocessing.Queue`, pipe/socket message path, feeder, per-event acknowledgements, unbounded queue or hidden result queue. Respect the proposed 65,536-byte synchronization allowance or mark the unsupported portion of P2 precisely.
- Separate supervisor, producer and consumer processes using the supported spawn context. The supervisor owns creation/unlink; children attach/close. Bounded diagnostics are evidence, not an auxiliary control/message queue.
- One producer nonblocking mutex try per submission: contention and capacity rejection remain different. Publish descriptor, admission timestamp and sequence at a defined linearization point. Never hold a shared lock during service, logging, sleep or reference work. Document memory visibility and ownership; do not rely on unsynchronized Python writes across processes.
- **64 admitted credits total**, including ring-waiting, staged and active requests. Dequeue alone does not release credit. Release once at owned output availability or an admitted terminal failure/cancellation. Distinguish slot reuse from credit reuse.
- FIFO/enqueue order, actual **m=1…8**, immediate full dispatch and **1 ms from oldest admission** for partial dispatch. Producer closure drains admitted work, including final partials, without inventing offers.

Implement intended offers lazily as `t0+floor(k*10^9/rate)`; preserve the original t0. Lag over **2 ms** becomes a miss, with at most **four** nonstale due attempts per wake; excess currently due offers become catch-up misses. No submissions at/after H, no replacement of missed/rejected offers and no service-feedback pacing. Make clocks and waits injectable for deterministic tests; use the actual core in multiprocess fixtures.

Use the exact symbolic U intervals `0..127`, `448..575`, `896..1023` and distinguish presentation identity from prefix position. Test the production workload formulas without running the 24-case campaign. Fixture runs use a separately declared shorter generated workload and a fixture routing token that can never be mistaken for a bound physical source.

Define a narrow backend interface for checked selected reads, feature construction, actual-shape scoring/strict-four decisions, owned outputs and reference checks. **Ship only a generated-memory fixture backend.** It must expose no production data-root/model-path option, discover no artifacts, and never fall back to a real provider. Any unsupported operational mode must fail before numerical/import/path access. Do not add an operational runner merely disabled by a convenience flag.

## 3. Prove grouping, ownership and records with generated data

Implement the proposed gather planner: stable-sort positions, assign each position's j-th occurrence to layer j, read each duplicate-free layer in increasing position order and scatter into owned FIFO order. Preserve every logical occurrence; no deduplication, neighboring-row return or caching substitution. A generated strict selection callback can prove the requested indices, request bounds, duplicate layering, scatter and no-alias behavior without opening HDF.

Use deterministic generated features/scores and four explicitly artificial thresholds. Test m=1…8, duplicated positions with distinct presentations, noncontiguous/reversed groups, ties rejected by `score > threshold`, all-false masks, nonfinite rejection, score/mask shape and owned copies. An independent direct indexing/comparison oracle must bypass the new gather/decision wrapper. Do not label this physical feature/model parity or independent scientific evidence. No Torch/model loader is needed; use NumPy only if useful and already installed.

Implement fixed **512-byte event and batch record** layouts, bounded capacities, nullable timestamps with explicit validity/reasons and phase/control records. Show where each process writes, how records are reconciled without races, and how H is reconstructed from timestamped linearized transitions. Account for any temporary reconciliation buffers in memory/storage; do not introduce an unbounded duplicate ledger. Select explicit integer overflow/error behavior rather than silent wraparound.

Track offered/due/unresolved/missed, submitted/undecided/rejected/admitted, ring/staged/active/completed/failed/cancelled states using Task0050's nonoverlapping identities. Verify at arbitrary cutoffs, H, normal drain and abnormal stop. Preserve uncertainty after interruption; a missing completion record cannot prove whether a side effect occurred. Output already available remains a boundary completion if a later check invalidates the case. False anomaly masks still complete service; four Booleans are not four events.

Keep per-stage intent/inflight/returned/failed counts and row denominators distinct. The generated backend must expose controlled fault points for an operation dying before return, after return and after output. Do not invent a successful final pending-zero state after failure.

Record intended offer, submission, admission/rejection, dequeue, dispatch, fixture read return, feature/decision/output and control-end timestamps, with owners. Label all read/feature/score stages synthetic. Reference/control work lies outside joint service but still stalls the consumer. Future HDF handles, cache histories, pre/post physical gates and every-realized-group public references remain specified interfaces/prerequisites, not performed work.

## 4. Implement bounded supervision and failure handling

Separate the service clock from continuous wall-time supervision. Implement injectable monitor/clock observations and bounded native smoke observations of the fixture's own processes. Do not query unrelated user processes, global application inventory or device availability to exercise monitoring.

Cover producer/consumer ready/closed/error states, deadline/drain/no-progress checks, record/storage bounds, monitor failure/gaps, clock discontinuity/suspension and process exit. The illustrative **100 ms deadline is a workload observation**, not the hard safety timeout. Keep the design's **2 s operation/no-progress**, **5 s drain**, **250 ms monitor-gap** and cleanup semantics explicit; shorter fixture-specific timeouts must be separately labeled and must not rewrite those design limits.

Cleanup must close/reap children and release/unlink only owned temporary resources within a bounded path. It must work after a child dies while holding the ring mutex: supervisor cleanup cannot depend on acquiring that mutex or receiving a final acknowledgement. Distinguish normal exits from termination; forced cleanup never turns a failed case into an accepted one. Retain failed/partial evidence and unattempted-case status. Test repeated close/unlink safely, resource-tracker behavior for the supported Python version, failed starts and leaked-child detection.

Avoid a new native build, privilege request, authorization/admission framework, experimental reservation system or copied historical controller. Add the small amount of supervision this core requires. If an existing pure clock/resource utility is suitable, reuse it without changing historical execution behavior.

## 5. Validate through two proportionate layers

**Deterministic unit/failure tests:** use fake time and explicit interleavings for scheduler boundaries, horizon races, full/partial dispatch, slot/credit conservation, lock contention, publication/dequeue/output transitions, malformed descriptors, overflow, record bounds and abort uncertainty. Include independent expected outcomes; do not test serialization solely by round-tripping the same encoder/decoder or accounting by restating implementation formulas. Exercise queue capacity with active and staged work, not just 64 ring entries.

**Bounded native generated fixtures:** use actual shared memory and spawned producer/consumer processes running the same core, with small deterministic in-memory services. Include normal completion and ring wrap/reuse; capacity/contended admission; child failure/inflight uncertainty; and stop/cleanup. Use explicit barriers/fault injection to make required interleavings observable rather than hoping the scheduler produces them. Test timing policy with fake time; native host jitter must not make functional assertions flaky.

The separate Task0051 fixture envelope is:

- At most **12 three-process fixture invocations**, including failed/aborted starts, with at most **128 artificial offers each**: **1536 offered presentations maximum** across native attempts.
- At most **5 s per invocation including cleanup**, **90 s total native-fixture wall time including setup/finalization**, and **16 MiB total owned fixture diagnostics**. Keep the core's 12,288-byte ring/64-credit bounds; use the Task0050 per-process/aggregate RSS ceilings as outer guards, never as measured future-model feasibility.
- No HDF files, real or generated, and no real/public/frozen models. Fixture arrays and arithmetic stubs are generated in memory. All persisted fixture evidence belongs to an explicitly owned ignored temporary directory.

Account for every native attempt and its own generated work, elapsed time, child exits, failures and cleanup outcome; do not manufacture an operational consumed-allowance system for reversible tests. Fix code and rerun affected checks within this envelope. If the envelope is exhausted or the host prevents a native check, preserve the actual result and remaining coverage; do not silently enlarge it or represent fakes as a native pass. Pure deterministic tests are separate and should be small enough to run routinely.

Record native observations honestly. A few generated records can expose a clock, monitor or logging failure; they cannot certify the future full producer/HDF/model workload or a production overhead distribution. Task0050's **50 μs/event** and **200 μs/batch** logging ceilings remain unvalidated for that workload unless supported by a separately scoped characterization. Do not subtract fixture overhead from future costs or infer throughput from stub speed.

Run focused new tests and relevant regression tests only for any shared pure utility actually changed; lint/format new code. Do not run broad historical suites, native matrices or fixture collectors that import/execute model/data paths. Audit imports and file-access boundaries: normal, malformed and error invocations must not open production payloads. Preserve historical hashes and check all new/changed local links.

## 6. Deliver implementation evidence and a prerequisite decision

Produce a small coherent set of streaming modules, focused tests and a fixture-only validation entrypoint, for example `scripts/validate_development_streaming_foundation.py`. It may accept only fixture settings and an explicitly owned output directory. Neither importing it nor asking for help may initialize shared memory, spawn children or load operational paths. Guard generated run activation explicitly; no fallback execution.

Add:

- `configs/streaming/development_streaming_foundation_v1.json` — versioned fixture/core configuration binding the unchanged Task0050 design, actual layouts and fixture envelope; clearly `fixture_only: true`, `operational_execution_authorized: false`, `operational_allowance_granted: false`.
- `docs/development-streaming-software-foundation.md` — concise English implementation/validation report: working behavior, ownership/concurrency argument, actual allocation inventory, tests/failures/limitations and reproduction commands.
- `results/tables/final/task0051-development-streaming-foundation-summary.json` — source/config hashes, actual implementation/version, software checks, all native attempts/generated activity, observed resource/clock facts and remaining prerequisites. No event-level payload bundle or invented physical metric.
- Actual Task0051 prompt and a self-contained Italian handoff; update README, handoff index and relevant living memory in place from the verified revision.

Keep changes proportional. If the design cannot be implemented as written within its fixed layouts/caps, document the exact counterexample and minimum proposed revision in the new report. Do not silently edit Task0050 or enlarge its envelope. Routine implementation choices that preserve semantics do not need a new protocol version or user confirmation. A material unresolved design conflict remains a prerequisite; implementing a different protocol and calling it Task0050 compliant is unacceptable.

Give a P1–P4 matrix distinguishing **implemented**, **proved by deterministic fixtures**, **observed on native generated fixtures**, **partially resolved** and **still unvalidated/ungranted**. In particular:

- P1 requires working core and the stated correctness/failure evidence, including actual multiprocess paths where claimed.
- P2 may gain exact core buffer/copy bounds and generated-process observations; real decoder/model/library workspace, cache metadata and effective numerical threads remain open.
- P3 may gain implemented timestamp/monitor/cleanup handling and limited native observations; operational scheduling, clocks/overhead under full service and valid supervision still require characterization.
- P4 grants **zero** raw/model/custody/operational work. The proposed 24×768 study and its 840 s envelope remain prospective.

Use **`completed_software_only_development_streaming_foundation`** only when the implemented foundation and claimed validation are complete. Report separate readiness **`requires_native_characterization_and_operational_authorization`**, or a more restrictive factual value if implementation/design gaps remain. Native generated fixtures are positive software/system activity, not native acceptance of the physical study. If required core validation remains incomplete, report an honest partial outcome instead of promoting the status.

Preserve Task0049 CPU/synthetic closure, Task0036 `unresolved_no_acquisition`, Task0034 gates, permanent **YES/YES/YES**, particle **192/192** consumed/canonical deferral, historical accepted/failed/software-only results, accepted Task0024 export versus failed Task0025 performance and no current MPS claim. Generated engineering correctness cannot establish strict-tail physics usefulness, physical signal efficiency, a causal nonlinearity benefit or detector readiness. No implied official CERN/experiment affiliation.

The final Italian response must explain what now works, actual test/native outcomes and generated activity, failed attempts/limitations, the remaining P2/P3/P4 gaps and the next separately scoped decision. Explicitly distinguish new generated arrays/stub calls/process observations from **zero operational** raw/model/inference/replay work; do not claim globally zero numerical or timing activity.

Recheck historical source bytes and Git. Finish with exact **manual Git review, selective staging, staged review, Conventional Commit and push commands last**, for the actual branch/upstream, excluding fixture logs/generated outputs/unrelated changes. Do not stage, commit or push. Do not launch Task0052 or the physical 24-case study.

Proceed with **Task0051 software foundation and generated fixtures only**.
