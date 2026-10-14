# LatentTrigger — Task0045: Paired Natural-Partial Raw-to-Decision Measurement

You are continuing **LatentTrigger**. Perform **Task0045 only**.

## Objective and explicit new authorization

Measure the missing natural-partial service boundary identified by Task0044. In one prospectively fixed campaign, compare:

- **natural_m:** selected first m approved raw events → unchanged frozen features → owned natural m-row CPU service → original four decisions/result retention.
- **full_B_control:** the complete containing B-event window through the same full natural B-row chain.

These paired measurements quantify costs at the listed partial occupancies against contemporaneous full-B controls. They do not execute padding or select a batching/deployment policy.

This actual prompt explicitly authorizes **one conditional Task0045 operational session**, after new final-source synthetic validation, emitted-record admission, immutable freeze and prerequisite checks. It authorizes the exact existing development membership/golden loads, approved raw selections, feature construction, frozen model loading/inference and operation budgets below. Bind the actual prompt to the final plan; no additional general confirmation is required for that scope.

No new population/acquisition, held-out/signal/selection/calibration access, processed-store construction, optimizer/fitting/scaler/threshold changes, stored scientific scores/new event fingerprints, scientific metrics, device/transport execution, simulator replay, policy selection or Task0046. Previous consumed allowances remain consumed.

## 1. Verify and preserve current state

Read applicable instructions, `docs/development.md`, living memory, Task0044 actual prompt/config/report/summary/handoff and billing limitations, Task0043 accepted source/chain/identity/measurement contracts, Task0038 original natural packing/service and supported cases, and Task0039/0040 feature/membership lineage. Inspect existing clocks/guards/admission/cleanup and original model loaders before implementation.

Planning inspection on 2026-10-13 Europe/Rome found clean `main` aligned with `origin/main`, HEAD `a8094adc697895a2f8ef05b6a24f0e1aeb86603c`, committed Task0044 and empty index; memory 1.39. Recheck actual Git. Task0044's `d4b92e55...` and earlier task-time bases remain historical.

Save actual prompt/initial handoff:

- `docs/prompts/0045-natural-partial-raw-decision-measurement.md`
- `docs/handoffs/0045-natural-partial-raw-decision-measurement.md`

Preserve historical helpers/configs/prompts/results/receipts/markers/snapshots, including Task0044's accepted replay and disclosed source-loader failure. Task0043 accepted/consumed, Task0041 failed/consumed, Task0042 software-only and Task0036 unresolved remain unchanged. Task0045 is a distinct allowance, not a retry, amendment or relabeling of those tasks.

Use additive Task0045 helpers, strict config such as `configs/benchmarks/development_partial_raw_decision_v1.json`, `data/task0045-validation/` and `results/benchmarks/task0045-natural-partial-raw-decisions/`. New task and validation owner are 0045 throughout. Do not mutate historical namespace/owner guards, globals or budgets to make them admit this scope.

## 2. Bind the exact original sources and CPU candidates

Inherit and verify all Task0039/0040/0043 byte, role, scientific and lineage pins: split/dev manifests, transform config, accepted membership resolver and successful Task0020 preparation. The overall Task0020 campaign remains failed. No filename/length-only alignment or cached-prefix substitute.

| Numerical source | Required identity |
| --- | --- |
| `data/analysis/lhco-rd-v1/dev_train_background.npy` | C-order little-endian int64 [6999], 56,120 bytes, SHA256 `2662f0762cf57e39156b0e5c6b1c8e7ac7279a2ecc98c33b2ed69d67a964c781` |
| Sorted first 1024 ID payload | SHA256 `f80a9483f5ddafcac0e05d9fd6de757e5bbfe9e805f65ced1c0aa801cc266f1a` |
| `data/raw/lhco/6466204/events_anomalydetection_v2.h5` | 2,908,260,409 bytes, SHA256 `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6` |
| `results/benchmarks/task0020-frozen-cpu/prepare/input.npy` | C-order little-endian FP32 [1024, 8], 32,896 bytes, file SHA256 `7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`, payload SHA256 `2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05` |

