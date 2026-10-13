# LatentTrigger — Task0040: Guarded Development Raw-to-Feature Measurement

You are continuing **LatentTrigger**. Perform **Task0040 only**.

## Objective and authorization

Complete the payload controller for Task0039's fixed development raw-to-feature design, validate it synthetically, then execute **one conditional operational measurement session** on the approved development-training rows.

This actual prompt is the separate prospective authorization required by Task0039. After successful final-source validation, prerequisite checks and plan freezing, it permits the exact membership/golden loads, approved raw row selections, frozen feature constructions and timing matrix specified below. Bind this prompt to that finalized plan; no further general confirmation is required.

It authorizes zero new source acquisition, raw/processed-store rebuilding, alternative membership, test/signal/selection/calibration access, model execution, reconstruction, optimizer updates, fitting, scaler refitting, threshold calibration, fingerprint computation or scientific evaluation. Historical synthetic regression models remain a separate permitted test scope. Do not launch Task0041.

## 1. Verify current state and preserve the completed foundation

Read applicable instructions, `docs/development.md`, memory, Task0039's actual prompt/design/config/summary/handoff and accepted resolver provenance, original preprocessing contract/pure feature helpers, and relevant scoped clock/guard/validation utilities.

Planning inspection on 2026-10-13 Europe/Rome found `main` tracking `origin/main`, HEAD `292a7e924ffaacfd058a56e1f84dd9a404de06e9`, committed Task0038, empty index and 20 intentional uncommitted Task0039 paths; memory 1.34. Recheck actual Git because the user may have committed meanwhile. Preserve Task0039/unrelated bytes and separate new shared README/memory/index updates. No prior commit requirement or automatic staging.

Save actual prompt/initial handoff:

- `docs/prompts/0040-development-raw-feature-measurement.md`
- `docs/handoffs/0040-development-raw-feature-measurement.md`

Task0039's resolver remains accepted/consumed, its config prospective and unauthorized for payloads. Do not flip its authorization flag, weaken its synthetic-provider block, monkeypatch it to read real events, reuse its resolver grant or overwrite its acceptance. Add a separate Task0040 payload protocol/provider/controller.

Preserve accepted Task0038/0037 results and all historical inputs/helpers/receipts. Task0036 remains `unresolved_no_acquisition`; Task0034 scientific gates unchanged; Task0032 complete, Task0033 exploratory, evaluated samples permanently exposed, Task0025 failed, particle192/192 consumed/canonical-deferred.

## 2. Bind the exact existing sources and membership

Inherit and verify Task0039's complete byte/scientific/lineage pins. Required numerical sources:

| Source | Identity |
| --- | --- |
| `data/analysis/lhco-rd-v1/dev_train_background.npy` | C-order little-endian int64 [6999], 56,120 bytes, SHA256 `2662f0762cf57e39156b0e5c6b1c8e7ac7279a2ecc98c33b2ed69d67a964c781` |
| Sorted first 1024 ID payload | SHA256 `f80a9483f5ddafcac0e05d9fd6de757e5bbfe9e805f65ced1c0aa801cc266f1a` |
| `data/raw/lhco/6466204/events_anomalydetection_v2.h5` | 2,908,260,409 bytes, SHA256 `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6` |
| `results/benchmarks/task0020-frozen-cpu/prepare/input.npy` | C-order little-endian FP32 [1024, 8], 32,896 bytes, file SHA256 `7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`, payload SHA256 `2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05` |

Each of three fresh repetition workers loads the original 6999-ID source once, repeats the accepted source-order/prefix checks, and loads the golden array once. No reading a derived prefix as a substitute for original lineage or selecting different IDs. Role/order binds through split/dev manifests, frozen config, successful Task0020 prepare and accepted Task0039 resolver, not merely filenames/lengths.

Use one readonly HDF handle per worker from before its pre gate through its post gate. Verify schema/cache on that owned handle without a fourth metadata-only handle: `/df/block0_values`, FP64 [1100000, 2101], chunk [62, 2101], exact accepted Blosc 32001 filter pipeline, unambiguous hard links and no external/virtual sources.

Raw custody has exactly two full SHA256 passes: one before numerical payload access and one after the numerical workers, 5,816,520,818 byte presentations total. Freeze their stages and accounting; they are not selected-row requests or timed I/O. Reject source mutation. No new MD5 pass, acquisition, source copy or whole numeric scan.

Reject missing/altered/symlink/ambiguous sources. No `ProcessedStore`, broad preprocessing/split validator, axis arrays, labels/multiplicities/fingerprints outside returned approved raw rows, other membership files, model artifacts or scientific score arrays. Source/config text and allowed byte custody are separately scoped.

