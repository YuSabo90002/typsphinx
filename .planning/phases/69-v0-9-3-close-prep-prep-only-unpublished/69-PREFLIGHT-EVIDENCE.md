# Phase 69 — REL-12 Update-Step Pre-Flight (D-07, non-committing)

Nothing in this file is committed to the branch except the file itself, and no merge is performed.
Every command below was re-run live from this worktree during this plan's execution — no value is
copied from `69-CONTEXT.md` or `69-RESEARCH.md`, both of which state their own numbers are stale by
execution time (Pitfall 1).

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T22:47:50Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a598531089ee1b8e7

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
[... resolved and installed the dev extra into this worktree's own .venv, including
typsphinx==0.9.2 from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a598531089ee1b8e7 ...]

$ uv --version
uv 0.12.13 (x86_64-unknown-linux-gnu)
```

Before any commit in this plan:

```
BASE_69_05 = becd70c31bfed573dc10cdc20dcf7a30d57edd57
TRIAL_HEAD = becd70c31bfed573dc10cdc20dcf7a30d57edd57
```
Both are `git rev-parse HEAD`, taken before this plan's first commit — the worktree branch check
recorded this same SHA as the fork base at spawn time.

```
START_CANONICAL = becd70c31bfed573dc10cdc20dcf7a30d57edd57
```
From `git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair`, equal to `BASE_69_05` — this
worktree forked from the canonical ref's own tip.

## Fetch and divergence

```
$ git fetch origin
(no output — up to date with what this worktree already had cached, or fetched silently)

$ git rev-parse origin/main
cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
```
```
ORIGIN_MAIN_SHA = cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
```

```
$ git log --oneline "$TRIAL_HEAD".."$ORIGIN_MAIN_SHA"
cf3305ce Merge pull request #138 from YuSabo90002/dependabot/uv/ruff-0.16.6
88088071 chore(deps): bump ruff from 0.15.20 to 0.16.6
293f0c26 Merge pull request #137 from YuSabo90002/chore/dependabot-uv-ecosystem
7cc85d28 chore(deps): switch dependabot Python updates from pip to uv
```
```
MAIN_ONLY_COMMITS = 4
```

```
$ git rev-list --left-right --count "$ORIGIN_MAIN_SHA"...HEAD
4	210
```
`origin/main` carries 4 commits this worktree's `HEAD` lacks; this worktree's `HEAD` carries 210
commits `origin/main` lacks (the milestone's own work through wave 1).

```
$ git merge-base HEAD "$ORIGIN_MAIN_SHA"
6181768f64b4cee62a77ac4e26c60c3c976cbb6e
```

## Trial merge

```
$ git merge-tree --write-tree "$TRIAL_HEAD" "$ORIGIN_MAIN_SHA"; echo "exit:$?"
32f0573c8dccda8101a8df34a9c968ba2952108b
exit:0
```
```
MERGE_RC = 0
MERGE_TREE = 32f0573c8dccda8101a8df34a9c968ba2952108b
```
A real tree SHA with exit code 0 means the trial merge is conflict-free.

**This tree SHA is valid only for these two inputs (`TRIAL_HEAD` and `ORIGIN_MAIN_SHA`) and must be
re-measured immediately before the real merge** — both refs are moving targets, exactly as
`69-RESEARCH.md` Pitfall 1 predicted (the tree SHA it measured, `2a8a5907…`, is already different
from `32f0573c…` measured here, a few commits later).

## Merged lock

```
$ S="$(mktemp -d)"
$ echo "$S"
/tmp/tmp.yur7eYFHqt
```

```
$ git archive "$MERGE_TREE" pyproject.toml uv.lock | tar -x -C "$S"
(no output)
$ ls -la "$S"
pyproject.toml
uv.lock
```

From the worktree root:

```
$ uv --directory "$S" lock --check; echo "exit:$?"
Using CPython 3.14.4
Resolved 91 packages in 4ms
exit:0
```
```
LOCK_CHECK_EXIT = 0
LOCK_CHECK_UV_VERSION = uv 0.12.13 (x86_64-unknown-linux-gnu)
```

```
$ sed -n 7p "$S/pyproject.toml"
version = "0.9.2"
```
```
MERGED_VERSION_LINE = version = "0.9.2"
```

```
$ grep -nE 'tox-uv|"ruff' "$S/pyproject.toml"
38:    "tox-uv>=1.35,<2",
40:    "ruff>=0.15,<0.17",
```

```
$ grep -A1 -xF 'name = "ruff"' "$S/uv.lock"
name = "ruff"
version = "0.16.6"
```
```
MERGED_RUFF_LOCK_VERSION = 0.16.6
```

```
$ grep -A1 -xF 'name = "ruff"' uv.lock
name = "ruff"
version = "0.15.20"
```
```
BRANCH_RUFF_LOCK_VERSION = 0.15.20
```
This is the divergence Phase 67 D-04 recorded and deliberately left unfixed: this branch's own lock
still pins `ruff` 0.15.20 (matching NIX-01's measurement on this branch), while `origin/main`'s lock —
and the merged tree above — pins 0.16.6 via PR #138. REL-12's merge is where the branch actually
absorbs 0.16.6; NIX-01's binding sense is "the version `uv.lock` pins," so this is expected to
change, not a regression to guard against here (67-CONTEXT D-03/D-04).

```
$ git show "$MERGE_TREE:CHANGELOG.md" > "$S/merged-changelog.md"
$ awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' "$S/merged-changelog.md" | grep -cE '^- \*\*'
3
```
```
MERGED_CHANGELOG_BOLD = 3
```
The merged tree's `## [Unreleased]` region carries exactly the three bold-lead bullets `69-01`
landed (TOX, DEP, NIX order) — the trial merge includes this phase's own wave-1 CHANGELOG edit, as
the task's `<precondition>` required.

