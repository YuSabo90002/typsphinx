Signature Page Boundary Render Gate
======================================

This fixture exists solely to be compiled and per-page-probed by
``tests/test_signature_page_boundary_render_gate.py`` (SIG-09). It is not
meant to be read as prose. The page height used to reach a real page
boundary is applied by the TEST (via a probe preamble prepended to the
already-emitted ``.typ``, per 37-03-PLAN.md Task 2's chosen mechanism (c))
-- this source has no page-geometry directive of its own.

Filler Section
------------------

Filler paragraph one consumes vertical space before the signature under
test, so the signature lands near a real page boundary. Filler paragraph
one consumes vertical space before the signature under test, so the
signature lands near a real page boundary.

Filler paragraph two consumes vertical space before the signature under
test, so the signature lands near a real page boundary. Filler paragraph
two consumes vertical space before the signature under test, so the
signature lands near a real page boundary.

Filler paragraph three consumes vertical space before the signature under
test, so the signature lands near a real page boundary. Filler paragraph
three consumes vertical space before the signature under test, so the
signature lands near a real page boundary.

Filler paragraph four consumes vertical space before the signature under
test, so the signature lands near a real page boundary. Filler paragraph
four consumes vertical space before the signature under test, so the
signature lands near a real page boundary.

Filler paragraph five consumes vertical space before the signature under
test, so the signature lands near a real page boundary. Filler paragraph
five consumes vertical space before the signature under test, so the
signature lands near a real page boundary.

Filler paragraph six consumes vertical space before the signature under
test, so the signature lands near a real page boundary. Filler paragraph
six consumes vertical space before the signature under test, so the
signature lands near a real page boundary.

The Boundary Signature
---------------------------

.. py:function:: sigboundarynamesentinel(sigboundaryparamsentinel, second_param, third_param)

   SIGBOUNDARYBODYFIRSTLINESENTINEL starts the description body's first
   line, immediately after the signature above. More body text follows
   this first line so the paragraph has real content beyond the sentinel.
   Still more trailing body text keeps the paragraph going a little
   further, well past the sentinel line itself.

Trailing Section
--------------------

Trailing filler paragraph one follows the boundary signature's body, so
the fixture has content on both sides of the signature under test.

Trailing filler paragraph two follows the boundary signature's body, so
the fixture has content on both sides of the signature under test.
