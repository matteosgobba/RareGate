# LatentTrigger — Task0039: Development Raw-to-Feature Benchmark Design and Synthetic Foundation

You are continuing **LatentTrigger**. Perform **Task0039 only**.

## Objective and authorization

Make the next missing-chain-cost measurement concrete: establish the exact1024development-training source IDs already used in Task0020/0022/0038, implement and synthetically validate a narrow HDF-to-frozen-feature adapter, and produce a fixed future read/feature/joint timing protocol.

This prompt authorizes additive design/implementation, ordinary synthetic validation, source/configuration/metadata/header/byte custody, and **one bounded operational membership-resolution session** after the resolver has passed synthetic tests. That session may numerically load only the specified development-training ID array, resolve the approved1024prefix, and inspect HDF metadata without reading any event dataset values. Complete this scope without another general confirmation.

It authorizes zero operational raw event reads, particle/feature/score/membership arrays beyond the one listed ID array, model execution, reconstruction, fitting, calibration, fingerprints, scientific evaluation, downloads or measured real raw-to-feature timing. Existing historical synthetic regressions may use their fixture models; distinguish that from zero new operational model work. The future real measurement requires a separate Task0040 prompt/authorization. Do not launch it.

## 1. Inspect and preserve the accepted state

Read applicable instructions, `docs/development.md`, memory, Task0038's report/protocol/summary/handoff, original preprocessing contract/implementation, raw audit/acquisition manifest and Task0020 accepted preparation lineage.

Final planning inspection on2026-10-13 Europe/Rome found:

- Clean `main` tracking `origin/main`, HEAD `292a7e924ffaacfd058a56e1f84dd9a404de06e9`, committed Task0038, empty index; memory1.33.
- An earlier inspection in this planning turn found its23intentional paths uncommitted at `84252b6`; the later commit is now verified. Task0038's historical base/acceptance records remain unchanged.
- One Task0038session accepted/consumed; no additional run or numerical repair is authorized.
- Task0036 remains `unresolved_no_acquisition`, with Task0034 scientific gates unchanged.

Recheck actual Git and preserve unrelated changes. Snapshot initial Task0038/other intended bytes and preserve them, separating any new README/memory/index updates. Do not stage old work, rerun Task0038 or rewrite historical bases/acceptance.

Save actual prompt/initial handoff:

- `docs/prompts/0039-development-raw-feature-foundation.md`
- `docs/handoffs/0039-development-raw-feature-foundation.md`

Task0032 stays complete, Task0033 exploratory, all evaluated samples permanently exposed, Task0025 failed, and particle192/192 consumed/canonical-deferred. No new source search, scientific protocol amendment, simulator rerun or deployment choice.

## 2. Resolve the exact development membership narrowly

Only this numerical membership source is permitted:

`data/analysis/lhco-rd-v1/dev_train_background.npy`

- Shape6999, dtype little-endian int64, C order.
- Size56120bytes.
- SHA256 `2662f0762cf57e39156b0e5c6b1c8e7ac7279a2ecc98c33b2ed69d67a964c781`.

Planning confirmed existence, nonsymlink status, file bytes and NPY header only; no numeric IDs were loaded. Bind the list through the unchanged split manifest/configuration and accepted dev-store manifest scientific identity, independently of its filename.

After synthetic validation and explicit resolver reservation, load the array once. Require unique integer IDs in0…1099999, all6999records, no duplicates or replacement source. Reproduce the historical ascending source order and select its first1024IDs. Do not assume the membership file is already source-sorted.

The selected contiguous little-endian int64 bytes must have SHA256:

`f80a9483f5ddafcac0e05d9fd6de757e5bbfe9e805f65ced1c0aa801cc266f1a`.

Compare this exact identity against Task0020's `prepare/prepared.json`, successful preparation receipt/access record and historical iterator semantics; Task0020's whole failed campaign remains failed. The role/order alignment must not rely on length equality alone.

Keep selected IDs and derived batch/window membership in ignored owned artifacts with hashes, not curated per-event exports. Report1membership load/6999metadata IDs inspected and1024selected IDs if successful. These are new numerical metadata access, not feature/population reads. If lineage/order/hash cannot be established, stop the resolver and preserve the blocker; do not choose different rows, scan full-store membership or regenerate preparation.

Do not construct `ProcessedStore`, invoke `prepare_inputs`/broad split validators, or load dev/full particles, features, labels, multiplicities, development flags, group maps, selection/calibration memberships or fingerprints. Their metadata/file bindings can be inspected as text without opening their numerical arrays.

## 3. Pin raw source and golden-feature identities

Existing raw source:

`data/raw/lhco/6466204/events_anomalydetection_v2.h5`

- Size2908260409bytes.
- SHA256 `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`.
- Publisher MD5 `629789d55813be3860781b084ae7f1de`; record6466204/v5.
- `/df/block0_values`: float64 shape1100000×2101, chunk62×2101, Blosc filter32001 under the accepted raw audit.

