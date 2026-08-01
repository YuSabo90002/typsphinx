Signature Break And Arrow Gate
================================

This fixture exists solely to be built through ``-b typst`` (structural
assertions) and compiled to PDF via ``typst.compile()`` (glyph and
text-extraction assertions) by
``tests/test_signature_break_and_arrow_gate.py`` (Phase 37, GATE-01,
SIG-06/SIG-08/D-11). It is not meant to be read as prose.

SIG-08 Nested Desc Break
==========================

.. The defect case: a py:class:: with a one-line body containing a nested
   py:method:: with its own one-line body. On the pre-phase translator this
   emits TWO consecutive parbreak() statements with nothing between them --
   the inner desc's own unconditional break, immediately followed by the
   outer desc's own unconditional break, because neither the inner class
   body nor anything else intervenes before the outer desc departs.

.. py:class:: SigBreakOuterClassOne

   Outer class one body.

   .. py:method:: sig_break_inner_method_one()

      Inner method one body.

SIG-08 Content Follows Nested Member
=======================================

.. The "content follows the nested member" case: a second py:class:: whose
   body holds a nested py:method:: AND a trailing paragraph after it. A
   naive desc-nesting-depth-counter fix would break this shape by
   suppressing the inner desc's break unconditionally, running the
   method's body and the trailing paragraph together. The correct fix
   (37-EMISSION-CONTRACT.md section 8's emission-position marker) must
   keep exactly one break between the nested member and the trailing
   paragraph, both before and after the fix.

.. py:class:: SigBreakOuterClassTwo

   Outer class two body.

   .. py:method:: sig_break_inner_method_two()

      Inner method two body.

   Trailing paragraph after the nested member.

SIG-08 Sibling Bodyless Control
==================================

.. CONTROL: mirrors tests/fixtures/desc_bodyless_concat_render_gate/
   index.rst -- two back-to-back body-less confval desc siblings (no
   nesting). Exactly one parbreak() must separate them, both before and
   after the SIG-08 fix -- this shape is never doubled because it is not
   nested, so it must never be converted into a defect case.

.. confval:: sig_break_confval_one
   :type: str
   :default: ``"a"``

.. confval:: sig_break_confval_two
   :type: str
   :default: ``"b"``

SIG-06 Return Arrow
======================

.. A py:function:: with an explicit return annotation. Pre-phase this
   emits the ASCII text(" -> ") literal (37-EMISSION-CONTRACT.md section
   7); the real arrow glyph U+2192 must reach the compiled PDF's
   extracted text after the fix, and the ASCII two-character arrow
   sequence must be absent.

.. py:function:: sig_arrow_get_value() -> int

D-11 Optional Group Separator Defect
=======================================

.. The D-11 defect case: this desc_optional group ([timeout]) HAS a
   following sibling (the kwargs parameter) at the desc_optional node
   level, which is precisely why the separator Sphinx's own HTML writer
   renders inside the bracket is currently lost (37-EMISSION-CONTRACT.md
   section 6.1).

.. py:function:: connect(host, port=8080, [timeout], **kwargs)

   Connect body.

D-11 Nested Optional Non-Regression Control
===============================================

.. CONTROL: the classic nested-optional printf shape. Both desc_optional
   nodes here ([args, [more]] and the nested [more]) are LAST children,
   so neither gains a separator under the D-11 fix -- this rendering must
   stay byte-unchanged. Never convert this into the defect case.

.. py:function:: printf(fmt[, args[, more]])
