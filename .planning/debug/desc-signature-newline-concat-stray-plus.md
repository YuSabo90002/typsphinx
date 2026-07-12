---
status: fixing
trigger: "Corpus gate fatal #9: TypstError: expected expression at usage/domains/c.typ:107 (also cpp.typ) — C/C++ domain multi-line function signature rendered via strong({...}) + _inline_concat_* path emits a malformed leading '+' (' + link(...)') after a NEWLINE-terminated sibling. Concat separator mixed with signature-line newlines produces a '+' with no left operand."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "Inside a desc_signature, visit_desc_signature delegates to visit_strong, which sets in_list_item=True (children newline-separated). visit_desc_parameterlist ALSO sets in_desc_parameter=True and appends 'text(\"(\") + ' (a trailing concat +), but leaves list_item_needs_separator=True (it consumes but does not reset it). So while emitting the FIRST parameter, BOTH in_list_item AND in_desc_parameter are active. When that first parameter starts with a cross-reference (a link), visit_reference emits the list-item newline UNCONDITIONALLY at line 2649 (`if in_list_item and list_item_needs_separator: add_text('\\n')`) BEFORE _enter_inline_concat_element. This inserts a '\\n' right after 'text(\"(\") + ', stranding the '+' at end-of-line with no right operand -> 'expected expression'. Root asymmetry: every OTHER inline visitor (visit_Text 798-800, visit_literal, visit_strong 920-922, visit_emphasis) guards the list-item newline behind `if not self._emit.../_enter_inline_concat_element():` so the newline and the concat + are mutually exclusive; visit_reference alone emits the newline first and unconditionally, violating that invariant inside a concat context."
  confirming_evidence:
    - "Minimal fixture `.. c:function:: void PyType_GenericAlloc(PyTypeObject *type, Py_ssize_t nitems)` emits: line 24 `text(\"(\") + ` (trailing + then EOL), line 25 `link(<c.PyTypeObject>, text(\"PyTypeObject\"))  + ...`. cat -A confirms `text(\"(\") + $` (trailing + + newline). typst.compile -> 'expected expression'. Byte-shape match to corpus c.typ:107."
    - "Sibling `.. cpp:function:: void Foo(std::string const &name, int count)` whose first parameter starts with TEXT (not a reference) compiles FINE: `text(\"(\") + text(\"std\") + ...` all on one line — because visit_Text (798-800) correctly suppresses the list-item newline when in_desc_parameter is active. Only the reference-first parameter breaks. This isolates visit_reference as the sole offender."
    - "visit_reference lines 2648-2650 emit the newline with NO concat-context guard, before _enter_inline_concat_element (2666-2667). visit_Text/visit_strong emit the newline only inside `if not self._emit_inline_concat_separator()/_enter_inline_concat_element():`."
  falsification_test: "If, after guarding visit_reference's list-item newline behind the concat-context check (emit newline only when _inline_concat_context() is None), the fixture STILL emits `text(\"(\") + \\nlink(...)` OR still fails typst.compile with 'expected expression', the hypothesis is wrong."
  fix_rationale: "Make visit_reference uphold the same mutual-exclusion invariant every other inline visitor already upholds: inside a code-mode concat context, the list-item newline separator must NOT fire — the concat + is the separator, and a newline inside the +-joined expression strands the operator. Capture in_concat = (_inline_concat_context() is not None) BEFORE _enter_inline_concat_element (which suppresses the outer flag), call _enter for wrapper-opening refs as today (it emits the leading + only when has_content), and emit the list-item newline ONLY when not in_concat. This is the ROOT (the newline/concat collision), general to every desc-parameter/link/term/field-body concat context — not a per-file patch. It preserves the genuine inline + from bugs #3/#5/#8 (visit_Text/literal/strong unchanged) and preserves the plain list-item newline for references OUTSIDE any concat context."
  blind_spots: "Fix targets visit_reference only. If the corpus surfaces a trailing/leading '+' shape produced by a DIFFERENT visitor inserting a newline into a concat context (not references), that would remain — but analysis shows only visit_reference emits an unguarded newline among inline concat participants; visit_desc_returns/desc_signature_line operate OUTSIDE the parameter concat context. Verified via corpus gate re-run (all 6 files)."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: guard visit_reference list-item newline behind concat-context check; rebuild fixture + fast suite + corpus gate
