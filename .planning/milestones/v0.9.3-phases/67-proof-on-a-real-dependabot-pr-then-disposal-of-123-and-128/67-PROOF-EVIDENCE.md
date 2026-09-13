executor worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout is never touched.

BASE_67_01 = f8707392d4e124c06076dd099cd3988db10b8205

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-adce6c276aa515a42

$ git rev-parse --abbrev-ref HEAD
worktree-agent-adce6c276aa515a42

$ git log --oneline -1
f8707392 docs(67): mark phase 67 executing (wave 1 of 4)
```

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.59ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-adce6c276aa515a42
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-adce6c276aa515a42
Prepared 1 package in 433ms
Installed 81 packages in 50ms
 ... (81 packages, including uv==0.12.13, tox==4.56.1, pytest==9.1.1)
```

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
```

`BASE_67_01 = f8707392d4e124c06076dd099cd3988db10b8205` — this worktree's HEAD at the start of this
plan.

## Phase 66 keys cited

From `66-DEPENDABOT-EVIDENCE.md`, § "SC#1 selection (D-04)":

```
$ sed -n 's/^SC1_PR = //p' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md | head -n 1
138

$ sed -n 's/^SC1_SHA = //p' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md | head -n 1
88088071e02a7411800f504e06b1ded9d6891cc7
```

From `66-DEPENDABOT-EVIDENCE.md`, § "D-05 leg 2 CI uv on the PR head":

```
$ sed -n 's/^SC1_RUN_ID = //p' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md | head -n 1
34689041575
```

These three values are cited, not measured by this task. Every re-read below is a fresh, live `gh`
query against them.

## D-01 proof run

```
$ gh run view "34689041575" --json databaseId,workflowName,status,conclusion,headSha,headBranch,event,attempt,createdAt,updatedAt,url
{"attempt":1,"conclusion":"success","createdAt":"2026-09-12T10:39:53Z","databaseId":34689041575,"event":"pull_request","headBranch":"dependabot/uv/ruff-0.16.6","headSha":"88088071e02a7411800f504e06b1ded9d6891cc7","status":"completed","updatedAt":"2026-09-12T10:46:13Z","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34689041575","workflowName":"CI"}
```

```
PROOF_RUN_ID = 34689041575
PROOF_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7
PROOF_RUN_ATTEMPT = 1
PROOF_RUN_CREATED_AT = 2026-09-12T10:39:53Z
```

`status: completed`, `event: pull_request`, `attempt: 1`, `headSha` equals `SC1_SHA`. No
difference from the recorded values — no HALT.

```
$ gh pr view "138" --json number,title,author,headRefName,headRefOid,baseRefName,createdAt,state
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","createdAt":"2026-09-12T10:39:49Z","headRefName":"dependabot/uv/ruff-0.16.6","headRefOid":"88088071e02a7411800f504e06b1ded9d6891cc7","number":138,"state":"OPEN","title":"chore(deps): bump ruff from 0.15.20 to 0.16.6"}
```

```
PROOF_PR = 138
PROOF_PR_CREATED_AT = 2026-09-12T10:39:49Z
```

The branch `dependabot/uv/ruff-0.16.6` starts with `dependabot/uv/`, the author login
`app/dependabot` matches `dependabot`, and the base is `main`. `headRefOid`
(`88088071e02a7411800f504e06b1ded9d6891cc7`) still equals `PROOF_SHA` — dependabot has not moved
the head since Phase 66.

## Job census

```
$ gh run view "34689041575" --json jobs --jq '.jobs[] | [.databaseId, .name, .status, .conclusion, .startedAt, .completedAt] | @tsv'
103540970888	Type Check	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:40:11Z
103540970962	Integration Test - basic	completed	success	2026-09-12T10:40:13Z	2026-09-12T10:40:25Z
103540970970	Code Coverage	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:44:53Z
103540970973	Integration Test - advanced	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:40:12Z
103540970982	Test Python 3.12 on ubuntu-latest	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:44:03Z
103540970987	Lint and Format Check	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:40:11Z
103540970988	Test Python 3.13 on macos-latest	completed	success	2026-09-12T10:40:08Z	2026-09-12T10:45:34Z
103540970992	Build Package	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:40:10Z
103540970995	Test Python 3.12 on windows-latest	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:46:12Z
103540971026	Test Python 3.13 on ubuntu-latest	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:43:36Z
103540971027	Test Python 3.13 on windows-latest	completed	success	2026-09-12T10:39:56Z	2026-09-12T10:46:11Z
103540971065	Test Python 3.12 on macos-latest	completed	success	2026-09-12T10:40:46Z	2026-09-12T10:44:37Z
```

| # | databaseId | Job | Conclusion |
|---|---|---|---|
| 1 | 103540970888 | Type Check | success |
| 2 | 103540970962 | Integration Test - basic | success |
| 3 | 103540970970 | Code Coverage | success |
| 4 | 103540970973 | Integration Test - advanced | success |
| 5 | 103540970982 | Test Python 3.12 on ubuntu-latest | success |
| 6 | 103540970987 | Lint and Format Check | success |
| 7 | 103540970988 | Test Python 3.13 on macos-latest | success |
| 8 | 103540970992 | Build Package | success |
| 9 | 103540970995 | Test Python 3.12 on windows-latest | success |
| 10 | 103540971026 | Test Python 3.13 on ubuntu-latest | success |
| 11 | 103540971027 | Test Python 3.13 on windows-latest | success |
| 12 | 103540971065 | Test Python 3.12 on macos-latest | success |

```
PROOF_JOB_COUNT = 12
```

All twelve jobs are `success`; zero non-success conclusions. The four OS-lane jobs named
individually: `Test Python 3.12 on windows-latest` (103540970995), `Test Python 3.13 on
windows-latest` (103540971027), `Test Python 3.12 on macos-latest` (103540971065), `Test Python
3.13 on macos-latest` (103540970988).

## Check runs on PROOF_SHA

```
$ gh api "repos/YuSabo90002/typsphinx/commits/88088071e02a7411800f504e06b1ded9d6891cc7/check-runs?per_page=100" --jq '.total_count'
15

