# Phase 64 — Milestone Branch Push and 3-OS CI Evidence (SC#5)

## Branch census

Re-measured per constraint 9 — never trusted from the RESOLVED note.

```
$ git branch --list 'gsd/v0.9.3*' -v
+ gsd/v0.9.3-toolchain-and-dependency-update-repair 7afbf5b2 docs(64): mark phase 64 wave 3 executing

$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5

$ git ls-remote --heads origin | grep -c '0\.9\.3'
0
```

No `gsd/v0.9.3-milestone` decoy branch exists in this worktree's local branch list — only the
canonical `gsd/v0.9.3-toolchain-and-dependency-update-repair`. No `merge-base --is-ancestor` check
or deletion was needed; nothing decoy-shaped to correct this time. The pre-push origin count for
`0.9.3` is 0, confirmed above.

## Tip identity and lock check

```
$ git rev-parse HEAD
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5

$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5
```

HEAD and the canonical branch pointer are identical before this plan's own commits — this worktree
was cut from the canonical tip after waves 1 and 2 merged, and no commit had yet been made in this
plan at the moment of measurement.

**`PUSHED_SHA = 7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`**

```
$ git log --oneline -1
7afbf5b2 docs(64): mark phase 64 wave 3 executing

$ grep -c typsphinx-fhs-run flake.nix
3
```

`flake.nix` carries 3 matches of `typsphinx-fhs-run` — the Phase 64 wave 1 deliverable is present on
this tip.

