Admonition Locale Title Gate (Japanese)
==========================================

This fixture exists to be compiled to ``.typ`` and string-scanned by
``tests/test_admonition_locale_title_precedence_gate.py`` (G-39-1),
SOURCE-tier only -- no PDF is compiled from this sub-project, and no CJK
glyph is ever extracted anywhere in that module. It carries the same three
directives as the sibling ``en/`` sub-project -- attention, danger and
error -- each with its own greppable body sentinel. Content is
deliberately ASCII-only even though ``conf.py`` sets ``language = "ja"``:
this gate asserts on the emitted title argument, never on rendered
Japanese glyphs, so the build must not depend on CJK font availability
(the ``tests/fixtures/typst_lang_gate/ja_default/conf.py`` precedent).

Attention Type
---------------

.. attention::

   LOCALEATTENTIONSENTINEL This is an attention admonition.

Danger Type
------------

.. danger::

   LOCALEDANGERSENTINEL This is a danger admonition.

Error Type
-----------

.. error::

   LOCALEERRORSENTINEL This is an error admonition.
