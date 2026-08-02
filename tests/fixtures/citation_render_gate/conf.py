"""Sphinx config for the citation render-gate fixture (Phase 40, GATE-01).

Root cause this fixture reproduces: ``docutils.nodes.citation`` and
``docutils.nodes.label`` have no translator handler today (measured
2026-08-02; see 40-CONTEXT.md/40-RESEARCH.md). A real
``sphinx-build -b typst`` build falls through to ``unknown_visit`` /
``unknown_departure`` for both node types -- logging
``WARNING: unknown node type: <citation ...>`` and
``WARNING: unknown node type: <label ...>`` -- and the label's bare Text
child juxtaposes against the citation's paragraph body with no separator:
``text("Krizhevsky2012")par({text("Krizhevsky, A. ...")})``. Compiling that
fragment with a real ``typst.compile()`` raises the classic
``TypstError: expected semicolon or line break``.

``index`` must be the master document (not ``second``) because that fatal
only fires inside ``TypstPDFBuilder.finish()``'s real compile step -- a
``-b typst`` build of a non-master document writes the same invalid ``.typ``
but never compiles it.
"""

project = "Citation Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build
# path where the "expected semicolon or line break" fatal is observable.
typst_documents = [
    ("index", "index", "Citation Render Gate", "Test Author"),
]
