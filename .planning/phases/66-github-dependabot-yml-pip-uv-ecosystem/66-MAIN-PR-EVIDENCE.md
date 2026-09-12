executor worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout is never touched.

BASE_SHA = 6181768f64b4cee62a77ac4e26c60c3c976cbb6e
MILESTONE_COMMIT = e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931
CONFIG_BLOB = a58ea1e25254138ff6967438feb948c1a0cc7064
PR_BRANCH = chore/dependabot-uv-ecosystem
PR_COMMIT = 7cc85d28c6946434aa4fb14a0b9b5555d29275ef
PUSH_AT = 2026-09-12T10:18:32Z
PR_NUMBER = 137
PR_URL = https://github.com/YuSabo90002/typsphinx/pull/137
PR_RUN_ID = 34688116389

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1bcb56644df5723

$ git rev-parse --abbrev-ref HEAD
worktree-agent-ae1bcb56644df5723

$ git log --oneline -1
de5a54ed docs(66): mark phase 66 executing (wave 1 of 4)
```

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.60ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1bcb56644df5723
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1bcb56644df5723
Prepared 1 package in 447ms
Installed 81 packages in 49ms
 ... (81 packages, including uv==0.12.13, tox==4.56.1, pytest==9.1.1)
```

The provisioning line ran verbatim (CLAUDE.md, "Worktree-isolated execution"). This plan only ever
runs `git` and `gh` afterward.

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

## Baseline

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git rev-parse origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e
```

```
$ git diff --stat origin/main HEAD -- .github/dependabot.yml
(empty)
```

The two copies were identical before the edit.

```
$ git show origin/main:.github/dependabot.yml | sed -n 4p
  - package-ecosystem: "pip"

$ git ls-tree origin/main .github/dependabot.yml
100644 blob 8c52c39999651b88f79fe186ad242c2fb495b219	.github/dependabot.yml
```

Line 4 is the pip line, and the mode is `100644`. No `## HALT` — the baseline had not moved.

## Milestone-branch commit

With the Edit tool, only the quoted value on line 4 of `.github/dependabot.yml` was changed from
`"pip"` to `"uv"`. Everything else — the comment above it, indentation, and every other line —
was left untouched.

```
$ git show "6181768f64b4cee62a77ac4e26c60c3c976cbb6e:.github/dependabot.yml" | sed '4s/"pip"$/"uv"/' | cmp - .github/dependabot.yml; echo "exit:$?"
exit:0

$ git diff --numstat -- .github/dependabot.yml
1	1	.github/dependabot.yml
```

```
$ git add .github/dependabot.yml
$ git commit -m "chore(66-01): switch dependabot Python updates from pip to uv ..."
[worktree-agent-ae1bcb56644df5723 e8c0e56f] chore(66-01): switch dependabot Python updates from pip to uv
 1 file changed, 1 insertion(+), 1 deletion(-)
```

```
$ git rev-parse HEAD
e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931

$ git rev-parse HEAD:.github/dependabot.yml
a58ea1e25254138ff6967438feb948c1a0cc7064

$ git show --name-only --format= e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931
.github/dependabot.yml
```

`MILESTONE_COMMIT = e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931`, `CONFIG_BLOB` equals
`git rev-parse HEAD:.github/dependabot.yml`, and the commit touches exactly one file.

## Main-bound commit

Built from `BASE_SHA`'s tree with `.github/dependabot.yml` replaced by `CONFIG_BLOB`, via a
scratch index — the worktree's own HEAD never moved off `MILESTONE_COMMIT`.

```
$ mkdir -p /tmp/gsd-66-01-scratch

$ GIT_INDEX_FILE=/tmp/gsd-66-01-scratch/index git read-tree 6181768f64b4cee62a77ac4e26c60c3c976cbb6e
(no output)

$ GIT_INDEX_FILE=/tmp/gsd-66-01-scratch/index git update-index --cacheinfo 100644,a58ea1e25254138ff6967438feb948c1a0cc7064,.github/dependabot.yml
(no output)

$ GIT_INDEX_FILE=/tmp/gsd-66-01-scratch/index git write-tree
697748ca51baa26aa36c37c3147064827be12536
```

Commit message written to `/tmp/gsd-66-01-scratch/msg`: subject `chore(deps): switch dependabot
Python updates from pip to uv`, a blank line, then the session's attribution trailers.

