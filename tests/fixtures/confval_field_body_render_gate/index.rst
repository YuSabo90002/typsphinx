Confval Field Body Render Gate
==============================

This fixture reproduces the corpus fatal where a ``confval`` field body written
inline on its field line is collapsed by docutils to inline children directly
under ``field_body`` (no wrapping paragraph). Those adjacent inline expressions
juxtaposed in the code-mode content block, aborting the compile with "expected
semicolon or line break".

.. confval:: html_title

   The confval directive itself; its ``:type:`` and ``:default:`` field bodies
   below are collapsed to inline children.

.. confval:: html_sidebars
   :type: ``dict`` or **mapping**
   :default: The value of **html_title** with a ``fallback``

   A description paragraph so the confval also exercises the block field-body
   and normal-paragraph path, which must stay wrapped in ``par({...})``.

Definition list nested in a list item
-------------------------------------

The second construct mirrors ``usage/configuration.rst:3546``: a bullet-list
item whose paragraph is directly followed by a definition list. The def-list
must newline-separate from the preceding paragraph inside the list item.

* Keys that you may want to override include:

  paragraphindent
      Number of spaces to indent the first line of each paragraph.

  exampleindent
      Number of spaces to indent examples.
