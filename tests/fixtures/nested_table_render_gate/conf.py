# Sphinx configuration for the nested-table render-gate fixture (Phase 43,
# TBL-04).
#
# Minimal self-contained project used by
# tests/test_nested_table_render_gate.py to prove a table nested inside
# another table's cell no longer clobbers the enclosing table's accumulated
# cells, column count, column widths, caption, header-row flag and span
# counters -- see
# .planning/todos/pending/2026-08-04-nested-table-clobbers-outer-table-state.md
# for the full reproduction. The defect is STRUCTURAL, not a compile fatal
# (the broken output compiles cleanly with no warning), so this fixture must
# be built through the ``typstpdf`` builder for the render-gate tests to
# assert on both the emitted ``.typ`` and the extracted PDF text.

project = "Nested Table Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- without this,
# TypstPDFBuilder.finish() returns early and the gate proves nothing.
typst_documents = [
    ("index", "index", "Nested Table Render Gate", "Test Author"),
]
