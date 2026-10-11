# Task0030 — Sleep-aware three-prong acquisition v3 and verified prefix recovery

## Metadata and objective

2026-10-11 Europe/Rome; main tracking origin/main, base/actual HEAD
`01617d5e3312785800058ad3ce0a8ca52741dd0b`; index empty. Complete byte artifact
accepted, sole Task0030 session consumed; no scientific evaluation authorized/run.
Actual prompt saved byte-for-byte before work. Memory1.24→1.25. No commit/push/hosted
CI claimed. [Report](../three-prong-acquisition-v3.md),
[summary](../../results/tables/final/task0030-three-prong-acquisition-summary.json),
[attempt CSV](../../results/tables/final/task0030-transport-attempts.csv),
[protocol](../../configs/acquisition/three_prong_v3.json).

Implement/validate separate v3, then one conditional session from verified copied
Task0029 prefix with continuous sleep-inclusive timing and temporary idle-system
sleep prevention. Explicit user prompt authorizes the session after prerequisites;
no further general confirmation or exact postimplementation-hash approval invented.

## Initial state and preservation

Task0029 remains uncommitted: three modified living documents (README, memory,
index), thirteen intentional untracked files below. Exact initial status/index,
all318tracked hashes,13untracked hashes,146accepted source/dependency bindings,
Task0029 operational hashes and initial living-document byte copies are saved
ignored under data/task0030-validation/. No reset/stage/folding. Copies in
Task0029-continuation/ preserve that task's documentation for manual split delivery.
All prior frozen scientific/source/config/calibration/dependency/acceptance/receipt
records remain. Synced sources read-only. Task0025 failed/consumed/provisional,
0028/0029 failed/consumed, particle192/192consumed/canonical-deferred; original
exposureYES/YES permanent/new signal modelNO. No numerical population readers.

## Changes and technical decisions

Six new v3-only modules plus one synthetic test module. Pure existing strict
range/header/transient classification, owned-file/checkpoint mechanisms and exact
bounded HDF inspector reused; old v2 transport loop/supervisor/termination never
executed by v3. No old controller rerun or frozen-source patch. Dependencies unchanged.

Unsigned native mach_continuous_time ticks use integer ticks*numer//denom→ns
(125/3 here) before seconds. Continuous grants/checks cover pre/post IO, retries,
copy/hash, supervision, cleanup, exit, finalization, promotion and publication;
old exclusively-monotonic helpers excluded. Supplementary timer/poll quanta are
wake-up mechanisms, not sole elapsed enforcement. Late exit0/publication rejects.
A suspended host cannot be terminated; overrun after waking is disclosed/rejected.
Limits60simport/1800stransfer/60sverify/15sfinal/2000sreserved, cleanup2s inside caps.

Installed caffeinate/pmset/SDK clock declarations read. Scoped caffeinate-i-w parent
PID prevents idle SYSTEM sleep, permits display sleep; owned assertionID/active
state proven before reservation, inspected every5s by parent/worker, lightweight
helper/controller-presence checks at boundaries. Helper RSS/lifecycle separate.
No persistent power changes/admin/display assertion/simulated activity/app management.
Manual sleep/lid/other interruptions remain possible. Release TERM/KILL/reap and
owned-ID/PID absence proof precede accepted manifest; wait-PID releases on parent
exit, but abrupt death cannot supply confirmed-release/acceptance evidence.

Retry-After HTTP errors plus failed bodies of validated200/206 is explicit
prospective application policy. Delta anchors to header continuous receipt;
HTTP date converts once via header UTC with local UTC/date-precision uncertainty.
Wait=max(fixed5/15/30/60/60minimum after failure,remainingheaderinterval), never
reset shared deadline. Malformed/source/range/encoding/validator/storage/guard
failures stop; only fixed transient class may recover. Six requests maximum,
seven representations maximum, no deletion/reset/resume. A200 to Range starts
new owned file; exact206 alone appends; If-Range only strong ETag; final MD5 mandatory.

