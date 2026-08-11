"""Sphinx config for the nested-figure render-gate fixture (FIG-01, Phase 43).

Reproduces the FIG-01 defect: a figure nested inside another figure's
``legend`` (docutils' name for a figure's body content beyond its first
caption paragraph) currently aborts the whole ``typst.compile()`` with a
classic ``TypstError`` -- ``visit_legend``/``depart_legend`` do not exist, so
docutils' ``unknown_visit`` warns and continues, streaming the legend's
children unwrapped directly after the outer ``image(...)`` call (43-RESEARCH.md
Pitfall 4).

``numfig = True`` is set so figure numbering is exercised, matching the
established figure-fixture convention (``figure_propagated_target_render_gate/conf.py``).

Fully offline and text-only -- no intersphinx, no network.
"""

project = "Nested Figure Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() calls typst.compile() -- without this the gate
# proves nothing (it would only emit .typ, never compile it).
#
# Phase 47 fixture de-collision: the target was originally "index", whose
# resolved stem is identical to the docname "index" itself -- a self-
# collision under the two-layer content/wrapper split. Renamed to
# "master.typ" per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule;
# no other element changed.
typst_documents = [
    ("index", "master.typ", "Nested Figure Render Gate", "typsphinx tests"),
]

numfig = True