```
$ git commit-tree 697748ca51baa26aa36c37c3147064827be12536 -p 6181768f64b4cee62a77ac4e26c60c3c976cbb6e -F /tmp/gsd-66-01-scratch/msg
7cc85d28c6946434aa4fb14a0b9b5555d29275ef
```

`PR_COMMIT = 7cc85d28c6946434aa4fb14a0b9b5555d29275ef`. The four pre-push assertions:

```
$ git rev-parse "$PR_COMMIT^"
6181768f64b4cee62a77ac4e26c60c3c976cbb6e

$ git diff --name-only "$BASE_SHA" "$PR_COMMIT"
.github/dependabot.yml

$ git diff --numstat "$BASE_SHA" "$PR_COMMIT"
1	1	.github/dependabot.yml

$ git rev-parse "$PR_COMMIT:.github/dependabot.yml"
a58ea1e25254138ff6967438feb948c1a0cc7064
```

Parent equals `BASE_SHA`; exactly one file changed, one line each way; the blob equals
`CONFIG_BLOB`. No `git checkout`, `git switch`, `git reset` or `git cherry-pick` was run against
this worktree; its index and HEAD stayed exactly where the milestone commit left them.

## Push and pull request

```
$ git ls-remote --heads origin refs/heads/chore/dependabot-uv-ecosystem
(empty)
```

The branch was absent on origin before the push.

```
$ date -u +%FT%TZ
2026-09-12T10:18:32Z
```

`PUSH_AT = 2026-09-12T10:18:32Z`.

```
$ git push origin 7cc85d28c6946434aa4fb14a0b9b5555d29275ef:refs/heads/chore/dependabot-uv-ecosystem
remote:
remote: Create a pull request for 'chore/dependabot-uv-ecosystem' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/chore/dependabot-uv-ecosystem
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        7cc85d28c6946434aa4fb14a0b9b5555d29275ef -> chore/dependabot-uv-ecosystem
```

No `--force`, no `--tags`, no `-u`, no other refspec.

```
$ git ls-remote --heads origin refs/heads/chore/dependabot-uv-ecosystem
7cc85d28c6946434aa4fb14a0b9b5555d29275ef	refs/heads/chore/dependabot-uv-ecosystem
```

The remote head equals `PR_COMMIT`. The milestone branch itself was not pushed.

Body written to `/tmp/gsd-66-01-scratch/body` — the two prescribed paragraphs plus the
pull-request attribution lines, naming no issue or PR number.

```
$ gh pr create --base main --head chore/dependabot-uv-ecosystem --title "chore(deps): switch dependabot Python updates from pip to uv" --body-file /tmp/gsd-66-01-scratch/body
https://github.com/YuSabo90002/typsphinx/pull/137
```

`PR_NUMBER = 137`, `PR_URL = https://github.com/YuSabo90002/typsphinx/pull/137`. No reviewer,
label or assignee was requested, and auto-merge was not enabled.

## CI run located

```
$ gh run list --workflow=ci.yml --branch chore/dependabot-uv-ecosystem --event pull_request --limit 5 --json databaseId,headSha,status,createdAt,url
[]
```

Empty on the first query — registration lag. Repeated a few seconds later:

```
$ gh run list --workflow=ci.yml --branch chore/dependabot-uv-ecosystem --event pull_request --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-12T10:18:53Z","databaseId":34688116389,"headSha":"7cc85d28c6946434aa4fb14a0b9b5555d29275ef","status":"in_progress","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34688116389"}]
```

The row's `headSha` equals `PR_COMMIT`, and its `createdAt` (`2026-09-12T10:18:53Z`) is later than
`PUSH_AT` (`2026-09-12T10:18:32Z`).

`PR_RUN_ID = 34688116389`, URL = `https://github.com/YuSabo90002/typsphinx/actions/runs/34688116389`.

## Run observed to completion

Waited in the foreground with `gh run watch 34688116389 --interval 30` (Bash timeout 600000ms, no
`run_in_background`). The single foreground call returned after the run reached a terminal state.

