"""
Regression gate for the def-list-term INLINE-CHILDREN concatenation fix
(Phase 15, GATE-02, bug #5).

Bug #3 gave a def-list TERM its own code-mode concat context (``_in_term``) so
adjacent inline expressions in the term -- the code-mode 1st arg of
``terms.item(TERM, DEFINITION)`` -- are ``" + "`` joined instead of juxtaposed
(a Typst ``expected comma`` syntax error). But that fix wired the context into
only ``visit_Text`` and ``visit_literal``. When a term's DIRECT children include
a ``reference``/``strong``/``emphasis`` element adjacent to a ``text``/
``literal``, those element visitors did NOT participate, producing (real corpus
fatal, ``extdev/logging.typ``)::

    terms.item(strong({text("type")}) + text(", ")strong({ + text("*subtype*")}), ...)

with two symptoms in one term:

1. **Missing '+':** ``text(", ")strong(`` -- no separator between the ``text``
   and the following ``strong`` element.
2. **Stray leading '+':** ``strong({ + text("*subtype*")})`` -- the term
   separator leaked INSIDE the strong element's own content block (the concat
   context was not suppressed while descending into the element's children).

Fix: a single shared inline-concat mechanism in the translator
(``_inline_concat_context`` + ``_emit``/``_mark_inline_concat_content`` +
``_enter``/``_exit_inline_concat_element``) routes ``visit_Text``,
``visit_literal``, ``visit_emphasis``, ``visit_strong`` and ``visit_reference``
through ONE source of truth. Every direct term child of any inline type is
``" + "`` separated between siblings, while the concat context is SUPPRESSED
inside each element's own block (so ``strong({...})`` / ``emph({...})`` /
``link(...)`` never leak an outer ``+``). The same mechanism also fixes the
latent identical gap in the ``_in_link`` (link body) and ``in_desc_parameter``
concat contexts.

This module proves both halves:

* Fast, offline **translator unit tests** assert the exact ``+`` separated term
  string for every inline-child combination the fix must cover -- including the
  nesting case (a link that WRAPS a strong must NOT emit an inner ``+`` inside
  its own ``link(...)`` body). These fail against the pre-fix translator
  (missing ``+`` / stray ``+``) and pass with it.
* A real-compile **render gate** builds a fixture through ``-b typstpdf`` and
  confirms ``typst.compile()`` yields a ``%PDF`` (no ``expected comma``) for a
  term mixing a literal, strong, emphasis, reference and text.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.translator import TypstTranslator

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


# ---------------------------------------------------------------------------
# Fast translator-level unit tests (no build, no compile)
# ---------------------------------------------------------------------------


def _make_translator() -> TypstTranslator:
    """Construct a TypstTranslator over a bare docutils document."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    class _Config:
        typst_use_mitex = False

    class _Domains:
        pass

    class _Env:
        domains = _Domains()

    class _Builder:
        config = _Config()
        env = _Env()

    return TypstTranslator(doc, _Builder())


def _term_output(*children: nodes.Node) -> str:
    """
    Walk a ``term`` node carrying ``children`` through the translator and return
    the buffered term string (what lands as the code-mode 1st arg of
    ``terms.item``).
    """
    translator = _make_translator()
    term = nodes.term()
    for child in children:
        term += child
    term.walkabout(translator)
    return translator.current_term_buffer


def _reference(url: str, *children: nodes.Node) -> nodes.reference:
    ref = nodes.reference(refuri=url)
    for child in children:
        ref += child
    return ref


def _assert_no_concat_leak(term: str) -> None:
    """
    Assert the term neither leaks a stray ``+`` inside an element's own content
    block (``({ +``) nor juxtaposes two adjacent code-mode expressions with no
    ``+`` separator (``)strong(`` / ``)emph(`` / ``)raw(`` / ``")text(``).
    """
    assert "({ +" not in term, f"stray '+' leaked inside a content block: {term}"
    for juxtaposition in (")strong(", ")emph(", ")raw(", '")text('):
        assert juxtaposition not in term, (
            f"adjacent term expressions juxtaposed with no '+' "
            f"({juxtaposition!r}): {term}"
        )


