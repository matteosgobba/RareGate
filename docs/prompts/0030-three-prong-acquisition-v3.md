# LatentTrigger — Task0030: Sleep-Aware Three-Prong Acquisition v3 and Verified Prefix Recovery

## Objective and authorization

Implement and validate a corrected acquisition path, then execute one bounded acquisition session to obtain the pinned three-prong HDF5 file, starting from a verified copy of the Task0029 retained prefix.

This prompt explicitly authorizes:

- Offline implementation, diagnostics, synthetic tests and software acceptance.
- Read-only byte verification of the specified Task0029 prefix and its provenance.
- Copying that verified prefix into a distinct Task0030 namespace.
- A temporary macOS assertion preventing automatic idle system sleep during the session.
- One real acquisition session, conditional on all prerequisite checks passing, with at most six payload requests within one shared transfer deadline.
- Full-file byte verification and bounded HDF structural metadata inspection after integrity verification.

Complete this authorized scope without asking for another general confirmation between implementation and acquisition. Standard platform network approvals still apply; do not bypass them.

This task does not authorize numerical dataset preparation, particle/label/axis value inspection, fingerprint loading, background score loading, model execution, training, recalibration or scientific evaluation.

## 1. Inspect and preserve the current project

Read applicable instructions, `docs/development.md`, project memory, Task0029 prompt/report/handoff, protocol, source, acceptance and operational receipts. Verify branch, HEAD, upstream, index and pre-existing changes.

The planning chat last observed:

- `main` tracking `origin/main`.
- Base commit `01617d5e3312785800058ad3ce0a8ca52741dd0b`.
- Task0029 changes still uncommitted and index empty.
- Memory revision 1.24.

Verify these facts again. Do not require a clean worktree or silently include existing Task0029 work in the Task0030 change list.

Preserve frozen Task0029 implementation, configuration, acceptance, payload and operational records. Verify the accepted source bindings against current bytes. Implement v3 separately, reusing suitable pure helpers where possible. Do not rerun either previous controller or patch historical source after its campaign.

Save this actual prompt and create the initial handoff before substantive work:

- `docs/prompts/0030-three-prong-acquisition-v3.md`
- `docs/handoffs/0030-three-prong-acquisition-v3.md`

Preserve all accepted scientific identities, dependencies and historical outcomes.

## 2. Document the newly observed sleep evidence

The planning chat inspected macOS power-management records and found these events on 2026-10-11, Europe/Rome:

| Task0029 request | Request start | Recorded system sleep |
|---|---|---|
| 1 | 14:46:23 | 14:51:32–14:52:02 |
| 2 | 14:52:36 | 14:52:47–15:08:25 |
| 3 | 15:09:09 | 15:09:25–15:24:28 |

Task0029 first-request to final-checkpoint spans:

- UTC: `2305.963121` seconds.
- Monotonic: `442.5587260829925` seconds.
- Difference: approximately `1863.404395` seconds.

The installed Python clock reported `mach_absolute_time()` for `time.monotonic()`.

Reconfirm available evidence read-only, with narrowly bounded output for the relevant interval. If logs are no longer available, identify the above as planning-chat observations rather than newly verified evidence.

System sleep is directly observed and broadly accounts for the clock divergence. Its contribution to network interruption is plausible; exclusive causation has not been proved.

Document this additional evidence in Task0030 and living memory. Preserve Task0029’s historical statement that the cause was unmeasured at that time.

## 3. Pin the source and retained prefix

Use only this source:

- Zenodo record `6466204`, version v5.
- Filename: `events_anomalydetection_Z_XY_qqq.h5`
- Expected complete size: `235488994` bytes.
- Published complete-file MD5: `54e123a86143b668f9cb76905152a124`
- URL: `https://zenodo.org/api/records/6466204/files/events_anomalydetection_Z_XY_qqq.h5/content`

Authorized retained prefix:

- Path: `data/task0029-three-prong-acquisition/payload-1.part`
- Expected size: `29990748` bytes.
- Partial SHA256: `2be92f0d6125305922494156d3a3e5ac03b146193d11d0101357144f4866d549`
- Partial MD5: `d938d2b24fafd1f9c584b120ad532a13`

Verify the prefix’s regular-file identity, size, byte digest, checkpoint lineage and parent post-reaping inventory. Reject symlinks or inconsistent provenance before a payload request.

If the prefix is missing or mismatched, stop before real acquisition and report the concrete discrepancy. Do not silently switch to downloading from zero.

Copy the matching prefix into a new, independently writable file. Never append to or hard-link the Task0029 prefix. Verify the copy and confirm that the historical file remains unchanged.

This proves the identity of the preserved prefix, not its equivalence to the complete published file. Final complete-file MD5 remains mandatory.

Use distinct namespaces:

- Protocol: `configs/acquisition/three_prong_v3.json`
- Operational output: `results/acquisition/task0030-three-prong/`
- Raw artifacts: `data/task0030-three-prong-acquisition/`

Refuse an existing consumed or foreign Task0030 session. No reset, second session or cross-session replay is authorized.

