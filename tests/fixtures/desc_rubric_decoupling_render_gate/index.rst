Desc Rubric Decoupling Render Gate
====================================

This fixture combines a single signature, sibling signatures, plain bold
markup, an autodoc-style Options rubric, a rubric carrying a propagated
target inside a list item, and a rubric at true end-of-document -- the
constructs Phase 36's SC#2 names -- into one file, so the desc_signature/
rubric decoupling can be proven to produce byte-identical .typ output.

Single signature with an id anchor.

.. py:function:: connect(host, port, timeout=30)

   Connect to *host*.

Sibling signatures under one directive.

.. py:function:: compile(source)
                  compile(source, filename)
                  compile(source, filename, symbol)

   Compile source into a code or AST object.

Plain bold markup -- the regression control.

This paragraph contains **bold text** that must keep routing through
visit_strong unchanged, byte-identical after the decoupling.

The autodoc "Options" rubric shape.

.. rubric:: Options

.. option:: --sep

   If specified, separate source and build directories.

A rubric carrying a propagated target, inside a list item.

* First bullet text.

  .. _decoupling-rubric-in-list-target:

  .. rubric:: A Rubric In A List Item

  More text after the rubric.

A rubric at true end-of-document.

.. rubric:: Trailing Heading
