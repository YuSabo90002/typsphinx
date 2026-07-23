Footnote Render Gate
======================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (FN-01, SC#1-4). It is not meant to be
read as prose -- it exercises the Plan 14-01 footnote pre-pass handlers
(``visit_document``'s id-to-node index, ``visit_footnote``'s ``SkipNode``
suppression, and ``visit_footnote_reference``'s definition/reuse emission)
against a real Typst compile.

Single Reference
-----------------

A footnote referenced exactly once [#single]_.

Double Reference
------------------

A footnote referenced from this first paragraph [#double]_.

A second, separate paragraph citing the very same footnote again [#double]_.

Inline Markup and Special Characters
--------------------------------------

A footnote whose body carries inline markup and special characters [#markup]_.

Footnote Inside a List Item
------------------------------

A bullet list with a footnote cited from inside one of its items:

- A list item citing a footnote [#listitem]_.
- A second, plain list item with no footnote reference.

.. rubric:: Footnotes

.. [#single] FOOTNOTESINGLESENTINEL body text.

.. [#double] FOOTNOTEDOUBLESENTINEL body text, cited twice.

.. [#markup] FOOTNOTEMARKUPSENTINEL body with *emphasis*, ``literal``, and
   special characters @ # $ _ * < > here.

.. [#listitem] FOOTNOTELISTSENTINEL body text cited from inside a bullet
   list item.
