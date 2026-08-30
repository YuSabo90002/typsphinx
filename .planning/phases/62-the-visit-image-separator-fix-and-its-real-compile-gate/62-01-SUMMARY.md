---
phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
plan: 01
subsystem: core-translator
tags: [sphinx, typst, translator, separator, real-compile-gate, tracer]

# Dependency graph
requires:
  - phase: 59-path-shape-predicate-and-image-uri-correctness
    provides: escape_typst_string() reused unmodified for image URI escaping
provides:
  - visit_image()/depart_image() joined to the existing separator triad, both in_figure branch bodies untouched (AMENDED D-08, IMG-08/IMG-10 tracer shape)
  - a 3-master tracer real-compile gate (index / fail_01_sub_mid_sentence / pass_parent) proving IMG-09's #include() blast-radius closure
  - canonical milestone branch gsd/v0.9.2-inline-image-blocker-fix-and-release pushed to origin with an upstream (SC#5 first half)
  - measured PHASE_BASE_SHA seeded in 62-RED-EVIDENCE.md for plan 03's RED choreography
affects: [62-02, 62-03, 62-04]

# Actuals (#2632)
actuals:
  tokens: 4567
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "visit_image()'s leading separator triad is hoisted above the in_figure/else split so a legend image (in_figure==True) reaches the same in_list_item/list_item_needs_separator context visit_legend already sets"
    - "depart_image()'s trailing bookkeeping consults _mark_inline_concat_content() before emitting the unconditional trailing newlines, so a field-list-body concat context is not broken"

key-files:
  created:
    - tests/fixtures/inline_image_separator_render_gate/conf.py
    - tests/fixtures/inline_image_separator_render_gate/index.rst
    - tests/fixtures/inline_image_separator_render_gate/fail_01_sub_mid_sentence.rst
    - tests/fixtures/inline_image_separator_render_gate/pass_parent.rst
    - tests/fixtures/inline_image_separator_render_gate/pass_a_standalone_block_image.rst
    - tests/fixtures/inline_image_separator_render_gate/_static/pic.png
    - tests/test_inline_image_separator_render_gate.py
    - .planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md
    - .planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/COVERAGE.md
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Applied the AMENDED D-08 mechanism from 62-01-PLAN.md <amendments>: the triad's leading half is hoisted above the if self.in_figure:/else: split (not confined to the else branch), because confining it leaves legend and field-list-body shapes red -- both in_figure branch bodies stay textually unmodified, satisfying SC#3's substance (a 9-line pure insertion, zero deletions, zero modified lines) even though its literal wording predicted the else-branch-only placement."
  - "Measured correction to the plan's D-10/D-11 assumption, recorded in 62-RED-EVIDENCE.md's SC#5 section: .github/workflows/links.yml has an UNSCOPED push trigger (unlike ci.yml, which is scoped to main/develop) and DID fire on the milestone-branch push, completing success in seconds. It is explicitly advisory (never a required status check) and is not the D-11 authority run -- plan 04 still owns dispatching that."
  - "No decoy branch (gsd/v0.9.2-milestone) was present at Task 2's pre-push git branch -vv measurement, so D-12's pointer-advance-before-deletion choreography was not needed this time."

requirements-completed: []  # IMG-08, IMG-09, IMG-10, TEST-05 close only after plan 04's phase-close measurements (per this plan's <output> directive)

coverage:
  - id: D1
    description: "The tracer fixture's failing shape (a substitution image mid-sentence) and image-free index master both build a valid PDF under sphinx-build -b typstpdf, proving IMG-08's separator fix and IMG-09's #include() blast-radius closure for the tracer subset"
    requirement: "IMG-08"
    verification:
      - kind: integration
        ref: "tests/test_inline_image_separator_render_gate.py::TestInlineImageSeparatorFullMatrix::test_full_matrix_every_master_writes_a_pdf"
        status: pass
    human_judgment: false
  - id: D2
    description: "The fail shape's emitted content .typ contains no unseparated closing-paren-then-image( juxtaposition"
    requirement: "IMG-08"
    verification:
      - kind: integration
        ref: "tests/test_inline_image_separator_render_gate.py::TestInlineImageSeparatorFailShapes::test_fail_shape_emits_a_separator_before_image"
        status: pass
    human_judgment: false
  - id: D3
    description: "typsphinx/translator.py's visit_image()/depart_image() diff is a pure 9-line insertion with zero deletions; both in_figure branch bodies are textually unchanged; the three ROADMAP SC#3 line-boundary-predicate spellings remain absent"
    requirement: "IMG-10"
    verification:
      - kind: other
        ref: "git diff --numstat 5a837238..HEAD -- typsphinx/translator.py (9/0); grep -F for the three forbidden spellings (no match)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The full pre-existing test suite passes with zero failures and zero pre-existing test edits (D-13); black --check and mypy are green; the two exact-byte figure gate tests pass unedited"
    requirement: "TEST-05"
    verification:
      - kind: unit
        ref: "uv run pytest -q (1515 passed, 5 skipped, 0 failed)"
        status: pass
      - kind: unit
        ref: "uv run pytest tests/test_nested_figure_render_gate.py tests/test_pdf_render_gate.py -q (38 passed)"
        status: pass
      - kind: other
        ref: "uv run black --check . ; uv run mypy typsphinx/"
        status: pass
    human_judgment: false
  - id: D5
    description: "Milestone branch gsd/v0.9.2-inline-image-blocker-fix-and-release is on origin, tracked as the local branch's upstream, exactly one local 0.9.2 branch exists, and no tag was created (SC#5 first half)"
    requirement: null
    verification:
      - kind: other
        ref: "git ls-remote --heads origin gsd/v0.9.2-inline-image-blocker-fix-and-release; git rev-parse --abbrev-ref ...@{upstream}; git branch --list 'gsd/v0.9.2*' (count 1); git tag -l 'v0.9.2*' (empty)"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-30
status: complete
---

# Phase 62 Plan 01: The `visit_image()` Separator Fix and Its Real-Compile Gate (Tracer) Summary

**`visit_image()`/`depart_image()` joined to the existing separator triad (AMENDED D-08: hoisted above the `in_figure`/`else` split), proven by a real `typst.compile()` tracer gate over one failing shape and the image-free `index` master, with the canonical milestone branch pushed to `origin`.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-30 (approx, before first read)
- **Completed:** 2026-08-30T07:48:36Z
- **Tasks:** 3
- **Files modified:** 10 (9 created, 1 modified)

## Accomplishments
- `visit_image()`'s leading separator triad (`_add_paragraph_separator()` + `_emit_inline_concat_separator()` + `in_list_item`/`list_item_needs_separator`) now runs on BOTH the `in_figure` and non-`in_figure` paths, mirroring `visit_Text`'s canonical call shape verbatim — the AMENDED D-08 mechanism from `62-01-PLAN.md <amendments>`, needed because confining it to the non-`in_figure` branch alone leaves legend-image shapes red.
- `depart_image()`'s trailing bookkeeping is now concat-aware: it consults `_mark_inline_concat_content()` before the existing unconditional trailing newlines, so a field-list-body concat context is not broken by an extra `\n\n`.
- Net diff over `typsphinx/translator.py`: a pure 9-line insertion, 0 deletions, 0 modified lines — both `in_figure` branch bodies stay textually unchanged, and none of ROADMAP SC#3's three forbidden line-boundary-predicate spellings were introduced.
- A new 3-master tracer fixture (`tests/fixtures/inline_image_separator_render_gate/`) and gate module (`tests/test_inline_image_separator_render_gate.py`) prove the fix end to end on a real `sphinx-build -b typstpdf` → `typst.compile()` path: the failing shape (a substitution image mid-sentence) and the image-free `index` root master (proving the `#include()` blast radius is closed) both write valid `%PDF` output.
- `gsd/v0.9.2-inline-image-blocker-fix-and-release` pushed to `origin` with `-u`; exactly one local `0.9.2` branch, zero tags — the milestone-branch-to-origin invariant (SC#5 first half) discharged at phase head per D-10.
- `62-RED-EVIDENCE.md` seeded with the measured `PHASE_BASE_SHA` (`5a837238aadc126611b175228cbed5ac8b1058f8`), taken via `git rev-parse HEAD` before any file in this phase was touched — never copied from executor worktree metadata, per the plan's explicit warning that this project's `worktree_metadata.expected_base` is unreliable.

## Task Commits

Each task was committed atomically:

1. **Task 1: One failing shape, end to end — fixture, the separator fix, and a real-compile gate** - `8430ca62` (feat)
2. **Task 2: Put the canonical milestone branch on origin with an upstream** - `056906b5` (docs)
3. **Task 3: Guardrails — COVERAGE.md, the IMG-10 structural greps, and a full-suite baseline** - `e8d3236e` (docs)

## Files Created/Modified
- `typsphinx/translator.py` - `visit_image()`/`depart_image()` gain the 9-line separator-triad insertion (AMENDED D-08)
- `tests/test_inline_image_separator_render_gate.py` - the tracer's real-compile gate module (TEST-05)
- `tests/fixtures/inline_image_separator_render_gate/conf.py` - 3-entry `typst_documents` tracer subset (grows to 18 in plan 02)
- `tests/fixtures/inline_image_separator_render_gate/index.rst` - image-free root master (SC#1 blast-radius document)
- `tests/fixtures/inline_image_separator_render_gate/fail_01_sub_mid_sentence.rst` - FEATURES.md Q1 row 1 (substitution image mid-sentence)
- `tests/fixtures/inline_image_separator_render_gate/pass_parent.rst` - positive-control parent (D-03), toctrees the one PASS document
- `tests/fixtures/inline_image_separator_render_gate/pass_a_standalone_block_image.rst` - FEATURES.md Q2 row A
- `tests/fixtures/inline_image_separator_render_gate/_static/pic.png` - copied from `glob_image_render_gate`'s fixture image
- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md` - `PHASE_BASE_SHA` + SC#5 push transcript; RED/golden/restore sections left for plan 03
- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/COVERAGE.md` - no-external-API declaration (Phase 59 precedent)

## Decisions Made
- Applied the AMENDED D-08 mechanism (leading triad hoisted above the `in_figure`/`else` split) as directed by the plan's `<amendments>` block, rather than the pre-amendment `ARCHITECTURE.md`-recommended else-branch-only placement — this was a planning-time amendment already owner-acknowledged, not a new deviation introduced during execution.
- No decoy branch (`gsd/v0.9.2-milestone`) existed at Task 2's pre-push measurement, so D-12's pointer-advance-before-deletion choreography was not exercised this time — recorded as a measured (not assumed) fact in `62-RED-EVIDENCE.md`.

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing critical functionality, or blocking issues were encountered that required Rule 1-3 auto-fixes.

### Measured Correction (not a fix — a plan-assumption correction, documented per instructions)

**1. `links.yml`'s unscoped push trigger fired on the milestone-branch push, contrary to the plan's stated expectation**
- **Found during:** Task 2 (branch-to-origin push)
- **Issue:** The plan's Task 2 acceptance criteria asserted `gh run list --branch <milestone-branch> --limit 5` would show no run triggered by the push, reasoning (D-10/D-11) that `.github/workflows/ci.yml`'s `push`/`pull_request` triggers are scoped to `main`/`develop`. Measured: a SEPARATE workflow, `.github/workflows/links.yml` ("Link Check"), declares an unscoped `on: push:` with no branch filter, and it DID trigger — completing `success` in seconds.
- **Resolution:** Not a fix — this is a measured correction to the plan's assumption, not a defect in this plan's own work. `links.yml` is explicitly advisory per its own header comment ("never registered as a GitHub required status check, so a red or cancelled run never blocks a merge"). It is not the D-11 authority run (that is `ci.yml`, still unstarted by this push, still owned by plan 04). No action was taken to suppress or cancel it — doing so would be out of scope and could look like evidence suppression.
- **Files modified:** none (documentation only, in `62-RED-EVIDENCE.md`'s SC#5 section)
- **Verification:** `gh run list --branch gsd/v0.9.2-inline-image-blocker-fix-and-release --json ...` transcribed verbatim in `62-RED-EVIDENCE.md`.
- **Committed in:** `056906b5` (Task 2 commit)

---

**Total deviations:** 0 auto-fixed; 1 measured correction to a plan assumption (documented, no code/process change required).
**Impact on plan:** None on substance — D-10's "zero CI minutes for the authority run" and D-11's "exactly one authority run, owned by plan 04" both still hold; only the *literal wording* of the acceptance criterion ("no run triggered") needed a factual correction, now on record.

## Issues Encountered

None beyond the measured correction documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02 can proceed: the tracer's mechanism (AMENDED D-08 triad hoist) is proven end to end on the 3-master subset and is ready to extend to the full 16 FAIL / 9 PASS / 18-master matrix.
- `PHASE_BASE_SHA` is recorded in `62-RED-EVIDENCE.md` for plan 03's RED-evidence choreography.
- The milestone branch is on `origin` with an upstream, satisfying SC#5's first half; plan 04 still owes the single D-11 authority CI dispatch at phase end.
- No blockers.

---
*Phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate*
*Completed: 2026-08-30*

## Self-Check: PASSED

- `typsphinx/translator.py` - FOUND (modified, verified via `git diff --numstat` = 9/0)
- `tests/test_inline_image_separator_render_gate.py` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/conf.py` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/index.rst` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/fail_01_sub_mid_sentence.rst` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/pass_parent.rst` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/pass_a_standalone_block_image.rst` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/_static/pic.png` - FOUND
- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md` - FOUND
- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/COVERAGE.md` - FOUND
- Commit `8430ca62` - FOUND in `git log --oneline --all`
- Commit `056906b5` - FOUND in `git log --oneline --all`
- Commit `e8d3236e` - FOUND in `git log --oneline --all`
- All task `<acceptance_criteria>` re-verified: PASS (see Task Commits section and the plan-level `<verification>` checks re-run above)
