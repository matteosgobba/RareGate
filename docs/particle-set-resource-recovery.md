# Particle/set resource recovery — Task 0011

**Readiness still blocked; canonical particle baseline pending.** Three fresh-CPU
preflight readings all failed the unchanged launch requirement. No recovery
attempt was reserved, no processed reader opened, and no real optimizer step was
consumed. This establishes an environment blocker, not model infeasibility or
convergence failure. Task 0011 completes its bounded readiness/routing work.

See the [curated evidence](../results/tables/final/task0011-particle-set-recovery-summary.json),
[handoff](handoffs/0011-particle-set-resource-recovery.md) and
[actual authorization](prompts/0011-particle-set-resource-recovery.md).
The historical [Task 0010 report](particle-set-baseline.md), handoff, gate summary,
original failed ledger/audit and both acceptance files remain byte-identical.
Task 0010 is still uncommitted at Task 0011's base `96ef5aa`; separate prerequisite
snapshots preserve its original content for manual Git delivery.

## Diagnosis and stable preflight

The operational metric remains **(Darwin free pages + inactive pages) × actual
page size**, obtained from `vm_stat`; page size is **16,384 bytes**. GiB means
2³⁰ bytes, MiB means 2²⁰. No active, compressed, speculative or file-backed category
is added. The fresh worker uses CPU, one intra-op/inter-op thread and deterministic
algorithms, without constructing a model, reader or optimizer.

| Reading UTC, 2026-10-06 | Free pages | Inactive pages | Available bytes | Available GiB | Peak process RSS bytes | Native heap reserved bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 18:02:44.616937 | 4,097 | 189,204 | 3,167,043,584 | 2.9495391845703125 | 357,384,192 | 180,011,008 |
| 18:02:47.122025 | 4,397 | 190,056 | 3,185,917,952 | 2.9671173095703125 | 357,433,344 | 184,205,312 |
| 18:02:49.627160 | 4,293 | 193,470 | 3,240,148,992 | 3.0176239013671875 | 357,498,880 | 184,205,312 |

Sampling span **5.010276458982844 s**, total context/sampling work
**5.058918917027768 s**, within 30 s. Every reading failed both ≥8 GiB launch and
≥4 GiB continuing availability; every RSS/native-reservation reading passed its
≤6 GiB / ≤512 MiB ceiling. The unchanged monitor reports the launch failure first.
All samples/timestamps, raw `vm_stat`, heap in-use values and contextual command
outcomes are retained in ignored
`data/baselines/task0011-particle-preflight.json`. No favorable sample was selected.

