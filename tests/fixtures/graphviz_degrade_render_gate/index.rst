Graphviz Degrade Render Gate
==============================

.. Scope note (kept as a source-only comment, never rendered): DEG-01's
   graph half no longer belongs in this fixture -- inline DOT now renders
   as a real diagram via @preview/diagraph, and that behaviour is gated by
   tests/test_graphviz_render_gate.py. This fixture deliberately declares
   no graph directive at all, so a leak of the DOT source keyword or of
   edge-arrow syntax into the compiled PDF could only come from the
   inheritance-diagram path. Keep this note in a comment: the gate asserts
   those tokens are absent from the extracted PDF text, so naming them in
   visible prose would fail the gate on the fixture's own words.

This fixture exists solely to be compiled to PDF by
``tests/test_pdf_render_gate.py`` (GATE-01, D-04). It exercises the DEG-02
graceful-degrade placeholder fix against a real Typst compile: the
inheritance-diagram directive below must compile without aborting the
build, the placeholder wording must be present in the extracted PDF text,
and no raw diagram-spec text may leak.

Inheritance Diagram
----------------------

.. inheritance-diagram:: mymodule.DerivedWidget
