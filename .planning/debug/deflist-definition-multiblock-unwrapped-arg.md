---
status: resolved
trigger: "Corpus gate fatal #7: TypstError: expected comma at usage/restructuredtext/directives.typ:1718:237 — a def-list DEFINITION with multiple block children (par + code fence + list) passed UNWRAPPED as terms.item's 2nd arg; Typst reads par({...}) as the whole arg then expects a comma."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "depart_definition ''.join()s a definition's block children (par({...}) + blank-line + codly(...) + fence + blank-line + list({...})) into a bare, blank-line-separated statement blob and passes it UNWRAPPED as terms.item(TERM, DEF)'s 2nd argument in depart_definition_list. Blank-line separation of sequential content statements is valid ONLY at document top level, not inside a function argument list. Typst parses the first statement par({...}) as the complete 2nd argument, then expects a comma but finds the next bare statement codly(...) -> 'expected comma'."
  confirming_evidence:
    - "Minimal fixture (term with para + code-block + bullet list) emits verbatim: terms.item(text(\"term one\"), par({...})\\n\\ncodly(...)\\n```...```\\n\\nlist({...})) — the 2nd arg par({...}) directly followed by a blank line + codly(...) with no comma. Byte-shape match to corpus fatal directives.typ:1718."
    - "typst.compile of the emitted index.typ -> FAIL 'expected comma'. Wrapping the definition arg as {par({...})\\n\\ncodly(...)\\n```...```\\n\\nlist({...})} -> COMPILE OK, %PDF (21551 bytes). Single-block definition wrapped {par({...})} also COMPILE OK."
    - "Assembly site depart_definition_list (translator.py:1391-1394) joins f'terms.item({term}, {definition})' with definition = raw ''.join of block children, no enclosing content block."
  falsification_test: "If, after wrapping the definition arg in { ... } in the terms.item assembly, the fixture STILL emits an unwrapped multi-statement 2nd arg OR still fails typst.compile with 'expected comma', the hypothesis is wrong."
  fix_rationale: "Inside a Typst content block { ... } sequential content statements auto-join into a single content value — a valid single argument. Wrapping ONLY the definition (2nd) arg of terms.item at the assembly site addresses the ROOT (definition assembled as bare top-level statements instead of one content value) and clears the whole at-risk class (multi-block definitions across ~16 corpus files) at once. The TERM (1st arg) + concat path (bug #3/#5) and the list-item block-separation path (bug #4) are untouched — the inner separators of the definition (already blank-line/newline) are CORRECT inside { } (Typst joins them); we add only the enclosing braces. A defensive guard avoids double-wrapping a buffer that is already a single {...} content value."
  blind_spots: "Wrapping is applied unconditionally except when the buffer is already a single balanced {...} block. In the current translator no definition child emits a bare top-level {...} (all start with a function name or a backtick fence), so the guard is defensive. Empty definitions now emit {} (valid empty content) instead of a bare empty 2nd arg. If the corpus surfaces a DISTINCT fatal after this (non-definition content-block adjacency), report it."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: wrap the definition (2nd) arg in { ... } at the terms.item assembly; rebuild fixture; fast suite; corpus gate
expecting: fixture emits terms.item(TERM, { par(...) ... codly(...) ... list(...) }); compiles to %PDF; corpus advances past directives.typ:1718 comma fatal
next_action: Implement wrap helper + guard in depart_definition_list, add fast regression test, run fast suite + lint + corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; a def-list definition with multiple block children emits a single valid content argument to terms.item.
actual: "Typst compilation failed: TypstError: expected comma" at usage/restructuredtext/directives.typ:1718:237 — a multi-block definition passed unwrapped as terms.item's 2nd arg. >=13 error locations in directives.typ; ~16 of 20 compiled .typ files with terms.item( also contain a code fence (at-risk multi-block definitions).
errors: "TypstError: expected comma"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after bugs #1-#6 unblocked the compile path.

## Eliminated

## Evidence

- timestamp: repro
  checked: Built minimal fixture (term = paragraph + code-block + bullet list, plus a plain single-paragraph term) via -b typst; inspected emitted index.typ
  found: terms.item(text("term one"), par({...})\n\ncodly(...)\n```python...```\n\nlist({...})) — 2nd arg par({...}) followed by blank-line-separated bare statements, no comma. Byte-shape match to corpus fatal.
  implication: Root cause reproduced offline. Definition assembled as bare top-level statements, not one content value.

- timestamp: compile-direction
  checked: typst.compile of emitted index.typ (unwrapped) vs manually-wrapped definition args (typst 0.13-era API)
  found: unwrapped -> 'expected comma'; wrapping each definition arg in { ... } (both the multi-block and the single-block par({...})) -> COMPILE OK, %PDF 21551 bytes.
  implication: Enclosing content-block { } is the exact fix; single-block wrapping is harmless and renders identically.

## Resolution

root_cause: A def-list definition's block children are ''.join'd in depart_definition into a bare, blank-line-separated statement blob and passed UNWRAPPED as terms.item's 2nd argument (depart_definition_list assembly). Blank-line separation of sequential content statements is valid only at document top level; inside a function-argument position Typst reads the first statement par({...}) as the complete argument, then expects a comma at the next bare statement -> 'expected comma'.
fix: depart_definition_list now wraps the definition (2nd) arg of every terms.item in a `{ ... }` content block via new helper _wrap_definition_arg (with _is_single_content_block guard to avoid double-wrapping an already-single-{...} buffer and to emit {} for an empty definition). Inside `{ }` Typst auto-joins the definition's sequential block statements (par + code fence + list) into one content value -- a valid single argument. TERM (1st arg) +-concat path and list-item block-separation path untouched. ONE site: typsphinx/translator.py depart_definition_list + 2 helpers.
verification: New tests/test_deflist_definition_multiblock_render_gate.py PASSES with fix, FAILS pre-fix (git stash) with the exact 'expected comma' fatal. Fast suite 408 passed / 15 deselected (407 prior + 1 new; NO existing expectation updates needed). black/mypy/ruff clean. Corpus proof: usage/configuration.typ went 0 -> 30 `, {par(` wrapped definitions (bug #7 cleared); corpus advanced PAST directives.typ:1718 'expected comma'. Now RED on DISTINCT fatal #8: 'expected semicolon or line break', 16 occurrences ALL in usage/configuration.typ -- a confval directive's :default:/:type: FIELD-BODY paragraph emitted UNWRAPPED (no par()) whose inline children juxtapose: 15x `text("The value of ")strong({...})` (text+strong, no +/newline), 1x (line 2009) a bare paragraph abutting a following terms(...). Proven independent of this fix: identical 15 occurrences at identical lines pre- and post-fix (git stash diff). Same inline-juxtaposition class as bug #3/#5 surfacing in the field_body-paragraph context. Reported, NOT fixed -- bounded scope (distinct construct/context).
files_changed: [typsphinx/translator.py, tests/test_deflist_definition_multiblock_render_gate.py, tests/fixtures/deflist_definition_multiblock_render_gate/conf.py, tests/fixtures/deflist_definition_multiblock_render_gate/index.rst]
