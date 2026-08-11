"""Sphinx config for the citation degradation-gate fixture (Phase 40.1,
GATE-EVIDENCE-01, WR-01).

Root cause this fixture reproduces: ``visit_citation``'s backref loop
(``typsphinx/translator.py``, D-01/D-04) treats "the citing
``nodes.reference`` could not be located in the resolved doctree" as
*eligible* rather than *skip*, because ``ref_node is not None and not ...``
short-circuits to ``False`` when ``_find_citing_reference`` returns
``None``. A citing site pruned by an ``only``-tag filter is exactly this
topology: Sphinx's citation domain populates a citation's ``backrefs`` list
BEFORE the ``only``-tag filter transform removes the pruned block's content
from the doctree the writer sees, so a backref id can survive in
``backrefs`` with no corresponding ``nodes.reference`` anywhere in the
resolved tree. Unfixed, ``visit_citation`` still appends a namespaced label
for that unreachable id, emitting ``link(<docname:id>, ...)`` to a Typst
label nothing ever attaches -- a whole-document compile fatal:
``typst.TypstError: label `<index:idN>` does not exist in the document``.

``index`` must be the master document (not merely built with ``-b typst``)
because that fatal only fires inside ``TypstPDFBuilder.finish()``'s real
compile step -- a ``-b typst`` build writes the same dangling-``link()``
``.typ`` but never compiles it.
"""

project = "Citation Degradation Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build
# path where the WR-01 "label ... does not exist in the document" fatal is
# observable.
#
# Phase 47 fixture de-collision: the target was originally "index", whose
# resolved stem is identical to the docname "index" itself -- a self-
# collision under the two-layer content/wrapper split. Renamed to
# "master.typ" per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule;
# no other element changed.
typst_documents = [
    ("index", "master.typ", "Citation Degradation Gate", "Test Author"),
]
