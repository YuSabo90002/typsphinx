Rubric Indent Invariance Gate
================================

This fixture exists solely to be built through ``-b typstpdf`` and measured
by ``tests/test_rubric_indent_invariance.py`` (Phase 39, ADM-05, D-12). It
is not meant to be read as prose. Every marker below is a single uppercase
run, unique in the repository, and is the FIRST text on its line in the
rendered output -- load-bearing for the column assertions. Changing a
marker here requires changing the test module in the same commit.

This module backs an INVARIANCE GUARD (D-12), not a GATE-01 RED: the
property it measures already holds against pre-phase code (Phase 38's
``pad(left: SHARED_INDENT_STEP, {...})`` wrapper around ``desc_content``
already carries the rubric structurally), so the guard is expected GREEN
in both directions and exists only to catch a future regression.

.. Top-level reference paragraph -- the page-margin column every other
   marker below is compared against. No absolute column is ever asserted,
   only relative comparisons against this one and against each other.

RIITOPREF sits at the ordinary top-level page margin, with no containing
description body.

.. A py:class:: whose body opens with an ordinary paragraph, then a rubric
   -- the autodoc-"Options"-shaped heading ADM-05 names, hand-authored per
   39-RESEARCH.md Open Question 2 rather than wired through real autodoc
   extraction (the docutils node shape is identical either way).

.. py:class:: RiiOuterClass

   RIICLASSBODY is the class body's own first paragraph.

   .. rubric:: RIICLASSRUBRIC

   .. Nested inside the same class body: a py:method:: whose own body
      opens with an ordinary paragraph, then its own rubric -- the second
      nesting level, making the strictly-deeper comparison possible.

   .. py:method:: rii_outer_class_inner_method(value)

      RIIMETHODBODY is the method body's own first paragraph.

      .. rubric:: RIIMETHODRUBRIC

.. After the class closes: an ordinary top-level paragraph, then a
   top-level rubric outside any description body -- the CONTROL proving a
   rubric gets no indent rule of its own. A naive implementation that gave
   the rubric a private indent would fail this pair.

RIITOPSECOND precedes the top-level control rubric, outside any
description body.

.. rubric:: RIICTRLRUBRIC