Bind existing acquisition/audit/configuration bytes. Whole-file hashing is allowed custody and must be recorded with actual pass/byte counts. During the bounded resolver, one read-only HDF metadata inspection may verify dataset path/shape/dtype/chunks/filter properties and effective cache settings. **No `Dataset[...]`, axis-array reads, sample validation or event values.** Reject links/ambiguous paths/schema changes; no raw acquisition or silent fallback.

The future numerical golden reference is the same Task0038prepared array:

`results/benchmarks/task0020-frozen-cpu/prepare/input.npy`,1024×8FP32,32896bytes,
fileSHA256 `7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`,
payloadSHA256 `2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05`.

Task0039 may verify its bytes/header/provenance but must not numerically load it. Pin the frozen transform configuration and original feature helper bytes. Do not read operational model artifacts or stored scores.

## 4. Implement the narrow adapter on synthetic HDF fixtures

Add a small separate benchmark/helper namespace. Reuse unchanged pure feature functions rather than reproducing or optimizing their arithmetic. No operational raw-measurement CLI is enabled in this task; execution-authorized flags remain false. The resolver permission is a separate metadata scope, not a benchmark grant.

The proposed reader accepts only checked, strictly increasing approved IDs for a bounded batch (maximum128). Reject unauthorized IDs/roles before calling the dataset backend. Select those rows directly with supported HDF indexing, returning only their2101columns; never read a broad row interval and then filter it in Python. A contiguous slice is permitted only if every row in it belongs to that exact approved request.

Source semantics: first2100columns are700(pT,eta,phi)triplets, final column must be background label0 for the selected events. Truth validates role but never enters features. The future numerical operation must preserve source order and inspect only approved rows.

Use the unchanged chain:

`canonicalize(raw_FP64_particles)` → `physical_aggregates(canonical_FP32_particles)` → `standardized_aggregates(..., frozen_parameters)`.

Preserve finite/nonempty/padding validation, signed-zero handling, FP64 source sort/wrap before physical FP32 casting, **all particles before truncation**, FP64 aggregate accumulation, frozen log channels/scalers and final FP32 cast. Do not build the384particle view, re-sort rounded values, compute directly from unrounded FP64 particles, refit, invert rounded features or change mass-roundoff behavior.

Keep raw batch/physical buffers bounded and ephemeral. Do not rebuild processed stores, cache a whole population or export per-event reconstructed features. The future feature parity gate must compare each result with the same approved-position golden feature row, with an exact-byte objective under unchanged arithmetic. If synthetic analysis identifies a genuine cross-batch numerical issue, document and fix the prospective parity policy before operational feature access; never enlarge a tolerance after seeing real errors.

Fixture tests must include noncontiguous approved selections, forbidden adjacent rows and source-order sentinels, invalid labels/nonfinite/padding/empty events, >384valid particles retained in full aggregates, phi boundaries/signed zero/equal-pT ties/FP32 rounding, mass guards, chunk/filter/cache metadata and resource/cleanup failures. Inspect/read generated HDF fixtures only.

## 5. Separate selected rows from storage chunk work

