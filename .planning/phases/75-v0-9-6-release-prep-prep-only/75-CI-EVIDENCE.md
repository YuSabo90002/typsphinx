# Phase 75 — CI Evidence (bumped-tip push and dispatch, SC4 CI half)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-20T11:08:08Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af14ee48a981e4485
$ test -f .git; echo "exit:$?"
exit:0
$ grep -q typsphinx-fhs-run "$(command -v uv)"; echo "exit:$?"
exit:0
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Resolved 91 packages in 0.63ms
Installed 90 packages in 62ms
... (91 packages resolved, typsphinx==0.9.6 built from this worktree)
exit:0
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --locked
Resolved 91 packages in 2ms
Checked 90 packages in 0.63ms
exit:0
```

`--locked` exits 0: the lock is in sync with `pyproject.toml`, the same precondition every CI job
starts with.

BASE_75_06 = b63e5d453d604350b55c51a1a77918985d6dad7c

SCRATCH_75_06 = /tmp/tmp.FZsVhvQtWR

## Wave-2 gate

`SC4_LOCAL_VERDICT` in `75-GREEN-TREE-EVIDENCE.md`:

```
SC4_LOCAL_VERDICT = MET
```

This is the amended verdict (`## AMENDED 2026-09-20 — owner decision on the three linkcheck
records`), which preserves the original `SC4_LOCAL_VERDICT_AS_FIRST_RECORDED = NOT-MET` reading
verbatim alongside it. The amendment reads SC4's linkcheck condition as "`working` plus the
classified, controlled exceptions equals `total`", classifies all three broken records, and edits
no product file — no `linkcheck_ignore` key was added. This plan takes the amended `MET` reading
as satisfying its precondition and does not re-run linkcheck or re-litigate the amendment.

`TRIAL_MERGE_VERDICT` in `75-PREFLIGHT-EVIDENCE.md`:

```
TRIAL_MERGE_VERDICT = MET
```

Both wave-2 verdicts read `MET`. Proceeding to push.

## Tip identity and fence

```
$ git rev-parse gsd/v0.9.6-doctest-block-rendering-and-release
b63e5d453d604350b55c51a1a77918985d6dad7c
$ git log --oneline -1 gsd/v0.9.6-doctest-block-rendering-and-release
b63e5d45 docs(phase-75): update tracking after wave 2
```

PUSHED_SHA = b63e5d453d604350b55c51a1a77918985d6dad7c

The pushed ref is this worktree's own HEAD — `BASE_75_06` and `PUSHED_SHA` are the same commit.

```
$ git diff --name-only HEAD b63e5d453d604350b55c51a1a77918985d6dad7c -- . ':(exclude).planning'
(empty)
```

Outside `.planning/` the ref equals this worktree's tree (trivially — same commit).

```
$ git merge-base --is-ancestor 84edd348b52f1f7e95073d2b3ebcbcd36417bc15 b63e5d453d604350b55c51a1a77918985d6dad7c; echo "exit:$?"
exit:0
```

The ref being pushed carries the bump commit (`BUMP_COMMIT_SHA` from `75-BUMP-EVIDENCE.md`).

```
$ git cat-file -e b63e5d453d604350b55c51a1a77918985d6dad7c:tests/test_docstring_rest_census_guard.py; echo "exit:$?"
exit:0
```

The run will cover the test file the milestone audit recorded as uncovered by the previous run
(`35476044079` on `e54d47d0`).

```
$ git cat-file -e b63e5d453d604350b55c51a1a77918985d6dad7c:.planning/phases/75-v0-9-6-release-prep-prep-only/75-GREEN-TREE-EVIDENCE.md; echo "exit:$?"
exit:0
$ git cat-file -e b63e5d453d604350b55c51a1a77918985d6dad7c:.planning/phases/75-v0-9-6-release-prep-prep-only/75-PREFLIGHT-EVIDENCE.md; echo "exit:$?"
exit:0
```

Wave 2 is merged into the ref being pushed.

```
$ git show b63e5d453d604350b55c51a1a77918985d6dad7c:pyproject.toml | grep -m1 '^version = '
version = "0.9.6"
```

```
$ git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b b63e5d453d604350b55c51a1a77918985d6dad7c -- typsphinx
typsphinx/pathfmt.py
typsphinx/translator.py
```

Exactly Phase 74's own diff, unchanged by this phase.

```
$ git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b b63e5d453d604350b55c51a1a77918985d6dad7c -- .github flake.nix
(empty)
```

```
$ git tag --points-at b63e5d453d604350b55c51a1a77918985d6dad7c
(empty)
```

No tag points at the pushed tip.

## Decoy census (constraint 10)

Run immediately before the push, with only the tip-identity measurements above in between.

```
$ git branch --list 'gsd/v0.9.6*' -v
+ gsd/v0.9.6-doctest-block-rendering-and-release b63e5d45 [ahead 52] docs(phase-75): update tracking after wave 2
$ git ls-remote --heads origin 'refs/heads/gsd/v0.9.6*'
e54d47d0b00d77f600d1aa27b0f78a031db055c7	refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
```

No `gsd/v0.9.6-milestone` decoy exists locally or on origin — only the canonical
`gsd/v0.9.6-doctest-block-rendering-and-release` branch is present in either census.

DECOY_ACTION = none-present

## Push

```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
e54d47d0b00d77f600d1aa27b0f78a031db055c7	refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
```

ORIGIN_BEFORE = e54d47d0b00d77f600d1aa27b0f78a031db055c7

```
$ git merge-base --is-ancestor e54d47d0b00d77f600d1aa27b0f78a031db055c7 b63e5d453d604350b55c51a1a77918985d6dad7c; echo "exit:$?"
exit:0
```

The previous origin head is an ancestor of the pushed SHA — this push is a fast-forward, never a
force.

```
$ git config --get push.followTags; echo "exit:$?"
exit:1
```

`push.followTags` is unset (no tags would be pushed implicitly even without `--no-follow-tags`).

PUSH_AT = 2026-09-20T11:08:46Z

```
$ git push --no-follow-tags origin gsd/v0.9.6-doctest-block-rendering-and-release
To https://github.com/YuSabo90002/typsphinx.git
   e54d47d0..b63e5d45  gsd/v0.9.6-doctest-block-rendering-and-release -> gsd/v0.9.6-doctest-block-rendering-and-release
