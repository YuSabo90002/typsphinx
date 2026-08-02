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

    def test_seealso_converts_to_tip_with_title(self, temp_sphinx_app: SphinxTestApp):
        """Test that addnodes.seealso converts to tip(title: "See also")[] (D-02).

        seealso joins the success bucket (the same `tip` function hint/tip
        already pass), and its title now comes from the
        sphinx.locale.admonitionlabels catalog, whose casing ("See also")
        differs from the old hardcoded literal ("See Also").
        """
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
        assert "tip({" in output
        assert "tip[" not in output
        assert ', title: "See also"' in output
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

    def test_nested_list_in_note(self, temp_sphinx_app: SphinxTestApp):
        """Test a bullet list nested inside a note (D-05)."""
        note = nodes.note()
        bullet_list = nodes.bullet_list()
        item1 = nodes.list_item()
        item1 += nodes.paragraph(text="Item one.")
        item2 = nodes.list_item()
        item2 += nodes.paragraph(text="Item two.")
        bullet_list += item1
        bullet_list += item2
        note += bullet_list

        doc = create_document()
        doc += note

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        # The note stays in code-mode content-block form and the nested
        # list's code-mode form evaluates inside it (no literal-source leak).
        assert "info({" in output
        assert "info[" not in output
        assert "list(" in output
        assert 'text("Item one.")' in output
        assert 'text("Item two.")' in output

    def test_nested_code_block_in_note(self, temp_sphinx_app: SphinxTestApp):
        """Test a literal/code block nested inside a note (D-05)."""
        note = nodes.note()
        literal_block = nodes.literal_block(text="x = 1")
        note += literal_block

        doc = create_document()
        doc += note

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "info({" in output
        assert "info[" not in output
        assert "```" in output
        assert "x = 1" in output

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

    def test_admonition_title_preserves_inline_markup(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """Test that an admonition title preserves inline markup (D-02).

        The title's rendered content is captured via the buffer-swap idiom
        (routing through the normal inline visitors) rather than flattened
        with node.astext(), so an emphasis child inside the title survives
        as an emph(...) code-mode call instead of being reduced to plain
        text. This also locks down the title double-emission regression
        found in RESEARCH.md: heading( must never appear in the output.

        Note: nodes.note() does not carry a title in real rST usage; this
        is a constructed shape used purely to exercise the admonition-aware
        visit_title/depart_title branch. The real docutils shape for a
        title-bearing admonition is nodes.admonition (generic `.. admonition::`),
        covered by Plan 03's D-06 generic-admonition test.
        """
        note = nodes.note()
        title = nodes.title()
        title += nodes.Text("Custom ")
        title += nodes.emphasis(text="Title")
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
        assert "info({" in output
        assert "info[" not in output
        assert ", title: {" in output
        assert "emph({" in output
        assert output.count("Custom") == 1
        assert output.count("Title") == 1
        assert "heading(" not in output  # double-emission bug fixed

    def test_hint_converts_to_tip(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.hint converts to tip[] (D-06).

        gentle-clues 1.3.1 has no dedicated `hint` clue; `tip` is the
        verified closest analog.
        """
        hint = nodes.hint()
        para = nodes.paragraph(text="Here's a hint.")
        hint += para

        doc = create_document()
        doc += hint

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "tip({" in output
        assert "tip[" not in output
        assert 'par({text("Here\'s a hint.")})' in output

    def test_error_converts_to_error(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.error converts to error[] (D-06)."""
        error = nodes.error()
        para = nodes.paragraph(text="This is an error.")
        error += para

        doc = create_document()
        doc += error

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "error({" in output
        assert "error[" not in output
        assert 'par({text("This is an error.")})' in output

    def test_danger_converts_to_error(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.danger converts to error[] (D-03).

        danger folds into the single error-bucket function -- the same
        one visit_error passes -- making the red bucket one function.
        """
        danger = nodes.danger()
        para = nodes.paragraph(text="This is dangerous.")
        danger += para

        doc = create_document()
        doc += danger

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "error({" in output
        assert "error[" not in output
        assert 'par({text("This is dangerous.")})' in output

    def test_attention_converts_to_error(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.attention converts to error[] (D-03).

        attention joins the error bucket -- the same function visit_error
        passes -- not the warning bucket.
        """
        attention = nodes.attention()
        para = nodes.paragraph(text="Pay attention.")
        attention += para

        doc = create_document()
        doc += attention

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "error({" in output
        assert "error[" not in output
        assert 'par({text("Pay attention.")})' in output

    def test_generic_admonition_converts_to_notify(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """Test that a generic nodes.admonition converts to notify[] (D-09).

        Uses the real docutils shape produced by `.. admonition:: <title>` —
        a `nodes.admonition` with a real `nodes.title` child — rather than
        an injected title on an unrelated admonition type. The title flows
        through the same buffer-swap `visit_title`/`depart_title` path used
        by all other admonition types. `nodes.admonition`'s class name
        ("admonition") is not a sphinx.locale.admonitionlabels catalog key,
        so no static title is injected here.
        """
        admonition = nodes.admonition()
        title = nodes.title(text="My Note")
        para = nodes.paragraph(text="Generic admonition body.")
        admonition += title
        admonition += para

        doc = create_document()
        doc += admonition

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "notify({" in output
        assert "notify[" not in output
        assert ", title: {" in output
        assert output.count("My Note") == 1
        assert "heading(" not in output
        assert 'par({text("Generic admonition body.")})' in output

    def test_note_with_own_title_wins_over_catalog(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """A directive-supplied title wins over the sphinx.locale.
        admonitionlabels catalog value (D-04/D-05 precedence, T-39-12).

        Uses nodes.note -- a real catalog key whose English catalog value
        is "Note" -- carrying its own title child, proving the dynamic
        (node-derived) title path in _depart_admonition still takes
        priority over the static catalog lookup Task 2 introduced, and
        that the catalog value never leaks through when a title child is
        present.
        """
        note = nodes.note()
        title = nodes.title(text="Custom Note Title")
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
        assert "info({" in output
        assert ", title: {" in output
        assert output.count("Custom Note Title") == 1
        assert '"Note"' not in output  # the catalog value must not leak through
