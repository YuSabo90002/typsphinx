Typst Lang Gate German Linkage Proof
======================================

This fixture exists solely to be compiled by
``tests/test_typst_lang_gate.py`` (GATE-01, CONF-07, SC#1's D-07 linkage
half). It carries one captioned table (Phase 25's motivating case for this
whole phase) and one captioned figure, so both the table and figure
supplement words can be read out of the compiled PDF and compared against
the German forms Typst generates when ``lang: "de"`` reaches
``set text(...)``.

.. table:: Lang Gate Table Caption

   ========  ========
   Column A  Column B
   ========  ========
   Cell      Cell
   ========  ========

.. figure:: image.png
   :width: 100px

   Lang Gate Figure Caption.
