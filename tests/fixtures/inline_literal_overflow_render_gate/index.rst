Inline Literal Overflow Render Gate
=====================================

This fixture exists solely to be compiled to PDF by
``tests/test_inline_literal_overflow_render_gate.py`` -- a regression gate
for a margin-overflow defect that existing string-agreement tests never
caught because they never real-compiled the emitted output. It is not meant
to be read as prose.

Long run of colon-leading inline literal tokens
--------------------------------------------------

A long run of double-backtick literal-role tokens, each starting with a
colon, must wrap at the space between tokens instead of overflowing the
page's right margin and clipping mid-token. This mirrors the audit's
``usage/domains/cpp`` p.85 repro (a run of C++ domain role names rendered as
literal text).

See also ``:cpp:any:`` ``:cpp:class:`` ``:cpp:enumerator:`` ``:cpp:expr:``
``:cpp:func:`` ``:cpp:member:`` ``:cpp:texpr:`` ``:cpp:type:`` ``:cpp:union:``
``:cpp:var:`` for the complete set of C++ domain cross-reference roles.
