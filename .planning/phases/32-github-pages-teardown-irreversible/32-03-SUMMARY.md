---
phase: 32-github-pages-teardown-irreversible
plan: 03
subsystem: infra
tags: [github-actions, ci, remote-git-state, github-pages, irreversible, teardown]

# Dependency graph
requires:
  - phase: 32-github-pages-teardown-irreversible (Plan 01)
    provides: "GATE VERDICT: GREEN — fresh in-phase proof RTD serves en/ja HTML+PDF, and the pre-teardown baseline (gh-pages SHA, github.io 200, PR #124 pre-teardown headRefOid)"
  - phase: 32-github-pages-teardown-irreversible (Plan 02)
    provides: "docs.yml with the GitHub Pages deploy step and unused permissions removed, D-06 guard tests, INTEGRATIONS.md updated"
provides:
  - "Post-teardown tree pushed to milestone draft PR #124; a fresh green build-docs run (30275369792) observed against the teardown head, with the docs-pdf regression gate recorded successful at step level"
  - "origin/gh-pages permanently deleted, proven absent by a live git ls-remote query"
  - "github.io 404 directly observed and honestly recorded (CONFIRMED, not assumed)"
  - "Revival-hazard and resolved-todo handoffs recorded for /gsd-complete-milestone"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Push-then-poll CI observation via gh run list/watch/view, pinning the cited run by headSha equality with the pushed SHA (guards against citing a pre-existing/stale green run)"
    - "Remote ref deletion proven only by live git ls-remote, never by local git branch -a/-r (SC#2's explicit requirement)"
    - "Bounded-retry, honest-verifier 404 observation: multiple independent curl attempts (with/without -L, full headers) rather than a single check, but concluding CONFIRMED only on directly observed evidence"

key-files:
  created: []
  modified:
    - .planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md

key-decisions:
  - "D-04 same-day re-confirmation: today (2026-07-27) matched Plan 01's gate-gathered date, so only the four URL statuses were re-checked (all 200) before the irreversible step, not the full five-check gate"
  - "A-02 resolved empirically: branch deletion alone already 404s the site (no owner Settings action was performed this session — none was present); the owner-manual Settings -> Pages disable remains on REQUIREMENTS.md's checklist as defense-in-depth, not skipped as redundant"

patterns-established: []

requirements-completed: [CI-04]

coverage:
  - id: D1
    description: "The post-teardown tree is pushed to draft PR #124 and a green build-docs run is observed whose headSha is provably the teardown commit, not the pre-teardown baseline"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "gh run view 30275369792 --json conclusion,event,headSha -- conclusion=success, event=pull_request, headSha=d53edecfd064a93d7a43455d505f7848a1c43320 (differs from Plan 01 baseline 980f6ca909b8b07045d664548094b98f31bd8551)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The Build PDF documentation (English only) step (the docs-pdf typstpdf regression gate) is recorded successful at step level, not merely inferred from job conclusion"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "gh run view 30275369792 --json jobs -- step 'Build PDF documentation (English only)' conclusion=success"
        status: pass
    human_judgment: false
  - id: D3
    description: "origin/gh-pages no longer exists, proven by a live git ls-remote query (not a local branch listing), with the deleted SHA reconciled against Plan 01's baseline"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "git ls-remote origin refs/heads/gh-pages -- no output; deleted SHA f97862dfea151dd904591a18d2ddbd0bf72fd851 matched Plan 01's recorded baseline exactly; refs/heads/main confirmed still resolving"
        status: pass
    human_judgment: false
  - id: D4
    description: "github.io returns 404 with no redirect, honestly recorded (CONFIRMED only on direct observation, never asserted)"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "4 independent curl attempts (with/without -L, full headers) all returned 404 with no Location header; GITHUB.IO 404: CONFIRMED recorded in 32-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "No redirect stub, meta-refresh page, or CNAME file exists anywhere in the repository; the only github.io mention outside .planning/ is the historical CHANGELOG.md entry"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "test -f CNAME (absent); git grep 'github\\.io' -- ':!.planning' shows exactly CHANGELOG.md:393; git grep 'http-equiv' -- ':!.planning' empty"
        status: pass
    human_judgment: false
  - id: D6
    description: "The revival hazard and the resolved hosting-migration todo are handed off to /gsd-complete-milestone in writing"
    requirement: "CI-04"
    verification:
      - kind: other
        ref: "32-EVIDENCE.md ## Handoffs names git ls-remote origin, /gsd-complete-milestone, dependabot PR #123, and 2026-07-21-move-documentation-hosting-to-read-the-docs.md"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-07-27
