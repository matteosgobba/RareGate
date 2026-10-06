# Task 0011 — Bounded Particle/Set Resource-Gate Recovery and Background Validation

## Initial metadata / scope

- Date: 2026-10-06 (Europe/Rome).
- Operational repository: `/Users/matteosgobba/Documents/GitHub/latent-trigger`.
- Branch/upstream: `main` / `origin/main`.
- Base: `96ef5aa86dea798966fa8d0e5cb38582ea84d70c`.
- Task0010 is **not committed**: thirteen prerequisite files are modified/new.
  Index empty, no unrelated changes identified; preserve prerequisite history.
- Initial hashes/content copies/diffs: `data/task0011-initial-state.json` and
  `data/task0011-prerequisites/` (ignored); overlapping maintained/source files
  saved before editing. Final Git guidance must stage initial prerequisite blobs
  separately, then Task0011 changes; ordinary whole-file staging cannot isolate
  overlapping edits.
- Read development/living memory and task evidence. No applicable AGENTS.md found.
- Original Task0010 ledger/workflow/audit/acceptance identities captured; original
  zero real-event/step/request failure verified. Final acceptance (after timing
  correction) matches initial source. Both original/final evidence preserved.
- Design/executable identities match Task0010 summary; scientific/resource
  choices remain immutable. Remote push/hosted CI unverified.

## Outcome

**Readiness still blocked.** Narrow recovery engineering and bounded readiness
work are complete. Three failed preflight readings reserved/dispatched no new
attempt. Every real particle stage remains pending. No evidence supports model
infeasibility, throughput failure or convergence failure.

Environment remains macOS26.6.2 ARM64, Python3.12.12/PyTorch2.14.1, 16GiB installed
RAM reported by read-only `memory_pressure -Q`. CPU only, one intra-op/inter-op
thread, deterministic algorithms. Remote push and hosted CI remain unverified.
No new dependencies, installation change, CI modification or synced-source edit.

## Evidence inspected and preserved

Read Task0009 report/design JSON/budget and Task0010 actual prompt/report/handoff/
curated gate summary, executable config, reader/model views, particle model/loss,
resource monitor, supervisor/worker, acceptance/tests, frozen preprocessing and
evaluation contracts. Inspected small manifests/config identities rather than
repeating costly store verification. The operational checkout is distinct from
any ChatGPT project mirror; no mirror content was edited.

Original Task0010 workflow has only a failed dev stage, error `Launch available
memory below 8 GiB.`, before store construction. Original audit has no population
requests. Curated count checks are exactly zero events/optimizer steps/passes.
The original launch recorded 3,967,254,528 available bytes. Both original and
final source-bound acceptance records were checked; the final record reflects
the documented correction making canonical total timing start after separate
dev. It matched the initial Task0011 source, then became stale for current code
as expected. Both were preserved; a separate Task0011 acceptance was generated.

Pinned **file-byte SHA-256** evidence (not scientific model hashes):

| Path | SHA-256 |
| --- | --- |
| `data/baselines/task0010-particle-attempt-budget.json` | `2a98539f5dc9e9f3653e57681613e19a920954c8fd250f954a5aec9cd974da70` |
| `data/baselines/compact-particle-set-autoencoder-v1/workflow.json` | `7897e03da20a853f842e201a492e95e08f6d5ac49c7025b3d0ae40cd49900d90` |
| `data/baselines/compact-particle-set-autoencoder-v1/dev/access-audit.json` | `a9400a16081e6a6c759a93bba45541b0c00c48ea9754333beb849a8da3d58c48` |
| `data/baselines/compact-particle-set-autoencoder-v1/dev/stage-result.json` | `1e36d40fe8df79c83ee6c821a9c59039f1621b01d485384a43a0a45deb7d69a8` |
| `data/task0010-synthetic-acceptance.json` | `535554d2673622bba6e9992de792a50bed7fb009dc5b4df5257d544bae3e6575` |
| `data/task0010-final-synthetic-acceptance.json` | `3037988a7975e6af040d3648b943930bf048b4b9648c193ab754b7f2f2b10020` |
| `results/tables/final/task0010-particle-set-gate-summary.json` | `f4d73f4a1018b711cea0f2fd187ffd591db32a76cd498a7e53d6007d65feaa22` |