$ gh api "repos/YuSabo90002/typsphinx/commits/88088071e02a7411800f504e06b1ded9d6891cc7/check-runs?per_page=100" --jq '.check_runs[] | [.name, .status, .conclusion] | @tsv'
Test Python 3.12 on macos-latest	completed	success
Test Python 3.13 on windows-latest	completed	success
Test Python 3.13 on ubuntu-latest	completed	success
build-docs	completed	success
Test Python 3.12 on windows-latest	completed	success
Build Package	completed	success
Test Python 3.13 on macos-latest	completed	success
Lint and Format Check	completed	success
Test Python 3.12 on ubuntu-latest	completed	success
Integration Test - advanced	completed	success
Code Coverage	completed	success
Integration Test - basic	completed	success
Repo-wide link check (advisory)	completed	success
Type Check	completed	success
Repo-wide link check (advisory)	completed	success
```

```
PROOF_CHECK_COUNT = 15
```

`PROOF_CHECK_COUNT` (15) equals the live `check-runs` `total_count`. Twelve entries are this run's
own CI jobs (see the job census above); the remaining three come from other workflows on the same
commit: `build-docs` and two `Repo-wide link check (advisory)` entries.

## Per-step reads

For every job in the census, `gh api repos/YuSabo90002/typsphinx/actions/jobs/<databaseId> --jq
'.steps[] | [.number, .name, .conclusion] | @tsv'`, verbatim.

### Test Python 3.12 on ubuntu-latest (103540970982)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python 3.12	success
5	Install dependencies	success
6	Run tests with tox	success
7	Upload test results	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

### Test Python 3.13 on ubuntu-latest (103540971026)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python 3.13	success
5	Install dependencies	success
6	Run tests with tox	success
7	Upload test results	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

### Test Python 3.12 on windows-latest (103540970995)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python 3.12	success
5	Install dependencies	success
6	Run tests with tox	success
7	Upload test results	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

### Test Python 3.13 on windows-latest (103540971027)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python 3.13	success
5	Install dependencies	success
6	Run tests with tox	success
7	Upload test results	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

### Test Python 3.12 on macos-latest (103540971065)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python 3.12	success
5	Install dependencies	success
6	Run tests with tox	success
7	Upload test results	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

### Test Python 3.13 on macos-latest (103540970988)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python 3.13	success
5	Install dependencies	success
6	Run tests with tox	success
7	Upload test results	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

### Lint and Format Check (103540970987)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python	success
5	Install dependencies	success
6	Run lint with tox	success
11	Post Install uv	success
12	Post Run actions/checkout@v7	success
13	Complete job	success
```