```
$ rm -rf "$S"
```

## Nothing moved

```
$ git rev-parse HEAD
becd70c31bfed573dc10cdc20dcf7a30d57edd57
```
Still equals `TRIAL_HEAD`, recorded before this plan's own commit of this evidence file.

```
$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
becd70c31bfed573dc10cdc20dcf7a30d57edd57
```
Still equals `START_CANONICAL` — the orchestrator has not yet advanced the canonical ref past this
worktree's fork point.

```
$ git status --porcelain
(empty, before this plan's own commit of this evidence file)
```

```
$ git merge-base --is-ancestor "$ORIGIN_MAIN_SHA" HEAD; echo "exit:$?"
exit:1
```
`origin/main` is **not** an ancestor of `HEAD` — the branch has not absorbed `main` (D-06). Together
with the merge-commit check below (no merge commit exists since `BASE_69_05`), this confirms
`git merge-tree --write-tree` added only unreferenced objects to the object store: no ref moved, no
commit was created, and no branch state changed.

```
$ git rev-list --merges becd70c31bfed573dc10cdc20dcf7a30d57edd57..HEAD
(empty)
```

## Task 1 result

The REL-12 update merge (`origin/main` into this milestone branch) is measured conflict-free, with a
valid merged lock, and this branch is untouched by the measurement.

## Head check (Task 2)

```
$ test -f .git; echo "exit:$?"
exit:0
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a598531089ee1b8e7
$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

## Merged-tree lint

This is D-07's optional half, exercised because the milestone changed test files that `main` has
not yet linted under `ruff` 0.16.x.

```
$ S2="$(mktemp -d)"
$ echo "$S2"
/tmp/tmp.hDSEwnyTpZ
$ git archive "$MERGE_TREE" | tar -x -C "$S2"
(no output)
```

```
$ uv --directory "$S2" sync --locked --extra dev --no-install-project
[... hash-verified install from the merged uv.lock only, resolving 91 packages including
ruff==0.16.6 ...]
```
This is a hash-verified install from the merged `uv.lock` only — every package it resolved,
including `ruff` 0.16.6, entered that lock through a reviewed commit (#138, `67-PROOF-EVIDENCE.md`).

```
$ uv --directory "$S2" run --no-sync ruff --version
ruff 0.16.6
```
```
MERGED_RUFF_RUN_VERSION = 0.16.6
```
Equal to `MERGED_RUFF_LOCK_VERSION` recorded above.

```
$ uv --directory "$S2" run --no-sync ruff check .; echo "exit:$?"
All checks passed!
exit:0
```
```
MERGED_RUFF_EXIT = 0
```

```
$ uv --directory "$S2" run --no-sync black --check .; echo "exit:$?"
All done! ✨ 🍰 ✨
355 files would be left unchanged.
exit:0
```
```
MERGED_BLACK_EXIT = 0
```

```
$ rm -rf "$S2"
```

Both exits are 0 — no `## FINDING: merged-tree lint` section is needed. Nothing was fixed because
nothing failed.

