---
phase: 31-published-url-cutover-repo-wide-link-guard
plan: 05
subsystem: docs
tags: [readthedocs, link-check, lychee, ci, github-issue, todo-hygiene]

# Dependency graph
requires:
  - phase: 31-published-url-cutover-repo-wide-link-guard (plan 01)
    provides: ".github/workflows/links.yml and the red negative-control run this plan's green run is paired against"
  - phase: 31-published-url-cutover-repo-wide-link-guard (plan 03)
    provides: "the DOC-09 URL rewrite in README.md/pyproject.toml that this plan's green run and consolidated grep/fetch pass measure"
  - phase: 31-published-url-cutover-repo-wide-link-guard (plan 04)
    provides: "the refreshed INTEGRATIONS.md whose URLs this plan's consolidated fetch re-verifies independently"
provides:
  - "31-EVIDENCE.md's positive (green) half of the D-09 CI evidence pair, plus the SC#2 consolidated fresh-grep/real-HTTP measurement"
  - "A fixed, non-bot-blocked replacement for README.md's Claude Code attribution link, discovered as a 4th failure class during the consolidated sweep"
  - "31-ISSUE-119-REPLY-DRAFT.md — a terse, English, owner-review-pending close-reply for Issue #119"
  - "The 2026-07-22 github.io-404 todo annotated resolved in place (not moved, to avoid the worktree deletion guard)"
affects: [complete-milestone-handoffs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CI false-positive triage: verify liveness with a browser-UA curl before choosing to tune --accept vs. fix the URL at the source; prefer the source fix when a literal-200 bar applies elsewhere in the same phase"

key-files:
  created:
    - .planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ISSUE-119-REPLY-DRAFT.md
  modified:
    - .planning/phases/31-published-url-cutover-repo-wide-link-guard/31-EVIDENCE.md
    - .planning/todos/pending/2026-07-22-github-io-doc-links-404-missing-en-prefix.md
    - README.md
    - .github/workflows/links.yml (net unchanged — tuned then reverted; see Deviations)

key-decisions:
  - "A 403 from a bot-blocking host is fixed at the source (repoint the URL to a non-blocked canonical successor) rather than tuned away in links.yml's --accept set, once a task in the same plan requires a literal curl-measured 200 — tuning is the right call only when no such literal bar exists elsewhere."
  - "Task 1's --accept 403 CI tuning, having become unnecessary once the source was fixed, was reverted rather than left in place, to avoid silently widening acceptance for any future unrelated 403."

requirements-completed: [DOC-09, DOC-10, CI-05]

coverage:
  - id: D1
    description: "Link Check concludes success on the rewritten tree, with the red/green pair (Plan 01 negative control + this plan's positive run) both recorded in 31-EVIDENCE.md with run URLs, conclusions, SHAs, and a then/now side-by-side"
    requirement: "CI-05"
    verification:
      - kind: other
        ref: "gh run view 30265271094 --json conclusion (success, 0 errors, final re-observation after all fixes) — see 31-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#2's consolidated fresh repo-wide grep (retired host in CHANGELOG.md only) and real-HTTP fetch of all 35 distinct URLs across README.md/pyproject.toml/INTEGRATIONS.md, all returning 200"
    requirement: "DOC-09"
    verification:
      - kind: other
        ref: "grep -rl 'github\\.io' --exclude-dir=.git --exclude-dir=.planning . -> CHANGELOG.md only; 35/35 curl -L fetches -> 200 — see 31-EVIDENCE.md Task 2"
        status: pass
    human_judgment: false
  - id: D3
    description: "Issue #119 close-reply drafted (English, terse, fulfillment-report only, awaiting owner review); issue left OPEN and untouched; folded todo annotated resolved in place without a deletion"
    requirement: "DOC-10"
    verification:
      - kind: other
        ref: "gh issue view 119 --json state,comments -> OPEN, 1 comment (unchanged); 31-ISSUE-119-REPLY-DRAFT.md acceptance checks; git diff --diff-filter=D --name-only HEAD~1 -> empty"
        status: pass
    human_judgment: false
  - id: D4
    description: "Green tree confirmed: full pytest suite passes on the fully-committed state"
    verification:
      - kind: unit
        ref: "uv run pytest -q -m 'not slow' -> 617 passed, 0 failed"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-07-27
status: complete
---

# Phase 31 Plan 05: Link Check Green Run + SC#2 Measurement + Issue #119 Draft Summary

**Closed the phase by pairing a green Link Check run against the rewritten tree with Plan 01's red negative control, taking a fresh consolidated real-HTTP measurement of all 35 documentation URLs (fixing one previously-unnoticed bot-blocked link discovered along the way), and preparing an owner-review-pending close-reply for Issue #119.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-07-27T21:20:39+09:00
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified; `links.yml` touched transiently and reverted, net unchanged)