```
$ gh run view 34688116389 --json status,conclusion
{"conclusion":"success","status":"completed"}

$ gh run view 34688116389 --json status,conclusion,headSha,event,url
{"conclusion":"success","event":"pull_request","headSha":"7cc85d28c6946434aa4fb14a0b9b5555d29275ef","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34688116389"}
```

`status: completed`, `conclusion: success`, `headSha` equal to `PR_COMMIT`, `event: pull_request`.

## Job census

```
$ gh run view 34688116389 --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
Code Coverage	success
Integration Test - basic	success
Test Python 3.13 on macos-latest	success
Integration Test - advanced	success
Build Package	success
Type Check	success
Test Python 3.13 on ubuntu-latest	success
Test Python 3.12 on windows-latest	success
Lint and Format Check	success
Test Python 3.12 on ubuntu-latest	success
Test Python 3.13 on windows-latest	success
Test Python 3.12 on macos-latest	success
```

Twelve jobs, numbered as reported by the API (transcription order only; no assertion depends on
this order):

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Code Coverage | success |
| 2 | Integration Test - basic | success |
| 3 | Test Python 3.13 on macos-latest | success |
| 4 | Integration Test - advanced | success |
| 5 | Build Package | success |
| 6 | Type Check | success |
| 7 | Test Python 3.13 on ubuntu-latest | success |
| 8 | Test Python 3.12 on windows-latest | success |
| 9 | Lint and Format Check | success |
| 10 | Test Python 3.12 on ubuntu-latest | success |
| 11 | Test Python 3.13 on windows-latest | success |
| 12 | Test Python 3.12 on macos-latest | success |

All twelve jobs are `success`; zero non-success conclusions.

## Required checks

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '{strict: .required_status_checks.strict, contexts: .required_status_checks.contexts, enforce_admins: .enforce_admins.enabled}'
{"contexts":["Test Python 3.12 on ubuntu-latest","Lint and Format Check","Type Check","Code Coverage","Build Package","Test Python 3.13 on ubuntu-latest"],"enforce_admins":false,"strict":true}
```

`strict: true`, `enforce_admins: false`, six required contexts. Each required context tabulated
against the job census above:

| Required context | Conclusion |
|-------------------|------------|
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| Lint and Format Check | success |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |

All six required contexts read `success`.

## PR state

```
$ gh pr view 137 --json state,mergeable,mergeStateStatus,headRefOid
{"headRefOid":"7cc85d28c6946434aa4fb14a0b9b5555d29275ef","mergeStateStatus":"CLEAN","mergeable":"MERGEABLE","state":"OPEN"}
```

`state: OPEN`, `headRefOid` equals `PR_COMMIT`, `mergeStateStatus: CLEAN` (`main` had not moved
ahead of the PR's merge base during this observation).

## Non-required job findings

None. The six non-required jobs (`Integration Test - basic`, `Integration Test - advanced`,
`Test Python 3.12 on windows-latest`, `Test Python 3.13 on windows-latest`,
`Test Python 3.12 on macos-latest`, `Test Python 3.13 on macos-latest`) are all `success` per the
job census above — there is nothing to list.

## Handoff to 66-02

The main-bound PR (#137, `chore/dependabot-uv-ecosystem` at `PR_COMMIT` `7cc85d28c6946434aa4fb14a0b9b5555d29275ef`)
is OPEN and unmerged. All six required checks are green, `mergeStateStatus` is `CLEAN`. It awaits
the owner's merge decision (D-01, one-way) in 66-02. There are no non-required findings to carry
forward.

---

# 66-02: Owner-gated merge to `main`

executor worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout is never
touched.

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa58d8d64f16d0afe

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.59ms
... (81 packages installed, including uv==0.12.13, tox==4.56.1, pytest==9.1.1)

$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
```

Both checks pass; the worktree is provisioned; `gh` is authenticated.

## Wave-1 gate

All nine evidence keys are present in this file:

```
BASE_SHA = 6181768f64b4cee62a77ac4e26c60c3c976cbb6e
MILESTONE_COMMIT = e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931
CONFIG_BLOB = a58ea1e25254138ff6967438feb948c1a0cc7064
PR_BRANCH = chore/dependabot-uv-ecosystem
PR_COMMIT = 7cc85d28c6946434aa4fb14a0b9b5555d29275ef
PUSH_AT = 2026-09-12T10:18:32Z
PR_NUMBER = 137
PR_URL = https://github.com/YuSabo90002/typsphinx/pull/137
PR_RUN_ID = 34688116389
```

