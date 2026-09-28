# Phase 77 — CI Evidence (bumped-tip push and dispatch, SC#3 CI half)

## Head check and provisioning

```
date -u +%FT%TZ  -> 2026-09-28T13:42:59Z
pwd -P            -> /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac152f37e43cdbd99
test -f .git; echo "exit:$?"  -> exit:0
```

Shim check:

```
grep -q typsphinx-fhs-run "$(command -v uv)" && echo shim-ok  -> shim-ok
```

Provisioning:

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```
exited 0 (venv resolved 91 packages, `typsphinx==0.9.7` from this worktree checkout installed
editable, plus every `dev`/`docs`-extra dependency).

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --locked
Resolved 91 packages in 2ms
Checked 90 packages in 0.67ms
```
exit:0 — the lock is in sync with the manifest, matching what every CI job starts with.

BASE_77_06 = df6357faf3d6ce93ac99bbfc3bdad58168a95a14
(from `git rev-parse HEAD` before any commit this plan makes; this worktree's HEAD is already the
canonical milestone tip merged after waves 1 and 2.)

SCRATCH_77_06 = /tmp/p7706.5kL0hs
(from `mktemp -d /tmp/p7706.XXXXXX`.)

## Wave gate

Quoted from the four wave-1/wave-2 evidence files:

```
SC3_LOCAL_VERDICT (77-GREEN-TREE-EVIDENCE.md) = MET
TRIAL_MERGE_VERDICT (77-PREFLIGHT-EVIDENCE.md) = MET
ATT06_VERDICT (77-ATT06-EVIDENCE.md) = MET
CONTROLS_VERDICT (77-CONTROLS-EVIDENCE.md) = READY
```

All four read their passing values — no HALT.

## Tip identity and fence

```
git rev-parse gsd/v0.9.7-trusted-publishing-and-release
df6357faf3d6ce93ac99bbfc3bdad58168a95a14

git log --oneline -1 gsd/v0.9.7-trusted-publishing-and-release
df6357fa docs(phase-77): update tracking after wave 2
```

PUSHED_SHA = df6357faf3d6ce93ac99bbfc3bdad58168a95a14

`PUSHED_SHA` equals `BASE_77_06` — this worktree's HEAD is already the ref being pushed, since
waves 1 and 2 were merged into it by the orchestrator before this plan's worktree was created.

```
git diff --name-only HEAD df6357faf3d6ce93ac99bbfc3bdad58168a95a14 -- . ':(exclude).planning'
```
prints nothing — outside `.planning/` the ref equals this worktree's tree.

```
git merge-base --is-ancestor 39cb79f970c4137d4238023e1df7291c7c282c3a df6357faf3d6ce93ac99bbfc3bdad58168a95a14; echo "exit:$?"
exit:0
```

`BUMP_COMMIT_SHA` (39cb79f970c4137d4238023e1df7291c7c282c3a, from `77-BUMP-EVIDENCE.md`) is an
ancestor of the pushed SHA.

```
D=.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
git cat-file -e df6357faf3d6ce93ac99bbfc3bdad58168a95a14:"$D/77-GREEN-TREE-EVIDENCE.md"; echo "exit:$?"
exit:0
git cat-file -e df6357faf3d6ce93ac99bbfc3bdad58168a95a14:"$D/77-PREFLIGHT-EVIDENCE.md"; echo "exit:$?"
exit:0
git cat-file -e df6357faf3d6ce93ac99bbfc3bdad58168a95a14:"$D/77-HANDOFF.md"; echo "exit:$?"
exit:0
git cat-file -e df6357faf3d6ce93ac99bbfc3bdad58168a95a14:"$D/77-ATT06-EVIDENCE.md"; echo "exit:$?"
exit:0
```

