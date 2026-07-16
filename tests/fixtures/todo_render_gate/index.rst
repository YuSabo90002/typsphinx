Task Box Render Gate
=====================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, TODO-01). It exercises the
``visit_todo_node``/``depart_todo_node`` fix against a real Typst compile:
the ``.. todo::`` body must render inside a gentle-clues ``task()`` box
titled "Todo" (D-01), and the literal word "Todo" must appear in the
compiled PDF text exactly once -- sourced only from the box's own dynamic
title, never from this heading or the project title.

.. todo::

   TODOBODYSENTINEL9X4 plus a few plain words describing this task item.
