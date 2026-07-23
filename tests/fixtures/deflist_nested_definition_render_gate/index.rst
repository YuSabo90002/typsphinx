Nested Definition Body Clobber Render Gate
==========================================

PREDEF_SENTINEL this intro paragraph appears before any definition list and is
part of the real document body. Pre-fix it was silently dropped because a later
nested-in-definition list left ``self.body`` pointing at an orphaned buffer, so
``astext()`` joined the wrong buffer and discarded everything before it.

Outer definition with a nested definition list
----------------------------------------------

Configuration
    OUTERSENTINEL_CONFIG this leading paragraph of the outer definition comes
    before the nested definition list and must stay paired with its term.

    debug
        Enable debug output.

    verbose
        Increase logging verbosity.

API declaration whose content begins with a nested definition list
------------------------------------------------------------------

.. py:class:: WidgetGamma

   parameters
       OUTERSENTINEL_PARAMS the widget parameters are described in the nested
       definition list that follows this leading paragraph.

       alpha
           Description of the first parameter of the widget.

       beta
           Description of the second parameter of the widget.

Cross-reference emitted after the declaration, so pre-fix its ``link(...)``
survived in the buffer ``astext()`` joined while the declaration's anchor -- in
the discarded buffer -- did not: see :py:class:`WidgetGamma` for details.
