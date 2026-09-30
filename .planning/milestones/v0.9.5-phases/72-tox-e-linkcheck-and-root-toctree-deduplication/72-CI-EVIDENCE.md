# Phase 72 — CI Evidence (first push, SC#5 CI half)

Recorded inside this plan's isolated worktree (`worktree-agent-af63422d94d37aec8`).

```
BASE_72_06 = 0b2595df21399363f50e5e1a55935f470e0df00d
```

```
SCRATCH_72_06 = /tmp/tmp.qBfv9BRDKs
```

## Head check and provisioning

`date -u +%FT%TZ`:
```
2026-09-13T14:00:22Z
```

`pwd -P`:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af63422d94d37aec8
```

`test -f .git; echo "exit:$?"`:
```
exit:0
```

`grep -q typsphinx-fhs-run "$(command -v uv)"; echo "shimcheck:$?"`:
```
shimcheck:0
```

Provisioning command:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --python 3.13.13
```
Ran to completion; final resolved lines included `typsphinx==0.9.2 (from
file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-af63422d94d37aec8)`, `ruff==0.16.6`,
`tox-uv==1.36.0`, `uv==0.12.13`.

Same provisioning line with `--locked` appended:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --python 3.13.13 --locked
```
```
Resolved 91 packages in 4ms
Checked 81 packages in 0.60ms
exit:0
```
The lock is in sync; every `ci.yml` job's own `uv sync --extra dev --locked` will not fail on a
stale lock before any signal.

## Wave-3 gate

```
$ sed -n 's/^SC3_VERDICT = //p' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-TOCTREE-EVIDENCE.md | head -n1
SC3_VERDICT = MET

$ sed -n 's/^SC4_VERDICT = //p' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-TOCTREE-EVIDENCE.md | head -n1
SC4_VERDICT = MET

$ sed -n 's/^SC5_LOCAL_VERDICT = //p' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-GATES-EVIDENCE.md | head -n1
SC5_LOCAL_VERDICT = MET

$ sed -n 's/^TIP_LINKCHECK_VERDICT = //p' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-GATES-EVIDENCE.md | head -n1
TIP_LINKCHECK_VERDICT = PASS

$ sed -n 's/^LINKCHECK_VERDICT = //p' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-LINKCHECK-EVIDENCE.md | head -n1
LINKCHECK_VERDICT = PASS

$ sed -n 's/^DOC24_VERDICT = //p' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-DOC24-EVIDENCE.md | head -n1
DOC24_VERDICT = MET
```

All six wave-3 keys read as required. No `## HALT` is written; the push proceeds.

## Tip identity and fence

```
$ git rev-parse gsd/v0.9.5-docs-link-check-and-navigation
0b2595df21399363f50e5e1a55935f470e0df00d

$ git log --oneline -1 gsd/v0.9.5-docs-link-check-and-navigation
0b2595df docs(phase-72): update tracking after wave 3, mark wave 4 executing
```

Key line:
```
PUSHED_SHA = 0b2595df21399363f50e5e1a55935f470e0df00d
```

`PUSHED_SHA` equals `BASE_72_06` — this worktree's own fork base already carried wave 3's merged
commits and wave 4's own tracking-update commit before this plan started.

```
$ git diff --name-only HEAD 0b2595df21399363f50e5e1a55935f470e0df00d -- . ':(exclude).planning'
(empty)
```
The pushed product tree equals this worktree's HEAD, outside `.planning/`.

```
$ git diff --name-only 34c77f59266acb028c8934ff56715dd4454bdfe8 0b2595df21399363f50e5e1a55935f470e0df00d -- typsphinx/ .github/
(empty)
```
No `typsphinx/` or `.github/` change since `PHASE_BASE_SHA`.

```
$ git show 0b2595df21399363f50e5e1a55935f470e0df00d:pyproject.toml | grep -m1 '^version = '
version = "0.9.2"
```

```
$ git tag --points-at 0b2595df21399363f50e5e1a55935f470e0df00d
(empty)
```
No tag rides along at the pushed tip.

## Decoy census (constraint 6)

Run immediately before the push, with only the tip-identity measurements above in between.

