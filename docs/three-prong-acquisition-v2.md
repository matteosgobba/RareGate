# Bounded three-prong acquisition v2 — Task0029

Task0029 separates network transport and byte integrity from numerical custody
and scientific evaluation. Its actual user prompt authorizes one new acquisition
session after new-source software acceptance, at most three payload requests in
one fixed transfer budget, and bounded HDF structural metadata inspection only.
**Actual session: failed/consumed with preserved partial bytes; no verified local copy.**
Three payload requests exhausted the fixed request budget; the verification/HDF
phase never started. Current limits and follow-up are recorded below.

[Actual specification](prompts/0029-three-prong-acquisition-v2.md),
[strict protocol](../configs/acquisition/three_prong_v2.json),
[curated summary](../results/tables/final/task0029-three-prong-acquisition-summary.json),
[handoff](handoffs/0029-three-prong-acquisition-v2.md).

## Actual transport outcome — 2026-10-11

[Curated attempts](../results/tables/final/task0029-transport-attempts.csv) contain
transport evidence, not scientific metrics. Approved same-context primary metadata
connectivity succeeded before reservation (one9124BGET, no payload); required disk
855364774B versus277988868096B available. Actual prompt/source/protocol/146source /
acceptance identities agreed. One exclusive new session and one controller
invocation; no post-reservation code/protocol/dependency/limit change or replay.

| Request | Offset / bytes | Response and terminal observation |
| --- | ---: | --- |
| 1 | 0 | 200full; `TimeoutError: The read operation timed out` |
| 2 | 27000832 | 206, `bytes 27000832-235488993/235488994`; read timeout |
| 3 | 28770304 | 206, `bytes 28770304-235488993/235488994`; truncated EOF |

Two valid range continuations,0full restarts,0redirects followed/observed. Fixed
waits5.002264167s and15.010565667s completed within the original monotonic deadline.
All observed ETag/Last-Modified were absent; valid206shows support for these two
requested offsets, not a universal resume/representation-identity guarantee.
No precise rate, server cause, completion ETA or favorable alternative is inferred.

| Byte scope | Actual bytes |
| --- | ---: |
| Application-observed received | 29990748 |
| Written | 29990748 |
| Durably checkpointed | 29990748 |
| Retained after exit/reaping | 29990748 |
| Accepted verified complete bytes | **0** |
| Pinned expected complete size | 235488994 |

Received counts refer to returned application reads/surfaced partials, not wire /
headers/internal buffers. Earlier timeout uncertainty is not converted into
confirmed bytes. Final truncated EOF and checkpoint leave `inflight=null`; no
active worker/read/write remains. The final retained prefix exactly matches the
fsynced prefix, independently hashed by the parent after exit. **It is unverified
as the complete source artifact**, not a valid scientific population or parser input.

Retained file:
`data/task0029-three-prong-acquisition/payload-1.part`,29990748B.
PartialMD5 `d938d2b24fafd1f9c584b120ad532a13`;
partialSHA256 `2be92f0d6125305922494156d3a3e5ac03b146193d11d0101357144f4866d549`.
These are partial-file byte identities, distinct from publisher full-fileMD5
`54e123a86143b668f9cb76905152a124`. Full-fileMD5/SHA256/integrity acceptance are
unavailable. The complete filename/manifest were never promoted/created. Owned
partial, progress/checkpoint journals, log, guards, receipt/dispatch/parent rejection,
reservation/source/authorization/acceptance/protocol copies and workflow remain
preserved. No file was deleted; future partial reuse needs separate authorization.

### Lifecycle, resources and clock scope

Worker error `Truncated: Truncated response; prefix retained`, exit1/reaped /
parent rejected, no parent timeout/error or forced termination. Parent transfer
lifecycle442.666572042s, worker442.608939458s, cleanup0.000128250s; interrupted-body /
isolated network duration not recorded. Parent finalization/retained digest
0.043758583s. Controller `wall_seconds`445.572426209s is measured using the
implemented **monotonic clock**. Verification/structural metadata not started.
These operational timings are not inference benchmarks or scientific metrics.

