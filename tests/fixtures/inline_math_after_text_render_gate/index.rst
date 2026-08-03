Inline Math After Text Render Gate
===================================

Construct A: control -- top-level paragraph (already works today; this
shape must stay byte-identical, it is a regression guard, not a defect
reproduction).

With space before math: :math:`E = m c^2` after.

No space where\ :math:`E = m c^2`\ immediately follows.

Construct B: bullet list item -- prose then inline math then prose (the
primary failing shape).

* Text before math :math:`E = m c^2` text after.

Construct C: collapsed field bodies -- the concat context. The ``:type:``
value is the sole inline math (math as the FIRST expression in the concat
context, no leading separator). The ``:default:`` value is prose then math
(math following a sibling, exactly one separator).

.. confval:: math_inline_default
   :type: :math:`x`
   :default: The value of :math:`x` computed inline

   A description paragraph so the confval also exercises the block
   field-body and normal-paragraph path.

Construct D: definition-list term -- a second concat context.

Term :math:`E = m c^2`
    Definition body text.

Construct E: display math inside a list item -- the visit_math_block scope.

* Text before block math.

  .. math::

     E = m c^2

  Text after block math.

Construct F: list item whose sole content is inline math -- the
single-element edge.

* :math:`a+b`

Construct G: a labeled display-math equation inside a list item -- the
_emit_id_anchors + list-item-separator ordering interaction (WR-02).

* Text before labeled block math.

  .. math:: G = m a
     :label: construct-g-labeled-eq

  Text after labeled block math.

Construct H: a list item whose sole content is display math -- the
block-math single-element edge (MATH-02). With no following sibling
inside the item, there is nothing for the trailing separator flag to
affect, so this construct's emission must be identical before and after
the MATH-02 fix.

*
  .. math::

     H = m g h
