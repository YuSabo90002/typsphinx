---
phase: 37-signature-typography-the-desc-family
plan: 06
subsystem: rendering
tags: [typst, translator, desc, signature, typography, monospace, sig-01, sig-02, sig-03, sig-04, sig-07, sig-09]

# Dependency graph
requires:
  - phase: 37-signature-typography-the-desc-family (plan 01, Wave 1)
    provides: "tests/test_signature_typography_gate.py -- the 14-node-id SIG-01..05 structural gate this plan flips (10 of 14; SIG-05's 4 stay RED, owned by 37-07)"
  - phase: 37-signature-typography-the-desc-family (plan 03, Wave 1)
    provides: "tests/test_signature_overflow_render_gate.py and tests/test_signature_page_boundary_render_gate.py -- the SIG-07/SIG-09 geometric gates this plan flips"
  - phase: 37-signature-typography-the-desc-family (plan 04, Wave 2)
    provides: "the migrated tests/test_translator.py assertions and the desc_sig_space/rubric_option hand-off (PyTypeObject discriminator note) this plan flips"
  - phase: 37-signature-typography-the-desc-family (plan 05, Wave 2)
    provides: "depart_desc's SIG-08 emission-position-marker fix -- this plan proves the new block() wrapper does not disturb it"
provides:
  - "typsphinx/translator.py: SHARED_INDENT_STEP module constant (2.5em, D-08) -- Phase 38 IND-04's declared reuse point"
  - "typsphinx/translator.py: TypstTranslator.in_signature_text -- the monospace-propagation flag read by visit_Text, set/cleared in visit_desc_signature/depart_desc_signature"
  - "typsphinx/translator.py: TypstTranslator._param_name_seen -- the D-05 discriminator's per-parameter state, reset in visit_desc_parameter"
  - "typsphinx/translator.py: the composed block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {...})) desc_signature wrapper (SIG-07 + SIG-09, D-10)"
  - "typsphinx/translator.py: visit_Text's in_signature_text branch -- every signature text run emits raw(...) with ZWSP break-opportunity injection (SIG-02, SIG-07/D-07)"
  - "typsphinx/translator.py: _escape_signature_text and _emit_signature_leaf_wrapper -- the shared escape+ZWSP and leaf-emission helpers reused by visit_Text, visit_desc_name, visit_desc_annotation and visit_desc_sig_name"
  - "typsphinx/translator.py: visit_desc_name / visit_desc_annotation's text-only-leaf bold branch (SIG-01, SIG-03)"
  - "typsphinx/translator.py: visit_desc_sig_name's three-rule D-05 discriminator (SIG-01 non-leaf case, SIG-04 italic parameter name, resolved-xref hyperlink preservation)"
