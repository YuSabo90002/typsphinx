---
phase: 38-structural-indentation-info-fields
plan: 07
subsystem: api
tags: [sphinx, typst, translator, docutils, field-list, monospace, typography]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields (38-02, 38-04, 38-06)
    provides: the RED gate module and FLD-03 test evidence (38-02), the
      authoritative test census identifying row A2's delegation-guard
      inversion (38-04), and the field-list wrapper + field-body reflow
      this plan's leaves render inside (38-06)
provides:
  - "visit_literal_strong/visit_literal_emphasis emit strong(raw(...))/emph(raw(...)) -- bold/italic MONOSPACE -- via a new shared private helper (_emit_field_body_monospace_leaf), replacing the last two dummy-node delegations to visit_strong/visit_emphasis in the translator (FLD-03, D-05, D-09)"
  - "38-TEST-CENSUS.md row A2's SC#1 delegation-guard inversion is migrated: NO_LONGER_DELEGATING_METHODS (renamed from RETAINED_DELEGATION_METHODS) now asserts zero delegating calls, and the dummy-node construction count inverts from == 2 to == 0"
affects: [38-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A field-body monospace leaf (literal_strong/literal_emphasis) shares one new private helper mirroring visit_literal's own leaf-emission idiom exactly (paragraph separator, concat-separator fallback, escaped emission, mark-content fallback, SkipNode) rather than being verbatim-copied twice (D-12 executor discretion, opposite choice from Phase 36's deliberate triplication, justified because the two bodies differ only in the wrapper call name)"
    - "Escaping for a new emission site routes through escape_typst_string ALONE, never through Phase 37's _emit_signature_leaf_wrapper/_escape_signature_text, which unconditionally inject the SIG-07 zero-width-space break opportunity -- an OUTPUT-side no-ZWSP-anywhere assertion is the check that cannot be defeated by renaming a helper"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/test_field_body_typography_render_gate.py
    - tests/test_desc_rubric_decoupling_render_gate.py

key-decisions:
  - "The two new leaf bodies share a private helper, _emit_field_body_monospace_leaf(node, wrapper), rather than being verbatim copies (D-12) -- the bodies are byte-identical except the wrapper call name (\"strong\" vs \"emph\"), so a shared helper removes duplication with zero behavioral cost; Phase 36's deliberate triplication precedent (D-01/D-09) permits either choice."
  - "The typeless-param FLD-03 test's region was narrowed to start at the field list's own label rather than the section heading (Rule 1 bug fix, not a scope-authorized census row) -- the fixture's desc_signature for field_name_without_type(untyped) shares the literal string \"untyped\" with the field-body parameter it documents, and Phase 37's SIG-04 rule (37-EMISSION-CONTRACT.md section 5.2 rule 2) unconditionally italicises a signature's bare parameter name regardless of type annotation, an orthogonal mechanism this plan does not touch. Including the signature block in the region made the \"zero italic-monospace calls\" assertion trip on that unrelated emph(raw(\"untyped\")), not on anything literal_emphasis emits."
  - "38-TEST-CENSUS.md row A2's SC#1 delegation guard is migrated in tests/test_desc_rubric_decoupling_render_gate.py, not tests/test_translator.py or tests/test_pdf_render_gate.py as this plan's own files_modified frontmatter lists -- neither of those two files contains any literal_strong/literal_emphasis assertion (confirmed by grep before editing); the census's own authority (row A2) and the orchestrator's wave-3 findings assign the actual delegation-guard file to this plan."

requirements-completed: [FLD-03]

