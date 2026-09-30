# Phase 69 — CI Evidence (D-13, SC#3 CI half)

This is the phase's only push and CI dispatch. `PUSHED_SHA` carries every product-tree change of
this phase; the only earlier plans (69-01, 69-02) touch `CHANGELOG.md` and `.planning/` only, and
that CHANGELOG edit is the change this run's tip carries. Every later commit of this phase touches
only `.planning/`, which no CI job reads.

BASE_69_04 = becd70c31bfed573dc10cdc20dcf7a30d57edd57
PUSHED_SHA = becd70c31bfed573dc10cdc20dcf7a30d57edd57
ORIGIN_BEFORE = d9c7555323e843b5a389ed4354ce656d2fd05ca2
PUSH_AT = 2026-09-12T22:47:06Z
RUN_ID = 34723677990
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990
LOCK_RUFF_VERSION = 0.15.20

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T22:46:25Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8d6f435633123829

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning line (`CLAUDE.md` § "Worktree-isolated execution"):

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.59ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8d6f435633123829
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8d6f435633123829
Prepared 1 package in 448ms
Installed 81 packages in 50ms
 ... (81 packages, including tox-uv==1.36.0, tox-uv-bare==1.36.0, uv==0.12.13, tox==4.56.1,
      ruff==0.15.20, pytest==9.1.1)
```

Pre-dispatch locked sync — every `ci.yml` job begins with this step, so a stale lock would fail all
twelve lanes before any signal:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --locked; echo "exit:$?"
Resolved 91 packages in 2ms
Checked 81 packages in 0.66ms
exit:0
```

Before any commit:

```
$ git rev-parse HEAD
becd70c31bfed573dc10cdc20dcf7a30d57edd57
```

`BASE_69_04 = becd70c31bfed573dc10cdc20dcf7a30d57edd57`.

## Wave-1 gate

The precondition's four checks, each re-run inside this worktree:

```
$ git show gsd/v0.9.3-toolchain-and-dependency-update-repair:CHANGELOG.md \
    | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' \
    | grep -c '^- \*\*'
3

$ git show gsd/v0.9.3-toolchain-and-dependency-update-repair:CHANGELOG.md \
    | awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' \
    | grep -oE '(TOX-0[1-4]|DEP-0[1-5]|NIX-0[1-8]|DOC-(19|20|21))' | sort -u | wc -l
20

$ git cat-file -e gsd/v0.9.3-toolchain-and-dependency-update-repair:.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CLOSEOUT-GUARD.md; echo "exit:$?"
exit:0
```

Three bold-lead bullets, 20 distinct requirement IDs, and the closeout-guard file both exist at the
canonical ref. Wave 1 (69-01's CHANGELOG edit, 69-02's closeout guard) is present on the tip this
plan is about to push. No `## HALT` is written.

## Tip identity and fence

```
$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
becd70c31bfed573dc10cdc20dcf7a30d57edd57

$ git log --oneline -1 becd70c31bfed573dc10cdc20dcf7a30d57edd57
becd70c3 docs(phase-69): update tracking after wave 1, mark wave 2 executing
```

`PUSHED_SHA = becd70c31bfed573dc10cdc20dcf7a30d57edd57`. This worktree was cut from the canonical
tip after wave 1 merged, and this task had not committed at the time of measurement, so `PUSHED_SHA`
equals both `BASE_69_04` and this worktree's own HEAD at measurement time.

```
$ git diff --name-only HEAD becd70c31bfed573dc10cdc20dcf7a30d57edd57 -- . ':(exclude).planning'
(empty)
```

The pushed tree equals this worktree's product tree.

```
$ git show becd70c31bfed573dc10cdc20dcf7a30d57edd57:pyproject.toml | sed -n 7p
version = "0.9.2"
```

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base becd70c31bfed573dc10cdc20dcf7a30d57edd57 origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e

