Captioned Table Propagated Target Render Gate
================================================================

This fixture reproduces TBL-03 (Phase 42): a standalone target placed
immediately before a captioned table has its id propagated onto the table
by docutils, but the anchor for that propagated id was discarded by
``depart_table`` rather than reaching the document body, leaving a
same-document reference dangling and aborting the Typst compile.

Target plus a named captioned table
------------------------------------------------------

.. _tbl-target:

.. table:: TBLTGTNAMEDSENTINEL
   :name: tbl-name

   ========  ========
   Column A  Column B
   ========  ========
   Cell      Cell
   ========  ========

Target plus a captioned table with no name
------------------------------------------------------

.. _tbl-target-noname:

.. table:: TBLTGTNONAMESENTINEL

   ========  ========
   Column A  Column B
   ========  ========
   Cell      Cell
   ========  ========

Target plus a captioned table inside a list item
------------------------------------------------------

- Lead-in text before the nested table:

  .. _tbl-target-li:

  .. table:: TBLTGTLISTSENTINEL
     :name: tbl-name-li

     ========  ========
     Column A  Column B
     ========  ========
     Cell      Cell
     ========  ========

Two consecutive targets before one captioned table
------------------------------------------------------

.. _tbl-target-a:
.. _tbl-target-b:

.. table:: TBLTGTTWOSENTINEL
   :name: tbl-name-two

   ========  ========
   Column A  Column B
   ========  ========
   Cell      Cell
   ========  ========

Caption-less control table
------------------------------------------------------

A table with no caption, no name, and no preceding target must stay
byte-unchanged by this fix -- it is not figure-wrapped at all.

.. table::

   ========  ========
   Column A  Column B
   ========  ========
   Cell      Cell
   ========  ========

References back to the propagated targets
------------------------------------------------------

See :numref:`tbl-name` for the named table's own cross-reference.

Every reference below is given explicit link text rather than a bare
reference, because a bare reference to a captioned table defaults its
link text to that table's own caption.

- :ref:`first target link text <tbl-target>`
- :ref:`second target link text <tbl-target-noname>`
- :ref:`third target link text <tbl-target-li>`
- :ref:`fourth target link text <tbl-target-a>`
- :ref:`fifth target link text <tbl-target-b>`
- :ref:`sixth target link text <tbl-name-li>`
- :ref:`seventh target link text <tbl-name-two>`