coverage:
  - id: D1
    description: "literal_strong emits strong(raw(\"<escaped>\")) -- bold monospace, distinct from the plain-bold proportional field label -- for a field-body parameter name (FLD-03, D-05, contract section 5.2 row 1)"
    requirement: "FLD-03"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_nonascii_param_name_roundtrips_codepoints"
        status: pass
    human_judgment: false
  - id: D2
    description: "literal_emphasis emits emph(raw(\"<escaped>\")) -- italic monospace -- for a field-body parameter type, composing correctly nested inside an emitted link(...) call for a resolvable cross-reference with the link's label argument unchanged (FLD-03, D-05, T-38-06, contract section 5.2 row 2 / section 5.4)"
    requirement: "FLD-03"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_resolvable_type_composes_inside_link_unchanged_label"
        status: pass
    human_judgment: false
  - id: D3
    description: "No zero-width space (literal U+200B or its Typst escape) appears anywhere in a field body's emitted bytes -- proves the wrong (Phase 37 signature) escape helper was not reused (T-38-05, contract section 5.3)"
    requirement: "FLD-03"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_no_zero_width_space_anywhere_in_field_bodies"
        status: pass
    human_judgment: false
  - id: D4
    description: "The field label stays unchanged, proportional-bold, and byte-distinct in wrapper shape from both the name and type calls; a typeless :param: entry emits exactly one bold-monospace call and zero italic-monospace calls (D-06 per-sub-part discipline)"
    requirement: "FLD-03"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_field_label_unchanged_and_distinct_from_name_and_type"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono"
        status: pass
    human_judgment: false
  - id: D5
    description: "The last two dummy-node delegation sites in the translator are removed; SC#1's over-reach guard (38-TEST-CENSUS.md row A2) is migrated to assert the inverted post-D-09 state"
    verification:
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong"
        status: pass
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden"
        status: pass
    human_judgment: false

# Metrics
duration: ~40min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 07: literal_strong/literal_emphasis Monospace Leaves Summary

**FLD-03 lands: a field-body parameter name now renders bold monospace and its type italic monospace (both distinct from the plain-bold proportional field label), and the translator's last two dummy-node delegation sites are gone, replaced by a shared private leaf-emission helper routed exclusively through the shared string-escaping helper (never the signature family's zero-width-space-injecting one).**

## Performance

- **Duration:** ~40 min
- **Tasks:** 2 planned tasks + 1 auto-fixed deviation, each committed atomically
- **Files modified:** 3 (`typsphinx/translator.py`, `tests/test_field_body_typography_render_gate.py`, `tests/test_desc_rubric_decoupling_render_gate.py`)

## Accomplishments

- `visit_literal_strong` and `visit_literal_emphasis` no longer construct a throwaway `nodes.strong()`/`nodes.emphasis()` and delegate to `visit_strong`/`visit_emphasis` — the last two dummy-node delegation sites in the translator (D-09). Both now call a new private helper, `_emit_field_body_monospace_leaf(node, wrapper)`, mirroring `visit_literal`'s leaf-emission idiom exactly: `_add_paragraph_separator()`, the `_emit_inline_concat_separator()` fallback (with its list-item newline), the escaped `wrapper(raw("..."))` emission with the markup-mode `#` prefix, the `_mark_inline_concat_content()` fallback, then `raise nodes.SkipNode`.
- `literal_strong` (a parameter's name) emits `strong(raw("<escaped>"))` — bold monospace. `literal_emphasis` (a parameter's type) emits `emph(raw("<escaped>"))` — italic monospace. Both are distinct from the field label's unchanged `strong(text("Parameters") + text(": "))` (plain-bold proportional), landing FLD-03's mechanical demand under D-05's chosen recipe (variant "A": name bold-mono, type italic-mono — deliberately different from the signature family's own name-italic-mono/type-regular-mono recipe).
- Escaping routes through `escape_typst_string` alone — the same shared helper `visit_literal`'s leaf branch already uses — never through Phase 37's `_emit_signature_leaf_wrapper`/`_escape_signature_text`, which unconditionally inject the SIG-07 zero-width-space break opportunity after every `.`. Verified as an OUTPUT property: no zero-width space (neither the literal U+200B byte nor its 8-character Typst escape) appears anywhere in a field body's emitted bytes.
- No special-casing on the visited node's parent: a resolvable `:type:` cross-reference's `literal_emphasis` composes correctly nested inside the emitted `link(...)` call, because `link()`'s body argument is just a content value — the same reason the signature family's own resolved-xref rule already works.
- `depart_literal_strong`/`depart_literal_emphasis` remain in place as documented-unreachable stubs (the visit handlers now raise `SkipNode`), mirroring `depart_literal`'s own unreachable stub, per the docutils dispatcher contract.
- `38-TEST-CENSUS.md` row A2's predicted breakage is migrated: `tests/test_desc_rubric_decoupling_render_gate.py`'s SC#1 "over-reach guard" (`RETAINED_DELEGATION_METHODS`, requiring `literal_strong`/`depart_literal_strong` to KEEP delegating) is renamed to `NO_LONGER_DELEGATING_METHODS` and its assertion inverted to require ZERO delegating calls; the `DUMMY_STRONG_LITERAL` construction-site count assertion inverts from `== 2` to `== 0`. The four `DECOUPLED_METHODS` checks (`desc_signature`/`rubric`) and SC#2's golden-file byte-identity gate are untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace the dummy-node delegations with real leaf-emission bodies** - `4c71600` (feat)
2. **Deviation: scope the typeless-param FLD-03 test past the signature block** - `8f7b808` (fix)
3. **Task 2: Migrate this plan's census row and prove composition/scope** - `eb16c20` (test)

