# Development raw-to-feature benchmark — Task0039 foundation

## Actual scope and status

Task0039 is complete as a synthetic-supported engineering foundation and one
`parent_accepted_membership_metadata_resolution`, not a real raw-to-feature
measurement. Task0038 is committed at292a7e924ffaacfd058a56e1f84dd9a404de06e9;
its historical84252b6base/acceptance/consumed session are preserved. Task0036 stays
`unresolved_no_acquisition`, Task0034 scientific gates unchanged, exposureYES3,
Task0032complete/Task0033exploratory/Task0025failed/particle192consumed deferred.

[Strict prospective config](../configs/benchmarks/development_raw_features_v1.json),
[curated summary](../results/tables/final/task0039-development-raw-feature-summary.json),
[actual prompt](prompts/0039-development-raw-feature-foundation.md) and
[handoff](handoffs/0039-development-raw-feature-foundation.md) distinguish implemented,
resolved and future-authorized work. `future_measurement_execution_authorized=false`.
No raw measurement CLI is enabled; the adapter refuses operational event-file
providers in Task0039. There is no model/score/fit/calibration or scientific path.

## Exact membership and source custody

Only `data/analysis/lhco-rd-v1/dev_train_background.npy` was numerically loaded:
56120bytes, little-endian C-order int64[6999], fileSHA256
2662f0762cf57e39156b0e5c6b1c8e7ac7279a2ecc98c33b2ed69d67a964c781.
All6999IDs pass integer/domain0…1099999/uniqueness checks. Sorting into ascending
source order and taking1024 reproduces payloadSHA256
f80a9483f5ddafcac0e05d9fd6de757e5bbfe9e805f65ced1c0aa801cc266f1a.
Do not assume the original list is sorted. No alternative rows or source were used.

The split manifest and dev scientific identity
2eb34e5b811c12ae5c47afba1ecdb6322feb7c7774b6c9ec5331abe78b3c9a2a
bind the dev-training role/count/hash independently of the filename. The original
frozen config binds development recipe/counts/seed and original full-role hashes;
it has no dev-ID hash entry. That missing key is explicitly resolved through
the split/dev manifests, not silently skipped or treated as missing identity.
The successful Task0020 preparation records first source-ordered dev train rows,
strict order/1024unique and the exact same ID hash. Original preprocessing sorts
source IDs; `ProcessedStore._positions`/`iter_features` preserve that order. Source
text was inspected; no store/broad validator was constructed. Task0020's overall
failed performance campaign remains failed.

Golden features remain the original `results/benchmarks/task0020-frozen-cpu/prepare/input.npy`,
FP32[1024,8]/32896bytes, fileSHA2567164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e,
payload identity2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05
pinned through accepted preparation. Byte/header custody only: zero numeric golden
loads or real feature construction. Source-order identity alone does not establish
operational feature parity; that is a future pre/post gate.

One raw SHA256 pass reads2908260409local bytes and reproduces
5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6.
This is byte custody, not numerical event access. Publisher MD5
629789d55813be3860781b084ae7f1de/v5/record6466204 are bound through unchanged
acquisition/config/audit metadata; MD5 is not newly recomputed. One readonly HDF
metadata open verifies `/df/block0_values`, float64[1100000,2101], chunks[62,2101],
Blosc32001/flags1/parameters[2,2,8,1042096,5,1], hard/nonalias object paths, no
virtual/external dataset sources, exact effective cache and handle closure. Dataset
value/index/read_direct/array/astype access is disabled during inspection. No axis
array, event labels, particles, features, fingerprints or other memberships are read.

## Implemented narrow synthetic adapter

Eight additive helpers separate protocol/custody, ID resolution, selected-row
adapter, pure scheduling/geometry, HDF metadata/hash operations, scoped runtime,
native synthetic fixtures and resolver-only controller. Historical helpers and
configs are untouched. Approval requires the exact1024ordered ID hash and
`development_train_background`; each request is strictly increasing int64, nonempty,
max128 and a subset of that approval. All checks precede backend selection.

