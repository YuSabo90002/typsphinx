"""Sphinx config for the rubric-with-inline-strong-markup render-gate fixture
(Phase 39, ADM-05/D-13).

Cloned from ``tests/fixtures/desc_rubric_decoupling_render_gate/conf.py``.
``index`` MUST be a master document so the compile-sanity leg actually
reaches ``typst.compile()``. This fixture's purpose is proving this phase's
classic GATE-01 RED -- a rubric containing a real inline bold child clobbers
the shared ``_strong_was_*`` save slots (Phase 36 D-02) and every paragraph
after it, to the end of the document, loses its ``par()`` wrapper.
"""

project = "Rubric Strong Nesting Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Rubric Strong Nesting Render Gate", "typsphinx tests"),
]
