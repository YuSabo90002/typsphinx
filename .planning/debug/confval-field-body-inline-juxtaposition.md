---
status: fixing
trigger: "Corpus gate fatal #8: TypstError: expected semicolon or line break at usage/configuration.typ:217:21 (representative) — 16 occurrences ALL in usage/configuration.typ. 15x a confval :default: FIELD BODY emitted as juxtaposed inline exprs text(\"The value of \")strong({...}) (no +/newline); 1x (line 2009) a paragraph abutting a following terms(...) inside a bullet-list item."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "TWO mechanisms, same fatal, both in usage/configuration.typ. (A) A confval :type:/:default: field body written inline on the field line (e.g. ':default: The value of **html_title**') is COLLAPSED by docutils: its children are inline nodes (Text, strong, literal) DIRECTLY under field_body, with NO wrapping <paragraph>. visit_field_body is a bare pass and sets NO concat context, so visit_Text/visit_strong emit their expressions with no separator: text(\"The value of \")strong({text(\"html_title\")}) — two juxtaposed code-mode expressions in the top-level #{ } content block -> Typst reads text(...) as a complete statement then hits strong(...) -> 'expected semicolon or line break'. (B) A definition_list nested inside a bullet-list item, following a paragraph, emits terms(...) with no leading separator: visit_definition_list adds nothing and depart_definition_list emits terms(...) via add_text with no in_list_item/list_item_needs_separator check, so it abuts the preceding text(...): text(\"Keys...\")terms(...) -> same fatal."
  confirming_evidence:
    - "Doctree (pseudoxml) of ':default: The value of **html_title**' shows field_body children are Text('The value of ') + strong('html_title') DIRECTLY — no <paragraph>. Emitted .typ: strong(text(\"Default\") + text(\":\"))\\ntext(\"The value of \")strong({text(\"html_title\")}) — byte-shape match to corpus configuration.typ:217."
    - "typst.compile of #{ text(\"The value of \")strong({text(\"html_title\")}) } -> FAIL 'expected semicolon or line break'. Wrapped { text(...)\\nstrong(...) } -> OK. + concat text(...) + strong(...) -> OK."
    - "Corpus configuration.typ line 2009: list({\\ntext(\"Keys...\")terms(terms.item(...)) — a def-list abutting a paragraph inside a list item with no separator. depart_definition_list emits terms(...) with no list_item_needs_separator guard (unlike every other block visitor)."
  falsification_test: "If, after (A) activating the shared _inline_concat_* context for all-inline field bodies and (B) adding the in_list_item/list_item_needs_separator guard to visit_definition_list, the field body STILL emits text(...)strong(...) juxtaposed OR the def-list STILL abuts the paragraph OR either still fails typst.compile, the hypothesis is wrong."
  fix_rationale: "(A) Reuse bug #5's _inline_concat_* machinery: add (_in_field_body, _field_body_has_content) as a lowest-precedence entry in _CONCAT_CONTEXTS. visit_field_body activates it ONLY when every child is inline (all isinstance (nodes.Text, nodes.Inline)) — the collapsed case; a block field body (real <paragraph> children) keeps the current par()-based path untouched (its paragraphs already emit valid, \\n\\n-separated statements). Then adjacent inline field-body expressions are '+'-separated: text(\"The value of \") + strong({...}) — one valid content value. Every inline visitor (Text/literal/strong/emphasis/reference) already routes through the concat helpers, so all inline shapes are covered. (B) Reuse the standard block-visitor separator pattern (used at literal_block/bullet_list/etc.): visit_definition_list emits a leading \\n when in_list_item and list_item_needs_separator; depart sets list_item_needs_separator=True for the next sibling. Both fixes reuse existing mechanisms; neither touches the par()-skip logic (bug #4) nor re-introduces par() in list items."
  blind_spots: "Concat context is activated only for ALL-inline field bodies; a hypothetical field body mixing inline + block children (docutils does not produce this — it either collapses to inline or keeps a paragraph) would skip concat. reference is both Inline and Body but IS Inline (predicate includes it). If corpus surfaces a DISTINCT fatal after this (different file/construct), report it (bounded scope)."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: (A) add _in_field_body concat context + all-inline guard in visit_field_body/depart_field_body; (B) add list-item separator guard to visit/depart_definition_list; rebuild fixtures; fast suite; corpus gate
