Diagraph Escaping Render Gate
==============================

This fixture exists to be built with the ``typst`` builder and compiled by
``typst.compile()``. It is not meant to be read as prose.

The raw Typst block below carries a ``render()`` call whose DOT argument was
escaped with ``typsphinx.translator.escape_typst_string()``. The DOT exercises
every R013-hazardous character: a double quote inside a quoted label, a
literal backslash, a newline escape sequence, a hash (as a quoted colour
value), and Japanese text.

A ``.. graphviz::`` directive is deliberately NOT used here: ``visit_graphviz``
still emits a placeholder at this point in the slice, so a directive would
prove nothing about escaping. The raw passthrough puts the escaped literal
into the emitted ``.typ`` directly.

The ``render()`` call below deliberately carries NO leading ``#``.
``visit_raw`` drops raw-typst content verbatim into the document body, and
the body is wrapped in a Typst code block (``#{ ... }``), so the call site is
CODE mode, where a bare call is the correct expression-statement form.
A leading ``#`` there fails the compile with "the character ``#`` is not
valid in code" -- measured, not assumed. Do not "fix" it by adding one.

Every label the gate asserts on is an explicitly QUOTED label. Bare node
identifiers (``a`` .. ``e``) are rendered by diagraph through Typst math mode
and extract from the PDF as math glyphs, not ASCII -- do not assert on them.

The DOT must stay syntactically VALID: diagraph calls plugin.get_labels()
unguarded (internals.typ:217) BEFORE the guarded render at :436, so a DOT
*parse* error raises out of typst.compile() and would abort the whole module.

.. toctree::
   :maxdepth: 1

   included

.. raw:: typst

   render("digraph HostileEscaping {\n  a [label=\"quote \\\" x\"];\n  b [label=\"back\\\\slash\"];\n  c [label=\"line1\\nline2\"];\n  d [label=\"日本語\"];\n  e [label=\"redhash\", color=\"#ff0000\"];\n  a -> b -> c -> d -> e;\n}")
