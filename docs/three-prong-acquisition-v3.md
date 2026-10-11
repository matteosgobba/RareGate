# Sleep-aware three-prong acquisition v3 — Task0030

## Outcome and scope

**Complete byte artifact accepted; one authorized session consumed.** A single coherent206 continuation from29990748B receives205498246 new bytes. All three workers exit0/reaped/parent-accepted; complete235488994B matches published MD5 and local SHA256 `063fff3547d17bf4f36a40109e940ac6990105a0fe33a79f4f7c630905dd0742`. The scoped assertion's release is confirmed. No retry, restart, redirect, new numerical preparation or scientific execution occurs.

This task acquires a fixed byte representation and inspects bounded HDF structural
metadata. It does not evaluate anomaly detection, prepare features, read dataset
values, load fingerprints or cached background scores, instantiate candidates or
update optimizers. The initial PCA/AE scientific comparison remains complete;
three-prong scientific generalization remains unmeasured. The original two tests
remain exposed permanently from Task0026. Read the [curated summary](../results/tables/final/task0030-three-prong-acquisition-summary.json),
[transport attempts](../results/tables/final/task0030-transport-attempts.csv) and
[Task0030 handoff](handoffs/0030-three-prong-acquisition-v3.md) for exact evidence.

## Source, copied prefix and durable progress

Only Zenodo record 6466204 / version v5 / DOI 10.5281/zenodo.6466204, CC-BY-4.0,
`events_anomalydetection_Z_XY_qqq.h5`, is authorized. The exact pinned API content
URL and primary metadata check are recorded in the [protocol](../configs/acquisition/three_prong_v3.json).
Complete size is 235488994 B and published MD5 is
`54e123a86143b668f9cb76905152a124`. No alternate endpoint, redirect or parallel
payload request is permitted. A single bounded primary metadata GET in the same
approved execution context reconfirms source/version/size/checksum before reservation.

The retained Task0029 prefix is 29990748 B, partial MD5
`d938d2b24fafd1f9c584b120ad532a13`, SHA256
`2be92f0d6125305922494156d3a3e5ac03b146193d11d0101357144f4866d549`.
Current regular-file/inode/size/digests, final fsynced checkpoint and parent
post-reaping inventory are verified; this is partial identity, not complete
published-file integrity. A byte copy into an independent writable inode is
verified before transfer. The historical prefix is never appended, hard-linked
or replaced; its identity is checked again after the session. No zero-download
fallback, cross-session resume, second session or implementation patch is allowed.

| Counter | Bytes |
| --- | ---: |
| Historical seed copied/imported, not downloaded now | 29990748 |
| Newly received in Task0030 | 205498246 |
| Written to the single owned representation | 235488994 |
| Durably checkpointed | 235488994 |
| Retained unique owned bytes after exit/reaping | 235488994 |
| Accepted complete bytes | 235488994 |

The complete `seed.part` and promoted pinned filename share the new inode.
The historical Task0029 inode remains distinct with its original size/MD5/SHA.
Both independent verification and parent post-exit hashing match the complete
MD5 and SHA above; the manifest/session parent jointly establish acceptance.

Confirmed received bytes mean bytes returned to this application. Imported seed
bytes are separate. Written and fsynced totals include all owned representations;
restarts would retain earlier copies. Wire/internal buffers not observed by the
application are unknown. Checkpoint journal is 8 MiB maximum; payload and journal
fsync plus atomic/fsynced progress records preserve request/offset/source/hash/time.
Promoted complete and `.part` names share only the task-owned completed inode;
retained physical-byte accounting does not double-count that final hard link.

## Newly verified sleep evidence and clocks

Read-only, narrowly filtered macOS power records on 2026-10-11 Europe/Rome confirm:

| Previous Task0029 request | System sleep interval | Coarse duration |
| --- | --- | ---: |
|1|14:51:32–14:52:02|30s|
|2|14:52:47–15:08:25|938s|
|3|15:09:25–15:24:28|903s|

The previous same-endpoint UTC span 2305.963121 s minus ordinary monotonic
442.5587260829925 s gives 1863.404395 s. Recorded coarse intervals sum 1871 s and
broadly explain the divergence, without exact per-second attribution. Sleep is
observed; its contribution to network interruption is plausible, not proved to
be the exclusive cause. The [historical Task0029 report](three-prong-acquisition-v2.md)
retains its task-time cause-unmeasured statement; this is dated additional evidence.

