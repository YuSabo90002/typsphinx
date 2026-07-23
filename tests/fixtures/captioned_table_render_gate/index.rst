Captioned Table Render Gate
=============================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, TBL-01, TBL-02, D-06). It
exercises the ``depart_table`` figure-wrap + single ``<label>`` fix across
two consecutive captioned tables (the stale-buffer proof -- the SECOND
table's caption must not be lost), a caption+``:width:`` composition case,
a ``:numref:``/``:ref:``-resolves case, and a captioned ``csv-table``/
``list-table`` case (D-05).

.. table:: TBLCAPFIRSTSENTINEL
   :name: first-table

   ========  ========
   Column A  Column B
   ========  ========
   Cell      Cell
   ========  ========

.. table:: TBLCAPSECONDSENTINEL
   :name: second-table

   ========  ========
   Column C  Column D
   ========  ========
   Cell      Cell
   ========  ========

.. table:: TBLCAPWIDTHSENTINEL
   :name: width-table
   :width: 50%

   ========  ========
   Column E  Column F
   ========  ========
   Cell      Cell
   ========  ========

See :numref:`first-table` and :ref:`Ref Link <first-table>` for the
resolved cross-reference proof. The ``:ref:`` role is given explicit link
text (rather than a bare reference) because a bare ``:ref:`` to a
captioned table defaults its link text to the target's own caption text,
which would make that caption's sentinel appear a second time in the
extracted PDF and break the exactly-once sentinel assertion this gate
relies on.

.. csv-table:: TBLCAPCSVSENTINEL
   :name: csv-table-name

   "Column A", "Column B"
   "Cell", "Cell"

.. list-table:: TBLCAPLISTSENTINEL
   :name: list-table-name

   * - Column A
     - Column B
   * - Cell
     - Cell
