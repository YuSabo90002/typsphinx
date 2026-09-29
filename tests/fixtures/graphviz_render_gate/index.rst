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

.. The two sections below carry S03's option-routing proofs (R004, R005).
   They are ADDITIVE: the four diagrams above and their seven sentinels
   belong to S02's R001/R002/R010/R012 proofs and must stay untouched.
   This note lives in an rST comment rather than visible prose so no
   sentinel-absence assertion in the module can be satisfied by the
   fixture's own explanatory text.

Layout option
---------------

.. The DOT below is deliberately a 3-node CYCLE: a cycle has no ranking,
   which is what makes neato's force-directed placement diverge visibly
   from dot's ranked layout, so a dropped ``engine:`` is observable.

.. graphviz::
   :layout: neato

   digraph layout_form {
       a [label="Brindlewockeighth"];
       b [label="Cavorteenninth"];
       c [label="Drimplenoxtenth"];
       a -> b;
       b -> c;
       c -> a;
   }

Alt option
------------

.. graphviz::
   :alt: Hoskrivendale alt sentinel

   digraph alt_form {
       a [label="Ferrymantleeleventh"];
       b [label="Glaskivoretwelfth"];
       a -> b;
   }