Design canonical JSON hash remains `3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67`;
executable canonical JSON remains `48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b`.
Protected exact model/reader/config/design/preprocessing bytes are pinned in
the recovery module and curated summary. Historical Task0010 prompt/report/
handoff/summary and original output bytes were rechecked after changes.

## Narrow changes / decisions

- New `models/particle_recovery.py`: actual-suite-derived acceptance generation,
  bounded read-only preflight, strict readiness/predecessor checks, fixed exclusive
  Task0011 plan/output/ledger, supervised recovery dispatch and worker lineage.
- `training/particle_set.py`: extract strict vm_stat page parser, expose exact
  page/raw/GiB accounting and contextual counters, bound vm_stat command to2s.
  The available metric, RSS/native methods and resource thresholds are unchanged.
- `models/particle_background.py`: optional engineering lineage in reservation/
  workflow, checked by recovery workers. Default Task0010 consumed-ledger refusal,
  stage order/authorization, timers, real training/loss/scoring/loader/artifact
  semantics unchanged.
- New49 synthetic cases in `tests/test_particle_recovery.py`; old tests untouched.
- Curated factual summary, report, actual prompt/handoff, README/index and living
  memory updated. No success-shaped model/threshold/history files.

One fixed recovery route binds the saved prompt, predecessor failure/zero
consumption, original/final acceptance, exact design/config, fresh acceptance,
all readiness samples and remaining original limits. Engineering provenance
stays outside scientific identity. Exclusive plan creation precedes atomic
ledger `open("x")`, which precedes supervisor worker dispatch. Existing plan,
ledger or output refuses reuse; no force/task/output override. A failed preflight
does not prepare or reserve an attempt. No recovery plan/ledger/output was
created in this execution because readiness failed. The code will create the
required explicit plan only when the prepared manual route passes prerequisites.

## Read-only diagnosis / actual preflight

An initial contextual `memory_pressure -Q` observation reported16GiB/page16384/
free35%; later the single source-accepted preflight reported free39%. These are
contextual percentages, not substitute launch tests; no repeated readiness
workers were opened to seek a passing value.

Actual invocation:

```bash
.venv/bin/python -m latenttrigger.models.particle_recovery --preflight-only \
  --acceptance data/task0011-synthetic-acceptance.json \
  --preflight data/baselines/task0011-particle-preflight.json
```

Exit1, readyfalse. Started UTC2026-10-06T18:02:44.587990+00:00, sample offsets
0.028950833017006516 /2.5341194579959847 /5.03922729199985s, span5.010276458982844s,
whole context/sampling5.058918917027768s. Exact readings:

| Free / inactive pages | Available bytes /GiB | Peak RSS bytes | Native reserved /in-use bytes |
| --- | --- | ---: | --- |
| 4097 /189204 | 3167043584 /2.9495391845703125 | 357384192 | 180011008 /138924304 |
| 4397 /190056 | 3185917952 /2.9671173095703125 | 357433344 | 184205312 /138932368 |
| 4293 /193470 | 3240148992 /3.0176239013671875 | 357498880 | 184205312 /138940432 |

Every available value = (free+inactive)*16384; all below8GiB and4GiB, all RSS/
native reservation values pass6GiB/512MiB. No rounding changes arithmetic.
Timestamp/sample/raw command details are in the ignored preflight; small factual
fields are curated. Preflight file-byte SHA256
`5d31e61967d6027f576143b807c5c689d56d2932c2957545127328794dfa17ae`.

Current swap/direct installed-RAM sysctl and current RSS ps were permission
restricted. Marked unavailable; no extrapolation from cumulative swap counters.
`memory_pressure -Q` independently exposes installed RAM; vm_stat preserves
compression context (logical stored1828663, physical occupied418982 pages at
first reading). Categories overlap and were not summed. Peak RSS is getrusage,
not current RSS. Native reserved/in-use and synthetic allocation are distinct.
Apple's [memory guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac)
was read as primary support for pressure interpretation. No app/service cleanup,
cache purge, reboot, data deletion, load generator or app-content inspection.

