Admonition Locale Title Gate (English)
=========================================

This fixture exists to be compiled to ``.typ`` (source-tier assertions) and
to PDF (``pypdf`` text-extraction) by
``tests/test_admonition_locale_title_precedence_gate.py`` (G-39-1). It
carries exactly three directives -- attention, danger and error -- each
with its own greppable body sentinel. Content is deliberately ASCII-only:
this gate asserts on the emitted title argument and on English PDF text,
never on rendered Japanese glyphs, so the build must not depend on CJK
font availability (see the sibling ``ja/`` sub-project and the
``tests/fixtures/typst_lang_gate/ja_default/conf.py`` precedent).

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
