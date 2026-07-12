Trivial Blocks Render Gate
===========================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (BLK-01/04/05/06). It is not meant to be
read as prose -- it exercises the transition, glossary, tabularcolumns, and
abbreviation handlers against a real Typst compile.

Transition
----------

BEFORETRANSITIONSENTINEL paragraph before the rule.

----

AFTERTRANSITIONSENTINEL paragraph after the rule.

Glossary
--------

.. glossary::

   Widget
      GLOSSARYDEFSENTINEL a thing that does stuff.

Tabularcolumns
--------------

.. tabularcolumns:: |LEAKCOLSPECSENTINEL|p{5cm}|

.. list-table::
   :header-rows: 1

   * - Column A
     - Column B
   * - value1
     - value2

Abbreviation
------------

The :abbr:`API (Application ABBREXPANSIONSENTINEL Interface)` is used
throughout this project.
