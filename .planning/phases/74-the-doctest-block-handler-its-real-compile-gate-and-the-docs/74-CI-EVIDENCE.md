# Phase 74 — CI Evidence (first push, SC4 CI half)

Recorded inside this plan's isolated worktree (`worktree-agent-adc31217724e8a4b0`).

BASE_74_07 = e54d47d0b00d77f600d1aa27b0f78a031db055c7
Captured before any commit in this plan, via `git rev-parse HEAD`.

SCRATCH_74_07 = /tmp/tmp.kKIi91xuy2
Via `mktemp -d`.

## Head check and provisioning

`date -u +%FT%TZ`:
```
2026-09-19T23:23:32Z
```

`pwd -P`:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-adc31217724e8a4b0
```

`test -f .git; echo "exit:$?"`:
```
exit:0
```

`grep -c typsphinx-fhs-run "$(command -v uv)"`:
```
2
```

Provisioning line (`<worktree_provisioning>`):
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --python 3.13.13
```
Ran to completion, `exit:0`. Final resolved lines included
`typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-adc31217724e8a4b0)`,
`ruff==0.16.7`, `tox-uv==1.36.0`, `uv==0.12.13`.

Same line with `--locked` appended:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --python 3.13.13 --locked
```
`exit:0`. The lock is in sync; the lock was never regenerated.

## Wave-4 gate

`sed -n 's/^SC1_VERDICT = //p' 74-TIP-EVIDENCE.md`:
```
MET
```

`sed -n 's/^SC3_VERDICT = //p' 74-TIP-EVIDENCE.md`:
```
MET
```

`sed -n 's/^D05_VERDICT = //p' 74-TIP-EVIDENCE.md`:
```
MET
```

`sed -n 's/^D05_UNEXPLAINED_HUNKS = //p' 74-TIP-EVIDENCE.md`:
```
0
```

`sed -n 's/^SC4_LOCAL_VERDICT = //p' 74-GATES-EVIDENCE.md`:
```
MET
```

All five wave-4 keys read as required. No `## HALT` is written; the push proceeds.

## Tip identity and fence

`git rev-parse gsd/v0.9.6-doctest-block-rendering-and-release`:
```
e54d47d0b00d77f600d1aa27b0f78a031db055c7
```

`git log --oneline -1 gsd/v0.9.6-doctest-block-rendering-and-release`:
```
e54d47d0 docs(phase-74): update tracking after wave 4
```

PUSHED_SHA = e54d47d0b00d77f600d1aa27b0f78a031db055c7
Equals `BASE_74_07` — this worktree's own HEAD already carried wave 4's merged commits before this
plan started.

`git diff --name-only HEAD e54d47d0b00d77f600d1aa27b0f78a031db055c7 -- . ':(exclude).planning'`:
```
(empty)
```
The pushed product tree equals this worktree's HEAD, outside `.planning/`.

`git cat-file -e "$PUSHED_SHA:.../74-TIP-EVIDENCE.md"` and the same for `74-GATES-EVIDENCE.md`:
```
TIP:0
GATES:0
```
Wave 4 is merged into the ref being pushed.

`git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b e54d47d0b00d77f600d1aa27b0f78a031db055c7 -- typsphinx`:
```
typsphinx/pathfmt.py
typsphinx/translator.py
```

`git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b e54d47d0b00d77f600d1aa27b0f78a031db055c7 -- .github flake.nix`:
```
(empty)
```

`git show "$PUSHED_SHA:pyproject.toml" | grep -m1 '^version = '`:
```
version = "0.9.2"
```

`git tag --points-at "$PUSHED_SHA"`:
```
(empty)
```
No tag rides along at the pushed tip.

## Decoy census (constraint 10)

Run immediately before the push, with only step 5's measurements in between.

`git branch --list 'gsd/v0.9.6*' -v`:
```
+ gsd/v0.9.6-doctest-block-rendering-and-release e54d47d0 docs(phase-74): update tracking after wave 4
```

`git ls-remote --heads origin 'refs/heads/gsd/v0.9.6*'`:
```
(empty)
```

`gsd/v0.9.6-milestone` is absent both locally and on origin — only the canonical branch appears
locally, and origin has nothing yet for `gsd/v0.9.6*`.

DECOY_ACTION = none-present
No decoy exists anywhere. Nothing is deleted.

## Push

`git ls-remote --heads origin refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release`:
```
(empty)
```

ORIGIN_BEFORE = none
Expected for the first push.

`git config --get push.followTags; echo "exit:$?"`:
```
exit:1
```
Unset.

PUSH_AT = 2026-09-19T23:24:15Z

`git push --no-follow-tags -u origin gsd/v0.9.6-doctest-block-rendering-and-release`:
```
remote:
remote: Create a pull request for 'gsd/v0.9.6-doctest-block-rendering-and-release' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.6-doctest-block-rendering-and-release
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.6-doctest-block-rendering-and-release -> gsd/v0.9.6-doctest-block-rendering-and-release
branch 'gsd/v0.9.6-doctest-block-rendering-and-release' set up to track 'origin/gsd/v0.9.6-doctest-block-rendering-and-release'.
```
The pull-request hint is recorded verbatim; it is not acted on.

Post-push checks:

`git ls-remote --heads origin refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release`:
```
e54d47d0b00d77f600d1aa27b0f78a031db055c7	refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
```
Origin head now equals `PUSHED_SHA`.

`git config --get branch.gsd/v0.9.6-doctest-block-rendering-and-release.remote`:
```
origin
```
The branch tracks `origin`.

`git ls-remote --tags origin`, filtered to `v0.9.[23456]`-shaped refs:
```
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}
```
Only `v0.9.2` is present; no `v0.9.3`, `v0.9.4`, `v0.9.5` or `v0.9.6` tag.

## Dispatch

`gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release`:
```
https://github.com/YuSabo90002/typsphinx/actions/runs/35476044079
exit:0
```
Issued exactly once; no HTTP 5xx was returned, so no retry or second attempt was needed.

`gh run list --workflow=ci.yml --branch gsd/v0.9.6-doctest-block-rendering-and-release --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url`:
```
[{"createdAt":"2026-09-19T23:24:33Z","databaseId":35476044079,"headSha":"e54d47d0b00d77f600d1aa27b0f78a031db055c7","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/35476044079"}]
```
The single row's `headSha` equals `PUSHED_SHA`, and `createdAt` (23:24:33Z) follows `PUSH_AT`
(23:24:15Z).

RUN_ID = 35476044079

RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/35476044079

## Task 1 close

The milestone branch is on origin at the green phase tip (`PUSHED_SHA`), with no decoy and no tag,
and one CI run (`RUN_ID`) is dispatched against exactly that tip. Task 2 observes it to completion.