### Type Check (103540970888)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python	success
5	Install dependencies	success
6	Run type check with tox	success
11	Post Install uv	success
12	Post Run actions/checkout@v7	success
13	Complete job	success
```

**The eight D-01 jobs tabulated** (the six `Test Python …` lanes, `Lint and Format Check`, `Type
Check`): `Install dependencies` conclusion, and the following tox step's name and conclusion.

| Job | `Install dependencies` | Following step | Conclusion |
|---|---|---|---|
| Test Python 3.12 on ubuntu-latest | success | Run tests with tox | success |
| Test Python 3.13 on ubuntu-latest | success | Run tests with tox | success |
| Test Python 3.12 on windows-latest | success | Run tests with tox | success |
| Test Python 3.13 on windows-latest | success | Run tests with tox | success |
| Test Python 3.12 on macos-latest | success | Run tests with tox | success |
| Test Python 3.13 on macos-latest | success | Run tests with tox | success |
| Lint and Format Check | success | Run lint with tox | success |
| Type Check | success | Run type check with tox | success |

Every one of the eight D-01 jobs has `Install dependencies` = `success`, and its tox step
concludes (`success`, in every case observed here — SC#1 asks only that it reach a conclusion).

### Code Coverage (103540970970)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python	success
5	Install dependencies	success
6	Run coverage with tox	success
7	Upload coverage to Codecov	success
8	Upload coverage HTML	success
15	Post Install uv	success
16	Post Run actions/checkout@v7	success
17	Complete job	success
```

### Build Package (103540970992)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python	success
5	Build package	success
6	Verify wheel carries the template bundle	success
7	Check package	success
8	Upload package artifacts	success
15	Post Install uv	success
16	Post Run actions/checkout@v7	success
17	Complete job	success
```

`Check package` (the `--locked` step per `ci.yml:174`) is `success`.

### Integration Test - basic (103540970962)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python	success
5	Install package and dependencies	success
6	Build basic example	success
7	Upload example output	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

### Integration Test - advanced (103540970973)

```
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python	success
5	Install package and dependencies	success
6	Build advanced example	success
7	Upload example output	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

`Install package and dependencies` (the `--locked` step per `ci.yml:202`) is `success` on both
Integration Test jobs.

No D-01 job's `Install dependencies` was anything other than `success`, and no tox step was absent,
`skipped` or null. No HALT.

## No new action on the proof PR

```
$ gh pr view "138" --json comments --jq '[.comments[] | select(.body | test("@dependabot"))] | length'
0

$ gh pr view "138" --json comments --jq '.comments[] | [.author.login, .createdAt] | @tsv'
dependabot	2026-09-12T10:39:49Z
```

Zero comments contain `@dependabot`; the PR's sole comment is dependabot's own automated "labels
could not be found" notice, timestamped at PR creation.

The run (`PROOF_RUN_ID`) was created at `PROOF_RUN_CREATED_AT`
(`2026-09-12T10:39:53Z`) by dependabot's own push during Phase 66 execution, so it predates
Phase 67 (D-01). `attempt` `1` means it was never rerun. This plan issued no rerun, no dispatch and
no `@dependabot` command against `PROOF_PR` or run `PROOF_RUN_ID` — every command run above is a
read (`gh run view`, `gh pr view`, `gh api .../check-runs`, `gh api .../actions/jobs/<id>`).

```
$ date -u +%FT%TZ
2026-09-12T13:18:08Z
```

```
DEP02_PROOF_AT = 2026-09-12T13:18:08Z
```

## D-02 citations

From `66-MAIN-PR-EVIDENCE.md` § "D-02 pre-merge snapshot":

```
Both PRs read only, immediately before the merge; neither was commented on, closed, labeled, or
sent an `@dependabot` command.

$ date -u +%FT%TZ
2026-09-12T10:38:17Z

$ gh pr view 123 --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null, ..., "headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a", ...,
 "number":123,"state":"OPEN","updatedAt":"2026-08-03T20:09:21Z"}

$ date -u +%FT%TZ
2026-09-12T10:38:19Z

$ gh pr view 128 --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null, ..., "headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f", ...,
 "number":128,"state":"OPEN","updatedAt":"2026-09-07T00:07:47Z"}

Both PRs are OPEN, unchanged from 66-01's planning-time census. Both snapshot timestamps
(10:38:17Z, 10:38:19Z) are before MERGED_AT (10:38:30Z).
```

From `66-DEPENDABOT-EVIDENCE.md` § "D-02 post-merge snapshot":