$ git diff --name-only 6181768f64b4cee62a77ac4e26c60c3c976cbb6e becd70c31bfed573dc10cdc20dcf7a30d57edd57 -- typsphinx .github/workflows
(empty)
```

Nothing under `typsphinx/` or `.github/workflows/` differs from the merge-base with `origin/main`
(constraint 13; CI is unchanged).

```
$ git merge-base --is-ancestor origin/main becd70c31bfed573dc10cdc20dcf7a30d57edd57; echo "exit:$?"
exit:1
```

`origin/main` is not an ancestor of the pushed tip (D-06: the milestone branch does not absorb
`main` in this phase).

```
$ git tag --points-at becd70c31bfed573dc10cdc20dcf7a30d57edd57
(empty)
```

No tag points at the pushed tip.

```
$ git show becd70c31bfed573dc10cdc20dcf7a30d57edd57:uv.lock | grep -A1 -xF 'name = "ruff"' | sed -n 's/^version = "\(.*\)"$/\1/p'
0.15.20
```

`LOCK_RUFF_VERSION = 0.15.20`.

## D-14 decoy census

Run immediately before the push, with nothing but the fence measurements above in between:

```
$ git branch --list 'gsd/v0.9.3*' -v
+ gsd/v0.9.3-toolchain-and-dependency-update-repair becd70c3 [ahead 132] docs(phase-69): update tracking after wave 1, mark wave 2 executing

$ git ls-remote --heads origin 'gsd/v0.9.3*'
d9c7555323e843b5a389ed4354ce656d2fd05ca2	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

No `gsd/v0.9.3-milestone` decoy exists, locally or on origin. Only the canonical branch is present
in either listing. No decoy handling was required — nothing to delete, nothing to halt on.

## Push

```
$ git fetch origin gsd/v0.9.3-toolchain-and-dependency-update-repair
From https://github.com/YuSabo90002/typsphinx
 * branch              gsd/v0.9.3-toolchain-and-dependency-update-repair -> FETCH_HEAD

$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
d9c7555323e843b5a389ed4354ce656d2fd05ca2	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

`ORIGIN_BEFORE = d9c7555323e843b5a389ed4354ce656d2fd05ca2`.

```
$ git merge-base --is-ancestor d9c7555323e843b5a389ed4354ce656d2fd05ca2 becd70c31bfed573dc10cdc20dcf7a30d57edd57; echo "exit:$?"
exit:0
```

`ORIGIN_BEFORE` is an ancestor of `PUSHED_SHA` — a fast-forward is possible.

```
$ git config --get push.followTags
(exit 1 — unset)

$ date -u +%FT%TZ
2026-09-12T22:47:06Z
```

`PUSH_AT = 2026-09-12T22:47:06Z`.

```
$ git push --no-follow-tags origin gsd/v0.9.3-toolchain-and-dependency-update-repair
To https://github.com/YuSabo90002/typsphinx.git
   d9c75553..becd70c3  gsd/v0.9.3-toolchain-and-dependency-update-repair -> gsd/v0.9.3-toolchain-and-dependency-update-repair
```

No pull-request hint was printed by GitHub on this push, and none would have been acted on
regardless. No force, no tags, no other ref.

```
$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
becd70c31bfed573dc10cdc20dcf7a30d57edd57	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair

$ git ls-remote --tags origin | grep 'v0\.9\.3' || echo "NO_MATCH"
NO_MATCH
```

The origin head now equals `PUSHED_SHA`, advanced from `ORIGIN_BEFORE` as a fast-forward. No
`refs/tags/v0.9.3*` line exists on origin.

## Dispatch

```
$ gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair
https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990

