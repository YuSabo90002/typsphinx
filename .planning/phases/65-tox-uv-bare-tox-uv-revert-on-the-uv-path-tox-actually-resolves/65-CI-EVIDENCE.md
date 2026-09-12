Measured shape: executor worktree, Phase 64 shims inherited from the session PATH; no nix develop,
no direnv exec, never the main checkout. This is TOX-04's run on the post-revert tip. Phase 64 run
`34618719267` is the pre-revert baseline, cited only for comparison — never as this green. This
plan's evidence commits land after the push and touch only `.planning/`, which no CI job reads.

REVERT_SHA = d32eb5db6219bf4917ab820a44562ba479e5fe71
PUSHED_SHA = d9c7555323e843b5a389ed4354ce656d2fd05ca2
RUN_ID = 34681968010

## Wave-1 gate

```
$ sed -n 's/^REVERT_SHA = //p' 65-REVERT-EVIDENCE.md | head -n 1
d32eb5db6219bf4917ab820a44562ba479e5fe71

$ git merge-base --is-ancestor d32eb5db6219bf4917ab820a44562ba479e5fe71 HEAD; echo "exit:$?"
exit:0

$ grep -c '^## DIVERGENT' 65-REVERT-EVIDENCE.md
0
```

TOX-01..TOX-03 closure rows, quoted verbatim from `65-REVERT-EVIDENCE.md` § Requirement closure:

| Requirement | Status | Deciding section |
|---|---|---|
| TOX-01 | MET | `## TOX-01 lock regeneration`, `## D-05 uv before and after`, `## Revert commit` |
| TOX-02 | MET | `## TOX-02 tox starts` |
| TOX-03 | MET | `## TOX-03 D-02 observation inside FHS`, `## TOX-03 D-03 isolated control outside FHS`, `## SC#3 literal and amended readings` |

`REVERT_SHA` is an ancestor of HEAD (`exit:0`), all three rows read MET, and the DIVERGENT count is
`0`. There is a proven revert to push.

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab0f5b93080e84ee7

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv
$ grep -c typsphinx-fhs-run /nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv
2

$ command -v tox
/nix/store/r70g13f57bbrw66k56dlqk9bbbcpch33-tox/bin/tox
$ grep -c typsphinx-fhs-run /nix/store/r70g13f57bbrw66k56dlqk9bbbcpch33-tox/bin/tox
1

$ printenv TOX_UV_PATH; echo "exit:$?"
exit:1
```

The worktree path lies under `/home/yuta/Documents/typsphinx/.claude/worktrees/`. Both shim bodies
name `typsphinx-fhs-run`. `TOX_UV_PATH` is unset (`exit:1`).

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.60ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab0f5b93080e84ee7
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab0f5b93080e84ee7
Prepared 1 package in 376ms
Installed 81 packages in 52ms
 ... (81 packages, including tox-uv==1.36.0, tox-uv-bare==1.36.0, uv==0.12.13, tox==4.56.1, pytest==9.1.1)

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --locked
Resolved 91 packages in 2ms
Checked 81 packages in 0.63ms
$ echo "exit:$?"
exit:0
```

The provisioning line ran verbatim, and the pre-dispatch locked sync exits `0` — the same step every
`ci.yml` job runs first.

## Branch census

```
$ git branch --list 'gsd/v0.9.3*' -v
+ gsd/v0.9.3-toolchain-and-dependency-update-repair d9c75553 [ahead 42] docs(phase-65): update tracking after wave 1, mark wave 2 executing

$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
d9c7555323e843b5a389ed4354ce656d2fd05ca2

$ git ls-remote --heads origin | grep '0\.9\.3'
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

Only `gsd/v0.9.3-toolchain-and-dependency-update-repair` exists locally (no `gsd/v0.9.3-milestone`
decoy). Origin carried only the canonical branch at `7afbf5b2…` before the push (this plan's
`ORIGIN_BEFORE`). No decoy handling was required — there is nothing to delete and nothing to halt on.

## Tip identity and constraint-13 fence

```
$ git rev-parse HEAD
d9c7555323e843b5a389ed4354ce656d2fd05ca2

$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
d9c7555323e843b5a389ed4354ce656d2fd05ca2