Final source review removed the recovery callable's internal output-root override
(the CLI already had no override), closing an unnecessary programmatic route.
Tests now change the module root only in synthetic fixtures and reject a root
argument to the supported callable. The next full suite exposed a fixture-copy
ordering error:295passed/1failed; acceptance failed and no workspace was measured.
After copying the fixture prompt before patching its root, final full suite
passed296 and produced reviewed acceptance. Preserved records:

- First passed/preflight acceptance: `data/task0011-synthetic-acceptance.json`,
  SHA256 `b0cc64841f5363e0f9b9f048577c5597a5e8e15eb61782c328a08b2457048361`.
- Failed fixture renewal: `data/task0011-final-synthetic-acceptance.json`,
  SHA256 `43b65e4af329b4bcc6df9a5aaaa45063c685ebf0af34d4bab4e43a8439efd898`.
- Final current-source acceptance: `data/task0011-reviewed-synthetic-acceptance.json`,
  SHA256 `1cef87bb612eb7066e1f3e91cb01ba16ff84d3152c2198945098a012c8d79159`.

No host readiness was repeated to fish for a pass. The preserved failed preflight
is historical, bound to first accepted source; it cannot authorize the changed
source, and no real attempt was dispatched. The prepared manual commands require
a new preflight using final reviewed acceptance. Measurement formulas/ceilings
and actual three failed host observations remain unchanged.

## Unchanged scientific/resource policy and accounting

All architecture/input/objective/score and training/calibration fields retain
their exact Task0009→Task0010 mapping. Shared4→16→8, local2, mean8, decoder10→16→4,
478 parameters/1912FP32bytes, code2n+8. Weighted corresponding-particle distance
`(r0²+r1²+0.5*r2²+0.5*r3²)/3`, valid-count event mean, equal-event objective,
FP32 forward/FP64 residual/reduction, no angular projection/count loss.

Seed1729/default ordered initialization, exact Adam lr0.001/options, batch32,
CPU1/1 threads/determinism, workers0/tail included, full train shuffle, strict
min_delta0/patience20/max200/earliest ties, restored reload-score verification,
second fresh exact reproduction before freeze remain. Full fitting699957 and
selection74749 per epoch; calibration74823 only after all gates, higher quantile,
strict score>threshold and unchanged FPRs/intervals/KS/diagnostic profiles.

Ceilings remain launch8GiB/floor4GiB/RSS6GiB/native512MiB; dev300s/1024 unique
train events/3passes/96steps plus1same-sample scorepass; factor2 full-cycle
prediction and actual≤180s; fit≤36000s/run, postfit≤3600s/run, two-run canonical
total≤79200s. Loading/model-view preparation stays in pass times. No new selection
allowance, dev weights reused for canonical fitting, policy/device fallback or
hidden-worker dispatch. A cap without patience remains convergence unresolved.

