---
phase: 42-captioned-table-drops-preceding-target-label
plan: 01
subsystem: testing
tags: [sphinx, typst, docutils, render-gate, regression-fixture, pytest]

# Dependency graph
requires: []
provides:
  - "tests/fixtures/captioned_table_propagated_target_render_gate/ — D-01's four failing shapes (named target, unnamed target, list-item-nested target, two consecutive targets) plus a caption-less byte-invariance control"
  - "tests/test_captioned_table_propagated_target_render_gate.py — TestCaptionedTablePropagatedTargetRenderGate, nine assertions, RED against unfixed depart_table"
  - "42-GATE-EVIDENCE-01.md — SC#1 (reproduction + observed depart_table ids) and SC#5's RED half"
affects: [42-04, 42-05, 42-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One dedicated fixture directory per fixed-defect-class (never extend an already-GREEN unrelated fixture during a RED-recording window)"
    - "Class-scoped real-compile build fixture shared across nine thin single-behavior test methods"
    - "index:-prefixed label-definition scan via negative lookbehind on link( — reused for both the D-03 duplicate-label check and the generic dangling-reference sweep"

key-files:
  created:
    - tests/fixtures/captioned_table_propagated_target_render_gate/conf.py
    - tests/fixtures/captioned_table_propagated_target_render_gate/index.rst
    - tests/test_captioned_table_propagated_target_render_gate.py
    - .planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-01.md
  modified: []

key-decisions:
  - "New fixture directory rather than extending tests/fixtures/captioned_table_render_gate/ — avoids contaminating that already-GREEN class's exact-count sentinel assertions during the RED-recording window (research recommendation, followed as planned)"
  - "Label-definition regex uses a negative lookbehind on link( restricted to index:-prefixed tokens, matching both the [#metadata(none) <name>] and the figure self-anchor postfix ) <name>] forms in one pass"

patterns-established:
  - "Classic-compile-fatal RED recorded via a throwaway (uncommitted) depart_table probe script pasted verbatim into the evidence file, rather than a committed debug utility"

requirements-completed: [TBL-03]

coverage:
  - id: D1
    description: "Fixture reproduces all four D-01 failing shapes plus the caption-less control; a real -b typst build emits the dangling references and exactly four figure-wrapped tables"
    requirement: "TBL-03"
    verification:
      - kind: integration
        ref: "uv run python -m sphinx -b typst -q -E tests/fixtures/captioned_table_propagated_target_render_gate <build>"
        status: pass
    human_judgment: false
  - id: D2
    description: "Render-gate module records the classic RED against unfixed depart_table with the exact does not exist in the document signature; production code untouched at this commit"
    requirement: "TBL-03"
    verification:
      - kind: integration
        ref: "tests/test_captioned_table_propagated_target_render_gate.py (7/9 RED, verified NON-zero exit + literal signature)"
        status: pass
    human_judgment: false
  - id: D3
    description: "42-GATE-EVIDENCE-01.md records the recording commit, verbatim TypstError, per-shape observed node[ids]/node[names] (including the reversed chained-target order), and the verbatim RED"
    requirement: "TBL-03"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-01.md"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-03
status: complete
---

# Phase 42 Plan 01: Captioned-Table Propagated-Target RED Gate Summary

**New render-gate fixture + module recording the classic compile-fatal RED for TBL-03 (a standalone target immediately before a captioned table drops the target's label), plus 42-GATE-EVIDENCE-01.md with the observed per-shape `depart_table` ids including the reversed chained-target order.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-08-03T23:13:50+09:00 (branch base)
- **Completed:** 2026-08-03T23:26:13+09:00
- **Tasks:** 3
- **Files modified:** 4 (all new)

## Accomplishments
- Authored a dedicated GATE-01 fixture (`tests/fixtures/captioned_table_propagated_target_render_gate/`) covering D-01's four measured-failing shapes (named target, unnamed target, list-item-nested target, two consecutive targets) plus a caption-less byte-invariance control table
- Authored `tests/test_captioned_table_propagated_target_render_gate.py` — nine thin test methods over one class-scoped `-b typstpdf` build — and confirmed it is RED against the current, unfixed `depart_table`: 7/9 tests fail with the real `TypstError: label \`<index:tbl-target>\` does not exist in the document` fatal; the other 2 (D-03 no-duplicate-label, caption-less control) already pass pre-fix as expected, since the bug drops anchors rather than duplicating or mis-wrapping them
- Recorded `42-GATE-EVIDENCE-01.md`: the recording commit with an empty `typsphinx/` status, the verbatim Shape-A reproduction and `TypstError` text, a per-shape `node["ids"]`/`node["names"]` table captured via a throwaway (uncommitted) `depart_table` probe script — including the explicit callout that Shape D's two chained targets arrive **reversed** relative to source order (`tbl-target-b` before `tbl-target-a`) — and the verbatim 7/9-failing pytest RED

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the captioned-table propagated-target fixture** - `b2a3564` (feat)
2. **Task 2: Author the classic RED-to-GREEN render-gate module and commit it against unfixed source** - `d28f2c8` (test)
3. **Task 3: Record the RED and the observed depart_table ids in 42-GATE-EVIDENCE-01.md** - `1b715cd` (docs)

_No TDD RED/GREEN/REFACTOR cycle applies to Task 2 itself — this plan is TBL-03's own classic-RED milestone-invariant exception (alongside CIT-01): the fixture and test module are committed once, recording the RED against unfixed production code. GREEN lands in a separate later plan (42-04)._

## Files Created/Modified
- `tests/fixtures/captioned_table_propagated_target_render_gate/conf.py` - master-document Sphinx config (`numfig = True` for the `:numref:` reference)
- `tests/fixtures/captioned_table_propagated_target_render_gate/index.rst` - five tables (D-01's four failing shapes + caption-less control) with a references-back section using explicit-text `:ref:`/`:numref:` roles
- `tests/test_captioned_table_propagated_target_render_gate.py` - `TestCaptionedTablePropagatedTargetRenderGate`, nine test methods (compile-clean, per-shape anchor presence ×4, D-03 no-duplicate-label, generic dangling-reference sweep, caption-less-not-figure-wrapped, PDF magic bytes)
- `.planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-01.md` - SC#1 + SC#5(RED) evidence

## Decisions Made
- Gave TBL-03 its own new fixture directory rather than extending the already-GREEN `captioned_table_render_gate/` — matches the research recommendation and the established "one fixture per fixed defect class" convention (`paragraph_propagated_target_render_gate/` et al.), avoiding contamination of that class's exact-count sentinel assertions during this plan's RED-recording window.
- Used a single generalized regex (`(?<!link\()<(index:[^>]+)>`) for label-definition detection, matching both the `[#metadata(none) <name>]` propagated-anchor form and the figure self-anchor postfix `) <name>]` form in one pass — reused unchanged for both the D-03 duplicate-label check and the generic dangling-reference sweep, per the plan's explicit "two load-bearing implementation details" instruction.
- Wrote the `depart_table`-id-observation probe as a throwaway script under the session scratchpad (never under `tests/`, `typsphinx/`, or `scripts/`) and pasted its full source into the evidence file, per the plan's explicit prohibition on committing it.

## Deviations from Plan

None - plan executed exactly as written. All acceptance criteria for all three tasks were verified directly (fixture build assertions, RED signature, evidence-file content greps) rather than assumed.

## Issues Encountered

**NixOS sandbox `ruff`/`uv` shim setup (environmental, not a defect):** the worktree's freshly `uv sync`'d `.venv/bin/uv` and `.venv/bin/ruff` are generic-linux ELF binaries that fail under the NixOS stub loader. `uv` was fixed with the standard `ln -sf "$(command -v uv)" .venv/bin/uv` shim (resolves to a `/nix/store/...` path). No system-wide `ruff` binary exists on this worktree's `PATH` to symlink from, so `ruff` was instead provisioned by copying the main checkout's own patchelf'd `.venv/bin/ruff` binary directly into the worktree's `.venv/bin/ruff` (verified `ruff 0.15.20` runs and matches the pinned version). Both `uv run python -c "import typsphinx..."` and `ruff --version` were confirmed resolving inside the worktree before any verification command was trusted.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Wave 1's other two plans (42-02, 42-03) proceed independently in this same wave. Plan 42-04 (wave 2, `depends_on: ["42-01"]`) is unblocked: it can now move `depart_table`'s `_emit_id_anchors` call to fire after `self.in_table` is cleared and re-run this exact module (`uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v`) to confirm all 9 tests turn GREEN, recording that in `42-GATE-EVIDENCE-04.md`. No blockers.

---
*Phase: 42-captioned-table-drops-preceding-target-label*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: tests/fixtures/captioned_table_propagated_target_render_gate/conf.py
- FOUND: tests/fixtures/captioned_table_propagated_target_render_gate/index.rst
- FOUND: tests/test_captioned_table_propagated_target_render_gate.py
- FOUND: .planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-01.md
- FOUND commit: b2a3564
- FOUND commit: d28f2c8
- FOUND commit: 1b715cd
- FOUND commit: 543d38a
