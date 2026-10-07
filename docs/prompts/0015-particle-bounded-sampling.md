# LatentTrigger — Task 0015: Versioned Bounded-Age Monitoring and Conditional Runtime Revalidation

You are continuing **LatentTrigger**. Perform **Task 0015 only**.

The user must keep using the Mac with other applications open. Complete implementation, synthetic validation and documentation under normal shared use. Do not request closing apps/Codex, rebooting, a dedicated machine or indefinite polling. A conditional real study may be deferred without blocking task completion.

## 1. Evidence and authorized decision

Task0013's external run passed memory, reader/custody and v2 activation **for bounded dev**, then failed the unchanged conservative throughput gate at749.3431957854029s>180s. Its1024 unique dev IDs, three training passes,96 started/completed real updates and one scoring pass are consumed. Task0014 reconciled this history and made the original synthetic tests independent of operational data.

Task0014 v3 retained a new synchronous system `vm_stat` process at every check. Its fixed synthetic matrix measured collector5.100→3.658ms and complete checks0.179→0.160s, but complete workload0.381828500→0.388047000s: **no end-to-end improvement demonstrated**. Direct Mach collection remains diagnostic-only because kernel caching lacks a trustworthy generation timestamp. V3 alone does not justify another identical real trial.

This prompt explicitly authorizes a **new versioned engineering observation contract**: sample the host through the existing system `vm_stat` backend at50ms cadence, and allow batch checks to consume the latest successfully validated host observation only while its conservative age upper bound is≤100ms. Process-local native reservation/RSS, pressure where available, errors and deadlines remain freshly checked at every batch boundary.

This changes the observation architecture: it is **not equivalent to v2/v3 fresh host collection on every check**. Record that distinction and the bounded-age rationale explicitly. Preserve all numerical/scientific limits. An unsupported observation contract must remain proposed; do not implement it by disguising reused samples as fresh.

If the synthetic acceptance and material-improvement criteria below pass, this prompt also grants **at most96 additional real optimizer steps**, solely for one new engineering revalidation on the same original1024 dev IDs. Cumulative original+new ceiling is192 started real steps. This is a deliberate additional budget, not recovered unused allowance. It grants no canonical fit, selection, calibration, reuse of dev weights or model tuning.

## 2. Inspect and preserve

Read applicable instructions, `docs/development.md`, and `docs/project-memory.md` before planning. Inspect actual branch/upstream/status/index/HEAD/prerequisites and preserve unrelated edits. Planning inspection found clean main/origin/main and Task0014 commit8d0e3f9 after9d5e03b; recheck actual state.

Read Task0009–0014 configs/prompts/handoffs/reports/summaries; actual Task0013 manual receipts and Task0014 acceptance/benchmark; old monitors, v3 collector, audit and streamed training code. Verify historical consumption and original identities before assigning additional budget. Inspect only small manifests/engineering records; do not construct stores or repeat dataset hashing as inspection.

Save the actual prompt and initial handoff before substantive work:

```text
docs/prompts/0015-particle-bounded-sampling.md
docs/handoffs/0015-particle-bounded-sampling.md
```

Preserve old configurations, v2/v3 implementations/manifests, historical source acceptances/failed results/manual receipts/ledgers and PCA/AE artifacts. Current memory/index/README may evolve; historical task-time records stay intact or receive explicit dated additive notes. Do not edit synced `sources/`, reset slots, use old staging helpers or automatically stage/commit/push.

## 3. Contracts that remain fixed

Preserve the478-parameter equivariant AE/local2+mean8, ordered initialization, frozen features/scalers/Nmax384/masks, FP32 network and FP64 pooling/residual/reductions, sole weighted corresponding-particle objective, equal event weights, CPU seed1729, exact Adam settings, batch32/workers0/CPU1intra+1inter/determinism, split membership and test embargo. No architecture/feature/device/precision/batch/thread/horizon changes or HPO.

Keep exactly: launch4.5GiB, continuing4GiB, whole-native reservation512MiB, worker lifetime peakRSS6GiB, watcher50ms, external `vm_stat` timeout2s, reader60s, dev300s, factor2 extrapolation≤180s, actual future full-cycle≤180s and original10h/run/22h two-run budgets. The canonical max200/patience20/min_delta0/convergence-unresolved rule is unchanged and not executed here.

Keep original design/executable JSON and launch-policy-v2 bytes/hashes. Add a separately typed exact v4 observation manifest, for example `configs/resources/particle_resource_monitor_v4.json`, binding original mathematical/profile hashes, actual collector/monitor versions, age semantics, numerical limits and bounded-study authorization. Do not mutate an old config and report its old hash or allow arbitrary profile overrides. Future full-run/artifact compatibility remains separately required.

