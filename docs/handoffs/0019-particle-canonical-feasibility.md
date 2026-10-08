# Task 0019 — Canonical Particle Feasibility and Project Progression Decision

## Metadata

- Date: 2026-10-08, Europe/Rome.
- Phase: engineering decision / documentation only.
- Initial status: evidence inspection and validation pending.
- Final status: completed locally; documentation-only decision, awaiting user commit.
- Branch/upstream: `main` / `origin/main`.
- Verified base/HEAD: `5da90944d48dd05fc761d23dad77b85c1fa2da60` (Task0018).
- Initial working tree and index: clean; no unrelated edits observed.
- Environment: shared local macOS workspace; no scientific execution authorized.
- Prompt: [original user specification](../prompts/0019-particle-canonical-feasibility.md).

## Objective and scope

Consolidate existing particle timing, full-custody resource and shared-host evidence;
record one current operational decision and an implementation-ready Task0020 CPU
benchmark brief for frozen PCA / compact AE v2. Preserve existing contracts,
accepted source, artifacts, receipts, ledgers and historical handoffs. No new
readiness, workers, population arrays, custody replay, updates, training, scoring,
calibration, inference timing, configurations or execution permission.

## Initial handoff

Saved before substantive decision work. Task index ends at0018; verify the
underlying receipt lineage and metadata next. Reconcile memory's Task0018
awaiting-commit statement through this later record without rewriting the
original Task0018 handoff. Arithmetic, identity checks, links and final diff
review remain pending. Do not stage, commit or push automatically.

## Changes and files

Seven intended files; no prerequisites or unrelated edits to stage:

- [Original prompt](../prompts/0019-particle-canonical-feasibility.md), saved before substantive work.
- This handoff, with the initial record above preserved and completion below.
- [Decision report and Task0020 brief](../particle-canonical-feasibility.md).
- [Curated summary](../../results/tables/final/task0019-particle-canonical-feasibility-summary.json).
- [README](../../README.md): present local deferral and concrete hardware next step.
- [Living memory](../project-memory.md): revision1.12, current decisions/roadmap/risks in place.
- [Handoff index](README.md): Task0018 commit confirmation and Task0019 outcome.

No executable, test, active configuration, dependency, CI, scientific artifact,
accepted-source record, ledger, receipt or synced source changed. No Task0020
code/configuration/prompt/acceptance/campaign was created. Its brief is contained
in Task0019's report and curated summary as inactive future implementation work.

## Evidence and history reconciliation

2026-10-08 confirmation: `main` tracks `origin/main`; verified HEAD/local tracking
ref is Task0018 `5da90944d48dd05fc761d23dad77b85c1fa2da60`, after `b194050`.
No network push/hosted CI was established. The original Task0018 handoff and
earlier records stay byte-identical. Current memory/index reconcile its historical
awaiting-commit text through this later dated record, without rewriting history.

Read development protocol/living memory first; no applicable AGENTS.md found in
repository or ancestor locations. Reviewed relevant Task0009–0018 design,
configuration, report, summary and handoff evidence, plus existing small models,
manifests, receipt lineage and accepted source. Only small-file inspection and
hashing: **metadata verification, not fresh population/payload verification**.
No ProcessedStore construction, NPY/raw read, multi-gigabyte hash or custody replay.

Task0018 acceptance file hash
`1a81fe8181b1bd430f0d55ccdb13363e912d8948d1347eee6e2944ec7515e047` and its74
source/test hashes match current bytes and the saved pre-execution source map.
Execution plan file hash
`ce175b39027a4b149e45b986d229dd58e437b0d616c133d1fec9954ba029c24b` is distinct
from canonical JSON hash
`6783a29979d45b435927be9b4e012f314561db404d11b43ea83b17e6dd148f49`.
Anchor binds the latter and remains `reserved_no_retry`. Workflow is
`characterization_completed_original_throughput_failed_canonical_blocked`;
all phase results agree, with parent dispatch metadata separately present in
workflow. Final resource receipts show owned threads closed. Original96 plus
additional96 started/completed, zero inflight, cumulative192/192, remaining0.
Anchor plus completed workflow means **consumed**, not permission to finish/retry.
Preflight permission stdout is historical. No anchor rewrite/reset/replacement.

