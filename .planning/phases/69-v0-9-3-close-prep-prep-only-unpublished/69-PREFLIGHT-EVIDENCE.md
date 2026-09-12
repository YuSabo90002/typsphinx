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
