---
phase: 61-v0-9-1-release-prep-prep-only
plan: 01
subsystem: docs
tags: [changelog, myst, docs-build, release-prep]

# Dependency graph
requires:
  - phase: 59-path-shape-predicate-and-image-uri-correctness
    provides: PATH-01, IMG-04, IMG-05, IMG-06, IMG-07 fixes and their evidence
  - phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
    provides: MSG-02, MSG-03, MSG-04, MSG-05 fixes and their evidence
provides:
  - Three defect-family bullets under CHANGELOG.md's existing ## [Unreleased] heading
  - 61-CHANGELOG-EVIDENCE.md recording base SHA, pre/post fence measurements, and both docs builds
affects: [61-02, 61-03, 61-04, v0.9.2-release-prep]

# Actuals (#2632)
actuals:
  tokens: 3881
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CHANGELOG bullets authored from scratch under ## [Unreleased] (D-03 shape, not the Phase 57 promote-existing-bullets shape)"
    - "Docs-warning baseline comparison requires a clean rm -rf docs/_build before each measurement -- an incremental rebuild under-reports warnings from unrelated unchanged pages"

key-files:
  created:
    - .planning/phases/61-v0-9-1-release-prep-prep-only/61-CHANGELOG-EVIDENCE.md
  modified:
    - CHANGELOG.md

key-decisions:
  - "PATH-01 bullet states the predicate change is contract hardening, not a user-affecting bugfix, per REQUIREMENTS.md's recorded unreachability from both real call sites"
  - "Path-diagnostics bullet names a POSIX path containing an apostrophe as an affected case (per CONTEXT specific idea #1), so no bullet frames the milestone's fixes as Windows-exclusive"
  - "MSG-01 and the new internal module typsphinx/pathfmt.py do not earn CHANGELOG bullets -- both are internal-only by construction (58-REPR-CENSUS.md)"
  - "No ### Verified subsection authored this phase -- deferred to the v0.9.2 release-prep phase, which will write it against the whole 0.9.2 diff"

patterns-established:
  - "Docs-warning measurements in evidence files must be taken on a freshly cleaned docs/_build, never an incremental rebuild, to avoid under-reporting"

requirements-completed: [REL-09]

coverage:
  - id: D1
    description: "PATH-01 authored as a real CHANGELOG bullet under ## [Unreleased], accurately describing it as contract hardening (not a user-affecting fix)"
    requirement: "REL-09"
    verification:
      - kind: other
        ref: "awk over CHANGELOG.md's ## [Unreleased] region asserting >=1 bullet citing PATH-01, plus the accuracy-constraint prose check"
        status: pass
    human_judgment: false
  - id: D2
    description: "IMG-04/05/06/07 and MSG-02/03/04/05 authored as CHANGELOG bullets in the same ### Fixed subsection, citing all nine requirement IDs and naming a POSIX apostrophe path as an affected case"
    requirement: "REL-09"
    verification:
      - kind: other
        ref: "awk over CHANGELOG.md's ## [Unreleased] region asserting 9 unique requirement IDs and >=1 'quote character' occurrence"
        status: pass
    human_judgment: false
  - id: D3
    description: "The whole edit is measurably pure addition against this plan's base SHA, with every version literal, release-heading count, link-reference count, and Known Limitations count byte-identical to the pre-edit measurement"
    verification:
      - kind: other
        ref: "git diff <base SHA> -- CHANGELOG.md | grep -cE '^-[^-]' == 0; grep -cE counts recorded in 61-CHANGELOG-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both documentation builds executed on the tree carrying all three bullets match the measured 3/5 warning baseline"
    requirement: "REL-09"
    verification:
      - kind: other
        ref: "uv run tox -e docs-html (build succeeded, 3 warnings.) and uv run tox -e docs-pdf (build succeeded, 5 warnings.) on a freshly cleaned docs/_build"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-29
status: complete
---

# Phase 61 Plan 01: CHANGELOG Authoring (Milestone Close-Out Prose) Summary

**Three latent-defect families from Phases 58-60 (PATH-01, IMG-04..07, MSG-02..05) authored as
real user-facing `### Fixed` bullets under CHANGELOG.md's existing `## [Unreleased]` heading,
each traceable to its requirement text and proven to render through MyST into both docs builds
with the warning count unchanged from the measured 3/5 baseline.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-29T14:45:00Z (approx, worktree provisioning start)
- **Completed:** 2026-08-29T15:10:41Z
- **Tasks:** 2 completed
- **Files modified:** 2 (`CHANGELOG.md`, `61-CHANGELOG-EVIDENCE.md`)

## Accomplishments