HDF5 may decompress an entire62-row chunk for a single selected row; [h5py documents this behavior](https://docs.h5py.org/en/stable/high/dataset.html#chunked-storage). Such mechanical neighboring-row decoding is not permission to expose or analyze neighboring rows. The Python adapter must receive only approved selected rows.

From the resolved IDs and verified chunk geometry, calculate chunks intersected per future request and theoretical decoded-byte bounds. Distinguish requested/returned selected rows, repeated logical reads, geometric touched chunks, HDF cache effects and unknown physical I/O. Do not label a geometric bound as measured decompression/bytes read or claim zero neighboring storage access.

Use [h5py's selection and cache documentation](https://docs.h5py.org/en/stable/high/file.html) to justify a fixed future policy. Explicitly propose raw chunk-cache settings1MiB/521slots/w0=0.75, verify supported/effective values, and retain other cache layers as unknown context. No cache-size search or timing-driven tuning. Query installed HDF5/h5py/hdf5plugin versions; no dependency install.

Whole-file hashing can warm OS pages. Fresh HDF handles do not prove cold disk/cache. No purge, cache eviction, app closure, swap changes or privileged tuning. Report this limitation prospectively instead of claiming cold I/O. Record decoder threading/control separately; BLAS/OpenMP settings alone do not prove single-threaded Blosc decompression.

## 6. Produce a fixed future measurement protocol

Design only three nonoverlapping meanings:

- `selected_hdf_read`: approved-ID selection/read/decompression/materialization, with file opening outside its per-call timer.
- `frozen_feature_construction`: the full canonicalization/aggregate/standardization chain from an already owned raw batch; no HDF read inside that timer.
- `selected_raw_to_features`: direct approved-ID HDF read through completed owned FP32features, timed jointly.

The joint path is the actual measured boundary; do not reconstruct it by adding separate medians. File-open/metadata/checksum costs are separate untimed/provenance stages or separately labeled context. No model service/queue/transport is silently included.

Propose B1/8/32/128, three deduplicated windows per B over the exact1024ID order, three fresh sequential workers, three warm-ups then20timed calls per worker/B/scope, with pre/post identity/parity gates. Expected36cells/720timed/108warm-up calls. Freeze actual scheduling/order, windows, HDF handle/cache lifetime and prepared raw buffers before any future measurements. Do not execute that matrix now.

Specify separately, and calculate exactly from the schedule, future membership/golden loads, raw selected-row requests/presentations, feature-construction presentations, pre/post gate reads, and peak live buffers. Internal decompression/cache work is a separate documented estimate. Do not substitute contiguous training rows, use source rows0…1023, or infer row IDs from the feature matrix.

Give justified prospective continuous/time/RSS/native/controller/journal/log/storage limits. A suitable initial ceiling to assess is180s per future numerical worker,60s reporting,15s finalization, reserved720s/whole780s including≤60prerequisites,1GiB RSS/512MiB native/128MiB parent and128MiBowned output. These are proposals, not measured feasibility or a grant. Do not infer raw-reader throughput from Task0038prepared-service timing.

The future session must verify the raw source before numerical access, use continuous supervision/temporary idle-sleep assertion/display sleep allowed/WARN advisory/CRITICAL-invalid-primary veto, retain unknown pressure/gaps, require normal exit/reaping/identities/parity and preserve one-attempt failure. No persistent power change or global free-RAM launch floor.

## 7. Validate before the one membership-resolution session

Run meaningful synthetic tests on source/membership/header/role boundaries, resolver order/hash identity, same-length wrong IDs, partial/duplicate/corrupt lists, prohibited provider calls, exact source/golden alignment, synthetic HDF selection and frozen feature construction. Include spy/reference checks proving no unapproved event rows are returned and all particles contribute.

Run relevant targeted/full/portable synthetic suites in artifact-free source copies, lint/format/dependency checks and bounded native synthetic integration where needed for HDF/filter/guard behavior. New acceptance must cover new helpers; old2122tests do not automatically cover them. Historical fixture model activity is separate. No operational membership/event/golden-feature load during these tests.

Then freeze final resolver source/configuration/dependency/input identities and this actual prompt for **one metadata-resolution invocation**. Use an owned ignored output and durable pre-load/completed/inflight entries. Limits:30s prerequisites,60s resolver dispatch-through-exit/reaping,30s aggregate finalization/reporting,150swhole; cleanup2sinside caps;1GiBworker/512MiBnative/128MiBparent,16MiBjournal/1MiBlog/32MiBowned storage. Verify temporary idle-sleep assertion and release on every exit, with continuous deadlines and existing scoped pressure/accounting semantics.

The operational resolver may perform only the one6999-ID load, exact1024prefix binding, raw byte/header metadata custody and generation of a prospective plan from geometry/scalars. Zero operational raw payload or golden-feature numerical access. Missing/failed inputs stop before dependent steps. On failure preserve partial evidence and report readiness blocked; no second operational ID load or broader scan in this task.

Do not mark the resulting future protocol as execution-authorized or the metadata resolver as a real raw-to-feature benchmark. Synthetic adapter success plus membership binding can establish implementation/design readiness; operational parity and costs remain unmeasured.

## 8. Deliver a reviewable next measurement

Produce:

- `docs/development-raw-feature-benchmark-design.md`
- Task0039 prompt/handoff.
- `configs/benchmarks/development_raw_features_v1.json`, clearly prospective/synthetic-supported, operational measurement unauthorized.
- Minimal resolver/adapter helpers and synthetic tests/validation entrypoint.
- `results/tables/final/task0039-development-raw-feature-summary.json`.

Curate source/role/hash/schema/transform/selection/cache/scope/buffer/access decisions, synthetic evidence, actual resolver status and blockers. Keep selected IDs, raw metadata observations, receipts, acceptance maps and fixture/operational logs ignored. No per-event feature tables or scientific plots are needed.

Update README/index/memory from verified1.33. The Italian handoff should distinguish implemented/tested, numerically resolved membership, and proposed future timing. Preserve all Task0038nonliving bytes/receipts and report shared living-document updates separately.

State actual counters, including:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
new_operational_development_membership_array_loads: ACTUAL_COUNT
membership_ID_records_inspected_selected: ACTUAL_COUNTS
raw_byte_hash_passes_and_bytes: ACTUAL_COUNTS
raw_HDF_metadata_opens: ACTUAL_COUNT
operational_raw_event_rows_requested_or_returned: 0
operational_feature_or_score_array_loads: 0
operational_feature_construction_or_model_forward_calls: 0
operational_optimizer_updates_calibrations_scientific_evaluations: 0
new_fingerprint_numeric_loads: 0
downloads: 0
new_real_raw_read_feature_timing_measurements: 0
membership_resolution_status: ACTUAL_STATUS
future_measurement_execution_authorized: false
```

Do not claim zero numerical access if membership was resolved. Synthetic feature construction and historical regression model work are separately disclosed; YES preserves permanent historical exposure.

End with the exact Task0040execution prerequisites and bounded scope, without launching it or requesting another general confirmation for the already authorized Task0039 work. Finish with actual Git review/selective staging/staged review/Conventional Commit/push commands. Do not stage, commit or push; preserve prior/unrelated work and keep uncommitted Task0038paths distinct if still present.

Proceed with **Task0039 only**.