$ git log --oneline -1
d9c75553 docs(phase-65): update tracking after wave 1, mark wave 2 executing
```

PUSHED_SHA = d9c7555323e843b5a389ed4354ce656d2fd05ca2

HEAD equals the canonical branch's own tip; this worktree was cut from the canonical tip after wave
1 merged, and this plan had not committed at the time this was measured.

Fence (a)-(e), all held:

```
(a) $ git show --name-only --format= d32eb5db6219bf4917ab820a44562ba479e5fe71 | sort
pyproject.toml
tests/test_toolchain_config_gate.py
tox.ini
uv.lock

(b) $ git diff --name-only d32eb5db6219bf4917ab820a44562ba479e5fe71 HEAD -- pyproject.toml tox.ini uv.lock tests/test_toolchain_config_gate.py typsphinx .github/workflows flake.nix flake.lock CLAUDE.md
(empty)

(c) $ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD
$ git rev-parse origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e
$ git merge-base HEAD origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e
$ git diff --name-only 6181768f64b4cee62a77ac4e26c60c3c976cbb6e HEAD -- typsphinx .github/workflows
(empty)

(d) $ git grep -n TOX_UV_PATH HEAD -- . ':(exclude).planning'
(empty, no match)

(e) $ sed -n 38p pyproject.toml
    "tox-uv>=1.35,<2",
$ sed -n 11p tox.ini
requires = tox-uv~=1.35
```

(a): the revert commit lists exactly the four files. (b): no later commit on the tip touches any
fenced path. (c): nothing under `typsphinx/` or `.github/workflows/` differs from the merge-base
with `origin/main` (which happens to equal `origin/main` itself here, since HEAD has not diverged
from `main` under those paths) — the four `@preview` declarations are unchanged. (d): no tracked
file outside `.planning/` names `TOX_UV_PATH`. (e): both pin lines show the tox-uv forms.

## Push

```
$ git fetch origin gsd/v0.9.3-toolchain-and-dependency-update-repair
From https://github.com/YuSabo90002/typsphinx
 * branch              gsd/v0.9.3-toolchain-and-dependency-update-repair -> FETCH_HEAD

$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

ORIGIN_BEFORE = 7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5

```
$ git merge-base --is-ancestor 7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5 HEAD; echo "exit:$?"
exit:0

$ date -u +%FT%TZ
2026-09-12T07:55:25Z
```

PUSH_AT = 2026-09-12T07:55:25Z

```
$ git push -u origin gsd/v0.9.3-toolchain-and-dependency-update-repair
To https://github.com/YuSabo90002/typsphinx.git
   7afbf5b2..d9c75553  gsd/v0.9.3-toolchain-and-dependency-update-repair -> gsd/v0.9.3-toolchain-and-dependency-update-repair
branch 'gsd/v0.9.3-toolchain-and-dependency-update-repair' set up to track 'origin/gsd/v0.9.3-toolchain-and-dependency-update-repair'.
```

No force, no tags, no other ref. GitHub printed no pull-request hint on this push, and none was
acted on regardless.

```
$ git rev-parse --abbrev-ref gsd/v0.9.3-toolchain-and-dependency-update-repair@{upstream}
origin/gsd/v0.9.3-toolchain-and-dependency-update-repair

$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
d9c7555323e843b5a389ed4354ce656d2fd05ca2	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

The upstream is the canonical remote branch, and the remote head now equals `PUSHED_SHA`
(`d9c75553…`), advanced from `ORIGIN_BEFORE` (`7afbf5b2…`) as a fast-forward.

## Dispatch

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)

$ gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair
https://github.com/YuSabo90002/typsphinx/actions/runs/34681968010

$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-12T07:55:42Z","databaseId":34681968010,"headSha":"d9c7555323e843b5a389ed4354ce656d2fd05ca2","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34681968010"},{"createdAt":"2026-09-11T15:52:41Z","databaseId":34618719267,"headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267"}]
```

RUN_ID = 34681968010, URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34681968010

The listed row's `headSha` (`d9c7555323e843b5a389ed4354ce656d2fd05ca2`) equals `PUSHED_SHA`, and its
`createdAt` (`2026-09-12T07:55:42Z`) is later than `PUSH_AT` (`2026-09-12T07:55:25Z`). No
registration lag was encountered — the run was listed on the first query. Exactly one
`gh workflow run CI` was issued.

## Run

Waited in the foreground with `gh run watch 34681968010 --interval 30` (Bash timeout 600000ms, no
`run_in_background`). The single foreground call returned after the run reached a terminal state.

