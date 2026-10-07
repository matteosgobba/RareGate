# LatentTrigger — Task 0013: Host Memory Diagnosis, Lightweight Supervision, and Conditional Bounded Feasibility

You are continuing **LatentTrigger**. Perform **Task 0013 only**.

Task0012 completed an engineering review, with final365 passing synthetic tests, but its provisional preflight measured2.583633/2.544327/2.696732GiB. All readings failed both admission4.5GiB and the unchanged4GiB continuing floor. The policy-v2 sidecar remains provisional/not activated. No real reader, custody, model view or optimizer step was reached; the original1024-event/96-step dev allowance remains unused.

The earlier post-reboot Task0011 readings were4.648499/4.624817/4.681854GiB. These are historical observations, not current readiness or evidence identifying the cause of the change. Task0012 worker peakRSS344,899,584bytes and native reservation180,011,008bytes passed their ceilings. Neither those measurements nor the5,228,448-byte synthetic tensor peak establish the full reader's footprint.

Source inspection shows that `models/particle_memory_study.py` imports NumPy, PyTorch, processed-store and training/recovery modules at module load. Its parent then starts a fresh worker which also imports that stack. Measure the added supervisor footprint; do not assume it explains the roughly2GiB change in host availability or that removing it will meet the gates.

This task authorizes one bounded, data-free accounting experiment, a lightweight supervisor, and **one conditional bounded reader/dev study** using the existing numerical policy-v2 limits and activation rule. It also authorizes preparing that same single study for user-controlled execution from an external Terminal if the in-app environment cannot meet admission. It does **not** authorize canonical training, selection, restoration/reproduction, freeze or calibration.

## 1. Inspect, preserve and record

Read applicable instructions, `docs/development.md`, and `docs/project-memory.md` before planning. Inspect status/index, branch/upstream, HEAD, actual commit history and unrelated edits. Verify Task0012's commit rather than trusting task-time memory: planning inspection found clean `main...origin/main`, local Task0012 commit `53b238a`, after Task0011 resumption `502c472`; recheck the actual state.

Read Task0009–0012 prompts, handoffs/reports/summaries, the two model configs, resource sidecar, current implementation, Task0010 ledger/failure, Task0011 preflights, Task0012 plan/workflow/reservation/audit and both362-test execution and365-test final acceptances. Resolve any later execution before assigning remaining budgets. Inspect small manifests and code without constructing stores as part of inspection.

Save the actual prompt and initial handoff before substantive changes:

```text
docs/prompts/0013-particle-host-readiness.md
docs/handoffs/0013-particle-host-readiness.md
```

Preserve all prior scientific configurations/artifacts and task-time evidence byte-for-byte. Update current project memory and indexes in place; historical handoffs receive only explicit dated corrections/confirmations if necessary. Do not edit synced `sources/`, run old staging helpers, reset ledgers, or stage/commit/push automatically.

## 2. Keep the scientific and resource contracts

Preserve the478-parameter shared4→16→8 encoder/local8→2/mean8 context/shared10→16→4 decoder, initialization order, frozen features/scalers/Nmax384/masks, canonical weighted corresponding-particle objective, FP32 network and FP64 pooling/residual/reduction semantics, equal event weighting, deterministic CPU seed1729, exact Adam settings, batch32, workers0 and one intra/inter-op thread. Preserve frozen role/membership guards and test embargo. No new architecture/features, tuning, MPS fallback, precision/batch/thread/epoch changes.

Retain these exact engineering limits:

| Contract | Required value |
| --- | --- |
| Metric | `(free_pages + inactive_pages) × actual_page_size` |
| Provisional launch | ≥4,831,838,208bytes =4.5GiB |
| Continuing availability | ≥4,294,967,296bytes =4GiB |
| Whole native malloc reservation | ≤536,870,912bytes =512MiB |
| Worker lifetime peakRSS | ≤6,442,450,944bytes =6GiB |
| Stable readiness | 3 readings spanning≥5s, completed≤30s |
| Dev reader | ≤60s, exactly first64 frozen dev-train IDs, two batches32, zero updates |
| Full-store custody | ≤300s, verification/mapping/close only, zero population requests/updates |
| Original dev feasibility | first1024 frozen dev-train IDs, ≤3passes/96steps, one same-sample score pass, ≤300s |

All startup/import/verification/view/monitor costs belong inside the corresponding stage deadlines. Retain original50ms watcher,2s external probe timeout, per-batch checks and signal/parent enforcement. Verified warning/critical pressure is a veto; unavailable pressure remains explicitly unknown under the existing rule. Unknown primary accounting fails closed.

