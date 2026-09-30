---
phase: 40-citations-full-round-trip
plan: 02
subsystem: docs
tags: [reststructuredtext, citations, examples, roadmap, typst]

# Dependency graph
requires:
  - phase: 40-citations-full-round-trip (plan 01)
    provides: "the citation_render_gate fixture and GATE-01 methodology this plan's re-run of the shipped-sample gate follows"
provides:
  - "Both examples/charged-ieee/{approach1,approach2}/source/index.rst restored verbatim to the pre-removal blob 82831eb092b9f52cba8b1247b95f7e148f499bb2 (D-11), byte-identical to each other again (D-12)"
  - "tests/test_examples_charged_ieee_gate.py re-run (unedited) and recorded RED against a build/compile failure, the CIT-05 GATE-01 evidence for plan 40-03 to flip GREEN"
  - "ROADMAP.md Phase 40 Goal + SC#3 narrowed from an unqualified 'every citing location' claim to D-08's same-document backrefs scope, recorded as a dated Roadmap Evolution bullet (D-09)"
affects: ["40-03-PLAN.md (the source change this RED gates)", "40-04-PLAN.md (closes the RED-to-GREEN loop this plan's evidence starts)"]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-02.md
  modified:
    - examples/charged-ieee/approach1/source/index.rst
    - examples/charged-ieee/approach2/source/index.rst
    - .planning/ROADMAP.md

key-decisions:
  - "Narrowed the Phase 40 Goal paragraph's 'docutils' own back-references to every citing site' alongside SC#3, since it repeated the same unqualified overreach in different wording -- not left untouched for symmetry."
  - "Used git cat-file -p <blob> > <path> to write the exact pre-removal blob into both files rather than hand-editing or reverse-patching, per the plan's own instruction that the restore is fully determined."

requirements-completed: [CIT-05]

coverage:
  - id: D1
    description: "Both charged-ieee samples restored to the pre-removal blob and byte-identical to each other again"
    requirement: "CIT-05"
    verification:
      - kind: other
        ref: "git hash-object examples/charged-ieee/approach1/source/index.rst == git hash-object examples/charged-ieee/approach2/source/index.rst == 82831eb092b9f52cba8b1247b95f7e148f499bb2; diff between the two files empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_examples_charged_ieee_gate.py re-run unedited, RED for a build/compile reason (not a Python error, not a missing-file error)"
    requirement: "CIT-05"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_examples_charged_ieee_gate.py -v -- 2 failed (both on the sphinx-build returncode==0 assertion, TypstError compile fatal in stderr)"
        status: fail
    human_judgment: false
  - id: D3
    description: "ROADMAP Phase 40 SC#3 (and Goal paragraph) corrected to D-08's same-document back-reference scope, recorded as a dated Roadmap Evolution bullet (D-09), no other phase entry moved"
    requirement: "CIT-05"
    verification:
      - kind: other
        ref: "git diff -- .planning/ROADMAP.md confined to Phase 40 detail block + Roadmap Evolution section; grep -c '^### Phase ' unchanged (6); pre-existing Phase 39 bullet byte-unchanged"
        status: pass
    human_judgment: false
  - id: D4
    description: "This plan modifies no file under typsphinx/ or tests/"
    requirement: "CIT-05"
    verification:
      - kind: other
        ref: "git diff --stat -- typsphinx/ tests/ ccb37b2e7099386462968177cf500a196db67c07..HEAD (empty)"
        status: pass
    human_judgment: false

duration: 21min
completed: 2026-08-02
status: complete
---

# Phase 40 Plan 02: Restore charged-ieee citations verbatim + ROADMAP SC#3 correction Summary

**Both `examples/charged-ieee/{approach1,approach2}/source/index.rst` restored byte-identically to
the pre-removal blob, turning `tests/test_examples_charged_ieee_gate.py` RED on a real Typst compile
fatal (`unknown node type: <citation>` / `<label>` → `TypstError: expected semicolon or line
break`) — CIT-05's own GATE-01 evidence, ready to flip GREEN in plan 40-03 — plus ROADMAP.md Phase
40's SC#3 and Goal paragraph narrowed to D-08's same-document `backrefs` scope, recorded as a dated
Roadmap Evolution bullet (D-09).**

## Performance

- **Duration:** 21 min
- **Started:** 2026-08-02T08:23:00Z
- **Completed:** 2026-08-02T08:44:27Z
- **Tasks:** 3
- **Files modified:** 4 (2 examples, 1 ROADMAP.md edit, 1 new evidence file)

## Accomplishments
- Both `examples/charged-ieee/{approach1,approach2}/source/index.rst` restored to git blob
  `82831eb092b9f52cba8b1247b95f7e148f499bb2` — the exact pre-removal content commits `8bed1a3` and
  `c014a0b` stripped — verified byte-identical to each other and to the target blob via
  `git hash-object` and `diff`.