**Plan metadata:** (this commit, forthcoming)

## Files Created/Modified

- `typsphinx/translator.py` — new private helper `_emit_field_body_monospace_leaf`; `visit_literal_strong`/`visit_literal_emphasis` rewritten to call it instead of delegating; `depart_literal_strong`/`depart_literal_emphasis` docstrings corrected to state they are unreachable (Task 1).
- `tests/test_field_body_typography_render_gate.py` — `test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono`'s region narrowed to start at the field list's own label instead of the section heading (deviation commit).
- `tests/test_desc_rubric_decoupling_render_gate.py` — SC#1's `RETAINED_DELEGATION_METHODS`/count assertions migrated to their D-09-inverted form; module and class docstrings updated to explain the Phase 38 inversion (Task 2).

## Decisions Made

See `key-decisions` in the frontmatter above for the full list; the two most consequential:

- **A shared private helper, not verbatim copies.** `_emit_field_body_monospace_leaf(node, wrapper)` is called by both `visit_literal_strong` (`wrapper="strong"`) and `visit_literal_emphasis` (`wrapper="emph"`). The two bodies differ only in the wrapper call name, so a shared helper removes duplication with zero behavioral cost. D-12 leaves this choice to the executor; Phase 36's deliberate triplication (D-01/D-09) is the cited precedent for the opposite choice, and either is acceptable.
- **The typeless-param test's region-scoping bug is a Rule 1 fix, not a census row.** `38-TEST-CENSUS.md` row A2 only names the SC#1 delegation guard as this plan's assigned migration. The typeless-param test's region including the fixture's own `desc_signature` (which shares the literal string "untyped" with the field-body parameter it documents) was an unpredicted authoring oversight from plan 38-02, surfaced only when Task 1's correct implementation still failed this one test. Fixed by narrowing the region's start marker rather than touching the translator or the fixture's signature text.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Narrowed test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono's region past the signature block**

- **Found during:** Task 1 verification (`uv run pytest tests/test_field_body_typography_render_gate.py -v`)
- **Issue:** The test sliced its region from the section heading (`_section(typ_text, _H_NOTYPE, _H_NONASCII)`), which includes the fixture's `.. py:function:: field_name_without_type(untyped)` signature. That signature's sole parameter is also named "untyped", and Phase 37's SIG-04 rule (`37-EMISSION-CONTRACT.md` section 5.2 rule 2) unconditionally italicises a signature's bare parameter name regardless of whether it carries a type annotation — orthogonal, untouched-by-this-plan behavior. With Task 1's correct implementation in place, the region therefore still contained `emph(raw("untyped"))` from the SIGNATURE (not from `literal_emphasis`), tripping the "zero italic-monospace calls" assertion on unrelated bytes.
- **Fix:** Narrowed the region to start at the field list's own label marker (`strong(text("Parameters") + text(": "))`), which excludes the signature block while preserving the assertion's actual intent (that the field body itself emits exactly one bold-mono call and zero italic-mono calls for this typeless entry).
- **Files modified:** `tests/test_field_body_typography_render_gate.py`
- **Verification:** `uv run pytest tests/test_field_body_typography_render_gate.py -v` — all 20 tests pass.
- **Committed in:** `8f7b808` (deviation commit, separate from the two planned tasks)

