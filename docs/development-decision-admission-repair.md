# Development-decision admission repair — Task0042

## Outcome and scope

Task0042 is a software-only repair of the emitted validation record and checked
synthetic launch path. It creates no replacement operational allowance. The
[actual prompt](prompts/0042-development-decision-admission-repair.md),
[handoff](handoffs/0042-development-decision-admission-repair.md) and
[curated summary](../results/tables/final/task0042-development-decision-admission-summary.json)
record final validation and lifecycle evidence separately from historical data.

The verified initial checkout was clean `main` tracking `origin/main`, commit
`a7ee0a23f92003a430a2570a233d08042f986e71`, committed Task0041, memory1.36.
Task0041's `8b6310d...` task-time base remains historical. Its issued software
checks passed, but its acceptance was not controller-admissible. Its sole actual
invocation remains `failed_prerequisites_no_retry`, consumed, with zero operational
numerical/model/raw work, header-only measured CSV and no cost figures. Task0040
remains the latest accepted raw boundary. No accepted joint raw-to-decision
sequence exists for replay.

## Demonstrated defects and narrow correction

The original producer emitted
`software_accepted_synthetic_development_raw_decision`; the consumer required
`software_accepted_synthetic_development_decision`. They were not tested together.
A freeze precheck failed; the agent then incorrectly continued to the actual
controller. That independent admission also failed and consumed the attempt.
Task0042 replaces the caller's need to notice an earlier command error with a
checked orchestration dependency. The additionally verified controller defect
was a hard-coded `task=0040` in Task0041 plans.

`development_decision_contract` is the authoritative schema/status/role contract.
Its typed canonical status retains the producer spelling. The shorter spelling,
unknown status, extra/missing fields, wrong role, malformed records and operational
permission flags are rejected. Record production is factored through the actual
Task0041 driver's `emit_record`; the new Task0042 driver and tests use that same
function, serialize the file, and consume it through `protocol.acceptance`.

The strict outer verifier checks the owned namespace, nonsymlink paths, current
source/package/native-build/config/prompt identities, all seven successful check
logs and their hashes, and the native receipt's hash, synthetic role, identity and
released assertion. Evidence must belong to that emitted record's directory;
absolute/traversal/foreign paths fail. Default production admission retains the
Task0041 namespace. Task0042 context admission is explicitly synthetic-only and
cannot authorize operational payloads.

Task, protocol kind, scope, config/prompt and validation-owner prompt are derived
from the bound contract and carried through plans, grants, worker receipts and
parent receipts. Fixture chain task is **0041**; repair/validation owner is **0042**.
The old `0040` plan value is not relabeled in preserved evidence. Current plans
reject it. Raw membership selection, feature arithmetic, model/threshold registry,
thread/cache/numerical rules, service timer boundaries, matrix and caps are
unchanged. Live changes are confined to producer/admission/controller/parent
receipt checks and necessary focused tests, with additive contract/coordinator,
validation driver and regression tests.

## Programmatic launch dependency

`admission.launch` performs real record verification, publishes an owned plan and
freeze, rereads and verifies both, and passes a sealed immutable result to
`dispatch`. Arbitrary Boolean/path inputs are not permits. A publication exception
retains rejected files and publishes no accepted plan/freeze. Changed record,
source, prompt, native build or frozen bytes, absent/partial freeze, copied
consumed markers and duplicate dispatch fail before the executor. An exclusive
claim permits only one dispatch. The native controller independently rechecks the
sealed result and claim before directory creation, guards, assertion or workers;
workers recheck admission freeze/claim and protocol identities before numerical
imports/access. Its historical one-attempt and normal exit/reaping rules remain.

The validation bootstrap is expressly an **unadmitted generated-fixture check**,
needed to create the native evidence for the immutable software record. It is
restricted to the Task0042 validation namespace, synthetic payloads and no
operational branch. After that record is emitted, the final driver runs the real
admission→freeze→dispatch path into a second native fixture integration. A separate
repair receipt binds the unchanged emitted record SHA256 and final roundtrip
workflow/freeze hashes, avoiding circular hashes or mutation after consumption.
The driver declares overall success only after this sequence succeeds.

Unit tests exercise observable leaf spies and actual controller pre-effect gates;
their zero launch assertions are not process-exit measurements. The native fixture
runs independently establish normal process exits, reaping, accounting and sleep
assertion lifecycle. Neither proves real-data parity or real chain feasibility.

## Preservation and validation

Before live edits, an ignored reproducible snapshot preserved all251original issued
source-map entries and159source/metadata/evidence files,9,663,647bytes including
manifest. Each entry resolves to exact preserved original bytes. Snapshot manifest
SHA256: `b3da104e9edaecd3e6bfe0681ec64429f150dad9e2ee2a26541ccfd2a30ff0ed`.
The issued record remains
`a86c964e9b6a4355c97c231c0617dda0ef5158ac529d5e7fe1c62bb2f5b08c4c`;
the consumed marker remains
`e12e95bf539b0ba1fbd4e4fec0d5f2b2aa5cc333abdcb219db784e2c9e8898c0`.
Original synthetic plans/receipts/logs, failure/diagnosis/workflow, prompt/config,
report/handoff/summary and empty CSV are preserved. Repaired live bytes are the new
version, not the historical failing source. No old actual CLI is invoked to test
refusal or changed bindings; generated roots/copy-schema markers are used.

