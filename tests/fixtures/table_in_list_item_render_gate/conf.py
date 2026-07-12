# Sphinx configuration for the table-in-list-item render-gate fixture
# (Phase 15, GATE-02 regression).
#
# Minimal self-contained project used by
# tests/test_table_in_list_item_render_gate.py to prove the translator
# newline-separates a table from a preceding sibling lead-in text inside a
# list item. This is the fast, offline reproduction of the sixteenth fatal
# GATE-02 surfaced against Sphinx's own doc/ tree (2 occurrences, 1 file:
# latex.typ:2382, also :2463), after bugs #1-#15 unblocked the compile path:
#
#     TypstError: expected semicolon or line break
#         ... text("Text styling commands:")table( ...
#
# Root cause: a bullet-list item whose lead-in text ("Text styling
# commands:") is immediately followed by a table (list-table) -- docutils
# nests the table as a direct block sibling inside the list_item.
# visit_table/depart_table had no in_list_item/list_item_needs_separator
# guard (the one block visitor omitted from the bug #4 sweep), so
# depart_table's table( juxtaposed directly against the preceding text's
# closing ) with no separator.
#
# Fix: visit_table emits the standard list-item newline separator
# (mirroring visit_block_quote/visit_field_list) when in_list_item and
# list_item_needs_separator; depart_table sets list_item_needs_separator =
# True when in_list_item so a following sibling separates.

project = "Table In List Item Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the "expected semicolon or line break" fatal is observable.
typst_documents = [
    ("index", "index", "Table In List Item Render Gate", "Test Author"),
]