expecting: field body emits text(\"The value of \") + strong({...}); def-list emits \\nterms(...) in list item; both compile to %PDF; corpus advances past configuration.typ 'expected semicolon or line break'
next_action: Implement both fixes in translator.py, add fast regression test, run fast suite + lint + corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; a confval field body and a def-list nested in a list item emit valid Typst statements.
actual: "Typst compilation failed: TypstError: expected semicolon or line break" at usage/configuration.typ:217:21 (representative). 16 occurrences ALL in usage/configuration.typ. 15x text("The value of ")strong({...}) collapsed :default: field body; 1x (2009) text(...)terms(...) def-list abutting a paragraph in a list item.
errors: "TypstError: expected semicolon or line break"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after bugs #1-#7 unblocked the compile path.

## Eliminated

## Evidence

- timestamp: repro
  checked: Built minimal confval fixture (:default: The value of **html_title**) via -b typst + -b pseudoxml; inspected doctree and emitted index.typ
  found: field_body children are Text + strong DIRECTLY (docutils collapse, no <paragraph>). Emitted: text("The value of ")strong({text("html_title")}) — juxtaposed, no +, no par(). Byte-match to corpus configuration.typ:217.
  implication: Root cause (A) reproduced offline: collapsed field body has no concat context -> inline juxtaposition.

- timestamp: compile-direction
  checked: typst.compile of broken (juxtaposed) vs {..} wrap vs + concat snippets
  found: broken -> 'expected semicolon or line break'; { text(..)\nstrong(..) } -> OK; text(..) + strong(..) -> OK.
  implication: + concat (concat context) and {..} wrap both fix it; concat context matches bug #5 machinery and the inline case.

- timestamp: corpus-line-2009
  checked: corpus configuration.typ line 2009 + rst source (line 3546 bullet '* Keys that you may want to override include:' then a def-list)
  found: list({\ntext("Keys...")terms(terms.item(...)) — def-list abuts paragraph in a list item, no separator. depart_definition_list has no list_item_needs_separator guard.
  implication: Root cause (B): def-list block visitor omitted from the list-item separator machinery.

## Resolution

root_cause: (A) A confval :type:/:default: field body written inline is collapsed by docutils to inline children (Text/strong/literal) directly under field_body; visit_field_body sets no concat context, so adjacent inline expressions emit juxtaposed (text(...)strong(...)) with no separator -> 'expected semicolon or line break' in the code-mode content block. (B) A definition_list nested in a bullet-list item after a paragraph emits terms(...) with no leading list-item separator, abutting the preceding text(...).
fix: (A) Added (_in_field_body, _field_body_has_content) as the lowest-precedence _CONCAT_CONTEXTS entry; visit_field_body activates it only when every child is inline (all isinstance (nodes.Text, nodes.Inline)) with save/restore for nesting safety; depart_field_body restores. Collapsed field-body inline children now '+'-separate into one content value; block field bodies (real paragraphs) untouched. (B) visit_definition_list emits a leading \n when in_list_item and list_item_needs_separator; depart_definition_list sets list_item_needs_separator=True. ONE file: typsphinx/translator.py.
verification: New tests/test_confval_field_body_render_gate.py PASSES with fix, FAILS pre-fix (git stash) with the exact 'expected semicolon or line break' fatal. Minimal fixture emits text("The value of ") + strong({text("html_title")}) + text(" with a ") + raw("fallback") (+-joined) and a newline-separated def-list in a list item; compiles to %PDF (37023 bytes). Fast suite 409 passed / 15 deselected (408 prior + 1 new; NO existing expectation updates). black/mypy/ruff clean. Corpus proof: PRE-FIX master -> 'expected semicolon or line break' (bug #8); POST-FIX master -> 'expected expression' (DISTINCT bug #9). All 16 configuration.typ sites cleared (15 field-body + 1 def-list-in-list-item). Corpus gate re-run RED on DISTINCT fatal #9: TypstError 'expected expression' in usage/domains/c.typ (repr line 107) and usage/domains/cpp.typ -- a C/C++ domain multi-line function signature where the desc-parameter/signature concat emits a malformed leading '+' (' + link(...)') after a newline-terminated sibling inside strong({...}). PRE-EXISTING (c.typ byte-identical pre/post this fix; fails both directions). Reported, NOT fixed -- bounded scope (distinct construct/context).
files_changed: [typsphinx/translator.py, tests/test_confval_field_body_render_gate.py, tests/fixtures/confval_field_body_render_gate/conf.py, tests/fixtures/confval_field_body_render_gate/index.rst]
