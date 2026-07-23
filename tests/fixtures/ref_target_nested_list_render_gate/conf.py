# Minimal Sphinx config for the reference-with-target + block-quote-in-list
# render gate (Phase 15, GATE-02, eleventh corpus fatal).
project = "Ref Target Nested List Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# One master document compiled straight to PDF by the typstpdf builder.
typst_documents = [
    ("index", "index", project, author),
]