Observed workerRSS37175296B=35.453125MiB, native reservation46137344B=44MiB,
parentRSS37142528B=35.421875MiB, below6GiB/512MiB/128MiB ceilings.7877guard checks /
7739periodic: NORMAL7228, WARN649, CRITICAL/unknown0. No latched guard error;
owned thread closed. Terminal guard-closure-to-exit gap0.013391709s unaccounted.
Actual guard journal3728987B<64MiB; checkpoint journal40535B<8MiB. No optional
availableRAM context recorded; no idle-host/cache/application action. Sampled /
lifetime metrics and overlapping memory scopes do not prove continuous resources.

**Recorded clocks diverge materially.** First requestUTC12:46:23.304958 and final
checkpointUTC13:24:49.268079 span2305.963121s; the same recorded endpoints span
442.558726083monotonic seconds. Cause was not measured. Monotonic budget checks
are within the fixed ceilings, but do not equate those durations with UTC elapsed
or claim an uninterrupted physical wall-clock budget pass. The recorded UTC span
exceeds the nominal whole-session ceiling; this is an explicit enforcement-scope
limitation, not a reason to relabel the failed session accepted or change budgets.

### Post-reservation implementation limits

The retained200/206response headers contain Retry-After58/59/59. Frozen
`retry_delay` consults that header for **HTTPError** cases; timeout/truncation after
200/206uses the fixed5/15backoffs and records those response headers without using
them in that calculation. Do not claim generic successful-response/read-failure
Retry-After handling, or infer a server-cause/significance result from it. Precise
Retry-After compliance across these cases is not established by the recorded
backoffs and divergent clocks. This is a limitation identified after reservation,
not covered by the passing HTTP-error Retry-After synthetic cases.

The accepted frozen source, protocol, acceptance and original receipts are left
unchanged; no after-the-fact patch, additional request, reset or new session.
Future policy must version/test successful-response Retry-After semantics and
explicitly define clock/enforcement semantics before a separately authorized
replacement. Historical software acceptance reports what passed; it does not
certify these broader untested claims.

### Structural and scientific outcome

**HDF metadata not inspected:** complete byte-integrity gate never passed,0HDF
opens/structural requests,0dataset/axis/particle/label reads. Actual layout/row
shape/chunks/filters/class remain unavailable. No numerical preparation/feature
identity/uniqueness/overlap/cached scores/model/scoring/optimizer work, no new
AUC/AP/efficiency/prevalence. Original testsYES/YES remain Task0026 exposure; new
three-prong modelNO. Task0025/0028failed/consumed andparticle192/192deferred intact.

The original study remains accepted. This task establishes tested isolated
preservation and observed206continuation evidence, **not a verified235488994B
artifact or three-prong scientific result**. One justified next step is an offline
review/versioning of the two exposed transport/enforcement limits and retained
prefix lineage. Any reuse/new request requires separate explicit authorization,
new current acceptance and distinct session namespace; no automatic session or
scientific study is launched. The successful-acquisition scientific brief below
remains conditional and was not activated.

## Preserved failed campaign and live base

Task0028 remains failed/consumed/no retry: acquisition298.033887s, campaign
298.116752s, deadline interruption, worker exit1/reaped/parent rejected. Its log
records a transferred-byte lower bound47185920B; not a final byte count, precise
rate, server-cause diagnosis or completion ETA. The frozen downloader removed its
own unsuccessful.part; no previous payload is available or reconstructed. All
later scientific phases were unstarted; WARN was advisory with no memory veto.

Live base is actual local Task0028 continuation commit
`01617d5e3312785800058ad3ce0a8ca52741dd0b`, main/origin/main, initially clean.
No prior continuation remains uncommitted. Old139source/dependency files and all
Task0028 source/protocol/acceptance/receipt/scientific history are preserved.
The old downloader/controller are unchanged; this session is independent.

## Same pinned source