## 4. Implement the bounded-age architecture

Use the already validated system one-shot `vm_stat` snapshot/parser and cached Darwin bindings. Retain displayed-free+inactive×actual-page-size; native speculative pages are not newly added. Do not enable diagnostic direct-Mach collection, a persistent interval stream, platform privileges or another unverified backend in this task. Primary field/type/arithmetic/ABI failures remain fail-closed; optional pressure unknown stays disclosed and verified warning/critical vetoes.

One owned sampling thread per worker performs a new system host query on a monotonic50ms schedule, without overlapping subprocesses or spinning. Publish an immutable sample with generation counter, query-start/query-end timestamps, actual backend and validation status. Use **now − query_start** as the conservative age upper bound; do not use publication/read time to renew age. Capture raw snapshots appropriately in bounded ignored evidence.

Before store construction and at launch/readiness/phase entry, require a fresh synchronous validated host observation. During batches, a host observation can be reused only if complete, provenance-valid, age≤100ms and no collector failure has been latched. Every before/after-batch guard still makes a fresh own-process RSS/native measurement and pressure query where available, checks all limits/deadlines and preserves pre/post optimizer accounting. The background thread also checks process limits, so blocked constructors/work do not lose periodic protection.

Refuse missing/expired/invalid samples; do not wait indefinitely, restart the worker or substitute a fictitious safe value. A startup/phase refresh must meet the100ms observation rule before permitting data/work. If scheduling or a slow2s-timeout query leaves no qualifying sample, stop fail-closed. This stronger age ceiling may make the shared host unsuitable at a particular moment; disclose it rather than loosening100ms automatically.

Latch collector/limit failures even if a later sample looks good. Preserve original main-thread signal and parent deadline interruption, cleanup of owned subprocesses/thread, phase minima/peaks, bounded journals and unknown telemetry. State that100ms bounds observation age at the guard, not guaranteed OS/Python termination latency; watcher scheduling, GIL and signal delivery remain practical limitations.

Keep publication locks short. Do not hold a batch guard lock over an external subprocess or let main/background calls issue duplicate queries. Preserve a synchronous auditable guard record before an optimizer step; retain flushed step reservation/completion semantics. Host generation and per-guard own-process measurements have distinct timestamps and scopes. Distinguish host query count, reused-host guards and actual fresh process checks; never count them all as independent host samples.

Prefer new narrowly scoped modules; reuse scientific reader/model/dev/audit functions. Keep the parent supervisor stdlib-only. All new executable helpers must be under source acceptance or explicitly included; no unstamped launcher in ignored data. No generic job scheduler, dashboard or app-management system.

## 5. Synthetic proof and one preregistered performance comparison

Add meaningful synthetic tests for100ms boundary/equality/expiration, missing/backward/nonfinite timestamps, publication/query age distinction, generation provenance, partial queries, collector error latching, low availability/pressure/RSS/native veto, per-boundary fresh process checks, slow/stalled sampling, deadlines during blocked work, concurrent publication/guards and owned cleanup. Verify every numerical limit and forbid synthetic fixtures from authorizing real readiness.

Use deterministic synthetic inputs and the existing478-parameter model/Adam/objective to show exact parameter/Adam/reconstruction/score parity with v3 on identical updates. Tests and ordinary CI must be synthetic and platform-independent, with no operational data/receipts required by fixtures.

Before timing, freeze one fixed paired matrix with **three predetermined repetitions per arm**, fresh matched workers, CPU1/1/seed1729/batch32/Nmax384, the same full/mixed synthetic physical batches and model-view transforms as Task0014,16synthetic updates plus8scoring batches. At most two physical batches resident. Include v3 and v4 complete monitored/audited workloads, plus a clearly diagnostic compute-only arm. No production no-monitor option.

Report every repetition and median, initialization/import/setup separately, workload wall/process CPU, host queries, per-guard checks/ages, lock/IO/audit costs and age/failure statistics. Use actual OS queries for cost, with separately named synthetic guard fixtures to exercise the workload under low shared-host availability. These fixtures are not real acceptance. Timing sections overlap; do not subtract them from historical749.343s or turn them into a new real extrapolation.

Bound the entire matrix≤120s and each dispatched arm≤30s including imports. Do not select best runs or iterate parameters to cross the target. Preserve failed arms; repeat only affected validation after a required source repair.

**Prerequisite for spending the new real budget:** all correctness/age/enforcement checks pass, exact numerical parity holds, and median complete v4 workload is≤one third of median complete v3 workload in this fixed matrix. This≥3× gate requires a substantial measured engineering change; it does not claim that the historical4.163× gap or180s real criterion is solved. If the criterion is missed/uncertain, do not create or execute another real slot; report the supported limitation and next decision.