```text
original Task0010 real workflow launches: 1 (failed before reader)
original real requests/events/optimizer steps: 0 / 0 / 0
Task0011 real recovery attempts reserved/dispatched: 0 / 0
Task0011 real requests/events/optimizer steps: 0 / 0 / 0
remaining dev unique events/passes/steps/score passes: 1024 / 3 / 96 / 1
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

No dev pass/extrapolation/full fit/restoration/reproduction/freeze/calibration/
profile stage ran. No real distribution, trained particle hash, threshold or
performance result exists. PCA and AE v1/v2 unchanged; compact AE v2 remains
canonical. No preprocessing/store rebuild or full custody check was run.

## Actual validation

- Initial targeted particle/recovery suite:125passed; subsequent new lineage/
  timeout/acceptance cases included in full suite below.
- `ruff check .`: passed; `ruff format --check .`:87files already formatted.
- `--acceptance-only --acceptance data/task0011-reviewed-synthetic-acceptance.json`:
  actual full pytest exit0, **296passed**, XML296cases/no skips. No acceptance
  flags manually flipped. Log/XML ignored and hashed by acceptance producer.
- Synthetic batch32/full384 measurement repeated through existing profiler:
  5228448bytes/4.986236572265625MiB,2synthetic Adam steps; not real optimization.
- Final acceptance file SHA256 `1cef87bb612eb7066e1f3e91cb01ba16ff84d3152c2198945098a012c8d79159`;
  accepted source-map canonical SHA256 `82d663c5aadae4f80b8b1f731f9e055ba3b7aa6c6c153edfba02533a87bb1083`.
  Current source acceptance and all7predecessor records reverified before reporting.
- `pip check`: no broken requirements; existing editable imports and CPU smoke
  passed. No reinstall/dependency/lock changes were needed.
- Synthetic cases exercise exact bytes/GiB, malformed/unavailable/equality/
  fluctuation, sample scope/time, failed-readiness no reservation, wrong predecessor/
  config/prior consumption/current-source rejection, fixed exclusive attempt,
  old-entry refusal, worker lineage and launch recheck, exception/timeout records
  and blocking, test/calibration guards and untouched model/config.
- Local relative documentation links, initial/prerequisite/ignored historical
  hashes, config mapping, no forbidden outputs/staged changes, final intended
  diff and `git diff --check` validated. Local checks do not establish hosted CI.

Unverified: real reader/process/workspace footprint, complete dev throughput,
full convergence/restoration/reproduction/calibration, remote push/hosted CI,
portability/export/latency. These remain future gates, not claimed successes.

## Files and Git separation

Intended **Task0011** files (11):

```text
README.md
docs/handoffs/README.md
docs/project-memory.md
docs/prompts/0011-particle-set-resource-recovery.md
docs/handoffs/0011-particle-set-resource-recovery.md
docs/particle-set-resource-recovery.md
results/tables/final/task0011-particle-set-recovery-summary.json
src/latenttrigger/models/particle_recovery.py
src/latenttrigger/models/particle_background.py
src/latenttrigger/training/particle_set.py
tests/test_particle_recovery.py
```

Five overlap uncommitted Task0010: README, index, memory, particle_background and
training/particle_set. Their original bytes are preserved in the thirteen-file
prerequisite snapshot. Remaining Task0010 files stay byte-identical and belong
in its separate prerequisite commit, including the unchanged reader/model/config/
tests/report/prompt/handoff/curated summary. No unrelated changes identified.

Ignored local outputs: initial-state JSON and prerequisite copies; actual
Task0011 acceptance/log/XML/profiler console; preflight/raw context/console;
`data/task0011-stage-prerequisites.py` (reviewable user-run staging helper);
validation notes/diff inspection under temporary paths. None belongs in Git.
The helper validates all original hashes/modes and empty index before selective
index staging of the initial blobs, leaves working-tree Task0011 changes intact,
and makes no commit/push. It was prepared but **not executed**. It refuses an
occupied index, preserving unrelated staged work for a separate review.

Manual sequence: review status/diffs/helper → stage original thirteen Task0010
blobs from snapshots → review cached/whitespace → commit
`feat: implement gated particle set baseline` → selectively add the eleven
Task0011 paths above → review cached/whitespace → commit
`fix: add bounded particle baseline recovery` → `git push origin main`.
No staging, commit or push was performed here. Exact commands are in task delivery;
ordinary whole-file staging before the prerequisite commit would mix tasks.

## Memory / limitations / follow-up

Living memory revision1.3 updates current state, resource evidence, milestone/
model status, durable recovery rationale, roadmap/dependency, open questions and
links in place; original user content, scientific state and short historical
revisions preserved. Explicitly separates readiness, launch, dev, convergence,
reproduction, freeze and calibration. README/index route to this current report;
historical Task0010 records remain unchanged.

Next dependency is user-controlled host preparation, followed by the exact
one bounded preflight/conditional recovery procedure in the
[report](../particle-set-resource-recovery.md#manual-host-preparation-and-conditional-run).
The real one-attempt authorization remains unused, and the actual worker can
still independently fail launch. If readiness cannot meet the original8GiB
requirement, propose a separate versioned engineering-policy review; no policy
relaxation/new task number/next execution here. Inference-foundation work waits
for the canonical baseline. Environment failure is not convergence failure.
