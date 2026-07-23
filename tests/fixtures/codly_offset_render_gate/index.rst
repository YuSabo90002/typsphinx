Codly Offset Render Gate
=========================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` -- a regression gate for the GATE-02
corpus fatal ``TypstError: unexpected argument: start``, which fired
because codly 1.3.0's ``codly()`` function has no ``start`` parameter (it
was renamed to ``offset``, an additive delta). It is not meant to be read
as prose.

Explicit lineno-start
----------------------

.. code-block:: python
   :linenos:
   :lineno-start: 5

   CODLYEXPLICITSTARTSENTINEL = 1
   second_line = 2
   third_line = 3

Plain linenos (code-block)
---------------------------

.. code-block:: python
   :linenos:

   CODLYPLAINLINENOSSENTINEL = 1
   second_line = 2

Plain linenos (literalinclude)
--------------------------------

Sphinx's ``literalinclude`` directive always populates
``highlight_args['linenostart']`` (defaulting to 1) even without an
explicit ``:lineno-start:`` option -- this is the exact construct that
produced 20 fatal occurrences across 4 real Sphinx tutorial docs.

.. literalinclude:: included_snippet.py
   :language: python
   :linenos:
