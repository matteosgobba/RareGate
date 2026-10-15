# LatentTrigger — Task0050: Development Streaming, Cache and Transport Protocol Design

You are continuing **LatentTrigger**. Perform **Task0050 only**.

## Objective and authorization

Turn Task0049's recommended next question into a concrete, reviewable **design-only development streaming protocol**. The native CPU and synthetic-trigger study is closed within its declared scope. Preserve that closure and its frozen scientific baseline.

The question is: **What bounded physical development experiment could establish the behavior of an actual producer, finite queue, selected HDF reads, frozen features, CPU scoring and four decisions, under explicitly controlled input reuse and cache histories?** Design an experiment capable of returning a negative or inconclusive result.

This prompt authorizes reading existing documentation, curated aggregates, configurations and a small amount of source as text; metadata hashing and static consistency checks; prospective resource/accounting arithmetic; and writing the protocol, its declarative specification and handoff. Continue autonomously within this reversible scope. Finish a specific recommended design, rather than a menu of unresolved options.

**No operational implementation or execution is authorized.** Do not create or modify a streaming runner, provider, controller, transport, benchmark or native admission system. Do not invoke existing operational workflows. No raw/HDF access, including metadata opens or raw-file hashing; no membership/golden/feature/score/fingerprint arrays; no model artifacts, model imports or instantiation, inference, reconstruction, fitting, optimization, calibration, scientific metrics or acquisition. Do not load timing vectors, generate arrivals/traces, replay queues, install dependencies, probe current hardware/runtime availability or reserve any allowance. Do not launch Task0051.

## 1. Establish the actual baseline

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, README and handoff index; inspect branch, HEAD, upstream, index and tracked/untracked changes.

Planning inspection on **2026-10-15, Europe/Rome** found:

- `main` tracking `origin/main`, HEAD `d26d64425da9b738c6d92fd3d852122ca36d92b0`.
- Task0048 committed; Task0049 artifacts present but uncommitted. README, memory and handoff index already contain Task0049 edits.
- Memory revision **1.44** and Task0049 status `completed_curated_cpu_trigger_synthesis`.

Recheck these facts. Completion, commitment and push are separate states. Do not require a clean tree merely because these known Task0049 changes remain. Preserve and record pre-existing changes, including their baseline contents for shared documents. Do not attribute them to Task0050 or stage them automatically. If Task0049 has since been committed, record the actual new base without rewriting historical task-time bases.

Save this actual prompt to `docs/prompts/0050-development-streaming-protocol-design.md` and create an initial `docs/handoffs/0050-development-streaming-protocol-design.md` before substantive work. Change historical artifacts only through an explicit later correction record, never by silently editing them.

## 2. Use existing evidence without reopening the study

Start with these **18 evidence files**, bound by actual repository-relative path, size and SHA256 in the design summary:

1. `docs/cpu-trigger-study-synthesis.md`
2. `docs/cpu-trigger-study-decision-brief.md`
3. `docs/handoffs/0049-cpu-trigger-study-synthesis.md`
4. `configs/reporting/cpu_trigger_synthesis_v1.json`
5. `results/tables/final/task0049-cpu-trigger-evidence-registry.csv`
6. `results/tables/final/task0049-cpu-service-boundaries.csv`
7. `results/tables/final/task0049-replay-comparability.csv`
8. `results/tables/final/task0049-refined-replay-conclusions.csv`
9. `results/tables/final/task0049-cpu-trigger-claims.csv`
10. `results/tables/final/task0049-cpu-trigger-synthesis-summary.json`
11. `docs/development-raw-feature-measurement.md`
12. `docs/development-raw-decision-campaign-v2.md`
13. `docs/targeted-partial-raw-decision-measurement.md`
14. `configs/benchmarks/development_raw_decision_v2.json`
15. `configs/benchmarks/development_targeted_raw_decision_v1.json`
16. `docs/preprocessing-contract.md`
17. `docs/controlled-follow-up-protocol.md`
18. `docs/confirmation-source-feasibility.md`

