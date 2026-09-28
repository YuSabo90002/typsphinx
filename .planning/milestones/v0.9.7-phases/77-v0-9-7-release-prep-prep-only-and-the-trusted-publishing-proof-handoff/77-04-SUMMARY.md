---
phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
plan: 04
subsystem: release-process
tags: [testing, documentation-build, linkcheck, pytest, ruff, black, mypy, preview-sync]

# Dependency graph
requires:
  - phase: 77 (waves 1: 77-01, 77-02, 77-03)
    provides: the bumped 0.9.7 tip (BUMP_COMMIT_SHA), the curated CHANGELOG extraction proof (EXTRACT_MATCHES_SECTION), and the base documentation/linkcheck ledger (77-BASE-EVIDENCE.md, 77-CLOSEOUT-GUARD.md)
provides:
  - "77-GREEN-TREE-EVIDENCE.md: SC3_LOCAL_VERDICT = MET, proving the bumped tip green on runs executed in this plan, not on Phase 76's word"
  - "Lint trio (ruff, black, mypy) and the full pytest suite (1573 passed, 1 skipped) run twice — host locale and LC_ALL=C — both zero-failed, zero-error, zero changelog-page-gate skips"
  - "The @preview version-sync family passing with all four packages intact and the three sync sites unchanged since the milestone base"
  - "Clean C-locale docs-html and docs-pdf builds (0 warnings each), not risen above 77-01's base ledger (also 0/0)"
  - "tox -e linkcheck classified PASS-CLASS-A-ONLY: 95/97 working, the two non-working records exactly the v0.9.7 tag-referencing changelog links (each 404, v0.9.6 controls 200), URI-set delta proving nothing else changed"
affects: [77-06 (reads SC3_LOCAL_VERDICT before pushing and dispatching CI), 77-07 (carries the two linkcheck records forward as a re-check obligation, not a waiver)]

# Actuals (#2632)
actuals:
  tokens: 3156
  tasks: 3
  commits: 3
  plan_head_before: 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3
  plan_head_after: eb677b52e3d7af27da6f2e04b7a1dac40834220c

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Every counted documentation build removes the whole docs/_build tree first and runs under LANG=C LANGUAGE=C LC_ALL=C, then re-parses its own warning integer from the saved log rather than trusting a running total."
    - "A linkcheck classification is accepted only when bounded to a literal, enumerated URI set with measured controls and an exact tip-versus-base URI-set delta (comm -13/-23) — never a broad pattern match."

key-files:
  created:
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-GREEN-TREE-EVIDENCE.md
  modified: []

key-decisions:
  - "None beyond what 77-CONTEXT.md and the Phase 75 precedent already settled — this plan applies the owner's 2026-09-20 PASS-CLASS-A-ONLY reading to the identical v0.9.7 shape, re-measured and re-bounded rather than assumed."

requirements-completed: []

coverage:
  - id: D1
    description: "Lint trio and full pytest suite (twice, once under LC_ALL=C) proven green on the bumped tip in this plan's own worktree, with the interpreter recorded and zero changelog-page-gate skips"
    requirement: REL-17
    verification:
      - kind: other
        ref: "77-04-PLAN.md Task 1 <verify><automated> (re-run live, exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Clean C-locale docs-html and docs-pdf builds, warning integers not risen above 77-01's base ledger, docs/source unchanged over the phase"
    requirement: REL-17
    verification:
      - kind: other
        ref: "77-04-PLAN.md Task 2 <verify><automated> (re-run live, exit 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Tip linkcheck classified PASS-CLASS-A-ONLY against measured controls and an exact URI-set delta; SC3_LOCAL_VERDICT = MET recorded for 77-06's push gate"
    requirement: REL-17
    verification:
      - kind: other
        ref: "77-04-PLAN.md Task 3 <verify><automated> (re-run live, exit 0)"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-09-28
status: complete
---

# Phase 77 Plan 04: SC#3 Local — Green Tree Proof on the Bumped Tip Summary

**Lint trio, full pytest (1573 passed/1 skipped) twice, clean C-locale docs builds and a
PASS-CLASS-A-ONLY linkcheck reading all proven fresh on the bumped 0.9.7 worktree — `SC3_LOCAL_VERDICT = MET`.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-09-28T13:09:00Z
- **Completed:** 2026-09-28T13:54:00Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments
- Ran `ruff check .`, `black --check .` and `mypy typsphinx/` on the bumped tip — all exit 0.
- Ran the full pytest suite twice (host locale and `LC_ALL=C`): `1573 passed, 1 skipped` in both,
  the one skip being the pre-existing env-gated `tests/test_corpus_gate.py`, zero
  changelog-page-gate skips in either run.
- Ran `tests/test_preview_version_sync.py`: all four `@preview` packages declared consistently,
  and the three declaration sites (`typsphinx/writer.py`, `typsphinx/template_engine.py`,
  `typsphinx/templates/base.typ`) unchanged since the milestone base.
- Built `docs-html` and `docs-pdf` from a removed `docs/_build` under `LANG=C LANGUAGE=C LC_ALL=C`:
  both `build succeeded.` with 0 warnings, matching 77-01's base ledger (also 0/0).
- Ran `tox -e linkcheck` on the bumped tip: 95/97 `working`; the two non-`working` records are
  exactly the `v0.9.7` tag-referencing changelog links (each measured 404, with the `v0.9.6`
  controls measured 200), and a `comm`-based URI-set delta against 77-01's base proves the tip's
  URI set differs by exactly those two added and the `v0.9.6` compare link removed.
- Applied the project owner's 2026-09-20 reading (`75-GREEN-TREE-EVIDENCE.md` § "AMENDED
  2026-09-20") to the identical shape: `TIP_LINKCHECK_VERDICT = PASS-CLASS-A-ONLY`, recorded as a
  **carried obligation, not a waiver** — both records must be re-checked once the tag and the
  GitHub Release exist, per `77-HANDOFF.md`.
- `SC3_LOCAL_VERDICT = MET`, with every contributing key from all three tasks enumerated in the
  evidence file's own `## SC#3 local verdict` section.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — lint trio, full pytest suite twice, @preview family** - `1f8c5154` (test)
2. **Task 2: Clean C-locale docs-html and docs-pdf, compared against base ledger** - `eaad3cc2` (test)
3. **Task 3: Linkcheck classified against controls, SC#3 local verdict** - `eb677b52` (test)

**Plan metadata:** committed together with this SUMMARY (see final commit).

## Files Created/Modified
- `.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-GREEN-TREE-EVIDENCE.md` - lint trio, both full pytest runs with skip transcripts, the `@preview` invariant, clean tip documentation builds against the base ledger, the classified linkcheck reading with its URI-set delta, and `SC3_LOCAL_VERDICT`

## Decisions Made
None - plan executed exactly as written. The linkcheck classification applies the reading the
project owner already approved on 2026-09-20 for the identical v0.9.6 shape (`77-CONTEXT.md`
flagged assumption), re-measured and re-bounded to the two literal `v0.9.7` URIs rather than
re-decided.

## Deviations from Plan

None - plan executed exactly as written. Every gate ran green on the first attempt: lint trio,
both pytest runs, the `@preview` family, both documentation builds, and the linkcheck attempt (1
of the allowed 3) all matched expectations without requiring a retry or a fix.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
`SC3_LOCAL_VERDICT = MET` is recorded in `77-GREEN-TREE-EVIDENCE.md` for `77-06` to gate its push
and CI dispatch on. The two classified linkcheck records
(`https://github.com/YuSabo90002/typsphinx/compare/v0.9.7...HEAD` and
`https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.7`) are carried forward as an
obligation `77-07` must write into `77-HANDOFF.md` as a required post-tag re-check step, not a
waiver. No blockers for wave 3.

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Completed: 2026-09-28*

## Self-Check: PASSED

- `77-GREEN-TREE-EVIDENCE.md` FOUND on disk at the path recorded above.
- All three task commits (`1f8c5154`, `eaad3cc2`, `eb677b52`) FOUND in `git log --oneline --all`.
- All three tasks' `<verify><automated>` blocks re-run live and printed `VERIFY_PASS`.
- All three tasks' `<acceptance_criteria>` confirmed met during execution (lint trio and both
  pytest runs green with zero failures/errors/changelog-gate-skips; both documentation builds
  clean and not risen above the base ledger; linkcheck classified PASS-CLASS-A-ONLY with
  `SC3_LOCAL_VERDICT = MET`).
- The plan-level `<verification>` block's four bullets all hold, matching the evidence file.
