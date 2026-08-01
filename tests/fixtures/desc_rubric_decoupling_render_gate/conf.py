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

typst_documents = [
    ("index", "index", "Desc Rubric Decoupling Render Gate", "typsphinx tests"),
]
