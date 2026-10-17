# Task0065 — Public repository README

2026-10-17, Europe/Rome. Base `f6a8f04c420cc0909e3ec04bfa3e728b98bba22a`,
`main` tracking `origin/main`. Initial tracked tree/index clean; the user's
`assets/` directory was already untracked.
Status: `completed_public_repository_readme`; manual commit/push pending.

## Objective and scope

Replace the operational log at the repository entrance with a concise,
professional English README; preserve its complete contents separately; use the
existing v2 logo and user-confirmed author links. Follow the repository's
[development protocol](../development.md) and preserve scientific conclusions.
The [original prompt](../prompts/0065-public-readme.md) is recorded.

## Changes and decisions

- Replaced the 85,078-byte operational log with an English public README of
  approximately 880 words, including code and the repository tree. It covers the
  research question, methodology, final ADC results, requirements and commands,
  repository layout, limitations, author profiles, dataset credits and license.
- Used the existing `assets/branding/raregate-logo-v2.png` as the first visual,
  without editing the image. Included one existing curated quality/cost figure
  and a four-method table, with explicit units, sample sizes and timing scope.
- Preserved the negative compact-compression outcome and conditional
  Mahalanobis recommendation. The unresolved LQ utility target and lack of
  deployment readiness remain explicit. Public presentation does not reclassify
  historical engineering branches or change scientific claims.
- Archived the previous root README byte-for-byte as
  `docs/old/README-operational.md`. The adjacent archive index explains its
  original root-relative links and links to the base-commit GitHub view, keeping
  the archive itself unchanged.
- Used the GitHub identity from the repository origin and the LinkedIn URL
  explicitly supplied by the user. Updated the task index and memory to 1.60.

Changed tracked files: `README.md`, `docs/project-memory.md`,
`docs/handoffs/README.md`. Added documents: this handoff,
`docs/prompts/0065-public-readme.md`, `docs/old/README.md` and
`docs/old/README-operational.md`. The existing, untracked v2 PNG is required for
the new README and is included in the selective Git commands below; v1 and
branding prompt notes remain the user's separate existing assets.

## Validation and evidence

- Verified archive equality against `git show HEAD:README.md`: **85,078 bytes**,
  SHA-256 `c8472500ac9dc56683f0e452938b6cf92a37173da5262c111ffa400cca94b947`.
- Checked all local Markdown/HTML links in the rewritten README, archive index,
  prompt and handoff; visually inspected the existing logo and selected figure.
  The original archive retains its historical relative links intentionally.
- Checked all eight displayed efficiencies against the primary inference rows
  in `task0062-adc-evaluation-summary.json`; independently reconstructed the four
  joint B32 CPU medians from the stream/block CSV, averaging seeds before taking
  the median across eight blocks. Display rounding agrees.
- `.venv/bin/python -B -c 'import raregate; print(raregate.__version__)'` passed:
  version **0.1.0**.
- `.venv/bin/python -B scripts/smoke_test.py` passed: Torch **2.14.1**, CPU,
  MPS unavailable in this execution context, expected tensor result **16.0**.
  This is an environment diagnostic, not a new model benchmark.
- `git diff --check` passed. Tracked changes are restricted to documentation;
  the index remains empty. Source, configurations and accepted result/model
  artifacts are unchanged. No original payload/model access, experiment,
  training, scientific inference or broad test suite was performed.

Installation extras and supported Python versions were checked against
`pyproject.toml`; test commands against the existing CI configuration and docs.
No fresh environment installation or hosted CI run is claimed. External dataset
credits follow the accepted protocols; remote link availability was not tested
exhaustively. The linked complete scientific reports remain authoritative.

## Git delivery

No automatic staging, commit or push. Review and run from the repository root:

```bash
git status --short
git diff --stat
git add README.md assets/branding/raregate-logo-v2.png \
  docs/old/ docs/project-memory.md docs/handoffs/README.md \
  docs/handoffs/0065-public-readme.md docs/prompts/0065-public-readme.md
git diff --cached --stat
git diff --cached --check
git diff --cached
git commit -m "docs: present RareGate with a concise public README"
git push origin main
```
