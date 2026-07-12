---
status: resolved
trigger: "Corpus gate fatal #16: TypstError: expected semicolon or line break at latex.typ:2382 (also :2463) -- `text(\"Text styling commands:\")table(` -- a docutils table (emitted as table(columns: N, table.header(...), ...)) nested inside a bullet-list item, juxtaposed against the list item's lead-in inline text with NO separator. visit_table/depart_table are the ONE block visitor still omitted from the list-item leading-separator pattern already applied to bullet_list, literal_block, definition_list, field_list (bug #12), block_quote (bug #11). 2 occurrences, 1 file (latex.typ)."
created: 2026-07-12T12:47:56
updated: 2026-07-12T12:47:56
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "visit_table (translator.py:1885) and depart_table (translator.py:1925) have NO in_list_item/list_item_needs_separator guard, unlike every other block visitor (bullet_list/literal_block/definition_list/block_quote/field_list, all fixed under bug #4/#11/#12's pattern). When a table follows a sibling paragraph/inline text inside a list item, depart_table's table(\\n  columns: ...) (body.append at line 1935) is emitted directly into the outer list item's code-mode content block, abutting the preceding text's closing ) with no separator -> text(\"Text styling commands:\")table( -> Typst 'expected semicolon or line break'."
  confirming_evidence:
    - "Corpus fatal at latex.typ:2382 (and :2463, 2 occurrences 1 file) shows the exact juxtaposition text(\"Text styling commands:\")table( -- byte-matches the established bug #4/#11/#12 juxtaposition shape."
    - "translator.py 1885-1958: visit_table body is `self.in_table = True; self.table_cells = []; self.table_colcount = 0` -- no in_list_item/list_item_needs_separator check. depart_table emits table(...) via self.body.append directly (comment at 1934: 'Use self.body.append directly to avoid routing to table_cell_content') but never sets list_item_needs_separator = True for a following sibling, and the emission has no leading-separator guard."
    - "visit_block_quote (2104-2138) and visit_field_list (3828-3855) both have the exact leading-\\n-on-visit + flag-set-on-depart pattern already, confirming table was the one remaining omission per the bug report."
  falsification_test: "If, after adding the guard to visit_table (leading \\n via self.body.append -- NOT self.add_text, since add_text would misroute into a stale table_cell_content list once in_table is True and table_cell_content exists from a prior table -- when in_list_item and list_item_needs_separator, before self.in_table = True is set) and depart_table (set list_item_needs_separator = True when in_list_item), a minimal fixture (bullet-list item = lead-in text + table) STILL emits text(...)table( juxtaposed OR still fails typst.compile with 'expected semicolon or line break', the hypothesis is wrong."
  fix_rationale: "Mirror the exact established block-visitor pattern (bug #4/#11/#12's block_quote/field_list/definition_list): visit_table emits a leading \\n when (in_list_item and list_item_needs_separator) and clears the flag; depart_table sets list_item_needs_separator = True when in_list_item. Top-level (non-list-item) tables are unaffected because in_list_item is False there -- both new code paths are gated on in_list_item. CRITICAL DEVIATION from the block_quote/field_list precedent: must use self.body.append (not self.add_text) for the guard's newline, because visit_table is about to set self.in_table = True, and add_text() routes to self.table_cell_content instead of self.body whenever in_table is True AND table_cell_content already exists as an instance attribute (true for the 2nd+ table encountered in a document) -- exactly the pitfall depart_table's own existing comment (line 1934) warns about for its own table( emission."
  blind_spots: "Have not yet run the minimal fixture through typst.compile() to confirm pre-fix failure and post-fix pass -- doing that next. Have not yet re-run the full slow corpus gate to confirm GATE-02 goes green or reveals the next fatal. Have not yet confirmed whether the guard must fire before or after self.in_table=True is set -- placing it before is safest per fix_rationale."

