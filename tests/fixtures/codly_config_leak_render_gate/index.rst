Codly Config Leak Render Gate
==============================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` -- a regression gate for two related
per-block code-highlighting defects that existing string-agreement tests
never caught because they never real-compiled the emitted output. It is not
meant to be read as prose, and it deliberately avoids naming the leaked
tokens so the test's body sweep is unambiguous.

Captioned code block with emphasis (markup context)
----------------------------------------------------

A captioned code block is emitted inside a Typst markup content block, so
its per-block configuration must be emitted as an executed call, never as
bare markup text that would be typeset as literal prose.

.. code-block:: python
   :caption: Captioned example
   :emphasize-lines: 2

   CODLYCAPFIRSTSENTINEL = 1
   CODLYCAPEMPHSENTINEL = 2
   CODLYCAPTHIRDSENTINEL = 3

Top-level code block with emphasis (code-mode context)
-------------------------------------------------------

A plain top-level code block sits in a code-mode context, so its per-block
configuration is emitted bare -- but the emphasis call must use a valid API
or the whole compile aborts.

.. code-block:: python
   :emphasize-lines: 3

   CODLYTOPFIRSTSENTINEL = 1
   CODLYTOPSECONDSENTINEL = 2
   CODLYTOPEMPHSENTINEL = 3
