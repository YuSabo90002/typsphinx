Table Width Render Gate
=========================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, LEN-01). It exercises the
``depart_table`` ``:width:`` wiring against a real Typst compile across all
three docutils table-directive types (``.. table::``, ``.. csv-table::``,
``.. list-table::`` -- all converging on the single ``nodes.table`` type via
``Table.set_table_width()``), each carrying a ``:width:`` option. None of the
three directives below carries a title argument (a table title child would
take an unrelated ``visit_title`` path).

.. table::
   :width: 200px

   ====================  ========
   Column A               Column B
   ====================  ========
   TABLEPXSENTINEL7Q4     value
   ====================  ========

.. list-table::
   :width: 50%

   * - TABLELISTSENTINEL8Q5
     - value

.. csv-table::
   :width: 1ex

   "TABLECSVSENTINEL9Q6", "value"
