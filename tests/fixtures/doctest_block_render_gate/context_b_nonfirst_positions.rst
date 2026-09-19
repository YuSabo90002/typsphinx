Context B - Doctest Block At A Non-First Position
=================================================

Shape B1 - definition-list item
-------------------------------

Examples:
    Leading paragraph of the definition.

    >>> ctx_b1_definition = [1, 2]
    >>> sum(ctx_b1_definition)
    3

Shape B2 - bullet-list item
---------------------------

- Leading paragraph in the list item.

  >>> ctx_b2_bullet = {"k": 1}
  >>> ctx_b2_bullet["k"]
  1

  Trailing paragraph in the same list item.