Each of three fresh workers loads the original 6999-ID source once, validates domain/uniqueness/sorted prefix, and loads the original golden once. Approved universe stays 1024 unique IDs. The complete union actually requested must be exactly the same **384 raw rows** as Task0043, not an enlarged population.

For nominal B = 1/8/32/128, keep original containing-window starts `0`, `floor((1024−B)/2)`, `1024−B`. At each start p, natural_m reads approved IDs `[p:p+m]`; full_B_control reads `[p:p+B]`. Do not recenter partial windows using m, substitute contiguous raw row numbers or construct partial input by slicing a previously read full raw buffer. Every side makes its own exact HDF selection.

Bind complete original model entries from `configs/benchmarks/prepared_batch_service_v1.json`: model/config/result file and scientific hashes, eight ordered features, training provenance and threshold calibration relationship. PCA remains six-component FP64; AE remains 155-parameter FP32 CPU v2 in eval/inference mode. Public SSE is FP64, all four original comparisons strict `score > threshold`. Load each candidate/threshold set once per worker: six of each total. No pickle/new model/backend/threshold recalculation.

Exactly two full raw SHA256 passes, before numerical payload access and after numerical/reporting stages: 5,816,520,818 byte presentations. No MD5 pass/copy/numeric scan. One readonly HDF handle per worker across both candidates/pre/post gates: three handles, with original schema/filter/hard-link/cache checks before/after on the same handles; no fourth metadata-only opening. Dataset `/df/block0_values` remains FP64 [1100000, 2101], chunks [62, 2101], exact Blosc 32001 pipeline.

## 3. Freeze the partial cases and unchanged natural service

The 15 distinct nominal (B,m) cases are:

| Nominal B | Actual natural m values |
| ---: | --- |
| 1 | 1 |
| 8 | 1, 2, 7, 8 |
| 32 | 1, 2, 8, 31, 32 |
| 128 | 1, 2, 32, 127, 128 |

The quarter-full points are deliberate exploratory engineering anchors informed by Task0044. This is a sparse prescribed grid, not a cost curve for every possible m or independent scientific confirmation.

Reuse unchanged `canonicalize` → `physical_aggregates` → `standardized_aggregates` with frozen `Parameters`: FP64 source sort/wrap before physical FP32 conversion, all valid particles in FP64 aggregates before any 384 truncation, exact mass/log/scaler rules and final FP32. Background label column 2100 validates role and stays outside features. No particle view/scaler/store path.

Preserve original `prepared_service.service` and packing. Distinguish **nominal B**, **actual rows processed**, and the helper's **service_B validation argument**. For natural_m, use service_B = nominal B when `(B,m)` is an existing supported Task0038 case. Only for `(32,8)` use service_B = 8; for `(128,32)` use service_B = 32. Those are already supported `(8,8)` and `(32,32)` natural calls, which allocate/copy exactly m rows. Full_B_control always uses service_B = B and m_actual = B. Freeze/test this explicit mapping; do not change the historical case validator or pretend the helper padded to nominal B.

All executable forward shapes are previously exercised natural shapes; no new arithmetic policy, tolerance, kernel optimization or padded strategy. Retain all B outputs for the full control, including its extra real B−m rows. Those are physical control work, not dummy events. At m=B the two sides perform identical intended work; keep these null-comparison cases to expose ordering/noise, without expecting equal durations.

Start each timer immediately before checked selected read; stop after owned natural packing, original public score/four decisions and result copies. File/model loading, window preparation, hashes/parity, durable accounting and explicit guard/thread queries are outside pairs. Retain computed features for the after-timer check without recomputation. No shared/preloaded raw window, feature-only substitute, delayed asynchronous execution or second standardization.

## 4. Paired order, exact gates and complete operation budget

Three workers, both original candidates. Workers 1/3 use PCA then AE and ascending `(B,m)` order; worker 2 uses AE then PCA and reverses the complete case list. All three logical windows use the original B-based starts above.