Distinct inode seed copy/size/MD5/SHA/checkpoint/post-reaping provenance confirmed;
never append/hardlink original. Imported/newreceived/written/fsynced/retained/
accepted counters separated. Fixed64KiB streaming buffer,8MiBcheckpoints /
64MiBguards each/1MiBlog each; worst budget1865478190B under2GiB free requirement.
6GiBworkerRSS/512MiBnative/128MiBstdlib parent; WARN advisory/CRITICAL veto/unknown
disclosed/invalid primary veto; no global RAM admission or idle-Mac prerequisite.

## Fresh sleep evidence, not historical rewriting

Narrow read-only pmset records confirm idle14:51:32→14:52:02(30s),
maintenance14:52:47→15:08:25(938s), sleep-service15:09:25→15:24:28(903s),
2026-10-11 Europe/Rome. Coarse sum1871s broadly accounts for Task0029 same-endpoint
UTC2305.963121−monotonic442.5587260829925≈1863.404395s. Installed Python ordinary
clock is mach_absolute_time; Apple's native declarations say continuous time
advances during sleep. Network-failure contribution plausible; exclusive cause
unproved. Task0029 historical cause-unmeasured report/receipts unchanged. Exact
bounded log lines/man pages/header copies remain ignored validation evidence.

## Validation before reservation and freeze

89 new synthetic cases; final1503full/1503portable (48.38/46.66s), lint,252-file
formatting, pip dependencies pass. Portable excludes data/artifacts/sources/.git/
.venv, uses unchanged historical CPU/MPS synthetic fixture plugin. Cases cover
continuous advancement while ordinary clock stationary, parent/worker after
suspension/late exit0, late promotion/publication,200/206bodytimeouts/truncation /
HTTPerror/date/elapsed Retry-After, six requests/shared waits, seed hash/MD5/inode /
checkpoint/inventory/symlink/reaping lineage, distinct-copy/history/foreign ownership,
range/validator failures, interruption/retention, assertion setup/loss/release.
No live-payload/host-sleep experiment. Self-contained toy mathematics are not
operational scientific population/model access.

Initial default-sandbox native diagnostic hit ps denial; finally-release returned
normally, initial detailed assertion record unavailable. Approved diagnostic then
proved creation/active/release (data/task0030-validation/native-bindings.json).
Final bounded native supervised synthetic integration exit0/reaped0.213169s,
RSS48218112/native50331648B,11WARN/no latch, active/released assertion and matching
synthetic byte/HDF metadata only. Preliminary suite/format records preserved;
minor pre-reservation validation repairs rerun, final acceptance only after checks.
No implementation/protocol changes after reservation.

153current source/dependency bindings have own acceptance, separate from historical
146-source/1414-test Task0029 and1259-test Task0026 scientific acceptance.
Protocol canonicalSHA268b946af53f3d907ca6153363874b2fae2b3221b2165d83e55184b612862043;
plan canonicalSHA34d98ab76b2bb80dc0503899933b8abd9132c9c7ede0e2af0d1831d41bfe5c12;
acceptance fileSHA1c8363b629f8a68a57238c4580732479a9431a85aea483e75d28d1da8baeefc9.
Actual conditional human prompt bound to these identities, exact-hash approvalFalse.
196historical protected bindings preserved; complete file/byte/canonical hashes
are separate in curated JSON. No hosted CI implied.

## Sole real session and measured outcome

Approved execution context; one9124Bprimary metadata GET, identity/provenance/
active assertion/storage prerequisites pass before reservation. Storage budget
1865478190B≤2147483648B, available277GB approximately. Real command invoked once:
`.venv/bin/python -m latenttrigger.data.three_prong_v3 --run-session --network-authorized`.
Driver exit0. Fixed reserved namespace, no retry/resume/next task.

