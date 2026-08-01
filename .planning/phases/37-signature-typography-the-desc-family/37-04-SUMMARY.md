---
phase: 37-signature-typography-the-desc-family
plan: 04
subsystem: testing
tags: [pytest, sphinx, typst, desc_signature, test-migration, gate-01, red-window]

requires:
  - phase: 37-signature-typography-the-desc-family (37-01..03)
    provides: 37-EMISSION-CONTRACT.md (the byte-level spec every replacement string is hand-derived from), 37-CONTEXT.md D-14 (the golden.typ migration constraint)
provides:
  - "10 pre-existing test node ids migrated to their final Phase 37 shapes, recorded RED against the untouched translator"
  - "tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ hand-derived to its Phase 37 signature shapes (9-line diff)"
  - "37-TEST-CENSUS.md: a three-bucket, re-measured blast-radius census with per-row contract sections and owning plans"
  - "37-GATE-EVIDENCE-04.md: token-by-token derivations, verbatim RED output, and a RED-versus-STAYS-GREEN table by node id"
affects: [37-05, 37-06, 37-07, 37-08]

tech-stack:
  added: []
  patterns: ["hand-derive expected strings from a written contract before the implementing code exists, never from running new code"]

key-files:
  created:
    - .planning/phases/37-signature-typography-the-desc-family/37-TEST-CENSUS.md
    - .planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-04.md
  modified:
    - tests/test_translator.py
    - tests/test_desc_signature_concat_render_gate.py
    - tests/test_rubric_option_concat_render_gate.py
    - tests/test_desc_sig_space_render_gate.py
    - tests/test_pdf_render_gate.py
    - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ

key-decisions:
  - "Migrated a TENTH assertion (TestDescSignatureConcatRenderGate in tests/test_desc_signature_concat_render_gate.py) beyond contract section 11's nine -- found by reading the whole file rather than only the two cited line numbers; its text(\"(\") + link( assertion also depends on the section 6 delimiter change."
  - "golden.typ's diff is 9 lines changed, not the plan's stated 7 -- reported as a discrepancy per Task 3's own instruction rather than silently forced to 7 by dropping a real signature-byte change; the plan's own block-by-block description (2+6+1=9) already implies 9, and contract section 9 independently confirms 9."
  - "tests/test_desc_sig_space_render_gate.py's FID-08 parameter-concat assertion italicises PyTypeObject (the type), not type (the name) -- measured: this fixture has no intersphinx, so the type never resolves to a reference and stays a bare desc_sig_name direct child of desc_parameter, making it (not the name) the first such child under contract section 5.2 rule 2. Mirror image of the intersphinx-resolved MyType *obj case."
  - "Added a defensive U+200B strip to tests/test_desc_sig_space_render_gate.py's PDF-extraction leg (a no-op today) ahead of Wave 3, per contract section 4.2's binding \"every compiled-PDF text assertion in this phase\" requirement."

requirements-completed: [SIG-01, SIG-02, SIG-03, SIG-04, SIG-05, SIG-06]

coverage:
  - id: D1
    description: "Re-measured SC#5 test census: three buckets (will-break / stays-green / conditional) with per-row contract sections and owning plan numbers, extending contract section 11 by one row found through reading"
    requirement: "SIG-01"
    verification:
      - kind: other
        ref: "test -s 37-TEST-CENSUS.md && grep -qi 'must not touch' 37-TEST-CENSUS.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "Nine pre-existing exact-string test assertions migrated to Phase 37 shapes, hand-derived from the emission contract, all RED against the untouched translator"
    requirement: "SIG-01"
    verification:
      - kind: unit
        ref: "tests/test_translator.py::test_desc_signature_rendering, test_desc_with_annotation_and_name, test_desc_parameterlist, test_full_api_description_structure -- FAILED (RED)"
        status: pass
      - kind: integration
        ref: "tests/test_desc_signature_concat_render_gate.py::TestDescSignatureConcatRenderGate::test_typstpdf_signature_reference_first_param_produces_pdf, TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf -- FAILED (RED)"
        status: pass
      - kind: integration
        ref: "tests/test_rubric_option_concat_render_gate.py::TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf -- FAILED (RED); Structure Options/Trailing Heading lookups confirmed still findable against untouched translator"
        status: pass
      - kind: integration
        ref: "tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces -- FAILED (RED); test_pdf_extracted_text_has_no_merged_tokens stays green"
        status: pass
    human_judgment: false
  - id: D3
    description: "golden.typ's five desc_signature-driven blocks hand-derived to Phase 37 shapes; byte-identity gate goes RED, delegation and compile-sanity controls stay green, no line outside the five blocks changed, no ZWSP anywhere"
    requirement: "SIG-03"
    verification:
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden -- FAILED (RED); test_desc_signature_and_rubric_do_not_delegate_to_visit_strong and test_decoupling_fixture_still_compiles_to_pdf -- PASSED"
        status: pass
      - kind: other
        ref: "git diff --numstat tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ -- 9/9 (see key-decisions for the 7-vs-9 discrepancy)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Return-arrow PDF assertion migrated to the U+2192 glyph with a U+200B strip; slow-marked, run explicitly"
    requirement: "SIG-06"
    verification:
      - kind: e2e
        ref: "tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline -- FAILED (RED)"
        status: pass
    human_judgment: false
  - id: D5
    description: "No collateral damage: full -m 'not slow' suite shows exactly the 9 expected non-slow failures and 616 passing, zero changes under typsphinx/, black/ruff/mypy all green"
    verification:
      - kind: other
        ref: "uv run pytest -m 'not slow' -- 9 failed, 616 passed, 29 deselected"
        status: pass
      - kind: other
        ref: "uv run black --check . && .venv/bin/ruff check . && uv run mypy typsphinx/"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-01