If necessary to resolve implementation facts, read only these additional files **as source text**, recording which were actually read:

- `src/latenttrigger/benchmarks/development_raw_adapter.py`
- `src/latenttrigger/benchmarks/development_raw_membership.py`
- `src/latenttrigger/benchmarks/development_decision_provider.py`
- `src/latenttrigger/benchmarks/development_decision_measure.py`
- `src/latenttrigger/benchmarks/targeted_raw_service.py`

Use a **4 MiB total unique-byte ceiling** for this evidence set, separate from bootstrap instructions/living context. Do not expand through embedded manifests, linked payloads or operational paths. Task0049's 57-source registry describes historical provenance; it does not require another 57-file reconciliation. Do not rerun its synthesis helper. In particular, do not parse the old Task0046 summary with embedded timing vectors. Check links by existence without opening their payloads.

Copy only the few historical facts needed to motivate the design. Keep provenance separate from fresh verification and proposals separate from measurements. If static evidence cannot resolve a detail, record it as a concrete prerequisite for future implementation; do not resolve it by executing the old path.

## 3. Select one small workload and a feasible boundary

Recommend one minimal primary experiment, with an explicit rationale and a short table of rejected/deferred alternatives. Avoid multiplying every batch, arrival, cache, transport and timeout option into another large grid.

Use frozen PCA and compact AE v2 on development background only. Begin with **nominal B8** as the primary batching case: all its occupancies have historical lookup support, making it a useful setting for studying a new physical boundary. That support does not validate streaming. Add a B1 reference or another nominal B within B1/8/32/128 only if it answers an indispensable separate question; explain the extra cost. No candidate or policy selection based on new physics outcomes.

Keep the proposed raw-row universe within the **384 historically selected rows**, represented symbolically as positions `0..127`, `448..575`, `896..1023` of the same sorted 1,024-ID development prefix from the original 6,999-ID source. Verify this positional description against the method reports without loading IDs. Do not enumerate real event IDs. The 1,024 approved/golden rows and 384 historically requested raw rows are distinct scopes. Any expansion, altered grouping or new sequence requires its own future implementation checks and authorization; old permissions do not transfer.

Specify exact finite presentation counts, order and wrap/reuse rules, warm-up/control work, repetitions, arrival construction, batching timeout, queue capacity and drain rule. Start from the declared **500 / 2,500 / 5,000 events/s** questions. They are development offered-load settings, not physical LHC rates. Prefer a compact periodic primary design; retain another arrival family only with a clear need. Specify the algorithm now without generating a trace. A repeated row receives a unique presentation identity and never becomes a new independent source event.

Resolve the transport semantics explicitly. The existing source is a filtered HDF dataset, not a ready-made stream of encoded event messages. A practical first design may transport **approved row descriptors** to a consumer that performs the selected HDF read and decode. Its ingress is a software request boundary before HDF processing; it is not ingress of physical event bytes. Explain exactly what traverses the transport, its format/size/ownership and which process opens HDF.

Contrast that with transport of already decoded arrays or independently encoded payloads. Those have different boundaries and preprocessing histories. Do not invent an existing encoded-event representation, silently replace the HDF decoder, or describe a descriptor/array queue as a detector link. Select one feasible local transport for the recommended protocol. Defer a payload-transport study explicitly if the present contracts cannot support it.

## 4. Specify timing, queueing and input history

Provide one readable pipeline diagram and a timestamp/boundary table. Define, at least:

- Intended offer time, actual producer submission, queue admission/rejection and consumer dequeue.
- Selected HDF read start/return, feature completion, actual-shape scoring/four-decision completion, and owned output availability.
- Startup/setup, model/source loading, identity checks, parity/reference work, warm-up, arrival horizon, drain and supervised cleanup.

Specify the monotonic clock and same-host cross-process comparability assumptions, timestamp ownership, units, missing records and maximum logging overhead to be characterized later. Report producer scheduling lag separately. Include latency from intended offer time so a delayed producer cannot conceal overload by shifting the starting timestamp. Exact clock resolution and actual scheduler behavior remain unmeasured.

