Desc Content Indent Render Gate
==================================

This fixture exists solely to be built through ``-b typst`` (structural
assertions) and compiled to PDF via ``typst.compile()`` (left-edge and
text-extraction assertions) by
``tests/test_desc_content_indent_render_gate.py`` (Phase 38, GATE-01,
IND-01..IND-05, FLD-01, D-04, D-11). It is not meant to be read as prose.

IND-01/02/03/05/FLD-01 Three-Level Nest
==========================================

.. The defect case (pre-phase): a py:class:: with a one-paragraph body,
   containing a py:method:: with its own one-paragraph body and its own
   field list, containing a py:attribute:: with its own one-paragraph
   body. On the pre-phase translator visit_desc_content/depart_desc_content
   are both `pass`, so every body sits flush with its own signature at
   the same left edge -- IND-01 (body indented past its own signature),
   IND-02 (cumulative with depth) and IND-03 (the nested method's own
   signature aligns with the class body and gets no further step) are all
   judged on this single construct (38-CONTEXT.md D-01).

.. py:class:: IndFldNestOuterClass

   Outer class body first paragraph. ind_fld_nest_outer_class_body_first_paragraph_sentinel

   .. py:method:: ind_fld_nest_inner_method(value)

      Inner method body paragraph. ind_fld_nest_inner_method_body_paragraph_sentinel

      :param value: A parameter of the nested method.
      :type value: str
      :returns: ind_fld_nest_returns_sentinel
      :rtype: str

      .. py:attribute:: ind_fld_nest_inner_attr

         Inner attribute body paragraph. ind_fld_nest_inner_attr_body_paragraph_sentinel

   Outer class body resumes here, after the nested member closes.
   ind_fld_nest_outer_class_body_resumes_paragraph_sentinel

IND-05 Sibling Top-Level Desc After The Nest
================================================

.. The defect case (pre-phase): a top-level py:function:: immediately
   following the three-level nest above. IND-05's whole proof is that
   depth cannot leak into this sibling -- there is no depth counter to
   fail to reset (D-01); the wrapper simply closes when the outer
   py:class::'s own desc_content departs.

.. py:function:: ind_fld_nest_sibling_toplevel_function(x)

   Sibling top-level function body paragraph. ind_fld_nest_sibling_toplevel_function_body_paragraph_sentinel

Body-less Desc CONTROL
=========================

.. CONTROL: mirrors tests/fixtures/desc_bodyless_concat_render_gate/
   index.rst -- two back-to-back body-less confval desc siblings (no
   nesting, no body paragraph). A desc_content node with zero children
   still gets a wrapper pair and must still compile, with exactly one
   break separating the siblings (contract section 2.4).

.. confval:: ind_bodyless_confval_one
   :type: str
   :default: ``"a"``

.. confval:: ind_bodyless_confval_two
   :type: str
   :default: ``"b"``

List-Item Desc CONTROL
=========================

.. CONTROL: a py:function:: nested inside a bullet-list item, exercising
   the block-visitor separator interaction the executor of the next plan
   must decide under D-12 (contract section 2.6) -- whether
   visit_desc_content needs the same leading-newline separator guard
   visit_block_quote already carries.

* A list item containing a desc.

  .. py:function:: ind_list_item_function(x)

     List item function body paragraph. ind_list_item_function_body_paragraph_sentinel

Table-Cell CONTROL
======================

.. CONTROL, deliberately NOT a desc (discovery, recorded verbatim in
   38-GATE-EVIDENCE-01.md): building this section with a real desc (of
   ANY shape -- with or without an id, parameters, or a body) inside a
   list-table cell was attempted and found to abort the ENTIRE Typst
   compile with "expected semicolon or line break", regardless of Phase
   38's own changes -- depart_desc_signature's own two
   self.body.append(...) calls (typsphinx/translator.py:5051, 5053,
   Phase 37, byte-identical whether or not the signature carries an id)
   bypass table-cell routing unconditionally, so the signature's closing
   bytes always juxtapose against whatever code-mode statement follows
   inside the cell -- confirmed with a minimal repro (a single bare
   py:attribute::, no fields, no body). A field list inside a table cell
   was independently confirmed to hit the SAME class of defect via
   visit_field_name's self.body.append("strong(") (translator.py:5403),
   exactly matching 38-EMISSION-CONTRACT.md section 3.1's five named
   sites. Both are PRE-EXISTING defects this plan does not touch --
   depart_desc_signature is Phase 37's completed work (not in
   38-CONTEXT.md's in-scope handler list), and the field_list-family
   sites are in Phase 38's scope but owned by a LATER plan, not this
   one. Since this plan's fixture must itself compile (Task 1's
   acceptance criteria), this section keeps only a plain, desc-free
   table as a non-regression baseline; the desc-in-table-cell/
   field-list-in-table-cell falsifier the emission contract's section
   2.1 describes must be added once those sites are fixed.