Read-only `memory_pressure -Q` reported installed RAM **17,179,869,184 bytes
(16 GiB)** and its own free percentage **39%**. That percentage is contextual,
not the frozen readiness metric. Apple's pressure assessment uses free memory,
swap rate, wired memory and cached files. [Apple Activity Monitor memory guide](https://support.apple.com/guide/activity-monitor/view-memory-usage-actmntr1004/mac)
The first raw sample had 1,828,663 logical pages stored in the compressor and
418,982 physical pages occupied by it; these overlap and neither supplies launch
availability. Cumulative swapin/swapout and compression counters are not current
swap use or measured rates. Current swap use and direct installed-RAM `sysctl`
were permission-restricted; current worker RSS through `ps` was also unavailable.
The table reports `getrusage` **peak** RSS, not an invented current RSS.

Native reservation uses all malloc zones as the existing conservative bound;
heap in-use is separately recorded. The renewed synthetic batch32/full384
allocation measurement is **5,228,448 bytes (4.986236572265625 MiB)**, including
autograd temporaries/two synthetic Adam steps. It does not measure the real
reader/mapped-store/process footprint and cannot justify lowering 8 GiB. No
applications/services were closed, caches purged, data removed or pressure load
generated. No unrelated app content was inspected.

## Narrow recovery routing and preserved evidence

[`models/particle_recovery.py`](../src/latenttrigger/models/particle_recovery.py)
exposes mutually exclusive `--acceptance-only`, `--preflight-only` and `--recover`.
The readiness mode performs only bounded read-only accounting, records three
samples 2.5 s apart, applies every original ceiling, rejects unavailable/malformed
accounting, and preserves failed/partial deadline records. A 30 s signal deadline
and 2 s diagnostic-command timeouts bound the check. It never touches an attempt
ledger or store. Existing output records are not overwritten.

The one Task 0011 recovery route verifies pinned predecessor file hashes,
original zero consumption, exact protected model/reader/design/preprocessing/
executable bytes, current source-bound acceptance, all preflight samples and
the saved one-attempt prompt. It has fixed engineering paths:

```text
plan:   data/baselines/task0011-particle-recovery-plan.json
ledger: data/baselines/task0011-particle-attempt-budget.json
output: data/baselines/compact-particle-set-autoencoder-task0011
```

The plan binds original/final Task 0010 acceptance, failure/audit/ledger, design/
config identities, new acceptance and readiness record, authorization, remaining
limits and gate order. It is created exclusively before the original supervisor
atomically reserves the new ledger with `open("x")`, before worker dispatch.
Existing plan/ledger/output refuses duplicate preparation or dispatch. A failed
preflight creates none of these. An interruption preserves reservations/failure
evidence and blocks downstream work. There is no force/reset, arbitrary task
retry or alternate recovery output option. The old Task 0010 default still
refuses its consumed ledger even if given another output directory.

The supervisor adds engineering lineage to its ledger/workflow only; recovery
workers verify that lineage against the fixed plan, reservation, output and
accepted source. They still independently enter the original launch monitor
before any reader. Later stages retain the original parent stage-authorization
checks; the wrapper dispatches through the supervisor, never hidden workers.
Task/path/time/host values do not enter mathematical or trained scientific identity.
No model/loss/loader or artifact-validation semantics changed. The original
timing correction (canonical two-run timer starts after separate dev gate) remains.

## Immutable science and future execution limits

Design canonical JSON SHA-256:
`3aaccbccb2610f60647d4eca9fab5a368ce10cf812cc189c3e3394b4a4db6f67`.
Executable canonical JSON SHA-256:
`48b1c647cd8979860a9231e2aea59295054dedf6b4339b3100b5b5679649416b`.
Both exact specifications remain unchanged; neither identifies a trained model.

The shared encoder is 4→16 ReLU→8 ReLU, local 8→2 linear, masked mean8 context,
decoder [local2,context8]→16 ReLU→4 linear: **478 parameters /1,912 FP32 bytes**,
capacity2n+8. Input FP32[B,384,4]/boolean[B,384], nonempty prefix, frozen scalers
and deterministic retention remain. Corresponding-particle reconstruction and
canonical higher-anomalous score are
`mean_valid((r0²+r1²+0.5*r2²+0.5*r3²)/3)` with FP64 residual/reduction and equal
event weighting. Angular predictions stay unconstrained; no extra count term,
matching, clipping, score adjustment or hidden feature path.

Original dev allowance is wholly unused: first1,024 source-ordered frozen
dev-train IDs, batch32, ≤3 passes/96 steps plus one same-sample score pass,
≤300 s. Complete pass times include loading/model-view preparation. Require
`2*(699957*max(train_pass_seconds)/1024 + 74749*score_pass_seconds/1024) ≤180 s`.
Dev weights are discarded. No real timings or extrapolation are available here.

Conditional full CPU runs retain seed1729/default layer initialization, exact Adam
options/lr0.001, batch32/workers0/no dropped tail, seeded full shuffling, FP32
forward/FP64 objective, one intra-op/inter-op thread and determinism. Fit699,957
backgrounds; selection74,749 each epoch. Strict min_delta0, earliest ties,
patience20/max200, restored serialization/reload score verification and a second
fresh exact CPU repetition precede freeze. Calibration74,823 only after freeze:
target FPRs0.1/0.05/0.01/0.001, existing higher quantile, accept iff score>threshold,
unchanged summaries/KS/intervals/background profiles and independent result
reproduction. No threshold retuning or diagnostic feedback.

All original ceilings remain: launch8 GiB, continuing4 GiB, RSS6 GiB, native
workspace512 MiB, cycle180 s, fit36,000 s/run, postfit3,600 s/run, canonical total
79,200 s/two runs. A cap without patience is convergence unresolved; failed dev,
restoration/reproduction or resource checks stop later stages. No scientific or
resource fallback is authorized here. PCA and both AE generations remain intact;
AE v2 remains canonical for aggregates.

## Validation and access accounting

Actual full synthetic pytest: **296 passed** (49 added to the existing247).
Ruff lint/format, dependency consistency, existing editable imports and CPU smoke
passed. The acceptance-only command derives pass count/exit code from actual XML
and runs the existing synthetic allocation profiler after successful tests;
acceptance flags were not hand-edited. Final review removed an internal output-root
override, so the supported recovery callable and CLI both use fixed paths. The
first renewed suite then exposed a synthetic fixture reading its prompt after
patching the test root (295 passed/1 failed); the fixture was corrected and that
failed record preserved. The final suite again passed296. The single failed
preflight remains bound to its earlier accepted source and was not repeated or
reused for authorization; a new matching manual preflight is required. Fresh
current-source acceptance is
`data/task0011-reviewed-synthetic-acceptance.json` (SHA-256
`1cef87bb612eb7066e1f3e91cb01ba16ff84d3152c2198945098a012c8d79159`).

Tests cover exact page/GiB arithmetic, malformed/unavailable probes, equality,
fluctuation and timing, read-only readiness, refusal after failed readiness,
predecessor/config/consumption/source rejection, fixed exclusive reservation,
old-entry retry refusal, worker lineage and independent launch recheck,
exception/timeout preservation, unchanged limits/config and background/test
guards. Existing synthetic model/loss/permutation/mask/restoration tests remain.
Real reader footprint, dev throughput, canonical convergence/reproduction and
background calibration remain unverified. Hosted CI and remote push are unverified.
Documentation links, historical/config/output hashes, intended scope and whitespace
were checked locally; detailed checks are in the handoff.

```text
original Task0010 real attempts: 1 (launch failed)
Task0011 real recovery attempts reserved/dispatched: 0
Task0011 real population requests/events/optimizer steps: 0 / 0 / 0
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

No full-store verification, preprocessing rebuild, signal/test evaluation, MPS
particle training, export, quantization or inference benchmark was run. No
trained artifact, convergence figure, threshold table or score distribution was
created. Small curated evidence is readiness-shaped only.

## Manual host preparation and conditional run

The user can close their chosen unnecessary workloads and inspect Activity
Monitor's memory pressure. Do not lower the requirement or reclaim memory through
automated cleanup. After that deliberate preparation, run one bounded check using
the same definition. These commands preserve the failed sample file and only
dispatch if **all three** new readings pass:

```bash
cd /Users/matteosgobba/Documents/GitHub/latent-trigger
if .venv/bin/python -m latenttrigger.models.particle_recovery \
  --preflight-only --acceptance data/task0011-reviewed-synthetic-acceptance.json \
  --preflight data/baselines/task0011-preflight-after-preparation.json; then
  .venv/bin/python -m latenttrigger.models.particle_recovery \
    --recover --acceptance data/task0011-reviewed-synthetic-acceptance.json \
    --preflight data/baselines/task0011-preflight-after-preparation.json
fi
```

Source changes invalidate acceptance and require an actual fresh synthetic run
using `--acceptance-only` with a new ignored output path, then a new matching
preflight record. Existing records must never be removed/reset to retry. Do not
poll indefinitely for a favorable host reading. The actual recovery worker can
still fail its launch recheck; that consumes the one authorized real attempt and
must not be repeated automatically. No attempt has been spent in Task0011 so far.

The next dependency is user-controlled host preparation, then the bounded
readiness/conditional workflow above. If the host cannot meet8 GiB under ordinary
preparation, propose a **separate versioned engineering-policy review** of the
conservative host metric/reader-process footprint, without changing this policy
or automatically numbering/executing a new task. Inference work waits for the
canonical baseline gates. This task updated living memory in place to distinguish
preflight, recovery launch, dev feasibility, convergence, reproduction, freeze
and calibration, retaining unresolved model questions and original failure evidence.
