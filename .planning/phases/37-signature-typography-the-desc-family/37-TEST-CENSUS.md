# Phase 37 Plan 04 — SC#5 Test Census

**Produced:** 2026-08-01, by 37-04-PLAN.md Task 1.
**Method:** every file below was opened and its actual assertions read (not grepped for
`desc_*` node names). Contract `37-EMISSION-CONTRACT.md` §11 is the verified starting point;
this census re-measures against the current tree and extends it where reading the code
disagreed with a name-based guess.

---

## Bucket A — ASSERTS on signature bytes, WILL BREAK

10 test node ids across 6 files (5 test modules + 1 fixture consumed by a 6th module). This is
one MORE assertion-bearing node than contract §11's "nine assertions across five test modules"
— row A5 below is a genuine extension found by reading `tests/test_desc_signature_concat_render_gate.py`
in full rather than only the two line numbers §11 names (see "Disagreement" note at the end of
this bucket).

| # | File:Line(s) | Test function | Current expected string | Driving contract section | Owning plan (flips green) |
|---|---|---|---|---|---|
| A1 | `tests/test_translator.py:3371` | `test_desc_signature_rendering` | `"TypstBuilder" in output and "strong({" in output` | §4 (monospace branch — bare `nodes.Text` directly under `desc_signature`, no `desc_name`, per the plan's explicit note **not** §5.1) | 37-06 |
| A2 | `tests/test_translator.py:3399` | `test_desc_with_annotation_and_name` | `'strong({text("class")' in output and 'text("TypstBuilder")' in output` | §3 (wrapper) + §5.1 (`desc_annotation`/`desc_name` text-only-leaf bold) | 37-06 |
| A3 | `tests/test_translator.py:3437` | `test_desc_parameterlist` | `'strong({text("function")' in output and "arg1" in output` | §3 + §5.1 (`desc_name`) + §4 (bare `nodes.Text` parameter children — no `desc_sig_name` node exists in this synthetic doctree, so §5.2's italic discriminator never fires; "arg1" gets the blanket flag-driven `raw()` wrap, not `emph(raw())`) | 37-06 |
| A4 | `tests/test_translator.py:3679` | `test_full_api_description_structure` | `'strong({text("class")' in output and "TypstBuilder" in output` | §3 + §5.1 | 37-06 |
| A5 | `tests/test_desc_signature_concat_render_gate.py:169,180` | `TestDescSignatureConcatRenderGate::test_typstpdf_signature_reference_first_param_produces_pdf` | `'text("(") + link(' in ln` (169); `'text(")")' in param_line` (180) | §6 (opening/closing paren delimiters) + §4 (the `link()`'s inner `MyType` text, a `reference`-wrapped `desc_sig_name` whose **parent is `reference`, not `desc_parameter`**, so §5.2 rule 3 passes it through to the blanket flag) + §5.2 rule 2 (`obj`/`count`, each the first `desc_sig_name` direct child of its own `desc_parameter`, become `emph(raw(...))`) | 37-07 |
| A6 | `tests/test_desc_signature_concat_render_gate.py:269,282` | `TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf` | `typ_text.index('strong({text("compile")')` (269); `typ_text.rindex('text("(") + text("source") + text(", ") + text("filename") + text(", ") + text("symbol") + text(")")')` (271-273); `typ_text.index('strong({text("solo")')` (282) | §3 + §5.1 (`strong(raw("compile"))` / `strong(raw("solo"))`) + §5.2 rule 2 (each parameter's own `desc_sig_name` → `emph(raw(...))`) + §6 (delimiters) | 37-07 |
| A7 | `tests/test_rubric_option_concat_render_gate.py:134` | `TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf` | `typ_text.index('strong({text("--sep")})')` | §3 + §5.1 (`.. option::`'s `desc_name` is a text-only leaf; its `desc_addname` sibling has zero children and contributes nothing, matching contract §9's worked `--sep` derivation) | 37-06 |
| A8 | `tests/test_desc_sig_space_render_gate.py:149,158,169` | `TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces` | `'text("class")\ntext(" ")\ntext("sphinx'` (149); `'text("PyObject")\ntext(" ")\ntext("*")\ntext("PyType_GenericAlloc")'` (158); `'text("PyTypeObject") + text(" ") + text("*") + text("type")'` (169) | §3 + §4 (every `desc_sig_space`/`desc_sig_keyword_type` routes through the monospace branch — the test's subject is the SPACE surviving, not the wrapper) | 37-06 |
| A9 | `tests/test_pdf_render_gate.py:780` | `TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` | `"-> int" in full_text` | §7 (return-arrow glyph) + §4.2 (U+200B strip needed before every comparison in this function — the fixture's `desc_addname` contains a dotted name) | 37-07 |
| A10 | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` (7 signature lines) consumed by `tests/test_desc_rubric_decoupling_render_gate.py:267` | `TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden` | full byte-identity of `golden.typ` against a fresh `-b typst` build | §9 (worked derivation from §3 + §5.1 + §5.2 rule 2 + §6) | 37-07 |

**Disagreement between grep-by-name and read-the-assertion (required evidence row):**
`tests/test_confval_field_body_render_gate.py` visually matches a `desc_*`-shaped grep
(`strong({text("html_title")})`, line 159) — a name/shape grep would flag it as
signature-adjacent. Reading the assertion shows `html_title` is `**html_title**`
markdown bold (`nodes.strong`) inside a confval `:default:` field body, not a
`desc_signature` sub-part; it is bucketed B (stays green) below. Conversely,
`tests/test_desc_signature_concat_render_gate.py` — a file already known by name/grep to be
signature-adjacent — turned out to contain a **second**, previously unlisted breaking class
(`TestDescSignatureConcatRenderGate`, row A5) that contract §11's line-scoped citation
(`:269,282`, row A6 only) did not name. Reading the whole file, not just the cited lines,
surfaced it. Both directions of disagreement are recorded here per the acceptance criteria.

---

## Bucket B — MENTIONS the node family, asserts on something Phase 37 does not change, MUST STAY GREEN

| File | Why it's safe |
|---|---|
| `tests/test_confval_field_body_render_gate.py` | `strong({text("html_title")})` (line 159) is `nodes.strong` markdown bold inside a confval field body — a different handler (`visit_strong`), not `desc_signature`. Untouched by Phase 37. |
| `tests/test_confval_field_spacing_render_gate.py` | Exercises `depart_field_name`/`depart_field` colon-space and inter-field separator bookkeeping (`field_list`, FID-09) — no `desc_*` node in its fixture or assertions at all. |
| `tests/test_deflist_nested_definition_render_gate.py` | Docstring mentions `desc_signature` only as unrelated historical context for an "orphaned buffer" bug; its actual assertions are about `definition_list` nesting. |
| `tests/test_deflist_term_concat_render_gate.py` | Docstring mentions `in_desc_parameter` only as an analogy for the `deflist`-term concat mechanism it actually tests; no `desc_*` node in the fixture. |
| `tests/test_deflist_term_inline_children_gate.py` | Asserts on `strong({text("bold")})` / `emph({...})` from markdown `**bold**`/`*italic*` inside deflist TERMS — `nodes.strong`/`nodes.emphasis`, not `desc_signature`. |
| `tests/test_desc_container_propagated_target_render_gate.py` | Asserts only on `[#metadata(none) <id>]` anchors and `link(<name>, ...)` label matching — the anchor-emission loop in `depart_desc_signature` is explicitly byte-unchanged by contract §3. |
| `tests/test_desc_signature_anchor_render_gate.py` | Same reasoning: anchor/label emission only (`[#metadata(none) <index:c.foo>]`, `link(<name>,...)` regex matching), no signature-wrapper or sub-part byte assertion. |
| `tests/test_pdf_render_gate.py` (every function except `TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline`, row A9) | No other function in this module asserts on `desc_*` signature bytes. |

---

## Bucket C — CONDITIONALLY at risk, re-verify after §8 (SIG-08, plan 37-05) lands

| File / test | Condition |
|---|---|
| `tests/test_desc_bodyless_concat_render_gate.py` | Is itself §8's (SIG-08, D-12) regression control for sibling body-less `desc` nodes. Expected to stay green through 37-05's `depart_desc` marker fix — re-verify after that plan lands that the marker logic did not disturb the sibling-desc separator it protects. |
| `tests/test_translator.py::test_desc_signature_line_multiline_emits_one_linebreak` | Counts `linebreak()` occurrences and checks bare content substrings — both survive re-wrapping under §3's new `block(...)`/`par(...)` wrapper, since the FID-03 sibling `linebreak()` mechanism is explicitly untouched. Re-verify once the wrapper (37-06) lands. |
| `tests/test_translator.py::test_desc_signature_line_single_line_emits_no_linebreak` | Same reasoning — the "no `linebreak()` for a single line" invariant does not depend on the wrapper shape. |
| `tests/test_translator.py::test_desc_signature_line_resets_per_signature` | Same reasoning — the per-signature `_is_first_desc_signature_line` reset is independent of the wrapper. |

---

## Counts

- Bucket A (will break): **10** test node ids across **5** test modules + **1** fixture (`golden.typ`, consumed by a 6th module).
- Bucket B (mentions, stays green): **8** files.
- Bucket C (conditional): **4** test node ids across **2** files.
- **Total files touched by this census's reading pass:** 13 (matches the 13 files named in `37-CONTEXT.md`'s starting blast-radius list — every one was opened and read this session).

## Agreement with the milestone's recorded 10-file / 61-class figure

`STATE.md`'s "Measured blast radius: 10 test files, 61 render-gate classes" is a
**milestone-wide** (all of Phases 36-41's `desc_*`/`field_list`/admonition/rubric/citation
surface) figure recorded at v0.7.0 roadmap creation, 2026-07-29 — before Phase 37 itself was
planned. It is not decomposable 1:1 against this phase's own census: this census's 13 files are
Phase-37-scoped only (the `desc_signature` family), counts assertion rows rather than test
classes, and several of the 13 files (Bucket B) are single-class-per-file gates that were never
part of the milestone-wide 61-class denominator's own Phase-37 subset in the first place. **This
phase's own numbers (10 breaking node ids / 5+1 files) do not attempt to reconcile against the
61-class milestone total** — they are the Phase-37-specific, freshly re-measured figure this
plan's `must_haves` requires, and the disagreement is recorded here explicitly rather than
silently adopting either number.

## MUST-NOT-TOUCH — rubric assertions (Phase 39 territory)

Two assertions are explicitly protected and must remain byte-identical, still green, in this
plan and this wave:

1. **`tests/test_rubric_option_concat_render_gate.py:133`** — `typ_text.index('strong({text("Structure Options")})')` (the `Structure Options` rubric half of the FID-04 gate).
2. **`tests/test_rubric_option_concat_render_gate.py:150`** — `typ_text.index('strong({text("Trailing Heading")})')` (the end-of-document `Trailing Heading` rubric).
3. **`tests/test_translator.py:3597`** — `test_rubric_rendering`'s `'strong({text("Methods")]' in output or "Methods" in output` assertion.

`rubric` is Phase 39 territory; Phase 36 already decoupled `rubric` from `desc_signature`
(`visit_rubric`/`depart_rubric` no longer delegate to `visit_strong` via a dummy node — see
`tests/test_desc_rubric_decoupling_render_gate.py`), so restyling one does not touch the other.
Editing either of these three assertions in this plan would destroy that evidence. Both
`--sep`-adjacent rubric lookups in `test_rubric_option_concat_render_gate.py` gain an inline
comment (Task 2) stating they are Phase 39 territory and deliberately unchanged; no value on
either line changes.
