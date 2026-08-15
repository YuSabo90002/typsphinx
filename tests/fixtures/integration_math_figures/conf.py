# Sphinx configuration for math and figures integration testing

project = "Math and Figures Test"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture de-collision
# rule"): the original target "index.typ" resolved to the SAME physical
# path as this docname's own content file (index.typ) under the
# two-layer split -- a self-collision (D-01). Retargeted to the
# canonical replacement "master.typ"; the docname, title and author are
# unchanged.
typst_documents = [
    ("index", "master.typ", "Math and Figures Test", "Test Author"),
]

# Enable both mitex and native math
typst_use_mitex = True