```

No pull-request hint was printed by GitHub for this push (the branch already existed on origin
before this push, so GitHub did not offer to open a PR). Run once.

```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
b63e5d453d604350b55c51a1a77918985d6dad7c	refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
```

The origin head now prints `PUSHED_SHA`.

```
$ git ls-remote --tags origin
... (37 tag refs, v0.1.0b1 through v0.9.2)
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}
```

`refs/tags/v0.9.2` is present; no `v0.9.3`, `v0.9.4`, `v0.9.5` or `v0.9.6` tag exists on origin.

## Dispatch

```
$ gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release
https://github.com/YuSabo90002/typsphinx/actions/runs/35507024851
```

Run exactly once, exit 0.

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.6-doctest-block-rendering-and-release --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
[
  {"createdAt":"2026-09-20T11:08:59Z","databaseId":35507024851,"headSha":"b63e5d453d604350b55c51a1a77918985d6dad7c","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/35507024851"},
  {"createdAt":"2026-09-19T23:24:33Z","databaseId":35476044079,"headSha":"e54d47d0b00d77f600d1aa27b0f78a031db055c7","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/35476044079"}
]
```

The first row's `headSha` is `PUSHED_SHA` and its `createdAt` (`2026-09-20T11:08:59Z`) is after
`PUSH_AT` (`2026-09-20T11:08:46Z`). No registration lag — the run appeared on the first list call.
The dispatch did not return an HTTP 5xx, so no repeat-then-conditionally-redispatch branch applies.

RUN_ID = 35507024851

RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/35507024851

Committing this evidence file now, before the first foreground wait (Task 2).

## Run

Waited in the foreground: `timeout 590 gh run watch 35507024851 --interval 30` (Bash tool
`timeout` 600000, no `run_in_background`). The run reached `completed`/`success` during that
single watch call — no repeated status polling was needed beyond it.

```
$ gh run view 35507024851 --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
{"conclusion":"success","createdAt":"2026-09-20T11:08:59Z","headSha":"b63e5d453d604350b55c51a1a77918985d6dad7c","status":"completed","updatedAt":"2026-09-20T11:17:19Z","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/35507024851","workflowName":"CI"}
```

RUN_HEAD_SHA = b63e5d453d604350b55c51a1a77918985d6dad7c

RUN_CONCLUSION = success

Run duration: `createdAt` 2026-09-20T11:08:59Z to `updatedAt` 2026-09-20T11:17:19Z (~8m20s).