$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-12T22:47:18Z","databaseId":34723677990,"headSha":"becd70c31bfed573dc10cdc20dcf7a30d57edd57","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990"},{"createdAt":"2026-09-12T07:55:42Z","databaseId":34681968010,"headSha":"d9c7555323e843b5a389ed4354ce656d2fd05ca2","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34681968010"},{"createdAt":"2026-09-11T15:52:41Z","databaseId":34618719267,"headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267"}]
```

`RUN_ID = 34723677990`, `RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990`.

The listed row's `headSha` (`becd70c31bfed573dc10cdc20dcf7a30d57edd57`) equals `PUSHED_SHA`, and its
`createdAt` (`2026-09-12T22:47:18Z`) is later than `PUSH_AT` (`2026-09-12T22:47:06Z`). No
registration lag was encountered — the run was listed on the first query. Exactly one
`gh workflow run CI` was issued. The two older entries are Phase 65's own dispatch (`34681968010`,
the pre-this-phase baseline) and Phase 64's dispatch (`34618719267`) — neither is this plan's run.

This plan's own evidence commits land after the push and touch only `.planning/`, which no CI job
reads.

## Run

Waited in the foreground: `timeout 590 gh run watch 34723677990 --interval 30` (Bash tool timeout
600000ms, no `run_in_background`). The single foreground watch call ran until the tool's own
590-second wrapper elapsed while the run was still `in_progress`; the immediate follow-up
`gh run view` poll then found the run already `completed`, so no second watch call was needed.

```
$ gh run view 34723677990 --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
{"conclusion":"success","createdAt":"2026-09-12T22:47:18Z","headSha":"becd70c31bfed573dc10cdc20dcf7a30d57edd57","status":"completed","updatedAt":"2026-09-12T22:53:54Z","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34723677990","workflowName":"CI"}
```

RUN_HEAD_SHA = becd70c31bfed573dc10cdc20dcf7a30d57edd57
RUN_CONCLUSION = success

`status: completed`, `conclusion: success`, `workflowName: CI`, `headSha` equal to `PUSHED_SHA`.

## Job census

```
$ gh run view 34723677990 --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
Code Coverage	success
Integration Test - basic	success
Lint and Format Check	success
Test Python 3.12 on macos-latest	success
Test Python 3.13 on macos-latest	success
Build Package	success
Test Python 3.12 on windows-latest	success
Test Python 3.13 on windows-latest	success
Integration Test - advanced	success
Test Python 3.13 on ubuntu-latest	success
Test Python 3.12 on ubuntu-latest	success
Type Check	success
```

Twelve jobs, numbered as reported by the API (transcription order only; no assertion depends on
this order):

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Code Coverage | success |
| 2 | Integration Test - basic | success |
| 3 | Lint and Format Check | success |
| 4 | Test Python 3.12 on macos-latest | success |
| 5 | Test Python 3.13 on macos-latest | success |
| 6 | Build Package | success |
| 7 | Test Python 3.12 on windows-latest | success |
| 8 | Test Python 3.13 on windows-latest | success |
| 9 | Integration Test - advanced | success |
| 10 | Test Python 3.13 on ubuntu-latest | success |
| 11 | Test Python 3.12 on ubuntu-latest | success |
| 12 | Type Check | success |

JOB_COUNT = 12
NON_SUCCESS_JOBS = 0

This is exactly the twelve jobs `ci.yml` defines: 6 `test` matrix cells (3 OS × 2 Python) +
`Lint and Format Check` + `Type Check` + `Code Coverage` + `Build Package` +
`Integration Test - basic` + `Integration Test - advanced`. All twelve are `success`.

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

## ruff's verdict

Quoted verbatim from the `Lint and Format Check` job's `Run lint with tox` step (job id
`103633947841`):

```
$ gh run view --job 103633947841 --log
...
Lint and Format Check	Install dependencies	2026-09-12T22:47:34.6141806Z  + ruff==0.15.20
Lint and Format Check	Run lint with tox	2026-09-12T22:47:35.4474016Z lint: commands[0]> black --check .
Lint and Format Check	Run lint with tox	2026-09-12T22:47:39.6531078Z All done! ✨ 🍰 ✨
Lint and Format Check	Run lint with tox	2026-09-12T22:47:39.6531610Z 355 files would be left unchanged.
Lint and Format Check	Run lint with tox	2026-09-12T22:47:39.6769749Z lint: commands[1]> ruff check .
Lint and Format Check	Run lint with tox	2026-09-12T22:47:39.7420882Z All checks passed!
Lint and Format Check	Run lint with tox	2026-09-12T22:47:39.7442471Z   lint: OK (4.51=setup[0.21]+cmd[4.23,0.07] seconds)
```

CI_RUFF_VERSION = 0.15.20

`CI_RUFF_VERSION` (`0.15.20`) equals `LOCK_RUFF_VERSION` (`0.15.20`, from `uv.lock` at
`PUSHED_SHA`). `black --check .` passed (`All done! ✨ 🍰 ✨` / `355 files would be left
unchanged.`), `ruff check .` passed (`All checks passed!`), and the tox environment reports
`lint: OK`. This is `ci.yml`'s `Run lint with tox` step; the differently-named lint step belongs to
`release.yml`, which this plan never searches and never triggers, and whose step name is absent
from this evidence. CI holds lint authority (constraint 7); 69-03's local `ruff check .` is set
beside this one in `69-06`, not here.

## Dispatch count and no release run

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 50 --json headSha
[{"headSha":"becd70c31bfed573dc10cdc20dcf7a30d57edd57"},{"headSha":"d9c7555323e843b5a389ed4354ce656d2fd05ca2"},{"headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5"}]
```