- `tests/test_examples_charged_ieee_gate.py` re-run unedited: RED on both test methods, failing at
  each method's first assertion (`sphinx-build` returncode == 0) with a real Typst compile fatal in
  `stderr` (two unknown-node warnings for `citation`/`label`, then
  `TypstError: expected semicolon or line break`) — not a Python error, not a missing-file error.
- ROADMAP.md Phase 40's Goal paragraph and SC#3 narrowed from an unqualified "back-references to
  every citing location/site" claim to D-08's same-document `backrefs` scope, with the amendment
  recorded as a dated Roadmap Evolution bullet (D-09) — SC#1/SC#2/SC#4/SC#5 and the pre-existing
  2026-08-02 Phase 39 bullet left byte-unchanged.
- `40-GATE-EVIDENCE-02.md` written recording the restoration proof, the verbatim RED pytest output,
  the verbatim unknown-node warning/compile-fatal text, an executed-vs-skipped statement
  (`TYPST_AVAILABLE` was `True`, both tests genuinely ran), confirmation the gate module itself was
  never touched, and the D-11 accepted-cost restatement (this sample proves only D-03's
  single-back-reference shape; multi-marker and D-05 widest-label shapes come from 40-01's fixture).

## Task Commits

Each task was committed atomically:

1. **Task 1: Restore both charged-ieee samples to their exact pre-removal content** - `1f643f0` (fix)
2. **Task 2: Correct ROADMAP Phase 40 SC#3 to D-08's same-document scope and record the amendment** - `4f79c6f` (docs)
3. **Task 3: Record the shipped-sample GATE-01 RED evidence** - `8c43dce` (docs)

No separate plan-metadata commit — SUMMARY.md is committed as part of this same session (worktree
mode; the orchestrator handles the final wave-level metadata commit).

## Files Created/Modified
- `examples/charged-ieee/approach1/source/index.rst` - restored to pre-removal blob (citation
  definition, inline reference, References heading back; top comment block removed)
- `examples/charged-ieee/approach2/source/index.rst` - same restoration; now byte-identical to
  `approach1`
- `.planning/ROADMAP.md` - Phase 40 Goal + SC#3 narrowed to same-document `backrefs` scope; one new
  dated Roadmap Evolution bullet (D-09)
- `.planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-02.md` - new, the shipped-sample
  GATE-01 RED evidence

## Decisions Made
- **Goal paragraph edited alongside SC#3.** The plan's Task 2 instructed checking whether the Goal
  paragraph "a few lines above" SC#3 repeated the same unqualified back-reference claim, narrowing
  it only if so. It did — "docutils' own back-references to every citing site" is the same overreach
  in different wording — so it was narrowed to "every same-document citing site" rather than left
  untouched for symmetry, per the plan's explicit branching instruction.
- **Blob write, not hand-edit.** Both restorations were done via `git cat-file -p <blob> > <path>`
  rather than reverse-patching the removal commits or hand-editing, per D-11/D-12 and the plan's own
  determination that the restore is fully specified by the blob.
- **STATE.md's mirrored Roadmap Evolution log intentionally left unedited.** Noted in the Task 2
  commit message and here per the plan's explicit instruction — it needs the same D-09 bullet, but
  the phase-close workflow owns that file, not this plan.

## Deviations from Plan

None - plan executed exactly as written. The only judgment call exercised was the Goal-paragraph
edit, which the plan itself anticipated and left as a conditional instruction (see Decisions Made
above) rather than a fixed action — so it is documented as a decision, not a deviation.

## Issues Encountered

None. The worktree environment required the standard per-worktree `uv sync --extra dev` provisioning
plus an `.venv/bin/uv` symlink to the Nix-store `uv` binary (the NixOS sandbox hazard this project's
CLAUDE.md documents); both were completed before any test run and are not deviations from the plan's
own `<environment_setup>` block.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `tests/test_examples_charged_ieee_gate.py`'s RED is now recorded against real shipped content and
  is ready for plan 40-03 to flip GREEN once `visit_citation`/`depart_citation`/`visit_label` land.
- ROADMAP.md's Phase 40 SC#3 now states the provable same-document scope, so `/gsd-verify-work` will
  grade the phase against the correct criterion rather than the wider claim the roadmap was
  originally written with.
- Full non-slow suite re-run after this plan's commits: 744 passed, 2 failed (both the expected
  examples-gate RED), 29 deselected — no incidental regression outside the two planned RED tests.
- STATE.md's Roadmap Evolution mirror still needs the D-09 bullet this plan's ROADMAP.md edit added
  — carried forward as a note for the phase-close workflow, not a blocker for plan 40-03/40-04.

## Self-Check: PASSED

- FOUND: `examples/charged-ieee/approach1/source/index.rst`
- FOUND: `examples/charged-ieee/approach2/source/index.rst`
- FOUND: `.planning/phases/40-citations-full-round-trip/40-GATE-EVIDENCE-02.md`
- FOUND: commit `1f643f0` (Task 1)
- FOUND: commit `4f79c6f` (Task 2)
- FOUND: commit `8c43dce` (Task 3)

---
*Phase: 40-citations-full-round-trip*
*Completed: 2026-08-02*