Installed Python identifies ordinary monotonic as `mach_absolute_time()`. Apple's
[primary declarations](https://raw.githubusercontent.com/apple/darwin-xnu/main/osfmk/mach/mach_time.h)
state that `mach_continuous_time()` advances during sleep. Actual native binding
uses unsigned 64-bit ticks and integer `ticks*numer//denom` conversion to nanoseconds
(timebase 125/3 here), then floating seconds for budgets. UTC and ordinary monotonic
are diagnostic; HTTP-date Retry-After is anchored once via header-receipt UTC,
with local UTC/date-precision uncertainty disclosed.

Continuous deadlines govern grants, import/hash, transfers, waits, independent
supervision, TERM/KILL/reaping, verification, finalization and acceptance. Limits:
60 s import, 1800 s shared transfer, 60 s integrity/structure, 15 s finalization, 2000 s
reserved session; 2 s cleanup slack inside each worker ceiling. Every request/read/
write/exit/acceptance checks the continuous deadline, including after suspension.
A late exit0 or late publication is rejected. No software can kill a process
while the machine sleeps; overshoot on resumption must be disclosed and rejected.
Short sleep/poll quanta and supplementary alarms do not replace these checks.

| Scope | Continuous seconds | Ceiling seconds |
| --- | ---: | ---: |
| Prerequisites before reservation | 2.193020 | 60 |
| Prefix import worker, startup/cleanup/exit included | 0.374777 | 60 |
| Transfer worker, startup/cleanup/exit included | 869.023110 | 1800 |
| Complete integrity + structural worker | 0.702536 | 60 |
| Parent finalization before durable publication | 0.456040 | 15 |
| Reserved session through recorded finalization | 870.632494 | 2000 |
| Controller including prerequisites | 872.825514 | separate scope |

Whole ordinary-monotonic duration is872.825513916s,
continuous-minus-ordinary≈2.09e-07s; no material
suspension discrepancy and no overshoot recorded. These are scoped acquisition
measurements, not an inference benchmark. Parent publication timestamp is
381693.177153000 continuous seconds (about8ms after the recorded workflow
finish); post-publication continuous acceptance check passed, driver exit0.
The continuous ceiling remains authoritative. Documentation/report curation
occurs offline after that session and is not part of its transfer/inference time.

## Temporary sleep assertion

Installed caffeinate(8)/pmset(1) manuals were read. The controller starts only
`/usr/bin/caffeinate -i -w controller_PID`: automatic idle SYSTEM sleep is prevented,
display sleep remains allowed. Actual owned assertionID/type/active state is
verified with `pmset -g assertions` before reservation/payload access. A living
helper alone is insufficient. Parent and worker inspect assertion state every 5 s
and process presence at boundaries. Helper RSS/lifecycle are observed separately.
No persistent setting, administrator action, display assertion, simulated user
activity or application management occurs. Manual sleep/lid closure and other
system events can still interrupt the session.

Actual controller PID2179 / helper PID2180, assertionID `0x0002700700019e1d`:174 active observations; creation continuous380820.463655291, confirmed release381692.748518500 / UTC2026-10-11T16:22:46.538078+00:00. Helper exit−15/reaped, owned assertion absent; sampled RSS maximum3227648B (3.078125MiB). The SIGTERM exit belongs to the normally closed sleep helper, not the three exit0workers.

Wait-PID ownership releases the assertion on controller exit; abrupt controller
death cannot itself produce confirmed-release evidence or an accepted artifact.
Explicit TERM/KILL/reaping and disappearance of owned PID/ID are required before
normal manifest acceptance. Missing proof is a failure, with retained artifacts.

## HTTP policy and measured transport

Only coherent 206 `bytes offset-(N-1)/N` may append to the current verified durable
prefix. Exact optional Content-Length and identity encoding are checked. A 200 to
Range creates a new owned representation; it never appends a full response to a
partial file. Changed validators/ranges/encoding/source and storage/guard errors
are fatal. If-Range uses only a strong ETag; missing/weak validators are disclosed
and full publisher MD5 remains mandatory. Up to seven representations are kept.

Following [RFC9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after),
Retry-After is handled on HTTP errors. Applying a valid 200/206 header to recovery
after subsequent body failure is this task's explicit prospective application
policy. The header receipt carries UTC/continuous anchors: remaining delta wait
is computed from header arrival, never reapplied in full after a long body read.
Next request waits `max(fixed minimum after failure, remaining Retry-After)`;
minimum backoffs 5/15/30/60/60 s, no deadline reset. HTTP dates convert once; malformed
values preserve files and stop. Only preregistered transient errors may recover,
within six requests and original transfer budget. 30 s socket timeout bounds blocking
IO, not whole session. The User-Agent identifies LatentTrigger/Task0030.

Exactly one payload request, starting2026-10-11T16:08:16.948266+00:00:
Range `bytes=29990748-`, response206, Content-Range
`bytes 29990748-235488993/235488994`, Content-Length205498246, identity encoding.
Header Retry-After59s was captured at380825.699194916 continuous seconds;
its not-before timestamp380884.699194916 is recorded. The body completes normally,
so no recovery wait or subsequent request is needed. ETag/Last-Modified absent:
no strong-validator claim and no If-Range. One continuation,0restarts/redirects/
retries; final inflight=null,205498246 new confirmed bytes, all written bytes
fsynced. Wire/internal buffering during transfer is not directly measured.

Body receipt, exact size, range response and partial hash are provisional. Acceptance
requires full size/publisher MD5/local SHA, normal exit/reaping, no guard latch,
source/time bindings, matching post-exit identity, exclusive promotion/manifest,
parent acceptance and confirmed assertion release. The manifest requires the
session's accepted parent record; a failed record never grants byte acceptance.

## Structural metadata and scientific limits

The unchanged inspector reports `compatible_looking_structural_metadata_only`:
five hard-linked nodes (`/df` group plus four datasets), pandas fixed frame,
oneFP64block, Blosc filter32001, no external/virtual datasets.

| Dataset | Shape | Dtype |
| --- | --- | --- |
| `/df/block0_values` | [100000,2101] | float64 |
| `/df/block0_items` | [2101] | int64 |
| `/df/axis0` | [2101] | int64 |
| `/df/axis1` | [100000] | int64 |

Value-block chunks are[31,2101]; axis/item chunks[8192].100000 is an observed
structural dimension, not a numerical valid-event/unique-event count.2101columns
fit the preregistered structural widths; meaning/order of columns and a potential
label column were not verified. No schema/parser extension was made.

The exact unchanged Task0029 inspector traverses bounded hard-linked metadata
(nodes/children≤64, depth≤8,bounded filters and fixed scalar relevant attributes ≤512 B).
External/soft links and unbounded attributes are not dereferenced. No dataset
`__getitem__`, particle/axis/label values, preview or new numerical reader is used.
Structure and byte integrity are reported separately. Shapes/dtypes do not verify
axis order, labels, padding, valid-event counts, class, uniqueness, all-role overlap,
frozen-feature compatibility or model quality. Publisher event-count/topology
claims remain publisher provenance until later numerical custody checks.

## Resources, validation and reproducibility

| Process scope | Peak lifetime RSS bytes | Peak conservative native bytes | Checks / WARN |
| --- | ---: | ---: | ---: |
| Import worker | 31408128 | 33554432 | 125 / 125 |
| Transfer worker | 36765696 | 46137344 | 19162 / 19162 |
| Integrity/structure worker | 52232192 | 41943040 | 243 / 243 |
| Stdlib controller | 36782080 | not claimed | separate |

All19530 worker samples areWARN advisory,0CRITICAL/unknown/no latched failure.
Largest workerRSS49.8125MiB, native44MiB; controller35.078125MiB.
Terminal unaccounted intervals0.036864625/0.020749875/0.030408750s are disclosed;
monitoring is sampled. Helper metrics are separate as above.

Worker limits are 6 GiB lifetime RSS / 512 MiB conservative all-malloc-zone reservation;
stdlib controller 128 MiB. WARN advisory, CRITICAL veto, unknown pressure disclosed,
invalid primary accounting veto; global RAM context is not admission. Guard journals
≤64 MiB each, checkpoints≤8 MiB, bounded buffers/logs. Space preflight requires 2 GiB;
seven complete-size representations, three journals, checkpoints, 3 MiB logs and 4 MiB
metadata budget 1865478190 B fit. Observation is not a host-wide headroom certificate,
continuous memory coverage or hard real-time guarantee. Terminal monitoring gaps
and sampled helper RSS are explicitly scoped in the summary.

Final source validation: 1503 tests full/portable (48.38/46.66s), 89 new synthetic
cases, lint / 252-file formatting/dependencies pass. Portable copy excludes data,
artifacts,sources,.git,.venv, retaining only curated fixtures; unchanged historical
portable plugin is used. Synthetic native supervised integration exits0/reaped
in 0.213169 s, no operational payload/value/model access, matching toy MD5, exact
structure-only inspector, active/released assertion, WARN advisory/no latch.
Suspension is simulated with injected continuous advancement and stationary
ordinary clock; no host-sleep experiment. Preliminary failed formatting/diagnostic
records are retained. The initial sandbox diagnostic could not inspect helper RSS;
approved native diagnostic passed and confirmed release. No hosted CI is claimed.

Frozen protocol canonicalSHA256 `268b946af53f3d907ca6153363874b2fae2b3221b2165d83e55184b612862043`;
protocol file-byteSHA256 `a454453a115386ec35ccc6487fbf86486c1016d1c089c1fb166b15efc868068c`.
Plan canonicalSHA256 `34d98ab76b2bb80dc0503899933b8abd9132c9c7ede0e2af0d1831d41bfe5c12`;
own acceptance file-byteSHA256 `1c8363b629f8a68a57238c4580732479a9431a85aea483e75d28d1da8baeefc9`.
The curated JSON registry contains current153source/dependency hashes, all196
historical bindings, prompt/authorization/source/acceptance/plan/operational hashes,
exact clocks/timings/counters/attempts/resource/lifecycle/structural evidence.
The CSV uses accepted checkpoint aggregates only; no per-event values are reopened.

153 current source/dependency file bindings have own Task0030 acceptance. All 146
historically accepted Task0029 sources/dependencies and 196 protected historical
file bindings remain unchanged; old scientific acceptances do not cover new code.
File-byte hashes are separate from canonical JSON protocol/plan hashes. Conditional
human authorization records the actual prompt and finalized source/acceptance/plan;
it does not claim approval of an exact hash that did not exist when the user spoke.
Raw files, manifests, logs, checkpoints, receipts and acceptances remain ignored.
The handoff records the still-uncommitted Task0029 continuation and manual split
of its three overlapping living documents. No staging, commit or push was performed.

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
new_three_prong_signal model/evaluation accessed: NO
new_three_prong_numerical_preparation_in_Task0030: 0
new_model_scoring_in_Task0030: 0
cached_background_numeric_loads_in_Task0030: 0
original_fingerprint_numeric_loads_in_Task0030: 0
optimizer_updates_in_Task0030: 0
```

YES preserves existing Task0026 exposure, not new model access. Real payload byte
access and structural metadata are separately recorded. These zeros concern the
operational scientific populations/models, not mathematical synthetic unit fixtures.
Task0025 remains failed/consumed with provisional ratios; Task0028 and Task0029 retain
consumed failures. Particle remains 192/192 consumed and canonical execution deferred.

## Justified follow-up, not automatic execution

Prepare a **new, separately authorized local-file scientific protocol** using
`data/task0030-three-prong-acquisition/events_anomalydetection_Z_XY_qqq.h5`,
size235488994B/publishedMD5/localSHA `063fff3547d17bf4f36a40109e940ac6990105a0fe33a79f4f7c630905dd0742` and its accepted parent/manifest.
Task0028's consumed reservation cannot be resumed. No new download is required.

Its purpose is testing frozen PCA-v1/compact-AE-v2 signal-topology generalization
against the same exposed Task0026 background reference. Required evidence:
full source/model/transform/calibration/reference bindings; numerical custody,
axis/label/padding/valid-count checks; new-source uniqueness and all-role original
fingerprint overlap gates; original eight features/scaler and native FP64 SSE /
strict `score > threshold`; canonical4096batches with complete tails. A fresh
software acceptance/plan/namespace, finite resources and explicit human consent
must precede any numerical access or scoring. Then PCA→AE→consolidation, all four
original targets0.1/0.05/0.01/0.001, counts/conditional intervals, prevalence-aware
ROC-AUC/AP and descriptive TPR/FPR, with transparent background reuse and no new
independent significance/background-generalization claim. No fitting, optimizer,
recalibration or response-driven candidate/threshold selection. This is a brief,
not a new task, active permission or launched scientific campaign.