.. list-table:: Table With Only Plain Content
   :header-rows: 1

   * - Column
     - Description
   * - ind_table_cell_plain_row
     - Plain paragraph content in a table cell (no desc, no field list).
       ind_table_cell_plain_body_sentinel

Page-Boundary Desc (D-11, SIG-09)
=====================================

.. The page-boundary case: enough filler paragraphs before a final
   py:class:: that, under this fixture's deliberately enlarged fontsize
   (conf.py's typst_elements, chosen so this is reproducible rather than
   incidental), its signature lands near a page boundary and its body
   crosses onto the next page. D-11 requires block(sticky: true, ...) to
   survive the new desc_content wrapper: the signature and the first line
   of its body must stay on the same page, and a body that crosses a page
   break must keep the SAME left-edge column on the following page.

Filler paragraph one before the page-boundary class. ind_page_boundary_filler_paragraph_1_sentinel

Filler paragraph two before the page-boundary class. ind_page_boundary_filler_paragraph_2_sentinel

Filler paragraph three before the page-boundary class. ind_page_boundary_filler_paragraph_3_sentinel

Filler paragraph four before the page-boundary class. ind_page_boundary_filler_paragraph_4_sentinel

Filler paragraph five before the page-boundary class. ind_page_boundary_filler_paragraph_5_sentinel

Filler paragraph six before the page-boundary class. ind_page_boundary_filler_paragraph_6_sentinel

Filler paragraph seven before the page-boundary class. ind_page_boundary_filler_paragraph_7_sentinel

Filler paragraph eight before the page-boundary class. ind_page_boundary_filler_paragraph_8_sentinel

Filler paragraph nine before the page-boundary class. ind_page_boundary_filler_paragraph_9_sentinel

Filler paragraph ten before the page-boundary class. ind_page_boundary_filler_paragraph_10_sentinel

Filler paragraph eleven before the page-boundary class. ind_page_boundary_filler_paragraph_11_sentinel

Filler paragraph twelve before the page-boundary class. ind_page_boundary_filler_paragraph_12_sentinel

Filler paragraph thirteen before the page-boundary class. ind_page_boundary_filler_paragraph_13_sentinel

Filler paragraph fourteen before the page-boundary class. ind_page_boundary_filler_paragraph_14_sentinel

Filler paragraph fifteen before the page-boundary class. ind_page_boundary_filler_paragraph_15_sentinel

Filler paragraph sixteen before the page-boundary class. ind_page_boundary_filler_paragraph_16_sentinel

Filler paragraph seventeen before the page-boundary class. ind_page_boundary_filler_paragraph_17_sentinel

Filler paragraph eighteen before the page-boundary class. ind_page_boundary_filler_paragraph_18_sentinel

Filler paragraph nineteen before the page-boundary class. ind_page_boundary_filler_paragraph_19_sentinel

Filler paragraph twenty before the page-boundary class. ind_page_boundary_filler_paragraph_20_sentinel

