# Phase 71 — REL-13 Update-Step Pre-Flight (D-05, non-committing)

Nothing in this file is committed to the branch except the file itself, and no merge is performed.
Every command below was re-run live from this worktree during this plan's execution — no value is
copied from `71-CONTEXT.md` or `71-RESEARCH.md`.

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-13T08:45:19Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7407c28186c095e6

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
[... resolved and installed the dev + docs extras into this worktree's own .venv, including
typsphinx==0.9.2 from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7407c28186c095e6 ...]

$ uv --version
uv 0.12.13 (x86_64-unknown-linux-gnu)
```

Before any commit:

```
BASE_71_05 = 7a42bf996b1aaca24a8b17346be78459e6d41e2b
TRIAL_HEAD = 7a42bf996b1aaca24a8b17346be78459e6d41e2b
```

Both are `git rev-parse HEAD`, taken before this plan's first commit — the worktree branch check
recorded this same SHA as the fork base at spawn time.

```
START_CANONICAL = 7a42bf996b1aaca24a8b17346be78459e6d41e2b
```

From `git rev-parse gsd/v0.9.4-typing-modernization`, equal to `BASE_71_05` — this worktree forked
from the canonical ref's own tip.

```
$ mktemp -d
/tmp/tmp.X9Br1OkXSk
```

```
SCRATCH_71_05 = /tmp/tmp.X9Br1OkXSk
```

## Fetch and divergence

```
$ git fetch origin
(no output)

$ git rev-parse origin/main
d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

```
ORIGIN_MAIN_SHA = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

```
$ git log --oneline "$TRIAL_HEAD".."$ORIGIN_MAIN_SHA"
(no output)
```

```
MAIN_ONLY_COMMITS = 0
```

```
$ git rev-list --left-right --count "$ORIGIN_MAIN_SHA"...HEAD
0	114
```

`origin/main` carries 0 commits this worktree's `HEAD` lacks; this worktree's `HEAD` carries 114
commits `origin/main` lacks (the milestone's own work through wave 1).

```
$ git merge-base HEAD "$ORIGIN_MAIN_SHA"
d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

This equals `MILESTONE_BASE` (`d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d`) recorded in
`71-SC1-INVARIANTS.md` § "Milestone fences".

```
MAIN_MOVED = no
```

`ORIGIN_MAIN_SHA` equals `MILESTONE_BASE` exactly, so `main` has not moved since the milestone
branch forked — nothing to absorb, and constraint 4's dependabot-`ruff`-bump case does not apply
today. Task 2's merged-tree lint is run anyway, per SC#3.

## Trial merge

```
$ git merge-tree --write-tree "$TRIAL_HEAD" "$ORIGIN_MAIN_SHA"; echo "exit:$?"
0fc0c03a5fc3cb730542fde7a1c11f01b90205fe
exit:0
```

```
MERGE_RC = 0
MERGE_TREE = 0fc0c03a5fc3cb730542fde7a1c11f01b90205fe
```

A real tree SHA with exit code 0 means the trial merge is conflict-free.

**This tree SHA is valid only for these two inputs (`TRIAL_HEAD` and `ORIGIN_MAIN_SHA`) and must be
re-measured immediately before any real merge** — both refs are moving targets.

```
$ git merge-tree --write-tree "$TRIAL_HEAD" "$ORIGIN_MAIN_SHA"; echo "exit:$?"
0fc0c03a5fc3cb730542fde7a1c11f01b90205fe
exit:0
```

```
MERGE_TREE_REPRODUCED = yes
```

Running the same command a second time prints the same tree SHA (edge: idempotency).

```
$ git rev-parse "$TRIAL_HEAD^{tree}"
0fc0c03a5fc3cb730542fde7a1c11f01b90205fe
```

```
TRIAL_IS_NOOP = yes
```

`TRIAL_HEAD`'s own tree equals `MERGE_TREE` exactly. With `MAIN_MOVED = no` this must be `yes`:
`origin/main` only touches the branch at the merge-base, so there is nothing to absorb (D-05,
edge: adjacency).

## Merged lock

```
$ mkdir -p /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch
$ echo /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch
/tmp/tmp.X9Br1OkXSk/p7105_lock_scratch
```

```
$ git archive --format=tar -o /tmp/tmp.X9Br1OkXSk/p7105_lock_archive.tar "$MERGE_TREE" pyproject.toml uv.lock
(no output)
$ tar -xf /tmp/tmp.X9Br1OkXSk/p7105_lock_archive.tar -C /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch
(no output)
$ ls -la /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch
pyproject.toml
uv.lock
```

From the worktree root:

```
$ uv --directory /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch lock --check; echo "exit:$?"
Using CPython 3.14.4
Resolved 91 packages in 3ms
exit:0
```

