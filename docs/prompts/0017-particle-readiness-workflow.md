# LatentTrigger — Task 0017: User-Triggered Readiness Checks and a Single Shared Characterization Slot

You are continuing **LatentTrigger**. Perform **Task 0017 only**.

The user explicitly authorized fixing readiness handling so that failed read-only checks do not require another implementation task or consume the real study. The Mac remains in normal use with other applications open. No app closure, reboot, dedicated window, background polling or automatic cleanup.

This task authorizes reconciliation, narrow readiness/orchestration changes, synthetic validation and **one read-only integration check after acceptance**. It also authorizes delivering a user-triggered command for the already granted single bounded characterization. **Do not execute real reader/dev work automatically during this implementation task**, even if its integration check passes. No new optimizer allowance or canonical training.

## 1. Actual state and problem

Task0016 automatic readiness failed at3.558059692GiB below the unchanged4/4.5GiB thresholds. Its later manual command also failed before data:

```text
status: readiness_deferred_attempt_unreserved
error: Verified pressure warning/critical veto.
pressure_dispatch_flags: 2 (WARN)
host generations published: 0
new reader/population/real steps: 0
cumulative real steps: 96
slot_reserved: false
```

The manual run measured own-process peakRSS358842368bytes/native reservation171622400bytes, but no complete available-memory sample was admitted. Do not carry the earlier3.558GiB forward as a measurement of this manual run. Warning is a separate veto; lowering the launch threshold would not resolve it.

Both fixed readiness reservation files now exist. The current controller creates those files exclusively, so a later read-only manual check is refused even though the real-study slot remains unreserved. The fix must separate a history of safe read-only checks from exclusive permission to execute real data phases.

Original Task0013 consumed96 updates; the replacement additional allowance remains≤96, cumulative≤192. Task0015's3× gate failed; Task0016 prospectively removed that synthetic admission criterion for diagnostic scope, while retaining180s. Do not erase historical failures, reintroduce an unearned throughput pass or create a third allowance.

## 2. Inspect, preserve and record

Read applicable instructions, `docs/development.md` and `docs/project-memory.md` before planning. Inspect Git status/index, branch/upstream/HEAD and prerequisites. Planning inspection found clean main/origin/main, Task0016 commitf74c7db after0610c0f; verify actual state and preserve unrelated edits.

Read Task0009–0016 relevant configs/prompts/handoffs/reports/summaries, unchanged v4 monitor/sampler, Task0016 authorization/plan/supersession, automatic and manual readiness/reservations/evidence, historical real receipts and current source acceptance. Inspect small engineering records only, not stores or dataset arrays.

Verify both failed checks' identities, actual pressure field and zero access/inflight counts; confirm the real attempt/output remain absent. Refuse unexpected later real consumption before preparing any successor execution route. Preserve manual receipt, bootstrap/access audit, partial monitor report and raw evidence byte-for-byte.

Save the actual prompt and initial handoff:

```text
docs/prompts/0017-particle-readiness-workflow.md
docs/handoffs/0017-particle-readiness-workflow.md
```

Preserve all historical configs/manifests/source acceptances/ledgers/results/artifacts and task-time records. Update current living memory/index/README; historical handoffs may receive an explicit dated additive reconciliation note. Do not edit the pinned Task0016 prompt, delete its readiness files to permit retry, reset a ledger or edit synced `sources/`. No automatic staging/commit/push.

## 3. Keep all science and safeguards

Keep the478-parameter model, frozen data/features/scalers/Nmax384/masks, sole objective/FP32-network/FP64-pooling-residual-score, equal event weights, seed1729/exact Adam/batch32/workers0/CPU1+1/determinism and role/embargo contracts unchanged. Preserve model/design/profile bytes and existing historical numerical results.

Adopt final corrected v4 unchanged: system one-shot vm_stat, displayed free+inactive×actual-page-size,50ms host cadence, query-start age≤100ms, fresh process/native/pressure guards, fresh launch/phase observations, latched failures, signals/deadlines and owned cleanup. No direct-Mach substitution, retimestamping stale samples, weakening pressure veto or synthetic values in live acceptance.

