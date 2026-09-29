Graphviz Render Gate
======================

This fixture exists solely to be compiled to PDF by
``tests/test_graphviz_render_gate.py``. Every label asserted by that module
is an explicitly QUOTED DOT label carrying a distinctive sentinel token.
Bare DOT node identifiers are rendered by diagraph through Typst *math*
mode -- ``a`` extracts as ``U+1D44E`` and ``alpha`` as ``U+03B1`` -- so an
assertion on a bare identifier is invalid even when it happens to pass.

Inline graphviz
-----------------

.. graphviz::

   digraph inline_form {
       a [label="Zylkefirst"];
       b [label="Quorbatsecond"];
       a -> b;
   }

digraph directive
-------------------

.. digraph:: digraph_form

   a [label="Vandrimthird"];
   b [label="Pelunkofourth"];
   a -> b;

graph directive
-----------------

.. graph:: graph_form

   a [label="Skarmelfifth"];
   b [label="Threbixsixth"];
   a -- b;

Japanese labels
-----------------

.. graphviz::

   digraph japanese_form {
       a [label="日本語ラベル"];
       b [label="Ondricseventh"];
       a -> b;
   }
