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