## Job census

```
$ gh run view 35507024851 --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
```

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Lint and Format Check | success |
| 2 | Build Package | success |
| 3 | Type Check | success |
| 4 | Integration Test - advanced | success |
| 5 | Code Coverage | success |
| 6 | Test Python 3.13 on ubuntu-latest | success |
| 7 | Test Python 3.13 on windows-latest | success |
| 8 | Test Python 3.13 on macos-latest | success |
| 9 | Test Python 3.12 on ubuntu-latest | success |
| 10 | Integration Test - basic | success |
| 11 | Test Python 3.12 on macos-latest | success |
| 12 | Test Python 3.12 on windows-latest | success |

JOB_COUNT = 12

NON_SUCCESS_JOBS = 0

```
$ gh run view 35507024851 --json jobs --jq '[.jobs[].name] | sort | join("|")'
Build Package|Code Coverage|Integration Test - advanced|Integration Test - basic|Lint and Format Check|Test Python 3.12 on macos-latest|Test Python 3.12 on ubuntu-latest|Test Python 3.12 on windows-latest|Test Python 3.13 on macos-latest|Test Python 3.13 on ubuntu-latest|Test Python 3.13 on windows-latest|Type Check
```

This equals `REFERENCE_JOB_NAMES` in `74-BASE-EVIDENCE.md` exactly — the same 12-name sorted set,
including both `windows-latest` and both `macos-latest` lanes. Constraint 7 (no workflow edit this
milestone) holds; `ci.yml`'s job set is unchanged since Phase 74.

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

All four cross-platform lanes are individually success.

## Lint through tox

`Lint and Format Check` job id: `106068461970`.

```
$ gh run view --job 106068461970 --log | grep -n "black --check\|ruff check\|lint: OK"
lint: commands[0]> black --check .
lint: commands[1]> ruff check .
  lint: OK (2.41=setup[0.12]+cmd[2.25,0.04] seconds)
```

The lint step's own `black --check .` and `ruff check .` command lines and its `lint: OK` result
line, quoted from the job's own log — the gate this project has seen fail in CI while every test
lane passed.

The log's `Install dependencies` step prints `ruff==0.16.7`.

CI_RUFF_VERSION = 0.16.7

```
$ git show b63e5d453d604350b55c51a1a77918985d6dad7c:uv.lock | grep -A1 -xF 'name = "ruff"'
name = "ruff"
version = "0.16.7"
```

LOCK_RUFF_VERSION = 0.16.7

CI's installed ruff version matches the pushed tree's own lock stanza.