```
$ gh run view 34681968010 --json status,conclusion,workflowName,headSha,url
{"conclusion":"success","headSha":"d9c7555323e843b5a389ed4354ce656d2fd05ca2","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34681968010","workflowName":"CI"}
```

`status: completed`, `conclusion: success`, `workflowName: CI`, `headSha` equal to `PUSHED_SHA`.

## Job census

```
$ gh run view 34681968010 --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
Type Check	success
Integration Test - basic	success
Lint and Format Check	success
Test Python 3.12 on windows-latest	success
Test Python 3.13 on ubuntu-latest	success
Build Package	success
Integration Test - advanced	success
Test Python 3.12 on macos-latest	success
Test Python 3.13 on macos-latest	success
Code Coverage	success
Test Python 3.12 on ubuntu-latest	success
Test Python 3.13 on windows-latest	success
```

Twelve jobs, numbered as reported by the API (transcription order only; no assertion depends on
this order):

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Type Check | success |
| 2 | Integration Test - basic | success |
| 3 | Lint and Format Check | success |
| 4 | Test Python 3.12 on windows-latest | success |
| 5 | Test Python 3.13 on ubuntu-latest | success |
| 6 | Build Package | success |
| 7 | Integration Test - advanced | success |
| 8 | Test Python 3.12 on macos-latest | success |
| 9 | Test Python 3.13 on macos-latest | success |
| 10 | Code Coverage | success |
| 11 | Test Python 3.12 on ubuntu-latest | success |
| 12 | Test Python 3.13 on windows-latest | success |

All twelve jobs are `success`; zero non-success conclusions. This is exactly the twelve jobs
`ci.yml` defines: 6 `test` matrix cells (3 OS × 2 Python) + `Lint and Format Check` + `Type Check` +
`Code Coverage` + `Build Package` + `Integration Test - basic` + `Integration Test - advanced`.

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

Quoted verbatim from the `Lint and Format Check` job's `Run lint with tox` step
(job id `103522124003`):

```
lint: venv> .venv/bin/uv venv -p /home/runner/work/typsphinx/typsphinx/.venv/bin/python --allow-existing '--prompt=typsphinx[lint]' --python-preference system /home/runner/work/typsphinx/typsphinx/.tox/lint
lint: uv-sync> .venv/bin/uv sync --locked --python-preference system --extra dev -p /home/runner/work/typsphinx/typsphinx/.venv/bin/python
lint: commands[0]> black --check .
Warning: Python 3.12 cannot parse code formatted for Python 3.13. To fix this: run Black with Python 3.13, set --target-version to py312, or use --fast to skip the safety check. Black's safety check verifies equivalence by parsing the AST, which fails when the running Python is older than the target version.
All done! ✨ 🍰 ✨
355 files would be left unchanged.
lint: commands[1]> ruff check .
All checks passed!
  lint: OK (4.55=setup[0.22]+cmd[4.27,0.07] seconds)
  congratulations :) (4.59 seconds)
```

