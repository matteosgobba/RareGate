# Task0033 — Exploratory frozen-feature and score-tail diagnostics

## Metadata and outcome

2026-10-12 Europe/Rome. One conditional exploratory diagnostic session completed
and was `parent_accepted`, consumed with no retry/reset. Actual clean initial
`main` tracking `origin/main`, HEAD
`a671b9843f0913d7324df2dfa1a03bb60d16f07b` (committed Task0032), empty index and
no unrelated changes. Memory1.27→1.28. No staging, commit, push or hosted CI.
The original prompt and initial pending handoff were saved before substantive
implementation; ignored initial-state snapshot later preserves tracked hashes
before validation/living-document changes.

## Objective and scope

[Actual prompt](../prompts/0033-exploratory-feature-score-diagnostics.md) explicitly
authorizes one session after current-source software acceptance and plan freezing.
It fixes four questions: frozen input marginals, accepted within-candidate score
marginals, within-population monotonic associations and original-threshold feature
profiles. These samples are already permanently exposed. Task0032 remains the
completed frozen baseline; Task0033 adds exploratory, result-informed evidence,
without causal proof, independent confirmation or post-result development.

Original allowlist: manifest/configuration, event_features, split_codes, event_ids,
labels. Three-prong: accepted prepared manifest/features. Scores: exactly the six
prompt-listed Task0026/0031 arrays. No broad store, raw HDF5, physical aggregates,
particles, fingerprints, operational candidates, reconstruction, fitting,
calibration, inversion, threshold/candidate selection, AUC/AP, curves, significance,
confidence intervals, downloads or per-event diagnostic exports.

## Changes, files and technical decisions

Eight new `src/latenttrigger/diagnostics` modules separate standard-library
identity/plan handling, narrow numerical reader, pure descriptions, aggregate-only
reporter, explicit1GiB runtime guard, numerical/report workers and stdlib parent.
No historical analytical helper/controller/source is modified. New protocol:
[exposed_feature_score_v1.json](../../configs/diagnostics/exposed_feature_score_v1.json).
A validation script and four synthetic fixture/test/native-integration files are
new. README/memory/index are the only modified historical tracked files.

[Report](../exploratory-feature-score-diagnostics.md), curated JSON, five CSVs and
two PNGs describe all requested outcomes. Operational namespace is
`results/diagnostics/task0033-exposed-feature-score/`, ignored by the existing
results policy; validation/acceptance/plan/authorization are ignored under data.
No .gitignore change, binary scientific array, membership extract or environment
belongs in Git.

The plan binds39input files (28metadata+11array files), scientific manifests,
complete source order, candidate/calibration identities, original cuts/counts,
200source/config/test file hashes, Python/macOS and all43installed package versions.
Task0026 basename output keys and Task0031 relative keys are resolved explicitly;
zero/multiple admissible keys fail. Every used operational metadata file agrees
with the accepted curated Task0026/0031 receipt registries. Symlink/missing/altered
sources fail before operational numerical analysis; arrays are never regenerated.

Task0030 integer-scaled `mach_continuous_time`, independent parent alarms,
TERM/KILL/reaping and caffeinate-i-w assertion are reused after reading their
paths/clock/resource assumptions. The historical evaluation guard’s6GiB RSS is
**not** adopted: new subclass independently latches at1GiB, retaining native512MiB,
invalid-primary-accounting/CRITICAL veto, WARN advisory and disclosed unavailable
pressure. Stdlib parent remains128MiB; global free/inactive RAM is context only.
No persistent power setting, display assertion or app cleanup.

Workers install an I/O/import boundary: only allowed operational reads and owned
worker writes; network and candidate/statistical-framework imports prohibited.
The reporter reads five owned CSVs only, with predecessor identity/acceptance.
Source and plan cannot change after reservation. Durable numerical requests are
written before loads, completed afterward; interrupted reads retain inflight
uncertainty. No membership rows or score/feature arrays are serialized.

## Dependencies and fresh validation

No dependency install/change/download. Existing NumPy/Matplotlib implement ranks,
quantiles and standard scientific plots; no significance API is invoked. Pure
FP64 rank correlation uses stable sorting/average ties and centered covariance,
with explicit null/reason for constant/insufficient/undefined variables. Feature
ranks are reused for both candidates; mean/std use FP64, `ddof=0`; quantiles are
linear at all11fixed probabilities. FP32 standardized inputs remain frozen, with
original log1p channels0/1/2/7; no physical inverse/refit.