[Official Zenodo v5 record](https://zenodo.org/records/6466204),
DOI10.5281/zenodo.6466204, record6466204; particle file
`events_anomalydetection_Z_XY_qqq.h5`, expected235488994B, publisherMD5
`54e123a86143b668f9cb76905152a124`, exact endpoint
`https://zenodo.org/api/records/6466204/files/events_anomalydetection_Z_XY_qqq.h5/content`.
Kasieczka–Nachman–Shih, CC-BY4.0 attribution/primary metadata is reused from
Task0028's verified official API/cards. No alternate source/version, mirror,
route-speed search, jet-feature file or answer key is used. Publisher signal
description/count are not new numerical custody or model evidence.

Approved platform network execution plus a bounded same-context primary metadata
GET precede reservation: exact record/version/source/size/checksum/license checked,
≤16384B response/10s socket/15s independent parent alarm. Failure does not reserve
the payload session. That one metadata request is separate from payload requests.

## Prospective finite session and storage policy

| Scope | Fixed ceiling |
| --- | ---: |
| Transfer process, connections/waits/recovery/cleanup included | 1800s |
| Independent byte verification + structural metadata process | 60s |
| Parent finalization | 15s |
| Whole session | 1900s |
| Termination/reaping grace inside stage ceilings | 2s |
| Worker observed lifetime RSS / whole native reservation | 6GiB /512MiB |
| Stdlib controller observed lifetime RSS | 128MiB |
| Guard journal per worker / checkpoint journal | 64MiB /8MiB |

The transfer operation deadline is grant start+1798s, preserving2s cleanup inside
1800s; never reset for another request. Same principle yields58s verification
operation inside60s. Existing validated process supervision/resource guard are
reused, one numerical metadata worker at a time. WARN advisory/CRITICAL veto /
unknown disclosed/invalid primary accounting veto; no global RAM admission floor,
idle-host wait or application/cache management. RSS/native scopes overlap and
terminal coverage gaps are disclosed; no hard-real-time/continuous memory claim.

Three retained representations need706466982B. With two64MiB guard journals,
8MiB checkpoint journal,2MiB logs and4MiB metadata slack, required free disk is
855364774B, checked before work. Exclusive atomic promotion uses a hard link,
retaining the complete owned representation under its.part name; the two names
share one inode and do not consume another payload allocation. There is no
overwrite of an existing artifact or deletion of previous representations.

Capacity planning budgets40000guard records at≤1024B,40960000B<64MiB, covering
nominal50ms periodic intent (≤36000transfer samples) and explicit checkpoints /
waits/prefix hash boundaries. Synthetic capacity checks pass; actual bounded
journal refusal remains enforced. Sampling intent is not a delivery guarantee.

## Preregistered HTTP recovery rules

Implementation consults [RFC9110 Range/Content-Range](https://www.rfc-editor.org/rfc/rfc9110.html#name-range),
[If-Range](https://www.rfc-editor.org/rfc/rfc9110.html#name-if-range),
[Retry-After](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after) and
[Python3.12 urllib.request](https://docs.python.org/3.12/library/urllib.request.html).
These prospective rules were frozen before reservation; the actual outcome and
post-reservation implementation limits above bound what was implemented/observed.
Resume support is never assumed.

At most3payload requests including initial. Retryable:408/429/5xx, timeout,
truncated EOF, IncompleteRead, RemoteDisconnected, EAI_AGAIN and the listed transient
connection errno values only. Other HTTP/source/size/header/encoding/range /
representation/SSL/write/guard/checksum/journal/foreign-file failures stop.416
preserves bytes and fails; it is never integrity evidence. Fixed backoffs5s/15s,
or longer valid Retry-After delta/date; remaining budget plus minimum2s request
slack must fit, otherwise stop. Malformed Retry-After refuses. Socket timeouts30s
do not replace independent process deadlines. Redirects are refused and counted,
never followed; only the exact approved URL is requested.

Continuation offset is an owned fsynced prefix, with inode/size/SHA rechecked.
Append only a206 whose Content-Range is exactly offset throughN−1 out ofN,
with coherent optional Content-Length. StrongETag may supply If-Range and must
match on206; changed supplied ETag/Last-Modified refuses. Weak/missing validators
are disclosed and never asserted strong; final publisherMD5 remains mandatory.
200in response toRange starts a new exclusive owned file for that request number,
preserving the previous prefix; never append a full response. Oversized chunks
are counted as received but refused before write; truncated bodies checkpoint
prefixes and may recover only within the original budget. Full-but-uncertain
interrupted responses are retained without extra recovery/acceptance.

## Durable progress and failure retention

64KiB streaming buffer, checkpoints after1MiB or5s, concise progress at least
every15s during active loops/waits (individual blocking operation≤30s timeout).
Payload fsync precedes bounded compact checkpoint journal fsync, then atomic
progress replacement/file+directory fsync. UTC/monotonic timestamps, request /
offset/source digest, inode and durable prefix SHA256 bind progress. Explicit
in-flight state conservatively retains read/write interruption uncertainty.

Received, written, cumulative durably checkpointed, retained-after-reaping and
accepted verified bytes are distinct. Confirmed progress cannot exceed fsynced
bytes. After reaping, the parent observes retained sizes and computes bounded
byte digests when feasible; unavailable digest reasons remain explicit. Unknown /
foreign inodes receive metadata-only treatment. Every owned partial/full but
unaccepted file remains present on interruption, exhaustion, integrity or
lifecycle failure. Future use of failed-session bytes needs separate authorization.
OS-acknowledged checkpoints do not promise physical power-loss immunity.

## Verification, structural inspection and acceptance

Independent streamed exact size/publisherMD5/localSHA256 verification precedes
any HDF open. Failed checks retain actual hash evidence and bytes, with no retry.
Normal worker exit0, reaping, deadlines, intact source/output identities and no
latched guard failure are required. Body receipts remain
`body_complete_awaiting_exit`; the parent accepts lifecycle/output gates.100%,
expected length or a worker receipt alone is insufficient. Exclusive final
promotion follows both accepted workers and a fresh matching post-exit byte hash.
Manifest acceptance requires the root session parent acceptance; verified bytes
can remain full but unaccepted if lifecycle/finalization fails.

HDF inspection reads only bounded names/link types, shapes/dtypes, chunk/filter
metadata and selected fixed scalar structural attributes≤512B. Variable-length /
array attributes are skipped; soft/external links are not dereferenced. Max64nodes /
children, depth8, bounded names/filter counts/parameters. No dataset slices,
previews, axis/index/particle/label values, distributions or fingerprints.

Comparison with Task0028's four-dataset pandas-fixed subset is **compatible-looking
structural metadata only**, unsupported structure, or inspection error. Byte
acquisition acceptance is separate: unsupported/error structure may leave a
verified byte artifact accepted after normal lifecycle, while parser/custody /
scientific compatibility stays pending. Row shape is not a verified count of
valid/unique/independent events. Task0028's schema is not expanded here.

## Own software validation and source-bound authorization

81new local synthetic cases;1414full and1414portable tests pass without skips /
errors/failures. Portable tree excludes data/artifacts/sources/Git/venv; unchanged
legacy narrow synthetic-schema plugin only. Guarded installed-h5py toy byte /
metadata integration exits0/reaped in0.177618s, no operational payload requests,
dataset-value/fingerprint/cached-score reads or model scoring. Lint/format and
dependency checks pass; dependencies unchanged. Historical1333acceptance does not
cover this new code; own146source/dependency acceptance binds validation evidence.

Protocol canonical SHA256
`669a10af75762bcca71bcd3c308ec24906a8d9c67bc2c3633b2383ea0182cd84`;
acceptance file-byte SHA256
`f1d0573ea87d403a11235e5645f0326cb32ace1cae025655c6b0b1381bc233ec`;
plan canonical SHA256
`dd7a7f546b1fae7e0aaa821715bfa029fa3b1725f9645932cb75c21b56abe50e`.
Actual prompt is the human authorization for conditional implementation/acceptance
then execution; it is not falsely described as human approval of a subsequently
generated exact hash. UTC/prompt bytes/source/acceptance/plan are bound in the
authorization audit before invocation. No additional general confirmation needed.

Fixed session `results/acquisition/task0029-three-prong/`, owned raw namespace
`data/task0029-three-prong-acquisition/`. Existing/foreign/partial/consumed state
refuses new launch; no reset/cross-session resume selector. Actual authorized
command invoked once, in a platform-approved network context:

```bash
.venv/bin/python -m latenttrigger.data.three_prong_acquisition --run-acquisition --network-authorized
```

## Scientific boundary

Original tests remain permanentlyYES/YES; new three-prong model evaluationNO.
No numerical preparation, original fingerprint numeric access, cached background
numeric load, model execution/scoring/optimizer/fitting/recalibration/scientific
metrics. Downloaded/verified bytes and structure are not AUC/AP/efficiency /
prevalence/overlap/feature identity. Initial Task0026/0027 study remains accepted.
Task0025 andTask0028 failed/consumed, particle192/192consumed/deferred.

On accepted acquisition, a separately authorized scientific replacement must use
the verified local artifact with a distinct evaluation namespace/current software
acceptance, original frozen candidates/transforms/thresholds, full numerical
custody/uniqueness/all-role overlap gates, and explicit permission for scoring /
cached-background reuse. Exposed original background remains dependent/reused,
not fresh background-generalization evidence. No automatic scientific launch.
On failure, retain evidence and report the blocker without another session.
