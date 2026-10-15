# LatentTrigger — Task0057: Session Journal Ownership and Sequential Lifecycle Repair

You are continuing **LatentTrigger**. Perform **Task0057 only**.

## Objective and scope

Repair the session/case diagnostic ownership mismatch observed in Task0056 and qualify the **actual sequential controller lifecycle with generated inputs**. The missing evidence is two candidate cases in one subject/supervisor sharing session resources, not another pair of isolated serialized fixtures.

Task0056 remains **`partial_failed_development_hdf_pilot_v2`** and its P4 session is consumed. Preserve the valid **PCA component run**:63/64 completions,207real raw/feature rows,174public calls/342score rows/1368Booleans, all pre/post and63realized references, two successful custody passes/5816520818B. The overall pilot was not accepted. AE had a supervisor attempt but zero worker/payload/model/stream activity.

The observed AE failure was `Unregistered diagnostic descriptor` during tracker publication. RSS was valid13156352B, joint44711936B; no memory limit failure is established. Current source shows a session Journal lazily opening after a per-case descriptor snapshot; case cleanup unregisters/closes it while the Python object survives into AE. This is an observed lifecycle defect, distinct from Task0054's unrecovered exception/RSS.

This prompt authorizes focused ownership/lifetime/cleanup changes, deterministic regressions, actual shared-supervisor generated sessions with serialized artificial models, existing generated-core checks and own-resource observations. **No new P4:** no raw custody/hash, production HDF/metadata open, real membership/golden/features/scores/fingerprints/model-artifact loads, original frozen-model inference, training/optimizer/calibration/science, acquisition, replay, device survey or Task0058. No activation/reset/retry of Task0054/0056, and no recorder optimization or larger study.

## 1. Establish the real starting state

Read applicable instructions, `docs/development.md`, README, living memory and handoff index; inspect Git HEAD/branch/upstream/index/unrelated changes. Planning inspection on **2026-10-15 Europe/Rome** found clean `main` tracking `origin/main`, empty index, HEAD **`5e64b42a34fb7f2e09d9d657f1070e1025744c8f`**, Task0056 committed. Recheck actual memory revision and current facts; local refs do not prove fresh remote/push/CI. Task0055 commit `6ca5c347…` and older bases remain historical.

Save this actual prompt at `docs/prompts/0057-streaming-session-lifecycle-repair.md` and create an initial Italian handoff at `docs/handoffs/0057-streaming-session-lifecycle-repair.md` before substantive work.

Read Task0056 report/config/summary/handoff and relevant journal/quota/controller/core/fixture sources. Verify these anchors:

| Task0056 input | Bytes | SHA256 |
| --- | ---: | --- |
| `docs/development-hdf-consumer-pilot-v2.md` |15924|`e2c7015d5fcbcbe883ddfa6ee602e8989a10f4dc9513b44615d827daaf62655c`|
| `configs/streaming/development_hdf_consumer_pilot_v2.json` |48795|`94957be7cd28be616a83f90e3462b4a5d80becef9adfd2655a8c20af0df0b8c5`|
| `results/tables/final/task0056-development-hdf-pilot-summary.json` |253853|`4c1947b25be1784167170c932e6f7183e287a91f3de400cadf45a0913ef146db`|

Use curated evidence, not ignored old native/operational payloads. Preserve historical documents/configs/results/prompts/handoffs and the valid PCA facts. Version live repairs and source identity; do not retroactively qualify Task0056's session or claim real AE evidence.

## 2. Reproduce and repair the actual ownership defect

First establish a deterministic generated-file regression matching the original order: take the per-case snapshot, construct the session Journal, trigger its **first lazy write**, run case emergency cleanup, then publish the second candidate's tracker sample through the **same Journal object**. Retain the failure evidence before correcting it; no real source is required.

Moving the Journal object before the loop is insufficient if its descriptor still opens on the first write inside the case. Choose a small explicit repair: for example, create/register the session-owned descriptor before any case cleanup snapshot and close it only in the session finalizer, or use narrowly scoped ownership metadata that makes the same lifetime guarantee. Avoid a general resource-management framework or changing unrelated runtime/model code.

