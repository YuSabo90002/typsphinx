# Phase 69 — CI Evidence (D-13, SC#3 CI half)

This is the phase's only push and CI dispatch. `PUSHED_SHA` carries every product-tree change of
this phase; the only earlier plans (69-01, 69-02) touch `CHANGELOG.md` and `.planning/` only, and
that CHANGELOG edit is the change this run's tip carries. Every later commit of this phase touches
only `.planning/`, which no CI job reads.

BASE_69_04 = becd70c31bfed573dc10cdc20dcf7a30d57edd57
PUSHED_SHA = becd70c31bfed573dc10cdc20dcf7a30d57edd57
ORIGIN_BEFORE = d9c7555323e843b5a389ed4354ce656d2fd05ca2
PUSH_AT = 2026-09-12T22:47:06Z
RUN_ID = 34723677990
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990
LOCK_RUFF_VERSION = 0.15.20

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T22:46:25Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8d6f435633123829

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning line (`CLAUDE.md` § "Worktree-isolated execution"):

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.59ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8d6f435633123829
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8d6f435633123829
Prepared 1 package in 448ms
Installed 81 packages in 50ms
 ... (81 packages, including tox-uv==1.36.0, tox-uv-bare==1.36.0, uv==0.12.13, tox==4.56.1,
      ruff==0.15.20, pytest==9.1.1)
```

Pre-dispatch locked sync — every `ci.yml` job begins with this step, so a stale lock would fail all
twelve lanes before any signal:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --locked; echo "exit:$?"
Resolved 91 packages in 2ms
Checked 81 packages in 0.66ms
exit:0
```

Before any commit:

```
$ git rev-parse HEAD
becd70c31bfed573dc10cdc20dcf7a30d57edd57
```

`BASE_69_04 = becd70c31bfed573dc10cdc20dcf7a30d57edd57`.

## Wave-1 gate

The precondition's four checks, each re-run inside this worktree:

```
$ git show gsd/v0.9.3-toolchain-and-dependency-update-repair:CHANGELOG.md \
    | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' \
    | grep -c '^- \*\*'
3

$ git show gsd/v0.9.3-toolchain-and-dependency-update-repair:CHANGELOG.md \
    | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' \
    | grep -oE '(TOX-0[1-4]|DEP-0[1-5]|NIX-0[1-8]|DOC-(19|20|21))' | sort -u | wc -l
20

$ git cat-file -e gsd/v0.9.3-toolchain-and-dependency-update-repair:.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CLOSEOUT-GUARD.md; echo "exit:$?"
exit:0
```

Three bold-lead bullets, 20 distinct requirement IDs, and the closeout-guard file both exist at the
canonical ref. Wave 1 (69-01's CHANGELOG edit, 69-02's closeout guard) is present on the tip this
plan is about to push. No `## HALT` is written.

## Tip identity and fence

```
$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
becd70c31bfed573dc10cdc20dcf7a30d57edd57

$ git log --oneline -1 becd70c31bfed573dc10cdc20dcf7a30d57edd57
becd70c3 docs(phase-69): update tracking after wave 1, mark wave 2 executing
```

`PUSHED_SHA = becd70c31bfed573dc10cdc20dcf7a30d57edd57`. This worktree was cut from the canonical
tip after wave 1 merged, and this task had not committed at the time of measurement, so `PUSHED_SHA`
equals both `BASE_69_04` and this worktree's own HEAD at measurement time.

```
$ git diff --name-only HEAD becd70c31bfed573dc10cdc20dcf7a30d57edd57 -- . ':(exclude).planning'
(empty)
```

The pushed tree equals this worktree's product tree.

```
$ git show becd70c31bfed573dc10cdc20dcf7a30d57edd57:pyproject.toml | sed -n 7p
version = "0.9.2"
```

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base becd70c31bfed573dc10cdc20dcf7a30d57edd57 origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e