Keep launch4.5GiB, continuing4GiB, native512MiB, peakRSS6GiB,2s query timeout,3readings spanning≥5s within30s, reader60s/dev300s, factor2/180s throughput criterion and original full-run limits. Unknown primary accounting fails closed; optional pressure unavailable remains disclosed under the existing rule, never labeled normal. Verified WARN/critical still stops real admission/work.

This changes **readiness invocation/history semantics**, not scientific, observation or numerical policy. A failed check is not a failed optimizer attempt. A reserved/dispatched real attempt is still non-retryable.

## 4. Implement independent, user-triggered read-only checks

Provide a narrow stdlib-only controller entry point, for example:

```bash
.venv/bin/python -m latenttrigger.supervision.particle_readiness --check-readiness
```

Every explicit invocation performs at most one bounded readiness protocol and exits. It never constructs a store/model/optimizer, opens dataset arrays, requests populations, scores, reserves the real slot or starts characterization, **including when ready**. Framework imports/CPU preparation needed to represent the actual worker are permitted in a fresh child, not the parent.

Store each invocation under a fixed ignored readiness-history root with a safely generated unique ID. Exclusively create that invocation's reservation, immutable final receipt and owned evidence/log paths; do not overwrite previous checks or use arbitrary user-provided directories. Unique readiness directories are history, not alternate real-attempt outputs. Preserve failed/interrupted/bootstrap-only checks as well as passes.

Bind each check to this authorization/implementation version, current source acceptance and model/profile/v4 hashes, worker token/parent, monotonic sampling times and UTC timestamps. Bound each check≤30s including imports/cleanup and logs. No scheduler, sleep-and-retry loop, heartbeat, readiness notification service or background waiting. Multiple separate user-invoked checks are expressly allowed; parallel checks must not mix receipts, leak children or corrupt history.

Use the unchanged guard logic for readiness. Preserve partial readings and the first latched veto. For useful failure reporting, when a pressure veto leaves available bytes unmeasured, one additional bounded **read-only diagnostic** system snapshot may be collected within the same deadline. Label its later timestamp/context separately; it must never reverse the original veto, count as an admitted generation or open data. If telemetry is unavailable, report unknown rather than inventing a number.

Report resource readiness separately from execution permission/budget availability. A passing host check cannot clear a consumed/foreign/inflight real slot or grant canonical permission. A stale/history receipt is not a bearer token to start work.

Default stdout must be brief and human-readable: ready/not ready/error, available memory when actually measured, pressure state/unknown, relevant blocker, explicit zero data/step/slot reservation for check-only and receipt path/ID. Save full structured JSON automatically; optional `--json` may print it for tooling. Do not dump raw vm_stat/large nested reports by default or inspect unrelated app/window/document content. Document expected not-ready separately from integrity/unsupported errors in status/exit semantics.

## 5. Preserve one shared real budget and an explicit run action

Provide a separate deliberate user action, for example:

```bash
.venv/bin/python -m latenttrigger.supervision.particle_readiness --run-characterization
```

It always performs its **own new readiness check**, recorded in the same history. Never trust a prior displayed pass or let the caller substitute a fabricated receipt. If not ready, it exits without a real reservation or step; another later user-triggered invocation is permitted only while the canonical real slot remains unused. No automatic retry or waiting loop.

After a fresh pass, atomically reserve the already authorized additional characterization slot before data. **Reuse the canonical Task0016 slot anchor**:

```text
data/baselines/task0016-runtime-characterization-attempt.json
```

Do not create an independently spendable Task0017 slot. All old/new/parallel routes must converge on that one exclusive anchor. Refuse existing, foreign, partial/inflight or consumed reservation; no stale-lock removal. Use one fixed real output location, preserving original Task0016 plan/supersession/readiness files. Bind the new worker implementation and readiness ID through a separate versioned execution plan; do not overwrite the old plan whose source acceptance is historical.

Adopt Task0016's≤96 additional/≤192 cumulative allowance and diagnostic phases exactly. The new plan supplies current implementation/source authorization and supersedes exhausted one-shot readiness handling; it grants no new budget, observation change or full-run scope. Keep old executables intact where practical; their stale or consumed paths must not bypass the canonical slot. Do not monkeypatch old module globals or disable their validation to make new code fit.

