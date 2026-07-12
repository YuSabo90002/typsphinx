"""Sphinx config for the desc-signature anchor render-gate fixture.

Reproduces GATE-02 corpus fatal #17 offline -- the FIRST *semantic* (non-parse)
corpus fatal. Once bugs #1-#16 unblocked the parse path, ``typst.compile()``
reached the label-resolution pass and aborted with::

    TypstError: label `<c._u40_alias.data>` does not exist in the document

Root cause: an API-declaration signature (``desc_signature``) carries docutils
ids, and ``depart_reference``'s refid branch emits a same-document
``link(<_sanitize_label(id)>, ...)`` for a cross-reference to it -- but
``depart_desc_signature`` never emitted a matching ``<id>`` anchor, so every
such link dangled. This fixture drives BOTH the clean-id shape
(``.. c:function::`` + ``:c:func:`` back-reference) and the exact corpus
``@alias`` construct (whose ids contain ``@`` -> ``_u40_``, exercising
``_sanitize_label`` on the anchor side and multiple ids in one alias).

Fully offline and text-only -- no intersphinx, no network.
"""

project = "Desc Signature Anchor Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    ("index", "index", "Desc Signature Anchor Render Gate", "typsphinx tests"),
]
