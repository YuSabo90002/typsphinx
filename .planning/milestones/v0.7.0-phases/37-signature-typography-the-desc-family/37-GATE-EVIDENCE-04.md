# Phase 37 Plan 04 — Gate Evidence

**Commit SHA (base, before this plan's edits):** `011b9265daf3389f3482b5efd96b4eaa16a94743`
**Plan commit series starts at:** `731228ead5d6ee38ffe870ce77c765d7ecef78d3` (Task 1, the census)
**Produced:** 2026-08-01.

This is the deliberate RED window's evidence record for 37-04. It records, by pytest node id, the
token-by-token derivation of every migrated assertion and `golden.typ` line, the verbatim RED
output against the untouched (pre-Phase-37) translator, and the RED-versus-STAYS-GREEN table
later waves verify against by set difference.

---

## 1. Token-by-token derivation — `golden.typ`'s 9 changed signature lines

**Correction to this plan's own frontmatter/objective: the diff is 9 lines changed, not 7.**
`git diff --numstat tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` reports:

```
9	9	tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
```

37-04-PLAN.md's objective ("golden.typ's 7 signature lines"), Task 3's action text ("replace exactly
the seven desc_signature-driven lines — the two-line connect block, the three two-line compile
blocks, and the one-line --sep block"), and Task 3's automated verify command
(`test "$(git diff --numstat ...)" = "7/7"`) all state 7. Counting the plan's OWN enumerated
blocks arithmetically: one 2-line `connect` block + three 2-line `compile` blocks + one 1-line
`--sep` block = 2 + 6 + 1 = **9**, not 7 — the plan's arithmetic is internally inconsistent with its
own block-by-block description. `37-EMISSION-CONTRACT.md` section 9's worked derivation (the
authoritative, hand-derived specification per the binding rule "expected strings are hand-derived …
never from running the new code") independently shows the SAME five 2-or-1-line blocks. Applying
section 9 literally and correctly therefore produces a 9-line diff, matching the plan's own
per-block description and NOT its "seven" summary figure. Per Task 3's own instruction ("If your
derivation disagrees with contract section 9's stated target line, STOP and report the discrepancy
in the SUMMARY rather than silently adopting either"), this is reported here and in
`37-04-SUMMARY.md` rather than silently forcing a 7-line result by dropping a real signature-byte
change. **The plan's `test = "7/7"` automated verify command will fail as written; this is expected
and is the discrepancy being reported, not a mistake in this plan's execution.**

### connect(host, port, timeout=30) — golden.typ lines 26-27

Doctree (measured, `37-EMISSION-CONTRACT.md` section 9's table): `desc_name>Text['connect']`;
`desc_parameterlist` with 3 `desc_parameter`s: `desc_sig_name['host']`, `desc_sig_name['port']`,
(`desc_sig_name['timeout']`, `desc_sig_operator['=']`, `inline.default_value['30']`).

| Token | Source rule | Emitted |
|---|---|---|
| wrapper open | section 3 | `block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {` |
| `connect` | section 5.1 (`desc_name`, text-only leaf) | `strong(raw("connect"))` |
| `(` | section 6 (`visit_desc_parameterlist`) | `raw("(") + ` |
| `host` | section 5.2 rule 2 (first+leaf `desc_sig_name` of its `desc_parameter`) | `emph(raw("host"))` |
| `, ` | section 6 (`depart_desc_parameter`) | ` + raw(", ") + ` |
| `port` | section 5.2 rule 2 | `emph(raw("port"))` |
| `, ` | section 6 | ` + raw(", ") + ` |
| `timeout` | section 5.2 rule 2 (first+leaf `desc_sig_name` of this parameter) | `emph(raw("timeout"))` |
| `=` | section 4.3 (`desc_sig_operator`, free monospace) | ` + raw("=")` |
| `30` | section 4.3 (`inline.default_value`, free monospace) | ` + raw("30")` |
| `)` | section 6 (`depart_desc_parameterlist`) | ` + raw(")")` |
| wrapper close | section 3 | `}))` |

Result:
```
block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("connect"))
raw("(") + emph(raw("host")) + raw(", ") + emph(raw("port")) + raw(", ") + emph(raw("timeout")) + raw("=") + raw("30") + raw(")")}))
```
Matches `37-EMISSION-CONTRACT.md` section 9 verbatim.

### compile(source) / compile(source, filename) / compile(source, filename, symbol) — golden.typ lines 36-37, 40-41, 43-44

Doctree: `desc_name>Text['compile']`; `desc_parameterlist` with 1/2/3 `desc_parameter`s, each
`desc_parameter>desc_sig_name` only (no operator, no default value).

| Token | Source rule | Emitted |
|---|---|---|
| `compile` | section 5.1 (text-only leaf) | `strong(raw("compile"))` |
| `(` | section 6 | `raw("(") + ` |
| each `source`/`filename`/`symbol` | section 5.2 rule 2 (first+leaf per its own `desc_parameter`) | `emph(raw("..."))` |
| `, ` between parameters | section 6 | ` + raw(", ") + ` |
| `)` | section 6 | ` + raw(")")` |

Result (three blocks, one per signature):
```
block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(")")}))
```
```
block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(")")}))
```
```
block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(", ") + emph(raw("symbol")) + raw(")")}))
```
Matches `37-EMISSION-CONTRACT.md` section 9 verbatim. The `linebreak()` tokens between siblings
(FID-03, untouched per section 3) are unchanged.

### --sep (.. option::) — golden.typ line 59

Doctree: `desc_name>Text['--sep']`; `desc_addname` with **zero children**.

| Token | Source rule | Emitted |
|---|---|---|
| `--sep` | section 5.1 (text-only leaf) | `strong(raw("--sep"))` |
| `desc_addname` (empty) | contributes zero bytes | (nothing) |

Result:
```
block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("--sep"))}))
```
Matches `37-EMISSION-CONTRACT.md` section 9 verbatim.

### Unchanged lines (the evidence that Phase 37 touched only signatures)

`git diff tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` (below, full) shows zero
changes to: the three rubric lines (`Options` line 57, `A Rubric In A List Item` line 75,
`Trailing Heading` line 87), the plain-bold regression control (line 51), the `list({ … })` bullet
structure (lines 66-82), every `par({text(...)})` body paragraph, every `[#metadata(none) <…>]`
anchor, every `linebreak()`/`parbreak()`, and the whole preamble (lines 1-25). No
`\u{200B}` sequence appears anywhere in the new file (verified: `grep -c '\\u{200B}'
golden.typ` returns no match) — none of the five signatures contains a `.` inside a signature text
run.

```diff
diff --git a/tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ b/tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
index 7b71512..d8481fd 100644
--- a/tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
+++ b/tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
@@ -23,8 +23,8 @@ par({text("This fixture combines a single signature, sibling signatures, plain b
 
 par({text("Single signature with an id anchor.")})
 
-strong({text("connect")
-text("(") + text("host") + text(", ") + text("port") + text(", ") + text("timeout") + text("=") + text("30") + text(")")})
+block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("connect"))
+raw("(") + emph(raw("host")) + raw(", ") + emph(raw("port")) + raw(", ") + emph(raw("timeout")) + raw("=") + raw("30") + raw(")")}))
 [#metadata(none) <index:connect>]
 par({text("Connect to ")
 emph({text("host")})
@@ -33,15 +33,15 @@ text(".")})
 parbreak()
 par({text("Sibling signatures under one directive.")})
 
-strong({text("compile")
-text("(") + text("source") + text(")")})
+block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
+raw("(") + emph(raw("source")) + raw(")")}))
 [#metadata(none) <index:compile>]
 linebreak()
-strong({text("compile")
-text("(") + text("source") + text(", ") + text("filename") + text(")")})
+block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
+raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(")")}))
 linebreak()
-strong({text("compile")
-text("(") + text("source") + text(", ") + text("filename") + text(", ") + text("symbol") + text(")")})
+block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
+raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(", ") + emph(raw("symbol")) + raw(")")}))
 par({text("Compile source into a code or AST object.")})
 
 parbreak()
@@ -56,7 +56,7 @@ par({text("The autodoc “Options” rubric shape.")})
 
 strong({text("Options")})
 linebreak()
-strong({text("--sep")})
+block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {strong(raw("--sep"))}))
 [#metadata(none) <index:cmdoption-sep>]
 par({text("If specified, separate source and build directories.")})
```

---

## 2. Measurement discrepancy found this session: unresolved C-domain type parameters

`37-EMISSION-CONTRACT.md` section 5.2 states (narrative claim): "the first `desc_sig_name` direct
child of a `desc_parameter` is always the parameter's own name and always a leaf; every later one
is part of the type annotation and may be a non-leaf."

Measured this session against `tests/fixtures/desc_sig_space_render_gate/index.rst`'s
`.. c:function:: PyObject *PyType_GenericAlloc(PyTypeObject *type, Py_ssize_t nitems)` (no
intersphinx configured, so `PyTypeObject`/`Py_ssize_t` never resolve to a cross-reference and are
never wrapped in a `reference` node): the doctree's `desc_parameter` for `PyTypeObject *type` is

```
<desc_parameter>
    <desc_sig_name>PyTypeObject</desc_sig_name>
    <desc_sig_space/>
    <desc_sig_punctuation>*</desc_sig_punctuation>
    <desc_sig_name>type</desc_sig_name>
```

Here the **type** (`PyTypeObject`), not the name (`type`), is the first direct `desc_sig_name`
child — the narrative claim does not hold for an unresolved C-domain type. Mechanically applying
rule 2 exactly as specified, the FIRST desc_sig_name (`PyTypeObject`) gets `emph(raw(...))` and the
SECOND (`type`) falls through to rule 3's plain `raw(...)`. This is the mirror image of
`tests/fixtures/desc_signature_concat_render_gate/index.rst`'s `MyType *obj` (WITH intersphinx
configured), where `MyType` resolves and IS wrapped in a `reference`, leaving `obj` as the first
direct child and therefore the one that gets italicised.

This plan does not fix the underlying discriminator (out of scope — no `typsphinx/` edits). The
test assertion in `tests/test_desc_sig_space_render_gate.py` is migrated to match the MECHANICAL
rule-2 output exactly as measured (`emph(raw("PyTypeObject")) + raw(" ") + raw("*") +
raw("type")`), not to the narrative's simplified claim. Flagged here for 37-06's implementer: this
existing fixture will demonstrate this discriminator edge case once the wrapper lands, and it is
correct-per-contract, not a bug in the migration.

---

## 3. Verbatim pytest output — the ten RED node ids (against commit `011b926`, untouched translator)

### `tests/test_translator.py` (4 node ids)

```
$ uv run pytest tests/test_translator.py::test_desc_signature_rendering tests/test_translator.py::test_desc_with_annotation_and_name tests/test_translator.py::test_desc_parameterlist tests/test_translator.py::test_full_api_description_structure -v
FAILED tests/test_translator.py::test_desc_signature_rendering - assert 'block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {' in 'strong({text("TypstBuilder(app, env)")})\nparbreak()\n'
FAILED tests/test_translator.py::test_desc_with_annotation_and_name - assert ('strong(raw("class"))' in 'strong({text("class")\ntext("TypstBuilder")})\nparbreak()\n')
FAILED tests/test_translator.py::test_desc_parameterlist - assert ('strong(raw("function"))' in 'strong({text("function")\ntext("(") + text("arg1") + text(", ") + text("arg2") + text(", ") + text("arg3") + text(")")})\nparbreak()\n')
FAILED tests/test_translator.py::test_full_api_description_structure - assert ('strong(raw("class"))' in 'strong({text("class")\ntext("TypstBuilder")\ntext("(") + text("app") + text(", ") + text("env") + text(")")})\npar({text("Builder class for Typst output.")})\n\nstrong(text("Parameters") + text(": "))\npar({text("app - Sphinx application")})\n\n\n\nparbreak()\n')
============================== 4 failed in 0.12s ===============================
```

### `tests/test_desc_signature_concat_render_gate.py` (2 node ids)

```
$ uv run pytest tests/test_desc_signature_concat_render_gate.py -v
FAILED tests/test_desc_signature_concat_render_gate.py::TestDescSignatureConcatRenderGate::test_typstpdf_signature_reference_first_param_produces_pdf
  AssertionError: Expected a parameter-list line emitting 'raw("(") + link(' on one statement -- the '+' was split from its link operand by a stray newline (the fix is not applied):
FAILED tests/test_desc_signature_concat_render_gate.py::TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf
  ValueError: substring not found  (typ_text.index('strong(raw("compile"))') -- not yet emitted)
============================== 2 failed in 0.61s ===============================
```

### `tests/test_rubric_option_concat_render_gate.py` (1 node id)

```
$ uv run pytest tests/test_rubric_option_concat_render_gate.py -v
FAILED tests/test_rubric_option_concat_render_gate.py::TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf
  ValueError: substring not found  (typ_text.index('strong(raw("--sep"))') -- not yet emitted)
============================== 1 failed in 0.36s ===============================
```
Confirmed separately (see section 4 below) that the `Structure Options` and `Trailing Heading`
rubric `.index()` lookups still succeed against the current (unfixed) translator output — the
failure is isolated to the `--sep` lookup.

### `tests/test_desc_sig_space_render_gate.py` (1 node id)

```
$ uv run pytest tests/test_desc_sig_space_render_gate.py -v
FAILED tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces
  AssertionError: Expected the 'class ' annotation-prefix space as a separate raw(" ") statement between raw("class") and the dotted class name (FID-07 regression):
PASSED tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_pdf_extracted_text_has_no_merged_tokens
============================== 1 failed, 1 passed in 0.79s ===============================
```

### `tests/test_desc_rubric_decoupling_render_gate.py` (golden.typ consumer, 1 node id)

```
$ uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -v
PASSED tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong
FAILED tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden
  AssertionError: Emitted .typ differs from the committed golden -- SC#2's byte-identity requirement is violated
PASSED tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_decoupling_fixture_still_compiles_to_pdf
============================== 1 failed, 2 passed in 0.66s ===============================
```

### `tests/test_pdf_render_gate.py` (1 node id, `@pytest.mark.slow`)

```
$ uv run pytest "tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline" -v -m ""
FAILED tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline
  AssertionError: Expected the ' → ' return arrow adjacent to the return type in extracted PDF text -- desc_returns regression
  assert '→ int' in '...get_value() -> int...'
============================== 1 failed in 0.44s ===============================
```

---

## 4. Rubric-lookup control check (Structure Options / Trailing Heading stay findable)

```
$ uv run python -m sphinx -b typstpdf tests/fixtures/rubric_option_concat_render_gate <tmp>
$ grep -c 'strong({text("Structure Options")})' <tmp>/index.typ
1
$ grep -c 'strong({text("Trailing Heading")})' <tmp>/index.typ
1
```
Both rubric substrings are still present, byte-identical, in the CURRENT (pre-Phase-37, untouched)
translator's output — confirming the two rubric `.index()` lookups in
`tests/test_rubric_option_concat_render_gate.py` were left untouched and remain findable.

---

## 5. RED-versus-STAYS-GREEN table, by pytest node id

| Node id | State (against `011b926`) | Flips green at |
|---|---|---|
| `tests/test_translator.py::test_desc_signature_rendering` | RED | 37-06 |
| `tests/test_translator.py::test_desc_with_annotation_and_name` | RED | 37-06 |
| `tests/test_translator.py::test_desc_parameterlist` | RED | 37-06 |
| `tests/test_translator.py::test_full_api_description_structure` | RED | 37-06 |
| `tests/test_desc_signature_concat_render_gate.py::TestDescSignatureConcatRenderGate::test_typstpdf_signature_reference_first_param_produces_pdf` | RED | 37-07 |
| `tests/test_desc_signature_concat_render_gate.py::TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf` | RED | 37-07 |
| `tests/test_rubric_option_concat_render_gate.py::TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf` | RED | 37-06 |
| `tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces` | RED | 37-06 |
| `tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_pdf_extracted_text_has_no_merged_tokens` | GREEN (control; U+200B strip added defensively) | already green; stays green through all waves |
| `tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden` | RED | 37-07 |
| `tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong` | GREEN (Phase 36 control) | already green; stays green |
| `tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_decoupling_fixture_still_compiles_to_pdf` | GREEN (compile-sanity control) | already green; stays green |
| `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` | RED (`@pytest.mark.slow`) | 37-07 |
| `tests/test_rubric_option_concat_render_gate.py`'s `Structure Options`/`Trailing Heading` lookups (same node id as above, sub-assertions) | GREEN (Phase 39 control, untouched) | never (Phase 39 territory) |
| `tests/test_translator.py::test_rubric_rendering` | GREEN (Phase 39 control, untouched) | never (Phase 39 territory) |
| `tests/test_translator.py::test_desc_signature_line_multiline_emits_one_linebreak` | GREEN | conditional; re-verify after 37-05/37-06 |
| `tests/test_translator.py::test_desc_signature_line_single_line_emits_no_linebreak` | GREEN | conditional; re-verify after 37-05/37-06 |
| `tests/test_translator.py::test_desc_signature_line_resets_per_signature` | GREEN | conditional; re-verify after 37-05/37-06 |
| `tests/test_desc_bodyless_concat_render_gate.py` (all node ids) | GREEN | conditional; re-verify after 37-05 |

Reads as 10 RED node ids (9 in the default `-m "not slow"` run, 1 in the slow-marked PDF gate) and
the explicitly-protected/conditional GREENs. Later waves verify by **set difference** over this
table, never by count, per `STATE.md`'s Operator Next Steps.

---

## 6. Whole-suite `-m "not slow"` line, with every intentional RED enumerated

```
$ uv run pytest -m "not slow"
FAILED tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden
FAILED tests/test_desc_sig_space_render_gate.py::TestDescSigSpaceRenderGate::test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces
FAILED tests/test_desc_signature_concat_render_gate.py::TestDescSignatureConcatRenderGate::test_typstpdf_signature_reference_first_param_produces_pdf
FAILED tests/test_desc_signature_concat_render_gate.py::TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf
FAILED tests/test_rubric_option_concat_render_gate.py::TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf
FAILED tests/test_translator.py::test_desc_signature_rendering
FAILED tests/test_translator.py::test_desc_with_annotation_and_name
FAILED tests/test_translator.py::test_desc_parameterlist
FAILED tests/test_translator.py::test_full_api_description_structure
================ 9 failed, 616 passed, 29 deselected in 44.41s =================
```
Exactly the 9 non-slow node ids from section 5's table, with zero unexpected/collateral failures.
The 10th (`tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline`) is `@pytest.mark.slow` and excluded from this run (see
section 3's separate invocation).

---

## 7. Standing invariants confirmed at this commit

```
$ uv run black --check .
All done! (175 files would be left unchanged.)

$ .venv/bin/ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files

$ git diff --stat -- typsphinx/
(empty -- zero changes under typsphinx/)
```
