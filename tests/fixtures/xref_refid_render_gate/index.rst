Xref Refid Render Gate
=======================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (XREF-01). It is not meant to be read as
prose -- it exercises a same-document ``:ref:`` section-anchor
cross-reference and a ``:term:`` glossary cross-reference, each of which
must resolve to a working Typst link in a real compile.

.. _target-section:

Target Section
---------------

This is the section a ``:ref:`` cross-reference resolves to.

.. glossary::

   Widget
      A thing that does stuff.

Cross-Reference Paragraph
--------------------------

See the REFSECTIONSENTINEL section :ref:`target-section` for details, and
the TERMSENTINEL glossary entry :term:`Widget` for a definition.