```
$ git branch --list 'gsd/v0.9.5*' -v
+ gsd/v0.9.5-docs-link-check-and-navigation 0b2595df docs(phase-72): update tracking after wave 3, mark wave 4 executing

$ git ls-remote --heads origin 'gsd/v0.9.5*'
(empty)
```

`gsd/v0.9.5-milestone` is absent both locally and on origin — only the canonical branch appears
locally, and origin has nothing yet for `gsd/v0.9.5*`. Census result: no decoy anywhere; this is the
first push, matching the planning-time census. Nothing is deleted.

## Push

```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
(empty)
```

Key line:
```
ORIGIN_BEFORE = none
```
Expected for the first push.

```
$ git config --get push.followTags; echo "exit:$?"
exit:1
```
Unset.

Key line:
```
PUSH_AT = 2026-09-13T14:00:53Z
```

```
$ git push --no-follow-tags -u origin gsd/v0.9.5-docs-link-check-and-navigation
remote:
remote: Create a pull request for 'gsd/v0.9.5-docs-link-check-and-navigation' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.5-docs-link-check-and-navigation
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.5-docs-link-check-and-navigation -> gsd/v0.9.5-docs-link-check-and-navigation
branch 'gsd/v0.9.5-docs-link-check-and-navigation' set up to track 'origin/gsd/v0.9.5-docs-link-check-and-navigation'.
```
The pull-request hint is recorded verbatim; it is not acted on.

Post-push checks:
```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
0b2595df21399363f50e5e1a55935f470e0df00d	refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
```
Origin head now equals `PUSHED_SHA`.

```
$ git config --get branch.gsd/v0.9.5-docs-link-check-and-navigation.remote
origin
```
The branch tracks `origin`, the SC#5 naming.

```
$ git ls-remote --tags origin | grep -E 'refs/tags/v0\.9\.[2345]'
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}
```
Only `v0.9.2` is present; no `v0.9.3`, `v0.9.4` or `v0.9.5` tag.

## Dispatch

```
$ gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation
https://github.com/YuSabo90002/typsphinx/actions/runs/34761445288
exit:0
```
Issued exactly once; no HTTP 5xx was returned, so no retry or second attempt was needed.

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.5-docs-link-check-and-navigation --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-13T14:01:06Z","databaseId":34761445288,"headSha":"0b2595df21399363f50e5e1a55935f470e0df00d","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34761445288"}]
```
The single row's `headSha` equals `PUSHED_SHA`, and `createdAt` (14:01:06Z) follows `PUSH_AT`
(14:00:53Z).

Key lines:
```
RUN_ID = 34761445288
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34761445288
```

## Task 1 close

The milestone branch is on origin at the green phase tip (`PUSHED_SHA`), with no decoy and no tag,
and one CI run (`RUN_ID`) is dispatched against exactly that tip. Task 2 observes it to completion.

## Run

Waited in the foreground: `timeout 590 gh run watch 34761445288 --interval 30` (Bash tool `timeout`
600000, no `run_in_background`). The run finished inside the first watch window; the watch call
itself exited 0 and printed the full job tree through completion.

```
$ gh run view "$RUNID" --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
{"conclusion":"success","createdAt":"2026-09-13T14:01:06Z","headSha":"0b2595df21399363f50e5e1a55935f470e0df00d","status":"completed","updatedAt":"2026-09-13T14:08:13Z","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34761445288","workflowName":"CI"}
```

Key lines:
```
RUN_HEAD_SHA = 0b2595df21399363f50e5e1a55935f470e0df00d
RUN_CONCLUSION = success
```

## Job census

`gh run view "$RUNID" --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'`:

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Lint and Format Check | success |
| 2 | Integration Test - advanced | success |
| 3 | Test Python 3.13 on windows-latest | success |
| 4 | Build Package | success |
| 5 | Test Python 3.13 on ubuntu-latest | success |
| 6 | Code Coverage | success |
| 7 | Integration Test - basic | success |
| 8 | Type Check | success |
| 9 | Test Python 3.12 on windows-latest | success |
| 10 | Test Python 3.13 on macos-latest | success |
| 11 | Test Python 3.12 on macos-latest | success |
| 12 | Test Python 3.12 on ubuntu-latest | success |

Key lines:
```
JOB_COUNT = 12
NON_SUCCESS_JOBS = 0
```

