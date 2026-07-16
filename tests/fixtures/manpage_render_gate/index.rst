Manpage Render Gate
====================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, MAN-01). It exercises the
``:manpage:`` role's ``visit_manpage``/``depart_manpage`` delegation to
``visit_emphasis``/``depart_emphasis`` against a real Typst compile, in all
three separator/mode contexts a manpage role can appear in (16-RESEARCH.md
Pitfall 4): a plain paragraph (code-mode default), a bullet list item, and a
figure caption (markup-mode context, exercising the ``#`` prefix toggle).

This file intentionally contains NO other emphasis/italic markup -- the test
counts ``emph({`` occurrences in the generated Typst source and the three
``:manpage:`` uses below must be the only source of that wrapper.

Plain Paragraph
----------------

See :manpage:`ls(1)` for details on listing directory contents.

List Item
---------

- :manpage:`grep(1)` searches text using patterns.

Figure Caption
---------------

.. figure:: image.png

   A screenshot referencing :manpage:`tar(1)` in its caption.
