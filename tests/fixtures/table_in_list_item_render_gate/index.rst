Table In List Item Render Gate
================================

This fixture reproduces the corpus fatal where a table nested inside a
bullet-list item, following lead-in text, is emitted with no leading
separator -- juxtaposing ``depart_table``'s ``table(`` against the preceding
text's closing ``)`` in the code-mode content block, aborting the compile
with "expected semicolon or line break". Mirrors ``latex.typ:2382`` (Sphinx's
own corpus).

- Text styling commands:

  .. list-table::
     :header-rows: 1

     * - Command
       - Description
     * - ``\textbf``
       - Bold text
     * - ``\textit``
       - Italic text

Top-level table
-----------------

A table at the top level (not nested in a list item) must stay
byte-unchanged by this fix.

.. list-table::
   :header-rows: 1

   * - Header A
     - Header B
   * - Row A
     - Row B