```
LOCK_CHECK_EXIT = 0
LOCK_CHECK_UV_VERSION = uv 0.12.13
```

```
$ sed -n 7p /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch/pyproject.toml
version = "0.9.2"
```

```
MERGED_VERSION_LINE = version = "0.9.2"
```

```
$ grep -nE 'tox-uv|"ruff' /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch/pyproject.toml
38:    "tox-uv>=1.35,<2",
40:    "ruff>=0.15,<0.17",
```

```
$ grep -A1 -xF 'name = "ruff"' /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch/uv.lock
name = "ruff"
version = "0.16.6"
```

```
MERGED_RUFF_LOCK_VERSION = 0.16.6
```

```
$ grep -A1 -xF 'name = "ruff"' uv.lock
name = "ruff"
version = "0.16.6"
```

```
BRANCH_RUFF_LOCK_VERSION = 0.16.6
```

The branch's own lock already pins the same `ruff` version as the merged tree — expected, since
`MAIN_MOVED = no` means the merge absorbs nothing.

```
$ git show "$MERGE_TREE:CHANGELOG.md" | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' | grep -cE '^- \*\*'
4
```

```
MERGED_CHANGELOG_BOLD = 4
```

The merged tree's `## [Unreleased]` region carries exactly the four bold-lead bullets this
worktree's HEAD carries (the three v0.9.3 bullets plus 71-01's new fourth bullet) — the trial
merge includes this phase's own wave-1 CHANGELOG edit, as the task's `<precondition>` required.

```
$ rm -rf /tmp/tmp.X9Br1OkXSk/p7105_lock_scratch /tmp/tmp.X9Br1OkXSk/p7105_lock_archive.tar
(no output)
```

## Nothing moved

```
$ git rev-parse HEAD
7a42bf996b1aaca24a8b17346be78459e6d41e2b
```

Still equals `TRIAL_HEAD`, recorded before this plan's own commit of this evidence file.

```
$ git rev-parse gsd/v0.9.4-typing-modernization
7a42bf996b1aaca24a8b17346be78459e6d41e2b
```

Still equals `START_CANONICAL` — the orchestrator has not yet advanced the canonical ref past
this worktree's fork point.

```
$ git status --porcelain
(empty, before this plan's own commit of this evidence file)
```

```
$ git merge-base HEAD "$ORIGIN_MAIN_SHA"
d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

Still equals `MILESTONE_BASE` (D-05).

`git merge-tree --write-tree` added only unreferenced objects to the object store: HEAD and the
canonical ref are both unmoved, and `git status --porcelain` lists nothing until this evidence
file itself is written.

## Task 1 result

The merge `/gsd-complete-milestone` may run (`origin/main` into the milestone branch) is measured
conflict-free and reproducible from its recorded inputs, a no-op while `main` sits at the
milestone base, with a valid merged lock, and this branch is untouched by the measurement.

## Head check (Task 2)

```
$ test -f .git; echo "exit:$?"
exit:0
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7407c28186c095e6
$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
$ git fetch origin
(no output)
```

## Merged-tree lint

D-05 and SC#3 require this: the trial merge must pass `ruff check .` on the merged tree, at the
merged lock's `ruff`. `MAIN_MOVED = no`, so this is not constraint 4's case, and it still runs.

```
$ mkdir -p /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch
$ echo /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch
/tmp/tmp.X9Br1OkXSk/p7105_lint_scratch
$ git archive --format=tar -o /tmp/tmp.X9Br1OkXSk/p7105_lint_archive.tar "$MERGE_TREE"
(no output)
$ tar -xf /tmp/tmp.X9Br1OkXSk/p7105_lint_archive.tar -C /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch
(no output)
```

From the worktree root:

```
$ uv --directory /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch sync --locked --extra dev --no-install-project
[... hash-verified install from the merged uv.lock only, resolving packages including
ruff==0.16.6 ...]
```

This is a hash-verified install from the merged `uv.lock` only.

```
$ uv --directory /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch run --no-sync ruff --version
ruff 0.16.6
```

```
MERGED_RUFF_RUN_VERSION = 0.16.6
```

Equal to `MERGED_RUFF_LOCK_VERSION` recorded above.

```
$ uv --directory /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch run --no-sync ruff check .; echo "exit:$?"
All checks passed!
exit:0
```

```
MERGED_RUFF_EXIT = 0
```

```
$ uv --directory /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch run --no-sync black --check .; echo "exit:$?"
All done! ✨ 🍰 ✨
355 files would be left unchanged.
exit:0
```

```
MERGED_BLACK_EXIT = 0
```

```
$ rm -rf /tmp/tmp.X9Br1OkXSk/p7105_lint_scratch /tmp/tmp.X9Br1OkXSk/p7105_lint_archive.tar
(no output)
```

Both exits are 0 — no `## FINDING: merged-tree lint` section is needed. Nothing was fixed because
nothing failed.

