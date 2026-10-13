# Task0040 — Guarded Development Raw-to-Feature Measurement

## Metadata and reconciliation

- Date: 2026-10-13 Europe/Rome.
- Status: `parent_accepted_development_raw_feature_measurement`, sole real session consumed.
- Initial branch/upstream: clean `main` / `origin/main`, empty index.
- Actual base: `90868d6e75fcb298fa7e606dce00ad3457f8374e`, committed Task0039.
- Planning's `292a7e9`/20uncommitted paths were superseded by this verified commit;
  Task0039's historical base, resolver and acceptance were preserved.
- Memory1.34→1.35. Initial483tracked byte hashes exclude two operational model
  contents;480nonliving preserved, model paths unchanged in Git.17Task0039 and
  20Task0038nonliving paths preserved. Living README/memory/index updates separate.
- No stage/commit/push/hosted CI, Task0041, source acquisition, scientific amendment,
  held-out work, Task0037/0038/0039rerun or new operational model path.

## Authorization, implementation and preserved contracts

The attachment was saved verbatim as
[actual prompt](../prompts/0040-development-raw-feature-measurement.md),
SHA2566c7f486f2187f9d8c182d59fc0b34f5761ce468a638def8d83120a6eb9e3cc7d.
It prospectively authorizes the conditional one-session scope after fresh acceptance
and freezing, without another general confirmation. Separate config/provider/
controller grants do not flip Task0039's false authorization, weaken its synthetic
provider or reuse its consumed resolver/acceptance. No historical helpers changed.

Six additive helpers separate strict protocol/lineage/custody, authenticated
single-worker payload permission/durable accounting, fixed measurements, aggregate
reporting, explicit resource/lifecycle adapters and native controller/workers.
One validation entrypoint and three focused test modules accompany the config.
The parent stays stdlib-only; numerical modules import after thread environment and
fresh source/dependency/build grant checks. Owned outputs only; network/children,
model/store/preprocessing controller imports and unallowed data paths are refused.
No arbitrary path/role/grid/unsafe flag. Grants are plan/source/prefix/input/phase/
parent/token/deadline-bound and single-claimed before backend access.

Membership/golden/raw/transform/scientific/role lineage follows Task0039's complete
pins and the successful Task0020 preparation. That campaign's overall failure remains
failed. Every worker loads the original6999-ID file once, sorts ascending and proves
f80a9483…1024prefix, then loads original golden once and proves file/payload identities.
No filename/length-only alignment or derived-prefix substitution. Raw custody exactly
two full SHA256 passes, before payloads and after numerical/reporting workers; no MD5.
One readonly HDF handle per worker spans both gates/all cases, exact accepted schema/
Blosc links/cache, no axis reads or fourth metadata handle.

Provider selection returns precisely approved increasing IDs/all2101columns,
max128; slice only when the exact request is contiguous. No broad interval filtered
in Python. Background truth0 is a role guard only. Feature arithmetic reuses original
FP64source canonicalization→physicalFP32all-particle FP64 aggregates→frozen log/scaler
FP32output, preserving signed zero/phi/ties/mass guards and particles beyond384.
No model view/refit/inversion/empirical tolerance. Pre/post exact golden/repeat bytes,
raw window integrity and immutable inputs are required. After-timer checks reuse
owned window hashes/golden bytes without extra reads/constructions. Integrity hashes
remain ignored and are not published per-event fingerprints.

## Fixed execution and actual access

Workers1/3 ascend B1/8/32/128, read→feature→joint; worker2 reverses B/scope order.
Three approved logical windows per B, independent1/1/1warm and7/7/6timed cycling.
Pre/post each12B/window combinations:2raw reads/3feature constructions each.
Three raw buffers are loaded immediately before feature scope perB, reused/released
before advancing. Durable started/completed/inflight accounting precedes/follows
operations outside timer pairs; errors preserve actual returned rows/completion facts.

| Component | Raw requests / rows | Feature calls / rows |
|---|---:|---:|
| Timed+warm-up read/joint/feature | 552 / 23322 | 552 / 23322 |
| Feature raw preloads | 36 / 1521 | 0 / 0 |
| Pre/post gates | 144 / 6084 | 216 / 9126 |
| Total | 732 / 30927 | 768 / 32448 |