Do not change `configs/resources/particle_memory_policy_v2.json` or either model config. V1's8GiB launch remains historical and is not claimed passed. Carry the existing provisional numerical envelope into this explicitly authorized Task0013 study through a separate execution manifest binding its unchanged profile hash, this prompt, actual source acceptance and lineage. The sidecar's Task0012 scope is historical: it does not by itself authorize another execution. Task0013 authorization and receipt must identify this bounded successor without granting canonical scope or weakening exact policy validation.

## 3. One data-free accounting experiment

Preregister a fixed experiment before measuring. Run it once after implementation and final synthetic acceptance, with an overall≤180s deadline and each diagnostic configuration≤30s including imports. Use three configurations in a fixed order:

1. A standard-library-only controller/probe baseline.
2. The legacy supervisor shape: a parent importing the actual Task0012 runtime stack and a fresh child importing the same worker stack, held alive together only for measurement.
3. The proposed lightweight supervisor plus a fully imported/prepared worker. This worker must include the imports and CPU setup that the real reader worker will require.

For each configuration collect3 timestamped raw host snapshots over≥5s, with per-process currentRSS where supported, lifetime peakRSS, native reserved/in-use and import/startup timings. Have each owned process report its own measurements, using supported existing Darwin bindings where possible. Record PID/parent relationships and loaded heavy-module names. Diagnostic workers must never call a study/run entry point, instantiate a store/model/optimizer, score anything, or open dataset arrays/raw files. Reading small configs/manifests and acceptance/lineage records is allowed.

Record installed RAM, actual page size, raw free/inactive and contextual wired/active/compressed/file-backed counters if available. Obtain pressure/current swap once through supported read-only queries, retaining permission failures. At most one optional process inventory may retain PID, parentPID, executable basename andRSS for the ten largest processes; exclude command arguments, environments, app/document/window content. Do not escalate merely to obtain missing telemetry.

Distinguish measured process footprint from host changes between configurations. Shared pages make summedRSS unsuitable as unique physical memory. Host variation, import caches and external activity limit causal attribution; report these limits and do not turn a favorable sample into a readiness result. Missing measurements remain missing.