Final validation before freeze:

- 90 new specific synthetic cases pass, covering numerical allowlist, non-test
feature exclusion, roles/labels/counts/order, accepted source/prepared/receipt
lineage, same-length reversed arrays, hash/header/symlink/refusal, finite complete
FP32 features/nonnegative FP64 scores, duplicate/inflight requests, ties/strict
cuts, population std/quantiles, constant ranks and no significance APIs,20event
suppression, aggregate-only reporting, preservation, ceilings, suspension,
assertion failure/loss/release and body-versus-parent acceptance.
- 179 focused pass including89reused Task0030 continuous-clock/assertion cases.
- 1728 full in41.53s and1728portable in40.98s pass. Both complete suites run in
artifact-free isolated source copies using the existing synthetic legacy-schema
plugin for three historical v1 expectations. No operational candidate/feature /
score numerical access. This is artifact independence, not an actual Linux run.
- Lint, format and installed dependency checks pass.
- One final bounded native synthetic integration parent-accepted in8.581950s,
verified active/released assertion,80synthetic feature rows/160synthetic score
values and0operational numerical access. Two guarded workers exit0/reaped; no
physical sleep/suspension or hosted CI claim.

A preliminary direct script invocation could not import `tests`; corrected to
module execution before acceptance/freeze. A prior fully passing source version
was retained in ignored `prior-pass` evidence; final changes complete installed
package binding and explicit parent-finalization timing, then all required checks
were rerun. No operational sample was used in any software validation. The final
checks and source/dependency map match the actual accepted session.

## Freeze and prospective authorization

Frozen plan canonical SHA256:
`04325edc2c6573b1597bc2104701b99527ea38ac1105dc4ca0780d8c49ae4583`.
Freeze’s byte/header-only prerequisite0.137353s≤60s. The actual saved prompt text,
prompt byte hash, fresh acceptance, complete source map and finalized plan are
bound in `data/task0033-human-authorization.json` **before reservation**. Its
byte SHA256 is
`517e589783223bcd8aeb74f41c13aaa1497bc7a5de4f84f22b780b52364db52c`.
No additional general confirmation was requested. `--run` was invoked once;
exclusive operational directory/reservation prohibits replay. No post-reservation
code/protocol/plan change or diagnostic worker repetition.

Ignored software record: `data/task0033-validation/acceptance-checks.json`; fresh
acceptance: `data/task0033-software-acceptance.json`; frozen plan:
`data/task0033-execution-plan.json`. Curated summary contains their byte/canonical
bindings and input identities, not copies of operational acceptances or ledgers.

## Alignment and actual access

Original scientific identity `d12574e9…e12d2`; original feature FP32[1100000,8],
35200128B/SHA213d94d9…53015. All four required array files agree with the manifest’s
size/dtype/shape/SHA. Entire split-code/source-ID/label arrays are loaded once each,
1100000records per file,3300000total. Role4/5counts are150471/100000, all labels
consistent; complete ascending IDs0…1099999. Test positions are selected before
feature values. Selected background first/last IDs5/999999, signal1000000/1099999;
every accepted original4096batch boundary/complete3015/1696tail matches both
candidate ledgers. Frozen membership bytes, evaluation store/configuration and
unchanged accepted source-order implementations establish alignment beyond length.

