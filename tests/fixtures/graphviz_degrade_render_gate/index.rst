Graphviz Degrade Render Gate
==============================

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, D-04). It exercises the DEG-01/
DEG-02 graceful-degrade placeholder fix against a real Typst compile: both
directives below must compile without aborting the build, the placeholder
wording must be present in the extracted PDF text, and no raw DOT source or
diagram-spec text may leak.

Graphviz Diagram
------------------

.. graphviz::

   digraph example {
       a -> b;
   }

Inheritance Diagram
----------------------

.. inheritance-diagram:: mymodule.DerivedWidget
