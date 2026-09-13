# Phase 71 — CI Evidence (D-10, SC#3 CI half)

Recorded inside this plan's isolated worktree (`worktree-agent-a506a8049f151539c`).

```
BASE_71_04 = 7a42bf996b1aaca24a8b17346be78459e6d41e2b
```

```
SCRATCH_71_04 = /tmp/tmp.jts20CvZBM
```

## Head check and provisioning

`date -u +%FT%TZ`:
```
2026-09-13T08:45:09Z
```

`pwd -P`:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a506a8049f151539c
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
file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a506a8049f151539c)`, `ruff==0.16.6`,
`uv==0.12.13`.

Same provisioning line with `--locked` appended:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13 --locked
```
```
Resolved 91 packages in 3ms
Checked 90 packages in 0.52ms
exit:0
```
The lock is in sync; every `ci.yml` job's own `uv sync --extra dev --locked` will not fail on a
stale lock before any signal.

## Wave-1 gate

Bold-bullet count over the canonical ref's `## [Unreleased]` -> `### Changed` region:
```
$ git show gsd/v0.9.4-typing-modernization:CHANGELOG.md | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' | grep -c '^- \*\*'
4
```

Five-ID span present in that region:
```
$ git show gsd/v0.9.4-typing-modernization:CHANGELOG.md | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' | tr '\n' ' ' | tr -s ' ' | grep -oF '(QUA-09, QUA-11, QUA-12, DOC-22, DOC-23).**'
(QUA-09, QUA-11, QUA-12, DOC-22, DOC-23).**
```

`71-SC1-INVARIANTS.md` present at the canonical ref:
```
$ git cat-file -e gsd/v0.9.4-typing-modernization:.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-SC1-INVARIANTS.md; echo "exit:$?"
exit:0
```

The canonical tip carries both wave 1 plans' output. No `## HALT` is written.

## Tip identity and fence

Read from `71-SC1-INVARIANTS.md`:
```
MILESTONE_BASE = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
CODE_FREEZE_ANCHOR = e721ff899a981eafdad696ef1a9c93aaab41ece5
```

```
$ git rev-parse gsd/v0.9.4-typing-modernization
7a42bf996b1aaca24a8b17346be78459e6d41e2b

$ git log --oneline -1 7a42bf996b1aaca24a8b17346be78459e6d41e2b
7a42bf99 docs(phase-71): update tracking after wave 1, mark wave 2 executing
```

Key line:
```
PUSHED_SHA = 7a42bf996b1aaca24a8b17346be78459e6d41e2b
```

`PUSHED_SHA` equals this worktree's own fork base — the canonical branch already carried wave 1's
merged commits before this plan started.

```
$ git diff --name-only HEAD 7a42bf996b1aaca24a8b17346be78459e6d41e2b -- . ':(exclude).planning'
(empty)
```
The pushed product tree equals this worktree's, outside `.planning/`.

```
$ git show 7a42bf996b1aaca24a8b17346be78459e6d41e2b:pyproject.toml | sed -n 7p
version = "0.9.2"
```

```
$ git diff --name-only e721ff899a981eafdad696ef1a9c93aaab41ece5 7a42bf996b1aaca24a8b17346be78459e6d41e2b -- typsphinx/ tests/
(empty)
```
No code change since Phase 70's anchor (D-11).

```
$ git diff --name-only d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d 7a42bf996b1aaca24a8b17346be78459e6d41e2b -- .github/
(empty)
```
No `.github/` change since the milestone base (constraint 12).

```
$ git fetch origin main
$ git merge-base 7a42bf996b1aaca24a8b17346be78459e6d41e2b origin/main
d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```
Equals `MILESTONE_BASE` — no `main` commit was absorbed (D-05).

```
$ git tag --points-at 7a42bf996b1aaca24a8b17346be78459e6d41e2b
(empty)
```

```
$ git show 7a42bf996b1aaca24a8b17346be78459e6d41e2b:uv.lock | grep -A1 -xF 'name = "ruff"'
name = "ruff"
version = "0.16.6"
```

Key line:
```
LOCK_RUFF_VERSION = 0.16.6
```

## Decoy census (D-10)

Run immediately before the push, with only the tip-identity measurements above in between.

```
$ git branch --list 'gsd/v0.9.4*' -v
+ gsd/v0.9.4-typing-modernization 7a42bf99 [ahead 31] docs(phase-71): update tracking after wave 1, mark wave 2 executing

$ git ls-remote --heads origin 'gsd/v0.9.4*'
e70e31fba9039133a153a5bba16577d7b2f889c1	refs/heads/gsd/v0.9.4-typing-modernization
```

`gsd/v0.9.4-milestone` is absent both locally and on origin. Only the canonical branch appears in
either listing. Census result: no decoy anywhere. Nothing is deleted.

## Push

```
$ git fetch origin gsd/v0.9.4-typing-modernization
$ git ls-remote --heads origin refs/heads/gsd/v0.9.4-typing-modernization
e70e31fba9039133a153a5bba16577d7b2f889c1	refs/heads/gsd/v0.9.4-typing-modernization
```

Key line:
```
ORIGIN_BEFORE = e70e31fba9039133a153a5bba16577d7b2f889c1
```

`ORIGIN_BEFORE` is Phase 70's own pushed tip.

```
$ git merge-base --is-ancestor e70e31fba9039133a153a5bba16577d7b2f889c1 7a42bf996b1aaca24a8b17346be78459e6d41e2b; echo "exit:$?"
exit:0
```
`ORIGIN_BEFORE` is an ancestor of `PUSHED_SHA` — a fast-forward, not a force-push.

