"""
Tests for admonition node conversion to Typst gentle-clues.

Task 3.4: アドモニション（Admonition）の変換
"""

from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter
from sphinx import addnodes
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


class TestAdmonitionConversion:
    """Test admonition node conversion using gentle-clues package."""

    def test_note_converts_to_info(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.note converts to info[]."""
        # Create a note admonition
        note = nodes.note()
        para = nodes.paragraph(text="This is a note.")
        note += para

        # Create document
        doc = create_document()
        doc += note

        # Translate
        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "info({" in output
        assert "info[" not in output
        assert 'par({text("This is a note.")})' in output

    def test_warning_converts_to_warning(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.warning converts to warning[]."""
        warning = nodes.warning()
        para = nodes.paragraph(text="This is a warning.")
        warning += para

        doc = create_document()
        doc += warning

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "warning({" in output
        assert "warning[" not in output
        assert 'par({text("This is a warning.")})' in output

    def test_tip_converts_to_tip(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.tip converts to tip[]."""
        tip = nodes.tip()
        para = nodes.paragraph(text="Here's a tip.")
        tip += para

        doc = create_document()
        doc += tip

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "tip({" in output
        assert "tip[" not in output
        assert 'par({text("Here\'s a tip.")})' in output

    def test_important_converts_to_warning_with_title(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """Test that nodes.important converts to warning(title: "Important")[]."""
        important = nodes.important()
        para = nodes.paragraph(text="This is important.")
        important += para

        doc = create_document()
        doc += important

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "warning({" in output
        assert "warning[" not in output
        assert ', title: "Important"' in output
        assert 'par({text("This is important.")})' in output

    def test_caution_converts_to_warning(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.caution converts to warning[]."""
        caution = nodes.caution()
        para = nodes.paragraph(text="Be cautious.")
        caution += para

        doc = create_document()
        doc += caution

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "warning({" in output
        assert "warning[" not in output
        assert 'par({text("Be cautious.")})' in output

    def test_seealso_converts_to_info_with_title(self, temp_sphinx_app: SphinxTestApp):
        """Test that addnodes.seealso converts to info(title: "See Also")[]."""
        seealso = addnodes.seealso()
        para = nodes.paragraph(text="See related documentation.")
        seealso += para

        doc = create_document()
        doc += seealso

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "info({" in output
        assert "info[" not in output
        assert ', title: "See Also"' in output
        assert 'par({text("See related documentation.")})' in output

    def test_admonition_with_multiple_paragraphs(self, temp_sphinx_app: SphinxTestApp):
        """Test admonition with multiple paragraphs."""
        note = nodes.note()
        para1 = nodes.paragraph(text="First paragraph.")
        para2 = nodes.paragraph(text="Second paragraph.")
        note += para1
        note += para2

        doc = create_document()
        doc += note

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "info({" in output
        assert "info[" not in output
        assert 'par({text("First paragraph.")})' in output
        assert 'par({text("Second paragraph.")})' in output

    def test_nested_admonitions(self, temp_sphinx_app: SphinxTestApp):
        """Test nested admonitions."""
        outer_note = nodes.note()
        para1 = nodes.paragraph(text="Outer note.")
        inner_warning = nodes.warning()
        para2 = nodes.paragraph(text="Inner warning.")
        inner_warning += para2
        outer_note += para1
        outer_note += inner_warning

        doc = create_document()
        doc += outer_note

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "info({" in output
        assert "info[" not in output
        assert 'par({text("Outer note.")})' in output
        assert "warning({" in output
        assert "warning[" not in output
        assert 'par({text("Inner warning.")})' in output

    def test_admonition_with_title_in_content(self, temp_sphinx_app: SphinxTestApp):
        """Test admonition with custom title in first paragraph."""
        # In Sphinx, custom admonitions have the title as the first child
        note = nodes.note()
        title = nodes.title(text="Custom Title")
        para = nodes.paragraph(text="Content here.")
        note += title
        note += para

        doc = create_document()
        doc += note

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        # Should use the dynamic (node-derived) title buffered as a code
        # block, emitted exactly once, with the body evaluating in code mode.
        assert "info({" in output
        assert "info[" not in output
        assert ", title: {" in output
        assert output.count("Custom Title") == 1
        assert "heading(" not in output  # double-emission bug fixed
        assert 'par({text("Content here.")})' in output
