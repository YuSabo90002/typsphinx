Rubric Strong Nesting Render Gate
===================================

.. CONTROL: the rubric below carries no inline markup at all, so it never
   touches the three shared _strong_was_* save slots (Phase 36 D-02) that
   the defect construct below clobbers. Placed BEFORE the defect construct
   deliberately -- D-13's corruption is document-wide (it never resets),
   so this construct's own paragraph-wrap assertion is only provably
   unaffected by the defect if it is measured before the defect fires. This
   isolates the defect to the nested-inline-child case: a fix that simply
   stops wrapping paragraphs after every rubric would break this construct
   too, and the assertion below would catch that.

.. rubric:: A Plain Rubric With No Markup

Delta prose sits after the markup free control rubric and must render inside a wrapped block.

Defect Rubric Section
-----------------------

.. D-13: the construct below is this phase's classic GATE-01 RED. A rubric
   whose title carries a real inline strong (bold) child clobbers the three
   shared _strong_was_* save slots (Phase 36 D-02) that visit_strong,
   visit_rubric and visit_desc_signature deliberately share, so
   depart_rubric's restore silently no-ops and in_list_item stays stuck True
   for the rest of the document. Every ordinary paragraph after this rubric,
   all the way to the end of the file, then loses its par() wrapper. This
   section heading exists only so the fixture's own compile-sanity leg
   reaches a valid PDF -- section boundaries are the one place the
   translator already emits an unconditional separator (depart_section),
   so the section housing the defect rubric is followed by sibling section
   headings rather than a heading landing directly under the untitled
   top-level body, which is the one juxtaposition the corrupted in_list_item
   state cannot itself route around.

.. rubric:: A Nested **Bold** Rubric

Alpha prose sits directly after the defect rubric and must render inside a wrapped block.

Intervening Heading One
------------------------

Bravo prose sits after an intervening section heading and must also render inside a wrapped block.

Intervening Heading Two
------------------------

Charlie prose sits deep in the document and must also render inside a wrapped block.
