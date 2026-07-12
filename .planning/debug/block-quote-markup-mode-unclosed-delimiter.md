---
status: resolved
trigger: "Corpus gate fatal #15: TypstError: unclosed delimiter. visit_block_quote emits markup `quote[...]`; children are code-mode calls (par({text(...)}), raw(...), link(...)) treated as LITERAL PROSE inside the markup block; a lone markup-special char (e.g. `_` in raw(\"_t\")) opens an inline emphasis span that never closes -> unclosed delimiter. Reproduces in development/html_themes/index.typ; 10 files / 11 quote[ occurrences corpus-wide."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "visit_block_quote emits a Typst MARKUP-mode trailing content block `quote[ ... ]`. But every body child is a CODE-MODE function call (par({text(...)}), raw(...), link(...)). Inside markup `[...]` those bytes are LITERAL PROSE, and any markup-special char in a string literal -- e.g. the lone `_` in raw(\"_t\") (Sphinx's `_t` static-template suffix) -- opens an inline-emphasis span that never closes -> TypstError: unclosed delimiter. Fix: emit quote(block: true, { <children> }) so the body is a CODE-MODE content block where the child calls are real calls and string-literal chars cannot open markup spans."
  confirming_evidence:
    - "Minimal typst.compile: `#{ quote[par({text(\"Prefix \")\\nraw(\"_t\")\\ntext(\" suffix\")})\\n] }` FAILS with the exact `TypstError: unclosed delimiter` -- byte-shape match to the current translator emission for a block quote containing an inline literal ``_t``."
    - "The code-mode form `#{ quote(block: true, {par({...raw(\"_t\")...})\\n}) }` COMPILES to %PDF. Attribution form `quote(block: true, {body}, attribution: [attr])` (positional body first, named attribution second) COMPILES. Nested-list body `quote(block: true, {list({text(\"_alpha\")}, ...)})` COMPILES (bonus: bug #11's deferred markup-mode list(...) fidelity issue also resolved)."
    - "base.typ + the 4 @preview imports (codly, codly-languages, mitex, gentle-clues) define NO `quote`; the minimal repros used NO imports and compiled -> confirms native Typst `quote(block, quotes, attribution, body)`."
  falsification_test: "If, after emitting quote(block: true, { ... }) (with attribution closing the body block and appending a named attribution arg), any block-quote fixture (plain / markup-special-char body / in-list-item / with-attribution) still fails typst.compile OR the corpus still aborts on `unclosed delimiter` at a block quote, the hypothesis/fix is wrong."
  fix_rationale: "The `{ ... }` code-mode content block is exactly how the rest of this translator wraps block content (par({...}) bug, definition wrap bug #7, footnote buffer). It evaluates child calls as real calls, so markup-special chars in their string args are inert -- addressing the root cause (mode mismatch), not the symptom (a specific `_`). block: true preserves block-quote rendering (more correct than the old markup `quote[...]` which is block:false)."
  blind_spots: "Attribution arg-order (positional body then named attribution) relies on Typst accepting a named arg after a positional -- verified compiling. A block quote whose body, inside a list item, emits BARE inline content (par() skipped when in_list_item) must still auto-join inside `{ }` -- verified via the list-body repro. Both re-checked end-to-end by the fast render gate + corpus gate."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: edit visit/depart_block_quote + visit/depart_attribution to code-mode form; update 3 unit tests + ref_target render gate; add fast regression gate; fast suite; lint; corpus gate
expecting: block quotes with markup-special-char bodies compile to %PDF; corpus advances past development/html_themes/index.typ
next_action: Edit translator.py visit_block_quote (2104-2131)/depart_block_quote (2133-2151)/visit_attribution (2153-2161)/depart_attribution (2163-2171)

## Symptoms

expected: -b typstpdf on doc/ corpus compiles through with no fatal; a block quote whose body contains markup-special chars renders as a block quote.
actual: "Typst compilation failed: TypstError: unclosed delimiter" at final PDF compile; site translator.py visit_block_quote (~2131 quote[) / depart_block_quote (~2146 ]).
errors: "TypstError: unclosed delimiter"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate after bugs #1-#14.

## Eliminated

## Evidence

