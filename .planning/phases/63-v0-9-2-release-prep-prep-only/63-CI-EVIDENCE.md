# Phase 63 — 3-OS CI Evidence (SC#4, dispatch half)

## Pre-dispatch confirmation

```
$ git rev-parse HEAD
225c6618ffd94ec5e1601de538438c47b4d558a9

$ git rev-parse --abbrev-ref HEAD
worktree-agent-a207bd1b50c05442b

$ uv sync --extra dev --locked
Resolved 89 packages in 0.59ms
Checked 79 packages in 0.58ms
```

Exit 0, no drift. Every one of `ci.yml`'s twelve jobs begins with the identical
`uv sync --extra dev --locked` step, so a lockfile still naming the old version would fail all
twelve lanes at the *install* step, before any test, lint or type signal exists. Plan 63-01's
`uv lock` regeneration (bumping the self-package version stanza to `0.9.2`) landed at commit
`10d9d95d` in wave 1, before this dispatch — D-17's whole sequencing requirement.

Branch census:

```
$ git branch --list 'gsd/v0.9.2*'
+ gsd/v0.9.2-inline-image-blocker-fix-and-release
```

No decoy `gsd/v0.9.2-milestone` branch exists in this worktree's view of local branches at
dispatch time — only the canonical `gsd/v0.9.2-inline-image-blocker-fix-and-release`. No pointer
advance or deletion was needed.

## Dispatch

This worktree is on its own per-agent branch, not the milestone's canonical name — confirmed by
`git rev-parse --abbrev-ref HEAD` above (`worktree-agent-a207bd1b50c05442b`), because
worktree-isolated execution puts each plan on its own branch.

```
$ git push origin worktree-agent-a207bd1b50c05442b
remote:
remote: Create a pull request for 'worktree-agent-a207bd1b50c05442b' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/worktree-agent-a207bd1b50c05442b
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        worktree-agent-a207bd1b50c05442b -> worktree-agent-a207bd1b50c05442b
```

No pull request was opened; the "Create a pull request" line is GitHub's own informational hint
on the push response and was not acted on.

```
$ gh workflow run ci.yml --ref worktree-agent-a207bd1b50c05442b
https://github.com/YuSabo90002/typsphinx/actions/runs/33309565005
```

`ci.yml` and only `ci.yml` was dispatched — the release workflow was never triggered by any route
and there was no reason to reach for it.

## Run

```
$ gh run list --workflow=ci.yml --branch worktree-agent-a207bd1b50c05442b --limit 1
queued		CI	CI	worktree-agent-a207bd1b50c05442b	workflow_dispatch	33309565005	4s	2026-08-30T11:41:37Z
```