Import worker exit0/reaped/accepted0.374776833s; copied29990748B into independent
seed inode; historical size/MD5/SHA retained. One payload request atUTC16:08:16.948266,
Rangebytes=29990748-, HTTP206 Content-Range29990748–235488993/235488994,
Content-Length205498246. Retry-After59 anchored at380825.699194916continuous /
UTC16:08:19.502330; body succeeds so no recoverywait. No ETag/Last-Modified/If-Range,
strong identity not claimed; no retries/restarts/redirects. Clear projectUser-Agent.
Transfer worker869.023110209s, exit0/reaped/parent accepted.205498246newreceived
plus29990748imported =235488994written/fsynced/retained/accepted; singleowned
representation, inflightnull. Unknown wire/internal buffering not counted.

Verify worker0.702536125s, exit0/reaped/accepted. Complete235488994B matches publisher
MD554e123a86143b668f9cb76905152a124 and localSHA
063fff3547d17bf4f36a40109e940ac6990105a0fe33a79f4f7c630905dd0742.
Independent worker verification and parent post-exit hash agree. Exclusive hard-link
promotion of task-owned seed.part only, accepted manifest requires accepted root
parent; original Task0029 inode stays distinct and unchanged. All predecessor /
source/grant/dependency/guard/time/exit gates pass; no checksum correction/retry.

Structure-only inspector: /df plus four hard-linked datasets, FP64[100000,2101]
values/chunks[31,2101]; int64axis0/items[2101],axis1[100000],chunks[8192];Blosc32001,
no virtual/external nodes. Compatible-looking supported structure; no label/axis/
particle values read, no schema expansion.100000shape is not valid/unique count;
2101column semantics/order/class/padding/uniqueness/overlap remain unverified.

Prerequisites2.193020s, reserved870.632494s, whole including prerequisites872.825514s,
ordinary872.825513916s (≈0.2µs discrepancy), finalization0.456040s; no overshoot.
Durable parent publication≈8ms later/postpublication continuous check passes;
terminal memory gaps0.036864625/0.020749875/0.030408750s separately disclosed.
These include network/custody/checkpoint/audit overhead, no inference benchmark.

Controller2179/helper2180 assertion0x0002700700019e1d,
174active observations, releaseUTC16:22:46.538078/continuous381692.7485185,
helper−15reaped/owned assertion absent before promotion. Exact ID is in the summary;
other applications' assertions are irrelevant and untouched.
MaxworkerRSS52232192B(49.8125MiB), maxnative46137344B(44MiB), parent36782080B
(35.078125MiB), helper sampled3227648B(3.078125MiB).19530WARN advisory,
0CRITICAL/unknown/guard latch; observed resource semantics/coverage caveats retained.

## Scientific access and limitations

Original test-background model/evaluationYES, original test-signalYES record the
existing Task0026 exposure. New three-prong model/evaluationNO; numerical preparation,
particle/axis/label dataset values, fingerprint/cache numeric loads, model scoring,
optimizer updates all0. Actual payload/prefix byte reads and structural scalar
attributes are separately recorded, never conflated with new model exposure.
No valid-event/uniqueness/overlap/class/padding/feature/model/scientific metrics or
new CPU/MPS/runtime/particle execution. No hard real-time guarantee, no host-wide
headroom or helper lifetime/native-heap certificate. Both original tests stay exposed.
Task0025failed/provisional,0028/0029consumed failures,particle192/deferred unchanged.

## Follow-up brief

Use the accepted local file/manifest/root parent, size/MD5/SHA above; no reacquisition.
A separate scientific protocol/source acceptance/namespace/explicit human consent
must define numerical custody/axis/label/padding/valid counts, new-source uniqueness
and all-role original-fingerprint overlap, fixed eight features/scaler, native
PCA-v1/AEv2/canonicalFP64SSE/strict>,4096complete-tail batches, PCA→AE→consolidate,
all four original thresholds/conditional intervals/prevalence-aware AUC/AP and
relative acceptance. Reuse exposed Task0026 background transparently; no independent
BG generalization/significance claim. No fitting/recalibration/response selection.
Old Task0028 reservation cannot resume. Brief only; no automatic next task.

