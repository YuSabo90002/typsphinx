"""Sphinx config for the duplicate-include-label render gate fixture.

Deterministic, offline reproduction of the nineteenth corpus fatal (Phase 15,
GATE-02): a document reachable via more than one toctree path (a "diamond") is
physically #included more than once into a single compiled master, so every
Typst <label> it defines is emitted twice and typst.compile() aborts with
"label ... occurs multiple times in the document".
"""

project = "Duplicate Include Label Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Duplicate Include Label Render Gate", "typsphinx tests"),
]
