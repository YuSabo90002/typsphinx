Codly Caption Listitem Leak Render Gate
=========================================

This fixture exists solely to be compiled to PDF by
``tests/test_codly_caption_listitem_leak_render_gate.py`` -- a regression
gate for a markup/code-mode defect that existing string-agreement tests
never caught because they never real-compiled the emitted output. It is not
meant to be read as prose, and it deliberately avoids naming the leaked
tokens so the test's body sweep is unambiguous.

Captioned code block nested in a numbered list item
------------------------------------------------------

A captioned code block nested inside a numbered list's list item combines
two contexts at once (a captioned figure's markup mode AND a list-item
code-mode wrapper); its per-block codly configuration must still execute
rather than leaking as visible prose.

1. The first item is plain prose with no code block.
2. The second item contains a captioned code block.

   .. code-block:: python
      :caption: Captioned example in a list item

      LISTITEMCAPSENTINEL = 1

3. The third item is plain prose again.
