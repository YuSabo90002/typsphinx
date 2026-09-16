# Phase 73 — REL-14 Update-Step Pre-Flight (D-09, non-committing)

Nothing in this file is committed to the branch except the file itself, no merge is performed, and
no value is copied from `73-CONTEXT.md` or `73-RESEARCH.md`. Every command below was re-run live
from this worktree during this plan's execution.

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-16T10:13:33Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9698df66160af27c

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
[... resolved and installed the dev + docs extras into this worktree's own .venv, including
typsphinx==0.9.2 from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9698df66160af27c ...]

$ uv --version
uv 0.12.13 (x86_64-unknown-linux-gnu)
```

Before any commit:

```
BASE_73_05 = a54a2d8a3b06b388c7ee004e5cfbe3405431421d
TRIAL_HEAD = a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

Both are `git rev-parse HEAD`, taken before this plan's first commit.

```
$ git rev-parse gsd/v0.9.5-docs-link-check-and-navigation
a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

```
START_CANONICAL = a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

Equal to `BASE_73_05` — this worktree forked from the canonical ref's own tip.

```
$ mktemp -d
/tmp/tmp.nxzTyUJGQS
```

```
SCRATCH_73_05 = /tmp/tmp.nxzTyUJGQS
```

## Fetch and divergence

```
$ git fetch origin
(no output)

$ git rev-parse origin/main
6e2b789922207eb72e7aef3216fdfd924dd4bcd9
```

```
ORIGIN_MAIN_SHA = 6e2b789922207eb72e7aef3216fdfd924dd4bcd9
```

```
$ git log --oneline "$TRIAL_HEAD".."$ORIGIN_MAIN_SHA"
6e2b7899 Merge pull request #146 from YuSabo90002/dependabot/uv/build-1.6.1
52aa8ec9 chore(deps): bump build from 1.5.0 to 1.6.1
96162f3a Merge pull request #148 from YuSabo90002/dependabot/uv/pypdf-6.18.0
daa63270 chore(deps): bump pypdf from 6.14.2 to 6.18.1
5bb304c1 Merge pull request #147 from YuSabo90002/dependabot/uv/ruff-0.16.7
e7c7e9b6 Merge branch 'main' into dependabot/uv/ruff-0.16.7
81cc2b3e Merge pull request #149 from YuSabo90002/dependabot/uv/twine-7.0.0
8ac0f05f chore(deps): bump ruff from 0.16.6 to 0.16.7
44b1f98e Merge branch 'main' into dependabot/uv/twine-7.0.0
a32e0be2 Merge pull request #150 from YuSabo90002/dependabot/uv/sphinx-autodoc-typehints-3.13.6
eb4efbc4 chore(deps): bump sphinx-autodoc-typehints from 3.0.1 to 3.13.6
6dee9d08 chore(deps): bump twine from 6.2.0 to 7.0.0

$ git log --oneline "$TRIAL_HEAD".."$ORIGIN_MAIN_SHA" | wc -l
12
```

```
MAIN_ONLY_COMMITS = 12
```

```
$ git rev-list --left-right --count "$ORIGIN_MAIN_SHA"...HEAD
12	69
```

`origin/main` carries 12 commits this worktree's `HEAD` lacks — all five Dependabot pull requests
(#146, #147, #148, #149, #150) have merged into `main` since the milestone branch forked. This
worktree's `HEAD` carries 69 commits `origin/main` lacks (this milestone's own work through
wave 1).

```
$ git merge-base HEAD "$ORIGIN_MAIN_SHA"
098a8ff64cf008822eef9dc69f75102ded3f7bc1
```

This equals `MILESTONE_BASE` (`098a8ff64cf008822eef9dc69f75102ded3f7bc1`) recorded in
`73-SC1-INVARIANTS.md` § "Milestone fences" — this branch has not absorbed any of `main`'s later
commits, and `main`'s later commits have not been rebased into this branch's history either.

```
MAIN_MOVED = yes
```

`ORIGIN_MAIN_SHA` differs from `MILESTONE_BASE` — `main` has moved. This is D-07's case: a
Dependabot pull request landed on `main` between planning and execution.