## main protection (D-06)

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

**Why the handoff's branch-update step is conditional (D-06):** under `strict: true` the PR
cannot merge until the branch is up to date with `main`. If `main` has moved by the time the
handoff reaches this step, the trial merge above must be re-measured and the branch updated with
a merge commit before opening the PR; today (`MAIN_MOVED = no`), the step is a recorded no-op.

## Merge-method precedent (D-06)

```
$ git log --first-parent --format='%h %s' origin/main | grep -E ' Merge pull request #(135|136|143) '
58d578f2 Merge pull request #143 from YuSabo90002/gsd/v0.9.3-toolchain-and-dependency-update-repair
45962faa Merge pull request #136 from YuSabo90002/gsd/v0.9.2-inline-image-blocker-fix-and-release
9db2274c Merge pull request #135 from YuSabo90002/gsd/v0.9.1-windows-path-correctness
```

```
MERGE_PRECEDENT_HITS = 3
```

```
$ git log --first-parent --format='%h %s' -8 origin/main
d14ca458 Merge pull request #144 from YuSabo90002/docs/issue-91-close-and-doctest-todo
5d59dbb6 Merge pull request #139 from YuSabo90002/dependabot/uv/tox-4.61.4
31480b6b Merge pull request #140 from YuSabo90002/dependabot/uv/sphinx-intl-2.4.0
cf6856c6 Merge pull request #141 from YuSabo90002/dependabot/uv/pre-commit-4.6.2
fd0c24f7 Merge pull request #142 from YuSabo90002/dependabot/uv/mypy-2.3.1
4dfdd664 chore: remove REQUIREMENTS.md for v0.9.3 milestone
d0e2f4e0 chore: archive v0.9.3 milestone files
58d578f2 Merge pull request #143 from YuSabo90002/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

Every prior milestone PR (#135, #136, #143) and every dependabot/docs PR reaching `main` in
between merged with a merge commit — never a squash or a rebase. The REL-13 PR follows the same
method (D-06).

## Open pull requests (D-12)

```
$ gh pr list --state all --limit 5 --json number
[{"number":144},{"number":143},{"number":142},{"number":141},{"number":140}]
```

Positive control: the unscoped listing returns five real PR numbers — proving the command
reached GitHub and the repository genuinely has PR history.

```
$ date -u +%FT%TZ
2026-09-13T08:48:59Z
```

```
PR_CENSUS_AT = 2026-09-13T08:48:59Z
```

```
$ gh pr list --state open --json number,title,author,headRefName,baseRefName,updatedAt
[]
```

```
OPEN_PRS = 0
DEPENDABOT_OPEN_PRS = 0
```

No pull request is open at census time, so no row is tabulated. No merge, close, comment or
rebase request was made against any pull request (D-12). A dependabot `ruff` bump merged to
`main` after this census is caught by the handoff's re-run of the trial merge.

## What the handoff can rely on

| Fact | Value | Key(s) |
|------|-------|--------|
| Conflict-free merge, no-op | `origin/main` merges into this branch with zero conflicts; nothing to absorb today | `MERGE_RC = 0`, `MERGE_TREE`, `TRIAL_IS_NOOP = yes` |
| Valid merged lock | `uv lock --check` passes against the merged `pyproject.toml`/`uv.lock` | `LOCK_CHECK_EXIT = 0` |
| Merged ruff version and lint result | 0.16.6; clean at that version | `MERGED_RUFF_LOCK_VERSION = 0.16.6`, `MERGED_RUFF_RUN_VERSION = 0.16.6`, `MERGED_RUFF_EXIT = 0`, `MERGED_BLACK_EXIT = 0` |
| Strict protection, six checks | `strict: true`, exactly the six named contexts | `PROTECTION_STRICT = true`, `PROTECTION_CONTEXTS_COUNT = 6` |
| Merge-commit method | Every prior milestone PR (#135, #136, #143) merged with a merge commit, never squash/rebase | `MERGE_PRECEDENT_HITS = 3` |
| PR census time and result | No open PR at census time, left untouched | `PR_CENSUS_AT`, `OPEN_PRS = 0`, `DEPENDABOT_OPEN_PRS = 0` |

```
TRIAL_MERGE_VERDICT = MET
```

`MERGE_RC`, `LOCK_CHECK_EXIT`, `MERGED_RUFF_EXIT` and `MERGED_BLACK_EXIT` are all `0`.
