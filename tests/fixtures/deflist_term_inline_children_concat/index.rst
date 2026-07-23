Deflist Term Inline-Children Concat Gate
========================================

This fixture reproduces the corpus fatal where a definition-list term whose
DIRECT inline children mix element types (a literal, a strong, an emphasis, a
reference and plain text, adjacent to one another) emitted juxtaposed code-mode
expressions with no ``+`` separator -- and leaked a stray ``+`` inside an
element's own content block -- inside ``terms.item(...)``, a Typst
``expected comma`` syntax error.

The headline term below mixes every inline child type on a single line so each
sibling boundary (literal->text->strong->text->emphasis->text->reference->text)
must be ``+`` separated, and no ``+`` may leak inside ``strong({...})`` /
``emph({...})`` / ``link(...)``:

``code`` **bold** *italic* `link <https://example.com/x>`_ tail
    Mixed inline children: a literal, a strong, an emphasis, a reference and
    trailing text, all adjacent direct children of the term.

SingleTerm
    A term with a single inline text node, to prove no leading or trailing
    ``+`` is emitted for a one-expression term.

prefix **bold**
    Plain text then a strong -- ``text("prefix ") + strong({...})``.

**bold** suffix
    A strong then plain text -- ``strong({...}) + text(" suffix")``.

`link <https://example.com/y>`_ suffix
    A reference then plain text -- ``link(...) + text(" suffix")``.

*italic* ``code``
    An emphasis then a literal -- ``emph({...}) + raw("code")``.
