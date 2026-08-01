Desc Break Marker Buffer Swap Gate
=====================================

This fixture exists solely to be built through ``-b typst`` by
``tests/test_desc_break_marker_buffer_swap_gate.py`` (the folded todo
``.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md``,
folded into Phase 38 by D-10). It is not meant to be read as prose.

Desc Inside A Glossary Definition
=====================================

.. Construct 1: a single, non-nested desc directive whose entire
   visit_desc/depart_desc pair lives inside a glossary term's definition
   body. Entering the definition (visit_definition) swaps self.body to
   current_definition_buffer via _saved_body_stack; both this desc's
   visit_desc and depart_desc run while self.body points at that swapped
   buffer.

.. glossary::

   buffer-swap-term-one
       Definition body containing a single desc directive.

       .. py:function:: desc_break_glossary_function_one()

          Glossary function one body.

Nested Desc Inside A Glossary Definition
============================================

.. Construct 2: a nested desc pair (py:class:: containing py:method::)
   whose ENTIRE pair -- both depart_desc calls the SIG-08 marker compares
   -- lives inside a glossary term's definition body, exercising the
   buffer swap AND the nesting boundary at once. This is the concretely
   reachable shape the folded todo names: an object description
   directive nested inside a glossary definition.

.. glossary::

   buffer-swap-term-two
       Definition body containing a nested desc pair.

       .. py:class:: DescBreakGlossaryOuterClass

          Glossary outer class body.

          .. py:method:: desc_break_glossary_inner_method()

             Glossary inner method body.

Nested Desc At Top Level -- Nesting-Only Control
=======================================================

.. CONTROL: the identical nested-desc shape (py:class:: containing
   py:method::) at document top level, outside any definition -- no
   self.body reassignment occurs anywhere in this construct's
   processing. Distinguishes "the buffer swap broke it" from "nesting
   broke it": if this control's break count ever diverges from
   construct 2's, the buffer swap -- not the nesting -- is the variable
   responsible.

.. py:class:: DescBreakTopLevelOuterClass

   Top-level outer class body.

   .. py:method:: desc_break_toplevel_inner_method()

      Top-level inner method body.

Desc Inside A Figure Caption Or Admonition Title -- Not Reachable
========================================================================

.. CONTROL (not constructible -- recorded per this plan's own
   instruction rather than silently omitted): the other two unguarded
   self.body reassignment sites are visit_title's admonition/topic-title
   buffer swap (_saved_body_for_admonition_title,
   typsphinx/translator.py:591) and visit_caption's figure-caption
   buffer swap (_saved_body_for_figure_caption,
   typsphinx/translator.py:2383). Both nodes.title and nodes.caption are
   parsed by docutils as ONE LINE of INLINE content -- a block-level
   domain directive such as py:function:: cannot occur inside a title's
   or a caption's argument text at all, at the RST grammar level, not as
   a rendering choice. Neither site therefore has a reachable
   desc-nesting case; this fourth control is recorded as structurally
   inapplicable rather than silently omitted.

Sentinel paragraph so this section is not empty.