Original full-custody lineage verified directly: Task0013 plan→invocation→phase
reservation→passed result→audit→workflow, including plan/slot/acceptance/profile/
model/audit hashes and the activation's reader-result hash. Audit records one
completed custody operation, zero population requests/views/updates/test accesses.
Workflow embeds the same custody result plus parent receipt metadata, then fails
dev throughput. Task0014 curated reconciliation agrees; it is not a new run.
The report/summary record original small receipt hashes for future inspection.

## Technical decision and results

**Defer local canonical particle execution under unchanged contracts.** Retain
its design/implementation for a later explicit full-store/time/environment policy.
No scientific rejection or convergence outcome follows. Particle work does not
block frozen aggregate hardware measurements or other independent project work.

Recomputed from original Task0018 `dev/dev-gate.json`, with slowest of all three
training passes,1024 divisor,699957/74749 populations and factor2 unchanged:

| Planning quantity | Verified value |
| --- | ---: |
| Full train+selection projection | 240.72835947066707s |
| Excess over180s | 33.73797748370393% |
| 200 projected cycles per run | 13.373797748370391h |
| Two runs plus full1hpostfit allowance each | 28.747595496740782h |
| Arithmetic10h capacity before other overhead | 149 cycles |

These are small-sample projections, not full epochs, guaranteed deadlines or
convergence forecasts. Postfit1h is an allowance, not measured cost.180s×200=10h
and two(10h+1h)=22h leave no separate startup slack at equality. Startup/full
verification/cleanup/parent and other costs need explicit accounting.180s is the
training engineering gate, not measured trigger-inference latency. Preserve
max200/patience20/min_delta0, strict selection/earliest ties, best restoration
and independent reproduction. Do not reduce horizon to149 or assume early stop.

Measured resources remain distinct: dev387989504bytes=370.015625MiB RSS and
188399616bytes=179.671875MiB whole native, below dev512/256MiB. Historical full
custody3351019520bytes=3.120880126953125GiB RSS and206831616bytes=197.25MiB native,
below full6GiB/512MiB with2.879119873GiB/314.75MiB headroom (47.985331%/61.474609%).
Custody is not sustained training; process ceilings do not guarantee machine-wide
headroom. RSS/native overlap and virtual mappings are not resident allocations.
Short-dev unknown/WARN permission does not establish multi-hour suitability.

Historical749.343s>180s and present240.728s>180s failures remain failed; Task0014
no workload gain and Task0015 synthetic2.14×<3× remain unchanged. Current local
deferral is adopted; resource/time revisions and alternative environments are
inactive. Illustrative300s×200 gives16h40m cycle allowance/run,35h20m for two plus
postfit **before** additional costs, not a threshold adopted or measured gain.
No alternative execution host is verified in inspected project evidence.

## Next implementation task and dependencies