Each candidate/case: three warm-up pairs, then 20 timed pairs. Reset window cycle and side ordering per phase. Pair i uses window i mod 3 and natural_m→full_B_control for even i, reversed for odd i. Thus warm windows 1/1/1 and timed windows 7/7/6; timed order is balanced 10/10. Both sides of a pair use the same containing window and candidate, with separate reads. No timing-driven ordering or sample search.

This is **90 paired candidate/case/repetition groups, 180 timing cells, 1800 timed pairs/3600 timed calls and 270 warm-up pairs/540 warm-up calls**.

Each candidate block has pre gates over ascending cases/windows, its timing schedule, then identical post gates. At each `(B,m,window)` gate context:

1. Run one golden-only natural service for each side, using its exact actual shape/service_B.
2. Run each side's complete raw-to-decision chain twice.
3. Require exact feature/golden bytes and exact same-shaped score/mask/reference/repeat bytes. Post references equal pre and inputs/parameters/thresholds remain unchanged.

Natural_m and full_B_control may have different score bytes for their common rows because forward shapes differ. Do not impose new cross-shape bit identity, compare one side against the other as its oracle, enlarge tolerances or add real FP64 diagnostic/affine model passes. These are integration gates against the same-shaped unchanged public service, not a new universal kernel certificate.

| Component | Calls | Actual row presentations |
| --- | ---: | ---: |
| Timed complete chains, both sides | 3600 | 145,920 |
| Warm-up complete chains, both sides | 540 | 21,888 |
| Pre/post complete-chain repeats | 2160 | 87,552 |
| All selected reads / feature constructions / chain services, each | 6300 | 255,360 |
| Golden-only reference services | 1080 | 43,776 |
| All public adapter / decision services | 7380 | 299,136 |

540 paired gate contexts / 1080 side gate records. Per worker: 2100 raw reads/constructions on 85,120 rows, 360 references on 14,592 rows, 2460 services on 99,712 rows. Per candidate across workers: 3690 services on 149,568 rows; 3690 AE forwards/reconstructions and 3690 PCA reconstructions separately. Four decisions per row produce 1,196,544 Boolean values.

Also three original membership loads/20,997 inspected records/3072 selected records, three golden loads/3072 rows/1024 unique, six frozen model/threshold instantiations, three HDF opens/closes, two custody passes, no preloads/padding/dummy rows.

A pure planner must derive/test counts, mapping, side/window/ordering identities, request-set deduplication and per-component/per-candidate conservation before freezing. Every timed/warm-up output is compared outside the timer with pre-established same-shaped references, without extra reads/feature/model calls. Durable nested progress preserves requests, actual returned/completed rows and inflight uncertainty on failure.

## 5. Separate closed authority and fresh final validation

Existing Task0043 providers allow only full B and have smaller fixed budgets. Do not widen them or convert old grants. Create a closed Task0045 provider/permit covering nominal case, actual side rows, exact prefix/window, candidate/model/threshold identities, parent/phase/token/deadline and the new 2100/2460 per-worker budgets. Unauthorized or oversized requests fail before backend selection; contiguous slices only if their complete interval equals requested IDs.

Use generated HDF/membership/golden/model/threshold fixtures only during software validation. Test quarter mapping, exact owned natural packing, actual full-control extra rows, m=B intended identity, same-shaped reference gates, wrong IDs/side length/source/state, denied adjacent rows, labels/nonfinite/padding/full-particle semantics and unchanged strict decisions. Test full paired schedule, independent side reads, exact counts, nested failure at each stage and no extra setup/diagnostic inference.

Test producer→serialized record→strict outer admission→immutable freeze/claim→controller→worker together, including wrong task/owner/scope/case/side/packing identity, stale source/native build/prompt/config, missing/failed checks, altered receipts/logs/freezes, unsafe paths, duplicate/foreign/consumed fixture permits and failures before downstream effects. Keep independent controller/worker checks. Do not mock admission to unconditional success or invoke any actual old/new real path as a test.

