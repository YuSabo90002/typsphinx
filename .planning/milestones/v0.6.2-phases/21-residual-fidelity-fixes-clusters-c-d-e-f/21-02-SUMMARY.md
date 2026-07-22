---
phase: 21-residual-fidelity-fixes-clusters-c-d-e-f
plan: 02
subsystem: rendering
tags: [sphinx, typst, translator, docutils, pypdf, gate-01]

# Dependency graph
requires:
  - phase: 21-residual-fidelity-fixes-clusters-c-d-e-f (plan 01, wave 1)
    provides: FID-10/FID-12 translator.py fixes (merged base for this wave)
provides:
  - "visit_Text collapses an intra-paragraph soft/semantic source newline to a single space before escaping (FID-11)"
  - "depart_abbreviation narrows its explanation guard to exclude the auto-generated PEP 3102 '*' / PEP 570 '/' signature separators (FID-14)"
  - "Two new GATE-01 render-gate fixtures + test modules proving both fixes against a real typst.compile()"
affects: [21-residual-fidelity-fixes-clusters-c-d-e-f (phase-gate verification), any future translator.py visit_Text/depart_abbreviation edits]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Collapse-before-escape ordering in visit_Text (guard-then-transform-then-escape) for source whitespace normalization"
    - "Narrow exact-text-equality predicate on node.astext() to distinguish auto-generated PEP-separator abbreviation nodes from genuine :abbr: usages"

key-files:
  created:
    - tests/fixtures/paragraph_soft_newline_render_gate/conf.py
    - tests/fixtures/paragraph_soft_newline_render_gate/index.rst
    - tests/test_paragraph_soft_newline_render_gate.py
    - tests/fixtures/abbr_pep_separator_render_gate/conf.py
    - tests/fixtures/abbr_pep_separator_render_gate/index.rst
    - tests/test_abbr_pep_separator_render_gate.py
  modified:
    - typsphinx/translator.py
    - tests/test_table_in_list_item_render_gate.py

key-decisions:
  - "FID-11 collapse runs in visit_Text strictly before escape_typst_string, per D-Disc-1/Pattern 2 (does not bypass or weaken the existing escaping choke point)"
  - "FID-11 verification is structural-.typ-assert-only (D-08) -- no pypdf, per the non-extractable vertical-layout-property precedent from Phase 19"
  - "FID-14 predicate narrows the existing guard to `if explanation and node.astext() not in (\"*\", \"/\"):` -- exact string equality on the abbreviation node's own text, per D-Disc-3"
  - "Updated a pre-existing test (test_table_in_list_item_render_gate.py) whose assertion embedded a stale '\\n' escape produced by the now-fixed soft-newline bug (Rule 1 auto-fix, unrelated to that test's actual subject)"

patterns-established:
  - "Pattern 2 (RESEARCH.md): collapse soft-wrap newline in visit_Text before escaping, guard set = in_literal_block early return + line_block structural linebreak() + inline raw() never routes through visit_Text"
  - "Pattern 6 (RESEARCH.md): narrow-scope suppression via exact node.astext() equality, verified via direct doctree inspection rather than output-string heuristics"

requirements-completed: [FID-11, FID-14]

