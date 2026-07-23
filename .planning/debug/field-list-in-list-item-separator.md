---
status: resolved
trigger: "Corpus gate fatal #12: TypstError: expected semicolon or line break at usage/advanced/intl.typ:391 -- `text(\"For example:\")strong(` -- a field list (:Organization ID:/:Project ID:/:Project URL:) nested inside an enumerated-list item, following a 'For example:' paragraph. visit_field_name appends strong( with NO list-item separator guard, juxtaposing directly against the preceding paragraph text in code mode. SAME class as bug #4/#8 (block-level element inside a list item needs the in_list_item + list_item_needs_separator leading newline); field-list block visitors were omitted from that pattern. 1 occurrence, 1 file -- confirmed the ONLY remaining )strong( juxtaposition in the corpus."
created: 2026-07-12T11:52:10
updated: 2026-07-12T11:52:10
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "visit_field_list (translator.py:3801) is a bare `pass` with no list-item separator guard, unlike every other block visitor (bullet_list/literal_block/definition_list/block_quote, all fixed under bug #4/#8's pattern). When a field_list is the second block sibling in a list item (paragraph, then field_list), depart_field_name's `strong(` (3836) is emitted directly into the outer list item's code-mode content block, abutting the preceding paragraph's closing `)` with no separator -> `text(\"For example:\")strong(` -> 'expected semicolon or line break'."
  confirming_evidence:
    - "Real corpus source (usage/advanced/intl.rst:245-256): an enumerated list item (`#.`) containing two paragraphs then a field list (:Organization ID:/:Project ID:/:Project URL:) with no directive/blank separation beyond normal RST -- docutils nests the field_list as a direct sibling block inside the list_item."
    - "translator.py:3801-3805 visit_field_list body is `pass` -- no in_list_item/list_item_needs_separator check, unlike visit_block_quote (2108-2109), visit_definition_list (1396-1398), visit_bullet_list (1128), all of which emit the leading `\\n` guard."
    - "translator.py:3807-3813 depart_field_list only appends a bare `\\n\\n`-style spacer (`self.body.append(\"\\n\")`) -- it does NOT set list_item_needs_separator = True for a following sibling, unlike depart_block_quote (2137-2138) / depart_definition_list."
  falsification_test: "If, after adding the guard to visit_field_list (leading \\n when in_list_item and list_item_needs_separator) and depart_field_list (set list_item_needs_separator = True when in_list_item), a minimal fixture (enumerated-list item = paragraph + field_list) STILL emits `)strong(` juxtaposed OR still fails typst.compile with 'expected semicolon or line break', the hypothesis is wrong."
  fix_rationale: "Mirror the exact established block-visitor pattern (bug #4's block_quote/definition_list): visit_field_list emits a leading \\n when (in_list_item and list_item_needs_separator) and clears the flag; depart_field_list sets list_item_needs_separator = True when in_list_item. This is the field-list block sibling, NOT visit_field_name/visit_field_body (explicitly out of scope per fix_requirements -- bug #8 already handles collapsed inline field bodies within a single field). Top-level (non-list-item) field lists are unaffected because in_list_item is False there -- the new code paths are both gated on in_list_item."
  blind_spots: "Have not yet run the minimal fixture through typst.compile() to confirm pre-fix failure and post-fix pass -- doing that next. Have not yet re-run the full slow corpus gate to confirm GATE-02 goes green or reveals the next fatal."

