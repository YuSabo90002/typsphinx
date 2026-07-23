# Sphinx configuration for the GATE-01 figure-target-caption render-gate
# fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the FIG-02 caption buffer-swap + internal `:target:` refid fix in a
# real compile: sphinx-build -> typst.compile() -> pypdf text-extraction,
# asserting each caption's sentinel token appears exactly once and that no
# LEAK_SIGNATURES token leaks into the rendered text (Issue #114, D-03).

project = "Figure Target Caption Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Figure Target Caption Render Gate", "Test Author"),
]
