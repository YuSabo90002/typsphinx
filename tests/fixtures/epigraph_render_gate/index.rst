Epigraph Attribution Render Gate
================================

The attribution of a ``.. epigraph::`` (a docutils block quote carrying the
``epigraph`` class) holds INLINE children directly -- emphasis, an inline
literal, plain text -- and must render as EVALUATED content, never literal
Typst source. The author line below carries an emphasis, an inline literal
whose lone underscore would open a stray unclosed emphasis span were it leaked
into markup mode, and a plain sentinel token.

Epigraph with an attribution
----------------------------

.. epigraph::

   Any sufficiently advanced ``_t`` template is indistinguishable from magic.
   EPIGRAPHBODYSENTINEL.

   -- *Ada* ``_lovelace`` EPIGRAPHAUTHORSENTINEL

Epigraph without an attribution
-------------------------------

.. epigraph::

   A standalone epigraph with an inline literal ``_t`` and no attribution
   line at all. EPIGRAPHNOATTRSENTINEL.