Run focused/full/portable artifact-free suites, lint/format/dependencies and bounded native synthetic integration of all 180 cells and paired gates/counters/cleanup/reporting. A generated bootstrap may create native software evidence; final immutable record must then pass the actual emitted-record admitted native roundtrip with a noncircular sidecar receipt. Failed software acceptance/freezing stops before any real controller invocation.

Fresh acceptance binds actual Task0045 prompt/config/final sources/tests, installed-package identities, NumPy/HDF/Blosc/Torch CPU native binaries and canonical JSON-string Torch build identity, exact scope/plan/budgets and successful evidence. Task0044's 2749 tests/269 bindings/36 pins do not cover the new physical chain; replay-native identities do not replace Torch/HDF acceptance. No install/update/backend substitution.

Set environment before numerical imports; enforce Torch intra/inter = 1, deterministic CPU, supported BLAS/OpenMP/Accelerate limits and requested `BLOSC_NTHREADS=1`. Decoder threading remains unknown. Restore owned state/resources on exit; fresh process teardown owns the one-time interop setting. Parent is stdlib-only; allow only declared source/model/metadata paths. Core module presence does not permit ProcessedStore construction/iteration, fitting, optimizers/network or extra children.

No operational IDs/golden/raw numerical loads, real model instantiations, raw hash or HDF opening during validation. Fixture/setup/legacy model forwards and toy updates are real separate work, honestly counted.

## 6. One bounded real campaign

After final software/roundtrip success, freeze executable/config/prompt/build. One checked Task0045 entry verifies record/freeze/actual authorization, claims its own prerequisite allowance and performs allowed byte/header/lineage custody plus first raw SHA pass. Numerical loads start only with fresh worker grants after immutable execution plan/reservation. Never continue after a failed precheck.

Once real prerequisites begin, any failure consumes this allowance, even before timing. No retry/reset/changed code, alternative rows/thresholds, tolerance repair, additional diagnostic or second physical campaign. Preserve failed peaks/partial records and actual requested/returned/completed/inflight facts.

Fixed ceilings: prerequisites 60 s; three numerical workers 180 s each dispatch through normal exit/reaping; reporting 60 s; post raw custody 45 s within reserved slack; finalization 15 s; reserved session 720 s; whole session 780 s. Cleanup 2 s inside worker caps; stop numerical work before cleanup slack. Larger workload feasibility is not proved by earlier campaign speed.

Worker RSS 1 GiB/native reserved 512 MiB/controller RSS 128 MiB; explicit owned numerical arrays 64 MiB; combined guard/access journals 16 MiB per process and 64 MiB across the session, log 1 MiB per worker; all owned output 128 MiB. The journal allocation explicitly accommodates the larger paired ledger without weakening numerical/process memory caps. Derive the live-array/reference envelope for this paired grid; no retained raw buffers. Report bounds separately from sampled allocation accounting, including parent-plus-serial-worker conventions.

Temporary owned idle-system-sleep assertion verified throughout stages, then released/reaped/confirmed absent on all exits before acceptance. Display sleep allowed; no persistent settings/cache purge/app closure/global RAM floor. Continuous clock includes suspension and supervises exit independently of sampled resource checks. WARN advisory; CRITICAL/invalid primary veto; optional unknown context/query/terminal gaps explicit.

Timer implementation/resolution recorded before timing; synchronous integer-ns pairs and independent continuous timestamps. All calls/workers/slow observations retained, no subtraction/trimming or fastest-run selection. Cache remains 1 MiB/521 slots/w0 = 0.75 per persistent handle. Alternating sides, pre gates, repeated windows and prehash warm the context; they do not reproduce partial-only streaming cache history or cold I/O.

Derive any repeated chunk/decode geometry from this 6300-read plan, rather than copying Task0043's different bound. Geometry is not measured physical I/O, decompression or cache misses; effective decoder threading remains unknown.

Parent acceptance requires exact scope/counts/gates/input-model-threshold identities/final raw hash, handle closure/restored state, normal exits/reaping, caps/deadlines/source-output identities and assertion release. Reporting reads owned aggregates/receipts only, never source arrays/models. A body-complete receipt is not parent acceptance.

## 7. Curated results and interpretation

