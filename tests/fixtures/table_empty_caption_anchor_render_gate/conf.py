"""Sphinx config for the table-empty-caption-anchor render-gate fixture.

TBL-05 / Phase 43. A ``.. table::`` whose title node exists but RENDERS to
the empty string (a ``raw-html`` role applied to an empty HTML span --
``title.astext()`` is non-empty, but ``visit_raw`` raises ``SkipNode`` for a
non-typst format, so the rendered content is empty) makes ``visit_table``'s
STRUCTURAL captioned pre-check and ``depart_table``'s RENDERED-caption
truthiness check disagree: the visit side treats the table as captioned and
skips its own unconditional id-anchor call, while the depart side treats it
as caption-less and never anchors either. A standalone target immediately
preceding the table has its id propagated onto the table's ``ids`` by
docutils' ``PropagateTargets`` transform, and that id is anchored on
NEITHER path -- a same-document ``:ref:`` to it dangles, aborting the whole
Typst compile with a real ``TypstError: label ... does not exist in the
document`` fatal.

``index`` MUST stay a master document (listed in ``typst_documents``) or
the writer only emits a minimal import set and ``TypstPDFBuilder.finish()``
never calls ``typst.compile()`` -- the fixture would not reach a real
compile fatal at all.

``numfig = True`` is required for the D-05 numbering control: the fixture's
second section is a real-caption table that must render as "Table 1" (NOT
"Table 2") -- proving the empty-rendered-caption table in section 1 is not
figure-wrapped and consumes no table number.
"""

project = "Table Empty Caption Anchor Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    (
        "index",
        "index",
        "Table Empty Caption Anchor Render Gate",
        "typsphinx tests",
    ),
]

numfig = True
