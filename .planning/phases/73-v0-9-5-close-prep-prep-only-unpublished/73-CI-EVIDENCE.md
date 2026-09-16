# Phase 73 — CI Evidence (D-12, SC#3 CI half)

Recorded inside this plan's isolated worktree (`worktree-agent-a2740f7c01295f306`).

```
BASE_73_04 = a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

```
SCRATCH_73_04 = /tmp/tmp.vuePWTLiOc
```

## Head check and provisioning

`date -u +%FT%TZ`:
```
2026-09-16T10:12:19Z
```

`pwd -P`:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2740f7c01295f306
```

`test -f .git; echo "exit:$?"`:
```
exit:0
```

`grep -c typsphinx-fhs-run "$(command -v uv)"`:
```
2
```

Provisioning command:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```
Ran to completion; final resolved lines included `typsphinx==0.9.2 (from
file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2740f7c01295f306)`, `ruff==0.16.6`,
`tox-uv==1.36.0`, `uv==0.12.13`.

Same provisioning line with `--locked` appended:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13 --locked
```
```
Resolved 91 packages in 4ms
Checked 90 packages in 0.63ms
exit:0
```
The lock is in sync; every `ci.yml` job's own `uv sync --extra dev --locked` will not fail on a
stale lock before any signal.

`git rev-parse HEAD` (before any commit, recorded as `BASE_73_04` above):
```
a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

`mktemp -d` (recorded as `SCRATCH_73_04` above):
```
/tmp/tmp.vuePWTLiOc
```

## Wave-1 gate

`git show gsd/v0.9.5-docs-link-check-and-navigation:CHANGELOG.md`, the `## [Unreleased]` region
(everything between `## [Unreleased]` and `## [0.9.2]`):

```
$ git show gsd/v0.9.5-docs-link-check-and-navigation:CHANGELOG.md | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' | grep -E '^### '
### Added
### Changed
### Fixed
### Planned for Future Releases
```

```
$ git show gsd/v0.9.5-docs-link-check-and-navigation:CHANGELOG.md | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' | grep -E '^- \*\*' | wc -l
6
```

Headings appear in the required order (`### Added`, `### Changed`, `### Fixed`), and there are
six bold bullets in that region — the two new bullets introduced this milestone (the `tox -e
linkcheck` bullet and the sidebar-toctree-dedup bullet) plus the four bullets carried from
v0.9.4/v0.9.3.

The two required spans are present:
```
$ git show gsd/v0.9.5-docs-link-check-and-navigation:CHANGELOG.md | grep -n 'QUA-13, DOC-24)\.\*\*\|DOC-18)\.\*\*'
13:  their `#anchor` targets (QUA-13, DOC-24).** It runs Sphinx's link-check builder over the
58:  once, nested under its section (DOC-18).** Previously each of those pages was also listed
```

`git cat-file -e` of `73-SC1-INVARIANTS.md` at the canonical ref:
```
$ git cat-file -e gsd/v0.9.5-docs-link-check-and-navigation:.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md; echo "exit:$?"
exit:0
```

Absence of a `## HALT` heading in `73-CHANGELOG-EVIDENCE.md` and `73-CLOSEOUT-GUARD.md` at the
canonical ref:
```
$ git show gsd/v0.9.5-docs-link-check-and-navigation:.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CHANGELOG-EVIDENCE.md | grep -c '^## HALT'
0

$ git show gsd/v0.9.5-docs-link-check-and-navigation:.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CLOSEOUT-GUARD.md | grep -c '^## HALT'
0
```

Wave-1 gate holds — no `## HALT` heading anywhere checked. The push proceeds.

## Tip identity and fence

`MILESTONE_BASE`, read from `73-SC1-INVARIANTS.md`:
```
$ sed -n "s/^MILESTONE_BASE = //p" .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md | head -n1
098a8ff64cf008822eef9dc69f75102ded3f7bc1
```

```
$ git rev-parse gsd/v0.9.5-docs-link-check-and-navigation
a54a2d8a3b06b388c7ee004e5cfbe3405431421d

$ git log --oneline -1 a54a2d8a3b06b388c7ee004e5cfbe3405431421d
a54a2d8a docs(phase-73): update tracking after wave 1
```

Key line:
```
PUSHED_SHA = a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```

`PUSHED_SHA` equals `BASE_73_04` — this worktree's own fork base already carried wave 1's merged
commits and wave 2's own tracking-update commit before this plan started.

```
$ git diff --name-only HEAD a54a2d8a3b06b388c7ee004e5cfbe3405431421d -- . ':(exclude).planning'
(empty)
```
The pushed product tree equals this worktree's HEAD, outside `.planning/`.

```
$ git show a54a2d8a3b06b388c7ee004e5cfbe3405431421d:pyproject.toml | sed -n 7p
version = "0.9.2"
```

