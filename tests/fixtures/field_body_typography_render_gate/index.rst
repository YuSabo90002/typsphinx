Field Body Typography Render Gate
====================================

This fixture exists solely to be built through ``-b typst`` (structural
assertions) and compiled to PDF via ``typst.compile()`` (glyph and
text-extraction assertions) by
``tests/test_field_body_typography_render_gate.py`` (Phase 38, FLD-01,
FLD-02, FLD-03, D-05, D-06, D-07, D-13). It is not meant to be read as
prose.

Multi-Value Bulleted Control
================================

.. CONTROL (FLD-02 bulleted half, NON-REGRESSION): a py:function:: with
   TWO :param: entries, each with its own :type:. This already renders as
   a bulleted list pre-phase and must survive the redesign unchanged -- it
   is a non-regression obligation, never a defect case (38-EMISSION-
   CONTRACT.md section 4.1/4.3 property 3). D-13's stray parbreak() at the
   head of each bulleted item is deliberately LEFT IN PLACE (contract
   section 4.5): the break is emitted by visit_paragraph's list-item
   fast-path, which fires for every list item in the document -- not only
   field-list bullets -- and its exact shape is already pinned by
   tests/test_inline_math_after_text_render_gate.py:291.

.. py:function:: field_multi_value_bulleted(alpha, beta)

   :param alpha: The first bulleted parameter.
   :type alpha: str
   :param beta: The second bulleted parameter.
   :type beta: int

Single-Entry Collapsed Param
================================

.. FLD-02 inline half: a py:function:: with exactly ONE :param: entry.
   Docutils' TypedField.make_field can_collapse branch produces a single
   paragraph field body here (not a one-item bulleted list) -- this must
   render as inline prose, never as a bulleted list of one.

.. py:function:: field_single_entry_param(only)

   :param only: The lone parameter, collapsed to one paragraph body.
   :type only: str

Single-Value Fields Returns Rtype Raises
============================================

.. FLD-02 inline half (D-07/D-08): a py:function:: carrying :returns:,
   :rtype: and :raises: in that order, so both the label/value inline
   join AND the "consecutive fields stay in separate paragraphs" trap are
   reachable in one construct. The returns text is a short, stable value
   ("A short stable value.") so a pinned adjacency string can be
   hand-derived from it per contract section 4.3 property 1.

.. py:function:: field_single_value_trio()

   :returns: A short stable value.
   :rtype: str
   :raises ValueError: If something goes wrong.

Resolvable Type Cross Reference
====================================

.. FLD-03 Pitfall 2: a py:class:: defined in this same document, plus a
   py:function:: whose :type: names that class, so Sphinx resolves the
   type into a reference node and the monospace leaf must compose inside
   the emitted link() call (38-RESEARCH.md Pitfall 2). A fixture of only
   builtin types (int, str) would pass even if this composition were
   broken.

.. py:class:: FieldXrefTarget

   A class defined in this document so its name resolves as a
   cross-reference from the function below.

.. py:function:: field_resolvable_xref_type(target)

   :param target: A parameter whose type resolves to a local class.
   :type target: FieldXrefTarget

Name Without Type
=====================

.. FLD-03 empty edge: a :param: entry with a name and description but no
   matching :type: field. Its region must contain exactly one
   bold-monospace call and zero italic-monospace calls.

.. py:function:: field_name_without_type(untyped)

   :param untyped: A parameter with no matching type field.

Non-ASCII Parameter Name
============================

.. FLD-03 encoding edge: a :param: whose name and description contain
   non-ASCII code points, so escaping can be asserted to round-trip
   Python str code points rather than bytes or grapheme clusters, with no
   Unicode normalisation.

.. py:function:: field_nonascii_param(x)

   :param 名前: 説明文です, a non-ASCII parameter name and description.
   :type 名前: str

Collapsed Inline Control
============================

.. CONTROL (contract section 4.3 property 3): a confval::-style directive
   carrying :type: and :default: written on their own field lines -- the
   docutils-collapsed all-inline shape whose one-line rendering via the
   EXISTING inter-field separator (FID-09) must stay byte-identical. This
   construct legitimately DOES share one line; mirrors
   tests/fixtures/confval_field_spacing_render_gate/index.rst's shape.
   Never edited by this plan.

.. confval:: field_collapsed_inline_confval
   :type: ``int`` (a *number*)
   :default: **99**

Single Field List
=====================

.. FLD-02 empty edge: a py:function:: with exactly ONE field in its
   field list (a lone :returns:, no :rtype:/:raises: siblings), so "no
   inter-field separator when there is no sibling field" is reachable.

.. py:function:: field_single_field_list()

   :returns: The only field in this function's field list.

List Item Bullet Single Value Field
===================================

.. FLD-02 list-item adjacency + empty edge (38-VERIFICATION.md gap 1,
   38-REVIEW.md CR-01): the enclosing list item is what makes
   in_list_item True for the nested field-body paragraph below, which is
   exactly what lets D-13's bulleted-item fast-path short-circuit the
   FLD-02 inline join before this plan's fix. Exactly one field
   (:returns:), no sibling fields, so the "lone field, no following
   sibling" empty edge is reachable here too.

* A bullet list item containing a documented function.

  .. py:function:: fld02_listitem_bullet_function(x)

     :returns: fld02 listitem bullet returns sentinel.

List Item Enumerated Consecutive Fields
=======================================

.. FLD-02 list-item ordering edge (38-VERIFICATION.md gap 1,
   38-REVIEW.md CR-01): three consecutive single-value fields (:returns:,
   :rtype:, :raises:) nested inside an enumerated list item, so both
   "each label joins its own value" and "consecutive fields stay on
   separate lines" are reachable in one construct.

#. An enumerated list item containing a documented function.

   .. py:function:: fld02_listitem_enum_function(y)

      :returns: fld02 listitem enum returns sentinel.
      :rtype: str
      :raises ValueError: If the enumerated list item case goes wrong.
