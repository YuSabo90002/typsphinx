Paragraph Soft Newline Render Gate
====================================

This fixture exists solely to be compiled to PDF by
``tests/test_paragraph_soft_newline_render_gate.py`` -- a regression gate
for FID-11 (a paragraph authored with reST soft/semantic source line breaks
rendering as a Typst HARD break instead of collapsing to a single space).
It deliberately avoids naming the collapsed sentinel tokens elsewhere in
this document so the test's body sweep is unambiguous.

Plain soft-wrapped paragraph (single merged Text node)
---------------------------------------------------------

SOFTWRAPALPHASENTINEL is a term that continues on the
SOFTWRAPBETASENTINEL line without any inline markup at the break point.

Soft break adjacent to an inline literal
------------------------------------------

Use ``MethodDocumenter`` or
``AttributeDocumenter`` when generating autodoc extension stubs.