## 3. Implement the smallest guarded payload path

Use a separate strict config such as `configs/benchmarks/development_raw_measurement_v1.json` and additive Task0040 helpers. Bind Task0039's frozen future design and pure scheduling/geometry/approval/feature code; preserve its historical validator and consumed metadata route.

Implement an owned parent-issued payload grant covering exact source/dataset, accepted role/prefix, expected identities, maximum 128 rows per request, phase, deadline, counters and source/dependency/build map. Invalid/foreign/stale/duplicate grants or unauthorized IDs must fail **before** backend value selection. No `--unsafe`, arbitrary path/role/grid or generic bypass flag.

The new provider selects precisely the approved increasing IDs and all 2101 columns, with a contiguous slice only if every row in it is exactly requested. Return owned contiguous FP64 rows of the expected shape; label column 2100 must be 0. Truth validates role and never enters features. Internal neighboring-chunk decoding does not authorize exposing neighboring rows to Python.

Reuse unchanged `canonicalize` → `physical_aggregates` → `standardized_aggregates` and frozen `Parameters`. Keep source FP64 sort/wrap/signed-zero/padding validation before the physical FP32 cast, all valid particles before truncation to 384, FP64 aggregates/mass guard, exact logs/scalers and final FP32 cast. No model/particle-view/fingerprint path, approximate inverse, arithmetic optimization or empirical tolerance.

Enforce owned writes and narrow read/import/network boundaries. Inspect reused helpers for Task0039's metadata-only prohibitions, 60 s worker/32 MiB storage limits and fixed output assumptions; do not mistake them for the new 180 s/128 MiB payload policy. Adapt through new validators, not historical mutations.

## 4. Execute the unchanged fixed schedule

Three workers, batch sizes 1, 8, 32 and 128 and three scopes:

1. `selected_hdf_read`: checked selection/read/decompression/owned materialization/background-label guard; excludes feature construction/file opening.
2. `frozen_feature_construction`: full unchanged chain and input guard from one of three preloaded owned raw windows; no HDF read inside timer.
3. `selected_raw_to_features`: the same direct selected read through owned FP32 features, timed jointly.

Windows are deduplicated positions `0`, `floor((1024−B)/2)` and `1024−B` in the approved 1024-ID sequence. Workers 1 and 3 ascend B and use read→feature→joint; worker 2 descends B and uses joint→feature→read. Each scope/B has three warm-ups and 20 timed calls, cycling windows/resetting per phase: one warm-up per window, then 7/7/6 timed calls per window. No timing-driven schedule/cache/sample changes.

For feature-only scope preload three approved raw windows once per B and release them before advancing B. A single worker HDF handle/cache persists through gates/all cases. Do not retain all raw source rows or create a full processed store.

Pre and post gates, each of 12 B/window combinations: one selected read followed by two feature constructions with repeat/golden equality, then one joint read+construction with golden equality. No extra real dry run or early payload validation outside this reserved session.

Fixed expected totals:

| Component | Calls/requests | Selected row presentations |
| --- | ---: | ---: |
| Timed+warm-up raw read/joint | 552 | 23,322 |
| Feature-only raw buffer preload | 36 | 1521 |
| Pre/post raw gates | 144 | 6084 |
| All raw selected requests | 732 | 30,927 |
| Timed+warm-up feature/joint constructions | 552 | 23,322 |
| Pre/post feature constructions | 216 | 9126 |
| All feature constructions | 768 | 32,448 |

36 cells / 720 timed / 108 warm-up invocations; three membership loads / 20,997 ID records; three golden loads / 3072 rows; 1024 approved/golden unique rows; **384 unique actually requested raw rows**, 312 geometric chunks. Verify these counts against the accepted Task0039 planner instead of hand-editing them.

After-timer output checks may compare with pre-established aggregate raw-window hashes/golden-position bytes without extra HDF reads or feature recomputation. These bounded block-equality hashes are benchmark integrity checks, not a new event-fingerprint computation; do not publish them as per-event records. Account for checks separately and keep them outside timers. Do not accidentally enlarge the 732/768 operation budget to verify every observation.

## 5. Require exact operational parity and immutable inputs

Before timing in each worker, every scheduled raw window must be finite, valid background, exactly approved/in order, and produce byte-exact golden-position FP32 features. Repeat construction must be byte-exact. Perform the identical post gate; require unchanged membership/prefix/golden/transform/source identities.

