"""Sphinx config for the captioned-table propagated-target render-gate fixture.

TBL-03 / Phase 42. A standalone target immediately preceding a captioned
table has its id propagated onto the table's ``node["ids"]`` by docutils'
``PropagateTargets`` transform. ``depart_table``'s trailing
``_emit_id_anchors`` call for the propagated remainder ids fires while
``self.in_table`` is still ``True``, so ``add_text`` routes the anchor
markup into ``self.table_cell_content`` -- a buffer discarded a few
statements later -- instead of ``self.body``. The propagated target's
anchor is therefore never emitted, and a same-document reference to it
dangles, aborting the Typst compile with a real
``TypstError: label ... does not exist in the document`` fatal.

``index`` MUST stay a master document (listed in ``typst_documents``) or
the writer only emits a minimal import set and ``TypstPDFBuilder.finish()``
never calls ``typst.compile()`` -- the fixture would not reach a real
compile fatal at all.

``numfig = True`` is required because the references section below uses
``:numref:`` against a captioned table with a ``:name:`` (mirrors
``captioned_table_render_gate/conf.py``'s own reason).
"""

project = "Captioned Table Propagated Target Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
#
# Target "index" (stem "index") casefold-collides with the docname's own
# content path "index.typ" (fixture de-collision rule, 47-EXPECTED-STRUCTURE.md);
# renamed to the canonical "master.typ".
typst_documents = [
    (
        "index",
        "master.typ",
        "Captioned Table Propagated Target Render Gate",
        "typsphinx tests",
    ),
]

numfig = True