Run appropriate full synthetic tests, lint/format, dependency/CPU smoke and required portability/history/link/whitespace checks. Generate fresh actual source-bound acceptance after final executable changes; freeze executable code before real execution. Any later source correction renews synthetic acceptance and never replays a consumed real phase.

## 6. Conditional single real engineering study

Only after section5 passes, prepare a fixed Task0015 execution manifest/ledger/output binding this actual prompt, unchanged model/profile, exact v4 implementation/observation manifest, fresh acceptance and consumed predecessor receipts. Refuse unexpected prior/later/inflight consumption; do not relax historical source validation to treat today's source as old acceptance.

This task grants one new bounded engineering attempt with≤96 started updates. Record original96, new started/completed/inflight and cumulative≤192. Use the same first1024 source-ordered frozen dev-training IDs, a newly initialized disposable model and original shuffle/seed. Do not continue historical dev weights, introduce new unique sample IDs or use engineering losses for model selection.

One fresh three-reading readiness spanning≥5s within30s precedes any real reservation/access. It must apply actual4.5GiB admission/native/RSS/pressure checks using fresh system snapshots, with no synthetic fixture. The worker independently rechecks launch and the v4 manifest/source/parent/token before data.

Attempt readiness at most once automatically after acceptance/benchmark if the prerequisite passed. If readiness is inadequate/unknown, save it and finish without reserving the real-study slot. No polling, requested cleanup or automatic external execution. Deliver one optional reviewed lightweight Terminal command for the same still-unreserved slot, which performs fresh readiness and checks at the user's chosen time; it must not require closing applications. Automatic and optional manual routes share one slot, never two allowances.

If ready, exclusively reserve before dispatch, then:

1. Fresh guarded dev reader: unchanged constructor, first64 IDs within the same1024 sample, two batch32 views, zero network/update,≤60s.
2. Fresh dev readiness, then the unchanged three-pass/96step/one-score disposable dev gate≤300s, all view/monitor costs included. Keep `2*(699957*max_train_pass_seconds/1024 +74749*score_pass_seconds/1024)≤180s` exactly.

No full-store custody replay solely as ceremony, full-population selection/calibration/test, fit/freeze/export or trained artifact. Previous full custody validates its historical scope; current full-run guarding remains a later prerequisite. Preserve all partial requests/started steps/failures. Once a real phase is reserved/dispatched, refuse retry/reset/alternate directory; any failure blocks dependent stages and consumes the attempt, even if fewer than96 updates finish.

A failed read-only readiness does not spend optimizer allowance; distinguish readiness receipts, attempt reservation and updates actually begun. Do not represent this as permission to loop. If automatic execution consumed the attempt, do not offer a manual rerun command. If manual execution is deferred, leave curated status pending and reconcile future receipts without replay.

## 7. Deliverables, memory and next dependency

Create:

```text
docs/particle-bounded-sampling.md
results/tables/final/task0015-particle-bounded-sampling-summary.json
```

Report the explicit observation-contract change, validation limits/freshness/enforcement, synthetic paired measurements, actual new readiness/phase access and optimizer counts, cumulative lineage consumption, v4 status and canonical pending state. If no real stage executes, state zero new custody/population/events/updates and why; engineering completion is valid with apps open and a deferred/unsupported real study.

Update living memory, README and handoff index in place. The proposed v3 rerun is superseded by this evidence-led v4 decision, not an absolute roadmap. Keep Task0013 failed749.343s result and Task0014 no-workload-gain result intact. Explain why changed observations needed an explicit version, why all numerical limits stayed fixed, and why synthetic speedup alone is insufficient. Preserve shared-Mac use as an enduring preference.

State the embargo:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

If actual v4 real dev passes every gate, propose **Task0016 — Actual-Policy Artifact Compatibility and Canonical Particle Background Training**, with explicit full-run authorization/current full-store guarding and fresh readiness. Do not execute it or repeat engineering dev merely because the task number changes. If host readiness prevents execution, use the delivered optional route rather than another identical implementation task. If synthetic or real throughput fails, identify the measured remaining blocker and a bounded engineering/runtime-budget decision; no automatic further optimization budget, time-limit relaxation or model tuning.

## 8. Required final Git section — last section of the response

Do not automatically stage, commit or push. End with exact commands for the actual branch/upstream: status/diff/index review, selective `git add --` of actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push. Exclude data, acceptances/ledgers/raw receipts/benchmarks, snapshots/caches and generated large outputs. Preserve unrelated work; do not stage inspected historical files or execute old prerequisite staging helpers. Prompt/handoff accompany the implementation.

Proceed with **Task0015 only**.