Final status is **`software_accepted_synthetic_admission_repair`**, after actual
emitted-record admission, immutable freeze and parent-accepted native dispatch.
Fresh validation: **172focused (64new cases),2482full and2482portable tests**, all
seven checks passed;256source/config/prompt/test bindings,43package versions and
41native-file identities. Record SHA256
`42cc5f1a971c0b681af7063d778d35984f37cc330a7cc03aac513b0231e36338`;
final repair-receipt SHA256
`37066812e3ca68572f08b007f38561c1c1e400dc8ad839e9d9e09ef659ecdb0d`.
The immutable record was not modified after consumption.

There are six native synthetic invocations: one preserved0.560781s failure
(relative owned path rejected before fixture setup), then five accepted runs:
15.561767s preliminary;15.407424/16.563599s version1 bootstrap/roundtrip;
15.163858/15.978458s final-version bootstrap/roundtrip. Normal exit0/reaping is
verified for all four workers in every accepted run. Failed child exit1/reaping,
assertion release and zero fixture setup are preserved. Its256-entry failed-source
map is recoverable. Relative paths are normalized without weakening checks.

Version1's accepted source map/record/receipt are preserved separately. Final
review made grant-native-build equality and top-level plan config/prompt/kind
consistency explicit, with four additional cases, then reran all final suites and
both native integrations. Version1 is historical synthetic evidence, not the final
current-source acceptance. No operational trial occurred during either version.

Each completed integration has24cells/480timed/72warmup calls,840selected fixture
reads and840feature constructions/35490rows,984public services/41574rows and
166296decision Boolean values, plus24setup read/construction calls/3072rows.
Across five accepted integrations there are4920fixture services/207870rows,
30canonical fixture-model loads and30fixture creator instances. No fitting in
the native chain. These are generated fixture results, not operational costs;
existing reporter figures remain ignored, with no new curated timing CSV/figure.

Final roundtrip numerical workers take4.373124/4.207041/4.249469s and reporting
1.558678s, reserved15.624468s/whole15.978458s, overshoot0. Peak worker RSS
391184384B, native194887680B, controller47349760B, owned output4203652B.
All fixed caps remain unchanged:60s prerequisites/180s numerical/60s reporting,
720s reserved/780s whole, cleanup2s, RSS1GiB/native512MiB/controller128MiB,
arrays64MiB/journal16MiB/log1MiB/output128MiB. Final workers have1222NORMAL samples,0WARN/CRITICAL/unknown; earlier-version
WARN samples remain advisory. Final query-start gap0.089210s and terminal gap
0.236458s. Across successful runs the largest such gaps are0.114797s and
0.307231s; monitoring is sampled, not continuous coverage. Optional RAM context
is unavailable rather than an admission floor. Assertions are released/reaped/
confirmed absent in all six invocations, including failure; final roundtrip has
six active observations, permits display sleep and changes no persistent settings.

Two interrupted-publication cases and nine absent/partial/changed-freeze cases
verify zero downstream executor/controller/worker calls. Three actual native-entry
pre-effect tests independently verify zero reservation/custody/assertion/dispatch.
Positive fixture dispatch occurs once; duplicate claim/copied consumed marker are
refused. These unit spies remain distinct from the native exit/reaping checks.

Artifact-free full and
portable suites exclude operational `data`, `artifacts`, `models` and checkpoints;
historical fixture model activity is separate from operational counters. Installed
package/native-library byte identity reads are metadata custody, not raw source
hashing. No dependency installation, web lookup or download occurs. Across two software versions, each of four full/portable
instrumented research subset runs records85fixture-model instances,31forwards/8710rows,
31reconstructions,2toy optimizer steps and2toy calibrations. The plugin excludes
other historical models and native subprocesses; these are not global totals.
There is no global-zero numerical/model/optimizer claim.

Reproduce software-only validation with
`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m scripts.validate_development_decision_admission`.
It creates a fresh ignored validation directory; it never creates an operational
campaign. All real controller/reservation/worker calls, membership/golden/raw
numerical loads, raw hash passes, real HDF opens, operational feature/forward/
reconstruction/decision/optimizer/calibration/scientific/fingerprint work and
downloads in Task0042 are zero.

## Remaining decision

Successful software admission establishes compatibility and fail-closed control
flow. It does not establish operational feature/score/decision parity, joint cost,
production latency, independent confirmation or deployment policy. A new real
campaign requires a separate explicit user prompt, new namespace, current-source
acceptance/freeze and one new allowance. No campaign namespace/live grants are
created here; Task0041 remains consumed. No Task0043 is launched.

Task0036 remains `unresolved_no_acquisition`, Task0034 gates are unchanged,
Task0032 stays complete, Task0033 exploratory, test exposure is permanently
YES/YES/YES, Task0025 stays failed and particle192/192 consumed/canonical-deferred.