affects: ["37-07 (Wave 4, lands SIG-05/SIG-06/D-11 delimiter+arrow work and the golden.typ byte-identity gate on top of this wrapper/monospace foundation)", "37-08 (merges the four sibling 37-GATE-EVIDENCE-*.md files and this plan's own set-difference evidence)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Shared escape+ZWSP helper (_escape_signature_text): one method wrapping escape_typst_string (D-04, reused unmodified) plus the load-bearing escape-then-inject order for the SIG-07 break-opportunity escape -- every signature text-emission site (visit_Text's branch, visit_desc_name/visit_desc_annotation's leaf branch, visit_desc_sig_name's two leaf branches) calls this ONE helper, so the algorithm has exactly one implementation."
    - "Shared leaf-emission helper (_emit_signature_leaf_wrapper): mirrors visit_literal's leaf-emission shape (paragraph separator, concat-or-list-item fallback, the wrapper(raw(...)) call, mark-content-or-list-item fallback, then nodes.SkipNode) parameterized on the wrapper call name (\"strong\" or \"emph\") -- reused by visit_desc_name, visit_desc_annotation, and both firing rules of visit_desc_sig_name's D-05 discriminator."
    - "D-05 discriminator as three mutually exclusive rules evaluated as sequential guarded early-exits (each firing rule calls _emit_signature_leaf_wrapper, which raises nodes.SkipNode, making the remaining checks unreachable for that node) rather than an if/elif chain -- keeps each rule's condition independently readable while the exception guarantees exclusivity."

key-files:
  created: []
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Extracted _escape_signature_text and _emit_signature_leaf_wrapper as shared private helpers rather than duplicating the escape+ZWSP algorithm and the leaf-emission shape across visit_Text, visit_desc_name, visit_desc_annotation and visit_desc_sig_name. This is NOT a second escaping helper (D-04's prohibition) -- both helpers call escape_typst_string unmodified and add no independent escaping logic; they are the single place the CONTRACT-SPECIFIED algorithm (escape, then inject ZWSP; emit wrapper(raw(...)) with the standard separator bookkeeping) lives, exactly as the contract's per-site repetition already specifies identically at every call site."
  - "Split the single continuous implementation session into 3 per-task commits by reconstructing each task's end-state against the original (pre-Phase-37-06) file and replaying the exact edits in task order, since the tasks were originally implemented in one continuous editing pass without intermediate commits. Each reconstructed commit was independently re-verified (task's own automated verify command + full lint/type trio) before committing, and the final reconstructed state was diffed byte-for-byte against the original fully-tested implementation (zero difference) before the Task 3 commit."
  - "Task 3's docstring for visit_desc_sig_name explicitly names addnodes.pending_xref in a comment explaining why it is NOT discriminated on, per the contract's explicit instruction (\"Record this in the code comment, because it is the exact wrong turn CONTEXT.md's own D-05 text invites\"). This is a documentary mention, not discriminating CODE (no isinstance/type check against pending_xref exists) -- read as satisfying the acceptance criterion's intent (no new pending_xref-based dispatch logic) rather than its literal grep-count phrasing, since the two would otherwise directly contradict the contract's own instruction to comment on it."
  - "Did not attempt to fix the discovered tests/test_inline_math_after_text_render_gate.py collateral regression (see Deviations) by either modifying its golden.txt fixtures (outside this plan's `files_modified: typsphinx/translator.py` scope) or altering the locked wrapper text (contract section 3's block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {...})) form is byte-mandated and independently required by the SIG-07/SIG-09 acceptance criteria)."

patterns-established:
  - "Shared signature-typography helper block (typsphinx/translator.py, immediately before visit_Text): _escape_signature_text and _emit_signature_leaf_wrapper are the two reuse points every future desc_sig_* or desc_name-family handler addition in this phase family should call into rather than re-deriving escaping, ZWSP injection, or the leaf-emission separator shape."

requirements-completed: [SIG-01, SIG-02, SIG-03, SIG-04, SIG-07, SIG-09]

# Coverage metadata
coverage:
  - id: D1
    description: "One composed block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {...})) desc_signature wrapper carries both SIG-09's page-keep-together and SIG-07's hanging-indent overflow mechanism, with vertical spacing explicitly zeroed to avoid a SIG-08-shaped doubled-gap regression"
    requirement: "SIG-09"
    verification:
      - kind: integration
        ref: "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_primary_signature_and_body_share_a_page"
        status: pass
      - kind: integration
        ref: "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_page_count_does_not_inflate"
        status: pass
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix"
        status: pass
    human_judgment: false
  - id: D2
    description: "SIG-07's hanging-indent half and the ZWSP break-opportunity injection after every period in a signature text run, both wired through the single visit_Text monospace branch"
    requirement: "SIG-07"
    verification:
      - kind: integration
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_primary_widest_segment_fits_column"
        status: pass
      - kind: integration
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_hanging_indent_present"
        status: pass
      - kind: integration
        ref: "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_break_opportunity_after_every_period"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every signature text-bearing descendant (desc_addname, desc_sig_keyword/space/punctuation/operator, inline.default_value, desc_sig_literal_string/number, desc_sig_keyword_type) gets regular-weight monospace for free via the in_signature_text flag with no dedicated handler -- desc_addname's lack of an enclosing bold call IS SIG-02"
    requirement: "SIG-02"
    verification:
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_and_name_are_two_separate_expressions"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_empty_addname_emits_zero_bytes"
        status: pass
      - kind: integration
        ref: "tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces"
        status: pass
    human_judgment: false
  - id: D4
    description: "desc_name and desc_annotation render byte-identically bold (strong(raw(...))) for text-only leaves, and the C++ non-leaf desc_name case gets bold via its nested desc_sig_name child instead of node.astext() flattening"
    requirement: "SIG-01"
    verification:
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_leaf_desc_name_bold_monospace"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py::test_desc_with_annotation_and_name"
        status: pass
    human_judgment: false
  - id: D5
    description: "The D-05 discriminator: a parameter's own name is italic (emph(raw(...))), its type annotation and default value stay plain monospace, and a resolved cross-reference inside a type annotation keeps its hyperlink (link(...)) rather than being silently flattened"
    requirement: "SIG-04"
    verification:
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_parameter_names_italic_type_and_default_plain"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_resolved_xref_type_annotation_keeps_hyperlink"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_generic_type_and_quoted_forward_ref_are_plain"
        status: pass
    human_judgment: false
  - id: D6
    description: "Non-ASCII signature names and parameter names round-trip their code points unchanged through the new escape+ZWSP path"
    verification:
      - kind: unit
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_encoding_non_ascii_signature_round_trips_code_points"
        status: pass
    human_judgment: false
  - id: D7
    description: "Discovered collateral regression: tests/test_inline_math_after_text_render_gate.py's byte-exact MATH-02 golden invariance test now fails because the mandatory block()-wrapped desc_signature (contract-locked, D-10) changes confval signature-to-content adjacency spacing in one specific fixture arrangement -- confirmed unavoidable given the locked wrapper text, and out of this plan's files_modified scope to fix (would require modifying an out-of-Phase-37 golden fixture)"
    verification: []
    human_judgment: true
    rationale: "Requires an owner/orchestrator decision on whether to regenerate tests/fixtures/inline_math_pdf_text_mitex.golden.txt (and its native counterpart) under a follow-up plan/todo, since fixing it is outside this plan's file scope and the root cause (D-10's locked wrapper) is architecturally mandated, not a bug."

# Metrics
duration: ~55min
completed: 2026-08-01
status: complete
---

# Phase 37 Plan 06: Signature Wrapper, Monospace Propagation, and Per-Sub-Part Typography Summary

**Replaced desc_signature's `strong({...})` wrapper with the one composed `block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {...}))` form (SIG-07 + SIG-09), routed every signature text run through the `raw(...)` monospace primitive with ZWSP break-opportunity injection (SIG-02, SIG-07), and implemented the D-05 discriminator so `desc_name`/`desc_annotation` render bold and each parameter's own name renders italic while a resolved cross-reference keeps its hyperlink (SIG-01, SIG-03, SIG-04).**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-01T (session start, per PLAN_START_TIME)
- **Completed:** 2026-08-01
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 1 (`typsphinx/translator.py`)

## Accomplishments

- Introduced `SHARED_INDENT_STEP = "2.5em"` (D-08) as the phase's only new module-level name, documented as Phase 38 IND-04's declared reuse point; `grep -c "2\.5em"` returns exactly 1.
- Replaced `desc_signature`'s wrapper open/close literals with the composed `block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {` / `}))` form (contract section 3, D-10) -- the ONE wrapper carrying both SIG-09's page-keep-together (`sticky: true`) and SIG-07's overflow mechanism (`hanging-indent`), spacing explicitly zeroed to avoid reintroducing a SIG-08-shaped doubled-gap defect. Everything else in `visit_desc_signature`/`depart_desc_signature` (the paragraph-separator call, the concat-element enter/exit pair, the `in_paragraph`/`in_list_item`/`list_item_needs_separator` save-restore, the `_strong_was_*` attribute names, the FID-03 sibling `linebreak()`, and the `[#metadata(none) <label>]` anchor loop) stays byte-identical.
- Added `self.in_signature_text` (set in `visit_desc_signature`, cleared in `depart_desc_signature` before the anchor loop) and a new `visit_Text` branch that routes every signature text run through `raw(...)` instead of `text(...)`, reusing `escape_typst_string` unmodified and replicating the plain-text path's separator bookkeeping byte-for-byte.
- Added the shared `_escape_signature_text` helper (escape first, then inject the `\u{200B}` break-opportunity escape after every period -- load-bearing order, since escaping doubles backslashes) and `_emit_signature_leaf_wrapper` helper (the `visit_literal`-mirrored leaf-emission shape, parameterized on `strong`/`emph`), reused by every signature leaf-emission site so the escape+ZWSP algorithm and the leaf-emission separator protocol each have exactly one implementation.
- Implemented `visit_desc_name`/`visit_desc_annotation`'s text-only-leaf bold branch (identical treatment, SIG-03) and `visit_desc_sig_name`'s three-rule D-05 discriminator: rule 1 (parent is `desc_annotation`/`desc_name`, leaf) bolds a non-leaf `desc_name`'s nested child (the C++ case); rule 2 (parent is `desc_parameter`, leaf, first) italicizes the parameter's own name; rule 3 (otherwise) is a no-op so a resolved cross-reference's `link(...)` call stays intact with the monospace primitive inside it.
- `visit_desc_parameter` now resets `self._param_name_seen` per parameter (scalar, mirroring the existing `_desc_parameter_has_content` reset idiom); `visit_desc_addname` and the four remaining `desc_sig_*` handlers stay `pass`, each gaining a docstring line explaining the flag already covers them.
- Verified via node-id set difference (not count) that exactly 20 pre-existing RED node ids flip GREEN, the 11 node ids explicitly owned by plan 37-07 (SIG-05 x4, SIG-06/D-11 x4, the `desc_signature_concat` xref-hyperlink pair, the `golden.typ` byte-identity gate) stay RED unchanged, SIG-08's Wave 2 fixes and every named control stay GREEN, and lint/type (`black`/`ruff`/`mypy`) stay clean throughout all three task commits.
- Discovered and documented one collateral regression outside this plan's own scope -- see Deviations.

## Task Commits

Each task was committed atomically (reconstructed against the original file and independently re-verified per commit -- see "Deviations from Plan" for why):

1. **Task 1: Introduce SHARED_INDENT_STEP and swap the desc_signature wrapper** - `550b04a` (feat)
2. **Task 2: Add visit_Text's monospace branch with the zero-width break injection** - `7674e3f` (feat)
3. **Task 3: Implement the per-sub-part bold and italic treatments and the D-05 discriminator** - `f63fe8f` (feat)

**Plan metadata:** commit pending (this SUMMARY + REQUIREMENTS.md, made immediately after this file is written)

_Note: no TDD tasks in this plan -- all three are `type="auto"` structural/behavioral implementation tasks against pre-existing Wave 1/2 gates._

## Files Created/Modified

- `typsphinx/translator.py` - `SHARED_INDENT_STEP` constant; `self.in_signature_text` and `self._param_name_seen` instance state; `visit_desc_signature`/`depart_desc_signature`'s composed wrapper; `visit_Text`'s monospace branch; `_escape_signature_text` and `_emit_signature_leaf_wrapper` shared helpers; `visit_desc_name`/`visit_desc_annotation`'s leaf-bold branch; `visit_desc_sig_name`'s D-05 discriminator; `visit_desc_parameter`'s per-parameter reset; docstring-only updates to `visit_desc_addname` and the four remaining `desc_sig_*` handlers.

## Decisions Made

See `key-decisions` in frontmatter. Summary:
- Extracted two shared private helpers (`_escape_signature_text`, `_emit_signature_leaf_wrapper`) rather than duplicating the contract's own per-site-repeated algorithm four times -- not a "second escaping helper" (D-04's actual prohibition), since both wrap `escape_typst_string` unmodified.
- Reconstructed the single continuous implementation pass into 3 independently-verified, atomically-committed task commits (see Deviations).
- Interpreted the pending_xref grep acceptance criterion as targeting discriminating CODE, not the contract-mandated explanatory comment, since the two literally conflict otherwise.
- Left the discovered MATH-02 golden regression unfixed and thoroughly documented rather than either modifying an out-of-scope fixture or weakening the locked wrapper text.

## Deviations from Plan

### Auto-fixed Issues

None in the Rule 1/2/3 sense -- no bugs, missing critical functionality, or blocking issues were found and silently patched. The two items below are process/scope deviations, documented per this plan's own established precedent (37-04-SUMMARY.md's "report the discrepancy rather than silently reconciling it").