Produce:

- `docs/natural-partial-raw-decision-measurement.md`, actual prompt and detailed handoff.
- Strict config, additive planning/provider/admission/worker/controller/reporting helpers, focused tests and validation entrypoint.
- `results/tables/final/task0045-natural-partial-raw-decision-cells.csv`.
- `results/tables/final/task0045-natural-partial-raw-decision-pairs.csv`.
- `results/tables/final/task0045-natural-partial-raw-decision-summary.json`.
- At most three readable inspected figures: natural/full joint costs, signed paired differences/ratios across occupancy and chronological variability.

180 cells retain 20 timed observations each; 90 paired groups retain 20 differences/ratios. Record candidate/repetition/nominal B/m/actual rows/service_B/side/window/order/pair ID, count/min/max/mean/population SD/linear p50/p95/p99. Pool actual observations only within the same candidate/B/m/side, never average percentiles or collapse distinct input/cache contexts.

Define difference `natural_m − full_B_control` and ratio `natural_m/full_B_control` from each matched timing pair, with order labels and all unfavorable cases. For natural service, amortize by its m actual rows. For full control, distinguish measured cost/B physical rows from hypothetical bill/m useful replay events. At m=B, paired deviations describe finite order/host effects; no requirement that costs match exactly.

Do not infer a universal upper bound, partial cost for unmeasured m, fitted/interpolated curve, selected policy or production p99. Full controls process extra real events; the contrast includes different raw selections/features/model shape and cannot isolate disk, decoder, packing or model causality. Costs are conditional on sparse warm windows and the paired schedule.

Exact integration parity is checked against same-shaped golden service, not natural-versus-full reconstruction attribution. Publish mismatch evidence and cost, not score distributions/development anomaly rates/scientific efficiencies. No raw/particle/feature/score/mask/event-ID exports; sequences/grants/plans/receipts/ledgers/integrity metadata remain ignored.

Task0043 full costs and Task0044 hypothetical bills are historical context. Do not subtract campaigns or silently rewrite/replay Task0044 with these sparse new points. A later separately authorized version must define treatment of every unmeasured occupancy and changed cache/input assumptions before using partial timings. Task0045 does not measure arrivals/queue/transport or confirm a signal source.

If the real campaign is rejected, preserve actual partial evidence and explicit unmeasured/rejected coverage; no accepted full matrix or real cost figure is fabricated. Reporting-only curation cannot justify another model/data run.

## 8. Italian handoff, memory and manual Git

Update README/index/relevant memory from verified 1.39. Preserve Task0043 accepted/consumed, Task0044 accepted synthetic replay, Task0041 failed/consumed, Task0042 software-only, Task0036 unresolved, unchanged scientific gates/exposure/failures/deferred particle state.

The self-contained Italian handoff must explain actual partial/control cost findings, quarter mapping and paired order, parity, access/load/forward/reference counters, fresh admission/native validation, continuous resources/lifecycle/release, limitations and next decision. Preserve YES/YES/YES historical exposure. New raw/feature/frozen-model inference/reconstruction/decisions are authorized actual work and must not be called zero.

Report actual source rows separately from repeated presentations: memberships/golden, 1024 approved/384 raw unique, side/case reads/requested/returned rows, feature completions, six frozen model/threshold instances, timed/warm/gate/reference calls, per-candidate computations, decision Boolean values, HDF checks/closure, byte custody and exact parity. Planned totals are not actual values on failure. Operational optimizer/scaler/calibration/scientific/fingerprint/held-out/download counts remain zero; historical fixture work is separately disclosed.

Use a specific status such as `parent_accepted_natural_partial_raw_decision_measurement` only with complete Task0045 parent gates. Keep failed-prerequisite/failed-consumed evidence when applicable. No hosted CI/global-zero fixture-model claims, automatic replay or Task0046.

Finish with actual Git review/selective staging/staged review/Conventional Commit/push commands for verified branch/upstream. Do not stage, commit or push; preserve unrelated work and keep ignored evidence/arrays/sequences out of staging.

Proceed with **Task0045 only**.
