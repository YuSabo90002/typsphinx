# Sphinx configuration for the VER-01 versionmodified render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the versionmodified/visit_inline classed-dispatch fix (Phase 12) in
# a real compile: sphinx-build -> typst.compile() -> pypdf text-extraction,
# asserting the Sphinx-computed label wordings render as unboxed italic
# prose with no LEAK_SIGNATURES token present.

project = "Version Modified Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template plus the gentle-clues @preview import -- included
# documents only get a minimal import set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Version Modified Render Gate", "Test Author"),
]
