# LatentTrigger — Task 0018: Shared-Mac Development Policy and Bounded Particle Characterization

You are continuing **LatentTrigger**. Perform **Task 0018 only**.

The user explicitly approved a single motivated execution-policy review and stated that available memory varies during normal Mac use and will often remain below our fixed limits. They cannot keep the Mac dedicated to this project. **Do not continue requiring a fixed global free-memory minimum or another cleanup/readiness window for the short dev study.** Implement the policy below, then move toward actual bounded characterization rather than another monitor-optimization experiment.

This task authorizes a separate, versioned **development-only process-budget policy** and one conditional use of the already granted, unspent≤96-step characterization allowance. It grants no additional allowance, canonical training, full-store study, selection/calibration, architectural change or test access.

## 1. Inspect actual state and preserve history

Read applicable instructions, `docs/development.md` and `docs/project-memory.md` first. Inspect actual status/index, branch/upstream, HEAD and prerequisites. Planning inspection found clean main/origin/main and Task0017 commitb194050 afterf74c7db; verify actual state and preserve unrelated edits.

Read Task0009–0017 relevant contracts/source/configs/reports/handoffs/curated results and actual small engineering receipts. Confirm original96 Task0013 updates are consumed and the canonical additional slot/output remain absent. Planning inspection found only the Task0017 NOT READY check receipt, no real Task0016 attempt/output or Task0017 execution plan. Refuse and reconcile unexpected later/inflight consumption; do not assign another budget automatically.

Record the evidence: original dev1024/96steps finished with367.25MiB peakRSS and167.672MiB native reservation; later startup measurements include179.672MiB native. The full-store custody peak was3,351,019,520bytes RSS and206,831,616bytes native. **Full-store evidence is not the footprint of this small dev store** and does not justify applying a512MiB RSS ceiling to canonical/full-store execution.

Historical749.343s>180s, Task0014 no workload gain, Task0015 synthetic2.14× below its3× gate, Task0016 prospective admission review and Task0017 checks remain factual records. Preserve old configs/manifests, code/acceptances/ledgers/receipts and PCA/AE artifacts. Do not erase failures, reset slots, edit synced `sources/` or invoke staging helpers.

Save actual prompt/initial handoff before substantive work:

```text
docs/prompts/0018-particle-shared-host-policy.md
docs/handoffs/0018-particle-shared-host-policy.md
```

## 2. Preregister the new development-only resource policy

Create a strict sidecar, for example:

```text
configs/resources/particle_shared_host_dev_policy_v1.json
```

Bind this actual prompt, unchanged mathematical model/design/input identities, exact new enforcement implementation/source acceptance, old policy/observation lineage and canonical additional budget anchor. This is an explicit engineering-policy change. Do not mutate the historical model JSON/resource fields, report an old policy hash for new behavior or use an arbitrary unsafe/config override.

The new fixed envelope is:

| Field | Shared-host dev policy |
| --- | --- |
| Global free+inactive available memory | Context only; **no launch minimum and no continuing floor** |
| Worker lifetime peakRSS | ≤536,870,912bytes =512MiB |
| Whole native malloc reservation | ≤268,435,456bytes =256MiB |
| Verified OS pressure NORMAL=1 | Record and permit if other guards pass |
| Verified OS pressure WARN=2 | Advisory, record and permit for this bounded dev scope |
| Verified OS pressure CRITICAL=4 | Veto before data; stop/latch during work |
| Pressure unavailable | Explicit unknown, permitted under these tight process/time bounds; never labeled normal |
| Unknown/malformed primary process accounting | Fail closed |
| CPU/batch/workers | Existing CPU1intra+1inter, batch32, workers0 |
| Dev-reader phase | ≤60s including imports/verification/cleanup, first64 sample IDs, zero updates |
| Dev phase | ≤300s including imports/verification/views/guards/audits/cleanup,≤96 started updates |

512MiB RSS leaves about145MiB above the observed367.25MiB dev peak;256MiB whole-native leaves about76MiB above the recorded179.672MiB startup reservation. These are declared conservative **process envelopes for bounded dev**, not guarantees of machine-wide availability. They replace the old dev6GiB/512MiB ceilings with tighter local budgets while removing the unsuitable global reserve. Do not sum RSS/native as disjoint allocations.

