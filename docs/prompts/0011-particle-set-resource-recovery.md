# LatentTrigger — Task 0011: Bounded Particle/Set Resource-Gate Recovery and Background Validation

You are continuing **LatentTrigger**.

Task 0009 designed the 478-parameter particle/set autoencoder. Task 0010 implemented it and its staged orchestration. The recorded synthetic suite has 247 passing tests, and synthetic batch32/full384 tensor allocation peaked at 5,228,448 bytes.

The **canonical particle baseline remains pending**. Task 0010's only real workflow launch failed before processed-store construction:

```text
available memory: 3,967,254,528 bytes / 3.694794 GiB
required launch minimum: 8,589,934,592 bytes / 8 GiB
real population requests: 0
real events: 0
real optimizer steps: 0
```

No real dev timings, canonical training, restoration, reproduction, freeze, calibration, or particle score distributions exist. Do not infer model infeasibility or convergence failure from this host launch result.

This is **Task 0011 — Bounded Particle/Set Resource-Gate Recovery and Background Validation**.

This prompt explicitly authorizes **one new bounded recovery attempt**, but only after the original launch condition is verified. Preserve the failed Task 0010 attempt and every original scientific/resource limit.

## 0. Inspect evidence, instructions, and current state

Before changes, read applicable instructions, `docs/development.md`, and the latest `docs/project-memory.md`. Inspect Git status, index, branch/upstream, HEAD/base, recent history, and unrelated changes.

Verify Task 0010's actual commit state rather than assuming it was committed. Preserve pre-existing changes and snapshot initial content hashes for overlapping files. Do not stage or commit prerequisites automatically.

Read:

- Task 0009 design report/JSON/budget;
- Task 0010 prompt, handoff, implementation report, and curated gate summary;
- executable particle configuration;
- processed-reader, particle-model, resource-monitor, orchestration, and acceptance tests;
- frozen preprocessing/evaluation contracts;
- ignored Task 0010 attempt ledger, launch audit, workflow failure, and source-bound acceptance records.

Verify the zero-event/zero-step failure and identify the final source-bound acceptance record; Task 0010 recorded a timing-boundary correction after its launch attempt. Preserve both original and final acceptance evidence. Do not reuse a stale acceptance file after code changes.

The memory is evolutionary and must be reconciled with verified evidence. Maintain it alongside existing prompt/handoff/index records; never edit synced `sources/` files or erase historical failures.

## 1. Scope and immutable contracts

Keep the selected design exactly:

```text
shared encoder: 4 → 16 ReLU → 8 ReLU
local bottleneck: 8 → 2 linear
context: eight-value masked mean of encoder h
shared decoder: [local2, context8] → 16 ReLU → 4 linear
parameters: 478 / 1,912 FP32 bytes
latent capacity: 2*n_retained + 8
```

Keep inputs, masks, frozen transformations, corresponding-particle objective, score, FP32/FP64 policy, initialization/order, seed1729, Adam options/lr, batch32, CPU/thread/determinism policy, patience20, maximum200 epochs, and all calibration conventions unchanged.

The numerical sources are the unchanged Task 0009 design and Task 0010 executable configuration. Verify their hashes and exact mapping. Do not overwrite them, reinterpret a configuration flag, or silently alter artifact validation.

Keep **all** original ceilings: launch available≥8GiB, continuing available≥4GiB, process RSS≤6GiB, native workspace bound≤512MiB, dev≤300s/1,024 events/three passes/96 steps plus one score pass, predicted/actual full cycle≤180s, fit≤36,000s/run, postfit≤3,600s/run, and two-run canonical total≤79,200s.

This task authorizes recovery routing and execution within those contracts, not a resource-policy relaxation, architectural change, device switch, or inference benchmark.

## 2. Read-only host diagnosis before another attempt

Inspect the implemented memory probe and collect a small bounded host diagnostic without opening a processed reader or consuming dev optimizer steps.

Use the **same operational definition** as Task 0010:

```text
available_bytes = (Darwin free_pages + inactive_pages) * actual_page_size
```

Record method, page size, raw counts, derived bytes/GiB, process RSS, native heap reservation, and available contextual memory-pressure/swap/compression information. Mark unavailable/permission-restricted fields honestly. Do not equate cumulative swap counters with current swap use or add overlapping categories together.

This conservative operational metric is not the entire macOS memory-pressure assessment. Apple's [Activity Monitor memory guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac) describes pressure using free memory, swap rate, wired memory, and cached files. Additional diagnostics explain the host state; they do not replace the frozen launch test or authorize counting compressed/active pages as available.

Distinguish installed RAM, free/inactive pages, process RSS, native heap, and tensor allocation. The synthetic 4.986MiB tensor measurement does not establish the missing real-reader/process footprint or justify lowering 8GiB.

Do not kill/quit unrelated applications, stop services, reboot, purge caches, delete data, or run memory-pressure generators. The user controls any manual host cleanup. Do not inspect unrelated app content or claim that an app was closed when it was not.

