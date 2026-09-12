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