Use the same existing malloc/RSS/pressure bindings, validated ABI and provenance. Apple describes [memory pressure](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac) using multiple indicators; the [XNU flags](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event_private.h) distinguish NORMAL/WARN/CRITICAL. WARN advisory and unknown-pressure tolerance here are **our prospective engineering decisions**, not an Apple recommendation or proof the host cannot exhaust memory.

No kernel/OS configuration, app termination, cache purging, swap manipulation, privilege workaround or artificial pressure generation. Real allocation/IO/OOM/numerical errors still stop and preserve the attempt.

## 3. Minimal enforcement adaptation; stop performance experiments

Keep historical v4 sampler/monitor/manifests intact where practical. Implement a narrowly scoped process-budget guard for the new policy, reusing verified Darwin bindings, deadline/signal/owned-cleanup and audit machinery. Do not invent a new OS backend, benchmark matrix, optimizer or generic scheduler.

At startup, every phase/batch boundary and immediately before optimizer mutation, obtain fresh own-process RSS/native and available pressure, validate exact types/methods and enforce the new profile. Continue periodic process/pressure checks at50ms intent during blocked work, with existing main-thread signal/parent deadline enforcement. Preserve actual failed measurements/maxima, latched errors and partial audits. State scheduling/GIL/termination limitations honestly.

Global vm_stat is now **optional context telemetry**, not a primary admission input. Record it once at startup/phase boundaries with its actual timestamps/backend/age when available, using the existing bounded system command. A low value, unavailable/malformed snapshot, host query timeout or expired context age cannot become a disguised global-RAM veto. Mark unavailable/stale/error context truthfully; never fabricate safe counts or reuse it as fresh. If collection is slow, bound/skip it while process/deadline protection continues.

The old v4≤100ms host-age admission requirement belonged to host-primary enforcement. It does not apply as a workload veto when global counters are context only. This is an explicit policy/observation-role revision, **not v4-equivalent execution**. Fresh process/pressure guards and their failures remain operative; no broad catch-and-ignore of guard exceptions.

Do not require three globally stable free-memory readings or any5s memory-stability wait. The new preflight verifies source/config/policy/budget integrity, current process caps and absence of verified CRITICAL. It never asks the user to change app state. A WARN/unknown state and available RAM below4GiB are expected permitted cases under this development policy.

## 4. Science and population boundaries remain unchanged

Preserve exactly the478-parameter shared encoder/local2+mean8/shared decoder, ordered initialization, frozen feature/scaler/Nmax384/mask/retention semantics, sole corresponding weighted objective, FP32 network and FP64 pooling/residual/score/reductions, equal event weights, CPU seed1729/exact Adam/batch32/workers0/1+1thread/deterministic settings and source membership.

Use only the same original first1024 frozen **dev train-background IDs**, with first64 reader subset. The dev store has8494 events/about23MiB persistent data; preserve its full constructor verification rather than skipping integrity. Refuse full-store paths, selection/calibration/test/truth and unsupported phases before constructing data. No data preprocessing rebuild, model redesign, hyperparameter search, discarded-weight reuse or new sample selection.

The canonical max200/patience20/min_delta0 and original180s/10h/22h full-run policy remain historical/current full-run contracts, **not authorized execution in this task**. A process-budget profile designed for the small dev store cannot authorize canonical training.

## 5. One shared allowance and usable CLI

Adopt the same exclusive canonical anchor/output:

```text
data/baselines/task0016-runtime-characterization-attempt.json
data/baselines/task0016-runtime-characterization-study
```

No independently spendable Task0018 slot, reset or alternate real output. Original96 + already granted new≤96 gives cumulative≤192, never another96 on top. A reserved/partial/foreign/inflight/consumed anchor blocks all run paths; reconcile rather than retry. A failed read-only preflight does not spend optimizer allowance.

Use a separate new execution plan/current acceptance binding the adopted budget and changed policy; preserve prior plans. Reuse the Task0017 history/concurrency pattern. When CLI/test code changes, verify original accepted bytes through the actual historical commit/snapshot and require a new complete current source map; never weaken identity validation wholesale or treat the old612-test acceptance as current.

Make **shared-host-dev-v1 the documented default for the short characterization commands**, clearly print/store the selected policy and diagnostic-only scope. The old policy can remain explicitly named for reproduction; do not leave users accidentally invoking the old fixed4/4.5GiB default. Any selector accepts only exact named/versioned profiles, not arbitrary thresholds or `--unsafe`.

