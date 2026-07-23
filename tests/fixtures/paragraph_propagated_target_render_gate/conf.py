"""Sphinx config for the propagated-target anchor render-gate fixture.

Reproduces GATE-02 corpus fatal #20 offline -- a missing-anchor (dangling
label) fatal on a propagated-target paragraph. On Sphinx's own ``doc/`` tree
(``usage/referencing.rst``) an explicit ``.. _xref-modifiers:`` target sits
before a PARAGRAPH (not a section). docutils' ``PropagateTargets`` transform
moves the target's id onto that following paragraph's ``node["ids"]``. The
translator's ``visit_paragraph`` emitted ``par({...})`` but read no
``node["ids"]`` -- so no ``<label>`` anchor was emitted -- while a same-doc
``:ref:`` renders ``link(<xref-modifiers>, ...)``. ``typst.compile()`` then
aborted the whole document at the semantic label-resolution pass with::

    TypstError: label `<xref-modifiers>` does not exist in the document

Fix: ``visit_paragraph`` (and the audited sibling body-element visitors) now
route ``node["ids"]`` through the shared ``_emit_id_anchors`` helper, emitting
the proven ``[#metadata(none) <id>]`` target-anchor form (bug #2) via
``_sanitize_label`` (bug #10) so the anchor name byte-matches the reference.

Fully offline and text-only -- no intersphinx, no network.
"""

project = "Paragraph Propagated Target Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    ("index", "index", "Paragraph Propagated Target Render Gate", "typsphinx tests"),
]
