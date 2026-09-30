# Phase 61 — 3-OS CI Evidence (SC#3, dispatch half, re-anchored per D-09)

## Pre-dispatch confirmation

```
$ git rev-parse HEAD
14fcb460919455d8910fff4dece8b948de96ecc4

$ git rev-parse --abbrev-ref HEAD
worktree-agent-a8497ee77be99419f
```

Requirement-ID count inside the `## [Unreleased]` region of `CHANGELOG.md`:

```
$ awk '/^## \[Unreleased\]/,/^## \[0\.9\.0\]/' CHANGELOG.md | grep -oE '(PATH-01|IMG-0[4567]|MSG-0[2345])' | sort -u | wc -l
9
```

Nonzero — confirming the tip about to be dispatched DOES carry this phase's own CHANGELOG
bullets. This is the inverse of the Phase 57 pre-dispatch check (which confirmed a bump had
landed); here it confirms the content addition landed instead.

```
$ uv sync --extra dev --locked
Resolved 89 packages in 0.61ms
Checked 79 packages in 0.55ms
```

Succeeded with no drift. This is the sequencing constraint carried forward from 57-CONTEXT
D-13 AMENDED: every CI job begins with the same locked sync across ten steps in four workflows,
so a lock drift would fail all 12 lanes on the lock itself, before any test, lint, or type
signal exists. It is confirmed clean here, before dispatch.

**Why a fresh dispatch is required even though nothing under `typsphinx/` has changed since the
Phase 60 close:** D-09 is explicit that SC#3's green must be observed here, not inherited. CI
has never run against a tree containing this phase's CHANGELOG edit — the most recent
successful full CI run on this branch (`33252336287`, 2026-08-29T12:22Z) predates this phase
entirely. The Phase 60 close's run is **not** cited as this phase's evidence; a fresh dispatch
against the tip below is the only route to real, phase-own evidence.

## Dispatch

Push the current branch to `origin`:

```
$ git push origin worktree-agent-a8497ee77be99419f
remote:
remote: Create a pull request for 'worktree-agent-a8497ee77be99419f' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/worktree-agent-a8497ee77be99419f
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        worktree-agent-a8497ee77be99419f -> worktree-agent-a8497ee77be99419f
```

`ci.yml`'s push trigger covers only `main` and `develop` (see `.github/workflows/ci.yml` `on:`
block), so pushing this branch alone runs no CI on its own — `workflow_dispatch` is the only
route to a 3-OS run on this branch without opening a pull request, which the fence forbids. No
pull request was opened; the "Create a pull request" line above is GitHub's own informational
hint on the push response and was not acted on.

Dispatch the workflow against the same ref:

```
$ gh workflow run ci.yml --ref worktree-agent-a8497ee77be99419f
https://github.com/YuSabo90002/typsphinx/actions/runs/33260111745
```

## Run

```
$ gh run list --workflow=ci.yml --branch worktree-agent-a8497ee77be99419f --limit 1
queued		CI	CI	worktree-agent-a8497ee77be99419f	workflow_dispatch	33260111745	5s	2026-08-29T15:23:09Z
```

- **Run URL:** https://github.com/YuSabo90002/typsphinx/actions/runs/33260111745
- **Dispatched head SHA:** `14fcb460919455d8910fff4dece8b948de96ecc4`
- **Local tip SHA (recorded in `## Pre-dispatch confirmation` above):** `14fcb460919455d8910fff4dece8b948de96ecc4`

The two are equal — the run executed against exactly the commit this plan's Task 2 committed,
carrying every plan in Phase 61's work through wave 2, including 61-01's CHANGELOG edit.

```
$ gh run watch 33260111745 --exit-status
...
✓ Test Python 3.12 on ubuntu-latest in 4m0s
✓ Test Python 3.12 on macos-latest in 4m29s
✓ Test Python 3.13 on ubuntu-latest in 3m47s
✓ Test Python 3.13 on macos-latest in 4m7s
✓ (all other jobs completed successfully)
```

Overall run conclusion (`gh run view 33260111745 --json conclusion`): **`success`**.

Full per-job conclusion list, transcribed literally from
`gh run view 33260111745 --json jobs` reduced to `name` + `conclusion` (all 12 rows):

| # | Job | Conclusion |
|---|-----|------------|
| 1 | Code Coverage | success |
| 2 | Type Check | success |
| 3 | Integration Test - basic | success |
| 4 | Build Package | success |
| 5 | Lint and Format Check | success |
| 6 | Integration Test - advanced | success |
| 7 | Test Python 3.12 on windows-latest | success |
| 8 | Test Python 3.13 on windows-latest | success |
| 9 | Test Python 3.12 on ubuntu-latest | success |
| 10 | Test Python 3.12 on macos-latest | success |
| 11 | Test Python 3.13 on ubuntu-latest | success |
| 12 | Test Python 3.13 on macos-latest | success |

All 12 rows conclude `success`. This is the literal transcription — "all jobs passed" is not
accepted as a substitute for it.

### Both windows-latest lanes

| Job | Conclusion |
|-----|------------|
| Test Python 3.12 on windows-latest | success |
| Test Python 3.13 on windows-latest | success |

Both green — the milestone's own acceptance bar.

## 12-job census

Derived from `.github/workflows/ci.yml` itself, not recalled:

- **6 matrix test jobs** — the `test` job's matrix crosses 3 operating systems
  (`ubuntu-latest`, `macos-latest`, `windows-latest`) × 2 Python versions (`3.12`, `3.13`) =
  6 jobs, named `Test Python {version} on {os}`.
- **`lint`** — "Lint and Format Check" (1 job).
- **`type-check`** — "Type Check" (1 job).
- **`coverage`** — "Code Coverage" (1 job).
- **`build`** — "Build Package" (1 job).
- **`integration`** — two named variants, "Integration Test - basic" and "Integration Test -
  advanced" (2 jobs).

Total: 6 + 1 + 1 + 1 + 1 + 2 = **12**, matching the recorded run's job count (12 rows in the
table above) exactly.

## Dispatch count

Exactly **one** dispatch was made in this phase (run `33260111745`), per D-09's one-dispatch
default: this phase lands no code-affecting change under `typsphinx/`, so there is no
pre-bump/post-bump split to justify a second run.
