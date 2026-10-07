# LatentTrigger — Task 0012: Versioned Launch-Memory Policy Review and Bounded Feasibility Validation

Prompt revised on 2026-10-07 after the explicitly resumed post-reboot preflight. This replaces the earlier planning draft that also proposed lower continuing-memory floors. Task0012 has not yet been executed.

You are continuing **LatentTrigger**.

Task0009 designed the particle/set baseline; Task0010 implemented it; Task0011 added bounded recovery routing. The latest recorded suite has 296 passing synthetic tests.

The canonical particle baseline remains pending. The original launch policy requires 8GiB under the conservative `(free + inactive pages) × page_size` metric, with a 4GiB continuing floor. Task0010 failed before reader construction at 3.694794GiB. Task0011 initially measured 2.949539/2.967117/3.017624GiB and reserved no recovery attempt.

After user-reported reboot/manual preparation, the explicitly resumed Task0011 check on2026-10-07 measured **4.648499 /4.624817 /4.681854GiB** over5.005s. All readings now pass the original continuing4GiB/RSS6GiB/native512MiB limits; only the launch8GiB requirement fails. Current source/config acceptance still matches296 recorded tests. Memory revision1.4 records this result. No real particle model views or optimizer steps have been consumed.

These measurements establish failure of that host policy, not the model's actual reader/training memory requirement. The 5,228,448-byte synthetic tensor allocation also does not establish whole-process feasibility.

This is **Task0012 — Versioned Memory Policy Review and Bounded Feasibility Validation**.

This task explicitly authorizes a **separate versioned engineering review of launch admission only**, bounded reader measurements under the provisional envelope below, and at most the original unused dev optimization allowance if the reviewed policy is justified and passes readiness. Preserve the original4GiB continuing floor. It does not authorize full canonical training, model selection, or calibration.

Do not run another unchanged 8GiB preflight as the sole deliverable, and do not silently lower the original configuration. Produce actual resource evidence where the preregistered provisional profile permits it.

## 0. Inspect and preserve current state

Read applicable instructions, `docs/development.md`, and `docs/project-memory.md`; inspect Git status/index, branch/upstream, HEAD/base, recent history and prerequisites.

Read Task0009–0011 specifications, reports, handoffs, curated summaries, the Task0011 resumption prompt and dated post-reboot preflight, design/executable configs, model/reader/monitor/recovery code, source-bound acceptance, and original attempt/audit records. Verify actual commit state rather than assuming earlier tasks were committed. Task0010 and initial Task0011 commits were verified; the seven resumption documentation files may still await a separate user commit.

Preserve initial snapshots of already modified files that this task must update. Keep Task0010/0011 historical evidence and any prerequisite staging helper intact. Do not stage, commit, push, execute a staging helper, or reset a ledger automatically.

Reconcile the living memory with evidence. Its roadmap and engineering choices may evolve through explicit decisions. Keep model/data/evaluation contracts and historical task records distinct. Do not edit synced `sources/` references.

## 1. Scope: engineering policy, not model redesign

Preserve exactly:

- the 478-parameter local2/mean8 equivariant AE and its ordered initialization;
- input channels/scalers, `Nmax=384`, masks, padding, retention and preprocessing identities;
- corresponding-particle weighted residual, FP32 layers/parameters and FP64 pooling/loss/score;
- equal event weights, seed1729, Adam options/lr0.001, batch32, workers0, CPU one intra/inter-op thread and deterministic policy;
- train/selection/calibration roles, source membership and embargo;
- patience20, min_delta0, maximum200 epochs and convergence-unresolved rule;
- original continuing4GiB, workspace512MiB/RSS6GiB ceilings and all original timing limits;
- original dev membership, ≤96 optimizer steps/three passes and one scoring pass.

No attention, new features, altered objective, score correction, search, MPS fallback, precision change, batch/thread tuning or epoch extension.

The only threshold revision authorized here concerns **engineering launch-memory admission**. Continuing-memory, workspace, RSS, numerical and timing thresholds are unchanged. Keep the original measurement definition and method/thresholds reproducible as policy v1; do not claim its8GiB launch requirement passed under policy v2.

The fact that the4GiB floor passes at idle does not prove it will pass during reader verification/training. Measure that behavior; if it fails under load, record the newly demonstrated blocker. Do not lower that floor within this task.

## 2. Records and version separation

Save the actual prompt and initial handoff before substantive work:

```text
docs/prompts/0012-particle-memory-policy-review.md
docs/handoffs/0012-particle-memory-policy-review.md
```

