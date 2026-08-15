"""Sphinx config for the desc/rubric decoupling render-gate fixture (Phase 36, ADM-06).

``index`` MUST be a master document so the compile-sanity leg actually reaches
``TypstPDFBuilder.finish()``. This fixture's purpose is equality-of-output
across the ADM-06 decoupling (a byte-identical golden .typ), not defect
reproduction -- unlike most render-gate fixtures in this repo, which prove a
compile fatal is fixed.
"""

project = "Desc Rubric Decoupling Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture de-collision
# rule"): the original target "index" resolved to the SAME physical path
# as this docname's own content file (index.typ) under the two-layer
# split -- a self-collision (D-01). Retargeted to the canonical
# replacement "master.typ"; the docname, title and author are unchanged.
typst_documents = [
    ("index", "master.typ", "Desc Rubric Decoupling Render Gate", "typsphinx tests"),
]
