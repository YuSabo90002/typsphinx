---
status: fixing
trigger: "Corpus gate fatal #4: TypstError: expected semicolon or line break at changes/1.6.typ:856 — `})par(` — a nested list({...}) immediately followed by a sibling par({...}) inside a list item, with no statement separator. 17 occurrences across 8 files, all identical `})par(`."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "`in_list_item` is a bare boolean with no save/restore across nested-list boundaries. When a list item contains [paragraph, nested list, paragraph], the nested list's `depart_list_item` (translator.py:1106) sets `in_list_item = False` unconditionally, clobbering the outer item's context. The trailing paragraph is then visited with `in_list_item == False`, so `visit_paragraph` does NOT skip par() wrapping (523) and emits `par({...})` as if it were a top-level paragraph — with no leading separator. It directly follows the nested `list(...)`'s closing `)` inside the outer content block `{...}`, producing `})par(`, a Typst code-mode syntax error (two juxtaposed statements need a newline/`;`). The FIRST paragraph in the same item correctly emits as bare `text(...)` because `in_list_item` was still True then."
  confirming_evidence:
    - "Minimal fixture (list item = para + nested bullet_list + para) emits byte-identical `})par({text(\"Paragraph after...\")})` — matching the corpus fatal at changes/1.6.typ:856."
    - "In the SAME emitted item, the first paragraph is `text(\"Outer item...\")` (unwrapped, in_list_item True) but the post-nested-list paragraph is `par({...})` (wrapped, in_list_item False). The only intervening event is the nested list, whose depart_list_item set in_list_item=False."
    - "depart_list_item (1094-1106) sets self.in_list_item = False with NO save of the prior value; visit_list_item (1070-1092) sets True with no save either. There is no stack — so nesting corrupts the flag."
  falsification_test: "If, after making visit_list_item/depart_list_item save+restore in_list_item via a stack, the fixture STILL emits `par(` (wrapped) for the trailing paragraph OR still fails typst.compile with 'expected semicolon or line break', the hypothesis is wrong."
  fix_rationale: "ONE central state-management fix: visit_list_item pushes the prior in_list_item onto a stack and sets True; depart_list_item pops+restores it. This makes in_list_item correctly reflect 'inside a list item content block' at arbitrary nesting depth. The trailing paragraph is then recognized as in-item → visit_paragraph skips par() (uniform with the first paragraph) → its text emits via visit_Text, which ALREADY inserts a `\\n` separator when `in_list_item and list_item_needs_separator` (661-662). This fixes the whole CLASS (list→par, list→list, par→list after a nested list, blockquote→par, etc.) because it restores the context that drives the existing list_item_needs_separator separator machinery — not just the one `})par(` shape."
  blind_spots: "Fix changes the trailing paragraph's emission from par({...}) to text(...) — but that is the ESTABLISHED behavior for paragraphs in list items (the first paragraph already emits text()), so it is a consistency fix, not a rendering regression from a working state (the current state does not compile). Deeper (>1 level) list nesting also relies on visit_bullet_list's single-attr _saved_* (not a stack) for is_first_list_item/list_item_needs_separator — pre-existing, separate, out of scope. If corpus surfaces a DISTINCT non-list content-block adjacency (e.g. blockquote sibling outside any list) after this, report it."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: add in_list_item save/restore stack in visit_list_item/depart_list_item; rebuild fixture; fast suite; corpus gate
expecting: fixture trailing paragraph emits `\ntext("Paragraph after...")` (separated), compiles to %PDF; corpus advances past changes/1.6.typ:856 `})par(`
next_action: Implement stack save/restore, add fast regression test, run fast suite + lint + corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; a nested list followed by a sibling paragraph inside a list item emits valid, separated Typst statements.
actual: "Typst compilation failed: TypstError: expected semicolon or line break" at changes/1.6.typ:856 — `})par(` — nested list(...) immediately followed by par(...) with no separator. 17 occurrences across 8 files (latex, usage/theming, usage/extensions/autodoc, usage/restructuredtext/basics, changes/{1.6,6.1,7.4,8.0}).
errors: "TypstError: expected semicolon or line break"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after bugs #1-#3 (asset-copy, target-label, def-list-term concat) unblocked the compile path.

## Eliminated

## Evidence

- timestamp: repro
  checked: Built minimal fixture (list item = paragraph + nested bullet_list + paragraph) via -b typst; inspected emitted index.typ
  found: "list({\ntext(\"Outer item...\")\nlist({...})par({text(\"Paragraph after...\")})" — nested list `)` immediately followed by `par(` with no separator. Byte-match to corpus fatal shape.
  implication: Root cause reproduced offline. First paragraph unwrapped (text), trailing paragraph wrapped (par) — proving in_list_item flipped to False across the nested list.

## Resolution

root_cause: in_list_item is a bare boolean with no nesting stack. A nested list's depart_list_item unconditionally sets it False, so a paragraph following a nested list inside the same outer list item is mis-classified as top-level → visit_paragraph emits par({...}) (instead of skipping wrapping like sibling paragraphs) with no leading separator, directly abutting the nested list's closing `)` inside the code-mode content block → `})par(` syntax error.
fix: Added an _list_item_stack (List[bool]) in __init__. visit_list_item pushes the prior in_list_item and sets True; depart_list_item pops+restores it (falls back to False if empty). This makes in_list_item correctly reflect "inside a list item content block" at any nesting depth. The trailing paragraph after a nested list is then recognized as in-item → visit_paragraph skips par() wrapping (uniform with the item's first paragraph) → its text emits via visit_Text, which already inserts a "\n" separator when (in_list_item and list_item_needs_separator). Central fix covering the whole block-adjacency class (list→par, par→list, list→list) via the existing separator machinery. ONE site: typsphinx/translator.py visit_list_item/depart_list_item + __init__.
verification: New tests/test_list_item_nested_block_render_gate.py PASSES with fix, FAILS pre-fix (git stash) with the exact `expected semicolon or line break` fatal on `})par(`. Minimal fixture emits `})` + newline + `text(...)` (separated) and compiles to %PDF. Fast suite 398 passed / 15 deselected (397 prior + 1 new; NO existing expectation updates needed). black/mypy/ruff clean. Corpus gate advanced PAST changes/1.6.typ:856 `})par(`; now RED on a DISTINCT fatal #5: `TypstError: expected comma` — def-list TERMs containing a reference(link)/strong/emphasis child adjacent to a text/literal child juxtapose with NO `+` (bug #3's documented blind spot: _in_term concat is wired only into visit_Text + visit_literal, not visit_emphasis/visit_strong/visit_reference). ~20+ occurrences across 4 files (extdev/logging.typ, internals/contributing.typ, usage/configuration.typ [~17], usage/restructuredtext/directives.typ). Representative: extdev/logging.typ:63 `terms.item(strong({text("type")}) + text(", ")strong({ + text("*subtype*")}), ...)` — `text(", ")strong(` juxtaposition (plus a stray leading `+` leaking into the strong content block). Reported, NOT fixed — bounded scope (distinct inline class, separate from the assigned block-level class).
files_changed: [typsphinx/translator.py, tests/test_list_item_nested_block_render_gate.py, tests/fixtures/list_item_nested_block_render_gate/conf.py, tests/fixtures/list_item_nested_block_render_gate/index.rst]
