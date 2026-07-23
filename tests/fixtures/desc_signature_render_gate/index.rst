Desc Signature Render Gate
===========================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (DESC-01..04, GATE-01). It is not meant to
be read as prose -- it exercises the four autodoc signature sub-part
handlers landed in Phase 12 Plan 03 against a real Typst compile.

Return Type Arrow
-------------------

.. py:function:: get_value() -> int

Genuine Multi-Line Signature
-------------------------------

A C++ template declaration is the confirmed construction that produces TWO
genuine ``desc_signature_line`` siblings under one ``desc_signature`` (the
templatePrefix line, then the main declarator line) -- resolving Open
Question 1 from 12-RESEARCH.md.

.. cpp:function:: template<typename DESCLINEONESENTINEL4Q1> void DESCLINETWOSENTINEL5Q2(int x)

Nested Optional Parameters
-----------------------------

.. py:function:: printf(fmt[, args[, more]])

Inline Signature Fragment
----------------------------

The type is :cpp:expr:`DescInlineExprToken`.