class TestDeflistTermInlineChildrenConcat:
    """
    Every inline child type that can be a direct def-list term child must be
    ``" + "`` separated from its siblings, with the concat context suppressed
    inside the element's own block.

    Requirements: GATE-02 (Phase 15 -- the fifth corpus fatal, the
    ``_in_term`` inline-element blind spot documented by the bug #3 fix).
    """

    def test_single_child_term_has_no_separator(self):
        """A one-expression term gains no leading or trailing ``+``."""
        assert _term_output(nodes.Text("SingleTerm")) == 'text("SingleTerm")'

    def test_text_then_strong(self):
        term = _term_output(nodes.Text("prefix "), nodes.strong(text="bold"))
        assert term == 'text("prefix ") + strong({text("bold")})'
        _assert_no_concat_leak(term)

    def test_strong_then_text(self):
        term = _term_output(nodes.strong(text="bold"), nodes.Text(" suffix"))
        assert term == 'strong({text("bold")}) + text(" suffix")'
        _assert_no_concat_leak(term)

    def test_reference_then_text(self):
        term = _term_output(
            _reference("https://example.com/a", nodes.Text("link")),
            nodes.Text(" tail"),
        )
        assert term == 'link("https://example.com/a", text("link")) + text(" tail")'
        _assert_no_concat_leak(term)

    def test_emphasis_then_literal(self):
        term = _term_output(nodes.emphasis(text="em"), nodes.literal(text="code"))
        assert term == 'emph({text("em")}) + raw("code")'
        _assert_no_concat_leak(term)

    def test_link_wrapping_strong_has_no_inner_separator(self):
        """
        A term child that is a link WRAPPING a strong must emit the strong as
        the link's own body with NO term-level ``+`` inside ``link(...)`` -- the
        separator applies only BETWEEN top-level term siblings.
        """
        term = _term_output(
            _reference("https://example.com/b", nodes.strong(text="bold"))
        )
        assert term == 'link("https://example.com/b", strong({text("bold")}))'
        _assert_no_concat_leak(term)
        # Exactly one link, one strong, and no '+' anywhere (single child).
        assert " + " not in term

    def test_mixed_all_inline_child_types(self):
        """
        The headline corpus shape: literal, strong, emphasis, reference and
        text as adjacent direct term children -- every boundary ``+`` separated,
        no leak inside any element block.
        """
        term = _term_output(
            nodes.literal(text="code"),
            nodes.Text(" "),
            nodes.strong(text="bold"),
            nodes.Text(" "),
            nodes.emphasis(text="it"),
            nodes.Text(" "),
            _reference("https://example.com/c", nodes.Text("lnk")),
            nodes.Text(" tail"),
        )
        assert term == (
            'raw("code") + text(" ") + strong({text("bold")}) + text(" ") '
            '+ emph({text("it")}) + text(" ") '
            '+ link("https://example.com/c", text("lnk")) + text(" tail")'
        )
        _assert_no_concat_leak(term)


# ---------------------------------------------------------------------------
# Real-compile render gate (full -b typstpdf build)
# ---------------------------------------------------------------------------


@pytest.fixture
def deflist_term_inline_children_dir():
    """Path to the deflist_term_inline_children_concat fixture project."""
    return Path(__file__).parent / "fixtures" / "deflist_term_inline_children_concat"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess.

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the def-list-term inline-children render gate",
)
class TestDeflistTermInlineChildrenRenderGate:
    """
    Real-compile regression gate proving the translator ``+`` concatenates a
    definition-list term whose direct inline children mix element types, so
    ``typst.compile()`` does not abort with "expected comma".

    Requirements: GATE-02 (the fast offline reproduction of the def-list-term
    inline-element concat corpus fatal, bug #5).
    """

    def test_typstpdf_concatenates_mixed_term_children_and_produces_pdf(
        self, deflist_term_inline_children_dir, temp_build_dir
    ):
        result = _run_sphinx_build_typstpdf(
            deflist_term_inline_children_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly.
        assert "expected comma" not in result.stderr, (
            "typst.compile() rejected the juxtaposed mixed-child term -- the "
            f"inline-children concat fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The mixed term must + concatenate every adjacent inline child; assert
        # the stable code-mode prefix (literal->text->strong->text->emphasis)
        # and the trailing text sibling.
        assert (
            'raw("code") + text(" ") + strong({text("bold")}) + text(" ") '
            '+ emph({text("italic")})'
        ) in typ_text, "mixed term inline children are not + concatenated"
        assert (
            '+ text(" tail")' in typ_text
        ), "trailing term text sibling is not + separated from the reference"
        # A single-inline-node term must not gain a spurious leading/trailing +.
        assert (
            'terms.item(text("SingleTerm")' in typ_text
        ), "a single-inline-node term must emit cleanly with no leading '+'"

        # No stray '+' may leak inside an element's own content block, and no two
        # code-mode term expressions may juxtapose with no '+' separator. These
        # patterns never occur in the (content-mode, newline separated) par({...})
        # definition bodies, so they are safe as whole-document assertions.
        for leak in ("({ +", ")strong(", ")emph(", ")raw(", '")text('):
            assert leak not in typ_text, (
                f"emitted .typ leaks/juxtaposes term expressions ({leak!r}) -- "
                "the inline-children concat fix is not applied"
            )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the juxtaposed mixed-child term:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"