If below the threshold, provide a concrete manual preparation/run procedure: let the user close their chosen unnecessary workloads, then recheck through the same preflight. Do not reserve a real recovery attempt while the preflight is already known to fail.

## 3. Stable preflight and bounded decision

Implement or expose a safe **preflight-only** entry point that performs no store construction, population requests, network optimization, or ledger reset.

Take three readings spanning at least five seconds and completing within 30 seconds in the fresh CPU worker environment. Require all three readings to satisfy the unchanged launch/continuing-memory, RSS, and workspace tests. Record timestamps and all readings; do not select only the favorable one.

Preflight sampling is a read-only readiness check, not a dev attempt. Do not poll indefinitely, repeatedly reopen workers to fish for a passing sample, or create an automation. If readings fail or accounting is unavailable, stop dependent stages and deliver the diagnosis plus the exact prepared preflight/run commands.

If the host cannot meet the original requirement, record **environment still blocks launch**, with zero new real-data access. Propose a separate versioned engineering-policy review if warranted; do not make that change here or automatically consume another task number.

Even after stable preflight, the actual new worker must independently pass the original launch check. Host memory may change between observations. A failed new worker counts as the one authorized recovery attempt; do not repeat it automatically.

## 4. Recovery plan and attempt accounting

Create a small explicit recovery plan/record before a real recovery launch, binding:

- Task0011 scope and the one-attempt authorization in this prompt;
- original Task0010 failure/ledger/audit identities;
- verified original zero real-event/step consumption;
- unchanged executable/design identities;
- current source-bound synthetic acceptance;
- stable-preflight results;
- one fixed new output directory and one exclusive Task0011 attempt ledger;
- unchanged gate order and remaining limits.

The original dev optimization allowance is wholly unused. The new attempt may consume at most those original 1,024 unique dev-train events, 96 steps/three passes, and one scoring pass. It does not receive an additional model-selection budget.

Implement a narrow supported recovery entry point if needed. The existing Task0010 default must still refuse its consumed attempt ledger. Preserve original ledger/audit/output bytes and link them from the new record.

Do not delete, rename, overwrite, reset, or bypass the old ledger; do not introduce a generic `--force`, arbitrary task-name retry, or directory-change loophole. Reserve the new ledger exclusively and atomically before worker dispatch, preserving failed/interrupted outcomes. Reusing it must refuse another attempt before any reader opens.

Task IDs, paths, timestamps, preflight values, and recovery lineage are engineering provenance. They must not change the model's mathematical definition or contaminate its deterministic scientific identity.

## 5. Validate recovery code before real stages

Keep changes narrow: preflight, lineage/attempt routing, diagnostics, and necessary orchestration repairs. Preserve model/loss/loader semantics. Any discovered correctness repair needs explicit documentation and fresh source-bound acceptance.

Add meaningful synthetic tests for:

- exact page-size/byte arithmetic and GiB reporting;
- malformed/unavailable probe data, threshold equality, fluctuating samples;
- preflight never constructing a reader or consuming real-attempt allowance;
- no automatic retry or reservation after a known failed preflight;
- original ledger remains unchanged and its old entry point still refuses retries;
- only one new recovery reservation; duplicate launch refusal;
- wrong predecessor/config/source acceptance or nonzero prior consumption rejection;
- worker launch recheck after passing preflight;
- exceptions/timeouts preserving new audit/ledger and blocking later stages;
- unchanged real resource limits, model/training configuration, and test guards.

Run appropriate quality checks and the full synthetic suite. Report actual counts; do not assume 247 remains the final count. Renew the source-bound acceptance and synthetic workspace measurement as required by the existing implementation. Do not manually flip acceptance flags to authorize execution.

## 6. Execute the existing dev gate only when ready

If stable preflight and all synthetic/compatibility checks pass, reserve the single Task0011 attempt and dispatch the unchanged dev workflow in a fresh CPU process.

Use only the first1,024 source-ordered IDs in frozen dev `train_background`, batch32, at most three training passes/96 updates, and one same-sample scoring pass. Maintain original memory/deadline enforcement and failed access audits.

Record complete pass times including loading/model-view preparation. The frozen extrapolation remains:

\[
2\left(699957\frac{\max(t_{train\ pass})}{1024}+74749\frac{t_{score\ pass}}{1024}\right)\le180\text{ s}.
\]

Do not use network-only times, remove the factor of two, require loss improvement as a model-selection criterion, or reuse dev weights for canonical training.

A failed dev gate ends dependent execution. Preserve new evidence and explain whether launch memory, actual workspace/RSS, loading, CPU throughput, numerical correctness, or a deadline was responsible. No hidden retry or scientific-policy change.

## 7. Conditional canonical training and completion

Passing recovery readiness alone does not authorize skipping dev feasibility. If the unchanged dev gate passes, this prompt authorizes continuation through the original Task0010 workflow, within its unchanged budgets:

1. Fresh full CPU training on 699,957 train backgrounds with full74,749 selection score each epoch.
2. Strict min_delta0/patience20/max200 selection and earliest ties; patience wins at epoch200 only if actually reached.
3. Best restoration and strict serialization/reload/selection-score verification.
4. Second independent fresh CPU run and exact scientific reproduction.
5. Finalized separate particle-model artifact only after all prerequisites succeed.
6. Postfreeze background scoring/calibration/diagnostics and independent background-result reproduction.

Reuse Task0010's implementation and exact validation/provenance contracts. Ensure source-bound acceptance, stage authorization, time budgets, and parent/worker lineage remain valid under recovery routing; do not call hidden workers to bypass the supervisor.

Keep fitting/calibration separate. Calibration is forbidden until convergence, restoration/reload, independent reproduction, and freeze succeed. No calibration/selection mixing or post-hoc score modification.

All completed history, exact score/hash comparisons, parameter identities, thresholds, counts, finite-sample intervals, and preregistered background profiles must use the existing definitions. Persist no per-event scores or reconstruction/code populations.

If a ceiling occurs without the fixed patience endpoint, report **convergence unresolved**. If reproduction fails, investigate and stop before calibration. Do not change horizon, batch, threads, device, model, or objective to obtain a success label.

Retain PCA and AE v1/v2 unchanged. A successful particle artifact adds a baseline for its representation; it does not supersede compact AE v2 or establish better signal discrimination.

## 8. Outputs and living memory

Create:

```text
docs/prompts/0011-particle-set-resource-recovery.md
docs/handoffs/0011-particle-set-resource-recovery.md
docs/particle-set-resource-recovery.md
results/tables/final/task0011-particle-set-recovery-summary.json
```

Save the prompt/initial handoff before substantive work. Keep large/local preflight, acceptance, recovery-plan, ledger, audits, and run outputs ignored. Curate only small factual evidence.

If later stages succeed, curate small training/threshold/profile tables, a clear convergence figure, and the tiny trained artifact using a narrow ignore exception. If stages do not execute, do not invent or emit success-shaped model/threshold tables.

Update the handoff index, current report/README where helpful, and `docs/project-memory.md` in place. Preserve the historical Task0010 report/handoff/gate summary; use dated links/additions where current reporting overlaps history.

Memory must distinguish preflight readiness, recovery launch, dev feasibility, full convergence, reproduction, freeze, and calibration. Record the remaining environment/resource issues, exact unchanged policy, motivation, actual new evidence, limitations, goals, roadmap, and short revision entry. Keep detailed execution chronology in the Task0011 handoff.

## 9. Validation, embargo, and completion states

Validate actual code changes with installation/import/dependency consistency as applicable, Ruff, full synthetic pytest, CPU smoke, documentation links, exclusions/historical hashes, `git diff --check`, and final diff inspection. Report checks not run and hosted CI as unverified unless observed.

Under every outcome:

```text
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

No test scores/distributions/metrics, final-unblinding invocation, signal-guided choice, MPS particle training, export, quantization, inference benchmark, Transformer, TensorRT, hls4ml, or trigger simulation.

Report one precise outcome:

- **Readiness still blocked:** no recovery data attempt; usable preparation/preflight/run procedure delivered.
- **Recovery attempted; baseline pending:** one authorized attempt stopped at a documented gate.
- **Canonical particle baseline completed:** all unchanged gates and background completion requirements passed.

Task0011 may complete its bounded recovery work while the canonical baseline remains pending. Do not relabel an environment failure as convergence failure, or a dev pass as finalized training.

Choose the next dependency from actual evidence. If successful, propose an inference-measurement protocol/foundation task. If not, propose a bounded host/engineering-resource/throughput/convergence decision matching the measured blocker. Do not execute the next task automatically.

## 10. Final response and manual Git delivery

Return:

1. Diagnosis, unchanged measurement definition, and preflight samples/results.
2. Recovery code/routing, preserved predecessor evidence, and attempt/step accounting.
3. Actual synthetic validation and test count.
4. Dev gate measurements and extrapolation, if reached.
5. Canonical epochs/best/stop/convergence/resources, restoration and independent reproduction, if reached.
6. Frozen artifact and background calibration/diagnostics, only if justified.
7. Explicit test-access audit and stages not reached.
8. Living-memory updates, completion status, limitations, next decision/task, and exact manual readiness/run instructions if blocked.
9. Actual intended files versus pre-existing/ignored/generated outputs.
10. **Git commit and push commands — mandatory and last.**

Do not stage, commit, or push automatically. Provide exact status/diff, selective intended-file staging, staged review/whitespace checks, outcome-appropriate Conventional Commit, and push for the actual branch/upstream.

Account explicitly for pre-existing Task0010 changes in overlapping files; ordinary whole-file staging cannot isolate this task's additions from earlier uncommitted work. Provide a concrete separate prerequisite-review/commit sequence where needed without executing it or silently combining tasks.

Do not use broad staging or include data, arrays, checkpoints, logs, caches, or unrelated work. A suitable message for recovery orchestration alone may be `fix: add bounded particle baseline recovery`; use a message reflecting the actual finalized outcome if training/calibration succeeds.

Proceed with **Task 0011 only**.