## main protection (D-08)

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '.required_status_checks'
{"checks":[{"app_id":15368,"context":"Test Python 3.12 on ubuntu-latest"},{"app_id":15368,"context":"Lint and Format Check"},{"app_id":15368,"context":"Type Check"},{"app_id":15368,"context":"Code Coverage"},{"app_id":15368,"context":"Build Package"},{"app_id":15368,"context":"Test Python 3.13 on ubuntu-latest"}],"contexts":["Test Python 3.12 on ubuntu-latest","Lint and Format Check","Type Check","Code Coverage","Build Package","Test Python 3.13 on ubuntu-latest"],"contexts_url":"https://api.github.com/repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks/contexts","strict":true,"url":"https://api.github.com/repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks"}
```
```
PROTECTION_STRICT = true
PROTECTION_CONTEXTS_COUNT = 6
```
The six required contexts, verbatim:
1. Test Python 3.12 on ubuntu-latest
2. Lint and Format Check
3. Type Check
4. Code Coverage
5. Build Package
6. Test Python 3.13 on ubuntu-latest

**Why the branch update is mandatory:** with `strict: true`, GitHub refuses to merge the REL-12 PR
until its head branch is up to date with `main` — i.e. until the merge in D-08's handoff step has
happened and the merged head's own required checks are green. This pre-flight (Task 1) has already
measured that merge is conflict-free and its lock is valid.

## Merge-method precedent (D-08)

```
$ git log --first-parent --format='%h %s' origin/main | grep -E ' Merge pull request #(135|136) '
45962faa Merge pull request #136 from YuSabo90002/gsd/v0.9.2-inline-image-blocker-fix-and-release
9db2274c Merge pull request #135 from YuSabo90002/gsd/v0.9.1-windows-path-correctness
```
```
MERGE_PRECEDENT_HITS = 2
```

```
$ git log --first-parent --format='%h %s' -8 origin/main
cf3305ce Merge pull request #138 from YuSabo90002/dependabot/uv/ruff-0.16.6
293f0c26 Merge pull request #137 from YuSabo90002/chore/dependabot-uv-ecosystem
6181768f chore: remove REQUIREMENTS.md for v0.9.2 milestone
54bee8cc chore: archive v0.9.2 milestone files
45962faa Merge pull request #136 from YuSabo90002/gsd/v0.9.2-inline-image-blocker-fix-and-release
da93a231 docs: record the v0.9.1 branch merge in the close records
9db2274c Merge pull request #135 from YuSabo90002/gsd/v0.9.1-windows-path-correctness
d65a6122 chore: remove REQUIREMENTS.md for v0.9.0 milestone
```
Every prior milestone PR (#135, #136, and the two dependency PRs #137/#138 in between) merged with a
merge commit — never a squash or a rebase. The REL-12 PR follows the same method (D-08).

## Dependabot PRs (D-10)

Read-only `gh pr view` for each of #139..#142, at `PR_CENSUS_AT = 2026-09-12T22:50:42Z`:

| PR | State | Base | Head | Title | Updated |
|----|-------|------|------|-------|---------|
| #139 | OPEN | main | dependabot/uv/tox-4.61.4 | chore(deps): bump tox from 4.56.1 to 4.61.4 | 2026-09-12T13:39:27Z |
| #140 | OPEN | main | dependabot/uv/sphinx-intl-2.4.0 | chore(deps): bump sphinx-intl from 2.3.2 to 2.4.0 | 2026-09-12T13:39:26Z |
| #141 | OPEN | main | dependabot/uv/pre-commit-4.6.2 | chore(deps): bump pre-commit from 4.6.0 to 4.6.2 | 2026-09-12T13:39:27Z |
| #142 | OPEN | main | dependabot/uv/mypy-2.3.1 | chore(deps): bump mypy from 2.1.0 to 2.3.1 | 2026-09-12T13:39:22Z |

```
PR_CENSUS_AT = 2026-09-12T22:50:42Z
```

No merge, close, comment or rebase request was made against any of #139..#142 (D-10). Once REL-12
merges and changes `main`'s `uv.lock`, dependabot will rebase these PRs on its own schedule against
the new lock state.

## What the handoff can rely on

| Fact | Value | Key(s) |
|------|-------|--------|
| Conflict-free merge | `origin/main` merges into this branch with zero conflicts | `MERGE_RC = 0`, `MERGE_TREE` |
| Valid merged lock | `uv lock --check` passes against the merged `pyproject.toml`/`uv.lock` | `LOCK_CHECK_EXIT = 0` |
| Merged ruff version | 0.16.x — consistent with NIX-01 per 67-CONTEXT D-03, because NIX-01's binding sense is "the version `uv.lock` pins," and after REL-12 that pin is `main`'s | `MERGED_RUFF_LOCK_VERSION`, `MERGED_RUFF_RUN_VERSION` |
| Merged-tree lint result | Clean at the merged lock's own `ruff`/`black` versions, no FINDING needed | `MERGED_RUFF_EXIT = 0`, `MERGED_BLACK_EXIT = 0` |
| Strict protection, six checks | `strict: true`, exactly the six named contexts | `PROTECTION_STRICT = true`, `PROTECTION_CONTEXTS_COUNT = 6` |
| Merge-commit method | Every prior milestone PR (#135, #136) merged with a merge commit, never squash/rebase | `MERGE_PRECEDENT_HITS = 2` |
| PR census time | Read-only census of #139..#142, all left untouched | `PR_CENSUS_AT` |