```
$ git merge-base --is-ancestor e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931 HEAD; echo "exit:$?"
exit:0

$ grep -c '^## HALT' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-MAIN-PR-EVIDENCE.md
0

$ git log --oneline -1
b2fa457f docs(phase-66): update tracking after wave 1, mark wave 2 executing
```

`MILESTONE_COMMIT` is an ancestor of this worktree's HEAD; the evidence file carries no HALT
heading.

## Pre-merge gate

```
$ git fetch origin main chore/dependabot-uv-ecosystem
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD
 * branch              chore/dependabot-uv-ecosystem -> FETCH_HEAD

$ git rev-parse origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e
```

`origin/main` still equals `BASE_SHA` (`6181768f64b4cee62a77ac4e26c60c3c976cbb6e`) — `main` has not
moved since 66-01.

```
$ gh pr view 137 --json state,headRefOid,mergeable,mergeStateStatus
{"headRefOid":"7cc85d28c6946434aa4fb14a0b9b5555d29275ef","mergeStateStatus":"CLEAN","mergeable":"MERGEABLE","state":"OPEN"}
```

PR #137 is `OPEN`, `headRefOid` equals `PR_COMMIT`, `mergeStateStatus: CLEAN`.

```
$ gh pr view 137 --json statusCheckRollup --jq '.statusCheckRollup[] | [.name, .conclusion] | @tsv'
Test Python 3.12 on ubuntu-latest	SUCCESS
build-docs	SUCCESS
Repo-wide link check (advisory)	SUCCESS
Repo-wide link check (advisory)	SUCCESS
Test Python 3.13 on ubuntu-latest	SUCCESS
Test Python 3.12 on windows-latest	SUCCESS
Test Python 3.13 on windows-latest	SUCCESS
Test Python 3.12 on macos-latest	SUCCESS
Test Python 3.13 on macos-latest	SUCCESS
Lint and Format Check	SUCCESS
Type Check	SUCCESS
Code Coverage	SUCCESS
Build Package	SUCCESS
Integration Test - basic	SUCCESS
Integration Test - advanced	SUCCESS
```

The six required contexts, tabulated:

| Required context | Conclusion |
|-------------------|------------|
| Test Python 3.12 on ubuntu-latest | SUCCESS |
| Test Python 3.13 on ubuntu-latest | SUCCESS |
| Lint and Format Check | SUCCESS |
| Type Check | SUCCESS |
| Code Coverage | SUCCESS |
| Build Package | SUCCESS |

All six required contexts read `SUCCESS`.

```
$ git rev-parse HEAD:.github/dependabot.yml
a58ea1e25254138ff6967438feb948c1a0cc7064

$ git rev-parse 7cc85d28c6946434aa4fb14a0b9b5555d29275ef:.github/dependabot.yml
a58ea1e25254138ff6967438feb948c1a0cc7064

$ git diff --stat 7cc85d28c6946434aa4fb14a0b9b5555d29275ef HEAD -- .github/dependabot.yml
(empty)
```

Both blobs equal `CONFIG_BLOB` (`a58ea1e25254138ff6967438feb948c1a0cc7064`); the DEP-03 encoding
edge holds as a blob-identity comparison, not a YAML comparison. The diff between `PR_COMMIT` and
HEAD for the file is empty.

## REL-12 merge simulation

```
$ git merge-tree --write-tree --name-only 7cc85d28c6946434aa4fb14a0b9b5555d29275ef HEAD; echo "exit:$?"
0fa1506209cceed8abc5d574dc0a919058d17d3c
exit:0
```

`exit:0` — no conflict. With strict branch protection, the merge commit's tree will equal
`PR_COMMIT`'s tree, so this is a faithful simulation of REL-12's later merge of the milestone
branch into `main`.

## Dependabot runs before the merge

