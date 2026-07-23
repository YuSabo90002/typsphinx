List Item Nested Block Render Gate
==================================

This fixture reproduces the corpus fatal where a list item that contains a
nested list directly followed by a sibling paragraph juxtaposed two code-mode
statements with no separator, a Typst "expected semicolon or line break" syntax
error.

The first item mirrors the construct that appears in changes/1.6 in Sphinx's
own doc tree: a paragraph, then a nested list, then another paragraph, all
inside one outer list item.

- Outer item introducing a nested list:

  - nested alpha
  - nested beta

  A paragraph AFTER the nested list, still inside the same outer item. This is
  the trailing block that must be newline-separated from the nested list
  rather than abutting its closing paren.

- The reverse sibling ordering, a paragraph THEN a nested list, to lock in that
  the fix is general and not specific to the list-then-paragraph shape:

  - reverse alpha
  - reverse beta

- A plain trailing item to keep the outer list well-formed.