**1. [Process] Reconstructed per-task commits after a continuous implementation pass**

- **Found during:** Task 3, at commit time.
- **Issue:** All three tasks were implemented in one continuous editing session (each task's edits were made via the plan's own instructed order, but no `git commit` was made between tasks). The `task_commit_protocol` requires each task committed individually.
- **Fix:** Restored the original (pre-Phase-37-06) `typsphinx/translator.py` via `git show HEAD:typsphinx/translator.py`, then replayed each task's exact edits in order, independently re-running that task's own automated verify command plus the full `black`/`ruff`/`mypy` trio before each commit. After Task 3's edits were reapplied, the reconstructed file was diffed byte-for-byte (`diff`, exit 0) against the fully-tested final implementation from the original continuous pass, confirming zero divergence before committing.
- **Files modified:** `typsphinx/translator.py` (no additional files; same net diff as the original implementation).
- **Verification:** Each of the 3 commits independently passes its own task's `<verify>` command; final state byte-identical to the pre-reconstruction, fully-suite-tested version (`12 failed, 674 passed, 1 skipped` both before and after reconstruction).
- **Committed in:** `550b04a`, `7674e3f`, `f63fe8f`.

**2. [Discovered, out-of-scope] Collateral regression in `tests/test_inline_math_after_text_render_gate.py`**

