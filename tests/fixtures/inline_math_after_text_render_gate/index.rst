Inline Math After Text Render Gate
===================================

Construct A: control -- top-level paragraph (already works today; this
shape must stay byte-identical, it is a regression guard, not a defect
reproduction).

With space before math: :math:`E=mc^2` after.

No space where\ :math:`E=mc^2`\ immediately follows.

Construct B: bullet list item -- prose then inline math then prose (the
primary failing shape).

* Text before math :math:`E=mc^2` text after.

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

Term :math:`E=mc^2`
    Definition body text.

Construct E: display math inside a list item -- the visit_math_block scope.

* Text before block math.

  .. math::

     E = mc^2

  Text after block math.

Construct F: list item whose sole content is inline math -- the
single-element edge.

* :math:`a+b`
