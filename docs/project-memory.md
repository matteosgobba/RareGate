# LatentTrigger - Living Project Memory

> **Purpose:** This is the maintained, project-wide memory of LatentTrigger. It preserves the project's intent, scientific contracts, architectural decisions, rationale, current canonical state, and future direction. Read it at the start of a new implementation or planning session, and update it as part of every task that changes project state or understanding.
>
> **This is not a task handoff.** Handoffs record what happened during individual tasks. This file explains what the project is, why it is being built this way, what remains to be established, and how the accumulated evidence should guide the next task. It complements the existing handoff system without replacing or duplicating it.

## Document control

| Field | Current value |
| --- | --- |
| Intended repository path | `docs/project-memory.md` |
| Memory revision | 1.35 |
| Last factual verification | 2026-10-13, Europe/Rome |
| Last completed phase | 0040 — one accepted/consumed development selected-raw/read/feature/joint measurement; exact golden parity, no models or held-out work |
| Latest task outcome | Separate authenticated payload protocol/current-source100focused/2310full+portable/236bindings43packages31native files/native synthetic accepted. One19.498497s real session/18.003004sreserved/0overshoot:3membership20997IDs/3golden3072rows,1024approved384rawunique,732rawrequests30927rows/768featurecalls32448rows/36cells720timed108warmups; exact72pre-post gates and unchanged raw2SHApasses5816520818B/3HDFhandlesclosed. Pooled B128read45.143/features5.778/joint50.013ms, all repetitions/outliers retained. WARNadvisory/caps/4normal exits/reaping/7assertion observations/release pass; decoder/cold-I/O/physical bytes unknown. Three inspected figures; Task0039/0038/0037/history preserved, scientific source/gates unchanged |
| Verified repository branch | `main` |
| Verified HEAD / Task0040 base | `90868d6e75fcb298fa7e606dce00ad3457f8374e`, committed Task0039; clean main/origin/main/empty index at start. Task0039 historical292a7e9base/resolver/acceptance and Task0038history unchanged.483initial tracked byte hashes excluding two operational model contents;480nonliving preserved and model paths Gitunchanged,17Task0039/20Task0038nonliving paths preserved; three living updates separate. No Task0040stage/commit/push/hosted CI claimed |
| Current compact neural baseline | `compact-autoencoder-v2` |
| Particle model state | Design/code retained; local canonical execution deferred under unchanged contracts. Two disposable real96step characterizations, same1024IDs;749.343s/240.728s fail180s;192/192 consumed. Convergence/usefulness unresolved; no canonical training/freeze/calibration |
| Next action | Separate prospective joint selected-raw→unchanged frozen features→original frozen native CPU adapter/four decisions design on the same approved development windows, with exact feature/decision/model/source gates, access caps/current-source acceptance/freeze and one new authorization. No Task0041launch, scientific/held-out/source-acquisition/deployment selection, Task0037rerun or sum of separate medians. Task0036unresolved/Task0034gates unchanged |
| Real test evaluation exposure | PermanentYES/YES/YES from Task0026/0031. Task0033 added3feature requests/350471rows/6stored score loads/700942values plus3membership arrays/3300000records. Task0034/0035/0036/0037 add zero operational population/features/scores/membership/fingerprint/model/reconstruction/calibration/evaluation/optimizer/event-payload work. Task0035 has separate authorized synthetic work/12native completed steps; Task0036 has1metadata-card download16084B. Task0037 reads accepted curated timing/produces synthetic streams; permitted artifact-free historical model regressions have forwards/updates, separate from model-free simulator. Task0038 adds authorized prepared-development engineering reads/inference:15708public adapter calls plus separately accounted FP32/FP64 full/local proof work, no new held-out/population/optimizer/calibration/scientific/download activity. Task0039 adds one6999-ID numeric metadata load/1024prefix, one raw2908260409B hash and HDFmetadata open; zero event/golden/model/scientific/fingerprint numeric work. Synthetic full-particle/legacy model regressions remain separate. No global-zero numerical/forward/update/download claim; samples cannot be reblinded Task0040 adds authorized development-only3membership/3golden loads,732rawrequests30927row presentations/768feature constructions32448rows, zero operational model/held-out/optimizer/calibration/scientific/fingerprint/download work. |

The HEAD above identifies the implementation snapshot used to establish this memory. It is not a claimed commit for this document. Recheck Git and the latest project files before starting new work. Do not infer a push or hosted CI result from a local commit or a configured workflow.

The earlier planning conversation stopped at Task 0007 and described Task 0008 as pending. Local repository inspection established that Task 0008 had subsequently been completed and committed. This memory therefore incorporates that result while preserving the historical v1 baseline.

## Contents

