# Phase 62 - RED Evidence

## Phase base SHA

`PHASE_BASE_SHA`: 5a837238aadc126611b175228cbed5ac8b1058f8

Measured by `git rev-parse HEAD` in this worktree (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a330bb914b3506bb0`) BEFORE any file in this phase was created or edited. This equals the `worktree_branch_check` expected base recorded by the orchestrator at dispatch time, cross-checked at task start.

## RED run (unfixed tree, 18 masters)

_(To be filled by plan 03's RED-evidence choreography.)_

## Positive control - pass_parent

_(To be filled by plan 03.)_

## Golden capture

_(To be filled by plan 03.)_

## Restore confirmation

_(To be filled by plan 03.)_

## SC#5 - branch on origin

**Pre-push `git branch -vv` (relevant line only, full output too long to transcribe wholesale):**

```
+ gsd/v0.9.2-inline-image-blocker-fix-and-release 5a837238 (/home/yuta/Documents/typsphinx) docs(62): record planning completion and owner-acknowledged amendments
```

**Decoy status:** absent. `git branch --list 'gsd/v0.9.2*'` returned exactly one branch
(`gsd/v0.9.2-inline-image-blocker-fix-and-release`) before the push. D-12 anticipated the decoy
`gsd/v0.9.2-milestone` might have been re-created by the commit helper that ran during Task 1's
commit; measured here that it was NOT re-created this time. No pointer-advance or deletion was
needed.

**Push command:**

```
git push -u origin gsd/v0.9.2-inline-image-blocker-fix-and-release
```

**Push output:**

```
remote:
remote: Create a pull request for 'gsd/v0.9.2-inline-image-blocker-fix-and-release' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.2-inline-image-blocker-fix-and-release
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.2-inline-image-blocker-fix-and-release -> gsd/v0.9.2-inline-image-blocker-fix-and-release
branch 'gsd/v0.9.2-inline-image-blocker-fix-and-release' set up to track 'origin/gsd/v0.9.2-inline-image-blocker-fix-and-release'.
```

**Post-push `git branch -vv` (relevant line):**

```
+ gsd/v0.9.2-inline-image-blocker-fix-and-release 5a837238 (/home/yuta/Documents/typsphinx) [origin/gsd/v0.9.2-inline-image-blocker-fix-and-release] docs(62): record planning completion and owner-acknowledged amendments
```

**Post-push `git ls-remote --heads origin | grep 0.9.2`:**

```
5a837238aadc126611b175228cbed5ac8b1058f8	refs/heads/gsd/v0.9.2-inline-image-blocker-fix-and-release
```

**D-11 authority CI run (`ci.yml`): NOT started by this push.** `ci.yml`'s `push`/`pull_request`
triggers are scoped to `main`/`develop` only (verified by reading `.github/workflows/ci.yml`'s
`on:` block this session), and `gsd/v0.9.2-inline-image-blocker-fix-and-release` is neither. No
`ci.yml` run appears against this branch. Plan 04 still owns dispatching the single D-11 authority
run at phase end.

**Measured correction to the plan's assumption — one OTHER workflow DID trigger.**
`gh run list --branch gsd/v0.9.2-inline-image-blocker-fix-and-release --limit 5` shows:

```
[{"conclusion":"success","createdAt":"2026-08-30T07:41:59Z","databaseId":33299819549,
  "event":"push","headBranch":"gsd/v0.9.2-inline-image-blocker-fix-and-release",
  "name":"Link Check","status":"completed"}]
```

`.github/workflows/links.yml` ("Link Check") declares an UNSCOPED `on: push:` (no `branches:`
filter), unlike `ci.yml`. This phase's D-10/D-11 rationale ("the push costs zero CI minutes and
starts no run") was written against `ci.yml` alone and did not account for other workflow files
with push triggers; it is corrected here by direct measurement rather than re-asserted from prose.
Substance is unaffected: `links.yml` is explicitly advisory per its own header comment ("never
registered as a GitHub required status check, so a red or cancelled run never blocks a merge"),
it is not the D-11 authority run, it completed `success` in seconds, and it did not run the
test/lint matrix this push was deliberately timed to avoid. See the plan's SUMMARY.md
"Deviations from Plan" section for the acknowledgment.