hypothesis: CONFIRMED via direct -b typst reproduction (scratchpad fixture) -- byte-matches corpus: `text("For example:")strong(` at generated index.typ:22.
test: add list-item separator guard to visit_field_list/depart_field_list mirroring visit_block_quote/visit_definition_list; build minimal fixture; fast suite; corpus gate
expecting: field list nested in a list item after a paragraph emits a leading \n before strong(; compiles to %PDF; corpus gate GREEN or advances to next distinct fatal
next_action: DONE. Fix committed (88574fd), test committed (e0d8c3f). Corpus gate re-run confirms bug #12 (`)strong(` in intl.typ) is CLEARED; GATE-02 is NOT yet green -- a DISTINCT, out-of-scope fatal #13 (image glob-extension resolution, `_static/translation.*`) is now the blocker. Reported to caller per bounded-scope instructions; not fixed in this session.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; a field list nested in a list item, following a paragraph, emits valid separated Typst statements.
actual: "Typst compilation failed: TypstError: expected semicolon or line break" at usage/advanced/intl.typ:391 -- `text(\"For example:\")strong(` -- field list juxtaposed against preceding paragraph inside an enumerated-list item.
errors: "TypstError: expected semicolon or line break"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after bugs #1-#11 unblocked the compile path (twelfth fatal in the fix-forward campaign).

## Eliminated

## Evidence

- timestamp: repro
  checked: Real corpus source usage/advanced/intl.rst:232-256 (via cached clone ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/usage/advanced/intl.rst)
  found: "Enumerated list item 3 (`#. Create your Transifex_ account...`) contains two paragraphs, the second ending 'For example:', immediately followed (no directive) by a 3-field field_list (:Organization ID:/:Project ID:/:Project URL:)."
  implication: Confirms the exact corpus construct matching the reported fatal -- a field_list as a block sibling inside a list item, following a paragraph.

- timestamp: code-read
  checked: typsphinx/translator.py visit_field_list/depart_field_list (3801-3813) vs. visit_block_quote/depart_block_quote (2091-2138) and visit_definition_list/depart_definition_list (1377-1402)
  found: field_list visitors have NO in_list_item/list_item_needs_separator guard; block_quote and definition_list (fixed under bug #4/#8) both have the leading-newline-on-visit + flag-set-on-depart pattern.
  implication: field_list was omitted from the bug #4 block-visitor sweep, exactly as the bug report states. Confirms root cause and the exact fix site.

- timestamp: direct-repro
  checked: Built minimal fixture (enumerated list item = paragraph "Create your account." + paragraph "For example:" + field_list with 2 fields) via -b typst against UNPATCHED translator.py; inspected generated index.typ.
  found: 'text("Create your account.")\ntext("For example:")strong(\ntext("Organization ID") + text(":"))\n\nraw("sphinx-document")\nstrong(\ntext("Project ID") + text(":"))' -- byte-identical juxtaposition shape to corpus fatal (text("For example:")strong().
  implication: Root cause reproduced offline, confirms exact fix site (visit_field_list needs the leading-separator guard).

## Resolution

root_cause: visit_field_list/depart_field_list (typsphinx/translator.py) were omitted from the bug #4 list-item block-visitor separator sweep. visit_field_list is a bare pass with no in_list_item/list_item_needs_separator guard, so when a field_list follows a sibling paragraph inside a list item, visit_field_name's strong( (emitted by the first field inside the list) abuts the preceding paragraph's closing ) with no separator -> text("For example:")strong( -> Typst "expected semicolon or line break".
fix: visit_field_list now emits a leading \n (and clears list_item_needs_separator) when in_list_item and list_item_needs_separator, mirroring visit_block_quote/visit_definition_list exactly. depart_field_list now sets list_item_needs_separator = True when in_list_item so a following sibling separates. Top-level (non-list-item) field lists are unaffected -- both new code paths are gated on in_list_item, which is False at top level. ONE file: typsphinx/translator.py (visit_field_list/depart_field_list, 2 guard blocks added).
verification: New tests/test_field_list_in_list_item_render_gate.py PASSES with fix, FAILS pre-fix (git stash) with the exact "expected semicolon or line break" fatal (text("For example:")strong( juxtaposition, byte-matching the corpus fatal at usage/advanced/intl.typ:391). Confirmed via direct scratchpad reproduction too (typst.compile() succeeds post-fix, 25017 bytes). Fast suite 413 passed / 15 deselected (412 prior + 1 new; NO existing expectation updates needed). black/ruff/mypy clean on all changed files.

Corpus gate re-run (uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s): bug #12's exact fatal is GONE -- rebuilt usage/advanced/intl.typ now shows `text("For example:")` on its own line, newline-separated from `strong(text("Organization ID") + text(":"))`, byte-confirmed via a manual `-b typst` build of the full cached corpus. GATE-02 is NOT yet green: the gate now fails on a DISTINCT fatal #13 (confirmed via manual `-b typst` build + Typst evaluation-order reasoning -- "expected semicolon or line break" is a parse-time error caught before any evaluation, so it preempted this runtime error even though usage/advanced/intl.typ line 25 is physically earlier in the file than line 391):

  TypstError: file not found (searched at <build>/_static/translation.*)

  Construct: `.. figure:: /_static/translation.*` (usage/advanced/intl.rst:12) -- a
  Sphinx image-glob path (any-extension wildcard). Sphinx's core
  Builder.post_process_images() normally resolves `.*` to a concrete
  extension via the builder's `supported_image_types` class attribute (checked
  against `node['candidates']`); TypstBuilder.post_process_images()
  (typsphinx/builder.py) OVERRIDES this with a bare `node.get("uri", "")`
  read that never resolves the glob, and TypstBuilder declares no
  `supported_image_types`. The literal, unresolved `.*` URI flows straight
  through to visit_image, emitting `image("../../_static/translation.*", ...)`
  (usage/advanced/intl.typ:25) -- a path Typst cannot find on disk (the real
  files are `translation.png`/`translation.svg`) -- and copy_image_files()
  also cannot copy a literally-named `translation.*`. One-line hypothesis:
  TypstBuilder.post_process_images() needs to resolve `*`-glob image
  candidates to a concrete extension (declare `supported_image_types` and
  mirror/call the base-class candidate-resolution logic) before storing the
  URI. Occurrence count: 1 real image()-emitting occurrence, 1 file
  (usage/advanced/intl.typ:25, from usage/advanced/intl.rst:12). (A second
  textual match, usage/restructuredtext/basics.rst:506 `.. image:: gnu.*`,
  has no corresponding `gnu.*` file in the corpus's `_static/`, and a third,
  changes/1.4.rst:431, is prose describing rst syntax inside a code block,
  not a live directive -- neither emits an image() call, confirmed via
  `grep '\.\*"' ` over the full generated .typ tree.) NOT fixed this session
  -- distinct bug class (asset/glob resolution vs. syntax separator),
  out of the assigned scope.
files_changed: [typsphinx/translator.py, tests/test_field_list_in_list_item_render_gate.py, tests/fixtures/field_list_in_list_item_render_gate/conf.py, tests/fixtures/field_list_in_list_item_render_gate/index.rst]