status: complete
---

# Phase 37 Plan 04: Deliberate RED Window — Test Migration + golden.typ Hand-Derivation Summary

**Migrated 10 pre-existing exact-string test assertions and hand-derived golden.typ's 5 signature blocks to their final Phase 37 shapes from 37-EMISSION-CONTRACT.md, all recorded RED against the untouched translator (Waves 2-4 flip them green by set difference, never by count).**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-01
- **Tasks:** 3
- **Files modified:** 8 (5 test modules + 1 fixture + 2 new `.planning/` docs)

## Accomplishments

- Re-measured `37-TEST-CENSUS.md`: 3 buckets (will-break / stays-green / conditional), extending `37-EMISSION-CONTRACT.md` section 11's list by one row (`TestDescSignatureConcatRenderGate`, found by reading the whole file), with the required grep-vs-read disagreement example and both rubric assertions explicitly protected by name.
- Migrated 10 pre-existing exact-string assertions across 5 test modules (`test_translator.py` x4, `test_desc_signature_concat_render_gate.py` x2, `test_rubric_option_concat_render_gate.py` x1, `test_desc_sig_space_render_gate.py` x1, `test_pdf_render_gate.py` x1) to their Phase 37 shapes, hand-derived from `37-EMISSION-CONTRACT.md` sections 3-7. All 10 now RED against the untouched translator (9 in the default `-m "not slow"` run; the PDF arrow assertion is `@pytest.mark.slow`).
- Hand-derived `golden.typ`'s five `desc_signature`-driven blocks (`connect`, three `compile` overloads, `--sep`) token-by-token from `37-EMISSION-CONTRACT.md` section 9. Every other line — the three rubric lines, the plain-bold control, the `list({...})` structure, every paragraph/anchor/`linebreak()`/`parbreak()`, and the whole preamble — stays byte-identical, proving the diff itself is signature-only. No ZWSP escape appears anywhere (correctly, per the contract: none of these five signatures has a period inside a signature text run).
- Left the two rubric assertions (`Structure Options`, `Trailing Heading` in `test_rubric_option_concat_render_gate.py`) and `test_translator.py::test_rubric_rendering` byte-identical and confirmed still green — Phase 39 territory, per Phase 36's decoupling.
- Created `37-GATE-EVIDENCE-04.md`: the token-by-token derivation of all 9 changed `golden.typ` lines (correcting the plan's own line-count claim), the discovered section-5.2 measurement discrepancy for unresolved C-domain type parameters, verbatim RED output for all 10 node ids, the rubric-lookup control check, and a RED-versus-STAYS-GREEN table by node id for Waves 2-4 to verify against by set difference.
- Confirmed zero collateral damage: `-m "not slow"` shows exactly the 9 expected non-slow failures against 616 passing tests; zero changes under `typsphinx/`; `black`/`ruff`/`mypy` all green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-measure the blast radius and write the SC#5 census** - `731228e` (docs)
2. **Task 2: Migrate the five test modules' exact-string assertions** - `fbe805a` (test)
3. **Task 3: Hand-derive golden.typ's seven [actually nine] signature lines and record the RED set** - `fd16d73` (test)

_Note: no `feat`/`refactor` commits — this plan is test-and-docs-only per its own `<files_modified>` list; `typsphinx/` is untouched._

## Files Created/Modified

- `.planning/phases/37-signature-typography-the-desc-family/37-TEST-CENSUS.md` - re-measured three-bucket SC#5 census
- `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-04.md` - token-by-token derivations, verbatim RED evidence, RED-vs-GREEN table by node id
- `tests/test_translator.py` - migrated 4 `desc_*` synthetic-doctree assertions to their `raw()`/`strong(raw())` shapes
- `tests/test_desc_signature_concat_render_gate.py` - migrated both classes' assertions (the second is a Rule-2 scope extension beyond the plan's cited lines)
- `tests/test_rubric_option_concat_render_gate.py` - migrated only the `--sep` lookup; added Phase-39-territory comments at both untouched rubric lookups
- `tests/test_desc_sig_space_render_gate.py` - migrated FID-07/FID-08 spacing assertions; added a defensive U+200B strip
- `tests/test_pdf_render_gate.py` - migrated the return-arrow assertion to the U+2192 glyph; added a defensive U+200B strip
- `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` - hand-derived the 5 signature blocks (9-line diff)

