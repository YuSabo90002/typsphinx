---
phase: 42-captioned-table-drops-preceding-target-label
plan: 03
subsystem: translator
tags: [sphinx, typst, docutils, anchors, sweep, evidence]

# Dependency graph
requires: []
provides:
  - "42-GATE-EVIDENCE-03.md: a repo-wide static classification of all 21 `_emit_id_anchors(` call sites in `typsphinx/translator.py`, plus a real-build re-measurement of both image-path call sites"
  - "Confirmation that `depart_table` is the ONLY misrouted call site in the entire file (D-06 satisfied, non-image, already known as the phase's own TBL-03 defect)"
  - "Confirmation that no image-path misrouting exists (D-07 satisfied, null result, D-06's 'fixed inside this phase' branch does not fire)"
  - "A filed pending todo carrying the D-08 whitespace-only-title-anchor divergence"
affects: [42-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Static sweep methodology: enumerate every call site of a shared emission helper via grep, cross-reference against the ONE flag the routing function (`add_text`) actually consults (read `add_text`'s own body, don't assume), then classify each site's own-flag state at call time."
    - "Formal image-path re-measurement: a throwaway Sphinx probe project under the session scratchpad (never `tests/`), driven through a real `-b typstpdf` build, with `.typ` label/link grep pairs as the falsifiable check — not a transcription of an earlier informal measurement."

key-files:
  created:
    - .planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-03.md
    - .planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md
  modified: []

key-decisions:
  - "The sweep's finding list contains exactly one MISROUTED row (`depart_table`, line 3341) — the phase's own already-known TBL-03 defect, not a new finding requiring its own todo. No other non-image call site is misrouted."
  - "The image-path re-measurement (both `visit_image` and `depart_figure`) is a NULL RESULT: a real `-b typstpdf` build of a two-shape probe project exits 0 with empty stderr, produces a non-empty PDF, and every `link(<index:...>)` reference in the emitted `.typ` matches a `<index:...>` label definition, including both propagated-target anchors. D-06's 'an image-path finding is fixed inside this phase' condition is therefore moot — no production code was touched by this plan."
  - "Documented (not filed as a new finding) a secondary, unrelated bug in `visit_rubric`: its `len(self.body)` before/after check for 'did I just emit an anchor' would read False for a rubric nested in a table cell (anchor still lands correctly in `table_cell_content`, just not detected by that length check) — a separator/spacing bookkeeping issue, not an anchor-drop, so it does not match this sweep's defect predicate and was left out of scope."

patterns-established:
  - "A node's own trailing anchor firing while a buffer-diverting flag IT opened for its children is still active is the actual hazard shape (depart_table). A DIFFERENT node's anchor firing while an ENCLOSING node's flag happens to still be open (e.g. a paragraph nested in a table cell) is desired routing, not a finding — this distinction is now recorded in evidence, not just tribal knowledge."

requirements-completed: [TBL-03]

coverage:
  - id: D1
    description: "Repo-wide static sweep: all 21 `_emit_id_anchors(` call sites in translator.py enumerated and classified SAFE/MISROUTED with an image-path flag, derived from the live tree at a named commit (D-06, D-07)"
    requirement: "TBL-03"
    verification:
      - kind: other
        ref: ".planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-03.md §1 (grep-derived classification table, verified against add_text's own body)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Formal, real-build re-measurement of both image-path call sites (visit_image, depart_figure) — null result, no image-path misrouting"
    requirement: "TBL-03"
    verification:
      - kind: integration
        ref: "uv run python -m sphinx -b typstpdf -q -E against a throwaway probe project — exit 0, empty stderr, index.pdf produced, both link(<index:...>) references matched by label definitions (42-GATE-EVIDENCE-03.md §2)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-08 whitespace-only-title-anchor divergence filed as a pending todo carrying the negative-but-inconclusive probe result"
    requirement: "TBL-03"
    verification:
      - kind: other
        ref: ".planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-03
status: complete
---

# Phase 42 Plan 03: Repo-Wide Anchor-Misrouting Sweep + Image-Path Re-Measurement + D-08 Todo Summary

**A full static sweep of every `_emit_id_anchors` call site in `translator.py` (21 sites, one MISROUTED: `depart_table`, the phase's own already-known defect) plus a real `-b typstpdf` build confirming zero image-path misrouting — both required by D-06/D-07 before plan 42-04's fix lands.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-03T14:27:32Z
- **Tasks:** 3
- **Files modified:** 0 production files; 2 new evidence/todo files

## Accomplishments

- Enumerated and classified all 21 `_emit_id_anchors(` call sites in `typsphinx/translator.py` against the live tree at commit `19a6378e6b12ec086e3e3af11f93e736a30c0cb3` (unfixed), confirming `add_text` consults exactly one buffer-diverting flag (`self.in_table`) and that `depart_table` is the sole MISROUTED site.
- Re-took the image-path measurement formally with a real `-b typstpdf` build of a throwaway two-shape probe project (bare image + captioned figure, each preceded by a standalone target), independent of the discussion-time and research-session measurements D-07 rules inadmissible — result: null, no image-path finding, D-06's "fixed inside this phase" branch does not fire.
- Filed the D-08 whitespace-only-title-anchor divergence as a pending todo, carrying the already-measured negative-but-inconclusive trailing-whitespace probe result forward so the next investigator does not re-run it.

## Task Commits

Each task was committed atomically:

1. **Task 1: Enumerate and classify every anchor-emission call site** - `5df4d6b` (docs)
2. **Task 2: Re-take the image-path measurement formally, with a real build (D-07)** - `4ad2194` (docs)
3. **Task 3: File the D-08 whitespace-only-title-anchor divergence as a pending todo** - `6441f73` (docs)

_No TDD tasks in this plan — all three tasks produce evidence/todo artifacts, no production code._

## Files Created/Modified

- `.planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-03.md` - Full static classification table (21 call sites) + formal image-path real-build measurement + D-06/D-07 disposition
- `.planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md` - D-08 divergence, filed per the phase's scope fence (D-05)

## Decisions Made

- The sweep confirms `depart_table` (line 3341) is the ONLY misrouted call site across the entire file — this is the phase's own already-known TBL-03 defect (fixed by plan 42-04, not by this plan), not a new discovery requiring its own todo.
- The image-path measurement is a formal NULL RESULT: both `visit_image` and `depart_figure` correctly anchor propagated-target ids in a real compiled build. No production code was changed by this plan, consistent with D-06's condition only firing on an actual image-path finding.
- A secondary, unrelated observation in `visit_rubric` (a `len(self.body)`-based "did I emit an anchor" check that would misread when nested in a table cell) was documented in the evidence file as out-of-scope — it is a spacing/bookkeeping issue, not an anchor-drop, and does not match this sweep's defect predicate, so it was not filed as a new todo.

## Deviations from Plan

None - plan executed exactly as written. No image-path finding was surfaced, so D-06's escalation path (recording a finding in this plan's Deviations for the orchestrator to route) was never triggered — the plan's own acceptance criteria anticipated and covered this outcome (§2.5's explicit NULL RESULT requirement).

## Issues Encountered

None. The worktree's per-worktree `uv sync` + `uv run` provisioning (CLAUDE.md's standing requirement) was completed successfully; `import typsphinx` was verified bound to this worktree's own editable copy before any measurement was taken.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `42-GATE-EVIDENCE-03.md` is ready for plan 42-04 (wave 2) to reference as the sweep's evidence base: `depart_table` is the confirmed, sole, already-scoped fix target — no other call site in the file needs touching as part of that fix.
- The D-08 todo is filed and pending; it deliberately carries no urgency signal beyond what D-08 itself assigned (reachability unproven, low severity per the phase's own threat register T-42-08).
- No blockers for wave 2 or wave 3. This plan changed zero production code, so it introduces no merge risk against 42-01/42-02's parallel wave-1 work or 42-04's planned `depart_table` edit.

---
*Phase: 42-captioned-table-drops-preceding-target-label*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-03.md`
- FOUND: `.planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md`
- FOUND: `.planning/phases/42-captioned-table-drops-preceding-target-label/42-03-SUMMARY.md`
- FOUND commit: `5df4d6b`
- FOUND commit: `4ad2194`
- FOUND commit: `6441f73`
- FOUND commit: `6516aaa`