Declare open-loop versus feedback-controlled arrivals. For the primary offered-load question, the producer must not silently slow arrivals to match consumer completion. Define late producer offers, burst catch-up, rejection/backpressure, capacity including in-flight work, FIFO/tie semantics, actual m at dispatch, oldest-event timeout and final partial drain. Distinguish requested from achieved offered rate. Queues and transport buffers must all be bounded; hidden pipe buffering must be accounted for.

Use actual raw-to-decision work for actual m in the proposed future experiment. No sparse-anchor mapping, interpolation, padded/full-B charge substitution or imported timing-vector bill. If a comparison path changes process placement, scheduling, packing or ownership, describe the whole intervention. Do not label its time difference pure transport overhead unless the proposed matched comparison can isolate that quantity.

Prescribe source order, HDF handle/cache settings and lifetime, prior custody hashing, golden/reference reads, prefetch and input reuse for every proposed history. Distinguish application-cache reset, reopened HDF handle, first pass and repeated pass. **None establishes a cold OS/page cache.** No purge, reboot, global cache reset or user-app closure is part of this design. If a setup/parity operation warms the target inputs, disclose it and place it in the history. Mechanical neighboring-chunk decode never permits returning or analyzing nonapproved rows. Chunk geometry is not a measured I/O/cache-miss count.

## 5. Make accounting and acceptance falsifiable

Define the event and batch record schemas, with explicit denominators and units. At the offered, submitted, admitted, rejected/dropped, queued, active, completed and failed boundaries, give nonoverlapping conservation identities at the arrival horizon and after drain. Account for producer-missed offers and every bounded queue separately. Four decision masks are outputs, not four completed events; a false anomaly decision is still a completed service.

Specify end-to-end offered-time latency, producer lag, queue wait and directly measured joint service duration; count deadline misses, overflow and pending separately. Use **100 ms only as an illustrative development deadline**, with an explicit prospective decision about whether overload is an observed result or a stop condition. Define any separate hard safety/liveness timeout numerically. Keep completed-survivor quantiles conditional and report their sample counts. Do not impute latency to dropped events or average quantiles across runs. No production p99 or independent-event inference from repeated finite rows.

Future numerical checks must cover frozen feature/scaler/model/calibration identities, full-particle feature semantics, actual batch shape, strict `score > threshold` with ties rejected, and owned four-mask output. Specify how an independent same-shaped reference would check every distinct planned grouping/shape or justify narrower coverage. Old small-window parity and the scientific B4096 reference are not blanket streaming certification. Do not loosen historical tolerances or execute a reference now.

Separate three outcomes:

1. **Valid experiment:** complete accounting, valid identities/parity, bounded resources and records, normal supervised lifecycle.
2. **Workload result:** achieved delivery, latency/loss/deadline behavior, including overload or no transport benefit.
3. **Scientific usefulness:** still unresolved by this engineering experiment.

Specify hard stops for identity/parity/nonfinite failures, unexpected population access, memory/storage/time ceilings, lost accounting, process/cleanup failure and monitoring failure. Distinguish a validity failure from a valid negative performance result. Preserve slow/unfavorable observations and incomplete-run status; no automatic retry or silent replacement of a failed run.

## 6. Derive a prospective resource envelope

Give one compact case matrix and a resource table with numeric proposed ceilings and derivations. Count all proposed runs and row presentations, including setup, parity, warm-up, repetitions and maximum drain/control work. Separate unique raw IDs, repeated presentations, HDF requests, feature rows, candidate calls, score rows and four Boolean decisions per row.

Bound producer/consumer buffers, native transport storage, active and queued requests, selected raw materialization, feature/model temporaries, references, output retention, logs, process/native memory, storage, per-run duration, whole-study duration and cleanup. Include framing/copies and variable-sized buffers or identify a prerequisite that prevents a defensible bound. Do not double-count aliases as owned allocations or omit library/native workspace. Full raw loading and particle-view materialization are excluded.