Noncontiguous selections use the exact ordered ID list and all2101columns. A
slice is permitted only when every row between its endpoints is in the exact
request. No broad interval is returned then filtered. Owned FP64 rows must have
label0 in final column2100; truth validates role and never enters features.
The installed [h5py selection documentation](https://docs.h5py.org/en/stable/high/dataset.html#fancy-indexing)
supports increasing point selections; the maximum128avoids its documented large-list
case without making a performance guarantee.

The unchanged pure chain is `canonicalize(raw_FP64_particles)` →
`physical_aggregates(canonical_FP32_particles)` →
`standardized_aggregates(..., frozen_parameters)`. It validates finite/nonempty/
trailing zero padding, normalizes signed zero, wraps/sorts original FP64 before
FP32casting and computes all full-event particles before any384view. Aggregates
accumulate FP64 and preserve the original mass-roundoff guard, log channels and
frozen scalers before one final FP32cast. No384particle view, rounded re-sort,
unrounded physical calculation, refit or inverse transform is introduced.

Synthetic tests cover sparse/contiguous approvals, adjacent-row spy/source-order
sentinels, malformed members/roles/headers/lineage, invalid labels/nonfinite/empty/
padding,500particles with a contributing tail beyond384, phi boundaries/signed
zero/FP32ties, mass guards, cross-B exact byte parity, cache/filter/links/cleanup,
no broad/model providers, durable load/one-winner/lifecycle/resource/assertion failures.
Golden fixtures are generated locally. Exact-byte parity remains the prospective
policy; no synthetic cross-batch issue required a tolerance or arithmetic change.

## Selected rows versus chunk work and caches

One nominal uncompressed chunk is62×2101×8=1042096bytes. HDF5 can involve the whole
chunk when selecting one element; neighboring storage decoding does not authorize
Python exposure of those rows. The adapter returns only approved rows. This follows
[h5py chunk documentation](https://docs.h5py.org/en/stable/high/dataset.html#chunked-storage).

Derived from resolved IDs, the fixed windows touch these numbers of chunks:

| B | Window0 / middle / final chunks | Upper decoded bytes per respective request |
|---:|---|---|
| 1 | 1 / 1 / 1 | 1042096 / 1042096 / 1042096 |
| 8 | 8 / 6 / 6 | 8336768 / 6252576 / 6252576 |
| 32 | 31 / 23 / 24 | 32304976 / 23968208 / 25010304 |
| 128 | 111 / 103 / 98 | 115672656 / 107335888 / 102125408 |

The union is312chunks. For all proposed repeated reads, the no-cache geometric
upper bound is26307713520bytes≈24.500967GiB. It is neither measured decompression
nor physical bytes read; cache hits and physical I/O remain unknown. Approved
prefix1024IDs versus384unique raw rows in the fixed window union are distinct.
Selected ID lists/source chunk lists stay ignored; no per-event export is curated.

The fixed policy is explicit1MiB/521slots/w0=0.75, verified at file and dataset
access property lists. It is a prospective reproducibility choice, not a cache-size
search. [h5py cache documentation](https://docs.h5py.org/en/stable/high/file.html#chunk-cache)
defines these controls and their per-dataset scope. OS/metadata/other caches remain
context; full-file hashing can warm pages and fresh handles do not prove cold I/O.
No purge, eviction, swap/app changes or privileged tuning. Installed h5py3.16.0/
HDF52.0.0/hdf5plugin7.1.0 are recorded and31selected native library/config files
pinned. BLAS/Accelerate control is queried separately. BLOSC_NTHREADS=1 is requested,
but effective decoder thread count remains unknown; no single-threaded decompression
claim follows from BLAS/OpenMP or plugin build flags.

## Fixed future timing meanings and schedule

| Scope | Timed boundary | Exclusions |
|---|---|---|
| selected_hdf_read | Approved-ID selection/read/decompression/owned materialization and background-label guard | File open, physical feature construction |
| frozen_feature_construction | Full unchanged canonicalization/aggregate/standardization from an owned preloaded raw batch, including its input guard | HDF read |
| selected_raw_to_features | Direct approved-ID read through completed owned FP32features using the same two operations | Models, queues, transport |

The joint timer is the actual combined boundary; separate medians must not be
added to invent it. File open/metadata/checksum/loading/identity/parity/log/guard
queries are outside pairs; periodic monitoring may interfere. Timer implementation/
resolution must be recorded before the future measurement, independently of
continuous deadline supervision. All observations/outliers remain, no trimming,
cache tuning or favorable-order selection.

B1/8/32/128, three windows at0/floor((1024−B)/2)/1024−B over approved ID positions.
Workers1/3 Bascending, scopes read→features→joint; worker2 Bdescending and scopes
joint→features→read. Per scope/case three warm-ups then20timed calls, cycle windows
reset per phase: warm1each, timed7/7/6. One readonly HDF handle per worker opens
before the pre gate and remains through all cases/post gate. The same explicit
cache persists. For feature-only scope, preload three raw windows once per B,
reuse for its calls and release before advancing B. No whole-population cache.

For each of12B/window combinations both pre and post: selected read once, construct
features twice with exact repeat/golden-position checks, then one joint read+
construction checked against golden. Thus each gate performs2raw reads and3
constructions per window. Gate windows and arrays are temporary; raw/features are
not exported. Future golden loads once per worker and existing6999ID load once
per worker; original prefix/hash/role checks repeat before raw access.

| Future access/accounting component | Requests or constructions | Selected row presentations |
|---|---:|---:|
| Timed+warm-up read/joint raw operations | 552 | 23322 |
| Feature-only raw-buffer preparation | 36 | 1521 |
| Pre/post raw gates | 144 | 6084 |
| Total raw selected reads | 732 | 30927 |
| Timed+warm-up feature/joint constructions | 552 | 23322 |
| Pre/post feature gates | 216 | 9126 |
| Total feature constructions | 768 | 32448 |

36cells/720timed/108warm-up calls total. Timed raw/feature presentations20280each,
warm-up3042each; loads3×6999IDs=20997metadata records,3golden×1024=3072feature
rows,1024approved unique golden rows and384unique selected raw rows. Two raw byte
custody passes proposed, before and after:5816520818bytes, separate from selected
reads. Nothing in this future matrix has run.

Maximum raw current batch2151424bytes; three preloaded raw buffers6454272bytes.
Canonical FP32/FP64 copies, order/slot arrays and aggregate temporaries are bounded
by max128×700; a conservative explicit64MiBowned-array envelope is proposed,
separate from decoder/cache/libraries and whole-process caps. It is not an RSS
measurement or permission to retain events. Future180sper worker/60report/15final,
720reserved/780whole with≤60prerequisites, cleanup2inside, RSS1GiB/native512MiB/
parent128MiB, journals16MiB/log1MiB/owned128MiB are initial bounded proposals. Three
180sworkers+report+final≤615s leave session slack; cost feasibility is unmeasured.
Neither Task0038 prepared service nor tiny synthetic HDF timing predicts real
read/decompression throughput.

## Actual validation and resolver lifecycle

Fresh acceptancef110204f38212e8f6752ab1883afde1df040e56c2c4cb8df20af00fb79decd91:
88targeted/2210full/2210portable in artifact-free copies, lint/format/pip-check,
223source/config/prompt/test files/43package versions/31native bindings. Full/
portable driver43.7698/42.4278s. Native final integration0.650047s is accepted;
two native synthetic invocations both accepted with32feature constructions each.
One copied-driver config-key precheck failed before any native/operational work and
was corrected before final acceptance; directory retained. Legacy instrumented
research fixture subsets each full/portable85models/31forwards/8710rows/two toy
updates/two toy calibrations, plus other uninstrumented old/new synthetic activity.
No globally-zero numerical/forward claim.

Actual prompt17449bytes/SHA256f4cea291e70b7ae215c0822ee3e451b9eca6135eae448945bdbea669f971e165
and prospective freezeSHA256d643a4b51ff6fb865a5e8da4eb823ba4c42b3d60f6019d3d08e50b0222c93d8e
bind final acceptance/source/dependencies/input/config before sole reservation.
PlanSHA256ac93283ee17e0d4c89819802b812335a1f4d14f8474d3fe90c3903a5701fd7a0;
resolver5ddf2cde9caa4040bba5675e15e96ccc consumes the metadata allowance. No source
changes after reservation. Body complete became parent accepted only after exit0,
reaping, output/source identities, gates/caps/continuous deadlines and assertion
release. IDs/windows/metadata observations/receipts/maps/logs remain ignored.

Whole1.867574625s, prerequisites0.116615041s, dispatch1.629381708s, worker1.585260541s,
cleanup0.000435625s, finalization0.074625458s; overshoot0. Fixed30prereq/60resolver/
30final/150whole,2cleanup, RSS1GiB/native512MiB/parent128MiB/journal16MiB/log1MiB/
owned32MiB caps pass. WorkerRSS60309504B/native50331648B,parent31604736B,owned
1479180B at acceptance. Pressure1653NORMAL/1153WARN advisory/0CRITICAL/unavailable.
Maximum sampled gap0.055286917s and terminal resource gap0.044663958s disclosed;
resource sampling ends before process teardown, lifecycle/deadlines remain supervised.
Global available RAM not queried/no floor. Three active owned idle assertions
observed, released/helper−15/reaped/absent, display sleep allowed/no persistent
changes. This custody/resolver duration is not a raw-event feature benchmark.

## Exact Task0040 prerequisites — no launch

1. Separate Task0040 prompt must authorize the listed membership/golden/approved
   raw rows/feature/timing scope. This document/config/resolver grant is not that
   authorization or an execution token.
2. Implement the smallest guarded payload controller and grant adapter; current
   Task0039 CLI/providers remain blocked for real events. Preserve source/model/
   thresholds/scientific/Task0037 identities and all consumed histories.
3. Fresh synthetic/full/portable/native acceptance, fixed source/dependency/build/
   config/input/authorization plan before one durable attempt. Verify source
   bytes/header/schema/cache/role/prefix/golden identities before dependent access.
4. All three workers must use the original ID list and exact1024prefix/golden
   ordering. Require byte-exact pre/post feature parity, zero unauthorized rows,
   finite valid background events, all-particle arithmetic and unchanged transforms.
   A real parity failure rejects the attempt; no empirical tolerance enlargement.
5. Pin/report HDF/Blosc runtime and decoder threading separately, retaining unknown
   effective count unless verified; no single-thread or cold-I/O claim without
   evidence. No cache-size tuning, source substitution or whole-store construction.
6. Freeze the exact36cells/720timed/108warm-up matrix, gates/buffers/732raw requests/
   30927presentations/768constructions32448rows, three handles/load accounting and
   prospective process/storage/time caps. No model/other-role/fingerprint/download.
7. Continuous clocks including suspension, temporary verified sleep assertion,
   display permission, WARN advisory/CRITICAL-invalid-primary veto, normal exits/
   reaping/identities/parity/release; disclose gaps/unknown pressure and preserve
   any failure as consumed, with no retry. Aggregate outputs only; no per-event
   raw/features or invented sums of medians/end-to-end/deployment/scientific claims.

Implementation and exact membership are ready; real parity, raw/feature costs and
180sceiling feasibility remain unmeasured. Task0040 is neither launched nor granted.