```
Both PRs read only, after the first post-merge dependabot runs completed; neither was commented on,
closed, labeled, or sent an `@dependabot` command.

$ date -u +%FT%TZ
2026-09-12T10:58:41Z

$ gh pr view 123 --json ... {"closed":false,"closedAt":null, ...,
 "headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a", ..., "state":"OPEN",
 "updatedAt":"2026-08-03T20:09:21Z"}

$ date -u +%FT%TZ
2026-09-12T10:58:45Z

$ gh pr view 128 --json ... {"closed":false,"closedAt":null, ...,
 "headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f", ..., "state":"OPEN",
 "updatedAt":"2026-09-07T00:07:47Z"}

Both PRs are OPEN, unchanged from 66-02's pre-merge snapshot. Zero owner-authored comments and zero
owner-authored timeline events on either PR after DECIDED_AT (2026-09-12T10:38:08Z). Neither PR was
closed.
```

From `66-DEPENDABOT-EVIDENCE.md` § "uv pull requests", the row for `PROOF_PR` (#138):

```
| number | title | branch | state | labels | createdAt | opened while #123 open | opened while #128 open |
|---|---|---|---|---|---|---|---|
| 138 | bump ruff 0.15.20→0.16.6 | dependabot/uv/ruff-0.16.6 | OPEN | [] | 2026-09-12T10:39:49Z | yes | yes |
```

`#138`'s `createdAt` (`2026-09-12T10:39:49Z`) equals `PROOF_PR_CREATED_AT`, and both "opened while
… open" columns read `yes`.

## The "can" branch, re-checked live

```
$ gh pr view 123 --json createdAt
{"createdAt":"2026-07-27T00:07:03Z"}

$ gh pr view 128 --json createdAt
{"createdAt":"2026-08-03T00:06:14Z"}

$ gh pr view 138 --json createdAt
{"createdAt":"2026-09-12T10:39:49Z"}
```

`#123` (`2026-07-27T00:07:03Z`) and `#128` (`2026-08-03T00:06:14Z`) both predate `PROOF_PR`'s
`createdAt` (`2026-09-12T10:39:49Z`, equal to `PROOF_PR_CREATED_AT`). The cited § uv pull requests
row for `PROOF_PR` reads `yes` and `yes`.

```
SC2_BRANCH = can
```

A `uv`-ecosystem PR can open for a dependency that already has an open `pip`-ecosystem PR (#138
opened while #123 was open), so SC#2's "both stay open until criterion 1 is satisfied" branch
applies.

## D-02 re-snapshot

Both PRs read only, after the D-01 proof was recorded (`DEP02_PROOF_AT = 2026-09-12T13:18:08Z`);
neither was commented on, closed, labeled, or sent an `@dependabot` command.

```
$ date -u +%FT%TZ
2026-09-12T13:20:35Z
```

```
SNAP_123_AT = 2026-09-12T13:20:35Z

$ gh pr view "123" --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABLybpkw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-07-27T00:07:03Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/123#issuecomment-5086046611","viewerDidAuthor":false}],"headRefName":"dependabot/pip/ruff-gte-0.15-and-lt-0.17","headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a","labels":[],"number":123,"state":"OPEN","updatedAt":"2026-08-03T20:09:21Z"}

$ gh api --paginate "repos/YuSabo90002/typsphinx/issues/123/events" --jq '.[] | [.event, .actor.login, .created_at] | @tsv'
referenced	YuSabo90002	2026-07-27T21:57:28Z
head_ref_force_pushed	dependabot[bot]	2026-07-27T22:04:57Z
head_ref_force_pushed	dependabot[bot]	2026-07-28T20:59:56Z
```

`#123`: `headRefOid` (`1c905bb8...`) — **unchanged** from Phase 66's post-merge snapshot.
`updatedAt` (`2026-08-03T20:09:21Z`) — **unchanged**. Comment count (1, dependabot's own) —
**unchanged**. No timeline event after Phase 66's snapshot other than dependabot's own force-pushes,
which pre-date `DEP02_PROOF_AT` and `SNAP_123_AT`, and no owner action.

```
$ date -u +%FT%TZ
2026-09-12T13:20:42Z
```

```
SNAP_128_AT = 2026-09-12T13:20:42Z

$ gh pr view "128" --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABM56Sgw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-08-03T00:06:15Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/128#issuecomment-5160997507","viewerDidAuthor":false}],"headRefName":"dependabot/pip/sphinx-typst-stack-12b5b89b5a","headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f","labels":[],"number":128,"state":"OPEN","updatedAt":"2026-09-07T00:07:47Z"}

$ gh api --paginate "repos/YuSabo90002/typsphinx/issues/128/events" --jq '.[] | [.event, .actor.login, .created_at] | @tsv'
renamed	dependabot[bot]	2026-08-03T20:10:21Z
head_ref_force_pushed	dependabot[bot]	2026-08-03T20:10:21Z
head_ref_force_pushed	dependabot[bot]	2026-08-10T00:07:23Z
head_ref_force_pushed	dependabot[bot]	2026-08-11T05:35:02Z
head_ref_force_pushed	dependabot[bot]	2026-08-15T03:10:41Z
head_ref_force_pushed	dependabot[bot]	2026-08-17T00:08:00Z
head_ref_force_pushed	dependabot[bot]	2026-08-22T07:47:33Z
head_ref_force_pushed	dependabot[bot]	2026-08-24T00:06:25Z
head_ref_force_pushed	dependabot[bot]	2026-08-30T15:12:59Z
head_ref_force_pushed	dependabot[bot]	2026-08-31T00:06:18Z
```

`#128`: `headRefOid` (`000859f7...`) — **unchanged** from Phase 66's post-merge snapshot.
`updatedAt` (`2026-09-07T00:07:47Z`) — **unchanged**. Comment count (1, dependabot's own) —
**unchanged**. All timeline events are dependabot's own historical force-pushes, all pre-dating
`DEP02_PROOF_AT`; no owner action, no close.

Neither PR was commented on, closed, labeled or `@dependabot`-commanded by this task.

```
MECHANICAL_CLOSE = none
```

Both `#123` and `#128` are `OPEN`.

## DEP-02 verdict

ROADMAP Phase 67 SC#1, quoted literally:

> **On a real dependabot PR, the install step succeeds and the jobs actually run — observed.**
> A PR opened by `dependabot[bot]` under the `uv` ecosystem has a completed check history in
> which the `uv sync --locked` step **succeeds** and the test, lint and type jobs **run to a
> conclusion** rather than dying before the first test. The evidence is the PR's own check runs
> and step logs. A hand-made branch carrying a fresh `uv.lock` does **not** satisfy this
> criterion, however green it is (DEP-02).

Each clause mapped to the section that observed it:

| SC#1 clause | Observing section |
|---|---|
| a PR opened by dependabot under `uv` | § "D-01 proof run" — `PROOF_PR` #138, branch `dependabot/uv/ruff-0.16.6`, author `app/dependabot` |
| `uv sync --locked` succeeds | § "Per-step reads" — all eight D-01 jobs' `Install dependencies` step `success` |
| the test, lint and type jobs run to a conclusion | § "Per-step reads" — all eight D-01 jobs' following tox step `success` |
| the evidence is the PR's own check runs and step logs, not a hand-made branch | § "D-01 proof run", § "Job census", § "Check runs on PROOF_SHA", § "Per-step reads" — every fact is read live from `PROOF_RUN_ID`/`PROOF_PR`, never from a fresh branch or `uv.lock` regeneration |

Task 1 (D-01) held: the run is `completed`/`success` (attempt 1) at `PROOF_SHA`, all 12 jobs and 15
check runs are transcribed, and every one of the eight Lint/Type/Test jobs shows `Install
dependencies` `success` followed by a concluded tox step. Steps 1–3 above hold: `SC2_BRANCH = can`,
the re-snapshot shows both `#123` and `#128` `OPEN` later than `DEP02_PROOF_AT`, and
`MECHANICAL_CLOSE = none`.

```
DEP02_VERDICT = MET
```

**Flagged assumption A-67-01** (DEP-02, unclassified): this verdict assumes run `34689041575`'s job
metadata, step conclusions and logs stay readable through `gh` until phase verification (GitHub
Actions retention) — confirmed readable as of `DEP02_PROOF_AT`, but not guaranteed to remain so
indefinitely.

## Handoff

`67-02` and `67-03` gate on:

```
DEP02_VERDICT = MET
SC2_BRANCH = can
MECHANICAL_CLOSE = none
PROOF_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7
```

The dispositions (D-03, D-04, D-05, in `67-02`, `67-03` and `67-04`) start only now — the D-01 →
D-02 → dispositions order holds. Neither #123 nor #128 nor #138 was merged, closed, commented on,
labeled, or sent an `@dependabot` command by this plan.