Historical means may motivate a planning estimate only with their original scope and an explicit assumption/safety factor. They are not a service bound or a budget grant. State uncertainty in library workspace, decoder threads, OS cache and host contention. Record historical host context; current hardware/resources were not probed. The future native CPU host and effective thread settings must be verified in a separately scoped implementation/execution task.

Conclude whether the protocol is **specified for implementation review** or **requires named prerequisites**. A coherent infeasibility finding is acceptable. Do not invent feasible runtime or memory measurements, waive old constraints, or create new operational authorization machinery merely to finish the document.

## 7. Deliver a usable protocol, with no runner

Create:

- `docs/development-streaming-protocol.md` — readable English protocol, roughly 1,800–2,800 words plus tables/references, leading with the chosen question, recommended design and claim boundary.
- `configs/protocols/development_streaming_v1.json` — a declarative design specification containing the exact case matrix, algorithms, boundaries, resource arithmetic, criteria and prerequisites. Mark `design_only: true`, `execution_authorized: false`, and `operational_allowance_granted: false`. It must not be loadable as an old campaign grant by implication.
- `results/tables/final/task0050-development-streaming-design-summary.json` — actual design outcome, evidence path/size/hash manifest, copied facts versus proposed values/derived bounds, validation performed and remaining prerequisites. Include no invented physical result or timing vector.
- Actual Task0050 prompt and a self-contained **Italian handoff**, explaining why this experiment would address the missing evidence, what it could establish, what remains unmeasured and the next separate decision.

Keep matrix/resource tables consistent with the declarative specification; avoid redundant ledgers and a general framework. Do not add runtime modules, tests that import model code, benchmark fixtures or new figures. A small static diagram in the protocol is enough. Use the existing environment for bounded metadata checks without dependency installation.

Verify JSON syntax, unique case IDs, finite values/units, case-count and worst-case accounting arithmetic, complete numeric ceilings or explicit blocking prerequisites, document/spec agreement, links and unchanged historical evidence hashes. Run relevant static checks only for any genuinely necessary small validation code; no helper is required. Do not run full historical suites or native fixture matrices for a document-only task. Clearly mark proposed behavior as unimplemented and all physical validation as unperformed.

## 8. Preserve closure and finish the handoff

Use status **`completed_design_only_development_streaming_protocol`** when the design and static checks are complete, with a separate readiness field `specified_for_implementation_review` or `requires_prerequisites`. This is not native acceptance, implementation completion or proof of feasibility. A specific prerequisite may remain without making the design itself falsely incomplete or operationally ready.

Update README, handoff index and relevant memory sections **in place**, advancing from the actual verified revision. Preserve CPU/synthetic phase closure; record Task0050 as a new design outcome and the next separately scoped implementation decision. Do not mark streaming, transport or cache performance measured.

Maintain unchanged: Task0036 `unresolved_no_acquisition`; Task0034 scientific gates; permanent **YES/YES/YES** exposure; particle **192/192** consumed and canonical deferral; all historical accepted/failed/software-only outcomes; accepted Task0024 ONNX export versus failed Task0025 performance campaign; no current MPS claim. Engineering results cannot establish strict-tail anomaly usefulness, physical signal efficiency, a causal nonlinearity benefit or detector readiness. LatentTrigger remains independent research without implied official CERN/experiment affiliation.

The final Italian response must state the chosen design, exact proposed workload/envelope, reasons for the transport/cache interpretation, static checks actually performed, unresolved prerequisites and the fact that no operational data/model/streaming work occurred. Historical positive work remains historical; do not make a global-zero claim.

Recheck branch/index/diff and preserve the starting evidence bytes. Finish with **manual Git instructions last**: exact review, selective staging, staged review, Conventional Commit and push for the actual branch/upstream. Do not stage, commit or push. Account explicitly for any pre-existing Task0049 changes; do not present a standalone Task0050 commit as independent of uncommitted Task0049 files or silently stage those files. If necessary, provide hunk-level manual staging for shared documents and explain the dependency. No automatic Task0051, native reservation, implementation or measurement follows.

Proceed with **Task0050 design only**.
