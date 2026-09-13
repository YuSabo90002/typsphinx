# Phase 70 — Push, CI and SC Roll-up

BASE_70_13 = e70e31fba9039133a153a5bba16577d7b2f889c1
(`git rev-parse HEAD`, recorded before any commit in this plan)

## Head check and provisioning

`date -u +%FT%TZ`:
```
2026-09-13T06:05:41Z
```

`pwd -P`:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab09a82b0853c77d4
```

`test -f .git; echo "exit:$?"`:
```
exit:0
```

`grep -q typsphinx-fhs-run "$(command -v uv)"; echo "shim: OK"`:
```
shim: OK
```

Provisioning command:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```
Ran to completion; final resolved lines included `typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab09a82b0853c77d4)`, `ruff==0.16.6`, `uv==0.12.13`. Exit 0.

VENV_VERSION_INFO = 3.13.13
(`.venv/pyvenv.cfg`: `home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`, `version_info = 3.13.13` — equal to 70-02's/`70-BASELINE-EVIDENCE.md`'s `VENV_HOME`/`VENV_VERSION_INFO`.)

## Wave-5 gate

Quoted from the evidence files at HEAD (`e70e31fba9039133a153a5bba16577d7b2f889c1`), none carrying a `## HALT` heading (`grep -c '^## HALT'` returned `0` for all three):

From `70-AFTER-STATIC-EVIDENCE.md`:
```
SC1_VERDICT = MET
SC2_VERDICT = MET
LEG_A_VERDICT = MET
LEG_C_VERDICT = MET
LEG_E_VERDICT = MET
```

From `70-AFTER-RUNTIME-EVIDENCE.md`:
```
LEG_B_VERDICT = MET
LEG_D_VERDICT = MET
```

From `70-DOCS-DIFF-EVIDENCE.md`:
```
DOC23_VERDICT = MET
```

All eight keys are `MET`, and no evidence file carries a `## HALT` heading.

## Gate quartet on the tip

`uv lock --check`:
```
Resolved 91 packages in 3ms
```
exit:0

`uv run ruff check .`:
```
All checks passed!
```
exit:0

`uv run black --check .`:
```
All done! ✨ 🍰 ✨
355 files would be left unchanged.
```
exit:0

`uv run mypy typsphinx/`:
```
Success: no issues found in 9 source files
```
exit:0

`LC_ALL=C uv run pytest -q -p no:cacheprovider` (summary line):
```
1547 passed, 1 skipped in 128.14s (0:02:08)
```
exit:0

QUARTET = PASS

## Census and decoy (constraint 9)

Run immediately before the push, with only the Tip identity measurements (below) in between.

`git branch --list 'gsd/v0.9.4*' -v`:
```
* gsd/v0.9.4-typing-modernization e70e31fb docs(phase-70): update tracking after wave 5, mark wave 6 executing
```
(shown with `*` because the main checkout has this branch checked out; the local `gsd/v0.9.4*` set contains only the canonical branch — no decoy.)

`git ls-remote --heads origin 'refs/heads/gsd/v0.9.4*'`:
```
(no output — origin has no gsd/v0.9.4* ref yet)
```

`git -C "$MAIN" symbolic-ref HEAD` (read directly from `/home/yuta/Documents/typsphinx/.git/HEAD`, since a worktree-isolation guard refuses a `git -C` redirect to the main checkout from this worktree):
```
ref: refs/heads/gsd/v0.9.4-typing-modernization
```

Decoy handling: `gsd/v0.9.4-milestone` is absent from origin (per the `ls-remote` above) and absent locally (per the `branch --list` above).

DECOY = ABSENT

## Tip identity

PUSHED_SHA = e70e31fba9039133a153a5bba16577d7b2f889c1

`git diff --name-only HEAD "$PUSHED_SHA" -- . ':(exclude).planning'`:
```
(empty)
```