**Total deviations:** 1 auto-fixed (Rule 1 bug fix, discovered while proving Task 1's own acceptance criteria)
**Impact on plan:** Necessary to satisfy the plan's acceptance criterion that all FLD-03 tests flip from FAILED to PASSED. No scope creep beyond the one test-file region-boundary correction; the translator implementation itself needed no change to satisfy this test once correctly scoped.

## Authorized Scope Extension: SC#1 Delegation Guard (Census Row A2)

`tests/test_desc_rubric_decoupling_render_gate.py` is NOT in this plan's `files_modified` frontmatter (which lists `typsphinx/translator.py`, `tests/test_translator.py`, `tests/test_pdf_render_gate.py`). `38-TEST-CENSUS.md` row A2 explicitly assigns this file's SC#1 delegation-guard migration to plan 38-07, and the orchestrator's own `<prior_wave_findings>` for this plan restated the same authorization by name, citing the census row's exact wording.

Before editing, `tests/test_translator.py` and `tests/test_pdf_render_gate.py` were grepped for any `literal_strong`/`literal_emphasis`/strong-or-emph-adjacent assertion that this plan's change could affect — neither file contains one (confirmed: `grep -n "literal_strong\|literal_emphasis"` returns nothing in either file; the `strong({text(...)`/`emph({text(...)` matches in `test_translator.py` are plain `nodes.strong`/`nodes.emphasis`, an unrelated node family this plan does not touch). No changes were needed to either file.

## Evidence

### Composition proof (cross-reference, contract section 5.4)

Built the fixture fresh via `-b typstpdf` and extracted the "Resolvable Type Cross Reference" region of the emitted `.typ`.

**Before (pre-phase, from `38-GATE-EVIDENCE-02.md`):**
```
par({strong({text("target")})
text(" (")
link(<index:FieldXrefTarget>, 
emph({text("FieldXrefTarget")}))
text(")")
text(" – ")
text("A parameter whose type resolves to a local class.")})
```

**After (this plan, measured):**
```
pad(left: 2.5em, {pad(left: 2.5em, {strong(text("Parameters") + text(": "))
strong(raw("target")) + text(" (") + link(<index:FieldXrefTarget>, emph(raw("FieldXrefTarget"))) + text(")") + text(" – ") + text("A parameter whose type resolves to a local class.")
})
})
```

The italic-monospace leaf (`emph(raw("FieldXrefTarget"))`) composes nested inside the emitted `link(...)` call, and the link's label argument (`<index:FieldXrefTarget>`) is byte-unchanged from the pre-phase build — `visit_reference` is untouched by this plan.

### Zero-width-space proof (contract section 5.3)

Searched the entire field-body-bearing region of the same fresh build's `.typ` (from `text("Multi-Value Bulleted Control")` to end of document) for both the literal U+200B byte and its 8-character Typst escape:

```python
zwsp = chr(0x200B)
zwsp in region        # False
"\\u{200B}" in region  # False
```

Neither is present anywhere in the field-body region, confirming `escape_typst_string` (not `_escape_signature_text`) was used at both new leaf-emission sites. `tests/test_field_body_typography_render_gate.py::test_fld03_no_zero_width_space_anywhere_in_field_bodies` asserts the same property over the whole test session's build and passes.

### Whole-suite set-difference proof

Baseline entering this plan (recorded by the orchestrator's `<prior_wave_findings>`, measured on this plan's base commit): `11 failed, 689 passed, 29 deselected` — all 11 failures in `tests/test_field_body_typography_render_gate.py`:

- `test_fld03_param_name_bold_monospace[multi-value-alpha]`
- `test_fld03_param_name_bold_monospace[multi-value-beta]`
- `test_fld03_param_name_bold_monospace[single-entry]`
- `test_fld03_param_name_bold_monospace[non-ascii]`
- `test_fld03_param_type_italic_monospace[multi-value-alpha]`
- `test_fld03_param_type_italic_monospace[multi-value-beta]`
- `test_fld03_param_type_italic_monospace[single-entry]`
- `test_fld03_param_type_italic_monospace[non-ascii]`
- `test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono`
- `test_fld03_nonascii_param_name_roundtrips_codepoints`
- `test_fld03_resolvable_type_composes_inside_link_unchanged_label`

After this plan's commits, `uv run pytest -m "not slow" -q` (run twice — once after Task 1's commit region gap closed by the deviation fix, once as the final post-Task-2 check): `700 passed, 29 deselected, 0 failed`. `689 + 11 = 700`, and the final run shows 0 failures, so the flipped set (FAILED → PASSED) is **exactly** the 11 node ids listed above, in the same direction the census predicted (row A2's SC#1 test is not itself a node-id flip in this baseline — it was already counted as passing in the 689, since the pre-existing over-reach guard's `!= []` form was still true before this plan's translator change landed; this plan's SC#1 migration keeps it passing post-change rather than flipping it). No other node id flipped in either direction. No unpredicted census miss beyond the one test-region deviation documented above.

**Lint/type trio**, same final state: `uv run black --check .` (190 files unchanged), `uv run ruff check .` (all checks passed), `uv run mypy typsphinx/` (no issues, 6 source files).

**Rubric assertions and shared bold/italic-visitor assertions unmodified:** confirmed via `git diff` — the only file in the SC#1 delegation-guard commit is `tests/test_desc_rubric_decoupling_render_gate.py`, and within it the `DECOUPLED_METHODS`/SC#2 golden-identity sections are byte-unchanged; `tests/test_rubric_option_concat_render_gate.py` and `tests/test_translator.py`'s rubric assertion (`test_rubric_rendering`, line ~3620) were not touched by any commit in this plan.

**No page-count constant re-pinned:** `tests/test_signature_page_boundary_render_gate.py` and `tests/test_signature_typography_multi_signature_page_count_gate.py` both stayed green in the final full-suite run with no edits — no observed page-count shift from this plan's change (consistent with contract section 5.6: within the monospace family, `raw`/`emph(raw)`/`strong(raw)` have identical advance widths; this plan only moves the field-body name/type from proportional to monospace inside constructs plan 38-06 already widened via the `pad` wrappers, so the incremental width delta from this specific change did not cross either fixture's page boundary at the current commit). Left alone per this plan's instructions; noted here for plan 38-08's own re-measurement pass.