1. [Start here: current project state](#1-start-here-current-project-state)
2. [Vision, motivation, and research question](#2-vision-motivation-and-research-question)
3. [Objectives and definition of success](#3-objectives-and-definition-of-success)
4. [Scope and non-scope](#4-scope-and-non-scope)
5. [Overall architecture and repository structure](#5-overall-architecture-and-repository-structure)
6. [Development platform, stack, and resource constraints](#6-development-platform-stack-and-resource-constraints)
7. [Dataset identity, schema, and acquisition decisions](#7-dataset-identity-schema-and-acquisition-decisions)
8. [Frozen population protocol and test embargo](#8-frozen-population-protocol-and-test-embargo)
9. [Frozen preprocessing and feature contracts](#9-frozen-preprocessing-and-feature-contracts)
10. [Implemented foundation and evidence](#10-implemented-foundation-and-evidence)
11. [Canonical model registry and measured results](#11-canonical-model-registry-and-measured-results)
12. [Evaluation, calibration, and uncertainty](#12-evaluation-calibration-and-uncertainty)
13. [Hardware inference and deployment methodology](#13-hardware-inference-and-deployment-methodology)
14. [Reproducibility and artifact governance](#14-reproducibility-and-artifact-governance)
15. [Decision register: choices and rationale](#15-decision-register-choices-and-rationale)
16. [Roadmap, milestones, and next-task definitions](#16-roadmap-milestones-and-next-task-definitions)
17. [Observations, risks, and open questions](#17-observations-risks-and-open-questions)
18. [Development workflow and mandatory Git delivery](#18-development-workflow-and-mandatory-git-delivery)
19. [How to maintain this living memory](#19-how-to-maintain-this-living-memory)
20. [Instructions to future ChatGPT/Codex sessions](#20-instructions-to-future-chatgptcodex-sessions)
21. [References and memory revision history](#21-references-and-memory-revision-history)

## 1. Start here: current project state

**Project:** LatentTrigger - *Hardware-Aware Machine Learning for Real-Time LHC Event Selection*.

**Core objective:** Investigate how much anomaly-detection performance can be retained when models are constrained by inference latency, throughput, memory, and deployment practicality.

**What exists:** A verified LHCO source, deterministic duplicate-safe population assignment, frozen preprocessing/stores, frozen PCA/compact AE v2 and calibration, reproducible CPU training, historical MPS compatibility, an audited future final-evaluation gate, and a complete accepted arithmetic-aware frozen CPU v2 reference with three independent repetitions per model; historical partial PCA1data remains separate. Task0023 CPU/MPS foundation is implemented/software validated, with a blocked sole availability check and no physical device numerical proof or paired timing. Task0024 adds an accepted ONNX CPU reconstruction artifact. Task0025 implements and measures all 90 paired CPU cells with passing numerical gates, but ORT3 fails process-exit supervision: only descriptive timings, no accepted performance comparison.

**Canonical models:** PCA with six retained components; compact AE v2 with architecture `8 -> 6 -> 3 -> 6 -> 8`, 155 parameters, best epoch 381, stopped at epoch 396 under the unchanged patience rule. AE v1 is retained as historical evidence, not the current compact AE.

**Particle/set design:** Task 0009 selects a 478-parameter equivariant particle autoencoder with local dimension 2 per retained particle and eight masked-mean context values. Corresponding-particle reconstruction avoids set matching; its total code is 2n+8, not an event-only eight-value compression. Task 0010 implements and synthetically validates this unchanged design. Its launch failed at 3.694794 GiB versus the frozen 8 GiB minimum before any real read/update. Task 0011 adds source-bound preflight and one fixed lineage-bound recovery route, with 296 synthetic tests. Initial readiness samples failed at2.9495–3.0176GiB. Explicitly resumed after user-reported reboot/manual preparation on2026-10-07, one new bounded check measured4.6485/4.6248/4.6819GiB: launch8GiB still fails while continuing4GiB passes. No recovery attempt was reserved. Task0012 reviewed a separate engineering launch admission of4.5GiB (4GiB+512MiB) with every other limit unchanged, but its historical2.5836/2.5443/2.6967GiB readiness failed the original floor as well; no reader/dev stage began. At Task0012, v2 was provisional/not activated and dev feasibility/canonical stages remained pending. Task0013 implements a stdlib-only controller without changing the sidecar/scientific/shared code. One data-free three-configuration experiment measured a319.391MiB lower own-parent lifetime peakRSS than the legacy shape, but fully prepared lightweight worker availability3.220428/3.177795/3.244232GiB still fails4.5GiB and4GiB. Those are initial task-time observations. The later external Task0013 invocation is now consumed: pilot8.8140/8.7283/8.6975GiB, dev64/full custody pass, v2 bound190340736bytes≤512MiB activates bounded dev only. Three1024 training passes/96started+completed updates/one score pass finish, then conservative749.3431957854029s projection fails180s. Memory success does not erase throughput failure; no canonical convergence/freeze/calibration. Task0014 reconciles this history and tests a cached-binding v3 with471synthetic tests and exact numerical parity; isolated/check cost improves but complete synthetic workload does not. Historical host variation is not causally attributed. Task0015 explicitly versions50ms system host sampling with≤100ms query-start age and fresh process/pressure checks, preserving numerical/scientific limits. Paired synthetic medians0.381356958→0.178179666s improve2.1403× but miss the required3×; no real readiness/plan/slot/data/update. Final532tests pass; failed-process peak reporting corrected with preserved original matrix and affected-only validation. Task0016 prospectively supersedes synthetic3×admission for one diagnostic, without calling Task0015 passed or introducing2×. Separate typed authorization/current576-test acceptance adopts unchanged v4; one automatic readiness guard observes3.558060GiB and fails the4GiB floor before stable3readings/reader. No new real data/steps, current/cumulative96, one additional replacement slot unreserved. Its later manual check also failed before data on pressureWARN2, with no admitted available-memory sample;3.558GiB is only the automatic observation. Task0017 preserves/reconciles both and fixes readiness history: explicit repeatable checks never start data/reserve, separate run always performs a new check and uses the same canonical slot.612tests pass; sole read-only integration3.705841GiB fails floor,0newreal work/slot. Task0018 explicitly versions dev-only512MiB RSS/256MiB native envelopes, global available memory context only, WARN advisory/CRITICAL veto/unknown disclosed.670tests pass; one real shared-host characterization finishes96new updates with exact Task0013 diagnostic parity,370.016MiB RSS/179.672MiB native, then240.728359s projection fails180s. Canonical Task0016 anchor consumed, cumulative192/192, no further granted steps. See [shared-host policy/evidence](particle-shared-host-policy.md). See [readiness workflow](particle-readiness-workflow.md), [runtime characterization](particle-runtime-characterization.md), [bounded sampling](particle-bounded-sampling.md), [the design](particle-set-baseline-design.md), [implementation](particle-set-baseline.md), [historical recovery](particle-set-resource-recovery.md), [memory-policy review](particle-memory-policy-review.md) and [host readiness](particle-host-readiness.md) and [monitor performance/manual reconciliation](particle-monitor-performance.md).

**Accepted scientific evaluation:** [Task0026](guarded-pca-ae-evaluation.md) Phase A implementation/1259full+portable tests/130-source freeze/one custody readiness is followed by actual explicit human approval of planSHA2c97dc2a…62e3d86f. All source/science/dependency/plan bytes match; readiness reused, no repeated readiness action. One31.094950s final campaign completes native PCA→AE→reporting, each exit0/reaped/parent_accepted.4requests/124complete4096-tail batches/500942presentations/250471unique held-out events; both tests now exposed, no unknown inflight/optimizer/recalibration/candidate selection/replay. PCA AUC0.468488658/AP0.364379155, AE0.660063803/AP0.547427268, evaluated test prevalence0.399247817. AE higher sampled frozen-threshold signal acceptance at all four targets, modest discrimination/very low tight-tail sensitivity; different6vs3latent capacity and higher historical accepted CPU cost prevent a causal nonlinearity/universal superiority claim.

**Completed integrated study:** [Task0027 synthesis](scientific-synthesis.md) joins accepted Task0026 canonical B4096 quality to accepted Task0022 prepared-dev adapter costs B1/8/32/128/1024. Nine source-byte hashes and separate scientific/config/calibration identities, ten cost rows/all three worker distributions, all eight original thresholds/counts/conditional Wilson intervals and two inspected figures are curated. Post-evaluation descriptive arithmetic at strict AE threshold:56/100000signal versus116/150471background, TPR0.00056 < FPR0.0007709126675572038, relative acceptance0.726411724137931, selected56/172=32.558139534884% below39.924781711256% initial mixture. No observed enrichment in this slice; no ratio/significance/physical-purity claim. Other three AE points have observed descriptive enrichment; none is selected. New population/scoring/custody/optimizer0; 12 new synthetic aggregate-helper tests are separate from historical1259acceptance, which is preserved/not rerun.

**Three-prong extension software and consumed attempt:** [Task0028](three-prong-generalization.md) implements the separately authorized prospective frozen-signal extension, preserving the completed initial study. Fresh official API confirms v5/6466204/235488994bytes/publishedMD5`54e123a86143b668f9cb76905152a124`/CCBY4.0; publisher declares100000W′→XY,X/Y→qqq events. Task0028 established no local payloadSHA/count/layout/class/overlap result; Task0030 later establishes complete byte integrity and structure-only metadata below, while numerical/class/uniqueness/overlap were still unmeasured at Task0030 completion. Task0031 now accepts all100000valid/unique/disjoint rows and the separately authorized science below. Candidate/transform/calibration identities unchanged, strict FP64 SSE/native CPU. New signal has separate source/scientific identity; original validators retain original training provenance. Supported pandas-fixed singleFP64block widths2100/2101/700slots, labels absent→publisher class provenance or present→all1. Table/mixed/external/wrong-layout/source/count/structure gates refuse; exact new-source uniqueness and all-role original-fingerprint overlap gate before scoring, no subset/retry. Accepted original background score files are pinned by bytes/header/count150471 and scientific/audit/parent lineage; Phase A numeric reuse0, original fingerprint payload access0. New stdlib parent/acquire→prepare→PCA→AE→consolidate, one native worker, durable separated exposure/inflight, normal exit/reaping acceptance. 300/180/120/120/30s stages/900s whole,6GiB RSS/512MiB native/128MiB parent/2s grace inside caps; no global RAM floor/idle wait. 62new synthetic cases and1333full/portable tests, lint/format/dependencies/protected toy pass; own139-source acceptance. Human approval of plan77f92d95…179fa9 was recorded, source/acceptance/plan identities verified at actual Phase A commit e381f54, then one Phase B reserved. Acquisition interrupted at298s operation deadline inside300s cap, exit1/reaped/parent rejected; whole298.116751583s, failed_consumed_no_retry. Log≥47185920B transferred; frozen cleanup removed its own .part. All surviving logs/guards/audits/receipts preserved. No verified payload/localSHA/HDF/count/uniqueness/overlap, no preparation/originalFP numeric load/model scoring/cache numeric reuse. Raw potential_inflight retained; no live worker/model inflight. Observed39.4375MiB RSS/44MiB native/28.484375MiB parent,5494WARN advisory,0CRITICAL,terminal gap0.020402125s; memory observations do not erase deadline failure. Task0028 itself yields no new-signal scientific measurement; Task0031 below subsequently supplies an accepted separate campaign. Planned scope is signal topology generalization with reused exposed background, not fresh background generalization or independent comparison.

**What does not yet exist:** A trained/frozen particle baseline; controlled CPU/MPS comparison; CoreML export or an accepted ONNX performance comparison; quantization; NVIDIA/TensorRT or FPGA measurements. Task0037 synthetic queue simulation and Task0038 prepared-row service measurement now exist; full-chain/device/production variability remain unmeasured.

**Scientific boundary:** Model development used background only. Task0026 Phase B subsequently evaluates the predeclared frozen candidates with explicit human authorization, both held-out populations fully exposed. No training/selection/calibration population reread or test-guided refit/threshold/candidate selection. Failed/partial exposure would still count; this campaign completes without uncertain inflight. Integrity custody remains separately counted: Phase A1plus two approved candidate constructors, not three model population requests. Future new model design needs a separate methodological decision and new evaluation protocol/population; these tests cannot be reblinded.

**Decision and next:** [Task0022](frozen-cpu-benchmark-v2.md) explicitly authorizes and implements a prospective arithmetic-aware CPU v2 policy, derived/tested with operation-level outward bounds and independent local/decision checks; old source/loader/kernel/model/threshold/scientific contracts remain unchanged.942full/portable tests and one fixed four-family/two-model synthetic study pass before96-source freeze. A new independent25.661481s campaign completes90cells/18000timings/1800warm-ups/1200empty pairs; all six workers pass pre/post gates, exact same-shape/reference identities and zero sampled frozen decisions. Source preparation opens original1024rows once and copies bytes; six local reads,0new population/custody/optimizer. [Task0020](frozen-cpu-benchmark.md) remains failed/partial/consumed15/90cells; [Task0021](ae-batch-parity-review.md) remains complete/consumed and its v1 failures are not relabeled. [Task0023](frozen-cpu-mps-benchmark.md) implements the isolated device foundation/policy/scopes and104-source software freeze. Its sole fresh check observes built=True/available=False; original receipt also fails because the helper compares raw build-text SHA with CPUv2's canonical JSON-string SHA. Stored build text is identical, not evidence of runtime change. Original code/acceptance/failed receipt are preserved; software comparison corrected and1033full/portable tests pass, no device replay. No synthetic physical study, real input/reservation/paired timings or current device acceptance. [Task0024](frozen-ae-onnx-cpu-export.md) verifies Task0022/0023commits and adds7missing ONNX packages without changing36prior distributions/core requirements/builds.1111full/portable tests and guarded synthetic smoke pass before114-source/dependency freeze; one19.407739saccepted attempt produces11464B/opset18/IR10/fourGemm+twoRelu/exact155FP32parameters. Four fixed synthetic families then1193real windows across five batches pass local/outward/repeat/strict frozen decisions;1prepared-array read/1024unique reused rows/0population/custody/optimizer/performance timers. Cross-runtime errors are bounded, not byte identical or a universal certificate. [Task0025](pytorch-onnx-cpu-benchmark.md) now validates 1179 full/portable tests and freezes 121 applicable source/dependency files before one paired campaign. All 90 cells / 18000 measurements / 1800 warm-ups / 1200 empty pairs and six pre/post gates complete with zero four-threshold mismatches. ORT3 writes a completed receipt at 10.072625084 s but fails to exit; parent terminates/reaps it at 58.030580209 s, exit −15. Whole 128.780991583 s, consumed/no retry, no accepted paired speedup. One original + six local prepared reads / 1024 unique reused rows / zero population/custody/optimizer. Task0024 commit cacaefd3 is verified; historical source/results/receipts/science unchanged. [Task0026](guarded-pca-ae-evaluation.md) now completes authorized Phase B after130-source/plan/acceptance recheck and actual recorded human consent. Original Phase A commit e69d80ed/readiness is preserved/reused; two necessary fresh full-store candidate constructors are distinct from repeating readiness. All three final stages parent-accepted/exit0/reaped,31.094950s≤600s, observed maxRSS2917859328B/native264339456B/parent30343168B within6GiB/512MiB/128MiB, terminal sampling gaps0.338450/0.268159/0.292505s disclosed.4test requests/124score batches/500942presentations/250471unique held-out rows/0unknowninflight/optimizer; final slot consumed, no replay. PCA ROC-AUC0.468489/AP0.364379; AE0.660064/0.547427; evaluated test prevalence39.924782%. Frozen1e-3 operating points: PCA124background/2signal (FPR0.082408%/TPR0.002%); AE116/56 (0.077091%/0.056%), low absolute sensitivity. All original thresholds retained; empirical ROC cutoffs are descriptive only. **Task0027 completes that integrated synthesis/frontier**, from accepted0026tables/figure and0022CPU context only, without further population/scoring/custody/optimizer work. The user explicitly selected Task0028 Phase A, a narrower three-prong topology extension with reused exposed background; its implementation/139-source software acceptance remain valid, but the explicitly approved sole Phase B acquisition failed at its frozen deadline and is consumed, without preparation/scoring/cache reuse or new scientific results. No retry/resume, new threshold/model selection or hardware prerequisite. [Task0019](particle-canonical-feasibility.md) particle deferral remains under unchanged180s/10hfit/1hpostfit/22htotal/max200/patience20/min_delta0;192/192consumed/0inflight/remaining. No idle Mac/readiness dependency or scientific-quality/trigger claim. Final responses follow the informative planning-handoff preference in [development.md](development.md#standing-delivery-preference).

### How to interpret the statements in this file

- **Frozen:** An established contract to reuse. Changes require an explicit, versioned methodological decision.
- **Implemented / measured:** Supported by source, artifacts, task reports, or actual execution evidence.
- **Planned / proposed:** Future work, not an implemented feature or an achieved result.
- **Open:** A question that the existing evidence does not answer.

Current user instructions and applicable repository instructions govern execution. This memory provides continuity; it is not blanket authorization to unblind tests, change frozen protocols, commit, push, or perform unrelated work.

### Separate acquisition v2 — Task0029 failed/consumed session

Task0028 remains failed/consumed and old139source/receipt/scientific bytes unchanged.
Its actual continuation was committed as01617d5; Task0029 starts clean, independently.
Explicit new user prompt authorizes one new source-bound session after own146-source /
1414full+portable/81new-case/native h5py metadata toy acceptance; same v5file /
235488994B/publisherMD554e123…a124. Fixed new namespaces, ≤3payload requests /
1800s shared transfer,60s verification/structural metadata,15s parent/1900s whole,
6GiB RSS/512MiB native/128MiB stdlib parent/64MiBguard journals/8MiBcheckpoints,
855364774B disk capacity. Exclusive retained representations, durable differentiated
received/written/checkpointed/retained/verified bytes, validated206or retained200
restart, fixed5/15backoffs/Retry-After, redirects refused; no old retry or broader
recovery framework. Actual prompt binding is conditional execution authorization,
not human approval of a subsequently generated exact hash. Approved network context /
pinned9124BAPI connectivity confirmed before reservation. Sole session failed /
consumed:3requests, initial200then valid206/206 at27000832/28770304,2readtimeouts /
truncatedEOF,2continuations,0restart/redirect.29990748Breturned-application received /
written/durable/retained after reaping, accepted verified complete0; partialMD5
andSHA2be92f0d…6d549 preserved, no deletion/manifest/promotion. Exit1/reaped/parent
rejected; transfer442.666572s, finalization0.043759s, whole445.572426s measured
monotonically. Same recorded first-request→last-checkpoint UTC span2305.963121s
versus442.558726s monotonic; cause was unknown at Task0029, no uninterrupted UTC wall-budget pass. Task0030 later verifies system-sleep records read-only; it does not rewrite the historical report.
Observed35.453125MiB workerRSS/44MiBnative/35.421875MiBparent,7877checks(NORMAL7228 /
WARN649/CRITICAL0/unknown0), no guard latch, terminal gap0.013391709s. Third EOF
leaves final inflightnull, all confirmed prefix bytes fsynced; earlier failed-read
wire/internal buffer bytes unmeasured. Frozen retry_delay reads Retry-After on
HTTPError only, recording200/206headers58/59/59 without using them in timeout /
truncation backoff; do not claim generic compliance. At Task0029 these and clock semantics needed versioned review/testing before
new authorization. Separately authorized Task0030 completes that work below;
no post-reservation patch/replay of Task0029 occurs. Byte verification/HDF structural phase unstarted. No dataset/axis/particle/label values,
numerical custody/preparation/FP/cache/model/scoring/optimizer/scientific metrics.
Original testsYES/YES permanent,new signal modelNO; failed0025/0028 andparticle192
unchanged. Future science needs separate explicit custody/overlap/scoring protocol /
namespace/acceptance/authorization; no automatic launch.

Task0029 acquired no verified local235488994Bcopy. Preserving/byte-hashing an
incomplete prefix is not numerical custody, valid-event count/overlap or model
exposure. Task0028 remains separately failed/consumed; future reuse of Task0029
partial was not automatic; Task0030 explicitly authorizes a distinct verified-copy
policy/session. Its later success does not relabel the failed Task0029 artifact.


### Sleep-aware acquisition v3 — Task0030 complete byte artifact

[Task0030](three-prong-acquisition-v3.md) is separately authorized and complete.
Own153-source/dependency acceptance,1503 full/portable tests,89 new synthetic cases,
lint/format/dependencies/native continuous/assertion bindings and0.213169s guarded
metadata-only toy integration pass before source/protocol/plan freeze. All146 old
Task0029 source bindings and196 protected files remain unchanged, including its
acceptance/failed receipts/29990748Bprefix. Three overlapping living documents are
saved before editing for a selective manual two-commit delivery; index stays empty.

Fresh narrowly bounded pmset history confirms2026-10-11idle sleep14:51:32–14:52:02,
maintenance14:52:47–15:08:25 and sleep-service15:09:25–15:24:28. Coarse1871s broadly
accounts for prior UTC-minus-monotonic1863.404395s; network-interruption contribution
is plausible, exclusive causation unproved. Python ordinary monotonic is
mach_absolute_time; v3 uses mach_continuous_time with integer125/3 timebase→ns,
then seconds, throughout grants/IO/waits/supervision/cleanup/acceptance. UTC is
context/header-date anchor. Late exit0/publication rejects, suspension overshoot
is disclosed; software cannot terminate a sleeping host. Temporary caffeinate-i-w
assertion prevents idle system sleep and permits display sleep; actual pmset ID is
verified before reservation and every5s, helper lifetime/RSS separate, owned
assertion release is mandatory before accepted promotion. No persistent settings,
app cleanup/admin/user-activity changes or real host-sleep experiment.

One primary metadata check in approved context, storage277GBfree/2GiB required,
then sole session import→transfer→verify. Distinct prefix inode copied/byte-verified;
one206 at29990748, exact Content-Range/Content-Length205498246, weak/missing
validators disclosed. Retry-After59 anchored to header; body completes,0retry/wait/
restart/redirect.205498246 newly received plus29990748 imported =235488994 written/
fsynced/retained/accepted. Complete publishedMD554e123…a124 matches; localSHA
063fff3547d17bf4f36a40109e940ac6990105a0fe33a79f4f7c630905dd0742.
Historical prefix unchanged; new complete .part/promoted filename share only the
new owned inode. All3workers exit0/reaped/parent-accepted,0inflight. Continuous
import0.374777/transfer869.023110/verify0.702536/finalization0.456040s, reserved
870.632494s≤2000, including prerequisites872.825514s; ordinary clock differs≈0.2µs,
no overshoot. Publication/terminal observation gaps separately recorded.
174 owned active assertion observations, release confirmed/helper−15reaped/absence.
Max worker49.8125MiB RSS/native44MiB; parent35.078125MiB;19530WARN advisory/
0CRITICAL/unknown/no latch; helper sampled3.078125MiB, no hard-real-time guarantee.

Exact unchanged structure inspector sees /df plus four hard-linked datasets,
pandas-fixed FP64[100000,2101], integer axes/items and Blosc32001; no external or
virtual dataset.100000 is shape, not valid/unique count; column/label semantics,
axis values/order, padding, integrity custody, uniqueness/overlap are unmeasured.
Byte reads and bounded fixed-scalar structural attributes occur; particle/axis/
label dataset values/preparation/fingerprints/cachedBG/models/optimizer/science0.
Original exposureYES/YES permanent, new signal modelNO. The initial scientific
report remains complete; no new AUC/AP/efficiency or inference cost is claimed.
Next brief requires separate local-file numerical-custody/overlap/scoring protocol,
acceptance/namespace/explicit human consent; old Task0028 reservation cannot resume.
Signal generalization uses exposed Task0026 background, not independent BG evidence.
Task0025failed/provisional,0028/0029consumed failures,particle192/deferred unchanged.


### Frozen local three-prong scientific evaluation — Task0031 completed

[Task0031 report](local-three-prong-evaluation.md) completes one separately
prospectively authorized local scientific campaign. Clean main/origin/main at
actual c825445; Task0029/0030 are committed, no obsolete restoration.153old source /
dependency bindings and all original science/data/receipt identities preserved;
161current bindings have own1590full/portable/87new-case acceptance, native continuous
synthetic integration/visually inspected figure before source/plan freeze. Actual
prompt bound to final plan1b10e4fe…99125, exact-postimplementation-hash approvalFalse.
No operational numerical access/model instantiation before freeze; byte/header /
manifest/accepted-parent checks only. No download/fitting/recalibration/selection.

Accepted local235488994B/MD554e123…a124/SHA063fff35…0742 streams101source chunks
(100×992+800), labels1,axes ordinal/source row order, all100000finite/nonempty/valid,
all invalidity categories0. Exact original FP64/signed-zero/phi/order fingerprints:
newduplicates0,all-role original1100000overlap0. Specific disjointness, not complete
statistical/simulation independence. PhysicalFP32storage after sourceFP64sorting /
wrapping, then full-eventFP64aggregates/frozen logs/scaler/finalFP32features; no
truncation or accuracy-path substitution. New prepared scientific identity retains
distinct source/compatibility; genuine original manifest validates training provenance.
PCA6/AE8→6→3→6→8/155/nativeCPUFP32forward/FP64SSE/highorientation/strict> unchanged.

prepare13.821576/PCA2.452941/AE2.267475/consolidate9.886448s, all4exit0/reaped /
parent-accepted; reserved29.058839≤600s, includingprereq29.607650s,no overshoot.
Two signal requests,25batches each24×4096+1696,50batches/200000presentations /
100000unique rows. One originalFPnumeric load1100000, twoBGcache numeric loads /
300942records, zero newBGforward/oldsignal numeric load/optimizer/download.
Columns/items4202 and rowaxis100000 numerical checks separately accounted;
2constructor/provenance checks/2ownedcurve/reporting loads. No uncertain inflight.
All3model-access statuses nowYES, permanently.7active idle-system assertion samples,
display permitted/release confirmed; no persistent setting/app/admin changes.
MaxworkerRSS512.203125MiB/native307.828125MiB/parent30.0625MiB within6GiB/512MiB /
128MiB;1498WARN advisory/0CRITICAL/unknown/no latch. Terminal gaps0.468708/0.337721 /
0.231515/0.283458s scoped; no hard-real-time or host-wide certificate.

PCA ROC-AUC0.4629531325637498/AP0.36022029761655994; AE0.5858771149922577 /
0.479971651666809, mixture100000/(150471+100000)=39.9247817113%, not physical rate.
PCA orientation not inverted. AE higher ranking/more signal at all4frozen cuts,
but both lower than two-prong globally and at every original operating point.
PCA signal3942/762/43/1 versus same14922/7362/1416/124BG; AE16438/10326/2662/34
versus14793/7357/1424/116BG. Every BGcount exactly reproduces Task0026; shared
historical FPR/conditional Wilson evidence, no independent replication/background
generalization or new significance. Strict AE TPR0.00034<FPR0.0007709127,
relativeacceptance0.44103569/selected34/150=22.6667%below initial39.9248%: no
observed enrichment in that slice. First3AEpoints descriptively enriched; no
winner threshold chosen, no multiplicative headline from PCA's1accepted signal.
Preregistered TPR/FPR/selected-fraction arithmetic has no invented ratio/modeldiff /
AUC/AP CI; Wilson conditional rates exclude calibration/model/simulation uncertainty.
Empirical attainable FPR/TPR points retain old tie/plateau/strict conventions and
are descriptive, never new calibrated cuts. Full ROC/PR+all4markers/prevalence
figure inspected; fourCSVtables/summary/hashes curated after root acceptance.

Observed AE advantage persists for these signals but weakens on three-prong;
6vs3latent dimensions/unequal capacity and residual magnitudes do not isolate
nonlinearity. Representation/bottleneck/score explanations remain hypotheses,
feature-level bias/other populations/physical deployment unmeasured. Task0022
accepted prepared-feature CPU costs are historical context; campaigntimes are
not inference benchmarks. Task0032 subsequently completes the offline combined
synthesis from accepted aggregates; no automatic successor. Future model development needs explicit methodology
and independent population/evaluation protocol; these evaluated samples are not
fresh tuning sets. Task0025failed/provisional,0028/0029consumed failures,0030accepted
acquisition,particle192/canonical deferral retain their actual historical outcomes.

### Integrated two-/three-prong synthesis and decision brief — Task0032 completed

[Task0032 report](two-three-prong-synthesis.md) closes the frozen baseline study
within its declared scope, using accepted Task0026/0031 science and Task0022
native CPU costs. A separate helper reads exactly 20 byte-pinned curated reports,
summaries, CSVs and PNGs, with input/output boundaries and symlink refusal. It
compares recorded model/config/calibration/store/scaler/cache identities without
following operational paths. Task0027 and all historical evidence remain unchanged.
Four global rows, sixteen calibrated points, eight descriptive topology comparisons,
ten adapter cost groups and three inspected static figures are curated. All four
thresholds and copied conditional Wilson intervals/rejection factors are retained;
28 descriptive empirical points remain separate from calibrated cuts.

AE ranks and accepts more signal than PCA on both declared samples, but the
advantage and absolute efficiencies are weaker on three prong. New Task0032
arithmetic is post-evaluation description: AE AUC change −0.0741866875 and AP
change −0.0674556167, with no significance/causal-topology claim. At strict AE
cut, two prong56/100000 and three prong34/100000 are below shared background
116/150471. Relative acceptance0.7264117/0.4410357 and selected fractions
56/172=32.5581% /34/150=22.6667% are below initial39.9248%; no observed enrichment.
First three AE points show descriptive enrichment for both signals, no winner
threshold. Avoid multiplicative claims from PCA's two/one strict-tail signals.

Cost remains historical prepared-feature CPU adapter B1/8/32/128/1024, three
worker medians/means and all outliers retained. B1 median of worker p50s8.125µs
PCA/24.708µsAE; pooled throughput uses600invocations and B/pooled mean, not
inverse median or averaged reciprocals. Quality reference is B4096, not new
quality at each cost batch. No combined utility score/deployment optimum,
end-to-end/trigger-rate claim or campaign-duration inference benchmark.

All three exposure states remain YES historically; new population/score-curve /
fingerprint numeric loads/model scoring/optimizer/download counts are zero.
Fresh focused synthetic validation is separate from historical scientific acceptance;
no campaign/full-suite rerun, hosted CI or dependency change is implied. Shared
background, exact-disjointness limits, preselected simulation, unequal6/3capacity,
residual-scale ambiguity and conditional-uncertainty limits remain visible. No
feature mechanism is measured; representation/bottleneck/tail explanations remain
hypotheses. Task0025/0028/0029 failures, Task0030 acquisition and particle192/192
consumed/canonical deferral remain intact.

Task0032 recommended an explicitly bounded exploratory diagnostic. The subsequent
actual Task0033 prompt authorized that extension; it is now completed below.
Independent background/signal generalization and physical deployment remain open
separate objectives; particle needs a new feasibility/budget decision.

### Exploratory frozen-feature and score-tail diagnostics — Task0033 completed

[Report](exploratory-feature-score-diagnostics.md) and
[curated summary](../results/tables/final/task0033-exploratory-feature-score-summary.json)
record one parent-accepted8.778443s continuous session after fresh200-source /
43-package acceptance and actual prompt-bound plan freezing.90specific/179focused
and1728full+1728portable artifact-free synthetic checks pass; native integration
verifies owned assertion creation/loss protections/release. Both real workers
exit0/reaped/accepted;1GiB RSS/512MiB native/128MiB parent limits pass, all observed
pressureWARN advisory, no overshoot. Sampled query/terminal monitoring gaps remain
visible; no hard continuous memory or physical suspension certificate.

The narrow reader never constructs the broad processed store. Frozen role4/5
membership, labels, complete ascending IDs and accepted per-batch ledger/source
code prove original alignment; accepted preparation/evaluation binds complete
three-prong source order.3feature populations/350471rows and6score arrays /
700942values are numerically read once, with separate3full membership loads /
3300000records. Whole-file hashing/header checks are custody, not population
numerical access. Reporting reads owned aggregate CSVs only; no per-event export,
new forward/reconstruction/AUC-AP/significance/fingerprint/optimizer/download.

24feature/6score marginals and48average-rank associations describe frozen
standardized FP32 inputs with FP64 accumulation, original log channels and no
physical inverse. Two prong has lower multiplicity than three prong(medians−0.680 /
−0.146), while both eta-spread marginals are nearly equal(−0.797/−0.795). AE score
medians1.237BG/2.009two/1.577three coexist with BGp99.9above both signals. AE signal
multiplicity rho−0.411/−0.299 and signed-eta/spread rho≈−0.25…−0.29 generate
hypotheses, not feature importance, residual attribution or causal topology proof.

All24strict original tail counts exactly match Task0032.16of192feature profiles
are null/suppressed for PCA’s strict2/1event signals;20event reporting convention
is not confidence. Strict PCA background concentration median5.494 occurs despite
weak global rho. AE strict BG/two-prong balance medians3.298/7.021 contrast with
three-prong−0.138 and its signed eta median−1.862; mechanisms/joint covariance /
capacity remain unresolved. No tail repair, candidate/feature/cut selection or
independent confirmation. Both readable median/IQR and quantile figures are
curated; the third heatmap fails visual curation because its colorbar overlaps,
remains ignored/unchanged, and all48coefficients are delivered in the table.

At Task0033 completion, the next decision was a separately authorized independent-
confirmation protocol with representation/capacity controls. Task0034 now supplies
that design below. Permanent exposureYES/YES/YES and historical consumed failures /
particle192 are preserved; Task0033 had no successor launch, retry, source or plan
mutation after reservation.

### Controlled activation follow-up — Task0034 design completed

[Protocol](controlled-follow-up-protocol.md),
[design-only sidecar](../configs/research/controlled_follow_up_v1.json),
[source registry](../results/tables/final/task0034-confirmation-source-registry.csv)
and [curated summary](../results/tables/final/task0034-controlled-follow-up-summary.json)
fix one question: two ReLUs versus identities at the same existing locations,
same8→6→3→6→8 biased layers/155parameters/bottleneck3, seeds1729/1730/1731.
Paired named initial tensors and actual loader-permutation hashes, exact Adam /
batch4096/max1000/patience15/min_delta0, own selected-state restore and own four
background thresholds are required; all six fits reported, no best seed/ensemble.
Old AE/PCA-six stay frozen references. Optional PCA-three is a separately identified,
calibrated leading-three-axis derivative, not parameter matched; no numerical
components inspected. Activation includes optimizer/checkpoint interaction, not
global optimization or causal physics. Eta symmetry, residual attribution and
richer particles remain deferred.

Primary alpha0.001 compares equal-weight paired TPR across the three fixed pairs,
with six realized background FPRs. Shared event-level acceptance differences,
empirical Bernstein bounds and family error allocation0.05 preserve dependence;
same events are not3N. Conditional uncertainty excludes calibration/training /
simulation uncertainty. All six background bounds must fit[0.00075,0.00125],
paired FPR upper≤0.0001; practical nonlinear TPR advantage requires lower>0.0002,
signal halfwidth≤0.0001 plus source/precision/lifecycle gates. Negative,
equivalent and inconclusive outcomes are specified. All secondary cuts reported
descriptively; Wilson overlap alone cannot establish improvement.

Three primary Zenodo records/16file rows are metadata-verified, zero accepted.
Preferred route is additional612858Cartesian full-event QCD rows restricted to
mJJ3.3–3.7TeV plus newly generated XtoYYprime. New signal jet-constituent versus
full-event coverage, units/counts/SR membership/generation runs, overlap and
expanded storage are unresolved. Old R&D EFPs remain exposed events; public BB
keys do not restore challenge blindness. This route could support independent
discrimination in a transported SR, not replication of the original topology
pair. Conservative planning needs≥236843signals even at zero observed variance;
variance0.001 scenario needs1450034. Publisher's≈20000analysis subset is not total
source count and insufficient for the specified precision. Fresh BG with old
signals supplies only fresh-background-rate evidence.

Task0034 makes24logical URL/GET attempts plus6text finds, including3accepted API
JSON bodies/30856bytes; no payload/key rows/archives. Nineteen synthetic
assertions,35rate/28variance scenarios/five minimum-N solves and design checks
use curated/config/source text only. No tracked code/dependency/new controller /
plot/full operational suite. Historical input bytes are preserved except intended
living documents. At Task0034 completion, implementation design was ready and
Task0035 was proposed without launch; the subsequently authorized foundation
is completed below. Six-fit development projection603s/fit→900s cap /
6600s whole/3GiB RSS is based on Task0008 aggregate evidence with explicit safety
assumptions, not Task0033 or particle timing. Confirmation8400s/16GiB working
envelope is conditional and ungranted; source counts/storage can invalidate it.
Continuous deadlines/scoped verified sleep assertion/release and parent lifecycle
remain required. Acquisition, development and confirmation need separate scopes.

### Controlled activation synthetic foundation — Task0035 completed

[Report](controlled-activation-synthetic-foundation.md),
[implementation config](../configs/research/controlled_activation_synthetic_v1.json),
[summary](../results/tables/final/task0035-controlled-activation-synthetic-summary.json)
and [handoff](handoffs/0035-controlled-activation-synthetic-foundation.md) record
additive research helpers only. Six Task0034 raw artifact identities remain
prerequisites; original model/training/evaluation validators/controllers unchanged.
Strict two-arm/three-seed/CPUFP32/155parameter recipe is separate from the fixed
two-epoch tiny profile. Own independent initial tensors, actual shared-generator
consumed orders/4096+1tail, strict15nonimprovement/earliest ties, own finite JSON
selected states and restored score identity, FP64-before-subtraction SSE and
once-only own four higher/strict thresholds pass synthetic checks. Python/NumPy /
TorchCPU RNG/thread/deterministic state restores; other-device RNG untouched.

64ordered pattern counts use exact Python integers/rational moments, preserving
shared-event seed dependence/Nnot3N. Original empirical Bernstein family0.05 /
unclipped precision and numerical gates remain; explicit precedence/eligibility
reasons cannot accept a source or issue an actual confirmation claim. All64patterns,
opposing/fully correlated seeds,10^25sparse counts and236843zero-variance floor /
all variance planning cases tested. No p-values/AUC/AP/subgroups/plots; unit
numerics are not coverage proof or causal physics. PCA-three unimplemented.

Final219bindings/43packages/189focused/1917full+1917portable/lint/format/dependencies
acceptance is fresh; complete suites are artifact-free with the unchanged portable
legacy schema plugin. Three native invocations: sandboxps assertion accounting
failure then __main__ child-dispatch failure, both before numerical work and both
released; corrected final source accepted/exit0/reaped,2.683233swhole /
2.515030sdispatch/2.270242sworker,12started+completed/0inflight,9research instances /
65forwards+reconstructions/2333rows/6calibrations,3historical reference forwards
separate. Each final pytest process has85research instances/31forwards/8710rows /
2updates/2calibrations; unrelated legacy/earlier repair work outside counter scope.

Observed RSS373604352B/native171622400B/controller30064640B pass1GiB/512MiB /
128MiB;102NORMAL, no WARN/CRITICAL/unknown. Owned assertion3active observations /
release confirmed/display permitted/no persistent settings; cleanup0.000094s /
overshoot0. Sample gap0.107453s and terminal0.245562s disclosed; optional global
RAM query prohibited by child policy/context unavailable, never admission. No
physical suspension/performance/real-fit projection claim. All detailed failed /
accepted receipts/maps/checkpoints/journals ignored.403historical tracked bytes
except three living docs preserved; original arrays not opened/modified.

Zero operational work, permanent exposure/baseline/failed campaigns/particle192
unchanged. Source/model freeze and real execution remain absent; source full-event,
independence/count/overlap/precision/storage blockers persist. Next source-adequacy
go/no-go before any separately scoped background-development implementation /
execution/acquisition/confirmation; no automaticTask0036.

### Confirmation-source feasibility — Task0036 completed

[Decision brief](confirmation-source-feasibility.md),
[evidence table](../results/tables/final/task0036-confirmation-source-evidence.csv),
[summary](../results/tables/final/task0036-confirmation-source-feasibility-summary.json)
and [handoff](handoffs/0036-confirmation-source-feasibility.md) fix
`unresolved_no_acquisition` for the existing extra-QCD/XtoYYprime route, with no
source acceptance/model freeze/operational permission. Task0035 was subsequently
committed as34d7401; its historical base/acceptance and all16nonliving Task0035
files are preserved;419old tracked nonliving files match their initial bytes.

The publisher-linked exporter at author commit6ed1f07 reads every EFlowTrack /
EFlowPhoton/EFlowNeutralHadron object, including outside the two selected jets;
≤700 zero-paddedFP32 triplets are compatible in principle. Above700 it retains
highest-pT700 then shuffles, incompatible with all-particle construction for those
events. Actual overflow/release production binding remains unknown; selected-jet
intermediate arrays cannot substitute. ROOT/card branches offer an untruncated
alternative in principle, without verified members/adapter/counts/storage. Extra
background declares full-event Cartesian2100+14fields/612858SR rows, but explicit
units/dtype/overflow and strict leading-jet/SR identity need binding.

XtoYYprime card requests50000events/automatic seed0; realized generation, detector,
trigger, strictSR and available totals are unknown. This is no certified upper
bound, so no mathematical count no-go is asserted. If50000were selected total,
minimum signalh0.0004736924 would fail fixed0.0001.236843zero-variance floor and
1450034forV0.001 remain;4Mcap does not guarantee precision. BG612858individual
h≈0.000185777 at assumedalpha variance may meet individual precision; paired
precision/background-band/independence remain unobserved. No threshold/family /
practical-effect/eligible-signal/SR amendment or original topology replication.

Three same-date metadata bodies/30856B reused;18logical retrievals/0searches /
3text finds,16direct capped20sHTTP requests/153614receivedB. One16084B card archive
has pinnedMD5/localSHA; conservative suffix preflight fails and archive route
stops without widening/retry/extraction. Separate pinned repository card texts
give recipe evidence, not executed logs. Web cache/physical requests/bytes unknown.
Known source bytes7589821691=7.068572GiB do not bound selected expandedROOT/HDF /
scratch within7GiBextraction/16GiBworking/20GiBadmission. No source payload/header /
range/key rows, operational arrays/models/generation/fits/evaluation or author
message.26temporary archive-boundary tests/35scalar monotonic+10integer boundaries,
30signal/12BGscenarios/CSVroundtrip/visual/JSON-link-identity checks; no full1917 /
native rerun, tracked code/dependency/controller or scientific plot added.

Next prerequisite is one publisher-bound representation/run/count/SR/overflow /
selected-member-size manifest. Hold acquisition/training for this claim; if that
cannot be supplied, prospectively amend/retire the claim or separately budget a
fresh-generation design. Background-only stability remains a separate conditional
possibility. The synthetic foundation stays valid. No automaticTask0037; permanent
YES3, completed baseline/exploratory status, failed campaigns and particle192 remain.

### Synthetic trigger/queue engineering study — Task0037 completed

[Report](synthetic-trigger-simulator.md),
[fixed config](../configs/simulation/synthetic_trigger_v1.json),
[scenario table](../results/tables/final/task0037-synthetic-trigger-scenarios.csv),
[summary](../results/tables/final/task0037-synthetic-trigger-summary.json) and
[handoff](handoffs/0037-synthetic-trigger-simulator.md) advance an explicitly chosen
engineering branch independent of the unresolved scientific source. No publisher
research/acquisition/source acceptance, real model execution, benchmark or change
to Task0034's alpha/arms/seeds/uncertainty/effect/precision/SR protocol.

One integer-ns FIFO nonpreemptive server includes waiting+actual in-service events
in1024capacity, drop-tail admission and completion-before-arrival-before-dispatch
ties. B1immediate; other batches flush from oldest original arrival, including
expired timeouts after busy periods and final partials. Partial m≤B pays frozen
B-slot constant service, no tensor/model padding; all admitted events process
before four strict Uniform toy cuts. Combined dispatch wait and full latency /
strict1msmisses have explicit completed/selected/generated denominators; drops
excluded from survivor latency but reported alongside. H and full-drain accounting
are separate; startup/drain and seed variation prevent stationarity guarantees.

Three curated SHA-pinned timing files/accepted Task0022 lineage/unique90cells /
Task0032 agreement supply only30adapter cells. Count-weighted600invocation means,
Decimalupward ns rounding/all repetitions+outliers retained. Main324scenarios
uses18PCG64separate-stream traces/90000events reused; stress54uses fixed worker
mean/p99/max at Poisson100000/B128/100µs. New simulator models/forwards0; six
curated loads across2actual sweeps plus six preparation inspections, byte custody
separate. The same18hashes are generated twice/180000materialized events;756actual
scenarios/3780000presentations; finalcurated378rows/1890000presentations.

B1 at1M/s loses67.44–67.78%PCA/76.64–76.72%AE under assumed means, while low-rate
B1024/100µs has0loss but≈0.19%slots used. Low-rate1000µsflush can cause1msdeadline
misses without overflow. Constant AE2/B128max26.2485ms yields79.18–79.36%loss /
≈227ms survivorp99; its worker p99 constant has0loss but100%deadline misses.
These finite what-ifs establish neither recurring stall frequency/cause nor policy
winner, whole-detector latency, physics acceptance or service distribution.

Final105targeted/2022full+2022portable/200source/config/prompt/43package-version
acceptance covers new code; complete suites artifact-free. Existing controlled-
activation helpers per final full/portable process have85instances/31forwards /
8710rows/2started+completed updates/2calibrations; other legacy synthetic activity
unquantified, no globallyzero regression model work. Historical1917acceptance not
reused. First native5.535386s numerical acceptance preserved; figure title/legend
overlap rejected forcuration. Layout-only repair/revalidation yields final6.105818s,
both phases exit0/reaped/accepted; identical CSV, all3finalfigures visually pass.

Final simulation/report dispatch3.308455/2.446330s, RSS52527104/129613824B /
native41943040/102039552B, parent39075840B, ownedstorage5536034B. Trace object
payload estimate6122304B≤16MiB,1GiBRSS/512MiBnative/128MiBparent/128MiBstorage
caps pass.2912WARN advisory/0CRITICAL/unknown, no primary error; optionalRAM context
unavailable because worker children forbidden. Sample gaps0.052096/0.107185s /
terminal gaps0.049905/0.061834s; cleanup0.000482/0.000112s andovershoot0. Six owned
active assertion observations/release/absence/helperreap/displayallowed/settings
unchanged. No physical-suspension or empirical inference performance certificate.

Five uncommittedTask0036specific files and419oldtracked nonliving files preserve
initial bytes; shared README/index/memory1.32 updates are separate. Task0036route
stays unresolved/unaccepted, baseline/exploratory/permanentYES3/historicalfailed
campaigns/particle192 preserved. Next separate development-only variability /
missing-chain-cost planning decision; no automaticTask0038 or deployment choice.

### Prepared-batch service engineering — Task0038 completed

Task0037 is now committed at84252b62; Task0036`2427373` andTask0035`34d7401`
are committed predecessors. Their task-time bases/acceptances remain unchanged.
Task0038's original user prompt authorizes a single development-only session
after fresh acceptance/freeze. Same existing prepared1024source-ordered dev-training
FP32 rows, original PCA-six/AE-v2/threshold/scientific identities; no raw/processed
store, population selector, IDs/memberships/fingerprints/scientific stored scores.

[Report](prepared-batch-service-measurement.md), [config](../configs/benchmarks/prepared_batch_service_v1.json),
[cells](../results/tables/final/task0038-prepared-batch-service-cells.csv),
[summary](../results/tables/final/task0038-prepared-batch-service-summary.json) and
[handoff](handoffs/0038-prepared-batch-service-measurement.md) bind the new scope.
Owned natural m×8 or padded B×8 with trailing FP32zero, canonical public adapter
plus four strict decisions, first-m result retention; padding is synthetic
standardizedzero and never useful events.17fixed cases/three paired sequential
workers/50timed+10warm-up observations per cell. New shapes retain unchanged
Task0022 rowwise outward AE policy/local checks and PCA tolerances, exact
same-shape/full-reference identity and zero actual-row decision mismatches.

One real sessionf7dd29ca6a234c22a3b3e84972993ac1 is consumed and parent accepted:
204cells/10200timed/2040warm-ups/600empty pairs;3array loads/3072rows/1024unique;
6canonical models plus6FP64diagnostic copies. Public adapter12240service+3468proof
=15708calls (7854each); direct AE1158FP32/PCA1158reconstructions, diagnostic
582FP64full/2328local-affine calls. Service1722960actual+855360dummy rows; all
canonical/proof/layer presentations2517696actual+1496790dummy, local layers
count separately. Not new population rows. No operational fitting/optimizer/
calibration/AUC/AP/significance/download/test/signal/selection/fingerprint access.

Fresh final acceptanceb696a315…558d:100focused/2122full+2122portable,211bindings/
43versions, lint/format/dependencies,9.1953s native synthetic acceptance before
freeze; four synthetic native invocations preserved, two preliminary failures
and two accepted integrations with different validated sources. These are not
real retries. Legacy synthetic fixture forwards/updates remain explicitly separate.
No source changes after real reservation.

Whole43.942592s/prerequisites3.750415s/reserved40.192176s/finalization0.077323s;
repetition dispatch12.571306/12.701193/13.007320s, reporting1.565194s, exits0/
reaped/pre-post/resource/deadline/owned assertion release pass. PeakRSS369934336B,
native184205312B, parent53477376B; owned27307794B,26400NORMALpressure samples,
WARN/CRITICAL/unknown0, overshoot0. Query and terminal monitoring gaps disclosed;
globalRAM not queried/no floor.18assertion observations,helper−15/reaped/absent,
display allowed/settings unchanged. Timer resolution about41.667ns inspected
after session in same pinned runtime; empty pairs never subtracted.

B1024/m1whole-batch pooled means17.570/64.592µs PCA,39.320/111.707µs AE
(natural/padded); slot utilization0.09765625%. Near-full contrasts small/mixed,
including AE128/127natural+1.4077µs slower. Worker variation and maximaPCA266.750/
AE243.083µs retained.50serial calls/cell/150pooled are not i.i.d. production
service samples or historical-stall explanations. Three inspected figures,
all204worker cells/68pooled groups/102paired summaries curated; raw sequences/
receipts/maps ignored. Task0037 constants/scenarios/figures are unchanged; no
deployment policy or scientific protocol/source amendment. Next separately
source/membership-bound raw-read/feature-construction design; no0039 launched.

### Development raw-feature foundation — Task0039 completed

Task0038 now committed292a7e9; its84252b6historical task-time base/acceptance and
one consumed measurement are preserved. Task0039 [report](development-raw-feature-benchmark-design.md),
[config](../configs/benchmarks/development_raw_features_v1.json),
[summary](../results/tables/final/task0039-development-raw-feature-summary.json) and
[handoff](handoffs/0039-development-raw-feature-foundation.md) add eight helpers,
validation entrypoint and three tests, with no operational raw measurement CLI.

One authorized1.867575s metadata resolution, after88focused/2210full+portable/
223bindings/43packages/31native binary/config identities/synthetic HDFintegration:
original6999little-endian IDs loaded once/allunique/in-domain/source-sorted; first
1024bytes reproduce f80a9483 and accepted Task0020 preparation/dev scientific
identity2eb34e5b. Original config has no dev-ID hash field: explicit dev/split
manifest hash plus config development recipe/count/full-role map binds identity,
no missing-key fallback or broad store/validator. Selected IDs/windows ignored.

One raw SHA256 pass2908260409B matches original5da8fda2; one readonly metadata
HDFopen verifies1100000×2101FP64/chunks62×2101/Blosc32001/unchanged filter parameters/
nonalias paths/effective1MiB521w0.75/closure. Dataset value methods disabled, no
axis/event/label/particles/feature/golden/fingerprint/other member/model access.
Byte custody warms caches and is not event analysis or read-feature timing.
NumPy/HDF5/h5py/hdf5plugin/Blosc build identities pinned; effective decoder threads
unknown despite requested environment1/queriedBLAS, no single-thread-decode claim.

Synthetic selected-row adapter guards role/hash/strict increasing max128approved
IDs before backend. Exact list selection, contiguous slice only if every row
approved, background truth excluded fromfeatures. UnchangedFP64source sort/wrap/
FP32physical/allparticles-before384/FP64aggregate/log-scaler/finalFP32chain; exact
synthetic cross-B/golden-position parity, no tolerance extension. Two native
synthetic integrations accepted/32feature constructions each; one driver precheck
key error corrected before acceptance, no operational attempt. Legacy synthetic
forwards/updates separately permitted; final instrumented full/portable subsets
each85models31forwards8710rows/two toyupdates/two calibrations (not total all tests).

Current resolver1load6999IDs/1024selected, raw payload rows/golden/scoring/features/
models/optimizers/calibration/science/fingerprints/downloads0. Dispatch1.629382s/
worker1.585261/prereq0.116615/final0.074625/cleanup0.000436/overshoot0; RSS60309504B,
native50331648B,parent31604736B,owned1479180B; NORMAL1653/WARN1153advisory/CRITICAL
unknown0, sampledgap0.055287/terminalgap0.044664s. Three idle assertion observations
thenhelper−15/reaped/absent, displayallowed/no persistent settings or RAMfloor.

Prospective36cells720timed108warmups overB1/8/32/128/threewindows/threeworkers,
read/feature/joint scopes with fixedforward/reverse ordering/cache/handle lifetime.
Count all552timing rawrequests23322rows+36bufferreads1521+144gate reads6084=
732requests30927selected rows;552timing featurecalls23322+216gatecalls9126=
768calls32448rows. Futurethree6999IDloads20997records/golden3loads3072rows;
1024approved but384unique rawwindow rows,312chunks. Nominal1042096B/chunk,
repeated no-cache decoded upper26307713520B≈24.500967GiB is geometry, not actual
decompression/I/O or neighboring Python exposure. PerB128raw2.15MB/threebuffers
6.45MB/conservative64MiBown arrays;180worker/60report/15final/720reserved/780whole
with60prereq and original RSS/native/controller/storage caps are proposals, not
feasibility measurements or grants. No adding separate medians as joint latency.

At the end of Task0039, real parity/decoder effective control/cost feasibility remained unmeasured. Its next requirement was a separate
explicit Task0040prompt/guarded payloadcontroller/fresh acceptance/freeze/exact
pre-post source/golden/role/shape/cache gates and one-attempt continuous supervised
execution; `future_measurement_execution_authorized=false`. No launch/confirmation/
scientific amendment/deployment/model/held-out access; Task0036unresolved/YES3/
Task0032complete/Task0033exploratory/failed campaigns/particle192 remain.

### Development selected-raw and frozen-feature cost — Task0040 completed

Task0039 committed90868d6e7; its prospective false flag/provider block/resolver
remain unchanged. [Report](development-raw-feature-measurement.md),
[separate strict config](../configs/benchmarks/development_raw_measurement_v1.json),
[summary](../results/tables/final/task0040-development-raw-feature-summary.json) and
[handoff](handoffs/0040-development-raw-feature-measurement.md) document one newly
prompt-authorized parent-accepted consumed session. Six additive helpers separate
payload permissions, durable accounting, fixed measurements, aggregate reports and
continuous parent/worker lifecycle; no model/science/new-source path.

Fresh100focused/2310full+portable/236bindings43packages31native files and native
synthetic acceptance precede freeze. Actual3original membership loads20997IDs/
same1024prefix/3golden3072rows,384unique raw rows,732selected reads30927requested=
returned rows/768constructions32448rows,36cells720timed108warmups. All72pre/post
windows pass exact golden/repeat bytes; original inputs/transforms unchanged.
Raw byte custody2passes5816520818B/3readonlyHDFhandlesclosed, no per-event exports.
Pooled meanB1read/features/joint0.437/0.138/0.592ms; B12845.143/5.778/50.013ms,
actual joint390.723µs/useful selected event. All repetitions and observed maxima
read52.347/features7.585/joint58.981ms retained;20serial calls/cell are not production
p99 or independent stochastic service evidence. Cache1MiB521.75/persistent perworker,
warmOScontext; decoder threading and physical I/O/cache misses unknown.312geometric
chunks/24.501GiB decoded upper bound remain geometry, not measured data throughput.

Whole19.498497s/reserved18.003004s/0overshoot;4normal exits/reaping, maxworkerRSS
96.45MB/native77.20MB/parent33.88MB/owned5.63MB/enforcedarraybound59.15MB below
caps. WorkersWARN1454advisory/noCRITICAL/unknown, parentNORMAL2220WARN3989;
querygap0.061234/terminalgap0.056575s disclosed. Seven assertion observations then
release/helper−15/reaped/absent, display allowed/no persistent setting/RAMfloor.
Two accepted native synthetic integrations, final6.861521s; one initial pytest
reserved-name collection error corrected before tests/acceptance. Historical research
fixture counters eachfull/portable85models31forwards8710rows/two toy updates/two
calibrations cover that subset only; no globalzero-model test claim.

Actual raw/feature engineering access is openly reported; no held-out/model/fit/
calibration/evaluation/fingerprint/download work, exposureYES3/scientific route/
baseline/failures/particle192 unchanged. Three figures inspected/all outliers kept.
Next separately authorized joint preprocessing+frozen-adapter measurement design;
no Task0041, Task0037replay, deployment policy or sums-of-medians whole-chain claim.

## 2. Vision, motivation, and research question

### 2.1 The project idea

Event selection is a setting where scientific usefulness and computational practicality must be considered together. A model that is accurate but cannot meet the intended processing budget is not sufficient. A model that is fast but discards useful anomaly information is also insufficient.

LatentTrigger studies this tradeoff using a controlled progression:

1. Build trustworthy scientific data and evaluation foundations.
2. Establish transparent aggregate-level baselines.
3. Investigate whether particle-level structure justifies additional complexity.
4. Measure inference cost under explicit hardware and runtime conditions.
5. Explore export, reduced precision, and streaming behavior.
6. Evaluate frozen candidates on the held-out test and report both scientific and systems outcomes.

The intended contribution is a defensible experimental study and a maintainable research implementation. The project does not depend on obtaining a positive result for every model or optimization. A carefully controlled finding that a simpler model is preferable, or that an optimization provides no useful gain, is a valid outcome.

### 2.2 CERN / openlab motivation

The project connects high-energy-physics data, machine learning, software engineering, and heterogeneous computing. This direction is relevant to the computing themes described by [CERN openlab](https://openlab.web.cern.ch/our-rd-directions/): AI, emerging technologies, efficient computing infrastructure, and collaboration between scientific computing and industry.

The personal motivation includes building a credible research and engineering portfolio relevant to CERN/openlab opportunities. The portfolio should demonstrate methodological discipline, readable software, reproducible experiments, measured tradeoffs, and the ability to explain limitations. This is a project judgment about relevance, not an official assessment of competitiveness or admission prospects.

**LatentTrigger is an independent project. It is not an official CERN, ATLAS, CMS, or CERN openlab project, and does not imply affiliation or endorsement.**

### 2.3 Main research question

> How much anomaly-detection performance can be retained when machine-learning models are optimized for real-time LHC event selection under strict computational constraints?

Supporting questions include:

- What information is lost when an event is reduced to eight aggregates?
- Does a compact nonlinear model offer a useful tradeoff relative to PCA?
- Does particle/set structure justify its additional compute and memory cost?
- How do runtime, batch size, precision, export constraints, and hardware change that tradeoff?
- How stable are background-calibrated decisions across populations and numerical implementations?
- What biases do scores introduce with respect to event scale, mass proxies, multiplicity, and truncation?
- What happens to queueing, latency, and acceptance when a model is placed in a synthetic event stream?

These questions are not all currently answered. In particular, lower background reconstruction loss is not evidence of better signal discrimination.

## 3. Objectives and definition of success

| Objective | Required outcome | Current state |
| --- | --- | --- |
| Reliable data foundation | Pinned source, verified integrity, reproducible population membership, frozen transformations | Achieved for the primary LHCO dataset |
| Transparent baselines | Linear and compact nonlinear models using a shared input/evaluation contract | PCA and compact AE implemented; AE convergence closure completed |
| Richer event representation | A justified, compact, mask-aware particle/set baseline | Design/code retained; two real96step characterizations/current240.728s>180s;192consumed; Task0019 defers local canonical execution, convergence/usefulness unresolved |
| Scientific evaluation | Frozen-candidate discrimination metrics, calibrated operating points, uncertainties, and bias analysis | Task0026 authorized frozen PCA/AE comparison accepted; counts/intervals/calibrated and descriptive ROC/PR outcomes curated. Bias/generalization beyond this signal remains unresolved; tests exposed |
| Hardware study | Repeatable latency, throughput, and memory measurements with clear timing boundaries | Task0022 CPU v2 complete/accepted; Task0023 MPS blocked; Task0025 all paired CPU timings/numerics measured but ORT3 exit deadline prevents campaign performance acceptance |
| Deployment study | Verified exports and reduced-precision variants where useful | Task0024 ONNX CPU structure/equivalence accepted; CoreML and reduced precision planned |
| Trigger-like systems study | Reproducible synthetic arrival/queue/acceptance scenarios | Pending |
| Initial research deliverable | Quality-versus-cost comparison, clear claims, reproducibility package, limitations, and conclusions | Completed Task0027 for frozen native PCA/AE/declared signal; further bias/generalization/deployment studies remain separate |

The final result should describe a quality/cost frontier rather than declare one model universally best. Any latency budget, throughput target, acceptable numerical deviation, or quality-retention requirement must be established in the relevant task before observing results. No numerical deployment target has yet been validated.

The project is successful when its conclusions are supported by evidence and another session or researcher can understand and reproduce the decisions. It does not require proving detector readiness, discovering new physics, or making the AE outperform PCA.

## 4. Scope and non-scope

### 4.1 Primary scope

- Corrected LHCO R&D particle data as the initial shared scientific source.
- Pure-background unsupervised fitting and background-only development.
- Aggregate reconstruction baselines, followed by compact particle/set-aware models.
- Common score orientation, population roles, calibration, metrics, and uncertainty conventions.
- Scientific bias and representation-loss analysis.
- Apple Silicon CPU/MPS inference as the initial hardware study.
- Controlled ONNX/ONNX Runtime and CoreML export/inference experiments.
- Precision reduction and quantization, where supported and justified.
- A synthetic trigger-like event-stream simulator.
- Conditional NVIDIA/TensorRT work and optional FPGA/hls4ml exploration.
- An explicitly authorized, frozen-candidate final test evaluation.

### 4.2 Non-scope and prohibited shortcuts

- No official experiment trigger implementation, DAQ integration, detector commissioning, or claim of operational readiness.
- No physical LHC arrival-rate inference from the released dataset's row count or class mixture.
- No discovery claim or discovery significance derived from event-score classification alone.
- No signal-driven model, preprocessing, sequence-length, epoch, or threshold selection under the current protocol.
- No test-guided iteration followed by describing the same population as untouched.
- No validation anomalies without a separate explicit protocol change and suitable reserved evaluation.
- No automatic choice of a Transformer merely because the input is a set.
- No CUDA/TensorRT assumption on the local Mac; NVIDIA work requires a separate supported environment.
- No full raw DataFrame loading on the 16 GiB development machine.
- No large data/checkpoint/export files added to Git by default.
- No expansion into unrelated applications, dashboards, tracking frameworks, or infrastructure without a concrete need.

Additional datasets, signal contamination studies, black-box studies, and real detector data are later extensions, not implicit changes to the initial benchmark.

## 5. Overall architecture and repository structure

### 5.1 Scientific and deployment pipeline

```text
Pinned and verified raw HDF5
    -> structural integrity and exact-content grouping
    -> deterministic frozen population membership
    -> canonical physical ragged event store
        -> standardized eight-aggregate view
            -> PCA / compact AE
        -> particle/set view [384, 4] + mask
            -> implemented compact particle/set AE (canonical baseline pending)
    -> finite anomaly score, larger = more anomalous
    -> frozen background-calibrated thresholds
    -> inference runtime / precision variant
    -> future synthetic streaming selection
    -> separately authorized final test evaluation
```

The canonical physical store preserves all valid source particles. Model views are derived from it; the padded representation is not the persistent source of truth. Labels and provenance remain outside model features.

Keep the following boundaries visible:

- Data custody and integrity versus model/evaluation population access.
- Frozen physical/preprocessing semantics versus model-specific representation choices.
- Model fitting/selection versus threshold calibration.
- Training resource observations versus controlled inference benchmarks.
- Model-only inference versus transfers, preprocessing, scoring, decision, and end-to-end latency.
- Scientific identities versus local build/run metadata.

### 5.2 Repository organization

```text
latent-trigger/
  .github/workflows/ci.yml
  configs/
    data/lhco_rnd_v5.json
    models/pca_baseline.json
    models/compact_autoencoder.json
    models/compact_autoencoder_v2.json
    models/particle_set_baseline_design_v1.json  # historical design-only specification
    models/compact_particle_set_autoencoder_v1.json  # exact executable mapping
  src/latenttrigger/
    data/          acquisition, inspection, splitting, features,
                   preprocessing, processed-store reading, analysis
    models/        PCA, compact AE, background loading, reporting
    training/      AE training and convergence closure
    evaluation/    metrics, thresholds, final evaluation gate
    utils/         device selection
  scripts/         acquisition audit, EDA, preprocessing checks, smoke tests
  tests/
  docs/
    project-memory.md       maintained project-wide state and direction
    development.md          task workflow
    *-contract.md           frozen scientific semantics
    *-protocol.md           evaluation and access rules
    model/data reports     detailed evidence and reproduction
    prompts/                task specifications
    handoffs/               historical task records and index
  artifacts/models/
    compact-autoencoder-v1/model.json
    compact-autoencoder-v2/model.json
  results/
    tables/final/           intentionally curated small results
    figures/final/          intentionally curated figures
    benchmarks/            future benchmark outputs/policy
  notebooks/exploration/
  data/                     local raw/analysis/processed/baseline outputs
  README.md
  pyproject.toml
  LICENSE
  .gitignore
```

Relative links in this memory are intended to resolve from `docs/` in the operational repository. The local repository used for verification was `/Users/matteosgobba/Documents/GitHub/latent-trigger`; that path is a local locator, not part of portable scientific provenance.

## 6. Development platform, stack, and resource constraints

### 6.1 Platform

- User-specified MacBook Pro M5.
- Enduring user preference: normal shared Mac use with other apps open. Engineering/reconciliation/synthetic work must finish without dedicated hardware windows, closing apps/Codex or reboot. Task0018 bounded dev no longer requires a global RAM reserve/stability window; tight process guards and CRITICAL pressure veto operate with WARN advisory/unknown disclosed. Task0019 defers long canonical particle work: short-dev WARN/unknown permission does not validate multi-hour suitability. Any future full run needs separately authorized limits/enforcement/compatibility/failure handling; no indefinite readiness polling or guaranteed availability. The next frozen CPU benchmark has its own proposed finite process/deadline scope, requiring synthetic validation within Task0020.
- Recorded/verified task environment: macOS 26.6.2, ARM64, 16 GiB RAM.
- CPU is the canonical compact AE training device.
- MPS availability is queried, not assumed. The generic device helper prefers MPS when available and otherwise CPU; model configuration explicitly fixes canonical training to CPU.
- A sandbox may expose CPU fallback even when native MPS works. Distinguish those execution contexts.

Task0020 filtered post-campaign system_profiler metadata verifies MacBook Pro/Mac17,2/Apple M5/16 GB, raw CPU descriptor `proc 10:4:6:0` (ten total indicated). Native sysctl exact RAM/core/build queries were unavailable; preserve that distinction. AC power/battery80% and shared-host load were recorded. Thermal query returned error text despite exit0, so thermal values remain unknown. GPU core counts and MPS performance are unmeasured. Task0022fresh filtered hardware capture inside the CPUcampaign independently confirms M5/16GB/Mac17,2/processor10:4:6:0, actual arm64/macOS26.6.2/AC80%/shared load; native sysctl and thermal remain unknown. Historical CPUsmoke reports MPSFalse. Task0023sole fresh process records built=True/available=False, not proof of absent physical GPU or sandbox causation; no second check. Fresh M5/16GB/10CPU-core descriptor confirmed, AC100%, thermal/Metal/GPU cores/native sysctl unknown.

### 6.2 Stack

| Layer | Established choice |
| --- | --- |
| Python | Primary 3.12; supported range `>=3.11,<3.13` |
| Environment/build | `venv`, `pip`, editable installation, Hatchling, `src` package layout |
| Package | `latenttrigger`, version 0.1.0 at this snapshot |
| Numeric/data | NumPy; h5py and hdf5plugin in the optional data extra |
| Modeling | scikit-learn PCA/metrics; PyTorch aggregate AE and implemented particle/set AE |
| Analysis | Matplotlib in the optional analysis extra |
| Quality | pytest, Ruff lint/format |
| CI | CPU checks configured for Python 3.11 and 3.12 |
| Future runtime work | ONNX Runtime, CoreML/coremltools, NVIDIA/TensorRT, optional hls4ml |

Historical experiment versions: Python 3.12.12; PyTorch 2.14.1; NumPy 2.5.3; scikit-learn 1.9.1; SciPy 1.18.1; h5py 3.16.0/HDF5 2.0.0; hdf5plugin 7.1.0; Matplotlib 3.11.2; pytest 9.1.1; Ruff 0.16.10.

Dependency ranges are not an experiment lockfile. Record exact versions in each run. Cross-version/device bitwise identity is not guaranteed.

### 6.3 Resource implications

The raw numeric payload is 18,488,800,000 uncompressed bytes, exceeding installed RAM before overhead. Use bounded contiguous HDF slices, memory mapping, and batch processing. The established default processing chunk is 992 events, equal to 16 HDF chunks.

Do not persist a full `[1,100,000,384,4]` tensor by default: the FP32 features alone would require 6,758,400,000 bytes. A single event's four-channel particle input uses 6,144 bytes, excluding mask, activations, and runtime overhead. Unified memory does not remove copies, synchronization costs, or capacity limits.

Task 0009 selected design has 1,912 FP32 parameter bytes, 165,888 dense forward MAC/event at 384 particles and no quadratic score. Batch32 has a 0.75 MiB largest network tensor; an allocation inventory is about 3.68 MiB and a 4× working-tensor planning envelope about 14.71 MiB, excluding runtime/store overhead. These are analytic estimates, not measured RSS or latency. Preregistered ceilings, enforced by Task 0010, are 512 MiB working tensors/workspace, 6 GiB process RSS (including verification/mmap), at least 8 GiB available at launch and stop below 4 GiB available. Stream at most 32 padded events; never cache the padded population. CPU feasibility must pass the dev gate before full training. Task 0010 measured synthetic batch32/full384 temporary tensor allocation at 5,228,448 bytes (4.986 MiB) with two Adam steps; this is not real-run peak memory or latency. The real launch attempt stopped at 3,967,254,528 available bytes (3.694794 GiB), before any store/view read. Launch RSS 356,663,296 bytes and native heap reservation 184,205,312 bytes are startup observations only. Available memory uses Darwin free+inactive pages; real stages also monitor native malloc arena reservation, RSS, memory floor and deadlines. No resource limit was relaxed. Task 0011 rechecked in a fresh CPU worker: page size16,384 bytes, available2.9495/2.9671/3.0176 GiB, all below launch and continuing floors; peak RSS≤357,498,880 bytes and native reserved≤184,205,312 bytes passed their ceilings. Readiness is not a real attempt. Installed RAM16 GiB and memory-pressure free39% are distinct contextual measurements; compressed pages/cumulative swap counters are not added to availability. Current swap/current RSS queries were permission-restricted. At Task0011, its recovery plan/ledger/output remained absent; real-stage evidence is still pending. On2026-10-07, after explicit reboot/manual preparation, one new preflight gave4.6485/4.6248/4.6819GiB over5.004717208s (total5.033480708s); launch still fails, all continuing/RSS/native tests now pass. Peak RSS357924864bytes, native reserved184205312bytes; contextual free61% is not the launch metric. Earlier records are preserved and no recovery launch/data access occurred. Task0012 explicitly separates historical v1 from a provisional engineering v2 sidecar: launch4.5GiB derived from continuing4GiB+512MiB whole-native headroom. Same metric,4GiB floor,512MiB native,6GiB lifetimeRSS and all time/update limits; v1 compliance false. Source/reader inventory and a fixed empirical incremental-bound+128MiB margin criterion precede any dev activation. Historical Task0012 single preflight2.5836/2.5443/2.6967GiB failed launch/floor, so no reader/custody/update. Optional own-task Mach currentRSS/virtual size is supported; pressure/current swap restricted, dirty/private not measured. Probe overhead7.12–17.67ms is readiness-only, not watcher/detector latency.

Task0013 measures supervisor overhead without constructing data/scientific objects. Three fixed configurations finish in20.817s; stdlib parent imports no numeric framework, legacy parent/worker import the actual stack, lightweight parent keeps one prepared CPU worker. Legacy own-parent peakRSS357105664bytes/native175816704bytes versus light22200320/29360128bytes (differences334905344/146456576bytes). These sequential process observations overlap shared pages and do not establish unique RAM savings or explain the historical~2GiB host change. Light worker samples3.220428/3.177795/3.244232GiB are all below4GiB as well as4.5GiB, native≤175816704bytes/lifetimeRSS≤357154816bytes pass. Current MachRSS succeeds; pressure/current swap/directRAM query restricted, contextual installed16GiB/free46% is not the metric, dirty/private unmeasured. At that initial task-time point no study was reserved. A subsequent external invocation consumed it and passed reader/memory/activation, then failed throughput; its preserved receipts are reconciled in Task0014. All startup/probe/reader costs remain inside original ceilings.

The external manual study measured full-custody lifetimeRSS3351019520bytes and native206831616bytes, below6GiB/512MiB. Two audited reader custody operations plus a separate dev-stage constructor are distinguished from five train-background/dev-only population requests:64+3072training+1024scoring=4160presentations within1024unique IDs.96started/completed updates, no inflight, no original allowance remains. Historical dev probes287/1.316605680s cumulative are overlapping work, never subtracted from749.3431957854029s=2×(346.22189913589574+28.44969875680573). This is an extrapolation, not a measured full epoch/convergence result.

Task0014 retains synchronous exact system vm_stat and cached native/Mach/pressure bindings rather than admitting potentially cached direct Mach counters. Speculative pages are subtracted to match displayed free. Public XNU rate limiting gives no native sample timestamp; the very fast direct API remains diagnostic-only. A stream is not selected because reuse weakens synchronous observation and fresh-sample waits add cost. V3 has unchanged4.5/4GiB,512MiB/6GiB,50ms intent/signals/per-batch/deadlines and immediate audit reservations. Journal flush is per sample, no fsync claim.49new synthetic cases are recorded in the Task0014 report; actual full suite471passed. Fixed matrix11.199s shows component gains but workload1.6%slower; shared-host variability prevents causal/speedup claims. Actual OS diagnostic availability~3.32GiB is context only; the explicit9GiB synthetic guard fixture is never readiness or production acceptance. No new real data/custody/steps.

Task0015 explicitly authorizes a different observation contract: a single owned thread samples system vm_stat every50ms; batch guards may reuse the latest valid generation only with now−query-start≤100ms, never publication/read age. Native reservation/lifetimeRSS/optional pressure/deadlines remain fresh at every before/after/pre-step boundary, with periodic process checks while a query is pending. Startup/phase/readiness refresh is synchronous and thread-owned; errors/staleness/limits latch.100ms is an observation bound, not guaranteed Python/OS termination latency; direct Mach stays diagnostic. Fixed nine-arm matrix14.910s: v3/v4/compute medians0.381356958/0.178179666/0.069689125s, exact numerics,2.1403×<3. No real admission was attempted. Final process-veto reporting repair retains actual failed peaks; separate renewed532-test acceptance and affected-v4-only validation preserve original evidence and cannot unlock material acceptance. V4 is synthetic only; numerical4.5/4GiB/512MiB/6GiB/180s and full-run budgets unchanged.

Task0016 keeps that monitor/sampler/collector/manifest byte-identical and adds a separate typed diagnostic permission. It prospectively removes synthetic3×as admission for one direct bounded measurement, with no new speed threshold and no alteration of historical failure or180s criterion.576synthetic tests pass (44new), allocation5228448bytes unchanged. Sole fully prepared read-only worker records `(3855+229326)×16384=3820437504bytes/3.558059692GiB`; continuing-floor veto occurs before the stable3reading protocol/publication. Current/lifetimeRSS360939520bytes/native reserved188399616bytes pass caps, guard age8.407ms/probe7.999ms pass, pressure errno1unknown. One host query completed/zero admitted generations, two process checks; partial readiness failed, no dataset constructor/access/update or real attempt. Automatic allowance is not loopable; optional one-shot manual route shares the same remaining≤96/cumulative192 slot under contemporaneous guards, with apps open and no extra implementation task.

Later manual Task0016 check vetoes on verifiedWARN2 before a complete available-memory sample; own peakRSS358842368/native171622400bytes pass caps but do not neutralize pressure. Both fixed read-only reservations exist, blocking further old-route checks despite unreserved real budget. Task0017 now distinguishes resource checks/history from execution permission. One explicit command/check owns one fresh prepared worker/≤30s protocol and unique32hex immutable history; no data/slot even ready. Separate explicit run always rechecks, uses one exclusive canonical Task0016 anchor/output and a new source-bound execution plan, no independent Task0017budget or stale-lock removal. Optional later read-only pressure snapshot remains separate diagnostic, never admitted or veto reversal. Actual612tests pass; one check-only integration3.705841064GiB/7.514ms/360611840RSS/188399616native fails floor with pressure unknown,0real work/slot. Future checks need no new numbered task or commit; no background monitoring service or app closure.

Task0018 explicitly supersedes global host admission only for the small bounded dev scope: fixed512MiB lifetimeRSS/256MiB whole-native, fresh process/pressure at every boundary/pre-step and periodic50ms intent; NORMAL/WARN permitted, CRITICAL latched, unknown pressure disclosed/allowed. Global system vm_stat once at startup/phase is optional context, no minimum/floor/100ms veto or5s stability wait. This is not v4-equivalent or full-run authorization. Original dev367.25MiB RSS/later179.672MiB native motivate144.75/76.328MiB headroom, not disjoint allocations or machine-wide availability. Small dev8494events/23046077persistent bytes remains constructor-verified.670tests/portable670/5228448synthetic tensor bytes pass. One source-frozen run: preflight3.374695GiB context/unknown pressure passes local caps; reader64/fresh phase checks/dev1024×3training+one score complete. Dev370.015625MiB RSS/179.671875MiB native pass, exact objective/mean/hash match Task0013,96new+96historical=192completed/0inflight. Projection240.72835947066707s fails180s;200projected cycles13.3738h/run conflict with10hfit/max200 planning (patience may stop earlier; no full epoch/convergence measured). Shared canonical anchor consumed, no remaining allowance/manual rerun. Full-store3.121GiB historical RSS is distinct and cannot fit this512MiB dev cap; Task0019 consolidates full-store/time/shared-use feasibility into local canonical deferral without global cleanup or full-run limit changes.

Task0019 recomputes original full-custody lineage and headroom without payload reads:6GiB−3351019520bytes=3091431424bytes/2.879119873GiB (47.985331%);512MiB−206831616bytes=330039296bytes/314.75MiB (61.474609%). These overlapping accounting measures are not disjoint allocations; virtual maps are not resident pages. No sustained full-training memory/pressure behavior is measured. Process-local budgets with contextual global telemetry remain an inactive full-run proposal; conservative NORMAL-only admission/WARN or CRITICAL veto/unknown blocked would require separate review and implementation. No active config changed. The shared Mac's16GiB installed capacity is not guaranteed free headroom.

Check actual disk availability before expensive work; account for raw data, processed stores, temporary streams, repeated runs, caches, and a safety margin. Never delete verified raw data automatically to free space.

## 7. Dataset identity, schema, and acquisition decisions

### 7.1 Exact primary source

| Field | Frozen value |
| --- | --- |
| Dataset | LHC Olympics 2020 R&D |
| Version | Zenodo v5 |
| Record | 6466204 |
| Version DOI | [10.5281/zenodo.6466204](https://doi.org/10.5281/zenodo.6466204) |
| Primary filename | `events_anomalydetection_v2.h5` |
| Exact size | 2,908,260,409 bytes |
| Published and verified MD5 | `629789d55813be3860781b084ae7f1de` |
| Locally computed SHA-256 | `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6` |
| Historical acquisition/first verification UTC | `2026-10-04T11:05:47.545875+00:00` |
| License | CC BY 4.0; retain dataset attribution |
| Default local raw directory | `data/raw/lhco/6466204/` |

Size, MD5, and SHA-256 were rechecked against local file bytes on 2026-10-06 when establishing the project memory. This was an integrity-only read, not test scoring. The software's MIT license does not relicense the dataset.

**Why the corrected v5 source matters:** The April 2022 correction aligned raw events with the v2 QCD generator threshold, `PhaseSpace:pTHatMin = 500`, and the published v2 feature file. Do not substitute the older `events_anomalydetection.h5`, use a floating latest URL, or mix older particles with corrected feature rows. See the [official correction notice](https://zenodo.org/records/6466204).

### 7.2 Physics context and interpretation

The primary file contains 1,000,000 QCD events and 100,000 two-prong signal events, shuffled together. The signal is `W' -> XY`, with `X -> qq` and `Y -> qq`; masses are 3.5 TeV, 500 GeV, and 100 GeV. Generation uses Pythia8 and Delphes 3.4.1 without pileup or multiple parton interactions.

The benchmark is already selected using a fat-jet trigger. The official challenge documents an anti-kT `R=1` jet with `pT > 1.2 TeV` and `|eta| < 2.5`. This is a jet requirement, not a per-particle cut.

These are simulated, preselected events. Rows are not timestamps; the class ratio is not a collision-rate model; reconstructed massless constituents do not represent detector readout or every stage of the real LHC trigger chain.

### 7.3 Actual HDF schema

| Object | Shape/dtype | Meaning |
| --- | --- | --- |
| `/df/block0_values` | `[1,100,000,2101]`, float64 | Numeric event rows |
| `/df/axis0` and `/df/block0_items` | `[2101]`, int64 | Column labels 0 through 2100 |
| `/df/axis1` | `[1,100,000]`, int64 | Stored row index, verified against ordinals |
| Particle slot `j`, `0 <= j < 700` | Columns `3j`, `3j+1`, `3j+2` | `pT [GeV]`, `eta`, `phi [rad]` |
| Column 2100 | float64 truth bit | 0 background, 1 signal; separate metadata |

The root contains a pandas fixed-format frame under `/df`, not an assumed dense `/table` dataset. Numeric HDF chunks are `[62,2101]`; one uncompressed numeric chunk is 1,042,096 bytes. All four datasets use Blosc filter 32001. Importing hdf5plugin registers the required decoder; plain h5py initially could inspect metadata but could not decode event content.

Real particles have `pT > 0`. Padding is an exact `(0,0,0)` trailing suffix. There are no particle type, charge, mass, or jet-assignment channels. Unit interpretation is source-supported, not supplied by a self-describing unit header.

### 7.4 Integrity evidence

Task 0003's bounded audit inspected 32 evenly spaced, class-agnostic rows. It found 16,890 padded slots, multiplicities 74-301 with mean 172.1875, and no sampled structural violations. This was a bounded finding, not a full-file quality guarantee.

Task 0004 then scanned the complete source before model-oriented EDA:

- 1,100,000 eligible events: 1,000,000 background and 100,000 signal.
- Zero unexpected truth values, NaNs, infinities, negative-pT events, malformed padding, non-trailing padding, empty events, or row-axis mismatches.
- Full structural multiplicity range: 22-560; zero events filled all 700 source slots.
- 1,100,000 unique exact-content groups; zero duplicated groups, participating duplicate rows, or conflicting-label groups; largest group size 1.

Do not generalize exact duplicate findings to approximate duplicates or other datasets.

### 7.5 Reserved sources

The v2 high-level jet-feature file is an optional later cross-check, not the primary input. The supplemental three-prong signal was allocated to Task0028 evaluation-only scope with exposed background reuse; Phase A software accepted, Phase B failed/consumed. Separate explicitly authorized Task0029 transport also failed/consumed after3requests;29990748Bunverified prefix/SHA/checkpoints retained. Task0029 itself supplies no complete byte artifact, HDF metadata, numerical custody or model exposure. Task0030 subsequently accepts complete bytes/structure, and Task0031 accepts numerical custody and scientific evaluation of all100000valid/unique/disjoint events with shared background. No consumed session is retried/resumed. LHCO black boxes remain reserved for separate protocols. Public black-box answer keys prevent claiming original challenge blindness.

Dark Machines was considered as a later cross-benchmark; CMS JetHT NanoAOD as a possible later realism study. Neither is part of the current implemented pipeline. Adding them requires new schema, selection, label, and evaluation decisions.

## 8. Frozen population protocol and test embargo

### 8.1 Exact populations

Protocol identifier: `lhco-rd-v1`. Seed: **1729**.

| Population | Exact count | Permitted role |
| --- | ---: | --- |
| `train_background` | 699,957 | EDA, fitted preprocessing, model fitting, future quantization calibration |
| `validation_selection_background` | 74,749 | Preregistered background model selection/early stopping and diagnostics |
| `validation_calibration_background` | 74,823 | Threshold calibration after selected model restoration and freeze |
| `test_background` | 150,471 | Task0026 frozen final evaluation completed; permanently exposed |
| `test_signal` | 100,000 | Task0026 frozen final evaluation completed; permanently exposed, never undeclared tuning |
| Total validation background | 149,572 | Two disjoint roles; do not merge them for convenience |
| Development subset | 8,494 | Pipeline/model implementation diagnostics, not final reported ML results |

Development subset composition: 6,999 training background, 747 selection background, 748 calibration background. No test events and no signal.

### 8.2 How membership is established

Exact-content grouping precedes split/subset selection and fitted statistics. Remove verified padding, normalize signed zero, wrap only out-of-interval phi, lexicographically sort physical triplets, and hash:

```text
uint64 little-endian particle count
    || contiguous little-endian float64 triplets
```

Labels, source ordinals, split names, and learned statistics are excluded. Do not round values to deduplicate. Future aliases share group membership; conflicting labels quarantine the group and block statistical analysis.

For each eligible background fingerprint, hash the exact UTF-8 prefix:

```text
lhco-rd-v1|1729|bg-split|<lowercase fingerprint hex>
```

Interpret the first eight digest bytes as a big-endian unsigned integer and derive `u = k / 2^64`: train below 0.70, validation from 0.70 to below 0.85, test otherwise. The independent `val-role` hash domain divides validation at 0.5. Use the implementation's exact integer cutoffs.

The fractions are hash probabilities, not exact quotas. Reuse saved membership and verified split provenance for every model. Do not resplit per experiment.

The `lhco-rd-dev-v1` subset ranks allowed groups using `dev-subset`, selecting `floor(role_count/100)` separately for each allowed background role. It is a convenience subset, not guaranteed kinematic stratification.

### 8.3 Embargo rules

**There is no anomaly validation population in the current protocol.** All primary two-prong signal is test-only.

During development, do not compute real test reconstruction loss, anomaly scores, ROC-AUC, AP, signal efficiencies, test-background FPR, signal latent distributions, or test physics distributions to guide choices. Test information must not select features, architecture, `Nmax`, scalers, training endpoint, runtime variants, or thresholds.

Allowed custody operations include raw/file hashing, structural schema/label-role consistency, duplicate/split integrity, and applying an already-frozen preprocessing function to construct the full store. Those operations must not feed test physics distributions or scores back into development.

The standard background loader permits only train, selection, and calibration backgrounds. The processed reader has explicit test and truth guards. A separate final evaluation module requires opt-in and frozen identities. Availability of an API or CLI is not authorization to run it on real test populations.

Any partial or interrupted model/evaluation test access is exposure. Repeated test-guided development cannot restore the population's untouched status. Disclose exposure and establish a new evaluation protocol/population if subsequent design is motivated by test results. Task0033 is an explicitly authorized exploratory exception for fixed descriptive reads of already exposed frozen features/scores; it is consumed, grants no development/selection access and supplies no untouched confirmation.

## 9. Frozen preprocessing and feature contracts

The exact numeric source of truth is [configs/data/lhco_rnd_v5.json](../configs/data/lhco_rnd_v5.json), supported by the [preprocessing contract](preprocessing-contract.md). Read the configuration; do not refit statistics or copy rounded report values.

### 9.1 Canonical physical records

- Store all valid particles as FP32 `[N,3]`, channel order `[pt_GeV, eta, phi_rad]`.
- No truncation, padding, logs, standardization, or sine/cosine replacement in the physical canonical record.
- Normalize signed zero; wrap out-of-range phi in float64 using `((phi + pi) mod (2*pi)) - pi`; preserve in-range values exactly.
- Before casting, sort original source float64 values by descending pT, ascending eta, ascending wrapped phi, then ascending original slot.
- Preserve original slots as uint16 provenance, not model channels.
- Event identity is `(source SHA-256, raw row ordinal)`; the exact-content fingerprint is separate provenance.

### 9.2 Particle/set view

Input shape: `[384,4]` FP32 and `[384]` boolean mask; batches `[B,384,4]` and `[B,384]`.

| Channel | Frozen transform |
| --- | --- |
| 0 `standardized_log1p_pt` | `(log1p(pT / 1 GeV) - 1.7563971656024226) / 1.1860427476562252` |
| 1 `standardized_eta` | `(eta - (-2.3446856614008353e-05)) / 1.4824139450954399` |
| 2 `sin_phi` | `sin(wrapped_phi)` |
| 3 `cos_phi` | `cos(wrapped_phi)` |

Object scalers were fitted in float64 on all **127,379,949 valid training-background particles**, before truncation, with equal particle weights and population standard deviation (`ddof=0`). Compute model transformations in float64 from canonical physical values, then cast once to FP32.

No clipping, winsorization, per-event rotation, event-scale removal, or learned angular standardization is part of the contract.

### 9.3 `Nmax`, ordering, padding, and mask

**Default `Nmax=384`.** Retain the leading `min(N,384)` particles in the frozen order. Preserve every particle in the canonical store.

The preregistered choice was the smallest candidate with at least 99% complete-event coverage and event-mean lost scalar-pT fraction no larger than 0.1%. Training-background evidence:

- 1,740 truncated events, or 0.248587%.
- Complete-event coverage 99.7514%.
- Mean scalar-pT loss over all training events 0.001118%; worst event loss 5.1146%.
- Truncated events lose an average 26.765 particles; worst removed count 176.
- `Nmax=320` meets momentum retention but fails complete-event coverage.

Transform real retained particles first, then pad with exactly `[0,0,0,0]`. Transforming a zero physical padding triplet would incorrectly produce `cos(phi)=1` and nonzero standardized values.

**Mask `True` means real retained particle; `False` means padding.** True entries form a prefix. Apply mask in pooling, attention, losses, and statistics. Record original/retained multiplicity and retained scalar-pT fraction separately. No original-slot channels or position embeddings in the initial permutation-symmetric set view.

Alternative `Nmax` values require controlled, versioned experiments, never test-signal tuning.

### 9.4 Eight aggregate features

Compute from **all canonical physical particles before truncation**, accumulating float64. Define:

```text
S = sum_i pT_i
Qx = sum_i pT_i * cos(phi_i)
Qy = sum_i pT_i * sin(phi_i)
mu_eta = sum_i pT_i * eta_i / S
E = sum_i pT_i * cosh(eta_i)
Pz = sum_i pT_i * sinh(eta_i)
```

| Index / channel | Physical definition | Transform before standardization |
| --- | --- | --- |
| 0 `multiplicity` | `N` | `log1p(N)` |
| 1 `scalar_pt` | `S [GeV]` | `log1p(S / 1 GeV)` |
| 2 `max_pt` | `max_i pT_i [GeV]` | `log1p(max_pt / 1 GeV)` |
| 3 `pt_balance` | `sqrt(Qx^2 + Qy^2) / S` | Identity |
| 4 `weighted_eta_mean` | `mu_eta` | Identity |
| 5 `weighted_eta_std` | `sqrt(sum_i pT_i * (eta_i-mu_eta)^2 / S)` | Identity |
| 6 `pt_concentration` | `sum_i pT_i^2 / S^2` | Identity |
| 7 `massless_event_mass` | `sqrt(E^2-Qx^2-Qy^2-Pz^2) [GeV]` | `log1p(M / 1 GeV)` |

Guard `S > 0`. Clamp a negative mass-squared only when its magnitude is within `64 * float64_eps * (E^2+Qx^2+Qy^2+Pz^2)`; materially negative values are errors. This is a visible massless event-mass proxy, not the published dijet mass. `pt_balance` is not detector-provided MET.

Every transformed aggregate is standardized using the frozen training-event mean and population std, with equal event weights. Output `[8]` FP32, in the permanent channel order above.

| Index | Exact transformed-feature mean | Exact population std |
| --- | ---: | ---: |
| 0 | 5.151002678640802 | 0.3506400659339444 |
| 1 | 7.963434750020592 | 0.13328049741910378 |
| 2 | 6.063241479784076 | 0.4747007020377456 |
| 3 | 0.02557015572051737 | 0.020723012003953097 |
| 4 | -0.0003911654144766292 | 0.42205163321441674 |
| 5 | 0.7250460126255276 | 0.24966927987490806 |
| 6 | 0.06391752754240078 | 0.03801299101213741 |
| 7 | 8.332576043011052 | 0.21947880024539493 |

Do not include truth, row ID, split, fingerprint, source identity, or original slot among features.

### 9.5 Processed storage

Local ignored root: `data/processed/lhco-rd-v1/schema-v1/{dev,dev-repeat,full}`.

| File | Dtype / shape | Role |
| --- | --- | --- |
| `particles.npy` | float32 `[P,3]` | All physical sorted particles |
| `original_slots.npy` | uint16 `[P]` | Source-slot provenance |
| `offsets.npy` | int64 `[E+1]` | Ragged event slices |
| `event_ids.npy` | int64 `[E]` | Source ordinals |
| `multiplicities.npy` | uint16 `[E]` | Full particle counts |
| `event_aggregates.npy` | float64 `[E,8]` | Physical full-event summaries |
| `event_features.npy` | float32 `[E,8]` | Standardized aggregate model input |
| `labels.npy` | uint8 `[E]` | Separate evaluation truth |
| `split_codes.npy` | uint8 `[E]` | Frozen roles |
| `development.npy` | bool `[E]` | Dev membership |
| `fingerprints.npy` | 32-byte void `[E]` | Exact-content identity |
| `configuration.json` | JSON | Exact configuration snapshot |
| `manifest.json` | JSON | Integrity/scientific identity plus separate build record |

## 10. Implemented foundation and evidence

This table preserves the project-level outcome of each task. Detailed chronology, commands, changed files, and task-time failures belong to the existing handoffs.

| Task | Verified local commit | Durable outcome | Recorded passing pytest count |
| --- | --- | --- | ---: |
| 0001 Project Initialization | `0930b03` | Package/tooling/CPU CI; CPU/MPS device diagnostic, result 16.0; repository policies | 4 |
| 0002 Data Foundation and Dataset Design | `182ff31` | Dataset selection, population/embargo and representation design; permanent prompt/handoff protocol | 4 |
| 0003 Verified Dataset Acquisition and Raw Schema Audit | `bdc8da0` | Real source acquired and hashed; streamed atomic downloader; Blosc-aware bounded schema audit | 32 |
| 0004 Training-Background EDA and Schema Validation | `cd3d24a` | Complete integrity/exact grouping, saved splits, train-only EDA; frozen scalers/order/Nmax | 54 |
| 0005 Deterministic Preprocessing Pipeline | `cb079ec` | Verified ragged dev/full stores, views, manifests, reproducibility and access safeguards | 84 |
| 0006 PCA Baseline and Evaluation Framework | `56a7409` | Frozen PCA, background diagnostics/calibration, common metrics, future audited final gate | 120 |
| 0007 Compact Autoencoder Baseline | `64bb817` | Frozen AE v1, deterministic full CPU repeat, background calibration, MPS compatibility | 148 |
| 0008 Compact Autoencoder Convergence Closure | `0645077` | Exact v1 prefix; unchanged-rule early stopping; canonical AE v2, exact independent repeat | 167 |
| 0009 Particle-Level / Set-Aware Neural Baseline Design | `96ef5aa`, verified in Task 0010 | One complete design, loss/score/budgets and future gates; zero real population requests | No suite rerun; synthetic formula/document checks |
| 0010 Compact Particle/Set Baseline Implementation and Background Validation | Commit `694bffd` verified2026-10-07; historical base `96ef5aa` | Exact implementation; original launch-memory failure and both source acceptances preserved | 247 |
| 0011 Bounded Particle/Set Resource-Gate Recovery and Background Validation | Initial `50e42b3`, resumption `502c472` verified in Task0012 | Initial/post-reboot failures preserved; unused route superseded by Task0012, no real consumption | 296 historical |
| 0012 Versioned Launch-Memory Policy Review and Bounded Feasibility Validation | `53b238a`, verified in Task0013 | Strict v2 sidecar/phase accounting; sole provisional preflight fails launch and original floor, no readers/dev; canonical pending | 365 final full synthetic tests |
| 0013 Host Memory Diagnosis, Lightweight Supervision, and Conditional Bounded Feasibility | `9d5e03b`, verified in Task0014 | Initial accounting preserved; later external slot consumed, memory/bounded-dev activation pass,96real steps completed,749.343s throughput failure | 422 historical full synthetic tests |
| 0014 External Study Reconciliation / Resource-Monitor Performance | `8d0e3f9`, verified in Task0015 | Historical budget reconciled; cached-bindings v3 tested with component gains/no complete-workload gain; no new real execution | 471 historical full synthetic tests |
| 0015 Versioned Bounded-Age Monitoring / Conditional Runtime Revalidation | `0610c0f`, verified in Task0016 | V4 observation change tested; paired gain2.1403× misses3×, zero new real work/readiness/slot; original96steps consumed | 532 historical final full synthetic tests |
| 0016 Engineering-Gate Review / Bounded v4 Runtime Characterization | `f74c7db`, verified in Task0017 | Typed diagnostic admission; automatic3.558GiB fail and later manualWARN2/no admitted availability,0real data/steps; unreserved canonical slot | 576 historical full synthetic tests |
| 0017 User-Triggered Readiness / Single Shared Characterization Slot | `b194050`, verified in Task0018; initial tree/index clean | Reconciled manualWARN; repeatable explicit read-only history/separate run with canonical Task0016 anchor,0newallowance. One integration3.705841GiB fails floor,0real work/slot | 612 full synthetic tests |
| 0018 Shared-Mac Development Policy / Bounded Characterization | `5da9094`, verified in Task0019; original base `b194050` | Strict dev-only process policy/default CLI, complete additional96updates/exact parity/240.728s target failure, shared anchor consumed192/192; no canonical scope | 670 historical full/portable synthetic tests |
| 0019 Canonical Particle Feasibility / Project Progression Decision | `c3008d4`, verified in Task0020; base `5da9094`; initially clean | Local canonical particle execution deferred under unchanged contracts; budgets/full-custody limits consolidated; frozen PCA/AE v2 CPU benchmark next, no new real work/permission | Small-file arithmetic/JSON/identity/lineage/link/diff checks; no suite rerun |
| 0020 Frozen PCA/AE CPU Inference Benchmark Foundation | Awaiting user commit; base `c3008d4`; initially clean | Guarded fixed CPU protocol implemented; one1024dev preparation/PCA1complete, AE1numerical veto/15of90cells, slot consumed, no retry/refit/calibration/MPS/test | 763full+portable synthetic tests; new86-entry acceptance before execution |

These counts and experiment outcomes belong to their corresponding tasks. Task0013 actually reran the full synthetic suite; no real training/store check was repeated for memory maintenance. A configured CI job is not a verified hosted CI success.

### 10.1 Training-background data observations

- 699,957 training events, 127,379,949 valid particles.
- Multiplicity min/max 22/560; mean 181.982535; population std 61.020073; median 177.
- Multiplicity p90/p95/p99/p99.5/p99.9: 263 / 291 / 344 / 365 / 408.044.
- Raw training pT min/max/median: 0.011443535 / 3138.8899 / 3.1709824 GeV; mean 15.935601 GeV, std 52.263314 GeV.
- All 699,957 training events contain at least one pT increase in raw slot order. Source order is not descending pT.
- All raw training particle values round-trip float64 -> float32 -> float64 exactly. This does not imply exactness of newly computed logs, wrapping, or aggregates.

### 10.2 Processed-store results

| Store | Events | Particles | Total bytes including metadata |
| --- | ---: | ---: | ---: |
| Dev | 8,494 | 1,549,328 | 23,055,615 |
| Independent dev repeat | 8,494 | 1,549,328 | 23,055,615 |
| Full | 1,100,000 | 195,918,046 | 2,906,852,158 |

Independent dev builds with chunks 992 and 496 reproduce all 11 arrays and configuration bytes, dtypes, shapes, scientific hashes, views, masks, and truncation metadata. Exactly 27 dev events truncate in the model view. Full/dev content matches on all 8,494 common allowed background events. Full event IDs cover ordinals 0 through 1,099,999.

Full raw cast error was zero in all three channels. Two source phi values required wrapping; the subsequent maximum FP32 angular error was `6.357301884918343e-8 rad`. Real rounded-sort diagnostics found no ordering change; source-before-cast ordering remains required and synthetic adversarial tests cover it. Six independent scalar-math spot checks showed aggregate differences no larger than `1.8189894035458565e-12`; standardized FP32 results matched exactly.

### 10.3 Engineering observations, not inference benchmarks

Task 0005 recorded:

| Build | Chunk events | Write/hash seconds | Verification seconds | Lifetime peak RSS |
| --- | ---: | ---: | ---: | --- |
| Dev | 992 | 4.754 | 0.086 | 298 MiB |
| Dev repeat | 496 | 5.277 | 0.087 | 252 MiB |
| Full | 992 | 143.771 | 6.366 | 2.44 GiB |

These exclude raw/input verification; mmap pages contribute to RSS. EDA temporary streams peaked at 3,101,916,024 bytes. Resource observations establish local feasibility, not trigger latency or controlled device performance.

## 11. Canonical model registry and measured results

### 11.1 Model roles

| Model | Role | Input / compression | Artifact |
| --- | --- | --- | --- |
| PCA reconstruction v1 | Frozen linear baseline | Eight aggregates; six retained axes | Local ignored `data/baselines/pca-v1/model.json`; curated results tracked |
| Compact AE v1 | Historical Task 0007 baseline, preserved | Eight aggregates; latent dimension three | [v1 model](../artifacts/models/compact-autoencoder-v1/model.json) |
| Compact AE v2 | Current canonical compact AE | Same architecture/input; later background-selected epoch | [v2 model](../artifacts/models/compact-autoencoder-v2/model.json) |
| Particle/set model | Implemented; original96+new96dev steps completed on same1024IDs; shared-host-dev-v1 measured;240.728s>180s, anchor/cumulative192consumed, local canonical execution deferred byTask0019 | Existing particle view plus mask; distributed local2 + mean8 code | [Executable configuration](../configs/models/compact_particle_set_autoencoder_v1.json), [report](particle-set-baseline.md); no frozen trained artifact/hash |

Implemented PCA/AE reconstruction scores remain SSE, larger means more anomalous. The implemented particle score instead uses a masked mean of weighted corresponding-particle residuals (defined below); raw scales are not directly comparable. Raw scores are not normalized for plotting; `ln(1+s)` is only a display transform where used in reports.

### 11.2 PCA baseline

Fit scikit-learn PCA using deterministic full SVD, float64 fitting, internal mean centering, no whitening, and no randomized solver on 699,957 training-background events. Select the smallest `k` reaching at least 95% cumulative **training** variance. No validation/signal-based retuning of `k`.

- Selected `k=6`.
- Retained variance 97.870086%.
- Five components retain 92.824643%.
- Variance-ratio spectrum, rounded for readability: 0.321932423 / 0.225297891 / 0.143915339 / 0.125000234 / 0.112100547 / 0.050454430 / 0.014317469 / 0.006981666.

```text
x_hat = mu + W.T @ W @ (x - mu)
score = sum_j (x_j - x_hat_j)^2
```

PCA saves 88 fitted numeric values: eight means, all eight axes, eight variances, eight variance ratios. Inference with six axes needs 56 coefficients including mean. Reported historical JSON size: 9,253 bytes. The mean residual agrees with discarded covariance eigenvalues times `(N-1)/N` to approximately `7e-16`.

Two independent real CPU runs reproduced parameters, scientific identities, score bytes, summaries, thresholds, tables, and figures exactly. This is local reproducibility, not guaranteed cross-platform BLAS identity.

**Background score summary** (numeric values copied from the curated CSV).

| Statistic | Training background | Selection background | Calibration background |
| --- | ---: | ---: | ---: |
| Events | 699957 | 74749 | 74823 |
| Mean SSE | 0.1703930829078328 | 0.17224552267031595 | 0.17282825364807736 |
| Population std | 0.3264928275983368 | 0.33077439810622167 | 0.3370284958137342 |
| Minimum | 6.229852392536156e-08 | 1.393933666930995e-06 | 2.716535882116778e-06 |
| Median | 0.09292943414097307 | 0.09344209250212934 | 0.09375141510825061 |
| p90 | 0.3466508725381213 | 0.3479482193778987 | 0.34967140578815487 |
| p95 | 0.5592304760861656 | 0.5627889007032169 | 0.5642050265377994 |
| p99 | 1.3908934004212525 | 1.4278172120604116 | 1.4231736552552572 |
| p99.9 | 4.011884664834042 | 4.005847266759414 | 4.118285218225896 |
| Maximum | 19.732761907767095 | 13.790413217924574 | 14.88682560350527 |

**Frozen calibration and independent selection check.** Calibration total 74,823; selection total 74,749. All decisions use strict `score > threshold`.

| Target FPR | SSE threshold | Calibration accepted | Calibration FPR | Selection accepted | Selection FPR |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 0.3496768162794852 | 7482 | 0.0999959905376689 | 7425 | 0.09933243254090356 |
| 0.05 | 0.5642097175249418 | 3741 | 0.04999799526883445 | 3729 | 0.04988695500943156 |
| 0.01 | 1.4232146905138892 | 748 | 0.00999692607887949 | 754 | 0.01008709146610657 |
| 0.001 | 4.1356483360291865 | 74 | 0.000989000708338345 | 71 | 0.0009498454828827141 |

**ECDF stability:** `train_vs_selection_ks` = 0.00446978684512106; `train_vs_calibration_ks` = 0.005223804426272655; `selection_vs_calibration_ks` = 0.00233090873155567.

At target FPR `1e-3`, the selection Wilson 95% interval is [0.0007531787855375236, 0.0011978033574092997]. Interpret relative tail deviations together with accepted counts and finite-sample uncertainty.

Detailed evidence: [pca-baseline.md](pca-baseline.md), [score summary](../results/tables/final/task0006-pca-background-summary.csv), [threshold results](../results/tables/final/task0006-pca-thresholds.csv), and [scientific JSON](../results/tables/final/task0006-pca-background-results.json).

### 11.3 Compact AE v1: historical result

Architecture: **`8 -> 6 -> 3 -> 6 -> 8`**, biased Linear layers; ReLU after the first encoder and first decoder layer; linear latent and output. Layer parameter counts 54+21+24+56 = **155**; raw FP32 parameter payload 620 bytes. No BatchNorm, dropout, residual blocks, or stochastic latent variables.

Frozen Task 0007 training choices:

- CPU canonical device; default PyTorch Linear initialization.
- Adam with default settings except learning rate 0.001.
- Batch size 4,096; deterministic shuffled batches, zero workers, no dropped tail.
- Seed 1729 for Python/NumPy/PyTorch and a separate shuffle generator.
- Deterministic algorithms; one intra-op CPU thread; observed inter-op setting 10.
- Channel-mean reconstruction MSE; equal event weights.
- Selection-background loss chooses epoch; patience 15, `min_delta=0`, strict improvement.
- Maximum 200 epochs.
- Calibration first loaded after best-state restoration and JSON export.

| Historical v1 result | Exact recorded value |
| --- | --- |
| Best epoch / executed epochs | 200 / 200 |
| Stop reason | `max_epochs`; zero consecutive non-improvements at stop |
| Best-epoch online training MSE | 0.22106828705179374 |
| Restored training MSE | 0.22100737705508344 |
| Best/restored selection MSE | 0.22261241728016284 |
| Canonical CPU training time | Approximately 31.18 seconds |
| Frozen JSON size | 11,945 bytes |

Forward/training arithmetic is FP32; score residual subtraction and SSE accumulation are CPU float64. Online training loss differs from restored-model loss because weights change within each epoch.

An independent full CPU rerun reproduced parameters, best epoch, scores, thresholds, summaries, tables, and figures exactly. A bounded latent check on the first 4,096 training-background events found finite values and no latent dimension with std at or below `1e-6`; it did not establish anomaly separation.

MPS compatibility used a separately initialized model for five Adam steps on 256 dev-training events, with finite forward/backward/scoring and loss approximately 0.999993265 -> 0.993118167. It exported no model and did not change canonical CPU weights. This is compatibility evidence, not a GPU benchmark.

**Background score summary** (numeric values copied from the curated CSV).

| Statistic | Training background | Selection background | Calibration background |
| --- | ---: | ---: | ---: |
| Events | 699957 | 74749 | 74823 |
| Mean SSE | 1.7680590277287618 | 1.7808993585556105 | 1.772382559767443 |
| Population std | 1.7509019423485825 | 1.7712287676678398 | 1.7475908900988042 |
| Minimum | 0.003588227986996817 | 0.016227133069896114 | 0.010355208376892137 |
| Median | 1.2739098618037987 | 1.27688273999012 | 1.2707276563316627 |
| p90 | 3.5868977539147466 | 3.61893284860893 | 3.6136349957311795 |
| p95 | 4.82906305560913 | 4.8702253578436006 | 4.862806190313804 |
| p99 | 8.589193778026782 | 8.708859649389234 | 8.637979526308955 |
| p99.9 | 16.557594381446762 | 16.29073783445919 | 16.501406212993558 |
| Maximum | 60.359542744402596 | 46.17539573286683 | 35.97693648552873 |

**Frozen calibration and independent selection check.** Calibration total 74,823; selection total 74,749. All decisions use strict `score > threshold`.

| Target FPR | SSE threshold | Calibration accepted | Calibration FPR | Selection accepted | Selection FPR |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 3.613707299930235 | 7482 | 0.0999959905376689 | 7498 | 0.1003090342345717 |
| 0.05 | 4.862834912896428 | 3741 | 0.04999799526883445 | 3751 | 0.05018127332807128 |
| 0.01 | 8.638938683116985 | 748 | 0.00999692607887949 | 772 | 0.010327897363175426 |
| 0.001 | 16.547151319930283 | 74 | 0.000989000708338345 | 73 | 0.0009766016936681428 |

**ECDF stability:** `train_vs_selection_ks` = 0.003388391473781671; `train_vs_calibration_ks` = 0.003285154347487884; `selection_vs_calibration_ks` = 0.004888069666493078.

At target FPR `1e-3`, the selection Wilson 95% interval is [0.0007768684401031215, 0.0012276233744754283]. Interpret relative tail deviations together with accepted counts and finite-sample uncertainty.

Detailed evidence: [compact-autoencoder.md](compact-autoencoder.md), [score summary](../results/tables/final/task0007-autoencoder-background-summary.csv), [threshold results](../results/tables/final/task0007-autoencoder-thresholds.csv), and [scientific JSON](../results/tables/final/task0007-autoencoder-results.json).

### 11.4 Why Task 0008 was necessary

V1's best epoch equaled the 200-epoch ceiling, with training still improving. The ceiling, rather than the stopping rule, determined the endpoint. Convergence was therefore unresolved, and introducing a richer neural architecture first would have left an avoidable methodological weakness in the compact baseline.

Task 0008 changed only `max_epochs: 200 -> 1000`, in a separate preserved v2 configuration. Architecture, optimizer, learning rate, batch size, initialization, seed/shuffle, deterministic CPU path, patience, `min_delta`, loss, populations, and preprocessing stayed unchanged. It retrained from scratch rather than resuming v1.

Mandatory prefix validation compared epochs 1-200 training/selection losses and best-state progression, plus exact FP32 parameter bytes at epoch 200. A mismatch would abort before interpreting later training or accessing calibration.

The planned cap-failure rule was also explicit: if the 1,000-epoch ceiling still determined the endpoint, report convergence unresolved and require a new methodological decision. Do not silently extend again or change optimizer/learning-rate policy within the closure task.

### 11.5 AE v2: current canonical result

Both independent extensions reproduced the historical first 200 epochs/progression and epoch-200 parameter bytes exactly.

| Current v2 result | Exact recorded value |
| --- | --- |
| Best epoch | 381 |
| Executed/stopping epoch | 396 |
| Stop reason | `patience`, 15 consecutive selection non-improvements |
| Best-epoch online training MSE | 0.21318465057790426 |
| Restored training MSE | 0.21305374425537163 |
| Best/restored selection MSE | 0.21447598731176187 |
| Last-epoch selection MSE, not selected | 0.2146456583262472 |
| Selection MSE improvement relative to v1 | Approximately 0.0081364299684, or 3.654976% |
| First / repeat extension training time | Approximately 59.700 / 59.063 seconds |
| Frozen JSON size | 11,941 bytes |
| Architecture / parameter count | Unchanged; 155 parameters |
| Interchange schema | `artifact_version=1`, despite model generation v2 |

**`compact-autoencoder-v2` supersedes v1 as the canonical compact AE.** The decision used exact prefix reproduction, continued training, strictly improved permitted selection loss, and an intact protocol/embargo. No signal information was used. Preserve v1 configuration, artifact, history, results, and task records.

Convergence closure means reaching the preregistered selection-patience endpoint. It does not prove a global optimum, a stationary training objective, an optimal architecture, or useful anomaly discrimination.

The independent v2 repeat reproduced all 396 epochs, selected weights, score-byte hashes, calibration, summaries, tables, and figure. Task 0008 kept scores in memory and saved their byte hashes; it wrote no per-event score arrays or checkpoints.

**Background score summary** (numeric values copied from the curated CSV).

| Statistic | Training background | Selection background | Calibration background |
| --- | ---: | ---: | ---: |
| Events | 699957 | 74749 | 74823 |
| Mean SSE | 1.7044299494344979 | 1.715807899924844 | 1.7158543992416249 |
| Population std | 1.6910402847301644 | 1.7099464304119902 | 1.7025519418076287 |
| Minimum | 0.005736122334827163 | 0.004962340965368073 | 0.012284028003597458 |
| Median | 1.2366082661770676 | 1.2410126407231847 | 1.2331580252857184 |
| p90 | 3.448114682422827 | 3.478031649472065 | 3.478330842943409 |
| p95 | 4.624700508292133 | 4.656520761689697 | 4.681018670431604 |
| p99 | 8.234200550503136 | 8.329682543754172 | 8.32375940704894 |
| p99.9 | 16.177322559458133 | 16.02839949271337 | 16.438957022844345 |
| Maximum | 70.74881844526628 | 43.981107267994176 | 40.728911220593275 |

**Frozen calibration and independent selection check.** Calibration total 74,823; selection total 74,749. All decisions use strict `score > threshold`.

| Target FPR | SSE threshold | Calibration accepted | Calibration FPR | Selection accepted | Selection FPR |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 3.478338537407165 | 7482 | 0.0999959905376689 | 7475 | 0.10000133781053927 |
| 0.05 | 4.681070974717348 | 3741 | 0.04999799526883445 | 3698 | 0.04947223374225742 |
| 0.01 | 8.324174660133213 | 748 | 0.00999692607887949 | 749 | 0.010020200939143 |
| 0.001 | 16.642218868621573 | 74 | 0.000989000708338345 | 64 | 0.0008561987451337141 |

**ECDF stability:** `train_vs_selection_ks` = 0.0034533996621334273; `train_vs_calibration_ks` = 0.004705428147432911; `selection_vs_calibration_ks` = 0.0047360563555980395.

At target FPR `1e-3`, the selection Wilson 95% interval is [0.0006706163426728948, 0.0010930819495628859]. Interpret relative tail deviations together with accepted counts and finite-sample uncertainty.

Detailed evidence: [autoencoder-convergence.md](autoencoder-convergence.md), [score summary](../results/tables/final/task0008-autoencoder-background-summary.csv), [threshold results](../results/tables/final/task0008-autoencoder-thresholds.csv), and [scientific JSON](../results/tables/final/task0008-autoencoder-convergence-summary.json).

### 11.6 What the model comparison currently means

PCA retains six dimensions while the AE retains three. Training mean SSE is approximately 0.170393083 for PCA, 1.768059028 for v1, and 1.704429949 for v2. Different compression capacities prevent interpreting these losses as a controlled comparison of linearity versus nonlinearity or as a signal-performance ranking.

Background-only Tasks0006–0008 established functioning score/calibration pipelines without signal sensitivity claims. Task0026 supplies the first explicitly authorized held-out scientific comparison: PCA AUC0.468488658/AP0.364379155, AE0.660063803/AP0.547427268 at evaluated test prevalence0.399247817. Frozen AE has greater sampled signal acceptance at each operating point, but tight-tail sensitivity remains low. This does not retroactively use signal to select either model or prove causal nonlinearity; all training/config/threshold identities persist.

Task0027 completes [the integrated synthesis](scientific-synthesis.md). Global ranking and all four original calibrated points are retained alongside the ten accepted adapter cost groups. At strict AE target0.001, greater signal count than PCA coexists with TPR below achieved FPR and selected signal fraction below evaluated prevalence; observed enrichment is absent in this slice. AP and selected fractions depend on the sample mixture, not physical LHC rates. No causal mechanism for ranking/tail behavior is established; representation/bottleneck/objective/score explanations remain hypotheses. The initial comparison is complete; capacity control, bias and other signals/populations are independent extensions.

### 11.7 Particle/set design, implementation and bounded characterization (Tasks0009–0019; local canonical deferred)

Five biased shared Linear layers: encoder 4→16 ReLU→8 ReLU; local 8→2 linear; global g is the masked mean of the eight encoder values; decoder concatenates [local2,g8] and applies 10→16 ReLU→4 linear. Total 80+136+18+176+68=478 parameters. No raw-feature or hidden skips, input positions, output queries, auxiliary heads or normalization layers. Pooling is FP64 then cast to FP32; dense forward is FP32. Local/output arrays permute with particles; g and score are invariant mathematically, with declared numerical tolerances.

Exact per-particle distance is `d=(r0²+r1²+0.5*r2²+0.5*r3²)/3`. Training and canonical score are `s=L_event=sum_valid(d)/n_retained`, with FP64 subtraction/reduction and equal-event batch/epoch weighting. Correspondence follows each particle's own local code; no nearest-neighbor or assignment solver. Angular outputs are unconstrained sin/cos values; seam continuity and off-circle residuals follow the formula, with no angle normalization or added penalty.

Capacity is 2n+8 real values plus validity metadata (776 floats at n384). Target information intentionally travels through each local2 and through mean8; small-n events can bypass strong compression through context. Equal-particle means can dilute rare residuals and are blind to uniform replication within capacity. Count is supplied by the mask, not independently reconstructed; original multiplicity and retained-pT fraction remain diagnostics. Truncation and absent particle labels constrain the physics information. Learned joint particle features use information absent from the fixed aggregates, but eight pooled means do not capture arbitrary pair relations. No rotation/IRC-safety or anomaly-performance claim.

Preregistered CPU training: seed1729, default Linear initialization in fixed layer order, explicit ordinary Adam options/lr0.001, batch32, workers0, shuffled complete train population/no dropped tail, one intra-op/inter-op thread, deterministic algorithms, no AMP/schedule/fallback. Full selection mean canonical score chooses strict improvements (ties retain earliest); min_delta0, patience20, max200 epochs, best-state restoration and exact independent reload/CPU reproduction before freeze/calibration. Resource or epoch cap without patience means convergence unresolved, requiring a new versioned decision.

The preregistered dev gate uses only first1,024 frozen dev-training IDs, at most three passes/96 steps plus one same-sample score pass, ≤300s; conservative full-cycle extrapolation must be ≤180s. Canonical cycles have a 180s ceiling, each fit+selection run ≤10h and postfit stages ≤1h; two complete repetitions ≤22h. The design alone authorizes no execution; Task 0010 explicitly authorized conditional stages. Its launch gate failed before any real read/update, and no later stage was reached. See [full contracts and acceptance gates](particle-set-baseline-design.md), [budget](../results/tables/final/task0009-particle-set-design-budget.csv), [implementation outcome](particle-set-baseline.md) and [Task 0010 handoff](handoffs/0010-particle-set-baseline.md). Task 0011 preserves this failure and both original/final source acceptance records, renews acceptance after narrow orchestration/probe changes, and records failed stable readiness without consuming the one newly authorized real attempt. See [recovery contracts and evidence](particle-set-resource-recovery.md). The2026-10-07 explicit resumption reverified existing current acceptance and performed exactly one new failed launch-readiness check; no code/scientific change or redundant training/test-suite rerun. Task0012 renews source acceptance after engineering observer/lineage changes; model/reader/loss/training JSON bytes stay unchanged. V2 sidecar distinguishes engineering profile from mathematical configuration. Reader64/custody/dev are implemented and guarded but unexecuted because even4GiB availability fails. No statement of actual reader footprint, convergence or signal performance follows.

Task0013 preserves scientific source/config bytes and adds stdlib-only supervision with422synthetic tests. Its initial accounting result/curated summary remain historical, but the subsequent external study passed memory/reader/custody and bounded-dev activation, completed original96steps and failed the fixed conservative throughput gate749.3431957854029s>180s. This is engineering throughput failure, not convergence. No trained/frozen particle artifact or canonical calibration exists. Task0014 reconciles actual receipts and adds v3 cached-binding resource instrumentation with471tests and exact synthetic numerical/Adam parity; no new real step or data request. The small synthetic state-comparison hashes are not canonical trained-model identities. [Monitor performance](particle-monitor-performance.md) preserves component gains/no observed workload gain. [Task0015 bounded sampling](particle-bounded-sampling.md) supersedes that proposal with an explicit observation change,532tests and paired2.1403×gain below3×; no new real work or original-route retry/disposable weight reuse. That task-time acceptance covers its five new source modules/tests; comparison hashes remain synthetic only. Task0016 now provides separate prospective diagnostic authorization/current576-test full acceptance without changing old entries. Its automatic and later manualWARN readiness failures precede real data; original/cumulative96 unchanged. Task0017 preserves those and adds repeatable explicit checks with immutable history/separate fresh-check run on the same anchor;612tests/one check-only integration,0realwork.

Task0018 adds development-only process policy without scientific changes and completes one additional disposable96step run. Every remaining budget is now consumed: original96+new96=192/192, no inflight, same1024IDs. Per1024training times[0.16781862499919953,0.13851762500416953,0.13835891600319883]s/scoring0.07742041700112168s; unchanged2×(114.71271611187959+5.6514636234539495)=240.72835947066707s>180s. Final objective0.8151977394784519/mean0.7520234728718791/score SHA31475c619699ee85c2e44a2e74e29a32dea3a5e092b441ccfa54a9e117343a13 match Task0013 exactly under PyTorch2.14.1. These are disposable diagnostic values/hashes, not a canonical artifact, independent full training or model quality. [Shared-host policy](particle-shared-host-policy.md) records caps, optional context, source identity, receipts and limitations; full-run compatibility/convergence/calibration remains pending. Task0019 now defers local canonical execution under unchanged contracts after consolidating the time/full-store/shared-host evidence. No new measurements or active policy changes; scientific rejection is not implied. Frozen PCA/AE v2 CPU hardware work is the selected next route.

### 11.8 Three-prong extension: software accepted, Phase B failed/consumed

The same frozen PCA-v1/compact AE v2, original thresholds/features/scalers and
accepted exposed150471background scores were bound to the human-approved plan
77f92d95…179fa9. The sole acquired attempt failed at its298s operation deadline:
parent298.033886542s, worker297.972533500s, whole298.116751583s, exit1/reaped /
parent rejected. Deadline guard error, not memory rejection; observedRSS39.4375MiB /
native44MiB/parent28.484375MiB,5494WARNadvisory, noCRITICAL;0.020402125s terminal gap.
No verified payload, actual count/layout/class/duplicates/overlap, originalFP
numerical read, preparation, new signal scoring or cached-score numerical reuse.
AUC/AP/prevalence/efficiencies/intervals/relative acceptance/tail utility and
topology comparison are unavailable, not zero performance. Expected100000 /
50B4096batches/200000presentations/2cache loads remain unfulfilled plan counts.
The raw interrupted-request in-flight flag remains true, although worker exited /
reaped and no model-scoring in-flight exists. Frozen downloader cleanup removed
its own .part; logged≥47185920B is only a lower bound, not verified custody.
All surviving metadata, logs, guards and receipts are preserved, code/protocol /
139source/dependency acceptance unchanged. No retry/resume/schema/cap change.
Original testsYES/YES permanent, new signal modelNO; optimizer0, Task0025failed /
consumed/provisional, particle192/192consumed/deferred. A separate prospective
policy/authorization decision is needed for any replacement; shared background
would still preclude fresh independent BG/generalization or significance claims.

## 12. Evaluation, calibration, and uncertainty

Protocol: `latenttrigger-evaluation-v1`; see [evaluation-protocol.md](evaluation-protocol.md).

### 12.1 Threshold contract

For target FPR `alpha` in `{0.1, 0.05, 0.01, 0.001}`, use calibration-background scores only:

```text
tau_alpha = sorted_scores[ceil((N - 1) * (1 - alpha))]
accept iff score > tau_alpha
```

This is NumPy `quantile(..., method="higher")`, with a strict `>` decision, including ties. It is conservative for empirical calibration acceptance, not a guarantee of population or independent selection acceptance.

Do not jitter ties, interpolate thresholds, or refit them using selection/test. Check frozen thresholds on selection background as a diagnostic. Calibration does not choose the winning model.

Summary quantiles use linear interpolation; calibration quantiles use higher. Preserve that distinction.

### 12.2 Metrics and reporting conventions

| Metric | Convention |
| --- | --- |
| ROC-AUC | Empirical rank-based area, score orientation as supplied; no silent flip |
| Average Precision | Recall-increment-weighted precision, not trapezoidal PR area; report prevalence/class counts |
| Signal efficiency / TPR | Accepted signal / total signal |
| Background efficiency / FPR | Accepted background / total background |
| Rejection | `1/FPR` when nonzero; zero observations require null rejection plus uncertainty, not infinity |
| TPR at fixed FPR | Largest attainable empirical TPR with achieved FPR <= target; no interpolation over unattainable tie jumps |
| FPR at fixed TPR | Highest-threshold empirical point reaching TPR target, initially 0.5/0.8/0.9 |
| Rate uncertainty | Counts, totals, empirical resolution `1/N`, and 95% Wilson binomial intervals |
| Zero-background acceptance | One-sided exact 95% upper bound `1 - 0.05^(1/N)` under the sampling assumption |

Descriptive final ROC operating points are not substitutes for deployable calibration-frozen thresholds. The implementation preserves strict-`>` semantics for ROC cutoffs and handles accept-none/accept-all explicitly.

Calibration contains approximately 74.823 expected tail events at FPR `1e-3`; test background approximately 150.471 at `1e-3` and 15.0471 at `1e-4`. Do not extrapolate extreme rejection beyond empirical support. Binomial intervals do not cover simulation, model-selection, or calibration uncertainty.

Background summaries include count, mean, population std, min, median, p90/p95/p99/p99.9, and max. Compare ECDFs with KS distance descriptively; do not tune against diagnostic p-values. Monitor score/acceptance against multiplicity, scalar pT, maximum pT, massless event mass, and retained pT fraction.

### 12.3 Final unblinding gate

Before the first real final-evaluation request, an explicitly authorized task must freeze candidate models/runtime variants, configurations, preprocessing/store/split identities, score semantics, calibration thresholds, metrics, uncertainty, and reporting plan.

The separate final CLI requires `--allow-test` and explicit frozen inputs. Before each test population request, create/preserve `test-unblinding.json` with UTC, code/base/dirty hashes, model/config/data/calibration identities, planned metrics, and access counts. Keep failed/interrupted records; save final output hashes and completion status. Disclose the exposure and candidate list in the corresponding task record and update this memory's exposure status.

Task0026 adds the isolated guarded route around unchanged scientific primitives: source-bound explicit human audit, parent-confirmed lifecycle,6GiB/512MiB caps, exact4096tails and durable pre-read/per-batch/inflight progress. Phase A readiness is reused after actual human consent; Phase B completes/consumes the final namespace and exposes both tests to both frozen candidates, no unknown inflight. A local consent file is an audit binding to that real human message, not permission inferred from its existence. Calibration-frozen operating points remain separate from descriptive final ROC thresholds. No post-test retraining/recalibration/candidate selection.

If test results motivate a new design, disclose it and establish a new protocol/population. Do not describe the already-exposed test as untouched again.

## 13. Hardware inference and deployment methodology

**Latest measured raw boundary:** Task0040 implements the separate authenticated payload grant and completes one parent-accepted36cell selected-HDF/read/feature/direct-joint study with exact development golden parity. Task0039 resolver/design remains historical metadata-only. Pooled B128read45.143/features5.778/directjoint50.013ms; fixed sparse/warm cache context and serial variability are disclosed, physical I/O/decoder threading unknown. No models in Task0040, sum-of-medians whole-chain estimate, deployment policy or Task0037change.

**Latest separate boundary:** Task0038 measures owned prepared-batch packing/zero padding, original CPU public adapter/four decisions and actual-row retention in one accepted development-only session. It preserves Task0022 preloaded-adapter evidence and Task0037 fixed simulation. All204cells/three inspected figures, finite numerical invariance and observed serial variability are available; no production-p99, deployment winner or missing-chain sum claim.

**Status:** [Task0022CPUv2](frozen-cpu-benchmark-v2.md) is implemented, validated and measured completely under explicit prospective engineering-policy authorization. Its new90cells/18000timings/1800warm-ups/1200empty pairs come from three independent workers per model; oldPCA1is not mixed in. All pre/post numerical, local affine, supported-band, same-shape, reference/hash and strict frozen decision requirements pass. Task0020partial/v1failure and Task0021diagnostic are historical, byte preserved; v2 does not retroactively pass them.

Frozen first1024dev-training FP32 aggregates are reused without scaling/store/custody/population requests; one original prepared-array read, one byte-identical local copy and six local reads. Canonical numerical forward presentations239616, timed4294800/warm-up429480, diagnostic FP64 whole-model6144/local-affine147456rows (layer operations counted separately); unique real rows1024/optimizer0. CPU1+1/effective OpenMP1/public Accelerate single-thread mode and actual build are verified. Five batches and three original timing kernels/scopes unchanged, guard queries outside pairs/periodic overlap disclosed. Full wall25.661481s versus600s, maxRSS348.609375MiB/native183.671875MiB versus1GiB/512MiB, parent27.03125MiB versus128MiB; children/watchers closed, pressure unknown/errno1/context no floor.

New [arithmetic derivation](arithmetic-cpu-v2-policy.md) includes both FP32 and rounded FP64 path rounding, per-operation outward products/sums/denominators/gamma/recurrence, checked2^-40…2^40nonzero support band, ordinary bounded IEEE accumulation assumptions and local affine checks. SSE exact residual magnitude is bounded from computed residual; gamma32(u64)/(1-gamma32) converts both exact nonnegative score scales to observed scales. No fitted slack or backend/precision/thread/operator change; engineering certificate only for supported scope, not exact kernel causality/universal backend proof. PCA retains1e-12/1e-12 and AE preserves exact same-shape repeats/original SSE1e-12/frozen strict decisions.

All AE workers pre/post: B1maxreconstruction5.4359436e-5 versus pair-envelope maximum0.0147545511 (maxpointwise ratio0.0102172935); score2.0492838e-4 versus0.0917121409 (ratio0.00401697314). B8/32/128errors1.3351440e-5/1.1829054e-4; B1024matches reference exactly. Local scalar comparisons847872total,0violations/maxratio0.2730991355. All four sampled threshold mismatches0; exact restored canonical/diagnostic/envelope hashes. Reference margins0.00933623417/0.00408397869/0.160126684/3.752131356. Conservative envelope size is not measured error; sampled agreement is not universal/calibration/test FPR. Historical Task0020firstfailure1.989305e-6 atrow7/channel5, confirmed inTask0021, remains failed under v1.

Median of three worker p50s for public adapter B1:PCA8.125µs/AE24.708µs; B1024:PCA44.4585µs/AE85.5µs. Defined pooled-throughputB/mean across600calls:B1024PCA22.3247millionevents/s/AE11.8714million. All90per-worker distributions and group medians retained in [CSV](../results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv)/[JSON](../results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json). AE2B128max26.2485ms remains, lowers pooled throughput; no favorable filtering or specific interference attribution. Different scopes are not added into end-to-end latency. Fixed order/200samplep99/warm cache/OS/watchdog/shared-host variability and input/model-loading instrumentation gaps remain explicit; no physical trigger/discrimination claim.

Fresh filtered hardware metadata inside v2 reports M5/16GB/Mac17,2/processor10:4:6:0, arm64/macOS26.6.2/AC80%/shared load; native sysctl and thermal values unknown. Current CPU smoke reports MPSunavailable; physical hardware/build flags alone do not establish usable runtime. Task0023subsequently implements its device foundation; sole check unavailable, no paired execution, current software-only repair acceptance separate from old failed proof. CoreML/quantization/simulation remain unmeasured; Task0026 subsequently completed native test evaluation and Task0027 its synthesis. Particle192/deferral unchanged.

Task0023 adds separate prospective operation-level MPS arithmetic/local-affine/ReLU/SSE/strict-decision requirements, exact FP32 transfer/repeatability, primary tensor256MiB/driver512MiB guards and correct completion timing. CPU gamma is not a universal Metal certificate. Same frozen155FP32AE/features/scalers/thresholds and original32896-byte input only;0numerical reads/rows/presentations/population/custody/updates here. Sole check child323MiB RSS/171.671875MiB native, parent27.75MiB,1.965876s child /2.572505swhole;36unknown-pressure samples/31periodic, guards closed/child reaped, device allocations unqueried/unknown.1032precheck/1033final full+portable tests,91newcases and current software-only acceptance; three source files repaired after check, original104-source snapshot retained, no current physical proof or replay. See [report](frozen-cpu-mps-benchmark.md)/[summary](../results/tables/final/task0023-cpu-mps-benchmark-summary.json). No timings/ratios/CSV or scientific quality/trigger claim.

Task0024adds reconstruction-only ONNX/opset18/IR10/fourGemm+twoRelu,155exactFP32parameters, CPU-only sequential1/1/optimization-disabled/fallback-disabled ORT; external canonical FP64 SSE/strict thresholds unchanged. All four fixed synthetic families and1193real windows/1024reused rows pass. Maxreal reconstruction3.9100647e-5/pair-bound utilization0.00787369 and SSE4.8503804e-5/utilization0.00160749 at every grid, zero four-threshold mismatches;259072real local scalar comparisons/0violations, byte-exact own repeats/diagnostic-primary final/SSE, restored references/input/params/threshold/artifact.11464B derived export SHA`4250b008…d04793`, not a new scientific model.1original numerical array read/0store/custody/population/optimizer/performance timers. Whole19.407739s, RSS445.671875MiB/native215.671875MiB/parent28.421875MiB, all caps/cleanup pass; pressure unknown/errno1.1111full+portable/78newtests and optional actual integration/guarded CPU smoke before114-source freeze. ONNX1.23.2/ORT1.31.0/onnxscript0.7.2 plus4missing transitive packages added in164.874s, all36prior versions/core file/build identities retained; optional export extra, no source builds or baseline upgrade. Source/receipt/scientific history unchanged, no MPS check/replay. See [report](frozen-ae-onnx-cpu-export.md)/[summary](../results/tables/final/task0024-ae-onnx-cpu-export-summary.json); equivalence establishes no speed benefit.

Task0025 paired CPU foundation is validated (1179 full + portable / 68 new tests) and source-frozen before its sole campaign. All six worker bodies pass pre/post outward/local/repeat/strict decisions; 90 cells, 18000 timings, 1800 warm-ups, 1200 empty pairs. ORT3 reports completion at 10.072625084 s but its process remains alive; parent deadline sends SIGTERM and reaps at 58.030580209 s. Campaign failed/consumed, no repair/replay or accepted paired speedup. Raw B1/B128/B1024 reconstruction pooled PyTorch/ORT ratios 1.909/1.582/1.391 and adapter 4.629/1.974/1.346 are provisional; PyTorch1 B1 adapter mean 169.292 µs versus later 23.662/23.599 µs shows variability, with no causal attribution. Common CPU score-only ratios are not ONNX acceleration. Whole 128.780991583 s; observed worker RSS 398.484375 MiB/native 203.671875 MiB, parent 36.953125 MiB; terminal memory behavior after ORT3 guard closure is unknown. 1 original + 6 local reads, 1024 reused rows, 0 population/custody/optimizer. See [report](pytorch-onnx-cpu-benchmark.md), [summary](../results/tables/final/task0025-pytorch-onnx-cpu-benchmark-summary.json), [90-cell CSV](../results/tables/final/task0025-pytorch-onnx-cpu-benchmark-cells.csv). No numerical arrays were reopened for final metadata/statistic verification.

### 13.1 Required benchmark design

- Declare model-only and end-to-end timing boundaries separately.
- Measure batch-1 latency and a preregistered batch sweep for throughput.
- Include warm-up, independent repeats, and latency distribution statistics such as p50/p95/p99.
- Synchronize asynchronous device execution around timed regions; do not measure dispatch alone.
- Separate raw I/O/decompression, view construction, transfers, forward, canonical score calculation, and threshold decision.
- Preload appropriate tensors for model-only timing.
- Record device/core configuration, OS/runtime/library versions, threads, precision, batch, power mode, concurrent load, and thermal conditions where observable.
- Report memory with scope and method; lifetime RSS after verification is not isolated model memory.
- Establish numerical/decision equivalence tolerances before interpreting runtime variants.
- Use synthetic/dev/allowed-background inputs during development; hardware timing does not require test unblinding.

GPU execution is not presumed faster for a tiny AE. Small-model overhead, batch size, synchronization, and memory traffic may dominate. That is a measurement question.

### 13.2 Apple Silicon, ONNX, and CoreML

Task0022 completes the independent CPU reference; Task0023 implements the device foundation but its sole check is unavailable and no physical device policy proof exists. Task0024subsequently supplies accepted ONNX CPU structural/numerical equivalence; Task0025 now supplies complete raw paired CPU timing/numerical coverage with failed ORT3 process-exit supervision, so no accepted performance advantage. Scientific closure can advance independently to bounded native PCA/AE evaluation with explicit new test authorization. Later MPS/CoreML remains conditional on explicit new authorization/proof. Verify actual operator support, shape policy, execution provider/compute units, and fallback. A configured accelerator provider is not proof that the entire graph executes there.

Preserve preprocessing, score orientation, and decision semantics. Export parity must cover reconstruction, each model's canonical score, and threshold decisions on controlled inputs. Unsupported operations or numerical changes require documented decisions, not silent retraining or altered scoring.

### 13.3 Quantization and reduced precision

Distinguish FP16 computation from integer quantization, weights-only from activation quantization, and numerical compression from measured speed/memory benefit. Fit any learned quantization ranges using training background under a recorded policy. Track variant identity, background score/acceptance changes, and calibration provenance.

If an optimized representation changes numerical scores materially, define/freeze the permitted variant calibration before final unblinding. Do not refit thresholds on test. Quantization is useful only when its measured tradeoff justifies it; preserving FP32 is an acceptable conclusion.

### 13.4 NVIDIA/TensorRT and FPGA/hls4ml

NVIDIA work uses separate supported hardware/runtime and records engine/device/compiler versions and numerical equivalence. Transfer-inclusive and forward-only scopes remain distinct.

FPGA is optional. Begin with a compatible compact model, explicit fixed-point policy, synthesis/resource analysis, and recorded toolchain assumptions. Report LUT/FF/DSP/BRAM, latency, and initiation interval where available. Without a board test, distinguish synthesis estimates from measured deployment performance. Toolchain/hardware availability must not block the core scientific report indefinitely.

### 13.5 Trigger-like simulator

The simulator should model explicitly chosen arrivals, service time, batching/queue policy, acceptance thresholds, capacity, drops, and total latency. Scenarios must be repeatable and state whether service times are measured or assumed. Dataset row order is not physical event timing; dataset signal prevalence is not an arrival-rate estimate.

Simulator design/load tests can use synthetic and allowed-background events. Any real held-out signal efficiency belongs to final frozen evaluation. No claim of a real trigger rate or deadline follows from a synthetic stream.

## 14. Reproducibility and artifact governance

### 14.1 Required provenance

Each scientific experiment must identify:

- Source DOI/version/file size/checksums and integrity result.
- Frozen population protocol, membership/split identity, scope, and counts.
- Preprocessing configuration and feature order/dtypes.
- Model configuration, architecture, selected state, score definition, and artifact identity.
- Calibration inputs, thresholds, decision convention, and result identities.
- Software/hardware environment, seed/RNG/shuffle/determinism/thread settings.
- Actual/base code commit and dirty-source hashes where applicable.
- Output shapes, dtypes, sizes, and checksums.
- Population-access audit and any test exposure.

Keep timestamps, host/output paths, chunk size, elapsed time, and resource observations separate from scientific content identity where the established scheme does so.

### 14.2 Frozen identity registry

| Identity | SHA-256 |
| --- | --- |
| Raw source bytes | `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6` |
| Preprocessing configuration file bytes | `2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68` |
| Split scientific identity | `74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea` |
| Processed full scientific identity | `d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2` |
| Processed dev scientific identity | `2eb34e5b811c12ae5c47afba1ecdb6322feb7c7774b6c9ec5331abe78b3c9a2a` |
| PCA model scientific identity | `d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f` |
| PCA results scientific identity | `285a254847424870b5bee08e5a218733dcbe553ff7a4d00ec5c9493288600ccb` |
| AE v1 model scientific identity | `30dadcdc20fa788d5442e031f44694346d2ac152c9b647b77e17351558a1610e` |
| AE v1 results scientific identity | `490f8cf757ea2f2ab46dc7cee58c8d1b5b40b29cb06b799df7d8361987c222cd` |
| AE v2 model scientific identity | `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b` |
| AE v2 results scientific identity | `324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33` |

Model/results scientific hashes are computed from canonical JSON of the scientific section using the established implementation; they are not necessarily hashes of the complete file bytes. The preprocessing identity above is a **file-byte** hash. Do not interchange these definitions. Hashes provide integrity identities, not authenticated signatures.

### 14.3 Reproduction claims and storage policy

Independent local repetitions established exact scientific outputs for EDA/splits, dev preprocessing, PCA, AE v1, and AE v2. This does not guarantee bitwise identity on another operating system, BLAS implementation, PyTorch version, or device. Validate a new environment explicitly, using justified preregistered tolerances where exact identity is unavailable. Investigate unexplained mismatches.

Keep raw/processed data, split/label arrays, large outputs, logs, caches, environments, score arrays, checkpoints, and export artifacts ignored unless an explicit curation policy allows a specific small output. The tracked tiny AE JSON exceptions are exact-path exceptions, not a general permission to commit models.

Verify before accepting existing stores. Use staging/verification/finalization to prevent interrupted outputs from appearing complete. Rebuild/replacement must be explicit. Preserve historical model artifacts and task records.

## 15. Decision register: choices and rationale

This register captures enduring project reasoning. Add or supersede decisions here when a task changes the direction; leave implementation chronology in handoffs.

| Decision | Rationale | Status / reconsideration rule |
| --- | --- | --- |
| Start with corrected LHCO R&D v5 | Public, manageable, labeled particle benchmark supports shared model inputs and a clean held-out study | Frozen for the initial benchmark; new sources need a new contract |
| Pure-background training and validation | Isolate unsupervised behavior and prevent signal-based selection | Frozen; contamination/supervised studies are separate experiments |
| Separate selection and calibration backgrounds | Prevent thresholds from influencing model selection and avoid conflating development roles | Frozen |
| Exact-content grouping before splitting | Row-disjoint splits alone do not prevent duplicate leakage | Frozen; fuzzy deduplication is not implemented |
| Keep all physical particles in ragged storage | Preserve interpretability and future views without raw rereads or permanent truncation | Frozen schema 1 |
| Use log1p pT, standardized eta, periodic phi | Handle long positive pT tails, signed nonperiodic eta, and angular continuity | Frozen training-derived contract |
| FP32 physical/model representation | Local source precision supports it; compatible with compact deployment work | Frozen; new precision studies are separate variants |
| Deterministic pT ordering and `Nmax=384` | A reproducible retained prefix meeting declared event/pT retention criteria | Frozen default; alternatives require controlled evidence |
| Begin PCA and AE on the same eight aggregates | Establish simple baselines before adding particle information | Implemented; compression differs, so nonlinearity is not isolated |
| Compact 155-parameter AE | Keep a transparent, practical first neural model without aggressive search | Implemented; no automatic architecture expansion |
| Canonical CPU training, separate MPS smoke | Strengthen local determinism and separate model evidence from device compatibility | Implemented; future inference is measured independently |
| Close convergence before richer models | V1's endpoint was an arbitrary epoch cap | Resolved by unchanged-rule Task 0008; v2 canonical |
| Add particle/set information with local bottleneck and pooled context | Complete equivariant correspondence avoids matching while limiting each local path; 478 parameters and linear forward/score | Design/code retained; dev throughput failed, local canonical execution deferred byTask0019; convergence/usefulness unresolved |
| Bound resource recovery without resetting history | Stable read-only samples precede exclusive phases; actual workers recheck memory and preserve failures | External Task0013 slot fully consumed;96steps completed, memory pass/throughput fail, old records intact |
| Keep supervisor stdlib-only | Duplicate parent framework imports are measurable overhead; move scientific checks into fresh guarded workers | Own-parent peakRSS reduced319.391MiB versus legacy shape; Task0013 initial availability failed, later external memory passed; no causal claim about historical availability |
| Preserve observation semantics when reducing overhead | Direct Mach cache age is unexposed; retain exact system snapshots and cache bindings only | V3 component improvement tested; no synthetic workload speedup, no real authorization or numerical relaxation |
| Review engineering launch admission separately |4GiB continuing floor+512MiB headroom gives provisional4.5GiB launch; source/reader evidence and margin must precede dev activation | Historical Task0012 failed; external Task0013 activated v2 for bounded dev only. Task0018 supersedes short-dev host admission through separate process policy; full-run scope not granted, v1 failures preserved |
| Shared-host development process envelope | Fixed global reserve repeatedly blocked small dev during ordinary Mac use; observed367.25MiB RSS/179.672MiB startup native supports tight512/256MiB caps instead | Task0018 explicitly reviewed/implemented/measured: WARN advisory, CRITICAL veto, unknown disclosed; optional host context/no floor. Dev only, full-store/canonical policy separate |
| Defer local canonical particle execution and advance frozen CPU hardware work | Current240.728s fails180s and projects13.3738h/200cycles/run versus10h; two runs plus postfit28.7476h versus22h. Full custody is not long-run training and192steps are consumed | Adopted Task0019 engineering/scheduling decision under unchanged contracts; design/code retained, convergence/usefulness unresolved. Next Task0020 frozen PCA/AE v2 CPU benchmark; future particle policy/environment needs separate explicit authorization, no idle Mac/readiness dependency |
| Reject pooled event-only Chamfer AE initially | Strict event compression needs output generation and costly matching; Chamfer can miss duplicate frequencies | Reconsider if fixed event-only compression becomes a concrete requirement under a new correspondence/resource contract |
| Reject compact attention initially | One-head candidate costs about 15.8× selected MAC and quadratic activations without demonstrated interaction need | Reconsider only through a new design decision justified by a specific interaction limitation |
| Calibrate on BG and hold out test until candidate freeze | Protect an interpretable final scientific comparison | Frozen |
| Adopt arithmetic-aware CPUv2 prospectively | Original FP32 output-relative gate failed complete-grid reconstruction/SSE; derive/test rounding of both FP32/FP64 paths and outward score bounds rather than fit slack | Explicit Task0022prompt authorizes new supported CPU engineering gate; local/finite/exact repeat/reference/strict sampled decisions independent, all90new cells accepted; historical v1/source/science unchanged, not a universal device certificate |
| Preserve blocked device proof and distinguish software repair | Task0023check observes built=True/available=False and a raw-vs-JSON build digest defect; same actual build text | Failed receipt/source/acceptance preserved, software-only fix/1033tests, no repeat or current physical proof/real slot; independent CPU export foundation next |
| Accept derived ONNX CPU artifact only after full equivalence | Export is a runtime representation, not a new scientific fit; CPU provider/FP32 alone do not prove parity | Task0024audits6standard nodes/all155parameters, four fixed synthetic families and1193real windows, own/local/outward/strict-decision/restored hashes; no performance benefit claimed |
| Require lifecycle acceptance as well as numerical timing | Smaller files or completed local receipts do not establish an accepted runtime advantage | Task0022 CPU v2 accepted; Task0025 paired raw timings complete but ORT3 exit deadline vetoes campaign acceptance. MPS blocked; CoreML/quantization planned |
| Stop hardware interpretation on numerical failure | Frozen AE batch1 reconstruction exceeds fixed tolerance, though local caps and synthetic acceptance pass | Task0020 consumed/partial and Task0021diagnostic preserved. Explicit Task0022prospective v2 derives/tests outward rounding gates and completes new independent CPU measurements with zero sampled frozen decisions; no retrospective v1pass or device certificate |
| Use selective, user-executed Git delivery | Keep scientific work reviewable and protect unrelated/local artifacts | Standing workflow requirement |

## 16. Roadmap, milestones, and next-task definitions

The roadmap is dependency-driven. Dates, speedups, and physical trigger budgets are not promised. Future task numbers beyond the next task are provisional and must be reconciled with the live task index.

### 16.1 Milestones

| Milestone | Deliverable and exit criterion | Current status |
| --- | --- | --- |
| Data foundation and aggregate baselines | Verified source/store/config, disjoint populations, reproducible PCA/AE | Completed, Tasks 0001-0007 |
| AE convergence closure | Exact v1 prefix; fixed-rule endpoint; documented canonical supersession | Completed, Task 0008 |
| Particle/set-aware baseline | Justified compact design, correct mask/permutation/loss/score semantics, background-only training/calibration | Design/code retained;749.343s/240.728s target failures and192consumed; local canonical execution deferred by Task0019, convergence/usefulness unresolved |
| Apple Silicon inference | Repeatable CPU/MPS batch-1 and throughput study, timing/memory scopes and hardware manifest | Task0022complete accepted CPUv2; Task0023foundation software validated, one unavailable check, no actual paired data/device proof |
| ONNX CPU | Export/operator/provider audit and numerical/decision parity | Task0024 accepted; Task0025 complete descriptive paired timings but failed exit supervision/no accepted performance comparison |
| CoreML | Export/operator/compute-unit audit and numerical/decision parity | Planned, separate optional branch |
| Precision reduction / quantization | Training-only calibration; measured cost benefit and background stability within declared policy | Planned |
| Trigger simulator | Repeatable arrival/service/queue/acceptance/drop/latency scenarios with explicit assumptions | Planned |
| NVIDIA / TensorRT | Comparable workload on documented supported hardware, engine provenance and transfer-aware timing | Conditional |
| FPGA / hls4ml | Compatible fixed-point model and synthesis/resource/latency evidence; board measurements if available | Optional |
| Final test unblinding | Explicit human-authorized frozen plan and thresholds; audited real metrics | Completed/accepted Task0026 Phase B; both tests exposed,4requests/500942presentations, frozen candidates/thresholds unchanged, no retry or post-test tuning |
| Initial final reporting | Frozen native quality/cost comparison, scoped uncertainty, reproducibility, limitations and conclusions | Completed Task0027/0032; Task0033 adds exploratory descriptions; Task0034 defines a conditional follow-up; Task0035 validates its synthetic software, independent confirmation remains unresolved |

NVIDIA and FPGA branches need not block the main report if resources are unavailable. Report unexecuted branches honestly. Final unblinding must not occur merely because another milestone completes.

### 16.2 Completed initial synthesis and accepted three-prong extension

**Task0027 — Frozen scientific synthesis and quality/cost frontier is complete.** [Report](scientific-synthesis.md), summary/two CSVs/two static figures integrate accepted Task0026 science and Task0022 costs. No new population/scoring/custody/optimizer/model/threshold/candidate selection, export or hardware work. All original eight operating points and ten adapter cost groups remain; a two-candidate sampled tradeoff is not a universal continuous Pareto frontier. Other branches do not block completion of this initial report.

Task0027 proposed an independent-population protocol. The subsequent explicit Task0028 request selects a narrower question: new three-prong signal with the accepted exposed Task0026 background scores. Phase A metadata research, isolated compatibility/custody/overlap/scoring orchestration and1333full/portable software validation are now complete. The source-bound plan `77f92d951b034575299ed81d6cf61d19d49430b41b954d03b5d3ec62b1179fa9` received actual explicit human approval. Its sole reserved Phase B acquisition failed at the frozen298s operation deadline; campaign failed/consumed, no retry/resume. The approval covered the pinned235488994-byte signal, integrity-only raw/all-role fingerprints, frozen preparation, one evaluation per candidate and two cached-background numeric reuses, conditional on all gates. Partial raw transfer occurred but no acquisition-integrity acceptance, raw numerical custody, preparation, model access or cached numeric reuse. All dependent phases stopped. Task0029 then implemented separately authorized durable transport but failed/consumed; Task0030 now completes a separately authorized sleep-aware copied-prefix acquisition with full byte acceptance and compatible-looking structural metadata. At Task0030 completion, numerical custody/uniqueness/overlap/scoring remained unstarted. The explicitly authorized Task0031 now completes that separate local-file protocol/campaign, with100000valid/unique/disjoint rows, all4stages accepted and both frozen candidates evaluated once. Original science and all consumed failures remain; background is shared historical evidence, not a new independent measurement.

This is **signal-topology generalization with a reused exposed background reference**, not a fully independent benchmark or BG domain-shift test. Candidate/transform/calibration identities and original training provenance remain separate from new signal identity. Both original tests remain exposed permanently; future design informed by results still requires an explicit methodological decision and independent evaluation protocol/population. No test-guided fitting, recalibration or candidate/threshold selection is authorized.

Task0026 final evaluation is accepted and consumed after actual explicit approval of the unchanged plan `2c97dc2ac903de4a911968bc2f97725cd3d80e18498b1003604c9e4562e3d86f`. Phase A commit `e69d80ed802492be3db965d0ab69ce3e1a50395d` verified, frozen130source/dependency bytes and1259full/portable acceptance reused; no source repair/retest/readiness replay. Native PCA then AE each150471test-background/100000test-signal,37/25complete batches at4096,4total requests/124score batches/500942presentations/250471unique events, no unknown inflight. All3processes exit0/reaped/parent-accepted in31.094950s; terminal memory gaps disclosed, no continuous/hard-real-time guarantee. Custody2candidate constructors is mandated by the approved plan and distinct from the original1PhaseAreadiness operation.

Scientific result: evaluated test mixture39.924782%signal; PCA AUC0.468489/AP0.364379 below0.5/prevalence under supplied high-SSE orientation, never flipped; AE0.660064/0.547427, modest ranking/higher sampled calibrated TPR but poor tight-tail sensitivity. At target1e-3, PCA2signal/124background versus AE56/116; conditional Wilson intervals and all original thresholds preserved. Descriptive empirical ROC thresholds are not adopted deployment thresholds. Six PCA versus three AE latent dimensions is not capacity-controlled nonlinearity, and native historical CPU B1adapter medians8.125/24.708µs have their own scope. No causal/universal superiority or physical-trigger claim.

**Both tests are exposed; they cannot be described as untouched again.** No test-guided retraining/recalibration/candidate selection was performed or authorized. A new model-development question requires explicit methodological approval and a new evaluation protocol/population; no automatic resume/replay. Particle192/192/local canonical deferral and original180s/10h/22h/max200/patience20/min_delta0 remain. Task0025failed/consumed/provisional ratios/unknown shutdown remain; optional ORT/MPS/CoreML/quantization/simulation are independent later work.

### 16.3 Proposed tasks after design

- **Particle/set future reconsideration:** Local canonical execution deferred by Task0019. Retain design/code; a future full-store/time/environment policy requires separate precise authorization/implementation, with consumed192steps unchanged. It does not block current hardware work.
- **Task0023 CPU/MPS foundation:** Implemented/1033tests, one unavailable check/old failed receipt preserved, software digest fix without replay. No physical device proof/real slot; future device study requires separate explicit authorization.
- **Task0024 ONNX CPU foundation:** Complete accepted derived export/1111tests/four synthetic families and all1193real windows; one read/0performance timing, slot consumed.
- **Task0025 paired CPU benchmark:** Implemented/1179 tests, all 90 cells and numerical gates measured; failed ORT3 exit deadline, consumed, descriptive comparisons only. No replay permission.
- **Task0026 guarded native scientific comparison:** Authorized Phase B completes/accepted/consumed, all counts/scientific outputs curated; both tests exposed, no post-test tuning/replay.
- **Task0027 frozen scientific synthesis/frontier:** Completed initial integrated report, ten accepted adapter groups/eight frozen operating points/two figures; zero new scientific execution.
- **Task0028 three-prong extension:** Phase A software accepted; sole approved Phase B failed/consumed at acquisition deadline, scientific extension unmeasured. Separate Task0029 acquisition-v2 software accepted, real3request session failed/consumed with29990748Bunverified prefix retained; no HDF/numerical/model/cache/scientific work. Its clock/200-206Retry-After limitations are historical. Separately authorized Task0030v3 now accepts full235488994B through one206 and confirmed assertion release; structure-only FP64[100000,2101], zero numerical/model work. Task0031 subsequently accepts the separately authorized local-file scientific campaign: PCA AUC0.462953/AP0.360220, AE0.585877/0.479972,2requests/50batches/200000presentations,all100000valid/unique/disjoint. Shared BG,no new BGforward/optimizer; strict AE34/116not enriched. No automatic successor.
- **CoreML export/equivalence:** Planned optional branch; ONNX CPU export/equivalence already accepted in Task0024. No automatic new export or performance task.
- **Reduced-precision study:** Compare supported precision variants using training-only calibration and preregistered tolerances; freeze variant thresholds before final test.
- **Streaming study:** Establish repeatable simulator assumptions and load scenarios, then evaluate queueing/capacity/latency and acceptance.
- **Conditional deployment branches:** NVIDIA/TensorRT and optional FPGA/hls4ml as resources permit.
- **Integrated scientific reporting / controlled follow-up:** Task0032 closes the frozen baseline; Task0033 exploratory/Task0034 design-only/Task0035 synthetic foundation remain. Task0036route stays `unresolved_no_acquisition`, unchanged/unaccepted. Explicitly chosen Task0037engineering branch completes a model-free fixed synthetic FIFO trigger study with scoped historical constant costs,105targeted/2022full+portable and final bounded native/3figures. No deployment winner, scientific confirmation or physical inference claim. Task0038 separately measures prepared natural/padded service with one parent-accepted204cell session and fresh100focused/2122full+portable acceptance. Task0039 resolves exact membership and preserves its metadata-only design; separate Task0040now measures selected-development read/features/direct joint with exact golden parity,100focused/2310full+portable and one accepted36cell session. Next bounded joint preprocessing+original CPU-adapter design requires separate authorization; acquisition/training/confirmation remain ungranted and no automaticTask0041. Exposure/result-informed origin, failures/particle192 preserved.

Do not treat these bullets as already executed tasks or fixed task numbers. Choose the next bounded task from the live state, dependency order, unresolved evidence, and user direction.

## 17. Observations, risks, and open questions

### 17.1 Observations that should influence future work

- The data foundation is already substantial. Rebuilding or refitting it without cause adds risk rather than progress.
- Background split score differences are small for current baselines, but finite tails remain statistically limited.
- V2 improved permitted selection reconstruction loss by about 3.65%, resolving the cap concern under the fixed stopping rule. This does not establish anomaly improvement versus historical v1; accepted Task0026/0027 compares v2 with PCA only.
- V2's maximum training SSE increased while mean/most quantiles decreased. Per-event error need not improve monotonically; do not clip inconvenient tails.
- PCA's lower residual and AE's smaller latent dimension reflect different retained capacity. Avoid a premature narrative of neural superiority or failure.
- A tiny AE can be dominated by runtime overhead. Task0022measures CPUadapter B1PCA8.125µs/AE24.708µs median of worker medians; these frozen pipelines differ in capacity/score scale and cannot rank scientific quality. Accelerator speedup remains unmeasured; current MPSavailability false.
- Particle structure has exact synthetic and same-sample real numerical parity; short-dev memory now passes under a reviewed shared-host envelope.240.728s projection still fails180s, full-store feasibility and canonical convergence remain prerequisites to scientific comparisons. No model/device change follows from these engineering observations.
- An externally readable memory must preserve both general intent and current specifics. Handoffs alone are insufficient for strategic continuity, while this memory alone is insufficient for exact implementation auditing.

### 17.2 Main risks and controls

| Risk | Required control |
| --- | --- |
| Leakage or accidental test access | Guarded readers, explicit scope, access audits, separate unblinding task |
| Reconstruction treated as detection quality | Separate development loss from final signal metrics |
| Background score sculpting | Acceptance/score diagnostics against event scale, mass proxy, multiplicity, and truncation |
| Finite tail statistics | Counts, resolution, intervals; no unsupported extreme-rejection extrapolation |
| Mask/cardinality/ordering mistakes | Hand-computable synthetic cases, permutation/padding tests, explicit score semantics |
| Unjustified richer architectures | Compact baseline first; preregistered scope and resource rationale |
| Export or quantization drift | Variant provenance and preregistered numerical/decision checks; no test recalibration |
| Misleading hardware comparisons | Synchronization, warm-up/repeats, matched workloads, actual provider and timing boundaries |
| Platform/version drift | Exact environment records and explicit reproduction/parity checks |
| Storage/RAM pressure | Chunking/mmap, output estimates, free-space checks, deliberate rebuild policy |
| Narrow simulation interpretation | State preselection, no pileup/MPI, limited topology, and detector/physics limits |
| Task scope expansion | One bounded question/deliverable; explicit new decisions when gates fail |
| Stale project memory | Update this file with every relevant task; verify live state at session start |

### 17.3 Open scientific and engineering questions

- Initial native result is established: AE has moderate ranking/higher signal acceptance than PCA at all four frozen points, with weak strict-tail utility and no observed strict-slice enrichment. Task0033 measures exploratory feature/score associations and distinct tail profiles; causal feature bias, generalization and capacity controls remain open. Correlations cannot select a favorable feature or establish a mechanism; these are not missing prerequisites to completed reporting.
- How much particle-level information is necessary for a meaningful quality/cost improvement?
- The initial set objective is now fixed: corresponding-particle weighted mean, avoiding matching costs. Will its local capacity, rare-particle dilution, count blindness or limited mean context undermine discrimination? Unknown until the appropriate frozen evaluation.
- Why did free+inactive availability fall from Task0011 post-reboot4.6248–4.6819GiB to Task0012 provisional2.5443–2.6967GiB? Task0013 now measures duplicate-supervisor overhead and a smaller light parent, but cannot causally explain that historical change. Light worker availability3.1778–3.2442GiB still fails; pressure/current swap restricted. The later external study passed memory and consumed96steps but failed throughput; no original budget remains. Task0016 automatic3.558GiB and manualWARN2/unmeasured availability remain separate; Task0017 check-only3.705841GiB fails floor. Repeated explicit checks now record current conditions, historical/synthetic probes are not stable readiness.
- Can a future explicitly revised resource/time/environment policy justify canonical particle work? Task0019 defers local execution under current contracts:240.728s>180s and200cycles13.3738h/run exceed10h, full custody does not validate sustained training, and no dev allowance remains. Exact long-run pressure/allocator/scale behavior and postfit costs are unknown; particle convergence/usefulness remain unresolved. No new measurement is granted to fill these gaps.
- How well do completeCPUv2costs generalize across hosts/load, and can supported MPS improve the frozen AE? Task0022provides all90CPUcells/3repetitions but fixed sample/order/200calltails and shared-host outliers limit inference. Current MPSavailability false and device arithmetic unvalidated; no device speedup or trigger deadline claim.
- Do ONNX/CoreML provide a useful benefit for these model sizes and shapes?
- What precision changes preserve decisions and improve measured cost?
- Which streaming arrival/service assumptions are informative without pretending to reproduce detector operation?
- Will NVIDIA/FPGA access be available, and which deployment branch is worth its engineering cost?
- How robust are conclusions to different signals, simulation shifts, pileup, or real-data selections? These require later protocols, not extrapolation from the current benchmark.

Task0012's provisional failed pilot and Task0013's initial pending accounting remain historical evidence. Task0013 later activated v2 for bounded dev only and consumed the original96steps, with no inflight; real throughput failed, canonical convergence not tested. Task0014 reconciles this distinction, records shared-Mac preference, validates v3/471tests and one11.199s synthetic matrix; no new real access/steps/full-run authorization. Direct Mach freshness is unresolved for enforcement and is rejected; exact system collection remains supported. Task0015 v4 establishes bounded synthetic2.14×gain under explicitly changed observations, below3×; final532tests pass, no additional real allowance unlocked or readiness attempted. Task0016 explicitly replaces synthetic admission only for one diagnostic, adopts unchanged v4/limits with576tests, and stops at first3.558GiB read-only readiness guard. No new real slot/data/steps. Its later manualWARN fails without admitted availability. Task0017 reconciles both and implements repeatable explicit checks/separate fresh-check run with612tests and one floor-failed integration; no real action/slot/additional budget. Canonical particle model, full scientific/background calibration and signal usefulness remain pending; no trained particle artifact/hash or final performance result exists.

Task0018 resolves the short-dev global-reserve blocker through an explicit process policy and completes96additional updates under normal shared use; cumulative192/192 and canonical anchor consumed. Task0019 consolidates full-store/time feasibility into present local canonical deferral, with no more readiness window or new permission. Exact same-sample numerical parity is established;240.728s target failure persists and source-frozen evidence is preserved. Task0020 now delivers the guarded CPU foundation/partial PCA1data; Task0021diagnostic is preserved; Task0022now validates an explicitly authorized arithmetic-aware contract and completes the new CPU campaign. Task0023foundation is implemented; sole device check unavailable, no paired data; Task0024CPU export/equivalence now accepted; Task0025 paired CPU timings/numerics are complete but ORT3 exit deadline prevents acceptance; Task0026 readiness and explicitly authorized final scientific comparison are now accepted; both tests exposed/final slot consumed; Task0027 integrated scientific synthesis is complete. Task0028 Phase A subsequently implements the separately authorized three-prong/shared-exposed-BG extension; the explicitly human-approved sole Phase B acquisition failed at its frozen deadline and is consumed, with no new scientific results or dependent work. Separate Task0029 acquisition failed/consumed, then Task0030 accepted complete local bytes and Task0031 accepted the separate local numerical/scientific campaign. All100000events are valid/unique/disjoint and model-exposed; shared background is historical evidence, strict AE34signal/116BG is not enriched. No consumed session is retried or resumed. Future particle reconsideration remains separate.

## 18. Development workflow and mandatory Git delivery

The existing task system remains authoritative: [development.md](development.md), [prompts/](prompts/), and [handoffs/README.md](handoffs/README.md).

Every operational task must inspect instructions and repository state, preserve unrelated work, save its specification, implement/research within scope, run relevant validation, document factual outcomes, update its handoff/index, and review the diff.

**Updating this memory is an additional project-level responsibility.** It does not replace a handoff, require inventing another handoff for the memory itself, or turn the memory into an append-only dump of task summaries. Include its relevant update in the same reviewed task change.

### Mandatory clause for every future Codex task prompt

> Read `docs/project-memory.md` before planning the task. Update it before completion wherever this task changes canonical state, project understanding, decisions/rationale, roadmap, risks, open questions, or the recommended next step. Preserve the distinction between implemented evidence and future proposals. Keep detailed execution records in the existing task handoff. At the end, provide exact Git commands for status/diff, selective staging of the intended task files, staged review and whitespace checking, a suitable Conventional Commit, and push for the actual branch/upstream. Do not automatically stage, commit, or push; leave those actions to the user unless explicitly instructed otherwise.

The final Git delivery must replace placeholders with the actual reviewed task file list, commit message, and branch/upstream. Its structure is:

```bash
git status --short --branch
git diff
git add <explicit intended task files, including project-memory.md if changed>
git diff --cached
git diff --cached --check
git commit -m "<appropriate Conventional Commit message>"
git push
```

For a branch without upstream, provide the appropriate explicit push command. Do not invent a resulting commit hash. Avoid broad staging that includes unrelated work or ignored scientific artifacts. Do not claim checks that were not run.

## 19. How to maintain this living memory

### 19.1 Update responsibility

Codex should maintain this file during every relevant task, using the verified outcome. The file's presence does not itself guarantee that every tool/session discovers it: future task prompts must include the mandatory read/update clause above, and a repository entry-point instruction or documentation link should direct sessions here when the user installs it.

An editorial memory update does not consume the next implementation task number or imply that the next planned model task is complete.

For automatic discovery in repository-based Codex sessions, add the following clause to the repository's existing root `AGENTS.md` (or create that entry point if the user chooses to install it). Preserve any existing repository instructions:

```markdown
## LatentTrigger project memory

Read docs/project-memory.md at the start of every task. Verify its current-state
claims against the relevant repository files before implementation. Treat it as
the maintained project-wide explanation of objectives, scientific contracts,
architecture, decisions/rationale, roadmap, risks, and next steps.

Before completing a task, update the affected parts of docs/project-memory.md
with verified durable outcomes and current canonical state. Keep detailed task
chronology in the existing handoff system; do not turn the memory into a second
handoff log. Follow its maintenance rules and preserve the test embargo. Always
provide concrete final manual Git commands; do not automatically stage, commit,
or push unless the user explicitly instructs otherwise.
```

This clause routes sessions to the memory; it does not supersede current user instructions or automatically authorize scientific protocol changes. A README link can aid human discovery but is not a substitute for an instruction to read and maintain the file.

### 19.2 Update procedure at task completion

1. Reconcile actual outcomes with the task specification and evidence. Separate completed, partially completed, failed, and deferred work.
2. Update document control and the start-here state: verified date/base/HEAD, latest completed task, canonical artifacts, embargo/exposure, and next recommended task.
3. Update affected objectives, architecture, measured results, milestone status, and next-task definitions in place.
4. Add or explicitly supersede enduring decisions with rationale, evidence, and the condition under which they could be reconsidered.
5. Resolve or revise open questions and risks. Preserve material limitations even when a result is positive.
6. Update the identity registry only from verified artifacts. Clearly distinguish scientific hashes from file-byte hashes.
7. Add a short revision-history entry and links to detailed reports/handoffs. Do not paste raw logs, all changed files, per-epoch histories, or per-event arrays here.
8. Check internal/relative links, numerical consistency, status terminology, and alignment with the handoff/index. Include the changed memory file in the task's proposed selective Git commands.

If a task leaves project-level state and understanding unchanged, record that the memory was reviewed and required no factual update in the task handoff/final result; avoid meaningless churn. If a task exposes test data, update exposure immediately, including failed or interrupted runs, rather than waiting for a successful completion.

### 19.3 Avoiding stale facts and duplicated sources of truth

- Configurations and artifacts remain the exact machine-readable sources; this file explains their purpose and records key identities/results.
- Handoffs remain historical evidence, not rewritten accounts of later state.
- Keep historical model generations when canonical state changes; explicitly record supersession.
- Replace outdated current-state text rather than leave conflicting assertions in different sections.
- Mark proposals as proposals and unmeasured performance as unmeasured.
- Do not invent dates, counts, hashes, commits, hardware availability, or results.
- If sources conflict, verify them and document the resolution. For example, a task-time handoff can say "awaiting commit" while later Git history establishes that the user subsequently committed it.
- If a planning chat has only this file and no repository access, it must treat current state as the document's verified snapshot and ask for missing evidence only when needed for the next decision.

### 19.4 What to send to a new Work planning chat

This file should be sufficient to explain the project and request a focused next Codex prompt. Send the latest version, state any new user priorities/constraints, and include the latest handoff or narrow configuration/report only when the next prompt needs implementation details absent here.

The planning chat should derive the next task from objectives, dependency order, verified state, unresolved questions, and scope boundaries. It must not issue another completed task, infer that a proposal was implemented, or turn hardware work into implicit test unblinding.

## 20. Instructions to future ChatGPT/Codex sessions

### 20.1 Binding operating rules

1. Read this memory, then verify current repository instructions/state and the relevant exact contracts before implementation.
2. Preserve pure-background development and permanent existing YES/YES exposure. This memory does not authorize new access or reblinding; future test-informed design needs explicit methodology and independent evaluation protocol/population.
3. Reuse frozen source, split membership, feature semantics/order, scalers, FP32 representation, ordering, `Nmax=384`, and mask/padding policy unless a new explicit versioned decision changes them.
4. Fit using training background; select using selection background; calibrate thresholds after restoration/freeze on calibration background. Never use signal/test performance to choose those quantities.
5. Treat compact AE v2 as canonical at this snapshot. Preserve v1 and PCA; do not silently overwrite history.
6. Distinguish reconstruction/generalization evidence from anomaly-discrimination evidence, compatibility from performance, local exact repeats from cross-platform guarantees, and measured runtime from hypothetical trigger capability.
7. Use one bounded, sequentially numbered task; keep existing prompt/handoff/index records and update this living memory as an additional responsibility.
8. Keep large/local artifacts out of Git. Preserve unrelated user work and read-only synced reference sources.
9. Report actual checks and limitations. Unknown remains unknown; pending checks remain pending. Follow [development.md](development.md#standing-delivery-preference): substantive final responses must be self-contained planning handoffs covering work/data/validation/limits/decision/next scope, with manual Git last.
10. Always provide concrete final manual Git commands. Do not stage, commit, or push automatically.
11. Treat any real model/evaluation test access as exposure. Preserve failed access records and update this memory immediately.
12. Do not assume a Transformer, a hardware speedup, or signal superiority. Let explicit questions and evidence determine the next step.

### 20.2 Initial checklist

- [ ] Locate the operational repository and distinguish it from any ChatGPT project mirror.
- [ ] Read applicable repository instructions and inspect Git status, branch/upstream, HEAD/base, and recent commits.
- [ ] Check this file's date and current state against the latest README/handoff/index and artifacts.
- [ ] Identify the next actual task number and whether the requested work is implementation, methodological design, measurement, or planning.
- [ ] Read [development.md](development.md), [evaluation-protocol.md](evaluation-protocol.md), [preprocessing-contract.md](preprocessing-contract.md), and relevant reports/configurations.
- [ ] Verify source/store/config/split/model provenance needed by the task; do not reflexively regenerate or refit frozen inputs.
- [ ] Confirm expected population counts and that the work plan avoids test model/evaluation access.
- [ ] Check resource and environment requirements before expensive runs.
- [ ] Define the task's bounded deliverable, acceptance criteria, and non-scope.
- [ ] Include the memory read/update and final manual Git clauses in a generated Codex prompt.

### 20.3 Reusable request for a new Work planning chat

```text
We are continuing LatentTrigger. Use the attached/current docs/project-memory.md
as the project-wide living memory. It is separate from task handoffs.

First identify the verified current state, completed work, frozen scientific
contracts, unresolved questions, and next dependency. If repository access is
available, reconcile the memory with current files; otherwise state that the
document is the latest provided snapshot and do not invent newer results.

Generate a concrete, bounded Codex prompt for the next appropriate task. Preserve
background-only development and the real test embargo. Require inspection of the
relevant exact contracts/configurations and existing prompt/handoff workflow.
Require an in-place update to docs/project-memory.md for project-level outcomes,
decisions/rationale, roadmap, risks, and the next step. Require final exact manual
Git review/staging/commit/push commands, with no automatic staging/commit/push.

Do not repeat a completed task or assume that a proposed model/runtime exists.
My current priority or requested task is: [state the new objective, if any].
```

### 20.4 Reusable start instruction for an implementation session

```text
Read docs/project-memory.md and the current repository instructions first.
Verify Git, the latest task index/handoff, exact relevant contracts/configurations,
canonical artifact identities, and test-embargo status before making changes.
Execute only the requested task within its stated scope. Update the living memory
with durable project outcomes and reasoning, while leaving execution chronology
in the task handoff. Report actual validation and provide concrete manual Git
commands. Do not automatically stage, commit, push, or unblind real test data.
```

## 21. References and memory revision history

### 21.1 Local sources of truth

- [Project overview](../README.md) and [package/dependency configuration](../pyproject.toml).
- [Development protocol](development.md) and [handoff index](handoffs/README.md).
- [Data design](data-design.md), [raw audit](raw-data-audit.md), [training EDA](training-data-eda.md).
- [Preprocessing contract](preprocessing-contract.md), [pipeline](preprocessing-pipeline.md), [frozen configuration](../configs/data/lhco_rnd_v5.json).
- [Evaluation protocol](evaluation-protocol.md).
- [Development raw-feature measurement](development-raw-feature-measurement.md), [Task0040 config](../configs/benchmarks/development_raw_measurement_v1.json), [summary](../results/tables/final/task0040-development-raw-feature-summary.json) and [handoff](handoffs/0040-development-raw-feature-measurement.md).
- [Development raw-feature design](development-raw-feature-benchmark-design.md), [Task0039 config](../configs/benchmarks/development_raw_features_v1.json), [summary](../results/tables/final/task0039-development-raw-feature-summary.json) and [handoff](handoffs/0039-development-raw-feature-foundation.md).
- [Prepared-batch service measurement](prepared-batch-service-measurement.md), [Task0038 config](../configs/benchmarks/prepared_batch_service_v1.json), [cells](../results/tables/final/task0038-prepared-batch-service-cells.csv), [summary](../results/tables/final/task0038-prepared-batch-service-summary.json) and [handoff](handoffs/0038-prepared-batch-service-measurement.md).
- [Synthetic trigger/queue simulator](synthetic-trigger-simulator.md), [Task0037 config](../configs/simulation/synthetic_trigger_v1.json), [scenario CSV](../results/tables/final/task0037-synthetic-trigger-scenarios.csv), [summary](../results/tables/final/task0037-synthetic-trigger-summary.json) and [handoff](handoffs/0037-synthetic-trigger-simulator.md).
- [Confirmation-source feasibility](confirmation-source-feasibility.md), [Task0036 evidence](../results/tables/final/task0036-confirmation-source-evidence.csv), [summary](../results/tables/final/task0036-confirmation-source-feasibility-summary.json) and [handoff](handoffs/0036-confirmation-source-feasibility.md).
- [Controlled activation synthetic foundation](controlled-activation-synthetic-foundation.md), [Task0035 config](../configs/research/controlled_activation_synthetic_v1.json), [summary](../results/tables/final/task0035-controlled-activation-synthetic-summary.json) and [handoff](handoffs/0035-controlled-activation-synthetic-foundation.md).
- [Controlled follow-up protocol](controlled-follow-up-protocol.md), [design-only sidecar](../configs/research/controlled_follow_up_v1.json), [Task0034 source registry](../results/tables/final/task0034-confirmation-source-registry.csv), [summary](../results/tables/final/task0034-controlled-follow-up-summary.json) and [handoff](handoffs/0034-controlled-follow-up-protocol.md).
- [Exploratory frozen-feature and score-tail diagnostics](exploratory-feature-score-diagnostics.md), [Task0033 summary](../results/tables/final/task0033-exploratory-feature-score-summary.json), [feature/score associations](../results/tables/final/task0033-feature-score-associations.csv) and [handoff](handoffs/0033-exploratory-feature-score-diagnostics.md).
- [Integrated two-/three-prong synthesis and decision brief](two-three-prong-synthesis.md), [Task0032 summary](../results/tables/final/task0032-two-three-prong-synthesis-summary.json), [calibrated utility](../results/tables/final/task0032-calibrated-utility.csv), [quality/cost](../results/tables/final/task0032-quality-cost.csv) and [handoff](handoffs/0032-two-three-prong-synthesis.md).
- [Integrated frozen scientific synthesis](scientific-synthesis.md), [Task0027 summary](../results/tables/final/task0027-frozen-scientific-synthesis-summary.json), [quality/cost CSV](../results/tables/final/task0027-quality-cost-frontier.csv) and [operating interpretation](../results/tables/final/task0027-operating-point-interpretation.csv).
- [Local three-prong scientific evaluation: accepted/consumed](local-three-prong-evaluation.md), [Task0031 summary](../results/tables/final/task0031-local-three-prong-evaluation-summary.json), [calibrated points](../results/tables/final/task0031-three-prong-calibrated-operating-points.csv), [topology comparison](../results/tables/final/task0031-two-vs-three-prong-comparison.csv), [figure](../results/figures/final/task0031-three-prong-roc-pr.png) and [handoff](handoffs/0031-local-three-prong-evaluation.md).
- [Acquisition v3: complete verified bytes, structure only](three-prong-acquisition-v3.md), [Task0030 summary](../results/tables/final/task0030-three-prong-acquisition-summary.json), [attempts](../results/tables/final/task0030-transport-attempts.csv), [protocol](../configs/acquisition/three_prong_v3.json) and [handoff](handoffs/0030-three-prong-acquisition-v3.md).
- [Acquisition v2: failed/consumed with retained partial](three-prong-acquisition-v2.md), [Task0029summary](../results/tables/final/task0029-three-prong-acquisition-summary.json), [attempts](../results/tables/final/task0029-transport-attempts.csv) and [handoff](handoffs/0029-three-prong-acquisition-v2.md).
- [Three-prong extension: Phase A accepted, Phase B failed/consumed](three-prong-generalization.md), [strict protocol](../configs/evaluation/frozen_three_prong_v1.json), [summary](../results/tables/final/task0028-three-prong-generalization-summary.json) and [handoff](handoffs/0028-three-prong-generalization.md).
- [PCA report](pca-baseline.md) and [configuration](../configs/models/pca_baseline.json).
- [Historical compact AE report](compact-autoencoder.md), [v1 configuration](../configs/models/compact_autoencoder.json), and [v1 artifact](../artifacts/models/compact-autoencoder-v1/model.json).
- [AE convergence report](autoencoder-convergence.md), [v2 configuration](../configs/models/compact_autoencoder_v2.json), and [v2 artifact](../artifacts/models/compact-autoencoder-v2/model.json).
- [Task 0006 scientific results](../results/tables/final/task0006-pca-background-results.json).
- [Task 0007 scientific results](../results/tables/final/task0007-autoencoder-results.json).
- [Task 0008 scientific results](../results/tables/final/task0008-autoencoder-convergence-summary.json).
- [Task 0008 handoff](handoffs/0008-autoencoder-convergence.md) for detailed closure evidence.
- [Particle/set design](particle-set-baseline-design.md), [design-only JSON](../configs/models/particle_set_baseline_design_v1.json), [analytic budget](../results/tables/final/task0009-particle-set-design-budget.csv) and [Task 0009 handoff](handoffs/0009-particle-set-baseline-design.md).
- [Particle/set implementation](particle-set-baseline.md), [executable JSON](../configs/models/compact_particle_set_autoencoder_v1.json), [gate/resource evidence](../results/tables/final/task0010-particle-set-gate-summary.json) and [Task 0010 handoff](handoffs/0010-particle-set-baseline.md).
- [Bounded resource recovery](particle-set-resource-recovery.md), [readiness summary](../results/tables/final/task0011-particle-set-recovery-summary.json) and [Task 0011 handoff](handoffs/0011-particle-set-resource-recovery.md).
- [Versioned memory-policy review](particle-memory-policy-review.md), [engineering profile](../configs/resources/particle_memory_policy_v2.json), [Task0012 evidence](../results/tables/final/task0012-particle-memory-policy-summary.json) and [handoff](handoffs/0012-particle-memory-policy-review.md).
- [Host diagnosis/lightweight supervision](particle-host-readiness.md), [Task0013 evidence](../results/tables/final/task0013-particle-host-readiness-summary.json) and [handoff](handoffs/0013-particle-host-readiness.md).
- [Manual reconciliation/monitor performance](particle-monitor-performance.md), [v3 implementation manifest](../configs/resources/particle_resource_monitor_v3.json), [Task0014 evidence](../results/tables/final/task0014-particle-monitor-performance-summary.json) and [handoff](handoffs/0014-particle-monitor-performance.md).

- [Shared-host development policy](particle-shared-host-policy.md), [strict sidecar](../configs/resources/particle_shared_host_dev_policy_v1.json), [Task0018 evidence](../results/tables/final/task0018-particle-shared-host-policy-summary.json) and [handoff](handoffs/0018-particle-shared-host-policy.md).
- [Canonical feasibility decision and Task0020 CPU brief](particle-canonical-feasibility.md), [Task0019 summary](../results/tables/final/task0019-particle-canonical-feasibility-summary.json) and [handoff](handoffs/0019-particle-canonical-feasibility.md).
- [Frozen CPU benchmark partial report](frozen-cpu-benchmark.md), [protocol](../configs/benchmarks/frozen_cpu_v1.json), [Task0020 summary](../results/tables/final/task0020-frozen-cpu-benchmark-summary.json), [cells](../results/tables/final/task0020-frozen-cpu-benchmark-cells.csv) and [handoff](handoffs/0020-frozen-cpu-benchmark.md).
- [AE batch-shape numerical review](ae-batch-parity-review.md), [review protocol](../configs/benchmarks/ae_batch_parity_review_v1.json), [Task0021 summary](../results/tables/final/task0021-ae-batch-parity-review-summary.json) and [handoff](handoffs/0021-ae-batch-parity-review.md).
- [CPU v2 complete benchmark](frozen-cpu-benchmark-v2.md), [frozen arithmetic derivation](arithmetic-cpu-v2-policy.md), [protocol](../configs/benchmarks/frozen_cpu_v2.json), [Task0022 summary](../results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json), [cell CSV](../results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv) and [handoff](handoffs/0022-frozen-cpu-benchmark-v2.md).
- [CPU/MPS foundation and blocked proof](frozen-cpu-mps-benchmark.md), [device arithmetic policy](arithmetic-mps-v1-policy.md), [protocol](../configs/benchmarks/frozen_cpu_mps_v1.json), [Task0023 summary](../results/tables/final/task0023-cpu-mps-benchmark-summary.json) and [handoff](handoffs/0023-frozen-cpu-mps-benchmark.md).
- [ONNX CPU accepted export/equivalence](frozen-ae-onnx-cpu-export.md), [independent arithmetic policy](arithmetic-onnx-cpu-v1-policy.md), [protocol](../configs/exports/frozen_ae_onnx_cpu_v1.json), [pinned optional dependencies](../configs/dependencies/onnx_cpu_v1.json), [Task0024 summary](../results/tables/final/task0024-ae-onnx-cpu-export-summary.json) and [handoff](handoffs/0024-frozen-ae-onnx-cpu-export.md).

### 21.2 External references

- [Zenodo LHCO R&D v5](https://zenodo.org/records/6466204), [version DOI](https://doi.org/10.5281/zenodo.6466204), and [API metadata](https://zenodo.org/api/records/6466204).
- [Original R&D schema description](https://zenodo.org/records/4536377) and [official LHCO challenge website](https://lhco2020.github.io/homepage/).
- [The LHC Olympics 2020 benchmark paper, arXiv:2101.08320](https://arxiv.org/abs/2101.08320).
- [CERN openlab R&D directions](https://openlab.web.cern.ch/our-rd-directions/).
- [ONNX Runtime CoreML execution provider](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html).
- [Apple Core ML optimization guide](https://apple.github.io/coremltools/docs-guides/source/opt-overview.html).
- [NVIDIA TensorRT documentation](https://docs.nvidia.com/deeplearning/tensorrt/latest/index.html).
- [hls4ml introduction](https://fastmachinelearning.org/hls4ml/intro/introduction.html).

Runtime documentation and compatibility must be rechecked when the corresponding deployment task begins. External context explains motivation/capabilities; local artifacts and reports establish project results.

### 21.3 Memory revision history

| Revision / date | Durable change | Evidence basis |
| --- | --- | --- |
| 1.0 / 2026-10-06 | Established an English, maintained project-wide memory distinct from task handoffs; incorporated Tasks 0001-0008, canonical v2, frozen scientific contracts, rationale, roadmap, update rules, and session bootstrap instructions | Repository snapshot `0645077`, exact configurations/artifacts/curated results, scientific reports and historical handoffs |
| 1.1 / 2026-10-06 | Selected local2/mean8 particle reconstruction design over event-only Chamfer and attention; froze score, capacity limits, CPU resource/convergence gates and proposed Task 0010; no implementation/training/calibration or new population access | Task 0009 design-only specification, analytic budgets/synthetic formulas and rechecked Task 0008 small-file evidence |
| 1.2 / 2026-10-06 | Exact particle design implemented with 247 synthetic tests and measured temporary allocations; 8 GiB launch gate failed at 3.694794 GiB before real reads, leaving canonical stages pending; next bounded decision addresses host resources without scientific drift | Task 0010 implementation/report/curated gate summary; base `96ef5aa`; zero real population requests |
| 1.3 / 2026-10-06 | Added one lineage-bound recovery route and stable read-only readiness; 296 synthetic tests pass but three samples fail unchanged memory thresholds, leaving all real particle stages pending and recovery allowance unused; separate prerequisite snapshots preserve uncommitted Task 0010 | Task 0011 report/readiness summary; zero new real attempts/reads/updates; original scientific/resource identities unchanged |
| 1.4 / 2026-10-07 | Explicit resumption after user-reported reboot/manual preparation: current acceptance verified, one new bounded preflight still fails8GiB launch (4.6248–4.6819GiB) while floor/RSS/native pass; stop before reservation/data; initial commits verified and next dependency narrowed to separate engineering-policy review | Dated Task0011 handoff/report/summary resumption; all older evidence preserved; science and every ceiling unchanged |
| 1.5 / 2026-10-07 | Explicit launch-only engineering v2 (4GiB+512MiB) with unchanged floor/native/RSS/time/math contracts; sole provisional preflight now fails4.5GiB and4GiB, zero reader/dev use. Final365synthetic checks; v2 provisional/not activated and future artifact compatibility specified; no canonical successor yet | Task0012 sidecar/report/summary; historical v1 and Task0010/0011 evidence preserved |
| 1.6 / 2026-10-07 | Stdlib supervisor delivered with422tests and one data-free fixed experiment; own-parent peakRSS319.391MiB lower but light worker3.1778–3.2442GiB still fails4.5/4GiB. External single study prepared/unreserved, original budget unused; causal attribution and full-run compatibility remain open | Task0013 measured receipts/summary/report; Task0012 commit53b238a and historical bytes verified |
| 1.7 / 2026-10-07 | Reconciled later external study: bounded-dev activation/memory pass,96steps consumed,749.343s throughput failure/no convergence. Shared-use Mac preference preserved. V3 cached bindings/flush tested471cases; one synthetic matrix gives component gains/no workload gain, zero new real work; Task0015 requires separate budget/authorization | Task0013 immutable manual receipts plus Task0014 manifest/report/summary/acceptance; commit9d5e03b verified |
| 1.8 / 2026-10-07 | Explicit50ms/≤100ms v4 observation architecture with fresh process guards and532tests; fixed paired2.1403×workload gain misses3×budget gate, zero readiness/real slots/updates. Failure-peak accounting repaired with original evidence preserved; v3 rerun superseded, next bounded engineering/runtime-budget decision, shared-Mac preference unchanged | Task0015 manifest/report/summary/current acceptance and original/affected-only synthetic receipts; Task0014 commit8d0e3f9 verified |
| 1.9 / 2026-10-07 | Prospective Task0016 synthetic3×admission supersession for one diagnostic, unchanged v4/science/180s; replaces unused≤96allowance/cumulative≤192,576tests. Sole readiness3.558GiB fails4/4.5GiB before data/steps; shared optional Terminal slot pending, no app cleanup/window or identical successor | Task0016 typed authorization/current acceptance/read-only receipt/report/summary; Task0015 commit0610c0f and historical original/final evidence verified |
| 1.10 / 2026-10-08 | Task0016 manualWARN2/unmeasured availability reconciled without borrowing3.558GiB. Task0017 versions explicit check/history semantics: repeated check-only never reserves, separate run always fresh-checks/claims canonical Task0016≤96/cumulative192anchor;612tests/one3.705841GiB floor-failed integration,0real action/slot. No new task/commit for later safe checks or app cleanup/polling | Task0017 workflow/current acceptance/immutable integration receipt/report/summary; Task0016 commitf74c7db and both historical failures preserved |
| 1.11 / 2026-10-08 | Explicit dev-only512MiB RSS/256MiB native policy removes fixed global reserve; WARN advisory/CRITICAL veto/unknown disclosed.670tests/portable670; one bounded real96step run completes exact historical parity,240.728s>180s. Shared anchor192/192consumed, next one consolidated full-store/time/shared-use decision; PCA/AE hardware independent | Task0018 policy/source acceptance/actual receipts/report/summary; baseb194050 verified, original science and historical failures preserved |
| 1.12 / 2026-10-08 | Task0018 commit reconciled; documentation-only consolidated time/full-custody/shared-host decision defers local canonical particle execution under unchanged contracts.240.728s/13.3738h per200cycles/28.7476h two-plus-postfit planning;192consumed/0newwork. Concrete frozen PCA/AE v2 CPU Task0020 brief next, no idle Mac/readiness prerequisite or new permission | Task0019 original small receipt lineage/arithmetic/JSON/source/config/artifact identity checks; base5da9094 verified, historical handoffs/failures/accepted source preserved |
| 1.13 / 2026-10-08 | Task0019commitc3008d4 reconciled; Task0020 CPU foundation validated763full/portable tests with public Accelerate thread proof. One guarded7.9898s campaign prepares1024rows/PCA1measures15cells; AE1fails unchanged batch-shape reconstruction tolerance,75cells missing/slot consumed/no retry. Parity review next before full CPU/MPS; particle192/deferral/test embargo intact | Task0020 protocol/new86-source acceptance/actual receipts/partial summary; frozen files and historical records preserved |
| 1.14 / 2026-10-08 | Task0020commitdba4635 reconciled; isolated Task0021review827full/portable tests and one complete AE diagnostic confirms historical coordinate. All1024rows/grid: exact repeats, v1 reconstruction/SSE failures, zero sampled frozen decisions;2.911858s/1prepared read/0newpopulation/custody/optimizer/timing. Recommend inactive arithmetic-aware Task0022contract/new independent CPU campaign; kernel/universal parity unverified, particle192/deferral intact; informative delivery preference persisted | New strict review protocol/90-source acceptance/fixed synthetic study/real numerical receipt/report/summary; historical executable/artifact/receipt bytes preserved |
| 1.15 / 2026-10-09 | Task0021commit17a7146 reconciled; explicit prospective CPUv2 arithmetic policy derives/tests both paths/SSE/outward bounds under checked band/local assumptions.942full/portable tests/fixed synthetic study before96-source freeze; one complete25.6615s/90cell/18000timing independent campaign, exact repeats/references/0sampleddecisions,1original+6local reads/0newpopulation/custody/optimizer. Raw outliers/history preserved; fresh M5metadata, MPSFalse/independent device Task0023brief next; particle192/deferral unchanged | Frozen derivation/protocol/acceptance and actual seven stage receipts/JSON/CSV/report; source/model/calibration/old records byte preserved |
| 1.16 / 2026-10-09 | Task0022still16staged/no commit, exact index preserved; isolated Task0023device policy/controller/workers/sync/scopes/guards/software tests. One104-source check built=True/available=False and initial raw-vs-JSON build digest failure; same actual CPUbuild, original failed evidence retained, software-only regression fix/1033full+portable/91newtests, no replay/current physical proof/real array/slot/timings. Next separately authorized Task0024CPU ONNX export/equivalence; particle192/deferral unchanged | Precheck and final software-only acceptances/snapshots, sole original availability receipt, zero real campaign and curated report/summary; old96sources/94receipts and frozen science preserved |
| 1.17 / 2026-10-09 | Task0022commit61611341/Task0023commit933cba22 verified, historical handoffs preserved. Task0024additive7ONNXwheels/all36prior packages/core builds unchanged;1111full+portable/78new actual synthetic integration/smoke before114-source freeze. One accepted11464B/opset18/IR10/exact155FP32/fourGemm+twoRelu CPU export, four synthetic families then1original1024row read/all1193windows/local/outward/repeat/strict0mismatches,19.407739s/0performance. Next separately authorized paired CPU Task0025; MPSproof/particle192/deferral unchanged | Strict protocol/dependency/policy/source acceptance and actual sole export/manifest/synthetic/real/guard receipts; final metadata validation, all old104source/101evidence/3acceptance identities retained |
| 1.18 / 2026-10-09 | Task0024 commit cacaefd3 verified. Isolated paired CPU benchmark 1179 full/portable tests, 121-source freeze; four frozen synthetic families, one original/six local reads, all 90 cells/18000 timings and zero pre/post threshold mismatches. ORT3 body receipt complete but parent exit deadline fails, −15/reaped; whole 128.781 s, consumed/no replay/accepted speedup. Scientific eval-v1 sufficient; finite full-store orchestration + explicit unblinding Task0026 next, independent of optional hardware; particle192/deferral unchanged | Task0025 protocol/source acceptance/unchanged 114 prior sources, original worker and failed parent receipts, curated JSON/CSV/report; 1147 initial prior byte identities preserved outside three living documents |
| 1.19 / 2026-10-09 | Task0025commit2f3cde01 reconciled/failed consumed lifecycle preserved. Task0026 Phase A implements guarded native evaluation/reporting, durable pre-read/per-batch/inflight exposure, exact4096tails, isolated6GiB/512MiB/128MiB/120s candidate caps.1259full+portable/80newcases and130-source freeze; one10.173718s custody-only check/7.041106s constructor,2.109359741GiB RSS/209.25MiB native/exit0/reaped,0model populations/scores. Terminal0.416120s memory gap disclosed. Current fixed PCA/AE plan4requests/124batches/500942presentations, human authorization pending/finalunreserved, no test metrics/optimizer/particle change | Strict protocol/source acceptance, original readiness/parent lifecycle receipts, prepared-planSHA2c97dc2a…62e3d86f and curated summary/report; prior1229byte identities retained except three living documents |
| 1.20 / 2026-10-09 | Verified PhaseAcommite69d80ed, actual human approval of plan2c97dc2a…62e3d86f, all130source/science/dependency/plan identities and1259acceptance/readiness reused. One31.094950s native PCA→AE→reporting campaign exits0/reaped/parent-accepted,4test requests/124batches/500942presentations/250471unique events,0inflight/optimizer/tuning/replay. Both tests exposed. PCA AUC0.468489/AP0.364379, AE0.660064/0.547427 at39.924782%test prevalence; tight1e-3signal2vs56/100000, modest utility/capacity/CPU caveats. Next frozen scientific synthesis/frontier from accepted existing summaries only | Original approval/source/plan/readiness/PhaseBexposure/lifecycle/output receipts and curated scientific/operating tables/ROC-PR; Task0025failed and particle192 unchanged |

| 1.21 / 2026-10-11 | Verified local Phase B commit839f8cd/clean index; initial frozen native comparison and integrated synthesis completed from9pinned sources,10adapter cost groups/8original thresholds/2figures. Strict AE descriptive acceptance0.7264/selected32.5581% below initial39.9248%; no observed enrichment/significance/physical-rate claim.12new synthetic helper tests separate from historical1259;0newpopulation/scoring/custody/optimizer, permanentYES/YES. Independent-population protocol proposed/no automatic0028 | Task0027 report/curated tables/summary/figures/helper validation; source130/prior evidence preserved, Task0025failed and particle192/deferred unchanged |

| 1.22 / 2026-10-11 | Verified Task0027commitc6f07da/clean initial state; explicit Task0028 Phase A frozen three-prong/shared exposed BG protocol/foundation completed. Fresh API/cards/source pin; scalar/model/calibration identities and original130source bytes intact. Cachedscore byte/header/lineage only, originalFP metadata only;62new/1333full+portable/protected toy/139-source acceptance. Plan77f92d95…179fa9 ready for conditional human consent,0realpayload/numeric preparation/scoring/cache/FP/new BG forwards. No fresh BG/domain-shift or independent comparison; originalYES/YES, particle192/Task0025failed unchanged | Task0028 protocol/report/summary/new software acceptance/metadata plan; no human consent record or reserved Phase B |
| 1.23 / 2026-10-11 | Actual Phase A commit e381f54/clean base; approved plan77f92d95…179fa9 invoked once. Acquisition deadline failure,298.116752s whole, exit1/reaped/consumed/no retry. Interrupted raw transfer≥47185920B; frozen cleanup removed .part, surviving evidence preserved. No new scientific/numerical/model/cache work;139source unchanged, originalYES/YES/new modelNO,optimizer0,Task0025failed,particle192deferred | Actual report/summary/phase CSV/human approval; raw in-flight record disclosed, independent prospective replacement required |

| 1.24 / 2026-10-11 | Verified Task0028continuation commit01617d5/clean base; Task0029own146-source/1414full+portable/81new-case byte transport acceptance then sole3request session failed/consumed. Two206continuations,2timeouts/truncatedEOF;29990748Bpartial/SHA/durable evidence retained, accepted0, no HDF/numerical/model/science. Clock/200-206Retry-After limits documented;old139/evidence/exposure/particle192 intact | Actual report/summary/attempt CSV/failed-parent receipts; any partial reuse/new request separately authorized |

| 1.25 / 2026-10-11 | Task0029 continuation preserved uncommitted; fresh sleep records broadly explain historical clock divergence. Separate153-source/1503full+portable/89-case v3 acceptance, continuous deadlines and active/released idle assertion; sole206 copied-prefix session accepts235488994B/MD5/SHA,205498246 new bytes,870.632494s reserved, structureFP64[100000,2101] only. Zero new numerical/model/optimizer, originalYES/YES,new modelNO; later explicit local-file science brief, historical failures/particle192 unchanged | Task0030 frozen protocol/own software acceptance/actual source-prefix/lifecycle/checkpoint/integrity/structure/assertion receipts/report/summary/CSV;196 old bindings intact, no Git automation |

| 1.26 / 2026-10-11 | Clean actual c825445/committed0029–0030; separate161-source/1590full+portable/87-case local-science acceptance then sole29.058839sreserved campaign accepted.100000valid/nonempty/unique/disjoint,2signal requests/50batches/200000presentations,1all-roleFPload/2BGcacheloads/0newBGforward/optimizer/download,all3exposureYES. PCA AUC0.462953/AP0.360220,AE0.585877/0.479972; weaker than two-prong,strict AE34/116relative0.4410/selected22.6667%not enriched. Four tables/ROC-PR/conditional intervals/shared-BG limits; next offline synthesis, no automatic successor; historical failures/particle192 unchanged | Task0031 own frozen acceptance/plan/actual prospective authorization and complete custody/overlap/access/parameter/thread/continuous/resource/assertion/parent receipts; all153old sources/science preserved |

| 1.27 / 2026-10-12 | Clean committed Task0031 bf6a5c3; offline20-source synthesis completes frozen two-/three-prong baseline:4global/16calibrated/8topology/10CPU groups/3figures, all cuts/shared background preserved. AE advantage weaker on three prong; both strict selected fractions below mixture. Post-evaluation arithmetic/no significance/mechanism; B4096quality vs historical prepared-feature CPU costs. New access/arrays/scoring/fingerprints/optimizer/downloads0, permanentYES/YES/YES; next explicit exploratory/methodology decision with independent confirmation; no0033 or particle budget reset | Task0032 pinned curated registry, boundary-enforced separate helper, focused synthetic tests, report/tables/figures and decision matrix; historical evidence/dependencies unchanged |

| 1.28 / 2026-10-12 | Clean committed Task0032a671b98; one authorized exploratory8.778443s session after200-source/43-package/90new/179focused/1728full+portable acceptance.3features/350471rows,6scores/700942values,3membership loads/3300000records;24/6marginals/48rho/24exacttails/192profiles/16suppressed/two curated figures. Distinct profiles and weak global associations yield hypotheses, no residual/causal/selection/tail-repair/independent claim. Zero new forwards/reconstruction/AUC-AP/significance/FP/optimizer/download; all3exposureYES, baseline/failed campaigns/particle192 preserved. Next independent-confirmation methodology/no0034 | Task0033 actual prompt/frozen acceptance/plan/sole parent receipts/access/resource/assertion evidence, report/tables and visual QA; source unchanged after reservation |

| 1.29 / 2026-10-12 | Clean committed Task0033c9f9bc5 reconciled; Task0034 design-only ReLU/identity155parameter/bottleneck3/three-paired-seed comparison, exact background recipe/own calibration, alpha0.001/shared-event bounds/fixed gates.3publisher records/16metadata rows/0accepted; extra SR QCD+new XtoYYprime conditional on full-event/count/independence/precision/storage.19synthetic assertions and metadata/design checks, zero new operational access/model/fit/calibration/payload; YES/YES/YES/baseline/failed campaigns/particle192 preserved. Synthetic-onlyTask0035 proposed, no launch; training/acquisition/confirmation ungranted | Actual prompt, protocol/design-only sidecar, source registry/curated summary, prospective resource/access brief and handoff; Task0033 historicala671b98base unchanged |

| 1.30 / 2026-10-12 | Clean committed Task0034f27ce61; additive synthetic-only controlled activation foundation/219bindings/43packages/189focused/1917full+portable. Paired155parameter arms/actual order/own restore+calibration/shared-event integer bounds/unchanged gates.3native attempts,2pre-numerical failures preserved then final2.683233s accepted/12toy updates/65forwards/2333rows/6calibrations/assertion release; caps/gaps/context disclosed.403old bytes preserved except living docs, operational work0/YES3/baseline/failed campaigns/particle192 unchanged. Source adequacy go/no-go next; no0036/source acceptance/real allowance | Actual prompt, separate config/source/tests/entrypoint, final synthetic-only acceptance and native receipts, curated report/summary; detailed maps/weights/logs ignored |

| 1.31 / 2026-10-12 | Clean committedTask0035 34d7401 reconciled; Task0036 metadata-only pinned extra-QCD/XtoYYprime decision `unresolved_no_acquisition`. Full-event nonoverflow method identified, overflow/release/realized selected count/member expansion unresolved;requested50000notupperbound,236843floor/1450034V0.001/unchanged gates preserved.18retrievals/0searches/1metadata archive16084B/0event requests; archivepreflight rejected/stopped, pinned author texts support recipe.30evidence rows/26temporary boundary/scalar/CSV/identity checks;419old nonliving tracked bytes preserved, memory1.31/YES3/baseline/failed campaigns/particle192 unchanged. Manifest prerequisite or prospective amendment/retirement; no0037/source acceptance/model freeze/real allowance | Actual prompt, decision/evidence/curated summary/handoff; raw research/cards/archive/temporary helpers/checks ignored, Task0035 hashes historical and unchanged |

| 1.32 / 2026-10-12 | Task0036eight paths uncommitted/HEAD34d7401/empty index preserved. Explicit Task0037engineering branch: one model-free FIFO actual-capacity drop-tail/oldest flush/modeled padded batches/post-service toy cuts,324main+54stress/18traces/90000unique/1890000presentations.105targeted/2022full+portable/200bindings/43versions.2native numerical passes, firstvisualoverlap rejected then layoutrepair/revalidation/final6.105818s accepted/CSVidentical/3figures;actual756scenarios/3780000presentations. FinalWARNadvisory/caps/reap/release/gaps disclosed, operational0/YES3/sourceunresolved/Task0034unchanged.419oldtracked+5priorTask0036bytes preserved except sharedliving1.32. Next separate development-only variability/missing-chain-cost plan,no0038/deploymentwinner | Actual prompt/config/source/tests/validation+native entrypoints/final source-bound acceptance/receipts, curated table/figures/report; detailed states/streams/logs/receipts/maps ignored |

Keep future entries short and focused on project-level changes. Update current-state sections in place; the revision table is not a second task log.

| 1.33 / 2026-10-13 | Task0037committed84252b62/clean main/origin/main/448initial tracked hashes, history bases preserved. AuthorizedTask0038same1024dev rows/natural-padded public-service boundary;3loads/6models+6FP64copies/204cells/10200timed/2040warm-ups,100focused/2122full+portable/211bindings/43versions/native synthetic acceptance before freeze. One43.942592s real parent-accepted session, all pre/post/zero decisions/hash/caps/exits/reaping/release,26400NORMALpressure/overshoot0/gaps disclosed;3inspected figures/all repetitions/outliers retained. Packing cost/serial variability measured, no production-p99/Task0037change/confirmation/deployment; sourceunresolved/YES3/failed campaigns/particle192 remain. Next separately bounded raw-read/features design,no0039 | Original prompt/config/source/tests/validation+native entrypoints/final acceptance/plan/anchor; curated cells/summary/figures/report. Detailed artifacts ignored |

| 1.34 / 2026-10-13 | Clean committedTask0038 292a7e9 reconciled; original23paths/base/acceptance preserved. Task0039 synthetic narrow selected-HDF/full-frozen-feature foundation,88focused/2210full+portable/223bindings43packages31native files. One1.867575s metadata resolver loads6999IDs once/exact1024f80prefix, one2908260409BrawSHApass/HDFmetadataopen, zero event/golden/models; original schema/cache1MiB521.75 verified/decoder threading unknown. Allcaps/reap/release/overshoot0,NORMAL1653WARN1153/gaps disclosed. Future36cells720timed108warmups/732rawrequests30927rows/768featurecalls32448rows,384rawunique1024approved/312chunks24.501GiBgeometry; costs/parity/physical I/O unmeasured/futureauthfalse.466snapshots exceptliving3 preserved, two model contents not read/Gitunchanged. Next Task0040explicit grant/controller/acceptance/freeze,no launch; YES3/science/failures/particle192/sourceunresolved unchanged | Actual prompt/config/additive source/tests/driver/current-source acceptance/prospective resolver freeze/one consumed anchor; IDs/observations/receipts/maps/logs ignored, curated design/summary |

| 1.35 / 2026-10-13 | Clean committedTask0039 90868d6 reconciled; original20paths/base/resolver preserved. Separate Task0040payload controller/100focused2310full+portable236bindings43packages31native files before freeze, one19.498497s parent-accepted raw/read/feature/joint session:3members20997IDs3golden3072rows/1024approved384rawunique732requests30927rows768constructions32448rows/36cells720timed108warmups/exact72gates;2rawSHA5816520818B3handlesclosed. Allcaps/exits/reap/7assertionsrelease/overshoot0,WARNadvisory/gaps disclosed. B128read45.143features5.778joint50.013ms/all3figures/allreps/outliers retained; cache warm/sparse and decoder/I/O unknown, no production-p99/model/science/held-out/deployment.480nonliving bytes/two unreadmodel paths preserved; YES3/sourceunresolved/Task0034/failures/particle192 unchanged. Next joint preprocessing+native adapter design/no0041 | Actual prompt/config/additive source/tests/driver/fresh acceptance/freeze/one consumed anchor; curated cells/summary/figures/report, detailed ledgers/receipts/timings ignored |