## 4. Correct sleep prevention and deadline enforcement

### Temporary idle-sleep prevention

Use a scoped native macOS power assertion or `/usr/bin/caffeinate` with idle-system-sleep prevention.

Read the installed primary documentation for the chosen mechanism. Verify the assertion is active before session reservation and payload access. A helper process merely existing is insufficient evidence that the assertion was established.

The assertion must:

- Be owned by this task’s controller/helper.
- Prevent automatic idle system sleep.
- Permit display sleep.
- Be released after success, failure, interruption or controller exit.
- Have observable creation and release evidence.
- Use no persistent power-setting changes, administrator privileges, simulated user activity or application management.

If the assertion cannot be established, stop before reservation. Monitor unexpected assertion/helper loss during execution.

Disclose that manual sleep, lid closure or other system events can still interrupt execution. Do not force the shared Mac into sleep to test this.

### Continuous elapsed time

Use a clock that advances through macOS system sleep for all operational deadlines, preferably `mach_continuous_time()` with correctly implemented integer timebase conversion.

Primary reference: [Apple’s clock declarations](https://github.com/apple/darwin-xnu/blob/main/osfmk/mach/mach_time.h).

Use that clock consistently in:

- Controller and worker grants.
- Transfer and retry waits.
- Prefix copying and hashing.
- Independent process supervision.
- Verification, finalization and acceptance.

Do not reuse a supervisor whose internal enforcement still relies exclusively on `time.monotonic()`. Inspect termination and cleanup helpers too.

Record UTC, ordinary monotonic and continuous timestamps, with explicit clock names. UTC is diagnostic and must not be the sole deadline clock.

After a suspension, check the continuous deadline before issuing another request, reading further payload or accepting a completed worker. Reject normal exit occurring beyond the permitted deadline.

No software can terminate a process while the machine is asleep. If suspension causes overshoot, stop promptly after resumption, preserve artifacts, disclose the overshoot and reject deadline acceptance.

## 5. Freeze one finite acquisition protocol

All session durations below use continuous elapsed time:

| Scope | Maximum |
|---|---:|
| Prefix import and verification worker | 60 s |
| Transfer, including connection, retry waits and recovery | 1800 s |
| Complete integrity verification and structural metadata worker | 60 s |
| Parent finalization | 15 s |
| Whole reserved session | 2000 s |
| Cleanup allowance within each stage | 2 s |
| Payload requests within this session | 6 |

Reserve cleanup slack inside stage ceilings. Neither requests nor retries reset deadlines.

Keep existing resource semantics:

- Worker RSS ceiling: 6 GiB.
- Native reservation ceiling: 512 MiB.
- Controller RSS ceiling: 128 MiB.
- WARN advisory, CRITICAL veto.
- Invalid primary accounting blocks; unavailable pressure is disclosed.
- Global available RAM is contextual.
- Guard journal ceiling: 64 MiB per worker.
- Checkpoint journal ceiling: 8 MiB.
- Bounded streaming buffers and logs.

Observe helper processes separately and include them in lifecycle reporting. Preserve resource-coverage caveats; do not claim hard real-time guarantees.

Allow at most seven retained candidate representations: the imported seed plus at most one new representation per payload request. Each representation must remain within the pinned complete size. Preserve all owned representations on failure.

Require at least 2 GiB free space for the new namespace and demonstrate that retained payloads, guard journals, checkpoints, logs and metadata fit within that capacity. Exclusive final promotion may share an inode with an owned completed file, but must not modify historical files.

## 6. Correct HTTP recovery and Retry-After semantics

Retain strict source, encoding, size and range validation.

For continuation:

- Request the current verified durable offset.
- Append only after a coherent `206` response with exact `Content-Range`.
- A `200` response to a range request starts a fresh owned representation and preserves the prefix.
- Never append a full `200` response to a partial file.
- Missing validators remain explicitly disclosed.
- Use `If-Range` only with an appropriate strong validator.
- Full-file MD5 verification is required regardless of range success.

Consult [RFC9110](https://www.rfc-editor.org/rfc/rfc9110.html) and the installed Python HTTP implementation as needed.

Use fixed minimum retry backoffs of `5, 15, 30, 60, 60` seconds after requests 1–5, subject to the original deadline.

Handle `Retry-After` from both HTTP error responses and validated `200/206` responses whose body later fails. Define successful-response handling explicitly as this application’s prospective recovery policy.

Record the response-header receipt time. For a delta value, calculate the remaining interval from header receipt; do not add the full interval again after a long body read. For an HTTP date, document UTC conversion and clock uncertainty.

The next request must satisfy both the minimum backoff after failure and any remaining applicable Retry-After interval. Waits must fit within the shared budget with request/cleanup slack. Malformed values preserve artifacts and stop.

Retry only the preregistered transient transport failures. Source, checksum, malformed range, representation, storage, ownership or guard failures must not trigger retries.

Keep the 30-second socket timeout as a blocking-operation limit; it is not the session deadline. No parallel payload requests, alternate endpoints, mirrors or unbounded recovery.

Use a clear project User-Agent and do not circumvent service limits.

## 7. Account for durable progress and full-file acceptance

Keep these counters distinct:

- Historical seed bytes imported.
- Bytes newly received during Task0030.
- Bytes written to each candidate representation.
- Durably checkpointed bytes.
- Retained bytes after worker exit.
- Accepted complete bytes.

Do not count imported bytes as newly downloaded bytes. Do not count unobserved network buffers as confirmed progress.

Retain checkpoint synchronization, prefix hashes, source identity, timestamps, request offsets and interruption uncertainty. Emit concise progress during transfer and waits. Keep the user informed at least every 60 seconds without blocking tool waits longer than 60 seconds.

Acceptance requires:

1. Exact complete size.
2. Matching published complete-file MD5.
3. Locally computed complete SHA256.
4. Normal worker exit, reaping and parent acceptance.
5. Continuous deadlines satisfied.
6. No latched guard failure or source drift.
7. Matching post-exit artifact identity.
8. Exclusive promotion and an accepted manifest.
9. Confirmed release of the task’s sleep assertion.

A matching partial hash, successful range response, expected byte count or body receipt alone is insufficient.

After full byte integrity passes, perform only the bounded structural metadata inspection defined in Task0029. No dataset values, previews, axes, labels or particle reads.

Report byte acquisition and structural compatibility separately. Unsupported structure can be recorded without inventing numerical custody or scientific validity.

## 8. Validate before the real session

Add meaningful synthetic tests for:

- Continuous-clock advancement while ordinary monotonic time is stationary.
- Parent and worker deadline enforcement after simulated suspension.
- Normal exit after a deadline being rejected.
- Retry-After on `200/206` followed by timeout or truncation.
- Already elapsed Retry-After intervals and HTTP-date handling.
- Shared deadlines across six requests and retry waits.
- Prefix import, hash mismatch, ownership and historical immutability.
- Valid continuation, ignored range, changed validators and invalid ranges.
- Truncation, exhaustion and preserved artifacts.
- Sleep assertion setup failure, unexpected loss and cleanup.
- Late exit, interruption and artifact-promotion rejection.

Use injected clocks and local HTTP fixtures. No real host-sleep experiments or operational payload requests during tests.

Run the required full and portable suites, lint, formatting, dependency checks and a bounded synthetic supervised integration. Verify actual macOS clock/assertion bindings without downloading operational data.

Historical Task0029 acceptance does not cover v3. Freeze new source/dependency acceptance, protocol and plan only after validation passes.

If validation exposes a defect, repair and rerun affected checks before reservation. Do not make implementation or protocol changes after the real session is reserved.

## 9. Execute the authorized session

Before reservation, establish the assertion, verify source/provenance and storage, and perform one bounded same-context primary metadata connectivity check.

Record this actual prompt as conditional human authorization, bound to the finalized source, acceptance and plan. Do not claim that the user approved a hash that did not yet exist.

Then execute exactly one Task0030 session:

verified prefix import → bounded transfer → complete integrity/structural inspection → finalization.

No further general confirmation is required by this prompt.

If any reserved stage fails, preserve evidence and stop. Do not start a seventh request, reset the session or automatically launch another task.

## 10. Deliver a clear outcome

Produce:

- `docs/three-prong-acquisition-v3.md`
- Task0030 prompt and handoff.
- `results/tables/final/task0030-three-prong-acquisition-summary.json`
- A curated transport-attempt table.

Update README, handoff index and living memory from the verified current revision. Link the newly established sleep evidence without rewriting historical reports.

The Italian final response should be self-contained and sufficiently detailed, approximately 600–1000 words excluding Git. Explain:

- The actual outcome and whether the complete file was accepted.
- Sleep evidence and the limits of causal attribution.
- Assertion creation, monitoring and release.
- Clock definitions, continuous durations, discrepancies and overshoot.
- Prefix provenance, imported/new/durable/retained/accepted bytes.
- Requests, offsets, HTTP outcomes and actual retry waits.
- Complete versus partial integrity evidence.
- Structural observations and their limits.
- Validation performed, resources and remaining issues.
- The concrete next step.

State explicitly:

original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
new_three_prong_signal model/evaluation accessed: NO
new_three_prong_numerical_preparation_in_Task0030: 0
new_model_scoring_in_Task0030: 0
cached_background_numeric_loads_in_Task0030: 0
original_fingerprint_numeric_loads_in_Task0030: 0
optimizer_updates_in_Task0030: 0

Record byte reads and structural metadata access separately. The original YES values preserve Task0026 exposure.

Task0025, Task0028 and Task0029 retain their historical outcomes. Particle remains 192/192 consumed and deferred.

If acquisition succeeds, prepare a brief for a later, separately authorized three-prong scientific evaluation using the verified local file. Do not execute that evaluation here.

Finish with manual Git commands for the actual branch/upstream. Do not stage, commit or push. If Task0029 remains uncommitted, identify its files separately and explain combined changes in living documents. Keep raw payloads, partials, manifests, operational logs, checkpoints and acceptance records excluded from Git.