## Files and manual Git delivery

Task0029 thirteen prior untracked files (unchanged):

- configs/acquisition/three_prong_v2.json
- docs/prompts/0029-three-prong-acquisition-v2.md
- docs/handoffs/0029-three-prong-acquisition-v2.md
- docs/three-prong-acquisition-v2.md
- results/tables/final/task0029-three-prong-acquisition-summary.json
- results/tables/final/task0029-transport-attempts.csv
- src/latenttrigger/data/three_prong_acquisition.py
- src/latenttrigger/data/three_prong_acquisition_protocol.py
- src/latenttrigger/data/three_prong_acquisition_worker.py
- src/latenttrigger/data/three_prong_acquisition_smoke.py
- src/latenttrigger/data/three_prong_transport.py
- src/latenttrigger/data/three_prong_structure.py
- tests/test_three_prong_acquisition.py

Task0030 thirteen additions:

- configs/acquisition/three_prong_v3.json
- docs/prompts/0030-three-prong-acquisition-v3.md
- docs/handoffs/0030-three-prong-acquisition-v3.md
- docs/three-prong-acquisition-v3.md
- results/tables/final/task0030-three-prong-acquisition-summary.json
- results/tables/final/task0030-transport-attempts.csv
- src/latenttrigger/data/three_prong_v3.py
- src/latenttrigger/data/three_prong_v3_protocol.py
- src/latenttrigger/data/three_prong_v3_runtime.py
- src/latenttrigger/data/three_prong_v3_transport.py
- src/latenttrigger/data/three_prong_v3_worker.py
- src/latenttrigger/data/three_prong_v3_smoke.py
- tests/test_three_prong_acquisition_v3.py

Overlapping three living documents: README.md, docs/project-memory.md,
docs/handoffs/README.md. Each already included Task0029 changes before Task0030;
full current versions combine both. Do not silently stage both tasks as one.
Manual split: save the final three current versions to a task-specific temporary
folder; restore the exact initial Task0029 versions from ignored
`data/task0030-validation/Task0029-continuation/`; selectively review/stage the
thirteen Task0029 files plus its three restored docs and commit that task. Restore
final three saved docs; selectively stage thirteen Task0030 files plus docs;
review unstaged/staged diffs/whitespace, commit Task0030, verified upstream
`git push origin main`. No commands executed automatically. Suggested messages:
`feat(data): add bounded acquisition v2 and retain failed prefix` then
`fix(data): acquire verified three-prong payload with sleep-aware bounds`.
Raw payloads/partials/manifests/acceptances/receipts/checkpoints/logs/validation
records remain ignored; never force-add. Exact final checks appended below.

## Final reconciliation

Final read-only checks pass: all315previous tracked files outside three overlapping
living documents, all13pre-existing Task0029 untracked files,146old source bindings
and196protected bindings unchanged. Current153frozen-source acceptance/plan/auth
still match; source/protocol unchanged since reservation. One request/one exact
206/group/cumulative counters/MD5/SHA/inode/post-exit/parent/assertion/shape/zero
scientific-access assertions agree across receipts/JSON/CSV/report. Summary uses
existing structural metadata; final filesystem verification is stat only, no
additional HDF value/particle/axis/label read. Full/portable suites are not replayed
after documentation-only edits; post-doc lint/252-file format pass. New CSV LF
normalization repairs reporting whitespace only (not frozen code or evidence).
Relative links, all13new-file whitespace checks and tracked diff checks pass;
raw/manifests/operational/acceptances remain ignored. main/origin/main/HEAD16…d0b
verified unchanged, empty index. Exact final-check JSON/log retained ignored;
no hosted CI or automatic Git operation. No Task0031 launched.
