"""
Tests for topic node conversion to Typst (BLK-02).

Phase 13 Plan 01: covers D-02 (a `.. topic::` renders as a `clue` box via
the widened visit_title buffer-swap), D-05 (a `.. contents::` topic renders
box-less as a bold label above its bullet_list), TOC-01 (title
heading-level clamp to max(1, section_level), surviving the level->depth
switch because Typst's relative depth argument is constrained the same way
its absolute level argument was -- values must be >= 1), and the Pitfall-1
fix (a title with more than one direct child must not bare-juxtapose its
child statements, in either the heading() or the admonition/topic
title: {...} form).

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


def _section_title_output(app: SphinxTestApp) -> str:
    """Positive control for this module's negative heading guards.

    Builds a bare nodes.section containing a nodes.title with a
    distinctive text sentinel, runs it through a fresh translator, and
    returns the emitted output. This proves the heading(depth: ...)
    literal the negative guards search for IS producible by the SAME
    translator, in the SAME session, on a DIFFERENT path (the generic
    section-heading path, not the topic/contents buffer-swap early
    return) -- so a guard's absence on the buffer-swap path carries
    information rather than being vacuously true (44.1-GATE-EVIDENCE-02.md
    Section 3, "positive control" proof shape). Unit-level only: no
    sphinx-build, no compile (D-05).
    """
    section = nodes.section()
    title = nodes.title(text="Positive Control Section Title")
    section += title

    doc = create_document()
    doc += section

    writer = TypstWriter(app.builder)
    writer.document = doc
    translator = TypstTranslator(doc, app.builder)
    doc.walkabout(translator)

    return translator.astext()


class TestTopicConversion:
    """Test `.. topic::` node conversion to an abstract box (D-02/D-10)."""

    def test_topic_converts_to_clue_box(self, temp_sphinx_app: SphinxTestApp):
        """A plain nodes.topic with a title+paragraph renders as an
        abstract box (D-10), not a heading -- proves D-02's widened
        visit_title buffer-swap branch is entered for a `topic` parent
        (not just `Admonition`).
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
        assert "abstract({" in output
        assert ", title: {" in output
        assert "heading(depth:" not in output
        assert output.count("A Topic Title") == 1
        assert 'par({text("Topic body text.")})' in output

        # Positive control (44.1-GATE-EVIDENCE-02.md Section 3): a pre-fix
        # revert of typsphinx/translator.py cannot make the guard above
        # fail, because a topic title never reaches the generic
        # section-heading path on either side of the level->depth
        # rewrite. Prove the searched literal IS producible by the same
        # translator on a DIFFERENT path, so its absence here carries
        # information.
        control_output = _section_title_output(temp_sphinx_app)
        assert "heading(depth:" in control_output

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
        assert "abstract({" in output
        assert ", title: {" in output
        assert "emph({" in output
        assert output.count("A Topic") == 1
        assert output.count("Title") == 1
        assert "heading(depth:" not in output

        # Positive control (44.1-GATE-EVIDENCE-02.md Section 3) -- see
        # test_topic_converts_to_clue_box for the full rationale.
        control_output = _section_title_output(temp_sphinx_app)
        assert "heading(depth:" in control_output


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
        # Reviewed 39-05 (D-10): this box-less `.. contents::` path is
        # unaffected by the abstract-function reroute -- it emits no clue
        # box at all (of any function name), so this assertion stays as
        # "clue({" not in output rather than being widened to also check
        # "abstract({". Left deliberately unchanged.
        assert "clue({" not in output
        assert "heading(depth:" not in output

        # Positive control (44.1-GATE-EVIDENCE-02.md Section 3) -- see
        # test_topic_converts_to_clue_box for the full rationale.
        control_output = _section_title_output(temp_sphinx_app)
        assert "heading(depth:" in control_output

        assert output.count("Table of Contents") == 1

        # D-05 body-insertion-order: the label must render BEFORE the list
        # content (an insert, not an append -- see 13-RESEARCH.md "Verified
        # Mechanism 3").
        label_index = output.index("Table of Contents")
        list_index = output.index("Section A")
        assert label_index < list_index


class TestTitleLevelClamp:
    """Test TOC-01: title heading-level clamp (max(1, section_level))."""

    def test_title_at_section_level_zero_clamps_to_one(
        self, temp_sphinx_app: SphinxTestApp
    ):
        """A title whose parent is neither an Admonition nor a topic, at
        section_level == 0 (the translator's initial state -- e.g. a
        top-level titled non-section such as an out-of-scope sidebar),
        must clamp to a depth of 1 -- never pass a rejected depth
        argument of 0. TOC-01: Typst's relative depth argument is
        constrained the same way its absolute level argument was
        (values must be >= 1), so this clamp's mechanism survives the
        level->depth switch unchanged; only the argument it clamps is
        relative now, not an absolute final level (mirrors the source
        rationale at typsphinx/translator.py, visit_title).

        The two assertions below are a matched pair read off ONE output:
        the positive shows the floor value IS produced, the negative
        shows the sub-floor value is NOT. The negative half has no
        independent positive control -- the sub-floor literal is
        unproducible by construction (44.1-GATE-EVIDENCE-02.md Section
        3) -- so its non-vacuity rests on the positive half plus the
        clamp-arithmetic assertion below.
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
        assert "heading(depth: 1" in output
        assert "heading(depth: 0" not in output

        # Adjacency edge: bind the emitted numeral to the clamp
        # expression itself, computed independently here from the
        # translator's own recorded section_level (asserted == 0 above),
        # so this assertion goes red if a future change alters the
        # clamp's arithmetic without altering its literal.
        assert f"heading(depth: {max(1, translator.section_level)}" in output

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
        assert "heading(depth: 1, {" in output