expecting: fixture emits `text("(") + link(...)` on one statement; compiles to %PDF; corpus advances past c.typ:107 / cpp.typ and clears the 4 trailing-'+'-at-EOL files
next_action: Edit visit_reference (lines 2645-2667); rebuild repro; run typst.compile; add fast regression test; fast suite + lint; corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; C/C++ domain multi-line function signatures emit valid Typst.
actual: "Typst compilation failed: TypstError: expected expression" at usage/domains/c.typ:107 (also cpp.typ). Multi-line function signature inside strong({...}) emits a malformed leading '+' (' + link(...)') after a newline-terminated sibling. Trailing-'+'-at-EOL shape also appears in coverage.typ, extending_build.typ, basics.typ, directives.typ (4 more files).
errors: "TypstError: expected expression"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after bugs #1-#8 unblocked the compile path.

## Eliminated

## Evidence

- timestamp: repro
  checked: Built minimal C/C++ function-signature fixture via -b typst; inspected emitted index.typ (cat -A) and ran typst.compile.
  found: c:function first param (a cross-ref type) emits `text("(") + $` (trailing + + newline) then `link(...)` on the next line -> typst.compile 'expected expression'. cpp:function whose first param starts with text compiles fine (`text("(") + text("std") + ...` one line).
  implication: Root cause is the trailing '+' at EOL, produced by visit_reference emitting a list-item newline immediately after parameterlist's `text("(") + `. Only reference-first parameters break; text-first ones are already guarded (visit_Text).

- timestamp: source-asymmetry
  checked: Compared list-item-newline emission across inline visitors.
  found: visit_Text (798-800), visit_strong (920-922), visit_literal, visit_emphasis all guard the newline behind `if not self._emit.../_enter_inline_concat_element():`. visit_reference (2648-2650) emits the newline UNCONDITIONALLY before _enter_inline_concat_element (2666-2667).
  implication: visit_reference alone violates the concat/newline mutual-exclusion invariant. Fix = uphold the invariant in visit_reference.

## Resolution

root_cause: Inside a desc_signature the translator delegates to visit_strong (in_list_item=True, children newline-separated). visit_desc_parameterlist also sets in_desc_parameter=True and appends `text("(") + ` (a trailing concat +) while leaving list_item_needs_separator=True. So while emitting the FIRST parameter BOTH in_list_item AND in_desc_parameter are active. When that first parameter leads with a cross-referenced type (a wrapper-opening reference -> link(...)), visit_reference emitted the list-item newline UNCONDITIONALLY (lines 2648-2650) BEFORE _enter_inline_concat_element, inserting a `\n` right after `text("(") + ` and stranding the + at end-of-line with no right operand -> 'expected expression'. Every OTHER inline visitor (visit_Text, visit_literal, visit_strong, visit_emphasis) guards its list-item newline behind the concat-context check so newline and + are mutually exclusive; visit_reference alone violated that invariant. C-style params (type-reference leads: `MyType *obj`) trigger it; Python-style (name leads: `obj: MyType`) do not -- hence the corpus fatal was C/C++-domain specific.
fix: In visit_reference, capture in_concat = (_inline_concat_context() is not None) BEFORE _enter_inline_concat_element (which suppresses the flag), then emit the list-item newline ONLY when not in_concat -- upholding the concat/newline mutual-exclusion invariant the other inline visitors already uphold. One central change to the single offending visitor; genuine inline + from bugs #3/#5/#8 untouched; plain list-item newline preserved for references outside any concat context.
verification: New tests/test_desc_signature_concat_render_gate.py PASSES with fix, FAILS pre-fix (git stash, both directions) with the exact 'expected expression' fatal. Minimal C-function fixture (leading cross-ref type resolved to an EXTERNAL URL via an offline intersphinx inventory so no Typst label is needed) emits `text("(") + link(...) + text("*") + ...` on one statement and compiles to %PDF. Fast suite 410 passed / 15 deselected (409 prior + 1 new; NO existing expectation updates -- none encoded the old stray-+ shape). black/ruff/mypy clean. Corpus scan: ZERO trailing-'+'-at-EOL across all 155 emitted .typ files. Corpus proof: PRE-FIX -> 'expected expression' (bug #9); POST-FIX -> DISTINCT fatal #10 'unclosed label' in usage/domains/c.typ (repr line 311) -- Typst labels/refs whose names contain '@' (C-domain anonymous entities `@data`/`@alias`, e.g. `link(<c.Data.@data.a>, ...)`; '@' is invalid in a Typst label). PRE-EXISTING (masked behind bug #9 at earlier line 107; my fix touched only newline emission, never label content). 3 files carry @-labels (usage/domains/c.typ, usage/restructuredtext/directives.typ, authors.typ). Reported, NOT fixed -- bounded scope (distinct construct/error class).
files_changed: [typsphinx/translator.py, tests/test_desc_signature_concat_render_gate.py, tests/fixtures/desc_signature_concat_render_gate/conf.py, tests/fixtures/desc_signature_concat_render_gate/index.rst]