Define owners and lifetimes for session tracker/heartbeat/observer diagnostics, case records/mappings/output and child-local resources. Case cleanup retires only case resources; session resources survive every case until final teardown. Session teardown remains independent of case mutexes, publication acknowledgements and diagnostic success.

Require:

- One session journal allocation/registration, bounded generation/storage, publication across candidate boundaries and one final logical close/unregistration. No per-case re-create/truncate/reopen silently standing in for persistence.
- Journal remains writable/registered after PCA cleanup and before AE readiness publication. The second publication cannot depend on a new fd secretly substituting for the first.
- Idempotent safe close, partial setup, failed/short writes and stale-handle detection. If a numeric fd is closed/reused for another owned file, a stale Journal cannot write to or close that other resource. Use the minimum identity/ownership mechanism needed; do not weaken quota validation.
- Per-case mappings/descriptors/semaphores still retire, with no journal exemption that accidentally retains case leaks. Account for the persistent fd inside the existing descriptor cardinality/mapping limits.

Preserve typed tracker values, joint80MiB policy, CPU initialization/hash/thread pins,512B records/CRC/nulls,12,288B ring,64inclusive credits, FIFO/B8/1ms/open-loop and same-shaped reference behavior. Do not raise caps or alter timing criteria to pass.50/200μs remain diagnostics.

## 3. Test the shared sequential path, not isolated copies

Factor or reuse the **same candidate-loop/session-lifecycle function used by the operational controller** with an explicit generated-session context. Do not copy the loop into a test-only controller, call two independent command-line sessions, or supply separate tracker Journals per candidate. Generated context must remain a distinct immutable type restricted to owned fixture files; it cannot supply or fake P4.

Use existing serialized artificial PCA/AE artifacts, actual model-class serialization/from-artifact/public-score interfaces and strict dataset stand-ins. No original parameters, real source arrays or HDF file is required. Candidate labels indicate fixture roles; results are generated software evidence, not PCA/AE scientific comparison. Record creator/setup/model/reference work separately from stream offers.

A frozen qualification group contains:

1. **The existing12-case v2 generated-core suite**, because quota/case cleanup is shared. Keep expected injected invalidity and normal workload validity distinct.
2. **Normal sequential session:** generated PCA→AE in one subject/supervisor/ledger,64offers each at500/s, nominalB8, one shared tracker journal and the actual case-cleanup path between candidates. Both gates/stream/after-drain references/finalizers run. Verify tracker publications and journal identity before/after both cleanups and final session close.
3. **First-candidate failure session:** inject a declared failure in PCA's generated work. Verify configured versus issued work/uncertainty, case cleanup, session evidence/final close and that AE is not started under stop-on-first-failure policy.
4. **Second-candidate failure session:** let generated PCA finish and clean up, then inject a declared AE pre-worker diagnostic/publication failure. Retain the valid tracker observation and primary/report/cleanup outcomes, no AE payload/start, and independent final journal/resource retirement.

Use explicit fault/barrier controls and independent expected identities/counts. A normal session must have both candidate outcomes valid with all realized-group checks; do not assert exact contention/drop counts unless controlled. Expected fault sessions pass their **software expectations**, not session acceptance. Do not repeat failures until scheduling is favorable.

Pure tests additionally cover lazy-open-after-snapshot regression, case-owned versus session-owned descriptors, numeric-fd reuse, double close, unopened/partially opened journal, inter-case checkpoint error, missing report, quota exhaustion and session-finalizer close failure. Establish cleanup/ownership invariants, not just encoder round trips or mocked successful `write()` calls.

## 4. Prove scope and bound final qualification

All normal/error/finalization fixture paths deny production data/artifact/result payloads and original model/transform configuration opens, except code/curated metadata and the explicitly owned generated root. No raw hash or P4 activation can be reached from the new entrypoint. Imports/help/malformed calls remain inactive. Library imports and generated model-class work are allowed and reported positively.

Freeze current source/config/test/prompt identity before native work. Permit at most **two complete frozen qualification groups** for correctness repair. Each has12core cases and3sequential sessions: at most24core cases and6session checks overall, and at most **36 underlying candidate/core case dispatches**, counting failures/starts. Core cases≤128configured offers each; session cases≤64per candidate, at most128configured per session. Thus native configured offers≤**3840** overall (3072core+768session); report unattempted AE separately rather than pretending it ran.