Sorted job-name set compared with Phase 71's run `34748483361`:
```
$ gh run view 34761445288 --json jobs --jq '[.jobs[].name] | sort | join("|")'
Build Package|Code Coverage|Integration Test - advanced|Integration Test - basic|Lint and Format Check|Test Python 3.12 on macos-latest|Test Python 3.12 on ubuntu-latest|Test Python 3.12 on windows-latest|Test Python 3.13 on macos-latest|Test Python 3.13 on ubuntu-latest|Test Python 3.13 on windows-latest|Type Check

$ gh run view 34748483361 --json jobs --jq '[.jobs[].name] | sort | join("|")'
Build Package|Code Coverage|Integration Test - advanced|Integration Test - basic|Lint and Format Check|Test Python 3.12 on macos-latest|Test Python 3.12 on ubuntu-latest|Test Python 3.12 on windows-latest|Test Python 3.13 on macos-latest|Test Python 3.13 on ubuntu-latest|Test Python 3.13 on windows-latest|Type Check
```
Identical sets — `ci.yml` has not changed since Phase 71 (constraint 3, no workflow edit this
phase).

Key line:
```
JOB_NAMES_MATCH_PHASE71 = yes
```

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

`Lint and Format Check` job id: `103734877146`. Quoted from `gh run view --job 103734877146 --log`:

`Run lint with tox` step, `commands[0]> black --check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-13T14:01:23.6405595Z lint: commands[0]> black --check .
Lint and Format Check	Run lint with tox	2026-09-13T14:01:28.2121740Z All done! ✨ 🍰 ✨
Lint and Format Check	Run lint with tox	2026-09-13T14:01:28.2122620Z 355 files would be left unchanged.
```
(The step also printed a benign `Warning: Python 3.12 cannot parse code formatted for Python 3.13`
diagnostic ahead of the verdict; `black --check .` still exited clean, per `All done!` above.)

`commands[1]> ruff check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-13T14:01:28.2345944Z lint: commands[1]> ruff check .
Lint and Format Check	Run lint with tox	2026-09-13T14:01:28.2921522Z All checks passed!
```

`lint: OK` line:
```
Lint and Format Check	Run lint with tox	2026-09-13T14:01:28.2947235Z   lint: OK (4.86=setup[0.20]+cmd[4.59,0.06] seconds)
```

This shows the runner parsed the edited `tox.ini` on the runner.

## Dispatch count and no release run

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.5-docs-link-check-and-navigation --event workflow_dispatch --limit 50 --json headSha
[{"headSha":"0b2595df21399363f50e5e1a55935f470e0df00d"}]
```

Key line:
```
DISPATCH_COUNT = 1
```

```
$ gh run list --workflow=release.yml --limit 20 --json headSha
```
(20 rows returned, none matching `0b2595df21399363f50e5e1a55935f470e0df00d` — the most recent is
the v0.9.2 release tag commit `45962faad21520c72ac9f1e14c7f684050826bb6`.)

Key line:
```
RELEASE_RUNS_AT_PUSHED = 0
```

## Required checks at phase close

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict
true

$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '[.contexts[]] | sort | join("|")'
Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

Key lines:
```
REQUIRED_STRICT_CLOSE = true
REQUIRED_CONTEXTS_CLOSE = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

Both equal `REQUIRED_STRICT_HEAD` (`true`) and `REQUIRED_CONTEXTS_HEAD` (the same six contexts)
from `72-BASE-EVIDENCE.md`.

Key line:
```
REQUIRED_CHECKS_UNCHANGED = yes
```

## SC#5 CI verdict

The run is completed and success, `NON_SUCCESS_JOBS = 0`, `JOB_NAMES_MATCH_PHASE71 = yes`, all four
named `windows-latest`/`macos-latest` lanes are success, `DISPATCH_COUNT = 1`,
`RELEASE_RUNS_AT_PUSHED = 0` and `REQUIRED_CHECKS_UNCHANGED = yes`.

```
SC5_CI_VERDICT = MET
```

ROADMAP SC#5's remote half is discharged: the milestone branch is on origin, and a completed,
green three-OS CI run on the phase tip is transcribed job by job, with no decoy, no tag, exactly
one dispatch, no release run at the pushed SHA, and `main`'s required checks unchanged from phase
head to phase close.
