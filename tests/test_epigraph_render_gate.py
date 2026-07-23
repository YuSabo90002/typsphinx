"""Real-render acceptance gate for the epigraph/block-quote ATTRIBUTION fix.

The shipping bug (backlog: attribution source-leak): visit_attribution emitted
the attribution as a markup-mode ``attribution: [ ... ]`` argument, while the
attribution's inline children are emitted through the CODE-MODE visitors
(``visit_Text`` -> ``text("...")``, ``visit_emphasis`` -> ``emph({...})``,
``visit_literal`` -> ``raw("...")``). Inside a markup ``[...]`` argument those
un-``#``-prefixed function calls are LITERAL PROSE, so Typst typesets them
verbatim: the author name rendered as ``text(“Author”)`` (curly quotes from
smart-quote typography) instead of ``Author``, and a lone ``_`` in an
inline-literal child (Sphinx's ``_t`` template suffix, or any ``_``-bearing
literal) opened a stray unclosed emphasis span that aborted the whole compile
with ``TypstError: unclosed delimiter``.

This module runs the full pipeline for real -- ``sphinx-build -b typstpdf``
(which emits the ``.typ`` AND compiles it to PDF via ``typst.compile()``) ->
``pypdf`` text-extraction -- and asserts the attribution renders as clean
evaluated prose (an emphasis + an inline literal + a plain sentinel), with none
of the literal-source-leak signatures reaching the compiled PDF. It fails on
the pre-fix markup-mode emission (compile aborts, no PDF) and passes on the
code-mode ``attribution: { ... }`` fix.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# Literal-source-leak signatures. These are the code-mode function-call
# wrappers (and the named-argument keyword) that must NEVER reach the rendered
# PDF prose -- their presence means the attribution's inline children leaked as
# literal Typst source instead of being evaluated. Both the straight-quote
# ``text("`` and the curly-quote ``text(“`` forms are checked: Typst applies
# smart-quote typography, so a leaked ``text("Author")`` is TYPESET as
# ``text(“Author”)`` -- the straight-quote form alone would miss the leak in
# the extracted PDF text.
LEAK_SIGNATURES = ('text("', "text(“", "emph(", 'raw("', "raw(“", "attribution:")


@pytest.fixture
def epigraph_render_gate_dir():
    """Return the path to the epigraph_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "epigraph_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the epigraph render gate",
)
class TestEpigraphAttributionRenderGate:
    """
    Real-compile acceptance gate for the block-quote / ``.. epigraph::``
    attribution markup-mode -> code-mode fix.
    """

    def test_epigraph_attribution_renders_as_evaluated_prose(
        self, epigraph_render_gate_dir, temp_build_dir
    ):
        """
        Compile the epigraph render-gate fixture straight to PDF via the
        typstpdf builder and confirm:

        - the build reports no Typst compilation error (the pre-fix markup-mode
          ``attribution: [ ... ]`` emission aborts the compile with an
          ``unclosed delimiter`` on the inline literal's lone underscore);
        - a valid ``%PDF`` is produced;
        - (source) the attribution is emitted as the code-mode
          ``}, attribution: {`` argument, never the markup-mode
          ``}, attribution: [`` argument;
        - the epigraph BODY sentinels (with AND without attribution) reach the
          extracted PDF text;
        - the attribution's inline children render as EVALUATED content -- the
          emphasis text, the inline literal, and the author sentinel appear as
          clean prose on the ``— Ada _lovelace ...`` attribution line, NOT
          wrapped in a leaked ``text(“...”)`` / ``emph(...)`` / ``raw(...)``;
        - none of the LEAK_SIGNATURES appear anywhere in the extracted text.

        Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
        so the exact interpreter/venv already running this test is reused, with
        no dependency on external PATH resolution of a ``uv`` executable -- a
        stray non-Nix ``uv`` on the sandbox PATH makes ``["uv", "run", ...]``
        exit 127 from inside a pytest-launched subprocess.
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "typstpdf",
                str(epigraph_render_gate_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # The typstpdf builder catches a Typst compilation error, logs it, and
        # continues (so a returncode of 0 alone does not prove the PDF
        # compiled). Assert the compile-error signatures are absent from the
        # build output -- the pre-fix markup-mode attribution aborts here with
        # `TypstError: unclosed delimiter` and writes NO index.pdf.
        combined = result.stdout + result.stderr
        for compile_error_marker in (
            "Failed to compile",
            "TypstError",
            "unclosed delimiter",
            "TypstCompilationError",
        ):
            assert compile_error_marker not in combined, (
                f"Typst compilation error '{compile_error_marker}' surfaced in "
                f"the build output -- the attribution markup/code-mode "
                f"regression aborted the compile:\n{combined}"
            )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_source = index_typ.read_text(encoding="utf-8")

        # Source-level: the attribution must be a CODE-MODE `{ ... }` argument,
        # where the inline children are evaluated function calls -- never the
        # markup-mode `[ ... ]` argument that typesets them as literal prose.
        assert "}, attribution: {" in typ_source, (
            "The attribution was not emitted as the code-mode "
            "`}, attribution: {` argument:\n" + typ_source
        )
        assert "}, attribution: [" not in typ_source, (
            "The attribution was emitted as the markup-mode `}, attribution: [` "
            "argument -- its code-mode children are literal prose there (the "
            "source-leak / unclosed-delimiter bug):\n" + typ_source
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not created -- the attribution compile likely "
            "aborted (pre-fix markup-mode emission)"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        # The epigraph BODIES (with and without attribution) must render.
        for sentinel in (
            "EPIGRAPHBODYSENTINEL",
            "EPIGRAPHNOATTRSENTINEL",
        ):
            assert sentinel in full_text, (
                f"Expected epigraph body sentinel '{sentinel}' in extracted "
                f"PDF text -- epigraph render regression:\n{full_text}"
            )

        # The attribution's inline children must render as EVALUATED prose:
        # the emphasis text, the inline literal, and the plain author sentinel
        # all appear on the attribution line -- and, crucially, as the clean
        # `— Ada _lovelace <sentinel>` form, NOT wrapped in a leaked
        # `text(“...”)`. Asserting the exact em-dash attribution-line form
        # rejects the leaked wrapper: a leaked attribution reads
        # `— text(“Ada”) ...`, so the clean form is absent.
        assert "— Ada _lovelace EPIGRAPHAUTHORSENTINEL" in full_text, (
            "The attribution did not render as the clean prose form "
            "'— Ada _lovelace EPIGRAPHAUTHORSENTINEL' -- its inline children "
            "(emphasis, inline literal, author sentinel) were not evaluated "
            f"as content:\n{full_text}"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into rendered "
                "PDF text -- the attribution's inline children were emitted as "
                "literal source, not evaluated content (attribution "
                f"markup/code-mode regression):\n{full_text}"
            )
