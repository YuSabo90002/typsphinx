Deflist Term In Listitem Render Gate
=====================================

This fixture reproduces FID-05 sub-case (a): a definition list nested inside
a bullet ``list_item``, mirroring the real corpus's ``usage/configuration.rst``
``texinfo_elements`` case (the ``'paragraphindent'`` / ``'exampleindent'``
entries). Pre-fix, the definition's first content is bare inline text (no
``par()`` wrapping, because ``visit_paragraph`` early-returns inside a list
item), so the term merges onto the same visual line as its definition. Fixed
by adding a named separator argument to the emitted ``terms`` call.

- ``'paragraphindent'``
      Number of spaces to indent the first line of each paragraph,
      default 2.

  ``'exampleindent'``
      Number of spaces to indent the example, default 5.
