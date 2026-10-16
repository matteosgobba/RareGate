# RareGate naming and migration

On 2026-10-16, Task0064 renamed the project from LatentTrigger to **RareGate**.
The Python distribution and import package are both `raregate`; the checkout
folder is `RareGate`. The software version remains 0.1.0.

## Current usage

Install from the checkout with `python -m pip install -e ".[dev,data,analysis]"`.
Use `import raregate` and `python -m raregate.<module>` in place of the previous
Python namespace. Worker module names, source discovery, environment variables,
examples and current documentation use the new name. Existing environments
must be reinstalled after moving a checkout because editable installs and
virtual-environment launchers contain absolute paths.

The final reports are now [raregate-final-report.md](raregate-final-report.md)
and [raregate-final-decision-brief.md](raregate-final-decision-brief.md).

## Historical evidence

This is a software and editorial rename. It does not repeat or reaccept an
experiment, change numerical results, or reopen the closed research cycle.
The tracked `results/` and `artifacts/` trees, frozen preprocessing/model
configurations, and original task prompts/handoffs retain their exact bytes.
`latenttrigger-evaluation-v1`, historical source-binding identifiers and Git
object paths retain their original spelling because they identify persisted
formats or historical evidence. They are compatibility identifiers rather than
the current project name.

Current source paths migrate from `src/latenttrigger/` to `src/raregate/`.
Historical source fingerprints remain fingerprints of their original bytes;
they do not certify the renamed source. Historical source-bound acceptance
must continue to fail closed when the current bytes differ. Use the original
recorded commit for exact historical reproduction; the complete pre-rename
checkout is available at commit `a3eb927`. For example:

```sh
git show a3eb927:docs/latenttrigger-final-report.md
git show a3eb927:src/latenttrigger/models/pca.py
```

The current human-readable scientific documents use RareGate editorially;
their scientific hashes and numerical claims remain historical. The explicit
pure-helper import pin in `synthesize_signal_topologies.py` tracks its renamed
helper; it does not update historical experiment receipts or grant execution.
Current configuration and documentation validation digests were recomputed for
the migrated software. The protected import-only particle implementations also
have current byte digests. Historical result/model digests and scientific
preprocessing/model configuration bytes were preserved. Structural comparison
against the pre-rename Python files checks that changes are restricted to names,
paths, formatting and these explicit validation digests.

## GitHub and Git history

Changing the local directory does not rename the GitHub repository. The manual
delivery commands rename the hosted repository to `RareGate`, update `origin`,
and create a normal commit on `main`. No staging, commit, push, hosted rename,
or history rewrite is performed automatically.

Git stores published file changes in commits. `git commit --amend --no-edit`
can incorporate a rename into the most recent commit without a separate commit
message, but changes that commit's identity. Replacing an already published
commit requires a history rewrite and does not make the modifications invisible.