Zero mismatching output bytes is required. The pure chain is unchanged and Task0039 synthetic cross-B parity passed. On an actual parity/label/schema/identity failure, preserve exact failure location and bounded diagnostics without publishing event values, reject the session and stop. No changed tolerances, clipping, new scalers, replacement rows, fingerprint scan, repair or operational retry.

Source/ID integrity and operational feature parity are distinct gates. Passing them does not measure scientific generalization, establish a confirmation source or authorize held-out evaluation.

## 6. Record timer, cache and decoding limits prospectively

Record service timer implementation/resolution in each worker **before** timing, with synchronous start/stop and a separate continuous supervision clock. Integer-ns storage does not imply 1 ns resolution. Timers include the scope's input guards/allocations; window lookup preparation, hashes/parity checks, durable ledger and resource queries are outside pairs. Sampled monitoring can still interfere.

Retain every observation, chronological phase/window order and outlier; no overhead subtraction, fastest worker selection or stall deletion. Do not fit a distribution or claim production p99 from 20 serial calls/cell. Fixed order, pre gates, buffer preloads and persistent caches affect results and must be stated.

Require effective HDF raw chunk cache: 1 MiB / 521 slots / w0 = 0.75. Keep existing NumPy/HDF5/h5py/hdf5plugin/native identities bound through fresh acceptance. Report BLAS/Accelerate enforcement separately from unknown effective Blosc decoder threading; `BLOSC_NTHREADS=1` alone is not proof. No backend/thread/cache-size search or dependency installation.

Distinguish selected rows returned, repeated calls, geometric chunks and unknown physical I/O/decompression/cache hits. Task0039's no-cache upper bound of 26,307,713,520 bytes (approximately 24.501 GiB) is a planning bound, not newly measured bytes. Entire compressed chunks may be decoded mechanically, including neighbors, without exposing their rows. No full chunk buffers may be returned then filtered as a shortcut.

The opening raw byte-hash warms OS pages. Fresh handles do not establish cold I/O; this is a warm-context selected-read study with unknown other cache state. No purge, eviction, app closure, privileged settings or machine-wide RAM floor. The joint raw-to-feature timer is measured directly; separate medians are not an end-to-end measurement.

## 7. Fresh software validation and freeze

Cover authenticated payload permission, exact allowed-ID selection before backend, source/header/links/cache/filter refusal, same-length wrong membership/golden, denied other roles/arrays/model/network access, finite/label/padding/full-particle semantics, exact parity and mutation failures.

Test the complete schedule/counts, raw buffer lifetimes and 64 MiB owned-array ceiling; durable started/completed/inflight records for membership/golden/HDF/read/construction calls; exact reporting/owned output scope; atomic one-winner reservation; timeout/suspension/CRITICAL/accounting/assertion loss/release; body-complete versus parent-accepted and failed process exit. Use generated HDF/golden/membership fixtures only.

Run targeted tests, full/portable artifact-free suites, lint/format/dependencies and bounded native synthetic integration of all three scopes, cache/filters, gates, counters and parent lifecycle. Historical fixture model activity is separately disclosed. Do not numerically load operational IDs/golden/raw data or construct operational feature batches during software validation.

Create fresh final source/config/test/dependency/native-build acceptance, binding Task0039 unchanged artifacts, actual authorization prompt and exact finalized plan. The old 2210 tests / 223 bindings do not cover new payload code. Freeze before the dedicated Task0040 reservation; this prompt then authorizes the conditional actual session.

## 8. One bounded operational session

Use `results/benchmarks/task0040-development-raw-features/` with one durable canonical attempt anchor, distinct from the consumed Task0039 resolver. Prerequisites may verify byte/header/source/acceptance/build/support and the first full raw SHA256 pass; numerical membership/golden/raw loads start only after reservation and fresh per-worker grants.

Fixed limits: prerequisites ≤ 60 s; three numerical workers each ≤ 180 s dispatch through normal exit/reaping; aggregate reporting ≤ 60 s; parent finalization ≤ 15 s; reserved session ≤ 720 s; whole session ≤ 780 s. Cleanup ≤ 2 s inside every worker cap. Operation stops before cleanup slack; parent deadlines remain independent through process exit.

Explicit process caps: worker RSS 1 GiB / native reserved memory 512 MiB / controller RSS 128 MiB; owned numerical buffers 64 MiB; journal 16 MiB per worker, log 1 MiB per worker, total owned output 128 MiB. Plan the post-numerical raw hash within an explicit remaining stage/deadline. It is final byte custody, not an extra payload run.