hypothesis: table nested in a list item after a paragraph emits `table(` with no leading separator because visit_table/depart_table omit the in_list_item/list_item_needs_separator guard present on every other block visitor.
test: add list-item separator guard to visit_table/depart_table (guard placed BEFORE self.in_table=True is set, using self.body.append not self.add_text) mirroring visit_block_quote/visit_field_list; build minimal fixture; fast suite; corpus gate
expecting: table nested in a list item after inline text emits a leading \n before table(; compiles to %PDF; corpus gate GREEN or advances to next distinct fatal
next_action: DONE. Fix applied to typsphinx/translator.py (visit_table/depart_table). Minimal fixture confirmed pre-fix failure (byte-matching corpus fatal) and post-fix pass (typst.compile() -> %PDF, 18247 bytes). Top-level table confirmed byte-unchanged (diff of pre/post -b typst output identical). Regression test tests/test_table_in_list_item_render_gate.py confirmed FAILS pre-fix (exact "expected semicolon or line break") and PASSES post-fix. Next: run fast suite, lint/type checks, then re-run slow corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; a table nested in a list item, following lead-in text, emits valid separated Typst statements.
actual: "Typst compilation failed: TypstError: expected semicolon or line break" at latex.typ:2382 (also :2463) -- `text("Text styling commands:")table(` -- table juxtaposed against preceding inline text inside a bullet-list item.
errors: "TypstError: expected semicolon or line break"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after bugs #1-#15 unblocked the compile path (sixteenth fatal in the fix-forward campaign).

## Eliminated

## Evidence

- timestamp: 2026-07-12T12:47:56
  checked: typsphinx/translator.py visit_table/depart_table (1885-1958) vs. visit_block_quote/depart_block_quote (2104-2153) and visit_field_list/depart_field_list (3828-3855)
  found: table visitors have NO in_list_item/list_item_needs_separator guard on visit, and depart_table never sets list_item_needs_separator=True; block_quote and field_list (fixed under bug #11/#12) both have the leading-newline-on-visit + flag-set-on-depart pattern. Also confirmed depart_table's own existing comment (line 1934, "Use self.body.append directly to avoid routing to table_cell_content") documents the exact add_text-misrouting pitfall that the new guard must also avoid.
  implication: Confirms root cause and the exact fix site; also confirms the guard must use self.body.append (not self.add_text) and must be placed before self.in_table = True is set in visit_table.

## Resolution

root_cause: visit_table/depart_table (typsphinx/translator.py) were omitted from the bug #4 list-item block-visitor separator sweep. visit_table set in_table/table_cells/table_colcount with no in_list_item/list_item_needs_separator guard, and depart_table (which emits the actual table( text, since table cells are collected between visit/depart and only rendered on depart) never set list_item_needs_separator=True. So when a table follows a sibling lead-in text inside a list item, depart_table's table(\n  columns:... abuts the preceding text's closing ) with no separator -> text("Text styling commands:")table( -> Typst "expected semicolon or line break".
fix: visit_table now emits a leading \n (and clears list_item_needs_separator) when in_list_item and list_item_needs_separator, mirroring visit_block_quote/visit_field_list -- placed BEFORE self.in_table=True is set and using self.body.append directly (NOT self.add_text), because add_text() routes to self.table_cell_content whenever in_table is True and table_cell_content already exists as a stale instance attribute from a prior table -- the same misrouting pitfall depart_table's own table( emission already avoids per its existing comment. depart_table now sets list_item_needs_separator=True when in_list_item so a following sibling separates. Top-level (non-list-item) tables are unaffected -- both new code paths are gated on in_list_item, which is False at top level (confirmed via byte-diff of a top-level-table fixture built before/after the fix: identical). ONE file: typsphinx/translator.py (visit_table/depart_table, 2 guard blocks added).
verification: New tests/test_table_in_list_item_render_gate.py PASSES with fix, FAILS pre-fix (git stash) with the exact "expected semicolon or line break" fatal (text("Text styling commands:")table( juxtaposition, byte-matching the corpus fatal shape at latex.typ:2382/:2463). Confirmed via direct scratchpad reproduction too (typst.compile() succeeds post-fix, 18247 bytes for the minimal fixture; 34902-byte PDF for the full test fixture, %PDF magic bytes confirmed). Fast suite: 418 passed / 15 deselected (417 prior + 1 new; NO existing expectation updates needed). black/ruff/mypy clean on all changed files (typsphinx/translator.py, tests/test_table_in_list_item_render_gate.py, tests/fixtures/table_in_list_item_render_gate/conf.py).

  Corpus gate re-run (uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s): bug #16's exact fatal is GONE -- rebuilt usage/domains/latex.typ (byte-confirmed via a manual `-b typst` build of the full cached corpus) no longer contains `text("Text styling commands:")table(`; the leading-separator newline is present. GATE-02 is NOT yet green: the gate now fails on a DISTINCT fatal #17 (confirmed via manual `-b typst` build of the full corpus + grep across every generated .typ file):

  TypstError: label `<c._u40_alias.data>` does not exist in the document

  Construct: `.. c:alias:: data` / `f` (usage/domains/c.rst:236-237, live directive
  use -- the `.. c:alias::` block inside the "Aliasing Declarations" section,
  preceded by `.. c:namespace-push:: @alias` at c.rst:207). Sphinx's C-domain
  alias mechanism synthesizes a copy of each aliased declaration's
  desc_signature and wraps its name in a same-document `reference` node
  (refid-based, no refuri) pointing back at the alias's own namespace-
  qualified id (`c.@alias.data` / `c.@alias.f`, sanitized by
  `_sanitize_label` to `c._u40_alias.data` / `c._u40_alias.f` per the
  existing @-encoding fix). depart_reference's refid branch (translator.py
  ~2848-2850) correctly emits `link(<c._u40_alias.data>, ...)` for this
  reference -- but the CORRESPONDING ANCHOR is never emitted anywhere:
  visit_desc_signature/depart_desc_signature (translator.py ~3653-3672) wrap
  the signature in strong({...}) and NEVER read/emit node["ids"] as a Typst
  `<label>` anchor (unlike visit_target/visit_title/depart_term, which do
  call _sanitize_label(node["ids"][0]) and emit a `[#metadata(none) <id>]`
  or `#label("id")` anchor). Confirmed via exhaustive grep of the full
  built corpus .typ tree: `<c._u40_alias.data>`/`<c._u40_alias.f>` appear
  ONLY inside `link(...)` calls (2 occurrences), never as an anchor
  definition anywhere in any file. One-line hypothesis: visit_desc_signature
  needs to emit a Typst label anchor from node["ids"] (mirroring the
  visit_target/depart_term pattern) so refid-based same-document references
  to API-declaration signatures (the c:alias construct being the one path
  in this corpus that produces such a same-document refid reference, as
  opposed to the far more common empty-URL or external #-fragment cases
  already handled) can resolve. Occurrence count: 2 broken-link occurrences
  (`data`, `f`), 1 file (usage/domains/c.typ:354/356), traced to 1 live
  directive use, 1 source file (usage/domains/c.rst:236-237). NOT fixed
  this session -- distinct bug class (desc_signature anchor emission gap,
  not a list-item separator issue), out of the assigned scope.
files_changed: [typsphinx/translator.py, tests/test_table_in_list_item_render_gate.py, tests/fixtures/table_in_list_item_render_gate/conf.py, tests/fixtures/table_in_list_item_render_gate/index.rst]