Core case≤5s including cleanup; each complete sequential session≤20s including both cases/session cleanup. Whole externally observed generated qualification≤**280s**, covering at most120s core+120s sessions+40s setup/reporting/observer reserves. Both groups, source versions, attempted/unattempted cases and any additional native launches from tests count. Reuse the established external observer/typed resource policy; no extra standalone CPU bootstrap is necessary unless a runtime function is changed, in which case scope it inside the same budgets and report coverage explicitly.

Use one **32MiB whole-task pre-growth ledger**, covering all generated sources, models/setup, shared journals, per-case files, samples, snapshots, failures, reports/receipts/temp/curated copies and both possible groups. No per-session quota reset or evidence deletion. Keep existing FD/mapping/buffer/cardinality, role/aggregate RSS, primitive/lifetime, clock/monitor/operation/cleanup limits. Do not infer kernel bytes, exact heap/workspace or physical throughput from generated observations.

Complete deterministic tests/lint before the first group. If a correctness change follows, final qualification requires all12core cases and all3sequential sessions on the **same new final source bundle**. Earlier-source cases cannot fill final coverage. No source edit during a group; no third group/automatic budget extension. If constraints prevent completion, preserve a precise partial outcome, not a renewed real pilot.

Keep checks focused on changed shared code and relevant initialization/payload-denial regressions. No historical full-suite/native/model matrix, dependency install, performance search or broader framework refactor. Record numerical/array/model-class/score/setup activity in generated fixtures distinctly; no global-zero claim.

## 5. Deliver ownership evidence and the next decision

Create focused implementation/test changes plus:

- `configs/streaming/development_streaming_session_lifecycle_v1.json` — explicit owners/lifetimes, generated-only context, prospective sequence/fault matrix, source/prompt pins, budgets and operational flags false.
- `docs/development-streaming-session-lifecycle.md` — English report leading with the defect/fix, exact shared-path evidence, journal identity and resource retirement across candidates, failures/limits and no operational retry.
- `results/tables/final/task0057-streaming-session-lifecycle-cases.csv` and `task0057-streaming-session-lifecycle-summary.json` — actual attempts/source versions, each session/candidate boundary, shared journal allocation/publication/close evidence, generated work, accounting/resource/time/quota outcomes and remaining gaps.
- Actual prompt and self-contained Italian handoff; update README/index/memory in place from the verified revision.

Use **`completed_software_only_streaming_session_lifecycle_repair`** only after focused checks and the full final-source12+3qualification pass their software expectations. Separate readiness **`requires_fresh_bounded_operational_authorization`**. Real AE behavior, exact workspace/heap attribution and decoder effective threading remain unvalidated. Preserve the valid historical PCA run without promoting the failed two-candidate session.

If qualified, recommend one next narrow authorization to obtain the missing real AE evidence. Explain whether AE-only is sufficient for that question or whether a new two-candidate session is needed for a distinct controller/experimental claim. Do not automatically repeat valid PCA work, combine source versions into a fictitious paired experiment, grant P4 or launch Task0058/24-case study.

Preserve0056partial/consumed,0054failed/consumed and their distinct custody totals,0055historical startup qualification,0053v2qualification,0052partial/negative,0049CPU/synthetic closure,0036unresolved,0034gates,YES/YES/YES,particle192/192consumed/canonical deferral,0024accepted export versus0025failed performance and no MPS claim. No scientific usefulness/efficiency/causal nonlinearity/independent confirmation, detector readiness or official CERN/experiment affiliation claim.

Final Italian delivery must explain what ownership changed, why lazy opening mattered, actual sequential final-bundle outcomes and journal retirement, generated positive work and zero **new operational** custody/HDF/array/model/public-inference work. Preserve all historical positive PCA/custody activity. Verify historical hashes/local links and finish with exact **manual Git review, selective staging, staged review, Conventional Commit and push commands last**, excluding diagnostics/generated model artifacts/unrelated changes. Do not stage, commit, push or launch another task.

Proceed with **Task0057 software-only session lifecycle repair and generated sequential qualification**.