Keep check-only repeatable and data/slot-free. The run action owns a new lightweight process-budget preflight, atomically reserves the shared slot before reader work and independently rechecks source/policy/process conditions in fresh workers. Two competing launches must still have at most one winner. User-facing output is concise; full structured evidence goes to immutable ignored receipts.

## 6. Validate, then execute one bounded characterization if locally admissible

Add meaningful synthetic tests proving that available-memory values below4/4.5GiB and WARN=2 **do not block the new dev profile**, while CRITICAL, excess512MiB RSS/256MiB native, unknown/malformed primary process accounting, unsupported scope and deadlines do. Test unknown pressure disclosure, unavailable/stale global context remaining advisory, periodic guards during slow context/blocked work, failed-peak preservation and unchanged audit/step reservations.

Retain explicit legacy-policy coverage, numerical/Adam/reconstruction/score parity, role/input guards and one-winner concurrency. CI fixtures must be self-contained with no operational receipts/data. Run appropriate full synthetic suite, lint/format, dependency/CPU smoke, history/link/JSON/whitespace checks. Generate actual current source acceptance after final executable changes; all helpers must be covered. No timing search or new synthetic speedup threshold.

Freeze executable code before real work. This prompt authorizes **one** actual bounded characterization after successful synthetic validation and a successful local process-budget preflight, even with other apps open, WARN/unknown pressure or low global available memory. Do not repeatedly attempt it or wait for resources automatically. If CRITICAL/process/technical integrity prevents admission, record the exact blocker and finish without a real reservation; provide the repeatable check/manual run path. Do not fall back to the old global free-memory criteria.

If admitted, run unchanged scientific functions under the new guard:

1. Fresh dev-reader first64/two batch32 views, zero updates,≤60s.
2. Fresh phase process checks, then fresh disposable model on the same1024 sample,≤3training passes/96started steps and one same-sample scoring pass,≤300s.

Persist started/completed/inflight counts before/after mutation. No individual real-score/weight persistence, full custody replay or later stages. A failure after real reservation consumes this attempt even at zero updates; no retry following source repairs. Compare eligible deterministic diagnostic fields/score hash with Task0013 when runtime bindings match; preserve unexplained mismatch as a blocker, never tune or rerun to fix it inside this budget.

Recompute the unchanged diagnostic projection `2*(699957*max(train_pass_seconds)/1024+74749*score_pass_seconds/1024)`. Record whether the original180s target passes. A complete characterization above180s remains a failed original target but useful completed evidence; do not subtract guards, change factor2, select a faster pass or stop documentation as if no measurement occurred. It does not unlock canonical training. Other resource/numerical/partial failures remain actual failures.

## 7. Deliverables, memory and the next scientific step

Create:

```text
docs/particle-shared-host-policy.md
results/tables/final/task0018-particle-shared-host-policy-summary.json
```

Record old/new policy differences and measured-envelope rationale before real reads, exact authorization/current source identity, actual local/global/pressure context, access/steps/cumulative budget, numerical comparison and observed timing/projection. Preserve historical failures rather than relabeling them. New measurements represent the shared host at their actual time; no guaranteed future RAM/performance or hard real-time claim.

Update `docs/project-memory.md`, README and handoff index in place. Explain that fixed global RAM reserve was an unsuitable dev admission heuristic for normal Mac use, and that the next step now follows real measurements. Shared-host policy is bounded-dev only; full-store/long-training resource policy remains unresolved and must use its own measured footprint. Keep source/model/calibration facts and roadmap distinct.

State:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

If characterization completes, propose one consolidated next decision for **canonical execution feasibility, full-store process budget and training-time budget**, based on the actual new measurement. Preserve the relationship between180s, max200,10h/run and22h total until an explicit versioned revision. No more monitor-optimization/readiness task sequence; no automatic full training. If canonical work cannot reasonably coexist with the user's host use, explain that finding and preserve the particle branch pending while planning hardware benchmarks of frozen PCA/aggregate AE. Do not make the entire project depend on repeatedly finding an idle Mac.

## 8. Required final Git section — last section of the response

Do not automatically stage, commit or push. End with exact status/diff/index review, selective `git add --` of actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push for the actual branch/upstream. Exclude data/acceptances/ledgers/raw receipts/logs, snapshots/caches and large outputs. Preserve unrelated work and inspected historical files; no prerequisite staging helper. Include this prompt and its handoff with the task.

Proceed with **Task0018 only**.