```
$ date -u +%FT%TZ
2026-09-12T10:34:57Z

$ gh run list --workflow "Dependabot Updates" --limit 10 --json databaseId,displayTitle,headSha,status,conclusion,createdAt
[{"conclusion":"success","createdAt":"2026-09-07T00:07:01Z","databaseId":34068767739,"displayTitle":"pip in / for docutils - Update #1559879891","headSha":"6181768f64b4cee62a77ac4e26c60c3c976cbb6e","status":"completed"},{"conclusion":"success","createdAt":"2026-09-07T00:07:00Z","databaseId":34068767503,"displayTitle":"pip in /. - Update #1559879825","headSha":"6181768f64b4cee62a77ac4e26c60c3c976cbb6e","status":"completed"},{"conclusion":"success","createdAt":"2026-09-01T09:58:35Z","databaseId":33495005626,"displayTitle":"github_actions in /. - Update #1549284100","headSha":"6181768f64b4cee62a77ac4e26c60c3c976cbb6e","status":"completed"},{"conclusion":"success","createdAt":"2026-08-31T00:05:23Z","databaseId":33343519833,"displayTitle":"pip in / for docutils - Update #1545802480","headSha":"6181768f64b4cee62a77ac4e26c60c3c976cbb6e","status":"completed"},{"conclusion":"success","createdAt":"2026-08-31T00:05:23Z","databaseId":33343519757,"displayTitle":"pip in /. - Update #1545802413","headSha":"6181768f64b4cee62a77ac4e26c60c3c976cbb6e","status":"completed"},{"conclusion":"success","createdAt":"2026-08-30T15:11:54Z","databaseId":33318960633,"displayTitle":"pip in / for docutils - Update #1545558216","headSha":"45962faad21520c72ac9f1e14c7f684050826bb6","status":"completed"},{"conclusion":"success","createdAt":"2026-08-24T00:05:26Z","databaseId":32675547354,"displayTitle":"pip in / for docutils - Update #1537079597","headSha":"d65a612230342068d7bfb97aeb197e4e40af4988","status":"completed"},{"conclusion":"success","createdAt":"2026-08-24T00:05:26Z","databaseId":32675547213,"displayTitle":"pip in /. - Update #1537079538","headSha":"d65a612230342068d7bfb97aeb197e4e40af4988","status":"completed"},{"conclusion":"success","createdAt":"2026-08-22T07:46:38Z","databaseId":32560506401,"displayTitle":"pip in / for docutils - Update #1536102730","headSha":"68b92e24e6ca3df410ca0435d226629ef7ef1e2e","status":"completed"},{"conclusion":"success","createdAt":"2026-08-17T00:07:02Z","databaseId":31981028372,"displayTitle":"pip in /. - Update #1527324717","headSha":"aed773c9807ab871468b1b2a7e1ec36b54e82907","status":"completed"}]

$ gh pr list --state open --author app/dependabot --json number,title,headRefName,labels,createdAt,updatedAt
[{"createdAt":"2026-08-03T00:06:14Z","headRefName":"dependabot/pip/sphinx-typst-stack-12b5b89b5a","labels":[],"number":128,"title":"chore(deps): update docutils requirement from <0.23,>=0.21 to >=0.21,<0.24 in the sphinx-typst-stack group across 1 directory","updatedAt":"2026-09-07T00:07:47Z"},{"createdAt":"2026-07-27T00:07:03Z","headRefName":"dependabot/pip/ruff-gte-0.15-and-lt-0.17","labels":[],"number":123,"title":"chore(deps-dev): update ruff requirement from <0.16,>=0.15 to >=0.15,<0.17","updatedAt":"2026-08-03T20:09:21Z"}]
```

