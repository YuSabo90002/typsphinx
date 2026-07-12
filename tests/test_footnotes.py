"""
Tests for footnote/footnote_reference node conversion to Typst (FN-01).

Phase 14 Plan 01: covers D-01 (visit_document pre-pass index build), D-05
(visit_footnote SkipNode suppression at the definition's natural location),
D-02/D-03/D-06 (first-reference definition-form emission via buffer-swap,
skipping the leading label child), D-03 (repeat-reference bare reuse form),
and D-08 (dangling refid warn+skip guard).

Mirrors tests/test_topics.py's construction idiom exactly: build a docutils
doctree fragment via `nodes`, run the translator via `doc.walkabout(translator)`,
and assert on `translator.astext()` (and on translator state directly for the
index test).
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


def _make_translator(doc: nodes.document, temp_sphinx_app: SphinxTestApp):
    """Helper to construct a writer + translator pair for a document."""
    writer = TypstWriter(temp_sphinx_app.builder)
    writer.document = doc
    return TypstTranslator(doc, temp_sphinx_app.builder)


def test_footnote_index_built(temp_sphinx_app: SphinxTestApp):
    """D-01: visit_document builds self._footnote_index (id -> footnote
    node) and initializes self._emitted_footnote_ids as an empty set,
    BEFORE any body content is visited.
    """
    footnote = nodes.footnote(ids=["f1"])
    label = nodes.label(text="1")
    para = nodes.paragraph(text="Unreferenced footnote body.")
    footnote += label
    footnote += para

    doc = create_document()
    doc += footnote

    translator = _make_translator(doc, temp_sphinx_app)
    doc.walkabout(translator)

    assert translator._footnote_index == {"f1": footnote}
    assert translator._emitted_footnote_ids == set()


def test_visit_footnote_skips_definition(temp_sphinx_app: SphinxTestApp):
    """D-05/D-09: a footnote definition with no referencing
    footnote_reference emits nothing at its natural (docutils) location --
    the body marker text must not appear anywhere in the output (silently
    dropped, per D-09).
    """
    footnote = nodes.footnote(ids=["f1"])
    label = nodes.label(text="1")
    para = nodes.paragraph(text="UNREFERENCEDBODYMARKER")
    footnote += label
    footnote += para

    doc = create_document()
    doc += footnote

    translator = _make_translator(doc, temp_sphinx_app)
    doc.walkabout(translator)

    output = translator.astext()
    assert "UNREFERENCEDBODYMARKER" not in output


def test_first_reference_definition_form(temp_sphinx_app: SphinxTestApp):
    """D-02/D-03/D-06: the FIRST footnote_reference to an id emits the
    bracket-wrapped definition form `[#footnote({body}) <fn-id>]`, sourcing
    the body via buffer-swap (skipping the footnote's leading label child),
    and never renders the footnote_reference's own docutils marker-digit
    child as standalone prose.
    """
    para = nodes.paragraph()
    footnote_ref = nodes.footnote_reference(refid="f1")
    footnote_ref += nodes.Text("2")
    para += footnote_ref

    footnote = nodes.footnote(ids=["f1"])
    label = nodes.label(text="2")
    body_para = nodes.paragraph(text="DEFINITIONBODYMARKER")
    footnote += label
    footnote += body_para

    doc = create_document()
    doc += para
    doc += footnote

    translator = _make_translator(doc, temp_sphinx_app)
    doc.walkabout(translator)

    output = translator.astext()
    assert "footnote({" in output
    assert "<fn-f1>" in output
    assert "DEFINITIONBODYMARKER" in output
    # The footnote_reference's own docutils marker-digit child ("2") must
    # never render as standalone prose -- it should not appear wrapped as
    # its own text() call outside of the definition body/label plumbing.
    assert 'text("2")' not in output


def test_repeat_reference_reuse_form(temp_sphinx_app: SphinxTestApp):
    """D-03: a REPEAT footnote_reference to an already-emitted id emits the
    bare reuse form `footnote(<fn-id>)` with no bracket-wrap and no
    re-rendered body -- the definition form fires exactly once per id.
    """
    para = nodes.paragraph()
    ref1 = nodes.footnote_reference(refid="f1")
    ref1 += nodes.Text("1")
    ref2 = nodes.footnote_reference(refid="f1")
    ref2 += nodes.Text("1")
    para += ref1
    para += ref2

    footnote = nodes.footnote(ids=["f1"])
    label = nodes.label(text="1")
    body_para = nodes.paragraph(text="REPEATBODYMARKER")
    footnote += label
    footnote += body_para

    doc = create_document()
    doc += para
    doc += footnote

    translator = _make_translator(doc, temp_sphinx_app)
    doc.walkabout(translator)

    output = translator.astext()
    assert output.count("footnote({") == 1
    assert "footnote(<fn-f1>)" in output
    assert output.count("REPEATBODYMARKER") == 1


def test_dangling_reference_warns(
    temp_sphinx_app: SphinxTestApp, caplog
):
    """D-08: a dangling footnote_reference (refid absent from the index)
    logs a logger.warning naming the refid and skips, emitting no
    footnote(...) call at all.
    """
    para = nodes.paragraph()
    footnote_ref = nodes.footnote_reference(refid="missing")
    footnote_ref += nodes.Text("1")
    para += footnote_ref

    doc = create_document()
    doc += para

    translator = _make_translator(doc, temp_sphinx_app)

    with caplog.at_level("WARNING"):
        doc.walkabout(translator)

    output = translator.astext()
    assert "footnote(" not in output
    assert any("missing" in record.getMessage() for record in caplog.records)