Temporary owned idle-system-sleep assertion must be verified before reservation and during stages, then released/reaped/confirmed absent on all exits. Permit display sleep, change no persistent power settings. Continuous deadlines include suspension. WARN advisory; CRITICAL/invalid-primary-accounting veto; pressure unavailable and monitoring/terminal gaps disclosed; global available RAM contextual.

Workers durably record requests before numerical operations and completion afterward. Interrupted calls retain requested/returned/completed counts and inflight uncertainty. Retain actual failed peaks, partial timings, HDF closure and thread/buffer cleanup. Do not lose evidence by claiming every requested row was returned after a failure.

Reporting opens owned aggregate tables/accepted receipts only; it never reopens raw data, golden features or memberships. Accept final outputs only with exact matrix/access conservation, all pre/post gates, unchanged final source hash, normal exits/reaping, source/output identities, resource/deadline checks and assertion release.

One actual reserved session only; failures consume it even before the first timing cell. Failed prerequisites also terminate this task without repeating real-source custody or starting a replacement attempt. No retry/reset/reselection or executable change after reservation. Ordinary synthetic software repair before freezing is permitted and versioned. Do not run another real diagnostic to investigate a failure.

## 9. Curated outputs and interpretation

Produce:

- `docs/development-raw-feature-measurement.md`
- Task0040 prompt/handoff and strict execution config.
- Additive payload/controller/worker/reporting helpers and focused tests/validation entrypoint.
- `results/tables/final/task0040-development-raw-feature-cells.csv`
- `results/tables/final/task0040-development-raw-feature-summary.json`
- At most three readable inspected figures for per-scope/B costs, repetition/chronological variation and selected-row/chunk geometry context.

Every cell retains count/min/max/mean/population SD/p50/p95/p99 using fixed linear quantiles, scope/window/order/repetition/timer context, whole-batch and amortized selected-event cost. Combine repetitions from their actual pooled observations, never averaged percentiles; retain all workers/outliers. Twenty observations/cell and shared cache/schedule limit tail interpretation.

Preserve raw timing sequences/receipts/ledgers/plans/acceptances and selected-ID metadata in ignored artifacts. Do not persist raw event matrices, reconstructed physical particles, per-event feature arrays, labels or other source extracts. Curated reports contain only aggregate cost, identity/gate/access/lifecycle evidence and limitations.

Explain measured raw read versus feature construction versus directly timed joint cost, parity outcome, cache/decoder/neighbor-chunk limits and useful-event denominators. Do not infer disk bandwidth from selected payload bytes, describe the fixed sparse-dev sample as a detector stream, or sum Task0038/0040 medians into measured whole-chain latency.

Update README/index/memory from verified revision 1.34. Preserve historical baseline, Task0038/0037 costs, unresolved Task0036 and unchanged scientific claim. The next engineering brief may consider scoped service-sequence replay or a separately measured joint preprocessing+inference path; do not implement it automatically or select a deployment policy.

The Italian handoff should explain actual outcomes, scope/cost findings, all access counts, fresh validation, continuous resources/lifecycle/release, limitations and next decision. Include:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
development_membership_loads_ID_records: ACTUAL_COUNTS
golden_feature_loads_rows: ACTUAL_COUNTS
approved_IDs_unique_requested_raw_rows: ACTUAL_COUNTS
raw_selected_requests_requested_returned_rows: ACTUAL_COUNTS
raw_timed_preload_gate_presentations: ACTUAL_COUNTS
feature_constructions_row_presentations: ACTUAL_COUNTS
raw_byte_hash_passes_bytes: ACTUAL_COUNTS
raw_HDF_handles_opened_closed: ACTUAL_COUNTS
timing_cells_timed_warmup_calls: ACTUAL_COUNTS
exact_feature_parity: ACTUAL_STATUS
new_heldout_signal_selection_calibration_accesses: 0
processed_store_constructions: 0
operational_model_forward_reconstruction_optimizer_calls: 0
new_fingerprint_or_stored_score_array_loads: 0
new_scaler_fits_threshold_calibrations_AUC_AP_significance: 0
downloads: 0
operational_measurement_session: ACTUAL_STATUS
```

Do not claim zero numerical/event access: this prompt authorizes new raw development reads and feature computations. YES preserves historical exposure and is not a new held-out request. Distinguish actual source rows, repeated presentations, mechanical chunk work, custody and synthetic regression work.

Finish with actual Git review/selective staging/staged review/Conventional Commit/push commands for the verified branch/upstream. Do not stage, commit or push. Keep prior Task0039 paths distinct if still uncommitted and preserve unrelated work. Do not launch Task0041.

Proceed with **Task0040 only**.
