---
status: resolved
trigger: "Corpus gate fatal #11: TypstError: expected semicolon or line break. TWO sub-constructs: (a) reference-with-adjacent-target markup wrapper (_in_reference_with_target) at usage/advanced/intl.typ:27 [#link(...) #label(...)]text(...) juxtaposed with no separator; (b) nested list(...) inside list item juxtaposed with following sibling at changes/6.1.typ:143."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "(a) A FIGURE CAPTION renders its inline children into a `{...}` code block (depart_figure) but visit_caption sets NEITHER in_paragraph NOR any concat/list-item context, so _add_paragraph_separator never fires and ALL adjacent inline caption expressions juxtapose (`text(...)[wrapper]text(...)`, and even `text(...)emph(...)`) -> 'expected semicolon or line break'. The reference-with-target markup wrapper itself is NOT broken: in a real paragraph (in_paragraph=True) the SAME wrapper renders correctly (leading `\\n` before `[` via visit_reference's _add_paragraph_separator, trailing `\\n` before the next sibling via that sibling's _add_paragraph_separator). The caption simply fails to establish that context. (b) visit_block_quote emits `quote[`/`quote(` with NO leading list-item separator and depart_block_quote does not set list_item_needs_separator -- block_quote was omitted from bug #4's block-visitor separator pattern. A block_quote following inline content in a list item juxtaposes: `text(\" functions:\")quote[`."
  confirming_evidence:
    - "Minimal figure-caption repro emits `caption: {text(\"...by\\n\")[#link(\"https://plantuml.com\", text(\"plantuml\"))\\n#label(\"plantuml\")]text(\".)\")}` -- byte-shape match to corpus intl.typ:27. typst.compile of that + of `{text(\"a \")emph({...})text(\" c\")}` BOTH fail 'expected semicolon or line break'; newline- or +-separated variants compile OK. A real paragraph with the SAME `plantuml <url>`_ named-link emits `par({text(\"...before \")\\n[#link(...)\\n...]\\ntext(\" and after\")})` and compiles -- proving the wrapper works when in_paragraph is set."
    - "Minimal block-quote-in-list-item repro (matching changes/6.1.rst:60-82) emits `text(\" functions:\")quote[` juxtaposed -> typst.compile 'expected semicolon or line break'. Patching a single `\\n` between `text(\" functions:\")` and `quote[` makes the WHOLE file compile to %PDF (23420 bytes)."
    - "visit_block_quote (2074-2090) emits quote[/quote( with no `if in_list_item and list_item_needs_separator: add_text('\\n')` guard and depart_block_quote (2092-2105) never sets list_item_needs_separator -- unlike every other block visitor (bullet_list 1128, literal_block, definition_list) fixed in bugs #4/#8."
  falsification_test: "If, after (a) setting in_paragraph=True (save/restore) in visit_caption's figure branch and (b) adding the list-item leading-separator guard to visit_block_quote + the depart marking, either the caption STILL juxtaposes the wrapper/emph OR the block_quote STILL abuts the preceding text OR either still fails typst.compile, the hypothesis is wrong."
  fix_rationale: "(a) Route the caption through the EXISTING paragraph separator machinery: a figure caption IS a paragraph of inline content, so visit_caption sets in_paragraph=True/paragraph_has_content=False (saved+restored in depart_caption). _add_paragraph_separator then newline-separates every inline sibling exactly as in a real paragraph -- which ALREADY handles the reference-with-target wrapper correctly (proven). No new scheme; single-text captions are byte-unchanged (first element needs no separator). (b) Reuse bug #4's block-visitor pattern: visit_block_quote emits a leading `\\n` when in_list_item and list_item_needs_separator; depart_block_quote sets list_item_needs_separator=True. Top-level block quotes (in_list_item False) are byte-unchanged."
  blind_spots: "(a) applies only to the in_figure caption branch (buffer-swap); the code-block caption (SkipNode) and any non-figure caption keep their current path. If a caption ever contained a nested block child (docutils captions are single-paragraph inline, so it cannot) in_paragraph would still be correct. (b) The markup-mode `list(...)` inside `quote[...]` (no `#` prefix) is a separate rendering-fidelity question but PARSES/compiles fine (empirically) -- not this fatal. Both verified via corpus gate re-run."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: (a) set in_paragraph in visit_caption/depart_caption figure branch; (b) add list-item separator guard to visit/depart_block_quote; rebuild repros; fast suite; corpus gate
expecting: caption emits newline-separated wrapper; block_quote emits leading `\n` in list item; both compile to %PDF; corpus advances past intl.typ:27 / changes/6.1.typ:143
next_action: Edit translator.py (visit_caption/depart_caption ~1709-1731; visit_block_quote/depart_block_quote 2074-2105), add fast regression test, run fast suite + lint + corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal; a reference-with-adjacent-target inline wrapper and a nested list inside a list item each separate from a following sibling.
actual: "Typst compilation failed: TypstError: expected semicolon or line break". (a) usage/advanced/intl.typ:27 `caption: {…[#link("https://plantuml.com", text("plantuml")) #label("plantuml")]text(".)")}` — wrapper `]` juxtaposed with `text(".)")`. (b) changes/6.1.typ:143 `list({…})]` … `})` — nested list juxtaposed with sibling.
errors: "TypstError: expected semicolon or line break"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate after bugs #1-#10.

## Eliminated

## Evidence

- timestamp: repro-a
  checked: Built minimal figure with a named external link `plantuml <https://plantuml.com>`_ + trailing `.)` in the caption; inspected emitted .typ + typst.compile.
  found: caption `{text("...by\n")[#link("https://plantuml.com", text("plantuml"))\n#label("plantuml")]text(".)")}` -- wrapper juxtaposed with text on BOTH sides. Also a `text(...)emph(...)text(...)` caption juxtaposes. typst.compile of both FAIL 'expected semicolon or line break'. Byte match to corpus intl.typ:27.
  implication: The caption `{...}` code block establishes no inline separator context; visit_caption sets neither in_paragraph nor a concat context.

- timestamp: paragraph-control
  checked: Same `plantuml <url>`_ named link placed in a normal paragraph.
  found: par({text("...before ")\n[#link("https://plantuml.com", \ntext("plantuml"))\n#label("plantuml")]\ntext(" and after...")}) -- fully separated via _add_paragraph_separator, compiles fine.
  implication: The reference-with-target wrapper is NOT broken; it works whenever in_paragraph is True. Root cause of (a) = caption not setting in_paragraph.

- timestamp: repro-b
  checked: Built minimal `* ``sphinx.util`` functions:` list item with an indented block_quote containing nested lists (matching changes/6.1.rst:60-82); inspected + compiled.
  found: `text(" functions:")quote[` juxtaposed -> typst.compile 'expected semicolon or line break'. Inserting a single `\n` before `quote[` compiles the WHOLE file to %PDF (23420 bytes).
  implication: Root cause of (b) = visit_block_quote emits quote[ with no list-item leading separator (omitted from bug #4's block-visitor pattern); depart never sets list_item_needs_separator.

## Resolution

root_cause: TWO distinct constructs, same 'expected semicolon or line break' parse class, both masked behind bug #10. (a) A figure caption renders its inline children into a `{...}` code block (depart_figure) but visit_caption set NEITHER in_paragraph NOR any concat/list-item context, so _add_paragraph_separator never fired -> adjacent inline caption expressions juxtaposed (the named external link `plantuml <url>`_ produces a reference-with-target markup wrapper `[#link(...) #label(...)]` juxtaposed on BOTH sides with the surrounding text, and even a plain text+emph caption juxtaposes). The reference-with-target wrapper itself is correct -- it renders fine in a real paragraph (in_paragraph=True); the caption simply failed to establish that context. (b) visit_block_quote emitted `quote[`/`quote(` with no list-item leading-separator guard and depart_block_quote never set list_item_needs_separator -- the one block visitor omitted from bug #4's block-visitor pattern; a block_quote after inline content in a list item juxtaposed (`text(" functions:")quote[`).
fix: (a) visit_caption's figure branch sets in_paragraph=True/paragraph_has_content=False (saved+restored in depart_caption), routing the caption through the EXISTING _add_paragraph_separator newline machinery (single-text captions byte-unchanged). (b) visit_block_quote emits a leading `\n` when in_list_item and list_item_needs_separator; depart_block_quote sets list_item_needs_separator=True (top-level block quotes byte-unchanged). ONE file: typsphinx/translator.py (visit_caption/depart_caption + visit_block_quote/depart_block_quote).
verification: New tests/test_ref_target_nested_list_render_gate.py PASSES with fix, FAILS pre-fix (git stash translator.py) with the exact 'expected semicolon or line break' fatal. Both fixes proven independently load-bearing (disabling ONLY the block_quote guard, caption fix present, still fails the block-quote repro). Fast suite 412 passed / 15 deselected (411 prior + 1 new; NO existing expectation updates). black/ruff/mypy clean. Corpus gate: bugs #11a (`]text(` caption wrapper) and #11b (`)quote[` block_quote) BOTH cleared corpus-wide (0 hits each across all 155 emitted leaves; corpus advanced PAST intl.typ:27 and changes/6.1.typ:143). NOT GATE-02 green. Next distinct fatal #12 = TypstError 'expected semicolon or line break' at usage/advanced/intl.typ:391, `text("For example:")strong(` -- a docutils FIELD LIST (`:Organization ID:` ...) nested inside a numbered-list item, following a paragraph: visit_field_name appends `strong(` (the bold field-name label) with NO in_list_item/list_item_needs_separator guard, juxtaposing against the preceding paragraph text. DISTINCT construct (field_list/field_name visitor, not caption/block_quote); PRE-EXISTING (masked behind #11's earlier abort). 1 occurrence, 1 file (intl.typ:391) across the whole corpus. Reported, NOT fixed -- bounded scope. One-line hypothesis: visit_field_list/visit_field_name bypass the list-item separator machinery (like bug #4/#8's def-list fix) so a field list following inline content in a list item juxtaposes.
files_changed: [typsphinx/translator.py, tests/test_ref_target_nested_list_render_gate.py, tests/fixtures/ref_target_nested_list_render_gate/conf.py, tests/fixtures/ref_target_nested_list_render_gate/index.rst, tests/fixtures/ref_target_nested_list_render_gate/_static/pixel.png]
