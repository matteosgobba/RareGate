# Task0064 — Rename the project to RareGate

2026-10-16 (Europe/Rome). Base `a3eb9273053c1774b42eea26acf12630e543c11b`,
`main` tracking `origin/main`; working tree and index initially clean.
Status: completed software/editorial rename; user reviews, commits and pushes.

## Outcome and scope

Current branding is **RareGate**, the Python distribution/import namespace is
`raregate`, and source code is in `src/raregate/`. Updated imports, dynamic worker
names, source discovery, configuration paths, environment variables, user agents,
installation metadata, examples, current documentation and the two final report
filenames. Version remains 0.1.0. The checkout is relocated to
`/Users/matteosgobba/Documents/GitHub/RareGate`; existing local virtual-environment
absolute locators are repaired and the editable distribution is installed as
`raregate` after removing the previous distribution metadata.

The [migration guide](../renaming.md) explains current usage, historical names,
source-binding implications, and exact pre-rename Git lookup. Updated the living
memory to 1.59, navigation links and this index. The actual user instruction is
preserved in the [task prompt](../prompts/0064-raregate-rename.md).

## Scientific identity and compatibility decisions

All 189 tracked files in `results/` and `artifacts/` preserve their exact bytes.
Frozen `configs/data/` and `configs/models/` files, original task prompts/handoffs
and persisted protocol IDs remain unchanged. In particular,
`latenttrigger-evaluation-v1` remains readable by existing models. The handoff
index is living navigation; its final-report links point to the renamed files.

Current configuration/document validation hashes and the explicitly protected
import-only particle-source hashes were rebound to the migrated software.
Historical experiment receipts, numerical identities, targets and outcomes are
not rewritten or reaccepted. Existing original acceptance/permission gates remain
source-bound and must refuse mismatching renamed code. No acquisition, original
payload/model read, scientific evaluation, operational benchmark or new research
cycle was run. Generated tests do perform their existing toy fits/forwards and
process checks; those are software validation, not scientific evidence.

## Validation and limitations

- Static comparison of 381 tracked Python files against base `a3eb927` found no
  unexpected structural changes after normalizing the explicit namespace/path
  substitutions, formatting and updated validation digests.
- Exact SHA-256 comparison preserved all 189 tracked result/model files; frozen
  scientific configuration trees have no Git diff.
- Ruff lint passes; Ruff formatting passes for 590 discovered files; whitespace
  checks pass. Editable wheel builds and installs as `raregate==0.1.0`; direct
  import and distribution metadata checks succeed.
- The broad generated portable run (`...-v4`) observed **3,086 passing tests and
  13 passing subtests**. It reached the existing 2 GiB observed scratch-storage
  ceiling and is **not a successful uninterrupted whole-suite run**. One setup
  error was induced by the runner's termination; one actual failure exposed the
  remaining current monitor/config binding mismatch.
- After correcting that binding, the focused final run (`...-v5`) completes
  **78/78 tests**, including both affected modules, in 8.93 seconds with no stop
  reason. Together v4/v5 contain **3,088 distinct test node IDs with passing
  observations and no outstanding failing node ID**. The existing 938 costly
  modules/cases were excluded by the established portable selection. Hosted CI
  and the unrestricted full suite were not run.
- Earlier collection/source-binding failures, sandbox process-inspection errors
  and the generated-only interrupted broad attempt remain in temporary receipts;
  they are superseded only for the corrected software checks. No historical
  experiment acceptance or consumed allowance is changed.

Temporary verification receipts are under `/private/tmp/raregate-rename-*`;
`raregate-rename-static-checks.json`, `raregate-current-config-rebinding.json`
and `raregate-checkout-move.json` record static checks, current configuration
rebinding and the directory/environment relocation. These are local scratch
receipts, not committed research outputs.

## Git and GitHub delivery

No staging, commit, push, history rewrite or hosted repository rename was
performed. The local `origin` remains
`https://github.com/matteosgobba/latent-trigger.git` until the user executes:

```sh
cd /Users/matteosgobba/Documents/GitHub/RareGate
git status --short --branch
git diff
gh repo rename RareGate --repo matteosgobba/latent-trigger --yes
git remote set-url origin https://github.com/matteosgobba/RareGate.git
git add -A -- LICENSE README.md pyproject.toml configs data/README.md docs scripts src tests
git diff --cached
git diff --cached --check
git commit -m "refactor: rename LatentTrigger to RareGate"
git push origin main
```

GitHub repository renaming is separate from committing content. Published file
changes cannot be invisible: an amend can avoid a separate rename commit but
changes the previous commit's hash and requires replacing published history.
A normal commit preserves the pre-rename snapshot referenced by this migration.
The scientific cycle stays closed; no successor experiment is launched.
