# Sphinx configuration for the list-item nested-block adjacency render-gate
# fixture (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by
# tests/test_list_item_nested_block_render_gate.py to prove the translator
# emits a valid, newline-separated statement stream when a list item contains a
# nested list directly adjacent to a sibling paragraph. This is the fast,
# offline reproduction of the fourth fatal GATE-02 surfaced against Sphinx's own
# doc/ tree (changes/1.6.rst and 7 other files, 17 identical occurrences), after
# the static-asset-copy, target-label, and def-list-term-concat fixes unblocked
# the compile path:
#
#     TypstError: expected semicolon or line break
#         ... })par( ...
#
# Root cause: in_list_item was a bare boolean with no nesting stack. A nested
# list's depart_list_item unconditionally reset it to False, so a paragraph
# following a nested list inside the SAME outer item was mis-classified as
# top-level -> visit_paragraph emitted par({...}) (instead of skipping wrapping
# like its sibling paragraphs) directly after the nested list's closing ")"
# inside the code-mode content block -> "})par(", two juxtaposed statements with
# no separator, a Typst syntax error.
#
# Fix: visit_list_item pushes the prior in_list_item onto a stack and
# depart_list_item pops+restores it, so the flag correctly reflects "inside a
# list item" at any nesting depth. The trailing paragraph is then recognized as
# in-item and its text emits via the existing list_item_needs_separator "\n"
# machinery, separated from the nested list.

project = "List Item Nested Block Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the "expected semicolon or line break" fatal is observable.
typst_documents = [
    ("index", "index", "List Item Nested Block Render Gate", "Test Author"),
]