.. py:class:: IndPageBoundaryClass

   Ind page boundary class body first line. ind_page_boundary_class_body_first_line_sentinel
   Repeated filler sentence number one inside the same body paragraph, to
   make this paragraph deliberately long. Repeated filler sentence number
   two inside the same body paragraph, to make this paragraph deliberately
   long. Repeated filler sentence number three inside the same body
   paragraph, to make this paragraph deliberately long. Repeated filler
   sentence number four inside the same body paragraph, to make this
   paragraph deliberately long. Repeated filler sentence number five inside
   the same body paragraph, to make this paragraph deliberately long.
   Repeated filler sentence number six inside the same body paragraph, to
   make this paragraph deliberately long. Repeated filler sentence number
   seven inside the same body paragraph, to make this paragraph
   deliberately long. Repeated filler sentence number eight inside the same
   body paragraph, to make this paragraph deliberately long. Repeated
   filler sentence number nine inside the same body paragraph, to make this
   paragraph deliberately long. Repeated filler sentence number ten inside
   the same body paragraph, to make this paragraph deliberately long.
   Repeated filler sentence number eleven inside the same body paragraph,
   to make this paragraph deliberately long. Repeated filler sentence
   number twelve inside the same body paragraph, to make this paragraph
   deliberately long. Repeated filler sentence number thirteen inside the
   same body paragraph, to make this paragraph deliberately long. Repeated
   filler sentence number fourteen inside the same body paragraph, to make
   this paragraph deliberately long. Repeated filler sentence number
   fifteen inside the same body paragraph, to make this paragraph
   deliberately long. Repeated filler sentence number sixteen inside the
   same body paragraph, to make this paragraph deliberately long. Repeated
   filler sentence number seventeen inside the same body paragraph, to make
   this paragraph deliberately long. Repeated filler sentence number
   eighteen inside the same body paragraph, to make this paragraph
   deliberately long. Repeated filler sentence number nineteen inside the
   same body paragraph, to make this paragraph deliberately long. Repeated
   filler sentence number twenty inside the same body paragraph, to make
   this paragraph deliberately long. Repeated filler sentence number
   twentyone inside the same body paragraph, to make this paragraph
   deliberately long. Repeated filler sentence number twentytwo inside the
   same body paragraph, to make this paragraph deliberately long. Repeated
   filler sentence number twentythree inside the same body paragraph, to
   make this paragraph deliberately long. Repeated filler sentence number
   twentyfour inside the same body paragraph, to make this paragraph
   deliberately long. Repeated filler sentence number twentyfive inside the
   same body paragraph, to make this paragraph deliberately long. Repeated
   filler sentence number twentysix inside the same body paragraph, to make
   this paragraph deliberately long. Repeated filler sentence number
   twentyseven inside the same body paragraph, to make this paragraph
   deliberately long. Repeated filler sentence number twentyeight inside
   the same body paragraph, to make this paragraph deliberately long.
   Repeated filler sentence number twentynine inside the same body
   paragraph, to make this paragraph deliberately long. Repeated filler
   sentence number thirty inside the same body paragraph, to make this
   paragraph deliberately long, so that -- under this fixture's default A4
   page geometry at an enlarged fontsize -- this ONE paragraph is
   guaranteed to span at least two compiled pages regardless of exactly
   where its signature happens to start.
   ind_page_boundary_class_body_continuation_sentinel

No-Desc, No-Field-List CONTROL (IND-04 Empty)
==================================================

.. CONTROL (IND-04 empty): a section containing only ordinary
   paragraphs -- no desc node and no field_list node anywhere -- so an
   assertion can prove that a document with neither construct emits no
   indent wrapper at all in this region.

This section contains only ordinary prose, with no desc node and no
field_list node anywhere. ind_no_desc_control_paragraph_sentinel

A second ordinary paragraph, to confirm two consecutive plain paragraphs
compile cleanly with no indent wrapper inserted between them.

Block Quote (D-04)
======================

.. D-04 CONTROL: a block quote with an attribution, deliberately NOT
   converted to the shared indent step -- block_quote keeps Typst's own
   quote() default (measured 11.0pt) instead of being forced onto the
   shared SHARED_INDENT_STEP (27.5pt). See 38-EMISSION-CONTRACT.md
   section 1.2; this is not to be re-opened at verify time.

Intro paragraph before the block quote (required: a docutils comment
immediately followed by more-indented content with no intervening
visible paragraph gets swallowed as comment continuation, silently
dropping the block quote -- discovered building this fixture).

    A block-quoted sentinel paragraph. ind_block_quote_sentinel

    -- Test Author