**Commit-by-commit against `uv.lock` and the `pyproject.toml` `ruff` pin:**

```
$ git log --oneline --name-only "$TRIAL_HEAD".."$ORIGIN_MAIN_SHA" -- uv.lock pyproject.toml
52aa8ec9 chore(deps): bump build from 1.5.0 to 1.6.1
uv.lock
daa63270 chore(deps): bump pypdf from 6.14.2 to 6.18.1
uv.lock
e7c7e9b6 Merge branch 'main' into dependabot/uv/ruff-0.16.7
8ac0f05f chore(deps): bump ruff from 0.16.6 to 0.16.7
uv.lock
44b1f98e Merge branch 'main' into dependabot/uv/twine-7.0.0
eb4efbc4 chore(deps): bump sphinx-autodoc-typehints from 3.0.1 to 3.13.6
uv.lock
6dee9d08 chore(deps): bump twine from 6.2.0 to 7.0.0
uv.lock
```

Every one of the five merged Dependabot commits touches `uv.lock` only — none touches
`pyproject.toml`, so no dependency range (including the `ruff>=0.15,<0.17` range) changed. The
`ruff` bump (#147, `0.16.6 -> 0.16.7`) is exactly the case D-07 names: the merged tree's lint at
the merged lock's `ruff` version is authoritative below (Task 2), and the handoff's branch-update
step is live rather than a no-op.

## Trial merge

```
$ git merge-tree --write-tree "$TRIAL_HEAD" "$ORIGIN_MAIN_SHA"; echo "exit:$?"
228dc64ea867e2f993b97229faf6607774ed39c6
exit:0
```

```
MERGE_RC = 0
MERGE_TREE = 228dc64ea867e2f993b97229faf6607774ed39c6
```

A real tree SHA with exit code 0 means the trial merge is conflict-free.

**This tree SHA is valid only for these two inputs (`TRIAL_HEAD` and `ORIGIN_MAIN_SHA`) and must be
re-measured immediately before any real merge** — both refs are moving targets, and `main` has
already moved once during this phase's own execution window.

```
$ git merge-tree --write-tree "$TRIAL_HEAD" "$ORIGIN_MAIN_SHA"; echo "exit:$?"
228dc64ea867e2f993b97229faf6607774ed39c6
exit:0
```

```
MERGE_TREE_REPRODUCED = yes
```

Running the same command a second time prints the same tree SHA (edge: idempotency).

```
$ git rev-parse "$TRIAL_HEAD^{tree}"
80c79cce117977dff4b7e47eef7465aed73cba1b
```

```
TRIAL_IS_NOOP = no
```

`TRIAL_HEAD`'s own tree (`80c79cce...`) differs from `MERGE_TREE` (`228dc64e...`) — with
`MAIN_MOVED = yes` this is expected: `origin/main` carries content beyond the merge-base that the
trial merge absorbs (D-09, edges: adjacency and empty do not apply here since `main` did move).

## Merged lock

```
$ mkdir -p /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch
$ echo /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch
/tmp/tmp.nxzTyUJGQS/p7305_lock_scratch
```

```
$ git archive --format=tar -o /tmp/tmp.nxzTyUJGQS/p7305_lock_archive.tar "$MERGE_TREE" pyproject.toml uv.lock
(no output)
$ tar -xf /tmp/tmp.nxzTyUJGQS/p7305_lock_archive.tar -C /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch
(no output)
$ ls -la /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch
pyproject.toml
uv.lock
```

From the worktree root:

```
$ uv --directory /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch lock --check; echo "exit:$?"
Using CPython 3.14.4
Resolved 91 packages in 7ms
exit:0
```

```
LOCK_CHECK_EXIT = 0
LOCK_CHECK_UV_VERSION = uv 0.12.13
```

```
$ sed -n 7p /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch/pyproject.toml
version = "0.9.2"
```

```
MERGED_VERSION_LINE = version = "0.9.2"
```

The merged `pyproject.toml:7` still reads `0.9.2` — no version bump landed via the merge.

```
$ grep -A1 -xF 'name = "ruff"' /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch/uv.lock
name = "ruff"
version = "0.16.7"
```

```
MERGED_RUFF_LOCK_VERSION = 0.16.7
```

```
$ grep -A1 -xF 'name = "ruff"' uv.lock
name = "ruff"
version = "0.16.6"
```

```
BRANCH_RUFF_LOCK_VERSION = 0.16.6
```

The merged tree's lock carries `ruff` `0.16.7` (from #147), one patch version ahead of this
branch's own `0.16.6` — exactly the D-07 case: `main` moved and the merge absorbs the Dependabot
`ruff` bump.

```
$ git show "$MERGE_TREE:CHANGELOG.md" | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' | grep -cE '^- \*\*'
6
```

```
MERGED_CHANGELOG_BOLD = 6
```

The merged tree's `## [Unreleased]` region carries exactly the six bold-lead bullets this
worktree's HEAD carries (one `### Added`, four `### Changed`, one `### Fixed`) — the trial merge
includes this phase's own wave-1 CHANGELOG edit, as the task's `<precondition>` required. `main`'s
own commits touch no CHANGELOG heading.

```
$ rm -rf /tmp/tmp.nxzTyUJGQS/p7305_lock_scratch /tmp/tmp.nxzTyUJGQS/p7305_lock_archive.tar
(no output)
```

## Nothing moved

```
$ git rev-parse HEAD
a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

Still equals `TRIAL_HEAD`, recorded before this plan's own commit of this evidence file.

```
$ git rev-parse gsd/v0.9.5-docs-link-check-and-navigation
a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

Still equals `START_CANONICAL` — the orchestrator has not yet advanced the canonical ref past
this worktree's fork point.

```
$ git status --porcelain
(empty, before this plan's own commit of this evidence file)
```

```
$ git merge-base HEAD "$ORIGIN_MAIN_SHA"
098a8ff64cf008822eef9dc69f75102ded3f7bc1
```

Still equals `MILESTONE_BASE`.

`git merge-tree --write-tree` added only unreferenced objects to the object store: HEAD and the
canonical ref are both unmoved, and `git status --porcelain` lists nothing until this evidence
file itself is written.

## Task 1 result

The merge `/gsd-complete-milestone` will run (`origin/main` into the milestone branch) is measured
conflict-free and reproducible from its recorded inputs. It is **not** a no-op: `main` moved by
absorbing all five Dependabot pull requests (#146–#150) between planning and this plan's
execution — D-07's case, caught live rather than assumed. The merged lock is valid, and this
branch is untouched by the measurement.

## Head check (Task 2)

```
$ test -f .git; echo "exit:$?"
exit:0
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9698df66160af27c
$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
$ git fetch origin
(no output)
```

## Merged-tree lint

D-09 and SC#3 require this: the trial merge must pass `ruff check .` on the merged tree, at the
merged lock's `ruff`. `MAIN_MOVED = yes` here (D-07's case — `main` absorbed the `ruff` bump from
#147), so under D-07 this count is authoritative for the conditional branch update.

```
$ mkdir -p /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch
$ echo /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch
/tmp/tmp.nxzTyUJGQS/p7305_lint_scratch
$ git archive --format=tar -o /tmp/tmp.nxzTyUJGQS/p7305_lint_archive.tar "$MERGE_TREE"
(no output)
$ tar -xf /tmp/tmp.nxzTyUJGQS/p7305_lint_archive.tar -C /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch
(no output)
```

From the worktree root:

```
$ uv --directory /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch sync --locked --extra dev --no-install-project
[... hash-verified install from the merged uv.lock only, resolving packages including
ruff==0.16.7 ...]
```

This is a hash-verified install from the merged `uv.lock` only.

```
$ uv --directory /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch run --no-sync ruff --version
ruff 0.16.7
```

```
MERGED_RUFF_RUN_VERSION = 0.16.7
```

Equal to `MERGED_RUFF_LOCK_VERSION` recorded above.

```
$ uv --directory /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch run --no-sync ruff check .; echo "exit:$?"
All checks passed!
exit:0
```

```
MERGED_RUFF_EXIT = 0
```

```
$ uv --directory /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch run --no-sync black --check .; echo "exit:$?"
All done! ✨ 🍰 ✨
355 files would be left unchanged.
exit:0
```

```
MERGED_BLACK_EXIT = 0
```

```
$ rm -rf /tmp/tmp.nxzTyUJGQS/p7305_lint_scratch /tmp/tmp.nxzTyUJGQS/p7305_lint_archive.tar
(no output)
```

Both exits are 0 — no `## FINDING: merged-tree lint` section is needed. Nothing was fixed because
nothing failed. The merged tree — which now includes the `ruff` 0.16.6 -> 0.16.7 bump from #147 —
lints cleanly at that bumped version. No documentation build of the merged tree was run (D-07).

## main protection (D-09)

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict
true
```

```
PROTECTION_STRICT = true
```

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '[.contexts[]] | sort | join("|")'
Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

```
PROTECTION_CONTEXTS = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
PROTECTION_CONTEXTS_COUNT = 6
```

The six required contexts, verbatim:
1. Build Package
2. Code Coverage
3. Lint and Format Check
4. Test Python 3.12 on ubuntu-latest
5. Test Python 3.13 on ubuntu-latest
6. Type Check

This equals `REQUIRED_CONTEXTS_HEAD` in `72-BASE-EVIDENCE.md` exactly.

**Why the handoff's branch-update step is conditional (D-10):** under `strict: true` the pull
request cannot merge until the branch is up to date with `main`. `main` has already moved by the
time this plan reaches this step (`MAIN_MOVED = yes`, Task 1), so the trial merge above must be
re-measured immediately before the real merge and the branch updated with a merge commit before
opening the pull request. Had `main` not moved, this step would instead be a recorded no-op.

## Merge-method precedent (D-10)

```
$ git log --first-parent --format='%h %s' origin/main | grep -E ' Merge pull request #(143|145) '
383a07e9 Merge pull request #145 from YuSabo90002/gsd/v0.9.4-typing-modernization
58d578f2 Merge pull request #143 from YuSabo90002/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

```
MERGE_PRECEDENT_HITS = 2
```

```
$ git log --first-parent --format='%h %s' -12 origin/main
6e2b7899 Merge pull request #146 from YuSabo90002/dependabot/uv/build-1.6.1
96162f3a Merge pull request #148 from YuSabo90002/dependabot/uv/pypdf-6.18.0
5bb304c1 Merge pull request #147 from YuSabo90002/dependabot/uv/ruff-0.16.7
81cc2b3e Merge pull request #149 from YuSabo90002/dependabot/uv/twine-7.0.0
a32e0be2 Merge pull request #150 from YuSabo90002/dependabot/uv/sphinx-autodoc-typehints-3.13.6
098a8ff6 chore: remove REQUIREMENTS.md for v0.9.4 milestone
95ba4862 chore: archive v0.9.4 milestone files
383a07e9 Merge pull request #145 from YuSabo90002/gsd/v0.9.4-typing-modernization
d14ca458 Merge pull request #144 from YuSabo90002/docs/issue-91-close-and-doctest-todo
5d59dbb6 Merge pull request #139 from YuSabo90002/dependabot/uv/tox-4.61.4
31480b6b Merge pull request #140 from YuSabo90002/dependabot/uv/sphinx-intl-2.4.0
cf6856c6 Merge pull request #141 from YuSabo90002/dependabot/uv/pre-commit-4.6.2
```

Both previous milestone pull requests (#143, v0.9.3; #145, v0.9.4) merged with a merge commit,
never a squash or a rebase — visible on `origin/main`'s first-parent history above. At the v0.9.3
close, Dependabot pull requests merged after #143 (#142, #141, visible further back in the same
history). This milestone's own five Dependabot pull requests (#146-#150) have now already merged
after #145, the v0.9.4 milestone pull request, following the same order.

## Dependabot and open pull requests (D-06)

```
$ gh pr list --state all --limit 5 --json number
[{"number":150},{"number":149},{"number":148},{"number":147},{"number":146}]
```

Positive control: the unscoped listing returns five real pull-request numbers — proving the
command reached GitHub and the repository genuinely has pull-request history.

```
$ gh pr list --state open --json number,title,author,headRefName,baseRefName,updatedAt
[]
```

```
$ gh api user -q .login
YuSabo90002
```

```
GH_ACTOR = YuSabo90002
```

```
$ date -u +%FT%TZ
2026-09-16T10:17:02Z
```

```
PR_CENSUS_AT = 2026-09-16T10:17:02Z
```

No pull request is open at census time — all five of #146-#150 have already merged into `main`
since planning (measured live in Task 1's `## Fetch and divergence`, `MAIN_MOVED = yes`). Each is
recorded below from its own `gh pr view`, not from the open listing:

```
$ gh pr view 146 --json number,title,state,author,headRefName,baseRefName,files,mergeable,updatedAt
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","files":[{"path":"uv.lock","additions":3,"deletions":3,"changeType":"MODIFIED"}],"headRefName":"dependabot/uv/build-1.6.1","mergeable":"UNKNOWN","number":146,"state":"MERGED","title":"chore(deps): bump build from 1.5.0 to 1.6.1","updatedAt":"2026-09-14T16:04:02Z"}

$ gh pr view 146 --json comments,reviews -q '[.comments[], .reviews[] | select(.author.login == "YuSabo90002")] | length'
0
```

```
PR_146_STATE = MERGED
PR_146_PACKAGE = build
PR_146_RANGE = 1.5.0 -> 1.6.1
PR_146_FILES = uv.lock
PR_146_ACTOR_TOUCHES = 0
```

```
$ gh pr view 147 --json number,title,state,author,headRefName,baseRefName,files,mergeable,updatedAt
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","files":[{"path":"uv.lock","additions":21,"deletions":21,"changeType":"MODIFIED"}],"headRefName":"dependabot/uv/ruff-0.16.7","mergeable":"UNKNOWN","number":147,"state":"MERGED","title":"chore(deps): bump ruff from 0.16.6 to 0.16.7","updatedAt":"2026-09-14T15:40:42Z"}

$ gh pr view 147 --json comments,reviews -q '[.comments[], .reviews[] | select(.author.login == "YuSabo90002")] | length'
0
```

```
PR_147_STATE = MERGED
PR_147_PACKAGE = ruff
PR_147_RANGE = 0.16.6 -> 0.16.7
PR_147_FILES = uv.lock
PR_147_ACTOR_TOUCHES = 0
```

```
$ gh pr view 148 --json number,title,state,author,headRefName,baseRefName,files,mergeable,updatedAt
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","files":[{"path":"uv.lock","additions":3,"deletions":3,"changeType":"MODIFIED"}],"headRefName":"dependabot/uv/pypdf-6.18.0","mergeable":"UNKNOWN","number":148,"state":"MERGED","title":"chore(deps): bump pypdf from 6.14.2 to 6.18.1","updatedAt":"2026-09-14T15:52:06Z"}

$ gh pr view 148 --json comments,reviews -q '[.comments[], .reviews[] | select(.author.login == "YuSabo90002")] | length'
0
```

```
PR_148_STATE = MERGED
PR_148_PACKAGE = pypdf
PR_148_RANGE = 6.14.2 -> 6.18.1
PR_148_FILES = uv.lock
PR_148_ACTOR_TOUCHES = 0
```

```
$ gh pr view 149 --json number,title,state,author,headRefName,baseRefName,files,mergeable,updatedAt
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","files":[{"path":"uv.lock","additions":3,"deletions":3,"changeType":"MODIFIED"}],"headRefName":"dependabot/uv/twine-7.0.0","mergeable":"UNKNOWN","number":149,"state":"MERGED","title":"chore(deps): bump twine from 6.2.0 to 7.0.0","updatedAt":"2026-09-14T15:18:49Z"}

$ gh pr view 149 --json comments,reviews -q '[.comments[], .reviews[] | select(.author.login == "YuSabo90002")] | length'
0
```

```
PR_149_STATE = MERGED
PR_149_PACKAGE = twine
PR_149_RANGE = 6.2.0 -> 7.0.0
PR_149_FILES = uv.lock
PR_149_ACTOR_TOUCHES = 0
```

```
$ gh pr view 150 --json number,title,state,author,headRefName,baseRefName,files,mergeable,updatedAt
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","files":[{"path":"uv.lock","additions":3,"deletions":3,"changeType":"MODIFIED"}],"headRefName":"dependabot/uv/sphinx-autodoc-typehints-3.13.6","mergeable":"UNKNOWN","number":150,"state":"MERGED","title":"chore(deps): bump sphinx-autodoc-typehints from 3.0.1 to 3.13.6","updatedAt":"2026-09-14T15:13:56Z"}

$ gh pr view 150 --json comments,reviews -q '[.comments[], .reviews[] | select(.author.login == "YuSabo90002")] | length'
0
```

```
PR_150_STATE = MERGED
PR_150_PACKAGE = sphinx-autodoc-typehints
PR_150_RANGE = 3.0.1 -> 3.13.6
PR_150_FILES = uv.lock
PR_150_ACTOR_TOUCHES = 0
```

| Pull request | Package | Range | State | Files | Actor touches |
|---|---|---|---|---|---|
| #146 | build | 1.5.0 -> 1.6.1 | MERGED | uv.lock | 0 |
| #147 | ruff | 0.16.6 -> 0.16.7 | MERGED | uv.lock | 0 |
| #148 | pypdf | 6.14.2 -> 6.18.1 | MERGED | uv.lock | 0 |
| #149 | twine | 6.2.0 -> 7.0.0 | MERGED | uv.lock | 0 |
| #150 | sphinx-autodoc-typehints | 3.0.1 -> 3.13.6 | MERGED | uv.lock | 0 |

No other pull request is open.

```
OPEN_PRS = 0
DEPENDABOT_OPEN_PRS = 0
```

No merge, close, comment, review, label or rebase request was made against any of #146-#150, or
any other pull request (D-06). All five of #146-#150 merged outside this phase — before this
plan's own execution began — confirmed above with `MAIN_MOVED = yes` in Task 1 (D-07). The order
the handoff records held here too: the milestone pull request (#145) merged first, then the
Dependabot pull requests (#146-#150) rebased and merged themselves in sequence afterward — no
manual action from this phase or its plans was needed or taken.

## What the handoff can rely on

| Fact | Value | Key(s) |
|------|-------|--------|
| Conflict-free merge, not a no-op | `origin/main` merges into this branch with zero conflicts; `main` moved by absorbing all five Dependabot pull requests | `MERGE_RC = 0`, `MERGE_TREE`, `TRIAL_IS_NOOP = no`, `MAIN_MOVED = yes` |
| Valid merged lock | `uv lock --check` passes against the merged `pyproject.toml`/`uv.lock` | `LOCK_CHECK_EXIT = 0` |
| Merged ruff version and lint result | 0.16.7 (bumped from 0.16.6 by #147); clean at that version | `MERGED_RUFF_LOCK_VERSION = 0.16.7`, `MERGED_RUFF_RUN_VERSION = 0.16.7`, `MERGED_RUFF_EXIT = 0`, `MERGED_BLACK_EXIT = 0` |
| Strict protection, six checks | `strict: true`, exactly the six named contexts, equal to Phase 72's base reading | `PROTECTION_STRICT = true`, `PROTECTION_CONTEXTS_COUNT = 6` |
| Merge-commit method | Both prior milestone pull requests (#143, #145) merged with a merge commit, never squash/rebase | `MERGE_PRECEDENT_HITS = 2` |
| Dependabot census time and result | Zero open at census time; all five already merged outside this phase, untouched by it | `PR_CENSUS_AT`, `OPEN_PRS = 0`, `DEPENDABOT_OPEN_PRS = 0` |

```
TRIAL_MERGE_VERDICT = MET
```

`MERGE_RC`, `LOCK_CHECK_EXIT`, `MERGED_RUFF_EXIT` and `MERGED_BLACK_EXIT` are all `0`.
