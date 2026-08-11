# Phase 47 — CI Evidence (Plan 47-10)

Records measured evidence for milestone invariant #5, binding constraint #2, and Phase 47
success criterion 5: the milestone branch pushed to `origin`, plus a completed CI run over it
covering the Windows and macOS lanes.

---

## Branch on origin

**Task 1 — pushed 2026-08-11T12:25:42Z, evidence captured 2026-08-11T12:25:51Z.**

Precondition check before push: `uv run pytest -q` on the branch tip (`fc288f0`) —
**1031 passed, 1 skipped, 212.56s** — confirmed green before pushing.

Command run: `git push -u origin gsd/v0.8.0-multi-master-composition`

```
remote:
remote: Create a pull request for 'gsd/v0.8.0-multi-master-composition' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.8.0-multi-master-composition
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]      gsd/v0.8.0-multi-master-composition -> gsd/v0.8.0-multi-master-composition
branch 'gsd/v0.8.0-multi-master-composition' set up to track 'origin/gsd/v0.8.0-multi-master-composition'.
```

Verbatim `git ls-remote --heads origin gsd/v0.8.0-multi-master-composition` output:

```
fc288f01d345ca252863e376ae2df043ecff0283	refs/heads/gsd/v0.8.0-multi-master-composition
```

- **Local SHA** (`git rev-parse gsd/v0.8.0-multi-master-composition`): `fc288f01d345ca252863e376ae2df043ecff0283`
- **Local SHA** (`git rev-parse HEAD` at push time): `fc288f01d345ca252863e376ae2df043ecff0283`
- **Remote SHA** (from `git ls-remote`): `fc288f01d345ca252863e376ae2df043ecff0283`
- **SHAs match.** No reconciliation needed.
- `gh pr list --head gsd/v0.8.0-multi-master-composition` returned **empty** — no pull request was
  opened, per the task's explicit instruction (the ship unit for `branching_strategy: milestone` is
  the milestone; the release PR is Phase 52's business).

<!-- gsd:write-continue -->
