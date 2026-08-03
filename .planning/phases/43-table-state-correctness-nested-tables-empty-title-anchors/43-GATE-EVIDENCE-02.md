# 43-GATE-EVIDENCE-02.md — SC#5 Push Evidence

**Phase:** 43 (Table State Correctness — Nested Tables + Empty-Title Anchors)
**Wave:** 1
**Plan:** 43-02
**Executed:** 2026-08-03T23:5x UTC (worktree agent, isolated worktree
`worktree-agent-a36d0ccd040edd99c`)

This file records every command and its verbatim output for the outward-facing push of the
milestone branch `gsd/v0.7.1-bug-fix-round`, per roadmap SC#5 and milestone invariant #5. The
Task 1 checkpoint (`push-now` vs `push-at-end`) was already resolved by the developer, via the
orchestrator, as **`push-now`** before this plan was dispatched — no re-ask occurred in this
session.

## 1. Pre-push baseline

```
$ git rev-parse --abbrev-ref HEAD
worktree-agent-a36d0ccd040edd99c

$ git rev-parse HEAD
7bdaf40ee131a63dc5cf9789d90668c54948a117

$ git rev-parse gsd/v0.7.1-bug-fix-round
7bdaf40ee131a63dc5cf9789d90668c54948a117
```

This executor runs inside an isolated worktree, so `HEAD` reports the `worktree-agent-*` branch
rather than `gsd/v0.7.1-bug-fix-round` directly. The tip actually being published is
`7bdaf40ee131a63dc5cf9789d90668c54948a117` (identical to this worktree's own HEAD, confirming the
worktree was forked directly from the milestone branch's tip with no additional commits).

```
$ git ls-remote --heads origin
1c905bb80d388465e57280dc104cbd117442e28a	refs/heads/dependabot/pip/ruff-gte-0.15-and-lt-0.17
67ed836e827cd31f5d679277252f6f381e5ee60d	refs/heads/dependabot/pip/sphinx-typst-stack-12b5b89b5a
9a544db57f77df463ec5090d06a96f9febf2d8eb	refs/heads/gsd/v0.7.0-api-rendering-design-overhaul
1a614a9368c71955cc846f5f085ff79a028ec505	refs/heads/main
c8e60dd07fd0b4b803a2ee629e88b01ca81c6276	refs/heads/worktree-agent-ad728f7d42898a802
e5edc376a69411ab72cc9c535bc65dba2f3daa58	refs/heads/worktree-agent-ad9fb4bbe59c49b28
```

Baseline confirmed: `gsd/v0.7.1-bug-fix-round` is **NOT** present on `origin` before the push.

## 2. Push

```
$ git push -u origin gsd/v0.7.1-bug-fix-round
remote:
remote: Create a pull request for 'gsd/v0.7.1-bug-fix-round' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.7.1-bug-fix-round
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]      gsd/v0.7.1-bug-fix-round -> gsd/v0.7.1-bug-fix-round
branch 'gsd/v0.7.1-bug-fix-round' set up to track 'origin/gsd/v0.7.1-bug-fix-round'.
```

## 3. Post-push effect (not just the action)

```
$ git ls-remote --heads origin
1c905bb80d388465e57280dc104cbd117442e28a	refs/heads/dependabot/pip/ruff-gte-0.15-and-lt-0.17
67ed836e827cd31f5d679277252f6f381e5ee60d	refs/heads/dependabot/pip/sphinx-typst-stack-12b5b89b5a
9a544db57f77df463ec5090d06a96f9febf2d8eb	refs/heads/gsd/v0.7.0-api-rendering-design-overhaul
7bdaf40ee131a63dc5cf9789d90668c54948a117	refs/heads/gsd/v0.7.1-bug-fix-round
1a614a9368c71955cc846f5f085ff79a028ec505	refs/heads/main
c8e60dd07fd0b4b803a2ee629e88b01ca81c6276	refs/heads/worktree-agent-ad728f7d42898a802
e5edc376a69411ab72cc9c535bc65dba2f3daa58	refs/heads/worktree-agent-ad9fb4bbe59c49b28
```

`refs/heads/gsd/v0.7.1-bug-fix-round` is now present at SHA
`7bdaf40ee131a63dc5cf9789d90668c54948a117` — **identical** to the tip recorded in step 1. The
push published exactly the intended commit, nothing more.

## 4. Triggered CI — polling record (including empty attempts)

**Deviation found and auto-fixed (Rule 3 — blocking issue, no file modified):** `.github/workflows/ci.yml`'s
`push` trigger is scoped to `branches: [ main, develop ]` only (verified by reading the file,
`<read_first>` requirement):

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
```

A plain `git push` to `gsd/v0.7.1-bug-fix-round` therefore does **not** trigger `ci.yml` (the
workflow carrying the OS/Python matrix and the Windows lanes) — it only satisfies `links.yml`,
whose `on: push:` has no branch filter. This is a real blocker against the plan's acceptance
criterion ("names at least one Windows lane"), which no amount of additional polling would have
resolved, since `ci.yml` structurally cannot fire from this push event. `ci.yml` already declares
`workflow_dispatch:` as a trigger, so the fix used that existing, unmodified trigger mechanism —
`gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round` — to get a real matrix run registered
against the branch. **No file was modified**; this is the same effect the plan's push-and-wait
step intended, reached through the workflow's own already-declared dispatch trigger instead of an
event that does not exist for this branch name.

Poll attempts, in order, exactly as executed:

```
$ gh run list --branch gsd/v0.7.1-bug-fix-round --limit 10
(no output — 0 runs registered yet, immediately after the push)

$ sleep 15 && gh run list --branch gsd/v0.7.1-bug-fix-round --limit 10
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z

$ sleep 10 && gh run list --branch gsd/v0.7.1-bug-fix-round --limit 10
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```

Only `links.yml` ("Link Check") had registered from the push event itself — confirming the
diagnosis above. Manual dispatch of `ci.yml`:

```
$ gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round
https://github.com/YuSabo90002/typsphinx/actions/runs/30863882894

$ sleep 12 && gh run list --branch gsd/v0.7.1-bug-fix-round --limit 10
in_progress		CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	16s	2026-08-03T23:55:14Z
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```

**Triggered CI run: `30863882894`** (`CI` workflow, trigger `workflow_dispatch`), status
`in_progress` at the time of this recording.

## 5. Complete lane list

```
$ gh run view 30863882894
* gsd/v0.7.1-bug-fix-round CI · 30863882894
Triggered via workflow_dispatch less than a minute ago

JOBS
* Integration Test - advanced (ID 91851432296)
* Build Package (ID 91851432298)
* Lint and Format Check (ID 91851432306)
* Type Check (ID 91851432318)
* Code Coverage (ID 91851432327)
* Integration Test - basic (ID 91851432346)
* Test Python 3.13 on ubuntu-latest (ID 91851432353)
* Test Python 3.12 on ubuntu-latest (ID 91851432354)
* Test Python 3.13 on windows-latest (ID 91851432358)
* Test Python 3.12 on macos-latest (ID 91851432374)
* Test Python 3.13 on macos-latest (ID 91851432381)
* Test Python 3.12 on windows-latest (ID 91851432384)
```

Cross-checked against `.github/workflows/ci.yml`'s `strategy.matrix` block (`test` job):

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.12', '3.13']
```

**Both Windows lanes are present and explicitly named:**
- `Test Python 3.12 on windows-latest` (job ID 91851432384)
- `Test Python 3.13 on windows-latest` (job ID 91851432358)

Full 12-job lane set for run `30863882894`: 6 `os × python-version` test lanes (3 OS × 2 Python,
including both Windows lanes above), `Lint and Format Check`, `Type Check`, `Code Coverage`,
`Build Package`, and 2 `Integration Test` lanes (`basic`, `advanced`). This is the complete,
verbatim job list plan 43-05 must confirm as **completed** (not merely registered) against the
finished-phase tip.

## 6. Scope statement

- **This plan's phase/wave:** Phase 43, wave 1 (plan 43-02), pushed 2026-08-03/2026-08-04
  (session timestamp above) — during the first phase of the milestone, not deferred to the
  release PR. This discharges the "pushed during Phase 43" half of roadmap SC#5 and milestone
  invariant #5.
- **NOT claimed here:** the *completed* half of SC#5 (a finished run, including both Windows
  lanes, GREEN) is explicitly **owned by plan 43-05**, which re-pushes the finished phase tip and
  confirms a COMPLETED run against it. Run `30863882894` above was `in_progress` at the time of
  this recording and proves only that a run was *triggered and registered* against the branch —
  not that it finished, and not that it is green. Per planner decision D-P2 (recorded in
  `43-02-PLAN.md`), a RED Windows lane on the completed run blocks handoff to Phase 44;
  enforcement of that gate lives entirely in plan 43-05, not here.

## 7. Working-tree state

```
$ git status --porcelain typsphinx/ tests/
(empty)
```

No file outside `.planning/` was modified by this plan.