The ref being pushed carries the wave-2 evidence and the committed rollback section (77-HANDOFF.md
carries the ATT-06 rollback section per `77-ATT06-EVIDENCE.md`'s `ROLLBACK_COMMIT_SHA`).

```
git show df6357faf3d6ce93ac99bbfc3bdad58168a95a14:pyproject.toml | grep -m1 '^version = '
version = "0.9.7"
```

```
git diff --name-only 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8 df6357faf3d6ce93ac99bbfc3bdad58168a95a14 -- typsphinx
typsphinx/translator.py
```

```
git diff --name-only 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8 df6357faf3d6ce93ac99bbfc3bdad58168a95a14 -- .github flake.nix
.github/workflows/release.yml
```

Both diffs are exactly Phase 76's own changes — nothing from this phase.

```
git tag --points-at df6357faf3d6ce93ac99bbfc3bdad58168a95a14
```
prints nothing — no tag points at the pushed tip.

## Decoy census

Immediately before the push, with only this section's own measurements in between.

```
git branch --list 'gsd/v0.9.7*' -v
+ gsd/v0.9.7-trusted-publishing-and-release df6357fa docs(phase-77): update tracking after wave 2

git ls-remote --heads origin 'refs/heads/gsd/v0.9.7*'
987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78	refs/heads/gsd/v0.9.7-trusted-publishing-and-release
```

No `gsd/v0.9.7-milestone` decoy exists locally or on origin — only the canonical branch appears in
either listing.

DECOY_ACTION = none-present

## Push

```
git ls-remote --heads origin refs/heads/gsd/v0.9.7-trusted-publishing-and-release
987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78	refs/heads/gsd/v0.9.7-trusted-publishing-and-release
```

ORIGIN_BEFORE = 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78

```
git merge-base --is-ancestor 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78 df6357faf3d6ce93ac99bbfc3bdad58168a95a14; echo "exit:$?"
exit:0
```

The previous origin head is an ancestor of the pushed SHA — this push is a fast-forward, never a
force.

```
git config --get push.followTags; echo "exit:$?"
exit:1
```

`push.followTags` is unset (no tags would be pushed implicitly even without `--no-follow-tags`).

PUSH_AT = 2026-09-28T13:43:40Z

```
git push --no-follow-tags origin gsd/v0.9.7-trusted-publishing-and-release
To https://github.com/YuSabo90002/typsphinx.git
   987ec3fe..df6357fa  gsd/v0.9.7-trusted-publishing-and-release -> gsd/v0.9.7-trusted-publishing-and-release
```

Run once, exit 0. No pull-request hint was printed by GitHub for this push (the branch already
existed on origin before this push, so GitHub did not offer to open a PR); the hint is not acted on
regardless.

```
git ls-remote --heads origin refs/heads/gsd/v0.9.7-trusted-publishing-and-release
df6357faf3d6ce93ac99bbfc3bdad58168a95a14	refs/heads/gsd/v0.9.7-trusted-publishing-and-release
```

The origin head now prints `PUSHED_SHA`.

```
LC_ALL=C git ls-remote --tags origin
... (39 tag refs, v0.1.0b1 through v0.9.6)
8963519d224b82b8a27a807a5b00d6360c929ed0	refs/tags/v0.9.6
6fcc5adb02f5eefffd88ecda5258dca842d1acaa	refs/tags/v0.9.6^{}
```

`refs/tags/v0.9.6` is present; no `v0.9.7` tag exists anywhere in the full output.

## Dispatch

```
gh run list --workflow=ci.yml --branch gsd/v0.9.7-trusted-publishing-and-release --event workflow_dispatch --limit 50 --json databaseId --jq length
1
```

CI_RUNS_BEFORE = 1

This file carries no prior `DISPATCH_ATTEMPTED = yes` marker — this is the first attempt, so the
dispatch proceeds.

DISPATCH_ATTEMPTED = yes

```
gh workflow run ci.yml --ref gsd/v0.9.7-trusted-publishing-and-release
https://github.com/YuSabo90002/typsphinx/actions/runs/36430787178
```

DISPATCH_EXIT = 0

Run exactly once.

```
gh run list --workflow=ci.yml --branch gsd/v0.9.7-trusted-publishing-and-release --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-28T13:44:40Z","databaseId":36430787178,"headSha":"df6357faf3d6ce93ac99bbfc3bdad58168a95a14","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/36430787178"},{"createdAt":"2026-09-27T12:50:32Z","databaseId":36320335404,"headSha":"987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/36320335404"}]
```

The first row's `headSha` is `PUSHED_SHA` and its `createdAt` (`2026-09-28T13:44:40Z`) is after
`PUSH_AT` (`2026-09-28T13:43:40Z`). No registration lag — the run appeared on the first list call.
The dispatch did not return an HTTP 5xx, so no repeat-then-conditionally-redispatch branch applies.

RUN_ID = 36430787178

RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/36430787178

Committing this evidence file now, before the first foreground wait (Task 2).
