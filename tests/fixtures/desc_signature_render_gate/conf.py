# Sphinx configuration for the DESC-01..04 desc_signature render-gate
# fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the desc_returns/desc_signature_line/desc_optional/desc_inline
# handlers (Phase 12, Plan 03) in a real compile: sphinx-build ->
# typst.compile() -> pypdf text-extraction, asserting the return arrow,
# genuine multi-line linebreak(), nested optional brackets, and inline
# fragment all render correctly with no LEAK_SIGNATURES token present.

project = "Desc Signature Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template plus the gentle-clues @preview import -- included
# documents only get a minimal import set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Desc Signature Render Gate", "Test Author"),
]
