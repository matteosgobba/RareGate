# LatentTrigger — Task 0029: Bounded Three-Prong Acquisition v2 and Durable Payload Preservation

You are continuing **LatentTrigger**. Perform **Task0029 only**.

Task0028’s sole authorized campaign failed and was consumed during acquisition. No three-prong numerical preparation, overlap audit or model evaluation occurred.

Implement a separate acquisition policy and obtain a verified local copy of the same pinned signal file. Separate network transport from scientific evaluation.

This prompt explicitly authorizes:

1. Offline inspection and policy revision.
2. Isolated implementation and synthetic validation.
3. Current-source/protocol acceptance.
4. One conditional new acquisition session, with at most three payload requests within its fixed transfer budget.
5. Byte-integrity verification.
6. Bounded HDF structural-metadata inspection after byte verification.

Once prerequisites pass, execute these authorized steps without another general confirmation.

No particle-value or label reading, feature preparation, fingerprint numerical access, cached-background numerical loading, model execution, scoring, recalibration or scientific evaluation is authorized.

## 1. Inspect live state and preserve the failed campaign

Read applicable instructions, development protocol, living memory and Task0028 prompt/protocol/report/summary/handoff.

Planning inspection found:

```text
branch: main
upstream: origin/main
HEAD:
e381f549225fa9e0960633a9a2093fa295bf39fe
```

Eight Task0028 Phase B continuation files were uncommitted, with an empty index. Verify live state; the user may have committed them before this task starts.

Preserve and distinguish any pre-existing continuation, including overlapping README/memory/index changes. Do not reset, stage or silently fold it into Task0029.

Save:

```text
docs/prompts/0029-three-prong-acquisition-v2.md
docs/handoffs/0029-three-prong-acquisition-v2.md
```

Preserve all old source/protocol/acceptance/receipt/scientific bytes. In particular, do not modify the frozen downloader or Task0028 controller.

Task0028 remains failed/consumed/no retry. Its deleted partial cannot be reconstructed or treated as available. This session starts independently.

Original test exposure remains YES/YES. Three-prong model evaluation remains NO.

Synced `sources/` remain read-only.

## 2. Record the actual engineering failure

Use existing logs and receipts only.

Document:

- Acquisition lifecycle298.033887s.
- Whole campaign298.116752s.
- Deadline interruption, exit1, child reaped, parent rejected.
- Logged transfer lower bound47185920bytes.
- No accepted raw integrity or preserved payload.
- Existing downloader’s unsuccessful-partial deletion.
- All later scientific phases unstarted.
- WARN advisory, without a recorded memory veto.

Do not infer a precise transfer rate, final byte count, server cause or completion ETA from the coarse progress log.

Do not reinterpret the failure as a result about PCA, AE or three-prong signal sensitivity.

## 3. Freeze the same source and a new transport policy

Use:

```text
DOI: 10.5281/zenodo.6466204
record/version: 6466204 / v5

filename:
events_anomalydetection_Z_XY_qqq.h5

expected bytes:
235488994

published MD5:
54e123a86143b668f9cb76905152a124

URL:
https://zenodo.org/api/records/6466204/files/events_anomalydetection_Z_XY_qqq.h5/content
```

Reuse verified primary metadata and attribution. Small metadata requests are permitted where needed; no route-speed search, mirrors or alternate dataset/version.

Create a strict versioned acquisition protocol, for example:

```text
configs/acquisition/three_prong_v2.json
```

Bind actual prompt, source, new code/dependency acceptance, budgets, transport rules, progress accounting, retention and output paths.

Keep a single fixed session namespace:

```text
results/acquisition/task0029-three-prong/
data/task0029-three-prong-acquisition/
```

Existing/foreign/partial/consumed session state must refuse a new launch. No reset or cross-session resume selector.

This new protocol authorizes limited transport recovery within its own session. It does not replenish Task0028 or alter any scientific policy.

## 4. Use finite transfer and lifecycle limits

Preregister:

```text
transfer process: ≤1800s, including connection waits/backoff/cleanup
byte verification and structural metadata process: ≤60s
parent finalization: ≤15s
whole session: ≤1900s
termination/kill/reap grace: ≤2s inside stage deadlines

worker observed lifetime RSS: ≤6GiB
whole native reservation: ≤512MiB
stdlib controller RSS: ≤128MiB
guard journal ceiling per process: 64MiB
```

Retain validated process accounting, pressure semantics and independent parent supervision. WARN advisory, CRITICAL blocks, unknown disclosed, invalid primary accounting blocks.

Global available RAM is context only. No idle-host wait or application/cache management.

The larger journal budget is prospective and explicit: a longer transfer must not inherit a short-run log ceiling without checking its capacity.

Use bounded streaming buffers, not whole-response reads. No new dependencies.

Confirm that the execution context has authorized network access before reserving the session. Do not consume it in a context already known to deny the required access.

Platform approval requirements still apply. Network requests must remain confined to the approved source.

## 5. Preregister limited transport recovery

Allow at most **three payload requests total**, including the initial request.

All requests, waits and continuations share the original1800s deadline. Do not reset it.

Declare retryable conditions before execution. Limit them to specified transient network failures and HTTP408/429/5xx responses. Respect Retry-After within the remaining budget; otherwise stop.

Use fixed retry backoffs of5s and15s where Retry-After does not require a longer wait. No retries for checksum, source-identity or malformed-response failures.

For continuation, validate requested offset,206 status and Content-Range. Never append a200 full response to an existing prefix. If Range is ignored, a full restart may use a new owned file within the same request/time budget, preserving the earlier partial.

Check representation validators where supplied; handle missing/weak validators honestly. Final complete size and publisher checksum remain mandatory.

Preregister oversized, truncated, invalid-range and416 handling. A header or file length alone cannot establish integrity.

Consult primary references:

- [RFC9110 Range/Content-Range](https://www.rfc-editor.org/rfc/rfc9110.html#name-range)
- [Python3.12 urllib.request](https://docs.python.org/3.12/library/urllib.request.html)

Library blocking-operation timeouts do not replace the independent whole-process deadline.

Count requests, continuations, restarts, redirects and waits explicitly. Do not claim Zenodo supports resume before observing a valid response.

## 6. Preserve bytes and make progress durable

Implement a new isolated streaming path. Do not call the old deletion-on-failure routine.

Use exclusive owned files. Never overwrite another session’s partial or an existing verified artifact.

On interruption, exhaustion, checksum failure or process rejection:

- Preserve every owned partial.
- Preserve progress and source bindings.
- Record actual retained size after reaping.
- Keep failed bytes clearly unverified.
- Record a partial digest when feasible, or explain why unavailable.
- Do not delete evidence automatically.

Distinguish:

```text
received bytes
written bytes
durably checkpointed bytes
retained bytes observed after exit
accepted verified bytes
```

Confirmed progress must not exceed durable bytes. Retain uncertainty for an interrupted read/write.

Use bounded durable checkpoints with UTC/monotonic times, request/offset/source identity and prefix state. Provide concise progress output regularly, including during waits, without printing payload content.

Capacity planning must cover up to three retained representations plus bounded journals/metadata. Verify sufficient disk space before work.

Recovery is allowed only inside this new session’s prescribed budget. Future reuse of a failed session’s partial needs separate authorization.

## 7. Verify before accepting the artifact

After transfer completion:

- Independently confirm exact235488994-byte size.
- Compute full MD5 and require the publisher value.
- Compute and record full SHA256.
- Bind verified bytes to source and transport evidence.
- Require normal worker exit, reaping, deadlines and no latched guard failure.

A body receipt is `body_complete_awaiting_exit`; parent confirmation determines acceptance.

Never accept an artifact merely because a transfer reached100%, the file has the expected length or the worker wrote a receipt.

Use atomic promotion/finalization only after required acceptance gates. Preserve full but unaccepted files if lifecycle or verification fails.

The final manifest must distinguish publisher MD5, locally computed SHA256, file-byte identities and metadata/protocol hashes.

## 8. Inspect only structural HDF metadata

After complete byte-integrity verification, use installed h5py to inspect:

- Root/group/dataset names and link types.
- Shapes and dtypes.
- Chunk/filter metadata.
- Bounded relevant structural attributes.

Do not read datasets containing particle values, axes/index values or labels. No slices, previews, distributions, fingerprints or feature calculations.

Compare observed structure with Task0028’s preregistered subset. Report compatible-looking metadata, unsupported structure or an inspection error.

Do not change Task0028’s schema or claim complete numerical custody passed.

A verified byte artifact can remain preserved even if its structure is unsupported. Keep acquisition acceptance distinct from future parser/scientific compatibility.

Observed row dimension is structural evidence, not a confirmed count of valid, unique, independent events.

## 9. Validate preservation and transport behavior

Use local synthetic responses/files. No live scientific payload during tests.

Meaningful cases include:

- Successful full transfer and integrity verification.
- Interrupted/slow response with preserved prefix.
- Retry budget and shared deadline exhaustion.
- Correct206 continuation.
- Wrong offset/total and malformed range.
-200 response to Range, without corrupt appending.
- Full restart retaining the previous partial.
- Retry-After/backoff behavior.
- Oversized/truncated body and checksum failure.
- Foreign files, competing reservations and consumed refusal.
- Durable progress under interrupted writes.
- Complete-body worker that hangs or exits nonzero.
- Parent cleanup/reaping and artifact rejection.
- Guard journal capacity for the longer process.
- Structural inspection without numerical dataset reads.

Reuse validated supervision primitives through a small isolated implementation. Do not build a new general recovery framework.

Run relevant full/portable checks, lint/format, dependency consistency and a guarded synthetic integration. Report actual counts; historical1333 does not cover new code.

Freeze current source/protocol acceptance before the real session. Preserve old139 files without presenting old acceptance as coverage of new code.

## 10. Execute the newly authorized session

After prerequisites pass, record this actual user prompt as authorization for the source-bound Task0029 session, then reserve and execute it once.

No additional general permission question is needed for the explicitly covered acquisition and metadata inspection.

If source or executable drift invalidates the plan, finish a new reviewable acceptance before execution. Do not alter accepted code or limits after reservation.

Keep the user informed at least every60s during a long transfer. Avoid a blocking tool wait that prevents those updates.

Stop at an accepted raw artifact or a preserved failed session. Do not start overlap, preprocessing, model evaluation or Task0028 again.

## 11. Document the outcome and future boundary

Create:

```text
docs/three-prong-acquisition-v2.md
results/tables/final/task0029-three-prong-acquisition-summary.json
```

Update README, living memory and handoff index. Increment from the verified current revision, expected1.23.

Report actual transport attempts/progress, timings, integrity, retained files, lifecycle acceptance and structural findings.

Downloaded bytes are not scientific results. No new AUC/AP, signal efficiency, prevalence evaluated, overlap result or prepared feature identity exists.

On success, prepare a narrow brief for a separately authorized scientific replacement study using the verified local artifact. It must preserve models/transforms/thresholds, perform custody/overlap and use a distinct evaluation namespace/current acceptance.

On failure, document retained evidence and the blocker without another automatic session.

## 12. Deliver detailed Italian output and manual Git

Write approximately600–1000 words excluding Git.

Explain the old failure, prospective policy changes, actual request count, received/durable/retained/verified bytes, size/MD5/SHA256, resource/deadline results, partial preservation, structural findings, validation and next step.

Clearly distinguish numerical custody still pending from byte/header evidence.

Include truthful flags:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
new_three_prong_signal model/evaluation accessed: NO
new_three_prong_numerical_preparation_in_Task0029: 0
new_model_scoring_in_Task0029: 0
cached_background_numeric_loads_in_Task0029: 0
original_fingerprint_numeric_loads_in_Task0029: 0
```

Record raw acquisition and structural-metadata access separately according to actual outcome.

Particle remains192/192 consumed/deferred. Task0025 and Task0028 remain failed/consumed.

Finish with actual selective manual Git commands, preserving any uncommitted Task0028 continuation and explaining overlapping documentation changes.

Do not stage, commit or push automatically. Exclude payloads/partials, logs, progress journals, manifests, acceptances and operational receipts.