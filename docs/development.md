# RareGate development protocol

Every operational Codex task receives the next sequential four-digit number.
Use `docs/prompts/NNNN-short-name.md` for its user specification and
`docs/handoffs/NNNN-short-name.md` for its factual handoff. Maintain the
[chronological index](handoffs/README.md) in every task.

## Workflow

Inspect → plan → implement/research → test/validate → document handoff → review
Git diff → user commits → user pushes.

1. Read [living project memory](project-memory.md) alongside instructions,
   repository state, branch, HEAD, and relevant files; verify its claims against
   current evidence before planning.
   Identify unrelated changes; preserve them and exclude them from staging.
2. Save the prompt before substantive work. Preserve an available original user
   message; if unavailable, label the record as reconstructed and cite its basis.
3. Write an initial handoff with the base commit, scope, and pending validation.
   Update it as evidence, decisions, and actual outcomes become available.
4. Keep implementation, externally verified facts, design proposals, and deferred
   work visibly distinct. Cite primary sources and explain decisions that affect
   later phases. Respect the task boundary.
5. Run relevant checks and report commands, outcomes, environment, and limitations.
   Never equate a configured CI job with a successful hosted CI run.
6. Update affected living-memory sections in place with durable outcomes,
   decisions/rationale, roadmap, limitations and next steps; preserve user content
   and distinguish designed, implemented and measured work. Keep execution detail
   in the handoff. Finish the handoff and index; inspect tracked and untracked
   changes, relative links, and artifact exclusions. Prompt and handoff files belong in the same
   commit as the work they document.
7. End every task with exact status/diff, selective staging, staged review,
   Conventional Commit, and push commands for the actual branch/upstream.
   Codex must not commit or push unless the user explicitly instructs it to.

## Handoff contents and history

Use Metadata, Objective, Scope, Changes, Files, Technical Decisions, Dependencies,
Validation, Results, Issues / Limitations, Rejected Alternatives, Reproducibility,
Follow-up, and Git sections where applicable. Metadata includes task number/name,
phase, date, status, branch, base commit, and environment. Mark unrun checks as
pending or unavailable. Before a user commit exists, record the base commit and
suggested message; do not invent a resulting commit hash.

Historical handoffs are records of their task-time state. Do not silently rewrite
them. A later correction must be explicit, dated, justified, and linked from the
new handoff and index. A later commit confirmation may be appended with its
verification date; it must preserve the original record.

Keep downloaded data, environments, caches, generated results, and checkpoints
out of Git. Only intentionally curated small artifacts may be committed through
the documented results policy. A design document or command example does not
mean a downloader, preprocessing step, model, or benchmark has been implemented.

## Generated portable audit hygiene

For the Task0060 portable selection, use `PYTHONDONTWRITEBYTECODE=1` and the
existing interpreter with `-B scripts/run_scientific_audit.py --root <new-absolute-root>`.
The root must be new and outside the checkout. The runner disables pytest cache
and plugin autoload, contains XDG/matplotlib/temp output before imports, preserves
incremental stage reports and binds the tested source/config bundle. Use Ruff
`--no-cache` for lint/format work. The periodic output monitor is an observed stop,
not a pre-growth all-writes guarantee. Keep interrupted attempts and distinguish
their work from a complete final-source result. Generated test contexts must use
fresh mock roots and restore shared state; never activate/reset historical runs
or treat unit-profile metadata as an operational permit. See the
[audit and exclusions](project-scientific-audit.md) before expanding its test group.

## Standing delivery preference

Final task responses must explain the completed work, key data, validation,
limitations, decisions and concrete next step in enough detail to serve as a
useful handoff to the planning chat. Make the response self-contained, distinguish
historical/measured/inferred/proposed/unverified statements, honor the requested
language and include the actual manual Git section last. A bare status/test count
or a link to logs is insufficient when substantive findings need interpretation.