$ git diff --name-only 6181768f64b4cee62a77ac4e26c60c3c976cbb6e becd70c31bfed573dc10cdc20dcf7a30d57edd57 -- typsphinx .github/workflows
(empty)
```

Nothing under `typsphinx/` or `.github/workflows/` differs from the merge-base with `origin/main`
(constraint 13; CI is unchanged).

```
$ git merge-base --is-ancestor origin/main becd70c31bfed573dc10cdc20dcf7a30d57edd57; echo "exit:$?"
exit:1
```

`origin/main` is not an ancestor of the pushed tip (D-06: the milestone branch does not absorb
`main` in this phase).

```
$ git tag --points-at becd70c31bfed573dc10cdc20dcf7a30d57edd57
(empty)
```

No tag points at the pushed tip.

```
$ git show becd70c31bfed573dc10cdc20dcf7a30d57edd57:uv.lock | grep -A1 -xF 'name = "ruff"' | sed -n 's/^version = "\(.*\)"$/\1/p'
0.15.20
```

`LOCK_RUFF_VERSION = 0.15.20`.

## D-14 decoy census

Run immediately before the push, with nothing but the fence measurements above in between:

```
$ git branch --list 'gsd/v0.9.3*' -v
+ gsd/v0.9.3-toolchain-and-dependency-update-repair becd70c3 [ahead 132] docs(phase-69): update tracking after wave 1, mark wave 2 executing

$ git ls-remote --heads origin 'gsd/v0.9.3*'
d9c7555323e843b5a389ed4354ce656d2fd05ca2	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

No `gsd/v0.9.3-milestone` decoy exists, locally or on origin. Only the canonical branch is present
in either listing. No decoy handling was required — nothing to delete, nothing to halt on.

## Push

```
$ git fetch origin gsd/v0.9.3-toolchain-and-dependency-update-repair
From https://github.com/YuSabo90002/typsphinx
 * branch              gsd/v0.9.3-toolchain-and-dependency-update-repair -> FETCH_HEAD

$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
d9c7555323e843b5a389ed4354ce656d2fd05ca2	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

`ORIGIN_BEFORE = d9c7555323e843b5a389ed4354ce656d2fd05ca2`.

```
$ git merge-base --is-ancestor d9c7555323e843b5a389ed4354ce656d2fd05ca2 becd70c31bfed573dc10cdc20dcf7a30d57edd57; echo "exit:$?"
exit:0
```

`ORIGIN_BEFORE` is an ancestor of `PUSHED_SHA` — a fast-forward is possible.

```
$ git config --get push.followTags
(exit 1 — unset)

$ date -u +%FT%TZ
2026-09-12T22:47:06Z
```

`PUSH_AT = 2026-09-12T22:47:06Z`.

```
$ git push --no-follow-tags origin gsd/v0.9.3-toolchain-and-dependency-update-repair
To https://github.com/YuSabo90002/typsphinx.git
   d9c75553..becd70c3  gsd/v0.9.3-toolchain-and-dependency-update-repair -> gsd/v0.9.3-toolchain-and-dependency-update-repair
```

No pull-request hint was printed by GitHub on this push, and none would have been acted on
regardless. No force, no tags, no other ref.

```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
becd70c31bfed573dc10cdc20dcf7a30d57edd57	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair

$ git ls-remote --tags origin | grep 'v0\.9\.3' || echo "NO_MATCH"
NO_MATCH
```

The origin head now equals `PUSHED_SHA`, advanced from `ORIGIN_BEFORE` as a fast-forward. No
`refs/tags/v0.9.3*` line exists on origin.

## Dispatch

```
$ gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair
https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990

$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-12T22:47:18Z","databaseId":34723677990,"headSha":"becd70c31bfed573dc10cdc20dcf7a30d57edd57","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990"},{"createdAt":"2026-09-12T07:55:42Z","databaseId":34681968010,"headSha":"d9c7555323e843b5a389ed4354ce656d2fd05ca2","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34681968010"},{"createdAt":"2026-09-11T15:52:41Z","databaseId":34618719267,"headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267"}]
```

`RUN_ID = 34723677990`, `RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990`.

The listed row's `headSha` (`becd70c31bfed573dc10cdc20dcf7a30d57edd57`) equals `PUSHED_SHA`, and its
`createdAt` (`2026-09-12T22:47:18Z`) is later than `PUSH_AT` (`2026-09-12T22:47:06Z`). No
registration lag was encountered — the run was listed on the first query. Exactly one
`gh workflow run CI` was issued. The two older entries are Phase 65's own dispatch (`34681968010`,
the pre-this-phase baseline) and Phase 64's dispatch (`34618719267`) — neither is this plan's run.

This plan's own evidence commits land after the push and touch only `.planning/`, which no CI job
reads.