Pre-dispatch lock check (every `ci.yml` job's first substantive step):

```
$ uv sync --extra dev --locked
Resolved 89 packages in 0.69ms
Checked 79 packages in 0.60ms
$ echo "exit:$?"
exit:0
```

Exit 0, no drift — the lockfile is consistent, so none of the twelve CI lanes will fail at the
install step before any test/lint/type signal exists.

## Push

Pushed the canonical branch, and only it, with tracking, from this worktree:

```
$ git push -u origin gsd/v0.9.3-toolchain-and-dependency-update-repair
remote:
remote: Create a pull request for 'gsd/v0.9.3-toolchain-and-dependency-update-repair' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.3-toolchain-and-dependency-update-repair
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.3-toolchain-and-dependency-update-repair -> gsd/v0.9.3-toolchain-and-dependency-update-repair
branch 'gsd/v0.9.3-toolchain-and-dependency-update-repair' set up to track 'origin/gsd/v0.9.3-toolchain-and-dependency-update-repair'.
```

GitHub's "Create a pull request" hint appeared, as it does on every first push of a new branch. It
was **not** acted on — no pull request was opened, per this plan's binding prohibition. No `--force`,
no `--tags`, no other ref was pushed.

Tracking verification:

```
$ git rev-parse --abbrev-ref 'gsd/v0.9.3-toolchain-and-dependency-update-repair@{upstream}'
origin/gsd/v0.9.3-toolchain-and-dependency-update-repair

$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

The upstream branch name is exactly `origin/gsd/v0.9.3-toolchain-and-dependency-update-repair`, and
origin's head SHA for that ref equals `PUSHED_SHA`.

## Dispatch

`ci.yml`'s `push`/`pull_request` triggers are scoped to `main`/`develop`, so the push alone ran
nothing. Dispatched exactly once:

```
$ gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair
https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267
```

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 1 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-11T15:52:41Z","databaseId":34618719267,"headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267"}]
```

- **Run id:** `34618719267`
- **Run URL:** https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267
- **Dispatched head SHA (from the run's own JSON):** `7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`
- **`PUSHED_SHA`:** `7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`

The two are equal, and the run was created after the push completed (both within the same
provisioning session). No tag points at the pushed tip (`git tag --points-at
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5` returned empty), and origin carries no decoy branch
(`git ls-remote --heads origin | grep -c 'gsd/v0.9.3-milestone'` = 0). No `release.yml` route was
touched by any command in this task.

## Baseline framing

`flake.nix` is invisible to CI (ROADMAP constraint 10 — no workflow references `nix` or `flake`),
so this run's value is not proving the FHS wrapper works in CI; it is putting the milestone branch
on `origin` with a known pre-revert baseline. This plan's own evidence commit (this file) lands on
the worktree branch **after** the push recorded above — it is `.planning/`-only, which no `ci.yml`
job reads, so it does not need a second dispatch to be covered by this run's result.

The pushed tip (`7afbf5b2`) is the phase's code-bearing tip **as of this push**. A later
`flake.nix`-only gap-closure commit (addressing 64-02's recorded `libz.so.1` finding) is anticipated
by owner decision (2026-09-12, recorded in `STATE.md`) and will land after this evidence file, on
this same worktree branch, before merge. Since `flake.nix` carries zero CI coverage either way, this
dispatched run remains a valid pre-revert baseline for Phase 65's TOX-04 regardless of that later
commit — the claim made here is scoped to *this push*, not to phase finality.

## Run

The run was watched to completion in the foreground (`gh run watch 34618719267 --exit-status
--interval 30`), which exited `0`. Final status transcribed from the run's own JSON:

```
$ gh run view 34618719267 --json status,conclusion,workflowName,headSha,url
{"conclusion":"success","headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267","workflowName":"CI"}
```

`status = completed`, `conclusion = success`, `workflowName = CI`, `headSha` equal to `PUSHED_SHA`.

## Job census

Transcribed literally from `gh run view 34618719267 --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'` — all twelve rows, not "the matrix passed":

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Integration Test - advanced | success |
| 2 | Code Coverage | success |
| 3 | Test Python 3.13 on macos-latest | success |
| 4 | Type Check | success |
| 5 | Build Package | success |
| 6 | Test Python 3.13 on ubuntu-latest | success |
| 7 | Integration Test - basic | success |
| 8 | Lint and Format Check | success |
| 9 | Test Python 3.12 on windows-latest | success |
| 10 | Test Python 3.12 on ubuntu-latest | success |
| 11 | Test Python 3.12 on macos-latest | success |
| 12 | Test Python 3.13 on windows-latest | success |

All twelve rows conclude `success`. This matches the twelve-job census derived from `ci.yml`
itself: the `test` job's 3 OS × 2 Python-version matrix = 6, plus `lint` ("Lint and Format Check"),
`type-check` ("Type Check"), `coverage` ("Code Coverage"), `build` ("Build Package"), and
`integration`'s two named variants ("Integration Test - basic", "Integration Test - advanced") = 6.
Total 6 + 6 = 12, matching the run's actual job count exactly.

## windows-latest lanes

| Job | Conclusion |
|-----|------------|
| Test Python 3.12 on windows-latest | success |
| Test Python 3.13 on windows-latest | success |

Both named individually and green — 2 `windows-latest` jobs
(`[.jobs[] | select(.name | test("windows-latest"))] | length` = `2`).

## macos-latest lanes

| Job | Conclusion |
|-----|------------|
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |

Both named individually and green — 2 `macos-latest` jobs
(`[.jobs[] | select(.name | test("macos-latest"))] | length` = `2`).

## ruff's verdict

`Lint and Format Check` job id `103327017656`, conclusion `success`. Quoted verbatim from the
`Run lint with tox` step's own log (`gh run view --job 103327017656 --log`):

```
Lint and Format Check	Run lint with tox	lint: commands[0]> black --check .
Lint and Format Check	Run lint with tox	Warning: Python 3.12 cannot parse code formatted for Python 3.13. To fix this: run Black with Python 3.13, set --target-version to py312, or use --fast to skip the safety check. Black's safety check verifies equivalence by parsing the AST, which fails when the running Python is older than the target version.
Lint and Format Check	Run lint with tox	All done! ✨ 🍰 ✨
Lint and Format Check	Run lint with tox	355 files would be left unchanged.
Lint and Format Check	Run lint with tox	lint: commands[1]> ruff check .
Lint and Format Check	Run lint with tox	All checks passed!
Lint and Format Check	Run lint with tox	  lint: OK (4.30=setup[0.19]+cmd[4.04,0.06] seconds)
Lint and Format Check	Run lint with tox	  congratulations :) (4.37 seconds)
```

The job's own `pip freeze` line in the same log (`lint: freeze>`) records `ruff==0.15.20` — the
exact `uv.lock:1209-1210` pin.

**Set beside 64-02's local shim verdict** (`64-NIX05-WORKTREE-EVIDENCE.md`, § NIX-01 — ruff, run
inside `typsphinx-fhs-run` in a nested worktree):

```
$ ruff --version
ruff 0.15.20

$ ruff check .
All checks passed!
$ echo "exit:$?"
exit:0
```

Both invocations report `ruff 0.15.20` and both conclude `All checks passed!` — local (via the
`flake.nix` shim, resolving `.venv/bin/ruff`) and CI (via `uv sync --extra dev --locked`,
resolving `uv.lock`) now run the identical pinned `ruff` version and agree on the verdict. This is
NIX-01's CI-side rationale: local and CI lint no longer diverge.

The step in `ci.yml` that runs this is named `Run lint with tox` (`ci.yml:69`). The differently
named lint step lives in `release.yml:84`, a separate workflow this plan never searched for and
never triggered.

## No release-workflow run against this tip

```
$ gh run list --workflow=release.yml --limit 5 --json headSha,conclusion,url
[{"conclusion":"success","headSha":"45962faad21520c72ac9f1e14c7f684050826bb6", ...},
 {"conclusion":"success","headSha":"68b92e24e6ca3df410ca0435d226629ef7ef1e2e", ...},
 {"conclusion":"success","headSha":"78e01e53641433a34c1bd8834b6252187fcae4ba", ...},
 {"conclusion":"success","headSha":"48bf135428bb093a77a432d93d16088ce6930342", ...},
 {"conclusion":"failure","headSha":"75fd8ed55f4fca206474f9e3aa934921588b52d5", ...}]
```

None of the five most recent `release.yml` runs' head SHAs equal `PUSHED_SHA`
(`7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`). No release-workflow run exists against this tip; no
route to `release.yml` was ever taken by this plan.

## Baseline label

This run (`34618719267`, `conclusion: success`, all twelve jobs green including both
`windows-latest` and both `macos-latest` lanes) is the **pre-revert baseline** Phase 65's TOX-04
compares against. `tox-uv-bare` is still pinned at this tip (`tox.ini:4-11`, `pyproject.toml:38`
unchanged by this plan) — Phase 65 has not yet run its revert to `tox-uv`.

## Dispatch count

Exactly **one** `workflow_dispatch` CI run exists on
`gsd/v0.9.3-toolchain-and-dependency-update-repair`:

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --json databaseId
[{"databaseId":34618719267}]
```

This wave's tip (`7afbf5b2`) carries the phase's flake.nix deliverable and every prior wave's
commits; this plan's own evidence commits (Task 1 and this Task 2 commit) add only
`.planning/`-only content, which no `ci.yml` job reads, so this tip is the phase's final
code-bearing tip as of this push and one dispatch satisfies SC#5. A second dispatch is justified
only by a second code-affecting change mid-phase, and none occurred.