## Accomplishments

- Pushed this plan's branch and observed the Link Check mechanism go green on the DOC-09-rewritten tree (run `30265271094`, conclusion `success`, 0 errors, 93 total links / 84 successful / 9 excluded / 20 redirected), transcribed alongside Plan 01's red negative-control run in `31-EVIDENCE.md` with a full then/now side-by-side (8 errors -> 0, all 7 retired-host deep links gone from the tree entirely) — the CI-05 mechanism is proven to have caught the original failure and to now pass because the links resolve, not because the scan stopped looking.
- Took SC#2's consolidated measurement fresh against the merged tree: a repo-wide grep for the retired `github.io` host returns `CHANGELOG.md` only (its historical mention is intentional, Phase 24 D-02 precedent), a second grep confirms `pyproject.toml`'s old README-anchor `Documentation` value is gone, and all 35 distinct URLs extracted from `README.md`, `pyproject.toml`, and `.planning/codebase/INTEGRATIONS.md` return HTTP 200 — transcribed verbatim, grouped by source file, cross-referencing Plan 02's and Plan 04's independent measurements rather than duplicating them.
- Discovered and fixed a 4th failure class the milestone brief hadn't named: README.md's Claude Code attribution link (`https://claude.ai/code`) returns `403` to a plain, no-UA `curl` — a bot-blocking response, not a dead link (confirmed alive via browser-UA `curl`), but one that fails SC#2's literal "every URL returns 200" bar. Fixed at the source by repointing to its canonical, non-bot-blocked successor (`https://claude.com/product/claude-code`, confirmed 200 to plain `curl`, and confirmed the destination three independent candidate URLs all redirect to), then reverted the CI-side `--accept 403` tuning that had been applied in Task 1 before this fix, since it was no longer needed and would otherwise needlessly widen the detector's acceptance.
- Drafted `31-ISSUE-119-REPLY-DRAFT.md`: re-read Issue #119's full live thread (state `OPEN`, 1 comment, no new question since the 2026-07-26 planning-time reading), then wrote a 3-line, English, fulfillment-report-only reply citing the new Read the Docs URL and its measured status — marked unmistakably as awaiting owner review, not posted, issue not closed (D-15/D-16).
- Annotated the folded todo (`2026-07-22-github-io-doc-links-404-missing-en-prefix.md`) resolved in place — frontmatter status fields plus a body-level Japanese "決着" section naming the resolving commit (`bd80fb8`, Plan 03) — without moving or deleting the file, since `worktree.cleanup-wave` blocks any branch containing a deletion with no bypass.

## Task Commits

Each task was committed atomically (Task 1 required one mid-task tuning-and-revert cycle, tracked below):

1. **Task 1a: Push and observe; tune `--accept` for the claude.ai/code 403 false positive** - `829a0b5` (chore)
2. **Task 1b: Record the green Link Check run and its comparison to the negative control** - `227ce29` (docs)
3. **Task 2a: Fix the claude.ai/code link at the source; revert the now-unneeded `--accept` tuning** - `260ade4` (fix)
4. **Task 2b: Record the SC#2 consolidated fresh-grep and real-HTTP measurement** - `a58163f` (docs)
5. **Task 3: Draft the Issue #119 close-reply and annotate the resolved todo in place** - `2969314` (docs)