- **Run URL:** https://github.com/YuSabo90002/typsphinx/actions/runs/33309565005
- **Run id:** `33309565005`
- **Dispatched head SHA (from the run's own JSON):** `225c6618ffd94ec5e1601de538438c47b4d558a9`
- **Local tip SHA (recorded in `## Pre-dispatch confirmation` above):** `225c6618ffd94ec5e1601de538438c47b4d558a9`

The two are equal — the run executed against exactly the commit this plan's Task 2 committed
(the format/type/docs-build gate evidence), which carries this plan's Task 1 commit and every
prior wave-1 commit in its history.

```
$ gh run watch 33309565005 --exit-status
[exited with code 0]

$ gh run view 33309565005 --json status,conclusion,workflowName,headSha,url
{"conclusion":"success","headSha":"225c6618ffd94ec5e1601de538438c47b4d558a9","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/33309565005","workflowName":"CI"}
```

Overall run: `status = completed`, `conclusion = success`, `workflowName = CI`.

## 12-job census

Transcribed literally from `gh run view 33309565005 --json jobs` reduced to `name` + `conclusion`
(all twelve rows — not "the matrix passed"):

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Code Coverage | success |
| 2 | Integration Test - basic | success |
| 3 | Lint and Format Check | success |
| 4 | Build Package | success |
| 5 | Type Check | success |
| 6 | Test Python 3.13 on windows-latest | success |
| 7 | Test Python 3.12 on ubuntu-latest | success |
| 8 | Test Python 3.12 on macos-latest | success |
| 9 | Integration Test - advanced | success |
| 10 | Test Python 3.13 on ubuntu-latest | success |
| 11 | Test Python 3.12 on windows-latest | success |
| 12 | Test Python 3.13 on macos-latest | success |

All twelve rows conclude `success`. Zero jobs have a conclusion other than `success`
(`[.jobs[] | select(.conclusion != "success")] | length` = `0`).

### Both windows-latest lanes

| Job | Conclusion |
|-----|------------|
| Test Python 3.12 on windows-latest | success |
| Test Python 3.13 on windows-latest | success |

Both green, named individually rather than summarised — 2 `windows-latest` jobs
(`[.jobs[] | select(.name | test("windows-latest"))] | length` = `2`).

### Both macos-latest lanes

| Job | Conclusion |
|-----|------------|
| Test Python 3.12 on macos-latest | success |
| Test Python 3.13 on macos-latest | success |

Both green, named individually rather than summarised — 2 `macos-latest` jobs
(`[.jobs[] | select(.name | test("macos-latest"))] | length` = `2`).

The expected twelve-job census, derived from `.github/workflows/ci.yml` itself: the `test` job's
3 OS × 2 Python-version matrix = 6 jobs, plus `lint` ("Lint and Format Check"), `type-check`
("Type Check"), `coverage` ("Code Coverage"), `build` ("Build Package"), and `integration`'s two
named variants ("Integration Test - basic", "Integration Test - advanced") = 6. Total 6 + 6 = 12,
matching the recorded run's job count exactly.

## ruff's verdict

Read as the `Lint and Format Check` job's own conclusion (`success`, job id `99252047964`) from
the same run JSON. Its one substantive step, `Run lint with tox` (`ci.yml:69`), runs
`uv run tox -e lint`, which is `tox.ini`'s `[testenv:lint]`: `black --check .` then
`ruff check .`. That job's conclusion IS the `ruff` verdict; no step-level drill-down is needed or
possible beyond quoting the step's own log.

Quoted verbatim from the step's own log (`gh run view --job 99252047964 --log`):

```
Lint and Format Check	Run lint with tox	lint: commands[0]> black --check .
Lint and Format Check	Run lint with tox	Warning: Python 3.12 cannot parse code formatted for Python 3.13. To fix this: run Black with Python 3.13, set --target-version to py312, or use --fast to skip the safety check. Black's safety check verifies equivalence by parsing the AST, which fails when the running Python is older than the target version.
Lint and Format Check	Run lint with tox	All done! ✨ 🍰 ✨
Lint and Format Check	Run lint with tox	355 files would be left unchanged.
Lint and Format Check	Run lint with tox	lint: commands[1]> ruff check .
Lint and Format Check	Run lint with tox	All checks passed!
Lint and Format Check	Run lint with tox	  lint: OK (4.00=setup[0.20]+cmd[3.74,0.06] seconds)
Lint and Format Check	Run lint with tox	  congratulations :) (4.08 seconds)
```

`ruff check .` actually executed (`commands[1]> ruff check .`) and reported `All checks passed!`
— the verdict rests on this transcribed output, not on a green tick alone.

`ci.yml` carries no step under the name `Run linters` — that name belongs to a step in
`.github/workflows/release.yml:84`, a different workflow entirely. The release workflow was not
triggered by this plan or any prior plan in this phase. This is the third recurrence of that
naming mismatch in this project (Phase 62 hit it live and handled it honestly; this phase's
`63-CONTEXT.md` § Amendments item 1 is the first correction made at the source, before any plan
went looking for the wrong name).

## No release-workflow run against this tip

```
$ gh run list --workflow=release.yml --limit 5 --json headSha,conclusion,url
[{"conclusion":"success","headSha":"68b92e24e6ca3df410ca0435d226629ef7ef1e2e", ...},
 {"conclusion":"success","headSha":"78e01e53641433a34c1bd8834b6252187fcae4ba", ...},
 {"conclusion":"success","headSha":"48bf135428bb093a77a432d93d16088ce6930342", ...},
 {"conclusion":"failure","headSha":"75fd8ed55f4fca206474f9e3aa934921588b52d5", ...},
 {"conclusion":"success","headSha":"839d77f38ffa67f18696265b361f7dcef92f679b", ...}]
```

None of the five most recent `release.yml` runs' head SHAs equal this tip
(`225c6618ffd94ec5e1601de538438c47b4d558a9`). No release-workflow run exists against this tip.

## Dispatch count

Exactly **one** dispatch was made in this phase (run `33309565005`). D-18 requires the run to sit
on the bumped tip; this wave's tip (`225c6618`) carries the bump commit (`10d9d95d`, wave 1) plus
this plan's own Tasks 1 and 2 evidence commits. Wave 3 (plan 63-04) adds only documents under
`.planning/`, which no CI job reads, so this wave's tip is the phase's final code-bearing tip and
one dispatch satisfies SC#4. A second dispatch is justified only by a second code-affecting change
mid-phase, and none is planned.