All requested raw rows returned, all768constructions completed, no inflight unknowns.
3membership loads20997metadata IDs inspected,3golden loads3072rows,1024unique approved/
golden rows,384unique actual raw rows,312geometric chunks. Raw hash2passes5816520818B;
3HDF handles opened/closed. All36cells/720timings/108warm-ups/72gates completed;
zero mismatching feature bytes. No operational raw/particles/features/labels exports;
only ignored timing/identity/accounting metadata and curated costs.

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
development_membership_loads_ID_records: [3, 20997]
golden_feature_loads_rows: [3, 3072]
approved_IDs_unique_requested_raw_rows: [1024, 384]
raw_selected_requests_requested_returned_rows: [732, 30927, 30927]
raw_timed_preload_gate_presentations: {timed: 20280, warmup: 3042, preload: 1521, gates: 6084}
feature_constructions_row_presentations: [768, 32448]
raw_byte_hash_passes_bytes: [2, 5816520818]
raw_HDF_handles_opened_closed: [3, 3]
timing_cells_timed_warmup_calls: [36, 720, 108]
exact_feature_parity: passed_zero_mismatching_bytes
new_heldout_signal_selection_calibration_accesses: 0
processed_store_constructions: 0
operational_model_forward_reconstruction_optimizer_calls: 0
new_fingerprint_or_stored_score_array_loads: 0
new_scaler_fits_threshold_calibrations_AUC_AP_significance: 0
downloads: 0
operational_measurement_session: parent_accepted_development_raw_feature_measurement
```

YES describes permanent historical exposure, not new held-out requests. Actual
raw/golden/membership numeric and feature work is openly reported.

## Cost findings and interpretation

All60observations per B/scope are pooled from three actual20call cells. Mean whole
batch milliseconds read/features/directjoint:

| B | Read | Features | Direct joint | Joint µs / actual selected row |
|---:|---:|---:|---:|---:|
| 1 | 0.436654 | 0.137628 | 0.592085 | 592.085 |
| 8 | 2.858273 | 0.453940 | 3.457469 | 432.184 |
| 32 | 11.679953 | 1.561234 | 13.532818 | 422.901 |
| 128 | 45.142758 | 5.778030 | 50.012520 | 390.723 |

The separately measured selected-read scope costs more than feature construction
on these sparse windows. It includes permission/point-selection/materialization/
label guard, so cannot isolate disk or decompressor cost. Joint boundary was timed
directly; it is not reconstructed by summing means/medians or combined with Task0038.
Whole-batch joint cost rises withB; amortized selected-event cost decreases over
this fixed matrix, without selecting a policy or asserting stationary throughput.

B128joint means47.940/50.004/52.093ms across workers; read41.813/47.529/46.086,
feature5.529/6.223/5.582. All slow calls retained: maxima52.347083read/7.585208feature/
58.980916joint ms.20serial observations/cell/shared caches/fixed order/host drift
limit tail inference; no distributions, production-p99/stall-frequency/causal claims.
Cell CSV retains mean/population SD/linear p50/p95/p99/min/max, timer/order/window/
repetition, throughput and useful-event denominator. Three real figures inspected,
allpoints/no clipping/logaxes explicitly labeled; lines connect fixed points only.

Cache1MiB/521/.75 confirmed, one persistent handle/worker, pre gates and preloads
warm it. Raw hash warms OS pages: warm-context study, unknown other cache state,
no cold-I/O/physical-bandwidth claim.312chunks/26307713520B≈24.501GiB no-cache
upper bound is inherited geometry, not measured decompression/I/O/cache misses.
Neighboring chunk decoding does not expose neighboring Python rows. h5py3.16.0/
HDF52.0.0/plugin7.1.0/build pinned; BLAS/Accelerate enforcement passes, effective
Blosc threads unknown despite requested1. Timermach_absolute_time()/41.666667ns
resolution recorded before pairs, independently of Mach continuous deadlines.
Continuous-minus-timer differences666…36709ns include instrumentation outside pairs;
no subtraction or inferred suspension cause. Periodic monitoring may interfere.

## Validation and prospective freeze

100focused/2310full/2310portable pass in artifact-free source copies; lint/format/
pip-check pass, no installs.236source/config/prompt/test/old-summary bindings,
43package versions/31native binaries. Two native synthetic runs accepted, preliminary
6.528403s and final6.861521s; each runs the same732reads/768feature constructions on
fixtures plus24setup raw reads/24setup constructions3072rows and24fixture writes.
One initial pytest collection failure used a reserved parameter name; corrected
before tests/operational work. Preliminary focused80/93passes reflect additions.
Final acceptance covers all new code; old2210tests do not supply that acceptance.

Historical instrumented research subset perfull/portable:85fixture model instances,
31forwards8710rows,31reconstructions,2toy optimizer updates/2toy calibrations.
Other historical fixture/native activity is outside this instrumentation. No global
zero-forward/update claim; new helpers and native fixtures are model-free.

Final acceptance:
`data/task0040-validation/d9d3127d67864a0886fc1761099fc64b/software-acceptance.json`
SHA508a95a0b7e432ffaf800369d8c988447bebcff5e131305c01a26352132b02d5.
FreezeSHA9f45a9acedfe3c665667fa3a857e7205544e95fca092cca88d164868530205fb,
actual prompt and exact inputs/counts/limits bind final source before reservation.
Operational namespace:
`results/benchmarks/task0040-development-raw-features/76ef4bc0a464437bbf0c7046243a6557`.
Plan/anchor/workflow/receipt hashes are in the curated summary. No source/config/test/
prompt changes after reservation; reports/living documents updated separately.
No real dry run, extra gate, payload replay, source repair or allowance reset.

## Continuous resources and lifecycle

Whole19.498497s/prereq1.495500s/reserved18.003004s/post-custody1.330165s/
final0.141319s, overshoot0. Bodies4.863738/4.948585/5.208784/report1.233463s;
dispatch through exit/reaping4.881756/5.004512/5.235015/report1.281219s
(the summary has exact accepted values). Cleanup perbody≤0.000143s.
Four normal exit0/reaped/source-output-identity/resource/deadline acceptances, then
assertion release before parent acceptance. Body complete alone was insufficient.

Worker numerical RSS≤83017728B, reporting-inclusive≤96452608B; native≤77201408B,
controller33882112B. Parent+maxserial worker native upper sum123338752B. Explicit
raw buffers6454272B, conservative enforced owned-array bound59145216B; actual
intermediate allocation attribution is not measured. Owned output5627071B at acceptance.
Caps60prereq/180each numerical/60report/45postcustody/15final/720reserved/780whole,
cleanup2inside; RSS1GiB/native512MiB/controller128MiB/arrays64MiB/journal16MiB/
log1MiB/owned128MiB pass. Postcustody is reserved slack, not another payload run.

Workers1454WARN advisory/0NORMAL/0CRITICAL/unknown; parent2220NORMAL/3989WARN/
0CRITICAL/unknown. Invalid-primary veto never triggered; no global RAM query/floor.
Querygap≤0.061234s, terminal resourcegap≤0.056575s disclosed; exit/deadline supervision
continues after sampled monitoring ends. Seven active owned idle-sleep assertion
observations; helper−15/reaped/release/absence verified, display sleep permitted,
no persistent settings. Historical Task0025 failed process-exit campaign remains failed.

## Deliverables, boundaries and next brief

Report, prompt/handoff, strict config, six additive helpers, validation driver,
three tests,36row cell table, curated summary and three figures plus living3updates:
22intentional paths. All operational arrays, raw timing sequences/window hashes/
ledgers/receipts/acceptance/build maps remain ignored; no per-event extracts curated.
Task0032baseline/Task0033exploratory/Task0036unresolved/Task0034gates/exposureYES3/
particle192consumed canonical-deferred and accepted Task0037/0038 evidence unchanged.

Concrete next decision: separately design/authorize a joint selected raw→unchanged
features→original native PCA/AE adapter/four original decisions measurement on these
same development windows. Pin membership/source/model/threshold identities and
exact feature/decision gates, phase/read/forward budgets, fixed cache/thread/timer,
continuous/sleep/resource/normal-exit acceptance and fresh synthetic freeze before
one new attempt. No test/signal/selection/calibration source, scientific metric,
acquisition, deployment policy or sums-of-medians shortcut. Task0041 not launched.
Transport, actual streaming/queueing and device paths remain unmeasured.

## Reproducibility and Git

Validation command already completed:
`.venv/bin/python scripts/validate_development_raw_measurement.py`.
The real CLI command already completed with the above fresh acceptance. The anchor
and prerequisite marker reject repeated actual invocations; do not rerun/reset them.
Final delivery review passed:22intentional paths,480nonliving hashes unchanged,
original prompt exact, fresh acceptance still current, complete CSV/JSON coverage,
relative links/figure and source identities/exclusions checked; index empty and
main/origin/main verified. The ignored final-review.json retains this evidence.
Hosted CI and user commit/push are unverified.

Actual branch main/upstream origin/main, same base90868d6, index empty. Review and
manual selective commands below curate only Task0040. Task0039 is committed; no
previous-path staging group is needed. Do not use `git add .` or include ignored data.

```bash
git status --short --branch
git diff --check
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git ls-files --others --exclude-standard
git add -- \
  README.md \
  docs/project-memory.md \
  docs/handoffs/README.md \
  docs/development-raw-feature-measurement.md \
  docs/prompts/0040-development-raw-feature-measurement.md \
  docs/handoffs/0040-development-raw-feature-measurement.md \
  configs/benchmarks/development_raw_measurement_v1.json \
  scripts/validate_development_raw_measurement.py \
  src/latenttrigger/benchmarks/development_payload_measure.py \
  src/latenttrigger/benchmarks/development_payload_native.py \
  src/latenttrigger/benchmarks/development_payload_protocol.py \
  src/latenttrigger/benchmarks/development_payload_provider.py \
  src/latenttrigger/benchmarks/development_payload_reporting.py \
  src/latenttrigger/benchmarks/development_payload_runtime.py \
  tests/test_development_payload.py \
  tests/test_development_payload_grants.py \
  tests/test_development_payload_runtime.py \
  results/tables/final/task0040-development-raw-feature-cells.csv \
  results/tables/final/task0040-development-raw-feature-summary.json \
  results/figures/final/task0040-development-raw-feature-scope-cost.png \
  results/figures/final/task0040-development-raw-feature-chronology.png \
  results/figures/final/task0040-development-raw-feature-geometry.png

git diff --cached --check
git diff --cached --stat
git diff --cached --name-only
git diff --cached
git commit -m "feat(benchmarks): add guarded raw-to-feature measurement"
git push origin main
```

These are manual commands; Codex has not staged, committed or pushed.
