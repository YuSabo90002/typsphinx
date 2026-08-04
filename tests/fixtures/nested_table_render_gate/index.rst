Nested Table Render Gate
==========================

This fixture reproduces TBL-04: a table nested inside another table's cell
silently clobbers the enclosing table's accumulated cells, column count,
column widths, caption, header-row flag and span counters, because the
translator's table state is a set of unconditionally-reset SCALARS rather
than a stack that survives nesting. The failure mode is STRUCTURAL, not a
compile fatal -- the broken output compiles cleanly with no warning, so
every assertion in the paired test file checks the emitted ``.typ`` /
extracted PDF text directly rather than the build's exit status alone.

Section 1: list-table in list-table
--------------------------------------

.. list-table:: NT1OUTERCAP
   :header-rows: 1

   * - NT1HEADA
     - NT1HEADB
   * - NT1PLAIN
     - .. list-table::

          * - NT1INNERA
            - NT1INNERB

Section 2: grid table in list-table
--------------------------------------

.. list-table:: NT2OUTERCAP
   :header-rows: 1

   * - NT2HEADA
     - NT2HEADB
   * - NT2PLAIN
     - .. table::

          +-----------+-----------+
          | NT2INNERA | NT2INNERB |
          +-----------+-----------+

Section 3: list-table in grid table
--------------------------------------

.. table:: NT3OUTERCAP

   +----------------------------------+-----------+
   | .. list-table::                  | NT3OUTERD |
   |                                  |           |
   |    * - NT3INNERA                 |           |
   |      - NT3INNERB                 |           |
   +----------------------------------+-----------+

Section 4: three-level nest
--------------------------------------

.. list-table:: NT4L1CAP

   * - NT4L1PLAIN
     - .. list-table::

          * - NT4L2PLAIN
            - .. list-table::

                 * - NT4L3A
                   - NT4L3B

Section 5: nested table inside a header cell
--------------------------------------------------

.. list-table::
   :header-rows: 1

   * - .. list-table::
          :header-rows: 1

          * - NT5INNERHEAD
          * - NT5INNERBODY
     - NT5HEADB
   * - NT5BODYA
     - NT5BODYB

Section 6: adjacency, empty cell, and sibling tables
--------------------------------------------------------

.. list-table::

   * - NT6TEXTBEFORE

       .. list-table::

          * - NT6INNERA
     -
   * - NT6ROWTWO
     -

.. list-table::

   * - NT7SIBA

.. list-table::

   * - NT7SIBB

Section 7: top-level control
--------------------------------------

This section must stay byte-unchanged by the TBL-04 fix -- a caption-less
top-level table with no nested table anywhere in it.

.. list-table::

   * - NT8CTRLA
     - NT8CTRLB