All ten listed Dependabot Updates runs pre-date the merge and all target `pip`/`github_actions`
ecosystems (the last two `pip` runs both `headSha` `6181768f`, from 2026-09-07). No `uv`-ecosystem
run exists yet. Both open dependabot PRs (#123, #128) are unchanged from the planning-time census —
same `headRefName`, same `updatedAt`.

## Non-required job findings (restated from 66-01)

None. 66-01 found all six non-required jobs (`Integration Test - basic`, `Integration Test -
advanced`, `Test Python 3.12 on windows-latest`, `Test Python 3.13 on windows-latest`, `Test Python
3.12 on macos-latest`, `Test Python 3.13 on macos-latest`) `success`, and the fresh
`statusCheckRollup` read above confirms the same for every non-required context queried this task
(`build-docs`, `Repo-wide link check (advisory)` ×2, `Integration Test - basic`, `Integration Test -
advanced`). There is nothing to carry to the checkpoint beyond "all green".

## Owner decision

```
OWNER_DECISION = merge
DECIDED_AT = 2026-09-12T10:38:08Z
```

The owner replied, literally, "merge" to the Task 2 checkpoint (relayed by the coordinator), which
presented `PR_URL`, the six required checks (all `SUCCESS`), the "None" non-required finding, the
blob identity (`CONFIG_BLOB` on both the milestone branch and the PR head), the REL-12 simulation's
`exit:0`, and that `origin/main` was still `BASE_SHA`.

### Gate re-asserted after the decision

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git rev-parse origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e

$ gh pr view 137 --json state,headRefOid
{"headRefOid":"7cc85d28c6946434aa4fb14a0b9b5555d29275ef","state":"OPEN"}

$ gh pr view 137 --json statusCheckRollup --jq '.statusCheckRollup[] | [.name, .conclusion] | @tsv'
Test Python 3.12 on ubuntu-latest	SUCCESS
build-docs	SUCCESS
Repo-wide link check (advisory)	SUCCESS
Repo-wide link check (advisory)	SUCCESS
Test Python 3.13 on ubuntu-latest	SUCCESS
Test Python 3.12 on windows-latest	SUCCESS
Test Python 3.13 on windows-latest	SUCCESS
Test Python 3.12 on macos-latest	SUCCESS
Test Python 3.13 on macos-latest	SUCCESS
Lint and Format Check	SUCCESS
Type Check	SUCCESS
Code Coverage	SUCCESS
Build Package	SUCCESS
Integration Test - basic	SUCCESS
Integration Test - advanced	SUCCESS
```

No difference from the pre-merge gate: `origin/main` is still `BASE_SHA`, PR #137 is still `OPEN`
at `PR_COMMIT`, and all six required contexts still read `SUCCESS`. The merge proceeds.

## D-02 pre-merge snapshot

Both PRs read only, immediately before the merge; neither was commented on, closed, labeled, or
sent an `@dependabot` command.

```
$ date -u +%FT%TZ
2026-09-12T10:38:17Z

$ gh pr view 123 --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABLybpkw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-07-27T00:07:03Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/123#issuecomment-5086046611","viewerDidAuthor":false}],"headRefName":"dependabot/pip/ruff-gte-0.15-and-lt-0.17","headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a","labels":[],"number":123,"state":"OPEN","updatedAt":"2026-08-03T20:09:21Z"}
```

```
$ date -u +%FT%TZ
2026-09-12T10:38:19Z

$ gh pr view 128 --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABM56Sgw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-08-03T00:06:15Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/128#issuecomment-5160997507","viewerDidAuthor":false}],"headRefName":"dependabot/pip/sphinx-typst-stack-12b5b89b5a","headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f","labels":[],"number":128,"state":"OPEN","updatedAt":"2026-09-07T00:07:47Z"}
```

Both PRs are `OPEN`, unchanged from 66-01's planning-time census (same `headRefOid`, same
`updatedAt`, same single dependabot "labels could not be found" comment each). Both snapshot
timestamps (`10:38:17Z`, `10:38:19Z`) are before `MERGED_AT` (`10:38:30Z`, recorded below).

## Merge

```
$ date -u +%FT%TZ
2026-09-12T10:38:23Z
```

`MERGE_STARTED_AT = 2026-09-12T10:38:23Z`.

```
$ gh pr merge 137 --merge --match-head-commit 7cc85d28c6946434aa4fb14a0b9b5555d29275ef
(no stdout)
```

Exactly those flags — no `--admin`, `--auto`, `--squash`, `--rebase` or `--delete-branch`.

```
$ gh pr view 137 --json state,mergeCommit,mergedAt
{"mergeCommit":{"oid":"293f0c2684641f5d4b2f5ed021b565656e38d48c"},"mergedAt":"2026-09-12T10:38:30Z","state":"MERGED"}
```

```
MERGE_SHA = 293f0c2684641f5d4b2f5ed021b565656e38d48c
MERGED_AT = 2026-09-12T10:38:30Z
```

PR #137 is `MERGED` at `MERGE_SHA`, a two-parent merge commit — the style #132 to #136 used.

## Post-merge main

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD
   6181768f..293f0c26  main       -> origin/main

$ git rev-list --parents -n 1 293f0c2684641f5d4b2f5ed021b565656e38d48c
293f0c2684641f5d4b2f5ed021b565656e38d48c 6181768f64b4cee62a77ac4e26c60c3c976cbb6e 7cc85d28c6946434aa4fb14a0b9b5555d29275ef

$ git rev-parse origin/main
293f0c2684641f5d4b2f5ed021b565656e38d48c

$ git diff --name-only 6181768f64b4cee62a77ac4e26c60c3c976cbb6e 293f0c2684641f5d4b2f5ed021b565656e38d48c
.github/dependabot.yml

$ git rev-parse 293f0c2684641f5d4b2f5ed021b565656e38d48c:.github/dependabot.yml
a58ea1e25254138ff6967438feb948c1a0cc7064

$ git show 293f0c2684641f5d4b2f5ed021b565656e38d48c:.github/dependabot.yml | sed -n 4p
  - package-ecosystem: "uv"

$ git diff 293f0c2684641f5d4b2f5ed021b565656e38d48c HEAD -- .github/dependabot.yml
(empty)

$ git merge-tree --write-tree --name-only origin/main HEAD; echo "exit:$?"
3bf4eda872cc92d185772038ba634b9e56c56c2e
exit:0
```

`MERGE_SHA`'s parents are exactly `BASE_SHA` and `PR_COMMIT`. `origin/main` now equals `MERGE_SHA`
(nothing landed on top). `git diff` between `BASE_SHA` and `MERGE_SHA` names only
`.github/dependabot.yml`, whose blob is `CONFIG_BLOB` — line 4 is the uv line. `MERGE_SHA` and this
worktree's HEAD carry an identical copy of the file (empty diff). REL-12's later merge of
`origin/main` into this HEAD still simulates conflict-free (`exit:0`).

### The push CI run on main

```
$ gh run list --workflow=ci.yml --branch main --event push --limit 5 --json databaseId,headSha,status,conclusion,createdAt
[{"conclusion":"","createdAt":"2026-09-12T10:38:32Z","databaseId":34688985508,"headSha":"293f0c2684641f5d4b2f5ed021b565656e38d48c","status":"queued"}, ...]
```

The row whose `headSha` is `MERGE_SHA`: `databaseId 34688985508`, `status: queued` at the time of
this read. Observational only, per the plan — not a merge gate.

## Dependabot runs right after the merge

```
$ date -u +%FT%TZ
2026-09-12T10:38:54Z

$ gh run list --workflow "Dependabot Updates" --limit 10 --json databaseId,displayTitle,headSha,status,conclusion,createdAt
[{"conclusion":"","createdAt":"2026-09-12T10:38:38Z","databaseId":34688990474,"displayTitle":"github_actions in /. - Update #1572468103","headSha":"293f0c2684641f5d4b2f5ed021b565656e38d48c","status":"in_progress"},{"conclusion":"","createdAt":"2026-09-12T10:38:38Z","databaseId":34688990228,"displayTitle":"uv in /. - Update #1572468102","headSha":"293f0c2684641f5d4b2f5ed021b565656e38d48c","status":"in_progress"},{"conclusion":"success","createdAt":"2026-09-07T00:07:01Z","databaseId":34068767739,"displayTitle":"pip in / for docutils - Update #1559879891","headSha":"6181768f64b4cee62a77ac4e26c60c3c976cbb6e","status":"completed"}, ...]
```

**Two Dependabot Updates runs already exist with `createdAt` (`2026-09-12T10:38:38Z`) later than
`MERGED_AT` (`2026-09-12T10:38:30Z`), both at `headSha` `MERGE_SHA`:**
- `databaseId 34688990228`, `displayTitle "uv in /. - Update #1572468102"`, `status: in_progress`
- `databaseId 34688990474`, `displayTitle "github_actions in /. - Update #1572468103"`, `status: in_progress`

This is the first `uv`-ecosystem Dependabot run this repository has ever had, and it started within
8 seconds of the merge landing — a config-change-triggers-immediate-run answer to the D-03 question
`about-the-dependabot-yml-file.md:50` left ambiguous. Both runs were `in_progress` at this read; 66-03
polls them to completion and reads their PR output. No wait was performed here, per the plan's
instruction that 66-03 owns polling.
