# Sphinx configuration for the confval field-spacing render-gate fixture
# (Phase 20 Plan 02, FID-09).
#
# Minimal self-contained project used by
# tests/test_confval_field_spacing_render_gate.py to prove the translator
# restores the colon-space after a field name AND the inter-field boundary
# double-space between sibling :type:/:default: fields. This is the fast,
# offline reproduction of the audit catalogue's literal `the_answer` repro
# (17-AUDIT-CATALOGUE.md finding #5):
#
#     the_answer Type:int (a number)Default:42
#
# Root cause: depart_field_name appended a bare colon with no trailing
# space, and depart_field was a no-op with no inter-field separator, so
# sibling fields concatenated with zero space between them in the code-mode
# content block.
#
# Fix: depart_field_name appends the colon-space form (`text(": ")`);
# depart_field emits a sibling-guarded `text("  ")` two-space separator
# between adjacent fields.

project = "Confval Field Spacing Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the real inter-token/inter-field spacing is observable via pypdf
# text extraction.
typst_documents = [
    ("index", "index", "Confval Field Spacing Render Gate", "Test Author"),
]