## Decisions Made

- **golden.typ 7-vs-9 line-count discrepancy.** The plan's objective, Task 3's action text, and its automated verify command (`test ... = "7/7"`) all state "seven" changed lines. Counting the plan's own enumerated blocks (one 2-line `connect` block + three 2-line `compile` blocks + one 1-line `--sep` block = 2+6+1) already gives 9, and `37-EMISSION-CONTRACT.md` section 9's worked derivation independently confirms 9. Per Task 3's own instruction ("STOP and report the discrepancy... rather than silently adopting either"), derived correctly (9 lines) rather than forcing 7 by dropping a real signature change. **The plan's own automated `7/7` verify command will report `9/9` and fail as written** — this is the expected, documented outcome, not an execution defect. Full reasoning in `37-GATE-EVIDENCE-04.md` section 1.
- **Extended the migration to a tenth assertion not named by contract section 11.** `tests/test_desc_signature_concat_render_gate.py`'s `TestDescSignatureConcatRenderGate` class (a C-domain fixture with a cross-referenced leading parameter type) also asserts `text("(") + link(`, which breaks once section 6's opening-paren delimiter changes to `raw("(")`. Contract section 11 only cited this file's OTHER class (lines 269, 282). Found by reading the whole file per the census's own methodology; migrated as a Rule 2 deviation (the plan's `must_haves.truths` requires migrating EVERY invalidated assertion, not only the ones section 11 happened to name).
- **Measured, not assumed, the desc_sig_space fixture's italic target.** `tests/test_desc_sig_space_render_gate.py`'s C signature (`PyTypeObject *type`) has no intersphinx inventory, so `PyTypeObject` never resolves to a reference and stays a bare `desc_sig_name` direct child of its `desc_parameter` — making it, not `type`, the first such child under contract section 5.2 rule 2. The migrated assertion therefore italicises `PyTypeObject` (the type), not `type` (the name) — mechanically correct per the contract, even though it reads as backwards from the design's intent. Flagged in `37-GATE-EVIDENCE-04.md` section 2 for the 37-06 implementer.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Migrated a tenth breaking assertion not named by contract section 11**
- **Found during:** Task 2 (test module migration)
- **Issue:** `tests/test_desc_signature_concat_render_gate.py::TestDescSignatureConcatRenderGate::test_typstpdf_signature_reference_first_param_produces_pdf` asserts `'text("(") + link(' in ln` and `'text(")")' in param_line` — both break once section 6's parenthesis delimiters change to `raw(...)`, but contract section 11's blast-radius table only cited this file's other class (lines 269, 282). The plan's own `must_haves.truths` requires every invalidated assertion to be migrated in this plan; leaving this one unmigrated would violate that.
- **Fix:** Migrated `'text("(") + link('` -> `'raw("(") + link('` and `'text(")")'` -> `'raw(")")'`, with a comment explaining the finding. Confirmed RED (verified via real Sphinx doctree dump that the type reference is wrapped in `reference`, not a direct `desc_parameter` child, so rule 3 — not rule 2 — governs it).
- **Files modified:** `tests/test_desc_signature_concat_render_gate.py`
- **Verification:** `uv run pytest tests/test_desc_signature_concat_render_gate.py -v` — both classes FAILED (RED)
- **Committed in:** `fbe805a` (Task 2 commit)

**2. [Rule 2 - Missing Critical] Added defensive U+200B strips to two PDF-extraction assertions not explicitly named by Task 2**
- **Found during:** Task 2 (test module migration)
- **Issue:** Contract section 4.2 is a binding, phase-wide requirement ("every compiled-PDF text assertion in this phase must normalise by stripping U+200B before comparing"). Task 2's action text names the strip explicitly only for `test_pdf_render_gate.py`'s arrow test, but `test_desc_sig_space_render_gate.py::test_pdf_extracted_text_has_no_merged_tokens` is also a compiled-PDF text assertion in a Phase-37-scoped file, over a fixture with a dotted `desc_addname` (`sphinx.builders.html.`).
- **Fix:** Added `full_text = full_text.replace("\u200b", "")` to both functions before any comparison. Currently a no-op (no ZWSP exists pre-Phase-37) — added defensively so these tests do not flake once 37-06/37-07 land.
- **Files modified:** `tests/test_desc_sig_space_render_gate.py`, `tests/test_pdf_render_gate.py`
- **Verification:** Re-ran both files after the change; RED/GREEN state unchanged from before the addition (no-op today, confirmed by rerun).
- **Committed in:** `fbe805a` (Task 2 commit)

**3. [Rule 1 - Bug] Corrected golden.typ's derivation to 9 changed lines instead of the plan's stated 7**
- **Found during:** Task 3 (golden.typ hand-derivation)
- **Issue:** The plan's objective, Task 3's action text, and its automated verify command all claim "seven" signature lines change. The plan's own block-by-block enumeration (2+6+1=9) and `37-EMISSION-CONTRACT.md` section 9's worked derivation both independently produce 9, not 7.
- **Fix:** Derived golden.typ's five signature blocks exactly per contract section 9 (9 lines changed), rather than dropping a real change to force a "7" line count. Documented the discrepancy in detail in `37-GATE-EVIDENCE-04.md` section 1 and here, per Task 3's own "STOP and report" instruction.
- **Files modified:** `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`, `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-04.md`
- **Verification:** `git diff tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` shows no change to any rubric/list/anchor/linebreak/parbreak/preamble line — only the five signature blocks changed. `test_emitted_typ_is_byte_identical_to_golden` FAILED (RED); `test_desc_signature_and_rubric_do_not_delegate_to_visit_strong` and `test_decoupling_fixture_still_compiles_to_pdf` stayed PASSED.
- **Committed in:** `fd16d73` (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (2 missing-critical, 1 bug/arithmetic-correction).
**Impact on plan:** All three widen the plan's own RED-window coverage to match its stated invariants (every invalidated assertion migrated once, in this plan, hand-derived from the contract) rather than narrowing it. No scope creep into `typsphinx/` or into new coverage — this plan changes expectations only, exactly as instructed.

## Issues Encountered

None beyond the deviations above (all resolved inline; no blockers carried forward).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Wave 2 (37-05, SIG-08):** Free to land `depart_desc`'s marker fix. None of this plan's 10 migrated assertions concern the doubled-`parbreak()` defect; `tests/test_desc_bodyless_concat_render_gate.py` and the three `test_desc_signature_line_*_linebreak` functions were left untouched and are recorded in `37-TEST-CENSUS.md`'s conditional bucket for re-verification after 37-05 lands.
- **Wave 3 (37-06, the wrapper + monospace propagation):** Flips 6 of this plan's 10 node ids green (the four `test_translator.py` functions, the `--sep` rubric-adjacent lookup, the `test_desc_sig_space_render_gate.py` FID-07/08 assertion). **Heads-up recorded in `37-GATE-EVIDENCE-04.md` section 2:** the desc_sig_space fixture's unresolved C-domain type parameter is a genuine edge case where section 5.2 rule 2 italicises the TYPE rather than the NAME — this is contract-correct, not a bug to "fix" during implementation.
- **Wave 4 (37-07, delimiters + return arrow):** Flips the remaining 4 node ids green (both `test_desc_signature_concat_render_gate.py` classes, the PDF arrow assertion, and `golden.typ`'s byte-identity gate). `37-GATE-EVIDENCE-04.md`'s RED-versus-STAYS-GREEN table is the set-difference reference.
- **Wave 5 (37-08, close-out):** `37-TEST-CENSUS.md` is ready to be finalised/consolidated; the golden.typ 7-vs-9 discrepancy should be reconciled in the phase-level roll-up (the plan's frontmatter/ROADMAP language should be corrected to "9 lines" or the discrepancy explicitly carried forward, not silently dropped).
- No blockers. `typsphinx/` remains completely untouched by this plan, confirming the deliberate RED window's scope fence held.

---
*Phase: 37-signature-typography-the-desc-family*
*Completed: 2026-08-01*
