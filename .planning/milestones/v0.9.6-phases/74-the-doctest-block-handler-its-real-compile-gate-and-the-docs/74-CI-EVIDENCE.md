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

## Run

Waited in the foreground: `timeout 590 gh run watch 35476044079 --interval 30` (Bash tool `timeout`
600000, no `run_in_background`). The run finished inside the first watch window; the watch call
exited 0 and printed the full job tree through completion.

`gh run view "$RUNID" --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt`:
```
{"conclusion":"success","createdAt":"2026-09-19T23:24:33Z","headSha":"e54d47d0b00d77f600d1aa27b0f78a031db055c7","status":"completed","updatedAt":"2026-09-19T23:31:25Z","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/35476044079","workflowName":"CI"}
```

RUN_HEAD_SHA = e54d47d0b00d77f600d1aa27b0f78a031db055c7

RUN_CONCLUSION = success

## Job census

`gh run view "$RUNID" --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'`:

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Build Package | success |
| 2 | Type Check | success |
| 3 | Lint and Format Check | success |
| 4 | Integration Test - advanced | success |
| 5 | Code Coverage | success |
| 6 | Test Python 3.13 on macos-latest | success |
| 7 | Test Python 3.12 on windows-latest | success |
| 8 | Test Python 3.13 on ubuntu-latest | success |
| 9 | Test Python 3.12 on ubuntu-latest | success |
| 10 | Test Python 3.13 on windows-latest | success |
| 11 | Integration Test - basic | success |
| 12 | Test Python 3.12 on macos-latest | success |

JOB_COUNT = 12

NON_SUCCESS_JOBS = 0

Sorted job-name set, `gh run view 35476044079 --json jobs --jq '[.jobs[].name] | sort | join("|")'`:
```
Build Package|Code Coverage|Integration Test - advanced|Integration Test - basic|Lint and Format Check|Test Python 3.12 on macos-latest|Test Python 3.12 on ubuntu-latest|Test Python 3.12 on windows-latest|Test Python 3.13 on macos-latest|Test Python 3.13 on ubuntu-latest|Test Python 3.13 on windows-latest|Type Check
```
Identical to `REFERENCE_JOB_NAMES` in `74-BASE-EVIDENCE.md` — `ci.yml` has not changed since the
reference run (constraint 7, no workflow edit this phase).

JOB_NAMES_MATCH_REFERENCE = yes

## windows-latest lanes

| Job | Conclusion |
|-----|------------|
| Test Python 3.12 on windows-latest | success |
| Test Python 3.13 on windows-latest | success |

## macos-latest lanes

| Job | Conclusion |
|-----|------------|
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |

## Lint through tox

`Lint and Format Check` job id: `105985354942`. Quoted from
`gh run view --job 105985354942 --log`:

`Run lint with tox` step, `commands[0]> black --check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-19T23:24:49.3685192Z lint: commands[0]> black --check .
Lint and Format Check	Run lint with tox	2026-09-19T23:24:53.9983607Z All done! ✨ 🍰 ✨
Lint and Format Check	Run lint with tox	2026-09-19T23:24:53.9984381Z 357 files would be left unchanged.
```
(The step also printed a benign `Warning: Python 3.12 cannot parse code formatted for Python 3.13`
diagnostic ahead of the verdict; `black --check .` still exited clean, per `All done!` above.)

`commands[1]> ruff check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-19T23:24:54.0220687Z lint: commands[1]> ruff check .
Lint and Format Check	Run lint with tox	2026-09-19T23:24:54.0817351Z All checks passed!
```

`lint: OK` line:
```
Lint and Format Check	Run lint with tox	2026-09-19T23:24:54.0838495Z   lint: OK (4.88=setup[0.16]+cmd[4.65,0.06] seconds)
```
This shows the runner ran the same lint through tox that this worktree ran locally in 74-06.

## Dispatch count and no release run

`gh run list --workflow=ci.yml --branch gsd/v0.9.6-doctest-block-rendering-and-release --event workflow_dispatch --limit 50 --json headSha`:
```
[{"headSha":"e54d47d0b00d77f600d1aa27b0f78a031db055c7"}]
```

DISPATCH_COUNT = 1

`gh run list --workflow=release.yml --limit 20 --json headSha`:
```
(20 rows returned, none matching e54d47d0b00d77f600d1aa27b0f78a031db055c7 — the most recent is the
v0.9.2 release tag commit 45962faad21520c72ac9f1e14c7f684050826bb6)
```

RELEASE_RUNS_AT_PUSHED = 0

## Required checks at phase close

`gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict`:
```
true
```

`... --jq '[.contexts[]] | sort | join("|")'`:
```
Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

REQUIRED_STRICT_CLOSE = true

REQUIRED_CONTEXTS_CLOSE = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check

Both equal `REQUIRED_STRICT_HEAD` (`true`) and `REQUIRED_CONTEXTS_HEAD` (the same six contexts) from
`74-BASE-EVIDENCE.md`.

REQUIRED_CHECKS_UNCHANGED = yes

## SC4 CI verdict

The run is completed and success, `NON_SUCCESS_JOBS = 0`, `JOB_NAMES_MATCH_REFERENCE = yes`, all
four named `windows-latest`/`macos-latest` lanes are success, `DISPATCH_COUNT = 1`,
`RELEASE_RUNS_AT_PUSHED = 0` and `REQUIRED_CHECKS_UNCHANGED = yes`.

SC4_CI_VERDICT = MET

ROADMAP SC4's remote half is discharged: the milestone branch is on origin, and a completed, green
three-OS CI run on the phase tip is transcribed job by job, with no decoy, no tag, exactly one
dispatch, no release run at the pushed SHA, and `main`'s required checks unchanged from phase head
to phase close.
