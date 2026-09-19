Context A - Doctest Block In Paragraph Position
===============================================

Leading paragraph before the doctest block.

>>> ctx_a_paragraph = "naïve #1 \\ `x`"
>>> for part in ctx_a_paragraph.split():
...     print(part)
naïve
#1
\
`x`

Trailing paragraph after the doctest block.
