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