- timestamp: repro-semantics
  checked: Compiled 4 minimal .typ via typst.compile -- (1) old markup quote[par({..raw("_t")..})], (2) quote(block: true, {..}), (3) quote(block: true, {body}, attribution: [attr]), (4) quote(block: true, {list({text("_alpha")}, ..)}).
  found: (1) FAIL TypstError: unclosed delimiter (exact corpus fatal). (2)(3)(4) OK magic=b'%PDF'.
  implication: Root cause confirmed = markup-mode body treats code-mode children as literal prose; lone markup-special char opens stray span. Code-mode { ... } body compiles; attribution positional-then-named works; nested list() body now a real call.

## Resolution

root_cause: visit_block_quote emitted the Typst MARKUP-mode trailing content block `quote[ ... ]`. Every body child is a code-mode function call (par({text(...)}), raw(...), link(...)); inside markup `[...]` those bytes are LITERAL PROSE, so a lone markup-special char in a child string literal (e.g. the `_` in raw("_t") -- Sphinx's `_t` static-template suffix) opened an inline-emphasis span that never closed -> TypstError: unclosed delimiter. 10 files / 11 quote[ occurrences corpus-wide.
fix: Emit a CODE-MODE body -- quote(block: true, { <children> }) -- so the child calls are real calls and string-literal chars are inert. visit_block_quote emits `quote(block: true, {` (identical for both cases); depart_block_quote closes `})\n\n` (no attribution) or `)\n\n` (attribution, since visit_attribution already closed the body block). visit_attribution now emits `}, attribution: [` (close body block, open named attribution arg -- positional body then named arg, accepted by Typst); depart_attribution unchanged (`]`). block: true keeps block-quote rendering. bug #11's list-item leading-separator guard (leading `\n` when in_list_item and list_item_needs_separator) and the depart list_item_needs_separator=True marking are PRESERVED verbatim. ONE production file: typsphinx/translator.py (visit/depart_block_quote + visit_attribution).
verification: New tests/test_pdf_render_gate.py::TestBlockQuoteMarkupModeRenderGate (fast, offline) PASSES with fix, FAILS pre-fix (git stash of translator.py -> source-level catches `quote[par(`; the compile would also abort with `unclosed delimiter`). Fixture has a plain block quote, a block-quote-in-list-item (composes bug #11's separator), and a block quote with attribution -- each carrying an inline literal ``_t``. Updated 3 pre-existing unit tests (test_translator.py: block_quote_conversion/with_attribution/nested) and the bug #11 gate (test_ref_target_nested_list_render_gate.py) that encoded the old quote[...] markup emission. Fast suite: 417 passed, 15 deselected (416 prior + 1 new gate; 4 pre-existing expectations updated). black/ruff/mypy clean. BONUS: bug #11's deferred markup-mode list(...) fidelity issue also resolved (nested list now a real call). NOT GATE-02 green. Corpus advanced PAST the block-quote unclosed-delimiter fatal to a NEXT DISTINCT fatal #16: TypstError 'expected semicolon or line break' at latex.typ:2382 (and :2463), source latex.rst -- `text("Text styling commands:")table(` : a docutils TABLE (emitted table(columns: N, table.header(...), ...)) nested inside a bullet-list item juxtaposes against the list item's lead-in inline text with NO separator. DISTINCT construct (visit_table, not block_quote); PRE-EXISTING (masked behind #15's earlier abort). 2 occurrences, 1 file (latex.typ) corpus-wide. Minimal repro `#{ list({text("x:")table(columns:2, table.header(...), ...)}) }` FAILS 'expected semicolon or line break'; newline-separated form compiles. One-line hypothesis: visit_table (1885) is the one block visitor omitted from the list-item leading-separator pattern (bullet_list/literal_block/definition_list/field_list/block_quote all have the `if in_list_item and list_item_needs_separator: add_text("\n")` guard), so a table following inline content inside a list item juxtaposes. Reported, NOT fixed -- bounded scope (bug #15 only).
files_changed: [typsphinx/translator.py, tests/test_pdf_render_gate.py, tests/test_translator.py, tests/test_ref_target_nested_list_render_gate.py, tests/fixtures/block_quote_markup_render_gate/conf.py, tests/fixtures/block_quote_markup_render_gate/index.rst]
