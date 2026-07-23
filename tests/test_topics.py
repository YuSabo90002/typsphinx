"""
Tests for topic node conversion to Typst (BLK-02).

Phase 13 Plan 01: covers D-02 (a `.. topic::` renders as a `clue` box via
the widened visit_title buffer-swap), D-05 (a `.. contents::` topic renders
box-less as a bold label above its bullet_list), D-06 (title heading-level
clamp to max(1, section_level)), and the Pitfall-1 fix (a title with more
than one direct child must not bare-juxtapose its child statements, in
either the heading() or the admonition/topic title: {...} form).

Mirrors tests/test_admonitions.py's construction idiom exactly: build a
docutils doctree fragment via `nodes`, run the translator via
`doc.walkabout(translator)`, and assert on `translator.astext()`.
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


class TestTopicConversion:
    """Test `.. topic::` node conversion to a clue box (D-02)."""

    def test_topic_converts_to_clue_box(self, temp_sphinx_app: SphinxTestApp):
        """A plain nodes.topic with a title+paragraph renders as a clue
        box, not a heading -- proves D-02's widened visit_title buffer-swap
        branch is entered for a `topic` parent (not just `Admonition`).
        """
        topic = nodes.topic()
        title = nodes.title(text="A Topic Title")
        para = nodes.paragraph(text="Topic body text.")
        topic += title
        topic += para

        doc = create_document()
        doc += topic

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "clue({" in output
        assert ", title: {" in output
        assert "heading(level:" not in output
        assert output.count("A Topic Title") == 1
        assert 'par({text("Topic body text.")})' in output

    def test_topic_title_with_multiple_children_does_not_concatenate(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """Pitfall-1 regression (topic/admonition title: {...} form): a
        topic title with a Text + emphasis child must not bare-juxtapose
        its child statements -- this is a currently-live real-compile
        fatal ("expected semicolon or line break") if unfixed.
        """
        topic = nodes.topic()
        title = nodes.title()
        title += nodes.Text("A Topic ")
        title += nodes.emphasis(text="Title")
        para = nodes.paragraph(text="Topic body text.")
        topic += title
        topic += para

        doc = create_document()
        doc += topic

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "clue({" in output
        assert ", title: {" in output
        assert "emph({" in output
        assert output.count("A Topic") == 1
        assert output.count("Title") == 1
        assert "heading(level:" not in output


class TestContentsTopicConversion:
    """Test `.. contents::` topic conversion (D-05: box-less pass-through)."""

    def test_contents_topic_renders_boxless_bold_label(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """A topic carrying the 'contents' class renders a bold
        strong({...}) label ABOVE its bullet_list, with NO clue box
        wrapper -- D-05. The bullet_list itself renders through the
        existing, unmodified list visitors (Sphinx already resolved the
        local TOC into a plain bullet_list of refid references).
        """
        topic = nodes.topic(classes=["contents", "local"])
        title = nodes.title(text="Table of Contents")
        topic += title

        bullet_list = nodes.bullet_list()
        list_item = nodes.list_item()
        item_para = nodes.paragraph()
        reference = nodes.reference(refid="section-a")
        reference += nodes.Text("Section A")
        item_para += reference
        list_item += item_para
        bullet_list += list_item
        topic += bullet_list

        doc = create_document()
        doc += topic

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "strong({" in output
        assert "clue({" not in output
        assert "heading(level:" not in output
        assert output.count("Table of Contents") == 1

        # D-05 body-insertion-order: the label must render BEFORE the list
        # content (an insert, not an append -- see 13-RESEARCH.md "Verified
        # Mechanism 3").
        label_index = output.index("Table of Contents")
        list_index = output.index("Section A")
        assert label_index < list_index


class TestTitleLevelClamp:
    """Test D-06: title heading-level clamp (max(1, section_level))."""

    def test_title_at_section_level_zero_clamps_to_one(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """A title whose parent is neither an Admonition nor a topic, at
        section_level == 0 (the translator's initial state -- e.g. a
        top-level titled non-section such as an out-of-scope sidebar),
        must clamp to heading(level: 1, ...) -- never
        heading(level: 0, ...), which Typst rejects (levels are >= 1).
        """
        title = nodes.title(text="Top Level Title")

        doc = create_document()
        doc += title

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        assert translator.section_level == 0
        doc.walkabout(translator)

        output = translator.astext()
        assert "heading(level: 1" in output
        assert "heading(level: 0" not in output

    def test_title_with_multiple_children_in_heading_form_does_not_concatenate(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """Pitfall-1 regression (plain heading() form): a section title
        with a Text + emphasis child must not bare-juxtapose its child
        statements -- the emph({...}) call must be a separate,
        newline-separated statement inside the {...}-wrapped heading
        content block.
        """
        section = nodes.section()
        title = nodes.title()
        title += nodes.Text("Mixed ")
        title += nodes.emphasis(text="Emphasis")
        para = nodes.paragraph(text="Section body.")
        section += title
        section += para

        doc = create_document()
        doc += section

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "emph({" in output
        assert output.count("Mixed") == 1
        assert output.count("Emphasis") == 1
        assert "heading(level: 1, {" in output
