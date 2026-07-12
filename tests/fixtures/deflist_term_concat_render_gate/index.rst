Deflist Term Concat Render Gate
===============================

This fixture reproduces the corpus fatal where a definition-list term with
adjacent inline nodes emitted ``raw("make.bat")text(" and ")raw("Makefile")``
inside ``terms.item(...)`` -- juxtaposed code-mode expressions with no ``+``
separator, a Typst ``expected comma`` syntax error.

The term below mirrors the one that closes ``tutorial/getting-started.rst`` in
Sphinx's own ``doc/`` tree (a literal, then plain text, then another literal):

``make.bat`` and ``Makefile``
    On Windows the shortcut ``make.bat`` mirrors the ``Makefile`` targets used
    on Unix-like systems, so the two adjacent inline literals share a single
    definition body.

SingleTerm
    A term with a single inline text node, to prove no leading or trailing
    ``+`` is emitted for a one-expression term.