Prepared three-prong FP32[100000,8] SHA3059ff96…7f93, scientific identity
`089f6c2c…2e622`, matches accepted Task0031 preparation and both new-signal score
receipts. Complete rows0…99999, label/validity/transform/source-order provenance;
no filtering/reorder/raw/fingerprint load. Six score hashes equal the prompt and
accepted parents/receipts; each FP64 array finite, nonnegative and exact-length.

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
exploratory_diagnostic_session: parent_accepted
feature_population_requests: 3
feature_rows_read: 350471
stored_score_array_loads: 6
stored_score_values_read: 700942
membership_array_loads: 3
membership_records_read: 3300000
new_model_forward_calls: 0
new_reconstruction_computations: 0
new_AUC_AP_or_significance_computations: 0
new_fingerprint_numeric_loads: 0
optimizer_updates: 0
downloads: 0
```

These are **new authorized numerical diagnostic reads**, not zero numerical access.
One original feature mapping supplies two owned role-selected populations; one
prepared array supplies the complete third population. All features reused across
candidates/tails; six score arrays each loaded once.24feature ranks/6score ranks
are in-memory repeated calculations. The plot worker reloads no feature/score.
Four explicit39file input-custody sweeps(freeze/prerequisites/worker/finalization)
and11NPYheaders each are distinct from numerical access.11NumPy loading calls also
parse headers; internal mapping/header rereads are not extra population requests.
Additional planning/source/dependency/output hashing is byte custody. Full access
journal remains ignored and includes requested/confirmed/inflight accounting.

## Observed results and interpretation

Complete coverage24feature/6score marginals,48associations,24tail-count rows and
192feature profiles. All24original-tail counts exactly reproduce Task0032.
Overlapping10statistics each of two original background score summaries agree;
no accepted signal marginal-summary overlap exists to cross-check.

Two-prong multiplicity median−0.680 vs three-prong−0.146; three-prong concentration
median−0.506 vs two-prong−0.239, with lower maximum-pT and balance medians. Both
signals have elevated scalar-pT and nearly equal eta-spread medians−0.797/−0.795.
Signed eta means are centered near zero and central mass ranges overlap. Similar
marginals alongside different scores leave single-feature narratives unresolved.

PCA mediansBG/two/three0.092717/0.084291/0.082806; AE1.237087/2.008749/1.576639.
AE central signal shifts coexist with BGp99.9=15.720911 above signal15.001871 /
14.419351. All comparisons remain within candidate; absolute cross-model residual
magnitudes are not discrimination. No AUC/AP/ROC/PR is recomputed.

AE multiplicity rho two/three−0.410895/−0.298538; signed eta/spread signal rho
roughly−0.25…−0.29. PCA associations mostly small (signal max-pT/eta-spread positive,
scalar-pT negative). None is undefined operationally; constants are validated
synthetically with explicit null reasons. These are associations, not feature
importance, causal effects or residual attribution.

Strict PCA background concentration median5.494/max-pT2.087, despite global
concentration rho−0.011. AE strict BG/two-prong balance medians3.298/7.021, versus
three-prong−0.138; its scalar-pT median2.188 and signed eta median−1.862. Two-prong
balance IQR0.739–11.592 and small reportable56/34signal slices require caution;
low signal eta spread≈−1.45/−1.47 is common. Nonlinear combinations, covariance,
capacity/score geometry and simulation differences remain alternatives.

Exact strict countsPCA124BG/2two/1three, AE116BG/56two/34three. All eight features
of PCA’s2/1event slices are suppressed:16of192rows, null values with exact
`small_tail_descriptive_summary_suppressed` reason. Counts remain; no singleton
feature values.20events is a descriptive convention, not confidence. Task0032’s
strict AE selected32.5581%/22.6667% below39.9248% remains; no weak-tail repair or
new winning cut. The report ends with observation/interpretation/alternative /
future-independent-test hypotheses; no test is launched or feature selected.

## Continuous lifecycle, resources and visual QA

Prerequisites0.124773s≤60; numerical dispatch0.555118s≤120; reporting8.043751s≤60;
parent finalization0.082993s≤15; reserved8.778443s≤240, whole8.904391s; overshoot0.
Both workers exit0/reaped/body-complete and independently parent-accepted after
source/grant/plan/output/deadline/resource checks. Cleanup within2s, watchers closed,
no latched errors. Resource peaks analysis121.171875MiB RSS/68.40625MiB native,
reporting128.078125/94.046875MiB; controller29.21875MiB. All296pressure samplesWARN,
0CRITICAL/unknown/malformed; global RAM contextual. Query-start max gaps56.367 /
76.217ms, terminal unaccounted28.181/79.903ms. No full continuous memory guarantee.

Storage policy before execution:256MiB total,64MiB guard per worker,1MiB logs and
access,4MiB JSON/receipt,2MiB CSV,8MiB per PNG. Final operational1437787B. No source
store copies or per-event exports. Seven active owned assertion observations;
controller89553/helper89556, release2026-10-12T08:47:53.103030Z (10:47:53Rome),
helper−15/reaped/timely/owned assertion absent/releasedTrue. Display sleep permitted;
manual sleep/lid closure possible, no persistent settings change.

All three generated PNGs visually inspected. Median/IQR panels and separate
within-candidate log-score quantiles are readable, denominators/standardized units /
original log channels/thresholds/guide-line and no-clipping caveats visible.
Association heatmap’s colorbar overlaps two columns: **excluded from curation**,
retained unchanged operationally. Complete48coefficient CSV/report table delivered.
No replot/retry/source/plan change after reservation. This limitation does not
alter parent lifecycle acceptance or numerical outputs; two readable figures are
curated, not a claim that all three passed presentation QA.

## Preservation, limitations and follow-up

Initial tracked-file hashes and final diff establish preservation outside the
three intentional living documents. Accepted input bytes checked before/after;
I/O boundaries prohibit source writes. Forbidden arrays are not reopened to invent
a broader history certificate. Task0032/0026/0031 scientific reports, parameters,
thresholds/transformations/source and all historical failures remain unchanged.
Particle192/192/deferred and Task0025failed/consumed remain. No package/power /
scientific-state or Git automation change. Operational artifacts remain ignored.

Shared background is not independent FPR replication; exact prepared disjointness
from Task0031 is inherited, not rechecked or proof of statistical independence.
Unequal6PCA/3AEcapacity, feature covariance/nonmonotonicity, simulation coverage and
quantile-only display leave mechanisms open. Exposed samples cannot be reblinded.
Next supported decision is to define a separately authorized independent-confirmation
protocol with representation/capacity controls before result-informed development.
Disclose this exploratory influence; no favorable feature/candidate/threshold
selection, new evaluation or automatic Task0034.

## Reproducibility and Git — manual only

Software validation command: `.venv/bin/python scripts/validate_feature_score_diagnostics.py`.
Historical Task0033 frozen evidence is immutable; do not overwrite its logs or rerun
`--freeze`/`--run` on this consumed namespace. Actual software and operational commands,
source/package/input/acceptance/plan/prompt/output hashes and numerical conventions
are retained in ignored evidence and summarized in the curated JSON. Any future
session requires new explicit authorization, own acceptance/namespace and scientific
scope. Regenerating scores or replaying the diagnostic is not a reproduction claim.

Final manual review/staging includes exactly the intentional new source/config/tests,
three paired/report documents, five CSVs, summary and two PNGs plus three living
documents. Do not force-add operational data/results/artifacts/logs/ledgers/receipts /
acceptances/plan/authorization or the visually rejected heatmap.

```bash
cd /Users/matteosgobba/Documents/GitHub/latent-trigger
git status --short --branch
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git diff --check
git diff --cached
git diff --no-index -- /dev/null src/latenttrigger/diagnostics/reader.py
git diff --no-index -- /dev/null tests/test_feature_score_diagnostics.py
git add -- \
  README.md docs/project-memory.md docs/handoffs/README.md \
  docs/prompts/0033-exploratory-feature-score-diagnostics.md \
  docs/handoffs/0033-exploratory-feature-score-diagnostics.md \
  docs/exploratory-feature-score-diagnostics.md \
  configs/diagnostics/exposed_feature_score_v1.json \
  src/latenttrigger/diagnostics \
  scripts/validate_feature_score_diagnostics.py \
  tests/test_feature_score_diagnostics.py tests/feature_score_fixtures.py \
  tests/feature_score_lineage_fixtures.py tests/feature_score_native.py \
  results/tables/final/task0033-exploratory-feature-score-summary.json \
  results/tables/final/task0033-feature-marginals.csv \
  results/tables/final/task0033-score-marginals.csv \
  results/tables/final/task0033-feature-score-associations.csv \
  results/tables/final/task0033-tail-counts.csv \
  results/tables/final/task0033-tail-feature-profiles.csv \
  results/figures/final/task0033-feature-median-iqr.png \
  results/figures/final/task0033-score-quantiles.png
git diff --cached --stat
git diff --cached
git diff --cached --check
git commit -m "feat(diagnostics): describe exposed frozen features and score tails"
git status --short --branch
git rev-parse --abbrev-ref '@{upstream}'
git push origin main
```

The no-index review commands return1for new content. These are manual instructions;
no task commit hash, push or hosted CI is claimed.

## Final delivery checks

Source/dependency/prompt/plan/acceptance bindings and both independently accepted
worker/output identities agree. Five curated CSVs are byte-identical to accepted
aggregates; both curated PNG identities agree. All24tail counts/denominators,
192profiles/16suppressions and exact3/350471/6/700942 plus3/3300000access counts
verified without numerical source reopening.304local relative links pass; whitespace
check passes; all operational arrays/evidence are ignored. Initial tracked hashes
are unchanged except README/memory/index, source map remains frozen, index empty,
HEAD/upstream unchanged.28intentional files(3modified+25new), no unrelated changes.
No stage/commit/push. Ignored final check: data/task0033-validation/final-check.json.