- **Found during:** Task 1, at the first full-suite regression check after the wrapper swap (persisted through Tasks 2 and 3 -- root cause is exclusively the Task 1 wrapper change).
- **Issue:** `test_block_math_pdf_text_is_invariant_across_the_math02_fix` (a Phase 34 MATH-02 byte-exact PDF-text invariance gate, unrelated to Phase 37) starts failing. Root cause, confirmed by building the fixture through both the pre-Phase-37 and Phase-37-06 translators and diffing the emitted `.typ` and rendered PDF text: the fixture's `confval:: math_inline_default` directive is preceded directly by a prose paragraph with no blank content, and immediately followed by a "collapsed field body" (`Type: x  Default: y`) with no blank paragraph either. Pre-Phase-37, `desc_signature`'s `strong({...})` wrapper was NOT a Typst block-level element -- Typst's default code-mode joining rules gave the confval signature normal paragraph-flow adjacency to its neighbors. Now that `desc_signature` is wrapped in `block(above: 0pt, below: 0pt, sticky: true, ...)` (the LOCKED, contract-mandated wrapper form, byte-verified against `37-EMISSION-CONTRACT.md` section 3), it becomes a genuine Typst block, and the explicit `above: 0pt`/`below: 0pt` override collapses the vertical spacing that previously came from ordinary paragraph-to-paragraph flow -- eliminating both the visual gap before the signature and the space between the signature and the immediately-following field-body text in the compiled PDF's extracted text.
- **Why not fixed:** The wrapper's exact text (`block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {`/`}))`) is byte-mandated by contract section 3 and independently required by this plan's own SIG-07/SIG-09 acceptance criteria (verified: `test_hanging_indent_present`, `test_primary_signature_and_body_share_a_page`, and the SIG-09 non-inflation guard all require exactly this zeroed-spacing form -- any non-zero spacing reintroduces the SIG-08-shaped doubled-gap defect the contract explicitly warns against). This plan's `files_modified` is exactly `typsphinx/translator.py`; the scope fence explicitly forbids modifying any test file, fixture, or golden file, and `tests/fixtures/inline_math_pdf_text_mitex.golden.txt`/`inline_math_pdf_text_native.golden.txt` are Phase 34 assets, not this phase's own SIG-01..09 gates. Confirmed via full-suite scan that this is the ONLY test affected by this interaction (the two Phase-37-owned confval control gates, `tests/test_confval_field_body_render_gate.py` and `tests/test_confval_field_spacing_render_gate.py`, both stay GREEN -- neither performs a byte-exact whole-document PDF-text comparison, so they are insensitive to this specific adjacency change).
- **Files that would need modification (not done, out of scope):** `tests/fixtures/inline_math_pdf_text_mitex.golden.txt`, `tests/fixtures/inline_math_pdf_text_native.golden.txt` (regeneration under a Phase-34-owning follow-up, after confirming the new signature-on-its-own-line layout is the intended visual outcome).
- **Verification:** Root cause independently reproduced by rebuilding the fixture at both the pre-Phase-37 translator (`git show HEAD:typsphinx/translator.py` temporarily restored, fixture rebuilt, restored back with zero net diff afterward -- confirmed via `diff`, exit 0) and the Phase-37-06 translator, diffing the emitted `.typ` (differs in exactly the one wrapper literal, matching contract section 3 byte-for-byte) and the failing test's own diff output (confirms the exact adjacency loss described above).
- **Committed in:** Not committed -- no code change made. Documented here per this plan's "STOP and report the discrepancy" instruction.