## Issues Encountered

- **The typeless-param test's naming-collision trap** — see the Deviations section above. Caught immediately by the FLD-03 gate itself going RED on this one test even after Task 1's implementation was otherwise complete and correct; resolved by narrowing the test's own region boundary, never by touching the translator or the fixture's signature/docstring text.
- **The worktree's `uv`/`ruff` shims were not applied at session start**, causing a spurious first full-suite run to show 45 unrelated "environmental" failures (`tests/test_integration_*.py`, `tests/test_examples_basic.py` — all `subprocess.run(["uv", "run", ...])` sites hitting the documented NixOS stub-ld ELF-exec hazard, per the `nixos-sandbox-test-env` project memory). Resolved by symlinking the nix-store `uv` and the main tree's patchelf'd `ruff` into `.venv/bin/`; the subsequent full-suite run was clean (`700 passed, 29 deselected, 0 failed`), confirming these were purely a provisioning miss, not a regression.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `visit_literal_strong`/`visit_literal_emphasis` and the shared `_emit_field_body_monospace_leaf` helper are landed and stable; every FLD-03 assertion in `tests/test_field_body_typography_render_gate.py` is green (20/20).
- `tests/test_desc_rubric_decoupling_render_gate.py`'s SC#1 guard is fully migrated to its post-D-09 form; no further work remains there for this phase.
- Plan 38-08 (page counts): both named page-count constants (`EXPECTED_PAGE_COUNT_PRE_PHASE` in `tests/test_signature_page_boundary_render_gate.py`, `EXPECTED_PAGE_COUNT` in `tests/test_signature_typography_multi_signature_page_count_gate.py`) stayed green with no edits at this plan's HEAD — 38-08 should still perform its own independent re-measurement per the phase's stated methodology (re-measure, never re-derive), since this plan's own verification is a pass/fail check against the CURRENT pinned constants, not a fresh page-count measurement.
- No blockers.

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: typsphinx/translator.py
- FOUND: tests/test_field_body_typography_render_gate.py
- FOUND: tests/test_desc_rubric_decoupling_render_gate.py
- FOUND: commit 4c71600 (Task 1)
- FOUND: commit 8f7b808 (deviation)
- FOUND: commit eb16c20 (Task 2)