DISPATCH_COUNT = 1

Exactly one entry carries `headSha` equal to `PUSHED_SHA` (`becd70c31bfed573dc10cdc20dcf7a30d57edd57`).
The other two are Phase 65's dispatch (`d9c75553…`) and Phase 64's dispatch (`7afbf5b2…`), neither
of which is this plan's tip.

```
$ gh run list --workflow=release.yml --limit 20 --json headSha
[{"headSha":"45962faad21520c72ac9f1e14c7f684050826bb6"},{"headSha":"68b92e24e6ca3df410ca0435d226629ef7ef1e2e"},{"headSha":"78e01e53641433a34c1bd8834b6252187fcae4ba"},{"headSha":"48bf135428bb093a77a432d93d16088ce6930342"},{"headSha":"75fd8ed55f4fca206474f9e3aa934921588b52d5"},{"headSha":"839d77f38ffa67f18696265b361f7dcef92f679b"},{"headSha":"2bf6ef318773b239e4ab20b41fbe40ce91337584"},{"headSha":"7f6db629351aa1229a2a07614b6a6f201001ad80"},{"headSha":"54b8fc90df0359b049a1cd9936f03c76d1169f74"},{"headSha":"27e77403f1d62ebec9f36c2c4a9b7c8e16067fc9"},{"headSha":"cc26b4723f671c0ac0dfdae687b6bee722aa6dd0"},{"headSha":"ea153bfca933b92ea23fdfa72efba2afb100f29b"},{"headSha":"dae500a1f2065691972e03cc70a9bf73a90cd26f"},{"headSha":"a2aca47b367b6a4320be6785202cacffad937c5e"},{"headSha":"415498a8cfa7dc21aa09871d4d3b061ed7ba48a2"},{"headSha":"445af8c4b8a30d924d30341bd87b476fa7d0b486"},{"headSha":"0ed33d10acbee8fa935850bcf77404d55832edc9"},{"headSha":"08aeb4b3cfba2293103aefa201b85c89397f50f3"},{"headSha":"28a80a6cc13288eb8c75612693d34a25ae865142"},{"headSha":"c1e2db714cfacd8ef96759ccdebf6e09f5c9152a"}]
```

RELEASE_RUNS_AT_PUSHED = 0

None of the 20 most recent `release.yml` runs carry `headSha` equal to `PUSHED_SHA`. No release
workflow ever ran against this tip.

## D-13 final tip

This run (`RUN_ID = 34723677990`, `headSha = becd70c31bfed573dc10cdc20dcf7a30d57edd57`) is D-13's
single dispatch for Phase 69. `PUSHED_SHA` carries every product-tree change of the phase — the
CHANGELOG edit authored by 69-01 — since the `## Tip identity and fence` section above showed the
pushed tree is byte-identical to this worktree's own HEAD, which itself carries wave 1's merged
commits and nothing else. Every later commit of this phase (this plan's own evidence commits, and
any commit 69-03/69-05 make) touches only `.planning/`, which no CI job reads; plan 69-06 proves
this with its own empty product-tree diff against `PUSHED_SHA`. D-13 permits a second dispatch only
for a code-affecting change; none has occurred and none is warranted here.

## SC#3 CI verdict

The run is `completed` and `success`, `JOB_COUNT = 12`, `NON_SUCCESS_JOBS = 0`, and all four named
lanes (`Test Python 3.12 on windows-latest`, `Test Python 3.13 on windows-latest`,
`Test Python 3.12 on macos-latest`, `Test Python 3.13 on macos-latest`) are `success`.

SC3_CI_VERDICT = MET