_No TDD tasks; this is a CI-observation/measurement/docs plan with no test files._

## Files Created/Modified

- `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-EVIDENCE.md` - Appended the green Link Check run, the tuning-then-revert trace, the SC#2 consolidated grep/fetch measurement, and the final re-observation confirming the reverted (tighter) `--accept` set stays green
- `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ISSUE-119-REPLY-DRAFT.md` - New; the Issue #119 close-reply draft, awaiting owner review
- `.planning/todos/pending/2026-07-22-github-io-doc-links-404-missing-en-prefix.md` - Annotated resolved in place (not moved)
- `README.md` - Repointed the Claude Code attribution link from the bot-blocked `claude.ai/code` to its canonical successor `claude.com/product/claude-code`
- `.github/workflows/links.yml` - Touched twice (widen `--accept` to include 403, then revert); net byte-identical to its state before this plan (confirmed via `git diff` against the pre-plan commit)

## Decisions Made

- A CI false positive that is genuinely alive (verified via browser-UA `curl`) is normally the sanctioned case for `--accept` tuning under D-06 — but when a *different* task in the same plan (Task 2's SC#2 measurement) applies a literal, no-UA "every URL returns 200" bar to the same URL, the correct resolution is to fix the URL at the source, not to tune the checker. Doing the tuning first (Task 1) and then superseding it with a source fix (Task 2) is recorded as the honest sequence of discovery rather than retroactively rewriting Task 1's history.
- The `--accept 403` widening was reverted once it became unnecessary, rather than left in place as harmless slack — an unused acceptance widening is a latent risk (it would silently pass a future, unrelated 403) with no offsetting benefit once its sole motivating case was fixed at the source.
- The folded todo's resolution is recorded via frontmatter + an in-body Japanese "決着" section (matching this project's existing closed-todo convention) rather than a bare one-line status flag, so the resolution reads with the same level of detail as the original problem description.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed the claude.ai/code bot-blocking 403 discovered during SC#2's consolidated sweep**
- **Found during:** Task 2 (SC#2 consolidated fresh-grep/real-HTTP measurement)
- **Issue:** `README.md`'s "Developed with Claude Code" attribution link (`https://claude.ai/code`) returns `403 Forbidden` to a plain, no-User-Agent `curl -L` request — the exact instrument Task 2's acceptance criteria use. The URL is not dead (browser-UA `curl` and Task 1's diagnostic both return `200`), but it fails the task's literal bar. This URL is not one of DOC-09's 7 retired-host deep links and was not named in the plan's `files_modified` list.
- **Fix:** Repointed the link to `https://claude.com/product/claude-code` — confirmed to be the URL's current canonical destination (three independent candidate URLs, including `www.anthropic.com/claude-code`, all redirect there) and confirmed to return `200` to a plain, no-UA `curl` with no workaround needed.
- **Files modified:** `README.md` (not in the plan's `files_modified` list — added per Rule 1)
- **Verification:** `curl -s -o /dev/null -w "%{http_code}" -L "https://claude.com/product/claude-code"` -> `200`; Task 2's full 35-URL fetch pass (post-fix) shows 35/35 returning `200`.
- **Committed in:** `260ade4` (Task 2, fix commit)

**2. [Rule 1 - Bug, follow-on] Reverted the now-superseded `--accept 403` CI tuning**
- **Found during:** Task 2, immediately after fix #1 above
- **Issue:** Task 1 had widened `links.yml`'s `--accept` set to include `403` to get Link Check green before the source fix existed. Once fix #1 removed the only 403-returning URL from the tree, this widening was unnecessary and, left in place, would silently accept any future unrelated 403 elsewhere in the repository.
- **Fix:** Reverted `--accept` to its original `'100..=103,200..=299,429'` and removed the now-orphaned explanatory comment block, in the same commit as fix #1.
- **Files modified:** `.github/workflows/links.yml` (in the plan's `files_modified` list; net change across the whole plan is zero — see Files Created/Modified)
- **Verification:** Re-pushed; Link Check run `30265271094` still concluded `success` with an identical 0-error summary under the reverted, tighter `--accept` set — confirming the green result now comes from the source fix, not the CI tuning.
- **Committed in:** `260ade4` (same commit as fix #1)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — a genuine bug discovered during in-scope measurement, and its direct follow-on cleanup).
**Impact on plan:** Both deviations are within the phase's own SC#2 bar ("every documentation URL... returns a live page") and its `31-CONTEXT.md`-anticipated possibility ("a fourth failure appearing here is a finding, not noise"). No scope creep beyond the one link and its CI-tuning follow-on; `typsphinx/` untouched (milestone invariant #3 held); no file was moved or deleted (worktree deletion guard held).

## Issues Encountered

None beyond the deviations documented above. The worktree's `.venv/bin/uv` required the documented NixOS symlink fix (`ln -sf <nix-store uv> .venv/bin/uv`) to get a clean `pytest` signal — a standing, previously-diagnosed environmental issue (see this project's `nixos-sandbox-test-env` memory note), not a new problem. The symlink is venv-local and untracked by git.

## User Setup Required

None - no external service configuration required for this plan. (Posting the Issue #119 reply and closing the issue are explicitly deferred to `/gsd-complete-milestone` — see Handoffs below.)

## Handoffs

Two items this phase deliberately leaves unfinished, both by owner decision (D-15), for `/gsd-complete-milestone` to discharge:

1. **Post the Issue #119 reply and close the issue**, after owner review of `31-ISSUE-119-REPLY-DRAFT.md` — deferred until the DOC-09 README rewrite is visible on `main` (D-15/D-16), so the fulfillment report describes a fix the reporter can actually verify, not one still sitting on a feature branch.
2. **Move `.planning/todos/pending/2026-07-22-github-io-doc-links-404-missing-en-prefix.md` into `.planning/todos/completed/`** — the resolution is already recorded in place (frontmatter + body "決着" section); only the physical file move is deferred, because `worktree.cleanup-wave` blocks any branch containing a deletion with no bypass, and a `git mv` registers as one.

These join the four post-merge flips already owed from Phases 29 and 30.1 (per `29-VERIFICATION.md` § "Phase 33 Handoff Precondition" and `STATE.md`'s carry-forwards): the parent RTD project's Default branch -> `main`, the `typsphinx-ja` RTD project's Default branch -> `main`, `.gitmodules`' `branch` field -> `main`, and RTD's Default Version `latest` -> `stable` (after the `v0.6.4` tag builds green). Milestone close should read this as **one list of six items**, not six scattered notes across three phases.

## Next Phase Readiness

- Phase 31's four success criteria are all measured and recorded: the Link Check red/green pair is complete and attributable to the DOC-09 rewrite (SC#1/SC#3), SC#2's fresh consolidated grep+fetch pass covers all three named surfaces with zero exceptions after the one in-scope fix, and DOC-10's "About set + resolving + close-reply drafted" half is fully discharged (the close itself is the recorded handoff above, per D-15's deliberate phase-boundary split).
- `typsphinx/` untouched throughout this plan (milestone invariant #3 held for the whole phase).
- Ready for Phase 32 (GitHub Pages teardown) — this phase's ordering rationale (prove the new links resolve while both hosts are still live, before destroying the old one) is now fully evidenced, not just asserted.
- Ready for `/gsd-complete-milestone` to pick up this plan's two Handoffs alongside the four pre-existing ones.

---
*Phase: 31-published-url-cutover-repo-wide-link-guard*
*Completed: 2026-07-27*

## Self-Check: PASSED

- FOUND: .planning/phases/31-published-url-cutover-repo-wide-link-guard/31-EVIDENCE.md
- FOUND: .planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ISSUE-119-REPLY-DRAFT.md
- FOUND: .planning/todos/pending/2026-07-22-github-io-doc-links-404-missing-en-prefix.md
- FOUND: README.md
- FOUND: .github/workflows/links.yml
- FOUND commit: 829a0b5
- FOUND commit: 227ce29
- FOUND commit: 260ade4
- FOUND commit: a58163f
- FOUND commit: 2969314
