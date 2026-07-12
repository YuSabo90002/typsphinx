r"""
Fast, offline regression gate for the reference-with-target caption wrapper +
block-quote-in-list-item separator fix (Phase 15, GATE-02).

Deterministic, network-free reproduction of the eleventh fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree, after bugs #1-#10 unblocked the compile
path::

    error: expected semicolon or line break
       ┌─ usage/advanced/intl.typ:27      (sub-construct a)
       ┌─ changes/6.1.typ:143             (sub-construct b)

Two distinct root constructs, same Typst parse-error class ("a code-mode
sibling juxtaposed with no separator"):

(a) A FIGURE CAPTION renders its inline children into a ``{...}`` code block
    (``depart_figure``), but ``visit_caption`` set NEITHER ``in_paragraph`` NOR
    any concat/list-item context, so ``_add_paragraph_separator`` never fired
    and adjacent inline caption expressions juxtaposed. The corpus case is a
    *named* external hyperlink (``plantuml <https://plantuml.com>``\_), which
    docutils splits into a ``reference`` node immediately followed by an inline
    ``target`` node -- rendered as the ``[#link(...) #label(...)]`` markup
    wrapper -- with a trailing ``.)`` text run in the SAME caption::

        caption: {text("...by\n")[#link("...", text("plantuml")) #label("plantuml")]text(".)")}

    The wrapper close ``]`` juxtaposed against ``text(".)")`` (and the leading
    text juxtaposed against ``[``). Fix: ``visit_caption``'s figure branch sets
    ``in_paragraph=True`` (saved/restored in ``depart_caption``) so the EXISTING
    paragraph separator machinery newline-separates every inline sibling --
    exactly as it already does in a real paragraph, which renders the SAME
    reference-with-target wrapper correctly.

(b) A ``block_quote`` (emitted ``quote[...]``) following inline content inside a
    bullet-list item juxtaposed against the preceding text::

        text(" functions:")quote[...

    ``visit_block_quote`` emitted ``quote[`` with no list-item leading-separator
    guard and ``depart_block_quote`` never set ``list_item_needs_separator`` --
    the one block visitor omitted from bug #4's block-visitor separator pattern.
    Fix: emit a leading ``\n`` when ``in_list_item and list_item_needs_separator``
    and set ``list_item_needs_separator`` on depart, like every other block
    visitor.

The fixture drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on
purpose: the fatal only aborts on the ``TypstPDFBuilder.finish()`` compile
path, so a ``-b typst`` build would emit the invalid ``.typ`` but never compile
it and thus prove nothing.

Confirmed both directions: FAILS against the pre-fix translator (both
juxtapositions present -> ``typst.compile()`` aborts with "expected semicolon
or line break"), and PASSES with the fix.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@pytest.fixture
def ref_target_nested_list_render_gate_dir():
    """Return the path to the ref_target_nested_list_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "ref_target_nested_list_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

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
    reason="typst-py is required for the ref-target/nested-block render gate",
)
class TestRefTargetNestedListRenderGate:
    """
    Real-compile regression gate proving (a) a figure caption's inline
    reference-with-target markup wrapper and (b) a block quote following inline
    content inside a list item each carry a statement separator to their
    following sibling, so ``typst.compile()`` does not abort with "expected
    semicolon or line break".

    Requirements: GATE-02 (Phase 15 -- fast offline reproduction of the
    eleventh corpus fatal).
    """

    def test_typstpdf_caption_wrapper_and_block_quote_separate_and_compile(
        self, ref_target_nested_list_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly with no "expected semicolon or line break"
          fatal logged;
        - (a) the figure caption's reference-with-target wrapper close
          (``#label("plantuml")]``) is separated by a newline from the
          following ``text(".)")`` run -- the juxtaposed ``]text(".)")`` form
          (the exact corpus fatal shape) is absent;
        - (b) the block quote ``quote[`` is separated by a newline from the
          preceding list-item text ``text("NESTEDBLOCKSENTINEL functions:")``
          -- the juxtaposed ``functions:")quote[`` form is absent;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the only proof both separated forms compiled to valid
          Typst and ``typst.compile()`` did NOT abort.
        """
        result = _run_sphinx_build_typstpdf(
            ref_target_nested_list_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signature explicitly rather than
        # trusting returncode alone.
        assert "expected semicolon or line break" not in result.stderr, (
            "typst.compile() hit a juxtaposition parse error -- the "
            "caption/block-quote separator fix is not in effect:\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # (a) The reference-with-target wrapper close must NOT juxtapose the
        # following inline text -- this is the exact corpus intl.typ:27 fatal
        # shape.
        assert '#label("plantuml")]' in typ_text, (
            "The reference-with-target markup wrapper was not emitted -- the "
            f"fixture's named external link did not render a wrapper:\n{typ_text}"
        )
        assert '#label("plantuml")]text(".)")' not in typ_text, (
            "The caption's reference-with-target wrapper close juxtaposes the "
            'following text(".)") with NO separator -- the exact '
            "intl.typ:27 'expected semicolon or line break' fatal"
        )
        # ...and the separated form (newline between wrapper close and the next
        # text run) must be present.
        assert re.search(r'#label\("plantuml"\)\]\s*\ntext\("\.\)"\)', typ_text), (
            "Expected a newline separator between the caption wrapper close "
            'and the following text(".)") run -- the paragraph-context fix for '
            "the figure caption did not take effect"
        )

        # (b) The block quote must NOT juxtapose the preceding list-item text --
        # this is the exact corpus changes/6.1.typ:143 fatal shape.
        assert "quote[" in typ_text, (
            "No block quote (quote[...]) was emitted -- the fixture's "
            f"over-indented sub-block did not render a block_quote:\n{typ_text}"
        )
        assert 'text("NESTEDBLOCKSENTINEL functions:")quote[' not in typ_text, (
            "The block quote juxtaposes the preceding list-item text with NO "
            "separator -- the exact changes/6.1.typ:143 'expected semicolon or "
            "line break' fatal"
        )
        # ...and the separated form (newline between the list-item text and the
        # block quote) must be present.
        assert re.search(
            r'text\("NESTEDBLOCKSENTINEL functions:"\)\s*\nquote\[', typ_text
        ), (
            "Expected a newline separator between the list-item text and the "
            "following block quote -- the block_quote list-item separator fix "
            "did not take effect"
        )

        # (c) The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            "likely on one of the two juxtapositions:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
