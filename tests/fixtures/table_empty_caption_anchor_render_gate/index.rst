Table Empty Caption Anchor Render Gate
================================================================

This fixture reproduces TBL-05 (Phase 43): a captioned table whose title
renders to the empty string anchors its ids on NEITHER ``visit_table``'s
structural pre-check nor ``depart_table``'s rendered-caption truthiness
check, leaving a propagated target's anchor unemitted and a same-document
``:ref:`` dangling -- aborting the whole ``typst.compile()`` at Typst's
semantic label-resolution pass.

Empty-rendered caption
------------------------------------------------------

.. role:: raw-html(raw)
   :format: html

.. _tbl-target:

.. table:: :raw-html:`<span></span>`

   +-------+-------+
   | TEC1A | TEC1B |
   +-------+-------+

See :ref:`the table <tbl-target>`.

Real-caption numbering control
------------------------------------------------------

This section is the D-05 control: if the empty-rendered-caption table above
were figure-wrapped it would consume a table number and this table would
render as "Table 2" instead of "Table 1".

.. table:: TECREALCAP
   :name: tec-real-name

   +-------+-------+
   | TEC2A | TEC2B |
   +-------+-------+

See :numref:`tec-real-name` for the real-caption table's own cross-reference.
