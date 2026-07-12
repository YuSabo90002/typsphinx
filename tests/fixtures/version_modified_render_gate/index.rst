Version Modified Render Gate
=============================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (VER-01, GATE-01). It is not meant to be
read as prose -- it exercises the ``versionmodified``/``visit_inline``
classed-dispatch fix against a real Typst compile, covering all four
version-directive kinds plus the content-less (period-terminated) case.

Version Added With Body
------------------------

.. versionadded:: 0.6

   VERADDEDBODYSENTINEL7Q1 is the sentinel for this body-bearing
   ``versionadded`` case.

Version Added Content-Less
----------------------------

.. versionadded:: 0.6

Version Changed With Body
----------------------------

.. versionchanged:: 0.6

   VERCHANGEDBODYSENTINEL8Q2 is the sentinel for this ``versionchanged``
   case.

Deprecated With Body
----------------------

.. deprecated:: 0.6

   VERDEPRECATEDBODYSENTINEL9Q3 is the sentinel for this ``deprecated``
   case.

Version Removed Label Only
-----------------------------

.. versionremoved:: 0.6
