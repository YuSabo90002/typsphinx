# Sphinx configuration for the field-list-in-list-item render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by
# tests/test_field_list_in_list_item_render_gate.py to prove the translator
# newline-separates a field_list from a preceding sibling paragraph inside a
# list item. This is the fast, offline reproduction of the twelfth fatal
# GATE-02 surfaced against Sphinx's own doc/ tree (1 occurrence, 1 file:
# usage/advanced/intl.typ:391), after bugs #1-#11 unblocked the compile path:
#
#     TypstError: expected semicolon or line break
#         ... text("For example:")strong( ...
#
# Root cause: an enumerated-list item whose paragraph ("For example:") is
# immediately followed by a field list (:Organization ID:/:Project ID:/
# :Project URL:) -- docutils nests the field_list as a direct block sibling
# inside the list_item. visit_field_list was a bare `pass` with no
# in_list_item/list_item_needs_separator guard (the one block visitor omitted
# from the bug #4 sweep), so visit_field_name's strong( juxtaposed directly
# against the preceding paragraph's closing ) with no separator.
#
# Fix: visit_field_list emits the standard list-item newline separator
# (mirroring visit_block_quote/visit_definition_list); depart_field_list sets
# list_item_needs_separator = True for a following sibling.

project = "Field List In List Item Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the "expected semicolon or line break" fatal is observable.
typst_documents = [
    ("index", "index", "Field List In List Item Render Gate", "Test Author"),
]