---

**Total deviations:** 1 process reconstruction (no functional impact) + 1 discovered, unfixable-in-scope collateral regression.
**Impact on plan:** The process reconstruction has zero functional impact (byte-identical final state, independently re-verified). The collateral regression is a genuine, unavoidable consequence of implementing the plan's own locked, contract-mandated wrapper design correctly -- not a defect in this plan's implementation, but a Phase-34 test asset now requiring a decision (regenerate vs. accept) outside this plan's authority.

## Set-Difference Verification

### Baseline (measured at session start, matching wave_state)

```
uv run pytest -q --tb=no -rf
31 failed, 655 passed, 1 skipped
```

### After this plan (all 3 tasks committed)

```
uv run pytest -q --tb=no -rf
12 failed, 674 passed, 1 skipped
```

### By node-id set difference (never by count)

**Flipped RED -> GREEN by this plan (20 node ids), independently re-verified as a batch:**

```
tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces
tests/test_rubric_option_concat_render_gate.py::TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_primary_widest_segment_fits_column
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_hanging_indent_present
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_break_opportunity_after_every_period
tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_primary_signature_and_body_share_a_page
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_leaf_desc_name_bold_monospace
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_and_name_are_two_separate_expressions
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_empty_addname_emits_zero_bytes
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_parameter_names_italic_type_and_default_plain
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_resolved_xref_type_annotation_keeps_hyperlink
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_generic_type_and_quoted_forward_ref_are_plain
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_encoding_non_ascii_signature_round_trips_code_points
tests/test_translator.py::test_desc_signature_rendering
tests/test_translator.py::test_desc_with_annotation_and_name
tests/test_translator.py::test_desc_parameterlist
tests/test_translator.py::test_full_api_description_structure
```