Create:

```text
docs/particle-memory-policy-review.md
configs/resources/particle_memory_policy_v2.json
results/tables/final/task0012-particle-memory-policy-summary.json
```

The new resource profile is a versioned sidecar binding to the unchanged design/executable configuration. Preserve their historical bytes and hashes. Explicitly separate model version, mathematical/training config identity, engineering profile version/hash, code/source acceptance, and attempt provenance.

If the implementation needs schema/interface changes, document them and whitelist their exact scope. Do not weaken model validation to accept arbitrary overrides, mutate the old config in memory and report its old hash, or reuse a generic `resource_gate_passed` flag as proof of policy-v1 compliance.

Future trained artifacts/completion checks must identify the actually active resource policy and validate its relationship to the model config. Specify that contract now; no trained artifact is created in this task.

## 3. Audit memory meanings and monitor cost

Review the actual probe and reader, including store verification, mapped arrays, bounded `_batch` copies, float64 transforms, Torch tensors, optimizer state and monitor subprocesses.

Distinguish installed RAM, virtual address space, current/lifetime-peak RSS, native malloc reservation/in-use, Torch tensor allocations, clean mapped pages, dirty/private memory where measurable, and system page categories. Do not add overlapping categories or call peak RSS current RSS.

Use primary references. [Apple's Activity Monitor guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac) explains pressure using several indicators. [Apple's memory-system guide](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/ManagingMemory/Articles/AboutMemory.html) explains paging and file-backed mappings; it is archived, so do not borrow its historical page-size constants. [Apple's XNU pressure documentation](https://github.com/apple-oss-distributions/xnu/blob/main/doc/vm/memorystatus_notify.md) provides kernel context, not blanket permission to count all compressed/active pages as immediately usable RAM.

Retain the exact free+inactive byte calculation as a named reproducible metric. A v2 profile may use a lower explicit **launch** reserve; it must not rename another OS percentage to equivalent bytes. Record actual page size, raw counts, units and unavailable/permission-restricted context honestly.

Inspect whether the 50ms monitor launches costly external commands and duplicates its full raw output indefinitely. Separate probe overhead, journal volume and model/reader cost. A sampling-implementation change needs a named version, stated detection latency and synthetic interruption tests; it must not loosen deadlines or hide full-stage overhead.

Do not close unrelated applications, kill services, reboot, purge caches, delete data, generate artificial memory pressure, or request machine-wide configuration changes. User-controlled cleanup can improve readiness but is not a substitute for reviewing the policy.

## 4. Preregister the provisional launch profile before real reads

The original policy cannot measure the real reader when it refuses launch. This prompt therefore authorizes **one explicitly separate provisional engineering measurement**, with the following fixed limits. Record them and their source-derived rationale in the task specification/plan before any real store is opened:

```text
same free+inactive metric at pilot launch:     >= 4.5 GiB
same metric while pilot runs:                 >= 4 GiB
native heap/workspace reservation:            <= 512 MiB
process lifetime peak RSS:                    <= 6 GiB
dev-reader measurement phase:                 <= 60 seconds
full-store custody measurement phase:         <= 300 seconds
real optimizer steps during these phases:     0
```

The proposed4.5GiB launch requirement is **the unchanged4GiB continuing reserve plus512MiB admission headroom**, equal to the unchanged whole-native-allocation ceiling. The headroom is derived from the allocation envelope rather than rounding just below a favorable observed sample. It does not bound every mapped-file/shared/VM effect; those remain protected by live available-memory/RSS checks. Check source-level allocation bounds and reject the pilot if this envelope cannot be enforced. This is a bounded engineering choice, not proof that a future full run is safe.

Require a bounded stable preflight with three readings over at least five seconds, completing within30s, and an independent worker launch recheck. If a verified OS pressure warning/critical signal is available, it is a veto; missing pressure/current-swap telemetry must be disclosed rather than invented. Do not infer a normal state from `memory_pressure -Q` percentage alone.

Use fresh CPU workers with the unchanged thread policy, live available/RSS/native checks, parent/worker time ceilings and preserved failure records. Monitor startup, store verification and mapped-page effects. Unsupported primary accounting or a violated bound blocks reads; no loop waiting for favorable samples or automatic repeat.

This provisional measurement is **not a pass of policy v1 or the canonical dev gate**. Its sole threshold change is the explicit launch8→4.5GiB revision authorized for this bounded measurement; the continuing4GiB reserve remains intact.

## 5. Measure reader/process footprint once

If provisional readiness and source-bound synthetic checks pass, perform at most:

1. One dev-reader probe: open/verify the existing dev store and read model views for the first64 source-ordered IDs within frozen dev `train_background`, in two batches of32. Retain at most one batch; discard it after accounting. No model reconstruction/score/gradient or feature-distribution analysis.
2. One separate full-store custody probe: instantiate/verify/close the existing full processed reader, recording resource phases. Do not request any full-store model population, produce test physics summaries, or rebuild the store. Existing whole-file hashing/structural integrity remains custody work.

The64 feature-view events belong to the same first1,024 dev-train sample used by the unused dev gate. Record actual requests/read presentations and unique IDs separately. No selection/calibration population request or labels in model inputs.

Measure startup, constructor verification, mapping, bounded view preparation, release and exit. Record peak RSS and native bounds by phase; use separate fresh processes if needed to distinguish lifetime peaks. Collect current/dirty/private accounting only where genuinely available and supported. Do not infer anonymous allocation from the size of a mapped file or infer reclaimability solely from an RSS difference.

Preserve every failure and partial audit. These probes are engineering measurements, not a detector benchmark or scientific performance result. Do not retry to obtain a better footprint.

If full custody verification cannot pass the provisional profile, the full-run memory question remains unresolved even if the dev reader works. Distinguish continuing-floor, native-reservation, RSS and deadline failures, and observed mapped-page behavior. A documented verification-routing optimization may be proposed, but do not disable integrity checks, lower the4GiB floor, or reinterpret a failed measurement as success.

## 6. Select and freeze a justified policy v2

Use source-level bounds, synthetic allocation evidence and completed reader measurements to decide whether a more practical engineering profile is justified. Do not choose a threshold merely below the latest available-memory observation.

For any profile accepted for the subsequent dev feasibility gate in this task:

- continuing free+inactive reserve must remain **exactly the original4GiB**;
- launch reserve must be **at least4.5GiB**;
- launch must also cover the continuing reserve plus a justified bound on incremental allocations and a declared margin;
- keep native bound≤512MiB, RSS≤6GiB and original wall-time/cycle/step limits;
- preserve verified pressure-warning vetoes where available;
- define unavailable-metric handling, threshold equality, detection latency and interruption behavior;
- include justification, scope, old/new diff, predecessor identities and reconsideration conditions.

The4.5GiB minimum is the4GiB continuing reserve plus512MiB admission headroom. It is an admissible lower launch bound for this bounded dev study, not permission to ignore larger measured demands. Choose a higher launch requirement or reject activation if reader evidence requires it; do not lower the continuing floor.

Do not reconfigure these choices after inspecting dev optimization losses or throughput. Preserve the rejected policy-v1 evidence; an active v2 profile must say exactly which v1 host thresholds it supersedes and what remains unchanged.

If no profile satisfies the evidence/constraints, finish with a concrete resource decision and measured blocker. Do not produce another wrapper that simply repeats the old unavailable8GiB condition, or claim the baseline is ready.

## 7. One conditional dev feasibility execution

Only after policy v2 is justified, written/frozen, source-bound acceptance renewed and its stable preflight passes, authorize **one** execution of the original dev gate under that named policy.

Use a fresh disposable model; exactly first1,024 frozen dev-training IDs; batch32; at most three passes/96 steps; one same-sample no-grad score pass; whole gate≤300s. Preserve numerical/shuffle/optimizer settings, guards, tails and audit semantics.

Compare complete loading+view+training/score pass timings with the unchanged conservative extrapolation:

\[
2\left(699957\frac{\max(t_{train\ pass})}{1024}+74749\frac{t_{score\ pass}}{1024}\right)\le180\text{ s}.
\]

Do not remove factor2, report network-only timing, require loss decrease to select settings, change batches/threads/device, or substitute a smaller sample. A measured throughput failure is valuable evidence distinct from launch memory failure.

Discard dev weights. Record real memory limits, minima, resources, event presentations/unique counts, optimizer steps, timing and pass/fail. No per-event scores, reconstructions or local codes are persisted.

One failed gate ends dependent work. Do not repeat or tune to pass. Full canonical fitting/selection, restoration/reproduction, freeze and calibration are **not authorized in Task0012**, even if this gate succeeds.

## 8. Exclusive lineage and unused allowances

Preserve Task0010's consumed ledger and Task0011's unreserved route, including the dated post-reboot preflight. A v2 measurement/dev plan must use fixed Task0012 paths, bind predecessor evidence and actual policy/source/config identities, and reserve each allowed phase exclusively before dispatch.

Reject duplicate dispatch, stale acceptance, unsupported profiles, predecessor mismatch, foreign/dev membership, additional optimizer allowance, arbitrary task-name/output-directory retries and hidden-worker invocation. No `--force`, ledger deletion or reset.

Explain that Task0012 supersedes the unused Task0011 route for this new engineering study; it is not an additive model-search budget. The original ≤96 real optimizer steps remain the only dev optimization allowance. Before proceeding, verify that no manual Task0011 recovery ran since its report; if it did, reconcile actual consumption and do not grant another full allowance automatically.

Keep readiness probes, custody reads, model-view reads and optimizer steps distinct in records. Store configuration/math identity remains unchanged; active engineering policy and feasibility outcome get their own explicit identities. Future canonical authorization must refer to those records without claiming old limits passed.

## 9. Validation, artifacts, and memory

Add meaningful synthetic tests for policy version/type/hash validation, exact allowed diff, immutable original config, byte/page arithmetic, bounds/veto/unknown handling, phase guards, deadlines, measured-overhead reporting, duplicate/foreign/predecessor rejection, cumulative optimizer budget and refusal of full-fit/calibration stages.

CI remains independent of the real dataset. Run actual full tests, lint/format, dependency/import/CPU checks as relevant, renew source-bound acceptance and workspace measurement, validate links/exclusions/historical hashes, and inspect whitespace/final diff. Report actual counts and checks; hosted CI stays unverified unless observed.

Curate small phase/policy/dev summaries and timing/accounting tables where executed. Keep detailed logs, raw snapshots, acceptance, ledgers and arrays ignored. No model hash, trained artifact, final loss curve, calibrated thresholds or final background distributions are produced here.

Update `docs/project-memory.md`, handoff/index and concise README/current-report links in place. Mark v1 historical, v2 reviewed/provisional or activated for bounded dev as appropriate, and full-run policy validation/canonical training pending. Preserve scientific limitations and original failure history.

Record why the memory policy changed, what evidence supports it, its limits, monitoring cost, measured reader footprint, actual dev feasibility and new open questions. Do not turn the living memory into another raw task log or treat an engineering profile as better anomaly detection.

## 10. Outcomes and next dependency

Report one exact outcome:

- provisional launch still blocked: no new real reads;
- reader measurement failed: partial custody/view evidence preserved;
- policy reviewed but not activated: explicit unresolved resource decision;
- policy-v2 dev gate failed: measured memory/numerical/throughput blocker;
- bounded policy-v2 feasibility established: reader/probe/dev evidence passes, canonical baseline still pending.

If the last outcome holds, propose **Task0013 — Canonical Particle/Set Training and Background Validation under Resource Policy v2**, subject to live index and a fresh readiness check. It must implement explicit active-policy artifact/provenance compatibility before canonical runs and preserve every mathematical/training/convergence/calibration choice. Do not automatically execute it or require another real dev optimization replay solely to consume the same budget again.

Otherwise propose the smallest bounded next decision matching the measured blocker. Do not automatically extend horizons, tune threads/batch/device, choose a new model, or move to inference benchmarking while the canonical baseline is unresolved.

Under every outcome:

```text
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Custody verification is disclosed separately. No signal metrics/test distributions, unblinding, MPS particle experiment, exports, quantization, detector latency benchmark, TensorRT, hls4ml or trigger simulation.

## 11. Final response and manual Git commands

Return diagnosis, v1/v2/provisional-launch differences and rationale; unchanged continuing4GiB floor; measurements with correct scope/units; actual validation; real-read/step/attempt audit; dev timing/extrapolation if reached; precise completion state; living-memory changes; limitations and next decision; and actual intended versus pre-existing/ignored files.

**Git commands are mandatory and last.** Do not stage, commit or push automatically. Provide concrete status/diff, selective reviewed Task0012 staging, staged review/whitespace check, an outcome-appropriate Conventional Commit and push for the actual branch/upstream.

Handle any uncommitted Task0011 resumption records and overlapping files explicitly. Task0010/initialTask0011 are already committed when verified; do not rerun their old prerequisite staging helper. Preserve current initial snapshots where needed; never claim whole-file staging isolates a later task's edits in a file already dirty. Do not execute staging helpers automatically, overwrite them, use broad staging or include data/logs/caches/arrays/checkpoints/unrelated work.

A suitable message for the completed engineering study may be `feat: version particle baseline memory policy`; reflect the actual outcome and do not claim a finalized trained baseline.

Proceed with **Task0012 only**.