```
$ git diff --name-only 098a8ff64cf008822eef9dc69f75102ded3f7bc1 a54a2d8a3b06b388c7ee004e5cfbe3405431421d -- typsphinx/ .github/workflows/
(empty)
```
No `typsphinx/` or `.github/workflows/` change since `MILESTONE_BASE` (D-13; constraints 2 and 3).

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base a54a2d8a3b06b388c7ee004e5cfbe3405431421d origin/main
098a8ff64cf008822eef9dc69f75102ded3f7bc1
```
Equal to `MILESTONE_BASE` — no `main` commit was absorbed.

```
$ git tag --points-at a54a2d8a3b06b388c7ee004e5cfbe3405431421d
(empty)
```
No tag rides along at the pushed tip.

```
$ git show a54a2d8a3b06b388c7ee004e5cfbe3405431421d:uv.lock | grep -A1 -xF 'name = "ruff"'
name = "ruff"
version = "0.16.6"
```

Key line:
```
LOCK_RUFF_VERSION = 0.16.6
```

## Decoy census (D-12)

Run immediately before the push, with nothing but the "Tip identity and fence" measurements
above in between.

```
$ git branch --list 'gsd/v0.9.5*' -v
+ gsd/v0.9.5-docs-link-check-and-navigation a54a2d8a [ahead 29] docs(phase-73): update tracking after wave 1

$ git ls-remote --heads origin 'gsd/v0.9.5*'
0b2595df21399363f50e5e1a55935f470e0df00d	refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
```

Only the canonical `gsd/v0.9.5-docs-link-check-and-navigation` appears — locally and on origin.
The decoy `gsd/v0.9.5-milestone` exists nowhere. Census result: no decoy anywhere; nothing is
deleted.

## Push

```
$ git fetch origin gsd/v0.9.5-docs-link-check-and-navigation
From https://github.com/YuSabo90002/typsphinx
 * branch              gsd/v0.9.5-docs-link-check-and-navigation -> FETCH_HEAD

$ git ls-remote --heads origin refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
0b2595df21399363f50e5e1a55935f470e0df00d	refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
```

Key line:
```
ORIGIN_BEFORE = 0b2595df21399363f50e5e1a55935f470e0df00d
```

```
$ git merge-base --is-ancestor 0b2595df21399363f50e5e1a55935f470e0df00d a54a2d8a3b06b388c7ee004e5cfbe3405431421d; echo "exit:$?"
exit:0

$ git merge-base --is-ancestor 0b2595df21399363f50e5e1a55935f470e0df00d a54a2d8a3b06b388c7ee004e5cfbe3405431421d; echo "exit:$?"
exit:0
```
`ORIGIN_BEFORE` and Phase 72's pushed tip (both `0b2595df21399363f50e5e1a55935f470e0df00d`, the
same commit) are ancestors of `PUSHED_SHA` — a fast-forward.

```
$ git config --get push.followTags; echo "exit:$?"
exit:1
```
Unset.

```
$ git config --get branch.gsd/v0.9.5-docs-link-check-and-navigation.remote
origin
```

Key line:
```
PUSH_AT = 2026-09-16T10:13:28Z
```

```
$ git push --no-follow-tags origin gsd/v0.9.5-docs-link-check-and-navigation
To https://github.com/YuSabo90002/typsphinx.git
   0b2595df..a54a2d8a  gsd/v0.9.5-docs-link-check-and-navigation -> gsd/v0.9.5-docs-link-check-and-navigation
```
No pull-request hint was printed on this push (the branch already existed on origin from Phase
72's first push); nothing is acted on regardless.

Post-push checks:
```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
a54a2d8a3b06b388c7ee004e5cfbe3405431421d	refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
```
Origin head now equals `PUSHED_SHA`.

```
$ git ls-remote --tags origin | grep -E 'refs/tags/v0\.9\.[2345]'
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}
```
Only `v0.9.2` is present; no `v0.9.3`, `v0.9.4` or `v0.9.5` tag.

## Dispatch

```
$ gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation
https://github.com/YuSabo90002/typsphinx/actions/runs/35083828156
exit:0
```
Issued exactly once; no HTTP 5xx was returned, so no retry or second attempt was needed.

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.5-docs-link-check-and-navigation --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-16T10:13:43Z","databaseId":35083828156,"headSha":"a54a2d8a3b06b388c7ee004e5cfbe3405431421d","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/35083828156"},{"createdAt":"2026-09-13T14:01:06Z","databaseId":34761445288,"headSha":"0b2595df21399363f50e5e1a55935f470e0df00d","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34761445288"}]
```
The first row's `headSha` equals `PUSHED_SHA`, and its `createdAt` (10:13:43Z) follows `PUSH_AT`
(10:13:28Z).

Key lines:
```
RUN_ID = 35083828156
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/35083828156
```

One dispatch call, exit code 0. No retry needed.

## Task 1 close

The milestone branch is on origin at the phase tip (`PUSHED_SHA`), with no decoy and no tag, and
one CI run (`RUN_ID`) is dispatched against exactly that tip. Task 2 observes it to completion.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 04*