**Discrepancy note on the count:** The orchestrator's wave-state message described this as "22 node ids", and its own itemized lists (14 typography + 4 geometric + 4 translator + 2 hand-off = 24) sum inconsistently with that stated total; its typography-gate list of "14" also included the 4 `test_sig05_*` node ids. Cross-checked against the authoritative source -- `37-06-PLAN.md`'s own frontmatter (`requirements: [SIG-01, SIG-02, SIG-03, SIG-04, SIG-07, SIG-09]`, no SIG-05/SIG-06), Task 3's action text ("Implement contract §5, and nothing beyond it"), and Task 3's own acceptance criterion ("differs from the Wave 2 baseline by exactly the SIG-01/02/03/04/07/09 node ids flipping red-to-green") -- SIG-05 is unambiguously NOT this plan's scope (delimiters/`desc_optional` comma logic, contract section 6, untouched). This plan flips exactly 20 node ids, matching its own PLAN.md's scope precisely; the 4 `test_sig05_*` ids remain RED, correctly owned by plan 37-07. Reported per this plan's own "STOP and report the discrepancy" precedent (established in `37-04-SUMMARY.md`) rather than silently forcing either number to match.

**Still RED, correctly owned by plan 37-07 (11 node ids):**

```
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden
tests/test_desc_signature_concat_render_gate.py::TestDescSignatureConcatRenderGate::test_typstpdf_signature_reference_first_param_produces_pdf
tests/test_desc_signature_concat_render_gate.py::TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf
tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline
tests/test_signature_break_and_arrow_gate.py::TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_separator_lands_inside_the_bracket
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_target_rendering_present_defective_rendering_absent
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_delimiters_use_monospace_primitive
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_empty_parameter_list_no_comma_separator
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_optional_group_separator_lands_inside_bracket
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_nested_optional_groups_close_in_reverse_open_order
```

**New failure, not in baseline (1 node id) -- the collateral regression, see Deviations item 2:**

```
tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix
```

**Arithmetic:** 31 (baseline) - 20 (flipped) + 1 (new) = 12 (current). Matches the measured `12 failed, 674 passed, 1 skipped` exactly.

### SIG-08 and named controls re-verified GREEN

```
uv run pytest tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate -v
```
- `test_sig08_exact_break_count_after_fix` -- PASSED (unchanged from Wave 2)
- `test_sig08_no_adjacent_break_statements_anywhere` -- PASSED (unchanged from Wave 2)
- `test_sig08_content_follows_nested_member_stays_separated` -- PASSED (control)
- `test_sig08_sibling_bodyless_control_keeps_one_break` -- PASSED (control)

`tests/test_desc_bodyless_concat_render_gate.py` (FID-06 control) and the 3 `tests/test_translator.py::test_desc_signature_line_*` node ids: all PASSED, unchanged.

Geometric controls (`tests/test_signature_overflow_render_gate.py::test_control_widest_segment_fits_column_before_and_after`, `test_column_width_sanity`, `test_fixture_identifier_is_synthetic_and_over_length`; `tests/test_signature_page_boundary_render_gate.py::test_two_page_precondition_guard`, `test_page_count_does_not_inflate`): all PASSED, unchanged.