status: complete
---

# Phase 32 Plan 03: Push, Observe CI, Delete gh-pages, Owner Handoff Summary

**Pushed the post-teardown tree to milestone draft PR #124 and cited a fresh green `build-docs` run (30275369792, head `d53edec…`) whose docs-pdf regression gate succeeded at step level; permanently deleted `origin/gh-pages` (matched Plan 01's baseline SHA `f97862d…`, no revival) and proved its absence via live `git ls-remote`; then directly observed `https://YuSabo90002.github.io/typsphinx/` returning `404` with no owner Settings action performed this session — GITHUB.IO 404: CONFIRMED.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-27T14:31:00Z (approx.)
- **Completed:** 2026-07-27T14:35:12Z
- **Tasks:** 3
- **Files modified:** `32-EVIDENCE.md` (append-only, incremental across all 3 task commits) + remote git state (push, branch deletion — no repo files touched by Tasks 1/2/3 beyond the evidence file)

## Accomplishments

- **Task 1 (SC#3, D-04 re-confirmation):** re-checked all four RTD URLs (200), confirmed the local milestone branch tip (`d53edec…`) carried Plan 02's teardown (0 `peaceiris`, 1 `Upload PDF to Release`), pushed `gsd/v0.6.4-read-the-docs-migration` to origin, and cited a fresh green `build-docs` run (`30275369792`) whose `headSha` matches the pushed SHA and differs from Plan 01's pre-teardown baseline (`980f6ca9…`). Per-step conclusions recorded, including `Build PDF documentation (English only)` = success. PR #124 confirmed still draft; no workflow trigger was added.
- **Task 2 (SC#2, irreversible):** re-took the before-state `git ls-remote` (gh-pages at `f97862d…`, matching Plan 01's baseline exactly — no revival), deleted `refs/heads/gh-pages` via `git push origin --delete gh-pages` (succeeded directly, no `gh api` fallback needed), and proved the after-state absence with both filtered and full unfiltered `git ls-remote origin` output. `refs/heads/main` confirmed untouched.
- **Task 3 (owner-manual handoff, 404, redirect-stub sweep, Handoffs):** wrote the owner-manual Settings → Pages disable instruction (REQUIREMENTS.md step #7) without performing or claiming completion. Directly observed 4 independent 404s at `https://YuSabo90002.github.io/typsphinx/` (with and without `-L`, plus full response headers confirming genuine GitHub Pages infrastructure with no `Location:` header) — recorded `GITHUB.IO 404: CONFIRMED`, side by side with Plan 01's pre-teardown `200` baseline. A fresh repo-wide grep confirmed no `CNAME` file and exactly one `github.io` hit outside `.planning/` (the historical `CHANGELOG.md:393` mention). Recorded `## Handoffs` for `/gsd-complete-milestone`: a `git ls-remote` re-check around the merge (naming dependabot PR #123 as a live revival-hazard instance) and closing the `2026-07-21-move-documentation-hosting-to-read-the-docs.md` todo.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-confirm the gate, push the post-teardown tree to draft PR #124, and observe a fresh green build-docs run against it** - `373a9ec` (docs)
2. **Task 2: Delete origin/gh-pages and prove its absence with a live remote query** - `b706b6d` (docs)
3. **Task 3: Hand off the owner-manual Pages disable, observe the github.io 404, and record the revival-hazard handoff** - `b797690` (docs)

_Plan metadata commit deferred to worktree-mode convention — this SUMMARY.md's own commit stands in for it since STATE.md/ROADMAP.md updates are owned by the orchestrator after wave merge._

## Cited CI Run (SC#3)

- **Run:** `30275369792` — `https://github.com/YuSabo90002/typsphinx/actions/runs/30275369792`
- **Head SHA (pushed/teardown commit):** `d53edecfd064a93d7a43455d505f7848a1c43320`
- **Plan 01's pre-teardown baseline head SHA (for contrast, NOT what was cited):** `980f6ca909b8b07045d664548094b98f31bd8551`
- **Conclusion:** `success` · **Event:** `pull_request`
- **`Build PDF documentation (English only)` step:** `success` (the `uv run tox -e docs-pdf` typstpdf regression gate, recorded at step level, not inferred from the job)
- **Cited run's own tree re-verified:** `git show d53edec…:.github/workflows/docs.yml | grep -c peaceiris` → `0`

## Deleted gh-pages SHA (SC#2)

- **Deleted SHA:** `f97862dfea151dd904591a18d2ddbd0bf72fd851`
- **Matched Plan 01's baseline:** yes, exactly — no revival occurred between the gate and the deletion.
- **Deletion command:** `git push origin --delete gh-pages` (succeeded directly; no `gh api -X DELETE` fallback needed)
- **Proof:** live `git ls-remote origin refs/heads/gh-pages` → no output; `refs/heads/main` confirmed still resolves.

## GITHUB.IO 404 Verdict

```
GITHUB.IO 404: CONFIRMED
```

Directly observed across 4 independent `curl` attempts (with `-L`, without `-L`, full response
headers, and a stability re-check), all returning `404` with no `Location:` header — i.e. no
redirect of any kind. Side by side with Plan 01's pre-teardown baseline for the same URL
(`200`), the transition is measured, not asserted.

**A-02 resolved:** this session performed no owner Settings action (no owner was present) — the
site 404s from branch deletion alone. The owner-manual Settings → Pages disable (REQUIREMENTS.md
step #7) remains on the checklist as the locked, permanent, defense-in-depth action; this
observation does not retire that step, it only confirms the current source-less state already
serves 404.

## Handoffs

**To `/gsd-complete-milestone`:**

1. **Re-run `git ls-remote origin`** immediately before and after the milestone merge, and
   confirm `refs/heads/gh-pages` is still absent. `main`'s copy of `docs.yml` retains the
   `peaceiris/actions-gh-pages@v4` deploy step until this milestone merges — any push landing on
   `main` first (before the merge) re-fires that unmodified workflow and recreates `gh-pages`,
   silently invalidating this plan's SC#2 proof after the fact. **Dependabot PR #123**
   (`dependabot/pip/ruff-gte-0.15-and-lt-0.17`) is an open live instance of exactly this
   condition. This is the recommended minimum mitigation CONTEXT.md records; this phase does not
   block on PR #123's disposition (a permanent fix was explicitly declined to be scoped by the
   owner).
2. **Close the pending todo**
   `.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md`
   (`resolves_phase: 32`) once this plan's commits merge — it is resolved by this phase landing.

## Files Created/Modified

- `.planning/phases/32-github-pages-teardown-irreversible/32-EVIDENCE.md` - appended the D-04 re-confirmation, SC#3 CI-run citation, SC#2 deletion proof, owner-manual handoff, 404 observation, redirect-stub sweep, and Handoffs sections
- `.planning/phases/32-github-pages-teardown-irreversible/32-03-SUMMARY.md` - this file
- Remote git state: `origin/gsd/v0.6.4-read-the-docs-migration` pushed (`980f6ca..d53edec`); `origin/refs/heads/gh-pages` permanently deleted

## Decisions Made

- D-04 same-day re-confirmation was sufficient (today matched Plan 01's gate date); only the four URL statuses were re-checked, not the full five-check gate.
- Task 3's 404 observation used 4 independent attempts (rather than stopping at 1) even though the first attempt already returned 404 — this exercises the plan's bounded-retry posture and rules out a transient/false-positive 404 via the full-headers cross-check, without looping indefinitely.
- A-02 (deleting gh-pages alone might not 404 the site) resolved empirically in the "harmless either way" direction the flagged assumption anticipated: it already 404s. The owner-manual Settings step is documented as retained regardless, per REQUIREMENTS.md's locked checklist — this observation is evidence the *current* state is already correct, not a basis to skip the owner's action.

## Deviations from Plan

**1. [Note, not a deviation — plan acceptance-criterion wording was stale relative to the whole milestone diff] The `git diff --name-only <merge-base>..HEAD -- .github/workflows/` acceptance check listed two files, not one.**
- **Found during:** Task 1, acceptance-criteria verification.
- **Issue:** The plan's acceptance criterion expected `git diff --name-only $(git merge-base main HEAD)..HEAD -- .github/workflows/` to list only `docs.yml`. It actually lists `docs.yml` AND `links.yml`, because the diff base is the whole milestone's merge-base with `main`, and `.github/workflows/links.yml` was added earlier in the milestone by Phase 31 (`feat(31-01): add advisory repo-wide link-check workflow`, commit `fede6f0`) — not by this task or this plan.
- **Resolution:** No code change needed. Verified and recorded in `32-EVIDENCE.md` that (a) this task made no edit to any workflow file (docs.yml was already edited by Plan 02, before this plan started) and no trigger was added anywhere, and (b) scoping the same diff command to `-- .github/workflows/docs.yml` specifically returns exactly one file, confirming the acceptance criterion's actual intent (no trigger added to obtain the CI run) is satisfied. Documented as a discrepancy between the plan's literal wording and the milestone-wide diff scope, not a defect in this plan's execution.
- **Files modified:** none (verification-only finding, recorded in evidence).
- **Commit:** `373a9ec` (the finding and its resolution are recorded within Task 1's evidence commit).

No other deviations. All other acceptance criteria and success criteria for all three tasks passed as written, including the honest-verifier 404 observation which produced a *better* result (CONFIRMED) than the environment briefing's expected outcome (PENDING-OWNER) — recorded as directly observed evidence, not assumed.

## Issues Encountered

None. All three tasks' automated verification commands passed on first execution.

## User Setup Required

**Owner-manual step #7 remains open on REQUIREMENTS.md's checklist** (disable GitHub Pages in
Settings → Pages), even though the observed effect (github.io 404) is already CONFIRMED without
it having been performed this session. The owner should still complete this step at their
convenience as the locked, permanent, defense-in-depth action — see `## Owner-manual step` in
`32-EVIDENCE.md` for the exact navigation path.

## Next Phase Readiness

Phase 32 (CI-04) is now closed on the automated side: the deploy step is gone (Plan 02),
`origin/gh-pages` is gone and proven absent by live `git ls-remote` (Plan 03 Task 2), no redirect
stub exists anywhere (Plan 03 Task 3), the github.io 404 is directly observed and CONFIRMED (not
merely pending), and a fresh green CI run on the post-teardown tree keeps the docs-pdf regression
gate and the tag-time Release attachment intact (Plan 03 Task 1). The revival hazard (dependabot
PR #123, `main`'s unmodified `docs.yml` until merge) and the resolved hosting-migration todo are
both handed to `/gsd-complete-milestone` in writing.

No blockers. Phase 33 (v0.6.4 Release Prep) may proceed once this wave merges.

---
*Phase: 32-github-pages-teardown-irreversible*
*Completed: 2026-07-27*
