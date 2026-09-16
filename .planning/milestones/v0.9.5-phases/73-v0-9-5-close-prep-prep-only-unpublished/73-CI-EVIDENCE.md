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

## Run

Waited in the foreground: `timeout 590 gh run watch 35083828156 --interval 30` (Bash tool
`timeout` 600000, no `run_in_background`). The run finished inside the first watch window; the
watch call itself exited 0 and printed the full job tree through completion.

```
$ gh run view 35083828156 --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
{"conclusion":"success","createdAt":"2026-09-16T10:13:43Z","headSha":"a54a2d8a3b06b388c7ee004e5cfbe3405431421d","status":"completed","updatedAt":"2026-09-16T10:20:12Z","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/35083828156","workflowName":"CI"}
```

Key lines:
```
RUN_HEAD_SHA = a54a2d8a3b06b388c7ee004e5cfbe3405431421d
```
```
RUN_CONCLUSION = success
```

## Job census

`gh run view "$RUNID" --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'`:

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Type Check | success |
| 2 | Lint and Format Check | success |
| 3 | Integration Test - advanced | success |
| 4 | Integration Test - basic | success |
| 5 | Build Package | success |
| 6 | Test Python 3.13 on macos-latest | success |
| 7 | Test Python 3.12 on windows-latest | success |
| 8 | Test Python 3.12 on ubuntu-latest | success |
| 9 | Test Python 3.13 on windows-latest | success |
| 10 | Test Python 3.12 on macos-latest | success |
| 11 | Code Coverage | success |
| 12 | Test Python 3.13 on ubuntu-latest | success |

Key lines:
```
JOB_COUNT = 12
```
```
NON_SUCCESS_JOBS = 0
```

Sorted job-name set compared with Phase 72's run `34761445288`:
```
$ gh run view 35083828156 --json jobs -q '[.jobs[].name] | sort | join("|")'
Build Package|Code Coverage|Integration Test - advanced|Integration Test - basic|Lint and Format Check|Test Python 3.12 on macos-latest|Test Python 3.12 on ubuntu-latest|Test Python 3.12 on windows-latest|Test Python 3.13 on macos-latest|Test Python 3.13 on ubuntu-latest|Test Python 3.13 on windows-latest|Type Check

$ gh run view 34761445288 --json jobs -q '[.jobs[].name] | sort | join("|")'
Build Package|Code Coverage|Integration Test - advanced|Integration Test - basic|Lint and Format Check|Test Python 3.12 on macos-latest|Test Python 3.12 on ubuntu-latest|Test Python 3.12 on windows-latest|Test Python 3.13 on macos-latest|Test Python 3.13 on ubuntu-latest|Test Python 3.13 on windows-latest|Type Check
```
Identical sets — `ci.yml` has not changed since Phase 72 (constraint 3, no workflow edit this
phase).

Key line:
```
JOB_NAMES_MATCH_PHASE72 = yes
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

`Lint and Format Check` job id: `104753859496`. Quoted from `gh run view --job 104753859496
--log`:

The dependency-install step's `+ ruff==` line:
```
Lint and Format Check	Install dependencies	2026-09-16T10:13:58.6407837Z  + ruff==0.16.6
```

Key line:
```
CI_RUFF_VERSION = 0.16.6
```

`Run lint with tox` step, `commands[0]> black --check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-16T10:13:59.4557091Z lint: commands[0]> black --check .
Lint and Format Check	Run lint with tox	2026-09-16T10:14:03.9089826Z All done! ✨ 🍰 ✨
Lint and Format Check	Run lint with tox	2026-09-16T10:14:03.9090905Z 355 files would be left unchanged.
```
(The step also printed a benign `Warning: Python 3.12 cannot parse code formatted for Python 3.13`
diagnostic ahead of the verdict; `black --check .` still exited clean, per `All done!` above.)

`commands[1]> ruff check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-16T10:14:03.9372847Z lint: commands[1]> ruff check .
Lint and Format Check	Run lint with tox	2026-09-16T10:14:03.9961540Z All checks passed!
```

`lint: OK` line:
```
Lint and Format Check	Run lint with tox	2026-09-16T10:14:03.9982181Z   lint: OK (4.69=setup[0.15]+cmd[4.48,0.06] seconds)
```

CI is the lint authority. 73-03's local ruff run is set beside this one in 73-07's handoff, not
here.

## Dispatch count and no release run

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.5-docs-link-check-and-navigation --event workflow_dispatch --limit 50 --json databaseId,headSha,status,conclusion
[{"conclusion":"success","databaseId":35083828156,"headSha":"a54a2d8a3b06b388c7ee004e5cfbe3405431421d","status":"completed"},{"conclusion":"success","databaseId":34761445288,"headSha":"0b2595df21399363f50e5e1a55935f470e0df00d","status":"completed"}]
```
Exactly one row at `PUSHED_SHA` (the other is Phase 72's own dispatched run at its own tip).

Key line:
```
DISPATCH_COUNT = 1
```

```
$ gh run list --workflow=release.yml --limit 20 --json headSha
```
(20 rows returned, none matching `a54a2d8a3b06b388c7ee004e5cfbe3405431421d` — the most recent is
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
```
```
REQUIRED_CONTEXTS_CLOSE = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

Both equal `REQUIRED_STRICT_HEAD` (`true`) and `REQUIRED_CONTEXTS_HEAD` (the same six contexts)
from `72-BASE-EVIDENCE.md`.

Key line:
```
REQUIRED_CHECKS_UNCHANGED = yes
```

## D-12 final tip

- This run (`RUN_ID = 35083828156`) is the phase's single dispatch.
- `PUSHED_SHA` (`a54a2d8a3b06b388c7ee004e5cfbe3405431421d`) carries every product-tree change of
  the phase, including the CHANGELOG edit.
- Every later commit of this phase touches only `.planning/`, which no CI job reads; plan 73-06
  proves this with an empty product-tree diff from `PUSHED_SHA`.
- No second dispatch is warranted: the run completed all-green, the job set matches Phase 72's,
  and `main`'s required checks are unchanged.

## SC#3 CI verdict

The run is completed and success, `NON_SUCCESS_JOBS = 0`, `JOB_NAMES_MATCH_PHASE72 = yes`, all
four named lanes are success, `DISPATCH_COUNT = 1`, and `REQUIRED_CHECKS_UNCHANGED = yes`.

```
SC3_CI_VERDICT = MET
```

ROADMAP SC#3's CI half is discharged: one fresh three-OS run dispatched on this phase's own tip,
every job conclusion transcribed, both `windows-latest` and both `macos-latest` lanes named, and
`ruff` green in `Lint and Format Check`, with the required contexts equal to the six read at
Phase 72's base.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 04*