### Lint/type trio (verified after every one of the 3 task commits)

```
uv run black --check .   -> All done! 183 files would be left unchanged.
uv run ruff check .      -> All checks passed!
uv run mypy typsphinx/   -> Success: no issues found in 6 source files
```

## Known Stubs

None -- this plan implements complete, correct behavior for every code path it touches; no placeholder or empty-value stub was introduced.

## Threat Flags

None -- every new emission site (visit_Text's branch, `_emit_signature_leaf_wrapper`, `visit_desc_sig_name`'s discriminator) reuses `escape_typst_string` unmodified per T-37-01's mitigation, the ZWSP injection happens strictly after escaping so it cannot re-open an escaped sequence, and the discriminator's rule 3 leaves non-leaf nodes structural so the unmodified `visit_reference` keeps emitting hyperlinks (T-37-07's mitigation) -- both threat register entries this plan's `<threat_model>` names are addressed exactly as specified, and no new network/file/subprocess/dependency surface was introduced.

## Issues Encountered

- **NixOS sandbox `uv`/`ruff` ELF incompatibility:** the worktree's `uv sync --extra dev` installed generic-linux ELF `uv`/`ruff` binaries incompatible with the NixOS sandbox's dynamic linker. Resolved per the documented pattern (`CLAUDE.md` / prior plans' precedent): symlinked the main checkout's already-patched `uv` (from `command -v uv`, a Nix-store path) and `ruff` (from `/home/yuta/Documents/typsphinx/.venv/bin/ruff`) into the worktree's `.venv/bin/`. No project file changed; pure environment setup.
- **Worktree-safety-checker false positives on compound Bash commands:** several multi-command Bash invocations (branch-check assertions, `ln -sf`) were rejected by the sandbox's command-complexity heuristic even though they stayed entirely within the worktree. Resolved by splitting into single, simple commands per invocation -- no functional impact, pure command-shape adjustment.
- **Discovered collateral regression:** see Deviations item 2. Investigated to root cause, confirmed unavoidable given the locked wrapper design, and documented rather than silently absorbed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 37-07 (Wave 4) can proceed: the wrapper is the final, locked D-10 form; every text-bearing signature descendant already routes through the monospace primitive; the D-05 discriminator is implemented and correctly handles both the intersphinx-resolved and unresolved-C-domain-type mirror-image cases. 37-07 needs only to implement contract section 6 (delimiter `raw(...)` swap, D-11's dropped-comma fix) and section 7 (the SIG-06 arrow glyph), then migrate `golden.typ` and the `desc_signature_concat`/`pdf_render_gate` assertions on top of this now-stable foundation.
- **Blocker/decision needed (not blocking 37-07's own work, but should be triaged before phase close):** `tests/test_inline_math_after_text_render_gate.py::test_block_math_pdf_text_is_invariant_across_the_math02_fix` fails due to the collateral regression documented above. Recommend either (a) a small follow-up plan/todo to regenerate `tests/fixtures/inline_math_pdf_text_mitex.golden.txt` and `inline_math_pdf_text_native.golden.txt` against the Phase-37-06-and-later translator once the phase's final signature rendering is locked (37-08), confirming the new signature-on-its-own-line layout visually, or (b) an explicit owner decision to accept the new layout as a documented, intentional Phase 37 side effect and update the test's own docstring/invariance claim accordingly. Either resolution belongs to whichever plan/step ships next against `tests/fixtures/inline_math_after_text_render_gate/`, not to 37-07's own SIG-05/SIG-06/D-11 scope.
- No other blockers. The 11 remaining REDs are explicitly enumerated above and match 37-07's declared scope exactly.

## Self-Check: PASSED

- `typsphinx/translator.py` - FOUND, contains `SHARED_INDENT_STEP`, `in_signature_text`, `_param_name_seen`, `_escape_signature_text`, `_emit_signature_leaf_wrapper`
- Commit `550b04a` (Task 1) - FOUND in `git log`
- Commit `7674e3f` (Task 2) - FOUND in `git log`
- Commit `f63fe8f` (Task 3) - FOUND in `git log`
- `.planning/phases/37-signature-typography-the-desc-family/37-06-SUMMARY.md` - FOUND (this file)

---
*Phase: 37-signature-typography-the-desc-family*
*Completed: 2026-08-01*
