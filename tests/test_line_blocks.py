"""
Tests for line/line_block node conversion to Typst (BLK-03).

Covers the visit_line_block/depart_line_block/visit_line/depart_line
branch logic: verbatim linebreak() breaks, per-depth h(...) nested
indentation, and the empty-line case. Mirrors the doctree-fragment
construction idiom in tests/test_admonitions.py.

The real-compile (typst.compile() + pypdf extraction) proof for BLK-03
lives in the Wave-3 combined render gate (13-03), not here -- these are
fast, string-assertion-level unit tests.
"""

from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter
from sphinx.testing.util import SphinxTestApp

from typsphinx.translator import TypstTranslator
from typsphinx.writer import TypstWriter


def create_document():
    """Helper function to create a minimal document with reporter."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


class TestLineBlockConversion:
    """Test line/line_block node conversion to Typst linebreak()/h()."""

    def test_flat_line_block_emits_linebreak_between_lines(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """A flat (non-nested) line_block wraps once in par({...}) and
        emits a real linebreak() after each line -- the two line texts
        must not be concatenated with no separator between them."""
        line_block = nodes.line_block()
        line_block += nodes.line(text="Line one")
        line_block += nodes.line(text="Line two")

        doc = create_document()
        doc += line_block

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()

        # Exactly one outer par({...}) wrapper.
        assert output.count("par({") == 1
        assert "})" in output

        # A real linebreak() call fires -- not merely a cosmetic '\n'.
        assert "linebreak()" in output
        assert output.count("linebreak()") == 2

        # The two line texts are not concatenated with zero separator.
        assert '"Line one"' in output
        assert '"Line two"' in output
        assert '"Line one""Line two"' not in output
        assert "Line oneLine two" not in output

        # Flat block: no nested indent spacer.
        assert "h(" not in output

    def test_nested_line_block_indents_only_nested_lines(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """The RESEARCH-verified nesting shape: top line_block -> line,
        nested line_block -> two lines, line back at top. Only the
        nested-depth lines get an h(...) indent spacer; the depth
        counter returns to 0 after departure (single outer par({...}),
        not nested par wrappers)."""
        outer = nodes.line_block()
        outer += nodes.line(text="Line one")

        nested = nodes.line_block()
        nested += nodes.line(text="Nested line indented")
        nested += nodes.line(text="Nested line two")
        outer += nested

        outer += nodes.line(text="Line three back at top")

        doc = create_document()
        doc += outer

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()

        # A single outer par({...}) wrapper -- not nested par wrappers.
        assert output.count("par({") == 1

        # Depth counter returned to 0 after departure.
        assert translator._line_block_depth == 0

        # Nested lines get an h(...) indent spacer.
        assert "h(1.5em)" in output
        assert output.count("h(1.5em)") == 2

        # All four lines' text and a real linebreak() per line are present.
        for text in (
            "Line one",
            "Nested line indented",
            "Nested line two",
            "Line three back at top",
        ):
            assert f'"{text}"' in output
        assert output.count("linebreak()") == 4

        # Top-level lines (before/after the nested block) are not indented:
        # confirm h(...) never precedes "Line one" or "Line three back at top".
        assert 'h(1.5em)text("Line one"' not in output
        assert 'h(1.5em)text("Line three back at top"' not in output

    def test_empty_line_emits_bare_linebreak(self, temp_sphinx_app: SphinxTestApp):
        """A nodes.line with no children (a blank '|' line in a line_block)
        emits a bare linebreak() -- no crash, no stray content."""
        line_block = nodes.line_block()
        line_block += nodes.line()  # empty line, no Text child

        doc = create_document()
        doc += line_block

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()

        assert "par({" in output
        assert "linebreak()" in output
        # No indent spacer at depth 0, no stray text content.
        assert "h(" not in output
        assert 'text("' not in output