coverage:
  - id: D1
    description: "A paragraph authored with reST soft/semantic source line breaks collapses the intra-paragraph newline to a single space instead of a Typst hard break (FID-11)"
    requirement: "FID-11"
    verification:
      - kind: integration
        ref: "tests/test_paragraph_soft_newline_render_gate.py::TestParagraphSoftNewlineRenderGate::test_typstpdf_soft_newline_produces_pdf_with_no_intra_paragraph_break"
        status: pass
    human_judgment: false
  - id: D2
    description: "The FID-11 collapse does not touch in_literal_block text, inline raw()/literal content, or explicit line_block/line hard breaks"
    requirement: "FID-11"
    verification:
      - kind: unit
        ref: "tests/test_line_blocks.py (full module)"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py (full module, 112 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The auto-generated PEP 3102 '*' / PEP 570 '/' signature separators no longer inject their abbr hover-title text inline; a genuine :abbr: role keeps its inline expansion (FID-14)"
    requirement: "FID-14"
    verification:
      - kind: integration
        ref: "tests/test_abbr_pep_separator_render_gate.py::TestAbbrPepSeparatorRenderGate::test_typstpdf_abbr_pep_separator_produces_pdf_with_structural_suppression"
        status: pass
      - kind: integration
        ref: "tests/test_abbr_pep_separator_render_gate.py::TestAbbrPepSeparatorRenderGate::test_pdf_extracted_text_suppresses_pep_separator_titles_only"
        status: pass
    human_judgment: false
  - id: D4
    description: "Regression: existing abbreviation coverage and desc-sig-space fixtures stay green"
    requirement: "FID-14"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTrivialBlocksRenderGate::test_trivial_blocks_pdf_renders_rule_glossary_and_abbr_no_leak"
        status: pass
    human_judgment: false

duration: 21min
completed: 2026-07-20
status: complete
---

# Phase 21 Plan 02: Residual Fidelity Fixes -- FID-11 / FID-14 Summary

**Paragraph soft-newlines now collapse to a single space instead of forcing a Typst hard break (FID-11), and the auto-generated PEP 3102/570 signature separators no longer inject their `<abbr>` hover-title text inline while genuine `:abbr:` roles keep theirs (FID-14) -- both proven by real `typst.compile()` GATE-01 fixtures.**

## Performance

- **Duration:** 21 min
- **Started:** 2026-07-20T13:32:00Z (approx, worktree provisioning)
- **Completed:** 2026-07-20T13:43:33Z
- **Tasks:** 2 completed
- **Files modified:** 8 (1 translator.py, 6 new fixture/test files, 1 pre-existing test updated)

## Accomplishments
- `visit_Text` collapses an intra-paragraph soft/semantic source newline (`\n`) to a single space BEFORE `escape_typst_string`, so a soft-wrapped paragraph reflows naturally instead of forcing a Typst hard break (FID-11)
- `depart_abbreviation`'s explanation-append guard is narrowed to `if explanation and node.astext() not in ("*", "/"):`, suppressing the inline hover-title text ONLY for the auto-generated PEP 3102 `*` / PEP 570 `/` signature separators; a genuine `:abbr:` role's acronym is never bare `*`/`/`, so it keeps its inline expansion unchanged (FID-14)
- Two new GATE-01 fixtures + render-gate test modules, both confirmed to FAIL against the pre-fix translator and PASS post-fix, each producing a valid `%PDF`

## Task Commits

Each task was committed atomically:

1. **Task 1: FID-11 -- collapse intra-paragraph soft newline to a space in visit_Text (reflow) + structural render gate** - `94a0dae` (feat)
2. **Task 2: FID-14 -- narrow-scope abbr-title suppression in depart_abbreviation (PEP separators) + render gate** - `d28e377` (feat)

Deviation commits (Rule 1 auto-fix, both in-scope of this plan's own changes):

3. `a199184` (fix) -- updated a stale embedded-`\n` assertion in a pre-existing render-gate test that this plan's FID-11 fix legitimately changed
4. `0a65c32` (style) -- black-formatted the two new test modules (project CI runs `black --check .`)

**Plan metadata:** (this SUMMARY commit, pending)

## Files Created/Modified
- `typsphinx/translator.py` -- `visit_Text` (FID-11 collapse) and `depart_abbreviation` (FID-14 narrowed guard)
- `tests/fixtures/paragraph_soft_newline_render_gate/conf.py` -- fixture Sphinx config
- `tests/fixtures/paragraph_soft_newline_render_gate/index.rst` -- plain soft-wrapped paragraph + soft break adjacent to an inline literal
- `tests/test_paragraph_soft_newline_render_gate.py` -- Shape-A (structural-only, D-08) GATE-01 module
- `tests/fixtures/abbr_pep_separator_render_gate/conf.py` -- fixture Sphinx config
- `tests/fixtures/abbr_pep_separator_render_gate/index.rst` -- `py:function` signature with both `*`/`/` separators + a genuine `:abbr:` usage
- `tests/test_abbr_pep_separator_render_gate.py` -- Shape-B (structural + pypdf, D-10) GATE-01 module
- `tests/test_table_in_list_item_render_gate.py` -- updated one stale assertion (embedded `\n` -> single space) for FID-11 lockstep

## Decisions Made
- FID-11's collapse is placed strictly BEFORE `escape_typst_string` inside `visit_Text` (not inside the shared escaping helper), per D-Disc-1 -- the helper stays the single choke point literals also route through, unmodified.
- FID-11 verification uses structural `.typ` asserts only (D-08) -- no pypdf, since the hard-break symptom is a non-extractable vertical-layout property (Phase 19 D-06 precedent).
- FID-14's predicate is exact string equality (`node.astext() not in ("*", "/")`) on the doctree node's own text, not a heuristic on rendered/escaped output -- verified via RESEARCH.md's direct doctree inspection.
- The pre-existing `test_table_in_list_item_render_gate.py` assertion that embedded a literal `\n` escape (produced by its own two-line source sentence) was updated to the new, correct single-space form -- its actual subject (table-in-list-item separator behavior) is unrelated to and unaffected by the FID-11 fix.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated stale embedded-newline assertion in a pre-existing render-gate test**
- **Found during:** Task 1 (running the full non-integration test suite after the FID-11 fix)
- **Issue:** `tests/test_table_in_list_item_render_gate.py` asserted a literal `text("...must stay\nbyte-unchanged...")` string, produced incidentally by that fixture's own two-line source sentence. FID-11's collapse-to-space fix correctly changes that embedded `\n` to a single space, which is the intended, correct behavior -- but it made the pre-existing exact-match assertion stale.
- **Fix:** Updated the assertion to the new correct single-space form (`"...must stay byte-unchanged..."`), with a comment noting the lockstep update. The test's actual subject (table nested in a list item newline-separating from its lead-in text) is unaffected.
- **Files modified:** `tests/test_table_in_list_item_render_gate.py`
- **Verification:** `uv run pytest tests/test_table_in_list_item_render_gate.py` passes; full non-integration suite green (455 passed, 1 skipped) after the update.
- **Committed in:** `a199184`

**2. [Rule 3 - Blocking, minor] Applied black formatting to new test modules**
- **Found during:** Post-implementation CI-parity check (`black --check .`)
- **Issue:** The two new render-gate test modules had a couple of lines that did not match `black`'s formatting (per CLAUDE.md, CI runs `black --check .`).
- **Fix:** Ran `black` (without `--check`) on the two files; `black --check .` across the whole repo then passes clean (145 files unchanged).
- **Files modified:** `tests/test_paragraph_soft_newline_render_gate.py`, `tests/test_abbr_pep_separator_render_gate.py`
- **Verification:** `uv run black --check .` passes; both gate modules re-run green post-format.
- **Committed in:** `0a65c32`

---

**Total deviations:** 2 auto-fixed (1 Rule-1 bug fix in an unrelated pre-existing test, 1 minor Rule-3 formatting fix)
**Impact on plan:** Both auto-fixes were necessary for correctness (Rule 1: the old assertion tested stale, pre-fix behavior) and CI-parity (Rule 3: black formatting). No scope creep -- neither touches FID-11/FID-14 behavior itself.

## Issues Encountered
- `ruff check` could not run in this NixOS sandbox worktree ("Could not start dynamically linked executable: ruff") -- this is the documented NixOS-sandbox environmental hazard (project MEMORY.md), not caused by this plan's changes. `mypy typsphinx/` ran clean (no issues in 6 source files) as a substitute static-analysis signal.
- `tests/test_examples_basic.py` (3 tests) fails in this worktree with `uv run sphinx-build` exit code 127 ("command not found") -- confirmed via a stash/pop bisection to be pre-existing and identical both before and after this plan's changes (the file uses the `uv run sphinx-build` subprocess pattern, the same NixOS-sandbox PATH-shadowing hazard CLAUDE.md documents for the 4 excluded integration-test files). Not a regression from this plan.
- The 4 `tests/test_integration_*.py` files were excluded from the local run per the execution-notes NixOS-sandbox guidance (pre-existing environmental failures, not this plan's defect).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- FID-11 and FID-14 are both fixed, gated, and green against the full non-integration/non-`uv-run-sphinx-build` test suite (455 passed, 1 skipped).
- `tests/test_preview_version_sync.py` stays green -- this plan's changes never touched `base.typ` or the `@preview` version-sync surface.
- Phase-gate corpus regression (`uv run pytest tests/test_corpus_gate.py -m slow`) was NOT run by this executor -- it is explicitly described in 21-02-PLAN.md's `<verification>` section as a phase-gate check ("once at end of phase"), owned by the phase verifier/orchestrator after all Phase 21 plans/waves complete.
- No blockers for the remaining Phase 21 plans (FID-10/FID-12/FID-13, if not already covered by wave 1's 21-01).

---
*Phase: 21-residual-fidelity-fixes-clusters-c-d-e-f*
*Completed: 2026-07-20*

## Self-Check: PASSED

All created files confirmed present on disk; all 4 task/deviation commit hashes (`94a0dae`, `d28e377`, `a199184`, `0a65c32`) confirmed present in `git log --oneline --all`.
