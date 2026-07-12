Deflist Multiblock Definition Render Gate
=========================================

This fixture reproduces the corpus fatal where a definition-list DEFINITION
holding several block-level children (a paragraph, then a code block, then a
bullet list) was passed UNWRAPPED as ``terms.item``'s second argument. Typst
read the first statement as the whole argument and then expected a comma at the
next statement, aborting the compile with "expected comma".

The first term mirrors the construct in usage/restructuredtext/directives in
Sphinx's own doc tree: one term whose definition has a paragraph, a code block,
and a bullet list, all under a single term.

multi-block term
    A paragraph explaining the term, the first block-level child of this
    definition.

    .. code-block:: python

        def build():
            return "typst"

    - a bullet after the code block
    - another bullet, so the definition has three distinct block children

single-block term
    A plain single-paragraph definition, the regression guard proving the
    wrap does not disturb the common one-block case.
