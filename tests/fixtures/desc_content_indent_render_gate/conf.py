# Sphinx configuration for the desc_content_indent_render_gate fixture
# (Phase 38, GATE-01, IND-01..IND-05, FLD-01, D-04, D-11).
#
# Minimal self-contained project used by
# tests/test_desc_content_indent_render_gate.py to prove, in ONE build,
# every doctree shape IND-01..IND-05 and FLD-01 are judged on:
#
#   - IND-01/02/03: a three-level nest (py:class:: -> py:method:: ->
#     py:attribute::), each with its own one-paragraph body -- proves a
#     desc_content body is indented past its own signature (IND-01),
#     accumulates with depth (IND-02), and a nested member's own signature
#     aligns with its parent's body rather than over-indenting (IND-03).
#   - IND-02 (continued): the class body resumes with a further paragraph
#     AFTER the nested method closes, so the "class body continues" row of
#     38-CONTEXT.md D-01's measured table is reachable.
#   - IND-05: a sibling top-level py:function:: immediately after the
#     three-level nest closes -- depth cannot leak because the wrapper
#     closes, not because a counter resets (there is no counter, D-01).
#   - FLD-01: the nested py:method:: carries its own :param:/:type:/
#     :returns: field list, so the field-list step nests inside the
#     method body's own step.
#   - Body-less CONTROL (contract section 2.4): two back-to-back body-less
#     confval:: siblings, mirroring
#     tests/fixtures/desc_bodyless_concat_render_gate/index.rst.
#   - List-item CONTROL (contract section 2.6): a py:function:: nested
#     inside a bullet-list item, exercising the block-visitor separator
#     interaction (D-12).
#   - Table-cell CONTROL (contract section 2.1): a plain, desc-free
#     list-table cell, kept as a non-regression baseline. A desc or
#     field_list inside a table cell was found, during this plan's own
#     fixture construction, to abort the WHOLE Typst compile via
#     PRE-EXISTING self.body.append bugs unrelated to this plan's own
#     changes (depart_desc_signature, Phase 37; the field_list family,
#     38-EMISSION-CONTRACT.md section 3.1) -- recorded verbatim in
#     38-GATE-EVIDENCE-01.md rather than worked around silently.
#   - Page-boundary case (D-11, SIG-09): a final py:class:: preceded by
#     enough filler paragraphs, under a deliberately enlarged fontsize
#     (via typst_elements, below) so its signature lands near a page
#     boundary and its body crosses onto the next page reproducibly
#     rather than incidentally.
#   - No-desc, no-field-list CONTROL (IND-04 empty): a section containing
#     only ordinary paragraphs, proving a document with neither construct
#     emits no indent wrapper at all.
#   - Block quote (D-04): a block quote with an attribution, proving
#     block_quote is deliberately NOT converted to the shared indent step
#     (contract section 1.2).

project = "Desc Content Indent Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# a manual typst.compile() call actually compiles it to PDF.
#
# Phase 47 fixture de-collision: the target was originally "index", whose
# resolved stem is identical to the docname "index" itself -- a self-
# collision under the two-layer content/wrapper split (the content file
# is unconditionally "index.typ"; a same-named wrapper would overwrite
# it). Renamed to "master.typ" per 47-EXPECTED-STRUCTURE.md's fixture
# de-collision rule; no other element changed.
typst_documents = [
    ("index", "master.typ", "Desc Content Indent Render Gate", "Test Author"),
]

# D-11/SIG-09: an enlarged fontsize (via the CONF-04 typst_elements
# allowlist -- RAW-emitted, unquoted, reaching project()'s own
# `set text(size: fontsize, ...)`) makes content fill each page faster, so
# the page-boundary construct below reproducibly lands its signature near
# a page break with a modest, hand-tunable amount of filler content,
# rather than depending on incidental A4-at-11pt page arithmetic. This
# does not touch page geometry itself (papersize stays the default "a4"),
# so it cannot break the width-sensitive constructs elsewhere in this same
# fixture (the table-cell desc, the longer signatures).
typst_elements = {
    "fontsize": "18pt",
}