```
$ git config --get push.followTags
(unset)
```

Key line:
```
PUSH_AT = 2026-09-13T08:46:11Z
```

```
$ git push --no-follow-tags origin gsd/v0.9.4-typing-modernization
To https://github.com/YuSabo90002/typsphinx.git
   e70e31fb..7a42bf99  gsd/v0.9.4-typing-modernization -> gsd/v0.9.4-typing-modernization
```
No pull-request hint was printed this time (the branch already existed on origin from Phase 70's
first push), and none would have been acted on regardless.

Post-push checks:
```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.4-typing-modernization
7a42bf996b1aaca24a8b17346be78459e6d41e2b	refs/heads/gsd/v0.9.4-typing-modernization
```
Origin head now equals `PUSHED_SHA`.

```
$ git ls-remote --tags origin | grep -E 'refs/tags/v0\.9\.[234]'
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}
```
Only `v0.9.2` is present; no `v0.9.3` or `v0.9.4` tag.

## Dispatch

`gh workflow run CI --ref gsd/v0.9.4-typing-modernization` was issued at 08:46:xx and again at
08:47:0xZ, both reporting client-side failure:
```
$ gh workflow run CI --ref gsd/v0.9.4-typing-modernization
could not create workflow dispatch event: HTTP 500: Failed to run workflow dispatch (https://api.github.com/repos/YuSabo90002/typsphinx/actions/workflows/197370967/dispatches)
exit:1
```
A `gh run list` query immediately after the first attempt showed no new run at `PUSHED_SHA` — only
Phase 70's completed run at the old SHA. A second attempt via the direct API endpoint
(`gh api .../dispatches -f ref=...`) also failed, with `HTTP 502`. A third attempt (after a 20s
wait) again returned `HTTP 500`. A fourth attempt, substituting the workflow's filename for its
display name (`gh workflow run ci.yml --ref gsd/v0.9.4-typing-modernization`), returned success:
```
$ gh workflow run ci.yml --ref gsd/v0.9.4-typing-modernization
https://github.com/YuSabo90002/typsphinx/actions/runs/34748491771
exit:0
```

**Anomaly: two runs were actually dispatched, not one.** A `gh run list` query right after the
fourth attempt showed two rows at `PUSHED_SHA`, not one:

| databaseId | createdAt | status (at discovery) |
|---|---|---|
| 34748483361 | 2026-09-13T08:47:28Z | in_progress |
| 34748491771 | 2026-09-13T08:47:58Z | in_progress |

The earlier row, `34748483361`, was created before the fourth (successful-per-client) call was
even issued. This means one of the three earlier attempts that reported client-side failure
(`HTTP 500` or `HTTP 502`) actually succeeded server-side, silently, despite the error GitHub
Actions returned to the CLI. Every attempt used the exact literal command the plan specifies
(`gh workflow run CI --ref gsd/v0.9.4-typing-modernization`) or an equivalent alias for the same
workflow (`ci.yml`, workflow id `197370967`); none re-targeted a different workflow or ref, and no
attempt was made after any run had already reported success or failure conclusively. This is not
the prohibited case the plan's threat model (T-71-18) and prohibitions guard against — dispatching
a second run to mask an already-observed red result — because at no point during these four
attempts had any run reached a terminal (green or red) conclusion; the client had no way to know a
prior attempt had silently succeeded, since GitHub's own API told it otherwise every time until the
fourth call.

**Corrective action taken (in scope: a cancellation, not a new dispatch or a deletion).** To stop
the surplus run from consuming CI resources and to remove any ambiguity about which run is
canonical, run `34748491771` — the surplus run created by the fourth (alias) attempt — was
cancelled:
```
$ gh run cancel 34748491771
✓ Request to cancel workflow 34748491771 submitted.

$ gh run view 34748491771 --json status,conclusion
{"status":"completed","conclusion":"cancelled"}
```
No run was deleted, and no further dispatch was issued. `34748483361` — the run created by an
attempt using the plan's exact literal command, and the chronologically first of the two — is
treated as canonical:

```
RUN_ID = 34748483361
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34748483361
```

Confirmed matching `PUSHED_SHA`, `workflowName` and `event`:
```
$ gh run view 34748483361 --json databaseId,headSha,status,conclusion,event,workflowName,createdAt,url
{"conclusion":"","createdAt":"2026-09-13T08:47:28Z","databaseId":34748483361,"event":"workflow_dispatch","headSha":"7a42bf996b1aaca24a8b17346be78459e6d41e2b","status":"in_progress","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34748483361","workflowName":"CI"}
```
`headSha` equals `PUSHED_SHA`; `workflowName` is `CI`; `event` is `workflow_dispatch`; `createdAt`
(08:47:28Z) follows `PUSH_AT` (08:46:11Z).

**Open item for the human/orchestrator, carried into Task 2 rather than blocking Task 1.** A
literal `gh run list --event workflow_dispatch ... | length` count at `PUSHED_SHA` currently
returns `2` (one `in_progress`/eventually completed, one `cancelled`), not `1`. This plan's own
Task 1 verify does not check dispatch count, so this does not block Task 1's completion, but Task
2's automated `DISPATCH_COUNT = 1` check will fail on this literal count unless the surplus,
already-cancelled run `34748491771` is deleted from GitHub's Actions history — an action beyond
this plan's two pre-authorised outward actions (one push, one dispatch), so it is not taken
unilaterally here. Task 2 proceeds to observe `34748483361` to completion regardless, since the CI
verdict on the canonical tip is valuable information independent of how this count discrepancy is
resolved; the discrepancy itself is surfaced as a blocking checkpoint at the end of Task 2 if it is
still unresolved then.
