# LatentTrigger — Task 0014: Reconcile the External Study and Reduce Resource-Monitor Overhead

User message transcribed with Markdown transport escapes normalized; wording and scope preserved.

You are continuing **LatentTrigger**. Perform **Task 0014 only**.

The user has reopened other applications and must continue using the Mac normally. **This task must progress and finish with those applications open.** Do not ask for a dedicated machine, closing Codex/apps, rebooting or another readiness window. Use existing receipts, synthetic fixtures and short bounded engineering measurements. No new real data access or real optimizer step is authorized.

## 1. Actual starting point and scope

Task0013's external study has now executed once. Its previously pending slot is consumed:

- Pilot readiness passed at8.814041/8.728348/8.697464GiB under the unchanged metric.
- Dev reader and separate full-store custody passed; the latter peakRSS was3,351,019,520bytes, below6GiB. No full-population model request occurred.
- The unchanged v2 activation rule passed **for bounded dev only**, with bound+margin190,340,736bytes≤536,870,912bytes.
- Dev readiness passed. Exactly1024 unique background-development events, three training passes,96 started/completed optimizer steps and one same-sample score pass were completed.
- The study failed at the throughput gate: **749.3431957854029s conservative extrapolation versus180s**. Canonical training, selection, reproduction, freeze and calibration were not reached.

Actual per1024 timings were training `[0.5065042919995904, 0.4505980419999105, 0.45002770899918687]`s and scoring0.3897375420001481s. Dev resource accounting recorded287 probes, cumulative probe time1.316605680018256s, max probe0.00705841600029089s, total worker time3.0156337919997895s including1.1284318750003877s runtime import/setup. Probes include synchronous/background calls and other phase work; their sum is **not** a directly subtractable critical-path duration.

The current living memory1.6 and original Task0013 curated summary still describe the earlier pending state. Reconcile them against actual saved receipts. The old outcome is an engineering throughput failure, not a convergence result. No trained/frozen particle artifact exists.

This task authorizes receipt reconciliation, bounded performance attribution, a separately versioned lower-overhead resource collector/monitor where evidence supports it, integration on synthetic inputs, and a proposed next real validation protocol. It does not authorize changing numerical limits, repeating Task0013 or starting canonical training.

## 2. Inspect and preserve

Read applicable instructions, `docs/development.md` and `docs/project-memory.md` first. Inspect Git status/index, branch/upstream, HEAD and actual prerequisite commits. Planning inspection found clean `main...origin/main`, Task0013 commit `9d5e03b` after Task0012 `53b238a`; verify the actual state. Preserve unrelated edits and initial snapshots of intended updates.

Read Task0009–0013 specifications, reports/handoffs, model configs, unchanged v2 sidecar, monitor/probe, streamed views, audit hooks, training and lightweight supervision code. Read the actual ignored records:

```text
data/baselines/task0013-particle-host-plan.json
data/baselines/task0013-particle-host-invocation.json
data/baselines/task0013-particle-host-study/workflow.json
data/baselines/task0013-particle-host-study/activation.json
data/baselines/task0013-particle-host-study/*/stage-result.json
data/baselines/task0013-particle-host-study/*/access-audit.json
data/baselines/task0013-particle-host-study/dev/dev-gate.json
data/baselines/task0013-particle-host-study/dev/dev-progress.json
data/baselines/task0013-particle-host-study/dev/resource-samples.jsonl
data/task0013-synthetic-acceptance.json
```

Verify file/source/config/profile/acceptance lineage and actual started/completed/inflight counts before planning. Reading these small engineering records is allowed; do not construct stores, hash dataset arrays/raw files, repeat custody, reread model populations or invoke old run/experiment/preparation routes. The original real dev allowance is fully consumed, not available again under a new task number.

Save the actual prompt and initial handoff before substantive work:

```text
docs/prompts/0014-particle-monitor-performance.md
docs/handoffs/0014-particle-monitor-performance.md
```

Preserve old configurations, source acceptances, plans/ledgers, receipts, failed result and all scientific artifacts. Do not edit the pinned Task0013 prompt. Keep original task-time handoffs/summaries intact; a dated additive Task0013 handoff note may link to the manual reconciliation, preserving its original content. Current memory/index/README should describe current facts. Do not edit synced `sources/`, reset reservations or automatically stage/commit/push.

## 3. Reconcile access, activation and timing honestly

Record that the external slot was used and96 real steps completed without inflight steps. Account for first64 reader views plus the three1024 training presentations and1024 scoring presentations, all within the same1024 unique dev IDs. Separate recorded custody operations from population access, and note the dev-stage constructor separately where source/receipts establish it. Test model/evaluation access remainsNO/NO.

Recompute, without new execution:

`2*(699957*max(train_pass_seconds)/1024 + 74749*score_pass_seconds/1024)`.

Preserve749.3431957854029s as the historical failed gate. Show its training/scoring terms and factor2 separately. Explain that this projects a full cycle from a small sample; it is not a measured full epoch. Do not subtract probes, remove the slowest pass, use later passes only, reduce factor2 or reinterpret180s to turn the failure into a pass.

Separate bounded-dev activation, memory acceptance, throughput acceptance and canonical model status. Earlier reader evidence remains valid for its actual code/profile/environment; it does not validate a changed collector, current host availability or future full training. Never discard dev failure because memory passed.

## 4. Profile the engineering cost using synthetic inputs

Inspect the call graph before attributing cost: before/after-batch resource checks,50ms background watcher, serialized probe lock, repeated `vm_stat` subprocesses, library/symbol lookup, optional telemetry, journal writes, audit/step persistence, synthetic model compute and view transformation. Avoid blaming unrelated apps or attributing all historical elapsed time to the monitor.

Preregister one small benchmark matrix before running it: fixed seed, shapes, CPU1/1, repetition counts/order, timing boundaries and reporting. Use batch32/Nmax384 and synthetic masks/channels satisfying the existing input contract. Keep at most a few batches resident; no fabricated full population. Run in fresh processes with the same initialization/optimizer/objective when comparing numerical behavior.

Compare old collector/monitor with the candidate on identical synthetic work. Include isolated collection, complete checks/journal/audit cost and an identical short synthetic training/scoring workload. A compute-only arm can estimate instrumentation cost but must be explicitly diagnostic; it is never a production no-monitor option. If timing instrumentation is added, separate wall time, process CPU time, probe duration, lock wait, serialization/file IO and monitor-thread time; do not sum overlapping timers as exclusive components.

Use fixed repetitions, no best-of timing selection. Target≤120s total for the benchmark matrix and≤30s per arm, including imports. Repeat only affected arms if a code correction requires it, preserving failed measurements; no timing-driven parameter search. Record ordinary shared-host conditions and variability. Synthetic timings establish comparative engineering behavior, not real throughput or signal performance.

Read-only OS probe diagnostics may collect low availability. They do not require4.5GiB admission because they open no data. Synthetic guard tests may inject explicit fixtures; never present those numbers as actual host readiness. Do not disable failing real checks to label a live production run accepted. Ordinary synthetic validation must remain possible with other applications open.

## 5. Implement a supported, versioned lower-overhead monitor

Prefer a narrow new collector/monitor over changing frozen scientific code. Keep the stdlib-only supervisor import contract and existing reader, math, initialization, optimizer and population semantics.

Investigate direct Darwin statistics via supported Mach interfaces with cached library/symbol bindings, actual kernel page size and validated ABI/return counts. Use installed headers where available and primary sources:

- [Apple vm_stat source](https://github.com/apple-oss-distributions/system_cmds/blob/main/vm_stat/vm_stat.c)
- [XNU VM structures](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/vm_statistics.h)
- [XNU host definitions](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/mach/host_info.h)
- [XNU host statistics and rate limiting](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/kern/host.c)

Two specific issues require review:

1. `vm_stat` displays **Pages free = native free_count − speculative_count**. Preserve that display convention: the existing metric uses displayed free+inactive. Raw Mach free_count+inactive would silently change the metric. Keep raw native counts and normalized counts distinct, reject impossible subtraction and test exact fixture parity.
2. XNU can cache/rate-limit host-statistics calls for third-party processes. Fast call completion does not prove fresh sampling. Verify the relevant platform behavior and document supported freshness/detection bounds. Do not claim fresh50ms measurements from an unverified cached API.

If the direct backend cannot support the required observation semantics, consider one bounded, owned long-lived system `vm_stat` stream rather than spawning it on every check. Validate exact integer fields, page size, partial lines/repeated headers, startup, sample timestamps/age, EOF, child failure, deadlines and cleanup. Reject abbreviated/lossy primary counters. No privilege/entitlement tricks or machine configuration changes to evade access controls. If neither candidate is defensible, report that limitation and retain the original backend; task completion does not depend on claiming an optimization.

Retain native whole-malloc reserved/in-use and current/lifetime peakRSS distinctions, optional pressure warning/critical veto, unknown telemetry disclosure and primary-unknown fail-closed behavior. Cache bindings, not unbounded stale values. No invented raw `vm_stat` output for native snapshots; name the actual backend and retain numeric/raw provenance appropriate to it.

Preserve admission4.5GiB, continuing4GiB, native512MiB, peakRSS6GiB,180s full-cycle/extrapolation target and every original phase/total deadline. Keep50ms watcher intent, synchronous before/after-batch checks and signal/parent interruption. State observed probe latency and any kernel/stream age/GIL scheduling limit. A candidate needing weaker freshness/enforcement must remain proposed and cannot be activated here.

Keep original v2 sidecar and its collector implementation byte-identical where practical. Add a separate strict implementation manifest, for example:

```text
configs/resources/particle_resource_monitor_v3.json
```

Its version identifies an engineering monitor change, not a new mathematical model. Bind unchanged design/model/profile hashes, exact backend/version/observation semantics, unchanged limits, synthetic acceptance and **no real execution/full-run authorization**. Whitelist the exact supported relationship; no arbitrary overrides or mutation followed by reporting an old hash. Leave future artifact/completion compatibility pending until its actual full-run authorization.

Resource journal and audit semantics must preserve failures, stage minima/peaks, sample age/method and step reservations. Reduce unnecessary plumbing only if guard/audit guarantees survive. No asynchronous loss of a pre-step reservation, unchecked sampling gap, unsupported workspace accounting or hidden fallback. Limit new dependencies; prefer existing stdlib/runtime. Do not build a generic scheduler, UI/dashboard or application-management system.

## 6. Validation and task acceptance

Add meaningful synthetic tests for counter normalization including speculative pages, ABI/malformed/unsupported behavior, optional versus primary unknowns, low memory/equality/pressure veto, collector errors/staleness, concurrent checks and expired deadlines, owned-child cleanup if applicable, strict manifest/source binding and unchanged numerical results. Verify matching reconstructions, objective/scores and deterministic parameter/Adam updates on identical synthetic data when integration changes. Existing historical tests must remain valid; CI stays synthetic/platform-independent.

All new executable code, including benchmark helpers, must be included in explicit source acceptance. Do not put unstamped executable launchers in ignored data. Generate current acceptance from actual validation after final source changes; preserve all historical acceptances and actual failed manual receipts. Run appropriate lint/format, dependency/CPU smoke, synthetic suite, link/history/whitespace checks. Report actual counts and unavailable platform checks; hostedCI remains unverified unless actually observed.

Acceptance does not require a favorable current host preflight or180s synthetic extrapolation. It requires exact manual-result reconciliation, truthful cost attribution, a tested implementation or well-supported limitation, and no unauthorized real execution. A synthetic speedup never changes the historical dev gate or establishes canonical feasibility.

Create:

```text
docs/particle-monitor-performance.md
results/tables/final/task0014-particle-monitor-performance-summary.json
```

The summary distinguishes historical real measurements, new synthetic timings, observed OS diagnostics, candidate readiness/limitations, original budget consumed and next validation pending. It must record **zero new real custody/population requests/events/steps in Task0014**, alongside the96 historical steps now reconciled. State:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Update `docs/project-memory.md` in place, README and handoff index. Replace stale pending-slot/no-real-steps statements with the actual manual result; preserve original scientific limitations and distinguish bounded-dev activation from throughput failure. Record the user's shared-use Mac constraint as an enduring operating preference. Keep detailed chronology in the task handoff, with a short memory revision entry.

## 7. Next step based on evidence

If a defensible tested lower-overhead implementation is available, propose **Task0015 — Bounded Runtime Revalidation under the Reviewed Monitor**. Specify a minimal fixed protocol and separate versioned execution authorization; the original96 real steps remain consumed. Any additional real benchmark budget must be explicitly justified and authorized in that future prompt, accounted cumulatively and separated from model selection. Do not create/execute another real slot here, replay old routes, reuse disposable weights or call synthetic timings proof that180s now passes.

If collector freshness/support or synthetic cost remains unresolved, propose only the required engineering decision. If180s appears impractical, explain its preregistered engineering role and implications for the existing10h/run/22h total limits; any future limit review must be explicit/versioned, not a silent adjustment in this task. No model redesign or HPO from this throughput result.

A later real validation/training run remains conditional on contemporaneous resource guards and user-chosen scheduling. Normal app use may affect its availability/timing. Do not demand permanent exclusive Mac use, automatically close workloads, poll indefinitely for a window or promise that today's historical8.8GiB persists. Finish this engineering task without requiring such a run.

## 8. Required final Git section — last section of the response

Do not automatically stage, commit or push. End with exact status/diff, selective `git add --` of actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push for the actual branch/upstream. Exclude data/acceptance/benchmark logs, manual receipts, snapshots, caches and generated large files. Preserve unrelated work and do not stage historical files merely inspected. Prompt and handoff belong with this task. Verify actual prerequisites; never run old snapshot-staging helpers.

Proceed with **Task0014 only**.
