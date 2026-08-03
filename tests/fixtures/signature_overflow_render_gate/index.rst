Signature Overflow Render Gate
================================

This fixture exists solely to be compiled and text/geometry-probed by
``tests/test_signature_overflow_render_gate.py`` (SIG-07). It is not meant
to be read as prose.

Synthetic Overflow Case
--------------------------

.. SYNTHETIC (37-RESEARCH.md Pitfall 2 / 37-EMISSION-CONTRACT.md section 10):
   no real Sphinx ``doc/`` corpus signature reaches this width at the
   production 453.54pt text column -- the corpus's own worst case
   (``sphinx.util.parsing.nested_parse_to_nodes``, 41 chars) fits
   comfortably. This 111-character dotted module path is a deliberately
   constructed, over-length identifier: the ONLY construct that can drive
   the SIG-07 gate RED against the untouched translator. It must never be
   replaced by a real corpus signature, and it must never be "fixed" by
   shortening it.

.. py:class:: typsphinx.overflow.probe.deeply.nested.package.namespace.segment.alpha.beta.gamma.delta.OverflowProbeDocumenter(directive)

   A synthetic class used only to overflow the production text column.

Real-Corpus Non-Regression Control
--------------------------------------

.. CONTROL (37-RESEARCH.md Pitfall 2 / 37-EMISSION-CONTRACT.md section 10):
   this reproduces, verbatim, the real Sphinx v9.1.0 worst-case qualified
   name found in the ``doc/`` corpus scan --
   ``sphinx.util.parsing.nested_parse_to_nodes`` (41 characters). It fits
   the 453.54pt production column BOTH before and after the SIG-07 fix, and
   must stay green throughout. Do NOT convert this into the RED case, and
   do NOT "improve" it into something narrower.

.. py:function:: sphinx.util.parsing.nested_parse_to_nodes(state: RSTState, text: str | StringList, *, source: str = '<generated text>', offset: int = 0, allow_section_headings: bool = True, keep_title_context: bool = False) -> list[Node]

   Reproduced verbatim from ``sphinx/util/parsing.py`` (Sphinx 9.1.0).
