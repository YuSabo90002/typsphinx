"""Sphinx config for the nested-definition body-clobber render-gate fixture.

Reproduces GATE-02 corpus fatal #18 offline. On Sphinx's own ``doc/`` tree the
``typstpdf`` build reached the semantic label pass and aborted with::

    TypstError: label `<sphinx.domains.Domain>` does not exist in the document

Root cause: ``visit_term``/``visit_definition`` saved/restored the main body
through a SINGLE-SLOT ``self.saved_body`` (plus single-slot
``current_term_buffer`` / ``current_definition_buffer``). When a definition list
is NESTED inside a definition, the inner list overwrote every slot; on the outer
``depart_definition`` the restore was skipped, leaving ``self.body`` pointing at
the orphaned inner buffer. From that point on EVERY subsequent body write --
including a later API declaration's ``desc_signature`` and its
``[#metadata(none) <id>]`` anchor -- was silently dropped, so a same-document
``link(<id>, ...)`` reference to that declaration dangled.

This fixture drives BOTH failure directions in one document:

* the outer definition's leading paragraph (sentinel ``OUTERSENTINEL_CONFIG``)
  must survive rather than being dropped when its definition contains a nested
  definition list; and
* a forward ``:py:class:`` reference (emitted before the orphaning list, so it
  lands in the real body) to a ``.. py:class::`` declaration that appears AFTER
  the orphaning list and whose own content BEGINS with a nested definition list
  -- the declaration's anchor was dropped pre-fix, dangling the reference.

Fully offline and text-only -- no intersphinx, no network.
"""

project = "Nested Definition Body Clobber Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    ("index", "index", "Nested Definition Body Clobber Render Gate", "typsphinx tests"),
]
