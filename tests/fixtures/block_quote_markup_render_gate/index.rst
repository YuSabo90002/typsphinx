Block Quote Markup-Mode Render Gate
===================================

Every block quote below carries an inline literal ``_t`` whose lone
underscore, were the quote body emitted in Typst markup mode, would open a
stray inline-emphasis span that never closes and abort the whole compile with
an unclosed-delimiter error. A code-mode block-quote body renders the inline
literal as a real value, so the underscore is inert.

Plain block quote
-----------------

Intro paragraph before the plain block quote.

    This quoted paragraph carries an inline literal ``_t`` template suffix
    and renders as a block quote. BLOCKQUOTEPLAINSENTINEL.

Block quote nested inside a list item
-------------------------------------

The over-indented sub-block below is wrapped by docutils in a block quote
inside the list item, following the list-item lead-in inline content (bug
#11's list-item separator must keep them apart).

* ``sphinx.util`` helpers BLOCKQUOTELISTSENTINEL:

      An over-indented sub-block quote inside the list item, again carrying a
      ``_t`` literal so a stray span would fatally abort compilation in markup
      mode.

Block quote with an attribution
-------------------------------

    To be or not to be, that is the ``_t`` question. BLOCKQUOTEATTRSENTINEL.

    -- William Shakespeare