Set beside `65-REVERT-EVIDENCE.md` § "Gate GREEN and lint" (this worktree's local run, same tip):

| Command | Local (`65-REVERT-EVIDENCE.md`) | CI (`Lint and Format Check` / `Run lint with tox`) |
|---|---|---|
| `black --check .` | `All done! ✨ 🍰 ✨` / `355 files would be left unchanged.` | `All done! ✨ 🍰 ✨` / `355 files would be left unchanged.` (with a benign cross-version parse-safety warning, no failure) |
| `ruff check .` | `All checks passed!` | `All checks passed!` |
| verdict | (n/a — local run has no tox verdict line) | `lint: OK` |

CI is the authority. The local run's `ruff check .` and `black --check .` verdicts agree with CI's.
This is `ci.yml`'s `Run lint with tox` step; the differently-named lint step belongs to
`release.yml`, which this plan never searches for and never triggers, and whose step name is
absent from this evidence.

## uv resolved on CI

For each of the six `Test Python …` lanes and `Lint and Format Check`, the first `venv> ` line from
the new run's job log, set beside the same lane's first `venv> ` line from the pre-revert baseline
run `34618719267`:

| Lane | Baseline (`34618719267`) `venv>` uv path | New (`34681968010`) `venv>` uv path |
|---|---|---|
| Test Python 3.12 on windows-latest | `C:\hostedtoolcache\windows\uv\0.12.13\x86_64\uv.EXE` | `.venv\Scripts\uv.exe` |
| Test Python 3.13 on windows-latest | `C:\hostedtoolcache\windows\uv\0.12.13\x86_64\uv.EXE` | `.venv\Scripts\uv.exe` |
| Test Python 3.12 on macos-latest | `/Users/runner/hostedtoolcache/uv/0.12.13/aarch64/uv` | `.venv/bin/uv` |
| Test Python 3.13 on macos-latest | `/Users/runner/hostedtoolcache/uv/0.12.13/aarch64/uv` | `.venv/bin/uv` |
| Test Python 3.12 on ubuntu-latest | `/opt/hostedtoolcache/uv/0.12.13/x86_64/uv` | `.venv/bin/uv` |
| Test Python 3.13 on ubuntu-latest | `/opt/hostedtoolcache/uv/0.12.13/x86_64/uv` | `.venv/bin/uv` |
| Lint and Format Check | `/opt/hostedtoolcache/uv/0.12.13/x86_64/uv` | `.venv/bin/uv` |

Full lines, quoted verbatim:

```
[baseline] Test Python 3.12 on windows-latest: py312: venv> C:\hostedtoolcache\windows\uv\0.12.13\x86_64\uv.EXE venv -p cpython3.12 --allow-existing --prompt=typsphinx[py312] --python-preference system D:\a\typsphinx\typsphinx\.tox\py312
[new]      Test Python 3.12 on windows-latest: py312: venv> .venv\Scripts\uv.exe venv -p cpython3.12 --allow-existing --prompt=typsphinx[py312] --python-preference system D:\a\typsphinx\typsphinx\.tox\py312

[baseline] Test Python 3.13 on windows-latest: py313: venv> C:\hostedtoolcache\windows\uv\0.12.13\x86_64\uv.EXE venv -p cpython3.13 --allow-existing --prompt=typsphinx[py313] --python-preference system D:\a\typsphinx\typsphinx\.tox\py313
[new]      Test Python 3.13 on windows-latest: py313: venv> .venv\Scripts\uv.exe venv -p cpython3.13 --allow-existing --prompt=typsphinx[py313] --python-preference system D:\a\typsphinx\typsphinx\.tox\py313

[baseline] Test Python 3.12 on macos-latest: py312: venv> /Users/runner/hostedtoolcache/uv/0.12.13/aarch64/uv venv -p cpython3.12 --allow-existing '--prompt=typsphinx[py312]' --python-preference system /Users/runner/work/typsphinx/typsphinx/.tox/py312
[new]      Test Python 3.12 on macos-latest: py312: venv> .venv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=typsphinx[py312]' --python-preference system /Users/runner/work/typsphinx/typsphinx/.tox/py312

[baseline] Test Python 3.13 on macos-latest: py313: venv> /Users/runner/hostedtoolcache/uv/0.12.13/aarch64/uv venv -p cpython3.13 --allow-existing '--prompt=typsphinx[py313]' --python-preference system /Users/runner/work/typsphinx/typsphinx/.tox/py313
[new]      Test Python 3.13 on macos-latest: py313: venv> .venv/bin/uv venv -p cpython3.13 --allow-existing '--prompt=typsphinx[py313]' --python-preference system /Users/runner/work/typsphinx/typsphinx/.tox/py313

[baseline] Test Python 3.12 on ubuntu-latest: py312: venv> /opt/hostedtoolcache/uv/0.12.13/x86_64/uv venv -p cpython3.12 --allow-existing '--prompt=typsphinx[py312]' --python-preference system /home/runner/work/typsphinx/typsphinx/.tox/py312
[new]      Test Python 3.12 on ubuntu-latest: py312: venv> .venv/bin/uv venv -p cpython3.12 --allow-existing '--prompt=typsphinx[py312]' --python-preference system /home/runner/work/typsphinx/typsphinx/.tox/py312

[baseline] Test Python 3.13 on ubuntu-latest: py313: venv> /opt/hostedtoolcache/uv/0.12.13/x86_64/uv venv -p cpython3.13 --allow-existing '--prompt=typsphinx[py313]' --python-preference system /home/runner/work/typsphinx/typsphinx/.tox/py313
[new]      Test Python 3.13 on ubuntu-latest: py313: venv> .venv/bin/uv venv -p cpython3.13 --allow-existing '--prompt=typsphinx[py313]' --python-preference system /home/runner/work/typsphinx/typsphinx/.tox/py313

[baseline] Lint and Format Check: lint: venv> /opt/hostedtoolcache/uv/0.12.13/x86_64/uv venv -p /home/runner/work/typsphinx/typsphinx/.venv/bin/python --allow-existing '--prompt=typsphinx[lint]' --python-preference system /home/runner/work/typsphinx/typsphinx/.tox/lint
[new]      Lint and Format Check: lint: venv> .venv/bin/uv venv -p /home/runner/work/typsphinx/typsphinx/.venv/bin/python --allow-existing '--prompt=typsphinx[lint]' --python-preference system /home/runner/work/typsphinx/typsphinx/.tox/lint
```

Every one of the seven lanes named `hostedtoolcache` (setup-uv's PATH branch) at the pre-revert
baseline and now names the runner checkout's own `.venv` uv (`.venv\Scripts\uv.exe` on Windows,
`.venv/bin/uv` on macOS/Linux) — tox-uv's bundled branch, exactly as this revert restores. No lane
still names `hostedtoolcache`; there is no finding to record for the owner on this axis.

## Comparison with the pre-revert baseline

Twelve rows, baseline conclusion beside the new one:

| Job | Baseline (`34618719267`) | New (`34681968010`) |
|---|---|---|
| Type Check | success | success |
| Integration Test - basic | success | success |
| Lint and Format Check | success | success |
| Test Python 3.12 on windows-latest | success | success |
| Test Python 3.13 on ubuntu-latest | success | success |
| Build Package | success | success |
| Integration Test - advanced | success | success |
| Test Python 3.12 on macos-latest | success | success |
| Test Python 3.13 on macos-latest | success | success |
| Code Coverage | success | success |
| Test Python 3.12 on ubuntu-latest | success | success |
| Test Python 3.13 on windows-latest | success | success |

Both runs are all-green across the same twelve jobs. Run `34618719267`'s `headSha`
(`7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`) predates `REVERT_SHA`
(`d32eb5db6219bf4917ab820a44562ba479e5fe71`), which is itself an ancestor of `PUSHED_SHA`
(`d9c7555323e843b5a389ed4354ce656d2fd05ca2`, this run's `headSha`) — the baseline is the pre-revert
tree, and this run is the post-revert tree. It is cited only for comparison, never as this green.

## No release-workflow run against this tip

```
$ gh run list --workflow=release.yml --limit 5 --json headSha
[{"headSha":"45962faad21520c72ac9f1e14c7f684050826bb6"},{"headSha":"68b92e24e6ca3df410ca0435d226629ef7ef1e2e"},{"headSha":"78e01e53641433a34c1bd8834b6252187fcae4ba"},{"headSha":"48bf135428bb093a77a432d93d16088ce6930342"},{"headSha":"75fd8ed55f4fca206474f9e3aa934921588b52d5"}]
```

None of the five most recent `release.yml` runs carry `headSha` equal to `PUSHED_SHA`
(`d9c7555323e843b5a389ed4354ce656d2fd05ca2`). No release workflow ever ran against this tip.

## Dispatch count

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 50 --json headSha
[{"headSha":"d9c7555323e843b5a389ed4354ce656d2fd05ca2"},{"headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5"}]
```

Exactly one `workflow_dispatch` CI run on this branch carries `headSha` equal to `PUSHED_SHA`
(the second entry, `7afbf5b2…`, is Phase 64's own dispatch at the pre-revert tip, not this plan's).

## Requirement closure

| Requirement | Status | Deciding section |
|---|---|---|
| TOX-04 | MET | `## Run`, `## Job census`, `## windows-latest lanes`, `## macos-latest lanes`, `## ruff's verdict`, `## uv resolved on CI`, `## Dispatch count` |

TOX-01, TOX-02 and TOX-03 are restated from `65-REVERT-EVIDENCE.md` § Requirement closure (not
re-decided here): all three read MET, deciding sections `## TOX-01 lock regeneration` / `## D-05 uv
before and after` / `## Revert commit` (TOX-01), `## TOX-02 tox starts` (TOX-02), and
`## TOX-03 D-02 observation inside FHS` / `## TOX-03 D-03 isolated control outside FHS` /
`## SC#3 literal and amended readings` (TOX-03).
