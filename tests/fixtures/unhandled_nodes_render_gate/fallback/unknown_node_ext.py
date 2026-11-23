"""Test-only Sphinx extension: node types with no Typst visitor.

Both node types below register only an HTML visitor, so the Typst translator
reaches ``unknown_visit`` for them:

- the ``:unk:`` role returns an inline ``unknown_inline`` node holding two
  inline children (a Text and a ``literal``);
- the ``.. unkblock:: <word>`` directive returns a body-level
  ``unknown_block`` node holding the same two inline children, so the
  children land directly in a code-mode statement context (document body,
  list item, table cell, definition) with no paragraph around them.
"""

from docutils import nodes
from docutils.parsers.rst import Directive


class unknown_inline(nodes.Inline, nodes.TextElement):  # noqa: N801
    """Inline node type deliberately left without a Typst visitor."""


class unknown_block(nodes.General, nodes.TextElement):  # noqa: N801
    """Body-level node type deliberately left without a Typst visitor."""


def _visit_html(self, node):
    pass


def _depart_html(self, node):
    pass


def _children(word):
    return [nodes.Text(f"{word}-alpha "), nodes.literal(f"{word}-beta", f"{word}-beta")]


def unk_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    node = unknown_inline(rawtext)
    node.extend(_children(text))
    return [node], []


class UnkBlockDirective(Directive):
    required_arguments = 1

    def run(self):
        node = unknown_block()
        node.extend(_children(self.arguments[0]))
        return [node]


def setup(app):
    app.add_node(unknown_inline, html=(_visit_html, _depart_html))
    app.add_node(unknown_block, html=(_visit_html, _depart_html))
    app.add_role("unk", unk_role)
    app.add_directive("unkblock", UnkBlockDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
