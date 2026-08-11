Nested Figure Render Gate
==========================

This fixture reproduces FIG-01 (Phase 43): a ``legend`` node (docutils' name
for a figure's body content beyond its first caption paragraph) has no
``visit_legend``/``depart_legend`` handler, so today's translator emits an
``image(...)`` call directly juxtaposed against the legend's unwrapped
children -- a real ``typst.compile()`` fatal, not merely a dropped caption
(43-RESEARCH.md Pitfall 4).

Figure nested in a figure's legend
------------------------------------

.. figure:: img.png

   NF1OUTERCAP

   .. figure:: img.png

      NF1INNERCAP

Plain-text legend, no nested figure
---------------------------------------

This section is broken TODAY with no nesting involved at all -- the root
cause is the missing ``legend`` handler, not the nesting. The fix must not be
narrowed to "only when the legend contains a figure" (Pitfall 4).

.. figure:: img.png

   NF2CAP

   NF2LEGENDTEXT

Image-only control
----------------------

This section must stay byte-unchanged by the FIG-01 fix (SC#4). No legend
child exists here, so the ``{...}`` body wrap this phase adds must never
apply to it.

.. figure:: img.png

   NF3CTRLCAP

Legend with no caption
--------------------------

An explicit ``.. legend::`` RST directive does not exist in docutils --
verified this session (``publish_doctree`` on a bare ``.. legend::`` block
raises "Unknown directive type"). A legend with NO caption is instead
produced by an empty comment (``..``) standing in for the caption slot,
followed by a plain paragraph, which docutils then classifies as the
figure's ``legend`` child with no ``caption`` sibling at all -- verified this
session via a direct ``publish_doctree`` probe (recorded in
43-GATE-EVIDENCE-03.md).

.. figure:: img.png

   ..

   NF4LEGENDONLY

Legend containing a figure that itself has a caption and a legend
-------------------------------------------------------------------

Reproduces 43-REVIEW.md CR-01: the outer figure's legend contains an INNER
figure that itself has BOTH a caption AND its own legend (not merely a
caption, as Section 1 above does). ``visit_legend``/``depart_legend``'s
pre-fix save/restore used two flat instance attributes instead of a real
stack, so the inner legend's ``visit_legend`` clobbers the outer legend's
saved values with its own already-mutated ``True``/``True`` before the
outer ``depart_legend`` ever restores them -- leaking ``in_list_item =
True`` into every sibling for the rest of the document. Section 1's inner
figure has no legend of its own, so it does NOT trigger this; the inner
figure here needs both a caption and a legend to reproduce the clobber.

.. figure:: img.png

   NF5OUTERCAP

   NF5OUTERLEGEND

   .. figure:: img.png

      NF5INNERCAP

      NF5INNERLEGEND

NF5TRAILINGPARA sentinel text.