The live index initially ended at0018; next after this decision is **Task0020 —
Frozen PCA/AE CPU Inference Benchmark Foundation**, subject to rechecking live
state when started. Its [brief](../particle-canonical-feasibility.md#task0020-implementation-brief)
defines actual frozen PCA and compact-autoencoder-v2 artifact/config/result paths,
scientific hashes, scaler/input/score contracts and all calibrated thresholds.
AE v1 remains history. No refit/recalibration/model export/test access.

Concrete proposed protocol: CPU PyTorch1intra/1inter/effective BLAS1, PCA FP64/AE
FP32/both FP64 SSE, first1024 source-ordered dev-training aggregate inputs;
batches1/8/32/128/1024,20warm-ups/200timed invocations per scope, three fresh
workers/model in fixed alternating family order. Reconstruction, precomputed
reconstruction score/decision and canonical public adapter+decision separate from
input/loading/preparation; p50/p95/p99 and all workers reported, no best selection.
Canonical numerical checks before/after, preregistered tolerances and zero frozen
threshold decision mismatches. Proposed new-scope worker1GiB RSS/512MiB native,
parent128MiB,600s total including preparation60s/six60sworkers/aggregation30s,
fresh/periodic guards and parent deadlines. Synthetic boundary/identity/pressure/
deadline/partial/crash/cleanup/no-retry tests required within Task0020 before a
separately authorized single campaign. No reuse of particle profile or slot.
Provenance, shared-host/unknown context, ignored raw outputs and small curated
summaries are specified. It permits implementation without another standalone
readiness or monitor-design task.

Remaining particle uncertainties: full-epoch scale/locality, long-run RSS/native/
pressure and interference, stopping horizon, postfit cost, scientific usefulness.
Future execution needs precise versioned limits/enforcement/scientific-artifact
compatibility/finite authorization/failure handling; Task0019 fills no measurement
gap and grants no new allowance. No app closure/reboot/cache or swap manipulation/
privilege workaround/dedicated window/polling dependency. MPS, ONNX/CoreML,
quantization, trigger simulation and final evaluation remain later tasks.

## Validation and reproducibility

Actual documentation-only validation uses the existing Python environment and
standard library; no scientific module imported or population array reopened:

- Recomputed timing/budget/unit/headroom arithmetic from original small receipts;
  checked original/curated timing agreement, config contracts and inactive300s
  example consistency.
- Parsed JSON with nonfinite values rejected; recomputed canonical scientific
  model/results/dev/full manifest/split identities and config file/content hashes;
  verified model-calibration links, exact155 FP32 AE parameter metadata, PCA k6,
  best AE epoch381 and all frozen thresholds. No fresh payload hashing.
- Verified current74-entry accepted source map/source freeze/plan binding,
  anchor/workflow/audits/progress/cleanup and original full-custody lineage.
- Compared the initial405 small tracked/engineering entries:402 outside the
  three intended overlapping files remain byte-identical, including historical
  handoffs/configs/artifacts/acceptances/receipts/ledgers/logs and manifests.
- Checked local links/anchors and report/summary values, intended seven-file
  scope, ignored temporary outputs, empty index, actual branch/upstream/HEAD and
  `git diff --check`; also checked new-file trailing whitespace explicitly.

Local metadata helper: `.venv/bin/python data/task0019-validate.py`; final factual
output: ignored `data/task0019-final-validation.json`. Initial snapshot is ignored
`data/task0019-initial-state.json`. These are validation helpers/metadata only,
not a supported launcher, new source acceptance or execution permission. Initial
helper path/schema assumptions were corrected against actual receipt fields;
final checks pass.670 synthetic tests were **not rerun**; no new acceptance or
hosted CI/remote push claim. No app/hardware-readiness experiment occurred.

```yaml
new_real_population_accesses: 0
new_optimizer_updates: 0
remaining_granted_dev_updates: 0
canonical_training_authorized: false
active_particle_resource_or_time_contract_changed: false
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## Rejected alternatives and limits

Rejected another readiness/monitor trial, idle-Mac prerequisite, new particle
slot, disposable-weight reuse, silent180s/10h/22h relaxation,149epoch horizon,
assumed early stop/convergence, full-custody-as-training validation and different
raw reconstruction scales as discrimination. The larger-budget and future-host
routes remain explicitly inactive proposals, not an unresolved next-step menu.
Selected route is Task0020 CPU foundation on existing frozen models.

## Git delivery

No staging, commit or push performed. All seven files belong to this one
documentation task. Operational data, accepted-source records, ledgers/receipts,
logs/snapshots/caches/scientific arrays and unrelated work are excluded. The index
remains empty; no resulting Task0019 commit or successful push is invented.

```bash
git status --short --branch
git diff --stat
git diff
git diff --cached --stat
git diff --cached
git ls-files --others --exclude-standard
git add -- README.md docs/project-memory.md docs/handoffs/README.md docs/prompts/0019-particle-canonical-feasibility.md docs/handoffs/0019-particle-canonical-feasibility.md docs/particle-canonical-feasibility.md results/tables/final/task0019-particle-canonical-feasibility-summary.json
git diff --cached --stat
git diff --cached
git diff --cached --check
git commit -m "docs: defer canonical particles and plan frozen CPU benchmarks"
git push origin main
```