`git show "$PUSHED_SHA:pyproject.toml"` version line:
```
version = "0.9.2"
```

`git diff --quiet "$PHASE_BASE_SHA" "$PUSHED_SHA" -- .github/workflows; echo "exit:$?"` (PHASE_BASE_SHA = `697a113221a8a267d7e8c6dd1f2b95672f9454d2`, from `70-BASELINE-EVIDENCE.md`):
```
exit:0
```

`git tag --points-at "$PUSHED_SHA"`:
```
(empty)
```

LOCK_RUFF_VERSION_TIP = 0.16.6
(`git show "$PUSHED_SHA:uv.lock"`: `name = "ruff"` / `version = "0.16.6"` — equal to 70-02's `LOCK_RUFF_VERSION` in `70-BASELINE-EVIDENCE.md`.)

## Push

ORIGIN_BEFORE = ABSENT
(`git ls-remote --heads origin refs/heads/gsd/v0.9.4-typing-modernization` printed nothing before the push.)

PUSH_AT = 2026-09-13T06:09:08Z

`git push --no-follow-tags -u origin gsd/v0.9.4-typing-modernization`:
```
remote:
remote: Create a pull request for 'gsd/v0.9.4-typing-modernization' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.4-typing-modernization
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.4-typing-modernization -> gsd/v0.9.4-typing-modernization
branch 'gsd/v0.9.4-typing-modernization' set up to track 'origin/gsd/v0.9.4-typing-modernization'.
```
GitHub's pull-request hint was not acted on — no PR was opened.

Post-push checks:
- `git ls-remote --heads origin refs/heads/gsd/v0.9.4-typing-modernization` → `e70e31fba9039133a153a5bba16577d7b2f889c1` (equals PUSHED_SHA)
- `git config --get branch.gsd/v0.9.4-typing-modernization.remote` → `origin`
- `git config --get branch.gsd/v0.9.4-typing-modernization.merge` → `refs/heads/gsd/v0.9.4-typing-modernization`
- `git ls-remote --tags origin` lists `refs/tags/v0.9.2` and no `refs/tags/v0.9.4` (full v0.1.0b1..v0.9.2 tag ladder present, no v0.9.4 line)

## Dispatch

`gh workflow run CI --ref gsd/v0.9.4-typing-modernization` (issued exactly once):
```
https://github.com/YuSabo90002/typsphinx/actions/runs/34742047126
```

`gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url`:
```json
[{"createdAt":"2026-09-13T06:09:27Z","databaseId":34742047126,"headSha":"e70e31fba9039133a153a5bba16577d7b2f889c1","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34742047126"}]
```
`headSha` equals PUSHED_SHA and `createdAt` (06:09:27Z) follows PUSH_AT (06:09:08Z). No registration lag — resolved on the first list query.

RUN_ID = 34742047126
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34742047126

## Run

Waited in the foreground: `timeout 590 gh run watch 34742047126 --interval 30` (Bash tool `timeout` 600000, no `run_in_background`), then `gh run view 34742047126 --json status,conclusion` confirmed `status: completed`. The run finished inside the first watch window — no second poll was needed, and no second run was ever dispatched.

`gh run view "$RUNID" --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt`:
```json
{"conclusion":"success","createdAt":"2026-09-13T06:09:27Z","headSha":"e70e31fba9039133a153a5bba16577d7b2f889c1","status":"completed","updatedAt":"2026-09-13T06:16:19Z","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34742047126","workflowName":"CI"}
```

RUN_HEAD_SHA = e70e31fba9039133a153a5bba16577d7b2f889c1
RUN_CONCLUSION = success

## Job census

EXPECTED_JOB_COUNT = 12
(arithmetic: test matrix 3 os × 2 python-version = 6, plus `Lint and Format Check` + `Type Check` + `Code Coverage` + `Build Package` = 4, plus integration matrix 2 `example` entries = 2; 6 + 4 + 2 = 12)

`gh run view "$RUNID" --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'`:

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Lint and Format Check | success |
| 2 | Integration Test - advanced | success |
| 3 | Test Python 3.13 on ubuntu-latest | success |
| 4 | Build Package | success |
| 5 | Code Coverage | success |
| 6 | Test Python 3.12 on windows-latest | success |
| 7 | Integration Test - basic | success |
| 8 | Type Check | success |
| 9 | Test Python 3.13 on windows-latest | success |
| 10 | Test Python 3.12 on macos-latest | success |
| 11 | Test Python 3.13 on macos-latest | success |
| 12 | Test Python 3.12 on ubuntu-latest | success |

JOB_COUNT = 12
NON_SUCCESS_JOBS = 0

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

`Lint and Format Check` job id: 103683279265. Quoted from `gh run view --job 103683279265 --log`:

`Install dependencies` step, the `+ ruff==` line:
```
Lint and Format Check	Install dependencies	2026-09-13T06:09:40.3979771Z  + ruff==0.16.6
```
CI_RUFF_VERSION = 0.16.6 — equal to `LOCK_RUFF_VERSION_TIP` (0.16.6).

`Run lint with tox` step, `commands[0]> black --check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-13T06:09:41.1366422Z lint: commands[0]> black --check .
Lint and Format Check	Run lint with tox	2026-09-13T06:09:44.2203550Z All done! ✨ 🍰 ✨
Lint and Format Check	Run lint with tox	2026-09-13T06:09:44.2203968Z 355 files would be left unchanged.
```

`Run lint with tox` step, `commands[1]> ruff check .` line and verdict:
```
Lint and Format Check	Run lint with tox	2026-09-13T06:09:44.2455569Z lint: commands[1]> ruff check .
Lint and Format Check	Run lint with tox	2026-09-13T06:09:44.2893229Z All checks passed!
```

`lint: OK` line:
```
Lint and Format Check	Run lint with tox	2026-09-13T06:09:44.2910680Z   lint: OK (3.34=setup[0.18]+cmd[3.11,0.04] seconds)
```

CI is the lint authority; `release.yml` has a differently-named lint step and was neither searched nor triggered by this plan.

## Dispatch count and no release run

`gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha -q '[.[] | select(.headSha == "e70e31fba9039133a153a5bba16577d7b2f889c1")] | length'`:
```
1
```
DISPATCH_COUNT = 1

`gh run list --workflow=release.yml --limit 20 --json headSha -q '[.[] | select(.headSha == "e70e31fba9039133a153a5bba16577d7b2f889c1")] | length'`:
```
0
```
RELEASE_RUNS_AT_PUSHED = 0

## SC#5 verdict

The run is completed and success, `JOB_COUNT` (12) equals `EXPECTED_JOB_COUNT` (12), `NON_SUCCESS_JOBS = 0`, the four named lanes are all success, and `Lint and Format Check` is success.

SC5_VERDICT = MET

## Phase SC roll-up

| SC | Evidence | Verdict |
|----|----------|---------|
| SC#1 | 70-10 `SC1_VERDICT` | MET |
| SC#2 | 70-10 `SC2_VERDICT` | MET |
| SC#3 | 70-04 pilot keys, 70-10 `LEG_A_VERDICT`, `LEG_C_VERDICT`, `LEG_E_VERDICT` | MET |
| SC#4 | 70-11 `LEG_B_VERDICT`, `LEG_D_VERDICT`; 70-12 `DOC23_VERDICT` | MET |
| SC#5 | this file's `SC5_VERDICT` | MET |

PHASE_SC_ROLLUP = ALL_MET

(SC#3 note: 70-04's `70-MASK-PILOT-EVIDENCE.md` records `MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65` and "Both pilot files hash EQUAL to base — no HALT needed," the pilot that was wired into the automated leg (a) check later reported `LEG_A_VERDICT = MET` in `70-AFTER-STATIC-EVIDENCE.md`.)