- Authored the PATH-01 tracer bullet first, proving the whole render chain
  (CHANGELOG.md → `docs/source/changelog.rst`'s MyST include → `docs-html`) end to end before
  writing the other two families, per the tracer-slice task shape.
- Authored the IMG family (IMG-04, IMG-05, IMG-06, IMG-07) and MSG family (MSG-02, MSG-03,
  MSG-04, MSG-05) bullets in the same `### Fixed` subsection, citing all nine requirement IDs.
- Proved the entire edit is pure addition against this plan's base SHA (`5e28fa9d...`) — zero
  removed lines, every historical release section and the tail link-reference block survive
  byte-identical.
- Ran both `docs-html` and `docs-pdf` on a freshly cleaned `docs/_build`, confirming 3 and 5
  warnings respectively — exactly the measured pre-existing baseline, with no new warning from
  any of the three bullets' MyST rendering.

## Task Commits

1. **Task 1: End-to-end slice — PATH-01 bullet, wired from requirement text through MyST to a
   rendered docs page** - `70b2823b` (docs, tracer)
2. **Task 2: Author the remaining two defect families and prove pure addition + full docs bar**
   - `8bb0288e` (docs)

**Plan metadata:** committed separately per worktree convention (STATE.md/ROADMAP.md excluded;
orchestrator owns those after the wave merges).

## Files Created/Modified

- `CHANGELOG.md` — three `### Fixed` bullets added under the existing `## [Unreleased]` heading;
  `### Planned for Future Releases` and every historical `## [x.y.z]` section untouched.
- `.planning/phases/61-v0-9-1-release-prep-prep-only/61-CHANGELOG-EVIDENCE.md` — created; records
  base SHA, pre/post-edit fence measurements, the PATH-01 tracer's docs-html run, the pure-addition
  diff, the full fence-assertion command/output pairs, and the final docs-html/docs-pdf
  warning-count comparison.

## Decisions Made

- PATH-01's bullet is worded as contract hardening, not a repaired user-facing defect — matching
  REQUIREMENTS.md's "Reachability, measured 2026-08-27" note that neither real call site can reach
  the pre-fix gap.
- The path-diagnostics bullet explicitly names a POSIX path with an apostrophe (`O'Brien`) as an
  affected case, per CONTEXT specific idea #1's binding framing constraint — no bullet in this
  plan frames the milestone's fixes as belonging to a single platform.
- MSG-01 (test-side-only decoupling) and the internal `typsphinx/pathfmt.py` module do not earn
  their own bullets — both are internal by construction and this project's CHANGELOG has
  historically described user-visible behavior only.
- No `### Verified` subsection authored this phase; deferred to the v0.9.2 release-prep phase per
  the "cheaper default" discretion item, to be written against the whole 0.9.2 diff.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Line-wrap split the required "quote character" phrase across two lines**
- **Found during:** Task 2 (authoring the MSG-family bullet)
- **Issue:** The initial wording wrapped "quote" and "character" onto separate lines, so the
  plan's own `<verify>` grep for the literal phrase `quote character` returned 0 instead of ≥1.
- **Fix:** Re-wrapped the sentence so "quote character" sits on one physical line.
- **Files modified:** `CHANGELOG.md`
- **Verification:** `awk '/^## \[Unreleased\]/,/^## \[0\.9\.0\]/' CHANGELOG.md | grep -ci 'quote character'` returns 1
- **Committed in:** `8bb0288e` (Task 2 commit — the correction landed before commit, not as a follow-up)

**2. [Rule 1 - Bug] Incremental docs rebuild under-reports the warning baseline**
- **Found during:** Task 2 (re-running `docs-html`/`docs-pdf` after both non-PATH-01 bullets landed)
- **Issue:** Re-running `uv run tox -e docs-html` against the `docs/_build` directory left over
  from Task 1's run produced `build succeeded.` with zero warnings — Sphinx's incremental build
  only reprocesses pages invalidated by the changed file (`changelog.rst`), so the pre-existing
  `visit_toctree` docstring warnings on unrelated pages were not recounted. This would have
  under-proven the baseline comparison the plan requires.
- **Fix:** `rm -rf docs/_build` before each measurement, forcing a full (non-incremental) rebuild
  that matches what a fresh checkout (e.g. CI) would produce.
- **Files modified:** none (build-artifact directory only, gitignored)
- **Verification:** Fresh `docs-html` run reports `build succeeded, 3 warnings.`; fresh `docs-pdf`
  run reports `build succeeded, 5 warnings.` — both matching the measured baseline exactly.
- **Committed in:** n/a (no source change; the corrected build commands are recorded verbatim in
  `61-CHANGELOG-EVIDENCE.md`, committed in `8bb0288e`)

---

**Total deviations:** 2 auto-fixed (1 bug in authored prose, 1 bug in the verification procedure
itself — an incremental-build false-negative risk, not a defect in `typsphinx/`).
**Impact on plan:** Both fixes were necessary to make the plan's own acceptance criteria
trustworthy; neither introduced scope creep. No `typsphinx/`, `tests/`, or `docs/` source file was
touched by either fix.

## Issues Encountered

None beyond the two deviations documented above, both resolved within the same task before
committing.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `CHANGELOG.md`'s `## [Unreleased]` block now holds all three defect-family bullets this
  milestone needs to record; `61-02` (fence observation 1 + `61-CLOSEOUT-GUARD.md`) can proceed
  independently in the same wave.
- The v0.9.2 release-prep phase, when it runs, promotes these bullets into its own `## [0.9.2]`
  section (D-03's stated mechanism) and authors the `### Verified` subsection this plan
  deliberately deferred.
- No blockers or concerns for downstream plans in this phase.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Completed: 2026-08-29*