## Dispatch count and no release run

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.6-doctest-block-rendering-and-release --event workflow_dispatch --limit 50 --json headSha
[{"headSha":"b63e5d453d604350b55c51a1a77918985d6dad7c"},{"headSha":"e54d47d0b00d77f600d1aa27b0f78a031db055c7"}]
```

Exactly one row at `PUSHED_SHA` (the second row is Phase 74's own run on the previous tip).

DISPATCH_COUNT = 1

```
$ gh run list --workflow=release.yml --limit 20 --json headSha
```

None of the 20 most recent `release.yml` runs carry `headSha` `b63e5d453d604350b55c51a1a77918985d6dad7c` —
the most recent is the v0.9.2 release tag's run at `45962faad21520c72ac9f1e14c7f684050826bb6`. No
`release.yml` run has fired on this tip.

RELEASE_RUNS_AT_PUSHED = 0

## Required checks at phase close

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict
true
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '[.contexts[]] | sort | join("|")'
Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

REQUIRED_STRICT_CLOSE_75 = true

REQUIRED_CONTEXTS_CLOSE_75 = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check

Both equal Phase 74's close values (`REQUIRED_STRICT_CLOSE = true`,
`REQUIRED_CONTEXTS_CLOSE = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check`).

REQUIRED_CHECKS_UNCHANGED = yes

All six required contexts (`Build Package`, `Code Coverage`, `Lint and Format Check`,
`Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Type Check`) appear in
this run's job list, each `success` — the required set is covered by a run that has already passed
on this exact tree.

## SC4 CI verdict

The run is `completed`/`success` on `PUSHED_SHA`; `NON_SUCCESS_JOBS = 0`;
`JOB_NAMES_MATCH_REFERENCE = yes`; all four named `windows-latest`/`macos-latest` lanes are
success; `DISPATCH_COUNT = 1`; `RELEASE_RUNS_AT_PUSHED = 0`; `REQUIRED_CHECKS_UNCHANGED = yes`.
Every condition holds.

SC4_CI_VERDICT = MET

## AMENDED 2026-09-22 — second dispatch after the code-review fix

Addendum. Nothing measured above was edited: every key in the sections above remains a true record
of **dispatch 1**, which happened exactly as written. This section records **dispatch 2** and
restates the one reading whose phase-level meaning the second dispatch changes.

AMEND2_AT = 2026-09-22T10:15:47Z
DISPATCH_COUNT_PHASE_TOTAL = 2
DISPATCH_COUNT_AS_FIRST_RECORDED = 1

### Why a second dispatch

The `execute:post` code-review gate returned one WARNING, WR-01 in `75-REVIEW.md`: `84edd348`
appended "0.9.6" to `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py` but left the comment
above it reading "The 16 releases ... 0.4.4 through 0.9.2, inclusive", which the same commit made
wrong on the count and on the upper bound. The project owner chose on 2026-09-22 to fix it **and
re-take the CI half on the fixed tip**, rather than inherit dispatch 1's green or defer the fix.

`DISPATCH_COUNT = 1` in the section above was true when written and remains a true count of
dispatches up to that moment. At phase close the phase-level total is 2. Both dispatches were
deliberate; neither was a retry, a duplicate, or a 5xx-induced double fire. Dispatch 2 was
requested only after `gh run list` confirmed dispatch 1 had completed, and the run list was re-read
immediately afterwards to confirm exactly one new run had appeared.

### Dispatch 2

FIX_COMMIT_SHA = 8416938871398f52a03636db2ef4c4895e39ac75
FIX_COMMIT_SCOPE = tests/test_changelog_page_gate.py
FIX_COMMIT_NUMSTAT = 1 file changed, 1 insertion, 1 deletion
PUSHED_SHA_2 = 8416938871398f52a03636db2ef4c4895e39ac75
PUSH_2_RANGE = b63e5d45..84169388
PUSH_2_FAST_FORWARD = yes
ORIGIN_TIP_AFTER_PUSH_2 = 8416938871398f52a03636db2ef4c4895e39ac75
RUN_ID_2 = 35714217450
RUN_URL_2 = https://github.com/YuSabo90002/typsphinx/actions/runs/35714217450
RUN_2_EVENT = workflow_dispatch
RUN_2_HEAD_SHA = 8416938871398f52a03636db2ef4c4895e39ac75
RUN_2_STATUS = completed
RUN_2_CONCLUSION = success
RUN_2_CREATED_AT = 2026-09-22T10:07:11Z
RUN_2_UPDATED_AT = 2026-09-22T10:14:43Z
JOB_COUNT_2 = 12
NON_SUCCESS_JOBS_2 = 0
JOB_NAMES_MATCH_RUN_1 = yes
CI_RUNS_ON_BRANCH_AFTER = 3
RELEASE_RUNS_AT_PUSHED_2 = 0

`RUN_2_HEAD_SHA` equals `PUSHED_SHA_2` equals the local tip, so the run tested exactly the pushed
tree. All twelve jobs are `success`, and the sorted job-name set is byte-identical to dispatch 1's,
so the same three-operating-system matrix ran:

```
Build Package | Code Coverage | Integration Test - advanced | Integration Test - basic |
Lint and Format Check | Test Python 3.12 on macos-latest | Test Python 3.12 on ubuntu-latest |
Test Python 3.12 on windows-latest | Test Python 3.13 on macos-latest |
Test Python 3.13 on ubuntu-latest | Test Python 3.13 on windows-latest | Type Check
```

`CI_RUNS_ON_BRANCH_AFTER = 3` decomposes as `35476044079` on `e54d47d0` (Phase 74's tip, before
this phase), `35507024851` on `b63e5d45` (dispatch 1), and `35714217450` on `84169388`
(dispatch 2). Exactly one run per pushed tip; no tip carries two runs.

### Prep-only fence, re-measured at AMEND2_AT

TAG_V096_LOCAL_2 = 0
TAG_V096_REMOTE_2 = 0
OPEN_PRS_2 = 0
DECOY_ON_ORIGIN_2 = 0

The fence is intact: the second push and the second dispatch are still the only things this phase
placed on the remote.

SC4_CI_VERDICT_AFTER_AMEND2 = MET
