Reference-with-target and nested-block render gate
==================================================

Sub-construct (a): a figure caption whose inline content is a plain text run,
then a named external hyperlink (which docutils splits into a reference node
immediately followed by an inline target node), then more inline text in the
same caption. This mirrors the corpus intl figure caption where the
reference-with-target markup wrapper juxtaposes against a following text run.

.. figure:: /_static/pixel.png

   Workflow figure REFTARGETSENTINEL created by
   `plantuml <https://plantuml.com>`_.)

Sub-construct (b): a bullet-list item whose lead-in paragraph is followed by
an over-indented sub-block, which docutils wraps in a block quote containing a
nested bullet list plus a trailing paragraph. This mirrors the corpus changes
entry where the block quote and the nested list juxtapose against the
preceding list-item inline content with no separator.

* NESTEDBLOCKSENTINEL functions:

   * nested alpha
   * nested beta

   Trailing paragraph after the nested block.