Fresh workers independently verify source/config/profile/v4/new plan/token/parent/reservation and launch immediately before data. Recheck at each existing phase boundary. Race between passing readiness and actual launch can still block safely; disclose this rather than promise a ready check guarantees execution.

Reuse existing scientific functions and Task0016 characterization semantics:

- first64 of the same original1024 frozen dev-train IDs, two batch32 views, zero updates, dev-reader≤60s;
- fresh dev readiness, then disposable fresh model/seed/shuffle,≤three1024 training passes/96 started updates and one same-sample score pass, dev≤300s;
- unchanged factor2/slowest-pass/180s projection, exact eligible historical numerical comparison and truthful throughput-only completion classification;
- started/completed/inflight accounting persisted before/after mutation, original96+new≤96, same1024 unique sample and no weights/individual-score persistence.

No full custody replay, full selection/calibration/test request, canonical fit/reproduction/freeze/export or model tuning. A reserved/dispatched real phase failure consumes the attempt even at zero optimizer steps. Only unreserved read-only readiness is repeatable. Existing historical749.343s and synthetic2.14× evidence remain intact; neither establishes real v4 throughput.

Do not run this action automatically in Task0017. The user chooses whether and when to invoke it, with their apps open and all contemporaneous guards intact.

## 6. Validation and bounded integration

Add meaningful self-contained synthetic tests for two consecutive failed checks preserving both receipts, failed-then-passing checks without slot reservation, check-only never constructing data or starting work, source/manifest/token/parent identity, malformed/stale/foreign receipts, unknown pressure versus verified veto, timeout/partial evidence and safe history IDs.

Test concurrency explicitly: independent checks, two simultaneous run actions competing for the same canonical anchor with at most one winner, no data for the loser, and refusal after partial/consumed real reservation. Verify original96/additional96/cumulative192 and no third allowance. Use fake stores/workers/clock/filesystems as appropriate; ordinary CI must not require operational receipts or datasets. Maintain existing v4 guard/numerical coverage.

Run appropriate full synthetic suite, lint/format, dependency/CPU smoke, portability, history/link/JSON/whitespace checks. Generate actual current source-bound acceptance after final executable changes, preserving old576-test acceptance/history rather than treating its old map as today's full map. All new executable helpers must be included; no unstamped launcher in ignored data.

After final acceptance, execute **one** integration `--check-readiness` only. Record actual pass/failure/unknown with no new real data/steps/slot. A shared-host veto is an expected valid outcome and must not block task completion. Do not repeat the check to fish for a pass or rerun timing matrices. User-triggered later checks are separate operations under the delivered protocol, not implementation-task replays.

## 7. Deliverables and living memory

Create:

```text
docs/particle-readiness-workflow.md
results/tables/final/task0017-particle-readiness-workflow-summary.json
```

Document the two exact commands, read-only versus real-action behavior, immutable receipt history, canonical shared slot, status/exit meanings and safe interruption handling. Explain that favorable resources and current source acceptance are prerequisites, not a promise of throughput/convergence. No command requires app closure or permanent dedicated use.

Reconcile the later Task0016 manual WARNING receipt in current memory/report, preserving original task-time pending records. Update `docs/project-memory.md`, README and handoff index with the enduring shared-Mac preference, repeated user checks now supported, still-unspent additional slot, original96 historical steps and no real Task0017 execution. CLI invocations write ignored receipts, not versioned docs/Git mutations; the next relevant working session reconciles new real receipts. A failed read-only check no longer needs another numbered task or commit.

State:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

The next dependency is the delivered user-controlled run action when resources permit, not another identical readiness implementation. If its eventual actual characterization passes, later explicitly authorize full-store/current-policy artifact compatibility and canonical training. If throughput fails, use its measured projection for a separate versioned time-budget decision. Preserve all current numerical/pressure limits; no automatic optimization allowance or inference of model infeasibility from host warnings.

## 8. Required final Git section — last section of the response

Do not automatically stage, commit or push. End with exact status/diff/index review, selective `git add --` of actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push for the actual branch/upstream. Exclude ignored receipt history/acceptances/ledgers/logs, snapshots/caches and large outputs. Preserve unrelated work and inspected historical files; no old prerequisite staging helper. Include the actual prompt and handoff with the implementation.

Proceed with **Task0017 only**.