Use primary references for platform interpretations: [Apple Activity Monitor](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac), [Apple's archived VM guide](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/ManagingMemory/Articles/AboutMemory.html), and the XNU sources already cited in Task0012. Do not borrow historical page-size constants or count all active/compressed pages as available. Pressure percentages and virtual address size do not replace the fixed metric.

These diagnostic configurations are read-only accounting, not reader admission or model resource acceptance. They may record low availability without opening data. No repeated experiments, polling until a pass, artificial allocations/pressure, cache purging, service/application termination, reboot or machine-wide configuration changes. Terminate only task-owned diagnostic children for cleanup/deadline enforcement.

## 4. Lightweight supervision and external execution

Implement a narrow standard-library-only controller. Neither its module imports nor its live parent process may load NumPy/PyTorch/pandas/h5py or the heavy project stack. Perform small-file JSON/hash/provenance checks without importing those libraries. Real scientific validators, reader and model code stay in fresh workers, and every worker independently verifies current acceptance/config/profile/prompt/reservation before data access.

Reuse existing reader, dev, audit and monitor functions where practical; avoid a new general workflow framework or changing old scientific code to accommodate the launcher. New launcher/helpers must be included in source acceptance; the current `source_hashes()` covers `src/latenttrigger/**/*.py` and top-level test files, so account explicitly for any executable placed elsewhere. Changes to shared helpers need narrow rationale and parity checks. Keep prior plans and acceptance bytes intact.

The controller must preserve exclusive reservations before dispatch, bounded logs, fixed phase order, import-inclusive parent deadlines, interruption/inflight accounting and partial failure evidence. A bootstrap that avoids duplicate framework imports is an engineering improvement, not a changed resource threshold or proof that the host is sufficient.

Provide one reviewed external-Terminal command using the existing environment and fixed repository paths. It must work without Codex being open, require no reinstall/new packages/sudo, independently validate source acceptance, and perform the same guarded conditional phases. Do not open Terminal, close Codex or execute this external route automatically to change the user's app state.

## 5. One exclusive conditional study, shared by automatic and manual execution

Create a fixed Task0013 successor plan/output, bound to predecessor file identities, both Task0012 acceptances, the unchanged v2 profile and mathematical configs, this prompt and fresh source acceptance. Verify that Task0012 stopped at its failed read-only pilot, with no reader/dev reservation or consumption. Refuse any unexpected later consumption; reconcile it before proceeding. The unused Task0011 route and consumed Task0012 pilot stay superseded/preserved.

The data-free diagnostic does not reserve a real-study slot. After configuration3 completes, if all its fully prepared-worker observations satisfy the numerical admission/native/RSS/pressure checks, this prompt authorizes automatically invoking the fixed Task0013 bounded study **once**. The study must still perform its own fresh3-reading readiness and worker launch rechecks; diagnostic observations alone never unlock data.

If diagnostic availability is inadequate/unknown, do not invoke that study in-app. Leave its one slot unreserved and deliver the exact external command, clearly marked pending. The user may choose to run it after closing their own unnecessary workloads, including Codex if desired. This prompt authorizes that one external execution; it shares the same exclusive slot as automatic execution. It is not a second allowance. If automatic execution reserved or dispatched the study, do not present the external command as available for another attempt.

Official study order:

1. Exclusive reservation and stable fresh launch readiness≤30s; failure consumes this study invocation and stops all dependent work.
2. Fresh guarded dev-reader measurement: unchanged verified constructor, first64 source-ordered IDs from the original1024 sample, two batches32, retain at most one batch, no network/score/gradient/update.
3. Separate fresh full-store custody worker: unchanged whole-file/structural verification and read-only mappings, then close; no full population model/evaluation request.
4. Evaluate the unchanged Task0012 activation rule using complete reader receipts: `max(reader_native_peak − its_startup_reserved,0) + 4 × synthetic_tensor_peak + 128MiB ≤512MiB`, exact identities, zero steps and all live limits. Preserve limitations of this empirical bound and mapped effects. Failure means reviewed/provisional/not activated.
5. If activated for bounded dev, fresh dev readiness and **one** unchanged disposable original dev gate. Keep the conservative extrapolation `2*(699957*max_train_pass_seconds/1024 + 74749*score_pass_seconds/1024) ≤180s`, including view preparation.

The dev budget is cumulative across the lineage:≤1024 unique events,≤3training passes/96 started optimizer steps and one same-sample scoring pass. Reader64 are a subset of those same IDs; custody is accounted separately. Persist started/completed/inflight steps before/after mutation. Discard dev weights. Do not persist individual scores, tune to loss/timing, introduce additional validation populations, reset failures or create alternate output directories to retry.

No canonical run, full selection/calibration, trained artifact/hash, thresholds, exports or final discrimination results. Custody verification may hash/structurally check the full store under existing rules; it does not authorize model/evaluation access to `test_background` or `test_signal`.

## 6. Validation and evidence

Add meaningful synthetic coverage for the lightweight import contract in a fresh process, exact byte arithmetic/profile binding, source acceptance including new code, fixed lineage/phase/budget rules, worker rechecks, missing telemetry, timeout/partial audit behavior, duplicate invocation and refusal of fit/calibration/test access. Show unchanged reader/dev math and optimizer behavior where shared code changes. Keep ordinary CI synthetic and platform-independent.

Run appropriate existing tests, lint/format, dependency/CPU smoke and required checks. Generate actual source-bound acceptance after final executable changes, preserving earlier records. Do not invent counts or rerun real stages after source edits. Freeze executable code before the sole diagnostic/study; later fixes require renewed synthetic acceptance and must not silently reuse consumed real phases. Review history preservation, links, ignored/local outputs and whitespace.

Create:

```text
docs/particle-host-readiness.md
results/tables/final/task0013-particle-host-readiness-summary.json
```

Report the per-configuration host/process measurements, supervisor improvement or inconclusive attribution, actually dispatched/reserved phases, stage minima/peaks/times, custody versus population counts, remaining budget, policy status and manual slot status. If the study is deferred, the curated summary records pending execution; the eventual manual receipt remains separate and must be reconciled by the next task without replaying the study.

Update `docs/project-memory.md` in place, README and the handoff index. Record durable rationale, observations and current next dependency. Memory remains evolutionary; distinguish proposed, implemented and measured findings.

Choose the next step from evidence:

- **Host still below admission:** lightweight route delivered, bounded study pending/unreserved or official preflight failed; provide one practical user-controlled preparation/Terminal path if the slot remains available. Do not propose another identical in-app preflight as a new implementation task or infer model infeasibility.
- **Reader/live floor/native/RSS failure:** report the measured blocker and propose only the engineering decision needed to address it, without changing4GiB here.
- **Dev numerical/throughput failure:** report its exact failure; no tuning or full training.
- **Bounded feasibility established:** propose Task0014 for actual-policy artifact/completion compatibility and canonical background training under an explicitly versioned full-run authorization. Reader/dev acceptance alone does not grant full-run scope. Do not repeat consumed dev optimization merely because the task number changes.

State the embargo explicitly:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## 7. Required final Git section — last section of the response

Do not automatically stage, commit or push. End with exact commands for actual repository/branch/upstream: status, working/index diff, selective `git add --` of only the actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push. Exclude data, diagnostic logs, acceptance/ledger/receipts, snapshots and generated large artifacts. Preserve unrelated work and do not include historical files just because they were inspected. Confirm pending prerequisites from actual Git state; never replay the old Task0010 snapshot staging helper.

Proceed with **Task0013 only**.
